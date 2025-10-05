#!/usr/bin/env python3
"""
Unit Tests for GMP Policy - Phase 1b

Tests coverage:
- Staged threshold validation (bootstrap, growth, stabilize, strict)
- Validation modes (WARN, STRICT)
- Test coverage validation
- Test pass rate validation
- Optional metric validations (magic numbers, duplication, complexity)
- GMP report generation
- Compliance checking
- Stage recommendation
- CLI integration
"""

import pytest
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from orchestration.gmp_policy import (
    GMPValidator,
    GMPStage,
    GMPMode,
    GMPReport,
    GMPViolation,
    GMPComplianceError,
    GMP_THRESHOLDS,
    validate_gmp,
    get_stage_thresholds,
    recommend_stage,
    validate_project_gmp
)


# ============================================================================
# THRESHOLD VALIDATION TESTS
# ============================================================================

class TestStageThresholds:
    """Test suite for stage-specific thresholds"""

    def test_bootstrap_thresholds(self):
        """Test bootstrap stage thresholds"""
        thresholds = get_stage_thresholds(GMPStage.BOOTSTRAP)

        assert thresholds["test_coverage_min"] == 65
        assert thresholds["test_pass_rate_min"] == 0.80
        assert thresholds["max_magic_numbers"] == 10
        assert thresholds["max_code_duplication"] == 0.25
        assert thresholds["max_cyclomatic_complexity"] == 15

    def test_growth_thresholds(self):
        """Test growth stage thresholds"""
        thresholds = get_stage_thresholds(GMPStage.GROWTH)

        assert thresholds["test_coverage_min"] == 80
        assert thresholds["test_pass_rate_min"] == 0.90

    def test_stabilize_thresholds(self):
        """Test stabilize stage thresholds"""
        thresholds = get_stage_thresholds(GMPStage.STABILIZE)

        assert thresholds["test_coverage_min"] == 90
        assert thresholds["test_pass_rate_min"] == 0.95

    def test_strict_thresholds(self):
        """Test strict stage thresholds"""
        thresholds = get_stage_thresholds(GMPStage.STRICT)

        assert thresholds["test_coverage_min"] == 93
        assert thresholds["test_pass_rate_min"] == 1.0
        assert thresholds["max_magic_numbers"] == 0

    def test_thresholds_increase_with_maturity(self):
        """Test that thresholds increase as system matures"""
        bootstrap = get_stage_thresholds(GMPStage.BOOTSTRAP)
        growth = get_stage_thresholds(GMPStage.GROWTH)
        stabilize = get_stage_thresholds(GMPStage.STABILIZE)
        strict = get_stage_thresholds(GMPStage.STRICT)

        # Coverage increases
        assert bootstrap["test_coverage_min"] < growth["test_coverage_min"]
        assert growth["test_coverage_min"] < stabilize["test_coverage_min"]
        assert stabilize["test_coverage_min"] < strict["test_coverage_min"]

        # Pass rate increases
        assert bootstrap["test_pass_rate_min"] < growth["test_pass_rate_min"]
        assert growth["test_pass_rate_min"] < stabilize["test_pass_rate_min"]
        assert stabilize["test_pass_rate_min"] <= strict["test_pass_rate_min"]


# ============================================================================
# BOOTSTRAP STAGE VALIDATION TESTS
# ============================================================================

class TestBootstrapValidation:
    """Test suite for bootstrap stage validation"""

    def test_bootstrap_compliant_metrics_strict(self):
        """Test compliant metrics in bootstrap/strict mode"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 70,
            "test_pass_rate": 0.85
        }

        report = validator.validate(metrics)

        assert report.compliant is True
        assert len(report.violations) == 0
        assert report.stage == GMPStage.BOOTSTRAP
        assert report.mode == GMPMode.STRICT

    def test_bootstrap_low_coverage_strict(self):
        """Test low coverage fails in bootstrap/strict mode"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 50,  # Below 65% threshold
            "test_pass_rate": 0.85
        }

        report = validator.validate(metrics)

        assert report.compliant is False
        assert len(report.violations) > 0
        assert any(v.metric == "test_coverage" for v in report.violations)

    def test_bootstrap_low_coverage_warn(self):
        """Test low coverage warns in bootstrap/warn mode"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.WARN)

        metrics = {
            "test_coverage": 50,
            "test_pass_rate": 0.85
        }

        report = validator.validate(metrics)

        assert report.compliant is True  # Passes in warn mode
        assert len(report.warnings) > 0
        assert any(w.metric == "test_coverage" for w in report.warnings)

    def test_bootstrap_low_pass_rate_strict(self):
        """Test low pass rate fails in bootstrap/strict mode"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 70,
            "test_pass_rate": 0.70  # Below 0.80 threshold
        }

        report = validator.validate(metrics)

        assert report.compliant is False
        assert any(v.metric == "test_pass_rate" for v in report.violations)


