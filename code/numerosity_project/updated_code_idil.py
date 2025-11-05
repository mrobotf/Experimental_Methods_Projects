"""
Experiment 1: Connectedness Affects Dot Numerosity Judgment

Based on: He, L., Zhang, J., Zhou, T., & Chen, L. (2009). 
Connectedness affects dot numerosity judgment: Implications for configural processing.
Psychonomic Bulletin & Review, 16(3), 509-517.
"""

import expyriment
from expyriment import design, control, stimuli
from expyriment.misc.constants import C_BLACK,C_GREEN, K_SPACE, K_LEFT, K_RIGHT
import random
import math
import numpy as np
from datetime import datetime

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Display settings
SCREEN_SIZE = (1024, 768)
BACKGROUND_COLOR = (0, 0, 0)  # Black background

# Pattern settings
# NOTE: Paper specifies 160×240 pixels, but this is too small to fit 15 dots
# with 42-pixel minimum spacing. We've increased to 240×320 and reduced spacing
# to 38 pixels to maintain similar density while fitting all dot numbers.
PATTERN_WIDTH = 240 # pixels (increased from 160 to fit more dots)
PATTERN_HEIGHT = 320 # pixels (increased from 240 to fit more dots)
PATTERN_COLOR = (102, 102, 102)  # Gray pattern rectangles

# Dot settings
DOT_DIAMETER = 12  # pixels
DOT_COLOR = (0, 0, 0)  # Black dots
MIN_DOT_DISTANCE = 38  # pixels (reduced from 42 to allow more dots)
MIN_DOT_BOUNDARY_DISTANCE = 10  # pixels from pattern edges

# Line settings
LINE_WIDTH = 2  # pixels
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
STIMULUS_DURATION =200  # ms
#STIMULUS_DURATION =2000
MIN_ITI = 500  # ms
MAX_ITI = 1000  # ms

# Trial organization
NUM_BLOCKS = 5
TRIALS_PER_HALF_BLOCK = 168  # 21 conditions × 8 repetitions

# Practice settings
NUM_PRACTICE_TRIALS = 30
PRACTICE_TEST_DOTS = 9  # Easy discrimination: 9 vs 12

# Positioning
HEMIFIELD_OFFSET = 200  # pixels from center


# ============================================================================
# HELPER CLASSES
# ============================================================================

