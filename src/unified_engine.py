#!/usr/bin/env python3
"""
UNIFIED OUROBOROS ENGINE
═══════════════════════════════════════════════════════════
All components wired together:
  Teslan analysis → Waveform inharmony → Pipeline → Assess → Gate → Feedback → Loop
"""

import math, random, time, numpy as np, sys, copy
random.seed(42); np.random.seed(42)

import toolkit
from vedic_planetary_transformers import MercurialClauseWeaver, TeslanResonantCollector
from pysat.solvers import Glucose3

PHI = (1+math.sqrt(5))/2; N = 72

# ═══════════════════════════════════════════════════════════
# 1. TESLAN — Spectral Analysis & Routing
# ═══════════════════════════════════════════════════════════

def teslan_analyze(clauses_tuple, n_vars):
    """Analyze SAT instance via Teslan Resonant Collector."""
    collector = TeslanResonantCollector(seed=42)
    signed = [[(l, True) if l > 0 else (abs(l), False) for l in 
               [v if s else -v for v,s in c]] for c in clauses_tuple]
    result = collector.analyze_sat_spectrum(signed, n_vars)
    sig = result.get("wavelength_signature", "unknown")
    return {"signature": sig, "ratio": result.get("ratio_m_n", 0),
            "near_phase": result.get("near_phase_transition", False),
            "spectral_radius": result.get("spectral_radius", 0)}

# ═══════════════════════════════════════════════════════════
# 2. WAVEFORM — Fibonacci φ-spacing + π grid
# ═══════════════════════════════════════════════════════════

class Waveform:
    def __init__(self, clauses_tuple, res=128):
        nv = max(abs(l) for c in clauses_tuple for l,_ in c) if clauses_tuple else 3
        self.n_vars, self.res = nv, res
        self.t = np.array(sorted([(2*np.pi*i*PHI)%(2*np.pi) for i in range(res)]))
        self.f = np.array([100.0*PHI**((v-1)/N) for v in range(1, nv+1)])
        self.sT, self.sF = {}, {}
        for v in range(1, nv+1):
            self.sT[v] = np.sin(2*np.pi*self.f[v-1]*self.t)
            self.sF[v] = np.sin(2*np.pi*self.f[v-1]*self.t + np.pi)
        w = np.zeros(res)
        for c in clauses_tuple:
            cw = np.zeros(res)
            for v,s in c:
                if 1<=v<=nv: cw += self.sT[v] if s else self.sF[v]
            w += np.abs(cw)
        self.σP = w/max(np.max(np.abs(w)), 1e-10)
    
    def inharmony(self, assign):
        w = np.zeros(self.res)
        for v in range(1, self.n_vars+1):
            w += self.sT[v] if assign.get(v,False) else self.sF[v]
        σS = w/max(np.max(np.abs(w)), 1e-10)
        return float(np.sqrt(np.mean((self.σP-σS)**2)))
    
    def worst_band(self, assign):
        w = np.zeros(self.res)
        for v in range(1, self.n_vars+1):
            w += self.sT[v] if assign.get(v,False) else self.sF[v]
        σS = w/max(np.max(np.abs(w)), 1e-10)
        bsz = max(1, self.res//N)
        errors = [np.mean(np.abs(self.σP[i*bsz:min((i+1)*bsz,self.res)] - 
                                σS[i*bsz:min((i+1)*bsz,self.res)])) 
                 for i in range(N) if i*bsz < self.res]
        return int(np.argmax(errors)) if errors else 0

# ═══════════════════════════════════════════════════════════
# 3. SATISFACTION
# ═══════════════════════════════════════════════════════════

def sat(clauses, assign):
    return sum(1 for c in clauses if any(
        (s and assign.get(v,False)) or (not s and not assign.get(v,True)) for v,s in c))

# ═══════════════════════════════════════════════════════════
# 4. UNIFIED ENGINE
# ═══════════════════════════════════════════════════════════

def unified_solve(clauses_tuple, max_cycles=500):
    nc = len(clauses_tuple)
    nv = max(abs(l) for c in clauses_tuple for l,_ in c)
    clauses_cnf = [[v if s else -v for v,s in c] for c in clauses_tuple]
    
    # Teslan analysis
    tesla = teslan_analyze(clauses_tuple, nv)
    
    # Waveform encoder
    wf = Waveform(clauses_tuple)
    
    # Pipeline + Ouroboros
    best_sat, best, stuck = 0, None, 0
    
    for cycle in range(max_cycles):
        state = {"_type": "sat", "clauses": clauses_cnf}
        if best is not None:
            state["best_assignment"] = best.copy()
        
        result = toolkit.pipeline(state)
        emanated = result['state']
        if 'assignment' not in emanated: continue
        
        assign = emanated['assignment']
        s = sat(clauses_tuple, assign)
        ih = wf.inharmony(assign) if s > 0 else 999
        
        # Waveform-guided refinement on best
        if best is not None and s < nc and stuck % 10 == 0:
            worst = wf.worst_band(best)
            vars_in = [v for v in range(1, nv+1) if (v-1)%N == worst]
            for v in vars_in[:min(len(vars_in), 5)]:
                best[v] = not best.get(v,False)
                ns = sat(clauses_tuple, best)
                if ns > best_sat:
                    best_sat = ns; stuck = 0
                else:
                    best[v] = not best.get(v,False)
        
        if s > best_sat:
            best_sat = s; best = assign.copy(); stuck = 0
        else:
            stuck += 1
        
        if best_sat == nc: break
        if stuck > 100: break
    
    return {"satisfied": best_sat, "total": nc, "pct": best_sat/nc*100,
            "tesla": tesla, "cycles": cycle+1, "perfect": best_sat==nc,
            "final_inharmony": wf.inharmony(best) if best else 999}

# ═══════════════════════════════════════════════════════════
# BENCHMARK
# ═══════════════════════════════════════════════════════════

print("UNIFIED ENGINE — Teslan + Waveform + Pipeline + Assess + Gate")
print("=" * 70)

for nv, nc in [(20,84), (50,210), (75,315), (100,420)]:
    clauses_tuple = [[(random.randint(1, nv), random.choice([True, False]))
                for _ in range(3)] for _ in range(nc)]
    
    g=Glucose3()
    for c in clauses_tuple: g.add_clause([v if s else -v for v,s in c])
    is_sat=g.solve(); g.delete()
    
    t0=time.time()
    result = unified_solve(clauses_tuple, max_cycles=200)
    ms=(time.time()-t0)*1000
    
    perf = "✓ PERFECT" if result['perfect'] else f"gap={result['total']-result['satisfied']}"
    print(f"{nv}v/{nc}c ({'SAT' if is_sat else 'UNSAT'}): {result['satisfied']}/{result['total']} "
          f"({result['pct']:.0f}%), tesla={result['tesla']['signature']}, "
          f"ι={result['final_inharmony']:.4f}, {result['cycles']}c, {ms:.0f}ms {perf}")
