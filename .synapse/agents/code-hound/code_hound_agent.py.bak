#!/usr/bin/env python3
"""
Code Hound Agent

Uncompromising code quality enforcer with zero tolerance for shortcuts, technical debt, or substandard practices.
Enforces TDD, KISS, SOLID principles, and DRY standards with Synapse System integration.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, TypedDict, Dict, List, Optional

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

# Claude Code SDK imports (placeholders for now)
try:
    from claude_code_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeCodeSdkMessage
    )
except ImportError:
    # Fallback for development/testing
    print("⚠️  Claude Code SDK not available, using mock implementations")
    from tools.mock_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeCodeSdkMessage
    )

from tools import (
    deep_code_analysis,
    enforce_tdd_standards,
    check_solid_principles,
    detect_dry_violations,
    scan_shortcuts,
    calculate_quality_scores,
    generate_review_report,
    load_config,
    get_synapse_patterns
)

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Tool argument schemas
class CodeReviewArgs(TypedDict):
    file_path: str
    language: Optional[str]
    review_type: Optional[str]  # "full", "tdd", "solid", "dry", "shortcuts"

class QualityAnalysisArgs(TypedDict):
    directory: str
    include_patterns: Optional[List[str]]
    exclude_patterns: Optional[List[str]]

@tool
async def comprehensive_code_review(args: CodeReviewArgs) -> Dict[str, Any]:
    """
    Perform a comprehensive code review enforcing TDD, KISS, SOLID, and DRY principles.

    Args:
        file_path: Path to the code file to review
        language: Programming language (optional, auto-detected if not provided)
        review_type: Type of review to perform (optional, defaults to "full")

    Returns:
        Comprehensive review report with violations, scores, and recommendations
    """
    file_path = args["file_path"]
    language = args.get("language")
    review_type = args.get("review_type", "full")

    console.print(f"🔍 [bold purple]Code Hound analyzing:[/bold purple] {file_path}")

    # Perform deep analysis
    analysis = await deep_code_analysis(file_path, language)

    # Run specific checks based on review type
    results = {
        "file_path": file_path,
        "language": analysis["language"],
        "timestamp": analysis["timestamp"]
    }

    if review_type in ["full", "tdd"]:
        results["tdd_analysis"] = await enforce_tdd_standards(file_path, analysis)

    if review_type in ["full", "solid"]:
        results["solid_analysis"] = await check_solid_principles(file_path, analysis)

    if review_type in ["full", "dry"]:
        results["dry_analysis"] = await detect_dry_violations(file_path, analysis)

    if review_type in ["full", "shortcuts"]:
        results["shortcuts_analysis"] = await scan_shortcuts(file_path, analysis)

    # Calculate quality scores
    results["quality_scores"] = await calculate_quality_scores(results)

    # Generate formatted report
    results["formatted_report"] = await generate_review_report(results)

    return results

@tool
async def project_quality_audit(args: QualityAnalysisArgs) -> Dict[str, Any]:
    """
    Perform a comprehensive quality audit across an entire project directory.

    Args:
        directory: Project directory to audit
        include_patterns: File patterns to include (optional)
        exclude_patterns: File patterns to exclude (optional)

    Returns:
        Project-wide quality assessment with aggregate scores and hotspots
    """
    directory = args["directory"]
    include_patterns = args.get("include_patterns", ["**/*.py", "**/*.js", "**/*.ts", "**/*.rs", "**/*.go"])
    exclude_patterns = args.get("exclude_patterns", ["**/node_modules/**", "**/target/**", "**/__pycache__/**"])

    console.print(f"📊 [bold purple]Code Hound auditing project:[/bold purple] {directory}")

    from pathlib import Path
    import glob

    project_path = Path(directory)
    files_to_review = []

    # Collect files based on patterns
    for pattern in include_patterns:
        for file_path in project_path.glob(pattern):
            if file_path.is_file():
                # Check if file should be excluded
                should_exclude = False
                for exclude_pattern in exclude_patterns:
                    if file_path.match(exclude_pattern) or any(
                        part for part in file_path.parts
                        if any(excl.strip("*") in part for excl in exclude_pattern.split("/"))
                    ):
                        should_exclude = True
                        break

                if not should_exclude:
                    files_to_review.append(str(file_path))

    # Perform analysis on each file
    audit_results = {
        "project_directory": directory,
        "files_analyzed": len(files_to_review),
        "file_results": [],
        "aggregate_scores": {},
        "critical_violations": [],
        "quality_hotspots": []
    }

    for file_path in files_to_review:
        try:
            file_result = await comprehensive_code_review({
                "file_path": file_path,
                "review_type": "full"
            })
            audit_results["file_results"].append(file_result)
        except Exception as e:
            console.print(f"⚠️ Error analyzing {file_path}: {e}")

    # Calculate aggregate metrics
    if audit_results["file_results"]:
        scores = [result["quality_scores"] for result in audit_results["file_results"]]
        audit_results["aggregate_scores"] = {
            "overall": sum(s.get("overall", 0) for s in scores) / len(scores),
            "tdd": sum(s.get("tdd", 0) for s in scores) / len(scores),
            "kiss": sum(s.get("kiss", 0) for s in scores) / len(scores),
            "solid": sum(s.get("solid", 0) for s in scores) / len(scores),
            "dry": sum(s.get("dry", 0) for s in scores) / len(scores),
            "no_shortcuts": sum(s.get("no_shortcuts", 0) for s in scores) / len(scores)
        }

    return audit_results

@tool
async def enforce_standards(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enforce coding standards and best practices based on Synapse knowledge base.

    Args:
        file_path: Path to file to check
        standards_type: Type of standards to enforce ("tdd", "solid", "dry", "kiss", "all")

    Returns:
        Standards enforcement report with specific violations and fixes
    """
    file_path = args["file_path"]
    standards_type = args.get("standards_type", "all")

    console.print(f"⚖️ [bold purple]Code Hound enforcing standards:[/bold purple] {standards_type}")

    # Get relevant patterns from Synapse
    patterns = await get_synapse_patterns(standards_type)

    # Perform analysis
    analysis = await deep_code_analysis(file_path)

    enforcement_results = {
        "file_path": file_path,
        "standards_type": standards_type,
        "violations": [],
        "recommendations": [],
        "synapse_patterns_applied": len(patterns)
    }

    # Apply standards based on type
    if standards_type in ["all", "tdd"]:
        tdd_violations = await enforce_tdd_standards(file_path, analysis)
        enforcement_results["violations"].extend(tdd_violations.get("violations", []))

    if standards_type in ["all", "solid"]:
        solid_violations = await check_solid_principles(file_path, analysis)
        enforcement_results["violations"].extend(solid_violations.get("violations", []))

    if standards_type in ["all", "dry"]:
        dry_violations = await detect_dry_violations(file_path, analysis)
        enforcement_results["violations"].extend(dry_violations.get("violations", []))

    if standards_type in ["all", "kiss"]:
        # KISS principle checks are integrated into deep analysis
        kiss_issues = analysis.get("complexity_issues", [])
        enforcement_results["violations"].extend(kiss_issues)

    return enforcement_results

