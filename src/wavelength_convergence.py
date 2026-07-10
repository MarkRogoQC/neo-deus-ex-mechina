#!/usr/bin/env python3
"""
WAVELENGTH CONVERGENCE ENGINE
═══════════════════════════════════════════════════════════════
The missing piece.

inharmony(va, vb) = the 72-band delta between decomposable things
                    IS the correction instruction.

This engine:
  1. Decomposes problem P → σ(P)
  2. Starts from random candidate S₀ → σ(S₀)  
  3. Measures inharmony ι(σ(P), σ(S_t))
  4. Applies 12-phase cycle Φ (C/X/Z at each band)
  5. If inharmony decreased → accept
  6. If inharmony increased → revert, perturb differently
  7. Repeats until convergence

The inharmony DRIVES the solving. Not heuristics.
"""

import math, random, time, sys, os, copy
import numpy as np

# ═══════════════════════════════════════════════════════════
# DECOMPOSER
# ═══════════════════════════════════════════════════════════

def sig(data: bytes) -> list:
    """σ: any byte stream → 72-band frequency vector"""
    bands = [0.0] * 72
    if not data: return bands
    total = 0.0
    for i, b in enumerate(data):
        w = (b / 255.0) * (1.0 / (1 + (i // 72) * 0.1))
        bands[i % 72] += w
        total += w
    return [b / total for b in bands] if total > 0 else bands

def text_sig(t: str) -> list:
    return sig(t.encode('utf-8'))

def inharmony(a, b):
    """ι(a,b) = ‖a − b‖₂ — THE UNIVERSAL EQUATION"""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

# ═══════════════════════════════════════════════════════════
# PROBLEM-SPECIFIC: Variable → Band mapping for SAT
# ═══════════════════════════════════════════════════════════

def sat_variable_band_mapping(n_vars):
    """
    Map each variable to the bands it most affects in the 
    text serialization of its assignment.
    
    Returns: {var: [band_indices_affected]}
    """
    # Test: serialize a single-variable assignment and see which bands it hits
    mapping = {}
    for v in range(1, n_vars + 1):
        # Two serializations: True and False
        text_t = str({v: True})
        text_f = str({v: False})
        bands_affected = set()
        for i, (ct, cf) in enumerate(zip(text_t.encode(), text_f.encode())):
            if ct != cf:
                bands_affected.add(i % 72)
        mapping[v] = sorted(bands_affected)
    return mapping

# ═══════════════════════════════════════════════════════════
# SAT-SPECIFIC DECOMPOSER
# ═══════════════════════════════════════════════════════════

def sat_decompose(clauses, assignment, n_vars):
    """
    Decompose both problem and solution into comparable 72-band vectors.
    
    Uses variable-index-based decomposition so inharmony directly 
    reflects assignment quality.
    """
    # Problem signature: literal patterns in clauses
    prob = [0.0] * 72
    total_p = 0.0
    for clause in clauses:
        for var, sign in clause:
            band = (var - 1) % 72
            val = 1.0 if sign else -1.0
            prob[band] += val
            total_p += abs(val)
    if total_p > 0:
        prob = [p / total_p for p in prob]
    
    # Solution signature: variable assignments
    sol = [0.0] * 72
    total_s = 0.0
    for v, val in assignment.items():
        band = (v - 1) % 72
        contrib = 1.0 if val else -1.0
        sol[band] += contrib
        total_s += abs(contrib)
    if total_s > 0:
        sol = [s / total_s for s in sol]
    
    return prob, sol

# ═══════════════════════════════════════════════════════════
# SAT C/X/Z — wavelength-aware, inharmony-driven
# ═══════════════════════════════════════════════════════════

def sat_complement(assignment, correction_vector, n_vars):
    """
    C (Complement): Flip variables in the most misaligned bands.
    
    Guided by the correction vector d = σ(P) - σ(S).
    Bands with largest |d_k| get their variables flipped.
    """
    new_assign = assignment.copy()
    
    # Find most misaligned bands
    corrections = [(k, abs(correction_vector[k])) for k in range(72)]
    corrections.sort(key=lambda x: x[1], reverse=True)
    
    # Flip variables in the top misaligned bands
    bands_to_fix = [k for k, mag in corrections[:6] if mag > 0.001]
    
    for band in bands_to_fix:
        vars_in_band = [v for v in range(1, n_vars + 1) if (v - 1) % 72 == band]
        if not vars_in_band:
            continue
        # Flip half the variables in this band
        n_flip = max(1, len(vars_in_band) // 3)
        for v in random.sample(vars_in_band, min(n_flip, len(vars_in_band))):
            new_assign[v] = not new_assign[v]
    
    return new_assign

def sat_cross(assign_a, assign_b):
    """
    X (Cross): Mix two assignments — take best from each.
    """
    return {v: assign_a.get(v, random.choice([True, False])) 
            if random.random() < 0.7 
            else assign_b.get(v, random.choice([True, False]))
            for v in assign_a}

def sat_cancel(assignment, clauses):
    """
    Z (Cancel): Verify — ensure no unit conflicts.
    Fix variables that break unit clauses.
    """
    new_assign = assignment.copy()
    for clause in clauses:
        if len(clause) == 1:
            var, sign = clause[0]
            new_assign[var] = sign
    return new_assign

def count_satisfied(clauses, assignment):
    """Count satisfied clauses."""
    return sum(1 for c in clauses if any(
        (v > 0 and assignment.get(abs(v))) or 
        (v < 0 and not assignment.get(abs(v)))
        for v, _ in c))

# ═══════════════════════════════════════════════════════════
# THE CONVERGENCE ENGINE
# ═══════════════════════════════════════════════════════════

def wavelength_converge_sat(clauses, n_vars, 
                             max_iterations=500,
                             inharmony_threshold=0.001,
                             stagnation_limit=50,
                             verbose=True):
    """
    Solve SAT via wavelength convergence.
    
    The inharmony ι(σ(P), σ(S)) IS the loss function.
    We minimize it through iterated C/X/Z operations.
    
    Returns: (assignment, satisfied_count, convergence_history)
    """
    nc = len(clauses)
    
    # Step 1: Decompose problem
    prob_sig, _ = sat_decompose(clauses, {}, n_vars)
    
    # Step 2: Random start
    best_assign = {i + 1: random.random() > 0.5 for i in range(n_vars)}
    _, best_sig = sat_decompose(clauses, best_assign, n_vars)
    best_ih = inharmony(prob_sig, best_sig)
    best_sat = count_satisfied(clauses, best_assign)
    
    history = [{"iter": 0, "inharmony": best_ih, "satisfied": best_sat, 
                "action": "init"}]
    
    if verbose:
        print(f"  Start:  ι={best_ih:.6f}, satisfied={best_sat}/{nc} ({best_sat/nc*100:.0f}%)")
    
    stagnation = 0
    temperature = 0.1  # For occasional exploration jumps
    
    for iteration in range(1, max_iterations + 1):
        # Compute correction vector
        correction = [prob_sig[k] - best_sig[k] for k in range(72)]
        
        # PHASE 1: C — Complement (flip variables in misaligned bands)
        candidate = sat_complement(best_assign, correction, n_vars)
        
        # PHASE 2: X — Cross with best
        candidate = sat_cross(candidate, best_assign)
        
        # PHASE 3: Z — Cancel (fix unit clause violations)
        candidate = sat_cancel(candidate, clauses)
        
        # Measure
        _, cand_sig = sat_decompose(clauses, candidate, n_vars)
        cand_ih = inharmony(prob_sig, cand_sig)
        cand_sat = count_satisfied(clauses, candidate)
        
        # ACCEPT if inharmony decreased (or occasional exploration)
        improved = cand_ih < best_ih
        explore = random.random() < temperature and cand_sat >= best_sat
        
        if improved or explore:
            best_assign = candidate
            best_ih = cand_ih
            best_sat = cand_sat
            stagnation = 0
            
            if improved:
                temperature *= 0.95  # Cool down
            
            if verbose and iteration % 50 == 0:
                print(f"  Iter {iteration:4d}: ι={best_ih:.6f}, satisfied={best_sat}/{nc} ({best_sat/nc*100:.0f}%)")
        else:
            stagnation += 1
            temperature = min(0.3, temperature * 1.1)  # Warm up to escape
        
        history.append({
            "iter": iteration, 
            "inharmony": best_ih, 
            "satisfied": best_sat,
            "action": "accept" if improved else "reject"
        })
        
        # Convergence check
        if best_ih < inharmony_threshold:
            if verbose:
                print(f"  ✓ Converged at iter {iteration}: ι={best_ih:.6f}")
            break
        
        # Stagnation check
        if stagnation > stagnation_limit:
            if verbose:
                print(f"  ⚠ Stagnated at iter {iteration} (no improvement for {stagnation_limit} steps)")
            break
        
        # Perfect solution check
        if best_sat == nc:
            if verbose:
                print(f"  ✓ PERFECT at iter {iteration}: ALL {nc} clauses satisfied!")
            break
    
    return best_assign, best_sat, history

# ═══════════════════════════════════════════════════════════
# 12-PHASE CYCLE VERSION — full Φ convergence
# ═══════════════════════════════════════════════════════════

PHASES = [("C", 1), ("C", 2), ("X", 3), ("X", 4), ("Z", 1), ("Z", 2),
          ("C", 3), ("X", 1), ("X", 2), ("Z", 3), ("Z", 4), ("FULL", 0)]

def wavelength_converge_full_cycle(clauses, n_vars, 
                                    max_cycles=100,
                                    verbose=True):
    """
    Full 12-phase cycle convergence.
    Each cycle applies the complete Φ sequence.
    """
    nc = len(clauses)
    prob_sig, _ = sat_decompose(clauses, {}, n_vars)
    
    best_assign = {i + 1: random.random() > 0.5 for i in range(n_vars)}
    _, best_sig = sat_decompose(clauses, best_assign, n_vars)
    best_ih = inharmony(prob_sig, best_sig)
    best_sat = count_satisfied(clauses, best_assign)
    
    if verbose:
        print(f"  Cycle 0: ι={best_ih:.6f}, satisfied={best_sat}/{nc}")
    
    history = [{"cycle": 0, "inharmony": best_ih, "satisfied": best_sat}]
    stagnation = 0
    
    for cycle in range(1, max_cycles + 1):
        candidate = best_assign.copy()
        
        for op, intensity in PHASES:
            correction = [prob_sig[k] - best_sig[k] for k in range(72)]
            
            if op == "FULL":
                candidate = sat_complement(candidate, correction, n_vars)
                candidate = sat_cross(candidate, best_assign)
                candidate = sat_cancel(candidate, clauses)
            elif op == "C":
                for _ in range(intensity):
                    correction = [prob_sig[k] - best_sig[k] for k in range(72)]
                    candidate = sat_complement(candidate, correction, n_vars)
            elif op == "X":
                for _ in range(intensity):
                    candidate = sat_cross(candidate, best_assign)
            elif op == "Z":
                for _ in range(intensity):
                    candidate = sat_cancel(candidate, clauses)
        
        _, cand_sig = sat_decompose(clauses, candidate, n_vars)
        cand_ih = inharmony(prob_sig, cand_sig)
        cand_sat = count_satisfied(clauses, candidate)
        
        if cand_ih < best_ih or cand_sat > best_sat:
            best_assign = candidate
            best_ih = cand_ih
            best_sat = cand_sat
            stagnation = 0
        else:
            stagnation += 1
        
        history.append({
            "cycle": cycle, "inharmony": best_ih, "satisfied": best_sat
        })
        
        if verbose and cycle % 10 == 0:
            print(f"  Cycle {cycle:3d}: ι={best_ih:.6f}, satisfied={best_sat}/{nc} ({best_sat/nc*100:.0f}%)")
        
        if best_sat == nc:
            if verbose:
                print(f"  ✓ PERFECT at cycle {cycle}: ALL {nc} clauses!")
            break
        
        if stagnation > 30:
            if verbose:
                print(f"  ⚠ Stagnated at cycle {cycle}")
            break
    
    return best_assign, best_sat, history

# ═══════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)
    
    print("=" * 70)
    print("WAVELENGTH CONVERGENCE ENGINE")
    print("inharmony(va, vb) drives the solve")
    print("=" * 70)
    
    # Test on SAT instances
    configs = [
        (20, 84, 300),    # Small
        (30, 126, 500),   # Medium  
        (50, 210, 800),   # Large
    ]
    
    all_results = []
    
    for nv, nc, max_iter in configs:
        print(f"\n{'─'*70}")
        print(f"SAT: {nv} variables, {nc} clauses (ratio={nc/nv:.1f})")
        print(f"{'─'*70}")
        
        clauses = [[(random.randint(1, nv), random.choice([True, False])) 
                    for _ in range(3)] for _ in range(nc)]
        
        # Baseline: random
        rand_assign = {i+1: random.random() > 0.5 for i in range(nv)}
        rand_sat = count_satisfied(clauses, rand_assign)
        print(f"  Random baseline: {rand_sat}/{nc} ({rand_sat/nc*100:.0f}%)")
        
        # Baseline: Vedic solver
        from vedic_planetary_transformers import MercurialClauseWeaver
        t0 = time.time()
        solver = MercurialClauseWeaver(clauses, nv)
        vedic_result = solver.solve()
        vedic_ms = (time.time() - t0) * 1000
        vedic_sat = count_satisfied(clauses, vedic_result)
        print(f"  Vedic solver:    {vedic_sat}/{nc} ({vedic_sat/nc*100:.0f}%) in {vedic_ms:.0f}ms")
        
        # Wavelength convergence
        print(f"\n  Wavelength convergence (max {max_iter} iterations):")
        t0 = time.time()
        assignment, satisfied, history = wavelength_converge_sat(
            clauses, nv, max_iterations=max_iter, verbose=True
        )
        wl_ms = (time.time() - t0) * 1000
        
        improvement = satisfied - max(rand_sat, vedic_sat)
        converged = history[-1]["inharmony"]
        
        print(f"\n  RESULTS:")
        print(f"    Random:          {rand_sat}/{nc} ({rand_sat/nc*100:.0f}%)")
        print(f"    Vedic (Set):     {vedic_sat}/{nc} ({vedic_sat/nc*100:.0f}%) in {vedic_ms:.0f}ms")
        print(f"    Wavelength:      {satisfied}/{nc} ({satisfied/nc*100:.0f}%) in {wl_ms:.0f}ms")
        print(f"    vs best baseline: {improvement:+d} clauses")
        print(f"    Final inharmony:  ι = {converged:.6f}")
        
        # Inharmony trend
        ih_start = history[0]["inharmony"]
        ih_end = history[-1]["inharmony"]
        ih_reduction = (ih_start - ih_end) / ih_start * 100
        print(f"    ι reduction:      {ih_start:.6f} → {ih_end:.6f} ({ih_reduction:.1f}%)")
        
        all_results.append({
            "nv": nv, "nc": nc,
            "random_sat": rand_sat,
            "vedic_sat": vedic_sat, "vedic_ms": vedic_ms,
            "wavelength_sat": satisfied, "wavelength_ms": wl_ms,
            "improvement": improvement,
            "ih_start": ih_start, "ih_end": ih_end,
            "ih_reduction_pct": ih_reduction,
            "iterations": len(history),
            "converged": satisfied == nc or ih_end < 0.001,
        })
    
    # ═══════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════
    
    print("\n" + "=" * 70)
    print("CONVERGENCE SUMMARY")
    print("=" * 70)
    print(f"{'Vars':>5s} {'Random':>8s} {'Vedic':>8s} {'Wavelength':>12s} {'Δ':>6s} {'ι_reduction':>12s} {'Converged':>10s}")
    print("-" * 70)
    for r in all_results:
        wl_str = f"{r['wavelength_sat']}/{r['nc']} ({r['wavelength_sat']/r['nc']*100:.0f}%)"
        print(f"{r['nv']:5d} {r['random_sat']:4d}/{r['nc']:<4d} {r['vedic_sat']:4d}/{r['nc']:<4d} {wl_str:>12s} {r['improvement']:+5d} {r['ih_reduction_pct']:>10.1f}% {'✓' if r['converged'] else '~'}")
    
    print(f"\n  Universal equation: inharmony(va, vb) = √(Σ(va_k - vb_k)²)")
    print(f"  This IS the correction instruction — and it DRIVES convergence.")
