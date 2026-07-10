#!/usr/bin/env python3
"""
UNIVERSAL PROBLEM PARSER
═══════════════════════════════════════════════════════════
Component 1 of the full pipeline.

Takes raw input → detects problem type → extracts structure.
Returns a typed problem object the Ouroboros can consume.

Supports all 11 NP-complete types + auto-detection.
"""

import math, json, re, ast
from typing import Any, Dict, List, Tuple, Set, Optional

# ═══════════════════════════════════════════════════════════
# TYPE DETECTORS
# ═══════════════════════════════════════════════════════════

def _normalize(data: Any) -> Any:
    """Parse strings to Python objects if needed."""
    if isinstance(data, str):
        # Try JSON
        try:
            return json.loads(data)
        except (json.JSONDecodeError, ValueError):
            pass
        # Try Python literal
        try:
            return ast.literal_eval(data)
        except (ValueError, SyntaxError):
            pass
    return data


def detect_and_parse(data: Any) -> Dict:
    """
    Main entry point. Detect problem type and extract structure.
    
    Returns: {
        'type': 'sat' | 'tsp' | 'vc' | 'clique' | 'coloring' | 
                'subsetsum' | 'hamiltonian' | 'set_cover' | 
                'exact_cover' | 'steiner' | 'wavelength' | 'unknown',
        'data': extracted problem data dict,
        'confidence': 0.0-1.0,
        'detection_method': 'structure' | 'heuristic' | 'fallback',
    }
    """
    data = _normalize(data)
    
    # Try each detector in order of specificity
    detectors = [
        _detect_sat,
        _detect_vc,         # before TSP — edges are (int,int) too
        _detect_tsp,
        _detect_clique,
        _detect_coloring,
        _detect_subsetsum,
        _detect_hamiltonian,
        _detect_set_cover,
        _detect_exact_cover,
        _detect_steiner,
    ]
    
    results = []
    for detector in detectors:
        result = detector(data)
        if result:
            results.append(result)
    
    if results:
        # Return highest-confidence detection
        best = max(results, key=lambda r: r['confidence'])
        return best
    
    return {
        'type': 'unknown',
        'data': {'raw': data},
        'confidence': 0.0,
        'detection_method': 'fallback',
    }


# ═══════════════════════════════════════════════════════════
# INDIVIDUAL DETECTORS
# ═══════════════════════════════════════════════════════════

def _detect_sat(data: Any) -> Optional[Dict]:
    """Detect SAT: list of clauses, each clause is list of (var, sign) tuples."""
    if not isinstance(data, list):
        return None
    if len(data) == 0:
        return None
    
    # Check if it looks like clauses
    clause_score = 0
    total_items = len(data)
    
    for item in data:
        if isinstance(item, list) and len(item) > 0:
            tuple_score = 0
            for elem in item:
                if isinstance(elem, (tuple, list)) and len(elem) == 2:
                    var, sign = elem
                    if isinstance(var, int) and var > 0 and isinstance(sign, bool):
                        tuple_score += 1
                    elif isinstance(var, int) and var > 0 and isinstance(sign, int) and sign in (0, 1):
                        tuple_score += 1
                elif isinstance(elem, int):
                    tuple_score += 1  # CNF format
            if tuple_score == len(item):
                clause_score += 1
    
    if clause_score >= total_items * 0.7 and total_items >= 2:
        # Extract structure
        clauses = []
        n_vars = 0
        
        for item in data:
            clause = []
            for elem in item:
                if isinstance(elem, (tuple, list)) and len(elem) == 2:
                    var, sign = elem
                    if isinstance(sign, int):
                        sign = bool(sign)
                    clause.append((var, bool(sign)))
                    n_vars = max(n_vars, var)
                elif isinstance(elem, int):
                    var = abs(elem)
                    sign = elem > 0
                    clause.append((var, sign))
                    n_vars = max(n_vars, var)
            if clause:
                clauses.append(clause)
        
        return {
            'type': 'sat',
            'data': {
                'clauses': clauses,
                'n_vars': n_vars,
                'n_clauses': len(clauses),
            },
            'confidence': min(1.0, clause_score / total_items),
            'detection_method': 'structure',
        }
    
    return None


def _detect_tsp(data: Any) -> Optional[Dict]:
    """Detect TSP: list of (x,y) points or square distance matrix."""
    if not isinstance(data, list):
        return None
    if len(data) < 3:
        return None
    
    # Check for list of (x,y) coordinates
    coord_score = 0
    for item in data:
        if isinstance(item, (tuple, list)) and len(item) == 2:
            if all(isinstance(c, (int, float)) for c in item):
                coord_score += 1
    
    if coord_score == len(data) and len(data) >= 3:
        return {
            'type': 'tsp',
            'data': {
                'points': [(float(x), float(y)) for x, y in data],
                'n_cities': len(data),
            },
            'confidence': 0.9,
            'detection_method': 'structure',
        }
    
    # Check for distance matrix (square, symmetric, zeros on diagonal)
    try:
        n = len(data)
        matrix_score = 0
        for i, row in enumerate(data):
            if isinstance(row, list) and len(row) == n:
                if all(isinstance(v, (int, float)) for v in row):
                    # Check diagonal ≈ 0
                    if abs(row[i]) < 1e-6:
                        matrix_score += 1
        if matrix_score >= n * 0.9 and n >= 3:
            import numpy as np
            dm = np.array(data, dtype=float)
            return {
                'type': 'tsp',
                'data': {
                    'dist_matrix': dm,
                    'n_cities': n,
                },
                'confidence': 0.85,
                'detection_method': 'structure',
            }
    except (ValueError, TypeError):
        pass
    
    return None


