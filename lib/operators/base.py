from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, runtime_checkable

@dataclass(frozen=True)
class Budget:
    wall_time_sec: float
    cpu_ms: Optional[int] = None
    gpu_ms: Optional[int] = None
    memory_mb: Optional[int] = None

@dataclass
class OpResult:
    output: Any
    metrics: Dict[str, float]  # e.g., {"latency_ms": 42, "R_2": 0.72, "psi": 0.83}
    logs: Optional[str] = None

@runtime_checkable
class Operator(Protocol):
    name: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

    def run(self, input_payload: Any, budget: Budget) -> OpResult: ...

class Registry:
    """Simple in-process operator registry."""
    def __init__(self) -> None:
        self._ops: Dict[str, Operator] = {}

    def register(self, op: Operator) -> None:
        if op.name in self._ops:
            raise ValueError(f"Operator already registered: {op.name}")
        self._ops[op.name] = op

    def get(self, name: str) -> Operator:
        return self._ops[name]

    def list(self) -> Dict[str, Operator]:
        return dict(self._ops)
