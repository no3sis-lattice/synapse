"""
GMP (Good Manufacturing Practice) Policy

Staged quality thresholds that evolve with system maturity:
- bootstrap: 65% coverage (initial development)
- growth: 80% coverage (feature expansion)
- stabilize: 90% coverage (pre-production)
- strict: 93% coverage (production)

Modes:
- warn: Log warnings, don't fail (development)
- strict: Enforce thresholds, fail on violations (CI/production)

Part of Phase 1b: Template System Foundation
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

class GMPStage(Enum):
    """System maturity stages with corresponding quality thresholds"""
    BOOTSTRAP = "bootstrap"   # Initial development
    GROWTH = "growth"         # Feature expansion
    STABILIZE = "stabilize"   # Pre-production hardening
    STRICT = "strict"         # Production quality


class GMPMode(Enum):
    """Enforcement modes"""
    WARN = "warn"       # Log warnings, don't fail
    STRICT = "strict"   # Enforce thresholds, fail on violations


# Stage-specific thresholds
GMP_THRESHOLDS = {
    GMPStage.BOOTSTRAP: {
        "test_coverage_min": 65,
        "test_pass_rate_min": 0.80,  # 80% tests passing
        "max_magic_numbers": 10,
        "max_code_duplication": 0.25,  # 25% duplication allowed
        "max_cyclomatic_complexity": 15
    },
    GMPStage.GROWTH: {
        "test_coverage_min": 80,
        "test_pass_rate_min": 0.90,  # 90% tests passing
        "max_magic_numbers": 5,
        "max_code_duplication": 0.15,  # 15% duplication allowed
        "max_cyclomatic_complexity": 12
    },
    GMPStage.STABILIZE: {
        "test_coverage_min": 90,
        "test_pass_rate_min": 0.95,  # 95% tests passing
        "max_magic_numbers": 2,
        "max_code_duplication": 0.10,  # 10% duplication allowed
        "max_cyclomatic_complexity": 10
    },
    GMPStage.STRICT: {
        "test_coverage_min": 93,
        "test_pass_rate_min": 1.0,   # 100% tests passing
        "max_magic_numbers": 0,
        "max_code_duplication": 0.05,  # 5% duplication allowed
        "max_cyclomatic_complexity": 8
    }
}


@dataclass
class GMPViolation:
    """Represents a GMP policy violation"""
    metric: str
    current_value: float
    threshold_value: float
    severity: str  # "warning" or "error"
    message: str
    stage: GMPStage


@dataclass
class GMPReport:
    """GMP compliance report"""
    stage: GMPStage
    mode: GMPMode
    compliant: bool
    violations: List[GMPViolation]
    warnings: List[GMPViolation]
    metrics: Dict[str, Any]

    def __str__(self) -> str:
        """Human-readable report"""
        lines = []
        lines.append(f"GMP Compliance Report")
        lines.append(f"Stage: {self.stage.value}")
        lines.append(f"Mode: {self.mode.value}")
        lines.append(f"Status: {'✅ COMPLIANT' if self.compliant else '❌ NON-COMPLIANT'}")
        lines.append("")

        if self.violations:
            lines.append(f"Violations ({len(self.violations)}):")
            for i, v in enumerate(self.violations, 1):
                lines.append(f"  {i}. {v.message}")
            lines.append("")

        if self.warnings:
            lines.append(f"Warnings ({len(self.warnings)}):")
            for i, w in enumerate(self.warnings, 1):
                lines.append(f"  {i}. {w.message}")
            lines.append("")

        lines.append("Metrics:")
        for key, value in self.metrics.items():
            lines.append(f"  {key}: {value}")

        return "\n".join(lines)


class GMPValidator:
    """
    Validates code quality metrics against staged GMP thresholds.

    Usage:
        validator = GMPValidator(stage=GMPStage.GROWTH, mode=GMPMode.WARN)
        report = validator.validate(metrics)
        if not report.compliant:
            # Handle violations
    """

    def __init__(
        self,
        stage: GMPStage = GMPStage.BOOTSTRAP,
        mode: GMPMode = GMPMode.WARN
    ):
        """
        Initialize GMP validator.

        Args:
            stage: GMP stage (determines thresholds)
            mode: Enforcement mode (WARN or STRICT)
        """
        self.stage = stage
        self.mode = mode
        self.thresholds = GMP_THRESHOLDS[stage]

    def validate(self, metrics: Dict[str, Any]) -> GMPReport:
        """
        Validate metrics against GMP thresholds.

        Args:
            metrics: Dictionary of metrics to validate
                Required keys:
                - test_coverage: float (0-100)
                - test_pass_rate: float (0-1.0)
                Optional keys:
                - magic_numbers: int
                - code_duplication: float (0-1.0)
                - cyclomatic_complexity: float

        Returns:
            GMPReport with validation results
        """
        violations = []
        warnings = []

        # Validate test coverage
        coverage = metrics.get("test_coverage", 0)
        min_coverage = self.thresholds["test_coverage_min"]

        if coverage < min_coverage:
            violation = GMPViolation(
                metric="test_coverage",
                current_value=coverage,
                threshold_value=min_coverage,
                severity="error" if self.mode == GMPMode.STRICT else "warning",
                message=f"Test coverage {coverage}% below threshold {min_coverage}%",
                stage=self.stage
            )

            if self.mode == GMPMode.STRICT:
                violations.append(violation)
            else:
                warnings.append(violation)

        # Validate test pass rate
        pass_rate = metrics.get("test_pass_rate", 0.0)
        min_pass_rate = self.thresholds["test_pass_rate_min"]

        if pass_rate < min_pass_rate:
            violation = GMPViolation(
                metric="test_pass_rate",
                current_value=pass_rate,
                threshold_value=min_pass_rate,
                severity="error" if self.mode == GMPMode.STRICT else "warning",
                message=f"Test pass rate {pass_rate:.1%} below threshold {min_pass_rate:.1%}",
                stage=self.stage
            )

            if self.mode == GMPMode.STRICT:
                violations.append(violation)
            else:
                warnings.append(violation)

        # Validate magic numbers (optional)
        if "magic_numbers" in metrics:
            magic_count = metrics["magic_numbers"]
            max_magic = self.thresholds["max_magic_numbers"]

            if magic_count > max_magic:
                violation = GMPViolation(
                    metric="magic_numbers",
                    current_value=magic_count,
                    threshold_value=max_magic,
                    severity="warning",  # Always warning for magic numbers
                    message=f"Magic numbers count {magic_count} exceeds threshold {max_magic}",
                    stage=self.stage
                )
                warnings.append(violation)

        # Validate code duplication (optional)
        if "code_duplication" in metrics:
            duplication = metrics["code_duplication"]
            max_duplication = self.thresholds["max_code_duplication"]

            if duplication > max_duplication:
                violation = GMPViolation(
                    metric="code_duplication",
                    current_value=duplication,
                    threshold_value=max_duplication,
                    severity="warning",  # Always warning for duplication
                    message=f"Code duplication {duplication:.1%} exceeds threshold {max_duplication:.1%}",
                    stage=self.stage
                )
                warnings.append(violation)

        # Validate cyclomatic complexity (optional)
        if "cyclomatic_complexity" in metrics:
            complexity = metrics["cyclomatic_complexity"]
            max_complexity = self.thresholds["max_cyclomatic_complexity"]

            if complexity > max_complexity:
                violation = GMPViolation(
                    metric="cyclomatic_complexity",
                    current_value=complexity,
                    threshold_value=max_complexity,
                    severity="warning",  # Always warning for complexity
                    message=f"Cyclomatic complexity {complexity} exceeds threshold {max_complexity}",
                    stage=self.stage
                )
                warnings.append(violation)

        # Determine compliance
        compliant = len(violations) == 0

        # Log results
        if violations:
            logger.error(f"GMP validation failed ({len(violations)} violations)")
            for v in violations:
                logger.error(f"  - {v.message}")

        if warnings:
            logger.warning(f"GMP warnings ({len(warnings)} warnings)")
            for w in warnings:
                logger.warning(f"  - {w.message}")

        return GMPReport(
            stage=self.stage,
            mode=self.mode,
            compliant=compliant,
            violations=violations,
            warnings=warnings,
            metrics=metrics
        )

    def validate_and_raise(self, metrics: Dict[str, Any]) -> GMPReport:
        """
        Validate and raise exception on non-compliance (strict mode only).

        Args:
            metrics: Metrics to validate

        Returns:
            GMPReport

        Raises:
            GMPComplianceError: If validation fails in strict mode
        """
        report = self.validate(metrics)

        if not report.compliant and self.mode == GMPMode.STRICT:
            raise GMPComplianceError(
                f"GMP compliance failed: {len(report.violations)} violations",
                report=report
            )

        return report


class GMPComplianceError(Exception):
    """Exception raised when GMP validation fails in strict mode"""

    def __init__(self, message: str, report: GMPReport):
        super().__init__(message)
        self.report = report


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def validate_gmp(
    metrics: Dict[str, Any],
    stage: GMPStage = GMPStage.BOOTSTRAP,
    mode: GMPMode = GMPMode.WARN
) -> GMPReport:
    """
    Validate metrics against GMP policy.

    Args:
        metrics: Metrics to validate
        stage: GMP stage
        mode: Enforcement mode

    Returns:
        GMPReport
    """
    validator = GMPValidator(stage=stage, mode=mode)
    return validator.validate(metrics)


def get_stage_thresholds(stage: GMPStage) -> Dict[str, Any]:
    """Get thresholds for a specific GMP stage"""
    return GMP_THRESHOLDS[stage].copy()


def recommend_stage(metrics: Dict[str, Any]) -> GMPStage:
    """
    Recommend appropriate GMP stage based on current metrics.

    Args:
        metrics: Current metrics

    Returns:
        Recommended GMPStage
    """
    coverage = metrics.get("test_coverage", 0)
    pass_rate = metrics.get("test_pass_rate", 0.0)

    # Check against each stage (descending order)
    for stage in [GMPStage.STRICT, GMPStage.STABILIZE, GMPStage.GROWTH, GMPStage.BOOTSTRAP]:
        thresholds = GMP_THRESHOLDS[stage]

        if (coverage >= thresholds["test_coverage_min"] and
            pass_rate >= thresholds["test_pass_rate_min"]):
            return stage

    # Default to bootstrap
    return GMPStage.BOOTSTRAP


# ============================================================================
# CLI INTEGRATION
# ============================================================================

def validate_project_gmp(
    test_coverage: float,
    test_pass_rate: float,
    stage: str = "bootstrap",
    mode: str = "warn"
) -> int:
    """
    CLI-friendly GMP validation.

    Args:
        test_coverage: Test coverage percentage (0-100)
        test_pass_rate: Test pass rate (0-1.0)
        stage: Stage name (bootstrap, growth, stabilize, strict)
        mode: Mode name (warn, strict)

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    try:
        # Parse stage and mode
        gmp_stage = GMPStage(stage.lower())
        gmp_mode = GMPMode(mode.lower())

        # Create metrics
        metrics = {
            "test_coverage": test_coverage,
            "test_pass_rate": test_pass_rate
        }

        # Validate
        validator = GMPValidator(stage=gmp_stage, mode=gmp_mode)
        report = validator.validate(metrics)

        # Print report
        print(report)

        # Return exit code
        return 0 if report.compliant else 1

    except ValueError as e:
        print(f"Error: {e}")
        return 1
