#!/usr/bin/env python3
"""
Synapse Context Manager
======================

The central API for intelligent context retrieval from the hybrid Neo4j/Redis system.
Implements the "Search then Traverse" pattern for optimal information synthesis.

Zone-0 Axiom: SoC (Separation of Concerns) - This class handles ONLY context retrieval,
not ingestion or activation.
"""

import os
import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from difflib import SequenceMatcher

import redis
from neo4j import GraphDatabase
from dotenv import load_dotenv
from vector_engine import VectorEngine

load_dotenv()


class QueryProcessor:
    """Handles query preprocessing, expansion, and intent classification"""

    def __init__(self):
        # Programming term synonyms for query expansion
        self.synonyms = {
            "error": ["exception", "bug", "issue", "fault", "failure"],
            "function": ["method", "func", "procedure", "fn", "def"],
            "class": ["struct", "type", "object", "interface"],
            "async": ["concurrent", "parallel", "asynchronous", "await"],
            "test": ["spec", "test_", "_test", "testing", "unittest"],
            "variable": ["var", "let", "const", "field", "property"],
            "loop": ["iterate", "for", "while", "foreach"],
            "condition": ["if", "conditional", "branch", "case"],
            "import": ["include", "require", "use", "from"],
            "config": ["configuration", "settings", "options", "params"]
        }

        # Intent classification patterns
        self.intent_patterns = {
            "implementation": ["how to", "implement", "create", "build", "make", "setup"],
            "debugging": ["error", "bug", "fix", "issue", "problem", "broken", "fail"],
            "explanation": ["what is", "explain", "definition", "meaning", "understand"],
            "testing": ["test", "spec", "testing", "unittest", "coverage", "mock"],
            "optimization": ["optimize", "performance", "speed", "faster", "efficient"],
            "security": ["secure", "auth", "permission", "vulnerability", "safe"]
        }

    def expand_query(self, query: str) -> List[str]:
        """Expand query with synonyms and programming variations"""
        expanded_terms = []
        words = query.lower().split()

        # Add original query
        expanded_terms.append(query.lower())

        # Add synonym expansions
        for word in words:
            if word in self.synonyms:
                for synonym in self.synonyms[word]:
                    # Create variations with the synonym
                    new_query = query.lower().replace(word, synonym)
                    if new_query not in expanded_terms:
                        expanded_terms.append(new_query)

        # Add partial matches (useful for compound terms)
        significant_words = [w for w in words if len(w) > 3]
        expanded_terms.extend(significant_words)

        return list(set(expanded_terms))

    def classify_query_intent(self, query: str) -> str:
        """Detect what the user is looking for"""
        query_lower = query.lower()

        intent_scores = {intent: 0 for intent in self.intent_patterns}

        # Score based on pattern matches
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    intent_scores[intent] += 1

        # Return highest scoring intent, or 'general' if no clear winner
        max_score = max(intent_scores.values())
        if max_score > 0:
            return max(intent_scores.keys(), key=intent_scores.get)
        return "general"

    def fuzzy_match_terms(self, query_term: str, target_text: str, threshold: float = 0.8) -> bool:
        """Handle typos and variations using fuzzy matching"""
        words = target_text.lower().split()
        for word in words:
            similarity = SequenceMatcher(None, query_term.lower(), word).ratio()
            if similarity >= threshold:
                return True
        return False

    def extract_key_terms(self, query: str) -> List[str]:
        """Extract most important terms from query"""
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = [w.strip('.,!?;:()[]{}') for w in query.lower().split()]
        return [w for w in words if len(w) > 2 and w not in stop_words]