# ============================================================================
# GROWTH STAGE VALIDATION TESTS
# ============================================================================

class TestGrowthValidation:
    """Test suite for growth stage validation"""

    def test_growth_compliant_metrics(self):
        """Test compliant metrics in growth stage"""
        validator = GMPValidator(stage=GMPStage.GROWTH, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 85,
            "test_pass_rate": 0.92
        }

        report = validator.validate(metrics)

        assert report.compliant is True
        assert len(report.violations) == 0

    def test_growth_below_threshold(self):
        """Test metrics below growth threshold fail"""
        validator = GMPValidator(stage=GMPStage.GROWTH, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 75,  # Below 80% threshold
            "test_pass_rate": 0.85  # Below 0.90 threshold
        }

        report = validator.validate(metrics)

        assert report.compliant is False
        assert len(report.violations) == 2


# ============================================================================
# STABILIZE STAGE VALIDATION TESTS
# ============================================================================

class TestStabilizeValidation:
    """Test suite for stabilize stage validation"""

    def test_stabilize_compliant_metrics(self):
        """Test compliant metrics in stabilize stage"""
        validator = GMPValidator(stage=GMPStage.STABILIZE, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 92,
            "test_pass_rate": 0.97
        }

        report = validator.validate(metrics)

        assert report.compliant is True

    def test_stabilize_high_requirements(self):
        """Test stabilize stage has high requirements"""
        validator = GMPValidator(stage=GMPStage.STABILIZE, mode=GMPMode.STRICT)

        # Metrics that pass growth but fail stabilize
        metrics = {
            "test_coverage": 85,  # Passes growth (80%) but fails stabilize (90%)
            "test_pass_rate": 0.92
        }

        report = validator.validate(metrics)

        assert report.compliant is False


# ============================================================================
# STRICT STAGE VALIDATION TESTS
# ============================================================================

class TestStrictValidation:
    """Test suite for strict stage validation"""

    def test_strict_compliant_metrics(self):
        """Test compliant metrics in strict stage"""
        validator = GMPValidator(stage=GMPStage.STRICT, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 95,
            "test_pass_rate": 1.0  # Must be 100%
        }

        report = validator.validate(metrics)

        assert report.compliant is True

    def test_strict_requires_perfect_pass_rate(self):
        """Test strict stage requires 100% test pass rate"""
        validator = GMPValidator(stage=GMPStage.STRICT, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 95,
            "test_pass_rate": 0.99  # 99% not good enough
        }

        report = validator.validate(metrics)

        assert report.compliant is False
        assert any(v.metric == "test_pass_rate" for v in report.violations)

    def test_strict_highest_coverage_requirement(self):
        """Test strict stage has highest coverage requirement"""
        validator = GMPValidator(stage=GMPStage.STRICT, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 90,  # Passes stabilize but fails strict (93%)
            "test_pass_rate": 1.0
        }

        report = validator.validate(metrics)

        assert report.compliant is False


# ============================================================================
# OPTIONAL METRICS TESTS
# ============================================================================

class TestOptionalMetrics:
    """Test suite for optional metric validations"""

    def test_magic_numbers_warning(self):
        """Test magic numbers generate warnings"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 70,
            "test_pass_rate": 0.85,
            "magic_numbers": 15  # Exceeds bootstrap threshold of 10
        }

        report = validator.validate(metrics)

        # Still compliant (magic numbers only warn)
        assert report.compliant is True
        assert len(report.warnings) > 0
        assert any(w.metric == "magic_numbers" for w in report.warnings)

    def test_code_duplication_warning(self):
        """Test code duplication generates warnings"""
        validator = GMPValidator(stage=GMPStage.GROWTH, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 85,
            "test_pass_rate": 0.92,
            "code_duplication": 0.20  # Exceeds growth threshold of 0.15
        }

        report = validator.validate(metrics)

        assert report.compliant is True
        assert any(w.metric == "code_duplication" for w in report.warnings)

    def test_cyclomatic_complexity_warning(self):
        """Test cyclomatic complexity generates warnings"""
        validator = GMPValidator(stage=GMPStage.STABILIZE, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 92,
            "test_pass_rate": 0.97,
            "cyclomatic_complexity": 12  # Exceeds stabilize threshold of 10
        }

        report = validator.validate(metrics)

        assert report.compliant is True
        assert any(w.metric == "cyclomatic_complexity" for w in report.warnings)

    def test_all_optional_metrics(self):
        """Test validation with all optional metrics"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.WARN)

        metrics = {
            "test_coverage": 70,
            "test_pass_rate": 0.85,
            "magic_numbers": 5,
            "code_duplication": 0.10,
            "cyclomatic_complexity": 8
        }

        report = validator.validate(metrics)

        # All within thresholds
        assert report.compliant is True
        assert len(report.warnings) == 0


