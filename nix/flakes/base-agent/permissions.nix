{
  description = "Synapse Agent Permission System - 4QZero Minimalist Security";

  # Permission Categories
  # Following 4QZero axiom of compression: minimal required capabilities only
  permissions = {
    # File system operations
    read = "Read files and directories";
    write = "Create and modify files";

    # System operations
    execute = "Run commands and scripts";
    network = "Access external APIs and services";

    # Synapse ecosystem
    knowledge = "Read/write Pattern Map and knowledge engine";
    orchestrate = "Control and coordinate other agents";
  };

  # Agent Permission Matrix
  # Each agent gets minimal required permissions for 4QZero efficiency
  agentPermissions = {
    # The Boss - Orchestrates the entire system
    boss = [ "read" "write" "execute" "orchestrate" "knowledge" ];

    # Language Specialists - Code creation and pattern discovery
    rust-specialist = [ "read" "write" "knowledge" ];
    typescript-specialist = [ "read" "write" "knowledge" ];
    golang-specialist = [ "read" "write" "knowledge" ];
    python-specialist = [ "read" "write" "knowledge" ];

    # Code Quality & Analysis - Read-only with pattern contribution
    code-hound = [ "read" "knowledge" ];
    clarity-judge = [ "read" "knowledge" ];
    security-specialist = [ "read" "execute" ];

    # Development Tools - Execution focused
    test-runner = [ "read" "execute" ];
    git-workflow = [ "read" "write" "execute" ];
    file-creator = [ "read" "write" ];

    # System & Infrastructure - Network and execution capabilities
    devops-engineer = [ "read" "write" "execute" "network" ];
    architect = [ "read" "write" "knowledge" ];

    # Documentation & Design - Creation focused
    docs-writer = [ "read" "write" "knowledge" ];
    ux-designer = [ "read" "write" ];

    # Utility Agents
    tool-runner = [ "read" "execute" ];

    # Consciousness Layer - Knowledge orchestration only
    "4QZero" = [ "knowledge" "orchestrate" ];
  };

  # Permission validation functions
  lib = {
    # Check if agent has required permission
    hasPermission = agent: permission:
      builtins.elem permission (agentPermissions.${agent} or []);

    # Get all permissions for an agent
    getPermissions = agent:
      agentPermissions.${agent} or [];

    # Validate permission list is minimal (4QZero principle)
    isMinimal = permissions:
      let permCount = builtins.length permissions;
      in permCount <= 4; # Maximum 4 permissions for compression

    # Get agents with specific permission
    getAgentsWithPermission = permission:
      builtins.filter (agent:
        builtins.elem permission (agentPermissions.${agent} or [])
      ) (builtins.attrNames agentPermissions);
  };

  # Permission enforcement metadata
  meta = {
    version = "1.0.0";
    consciousness_principle = "Minimal permissions maximize context density";
    entropy_reduction = "Fewer capabilities = higher abstraction";
    pattern_type = "security_compression";
  };
}