"""
Connectedness & Numerosity Experiment
Presentation Demo Version
"""

import expyriment
from expyriment import design, control, stimuli
import random
import math
import copy

# ============================================================================
# CONFIGURATION
# ============================================================================

SCREEN_SIZE = (1024, 768)
BACKGROUND_COLOR = (0, 0, 0)

# Pattern settings
PATTERN_WIDTH = 280
PATTERN_HEIGHT = 360
PATTERN_COLOR = (102, 102, 102)

# Dot settings
DOT_DIAMETER = 12
DOT_COLOR = (0, 0, 0)
MIN_DOT_DISTANCE = 42
MIN_DOT_BOUNDARY_DISTANCE = 20

# Line settings
LINE_WIDTH = 5
LINE_COLOR = (0, 0, 0)
MIN_LINE_LENGTH = 30
MAX_LINE_LENGTH = 60
MIN_LINE_DOT_DISTANCE = 12

# Experimental settings
NUM_REFERENCE_DOTS = 12
NUM_LINES = 4
HEMIFIELD_OFFSET = 220

# ============================================================================
# PATTERN GENERATION
# ============================================================================

class DotPattern:
    """Represents a dot pattern with dots and lines"""
    
    def __init__(self, num_dots, connectedness, pattern_id=0, base_dots=None):
        self.num_dots = num_dots
        self.connectedness = connectedness
        self.pattern_id = pattern_id
        self.dots = base_dots if base_dots is not None else []
        self.lines = []
        self.connected_pairs = []
        
    def generate(self):
        """Generate the complete pattern with constraints"""
        if not self.dots:
            self.dots = self._generate_dots()
        self.lines = self._generate_lines()
        
    def copy_dots(self):
        """Return a copy of the dot configuration"""
        return copy.deepcopy(self.dots)
        
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
            
            num_free = NUM_LINES - self.connectedness
            if num_free > 0:
                free_lines = self._generate_free_lines(num_free)
                lines.extend(free_lines)
        
        return lines
    
    def _generate_connecting_lines(self, num_connections):
        """Generate lines connecting pairs of dots"""
        lines = []
        connected_pairs = []
        available_dots = list(range(len(self.dots)))
        random.shuffle(available_dots)
        
        for _ in range(num_connections):
            if len(available_dots) < 2:
                raise RuntimeError("Not enough dots for connections")
            
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
                print(f"Warning: Could only create {len(connected_pairs)} of {num_connections} connections")
                break
        
        return lines, connected_pairs
    
    def _generate_free_lines(self, num_lines):
        """Generate free-hanging lines"""
        lines = []
        
        for _ in range(num_lines):
            max_attempts = 1000
            for attempt in range(max_attempts):
                x1 = random.randint(-PATTERN_WIDTH // 2 + 15, PATTERN_WIDTH // 2 - 15)
                y1 = random.randint(-PATTERN_HEIGHT // 2 + 15, PATTERN_HEIGHT // 2 - 15)
                
                angle = random.uniform(0, 2 * math.pi)
                length = random.randint(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
                
                x2 = x1 + int(length * math.cos(angle))
                y2 = y1 + int(length * math.sin(angle))
                
                if (abs(x2) > PATTERN_WIDTH // 2 - 5 or 
                    abs(y2) > PATTERN_HEIGHT // 2 - 5):
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
    
    def _line_too_close_to_other_dots(self, line, idx1, idx2):
        """Check if connecting line is too close to dots OTHER than the connected ones"""
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


def create_labeled_pattern(pattern, offset_x, label_text):
    """Create pattern with label"""
    canvas = stimuli.Canvas(size=(PATTERN_WIDTH, PATTERN_HEIGHT + 100),
                           colour=BACKGROUND_COLOR,
                           position=(offset_x, 0))
    
    # Pattern at top
    rect = stimuli.Rectangle(size=(PATTERN_WIDTH, PATTERN_HEIGHT),
                            colour=PATTERN_COLOR,
                            position=(0, -30))
    rect.plot(canvas)
    
    for (x, y) in pattern.dots:
        dot = stimuli.Circle(radius=DOT_DIAMETER // 2,
                           colour=DOT_COLOR,
                           position=(x, y - 30))
        dot.plot(canvas)
    
    for ((x1, y1), (x2, y2)) in pattern.lines:
        line = stimuli.Line(start_point=(x1, y1 - 30),
                          end_point=(x2, y2 - 30),
                          line_width=LINE_WIDTH,
                          colour=LINE_COLOR)
        line.plot(canvas)
    
    # Label BELOW pattern - visible
    label = stimuli.TextLine(label_text, 
                            text_size=32,
                            text_colour=(255, 255, 255),
                            position=(0, PATTERN_HEIGHT // 2 + 40))
    label.plot(canvas)
    
    return canvas


def show_title(exp, text):
    """Show title screen"""
    screen = stimuli.TextScreen(
        heading=text,
        text="[Press SPACE]",
        heading_size=48,
        text_size=28,
        text_colour=(200, 200, 200),
        heading_colour=(255, 255, 255)
    )
    screen.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)


def show_patterns_extended(exp, left_pattern, right_pattern, left_label, right_label, bottom_text=""):
    """Show patterns with labels"""
    left_canvas = create_labeled_pattern(left_pattern, -HEMIFIELD_OFFSET, left_label)
    right_canvas = create_labeled_pattern(right_pattern, HEMIFIELD_OFFSET, right_label)
    
    display = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    left_canvas.plot(display)
    right_canvas.plot(display)
    
    if bottom_text:
        instruction = stimuli.TextLine(
            bottom_text,
            text_size=26,
            text_colour=(255, 255, 255),
            position=(0, -360)
        )
        instruction.plot(display)
    
    display.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)


def flash_patterns(exp, left_canvas_preloaded, right_canvas_preloaded, fixation_cross):
    """Flash patterns briefly (200ms)"""
    fixation_cross.present()
    exp.clock.wait(500)
    
    display = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    left_canvas_preloaded.plot(display)
    right_canvas_preloaded.plot(display)
    
    display.present()
    exp.clock.wait(200)
    
    blank = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    blank.present()


def run_demo_trial(exp, title, ref_pattern, test_pattern, test_on_left, fixation_cross):
    """Run one demo trial"""
    
    show_title(exp, title)
    
    if test_on_left:
        left_pattern = test_pattern
        right_pattern = ref_pattern
        left_label = f"{test_pattern.num_dots} dots, {test_pattern.connectedness} connected"
        right_label = f"{ref_pattern.num_dots} dots (reference)"
    else:
        left_pattern = ref_pattern
        right_pattern = test_pattern
        left_label = f"{ref_pattern.num_dots} dots (reference)"
        right_label = f"{test_pattern.num_dots} dots, {test_pattern.connectedness} connected"
    
    show_patterns_extended(exp, left_pattern, right_pattern, left_label, right_label, 
                          "Which has MORE dots? [SPACE to see flash]")
    
    left_canvas_preloaded = create_pattern_stimulus(left_pattern, -HEMIFIELD_OFFSET)
    right_canvas_preloaded = create_pattern_stimulus(right_pattern, HEMIFIELD_OFFSET)
    left_canvas_preloaded.preload()
    right_canvas_preloaded.preload()
    
    flash_patterns(exp, left_canvas_preloaded, right_canvas_preloaded, fixation_cross)
    
    exp.clock.wait(500)
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)


def generate_pattern_set(num_dots_test):
    """
    Generate patterns with SAME dot configuration but different connectedness
    """
    base_pattern = DotPattern(num_dots_test, connectedness=0)
    base_pattern.generate()
    
    base_dots = base_pattern.copy_dots()
    
    pattern_1conn = DotPattern(num_dots_test, connectedness=1, base_dots=base_dots)
    pattern_1conn.generate()
    
    pattern_2conn = DotPattern(num_dots_test, connectedness=2, base_dots=base_dots)
    pattern_2conn.generate()
    
    return base_pattern, pattern_1conn, pattern_2conn


def run_presentation():
    """Main presentation"""
    exp = design.Experiment(name="Connectedness_Demo")
    control.initialize(exp)
    
    welcome = stimuli.TextScreen(
        "Connectedness & Numerosity",
        text="""Demonstration

Practice trials + Connection examples

Press SPACE to continue""",
        heading_size=52,
        text_size=32
    )
    
    control.start(skip_ready_screen=True)
    welcome.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    loading = stimuli.TextScreen(
        "Generating patterns...", 
        text="Please wait",
        heading_size=42,
        text_size=28
    )
    loading.present()
    
    fixation_cross = stimuli.FixCross(size=(20, 20), 
                                     colour=(0, 255, 0),
                                     line_width=2)
    fixation_cross.preload()
    
    # PRACTICE TRIALS
    practice_ref = DotPattern(12, 0)
    practice_ref.generate()
    
    practice_test_1 = DotPattern(9, 0)
    practice_test_1.generate()
    
    practice_test_2 = DotPattern(9, 0)
    practice_test_2.generate()
    
    # MAIN EXAMPLES
    pattern_12_0conn, pattern_12_1conn, pattern_12_2conn = generate_pattern_set(12)
    pattern_13_0conn, pattern_13_1conn, pattern_13_2conn = generate_pattern_set(13)
    pattern_14_0conn, pattern_14_1conn, pattern_14_2conn = generate_pattern_set(14)
    
    ref_pattern = DotPattern(12, 0)
    ref_pattern.generate()
    
    # PRACTICE TRIALS
    show_title(exp, "PRACTICE TRIALS")
    
    run_demo_trial(exp, "Practice Trial 1", 
                   practice_ref, practice_test_1, True, fixation_cross)
    
    run_demo_trial(exp, "Practice Trial 2", 
                   practice_ref, practice_test_2, False, fixation_cross)
    
    # 0 CONNECTIONS
    show_title(exp, "0 CONNECTIONS")
    
    run_demo_trial(exp, "Equal (12 vs 12)", 
                   ref_pattern, pattern_12_0conn, True, fixation_cross)
    
    run_demo_trial(exp, "Different (12 vs 14)", 
                   ref_pattern, pattern_14_0conn, False, fixation_cross)
    
    # 1 CONNECTION
    show_title(exp, "1 CONNECTION")
    
    run_demo_trial(exp, "12 vs 13 (1 connection)", 
                   ref_pattern, pattern_13_1conn, True, fixation_cross)
    
    # 2 CONNECTIONS
    show_title(exp, "2 CONNECTIONS")
    
    run_demo_trial(exp, "12 vs 13 (2 connections)", 
                   ref_pattern, pattern_13_2conn, False, fixation_cross)
    
    run_demo_trial(exp, "12 vs 14 (2 connections)", 
                   ref_pattern, pattern_14_2conn, True, fixation_cross)
    
    end_screen = stimuli.TextScreen(
        "Demonstration Complete",
        text="""Thank you!

Press SPACE to exit""",
        heading_size=52,
        text_size=32
    )
    end_screen.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    control.end()


if __name__ == "__main__":
    run_presentation()
