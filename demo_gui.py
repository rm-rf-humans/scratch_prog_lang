#!/usr/bin/env python3
"""
Vault Runner GUI Demo

This script demonstrates the GUI features of the Vault Runner game.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Run the GUI demo."""
    print("Vault Runner GUI Demo")
    print("=" * 50)
    print()
    print("This demo will launch the Vault Runner GUI game.")
    print("The GUI includes:")
    print("• Visual world display with real-time robot visualization")
    print("• Program editor with syntax highlighting")
    print("• Interactive program execution with step-by-step feedback")
    print("• Challenge selection and scoring system")
    print("• Program analysis with token counting")
    print()
    print("Features to try:")
    print("1. Select different challenges from the dropdown")
    print("2. Write a simple program like:")
    print("   MOVE")
    print("   MOVE")
    print("   IF KEY")
    print("     PICK")
    print("   END")
    print("3. Click 'Run Program' to see it execute")
    print("4. Watch the robot move in real-time")
    print("5. Check the program analysis panel")
    print()
    
    input("Press Enter to launch the GUI...")
    
    try:
        from scratch.gui_game import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error: PyQt5 is required for the GUI game.")
        print(f"Import error: {e}")
        print("\nTo install PyQt5:")
        print("  brew install pyqt5  # On macOS")
        print("  pip install PyQt5  # On other systems")
        sys.exit(1)
    except Exception as e:
        print(f"Error launching GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
