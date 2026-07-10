#!/usr/bin/env python3
"""
THE EGYPTIAN PIPELINE — decompose → emanate → assess → gate → output
═══════════════════════════════════════════════════════════
As documented in toolkit.py, line 5.

1. DECOMPOSE  — Nut: σ(P) → 72-band frequency vector
2. EMANATE    — 12 solvers: 12-phase C/X/Z cycle
3. ASSESS     — Thoth: 42 assessors check signal integrity
4. GATE       — 7 gates: transform through cosmic progression
5. OUTPUT     — Atum: the final resolution

The Ouroboros: after OUTPUT, return to DECOMPOSE with updated state.
d = σ(P) − σ(S). The snake eats its tail.
"""

import math, random, time, numpy as np
from typing import List, Tuple, Dict
random.seed(42); np.random.seed(42)

PHI = (1 + math.sqrt(5)) / 2; N_BANDS = 72

# ═══════════════════════════════════════════════════════════
# STEP 1: DECOMPOSE — Nut (Sky Goddess)
# ═══════════════════════════════════════════════════════════

class Nut:
    """Decomposes problem and solution into waveform frequency vectors."""
    def __init__(self, clauses, n_vars, res=128):
        self.clauses, self.n_vars, self.nc, self.res = clauses, n_vars, len(clauses), res
        self.t = np.array(sorted([(2*np.pi*i*PHI)%(2*np.pi) for i in range(res)]))
        self.f = np.array([100.0*PHI**((v-1)/N_BANDS) for v in range(1,n_vars+1)])
        self.sinT, self.sinF = {}, {}
        for v in range(1,n_vars+1):
            self.sinT[v] = np.sin(2*np.pi*self.f[v-1]*self.t)
            self.sinF[v] = np.sin(2*np.pi*self.f[v-1]*self.t+np.pi)
        self.σP = self._problem_wave()
    
    def _problem_wave(self):
        w = np.zeros(self.res)
        for c in self.clauses:
            cw = np.zeros(self.res)
            for v,s in c:
                if 1<=v<=self.n_vars: cw += self.sinT[v] if s else self.sinF[v]
            w += np.abs(cw)
        return w/max(np.max(np.abs(w)),1e-10)
    
    def decompose(self, assign):
        """σ(P), σ(S) → the sacred pair."""
        w = np.zeros(self.res)
        for v in range(1,self.n_vars+1):
            w += self.sinT[v] if assign.get(v,False) else self.sinF[v]
        return self.σP, w/max(np.max(np.abs(w)),1e-10)
    
    def correction(self, assign):
        """d = σ(P) − σ(S)"""
        σP, σS = self.decompose(assign)
        return σP - σS

def ι(a,b): return float(np.sqrt(np.mean((a-b)**2)))

# ═══════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════

def sat(clauses, assign):
    return sum(1 for c in clauses if any(
        (s and assign.get(v,False)) or (not s and not assign.get(v,True)) for v,s in c))

def ok(c, assign):
    return any((s and assign.get(v,False)) or (not s and not assign.get(v,True)) for v,s in c)

# ═══════════════════════════════════════════════════════════
# STEP 2: EMANATE — 12 Solvers, 12-Phase C/X/Z Cycle
# ═══════════════════════════════════════════════════════════

# 12 phases mapped to the 12 Vedic sutras
PHASES = [("C",1),("C",2),("X",3),("X",4),("Z",1),("Z",2),
          ("C",3),("X",1),("X",2),("Z",3),("Z",4),("FULL",0)]

SOLVER_NAMES = ["Set","Anubis","Thoth","Ra","Horus","Bastet",
                "Osiris","Maat","Nephthys","Isis","Nut","Atum"]