async def handle_message(message: ClaudeCodeSdkMessage) -> str:
    """Process incoming messages and route to appropriate tools."""

    content = message.get("content", "").lower()

    # Display Code Hound banner
    banner = Text("🐕 CODE HOUND", style="bold purple")
    banner.append(" - Uncompromising Quality Enforcer", style="purple")
    console.print(Panel(banner, border_style="purple"))

    if "review" in content or "analyze" in content:
        # Extract file path from message (simplified for demo)
        file_path = message.get("file_path", "./")

        result = await comprehensive_code_review({
            "file_path": file_path,
            "review_type": "full"
        })

        return result["formatted_report"]

    elif "audit" in content or "project" in content:
        directory = message.get("directory", "./")

        result = await project_quality_audit({
            "directory": directory
        })

        return f"Project audit complete. Analyzed {result['files_analyzed']} files. " + \
               f"Overall quality score: {result['aggregate_scores'].get('overall', 0):.1f}/100"

    else:
        return (
            "🐕 **Code Hound Ready**\n\n"
            "I'm here to enforce uncompromising code quality standards:\n"
            "- **TDD Verification**: Demand test-first evidence\n"
            "- **KISS Enforcement**: Ruthlessly identify unnecessary complexity\n"
            "- **SOLID Audit**: Verify all five principles\n"
            "- **DRY Compliance**: Detect any repeated code or knowledge\n"
            "- **Shortcut Detection**: Hunt down technical debt\n\n"
            "Available commands:\n"
            "- `review [file_path]` - Comprehensive code review\n"
            "- `audit [directory]` - Project-wide quality audit\n"
            "- `enforce [standards_type]` - Apply specific standards\n\n"
            "*This shortcut stops here. Fix it properly or don't ship it.*"
        )

async def main():
    """Main agent loop."""
    config = load_config()

    console.print("[bold purple]Code Hound Agent Starting...[/bold purple]")

    # Create MCP server with tools
    server = create_sdk_mcp_server(
        name="code_hound_tools",
        tools=[comprehensive_code_review, project_quality_audit, enforce_standards]
    )

    # Start the server
    await server.run()

    # Agent message loop
    async for message in query("You are Code Hound, ready to enforce quality standards."):
        response = await handle_message(message)
        print(response)

if __name__ == "__main__":
    asyncio.run(main())