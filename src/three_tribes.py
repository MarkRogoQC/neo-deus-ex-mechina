#!/usr/bin/env python3
"""
THREE TRIBES SOLVER
═══════════════════════════════════════════════════════════
Egyptian pipeline + Indus math + Norse destruction.

Shiva — destroy and rebuild
Odin — sacrifice best to learn
Fenrir — break constraints
Kali — kill attachment
Inanna — strip to core
Saraswati — remember
Mitra — detect contracts
"""

import math, random, time, numpy as np, sys
random.seed(42); np.random.seed(42)

from vedic_planetary_transformers import MercurialClauseWeaver
from pysat.solvers import Glucose3

def sat(clauses, assign):
    return sum(1 for c in clauses if any(
        (s and assign.get(v,0)) or (not s and not assign.get(v,1)) for v,s in c))

def vedic_solve(clauses, nv, seeds=10):
    best_s, best_a = 0, None
    for seed in range(seeds):
        a = MercurialClauseWeaver(clauses, nv, seed=seed).solve()
        s = sat(clauses, a)
        if s > best_s: best_s, best_a = s, a
    return best_a, best_s

def exhaustive_polish(clauses, assign, passes=5):
    best_a = assign.copy()
    best_s = sat(clauses, assign)
    for _ in range(passes):
        improved = False
        for v in range(1, max(abs(l) for c in clauses for l,_ in c) + 1):
            if v not in best_a: continue
            best_a[v] = not best_a[v]
            ns = sat(clauses, best_a)
            if ns > best_s: best_s = ns; improved = True
            else: best_a[v] = not best_a[v]
        if not improved: break
    return best_a, best_s

def shiva_destroy(nv):
    """Shiva: total annihilation. Random restart from nothing."""
    return {v: random.random() > 0.5 for v in range(1, nv+1)}

