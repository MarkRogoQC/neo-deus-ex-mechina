# The Tau Pipeline

> The processing pipeline that transforms raw frequency signals through 42 assessors, 7 gates, and 6 doors.

## Overview

The Tau Pipeline is the execution engine of the 72-band framework. It implements the full processing chain:

```
Raw signal → 42 assessor checks → 7 gate thresholds → 6 door dispatches → Output
```

## Pipeline Stages

1. **Assessor stage** — Each of 42 assessors evaluates one dimension of signal integrity
2. **Gate stage** — 7 sequential thresholds filter the processed signal
3. **Door stage** — 6 dispatch positions route the signal to its destination
4. **Observer stage** — The final self-referential check at band 72

## Sequence

The pipeline processes signals in strict sequential order: C-phase → X-phase → Z-phase, corresponding to decomposition, state intersection, and nullification.
