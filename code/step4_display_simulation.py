"""
STEP 4: Display Simulation
===========================

This script shows how stimuli appear in the actual experiment:
1. Side-by-side presentation (left/right hemifields)
2. Gray rectangles on black background
3. Brief presentation timing (simulated)
4. Reference vs. Test comparison

This gives you a preview of what participants see.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines
import random
import math
import time

# ============================================================================
# CONFIGURATION - Matches Experiment
# ============================================================================

# Display
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
BACKGROUND_COLOR = (0, 0, 0)  # Black

# Patterns
PATTERN_WIDTH = 240
PATTERN_HEIGHT = 320
PATTERN_COLOR = (102/255, 102/255, 102/255)  # Gray (matplotlib uses 0-1 range)

# Positioning
HEMIFIELD_OFFSET = 200  # Distance from center

# Dot and line settings
DOT_DIAMETER = 12
MIN_DOT_DISTANCE = 38
MIN_DOT_BOUNDARY_DISTANCE = 10
LINE_WIDTH = 2
MIN_LINE_LENGTH = 30
MAX_LINE_LENGTH = 60
MIN_LINE_DOT_DISTANCE = 12

# Timing (for display purposes only - matplotlib can't do precise timing)
STIMULUS_DURATION_MS = 200


# ============================================================================
# PATTERN GENERATION (Combined from previous steps)
# ============================================================================

def generate_dots(num_dots):
    """Generate dots"""
    dots = []
    for _ in range(num_dots):
        attempts = 0
        while attempts < 10000:
            x = random.randint(-PATTERN_WIDTH // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                             PATTERN_WIDTH // 2 - MIN_DOT_BOUNDARY_DISTANCE)
            y = random.randint(-PATTERN_HEIGHT // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                             PATTERN_HEIGHT // 2 - MIN_DOT_BOUNDARY_DISTANCE)
            
            valid = all(math.sqrt((x - dx)**2 + (y - dy)**2) >= MIN_DOT_DISTANCE 
                       for dx, dy in dots)
            
            if valid:
                dots.append((x, y))
                break
            attempts += 1
        
        if attempts >= 10000:
            raise RuntimeError(f"Could not place dot")
    
    return dots


def lines_intersect(line1, line2):
    """Check intersection"""
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return False
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    return 0 < t < 1 and 0 < u < 1


def point_to_segment_distance(point, seg_start, seg_end):
    """Distance from point to segment"""
    px, py = point
    x1, y1 = seg_start
    x2, y2 = seg_end
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.sqrt((px - x1)**2 + (py - y1)**2)
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx**2 + dy**2)))
    closest_x, closest_y = x1 + t * dx, y1 + t * dy
    return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)


def generate_connecting_lines(num_connections, dots):
    """Generate connecting lines"""
    lines, connected_pairs = [], []
    available = list(range(len(dots)))
    
    for _ in range(num_connections):
        if len(available) < 2:
            break
        for _ in range(1000):
            idx1, idx2 = random.sample(available, 2)
            x1, y1 = dots[idx1]
            x2, y2 = dots[idx2]
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            if MIN_LINE_LENGTH <= distance <= MAX_LINE_LENGTH:
                new_line = ((x1, y1), (x2, y2))
                if not any(lines_intersect(new_line, l) for l in lines):
                    lines.append(new_line)
                    connected_pairs.append((idx1, idx2))
                    available.remove(idx1)
                    available.remove(idx2)
                    break
    
    return lines, connected_pairs


def generate_free_lines(num_lines, dots, existing_lines):
    """Generate free lines"""
    lines = list(existing_lines)
    
    for _ in range(num_lines):
        for _ in range(1000):
            x1 = random.randint(-PATTERN_WIDTH // 2 + 10, PATTERN_WIDTH // 2 - 10)
            y1 = random.randint(-PATTERN_HEIGHT // 2 + 10, PATTERN_HEIGHT // 2 - 10)
            angle = random.uniform(0, 2 * math.pi)
            length = random.randint(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
            x2 = x1 + int(length * math.cos(angle))
            y2 = y1 + int(length * math.sin(angle))
            
            if abs(x2) > PATTERN_WIDTH // 2 or abs(y2) > PATTERN_HEIGHT // 2:
                continue
            
            new_line = ((x1, y1), (x2, y2))
            if any(lines_intersect(new_line, l) for l in lines):
                continue
            if any(point_to_segment_distance(d, (x1, y1), (x2, y2)) < MIN_LINE_DOT_DISTANCE 
                   for d in dots):
                continue
            
            lines.append(new_line)
            break
    
    return lines


def generate_pattern(num_dots, num_connections):
    """Generate complete pattern"""
    dots = generate_dots(num_dots)
    
    if num_connections > 0:
        lines, connected_pairs = generate_connecting_lines(num_connections, dots)
    else:
        lines, connected_pairs = [], []
    
    num_free = 4 - num_connections
    if num_free > 0:
        lines = generate_free_lines(num_free, dots, lines)
    
    return dots, lines, connected_pairs


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def draw_pattern_on_axis(ax, dots, lines, x_offset, label=""):
    """
    Draw a single pattern at specified x_offset
    
    This mimics how patterns appear in the experiment:
    - Gray rectangle
    - Black dots and lines
    """
    # Gray rectangle (the pattern background)
    rect = patches.Rectangle(
        (x_offset - PATTERN_WIDTH // 2, -PATTERN_HEIGHT // 2),
        PATTERN_WIDTH,
        PATTERN_HEIGHT,
        facecolor=PATTERN_COLOR,
        edgecolor='none'
    )
    ax.add_patch(rect)
    
    # Draw lines
    for ((x1, y1), (x2, y2)) in lines:
        line = mlines.Line2D(
            [x1 + x_offset, x2 + x_offset],
            [y1, y2],
            linewidth=LINE_WIDTH,
            color='black'
        )
        ax.add_line(line)
    
    # Draw dots
    for (x, y) in dots:
        circle = patches.Circle(
            (x + x_offset, y),
            radius=DOT_DIAMETER / 2,
            color='black'
        )
        ax.add_patch(circle)
    
    # Label
    if label:
        ax.text(x_offset, PATTERN_HEIGHT // 2 + 30, label,
               ha='center', va='bottom',
               fontsize=12, color='white', weight='bold')


def display_trial(ref_dots, ref_lines, test_dots, test_lines, test_connections,
                  test_on_left=True, show_info=True):
    """
    Display a trial as it appears in the experiment
    
    Args:
        ref_dots, ref_lines: reference pattern (always 12 dots, 0 connections)
        test_dots, test_lines: test pattern
        test_connections: number of connections in test (0, 1, or 2)
        test_on_left: which side the test appears
        show_info: whether to show helpful information
    """
    # Create figure with black background
    fig = plt.figure(figsize=(12, 8), facecolor='black')
    ax = fig.add_subplot(111, facecolor='black')
    
    # Determine positions
    if test_on_left:
        left_dots, left_lines = test_dots, test_lines
        right_dots, right_lines = ref_dots, ref_lines
        left_label = f"TEST: {len(test_dots)} dots, {test_connections} connections"
        right_label = f"REFERENCE: {len(ref_dots)} dots, 0 connections"
    else:
        left_dots, left_lines = ref_dots, ref_lines
        right_dots, right_lines = test_dots, test_lines
        left_label = f"REFERENCE: {len(ref_dots)} dots, 0 connections"
        right_label = f"TEST: {len(test_dots)} dots, {test_connections} connections"
    
    # Draw both patterns
    draw_pattern_on_axis(ax, left_dots, left_lines, -HEMIFIELD_OFFSET, 
                        left_label if show_info else "")
    draw_pattern_on_axis(ax, right_dots, right_lines, HEMIFIELD_OFFSET,
                        right_label if show_info else "")
    
    # Fixation cross (green, at center)
    cross_size = 20
    ax.plot([0, 0], [-cross_size//2, cross_size//2], 
           color='green', linewidth=2)
    ax.plot([-cross_size//2, cross_size//2], [0, 0],
           color='green', linewidth=2)
    
    # Set axis limits to match screen
    ax.set_xlim(-SCREEN_WIDTH // 2, SCREEN_WIDTH // 2)
    ax.set_ylim(-SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add instruction
    if show_info:
        instruction = "Which side has MORE dots?\nPress LEFT or RIGHT arrow"
        ax.text(0, -SCREEN_HEIGHT // 2 + 50, instruction,
               ha='center', va='bottom',
               fontsize=14, color='white')
        
        # Show timing info
        timing_text = f"Presentation duration: {STIMULUS_DURATION_MS} ms"
        ax.text(0, SCREEN_HEIGHT // 2 - 30, timing_text,
               ha='center', va='top',
               fontsize=10, color='yellow')
    
    plt.tight_layout()
    return fig


# ============================================================================
# DEMONSTRATION SCENARIOS
# ============================================================================

def demo_easy_trial():
    """Easy discrimination: 9 vs 12 dots (practice trial)"""
    print("\n" + "="*60)
    print("DEMO 1: Easy Trial (Practice)")
    print("="*60)
    print("9 dots vs 12 dots - easy to discriminate")
    
    ref_dots, ref_lines, _ = generate_pattern(12, 0)
    test_dots, test_lines, _ = generate_pattern(9, 0)
    
    fig = display_trial(ref_dots, ref_lines, test_dots, test_lines, 0,
                       test_on_left=random.choice([True, False]))
    plt.show()


def demo_connectedness_effect():
    """Show the connectedness manipulation"""
    print("\n" + "="*60)
    print("DEMO 2: Connectedness Effect")
    print("="*60)
    print("Same number of dots (12), different connectedness")
    
    # Reference: 12 dots, 0 connections
    ref_dots, ref_lines, _ = generate_pattern(12, 0)
    
    # Test conditions
    for num_connections in [0, 1, 2]:
        print(f"\nShowing: 12 dots, {num_connections} connections")
        test_dots, test_lines, _ = generate_pattern(12, num_connections)
        
        fig = display_trial(ref_dots, ref_lines, test_dots, test_lines,
                          num_connections, test_on_left=True)
        plt.show()


def demo_hard_trial():
    """Difficult discrimination: 13 vs 12 with 2 connections"""
    print("\n" + "="*60)
    print("DEMO 3: Difficult Trial")
    print("="*60)
    print("13 dots (2 connected) vs 12 dots (0 connected)")
    print("Hypothesis: 13 connected dots LOOK like ~12 dots")
    
    ref_dots, ref_lines, _ = generate_pattern(12, 0)
    test_dots, test_lines, _ = generate_pattern(13, 2)
    
    fig = display_trial(ref_dots, ref_lines, test_dots, test_lines, 2,
                       test_on_left=random.choice([True, False]))
    plt.show()


def demo_trial_sequence():
    """Show a sequence of trials"""
    print("\n" + "="*60)
    print("DEMO 4: Trial Sequence")
    print("="*60)
    print("Showing 3 consecutive trials...")
    
    # Generate reference once
    ref_dots, ref_lines, _ = generate_pattern(12, 0)
    
    trials = [
        (11, 1, "11 dots, 1 connection"),
        (12, 0, "12 dots, 0 connections"),
        (14, 2, "14 dots, 2 connections"),
    ]
    
    for num_dots, connections, description in trials:
        print(f"\nTrial: {description}")
        test_dots, test_lines, _ = generate_pattern(num_dots, connections)
        
        fig = display_trial(ref_dots, ref_lines, test_dots, test_lines,
                          connections, test_on_left=random.choice([True, False]))
        
        plt.suptitle(f"Trial: {description}", 
                    color='white', fontsize=14, y=0.98)
        plt.show()


def demo_without_labels():
    """Show how it actually looks (no helpful labels)"""
    print("\n" + "="*60)
    print("DEMO 5: Actual Appearance (No Labels)")
    print("="*60)
    print("This is how participants see it - NO helpful information!")
    
    ref_dots, ref_lines, _ = generate_pattern(12, 0)
    test_dots, test_lines, _ = generate_pattern(13, 2)
    
    fig = display_trial(ref_dots, ref_lines, test_dots, test_lines, 2,
                       test_on_left=True, show_info=False)
    
    plt.suptitle("What participants see (200ms flash)", 
                color='white', fontsize=14, y=0.98)
    plt.show()


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    """Run all demonstrations"""
    
    print("="*60)
    print("STEP 4: DISPLAY SIMULATION")
    print("="*60)
    
    print("\nThis shows how stimuli appear in the actual experiment:")
    print("- Black background (RGB 0,0,0)")
    print("- Gray pattern rectangles (RGB 102,102,102)")  
    print("- Side-by-side presentation")
    print("- Green fixation cross at center")
    print("- Brief flash (200ms - simulated here with static images)")
    
    print("\nYou will see 5 demonstrations:")
    print("1. Easy trial (practice)")
    print("2. Connectedness effect (0, 1, 2 connections)")
    print("3. Difficult trial")
    print("4. Trial sequence")
    print("5. Actual appearance (no labels)")
    
    input("\nPress ENTER to start demonstrations...")
    
    demo_easy_trial()
    demo_connectedness_effect()
    demo_hard_trial()
    demo_trial_sequence()
    demo_without_labels()
    
    print("\n" + "="*60)
    print("STEP 4 COMPLETE")
    print("="*60)
    print("\nKey Takeaways:")
    print("✓ Patterns appear on gray rectangles (not full black screen)")
    print("✓ Side-by-side comparison (left vs right)")
    print("✓ Green fixation cross helps maintain focus")
    print("✓ 200ms is VERY brief - impossible to count")
    print("✓ Connectedness makes dots 'look like' fewer")
    print("\nNext: Step 5 will show the timing and response collection")


if __name__ == "__main__":
    main()