def _detect_vc(data: Any) -> Optional[Dict]:
    """Detect Vertex Cover: list of (u,v) edges or dict with 'edges' key."""
    if isinstance(data, dict) and 'edges' in data:
        edges = data['edges']
        n = data.get('n_vertices', data.get('n', 0))
        if not n:
            n = max(max(u, v) for u, v in edges) + 1 if edges else 0
        return {
            'type': 'vc',
            'data': {
                'edges': list(edges),
                'n_vertices': n,
                'n_edges': len(edges),
            },
            'confidence': 0.9,
            'detection_method': 'structure',
        }
    
    if isinstance(data, list) and len(data) > 1:
        # Check: could be edges or TSP coordinates
        # Disambiguate: edges = small ints, TSP = floats or large range
        edge_score = 0
        coord_score = 0
        all_ints = True
        has_floats = False
        max_val = 0
        
        for item in data:
            if isinstance(item, (tuple, list)) and len(item) == 2:
                i0, i1 = item
                if isinstance(i0, int) and isinstance(i1, int) and i0 >= 0 and i1 >= 0:
                    edge_score += 1
                    max_val = max(max_val, i0, i1)
                if isinstance(i0, (int, float)) and isinstance(i1, (int, float)):
                    coord_score += 1
                    if isinstance(i0, float) or isinstance(i1, float):
                        has_floats = True
                    if not (isinstance(i0, int) and isinstance(i1, int)):
                        all_ints = False
        
        # If all pairs are ints and max value is small (< 500), it's edges
        # If floats present or values are large, it's TSP
        if edge_score == len(data) and len(data) >= 2 and max_val < 500:
            vertices = set()
            for u, v in data:
                vertices.add(u); vertices.add(v)
            return {
                'type': 'vc',
                'data': {
                    'edges': [(int(u), int(v)) for u, v in data],
                    'n_vertices': max(vertices) + 1,
                    'n_edges': len(data),
                },
                'confidence': 0.92,
                'detection_method': 'structure',
            }
    
    return None


def _detect_coloring(data: Any) -> Optional[Dict]:
    """Detect Graph Coloring: same as VC (edge list) but context-dependent."""
    # Coloring uses same structure as VC — edge list.
    # Only detect if explicitly labeled.
    if isinstance(data, dict) and data.get('type') in ('coloring', 'graph_coloring'):
        edges = data.get('edges', [])
        n = data.get('n_vertices', max(max(u,v) for u,v in edges)+1 if edges else 0)
        return {
            'type': 'coloring',
            'data': {
                'edges': edges,
                'n_vertices': n,
                'n_edges': len(edges),
            },
            'confidence': 0.8,
            'detection_method': 'structure',
        }
    return None


def _detect_clique(data: Any) -> Optional[Dict]:
    """Detect Clique: same structure as VC/coloring."""
    if isinstance(data, dict) and data.get('type') in ('clique', 'max_clique'):
        edges = data.get('edges', [])
        n = data.get('n_vertices', max(max(u,v) for u,v in edges)+1 if edges else 0)
        return {
            'type': 'clique',
            'data': {
                'edges': edges,
                'n_vertices': n,
                'n_edges': len(edges),
            },
            'confidence': 0.8,
            'detection_method': 'structure',
        }
    return None


