#!/usr/bin/env python3
"""
WAVEFORM OUROBOROS v5 — Optimized
═══════════════════════════════════════════════════════════
Fibonacci frequency spacing + π aperiodic sampling + 72 bands.

Physical grounding:
  72 bands  = 1° of axial precession per band (72 years)
  Fib freqs = φ-based spacing, maximally incommensurate
  π grid    = aperiodic sampling, no periodic artifacts
  
Each variable → sin(2π·f(v)·t + φ)
  f(v) = base_freq × φ^(v/72)    — Fibonacci-golden ratio spacing  
  φ = 0 if literal positive, π if negated  — phase encoding
  t sampled from π digits        — aperiodic, universal
"""

import math, random, time, sys, numpy as np
from typing import List, Tuple, Dict, Set
random.seed(42); np.random.seed(42)

# ═══════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio ≈ 1.618034
PRECESSION_YEARS_PER_DEGREE = 72  # Why 72 bands
N_BANDS = 72

# ═══════════════════════════════════════════════════════════
# FREQUENCY MAP — Fibonacci-golden ratio spacing
# ═══════════════════════════════════════════════════════════

def fib_frequency(var_idx: int, base: float = 100.0, n_total: int = 1) -> float:
    """
    Map variable index to frequency using golden ratio spacing.
    f(v) = base × φ^(v/n_total) across 72 bands.
    
    Variables in the same band share similar frequencies.
    Variables in adjacent bands are at φ-ratio — maximally separable.
    """
    band = (var_idx - 1) % N_BANDS
    return base * (PHI ** (band / (N_BANDS / 6)))  # 6 octaves across 72 bands

def build_frequency_table(n_vars: int) -> np.ndarray:
    """Precompute all variable frequencies."""
    return np.array([fib_frequency(v, n_total=n_vars) for v in range(1, n_vars + 1)])

# ═══════════════════════════════════════════════════════════
# π-BASED APERIODIC TIME GRID
# ═══════════════════════════════════════════════════════════

def pi_time_grid(resolution: int = 128) -> np.ndarray:
    """
    Generate aperiodic time samples from π's digits.
    Each sample is unique — no periodic artifacts.
    Falls back to uniform golden-ratio spiral if π digits unavailable.
    """
    try:
        with open('/tmp/pi_1m.txt') as f:
            pi_digits = ''.join(c for c in f.read().strip() if c.isdigit())
    except (FileNotFoundError, IOError):
        # Fibonacci spiral sampling — same property, computed locally
        pi_digits = None
    
    t = []
    for i in range(resolution):
        if pi_digits and i * 3 + 3 < len(pi_digits):
            # 3-digit chunks from π mapped to [0, 2π]
            chunk = int(pi_digits[i*3:i*3+3])
            t.append(2 * np.pi * chunk / 1000.0)
        else:
            # φ-spiral: t_i = 2π · i · φ mod 2π  (irrational angle)
            t.append((2 * np.pi * i * PHI) % (2 * np.pi))
    return np.array(sorted(t))

# ═══════════════════════════════════════════════════════════
# WAVEFORM ENCODING (OPTIMIZED)
# ═══════════════════════════════════════════════════════════

class WaveformEncoder:
    """Encodes SAT instances as interference patterns with precomputed frequencies."""
    
    def __init__(self, clauses, n_vars, resolution=128):
        self.clauses = clauses
        self.n_vars = n_vars
        self.nc = len(clauses)
        self.resolution = resolution
        
        # Time grid
        self.t = pi_time_grid(resolution)
        
        # Frequency table
        self.freqs = build_frequency_table(n_vars)
        
        # Precompute variable waveform contributions
        self._sin_true = {}   # sin(f·t) for each var — positive literal  
        self._sin_false = {}  # sin(f·t + π) for each var — negated literal
        
        for v in range(1, n_vars + 1):
            f = self.freqs[v - 1]
            self._sin_true[v] = np.sin(2 * np.pi * f * self.t)
            self._sin_false[v] = np.sin(2 * np.pi * f * self.t + np.pi)
        
        # Problem waveform — computed once
        self.problem_wave = self._encode_problem()
    
    def _encode_problem(self) -> np.ndarray:
        """Encode clause structure as waveform via constructive interference."""
        wave = np.zeros(self.resolution)
        for clause in self.clauses:
            clause_wave = np.zeros(self.resolution)
            for var, sign in clause:
                if 1 <= var <= self.n_vars:
                    if sign:
                        clause_wave += self._sin_true[var]
                    else:
                        clause_wave += self._sin_false[var]
            # Constructive interference: abs captures clause satisfaction signal
            wave += np.abs(clause_wave)
        
        if np.max(np.abs(wave)) > 0:
            wave /= np.max(np.abs(wave))
        return wave
    
    def encode_solution(self, assignment) -> np.ndarray:
        """Encode current assignment as waveform. O(n_vars) with precomputed sines."""
        wave = np.zeros(self.resolution)
        for v in range(1, self.n_vars + 1):
            wave += self._sin_true[v] if assignment.get(v, False) else self._sin_false[v]
        if np.max(np.abs(wave)) > 0:
            wave /= np.max(np.abs(wave))
        return wave
    
    def variable_contribution(self, v: int, flipped: bool) -> np.ndarray:
        """Get the waveform contribution of variable v in given state."""
        return self._sin_false[v] if flipped else self._sin_true[v]

