"""
STEP 2: Free-Hanging Line Generation
=====================================

This script shows how to:
1. Generate random lines that don't cross each other
2. Keep lines away from dots
3. Ensure lines stay within pattern boundaries
4. Visualize lines with dots

This covers the "free-hanging" lines (not connecting dots).
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines
import random
import math

# ============================================================================
# CONFIGURATION (same as Step 1)
# ============================================================================

PATTERN_WIDTH = 240
PATTERN_HEIGHT = 320

DOT_DIAMETER = 12
MIN_DOT_DISTANCE = 38
MIN_DOT_BOUNDARY_DISTANCE = 10

# Line settings
LINE_WIDTH = 2
MIN_LINE_LENGTH = 30
MAX_LINE_LENGTH = 60
MIN_LINE_DOT_DISTANCE = 12  # Lines must stay this far from dots


# ============================================================================
# DOT GENERATION (from Step 1)
# ============================================================================

def generate_dots(num_dots):
    """Generate dots (same as Step 1)"""
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


# ============================================================================
# LINE INTERSECTION CHECK
# ============================================================================

def lines_intersect(line1, line2):
    """
    Check if two line segments intersect
    
    Args:
        line1: ((x1, y1), (x2, y2))
        line2: ((x3, y3), (x4, y4))
    
    Returns:
        True if lines intersect, False otherwise
    
    Algorithm:
        Uses parametric representation and cross products
        Lines intersect if both parameters t and u are in (0, 1)
    """
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    
    # Calculate denominator (if 0, lines are parallel)
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if abs(denom) < 1e-10:
        return False  # Parallel or collinear
    
    # Calculate parameters t and u
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    # Intersection occurs if both are in (0, 1)
    # We use 0 < t < 1 to exclude endpoint touching
    return 0 < t < 1 and 0 < u < 1


# ============================================================================
# POINT-TO-LINE-SEGMENT DISTANCE
# ============================================================================

def point_to_segment_distance(point, seg_start, seg_end):
    """
    Calculate minimum distance from a point to a line segment
    
    Args:
        point: (x, y)
        seg_start: (x1, y1)
        seg_end: (x2, y2)
    
    Returns:
        Minimum distance in pixels
    
    Algorithm:
        1. Project point onto infinite line
        2. Clamp projection to segment (parameter t ∈ [0, 1])
        3. Calculate distance to clamped point
    """
    px, py = point
    x1, y1 = seg_start
    x2, y2 = seg_end
    
    # Vector from start to end
    dx = x2 - x1
    dy = y2 - y1
    
    # Handle degenerate case (zero-length segment)
    if dx == 0 and dy == 0:
        return math.sqrt((px - x1)**2 + (py - y1)**2)
    
    # Calculate parameter t of closest point on infinite line
    # t = dot(point - start, end - start) / ||end - start||²
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    
    # Clamp t to [0, 1] to stay on segment
    t = max(0, min(1, t))
    
    # Calculate closest point on segment
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    
    # Return distance
    return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)


# ============================================================================
# LINE GENERATION
# ============================================================================

def generate_free_lines(num_lines, dots, existing_lines=[]):
    """
    Generate free-hanging lines (not touching dots)
    
    Constraints:
    1. Lines don't cross each other
    2. Lines stay within pattern boundaries
    3. Lines stay at least MIN_LINE_DOT_DISTANCE from all dots
    4. Lines have length between MIN_LINE_LENGTH and MAX_LINE_LENGTH
    
    Args:
        num_lines: how many lines to generate
        dots: list of (x, y) dot positions
        existing_lines: any lines already present (e.g., connecting lines)
    
    Returns:
        list of ((x1, y1), (x2, y2)) line segments
    """
    lines = list(existing_lines)  # Copy existing lines
    
    print(f"\nGenerating {num_lines} free-hanging lines...")
    
    for line_num in range(num_lines):
        max_attempts = 1000
        placed = False
        
        for attempt in range(max_attempts):
            # Random starting point
            x1 = random.randint(-PATTERN_WIDTH // 2 + 10, PATTERN_WIDTH // 2 - 10)
            y1 = random.randint(-PATTERN_HEIGHT // 2 + 10, PATTERN_HEIGHT // 2 - 10)
            
            # Random angle and length
            angle = random.uniform(0, 2 * math.pi)
            length = random.randint(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
            
            # Calculate end point
            x2 = x1 + int(length * math.cos(angle))
            y2 = y1 + int(length * math.sin(angle))
            
            # Check if end point is within boundaries
            if (abs(x2) > PATTERN_WIDTH // 2 or 
                abs(y2) > PATTERN_HEIGHT // 2):
                continue
            
            new_line = ((x1, y1), (x2, y2))
            
            # Check if line crosses any existing lines
            crosses = False
            for existing_line in lines:
                if lines_intersect(new_line, existing_line):
                    crosses = True
                    break
            
            if crosses:
                continue
            
            # Check if line is too close to any dot
            too_close = False
            for dot in dots:
                dist = point_to_segment_distance(dot, (x1, y1), (x2, y2))
                if dist < MIN_LINE_DOT_DISTANCE:
                    too_close = True
                    break
            
            if too_close:
                continue
            
            # All checks passed!
            lines.append(new_line)
            placed = True
            print(f"  Line {line_num + 1}/{num_lines} placed: ({x1},{y1}) to ({x2},{y2}) [attempts: {attempt + 1}]")
            break
        
        if not placed:
            print(f"  ⚠️  Warning: Could not place line {line_num + 1} after {max_attempts} attempts")
            # Continue anyway - some patterns may have difficulty fitting all lines
    
    print(f"Successfully generated {len(lines) - len(existing_lines)} new lines")
    return lines


# ============================================================================
# VISUALIZATION
# ============================================================================

def visualize_pattern(dots, lines, title="Pattern with Lines"):
    """Visualize dots and lines together"""
    
    fig, ax = plt.subplots(1, 1, figsize=(6, 8))
    
    # Draw pattern boundary
    pattern_rect = patches.Rectangle(
        (-PATTERN_WIDTH // 2, -PATTERN_HEIGHT // 2),
        PATTERN_WIDTH,
        PATTERN_HEIGHT,
        linewidth=2,
        edgecolor='black',
        facecolor='gray',
        alpha=0.3
    )
    ax.add_patch(pattern_rect)
    
    # Draw lines FIRST (so they appear behind dots)
    for ((x1, y1), (x2, y2)) in lines:
        line = mlines.Line2D([x1, x2], [y1, y2], 
                            linewidth=LINE_WIDTH, 
                            color='black')
        ax.add_line(line)
    
    # Draw dots
    for (x, y) in dots:
        circle = patches.Circle((x, y), radius=DOT_DIAMETER / 2, color='black')
        ax.add_patch(circle)
    
    # Optional: visualize minimum distance zones around dots
    # Uncomment to see the "keep-out" zones for lines
    # for (x, y) in dots:
    #     circle = patches.Circle(
    #         (x, y),
    #         radius=MIN_LINE_DOT_DISTANCE,
    #         color='red',
    #         fill=False,
    #         linestyle='--',
    #         alpha=0.3
    #     )
    #     ax.add_patch(circle)
    
    ax.set_xlim(-PATTERN_WIDTH // 2 - 20, PATTERN_WIDTH // 2 + 20)
    ax.set_ylim(-PATTERN_HEIGHT // 2 - 20, PATTERN_HEIGHT // 2 + 20)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
    
    ax.set_title(f"{title}\n({len(dots)} dots, {len(lines)} lines)")
    ax.set_xlabel("X position (pixels)")
    ax.set_ylabel("Y position (pixels)")
    
    plt.tight_layout()
    plt.show()


# ============================================================================
# LINE STATISTICS
# ============================================================================

def calculate_line_statistics(lines, dots):
    """Calculate and print statistics about lines"""
    
    print("\n" + "="*60)
    print("LINE PATTERN STATISTICS")
    print("="*60)
    
    print(f"\nNumber of lines: {len(lines)}")
    print(f"Line length constraint: {MIN_LINE_LENGTH}-{MAX_LINE_LENGTH} pixels")
    
    # Calculate line lengths
    lengths = []
    for ((x1, y1), (x2, y2)) in lines:
        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        lengths.append(length)
    
    if lengths:
        print(f"\nActual line lengths:")
        print(f"  Minimum: {min(lengths):.2f} pixels")
        print(f"  Maximum: {max(lengths):.2f} pixels")
        print(f"  Average: {sum(lengths)/len(lengths):.2f} pixels")
    
    # Check distances to dots
    min_distances = []
    for line in lines:
        (x1, y1), (x2, y2) = line
        for dot in dots:
            dist = point_to_segment_distance(dot, (x1, y1), (x2, y2))
            min_distances.append(dist)
    
    if min_distances:
        print(f"\nDistance from lines to dots:")
        print(f"  Minimum: {min(min_distances):.2f} pixels")
        print(f"  Required minimum: {MIN_LINE_DOT_DISTANCE} pixels")
        
        violations = [d for d in min_distances if d < MIN_LINE_DOT_DISTANCE]
        if violations:
            print(f"  ⚠️  WARNING: {len(violations)} distance violations!")
        else:
            print(f"  ✓ All lines satisfy minimum distance from dots")
    
    # Check for intersections
    intersections = 0
    for i, line1 in enumerate(lines):
        for j, line2 in enumerate(lines):
            if i < j:
                if lines_intersect(line1, line2):
                    intersections += 1
    
    print(f"\nLine intersections: {intersections}")
    if intersections > 0:
        print(f"  ⚠️  WARNING: Lines should not intersect!")
    else:
        print(f"  ✓ No line intersections")
    
    print("="*60)


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    """Main demonstration"""
    
    print("="*60)
    print("STEP 2: FREE-HANGING LINE GENERATION")
    print("="*60)
    
    print("\nThis script demonstrates:")
    print("1. How to generate lines that don't cross")
    print("2. How to keep lines away from dots")
    print("3. Geometric constraint checking")
    
    # Generate a pattern
    print("\n" + "="*60)
    print("Generating test pattern: 12 dots + 4 free lines")
    print("="*60)
    
    # Step 1: Generate dots
    dots = generate_dots(12)
    print(f"Generated {len(dots)} dots")
    
    # Step 2: Generate lines
    lines = generate_free_lines(num_lines=4, dots=dots)
    
    # Step 3: Check statistics
    calculate_line_statistics(lines, dots)
    
    # Step 4: Visualize
    print("\nShowing visualization...")
    visualize_pattern(dots, lines, title="12 Dots + 4 Free Lines")
    
    # Test with different configurations
    print("\n" + "="*60)
    print("Testing edge case: Many lines")
    print("="*60)
    
    dots2 = generate_dots(10)
    lines2 = generate_free_lines(num_lines=8, dots=dots2)
    calculate_line_statistics(lines2, dots2)
    visualize_pattern(dots2, lines2, title="10 Dots + 8 Free Lines (Crowded)")
    
    print("\n" + "="*60)
    print("STEP 2 COMPLETE")
    print("="*60)
    print("\nKey Takeaways:")
    print("✓ Lines use random angle + length generation")
    print("✓ Multiple geometric constraints checked")
    print("✓ Line intersection uses parametric equations")
    print("✓ Point-to-segment distance uses projection")
    print("\nNext: Step 3 will add CONNECTING lines between dots")


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
