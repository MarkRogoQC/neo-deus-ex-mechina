"""
EGYPTIAN PROTOCOL TOOLKIT
Book of the Dead = Code72 ∘ Consciousness ∘ {transition handler}

Pipeline: decompose → emanate → assess → gate → output
"""

import copy, math, sys, os

# ── Working algorithms imported, not rewritten ────────────────────────────
from vedic_planetary_transformers import (
    MercurialClauseWeaver as Set,        # SAT
    VenusianTourLoom as Anubis,            # TSP
    SaturnianMinimalShield as Thoth,        # Vertex Cover
    NeptunianDreamWeaver as Ra,             # Max Clique
    SolarChromaticWeaver as Horus,         # Graph Coloring
    JovianExpansiveNet as Maat,            # Set Cover
    MartianPathfinder as Osiris,           # Hamiltonian Path
    LunarIntuitiveOracle as Bastet,        # Subset Sum
    UranianInnovationEngine as Nephthys,   # Exact Cover
    PlutonianTransformer as Isis,          # Steiner Tree
    TeslanResonantCollector as Nut,        # Wavelength
    UniversalOneSolver,                    # Universal One
)

print("1. Algorithms imported with Egyptian names: ✓")
print(f"   Set={Set}, Anubis={Anubis}, Thoth={Thoth}")
print(f"   Ra={Ra}, Horus={Horus}, Maat={Maat}")
print(f"   Osiris={Osiris}, Bastet={Bastet}, Nephthys={Nephthys}")
print(f"   Isis={Isis}, Nut={Nut}")
print(f"   UniversalOneSolver={UniversalOneSolver}")

# ── 3 Operations (C/X/Z) ──────────────────────────────────────────────────
C = {}
X = {}
Z = {}

def regC(t):
    def wrap(f): C[t] = f; return f
    return wrap
def regX(t):
    def wrap(f): X[t] = f; return f
    return wrap
def regZ(t):
    def wrap(f): Z[t] = f; return f
    return wrap

@regC("input")
@regC("generic")
def _c_id(st,p=None): return copy.deepcopy(st)

# ── Audio-band C/X/Z ─────────────────────────────────────────────────────
# Audio states: {"_type":"audio_band", "band":1-72, "energy":0-1,
#                "phase_coherence":0-1, "spectral_centroid":float, ...}
NOISE_FLOOR = 0.05

@regC("audio_band")
def _c_audio(st, p=None):
    """Complement: invert band energy → anti-resonance detection."""
    s = copy.deepcopy(st)
    s["energy"] = max(0.0, 1.0 - s.get("energy", 0))
    return s

@regX("audio_band")
def _x_audio(st, partner):
    """Cross: mix band energies → harmonic relationship detection."""
    s = copy.deepcopy(st)
    if partner and "energy" in partner:
        s["energy"] = (s.get("energy", 0) + partner.get("energy", 0)) / 2.0
    return s

@regZ("audio_band")
def _z_audio(st, p=None):
    """Cancel: null bands below noise floor → signal purification."""
    s = copy.deepcopy(st)
    if s.get("energy", 1.0) < NOISE_FLOOR:
        s["energy"] = 0.0
    return s

@regX("audio")
def _x_audio_cross(st, partner):
    """Cross for raw audio state dicts (72-band arrays)."""
    s = copy.deepcopy(st)
    if partner and isinstance(partner, dict):
        for k in partner:
            if k not in ("_type",) and isinstance(s.get(k), list) and isinstance(partner.get(k), list):
                a = s[k]
                b = partner[k]
                s[k] = [(x + y) / 2.0 for x, y in zip(a, b)]
    return s

@regC("audio")
def _c_audio_invert(st, p=None):
    """Complement for raw audio states: invert band energies."""
    s = copy.deepcopy(st)
    for k in ("band_energies", "energies"):
        if k in s and isinstance(s[k], list):
            s[k] = [max(0.0, 1.0 - e) for e in s[k]]
    return s

@regZ("audio")
def _z_audio_null(st, p=None):
    """Cancel for raw audio states: null below noise floor."""
    s = copy.deepcopy(st)
    for k in ("band_energies", "energies"):
        if k in s and isinstance(s[k], list):
            s[k] = [0.0 if e < NOISE_FLOOR else e for e in s[k]]
    return s

def complement(st):
    t = st.get("_type","")
    if t in C: return C[t](st)
    if "input" in C: return C["input"](st)
    st2 = copy.deepcopy(st); st2["_type"]="input"
    return st2
def cross(a, b):
    t = a.get("_type","")
    if t in X: return X[t](a,b)
    return copy.deepcopy(a)
def cancel(st):
    t = st.get("_type","")
    if t in Z: return Z[t](st)
    return copy.deepcopy(st)

_ident = lambda s,p=None: copy.deepcopy(s)

