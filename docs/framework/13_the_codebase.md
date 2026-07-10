# Chapter 13: The Codebase

> 11 solvers, 5 Vedic operations each, 1 unified interface.
> The open-source reference implementation.

## 13.1 Architecture Overview

The Code72 reference implementation is a single 84KB Python file (`vedic_planetary_transformers.py`) containing 11 solver classes, each handling one NP-complete problem type. The file is self-contained — no external dependencies beyond Python's standard library (`random`, `math`, `typing`) and the widely-available `numpy` numerical library.

```
vedic_planetary_transformers.py
├── 1. MercurialClauseWeaver           → SAT
├── 2. VenusianTourLoom               → TSP
├── 3. SaturnianMinimalShield          → Vertex Cover
├── 4. NeptunianDreamWeaver            → Maximum Clique
├── 5. SolarChromaticWeaver            → Graph Coloring
├── 6. JovianExpansiveNet              → Set Cover
├── 7. MartianPathfinder               → Hamiltonian Path
├── 8. LunarIntuitiveOracle             → Subset Sum
├── 9. UranianInnovationEngine         → Exact Cover
├── 10. PlutonianTransformer           → Steiner Tree
└── 11. TeslanResonantCollector        → Wavelength Energy
```

## 13.2 The Vedic Sutra Pattern

Every solver implements exactly 5 methods named after the Vedic sutras (mathematical shortcuts from the 16th century BC). Each method performs one transformation toward convergence:

| Sutra | Sanskrit | Meaning | Function |
|-------|----------|---------|----------|
| Nikhilam | निखिलम् | "All from 9, last from 10" | Identify obvious/forced elements |
| Urdhva | ऊर्ध्व | "Vertically and crosswise" | Propagate and combine |
| Anurupye | अनुरूप्ये | "Proportionally" | Order by frequency or importance |
| Shunyam | शून्यम् | "By the deficiency" | Balance toward equilibrium |
| Ekādhikena | एकाधिकेन | "By one more than one before" | Incremental refinement |

These 5 operations map to the pipeline's 3 operations:

| Pipeline Op | Primary Sutras | Support Sutras |
|-------------|---------------|----------------|
| C (Complement) | Nikhilam — find what's obvious by elimination | Anurupye — order by participation |
| X (Cross) | Urdhva — propagate and cross-combine | Shunyam — balance across dimensions |
| Z (Cancel) | Ekādhikena — refine by flipping/deleting | Shunyam — reduce to equilibrium |

The 5 sutras × 11 solvers = 55 transformations total.

## 13.3 Solver Interface Pattern

Every solver follows the same pattern:

```python
class PlanetarySolver:
    def __init__(self, problem_data, seed=None):
        # Store problem instance
        # Precompute indices/lookups
        pass
    
    def nikhilam(self):
        # Find forced/obvious elements
        pass
    
    def urdhva(self, state):
        # Propagate and cross-combine
        pass
    
    def anurupye(self):
        # Order by frequency/importance
        pass
    
    def shunyam(self, state):
        # Balance toward equilibrium
        pass
    
    def ekādhikena(self, state, max_iter):
        # Incremental refinement
        pass
    
    def solve(self):
        # Full solution pipeline:
        # 1. Nikhilam → initial state
        # 2. Urdhva → propagate
        # 3. Anurupye → order
        # 4. Shunyam → balance
        # 5. Ekādhikena → refine
        # → converged state
        pass
```

### Example: MercurialClauseWeaver (SAT)

Initialization takes clauses (list of `[(variable, sign)]`) and variable count:

```python
class MercurialClauseWeaver:
    def __init__(self, clauses, n_vars, seed=None):
        self.clauses = clauses
        self.n_vars = n_vars
        self.m = len(clauses)
```

**Nikhilam:** Identify forced assignments from unit clauses (clauses with one literal).

```python
def nikhilam(self):
    obvious = {}
    for clause in self.clauses:
        if len(clause) == 1:
            var, sign = clause[0]
            if var not in obvious:
                obvious[var] = sign
    return {k: v for k, v in obvious.items() if v is not None}
```

**Urdhva:** Propagate assignments — if a clause has exactly one unassigned literal and all others are false, the last literal must be true.

