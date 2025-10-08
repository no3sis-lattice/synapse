
 Status: 3/4 tools working ✅

  Working Tools

  1. check_system_health - Returns comprehensive infrastructure status (Neo4j, Redis, Vector DB)
  2. get_coding_standard - Retrieves detailed coding standards with examples (8KB+ markdown content)
  3. get_project_template - Provides templates with variable substitution

  Issue Found

  search_pattern_map - Timing out after 30s

  Root cause: Noesis venv missing numpy dependencies; subprocess uses wrong Python interpreter

  Fix: Update /home/m0xu/1-projects/noesis/src/noesis/server.py:59:
  # Change to use Neo4j venv Python
  neo4j_python = "/home/m0xu/.synapse-system/.synapse/neo4j/.venv/bin/python"
  cmd = [neo4j_python, str(script_path)] + args + ["--json"]

  Full test report includes response examples, available standards (C, Golang, Rust, TypeScript, Zig), and 11 available templates.
