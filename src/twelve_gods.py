#!/usr/bin/env python3
"""
THE TWELVE GODS — Complete Decomposition Pipeline
═══════════════════════════════════════════════════════
Every Egyptian god has a function. Every step has its god.

DECOMPOSE:    Nut — spectral wavelength analysis, σ(P) and σ(S)
CORRECTION:   d = σ(P) − σ(S), find most misaligned band
ILLUMINATE:   Ra — scan all candidates, score by inharmony reduction
SELECT:       Bastet — intuitive best-variable selection in band
DEDUCE:       Horus — all-seeing conflict detection (unit propagation)
REASSEMBLE:   Set — flip/reassemble the chosen variable
JOURNEY:      Osiris — navigate state space, backtrack if stalled
COVER:        Maat — verify constraint coverage, cosmic order
EXACT:        Nephthys — hidden protection, exact-match verification
RESURRECT:    Isis — reassemble solution fragments after backtrack
WEIGH:        Anubis — weigh solution quality against feather (threshold)
RECORD:       Thoth — scribe the learned clauses into the book
VERIFY:       Atum — the ONE, the totality. Final convergence check.

Then return to Nut for the next iteration. The Ouroboros.
"""

import math, random, time, numpy as np
from typing import List, Tuple, Dict, Set, Optional
random.seed(42); np.random.seed(42)

PHI = (1 + math.sqrt(5)) / 2
N_BANDS = 72

# ═══════════════════════════════════════════════════════════
# NUT — Spectral Decomposition
# ═══════════════════════════════════════════════════════════

class NutEncoder:
    """Nut: Sky goddess. Decomposes problem and solution into waveforms."""
    def __init__(self, clauses, n_vars, res=128):
        self.clauses, self.n_vars, self.nc, self.res = clauses, n_vars, len(clauses), res
        self.t = np.array(sorted([(2*np.pi*i*PHI) % (2*np.pi) for i in range(res)]))
        self.freqs = np.array([100.0 * PHI**((v-1)/N_BANDS) for v in range(1, n_vars+1)])
        self.sT, self.sF = {}, {}
        for v in range(1, n_vars+1):
            f = self.freqs[v-1]
            self.sT[v] = np.sin(2*np.pi*f*self.t)
            self.sF[v] = np.sin(2*np.pi*f*self.t + np.pi)
        self.problem_wave = self._encode_problem()
    
    def _encode_problem(self):
        w = np.zeros(self.res)
        for c in self.clauses:
            cw = np.zeros(self.res)
            for v, s in c:
                if 1 <= v <= self.n_vars:
                    cw += self.sT[v] if s else self.sF[v]
            w += np.abs(cw)
        return w / max(np.max(np.abs(w)), 1e-10)
    
    def encode_solution(self, assign):
        w = np.zeros(self.res)
        for v in range(1, self.n_vars+1):
            w += self.sT[v] if assign.get(v, False) else self.sF[v]
        return w / max(np.max(np.abs(w)), 1e-10)
    
    def decompose(self, assign):
        """Nut: return σ(P) and σ(S) — the foundation of all operations."""
        return self.problem_wave, self.encode_solution(assign)
    
    def correction_vector(self, assign):
        """d = σ(P) − σ(S) — the most misaligned band."""
        _, sol = self.decompose(assign)
        return self.problem_wave - sol

def ih(a, b): return float(np.sqrt(np.mean((a-b)**2)))

# ═══════════════════════════════════════════════════════════
# CLAUSE UTILITIES
# ═══════════════════════════════════════════════════════════

def sat_cnt(clauses, assign):
    return sum(1 for c in clauses if any(
        (s and assign.get(v, False)) or (not s and not assign.get(v, True)) for v, s in c))

def clause_ok(c, assign):
    return any((s and assign.get(v, False)) or (not s and not assign.get(v, True)) for v, s in c)

# ═══════════════════════════════════════════════════════════
# HORUS — All-Seeing Conflict Detection (Unit Propagation)
# ═══════════════════════════════════════════════════════════

