#!/usr/bin/env python3
"""
Synapse System - Project Management
===================================

Handles project initialization, configuration, and agent deployment.
"""

import os
import yaml
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class ProjectManager:
    """Manages synapse project initialization and configuration"""

    def __init__(self, synapse_home: Path):
        self.synapse_home = synapse_home
        self.agents_source = synapse_home / ".synapse" / "agents"
        self.version_file = synapse_home / ".synapse" / "VERSION"

    def detect_language(self, project_dir: Path) -> str:
        """Detect project language from files"""
        if (project_dir / "Cargo.toml").exists():
            return "rust"
        elif (project_dir / "go.mod").exists():
            return "golang"
        elif (project_dir / "package.json").exists():
            return "typescript"
        elif any((project_dir / f).exists() for f in ["pyproject.toml", "requirements.txt", "setup.py"]):
            return "python"
        elif (project_dir / "build.zig").exists():
            return "zig"
        elif any((project_dir / f).exists() for f in ["Makefile", "CMakeLists.txt"]):
            return "c"
        else:
            return "unknown"

    def get_system_version(self) -> str:
        """Get current synapse system version"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return "unknown"

    def get_agent_versions(self) -> Dict[str, str]:
        """Get versions of all available agents with checksums"""
        versions = {}
        # Handle new directory-based agent structure
        for agent_dir in self.agents_source.iterdir():
            if agent_dir.is_dir():
                agent_name = agent_dir.name
                # Look for the main agent file
                agent_file = agent_dir / f"{agent_name}.md"
                if agent_file.exists():
                    # Use file modification time and content hash as version
                    content = agent_file.read_text()
                    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
                    mod_time = agent_file.stat().st_mtime
                    versions[agent_name] = f"{int(mod_time)}.{content_hash}"
                else:
                    # Fallback: use directory modification time
                    mod_time = agent_dir.stat().st_mtime
                    versions[agent_name] = f"{int(mod_time)}.000"
        return versions

    def get_universal_agents(self) -> List[str]:
        """Get list of universal agents that should be included in all projects"""
        return [
            "boss",
            "code-hound",
            "git-workflow",
            "test-runner",
            "file-creator",
            "architect",
            "devops-engineer",
            "docs-writer",
            "security-specialist",
            "ux-designer",
            "pneuma"
        ]

    def get_language_specialists(self) -> List[str]:
        """Get list of all language specialist agents"""
        return [
            "rust-specialist",
            "golang-specialist",
            "python-specialist",
            "typescript-specialist"
        ]

    def get_agent_directory_mapping(self) -> Dict[str, str]:
        """Map expected agent names to actual directory names"""
        return {
            # Standard mappings where name matches directory
            "boss": "boss",
            "code-hound": "code-hound",
            "git-workflow": "git-workflow",
            "test-runner": "test-runner",
            "file-creator": "file-creator",
            "architect": "architect",
            "devops-engineer": "devops-engineer",
            "docs-writer": "docs-writer",
            "security-specialist": "security-specialist",
            "ux-designer": "ux-designer",
            "pneuma": "pneuma",
            # Language specialists - both old and new directory names
            "rust-specialist": "rust-specialist",
            "golang-specialist": "golang-specialist",
            "python-specialist": "python-specialist",
            "typescript-specialist": "typescript-specialist",
            # Legacy mappings for backward compatibility
            "synapse-project-manager": "boss",  # Renamed agent
            "rust-dev": "rust-specialist",
            "goland-dev": "golang-specialist",
            "python-dev": "python-specialist",
            "typescript-dev": "typescript-specialist"
        }

    def load_project_config(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """Load project configuration from .synapse.yml"""
        config_file = project_dir / ".synapse.yml"
        if not config_file.exists():
            return None

        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Failed to load project config: {e}")
            return None

    def save_project_config(self, project_dir: Path, config: Dict[str, Any]) -> None:
        """Save project configuration to .synapse.yml"""
        config_file = project_dir / ".synapse.yml"
        try:
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            raise Exception(f"Failed to save project config: {e}")

    def copy_or_link_agent(self, agent_name: str, project_dir: Path, use_links: bool = False) -> bool:
        """Copy or symlink agent to project directory"""
        # Get the actual directory name for this agent
        directory_mapping = self.get_agent_directory_mapping()
        actual_dir_name = directory_mapping.get(agent_name, agent_name)

        # Try multiple source patterns
        source_file = None
        agent_dir = self.agents_source / actual_dir_name

        if agent_dir.is_dir():
            # New directory-based structure
            # Try main agent file first
            potential_sources = [
                agent_dir / f"{actual_dir_name}.md",
                agent_dir / f"{agent_name}.md",
                # Fallback to compressed version if available
                agent_dir / f"{actual_dir_name.replace('-', '_')}_compressed.md",
                # Fallback to prompt version
                agent_dir / f"{actual_dir_name.replace('-', '_')}_prompt.md"
            ]

            for potential_source in potential_sources:
                if potential_source.exists():
                    source_file = potential_source
                    break
        else:
            # Legacy flat file structure
            source_file = self.agents_source / f"{agent_name}.md"

        if not source_file or not source_file.exists():
            print(f"Warning: Agent {agent_name} not found (tried {actual_dir_name} directory)")
            return False

        target_file = project_dir / ".claude" / "agents" / f"{agent_name}.md"
        target_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            if use_links:
                # Create symlink
                if target_file.exists() or target_file.is_symlink():
                    target_file.unlink()
                target_file.symlink_to(source_file.resolve())
                print(f"✓ Linked {agent_name} agent")
            else:
                # Copy file
                shutil.copy2(source_file, target_file)
                print(f"✓ Added {agent_name} agent")
            return True
        except Exception as e:
            print(f"Warning: Failed to deploy {agent_name} agent: {e}")
            return False

    def initialize_project(self, project_dir: Path, link_agents: bool = False) -> None:
        """Initialize a project with synapse agents and configuration"""
        project_dir = project_dir.resolve()

        if not project_dir.exists():
            raise Exception(f"Directory does not exist: {project_dir}")

        if not project_dir.is_dir():
            raise Exception(f"Not a directory: {project_dir}")

        if not os.access(project_dir, os.W_OK):
            raise Exception(f"Directory is not writable: {project_dir}")

        # Detect project language
        language = self.detect_language(project_dir)
        if language == "unknown":
            print("⚠️  Could not detect project language")
            print("   Supported: Cargo.toml (rust), package.json (typescript), go.mod (golang), pyproject.toml (python)")
            language = "generic"
        else:
            print(f"✓ Detected language: {language}")

        # Create directory structure
        claude_dir = project_dir / ".claude"
        agents_dir = claude_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        # Create synapse context directory
        synapse_dir = project_dir / ".synapse"
        context_dir = synapse_dir / "context"
        context_dir.mkdir(parents=True, exist_ok=True)

        # Deploy universal agents
        universal_agents = self.get_universal_agents()
        deployed_agents = []

        for agent in universal_agents:
            if self.copy_or_link_agent(agent, project_dir, link_agents):
                deployed_agents.append(agent)

        # Deploy all language specialist agents
        language_specialists = self.get_language_specialists()
        for lang_agent in language_specialists:
            if self.copy_or_link_agent(lang_agent, project_dir, link_agents):
                deployed_agents.append(lang_agent)

        # Get current versions for tracking
        system_version = self.get_system_version()
        agent_versions = self.get_agent_versions()

        # Create project configuration
        config = {
            "version": "1.0",
            "language": language,
            "synapse_home": str(self.synapse_home),
            "synapse_version": system_version,
            "project_name": project_dir.name,
            "knowledge_paths": [
                "./docs",
                "./README.md",
                "./CHANGELOG.md"
            ],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "agent_versions": {
                agent: agent_versions.get(agent, "unknown")
                for agent in deployed_agents
            },
            "deployment_method": "symlink" if link_agents else "copy"
        }

        self.save_project_config(project_dir, config)
        print("✓ Created .synapse.yml configuration")

        # Summary
        print(f"\n✅ Project initialized successfully!")
        print(f"\n📁 Available agents:")
        for agent in deployed_agents:
            print(f"   • {agent}")

        print(f"\n💡 Usage in Claude Code:")
        print(f"   @boss help with this {language} project")
        print(f"   @rust-specialist implement error handling patterns")
        print(f"   @golang-specialist optimize concurrent operations")
        print(f"   @python-specialist improve data processing")
        print(f"   @typescript-specialist create React components")
        print(f"   @code-hound review my code for quality issues")
        print(f"   @git-workflow create feature branch and PR")

        deployment_method = "symlinked" if link_agents else "copied"
        print(f"\n🔗 Agents are {deployment_method} ({'auto-update' if link_agents else 'manual update'})")
        if not link_agents:
            print(f"   Run 'synapse update' to get agent updates")

    def get_project_agents(self, project_dir: Path) -> List[str]:
        """Get list of agents currently deployed in project"""
        agents_dir = project_dir / ".claude" / "agents"
        if not agents_dir.exists():
            return []

        agents = []
        for agent_file in agents_dir.glob("*.md"):
            agents.append(agent_file.stem)
        return sorted(agents)

    def is_agent_symlinked(self, project_dir: Path, agent_name: str) -> bool:
        """Check if an agent is symlinked rather than copied"""
        agent_file = project_dir / ".claude" / "agents" / f"{agent_name}.md"
        return agent_file.is_symlink() if agent_file.exists() else False

    def get_agent_checksum(self, agent_path: Path) -> str:
        """Get checksum of agent file"""
        if not agent_path.exists():
            return ""
        content = agent_path.read_text()
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def validate_project(self, project_dir: Path) -> Dict[str, Any]:
        """Validate project configuration and agents"""
        results = {
            "valid": True,
            "issues": [],
            "config": None,
            "agents": {}
        }

        # Check configuration file
        config = self.load_project_config(project_dir)
        if not config:
            results["valid"] = False
            results["issues"].append("Missing or invalid .synapse.yml")
            return results

        results["config"] = config

        # Check agents directory
        agents_dir = project_dir / ".claude" / "agents"
        if not agents_dir.exists():
            results["valid"] = False
            results["issues"].append("Missing .claude/agents directory")
            return results

        # Validate each agent
        for agent_name in config.get("agent_versions", {}):
            agent_file = agents_dir / f"{agent_name}.md"
            agent_info = {
                "exists": agent_file.exists(),
                "symlinked": self.is_agent_symlinked(project_dir, agent_name),
                "checksum": self.get_agent_checksum(agent_file) if agent_file.exists() else None
            }

            if not agent_info["exists"]:
                results["valid"] = False
                results["issues"].append(f"Missing agent: {agent_name}")

            results["agents"][agent_name] = agent_info

        return results

    def get_project_context(self, project_dir: Path) -> str:
        """Load and concatenate all context files from .synapse/context/ directory"""
        context_dir = project_dir / ".synapse" / "context"

        if not context_dir.exists():
            return ""

        context_parts = []

        # Find all markdown files in context directory
        context_files = sorted(context_dir.glob("*.md"))

        if not context_files:
            return ""

        for context_file in context_files:
            try:
                content = context_file.read_text(encoding='utf-8')
                # Add file header for clarity
                context_parts.append(f"## Context from {context_file.name}\n\n{content}")
            except Exception as e:
                print(f"Warning: Failed to read context file {context_file}: {e}")
                continue

        if context_parts:
            header = "# Project-Specific Context\n\n"
            header += "The following context information is specific to this project and should be considered when performing any tasks:\n\n"
            return header + "\n\n---\n\n".join(context_parts)

        return ""