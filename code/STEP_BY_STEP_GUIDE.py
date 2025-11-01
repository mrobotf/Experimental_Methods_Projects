"""
MASTER GUIDE: Step-by-Step Learning Scripts
============================================

This guide explains all the step-by-step scripts for learning
how the experiment works, piece by piece.

Each script is standalone and demonstrates ONE concept clearly.
"""

# ============================================================================
# OVERVIEW
# ============================================================================

"""
The experiment has several components:
1. Dot generation (with spacing constraints)
2. Line generation (free-hanging lines)
3. Connecting lines (dot-to-dot)
4. Display presentation (side-by-side)
5. Expyriment integration (timing, response, data)
6. Full experiment (putting it all together)

We've broken this down into 5 learning scripts + the final experiment.
"""

# ============================================================================
# STEP 1: DOT GENERATION
# ============================================================================

STEP_1 = {
    'file': 'step1_dot_generation.py',
    'title': 'Dot Generation with Constraints',
    'duration': '5-10 minutes',
    'requires': 'matplotlib',
    'teaches': [
        'Random dot placement algorithm',
        'Minimum distance constraint',
        'Boundary constraints',
        'Retry mechanism',
        'Visualization with matplotlib'
    ],
    'key_concepts': [
        'Trial-and-error generation',
        'Distance calculation (Euclidean)',
        'Why 15 dots is harder than 9 dots',
        'Constraint satisfaction problem'
    ],
    'run': 'python step1_dot_generation.py',
    'what_you_see': [
        'Console output showing generation progress',
        'Matplotlib plots of dot patterns',
        'Statistics about spacing',
        'Three examples: 12, 9, and 15 dots'
    ],
    'modifications': [
        'Change MIN_DOT_DISTANCE to see effect',
        'Change PATTERN_WIDTH/HEIGHT',
        'Try different numbers of dots'
    ]
}

# ============================================================================
# STEP 2: FREE-HANGING LINES
# ============================================================================

STEP_2 = {
    'file': 'step2_line_generation.py',
    'title': 'Free-Hanging Line Generation',
    'duration': '10-15 minutes',
    'requires': 'matplotlib',
    'teaches': [
        'Random line generation',
        'Line intersection detection',
        'Point-to-line-segment distance',
        'Keeping lines away from dots',
        'Multiple constraint checking'
    ],
    'key_concepts': [
        'Parametric line intersection',
        'Geometric constraint checking',
        'Line endpoint boundary checking',
        'Why lines can\'t cross',
        'Distance from point to line segment'
    ],
    'run': 'python step2_line_generation.py',
    'what_you_see': [
        'Dots with free-hanging lines',
        'Lines that don\'t touch dots',
        'Lines that don\'t cross each other',
        'Statistics about line lengths and distances'
    ],
    'modifications': [
        'Change number of lines',
        'Change MIN_LINE_LENGTH / MAX_LINE_LENGTH',
        'Change MIN_LINE_DOT_DISTANCE',
        'Try crowded patterns (many lines, few dots)'
    ]
}

# ============================================================================
# STEP 3: CONNECTING LINES
# ============================================================================

STEP_3 = {
    'file': 'step3_connecting_lines.py',
    'title': 'Connecting Lines (The Key Manipulation!)',
    'duration': '10-15 minutes',
    'requires': 'matplotlib',
    'teaches': [
        'How to connect dot pairs',
        'Distance constraints for connections',
        'Combining connecting + free lines',
        'The 0, 1, 2 connection conditions',
        'Why this affects numerosity perception'
    ],
    'key_concepts': [
        'Connecting lines = perceptual grouping',
        'Connected dots form "objects"',
        'Always 4 total lines (control for clutter)',
        'Connected dots are "used up"',
        'This is the EXPERIMENTAL MANIPULATION'
    ],
    'run': 'python step3_connecting_lines.py',
    'what_you_see': [
        'Zero-connected (baseline)',
        'One-connected (1 pair linked)',
        'Two-connected (2 pairs linked)',
        'RED lines = connecting, BLACK = free',
        'Pink/red dots = connected'
    ],
    'modifications': [
        'Try 3 connections (beyond experiment)',
        'Change connection distance constraints',
        'See effect with different dot numbers'
    ],
    'key_insight': 'Connected dots should look like FEWER dots!'
}

# ============================================================================
# STEP 4: DISPLAY SIMULATION
# ============================================================================

