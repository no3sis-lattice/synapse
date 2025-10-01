#!/usr/bin/env python3
"""
Synapse System - Unified CLI
============================

Single entry point for all synapse functionality with intelligent context detection.
"""

import os
import sys
import argparse
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any

# Add current directory to path for local imports
sys.path.insert(0, os.path.dirname(__file__))

from project import ProjectManager
from updater import UpdateManager
from version_manager import VersionManager
from orchestration import TaskOrchestrator
from task_state import TaskTracker, TaskState


class SynapseCLI:
    """Unified command-line interface for Synapse System"""

    def __init__(self):
        self.synapse_home = Path(__file__).parent.parent.resolve()
        self.neo4j_dir = self.synapse_home / ".synapse" / "neo4j"
        self.project_manager = ProjectManager(self.synapse_home)
        self.update_manager = UpdateManager(self.synapse_home)
        self.version_manager = VersionManager(self.synapse_home)
        self.orchestrator = TaskOrchestrator(self.synapse_home)
        self.task_tracker = TaskTracker(self.synapse_home)
        self._orchestrator_initialized = False

        # Auto-detect current project context
        self.current_project = self._find_project_root()

    async def _ensure_orchestrator_initialized(self):
        """
        Ensure orchestrator is async-initialized for reactive routing.

        This enables the reactive Corpus Callosum if configured.
        Safe to call multiple times (idempotent).

        Handles errors gracefully:
        - TimeoutError: Falls back to sync mode
        - ImportError: Continues without reactive components
        - ConnectionError: Logs warning, continues with degraded functionality
        """
        if not self._orchestrator_initialized:
            try:
                await self.orchestrator.async_init()
                self._orchestrator_initialized = True
            except asyncio.TimeoutError:
                print("⚠️  Orchestrator initialization timed out, using sync mode")
                self._orchestrator_initialized = True  # Don't retry
            except ImportError as e:
                print(f"⚠️  Reactive components not available: {e}")
                self._orchestrator_initialized = True  # Don't retry
            except Exception as e:
                print(f"⚠️  Failed to initialize async components: {e}")
                print("Continuing with synchronous execution mode")
                self._orchestrator_initialized = True  # Don't retry

    def _find_project_root(self) -> Optional[Path]:
        """Find synapse project by walking up directories"""
        current = Path.cwd()
        while current.parent != current:
            if (current / ".synapse.yml").exists():
                return current
            current = current.parent
        return None

    def _run_neo4j_script(self, script_name: str, args: List[str] = None) -> int:
        """Run a script in the Neo4j environment"""
        if args is None:
            args = []

        venv_python = self.neo4j_dir / ".venv" / "bin" / "python"
        script_path = self.neo4j_dir / script_name

        if not script_path.exists():
            print(f"Error: Script {script_name} not found", file=sys.stderr)
            return 1

        try:
            result = subprocess.run(
                [str(venv_python), str(script_path)] + args,
                cwd=self.neo4j_dir
            )
            return result.returncode
        except Exception as e:
            print(f"Error running {script_name}: {e}", file=sys.stderr)
            return 1

    def _check_services(self) -> bool:
        """Quick check if synapse services are running"""
        try:
            import requests
            response = requests.get("http://localhost:7474", timeout=2)
            return response.status_code == 200
        except:
            return False

    def cmd_start(self, args) -> int:
        """Start synapse services"""
        print("🚀 Starting synapse services...")

        # Check if Docker is available
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker is not installed. Get it from: https://docs.docker.com/get-docker/")
            return 1

        # Check if Docker daemon is running
        try:
            subprocess.run(["docker", "info"], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            print("❌ Docker daemon is not running")
            print("💊 Fix: sudo systemctl start docker (Linux) or start Docker Desktop (macOS/Windows)")
            return 1

        # Check for port conflicts
        import socket
        ports_to_check = [7474, 7687, 6379]
        for port in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                print(f"⚠️  Port {port} is already in use")

        # Try docker-compose first, fallback to docker compose
        compose_cmd = ["docker-compose"]
        try:
            subprocess.run(["docker-compose", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(["docker", "compose", "version"], capture_output=True, check=True)
                compose_cmd = ["docker", "compose"]
            except subprocess.CalledProcessError:
                print("❌ Neither docker-compose nor 'docker compose' is available")
                print("💊 Fix: Install Docker Compose")
                return 1

        # Start services
        try:
            result = subprocess.run(
                compose_cmd + ["up", "-d"],
                cwd=self.neo4j_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("✅ Docker services started")

                # Wait for services to be ready
                print("⏳ Waiting for services to initialize...")
                import time
                time.sleep(3)

                # Check if services are responding
                if self._check_services():
                    print("✅ Synapse services ready!")
                    print("🔗 Neo4j: http://localhost:7474")
                    print("🔗 Redis: localhost:6379")
                else:
                    print("⚠️  Services started but may still be initializing")
                    print("💊 Check status with: synapse status")

                return 0
            else:
                print(f"❌ Failed to start services:")
                print(result.stderr)
                print("💊 Try: synapse doctor --fix")
                return 1

        except Exception as e:
            print(f"❌ Error starting services: {e}")
            return 1

    def cmd_stop(self, args) -> int:
        """Stop synapse services"""
        print("🛑 Stopping synapse services...")

        try:
            result = subprocess.run(
                ["docker-compose", "down"],
                cwd=self.neo4j_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("✅ Synapse services stopped")
                return 0
            else:
                print(f"❌ Failed to stop services: {result.stderr}")
                return 1

        except Exception as e:
            print(f"❌ Error stopping services: {e}")
            return 1

    def cmd_status(self, args) -> int:
        """Check synapse system status"""
        print("📊 Synapse System Status")
        print("=" * 30)

        # Check services
        print("\n🔧 Services:")
        if self._check_services():
            print("✅ Neo4j running on http://localhost:7474")
        else:
            print("❌ Neo4j not responding")

        # Check Redis
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, socket_timeout=2)
            r.ping()
            print("✅ Redis running on localhost:6379")
        except:
            print("❌ Redis not responding")

        # Project context
        print(f"\n📁 Current Directory: {Path.cwd()}")
        if self.current_project:
            print(f"✅ Synapse project detected: {self.current_project}")
            config = self.project_manager.load_project_config(self.current_project)
            if config:
                print(f"   Language: {config.get('language', 'unknown')}")
                print(f"   Version: {config.get('synapse_version', 'unknown')}")
        else:
            print("ℹ️  No synapse project in current directory")

        return 0

    def cmd_doctor(self, args) -> int:
        """Run comprehensive system health checks"""
        auto_fix = hasattr(args, 'fix') and args.fix

        print("🩺 Synapse Doctor - System Health Check")
        if auto_fix:
            print("🔧 Auto-fix mode enabled")
        print("=" * 50)

        all_healthy = True
        fixes_applied = []

        # Check 1: Neo4j connectivity
        print("\n1. Neo4j Database:")
        if self._check_services():
            print("   ✅ Neo4j is running on http://localhost:7474")
        else:
            print("   ❌ Neo4j is not responding")
            if auto_fix:
                print("   🔧 Attempting to start services...")
                if self.cmd_start(None) == 0:
                    print("   ✅ Services started successfully")
                    fixes_applied.append("Started Neo4j services")
                else:
                    print("   ❌ Failed to start services automatically")
                    all_healthy = False
            else:
                print("   💊 Fix: Run 'synapse start' or 'synapse doctor --fix'")
                all_healthy = False

        # Check 2: Redis connectivity
        print("\n2. Redis Cache:")
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, socket_timeout=2)
            r.ping()
            print("   ✅ Redis is running on localhost:6379")
        except ImportError:
            print("   ⚠️  Redis module not available in system Python")
            print("   💊 Info: Redis checks require services to be running")
        except Exception as e:
            print("   ❌ Redis is not responding")
            if not auto_fix:
                print("   💊 Fix: Run 'synapse start' or 'synapse doctor --fix'")
                all_healthy = False

        # Check 3: Docker environment
        print("\n3. Docker Environment:")
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            print("   ✅ Docker is installed")

            # Check if Docker daemon is running
            try:
                subprocess.run(["docker", "info"], capture_output=True, check=True)
                print("   ✅ Docker daemon is running")
            except subprocess.CalledProcessError:
                print("   ❌ Docker daemon is not running")
                if auto_fix:
                    print("   🔧 Attempting to start Docker...")
                    try:
                        subprocess.run(["sudo", "systemctl", "start", "docker"],
                                     capture_output=True, check=True)
                        print("   ✅ Docker daemon started")
                        fixes_applied.append("Started Docker daemon")
                    except:
                        print("   ❌ Failed to start Docker automatically")
                        print("   💊 Manual fix: sudo systemctl start docker")
                        all_healthy = False
                else:
                    print("   💊 Fix: sudo systemctl start docker")
                    all_healthy = False

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ❌ Docker is not installed")
            print("   💊 Fix: Install from https://docs.docker.com/get-docker/")
            all_healthy = False

        # Check 4: Project configuration
        print("\n4. Project Configuration:")
        if self.current_project:
            synapse_yml = self.current_project / ".synapse.yml"
            if synapse_yml.exists():
                print(f"   ✅ Synapse project found at {self.current_project}")
                config = self.project_manager.load_project_config(self.current_project)
                if config:
                    print(f"      Language: {config.get('language', 'unknown')}")
                    print(f"      Version: {config.get('synapse_version', 'unknown')}")
            else:
                print("   ⚠️  Project directory exists but .synapse.yml missing")
                if auto_fix:
                    print("   🔧 Initializing synapse project...")
                    if self.cmd_init(type('Args', (), {'directory': str(self.current_project)})()) == 0:
                        print("   ✅ Project initialized")
                        fixes_applied.append("Initialized synapse project")
                    else:
                        print("   ❌ Failed to initialize project")
                        all_healthy = False
                else:
                    print("   💊 Fix: Run 'synapse init .' or 'synapse doctor --fix'")
                    all_healthy = False
        else:
            print("   ℹ️  No synapse project in current directory")
            print("   💊 Info: Run 'synapse init .' to create a new project")

        # Check 5: Virtual environment
        print("\n5. Neo4j Virtual Environment:")
        venv_python = self.neo4j_dir / ".venv" / "bin" / "python"
        if venv_python.exists():
            print("   ✅ Python virtual environment is configured")
        else:
            print("   ❌ Python virtual environment not found")
            print("   💊 Fix: Re-run install.sh or check installation")
            all_healthy = False

        # Summary
        print("\n" + "=" * 50)
        if fixes_applied:
            print("🔧 Fixes applied:")
            for fix in fixes_applied:
                print(f"   • {fix}")
            print()

        if all_healthy:
            print("✅ All systems healthy!")
            return 0
        else:
            print("⚠️  Some issues detected.")
            if not auto_fix:
                print("💡 Try: synapse doctor --fix")
            return 1

    def cmd_search(self, args) -> int:
        """Search global knowledge base"""
        if not args.query:
            print("❌ Search query required")
            print("Usage: synapse search \"your query\"")
            return 1

        if not self._check_services():
            print("⚠️  Services not running, starting them...")
            if self.cmd_start(None) != 0:
                return 1
            import time
            time.sleep(2)

        print(f"🔍 Searching for: {args.query}")
        return self._run_neo4j_script("synapse_search.py", [args.query])

    def cmd_init(self, args) -> int:
        """Initialize project with synapse"""
        target_dir = Path(args.directory) if args.directory else Path.cwd()

        if not target_dir.exists():
            print(f"❌ Directory does not exist: {target_dir}")
            return 1

        if not target_dir.is_dir():
            print(f"❌ Not a directory: {target_dir}")
            return 1

        print(f"🎯 Initializing synapse for: {target_dir.name}")

        try:
            self.project_manager.initialize_project(
                target_dir,
                link_agents=args.link if hasattr(args, 'link') else False
            )
            print("✅ Project initialized successfully!")
            return 0
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return 1

    def cmd_update(self, args) -> int:
        """Update project agents and configuration"""
        target_dir = Path(args.directory) if args.directory else self.current_project

        if not target_dir:
            print("❌ No synapse project found in current directory")
            print("Use: synapse update /path/to/project")
            return 1

        if not (target_dir / ".synapse.yml").exists():
            print(f"❌ Not a synapse project: {target_dir}")
            return 1

        print(f"🔄 Updating synapse project: {target_dir.name}")

        try:
            updates = self.update_manager.check_updates(target_dir)
            if not updates:
                print("✅ Project is up to date")
                return 0

            print(f"📦 Found {len(updates)} updates:")
            for update in updates:
                print(f"   • {update['name']}: {update['old_version']} → {update['new_version']}")

            if not args.yes:
                response = input("\nApply updates? [y/N]: ")
                if response.lower() not in ['y', 'yes']:
                    print("Update cancelled")
                    return 0

            self.update_manager.apply_updates(target_dir, updates)
            print("✅ Project updated successfully!")
            return 0

        except Exception as e:
            print(f"❌ Update failed: {e}")
            return 1

    def cmd_ingest(self, args) -> int:
        """Ingest knowledge into synapse"""
        if self.current_project:
            print(f"📚 Ingesting project: {self.current_project.name}")
        else:
            print("📚 Ingesting global knowledge")

        script_args = []
        if args.force:
            script_args.append("--force")

        return self._run_neo4j_script("ingestion.py", script_args)

    def cmd_health(self, args) -> int:
        """Check system health"""
        if self.current_project:
            print(f"🩺 Health check for project: {self.current_project.name}")
        else:
            print("🩺 Global system health check")

        return self._run_neo4j_script("synapse_health.py")

    def cmd_standards(self, args) -> int:
        """Get coding standards"""
        if not args.name:
            print("❌ Standard name required")
            print("Usage: synapse standards <name> [language]")
            return 1

        script_args = [args.name]
        if args.language:
            script_args.append(args.language)
        elif self.current_project:
            # Auto-detect language from project
            config = self.project_manager.load_project_config(self.current_project)
            if config and config.get('language'):
                script_args.append(config['language'])

        return self._run_neo4j_script("synapse_standard.py", script_args)

    def cmd_template(self, args) -> int:
        """Get project templates"""
        if not args.name:
            print("❌ Template name required")
            print("Usage: synapse template <name>")
            return 1

        return self._run_neo4j_script("synapse_template.py", [args.name])

    def cmd_tool(self, args) -> int:
        """Direct tool access (for debugging)"""
        tool_map = {
            'search': ('synapse_search.py', ['query']),
            'standard': ('synapse_standard.py', ['name', 'language']),
            'template': ('synapse_template.py', ['name']),
            'health': ('synapse_health.py', []),
        }

        if args.tool_name not in tool_map:
            print(f"❌ Unknown tool: {args.tool_name}")
            print(f"Available tools: {', '.join(tool_map.keys())}")
            return 1

        script_name, param_names = tool_map[args.tool_name]
        script_args = args.tool_args if args.tool_args else []

        return self._run_neo4j_script(script_name, script_args)

    def cmd_version(self, args) -> int:
        """Show version information"""
        version_file = self.synapse_home / ".synapse" / "VERSION"
        if version_file.exists():
            version = version_file.read_text().strip()
        else:
            version = "unknown"

        print(f"Synapse System v{version}")
        print(f"Location: {self.synapse_home}")

        if self.current_project:
            config = self.project_manager.load_project_config(self.current_project)
            if config:
                proj_version = config.get('synapse_version', 'unknown')
                print(f"Project version: {proj_version}")
                if proj_version != version:
                    print("⚠️  Project version differs from system version")
                    print("   Consider running: synapse update")

        return 0

    def cmd_manifest(self, args) -> int:
        """Manage agent manifest and versions"""
        if args.manifest_action == "update":
            try:
                self.version_manager.update_manifest()
                return 0
            except Exception as e:
                print(f"❌ Failed to update manifest: {e}")
                return 1

        elif args.manifest_action == "verify":
            if args.agent:
                success = self.version_manager.verify_agent_integrity(args.agent)
                return 0 if success else 1
            else:
                success = self.version_manager.verify_all_agents()
                return 0 if success else 1

        elif args.manifest_action == "list":
            self.version_manager.list_agents_summary()
            return 0

        elif args.manifest_action == "info":
            if not args.agent:
                print("❌ Agent name required for info command")
                return 1
            info = self.version_manager.get_agent_info(args.agent)
            if "error" in info:
                print(f"❌ {info['error']}")
                return 1

            import json
            print(json.dumps(info, indent=2))
            return 0

        else:
            print(f"❌ Unknown manifest action: {args.manifest_action}")
            return 1

    async def cmd_workflow_async(self, args) -> int:
        """Manage and execute workflows (async-aware for reactive routing)"""
        # Ensure orchestrator is initialized for reactive routing
        await self._ensure_orchestrator_initialized()

        if args.workflow_action == "list":
            workflows = self.orchestrator.list_available_workflows()
            if not workflows:
                print("No workflows available")
                return 0

            print("📋 Available Workflows:")
            print("=" * 50)
            for workflow in workflows:
                print(f"• {workflow['id']:<20} {workflow['name']}")
                print(f"  {workflow['description']}")
                print(f"  Type: {workflow['type']:<15} Duration: ~{workflow['estimated_duration']//60}min")
                print()
            return 0

        elif args.workflow_action == "execute":
            if not args.request:
                print("❌ Request description required for workflow execution")
                print("Usage: synapse workflow execute \"implement user authentication\"")
                return 1

            # Detect language from current project
            language = None
            if self.current_project:
                config = self.project_manager.load_project_config(self.current_project)
                if config:
                    language = config.get('language')

            if not language and args.language:
                language = args.language

            print(f"🎯 Executing workflow for: {args.request}")
            if language:
                print(f"🔧 Language context: {language}")

            try:
                # Decompose request into workflow
                workflow = self.orchestrator.decompose_request(args.request, language)
                print(f"📋 Created workflow: {workflow.name}")
                print(f"📊 Estimated duration: {workflow.estimated_total_duration // 60} minutes")
                print(f"🔄 Phases: {len(workflow.phases)}")

                if not args.yes:
                    response = input("\nExecute this workflow? [y/N]: ")
                    if response.lower() not in ['y', 'yes']:
                        print("Workflow cancelled")
                        return 0

                # Execute workflow (placeholder - would be async in real implementation)
                print("\n🚀 Executing workflow...")
                print("⚠️  Note: This is a preview - actual agent execution not yet implemented")

                # Show workflow structure
                for i, phase in enumerate(workflow.phases, 1):
                    print(f"\nPhase {i}: {phase.name}")
                    for task in phase.tasks:
                        print(f"  • {task.agent}: {task.description}")

                print("\n✅ Workflow structure created successfully!")
                print("🔜 Agent execution will be implemented in the next phase")
                return 0

            except Exception as e:
                print(f"❌ Workflow execution failed: {e}")
                return 1

        elif args.workflow_action == "status":
            # Show active workflows and their status
            print("📊 Workflow Status:")
            print("=" * 30)
            print("🔜 Workflow status tracking will be implemented in next phase")
            return 0

        elif args.workflow_action == "create":
            if not args.workflow_file:
                print("❌ Workflow file required")
                print("Usage: synapse workflow create my-workflow.yml")
                return 1

            print(f"🛠️  Creating custom workflow from: {args.workflow_file}")
            print("🔜 Custom workflow creation will be implemented in next phase")
            return 0

        else:
            print(f"❌ Unknown workflow action: {args.workflow_action}")
            return 1

    def cmd_workflow(self, args) -> int:
        """
        Synchronous wrapper for cmd_workflow_async with error handling.

        Handles:
        - Keyboard interrupts (Ctrl+C) gracefully
        - Async execution errors with proper cleanup
        - Standard Unix exit codes
        """
        try:
            return asyncio.run(self.cmd_workflow_async(args))
        except KeyboardInterrupt:
            print("\n⚠️  Workflow command cancelled by user")
            return 130  # Standard Unix exit code for SIGINT
        except Exception as e:
            print(f"❌ Workflow command failed: {e}")
            return 1

    def cmd_tasks(self, args) -> int:
        """Manage tasks and task state"""
        if args.task_action == "list":
            state_filter = None
            if args.state:
                try:
                    state_filter = TaskState(args.state.upper())
                except ValueError:
                    print(f"❌ Invalid state: {args.state}")
                    print(f"Valid states: {', '.join([s.value for s in TaskState])}")
                    return 1

            if state_filter:
                tasks = self.task_tracker.get_tasks_by_state(state_filter)
                print(f"📋 Tasks in {state_filter.value} state:")
            else:
                # Get ready tasks by default
                tasks = self.task_tracker.get_ready_tasks()
                print("📋 Ready to execute tasks:")

            if not tasks:
                print("No tasks found")
                return 0

            print("=" * 60)
            for task in tasks:
                print(f"• {task.id[:8]} | {task.agent:<20} | {task.action}")
                print(f"  {task.description}")
                print(f"  State: {task.state.value} | Priority: {task.priority.value}")
                print()

            return 0

        elif args.task_action == "show":
            if not args.task_id:
                print("❌ Task ID required")
                return 1

            task = self.task_tracker.get_task(args.task_id)
            if not task:
                print(f"❌ Task not found: {args.task_id}")
                return 1

            print(f"📄 Task Details: {task.id}")
            print("=" * 40)
            print(f"Agent: {task.agent}")
            print(f"Action: {task.action}")
            print(f"Description: {task.description}")
            print(f"State: {task.state.value}")
            print(f"Priority: {task.priority.value}")
            print(f"Created: {task.created_at}")
            print(f"Updated: {task.updated_at}")

            if task.dependencies:
                print(f"Dependencies: {', '.join(task.dependencies)}")

            if task.error:
                print(f"Error: {task.error}")

            return 0

        elif args.task_action == "history":
            if not args.task_id:
                print("❌ Task ID required")
                return 1

            history = self.task_tracker.get_task_history(args.task_id)
            if not history:
                print(f"❌ No history found for task: {args.task_id}")
                return 1

            print(f"📜 Task History: {args.task_id}")
            print("=" * 50)
            for entry in history:
                prev = entry.previous_state.value if entry.previous_state else "None"
                print(f"{entry.timestamp} | {prev} → {entry.new_state.value} | {entry.agent}")
                if entry.notes:
                    print(f"  Notes: {entry.notes}")

            return 0

        else:
            print(f"❌ Unknown task action: {args.task_action}")
            return 1


def main():
    """Main CLI entry point"""
    cli = SynapseCLI()

    parser = argparse.ArgumentParser(
        description="Synapse System - Global Knowledge and Agent Management",
        prog="synapse"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Service management
    subparsers.add_parser("start", help="Start synapse services")
    subparsers.add_parser("stop", help="Stop synapse services")
    subparsers.add_parser("status", help="Check system status")

    doctor_parser = subparsers.add_parser("doctor", help="Run comprehensive system health checks")
    doctor_parser.add_argument("--fix", action="store_true", help="Automatically fix common issues")

    # Core functionality
    search_parser = subparsers.add_parser("search", help="Search global knowledge")
    search_parser.add_argument("query", help="Search query")

    init_parser = subparsers.add_parser("init", help="Initialize project")
    init_parser.add_argument("directory", nargs="?", help="Project directory")
    init_parser.add_argument("--link", action="store_true",
                           help="Use symlinks instead of copies")

    update_parser = subparsers.add_parser("update", help="Update project")
    update_parser.add_argument("directory", nargs="?", help="Project directory")
    update_parser.add_argument("-y", "--yes", action="store_true",
                             help="Apply updates without confirmation")

    # Knowledge management
    ingest_parser = subparsers.add_parser("ingest", help="Ingest knowledge")
    ingest_parser.add_argument("--force", action="store_true",
                             help="Force full re-ingestion")

    subparsers.add_parser("health", help="System health check")

    # Content access
    standards_parser = subparsers.add_parser("standards", help="Get coding standards")
    standards_parser.add_argument("name", help="Standard name")
    standards_parser.add_argument("language", nargs="?", help="Programming language")

    template_parser = subparsers.add_parser("template", help="Get templates")
    template_parser.add_argument("name", help="Template name")

    # Tool access
    tool_parser = subparsers.add_parser("tool", help="Direct tool access")
    tool_parser.add_argument("tool_name", choices=["search", "standard", "template", "health"])
    tool_parser.add_argument("tool_args", nargs="*", help="Tool arguments")

    # Utility
    subparsers.add_parser("version", help="Show version information")

    # Manifest management
    manifest_parser = subparsers.add_parser("manifest", help="Manage agent manifest")
    manifest_parser.add_argument("manifest_action", choices=["update", "verify", "list", "info"])
    manifest_parser.add_argument("agent", nargs="?", help="Agent name (for verify/info)")

    # Workflow management
    workflow_parser = subparsers.add_parser("workflow", help="Manage and execute workflows")
    workflow_parser.add_argument("workflow_action", choices=["list", "execute", "status", "create"])
    workflow_parser.add_argument("request", nargs="?", help="Request description (for execute)")
    workflow_parser.add_argument("--language", help="Programming language context")
    workflow_parser.add_argument("--workflow-file", help="Workflow file (for create)")
    workflow_parser.add_argument("-y", "--yes", action="store_true", help="Auto-confirm execution")

    # Task management
    task_parser = subparsers.add_parser("tasks", help="Manage tasks and task state")
    task_parser.add_argument("task_action", choices=["list", "show", "history"])
    task_parser.add_argument("--state", help="Filter tasks by state")
    task_parser.add_argument("--task-id", help="Task ID (for show/history)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate command handler
    cmd_method = getattr(cli, f"cmd_{args.command.replace('-', '_')}", None)
    if cmd_method:
        return cmd_method(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())