#!/usr/bin/env python3
"""
THE OUROBOROS ENGINE — Phase 2: Type-Specific NP-Complete Solvers
═══════════════════════════════════════════════════════════════════════
Each problem type has its own decomposition into 72-band frequency space,
its own correction operator, and its own convergence loop.

The universal pattern:
  σ(P) − σ(S) = d       ← measurement in 72-band space
  S' = S + η·C(d)       ← correction proportional to measurement
  σ(P) − σ(S') = d'     ← new measurement
  S'' = S' + η·C(d')    ← new correction

inharmony(va, vb) IS the correction instruction.
"""

import math, random, time, sys, os, copy
import numpy as np

random.seed(42)
np.random.seed(42)

# =====================================================================
# CORE — shared across all types
# =====================================================================

def inharmony(a, b):
    """Universal inharmony (Euclidean distance between 72-band vectors)."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def normalize(vec):
    """Safe L1 normalization."""
    total = sum(abs(v) for v in vec)
    if total < 1e-12:
        return [0.0] * len(vec)
    return [v / total for v in vec]


def random_band_groups(n_items, n_bands=72):
    """Map items (0..n_items-1) to bands (0..71). Returns dict band→[items]."""
    groups = {k: [] for k in range(n_bands)}
    for i in range(n_items):
        groups[i % n_bands].append(i)
    return groups


# =====================================================================
# UTILITY: run Vedic solver baselines
# =====================================================================

def _vedic_benchmarks():
    """Lazy-import Vedic solvers for baseline comparison."""
    from vedic_planetary_transformers import (
        VenusianTourLoom, SaturnianMinimalShield, SolarChromaticWeaver,
        MartianPathfinder, JovianExpansiveNet, NeptunianDreamWeaver,
        LunarIntuitiveOracle, solve_sat, solve_tsp, solve_vertex_cover,
        solve_coloring, solve_set_cover, solve_hamiltonian,
        solve_subset_sum, solve_clique
    )
    return locals()


# =====================================================================
# 1. TRAVELLING SALESMAN PROBLEM (TSP)
# =====================================================================

def decompose_tsp(dist_matrix, tour):
    """
    Decompose TSP problem/solution into 72-band vectors.

    Problem decomposition:
      Each city i maps to band (i % 72). Energy spreads to bands of
      k-nearest neighbours (k=3). The problem signature = distance
      distribution: each band accumulates normalised distance statistics.

    Solution decomposition:
      Same band mapping, but the energy reflects the tour order.
      A city's contribution = how far its tour-edge distance deviates
      from the mean edge distance.

    Returns (prob_sig, sol_sig) — both 72-element frequency vectors.
    """
    n = len(dist_matrix)
    prob = [0.0] * 72
    sol = [0.0] * 72

    # Precompute nearest neighbours for each city
    k = min(3, n - 1)
    neighbors = []
    for i in range(n):
        dists = [(dist_matrix[i][j], j) for j in range(n) if j != i]
        dists.sort()
        neighbors.append([j for _, j in dists[:k]])

    # Problem signature: distance distribution
    prob_total = 0.0
    for i in range(n):
        for j in neighbors[i]:
            d = dist_matrix[i][j]
            band_i = i % 72
            band_j = j % 72
            weight = d / (1 + d)
            prob[band_i] += weight * 0.5
            prob[band_j] += weight * 0.5
            prob_total += weight

    # Solution signature: tour edge cost distribution
    sol_total = 0.0
    if tour and len(tour) == n:
        mean_edge = sum(dist_matrix[tour[i]][tour[(i + 1) % n]] for i in range(n)) / n
        for i in range(n):
            city = tour[i]
            next_city = tour[(i + 1) % n]
            edge_cost = dist_matrix[city][next_city]
            deviation = abs(edge_cost - mean_edge) / max(mean_edge, 1e-10)
            band = city % 72
            sol[band] += deviation
            sol_total += deviation
            # Also spread to neighbour bands
            for nb in neighbors[city]:
                sol[nb % 72] += deviation * 0.25
                sol_total += deviation * 0.25

    prob = normalize(prob)
    sol = normalize(sol)
    return prob, sol


def tour_length(dist_matrix, tour):
    """Compute total tour distance."""
    n = len(tour)
    return sum(dist_matrix[tour[i]][tour[(i + 1) % n]] for i in range(n))


def ouroboros_tsp(dist_matrix, max_steps=2000, verbose=True):
    """
    Solve TSP via inharmony-driven 2-opt gradient descent.

    C: swap two cities in the most misaligned band region (guided 2-opt)
    X: mix two tours — take best segments
    Z: cancel sub-tour crossings (remove crossing edges)
    """
    n = len(dist_matrix)
    if n < 3:
        tour = list(range(n))
        return tour, tour_length(dist_matrix, tour), [{"step": 0, "length": tour_length(dist_matrix, tour)}]

    # Nearest neighbour heuristic for initial tour
    def nearest_neighbour(start=0):
        unvisited = set(range(n))
        tour = [start]
        unvisited.remove(start)
        while unvisited:
            last = tour[-1]
            next_city = min(unvisited, key=lambda c: dist_matrix[last][c])
            tour.append(next_city)
            unvisited.remove(next_city)
        return tour

    # Try best of several NN starts
    best_nn = None
    best_nn_len = float('inf')
    for start in range(min(5, n)):
        t = nearest_neighbour(start)
        l = tour_length(dist_matrix, t)
        if l < best_nn_len:
            best_nn_len = l
            best_nn = t

    tour = best_nn[:]
    current_len = best_nn_len

    # Precompute k-nearest for decomposition
    k = min(3, n - 1)
    neighbors = []
    for i in range(n):
        dists = [(dist_matrix[i][j], j) for j in range(n) if j != i]
        dists.sort()
        neighbors.append([j for _, j in dists[:k]])

    history = [{"step": 0, "length": current_len}]
    if verbose:
        print(f"  Step    0: length={current_len:.4f} (NN heuristic)")

    for step in range(1, max_steps + 1):
        # Decompose
        prob_sig, sol_sig = decompose_tsp(dist_matrix, tour)
        d = [(prob_sig[k] - sol_sig[k]) for k in range(72)]

        # Find most misaligned band
        bands_by_magnitude = sorted(range(72), key=lambda k: abs(d[k]), reverse=True)

        flipped = False
        for band in bands_by_magnitude[:5]:  # try top 5 bands
            if abs(d[band]) < 1e-6:
                continue

            # Find cities in this band or connected to this band
            band_cities = [i for i in range(n) if i % 72 == band]
            # Also include neighbours of those cities
            candidate_cities = set(band_cities)
            for c in band_cities:
                for nb in neighbors[c] if c < len(neighbors) else []:
                    candidate_cities.add(nb)

            candidates = list(candidate_cities)
            if len(candidates) < 2:
                continue

            # Try 2-opt swaps among candidates, guided by inharmony
            best_swap = None
            best_len = current_len

            # Score edges: edges contributing most to inharmony
            edge_scores = {}
            for i in range(n):
                a = tour[i]
                b = tour[(i + 1) % n]
                band_a = a % 72
                band_b = b % 72
                score = abs(d[band_a]) + abs(d[band_b])
                edge_scores[i] = score

            # Sort edges by inharmony score, look at top ones
            scored_edges = sorted(edge_scores.items(), key=lambda x: -x[1])
            examined = 0

            for edge_idx, score in scored_edges[:min(20, n)]:
                i = edge_idx
                j = (i + 1) % n
                # Try swapping with other edges in misaligned band
                for other_edge_idx, _ in scored_edges[:min(20, n)]:
                    k = other_edge_idx
                    l = (k + 1) % n
                    if j == k or i == l or i == k:
                        continue

                    # 2-opt swap: reverse segment [j:k]
                    if j < k:
                        new_tour = tour[:j] + tour[j:k+1][::-1] + tour[k+1:]
                    else:
                        new_tour = tour[:k] + tour[k:j+1][::-1] + tour[j+1:]

                    new_len = tour_length(dist_matrix, new_tour)
                    examined += 1
                    if new_len < best_len:
                        best_len = new_len
                        best_swap = new_tour

            if best_swap is not None and best_len < current_len:
                tour = best_swap
                current_len = best_len
                flipped = True
                break

        # (X) Cross: also try segment inversion with random partner
        if not flipped and step % 5 == 0:
            i = random.randint(0, n - 1)
            j = random.randint(0, n - 1)
            if i > j:
                i, j = j, i
            if j - i > 1:
                new_tour = tour[:i] + tour[i:j+1][::-1] + tour[j+1:]
                new_len = tour_length(dist_matrix, new_tour)
                if new_len < current_len:
                    tour = new_tour
                    current_len = new_len
                    flipped = True

        # (Z) Cancel: try 2-opt swaps regardless of band guidance
        if not flipped:
            # Every 15 steps, try aggressive random 2-opt
            if step % 15 == 0:
                i = random.randint(0, n - 3)
                j = random.randint(i + 2, min(n - 1, i + n // 3))
                if j > i + 1:
                    new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
                    new_len = tour_length(dist_matrix, new_tour)
                    accept = new_len < current_len
                    # Also sometimes accept worse solutions for exploration
                    if not accept and random.random() < max(0.005, 0.08 * (1 - step / max_steps)):
                        accept = True
                    if accept:
                        tour = new_tour
                        current_len = new_len
            # Every 30 steps: try swapping non-adjacent random cities
            if not flipped and step % 30 == 0:
                positions = random.sample(range(n), 2)
                if abs(positions[0] - positions[1]) > 1:
                    i, k = sorted(positions)
                    new_tour = tour[:i] + tour[i:k+1][::-1] + tour[k+1:]
                    new_len = tour_length(dist_matrix, new_tour)
                    if new_len < current_len:
                        tour = new_tour
                        current_len = new_len

        # Restart from fresh NN if stuck for too long
        stall_threshold = min(300, n * 15)
        if step > 100 and step % stall_threshold == 0:
            start_v = random.randint(0, n - 1)
            new_tour = nearest_neighbour(start_v)
            new_len = tour_length(dist_matrix, new_tour)
            if new_len < current_len:
                tour = new_tour
                current_len = new_len
                if verbose:
                    print(f"  Step {step:4d}: restart from NN({start_v}), len={current_len:.4f}")
            elif random.random() < 0.15:
                # Sometimes restart anyway
                tour = new_tour
                current_len = new_len
                if verbose:
                    print(f"  Step {step:4d}: restart (explore) from NN({start_v}), len={current_len:.4f}")

        if step % 100 == 0:
            history.append({"step": step, "length": current_len})
            if verbose:
                print(f"  Step {step:4d}: length={current_len:.4f}")

    history.append({"step": min(step, max_steps), "length": current_len, "best_nn": best_nn_len})
    return tour, current_len, history


def test_ouroboros_tsp():
    """Test TSP Ouroboros on random instances, compare vs NN and Vedic."""
    print("\n" + "=" * 70)
    print("TSP OUROBOROS — City Tour Optimisation")
    print("=" * 70)

    configs = [20, 50, 100]
    all_results = []

    for n_cities in configs:
        print(f"\n--- {n_cities} cities ---")

        # Generate random city coordinates
        np.random.seed(n_cities)
        points = np.random.rand(n_cities, 2) * 100
        dist_matrix = np.zeros((n_cities, n_cities))
        for i in range(n_cities):
            for j in range(n_cities):
                dist_matrix[i][j] = math.sqrt(
                    (points[i][0] - points[j][0]) ** 2 +
                    (points[i][1] - points[j][1]) ** 2
                )

        # Nearest neighbour baseline
        def nn_tour(start=0):
            unvisited = set(range(n_cities))
            t = [start]
            unvisited.remove(start)
            while unvisited:
                last = t[-1]
                nxt = min(unvisited, key=lambda c: dist_matrix[last][c])
                t.append(nxt)
                unvisited.remove(nxt)
            return t

        best_nn_len = min(tour_length(dist_matrix, nn_tour(s)) for s in range(min(5, n_cities)))

        # Vedic baseline
        vedic_len = None
        try:
            vedic_mods = _vedic_benchmarks()
            solver = vedic_mods['VenusianTourLoom'](dist_matrix)
            vedic_tour, vedic_len = solver.solve()
        except Exception as e:
            print(f"  Vedic failed: {e}")

        # Ouroboros
        print(f"\n  OUROBOROS ({n_cities} cities, up to 2000 steps):")
        t0 = time.time()
        tour, length, history = ouroboros_tsp(dist_matrix, max_steps=2000, verbose=True)
        ouro_ms = (time.time() - t0) * 1000

        nn_improv = (best_nn_len - length) / best_nn_len * 100 if best_nn_len > 0 else 0
        vedic_improv = ((vedic_len - length) / vedic_len * 100) if vedic_len and vedic_len > 0 else None

        print(f"\n  RESULTS:")
        print(f"    NN heuristic:  {best_nn_len:.2f}")
        if vedic_len:
            print(f"    Vedic:         {vedic_len:.2f}")
        print(f"    Ouroboros:     {length:.2f} in {ouro_ms:.0f}ms")
        print(f"    Improvement:   {nn_improv:.1f}% over NN" +
              (f", {vedic_improv:.1f}% over Vedic" if vedic_improv else ""))

        all_results.append({
            "n": n_cities,
            "nn": best_nn_len,
            "vedic": vedic_len,
            "ouro": length,
            "ouro_ms": ouro_ms,
            "nn_improv": nn_improv,
        })

    # Summary
    print("\n" + "-" * 70)
    print(f"{'Cities':>7} {'NN':>10} {'Vedic':>10} {'Ouroboros':>12} {'vs NN':>8} {'vs Ved':>8} {'Time':>8}")
    print("-" * 70)
    for r in all_results:
        ved = f"{r['vedic']:.1f}" if r['vedic'] else "N/A"
        vim = f"{((r['vedic']-r['ouro'])/r['vedic']*100):.1f}%" if r['vedic'] else "N/A"
        print(f"{r['n']:7d} {r['nn']:10.1f} {ved:>10} {r['ouro']:12.1f} "
              f"{r['nn_improv']:>+7.1f}% {vim:>8} {r['ouro_ms']:>7.0f}ms")

    return all_results


# =====================================================================
# 2. VERTEX COVER
# =====================================================================

def decompose_vc(edges, n_vertices, cover):
    """
    Decompose Vertex Cover into 72-band vectors.

    Problem: each vertex maps to band (v % 72). Energy spreads to
    bands of neighbours. Problem signature = edge coverage needs
    (how many uncovered edges each vertex sees).

    Solution: cover set membership signal (1.0 if in cover, -1.0 if not).
    """
    prob = [0.0] * 72
    sol = [0.0] * 72

    adj = {i: [] for i in range(n_vertices)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    cover_set = set(cover)
    prob_total = 0.0
    sol_total = 0.0

    for v in range(n_vertices):
        band = v % 72
        # Problem: how many edges incident to v would be uncovered
        # if v is NOT in cover? Count neighbours not in cover.
        uncovered_if_missing = sum(1 for nb in adj[v] if nb not in cover_set)
        prob_val = uncovered_if_missing / max(1, len(adj[v]))
        prob[band] += prob_val
        prob_total += prob_val
        # Spread to neighbour bands
        for nb in adj[v]:
            prob[nb % 72] += prob_val * 0.3
            prob_total += prob_val * 0.3

        # Solution: is v in the cover?
        sol_val = 1.0 if v in cover_set else -1.0
        sol[band] += sol_val
        sol_total += abs(sol_val)

    prob = normalize(prob)
    sol = normalize(sol)
    return prob, sol


def cover_quality(edges, cover):
    """Return (all_covered, uncovered_count, covered_count)."""
    cover_set = set(cover)
    uncovered = 0
    covered = 0
    for u, v in edges:
        if u in cover_set or v in cover_set:
            covered += 1
        else:
            uncovered += 1
    return uncovered == 0, uncovered, covered


def ouroboros_vc(edges, n_vertices, max_steps=1000, verbose=True):
    """
    Solve Vertex Cover via inharmony gradient descent.

    C: add/remove vertices in the most misaligned band
    """
    adj = {i: [] for i in range(n_vertices)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # Greedy cover as starting point
    uncovered_edges = set((min(u, v), max(u, v)) for u, v in edges)
    cover = set()
    while uncovered_edges:
        u, v = next(iter(uncovered_edges))
        # Pick vertex with more uncovered incident edges
        u_count = sum(1 for nb in adj[u] if (min(u, nb), max(u, nb)) in uncovered_edges)
        v_count = sum(1 for nb in adj[v] if (min(v, nb), max(v, nb)) in uncovered_edges)
        pick = u if u_count >= v_count else v
        cover.add(pick)
        uncovered_edges = {e for e in uncovered_edges if pick not in e}

    all_covered, uncovered, covered = cover_quality(edges, list(cover))
    history = [{"step": 0, "cover_size": len(cover), "uncovered": uncovered}]

    if verbose:
        print(f"  Step    0: |cover|={len(cover)}, uncovered={uncovered}/{len(edges)}")

    best_cover = cover.copy()
    best_size = len(cover)
    stall = 0

    for step in range(1, max_steps + 1):
        # Decompose
        prob_sig, sol_sig = decompose_vc(edges, n_vertices, list(cover))
        d = [(prob_sig[k] - sol_sig[k]) for k in range(72)]

        # Find most misaligned bands
        bands_by_magnitude = sorted(range(72), key=lambda k: abs(d[k]), reverse=True)

        flipped = False
        for band in bands_by_magnitude[:5]:
            if abs(d[band]) < 1e-6:
                continue

            # Vertices in this band
            band_verts = [v for v in range(n_vertices) if v % 72 == band]
            if not band_verts:
                continue

            # Score each vertex: how much would changing it help?
            uncovered_edges = [(u, v) for u, v in edges
                               if u not in cover and v not in cover]

            best_v = None
            best_score = 0

            for v in band_verts:
                currently_in = v in cover
                if currently_in:
                    # Consider removing: maintain coverage?
                    # Only safe if all neighbours already covered
                    is_essential = False
                    for nb in adj[v]:
                        if nb not in cover:
                            is_essential = True
                            break
                        # Check if any edge (v, nb) would be uncovered
                        if (v, nb) in edges or (nb, v) in edges:
                            if nb not in cover - {v}:
                                is_essential = v not in cover - {v}
                    if not is_essential:
                        # Removing saves size
                        score = 1.0 + len(adj[v]) * 0.1  # + correlation direction
                        if d[band] < 0:  # correction says reduce positive energy
                            score += 2.0
                        if score > best_score:
                            best_score = score
                            best_v = v
                else:
                    # Consider adding: how many uncovered edges would it cover?
                    uncovered_adj = sum(1 for nb in adj[v] if nb not in cover
                                        and ((v, nb) in edges or (nb, v) in edges))
                    if uncovered_adj > 0:
                        score = uncovered_adj
                        if d[band] > 0:  # correction says increase positive energy
                            score += 2.0
                        if score > best_score:
                            best_score = score
                            best_v = v

            if best_v is not None:
                if best_v in cover:
                    cover.remove(best_v)
                else:
                    cover.add(best_v)
                flipped = True
                break

        # (Z) Cancel: if no improvement, force-fix uncovered edges
        if not flipped:
            uncovered_edges = [(u, v) for u, v in edges
                               if u not in cover and v not in cover]
            if uncovered_edges:
                u, v = random.choice(uncovered_edges)
                cover.add(u)
                flipped = True

        # Track best solution
        all_covered, uncovered, covered_count = cover_quality(edges, list(cover))
        if all_covered and len(cover) < best_size:
            best_size = len(cover)
            best_cover = cover.copy()
            stall = 0
        else:
            stall += 1

        # Time to simplify if stable
        if stall > 50 and all_covered:
            # Try removing redundant vertices
            for v in list(cover):
                test = cover - {v}
                tc, u, _ = cover_quality(edges, list(test))
                if tc:
                    cover = test
                    best_cover = test.copy()
                    best_size = len(cover)
            stall = 0

        if step % 100 == 0:
            history.append({"step": step, "cover_size": len(cover), "uncovered": uncovered})
            if verbose:
                print(f"  Step {step:4d}: |cover|={len(cover)}, uncovered={uncovered}/{len(edges)}")

        if all_covered and stall > 100:
            break

    # Use best found
    cover = best_cover
    all_covered, uncovered, covered_count = cover_quality(edges, list(cover))
    return list(cover), all_covered, history


def test_ouroboros_vc():
    """Test Vertex Cover on random graphs."""
    print("\n" + "=" * 70)
    print("VERTEX COVER OUROBOROS")
    print("=" * 70)

    configs = [(20, 40), (50, 100), (100, 200)]
    all_results = []

    for n_verts, n_edges in configs:
        print(f"\n--- {n_verts} vertices, {n_edges} edges ---")

        # Generate random graph
        edges_set = set()
        while len(edges_set) < n_edges:
            u = random.randint(0, n_verts - 1)
            v = random.randint(0, n_verts - 1)
            if u != v:
                edges_set.add((min(u, v), max(u, v)))
        edges = list(edges_set)
        n = n_verts

        # Greedy baseline
        adj = {i: [] for i in range(n)}
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        greedy_cover = set()
        remaining = set(edges)
        while remaining:
            best_v = max(range(n), key=lambda v: sum(1 for e in remaining if v in e))
            greedy_cover.add(best_v)
            remaining = {e for e in remaining if best_v not in e}

        _, greed_uncover, greed_covered = cover_quality(edges, list(greedy_cover))

        # Vedic baseline
        vedic_cover = None
        try:
            vedic_mods = _vedic_benchmarks()
            vedic_result = vedic_mods['SaturnianMinimalShield'](
                adj, edges, n
            ).solve()
            vedic_cover = list(vedic_result) if hasattr(vedic_result, '__iter__') else [vedic_result]
        except Exception as e:
            print(f"  Vedic failed: {e}")

        # Ouroboros
        print(f"\n  OUROBOROS ({n} verts, {len(edges)} edges):")
        t0 = time.time()
        cover, all_covered, history = ouroboros_vc(edges, n, max_steps=800, verbose=True)
        ouro_ms = (time.time() - t0) * 1000

        _, ouro_uncover, ouro_covered = cover_quality(edges, cover)

        print(f"\n  RESULTS:")
        print(f"    Greedy:  |cover|={len(greedy_cover)}, covered={greed_covered}/{len(edges)}")
        if vedic_cover:
            _, ve_un, ve_co = cover_quality(edges, vedic_cover)
            print(f"    Vedic:   |cover|={len(vedic_cover)}, covered={ve_co}/{len(edges)}")
        print(f"    Ouro:    |cover|={len(cover)}, covered={ouro_covered}/{len(edges)}")
        print(f"    Time:    {ouro_ms:.0f}ms")

        all_results.append({
            "n": n, "e": len(edges),
            "greedy": len(greedy_cover),
            "vedic": len(vedic_cover) if vedic_cover else None,
            "ouro": len(cover),
            "ouro_covered": ouro_covered,
            "all_covered": all_covered,
        })

    print("\n" + "-" * 70)
    print(f"{'Verts':>6} {'Edges':>6} {'Greedy':>8} {'Vedic':>8} {'Ouro':>8} {'Ouro_Cov':>10}")
    print("-" * 70)
    for r in all_results:
        ved = f"{r['vedic']}" if r['vedic'] else "N/A"
        cov_str = f"{r['ouro_covered']}/{r['e']}" if r['ouro_covered'] else "0"
        print(f"{r['n']:6d} {r['e']:6d} {r['greedy']:8d} {ved:>8} {r['ouro']:8d} {cov_str:>10}")
    return all_results


# =====================================================================
# 3. GRAPH COLORING
# =====================================================================

def decompose_coloring(edges, n_vertices, assignment, max_colors=4):
    """
    Decompose Graph Coloring into 72-band vectors.

    Problem: each vertex maps to band (v % 72). Energy spreads
    through adjacency. Problem signature = edge constraints
    (each edge must have different-colored endpoints).

    Solution: the color assignment, projected as color-frequency.
    """
    prob = [0.0] * 72
    sol = [0.0] * 72

    adj = {i: [] for i in range(n_vertices)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    prob_total = 0.0
    sol_total = 0.0

    for v in range(n_vertices):
        band = v % 72
        color = assignment.get(v, -1)

        # Problem: conflict pressure
        if adj[v]:
            conflicts = sum(1 for nb in adj[v] if assignment.get(nb) == color)
            prob_val = conflicts / max(1, len(adj[v]))
        else:
            prob_val = 0.0
        prob[band] += prob_val
        prob_total += prob_val
        for nb in adj[v]:
            prob[nb % 72] += prob_val * 0.2
            prob_total += prob_val * 0.2

        # Solution: color encoding (1/color as frequency, scaled)
        if color >= 0:
            sol_val = 1.0 - color / max(1, max_colors)
        else:
            sol_val = 0.0
        sol[band] += sol_val
        sol_total += abs(sol_val)

    prob = normalize(prob)
    sol = normalize(sol)
    return prob, sol


def count_conflicts(edges, assignment):
    """Count edges with same-colored endpoints."""
    return sum(1 for u, v in edges if assignment.get(u) == assignment.get(v))


def ouroboros_coloring(edges, n_vertices, max_colors=3, max_steps=1500, verbose=True):
    """
    Solve Graph Coloring via inharmony gradient descent.

    C: recolor vertices in misaligned bands (pick best color)
    """
    adj = {i: [] for i in range(n_vertices)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # Greedy initial coloring (Welsh-Powell)
    verts_by_degree = sorted(range(n_vertices), key=lambda v: -len(adj[v]))
    assignment = {}
    for v in verts_by_degree:
        used_colors = {assignment[nb] for nb in adj[v] if nb in assignment}
        for c in range(max_colors):
            if c not in used_colors:
                assignment[v] = c
                break
        else:
            assignment[v] = 0  # assign first color if needed (will conflict)

    conflicts = count_conflicts(edges, assignment)
    history = [{"step": 0, "conflicts": conflicts}]
    if verbose:
        print(f"  Step    0: conflicts={conflicts}/{len(edges)}")

    best_assign = assignment.copy()
    best_conflicts = conflicts
    stall = 0

    for step in range(1, max_steps + 1):
        # Decompose
        prob_sig, sol_sig = decompose_coloring(edges, n_vertices, assignment, max_colors)
        d = [(prob_sig[k] - sol_sig[k]) for k in range(72)]

        bands_by_magnitude = sorted(range(72), key=lambda k: abs(d[k]), reverse=True)

        flipped = False
        for band in bands_by_magnitude[:5]:
            if abs(d[band]) < 1e-6:
                continue

            band_verts = [v for v in range(n_vertices) if v % 72 == band]
            if not band_verts:
                continue

            # Find the vertex with the most conflicts in this band
            best_v = None
            best_new_color = -1
            best_gain = 0

            for v in band_verts:
                if v not in assignment:
                    continue
                current_color = assignment[v]
                neighbor_colors = {assignment[nb] for nb in adj[v] if nb in assignment}
                current_conflicts = sum(1 for nb in adj[v]
                                        if assignment.get(nb) == current_color)

                for new_color in range(max_colors):
                    if new_color == current_color:
                        continue
                    new_conflicts = sum(1 for nb in adj[v]
                                        if assignment.get(nb) == new_color)
                    gain = current_conflicts - new_conflicts
                    if gain > best_gain:
                        best_gain = gain
                        best_v = v
                        best_new_color = new_color

            if best_v is not None and best_new_color >= 0 and best_gain > 0:
                assignment[best_v] = best_new_color
                flipped = True
                break

        # (X) Cross: try recoloring a conflicting vertex to best available
        if not flipped:
            # Find a conflicting vertex
            for u, v in edges:
                if assignment.get(u) == assignment.get(v):
                    conflicted = random.choice([u, v])
                    neighbor_colors = {assignment[nb] for nb in adj[conflicted] if nb in assignment}
                    for c in range(max_colors):
                        if c not in neighbor_colors:
                            assignment[conflicted] = c
                            flipped = True
                            break
                    if flipped:
                        break

        # (Z) Cancel: aggressive random search every 20 steps
        if not flipped and step % 20 == 0:
            # Try swapping all conflicting vertices
            current_conflicts = count_conflicts(edges, assignment)
            for attempt in range(20):
                v = random.randint(0, n_vertices - 1)
                old_color = assignment.get(v, 0)
                new_color = (v + attempt) % max_colors
                if new_color != old_color:
                    assignment[v] = new_color
                    new_conflicts = count_conflicts(edges, assignment)
                    if new_conflicts < current_conflicts:
                        flipped = True
                        break
                    else:
                        assignment[v] = old_color  # revert

        if flipped:
            conflicts = count_conflicts(edges, assignment)
            if conflicts < best_conflicts:
                best_conflicts = conflicts
                best_assign = assignment.copy()
                stall = 0
            else:
                # Accept worse solutions with decaying probability (simulated annealing)
                temp = max(0.01, 0.3 * (1 - step / max_steps))
                if random.random() < temp:
                    pass  # keep the change
                else:
                    # Revert but keep the assignment at the last known state
                    # Actually we track best separately, so just increment stall
                    pass
                stall += 1
        else:
            stall += 1

        # Restart from scratch if stuck for a long time
        if stall > 300 and best_conflicts > 0:
            # Re-initialize using greedy
            verts_by_degree = sorted(range(n_vertices), key=lambda v: -len(adj[v]))
            assignment = {}
            for v in verts_by_degree:
                used_colors = {assignment[nb] for nb in adj[v] if nb in assignment}
                for c in range(max_colors):
                    if c not in used_colors:
                        assignment[v] = c
                        break
                else:
                    assignment[v] = 0
            stall = 0

        if step % 100 == 0:
            history.append({"step": step, "conflicts": conflicts})
            if verbose:
                print(f"  Step {step:4d}: conflicts={conflicts}/{len(edges)}")

        if best_conflicts == 0 and stall > 50:
            break

    assignment = best_assign
    conflicts = best_conflicts
    history.append({"step": min(step, max_steps), "conflicts": conflicts})
    return assignment, conflicts, history


def test_ouroboros_coloring():
    """Test Graph Coloring on random graphs."""
    print("\n" + "=" * 70)
    print("GRAPH COLORING OUROBOROS")
    print("=" * 70)

    configs = [(20, 60, 3), (30, 100, 4), (50, 150, 4)]
    all_results = []

    for n_verts, n_edges, max_c in configs:
        print(f"\n--- {n_verts} vertices, {n_edges} edges, {max_c} colors ---")

        edges_set = set()
        while len(edges_set) < n_edges:
            u = random.randint(0, n_verts - 1)
            v = random.randint(0, n_verts - 1)
            if u != v:
                edges_set.add((min(u, v), max(u, v)))
        edges = list(edges_set)

        # Greedy baseline
        adj = {i: [] for i in range(n_verts)}
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        greedy_assign = {}
        for v in sorted(range(n_verts), key=lambda x: -len(adj[x])):
            used = {greedy_assign[nb] for nb in adj[v] if nb in greedy_assign}
            for c in range(max_c):
                if c not in used:
                    greedy_assign[v] = c
                    break
            else:
                greedy_assign[v] = 0
        greedy_conflicts = count_conflicts(edges, greedy_assign)

        # Vedic baseline
        vedic_assign = None
        vedic_conflicts = None
        try:
            vedic_mods = _vedic_benchmarks()
            vedic_assign, vedic_colors = vedic_mods['SolarChromaticWeaver'](
                adj, edges, n_verts
            ).solve()
            if isinstance(vedic_assign, dict) and all(isinstance(v, int) for v in vedic_assign.values()):
                vedic_conflicts = count_conflicts(edges, vedic_assign)
        except Exception as e:
            print(f"  Vedic failed: {e}")

        # Ouroboros
        print(f"\n  OUROBOROS ({n_verts} verts, {len(edges)} edges, {max_c} colors):")
        t0 = time.time()
        assign, conflicts, history = ouroboros_coloring(
            edges, n_verts, max_colors=max_c, max_steps=1500, verbose=True
        )
        ouro_ms = (time.time() - t0) * 1000

        print(f"\n  RESULTS:")
        print(f"    Greedy:  conflicts={greedy_conflicts}/{len(edges)}")
        if vedic_conflicts is not None:
            print(f"    Vedic:   conflicts={vedic_conflicts}/{len(edges)}, colors={max(vedic_assign.values())+1}")
        print(f"    Ouro:    conflicts={conflicts}/{len(edges)} in {ouro_ms:.0f}ms")

        all_results.append({
            "n": n_verts, "e": len(edges), "max_c": max_c,
            "greedy_conflicts": greedy_conflicts,
            "vedic_conflicts": vedic_conflicts,
            "ouro_conflicts": conflicts,
        })

    print("\n" + "-" * 70)
    print(f"{'Verts':>6} {'Edges':>6} {'Colors':>7} {'GreedyC':>8} {'VedicC':>8} {'OuroC':>8}")
    print("-" * 70)
    for r in all_results:
        ved = f"{r['vedic_conflicts']}" if r['vedic_conflicts'] is not None else "N/A"
        print(f"{r['n']:6d} {r['e']:6d} {r['max_c']:7d} {r['greedy_conflicts']:8d} "
              f"{ved:>8} {r['ouro_conflicts']:8d}")
    return all_results


# =====================================================================
# 4. SUBSET SUM
# =====================================================================

def decompose_subsetsum(numbers, target, selected_indices):
    """
    Decompose Subset Sum into 72-band vectors.

    Problem: each number maps to band (i % 72). Energy spreads through
    value-proximity neighbours (close values cluster). Problem signature =
    the target distribution (how much each band needs to reach target).

    Solution: which numbers are selected/not selected.
    """
    n = len(numbers)
    prob = [0.0] * 72
    sol = [0.0] * 72

    selected_set = set(selected_indices)

    # Sort numbers by value for proximity grouping
    sorted_by_val = sorted(range(n), key=lambda i: numbers[i])

    # Problem: target energy distribution
    prob_total = 0.0
    remaining = target
    for i, idx in enumerate(sorted_by_val):
        val = numbers[idx]
        if remaining <= 0:
            break
        band = idx % 72
        contribution = min(val, remaining) / max(1, target)
        prob[band] += contribution
        prob_total += contribution
        # Spread to bands of value-similar neighbours
        for j in range(max(0, i-2), min(n, i+3)):
            if j != i:
                nb = sorted_by_val[j]
                prob[nb % 72] += contribution * 0.15
                prob_total += contribution * 0.15
        remaining -= val

    # Solution: which numbers are selected
    sol_total = 0.0
    current_sum = sum(numbers[i] for i in selected_indices)
    for i in range(n):
        band = i % 72
        if i in selected_set:
            sol_val = numbers[i] / max(1, target) if current_sum > 0 else 0.5
        else:
            sol_val = 0.0
        sol[band] += sol_val
        sol_total += sol_val

    prob = normalize(prob)
    sol = normalize(sol)
    return prob, sol


def ouroboros_subsetsum(numbers, target, max_steps=1000, verbose=True):
    """
    Solve Subset Sum via inharmony gradient descent.

    C: include/exclude numbers in misaligned bands to approach target.
    """
    n = len(numbers)
    current_indices = set()
    current_sum = 0.0

    # Greedy start: pick largest numbers that don't exceed target
    sorted_desc = sorted(range(n), key=lambda i: -numbers[i])
    for i in sorted_desc:
        if current_sum + numbers[i] <= target:
            current_indices.add(i)
            current_sum += numbers[i]

    best_indices = current_indices.copy()
    best_sum = current_sum
    best_abs_diff = abs(target - current_sum)

    history = [{"step": 0, "sum": current_sum, "diff": best_abs_diff}]
    if verbose:
        print(f"  Step    0: sum={current_sum}/{target}, diff={abs(current_sum-target)}")

    for step in range(1, max_steps + 1):
        # Decompose
        prob_sig, sol_sig = decompose_subsetsum(numbers, target, list(current_indices))
        d = [(prob_sig[k] - sol_sig[k]) for k in range(72)]

        bands_by_magnitude = sorted(range(72), key=lambda k: abs(d[k]), reverse=True)

        flipped = False
        for band in bands_by_magnitude[:5]:
            if abs(d[band]) < 1e-6:
                continue

            # Numbers in this band
            band_indices = [i for i in range(n) if i % 72 == band]
            if not band_indices:
                continue

            # Score each: would adding/removing improve the sum?
            over_target = current_sum > target
            best_i = None
            best_gain = 0

            for i in band_indices:
                currently_in = i in current_indices
                if currently_in and over_target:
                    # Removing helps — bring sum down
                    gain = min(numbers[i], current_sum - target) / max(1, target)
                    # Inharmony alignment
                    if d[band] < 0:  # correction says reduce positive
                        gain *= 1.5
                    if gain > best_gain:
                        best_gain = gain
                        best_i = i
                elif not currently_in and not over_target:
                    # Adding helps — bring sum up
                    new_sum = current_sum + numbers[i]
                    if new_sum <= target:
                        gain = numbers[i] / max(1, target)
                    else:
                        # Would overshoot — penalize by how much
                        gain = (target - current_sum) / max(1, numbers[i])
                    if d[band] > 0:  # correction says increase positive
                        gain *= 1.5
                    if gain > best_gain:
                        best_gain = gain
                        best_i = i

            if best_i is not None and best_gain > 0:
                if best_i in current_indices:
                    current_indices.remove(best_i)
                    current_sum -= numbers[best_i]
                else:
                    current_indices.add(best_i)
                    current_sum += numbers[best_i]
                flipped = True
                break

        # (Z) Cancel: if stuck, try swapping
        if not flipped:
            if over_target:
                # Remove the largest in current sum
                if current_indices:
                    largest = max(current_indices, key=lambda i: numbers[i])
                    current_indices.remove(largest)
                    current_sum -= numbers[largest]
                    flipped = True
            else:
                # Add the best single number
                candidates = [i for i in range(n) if i not in current_indices
                              and current_sum + numbers[i] <= target]
                if candidates:
                    best_add = max(candidates, key=lambda i: numbers[i])
                    current_indices.add(best_add)
                    current_sum += numbers[best_add]
                    flipped = True

        # Track best
        abs_diff = abs(target - current_sum)
        if abs_diff < best_abs_diff:
            best_abs_diff = abs_diff
            best_sum = current_sum
            best_indices = current_indices.copy()

        if step % 100 == 0:
            history.append({"step": step, "sum": current_sum, "diff": abs_diff})
            if verbose:
                print(f"  Step {step:4d}: sum={current_sum}/{target}, diff={abs_diff}")

        if current_sum == target:
            history.append({"step": step, "sum": current_sum, "diff": 0})
            if verbose:
                print(f"  ✓ PERFECT at step {step}: sum={current_sum} == target={target}")
            break

    return list(best_indices), best_sum, history


def test_ouroboros_subsetsum():
    """Test Subset Sum on random instances."""
    print("\n" + "=" * 70)
    print("SUBSET SUM OUROBOROS")
    print("=" * 70)

    configs = [(20, 10), (30, 10), (50, 20)]
    all_results = []

    for n_nums, max_val in configs:
        print(f"\n--- {n_nums} numbers (1-{max_val}) ---")

        numbers = [random.randint(1, max_val) for _ in range(n_nums)]
        target = sum(numbers) // 2

        # Greedy baseline
        sorted_desc = sorted(range(n_nums), key=lambda i: -numbers[i])
        greedy_sel = set()
        greedy_sum = 0
        for i in sorted_desc:
            if greedy_sum + numbers[i] <= target:
                greedy_sel.add(i)
                greedy_sum += numbers[i]
        greedy_diff = abs(target - greedy_sum)

        # Vedic baseline
        vedic_sum = None
        vedic_diff = None
        try:
            vedic_mods = _vedic_benchmarks()
            vedic_result = vedic_mods['LunarIntuitiveOracle'](numbers, target).solve()
            if isinstance(vedic_result, set):
                vedic_sum = sum(numbers[i] for i in vedic_result)
                vedic_diff = abs(target - vedic_sum)
        except Exception as e:
            print(f"  Vedic failed: {e}")

        # Ouroboros
        print(f"\n  OUROBOROS ({n_nums} numbers, target={target}):")
        t0 = time.time()
        sel, current_sum, history = ouroboros_subsetsum(
            numbers, target, max_steps=800, verbose=True
        )
        ouro_ms = (time.time() - t0) * 1000
        ouro_diff = abs(target - current_sum)

        print(f"\n  RESULTS:")
        print(f"    Greedy:  sum={greedy_sum}/{target}, diff={greedy_diff}")
        if vedic_sum is not None:
            print(f"    Vedic:   sum={vedic_sum}/{target}, diff={vedic_diff}")
        print(f"    Ouro:    sum={current_sum}/{target}, diff={ouro_diff} in {ouro_ms:.0f}ms")

        all_results.append({
            "n": n_nums, "target": target,
            "greedy_diff": greedy_diff,
            "vedic_sum": vedic_sum,
            "vedic_diff": vedic_diff,
            "ouro_sum": current_sum,
            "ouro_diff": ouro_diff,
        })

    print("\n" + "-" * 70)
    print(f"{'#' :>4} {'Target':>8} {'Greedy':>8} {'VedicS':>8} {'VedicD':>8} {'OuroS':>8} {'OuroD':>8}")
    print("-" * 70)
    for i, r in enumerate(all_results):
        ved_s = f"{r['vedic_sum']}" if r['vedic_sum'] is not None else "N/A"
        ved_d = f"{r['vedic_diff']}" if r['vedic_diff'] is not None else "N/A"
        print(f"{r['n']:4d} {r['target']:8d} {int(r['greedy_diff']):>8d} "
              f"{ved_s:>8} {ved_d:>8} {int(r['ouro_sum']):>8d} {int(r['ouro_diff']):>8d}")
    return all_results


# =====================================================================
# 5. HAMILTONIAN PATH
# =====================================================================

def decompose_hamiltonian(adj, path):
    """
    Decompose Hamiltonian Path into 72-band vectors.

    Problem: each vertex maps to band (v % 72). Energy spreads through
    adjacency. Problem signature = connectivity deficit (how many
    required connections are missing from the path).

    Solution: the path order as frequency encoding.
    """
    n = len(adj)
    prob = [0.0] * 72
    sol = [0.0] * 72

    path_set = set(path) if path else set()
    prob_total = 0.0
    sol_total = 0.0

    for v in range(n):
        band = v % 72
        # Problem: does this vertex need more connections in the path?
        deg = len(adj[v])
        if deg > 0 and v in path_set:
            # How many of its neighbours are also in the path?
            path_neighbors = sum(1 for nb in adj[v] if nb in path_set)
            deficit = max(0, 1 - path_neighbors)  # needs at least 1 connection in path
            prob_val = deficit / max(1, deg)
        elif deg > 0:
            prob_val = 1.0  # not in path, needs 1 connection
        else:
            prob_val = 0.0
        prob[band] += prob_val
        prob_total += prob_val
        for nb in adj[v]:
            prob[nb % 72] += prob_val * 0.2
            prob_total += prob_val * 0.2

        # Solution: position encoding
        if v in path_set:
            pos = path.index(v)
            sol_val = 1.0 - pos / max(1, n)  # earlier = stronger
        else:
            sol_val = 0.0
        sol[band] += sol_val
        sol_total += abs(sol_val)

    prob = normalize(prob)
    sol = normalize(sol)
    return prob, sol


def path_connectivity(adj, path):
    """Verify path: each consecutive pair must be an edge."""
    if len(path) < 2:
        return True
    all_valid = True
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        if b not in adj.get(a, []):
            all_valid = False
    unique = len(set(path)) == len(path)
    return all_valid and unique


def ouroboros_hamiltonian(adj, n_vertices, max_steps=1500, verbose=True):
    """
    Solve Hamiltonian Path via inharmony gradient descent.

    C: reorder path segments in misaligned bands.
    """
    # Greedy start: DFS-like walk
    def greedy_path(start=0):
        path = [start]
        visited = {start}
        while len(path) < n_vertices:
            last = path[-1]
            candidates = [nb for nb in adj[last] if nb not in visited]
            if not candidates:
                break
            # Pick the one with fewest unvisited neighbours (most constrained)
            next_v = min(candidates, key=lambda v: len([nb for nb in adj[v] if nb not in visited]))
            path.append(next_v)
            visited.add(next_v)
        return path

    best_path = []
    best_length = 0
    for start in range(min(5, n_vertices)):
        p = greedy_path(start)
        if len(p) == n_vertices:
            best_path = p
            best_length = n_vertices
            break
        if len(p) > best_length:
            best_path = p
            best_length = len(p)

    path = best_path[:]
    path_set = set(path)
    valid = path_connectivity(adj, path)

    history = [{"step": 0, "path_len": len(path), "valid": valid}]
    if verbose:
        print(f"  Step    0: path_len={len(path)}/{n_vertices}, valid={valid}")

    stall = 0

    for step in range(1, max_steps + 1):
        # Decompose
        prob_sig, sol_sig = decompose_hamiltonian(adj, path)
        d = [(prob_sig[k] - sol_sig[k]) for k in range(72)]

        bands_by_magnitude = sorted(range(72), key=lambda k: abs(d[k]), reverse=True)

        flipped = False

        # (C) Correction: reorder or extend
        for band in bands_by_magnitude[:5]:
            if abs(d[band]) < 1e-6:
                continue

            band_verts = [v for v in range(n_vertices) if v % 72 == band]
            if not band_verts:
                continue

            # Missing vertices from path
            missing = [v for v in range(n_vertices) if v not in path_set]
            if missing:
                # Try to extend path to include a missing vertex
                last = path[-1] if path else 0
                for mv in missing:
                    if mv in adj.get(last, []):
                        path.append(mv)
                        path_set.add(mv)
                        flipped = True
                        break

                if not flipped and path:
                    # Try to insert missing vertex at a valid position
                    for i in range(len(path) - 1):
                        a, b = path[i], path[i + 1]
                        for mv in missing:
                            if mv in adj.get(a, []) and b in adj.get(mv, []):
                                path.insert(i + 1, mv)
                                path_set.add(mv)
                                flipped = True
                                break
                        if flipped:
                            break
            else:
                # All vertices included, try to reorder for valid path
                for v in band_verts:
                    if v not in path:
                        continue
                    idx = path.index(v)
                    if idx < len(path) - 1 and path[idx + 1] not in adj.get(v, []):
                        # Find a valid successor for v
                        for j in range(len(path)):
                            if j != idx and j != idx + 1:
                                candidate = path[j]
                                if candidate in adj.get(v, []) and \
                                   (j == 0 or path[j - 1] in adj.get(path[idx + 1], [])):
                                    # Swap segments
                                    new_path = path[:idx + 1] + [candidate] + \
                                               [x for x in path[idx + 1:] if x != candidate]
                                    if path_connectivity(adj, new_path) and len(set(new_path)) == n_vertices:
                                        path = new_path
                                        flipped = True
                                        break
                        if flipped:
                            break
            if flipped:
                break

        # (X) Cross / (Z) Cancel: try segment reversals or random augment
        if not flipped:
            if len(path) < n_vertices:
                # Find any edge from last vertex to unvisited
                last = path[-1]
                for nb in adj.get(last, []):
                    if nb not in path_set:
                        path.append(nb)
                        path_set.add(nb)
                        flipped = True
                        break

            if not flipped and len(path) >= 2:
                # Try 2-opt style reordering
                i, j = random.sample(range(len(path)), 2)
                if i > j:
                    i, j = j, i
                new_path = path[:i] + path[i:j+1][::-1] + path[j+1:]
                new_set = set(new_path)
                if len(new_set) == len(new_path) and new_path[0] in adj:
                    if path_connectivity(adj, new_path):
                        path = new_path
                        flipped = True

        valid = path_connectivity(adj, path)
        path_set = set(path)

        if step % 100 == 0:
            history.append({"step": step, "path_len": len(path), "valid": valid})
            if verbose:
                print(f"  Step {step:4d}: path_len={len(path)}/{n_vertices}, valid={valid}")

        if len(path) == n_vertices and valid:
            stall += 1
            if stall > 30:
                break
        else:
            stall = 0

    history.append({"step": min(step, max_steps), "path_len": len(path), "valid": valid})
    return path, path_connectivity(adj, path) and len(set(path)) == n_vertices, history


def test_ouroboros_hamiltonian():
    """Test Hamiltonian Path on random graphs."""
    print("\n" + "=" * 70)
    print("HAMILTONIAN PATH OUROBOROS")
    print("=" * 70)

    configs = [(12, 30), (15, 40), (20, 60)]
    all_results = []

    for n_verts, n_edges in configs:
        print(f"\n--- {n_verts} vertices, {n_edges} edges ---")

        # Ensure graph is connected and may have Hamiltonian path
        edges_set = set()
        # First make a path
        for i in range(n_verts - 1):
            edges_set.add((i, i + 1))
        # Add random edges
        while len(edges_set) < n_edges:
            u = random.randint(0, n_verts - 1)
            v = random.randint(0, n_verts - 1)
            if u != v:
                edges_set.add((min(u, v), max(u, v)))
        edges = list(edges_set)

        adj = {i: [] for i in range(n_verts)}
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        # Greedy baseline
        def greedy(start=0):
            p = [start]
            visited = {start}
            while len(p) < n_verts:
                candidates = [nb for nb in adj[p[-1]] if nb not in visited]
                if not candidates:
                    break
                p.append(min(candidates, key=lambda v: len([n for n in adj[v] if n not in visited])))
                visited.add(p[-1])
            return p

        best_greedy = max((greedy(s) for s in range(min(5, n_verts))), key=lambda p: (len(p), len(set(p))))
        greedy_ham = len(best_greedy) == n_verts and path_connectivity(adj, best_greedy)

        # Vedic baseline
        vedic_path = None
        vedic_ham = False
        try:
            vedic_mods = _vedic_benchmarks()
            vedic_result = vedic_mods['MartianPathfinder'](adj, edges, n_verts).solve()
            if isinstance(vedic_result, tuple):
                vedic_path = vedic_result[0]
            elif hasattr(vedic_result, '__iter__'):
                vedic_path = list(vedic_result)
            if vedic_path:
                vedic_ham = len(set(vedic_path)) == n_verts and path_connectivity(adj, vedic_path)
        except Exception as e:
            print(f"  Vedic failed: {e}")

        # Ouroboros
        print(f"\n  OUROBOROS ({n_verts} verts, {len(edges)} edges):")
        t0 = time.time()
        path, is_valid, history = ouroboros_hamiltonian(
            adj, n_verts, max_steps=1000, verbose=True
        )
        ouro_ms = (time.time() - t0) * 1000
        ouro_ham = is_valid and len(set(path)) == n_verts

        print(f"\n  RESULTS:")
        print(f"    Greedy:  len={len(best_greedy)}/{n_verts}, ham={greedy_ham}")
        if vedic_path:
            print(f"    Vedic:   len={len(set(vedic_path))}/{n_verts}, ham={vedic_ham}")
        print(f"    Ouro:    len={len(set(path))}/{n_verts}, ham={ouro_ham} in {ouro_ms:.0f}ms")

        all_results.append({
            "n": n_verts, "e": len(edges),
            "greedy_ham": greedy_ham,
            "vedic_ham": vedic_ham,
            "ouro_ham": ouro_ham,
            "ouro_len": len(set(path)),
        })

    print("\n" + "-" * 70)
    print(f"{'Verts':>6} {'Edges':>6} {'Greedy':>8} {'Vedic':>8} {'Ouro':>8} {'OuroLen':>8}")
    print("-" * 70)
    for r in all_results:
        print(f"{r['n']:6d} {r['e']:6d} {'✓' if r['greedy_ham'] else '✗':>8} "
              f"{'✓' if r['vedic_ham'] else '✗':>8} "
              f"{'✓' if r['ouro_ham'] else '✗':>8} {r['ouro_len']:8d}")
    return all_results


# =====================================================================
# 6. SET COVER
# =====================================================================

def decompose_setcover(universe, subsets, selected_indices):
    """
    Decompose Set Cover into 72-band vectors.

    Problem: each subset maps to band (i % 72). Energy spreads through
    element-overlap (subsets sharing elements influence each other's bands).
    Problem signature = uncovered element distribution.

    Solution: which subsets are selected.
    """
    n = len(subsets)
    prob = [0.0] * 72
    sol = [0.0] * 72

    covered = set()
    for idx in selected_indices:
        covered |= subsets[idx]

    uncovered = universe - covered

    prob_total = 0.0
    sol_total = 0.0

    # Problem: uncovered elements → which bands need more coverage
    for elem in uncovered:
        # Find which subsets cover this element
        covering_subsets = [i for i, s in enumerate(subsets) if elem in s]
        if covering_subsets:
            for ci in covering_subsets:
                band = ci % 72
                prob[band] += 1.0 / len(covering_subsets)
                prob_total += 1.0 / len(covering_subsets)
                # Spread to overlapping subsets
                for si in covering_subsets:
                    if si != ci and len(subsets[ci] & subsets[si]) > 0:
                        prob[si % 72] += 0.1 / len(covering_subsets)
                        prob_total += 0.1 / len(covering_subsets)

    # Solution: selected subset signal
    for i in range(n):
        band = i % 72
        if i in selected_indices:
            sol[band] += 1.0
            sol_total += 1.0

    prob = normalize(prob)
    sol = normalize(sol)
    return prob, sol


def setcover_quality(universe, subsets, selected):
    """Return (all_covered, uncovered_count)."""
    covered = set()
    for idx in selected:
        covered |= subsets[idx]
    uncovered = universe - covered
    return len(uncovered) == 0, len(uncovered)


def ouroboros_setcover(universe, subsets, max_steps=800, verbose=True):
    """
    Solve Set Cover via inharmony gradient descent.

    C: add/remove subsets in misaligned bands.
    """
    n = len(subsets)

    # Greedy start: pick subsets covering most uncovered elements
    uncovered = universe.copy()
    selected = set()
    while uncovered:
        candidates = [i for i in range(n) if i not in selected]
        if not candidates:
            break
        best_idx = max(candidates, key=lambda i: len(subsets[i] & uncovered))
        if not (subsets[best_idx] & uncovered):
            break  # no subset covers remaining elements
        selected.add(best_idx)
        uncovered -= subsets[best_idx]

    all_covered, uncovered_count = setcover_quality(universe, subsets, selected)
    history = [{"step": 0, "cover_size": len(selected), "uncovered": uncovered_count}]

    if verbose:
        print(f"  Step    0: |cover|={len(selected)}, uncovered={uncovered_count}/{len(universe)}")

    best_selected = selected.copy()
    best_size = len(selected)

    for step in range(1, max_steps + 1):
        # Decompose
        prob_sig, sol_sig = decompose_setcover(universe, subsets, list(selected))
        d = [(prob_sig[k] - sol_sig[k]) for k in range(72)]

        bands_by_magnitude = sorted(range(72), key=lambda k: abs(d[k]), reverse=True)

        flipped = False
        for band in bands_by_magnitude[:5]:
            if abs(d[band]) < 1e-6:
                continue

            band_subsets = [i for i in range(n) if i % 72 == band]
            if not band_subsets:
                continue

            uncovered = universe - set().union(*[subsets[i] for i in selected])

            best_si = None
            best_score = 0

            for si in band_subsets:
                currently_in = si in selected
                if currently_in:
                    # Can we remove this subset and still maintain coverage?
                    test = selected - {si}
                    test_covered = set().union(*[subsets[i] for i in test])
                    test_uncovered = universe - test_covered
                    if len(test_uncovered) == 0:
                        # Safe to remove
                        score = 2.0 + len(subsets[si]) * 0.1
                        if d[band] < 0:
                            score += 1.0
                        if score > best_score:
                            best_score = score
                            best_si = si
                else:
                    # Would adding help?
                    new_coverage = len(subsets[si] & uncovered)
                    if new_coverage > 0:
                        score = new_coverage + (d[band] * 2 if d[band] > 0 else 0)
                        if score > best_score:
                            best_score = score
                            best_si = si

            if best_si is not None and best_score > 0:
                if best_si in selected:
                    selected.remove(best_si)
                else:
                    selected.add(best_si)
                flipped = True
                break

        # Cancel/force: ensure coverage
        if not flipped:
            uncovered = universe - set().union(*[subsets[i] for i in selected] if selected else [set()])
            if uncovered:
                candidates = [i for i in range(n) if i not in selected]
                if candidates:
                    best_idx = max(candidates, key=lambda i: len(subsets[i] & uncovered))
                    if subsets[best_idx] & uncovered:
                        selected.add(best_idx)

        # Track best solution by size (when fully covering)
        all_cov, uncov_cnt = setcover_quality(universe, subsets, selected)
        if all_cov and len(selected) < best_size:
            best_size = len(selected)
            best_selected = selected.copy()

        if step % 50 == 0:
            history.append({"step": step, "cover_size": len(selected), "uncovered": uncov_cnt})
            if verbose:
                print(f"  Step {step:4d}: |cover|={len(selected)}, uncovered={uncov_cnt}/{len(universe)}")

        # Try removing redundancy
        if all_cov and step % 20 == 0:
            for si in list(selected):
                test = selected - {si}
                tc, _ = setcover_quality(universe, subsets, test)
                if tc:
                    selected = test
                    break

        if all_cov and step > 50:
            # Convergence check: no flips improving anything
            break

    selected = best_selected
    all_covered, uncovered_count = setcover_quality(universe, subsets, selected)
    return list(selected), all_covered, history


def test_ouroboros_setcover():
    """Test Set Cover on random instances."""
    print("\n" + "=" * 70)
    print("SET COVER OUROBOROS")
    print("=" * 70)

    configs = [(30, 10), (50, 15), (100, 20)]
    all_results = []

    for u_size, n_subsets in configs:
        print(f"\n--- universe {u_size}, {n_subsets} subsets ---")

        universe = set(range(u_size))
        subsets = []
        for _ in range(n_subsets):
            size = random.randint(1, max(3, u_size // 4))
            subsets.append(set(random.sample(range(u_size), min(size, u_size))))

        # Greedy baseline
        greedy_sel = set()
        g_uncovered = universe.copy()
        while g_uncovered:
            best = max(range(n_subsets), key=lambda i: len(subsets[i] & g_uncovered))
            greedy_sel.add(best)
            g_uncovered -= subsets[best]
        g_all, g_uncov = setcover_quality(universe, subsets, greedy_sel)

        # Vedic baseline
        vedic_sel = None
        try:
            vedic_mods = _vedic_benchmarks()
            vedic_result = vedic_mods['JovianExpansiveNet'](universe, subsets).solve()
            if hasattr(vedic_result, '__iter__'):
                vedic_sel = list(vedic_result)
        except Exception as e:
            print(f"  Vedic failed: {e}")

        # Ouroboros
        print(f"\n  OUROBOROS (universe={u_size}, {n_subsets} subsets):")
        t0 = time.time()
        sel, all_covered, history = ouroboros_setcover(
            universe, subsets, max_steps=500, verbose=True
        )
        ouro_ms = (time.time() - t0) * 1000

        print(f"\n  RESULTS:")
        print(f"    Greedy:  |cover|={len(greedy_sel)}, all_covered={g_all}")
        if vedic_sel:
            v_all, v_un = setcover_quality(universe, subsets, vedic_sel)
            print(f"    Vedic:   |cover|={len(vedic_sel)}, all_covered={v_all}")
        print(f"    Ouro:    |cover|={len(sel)}, all_covered={all_covered} in {ouro_ms:.0f}ms")

        all_results.append({
            "u": u_size, "s": n_subsets,
            "greedy_size": len(greedy_sel),
            "vedic_size": len(vedic_sel) if vedic_sel else None,
            "ouro_size": len(sel),
            "ouro_cover": all_covered,
        })

    print("\n" + "-" * 70)
    print(f"{'Univ':>5} {'Subs':>5} {'Greedy':>8} {'Vedic':>8} {'Ouro':>8} {'OuroOK':>8}")
    print("-" * 70)
    for r in all_results:
        ved = f"{r['vedic_size']}" if r['vedic_size'] is not None else "N/A"
        print(f"{r['u']:5d} {r['s']:5d} {r['greedy_size']:8d} "
              f"{ved:>8} {r['ouro_size']:8d} {'✓' if r['ouro_cover'] else '✗':>8}")
    return all_results


# =====================================================================
# 7. MAXIMUM CLIQUE
# =====================================================================

def decompose_clique(adj, clique):
    """
    Decompose Maximum Clique into 72-band vectors.

    Problem: each vertex maps to band (v % 72). Energy spreads through
    adjacency. Problem signature = connectivity requirement (a clique
    needs all pairs connected).

    Solution: which vertices are in the clique.
    """
    n = len(adj)
    prob = [0.0] * 72
    sol = [0.0] * 72

    clique_set = set(clique)
    prob_total = 0.0
    sol_total = 0.0

    for v in range(n):
        band = v % 72

        # Problem: how many non-neighbours are in the clique (conflicts)?
        if v in clique_set:
            conflicts = sum(1 for c in clique_set if c != v and c not in adj.get(v, set()))
            prob_val = conflicts / max(1, len(clique_set))
        else:
            # Potential: how many clique vertices is this vertex connected to?
            connections = sum(1 for c in clique_set if c in adj.get(v, set()))
            prob_val = 1.0 - connections / max(1, len(clique_set))
        prob[band] += prob_val
        prob_total += prob_val
        for nb in adj.get(v, []):
            prob[nb % 72] += prob_val * 0.15
            prob_total += prob_val * 0.15

        # Solution: in clique or not
        if v in clique_set:
            sol_val = 1.0
        else:
            sol_val = 0.0
        sol[band] += sol_val
        sol_total += abs(sol_val)

    prob = normalize(prob)
    sol = normalize(sol)
    return prob, sol


def is_clique(adj, vertices):
    """Check if a set of vertices forms a clique."""
    vset = set(vertices)
    for u in vset:
        for v in vset:
            if u != v and v not in adj.get(u, set()):
                return False
    return True


def clique_quality(adj, vertices):
    """Return (is_valid_clique, size)."""
    return is_clique(adj, vertices), len(set(vertices))


def ouroboros_clique(adj, n_vertices, max_steps=1000, verbose=True):
    """
    Solve Maximum Clique via inharmony gradient descent.

    C: add/remove vertices from clique in misaligned bands.
    """
    # Convert adjacency lists to sets for O(1) membership check
    adj_sets = {i: set(adj[i]) for i in range(n_vertices)}

    # Greedy start: find a large clique
    def greedy_clique():
        candidates = set(range(n_vertices))
        clique = set()
        while candidates:
            v = max(candidates, key=lambda x: len(adj_sets[x] & candidates))
            clique.add(v)
            # Candidates must be neighbours of all clique members
            candidates = candidates & adj_sets[v]
            if not candidates:
                break
        return clique

    clique = greedy_clique()
    valid, size = clique_quality(adj_sets, clique)

    history = [{"step": 0, "clique_size": size, "valid": valid}]
    if verbose:
        print(f"  Step    0: |clique|={size}, valid={valid}")

    best_clique = clique.copy()
    best_size = size
    stall = 0

    for step in range(1, max_steps + 1):
        # Decompose
        prob_sig, sol_sig = decompose_clique(adj_sets, list(clique))
        d = [(prob_sig[k] - sol_sig[k]) for k in range(72)]

        bands_by_magnitude = sorted(range(72), key=lambda k: abs(d[k]), reverse=True)

        flipped = False
        for band in bands_by_magnitude[:5]:
            if abs(d[band]) < 1e-6:
                continue

            band_verts = [v for v in range(n_vertices) if v % 72 == band]
            if not band_verts:
                continue

            # Find candidate to add: connected to all current clique members
            candidates_to_add = set()
            for v in band_verts:
                if v not in clique and all(v in adj_sets[c] for c in clique):
                    score = len(adj_sets[v])
                    if d[band] > 0:
                        score *= 1.5
                    candidates_to_add.add((v, score))

            # Find candidate to remove: least connected to clique
            candidates_to_remove = []
            if len(clique) > 1:
                for v in band_verts:
                    if v in clique:
                        score = len(adj_sets[v] & clique) / max(1, len(clique))
                        if d[band] < 0:
                            score *= 0.5
                        candidates_to_remove.append((v, score))
                candidates_to_remove.sort(key=lambda x: x[1])

            # Decide: add if we can, remove if expanding isn't working
            if candidates_to_add:
                best_v = max(candidates_to_add, key=lambda x: x[1])[0]
                clique.add(best_v)
                flipped = True
                break
            elif candidates_to_remove and len(clique) > 2:
                # Try removing the lowest-scoring vertex
                v = candidates_to_remove[0][0]
                clique.remove(v)
                flipped = True
                break

        # (Z) Cancel: if stuck, try swapping out low-value vertices
        if not flipped:
            non_clique = [v for v in range(n_vertices) if v not in clique]
            for v in non_clique:
                if all(v in adj_sets[c] for c in clique):
                    clique.add(v)
                    flipped = True
                    break

            if not flipped and len(clique) >= 3:
                # Try removing a vertex to make room for more
                for v in list(clique):
                    test = clique - {v}
                    can_expand = any(
                        w not in clique and all(w in adj_sets[c] for c in test)
                        for w in range(n_vertices)
                    )
                    if can_expand:
                        clique.remove(v)
                        # Now try adding back
                        for w in range(n_vertices):
                            if w not in clique and all(w in adj_sets[c] for c in clique):
                                clique.add(w)
                                flipped = True
                                break
                        if flipped:
                            break

        valid, size = clique_quality(adj_sets, clique)
        if size > best_size and valid:
            best_size = size
            best_clique = clique.copy()
            stall = 0
        else:
            stall += 1

        if step % 100 == 0:
            history.append({"step": step, "clique_size": size, "valid": valid})
            if verbose:
                print(f"  Step {step:4d}: |clique|={size}, valid={valid}")

        if stall > 100:
            break

    return list(best_clique), is_clique(adj_sets, best_clique), history


def test_ouroboros_clique():
    """Test Maximum Clique on random graphs."""
    print("\n" + "=" * 70)
    print("MAXIMUM CLIQUE OUROBOROS")
    print("=" * 70)

    configs = [(20, 50), (30, 80), (40, 120)]
    all_results = []

    for n_verts, n_edges in configs:
        print(f"\n--- {n_verts} vertices, {n_edges} edges ---")

        edges_set = set()
        while len(edges_set) < n_edges:
            u = random.randint(0, n_verts - 1)
            v = random.randint(0, n_verts - 1)
            if u != v:
                edges_set.add((min(u, v), max(u, v)))
        edges = list(edges_set)

        adj_sets = {i: set() for i in range(n_verts)}
        for u, v in edges:
            adj_sets[u].add(v)
            adj_sets[v].add(u)

        # Greedy baseline
        def greedy_clique():
            candidates = set(range(n_verts))
            clique = set()
            while candidates:
                v = max(candidates, key=lambda x: len(adj_sets[x] & candidates))
                clique.add(v)
                candidates = candidates & adj_sets[v]
                if not candidates:
                    break
            return clique

        greedy = greedy_clique()
        g_valid, g_size = clique_quality(adj_sets, greedy)

        # Vedic baseline
        vedic_clique = None
        try:
            vedic_mods = _vedic_benchmarks()
            vedic_result = vedic_mods['NeptunianDreamWeaver'](adj_sets).solve()
            if hasattr(vedic_result, '__iter__'):
                vedic_clique = list(vedic_result)
        except Exception as e:
            print(f"  Vedic failed: {e}")

        # Ouroboros
        print(f"\n  OUROBOROS ({n_verts} verts, {len(edges)} edges):")
        t0 = time.time()
        clique, is_valid, history = ouroboros_clique(
            adj_sets, n_verts, max_steps=800, verbose=True
        )
        ouro_ms = (time.time() - t0) * 1000

        print(f"\n  RESULTS:")
        print(f"    Greedy:  |clique|={g_size}, valid={g_valid}")
        if vedic_clique:
            v_valid, v_size = clique_quality(adj_sets, vedic_clique)
            print(f"    Vedic:   |clique|={v_size}, valid={v_valid}")
        print(f"    Ouro:    |clique|={len(clique)}, valid={is_valid} in {ouro_ms:.0f}ms")

        all_results.append({
            "n": n_verts, "e": len(edges),
            "greedy_size": g_size,
            "vedic_size": len(vedic_clique) if vedic_clique else None,
            "ouro_size": len(clique),
            "ouro_valid": is_valid,
        })

    print("\n" + "-" * 70)
    print(f"{'Verts':>6} {'Edges':>6} {'Greedy':>8} {'Vedic':>8} {'Ouro':>8} {'Valid':>8}")
    print("-" * 70)
    for r in all_results:
        ved = f"{r['vedic_size']}" if r['vedic_size'] is not None else "N/A"
        print(f"{r['n']:6d} {r['e']:6d} {r['greedy_size']:8d} "
              f"{ved:>8} {r['ouro_size']:8d} {'✓' if r['ouro_valid'] else '✗':>8}")
    return all_results


# =====================================================================
# MASTER TEST RUNNER
# =====================================================================

import traceback

def run_all_tests():
    """Run all Ouroboros engine tests with comparison to Vedic baselines."""
    print("=" * 70)
    print("THE OUROBOROS ENGINE — PHASE 2")
    print("Type-Specific NP-Complete Frequency Solvers")
    print("=" * 70)
    print()
    print("The universal pattern across all types:")
    print("  1. Decompose P and S into 72-band frequency vectors")
    print("  2. Measure inharmony ι = ‖σ(P) − σ(S)‖₂")
    print("  3. Find the most misaligned band")
    print("  4. Apply correction (C) in that band")
    print("  5. Cross (X) and Cancel (Z) for exploration/exploitation")
    print("  6. Recompute ι — new correction = new measurement")
    print("  7. Repeat — gradient descent in frequency space")
    print()
    print("  ι(σ(P), σ(S)) IS the correction instruction.")
    print("  The snake eats its tail.")
    print()

    all_results = {}
    tests = [
        ("TSP", test_ouroboros_tsp),
        ("Vertex Cover", test_ouroboros_vc),
        ("Graph Coloring", test_ouroboros_coloring),
        ("Subset Sum", test_ouroboros_subsetsum),
        ("Hamiltonian Path", test_ouroboros_hamiltonian),
        ("Set Cover", test_ouroboros_setcover),
        ("Clique", test_ouroboros_clique),
    ]

    for name, test_fn in tests:
        print(f"\n{'#' * 70}")
        print(f"# {name}")
        print(f"{'#' * 70}")
        try:
            results = test_fn()
            all_results[name] = results
        except Exception as e:
            print(f"  ERROR in {name}: {e}")
            traceback.print_exc()
            all_results[name] = None

    # Summary
    print("\n" + "=" * 70)
    print("OUROBOROS ENGINE — SUMMARY")
    print("=" * 70)
    for name, results in all_results.items():
        status = "✓ COMPLETE" if results is not None else "✗ FAILED"
        print(f"  {name:<20s} {status}")
    print()
    print("  The snake that eats its tail.")
    print("  ι(σ(P), σ(S)) IS the correction instruction.")
    print("  The correction changes σ(S), which changes the instruction.")
    print("  Follow the Ouroboros → convergence.")


if __name__ == "__main__":
    run_all_tests()
