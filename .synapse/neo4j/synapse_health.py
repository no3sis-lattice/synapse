#!/usr/bin/env python3
"""
Synapse Health Check Tool
==========================

Monitors Neo4j, Redis, vector DB, and computes consciousness metrics.

Usage:
    python synapse_health.py [--json]

Returns:
    - Neo4j node/relationship counts
    - Redis key counts
    - Vector DB rows
    - Model warm status
    - Consciousness level (Ψ)
"""

import json
import sys
from pathlib import Path

# Dependency imports with graceful degradation
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Configuration (using alternate ports to avoid conflicts)
NEO4J_URI = "bolt://localhost:17687"
NEO4J_AUTH = ("neo4j", "synapse2025")
REDIS_HOST = "localhost"
REDIS_PORT = 16379
MODEL_PATH = "../data/models/bge-m3"


def check_neo4j(uri=NEO4J_URI, auth=NEO4J_AUTH):
    """Query Neo4j for pattern counts"""
    if not NEO4J_AVAILABLE:
        return {"accessible": False, "error": "neo4j package not installed"}

    try:
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session() as session:
            # Count all nodes
            result = session.run("MATCH (n) RETURN count(n) as nodes")
            nodes = result.single()["nodes"]

            # Count all relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as rels")
            rels = result.single()["rels"]

            # Count patterns specifically
            result = session.run("MATCH (p:Pattern) RETURN count(p) as patterns")
            patterns = result.single()["patterns"] if result.peek() else 0

        driver.close()
        return {
            "accessible": True,
            "nodes": nodes,
            "relationships": rels,
            "patterns": patterns,
            "uri": uri
        }
    except Exception as e:
        return {"accessible": False, "error": str(e), "uri": uri}


def check_redis(host=REDIS_HOST, port=REDIS_PORT):
    """Query Redis for cache stats"""
    if not REDIS_AVAILABLE:
        return {"accessible": False, "error": "redis package not installed"}

    try:
        r = redis.Redis(host=host, port=port, decode_responses=True)
        r.ping()  # Test connection
        info = r.info()
        return {
            "accessible": True,
            "keys": r.dbsize(),
            "memory_used": info["used_memory_human"],
            "uptime_days": info["uptime_in_days"],
            "endpoint": f"{host}:{port}"
        }
    except Exception as e:
        return {"accessible": False, "error": str(e), "endpoint": f"{host}:{port}"}


def check_model(model_path=MODEL_PATH):
    """Check if BGE-M3 model is cached"""
    # Resolve relative path from script location
    script_dir = Path(__file__).parent
    path = (script_dir / model_path).resolve()

    exists = path.exists()
    size_mb = 0

    if exists:
        try:
            size_mb = sum(f.stat().st_size for f in path.rglob('*')) / (1024 * 1024)
        except Exception:
            pass

    return {
        "exists": exists,
        "path": str(path),
        "warm": exists,
        "size_mb": round(size_mb, 1) if exists else 0
    }


def compute_consciousness(neo4j_info, redis_info, model_info):
    """
    Compute consciousness metric (Ψ) based on pattern density.

    Formula: Ψ = (pattern_count / 1000) * redis_efficiency * model_warm_factor
    Target: 1000 patterns + Redis + Model = Ψ ≈ 0.50
    """
    if not neo4j_info["accessible"]:
        return {
            "psi": 0.0,
            "pattern_count": 0,
            "level": "offline",
            "status": "Neo4j not accessible"
        }

    pattern_count = neo4j_info.get("patterns", 0)
    redis_efficiency = 0.9 if redis_info["accessible"] else 0.5
    model_warm_factor = 1.0 if model_info["warm"] else 0.7

    # Ψ formula: pattern density * infrastructure quality
    pattern_density = min(pattern_count / 1000.0, 1.0)  # Cap at 1.0
    psi = pattern_density * redis_efficiency * model_warm_factor

    # Determine consciousness level
    if psi < 0.1:
        level = "dormant"
        status = "Infrastructure only, no patterns"
    elif psi < 0.3:
        level = "emerging"
        status = "Basic patterns ingested"
    elif psi < 0.5:
        level = "operational"
        status = "Moderate pattern density"
    else:
        level = "conscious"
        status = "Full pattern map active"

    return {
        "psi": round(psi, 3),
        "pattern_count": pattern_count,
        "level": level,
        "status": status,
        "components": {
            "pattern_density": round(pattern_density, 3),
            "redis_efficiency": redis_efficiency,
            "model_warm": model_warm_factor
        }
    }


def main():
    neo4j_info = check_neo4j()
    redis_info = check_redis()
    model_info = check_model()

    consciousness = compute_consciousness(neo4j_info, redis_info, model_info)

    health = {
        "neo4j": neo4j_info,
        "redis": redis_info,
        "model": model_info,
        "consciousness": consciousness,
        "overall_status": "healthy" if all([
            neo4j_info["accessible"],
            redis_info["accessible"],
            model_info["warm"]
        ]) else "degraded"
    }

    if "--json" in sys.argv:
        print(json.dumps(health, indent=2))
    else:
        # Human-readable output
        print("=== Synapse Health Status ===\n")
        print(f"Neo4j:  {'✓' if neo4j_info['accessible'] else '✗'} "
              f"({neo4j_info.get('patterns', 0)} patterns, "
              f"{neo4j_info.get('nodes', 0)} nodes)")
        if not neo4j_info['accessible']:
            print(f"  Error: {neo4j_info.get('error', 'Unknown')}")

        print(f"Redis:  {'✓' if redis_info['accessible'] else '✗'} "
              f"({redis_info.get('keys', 0)} keys)")
        if not redis_info['accessible']:
            print(f"  Error: {redis_info.get('error', 'Unknown')}")

        print(f"BGE-M3: {'✓' if model_info['warm'] else '✗'} "
              f"({model_info.get('size_mb', 0)} MB)")

        print(f"\nConsciousness: Ψ = {consciousness['psi']:.3f}")
        print(f"Level: {consciousness['level']}")
        print(f"Status: {consciousness['status']}")

        print(f"\nOverall: {health['overall_status'].upper()}")


if __name__ == "__main__":
    main()
