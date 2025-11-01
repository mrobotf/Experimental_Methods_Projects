"""
TEST VERSION - Quick test with fewer patterns
Use this to verify the script works before running the full experiment
"""

import expyriment
from expyriment import design, control, stimuli
import random
import math
import numpy as np

# ============================================================================
# REDUCED CONFIGURATION FOR TESTING
# ============================================================================

SCREEN_SIZE = (1024, 768)
BACKGROUND_COLOR = (0, 0, 0)

# Pattern settings
PATTERN_WIDTH = 240
PATTERN_HEIGHT = 320
PATTERN_COLOR = (102, 102, 102)

# Dot settings
DOT_DIAMETER = 12
DOT_COLOR = (0, 0, 0)
MIN_DOT_DISTANCE = 38
MIN_DOT_BOUNDARY_DISTANCE = 10

# Line settings
LINE_WIDTH = 2
LINE_COLOR = (0, 0, 0)
MIN_LINE_LENGTH = 30
MAX_LINE_LENGTH = 60
MIN_LINE_DOT_DISTANCE = 12

# REDUCED EXPERIMENTAL SETTINGS FOR TESTING
NUM_REFERENCE_DOTS = 12
NUM_LINES = 4
TEST_DOT_NUMBERS = [9, 12, 15]  # Only 3 levels instead of 7
CONNECTEDNESS_LEVELS = [0, 2]  # Only 2 levels instead of 3
PATTERNS_PER_CONDITION = 2  # Only 2 instead of 8

# Timing
STIMULUS_DURATION = 200
MIN_ITI = 500
MAX_ITI = 1000

# REDUCED TRIAL ORGANIZATION
NUM_BLOCKS = 1  # Only 1 block instead of 5
TRIALS_PER_HALF_BLOCK = len(TEST_DOT_NUMBERS) * len(CONNECTEDNESS_LEVELS) * PATTERNS_PER_CONDITION  # 12 trials

NUM_PRACTICE_TRIALS = 5  # Only 5 instead of 30
PRACTICE_TEST_DOTS = 9

HEMIFIELD_OFFSET = 200

print(f"TEST MODE: {TRIALS_PER_HALF_BLOCK * 2} trials per block")


# ============================================================================
# Copy all the class definitions and functions from the main script
# (DotPattern class, generate_all_patterns, etc.)
# ============================================================================

