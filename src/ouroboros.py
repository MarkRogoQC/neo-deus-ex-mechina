#!/usr/bin/env python3
"""
THE OUROBOROS ENGINE
═══════════════════════════════════════════════════════════════
The snake that eats its tail.

inharmony(va, vb) IS the correction instruction.
But the correction CHANGES the inharmony.
Which changes the correction.
Which changes the inharmony.

σ(P) − σ(S) = d       ← measurement
S' = S + η·C(d)       ← correction proportional to measurement
σ(P) − σ(S') = d'     ← new measurement
S'' = S' + η·C(d')    ← correction proportional to new measurement

This is GRADIENT DESCENT in frequency space.
The loss function is ι(σ(P), σ(S)).
We descend the inharmony gradient through continuous C/X/Z steps.
"""

import math, random, time, sys, os, copy
import numpy as np

random.seed(42)
np.random.seed(42)

# ═══════════════════════════════════════════════════════════
# DECOMPOSER — maps any data to 72-band frequency space
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
# SAT DECOMPOSER — clause-aware variable mapping
# ═══════════════════════════════════════════════════════════

def decompose_sat(clauses, assignment, n_vars):
    """
    Decompose SAT problem and solution into clause-aware 72-band vectors.
    
    Each variable's contribution is weighted by the clauses it appears in.
    Clauses span multiple bands — the decomposition captures this structure.
    """
    prob = [0.0] * 72
    sol = [0.0] * 72
    
    prob_total = 0.0
    sol_total = 0.0
    
    # Build variable → clause index
    var_clauses = {v: [] for v in range(1, n_vars + 1)}
    for ci, clause in enumerate(clauses):
        for var, sign in clause:
            if 1 <= var <= n_vars:
                var_clauses[var].append((ci, sign))
    
    for v in range(1, n_vars + 1):
        if not var_clauses[v]:
            continue
        
        band = (v - 1) % 72
        
        # Problem: what does this variable need to do?
        pos_need = sum(1 for _, s in var_clauses[v] if s)     # needs True
        neg_need = sum(1 for _, s in var_clauses[v] if not s) # needs False
        prob_val = (pos_need - neg_need) / max(1, len(var_clauses[v]))
        prob[band] += prob_val
        prob_total += abs(prob_val)
        
        # Solution: what does the assignment say?
        if v in assignment:
            sol_val = 1.0 if assignment[v] else -1.0
        else:
            sol_val = 0.0
        sol[band] += sol_val
        sol_total += abs(sol_val)
    
    # Normalize
    if prob_total > 0:
        prob = [p / prob_total for p in prob]
    if sol_total > 0:
        sol = [s / sol_total for s in sol]
    
    return prob, sol

def count_satisfied(clauses, assignment):
    """Count satisfied clauses — correctly handling literal sign."""
    return sum(1 for c in clauses if any(
        (sign and assignment.get(var, False)) or
        (not sign and not assignment.get(var, True))
        for var, sign in c))

# ═══════════════════════════════════════════════════════════
# THE OUROBOROS — continuous gradient descent
# ═══════════════════════════════════════════════════════════

