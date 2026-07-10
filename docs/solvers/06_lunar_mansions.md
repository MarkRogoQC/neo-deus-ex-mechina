# Lunar Mansions

> The 28-band lunar spectrum processor. Implements the lunar phase cycle as a frequency-domain operation.

## Overview

Lunar Mansions implements the 28-band lunar frequency spectrum. Each mansion corresponds to one day of the lunar cycle, producing a 28-position frequency register that complements the 72-band solar spectrum.

## 28-Band Structure

The 28 lunar mansions divide the full 72-band spectrum into a lunar sub-cycle:

- **Bands 1-14:** Waxing phase (C-dominated)
- **Bands 15-28:** Waning phase (Z-dominated)
- **Bands 14-15:** Full moon (X-intersection)

## Integration

The lunar spectrum integrates with the solar 72-band spectrum through:
- **Harmonic alignment** — Lunar bands resonate with specific solar bands
- **Phase coupling** — Lunar phase determines the C/X/Z emphasis
- **Carrier modulation** — The moon modulates the base carrier frequency
