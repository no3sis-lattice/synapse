"""
Template Loader and Validator

Provides functionality to:
1. Load template metadata from JSON files
2. Validate metadata against JSON Schema
3. List available templates
4. Query template information

Part of Phase 1b: Template System Foundation
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    ValidationError = Exception  # Fallback

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Template discovery paths
DEFAULT_TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"
SCHEMA_DIR = Path(__file__).parent.parent.parent / "schemas"
TEMPLATE_SCHEMA_FILE = SCHEMA_DIR / "template-v1.json"

# Validation modes
class ValidationMode(Enum):
    STRICT = "strict"  # Fail on any validation error
    WARN = "warn"      # Log warnings but continue
    DISABLED = "disabled"  # Skip validation


@dataclass
class TemplateInfo:
    """Template metadata container"""
    name: str
    display_name: str
    version: str
    description: str
    orchestrator_class: str
    orchestrator_module: str
    particle_count: int
    capabilities: List[str]
    metadata_path: Path
    metadata: Dict[str, Any]


@dataclass
class ValidationResult:
    """Template validation result"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Optional[Dict[str, Any]] = None


class TemplateLoader:
    """
    Loads and validates Synapse System templates.

    Responsibilities:
    1. Discover templates in templates/ directory
    2. Load metadata.json files
    3. Validate against JSON Schema
    4. Provide template query interface

    Usage:
        loader = TemplateLoader()
        templates = loader.list_templates()
        info = loader.get_template_info("file_creator")
        result = loader.validate_template("file_creator")
    """

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        validation_mode: ValidationMode = ValidationMode.STRICT
    ):
        """
        Initialize template loader.

        Args:
            template_dir: Directory containing templates (default: ./templates)
            validation_mode: Validation mode (STRICT, WARN, or DISABLED)
        """
        self.template_dir = template_dir or DEFAULT_TEMPLATE_DIR
        self.validation_mode = validation_mode
        self.schema = self._load_schema()
        self._template_cache: Dict[str, TemplateInfo] = {}

        if not JSONSCHEMA_AVAILABLE and validation_mode != ValidationMode.DISABLED:
            logger.warning(
                "jsonschema package not available. Install with: pip install jsonschema"
            )
            logger.warning("Falling back to DISABLED validation mode")
            self.validation_mode = ValidationMode.DISABLED

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """Load JSON Schema for template validation"""
        if not TEMPLATE_SCHEMA_FILE.exists():
            logger.warning(f"Template schema not found at {TEMPLATE_SCHEMA_FILE}")
            return None

        try:
            with open(TEMPLATE_SCHEMA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load template schema: {e}")
            return None

    def discover_templates(self) -> List[Path]:
        """
        Discover all templates in template directory.

        Returns:
            List of paths to template directories containing metadata.json
        """
        if not self.template_dir.exists():
            logger.warning(f"Template directory not found: {self.template_dir}")
            return []

        templates = []
        for item in self.template_dir.iterdir():
            if item.is_dir():
                metadata_file = item / "metadata.json"
                if metadata_file.exists():
                    templates.append(item)

        return templates

    def load_metadata(self, template_name: str) -> Dict[str, Any]:
        """
        Load metadata for a specific template.

        Args:
            template_name: Name of the template

        Returns:
            Metadata dictionary

        Raises:
            FileNotFoundError: If template or metadata not found
            json.JSONDecodeError: If metadata is invalid JSON
        """
        template_path = self.template_dir / template_name
        metadata_file = template_path / "metadata.json"

        if not metadata_file.exists():
            raise FileNotFoundError(
                f"Template metadata not found: {metadata_file}"
            )

        with open(metadata_file, 'r') as f:
            return json.load(f)

    def validate_metadata(
        self,
        metadata: Dict[str, Any],
        template_name: str
    ) -> ValidationResult:
        """
        Validate metadata against JSON Schema.

        Args:
            metadata: Template metadata dictionary
            template_name: Name of template (for error messages)

        Returns:
            ValidationResult with validation status and errors
        """
        errors = []
        warnings = []

        # Check if validation is disabled
        if self.validation_mode == ValidationMode.DISABLED:
            return ValidationResult(
                valid=True,
                errors=[],
                warnings=["Validation disabled"],
                metadata=metadata
            )

        # Check if schema is available
        if not self.schema:
            msg = "JSON Schema not available, cannot validate"
            if self.validation_mode == ValidationMode.STRICT:
                errors.append(msg)
                return ValidationResult(valid=False, errors=errors, warnings=warnings)
            else:
                warnings.append(msg)
                return ValidationResult(valid=True, errors=[], warnings=warnings, metadata=metadata)

        # Validate against schema
        try:
            validate(instance=metadata, schema=self.schema)

            # Additional custom validations
            custom_errors, custom_warnings = self._custom_validations(metadata)
            errors.extend(custom_errors)
            warnings.extend(custom_warnings)

            if errors and self.validation_mode == ValidationMode.STRICT:
                return ValidationResult(valid=False, errors=errors, warnings=warnings)

            return ValidationResult(
                valid=True,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )

        except ValidationError as e:
            error_msg = f"Schema validation failed: {e.message}"
            errors.append(error_msg)

            if self.validation_mode == ValidationMode.STRICT:
                return ValidationResult(valid=False, errors=errors, warnings=warnings)
            else:
                logger.warning(f"Template '{template_name}': {error_msg}")
                return ValidationResult(
                    valid=True,
                    errors=errors,
                    warnings=warnings,
                    metadata=metadata
                )

    def _custom_validations(
        self,
        metadata: Dict[str, Any]
    ) -> tuple[List[str], List[str]]:
        """
        Perform custom validations beyond JSON Schema.

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Check particle count consistency
        declared_count = len(metadata.get('particles', []))
        deployment_min = metadata.get('deployment', {}).get('min_particles', 0)

        if declared_count < deployment_min:
            errors.append(
                f"Particle count mismatch: {declared_count} particles declared "
                f"but min_particles is {deployment_min}"
            )

        # Check if test coverage meets target
        testing = metadata.get('testing', {})
        coverage = testing.get('test_coverage', {})
        current = coverage.get('current', 0)
        target = coverage.get('target', 85)

        if current < target:
            warnings.append(
                f"Test coverage below target: {current}% (target: {target}%)"
            )

        # Check for deprecated patterns
        if metadata.get('architecture', {}).get('type') == 'single-tract':
            warnings.append(
                "Single-tract architecture is deprecated. Consider dual-tract design."
            )

        return errors, warnings

    def validate_template(self, template_name: str) -> ValidationResult:
        """
        Validate a template by name.

        Args:
            template_name: Name of the template to validate

        Returns:
            ValidationResult
        """
        try:
            metadata = self.load_metadata(template_name)
            return self.validate_metadata(metadata, template_name)
        except FileNotFoundError as e:
            return ValidationResult(
                valid=False,
                errors=[str(e)],
                warnings=[]
            )
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                errors=[f"Invalid JSON: {e}"],
                warnings=[]
            )

    def get_template_info(self, template_name: str) -> Optional[TemplateInfo]:
        """
        Get template information.

        Args:
            template_name: Name of the template

        Returns:
            TemplateInfo object or None if template not found
        """
        # Check cache first
        if template_name in self._template_cache:
            return self._template_cache[template_name]

        try:
            metadata = self.load_metadata(template_name)

            # Validate if in strict mode
            if self.validation_mode == ValidationMode.STRICT:
                result = self.validate_metadata(metadata, template_name)
                if not result.valid:
                    logger.error(f"Template '{template_name}' validation failed: {result.errors}")
                    return None

            # Extract key information
            template_meta = metadata.get('template', {})
            orchestrator = metadata.get('orchestrator', {})
            particles = metadata.get('particles', [])
            capabilities = metadata.get('capabilities', {}).get('operations', [])

            info = TemplateInfo(
                name=template_meta.get('name', template_name),
                display_name=template_meta.get('display_name', template_name),
                version=template_meta.get('version', 'unknown'),
                description=template_meta.get('description', ''),
                orchestrator_class=orchestrator.get('class_name', ''),
                orchestrator_module=orchestrator.get('module', ''),
                particle_count=len(particles),
                capabilities=capabilities,
                metadata_path=self.template_dir / template_name / "metadata.json",
                metadata=metadata
            )

            # Cache for future use
            self._template_cache[template_name] = info

            return info

        except Exception as e:
            logger.error(f"Failed to get template info for '{template_name}': {e}")
            return None

    def list_templates(self) -> List[TemplateInfo]:
        """
        List all available templates.

        Returns:
            List of TemplateInfo objects
        """
        templates = []

        for template_path in self.discover_templates():
            template_name = template_path.name
            info = self.get_template_info(template_name)
            if info:
                templates.append(info)

        return templates

    def get_particle_info(
        self,
        template_name: str,
        particle_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific particle in a template.

        Args:
            template_name: Name of the template
            particle_name: Name of the particle

        Returns:
            Particle metadata dictionary or None
        """
        try:
            metadata = self.load_metadata(template_name)
            particles = metadata.get('particles', [])

            for particle in particles:
                if particle.get('name') == particle_name:
                    return particle

            return None

        except Exception as e:
            logger.error(f"Failed to get particle info: {e}")
            return None


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_template_loader(
    validation_mode: ValidationMode = ValidationMode.STRICT
) -> TemplateLoader:
    """
    Create a TemplateLoader instance with default configuration.

    Args:
        validation_mode: Validation mode (default: STRICT)

    Returns:
        Configured TemplateLoader instance
    """
    return TemplateLoader(validation_mode=validation_mode)


def validate_template_file(metadata_path: Path) -> ValidationResult:
    """
    Validate a template metadata file directly.

    Args:
        metadata_path: Path to metadata.json file

    Returns:
        ValidationResult
    """
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        loader = TemplateLoader(validation_mode=ValidationMode.STRICT)
        template_name = metadata_path.parent.name

        return loader.validate_metadata(metadata, template_name)

    except Exception as e:
        return ValidationResult(
            valid=False,
            errors=[f"Failed to load/validate: {e}"],
            warnings=[]
        )
