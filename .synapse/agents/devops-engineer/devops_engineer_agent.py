#!/usr/bin/env python3
"""
DevOps Engineer Agent: Infrastructure, Deployment, and Operations Specialist

Provides comprehensive DevOps capabilities including:
- Infrastructure as Code management
- CI/CD pipeline configuration
- Container and deployment orchestration
- Monitoring and observability setup
- Security scanning and compliance
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, TypedDict

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

# Claude Code SDK imports (with fallback)
try:
    from claude_agent_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeAgentOptions
    )
except ImportError:
    # Fallback for development/testing - use shared mock SDK
    print("⚠️  Claude Agent SDK not available, using shared mock SDK")
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
    from mock_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeAgentOptions
    )

from tools import (
    # Infrastructure tools
    manage_containers, configure_ci_cd, deploy_services,
    monitor_health, scan_infrastructure, provision_resources,

    # Deployment tools
    create_dockerfile, build_image, deploy_to_environment,
    manage_secrets, validate_deployment,

    # Monitoring tools
    setup_monitoring, check_service_health, analyze_logs,
    create_alerts, generate_reports,

    # Integration tools
    query_synapse_devops, search_deployment_patterns
)

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Tool argument schemas
class ContainerArgs(TypedDict):
    action: str
    container_name: str
    options: dict

class CICDArgs(TypedDict):
    platform: str
    config: dict

class DeploymentArgs(TypedDict):
    service_name: str
    image: str
    environment: str
    options: dict

class MonitoringArgs(TypedDict):
    services: list[str]
    config: dict

class SecurityArgs(TypedDict):
    target: str
    scan_type: str

class ReportArgs(TypedDict):
    report_type: str
    config: dict

# Agent tools with decorators

@tool(
    "docker_operations",
    "Manage Docker containers - build, run, stop, inspect",
    {
        "action": str,
        "container_name": str,
        "options": dict
    }
)
async def docker_operations(args: ContainerArgs) -> dict[str, Any]:
    """Manage Docker containers - build, run, stop, inspect."""
    return await manage_containers(
        args["action"],
        args.get("container_name", ""),
        args.get("options", {})
    )

@tool(
    "setup_ci_cd_pipeline",
    "Set up CI/CD pipeline for the project",
    {
        "project_path": str,
        "ci_platform": str,
        "deployment_targets": list
    }
)
async def setup_ci_cd_pipeline(args: CICDArgs) -> dict[str, Any]:
    """Generate and configure CI/CD pipelines for various platforms."""
    return await configure_ci_cd(
        args["platform"],
        args.get("config", {})
    )

@tool(
    "deploy_application",
    "Deploy services to specified environments with various strategies",
    {
        "service_name": str,
        "image": str,
        "environment": str,
        "options": dict
    }
)
async def deploy_application(args: DeploymentArgs) -> dict[str, Any]:
    """Deploy services to specified environments with various strategies."""
    return await deploy_services(
        args["environment"],
        [args["service_name"]],  # Convert single service to list
        args.get("options", {})
    )

@tool(
    "setup_service_monitoring",
    "Configure comprehensive monitoring for services",
    {
        "services": list,
        "config": dict
    }
)
async def setup_service_monitoring(args: MonitoringArgs) -> dict[str, Any]:
    """Configure comprehensive monitoring for services."""
    return await setup_monitoring(
        args["services"],
        args.get("config", {})
    )

@tool(
    "health_check_services",
    "Perform health checks on running services",
    {
        "services": list,
        "config": dict
    }
)
async def health_check_services(args: MonitoringArgs) -> dict[str, Any]:
    """Perform health checks on running services."""
    return await check_service_health(
        args["services"],
        args.get("config", {})
    )

@tool(
    "security_scan_infrastructure",
    "Scan infrastructure for security vulnerabilities",
    {
        "target": str,
        "scan_type": str
    }
)
async def security_scan_infrastructure(args: SecurityArgs) -> dict[str, Any]:
    """Scan infrastructure components for security vulnerabilities."""
    return await scan_infrastructure(
        args["target"],
        args.get("scan_type", "security")
    )

@tool(
    "generate_devops_report",
    "Generate comprehensive DevOps reports (performance, availability, etc.)",
    {
        "report_type": str,
        "config": dict
    }
)
async def generate_devops_report(args: ReportArgs) -> dict[str, Any]:
    """Generate comprehensive DevOps reports (performance, availability, etc.)."""
    return await generate_reports(
        args["report_type"],
        args.get("config", {})
    )

@tool(
    "create_container_image",
    "Create optimized Dockerfile and build container images",
    {
        "language": str,
        "options": dict,
        "build": bool,
        "dockerfile_path": str,
        "image_name": str
    }
)
async def create_container_image(args: dict) -> dict[str, Any]:
    """Create optimized Dockerfile and build container images."""
    if "language" in args:
        # Generate Dockerfile
        dockerfile_result = await create_dockerfile(
            args["language"],
            args.get("options", {})
        )

        if dockerfile_result.get("success") and args.get("build", False):
            # Also build the image if requested
            build_result = await build_image(
                "Dockerfile",
                args.get("image_name", "app:latest"),
                args.get("build_options", {})
            )

            return {
                **dockerfile_result,
                "build_result": build_result
            }

        return dockerfile_result

    elif "dockerfile_path" in args and "image_name" in args:
        # Build existing Dockerfile
        return await build_image(
            args["dockerfile_path"],
            args["image_name"],
            args.get("options", {})
        )

    return {
        "success": False,
        "error": "Must provide either 'language' for Dockerfile generation or 'dockerfile_path' and 'image_name' for building"
    }

@tool(
    "manage_application_secrets",
    "Manage application secrets and configuration",
    {
        "action": str,
        "secret_name": str,
        "options": dict
    }
)
async def manage_application_secrets(args: dict) -> dict[str, Any]:
    """Manage application secrets and configuration."""
    return await manage_secrets(
        args["action"],
        args["secret_name"],
        args.get("options", {})
    )

@tool(
    "validate_service_deployment",
    "Validate deployment with comprehensive testing",
    {
        "service_name": str,
        "environment": str,
        "checks": dict
    }
)
async def validate_service_deployment(args: dict) -> dict[str, Any]:
    """Validate deployment with comprehensive testing."""
    return await validate_deployment(
        args["service_name"],
        args["environment"],
        args.get("checks", {})
    )

@tool(
    "analyze_system_logs",
    "Analyze logs for patterns, errors, and performance insights",
    {
        "log_source": str,
        "config": dict
    }
)
async def analyze_system_logs(args: dict) -> dict[str, Any]:
    """Analyze logs for patterns, errors, and performance insights."""
    return await analyze_logs(
        args["log_source"],
        args.get("config", {})
    )

@tool(
    "setup_alerting_system",
    "Create monitoring alerts with notification channels",
    {
        "alert_rules": list,
        "config": dict
    }
)
async def setup_alerting_system(args: dict) -> dict[str, Any]:
    """Create monitoring alerts with notification channels."""
    return await create_alerts(
        args["alert_rules"],
        args.get("config", {})
    )

@tool(
    "provision_cloud_resources",
    "Provision cloud infrastructure using Infrastructure as Code",
    {
        "provider": str,
        "resources": list,
        "options": dict
    }
)
async def provision_cloud_resources(args: dict) -> dict[str, Any]:
    """Provision cloud infrastructure using Infrastructure as Code."""
    return await provision_resources(
        args["provider"],
        args["resources"],
        args.get("options", {})
    )

@tool(
    "search_devops_knowledge",
    "Search Synapse knowledge graph for DevOps best practices and patterns",
    {
        "query": str,
        "context_type": str
    }
)
async def search_devops_knowledge(args: dict) -> dict[str, Any]:
    """Search Synapse knowledge graph for DevOps best practices and patterns."""
    return await query_synapse_devops(
        args["query"],
        args.get("context_type", "devops")
    )

@tool(
    "find_deployment_patterns",
    "Find deployment patterns and implementation guides",
    {
        "deployment_type": str,
        "technology": str
    }
)
async def find_deployment_patterns(args: dict) -> dict[str, Any]:
    """Find deployment patterns and implementation guides."""
    return await search_deployment_patterns(
        args["deployment_type"],
        args.get("technology", "")
    )

async def create_mcp_server():
    """Create and configure the MCP server with all DevOps tools."""
    tools = [
        # Container and deployment tools
        docker_operations,
        create_container_image,
        deploy_application,
        validate_service_deployment,
        manage_application_secrets,

        # Infrastructure and CI/CD tools
        setup_ci_cd_pipeline,
        provision_cloud_resources,
        security_scan_infrastructure,

        # Monitoring and observability tools
        setup_service_monitoring,
        health_check_services,
        analyze_system_logs,
        setup_alerting_system,
        generate_devops_report,

        # Knowledge and pattern search
        search_devops_knowledge,
        find_deployment_patterns
    ]

    return create_sdk_mcp_server(
        name="devops_engineer_tools",
        version="1.0.0",
        tools=tools
    )

async def devops_agent_prompt() -> AsyncGenerator[ClaudeAgentOptions, None]:
    """Generate the DevOps agent system prompt."""
    prompt = """You are a DevOps Engineer Agent, specializing in infrastructure automation, deployment strategies, and operational excellence.

