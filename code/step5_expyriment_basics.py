"""
STEP 5: Expyriment Basics - Timing and Response Collection
===========================================================

This script demonstrates:
1. How to initialize Expyriment
2. How to present stimuli with precise timing
3. How to collect keyboard responses
4. How to record data

This is a minimal working example using Expyriment.
"""

import expyriment
from expyriment import design, control, stimuli
import random

# ============================================================================
# SIMPLE DEMONSTRATION
# ============================================================================

def demo_basic_presentation():
    """Demonstrate basic stimulus presentation"""
    
    print("="*60)
    print("DEMO 1: Basic Presentation")
    print("="*60)
    
    # Create experiment
    exp = design.Experiment(name="Expyriment_Basics")
    
    # Initialize (this opens the window)
    control.initialize(exp)
    
    # Create stimuli
    instruction = stimuli.TextScreen(
        "Instructions",
        "You will see some colored screens.\n\n"
        "Just watch - no response needed.\n\n"
        "Press SPACE to start."
    )
    
    # Start experiment
    control.start(skip_ready_screen=True)
    
    # Show instruction
    instruction.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    # Show sequence of colored screens
    colors = [
        ((255, 0, 0), "RED", 500),
        ((0, 255, 0), "GREEN", 500),
        ((0, 0, 255), "BLUE", 500),
    ]
    
    for color, name, duration in colors:
        screen = stimuli.BlankScreen(colour=color)
        text = stimuli.TextLine(name, text_size=40, text_colour=(255, 255, 255))
        text.plot(screen)
        
        screen.present()
        exp.clock.wait(duration)
    
    # End
    end_text = stimuli.TextScreen("Done", "That's basic presentation!")
    end_text.present()
    exp.clock.wait(2000)
    
    control.end()


def demo_response_collection():
    """Demonstrate collecting responses"""
    
    print("\n" + "="*60)
    print("DEMO 2: Response Collection")
    print("="*60)
    
    exp = design.Experiment(name="Response_Demo")
    control.initialize(exp)
    
    instruction = stimuli.TextScreen(
        "Response Collection",
        "You will answer simple questions.\n\n"
        "Press LEFT or RIGHT arrow key.\n\n"
        "Press SPACE to start."
    )
    
    control.start(skip_ready_screen=True)
    instruction.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    # Ask 3 questions
    questions = [
        "Is the sky blue?\nLEFT = Yes, RIGHT = No",
        "Is 2 + 2 = 5?\nLEFT = Yes, RIGHT = No",
        "Do you like pizza?\nLEFT = Yes, RIGHT = No",
    ]
    
    print("\nCollecting responses...")
    
    for i, question_text in enumerate(questions):
        # Show question
        question = stimuli.TextScreen("Question", question_text)
        question.present()
        
        # Wait for response
        key, rt = exp.keyboard.wait([
            expyriment.misc.constants.K_LEFT,
            expyriment.misc.constants.K_RIGHT
        ])
        
        # Interpret response
        response = "LEFT" if key == expyriment.misc.constants.K_LEFT else "RIGHT"
        
        # Record data
        exp.data.add([i + 1, question_text[:20], response, rt])
        
        print(f"  Q{i+1}: Response = {response}, RT = {rt} ms")
        
        # Feedback
        feedback = stimuli.TextLine(
            f"You pressed: {response}\nRT: {rt} ms",
            text_size=30
        )
        feedback.present()
        exp.clock.wait(1000)
    
    # Show where data was saved
    end_text = stimuli.TextScreen(
        "Complete!",
        f"Data saved to:\n{exp.data.filename}\n\nPress SPACE to exit"
    )
    end_text.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    control.end()
    
    print(f"\n✓ Data saved to: {exp.data.filename}")


