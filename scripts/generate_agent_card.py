from enum import Enum

class AdaptationHook(str, Enum):
    PLAN_ADVICE = "PLAN_ADVICE"
    INVARIANT_DRIFT = "INVARIANT_DRIFT"
    DIALOGUE_BALANCE = "DIALOGUE_BALANCE"
    ROUTING_TUNING = "ROUTING_TUNING"
    CAPABILITY_RERANK = "CAPABILITY_RERANK"
    RESOURCE_STRAIN = "RESOURCE_STRAIN"
    REFAC_OPPORTUNITY = "REFAC_OPPORTUNITY"

# Minimal dispatch helper (extend with handlers registry if needed)
HANDLERS = {}

def register(hook: AdaptationHook):
    def wrap(fn):
        HANDLERS.setdefault(hook, []).append(fn)
        return fn
    return wrap

def emit(hook: AdaptationHook, payload: dict):
    for fn in HANDLERS.get(hook, []):
        fn(payload)