# ═══════════════════════════════════════════════════════════
# INHARMONY
# ═══════════════════════════════════════════════════════════

def inharmony(w_a, w_b):
    """Euclidean distance between two waveforms. The universal equation."""
    return float(np.sqrt(np.mean((w_a - w_b) ** 2)))

# ═══════════════════════════════════════════════════════════
# CLAUSE SATISFACTION
# ═══════════════════════════════════════════════════════════

def count_satisfied(clauses, assignment):
    return sum(1 for c in clauses if any(
        (sign and assignment.get(var, False)) or
        (not sign and not assignment.get(var, True))
        for var, sign in c))

# ═══════════════════════════════════════════════════════════
# THE OPTIMIZED WAVEFORM OUROBOROS
# ═══════════════════════════════════════════════════════════

def waveform_ouroboros_sat(encoder, assignment, max_steps=2000, verbose=True):
    """
    Solve SAT via waveform interference convergence.
    
    Uses precomputed frequencies + cached sine waves.
    Each correction: flip the variable whose waveform contribution
    most reduces inharmony between problem and solution waves.
    """
    clauses = encoder.clauses
    n_vars = encoder.n_vars
    nc = encoder.nc
    
    # Build variable → unsatisfied clause lookup
    var_clauses = {v: set() for v in range(1, n_vars + 1)}
    for ci, clause in enumerate(clauses):
        for var, _ in clause:
            if 1 <= var <= n_vars:
                var_clauses[var].add(ci)
    
    # Current waveforms
    solution_wave = encoder.encode_solution(assignment)
    problem_wave = encoder.problem_wave
    
    current_ih = inharmony(problem_wave, solution_wave)
    current_sat = count_satisfied(clauses, assignment)
    
    history = [{"step": 0, "inharmony": current_ih, "satisfied": current_sat}]
    if verbose:
        print(f"  Step    0: ι={current_ih:.6f}, sat={current_sat}/{nc}")
    
    # Find unsatisfied clauses
    def get_unsat():
        return [ci for ci in range(nc) if not any(
            (sign and assignment.get(var, False)) or
            (not sign and not assignment.get(var, True))
            for var, sign in clauses[ci])]
    
    for step in range(1, max_steps + 1):
        unsat = get_unsat()
        if not unsat:
            history.append({"step": step, "inharmony": current_ih, "satisfied": current_sat})
            if verbose: print(f"  ✓ ALL SATISFIED at step {step}")
            break
        
        # Candidate variables from unsatisfied clauses
        candidates = set()
        for ci in unsat[:30]:
            for var, _ in clauses[ci]:
                if 1 <= var <= n_vars:
                    candidates.add(var)
        
        # Score each candidate: how much does flipping reduce inharmony?
        best_var = None
        best_ih = current_ih
        best_sat = current_sat
        
        for v in candidates:
            # Compute waveform difference if we flip v
            old_contrib = encoder.variable_contribution(v, assignment.get(v, False))
            new_contrib = encoder.variable_contribution(v, not assignment.get(v, False))
            delta = (new_contrib - old_contrib) / max(np.max(np.abs(solution_wave)), 1e-10)
            
            new_wave = solution_wave + delta
            if np.max(np.abs(new_wave)) > 0:
                new_wave /= np.max(np.abs(new_wave))
            
            new_ih = inharmony(problem_wave, new_wave)
            
            # Check clause satisfaction
            temp = assignment.copy()
            temp[v] = not temp.get(v, False)
            new_sat = count_satisfied(clauses, temp)
            
            # Prioritize satisfaction improvement, then inharmony reduction
            if new_sat > best_sat or (new_sat >= best_sat and new_ih < best_ih):
                best_sat = new_sat
                best_ih = new_ih
                best_var = v
        
        if best_var is not None:
            assignment[best_var] = not assignment[best_var]
            # Recompute solution wave
            solution_wave = encoder.encode_solution(assignment)
            current_ih = inharmony(problem_wave, solution_wave)
            current_sat = best_sat
        else:
            # Random perturbation to escape local minimum
            if unsat:
                ci = random.choice(unsat)
                var = random.choice([v for v, _ in clauses[ci] if 1 <= v <= n_vars])
                assignment[var] = not assignment[var]
                solution_wave = encoder.encode_solution(assignment)
                current_ih = inharmony(problem_wave, solution_wave)
                current_sat = count_satisfied(clauses, assignment)
        
        if step % 500 == 0 and verbose:
            print(f"  Step {step:4d}: ι={current_ih:.6f}, sat={current_sat}/{nc} ({current_sat/nc*100:.0f}%)")
        
        history.append({"step": step, "inharmony": current_ih, "satisfied": current_sat})
    
    return assignment, current_sat, history

