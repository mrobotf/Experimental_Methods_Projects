# Experiment 1: Connectedness Affects Dot Numerosity Judgment

Python implementation using Expyriment framework.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Test (Recommended First)

**Try the test version first** to verify everything works:

```bash
python experiment1_TEST_VERSION.py
```

This runs a quick test with:
- Only 5 practice trials (instead of 30)
- Only 24 main trials (instead of 1,680)
- Only 1 block (instead of 5)
- Should complete in ~2-3 minutes

## Running the Full Experiment

```bash
python experiment1_connectedness.py
```

Full experiment takes ~1 hour per participant.

## Implementation Details

### What's Implemented

✅ **Stimulus Generation**
- 168 reference patterns (12 dots, 0 connections, 4 free lines)
- 168 test patterns (3 connectedness × 7 dot numbers × 8 repetitions)
- All geometric constraints from the paper:
  - Dots minimum 42px apart (center-to-center)
  - Dots minimum 10px from boundaries
  - Lines don't cross each other
  - Lines don't extend beyond boundaries
  - Lines >12px from dots (except connecting lines)
  - Connecting lines 30-60px long

✅ **Experimental Procedure**
- 30 practice trials (9 vs 12 dots)
- 5 blocks of 336 trials each
- 200ms stimulus presentation
- Random ITI (500-1000ms)
- Green fixation cross
- Counterbalanced positions (first 168 trials, then reversed)

✅ **Display Settings**
- 1024×768 resolution
- Black background (RGB 0,0,0)
- Gray pattern rectangles (RGB 102,102,102)
- Black dots and lines
- Left/right hemifield presentation

✅ **Data Collection**
- Block number
- Half (1 or 2)
- Number of dots in test
- Connectedness level (0, 1, 2)
- Test position (left/right)
- Response (left/right)
- Chose test pattern (yes/no)
- Response time (ms)

### Key Features

1. **Robust Pattern Generation**: Uses constraint-based generation with retry logic
2. **Collision Detection**: Lines don't cross, proper distance from dots
3. **Counterbalancing**: Second half of each block reverses positions
4. **Progress Indicators**: Shows progress during pattern generation and trials
5. **Break Periods**: Enforced breaks between blocks

### Known Limitations

1. **Pattern Size Adjusted**: The paper specifies 160×240 pixels, but this is too small to fit 15 dots with 42-pixel spacing. We increased to 240×320 pixels and reduced spacing slightly to 38 pixels.
2. **Pattern Generation Time**: ~1-2 minutes to generate all 336 patterns at startup
3. **Retry Mechanism**: Includes automatic retry if pattern generation fails (up to 10 attempts)
4. **No Mirror Flipping**: The paper mentions flipping patterns, but this implementation generates unique patterns instead

### Timing Validation

The 200ms presentation is critical. To validate:
```python
# The script uses expyriment's built-in timing
# Expyriment synchronizes with monitor refresh rate
# For 60Hz monitor: refresh every ~16.67ms
# 200ms = 12 frames (200/16.67 ≈ 12)
```

### File Output

Data is saved automatically by Expyriment to:
```
data/Connectedness_Numerosity_Exp1_XX.xpd
```

Where XX is the subject number.

### Data Analysis

The output file contains:
```
block, half, num_dots, connectedness, test_on_left, chose_left, chose_test, rt
```

To analyze (not included in this script):
1. Calculate proportion "test has more" for each condition
2. Fit cumulative Gaussian psychometric curves
3. Extract PSE (Point of Subjective Equality)
4. Compare PSE across connectedness levels

## Troubleshooting

### "Could not place dot" Error

**Fixed in current version!** The script now:
- Uses larger patterns (240×320 instead of 160×240)
- Reduced spacing slightly (38px instead of 42px)
- Includes automatic retry mechanism (up to 10 attempts)

If you still get this error:
- The random configuration was very unlucky
- Try running again - patterns are randomly generated each time
- Or further reduce `MIN_DOT_DISTANCE` in the script

### Test First!

Always run `experiment1_TEST_VERSION.py` first to verify:
- Pattern generation works
- Stimuli display correctly
- Timing is acceptable
- Controls work properly

### Timing Issues
If 200ms seems too fast/slow:
- Check monitor refresh rate (should be 60Hz)
- Expyriment will print warnings if timing is imprecise
- Consider using a CRT monitor for more precise timing

### Display Issues
If patterns don't look right:
- Check screen resolution (should be 1024×768)
- Verify PATTERN_COLOR (102,102,102) looks gray
- Black background should be RGB (0,0,0)

## Modifications

### Changing Parameters

Edit these constants at the top of the script:

```python
# Make patterns larger
PATTERN_WIDTH = 200
PATTERN_HEIGHT = 300

# Change timing
STIMULUS_DURATION = 150  # ms

# Reduce number of blocks for testing
NUM_BLOCKS = 2
```

### Testing Mode

For quick testing, modify:

```python
# Fewer patterns per condition
PATTERNS_PER_CONDITION = 2  # instead of 8

# Fewer blocks
NUM_BLOCKS = 1  # instead of 5

# Fewer practice trials
NUM_PRACTICE_TRIALS = 5  # instead of 30
```

## References

He, L., Zhang, J., Zhou, T., & Chen, L. (2009). Connectedness affects dot numerosity judgment: Implications for configural processing. *Psychonomic Bulletin & Review, 16*(3), 509-517.
