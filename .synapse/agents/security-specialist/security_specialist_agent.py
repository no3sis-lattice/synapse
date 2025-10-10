#!/usr/bin/env python3
"""
Security Specialist Agent: Comprehensive Security Analysis and Threat Assessment

Provides vulnerability scanning, threat modeling, security hardening recommendations,
and compliance validation with Synapse System integration.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, TypedDict, List, Dict

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

# Claude Agent SDK imports (with fallback to mock)
try:
    from claude_agent_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeAgentOptions
    )
except ImportError:
    print("⚠️  Claude Agent SDK not available, using mock implementations")
    from tools.mock_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeAgentOptions
    )

from tools import (
    # Vulnerability scanning
    scan_vulnerabilities, analyze_dependencies, check_owasp_compliance,
    detect_secrets, audit_permissions, validate_security_headers,

    # Threat modeling
    analyze_threats, create_threat_model, assess_attack_vectors,
    evaluate_risk_score, suggest_mitigations, document_security_requirements,

    # Security hardening
    suggest_hardening, validate_configuration, audit_access_controls,
    check_encryption, review_authentication, analyze_network_security,

    # Compliance
    check_compliance_frameworks, generate_security_reports,
    validate_privacy_requirements, audit_data_protection, assess_regulatory_compliance,

    # Synapse integration
    query_synapse_security, search_vulnerability_patterns
)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Tool argument schemas
class VulnerabilityScanArgs(TypedDict):
    target_path: str
    scan_type: str

class ThreatAnalysisArgs(TypedDict):
    system_components: List[str]
    data_flows: List[str]

class ComplianceCheckArgs(TypedDict):
    frameworks: List[str]
    system_components: List[str]

class SecurityHardeningArgs(TypedDict):
    system_type: str
    current_config: Dict[str, Any]

class SecurityReportArgs(TypedDict):
    assessment_data: Dict[str, Any]
    report_type: str

class SynapseQueryArgs(TypedDict):
    query: str
    context: str


@tool(
    "comprehensive_vulnerability_scan",
    "Perform comprehensive vulnerability scanning of codebase",
    {
        "target_path": str,
        "scan_type": str,
        "include_dependencies": bool,
        "include_secrets": bool
    }
)
async def comprehensive_vulnerability_scan(
    target_path: str = ".",
    scan_type: str = "comprehensive",
    include_dependencies: bool = True,
    include_secrets: bool = True
) -> Dict[str, Any]:
    """
    Perform comprehensive vulnerability scanning of codebase.

    Args:
        target_path: Path to scan (default: current directory)
        scan_type: Scan depth - "quick", "comprehensive", "dependency-only"
        include_dependencies: Include dependency vulnerability analysis
        include_secrets: Include secret/credential detection

    Returns:
        Dict containing comprehensive vulnerability assessment
    """
    console.print(f"[blue]🔍 Starting comprehensive vulnerability scan of {target_path}")

    # Main vulnerability scan
    vulnerabilities = await scan_vulnerabilities(target_path, scan_type)

    results = {
        "scan_metadata": vulnerabilities["scan_metadata"],
        "vulnerability_summary": {
            "critical": len(vulnerabilities["critical"]),
            "high": len(vulnerabilities["high"]),
            "medium": len(vulnerabilities["medium"]),
            "low": len(vulnerabilities["low"])
        },
        "detailed_findings": vulnerabilities,
        "additional_analysis": {}
    }

    # Additional analysis based on flags
    if include_dependencies:
        console.print("[yellow]📦 Analyzing dependencies...")
        dep_analysis = await analyze_dependencies(target_path)
        results["additional_analysis"]["dependencies"] = dep_analysis

    if include_secrets:
        console.print("[red]🔐 Scanning for secrets...")
        secrets = await detect_secrets(target_path)
        results["additional_analysis"]["secrets"] = secrets

    # OWASP compliance check
    console.print("[blue]🛡️  Checking OWASP compliance...")
    owasp_results = await check_owasp_compliance(target_path)
    results["additional_analysis"]["owasp_compliance"] = owasp_results

    console.print(f"[green]✅ Vulnerability scan complete. Found {results['vulnerability_summary']['critical']} critical issues")

    return {
        "content": [{
            "type": "text",
            "text": str(results)
        }]
    }


@tool(
    "threat_modeling_analysis",
    "Perform comprehensive threat modeling using STRIDE methodology",
    {
        "project_description": str,
        "system_components": list,
        "architecture": dict,
        "entry_points": list
    }
)
async def threat_modeling_analysis(
    project_description: str,
    system_components: List[str] = None,
    architecture: Dict[str, Any] = None,
    entry_points: List[str] = None
) -> Dict[str, Any]:
    """
    Perform comprehensive threat modeling using STRIDE methodology.

    Args:
        project_description: Description of the system to model
        system_components: List of system components (web_app, database, api, etc.)
        architecture: Architecture details including data flows and trust boundaries
        entry_points: System entry points for attack vector analysis

    Returns:
        Dict containing complete threat model and risk analysis
    """
    console.print("[blue]🎯 Performing comprehensive threat modeling analysis")

    if system_components is None:
        system_components = ["web_application", "api", "database"]
    if architecture is None:
        architecture = {}
    if entry_points is None:
        entry_points = []

    # Create comprehensive threat model
    threat_model = await create_threat_model(project_description, architecture)

    # Analyze attack vectors for entry points
    attack_vectors = {}
    if entry_points:
        console.print("[yellow]⚔️  Analyzing attack vectors...")
        attack_vectors = await assess_attack_vectors(entry_points)

    # Analyze specific threats
    console.print("[blue]🔍 Analyzing threats using STRIDE methodology...")
    threat_analysis = await analyze_threats(system_components)

    # Generate mitigation suggestions
    console.print("[green]🛡️  Generating mitigation strategies...")
    all_threats = []
    for category_threats in threat_analysis["threats_by_category"].values():
        all_threats.extend(category_threats)

    mitigations = await suggest_mitigations(all_threats)

    # Document security requirements
    compliance_frameworks = architecture.get("compliance_requirements", ["OWASP", "NIST"])
    security_requirements = await document_security_requirements(all_threats, compliance_frameworks)

    results = {
        "threat_model": threat_model,
        "threat_analysis": threat_analysis,
        "attack_vectors": attack_vectors,
        "mitigation_strategies": mitigations,
        "security_requirements": security_requirements,
        "executive_summary": {
            "total_threats_identified": len(all_threats),
            "critical_risks": len([t for t in all_threats if t.get("risk_score", 0) >= 12]),
            "high_priority_mitigations": len(mitigations.get("mitigation_strategies", {}).get("immediate_actions", [])),
            "compliance_frameworks": compliance_frameworks
        }
    }

    console.print(f"[green]✅ Threat modeling complete. Identified {results['executive_summary']['total_threats_identified']} threats")

    return {
        "content": [{
            "type": "text",
            "text": str(results)
        }]
    }


@tool(
    "security_compliance_assessment",
    "Perform comprehensive security compliance assessment",
    {
        "frameworks": list,
        "system_components": list,
        "business_operations": list,
        "industry": str
    }
)
async def security_compliance_assessment(
    frameworks: List[str],
    system_components: List[str] = None,
    business_operations: List[str] = None,
    industry: str = "technology"
) -> Dict[str, Any]:
    """
    Perform comprehensive security compliance assessment.

    Args:
        frameworks: List of compliance frameworks (OWASP, NIST, ISO27001, SOC2, GDPR, etc.)
        system_components: List of system components to assess
        business_operations: List of business operations/activities
        industry: Industry sector for regulatory requirements

    Returns:
        Dict containing complete compliance assessment and gap analysis
    """
    console.print(f"[blue]📋 Performing compliance assessment for {', '.join(frameworks)}")

    if system_components is None:
        system_components = ["web_application", "database", "api"]
    if business_operations is None:
        business_operations = ["data_processing", "user_authentication"]

    # Main compliance framework check
    compliance_results = await check_compliance_frameworks(frameworks, system_components)

    # Privacy requirements validation (if applicable)
    privacy_validation = {}
    if any(fw in ["GDPR", "CCPA", "PIPEDA"] for fw in frameworks):
        console.print("[yellow]🔒 Validating privacy requirements...")
        privacy_validation = await validate_privacy_requirements(business_operations)

    # Industry-specific regulatory assessment
    console.print(f"[blue]🏢 Assessing {industry} industry regulations...")
    regulatory_compliance = await assess_regulatory_compliance(industry, business_operations)

    # Data protection audit
    console.print("[green]🛡️  Auditing data protection measures...")
    data_stores = [comp for comp in system_components if "database" in comp.lower() or "storage" in comp.lower()]
    if not data_stores:
        data_stores = ["primary_database"]

    data_protection_audit = await audit_data_protection(data_stores)

    results = {
        "compliance_assessment": compliance_results,
        "privacy_validation": privacy_validation,
        "regulatory_compliance": regulatory_compliance,
        "data_protection_audit": data_protection_audit,
        "executive_summary": {
            "overall_compliance_score": compliance_results["overall_compliance_score"],
            "frameworks_assessed": len(frameworks),
            "critical_gaps": len(compliance_results["critical_gaps"]),
            "applicable_regulations": regulatory_compliance.get("applicable_regulations", []),
            "privacy_compliant": len(privacy_validation.get("compliance_gaps", [])) == 0
        },
        "action_items": {
            "immediate": compliance_results.get("recommendations", [])[:3],
            "regulatory": regulatory_compliance.get("implementation_roadmap", []),
            "privacy": privacy_validation.get("recommended_measures", [])[:5]
        }
    }

    console.print(f"[green]✅ Compliance assessment complete. Overall score: {results['executive_summary']['overall_compliance_score']}%")

    return {
        "content": [{
            "type": "text",
            "text": str(results)
        }]
    }


@tool(
    "security_hardening_recommendations",
    "Generate comprehensive security hardening recommendations",
    {
        "system_type": str,
        "target_path": str,
        "config_files": list,
        "network_config": dict
    }
)
async def security_hardening_recommendations(
    system_type: str = "web_application",
    target_path: str = ".",
    config_files: List[str] = None,
    network_config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive security hardening recommendations.

    Args:
        system_type: Type of system (web_application, api, database, mobile_app)
        target_path: Path to analyze for hardening opportunities
        config_files: List of configuration files to review
        network_config: Network configuration details

    Returns:
        Dict containing comprehensive hardening recommendations
    """
    console.print(f"[blue]🔧 Generating security hardening recommendations for {system_type}")

    if config_files is None:
        config_files = []
    if network_config is None:
        network_config = {}

    # Get system-specific hardening suggestions
    hardening_suggestions = await suggest_hardening(system_type)

    # Validate current configurations
    console.print("[yellow]⚙️  Validating current configurations...")
    config_validation = await validate_configuration(config_files, system_type.split('_')[0])

    # Audit access controls
    console.print("[blue]🔐 Auditing access controls...")
    access_audit = await audit_access_controls(target_path, "file_system")

    # Check encryption implementation
    console.print("[green]🔒 Analyzing encryption implementation...")
    encryption_analysis = await check_encryption(target_path, "data_at_rest")

    # Review authentication mechanisms
    console.print("[cyan]🗝️  Reviewing authentication mechanisms...")
    auth_review = await review_authentication(config_files, system_type)

    # Analyze network security
    console.print("[magenta]🌐 Analyzing network security...")
    network_analysis = await analyze_network_security(network_config)

    # Consolidate all recommendations
    all_recommendations = []
    all_recommendations.extend(hardening_suggestions.get("critical", []))
    all_recommendations.extend(hardening_suggestions.get("high", []))
    all_recommendations.extend(config_validation.get("recommendations", []))
    all_recommendations.extend(access_audit.get("recommendations", []))
    all_recommendations.extend(encryption_analysis.get("encryption_recommendations", []))
    all_recommendations.extend(auth_review.get("recommendations", []))
    all_recommendations.extend(network_analysis.get("recommendations", []))

    # Prioritize and deduplicate
    unique_recommendations = list(set(all_recommendations))

    results = {
        "hardening_analysis": {
            "system_hardening": hardening_suggestions,
            "configuration_validation": config_validation,
            "access_control_audit": access_audit,
            "encryption_analysis": encryption_analysis,
            "authentication_review": auth_review,
            "network_security": network_analysis
        },
        "prioritized_recommendations": {
            "immediate_actions": unique_recommendations[:5],
            "short_term_improvements": unique_recommendations[5:10],
            "long_term_investments": unique_recommendations[10:15]
        },
        "implementation_guides": hardening_suggestions.get("implementation_guides", {}),
        "security_score": {
            "current": _calculate_security_score({
                "config_issues": len(config_validation.get("insecure_configurations", [])),
                "access_issues": len(access_audit.get("excessive_permissions", [])),
                "crypto_issues": len(encryption_analysis.get("weak_encryption", [])),
                "auth_issues": len(auth_review.get("weak_practices", []))
            }),
            "potential": 9.5  # Potential score after implementing recommendations
        }
    }

    console.print(f"[green]✅ Hardening analysis complete. Current security score: {results['security_score']['current']}/10")

    return {
        "content": [{
            "type": "text",
            "text": str(results)
        }]
    }


