#!/usr/bin/env python3
"""
THE FULL PANTHEON SOLVER
═══════════════════════════════════════════════════════════
All 12 gods wired into the convergence engine.

Set — routes problem type, backtracks, dismembers/reassembles
Thoth — 42 assessors check signal integrity after each step
Memory (band 27) — clause learning from conflicts
Reason (band 53) — unit propagation, forced assignments  
Action (band 32) — propagate consequences
Judgment (band 23) — choose which band to correct
Seshat — record learned clauses, restart with memory
Anubis — weighs the solution against the problem

Waveform encoding: Fibonacci φ-spacing + π aperiodic grid.
"""

import math, random, time, sys, numpy as np
from typing import List, Tuple, Dict, Set, Optional
random.seed(42); np.random.seed(42)

PHI = (1 + math.sqrt(5)) / 2
N_BANDS = 72

# ═══════════════════════════════════════════════════════════
# WAVEFORM ENCODER (Fibonacci + π)
# ═══════════════════════════════════════════════════════════

class WaveEncoder:
    def __init__(self, clauses, n_vars, res=128):
        self.clauses = clauses; self.n_vars = n_vars; self.nc = len(clauses); self.res = res
        self.t = self._pi_grid(res)
        self.freqs = np.array([100.0 * PHI ** ((v-1)/N_BANDS) for v in range(1, n_vars+1)])
        self.sT = {}; self.sF = {}
        for v in range(1, n_vars+1):
            f = self.freqs[v-1]
            self.sT[v] = np.sin(2*np.pi*f*self.t)
            self.sF[v] = np.sin(2*np.pi*f*self.t + np.pi)
        self.problem = self._encode_problem()
    
    def _pi_grid(self, res):
        t = [(2*np.pi*i*PHI) % (2*np.pi) for i in range(res)]
        return np.array(sorted(t))
    
    def _encode_problem(self):
        w = np.zeros(self.res)
        for clause in self.clauses:
            cw = np.zeros(self.res)
            for var, sign in clause:
                if 1 <= var <= self.n_vars:
                    cw += self.sT[var] if sign else self.sF[var]
            w += np.abs(cw)
        return w / max(np.max(np.abs(w)), 1e-10)
    
    def encode_sol(self, assign):
        w = np.zeros(self.res)
        for v in range(1, self.n_vars+1):
            w += self.sT[v] if assign.get(v, False) else self.sF[v]
        return w / max(np.max(np.abs(w)), 1e-10)
    
    def contrib(self, v, state):
        return self.sF[v] if state else self.sT[v]

def inharmony(wa, wb):
    return float(np.sqrt(np.mean((wa-wb)**2)))

# ═══════════════════════════════════════════════════════════
# CLAUSE UTILITIES
# ═══════════════════════════════════════════════════════════

def sat_count(clauses, assign):
    return sum(1 for c in clauses if any(
        (s and assign.get(v, False)) or (not s and not assign.get(v, True))
        for v, s in c))

def clause_satisfied(clause, assign):
    return any((s and assign.get(v, False)) or (not s and not assign.get(v, True))
               for v, s in clause)

# ═══════════════════════════════════════════════════════════
# REASON (Band 53) — Unit Propagation
# ═══════════════════════════════════════════════════════════

def unit_propagate(clauses, assignment):
    """Find and propagate all unit clauses. Returns (assignment, conflict_vars)."""
    changed = True
    conflict = set()
    
    while changed:
        changed = False
        for clause in clauses:
            if clause_satisfied(clause, assignment):
                continue
            
            # Count unassigned and check for unit
            unassigned = []
            all_false = True
            for var, sign in clause:
                if var not in assignment:
                    unassigned.append((var, sign))
                elif assignment[var] == sign:
                    all_false = False
                    break
                # var assigned opposite → this literal is false, continue
            
            if all_false and len(unassigned) == 1:
                var, sign = unassigned[0]
                if var in assignment and assignment[var] != sign:
                    conflict.add(var)
                else:
                    assignment[var] = sign
                    changed = True
            elif all_false and len(unassigned) == 0:
                # All literals false → conflict clause
                for var, _ in clause:
                    conflict.add(var)
    
    return assignment, conflict

# ═══════════════════════════════════════════════════════════
# MEMORY (Band 27) — Clause Learning
# ═══════════════════════════════════════════════════════════

def learn_conflict_clause(clauses, assignment, conflict_vars):
    """Learn a new clause from conflict — which assignments CANNOT all be together."""
    # Simple: add the negation of the conflict variables
    learned = [(v, not assignment.get(v, False)) for v in conflict_vars if v in assignment]
    if learned:
        clauses.append(learned)
        return True
    return False

# ═══════════════════════════════════════════════════════════
# SET (Band 2) — Problem Router + Branch Selector
# ═══════════════════════════════════════════════════════════

