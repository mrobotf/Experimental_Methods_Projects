# Experiment 1: Connectedness & Numerosity - Technical Documentation

## Overview
`experiment1_connectedness.py` is the full experimental implementation testing how connectedness affects dot numerosity judgment, based on He et al. (2009).

## Research Question
**Does visual connectedness bias numerosity perception?**  
Hypothesis: Connected dots are perceived as fewer in number than unconnected dots.

---

## Key Improvements in This Version

### 1. Fixed Line Crossing Issues
- Added `MIN_LINE_SEPARATION = 8px` to prevent near-miss crossings
- Implemented `_line_too_close_to_other_lines()` method
- Enhanced intersection detection with stricter bounds (0.01-0.99 instead of 0-1)

### 2. Pattern Reuse Across Connectedness Levels
**Critical Design Feature:** Each unique dot configuration is used for ALL three connectedness levels (0, 1, 2 connections).

**Why This Matters:**
- Isolates the effect of connectedness from spatial configuration effects
- Controls for accidental clustering or gestalts
- Ensures any differences are due to connections, not dot placement

**Implementation:**
```python
# Generate 56 unique dot configurations (7 dot numbers × 8 repetitions)
for num_dots in [9, 10, 11, 12, 13, 14, 15]:
    for repetition in range(8):
        # Create base with 0 connections
        base = DotPattern(num_dots, 0)
        base.generate()
        
        # Copy dots for other levels
        dots = base.copy_dots()
        pattern_1conn = DotPattern(num_dots, 1, base_dots=dots)
        pattern_2conn = DotPattern(num_dots, 2, base_dots=dots)
        
# Result: 56 × 3 = 168 patterns (same 56 dot configs used 3 times)
```

---

## Experimental Design

### Factors
- **Test dots:** 7 levels (9, 10, 11, 12, 13, 14, 15)
- **Connectedness:** 3 levels (0, 1, 2 pairs connected)
- **Repetitions:** 8 unique patterns per condition
- **Total conditions:** 7 × 3 = 21
- **Total test patterns:** 21 × 8 = 168

### Reference Stimuli
- Always 12 dots
- Always 0 connections
- 168 unique reference patterns (one per test pattern)

### Trial Structure
Each pattern shown twice (left/right counterbalanced):
- Block: 168 × 2 = 336 trials
- Full experiment: 336 × 5 blocks = 1,680 trials
- Plus 30 practice trials

---

## Pattern Generation with Reuse

### `generate_all_patterns()` Function

#### Step 1: Generate Reference Patterns
```python
for i in range(168):
    ref = DotPattern(12, connectedness=0)
    ref.generate()
    reference_patterns.append(ref)
```

#### Step 2: Generate Test Patterns with Reuse
```python
test_patterns_by_connectivity = {0: [], 1: [], 2: []}

for num_dots in [9, 10, 11, 12, 13, 14, 15]:
    for rep in range(8):
        # Generate base (0 connections)
        base = DotPattern(num_dots, 0)
        base.generate()
        test_patterns_by_connectivity[0].append(base)
        
        # Reuse dots for 1 connection
        dots = base.copy_dots()
        p1 = DotPattern(num_dots, 1, base_dots=dots)
        p1.generate()
        test_patterns_by_connectivity[1].append(p1)
        
        # Reuse dots for 2 connections
        p2 = DotPattern(num_dots, 2, base_dots=dots)
        p2.generate()
        test_patterns_by_connectivity[2].append(p2)
```

#### Step 3: Interleave Patterns
```python
# Interleave to create final list
test_patterns = []
for i in range(56):  # 56 unique dot configs
    for conn in [0, 1, 2]:
        test_patterns.append(test_patterns_by_connectivity[conn][i])

# Result: [pattern_0_0conn, pattern_0_1conn, pattern_0_2conn, 
#          pattern_1_0conn, pattern_1_1conn, pattern_1_2conn, ...]
```

**Key Insight:** Indices 0, 1, 2 have the same dots. Indices 3, 4, 5 have the same dots. And so on.