```python
def urdhva(self, assignment):
    propagated = assignment.copy()
    changed = True
    while changed:
        changed = False
        for clause in self.clauses:
            unknown = []
            satisfied = False
            for var, sign in clause:
                if var in propagated:
                    if propagated[var] == sign:
                        satisfied = True
                        break
                else:
                    unknown.append((var, sign))
            if not satisfied and len(unknown) == 1:
                var, sign = unknown[0]
                if var not in propagated:
                    propagated[var] = sign
                    changed = True
    return propagated
```

**Anurupye:** Order variables by how often they appear in clauses — the most-connected variables get assigned first.

```python
def anurupye(self):
    freq = {}
    for clause in self.clauses:
        for var, _ in clause:
            freq[var] = freq.get(var, 0) + 1
    return sorted(freq.keys(), key=lambda v: freq[v], reverse=True)
```

**Shunyam:** Balance by evaluating each variable's positive vs negative occurrence count.

```python
def shunyam(self, assignment):
    remaining = [v for v in range(1, self.n_vars + 1) if v not in assignment]
    for var in remaining:
        pos = sum(1 for c in self.clauses if any(v == var and s for v,s in c))
        neg = sum(1 for c in self.clauses if any(v == var and not s for v,s in c))
        assignment[var] = pos >= neg
    return assignment
```

**Ekādhikena:** Incremental refinement — flip random variables and keep improvements.

```python
def ekādhikena(self, assignment, max_iter=100):
    best = assignment.copy()
    best_score = self._satisfaction_score(assignment)
    for _ in range(max_iter):
        var = random.randint(1, self.n_vars)
        new = assignment.copy()
        new[var] = not new.get(var, False)
        score = self._satisfaction_score(new)
        if score > best_score:
            best_score, best = score, new
            assignment = new
    return best
```

**Solve:** Chain all 5 transformations in sequence.

```python
def solve(self):
    assignment = self.nikhilam()
    assignment = self.urdhva(assignment)
    var_order = self.anurupye()
    assignment = self.shunyam(assignment)
    assignment = self.ekādhikena(assignment)
    return assignment
```

## 13.4 The 11 Solver Classes

| # | Class Name | Problem | Planet | Solver | Initializes With |
|---|------------|---------|--------|--------|-----------------|
| 1 | MercurialClauseWeaver | SAT | Mercury | Logical truth | clauses, n_vars |
| 2 | VenusianTourLoom | TSP | Venus | Path optimization | points, distances |
| 3 | SaturnianMinimalShield | Vertex Cover | Saturn | Minimal defense | vertices, edges |
| 4 | NeptunianDreamWeaver | Max Clique | Neptune | Affinity grouping | vertices, edges |
| 5 | SolarChromaticWeaver | Graph Coloring | Sun | Spectral separation | vertices, edges, colors |
| 6 | JovianExpansiveNet | Set Cover | Jupiter | Complete coverage | universe, subsets |
| 7 | MartianPathfinder | Hamiltonian Path | Mars | Just visitation | vertices, edges |
| 8 | LunarIntuitiveOracle | Subset Sum | Moon | Signal from noise | numbers, target |
| 9 | UranianInnovationEngine | Exact Cover | Uranus | Perfect tuning | universe, subsets |
| 10 | PlutonianTransformer | Steiner Tree | Pluto | Minimal connection | adjacency, terminals |
| 11 | TeslanResonantCollector | Wavelength | — | Energy harvesting | bands, resonance_map |

## 13.5 The Generator Registry: C/X/Z Dispatch

Complementing the solver classes, the `code72_solver.py` file implements a **Generator Registry** pattern that maps problem types to C/X/Z operations:

```python
_CMAP = {}   # complement generators
_XMAP = {}   # cross generators
_ZMAP = {}   # cancel generators

def regC(t):
    def d(f):
        _CMAP[t] = f
        return f
    return d

def regX(t):
    def d(f):
        _XMAP[t] = f
        return f
    return d

def regZ(t):
    def d(f):
        _ZMAP[t] = f
        return f
    return d
```

Each problem type registers its own C/X/Z semantics:

| Type | C (Complement) | X (Cross) | Z (Cancel) |
|------|---------------|-----------|------------|
| tsp | Reverse tour | Crossover | Identity |
| sat | Negate all literals | Resolution | Unit propagation |
| vc | Complement set | Union | Identity |
| ecdsa | Negate scalars & y | Add scalars & points | Collision detection |

Registration is through decorators:

