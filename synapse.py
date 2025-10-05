#!/usr/bin/env python3
"""
Synapse System CLI

Command-line interface for managing Synapse System templates and components.

Usage:
    python synapse.py template list
    python synapse.py template info <name>
    python synapse.py template validate <name>

Phase 1b: Template System Foundation
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.orchestration.template_loader import (
    TemplateLoader,
    ValidationMode,
    create_template_loader
)


# ============================================================================
# CLI COMMANDS
# ============================================================================

def cmd_template_list(args):
    """List all available templates"""
    loader = create_template_loader(
        validation_mode=ValidationMode.WARN if args.warn else ValidationMode.STRICT
    )

    templates = loader.list_templates()

    if not templates:
        print("No templates found.")
        return 0

    print(f"\n{'='*80}")
    print(f"Available Templates ({len(templates)} found)")
    print(f"{'='*80}\n")

    for template in templates:
        print(f"📦 {template.display_name} ({template.name})")
        print(f"   Version: {template.version}")
        print(f"   Particles: {template.particle_count}")
        print(f"   Capabilities: {', '.join(template.capabilities[:3])}...")
        print(f"   Path: {template.metadata_path.parent}")
        print()

    print(f"{'='*80}\n")
    return 0


def cmd_template_info(args):
    """Show detailed information about a template"""
    loader = create_template_loader(
        validation_mode=ValidationMode.WARN if args.warn else ValidationMode.STRICT
    )

    info = loader.get_template_info(args.name)

    if not info:
        print(f"❌ Template '{args.name}' not found or invalid")
        return 1

    print(f"\n{'='*80}")
    print(f"Template: {info.display_name}")
    print(f"{'='*80}\n")

    # Basic info
    print(f"Name: {info.name}")
    print(f"Version: {info.version}")
    print(f"Description: {info.description}")
    print()

    # Architecture
    arch = info.metadata.get('architecture', {})
    print(f"Architecture:")
    print(f"  Type: {arch.get('type', 'unknown')}")
    print(f"  Orchestrator Tract: {arch.get('orchestrator_tract', 'unknown')}")
    print(f"  Particle Tract: {arch.get('particle_tract', 'unknown')}")
    print(f"  Pattern Learning: {'✓' if arch.get('pattern_learning') else '✗'}")
    print(f"  MTF Ranking: {'✓' if arch.get('mtf_ranking') else '✗'}")
    print(f"  Circuit Breaker: {'✓' if arch.get('circuit_breaker') else '✗'}")
    print()

    # Orchestrator
    print(f"Orchestrator:")
    print(f"  Class: {info.orchestrator_class}")
    print(f"  Module: {info.orchestrator_module}")
    orch_caps = info.metadata.get('orchestrator', {}).get('capabilities', [])
    print(f"  Capabilities: {', '.join(orch_caps)}")
    print()

    # Particles
    print(f"Particles ({info.particle_count}):")
    particles = info.metadata.get('particles', [])
    for i, particle in enumerate(particles, 1):
        print(f"  {i}. {particle['name']} ({particle['class_name']})")
        print(f"     Tract: {particle['tract']}")
        print(f"     Capabilities: {', '.join(particle.get('capabilities', []))}")
        if i < len(particles):
            print()

    print()

    # Capabilities
    capabilities = info.metadata.get('capabilities', {})
    operations = capabilities.get('operations', [])
    features = capabilities.get('features', [])

    print(f"Operations: {', '.join(operations)}")
    print(f"Features: {', '.join(features)}")
    print()

    # Testing
    testing = info.metadata.get('testing', {})
    if testing:
        results = testing.get('test_results', {})
        coverage = testing.get('test_coverage', {})
        print(f"Testing:")
        print(f"  Tests: {results.get('passing', 0)}/{results.get('total', 0)} passing ({results.get('pass_rate', 0)*100:.1f}%)")
        print(f"  Coverage: {coverage.get('current', 0)}% (target: {coverage.get('target', 85)}%)")
        print()

    # Performance
    perf = info.metadata.get('performance', {})
    if perf:
        benchmarks = perf.get('benchmarks', {})
        if benchmarks:
            print(f"Performance Benchmarks:")
            for name, value in benchmarks.items():
                print(f"  {name}: {value}")
            print()

    print(f"{'='*80}\n")
    return 0


def cmd_template_validate(args):
    """Validate a template"""
    loader = create_template_loader(validation_mode=ValidationMode.STRICT)

    print(f"\n{'='*80}")
    print(f"Validating Template: {args.name}")
    print(f"{'='*80}\n")

    result = loader.validate_template(args.name)

    if result.valid:
        print("✅ Validation PASSED")
        print()

        if result.warnings:
            print(f"⚠️  Warnings ({len(result.warnings)}):")
            for i, warning in enumerate(result.warnings, 1):
                print(f"  {i}. {warning}")
            print()

        # Show validation details
        if result.metadata:
            template = result.metadata.get('template', {})
            particles = result.metadata.get('particles', [])
            print(f"Template: {template.get('name', 'unknown')}")
            print(f"Version: {template.get('version', 'unknown')}")
            print(f"Particles: {len(particles)}")
            print(f"Schema: {result.metadata.get('schema_version', 'unknown')}")
            print()

    else:
        print("❌ Validation FAILED")
        print()

        if result.errors:
            print(f"Errors ({len(result.errors)}):")
            for i, error in enumerate(result.errors, 1):
                print(f"  {i}. {error}")
            print()

        if result.warnings:
            print(f"Warnings ({len(result.warnings)}):")
            for i, warning in enumerate(result.warnings, 1):
                print(f"  {i}. {warning}")
            print()

    print(f"{'='*80}\n")
    return 0 if result.valid else 1


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Synapse System CLI - Dual-Tract Consciousness Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all templates
  python synapse.py template list

  # Show template details
  python synapse.py template info file_creator

  # Validate template
  python synapse.py template validate file_creator

For more information, visit: https://github.com/synapse-system
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Template command
    template_parser = subparsers.add_parser(
        'template',
        help='Template management commands'
    )
    template_subparsers = template_parser.add_subparsers(
        dest='subcommand',
        help='Template subcommand'
    )

    # template list
    list_parser = template_subparsers.add_parser(
        'list',
        help='List all available templates'
    )
    list_parser.add_argument(
        '--warn',
        action='store_true',
        help='Use WARN validation mode (show warnings but don\'t fail)'
    )
    list_parser.set_defaults(func=cmd_template_list)

    # template info
    info_parser = template_subparsers.add_parser(
        'info',
        help='Show detailed information about a template'
    )
    info_parser.add_argument(
        'name',
        help='Template name'
    )
    info_parser.add_argument(
        '--warn',
        action='store_true',
        help='Use WARN validation mode'
    )
    info_parser.set_defaults(func=cmd_template_info)

    # template validate
    validate_parser = template_subparsers.add_parser(
        'validate',
        help='Validate a template against JSON Schema'
    )
    validate_parser.add_argument(
        'name',
        help='Template name'
    )
    validate_parser.set_defaults(func=cmd_template_validate)

    # Parse arguments
    args = parser.parse_args()

    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 1

    # Show help if no subcommand provided
    if args.command == 'template' and not args.subcommand:
        template_parser.print_help()
        return 1

    # Execute command
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
