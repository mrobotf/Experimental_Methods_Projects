# Merged experiment: full experiment (second script) using main script's generator functions
# Option A: keep experimental flow, replace DotPattern with main procedural generator
import expyriment
from expyriment import design, control, stimuli
from expyriment.misc.constants import C_BLACK, C_GREEN, K_SPACE, K_LEFT, K_RIGHT
import random
import numpy as np
import math

# -----------------------
# DISPLAY & STIMULUS CONSTANTS (taken from main script)
# -----------------------
SCREEN_SIZE = (1024, 768)
BACKGROUND_COLOR = (0, 0, 0)

# Pattern settings (main script values)
PATTERN_WIDTH = 240 # Increased to allow more dots
PATTERN_HEIGHT = 320
PATTERN_COLOR = (102, 102, 102)
PATTERN_OFFSET_X = 300

# Dot settings
DOT_DIAMETER = 12
DOT_COLOR = (0, 0, 0)
MIN_DOT_DISTANCE = 42
MIN_DOT_BOUNDARY_DISTANCE = 10

# Line settings
LINE_WIDTH = 2
LINE_COLOR = (0, 0, 0)
MIN_LINE_LENGTH = 30
MAX_LINE_LENGTH = 60
MIN_LINE_DOT_DISTANCE = 12

# Timing (use experimental script's timing values where relevant)
STIMULUS_DURATION = 200  # ms (from main)
MIN_ITI = 500
MAX_ITI = 1000

# Experimental settings (from second script)
NUM_REFERENCE_DOTS = 12
NUM_LINES = 4
TEST_DOT_NUMBERS = [9, 10, 11, 12, 13, 14, 15]
CONNECTEDNESS_LEVELS = [0, 1, 2]
PATTERNS_PER_CONDITION = 8

# Trial organization
NUM_BLOCKS = 5
TRIALS_PER_HALF_BLOCK = 168  # 21 conditions × 8 repetitions

# Practice
NUM_PRACTICE_TRIALS = 30
PRACTICE_TEST_DOTS = 9

# Hemifield offset (from second script)
HEMIFIELD_OFFSET = 200

# -----------------------
# Utility / geometry functions (from main script)
# -----------------------
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def lines_intersect(line1, line2):
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return False

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

    return 0 < t < 1 and 0 < u < 1

def point_to_segment_distance(point, seg_start, seg_end):
    px, py = point
    x1, y1 = seg_start
    x2, y2 = seg_end

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        return math.sqrt((px - x1)**2 + (py - y1)**2)

    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy

    return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)

