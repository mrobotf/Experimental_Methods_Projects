"""
STEP 1: Basic Dot Generation
=============================

This script shows how to:
1. Generate random dots with minimum spacing constraint
2. Visualize them using matplotlib
3. Understand the dot placement algorithm

Run this to verify dot generation works before moving to the full experiment.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import math

# ============================================================================
# CONFIGURATION
# ============================================================================

# Pattern size
PATTERN_WIDTH = 240
PATTERN_HEIGHT = 320

# Dot settings
DOT_DIAMETER = 12
MIN_DOT_DISTANCE = 38  # pixels (center-to-center)
MIN_DOT_BOUNDARY_DISTANCE = 10  # pixels from edges

# How many dots to generate
NUM_DOTS = 12  # Start with reference number


# ============================================================================
# DOT GENERATION FUNCTION
# ============================================================================

def generate_dots(num_dots):
    """
    Generate random dot positions with constraints
    
    Constraints:
    1. Dots must be at least MIN_DOT_DISTANCE apart
    2. Dots must be at least MIN_DOT_BOUNDARY_DISTANCE from edges
    
    Returns:
        list of (x, y) tuples representing dot centers
    """
    dots = []
    max_attempts = 10000
    
    print(f"\nGenerating {num_dots} dots...")
    
    for dot_num in range(num_dots):
        attempts = 0
        placed = False
        
        while attempts < max_attempts and not placed:
            # Generate random position
            # Origin is at center, so range is -width/2 to +width/2
            x = random.randint(
                -PATTERN_WIDTH // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                PATTERN_WIDTH // 2 - MIN_DOT_BOUNDARY_DISTANCE
            )
            y = random.randint(
                -PATTERN_HEIGHT // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                PATTERN_HEIGHT // 2 - MIN_DOT_BOUNDARY_DISTANCE
            )
            
            # Check if this position is valid (far enough from other dots)
            valid = True
            for (existing_x, existing_y) in dots:
                distance = math.sqrt((x - existing_x)**2 + (y - existing_y)**2)
                if distance < MIN_DOT_DISTANCE:
                    valid = False
                    break
            
            if valid:
                dots.append((x, y))
                placed = True
                print(f"  Dot {dot_num + 1}/{num_dots} placed at ({x}, {y}) after {attempts + 1} attempts")
            
            attempts += 1
        
        if not placed:
            raise RuntimeError(f"Could not place dot {dot_num + 1}/{num_dots} after {max_attempts} attempts")
    
    print(f"\nSuccessfully generated {len(dots)} dots!")
    return dots


# ============================================================================
# VISUALIZATION FUNCTION
# ============================================================================

def visualize_dots(dots, title="Dot Pattern"):
    """
    Visualize the dots using matplotlib
    
    Args:
        dots: list of (x, y) tuples
        title: plot title
    """
    fig, ax = plt.subplots(1, 1, figsize=(6, 8))
    
    # Draw pattern boundary (gray rectangle)
    pattern_rect = patches.Rectangle(
        (-PATTERN_WIDTH // 2, -PATTERN_HEIGHT // 2),  # bottom-left corner
        PATTERN_WIDTH,
        PATTERN_HEIGHT,
        linewidth=2,
        edgecolor='black',
        facecolor='gray',
        alpha=0.3
    )
    ax.add_patch(pattern_rect)
    
    # Draw dots
    for (x, y) in dots:
        circle = patches.Circle(
            (x, y),
            radius=DOT_DIAMETER / 2,
            color='black'
        )
        ax.add_patch(circle)
        
        # Optional: show dot centers with small red points
        ax.plot(x, y, 'r.', markersize=2)
    
    # Draw minimum distance circles (for visualization only)
    # Uncomment to see the "exclusion zones" around each dot
    # for (x, y) in dots:
    #     circle = patches.Circle(
    #         (x, y),
    #         radius=MIN_DOT_DISTANCE / 2,
    #         color='red',
    #         fill=False,
    #         linestyle='--',
    #         alpha=0.3
    #     )
    #     ax.add_patch(circle)
    
    # Set axis properties
    ax.set_xlim(-PATTERN_WIDTH // 2 - 20, PATTERN_WIDTH // 2 + 20)
    ax.set_ylim(-PATTERN_HEIGHT // 2 - 20, PATTERN_HEIGHT // 2 + 20)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
    
    ax.set_title(f"{title}\n({len(dots)} dots, min distance={MIN_DOT_DISTANCE}px)")
    ax.set_xlabel("X position (pixels)")
    ax.set_ylabel("Y position (pixels)")
    
    plt.tight_layout()
    plt.show()


# ============================================================================
# CALCULATE STATISTICS
# ============================================================================

def calculate_statistics(dots):
    """Calculate and print statistics about dot distribution"""
    
    if len(dots) < 2:
        print("Need at least 2 dots for statistics")
        return
    
    print("\n" + "="*60)
    print("DOT PATTERN STATISTICS")
    print("="*60)
    
    # Calculate all pairwise distances
    distances = []
    for i, (x1, y1) in enumerate(dots):
        for j, (x2, y2) in enumerate(dots):
            if i < j:  # Only calculate each pair once
                dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                distances.append(dist)
    
    print(f"\nNumber of dots: {len(dots)}")
    print(f"Minimum distance constraint: {MIN_DOT_DISTANCE} pixels")
    print(f"\nActual distances:")
    print(f"  Minimum: {min(distances):.2f} pixels")
    print(f"  Maximum: {max(distances):.2f} pixels")
    print(f"  Average: {sum(distances)/len(distances):.2f} pixels")
    
    # Check if any dots are too close (this should never happen!)
    violations = [d for d in distances if d < MIN_DOT_DISTANCE]
    if violations:
        print(f"\n⚠️  WARNING: {len(violations)} distance violations found!")
        print(f"  Closest pair: {min(violations):.2f} pixels")
    else:
        print(f"\n✓ All dots satisfy minimum distance constraint")
    
    # Calculate density
    area = PATTERN_WIDTH * PATTERN_HEIGHT
    density = len(dots) / area
    print(f"\nPattern area: {area} square pixels")
    print(f"Dot density: {density:.6f} dots per square pixel")
    print(f"Average area per dot: {area/len(dots):.2f} square pixels")
    
    print("="*60)


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    """Main demonstration function"""
    
    print("="*60)
    print("STEP 1: DOT GENERATION DEMONSTRATION")
    print("="*60)
    
    print("\nThis script demonstrates:")
    print("1. How to generate dots with minimum spacing")
    print("2. The algorithm's retry mechanism")
    print("3. Visualization of the result")
    
    # Test with different numbers of dots
    test_configurations = [
        ("12 dots (reference)", 12),
        ("9 dots (easy test)", 9),
        ("15 dots (hard test)", 15),
    ]
    
    for description, num_dots in test_configurations:
        print("\n" + "="*60)
        print(f"Testing: {description}")
        print("="*60)
        
        try:
            # Generate dots
            dots = generate_dots(num_dots)
            
            # Calculate statistics
            calculate_statistics(dots)
            
            # Visualize
            print(f"\nShowing visualization for {num_dots} dots...")
            visualize_dots(dots, title=description)
            
        except RuntimeError as e:
            print(f"\n❌ ERROR: {e}")
            print("This configuration is too difficult with current constraints.")
            print("Try: increase pattern size, decrease min distance, or reduce dot count")
    
    print("\n" + "="*60)
    print("STEP 1 COMPLETE")
    print("="*60)
    print("\nKey Takeaways:")
    print("✓ Dot generation uses random trial-and-error")
    print("✓ More dots = more attempts needed")
    print("✓ Constraints ensure dots don't overlap or crowd")
    print("✓ Pattern size and spacing must be balanced")
    print("\nNext: Step 2 will add lines to these dots")


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