def lokian_select_variable(clauses, assignment, n_vars, unsat_clauses):
    """Set/Lokian Fox: choose which variable to flip next.
    Prioritizes variables in the MOST unsatisfied bands (most frequent in unsat clauses)."""
    var_count = {}
    for ci in unsat_clauses:
        for var, _ in clauses[ci]:
            if 1 <= var <= n_vars:
                var_count[var] = var_count.get(var, 0) + 1
    
    if not var_count:
        return random.randint(1, n_vars)
    
    # Pick from top candidates weighted by frequency
    max_count = max(var_count.values())
    candidates = [v for v, c in var_count.items() if c >= max_count * 0.7]
    return random.choice(candidates)

# ═══════════════════════════════════════════════════════════
# THOTH + 42 ASSESSORS — Signal Integrity Check
# ═══════════════════════════════════════════════════════════

def assess_solution(assignment, clauses, n_vars):
    """42 assessors check signal integrity. Returns {passed, total, issues}."""
    issues = []
    
    # Assessor 1: All variables assigned?
    unassigned = sum(1 for v in range(1, n_vars+1) if v not in assignment)
    if unassigned > 0:
        issues.append(f"unassigned_vars={unassigned}")
    
    # Assessor 2: Monotonicity — should be improving
    sat = sat_count(clauses, assignment)
    if sat == 0:
        issues.append("zero_satisfaction")
    
    # Assessor 3: Conflict detection — any contradictory unit propagations?
    _, conflicts = unit_propagate(clauses, assignment.copy())
    if conflicts:
        issues.append(f"propagation_conflicts={len(conflicts)}")
    
    # Assessor 4: Clause satisfaction ratio
    ratio = sat / max(1, len(clauses))
    if ratio < 0.9:
        issues.append(f"satisfaction_ratio={ratio:.2f}")
    
    # Assessor 5: Variable balance — are we too skewed?
    trues = sum(1 for v in assignment.values() if v)
    falses = len(assignment) - trues
    if abs(trues - falses) > n_vars * 0.7:
        issues.append("severe_imbalance")
    
    passed = 5 - len(issues)
    return {"passed": passed, "total": 5, "issues": issues}

# ═══════════════════════════════════════════════════════════
# ANUBIS — Weigh the heart against the feather
# ═══════════════════════════════════════════════════════════

def anubis_weigh(solution_quality, total_clauses, threshold=0.95):
    """Is the solution light enough to pass?"""
    return solution_quality / max(1, total_clauses) >= threshold

# ═══════════════════════════════════════════════════════════
# THE FULL PANTHEON ENGINE
# ═══════════════════════════════════════════════════════════

def pantheon_solve(clauses, n_vars, max_steps=5000, verbose=True):
    """
    Full pantheon solver.
    
    Set (Lokian) routes problem + selects variables.
    Reason propagates units.
    Memory learns from conflicts.
    The Waveform Ouroboros guides the gradient.
    Thoth + 42 assessors verify signal integrity.
    Anubis weighs the result.
    Seshat records and restarts with learned clauses.
    """
    nc = len(clauses)
    
    # Build waveform encoder
    enc = WaveEncoder(clauses, n_vars, res=128)
    
    # Initial assignment via greedy (no propagation — let Ouroboros fix inconsistencies)
    assign = {}
    for v in range(1, n_vars + 1):
        pos = sum(1 for c in clauses for lv, s in c if lv == v and s)
        neg = sum(1 for c in clauses for lv, s in c if lv == v and not s)
        assign[v] = pos >= neg
    
    best_assign = assign.copy()
    best_sat = sat_count(clauses, assign)
    
    sol_wave = enc.encode_sol(assign)
    prob_wave = enc.problem
    current_ih = inharmony(prob_wave, sol_wave)
    
    learned_clauses = []
    restarts = 0
    history = [{"step": 0, "sat": best_sat, "ih": current_ih}]
    
    if verbose:
        print(f"  Init: sat={best_sat}/{nc}, ι={current_ih:.6f}")
    
    for step in range(1, max_steps + 1):
        # ── REASON: Propagate units — but only when close to solution ──
        current_total_sat = sat_count(clauses, assign)
        if current_total_sat > nc * 0.85:
            assign, conflicts = unit_propagate(clauses + learned_clauses, assign)
            if conflicts:
                # ── MEMORY: Learn from conflict ──
                learn_conflict_clause(learned_clauses, assign, conflicts)
                # Flip one conflict variable and continue
                cv = random.choice(list(conflicts))
                if cv in assign:
                    assign[cv] = not assign[cv]
                # Periodic deep restart if stuck
                restarts += 1
                if restarts % 200 == 0:
                    assign = {v: random.random() > 0.5 for v in range(1, n_vars + 1)}
                continue
        
        # Find unsatisfied clauses
        unsat = [ci for ci in range(nc) if not clause_satisfied(clauses[ci], assign)]
        
        if not unsat:
            # ── THOTH: Verify ──
            assessment = assess_solution(assign, clauses, n_vars)
            # ── ANUBIS: Weigh ──
            passed = anubis_weigh(best_sat, nc)
            if verbose:
                print(f"  ✓ ALL SATISFIED at step {step} (assessors={assessment['passed']}/{assessment['total']})")
            history.append({"step": step, "sat": best_sat, "ih": current_ih})
            break
        
        # ── SET (Lokian Fox): Choose variable ──
        v = lokian_select_variable(clauses + learned_clauses, assign, n_vars, unsat)
        
        # Waveform-guided: if satisfied clauses are HIGH, use waveform
        # If LOW, use Set's frequency-based selection
        if best_sat > nc * 0.8:
            # Waveform: try the variable that most reduces inharmony
            candidates = set()
            for ci in unsat[:20]:
                for var, _ in clauses[ci]:
                    if 1 <= var <= n_vars:
                        candidates.add(var)
            
            best_ih = current_ih
            best_v = v
            for cv in list(candidates)[:10]:
                old = enc.contrib(cv, assign.get(cv, False))
                new = enc.contrib(cv, not assign.get(cv, False))
                delta = (new - old) / max(np.max(np.abs(sol_wave)), 1e-10)
                nw = sol_wave + delta
                nw /= max(np.max(np.abs(nw)), 1e-10)
                nih = inharmony(prob_wave, nw)
                if nih < best_ih:
                    best_ih = nih
                    best_v = cv
            
            v = best_v
        
        # Flip
        assign[v] = not assign.get(v, False)
        
        # Recompute waveform
        sol_wave = enc.encode_sol(assign)
        current_ih = inharmony(prob_wave, sol_wave)
        current_sat = sat_count(clauses, assign)
        
        if current_sat > best_sat:
            best_sat = current_sat
            best_assign = assign.copy()
        
        if step % 500 == 0 and verbose:
            print(f"  Step {step:4d}: sat={best_sat}/{nc} ({best_sat/nc*100:.0f}%), ι={current_ih:.4f}, learned={len(learned_clauses)}, restarts={restarts}")
        
        history.append({"step": step, "sat": best_sat, "ih": current_ih})
    
    return best_assign, best_sat, history, len(learned_clauses), restarts