---

## Line Generation Logic

### Connecting Lines
Lines that connect pairs of dots:

```
Constraints:
- Length: 30-60 pixels (MIN_LINE_LENGTH to MAX_LINE_LENGTH)
- Each dot used at most once
- Cannot cross other lines
- Cannot come within 8px of other lines (NEW)
- Cannot come within 12px of unconnected dots
```

**Algorithm:**
1. Shuffle available dot indices
2. Take first available dot
3. Search through remaining dots for valid partner:
   - Distance in 30-60px range
   - Line passes all constraints
4. If found, mark both dots as used
5. If not found after 1000 attempts, try next dot
6. Continue until required connections made

### Free-Hanging Lines
Lines that float in space (not connecting dots):

```
Constraints:
- Length: 30-60 pixels
- Both endpoints within pattern bounds
- Cannot cross other lines
- Cannot come within 8px of other lines (NEW)
- Cannot come within 12px of ANY dot
```

**Algorithm:**
1. Generate random start point
2. Generate random angle and length
3. Calculate end point
4. Check all constraints
5. If valid, add line
6. Retry up to 2000 times if invalid

---

## Constraint Checking (Detailed)

### 1. Line Intersection Detection (`_lines_intersect()`)

**Parametric Line Equation Method:**
```
Line 1: P = P1 + t(P2 - P1)  where t ∈ [0, 1]
Line 2: P = P3 + u(P4 - P3)  where u ∈ [0, 1]

Set equal and solve:
P1 + t(P2 - P1) = P3 + u(P4 - P3)

Solve for t and u:
t = [(x1-x3)(y3-y4) - (y1-y3)(x3-x4)] / [(x1-x2)(y3-y4) - (y1-y2)(x3-x4)]
u = -[(x1-x2)(y1-y3) - (y1-y2)(x1-x3)] / [(x1-x2)(y3-y4) - (y1-y2)(x3-x4)]

Lines intersect if: 0.01 < t < 0.99 AND 0.01 < u < 0.99
```

**Why 0.01-0.99 instead of 0-1?**
- Prevents endpoint touching from counting as intersection
- Provides small buffer zone
- More visually clean results

### 2. Line Proximity Check (`_line_too_close_to_other_lines()`)

**NEW METHOD - Prevents near-misses:**
```python
For new_line and each existing_line:
    Calculate 4 distances:
    1. Distance from new_line.start to existing_line
    2. Distance from new_line.end to existing_line
    3. Distance from existing_line.start to new_line
    4. Distance from existing_line.end to new_line
    
    If min(distances) < MIN_LINE_SEPARATION:
        return True  # Too close!
```

**Why This Works:**
- Checks proximity at endpoints (most likely points of near-miss)
- Catches cases where lines run parallel
- Prevents visual ambiguity

### 3. Point-to-Segment Distance (`_point_to_segment_distance()`)

**Vector Projection Method:**
```
Given: Point P, Line segment from A to B

Step 1: Project P onto infinite line through A-B
  v = B - A  (line direction vector)
  w = P - A  (vector from A to P)
  t = dot(w, v) / dot(v, v)

Step 2: Clamp to segment
  t_clamped = max(0, min(1, t))
  
Step 3: Find closest point
  closest = A + t_clamped * v
  
Step 4: Calculate distance
  distance = ||P - closest||
```

**Special Cases:**
- If t < 0: Closest point is A (start)
- If t > 1: Closest point is B (end)
- If 0 ≤ t ≤ 1: Closest point is on segment

---

## Trial Organization

### Block Structure
```
1 Block = 336 trials
  = 168 patterns × 2 presentations (left/right counterbalanced)
  
Each pattern appears exactly twice per block:
  - Once with test on left
  - Once with test on right
```

### Trial Creation (`create_trial_list()`)
```python
# First half: Random order
indices = shuffle(0 to 167)
for idx in indices:
    create_trial(test_on_left=random)

# Second half: Opposite side
for idx in indices:
    create_trial(test_on_left=opposite_of_first_half)
```

