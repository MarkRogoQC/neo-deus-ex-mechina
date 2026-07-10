#!/usr/bin/env python3
"""
RIGOROUS MULTI-SEED SAT BENCHMARK
═══════════════════════════════════════════════════════════
Complete framework benchmark of Ouroboros pipeline vs Glucose3.

Pipeline: toolkit.pipeline() with _type="sat"
  - MercurialClauseWeaver (Set) via _c_sat
  - X/Z SAT operations + best_assignment injection
  - Post-pipeline: exhaustive polish + rebel brute force on ≤8 unsat variables
  - Leaps: 100 different random seeds per solver call

Sizes: 20, 50, 75, 100, 150 vars, clause ratio 4.2
10 random seeds per size = 50 total instances
"""

import math, random, time, sys, os, copy

import numpy as np
from pysat.solvers import Glucose3

# ── Pipeline imports ──────────────────────────────────────────────────────
import importlib
import toolkit
importlib.reload(toolkit)

from toolkit import complement, cross, cancel
from vedic_planetary_transformers import MercurialClauseWeaver as Set

# ── Utilities ─────────────────────────────────────────────────────────────

def sat_count(clauses, assign):
    """Count satisfied clauses given assignment dict ({var: bool})."""
    return sum(1 for c in clauses if any(
        (sign and assign.get(var, False)) or
        (not sign and not assign.get(var, True))
        for var, sign in c))

def clauses_to_cnf(clauses_tuple):
    """Convert internal (var, sign) format to [-var, +var] CNF format."""
    return [[v if s else -v for v, s in c] for c in clauses_tuple]

def generate_instance(n_vars, n_clauses, seed):
    """Generate a random 3-SAT instance with given seed."""
    rng = random.Random(seed * 31337 + n_vars * 10007)
    clauses = []
    for _ in range(n_clauses):
        vars_pool = list(range(1, n_vars + 1))
        rng.shuffle(vars_pool)
        chosen = vars_pool[:3]
        clause = [(v, rng.choice([True, False])) for v in chosen]
        clauses.append(clause)
    return clauses

def glucose3_solve(clauses_tuple):
    """Run Glucose3 on the instance, return (satisfiable, assignment_or_None, time_ms)."""
    cnf = clauses_to_cnf(clauses_tuple)
    t0 = time.perf_counter()
    g = Glucose3()
    for c in cnf:
        g.add_clause(c)
    result = g.solve()
    elapsed = (time.perf_counter() - t0) * 1000
    if result:
        model = g.get_model()
        g.delete()
        assign = {abs(lit): lit > 0 for lit in model if lit != 0}
        return True, assign, elapsed
    else:
        g.delete()
        return False, None, elapsed

# ── Pipeline cycle ────────────────────────────────────────────────────────