class SynapseContextManager:
    """
    Central interface for intelligent context retrieval from the Synapse System.

    Implements hybrid search: Redis cache -> Graph traversal -> Synthesis
    """

    def __init__(self):
        self.synapse_root = Path.home() / ".synapse-system"
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "synapse_neo4j_pass")
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_password = os.getenv("REDIS_PASSWORD", None)

        # Initialize connections
        self.driver = None
        self.redis_client = None
        self.sqlite_path = self.synapse_root / "neo4j" / "vector_store.db"
        self.vector_engine = VectorEngine(self.synapse_root)

        # Cache configuration
        self.cache_ttl = int(os.getenv("SYNAPSE_CACHE_TTL", 3600))  # 1 hour
        self.cache_prefix = "synapse:query:"

        # Initialize query processor
        self.query_processor = QueryProcessor()

    def connect(self) -> bool:
        """Initialize connections to Neo4j and Redis"""
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")

            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=True
            )
            self.redis_client.ping()

            return True

        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def intelligent_search(self, user_query: str, max_results: int = 5, context: Dict = None) -> Dict[str, Any]:
        """
        The core "Search then Traverse" function with enhanced query processing.

        Returns a structured context summary optimized for agent consumption.
        """
        if not self.connect():
            return {"error": "Failed to connect to data stores"}

        # 1. Process and expand the query
        intent = self.query_processor.classify_query_intent(user_query)
        expanded_queries = self.query_processor.expand_query(user_query)
        key_terms = self.query_processor.extract_key_terms(user_query)

        # 2. Build enhanced context
        search_context = context or {}
        search_context["intent"] = intent
        search_context["expanded_queries"] = expanded_queries
        search_context["key_terms"] = key_terms

        # 3. Check Redis Cache First (with context-aware key)
        cache_key = f"{self.cache_prefix}{self._hash_query(user_query, search_context)}"
        cached_result = self.redis_client.get(cache_key)

        if cached_result:
            cached_data = json.loads(cached_result)
            return {
                "source": "cache",
                "query": user_query,
                "intent": intent,
                "context": cached_data,
                "cached_at": "recently"
            }

        # 4. Perform Enhanced Hybrid Search
        relevant_nodes = self._enhanced_hybrid_search(user_query, expanded_queries, key_terms, intent, max_results)

        if not relevant_nodes:
            # Try fuzzy search as fallback
            fuzzy_results = self._fuzzy_fallback_search(user_query, max_results)
            if fuzzy_results:
                relevant_nodes = fuzzy_results
            else:
                return {
                    "source": "search",
                    "query": user_query,
                    "intent": intent,
                    "context": {"message": f"No relevant files found for '{user_query}' (intent: {intent})"},
                    "nodes_found": 0
                }

        # 5. Apply smart scoring
        for node in relevant_nodes:
            node["smart_score"] = self.calculate_smart_score(node, key_terms, intent)

        # Re-sort by smart score
        relevant_nodes.sort(key=lambda x: x.get("smart_score", 0), reverse=True)

        # 6. Enrich with Graph Traversal
        enriched_context = self._enrich_with_graph_data(relevant_nodes)

        # 7. Synthesize Final Context
        final_context = self._synthesize_context(enriched_context, user_query, intent)

        # 8. Cache Result
        self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(final_context))

        return {
            "source": "neo4j",
            "query": user_query,
            "intent": intent,
            "expanded_queries": expanded_queries[:3],  # Show first 3 expansions
            "context": final_context,
            "nodes_found": len(relevant_nodes),
            "cache_key": cache_key
        }

    def _hash_query(self, query: str, context: Dict = None) -> str:
        """Generate a hash for the query to use as cache key"""
        # Include context in cache key for better hits
        factors = [query.lower().strip()]

        if context:
            factors.append(context.get("project_language", ""))
            factors.append(context.get("current_file_type", ""))
            factors.append(context.get("intent", ""))

        return hashlib.md5("::".join(factors).encode()).hexdigest()

    def calculate_smart_score(self, node: Dict, query_terms: List[str], intent: str = "general") -> float:
        """Multi-factor relevance scoring based on various signals"""
        score = node.get("relevance_score", 0.0)

        # File type boost (prioritize code files)
        extension = node.get("extension", "").lower()
        if extension in [".py", ".rs", ".ts", ".go", ".js", ".java", ".cpp", ".c"]:
            score += 0.3
        elif extension in [".md", ".txt", ".rst"]:
            score += 0.1

        # Intent-based scoring adjustments
        if intent == "testing" and any(test_word in node.get("path", "").lower()
                                      for test_word in ["test", "spec", "__test__"]):
            score += 0.4
        elif intent == "debugging" and any(error_word in node.get("summary", "").lower()
                                          for error_word in ["error", "exception", "bug", "fix"]):
            score += 0.3
        elif intent == "implementation" and any(impl_word in node.get("summary", "").lower()
                                              for impl_word in ["implement", "create", "example"]):
            score += 0.3

        # Recency boost (newer files more relevant)
        if "modified_at" in node and node["modified_at"]:
            try:
                if isinstance(node["modified_at"], str):
                    modified_time = datetime.fromisoformat(node["modified_at"].replace('Z', '+00:00'))
                else:
                    modified_time = node["modified_at"]
                days_old = (datetime.now() - modified_time.replace(tzinfo=None)).days
                recency_boost = max(0, 0.2 - (days_old / 365) * 0.2)  # Decay over a year
                score += recency_boost
            except (ValueError, AttributeError):
                pass  # Skip if date parsing fails

        # Exact match bonus
        summary_lower = node.get("summary", "").lower()
        path_lower = node.get("path", "").lower()
        if all(term.lower() in summary_lower for term in query_terms):
            score += 0.5
        elif any(term.lower() in summary_lower for term in query_terms):
            score += 0.2

        # Path relevance (prefer certain directories)
        if any(important_dir in path_lower for important_dir in ["src/", "lib/", "api/", "core/"]):
            score += 0.1

        # Path depth penalty (prefer root-level files)
        depth = path_lower.count("/")
        score -= min(depth * 0.05, 0.3)  # Cap the penalty

        # Size consideration (very small or very large files are less relevant)
        size = node.get("size", 0)
        if 100 < size < 50000:  # Sweet spot for most code files
            score += 0.1
        elif size > 100000:  # Very large files get a penalty
            score -= 0.2

        return max(0, score)  # Ensure non-negative score

    def _enhanced_hybrid_search(self, original_query: str, expanded_queries: List[str],
                               key_terms: List[str], intent: str, max_results: int) -> List[Dict]:
        """
        Enhanced hybrid search using query expansion and intent-aware ranking.

        PERFORMANCE OPTIMIZATION:
        - OLD: 5 sequential embeddings × 10s each = 50s (timeout risk)
        - NEW: 3 batch embeddings × 4s = 12s (4x speedup)
        """
        all_results = []
        seen_paths = set()

        # 1. Batch vector search with query expansion
        # CRITICAL: Reduced from 5→3 variants for safety margin + batch processing
        query_variants = expanded_queries[:3]

        try:
            # BATCH OPTIMIZATION: Generate all embeddings in single call
            # This is 5-10x faster than sequential generation
            query_embeddings = self.vector_engine.generate_embeddings_batch_cached(query_variants)

            # Process each embedding (vector search is fast, parallelization not needed)
            for query_variant, query_embedding in zip(query_variants, query_embeddings):
                try:
                    vector_results = self.vector_engine.similarity_search(query_embedding, max_results)

                    if vector_results:
                        node_ids = [result[0] for result in vector_results]
                        vector_scores = {result[0]: result[1] for result in vector_results}

                        with self.driver.session() as session:
                            for node_id in node_ids:
                                try:
                                    result = session.run(
                                        "MATCH (f:SynapseFile) WHERE elementId(f) = $id RETURN f",
                                        id=node_id
                                    )
                                    record = result.single()
                                    if record:
                                        node = dict(record["f"])
                                        if node.get("path") not in seen_paths:
                                            node["relevance_score"] = vector_scores.get(node_id, 0.0)
                                            node["match_type"] = "vector"
                                            node["query_variant"] = query_variant
                                            all_results.append(node)
                                            seen_paths.add(node.get("path"))
                                except Exception as e:
                                    continue  # Skip problematic nodes

                except Exception as e:
                    print(f"Vector search failed for '{query_variant}': {e}")
                    continue

        except Exception as e:
            print(f"Batch embedding generation failed: {e}")
            # If batch fails entirely, skip vector search and rely on graph search

        # 2. Graph search with intent-aware strategies
        graph_results = self._intent_aware_graph_search(original_query, key_terms, intent, max_results)

        for result in graph_results:
            if result.get("path") not in seen_paths:
                result["match_type"] = "graph"
                all_results.append(result)
                seen_paths.add(result.get("path"))

        return all_results

    def _intent_aware_graph_search(self, query: str, key_terms: List[str],
                                  intent: str, max_results: int) -> List[Dict]:
        """
        Graph search adapted based on query intent
        """
        results = []

        with self.driver.session() as session:
            # Strategy 1: Intent-specific patterns
            if intent == "testing":
                # Prioritize test files
                test_results = session.run("""
                    MATCH (f:SynapseFile)
                    WHERE ANY(term IN $terms WHERE toLower(f.summary) CONTAINS term OR toLower(f.path) CONTAINS term)
                    AND (toLower(f.path) CONTAINS "test" OR toLower(f.name) CONTAINS "test"
                         OR toLower(f.path) CONTAINS "spec" OR f.extension = ".test")
                    RETURN f,
                           size([term IN $terms WHERE toLower(f.summary) CONTAINS term]) +
                           size([term IN $terms WHERE toLower(f.path) CONTAINS term]) as relevance_score
                    ORDER BY relevance_score DESC
                    LIMIT $limit
                """, terms=key_terms, limit=max_results)

                for record in test_results:
                    node = dict(record["f"])
                    node["relevance_score"] = record["relevance_score"] + 0.5  # Test file boost
                    node["match_type"] = "intent_test"
                    results.append(node)

            elif intent == "debugging":
                # Look for error handling patterns
                debug_results = session.run("""
                    MATCH (f:SynapseFile)
                    WHERE ANY(term IN $terms WHERE toLower(f.summary) CONTAINS term)
                    AND (toLower(f.summary) CONTAINS "error" OR toLower(f.summary) CONTAINS "exception"
                         OR toLower(f.summary) CONTAINS "try" OR toLower(f.summary) CONTAINS "catch")
                    RETURN f,
                           size([term IN $terms WHERE toLower(f.summary) CONTAINS term]) as relevance_score
                    ORDER BY relevance_score DESC
                    LIMIT $limit
                """, terms=key_terms, limit=max_results)

                for record in debug_results:
                    node = dict(record["f"])
                    node["relevance_score"] = record["relevance_score"] + 0.3  # Error handling boost
                    node["match_type"] = "intent_debug"
                    results.append(node)

            # Strategy 2: General enhanced search (always run as fallback)
            general_results = session.run("""
                MATCH (f:SynapseFile)
                WHERE ANY(term IN $terms WHERE
                    toLower(f.summary) CONTAINS term OR
                    toLower(f.name) CONTAINS term OR
                    toLower(f.path) CONTAINS term)
                RETURN f,
                       size([term IN $terms WHERE toLower(f.summary) CONTAINS term]) * 3 +
                       size([term IN $terms WHERE toLower(f.name) CONTAINS term]) * 2 +
                       size([term IN $terms WHERE toLower(f.path) CONTAINS term]) as relevance_score
                ORDER BY relevance_score DESC
                LIMIT $limit
            """, terms=key_terms, limit=max_results * 2)  # Get more for diversity

            existing_paths = {r.get("path") for r in results}
            for record in general_results:
                node = dict(record["f"])
                if node.get("path") not in existing_paths:
                    node["relevance_score"] = record["relevance_score"]
                    node["match_type"] = "general"
                    results.append(node)
                    if len(results) >= max_results:
                        break

        return results

    def _fuzzy_fallback_search(self, query: str, max_results: int) -> List[Dict]:
        """
        Fuzzy search fallback for when exact matches fail
        """
        results = []
        query_terms = self.query_processor.extract_key_terms(query)

        with self.driver.session() as session:
            # Get a broader set of files for fuzzy matching
            all_files = session.run("""
                MATCH (f:SynapseFile)
                RETURN f
                LIMIT 500
            """)

            for record in all_files:
                node = dict(record["f"])
                summary = node.get("summary", "")
                path = node.get("path", "")
                name = node.get("name", "")

                # Check fuzzy matches
                fuzzy_score = 0
                for term in query_terms:
                    if self.query_processor.fuzzy_match_terms(term, summary, 0.7):
                        fuzzy_score += 2
                    elif self.query_processor.fuzzy_match_terms(term, name, 0.8):
                        fuzzy_score += 1.5
                    elif self.query_processor.fuzzy_match_terms(term, path, 0.8):
                        fuzzy_score += 1

                if fuzzy_score > 0:
                    node["relevance_score"] = fuzzy_score
                    node["match_type"] = "fuzzy"
                    results.append(node)

        # Sort and limit results
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results[:max_results]

    def _hybrid_search(self, query: str, max_results: int) -> List[Dict]:
        """
        Hybrid search combining vector similarity and graph search.
        Returns nodes ranked by combined relevance score.

        NOTE: This is the legacy single-query hybrid search.
        For multi-variant search, use _enhanced_hybrid_search() which includes batch optimization.
        """
        all_results = []

        # Vector search (single query, uses cache)
        try:
            query_embedding = self.vector_engine.generate_embedding_cached(query)
            vector_results = self.vector_engine.similarity_search(query_embedding, max_results * 2)

            # Get Neo4j nodes for vector matches
            if vector_results:
                node_ids = [result[0] for result in vector_results]
                vector_scores = {result[0]: result[1] for result in vector_results}

                with self.driver.session() as session:
                    # Batch fetch nodes by their IDs
                    placeholders = ", ".join(["$id" + str(i) for i in range(len(node_ids))])
                    params = {f"id{i}": node_id for i, node_id in enumerate(node_ids)}

                    result = session.run(f"""
                        MATCH (f:SynapseFile)
                        WHERE elementId(f) IN [{placeholders}]
                        RETURN f
                    """, **params)

                    for record in result:
                        node = dict(record["f"])
                        node_id = node_ids[0] if len(node_ids) == 1 else None  # Find correct ID
                        # Find the correct node ID by matching
                        for nid in node_ids:
                            # Try to get this node specifically to match
                            node_result = session.run("MATCH (f:SynapseFile) WHERE elementId(f) = $id RETURN f", id=nid)
                            node_record = node_result.single()
                            if node_record and dict(node_record["f"]) == node:
                                node_id = nid
                                break

                        if node_id:
                            node["relevance_score"] = vector_scores.get(node_id, 0.0)
                            node["match_type"] = "vector"
                            all_results.append(node)

        except Exception as e:
            print(f"Vector search failed: {e}")

        # Graph search as fallback/supplement
        graph_results = self._graph_search(query, max_results)

        # Combine results, avoiding duplicates
        existing_paths = {result.get("path") for result in all_results}
        for result in graph_results:
            if result.get("path") not in existing_paths:
                # Boost graph search scores slightly if no vector results
                boost = 0.1 if not all_results else 0.0
                result["relevance_score"] = result.get("relevance_score", 0) + boost
                result["match_type"] = "graph"
                all_results.append(result)

        # Sort by combined relevance score
        all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return all_results[:max_results]

    def _graph_search(self, query: str, max_results: int) -> List[Dict]:
        """
        Search the Neo4j graph for relevant nodes.
        Uses full-text search on summaries and content.
        """
        # Prepare search terms
        search_terms = query.lower().split()

        with self.driver.session() as session:
            # Multi-strategy search
            results = []

            # Strategy 1: Summary contains any search terms
            summary_results = session.run("""
                MATCH (f:SynapseFile)
                WHERE ANY(term IN $terms WHERE toLower(f.summary) CONTAINS term)
                RETURN f,
                       size([term IN $terms WHERE toLower(f.summary) CONTAINS term]) as relevance_score
                ORDER BY relevance_score DESC
                LIMIT $limit
            """, terms=search_terms, limit=max_results)

            for record in summary_results:
                node = dict(record["f"])
                node["relevance_score"] = record["relevance_score"]
                node["match_type"] = "summary"
                results.append(node)

            # Strategy 2: File name or path contains terms (if we have space for more)
            if len(results) < max_results:
                name_results = session.run("""
                    MATCH (f:SynapseFile)
                    WHERE ANY(term IN $terms WHERE
                        toLower(f.name) CONTAINS term OR toLower(f.path) CONTAINS term)
                    AND NOT f.path IN $existing_paths
                    RETURN f,
                           size([term IN $terms WHERE
                               toLower(f.name) CONTAINS term OR toLower(f.path) CONTAINS term]) as relevance_score
                    ORDER BY relevance_score DESC
                    LIMIT $remaining
                """,
                terms=search_terms,
                existing_paths=[r["path"] for r in results],
                remaining=max_results - len(results))

                for record in name_results:
                    node = dict(record["f"])
                    node["relevance_score"] = record["relevance_score"]
                    node["match_type"] = "name"
                    results.append(node)

            return results

    def _enrich_with_graph_data(self, nodes: List[Dict]) -> List[Dict]:
        """
        Enrich the found nodes with their graph relationships.
        This implements the "Traversal" part of "Search then Traverse".
        """
        enriched_nodes = []

        with self.driver.session() as session:
            for node in nodes:
                node_path = node["path"]

                # Get relationships for this node
                relationships = session.run("""
                    MATCH (f:SynapseFile {path: $path})
                    OPTIONAL MATCH (f)-[r1:CONTAINS]->(child)
                    OPTIONAL MATCH (f)-[r2:REFERENCES]->(ref)
                    OPTIONAL MATCH (f)-[r3:SIMILAR_TO]->(similar)
                    OPTIONAL MATCH (parent)-[r4:CONTAINS]->(f)
                    RETURN
                        collect(DISTINCT {type: "contains", target: child.path, name: child.name}) as contains,
                        collect(DISTINCT {type: "references", target: ref.path, name: ref.name}) as references,
                        collect(DISTINCT {type: "similar_to", target: similar.path, name: similar.name}) as similar,
                        collect(DISTINCT {type: "contained_by", target: parent.path, name: parent.name}) as parents
                """, path=node_path)

                rel_data = relationships.single()

                enriched_node = node.copy()
                enriched_node["relationships"] = {
                    "contains": [r for r in rel_data["contains"] if r["target"] is not None],
                    "references": [r for r in rel_data["references"] if r["target"] is not None],
                    "similar_to": [r for r in rel_data["similar"] if r["target"] is not None],
                    "contained_by": [r for r in rel_data["parents"] if r["target"] is not None]
                }

                enriched_nodes.append(enriched_node)

        return enriched_nodes

    def _synthesize_context(self, enriched_nodes: List[Dict], query: str, intent: str = "general") -> Dict[str, Any]:
        """
        Synthesize the enriched graph data into a concise, token-efficient summary.
        This is the final "formatting" step optimized for agent consumption.
        """
        if not enriched_nodes:
            return {"summary": "No relevant content found", "intent": intent}

        # Group nodes by smart score and match type
        high_relevance = [n for n in enriched_nodes if n.get("smart_score", 0) >= 1.0]
        medium_relevance = [n for n in enriched_nodes if 0.5 <= n.get("smart_score", 0) < 1.0]
        low_relevance = [n for n in enriched_nodes if n.get("smart_score", 0) < 0.5]

        synthesis = {
            "intent": intent,
            "query": query,
            "primary_matches": [],
            "secondary_matches": [],
            "related_files": [],
            "key_concepts": [],
            "suggested_actions": [],
            "search_strategy": self._get_search_strategy_summary(enriched_nodes)
        }

        # Process high relevance matches with enhanced metadata
        for node in high_relevance:
            match_entry = {
                "file": node["name"],
                "path": node["path"],
                "summary": node["summary"],
                "type": node.get("type", "unknown"),
                "word_count": node.get("word_count", 0),
                "smart_score": round(node.get("smart_score", 0), 2),
                "match_type": node.get("match_type", "unknown")
            }

            # Add query variant if from vector search
            if node.get("query_variant"):
                match_entry["matched_query"] = node["query_variant"]

            synthesis["primary_matches"].append(match_entry)

        # Process medium relevance matches (condensed)
        for node in medium_relevance:
            synthesis["secondary_matches"].append({
                "file": node["name"],
                "path": node["path"],
                "summary": node["summary"][:100] + "..." if len(node["summary"]) > 100 else node["summary"],
                "smart_score": round(node.get("smart_score", 0), 2),
                "match_type": node.get("match_type", "unknown")
            })

        # Extract related files from relationships
        all_related = set()
        for node in enriched_nodes:
            rels = node.get("relationships", {})
            for rel_type in ["contains", "references", "similar_to", "contained_by"]:
                for rel in rels.get(rel_type, []):
                    if rel["target"]:
                        all_related.add((rel["target"], rel["name"]))

        synthesis["related_files"] = [
            {"path": path, "name": name}
            for path, name in list(all_related)[:5]  # Limit to 5 related files
        ]

        # Extract key concepts with enhanced filtering
        all_content = " ".join([node.get("summary", "") for node in enriched_nodes])
        words = all_content.lower().split()

        # Filter out common programming words and focus on meaningful terms
        stop_words = {"the", "and", "for", "with", "from", "this", "that", "file", "code", "function"}
        word_freq = {}
        for word in words:
            clean_word = word.strip('.,!?;:()[]{}')
            if len(clean_word) > 3 and clean_word not in stop_words:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1

        synthesis["key_concepts"] = [
            word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:8]
        ]

        # Generate intent-aware suggested actions
        synthesis["suggested_actions"] = self._generate_intent_actions(enriched_nodes, intent)

        return synthesis

    def _get_search_strategy_summary(self, nodes: List[Dict]) -> Dict[str, int]:
        """Summarize which search strategies found results"""
        strategy_counts = {}
        for node in nodes:
            match_type = node.get("match_type", "unknown")
            strategy_counts[match_type] = strategy_counts.get(match_type, 0) + 1
        return strategy_counts

    def _generate_intent_actions(self, nodes: List[Dict], intent: str) -> List[str]:
        """Generate intent-aware suggested actions"""
        actions = []
        file_types = set(node.get("type", "unknown") for node in nodes)

        if intent == "implementation":
            if "py" in file_types:
                actions.append("Review Python implementation examples for patterns")
            if "rs" in file_types:
                actions.append("Study Rust code structure for best practices")
            if "md" in file_types:
                actions.append("Check documentation for implementation guides")

        elif intent == "debugging":
            actions.append("Look for error handling patterns in the codebase")
            if "test" in [node.get("match_type") for node in nodes]:
                actions.append("Examine test files for debugging examples")
            actions.append("Check for similar bug fixes in commit history")

        elif intent == "testing":
            actions.append("Review existing test patterns and structures")
            if any("test" in node.get("path", "").lower() for node in nodes):
                actions.append("Use found test files as templates")
            actions.append("Look for test utilities and helper functions")

        elif intent == "optimization":
            actions.append("Analyze performance-critical code sections")
            actions.append("Look for optimization opportunities in hot paths")

        else:  # general
            if "md" in file_types:
                actions.append("Review documentation files for context")
            if "sh" in file_types:
                actions.append("Check shell scripts for automation opportunities")
            if any(ext in file_types for ext in ["py", "rs", "go", "ts"]):
                actions.append("Examine code files for implementation patterns")

        return actions[:4]  # Limit to 4 suggestions

    def check_health(self) -> Dict[str, Any]:
        """Check the health status of all system components"""
        health = {
            "neo4j": {"status": "unknown", "details": ""},
            "redis": {"status": "unknown", "details": ""},
            "files": {"status": "unknown", "count": 0},
            "overall": {"status": "unknown", "last_check": datetime.now().isoformat()}
        }

        # Check Neo4j
        try:
            if not self.driver:
                self.connect()

            with self.driver.session() as session:
                result = session.run("MATCH (f:SynapseFile) RETURN count(f) as file_count")
                file_count = result.single()["file_count"]

                health["neo4j"]["status"] = "healthy"
                health["neo4j"]["details"] = f"{file_count} files indexed"
                health["files"]["count"] = file_count
                health["files"]["status"] = "healthy" if file_count > 0 else "empty"

        except Exception as e:
            health["neo4j"]["status"] = "error"
            health["neo4j"]["details"] = str(e)

        # Check Redis
        try:
            if not self.redis_client:
                self.connect()

            self.redis_client.ping()
            cache_keys = len(self.redis_client.keys(f"{self.cache_prefix}*"))

            health["redis"]["status"] = "healthy"
            health["redis"]["details"] = f"{cache_keys} cached queries"

        except Exception as e:
            health["redis"]["status"] = "error"
            health["redis"]["details"] = str(e)

        # Overall status
        if (health["neo4j"]["status"] == "healthy" and
            health["redis"]["status"] == "healthy" and
            health["files"]["count"] > 0):
            health["overall"]["status"] = "healthy"
        elif health["files"]["count"] == 0:
            health["overall"]["status"] = "empty"
        else:
            health["overall"]["status"] = "degraded"

        return health

    def is_stale(self, max_age_hours: int = 24) -> bool:
        """
        Check if the synapse system data is stale and needs re-ingestion.
        Returns True if data is older than max_age_hours or doesn't exist.
        """
        try:
            if self.redis_client:
                metadata = self.redis_client.get("synapse:ingestion_metadata")
                if metadata:
                    meta_data = json.loads(metadata)
                    last_ingestion = datetime.fromisoformat(meta_data["last_ingestion"])
                    age = datetime.now() - last_ingestion
                    return age > timedelta(hours=max_age_hours)

            # Fallback: check Neo4j metadata
            if self.driver:
                with self.driver.session() as session:
                    result = session.run("""
                        MATCH (meta:SynapseMetadata {type: 'ingestion'})
                        RETURN meta.last_run as last_run
                        ORDER BY meta.last_run DESC
                        LIMIT 1
                    """)

                    record = result.single()
                    if record and record["last_run"]:
                        # Neo4j datetime comparison is complex, so we'll assume recent if exists
                        return False

            # If no metadata found, consider stale
            return True

        except Exception:
            # If any error occurs, consider stale
            return True

    def clear_cache(self) -> int:
        """Clear all cached query results. Returns number of keys deleted."""
        try:
            keys = self.redis_client.keys(f"{self.cache_prefix}*")
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception:
            return 0

    def close(self):
        """Close all connections"""
        if self.driver:
            self.driver.close()
        if self.redis_client:
            self.redis_client.close()

# Convenience functions for external use
def search_synapse(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Convenience function for one-off searches"""
    manager = SynapseContextManager()
    try:
        return manager.intelligent_search(query, max_results)
    finally:
        manager.close()

def check_synapse_health() -> Dict[str, Any]:
    """Convenience function for health checks"""
    manager = SynapseContextManager()
    try:
        return manager.check_health()
    finally:
        manager.close()

def is_synapse_stale() -> bool:
    """Convenience function for staleness checks"""
    manager = SynapseContextManager()
    try:
        return manager.is_stale()
    finally:
        manager.close()

if __name__ == "__main__":
    # Simple CLI interface for testing
    import sys

    if len(sys.argv) < 2:
        print("Usage: python context_manager.py <search_query>")
        print("       python context_manager.py --health")
        print("       python context_manager.py --stale")
        sys.exit(1)

    if sys.argv[1] == "--health":
        health = check_synapse_health()
        print(json.dumps(health, indent=2))
    elif sys.argv[1] == "--stale":
        stale = is_synapse_stale()
        print(f"System is {'stale' if stale else 'fresh'}")
    else:
        query = " ".join(sys.argv[1:])
        result = search_synapse(query)
        print(json.dumps(result, indent=2))