STEP_4 = {
    'file': 'step4_display_simulation.py',
    'title': 'How Stimuli Appear in the Experiment',
    'duration': '10-15 minutes',
    'requires': 'matplotlib',
    'teaches': [
        'Side-by-side presentation',
        'Black background, gray patterns',
        'Green fixation cross',
        'Reference vs. Test comparison',
        'What participants actually see'
    ],
    'key_concepts': [
        'Left/right hemifield presentation',
        'Brief presentation (200ms)',
        'No counting possible',
        'Comparison task',
        'Display matches experiment specs'
    ],
    'run': 'python step4_display_simulation.py',
    'what_you_see': [
        'Easy trial (9 vs 12)',
        'Connectedness effect demo',
        'Hard trial (13 connected vs 12)',
        'Trial sequence',
        'Actual appearance (no labels)'
    ],
    'modifications': [
        'Change HEMIFIELD_OFFSET',
        'Try different color schemes',
        'Add more information / remove information'
    ],
    'note': 'This uses matplotlib, not Expyriment. Just for visualization!'
}

# ============================================================================
# STEP 5: EXPYRIMENT BASICS
# ============================================================================

STEP_5 = {
    'file': 'step5_expyriment_basics.py',
    'title': 'Expyriment Fundamentals',
    'duration': '15-20 minutes',
    'requires': 'expyriment',
    'teaches': [
        'How to initialize Expyriment',
        'Present stimuli with timing',
        'Collect keyboard responses',
        'Record data automatically',
        'Canvas drawing for patterns'
    ],
    'key_concepts': [
        'Experiment object structure',
        'present() and wait() timing',
        'keyboard.wait() for responses',
        'data.add() for recording',
        'Screen refresh synchronization',
        'Complete trial structure'
    ],
    'run': 'python step5_expyriment_basics.py',
    'what_you_see': [
        'Menu of 5 demos',
        'Interactive Expyriment windows',
        'Colored screens, text, shapes',
        'Response collection in action',
        'Timing precision demonstration'
    ],
    'modifications': [
        'Run individual demos',
        'Change timing durations',
        'Add more response keys',
        'Try different stimulus types'
    ],
    'important': 'This introduces the actual experiment framework!'
}

# ============================================================================
# STEP 6: FULL EXPERIMENT
# ============================================================================

STEP_6 = {
    'file': 'experiment1_connectedness.py',
    'title': 'Complete Experiment (Putting It All Together)',
    'duration': '~60 minutes for full run',
    'requires': 'expyriment, numpy',
    'combines': [
        'Dot generation (Step 1)',
        'Line generation (Steps 2-3)',
        'Display layout (Step 4)',
        'Expyriment integration (Step 5)',
        'Trial structure',
        'Block organization',
        'Data collection'
    ],
    'key_features': [
        '168 reference patterns',
        '168 test patterns',
        '5 blocks × 336 trials',
        'Practice trials',
        'Counterbalanced positions',
        'Automatic data saving'
    ],
    'run': 'python experiment1_connectedness.py',
    'alternatives': [
        'experiment1_TEST_VERSION.py (quick 3-min test)',
    ],
    'note': 'Use TEST version first to verify everything works!'
}

# ============================================================================
# LEARNING PATH
# ============================================================================

LEARNING_PATH = """
RECOMMENDED LEARNING PATH
=========================

For Complete Beginners:
-----------------------
1. Step 1 (dots)          → Understand constraint-based generation
2. Step 2 (free lines)    → Understand geometric constraints  
3. Step 3 (connections)   → Understand the manipulation
4. Step 4 (display)       → See how it looks
5. Step 5 (Expyriment)    → Learn the framework
6. TEST version           → Verify everything works
7. Full experiment        → Run real experiment

For Quick Start:
---------------
1. Step 3 (connections)   → See the key idea
2. Step 4 (display)       → See how it looks
3. Step 5 demo 5          → See complete trial
4. TEST version           → Verify it works
5. Full experiment        → Run it

For Debugging/Understanding:
---------------------------
1. Identify which component has issues
2. Run corresponding step script
3. Modify parameters to understand effect
4. Check console output and visualizations
5. Apply learning to full experiment

For Teaching:
------------
Show students in order:
1. Step 3 (the "wow" factor - connectedness effect)
2. Step 4 (show them what participants see)
3. Step 1 (how it's made - dots)
4. Step 2-3 (how it's made - lines)
5. Step 5 (the machinery - Expyriment)
6. Run TEST version together
"""

# ============================================================================
# COMMON MODIFICATIONS
# ============================================================================

COMMON_MODIFICATIONS = """
COMMON MODIFICATIONS ACROSS STEPS
==================================

Make Patterns Easier to Generate:
---------------------------------
MIN_DOT_DISTANCE = 35           # From 38
PATTERN_WIDTH = 280             # From 240
PATTERN_HEIGHT = 360            # From 320

Make Experiment Shorter:
-----------------------
NUM_BLOCKS = 2                  # From 5
PATTERNS_PER_CONDITION = 4      # From 8
NUM_PRACTICE_TRIALS = 10        # From 30

Change Timing:
-------------
STIMULUS_DURATION = 150         # From 200 (harder)
STIMULUS_DURATION = 300         # From 200 (easier)

Change Display:
--------------
HEMIFIELD_OFFSET = 250          # From 200 (farther apart)
PATTERN_COLOR = (150,150,150)   # Lighter gray
DOT_COLOR = (50, 50, 50)        # Dark gray instead of black

Debug Mode:
----------
# Add this to see what's happening
print(f"Generated pattern: {num_dots} dots, {connectedness} connections")
# Add delays
exp.clock.wait(2000)  # Wait 2 seconds between trials
# Show pattern info on screen
info_text = stimuli.TextLine(f"{num_dots} dots, {connectedness} conn")
info_text.present()
"""

