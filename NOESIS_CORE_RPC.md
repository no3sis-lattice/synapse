# Noesis Core RPC: A Typed, Streaming Control Plane for Synapse

Status: Proposal (v0.1)
Owners: Noesis Lattice
Last updated: 2025-10-16

## Summary
- Keep MCP as a thin IDE adapter.
- Introduce a local gRPC-based “Noesis Core RPC” sidecar (over Unix domain sockets) as the authoritative control plane for search, memory, compression operators (CIG‑3), and planning.
- Use Protobuf contracts, bidirectional streaming, deadlines/cancellations, and a zero-copy data plane (Arrow Flight or shared memory) for large tensors.
- This aligns the running system with the Sovereign Intelligence/Compression Lattice direction in MAHAKALA_FRAMEWORK.md while remaining compatible with existing agents.

Why move beyond MCP?
- MCP over stdio is great for simple tools in editors but is single-shot and untyped. For Synapse:
  - We need typed, versionable contracts across Search, Memory, Operators, and Health.
  - We need streaming (results, logs, partial progress), backpressure, and cancellation.
  - We need a zero-copy path to feed matrices/vectors into Mojo and CIG‑3 without JSON/stdlib overhead.
  - We want built-in observability (OpenTelemetry), deadlines, and status codes.

Scope and alignment with current docs
- Aligns with:
  - MAHAKALA_FRAMEWORK.md: Intelligence as compression; operators, not agents, as the core primitive.
  - CIG‑3 docs (MNEUMONIC_LATTICE.md, CIG3.md): Defines a pipeline that can be exposed as operators.
  - 3-layer-architecture-current-state.md: Layer 2 (Noesis) is currently a thin MCP subprocess bridge; this introduces the real control plane with live health metrics to replace stale figures (e.g., “247 patterns”).
- Compatible with:
  - PRIME_DUALITY_HIERARCHY.md and LOGOS.md: MCP remains the external UX adapter; Core RPC is the “corpus callosum” for typed interop across tracts/operators.
  - NIX_GUIDE.md, MOJO_PILOT_PLAN.md: Future Mojo acceleration uses Core RPC’s data plane without changing IDE workflows.

Architecture at a glance
```
Agents (IDE, Slack, CLI) ── MCP (UI adapter, stdio JSON) ─┐
                                                           │
                                                     Noesis Core RPC (sidecar over UDS)
                                                     - gRPC/Protobuf API
                                                     - Streams, deadlines, cancel
                                                     - Health, Search, Memory
                                                     - Operator runtime (CIG‑3, compression)
                                                     - OTEL tracing, metrics
                                                           │
                                                           ├── Synapse Engine (Python)
                                                           │     - Neo4j, Redis, Vector DB
                                                           │     - Ingestion, Search, Memory adapters
                                                           │
                                                           └── Mojo FFI libraries (hot paths)
                                                                 - Pattern search, spectral SVD, router
                                                                 - Zero-copy tensors via Flight/shm
```

Design goals
- Typed, evolvable contracts: Protobuf services and messages with semantic versioning.
- Streaming-first: Server streams for search hits, operator progress, logs.
- Deadlines and cancellation: Every call supports deadlines; clients can cancel.
- Zero-copy for large payloads: Use Arrow Flight or shared-memory handles for tensors; keep metadata in gRPC headers/trailers.
- Observability: OpenTelemetry interceptors, standardized error codes, request IDs, and structured events.
- Security: Local-first via Unix domain sockets; optional mTLS if remote.

Core API surface (v0)
- SearchPatternMap: Query and stream hits with code refs.
- ComputeContext: Retrieve top‑k hybrid memory snippets for repo/user/query.
- WriteMemory: Persist episodic/semantic memories; returns ids and embedding keys.
- RunOperator: Execute a Compression/CIG‑3 operator; stream progress and results.
- CheckHealth: Live counts for Neo4j nodes/rels, vector rows, Redis keys, model warm status; version string.

