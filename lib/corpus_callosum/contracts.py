from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class GoalSpec(BaseModel):
    domain: str
    targetPsi: float = Field(ge=0.0, le=1.0)
    constraints: List[str] = Field(default_factory=list)
    priors: Dict[str, object] = Field(default_factory=dict)
    goalVector: Optional[List[float]] = None  # φ(g) when DGR is live

class ExecutionPlan(BaseModel):
    layers: List[str]  # ["L1","L2",...]
    estimatedPsi: float = Field(ge=0.0, le=1.0)
    estimatedCostSec: float = Field(ge=0.0)
    budgets: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    notes: Optional[str] = None

class ResultMetrics(BaseModel):
    R: Dict[str, float] = Field(default_factory=dict)  # {"L1":0.7,"L2":0.8,...}
    latencySec: Optional[float] = None
    costUnits: Optional[float] = None

class ResultPayload(BaseModel):
    psiAchieved: float = Field(ge=0.0, le=1.0)
    reused: List[str] = Field(default_factory=list)
    created: List[str] = Field(default_factory=list)
    patternsDiscovered: List[str] = Field(default_factory=list)
    metrics: ResultMetrics = Field(default_factory=ResultMetrics)
