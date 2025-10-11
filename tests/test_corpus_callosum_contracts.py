"""
Test the Corpus Callosum contracts and operator base classes.

This test file validates:
1. JSON Schema is valid and can validate contract payloads
2. Pydantic models work correctly with validation
3. Operator protocol and registry work as expected
"""
import json
import pytest
from pathlib import Path

import jsonschema
from lib.operators.base import Budget, OpResult, Operator, Registry
from lib.corpus_callosum.contracts import GoalSpec, ExecutionPlan, ResultPayload, ResultMetrics


class TestCorpusCallosumSchema:
    """Test JSON Schema validation."""

    def test_schema_is_valid(self):
        """Test that the JSON schema itself is well-formed."""
        schema_path = Path(__file__).parent.parent / "schemas" / "corpus_callosum.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)
        
        # Validate the schema itself
        jsonschema.Draft7Validator.check_schema(schema)

    def test_validator_creation(self):
        """Test that we can create a validator from the schema."""
        schema_path = Path(__file__).parent.parent / "schemas" / "corpus_callosum.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)
        
        validator = jsonschema.Draft7Validator(schema)
        assert validator is not None


class TestPydanticContracts:
    """Test Pydantic models for contract validation."""

    def test_goal_spec_creation(self):
        """Test GoalSpec model creation and validation."""
        goal = GoalSpec(
            domain="web_api.auth",
            targetPsi=0.85,
            constraints=["no_external_deps"],
            priors={"strategy": "oauth2"},
            goalVector=[0.1, 0.2, 0.3]
        )
        assert goal.domain == "web_api.auth"
        assert goal.targetPsi == 0.85
        assert len(goal.constraints) == 1
        assert goal.priors["strategy"] == "oauth2"

    def test_goal_spec_defaults(self):
        """Test GoalSpec with default values."""
        goal = GoalSpec(domain="test", targetPsi=0.5)
        assert goal.constraints == []
        assert goal.priors == {}
        assert goal.goalVector is None

    def test_goal_spec_validation_invalid_psi(self):
        """Test that targetPsi validation works."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            GoalSpec(domain="test", targetPsi=1.5)
        
        with pytest.raises(Exception):
            GoalSpec(domain="test", targetPsi=-0.1)

    def test_execution_plan_creation(self):
        """Test ExecutionPlan model creation."""
        plan = ExecutionPlan(
            layers=["L1", "L2", "L3"],
            estimatedPsi=0.82,
            estimatedCostSec=1.5,
            budgets={"L1": {"wallTimeSec": 0.5, "cpuMs": 100}},
            notes="Test plan"
        )
        assert len(plan.layers) == 3
        assert plan.estimatedPsi == 0.82
        assert plan.notes == "Test plan"

    def test_result_payload_creation(self):
        """Test ResultPayload model creation."""
        metrics = ResultMetrics(
            R={"L1": 0.75, "L2": 0.82},
            latencySec=1.2,
            costUnits=0.05
        )
        result = ResultPayload(
            psiAchieved=0.83,
            reused=["pattern_A"],
            created=["new_abstraction"],
            patternsDiscovered=["repetition"],
            metrics=metrics
        )
        assert result.psiAchieved == 0.83
        assert len(result.reused) == 1
        assert result.metrics.latencySec == 1.2


class TestOperatorBase:
    """Test operator base classes."""

    def test_budget_creation(self):
        """Test Budget dataclass."""
        budget = Budget(wall_time_sec=2.0, cpu_ms=500)
        assert budget.wall_time_sec == 2.0
        assert budget.cpu_ms == 500
        assert budget.gpu_ms is None

    def test_budget_immutable(self):
        """Test that Budget is frozen/immutable."""
        budget = Budget(wall_time_sec=1.0)
        with pytest.raises(Exception):  # FrozenInstanceError
            budget.wall_time_sec = 2.0

    def test_op_result_creation(self):
        """Test OpResult dataclass."""
        result = OpResult(
            output={"status": "success"},
            metrics={"latency_ms": 42, "psi": 0.83}
        )
        assert result.output["status"] == "success"
        assert result.metrics["latency_ms"] == 42
        assert result.logs is None

    def test_operator_protocol(self):
        """Test that a class can conform to Operator protocol."""
        class TestOp:
            name = "TestOp"
            input_schema = {"x": "number"}
            output_schema = {"y": "number"}
            
            def run(self, input_payload, budget):
                return OpResult(
                    output={"y": input_payload["x"] * 2},
                    metrics={"latency_ms": 1}
                )
        
        op = TestOp()
        assert isinstance(op, Operator)
        
        # Test execution
        budget = Budget(wall_time_sec=1.0)
        result = op.run({"x": 5}, budget)
        assert result.output["y"] == 10

    def test_registry_operations(self):
        """Test operator registry."""
        registry = Registry()
        
        class TestOp:
            name = "TestOp"
            input_schema = {}
            output_schema = {}
            def run(self, input_payload, budget):
                return OpResult(output={}, metrics={})
        
        op = TestOp()
        
        # Register
        registry.register(op)
        
        # Retrieve
        retrieved = registry.get("TestOp")
        assert retrieved.name == "TestOp"
        
        # List
        ops = registry.list()
        assert "TestOp" in ops
        
    def test_registry_duplicate_registration(self):
        """Test that duplicate registration raises error."""
        registry = Registry()
        
        class TestOp:
            name = "DuplicateOp"
            input_schema = {}
            output_schema = {}
            def run(self, input_payload, budget):
                return OpResult(output={}, metrics={})
        
        op = TestOp()
        registry.register(op)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(op)


class TestIntegration:
    """Integration tests for the complete contract flow."""

    def test_full_contract_flow(self):
        """Test a complete flow using all contracts."""
        # 1. Create a GoalSpec (from External Tract)
        goal = GoalSpec(
            domain="code_structure.refactor",
            targetPsi=0.9,
            constraints=["preserve_behavior"],
            priors={"pattern": "extract_function"}
        )
        
        # 2. Create an ExecutionPlan (from Corpus Callosum)
        plan = ExecutionPlan(
            layers=["L2", "L3"],
            estimatedPsi=0.88,
            estimatedCostSec=2.5,
            budgets={
                "L2": {"wallTimeSec": 1.0, "cpuMs": 500},
                "L3": {"wallTimeSec": 1.5, "cpuMs": 800}
            }
        )
        
        # 3. Create a ResultPayload (from Internal Tract)
        result = ResultPayload(
            psiAchieved=0.89,
            reused=["function_extractor_pattern"],
            created=["new_module_structure"],
            patternsDiscovered=["common_code_block"],
            metrics=ResultMetrics(
                R={"L2": 0.85, "L3": 0.91},
                latencySec=2.3,
                costUnits=0.05
            )
        )
        
        # Validate all pieces are properly connected
        assert goal.targetPsi <= 1.0
        assert plan.estimatedPsi < goal.targetPsi  # Plan is conservative
        assert result.psiAchieved >= plan.estimatedPsi  # Achieved goal
        assert result.metrics.latencySec <= plan.estimatedCostSec  # Within budget
