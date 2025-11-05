# Connectedness & Numerosity Experiment Suite

## Overview
This suite contains three Python scripts for running a numerosity judgment experiment investigating how visual connectedness affects dot quantity perception.

**Research Question:** Do connected dots appear less numerous than unconnected dots?

**Based on:** He, L., Zhang, J., Zhou, T., & Chen, L. (2009). *Connectedness affects dot numerosity judgment: Implications for configural processing.* Psychonomic Bulletin & Review, 16(3), 509-517.

---

## Files in This Suite

### 1. **experiment_presentation.py** 
**Purpose:** Demonstration/preview script  
**Duration:** ~5 minutes  
**Use for:**
- Showing the paradigm to participants before the real experiment
- Training experimenters
- Verifying pattern quality
- Presenting examples of different connectedness levels

---

### 2. **experiment1_connectedness.py**
**Purpose:** Full experimental implementation  
**Duration:** ~90 minutes  
**Trials:** 1,680 (plus 30 practice)  
**Use for:**
- Running the actual data collection
- Testing the connectedness effect hypothesis

---

### 3. **experiment1_TEST_VERSION.py**
**Purpose:** Quick testing/debugging script  
**Duration:** ~3 minutes  
**Trials:** 24 (plus 5 practice)  
**Use for:**
- Verifying code works before running full experiment
- Testing on new computers/displays
- Debugging modifications


---

## Quick Start Guide

### Step 1: Install Dependencies
```bash
pip install expyriment
```

### Step 2: Test Your Setup
```bash
python experiment1_TEST_VERSION.py
```
✓ Runs in ~3 minutes  
✓ Verifies everything works  
✓ Produces sample data file

### Step 3: Show Demonstration (Optional)
```bash
python experiment_presentation.py
```
✓ Shows participants what to expect  
✓ Displays examples of different patterns  
✓ No data collection

### Step 4: Run Full Experiment
```bash
python experiment1_connectedness.py
```
✓ Full 90-minute experiment  
✓ 5 blocks with breaks  
✓ Complete data collection

---

## Major Improvements in This Version

### 🔧 Fixed: Line Crossing Issue
**Problem:** Lines sometimes crossed each other, creating visual ambiguity.

**Solution:** 
- Added `MIN_LINE_SEPARATION` constraint (8 pixels)
- New method: `_line_too_close_to_other_lines()`
- Enhanced intersection detection with stricter bounds (0.01-0.99)

**Result:** Clean, unambiguous stimuli with no crossing lines.

---

### 🔄 Fixed: Pattern Reuse Across Connectedness
**Problem:** Each connectedness level had different dot configurations, confounding the experimental manipulation.

**Solution:**
- Generate base dot configuration once
- Reuse same dots for all connectedness levels (0, 1, 2)
- Only lines differ between conditions

**Scientific Importance:** This isolates the effect of connectedness from spatial configuration effects.

**Example:**
```python
# Pattern ID 0 with same dots:
- 0 connections: ●  ●  ●  ●  —  —  —  —
- 1 connection:  ●—●  ●  ●  —  —  —
- 2 connections: ●—●  ●—●  —  —

# Pattern ID 1 with different dots:
- 0 connections: ●    ●  ●  ●  —  —  —  —
- 1 connection:  ●    ●—●  ●  —  —  —
- 2 connections: ●—●    ●—●  —  —
```

---

## How Pattern Generation Works

### Core Algorithm

#### Step 1: Dot Placement
```
For each dot:
  1. Generate random position
  2. Check constraints:
     - Min 42px from other dots
     - Min 20px from pattern edges
  3. If valid: place dot
  4. Else: retry (max 10,000 attempts)
```

#### Step 2: Connecting Lines
```
For each required connection:
  1. Find pair of unused dots
  2. Check if distance is 30-60 pixels
  3. Check constraints:
     ✓ Doesn't cross other lines
     ✓ Not within 8px of other lines (NEW)
     ✓ Not within 12px of unconnected dots
  4. If valid: add line and mark dots as used
  5. Else: try different pair (max 1,000 attempts)
```

#### Step 3: Free-Hanging Lines
```
For each free line:
  1. Generate random start point
  2. Generate random angle and length (30-60px)
  3. Calculate end point
  4. Check constraints:
     ✓ Both endpoints within bounds
     ✓ Doesn't cross other lines
     ✓ Not within 8px of other lines (NEW)
     ✓ Not within 12px of any dots
  5. If valid: add line
  6. Else: retry (max 2,000 attempts)
```

---

## Pattern Reuse Logic

### Why Reuse Matters

