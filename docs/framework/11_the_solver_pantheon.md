# Chapter 11: The Solver Pantheon

> 10 NP-complete solvers + 1 Wavelength Collector.
> 1 Observer that watches them all.

## 11.1 Overview

The Solver Pantheon is a set of 11 specialized constraint-satisfaction processors, each operating on a specific NP-complete problem class, plus a 12th Observer function that watches all 11 simultaneously.

Each solver takes a problem state, applies its specific transformation toward convergence, and returns either a valid configuration or a signal that no valid configuration exists. The solvers operate in parallel, not sequentially — they are dispatched by the valkyrie system (the Door Guardians) based on which assessment criteria the signal fails.

### The 11 + 1 Structure

| # | Name | Problem | Complexity | Pipeline Function |
|---|------|---------|------------|-------------------|
| 1 | SAT Solver | Boolean Satisfiability | NP-complete | Truth assignment |
| 2 | TSP Solver | Traveling Salesman | NP-hard | Path optimization |
| 3 | Vertex Cover | Minimum Vertex Cover | NP-complete | Minimal shield |
| 4 | Max Clique | Maximum Clique | NP-complete | Affinity grouping |
| 5 | Graph Coloring | Chromatic Number | NP-complete | Spectral separation |
| 6 | Set Cover | Minimum Set Cover | NP-complete | Complete coverage |
| 7 | Hamiltonian Path | Hamiltonian Path | NP-complete | Just visitation |
| 8 | Subset Sum | Subset Sum | NP-complete | Signal from noise |
| 9 | Exact Cover | Exact Cover | NP-complete | Perfect tuning |
| 10 | Steiner Tree | Steiner Tree | NP-complete | Minimal connection |
| 11 | Wavelength | Resonance Collector | Polynomial | Energy harvesting |
| O | Observer | Self-referential | Meta | All-seeing |

## 11.2 The 11 Solvers

### SOLVER-1: Boolean Satisfiability (SAT)

**Problem:** Given a set of clauses in conjunctive normal form, find a truth assignment that satisfies all clauses, or determine none exists.

**Input:** `{clauses: [[±1, ±2, ..., ±n], ...], assignment: {var: bool}}`

**Operation:** Determines if a state configuration is satisfiable. Returns the truth assignment that makes every constraint true.

**Pantheon mappings:** Egyptian — Maat (truth feather). Vedic — Mitra (contract). Norse — Sannspá (true-seer). Chinese — Qián (heaven, creative truth). Greek — Athena (wisdom born fully-formed).

### SOLVER-2: Traveling Salesman Problem (TSP)

**Problem:** Given a set of cities and distances between them, find the shortest possible route that visits each city exactly once and returns to the origin.

**Input:** `{distances: [(D, a, b), ...], tour: [city sequence]}`

**Operation:** Finds the optimal path through adversarial state space. The route that minimizes traversal cost.

**Pantheon mappings:** Egyptian — Wepwawet (way-opener). Vedic — Ashvins (horse-twins). Norse — Vegljós (way-light). Chinese — Chéng-huáng (city god). Greek — Hermes (roads, travelers).

### SOLVER-3: Vertex Cover

**Problem:** Given a graph G = (V, E), find the smallest set of vertices such that every edge in E has at least one endpoint in the set.

**Input:** `{vertices: [...], edges: [(u,v), ...], cover: [vertex set]}`

**Operation:** Finds the minimal defensive resource. The smallest shield that covers all vulnerabilities.

**Pantheon mappings:** Egyptian — Thoth (scribe, defense). Vedic — Indra (thunderbolt). Norse — Þrúðr (strength/power). Chinese — Shénnóng (divine farmer). Greek — Ares (war, defense).

### SOLVER-4: Maximum Clique

**Problem:** Given a graph G = (V, E), find the largest subset of vertices that are all mutually connected (a clique).

**Input:** `{vertices: [...], edges: [(u,v), ...], clique: [vertex set]}`

