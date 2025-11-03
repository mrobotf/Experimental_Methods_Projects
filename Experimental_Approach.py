# 1. INITIALIZATION
# Import Expyriment
# Set display: 1024x768, BLACK background
# Define constants:
#  - Pattern size: 160x240 pixels
#  - Dots: 12 pixels diameter, black
#  - Lines: 2 pixels width, 30-60 pixels length, black
#  - Timing: 200ms presentation
#  - Total lines: always 4 per pattern
# Left/right hemifield presentation


import expyriment
from expyriment import design, control, stimuli
import random
import numpy as np
import math


exp = design.Experiment()
control.initialize(exp)
control.set_develop_mode()
control.start()

# Display settings
SCREEN_SIZE = (1024, 768)
BACKGROUND_COLOR = (0, 0, 0)

# Pattern settings
PATTERN_WIDTH = 160 # changed to have more dots
PATTERN_HEIGHT = 240 
PATTERN_COLOR = (102, 102, 102) 
STIMULUS_DURATION = 200
PATTERN_OFFSET_X = 300

# Dot settings
DOT_DIAMETER = 12  # pixels
DOT_COLOR = (0, 0, 0)  # Black dots
MIN_DOT_DISTANCE = 42  # pixels between the dots 
MIN_DOT_BOUNDARY_DISTANCE = 10  # pixels from pattern edges

# Line settings
LINE_WIDTH = 2  # pixels
LINE_COLOR = (0, 0, 0)  # Black lines
MIN_LINE_LENGTH = 30  
MAX_LINE_LENGTH = 60  
MIN_LINE_DOT_DISTANCE = 12  # except for connecting lines


# 2. STIMULUS GENERATION
# GENERATE 168 REFERENCE patterns:
#  - Each has: 12 dots, 4 free lines, 0 connections
#  - Random dot positions
#  - Random line positions

N_DOT = 12
N_LINE = 4
N_CONNECTION = 0    

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)


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


def generate_dots(n_dots):
    dots = []
    max_attempts = 10000
    for i in range(n_dots):
        for attempt in range(max_attempts):
            x = random.randint(
                -PATTERN_WIDTH // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                PATTERN_WIDTH // 2 - MIN_DOT_BOUNDARY_DISTANCE
            )
            y = random.randint(
                -PATTERN_HEIGHT // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                PATTERN_HEIGHT // 2 - MIN_DOT_BOUNDARY_DISTANCE
            )

    # Check if this position is far enough from other dots
            if all(distance((x,y), d) >= MIN_DOT_DISTANCE for d in dots):
                dots.append((x,y))
                break
        else:
            raise RuntimeError(f'Could not place dot {i + 1}')
    return dots

def generate_free_lines(n_line, dots, existing_lines= None):
    if existing_lines is None:
        existing_lines = []
    lines = list(existing_lines)
    max_attempts = 1000
    for line in range(n_line):
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


# Generate reference patterns
def generate_reference_pattern():
    while True:
        try:
            reference_dots = generate_dots(12)
            reference_lines = generate_free_lines(4, reference_dots)
            return reference_dots, reference_lines
        except RuntimeError:
            # If placement fails, retry the whole pattern
            continue

# GENERATE 168 TEST patterns:
#  - 3 connectedness (connectedness: 0, 1, or 2 pairs connected)
#  - 7 dot numbers conditions (Dot numbers: 9, 10, 11, 12, 13, 14, 15)
#  - 8 patterns per condition
#  - 56 patterns (7x8)
#  - 168 final pattern (for each connectedness 56 patterns)
#  - Start with free lines, then replace some with connecting lines

def generate_connecting_lines(dots, n_connection, existing_lines):
    connecting_lines = list(existing_lines)
    connected_pairs= []
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
            
            if any(point_to_segment_distance(d, p1, p2) < MIN_LINE_DOT_DISTANCE for d in dots):
                continue

            connecting_lines.append((p1, p2))
            connected_pairs.append((i1, i2))
            available_dots.remove(i1)
            available_dots.remove(i2)
            break
        
        else:
            print('Could not place a connecting line')

    return connecting_lines, connected_pairs

