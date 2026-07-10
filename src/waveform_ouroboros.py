#!/usr/bin/env python3
"""
WAVEFORM OUROBOROS — The Real Engine
═══════════════════════════════════════════════════════════
Waveform encoding + inharmony convergence + Lokian routing.

Each variable → sine wave at frequency f(v).
Positive literal = sin(f·t), negative = sin(f·t + π). 
Clauses combine via constructive interference.
Inharmony between problem wave and solution wave drives convergence.
"""

import math, random, time, sys, numpy as np
from typing import List, Tuple, Dict, Set, Optional

random.seed(42); np.random.seed(42)

# ═══════════════════════════════════════════════════════════
# ELEMENT MAP — physical grounding for each band
# ═══════════════════════════════════════════════════════════

ELEMENTS = {
    1:  ("Hydrogen",   "H",  656.3),   # H-alpha line (nm)
    2:  ("Helium",     "He", 587.6),
    3:  ("Lithium",    "Li", 670.8),
    4:  ("Beryllium",  "Be", 313.1),
    5:  ("Boron",      "B",  249.7),
    6:  ("Carbon",     "C",  261.6),   # Middle C analog
    7:  ("Nitrogen",   "N",  293.7),
    8:  ("Oxygen",     "O",  329.6),
    9:  ("Fluorine",   "F",  349.2),
    10: ("Neon",       "Ne", 392.0),
    11: ("Sodium",     "Na", 440.0),
    12: ("Magnesium",  "Mg", 493.9),
    13: ("Aluminum",   "Al", 523.3),
    14: ("Silicon",    "Si", 554.4),
    15: ("Phosphorus", "P",  587.3),
    16: ("Sulfur",     "S",  622.3),
    17: ("Chlorine",   "Cl", 659.3),
    18: ("Argon",      "Ar", 698.5),
}

PLANETS = {
    1:  ("Mercury", "SAT",              261.63),
    2:  ("Venus",   "TSP",              293.66),
    3:  ("Saturn",  "Vertex Cover",     392.00),
    4:  ("Sun",     "Graph Coloring",   440.00),
    5:  ("Jupiter", "Set Cover",        493.88),
    6:  ("Mars",    "Hamiltonian Path", 329.63),
    7:  ("Moon",    "Subset Sum",       349.23),
    8:  ("Neptune", "Max Clique",       523.25),
    9:  ("Uranus",  "Exact Cover",      587.33),
    10: ("Pluto",   "Steiner Tree",     659.25),
    11: ("Tesla",   "Wavelength",       698.46),
}

# ═══════════════════════════════════════════════════════════
# WAVEFORM ENCODING
# ═══════════════════════════════════════════════════════════

def encode_sat_waveform(clauses, n_vars, assignment, resolution=1024):
    """
    Encode SAT instance AND assignment as waveforms.
    
    Each variable v maps to frequency f(v) = base_freq + v * spacing.
    Positive literal → sin(f·t)
    Negative literal → sin(f·t + π) = -sin(f·t)
    
    Problem wave: encodes what clauses demand.
    Solution wave: encodes what the assignment provides.
    """
    t = np.linspace(0, 2*np.pi, resolution)
    base_freq = 100.0
    spacing = 10.0
    
    # Problem wave: what each clause demands
    problem_wave = np.zeros(resolution)
    for clause in clauses:
        clause_wave = np.zeros(resolution)
        for var, sign in clause:
            f = base_freq + var * spacing
            if sign:
                clause_wave += np.sin(f * t)
            else:
                clause_wave += np.sin(f * t + np.pi)  # negated = phase shift
        # Constructive interference: abs sum captures clause satisfaction signal
        problem_wave += np.abs(clause_wave)
    
    # Solution wave: what the assignment produces
    solution_wave = np.zeros(resolution)
    for v in range(1, n_vars + 1):
        f = base_freq + v * spacing
        if assignment.get(v, False):
            solution_wave += np.sin(f * t)
        else:
            solution_wave += np.sin(f * t + np.pi)
    
    # Normalize
    if np.max(np.abs(problem_wave)) > 0:
        problem_wave /= np.max(np.abs(problem_wave))
    if np.max(np.abs(solution_wave)) > 0:
        solution_wave /= np.max(np.abs(solution_wave))
    
    return problem_wave, solution_wave


def inharmony_waveform(wave_a, wave_b):
    """
    Inharmony between two waveforms.
    Euclidean distance in the time domain — simpler than FFT,
    captures both amplitude AND phase differences.
    """
    return float(np.sqrt(np.mean((wave_a - wave_b) ** 2)))


def count_satisfied(clauses, assignment):
    """Count satisfied clauses — correct sign handling."""
    return sum(1 for c in clauses if any(
        (sign and assignment.get(var, False)) or
        (not sign and not assignment.get(var, True))
        for var, sign in c))