**Operation:** Finds the maximum mutually compatible group. The largest set that shares total affinity.

**Pantheon mappings:** Egyptian — Ra (sun, unity). Vedic — Vishnu (pervader). Norse — Samhelda (together-hold). Chinese — Yuè Lǎo (matchmaker). Greek — Aphrodite (love, affinity).

### SOLVER-5: Graph Coloring

**Problem:** Given a graph G = (V, E), assign a color to each vertex such that no two adjacent vertices share the same color, using the minimum number of colors.

**Input:** `{vertices: [...], edges: [(u,v), ...], assignment: {vertex: color}}`

**Operation:** Separates conflicting elements into non-interfering channels. Prevents frequency collision.

**Pantheon mappings:** Egyptian — Horus (falcon, distinction). Vedic — Varuna (order, separation). Norse — Litgreina (color-splitter/shining-ruler). Chinese — Zhēn Wǔ (dark warrior). Greek — Apollo (lyre, separation).

### SOLVER-6: Set Cover

**Problem:** Given a universe of elements and a collection of sets whose union covers the universe, find the smallest sub-collection that still covers all elements.

**Input:** `{universe: [...], sets: [[...], ...], cover: [set indices]}`

**Operation:** Finds the minimal complete transmission. Everything covered, nothing wasted.

**Pantheon mappings:** Egyptian — Geb (earth, complete domain). Vedic — Dyaus (sky, complete coverage). Norse — Geirahöð (spear-war). Chinese — Yù Huáng (Jade Emperor). Greek — Zeus (sky, complete domain).

### SOLVER-7: Hamiltonian Path

**Problem:** Given a graph G = (V, E), find a path that visits each vertex exactly once.

**Input:** `{vertices: [...], edges: [(u,v), ...], path: [vertex sequence]}`

**Operation:** Finds the path that visits every seat exactly once. The traversal that honors every position without repetition.

**Pantheon mappings:** Egyptian — Osiris (severed, reassembled). Vedic — Yama (death, first mortal). Norse — Gegnumsól (through-sun). Chinese — Mèng Pó (oblivion, severed). Greek — Chaos (first creation).

### SOLVER-8: Subset Sum

**Problem:** Given a set of numbers and a target sum, find a subset that sums exactly to the target, or determine none exists.

**Input:** `{numbers: [...], target: int, selected: [indices], sum: int}`

**Operation:** Identifies hidden pattern in numerical noise. Finds the subset that sums to meaning.

**Pantheon mappings:** Egyptian — Bastet (hidden, feline). Vedic — Rudra (howler, hidden in storm). Norse — Hlökk (noise). Chinese — Guǐ (ghosts, hidden signals). Greek — Hecate (crossroads, hidden).

### SOLVER-9: Exact Cover

**Problem:** Given a universe and a collection of subsets, find a sub-collection that covers every element exactly once (no overlaps, no gaps).

**Input:** `{universe: [...], sets: [[...], ...], cover: [set indices]}`

**Operation:** Finds the partition with zero waste and zero overlap. Perfect exactness.

**Pantheon mappings:** Egyptian — Nephthys (exact ritual). Vedic — Savitr (impeller, precision). Norse — Göll (screamer). Chinese — Dòumǔ (dipper mother). Greek — Artemis (boundaries, precision).

### SOLVER-10: Steiner Tree

**Problem:** Given a graph G = (V, E) with edge weights and a subset of required vertices (terminals), find the minimum-weight tree connecting all terminals (may include non-terminal vertices as Steiner points).

**Input:** `{vertices: [...], edges: [(w, u, v), ...], terminals: [...], tree: [edge set]}`

**Operation:** Finds the minimal connection across required points. The finest thread that holds everything together.

**Pantheon mappings:** Egyptian — Isis (magic, connection). Vedic — Saraswati (wisdom thread). Norse — Reginleif (inheritance). Chinese — Fú Xī (culture founder). Greek — Hera (marriage, preservation).

### SOLVER-11: Wavelength Resonance (Teslan Collector)

