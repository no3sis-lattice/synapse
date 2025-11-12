# Synapse Infrastructure Configuration

**Date**: 2025-11-12
**Status**: Phase 0 Complete - Infrastructure Operational

---

## Services

### Neo4j (Graph Database)
- **Container**: synapse-neo4j
- **Image**: neo4j:latest
- **Ports**:
  - HTTP: localhost:17474 (public port offset by +10000 to avoid conflicts)
  - Bolt: localhost:17687 (internal: 7687)
- **Credentials**:
  - Username: neo4j
  - Password: synapse2025
- **Data**: /home/m0xu/1-projects/synapse/.synapse/data/neo4j
- **Plugins**: APOC (enabled)

### Redis (Cache Layer)
- **Container**: synapse-redis
- **Image**: redis:7-alpine
- **Port**: localhost:16379 (public port offset by +10000)
- **Data**: /home/m0xu/1-projects/synapse/.synapse/data/redis
- **Persistence**: AOF (Append-Only File) enabled

### BGE-M3 (Embedding Model)
- **Model**: BAAI/bge-m3
- **Location**: /home/m0xu/1-projects/synapse/.synapse/data/models/bge-m3
- **Size**: 2182 MB
- **Dimensions**: 1024D (BGE-M3 standard)
- **Status**: Downloaded and cached

---

## Python Environment

### .venv-ml (ML Dependencies)
- **Location**: /home/m0xu/1-projects/synapse/.venv-ml
- **Python**: 3.13.x
- **Packages**:
  - neo4j>=5.0.0 (graph database client)
  - redis>=5.0.0 (cache client)
  - sentence-transformers (BGE-M3 wrapper)
  - torch (ML backend)
  - numpy (numerical computing)
  - tqdm (progress bars)

---

## Port Mapping

**Why offset ports by +10000?**

The system already had Neo4j/Redis running on standard ports (7474, 7687, 6379) with unknown credentials. Rather than conflict or attempt to kill system services, we deploy Synapse infrastructure on offset ports for clean isolation.

| Service | Standard Port | Synapse Port | Reason |
|---------|---------------|--------------|--------|
| Neo4j HTTP | 7474 | 17474 | +10000 offset |
| Neo4j Bolt | 7687 | 17687 | +10000 offset |
| Redis | 6379 | 16379 | +10000 offset |

---

## Management Commands

**Note**: Infrastructure uses Podman (not Docker). The `podman-compose.sh` wrapper sets the correct socket.

### Start Infrastructure
```bash
cd /home/m0xu/1-projects/synapse/.synapse
./podman-compose.sh up -d
```

### Stop Infrastructure
```bash
cd /home/m0xu/1-projects/synapse/.synapse
./podman-compose.sh down
```

### View Logs
```bash
./podman-compose.sh logs -f neo4j    # Neo4j logs
./podman-compose.sh logs -f redis    # Redis logs
```

### Alternative (Direct Podman)
```bash
export DOCKER_HOST=unix:///run/user/1000/podman/podman.sock
podman compose up -d
```

### Health Check
```bash
cd /home/m0xu/1-projects/synapse/.synapse/neo4j
/home/m0xu/1-projects/synapse/.venv-ml/bin/python synapse_health.py
```

### Access Neo4j Browser
```
http://localhost:17474
```

---

## Current Status

### Infrastructure: ✓ Operational

- Neo4j: **✓ Running** (0 patterns, 0 nodes)
- Redis: **✓ Running** (0 keys)
- BGE-M3: **✓ Cached** (2182 MB)

### Consciousness: Ψ = 0.000 (dormant)

**Reason**: Infrastructure exists but Pattern Map is empty. This is expected for Phase 0.

**Next Step**: Phase 1 - Build Synapse CLI tools (synapse_search, synapse_standard, synapse_template)

---

## Configuration Files

### .env (Environment Variables)
```bash
SYNAPSE_NEO4J_DIR=/home/m0xu/1-projects/synapse/.synapse/neo4j
SYNAPSE_PYTHON=/home/m0xu/1-projects/synapse/.venv-ml/bin/python
NEO4J_URI=bolt://localhost:17687
NEO4J_AUTH=neo4j/synapse2025
REDIS_HOST=localhost
REDIS_PORT=16379
```

### docker-compose.yml (Service Definitions)
Location: /home/m0xu/1-projects/synapse/.synapse/docker-compose.yml

---

## Disk Usage

- Neo4j data: ~50 MB (minimal, no patterns yet)
- Redis data: ~2 MB (empty cache)
- BGE-M3 model: 2182 MB
- Total: ~2.25 GB

---

**Created**: 2025-11-12
**Phase**: 0 (Infrastructure Deployment) - Complete
