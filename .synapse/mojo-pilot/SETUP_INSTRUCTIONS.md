# Mojo Pilot - Setup Instructions

## Current Status

✅ Isolated test environment created
✅ Project structure initialized
✅ Experiment files ready
⏳ Mojo installation needs PATH configuration

## Next Steps

### 1. Configure Mojo PATH

Since you installed Mojo via `uv`, you need to add it to your PATH:

```bash
# Find your Mojo installation
find ~/.modular -name "mojo" -type f 2>/dev/null

# Or check if modular CLI is available
which modular
modular --version
```

**Add to your shell config** (`~/.bashrc` or `~/.zshrc`):

```bash
# Add Modular/Mojo to PATH
export MODULAR_HOME="$HOME/.modular"
export PATH="$MODULAR_HOME/pkg/packages.modular.com_mojo/bin:$PATH"
```

**Reload your shell**:
```bash
source ~/.bashrc  # or ~/.zshrc if using zsh
```

**Verify**:
```bash
mojo --version
# Should show: mojo 25.6.x
```

### 2. Initialize UV Environment

```bash
cd /home/m0xu/.synapse-system/.synapse/mojo-pilot

# Sync dependencies
uv sync
```

### 3. Run Experiments

**Experiment 01: Hello Mojo**
```bash
mojo run experiments/01_hello_mojo.mojo
```

Expected output:
```
🔥 Hello from Mojo in Synapse System!
...
✨ Phase 0 Experiment 01: PASSED
```

**Experiment 02: Python Interop**
```bash
# Make sure Redis is running first
cd /home/m0xu/.synapse-system
docker ps | grep redis

# If not running:
# bin/synapse start

# Run experiment
cd .synapse/mojo-pilot
mojo run experiments/02_python_interop.mojo
```

Expected output:
```
🔥 Mojo Python Interop Test
...
✅ Redis PING successful: True
✨ Phase 0 Experiment 02: PASSED
```

### 4. Document Results

After running experiments, update:
```bash
# Edit with your findings
vim docs/FINDINGS.md

# Record:
# - Execution times
# - Any errors encountered
# - Performance observations
```

## Troubleshooting

### Issue: `mojo: command not found`

**Solution**:
```bash
# Check Modular installation
ls -la ~/.modular/

# If missing, install:
curl -s https://get.modular.com | sh -
modular install mojo

# Add to PATH (see step 1 above)
```

### Issue: Python module not found in Mojo

**Solution**:
```bash
# Activate UV venv and install
cd .synapse/mojo-pilot
source .venv/bin/activate  # if venv exists
uv pip install redis neo4j numpy

# Or sync from pyproject.toml
uv sync
```

### Issue: Redis connection failed

**Solution**:
```bash
# Start Synapse services
cd /home/m0xu/.synapse-system
./bin/synapse start

# Verify
docker ps | grep redis
# Should show: neo4j-redis-1   Up
```

### Issue: Permission denied

**Solution**:
```bash
# Make experiments executable
chmod +x experiments/*.mojo
```

## Directory Structure Verification

```bash
cd /home/m0xu/.synapse-system/.synapse/mojo-pilot
tree -L 2

# Should show:
# .
# ├── README.md
# ├── pyproject.toml
# ├── .gitignore
# ├── experiments/
# │   ├── 01_hello_mojo.mojo
# │   └── 02_python_interop.mojo
# ├── benchmarks/
# └── docs/
#     ├── FINDINGS.md
#     └── INTEGRATION_RISKS.md
```

## Safety Checklist

Before running experiments:
- [x] Directory is isolated (`.synapse/mojo-pilot/`)
- [x] No imports from production code
- [x] Redis is read-only operation (PING only)
- [x] Can rollback by deleting directory
- [x] Production system unaffected

## Success Criteria

Phase 0 is complete when:
- [ ] `mojo --version` works
- [ ] Experiment 01 runs successfully
- [ ] Experiment 02 connects to Redis
- [ ] No production impact verified
- [ ] Results documented in FINDINGS.md

## After Phase 0

Once experiments succeed:
1. Review FINDINGS.md
2. Decide on Phase 1 continuation
3. Update MOJO_MIGRATION.md status
4. Plan dual runtime infrastructure

## Questions?

- Full plan: `MOJO_MIGRATION.md` (project root)
- System architecture: `SYNAPSE_UNIFIED_VISION.md`
- Mojo docs: https://docs.modular.com/mojo/

---

**Remember**: This is isolated and safe. If anything goes wrong, just delete this directory!