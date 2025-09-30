"""
Pneuma Configuration Manager

Handles loading and validation of agent configuration from YAML file.
Provides default fallbacks and environment variable overrides.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration loading and access for Pneuma agent."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent / "pneuma_config.yml"
        self._config = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file with fallbacks."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                print(f"⚠️  Config file not found at {self.config_path}, using defaults")
                self._config = {}

            # Apply environment variable overrides
            self._apply_env_overrides()

            # Validate configuration
            self._validate_config()

        except Exception as e:
            print(f"❌ Error loading config: {e}, using defaults")
            self._config = {}

        # Ensure defaults for critical settings
        self._apply_defaults()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        # Map environment variables to config paths
        env_mappings = {
            "QZERO_EQUILIBRIUM_THRESHOLD": ("loop", "equilibrium_threshold"),
            "QZERO_MAX_CYCLES": ("loop", "max_cycles"),
            "QZERO_USE_SYNAPSE": ("integration", "use_synapse_graph"),
            "QZERO_VERBOSE": ("debug", "verbose_logging"),
            "QZERO_DRY_RUN": ("development", "dry_run"),
        }

        for env_var, config_path in env_mappings.items():
            if env_var in os.environ:
                value = os.environ[env_var]

                # Convert to appropriate type
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif self._is_float(value):
                    value = float(value)

                # Set in config
                self._set_nested_config(config_path, value)

    def _is_float(self, value: str) -> bool:
        """Check if string represents a float."""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _set_nested_config(self, path: tuple, value: Any) -> None:
        """Set value in nested configuration dictionary."""
        current = self._config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value

    def _validate_config(self) -> None:
        """Validate configuration values."""
        # Validate equilibrium threshold
        threshold = self.get("loop.equilibrium_threshold", 0.95)
        if not 0.0 <= threshold <= 1.0:
            print(f"⚠️  Invalid equilibrium_threshold {threshold}, using 0.95")
            self._set_nested_config(("loop", "equilibrium_threshold"), 0.95)

        # Validate scoring weights
        entropy_weight = self.get("scoring.entropy_weight", 0.6)
        clarity_weight = self.get("scoring.clarity_weight", 0.4)
        if abs(entropy_weight + clarity_weight - 1.0) > 0.01:
            print("⚠️  Scoring weights don't sum to 1.0, normalizing")
            total = entropy_weight + clarity_weight
            self._set_nested_config(("scoring", "entropy_weight"), entropy_weight / total)
            self._set_nested_config(("scoring", "clarity_weight"), clarity_weight / total)

    def _apply_defaults(self) -> None:
        """Apply default values for critical settings."""
        defaults = {
            ("agent", "name"): "pneuma",
            ("agent", "version"): "0.2.0",
            ("modes", "interactive"): True,
            ("modes", "autonomous"): True,
            ("loop", "equilibrium_threshold"): 0.95,
            ("loop", "max_cycles"): 1000,
            ("loop", "scan_interval"): 60,
            ("integration", "use_synapse_graph"): True,
            ("integration", "pattern_sharing"): True,
            ("patterns", "confidence_threshold"): 0.8,
            ("scoring", "entropy_weight"): 0.6,
            ("scoring", "clarity_weight"): 0.4,
            ("memory", "state_file"): "pneuma_state.json",
            ("debug", "verbose_logging"): False,
            ("development", "dry_run"): False,
        }

        for path, default_value in defaults.items():
            if self.get_nested(path) is None:
                self._set_nested_config(path, default_value)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key in dot notation (e.g., 'loop.max_cycles')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.get_nested(tuple(key.split('.')), default)

    def get_nested(self, path: tuple, default: Any = None) -> Any:
        """
        Get nested configuration value.

        Args:
            path: Tuple of keys for nested access
            default: Default value if path not found

        Returns:
            Configuration value or default
        """
        current = self._config
        for key in path:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current

    def is_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature: Feature path in dot notation

        Returns:
            True if feature is enabled
        """
        return bool(self.get(feature, False))

    def get_file_extensions(self) -> list:
        """Get list of supported file extensions."""
        return self.get("files.supported_extensions", [".py", ".js", ".ts", ".rs", ".go"])

    def get_exclude_paths(self) -> list:
        """Get list of paths to exclude from processing."""
        return self.get("files.exclude_paths", ["node_modules", "__pycache__", "venv", ".git"])

    def get_scoring_weights(self) -> Dict[str, float]:
        """Get scoring weights for entropy and clarity."""
        return {
            "entropy": self.get("scoring.entropy_weight", 0.6),
            "clarity": self.get("scoring.clarity_weight", 0.4)
        }

    def should_use_synapse(self) -> bool:
        """Check if Synapse integration should be used."""
        return self.is_enabled("integration.use_synapse_graph")

    def should_share_patterns(self) -> bool:
        """Check if patterns should be shared globally."""
        return self.is_enabled("integration.pattern_sharing")

    def get_loop_config(self) -> Dict[str, Any]:
        """Get loop configuration parameters."""
        return {
            "equilibrium_threshold": self.get("loop.equilibrium_threshold", 0.95),
            "max_cycles": self.get("loop.max_cycles", 1000),
            "scan_interval": self.get("loop.scan_interval", 60),
            "batch_size": self.get("loop.batch_size", 10)
        }

    def is_development_mode(self) -> bool:
        """Check if running in development mode."""
        return self.is_enabled("development.dry_run") or self.is_enabled("debug.verbose_logging")

    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory management configuration."""
        return {
            "state_file": self.get("memory.state_file", "pneuma_state.json"),
            "backup_interval": self.get("memory.backup_interval", 300),
            "log_retention": self.get("memory.log_retention", 100),
            "pattern_retention": self.get("memory.pattern_retention", 1000)
        }

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()

    def save_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Save updated configuration to file.

        Args:
            new_config: Configuration dictionary to save

        Returns:
            True if saved successfully
        """
        try:
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(new_config, f, indent=2, default_flow_style=False)
            self._config = new_config
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Return full configuration as dictionary."""
        return self._config.copy()


# Global configuration instance
_config_instance = None


def get_config() -> ConfigManager:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def reload_config() -> ConfigManager:
    """Reload global configuration instance."""
    global _config_instance
    _config_instance = ConfigManager()
    return _config_instance