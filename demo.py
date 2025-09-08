#!/usr/bin/env python3
"""
Vault Runner Programming Language - Feature Demo

This script demonstrates all the features of the Vault Runner programming language:
- Core language functionality
- Interactive game
- Language extensions
- Program analysis
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'scratch'))

from interpreter import VaultInterpreter
from vault_runner import VaultRunner, create_corridor_world, create_room_world
from extensions import ExtendedVaultInterpreter, LanguageExtensions
from game import VaultRunnerGame


def demo_core_language():
    """Demonstrate core language features."""
    print("=" * 60)
    print("🏗️  CORE LANGUAGE DEMO")
    print("=" * 60)
    
    # Simple program
    program = [
        "MOVE",
        "MOVE", 
        "IF KEY",
        "  PICK",
        "END",
        "LEFT",
        "MOVE"
    ]
    
    print("Program:")
    for i, line in enumerate(program, 1):
        print(f"  {i}: {line}")
    
    # Create world and run
    world = create_room_world()
    runner = VaultRunner(world, (0, 0), 1)  # Start facing East
    
    print("\nInitial world:")
    runner.display_world()
    
    interpreter = VaultInterpreter(program)
    result = interpreter.run(runner, show_steps=False)
    
    print(f"\nResult: {'SUCCESS' if result else 'COMPLETED'}")
    print(f"Instructions executed: {interpreter.instruction_count}")
    
    # Analyze program
    analysis = interpreter.analyze_program()
    print(f"\nProgram Analysis:")
    print(f"  Total tokens: {analysis['total_tokens']}")
    print(f"  Distinct tokens: {analysis['distinct_tokens']}/20")
    print(f"  Complexity score: {analysis['complexity_score']}")


def demo_extensions():
    """Demonstrate language extensions."""
    print("\n" + "=" * 60)
    print("🔧 LANGUAGE EXTENSIONS DEMO")
    print("=" * 60)
    
    # Extended program
    program = [
        "MARK",      # Mark current position
        "MOVE",
        "MOVE",
        "IF KEY",
        "  PICK",
        "  SAVE",    # Save state after picking key
        "END",
        "GOTO",      # Return to marked position
        "IF DOOR",
        "  OPEN",
        "END"
    ]
    
    print("Extended Program:")
    for i, line in enumerate(program, 1):
        print(f"  {i}: {line}")
    
    # Create extended world
    world = LanguageExtensions.create_extended_world(6)
    runner = VaultRunner(world, (0, 0), 1)
    
    print("\nExtended world:")
    runner.display_world()
    
    # Run with extended interpreter
    interpreter = ExtendedVaultInterpreter(program, enable_extensions=True)
    result = interpreter.run(runner, show_steps=False)
    
    print(f"\nResult: {'SUCCESS' if result else 'COMPLETED'}")
    
    # Analyze with extensions
    analysis = LanguageExtensions.analyze_program_complexity(program)
    print(f"\nExtended Analysis:")
    print(f"  Has extensions: {analysis.get('has_extensions', False)}")
    print(f"  Extension count: {analysis.get('extension_count', 0)}")
    print(f"  Total tokens: {analysis.get('total_tokens', 0)}")


def demo_game_features():
    """Demonstrate game features."""
    print("\n" + "=" * 60)
    print("🎮 GAME FEATURES DEMO")
    print("=" * 60)
    
    # Create a game instance
    game = VaultRunnerGame()
    
    print("Available Challenges:")
    for i, challenge in enumerate(game.challenges, 1):
        status = "✅" if challenge.best_score else "⭕"
        print(f"  {i}. {status} {challenge.name}")
        print(f"     {challenge.description}")
    
    # Test a simple program on the first challenge
    print(f"\nTesting program on '{game.challenges[0].name}':")
    test_program = ["MOVE", "MOVE", "MOVE"]
    
    result = game.challenges[0].test_program(test_program)
    print(f"  Success: {'✅' if result['success'] else '❌'}")
    print(f"  Score: {result['score']}")
    print(f"  Instructions: {result['instructions']}")


def demo_sample_programs():
    """Demonstrate sample programs."""
    print("\n" + "=" * 60)
    print("📝 SAMPLE PROGRAMS DEMO")
    print("=" * 60)
    
    # Get sample programs
    programs = LanguageExtensions.create_sample_extended_programs()
    
    for name, program in programs.items():
        print(f"\n{name.replace('_', ' ').title()}:")
        for i, line in enumerate(program, 1):
            print(f"  {i}: {line}")
        
        # Analyze the program
        analysis = LanguageExtensions.analyze_program_complexity(program)
        print(f"  Analysis: {analysis.get('distinct_tokens', 0)} distinct tokens, "
              f"{analysis.get('extension_count', 0)} extensions")


def main():
    """Run all demonstrations."""
    print("🏰 VAULT RUNNER PROGRAMMING LANGUAGE - FEATURE DEMO 🏰")
    print("=" * 70)
    print("This demo showcases all the features of the Vault Runner language:")
    print("• Core programming language with constraints")
    print("• Interactive game with challenges")
    print("• Language extensions for advanced features")
    print("• Program analysis and complexity metrics")
    print("• Visual robot simulation")
    
    try:
        demo_core_language()
        demo_extensions()
        demo_game_features()
        demo_sample_programs()
        
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nTo explore more features:")
        print("• Run 'python3 -m scratch' for interactive mode")
        print("• Try the game: Select option 7 in the menu")
        print("• Test extensions: Select option 8 in the menu")
        print("• Run tests: 'python3 -m unittest tests/test.py'")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
