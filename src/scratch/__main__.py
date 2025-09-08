import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from vault_runner import VaultRunner, create_corridor_world, create_room_world, create_multi_key_world
from interpreter import VaultInterpreter
from programs import program1_corridor, program2_room, program3_multikey, print_program_analysis
from game import VaultRunnerGame
from extensions import ExtendedVaultInterpreter, AdvancedVaultRunner, LanguageExtensions


def interactive_demo():
    """Interactive demonstration of the Vault Runner language."""
    print("=" * 70)
    print("VAULT RUNNER PROGRAMMING LANGUAGE - INTERACTIVE DEMO")
    print("=" * 70)
    
    while True:
        print("\nSelect a demonstration:")
        print("1. Analyze all programs")
        print("2. Run Program 1 (Corridor Navigation)")
        print("3. Run Program 2 (Room Exploration)")
        print("4. Run Program 3 (Multi-key Challenge) [Optional]")
        print("5. Custom program input")
        print("6. Show world visualizations only")
        print("7. Play the Vault Runner Game")
        print("8. Try Language Extensions")
        print("9. Launch GUI Game")
        print("10. Exit")
        
        choice = input("\nEnter your choice (1-10): ").strip()
        
        if choice == '1':
            print_program_analysis()
            
        elif choice == '2':
            demo_corridor_program()
            
        elif choice == '3':
            demo_room_program()
            
        elif choice == '4':
            demo_multikey_program()
            
        elif choice == '5':
            demo_custom_program()
            
        elif choice == '6':
            show_world_visualizations()
            
        elif choice == '7':
            game = VaultRunnerGame()
            game.start_game()
            
        elif choice == '8':
            demo_extensions()
            
        elif choice == '9':
            launch_gui_game()
            
        elif choice == '10':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")


def demo_corridor_program():
    """Demonstrate Program 1: Corridor Navigation."""
    print("\n" + "=" * 60)
    print("PROGRAM 1: CORRIDOR NAVIGATION")
    print("=" * 60)
    
    print("\nProgram Description:")
    print("- Navigate a twisting corridor blocked at both ends")
    print("- Robot starts at unknown position and direction")
    print("- Must collect key, open door, and escape")
    print("- Uses WHILE loops and IF conditionals")
    
    # Show the program code
    print("\nProgram Code:")
    print("-" * 20)
    for i, line in enumerate(program1_corridor, 1):
        print(f"{i:2d}: {line}")
    
    # Analyze program
    interpreter = VaultInterpreter(program1_corridor)
    analysis = interpreter.analyze_program()
    print(f"\nProgram Analysis:")
    print(f"- Total tokens: {analysis['total_tokens']}")
    print(f"- Distinct tokens: {analysis['distinct_tokens']}/20")
    print(f"- Control structures: {analysis['control_structures']}")
    print(f"- Max nesting depth: {analysis['max_nesting_depth']}")
    
    # Create world and runner
    world = create_corridor_world()
    runner = VaultRunner(world, (0, 0), 1)  # Start facing East
    
    print("\nInitial World State:")
    runner.display_world()
    
    # Ask if user wants to see step-by-step execution
    show_steps = input("\nShow step-by-step execution? (y/n): ").lower().startswith('y')
    
    # Run the program
    print("\nExecuting program...")
    interpreter.set_debug_mode(show_steps)
    result = interpreter.run(runner, show_steps=show_steps)
    
    print(f"\n{'SUCCESS!' if result else 'FAILED!'}")
    if result:
        print("✓ Robot successfully escaped from the corridor!")
    else:
        print("✗ Robot failed to escape. Check the program logic.")


def demo_room_program():
    """Demonstrate Program 2: Room Exploration."""
    print("\n" + "=" * 60)
    print("PROGRAM 2: ROOM EXPLORATION") 
    print("=" * 60)
    
    print("\nProgram Description:")
    print("- Navigate a rectangular room with no obstacles")
    print("- Robot starts at bottom-left corner facing north")
    print("- Uses bounded loop with right-hand rule navigation")
    print("- Collects key and opens door when encountered")
    
    # Show program code
    print("\nProgram Code:")
    print("-" * 20)
    for i, line in enumerate(program2_room, 1):
        print(f"{i:2d}: {line}")
    
    # Analyze program
    interpreter = VaultInterpreter(program2_room)
    analysis = interpreter.analyze_program()
    print(f"\nProgram Analysis:")
    print(f"- Total tokens: {analysis['total_tokens']}")
    print(f"- Distinct tokens: {analysis['distinct_tokens']}/20")
    print(f"- Control structures: {analysis['control_structures']}")
    
    # Create world and runner
    world = create_room_world()
    runner = VaultRunner(world, (0, 0), 0)  # Start facing North
    
    print("\nInitial World State:")
    runner.display_world()
    
    # Run program
    print("\nExecuting program...")
    result = interpreter.run(runner, show_steps=False)
    
    print(f"\n{'SUCCESS!' if result else 'COMPLETED'}")
    if result:
        print("✓ Robot successfully escaped from the room!")
    else:
        print("◦ Robot completed exploration (may not have found exit)")


