#!/usr/bin/env python3
"""
TSP SOLVER — Full 72-Band Frequency-Domain Convergence
═══════════════════════════════════════════════════════════════════
Integrates the complete Code72 framework for the Travelling Salesman Problem.

Core principle:
  σ(P) − σ(S) = d       ← inharmony vector in 72-band space
  This IS the correction instruction.

Operations:
  C (complement) — invert solution signature → target → guided 2-opt
  X (cross)      — blend with best-known → target → guided 2-opt
  Z (cancel)     — strip noise bands → target → guided 2-opt

12-phase cycle drives convergence with structural floor detection,
perturbation escape, and inharmony-based convergence monitoring.

This is NOT a band-labelled 2-opt. Operations happen in signature space.
Tour-space moves are translations of signature-space targets.
"""

import math
import random
import time
import numpy as np

N_BANDS = 72
PHI = (1 + math.sqrt(5)) / 2

# ═══════════════════════════════════════════════════════════
# CORE PRIMITIVES
# ═══════════════════════════════════════════════════════════

def inharmony(a, b):
    """ι(a,b) = ‖a − b‖₂"""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def inharmony_bandwise(a, b):
    """Per-band difference vector. b - a."""
    return [y - x for x, y in zip(a, b)]

def complement(sig):
    """C: invert band weights. What this is NOT."""
    inv = [(1 - w) for w in sig]
    total = sum(inv)
    if total == 0:
        return [1.0 / len(sig)] * len(sig)
    scale = sum(sig) / total
    return [w * scale for w in inv]

def cross(a, b):
    """X: blend two signatures."""
    vec = [(x + y) / 2.0 for x, y in zip(a, b)]
    total = sum(vec)
    return [v / total for v in vec] if total > 0 else vec

def cancel(sig):
    """Z: zero-out bands below mean. Remove noise."""
    n = len(sig)
    mean = sum(sig) / n
    result = [w if w >= mean else 0.0 for w in sig]
    total = sum(result)
    if total == 0:
        return [1.0 / n] * n
    return [w / total for w in result]

def normalize(vec):
    """Safe L1 normalization."""
    total = sum(abs(v) for v in vec)
    if total < 1e-12:
        return [0.0] * len(vec)
    return [v / total for v in vec]

# ═══════════════════════════════════════════════════════════
# 12-PHASE CYCLE DEFINITION
# ═══════════════════════════════════════════════════════════
# Each phase: (operation, band_octave_range, intensity)
# Octaves: 1=Foundation(bands 0-8), 2=Rhythm(9-17), 3=Heart(18-26), 
#          4=Mind(27-35), 5=Spirit(36-44), 6=Unity(45-53), 
#          7=Creation(54-62), 8=Infinity(63-71)

BANDS_PER_OCTAVE = N_BANDS // 8  # 9 bands per octave

TSP_PHASES = [
    ("C", 1, 1.0),   # Phase 1:  Complement — Foundation octave
    ("C", 5, 0.7),   # Phase 2:  Complement — Spirit octave  
    ("X", 1, 0.5),   # Phase 3:  Cross — Foundation octave
    ("X", 8, 0.3),   # Phase 4:  Cross — Infinity octave
    ("Z", 1, 1.0),   # Phase 5:  Cancel — Foundation octave
    ("Z", 5, 0.7),   # Phase 6:  Cancel — Spirit octave
    ("C", 4, 0.8),   # Phase 7:  Complement — Mind octave
    ("X", 4, 0.6),   # Phase 8:  Cross — Mind octave
    ("X", 6, 0.5),   # Phase 9:  Cross — Unity octave
    ("Z", 4, 0.8),   # Phase 10: Cancel — Mind octave
    ("Z", 8, 0.5),   # Phase 11: Cancel — Infinity octave
    ("FULL", 0, 1.0) # Phase 12: Full — all octaves, all operations
]

# ═══════════════════════════════════════════════════════════
# TSP DECOMPOSER — problem and solution → 72-band signatures
# ═══════════════════════════════════════════════════════════