Proto sketch (authoritative in api/noesis.proto)
```proto
syntax = "proto3";
package noesis.v1;

service NoesisCore {
  rpc SearchPatternMap(SearchRequest) returns (stream SearchHit);
  rpc ComputeContext(ContextRequest) returns (ContextReply);
  rpc WriteMemory(WriteMemoryRequest) returns (WriteMemoryReply);
  rpc RunOperator(RunOperatorRequest) returns (stream OperatorEvent);
  rpc CheckHealth(HealthRequest) returns (HealthReply);
}

message SearchRequest {
  string query = 1;
  uint32 top_k = 2;
  string repo_id = 3;
  repeated string tags = 4;
  int64 deadline_ms = 5;
}

message SearchHit {
  string id = 1;
  string title = 2;
  string path = 3;
  double score = 4;
  repeated CodeRef refs = 5;
}

message CodeRef {
  string file = 1;
  uint32 start_line = 2;
  uint32 end_line = 3;
  string snippet = 4;
}

message ContextRequest {
  string repo_id = 1;
  string user_id = 2;
  string query = 3;
  repeated string concept_labels = 4;
  uint32 top_k = 5;
}

message ContextReply {
  repeated MemoryItem items = 1;
}
message MemoryItem {
  string id = 1;
  string text = 2;
  double score = 3;
  repeated string tags = 4;
}

message WriteMemoryRequest {
  string repo_id = 1;
  string user_id = 2;
  string session_id = 3;
  string text = 4;
  repeated string concept_labels = 5;
  string type = 6; // episodic|semantic
}
message WriteMemoryReply {
  string memory_id = 1;
  string embedding_key = 2;
}

message RunOperatorRequest {
  string operator_id = 1;      // e.g., "cig3/spectral_svd", "compression/mtf_ranker"
  string level = 2;            // lattice level or "auto"
  bytes payload = 3;           // small inputs inline; large payloads via data-plane handle
  map<string,string> params = 4;
}

message OperatorEvent {
  string stage = 1;            // "start","progress","result","error","log"
  double progress = 2;         // 0..1
  bytes data = 3;              // small results inline
  string msg = 4;              // human-readable notes/errors
}

message HealthRequest {}
message HealthReply {
  uint64 neo4j_nodes = 1;
  uint64 neo4j_rels = 2;
  uint64 vector_rows = 3;
  uint64 redis_embeddings = 4;
  uint64 redis_results = 5;
  bool model_warm = 6;
  string version = 7;
}
```

Data plane for large tensors
- Option A: Apache Arrow Flight
  - Pros: Columnar, language-agnostic, built for high-throughput. Good fit for embedding matrices, SVD bases, attention maps.
  - Pattern: Client uploads tensors via Flight; gRPC carries a “flight://” ticket.
- Option B: Shared memory ring buffers
  - Pros: Minimal copy over UDS; excellent for local-only, Mojo FFI-close paths.
  - Pattern: gRPC returns shm key/offset/shape/dtype; Mojo libraries map and operate in place.

Both options can coexist: default to Flight; fall back to shm (or vice versa) based on platform and operator needs.

Operator catalog (initial)
- cig3/attention_local (Φ)
- cig3/spectral_svd (Σ)
- cig3/topology_persistence (Π)
- cig3/invariant_csd (Ψ)
- compression/mtf_ranker
- compression/pattern_search (Mojo accelerated)
- memory/write, memory/retrieve (composed into ComputeContext)

Error model and cancellations
- Status codes: INVALID_ARGUMENT, NOT_FOUND, DEADLINE_EXCEEDED, FAILED_PRECONDITION, UNAVAILABLE, INTERNAL.
- Deadlines: Clients set per-RPC deadlines; server honors with cooperative cancellation.
- Cancellation: Client-side cancellation propagates to operators; long-running CIG‑3 steps must check tokens and yield.

Security and deployment
- Transport: Unix domain socket at /run/noesis/core.sock (configurable).
- Permissions: Filesystem ACLs/user groups gate which processes can connect.
- Optional remote mode: mTLS and JWT auth if exposed beyond local host (not recommended initially).

Observability
- OpenTelemetry interceptors:
  - Trace spans per RPC with attributes: repo_id, user_id (pseudonymous), operator_id, result counts, latency bins.
  - Metrics: RPC latency histograms, active streams, operator run counts, error rates.
- Structured logs correlated via request_id header.

Compatibility with current Layer 1–3 stack
- Layer 1 (Agents / MCP): Keep existing 4 MCP tools; progressively swap MCP tool internals to call Core RPC.
- Layer 2 (Noesis MCP server): Becomes a facade that translates MCP JSON to Core RPC calls.
- Layer 3 (Synapse Engine): Implements Core RPC handlers by calling existing scripts/modules (synapse_search.py, vector_engine.py, ingestion.py, CIG‑3 pipeline), then gradually inlines or rewires for performance.
- Mojo: Core RPC’s RunOperator connects to Mojo FFI libs for hot paths (pattern search, spectral SVD, message router), passing tensors via Flight/shm.

Live health replaces stale numbers
- Replace hard-coded “247 patterns” and inconsistent “consciousness” values with CheckHealth live counts:
  - Neo4j node/rel counts
  - Vector row count
  - Redis key counts
  - Model warm state
- Surface these in MCP check_system_health responses via the facade so agents see real-time truth.

Client usage examples

Python client snippet (Search and context)
```python
import grpc
from noesis.v1 import noesis_pb2, noesis_pb2_grpc

channel = grpc.insecure_channel("unix:/run/noesis/core.sock")
stub = noesis_pb2_grpc.NoesisCoreStub(channel)

# Search stream
stream = stub.SearchPatternMap(noesis_pb2.SearchRequest(
    query="error handling rust",
    top_k=5,
    repo_id="repo://noesis-lattice/synapse"
))
for hit in stream:
    print(hit.title, hit.path, hit.score)

# Compose context for prompts
ctx = stub.ComputeContext(noesis_pb2.ContextRequest(
    repo_id="repo://noesis-lattice/synapse",
    user_id="user://sub0xdai",
    query="how do we handle unwrap? in rust modules",
    concept_labels=["rust", "error-handling"],
    top_k=8
))
print([item.text for item in ctx.items[:3]])
```

