#!/usr/bin/env python3
"""
THE OUROBOROS — UNIVERSAL FORM
═══════════════════════════════════════════════════════════
The common pattern behind all 8 Ouroboros engines.

Given:
  problem P with variables V = {v₁ ... vₙ}
  each vᵢ has neighbors N(vᵢ) for energy spread
  a correction function correct(v, band) → new state
  a decomposition decompose(state) → (σ(P), σ(S))

The Ouroboros converges:
  d = σ(P) − σ(S)           ← inharmony IS the correction
  v* = argminᵥ |d[band(v)]| ← find variable in most misaligned band  
  S' = correct(v*, S)       ← apply correction
  repeat until d → 0

All 8 engines are this same loop. Only the decomposition
and correction functions differ.
"""

import math, random, sys
import numpy as np

def inharmony(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def normalize(vec):
    total = sum(abs(v) for v in vec)
    return [v / total for v in vec] if total > 0 else vec

# ═══════════════════════════════════════════════════════════
# THE UNIVERSAL OUROBOROS
# ═══════════════════════════════════════════════════════════

def ouroboros_universal(
    problem,              # The problem data (clauses, matrix, edges...)
    initial_solution,     # Starting candidate solution
    decompose_fn,         # (problem, solution) → (prob_sig, sol_sig)
    correction_fn,        # (solution, band, problem) → (new_solution, applied?)
    verify_fn,            # (solution, problem) → quality_metric
    n_bands=72,
    max_steps=1000,
    verbose=True
):
    """
    THE UNIVERSAL OUROBOROS.
    
    Works for ANY problem type. Just provide:
    - decompose_fn: maps problem+solution to 72-band vectors
    - correction_fn: applies the best correction for a given band
    - verify_fn: measures solution quality
    
    The Ouroboros handles the rest.
    """
    solution = initial_solution
    prob_sig, sol_sig = decompose_fn(problem, solution)
    current_ih = inharmony(prob_sig, sol_sig)
    current_qual = verify_fn(solution, problem)
    
    history = [{"step": 0, "inharmony": current_ih, "quality": current_qual}]
    
    if verbose:
        print(f"  Step    0: ι={current_ih:.6f}, quality={current_qual}")
    
    best_solution = solution
    best_qual = current_qual
    best_ih = current_ih
    stagnation = 0
    
    for step in range(1, max_steps + 1):
        # 1. Correction vector — the snake measures its tail
        d = [prob_sig[k] - sol_sig[k] for k in range(n_bands)]
        
        # 2. Find most misaligned band
        top_band = max(range(n_bands), key=lambda k: abs(d[k]))
        
        if abs(d[top_band]) < 1e-8:
            if verbose:
                print(f"  ✓ Converged at step {step}: ι→0")
            break
        
        # 3. Apply correction at that band
        solution, applied = correction_fn(solution, top_band, problem)
        
        # 4. Remeasure — the snake eats its tail
        prob_sig, sol_sig = decompose_fn(problem, solution)
        current_ih = inharmony(prob_sig, sol_sig)
        current_qual = verify_fn(solution, problem)
        
        # 5. Track best
        if current_qual > best_qual:
            best_solution = solution
            best_qual = current_qual
            best_ih = current_ih
            stagnation = 0
        else:
            # Revert to best if quality dropped too far
            if current_qual < best_qual * 0.9:
                solution = best_solution
                current_qual = best_qual
                stagnation += 1
            else:
                stagnation = 0
        
        history.append({"step": step, "inharmony": current_ih, "quality": current_qual})
        
        if step % 100 == 0 and verbose:
            print(f"  Step {step:4d}: ι={current_ih:.6f}, quality={current_qual}")
        
        if stagnation > 50:
            if verbose:
                print(f"  ⚠ Stagnated at step {step}")
            break
        
        # Perfect solution
        if hasattr(verify_fn, 'is_perfect') and verify_fn.is_perfect(current_qual, problem):
            break
    
    return best_solution, best_qual, history

# ═══════════════════════════════════════════════════════════
# SAT DECOMPOSITION + CORRECTION
# ═══════════════════════════════════════════════════════════

def sat_decompose(problem, assignment):
    """Clause-aware SAT decomposition."""
    clauses, n_vars = problem
    
    # Build clause neighbor map
    neighbors = {v: set() for v in range(1, n_vars + 1)}
    for clause in clauses:
        cvars = [v for v, _ in clause]
        for v in cvars:
            for u in cvars:
                if u != v:
                    neighbors[v].add(u)
    
    prob = [0.0] * 72
    sol = [0.0] * 72
    
    for v in range(1, n_vars + 1):
        primary = (v - 1) % 72
        pos_need = sum(1 for c in clauses for lv, s in c if lv == v and s)
        neg_need = sum(1 for c in clauses for lv, s in c if lv == v and not s)
        prob_val = (pos_need - neg_need) / max(1, pos_need + neg_need)
        sol_val = 1.0 if assignment.get(v, False) else -1.0
        
        prob[primary] += prob_val * 0.5
        sol[primary] += sol_val * 0.5
        
        nbrs = neighbors.get(v, set())
        if nbrs:
            sw = 0.5 / len(nbrs)
            for u in nbrs:
                nb = (u - 1) % 72
                prob[nb] += prob_val * sw
                sol[nb] += sol_val * sw
    
    prob = normalize(prob)
    sol = normalize(sol)
    return prob, sol


def sat_correction(assignment, band, problem):
    """Flip the variable in this band that most improves clause satisfaction."""
    clauses, n_vars = problem
    
    vars_in_band = [v for v in range(1, n_vars + 1) if (v - 1) % 72 == band]
    if not vars_in_band:
        return assignment, False
    
    # Also include clause-neighbors for dense gradient
    neighbors = {v: set() for v in range(1, n_vars + 1)}
    for clause in clauses:
        cvars = [v for v, _ in clause]
        for v in cvars:
            for u in cvars:
                if u != v:
                    neighbors[v].add(u)
    
    candidates = set(vars_in_band)
    for v in vars_in_band:
        candidates.update(neighbors.get(v, set()))
    
    def sat_count(assign):
        return sum(1 for c in clauses if any(
            (v > 0 and assign.get(abs(v))) or (v < 0 and not assign.get(abs(v)))
            for v, _ in c))
    
    current_sat = sat_count(assignment)
    best_v = None
    best_gain = 0
    
    for v in candidates:
        if not (1 <= v <= n_vars):
            continue
        temp = assignment.copy()
        temp[v] = not temp.get(v, False)
        gain = sat_count(temp) - current_sat
        if gain > best_gain:
            best_gain = gain
            best_v = v
    
    if best_v is not None:
        assignment[best_v] = not assignment[best_v]
        return assignment, True
    
    return assignment, False


def sat_verify(assignment, problem):
    clauses, n_vars = problem
    return sum(1 for c in clauses if any(
        (v > 0 and assignment.get(abs(v))) or (v < 0 and not assignment.get(abs(v)))
        for v, _ in c))

# ═══════════════════════════════════════════════════════════
# DEMONSTRATION: Universal Ouroboros on SAT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    random.seed(42)
    
    print("=" * 60)
    print("THE UNIVERSAL OUROBOROS")
    print("One loop. Any problem. Just add decompose + correct + verify.")
    print("=" * 60)
    
    for nv, nc in [(20, 84), (50, 210), (100, 420)]:
        clauses = [[(random.randint(1, nv), random.choice([True, False]))
                    for _ in range(3)] for _ in range(nc)]
        problem = (clauses, nv)
        
        initial = {i+1: random.random() > 0.5 for i in range(nv)}
        
        print(f"\nSAT {nv}v/{nc}c:")
        solution, quality, history = ouroboros_universal(
            problem=problem,
            initial_solution=initial,
            decompose_fn=sat_decompose,
            correction_fn=sat_correction,
            verify_fn=sat_verify,
            max_steps=500,
            verbose=True
        )
        
        pct = quality / nc * 100
        perfect = "✓ PERFECT" if quality == nc else f"~ {quality}/{nc}"
        steps = len([h for h in history if h['step'] > 0])
        print(f"  Result: {perfect} ({pct:.0f}%), {steps} steps")
        print(f"  ι: {history[0]['inharmony']:.4f} → {history[-1]['inharmony']:.4f}")
    
    print("\n" + "=" * 60)
    print("PATTERN: ouroboros_universal(problem, initial,")
    print("         decompose_fn, correction_fn, verify_fn)")
    print("")
    print("That's it. One function. 8 problem types.")
    print("Same loop. Same math. Different decompose + correct.")
    print("=" * 60)