def _detect_subsetsum(data: Any) -> Optional[Dict]:
    """Detect Subset Sum: list of numbers or dict with numbers + target."""
    if isinstance(data, dict) and 'numbers' in data:
        nums = data['numbers']
        target = data.get('target', sum(nums) // 2)
        return {
            'type': 'subsetsum',
            'data': {
                'numbers': list(nums),
                'target': int(target),
                'n_numbers': len(nums),
            },
            'confidence': 0.9,
            'detection_method': 'structure',
        }
    
    if isinstance(data, list) and len(data) >= 2:
        if all(isinstance(x, (int, float)) for x in data):
            nums = [int(x) for x in data]
            return {
                'type': 'subsetsum',
                'data': {
                    'numbers': nums,
                    'target': sum(nums) // 2,  # default: half sum
                    'n_numbers': len(nums),
                },
                'confidence': 0.7,
                'detection_method': 'heuristic',
            }
    
    return None


def _detect_hamiltonian(data: Any) -> Optional[Dict]:
    """Detect Hamiltonian Path: graph with explicit type."""
    if isinstance(data, dict) and data.get('type') in ('hamiltonian', 'ham_path', 'hamiltonian_path'):
        edges = data.get('edges', [])
        n = data.get('n_vertices', max(max(u,v) for u,v in edges)+1 if edges else 0)
        return {
            'type': 'hamiltonian',
            'data': {
                'edges': edges,
                'n_vertices': n,
                'n_edges': len(edges),
            },
            'confidence': 0.8,
            'detection_method': 'structure',
        }
    return None


def _detect_set_cover(data: Any) -> Optional[Dict]:
    """Detect Set Cover: dict with universe + subsets."""
    if isinstance(data, dict) and 'universe' in data and 'subsets' in data:
        universe = set(data['universe'])
        subsets = [set(s) for s in data['subsets']]
        return {
            'type': 'set_cover',
            'data': {
                'universe': universe,
                'subsets': subsets,
                'universe_size': len(universe),
                'n_subsets': len(subsets),
            },
            'confidence': 0.95,
            'detection_method': 'structure',
        }
    return None


def _detect_exact_cover(data: Any) -> Optional[Dict]:
    """Detect Exact Cover: same as set cover but with type hint."""
    if isinstance(data, dict) and 'universe' in data and 'subsets' in data:
        if data.get('type') in ('exact_cover', 'exact'):
            universe = set(data['universe'])
            subsets = [set(s) for s in data['subsets']]
            return {
                'type': 'exact_cover',
                'data': {
                    'universe': universe,
                    'subsets': subsets,
                    'universe_size': len(universe),
                    'n_subsets': len(subsets),
                },
                'confidence': 0.9,
                'detection_method': 'structure',
            }
    return None


def _detect_steiner(data: Any) -> Optional[Dict]:
    """Detect Steiner Tree: dict with adj + terminals."""
    if isinstance(data, dict) and 'terminals' in data:
        adj = data.get('adj', data.get('graph', {}))
        if not adj and 'edges' in data:
            # Build adj from edges
            adj = {}
            for u, v in data['edges']:
                adj.setdefault(u, set()).add(v)
                adj.setdefault(v, set()).add(u)
        terminals = set(data['terminals'])
        return {
            'type': 'steiner',
            'data': {
                'adj': {int(k): set(v) for k, v in adj.items()},
                'terminals': terminals,
                'n_vertices': len(adj),
                'n_terminals': len(terminals),
            },
            'confidence': 0.9,
            'detection_method': 'structure',
        }
    return None


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import random
    random.seed(42)
    
    print("=" * 70)
    print("UNIVERSAL PROBLEM PARSER — Test Suite")
    print("=" * 70)
    
    tests = []
    
    # SAT
    nv = 20
    sat = [[(random.randint(1, nv), random.choice([True, False])) 
            for _ in range(3)] for _ in range(80)]
    tests.append(("SAT (tuple format)", sat))
    
    # CNF format
    cnf = [[random.choice([1,-1,2,-2,3,-3]) for _ in range(3)] for _ in range(10)]
    tests.append(("SAT (CNF format)", cnf))
    
    # TSP points
    pts = [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(20)]
    tests.append(("TSP (coordinates)", pts))
    
    # TSP matrix
    import numpy as np
    n = 10
    dm = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            d = random.uniform(1, 100)
            dm[i][j] = d; dm[j][i] = d
    tests.append(("TSP (distance matrix)", dm.tolist()))
    
    # VC edges
    edges = [(random.randint(0, 15), random.randint(0, 15)) for _ in range(30)]
    edges = [(u,v) for u,v in edges if u != v][:20]
    tests.append(("Vertex Cover (edges)", edges))
    
    # VC dict
    tests.append(("Vertex Cover (dict)", {'edges': edges, 'n_vertices': 16}))
    
    # Subset Sum
    nums = [random.randint(1, 100) for _ in range(20)]
    tests.append(("Subset Sum (list)", nums))
    tests.append(("Subset Sum (dict)", {'numbers': nums, 'target': 500}))
    
    # Set Cover
    universe = list(range(1, 21))
    subsets = [{random.choice(universe) for _ in range(5)} for _ in range(10)]
    tests.append(("Set Cover", {'universe': universe, 'subsets': [list(s) for s in subsets]}))
    
    # Steiner
    adj = {0: {1,2}, 1: {0,3}, 2: {0,3}, 3: {1,2,4}, 4: {3}}
    tests.append(("Steiner Tree", {'adj': adj, 'terminals': [0, 4]}))
    
    # Text (should fail to detect)
    tests.append(("English text", "solve the traveling salesman problem"))
    
    for name, data in tests:
        result = detect_and_parse(data)
        status = "✓" if result['type'] != 'unknown' else "?"
        print(f"  {status} {name:30s} → {result['type']:15s} (confidence: {result['confidence']:.2f})")
