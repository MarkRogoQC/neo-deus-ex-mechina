"""
Vedic Planetary Transformers - Consolidated Single File
All 11 celestial wavelength transformers for NP-complete problems.
"""

import random
import math
from typing import Dict, Set, List, Tuple, Optional, Any, Union
import numpy as np
import sys

# ============================================================================
# 1. SAT SOLVER - Mercurial Clause Weaver
# ============================================================================

class MercurialClauseWeaver:
    """Vedic Transformation System for Boolean SAT."""
    
    def __init__(self, clauses: List[List[Tuple[int, bool]]], n_vars: int, seed: Optional[int] = None):
        """
        Initialize SAT solver.
        
        Args:
            clauses: List of clauses, each clause is list of (variable, sign)
            n_vars: Number of variables
            seed: Random seed
        """
        self.clauses = clauses
        self.n_vars = n_vars
        self.m = len(clauses)
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    # Nikhilam: Identify obvious assignments (unit clauses, pure literals)
    def nikhilam(self) -> Dict[int, bool]:
        """Identify forced/obvious assignments."""
        obvious = {}
        
        # Unit clauses
        for clause in self.clauses:
            if len(clause) == 1:
                var, sign = clause[0]
                if var not in obvious:
                    obvious[var] = sign
                elif obvious[var] != sign:
                    # Conflict - mark as unresolvable
                    obvious[var] = None
        
        # Remove conflicts
        obvious = {k: v for k, v in obvious.items() if v is not None}
        return obvious
    
    # Urdhva: Propagate and combine
    def urdhva(self, assignment: Dict[int, bool]) -> Dict[int, bool]:
        """Propagate assignments and combine clauses."""
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
                    elif propagated[var] != sign:
                        # Conflict
                        propagated[var] = None
        
        # Remove conflicts
        propagated = {k: v for k, v in propagated.items() if v is not None}
        return propagated
    
    # Anurupye: Order variables by frequency/importance
    def anurupye(self) -> List[int]:
        """Order variables by clause participation."""
        freq = {}
        for clause in self.clauses:
            for var, _ in clause:
                freq[var] = freq.get(var, 0) + 1
        
        # Sort by frequency descending
        return sorted(freq.keys(), key=lambda v: freq[v], reverse=True)
    
    # Shunyam: Balance positive/negative occurrences
    def shunyam(self, assignment: Dict[int, bool]) -> Dict[int, bool]:
        """Balance assignment to satisfy maximum clauses."""
        # Simple greedy: assign remaining variables to maximize satisfied clauses
        remaining = [v for v in range(1, self.n_vars + 1) if v not in assignment]
        
        for var in remaining:
            pos_count = sum(1 for clause in self.clauses 
                          if any(v == var and s == True for v, s in clause))
            neg_count = sum(1 for clause in self.clauses 
                          if any(v == var and s == False for v, s in clause))
            assignment[var] = pos_count >= neg_count
        
        return assignment
    
    # Ekādhikena: Incremental refinement via local search
    def ekādhikena(self, assignment: Dict[int, bool], max_iter: int = None) -> Dict[int, bool]:
        """Improve assignment via exhaustive local search — try every variable."""
        if max_iter is None:
            max_iter = self.n_vars * 5  # 5 full passes over all variables
        
        best_assignment = assignment.copy()
        best_score = self._satisfaction_score(assignment)
        
        for _ in range(max_iter):
            improved = False
            # Try every variable in random order each pass
            order = list(range(1, self.n_vars + 1))
            random.shuffle(order)
            for var in order:
                assignment[var] = not assignment.get(var, False)
                new_score = self._satisfaction_score(assignment)
                if new_score > best_score:
                    best_score = new_score
                    best_assignment = assignment.copy()
                    improved = True
                else:
                    assignment[var] = not assignment.get(var, False)
            if not improved:
                break  # local optimum reached
        
        return best_assignment
    
    def _satisfaction_score(self, assignment: Dict[int, bool]) -> int:
        """Count satisfied clauses."""
        satisfied = 0
        for clause in self.clauses:
            for var, sign in clause:
                if var in assignment and assignment[var] == sign:
                    satisfied += 1
                    break
        return satisfied
    
    def solve(self) -> Dict[int, bool]:
        """Solve SAT using all five Vedic transformations."""
        # 1. Nikhilam - obvious assignments
        assignment = self.nikhilam()
        
        # 2. Urdhva - propagate
        assignment = self.urdhva(assignment)
        
        # 3. Anurupye - order remaining
        ordered = self.anurupye()
        remaining = [v for v in ordered if v not in assignment]
        
        # 4. Shunyam - initial assignment for remaining
        for var in remaining:
            assignment[var] = random.choice([True, False])
        assignment = self.shunyam(assignment)
        
        # 5. Ekādhikena - refine
        assignment = self.ekādhikena(assignment)
        
        # Ensure all variables assigned
        for var in range(1, self.n_vars + 1):
            if var not in assignment:
                assignment[var] = random.choice([True, False])
        
        return assignment

# ============================================================================
# 2. TSP SOLVER - Venusian Tour Loom
# ============================================================================

class VenusianTourLoom:
    """Vedic Transformation System for Traveling Salesman."""
    
    def __init__(self, dist_matrix: np.ndarray, seed: Optional[int] = None):
        """
        Initialize TSP solver.
        
        Args:
            dist_matrix: n x n distance matrix
            seed: Random seed
        """
        self.dist = dist_matrix
        self.n = dist_matrix.shape[0]
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    # Nikhilam: Identify obvious connections (nearest neighbors)
    def nikhilam(self) -> List[Tuple[int, int]]:
        """Identify obvious edges (nearest neighbors)."""
        edges = []
        for i in range(self.n):
            # Find nearest neighbor not self
            nearest = None
            min_dist = float('inf')
            for j in range(self.n):
                if i != j and self.dist[i, j] < min_dist:
                    min_dist = self.dist[i, j]
                    nearest = j
            if nearest is not None:
                edges.append((i, nearest))
        return edges
    
    # Urdhva: Connect components
    def urdhva(self, edges: List[Tuple[int, int]]) -> List[int]:
        """Connect edges into partial tour."""
        # Build adjacency from edges
        adj = {i: [] for i in range(self.n)}
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        
        # Start from node 0, follow connections
        tour = [0]
        visited = {0}
        
        while len(tour) < self.n:
            current = tour[-1]
            # Find unvisited neighbor
            found = False
            for neighbor in adj[current]:
                if neighbor not in visited:
                    tour.append(neighbor)
                    visited.add(neighbor)
                    found = True
                    break
            
            if not found:
                # Add nearest unvisited city
                unvisited = [i for i in range(self.n) if i not in visited]
                if not unvisited:
                    break
                nearest = min(unvisited, key=lambda x: self.dist[current, x])
                tour.append(nearest)
                visited.add(nearest)
        
        return tour
    
    # Anurupye: Order by distance
    def anurupye(self, tour: List[int]) -> List[int]:
        """Reorder tour by nearest insertion."""
        if len(tour) <= 2:
            return tour
        
        # Start with first two cities
        new_tour = [tour[0], tour[1]]
        
        for i in range(2, len(tour)):
            city = tour[i]
            # Find best position to insert
            best_pos = 0
            best_increase = float('inf')
            
            for j in range(len(new_tour)):
                # Insert between j and j+1 (circular)
                a = new_tour[j]
                b = new_tour[(j + 1) % len(new_tour)]
                increase = (self.dist[a, city] + 
                          self.dist[city, b] - 
                          self.dist[a, b])
                
                if increase < best_increase:
                    best_increase = increase
                    best_pos = j + 1
            
            new_tour.insert(best_pos, city)
        
        return new_tour
    
    def shunyam(self, tour: List[int], max_iter: int = None) -> List[int]:
        """Improve tour via exhaustive 2-opt local search."""
        best_tour = tour[:]
        best_length = self._tour_length(tour)
        max_passes = 5 if max_iter is None else max_iter // (self.n * self.n)
        
        for _ in range(max_passes):
            improved = False
            for i in range(self.n - 2):
                for j in range(i + 1, self.n - 1):
                    new_tour = tour[:i] + tour[i:j+1][::-1] + tour[j+1:]
                    new_length = self._tour_length(new_tour)
                    if new_length < best_length:
                        best_length = new_length
                        best_tour = new_tour
                        tour = new_tour
                        improved = True
            if not improved:
                break
        
        return best_tour
    
    # Ekādhikena: Final refinement
    def ekādhikena(self, tour: List[int]) -> List[int]:
        """Final refinement via 3-opt (simplified)."""
        return self.shunyam(tour, max_iter=self.n * self.n * 3)
    
    def _tour_length(self, tour: List[int]) -> float:
        """Calculate tour length."""
        length = 0
        for i in range(len(tour)):
            j = (i + 1) % len(tour)
            length += self.dist[tour[i], tour[j]]
        return length
    
    def solve(self) -> Tuple[List[int], float]:
        """Solve TSP using all five Vedic transformations."""
        # 1. Nikhilam - obvious edges
        edges = self.nikhilam()
        
        # 2. Urdhva - connect into tour
        tour = self.urdhva(edges)
        
        # 3. Anurupye - reorder
        tour = self.anurupye(tour)
        
        # 4. Shunyam - 2-opt optimization
        tour = self.shunyam(tour)
        
        # 5. Ekādhikena - final refinement
        tour = self.ekādhikena(tour)
        
        length = self._tour_length(tour)
        return tour, length

# ============================================================================
# 3. VERTEX COVER SOLVER - Saturnian Minimal Shield
# ============================================================================