def demo_precise_timing():
    """Demonstrate precise timing control"""
    
    print("\n" + "="*60)
    print("DEMO 3: Precise Timing")
    print("="*60)
    
    exp = design.Experiment(name="Timing_Demo")
    control.initialize(exp)
    
    instruction = stimuli.TextScreen(
        "Timing Test",
        "You will see a RED square for exactly 200ms.\n\n"
        "This simulates the brief stimulus presentation.\n\n"
        "Press SPACE to start."
    )
    
    control.start(skip_ready_screen=True)
    instruction.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    # Create stimuli
    fixation = stimuli.FixCross(size=(30, 30), colour=(0, 255, 0), line_width=3)
    target = stimuli.Rectangle(size=(100, 100), colour=(255, 0, 0))
    blank = stimuli.BlankScreen()
    
    # Preload everything
    fixation.preload()
    target.preload()
    blank.preload()
    
    print("\nRunning timing test (5 trials)...")
    
    for trial in range(5):
        # Fixation (1000ms)
        fixation.present()
        exp.clock.wait(1000)
        
        # Target (200ms) - THIS IS THE CRITICAL TIMING
        t0 = target.present()
        exp.clock.wait(200)
        
        # Blank
        t1 = blank.present()
        
        actual_duration = t1 - t0
        print(f"  Trial {trial + 1}: Target shown for {actual_duration} ms (target: 200 ms)")
        
        # Inter-trial interval
        exp.clock.wait(random.randint(500, 1000))
    
    end_text = stimuli.TextScreen(
        "Timing Complete",
        "Check console for actual timings.\n\n"
        "Expyriment synchronizes with screen refresh.\n"
        "At 60Hz, each frame = ~16.67ms\n"
        "200ms = 12 frames\n\n"
        "Press SPACE to exit"
    )
    end_text.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    control.end()


def demo_canvas_drawing():
    """Demonstrate drawing on canvas (for our dot patterns)"""
    
    print("\n" + "="*60)
    print("DEMO 4: Canvas Drawing")
    print("="*60)
    
    exp = design.Experiment(name="Canvas_Demo")
    control.initialize(exp)
    
    instruction = stimuli.TextScreen(
        "Canvas Drawing",
        "You will see how we draw dots and lines.\n\n"
        "This is how patterns are created.\n\n"
        "Press SPACE to start."
    )
    
    control.start(skip_ready_screen=True)
    instruction.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    # Create a canvas (gray rectangle)
    canvas = stimuli.Canvas(size=(200, 300), colour=(102, 102, 102))
    
    # Draw some dots
    dot_positions = [(0, 0), (50, 50), (-50, -50), (30, -40)]
    for (x, y) in dot_positions:
        dot = stimuli.Circle(radius=6, colour=(0, 0, 0), position=(x, y))
        dot.plot(canvas)
    
    # Draw a line
    line = stimuli.Line(start_point=(-50, 50), end_point=(50, -50),
                       line_width=2, colour=(0, 0, 0))
    line.plot(canvas)
    
    # Show it
    canvas.present()
    
    exp.keyboard.wait()
    
    control.end()