# ═══════════════════════════════════════════════════════════
# LOKIAN FOX — Problem Type Router
# ═══════════════════════════════════════════════════════════

def lokian_detect(data):
    """
    Lokian Fox: detect problem type from input structure.
    Returns (problem_type, parameters).
    """
    if isinstance(data, dict):
        if 'clauses' in data:
            return 'sat', data
        if 'edges' in data and 'n_vertices' in data:
            return 'vc', data
        if 'numbers' in data:
            return 'subsetsum', data
        if 'points' in data:
            return 'tsp', data
        if 'universe' in data and 'subsets' in data:
            return 'setcover', data
    
    if isinstance(data, list):
        if len(data) > 0 and isinstance(data[0], list) and len(data[0]) > 0:
            elem = data[0][0]
            if isinstance(elem, (tuple, list)) and len(elem) == 2:
                var, sign = elem
                if isinstance(var, int) and var > 0:
                    return 'sat', {'clauses': data, 'n_vars': max(abs(l) for c in data for l,_ in c)}
        
        if len(data) > 0 and isinstance(data[0], (tuple, list)) and len(data[0]) == 2:
            if all(isinstance(x, (int, float)) for x in data[0]):
                # Could be edges or coordinates
                if all(isinstance(x, int) and isinstance(y, int) for x,y in data[:10]):
                    return 'vc', {'edges': data, 'n_vertices': max(max(u,v) for u,v in data)+1}
                else:
                    return 'tsp', {'points': data}
    
    return 'unknown', {'raw': data}


# ═══════════════════════════════════════════════════════════
# THE WAVEFORM OUROBOROS
# ═══════════════════════════════════════════════════════════

