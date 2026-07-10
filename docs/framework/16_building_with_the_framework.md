# Chapter 16: Building with the Framework

> From decoding to construction.
> A practical guide to using the 72-band pipeline.

## 16.1 Starting Point

You do not need to be a mathematician or a programmer to use the framework. The pipeline is a tool — like a telescope or a tuning fork — that reveals structure that was always there. This chapter walks you through building with it.

### What You Need

- **Curiosity** — the desire to see what the 72-band structure reveals
- **Something to analyze** — a piece of text, a signal, a problem, a system
- **The sig() function** — decomposition into 72 bands (Chapter 10)
- **The assessor table** — 42 dimensions of signal integrity (Chapter 12)

That's it. The rest emerges.

## 16.2 The Two Directions

The framework operates in two directions:

```
Decode:  Input → 72 bands → Pipeline → Meaning
Encode:  Meaning → Pipeline → 72 bands → Output
```

**Decode** takes something you have and reveals its structure. This is the Voynich direction — the manuscript was there, the framework revealed what it encoded.

**Encode** takes something you want to express and translates it into the pipeline's vocabulary. This is the construction direction — building new things that the pipeline can process.

## 16.3 Decoding Workflow

Given an input (text, signal, problem instance), follow these steps:

### Step 1: Decompose

```python
bands = sig(input)
```

This produces a 72-element vector summing to 1.0. Each element represents the energy in one frequency band.

### Step 2: Check Noise Floor

```
if bands[i] < 0.05:
    # This band is below the noise floor — exclude from analysis
```

Bands with energy below ε = 0.05 carry negligible signal.

### Step 3: Identify Dominant Category

The 72 bands divide into 6 categories of 12:

| Category | Bands | If dominant, the input encodes... |
|----------|-------|-----------------------------------|
| Planetary (1-12) | Logical/mathematical structure | A constraint problem |
| Hermetic (13-24) | Universal principles | A structural pattern |
| Religious (25-36) | Archetypal patterns | A narrative/meaning structure |
| Cosmic (37-48) | Universal scale | A systems-level problem |
| Human (49-60) | Psychological/biological | A living system |
| Meta (61-72) | Transcendence | A consciousness/awareness structure |

Where does most energy concentrate? That's the domain of the input.

### Step 4: Find ONE Bands

ONE bands (positions 12, 24, 36, 48, 60, 72) show the category transition points. High energy at a ONE band means the input is cycling between categories.

### Step 5: Run the Assessors

Check each of the 42 assessors against the band vector:

```
pass_count = 0
for i in range(42):
    if assess(bands, assessor=i) == PASS:
        pass_count += 1
```

If pass_count >= 34, the signal is internally consistent — proceed to gates.

### Step 6: Trace the Gates

Each gate is a sequential threshold. The state either passes or fails at each one. If all 7 pass — the state has converged.

## 16.4 Encoding Workflow

Given a desired output or design, work backward through the pipeline:

### Step 1: Define the Output

What is the converged state? What does the output buffer contain after processing?

### Step 2: Construct the Gates

What thresholds must the state pass? Plan the 7 sequential checks that validate success.

### Step 3: Define the Assessors

What integrity criteria will the state be measured against? The 42 dimensions can be customized to the domain.

### Step 4: Choose the 12-Phase Cycle

Will the system use all 11 solvers, or a subset? Which C/X/Z operations are needed?

### Step 5: Compose the Input

Given the desired output, work backwards through the pipeline to determine what input decomposition produces that output.

## 16.5 Template: Building a Pipeline for Any Problem

```python
def build_pipeline(input_data, domain="planetary"):
    # Stage 1: Decompose
    bands = sig(input_data)
    categories = {
        "planetary":  range(1, 13),
        "hermetic":   range(13, 25),
        "religious":  range(25, 37),
        "cosmic":     range(37, 49),
        "human":      range(49, 61),
        "meta":       range(61, 73)
    }
    
    # Identify dominant category
    domain_bands = categories[domain]
    focus_energy = sum(bands[i] for i in domain_bands if i < len(bands))
    
    # Stage 2: 12-Phase Cycle
    ops = ["C","C","X","X","Z","Z","C","X","X","Z","Z","ONE"]
    state = bands
    for phase in range(12):
        state = apply_operation(state, ops[phase])
    
    # Stage 3: Assess
    result = assess(state)
    passed = result["passed"]
    
    # Stage 4: Gate
    if passed >= 34:
        gate_result = gates(state)
        if gate_result["reached"] == 7:
            # Stage 5: Output
            return output(state)
    
    # Not converged — recycle
    return build_pipeline(state, domain)
```

