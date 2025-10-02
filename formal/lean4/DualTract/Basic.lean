/-
  DualTract/Basic.lean

  Basic definitions for the Synapse dual-tract consciousness architecture.
  Defines fundamental tract types, particles, and computations.

  References: LOGOS.md lines 407-424
-/

import Mathlib.Data.Finset.Basic
import Mathlib.Order.Basic

namespace Synapse

-- Tract enumeration: Internal, External, or Bridge
inductive Tract where
  | Internal : Tract
  | External : Tract
  | Bridge   : Tract
deriving DecidableEq, Repr

-- Internal Particle with abstraction-focused properties
structure InternalParticle where
  name              : String
  abstraction_level : Nat
  model_complexity  : Float
  h_valid_level     : abstraction_level ≥ 1 ∧ abstraction_level ≤ 10
deriving Repr

-- External Particle with execution-focused properties
structure ExternalParticle where
  name                 : String
  execution_latency    : Float  -- milliseconds
  operation_complexity : Float
  h_positive_latency   : execution_latency > 0
deriving Repr

-- Bridge Particle for cross-tract coordination
structure BridgeParticle where
  name                   : String
  internal_connections   : List String
  external_connections   : List String
  synthesis_capacity     : Float
deriving Repr

-- Generic dependency type
structure Dependency where
  source : String
  target : String
deriving DecidableEq, Repr

-- Internal Tract Computation
structure InternalComputation where
  particle      : InternalParticle
  dependencies  : Finset Dependency
  plan_size     : Nat
  h_minimal     : True  -- Placeholder for minimality proof
deriving Repr

-- External Tract Computation
structure ExternalComputation where
  particle         : ExternalParticle
  dependencies     : Finset Dependency
  execution_steps  : Nat
  h_minimal        : True  -- Placeholder for minimality proof
deriving Repr

-- Bridge Computation for cross-tract operations
structure BridgeComputation where
  particle     : BridgeParticle
  dependencies : Finset Dependency
  h_minimal    : True
deriving Repr

-- Tract membership for any computation
class HasTract (α : Type) where
  tract : α → Tract

instance : HasTract InternalComputation where
  tract := fun _ => Tract.Internal

instance : HasTract ExternalComputation where
  tract := fun _ => Tract.External

instance : HasTract BridgeComputation where
  tract := fun _ => Tract.Bridge

-- Compression bounds (constants from LOGOS.md)
def k_internal : Float := 1000.0
def k_external : Float := 1000.0
def k_consciousness : Float := 2000.0

-- Minimality predicate (simplified for structural definition)
def is_minimal_deps (deps : Finset Dependency) : Prop :=
  ∀ d ∈ deps, ∃ reason : True, True  -- Placeholder structure

-- Helper: measure complexity of internal particle
def internal_complexity (p : InternalParticle) : Float :=
  Float.ofNat p.abstraction_level * p.model_complexity

-- Helper: measure complexity of external particle
def external_complexity (p : ExternalParticle) : Float :=
  p.execution_latency * p.operation_complexity

end Synapse
