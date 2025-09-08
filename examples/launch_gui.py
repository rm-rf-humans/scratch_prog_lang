#!/usr/bin/env python3
"""
Vault Runner GUI Launcher

This script launches the GUI version of the Vault Runner game.
It can be run independently or as part of the main application.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Launch the GUI game."""
    try:
        from scratch.gui_game import main as gui_main
        print("Starting Vault Runner GUI...")
        gui_main()
    except ImportError as e:
        print(f"Error: PyQt5 is required for the GUI game.")
        print(f"Import error: {e}")
        print("\nTo install PyQt5:")
        print("  pip install PyQt5")
        print("\nOr install all dependencies:")
        print("  pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"Error launching GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