# ============================================================================
# TROUBLESHOOTING GUIDE
# ============================================================================

TROUBLESHOOTING = """
TROUBLESHOOTING GUIDE
====================

Problem: Pattern generation fails
Solution: 
  - Run Step 1 with same parameters
  - Check console output for which dot fails
  - Increase pattern size or decrease min distance
  - Reduce number of dots

Problem: Lines don't generate
Solution:
  - Run Step 2 to test line generation
  - Check MIN_LINE_DOT_DISTANCE
  - May need fewer lines or more space

Problem: Can't make connections
Solution:
  - Run Step 3 to test connections
  - Check MIN_LINE_LENGTH and MAX_LINE_LENGTH
  - May need closer dots or different range

Problem: Display looks wrong
Solution:
  - Run Step 4 to check visualization
  - Verify PATTERN_COLOR (should be gray)
  - Verify BACKGROUND_COLOR (should be black)
  - Check HEMIFIELD_OFFSET

Problem: Timing is imprecise
Solution:
  - Run Step 5 demo 3 (timing test)
  - Check monitor refresh rate (should be 60Hz)
  - Expyriment will warn if timing is bad
  - Consider using CRT monitor

Problem: Responses not recorded
Solution:
  - Run Step 5 demo 2 (response collection)
  - Check keyboard constants
  - Verify data.add() is called
  - Check data file location

Problem: Experiment crashes
Solution:
  - Run TEST version first
  - Check console for error messages
  - Try individual steps to isolate problem
  - Verify all requirements installed
"""

# ============================================================================
# FILE SUMMARY
# ============================================================================

FILE_SUMMARY = """
FILE SUMMARY
===========

Step-by-Step Learning Scripts:
------------------------------
step1_dot_generation.py         (~200 lines) - Dot placement
step2_line_generation.py        (~350 lines) - Free lines
step3_connecting_lines.py       (~450 lines) - Connections
step4_display_simulation.py     (~400 lines) - Display
step5_expyriment_basics.py      (~450 lines) - Framework

Full Experiments:
----------------
experiment1_connectedness.py    (~650 lines) - Full version
experiment1_TEST_VERSION.py     (~500 lines) - Quick test

Documentation:
-------------
README.md                       - Complete documentation
QUICK_START.md                  - Quick start guide
STEP_BY_STEP_GUIDE.md          - This file

Requirements:
------------
requirements.txt                - Python dependencies

Total Lines of Code: ~3,000 lines
Total Scripts: 8 scripts
Learning Time: 1-3 hours for all steps
"""

# ============================================================================
# PRINT GUIDE
# ============================================================================

def print_guide():
    """Print the complete guide"""
    
    print("="*70)
    print("STEP-BY-STEP LEARNING GUIDE")
    print("="*70)
    
    for step_num, step in enumerate([STEP_1, STEP_2, STEP_3, STEP_4, STEP_5], 1):
        print(f"\n{'='*70}")
        print(f"STEP {step_num}: {step['title']}")
        print(f"{'='*70}")
        print(f"File: {step['file']}")
        print(f"Duration: {step['duration']}")
        print(f"Requires: {step['requires']}")
        
        print(f"\nTeaches:")
        for item in step['teaches']:
            print(f"  • {item}")
        
        print(f"\nKey Concepts:")
        for concept in step['key_concepts']:
            print(f"  • {concept}")
        
        print(f"\nTo Run:")
        print(f"  {step['run']}")
        
        print(f"\nWhat You'll See:")
        for item in step['what_you_see']:
            print(f"  • {item}")
        
        if 'key_insight' in step:
            print(f"\n⭐ KEY INSIGHT: {step['key_insight']}")
    
    print(f"\n{'='*70}")
    print(f"STEP 6: {STEP_6['title']}")
    print(f"{'='*70}")
    print(f"File: {STEP_6['file']}")
    print(f"Duration: {STEP_6['duration']}")
    
    print(LEARNING_PATH)
    print(COMMON_MODIFICATIONS)
    print(TROUBLESHOOTING)
    print(FILE_SUMMARY)
    
    print("\n" + "="*70)
    print("READY TO START!")
    print("="*70)
    print("\nBegin with: python step1_dot_generation.py")
    print("Or jump to the key idea: python step3_connecting_lines.py")
    print("Or see it in action: python step4_display_simulation.py")
    print("\n" + "="*70)


if __name__ == "__main__":
    print_guide()
