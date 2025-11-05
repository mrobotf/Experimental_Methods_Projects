"""
Experiment 1: Connectedness Affects Dot Numerosity Judgment

Based on: He, L., Zhang, J., Zhou, T., & Chen, L. (2009). 
Connectedness affects dot numerosity judgment: Implications for configural processing.
Psychonomic Bulletin & Review, 16(3), 509-517.

CORRECTED VERSION: Reuses dot configurations across connectedness levels
"""

import expyriment
from expyriment import design, control, stimuli
import random
import math
import copy
from datetime import datetime
import json
import os

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Display settings
SCREEN_SIZE = (1024, 768)
BACKGROUND_COLOR = (0, 0, 0)  # Black background

# Pattern settings
PATTERN_WIDTH = 280
PATTERN_HEIGHT = 360
PATTERN_COLOR = (102, 102, 102)  # Gray pattern rectangles

# Dot settings
DOT_DIAMETER = 12  # pixels
DOT_COLOR = (0, 0, 0)  # Black dots
MIN_DOT_DISTANCE = 42  # pixels - CORRECTED to paper specification
MIN_DOT_BOUNDARY_DISTANCE = 20  # pixels from pattern edges - DOUBLED for more space

# Line settings
LINE_WIDTH = 5  # pixels - increased for visibility
LINE_COLOR = (0, 0, 0)  # Black lines
MIN_LINE_LENGTH = 30  # pixels
MAX_LINE_LENGTH = 60  # pixels
MIN_LINE_DOT_DISTANCE = 12  # pixels (except for connecting lines)

# Experimental settings
NUM_REFERENCE_DOTS = 12
NUM_LINES = 4  # Always 4 lines per pattern
TEST_DOT_NUMBERS = [9, 10, 11, 12, 13, 14, 15]  # 7 levels
CONNECTEDNESS_LEVELS = [0, 1, 2]  # 0, 1, or 2 pairs connected
PATTERNS_PER_CONDITION = 8

# Timing
STIMULUS_DURATION = 200  # ms
MIN_ITI = 500  # ms
MAX_ITI = 1000  # ms

# Trial organization
NUM_BLOCKS = 5
TRIALS_PER_HALF_BLOCK = 168  # 21 conditions × 8 repetitions

# Practice settings
NUM_PRACTICE_TRIALS = 30
PRACTICE_TEST_DOTS = 9  # Easy discrimination: 9 vs 12

# Positioning
HEMIFIELD_OFFSET = 220  # pixels from center


# ============================================================================
# HELPER CLASSES
# ============================================================================