**Without Reuse (BAD):**
```
Pattern A: 12 dots, 0 connections → dots clustered on left
Pattern B: 12 dots, 2 connections → dots spread evenly

Result: Can't tell if difference is due to:
- Connectedness (what we want to measure)
- Spatial clustering (confound)
```

**With Reuse (GOOD):**
```
Pattern A: 12 dots at positions [x1,y1], [x2,y2], ... + 0 connections
Pattern B: SAME 12 dots at SAME positions       + 2 connections

Result: Any difference MUST be due to connectedness!
```

### Implementation

All three scripts use this pattern:

```python
# 1. Generate base dot configuration
base_pattern = DotPattern(num_dots, connectedness=0)
base_pattern.generate()

# 2. Copy dots for reuse
dots = base_pattern.copy_dots()  # Deep copy

# 3. Create variants with different connectedness
pattern_1conn = DotPattern(num_dots, connectedness=1, base_dots=dots)
pattern_1conn.generate()  # Same dots, different lines

pattern_2conn = DotPattern(num_dots, connectedness=2, base_dots=dots)
pattern_2conn.generate()  # Same dots, different lines
```

---

## Constraint Checking Details

### 1. Line Intersection (`_lines_intersect()`)
**Method:** Parametric line equations

```
Line 1: P = P1 + t(P2 - P1)
Line 2: P = P3 + u(P4 - P3)

Solve for t and u. Lines intersect if:
  0.01 < t < 0.99 AND 0.01 < u < 0.99
```

**Why 0.01-0.99?** Prevents endpoint touching from counting as intersection.

### 2. Line Proximity (`_line_too_close_to_other_lines()`)
**NEW METHOD** - Prevents near-misses:

```
For each pair of lines:
  - Calculate 4 endpoint-to-segment distances
  - If min distance < 8px: reject
```

This catches cases where lines run parallel or nearly intersect.

### 3. Point-to-Segment Distance (`_point_to_segment_distance()`)
**Method:** Vector projection

```
1. Project point P onto line AB
2. If projection is between A and B: use it
3. If before A: closest point is A
4. If after B: closest point is B
5. Return distance to closest point
```

---

## Experimental Design

### Full Experiment Parameters
- **Test numerosities:** 7 levels (9, 10, 11, 12, 13, 14, 15 dots)
- **Reference numerosity:** Always 12 dots
- **Connectedness:** 3 levels (0, 1, 2 pairs connected)
- **Repetitions:** 8 unique patterns per condition
- **Blocks:** 5 blocks
- **Total trials:** 7 × 3 × 8 × 5 × 2 = 1,680 trials
- **Duration:** ~90 minutes with breaks

### Data Collection
Each trial logs:
- Block number
- Trial number within block
- Test numerosity
- Connectedness level
- Test position (left/right)
- Response (left/right)
- Whether test was chosen
- Response time (ms)

---

## Usage Recommendations

### For Experimenters

**Before Each Session:**
1. Run test version to verify setup
2. Show presentation to familiarize participant
3. Run full experiment

**During Pilot Testing:**
1. Run test version on multiple computers
2. Check data files are readable
3. Verify patterns look good on your displays
4. Time practice and main blocks
5. Gather participant feedback

### For Development

**When Modifying Code:**
1. Make changes
2. Test with test version (fast feedback)
3. Verify patterns look correct
4. Check data output
5. Run presentation version
6. Only then run full version

**Common Modifications:**
- Adjust timing (`STIMULUS_DURATION`)
- Change pattern size (`PATTERN_WIDTH`, `PATTERN_HEIGHT`)
- Modify constraints (`MIN_DOT_DISTANCE`, `MIN_LINE_SEPARATION`)
- Add/remove trial conditions

---

## Troubleshooting

### Pattern Generation Fails
**Symptoms:** `RuntimeError: Could not place dot...` or `Could not generate line...`

**Solutions:**
1. Increase `max_attempts` in retry loops
2. Relax constraints:
   - Decrease `MIN_DOT_DISTANCE`
   - Decrease `MIN_LINE_SEPARATION`
   - Decrease `MIN_LINE_DOT_DISTANCE`
3. Increase pattern size:
   - Increase `PATTERN_WIDTH`
   - Increase `PATTERN_HEIGHT`

### Lines Still Cross
**Solutions:**
1. Increase `MIN_LINE_SEPARATION` to 10-12 pixels
2. Check display scaling/resolution
3. Save pattern images and inspect visually

### Experiment Too Long
**Solutions:**
1. Reduce blocks: `NUM_BLOCKS = 3`
2. Reduce repetitions: `PATTERNS_PER_CONDITION = 6`
3. Fewer numerosities: `TEST_DOT_NUMBERS = [9, 11, 13, 15]`

