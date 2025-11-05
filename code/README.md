# Connectedness & Numerosity Experiment Suite

## Overview
Three Python scripts investigating how visual connectedness affects dot quantity perception.

**Research Question:** Do connected dots appear less numerous than unconnected dots?

---

## Files

| Script | Duration | Trials | Use |
|--------|----------|--------|-----|
| **experiment_presentation.py** | 5 min | ~10 | Demo/training |
| **experiment1_TEST_VERSION.py** | 3 min | 24 | Testing/debugging |
| **experiment1_connectedness.py** | 90 min | 1,680 | Full data collection |

---

## Quick Start

```bash
pip install expyriment
python experiment1_TEST_VERSION.py    # Test setup
python experiment_presentation.py     # Show demo (optional)
python experiment1_connectedness.py   # Run experiment
```

---

## Pattern Generation

### Core Principle: Dot Reuse

Same dot positions used across all connectedness levels. Only lines change.

```python
# Step 1: Generate base dots (0 connections)
base_pattern = DotPattern(9, connectedness=0)
base_pattern.generate()

# Step 2: Copy dots for reuse
base_dots = base_pattern.copy_dots()

# Step 3: Create variants with SAME dots
pattern_1conn = DotPattern(9, connectedness=1, base_dots=base_dots)
pattern_2conn = DotPattern(9, connectedness=2, base_dots=base_dots)
```

**Why?** Ensures differences are from connectedness, not dot arrangement.

---

## Constraints

### Dot Placement
- Min 38px between dots
- Min 10px from edges
- Max 10,000 attempts per dot

### Lines
- Length: 30-60px
- Cannot cross other lines
- Min 8px from other lines
- Min 12px from dots

Each pattern has **4 total lines**:
- Connectedness 0: 0 connecting + 4 free
- Connectedness 1: 1 connecting + 3 free  
- Connectedness 2: 2 connecting + 2 free

---

## Retry Logic

"All or nothing" approach: if ANY pattern fails, discard ALL and retry with new dots.

```python
for retry in range(10):
    try:
        base_pattern.generate()      # 0 connections
        pattern_1conn.generate()     # 1 connection
        pattern_2conn.generate()     # 2 connections
        
        # Add only if ALL succeeded
        patterns.append(base_pattern, pattern_1conn, pattern_2conn)
        break
        
    except RuntimeError:
        continue  # Try new dots
```

Max 10 retries, then crash.

---

## Key Algorithms

### 1. Distance Between Points
```python
distance = √((x2-x1)² + (y2-y1)²)
```

### 2. Line Intersection (Parametric)
```python
denom = (x1-x2)×(y3-y4) - (y1-y2)×(x3-x4)
t = ((x1-x3)×(y3-y4) - (y1-y3)×(x3-x4)) / denom
u = -((x1-x2)×(y1-y3) - (y1-y2)×(x1-x3)) / denom

intersect = (0.01 < t < 0.99) AND (0.01 < u < 0.99)
```

### 3. Point-to-Line Distance
```python
t = ((px-x1)×dx + (py-y1)×dy) / (dx²+dy²)
t = clamp(t, 0, 1)
closest = (x1 + t×dx, y1 + t×dy)
distance = √((px-closest_x)² + (py-closest_y)²)
```

---

## Experimental Design

### Full Experiment
- Test numerosities: 9-15 dots (7 levels)
- Reference: Always 12 dots
- Connectedness: 0, 1, 2 pairs
- Repetitions: 8 patterns per condition
- Blocks: 5
- Total: 1,680 trials

### Data Output

**Standard .xpd file:**
```
trial_number, block, half, num_dots, connectedness, 
test_on_left, chose_left, chose_test, rt_ms
```

**Enhanced JSON file:**
```json
{
  "participant_id": 1,
  "trials": [{
    "test": {
      "num_dots": 9,
      "connectedness": 2,
      "pattern_id": 5,
      "dots": [[x1,y1], [x2,y2], ...],
      "lines": [{"start":[x1,y1], "end":[x2,y2]}, ...],
      "connected_pairs": [[0,3], [1,5]]
    },
    "response": {"chose_test": true, "rt_ms": 1234}
  }]
}
```

---

## Configuration

```python
MIN_DOT_DISTANCE = 38
MIN_LINE_LENGTH = 30
MAX_LINE_LENGTH = 60
MIN_LINE_DOT_DISTANCE = 12
MIN_LINE_SEPARATION = 8
STIMULUS_DURATION = 200  # ms
NUM_LINES = 4
```


## Requirements

- Python 3.7+
- Expyriment 0.10+
- Display: 1024×768 minimum
- Generation time: 30-60 seconds