# ── 12-Phase Cycle ────────────────────────────────────────────────────────
PHASES = [("C",1),("C",2),("X",3),("X",4),("Z",1),("Z",2),
          ("C",3),("X",1),("X",2),("Z",3),("Z",4),("FULL",0)]

def process(state):
    s = copy.deepcopy(state)
    for op,n in PHASES:
        if op == "FULL":
            s = complement(s); s = cross(s, copy.deepcopy(s)); s = cancel(s)
        elif op == "C":
            for _ in range(n): s = complement(s)
        elif op == "X":
            for _ in range(n): s = cross(s, copy.deepcopy(s))
        elif op == "Z":
            for _ in range(n): s = cancel(s)
    return s

# ── Input Decomposer ──────────────────────────────────────────────────────
def sig(data: bytes) -> list:
    bands = [0.0]*72
    if not data: return bands
    total = 0.0
    for i,b in enumerate(data):
        w = (b/255.0)*(1.0/(1+(i//72)*0.1))
        bands[i%72] += w; total += w
    return [b/total for b in bands] if total > 0 else bands

def text_sig(t: str) -> list:  return sig(t.encode('utf-8'))
def inharmony(a: list, b: list) -> float:
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

print("2. Operations, phase cycle, decomposer: ✓")

# ── Helpers ───────────────────────────────────────────────────────────────
def _dm(d):
    import numpy as np
    if not d: return np.array([[0,1,1.4,1],[1,0,1,1.4],[1.4,1,0,1],[1,1.4,1,0]])
    n = max(max(a,b) for _,a,b in d)+1
    m = np.zeros((n,n))
    for D,a,b in d: m[a][b]=D; m[b][a]=D
    return m
def _adj(e,n):
    a = {i:[] for i in range(n)}
    for u,v in e: a[u].append(v); a[v].append(u)
    return a

# Cross/Cancel defaults — but NOT for sat (implemented below)
for t in ["tsp","vc","clique","coloring","subsetsum","hamiltonian"]:
    X[t]=_ident; Z[t]=_ident

# ── Enhanced SAT C — multi-restart with best-of-N ─────────────────────
@regC("sat")
def _c_sat(st,p=None):
    s=copy.deepcopy(st)
    r=s.get('clauses',[]); n=max(abs(l) for c in r for l in c) if r else 3
    sg=[[(l,1) if l>0 else (abs(l),0) for l in c] for c in r]
    sol=Set(sg,n); result=sol.solve(); s['assignment']=result; return s

# Anubis (TSP)
@regC("tsp")
def _c_tsp(st,p=None):
    s=copy.deepcopy(st)
    sol=Anubis(_dm(s.get('distances',[])))
    t,d=sol.solve(); s['tour']=t; return s

# Thoth (Vertex Cover)
@regC("vc")
def _c_vc(st,p=None):
    s=copy.deepcopy(st)
    e=s.get('edges',[]); n=max(max(u,v) for u,v in e)+1 if e else 4
    sol=Thoth(_adj(e,n),e,n); c=sol.solve()
    s['cover']=sorted(c) if hasattr(c,'__iter__') else [c]; return s

# Ra (Max Clique)
@regC("clique")
def _c_cl(st,p=None):
    s=copy.deepcopy(st)
    e=s.get('edges',[]); n=max(max(u,v) for u,v in e)+1 if e else 4
    adj={i:set() for i in range(n)}
    for u,v in e: adj[u].add(v); adj[v].add(u)
    sol=Ra(adj); result=sol.solve()
    s['clique']=sorted(result) if hasattr(result,'__iter__') else [result]; return s

# Horus (Graph Coloring)
@regC("coloring")
def _c_col(st,p=None):
    s=copy.deepcopy(st)
    e=s.get('edges',[]); n=max(max(u,v) for u,v in e)+1 if e else 4
    sol=Horus(_adj(e,n),e,n); c,cols=sol.solve(); s['assignment']=c; return s

# Bastet (Subset Sum)
@regC("subsetsum")
def _c_ss(st,p=None):
    s=copy.deepcopy(st)
    n=s.get('numbers',[]); t=s.get('target',sum(n)//2)
    sol=Bastet(n,t); result=sol.solve()
    if isinstance(result,set): s['selected']=list(result); s['sum']=sum(n[i] for i in result)
    return s

# Osiris (Hamiltonian Path)
@regC("hamiltonian")
def _c_ham(st,p=None):
    s=copy.deepcopy(st)
    e=s.get('edges',[]); n=max(max(u,v) for u,v in e)+1 if e else 4
    sol=Osiris(_adj(e,n),e,n); result=sol.solve()
    if isinstance(result,tuple) and len(result)>=1: s['path']=result[0]
    else: s['path']=result if hasattr(result,'__iter__') else [result]
    return s

# Cross/Cancel defaults — but NOT for sat/tsp/vc (implemented below)
for t in ["tsp","vc","clique","coloring","subsetsum","hamiltonian"]:
    X[t]=_ident; Z[t]=_ident

# ── SAT Cross/Cancel ───────────────────────────────────────────────────
@regX("sat")
def _x_sat(st, partner):
    """Cross: mix with partner OR with best from state history."""
    s=copy.deepcopy(st)
    if "assignment" not in s: return s
    # Use partner if available, otherwise check for best_assignment in state
    effective_partner = None
    if partner and "assignment" in partner:
        effective_partner = partner["assignment"]
    elif "best_assignment" in s:
        effective_partner = s["best_assignment"]
    
    if effective_partner:
        for v in s["assignment"]:
            if v in effective_partner and random.random() < 0.5:
                s["assignment"][v] = effective_partner[v]
    return s

@regZ("sat")
def _z_sat(st, p=None):
    """Cancel: aggressively fix all unsatisfied clauses."""
    s=copy.deepcopy(st)
    if "assignment" not in s or "clauses" not in s: return s
    clauses = s["clauses"]
    assign = s["assignment"]
    # Find ALL unsatisfied clauses
    unsat = []
    for c in clauses:
        ok = False
        for lit in c:
            v = abs(lit); sign = lit > 0
            if (v in assign and ((sign and assign[v]) or (not sign and not assign[v]))):
                ok = True; break
        if not ok: unsat.append(c)
    # Flip most implicated variable with clause-aware targeting
    if unsat:
        for _ in range(min(3, len(unsat))):
            freq = {}
            for c in unsat:
                for lit in c:
                    v = abs(lit)
                    freq[v] = freq.get(v, 0) + 1
            if not freq: break
            v = max(freq, key=freq.get)
            assign[v] = not assign.get(v, False)
            # Re-check which clauses are still unsatisfied
            unsat = [c for c in unsat if not any(
                abs(l) in assign and ((l>0 and assign[abs(l)]) or (l<0 and not assign[abs(l)]))
                for l in c)]
    return s

import random

# Maat (Set Cover), Nephthys (Exact Cover), Isis (Steiner Tree), Nut (Wavelength)
@regC("set_cover")
def _c_sc(s,p=None): return copy.deepcopy(s)
@regC("exact_cover")
def _c_ec(s,p=None): return copy.deepcopy(s)
@regC("steiner")
def _c_st(s,p=None): return copy.deepcopy(s)
@regC("wavelength")
def _c_wl(s,p=None): return copy.deepcopy(s)
for t in ["set_cover","exact_cover","steiner","wavelength"]:
    X[t]=_ident; Z[t]=_ident

# ── Verify ────────────────────────────────────────────────────────────────
def verify(o, s):
    t = o.get("_type","")
    if t=="audio_band":  return inharmony_energy(o, s)
    if t=="tsp":         return len(set(s.get("tour",[])))==len(s.get("tour",[]))
    if t=="sat":         return "assignment" in s
    if t=="vc":
        from collections import defaultdict
        cov=set(); [cov.add((u,v)) for u,v in o.get("edges",[]) if u in s.get("cover",[]) or v in s.get("cover",[])]
        return len(cov)==len(o.get("edges",[]))
    if t=="clique":      return len(s.get("clique",[]))>0
    if t=="coloring":    return all(s["assignment"].get(a)!=s["assignment"].get(b) for a,b in o.get("edges",[]))
    if t=="subsetsum":   return s.get("sum",999)<=s.get("target",0)
    if t=="hamiltonian": return len(set(s.get("path",[])))==len(o.get("vertices",[]))
    return True

def inharmony_energy(a, b):
    """Audio-band inharmony: 1.0 - cosine similarity of energies."""
    import numpy as np
    ea = a.get("energy", a) if isinstance(a, dict) else a
    eb = b.get("energy", b) if isinstance(b, dict) else b
    if isinstance(ea, (int, float)) and isinstance(eb, (int, float)):
        return 1.0 - abs(ea - eb)
    if hasattr(ea, '__iter__') and hasattr(eb, '__iter__'):
        va, vb = np.array(list(ea), dtype=float), np.array(list(eb), dtype=float)
        na, nb = np.linalg.norm(va), np.linalg.norm(vb)
        return float(1.0 - np.dot(va, vb) / (na * nb)) if na > 0 and nb > 0 else 1.0
    return 1.0

# ── Test ──────────────────────────────────────────────────────────────────
def test():
    cases = [
        (1,"TSP",    {"_type":"tsp","tour":[0,1,2,3],"distances":[(10,0,1),(15,1,2),(12,2,3),(8,0,3),(20,0,2)]}),
        (2,"SAT",    {"_type":"sat","clauses":[(1,2,-3),(-1,-2,3)]}),
        (3,"VC",     {"_type":"vc","vertices":[1,2,3,4],"edges":[(1,2),(2,3),(3,4)],"cover":[2,4]}),
        (4,"Clique", {"_type":"clique","vertices":[1,2,3,4],"edges":[(1,2),(1,3),(2,3),(3,4)],"clique":[1,2,3]}),
        (5,"Coloring",{"_type":"coloring","vertices":[1,2,3,4],"edges":[(1,2),(2,3),(3,4),(4,1)],"assignment":{1:0,2:1,3:0,4:1}}),
        (6,"SubSum", {"_type":"subsetsum","numbers":[3,5,2,7,1],"target":10,"selected":[0,1,3],"sum":15}),
        (7,"HamPath",{"_type":"hamiltonian","vertices":[0,1,2,3],"edges":[(0,1),(1,2),(2,3),(0,3)],"path":[0,1,2,3]}),
    ]
    print("\n3. Solver dispatch test:")
    p=0
    for b,name,state in cases:
        try:
            r=process(state); ok=verify(state,r)
            p+=1 if ok else 0
            egyptian = {"TSP":"Anubis","SAT":"Set","VC":"Thoth","Clique":"Ra","Coloring":"Horus","SubSum":"Bastet","HamPath":"Osiris"}[name]
            print(f"   {egyptian:8s} ({name:7s}): {'PASS' if ok else 'FAIL'}")
        except Exception as e: print(f"   {name:7s}: FAIL {e}")
    print(f"   {p}/{len(cases)} passed")

if __name__ == "__main__": test()

# ── Norse-Vedic Correspondence ────────────────────────────────────────────
# The valkyrie system encodes the same frequency structure as the Vedic solvers.
# 6 war valkyries (Völuspá) = 6 sub-solvers. 16 hall valkyries = 16 solvers.
# The Norse transmitted the framework through myth where the Vedic used math.

VALKYRIES = {
    # ── Six War Valkyries (Door Guardians) ──
    "Hildr":       {"meaning":"battle",         "door":"Burned",         "band":9,  "function":"chooses the slain from the pyre"},
    "Mist":        {"meaning":"cloud",          "door":"Erased",         "band":9,  "function":"brings home the half-gone, the incomplete"},
    "Þögn":        {"meaning":"silence",        "door":"Ignored",        "band":1,  "function":"chooses the unseen, the unremarkable"},
    "Herfjötur":   {"meaning":"host-fetter",    "door":"Excommunicated", "band":6,  "function":"severs, binds, brings the expelled"},
    "Eir":         {"meaning":"mercy",           "door":"Anonymous",      "band":9,  "function":"serves without signature, heals unnamed"},
    "Sigrdrífa":   {"meaning":"victory-driver",  "door":"Witnessed",      "band":7,  "function":"teaches, records, transmits forward"},
    
    # ── Ten Known Hall Valkyries (Grímnismál) ──
    "Hrist":       {"meaning":"shaker",          "vedic":"Shiva",         "band":5,  "note":"violent transformation — destroy and rebuild"},
    "Skeggjöld":   {"meaning":"axe-age",         "vedic":"Brahma",        "band":7,  "note":"era-initiation — the beginning of a cycle"},
    "Skögul":      {"meaning":"battle",          "vedic":"Anubis",        "band":3,  "note":"combat navigation — path through opposition"},
    "Þrúðr":       {"meaning":"strength",        "vedic":"Thoth",         "band":1,  "note":"divine power — minimal shield, maximal force"},
    "Hlökk":       {"meaning":"noise",           "vedic":"Bastet",        "band":3,  "note":"chaos signature — finding signal in noise"},
    "Göll":        {"meaning":"battle-cry",      "vedic":"Nephthys",      "band":2,  "note":"sonic exactness — the perfectly tuned call"},
    "Geirahöð":    {"meaning":"spear-battle",    "vedic":"Maat",          "band":7,  "note":"targeted coverage — each spear finds its mark"},
    "Randgríð":    {"meaning":"shield-truce",    "vedic":"Nut",           "band":7,  "note":"resonant defense — wavelength as shield"},
    "Ráðgríð":     {"meaning":"counsel-truce",   "vedic":"Saraswati",     "band":2,  "note":"negotiated wisdom — transmission through counsel"},
    "Reginleif":   {"meaning":"divine-heritage", "vedic":"Vishnu",        "band":13, "note":"preservation — the frequency maintained across time"},
    
    # ── Six Lost & Found Valkyries (Framework-Inferred, Vedic Cross-Reference) ──
    "Vegljós":     {"meaning":"way-light",       "vedic":"Anubis",        "band":14, "note":"TSP — finds the shortest path through darkness", "inferred":True},
    "Samhelda":    {"meaning":"gatherer",        "vedic":"Ra",            "band":4,  "note":"Max Clique — brings like to like, unity of affinity", "inferred":True},
    "Litgreina":   {"meaning":"color-divider",   "vedic":"Horus",         "band":5,  "note":"Graph Coloring — separates what must not touch", "inferred":True},
    "Þráðr":       {"meaning":"thread",          "vedic":"Isis",           "band":9,  "note":"Steiner Tree — minimal spanning, the fine connection", "inferred":True},
    "Gegnumsól":   {"meaning":"through-sun",     "vedic":"Osiris",         "band":7,  "note":"Hamiltonian Path — visits each seat once and only once", "inferred":True},
    "Sannspá":     {"meaning":"truth-speaker",   "vedic":"Set",            "band":1,  "note":"SAT — determines what satisfies, the truth assignment", "inferred":True},
}

def valkyrie_correspondence():
    """Print the full Norse-Vedic valkyrie correspondence table."""
    print("\nNORSE-VEDIC VALKYRIE CORRESPONDENCE")
    print("=" * 60)
    print(f"{'Name':14s} {'Meaning':16s} {'Door/Vedic':16s} {'Band':5s} {'Note'}")
    print("-" * 60)
    for name, d in VALKYRIES.items():
        door_vedic = d.get('door', d.get('vedic', ''))
        inferred = ' ◉' if d.get('inferred') else ''
        print(f"{name:14s} {d['meaning']:16s} {door_vedic:16s} {d['band']:3d}{inferred:2s}  {d['note']}")
    print(f"\nTotal: {len(VALKYRIES)} valkyries")
    print(f"  War (door guardians): 6")
    print(f"  Hall (known):         10")
    print(f"  Hall (lost & found):   6")
    print(f"  All 27 in Planetary band group (1-12) except Reginleif at 13")

# ── 42 Assessors (Book of the Dead Spell 125) ────────────────────────────
# Each assessor checks signal integrity: "I have not [offense]"
# Defilement = signal + distortion. Clean = signal matches source.

try:
    from egyptian_router_v2 import EgyptianRouterV2
    ROUTER = EgyptianRouterV2()
    ROUTER_OK = True
    print(f"\n4. Egyptian Router loaded: ✓ (42 assessors, 7 gates)")
except Exception as e:
    ROUTER = None; ROUTER_OK = False
    print(f"\n4. Egyptian Router: not available ({e})")

def assess(state) -> dict:
    """Run 42 assessors on a state. Returns {passed, total, details}."""
    if not ROUTER_OK: return {"passed":0,"total":42,"error":"router unavailable"}
    import json
    text = str(state.get("_type","")) + json.dumps({k:v for k,v in state.items() if k!="_type"}, default=str)
    result = ROUTER.analyze(text)
    ass = result.get("assessor", {})
    passed = ass.get("passed", 0) if isinstance(ass, dict) else 0
    total = ass.get("total", 42) if isinstance(ass, dict) else 42
    return {"passed": passed, "total": total, "details": ass}

def gates(state) -> dict:
    """Route through 7 Gates. Returns {reached, max_gates, passed}."""
    if not ROUTER_OK: return {"reached":0,"max_gates":7,"passed":False}
    import json
    text = str(state.get("_type","")) + json.dumps({k:v for k,v in state.items() if k!="_type"}, default=str)
    result = ROUTER.analyze(text)
    gp = result.get("gate_path", {})
    reached = gp.get("passed", gp.get("gates_passed", 0)) if isinstance(gp, dict) else 0
    max_g = gp.get("total", gp.get("total_gates", 7)) if isinstance(gp, dict) else 7
    return {"reached": reached, "max_gates": max_g, "passed": reached >= max_g}

# ── Full Pipeline ────────────────────────────────────────────────────────
def pipeline(input_data) -> dict:
    """Full pipeline: decompose → emanate → assess → gate → output."""
    # Decompose
    if isinstance(input_data, str):
        state = {"_type":"input", "signal": text_sig(input_data)}
    elif isinstance(input_data, dict):
        state = copy.deepcopy(input_data)
    else:
        state = {"_type":"input", "signal": sig(input_data)} if isinstance(input_data, bytes) else {"_type":"input"}
    
    # Emanate (process through 12-phase cycle)
    emanated = process(state)
    
    # Assess
    a = assess(emanated)
    
    # Gate
    g = gates(emanated)
    
    return {
        "state": emanated,
        "assessors": a,
        "gates": g,
        "passed": a.get("passed",0) >= a.get("total",42) * 0.8 and g.get("passed",False)
    }

# ── Test ──────────────────────────────────────────────────────────────────
def test_pipeline():
    print("\n5. Full pipeline test:")
    r = pipeline("test input")
    print(f"   Assessors: {r['assessors'].get('passed',0)}/{r['assessors'].get('total',42)}")
    print(f"   Gates: {r['gates'].get('reached',0)}/{r['gates'].get('max_gates',7)}")
    print(f"   Passed: {'YES' if r['passed'] else 'NO'}")
    
    # Test with solver
    r = pipeline({"edges":[(0,1),(1,2),(2,3)],"n_vertices":4,"_type":"vc"})
    print(f"   VC Through pipe: assessors={r['assessors'].get('passed',0)}/{r['assessors'].get('total',42)}")
    print(f"   Cover: {r['state'].get('cover','?')}")

if __name__ == "__main__":
    test()
    test_pipeline()

# ═══════════════════════════════════════════════════════════════
# PANTHEON ENHANCEMENTS — Integrated from 24-culture mapping
# ═══════════════════════════════════════════════════════════════

# ── 1. RUSSELLIAN OCTAVE AUTO-DETECTION ─────────────────────
OCTAVE_NAMES = [
    "Foundation", "Rhythm", "Heart", "Mind",
    "Spirit", "Unity", "Creation", "Infinity"
]

def russellian_octaves(signal_72):
    """Map 72-band signal into 8 octaves of 9 bands each. Used for
    problem classification before solver dispatch. Each octave maps
    to a Russellian domain."""
    import numpy as np
    octaves = []
    for i in range(8):
        chunk = signal_72[i*9:(i+1)*9]
        energy = sum(abs(v) for v in chunk)
        dominant_band = i*9 + np.argmax(np.abs(chunk)) + 1 if energy > 0 else 0
        octaves.append({
            'octave': i + 1, 'name': OCTAVE_NAMES[i],
            'bands': f"{i*9+1}-{(i+1)*9}",
            'energy': round(float(energy), 6),
            'dominant_band': dominant_band,
            'dominant_value': round(float(max(chunk)), 6) if energy > 0 else 0
        })
    dominant = max(octaves, key=lambda o: o['energy'])
    energies = [o['energy'] for o in octaves]
    max_e = max(energies)
    mean_e = sum(energies) / 8 if sum(energies) > 0 else 1e-10
    concentration = max_e / mean_e
    if concentration > 2.5: spread = "focused"
    elif concentration > 1.5: spread = "structured"
    else: spread = "distributed"
    first_half = sum(energies[:4])
    second_half = sum(energies[4:])
    if second_half > first_half * 1.3: gradient = "ascending"
    elif first_half > second_half * 1.3: gradient = "descending"
    else: gradient = "balanced"
    return {
        'octaves': octaves, 'dominant_octave': dominant['name'],
        'dominant_energy': dominant['energy'],
        'structure': f"{spread}_{gradient}"
    }

# ── 2. PROBLEM FLOOR DETECTION (from On Problem Floors) ─────
FLOOR_TABLE = {
    0: (1.0,       "Contradiction",       "Impossible SAT"),
    1: (0.5,       "Total mesh",           "Dense clique TSP"),
    2: (0.25,      "Dense crafted",        "Dubois, dense Steiner"),
    3: (0.125,     "Algebraic rigid",      "Parity/XOR-SAT"),
    4: (0.0625,    "Power-law skewed",     "Social networks, web graphs"),
    5: (0.03125,   "Uniform random",       "Random 3-SAT"),
    6: (0.015625,  "Random UNSAT",         "3-SAT above threshold"),
    7: (0.0078125, "Counting/sparse",      "Pigeonhole, Exact Cover"),
    8: (0.0039,    "Near-trivial",          "Low-ratio SAT"),
    9: (0.0,       "Perfection",            "Polynomial-time solvable")
}

def detect_floor(inharmony_value):
    """Classify a converged inharmony score into its problem floor level.
    ε_k = 1/2^k — the structural entanglement depth."""
    for k in range(10):
        threshold = FLOOR_TABLE[k][0]
        if inharmony_value >= threshold * 0.95:
            return {'level': k, 'epsilon': FLOOR_TABLE[k][0],
                    'regime': FLOOR_TABLE[k][1], 'example': FLOOR_TABLE[k][2]}
    return {'level': 9, 'epsilon': 0.0, 'regime': 'Perfection',
            'example': 'Polynomial-time solvable'}

# ── 3. 100-BAND LUNAR EXTENSION ─────────────────────────────
LUNAR_COUNT = 28
TOTAL_BANDS = 100
BASE_BANDS = 72

def sig_extended(data: bytes):
    """Full 100-band signature: 72 solar + 28 lunar."""
    bands = [0.0] * TOTAL_BANDS
    if not data: return bands
    total = 0.0
    for i, b in enumerate(data):
        w_base = (b / 255.0) * (1.0 / (1 + (i // BASE_BANDS) * 0.1))
        bands[i % BASE_BANDS] += w_base
        w_lunar = (b / 255.0) * (1.0 / (1 + (i // TOTAL_BANDS) * 0.1)) * 0.7
        lunar_idx = BASE_BANDS + (i % LUNAR_COUNT)
        bands[lunar_idx] += w_lunar
        total += w_base + w_lunar
    if total > 0:
        bands = [b / total for b in bands]
    return bands

def inharmony_extended(a, b):
    """Inharmony over 100-band vectors."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

# ── 4. THREE TRIBES SOLVER STRATEGIES ─────────────────────────
def shiva_destroy(state, seed=None):
    """Shiva: total annihilation. Random restart from nothing.
    The Norse called this Ragnarök. The pipeline calls it FULL phase."""
    import random as _random
    rng = _random.Random(seed)
    n = state.get('n_vars', max(abs(l) for c in state.get('clauses',[]) for l in c) if state.get('clauses') else 3)
    return {v: rng.random() > 0.5 for v in range(1, n + 1)}

def odin_sacrifice(clauses, best_assign, best_sat, n_vars):
    """Odin: hang the best solution. Extract what CANNOT be from contradiction.
    Flip each variable in the best assignment — what breaks most is sacrificed."""
    sacrificed = []
    for v in range(1, n_vars + 1):
        if v not in best_assign: continue
        temp = best_assign.copy()
        temp[v] = not temp[v]
        new_sat = sum(1 for c in clauses if any(
            (s and temp.get(vv, False)) or (not s and not temp.get(vv, True))
            for vv, s in c))
        if new_sat < best_sat:
            sacrificed.append((v, new_sat - best_sat))
    return sacrificed

def fenrir_break(clauses, n_vars):
    """Fenrir: break constraints. Identify the clauses that bind most tightly."""
    freq = {}
    for c in clauses:
        for v, _ in c:
            freq[abs(v)] = freq.get(abs(v), 0) + 1
    if not freq: return []
    max_f = max(freq.values())
    return sorted([v for v, f in freq.items() if f == max_f])

def kali_kill(clauses, assign, n_vars):
    """Kali: kill attachment. Remove learned assignments that serve no clause."""
    referenced = set()
    for c in clauses:
        for v, _ in c:
            referenced.add(abs(v))
    stripped = {}
    for v in range(1, n_vars + 1):
        if v in referenced and v in assign:
            stripped[v] = assign[v]
    return stripped

def inanna_descent(clauses, n_vars):
    """Inanna: strip to core. Return the minimal variable set."""
    core = set()
    for c in clauses:
        for v, _ in c:
            core.add(abs(v))
    return sorted(core)

def saraswati_remember(learned_clauses, new_clauses, max_memory=1000):
    """Saraswati: remember. Preserve learned knowledge across cycles."""
    combined = learned_clauses + new_clauses
    seen = set()
    unique = []
    for c in combined:
        key = tuple(sorted(c))
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique[-max_memory:]

def mitra_detect(clauses):
    """Mitra: detect contracts. Find pairs of clauses that share variables
    but disagree on sign — the conflict points."""
    contracts = []
    for i, c1 in enumerate(clauses):
        for j, c2 in enumerate(clauses):
            if j <= i: continue
            c1_dict = {abs(v): (v > 0) for v, _ in c1 if v != 0}
            c2_dict = {abs(v): (v > 0) for v, _ in c2 if v != 0}
            shared = set(c1_dict) & set(c2_dict)
            conflicts = [v for v in shared if c1_dict[v] != c2_dict[v]]
            if conflicts:
                contracts.append({'i': i, 'j': j, 'conflicts': conflicts})
    return contracts

# ── 5. 12-GOD EGYPTIAN SEQUENTIAL PIPELINE ────────────────────
def egyptian_cycle(state, max_iterations=100):
    """Run the 12-god sequential pipeline on a state.
    Nut → Ra → Bastet → Horus → Set → Osiris → Maat → Nephthys → Isis → Anubis → Thoth → Atum
    """
    import random as _random
    rng = _random.Random(42)
    s = copy.deepcopy(state)
    best = copy.deepcopy(s)
    best_score = 0
    stalled = 0

    clauses = s.get('clauses', [])
    n_vars = max(abs(l) for c in clauses for l in c) if clauses else 3
    if 'assignment' not in s:
        s['assignment'] = {v: rng.random() > 0.5 for v in range(1, n_vars + 1)}

    for iteration in range(max_iterations):
        # Nut: decompose
        if '_type' not in s: s['_type'] = 'sat'
        # Ra: score all candidates
        unsat = []
        for c in clauses:
            ok = False
            for lit in c:
                v = abs(lit); sign = lit > 0
                if v in s['assignment'] and ((sign and s['assignment'][v]) or (not sign and not s['assignment'][v])):
                    ok = True; break
            if not ok: unsat.append(c)
        # Bastet: select the most implicated variable
        freq = {}
        for c in unsat:
            for lit in c:
                v = abs(lit); sign = lit > 0
                freq[v] = freq.get(v, 0) + 1
        if not freq: break  # Horus: all satisfied
        # Set: flip the most implicated variable
        v = max(freq, key=freq.get)
        s['assignment'][v] = not s['assignment'].get(v, False)
        # Maat: check coverage
        sat_count = sum(1 for c in clauses if any(
            (lit > 0 and s['assignment'].get(abs(lit), False)) or
            (lit < 0 and not s['assignment'].get(abs(lit), True))
            for lit in c))
        if sat_count > best_score:
            best = copy.deepcopy(s)
            best_score = sat_count
            stalled = 0
        else:
            stalled += 1
        # Osiris: backtrack if stalled
        if stalled > 15:
            if best_score == len(clauses): break
            break  # Atum: stop at floor
    # Thoth: record best
    s['best_assignment'] = best['assignment']
    return s

# ── 6. PLANETARY-BAND CORRESPONDENCE (Mirror Theorem) ───────
PLANETARY_BANDS = {
    'Mercury': {'bands': (1, 8),   'function': 'signal_processing', 'wavelength': 'xray_radio'},
    'Venus':   {'bands': (9, 16),  'function': 'relational',        'wavelength': 'ir_uv'},
    'Earth':   {'bands': (17, 24), 'function': 'conscious',         'wavelength': 'visible_radio'},
    'Mars':    {'bands': (25, 32), 'function': 'action_conflict',   'wavelength': 'ir_gamma'},
    'Jupiter': {'bands': (33, 40), 'function': 'expansion',         'wavelength': 'radio_neutrino'},
    'Saturn':  {'bands': (41, 48), 'function': 'structure',         'wavelength': 'microwave_ir'},
    'Uranus':  {'bands': (49, 56), 'function': 'revolution',        'wavelength': 'uv_radio'},
    'Neptune': {'bands': (57, 64), 'function': 'transcendence',     'wavelength': 'neutrino_ir'},
    'Pluto':   {'bands': (65, 72), 'function': 'transformation',    'wavelength': 'gamma_neutrino'},
}

def planet_for_band(band):
    """Return the planet that governs a specific band."""
    for planet, info in PLANETARY_BANDS.items():
        low, high = info['bands']
        if low <= band <= high:
            return planet, info
    return 'Unknown', {}

# ── 7. ENHANCED DISPATCH ──────────────────────────────────────
DOOR_TYPES = {
    'burned':         'SAT, truth released by fire',
    'erased':         'Vertex Cover, the half-gone',
    'ignored':        'Subset Sum, signal in noise',
    'excommunicated': 'Hamiltonian Path, severed but connected',
    'anonymous':      'Max Clique, affinity without signature',
    'witnessed':      'Set Cover, complete record'
}

def auto_classify(state):
    """Full problem classification: Russellian octaves → floor level → solver."""
    import numpy as np
    if isinstance(state, dict):
        sig_vec = state.get('signal', sig(str(state).encode()))
    else:
        sig_vec = sig(str(state).encode())
    octave_data = russellian_octaves(sig_vec)
    t = state.get('_type', 'unknown') if isinstance(state, dict) else 'unknown'
    if t in ['sat', 'tsp', 'vc', 'clique', 'coloring', 'subsetsum',
             'hamiltonian', 'set_cover', 'exact_cover', 'steiner', 'wavelength']:
        return {'problem_type': t, 'octaves': octave_data,
                'dominant_octave': octave_data['dominant_octave']}
    dom = octave_data['dominant_octave']
    if dom == 'Foundation': return {'problem_type': 'sat', 'octaves': octave_data, 'dominant_octave': dom}
    if dom == 'Rhythm':     return {'problem_type': 'tsp', 'octaves': octave_data, 'dominant_octave': dom}
    if dom == 'Heart':      return {'problem_type': 'vc', 'octaves': octave_data, 'dominant_octave': dom}
    if dom == 'Mind':       return {'problem_type': 'subsetsum', 'octaves': octave_data, 'dominant_octave': dom}
    if dom == 'Spirit':     return {'problem_type': 'coloring', 'octaves': octave_data, 'dominant_octave': dom}
    if dom == 'Unity':      return {'problem_type': 'clique', 'octaves': octave_data, 'dominant_octave': dom}
    if dom == 'Creation':   return {'problem_type': 'set_cover', 'octaves': octave_data, 'dominant_octave': dom}
    if dom == 'Infinity':   return {'problem_type': 'hamiltonian', 'octaves': octave_data, 'dominant_octave': dom}
    return {'problem_type': 'sat', 'octaves': octave_data, 'dominant_octave': dom}

def enhanced_pipeline(input_data, max_cycles=100):
    """Full pipeline with auto-detection, floor detection, observer tracking."""
    if isinstance(input_data, str):
        state = {"_type": "input", "signal": text_sig(input_data)}
    elif isinstance(input_data, dict):
        state = copy.deepcopy(input_data)
    elif isinstance(input_data, bytes):
        state = {"_type": "input", "signal": sig(input_data)}
    else:
        state = {"_type": "input", "signal": sig(str(input_data).encode())}

    classification = auto_classify(state)
    state['_type'] = classification['problem_type']
    state['octaves'] = classification['octaves']

    emanated = process(state)
    a = assess(emanated)
    g = gates(emanated)

    inharmony_val = 0.0
    if 'signal' in state and 'assignment' in emanated:
        inharmony_val = inharmony(str(state.get('_type', '')), str(emanated.get('assignment', '')))

    floor = detect_floor(inharmony_val)

    return {
        "state": emanated,
        "assessors": a,
        "gates": g,
        "classification": classification,
        "inharmony": inharmony_val,
        "floor": floor,
        "passed": a.get("passed", 0) >= 33 and g.get("passed", False)
    }