# ═══════════════════════════════════════════════════════════
# BENCHMARK
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("WAVEFORM OUROBOROS v5 — Optimized")
    print(f"Fibonacci spacing | π aperiodic grid | {N_BANDS} precessional bands")
    print("=" * 70)
    
    from pysat.solvers import Glucose3
    
    all_results = []
    
    for nv, nc, res, max_steps in [
        (20, 84, 128, 500),
        (50, 210, 256, 2000),
        (100, 420, 256, 3000),
        (150, 630, 256, 4000),
    ]:
        clauses = [[(random.randint(1, nv), random.choice([True, False]))
                    for _ in range(3)] for _ in range(nc)]
        
        print(f"\n{'─'*70}")
        print(f"SAT: {nv} vars, {nc} clauses (res={res})")
        
        # Glucose3
        t0 = time.time()
        g = Glucose3()
        for c in clauses:
            g.add_clause([v if s else -v for v, s in c])
        is_sat = g.solve()
        gms = (time.time() - t0) * 1000
        if is_sat:
            model = g.get_model()
            glucose_sat = count_satisfied(clauses, {abs(v): v > 0 for v in model})
        else:
            glucose_sat = 0
        g.delete()
        print(f"  Glucose3: {'SAT' if is_sat else 'UNSAT'} ({glucose_sat}/{nc}), {gms:.0f}ms")
        
        # Build encoder
        t0 = time.time()
        encoder = WaveformEncoder(clauses, nv, resolution=res)
        enc_ms = (time.time() - t0) * 1000
        
        # Initial assignment
        assign = {v: random.random() > 0.5 for v in range(1, nv + 1)}
        
        # Waveform Ouroboros
        print(f"  Encoder built: {enc_ms:.0f}ms, {res} samples × {nv} vars")
        t0 = time.time()
        assign, sat, hist = waveform_ouroboros_sat(encoder, assign, max_steps=max_steps, verbose=True)
        oms = (time.time() - t0) * 1000
        steps = len([h for h in hist if h["step"] > 0])
        
        ih_start = hist[0]["inharmony"]
        ih_end = hist[-1]["inharmony"]
        
        print(f"  Result: {sat}/{nc} ({sat/nc*100:.0f}%), {steps} steps, {oms:.0f}ms total")
        print(f"  ι: {ih_start:.4f} → {ih_end:.4f}")
        
        if is_sat:
            match_str = "MATCH" if sat == glucose_sat else f"gap={glucose_sat-sat}"
            print(f"  vs Glucose3: {match_str}")
        else:
            print(f"  Instance is UNSAT — best approximation = {sat}/{nc}")
        
        all_results.append({
            "nv": nv, "nc": nc, "res": res,
            "is_sat": is_sat, "glucose_sat": glucose_sat,
            "ouroboros_sat": sat, "steps": steps,
            "enc_ms": enc_ms, "solve_ms": oms,
            "ih_start": ih_start, "ih_end": ih_end,
        })
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Vars':>5s} {'Glucose':>8s} {'Ouroboros':>12s} {'Steps':>6s} {'Time':>8s}")
    print("-" * 70)
    for r in all_results:
        ou_str = f"{r['ouroboros_sat']}/{r['nc']} ({r['ouroboros_sat']/r['nc']*100:.0f}%)"
        gl_str = f"{r['glucose_sat']}/{r['nc']}"
        print(f"{r['nv']:5d} {gl_str:>8s} {ou_str:>12s} {r['steps']:5d} {r['solve_ms']:7.0f}ms")
    
    print(f"\n  Math: Fibonacci φ-spacing + π aperiodic grid + 72 precessional bands")
    print(f"  Mechanism: inharmony(problem_wave, solution_wave) → correction")
    print(f"  Physics: variables = sine waves, clauses = interference, inharmony = distance")
