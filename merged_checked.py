import expyriment
from expyriment import design, control, stimuli
from expyriment.misc.constants import C_BLACK, C_GREEN, K_SPACE, K_LEFT, K_RIGHT
import random
import math
import copy
import itertools
import sys

# -----------------------
# DISPLAY & STIMULUS CONSTANTS
# -----------------------
SCREEN_SIZE = (1024, 768)
BACKGROUND_COLOR = (0, 0, 0)

# Pattern settings
PATTERN_WIDTH = 160
PATTERN_HEIGHT = 240
PATTERN_COLOR = (102, 102, 102)

# Dot settings
DOT_DIAMETER = 12
DOT_COLOR = (0, 0, 0)
MIN_DOT_DISTANCE = 42  # must be at least 42 px apart
MIN_DOT_BOUNDARY_DISTANCE = 10  # must be >=10 px from boundaries

# Line settings
LINE_WIDTH = 2
LINE_COLOR = (0, 0, 0)
MIN_LINE_LENGTH = 30
MAX_LINE_LENGTH = 60
MIN_LINE_DOT_DISTANCE = 12  # lines must be >=12px from any dot except the two connected dots

# Timing
STIMULUS_DURATION = 200  # ms
MIN_ITI = 500
MAX_ITI = 1000

# Experimental settings
NUM_REFERENCE_DOTS = 12
NUM_LINES = 4
TEST_DOT_NUMBERS = [9,10,11,12,13,14,15]
CONNECTEDNESS_LEVELS = [0,1,2]
PATTERNS_PER_CONDITION = 8

NUM_BLOCKS = 5
TRIALS_PER_HALF_BLOCK = 168

NUM_PRACTICE_TRIALS = 30
PRACTICE_TEST_DOTS = 9

HEMIFIELD_OFFSET = 200

