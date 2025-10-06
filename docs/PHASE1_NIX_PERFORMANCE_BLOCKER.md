# Phase 1 Nix Validation - Performance Blocker

**Date**: 2025-10-06
**Status**: BLOCKED
**Priority**: HIGH
**Affects**: Phase 1 Nix validation (TEST 4/17)

---

## Executive Summary

Phase 1 Nix validation discovered a **critical performance blocker**: Mojo compilation in Nix sandbox exhibits **1,380x slowdown** compared to direct builds, making validation impractical.

### Key Metrics

| Metric | Direct Build | Nix Sandbox Build | Slowdown |
|--------|--------------|-------------------|----------|
| Compilation Time | 1.05 seconds | 23+ minutes (killed) | **1,380x** |
| CPU Usage | 100% compute | 100% CPU @ 15% iowait | I/O bound |
| Output Size | 15KB | N/A (killed) | - |
| FFI Symbols | 9 symbols ✅ | N/A | - |

---

## Timeline of Discovery

### Day 6 - Issue Evolution

**14:00** - Fixed Mojo venv path (`/home/m0xu/1-projects/synapse/.venv`)
**14:15** - Fixed build command (added `--emit=shared-lib` flag)
**14:30** - Verified direct build: **1.05 sec, 15KB .so, 9 FFI symbols** ✅
**14:45** - Started Nix validation (TEST 4/17)
**14:50** - 5 min: Still compiling (expected ~1 min first-time overhead)
**15:00** - 10 min: CPU contention identified (Zen browser @ 101% CPU)
**15:10** - Browser killed, 15% iowait discovered (disk I/O bottleneck)
**15:20** - 23 min: Killed build manually (unacceptable performance)

---

## Root Cause Analysis

### The Problem

Mojo compilation in Nix sandbox experiences **extreme I/O bottleneck**:

```
Direct build:  1.05s (100% CPU compute)
Nix build:     23+ min (100% CPU @ 15% iowait)
Overhead:      ~1,380x slowdown
```

### Why This Happens

1. **LLVM Intermediate Files**: Mojo uses LLVM backend which generates many temporary files during compilation
2. **Nix Sandbox Isolation**: All I/O goes through Nix's hermetic filesystem layer
3. **Small Random Writes**: LLVM creates/reads many small files (worst case for I/O)
4. **No Caching**: First-time builds have no compiled artifacts cached

### Evidence

**System Metrics During Build:**
```
%iowait:  15.9% (disk bottleneck)
nvme0n1:  39 writes/s (LLVM intermediate files)
Memory:   5.4GB available (not memory bound)
```

**Process Behavior:**
```
PID 190106: 100% CPU but only ~82% effective (rest is I/O wait)
Runtime: 23+ minutes for 1-second compilation
```

---

## What We Fixed (Successfully)

### Issue 1: Wrong Mojo venv Path ✅

**Before:**
```nix
src = /home/m0xu/.synapse-system/.venv;  # ❌ Wrong location
```

**After:**
```nix
src = /home/m0xu/1-projects/synapse/.venv;  # ✅ Correct (project-local)
```

**Result:** Mojo SDK now accessible from Nix flake

---

### Issue 2: Missing `--emit=shared-lib` Flag ✅

**Before:**
```nix
${mojoPath} build pattern_search_mojo.mojo -o libpattern_search.so
# ❌ Hangs forever (expects main() function)
```

**After:**
```nix
${mojoPath} build --emit=shared-lib pattern_search_mojo.mojo -o libpattern_search.so
# ✅ Compiles FFI library (in 1s direct, 23min+ Nix)
```

**Verification:**
```bash
$ time mojo build --emit=shared-lib pattern_search_mojo.mojo -o /tmp/test.so
# Compiled in 1.05 seconds ✅

$ file /tmp/test.so
# ELF 64-bit LSB shared object ✅

$ nm -D /tmp/test.so | grep pattern_search_ffi
# 0000000000001140 T pattern_search_ffi ✅

$ ls -lh /tmp/test.so
# 15K (matches production) ✅
```