# Generate test pattern
def generate_test_pattern(n_dots, n_connection):
    while True:
        try:
            test_dots = generate_dots(n_dots)
            test_lines = []
            if n_connection > 0:
                test_lines, connected_pairs = generate_connecting_lines(test_dots, n_connection, test_lines)
            else:
                connected_pairs = []

            n_free = 4 - len(test_lines)
            if n_free > 0:
                test_lines += generate_free_lines(n_free, test_dots, existing_lines=test_lines)

            return test_dots, test_lines, connected_pairs
        except RuntimeError:
            continue


# GENERATE ALL REFERENCE PATTERNS
def generate_all_reference_patterns():
    """
    Generates 168 reference patterns:
    - Each has 12 dots, 4 free lines, 0 connections
    """
    all_ref_patterns = []
    for _ in range(168):
        dots, lines = generate_reference_pattern()
        pattern = {
            'dots': dots,
            'lines': lines,
            'n_dots': 12,
            'n_connection': 0
        }
        all_ref_patterns.append(pattern)
    return all_ref_patterns

# GENERATE ALL TEST PATTERNS
def generate_all_test_patterns():
    """
    Generates 168 test patterns:
    - 3 connectedness levels (0,1,2)
    - 7 dot number conditions (9-15)
    - 8 patterns per condition
    """
    all_test_patterns = []

    for n_connection in [0, 1, 2]:  # connectedness levels
        for n_dots in range(9, 16):  # dot number conditions
            for pattern_idx in range(8):  # 8 patterns per condition
                dots, lines, connected_pairs = generate_test_pattern(n_dots, n_connection)
                pattern = {
                    'dots': dots,
                    'lines': lines,
                    'pairs': connected_pairs,
                    'n_dots': n_dots,
                    'n_connection': n_connection
                }
                all_test_patterns.append(pattern)

    return all_test_patterns

reference_patterns = generate_all_reference_patterns()
test_patterns = generate_all_test_patterns() 

# Shuffle patterns
random.shuffle(reference_patterns)
random.shuffle(test_patterns)

# Randomize left/right assignment (maybe later stage to counterbalance)
ref_pattern = random.choice(reference_patterns)
test_pattern = random.choice(test_patterns)

ref_dots, ref_lines = ref_pattern['dots'], ref_pattern['lines']
test_dots, test_lines = test_pattern['dots'], test_pattern['lines']

if random.choice([True,False]):
    left_dots, left_lines = ref_dots, ref_lines
    right_dots, right_lines = test_dots, test_lines
else:
    left_dots, left_lines = test_dots, test_lines
    right_dots, right_lines = ref_dots, ref_lines

bg_left = stimuli.Rectangle((PATTERN_WIDTH, PATTERN_HEIGHT), colour=PATTERN_COLOR)
bg_left.position = (-PATTERN_OFFSET_X, 0)
bg_left.preload()

bg_right = stimuli.Rectangle((PATTERN_WIDTH, PATTERN_HEIGHT), colour=PATTERN_COLOR)
bg_right.position = (PATTERN_OFFSET_X, 0)
bg_right.preload()

# Draw dots and lines
all_stims = []
for dots, lines, x_off in [(left_dots,left_lines,-PATTERN_OFFSET_X), 
                           (right_dots,right_lines,PATTERN_OFFSET_X)]:
    for d in dots:
        dot = stimuli.Circle(DOT_DIAMETER/2, colour=DOT_COLOR)
        dot.position = (d[0]+x_off,d[1])
        dot.preload()
        all_stims.append(dot)
    for l in lines:
        line = stimuli.Line((l[0][0]+x_off,l[0][1]), 
                            (l[1][0]+x_off,l[1][1]), 
                            colour=LINE_COLOR, line_width=LINE_WIDTH)
        line.preload()
        all_stims.append(line)

# Present all
bg_left.present(clear=False, update=False)
bg_right.present(clear=False, update=False)
for stim in all_stims:
    stim.present(clear=False, update=False)
exp.screen.update()
exp.clock.wait(STIMULUS_DURATION)
control.end()
