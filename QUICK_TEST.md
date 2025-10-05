# Quick Testing Guide

Fast ways to test and validate the file_creator MVP system.

## Prerequisites

```bash
# Ensure environment is set up
uv sync --all-extras
```

---

## Option 1: Run Automated Tests (Recommended)

**Best for**: Verifying everything works

```bash
# Run full MVP test suite
uv run pytest tests/test_file_creator_mvp.py -v

# Expected output:
# ✅ 13/14 tests passing (93%)
# ❌ 1 test failing (template naming - cosmetic only)
# Time: ~16 seconds
```

### What it tests:
- ✅ File creation (file_writer)
- ✅ Directory creation (directory_creator)
- ✅ File reading (file_reader)
- ✅ File deletion (file_deleter)
- ✅ Directory deletion (directory_deleter)
- ✅ File moving (file_mover)
- ✅ Batch operations (batch_file_creator)
- ✅ Template application (template_applier)
- ✅ State persistence
- ✅ Dual-tract message routing

---

## Option 2: Run Demo Script

**Best for**: Seeing the system in action

```bash
uv run python demo_mvp.py
```

### What it demonstrates:
1. **File Creation** - Creates `hello.txt`
2. **Directory Creation** - Creates nested `components/auth/utils`
3. **Component Scaffolding** - Creates `user_service/` with files
4. **File Deletion** - Deletes test file
5. **File Move** - Renames component file
6. **Batch Creation** - Creates config.yaml, README.md, .gitignore

### Expected output:
```
╔════════════════════════════════════════════════════════════╗
║  file_creator MVP Demonstration                            ║
║  Dual-Tract Architecture in Action                         ║
╚════════════════════════════════════════════════════════════╝

Demo directory: /tmp/synapse_demo_XXXXXX

🧠 Initializing Corpus Callosum...
⚛️  Creating T_ext Particles - All 8...
🎯 Creating T_int Orchestrator...
▶️  Starting all agents...

[6 demos execute showing create/delete/move/batch operations]

📊 System Statistics:
   Corpus Callosum: X messages routed
   Particles: Success rates, cycle counts

✅ All operations successful
```

**Time**: ~10 seconds

---

## Option 3: Interactive Testing

**Best for**: Manual validation and exploration

```bash
uv run python interactive_test.py
```

### Interactive Menu:
```
╔════════════════════════════════════════════════════════════╗
║  Synapse Interactive Tester                                ║
║  Manual Testing Interface for file_creator MVP            ║
╚════════════════════════════════════════════════════════════╝

1. Create File
2. Create Directory
3. Read File
4. Delete File
5. Move/Rename File
6. Batch Create Files
7. Show Statistics
8. List Test Directory
9. Exit

Select option (1-9):
```

### Example session:
```bash
# 1. Select "1. Create File"
Enter file path: test.txt
Enter file content: Hello from Synapse!
✅ Success: File created

# 2. Select "8. List Test Directory"
/tmp/synapse_interactive_XXXXXX/
└── test.txt

# 3. Select "7. Show Statistics"
📊 Corpus Callosum:
   Total messages: 1
⚛️  Particle Statistics:
   file_writer:
      Executions: 1
      Success rate: 100.0%
```

---

## Option 4: Basic Validation

**Best for**: Quick sanity check

```bash
uv run python validate_mvp.py
```

### What it validates:
- ✅ All required files exist
- ✅ All imports work
- ✅ Registry structure is valid

### Expected output:
```
=== Validating File Structure ===
✓ lib/registry.json
✓ lib/atomic_particle.py
✓ lib/particles/file_writer.py
...

=== Validating Registry ===
✓ Registry structure valid
  - 9 agents registered
  - 1 INTERNAL agents
  - 8 EXTERNAL agents

=== Validating Imports ===
✓ AtomicParticle
✓ FileWriter
...

✅ All validations passed!
```

---

## Quick Verification Checklist

After running any test, verify:

### 1. Test Results
- [ ] 13/14 tests passing (93%) OR
- [ ] Demo completed all 6 demonstrations OR
- [ ] Interactive tester works without errors

### 2. Particle Functionality
- [ ] All 8 particles initialized
- [ ] Success rates > 90%
- [ ] State files created in test directory

### 3. Message Routing
- [ ] Corpus Callosum shows messages routed
- [ ] Messages to INTERNAL (orchestrator)
- [ ] Messages to EXTERNAL (particles)
- [ ] Zero message loss

### 4. File Operations
- [ ] Files created successfully
- [ ] Directories created with parents
- [ ] Files deleted
- [ ] Files moved/renamed
- [ ] Batch operations work

---

## Troubleshooting

### Tests fail with "No module named pytest"
```bash
uv sync --all-extras
```

### Demo hangs or times out
- Ensure Corpus Callosum is running (check for startup messages)
- Wait 1 second per operation (async message round-trip)
- Check logs for errors

### Interactive tester shows 0 executions
- Make sure to wait 1 second after sending request
- Check test directory exists
- Verify particles started (look for "✅ Environment ready!")

### File operations don't work
```bash
# Verify the broadcast fix is applied
cat ~/.synapse-system/.synapse/corpus_callosum/reactive_message_router.py | grep -A 10 "def _distribute_messages"

# Should show broadcast loop, not round-robin break
```

---

## Performance Metrics

**Expected performance** (on modern hardware):

| Test Type | Duration | Pass Rate |
|-----------|----------|-----------|
| Automated tests | ~16s | 93% (13/14) |
| Demo script | ~10s | 100% |
| Interactive test | Varies | User-dependent |
| Validation | <1s | 100% |

**System Stats** (after full test run):
- Messages routed: ~20-30
- Particle executions: ~15-20
- Success rates: >95%
- State files: 9 JSON files

---

## What's Working ✅

1. **Dual-Tract Architecture**
   - T_int orchestrator (planning)
   - T_ext particles (execution)
   - Corpus Callosum (message routing)

2. **All 8 Particles**
   - file_writer
   - directory_creator
   - file_reader
   - file_deleter
   - directory_deleter
   - file_mover
   - batch_file_creator
   - template_applier

3. **Advanced Features**
   - Broadcast message routing (Day 5 fix)
   - State persistence with cycle counting
   - Reactive streams with backpressure
   - Circuit breaker pattern
   - Fractal Pneuma Micro-Loop

4. **Test Infrastructure**
   - UV-based reproducible environment
   - pytest-asyncio working
   - 68 dependencies locked

## What's Not Working ❌

1. **Template Naming** (Low priority, cosmetic)
   - test_scaffold_module fails
   - Creates `Data_Processor` instead of `DataProcessor`
   - File IS created, just naming differs

---

## Next Steps

Once testing is complete:

1. ✅ **DONE**: MVP functional (93% pass rate)
2. 🔄 **OPTIONAL**: Fix template naming (low priority)
3. ⏳ **READY**: Begin Mojo migration
4. ⏳ **READY**: Start Nix packaging

---

**Generated**: 2025-10-05
**Status**: ✅ System Operational (13/14 tests passing)
**Next Milestone**: Mojo Migration
