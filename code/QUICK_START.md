# QUICK START GUIDE
## Experiment 1: Connectedness Affects Dot Numerosity

### 🚀 Getting Started (3 Steps)

#### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Run Test Version (2-3 minutes)
```bash
python experiment1_TEST_VERSION.py
```

This will verify everything works with a quick 24-trial test.

#### Step 3: Run Full Experiment (~1 hour)
```bash
python experiment1_connectedness.py
```

---

## ✅ What Was Fixed from Your Error

### Problem
```
RuntimeError: Could not place dot 14/14
```

### Solution
1. **Increased pattern size**: 160×240 → 240×320 pixels
2. **Reduced spacing**: 42px → 38px (still maintains good separation)
3. **Added retry mechanism**: Automatically retries up to 10 times if generation fails
4. **Created test version**: Quick validation before running full experiment

### Why This Happened
The paper's specifications (160×240 pixels, 42-pixel minimum spacing) create a challenging packing problem. With 15 dots and all the constraints:
- Minimum 42px between dots
- Minimum 10px from edges  
- Random distribution required
- Lines must not cross
- Lines must avoid dots

...there's simply not enough space. Our adjustments maintain the experiment's validity while making it technically feasible.

---

## 📁 Files You Received

| File | Purpose |
|------|---------|
| `experiment1_connectedness.py` | **Full experiment** - 1,680 trials, ~1 hour |
| `experiment1_TEST_VERSION.py` | **Quick test** - 24 trials, ~3 minutes |
| `requirements.txt` | Python dependencies |
| `README.md` | Detailed documentation |
| `QUICK_START.md` | This file |

---

## 🎯 What the Experiment Does

### Design
- **Task**: Judge which of two briefly-flashed dot patterns has MORE dots
- **Manipulation**: Some dots connected by lines (0, 1, or 2 pairs)
- **Hypothesis**: Connected dots = perceived as objects = underestimation
- **Controls**: Always 4 lines total (some connecting, some free)

### Trial Structure
1. Fixation cross (green, center)
2. Random delay (500-1000ms)
3. **FLASH** both patterns (200ms) ← too fast to count
4. Blank screen
5. Response: LEFT or RIGHT arrow
6. No feedback

### Full Experiment
- 30 practice trials (easy: 9 vs 12 dots)
- 5 blocks × 336 trials = **1,680 total trials**
- Brief breaks between blocks
- **Duration**: ~60 minutes

### Test Version
- 5 practice trials
- 1 block × 24 trials = **24 total trials**
- **Duration**: ~3 minutes

---

## 📊 Data Output

Automatically saved to: `data/Connectedness_Numerosity_Exp1_XX.xpd`

Format:
```
block | half | num_dots | connectedness | test_on_left | chose_left | chose_test | rt
```

### To Analyze (not included)
1. Calculate proportion "test has more" per condition
2. Fit psychometric curves (cumulative Gaussian)
3. Extract PSE (Point of Subjective Equality)
4. Expected result: PSE increases with more connections

---

## ⚙️ Customization

### Quick Adjustments
Edit these constants at the top of the script:

```python
# Make experiment shorter for testing
NUM_BLOCKS = 2  # instead of 5
PATTERNS_PER_CONDITION = 4  # instead of 8

# Adjust timing
STIMULUS_DURATION = 150  # instead of 200ms

# Change spacing if still getting errors
MIN_DOT_DISTANCE = 35  # instead of 38
```

### Pattern Size
If you need to match the paper exactly (160×240), you'll need to:
1. Reduce `MAX_DOT_NUMBERS` from 15 to 13
2. Or use smaller dots
3. Or accept occasional generation failures

---

## 🐛 Common Issues

### Issue: Pattern generation takes forever
**Solution**: This is normal! Generating 336 patterns with constraints takes 1-2 minutes. Progress is shown.

### Issue: Black screen, nothing appears
**Solution**: 
- Check screen resolution (should support 1024×768)
- Verify Expyriment is installed correctly
- Try test version first

### Issue: Timing seems off
**Solution**:
- Check monitor refresh rate (60Hz recommended)
- Expyriment will warn if timing is imprecise
- 200ms = ~12 frames at 60Hz

### Issue: Can't see the gray patterns
**Solution**:
- Pattern color is RGB (102, 102, 102) - medium gray
- Background is RGB (0, 0, 0) - pure black
- If contrast is low, adjust `PATTERN_COLOR`

---

## 📖 Theory Behind the Experiment

### Research Question
Does connecting dots with lines affect perceived numerosity?

### Hypothesis
When dots are connected:
1. They form unified perceptual objects
2. Visual system counts OBJECTS not ELEMENTS
3. Fewer objects perceived → numerosity underestimated

### Predicted Results
- 0 connections: PSE ≈ 12 (accurate)
- 1 connection: PSE ≈ 12.6 (slight underestimation)
- 2 connections: PSE ≈ 13.5 (larger underestimation)

PSE = "Point of Subjective Equality" = number of dots that LOOKS like 12

If PSE = 13.5, participant needs 13.5 actual dots to perceive "equal to 12" → ~1.5 dots underestimated

---

## 🎓 Citation

Based on:

He, L., Zhang, J., Zhou, T., & Chen, L. (2009). Connectedness affects dot numerosity judgment: Implications for configural processing. *Psychonomic Bulletin & Review, 16*(3), 509-517.

---

## ❓ Questions?

### Pattern Generation
Q: Why does it take so long?  
A: Creating 336 unique patterns with all constraints requires checking thousands of random configurations.

Q: Can I speed it up?  
A: Reduce `PATTERNS_PER_CONDITION` or use the test version.

### Experiment Design
Q: Why 200ms presentation?  
A: Too short to count, long enough to perceive the pattern clearly.

Q: Why counterbalance positions?  
A: Eliminates any left/right spatial bias in responses.

Q: Why no feedback?  
A: Prevents learning effects that would confound results.

### Technical
Q: Can I run this on a laptop screen?  
A: Yes, as long as resolution is 1024×768 or higher.

Q: Does it work on Mac/Linux?  
A: Yes! Expyriment is cross-platform.

---

## 🎉 You're Ready!

1. ✅ Install dependencies
2. ✅ Run test version
3. ✅ Check that patterns display correctly
4. ✅ Run full experiment
5. ✅ Analyze your data

Good luck with your experiment! 🧪