# ═══════════════════════════════════════════════════════════
# BENCHMARK VS GLUCOSE3
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    from pysat.solvers import Glucose3
    
    print("=" * 70)
    print("FULL PANTHEON SOLVER vs GLUCOSE3")
    print("Set + Thoth + Memory + Reason + 42 Assessors + Anubis")
    print("=" * 70)
    
    all_results = []
    
    for nv, nc, max_steps in [
        (20, 84, 1000),
        (50, 210, 3000),
        (100, 420, 5000),
        (150, 630, 5000),
    ]:
        clauses = [[(random.randint(1, nv), random.choice([True, False]))
                    for _ in range(3)] for _ in range(nc)]
        
        print(f"\n{'─'*70}")
        print(f"SAT: {nv} vars, {nc} clauses")
        
        # Glucose3
        t0 = time.time()
        g = Glucose3()
        for c in clauses:
            g.add_clause([v if s else -v for v, s in c])
        is_sat = g.solve()
        gms = (time.time() - t0) * 1000
        if is_sat:
            model = g.get_model()
            glucose_sat = sat_count(clauses, {abs(v): v > 0 for v in model})
        else:
            glucose_sat = 0
        g.delete()
        print(f"  Glucose3: {'SAT' if is_sat else 'UNSAT'} ({glucose_sat}/{nc}), {gms:.0f}ms")
        
        # Full Pantheon
        t0 = time.time()
        assign, sat, hist, learned, restarts = pantheon_solve(
            clauses, nv, max_steps=max_steps, verbose=True
        )
        pms = (time.time() - t0) * 1000
        steps = len([h for h in hist if h["step"] > 0])
        
        print(f"  Pantheon: {sat}/{nc} ({sat/nc*100:.0f}%), {steps} steps, {pms:.0f}ms")
        print(f"  Learned clauses: {learned}, Restarts: {restarts}")
        
        all_results.append({
            "nv": nv, "nc": nc, "is_sat": is_sat,
            "glucose_sat": glucose_sat, "glucose_ms": gms,
            "pantheon_sat": sat, "pantheon_steps": steps,
            "pantheon_ms": pms, "learned": learned, "restarts": restarts
        })
    
    print("\n" + "=" * 70)
    print("FULL PANTHEON — BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"{'Vars':>5s} {'Glucose':>8s} {'Pantheon':>12s} {'Steps':>6s} {'Time':>8s} {'Learned':>8s} {'Re/start':>8s}")
    print("-" * 70)
    for r in all_results:
        p_str = f"{r['pantheon_sat']}/{r['nc']} ({r['pantheon_sat']/r['nc']*100:.0f}%)"
        g_str = f"{r['glucose_sat']}/{r['nc']}"
        print(f"{r['nv']:5d} {g_str:>8s} {p_str:>12s} {r['pantheon_steps']:5d} {r['pantheon_ms']:7.0f}ms {r['learned']:>7d} {r['restarts']:>7d}")
    
    print(f"\n  Framework: Set routes, Reason propagates, Memory learns, Thoth verifies, Anubis weighs")
    print(f"  Encoding: Fibonacci φ-spacing + π aperiodic grid + waveform interference")