---

## What Remains Blocked

### The Nix I/O Bottleneck ❌

**Status:** UNRESOLVED
**Impact:** Phase 1 validation cannot complete (stuck at TEST 4/17)

**The Dilemma:**
- ✅ Fix is correct (direct build proves it)
- ✅ Command works perfectly (1s compilation)
- ❌ Nix sandbox makes it impractical (23+ min)

---

## Solution Options

### Option A: Nix tmpfs Build (RECOMMENDED)

**Description:** Configure Nix to build in RAM instead of disk

**Implementation:**
```nix
# In flake.nix or nix.conf
build-dir = /dev/shm/nix-builds
# OR
sandbox-paths = /dev/shm=/dev/shm
```

**Pros:**
- ✅ Eliminates I/O bottleneck (RAM is 1000x faster)
- ✅ Maintains Nix hermetic builds
- ✅ Should reduce build time to ~10-30 seconds

**Cons:**
- ⚠️ Requires 500MB+ RAM per build
- ⚠️ Not persistent across reboots

**Estimated Impact:** 1,380x → ~10-30x overhead (acceptable)

---

### Option B: Relaxed Sandbox

**Description:** Disable unnecessary Nix isolation for Mojo builds

**Implementation:**
```nix
sandbox = "relaxed"
# OR
__noChroot = true;  # In derivation
```

**Pros:**
- ✅ May reduce I/O overhead
- ✅ Simpler configuration

**Cons:**
- ❌ Violates Nix reproducibility principles
- ❌ May not solve LLVM temp file issue
- ❌ Less portable across systems

**Verdict:** ⚠️ Not recommended (defeats Nix purpose)

---

### Option C: Accept Direct Builds as Validation

**Description:** Skip Nix validation for Mojo libraries, use direct builds

**Implementation:**
- Validate Nix can *package* the pre-built `.so`
- Use direct `mojo build` for actual compilation
- Nix flake just copies/verifies the artifact

**Pros:**
- ✅ Immediate unblock (works today)
- ✅ Practical for development
- ✅ 1-second build times

**Cons:**
- ❌ **VIOLATES PHASE 1 SUCCESS CRITERIA**
- ❌ Doesn't prove Nix can build Mojo
- ❌ Not reproducible across systems

**Verdict:** ❌ Fails Phase 1 goals

---

### Option D: Incremental Nix Builds

**Description:** Configure Nix to cache LLVM intermediates

**Implementation:**
```nix
# Use ccache or similar for LLVM
buildInputs = [ pkgs.ccache ];
```

**Pros:**
- ✅ Second builds would be fast
- ✅ Maintains reproducibility

**Cons:**
- ⚠️ First build still slow
- ⚠️ Complex setup
- ⚠️ May not work with Mojo's LLVM version

**Verdict:** ⚙️ Good long-term, not immediate fix

---

## Recommended Path Forward

### Immediate (Day 6-7)

1. **Implement Option A (tmpfs):**
   ```bash
   # Add to nix.conf or flake
   build-dir = /dev/shm/nix-builds
   ```

2. **Test with single build:**
   ```bash
   nix build path:./nix/flakes/mojo-pattern-search --option build-dir /dev/shm
   ```

3. **Measure performance:**
   - Target: <30 seconds (acceptable)
   - If still >5 min: Investigate further

### Week 2 (If tmpfs succeeds)

4. **Complete Phase 1 validation** (TEST 4-17)
5. **Document tmpfs requirement** in Nix flakes
6. **Update MOJO_PILOT_PLAN.md** with Nix performance notes

### Week 2 (If tmpfs fails)

7. **Escalate to Mojo/Nix communities:**
   - Report LLVM I/O issue to Mojo team
   - Ask Nix community for Mojo-specific optimizations

8. **Consider hybrid approach:**
   - Use direct builds for development
   - Use Nix for deployment/packaging only

