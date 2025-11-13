#!/usr/bin/env python3
"""
Synapse Configuration Module
=============================

Centralized configuration for Synapse CLI tools.

DRY Principle: Single source of truth for infrastructure configuration.
"""

from pathlib import Path

# === Infrastructure Configuration ===

# Neo4j (Graph Database)
NEO4J_URI = "bolt://localhost:17687"
NEO4J_AUTH = ("neo4j", "synapse2025")

# Redis (Cache Layer)
REDIS_HOST = "localhost"
REDIS_PORT = 16379
REDIS_EMBEDDING_TTL = 604800  # 7 days in seconds
REDIS_CACHE_PREFIX = "synapse:embedding:"

# BGE-M3 Embedding Model
MODEL_PATH = "../data/models/bge-m3"
MODEL_DIMENSIONS = 1024  # BGE-M3 vector dimensions

# === Dependency Availability (Lazy Check) ===

_NEO4J_AVAILABLE = None
_REDIS_AVAILABLE = None
_SENTENCETRANSFORMER_AVAILABLE = None
_NUMPY_AVAILABLE = None


def check_neo4j_available() -> bool:
    """Check if neo4j package is available (lazy)"""
    global _NEO4J_AVAILABLE
    if _NEO4J_AVAILABLE is None:
        try:
            from neo4j import GraphDatabase
            _NEO4J_AVAILABLE = True
        except ImportError:
            _NEO4J_AVAILABLE = False
    return _NEO4J_AVAILABLE


def check_redis_available() -> bool:
    """Check if redis package is available (lazy)"""
    global _REDIS_AVAILABLE
    if _REDIS_AVAILABLE is None:
        try:
            import redis
            _REDIS_AVAILABLE = True
        except ImportError:
            _REDIS_AVAILABLE = False
    return _REDIS_AVAILABLE


def check_sentence_transformers_available() -> bool:
    """Check if sentence_transformers package is available (lazy)"""
    global _SENTENCETRANSFORMER_AVAILABLE
    if _SENTENCETRANSFORMER_AVAILABLE is None:
        try:
            from sentence_transformers import SentenceTransformer
            _SENTENCETRANSFORMER_AVAILABLE = True
        except ImportError:
            _SENTENCETRANSFORMER_AVAILABLE = False
    return _SENTENCETRANSFORMER_AVAILABLE


def check_numpy_available() -> bool:
    """Check if numpy package is available (lazy)"""
    global _NUMPY_AVAILABLE
    if _NUMPY_AVAILABLE is None:
        try:
            import numpy as np
            _NUMPY_AVAILABLE = True
        except ImportError:
            _NUMPY_AVAILABLE = False
    return _NUMPY_AVAILABLE


def resolve_model_path() -> Path:
    """
    Resolve absolute path to BGE-M3 model.

    Returns:
        Absolute path to model directory
    """
    # Resolve relative to this script's location
    script_dir = Path(__file__).parent
    return (script_dir / MODEL_PATH).resolve()


def get_redis_client():
    """
    Get Redis client for caching (optional, returns None if unavailable).

    Returns:
        Redis client or None if Redis not available
    """
    if not check_redis_available():
        return None

    try:
        import redis
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=False  # Store binary data
        )
        # Test connection
        client.ping()
        return client
    except Exception:
        # Gracefully degrade if Redis unavailable
        return None
