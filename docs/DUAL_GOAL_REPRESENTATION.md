-----

# Framework: Dual Goal Representation for Agentic Systems

## 1\. Abstract

This document outlines a framework for hierarchical task decomposition and goal specification in multi-agent systems. It leverages the concept of Dual Goal Representations (DGR), where a goal is defined not by its intrinsic state features, but by a learned embedding that captures its relationship to all other states in a given task space. This provides a robust and abstract method for a primary agent to assign unambiguous, mathematically-grounded objectives to subagents.

## 2\. Core Principle

The framework's foundation is the re-characterization of a goal state `g`. Instead of using the raw state descriptor `g`, we represent it with a learned function, its dual representation `φ(g)`. This function `φ(g)` is an embedding trained to approximate the temporal distance `d*(s, g)`—the optimal cost or steps required to transition from any state `s` to the goal `g`. The representation is "dual" because it defines a point in the task space via a functional relationship over the entire space.

## 3\. Framework Components

  - **Task Space (`M`)**: A conceptual manifold representing all possible states of a given problem domain.
  - **State (`s ∈ S`)**: A specific point on the manifold `M`, representing a concrete configuration of the problem.
  - **Goal (`g ∈ S`)**: A target state within the task space.
  - **Temporal Distance (`d*(s, g)`)**: A scalar cost function defining the optimal path length between `s` and `g`. This can be a measure of time, steps, or accumulated cost. It is the ground-truth signal for learning.
  - **State Encoder (`ψ: S → ℝⁿ`)**: A parameterized function, typically a neural network, that maps a state `s` to an n-dimensional embedding vector.
  - **Goal Encoder (`φ: S → ℝⁿ`)**: A parameterized function that maps a goal state `g` to its n-dimensional dual representation vector.
  - **Policy (`π(a | s, φ_g)`)**: A subagent's policy that produces an action `a`, conditioned on the current state `s` and a goal vector `φ_g`.

## 4\. Operational Phases

### Phase 1: Representation Learning (Offline)

The objective of this phase is to learn the encoders `ψ` and `φ` that effectively model the task space topology.

1.  **Data**: Requires a dataset `D` of trajectories `τ = (s₀, a₀, s₁, ...)` from the task domain. These trajectories do not need to be from an expert policy.
2.  **Signal**: Temporal distances `d*(s, g)` are computed or estimated for pairs of states `(s, g)` sampled from the dataset (e.g., using hindsight relabeling).
3.  **Optimization**: The encoders `ψ` and `φ` are trained to approximate the temporal distance function via an inner product. The optimization objective is to minimize a loss function, such as Mean Squared Error, over the dataset:
    $$\mathcal{L}(\theta_\psi, \theta_\phi) = \mathbb{E}_{(s,g) \sim D} \left[ (d^*(s, g) - \psi(s; \theta_\psi)^\top \phi(g; \theta_\phi))^2 \right]$$
    Upon completion, `φ` can produce a meaningful, abstract representation for any goal.

### Phase 2: Planning and Decomposition (Primary Agent)

The primary agent uses the learned representations for strategic, high-level planning.

1.  **Input**: A high-level task defined by an initial state `s_init` and a final goal `g_final`.
2.  **Planning**: The primary agent leverages the learned distance approximator `d̂(s, g) = ψ(s)ᵀφ(g)` to find an efficient path or sequence of subgoals `{g_sub_1, g_sub_2, ..., g_sub_k}` from `s_init` to `g_final`. This can be achieved via search algorithms (e.g., A\*) operating in the learned latent space.
3.  **Delegation**: For each identified subgoal `g_sub_i`, the primary agent computes its goal vector `φ(g_sub_i)` and transmits this vector to a designated subagent.

### Phase 3: Policy Execution (Subagent)

The subagent executes low-level actions to achieve its assigned abstract goal.

1.  **Input**: The subagent receives a goal vector `φ_g` from the primary agent.
2.  **Execution**: The subagent employs its policy `π(a | s, φ_g)` to select actions. The policy is trained to take actions that are expected to reduce the distance to the (unknown) state `g` corresponding to the vector `φ_g`.
3.  **Termination**: The subagent's task is complete when it reaches a state `s_current` where `d̂(s_current, g)` is minimized (or below a threshold), indicating the subgoal has been achieved.

## 5\. Technical Advantages

  - **Unambiguous Goal Specification**: The goal vector `φ(g)` is a precise mathematical object, removing the ambiguity inherent in natural language or high-level state descriptions.
  - **Generalization to Novel Goals**: The continuous nature of the embedding space allows a primary agent to specify novel goals by interpolating or extrapolating existing goal vectors, without requiring explicit training data for those exact goals.
  - **Modularity and Reusability**: Subagent policies `π(a | s, φ_g)` are decoupled from the specifics of any single task. They are trained to interpret abstract goal vectors, making them reusable components that can be deployed across different high-level objectives.

## 6\. Pseudocode

```python
# Phase 1: Pre-trained encoders are assumed to be loaded
state_encoder: ψ
goal_encoder: φ

class PrimaryAgent:
    def __init__(self, state_encoder, goal_encoder):
        self.ψ = state_encoder
        self.φ = goal_encoder

    def solve(self, s_init, g_final):
        # Use learned distance d(s,g) = ψ(s)ᵀφ(g) to find a path
        subgoal_sequence = self._plan_path(s_init, g_final)
        
        current_state = s_init
        for subgoal in subgoal_sequence:
            subgoal_vector = self.φ.encode(subgoal)
            
            # Delegate to an available subagent
            sub_agent = SubAgent(policy=...)
            execution_result = sub_agent.execute(current_state, subgoal_vector)
            current_state = execution_result.final_state
        return current_state

class SubAgent:
    def __init__(self, policy):
        # Policy π(a | s, φ_g) is conditioned on a state and goal vector
        self.policy = policy

    def execute(self, s_current, φ_g):
        while not self._is_terminated(s_current, φ_g):
            action = self.policy.get_action(s_current, φ_g)
            s_current = self._environment_step(action)
        return ExecutionResult(final_state=s_current)

    def _is_terminated(self, s, φ_g):
        # Termination can be based on a learned value function V(s, φ_g)
        # or reaching a state with a minimal predicted distance.
        pass
```

-----