## 16.6 Example: Composing a Frequency Instruction

A frequency instruction is a sequence of C/X/Z operations at specific bands. To compose one:

1. **Identify the target** — what state do you want to produce?
2. **Identify the starting state** — what state are you processing?
3. **Compute the delta vector** — `delta[i] = sig(target)[i] - sig(start)[i]` for each band
4. **Decompose the delta** — which bands need which operation? Positive delta suggests C, crossing patterns suggest X, near-zero suggests Z
5. **Compose the instruction** — sequence of `(band, operation, intensity)` tuples

The instruction is executable by any implementation of the pipeline.

## 16.7 The Observer Position

Every pipeline needs an observer — the function that watches all 11 solvers simultaneously and records the output. In building your own pipeline:

```
Observer properties:
- Sees all 9 processing levels simultaneously
- Sacrifices half its perspective to access the wisdom well (cross-reference)
- Hangs on the tree for 9 cycles to recover all 18 operational sub-phases
- Is consumed during FULL phase (its current perspective is subsumed)
- Is replaced by a new observer after cycle completion
```

The observer is a self-referential assessment function — it catalogues what the solvers produce and ensures it survives. In implementation terms, it can be a logging function, a database commit, or any persistent storage that preserves the cycle's output for the next iteration.

## 16.8 Construction Principles

### Principle 1: Start with the invariant

The pipeline is invariant. The operations are correct by definition. Your job is not to redesign the pipeline — it is to apply it to your domain.

### Principle 2: Let the band structure guide you

If your problem doesn't fit into 72 bands in 6 categories of 12 — check your assumption. The band structure is universal. The problem's representation might need adjustment.

### Principle 3: Use the noise floor

ε = 0.05 is not arbitrary. It is the threshold below which the signal cannot be reliably distinguished from noise. Pushing below ε introduces error into the assessment phase. If your signal has too many bands below ε, increase the input size or reduce the band count.

### Principle 4: The inbetween is the instruction

The delta between two decomposable things IS the correction instruction. Given input A and desired output B, compute the per-band delta vector:

```
delta[i] = sig(A)[i] - sig(B)[i]
```

The **direction** of each delta[i] tells you which operation to apply (positive → C-complement, crossing zero → X-cross, near zero → Z-cancel). The **magnitude** tells you the intensity. Inharmony — the scalar `sqrt(Σ delta[i]²)` — is the overall distance metric. The delta vector itself is the instruction.

### Principle 5: FULL phase completes the cycle

The FULL phase (ONE at band 12, then all 12 phases) performs C→X→Z in sequence. This is NOT termination — it is cycle completion. The observer's current perspective is subsumed into the cycle's output, and a new observer is created to carry forward what was learned. The hall endures.

## 16.9 The Complete Toolset

| Tool | Function | When to Use |
|------|----------|-------------|
| sig() | Decompose input to 72 bands | Always — this is the entry point |
| inharmony() | Measure scalar difference between states | Comparing two inputs |
| assess() | Check signal integrity | Before routing to gates |
| gates() | Apply sequential thresholds | After assessment |
| complement() | Apply C operation | When state needs structural inversion |
| cross() | Apply X operation | When two states need combination |
| cancel() | Apply Z operation | When state needs reduction |
| Solver 1-11 | Domain-specific constraint solving | When specific processing is needed |
| FULL phase | Cycle completion | When the cycle is done |

## 16.10 Closing

The framework is open. The code is available. The pipeline works.

You do not need to be a priest, a mathematician, or a programmer to use it. You need an input and curiosity about what it encodes.

The signal is free. The road is open. The hall is waiting.

**The invariant: Ω = {C,X,Z} × f.**

**The answer is always in the frequency.**
