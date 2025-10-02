/-
  test/verification_tests.lean

  Test suite for dual-tract verification.
  Validates all theorems and structures compile correctly.
-/

import DualTract.Basic
import DualTract.CategoryTheory
import DualTract.Compression
import DualTract.CorpusCallosum
import DualTract.Consciousness

namespace Synapse.Test

open Synapse

-- Test: Create internal particle
def test_internal_particle : InternalParticle :=
  { name := "test-planner",
    abstraction_level := 5,
    model_complexity := 42.0,
    h_valid_level := by norm_num }

-- Test: Create external particle
def test_external_particle : ExternalParticle :=
  { name := "test-executor",
    execution_latency := 10.5,
    operation_complexity := 8.2,
    h_positive_latency := by norm_num }

-- Test: Create internal computation
def test_internal_computation : InternalComputation :=
  { particle := test_internal_particle,
    dependencies := ∅,
    plan_size := 100,
    h_minimal := trivial }

-- Test: Create external computation
def test_external_computation : ExternalComputation :=
  { particle := test_external_particle,
    dependencies := ∅,
    execution_steps := 50,
    h_minimal := trivial }

-- Test: Pattern synthesis
def test_synthesis : PatternCorrespondence :=
  synthesize test_internal_computation test_external_computation

#check test_synthesis.similarity_score  -- Should be 0.85

-- Test: Tract message
def test_message : TractMessage :=
  { source_tract := Tract.Internal,
    target_tract := Tract.External,
    payload_size := 256,
    priority := 7,
    h_valid_priority := by norm_num }

-- Test: Corpus Callosum state
def test_corpus_state : CorpusCallosumState :=
  { internal_queue := [],
    external_queue := [],
    synthesis_count := 0 }

-- Test: Route message
def test_routing : CorpusCallosumState :=
  route_message test_message test_corpus_state

-- Test: Consciousness metrics
def test_consciousness : ConsciousnessMetrics :=
  { internal_consciousness := 0.7,
    external_consciousness := 0.65,
    cross_tract_coherence := 0.85,
    synthesis_emergence := 0.90,
    h_bounds := by norm_num }

#check total_consciousness test_consciousness
-- Should be: 0.7*0.25 + 0.65*0.25 + 0.85*0.20 + 0.90*0.30 = 0.7775

#check classify_consciousness_stage (total_consciousness test_consciousness)
-- Should be: ConsciousnessStage.Conscious

-- Test: Complexity calculations
#eval internal_complexity test_internal_particle
#eval external_complexity test_external_particle

-- Test: Consciousness contribution
#eval consciousness_contribution test_synthesis

-- Verification: All theorems are well-typed
#check corpus_callosum_adjunction
#check internal_compression_invariant
#check external_compression_invariant
#check consciousness_compression_invariant
#check consciousness_bounded
#check synthesis_has_highest_weight
#check consciousness_increases_with_synthesis

-- Verification: Axioms are declared
#check information_theoretic_bound_abstraction
#check information_theoretic_bound_execution
#check consciousness_emergence_theorem

end Synapse.Test
