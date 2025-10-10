#!/usr/bin/env python3
"""
Vector Embedding Engine for Synapse System
==========================================

This module handles vector embeddings generation, storage, and similarity search.
Implements a placeholder system that can be upgraded to use sentence-transformers later.

Zone-0 Axiom: Start simple, evolve intelligently.
"""

import os
import json
import sqlite3
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
import redis
from dotenv import load_dotenv

load_dotenv()

class VectorEngine:
    """
    Handles vector embeddings for the Synapse System.
    Currently uses simple TF-IDF-like vectors, can be upgraded to transformer models.
    """

    def __init__(self, synapse_root: Path = None):
        self.synapse_root = synapse_root or Path.home() / ".synapse-system"
        self.sqlite_path = self.synapse_root / "neo4j" / "vector_store.db"
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "simple_tfidf")
        self.embedding_dim = 1024  # BGE-M3 output dimension

        # Simple vocabulary for TF-IDF (placeholder until real embeddings)
        self.vocabulary = {}
        self.idf_scores = {}

        # Redis configuration for query embedding cache
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_password = os.getenv("REDIS_PASSWORD", None)
        self.redis_client = None
        self.embedding_cache_ttl = 604800  # 7 days in seconds
        self.cache_prefix = "synapse:embedding:"

        # Initialize Redis client
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=False  # We store binary data
            )
            self.redis_client.ping()
        except Exception as e:
            print(f"⚠️  Redis not available for embedding cache: {e}")
            self.redis_client = None

        # Initialize transformer model if using BGE-M3
        self.transformer_model = None
        if self.embedding_model.startswith("BAAI/"):
            self._initialize_transformer_model()

    def initialize_vector_store(self):
        """Initialize the vector storage with proper schema"""
        os.makedirs(self.sqlite_path.parent, exist_ok=True)

        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()

        # Enhanced vector metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vector_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                neo4j_node_id TEXT UNIQUE,
                file_path TEXT,
                content_hash TEXT,
                embedding_model TEXT,
                embedding_dim INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Vector storage table (for actual embeddings)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                neo4j_node_id TEXT,
                vector_data BLOB,
                vector_norm REAL,
                FOREIGN KEY (neo4j_node_id) REFERENCES vector_metadata(neo4j_node_id)
            )
        """)

        # Index for fast similarity search
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_node_id ON vectors(neo4j_node_id)
        """)

        conn.commit()
        conn.close()

    def simple_tfidf_embedding(self, text: str) -> np.ndarray:
        """
        Generate simple TF-IDF-like embedding as placeholder.
        This can be replaced with sentence-transformers later.
        """
        # Tokenize and clean text
        words = text.lower().split()
        words = [w.strip('.,!?;:()[]{}') for w in words if len(w) > 2]

        # Build simple vocabulary on the fly
        for word in words:
            if word not in self.vocabulary:
                self.vocabulary[word] = len(self.vocabulary)

        # Create TF vector
        tf_vector = np.zeros(self.embedding_dim)
        word_count = {}

        for word in words:
            word_count[word] = word_count.get(word, 0) + 1

        # Map to fixed-size vector using hash-based indexing
        for word, count in word_count.items():
            # Use hash to map words to vector positions
            word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
            positions = [word_hash % self.embedding_dim,
                        (word_hash // self.embedding_dim) % self.embedding_dim]

            for pos in positions:
                tf_vector[pos] += count / len(words)  # Normalized TF

        # Add some random noise to make vectors more distinctive
        noise = np.random.normal(0, 0.01, self.embedding_dim)
        tf_vector += noise

        # Normalize vector
        norm = np.linalg.norm(tf_vector)
        if norm > 0:
            tf_vector = tf_vector / norm

        return tf_vector

    def _initialize_transformer_model(self):
        """Initialize the sentence-transformers model for BGE-M3"""
        try:
            from sentence_transformers import SentenceTransformer
            import sys

            # Check if model is already cached
            cache_path = Path.home() / ".cache" / "huggingface" / "hub"
            model_exists = any("bge-m3" in str(p) for p in cache_path.glob("*") if cache_path.exists())

            if not model_exists:
                print(f"🔽 Downloading BGE-M3 model (~2.3GB)...")
                print("⏳ This may take several minutes on first run...")

                # Add progress indication for download
                print("📥 Progress: ", end="", flush=True)

                # Create a simple progress indicator
                def progress_callback():
                    print(".", end="", flush=True)

                # Override the download progress (simple dots)
                import threading
                import time
                progress_thread = threading.Thread(target=lambda: [progress_callback() or time.sleep(5) for _ in range(60)])
                progress_thread.daemon = True
                progress_thread.start()
            else:
                print(f"📦 Loading cached BGE-M3 model...", file=sys.stderr)

            self.transformer_model = SentenceTransformer(self.embedding_model)

            if not model_exists:
                print("\n✅ BGE-M3 model downloaded and loaded successfully!", file=sys.stderr)
            else:
                print("✅ BGE-M3 model loaded from cache.", file=sys.stderr)

        except ImportError:
            print("❌ sentence-transformers not installed")
            print("💊 Install with: pip install sentence-transformers")
            self.transformer_model = None
        except Exception as e:
            print(f"❌ Error loading BGE-M3 model: {e}")
            print("💊 Try: pip install --upgrade sentence-transformers")
            self.transformer_model = None

    def transformer_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding using BGE-M3 transformer model.
        """
        if self.transformer_model is None:
            print("Transformer model not loaded. Falling back to TF-IDF.")
            return self.simple_tfidf_embedding(text)

        try:
            # Generate embedding using BGE-M3
            embedding = self.transformer_model.encode(text, convert_to_numpy=True)

            # Ensure it's the expected dimension
            if embedding.shape[0] != self.embedding_dim:
                print(f"Warning: Expected {self.embedding_dim}D, got {embedding.shape[0]}D")

            return embedding.astype(np.float64)
        except Exception as e:
            print(f"Error generating transformer embedding: {e}")
            return self.simple_tfidf_embedding(text)

    def generate_embedding(self, text: str, file_path: str = "") -> np.ndarray:
        """
        Generate embedding for text content.
        Uses BGE-M3 transformer model or falls back to TF-IDF.
        """
        if self.embedding_model == "simple_tfidf":
            return self.simple_tfidf_embedding(text)
        elif self.embedding_model.startswith("BAAI/"):
            return self.transformer_embedding(text)
        else:
            # Fallback to simple method
            return self.simple_tfidf_embedding(text)

    def _get_embedding_cache_key(self, text: str) -> str:
        """Generate cache key for query embedding"""
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"{self.cache_prefix}{self.embedding_model}:{text_hash}"

    def get_cached_embedding(self, text: str) -> Optional[np.ndarray]:
        """Retrieve cached embedding from Redis if available"""
        if not self.redis_client:
            return None

        try:
            cache_key = self._get_embedding_cache_key(text)
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                # Deserialize numpy array from bytes
                return np.frombuffer(cached_data, dtype=np.float64)
        except Exception as e:
            # Silently fail and regenerate if cache is unavailable
            pass

        return None

    def cache_embedding(self, text: str, embedding: np.ndarray):
        """Cache query embedding in Redis with 7-day TTL"""
        if not self.redis_client:
            return

        try:
            cache_key = self._get_embedding_cache_key(text)
            embedding_bytes = embedding.tobytes()
            self.redis_client.setex(cache_key, self.embedding_cache_ttl, embedding_bytes)
        except Exception as e:
            # Silently fail - caching is optimization, not critical
            pass

    def generate_embedding_cached(self, text: str, file_path: str = "") -> np.ndarray:
        """
        Generate embedding with Redis caching layer.

        This is the hot-path optimized version for query embeddings:
        - Check Redis cache first (< 1ms)
        - Generate via BGE-M3 if cache miss (~5-10s)
        - Store result in Redis for future queries

        Args:
            text: Text to embed
            file_path: Optional file path (ignored for query embeddings)

        Returns:
            1024-dimensional embedding vector
        """
        # Try cache first
        cached = self.get_cached_embedding(text)
        if cached is not None:
            return cached

        # Cache miss - generate new embedding
        embedding = self.generate_embedding(text, file_path)

        # Store in cache for next time
        self.cache_embedding(text, embedding)

        return embedding

    def store_embedding(self, neo4j_node_id: str, file_path: str, content_hash: str, embedding: np.ndarray):
        """Store embedding in SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()

        # Update or insert metadata
        cursor.execute("""
            INSERT OR REPLACE INTO vector_metadata
            (neo4j_node_id, file_path, content_hash, embedding_model, embedding_dim, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (neo4j_node_id, file_path, content_hash, self.embedding_model, self.embedding_dim))

        # Store vector
        vector_blob = embedding.tobytes()
        vector_norm = float(np.linalg.norm(embedding))

        cursor.execute("""
            INSERT OR REPLACE INTO vectors
            (neo4j_node_id, vector_data, vector_norm)
            VALUES (?, ?, ?)
        """, (neo4j_node_id, vector_blob, vector_norm))

        conn.commit()
        conn.close()

    def get_embedding(self, neo4j_node_id: str) -> Optional[np.ndarray]:
        """Retrieve embedding for a node"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT vector_data FROM vectors WHERE neo4j_node_id = ?
        """, (neo4j_node_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return np.frombuffer(result[0], dtype=np.float64)
        return None

    def similarity_search(self, query_embedding: np.ndarray, top_k: int = 5, min_similarity: float = 0.1) -> List[Tuple[str, float]]:
        """
        Find similar embeddings using cosine similarity.
        Returns list of (neo4j_node_id, similarity_score) tuples.
        """
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()

        cursor.execute("SELECT neo4j_node_id, vector_data FROM vectors")
        results = []

        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return []

        for row in cursor.fetchall():
            node_id, vector_blob = row
            stored_vector = np.frombuffer(vector_blob, dtype=np.float64)

            # Cosine similarity
            dot_product = np.dot(query_embedding, stored_vector)
            stored_norm = np.linalg.norm(stored_vector)

            if stored_norm > 0:
                similarity = dot_product / (query_norm * stored_norm)
                if similarity >= min_similarity:
                    results.append((node_id, float(similarity)))

        conn.close()

        # Sort by similarity (descending) and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def get_stored_embeddings_count(self) -> int:
        """Get count of stored embeddings"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vectors")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_embedding_stats(self) -> Dict:
        """Get statistics about stored embeddings"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()

        stats = {}

        # Count by model
        cursor.execute("""
            SELECT embedding_model, COUNT(*)
            FROM vector_metadata
            GROUP BY embedding_model
        """)
        stats["by_model"] = dict(cursor.fetchall())

        # Total count
        cursor.execute("SELECT COUNT(*) FROM vectors")
        stats["total_vectors"] = cursor.fetchone()[0]

        # Average vector norm
        cursor.execute("SELECT AVG(vector_norm) FROM vectors")
        avg_norm = cursor.fetchone()[0]
        stats["avg_vector_norm"] = float(avg_norm) if avg_norm else 0.0

        conn.close()
        return stats

    def clear_embeddings(self):
        """Clear all stored embeddings"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM vectors")
        cursor.execute("DELETE FROM vector_metadata")

        conn.commit()
        conn.close()

# Convenience functions
def create_vector_engine() -> VectorEngine:
    """Create and initialize a vector engine"""
    engine = VectorEngine()
    engine.initialize_vector_store()
    return engine

def generate_query_embedding(query: str) -> np.ndarray:
    """Generate embedding for a search query"""
    engine = VectorEngine()
    return engine.generate_embedding(query)

if __name__ == "__main__":
    # Simple CLI for testing
    import sys

    if len(sys.argv) < 2:
        print("Usage: python vector_engine.py <test_text>")
        print("       python vector_engine.py --stats")
        sys.exit(1)

    if sys.argv[1] == "--stats":
        engine = create_vector_engine()
        stats = engine.get_embedding_stats()
        print(json.dumps(stats, indent=2))
    else:
        text = " ".join(sys.argv[1:])
        engine = create_vector_engine()
        embedding = engine.generate_embedding(text)
        print(f"Generated {len(embedding)}-dimensional embedding")
        print(f"Vector norm: {np.linalg.norm(embedding):.4f}")
        print(f"Sample values: {embedding[:5]}")