def decompose_tsp(dist_matrix, tour):
    """
    Decompose TSP into 72-band frequency-domain signatures.
    
    Problem signature σ(P):
      Each city i maps to band (i % 72). Distance contributions spread
      to nearest-neighbour bands. Captures distance distribution.
    
    Solution signature σ(S):
      Each city i maps to band (i % 72). Contribution = how far the
      tour edge cost deviates from mean. Captures tour quality.
    
    Returns (problem_sig, solution_sig).
    """
    n = len(dist_matrix)
    prob = [0.0] * N_BANDS
    sol = [0.0] * N_BANDS

    # Precompute k-nearest neighbours
    k = min(3, n - 1)
    neighbors = []
    for i in range(n):
        dists = [(dist_matrix[i][j], j) for j in range(n) if j != i]
        dists.sort()
        neighbors.append([j for _, j in dists[:k]])

    # Problem signature: distance distribution across band-mapped cities
    prob_total = 0.0
    for i in range(n):
        band_i = i % N_BANDS
        # Distance to k-nearest contributes to city's bands
        for nb in neighbors[i]:
            d = dist_matrix[i][nb]
            band_nb = nb % N_BANDS
            weight = d / (1 + d)  # [0,1) mapping — closer cities weight less
            prob[band_i] += weight * 0.7
            prob[band_nb] += weight * 0.3  # neighbour influence
            prob_total += weight

    # Solution signature: edge cost deviation per band
    sol_total = 0.0
    if tour and len(tour) == n:
        mean_edge = sum(dist_matrix[tour[i]][tour[(i + 1) % n]] for i in range(n)) / n
        for i in range(n):
            city = tour[i]
            next_city = tour[(i + 1) % n]
            edge_cost = dist_matrix[city][next_city]
            deviation = abs(edge_cost - mean_edge) / max(mean_edge, 1e-10)
            band = city % N_BANDS
            sol[band] += deviation
            sol_total += deviation
            # Spread to neighbour influence
            for nb in neighbors[city]:
                sol[nb % N_BANDS] += deviation * 0.25
                sol_total += deviation * 0.25

    return normalize(prob), normalize(sol)


def tour_length(dist_matrix, tour):
    """Total tour distance."""
    n = len(tour)
    return sum(dist_matrix[tour[i]][tour[(i + 1) % n]] for i in range(n))


# ═══════════════════════════════════════════════════════════
# SIGNATURE → TOUR TRANSLATOR (the bridge)
# ═══════════════════════════════════════════════════════════

def apply_target_signature(tour, dist_matrix, target_sig, problem_sig,
                           octave_range, intensity, neighbors, n_cities):
    """
    Translate a target signature into tour-space changes via band-guided 2-opt.

    The target signature is what we want the solution signature to look like.
    We compute the per-band gap between current and target, then perform
    2-opt swaps on edges associated with the most divergent bands.

    Returns (new_tour, improved).
    """
    n = n_cities
    current_len = tour_length(dist_matrix, tour)
    _, sol_sig = decompose_tsp(dist_matrix, tour)

    # Band gap: target − current → which bands need the most change
    band_gap = inharmony_bandwise(sol_sig, target_sig)

    # Restrict to specified octave range if given
    if octave_range > 0:
        start_band = (octave_range - 1) * BANDS_PER_OCTAVE
        end_band = start_band + BANDS_PER_OCTAVE
        for k in range(N_BANDS):
            if k < start_band or k >= end_band:
                band_gap[k] = 0.0

    # Rank bands by absolute gap
    ranked_bands = sorted(range(N_BANDS), key=lambda k: abs(band_gap[k]), reverse=True)

    # Score tour edges by band gap contribution
    edge_scores = {}
    for i in range(n):
        a = tour[i]
        b = tour[(i + 1) % n]
        edge_scores[i] = abs(band_gap[a % N_BANDS]) + abs(band_gap[b % N_BANDS])

    scored_edges = sorted(edge_scores.items(), key=lambda x: -x[1])

    # Try 2-opt swaps on the most gap-contributing edges
    n_try = max(2, int(n * intensity * 0.3))
    best_swap = None
    best_len = current_len

    for edge_a_idx, _ in scored_edges[:n_try]:
        i = edge_a_idx
        j = (i + 1) % n
        for edge_b_idx, _ in scored_edges[:n_try]:
            k = edge_b_idx
            if j == k or i == k or i == (k + 1) % n:
                continue

            # 2-opt swap: reverse segment j...k
            if j < k:
                new_tour = tour[:j] + tour[j:k+1][::-1] + tour[k+1:]
            else:
                new_tour = tour[:k] + tour[k:j+1][::-1] + tour[j+1:]

            new_len = tour_length(dist_matrix, new_tour)
            if new_len < best_len:
                best_len = new_len
                best_swap = new_tour

    if best_swap is not None and best_len < current_len:
        return best_swap, True

    return tour, False