class DotPattern:
    """Represents a dot pattern with dots and lines"""
    
    def __init__(self, num_dots, connectedness, pattern_id=0):
        self.num_dots = num_dots
        self.connectedness = connectedness  # 0, 1, or 2
        self.pattern_id = pattern_id
        self.dots = []  # List of (x, y) tuples
        self.lines = []  # List of ((x1, y1), (x2, y2)) tuples
        self.connected_pairs = []  # List of indices of connected dot pairs
        
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
                # Random position within pattern bounds
                x = random.randint(
                    -PATTERN_WIDTH // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                    PATTERN_WIDTH // 2 - MIN_DOT_BOUNDARY_DISTANCE
                )
                y = random.randint(
                    -PATTERN_HEIGHT // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                    PATTERN_HEIGHT // 2 - MIN_DOT_BOUNDARY_DISTANCE
                )
                
                # Check minimum distance from other dots
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
            # All lines are free-hanging
            lines = self._generate_free_lines(NUM_LINES)
        else:
            # Generate connecting lines first
            connecting_lines, self.connected_pairs = self._generate_connecting_lines(
                self.connectedness
            )
            lines.extend(connecting_lines)
            
            # Generate remaining free lines
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
            
            # Find valid pair of dots
            max_attempts = 1000
            for attempt in range(max_attempts):
                # Randomly select two dots
                idx1, idx2 = random.sample(available_dots, 2)
                x1, y1 = self.dots[idx1]
                x2, y2 = self.dots[idx2]
                
                # Check distance constraint (30-60 pixels)
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                if MIN_LINE_LENGTH <= distance <= MAX_LINE_LENGTH:
                    # Check line doesn't cross other lines
                    new_line = ((x1, y1), (x2, y2))
                    if not self._line_crosses_others(new_line, lines):
                        lines.append(new_line)
                        connected_pairs.append((idx1, idx2))
                        available_dots.remove(idx1)
                        available_dots.remove(idx2)
                        break
            else:
                # Couldn't find valid pair, try again with different dots
                pass
        
        return lines, connected_pairs
    
    def _generate_free_lines(self, num_lines):
        """Generate free-hanging lines (not touching dots)"""
        lines = []
        
        for _ in range(num_lines):
            max_attempts = 1000
            for attempt in range(max_attempts):
                # Random starting point
                x1 = random.randint(-PATTERN_WIDTH // 2 + 10, PATTERN_WIDTH // 2 - 10)
                y1 = random.randint(-PATTERN_HEIGHT // 2 + 10, PATTERN_HEIGHT // 2 - 10)
                
                # Random angle and length
                angle = random.uniform(0, 2 * math.pi)
                length = random.randint(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
                
                x2 = x1 + int(length * math.cos(angle))
                y2 = y1 + int(length * math.sin(angle))
                
                # Check boundaries
                if (abs(x2) > PATTERN_WIDTH // 2 or 
                    abs(y2) > PATTERN_HEIGHT // 2):
                    continue
                
                new_line = ((x1, y1), (x2, y2))
                
                # Check doesn't cross other lines
                if self._line_crosses_others(new_line, lines):
                    continue
                
                # Check minimum distance from dots
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
        
        # Calculate intersection using cross products
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return False  # Parallel lines
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        return 0 < t < 1 and 0 < u < 1
    
    def _line_too_close_to_dots(self, line):
        """Check if line is too close to any dot"""
        (x1, y1), (x2, y2) = line
        
        for (dx, dy) in self.dots:
            # Calculate distance from point to line segment
            dist = self._point_to_segment_distance((dx, dy), (x1, y1), (x2, y2))
            if dist < MIN_LINE_DOT_DISTANCE:
                return True
        return False
    
    def _point_to_segment_distance(self, point, seg_start, seg_end):
        """Calculate minimum distance from point to line segment"""
        px, py = point
        x1, y1 = seg_start
        x2, y2 = seg_end
        
        # Vector from start to end
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            # Degenerate segment
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        # Parameter t of closest point on line
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        # Closest point on segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)


# ============================================================================
# STIMULUS GENERATION
# ============================================================================

def generate_all_patterns():
    """
    Generate all patterns for the experiment:
    - 168 reference patterns (12 dots, 0 connections)
    - 168 test patterns (21 conditions × 8 repetitions)
    """
    print("Generating patterns...")
    
    reference_patterns = []
    test_patterns = []
    
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
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print(f"  Failed to generate reference pattern {i} after {max_retries} attempts")
                    raise
                # Try again with different random seed
                continue
        
        if (i + 1) % 20 == 0:
            print(f"  Generated {i + 1}/{TRIALS_PER_HALF_BLOCK} reference patterns")
    
    # Generate test patterns
    # 3 connectedness × 7 dot numbers × 8 repetitions = 168 patterns
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
                            print(f"  Failed to generate test pattern: {num_dots} dots, {connectedness} connections")
                            raise
                        # Try again with different random seed
                        continue
                
                if (pattern_id) % 20 == 0:
                    print(f"  Generated {pattern_id}/{TRIALS_PER_HALF_BLOCK} test patterns")
    
    print(f"Pattern generation complete!")
    print(f"  Reference patterns: {len(reference_patterns)}")
    print(f"  Test patterns: {len(test_patterns)}")
    
    return reference_patterns, test_patterns


def create_pattern_stimulus(pattern, offset_x):
    """
    Create an Expyriment Canvas with the pattern rendered
    
    Args:
        pattern: DotPattern object
        offset_x: horizontal offset from screen center
    
    Returns:
        expyriment.stimuli.Canvas
    """
    canvas = stimuli.Canvas(size=(PATTERN_WIDTH, PATTERN_HEIGHT),
                           colour=PATTERN_COLOR,
                           position=(offset_x, 0))
    
    # Draw dots
    for (x, y) in pattern.dots:
        dot = stimuli.Circle(radius=DOT_DIAMETER // 2,
                           colour=DOT_COLOR,
                           position=(x, y))
        dot.plot(canvas)
    
    # Draw lines
    for ((x1, y1), (x2, y2)) in pattern.lines:
        line = stimuli.Line(start_point=(x1, y1),
                          end_point=(x2, y2),
                          line_width=LINE_WIDTH,
                          colour=LINE_COLOR)
        line.plot(canvas)
    
    return canvas


# ============================================================================
# EXPERIMENT STRUCTURE
# ============================================================================
def create_trial_list(reference_patterns, test_patterns, block_num):
    """
    Create trial list for one block
    
    Each block has 336 trials:
    - First 168: randomized conditions and balanced positions (50% left, 50% right per condition)
    - Second 168: same conditions, reversed positions
    """
    trials = []
    
    # First half: randomized
    number_of_trials = 168
    order = list(range(number_of_trials))
    random.shuffle(order) 
    
    #84 on left, 84 on right
    left_right = [True] * (number_of_trials // 2) + [False] * (number_of_trials // 2)
    random.shuffle(left_right)
    
    for i, idx in enumerate(order):
        ref_pattern = reference_patterns[idx]
        test_pattern = test_patterns[idx]
        test_on_left = left_right[i]
        
        #Storing information for the trial
        trial_info = {
            'block': block_num,
            'half': 1,
            'reference_pattern': ref_pattern,
            'test_pattern': test_pattern,
            'test_on_left': test_on_left,
            'num_dots': test_pattern.num_dots,
            'connectedness': test_pattern.connectedness
        }
        trials.append(trial_info)
    
    # Create second half as mirrored positions
    for first_trial in trials[:number_of_trials]:
        new_trial = first_trial.copy()
        new_trial['half'] = 2
        new_trial['test_on_left'] = not first_trial['test_on_left']
        trials.append(new_trial)

    return trials

#Practice Trials
def create_practice_trials(reference_patterns):
    """Create 30 practice trials with easy discrimination (9 vs 12 dots)"""
    trials = []
    
    for i in range(NUM_PRACTICE_TRIALS):
        test_pattern = DotPattern(num_dots=9,  connectedness=0);  test_pattern.generate()
        ref_pattern  = DotPattern(num_dots=12, connectedness=0);  ref_pattern.generate()


        test_on_left = random.choice([True, False])
        
        trial_info = {
            'block': 0,  # Practice block
            'half': 0,
            'reference_pattern': ref_pattern,
            'test_pattern': test_pattern,
            'test_on_left': test_on_left,
            'num_dots': test_pattern.num_dots,
            'connectedness': test_pattern.connectedness,
            'is_practice': True
        }
        trials.append(trial_info)
    
    return trials

# ============================================================================
# TRIAL EXECUTION
# ============================================================================

#Preload and draw multiple stimuli on a single canvas.
def draw(stims, canvas):
    canvas.clear_surface()  # clears previous drawings
           
    for stim in stims:
        stim.plot(canvas)  
        
    canvas.preload() 
    canvas.present()
    
#Execute a single trial  
def run_trial(exp, trial_info, fixation_cross):
   
    # Random ITI
    iti = random.randint(MIN_ITI, MAX_ITI)
    exp.clock.wait(iti)
    
    # Show fixation cross
    fixation_cross.present()
    
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
    
    # Create composite stimulus
    left_canvas = create_pattern_stimulus(left_pattern, left_offset)
    right_canvas = create_pattern_stimulus(right_pattern, right_offset)
    
    # Combine on blank canvas
    display = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    left_canvas.plot(display)
    right_canvas.plot(display)
    fixation_cross.plot(display)
    
    # Present stimulus
    draw([left_canvas, right_canvas], display)
    exp.clock.wait(STIMULUS_DURATION)
    
    # Blank screen
    blank = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    blank.present()
    
    # Wait for response
    key, rt = exp.keyboard.wait([K_LEFT, K_RIGHT])
    
    # Determine response
    choice_side = "left" if key == K_LEFT else "right"  #Which side participant chose
    test_side = "left" if trial_info['test_on_left'] else "right" #Where test pattern was located
    chose_test = (choice_side == test_side) #True if chose the test pattern
    
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

# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def run_experiment():
    """Main experiment function"""
    
    # Create experiment
    exp = design.Experiment(name="Connectedness_Numerosity_Exp1")
    
    control.set_develop_mode(True)
    
    # Set up experiment
    control.initialize(exp)
    
    # Generate all patterns
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
    
    # Create fixation cross
    fixation_cross = stimuli.FixCross(size=(20, 20), 
                                     colour=C_GREEN,
                                     line_width=2)
    fixation_cross.preload()
    
    # Start experiment
    control.start(skip_ready_screen=True)

    instructions.present()
    exp.keyboard.wait(K_SPACE)
    
    # ========================================================================
    # PRACTICE
    # ========================================================================
    
    practice_trials = create_practice_trials(reference_patterns)
    
    practice_instruction = stimuli.TextScreen(
        "Practice",
        "Practice trials\n\nPress SPACE to start")
    
    practice_instruction.present()
    exp.keyboard.wait(K_SPACE)
    
    for trial in practice_trials:
        run_trial(exp, trial, fixation_cross)

    # End of practice 
    end_practice = stimuli.TextScreen(
        "Practice Complete",
        "Practice is complete!\n\nThe main experiment will now begin.\n\nPress SPACE to continue"
    )
    end_practice.present()
    exp.keyboard.wait(K_SPACE)
    
    # ========================================================================
    # MAIN EXPERIMENT - 5 BLOCKS
    # ========================================================================
    
    for block_num in range(1, NUM_BLOCKS + 1):
        # Block instruction
        block_instruction = stimuli.TextScreen(
            f"Block {block_num} of {NUM_BLOCKS}",
            f"Starting block {block_num}\n\nPress SPACE when ready"
        )
        block_instruction.present()
        exp.keyboard.wait(K_SPACE)
        
        # Create trials for this block
        trials = create_trial_list(reference_patterns, test_patterns, block_num)
        
        # Run trials
        for i, trial in enumerate(trials):
            run_trial(exp, trial, fixation_cross)
        
        # Break between blocks (except after last block)
        if block_num < NUM_BLOCKS:
            break_screen = stimuli.TextScreen(
                "Break Time",
                f"Block {block_num} complete!\n\nTake a rest.\n\nPress SPACE when ready to continue"
            )
            break_screen.present()
            exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    # ========================================================================
    # END OF EXPERIMENT
    # ========================================================================
    end_screen = stimuli.TextScreen(
        "Experiment Complete",
        "Thank you for participating"
    )
    end_screen.present()
    exp.clock.wait(3000)
    
    control.end()
# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    run_experiment()