# -----------------------
# Pattern generation (adapted from main)
# Patterns are dictionaries:
# {'dots': [(x,y),...], 'lines': [((x1,y1),(x2,y2)), ...], 'pairs': [...], 'n_dots': N, 'n_connection': C}
# -----------------------
def generate_dots(n_dots):
    dots = []
    max_attempts = 10000
    for i in range(n_dots):
        for attempt in range(max_attempts):
            x = random.randint(-PATTERN_WIDTH // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                                PATTERN_WIDTH // 2 - MIN_DOT_BOUNDARY_DISTANCE)
            y = random.randint(-PATTERN_HEIGHT // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                                PATTERN_HEIGHT // 2 - MIN_DOT_BOUNDARY_DISTANCE)

            if all(distance((x, y), d) >= MIN_DOT_DISTANCE for d in dots):
                dots.append((x, y))
                break
        else:
            raise RuntimeError(f'Could not place dot {i + 1}')
    return dots

def generate_free_lines(n_line, dots, existing_lines=None):
    if existing_lines is None:
        existing_lines = []
    lines = list(existing_lines)
    max_attempts = 1000
    for _ in range(n_line):
        for attempt in range(max_attempts):
            x1 = random.randint(-PATTERN_WIDTH // 2, PATTERN_WIDTH // 2)
            y1 = random.randint(-PATTERN_HEIGHT // 2, PATTERN_HEIGHT // 2)
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
            x2 = x1 + length * math.cos(angle)
            y2 = y1 + length * math.sin(angle)

            # boundary check
            if not (-PATTERN_WIDTH // 2 <= x2 <= PATTERN_WIDTH // 2 and 
                    -PATTERN_HEIGHT // 2 <= y2 <= PATTERN_HEIGHT // 2):
                continue

            # check distance from all dots
            if any(point_to_segment_distance(d, (x1, y1), (x2, y2)) < MIN_LINE_DOT_DISTANCE for d in dots):
                continue

            # check intersection with existing lines
            if any(lines_intersect(((x1, y1), (x2, y2)), l) for l in lines):
                continue

            lines.append(((x1, y1), (x2, y2)))
            break
        else:
            raise RuntimeError('Could not place a line after many attempts')

    return lines

def generate_connecting_lines(dots, n_connection, existing_lines=None):
    if existing_lines is None:
        existing_lines = []
    connecting_lines = list(existing_lines)
    connected_pairs = []
    available_dots = list(range(len(dots)))

    for _ in range(n_connection):
        if len(available_dots) < 2:
            break
        for attempt in range(1000):
            i1, i2 = random.sample(available_dots, 2)
            p1, p2 = dots[i1], dots[i2]
            d = distance(p1, p2)

            if not (MIN_LINE_LENGTH <= d <= MAX_LINE_LENGTH):
                continue

            # avoid intersecting existing lines
            if any(lines_intersect((p1, p2), l) for l in connecting_lines):
                continue

            if any(point_to_segment_distance(dpt, p1, p2) < MIN_LINE_DOT_DISTANCE for dpt in dots):
                continue

            connecting_lines.append((p1, p2))
            connected_pairs.append((i1, i2))
            available_dots.remove(i1)
            available_dots.remove(i2)
            break
        else:
            # if cannot place a connecting line, print a warning and continue (non-fatal)
            print('Warning: Could not place a connecting line (continuing)')

    return connecting_lines, connected_pairs

def generate_reference_pattern():
    while True:
        try:
            reference_dots = generate_dots(NUM_REFERENCE_DOTS)
            reference_lines = generate_free_lines(NUM_LINES, reference_dots)
            return {
                'dots': reference_dots,
                'lines': reference_lines,
                'pairs': [],
                'n_dots': NUM_REFERENCE_DOTS,
                'n_connection': 0
            }
        except RuntimeError:
            continue

def generate_test_pattern(n_dots, n_connection):
    while True:
        try:
            test_dots = generate_dots(n_dots)
            test_lines = []
            connected_pairs = []
            if n_connection > 0:
                test_lines, connected_pairs = generate_connecting_lines(test_dots, n_connection, test_lines)
            n_free = NUM_LINES - len(test_lines)
            if n_free > 0:
                test_lines += generate_free_lines(n_free, test_dots, existing_lines=test_lines)
            return {
                'dots': test_dots,
                'lines': test_lines,
                'pairs': connected_pairs,
                'n_dots': n_dots,
                'n_connection': n_connection
            }
        except RuntimeError:
            continue

def generate_all_reference_patterns():
    all_ref_patterns = []
    for _ in range(TRIALS_PER_HALF_BLOCK):
        dots, lines = None, None
        # Use generate_reference_pattern which already retries internally
        p = generate_reference_pattern()
        all_ref_patterns.append(p)
    return all_ref_patterns

def generate_all_test_patterns():
    all_test_patterns = []
    for n_connection in [0, 1, 2]:
        for n_dots in range(9, 16):
            for _ in range(8):
                p = generate_test_pattern(n_dots, n_connection)
                all_test_patterns.append(p)
    return all_test_patterns

# -----------------------
# Stimulus creation for Expyriment (works with dict-based pattern)
# -----------------------
def create_pattern_stimulus(pattern, offset_x):
    """
    Create an Expyriment Canvas with the pattern rendered at offset_x from center.
    pattern: dict with 'dots' and 'lines'
    """
    # We create a canvas the size of PATTERN and position it with offset
    canvas = stimuli.Canvas(size=(PATTERN_WIDTH, PATTERN_HEIGHT), colour=PATTERN_COLOR, position=(offset_x, 0))

    # Draw dots: canvas coordinates are centered at 0,0 for plotting here (Expyriment Canvas expects coordinates)
    for (x, y) in pattern['dots']:
        dot = stimuli.Circle(radius=DOT_DIAMETER / 2, colour=DOT_COLOR, position=(x, y))
        dot.plot(canvas)

    # Draw lines
    for ((x1, y1), (x2, y2)) in pattern['lines']:
        line = stimuli.Line(start_point=(x1, y1), end_point=(x2, y2), line_width=LINE_WIDTH, colour=LINE_COLOR)
        line.plot(canvas)

    return canvas

# -----------------------
# Pattern generation wrapper used by the experiment
# -----------------------
def generate_all_patterns():
    """
    Generate reference_patterns and test_patterns lists using main generator functions.
    Returns (reference_patterns, test_patterns)
    """
    reference_patterns = generate_all_reference_patterns()
    test_patterns = generate_all_test_patterns()

    # Shuffle for randomness across blocks
    random.shuffle(reference_patterns)
    random.shuffle(test_patterns)

    return reference_patterns, test_patterns

# -----------------------
# Trial list creation (keeps second script logic)
# -----------------------
def create_trial_list(reference_patterns, test_patterns, block_num):
    trials = []

    number_of_trials = TRIALS_PER_HALF_BLOCK
    order = list(range(number_of_trials))
    random.shuffle(order)

    for i in order:
        ref_pattern = reference_patterns[i]
        test_pattern = test_patterns[i]
        test_on_left = random.choice([True, False])

        trial_info = {
            'block': block_num,
            'half': 1,
            'reference_pattern': ref_pattern,
            'test_pattern': test_pattern,
            'test_on_left': test_on_left,
            'num_dots': test_pattern['n_dots'],
            'connectedness': test_pattern['n_connection'],
            'is_practice': False
        }
        trials.append(trial_info)

    # Second half: reverse positions
    for first_trial in trials[:number_of_trials]:
        new_trial = first_trial.copy()
        new_trial['half'] = 2
        new_trial['test_on_left'] = not first_trial['test_on_left']
        trials.append(new_trial)

    return trials

# -----------------------
# Practice trials creation (fixed)
# -----------------------
def create_practice_trials():
    trials = []
    for i in range(NUM_PRACTICE_TRIALS):
        # test pattern: easy (9 dots, 0 connections)
        test_pattern = generate_test_pattern(PRACTICE_TEST_DOTS, 0)
        # reference pattern: 12 dots, 0 connections
        ref_pattern = generate_reference_pattern()
        test_on_left = random.choice([True, False])
        trial_info = {
            'block': 0,
            'half': 0,
            'reference_pattern': ref_pattern,
            'test_pattern': test_pattern,
            'test_on_left': test_on_left,
            'num_dots': test_pattern['n_dots'],
            'connectedness': test_pattern['n_connection'],
            'is_practice': True
        }
        trials.append(trial_info)
    return trials

# -----------------------
# Drawing helper and trial runner (from second script, adapted)
# -----------------------
def draw(stims, canvas):
    canvas.clear_surface()
    canvas.preload()
    for stim in stims:
        stim.plot(canvas)
    canvas.present()

def run_trial(exp, trial_info, fixation_cross):
    # Random ITI
    iti = random.randint(MIN_ITI, MAX_ITI)
    exp.clock.wait(iti)

    # Show fixation cross
    fixation_cross.present()
    exp.clock.wait(300)  # small fixation duration (optional)

    # Prepare stimuli
    ref_pattern = trial_info['reference_pattern']
    test_pattern = trial_info['test_pattern']

    if trial_info['test_on_left']:
        left_pattern = test_pattern
        right_pattern = ref_pattern
        left_offset = -HEMIFIELD_OFFSET
        right_offset = HEMIFIELD_OFFSET
    else:
        left_pattern = ref_pattern
        right_pattern = test_pattern
        left_offset = -HEMIFIELD_OFFSET
        right_offset = HEMIFIELD_OFFSET

    left_canvas = create_pattern_stimulus(left_pattern, left_offset)
    right_canvas = create_pattern_stimulus(right_pattern, right_offset)

    # Combine on blank screen
    display = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    # Plot canvases onto display
    left_canvas.plot(display)
    right_canvas.plot(display)

    # Present stimulus
    display.present()
    exp.clock.wait(STIMULUS_DURATION)

    # Blank screen
    blank = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    blank.present()

    # Wait for response
    key, rt = exp.keyboard.wait([K_LEFT, K_RIGHT])

    choice_side = "left" if key == K_LEFT else "right"
    test_side = "left" if trial_info['test_on_left'] else "right"
    chose_test = (choice_side == test_side)

    # Record data
    exp.data.add([
        trial_info['block'],
        trial_info['half'],
        trial_info['num_dots'],
        trial_info['connectedness'],
        trial_info['test_on_left'],
        choice_side,
        test_side,
        chose_test,
        rt
    ])

    return chose_test

# -----------------------
# Main experiment runner (keeps second's overall flow)
# -----------------------
def run_experiment():
    exp = design.Experiment(name="Connectedness_Numerosity_Merged")
    control.initialize(exp)
    control.set_develop_mode()  # developer mode for debugging
    # Start control at the right moment later (after preload of fixation etc.)

    # Generate patterns
    reference_patterns, test_patterns = generate_all_patterns()

    # Instructions
    instructions = stimuli.TextScreen(
        "Numerosity Judgment Task",
        text="""You will see two patterns of dots flash briefly on the screen.

Your task is to decide which pattern contains MORE dots.

Press the LEFT arrow key if the LEFT pattern has more dots.
Press the RIGHT arrow key if the RIGHT pattern has more dots.

Keep your eyes on the green fixation cross in the center.

There is no time limit for your response.

We will start with some practice trials.

Press SPACE to begin practice."""
    )

    # Fixation cross
    fixation_cross = stimuli.FixCross(size=(20, 20), colour=C_GREEN, line_width=2)
    fixation_cross.preload()

    # Start experiment
    control.start(skip_ready_screen=True)

    instructions.present()
    exp.keyboard.wait(K_SPACE)

    # Practice
    practice_trials = create_practice_trials()
    practice_instruction = stimuli.TextScreen("Practice", "Practice trials\n\nPress SPACE to start")
    practice_instruction.present()
    exp.keyboard.wait(K_SPACE)
    for trial in practice_trials:
        run_trial(exp, trial, fixation_cross)

    end_practice = stimuli.TextScreen("Practice Complete",
                                     "Practice is complete!\n\nThe main experiment will now begin.\n\nPress SPACE to continue")
    end_practice.present()
    exp.keyboard.wait(K_SPACE)

    # Main blocks
    for block_num in range(1, NUM_BLOCKS + 1):
        block_instruction = stimuli.TextScreen(f"Block {block_num} of {NUM_BLOCKS}", f"Starting block {block_num}\n\nPress SPACE when ready")
        block_instruction.present()
        exp.keyboard.wait(K_SPACE)

        trials = create_trial_list(reference_patterns, test_patterns, block_num)

        for i, trial in enumerate(trials):
            run_trial(exp, trial, fixation_cross)

        if block_num < NUM_BLOCKS:
            break_screen = stimuli.TextScreen("Break Time", f"Block {block_num} complete!\n\nTake a rest.\n\nPress SPACE when ready to continue")
            break_screen.present()
            exp.keyboard.wait(K_SPACE)

    # End
    end_screen = stimuli.TextScreen("Experiment Complete", "Thank you for participating")
    end_screen.present()
    exp.clock.wait(3000)
    control.end()

if __name__ == "__main__":
    run_experiment()