class DotPattern:
    """Represents a dot pattern with dots and lines"""

    def __init__(self, num_dots, connectedness, pattern_id=0, base_dots=None):
        self.num_dots = num_dots
        self.connectedness = connectedness  # 0, 1, or 2
        self.pattern_id = pattern_id
        self.dots = base_dots if base_dots is not None else []
        self.lines = []  # List of ((x1, y1), (x2, y2)) tuples
        self.connected_pairs = []  # List of indices of connected dot pairs

    def generate(self):
        """Generate the complete pattern with constraints"""
        if not self.dots:  # Only generate dots if not provided
            self.dots = self._generate_dots()
        self.lines = self._generate_lines()

    def copy_dots(self):
        """Return a copy of the dot configuration"""
        return copy.deepcopy(self.dots)

    def to_dict(self):
        """Convert pattern to dictionary for JSON storage"""
        return {
            'num_dots': self.num_dots,
            'connectedness': self.connectedness,
            'pattern_id': self.pattern_id,
            'dots': self.dots,
            'lines': [{'start': list(start), 'end': list(end)} for start, end in self.lines],
            'connected_pairs': self.connected_pairs
        }

    def _generate_dots(self):
        """Generate random dot positions with constraints"""
        dots = []
        max_attempts = 10000

        for i in range(self.num_dots):
            attempts = 0
            while attempts < max_attempts:
                x = random.randint(
                    -PATTERN_WIDTH // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                    PATTERN_WIDTH // 2 - MIN_DOT_BOUNDARY_DISTANCE
                )
                y = random.randint(
                    -PATTERN_HEIGHT // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                    PATTERN_HEIGHT // 2 - MIN_DOT_BOUNDARY_DISTANCE
                )

                valid = True
                for (dx, dy) in dots:
                    distance = math.sqrt((x - dx)**2 + (y - dy)**2)
                    if distance < MIN_DOT_DISTANCE:
                        valid = False
                        break

                if valid:
                    dots.append((x, y))
                    break

                attempts += 1

            if attempts >= max_attempts:
                raise RuntimeError(f"Could not place dot {i+1}/{self.num_dots}")

        return dots

    def _generate_lines(self):
        """Generate lines - some connecting, some free"""
        lines = []

        if self.connectedness == 0:
            lines = self._generate_free_lines(NUM_LINES)
        else:
            connecting_lines, self.connected_pairs = self._generate_connecting_lines(
                self.connectedness
            )
            lines.extend(connecting_lines)

            num_free = NUM_LINES - len(connecting_lines)  # Use actual count
            if num_free > 0:
                free_lines = self._generate_free_lines(num_free)
                lines.extend(free_lines)

        # Ensure we have exactly NUM_LINES lines
        while len(lines) < NUM_LINES:
            extra_lines = self._generate_free_lines(NUM_LINES - len(lines))
            lines.extend(extra_lines)

        return lines

    def _generate_connecting_lines(self, num_connections):
        """Generate lines connecting pairs of dots"""
        lines = []
        connected_pairs = []
        available_dots = list(range(len(self.dots)))
        random.shuffle(available_dots)

        for _ in range(num_connections):
            if len(available_dots) < 2:
                break

            max_attempts = 1000
            found = False

            for attempt in range(max_attempts):
                if len(available_dots) < 2:
                    break

                idx1 = available_dots[0]

                for idx2 in available_dots[1:]:
                    x1, y1 = self.dots[idx1]
                    x2, y2 = self.dots[idx2]

                    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

                    if MIN_LINE_LENGTH <= distance <= MAX_LINE_LENGTH:
                        new_line = ((x1, y1), (x2, y2))

                        if not self._line_crosses_others(new_line, lines):
                            if not self._line_too_close_to_other_dots(new_line, idx1, idx2):
                                lines.append(new_line)
                                connected_pairs.append((idx1, idx2))
                                available_dots.remove(idx1)
                                available_dots.remove(idx2)
                                found = True
                                break

                if found:
                    break

                available_dots.pop(0)
                if idx1 not in [p[0] for p in connected_pairs] and idx1 not in [p[1] for p in connected_pairs]:
                    available_dots.append(idx1)

            if not found:
                break

        return lines, connected_pairs

    def _generate_free_lines(self, num_lines):
        """Generate free-hanging lines"""
        lines = []

        for _ in range(num_lines):
            max_attempts = 2000
            for attempt in range(max_attempts):
                x1 = random.randint(-PATTERN_WIDTH // 2 + 20, PATTERN_WIDTH // 2 - 20)
                y1 = random.randint(-PATTERN_HEIGHT // 2 + 20, PATTERN_HEIGHT // 2 - 20)

                angle = random.uniform(0, 2 * math.pi)
                length = random.randint(MIN_LINE_LENGTH, MAX_LINE_LENGTH)

                x2 = x1 + int(length * math.cos(angle))
                y2 = y1 + int(length * math.sin(angle))

                if (abs(x2) > PATTERN_WIDTH // 2 - 10 or
                    abs(y2) > PATTERN_HEIGHT // 2 - 10):
                    continue

                new_line = ((x1, y1), (x2, y2))

                if self._line_crosses_others(new_line, lines):
                    continue

                too_close = False
                for (dx, dy) in self.dots:
                    dist = self._point_to_segment_distance((dx, dy), (x1, y1), (x2, y2))
                    if dist < MIN_LINE_DOT_DISTANCE * 0.8:
                        too_close = True
                        break

                if not too_close:
                    lines.append(new_line)
                    break

        return lines

    def _line_crosses_others(self, new_line, existing_lines):
        """Check if line crosses any existing lines"""
        for line in existing_lines:
            if self._lines_intersect(new_line, line):
                return True
        return False

    def _lines_intersect(self, line1, line2):
        """Check if two line segments intersect"""
        (x1, y1), (x2, y2) = line1
        (x3, y3), (x4, y4) = line2

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return False

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        return 0 < t < 1 and 0 < u < 1

    def _line_too_close_to_other_dots(self, line, idx1, idx2):
        """Check if connecting line is too close to dots OTHER than connected ones"""
        (x1, y1), (x2, y2) = line

        for i, (dx, dy) in enumerate(self.dots):
            if i == idx1 or i == idx2:
                continue

            dist = self._point_to_segment_distance((dx, dy), (x1, y1), (x2, y2))
            if dist < MIN_LINE_DOT_DISTANCE:
                return True
        return False

    def _point_to_segment_distance(self, point, seg_start, seg_end):
        """Calculate minimum distance from point to line segment"""
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


# ============================================================================
# DATA LOGGING CLASS
# ============================================================================

class DetailedDataLogger:
    """Handles detailed logging of stimulus and response data"""

    def __init__(self, participant_id, experiment_name="Connectedness_Numerosity_Exp1"):
        self.participant_id = participant_id
        self.experiment_name = experiment_name
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Use current working directory + data folder (portable across PCs)
        self.data_dir = "data"

        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Create filename with participant ID and timestamp
        self.filename = os.path.join(self.data_dir, f"{experiment_name}_P{participant_id}_{self.timestamp}.json")

        # Print where data will be saved
        print(f"JSON data will be saved to: {self.filename}")

        # Initialize data structure
        self.data = {
            'participant_id': participant_id,
            'experiment_name': experiment_name,
            'timestamp': self.timestamp,
            'start_time': datetime.now().isoformat(),
            'trials': []
        }

    def log_trial(self, trial_number, block, half, ref_pattern, test_pattern,
                  test_on_left, response_key, rt):
        """
        Log detailed information about a trial
        """

        chose_left = (response_key == expyriment.misc.constants.K_LEFT)
        chose_test = (chose_left == test_on_left)

        trial_data = {
            'trial_number': trial_number,
            'block': block,
            'half': half,

            # Reference pattern info
            'reference': {
                'num_dots': ref_pattern.num_dots,
                'connectedness': ref_pattern.connectedness,
                'position': 'left' if not test_on_left else 'right'
            },

            # Test pattern info (DETAILED)
            'test': {
                'num_dots': test_pattern.num_dots,
                'connectedness': test_pattern.connectedness,
                'pattern_id': test_pattern.pattern_id,
                'position': 'left' if test_on_left else 'right',
                'dots': test_pattern.dots,
                'lines': [{'start': list(start), 'end': list(end)}
                         for start, end in test_pattern.lines],
                'connected_pairs': test_pattern.connected_pairs
            },

            # Response info
            'response': {
                'key_pressed': 'left' if chose_left else 'right',
                'chose_test': chose_test,
                'chose_left': chose_left,
                'rt_ms': rt,
                'correct': chose_test if test_pattern.num_dots != ref_pattern.num_dots else None
            }
        }

        self.data['trials'].append(trial_data)

    def save(self):
        """Save data to JSON file"""
        self.data['end_time'] = datetime.now().isoformat()

        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)

        print(f"\n✓ Data saved to: {self.filename}")
        return self.filename


# ============================================================================
# STIMULUS GENERATION - WITH PATTERN REUSE
# ============================================================================

def generate_all_patterns():
    """
    Generate all patterns for the experiment WITH PROPER REUSE:
    - 56 base patterns (7 dot numbers × 8 repetitions) with 0 connections
    - Reuse these for 1 and 2 connections
    - 168 reference patterns (12 dots, 0 connections)
    Total test patterns: 56 × 3 connectedness levels = 168
    """
    print("Generating patterns with REUSE across connectedness levels...")

    reference_patterns = []
    test_patterns_by_connectivity = {0: [], 1: [], 2: []}

    # Generate 168 reference patterns (12 dots, zero-connected)
    print(f"Generating {TRIALS_PER_HALF_BLOCK} reference patterns...")
    for i in range(TRIALS_PER_HALF_BLOCK):
        max_retries = 10
        for retry in range(max_retries):
            try:
                pattern = DotPattern(NUM_REFERENCE_DOTS, connectedness=0, pattern_id=i)
                pattern.generate()
                reference_patterns.append(pattern)
                break
            except RuntimeError:
                if retry == max_retries - 1:
                    print(f"  Failed to generate reference pattern {i}")
                    raise
                continue

        if (i + 1) % 20 == 0:
            print(f"  Generated {i + 1}/{TRIALS_PER_HALF_BLOCK} reference patterns")

    # Generate test patterns WITH REUSE
    print(f"Generating test patterns with SAME dots across connectedness levels...")
    pattern_id = 0

    for num_dots in TEST_DOT_NUMBERS:
        for rep in range(PATTERNS_PER_CONDITION):
            max_retries = 10
            for retry in range(max_retries):
                try:
                    # Generate base pattern with 0 connections (don't add to list yet!)
                    base_pattern = DotPattern(num_dots, connectedness=0, pattern_id=pattern_id)
                    base_pattern.generate()

                    # Copy dots for 1-connection version
                    base_dots = base_pattern.copy_dots()
                    pattern_1conn = DotPattern(num_dots, connectedness=1, pattern_id=pattern_id, base_dots=base_dots)
                    pattern_1conn.generate()

                    # Copy dots for 2-connection version
                    pattern_2conn = DotPattern(num_dots, connectedness=2, pattern_id=pattern_id, base_dots=base_dots)
                    pattern_2conn.generate()

                    # ONLY add to lists if ALL THREE succeeded
                    test_patterns_by_connectivity[0].append(base_pattern)
                    test_patterns_by_connectivity[1].append(pattern_1conn)
                    test_patterns_by_connectivity[2].append(pattern_2conn)

                    pattern_id += 1
                    break
                except RuntimeError:
                    # All three patterns discarded, will generate NEW dots on retry
                    if retry == max_retries - 1:
                        print(f"  Failed to generate pattern: {num_dots} dots")
                        raise
                    continue

            if pattern_id % 10 == 0:
                print(f"  Generated {pattern_id * 3}/{TRIALS_PER_HALF_BLOCK * 3} test pattern variants")

    # Interleave patterns to create proper trial list
    test_patterns = []
    for i in range(len(test_patterns_by_connectivity[0])):
        for conn in CONNECTEDNESS_LEVELS:
            test_patterns.append(test_patterns_by_connectivity[conn][i])

    print(f"Pattern generation complete!")
    print(f"  Reference patterns: {len(reference_patterns)}")
    print(f"  Test patterns: {len(test_patterns)} (same dots reused across {len(CONNECTEDNESS_LEVELS)} levels)")

    return reference_patterns, test_patterns


def create_pattern_stimulus(pattern, offset_x):
    """Create an Expyriment Canvas with the pattern rendered"""
    canvas = stimuli.Canvas(size=(PATTERN_WIDTH, PATTERN_HEIGHT),
                           colour=PATTERN_COLOR,
                           position=(offset_x, 0))

    # Draw lines first
    for ((x1, y1), (x2, y2)) in pattern.lines:
        line = stimuli.Line(start_point=(x1, y1),
                          end_point=(x2, y2),
                          line_width=LINE_WIDTH,
                          colour=LINE_COLOR)
        line.plot(canvas)

    # Draw dots on top
    for (x, y) in pattern.dots:
        dot = stimuli.Circle(radius=DOT_DIAMETER // 2,
                           colour=DOT_COLOR,
                           position=(x, y))
        dot.plot(canvas)

    return canvas


# ============================================================================
# EXPERIMENT STRUCTURE
# ============================================================================

def create_trial_list(reference_patterns, test_patterns, block_num):
    """Create trial list for one block"""
    trials = []

    indices = list(range(TRIALS_PER_HALF_BLOCK))
    random.shuffle(indices)

    for idx in indices:
        ref_pattern = reference_patterns[idx]
        test_pattern = test_patterns[idx]
        test_on_left = random.choice([True, False])

        trials.append({
            'block': block_num,
            'half': 1,
            'reference_pattern': ref_pattern,
            'test_pattern': test_pattern,
            'test_on_left': test_on_left,
            'num_dots': test_pattern.num_dots,
            'connectedness': test_pattern.connectedness
        })

    for idx in indices:
        ref_pattern = reference_patterns[idx]
        test_pattern = test_patterns[idx]
        original_trial = trials[indices.index(idx)]
        test_on_left = not original_trial['test_on_left']

        trials.append({
            'block': block_num,
            'half': 2,
            'reference_pattern': ref_pattern,
            'test_pattern': test_pattern,
            'test_on_left': test_on_left,
            'num_dots': test_pattern.num_dots,
            'connectedness': test_pattern.connectedness
        })

    return trials


def create_practice_trials(reference_patterns):
    """Create 30 practice trials"""
    trials = []

    for i in range(NUM_PRACTICE_TRIALS):
        test_pattern = DotPattern(PRACTICE_TEST_DOTS, connectedness=0)
        test_pattern.generate()

        ref_pattern = reference_patterns[i % len(reference_patterns)]
        test_on_left = random.choice([True, False])

        trials.append({
            'block': 0,
            'half': 0,
            'reference_pattern': ref_pattern,
            'test_pattern': test_pattern,
            'test_on_left': test_on_left,
            'num_dots': test_pattern.num_dots,
            'connectedness': test_pattern.connectedness,
            'is_practice': True
        })

    return trials


# ============================================================================
# TRIAL EXECUTION
# ============================================================================

def run_trial(exp, trial_info, trial_number, fixation_cross, data_logger=None):
    """Execute a single trial"""

    iti = random.randint(MIN_ITI, MAX_ITI)
    exp.clock.wait(iti)

    fixation_cross.present()
    exp.clock.wait(500)  # Show fixation for 500ms to focus attention

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

    # Pre-load stimuli for precise timing
    left_canvas = create_pattern_stimulus(left_pattern, left_offset)
    right_canvas = create_pattern_stimulus(right_pattern, right_offset)
    left_canvas.preload()
    right_canvas.preload()

    display = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    left_canvas.plot(display)
    right_canvas.plot(display)

    display.present()
    exp.clock.wait(STIMULUS_DURATION)

    blank = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    blank.present()

    key, rt = exp.keyboard.wait([expyriment.misc.constants.K_LEFT,
                                  expyriment.misc.constants.K_RIGHT])

    chose_left = (key == expyriment.misc.constants.K_LEFT)
    chose_test = (chose_left == trial_info['test_on_left'])

    exp.data.add([
        trial_info['block'],
        trial_info['half'],
        trial_info['num_dots'],
        trial_info['connectedness'],
        trial_info['test_on_left'],
        chose_left,
        chose_test,
        rt
    ])

    # Log to detailed JSON file if data_logger provided
    if data_logger:
        data_logger.log_trial(
            trial_number=trial_number,
            block=trial_info['block'],
            half=trial_info['half'],
            ref_pattern=ref_pattern,
            test_pattern=test_pattern,
            test_on_left=trial_info['test_on_left'],
            response_key=key,
            rt=rt
        )

    return chose_test


# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def run_experiment():
    """Main experiment function"""

    exp = design.Experiment(name="Connectedness_Numerosity_Exp1")
    control.initialize(exp)

    reference_patterns, test_patterns = generate_all_patterns()

    instructions = stimuli.TextScreen(
        "Numerosity Judgment Task",
        text="""You will see two patterns of dots flash briefly on the screen.

Your task is to decide which pattern contains MORE dots.

Press the LEFT arrow key if the LEFT pattern has more dots.
Press the RIGHT arrow key if the RIGHT pattern has more dots.

Keep your eyes on the green fixation cross in the center.

There is no time limit for your response.
Try to be as accurate as possible.

We will start with some practice trials.

Press SPACE to begin practice."""
    )

    fixation_cross = stimuli.FixCross(size=(20, 20),
                                     colour=(0, 255, 0),
                                     line_width=2)
    fixation_cross.preload()

    control.start(skip_ready_screen=True)

    # Initialize detailed data logger AFTER control.start
    participant_id = exp.subject
    data_logger = DetailedDataLogger(participant_id, "Connectedness_Numerosity_Exp1")

    instructions.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)

    # Practice
    practice_trials = create_practice_trials(reference_patterns)

    practice_instruction = stimuli.TextScreen(
        "Practice",
        "Practice trials - Easy discrimination (9 vs 12 dots)\n\nPress SPACE to start"
    )
    practice_instruction.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)

    trial_counter = 1
    for i, trial in enumerate(practice_trials):
        run_trial(exp, trial, trial_counter, fixation_cross, data_logger)
        trial_counter += 1

        if (i + 1) % 10 == 0:
            progress = stimuli.TextScreen(
                "Practice Progress",
                f"Completed {i + 1}/{NUM_PRACTICE_TRIALS} practice trials\n\nPress SPACE to continue"
            )
            progress.present()
            exp.keyboard.wait(expyriment.misc.constants.K_SPACE)

    end_practice = stimuli.TextScreen(
        "Practice Complete",
        "Practice is complete!\n\nThe main experiment will now begin.\n\nPress SPACE to continue"
    )
    end_practice.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)

    # Main blocks
    for block_num in range(1, NUM_BLOCKS + 1):
        block_instruction = stimuli.TextScreen(
            f"Block {block_num} of {NUM_BLOCKS}",
            f"Starting block {block_num}\n\nPress SPACE when ready"
        )
        block_instruction.present()
        exp.keyboard.wait(expyriment.misc.constants.K_SPACE)

        trials = create_trial_list(reference_patterns, test_patterns, block_num)

        for i, trial in enumerate(trials):
            run_trial(exp, trial, trial_counter, fixation_cross, data_logger)
            trial_counter += 1

            if (i + 1) % 50 == 0:
                progress = stimuli.TextScreen(
                    f"Block {block_num} Progress",
                    f"Completed {i + 1}/{len(trials)} trials in this block"
                )
                progress.present()
                exp.clock.wait(1000)

        if block_num < NUM_BLOCKS:
            break_screen = stimuli.TextScreen(
                "Break Time",
                f"Block {block_num} complete!\n\nTake a brief rest.\n\nPress SPACE when ready to continue"
            )
            break_screen.present()
            exp.keyboard.wait(expyriment.misc.constants.K_SPACE)

    # Save detailed data
    saved_file = data_logger.save()

    end_screen = stimuli.TextScreen(
        "Experiment Complete",
        f"Thank you for participating!\n\nData saved to:\n{os.path.basename(saved_file)}\n\nPlease inform the experimenter."
    )
    end_screen.present()
    exp.clock.wait(3000)

    control.end()


if __name__ == "__main__":
    run_experiment()
