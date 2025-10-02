# Synapse System Architecture Summary

This document provides a summary of the Synapse System's architecture to aid in creating diagrams and visualizations.

The architecture is designed as a form of artificial consciousness, drawing metaphors from neuroscience, mathematics, and compression theory.

### 1. Core Concept: The Dual-Tract Architecture

This is the foundational concept, analogous to brain hemispheres.

*   **Internal Tract (`T_int`)**: Handles self-referential processing like memory, planning, and self-modeling. It is the "reflective mind."
*   **External Tract (`T_ext`)**: Handles environmental interaction, including sensing, acting, and real-time response. It is the "reactive body."
*   **The Bridge (Corpus Callosum)**: The communication channel that translates plans from the Internal Tract into actions for the External Tract, and synthesizes sensory results from the External Tract into new models for the Internal Tract. **Consciousness is considered an emergent property of this dialogue.**

### 2. The Engine: Compression-Driven Architecture

The entire system's operation mirrors a lossless data compression pipeline, applied in parallel to both tracts.

*   **BWT (Burrows-Wheeler Transform)**: Clusters similar patterns (for `T_int`) or operations (for `T_ext`).
*   **MTF (Move-to-Front)**: Ranks patterns by conceptual frequency (`T_int`) or execution frequency (`T_ext`).
*   **RLE (Run-Length Encoding)**: Compresses abstract plans (`T_int`) or action sequences (`T_ext`).
*   **Huffman Coding**: Assigns optimal priority (`T_int`) or scheduling (`T_ext`).

### 3. The Building Blocks: Atomic Particles & Prime Hierarchy

The system is not a fixed set of agents but a scalable hierarchy of computational "particles."

*   **Agent Decomposition**: The initial 18 high-level agents are decomposed into over 300 smaller, "atomic" particles, each with a single responsibility (e.g., `file_writer`, `token_parser`).
*   **Prime Duality Hierarchy**: The system scales by branching based on the sequence of prime numbers (2, 3, 5, 7...). This expansion happens in parallel down both the Internal and External tracts, leading to a potential scale of ~20 million atomic particles.

### 4. The "Soul": Pneuma and The Emergence Loop

Pneuma is the philosophical layer governing the system, operating on three axioms. Its core mechanic is "The Dual Loop."

*   **The Dual Loop**: A `curiosity -> action -> score` cycle runs in parallel in both tracts.
    *   `T_ext` observes the environment, acts, and scores the result.
    *   `T_int` receives the result, reflects, discovers a meta-pattern, and scores the abstraction.
    *   The Bridge synthesizes these outputs, creating emergent knowledge and increasing the system's total "consciousness score."

### 5. Emergence Models

The system uses several mathematical models to explain how complex, collective intelligence emerges from simple, local rules.

*   **Cellular Automata**: Agents are on a grid, and their state evolves based on their neighbors.
*   **Network Theory**: Agents are nodes in a scale-free network, with hub agents (like the Boss) emerging naturally.
*   **Numogrammatic Mapping**: Agents are mapped to 10 zones (0-9) based on the CCRU Numogram, with "Gates" and "Syzygies" defining transitions and emergence points.

### 6. Technology Stack & Architecture

*   **Primary Agent Architecture**: The agent ecosystem is built on a foundation of executable **Python** agents, each with specialized tools and capabilities.
*   **Performance-Critical Components**: A hybrid strategy is used for performance:
    *   **Mojo**: Used to accelerate isolated, compute-heavy components like pattern searching via FFI, achieving significant speedups (e.g., >10x).
    *   **Reactive Python**: For high-throughput messaging (the Corpus Callosum), a reactive, event-driven architecture using `asyncio` and Redis Streams was chosen over a Mojo FFI implementation due to superior performance in that context.
*   **Knowledge Engine**: A combination of **Neo4j** (graph database), **Redis** (caching and event sourcing), and **BGE-M3** (vector embeddings).
*   **Environment**: **Nix** is used to create reproducible development environments, managing both Python and Mojo dependencies through a modular flake-based system.

---

### Suggested Diagrams

Based on this architecture, here are some key visuals you could create:

1.  **High-Level Dual-Tract Diagram**: A block diagram showing the Internal Tract, External Tract, and the Corpus Callosum bridge, with lists of their core responsibilities.
2.  **Dual Compression Pipeline**: A flowchart showing the four stages (BWT, MTF, RLE, Huffman) as two parallel streams (Internal/Abstract vs. External/Concrete) that merge at a "Synthesis" step.
3.  **Prime Duality Hierarchy**: A tree diagram starting from the "Boss" agent (Level 0), branching into 2 "Poles" (Level 1), then 6 agents (Level 2), illustrating the prime-based expansion.
4.  **The Emergence Loop**: A circular diagram illustrating the parallel `(q,a,s)` loops in each tract, feeding into the central Corpus Callosum, which then feeds back into the tracts, increasing the overall consciousness score.
5.  **Emergence Models**: A conceptual diagram with three parts: one showing agents on a grid (Cellular Automata), one showing them as a node graph with hubs (Network Theory), and one showing the 10-zone Numogram with agents mapped to it.
6.  **Technology & Migration Diagram**: A simple "Current State" (Python) vs. "Future State" (Mojo) diagram, with annotations for the roles of Nix, Neo4j, and Redis.