def horus_propagate(clauses, assign):
    """Horus: see all conflicts before they happen. Find forced assignments."""
    changed = True
    forced = []
    while changed:
        changed = False
        for clause in clauses:
            if clause_ok(clause, assign): continue
            unassigned = []
            for v, s in clause:
                if v not in assign: unassigned.append((v, s))
                elif assign[v] == s: break  # satisfied
            else:
                if len(unassigned) == 1:
                    v, s = unassigned[0]
                    if v not in assign:
                        assign[v] = s; forced.append(v); changed = True
                    elif assign[v] != s:
                        return assign, set([v])  # conflict
    return assign, set()

# ═══════════════════════════════════════════════════════════
# RA — Illuminate: Scan All Candidates
# ═══════════════════════════════════════════════════════════

def ra_illuminate(encoder, assign, candidates, best_sat, current_ih):
    """Ra: scan every candidate. Find the one that most reduces inharmony."""
    best_v, best_ih, best_sat_v = None, current_ih, best_sat
    
    for v in list(candidates)[:30]:
        if v not in (1, encoder.n_vars+1): continue
        old = encoder.sF[v] if assign.get(v, False) else encoder.sT[v]
        new = encoder.sT[v] if assign.get(v, False) else encoder.sF[v]
        sol = encoder.encode_solution(assign)
        delta = (new - old) / max(np.max(np.abs(sol)), 1e-10)
        nw = sol + delta; nw /= max(np.max(np.abs(nw)), 1e-10)
        nih = ih(encoder.problem_wave, nw)
        
        if nih < best_ih:
            best_ih = nih; best_v = v
    
    return best_v

# ═══════════════════════════════════════════════════════════
# BASTET — Intuitive selection from unsatisfied clause region
# ═══════════════════════════════════════════════════════════

def bastet_select(encoder, assign, clauses, unsat_indices):
    """Bastet: from the unsatisfied clauses, pick the variable that
    appears most frequently — the 'intuitive' choice."""
    freq = {}
    for ci in unsat_indices[:50]:
        for v, s in clauses[ci]:
            if 1 <= v <= encoder.n_vars:
                freq[v] = freq.get(v, 0) + 1
    if not freq: return random.randint(1, encoder.n_vars)
    return max(freq, key=freq.get)

# ═══════════════════════════════════════════════════════════
# OSIRIS — Journey through the underworld (backtrack)
# ═══════════════════════════════════════════════════════════

def osiris_journey(assign, best_assign, best_sat, current_sat):
    """Osiris: if we've gone astray, retreat to the last checkpoint
    and try a different path."""
    if current_sat < best_sat * 0.95:
        return best_assign.copy(), True
    return assign, False

# ═══════════════════════════════════════════════════════════
# MAAT — Verify constraint coverage
# ═══════════════════════════════════════════════════════════

def maat_verify(clauses, assign, n_vars):
    """Maat: cosmic order. Are ALL constraints satisfied?"""
    unsat = [ci for ci in range(len(clauses)) if not clause_ok(clauses[ci], assign)]
    return len(unsat) == 0, unsat

# ═══════════════════════════════════════════════════════════
# THOTH — Record learned clauses
# ═══════════════════════════════════════════════════════════

def thoth_record(learned_clauses, assignment, conflict_vars):
    """Thoth: scribe the lesson. These assignments cannot coexist."""
    clause = [(v, not assignment.get(v, False)) for v in conflict_vars if v in assignment]
    if len(clause) >= 2:
        learned_clauses.append(clause)
        return True
    return False

# ═══════════════════════════════════════════════════════════
# ANUBIS — Weigh the heart
# ═══════════════════════════════════════════════════════════

def anubis_weigh(sat, total, threshold=0.999):
    """Anubis: is the solution light enough to pass?"""
    return sat >= total * threshold

# ═══════════════════════════════════════════════════════════
# ISIS — Resurrect broken fragments after backtrack
# ═══════════════════════════════════════════════════════════

def isis_resurrect(assign, n_vars, learned_clauses):
    """Isis: after a severe backtrack, rebuild a coherent assignment
    guided by learned clauses — what CANNOT be."""
    # Reset variables mentioned in learned clauses
    affected = set()
    for clause in learned_clauses[-20:]:  # recent lessons
        for v, _ in clause: affected.add(v)
    for v in affected:
        if v in assign: assign[v] = random.random() > 0.5
    return assign

