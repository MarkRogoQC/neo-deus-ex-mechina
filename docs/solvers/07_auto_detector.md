# Auto Detector

> Automatic frequency detection and band classification engine.

## Overview

The Auto Detector is the framework's signal detection module. It automatically identifies frequency patterns in input data and classifies them to their correct 72-band positions.

## Detection Process

1. **Input sampling** — Collect raw frequency data
2. **Noise filtering** — Apply Z-cancel to remove noise
3. **Pattern matching** — Match against known band templates
4. **Classification** — Assign each pattern to a band position
5. **Confidence scoring** — Score each match by φ/2 decay similarity

## Features

- Automatic band detection from raw signal data
- Multi-source pattern correlation
- Confidence-based threshold filtering
- Real-time processing support
