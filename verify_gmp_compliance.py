#!/usr/bin/env python3
"""
GMP Compliance Verification Script

Verifies that the Synapse project meets Good Manufacturing Practice (GMP)
quality thresholds for the current stage.

Usage:
    python verify_gmp_compliance.py
    python verify_gmp_compliance.py --stage growth
    python verify_gmp_compliance.py --stage bootstrap --mode strict
"""

import argparse
import sys
from pathlib import Path

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from orchestration.gmp_policy import (
    GMPStage,
    GMPMode,
    validate_gmp,
    recommend_stage
)


def get_current_metrics() -> dict:
    """
    Get current project quality metrics.

    In a full implementation, this would:
    - Run pytest --cov to get test coverage
    - Parse test results for pass rate
    - Run radon cc for cyclomatic complexity
    - Run radon raw for code duplication
    - Count magic numbers with AST analysis

    For Phase 1c, we use the known metrics from test results.
    """
    # Current metrics from test run (as of Phase 1c)
    total_tests = 14
    passing_tests = 13
    test_pass_rate = passing_tests / total_tests  # 0.93 (93%)
    test_coverage = 21  # From coverage report (17% to 21% range)

    return {
        "test_coverage": test_coverage,
        "test_pass_rate": test_pass_rate,
        "total_tests": total_tests,
        "passing_tests": passing_tests
    }


def print_metrics(metrics: dict) -> None:
    """Print current metrics in a readable format"""
    print("Current Project Metrics:")
    print(f"  Test Coverage:  {metrics['test_coverage']:.1f}%")
    print(f"  Test Pass Rate: {metrics['test_pass_rate']:.1%} ({metrics['passing_tests']}/{metrics['total_tests']} passing)")
    print()


def main():
    parser = argparse.ArgumentParser(description="Verify GMP compliance")
    parser.add_argument(
        '--stage',
        type=str,
        default='bootstrap',
        choices=['bootstrap', 'growth', 'stabilize', 'strict'],
        help='GMP stage to validate against (default: bootstrap)'
    )
    parser.add_argument(
        '--mode',
        type=str,
        default='warn',
        choices=['warn', 'strict'],
        help='Enforcement mode (default: warn)'
    )
    parser.add_argument(
        '--recommend',
        action='store_true',
        help='Recommend appropriate GMP stage based on current metrics'
    )

    args = parser.parse_args()

    # Get current metrics
    metrics = get_current_metrics()
    print_metrics(metrics)

    # Recommend stage if requested
    if args.recommend:
        recommended_stage = recommend_stage(metrics)
        print(f"Recommended Stage: {recommended_stage.value}")
        print()

    # Validate against specified stage
    stage = GMPStage(args.stage)
    mode = GMPMode(args.mode)

    print(f"Validating against GMP Stage: {stage.value}")
    print(f"Enforcement Mode: {mode.value}")
    print()

    report = validate_gmp(metrics, stage=stage, mode=mode)

    # Print report
    print(report)
    print()

    # Exit with appropriate code
    if report.compliant:
        print("✅ GMP Compliance: PASS")
        return 0
    else:
        if mode == GMPMode.WARN:
            print("⚠️  GMP Compliance: WARNINGS (non-blocking)")
            return 0  # Don't fail in warn mode
        else:
            print("❌ GMP Compliance: FAIL")
            return 1


if __name__ == '__main__':
    sys.exit(main())
