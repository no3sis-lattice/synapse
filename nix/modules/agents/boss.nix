# Boss Agent Module
# L0 Orchestrator - Bridge coordinator between Internal and External tracts
#
# From AGENT_IDENTITY_CATALOGUE.md:
# - Level: 0 (Root)
# - Tract: CROSS (manages both poles)
# - Archetype: orchestrator-meta
# - Particles: 25 (orchestration, monitoring, synthesis, planning, communication)

{ pkgs, pythonBase, neo4jTools, system }:

let
  # Boss agent definition (Claude Code agent)
  agentDefinition = ../../.claude/agents/boss.md;

  # Boss agent package
  bossPackage = pkgs.stdenv.mkDerivation {
    pname = "synapse-boss-agent";
    version = "0.1.0";

    src = ../..;  # Root of synapse project

    buildInputs = [ pythonBase.env ];

    dontBuild = true;

    installPhase = ''
      mkdir -p $out/share/synapse/agents

      # Install agent definition
      cp ${agentDefinition} $out/share/synapse/agents/boss.md

      # Create wrapper script for Boss agent invocation
      mkdir -p $out/bin
      cat > $out/bin/synapse-boss <<'EOF'
      #!/usr/bin/env bash
      # Boss agent wrapper
      # This would integrate with Claude Code CLI when available
      echo "Boss agent (L0 Orchestrator)"
      echo "Tract: CROSS (bridge between Internal/External)"
      echo "Particles: 25 (orchestration, monitoring, synthesis, planning, communication)"
      echo ""
      echo "Agent definition: $out/share/synapse/agents/boss.md"
      echo ""
      echo "To use: Invoke via Claude Code with @boss"
      EOF
      chmod +x $out/bin/synapse-boss
    '';

    meta = with pkgs.lib; {
      description = "Boss agent - L0 orchestrator for Synapse dual-tract architecture";
      homepage = "https://github.com/synapse-system";
      license = licenses.mit;
    };
  };

  # Boss particles (from LOGOS.md L0 definition)
  # These are conceptual definitions - implementation pending
  particles = {
    # Orchestration particles (bridge)
    task_router = "Routes tasks to appropriate tract/agent";
    priority_queue = "Manages task priorities (internal)";
    dependency_resolver = "Resolves task dependencies (internal)";
    pipeline_builder = "Builds execution pipelines (internal)";
    parallel_executor = "Executes parallel operations (external)";

    # Monitoring particles
    progress_tracker = "Tracks task progress (internal)";
    error_monitor = "Monitors errors (external)";
    performance_meter = "Measures performance (external)";
    resource_monitor = "Monitors resources (external)";
    deadlock_detector = "Detects deadlocks (internal)";

    # Synthesis particles (bridge)
    result_aggregator = "Aggregates results from tracts";
    conflict_resolver = "Resolves conflicts (internal)";
    pattern_extractor = "Extracts patterns (internal)";
    summary_generator = "Generates summaries (internal)";
    report_builder = "Builds reports (external)";

    # Planning particles (internal)
    goal_decomposer = "Decomposes goals";
    strategy_selector = "Selects strategies";
    path_optimizer = "Optimizes execution paths (uses MiniZinc)";
    risk_assessor = "Assesses risks";
    fallback_planner = "Plans fallbacks";

    # Communication particles (bridge/external)
    context_builder = "Builds context (bridge)";
    message_formatter = "Formats messages (external)";
    event_emitter = "Emits events (external)";
    log_writer = "Writes logs (external)";
    notification_sender = "Sends notifications (external)";
  };

in
{
  # Main boss agent package
  package = bossPackage;

  # Particle definitions (for documentation/future implementation)
  inherit particles;

  # Boss agent metadata
  meta = {
    id = "boss";
    level = 0;
    tract = "CROSS";
    archetype = "orchestrator-meta";
    particle_count = 25;
    internal_particles = 12;
    external_particles = 13;
    core_responsibilities = [
      "Global plan approval"
      "Tract balancing root policy"
      "Admission control for new dynamos"
    ];
    adaptation_hooks = {
      emits = [ "ADAPTATION_POLICY" ];
      consumes = [ ];
    };
    a2a_export = [ "system.listCapabilities" ];
    stability = "core";
  };

  # Integration with Neo4j tools
  withNeo4j = neo4jTools;
}
