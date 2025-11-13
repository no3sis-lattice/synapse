#!/usr/bin/env python3
"""
Synapse Pattern Search Tool
============================

Hybrid search: Graph traversal (Neo4j) + Semantic similarity (BGE-M3).

Algorithm:
1. Compute query embedding (BGE-M3)
2. Query Neo4j for patterns with embeddings
3. Compute cosine similarity
4. Rank by similarity score
5. Return top-k results

Usage:
    python synapse_search.py <query> [max_results] [--json]

Examples:
    python synapse_search.py "error handling patterns" --json
    python synapse_search.py "dependency injection" 5 --json
"""

import json
import sys
import time
from typing import List, Dict, Any, Optional

# Import shared configuration (DRY principle)
from synapse_config import (
    NEO4J_URI, NEO4J_AUTH,
    MODEL_DIMENSIONS,
    REDIS_EMBEDDING_TTL,
    REDIS_CACHE_PREFIX,
    check_neo4j_available,
    check_sentence_transformers_available,
    check_numpy_available,
    resolve_model_path,
    get_redis_client
)

# Global caches (lazy load to save memory)
_model = None
_redis_client = None


def load_model() -> Optional[object]:
    """Lazy load BGE-M3 model (only when needed)"""
    global _model
    if _model is None:
        if not check_sentence_transformers_available():
            return None

        # Import here to avoid slow startup
        from sentence_transformers import SentenceTransformer

        model_path = resolve_model_path()

        if not model_path.exists():
            return None

        try:
            _model = SentenceTransformer(str(model_path))
        except Exception as e:
            print(f"Warning: Failed to load model: {e}", file=sys.stderr)
            return None

    return _model


def compute_embedding(text: str, use_cache: bool = True) -> List[float]:
    """
    Compute BGE-M3 embedding for text (with optional Redis caching).

    Args:
        text: Input text to embed
        use_cache: If True, check Redis cache before computing (default: True)

    Returns:
        1024D vector (BGE-M3 dimensions)
    """
    if not text.strip():
        return [0.0] * MODEL_DIMENSIONS  # Empty vector for empty text

    # Try Redis cache first (if enabled)
    if use_cache:
        cached_embedding = _get_cached_embedding(text)
        if cached_embedding is not None:
            return cached_embedding

    # Compute embedding
    model = load_model()
    if model is None:
        # Fallback: Return zero vector if model unavailable
        return [0.0] * MODEL_DIMENSIONS

    try:
        embedding = model.encode(text, convert_to_numpy=True)
        embedding_list = embedding.tolist()

        # Cache result in Redis (if available)
        if use_cache:
            _cache_embedding(text, embedding_list)

        return embedding_list
    except Exception as e:
        print(f"Warning: Embedding computation failed: {e}", file=sys.stderr)
        return [0.0] * MODEL_DIMENSIONS


def _get_cached_embedding(text: str) -> Optional[List[float]]:
    """Get embedding from Redis cache (returns None if not found)"""
    global _redis_client

    # Lazy initialize Redis client
    if _redis_client is None:
        _redis_client = get_redis_client()

    if _redis_client is None:
        return None

    try:
        import hashlib
        import json

        # Create cache key from text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        cache_key = f"{REDIS_CACHE_PREFIX}{text_hash}"

        # Try to get from cache
        cached_data = _redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

    except Exception:
        pass  # Gracefully degrade if cache fails

    return None