# ============================================================================
# GMP REPORT TESTS
# ============================================================================

class TestGMPReport:
    """Test suite for GMP report generation"""

    def test_report_structure(self):
        """Test GMP report has correct structure"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 70,
            "test_pass_rate": 0.85
        }

        report = validator.validate(metrics)

        assert hasattr(report, 'stage')
        assert hasattr(report, 'mode')
        assert hasattr(report, 'compliant')
        assert hasattr(report, 'violations')
        assert hasattr(report, 'warnings')
        assert hasattr(report, 'metrics')

    def test_report_string_representation(self):
        """Test GMP report string formatting"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 50,  # Will violate
            "test_pass_rate": 0.70  # Will violate
        }

        report = validator.validate(metrics)
        report_str = str(report)

        assert "GMP Compliance Report" in report_str
        assert "Stage: bootstrap" in report_str
        assert "Mode: strict" in report_str
        assert "Violations" in report_str


# ============================================================================
# VIOLATION TRACKING TESTS
# ============================================================================

class TestViolationTracking:
    """Test suite for violation tracking"""

    def test_violation_details(self):
        """Test violation contains correct details"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 50,
            "test_pass_rate": 0.85
        }

        report = validator.validate(metrics)

        assert len(report.violations) > 0
        violation = report.violations[0]

        assert violation.metric == "test_coverage"
        assert violation.current_value == 50
        assert violation.threshold_value == 65
        assert violation.severity == "error"
        assert violation.stage == GMPStage.BOOTSTRAP

    def test_multiple_violations(self):
        """Test multiple violations are tracked"""
        validator = GMPValidator(stage=GMPStage.GROWTH, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 50,  # Violates
            "test_pass_rate": 0.70  # Violates
        }

        report = validator.validate(metrics)

        assert len(report.violations) == 2

        violation_metrics = [v.metric for v in report.violations]
        assert "test_coverage" in violation_metrics
        assert "test_pass_rate" in violation_metrics


# ============================================================================
# STAGE RECOMMENDATION TESTS
# ============================================================================

class TestStageRecommendation:
    """Test suite for stage recommendation"""

    def test_recommend_bootstrap(self):
        """Test recommendation for bootstrap stage"""
        metrics = {
            "test_coverage": 60,
            "test_pass_rate": 0.75
        }

        recommended = recommend_stage(metrics)

        assert recommended == GMPStage.BOOTSTRAP

    def test_recommend_growth(self):
        """Test recommendation for growth stage"""
        metrics = {
            "test_coverage": 82,
            "test_pass_rate": 0.91
        }

        recommended = recommend_stage(metrics)

        assert recommended == GMPStage.GROWTH

    def test_recommend_stabilize(self):
        """Test recommendation for stabilize stage"""
        metrics = {
            "test_coverage": 91,
            "test_pass_rate": 0.96
        }

        recommended = recommend_stage(metrics)

        assert recommended == GMPStage.STABILIZE

    def test_recommend_strict(self):
        """Test recommendation for strict stage"""
        metrics = {
            "test_coverage": 95,
            "test_pass_rate": 1.0
        }

        recommended = recommend_stage(metrics)

        assert recommended == GMPStage.STRICT

    def test_recommend_highest_stage_qualified(self):
        """Test recommendation picks highest qualified stage"""
        # Metrics that qualify for multiple stages
        metrics = {
            "test_coverage": 95,  # Qualifies for all stages
            "test_pass_rate": 0.96  # Qualifies up to stabilize
        }

        recommended = recommend_stage(metrics)

        # Should recommend stabilize (highest qualified)
        assert recommended == GMPStage.STABILIZE


# ============================================================================
# COMPLIANCE ERROR TESTS
# ============================================================================

class TestComplianceError:
    """Test suite for compliance error handling"""

    def test_validate_and_raise_success(self):
        """Test validate_and_raise doesn't raise on success"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 70,
            "test_pass_rate": 0.85
        }

        # Should not raise
        report = validator.validate_and_raise(metrics)
        assert report.compliant is True

    def test_validate_and_raise_strict_failure(self):
        """Test validate_and_raise raises on strict mode failure"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.STRICT)

        metrics = {
            "test_coverage": 50,
            "test_pass_rate": 0.70
        }

        with pytest.raises(GMPComplianceError) as exc_info:
            validator.validate_and_raise(metrics)

        assert exc_info.value.report.compliant is False

    def test_validate_and_raise_warn_no_exception(self):
        """Test validate_and_raise doesn't raise in warn mode"""
        validator = GMPValidator(stage=GMPStage.BOOTSTRAP, mode=GMPMode.WARN)

        metrics = {
            "test_coverage": 50,
            "test_pass_rate": 0.70
        }

        # Should not raise in warn mode
        report = validator.validate_and_raise(metrics)
        assert report.compliant is True


