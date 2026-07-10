#!/usr/bin/env python3
"""
PROBLEM AUTO-DETECTOR
═══════════════════════════════════════════════════════════════
Teslan Resonant Collector + Russellian Octaves + Ouroboros

Given ANY input:
  1. Decompose → 72-band signature
  2. Russellian: identify octave structure
  3. Teslan: classify wavelength signature  
  4. Route to correct solver + decomposition
  5. Ouroboros converges
"""

import math, random, time, sys, os, copy
import numpy as np

random.seed(42)
np.random.seed(42)

# ═══════════════════════════════════════════════════════════
# 1. UNIVERSAL DECOMPOSER
# ═══════════════════════════════════════════════════════════

def sig(data: bytes) -> list:
    bands = [0.0] * 72
    if not data: return bands
    total = 0.0
    for i, b in enumerate(data):
        w = (b / 255.0) * (1.0 / (1 + (i // 72) * 0.1))
        bands[i % 72] += w
        total += w
    return [b / total for b in bands] if total > 0 else bands

def inharmony(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

# ═══════════════════════════════════════════════════════════
# 2. RUSSELLIAN OCTAVE ANALYSIS
# ═══════════════════════════════════════════════════════════

OCTAVE_NAMES = [
    "Foundation",    # bands 1-9:    physical base
    "Rhythm",        # bands 10-18:  patterns, cycles
    "Heart",         # bands 19-27:  connection, emotion
    "Mind",          # bands 28-36:  cognition, logic
    "Spirit",        # bands 37-45:  transcendence
    "Unity",         # bands 46-54:  integration
    "Creation",      # bands 55-63:  manifestation
    "Infinity",      # bands 64-72:  recursion, meta
]

def russellian_octaves(signal_72: list) -> dict:
    """Map 72-band signal into 8 octaves of 9 bands each."""
    octaves = []
    for i in range(8):
        chunk = signal_72[i*9:(i+1)*9]
        energy = sum(abs(v) for v in chunk)
        dominant_band = i*9 + np.argmax(np.abs(chunk)) + 1 if energy > 0 else 0
        octaves.append({
            'octave': i + 1,
            'name': OCTAVE_NAMES[i],
            'bands': f"{i*9+1}-{(i+1)*9}",
            'energy': round(float(energy), 6),
            'dominant_band': dominant_band,
            'dominant_value': round(float(max(chunk)), 6) if energy > 0 else 0,
        })
    
    # Dominant octave
    dominant = max(octaves, key=lambda o: o['energy'])
    
    return {
        'octaves': octaves,
        'dominant_octave': dominant['name'],
        'dominant_energy': dominant['energy'],
        'structure': _classify_structure(octaves),
    }

def _classify_structure(octaves: list) -> str:
    """Classify the octave energy distribution."""
    energies = [o['energy'] for o in octaves]
    total = sum(energies)
    if total == 0:
        return "null"
    
    max_e = max(energies)
    min_e = min(e for e in energies if e > 0) if any(e > 0 for e in energies) else 0
    mean_e = total / 8
    std_e = np.std(energies)
    
    # Concentration: is energy concentrated in one octave or spread?
    concentration = max_e / mean_e if mean_e > 0 else 0
    
    if concentration > 2.5:
        spread = "focused"
    elif concentration > 1.5:
        spread = "structured"
    else:
        spread = "distributed"
    
    # Gradient: does energy increase or decrease across octaves?
    first_half = sum(energies[:4])
    second_half = sum(energies[4:])
    if second_half > first_half * 1.3:
        gradient = "ascending"
    elif first_half > second_half * 1.3:
        gradient = "descending"
    else:
        gradient = "balanced"
    
    return f"{spread}_{gradient}"

# ═══════════════════════════════════════════════════════════
# 3. TESLAN WAVELENGTH SIGNATURE
# ═══════════════════════════════════════════════════════════

def teslan_signature(signal_72: list) -> dict:
    """Classify wavelength signature without needing graph structure."""
    arr = np.array(signal_72)
    
    if np.max(np.abs(arr)) > 0:
        normalized = arr / np.max(np.abs(arr))
    else:
        normalized = arr
    
    mean_val = float(np.mean(normalized))
    std_val = float(np.std(normalized))
    
    # Spread classification
    if std_val < 0.1:
        spread = "coherent"      # Tightly clustered — ordered problem
    elif std_val < 0.3:
        spread = "resonant"      # Moderate variation — structured
    else:
        spread = "chaotic"       # High variation — complex/irregular
    
    # Energy classification
    if mean_val < 0.3:
        energy = "low"
    elif mean_val < 0.7:
        energy = "medium"
    else:
        energy = "high"
    
    # Harmonic analysis
    if len(arr) >= 3:
        fundamental = abs(arr[1]) if abs(arr[1]) > 1e-10 else 1e-10
        harmonics = 0
        for i in range(2, min(len(arr), 20)):
            val = abs(arr[i])
            if val > 0:
                ratio = val / fundamental
                if abs(ratio - round(ratio)) < 0.15:
                    harmonics += 1
        harmonic_ratio = harmonics / min(len(arr) - 2, 18)
        if harmonic_ratio > 0.5:
            harmony = "harmonic"
        elif harmonic_ratio > 0.2:
            harmony = "partially_harmonic"
        else:
            harmony = "inharmonic"
    else:
        harmony = "undefined"
    
    signature = f"{spread}_{energy}_{harmony}"
    
    # Map signature to recommended approach
    recommendations = {
        "coherent_low_harmonic": "SAT (Set) or TSP (Anubis) — structured optimization",
        "coherent_medium_harmonic": "Vertex Cover (Thoth) — covering problems",
        "resonant_low_harmonic": "Graph Coloring (Horus) — assignment problems",
        "resonant_medium_harmonic": "Set Cover (Maat) — subset selection",
        "chaotic_low_inharmonic": "Hamiltonian Path (Osiris) — path finding",
        "chaotic_medium_inharmonic": "Clique (Ra) — dense subgraph problems",
        "coherent_high_harmonic": "Subset Sum (Bastet) — numerical constraints",
        "resonant_high_partially_harmonic": "Steiner Tree (Isis) — connectivity",
        "chaotic_high_partially_harmonic": "Exact Cover (Nephthys) — exact matching",
    }
    
    recommendation = recommendations.get(signature, "UniversalOneSolver — general purpose")
    
    return {
        'wavelength_signature': signature,
        'spread': spread,
        'energy': energy,
        'harmony': harmony,
        'mean': round(mean_val, 4),
        'std': round(std_val, 4),
        'recommended_solver': recommendation,
    }

# ═══════════════════════════════════════════════════════════
# 4. UNIFIED AUTO-DETECTOR
# ═══════════════════════════════════════════════════════════

def detect_problem(data):
    """
    Given ANY input, detect what kind of problem it is.
    
    Returns: {
        'type': inferred problem type,
        'russellian': octave analysis,
        'teslan': wavelength signature,
        'recommended_solver': which transformer to use,
    }
    """
    # Decompose
    if isinstance(data, str):
        sig72 = sig(data.encode('utf-8'))
    elif isinstance(data, bytes):
        sig72 = sig(data)
    elif isinstance(data, list) and len(data) == 72:
        sig72 = data
    else:
        sig72 = sig(str(data).encode('utf-8'))
    
    # Russellian: octave structure
    russ = russellian_octaves(sig72)
    
    # Teslan: wavelength classification
    tesla = teslan_signature(sig72)
    
    # Infer problem type from combined signals
    problem_type = _infer_problem_type(russ, tesla)
    
    return {
        'problem_type': problem_type,
        'russellian': russ,
        'teslan': tesla,
        'signature_72': sig72,
    }

def _infer_problem_type(russ: dict, tesla: dict) -> str:
    """Infer problem type from octave structure + wavelength signature."""
    dom_octave = russ['dominant_octave']
    structure = russ['structure']
    spread = tesla['spread']
    harmony = tesla['harmony']
    energy = tesla['energy']
    
    # Foundation-dominant → TSP, VC, physical optimization
    if dom_octave == "Foundation" and spread in ("coherent", "resonant"):
        return "tsp_or_vc"
    
    # Rhythm-dominant → SAT, pattern matching
    if dom_octave == "Rhythm":
        return "sat"
    
    # Heart/Mind → assignment, coloring
    if dom_octave in ("Heart", "Mind") and harmony == "harmonic":
        return "coloring_or_partition"
    
    # Spirit → clique, steiner
    if dom_octave == "Spirit" and spread == "chaotic":
        return "clique_or_steiner"
    
    # Unity → set cover, exact cover
    if dom_octave == "Unity":
        return "set_cover_or_exact"
    
    # Creation → subset sum, hamiltonian
    if dom_octave == "Creation" and harmony in ("harmonic", "partially_harmonic"):
        return "subsetsum_or_hamiltonian"
    
    # Fallback
    return "universal"

# ═══════════════════════════════════════════════════════════
# 5. WAVELENGTH DECOMPOSITION BY TYPE
# ═══════════════════════════════════════════════════════════

def decompose_for_type(problem_type, data, n_vars=None):
    """
    Create the appropriate problem-specific decomposition
    for the detected problem type. Returns (prob_sig, sol_sig) generator.
    """
    if problem_type in ("sat", "tsp_or_vc"):
        # SAT-style clause-aware decomposition
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
            # Looks like clauses
            clauses = data
            if n_vars is None:
                n_vars = max(abs(l) for c in clauses for l, _ in c)
            
            def sat_decomp(assignment):
                return _decompose_clause_aware(clauses, assignment, n_vars)
            return "sat", sat_decomp, n_vars
    
    # Fallback: standard 72-band decomposition
    def standard_decomp(state):
        if isinstance(state, dict):
            prob_sig = sig(str(data).encode('utf-8'))
            sol_sig = sig(str(state).encode('utf-8'))
        else:
            prob_sig = sig(str(data).encode('utf-8'))
            sol_sig = sig(str(state).encode('utf-8'))
        return prob_sig, sol_sig
    return "universal", standard_decomp, n_vars

def _decompose_clause_aware(clauses, assignment, n_vars):
    """Clause-aware decomposition — spreads variable energy across neighbor bands."""
    clause_neighbors = {v: set() for v in range(1, n_vars + 1)}
    for clause in clauses:
        clause_vars = [var for var, _ in clause]
        for v in clause_vars:
            for u in clause_vars:
                if u != v:
                    clause_neighbors[v].add(u)
    
    prob = [0.0] * 72
    sol = [0.0] * 72
    prob_total = 0.0
    sol_total = 0.0
    
    for v in range(1, n_vars + 1):
        primary_band = (v - 1) % 72
        
        pos_need = sum(1 for c in clauses for lv, s in c if lv == v and s)
        neg_need = sum(1 for c in clauses for lv, s in c if lv == v and not s)
        prob_val = (pos_need - neg_need) / max(1, pos_need + neg_need)
        sol_val = 1.0 if assignment.get(v, False) else -1.0
        
        prob[primary_band] += prob_val * 0.5
        sol[primary_band] += sol_val * 0.5
        prob_total += abs(prob_val) * 0.5
        sol_total += abs(sol_val) * 0.5
        
        neighbors = clause_neighbors.get(v, set())
        if neighbors:
            spread_w = 0.5 / len(neighbors)
            for u in neighbors:
                nb = (u - 1) % 72
                prob[nb] += prob_val * spread_w
                sol[nb] += sol_val * spread_w
                prob_total += abs(prob_val) * spread_w
                sol_total += abs(sol_val) * spread_w
    
    if prob_total > 0: prob = [p / prob_total for p in prob]
    if sol_total > 0: sol = [s / sol_total for s in sol]
    return prob, sol

# ═══════════════════════════════════════════════════════════
# 6. DEMONSTRATION
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("PROBLEM AUTO-DETECTOR")
    print("Teslan Wavelength + Russellian Octaves")
    print("=" * 70)
    
    # Test with different problem types
    np.random.seed(42)
    random.seed(42)
    
    tests = []
    
    # SAT instance
    nv, nc = 30, 126
    sat_clauses = [[(random.randint(1, nv), random.choice([True, False]))
                    for _ in range(3)] for _ in range(nc)]
    tests.append(("SAT (30 vars, 126 clauses)", str(sat_clauses)))
    
    # TSP instance
    pts = [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(30)]
    dm = np.zeros((30, 30))
    for i in range(30):
        for j in range(30):
            dx = pts[i][0] - pts[j][0]
            dy = pts[i][1] - pts[j][1]
            dm[i][j] = math.sqrt(dx*dx + dy*dy)
    tests.append(("TSP (30 cities)", dm.tobytes()))
    
    # Graph edges
    nv2 = 25
    edges = [(random.randint(0, nv2-1), random.randint(0, nv2-1)) for _ in range(60)]
    edges = [(u,v) for u,v in edges if u != v][:40]
    tests.append(("Graph (25v, 40e)", str(edges)))
    
    # Text
    tests.append(("English text", "solve this traveling salesman problem with 50 cities"))
    
    for name, data in tests:
        print(f"\n{'─'*70}")
        print(f"Input: {name}")
        print(f"{'─'*70}")
        
        result = detect_problem(data)
        
        # Russellian
        russ = result['russellian']
        print(f"  Octaves:")
        for o in russ['octaves']:
            bar = '█' * int(o['energy'] / max(1e-10, russ['dominant_energy']) * 30)
            print(f"    {o['name']:12s} ({o['bands']:>7s}): {o['energy']:.4f} {bar}")
        print(f"  Structure: {russ['structure']}")
        print(f"  Dominant:  {russ['dominant_octave']}")
        
        # Teslan
        tesla = result['teslan']
        print(f"\n  Wavelength: {tesla['wavelength_signature']}")
        print(f"  Spread: {tesla['spread']}, Energy: {tesla['energy']}, Harmony: {tesla['harmony']}")
        print(f"  Mean={tesla['mean']}, Std={tesla['std']}")
        
        # Detection
        print(f"\n  ★ DETECTED: {result['problem_type']}")
        print(f"  ★ SOLVER:   {tesla['recommended_solver']}")