**Result:** Complete counterbalancing within each block.

### Practice Trials
- 30 trials with easy discrimination (9 vs 12 dots)
- All with 0 connections
- Familiarizes participants with task and timing

---

## Trial Execution (`run_trial()`)

### Timing Sequence
```
1. Inter-trial interval (ITI): 500-1000ms (random)
2. Fixation cross: displayed
3. Stimulus presentation: 200ms
4. Blank screen: until response
5. Response collection: self-paced
6. Data logging: immediate
```

### Stimulus Presentation
```python
# 1. Determine left/right placement
if test_on_left:
    left_pattern = test
    right_pattern = reference
else:
    left_pattern = reference
    right_pattern = test

# 2. Pre-load for precise timing
left_canvas = create_pattern_stimulus(left_pattern, -220)
right_canvas = create_pattern_stimulus(right_pattern, 220)
left_canvas.preload()
right_canvas.preload()

# 3. Create display
display = BlankScreen()
left_canvas.plot(display)
right_canvas.plot(display)

# 4. Present for exactly 200ms
display.present()
exp.clock.wait(200)

# 5. Blank until response
blank.present()
```

**Why Pre-load?**
- Ensures exact 200ms presentation
- Prevents rendering lag
- Maintains temporal precision

---

## Data Collection

### Variables Logged per Trial
```
1. block           - Block number (1-5)
2. half            - Trial half (1 or 2)
3. num_dots        - Number of dots in test pattern
4. connectedness   - Number of connected pairs (0, 1, or 2)
5. test_on_left    - Boolean: True if test on left
6. chose_left      - Boolean: True if left chosen
7. chose_test      - Boolean: True if test chosen
8. rt              - Response time in milliseconds
```

### Data Analysis Considerations
- **Accuracy:** `chose_test` when `num_dots > 12`, `!chose_test` when `num_dots < 12`
- **Bias:** Compare `chose_test` rates across connectedness levels
- **Expected effect:** Higher connectedness → lower `chose_test` rate (perceive as fewer)

---

## Configuration Constants

### Display
- `SCREEN_SIZE = (1024, 768)`
- `BACKGROUND_COLOR = (0, 0, 0)` black
- `HEMIFIELD_OFFSET = 220px` from center

### Pattern Geometry
- `PATTERN_WIDTH = 280px`
- `PATTERN_HEIGHT = 360px`
- `PATTERN_COLOR = (102, 102, 102)` gray

### Dot Constraints
- `DOT_DIAMETER = 12px`
- `MIN_DOT_DISTANCE = 42px` (matches paper)
- `MIN_DOT_BOUNDARY_DISTANCE = 20px`

### Line Constraints
- `LINE_WIDTH = 5px`
- `MIN_LINE_LENGTH = 30px`
- `MAX_LINE_LENGTH = 60px`
- `MIN_LINE_DOT_DISTANCE = 12px`
- `MIN_LINE_SEPARATION = 8px` (NEW)

### Timing
- `STIMULUS_DURATION = 200ms`
- `MIN_ITI = 500ms`
- `MAX_ITI = 1000ms`

---

## Usage

```bash
python experiment1_connectedness.py
```

### Experiment Flow
1. **Instructions:** Task explanation
2. **Practice:** 30 easy trials (9 vs 12 dots)
3. **Main experiment:** 5 blocks × 336 trials
   - Progress feedback every 50 trials
   - Break between blocks
4. **Completion:** Thank you screen

### Estimated Duration
- Practice: ~3-5 minutes
- Each block: ~15-20 minutes
- Total: ~90-100 minutes (with breaks)

---

## Error Handling

### Pattern Generation Failures
```python
for retry in range(10):
    try:
        pattern.generate()
        break
    except RuntimeError:
        if retry == 9:
            print(f"Failed after 10 attempts")
            raise
        continue
```