@tool(
    "generate_comprehensive_security_report",
    "Generate comprehensive security assessment reports",
    {
        "assessment_data": dict,
        "report_type": str,
        "include_compliance": bool,
        "include_recommendations": bool
    }
)
async def generate_comprehensive_security_report(
    assessment_data: Dict[str, Any],
    report_type: str = "executive",
    include_compliance: bool = True,
    include_recommendations: bool = True
) -> Dict[str, Any]:
    """
    Generate comprehensive security assessment reports.

    Args:
        assessment_data: Combined data from security assessments
        report_type: Report type - "executive", "technical", "audit"
        include_compliance: Include compliance section in report
        include_recommendations: Include detailed recommendations

    Returns:
        Dict containing formatted comprehensive security report
    """
    console.print(f"[blue]📊 Generating {report_type} security report")

    # Generate base security report
    report = await generate_security_reports(assessment_data, report_type)

    # Enhance with additional analysis
    if include_compliance and "compliance" in assessment_data:
        console.print("[yellow]📋 Adding compliance analysis...")
        compliance_section = {
            "frameworks_assessed": assessment_data["compliance"].get("framework_assessments", {}),
            "overall_compliance": assessment_data["compliance"].get("overall_compliance_score", 0),
            "critical_gaps": assessment_data["compliance"].get("critical_gaps", [])
        }
        report["compliance_analysis"] = compliance_section

    if include_recommendations:
        console.print("[green]💡 Compiling actionable recommendations...")
        all_recommendations = []

        # Collect recommendations from all assessment types
        for assessment_type, data in assessment_data.items():
            if isinstance(data, dict) and "recommendations" in data:
                all_recommendations.extend(data["recommendations"])

        # Categorize and prioritize recommendations
        categorized_recommendations = _categorize_recommendations(all_recommendations)
        report["actionable_recommendations"] = categorized_recommendations

    # Add executive dashboard for executive reports
    if report_type == "executive":
        report["executive_dashboard"] = {
            "security_posture": _assess_overall_posture(assessment_data),
            "key_metrics": _extract_key_metrics(assessment_data),
            "investment_priorities": _identify_security_investments(assessment_data),
            "compliance_status": _summarize_compliance_status(assessment_data)
        }

    console.print("[green]✅ Comprehensive security report generated")

    return {
        "content": [{
            "type": "text",
            "text": str(report)
        }]
    }