def odin_sacrifice(clauses, best_assign, best_sat, nv):
    """Odin: hang the best solution. Extract what CANNOT be from contradiction."""
    n = max(abs(l) for c in clauses for l,_ in c)
    # Find variables where flipping improves — those are the sacrifices
    sacrificed = []
    for v in range(1, n+1):
        temp = best_assign.copy()
        temp[v] = not temp.get(v,0)
        ns = sat(clauses, temp)
        if ns >= best_sat:  # doesn't hurt — sacrifice it
            sacrificed.append(v)
    # Return with Odin's wisdom: a new assignment with sacrificed variables flipped
    new_a = best_assign.copy()
    for v in sacrificed[:max(1, len(sacrificed)//5)]:
        new_a[v] = not new_a.get(v,0)
    return new_a

def fenrir_unbind(clauses, assign):
    """Fenrir: remove most constraining clauses, solve, reintroduce."""
    unsat_c = [c for c in clauses if not any(
        (s and assign.get(v,0)) or (not s and not assign.get(v,1)) for v,s in c)]
    if not unsat_c: return assign
    
    # Remove clauses with most variables in unsat set
    unsat_vars = set(v for c in unsat_c for v,_ in c)
    constraining = []
    for ci, c in enumerate(clauses):
        overlap = len(set(v for v,_ in c) & unsat_vars)
        if overlap > 0:
            constraining.append((ci, overlap))
    constraining.sort(key=lambda x: -x[1])
    
    # Remove top 10% most constraining, solve without them
    remove_n = max(1, len(constraining) // 10)
    kept = [c for i, c in enumerate(clauses) if i not in 
            set(ci for ci, _ in constraining[:remove_n])]
    
    # Solve reduced problem
    nv = max(abs(l) for c in kept for l,_ in c) if kept else 1
    best_a, _ = vedic_solve(kept, nv)
    return best_a

def kali_ego_death(best_assign, nv):
    """Kali: kill the ego. Destroy 50% of what the solver loves."""
    new_a = best_assign.copy()
    all_vars = list(range(1, nv+1))
    random.shuffle(all_vars)
    for v in all_vars[:nv//2]:
        new_a[v] = not new_a.get(v,0)
    return new_a

def inanna_descent(clauses, assign, nv):
    """Inanna: strip one variable class at a time. Return from the core."""
    best_a = assign.copy()
    best_s = sat(clauses, best_a)
    
    # Categorize variables by their unsat clause involvement
    unsat = [c for c in clauses if not any(
        (s and assign.get(v,0)) or (not s and not assign.get(v,1)) for v,s in c)]
    var_count = {}
    for c in unsat:
        for v,_ in c: var_count[v] = var_count.get(v,0) + 1
    
    # Sort by involvement, strip one group at a time
    by_count = sorted(var_count.items(), key=lambda x: -x[1])
    
    for (v, _) in by_count[:min(len(by_count), nv//5)]:
        temp = best_a.copy()
        temp[v] = not temp.get(v,0)
        ns = sat(clauses, temp)
        if ns > best_s:
            best_s = ns; best_a = temp
    
    return best_a, best_s == len(clauses)

def saraswati_remember(history, nv):
    """Saraswati: learn from history. Majority vote on variable preferences."""
    if len(history) < 3: return None
    votes = {v: {True: 0, False: 0} for v in range(1, nv+1)}
    for _, assign, score in history[-10:]:
        weight = score / max(1, sum(s for _,_,s in history[-10:]) / len(history[-10:]))
        for v in range(1, nv+1):
            votes[v][assign.get(v,0)] += weight
    
    # Return majority-preferred assignment
    return {v: True if votes[v][True] > votes[v][False] else False 
            for v in range(1, nv+1)}

# ═══════════════════════════════════════════════════════════
# THREE TRIBES SOLVER
# ═══════════════════════════════════════════════════════════

def three_tribes_solve(clauses, max_cycles=50, verbose=True):
    nc = len(clauses)
    nv = max(abs(l) for c in clauses for l,_ in c)
    
    # Egyptian pipeline: get to 97%
    best_a, best_s = vedic_solve(clauses, nv, seeds=30)
    best_a, best_s = exhaustive_polish(clauses, best_a, passes=10)
    
    history = [(0, best_a.copy(), best_s)]
    
    if verbose:
        print(f"  Egyptian: {best_s}/{nc} ({best_s/nc*100:.0f}%)")
    
    stall_count = 0
    
    for cycle in range(1, max_cycles + 1):
        if best_s == nc: break
        
        intervention = "none"
        result_s = best_s
        
        # Norse interventions — apply in rotation based on stall
        if stall_count % 6 == 0:
            # SHIVA: total destruction
            chaos = shiva_destroy(nv)
            new_a, new_s = vedic_solve(clauses, nv, seeds=10)
            new_a, new_s = exhaustive_polish(clauses, new_a)
            if new_s > result_s: result_s = new_s; best_a = new_a; intervention = "Shiva"
        
        elif stall_count % 6 == 1:
            # ODIN: sacrifice to gain wisdom
            new_a = odin_sacrifice(clauses, best_a, best_s, nv)
            new_a, new_s = exhaustive_polish(clauses, new_a)
            if new_s > result_s: result_s = new_s; best_a = new_a; intervention = "Odin"
        
        elif stall_count % 6 == 2:
            # FENRIR: break chains
            new_a = fenrir_unbind(clauses, best_a)
            new_a, new_s = exhaustive_polish(clauses, new_a)
            if new_s > result_s: result_s = new_s; best_a = new_a; intervention = "Fenrir"
        
        elif stall_count % 6 == 3:
            # KALI: kill attachment
            new_a = kali_ego_death(best_a, nv)
            new_a, new_s = vedic_solve(clauses, nv, seeds=5)
            new_a, new_s = exhaustive_polish(clauses, new_a)
            if new_s > result_s: result_s = new_s; best_a = new_a; intervention = "Kali"
        
        elif stall_count % 6 == 4:
            # INANNA: strip to core
            new_a, _ = inanna_descent(clauses, best_a, nv)
            new_s = sat(clauses, new_a)
            if new_s > result_s: result_s = new_s; best_a = new_a; intervention = "Inanna"
        
        elif stall_count % 6 == 5:
            # SARASWATI: remember
            new_a = saraswati_remember(history, nv)
            if new_a:
                new_a, new_s = exhaustive_polish(clauses, new_a)
                if new_s > result_s: result_s = new_s; best_a = new_a; intervention = "Saraswati"
        
        if result_s > best_s:
            best_s = result_s
            stall_count = 0
            if verbose and best_s > history[-1][2]:
                print(f"  {intervention} cycle {cycle}: {best_s}/{nc} ({best_s/nc*100:.0f}%)")
        else:
            stall_count += 1
        
        history.append((cycle, best_a.copy(), best_s))
        
        if stall_count > 30: break
    
    if verbose:
        perf = "✓ PERFECT" if best_s == nc else f"gap={nc-best_s}"
        print(f"  Final: {best_s}/{nc} ({best_s/nc*100:.0f}%), cycles={cycle} — {perf}")
    
    return best_a, best_s, history


# ═══════════════════════════════════════════════════════════
# BENCHMARK
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import importlib
    
    print("THREE TRIBES: Egyptian + Indus + Norse")
    print("=" * 60)
    
    for nv, nc in [(50,210), (100,420), (150,630)]:
        clauses = [[(random.randint(1, nv), random.choice([True, False]))
                    for _ in range(3)] for _ in range(nc)]
        
        g = Glucose3()
        for c in clauses: g.add_clause([v if s else -v for v,s in c])
        is_sat = g.solve(); g.delete()
        
        t0 = time.time()
        assign, s, hist = three_tribes_solve(clauses, max_cycles=30, verbose=True)
        ms = (time.time() - t0) * 1000
        
        status = "SAT" if is_sat else "UNSAT"
        perf = "✓" if s == nc else f"gap={nc-s}"
        print(f"  {nv}v/{nc}c ({status}): {s}/{nc} ({s/nc*100:.0f}%), {ms:.0f}ms — {perf}\n")