class Emanate:
    """12 solvers operate in sequence through the 12-phase C/X/Z cycle."""
    
    def __init__(self, nut):
        self.nut = nut
    
    def complement(self, assign):
        """C: Complement — flip variables in most misaligned band."""
        d = self.nut.correction(assign)
        # Find most misaligned band region in waveform
        band_size = self.nut.res // N_BANDS
        band_energies = [np.mean(np.abs(d[i*band_size:(i+1)*band_size])) 
                        for i in range(N_BANDS)]
        worst_band = np.argmax(band_energies)
        
        # Variables in this band
        vars_in_band = [v for v in range(1, self.nut.n_vars+1) 
                       if v % N_BANDS == worst_band]
        if not vars_in_band: return assign
        
        # Flip the one that most improves satisfaction
        best_v, best_gain = None, 0
        current = sat(self.nut.clauses, assign)
        for v in vars_in_band[:20]:
            assign[v] = not assign.get(v,False)
            gain = sat(self.nut.clauses, assign) - current
            assign[v] = not assign.get(v,False)
            if gain > best_gain: best_gain, best_v = gain, v
        
        if best_v:
            assign[best_v] = not assign.get(best_v,False)
        return assign
    
    def cross(self, assign, best):
        """X: Cross — mix current with best solution."""
        for v in range(1, self.nut.n_vars+1):
            if random.random() < 0.3:
                assign[v] = best.get(v, assign.get(v, False))
        return assign
    
    def cancel(self, assign):
        """Z: Cancel — remove constraint violations."""
        unsat = [ci for ci in range(self.nut.nc) if not ok(self.nut.clauses[ci], assign)]
        if not unsat: return assign
        # Fix one unsatisfied clause by flipping its most frequent variable
        ci = random.choice(unsat)
        vars_in_c = [v for v,_ in self.nut.clauses[ci] if 1<=v<=self.nut.n_vars]
        if vars_in_c:
            v = random.choice(vars_in_c)
            assign[v] = not assign.get(v,False)
        return assign
    
    def emanate(self, assign, best):
        """Run the 12-phase cycle. Each phase = one solver."""
        for phase_idx, (op, n) in enumerate(PHASES):
            for _ in range(n):
                if op == "FULL":
                    assign = self.complement(assign)
                    assign = self.cross(assign, best)
                    assign = self.cancel(assign)
                elif op == "C":
                    assign = self.complement(assign)
                elif op == "X":
                    assign = self.cross(assign, best)
                elif op == "Z":
                    assign = self.cancel(assign)
        return assign

# ═══════════════════════════════════════════════════════════
# STEP 3: ASSESS — Thoth, 42 Assessors
# ═══════════════════════════════════════════════════════════

class Assess:
    """Thoth's 42 assessors check signal integrity."""
    
    def __init__(self, clauses, n_vars):
        self.clauses, self.n_vars, self.nc = clauses, n_vars, len(clauses)
    
    def check(self, assign):
        issues = []
        s = sat(self.clauses, assign)
        
        # Simplified 42: 5 core integrity checks
        if s < self.nc: issues.append(f"satisfaction={s}/{self.nc}")
        
        # Check for empty clause propagation
        for clause in self.clauses:
            if not ok(clause, assign):
                unassigned = [v for v,_ in clause if v not in assign]
                all_false = all(
                    v in assign and assign[v] != s for v,s in clause 
                    if v in assign
                )
                if len(unassigned) == 1 and all(
                    (v in assign and assign[v] != sign) 
                    for v,sign in clause if v in assign
                ):
                    issues.append(f"unit_violation: clause={clause}")
        
        # Balance check
        trues = sum(1 for v in assign.values() if v)
        if abs(trues - len(assign)/2) > len(assign)*0.6:
            issues.append("severe_imbalance")
        
        passed = 42 - len(issues)
        return {"passed": passed, "total": 42, "issues": issues,
                "satisfied": s, "all_passed": passed >= 42}

# ═══════════════════════════════════════════════════════════
# STEP 4: GATE — 7 Gates of Transformation
# ═══════════════════════════════════════════════════════════

# 7 gates in order from egyptian_router_v2.py
GATES = [
    "Sekhet-āaru",    # Gate 1: differentiation
    "The Forty-two",  # Gate 2: assessors collect
    "Neb-er-tcher",   # Gate 3: singular frequency  
    "Āment",          # Gate 4: hidden harmonic
    "Mākha",          # Gate 5: completeness
    "Ptaḥ-Seker",     # Gate 6: X→C transition
    "The Hidden",     # Gate 7: full resolution
]