@tool(
    "query_security_knowledge",
    "Query Synapse knowledge base for security-related information and patterns",
    {
        "query": str,
        "context": str,
        "include_patterns": bool
    }
)
async def query_security_knowledge(
    query: str,
    context: str = "security_analysis",
    include_patterns: bool = True
) -> Dict[str, Any]:
    """
    Query Synapse knowledge base for security-related information and patterns.

    Args:
        query: Security-related query
        context: Query context (security_analysis, threat_modeling, compliance, etc.)
        include_patterns: Include vulnerability pattern analysis

    Returns:
        Dict containing relevant security knowledge and patterns
    """
    console.print(f"[blue]🧠 Querying security knowledge: {query}")

    # Query main security knowledge
    knowledge_results = await query_synapse_security(query, context)

    results = {
        "query_results": knowledge_results,
        "vulnerability_patterns": {},
        "recommendations": knowledge_results.get("best_practices", [])
    }

    # Include vulnerability pattern analysis if requested
    if include_patterns:
        console.print("[yellow]🔍 Analyzing vulnerability patterns...")

        # Extract technology stack from query or assume common stack
        common_technologies = ["python", "javascript", "typescript", "java"]
        pattern_search = await search_vulnerability_patterns(query, common_technologies)
        results["vulnerability_patterns"] = pattern_search

        # Merge pattern-specific recommendations
        if pattern_search.get("recommendations"):
            results["recommendations"].extend(pattern_search["recommendations"])

    console.print("[green]✅ Security knowledge query complete")

    return {
        "content": [{
            "type": "text",
            "text": str(results)
        }]
    }


