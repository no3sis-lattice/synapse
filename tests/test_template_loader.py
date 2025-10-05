#!/usr/bin/env python3
"""
Unit Tests for Template Loader - Phase 1b

Tests coverage:
- Template discovery
- Metadata loading and parsing
- JSON Schema validation
- Custom validation rules
- Template info extraction
- Particle info querying
- Validation modes (STRICT, WARN, DISABLED)
- Error handling for missing/invalid templates
"""

import json
import pytest
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from orchestration.template_loader import (
    TemplateLoader,
    TemplateInfo,
    ValidationResult,
    ValidationMode,
    create_template_loader,
    validate_template_file
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def temp_template_dir(tmp_path):
    """Create temporary template directory with test templates"""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Create valid template
    valid_template = templates_dir / "valid_template"
    valid_template.mkdir()

    valid_metadata = {
        "template": {
            "name": "valid_template",
            "display_name": "Valid Template",
            "version": "1.0.0",
            "description": "A valid test template"
        },
        "orchestrator": {
            "class_name": "TestOrchestrator",
            "module": "lib.test_orchestrator"
        },
        "particles": [
            {
                "name": "particle_1",
                "type": "worker",
                "capabilities": ["read", "write"]
            },
            {
                "name": "particle_2",
                "type": "worker",
                "capabilities": ["compute"]
            }
        ],
        "capabilities": {
            "operations": ["test_op_1", "test_op_2"]
        },
        "deployment": {
            "min_particles": 2,
            "max_particles": 10
        },
        "testing": {
            "test_coverage": {
                "current": 85,
                "target": 85
            }
        },
        "architecture": {
            "type": "dual-tract"
        }
    }

    with open(valid_template / "metadata.json", 'w') as f:
        json.dump(valid_metadata, f, indent=2)

    # Create invalid JSON template
    invalid_json = templates_dir / "invalid_json"
    invalid_json.mkdir()
    with open(invalid_json / "metadata.json", 'w') as f:
        f.write("{ invalid json }")

    # Create template with validation warnings
    warning_template = templates_dir / "warning_template"
    warning_template.mkdir()

    warning_metadata = {
        "template": {
            "name": "warning_template",
            "display_name": "Warning Template",
            "version": "1.0.0",
            "description": "Template with warnings"
        },
        "orchestrator": {
            "class_name": "WarningOrchestrator",
            "module": "lib.warning_orchestrator"
        },
        "particles": [
            {
                "name": "particle_1",
                "type": "worker",
                "capabilities": []
            }
        ],
        "capabilities": {
            "operations": ["warn_op"]
        },
        "deployment": {
            "min_particles": 5,  # More than particle count (1) - should warn
            "max_particles": 10
        },
        "testing": {
            "test_coverage": {
                "current": 50,  # Below target - should warn
                "target": 85
            }
        },
        "architecture": {
            "type": "single-tract"  # Deprecated - should warn
        }
    }

    with open(warning_template / "metadata.json", 'w') as f:
        json.dump(warning_metadata, f, indent=2)

    return templates_dir


@pytest.fixture
def temp_schema_dir(tmp_path):
    """Create temporary schema directory with test schema"""
    schemas_dir = tmp_path / "schemas"
    schemas_dir.mkdir()

    # Minimal JSON Schema for template validation
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["template", "orchestrator", "particles"],
        "properties": {
            "template": {
                "type": "object",
                "required": ["name", "version"],
                "properties": {
                    "name": {"type": "string"},
                    "display_name": {"type": "string"},
                    "version": {"type": "string"},
                    "description": {"type": "string"}
                }
            },
            "orchestrator": {
                "type": "object",
                "required": ["class_name", "module"],
                "properties": {
                    "class_name": {"type": "string"},
                    "module": {"type": "string"}
                }
            },
            "particles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "type"],
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "capabilities": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }
    }

    with open(schemas_dir / "template-v1.json", 'w') as f:
        json.dump(schema, f, indent=2)

    return schemas_dir


# ============================================================================
# TEMPLATE DISCOVERY TESTS
# ============================================================================

