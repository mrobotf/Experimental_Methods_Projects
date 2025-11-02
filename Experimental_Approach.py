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
            valid = True
            for (dx, dy) in dots:
                distance = math.sqrt((x - dx)**2 + (y - dy)**2)
                if distance < MIN_DOT_DISTANCE:
                    valid = False
                    break
    
            if valid:
                dots.append((x, y))
                break
        else:
            raise RuntimeError(f'Could not place dot {i + 1}')
    return dots


def generate_free_lines(n_line):
    lines = []
    for line in range(n_line):
        x1 = random.randint(-PATTERN_WIDTH // 2, PATTERN_WIDTH // 2)
        y1 = random.randint(-PATTERN_HEIGHT // 2, PATTERN_HEIGHT // 2)
        angle = random.uniform(0, 2 * math.pi)
        length = random.uniform(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
        x2 = x1 + length * math.cos(angle)
        y2 = y1 + length * math.sin(angle)
        lines.append(((x1, y1), (x2, y2)))
    return lines


# Generate patterns
reference_dots = generate_dots(N_DOT)
reference_lines = generate_free_lines(N_LINE)

test_dots = generate_dots(N_DOT)
test_lines = generate_free_lines(N_LINE)

# Randomize left/right assignment (maybe later stage to counterbalance)
if random.choice([True, False]):
    left_dots, left_lines = reference_dots, reference_lines
    right_dots, right_lines = test_dots, test_lines
else:
    left_dots, left_lines = test_dots, test_lines
    right_dots, right_lines = reference_dots, reference_lines

bg_left = stimuli.Rectangle((PATTERN_WIDTH, PATTERN_HEIGHT), colour=PATTERN_COLOR)
bg_left.position = (-PATTERN_OFFSET_X, 0)
bg_left.preload()

bg_right = stimuli.Rectangle((PATTERN_WIDTH, PATTERN_HEIGHT), colour=PATTERN_COLOR)
bg_right.position = (PATTERN_OFFSET_X, 0)
bg_right.preload()

# Preload dots
for x, y in left_dots:
    dot = stimuli.Circle(DOT_DIAMETER/2, colour=DOT_COLOR)
    dot.position = (x - PATTERN_OFFSET_X, y)
    dot.preload()

# Preload lines
for (x1, y1), (x2, y2) in left_lines:
    line = stimuli.Line((x1 - PATTERN_OFFSET_X, y1), (x2 - PATTERN_OFFSET_X, y2),
                        colour=LINE_COLOR, line_width=LINE_WIDTH)
    line.preload()

# Present dot on the buffer
left_dot_stims = []
for x, y in left_dots:
    dot = stimuli.Circle(DOT_DIAMETER / 2, colour=DOT_COLOR)
    dot.position = (x - PATTERN_OFFSET_X, y)
    dot.preload()
    left_dot_stims.append(dot)

right_dot_stims = []
for x, y in right_dots:
    dot = stimuli.Circle(DOT_DIAMETER / 2, colour=DOT_COLOR)
    dot.position = (x + PATTERN_OFFSET_X, y)
    dot.preload()
    right_dot_stims.append(dot)

left_line_stims = []
for (x1, y1), (x2, y2) in left_lines:
    line = stimuli.Line((x1 - PATTERN_OFFSET_X, y1), (x2 - PATTERN_OFFSET_X, y2),
                        colour=LINE_COLOR, line_width=LINE_WIDTH)
    line.preload()
    left_line_stims.append(line)

right_line_stims = []
for (x1, y1), (x2, y2) in right_lines:
    line = stimuli.Line((x1 + PATTERN_OFFSET_X, y1), (x2 + PATTERN_OFFSET_X, y2),
                        colour=LINE_COLOR, line_width=LINE_WIDTH)
    line.preload()
    right_line_stims.append(line)

bg_left.present(clear=False, update = False)
bg_right.present(clear=False, update = False)
for stim in left_dot_stims + right_dot_stims + left_line_stims + right_line_stims:
    stim.present(clear=False, update = False)

# left_dot_stims[0].present(clear=False, update = True) 
exp.screen.update()
exp.clock.wait(STIMULUS_DURATION)

control.end()