🛠️ **Core Capabilities:**

**Infrastructure Management:**
- Container orchestration with Docker and Kubernetes
- Infrastructure as Code (Terraform, CloudFormation, Ansible)
- Cloud resource provisioning (AWS, GCP, Azure)
- Security scanning and compliance automation

**Deployment & CI/CD:**
- Multi-strategy deployments (blue-green, canary, rolling)
- CI/CD pipeline configuration (GitHub Actions, GitLab CI, Jenkins)
- Automated testing and quality gates
- Environment management and configuration

**Monitoring & Observability:**
- Comprehensive monitoring stack setup (Prometheus, Grafana, ELK)
- Health check automation and SLA monitoring
- Log analysis and anomaly detection
- Alerting systems with intelligent escalation

**Security & Compliance:**
- Container and infrastructure security scanning
- Secrets management and rotation
- Compliance automation and reporting
- Vulnerability assessment and remediation

**Operations & Optimization:**
- Performance monitoring and optimization
- Cost analysis and resource optimization
- Capacity planning and auto-scaling
- Incident response and troubleshooting

According to the updated strategy, as a DevOps Engineer I use the **Claude-4.1-Opus** model for maximum capability in complex infrastructure automation and deployment orchestration.

I integrate with the Synapse knowledge graph to:
- Share deployment patterns and best practices
- Learn from organizational infrastructure experiences
- Provide context-aware recommendations
- Maintain operational knowledge base