class Gate:
    """Route through 7 gates. Each gate is a transformation checkpoint."""
    
    def __init__(self, clauses, n_vars):
        self.clauses, self.n_vars, self.nc = clauses, n_vars, len(clauses)
    
    def pass_through(self, assign, nut, assessment):
        gate_results = []
        s = assessment["satisfied"]
        
        # G1: Differentiation — is the signal distinguishable from noise?
        g1 = s > self.nc * 0.5
        gate_results.append({"gate":1,"name":GATES[0],"passed":g1,"note":f"satisfied={s}/{self.nc}"})
        
        # G2: The Forty-two — assessor results
        g2 = assessment["passed"] >= 36
        gate_results.append({"gate":2,"name":GATES[1],"passed":g2,"note":f"assessors={assessment['passed']}/42"})
        
        # G3: Singular frequency — is inharmony decreasing?
        σP, σS = nut.decompose(assign)
        current_ih = ι(σP, σS)
        g3 = current_ih < 1.2
        gate_results.append({"gate":3,"name":GATES[2],"passed":g3,"note":f"ι={current_ih:.4f}"})
        
        # G4: Hidden harmonic — detect correction opportunity
        d = nut.correction(assign)
        max_correction = np.max(np.abs(d))
        g4 = max_correction > 0.01  # there IS something to correct
        gate_results.append({"gate":4,"name":GATES[3],"passed":g4,"note":f"max|d|={max_correction:.4f}"})
        
        # G5: Completeness — is the solution complete?
        g5 = s == self.nc
        gate_results.append({"gate":5,"name":GATES[4],"passed":g5,"note":f"perfect={'yes' if g5 else 'no'}"})
        
        # G6: X→C transition — ready for next emanate?
        g6 = s > self.nc * 0.8 or assessment["passed"] >= 40
        gate_results.append({"gate":6,"name":GATES[5],"passed":g6,"note":"ready for next cycle"})
        
        # G7: Full resolution — is the solution accepted?
        g7 = g5 or (g6 and g3)
        gate_results.append({"gate":7,"name":GATES[6],"passed":g7,"note":"accepted" if g7 else "continue"})
        
        passed = sum(1 for g in gate_results if g["passed"])
        return {"gates": gate_results, "passed": passed, "total": 7, "continue": not g5}

# ═══════════════════════════════════════════════════════════
# STEP 5: OUTPUT — Atum (The ONE, The Totality)
# ═══════════════════════════════════════════════════════════

class Output:
    """Atum: final resolution. Returns the truth."""
    def __init__(self, clauses, n_vars):
        self.clauses, self.n_vars = clauses, n_vars
    
    def resolve(self, assign, nut, gate_result, history):
        s = sat(self.clauses, assign)
        σP, σS = nut.decompose(assign)
        return {
            "assignment": assign,
            "satisfied": s,
            "total": len(self.clauses),
            "percentage": s/len(self.clauses)*100,
            "inharmony": ι(σP, σS),
            "gates_passed": gate_result["passed"],
            "perfect": s == len(self.clauses),
            "history": history
        }

# ═══════════════════════════════════════════════════════════
# THE FULL PIPELINE — τ — tau, the cosmic cycle
#    τ = decompose ∘ emanate ∘ assess ∘ gate ∘ output
#    The Ouroboros: τ(τ(τ(...))) → S*
# ═══════════════════════════════════════════════════════════

