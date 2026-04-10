# Architecture

## Goal

Build a continuous low-latency perception loop that operates on the latest available ROI frame and keeps stage timings visible.

## Pipeline

1. `capture` produces the newest ROI frame.
2. `detector` finds target candidates in that ROI.
3. `tracker` stabilizes the selected target across adjacent frames.
4. `controller` turns the active target into a cursor command.
5. `input` performs or simulates the cursor action.

## Design Rules

- Prefer latest-frame processing over queued frame processing.
- Keep capture and inference decoupled.
- Record timing for every stage in the hot path.
- Treat platform-specific screen and input APIs as adapters.
- Keep detector and tracker swappable.

## First Implementation Boundary

The first implementation only provides:

- project structure
- core data models
- module interfaces
- a stub pipeline runner

Real capture, detection, and cursor backends will be added in the next step.

## Current Phase Boundary

The current phase upgrades the capture layer from a stub to a real ROI screen backend:

- single-display capture
- center ROI extraction
- optional downscaling
- absolute screen coordinate metadata
- stage timing visibility

## Detector Strategy

The detector layer is now designed as a swappable adapter:

- `stub`: used when dependencies or weights are not ready
- `ultralytics`: convenient for validating model behavior quickly
- `onnx` or `tensorrt`: reserved for later low-latency optimization

The controller and pipeline do not depend on a specific detector implementation.