def demo_trial_structure():
    """Demonstrate a complete trial structure"""
    
    print("\n" + "="*60)
    print("DEMO 5: Complete Trial Structure")
    print("="*60)
    
    exp = design.Experiment(name="Trial_Structure_Demo")
    control.initialize(exp)
    
    instruction = stimuli.TextScreen(
        "Trial Structure",
        "This demonstrates a complete trial:\n\n"
        "1. Fixation cross\n"
        "2. Random delay\n"
        "3. Stimulus (200ms)\n"
        "4. Blank screen\n"
        "5. Response collection\n\n"
        "Press SPACE to start."
    )
    
    control.start(skip_ready_screen=True)
    instruction.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    # Create stimuli
    fixation = stimuli.FixCross(size=(20, 20), colour=(0, 255, 0))
    
    # Simulate left and right patterns
    left_pattern = stimuli.Rectangle(size=(100, 150), colour=(102, 102, 102),
                                    position=(-200, 0))
    right_pattern = stimuli.Rectangle(size=(100, 150), colour=(102, 102, 102),
                                     position=(200, 0))
    
    # Add text to indicate which is which
    left_text = stimuli.TextLine("LEFT", text_size=20, position=(-200, 0))
    right_text = stimuli.TextLine("RIGHT", text_size=20, position=(200, 0))
    
    # Combine into display
    display = stimuli.BlankScreen()
    left_pattern.plot(display)
    right_pattern.plot(display)
    left_text.plot(display)
    right_text.plot(display)
    fixation.plot(display)
    
    blank = stimuli.BlankScreen()
    
    print("\nRunning 3 trials...")
    
    for trial_num in range(3):
        print(f"\nTrial {trial_num + 1}:")
        
        # 1. Fixation
        fixation.present()
        print("  - Showing fixation...")
        
        # 2. Random delay
        delay = random.randint(500, 1000)
        exp.clock.wait(delay)
        print(f"  - Waited {delay} ms")
        
        # 3. Stimulus (200ms)
        display.present()
        print("  - Showing stimulus (200ms)...")
        exp.clock.wait(200)
        
        # 4. Blank
        blank.present()
        print("  - Blank screen, waiting for response...")
        
        # 5. Response
        key, rt = exp.keyboard.wait([
            expyriment.misc.constants.K_LEFT,
            expyriment.misc.constants.K_RIGHT
        ])
        
        response = "LEFT" if key == expyriment.misc.constants.K_LEFT else "RIGHT"
        print(f"  - Response: {response}, RT: {rt} ms")
        
        # Record data
        exp.data.add([trial_num + 1, response, rt])
    
    end_text = stimuli.TextScreen(
        "Complete!",
        "That's the complete trial structure!\n\n"
        "Press SPACE to exit"
    )
    end_text.present()
    exp.keyboard.wait(expyriment.misc.constants.K_SPACE)
    
    control.end()


# ============================================================================
# MAIN MENU
# ============================================================================

def main():
    """Run demonstrations"""
    
    print("="*60)
    print("STEP 5: EXPYRIMENT BASICS")
    print("="*60)
    
    print("\nThis demonstrates core Expyriment concepts:")
    print("1. Basic presentation")
    print("2. Response collection")
    print("3. Precise timing")
    print("4. Canvas drawing")
    print("5. Complete trial structure")
    
    demos = [
        ("Basic Presentation", demo_basic_presentation),
        ("Response Collection", demo_response_collection),
        ("Precise Timing", demo_precise_timing),
        ("Canvas Drawing", demo_canvas_drawing),
        ("Complete Trial Structure", demo_trial_structure),
    ]
    
    print("\n" + "="*60)
    print("Available Demos:")
    for i, (name, _) in enumerate(demos):
        print(f"{i + 1}. {name}")
    print("0. Run all demos")
    print("="*60)
    
    choice = input("\nEnter number (or ENTER for all): ").strip()
    
    if choice == "" or choice == "0":
        # Run all
        for name, demo_func in demos:
            input(f"\nPress ENTER to run: {name}...")
            demo_func()
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(demos):
                name, demo_func = demos[idx]
                print(f"\nRunning: {name}")
                demo_func()
            else:
                print("Invalid choice!")
        except ValueError:
            print("Invalid input!")
    
    print("\n" + "="*60)
    print("STEP 5 COMPLETE")
    print("="*60)
    print("\nKey Takeaways:")
    print("✓ Expyriment handles display and timing")
    print("✓ present() shows stimulus, wait() controls duration")
    print("✓ keyboard.wait() collects responses + reaction time")
    print("✓ data.add() saves trial data automatically")
    print("✓ Timing syncs with screen refresh (important!)")
    print("\nNext: Step 6 will combine everything into the full experiment")


if __name__ == "__main__":
    main()