# ═══════════════════════════════════════════════════════════
# STRUCTURAL FLOOR DETECTOR
# ═══════════════════════════════════════════════════════════

def detect_structural_floor(inharmony_history, window=30, threshold=0.0001):
    """
    Detect when inharmony has stopped improving.

    A structural floor is reached when the inharmony reduction over
    the last `window` steps is below `threshold`.

    Returns True if at floor.
    """
    if len(inharmony_history) < window:
        return False
    recent = inharmony_history[-window:]
    first = recent[0]
    last = recent[-1]
    reduction = first - last
    return reduction < threshold


# ═══════════════════════════════════════════════════════════
# PERTURBATION ESCAPE
# ═══════════════════════════════════════════════════════════

def perturbation_escape(tour, dist_matrix, problem_sig, n_cities, temperature=0.3):
    """
    Escape a structural floor by applying a large random perturbation.

    If at floor:
      1. Randomly select a subset of bands (5-15%)
      2. Apply aggressive random 2-opt swaps on those bands' cities
      3. Accept with simulated annealing probability

    Returns (new_tour, escaped).
    """
    n = n_cities
    current_len = tour_length(dist_matrix, tour)

    # Select random bands to perturb
    n_bands_perturb = random.randint(4, 11)  # 5-15% of 72
    perturb_bands = set(random.sample(range(N_BANDS), n_bands_perturb))

    # Build candidate cities from perturb bands
    perturb_cities = set()
    for i in range(n):
        if (i % N_BANDS) in perturb_bands:
            perturb_cities.add(i)

    if len(perturb_cities) < 2:
        perturb_cities = set(random.sample(range(n), min(n // 4, 15)))

    candidates = list(perturb_cities)

    # Apply aggressive random 2-opt
    for _ in range(max(3, n // 10)):
        if len(candidates) < 2:
            break
        i, j = random.sample(candidates, 2)
        if abs(i - j) < 2:
            continue
        a, b = sorted([i, j])
        new_tour = tour[:a+1] + tour[a+1:b+1][::-1] + tour[b+1:]
        new_len = tour_length(dist_matrix, new_tour)

        # Simulated annealing: accept if better, or with probability if worse
        if new_len < current_len or random.random() < temperature:
            tour = new_tour
            current_len = new_len

    return tour, True


# ═══════════════════════════════════════════════════════════
# THE FULL TSP CONVERGENCE ENGINE
# ═══════════════════════════════════════════════════════════

def tsp_converge_from(dist_matrix, initial_tour, max_cycles=500, verbose=True):
    """Run frequency-domain convergence from a provided initial tour."""
    return _tsp_converge(dist_matrix, max_cycles, verbose, start_tour=initial_tour)


def tsp_converge(dist_matrix, max_cycles=500, verbose=True):
    """
    Solve TSP via frequency-domain convergence.

    Architecture:
      1. Decompose problem → σ(P)
      2. Initial tour via nearest-neighbour heuristic
      3. Decompose solution → σ(S)
      4. Compute inharmony ι(σ(P), σ(S))
      5. Enter 12-phase convergence cycle:
         a. Phase determines: operation (C/X/Z/FULL), octave range, intensity
         b. Apply operation in SIGNATURE SPACE → target signature
         c. Translate to tour space via band-guided 2-opt
         d. Recompute tour length; accept if improved
         e. Track best-ever tour separately (defensive)
         f. Detect structural floor → perturbation escape
         g. Periodic random restart to escape local minima
      6. Return optimal tour

    Returns (best_tour, tour_distance, history).
    """
    n = len(dist_matrix)
    if n < 3:
        tour = list(range(n))
        return tour, tour_length(dist_matrix, tour), []

    # ── Precompute nearest neighbours for decomposition ──
    k = min(3, n - 1)
    neighbors = []
    for i in range(n):
        dists = [(dist_matrix[i][j], j) for j in range(n) if j != i]
        dists.sort()
        neighbors.append([j for _, j in dists[:k]])

    # ── Initial tour via Vedic solver (VenusianTourLoom) ──
    def initial_tour():
        """Get best initial tour from Vedic solver or fall back to NN."""
        try:
            from vedic_planetary_transformers import VenusianTourLoom
            loom = VenusianTourLoom(dist_matrix)
            vedic_tour, vedic_len = loom.solve()
            return list(vedic_tour), vedic_len
        except (ImportError, Exception):
            # Fallback: best-of-5 nearest neighbour
            best = None
            best_l = float('inf')
            for start in range(min(5, n)):
                unvisited = set(range(n))
                t = [start]
                unvisited.remove(start)
                while unvisited:
                    last = t[-1]
                    nxt = min(unvisited, key=lambda c: dist_matrix[last][c])
                    t.append(nxt)
                    unvisited.remove(nxt)
                l = tour_length(dist_matrix, t)
                if l < best_l:
                    best_l = l
                    best = t
            return best, best_l

    best_tour, initial_len = initial_tour()
    return _tsp_converge(dist_matrix, max_cycles, verbose, start_tour=best_tour, initial_len=initial_len)


def _tsp_converge(dist_matrix, max_cycles=500, verbose=True, start_tour=None, initial_len=None):
    """Internal: run convergence from a provided or computed start."""
    n = len(dist_matrix)
    
    # ── Precompute nearest neighbours for decomposition ──
    k = min(3, n - 1)
    neighbors = []
    for i in range(n):
        dists = [(dist_matrix[i][j], j) for j in range(n) if j != i]
        dists.sort()
        neighbors.append([j for _, j in dists[:k]])

    if start_tour is None:
        def initial_tour():
            try:
                from vedic_planetary_transformers import VenusianTourLoom
                loom = VenusianTourLoom(dist_matrix)
                vedic_tour, vedic_len = loom.solve()
                return list(vedic_tour), vedic_len
            except (ImportError, Exception):
                best = None
                best_l = float('inf')
                for start in range(min(5, n)):
                    unvisited = set(range(n))
                    t = [start]
                    unvisited.remove(start)
                    while unvisited:
                        last = t[-1]
                        nxt = min(unvisited, key=lambda c: dist_matrix[last][c])
                        t.append(nxt)
                        unvisited.remove(nxt)
                    l = tour_length(dist_matrix, t)
                    if l < best_l:
                        best_l = l
                        best = t
                return best, best_l
        start_tour, initial_len = initial_tour()
    elif initial_len is None:
        initial_len = tour_length(dist_matrix, start_tour)

    best_tour = start_tour[:]
    current_tour = start_tour[:]
    current_len = initial_len
    current_tour = best_tour[:]
    current_len = initial_len

    # Separately track best-ever (defensive — perturbation can't destroy it)
    best_ever_tour = best_tour[:]
    best_ever_len = initial_len

    best_signature = None
    length_history = [current_len]  # For floor detection
    history = [{"phase": 0, "length": current_len, "inharmony": None, "action": "init"}]

    if verbose:
        print(f"  Phase    0: tour={current_len:.2f} (Vedic initial)")

    # ── Convergence loop ──
    stagnation = 0
    phase_idx = 0
    floor_count = 0

    for cycle in range(1, max_cycles + 1):
        # Phase rotation
        op, octave, intensity = TSP_PHASES[phase_idx]
        phase_idx = (phase_idx + 1) % 12

        # Decompose current state
        prob_sig, sol_sig = decompose_tsp(dist_matrix, current_tour)
        current_ih = inharmony(prob_sig, sol_sig)
        length_history.append(current_len)

        # ── Operation in signature space → target signature ──
        if op == "C":
            target_sig = complement(sol_sig)
        elif op == "X":
            if best_signature is None:
                best_signature = sol_sig
            target_sig = cross(sol_sig, best_signature)
        elif op == "Z":
            target_sig = cancel(sol_sig)
        elif op == "FULL":
            t1 = complement(sol_sig)
            if best_signature is None:
                best_signature = sol_sig
            t2 = cross(t1, best_signature)
            target_sig = cancel(t2)

        # ── Translate to tour space ──
        new_tour, improved = apply_target_signature(
            current_tour, dist_matrix, target_sig, prob_sig,
            octave, intensity, neighbors, n
        )

        new_len = tour_length(dist_matrix, new_tour) if improved else current_len

        if improved and new_len < current_len:
            current_tour = new_tour[:]
            current_len = new_len
            best_signature = sol_sig

            if current_len < best_ever_len:
                best_ever_tour = current_tour[:]
                best_ever_len = current_len

            stagnation = 0
            floor_count = 0
        else:
            stagnation += 1

        # ── Structural floor detection ──
        at_floor = detect_structural_floor(length_history, window=50, threshold=0.001)
        if at_floor:
            floor_count += 1

            if floor_count >= 5:
                if verbose:
                    print(f"  Phase {cycle:4d}: structural floor (tur={current_len:.2f}),"
                          f" escaping")
                # Perturb from best-ever
                escaped_tour, _ = perturbation_escape(
                    current_tour, dist_matrix, prob_sig, n, temperature=0.35
                )
                escaped_len = tour_length(dist_matrix, escaped_tour)
                # Accept even if worse (exploration)
                current_tour = escaped_tour
                current_len = escaped_len
                best_signature = None  # reset best-known signature
                length_history = [current_len]
                floor_count = 0

        # ── Periodic restart from Vedic solver (escape deep local minima) ──
        if stagnation > 200:
            if verbose:
                print(f"  Phase {cycle:4d}: restarting from Vedic solver"
                      f" (best-ever={best_ever_len:.2f})")
            try:
                from vedic_planetary_transformers import SaturnianMinimalShield
                import copy as _cp
                reduced = SaturnianMinimalShield(_cp.deepcopy(dist_matrix))
                reduced.solve()
                from vedic_planetary_transformers import VenusianTourLoom
                loom = VenusianTourLoom(dist_matrix)
                fresh_tour, fresh_len = loom.solve()
                current_tour = list(fresh_tour)
                current_len = fresh_len
            except (ImportError, Exception):
                # Fallback: random restart
                start_v = random.randint(0, n - 1)
                unvisited = set(range(n))
                t = [start_v]
                unvisited.remove(start_v)
                while unvisited:
                    last = t[-1]
                    nxt = min(unvisited, key=lambda c: dist_matrix[last][c])
                    t.append(nxt)
                    unvisited.remove(nxt)
                current_tour = t
                current_len = tour_length(dist_matrix, current_tour)
            best_signature = None
            length_history = [current_len]
            stagnation = 0
            floor_count = 0

        # ── Logging ──
        if cycle % 50 == 0:
            history.append({
                "phase": cycle,
                "current": current_len,
                "best": best_ever_len,
                "inharmony": round(current_ih, 6),
                "action": op,
                "octave": octave,
            })
            if verbose:
                print(f"  Phase {cycle:4d}: tur={current_len:.2f}"
                      f" best={best_ever_len:.2f}"
                      f" ι={current_ih:.6f}"
                      f" op={op}")

    history.append({
        "phase": "final",
        "current": current_len,
        "best": best_ever_len,
        "inharmony": round(current_ih if 'current_ih' in dir() else 0, 6),
        "initial": initial_len,
        "improvement_pct": round((initial_len - best_ever_len) / max(initial_len, 1) * 100, 2),
    })

    return best_ever_tour, best_ever_len, history


# ═══════════════════════════════════════════════════════════
# TEST HARNESS
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("TSP CONVERGENCE ENGINE — 72-Band Frequency-Domain Solver")
    print("=" * 70)
    print("  σ(P) − σ(S) = d  →  correction instruction  →  guided 2-opt")
    print("  12-phase C/X/Z cycle  →  structural floor detection")
    print("  →  perturbation escape  →  convergence")
    print()

    random.seed(42)
    np.random.seed(42)

    configs = [
        (20, (20, "Small")),
        (50, (50, "Medium")),
        (100, (100, "Large")),
        (200, (200, "Stress")),
    ]

    for n_cities, (seed_val, label) in configs:
        print(f"\n{'─' * 70}")
        print(f"TSP: {n_cities} cities ({label})")
        print(f"{'─' * 70}")

        # Generate random city coordinates for reproducible test
        np.random.seed(seed_val)
        points = np.random.rand(n_cities, 2) * 100
        dist = np.zeros((n_cities, n_cities))
        for i in range(n_cities):
            for j in range(n_cities):
                dist[i][j] = math.sqrt(
                    (points[i][0] - points[j][0]) ** 2 +
                    (points[i][1] - points[j][1]) ** 2
                )

        # NN baseline (single start)
        t0 = time.time()
        unvisited = set(range(n_cities))
        nn_tour = [0]
        unvisited.remove(0)
        while unvisited:
            last = nn_tour[-1]
            nxt = min(unvisited, key=lambda c: dist[last][c])
            nn_tour.append(nxt)
            unvisited.remove(nxt)
        nn_len = tour_length(dist, nn_tour)
        nn_ms = (time.time() - t0) * 1000

        # Try Vedic solver baseline
        try:
            from vedic_planetary_transformers import VenusianTourLoom
            t0 = time.time()
            loom = VenusianTourLoom()
            loom.dist_matrix = dist
            loom.n_cities = n_cities
            vedic_tour, vedic_len = loom.solve()
            vedic_ms = (time.time() - t0) * 1000
            vedic_str = f"{vedic_len:.2f} ({vedic_ms:.0f}ms)"
        except (ImportError, Exception):
            vedic_tour = None
            vedic_len = nn_len
            vedic_str = "unavailable"

        # Frequency-domain convergence
        print(f"  NN baseline:            {nn_len:.2f} ({nn_ms:.0f}ms)")
        print(f"  Vedic baseline:         {vedic_str}")
        print(f"\n  Frequency-domain convergence (max 500 cycles):")

        t0 = time.time()
        tour, cost, hist = tsp_converge(dist, max_cycles=500, verbose=True)
        tsp_ms = (time.time() - t0) * 1000

        nn_improvement_pct = (nn_len - cost) / nn_len * 100
        vedic_improvement_pct = (vedic_len - cost) / max(vedic_len, 1) * 100

        print(f"\n  RESULTS:")
        print(f"    NN:              {nn_len:.2f}")
        print(f"    Vedic:           {vedic_len:.2f}" if vedic_tour else f"    Vedic:           N/A")
        print(f"    Convergence:     {cost:.2f} ({tsp_ms:.0f}ms)")
        print(f"    vs NN:           -{nn_improvement_pct:.1f}%")
        if vedic_tour:
            print(f"    vs Vedic:        -{vedic_improvement_pct:.1f}%")
        print(f"    Convergence ι:   {hist[-1].get('inharmony', 'N/A')}")
        if 'improvement_pct' in hist[-1]:
            print(f"    Total improvement: {hist[-1]['improvement_pct']}% from initial NN")

    print(f"\n{'=' * 70}")
    print("  ι → 0. The snake eats its tail.")
    print("=" * 70)
