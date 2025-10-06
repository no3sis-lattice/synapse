#!/usr/bin/env python3
"""
Prime-branch agent generator (compressed).
Generates next-level children given a registry + taxonomy.
"""
import json, hashlib, sys
from pathlib import Path

PRIMES = [2,3,5,7,11,13,17,19]

# Minimal taxonomy seeds per archetype (extend as needed)
TAXONOMIES = {
    "lang-rust": ["rs01","rs02","rs03","rs04","rs05","rs06","rs07"],
    "cig3-spectral": ["spec01","spec02","spec03","spec04","spec05","spec06","spec07"]
}

def load_registry(path="registry.json"):
    return json.loads(Path(path).read_text())

def blake(s: str) -> str:
    return hashlib.blake2s(s.encode(), digest_size=8).hexdigest()

def next_prime(level: int) -> int:
    # level here = parent level; we pick prime for child expansion (level+1)
    return PRIMES[level] if level < len(PRIMES) else PRIMES[-1]

def pick_taxonomy(archetype: str, count: int):
    base = TAXONOMIES.get(archetype, [])
    if len(base) >= count:
        return base[:count]
    # fallback: generate generic codes
    return base + [f"x{str(i).zfill(2)}" for i in range(1, count - len(base) + 1)]

def generate_children(agent: dict, target_level: int):
    p_level = agent["level"]
    if p_level != target_level - 1:
        return []
    prime = next_prime(p_level)  # branching factor
    arche = agent["archetype"]
    codes = pick_taxonomy(arche, prime)
    children = []
    for idx, code in enumerate(codes, 1):
        cid = f"{agent['id']}-{code}"
        children.append({
            "id": cid,
            "level": target_level,
            "tract": agent["tract"],
            "parent": agent["id"],
            "archetype": f"{arche}-sub",
            "a2a_export": []
        })
    return children

def main():
    if len(sys.argv) < 2:
        print("Usage: generate_agents.py <next_level>")
        sys.exit(1)
    target_level = int(sys.argv[1])
    reg = load_registry()
    existing = reg["agents"]
    new_agents = []
    for a in existing:
        new_agents.extend(generate_children(a, target_level))
    if not new_agents:
        print("No parents found for expansion.")
        return
    reg["agents"].extend(new_agents)
    Path("registry_generated.json").write_text(json.dumps(reg, indent=2))
    sig = blake("|".join(sorted(a["id"] for a in reg["agents"])))
    print(f"Generated {len(new_agents)} agents for level {target_level}. REGISTRY_HASH={sig}")

if __name__ == "__main__":
    main()