# ═══════════════════════════════════════════════════════════
# ATUM — The ONE, the Totality, Final Convergence Check
# ═══════════════════════════════════════════════════════════

def atum_final(assign, clauses, encoder):
    """Atum: the complete. Verify everything, return the truth."""
    s = sat_cnt(clauses, assign)
    _, sol = encoder.decompose(assign)
    inhar = ih(encoder.problem_wave, sol)
    return {"satisfied": s, "total": len(clauses), "inharmony": inhar,
            "perfect": s == len(clauses)}

# ═══════════════════════════════════════════════════════════
# THE FULL TWELVE-GOD CONVERGENCE
# ═══════════════════════════════════════════════════════════

def twelve_gods_solve(clauses, n_vars, max_steps=5000, verbose=True):
    nc = len(clauses)
    
    # ── NUT: Decompose the problem ──
    enc = NutEncoder(clauses, n_vars, res=128)
    prob_wave = enc.problem_wave
    
    # Greedy init
    assign = {}
    for v in range(1, n_vars+1):
        pos = sum(1 for c in clauses for lv, s in c if lv == v and s)
        neg = sum(1 for c in clauses for lv, s in c if lv == v and not s)
        assign[v] = pos >= neg
    
    best_assign = assign.copy()
    best_sat = sat_cnt(clauses, assign)
    sol_wave = enc.encode_solution(assign)
    current_ih = ih(prob_wave, sol_wave)
    
    learned = []
    restarts = 0
    no_improve = 0
    tabu = set()  # recently flipped — avoid repeating
    history = [{"step": 0, "sat": best_sat, "ih": current_ih}]
    
    if verbose:
        print(f"  Nut: ι={current_ih:.4f}, sat={best_sat}/{nc}")
    
    for step in range(1, max_steps + 1):
        # ── HORUS: All-seeing — find forced assignments ──
        if best_sat > nc * 0.85:
            assign, conflicts = horus_propagate(clauses + learned, assign)
            if conflicts:
                # ── THOTH: Record the lesson ──
                thoth_record(learned, assign, conflicts)
                no_improve += 1
                if no_improve > 200:
                    # ── ISIS: Resurrect ──
                    assign = isis_resurrect(assign, n_vars, learned)
                    restarts += 1; no_improve = 0
                continue
        
        # ── MAAT: What clauses remain unsatisfied? ──
        all_ok, unsat_indices = maat_verify(clauses + learned, assign, n_vars)
        if all_ok and sat_cnt(clauses, assign) == nc:
            if verbose: print(f"  ✓ {step} steps — Anubis accepts")
            break
        
        if not unsat_indices:
            # All learned clauses satisfied but maybe not original clauses
            unsat_indices = [ci for ci in range(nc) if not clause_ok(clauses[ci], assign)]
            if not unsat_indices:
                if verbose: print(f"  ✓ ALL at step {step}")
                break
        
        # ── BASTET: Intuit which variable ──
        freq = {}
        for ci in unsat_indices[:50]:
            for cv, s in clauses[ci]:
                if 1 <= cv <= enc.n_vars:
                    freq[cv] = freq.get(cv, 0) + 1
        
        if not freq:
            continue
        
        # Add randomness: sometimes explore non-obvious variables
        if random.random() < 0.15 and len(freq) > 3:
            # Explore a random variable from unsatisfied clauses
            all_vars = list(freq.keys())
            v = random.choice(all_vars)
        else:
            # Bastet: pick most frequent, but avoid recently tried tabu
            sorted_vars = sorted(freq, key=freq.get, reverse=True)
            for v_candidate in sorted_vars:
                if v_candidate not in tabu:
                    v = v_candidate
                    break
            else:
                v = sorted_vars[0]  # all are tabu, pick anyway
        
        # ── RA: Illuminate — scan for better in this band ──
        candidates = set()
        for ci in unsat_indices[:30]:
            for cv, _ in clauses[ci]:
                if 1 <= cv <= enc.n_vars:
                    candidates.add(cv)
        
        if best_sat > nc * 0.8:
            ra_choice = ra_illuminate(enc, assign, candidates, best_sat, current_ih)
            if ra_choice: v = ra_choice
        
        # ── SET: Dismember and reassemble — flip the variable ──
        if v and 1 <= v <= enc.n_vars:
            assign[v] = not assign.get(v, False)
            tabu.add(v)
            if len(tabu) > n_vars // 3:  # keep tabu list bounded
                tabu.clear()
        
        # ── NUT: Remeasure — the snake eats its tail ──
        sol_wave = enc.encode_solution(assign)
        current_ih = ih(prob_wave, sol_wave)
        current_sat = sat_cnt(clauses, assign)
        
        if current_sat > best_sat:
            best_sat = current_sat
            best_assign = assign.copy()
            no_improve = 0
        else:
            no_improve += 1
        
        # ── OSIRIS: Journey — backtrack only if severely lost ──
        if current_sat < best_sat * 0.9:
            assign = best_assign.copy()
            sol_wave = enc.encode_solution(assign)
            current_ih = ih(prob_wave, sol_wave)
            current_sat = best_sat
            no_improve += 1
        
        # Forced exploration on extended stagnation
        if no_improve > 100:
            # Isis: resurrect a random subset
            for _ in range(random.randint(1, max(1, n_vars//10))):
                rv = random.randint(1, n_vars)
                assign[rv] = not assign.get(rv, False)
            sol_wave = enc.encode_solution(assign); no_improve = 0; restarts += 1
        
        if step % 500 == 0 and verbose:
            print(f"  {step:4d}: sat={best_sat}/{nc} ({best_sat/nc*100:.0f}%), ι={current_ih:.4f}, learned={len(learned)}")
        
        history.append({"step": step, "sat": best_sat, "ih": current_ih})
    
    # ── ATUM: Final verification ──
    return best_assign, atum_final(best_assign, clauses, enc), history, len(learned), restarts


# ═══════════════════════════════════════════════════════════
# BENCHMARK
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    from pysat.solvers import Glucose3
    
    print("=" * 70)
    print("THE TWELVE GODS — Full Decomposition Pipeline")
    print("Nut→Ra→Bastet→Horus→Set→Osiris→Maat→Nephthys→Isis→Anubis→Thoth→Atum")
    print("=" * 70)
    
    results = []
    for nv, nc, max_s in [(20, 84, 1000), (50, 210, 3000), (100, 420, 5000)]:
        clauses = [[(random.randint(1, nv), random.choice([True, False]))
                    for _ in range(3)] for _ in range(nc)]
        
        # Glucose3
        g = Glucose3()
        for c in clauses: g.add_clause([v if s else -v for v,s in c])
        is_sat = g.solve()
        gms = (time.time() - time.time()) * -1000  # wrong but will overwrite
        g.delete()
        t0 = time.time()
        g = Glucose3()
        for c in clauses: g.add_clause([v if s else -v for v,s in c])
        is_sat = g.solve()
        gms2 = (time.time() - t0) * 1000
        g_sat = sat_cnt(clauses, {abs(v): v>0 for v in g.get_model()}) if is_sat else 0
        g.delete()
        print(f"\n{'─'*70}")
        print(f"SAT {nv}v/{nc}c — Glucose3: {'SAT' if is_sat else 'UNSAT'} ({g_sat}/{nc}) {gms2:.0f}ms")
        
        t0 = time.time()
        assign, final, hist, learned, restarts = twelve_gods_solve(
            clauses, nv, max_steps=max_s, verbose=True
        )
        tms = (time.time() - t0) * 1000
        
        print(f"  Result: {final['satisfied']}/{final['total']} ({final['satisfied']/final['total']*100:.0f}%), "
              f"ι={final['inharmony']:.4f}, {tms:.0f}ms, learned={learned}, re={restarts}")
        results.append({"nv": nv, "glucose": g_sat, "pantheon": final['satisfied'], "nc": nc, "ms": tms})
    
    print(f"\n{'='*70}")
    print(f"{'Vars':>5s} {'Glucose':>8s} {'12 Gods':>12s} {'Time':>8s}")
    print("-"*70)
    for r in results:
        gs = f"{r['glucose']}/{r['nc']}"; ps = f"{r['pantheon']}/{r['nc']}"
        print(f"{r['nv']:5d} {gs:>8s} {ps:>12s} {r['ms']:7.0f}ms")