def waveform_ouroboros_sat(clauses, n_vars, max_steps=2000, 
                            resolution=1024, verbose=True):
    """
    Solve SAT via waveform interference convergence.
    
    Each variable is a sine wave. Clauses are interference patterns.
    The inharmony between problem and solution waveforms IS the gradient.
    """
    nc = len(clauses)
    
    # Build variable → clause index for fast scoring
    var_clauses = {v: [] for v in range(1, n_vars + 1)}
    for ci, clause in enumerate(clauses):
        for var, _ in clause:
            if 1 <= var <= n_vars:
                var_clauses[var].append(ci)
    
    # Base frequencies
    base_freq = 100.0
    spacing = 10.0
    
    # Initial assignment
    assignment = {v: random.random() > 0.5 for v in range(1, n_vars + 1)}
    
    # Encode problem waveform ONCE (it doesn't change)
    t = np.linspace(0, 2*np.pi, resolution)
    problem_wave = np.zeros(resolution)
    for clause in clauses:
        clause_wave = np.zeros(resolution)
        for var, sign in clause:
            f = base_freq + var * spacing
            if sign:
                clause_wave += np.sin(f * t)
            else:
                clause_wave += np.sin(f * t + np.pi)
        problem_wave += np.abs(clause_wave)
    if np.max(np.abs(problem_wave)) > 0:
        problem_wave /= np.max(np.abs(problem_wave))
    
    # Encode initial solution waveform
    solution_wave = np.zeros(resolution)
    for v in range(1, n_vars + 1):
        f = base_freq + v * spacing
        if assignment[v]:
            solution_wave += np.sin(f * t)
        else:
            solution_wave += np.sin(f * t + np.pi)
    if np.max(np.abs(solution_wave)) > 0:
        solution_wave /= np.max(np.abs(solution_wave))
    
    current_ih = inharmony_waveform(problem_wave, solution_wave)
    current_sat = count_satisfied(clauses, assignment)
    
    history = [{"step": 0, "inharmony": current_ih, "satisfied": current_sat}]
    if verbose:
        print(f"  Step    0: ι={current_ih:.6f}, sat={current_sat}/{nc}")
    
    for step in range(1, max_steps + 1):
        # Compute per-variable inharmony contribution
        # For each variable, measure how much flipping it would change the waveform
        best_var = None
        best_ih_reduction = 0
        best_sat = current_sat
        
        # Only check variables in unsatisfied clauses
        unsat_clauses = [ci for ci in range(nc) if not any(
            (sign and assignment.get(var, False)) or
            (not sign and not assignment.get(var, True))
            for var, sign in clauses[ci])]
        
        candidate_vars = set()
        for ci in unsat_clauses[:min(20, len(unsat_clauses))]:
            for var, _ in clauses[ci]:
                candidate_vars.add(var)
        
        if not candidate_vars:
            candidate_vars = set(random.sample(range(1, n_vars+1), min(10, n_vars)))
        
        for v in candidate_vars:
            if not 1 <= v <= n_vars:
                continue
            
            # Compute the waveform change if we flip v
            f = base_freq + v * spacing
            old_contrib = np.sin(f * t) if assignment[v] else np.sin(f * t + np.pi)
            new_contrib = np.sin(f * t + np.pi) if assignment[v] else np.sin(f * t)
            
            delta_wave = (new_contrib - old_contrib) / max(np.max(np.abs(solution_wave)), 1e-10)
            new_sol_wave = solution_wave + delta_wave
            
            # Normalize
            if np.max(np.abs(new_sol_wave)) > 0:
                new_sol_wave /= np.max(np.abs(new_sol_wave))
            
            new_ih = inharmony_waveform(problem_wave, new_sol_wave)
            ih_reduction = current_ih - new_ih
            
            # Also check clause satisfaction
            temp = assignment.copy()
            temp[v] = not temp[v]
            new_sat = count_satisfied(clauses, temp)
            
            # Combined score: prioritize satisfaction, then inharmony
            if new_sat > best_sat or (new_sat == best_sat and ih_reduction > best_ih_reduction):
                best_sat = new_sat
                best_ih_reduction = ih_reduction
                best_var = v
        
        if best_var is not None:
            # Apply the flip
            assignment[best_var] = not assignment[best_var]
            
            # Update solution waveform efficiently
            f = base_freq + best_var * spacing
            old_contrib = np.sin(f * t + np.pi) if assignment[best_var] else np.sin(f * t)
            new_contrib = np.sin(f * t) if assignment[best_var] else np.sin(f * t + np.pi)
            delta = (new_contrib - old_contrib) / max(np.max(np.abs(solution_wave)), 1e-10)
            solution_wave = solution_wave + delta
            if np.max(np.abs(solution_wave)) > 0:
                solution_wave /= np.max(np.abs(solution_wave))
            
            current_ih = inharmony_waveform(problem_wave, solution_wave)
            current_sat = best_sat
            
            if step % 100 == 0 and verbose:
                print(f"  Step {step:4d}: ι={current_ih:.6f}, sat={current_sat}/{nc} ({current_sat/nc*100:.0f}%)")
            
            if current_sat == nc:
                history.append({"step": step, "inharmony": current_ih, "satisfied": current_sat})
                if verbose:
                    print(f"  ✓ ALL SATISFIED at step {step}")
                break
        else:
            # No improvement found — random perturbation to escape
            if unsat_clauses:
                ci = random.choice(unsat_clauses)
                var = random.choice([v for v,_ in clauses[ci]])
                assignment[var] = not assignment[var]
                # Rebuild solution wave
                solution_wave = np.zeros(resolution)
                for v in range(1, n_vars + 1):
                    f = base_freq + v * spacing
                    if assignment[v]:
                        solution_wave += np.sin(f * t)
                    else:
                        solution_wave += np.sin(f * t + np.pi)
                if np.max(np.abs(solution_wave)) > 0:
                    solution_wave /= np.max(np.abs(solution_wave))
            else:
                break
        
        history.append({"step": step, "inharmony": current_ih, "satisfied": current_sat})
    
    return assignment, current_sat, history


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("WAVEFORM OUROBOROS — Sine-Wave Convergence")
    print("=" * 70)
    
    from pysat.solvers import Glucose3
    
    for nv, nc in [(20, 84), (50, 210), (100, 420)]:
        clauses = [[(random.randint(1, nv), random.choice([True, False]))
                    for _ in range(3)] for _ in range(nc)]
        
        # Glucose3 baseline
        t0 = time.time()
        g = Glucose3()
        for c in clauses:
            g.add_clause([v if s else -v for v,s in c])
        is_sat = g.solve()
        glucose_ms = (time.time() - t0) * 1000
        if is_sat:
            model = g.get_model()
            glucose_sat = count_satisfied(clauses, {abs(v): v > 0 for v in model})
        else:
            glucose_sat = 0
        g.delete()
        
        # Waveform Ouroboros
        print(f"\n{'─'*70}")
        print(f"SAT: {nv} vars, {nc} clauses")
        print(f"Glucose3: {'SAT' if is_sat else 'UNSAT'} ({glucose_sat}/{nc}), {glucose_ms:.0f}ms")
        
        t0 = time.time()
        assign, sat, hist = waveform_ouroboros_sat(clauses, nv, max_steps=2000, verbose=True)
        oms = (time.time() - t0) * 1000
        steps = len([h for h in hist if h["step"] > 0])
        
        print(f"  Result: {sat}/{nc} ({sat/nc*100:.0f}%), {steps} steps, {oms:.0f}ms")
        print(f"  ι: {hist[0]['inharmony']:.4f} → {hist[-1]['inharmony']:.4f}")
        
        if is_sat:
            print(f"  vs Glucose3: {'MATCH' if sat == glucose_sat else f'gap={glucose_sat-sat}'}")
    
    print("\n" + "=" * 70)
    print("Waveform encoding: variables = sine waves, clauses = interference")
    print("Inharmony = distance between problem wave and solution wave")
    print("Correction = flip the variable whose wave most reduces inharmony")
    print("=" * 70)