# ============================================================================
# CONVENIENCE FUNCTIONS TESTS
# ============================================================================

class TestConvenienceFunctions:
    """Test suite for convenience functions"""

    def test_validate_gmp_function(self):
        """Test validate_gmp convenience function"""
        metrics = {
            "test_coverage": 70,
            "test_pass_rate": 0.85
        }

        report = validate_gmp(metrics, stage=GMPStage.BOOTSTRAP, mode=GMPMode.STRICT)

        assert report.compliant is True
        assert report.stage == GMPStage.BOOTSTRAP

    def test_validate_gmp_default_parameters(self):
        """Test validate_gmp uses correct defaults"""
        metrics = {
            "test_coverage": 70,
            "test_pass_rate": 0.85
        }

        report = validate_gmp(metrics)

        # Defaults to BOOTSTRAP/WARN
        assert report.stage == GMPStage.BOOTSTRAP
        assert report.mode == GMPMode.WARN


# ============================================================================
# CLI INTEGRATION TESTS
# ============================================================================

class TestCLIIntegration:
    """Test suite for CLI integration"""

    def test_validate_project_gmp_success(self):
        """Test CLI validation success"""
        exit_code = validate_project_gmp(
            test_coverage=70,
            test_pass_rate=0.85,
            stage="bootstrap",
            mode="strict"
        )

        assert exit_code == 0

    def test_validate_project_gmp_failure(self):
        """Test CLI validation failure"""
        exit_code = validate_project_gmp(
            test_coverage=50,
            test_pass_rate=0.70,
            stage="bootstrap",
            mode="strict"
        )

        assert exit_code == 1

    def test_validate_project_gmp_invalid_stage(self):
        """Test CLI with invalid stage"""
        exit_code = validate_project_gmp(
            test_coverage=70,
            test_pass_rate=0.85,
            stage="invalid_stage",
            mode="warn"
        )

        assert exit_code == 1

    def test_validate_project_gmp_warn_mode(self):
        """Test CLI warn mode always succeeds"""
        exit_code = validate_project_gmp(
            test_coverage=50,
            test_pass_rate=0.70,
            stage="bootstrap",
            mode="warn"
        )

        # Warn mode should still succeed
        assert exit_code == 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_progression_through_stages(self):
        """Test project progressing through GMP stages"""
        # Start at bootstrap
        metrics_v1 = {
            "test_coverage": 70,
            "test_pass_rate": 0.85
        }

        stage1 = recommend_stage(metrics_v1)
        assert stage1 in [GMPStage.BOOTSTRAP, GMPStage.GROWTH]

        # Improve to growth
        metrics_v2 = {
            "test_coverage": 85,
            "test_pass_rate": 0.92
        }

        stage2 = recommend_stage(metrics_v2)
        assert stage2 == GMPStage.GROWTH

        # Improve to stabilize
        metrics_v3 = {
            "test_coverage": 92,
            "test_pass_rate": 0.97
        }

        stage3 = recommend_stage(metrics_v3)
        assert stage3 == GMPStage.STABILIZE

    def test_full_validation_workflow(self):
        """Test complete validation workflow"""
        # 1. Check current metrics
        metrics = {
            "test_coverage": 85,
            "test_pass_rate": 0.92,
            "magic_numbers": 3,
            "code_duplication": 0.12,
            "cyclomatic_complexity": 9
        }

        # 2. Recommend stage
        recommended = recommend_stage(metrics)
        assert recommended == GMPStage.GROWTH

        # 3. Validate at recommended stage
        validator = GMPValidator(stage=recommended, mode=GMPMode.STRICT)
        report = validator.validate(metrics)

        # Should pass
        assert report.compliant is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