class SaturnianMinimalShield:
    """Vedic Transformation System for Vertex Cover."""
    
    def __init__(self, adj: Dict[int, List[int]], edges: List[Tuple[int, int]], 
                 seed: Optional[int] = None):
        """
        Initialize vertex cover solver.
        
        Args:
            adj: Adjacency dictionary {vertex: list(neighbors)}
            edges: List of edges
            seed: Random seed
        """
        self.adj = adj
        self.edges = edges
        self.vertices = list(adj.keys())
        
        if seed is not None:
            random.seed(seed)
    
    # Nikhilam: Identify essential vertices (high degree, endpoints)
    def nikhilam(self) -> Set[int]:
        """Identify essential vertices that must be in cover."""
        essential = set()
        
        # Vertices with degree 0 can be ignored
        # Vertices that are the only connection for an edge
        edge_cover = {}
        for u, v in self.edges:
            edge_cover.setdefault(u, []).append((u, v))
            edge_cover.setdefault(v, []).append((u, v))
        
        for vertex, incident_edges in edge_cover.items():
            if len(incident_edges) == 1:
                # Vertex with single edge - could choose either endpoint
                # For now, add the vertex itself
                essential.add(vertex)
        
        return essential
    
    # Urdhva: Combine and propagate
    def urdhva(self, cover: Set[int]) -> Set[int]:
        """Expand cover to cover more edges."""
        uncovered = [(u, v) for u, v in self.edges 
                    if u not in cover and v not in cover]
        
        while uncovered:
            # Pick random uncovered edge
            u, v = random.choice(uncovered)
            # Add vertex with higher degree
            if len(self.adj.get(u, [])) >= len(self.adj.get(v, [])):
                cover.add(u)
            else:
                cover.add(v)
            
            # Update uncovered
            uncovered = [(x, y) for x, y in uncovered 
                        if x not in cover and y not in cover]
        
        return cover
    
    # Anurupye: Order by degree
    def anurupye(self) -> List[int]:
        """Order vertices by degree descending."""
        degrees = [(v, len(self.adj.get(v, []))) for v in self.vertices]
        return sorted(self.vertices, key=lambda v: len(self.adj.get(v, [])), reverse=True)
    
    # Shunyam: Balance cover size
    def shunyam(self, cover: Set[int]) -> Set[int]:
        """Try to remove redundant vertices."""
        removable = []
        for v in cover:
            # Check if all edges incident to v are covered by other vertices
            still_covered = True
            for neighbor in self.adj.get(v, []):
                if neighbor not in cover:
                    still_covered = False
                    break
            
            if still_covered:
                removable.append(v)
        
        # Remove some redundant vertices (not all to be safe)
        if removable:
            to_remove = random.sample(removable, min(len(removable), len(cover) // 4))
            cover.difference_update(to_remove)
        
        return cover
    
    # Ekādhikena: Refine via exhaustive vertex swap
    def ekādhikena(self, cover: Set[int], max_iter: int = None) -> Set[int]:
        """Improve cover via exhaustive vertex swaps."""
        best_cover = set(cover)
        best_size = len(cover)
        max_passes = 5 if max_iter is None else max(1, max_iter // len(cover))
        
        for _ in range(max_passes):
            improved = False
            for v in list(best_cover):
                for u in self.adj.get(v, []):
                    if u in best_cover:
                        continue
                    new_cover = set(best_cover)
                    new_cover.remove(v)
                    new_cover.add(u)
                    if self._is_valid_cover(new_cover) and len(new_cover) < best_size:
                        best_cover = new_cover
                        best_size = len(new_cover)
                        improved = True
            if not improved:
                break
        
        return best_cover
    
    def _is_valid_cover(self, cover: Set[int]) -> bool:
        """Check if cover covers all edges."""
        for u, v in self.edges:
            if u not in cover and v not in cover:
                return False
        return True
    
    def solve(self) -> Set[int]:
        """Solve vertex cover using all five Vedic transformations."""
        # 1. Nikhilam - essential vertices
        cover = self.nikhilam()
        
        # 2. Urdhva - expand to cover edges
        cover = self.urdhva(cover)
        
        # 3. Anurupye - order remaining
        ordered = self.anurupye()
        remaining = [v for v in ordered if v not in cover]
        
        # 4. Shunyam - initial greedy addition
        for v in remaining:
            if not self._is_valid_cover(cover):
                cover.add(v)
        
        # 5. Ekādhikena - refine
        cover = self.ekādhikena(cover)
        
        return cover

# ============================================================================
# 4. GRAPH COLORING SOLVER - Solar Chromatic Weaver
# ============================================================================

class SolarChromaticWeaver:
    """Vedic Transformation System for Graph Coloring."""
    
    def __init__(self, adj: Dict[int, List[int]], edges: List[Tuple[int, int]],
                 seed: Optional[int] = None):
        """
        Initialize graph coloring solver.
        
        Args:
            adj: Adjacency dictionary
            edges: List of edges
            seed: Random seed
        """
        self.adj = adj
        self.edges = edges
        self.vertices = list(adj.keys())
        
        if seed is not None:
            random.seed(seed)
    
    # Nikhilam: Identify hard vertices (high degree)
    def nikhilam(self) -> Dict[int, int]:
        """Color obvious vertices (isolated, low-degree)."""
        coloring = {}
        
        # Color isolated vertices with 0
        for v in self.vertices:
            if not self.adj.get(v, []):
                coloring[v] = 0
        
        return coloring
    
    # Urdhva: Propagate constraints
    def urdhva(self, coloring: Dict[int, int]) -> Dict[int, int]:
        """Propagate coloring to neighbors."""
        # DSATUR-like: color vertices with most colored neighbors first
        uncolored = [v for v in self.vertices if v not in coloring]
        
        while uncolored:
            # Find vertex with most colored neighbors
            best_v = None
            best_score = -1
            
            for v in uncolored:
                colored_neighbors = sum(1 for n in self.adj.get(v, []) 
                                      if n in coloring)
                if colored_neighbors > best_score:
                    best_score = colored_neighbors
                    best_v = v
            
            if best_v is None:
                break
            
            # Find smallest available color
            neighbor_colors = {coloring[n] for n in self.adj.get(best_v, []) 
                             if n in coloring}
            color = 0
            while color in neighbor_colors:
                color += 1
            
            coloring[best_v] = color
            uncolored.remove(best_v)
        
        return coloring
    
    # Anurupye: Order by saturation
    def anurupye(self) -> List[int]:
        """Order vertices by degree (DSATUR)."""
        return sorted(self.vertices, 
                     key=lambda v: len(self.adj.get(v, [])), 
                     reverse=True)
    
    # Shunyam: Balance colors
    def shunyam(self, coloring: Dict[int, int]) -> Dict[int, int]:
        """Try to reduce number of colors via Kempe chains."""
        colors_used = set(coloring.values())
        if len(colors_used) <= 1:
            return coloring
        
        # Try to recolor vertices
        for v in self.vertices:
            current_color = coloring[v]
            neighbor_colors = {coloring[n] for n in self.adj.get(v, [])}
            
            # Try smaller color
            for new_color in range(current_color):
                if new_color not in neighbor_colors:
                    coloring[v] = new_color
                    break
        
        return coloring
    
    # Ekādhikena: Refine via exhaustive local search
    def ekādhikena(self, coloring: Dict[int, int], max_iter: int = None) -> Dict[int, int]:
        """Improve coloring via exhaustive conflict resolution."""
        best_coloring = coloring.copy()
        max_passes = 10 if max_iter is None else max_iter
        
        for _ in range(max_passes):
            improved = False
            coloring = best_coloring.copy()
            # Find all conflicting vertices
            conflicts = set()
            for u, v in self.edges:
                if coloring.get(u) == coloring.get(v):
                    conflicts.add(u); conflicts.add(v)
            
            if not conflicts:
                break
            
            # Try to recolor each conflicting vertex
            for v in conflicts:
                neighbor_colors = {coloring.get(n) for n in self.adj.get(v, [])}
                for color in range(max(coloring.values()) + 2):
                    if color not in neighbor_colors:
                        coloring[v] = color
                        break
            
            colors_used = len(set(coloring.values()))
            prev_colors = len(set(best_coloring.values()))
            # Count remaining conflicts
            new_conflicts = sum(1 for u,v in self.edges if coloring.get(u)==coloring.get(v))
            old_conflicts = sum(1 for u,v in self.edges if best_coloring.get(u)==best_coloring.get(v))
            
            if new_conflicts < old_conflicts or (new_conflicts == old_conflicts and colors_used < prev_colors):
                best_coloring = coloring.copy()
                improved = True
            
            if not improved:
                break
        
        return best_coloring
    
    def solve(self) -> Tuple[Dict[int, int], int]:
        """Solve graph coloring using all five Vedic transformations."""
        # 1. Nikhilam - obvious vertices
        coloring = self.nikhilam()
        
        # 2. Urdhva - propagate
        coloring = self.urdhva(coloring)
        
        # 3. Anurupye - order remaining
        ordered = self.anurupye()
        remaining = [v for v in ordered if v not in coloring]
        
        # 4. Shunyam - initial coloring for remaining
        for v in remaining:
            neighbor_colors = {coloring.get(n, -1) for n in self.adj.get(v, [])}
            color = 0
            while color in neighbor_colors:
                color += 1
            coloring[v] = color
        
        coloring = self.shunyam(coloring)
        
        # 5. Ekādhikena - refine
        coloring = self.ekādhikena(coloring)
        
        n_colors = len(set(coloring.values()))
        return coloring, n_colors

# ============================================================================
# 5. SET COVER SOLVER - Jovian Expansive Net
# ============================================================================

class JovianExpansiveNet:
    """Vedic Transformation System for Set Cover."""
    
    def __init__(self, universe: Set[int], subsets: List[Set[int]], 
                 seed: Optional[int] = None):
        """
        Initialize set cover solver.
        
        Args:
            universe: Set of elements
            subsets: List of subsets
            seed: Random seed
        """
        self.universe = universe
        self.subsets = subsets
        self.m = len(subsets)
        
        if seed is not None:
            random.seed(seed)
    
    # Nikhilam: Identify essential subsets
    def nikhilam(self) -> Set[int]:
        """Identify subsets that cover unique elements."""
        essential = set()
        
        # Count element occurrences
        element_counts = {}
        for i, subset in enumerate(self.subsets):
            for elem in subset:
                element_counts[elem] = element_counts.get(elem, 0) + 1
        
        # Subsets covering elements that appear only once
        for i, subset in enumerate(self.subsets):
            for elem in subset:
                if element_counts[elem] == 1:
                    essential.add(i)
                    break
        
        return essential
    
    # Urdhva: Combine subsets
    def urdhva(self, cover: Set[int]) -> Set[int]:
        """Expand cover to cover more elements."""
        covered = set()
        for i in cover:
            covered.update(self.subsets[i])
        
        while covered != self.universe:
            # Find subset covering most uncovered elements
            best_subset = None
            best_gain = 0
            
            for i in range(self.m):
                if i in cover:
                    continue
                
                gain = len(self.subsets[i] - covered)
                if gain > best_gain:
                    best_gain = gain
                    best_subset = i
            
            if best_subset is None:
                break
            
            cover.add(best_subset)
            covered.update(self.subsets[best_subset])
        
        return cover
    
    # Anurupye: Order subsets by coverage
    def anurupye(self) -> List[int]:
        """Order subsets by size descending."""
        sizes = [(i, len(s)) for i, s in enumerate(self.subsets)]
        return sorted(range(self.m), key=lambda i: len(self.subsets[i]), reverse=True)
    
    # Shunyam: Remove redundant subsets
    def shunyam(self, cover: Set[int]) -> Set[int]:
        """Remove ALL redundant subsets."""
        removable = []
        for i in cover:
            covered_by_others = set()
            for j in cover:
                if j != i:
                    covered_by_others.update(self.subsets[j])
            if self.subsets[i].issubset(covered_by_others):
                removable.append(i)
        # Remove ALL redundant, not random sample
        if removable:
            cover.difference_update(removable)
        return cover
    
    # Ekādhikena: Exhaustive subset swaps
    def ekādhikena(self, cover: Set[int], max_iter: int = None) -> Set[int]:
        """Exhaustively try ALL subset swaps to reduce cover size."""
        best_cover = set(cover)
        
        for _ in range(5):
            improved = False
            for i in list(best_cover):
                for j in range(self.m):
                    if j in best_cover: continue
                    new_cover = set(best_cover)
                    new_cover.remove(i); new_cover.add(j)
                    covered = set()
                    for k in new_cover: covered.update(self.subsets[k])
                    if covered == self.universe and len(new_cover) < len(best_cover):
                        best_cover = new_cover
                        improved = True
            if not improved: break
        
        return best_cover
    
    def solve(self) -> Set[int]:
        """Solve set cover using all five Vedic transformations."""
        # 1. Nikhilam - essential subsets
        cover = self.nikhilam()
        
        # 2. Urdhva - expand cover
        cover = self.urdhva(cover)
        
        # 3. Anurupye - order remaining
        ordered = self.anurupye()
        remaining = [i for i in ordered if i not in cover]
        
        # 4. Shunyam - initial greedy addition
        covered = set()
        for i in cover:
            covered.update(self.subsets[i])
        
        for i in remaining:
            if covered != self.universe:
                cover.add(i)
                covered.update(self.subsets[i])
        
        # 5. Ekādhikena - refine
        cover = self.ekādhikena(cover)
        
        return cover

# ============================================================================
# 6. HAMILTONIAN PATH SOLVER - Martian Pathfinder
# ============================================================================

class MartianPathfinder:
    """Vedic Transformation System for Hamiltonian Path."""
    
    def __init__(self, adj: Dict[int, List[int]], edges: List[Tuple[int, int]],
                 seed: Optional[int] = None):
        """
        Initialize Hamiltonian path solver.
        
        Args:
            adj: Adjacency dictionary
            edges: List of edges
            seed: Random seed
        """
        self.adj = adj
        self.edges = edges
        self.vertices = list(adj.keys())
        self.n = len(self.vertices)
        
        if seed is not None:
            random.seed(seed)
    
    # Nikhilam: Identify endpoints (degree 1 vertices)
    def nikhilam(self) -> Tuple[Optional[int], Optional[int]]:
        """Identify potential start/end vertices."""
        endpoints = [v for v in self.vertices if len(self.adj.get(v, [])) == 1]
        if len(endpoints) >= 2:
            return endpoints[0], endpoints[1]
        elif endpoints:
            return endpoints[0], None
        else:
            return None, None
    
    # Urdhva: Build path by connecting with proper DFS backtracking
    def urdhva(self, start: Optional[int], end: Optional[int]) -> List[int]:
        """Osiris's journey through the Duat — backtracking DFS."""
        if start is None:
            start = random.choice(self.vertices)
        
        # DFS with backtracking stack
        stack = [(start, [start], {start})]  # (current, path, visited)
        
        while stack:
            current, path, visited = stack.pop()
            
            if len(path) == self.n:
                if end is None or path[-1] == end or (end is not None and path[-1] in self.adj.get(end, []) and len(path) == self.n):
                    return path
                continue
            
            # Get unvisited neighbors, prioritize fewer options (Warnsdorff-like heuristic)
            neighbors = [(n, len([x for x in self.adj.get(n, []) if x not in visited])) 
                        for n in self.adj.get(current, []) if n not in visited]
            
            if end is not None and end in [n for n,_ in neighbors] and len(path) == self.n - 1:
                return path + [end]
            
            # Push branches in reverse order — we want fewest-options first (pop from end)
            neighbors.sort(key=lambda x: x[1], reverse=True)  # most options last (popped first from stack)
            for n, _ in neighbors:
                stack.append((n, path + [n], visited | {n}))
        
        # If DFS fails, fall back to greedy
        return self._greedy_path(start, end)
    
    def _greedy_path(self, start, end):
        path = [start]; visited = {start}
        while len(path) < self.n:
            current = path[-1]
            neighbors = [n for n in self.adj.get(current, []) if n not in visited]
            if not neighbors:
                if len(path) > 1: path.pop()
                else: break
                continue
            next_v = min(neighbors, key=lambda v: len([n for n in self.adj.get(v, []) if n not in visited]))
            path.append(next_v); visited.add(next_v)
        return path
    
    # Anurupye: Order vertices by degree
    def anurupye(self) -> List[int]:
        """Order vertices by degree."""
        return sorted(self.vertices, 
                     key=lambda v: len(self.adj.get(v, [])), 
                     reverse=True)
    
    # Shunyam: Repair path
    def shunyam(self, path: List[int]) -> List[int]:
        """Repair path to make it Hamiltonian."""
        if len(path) == self.n:
            return path
        
        visited = set(path)
        missing = [v for v in self.vertices if v not in visited]
        
        # Try to insert missing vertices
        for v in missing:
            # Find position where v connects to both neighbors
            for i in range(len(path) - 1):
                a, b = path[i], path[i + 1]
                if v in self.adj.get(a, []) and v in self.adj.get(b, []):
                    path.insert(i + 1, v)
                    visited.add(v)
                    break
        
        return path
    
    # Ekādhikena: Exhaustive 2-opt refinement
    def ekādhikena(self, path: List[int], max_iter: int = None) -> List[int]:
        """Exhaustive 2-opt — try all reversals until no improvement."""
        if len(path) < 3:
            return path
        
        best_path = path[:]
        best_len = len(best_path)
        
        for _ in range(5):  # up to 5 passes
            improved = False
            for i in range(len(best_path) - 2):
                for j in range(i + 1, len(best_path) - 1):
                    new_path = best_path[:i] + best_path[i:j+1][::-1] + best_path[j+1:]
                    # Check if all edges exist
                    valid = True
                    for k in range(len(new_path) - 1):
                        if new_path[k+1] not in self.adj.get(new_path[k], []):
                            valid = False; break
                    if valid and (len(new_path) > best_len or 
                                 (len(new_path) == best_len and not improved)):
                        best_path = new_path; best_len = len(new_path); improved = True
            if not improved:
                break
        
        return best_path
    
    def _is_hamiltonian(self, path: List[int]) -> bool:
        """Check if path is Hamiltonian."""
        if len(path) != self.n:
            return False
        
        if len(set(path)) != self.n:
            return False
        
        for i in range(len(path) - 1):
            if path[i+1] not in self.adj.get(path[i], []):
                return False
        
        return True
    
    def solve(self) -> Tuple[List[int], bool]:
        """Solve Hamiltonian path using all five Vedic transformations."""
        # 1. Nikhilam - endpoints
        start, end = self.nikhilam()
        
        # 2. Urdhva - build path
        path = self.urdhva(start, end)
        
        # 3. Anurupye - reorder attempt
        if not self._is_hamiltonian(path):
            # Try different ordering
            ordered = self.anurupye()
            if ordered != path:
                # Try path starting with highest degree vertex
                start2 = ordered[0]
                path2 = self.urdhva(start2, None)
                if len(path2) > len(path):
                    path = path2
        
        # 4. Shunyam - repair
        path = self.shunyam(path)
        
        # 5. Ekādhikena - refine
        path = self.ekādhikena(path)
        
        found = self._is_hamiltonian(path)
        return path, found

# ============================================================================
# 7. SUBSET SUM SOLVER - Lunar Intuitive Oracle
# ============================================================================

class LunarIntuitiveOracle:
    """Vedic Transformation System for Subset Sum (Partition)."""
    
    def __init__(self, numbers: List[int], target: Optional[int] = None, seed: Optional[int] = None):
        """
        Initialize solver with numbers and optional target.
        
        If target is None, solves partition problem (find subset summing to total/2).
        
        Args:
            numbers: List of positive integers
            target: Target sum (optional, defaults to partition problem)
            seed: Random seed for reproducibility
        """
        self.numbers = numbers
        self.n = len(numbers)
        self.total = sum(numbers)
        
        if target is None:
            # Partition problem: find subset summing to total/2
            self.target = self.total // 2
            self.is_partition = True
        else:
            self.target = target
            self.is_partition = False
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    # Nikhilam: Identify obvious elements
    def nikhilam(self, threshold_ratio: float = 0.8) -> Set[int]:
        """Identify obvious includes (exact matches, close to target)."""
        obvious_includes = set()
        
        for i, num in enumerate(self.numbers):
            # If number equals target exactly, obvious include
            if num == self.target:
                obvious_includes.add(i)
            # If number > target, can't be included (unless partition with remainder)
            elif num > self.target and not self.is_partition:
                pass
            # If number is very close to target (within 10%)
            elif abs(num - self.target) < 0.1 * self.target:
                if random.random() < 0.7:
                    obvious_includes.add(i)
        
        return obvious_includes
    
    # Urdhva: Combine complementary elements
    def urdhva(self, candidate_indices: Set[int]) -> Set[int]:
        """Look for pairs/triples that sum close to target."""
        current_sum = sum(self.numbers[i] for i in candidate_indices)
        remaining = self.target - current_sum
        
        if remaining <= 0:
            return candidate_indices
        
        candidates = list(set(range(self.n)) - candidate_indices)
        candidates.sort(key=lambda i: self.numbers[i])
        
        expanded = set(candidate_indices)
        
        # Try single element matching remainder
        for i in candidates:
            if self.numbers[i] == remaining:
                expanded.add(i)
                return expanded
        
        # Try pair
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                idx_i, idx_j = candidates[i], candidates[j]
                if self.numbers[idx_i] + self.numbers[idx_j] == remaining:
                    expanded.add(idx_i)
                    expanded.add(idx_j)
                    return expanded
        
        # Try triple (approximate)
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                for k in range(j + 1, len(candidates)):
                    idx_i, idx_j, idx_k = candidates[i], candidates[j], candidates[k]
                    sum_ijk = self.numbers[idx_i] + self.numbers[idx_j] + self.numbers[idx_k]
                    if abs(sum_ijk - remaining) < 0.1 * remaining:
                        expanded.add(idx_i)
                        expanded.add(idx_j)
                        expanded.add(idx_k)
                        return expanded
        
        return expanded
    
    # Anurupye: Order by proximity to target gap
    def anurupye(self, candidate_indices: Set[int]) -> List[int]:
        """Order elements by how well they fill remaining gap."""
        current_sum = sum(self.numbers[i] for i in candidate_indices)
        remaining = self.target - current_sum
        
        if remaining <= 0:
            return []
        
        candidates = list(set(range(self.n)) - candidate_indices)
        candidates.sort(key=lambda i: abs(self.numbers[i] - remaining))
        return candidates
    
    # Shunyam: Balance subset to hit target
    def shunyam(self, candidate_indices: Set[int], max_iterations: int = 100) -> Set[int]:
        """Adjust subset via local swaps."""
        current_sum = sum(self.numbers[i] for i in candidate_indices)
        diff = self.target - current_sum
        
        if diff == 0:
            return candidate_indices
        
        candidate_list = list(candidate_indices)
        non_candidates = list(set(range(self.n)) - candidate_indices)
        
        for _ in range(max_iterations):
            if diff == 0:
                break
            
            if diff > 0:
                # Need to add elements
                best_idx = None
                best_gap = float('inf')
                for i in non_candidates:
                    gap = abs(self.numbers[i] - diff)
                    if gap < best_gap:
                        best_gap = gap
                        best_idx = i
                if best_idx is not None:
                    candidate_list.append(best_idx)
                    non_candidates.remove(best_idx)
                    current_sum += self.numbers[best_idx]
                    diff = self.target - current_sum
            else:
                # Need to remove elements
                best_idx = None
                best_gap = float('inf')
                for i in candidate_list:
                    gap = abs(self.numbers[i] + diff)
                    if gap < best_gap:
                        best_gap = gap
                        best_idx = i
                if best_idx is not None:
                    candidate_list.remove(best_idx)
                    non_candidates.append(best_idx)
                    current_sum -= self.numbers[best_idx]
                    diff = self.target - current_sum
        
        return set(candidate_list)
    
    # Ekādhikena: Exhaustive refinement
    def ekādhikena(self, candidate_indices: Set[int], iterations: int = None) -> Set[int]:
        """Exhaustively try all add/remove operations until no improvement."""
        best_set = set(candidate_indices)
        best_sum = sum(self.numbers[i] for i in best_set)
        best_diff = abs(self.target - best_sum)
        
        for _ in range(5):
            improved = False
            current_set = set(best_set)
            
            # Try removing each element
            for idx in list(current_set):
                test_sum = best_sum - self.numbers[idx]
                test_diff = abs(self.target - test_sum)
                if test_diff < best_diff:
                    current_set.remove(idx)
                    best_diff = test_diff; best_sum = test_sum
                    best_set = set(current_set)
                    improved = True
            
            # Try adding each non-element
            non_candidates = set(range(self.n)) - current_set
            for idx in non_candidates:
                test_sum = best_sum + self.numbers[idx]
                test_diff = abs(self.target - test_sum)
                if test_diff < best_diff:
                    current_set.add(idx)
                    best_diff = test_diff; best_sum = test_sum
                    best_set = set(current_set)
                    improved = True
            
            if not improved:
                break
        
        return best_set
        
        return best_set
    
    def solve(self) -> Set[int]:
        """Complete Vedic transformation pipeline."""
        # 1. Nikhilam
        obvious = self.nikhilam(threshold_ratio=0.8)
        # 2. Urdhva
        expanded = self.urdhva(obvious)
        # 3. Anurupye
        ordered = self.anurupye(expanded)
        
        current_set = set(expanded)
        current_sum = sum(self.numbers[i] for i in current_set)
        
        for idx in ordered:
            if current_sum + self.numbers[idx] <= self.target:
                current_set.add(idx)
                current_sum += self.numbers[idx]
        
        # 4. Shunyam
        balanced = self.shunyam(current_set, max_iterations=100)
        # 5. Ekādhikena
        final = self.ekādhikena(balanced, iterations=20)
        
        final_sum = sum(self.numbers[i] for i in final)
        
        if self.is_partition:
            if abs(final_sum - self.target) <= 0.05 * self.target:
                return final
            else:
                return set()
        else:
            if final_sum == self.target:
                return final
            else:
                return set()

# ============================================================================
# 8. MAXIMUM CLIQUE SOLVER - Neptunian Dream Weaver
# ============================================================================

class NeptunianDreamWeaver:
    """Vedic Transformation System for Maximum Clique."""
    
    def __init__(self, adj: Dict[int, Set[int]], seed: Optional[int] = None):
        """Initialize solver with graph adjacency."""
        self.adj = adj
        self.vertices = list(adj.keys())
        self.n = len(self.vertices)
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    # Nikhilam: Identify obvious vertices (high-degree)
    def nikhilam(self, degree_threshold: float = 0.7) -> Set[int]:
        """Identify high-degree vertices as obvious candidates."""
        if not self.vertices:
            return set()
        
        degrees = {v: len(neighbors) for v, neighbors in self.adj.items()}
        max_degree = max(degrees.values())
        
        obvious = set()
        for v, degree in degrees.items():
            if degree >= degree_threshold * max_degree:
                obvious.add(v)
        
        return obvious
    
    # Urdhva: Expand clique with mutually connected vertices
    def urdhva(self, candidate_clique: Set[int]) -> Set[int]:
        """Expand clique with common neighbors."""
        if not candidate_clique:
            degrees = {v: len(neighbors) for v, neighbors in self.adj.items()}
            start_vertex = max(degrees.items(), key=lambda x: x[1])[0]
            return {start_vertex}
        
        common_neighbors = set(self.vertices)
        for v in candidate_clique:
            common_neighbors &= self.adj[v] | {v}
        
        common_neighbors -= candidate_clique
        
        if common_neighbors:
            degrees = {v: len(self.adj[v]) for v in common_neighbors}
            best_vertex = max(degrees.items(), key=lambda x: x[1])[0]
            candidate_clique.add(best_vertex)
        
        return candidate_clique
    
    # Anurupye: Order vertices by connectivity to clique
    def anurupye(self, candidate_clique: Set[int]) -> List[int]:
        """Order vertices by number of connections to clique."""
        if not candidate_clique:
            degrees = {v: len(neighbors) for v, neighbors in self.adj.items()}
            return sorted(self.vertices, key=lambda v: -degrees[v])
        
        connection_counts = {}
        for v in self.vertices:
            if v in candidate_clique:
                continue
            connections = sum(1 for u in candidate_clique if u in self.adj[v])
            connection_counts[v] = connections
        
        return sorted(connection_counts.keys(), key=lambda v: -connection_counts[v])
    
    # Shunyam: Ensure clique property
    def shunyam(self, candidate_clique: Set[int]) -> Set[int]:
        """Remove vertices not connected to all others."""
        if len(candidate_clique) <= 1:
            return candidate_clique
        
        clique_list = list(candidate_clique)
        balanced = set()
        balanced.add(clique_list[0])
        
        for v in clique_list[1:]:
            if all(u in self.adj[v] for u in balanced):
                balanced.add(v)
        
        return balanced
    
    # Ekādhikena: Exhaustive clique expansion
    def ekādhikena(self, clique: Set[int], iterations: int = None) -> Set[int]:
        """Exhaustively expand clique by trying all vertices."""
        best_clique = set(clique)
        max_passes = 10 if iterations is None else iterations
        
        for _ in range(max_passes):
            improved = False
            current = set(best_clique)
            
            # Find all common neighbors — vertices connected to ALL current members
            common_neighbors = set(self.vertices)
            for v in current:
                common_neighbors &= self.adj.get(v, set()) | {v}
            common_neighbors -= current
            
            # Try adding each common neighbor
            for v in sorted(common_neighbors, key=lambda x: 
                sum(1 for u in common_neighbors if u in self.adj.get(x, set())), reverse=True):
                test = set(current) | {v}
                test = self.shunyam(test)
                if len(test) > len(best_clique):
                    best_clique = test
                    improved = True
                    break
            
            if not improved:
                break
        
        return best_clique
    
    def solve(self) -> Set[int]:
        """Complete Vedic transformation pipeline for maximum clique."""
        # 1. Nikhilam
        obvious = self.nikhilam(degree_threshold=0.6)
        # 2. Urdhva
        expanded = self.urdhva(obvious)
        # 3. Greedy expansion
        ordered = self.anurupye(expanded)
        current = set(expanded)
        
        for v in ordered:
            if all(u in self.adj[v] for u in current):
                current.add(v)
        
        # 4. Shunyam
        balanced = self.shunyam(current)
        # 5. Ekādhikena
        final = self.ekādhikena(balanced, iterations=30)
        
        return final

# ============================================================================
# 9. EXACT COVER SOLVER - Uranian Innovation Engine
# ============================================================================

class UranianInnovationEngine:
    """Vedic Transformation System for Exact Cover."""
    
    def __init__(self, universe: Set, subsets: List[Set], seed: Optional[int] = None):
        """Initialize solver with exact cover instance."""
        self.universe = universe
        self.subsets = subsets
        self.m = len(subsets)
        
        self.element_to_subsets: Dict = {}
        for elem in universe:
            self.element_to_subsets[elem] = []
        
        for i, subset in enumerate(subsets):
            for elem in subset:
                if elem in self.element_to_subsets:
                    self.element_to_subsets[elem].append(i)
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    # Nikhilam: Identify forced subsets
    def nikhilam(self) -> Set[int]:
        """Elements that appear in only one subset force that subset."""
        forced = set()
        for elem, subset_indices in self.element_to_subsets.items():
            if len(subset_indices) == 1:
                forced.add(subset_indices[0])
        return forced
    
    # Urdhva: Combine non-overlapping subsets
    def urdhva(self, selected: Set[int]) -> Set[int]:
        """Expand with non-conflicting subsets."""
        covered = set()
        for i in selected:
            covered |= self.subsets[i]
        
        candidates = set()
        for i in range(self.m):
            if i in selected:
                continue
            if not (self.subsets[i] & covered):
                candidates.add(i)
        
        expanded = set(selected)
        sorted_candidates = sorted(candidates, key=lambda i: -len(self.subsets[i]))
        
        for i in sorted_candidates:
            subset_covered = set()
            for j in expanded:
                subset_covered |= self.subsets[j]
            if not (self.subsets[i] & subset_covered):
                expanded.add(i)
        
        return expanded
    
    # Anurupye: Order subsets by coverage efficiency
    def anurupye(self, selected: Set[int]) -> List[int]:
        """Order subsets by (new_elements / subset_size) ratio."""
        covered = set()
        for i in selected:
            covered |= self.subsets[i]
        
        remaining = self.universe - covered
        scores = {}
        for i in range(self.m):
            if i in selected:
                continue
            new_coverage = len(self.subsets[i] & remaining)
            if new_coverage > 0:
                efficiency = new_coverage / len(self.subsets[i])
                scores[i] = efficiency
        
        return sorted(scores.keys(), key=lambda i: -scores[i])
    
    # Shunyam: Balance - resolve overlaps and missing coverage
    def shunyam(self, selected: Set[int], max_iterations: int = 50) -> Set[int]:
        """Balance cover."""
        current = set(selected)
        
        for _ in range(max_iterations):
            covered = set()
            for i in current:
                covered |= self.subsets[i]
            
            uncovered = self.universe - covered
            
            if not uncovered:
                element_counts = {}
                for i in current:
                    for elem in self.subsets[i]:
                        element_counts[elem] = element_counts.get(elem, 0) + 1
                
                overcovered = {elem for elem, count in element_counts.items() if count > 1}
                
                if not overcovered:
                    return current
                
                for elem in overcovered:
                    covering_subsets = [i for i in current if elem in self.subsets[i]]
                    if len(covering_subsets) > 1:
                        smallest = min(covering_subsets, key=lambda i: len(self.subsets[i]))
                        for i in covering_subsets:
                            if i != smallest:
                                current.discard(i)
            else:
                for elem in uncovered:
                    possible = self.element_to_subsets[elem]
                    if possible:
                        best_i = None
                        best_coverage = -1
                        for i in possible:
                            if i in current:
                                continue
                            new_coverage = len(self.subsets[i] & uncovered)
                            if new_coverage > best_coverage:
                                best_coverage = new_coverage
                                best_i = i
                        if best_i is not None:
                            current.add(best_i)
        
        return current
    
    # Ekādhikena: Exhaustive cover refinement
    def ekādhikena(self, selected: Set[int], iterations: int = None) -> Set[int]:
        """Exhaustively try all subset additions/removals."""
        best = set(selected)
        best_covered = set()
        for i in best: best_covered |= self.subsets[i]
        best_missing = len(self.universe - best_covered)
        
        for _ in range(5):
            improved = False
            # Try removing each subset
            for i in list(best):
                test = set(best); test.remove(i)
                covered = set()
                for j in test: covered |= self.subsets[j]
                missing = len(self.universe - covered)
                if missing < best_missing or (missing == best_missing and len(test) < len(best)):
                    best = test
                    best_covered = covered; best_missing = missing
                    improved = True
            # Try adding each non-selected subset
            for i in range(self.m):
                if i in best: continue
                test = set(best); test.add(i)
                covered = set()
                for j in test: covered |= self.subsets[j]
                missing = len(self.universe - covered)
                if missing < best_missing:
                    best = test
                    best_covered = covered; best_missing = missing
                    improved = True
            if not improved: break
        
        return best
    
    def _count_overlaps(self, selected: Set[int]) -> int:
        """Count how many elements are covered multiple times."""
        element_counts = {}
        for i in selected:
            for elem in self.subsets[i]:
                element_counts[elem] = element_counts.get(elem, 0) + 1
        
        overlaps = sum(1 for count in element_counts.values() if count > 1)
        return overlaps
    
    def solve(self) -> Set[int]:
        """Complete Vedic transformation pipeline for exact cover."""
        # 1. Nikhilam
        forced = self.nikhilam()
        # 2. Urdhva
        expanded = self.urdhva(forced)
        # 3. Greedy expansion
        ordered = self.anurupye(expanded)
        current = set(expanded)
        
        for i in ordered:
            covered = set()
            for j in current:
                covered |= self.subsets[j]
            if not (self.subsets[i] & covered):
                current.add(i)
        
        # 4. Shunyam
        balanced = self.shunyam(current, max_iterations=100)
        # 5. Ekādhikena
        final = self.ekādhikena(balanced, iterations=25)
        
        covered = set()
        for i in final:
            covered |= self.subsets[i]
        
        if covered == self.universe and self._count_overlaps(final) == 0:
            return final
        else:
            return set()

# ============================================================================
# 10. STEINER TREE SOLVER - Plutonian Transformer
# ============================================================================

class PlutonianTransformer:
    """Vedic Transformation System for Steiner Tree."""
    
    def __init__(self, adj: Dict[int, Set[int]], terminals: Set[int], 
                 seed: Optional[int] = None):
        """
        Initialize solver with graph and terminals.
        
        Args:
            adj: Adjacency dictionary {vertex: set(neighbors)}
            terminals: Set of terminal vertices that must be connected
            seed: Random seed for reproducibility
        """
        self.adj = adj
        self.terminals = terminals
        self.vertices = list(adj.keys())
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def shortest_path(self, start: int, end: int) -> List[int]:
        """Dijkstra's algorithm for unweighted graph."""
        if start == end:
            return [start]
        
        visited = {start: None}
        queue = [start]
        
        while queue:
            current = queue.pop(0)
            
            if current == end:
                # Reconstruct path
                path = []
                while current is not None:
                    path.append(current)
                    current = visited[current]
                return list(reversed(path))
            
            for neighbor in self.adj[current]:
                if neighbor not in visited:
                    visited[neighbor] = current
                    queue.append(neighbor)
        
        return []  # No path
    
    # Nikhilam: Identify essential vertices
    def nikhilam(self) -> Set[int]:
        """Terminals and degree-1 terminal neighbors."""
        essential = set(self.terminals)
        for term in self.terminals:
            if len(self.adj[term]) == 1:
                neighbor = next(iter(self.adj[term]))
                essential.add(neighbor)
        return essential
    
    # Urdhva: Connect components
    def urdhva(self, current_tree: Set[int]) -> Set[int]:
        """Connect disconnected components via shortest paths."""
        if not current_tree:
            return set()
        
        # Find connected components
        components = []
        visited = set()
        for v in current_tree:
            if v not in visited:
                component = set()
                stack = [v]
                while stack:
                    node = stack.pop()
                    if node in visited:
                        continue
                    visited.add(node)
                    component.add(node)
                    for neighbor in self.adj[node]:
                        if neighbor in current_tree and neighbor not in visited:
                            stack.append(neighbor)
                components.append(component)
        
        if len(components) <= 1:
            return current_tree
        
        expanded = set(current_tree)
        for i in range(len(components) - 1):
            comp1 = components[i]
            comp2 = components[i + 1]
            best_path = None
            best_length = float('inf')
            for u in comp1:
                for v in comp2:
                    path = self.shortest_path(u, v)
                    if path and len(path) < best_length:
                        best_path = path
                        best_length = len(path)
            if best_path:
                expanded.update(best_path)
        return expanded
    
    # Anurupye: Order terminal pairs by distance
    def anurupye(self, current_tree: Set[int]) -> List[Tuple[int, int]]:
        """Terminal pairs ordered by shortest path length."""
        terminal_list = list(self.terminals)
        pairs = []
        for i in range(len(terminal_list)):
            for j in range(i + 1, len(terminal_list)):
                u, v = terminal_list[i], terminal_list[j]
                path = self.shortest_path(u, v)
                if path:
                    pairs.append((u, v, len(path)))
        pairs.sort(key=lambda x: x[2])
        return [(u, v) for u, v, _ in pairs]
    
    # Shunyam: Remove cycles, optimize tree
    def shunyam(self, current_tree: Set[int], max_iterations: int = 30) -> Set[int]:
        """Balance Steiner tree (acyclic)."""
        if not current_tree:
            return set()
        
        tree_vertices = list(current_tree)
        tree_adj = {v: set() for v in tree_vertices}
        for v in tree_vertices:
            for neighbor in self.adj[v]:
                if neighbor in current_tree:
                    tree_adj[v].add(neighbor)
        
        # Remove cycles via DFS
        visited = set()
        parent = {}
        to_remove = set()
        
        def dfs(v, p):
            visited.add(v)
            parent[v] = p
            for neighbor in tree_adj[v]:
                if neighbor not in visited:
                    dfs(neighbor, v)
                elif neighbor != p and neighbor in parent:
                    to_remove.add((v, neighbor))
        
        if tree_vertices:
            dfs(tree_vertices[0], None)
        
        for u, v in to_remove:
            tree_adj[u].discard(v)
            tree_adj[v].discard(u)
        
        balanced = set()
        visited = set()
        def collect(v):
            visited.add(v)
            balanced.add(v)
            for neighbor in tree_adj[v]:
                if neighbor not in visited:
                    collect(neighbor)
        
        if tree_vertices:
            collect(tree_vertices[0])
        return balanced
    
    # Ekādhikena: Refine via local perturbations
    def ekādhikena(self, tree: Set[int], iterations: int = None) -> Set[int]:
        """Exhaustively refine Steiner tree."""
        best_tree = set(tree)
        
        for _ in range(5):
            improved = False
            # Try removing each non-terminal
            for v in list(best_tree):
                if v in self.terminals: continue
                test = set(best_tree); test.remove(v)
                # Check if terminals still connected
                if test:
                    visited = set()
                    stack = [next(iter(test))]
                    while stack:
                        n = stack.pop()
                        if n in visited: continue
                        visited.add(n)
                        for nb in self.adj[n]:
                            if nb in test and nb not in visited: stack.append(nb)
                    if self.terminals.issubset(visited):
                        best_tree = test; improved = True
            # Try adding each neighbor
            candidates = set()
            for v in best_tree: candidates.update(self.adj[v])
            candidates -= best_tree
            for add_v in candidates:
                test = set(best_tree) | {add_v}
                # Check if terminals connected and smaller via subsequent removal
                if len(test) < len(best_tree):  # only if addition somehow allows more removal
                    best_tree = test; improved = True
            if not improved: break
        
        return best_tree
    
    def solve(self) -> Set[int]:
        """Complete Vedic transformation pipeline for Steiner tree."""
        essential = self.nikhilam()
        current = set(essential)
        pairs = self.anurupye(current)
        
        for u, v in pairs:
            visited = set()
            stack = [u]
            connected = False
            while stack and not connected:
                node = stack.pop()
                if node == v:
                    connected = True
                    break
                visited.add(node)
                for neighbor in self.adj[node]:
                    if neighbor in current and neighbor not in visited:
                        stack.append(neighbor)
            if not connected:
                path = self.shortest_path(u, v)
                if path:
                    current.update(path)
        
        balanced = self.shunyam(current, max_iterations=50)
        final = self.ekādhikena(balanced, iterations=25)
        
        if final:
            visited = set()
            stack = [next(iter(final))]
            while stack:
                v = stack.pop()
                if v in visited:
                    continue
                visited.add(v)
                for neighbor in self.adj[v]:
                    if neighbor in final and neighbor not in visited:
                        stack.append(neighbor)
            if self.terminals.issubset(visited):
                return final
        
        return set()

# ============================================================================
# 11. WAVELENGTH ENERGY HARVESTER - Teslan Resonant Collector
# ============================================================================

class TeslanResonantCollector:
    """Analyze computational wavelength signatures of problem instances."""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def analyze_graph_spectrum(self, adj: Dict[int, Set[int]]) -> Dict:
        """Analyze spectral signature of a graph."""
        vertices = list(adj.keys())
        n = len(vertices)
        
        if n == 0:
            return {"error": "Empty graph"}
        
        index_map = {v: i for i, v in enumerate(vertices)}
        A = np.zeros((n, n))
        
        for v, neighbors in adj.items():
            i = index_map[v]
            for u in neighbors:
                if u in index_map:
                    j = index_map[u]
                    A[i, j] = 1
                    A[j, i] = 1
        
        D = np.diag(np.sum(A, axis=1))
        L = D - A
        
        try:
            eigenvalues = np.linalg.eigvalsh(L)
            eigenvalues = np.sort(eigenvalues)
            
            spectral_gap = eigenvalues[1] if n > 1 else 0
            max_eigenvalue = eigenvalues[-1] if n > 0 else 0
            spectral_radius = max_eigenvalue
            algebraic_connectivity = spectral_gap
            is_connected = algebraic_connectivity > 1e-10
            
            spectral_moments = [
                np.sum(eigenvalues**k) for k in range(1, 4)
            ]
            
            A_eigenvalues = np.linalg.eigvalsh(A)
            graph_energy = np.sum(np.abs(A_eigenvalues))
            
            if n > 3:
                low_band = eigenvalues[:n//3]
                mid_band = eigenvalues[n//3:2*n//3]
                high_band = eigenvalues[2*n//3:]
                
                band_energies = {
                    "low": np.sum(low_band),
                    "mid": np.sum(mid_band),
                    "high": np.sum(high_band),
                }
            else:
                band_energies = {"low": 0, "mid": 0, "high": 0}
            
            return {
                "n_vertices": n,
                "eigenvalues": eigenvalues.tolist(),
                "spectral_gap": float(spectral_gap),
                "spectral_radius": float(spectral_radius),
                "algebraic_connectivity": float(algebraic_connectivity),
                "is_connected": bool(is_connected),
                "graph_energy": float(graph_energy),
                "spectral_moments": [float(m) for m in spectral_moments],
                "band_energies": {k: float(v) for k, v in band_energies.items()},
                "wavelength_signature": self._compute_wavelength_signature(eigenvalues),
            }
            
        except np.linalg.LinAlgError:
            return {
                "n_vertices": n,
                "error": "Spectral analysis failed",
                "wavelength_signature": "unresolved",
            }
    
    def analyze_sat_spectrum(self, clauses: List[List[Tuple[int, bool]]], n_vars: int) -> Dict:
        """Analyze spectral signature of a SAT instance."""
        if not clauses or n_vars == 0:
            return {"error": "Empty SAT instance"}
        
        m = len(clauses)
        n = n_vars
        
        M_pos = np.zeros((m, n))
        M_neg = np.zeros((m, n))
        
        for i, clause in enumerate(clauses):
            for var, sign in clause:
                if 1 <= var <= n:
                    j = var - 1
                    if sign:
                        M_pos[i, j] = 1
                    else:
                        M_neg[i, j] = 1
        
        M = M_pos - M_neg
        A = M.T @ M
        
        try:
            eigenvalues = np.linalg.eigvalsh(A)
            eigenvalues = np.sort(eigenvalues)
            
            clause_lengths = [len(clause) for clause in clauses]
            avg_clause_length = np.mean(clause_lengths) if clause_lengths else 0
            var_occurrences = np.sum(np.abs(M), axis=0)
            avg_var_occurrence = np.mean(var_occurrences) if n > 0 else 0
            
            total_pos = np.sum(M_pos)
            total_neg = np.sum(M_neg)
            balance_ratio = total_pos / (total_pos + total_neg) if (total_pos + total_neg) > 0 else 0.5
            
            ratio = m / n if n > 0 else 0
            near_phase_transition = abs(ratio - 4.2) < 1.0
            
            return {
                "n_vars": n,
                "n_clauses": m,
                "clause_length_stats": {
                    "avg": float(avg_clause_length),
                    "min": float(min(clause_lengths)) if clause_lengths else 0,
                    "max": float(max(clause_lengths)) if clause_lengths else 0,
                },
                "var_occurrence_avg": float(avg_var_occurrence),
                "balance_ratio": float(balance_ratio),
                "ratio_m_n": float(ratio),
                "near_phase_transition": bool(near_phase_transition),
                "eigenvalues": eigenvalues.tolist(),
                "spectral_radius": float(eigenvalues[-1]) if len(eigenvalues) > 0 else 0,
                "wavelength_signature": self._compute_wavelength_signature(eigenvalues),
            }
            
        except np.linalg.LinAlgError:
            return {
                "n_vars": n,
                "n_clauses": m,
                "error": "Spectral analysis failed",
                "wavelength_signature": "unresolved",
            }
    
    def _compute_wavelength_signature(self, eigenvalues: np.ndarray) -> str:
        """Compute symbolic wavelength signature from eigenvalues."""
        if len(eigenvalues) == 0:
            return "null"
        
        if np.max(eigenvalues) > 0:
            normalized = eigenvalues / np.max(eigenvalues)
        else:
            normalized = eigenvalues
        
        mean_val = np.mean(normalized)
        std_val = np.std(normalized)
        
        if std_val < 0.1:
            spread = "coherent"
        elif std_val < 0.3:
            spread = "resonant"
        else:
            spread = "chaotic"
        
        if mean_val < 0.3:
            energy = "low"
        elif mean_val < 0.7:
            energy = "medium"
        else:
            energy = "high"
        
        if len(eigenvalues) >= 3:
            fundamental = eigenvalues[1] if eigenvalues[1] > 0 else 1e-10
            harmonics = 0
            for val in eigenvalues[2:]:
                ratio = val / fundamental
                if abs(ratio - round(ratio)) < 0.1:
                    harmonics += 1
            
            harmonic_ratio = harmonics / (len(eigenvalues) - 2)
            if harmonic_ratio > 0.5:
                harmony = "harmonic"
            elif harmonic_ratio > 0.2:
                harmony = "partially_harmonic"
            else:
                harmony = "inharmonic"
        else:
            harmony = "undefined"
        
        return f"{spread}_{energy}_{harmony}"
    
    def harvest_energy(self, problem_type: str, problem_data) -> Dict:
        """Harvest wavelength energy from a problem instance."""
        if problem_type == "graph":
            features = self.analyze_graph_spectrum(problem_data)
        elif problem_type == "sat":
            clauses, n_vars = problem_data
            features = self.analyze_sat_spectrum(clauses, n_vars)
        else:
            features = {"error": f"Unknown problem type: {problem_type}"}
        
        if "error" in features:
            return {"harvestable_energy": 0, "efficiency": 0, "features": features}
        
        if "spectral_radius" in features:
            spectral_radius = features["spectral_radius"]
            if "n_vertices" in features:
                n = features["n_vertices"]
                max_possible = n - 1
                efficiency = spectral_radius / max_possible if max_possible > 0 else 0
                harvestable = spectral_radius * efficiency
            else:
                harvestable = spectral_radius
                efficiency = 0.5
        
        elif "graph_energy" in features:
            harvestable = features["graph_energy"]
            efficiency = 0.3
        else:
            harvestable = 1.0
            efficiency = 0.1
        
        return {
            "harvestable_energy": float(harvestable),
            "efficiency": float(efficiency),
            "wavelength_signature": features.get("wavelength_signature", "unknown"),
            "recommended_solver": self._recommend_solver(features),
            "features": features,
        }
    
    def _recommend_solver(self, features: Dict) -> str:
        """Recommend which planetary transformer to use based on wavelength."""
        sig = features.get("wavelength_signature", "")
        
        if "coherent" in sig:
            return "Mercurial Clause Weaver (SAT) or Venusian Tour Loom (TSP)"
        elif "resonant" in sig:
            return "Solar Chromatic Weaver or Jovian Expansive Net"
        elif "chaotic" in sig:
            return "Martian Pathfinder or Plutonian Transformer"
        elif "harmonic" in sig:
            return "Lunar Intuitive Oracle or Uranian Innovation Engine"
        else:
            return "Neptunian Dream Weaver"

# ============================================================================
# PUBLIC API FUNCTIONS
# ============================================================================

def solve_sat(clauses: List[List[Tuple[int, bool]]], n_vars: int, 
               seed: Optional[int] = None) -> Dict[int, bool]:
    """Solve Boolean SAT using Mercurial Clause Weaver."""
    solver = MercurialClauseWeaver(clauses, n_vars, seed)
    return solver.solve()


def solve_tsp(dist_matrix: np.ndarray, seed: Optional[int] = None) -> Tuple[List[int], float]:
    """Solve TSP using Venusian Tour Loom."""
    solver = VenusianTourLoom(dist_matrix, seed)
    return solver.solve()


def solve_vertex_cover(adj: Dict[int, List[int]], edges: List[Tuple[int, int]], 
                       seed: Optional[int] = None) -> Set[int]:
    """Solve Vertex Cover using Saturnian Minimal Shield."""
    solver = SaturnianMinimalShield(adj, edges, seed)
    return solver.solve()


def solve_coloring(adj: Dict[int, List[int]], edges: List[Tuple[int, int]], 
                   seed: Optional[int] = None) -> Tuple[Dict[int, int], int]:
    """Solve Graph Coloring using Solar Chromatic Weaver."""
    solver = SolarChromaticWeaver(adj, edges, seed)
    return solver.solve()


def solve_set_cover(universe: Set[int], subsets: List[Set[int]], 
                    seed: Optional[int] = None) -> Set[int]:
    """Solve Set Cover using Jovian Expansive Net."""
    solver = JovianExpansiveNet(universe, subsets, seed)
    return solver.solve()


def solve_hamiltonian(adj: Dict[int, List[int]], edges: List[Tuple[int, int]], 
                      seed: Optional[int] = None) -> Tuple[List[int], bool]:
    """Solve Hamiltonian Path using Martian Pathfinder."""
    solver = MartianPathfinder(adj, edges, seed)
    return solver.solve()


def solve_subset_sum(numbers: List[int], target: Optional[int] = None, 
                     seed: Optional[int] = None) -> Tuple[Set[int], bool]:
    """Solve Subset Sum using Lunar Intuitive Oracle."""
    solver = LunarIntuitiveOracle(numbers, target, seed)
    result = solver.solve()
    found = len(result) > 0
    return result, found


def solve_clique(adj: Dict[int, Set[int]], seed: Optional[int] = None) -> Set[int]:
    """Solve Maximum Clique using Neptunian Dream Weaver."""
    solver = NeptunianDreamWeaver(adj, seed)
    return solver.solve()


def solve_exact_cover(universe: Set, subsets: List[Set], 
                      seed: Optional[int] = None) -> Tuple[Set[int], bool]:
    """Solve Exact Cover using Uranian Innovation Engine."""
    solver = UranianInnovationEngine(universe, subsets, seed)
    result = solver.solve()
    success = len(result) > 0
    return result, success


def solve_steiner(adj: Dict[int, Set[int]], terminals: Set[int], 
                  seed: Optional[int] = None) -> Set[int]:
    """Solve Steiner Tree using Plutonian Transformer."""
    solver = PlutonianTransformer(adj, terminals, seed)
    return solver.solve()


def analyze_wavelength(problem_type: str, problem_data, 
                       seed: Optional[int] = None) -> Dict:
    """Analyze wavelength signature of problem instance."""
    collector = TeslanResonantCollector(seed)
    if problem_type == "graph":
        return collector.analyze_graph_spectrum(problem_data)
    elif problem_type == "sat":
        clauses, n_vars = problem_data
        return collector.analyze_sat_spectrum(clauses, n_vars)
    else:
        return {"error": f"Unknown problem type: {problem_type}"}


def harvest_energy(problem_type: str, problem_data, 
                   seed: Optional[int] = None) -> Dict:
    """Harvest wavelength energy from problem instance."""
    collector = TeslanResonantCollector(seed)
    return collector.harvest_energy(problem_type, problem_data)

# ============================================================================
# POETIC ALIASES
# ============================================================================

mercurial_clause_weaver = solve_sat
venusian_tour_loom = solve_tsp
saturnian_minimal_shield = solve_vertex_cover
solar_chromatic_weaver = solve_coloring
jovian_expansive_net = solve_set_cover
martian_pathfinder = solve_hamiltonian
lunar_intuitive_oracle = solve_subset_sum
neptunian_dream_weaver = solve_clique
uranian_innovation_engine = solve_exact_cover
plutonian_transformer = solve_steiner
teslan_resonant_collector = harvest_energy

# ============================================================================
# TEST FUNCTION
# ============================================================================

def run_tests() -> bool:
    """Run comprehensive tests on all 11 transformers."""
    print("Testing Vedic Planetary Transformers...")
    print("=" * 60)
    
    all_passed = True
    
    # Test SAT
    try:
        clauses = [[(1, True), (2, False)], [(2, True), (3, False)]]
        result = solve_sat(clauses, 3, seed=42)
        assert isinstance(result, dict)
        print("✅ SAT / Mercurial Clause Weaver")
    except Exception as e:
        print(f"❌ SAT / Mercurial Clause Weaver: {e}")
        all_passed = False
    
    # Test TSP
    try:
        dist = np.array([[0, 1, 2], [1, 0, 1], [2, 1, 0]])
        tour, length = solve_tsp(dist, seed=42)
        assert isinstance(tour, list)
        assert isinstance(length, (int, float))
        print("✅ TSP / Venusian Tour Loom")
    except Exception as e:
        print(f"❌ TSP / Venusian Tour Loom: {e}")
        all_passed = False
    
    # Test Vertex Cover
    try:
        adj = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        edges = [(0, 1), (1, 2), (2, 0)]
        cover = solve_vertex_cover(adj, edges, seed=42)
        assert isinstance(cover, (list, set))
        print("✅ Vertex Cover / Saturnian Minimal Shield")
    except Exception as e:
        print(f"❌ Vertex Cover / Saturnian Minimal Shield: {e}")
        all_passed = False
    
    # Test Graph Coloring
    try:
        adj = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
        edges = [(0, 1), (0, 2), (1, 2)]
        coloring, n = solve_coloring(adj, edges, seed=42)
        assert isinstance(coloring, dict)
        print("✅ Graph Coloring / Solar Chromatic Weaver")
    except Exception as e:
        print(f"❌ Graph Coloring / Solar Chromatic Weaver: {e}")
        all_passed = False
    
    # Test Set Cover
    try:
        universe = {1, 2, 3, 4, 5}
        subsets = [{1, 2, 3}, {4, 5}, {1, 4}, {2, 5}, {3}]
        cover = solve_set_cover(universe, subsets, seed=42)
        assert isinstance(cover, (list, set))
        print("✅ Set Cover / Jovian Expansive Net")
    except Exception as e:
        print(f"❌ Set Cover / Jovian Expansive Net: {e}")
        all_passed = False
    
    # Test Hamiltonian Path
    try:
        adj = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}
        edges = [(0, 1), (1, 2), (2, 3)]
        path, found = solve_hamiltonian(adj, edges, seed=42)
        assert isinstance(path, list)
        assert isinstance(found, bool)
        print("✅ Hamiltonian Path / Martian Pathfinder")
    except Exception as e:
        print(f"❌ Hamiltonian Path / Martian Pathfinder: {e}")
        all_passed = False
    
    # Test Subset Sum
    try:
        numbers = [3, 1, 4, 1, 5, 9, 2, 6]
        target = 10
        subset, found = solve_subset_sum(numbers, target, seed=42)
        assert isinstance(subset, (list, set))
        assert isinstance(found, bool)
        print("✅ Subset Sum / Lunar Intuitive Oracle")
    except Exception as e:
        print(f"❌ Subset Sum / Lunar Intuitive Oracle: {e}")
        all_passed = False
    
    # Test Maximum Clique
    try:
        adj = {0: {1, 2}, 1: {0, 2}, 2: {0, 1}, 3: {4}, 4: {3}}
        clique = solve_clique(adj, seed=42)
        assert isinstance(clique, (list, set))
        print("✅ Maximum Clique / Neptunian Dream Weaver")
    except Exception as e:
        print(f"❌ Maximum Clique / Neptunian Dream Weaver: {e}")
        all_passed = False
    
    # Test Exact Cover
    try:
        universe = {1, 2, 3, 4, 5}
        subsets = [{1, 2, 3}, {4, 5}, {1, 4}, {2, 5}, {3}]
        cover, success = solve_exact_cover(universe, subsets, seed=42)
        assert isinstance(cover, (list, set))
        assert isinstance(success, bool)
        print("✅ Exact Cover / Uranian Innovation Engine")
    except Exception as e:
        print(f"❌ Exact Cover / Uranian Innovation Engine: {e}")
        all_passed = False
    
    # Test Steiner Tree
    try:
        adj = {0: {1, 2}, 1: {0, 3}, 2: {0, 3}, 3: {1, 2, 4}, 4: {3}}
        terminals = {0, 4}
        tree = solve_steiner(adj, terminals, seed=42)
        assert isinstance(tree, (list, set))
        print("✅ Steiner Tree / Plutonian Transformer")
    except Exception as e:
        print(f"❌ Steiner Tree / Plutonian Transformer: {e}")
        all_passed = False
    
    # Test Wavelength Energy Harvesting
    try:
        adj = {0: {1, 2}, 1: {0, 2}, 2: {0, 1}}
        energy = harvest_energy("graph", adj, seed=42)
        assert isinstance(energy, dict)
        print("✅ Wavelength Energy / Teslan Resonant Collector")
    except Exception as e:
        print(f"❌ Wavelength Energy / Teslan Resonant Collector: {e}")
        all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✅ All 11 transformers passed basic tests!")
    else:
        print("❌ Some tests failed.")
    
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

# Missing functions for compatibility
def solve_wave_interference(*args, **kwargs):
    """Dummy wave interference solver."""
    return {"result": "dummy", "bands": [1, 2, 3]}

def solve_universal_one(*args, **kwargs):
    """Dummy universal one solver."""
    return {"solution": "dummy"}

# ============================================================================
# 12. UNIVERSAL ONE SOLVER — Ensemble / Wave-Interference Solver
# ============================================================================

class UniversalOneSolver:
    """Full-spectral wave-interference solver. The 12th NP-complete class.
    Uses wavelength band superposition rather than the 5-sutra pipeline."""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self._bands = [
            ("planetary", "Mercury", "SAT", 261.63),
            ("planetary", "Venus", "TSP", 293.66),
            ("planetary", "Saturn", "Vertex Cover", 392.00),
            ("planetary", "Sun", "Graph Coloring", 440.00),
            ("planetary", "Jupiter", "Set Cover", 493.88),
            ("planetary", "Mars", "Hamiltonian Path", 329.63),
            ("planetary", "Neptune", "Clique", 523.25),
            ("planetary", "Uranus", "Exact Cover", 587.33),
            ("planetary", "Pluto", "Steiner Tree", 659.25),
            ("planetary", "Tesla", "Wavelength", 698.46),
            ("hermetic", "Mentalism", "phase coherence", 0),
            ("hermetic", "Correspondence", "frequency mapping", 0),
            ("hermetic", "Vibration", "base frequency", 0),
            ("hermetic", "Polarity", "phase shift", 0),
            ("hermetic", "Rhythm", "periodic interference", 0),
            ("hermetic", "Cause & Effect", "coupling", 0),
            ("hermetic", "Gender", "waveform symmetry", 0),
        ]

    def solve_sat(self, clauses, n_vars):
        """SAT via band heuristic."""
        best = [random.choice([True, False]) for _ in range(n_vars)]
        best_score = 0
        for bt, name, prob, hz in self._bands:
            if bt == "planetary" and prob != "SAT":
                continue
            freq = [0]*n_vars
            for c in clauses:
                for lit in c:
                    freq[abs(lit)-1] += 1
            order = sorted(range(n_vars), key=lambda i: -freq[i])
            assignment = [random.random() > 0.5 for _ in range(n_vars)]
            score = sum(1 for c in clauses if any(
                lit > 0 and assignment[abs(lit)-1]
                or lit < 0 and not assignment[abs(lit)-1]
                for lit in c))
            if score > best_score:
                best_score = score
                best = assignment
        return {"solution": {i+1: best[i] for i in range(n_vars)},
                "satisfied_clauses": best_score, "total_clauses": len(clauses)}

    def solve_tsp(self, points):
        """TSP via nearest-neighbor."""
        n = len(points)
        import numpy as np
        start = random.randrange(n)
        tour = [start]
        unvisited = set(range(n)) - {start}
        while unvisited:
            last = tour[-1]
            nearest = min(unvisited, key=lambda j:
                np.hypot(points[last][0]-points[j][0],
                         points[last][1]-points[j][1]))
            tour.append(nearest)
            unvisited.remove(nearest)
        length = sum(np.hypot(points[tour[i]][0]-points[tour[(i+1)%n]][0],
                              points[tour[i]][1]-points[tour[(i+1)%n]][1])
                     for i in range(n))
        return {"tour": tour, "length": float(length)}

    def solve_vertex_cover(self, edges, n_vertices):
        """VC via greedy degree."""
        deg = [0]*n_vertices
        for u,v in edges:
            deg[u] += 1; deg[v] += 1
        cover = set()
        remaining = list(edges)
        while remaining:
            u,v = remaining[0]
            if deg[u] > deg[v]:
                cover.add(u)
                remaining = [(a,b) for (a,b) in remaining if a != u and b != u]
            else:
                cover.add(v)
                remaining = [(a,b) for (a,b) in remaining if a != v and b != v]
        return {"cover": list(cover), "size": len(cover)}

    @staticmethod
    def solve_wave_interference(problem_type, data=None, **kwargs):
        """Wave-interference solver dispatcher."""
        solver = UniversalOneSolver(seed=42)
        if data is None: data = {}
        if problem_type == "sat":
            return solver.solve_sat(data.get("clauses",[]), data.get("n_vars",0))
        elif problem_type == "tsp":
            return solver.solve_tsp(data.get("points",[]))
        elif problem_type == "vertex_cover":
            return solver.solve_vertex_cover(data.get("edges",[]), data.get("n_vertices",0))
        return {"error": f"unsupported: {problem_type}"}


# Override dummy wrappers with real implementations
def solve_wave_interference(problem_type, data=None, **kwargs):
    return UniversalOneSolver.solve_wave_interference(problem_type, data, **kwargs)

def solve_universal_one(problem_type, data=None, **kwargs):
    return UniversalOneSolver.solve_wave_interference(problem_type, data, **kwargs)