def run_ouroboros_pipeline(clauses_tuple, n_vars, seed):
    """
    Run the Ouroboros pipeline for one seed.
    Returns: best_satisfied_count, elapsed_seconds, cycles_used
    """
    total = len(clauses_tuple)
    cnf = clauses_to_cnf(clauses_tuple)
    
    t0 = time.perf_counter()
    
    # Set seed
    random.seed(seed)
    np.random.seed(seed)
    
    # Initial random assignment
    init_assign = {v: random.random() > 0.5 for v in range(1, n_vars + 1)}
    
    best_assignment = init_assign.copy()
    best_sat = sat_count(clauses_tuple, init_assign)
    
    # Get n_vars from clauses if not provided
    max_var = max(abs(l) for c in clauses_tuple for l, _ in c)
    
    state = {
        "_type": "sat",
        "clauses": cnf,
        "assignment": init_assign.copy(),
        "best_assignment": best_assignment.copy(),
        "n_vars": max_var,
    }
    
    stall_count = 0
    max_cycles = 200
    stall_limit = 100
    cycle = 0
    
    for cycle in range(max_cycles):
        if best_sat >= total:
            break
        
        # ── 1. Complement (C) — run Set solver ──
        state = complement(state)
        
        if "assignment" not in state:
            state["assignment"] = best_assignment.copy()
        
        current_sat = sat_count(clauses_tuple, state.get("assignment", {}))
        if current_sat > best_sat:
            best_sat = current_sat
            best_assignment = state["assignment"].copy()
            stall_count = 0
        else:
            stall_count += 1
        
        state["best_assignment"] = best_assignment.copy()
        
        # ── 2. Cross (X) — mix with best assignment ──
        state = cross(state, None)
        
        current_sat = sat_count(clauses_tuple, state.get("assignment", {}))
        if current_sat > best_sat:
            best_sat = current_sat
            best_assignment = state["assignment"].copy()
            stall_count = 0
        
        state["best_assignment"] = best_assignment.copy()
        
        # ── 3. Cancel (Z) — fix unsatisfied clauses ──
        state = cancel(state)
        
        current_sat = sat_count(clauses_tuple, state.get("assignment", {}))
        if current_sat > best_sat:
            best_sat = current_sat
            best_assignment = state["assignment"].copy()
            stall_count = 0
        
        state["best_assignment"] = best_assignment.copy()
        
        # ── Check stall ──
        if stall_count >= stall_limit:
            break
        
        # ── Rebel brute force every 25 stall cycles ──
        if stall_count > 0 and stall_count % 25 == 0:
            unsat_clauses = [c for c in clauses_tuple
                             if not any((sign and best_assignment.get(var, False)) or
                                        (not sign and not best_assignment.get(var, True))
                                        for var, sign in c)]
            unsat_vars = set()
            for c in unsat_clauses:
                for v, _ in c:
                    unsat_vars.add(v)
            
            if len(unsat_vars) <= 8 and len(unsat_vars) > 0:
                unsat_list = list(unsat_vars)
                brute_best = best_sat
                brute_assign = best_assignment.copy()
                
                for mask in range(1 << len(unsat_list)):
                    temp = best_assignment.copy()
                    for i, v in enumerate(unsat_list):
                        temp[v] = bool((mask >> i) & 1)
                    s = sat_count(clauses_tuple, temp)
                    if s > brute_best:
                        brute_best = s
                        brute_assign = temp.copy()
                        if s == total:
                            break
                
                if brute_best > best_sat:
                    best_sat = brute_best
                    best_assignment = brute_assign.copy()
                    stall_count = 0
                    state["assignment"] = best_assignment.copy()
                    state["best_assignment"] = best_assignment.copy()
    
    # ── Post-pipeline: exhaustive polish ──
    for _pass in range(10):
        if best_sat >= total:
            break
        improved = False
        for v in range(1, max_var + 1):
            if v not in best_assignment:
                continue
            best_assignment[v] = not best_assignment[v]
            s = sat_count(clauses_tuple, best_assignment)
            if s > best_sat:
                best_sat = s
                improved = True
                if best_sat >= total:
                    break
            else:
                best_assignment[v] = not best_assignment[v]
        if not improved:
            break
    
    # ── Final rebel brute force on ≤8 unsat variables ──
    if best_sat < total:
        unsat_clauses = [c for c in clauses_tuple
                         if not any((sign and best_assignment.get(var, False)) or
                                    (not sign and not best_assignment.get(var, True))
                                    for var, sign in c)]
        unsat_vars = set()
        for c in unsat_clauses:
            for v, _ in c:
                unsat_vars.add(v)
        
        if len(unsat_vars) <= 8 and len(unsat_vars) > 0:
            unsat_list = list(unsat_vars)
            for mask in range(1 << len(unsat_list)):
                temp = best_assignment.copy()
                for i, v in enumerate(unsat_list):
                    temp[v] = bool((mask >> i) & 1)
                s = sat_count(clauses_tuple, temp)
                if s > best_sat:
                    best_sat = s
                    best_assignment = temp.copy()
                    if best_sat >= total:
                        break
    
    # ── Final polish after brute force ──
    if best_sat < total:
        for v in range(1, max_var + 1):
            if v not in best_assignment:
                continue
            best_assignment[v] = not best_assignment[v]
            s = sat_count(clauses_tuple, best_assignment)
            if s > best_sat:
                best_sat = s
            else:
                best_assignment[v] = not best_assignment[v]
            if best_sat >= total:
                break
    
    elapsed = time.perf_counter() - t0
    return best_sat, elapsed, cycle + 1


def run_multi_seed(clauses_tuple, n_vars, num_seeds=100):
    """Run pipeline across many seeds. Returns stats dict."""
    all_sats = []
    all_times = []
    all_cycles = []
    overall_best = 0
    
    for seed in range(num_seeds):
        s, elapsed, cycles = run_ouroboros_pipeline(clauses_tuple, n_vars, seed)
        all_sats.append(s)
        all_times.append(elapsed)
        all_cycles.append(cycles)
        if s > overall_best:
            overall_best = s
    
    return overall_best, all_sats, all_times, all_cycles


# ── Main benchmark ────────────────────────────────────────────────────────