### Timing Imprecise
**Solutions:**
1. Use `preload()` on all stimuli (already implemented)
2. Close background applications
3. Use dedicated experimental computer
4. Check CPU usage during experiment

---

## File Structure

```
connectedness_experiment/
├── experiment_presentation.py          # Demo script
├── experiment1_connectedness.py        # Full experiment
├── experiment1_TEST_VERSION.py         # Quick test
├── README_presentation.md              # Presentation docs
├── README_experiment1.md               # Full experiment docs
├── README_test_version.md              # Test version docs
└── README.md                           # This file
```

---

## Data Output

### File Naming
```
[experiment_name]_[subject_id]_[timestamp].xpd
```

Example: `Connectedness_Numerosity_Exp1_001_202411051430.xpd`

### Data Structure
```
Column 1: block           (1-5)
Column 2: half            (1-2 for counterbalancing)
Column 3: num_dots        (9-15)
Column 4: connectedness   (0, 1, or 2)
Column 5: test_on_left    (True/False)
Column 6: chose_left      (True/False)
Column 7: chose_test      (True/False)
Column 8: rt              (milliseconds)
```

### Analysis Example (Python)
```python
import pandas as pd

# Load data
data = pd.read_csv('subject_001.xpd', delimiter='\t')

# Calculate proportion "test has more" by condition
results = data.groupby(['num_dots', 'connectedness'])['chose_test'].mean()

# Plot psychometric curves
import matplotlib.pyplot as plt
for conn in [0, 1, 2]:
    subset = results.xs(conn, level='connectedness')
    plt.plot(subset.index, subset.values, label=f'{conn} connections')
plt.xlabel('Test Numerosity')
plt.ylabel('P(Choose Test)')
plt.legend()
plt.show()
```

---

## Configuration Overview

### Constants Across All Scripts

| Constant | Value | Purpose |
|----------|-------|---------|
| `MIN_DOT_DISTANCE` | 42px | Prevent dot overlap |
| `MIN_DOT_BOUNDARY_DISTANCE` | 20px | Edge padding |
| `MIN_LINE_LENGTH` | 30px | Minimum line length |
| `MAX_LINE_LENGTH` | 60px | Maximum line length |
| `MIN_LINE_DOT_DISTANCE` | 12px | Line-dot clearance |
| `MIN_LINE_SEPARATION` | 8px | Line-line clearance (NEW) |
| `STIMULUS_DURATION` | 200ms | Flash duration |
| `NUM_LINES` | 4 | Lines per pattern |

### Script-Specific Differences

| Parameter | Presentation | Test | Full |
|-----------|-------------|------|------|
| Patterns generated | ~20 | 12 | 168 |
| Trial count | ~10 | 24 | 1,680 |
| Blocks | 1 | 1 | 5 |
| Practice | 0 | 5 | 30 |

---

## Technical Requirements

### Software
- Python 3.7+
- Expyriment 0.10+
- Operating System: Windows, macOS, or Linux

### Hardware
- Display: 1024×768 or higher
- Keyboard with arrow keys
- Dedicated experimental computer recommended
- No touchscreen required

### Performance
- RAM: 512 MB minimum, 2 GB recommended
- CPU: Any modern processor
- Disk: 100 MB free space
- Generation time: 30-60 seconds for full experiment

---

## Citation

If you use this code in your research, please cite:

**Original Paper:**
He, L., Zhang, J., Zhou, T., & Chen, L. (2009). Connectedness affects dot numerosity judgment: Implications for configural processing. *Psychonomic Bulletin & Review, 16*(3), 509-517.

**Code Implementation:**
[Your citation here when published]

---

## License

[Specify your license here]

---

## Support

For questions or issues:
1. Check the detailed README for your specific script
2. Review the troubleshooting sections
3. Verify using test version first
4. [Contact information]

---

## Version History

**v2.0 (Current) - November 2024**
- ✅ Fixed line crossing issue
- ✅ Added line proximity checking
- ✅ Implemented proper pattern reuse across connectedness levels
- ✅ Enhanced documentation
- ✅ Improved error handling

**v1.0 - [Previous Date]**
- Initial implementation
- Known issue: Lines sometimes crossed
- Known issue: No pattern reuse

---

## Summary

This suite provides a complete, scientifically valid implementation of the connectedness-numerosity experiment with:

✓ **Clean stimuli** - No crossing or overlapping lines  
✓ **Controlled design** - Same dots across connectedness levels  
✓ **Precise timing** - 200ms stimulus presentation  
✓ **Complete counterbalancing** - Left/right randomized  
✓ **Comprehensive testing** - Test version for verification  
✓ **Detailed documentation** - README for each script  
✓ **Publication ready** - Matches paper specifications  

Ready to use for data collection or further development!