def demo_multikey_program():
    """Demonstrate Program 3: Multi-key Challenge (Optional)."""
    print("\n" + "=" * 60)
    print("PROGRAM 3: MULTI-KEY CHALLENGE (OPTIONAL)")
    print("=" * 60)
    
    print("\nProgram Description:")
    print("- Room contains multiple keys, only one opens the door")
    print("- Robot starts at unknown position and direction")
    print("- Uses random exploration with key testing")
    print("- More complex logic with flag management")
    
    # Show program code
    print("\nProgram Code:")
    print("-" * 20)
    for i, line in enumerate(program3_multikey, 1):
        print(f"{i:2d}: {line}")
    
    # Create world and runner
    world = create_multi_key_world()
    runner = VaultRunner(world, (4, 3), 0)  # Random start
    
    print("\nInitial World State:")
    runner.display_world()
    
    # Run program
    print("\nExecuting program...")
    interpreter = VaultInterpreter(program3_multikey)
    result = interpreter.run(runner, show_steps=False)
    
    print(f"\n{'SUCCESS!' if result else 'COMPLETED'}")


def demo_custom_program():
    """Allow user to input a custom program."""
    print("\n" + "=" * 60)
    print("CUSTOM PROGRAM INPUT")
    print("=" * 60)
    
    print("\nAvailable commands:")
    print("Actions: MOVE, LEFT, RIGHT, RTURN, PICK, OPEN")
    print("Control: LOOP <n>, WHILE <sensor>, IF <sensor>, END")
    print("Sensors: FRONT, KEY, DOOR, EXIT")
    print("State: SET, CLR")
    
    print("\nEnter your program (one command per line, empty line to finish):")
    
    program_lines = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        program_lines.append(line)
    
    if not program_lines:
        print("No program entered.")
        return
    
    try:
        # Create interpreter
        interpreter = VaultInterpreter(program_lines)
        analysis = interpreter.analyze_program()
        
        print(f"\nProgram Analysis:")
        print(f"- Total tokens: {analysis['total_tokens']}")
        print(f"- Distinct tokens: {analysis['distinct_tokens']}/20")
        print(f"- Tokens used: {', '.join(analysis['distinct_token_list'])}")
        
        # Choose world
        print("\nSelect world:")
        print("1. Corridor world")
        print("2. Room world")
        print("3. Multi-key world")
        
        world_choice = input("Enter choice (1-3): ").strip()
        
        if world_choice == '1':
            world = create_corridor_world()
            start_pos, start_dir = (0, 0), 1
        elif world_choice == '2':
            world = create_room_world()
            start_pos, start_dir = (0, 0), 0
        elif world_choice == '3':
            world = create_multi_key_world()
            start_pos, start_dir = (4, 3), 0
        else:
            print("Invalid choice, using room world.")
            world = create_room_world()
            start_pos, start_dir = (0, 0), 0
        
        # Create runner and execute
        runner = VaultRunner(world, start_pos, start_dir)
        print("\nInitial world:")
        runner.display_world()
        
        print("\nExecuting custom program...")
        result = interpreter.run(runner, show_steps=True)
        
        print(f"\n{'SUCCESS!' if result else 'COMPLETED'}")
        
    except Exception as e:
        print(f"Error in custom program: {e}")


def show_world_visualizations():
    """Show all world visualizations."""
    print("\n" + "=" * 60)
    print("WORLD VISUALIZATIONS")
    print("=" * 60)
    
    print("\n1. CORRIDOR WORLD:")
    print("-" * 20)
    corridor_world = create_corridor_world()
    runner1 = VaultRunner(corridor_world, (0, 0), 1)
    runner1.display_world()
    
    print("\n2. ROOM WORLD:")
    print("-" * 20)
    room_world = create_room_world()
    runner2 = VaultRunner(room_world, (0, 0), 0)
    runner2.display_world()
    
    print("\n3. MULTI-KEY WORLD:")
    print("-" * 20)
    multi_world = create_multi_key_world()
    runner3 = VaultRunner(multi_world, (4, 3), 0)
    runner3.display_world()
    
    print("Legend:")
    print("███ = Wall    · = Floor    K = Key    D = Door    E = Exit")
    print("^>v< = Robot facing North/East/South/West")