class TestTemplateDiscovery:
    """Test suite for template discovery"""

    def test_discover_templates(self, temp_template_dir):
        """Test template discovery finds all valid templates"""
        loader = TemplateLoader(template_dir=temp_template_dir)
        templates = loader.discover_templates()

        # Should find 3 templates (valid_template, invalid_json, warning_template)
        assert len(templates) == 3

        template_names = [t.name for t in templates]
        assert "valid_template" in template_names
        assert "invalid_json" in template_names
        assert "warning_template" in template_names

    def test_discover_empty_directory(self, tmp_path):
        """Test discovery in empty directory"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        loader = TemplateLoader(template_dir=empty_dir)
        templates = loader.discover_templates()

        assert len(templates) == 0

    def test_discover_nonexistent_directory(self, tmp_path):
        """Test discovery with nonexistent directory"""
        nonexistent = tmp_path / "does_not_exist"

        loader = TemplateLoader(template_dir=nonexistent)
        templates = loader.discover_templates()

        assert len(templates) == 0


# ============================================================================
# METADATA LOADING TESTS
# ============================================================================

class TestMetadataLoading:
    """Test suite for metadata loading"""

    def test_load_valid_metadata(self, temp_template_dir):
        """Test loading valid metadata"""
        loader = TemplateLoader(template_dir=temp_template_dir)
        metadata = loader.load_metadata("valid_template")

        assert metadata["template"]["name"] == "valid_template"
        assert metadata["template"]["version"] == "1.0.0"
        assert len(metadata["particles"]) == 2

    def test_load_nonexistent_template(self, temp_template_dir):
        """Test loading nonexistent template raises error"""
        loader = TemplateLoader(template_dir=temp_template_dir)

        with pytest.raises(FileNotFoundError):
            loader.load_metadata("nonexistent_template")

    def test_load_invalid_json(self, temp_template_dir):
        """Test loading invalid JSON raises error"""
        loader = TemplateLoader(template_dir=temp_template_dir)

        with pytest.raises(json.JSONDecodeError):
            loader.load_metadata("invalid_json")


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestValidation:
    """Test suite for template validation"""

    def test_validate_valid_template_strict(self, temp_template_dir):
        """Test validating valid template in strict mode"""
        loader = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.STRICT
        )

        result = loader.validate_template("valid_template")

        assert result.valid is True
        assert len(result.errors) == 0

    def test_validate_template_with_warnings_strict(self, temp_template_dir):
        """Test template with warnings in strict mode"""
        loader = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.STRICT
        )

        result = loader.validate_template("warning_template")

        # Should fail in strict mode due to particle count mismatch
        assert result.valid is False
        assert len(result.errors) > 0
        assert any("Particle count mismatch" in err for err in result.errors)

    def test_validate_template_with_warnings_warn_mode(self, temp_template_dir):
        """Test template with warnings in warn mode"""
        loader = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.WARN
        )

        result = loader.validate_template("warning_template")

        # Should pass in warn mode with warnings
        assert result.valid is True
        assert len(result.warnings) > 0

    def test_validate_disabled_mode(self, temp_template_dir):
        """Test validation in disabled mode"""
        loader = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.DISABLED
        )

        # Even invalid template should pass
        result = loader.validate_template("warning_template")

        assert result.valid is True
        assert any("Validation disabled" in w for w in result.warnings)

    def test_custom_validations(self, temp_template_dir):
        """Test custom validation rules"""
        loader = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.WARN
        )

        result = loader.validate_template("warning_template")

        # Check for specific warnings
        warning_messages = [w for w in result.warnings]

        # Should warn about low test coverage
        assert any("Test coverage below target" in str(w) for w in warning_messages)

        # Should warn about deprecated architecture
        assert any("Single-tract architecture is deprecated" in str(w) for w in warning_messages)


# ============================================================================
# TEMPLATE INFO TESTS
# ============================================================================

class TestTemplateInfo:
    """Test suite for template info extraction"""

    def test_get_template_info(self, temp_template_dir):
        """Test extracting template info"""
        loader = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.WARN
        )

        info = loader.get_template_info("valid_template")

        assert info is not None
        assert info.name == "valid_template"
        assert info.display_name == "Valid Template"
        assert info.version == "1.0.0"
        assert info.description == "A valid test template"
        assert info.orchestrator_class == "TestOrchestrator"
        assert info.orchestrator_module == "lib.test_orchestrator"
        assert info.particle_count == 2
        assert "test_op_1" in info.capabilities
        assert "test_op_2" in info.capabilities

    def test_get_template_info_caching(self, temp_template_dir):
        """Test that template info is cached"""
        loader = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.WARN
        )

        # Load twice
        info1 = loader.get_template_info("valid_template")
        info2 = loader.get_template_info("valid_template")

        # Should be same object (cached)
        assert info1 is info2

    def test_list_templates(self, temp_template_dir):
        """Test listing all templates"""
        loader = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.WARN
        )

        templates = loader.list_templates()

        # Should return valid and warning templates (invalid_json fails)
        assert len(templates) >= 1

        names = [t.name for t in templates]
        assert "valid_template" in names


# ============================================================================
# PARTICLE INFO TESTS
# ============================================================================

class TestParticleInfo:
    """Test suite for particle info extraction"""

    def test_get_particle_info(self, temp_template_dir):
        """Test getting particle info"""
        loader = TemplateLoader(template_dir=temp_template_dir)

        particle = loader.get_particle_info("valid_template", "particle_1")

        assert particle is not None
        assert particle["name"] == "particle_1"
        assert particle["type"] == "worker"
        assert "read" in particle["capabilities"]
        assert "write" in particle["capabilities"]

    def test_get_nonexistent_particle(self, temp_template_dir):
        """Test getting nonexistent particle"""
        loader = TemplateLoader(template_dir=temp_template_dir)

        particle = loader.get_particle_info("valid_template", "nonexistent")

        assert particle is None


# ============================================================================
# CONVENIENCE FUNCTIONS TESTS
# ============================================================================

class TestConvenienceFunctions:
    """Test suite for convenience functions"""

    def test_create_template_loader(self):
        """Test create_template_loader function"""
        loader = create_template_loader(validation_mode=ValidationMode.STRICT)

        assert loader is not None
        assert loader.validation_mode == ValidationMode.STRICT

    def test_validate_template_file(self, temp_template_dir):
        """Test validate_template_file function"""
        metadata_path = temp_template_dir / "valid_template" / "metadata.json"

        result = validate_template_file(metadata_path)

        assert result.valid is True


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test suite for error handling"""

    def test_missing_schema_strict_mode(self, temp_template_dir, tmp_path):
        """Test behavior when schema is missing in strict mode"""
        # Create loader pointing to nonexistent schema
        loader = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.STRICT
        )
        # Override schema to None
        loader.schema = None

        metadata = {"template": {"name": "test"}, "orchestrator": {}, "particles": []}
        result = loader.validate_metadata(metadata, "test")

        # Should fail in strict mode when schema unavailable
        assert result.valid is False
        assert any("JSON Schema not available" in err for err in result.errors)

    def test_missing_schema_warn_mode(self, temp_template_dir):
        """Test behavior when schema is missing in warn mode"""
        loader = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.WARN
        )
        # Override schema to None
        loader.schema = None

        metadata = {"template": {"name": "test"}, "orchestrator": {}, "particles": []}
        result = loader.validate_metadata(metadata, "test")

        # Should pass in warn mode with warning
        assert result.valid is True
        assert any("JSON Schema not available" in w for w in result.warnings)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_full_template_workflow(self, temp_template_dir):
        """Test complete workflow: discover -> load -> validate -> extract info"""
        loader = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.WARN
        )

        # 1. Discover templates
        discovered = loader.discover_templates()
        assert len(discovered) > 0

        # 2. Validate template
        result = loader.validate_template("valid_template")
        assert result.valid is True

        # 3. Get template info
        info = loader.get_template_info("valid_template")
        assert info is not None
        assert info.particle_count == 2

        # 4. Get particle info
        particle = loader.get_particle_info("valid_template", "particle_1")
        assert particle is not None
        assert particle["name"] == "particle_1"

    def test_validation_mode_transitions(self, temp_template_dir):
        """Test switching validation modes"""
        # Start with STRICT
        loader_strict = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.STRICT
        )

        result_strict = loader_strict.validate_template("warning_template")
        assert result_strict.valid is False

        # Switch to WARN
        loader_warn = TemplateLoader(
            template_dir=temp_template_dir,
            validation_mode=ValidationMode.WARN
        )

        result_warn = loader_warn.validate_template("warning_template")
        assert result_warn.valid is True
        assert len(result_warn.warnings) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