**Common Failure Reasons:**
1. Not enough space for dots (increase pattern size or decrease `MIN_DOT_DISTANCE`)
2. No valid connecting line pairs (increase `MAX_LINE_LENGTH`)
3. Too many line constraints (decrease `MIN_LINE_SEPARATION`)

### Experiment Interruption
- Expyriment automatically saves data on crash
- Data file: `[experiment_name]_[subject_id]_[timestamp].xpd`
- Can resume from last completed block

---

## Data Analysis Pipeline

### Expected Data File Structure
```
Column 1: block (1-5)
Column 2: half (1-2)
Column 3: num_dots (9-15)
Column 4: connectedness (0-2)
Column 5: test_on_left (True/False)
Column 6: chose_left (True/False)
Column 7: chose_test (True/False)
Column 8: rt (milliseconds)
```

### Key Analyses
1. **Point of Subjective Equality (PSE):** Fit psychometric curves per connectedness level
2. **Bias Effect:** Compare PSEs across connectedness levels
3. **Response Time:** Check for speed-accuracy tradeoffs
4. **Learning Effects:** Compare early vs. late blocks

---

## Troubleshooting

**Q: Pattern generation takes too long**
- Decrease `max_attempts` in retry loops
- Relax some constraints (e.g., `MIN_LINE_SEPARATION`)
- Use smaller `PATTERNS_PER_CONDITION`

**Q: Participants report difficulty seeing patterns**
- Increase `STIMULUS_DURATION` beyond 200ms
- Increase `DOT_DIAMETER`
- Increase `LINE_WIDTH`

**Q: Lines still appear to cross**
- Increase `MIN_LINE_SEPARATION` to 10-12px
- Check if display scaling is distorting lines

**Q: Experiment too long**
- Reduce `NUM_BLOCKS` from 5 to 3
- Reduce `PATTERNS_PER_CONDITION` from 8 to 6

---

## Code Architecture

```
Main Flow
├── run_experiment()
│   ├── generate_all_patterns()        # Pre-generate all stimuli
│   ├── create_practice_trials()       # Easy discrimination practice
│   ├── [5 blocks]
│   │   ├── create_trial_list()        # Shuffle + counterbalance
│   │   └── [336 trials]
│   │       └── run_trial()            # Present + collect response
│   └── control.end()

Pattern Generation
├── generate_all_patterns()
│   ├── [168 reference patterns]      # 12 dots, 0 connections
│   └── [168 test patterns]           # Reuse 56 dot configs × 3 levels
│       ├── Generate base (0 conn)
│       ├── Copy dots → 1 connection
│       └── Copy dots → 2 connections

DotPattern Class
├── __init__(num_dots, connectedness, base_dots=None)
├── generate()                         # Main entry
│   ├── _generate_dots()              # Place dots (if base_dots is None)
│   └── _generate_lines()             # Add lines
│       ├── _generate_connecting_lines()    # Connect dot pairs
│       └── _generate_free_lines()          # Floating lines
├── copy_dots()                        # Deep copy for reuse
└── [Constraint checking methods]
    ├── _lines_intersect()            # Parametric intersection
    ├── _line_too_close_to_other_lines()  # NEW: Proximity check
    ├── _line_too_close_to_dots()
    ├── _line_too_close_to_other_dots()
    └── _point_to_segment_distance()
```

---

## Scientific Validity Checklist

✓ **Controlled dot configurations:** Same dots across connectedness levels  
✓ **No visual artifacts:** Lines don't cross or overlap  
✓ **Precise timing:** 200ms stimulus presentation  
✓ **Complete counterbalancing:** Left/right position balanced  
✓ **Sufficient power:** 8 repetitions × 5 blocks = 40 observations per condition  
✓ **Practice trials:** Familiarization with task  
✓ **Random ITI:** Prevents temporal expectation  
✓ **Paper compliance:** Matches He et al. (2009) specifications  

---

## References

He, L., Zhang, J., Zhou, T., & Chen, L. (2009). Connectedness affects dot numerosity judgment: Implications for configural processing. *Psychonomic Bulletin & Review, 16*(3), 509-517.