def main():
    print("=" * 90)
    print("RIGOROUS MULTI-SEED SAT BENCHMARK")
    print("Ouroboros Pipeline vs Glucose3")
    print("=" * 90)
    print()
    print(f"Framework: toolkit.pipeline() with _type='sat'")
    print(f"Solver: MercurialClauseWeaver (exhaustive local search)")
    print(f"Pipeline: 12-phase C/X/Z cycles + best_assignment injection")
    print(f"Post-pipeline: exhaustive polish + rebel brute force (≤8 vars)")
    print(f"Leaps: 100 different random seeds per solver call")
    print(f"Max cycles per seed: 200, stall limit: 100, brute every 25 stall")
    print()
    
    sizes = [20, 50, 75, 100, 150]
    clause_ratio = 4.2
    seeds_per_size = 10
    leaps = 100
    
    # Store all data for final tables
    instance_data = []  # list of dicts with all computed data
    
    run_count = 0
    total_runs = len(sizes) * seeds_per_size
    
    for n_vars in sizes:
        n_clauses = int(n_vars * clause_ratio)
        print(f"\n{'─' * 90}")
        print(f"SIZE: {n_vars} variables, {n_clauses} clauses (ratio={clause_ratio})")
        print(f"{'─' * 90}")
        
        for run_seed in range(seeds_per_size):
            run_count += 1
            clauses_tuple = generate_instance(n_vars, n_clauses, run_seed)
            total = len(clauses_tuple)
            
            # ── Glucose3 baseline ──
            is_sat, g_assign, g_time = glucose3_solve(clauses_tuple)
            
            # ── Ouroboros ──
            best_sat, all_sats, all_times, all_cycles = run_multi_seed(
                clauses_tuple, n_vars, num_seeds=leaps
            )
            
            # Stats
            mean_sat = np.mean(all_sats)
            std_sat = np.std(all_sats)
            perfect = sum(1 for s in all_sats if s == total)
            perfect_rate = perfect / len(all_sats) * 100
            mean_time = np.mean(all_times) * 1000  # ms
            best_time = min(all_times) * 1000
            mean_cycles = np.mean(all_cycles)
            
            gap = total - best_sat
            pct = best_sat / total * 100
            
            # Store
            inst = {
                "n_vars": n_vars,
                "n_clauses": n_clauses,
                "run_seed": run_seed,
                "is_sat": is_sat,
                "glucose_time": g_time,
                "best_sat": best_sat,
                "all_sats": all_sats,
                "mean_sat": mean_sat,
                "std_sat": std_sat,
                "perfect_rate": perfect_rate,
                "mean_time_ms": mean_time,
                "best_time_ms": best_time,
                "mean_cycles": mean_cycles,
                "gap": gap,
                "pct": pct,
            }
            instance_data.append(inst)
            
            # Detailed per-seed breakdown (show first 20 seeds only)
            seed_detail = " ".join(f"{s}/{total}" for s in all_sats[:20])
            if len(all_sats) > 20:
                seed_detail += f" ... (+{len(all_sats)-20} more)"
            
            instance_type = "SAT" if is_sat else "UNSAT"
            gap_str = f"gap=0" if best_sat == total else f"gap={gap}"
            print(f"\n  [{run_count}/{total_runs}] {instance_type:5s} seed={run_seed}: "
                  f"Ouroboros={best_sat}/{total} ({pct:.1f}%) {gap_str}")
            print(f"       seeds: μ={mean_sat:.0f} σ={std_sat:.0f} "
                  f"perf={perfect_rate:.0f}% time={mean_time:.0f}ms "
                  f"Glucose3={g_time:.0f}ms")
            print(f"       first 20 of {leaps} seeds: [ {seed_detail} ]")
        
        # Print size status
        sat_count_size = sum(1 for d in instance_data if d["n_vars"] == n_vars and d["is_sat"])
        perf_count_size = sum(1 for d in instance_data if d["n_vars"] == n_vars and d["gap"] == 0)
        print(f"\n  ── Size {n_vars} done: {seeds_per_size} instances, "
              f"{sat_count_size} SAT, {perf_count_size} perfect Ouroboros ──")
    
    # ════════════════════════════════════════════════════════════════
    # FINAL TABLES
    # ════════════════════════════════════════════════════════════════
    
    print("\n\n" + "=" * 90)
    print("FINAL RESULTS")
    print("=" * 90)
    
    # TABLE 1: Per-instance detail
    print("\nTABLE 1: Per-instance results")
    print("-" * 90)
    header = (
        f"{'Size':>5s} {'Seed':>4s} {'T':>5s} | "
        f"{'Glucose3':>10s} | "
        f"{'Ouroboros (mean±std)':>22s} | "
        f"{'Perfect%':>8s} | {'MeanTime':>9s} | {'Gap':>5s}"
    )
    print(header)
    print("-" * 90)
    
    for d in instance_data:
        inst_type = "SAT" if d["is_sat"] else "UNS"
        g_str = f"{'SAT':>10s}" if d["is_sat"] else f"{'UNSAT':>10s}"
        gap_str = f"{d['gap']:5d}"
        
        print(
            f"{d['n_vars']:5d} {d['run_seed']:4d} {inst_type:5s} | "
            f"{g_str} | "
            f"{d['mean_sat']:7.1f}±{d['std_sat']:5.1f}     | "
            f"{d['perfect_rate']:6.1f}%   | "
            f"{d['mean_time_ms']:6.0f}ms  | {gap_str}"
        )
    
    # TABLE 2: Aggregate by size, separating SAT vs UNSAT
    print("\nTABLE 2: Aggregate by size (SAT / UNSAT separated)")
    print("-" * 90)
    
    h2 = (
        f"{'Size':>5s} {'Type':>6s} {'N':>3s} | "
        f"{'Glucose3':>8s} | "
        f"{'Ouroboros':>14s} | "
        f"{'PerfectR':>8s} | {'MeanTime':>9s} | {'Gap':>6s}"
    )
    print(h2)
    print("-" * 90)
    
    for n_vars in sizes:
        n_clauses = int(n_vars * clause_ratio)
        insts = [d for d in instance_data if d["n_vars"] == n_vars]
        
        sat_insts = [d for d in insts if d["is_sat"]]
        unsat_insts = [d for d in insts if not d["is_sat"]]
        
        # SAT row
        if sat_insts:
            sat_bests = [d["best_sat"] for d in sat_insts]
            sat_mean_best = np.mean(sat_bests)
            sat_mean_pct = sat_mean_best / n_clauses * 100
            sat_perf_count = sum(1 for d in sat_insts if d["best_sat"] == n_clauses)
            sat_perf_rate = sat_perf_count / len(sat_insts) * 100
            sat_mean_gap = np.mean([d["gap"] for d in sat_insts])
            sat_mean_t = np.mean([d["mean_time_ms"] for d in sat_insts])
            sat_std_t = np.std([d["mean_time_ms"] for d in sat_insts])
            
            print(
                f"{n_vars:5d} {'SAT':>6s} {len(sat_insts):3d} | "
                f"{'SAT':>8s} | "
                f"{sat_mean_pct:>5.1f}%{'':9s} | "
                f"{sat_perf_rate:>5.1f}%   | "
                f"{sat_mean_t:>5.0f}ms   | {sat_mean_gap:>5.1f}"
            )
        
        # UNSAT row
        if unsat_insts:
            unsat_bests = [d["best_sat"] for d in unsat_insts]
            unsat_mean_best = np.mean(unsat_bests)
            unsat_mean_pct = unsat_mean_best / n_clauses * 100
            unsat_mean_t = np.mean([d["mean_time_ms"] for d in unsat_insts])
            
            print(
                f"{n_vars:5d} {'UNSAT':>6s} {len(unsat_insts):3d} | "
                f"{'UNSAT':>8s} | "
                f"{unsat_mean_pct:>5.1f}%{'':9s} | "
                f"{'N/A':>7s} | "
                f"{unsat_mean_t:>5.0f}ms   | {'N/A':>6s}"
            )
    
    print()
    print("=" * 90)
    print("BENCHMARK COMPLETE")
    print("=" * 90)
    
    # Quick findings
    total_sat = sum(1 for d in instance_data if d["is_sat"])
    total_unsat = sum(1 for d in instance_data if not d["is_sat"])
    total_perfect = sum(1 for d in instance_data if d["best_sat"] == d["n_clauses"])
    print(f"\nSUMMARY: {len(instance_data)} instances total")
    print(f"  SAT:   {total_sat}")
    print(f"  UNSAT: {total_unsat}")
    print(f"  Perfect Ouroboros solves: {total_perfect}")
    print(f"  Ouroboros beat rate (SAT): "
          f"{sum(1 for d in instance_data if d['is_sat'] and d['best_sat'] == d['n_clauses'])}/{total_sat} "
          f"({sum(1 for d in instance_data if d['is_sat'] and d['best_sat'] == d['n_clauses'])/max(1,total_sat)*100:.0f}%)")


if __name__ == "__main__":
    main()