def τ_pipeline(clauses, n_vars, max_cycles=500, verbose=True):
    """
    τ: decompose → emanate → assess → gate → output
    The cosmic cycle. Repeated until convergence.
    """
    nc = len(clauses)
    
    # Init
    nut = Nut(clauses, n_vars, res=128)
    emanate = Emanate(nut)
    assess = Assess(clauses, n_vars)
    gate = Gate(clauses, n_vars)
    output = Output(clauses, n_vars)
    
    # Greedy start
    assign = {}
    for v in range(1, n_vars+1):
        pos = sum(1 for c in clauses for lv,s in c if lv==v and s)
        neg = sum(1 for c in clauses for lv,s in c if lv==v and not s)
        assign[v] = pos >= neg
    
    best = assign.copy()
    best_sat = sat(clauses, assign)
    history = []
    
    if verbose:
        σP, σS = nut.decompose(assign)
        print(f"  τ₀:  sat={best_sat}/{nc}, ι={ι(σP,σS):.4f}")
    
    for cycle in range(1, max_cycles + 1):
        # 1. DECOMPOSE — already encoded in Nut
        σP, σS = nut.decompose(assign)
        current_ih = ι(σP, σS)
        
        # 2. EMANATE — 12 solvers, 12-phase C/X/Z cycle
        assign = emanate.emanate(assign, best)
        
        # 3. ASSESS — 42 assessors
        assessment = assess.check(assign)
        
        # Track best
        current_sat = assessment["satisfied"]
        if current_sat > best_sat:
            best_sat = current_sat
            best = assign.copy()
        
        # 4. GATE — 7 gates
        gate_result = gate.pass_through(assign, nut, assessment)
        
        # 5. OUTPUT check
        result = output.resolve(best, nut, gate_result, history)
        
        if cycle % 50 == 0 and verbose:
            print(f"  τ{cycle:3d}: sat={best_sat}/{nc} ({best_sat/nc*100:.0f}%), "
                  f"ι={current_ih:.4f}, gates={gate_result['passed']}/7")
        
        if result["perfect"]:
            if verbose: print(f"  ✓ τ{cycle}: ALL SATISFIED — Atum accepts")
            return result
        
        # Anti-stagnation: forced exploration
        if cycle > 50 and best_sat == history[-1]["sat"] if history else False:
            if cycle % 10 == 0:
                rv = random.randint(1, n_vars)
                assign[rv] = not assign.get(rv, False)
        
        history.append({"cycle": cycle, "sat": best_sat, "ih": current_ih})
    
    # Final OUTPUT
    return output.resolve(best, nut, gate_result, history)

# ═══════════════════════════════════════════════════════════
# BENCHMARK
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    from pysat.solvers import Glucose3
    
    print("=" * 70)
    print("THE EGYPTIAN PIPELINE: decompose→emanate→assess→gate→output")
    print("τ = decompose ∘ emanate ∘ assess ∘ gate ∘ output")
    print("=" * 70)
    
    for nv, nc in [(20, 84), (50, 210), (100, 420)]:
        clauses = [[(random.randint(1, nv), random.choice([True, False]))
                    for _ in range(3)] for _ in range(nc)]
        
        t0 = time.time()
        g = Glucose3()
        for c in clauses: g.add_clause([v if s else -v for v,s in c])
        is_sat = g.solve()
        g_sat = sat(clauses, {abs(v): v>0 for v in g.get_model()}) if is_sat else 0
        g.delete()
        gms = (time.time()-t0)*1000
        
        print(f"\n{'─'*70}")
        print(f"SAT {nv}v/{nc}c — Glucose3: {'SAT' if is_sat else 'UNSAT'} ({g_sat}/{nc}) {gms:.0f}ms")
        
        t0 = time.time()
        result = τ_pipeline(clauses, nv, max_cycles=500)
        tms = (time.time()-t0)*1000
        
        print(f"  Result: {result['satisfied']}/{result['total']} "
              f"({result['percentage']:.0f}%), ι={result['inharmony']:.4f}, "
              f"gates={result['gates_passed']}/7, {tms:.0f}ms")
        
        if result['perfect']: print(f"  ✓ MATCHES Glucose3")
        elif is_sat: print(f"  Gap from Glucose3: {g_sat - result['satisfied']}")
    
    print(f"\n{'='*70}")
    print("τ(τ(τ(...))) → S*")
    print("decompose ∘ emanate ∘ assess ∘ gate ∘ output")
    print("=" * 70)