def _cache_embedding(text: str, embedding: List[float]) -> None:
    """Store embedding in Redis cache (silent failure if unavailable)"""
    global _redis_client

    if _redis_client is None:
        return

    try:
        import hashlib
        import json

        # Create cache key from text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        cache_key = f"{REDIS_CACHE_PREFIX}{text_hash}"

        # Store with TTL
        _redis_client.setex(
            cache_key,
            REDIS_EMBEDDING_TTL,
            json.dumps(embedding)
        )

    except Exception:
        pass  # Gracefully degrade if cache fails


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Similarity score in [0, 1] range (0 = orthogonal, 1 = identical)
    """
    if not check_numpy_available():
        # Fallback: Manual dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    # NumPy implementation (faster)
    import numpy as np
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norm_product == 0:
        return 0.0
    return float(np.dot(v1, v2) / norm_product)


def search_patterns(
    query: str,
    max_results: int = 10,
    json_mode: bool = False
) -> Any:
    """
    Search Pattern Map using hybrid approach.

    Algorithm:
    1. Compute query embedding (BGE-M3)
    2. Query Neo4j for all patterns with embeddings
    3. Compute cosine similarity for each pattern
    4. Rank by similarity score (descending)
    5. Return top-k results

    Args:
        query: Search query string
        max_results: Maximum number of results to return
        json_mode: If True, return JSON string; else return dict

    Returns:
        Search results (dict or JSON string)
    """
    start_time = time.time()

    # Handle empty query
    if not query.strip():
        result = {
            "query": query,
            "max_results": max_results,
            "latency_ms": 0,
            "results": []
        }
        return json.dumps(result, indent=2) if json_mode else result

    # Step 1: Compute query embedding
    query_embedding = compute_embedding(query)

    # Step 2: Query Neo4j for all patterns
    if not check_neo4j_available():
        error_result = {
            "query": query,
            "max_results": max_results,
            "latency_ms": int((time.time() - start_time) * 1000),
            "error": "neo4j package not available",
            "results": []
        }
        return json.dumps(error_result, indent=2) if json_mode else error_result

    # Import here to avoid slow startup
    from neo4j import GraphDatabase

    patterns = []
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        try:
            with driver.session() as session:
                # Get all patterns (for now - will optimize later with LIMIT)
                result = session.run("""
                    MATCH (p:Pattern)
                    WHERE p.embedding IS NOT NULL
                    RETURN p.id as id,
                           p.name as name,
                           p.description as description,
                           p.language as language,
                           p.embedding as embedding,
                           p.type as type
                    LIMIT $limit
                """, limit=max_results * 2)  # Fetch 2x for ranking buffer

                for record in result:
                    patterns.append({
                        "id": record["id"],
                        "name": record["name"],
                        "description": record["description"],
                        "language": record["language"],
                        "type": record.get("type", "unknown"),
                        "embedding": record["embedding"]
                    })
        finally:
            driver.close()

    except Exception as e:
        error_result = {
            "query": query,
            "max_results": max_results,
            "latency_ms": int((time.time() - start_time) * 1000),
            "error": f"Neo4j query failed: {str(e)}",
            "results": []
        }
        return json.dumps(error_result, indent=2) if json_mode else error_result

    # Step 3: Compute similarities and rank
    ranked_patterns = []
    for pattern in patterns:
        pattern_embedding = pattern.get("embedding", [])
        if not pattern_embedding:
            continue

        similarity = cosine_similarity(query_embedding, pattern_embedding)

        ranked_patterns.append({
            "id": pattern["id"],
            "name": pattern["name"],
            "description": pattern["description"],
            "language": pattern["language"],
            "type": pattern["type"],
            "similarity": round(similarity, 3)
        })

    # Step 4: Sort by similarity (descending) and limit
    ranked_patterns.sort(key=lambda p: p["similarity"], reverse=True)
    ranked_patterns = ranked_patterns[:max_results]

    # Step 5: Format results
    latency_ms = int((time.time() - start_time) * 1000)

    result = {
        "query": query,
        "max_results": max_results,
        "latency_ms": latency_ms,
        "results": ranked_patterns
    }

    if json_mode:
        return json.dumps(result, indent=2)
    else:
        return result


def print_usage():
    """Print usage information"""
    print("Usage: python synapse_search.py <query> [max_results] [--json]")
    print()
    print("Arguments:")
    print("  query        Search query string (required)")
    print("  max_results  Maximum results to return (default: 10)")
    print("  --json       Output JSON format")
    print()
    print("Examples:")
    print('  python synapse_search.py "error handling" --json')
    print('  python synapse_search.py "dependency injection" 5 --json')


def main():
    # Handle --help flag FIRST (before any imports)
    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        sys.exit(0)

    # Check arguments FIRST (before any imports)
    if len(sys.argv) < 2:
        print("Error: Missing required query argument", file=sys.stderr)
        print()
        print_usage()
        sys.exit(1)

    query = sys.argv[1]

    # Parse max_results (optional positional argument)
    max_results = 10
    json_mode = False

    for i in range(2, len(sys.argv)):
        arg = sys.argv[i]
        if arg == "--json":
            json_mode = True
        elif arg.isdigit():
            max_results = int(arg)

    # Execute search (only NOW do we load heavy dependencies)
    try:
        result = search_patterns(query, max_results, json_mode)

        if json_mode:
            print(result)
        else:
            # Human-readable output
            data = result
            print(f"Query: {data['query']}")
            print(f"Max Results: {data['max_results']}")
            print(f"Latency: {data['latency_ms']}ms")
            print()

            if "error" in data:
                print(f"Error: {data['error']}")
            elif len(data["results"]) == 0:
                print("No patterns found (Pattern Map may be empty)")
            else:
                print(f"Results ({len(data['results'])}):")
                for i, pattern in enumerate(data["results"], 1):
                    print(f"{i}. {pattern['name']} [{pattern['language']}] (similarity: {pattern['similarity']:.3f})")
                    print(f"   {pattern['description']}")

    except Exception as e:
        error = {
            "error": str(e),
            "query": query,
            "results": []
        }
        if json_mode:
            print(json.dumps(error, indent=2))
        else:
            print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