**Problem:** Given a spectrum of frequency bands, identify resonant patterns and collect coherent energy across bands.

**Input:** `{bands: [...], resonance_map: {...}, output: float}`

**Operation:** Harvests resonant energy across the full 72-band spectrum. The collector that draws power from coherence.

**Pantheon mappings:** Egyptian — Nut (sky, wavelength). Vedic — Prithvi (earth, resonance). Norse — Randgríð (shield-truce). Chinese — Hòu Tǔ (earth, resonance). Greek — Gaia (earth, frequency).

## 11.3 The Observer — 12th Solver

**Function:** Self-referential assessment. Watches all 11 solvers simultaneously. Cannot be watched from below. The function that catalogues what is known and ensures it survives.

**Position:** LEVEL-9 (crown). Accessible from ARTIFACT-11 (the high seat).

**Properties:**
- Sees all 9 processing levels simultaneously
- Sacrifices half its perspective to drink from the wisdom well
- Hangs on the tree for 9 cycles to recover the 18 operational sub-phases
- Is consumed by its own observation during the FULL phase
- Is replaced by a new observer after cycle completion

**Pantheon mappings:** Egyptian — Atum/Atum-Kheprer. Vedic — Brahman (the Absolute). Norse — Odin/Valföðr. Chinese — Dào (the unnameable). Greek — Kronos (time itself).

**The Observer is not a solver.** It does not solve — it watches. It catalogues. It ensures that whatever the 11 solvers produce is recorded and preserved. Without the Observer, the pipeline would process cycling states indefinitely with no memory of what was learned.

## 11.4 Solver Dispatch Architecture

Solvers are not applied to the raw input. They operate on specific assessment failures:

```
Assessment identifies: BAND-5 below noise floor
    |
    Which door? EXCOMMUNICATED (severed transmission path)
    |
    Which dispatch? DOOR-4 → Solver-7 (Hamiltonian Path)
    |
    Result: Path restored across the severed connection
```

The valkyrie system (Norse) and door guardians (all frameworks) are dispatchers — they classify the type of signal failure and route to the appropriate solver. A single state may trigger multiple dispatchers simultaneously. Solvers run in parallel, each attempting to correct its assignment.

## 11.5 Complexity Classes

| Class | Solver | Example |
|-------|--------|---------|
| NP-complete | SAT, Vertex Cover, Max Clique, Graph Coloring, Set Cover, Hamiltonian Path, Subset Sum, Exact Cover, Steiner Tree | Any constraint on a finite satisfiability set |
| NP-hard | TSP | Optimization version of NP-complete decision problem |
| Polynomial | Wavelength Resonance | Spectral decomposition of 72-element vectors |

The pipeline only cares about NP-complete problems because **every real-world problem can be reduced to an NP-complete instance**. The FP = NP conjecture (Functional Polynomial = Non-deterministic Polynomial) means these reductions are tractable — but the framework predates that proof by 4,000 years.

## 11.6 Summary

| # | Solver | Pantheon (Egyptian) | Problem Solved |
|---|--------|--------------------|----------------|
| 1 | SAT | Maat (truth feather) | Truth assignment |
| 2 | TSP | Wepwawet (way-opener) | Path optimization |
| 3 | Vertex Cover | Thoth (scribe) | Minimal shield |
| 4 | Max Clique | Ra (sun) | Affinity grouping |
| 5 | Graph Coloring | Horus (falcon) | Spectral separation |
| 6 | Set Cover | Geb (earth) | Complete coverage |
| 7 | Hamiltonian Path | Osiris (reassembled) | Just visitation |
| 8 | Subset Sum | Bastet (hidden) | Signal from noise |
| 9 | Exact Cover | Nephthys (exact ritual) | Perfect tuning |
| 10 | Steiner Tree | Isis (connection) | Minimal connection |
| 11 | Wavelength | Nut (sky) | Energy harvesting |
| O | Observer | Atum | Self-referential watch |
