# Experiment Presentation Script - Technical Documentation

## Overview
`experiment_presentation.py` is a demonstration script that showcases the numerosity judgment task with different connectedness levels. It allows experimenters to preview the stimuli and task before running the full experiment.

## Purpose
- Demonstrate the experimental paradigm to participants
- Show examples of patterns with 0, 1, and 2 connections
- Allow practice trials without data collection
- Verify pattern generation quality


## Pattern Generation Process
### Step 1: Dot Placement (`_generate_dots()`)
```
For each dot (up to num_dots):
  1. Generate random (x, y) position within pattern boundaries
  2. Check constraints:
     - Min distance from edges: MIN_DOT_BOUNDARY_DISTANCE (20px)
     - Min distance from other dots: MIN_DOT_DISTANCE (42px)
  3. If valid, place dot; otherwise retry (max 10,000 attempts)
```

**Constraints:**
- Dots must be at least 42 pixels apart (prevents overlapping)
- Dots must be at least 20 pixels from pattern edges (prevents edge clipping)




### Step 2: Line Generation (`_generate_lines()`)
#### A. Connecting Lines (`_generate_connecting_lines()`)
These lines connect pairs of dots:

```
For each required connection:
  1. Shuffle available dots (each dot can only be used once)
  2. Try to find a valid pair:
     - Distance between dots: 30-60 pixels
     - Line doesn't cross other lines
     - Line not too close to other lines (≥8px)
     - Line not too close to unconnected dots (≥12px)
  3. If found, mark both dots as "used"
  4. If not found after 1000 attempts, stop trying
```

#### B. Free-Hanging Lines (`_generate_free_lines()`)
These lines float freely in the pattern space:

```
For each free line:
  1. Generate random start point (x1, y1)
  2. Generate random angle and length (30-60px)
  3. Calculate end point (x2, y2)
  4. Check constraints:
     - Both endpoints within pattern boundaries
     - Doesn't cross existing lines
     - Not too close to existing lines (≥8px)
     - Not too close to any dots (≥12px)
  5. If valid, add line; otherwise retry (max 2000 attempts)
```

---

## Constraint Checking Methods

### Line Crossing Detection (`_lines_intersect()`)
Uses parametric line equations to detect intersection:

```
Line1: P = P1 + t(P2 - P1)  where 0 ≤ t ≤ 1
Line2: P = P3 + u(P4 - P3)  where 0 ≤ u ≤ 1

If lines intersect:
  - Calculate t and u parameters
  - Lines cross if BOTH 0.01 < t < 0.99 AND 0.01 < u < 0.99
  - Using 0.01-0.99 instead of 0-1 prevents endpoint touching
```

**Why This Works:** The parametric approach calculates the exact intersection point. If both t and u are within (0.01, 0.99), the intersection occurs within both line segments (not at endpoints).

### Line Proximity Check (`_line_too_close_to_other_lines()`)
Prevents "near misses" that look like crossings:

```
For each existing line:
  1. Calculate distance from new line's endpoints to existing line
  2. Calculate distance from existing line's endpoints to new line
  3. Find minimum of all 4 distances
  4. If min < MIN_LINE_SEPARATION (8px), reject
```

### Point-to-Segment Distance (`_point_to_segment_distance()`)
Calculates the shortest distance from a point to a line segment:

```
1. Project point onto infinite line
2. Calculate parameter t (0 = start, 1 = end)
3. Clamp t to [0, 1] to stay on segment
4. Calculate distance to closest point on segment
```

**Mathematics:**
```
t = dot(P - P1, P2 - P1) / ||P2 - P1||²
t_clamped = max(0, min(1, t))
closest_point = P1 + t_clamped * (P2 - P1)
distance = ||P - closest_point||
```

---

## Pattern Reuse Logic

### Why Reuse Patterns?
**Scientific Rationale:** To test the effect of connectedness on numerosity judgment, we need to control for dot placement. If we generate new dot configurations for each connectedness level, differences could be due to:
- Dot clustering
- Spatial distribution
- Accidental gestalts

By reusing the same dots, we isolate the effect of connectedness.

### Implementation: `generate_pattern_set(num_dots_test)`