def _calculate_security_score(issues: Dict[str, int]) -> float:
    """Calculate overall security score based on identified issues."""
    base_score = 10.0

    # Deduct points for various types of issues
    deductions = {
        "config_issues": 0.5,
        "access_issues": 0.3,
        "crypto_issues": 0.8,
        "auth_issues": 0.7
    }

    for issue_type, count in issues.items():
        if issue_type in deductions:
            base_score -= (count * deductions[issue_type])

    return max(0.0, min(10.0, base_score))


def _categorize_recommendations(recommendations: List[str]) -> Dict[str, List[str]]:
    """Categorize security recommendations by type and priority."""
    categories = {
        "critical_security": [],
        "authentication": [],
        "encryption": [],
        "access_control": [],
        "monitoring": [],
        "compliance": [],
        "general": []
    }

    for rec in recommendations:
        rec_lower = rec.lower()

        if any(word in rec_lower for word in ["critical", "urgent", "immediate"]):
            categories["critical_security"].append(rec)
        elif any(word in rec_lower for word in ["auth", "login", "password", "mfa"]):
            categories["authentication"].append(rec)
        elif any(word in rec_lower for word in ["encrypt", "tls", "ssl", "crypto"]):
            categories["encryption"].append(rec)
        elif any(word in rec_lower for word in ["access", "permission", "privilege"]):
            categories["access_control"].append(rec)
        elif any(word in rec_lower for word in ["monitor", "log", "alert"]):
            categories["monitoring"].append(rec)
        elif any(word in rec_lower for word in ["compliance", "gdpr", "hipaa", "sox"]):
            categories["compliance"].append(rec)
        else:
            categories["general"].append(rec)

    return categories