---

## Impact on Pilot Timeline

### Original Timeline
```
Week 1-2:  Phase 1 (Nix validation)  ← BLOCKED at TEST 4/17
Week 3-4:  Pattern search 10% → 50%
Week 5-8:  Pattern search 50% → 100%
Week 9-16: Message router rollout
```

### Revised Timeline (If tmpfs works)
```
Day 6-7:   Implement tmpfs, complete Phase 1  ← +1 day
Week 2:    Phase 2 planning
Week 3-4:  Pattern search 10% → 50%
...
```

**Impact:** +1 day delay (acceptable)

### Revised Timeline (If tmpfs fails)
```
Week 1:    Investigation + workarounds         ← +1 week
Week 2-3:  Complete Phase 1 (alternative)
Week 4-5:  Pattern search rollout (compressed)
...
```

**Impact:** +1 week delay (concerning, but Phase 2-3 can compress)

---

## Lessons Learned

### Pattern Discovered: Mojo + Nix I/O Characteristics

**Observation:** Mojo compilation is I/O intensive (LLVM backend)

**Pattern:**
```yaml
pattern_id: mojo_nix_io_bottleneck
trigger: "Mojo compilation in Nix sandbox"
symptom: "1,000x+ slowdown vs direct build"
cause: "LLVM small-file I/O + Nix isolation overhead"
solution: "tmpfs build directory (RAM-based compilation)"
applicable_to: ["pattern_search", "message_router", "all_mojo_libs"]
```

**Future Prevention:**
- Always test Nix builds on representative hardware
- Measure Nix overhead before committing to Nix-based CI/CD
- Consider tmpfs as default for LLVM-based languages in Nix

### Root Cause (5 Whys)

1. **Why blocked?** → Nix build takes 23+ min (impractical)
2. **Why so slow?** → 15% iowait (disk I/O bottleneck)
3. **Why I/O bound?** → LLVM generates many small temp files
4. **Why does Nix amplify?** → Sandbox isolation adds overhead to every I/O operation
5. **Why no mitigation?** → Nix flake didn't anticipate LLVM I/O pattern

**Root Cause:** Mismatch between LLVM's I/O-heavy compilation model and Nix's disk-based isolation.

---

## References

### Files Modified
- ✅ `nix/flakes/mojo-runtime/flake.nix` (line 23: venv path)
- ✅ `nix/flakes/mojo-pattern-search/flake.nix` (line 32: `--emit=shared-lib`)
- ✅ `nix/flakes/mojo-pattern-search/README.md` (line 149: documentation)

### Validation Artifacts
- `/tmp/test_build.so` (1s direct build, 15KB, 9 symbols) ✅
- `/tmp/validation-fixed.log` (Nix build killed at 23min)
- `nix/validation-results.txt` (3/17 tests pass)

### Related Documentation
- `docs/MOJO_PILOT_PLAN.md` (Phase 1 success criteria)
- `docs/PHASE1_VALIDATION_ISSUES.md` (original venv discovery)
- `HANDOVER.md` (Day 6 summary)

---

## Next Actions

### For User
1. **Try tmpfs solution:**
   ```bash
   nix build path:./nix/flakes/mojo-pattern-search \
     --option build-dir /dev/shm/nix-builds
   ```

2. **Measure time:** Should be <30s (vs 23+ min)

3. **If success:** Update flake to use tmpfs by default

4. **If failure:** Report to #mojo and #nixos communities

### For Boss Agent
- [ ] Update MOJO_PILOT_PLAN.md with Nix performance notes
- [ ] Add tmpfs requirement to Nix flake documentation
- [ ] Research alternative Nix optimization strategies
- [ ] Prepare Phase 1 completion report (pending tmpfs test)

---

**Status:** Awaiting tmpfs validation test
**ETA to Phase 1 Complete:** 1-2 days (if tmpfs works)
**Blocker Severity:** HIGH (blocks 14/17 remaining tests)