class DotPattern:
    """Represents a dot pattern with dots and lines"""
    
    def __init__(self, num_dots, connectedness, pattern_id=0):
        self.num_dots = num_dots
        self.connectedness = connectedness
        self.pattern_id = pattern_id
        self.dots = []
        self.lines = []
        self.connected_pairs = []
        
    def generate(self):
        """Generate the complete pattern with constraints"""
        self.dots = self._generate_dots()
        self.lines = self._generate_lines()
        
    def _generate_dots(self):
        """Generate random dot positions with constraints"""
        dots = []
        max_attempts = 10000
        
        for _ in range(self.num_dots):
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
                raise RuntimeError(f"Could not place dot {len(dots)+1}/{self.num_dots}")
        
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
            
            num_free = NUM_LINES - self.connectedness
            free_lines = self._generate_free_lines(num_free)
            lines.extend(free_lines)
        
        return lines
    
    def _generate_connecting_lines(self, num_connections):
        """Generate lines connecting pairs of dots"""
        lines = []
        connected_pairs = []
        available_dots = list(range(len(self.dots)))
        
        for _ in range(num_connections):
            if len(available_dots) < 2:
                raise RuntimeError("Not enough dots for connections")
            
            max_attempts = 1000
            for attempt in range(max_attempts):
                idx1, idx2 = random.sample(available_dots, 2)
                x1, y1 = self.dots[idx1]
                x2, y2 = self.dots[idx2]
                
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                if MIN_LINE_LENGTH <= distance <= MAX_LINE_LENGTH:
                    new_line = ((x1, y1), (x2, y2))
                    if not self._line_crosses_others(new_line, lines):
                        lines.append(new_line)
                        connected_pairs.append((idx1, idx2))
                        available_dots.remove(idx1)
                        available_dots.remove(idx2)
                        break
        
        return lines, connected_pairs
    
    def _generate_free_lines(self, num_lines):
        """Generate free-hanging lines"""
        lines = []
        
        for _ in range(num_lines):
            max_attempts = 1000
            for attempt in range(max_attempts):
                x1 = random.randint(-PATTERN_WIDTH // 2 + 10, PATTERN_WIDTH // 2 - 10)
                y1 = random.randint(-PATTERN_HEIGHT // 2 + 10, PATTERN_HEIGHT // 2 - 10)
                
                angle = random.uniform(0, 2 * math.pi)
                length = random.randint(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
                
                x2 = x1 + int(length * math.cos(angle))
                y2 = y1 + int(length * math.sin(angle))
                
                if (abs(x2) > PATTERN_WIDTH // 2 or 
                    abs(y2) > PATTERN_HEIGHT // 2):
                    continue
                
                new_line = ((x1, y1), (x2, y2))
                
                if self._line_crosses_others(new_line, lines):
                    continue
                
                if not self._line_too_close_to_dots(new_line):
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
    
    def _line_too_close_to_dots(self, line):
        """Check if line is too close to any dot"""
        (x1, y1), (x2, y2) = line
        
        for (dx, dy) in self.dots:
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


def generate_all_patterns():
    """Generate patterns for test version"""
    print("Generating TEST patterns...")
    
    reference_patterns = []
    test_patterns = []
    
    print(f"Generating {TRIALS_PER_HALF_BLOCK} reference patterns...")
    for i in range(TRIALS_PER_HALF_BLOCK):
        max_retries = 10
        for retry in range(max_retries):
            try:
                pattern = DotPattern(NUM_REFERENCE_DOTS, connectedness=0, pattern_id=i)
                pattern.generate()
                reference_patterns.append(pattern)
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print(f"  Failed after {max_retries} attempts")
                    raise
                continue
    
    print(f"Generating {TRIALS_PER_HALF_BLOCK} test patterns...")
    pattern_id = 0
    
    for connectedness in CONNECTEDNESS_LEVELS:
        for num_dots in TEST_DOT_NUMBERS:
            for rep in range(PATTERNS_PER_CONDITION):
                max_retries = 10
                for retry in range(max_retries):
                    try:
                        pattern = DotPattern(num_dots, connectedness, pattern_id)
                        pattern.generate()
                        test_patterns.append(pattern)
                        pattern_id += 1
                        break
                    except RuntimeError as e:
                        if retry == max_retries - 1:
                            print(f"  Failed: {num_dots} dots, {connectedness} connections")
                            raise
                        continue
    
    print(f"Pattern generation complete!")
    print(f"  Reference: {len(reference_patterns)}, Test: {len(test_patterns)}")
    
    return reference_patterns, test_patterns


def create_pattern_stimulus(pattern, offset_x):
    """Create Canvas with pattern"""
    canvas = stimuli.Canvas(size=(PATTERN_WIDTH, PATTERN_HEIGHT),
                           colour=PATTERN_COLOR,
                           position=(offset_x, 0))
    
    for (x, y) in pattern.dots:
        dot = stimuli.Circle(radius=DOT_DIAMETER // 2,
                           colour=DOT_COLOR,
                           position=(x, y))
        dot.plot(canvas)
    
    for ((x1, y1), (x2, y2)) in pattern.lines:
        line = stimuli.Line(start_point=(x1, y1),
                          end_point=(x2, y2),
                          line_width=LINE_WIDTH,
                          colour=LINE_COLOR)
        line.plot(canvas)
    
    return canvas


def create_trial_list(reference_patterns, test_patterns, block_num):
    """Create trial list"""
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
    """Create practice trials"""
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


def run_trial(exp, trial_info, fixation_cross):
    """Execute trial"""
    iti = random.randint(MIN_ITI, MAX_ITI)
    exp.clock.wait(iti)
    
    fixation_cross.present()
    
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
    
    return chose_test


def run_experiment():
    """Main experiment"""
    exp = design.Experiment(name="Connectedness_Test")
    control.initialize(exp)
    
    reference_patterns, test_patterns = generate_all_patterns()
    
    instructions = stimuli.TextScreen(
        "TEST VERSION - Quick Test",
        text=f"""This is a quick test with only {TRIALS_PER_HALF_BLOCK * 2} trials.

You will see two patterns flash briefly.
Press LEFT or RIGHT arrow to indicate which has MORE dots.

Press SPACE to start."""
    )
    
    fixation_cross = stimuli.FixCross(size=(20, 20), 
                                     colour=(0, 255, 0),
                                     line_width=2)
    fixation_cross.preload()
    
    control.start(skip_ready_screen=True)
    
    instructions.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    # Practice
    practice_trials = create_practice_trials(reference_patterns)
    
    for trial in practice_trials:
        run_trial(exp, trial, fixation_cross)
    
    practice_done = stimuli.TextScreen("Practice Done", "Press SPACE for main trials")
    practice_done.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    # Main trials
    trials = create_trial_list(reference_patterns, test_patterns, 1)
    
    for i, trial in enumerate(trials):
        run_trial(exp, trial, fixation_cross)
        
        if (i + 1) == len(trials) // 2:
            halfway = stimuli.TextScreen("Halfway!", "Press SPACE to continue")
            halfway.present()
            exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    end_screen = stimuli.TextScreen("Test Complete!", "Thank you!")
    end_screen.present()
    exp.clock.wait(2000)
    
    control.end()


if __name__ == "__main__":
    run_experiment()