def batch_demo():
    """Run all demonstrations in sequence for presentation."""
    print("=" * 70)
    print("VAULT RUNNER PROGRAMMING LANGUAGE - BATCH DEMONSTRATION")
    print("=" * 70)
    
    # Show program analysis
    print_program_analysis()
    
    # Run corridor program
    print("\n" + "=" * 60)
    print("RUNNING CORRIDOR PROGRAM")
    print("=" * 60)
    
    world = create_corridor_world()
    runner = VaultRunner(world, (0, 0), 1)
    interpreter = VaultInterpreter(program1_corridor)
    
    print("Initial state:")
    runner.display_world()
    
    result1 = interpreter.run(runner, show_steps=False)
    print(f"Corridor result: {'SUCCESS' if result1 else 'FAILED'}")
    
    # Run room program
    print("\n" + "=" * 60)
    print("RUNNING ROOM PROGRAM")
    print("=" * 60)
    
    world = create_room_world()
    runner = VaultRunner(world, (0, 0), 0)
    interpreter = VaultInterpreter(program2_room)
    
    print("Initial state:")
    runner.display_world()
    
    result2 = interpreter.run(runner, show_steps=False)
    print(f"Room result: {'SUCCESS' if result2 else 'COMPLETED'}")
    
    # Summary
    print("\n" + "=" * 60)
    print("DEMONSTRATION SUMMARY")
    print("=" * 60)
    print(f"Program 1 (Corridor): {'SUCCESS' if result1 else 'FAILED'}")
    print(f"Program 2 (Room): {'SUCCESS' if result2 else 'COMPLETED'}")
    print("\nAll demonstrations completed!")


def demo_extensions():
    """Demonstrate language extensions."""
    print("\n" + "=" * 60)
    print("LANGUAGE EXTENSIONS DEMO")
    print("=" * 60)
    
    print("Available extended commands:")
    print("  WAIT <n>    - Pause execution for n steps")
    print("  MARK        - Mark current position")
    print("  GOTO        - Move to marked position")
    print("  SCAN        - Check all directions")
    print("  COUNT       - Count items in area")
    print("  SAVE        - Save current state")
    print("  LOAD        - Restore saved state")
    
    print("\nSample extended program:")
    sample_program = [
        "MARK",
        "MOVE",
        "MOVE",
        "IF KEY",
        "  PICK",
        "END",
        "GOTO",
        "IF DOOR",
        "  OPEN",
        "END"
    ]
    
    for i, line in enumerate(sample_program, 1):
        print(f"{i:2d}: {line}")
    
    print("\nTesting extended program...")
    
    try:
        # Create extended world
        world = LanguageExtensions.create_extended_world(6)
        runner = AdvancedVaultRunner(world, (0, 0), 1, enable_extensions=True)
        
        print("Extended world:")
        runner.display_world()
        
        # Test with extended interpreter
        interpreter = ExtendedVaultInterpreter(sample_program, enable_extensions=True)
        result = interpreter.run(runner, show_steps=True)
        
        print(f"\nResult: {'SUCCESS' if result else 'COMPLETED'}")
        
        # Show analysis
        analysis = LanguageExtensions.analyze_program_complexity(sample_program)
        print(f"Program analysis:")
        print(f"  Has extensions: {analysis.get('has_extensions', False)}")
        print(f"  Extension count: {analysis.get('extension_count', 0)}")
        print(f"  Total tokens: {analysis.get('total_tokens', 0)}")
        print(f"  Distinct tokens: {analysis.get('distinct_tokens', 0)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def launch_gui_game():
    """Launch the GUI version of the Vault Runner game."""
    try:
        from gui_game import main as gui_main
        print("Launching GUI game...")
        gui_main()
    except ImportError as e:
        print(f"Error: PyQt5 is required for the GUI game. {e}")
        print("Please install PyQt5: pip install PyQt5")
    except Exception as e:
        print(f"Error launching GUI: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--batch':
        batch_demo()
    else:
        interactive_demo()


if __name__ == "__main__":
    main()