def _assess_overall_posture(assessment_data: Dict[str, Any]) -> str:
    """Assess overall security posture from assessment data."""
    # Simple scoring based on critical issues found
    total_critical = 0

    for data in assessment_data.values():
        if isinstance(data, dict):
            if "critical" in data:
                total_critical += len(data["critical"]) if isinstance(data["critical"], list) else data["critical"]

    if total_critical == 0:
        return "Strong"
    elif total_critical <= 3:
        return "Good"
    elif total_critical <= 10:
        return "Fair"
    else:
        return "Needs Improvement"


def _extract_key_metrics(assessment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key security metrics from assessment data."""
    return {
        "vulnerabilities_found": sum(
            len(data.get("vulnerabilities", [])) if isinstance(data.get("vulnerabilities"), list) else 0
            for data in assessment_data.values() if isinstance(data, dict)
        ),
        "compliance_score": assessment_data.get("compliance", {}).get("overall_compliance_score", "N/A"),
        "critical_issues": sum(
            len(data.get("critical", [])) if isinstance(data.get("critical"), list) else 0
            for data in assessment_data.values() if isinstance(data, dict)
        )
    }


def _identify_security_investments(assessment_data: Dict[str, Any]) -> List[str]:
    """Identify priority security investments."""
    return [
        "Security monitoring and SIEM implementation",
        "Advanced threat detection systems",
        "Security awareness training program",
        "Automated security testing integration"
    ]


def _summarize_compliance_status(assessment_data: Dict[str, Any]) -> Dict[str, str]:
    """Summarize compliance status across frameworks."""
    compliance_data = assessment_data.get("compliance", {})

    if not compliance_data:
        return {"status": "Not assessed"}

    return {
        "overall_score": f"{compliance_data.get('overall_compliance_score', 0)}%",
        "critical_gaps": str(len(compliance_data.get("critical_gaps", []))),
        "frameworks": str(len(compliance_data.get("framework_assessments", {})))
    }


async def main():
    """Main entry point for the Security Specialist Agent."""
    console.print(Panel(
        "[bold blue]Security Specialist Agent[/bold blue]\n"
        "Comprehensive security analysis, threat modeling, and compliance validation",
        title="🛡️ Starting Agent",
        border_style="blue"
    ))

    # Collect all tools
    tools = [
        comprehensive_vulnerability_scan,
        threat_modeling_analysis,
        security_compliance_assessment,
        security_hardening_recommendations,
        generate_comprehensive_security_report,
        query_security_knowledge
    ]

    # Create MCP server
    server = create_sdk_mcp_server(
        name="security_specialist_tools",
            version="1.0.0",
        tools=tools
    )

    console.print(f"[green]✅ Security Specialist Agent ready with {len(tools)} tools")
    console.print("\n[yellow]Available capabilities:")

    capabilities_table = Table(title="Security Analysis Capabilities")
    capabilities_table.add_column("Category", style="cyan")
    capabilities_table.add_column("Capabilities", style="white")

    capabilities_table.add_row(
        "Vulnerability Analysis",
        "Comprehensive scanning, dependency analysis, secret detection, OWASP compliance"
    )
    capabilities_table.add_row(
        "Threat Modeling",
        "STRIDE methodology, attack vector analysis, risk assessment, mitigation strategies"
    )
    capabilities_table.add_row(
        "Security Hardening",
        "Configuration validation, access control audit, encryption analysis, authentication review"
    )
    capabilities_table.add_row(
        "Compliance Assessment",
        "Multi-framework compliance (GDPR, HIPAA, SOC2, etc.), gap analysis, regulatory requirements"
    )
    capabilities_table.add_row(
        "Reporting & Knowledge",
        "Executive/technical reports, Synapse knowledge integration, actionable recommendations"
    )

    console.print(capabilities_table)

    # Start the server
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[red]🛑 Security Specialist Agent shutting down...")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}")
        sys.exit(1)