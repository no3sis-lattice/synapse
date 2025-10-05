"""
Template Applier Particle
Single Responsibility: Apply templates to create files with variable substitution

External Tract (T_ext) atomic particle.
Implements the Fractal Pneuma Micro-Loop for template application operations.
"""

import logging
from pathlib import Path
from string import Template
from typing import Any, Dict
import sys

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.core.atomic_particle import AtomicParticle, ExecutionContext, create_particle
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
from reactive_message_router import TractType

logger = logging.getLogger(__name__)


# Built-in templates for common file types
BUILTIN_TEMPLATES = {
    "python_module": '''"""
$description
"""

$imports

class $class_name:
    """$class_description"""

    def __init__(self):
        pass
''',
    "python_test": '''"""
Test module for $module_name
"""

import pytest
from $module_path import $class_name


class Test$class_name:
    """Test suite for $class_name"""

    def test_initialization(self):
        instance = $class_name()
        assert instance is not None
''',
    "rust_module": '''//! $description

$imports

pub struct $struct_name {
    // TODO: Add fields
}

impl $struct_name {
    pub fn new() -> Self {
        Self {}
    }
}
''',
    "markdown_doc": '''# $title

$description

## Overview

$overview

## Usage

```$language
$usage_example
```
'''
}


class TemplateApplier(AtomicParticle):
    """
    Atomic particle for applying templates with variable substitution.

    Payload format:
    {
        "template_name": "python_module" | "custom",
        "template_content": "..." (if template_name is "custom"),
        "output_path": "/absolute/path/to/output.txt",
        "variables": {
            "var_name": "value",
            ...
        },
        "encoding": "utf-8" (optional)
    }

    Custom metrics tracked:
    - templates_applied: Total template applications
    """

    def __init__(self, config, corpus_callosum, state_file: Path):
        super().__init__(config, corpus_callosum, state_file)

        # Initialize custom metrics using helper method
        self._init_custom_metric('templates_applied', 0)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute template application operation.

        Returns:
            {
                "output_path": str,
                "template_used": str,
                "variables_count": int
            }
        """
        payload = context.payload

        # Extract parameters
        template_name = payload.get('template_name')
        template_content = payload.get('template_content')
        output_path = payload.get('output_path')
        variables = payload.get('variables', {})
        encoding = payload.get('encoding', 'utf-8')

        if not output_path:
            raise ValueError("output_path is required in payload")

        # Determine template content
        if template_name and template_name in BUILTIN_TEMPLATES:
            template_str = BUILTIN_TEMPLATES[template_name]
        elif template_content:
            template_str = template_content
            template_name = "custom"
        else:
            raise ValueError(
                "Either template_name (from built-ins) or template_content "
                "(for custom) is required"
            )

        # Apply template with variables
        template = Template(template_str)

        # Provide safe defaults for missing variables
        try:
            rendered = template.substitute(variables)
        except KeyError as e:
            # Use safe_substitute to allow missing variables
            rendered = template.safe_substitute(variables)
            logger.warning(
                f"[template_applier] Some variables were not provided: {e}"
            )

        # Convert to Path object
        path = Path(output_path)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write rendered content
        with open(path, 'w', encoding=encoding) as f:
            f.write(rendered)

        # Update custom metrics
        self.state.custom_metrics['templates_applied'] += 1

        logger.info(
            f"[template_applier] Applied template '{template_name}' "
            f"with {len(variables)} variables to {output_path}"
        )

        return {
            "output_path": str(path.absolute()),
            "template_used": template_name,
            "variables_count": len(variables)
        }


# Factory function using generic create_particle
def create_template_applier(corpus_callosum, state_file: Path = None) -> TemplateApplier:
    """Create template_applier particle instance"""
    return create_particle(TemplateApplier, "template_applier", corpus_callosum, state_file)