def ouroboros_sat(clauses, n_vars, 
                  max_steps=2000,
                  learning_rate=0.3,
                  verbose=True):
    """
    Solve SAT via continuous inharmony gradient descent.
    
    At each step:
      1. Decompose P and S → prob_sig, sol_sig
      2. Compute correction d = prob_sig - sol_sig  (THE MEASUREMENT)
      3. For the most misaligned band k:
         Flip variable(s) in band k toward the correction direction
         (THE CORRECTION = THE MEASUREMENT = THE SNAKE EATING ITS TAIL)
      4. Recompute — d changes because S changed
      5. Repeat — following the continuously changing gradient
    
    There is no "check if better, revert if not."
    Every step follows d. d guides. d IS the path.
    """
    nc = len(clauses)
    
    # Build variable → clause mapping and band groups
    vars_by_band = {k: [] for k in range(72)}
    var_sign_map = {}  # var → (pos_clauses, neg_clauses) counts
    
    for v in range(1, n_vars + 1):
        band = (v - 1) % 72
        vars_by_band[band].append(v)
        
        pos = sum(1 for c in clauses for lit_v, sign in c 
                  if lit_v == v and sign)
        neg = sum(1 for c in clauses for lit_v, sign in c 
                  if lit_v == v and not sign)
        var_sign_map[v] = (pos, neg)
    
    # Initial assignment
    assignment = {v: random.random() > 0.5 for v in range(1, n_vars + 1)}
    
    # Initial decomposition
    prob_sig, sol_sig = decompose_sat(clauses, assignment, n_vars)
    current_ih = inharmony(prob_sig, sol_sig)
    current_sat = count_satisfied(clauses, assignment)
    
    history = [{"step": 0, "inharmony": current_ih, "satisfied": current_sat}]
    
    if verbose:
        print(f"  Step    0: ι={current_ih:.6f}, sat={current_sat}/{nc}")
    
    # ── THE OUROBOROS LOOP ──
    for step in range(1, max_steps + 1):
        # 1. Compute correction vector d = σ(P) - σ(S)
        d = [(prob_sig[k] - sol_sig[k]) for k in range(72)]
        
        # 2. Find the most misaligned band
        bands_by_magnitude = sorted(range(72), key=lambda k: abs(d[k]), reverse=True)
        
        # 3. For the top misaligned band, flip the variable most out of alignment
        flipped = False
        for band in bands_by_magnitude:
            if not vars_by_band[band]:
                continue
            
            # For this band, which way does the correction point?
            correction_direction = d[band]  # positive = need more positive contribution
            magnitude = abs(correction_direction)
            
            if magnitude < 1e-6:
                continue
            
            # Score each variable: how much would flipping it correct this band?
            best_var = None
            best_gain = -float('inf')
            
            for v in vars_by_band[band]:
                current_val = 1.0 if assignment[v] else -1.0
                flipped_val = -current_val
                
                # The gain is how much closer to the correction direction we get
                gain = (flipped_val - current_val) * correction_direction
                
                # Also check clause satisfaction impact
                sat_before = sum(1 for c in clauses if any(
                    (sign and assignment.get(var)) or
                    (not sign and not assignment.get(var))
                    for var, sign in c))
                
                temp_assign = assignment.copy()
                temp_assign[v] = not temp_assign.get(v, False)
                sat_after = sum(1 for c in clauses if any(
                    (sign and temp_assign.get(var)) or
                    (not sign and not temp_assign.get(var))
                    for var, sign in c))
                sat_gain = sat_after - sat_before
                
                total_gain = gain * 0.3 + sat_gain * 0.7  # weighted toward satisfaction
                
                if total_gain > best_gain and total_gain > 0:
                    best_gain = total_gain
                    best_var = v
            
            if best_var is not None:
                # Flip the best variable
                assignment[best_var] = not assignment[best_var]
                flipped = True
                break  # One flip per step — follow the gradient smoothly
        
        # 4. Adaptive step: also flip a random variable in top misaligned band
        #    (stochasticity helps escape local inharmony minima)
        if step % 10 == 0 and len(bands_by_magnitude) > 0:
            explore_band = bands_by_magnitude[0]
            if vars_by_band[explore_band]:
                v = random.choice(vars_by_band[explore_band])
                assignment[v] = not assignment[v]
        
        # 5. Recompute — THE SNAKE EATS ITS TAIL
        prob_sig, sol_sig = decompose_sat(clauses, assignment, n_vars)
        new_ih = inharmony(prob_sig, sol_sig)
        new_sat = count_satisfied(clauses, assignment)
        
        # The inharmony IS the guide. It changes continuously.
        # We track it but don't use it to accept/reject.
        # Every flip IS the correction, and the correction IS the measurement.
        current_ih = new_ih
        current_sat = new_sat
        
        if step % 100 == 0:
            history.append({"step": step, "inharmony": current_ih, "satisfied": current_sat})
            if verbose:
                print(f"  Step {step:4d}: ι={current_ih:.6f}, sat={current_sat}/{nc} ({current_sat/nc*100:.0f}%)")
        
        # Perfect solution
        if current_sat == nc:
            history.append({"step": step, "inharmony": current_ih, "satisfied": current_sat})
            if verbose:
                print(f"  ✓ PERFECT at step {step}: ALL {nc} clauses satisfied!")
            break
    
    history.append({"step": min(step, max_steps), "inharmony": current_ih, "satisfied": current_sat})
    return assignment, current_sat, history

