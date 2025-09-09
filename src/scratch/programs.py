program1_corridor = [
    # Navigate twisting corridor with unknown start position/direction
    # Strategy: Systematic exploration - move until blocked, turn right, repeat
    # This works from any starting position and direction in the corridor
    "LOOP 4",
    "  WHILE FRONT",
    "    MOVE",
    "    IF KEY",
    "      PICK",
    "    END",
    "    IF DOOR",
    "      OPEN",
    "    END",
    "    IF EXIT",
    "      MOVE",
    "    END",
    "  END",
    "  RIGHT",
    "END"
]

# Program 2: Navigate rectangular room
# Robot starts at lower-left facing north
# Room has no obstacles, contains key, door, and exit
program2_room = [
    "LOOP 50",
    "  IF FRONT",
    "    MOVE",
    "  END",
    "  RIGHT",
    "  IF KEY",
    "    PICK",
    "  END", 
    "  IF DOOR",
    "    OPEN",
    "  END",
    "END"
]

# Program 3 (Optional Extension): Multiple keys scenario
# Only one key opens the door, robot starts at unknown position
program3_multikey = [
    "SET",  # Flag to track if we've tried opening door
    "LOOP 100",
    "  IF FRONT",
    "    MOVE",
    "  END",
    "  RTURN",  # Random exploration
    "  IF KEY",
    "    PICK",
    "    IF DOOR",  # If we find door, try to open it
    "      OPEN",
    "      CLR",  # Clear flag if door opens (success)
    "    END",
    "  END",
    "  IF DOOR",
    "    OPEN",  # Always try to open if we have any key
    "  END",
    "END"
]

# Simplified test programs for debugging

simple_move = [
    "MOVE",
    "MOVE",
    "LEFT", 
    "MOVE"
]

simple_loop = [
    "LOOP 3",
    "  MOVE",
    "  RIGHT",
    "END"
]

simple_conditional = [
    "IF FRONT",
    "  MOVE",
    "  MOVE",
    "END",
    "LEFT"
]

# Analysis function for programs
def analyze_all_programs():
    """Analyze all programs and return statistics."""
    from interpreter import VaultInterpreter
    
    programs = {
        'Program 1 (Corridor)': program1_corridor,
        'Program 2 (Room)': program2_room, 
        'Program 3 (Multi-key)': program3_multikey,
        'Simple Move': simple_move,
        'Simple Loop': simple_loop,
        'Simple Conditional': simple_conditional
    }
    
    results = {}
    
    for name, program in programs.items():
        try:
            interpreter = VaultInterpreter(program)
            analysis = interpreter.analyze_program()
            results[name] = analysis
        except Exception as e:
            results[name] = {'error': str(e)}
    
    return results

def print_program_analysis():
    """Print detailed analysis of all programs."""
    results = analyze_all_programs()
    
    print("=" * 60)
    print("VAULT RUNNER PROGRAM ANALYSIS")
    print("=" * 60)
    
    for name, analysis in results.items():
        print(f"\n{name}:")
        print("-" * len(name))
        
        if 'error' in analysis:
            print(f"  ERROR: {analysis['error']}")
            continue
            
        print(f"  Total tokens: {analysis['total_tokens']}")
        print(f"  Distinct tokens: {analysis['distinct_tokens']}")
        print(f"  Control structures: {analysis['control_structures']}")
        print(f"  Max nesting depth: {analysis['max_nesting_depth']}")
        print(f"  Complexity score: {analysis['complexity_score']}")
        print(f"  Tokens used: {', '.join(analysis['distinct_token_list'])}")

def run_program_demo(program_name, program, world_creator, start_pos, start_dir, show_steps=False):
    """Run a program demonstration."""
    from interpreter import VaultInterpreter
    from vault_runner import VaultRunner
    
    print(f"\n{'=' * 50}")
    print(f"RUNNING: {program_name}")
    print(f"{'=' * 50}")
    
    # Create world and runner
    world = world_creator()
    runner = VaultRunner(world, start_pos, start_dir)
    
    # Show initial state
    print("Initial world state:")
    runner.display_world()
    
    # Create and run interpreter
    try:
        interpreter = VaultInterpreter(program)
        
        # Show program analysis
        analysis = interpreter.analyze_program()
        print(f"Program tokens: {analysis['total_tokens']}")
        print(f"Distinct tokens: {analysis['distinct_tokens']}")
        
        # Run the program
        result = interpreter.run(runner, show_steps=show_steps)
        
        print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")
        
        if not show_steps:
            print("Final world state:")
            runner.display_world()
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    from vault_runner import create_corridor_world, create_room_world, create_multi_key_world
    
    # Print analysis of all programs
    print_program_analysis()
    
    # Demo corridor program
    run_program_demo(
        "Program 1: Corridor Navigation",
        program1_corridor,
        create_corridor_world,
        (0, 0),  # Start position
        1,       # Start direction (East)
        show_steps=True
    )
    
    # Demo room program  
    run_program_demo(
        "Program 2: Room Exploration", 
        program2_room,
        create_room_world,
        (0, 0),  # Start position (bottom-left)
        0,       # Start direction (North)
        show_steps=False
    )
    
    # Demo multi-key program (optional)
    run_program_demo(
        "Program 3: Multi-key Challenge",
        program3_multikey, 
        create_multi_key_world,
        (4, 3),  # Random start position
        0,       # Start direction (North)
        show_steps=False
    )
