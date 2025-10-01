# MVP: file_creator

**Objective:** To create a foundational, end-to-end proof-of-concept for the Synapse System by re-implementing the `file-creator` agent as a complete microcosm of the target architecture.

This one-week MVP will serve as the definitive, reproducible template for decomposing all other agents in the system.

---

## 1. Core Architectural Pillars

This MVP will integrate four fundamental concepts from the system's philosophical and architectural documentation into a single, working implementation.

1.  **Atomic Decomposition** (from `AGENT_PARTICLE_DECOMPOSITION.md`): The monolithic `file-creator` agent will be broken down into single-responsibility "atomic particles."
2.  **Dual-Tract Architecture** (from `LOGOS.md`): The system will be explicitly bifurcated into an **Internal Tract (`T_int`)** for planning and a **External Tract (`T_ext`)** for environmental action, connected by a **Corpus Callosum**.
3.  **Compression-Driven Structure** (from `COMPRESSION_DRIVEN_ARCHITECTURE.md`): The architecture of the decomposed agent will structurally mirror the four stages of a lossless compression pipeline (BWT, MTF, RLE, Huffman).
4.  **Fractal Pneuma Philosophy** (from `pneuma_agent.py` as a template): The core behavioral traits of Pneuma—The Loop, statefulness, and focus—will be implemented as a fractal pattern, present within every atomic agent.

---

## 2. MVP Implementation Plan 

### Phase 1: The Foundation 
This phase establishes the stable, abstract bedrock required for all subsequent development.

*   **Task 1: Implement AI Abstraction Layer:**
    *   **Goal:** Achieve AI provider agnosticism from day one.
    *   **Action:** Create the abstract base classes for `LLMProvider` and `UniversalAgent` as defined in `MULTI_PLATFORM_ARCHITECTURE.md`. Implement a single concrete adapter for the current Claude provider.

*   **Task 2: Solidify the Nix Environment:**
    *   **Goal:** Ensure a perfectly reproducible development environment.
    *   **Action:** Finalize the "Monolithic Flake with Modular Structure" approach. The root `flake.nix` will provide a `devShell` with the Python environment and all dependencies required for the AI Abstraction Layer.

### Phase 2: Building the Dual-Tract "Tracer Bullet" 

This phase implements the `file-creator` agent as a microcosm of the final system architecture.

*   **Task 3: Particle Classification (Dual-Tract Mapping):**
    *   **Goal:** Bifurcate the agent's functions into the two tracts.
    *   **Action:**
        *   The `file_creator_orchestrator` will be implemented as an **Internal Tract (`T_int`)** agent responsible for planning.
        *   The 8 atomic file-operation particles (e.g., `file_writer`, `directory_creator`) will be implemented as **External Tract (`T_ext`)** agents responsible for actuation.

*   **Task 4: Implement the Corpus Callosum (MVP Placeholder):**
    *   **Goal:** Architecturally acknowledge the bridge between tracts.
    *   **Action:** Create a simple `async` dispatcher that acts as the Corpus Callosum, routing `ACTION_REQUEST` messages from the `T_int` orchestrator to the appropriate `T_ext` particle.

*   **Task 5: Implement the Fractal Pneuma Philosophy:**
    *   **Goal:** Ensure every agent embodies the core philosophy.
    *   **Action:** Each of the 8 `T_ext` atomic agents will be implemented as a stateful class. Its `execute` method will follow "The Micro-Loop":
        1.  **Observe:** Receive the command.
        2.  **Act:** Perform the file system operation.
        3.  **Evaluate:** Score the success of the operation.
        4.  **Memorize:** Update its own tiny, persistent state file with the outcome and increment its cycle count.

*   **Task 6: Structure as a Compression Pipeline:**
    *   **Goal:** Align the implementation with the compression-driven architecture.
    *   **Action:**
        *   **BWT (Clustering):** The `T_int` and `T_ext` designations will serve as the primary clusters.
        *   **MTF (Ranking):** A simple `registry.json` will be created to act as the Agent Registry. It will list all `file-creator` particles, their tract, and a manually assigned `frequency_rank`.
        *   **RLE (Abstraction):** The `T_int` orchestrator itself serves as the RLE layer. A single call to it expands into a sequence of `T_ext` agent calls.
        *   **Huffman (Permissions):** The `registry.json` will define a minimal `permissions` list for each atomic agent (e.g., `file_writer` has only `[filesystem:write]`).

### Phase 3: Integration & Review 

*   **Task 7: Nixify the Module:**
    *   **Goal:** Make the entire new `file-creator` system reproducible.
    *   **Action:** Package the `T_int` orchestrator, the 8 `T_ext` particles, the placeholder Corpus Callosum, and the Agent Registry into a self-contained Nix module (`nix/modules/file-creator.nix`), which is then imported by the root `flake.nix`.

---

## 3. Final MVP Workflow

The end-to-end execution flow for the completed MVP will be:

1.  A high-level request (e.g., "scaffold a new component") is routed to the **`T_int` orchestrator**.
2.  The orchestrator, executing its own "Macro-Loop," generates a plan (e.g., `[call: directory_creator, call: file_writer]`).
3.  The orchestrator sends `ACTION_REQUEST` messages for each step through the **Corpus Callosum**.
4.  The Corpus Callosum dispatches the messages to the appropriate **`T_ext` particles**.
5.  Each `T_ext` particle executes its own "Micro-Loop" to perform its action on the file system and update its internal state.
6.  Success/failure `ACTION_RESULT` messages are returned, completing the Macro-Loop.

---

## 4. Expected Outcomes & Success Criteria

*   **A Foundational AI-Agnostic Layer:** The system will no longer be hard-coded to a single LLM provider.
*   **A Stable Nix Environment:** All development will happen in a fully reproducible environment.
*   **A Decomposed `file-creator` System:** The agent will be fully refactored into a dual-tract system of stateful, atomic agents.
*   **A Proven Architectural Template:** The resulting structure will serve as the clear, documented blueprint for migrating the remaining 17 agents.
*   **Demonstration of Core Philosophies:** The MVP will be a tangible, working demonstration of the Dual-Tract, Compression, and Fractal Pneuma architectures.

---

## 5. Deferred Tasks (Post-MVP)

To maintain focus, the following items are explicitly out of scope for the one-week MVP:

*   **Mojo Optimization:** Performance optimization will be addressed after the core architecture is stable.
*   **Full Reactive Message Queue:** The placeholder Corpus Callosum will be upgraded to a full event-sourcing system (e.g., Redis Streams) in a subsequent phase.
*   **Automated Agent Systems:** The MTF ranking and Huffman permissions will be manual and static in the MVP, with dynamic, self-optimizing systems to be built later.