```
# 1. Generate base pattern with 0 connections
base_pattern = DotPattern(num_dots_test, connectedness=0)
base_pattern.generate()  # Creates dots AND lines

# 2. Copy the dot configuration
base_dots = base_pattern.copy_dots()  # Deep copy

# 3. Create 1-connection pattern with SAME dots
pattern_1conn = DotPattern(num_dots_test, connectedness=1, base_dots=base_dots)
pattern_1conn.generate()  # Reuses dots, generates different lines

# 4. Create 2-connection pattern with SAME dots
pattern_2conn = DotPattern(num_dots_test, connectedness=2, base_dots=base_dots)
pattern_2conn.generate()  # Reuses dots, generates different lines
```

**Key Point:** The `base_dots` parameter in `__init__()` allows patterns to share dot configurations while generating different line arrangements.

---

## Display Functions

### `create_pattern_stimulus(pattern, offset_x)`
Renders a pattern to an Expyriment Canvas:
1. Creates canvas at specified horizontal offset
2. Plots all dots as circles (6px radius)
3. Plots all lines (5px width)
4. Returns canvas ready for display

### `create_labeled_pattern(pattern, offset_x, label_text)`
Same as above but adds:
- Pattern background rectangle
- Text label below pattern
- Extra vertical space for label

### `flash_patterns(exp, left_canvas, right_canvas, fixation_cross)`
Presentation sequence:
1. Show fixation cross (500ms)
2. Show both patterns (200ms)
3. Show blank screen
4. Wait for response

---

## Trial Flow

```
1. Show title screen
2. Show patterns with labels (unlimited viewing time)
3. User presses SPACE
4. Show fixation cross (500ms)
5. Flash patterns (200ms)
6. Patterns disappear
7. Wait for user to press SPACE to continue
```

---

## Configuration Constants

### Pattern Geometry
- `PATTERN_WIDTH = 280` pixels
- `PATTERN_HEIGHT = 360` pixels
- `HEMIFIELD_OFFSET = 220` pixels from center

### Dot Constraints
- `DOT_DIAMETER = 12` pixels
- `MIN_DOT_DISTANCE = 42` pixels (center-to-center)
- `MIN_DOT_BOUNDARY_DISTANCE = 20` pixels from edge

### Line Constraints
- `LINE_WIDTH = 5` pixels
- `MIN_LINE_LENGTH = 30` pixels
- `MAX_LINE_LENGTH = 60` pixels
- `MIN_LINE_DOT_DISTANCE = 12` pixels
- `MIN_LINE_SEPARATION = 8` pixels (NEW - prevents near-misses)

### Experimental Parameters
- `NUM_REFERENCE_DOTS = 12`
- `NUM_LINES = 4` (always 4 lines per pattern)

---

## Usage

```bash
python experiment_presentation.py
```

The script will:
1. Generate practice patterns (9 vs 12 dots)
2. Generate demonstration patterns (12, 13, 14 dots with 0, 1, 2 connections)
3. Show practice trials
4. Show examples of each connectedness level
5. Allow unlimited viewing time for each example

---

## Code Architecture

```
DotPattern class
├── __init__()              # Initialize with base_dots option
├── generate()              # Main generation entry point
├── copy_dots()             # Deep copy for reuse
├── _generate_dots()        # Place dots with constraints
├── _generate_lines()       # Orchestrate line generation
├── _generate_connecting_lines()    # Lines between dots
├── _generate_free_lines()          # Floating lines
├── _line_crosses_others()          # Check all crossings
├── _lines_intersect()              # Parametric intersection
├── _line_too_close_to_other_lines() # NEW: Proximity check
├── _line_too_close_to_dots()       # Distance to dots
├── _line_too_close_to_other_dots() # Distance to unconnected dots
└── _point_to_segment_distance()    # Geometric calculation

Stimulus Functions
├── create_pattern_stimulus()    # Basic pattern canvas
├── create_labeled_pattern()     # Pattern with text label
├── flash_patterns()             # Timed presentation
└── show_patterns_extended()     # Unlimited viewing

Pattern Generation
├── generate_pattern_set()       # Creates reused dot configs
└── run_presentation()           # Main demo flow
```

---