Python client snippet (RunOperator streaming)
```python
events = stub.RunOperator(noesis_pb2.RunOperatorRequest(
    operator_id="cig3/spectral_svd",
    level="L2",
    payload=b"...",  # or pass Flight ticket via metadata
    params={"energy_threshold": "0.90", "k_max": "128"}
))
for ev in events:
    if ev.stage == "progress":
        print(f"{ev.progress*100:.0f}%")
    elif ev.stage == "result":
        # Small payload inline; large results via data plane handle
        ...
    elif ev.stage == "error":
        raise RuntimeError(ev.msg)
```

Migration plan (6 steps)

1) Stand up the sidecar (Week 1)
- Implement NoesisCore gRPC server (UDS), with CheckHealth and SearchPatternMap backed by current synapse_search/context_manager/vector_engine.
- Add OpenTelemetry, deadlines, and minimal config.

2) Memory path (Week 1–2)
- Implement WriteMemory and ComputeContext.
- Adopt the simple memory schema and Cypher from earlier guidance; compute embeddings; key vector rows by memory_id.

3) MCP facade (Week 2)
- Patch existing MCP tools to call Core RPC under the hood:
  - search_pattern_map → SearchPatternMap
  - check_system_health → CheckHealth
  - context retrieval pre‑prompt hook → ComputeContext
- Preserve tool signatures to avoid agent changes.

4) Operator bridge (Week 3–4)
- Expose RunOperator and wire CIG‑3 stages (Φ, Σ, Π, Ψ) to existing Python pipeline.
- Add Mojo hot path for spectral SVD or pattern search as available; adopt Flight/shm for tensors.

5) Observability and live dashboards (Week 4)
- Export OTEL traces/metrics; add a simple dashboard for health counts, operator latencies, cache hit rates.
- Remove static “247 patterns” references; link dashboards as source of truth.

6) Cutover and cleanup (Week 5)
- Make MCP tools use only Core RPC; treat subprocess calls as fallback.
- Document the new API and client stubs; begin adding new tools as RPCs directly.

Risks and mitigations
- Risk: Stdio/MCP consumers diverge from real contracts
  - Mitigation: Keep MCP thin; generate clients from proto; test facade in CI.
- Risk: Large payload handling complexity
  - Mitigation: Start with inline for small inputs; enable Flight/shm only for operator paths that need it.
- Risk: Path drift (old vs new script dirs)
  - Mitigation: CheckHealth verifies script and data paths; CI checks env; deprecate legacy directories.
- Risk: Versioning churn
  - Mitigation: Prefix services with noesis.v1; add new fields as optional; avoid breaking changes.

Acceptance criteria
- gRPC server reachable at unix:/run/noesis/core.sock with documented proto.
- SearchPatternMap and CheckHealth operational; MCP facade calls these.
- ComputeContext and WriteMemory in use by at least one agent path (memory visible in prompts).
- Live health counts match reality (no hard-coded figures remain).
- At least one CIG‑3 operator runs via RunOperator with streaming progress.
- OTEL traces for RPCs visible in the chosen backend.

Appendix A: Mapping to project docs
- MAHAKALA_FRAMEWORK.md (“Sovereign Intelligence Framework”)
  - Operators, compression, and entropy-centric design map to RunOperator and the operator catalog. This RPC formalizes operators as first-class citizens.
- CIG‑3 docs (MNEUMONIC_LATTICE.md, CIG3.md)
  - Φ/Σ/Π/Ψ become addressable operators; Ψ can be logged/returned as a metric in OperatorEvent.
- 3-layer-architecture-current-state.md
  - Replaces subprocess invocation with Core RPC; improves health truthfulness; preserves MCP for IDEs.
- MOJO_PILOT_PLAN.md
  - Zero-copy data plane + FFI hooks make Mojo libraries pluggable without changing agent UX.

Appendix B: Configuration keys (suggested)
```ini
[core]
socket_path = /run/noesis/core.sock
max_concurrency = 64
otel_endpoint = http://localhost:4317
arrow_flight = disabled  # or "enabled"
shared_memory = enabled

[data]
neo4j_uri = bolt://localhost:7687
neo4j_user = neo4j
neo4j_password = ...
redis_host = localhost
redis_port = 6379
vector_db_path = /var/lib/noesis/vectors.db

[operators]
enable_cig3 = true
enable_mojo_svd = false
```

Appendix C: Glossary
- Core RPC: The typed control plane for Noesis, served over gRPC on a Unix domain socket.
- Data plane: High-throughput channel for large tensors (Arrow Flight or shared memory).
- Operator: A compression or analysis function (e.g., CIG‑3 stage) callable via RunOperator.
- Facade: The MCP server that translates tool calls into Core RPC requests.

–––
