"""
Synapse System Configuration
Centralized configuration for feature flags, Mojo integration, and system settings.
"""

import os
from typing import Dict, Any


# Mojo Feature Flags
# Control which components use Mojo optimization vs Python fallback
MOJO_FEATURES: Dict[str, bool] = {
    # Phase 2: Pattern Search (FFI integration complete!)
    'pattern_search': True,      # Phase 2 Week 3 complete: FFI working, 13.1x speedup via Mojo library

    # Phase 3: Message Router (Corpus Callosum)
    'message_router': False,          # Phase 3: FFI-based (deprecated - 2x slower than Python)
    'message_router_reactive': False, # Phase 3: Reactive architecture (100x better latency, ready for rollout)

    # Future: Vector Engine (Future)
    'vector_engine': False,      # Enable after future phase

    # Future: Full Corpus Callosum (Future)
    'corpus_callosum': False,    # Enable after Phase 3+ validation
}


# Mojo Runtime Configuration
MOJO_CONFIG: Dict[str, Any] = {
    # Minimum required Mojo version
    'min_version': '0.25.7',

    # Force Python fallback (override via environment)
    'force_python': os.getenv('SYNAPSE_FORCE_PYTHON', '0') == '1',

    # Mojo execution timeout (seconds)
    'execution_timeout': 30,

    # Fallback behavior
    'auto_fallback': True,  # Automatically fallback to Python on error

    # Performance monitoring
    'track_metrics': True,  # Track Mojo vs Python performance
    'log_fallbacks': True,  # Log when fallback occurs
}


# Performance Thresholds
PERFORMANCE_THRESHOLDS: Dict[str, float] = {
    # Maximum acceptable fallback rate (percentage)
    'max_fallback_rate': 1.0,  # 1% threshold

    # Maximum acceptable error rate (percentage)
    'max_error_rate': 0.1,  # 0.1% threshold

    # Minimum required speedup to keep Mojo enabled
    'min_speedup': 5.0,  # Must be at least 5x faster than Python

    # Maximum acceptable latency regression (percentage)
    'max_latency_regression': 20.0,  # 20% threshold
}


# Monitoring Configuration
MONITORING_CONFIG: Dict[str, Any] = {
    # Enable/disable monitoring
    'enabled': True,

    # Metrics collection interval (seconds)
    'collection_interval': 60,

    # Metrics retention period (hours)
    'retention_hours': 24,

    # Alert on threshold breach
    'alert_on_threshold': True,
}


# Phase 2 & 3 Rollout Configuration
ROLLOUT_CONFIG: Dict[str, Any] = {
    # Current rollout percentages (0-100)
    'pattern_search_rollout': 10,           # Phase 2 Week 4: 10% rollout, stable
    'message_router_rollout': 0,            # Phase 3: FFI-based (deprecated)
    'message_router_reactive_rollout': 0,   # Phase 3: Reactive architecture (pending rollout)

    # Rollout stages
    'stages': [0, 10, 25, 50, 75, 100],     # Percentage steps (0% = validation only)

    # Time between stages (hours)
    'stage_duration': 48,  # 48 hours per stage for Phase 3

    # Auto-rollback on high error rate
    'auto_rollback': True,

    # Rollback thresholds for reactive router
    'reactive_rollback_thresholds': {
        'max_error_rate': 1.0,        # 1% error rate triggers rollback
        'min_latency_ms': 5.0,        # 5ms max latency target
        'min_emergence_score': 0.5,   # 0.5 consciousness emergence minimum
        'max_message_loss': 100,      # 100 messages max loss
    }
}


def get_mojo_feature_enabled(feature_name: str) -> bool:
    """
    Check if a Mojo feature is enabled.

    Args:
        feature_name: Name of feature (e.g., 'pattern_search')

    Returns:
        True if feature is enabled, False otherwise
    """
    # Check force Python override
    if MOJO_CONFIG['force_python']:
        return False

    # Check feature flag
    return MOJO_FEATURES.get(feature_name, False)


def set_mojo_feature(feature_name: str, enabled: bool) -> None:
    """
    Enable or disable a Mojo feature.

    Args:
        feature_name: Name of feature
        enabled: True to enable, False to disable
    """
    if feature_name in MOJO_FEATURES:
        MOJO_FEATURES[feature_name] = enabled
    else:
        raise ValueError(f"Unknown Mojo feature: {feature_name}")


def get_rollout_percentage(feature_name: str) -> int:
    """
    Get current rollout percentage for a feature.

    Args:
        feature_name: Name of feature

    Returns:
        Rollout percentage (0-100)
    """
    key = f"{feature_name}_rollout"
    return ROLLOUT_CONFIG.get(key, 0)


def is_mojo_available() -> bool:
    """
    Check if Mojo runtime is available.

    Returns:
        True if Mojo is available, False otherwise
    """
    try:
        import subprocess
        result = subprocess.run(
            ['mojo', '--version'],
            capture_output=True,
            timeout=2,
            text=True
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# System-wide configuration
SYSTEM_CONFIG: Dict[str, Any] = {
    # Neo4j connection
    'neo4j_uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    'neo4j_user': os.getenv('NEO4J_USER', 'neo4j'),
    'neo4j_password': os.getenv('NEO4J_PASSWORD', 'password'),

    # Redis connection
    'redis_host': os.getenv('REDIS_HOST', 'localhost'),
    'redis_port': int(os.getenv('REDIS_PORT', '6379')),
    'redis_db': int(os.getenv('REDIS_DB', '0')),

    # BGE-M3 model
    'embedding_model': 'BAAI/bge-m3',
    'embedding_dim': 1024,

    # Logging
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
}


# Pneuma Consciousness Configuration
PNEUMA_CONFIG: Dict[str, Any] = {
    # Consciousness metrics (updated Phase 3)
    'consciousness_level': 0.62,
    'total_patterns': 10,
    'emergence_events': 3,

    # Pattern Map settings
    'pattern_map_path': '.synapse/PATTERN_MAP.json',
    'auto_pattern_discovery': True,

    # Axiom weights
    'bifurcation_weight': 0.4,  # Context density
    'map_weight': 0.3,          # Pattern discovery
    'emergence_weight': 0.3,    # Recursive improvement
}