"""
STEP 3: Connecting Lines (Dot-to-Dot)
======================================

This script shows how to:
1. Generate lines that connect pairs of dots
2. Find suitable dot pairs within distance constraints
3. Combine connecting lines with free-hanging lines
4. Visualize the connectedness effect

This is the KEY manipulation in the experiment!
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines
import random
import math

# ============================================================================
# CONFIGURATION
# ============================================================================

PATTERN_WIDTH = 240
PATTERN_HEIGHT = 320

DOT_DIAMETER = 12
MIN_DOT_DISTANCE = 38
MIN_DOT_BOUNDARY_DISTANCE = 10

LINE_WIDTH = 2
MIN_LINE_LENGTH = 30  # For CONNECTING lines: minimum distance between dots
MAX_LINE_LENGTH = 60  # For CONNECTING lines: maximum distance between dots
MIN_LINE_DOT_DISTANCE = 12  # For FREE lines only


# ============================================================================
# HELPER FUNCTIONS (from previous steps)
# ============================================================================

def generate_dots(num_dots):
    """Generate dots"""
    dots = []
    max_attempts = 10000
    
    for _ in range(num_dots):
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
            raise RuntimeError(f"Could not place dot {len(dots)+1}/{num_dots}")
    
    return dots


def lines_intersect(line1, line2):
    """Check if two line segments intersect"""
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return False
    
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    return 0 < t < 1 and 0 < u < 1


def point_to_segment_distance(point, seg_start, seg_end):
    """Calculate distance from point to line segment"""
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
# CONNECTING LINE GENERATION
# ============================================================================

def generate_connecting_lines(num_connections, dots, existing_lines=[]):
    """
    Generate lines that connect pairs of dots
    
    Key differences from free lines:
    - Line endpoints MUST be at dot centers
    - Distance constraint: MIN_LINE_LENGTH <= distance <= MAX_LINE_LENGTH
    - Once a dot is connected, it's "used up" (can't connect again)
    - Still must not cross other lines
    
    Args:
        num_connections: how many pairs of dots to connect
        dots: list of (x, y) dot positions
        existing_lines: any lines already present
    
    Returns:
        (lines, connected_pairs)
        - lines: list of ((x1, y1), (x2, y2))
        - connected_pairs: list of (idx1, idx2) showing which dots are connected
    """
    lines = list(existing_lines)
    connected_pairs = []
    available_dots = list(range(len(dots)))  # Indices of dots not yet connected
    
    print(f"\nGenerating {num_connections} connecting lines...")
    
    for conn_num in range(num_connections):
        if len(available_dots) < 2:
            print(f"  ⚠️  Only {len(available_dots)} dots available, can't make more connections")
            break
        
        max_attempts = 1000
        placed = False
        
        for attempt in range(max_attempts):
            # Randomly select two different available dots
            idx1, idx2 = random.sample(available_dots, 2)
            
            x1, y1 = dots[idx1]
            x2, y2 = dots[idx2]
            
            # Calculate distance between dots
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            # Check distance constraint
            if not (MIN_LINE_LENGTH <= distance <= MAX_LINE_LENGTH):
                continue
            
            # Create connecting line
            new_line = ((x1, y1), (x2, y2))
            
            # Check if line crosses any existing lines
            crosses = False
            for existing_line in lines:
                if lines_intersect(new_line, existing_line):
                    crosses = True
                    break
            
            if crosses:
                continue
            
            # All checks passed!
            lines.append(new_line)
            connected_pairs.append((idx1, idx2))
            
            # Remove these dots from available pool
            available_dots.remove(idx1)
            available_dots.remove(idx2)
            
            print(f"  Connection {conn_num + 1}/{num_connections}: " + 
                  f"Dot {idx1} ({x1},{y1}) ↔ Dot {idx2} ({x2},{y2}) " +
                  f"[distance: {distance:.1f}px, attempts: {attempt + 1}]")
            
            placed = True
            break
        
        if not placed:
            print(f"  ⚠️  Could not place connection {conn_num + 1} after {max_attempts} attempts")
    
    print(f"Successfully created {len(connected_pairs)} connections")
    print(f"Dots still available: {len(available_dots)} out of {len(dots)}")
    
    return lines, connected_pairs


def generate_free_lines(num_lines, dots, existing_lines=[]):
    """Generate free-hanging lines (same as Step 2)"""
    lines = list(existing_lines)
    
    print(f"\nGenerating {num_lines} free-hanging lines...")
    
    for line_num in range(num_lines):
        max_attempts = 1000
        placed = False
        
        for attempt in range(max_attempts):
            x1 = random.randint(-PATTERN_WIDTH // 2 + 10, PATTERN_WIDTH // 2 - 10)
            y1 = random.randint(-PATTERN_HEIGHT // 2 + 10, PATTERN_HEIGHT // 2 - 10)
            
            angle = random.uniform(0, 2 * math.pi)
            length = random.randint(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
            
            x2 = x1 + int(length * math.cos(angle))
            y2 = y1 + int(length * math.sin(angle))
            
            if (abs(x2) > PATTERN_WIDTH // 2 or abs(y2) > PATTERN_HEIGHT // 2):
                continue
            
            new_line = ((x1, y1), (x2, y2))
            
            crosses = False
            for existing_line in lines:
                if lines_intersect(new_line, existing_line):
                    crosses = True
                    break
            if crosses:
                continue
            
            too_close = False
            for dot in dots:
                dist = point_to_segment_distance(dot, (x1, y1), (x2, y2))
                if dist < MIN_LINE_DOT_DISTANCE:
                    too_close = True
                    break
            if too_close:
                continue
            
            lines.append(new_line)
            placed = True
            print(f"  Free line {line_num + 1}/{num_lines} placed [attempts: {attempt + 1}]")
            break
        
        if not placed:
            print(f"  ⚠️  Could not place free line {line_num + 1}")
    
    return lines


# ============================================================================
# COMPLETE PATTERN GENERATION
# ============================================================================

def generate_complete_pattern(num_dots, num_connections):
    """
    Generate a complete pattern with dots and lines
    
    Process:
    1. Generate dots
    2. Generate connecting lines (these use up some dots)
    3. Generate free-hanging lines (to keep total at 4 lines)
    
    Args:
        num_dots: total number of dots
        num_connections: 0, 1, or 2 (number of dot pairs to connect)
    
    Returns:
        (dots, all_lines, connected_pairs)
    """
    TOTAL_LINES = 4  # Always 4 lines in the experiment
    
    print("\n" + "="*60)
    print(f"GENERATING PATTERN: {num_dots} dots, {num_connections} connections")
    print("="*60)
    
    # Step 1: Generate dots
    dots = generate_dots(num_dots)
    print(f"✓ Generated {len(dots)} dots")
    
    # Step 2: Generate connecting lines
    if num_connections > 0:
        all_lines, connected_pairs = generate_connecting_lines(num_connections, dots)
    else:
        all_lines = []
        connected_pairs = []
    
    # Step 3: Generate free-hanging lines to fill up to 4 total
    num_free_lines = TOTAL_LINES - num_connections
    if num_free_lines > 0:
        all_lines = generate_free_lines(num_free_lines, dots, all_lines)
    
    print(f"\n✓ Pattern complete: {len(dots)} dots, {len(all_lines)} lines")
    print(f"  - Connecting lines: {num_connections}")
    print(f"  - Free-hanging lines: {TOTAL_LINES - num_connections}")
    
    return dots, all_lines, connected_pairs


# ============================================================================
# ENHANCED VISUALIZATION
# ============================================================================

def visualize_pattern_with_connections(dots, lines, connected_pairs, title):
    """
    Visualize pattern with connections highlighted
    
    - Connecting lines shown in RED
    - Free lines shown in BLACK
    - Connected dots highlighted
    """
    fig, ax = plt.subplots(1, 1, figsize=(6, 8))
    
    # Pattern boundary
    pattern_rect = patches.Rectangle(
        (-PATTERN_WIDTH // 2, -PATTERN_HEIGHT // 2),
        PATTERN_WIDTH, PATTERN_HEIGHT,
        linewidth=2, edgecolor='black',
        facecolor='gray', alpha=0.3
    )
    ax.add_patch(pattern_rect)
    
    # Identify which dots are connected
    connected_dot_indices = set()
    for (idx1, idx2) in connected_pairs:
        connected_dot_indices.add(idx1)
        connected_dot_indices.add(idx2)
    
    # Identify which lines are connecting lines
    connecting_lines = []
    for (idx1, idx2) in connected_pairs:
        line = (dots[idx1], dots[idx2])
        connecting_lines.append(line)
    
    # Draw FREE lines (black)
    for line in lines:
        if line not in connecting_lines:
            (x1, y1), (x2, y2) = line
            line_obj = mlines.Line2D([x1, x2], [y1, y2],
                                    linewidth=LINE_WIDTH,
                                    color='black',
                                    label='Free line')
            ax.add_line(line_obj)
    
    # Draw CONNECTING lines (red, thicker)
    for line in connecting_lines:
        (x1, y1), (x2, y2) = line
        line_obj = mlines.Line2D([x1, x2], [y1, y2],
                                linewidth=LINE_WIDTH + 1,
                                color='red',
                                label='Connecting line')
        ax.add_line(line_obj)
    
    # Draw dots
    for i, (x, y) in enumerate(dots):
        if i in connected_dot_indices:
            # Connected dots: red fill with black border
            circle = patches.Circle((x, y), radius=DOT_DIAMETER / 2,
                                   edgecolor='red', facecolor='pink',
                                   linewidth=2)
        else:
            # Unconnected dots: solid black
            circle = patches.Circle((x, y), radius=DOT_DIAMETER / 2,
                                   color='black')
        ax.add_patch(circle)
        
        # Add dot number (for debugging)
        ax.text(x, y, str(i), ha='center', va='center',
               fontsize=6, color='white', weight='bold')
    
    ax.set_xlim(-PATTERN_WIDTH // 2 - 20, PATTERN_WIDTH // 2 + 20)
    ax.set_ylim(-PATTERN_HEIGHT // 2 - 20, PATTERN_HEIGHT // 2 + 20)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    ax.set_title(f"{title}\n({len(dots)} dots, {len(lines)} lines, {len(connected_pairs)} connections)")
    ax.set_xlabel("X position (pixels)")
    ax.set_ylabel("Y position (pixels)")
    
    # Legend
    red_line = mlines.Line2D([], [], color='red', linewidth=LINE_WIDTH+1, label='Connecting')
    black_line = mlines.Line2D([], [], color='black', linewidth=LINE_WIDTH, label='Free')
    ax.legend(handles=[red_line, black_line], loc='upper right')
    
    plt.tight_layout()
    plt.show()


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    """Main demonstration - create the 3 key conditions"""
    
    print("="*60)
    print("STEP 3: CONNECTING LINES DEMONSTRATION")
    print("="*60)
    
    print("\nThis script demonstrates the KEY EXPERIMENTAL MANIPULATION:")
    print("- Zero-connected: All 4 lines are free (baseline)")
    print("- One-connected: 1 line connects dots, 3 lines free")
    print("- Two-connected: 2 lines connect dots, 2 lines free")
    print("\nHypothesis: More connections → more underestimation")
    
    # Generate and visualize each condition
    conditions = [
        ("Zero-Connected (Baseline)", 12, 0),
        ("One-Connected", 12, 1),
        ("Two-Connected", 12, 2),
    ]
    
    for title, num_dots, num_connections in conditions:
        try:
            dots, lines, connected_pairs = generate_complete_pattern(num_dots, num_connections)
            
            print(f"\nVisualizing: {title}")
            visualize_pattern_with_connections(dots, lines, connected_pairs, title)
            
        except RuntimeError as e:
            print(f"\n❌ ERROR generating {title}: {e}")
    
    # Show the effect with different dot numbers
    print("\n" + "="*60)
    print("TESTING DIFFERENT DOT NUMBERS")
    print("="*60)
    print("The experiment uses 7 different dot numbers: 9, 10, 11, 12, 13, 14, 15")
    print("Let's test the extremes with 2 connections:")
    
    for num_dots in [9, 15]:
        title = f"{num_dots} Dots, Two-Connected"
        try:
            dots, lines, connected_pairs = generate_complete_pattern(num_dots, 2)
            visualize_pattern_with_connections(dots, lines, connected_pairs, title)
        except RuntimeError as e:
            print(f"\n❌ ERROR: {e}")
    
    print("\n" + "="*60)
    print("STEP 3 COMPLETE")
    print("="*60)
    print("\nKey Takeaways:")
    print("✓ Connecting lines link dot centers exactly")
    print("✓ Connected dots are 'used up' (can't connect twice)")
    print("✓ Total lines always = 4 (controls for visual clutter)")
    print("✓ Red lines = connecting, Black lines = free")
    print("✓ This is the core manipulation!")
    print("\nNext: Step 4 will show these as they appear in the experiment")


if __name__ == "__main__":
    main()