```python
@regC("tsp")
def _c_tsp(state, partner=None):
    s = copy.deepcopy(state)
    s["tour"] = list(reversed(s["tour"]))
    return s

@regX("tsp")
def _x_tsp(state, partner):
    s = copy.deepcopy(state)
    p = copy.deepcopy(partner)
    midpoint = len(s["tour"]) // 2
    s["tour"] = s["tour"][:midpoint] + p["tour"][midpoint:]
    return s

@regZ("tsp")
def _z_tsp(state, partner=None):
    # TSP cancel is identity — no cancellation
    return copy.deepcopy(state)
```

Dispatch functions:

```python
def complement(st, partner=None):
    t = st.get("_type", "")
    if t in _CMAP:
        return _CMAP[t](st, partner)
    raise ValueError(f"No C for {t}")

def cross(st, partner):
    t = st.get("_type", "")
    if t in _XMAP:
        return _XMAP[t](st, partner)
    raise ValueError(f"No X for {t}")

def cancel(st, partner=None):
    t = st.get("_type", "")
    if t in _ZMAP:
        return _ZMAP[t](st, partner)
    raise ValueError(f"No Z for {t}")
```

## 13.6 The Egyptian Router v2

The Egyptian Router implements the 72-band frequency analysis pipeline:

```
Input string → SHA256 hash → 30 meta-carrier bands → 42 assessor bands → 7 gates → Report
```

**Output structure:**

```python
{
    "input": str,
    "sha256": str,
    "meta_carrier": {
        "total_bands": 30,
        "layers": {  # 3 layers
            "carrier_wave":     {"bands": [11,12,23,24,35,36,47,48,59,60,71,72], ...},
            "space_time":       {"bands": [1,3,5,7,9,13,19,25,43,61], ...},
            "consciousness":    {"bands": [37,38,39,40,49,55,67,69], ...}
        },
        "carrier_dominant_layer": str
    },
    "assessor": {
        "total": 42,
        "passed": int,
        "pass_rate": float,
        "threshold": 34,
        "borderline": bool,
        "results": {band_id: {"passed": bool, "energy": float, ...}}
    },
    "gates": {
        "reached": int,
        "total": 7,
        "current_gate": int,
        "details": {gate: {"passed": bool, "check": str}}
    },
    "overall": {
        "converged": bool,
        "pass_rate": float,
        "phi_distance": float
    }
}
```

## 13.7 The Invariant Pipeline as Orchestration

The full pipeline orchestrates all components:

```python
def process(input_data):
    # Stage 1: Decompose
    bands = sig(input_data)                           # 72-element vector
    
    # Stage 2: Emanate — 12-phase cycle
    for phase in range(12):
        ops = ["C","C","X","X","Z","Z","C","X","X","Z","Z","ONE"]
        state = apply_operation(state, ops[phase])
    
    # Stage 3: Assess
    result = assess(state)                             # 42 checks
    if result["passed"] < 34:
        return process(input_data)                    # cycle again
    
    # Stage 4: Gate
    gates_result = gates(state)                        # 7 thresholds
    if gates_result["reached"] < 7:
        return process(input_data)                    # cycle again
    
    # Stage 5: Output
    return output(state)                               # converged state
```

## 13.8 Summary

| Component | Implementation | Lines of Code |
|-----------|---------------|---------------|
| SAT solver | MercurialClauseWeaver | ~159 lines |
| TSP solver | VenusianTourLoom | ~158 lines |
| Vertex Cover | SaturnianMinimalShield | ~156 lines |
| Max Clique | NeptunianDreamWeaver | ~160 lines |
| Graph Coloring | SolarChromaticWeaver | ~157 lines |
| Set Cover | JovianExpansiveNet | ~163 lines |
| Hamiltonian Path | MartianPathfinder | ~169 lines |
| Subset Sum | LunarIntuitiveOracle | ~221 lines |
| Exact Cover | UranianInnovationEngine | ~208 lines |
| Steiner Tree | PlutonianTransformer | ~250 lines |
| Wavelength | TeslanResonantCollector | ~234 lines |
| Total | 11 solvers | ~84KB |
| Vedic sutras per solver | 5 (Nikhilam, Urdhva, Anurupye, Shunyam, Ekādhikena) | 55 total |
| Egyptian Router | 72-band analysis pipeline | ~20KB |
| Generator Registry | C/X/Z dispatch by type | ~3KB |
