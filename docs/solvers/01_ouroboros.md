# The Ouroboros Solver

> Self-referential decomposition engine. The solver that eats its own tail — iterating until convergence.

## Overview

The Ouroboros solver implements a self-referential decomposition strategy for NP-complete problems. It processes constraints through repeated cycles, where each cycle refines the previous solution until a fixed point is reached.

## Algorithm

1. **Initial decomposition** — Break the problem into sub-components
2. **Frequency mapping** — Map each component to its 72-band position
3. **Cycle processing** — Iterate through component refinement
4. **Convergence check** — Verify against the φ/2 decay threshold
5. **Fixed point** — Return the self-consistent solution

## Implementation

The solver uses the 72-band frequency decomposition to identify structural invariants across multiple decomposition passes.