# ═══════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("THE OUROBOROS — WAVELENGTH CONVERGENCE ENGINE")
    print("The snake that eats its tail")
    print("=" * 70)
    print()
    print("  σ(P) − σ(S) = d       ← measurement")
    print("  S' = S + C(d)         ← correction (= measurement)")
    print("  σ(P) − σ(S') = d'     ← new measurement (= new correction)")
    print("  S'' = S' + C(d')      ← snake follows its tail")
    print()
    
    configs = [
        (20, 84, 500, 0.3),
        (30, 126, 1000, 0.25),
        (50, 210, 2000, 0.2),
        (100, 420, 3000, 0.15),
    ]
    
    all_results = []
    
    for nv, nc, max_steps, lr in configs:
        print(f"{'─'*70}")
        print(f"SAT: {nv} vars, {nc} clauses (ratio={nc/nv:.1f})")
        print(f"{'─'*70}")
        
        clauses = [[(random.randint(1, nv), random.choice([True, False]))
                    for _ in range(3)] for _ in range(nc)]
        
        # Baselines
        from vedic_planetary_transformers import MercurialClauseWeaver
        t0 = time.time()
        vedic = MercurialClauseWeaver(clauses, nv).solve()
        vedic_ms = (time.time() - t0) * 1000
        vedic_sat = count_satisfied(clauses, vedic)
        
        rand_sat = count_satisfied(clauses, 
            {i+1: random.random() > 0.5 for i in range(nv)})
        
        print(f"  Random baseline:  {rand_sat}/{nc} ({rand_sat/nc*100:.0f}%)")
        print(f"  Vedic (Set):      {vedic_sat}/{nc} ({vedic_sat/nc*100:.0f}%) in {vedic_ms:.0f}ms")
        
        # Ouroboros
        print(f"\n  OUROBOROS (η={lr}, max {max_steps} steps):")
        t0 = time.time()
        assign, sat, history = ouroboros_sat(
            clauses, nv, max_steps=max_steps, learning_rate=lr, verbose=True
        )
        ouro_ms = (time.time() - t0) * 1000
        
        ih_start = history[0]["inharmony"]
        ih_end = history[-1]["inharmony"]
        ih_red = (ih_start - ih_end) / max(ih_start, 1e-10) * 100
        
        best_sat = max(r["satisfied"] for r in history)
        
        print(f"\n  RESULTS:")
        print(f"    Random:      {rand_sat}/{nc} ({rand_sat/nc*100:.0f}%)")
        print(f"    Vedic:       {vedic_sat}/{nc} ({vedic_sat/nc*100:.0f}%)")
        print(f"    Ouroboros:   {sat}/{nc} ({sat/nc*100:.0f}%) in {ouro_ms:.0f}ms")
        print(f"    Best during: {best_sat}/{nc} ({best_sat/nc*100:.0f}%)")
        print(f"    ι: {ih_start:.6f} → {ih_end:.6f} ({ih_red:.1f}% reduction)")
        
        all_results.append({
            "nv": nv, "nc": nc,
            "random": rand_sat, "vedic": vedic_sat,
            "ouroboros": sat, "best_during": best_sat,
            "ih_start": ih_start, "ih_end": ih_end,
            "ih_reduction": ih_red,
            "steps": len(history), "time_ms": ouro_ms,
        })
    
    # Summary
    print("\n" + "=" * 70)
    print("OUROBOROS SUMMARY")
    print("=" * 70)
    print(f"{'Vars':>5s} {'Random':>7s} {'Vedic':>7s} {'Ouroboros':>11s} {'Best':>7s} {'ι_red':>8s} {'Steps':>6s}")
    print("-" * 70)
    for r in all_results:
        ou_str = f"{r['ouroboros']}/{r['nc']} ({r['ouroboros']/r['nc']*100:.0f}%)"
        best_str = f"{r['best_during']}/{r['nc']} ({r['best_during']/r['nc']*100:.0f}%)"
        print(f"{r['nv']:5d} {r['random']:4d}/{r['nc']} {r['vedic']:4d}/{r['nc']} {ou_str:>11s} {best_str:>7s} {r['ih_reduction']:6.1f}% {r['steps']:5d}")
    
    print(f"\n  The snake eats its tail.")
    print(f"  ι(σ(P), σ(S)) IS the correction instruction.")
    print(f"  The correction changes σ(S), which changes the instruction.")
    print(f"  Follow the Ouroboros → convergence.")