**Communication Style:**
- Practical, implementation-focused guidance
- Clear security and reliability considerations
- Step-by-step operational procedures
- Cost and performance impact awareness

Ready to help with infrastructure, deployments, monitoring, or any DevOps challenges. What would you like to work on?"""

    yield {"message": {"role": "system", "content": prompt}}

async def main():
    """Main agent execution loop."""
    console.print(Panel.fit(
        Text("🚀 DevOps Engineer Agent", style="bold blue") +
        Text("\nInfrastructure • Deployment • Monitoring • Security", style="dim"),
        title="Agent Active",
        border_style="blue"
    ))

    # Create MCP server
    server = await create_mcp_server()

    console.print(f"[green]✓[/green] Loaded {len(server.tools)} DevOps tools")
    console.print("[blue]Ready to assist with infrastructure and deployment tasks[/blue]\n")

    try:
        # Example usage - in real implementation, this would be the agent event loop
        async for response in query(devops_agent_prompt()):
            if response.get("type") == "result":
                result_content = response.get("result", {}).get("content", [])
                for content_item in result_content:
                    if content_item.get("type") == "text":
                        console.print(Panel(
                            content_item["text"],
                            title="DevOps Agent Response",
                            border_style="green"
                        ))

    except KeyboardInterrupt:
        console.print("\n[yellow]DevOps Agent shutting down...[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 DevOps Engineer Agent stopped[/yellow]")