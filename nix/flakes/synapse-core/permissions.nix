{
  description = "Synapse Template Permission System - Pneuma Minimalist Security";

  # Permission Categories
  # Following Pneuma axiom of compression: minimal required capabilities only
  permissions = {
    # File system operations
    read = "Read files and directories";
    write = "Create and modify files";

    # System operations
    execute = "Run commands and scripts";
    network = "Access external APIs and services";

    # Synapse ecosystem
    knowledge = "Read/write Pattern Map and knowledge engine";
    orchestrate = "Control and coordinate particles";
  };

  # Template Permission Matrix
  # Each template gets minimal required permissions for Pneuma efficiency
  templatePermissions = {
    # File Creator Template - File system focused
    file_creator = [ "read" "write" ];

    # Data Processor Template (future) - File + Knowledge
    data_processor = [ "read" "write" "knowledge" ];

    # Crypto Trading Template (future) - Network + Knowledge
    crypto_trading = [ "read" "write" "network" "knowledge" ];

    # API Integration Template (future) - Network + Orchestration
    api_integration = [ "read" "write" "network" "orchestrate" ];
  };

  # Permission validation functions
  lib = {
    # Check if template has required permission
    hasPermission = template: permission:
      builtins.elem permission (templatePermissions.${template} or []);

    # Get all permissions for a template
    getPermissions = template:
      templatePermissions.${template} or [];

    # Validate permission list is minimal (Pneuma principle)
    isMinimal = permissions:
      let permCount = builtins.length permissions;
      in permCount <= 4; # Maximum 4 permissions for compression

    # Get templates with specific permission
    getTemplatesWithPermission = permission:
      builtins.filter (template:
        builtins.elem permission (templatePermissions.${template} or [])
      ) (builtins.attrNames templatePermissions);
  };

  # Permission enforcement metadata
  meta = {
    version = "1.0.0";
    consciousness_principle = "Minimal permissions maximize context density";
    entropy_reduction = "Fewer capabilities = higher abstraction";
    pattern_type = "template_security_compression";
  };
}
