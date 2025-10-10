# Neo4j Tools Module
# Knowledge engine components: Pattern Map, Context Manager, Search
#
# Provides:
# - Neo4j Python scripts and utilities
# - BGE-M3 semantic search integration (via .venv-ml)
# - Pattern ingestion and search tools
# - Health check utilities

{ pkgs, pythonBase, system }:

let
  # Neo4j tools require additional ML dependencies
  # These are installed in .venv-ml due to UV packaging bug (see CHANGELOG Day 10)
  mlPythonPackages = ps: with ps; [
    # sentence-transformers and dependencies are in .venv-ml
    # We reference that environment when needed
  ];

  # Create wrapper scripts for Neo4j tools
  mkNeo4jScript = name: script:
    pythonBase.mkPythonScript {
      inherit name;
      script = ".synapse/neo4j/${script}";
      runtimeInputs = [ ];
    };

in
{
  # Main Neo4j tools
  tools = {
    # Health check utility
    health = mkNeo4jScript "synapse-health" "synapse_health.py";

    # Pattern search (uses BGE-M3 from .venv-ml)
    search = mkNeo4jScript "synapse-search" "pattern_search.py";

    # Pattern ingestion
    ingest = mkNeo4jScript "synapse-ingest" "ingestion.py";

    # Context manager (Redis + Neo4j integration)
    context = pkgs.writeShellScriptBin "synapse-context" ''
      export PYTHONPATH="${pythonBase.env}/${pythonBase.env.sitePackages}:$PYTHONPATH"
      exec ${pythonBase.env}/bin/python .synapse/neo4j/context_manager.py "$@"
    '';
  };

  # Benchmark utilities (for performance testing)
  benchmarks = {
    search = mkNeo4jScript "benchmark-search" "benchmark_search.py";
    ffi = mkNeo4jScript "benchmark-ffi" "benchmark_ffi.py";
    detailed = mkNeo4jScript "benchmark-detailed" "benchmark_detailed.py";
  };

  # Combined package with all Neo4j tools
  package = let
    self' = { inherit tools; };
  in pkgs.buildEnv {
    name = "synapse-neo4j-tools";
    paths = [
      tools.health
      tools.search
      tools.ingest
      tools.context
    ];
  };

  # Note about .venv-ml
  # The ML environment (.venv-ml) with BGE-M3 is created via pip
  # due to UV packaging bug. See CHANGELOG Day 10 for details.
  # Noesis MCP server uses SYNAPSE_PYTHON env var to point to .venv-ml
}
