# Test Version - Quick Verification Script

## Overview
`experiment1_TEST_VERSION.py` is a streamlined version of the full experiment designed for rapid testing and verification. It uses the same pattern generation logic but with dramatically reduced trial counts.

## Purpose
- Verify pattern generation works correctly
- Test timing and presentation sequences
- Debug code changes before running full experiment
- Train experimenters on the paradigm
- Check display compatibility

---

## Key Differences from Full Experiment

### Reduced Parameters

| Parameter | Full Version | Test Version |
|-----------|-------------|--------------|
| Test dot numbers | 7 levels (9-15) | 3 levels (9, 12, 15) |
| Connectedness levels | 3 (0, 1, 2) | 2 (0, 2) |
| Patterns per condition | 8 | 2 |
| Blocks | 5 | 1 |
| Practice trials | 30 | 5 |
| **Total trials** | **1,680** | **24** |
| **Duration** | **~90 minutes** | **~3 minutes** |

### Calculation
```
Test version trials:
- Conditions: 3 dot numbers × 2 connectedness = 6
- Patterns: 6 × 2 repetitions = 12
- Counterbalanced: 12 × 2 (left/right) = 24 trials
- Plus 5 practice trials
- Total: 29 trials (~3 minutes)
```

---

## Configuration Changes

### Pattern Settings
```python
# Smaller pattern area for faster generation
PATTERN_WIDTH = 240   # vs 280 in full version
PATTERN_HEIGHT = 320  # vs 360 in full version

# Relaxed dot spacing for faster placement
MIN_DOT_DISTANCE = 38  # vs 42 in full version
MIN_DOT_BOUNDARY_DISTANCE = 10  # vs 20 in full version

# Thinner lines for faster rendering
LINE_WIDTH = 2  # vs 5 in full version
```

### Experimental Parameters
```python
TEST_DOT_NUMBERS = [9, 12, 15]  # Only 3 levels
CONNECTEDNESS_LEVELS = [0, 2]   # Only 0 and 2 connections
PATTERNS_PER_CONDITION = 2      # Only 2 repetitions
NUM_BLOCKS = 1                  # Single block
NUM_PRACTICE_TRIALS = 5         # Quick practice
```


## Same Core Logic as Full Experiment
### 1. Pattern Reuse
**The test version uses the SAME pattern reuse logic:**

```
for num_dots in [9, 12, 15]:
    for rep in range(2):
        # Generate base with 0 connections
        base = DotPattern(num_dots, 0)
        base.generate()
        
        # Reuse dots for 2 connections
        dots = base.copy_dots()
        pattern_2conn = DotPattern(num_dots, 2, base_dots=dots)
        pattern_2conn.generate()
```

**Result:** 6 unique dot configurations, each used twice (0 and 2 connections) = 12 patterns

### 2. Line Generation
**Identical constraint checking:**
- ✓ Line intersection detection
- ✓ Line proximity checking (`MIN_LINE_SEPARATION`)
- ✓ Dot distance constraints
- ✓ Boundary checking

### 3. Trial Structure
**Same counterbalancing:**
```
# First half: Random left/right
for pattern in patterns:
    test_on_left = random.choice([True, False])

# Second half: Opposite side
for pattern in patterns:
    test_on_left = !first_half_choice
```

### 4. Timing
**Identical presentation:**
- ITI: 500-1000ms (random)
- Fixation: displayed before stimulus
- Stimulus: 200ms
- Response: self-paced


### Expected Output
```
TEST MODE: 24 trials per block
Generating TEST patterns with dot reuse...
Generating 12 reference patterns...
Generating test patterns with SAME dots across connectedness...
Pattern generation complete!
  Reference: 12, Test: 12
```

### Experiment Flow
1. **Instructions:** Brief explanation
2. **Practice:** 5 easy trials
3. **Main trials:** 24 trials (with halfway break)
4. **Completion:** Thank you screen

## Converting Test to Full Experiment
To convert test version to full experiment settings:

```
# Change these lines:
TEST_DOT_NUMBERS = [9, 10, 11, 12, 13, 14, 15]  # All 7 levels
CONNECTEDNESS_LEVELS = [0, 1, 2]                 # All 3 levels
PATTERNS_PER_CONDITION = 8                       # Full repetitions
NUM_BLOCKS = 5                                   # All blocks
NUM_PRACTICE_TRIALS = 30                         # Full practice

# And pattern size:
PATTERN_WIDTH = 280
PATTERN_HEIGHT = 360
LINE_WIDTH = 5
MIN_DOT_DISTANCE = 42
MIN_DOT_BOUNDARY_DISTANCE = 20
```