# -----------------------
# Geometry helpers
# -----------------------
def distance(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

def lines_intersect(line1, line2):
    (x1,y1),(x2,y2) = line1
    (x3,y3),(x4,y4) = line2
    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(denom) < 1e-10:
        return False
    t = ((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4))/denom
    u = -((x1-x2)*(y1-y3)-(y1-y2)*(x1-x3))/denom
    return 0 < t < 1 and 0 < u < 1

def point_to_segment_distance(point, seg_start, seg_end):
    px,py = point
    x1,y1 = seg_start
    x2,y2 = seg_end
    dx = x2-x1; dy = y2-y1
    if dx == 0 and dy == 0:
        return math.hypot(px-x1, py-y1)
    t = ((px-x1)*dx + (py-y1)*dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    cx = x1 + t*dx; cy = y1 + t*dy
    return math.hypot(px-cx, py-cy)

# -----------------------
# Dot generation
# -----------------------
def generate_dots(n_dots, max_attempts=20000):
    dots = []
    attempts_total = 0
    # Domain for positions: centered at (0,0), coordinates in range [-W/2, W/2]
    min_x = -PATTERN_WIDTH//2 + MIN_DOT_BOUNDARY_DISTANCE
    max_x = PATTERN_WIDTH//2 - MIN_DOT_BOUNDARY_DISTANCE
    min_y = -PATTERN_HEIGHT//2 + MIN_DOT_BOUNDARY_DISTANCE
    max_y = PATTERN_HEIGHT//2 - MIN_DOT_BOUNDARY_DISTANCE

    if min_x > max_x or min_y > max_y:
        raise RuntimeError("Pattern bounds too small for boundary constraints")

    for i in range(n_dots):
        placed = False
        while not placed and attempts_total < max_attempts:
            attempts_total += 1
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)

            # Check min distance from already placed dots
            if all(distance((x,y),d) >= MIN_DOT_DISTANCE for d in dots):
                dots.append((x,y))
                placed = True
        if not placed:
            raise RuntimeError(f"Could not place dot {i+1}/{n_dots} after {max_attempts} attempts")
    return dots

# -----------------------
# Free-line generation (must not intersect other lines, must be >=12px from any dot)
# -----------------------
def generate_free_lines(n_lines, dots, existing_lines=None, max_attempts_per_line=2000):
    if existing_lines is None:
        existing_lines = []
    lines = list(existing_lines)

    for _ in range(n_lines):
        placed = False
        for attempt in range(max_attempts_per_line):
            x1 = random.randint(-PATTERN_WIDTH//2, PATTERN_WIDTH//2)
            y1 = random.randint(-PATTERN_HEIGHT//2, PATTERN_HEIGHT//2)
            angle = random.uniform(0, 2*math.pi)
            length = random.uniform(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
            x2 = x1 + length*math.cos(angle)
            y2 = y1 + length*math.sin(angle)
            # boundary check
            if not (-PATTERN_WIDTH//2 <= x2 <= PATTERN_WIDTH//2 and -PATTERN_HEIGHT//2 <= y2 <= PATTERN_HEIGHT//2):
                continue
            new_line = ((x1,y1),(x2,y2))
            # Must not intersect existing lines
            if any(lines_intersect(new_line, l) for l in lines):
                continue
            # Must be MIN_LINE_DOT_DISTANCE from all dots
            if any(point_to_segment_distance(d, new_line[0], new_line[1]) < MIN_LINE_DOT_DISTANCE for d in dots):
                continue
            lines.append(new_line)
            placed = True
            break
        if not placed:
            raise RuntimeError("Could not place a free line after many attempts")
    return lines

# -----------------------
# Connecting lines generation: connect exact dot centers
# Ensure pair distance in [MIN_LINE_LENGTH, MAX_LINE_LENGTH],
# does not intersect existing lines, and stays >= MIN_LINE_DOT_DISTANCE from other dots (except its endpoints).
# -----------------------
def generate_connecting_lines_from_dots(dots, n_connection, existing_lines=None, max_attempts=2000):
    if existing_lines is None:
        existing_lines = []
    connecting_lines = list(existing_lines)
    connected_pairs = []
    available_indices = set(range(len(dots)))

    # For reproducibility, we will try random pairs but ensure we don't reuse a dot twice
    for _ in range(n_connection):
        placed = False
        attempts = 0
        while attempts < max_attempts and not placed:
            attempts += 1
            if len(available_indices) < 2:
                break
            i1, i2 = random.sample(list(available_indices), 2)
            p1 = dots[i1]; p2 = dots[i2]
            d = distance(p1,p2)
            if not (MIN_LINE_LENGTH <= d <= MAX_LINE_LENGTH):
                continue
            new_line = (p1,p2)
            # no intersection with existing lines
            if any(lines_intersect(new_line, l) for l in connecting_lines):
                continue
            # For other dots, ensure not too close (note: endpoints are fine)
            other_indices = set(range(len(dots))) - {i1,i2}
            too_close = False
            for oi in other_indices:
                if point_to_segment_distance(dots[oi], p1, p2) < MIN_LINE_DOT_DISTANCE:
                    too_close = True
                    break
            if too_close:
                continue
            # Accept
            connecting_lines.append(new_line)
            connected_pairs.append((i1,i2))
            # remove those indices from available to prevent reusing a dot in another connection
            available_indices.remove(i1)
            available_indices.remove(i2)
            placed = True
        if not placed:
            # Can't place this connection — fail and return what we have (caller must handle)
            # We'll not raise: caller may attempt other approach
            break
    return connecting_lines, connected_pairs

# -----------------------
# Utilities for checking pattern equality and mirroring
# -----------------------
def pattern_signature(pattern):
    """A canonical signature to compare patterns: round coords to ints and sort lists"""
    dots = tuple(sorted((int(round(x)), int(round(y))) for x,y in pattern['dots']))
    lines = tuple(sorted(((int(round(l[0][0])),int(round(l[0][1]))),(int(round(l[1][0])),int(round(l[1][1])))) for l in pattern['lines']))
    return (dots, lines)

def mirror_pattern(pattern):
    """Mirror pattern horizontally (x -> -x) keeping dots/lines same relative positions."""
    mirrored = {
        'dots': [(-x,y) for x,y in pattern['dots']],
        'lines': [((-l[0][0], l[0][1]), (-l[1][0], l[1][1])) for l in pattern['lines']],
        'pairs': [( (len(pattern['dots'])-1 - a), (len(pattern['dots'])-1 - b)) for (a,b) in pattern.get('pairs',[]) ],
        'n_dots': pattern['n_dots'],
        'n_connection': pattern['n_connection']
    }
    return mirrored

# -----------------------
# Pattern generation top-level:
# Strategy:
# - Create a pool of unique 0-connected base patterns (reference/test base)
# - For each base 0-connected pattern, create derived patterns:
#     * 0-connected (base)
#     * 1-connected: replace exactly one free line by a connecting line between an eligible pair of dots
#     * 2-connected: replace exactly two free lines by two connecting lines (non-overlapping, eligible pairs)
# - For each pattern, also generate mirrored version (x->-x)
# - Ensure uniqueness across produced patterns and produce PATTERNS_PER_CONDITION distinct ones per condition.
# -----------------------
def generate_all_reference_patterns():
    """Generate TRIALS_PER_HALF_BLOCK reference patterns (0-connected), guaranteeing uniqueness."""
    unique_patterns = []
    signatures = set()
    attempts = 0
    while len(unique_patterns) < TRIALS_PER_HALF_BLOCK:
        attempts += 1
        if attempts > TRIALS_PER_HALF_BLOCK * 1000:
            raise RuntimeError("Too many attempts to generate unique reference patterns; loosen constraints.")
        # generate dots and free lines
        try:
            dots = generate_dots(NUM_REFERENCE_DOTS)
            lines = generate_free_lines(NUM_LINES, dots)
        except RuntimeError:
            continue
        p = {
            'dots': dots,
            'lines': lines,
            'pairs': [],
            'n_dots': NUM_REFERENCE_DOTS,
            'n_connection': 0
        }
        sig = pattern_signature(p)
        if sig in signatures:
            continue
        signatures.add(sig)
        unique_patterns.append(p)
    return unique_patterns

def replace_free_lines_with_connecting(dots, free_lines, n_connections):
    """
    Attempt to replace n_connections of free_lines with connecting lines between dot centers.
    Returns new_lines, connected_pairs if success, else raises RuntimeError
    """
    # We'll attempt to find suitable dot pairs (length in range) that do not conflict.
    # Start from available free_lines list; we will remove as many free lines as we add connecting lines.
    max_attempts = 1000
    for attempt in range(max_attempts):
        # Copy
        lines_copy = [l for l in free_lines]
        connected_lines = []
        connected_pairs = []
        used_dots = set()
        success = True
        for c in range(n_connections):
            # Try to find a valid pair among dots not yet used
            found_pair = False
            pair_attempts = 0
            all_indices = list(range(len(dots)))
            random.shuffle(all_indices)
            for i1 in all_indices:
                if i1 in used_dots: 
                    continue
                for i2 in all_indices:
                    if i2 == i1 or i2 in used_dots:
                        continue
                    p1 = dots[i1]; p2 = dots[i2]
                    d = distance(p1,p2)
                    if not (MIN_LINE_LENGTH <= d <= MAX_LINE_LENGTH):
                        continue
                    new_line = (p1,p2)
                    # must not intersect existing connecting_lines or free lines that remain
                    if any(lines_intersect(new_line, l) for l in connected_lines + lines_copy):
                        continue
                    # must not come too close to other dots (except endpoints)
                    others = set(range(len(dots))) - {i1,i2}
                    too_close = False
                    for oi in others:
                        if point_to_segment_distance(dots[oi], p1, p2) < MIN_LINE_DOT_DISTANCE:
                            too_close = True
                            break
                    if too_close:
                        continue
                    # found candidate
                    connected_lines.append(new_line)
                    connected_pairs.append((i1,i2))
                    used_dots.add(i1); used_dots.add(i2)
                    found_pair = True
                    break
                if found_pair:
                    break
                pair_attempts += 1
                if pair_attempts > 5000:
                    break
            if not found_pair:
                success = False
                break
            # After finding a connecting line, remove one free line from lines_copy to represent replacement
            if lines_copy:
                # pick a random free line to replace
                lines_copy.pop(random.randrange(len(lines_copy)))
            else:
                success = False
                break
        if success:
            # Build resulting lines: remaining free lines + connected_lines
            final_lines = lines_copy + connected_lines
            # last checks: ensure final_lines don't intersect among themselves and respect distance to dots
            ok = True
            for a,b in itertools.combinations(final_lines,2):
                if lines_intersect(a,b):
                    ok = False; break
            if not ok:
                continue
            # ensure non-connecting lines are at least MIN_LINE_DOT_DISTANCE from dots
            for l in final_lines:
                # endpoints may be dot centers only if l in connected_lines
                for idx,dpt in enumerate(dots):
                    if (l in connected_lines) and (dpt in [l[0], l[1]]):
                        continue
                    if point_to_segment_distance(dpt, l[0], l[1]) < MIN_LINE_DOT_DISTANCE:
                        ok = False; break
                if not ok:
                    break
            if not ok:
                continue
            return final_lines, connected_pairs
    raise RuntimeError("Could not replace free lines with connecting lines after many attempts")

def generate_all_test_patterns():
    """
    For each connectedness level (0,1,2) and each dot number (9..15) produce PATTERNS_PER_CONDITION
    patterns. For connectedness>0, we derive patterns from 0-connected base configurations (reuse same dots)
    and mirror them as specified.
    """
    test_patterns = []

    # Pre-generate a pool of base configurations for each n_dots
    base_pool = {}  # key: n_dots -> list of base patterns (0-connected) sufficient to create derived ones
    for n_dots in TEST_DOT_NUMBERS:
        base_list = []
        signatures = set()
        attempts = 0
        needed = PATTERNS_PER_CONDITION # we'll create derived patterns per base; generate more if needed
        while len(base_list) < needed:
            attempts += 1
            if attempts > needed * 1000:
                raise RuntimeError(f"Too many attempts generating base patterns for {n_dots} dots")
            # generate dots placed with constraints
            try:
                dots = generate_dots(n_dots)
                # start with NUM_LINES free lines
                free_lines = generate_free_lines(NUM_LINES, dots)
            except RuntimeError:
                continue
            p = {'dots': dots, 'lines': free_lines.copy(), 'pairs': [], 'n_dots': n_dots, 'n_connection': 0}
            sig = pattern_signature(p)
            if sig in signatures:
                continue
            signatures.add(sig)
            base_list.append(p)
        base_pool[n_dots] = base_list

    # Now for each connectedness level, for each n_dots, derive patterns:
    for n_connection in CONNECTEDNESS_LEVELS:
        for n_dots in TEST_DOT_NUMBERS:
            # For each pattern replicate
            created = 0
            base_index = 0
            # We'll derive up to PATTERNS_PER_CONDITION per condition
            while created < PATTERNS_PER_CONDITION:
                base = base_pool[n_dots][base_index % len(base_pool[n_dots])]
                base_index += 1
                # Work on a deep copy of the base dots to preserve base for reuse
                dots = [ (x,y) for x,y in base['dots'] ]
                free_lines = [ ((l[0][0],l[0][1]),(l[1][0],l[1][1])) for l in base['lines'] ]
                if n_connection == 0:
                    pattern = {'dots': dots, 'lines': free_lines.copy(), 'pairs': [], 'n_dots': n_dots, 'n_connection': 0}
                    test_patterns.append(pattern)
                    created += 1
                    # add mirrored variant as long as we don't exceed required and it's unique
                    if created < PATTERNS_PER_CONDITION:
                        mirrored = mirror_pattern(pattern)
                        test_patterns.append(mirrored)
                        created += 1
                    continue
                # For connectedness > 0: attempt to replace free lines with connecting lines
                try:
                    final_lines, connected_pairs = replace_free_lines_with_connecting(dots, free_lines, n_connection)
                except RuntimeError:
                    # failed to derive from this base; skip to next base
                    continue
                pattern = {'dots': dots, 'lines': final_lines, 'pairs': connected_pairs, 'n_dots': n_dots, 'n_connection': n_connection}
                # ensure uniqueness relative to existing test_patterns for same condition
                sig = pattern_signature(pattern)
                if any(sig == pattern_signature(p) for p in test_patterns):
                    continue
                test_patterns.append(pattern)
                created += 1
                # Mirrored variant (explicitly requested)
                if created < PATTERNS_PER_CONDITION:
                    mirrored = mirror_pattern(pattern)
                    msig = pattern_signature(mirrored)
                    if not any(msig == pattern_signature(p) for p in test_patterns):
                        test_patterns.append(mirrored)
                        created += 1
            # end while for created per condition
    # Shuffle patterns before returning
    random.shuffle(test_patterns)
    return test_patterns

# -----------------------
# Top-level generation wrapper
# -----------------------
def generate_all_patterns():
    reference_patterns = generate_all_reference_patterns()
    test_patterns = generate_all_test_patterns()
    # Shuffle both lists
    random.shuffle(reference_patterns)
    random.shuffle(test_patterns)
    # Final sanity checks: lengths
    if len(reference_patterns) < TRIALS_PER_HALF_BLOCK or len(test_patterns) < TRIALS_PER_HALF_BLOCK:
        raise RuntimeError("Not enough patterns generated for full half-block; adjust parameters")
    return reference_patterns, test_patterns

# -----------------------
# Stimulus creation + preloading for performance
# We'll create canvases (or pre-render images) ahead of the experiment to avoid delays.
# -----------------------
def create_pattern_canvas(pattern, offset_x):
    """Return a Canvas pre-populated with the pattern drawn centered at (offset_x,0)."""
    canvas = stimuli.Canvas(size=(PATTERN_WIDTH, PATTERN_HEIGHT), colour=PATTERN_COLOR, position=(offset_x,0))
    # draw dots
    for (x,y) in pattern['dots']:
        dot = stimuli.Circle(radius=DOT_DIAMETER/2, colour=DOT_COLOR, position=(x,y))
        dot.plot(canvas)
    # draw lines
    for ((x1,y1),(x2,y2)) in pattern['lines']:
        line = stimuli.Line(start_point=(x1,y1), end_point=(x2,y2), line_width=LINE_WIDTH, colour=LINE_COLOR)
        line.plot(canvas)
    # Preload the canvas into the video memory if possible
    try:
        canvas.preload()
    except Exception:
        # some expyriment versions may not support preload on Canvas; best-effort
        pass
    return canvas

# -----------------------
# Trial list creation with simple counterbalancing
# For counterbalancing: ensure equal left/right across conditions by creating pairs and shuffling.
# -----------------------
def create_trial_list(reference_patterns, test_patterns, block_num):
    # We'll take TRIALS_PER_HALF_BLOCK items from each list and create half-block 1
    indices = list(range(TRIALS_PER_HALF_BLOCK))
    random.shuffle(indices)
    trials = []
    for i in indices:
        ref_pattern = reference_patterns[i]
        test_pattern = test_patterns[i]
        # Counterbalance left/right at condition-level:
        # To ensure approximate balance, alternate assignment for repeated instances of same (n_dots, n_connection)
        # A simpler approach: choose randomly but ensure global counts per condition are balanced:
        trials.append({
            'block': block_num,
            'half': 1,
            'reference_pattern': ref_pattern,
            'test_pattern': test_pattern,
            'test_on_left': random.choice([True, False]),
            'num_dots': test_pattern['n_dots'],
            'connectedness': test_pattern['n_connection'],
            'is_practice': False
        })
    # Create second half as mirrored positions
    second_half = []
    for t in trials:
        nt = t.copy()
        nt['half'] = 2
        nt['test_on_left'] = not t['test_on_left']
        second_half.append(nt)
    full = trials + second_half
    # Shuffle full list to avoid blockwise ordering but keep 'half' markers intact (if needed)
    random.shuffle(full)
    # Add trial numbering
    for idx, t in enumerate(full, start=1):
        t['trial_num'] = idx
    return full

# -----------------------
# Practice trials
# -----------------------
def create_practice_trials():
    trials = []
    for i in range(NUM_PRACTICE_TRIALS):
        test_pat = generate_test_pattern(PRACTICE_TEST_DOTS, 0) if 'generate_test_pattern' in globals() else None
        # fallback: use generate_test_pattern function below (we'll implement generate_test_pattern quickly)
        # but easier: create a small 9-dot pattern here using same functions
        dots = generate_dots(PRACTICE_TEST_DOTS)
        free_lines = generate_free_lines(NUM_LINES, dots)
        test_pattern = {'dots': dots, 'lines': free_lines, 'pairs': [], 'n_dots': PRACTICE_TEST_DOTS, 'n_connection': 0}
        ref_pattern = generate_reference_pattern()
        test_on_left = random.choice([True, False])
        trials.append({
            'block': 0,
            'half': 0,
            'reference_pattern': ref_pattern,
            'test_pattern': test_pattern,
            'test_on_left': test_on_left,
            'num_dots': test_pattern['n_dots'],
            'connectedness': test_pattern['n_connection'],
            'is_practice': True,
            'trial_num': i+1
        })
    return trials

# Small wrapper functions referencing earlier implemented functions (for usage in practice)
def generate_reference_pattern():
    # use generate_dots(NUM_REFERENCE_DOTS) + generate_free_lines
    while True:
        try:
            dots = generate_dots(NUM_REFERENCE_DOTS)
            lines = generate_free_lines(NUM_LINES, dots)
            return {'dots': dots, 'lines': lines, 'pairs': [], 'n_dots': NUM_REFERENCE_DOTS, 'n_connection': 0}
        except RuntimeError:
            continue

def generate_test_pattern(n_dots, n_connection):
    while True:
        try:
            dots = generate_dots(n_dots)
            lines = []
            connected_pairs = []
            if n_connection > 0:
                # attempt to create some connecting lines first, using generate_connecting_lines_from_dots
                lines_tmp, connected_pairs = generate_connecting_lines_from_dots(dots, n_connection, [])
                lines.extend(lines_tmp)
            # fill the remaining lines with free lines
            n_free = NUM_LINES - len(lines)
            if n_free > 0:
                lines += generate_free_lines(n_free, dots, existing_lines=lines)
            return {'dots': dots, 'lines': lines, 'pairs': connected_pairs, 'n_dots': n_dots, 'n_connection': n_connection}
        except RuntimeError:
            continue

# -----------------------
# Presentation helpers
# -----------------------
def present_pattern_pair(exp, left_canvas, right_canvas, fixation_cross):
    # Show fixation
    fixation_cross.present()
    exp.clock.wait(300)
    # display canvases
    screen = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    left_canvas.plot(screen)
    right_canvas.plot(screen)
    screen.present()
    # keep for the duration
    exp.clock.wait(STIMULUS_DURATION)
    # blank
    stimuli.BlankScreen(colour=BACKGROUND_COLOR).present()

# -----------------------
# Run single trial (records data)
# -----------------------
def run_trial(exp, trial_info, fixation_cross, preload_cache):
    iti = random.randint(MIN_ITI, MAX_ITI)
    exp.clock.wait(iti)

    # Choose canvases from preload cache if available
    ref_p = trial_info['reference_pattern']
    test_p = trial_info['test_pattern']
    # make signature keys for cache
    # keying by signature + left/right
    left_offset = -HEMIFIELD_OFFSET
    right_offset = HEMIFIELD_OFFSET
    if trial_info['test_on_left']:
        left_pattern = test_p; right_pattern = ref_p
    else:
        left_pattern = ref_p; right_pattern = test_p
    # create cache keys
    left_key = (pattern_signature(left_pattern), 'L')
    right_key = (pattern_signature(right_pattern), 'R')
    # obtain canvases (preloaded) or create on the fly if not present
    left_canvas = preload_cache.get(left_key) or create_pattern_canvas(left_pattern, left_offset)
    right_canvas = preload_cache.get(right_key) or create_pattern_canvas(right_pattern, right_offset)

    # present and wait for response
    present_pattern_pair(exp, left_canvas, right_canvas, fixation_cross)
    # wait for response
    key, rt = exp.keyboard.wait([K_LEFT, K_RIGHT])
    choice_side = "left" if key == K_LEFT else "right"
    test_side = "left" if trial_info['test_on_left'] else "right'
    chose_test = (choice_side == test_side)

    # record data (include detailed fields)
    exp.data.add([
        trial_info.get('block', -1),
        trial_info.get('half', -1),
        trial_info.get('trial_num', -1),
        trial_info.get('num_dots', -1),
        trial_info.get('connectedness', -1),
        'test' if trial_info.get('is_practice', False) else 'main',
        trial_info.get('test_on_left'),
        choice_side,
        test_side,
        chose_test,
        rt
    ])
    return chose_test

# -----------------------
# Main experiment
# -----------------------
def run_experiment():
    exp = design.Experiment(name="Connectedness_Numerosity_Checked")
    # define data column names for clarity
    exp.data.add_variable_names([
        'block','half','trial_num','num_dots','connectedness','phase','test_on_left',
        'choice_side','test_side','chose_test','rt'
    ])
    control.initialize(exp)
    # developer mode False for better timing in actual run; set True for debugging
    control.set_develop_mode(False)

    # Generate patterns
    print("Generating all patterns (this may take some time)...")
    reference_patterns, test_patterns = generate_all_patterns()
    print("Generation complete.")

    # Preload canvases for faster presentation: store a limited cache (e.g., first N used patterns)
    preload_cache = {}
    # Preload for the first TRIALS_PER_HALF_BLOCK patterns as they will be used in block 1
    for i in range(TRIALS_PER_HALF_BLOCK):
        # ref left/right versions
        ref = reference_patterns[i]
        test = test_patterns[i]
        # create canvases both positions (L/R)
        key_ref_L = (pattern_signature(ref),'L'); key_ref_R = (pattern_signature(ref),'R')
        key_test_L = (pattern_signature(test),'L'); key_test_R = (pattern_signature(test),'R')
        if key_ref_L not in preload_cache:
            preload_cache[key_ref_L] = create_pattern_canvas(ref, -HEMIFIELD_OFFSET)
            preload_cache[key_ref_R] = create_pattern_canvas(ref, HEMIFIELD_OFFSET)
        if key_test_L not in preload_cache:
            preload_cache[key_test_L] = create_pattern_canvas(test, -HEMIFIELD_OFFSET)
            preload_cache[key_test_R] = create_pattern_canvas(test, HEMIFIELD_OFFSET)

    # Instructions and fixation
    instructions = stimuli.TextScreen("Numerosity Judgment Task", text="""You will see two patterns of dots flash briefly on the screen.

Your task is to decide which pattern contains MORE dots.

Press the LEFT arrow key if the LEFT pattern has more dots.
Press the RIGHT arrow key if the RIGHT pattern has more dots.

Keep your eyes on the green fixation cross in the center.

We will start with some practice trials.

Press SPACE to begin practice.""")
    fixation_cross = stimuli.FixCross(size=(20,20), colour=C_GREEN, line_width=2)
    fixation_cross.preload()

    # Start
    control.start(skip_ready_screen=True)
    instructions.present()
    exp.keyboard.wait(K_SPACE)

    # Practice
    practice_trials = create_practice_trials()
    stimuli.TextScreen("Practice", "Practice trials\n\nPress SPACE to start").present()
    exp.keyboard.wait(K_SPACE)
    for t in practice_trials:
        run_trial(exp, t, fixation_cross, preload_cache)

    stimuli.TextScreen("Practice Complete", "Practice is complete!\n\nThe main experiment will now begin.\n\nPress SPACE to continue").present()
    exp.keyboard.wait(K_SPACE)

    # Main blocks
    for block_num in range(1, NUM_BLOCKS+1):
        stimuli.TextScreen(f"Block {block_num} of {NUM_BLOCKS}", f"Starting block {block_num}\n\nPress SPACE when ready").present()
        exp.keyboard.wait(K_SPACE)
        trials = create_trial_list(reference_patterns, test_patterns, block_num)
        for t in trials:
            run_trial(exp, t, fixation_cross, preload_cache)
        if block_num < NUM_BLOCKS:
            stimuli.TextScreen("Break Time", "Take a rest.\n\nPress SPACE when ready to continue").present()
            exp.keyboard.wait(K_SPACE)

    stimuli.TextScreen("Experiment Complete", "Thank you for participating").present()
    exp.clock.wait(2000)
    control.end()

if __name__ == "__main__":
    run_experiment()
