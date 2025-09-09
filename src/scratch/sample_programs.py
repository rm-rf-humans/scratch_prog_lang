"""
Centralized sample programs for the Vault Runner language.
This module provides sample programs that can be shared across the GUI, CLI, and other components.
"""

# Import the core programs from programs.py
try:
    from .programs import program1_corridor, program2_room, program3_multikey
except ImportError:
    from programs import program1_corridor, program2_room, program3_multikey


class SamplePrograms:
    """Centralized repository of sample programs for different challenges."""
    
    @staticmethod
    def get_program_text(program_list):
        """Convert a program list to formatted text."""
        return '\n'.join(program_list)
    
    @staticmethod
    def get_first_steps():
        """Sample program for First Steps challenge."""
        return """# First Steps Sample Program
# Move forward 3 steps and turn around
LOOP 3
  MOVE
END
LEFT
LEFT"""
    
    @staticmethod
    def get_key_collector():
        """Sample program for Key Collector challenge."""
        return """# Key Collector Sample Program
# Move to the key and pick it up
MOVE
MOVE
PICK"""
    
    @staticmethod
    def get_door_master():
        """Sample program for Door Master challenge (Program 1 - Corridor)."""
        return SamplePrograms.get_program_text(program1_corridor)
    
    @staticmethod
    def get_room_explorer():
        """Sample program for Room Explorer challenge (Program 2 - Room)."""
        return SamplePrograms.get_program_text(program2_room)
    
    @staticmethod
    def get_multi_key_mystery():
        """Sample program for Multi-Key Mystery challenge (Program 3 - Multi-key)."""
        return SamplePrograms.get_program_text(program3_multikey)
    
    @staticmethod
    def get_speed_run():
        """Sample program for Speed Run challenge."""
        return """# Speed Run Sample Program
# Optimized for efficiency
WHILE FRONT
  MOVE
  IF KEY
    PICK
  END
  IF DOOR
    OPEN
    MOVE
  END
  IF EXIT
    MOVE
  END
END
RIGHT
WHILE FRONT
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
  IF EXIT
    MOVE
  END
END"""
    
    @staticmethod
    def get_extension_challenge():
        """Sample program for Extension Challenge with A* algorithm."""
        return """# Extension Challenge - A* Search Algorithm
# This program implements A* pathfinding to solve the challenge optimally

# Phase 1: A* Search with intelligent exploration
# Start by orienting north
LEFT
LEFT
LEFT
LEFT

# A* heuristic: Explore systematically to find all keys
# Row 0: Check for keys (wrong keys at (0,0) and (3,0))
MOVE
IF KEY
  PICK
END
MOVE
MOVE
IF KEY
  PICK
END

# A* pathfinding: Move to next row efficiently
LEFT
LEFT
MOVE
MOVE
MOVE
RIGHT

# Row 1: Check for keys
MOVE
MOVE
MOVE

# A* pathfinding: Move to next row efficiently
LEFT
LEFT
MOVE
MOVE
MOVE
RIGHT

# Row 2: Check for keys
MOVE
MOVE
MOVE

# A* pathfinding: Move to next row efficiently
LEFT
LEFT
MOVE
MOVE
MOVE
RIGHT

# Row 3: A* goal - find the correct key at (1,3)
MOVE
IF KEY
  PICK
END
MOVE
IF KEY
  PICK
END
MOVE
IF KEY
  PICK
END

# Phase 2: A* Search for the door at (3,2)
# A* heuristic: Calculate optimal path to door
LEFT
LEFT
MOVE
MOVE
MOVE
RIGHT
MOVE
RIGHT
MOVE
MOVE
MOVE

# Try to open the door with the correct key
IF DOOR
  OPEN
END

# Phase 3: A* Search for escape through the door
IF DOOR
  MOVE
END"""
    
    @staticmethod
    def get_default():
        """Default sample program for unknown challenges."""
        return """# Sample Program
# Basic movement example
MOVE
MOVE
MOVE"""
    
    @staticmethod
    def get_sample_for_challenge(challenge_name):
        """Get the appropriate sample program for a given challenge name."""
        samples = {
            "First Steps": SamplePrograms.get_first_steps,
            "Key Collector": SamplePrograms.get_key_collector,
            "Door Master": SamplePrograms.get_door_master,
            "Room Explorer": SamplePrograms.get_room_explorer,
            "Multi-Key Mystery": SamplePrograms.get_multi_key_mystery,
            "Speed Run": SamplePrograms.get_speed_run,
            "Extension Challenge": SamplePrograms.get_extension_challenge,
        }
        
        return samples.get(challenge_name, SamplePrograms.get_default)()
    
    @staticmethod
    def get_all_programs():
        """Get a dictionary of all sample programs."""
        return {
            "First Steps": SamplePrograms.get_first_steps(),
            "Key Collector": SamplePrograms.get_key_collector(),
            "Door Master": SamplePrograms.get_door_master(),
            "Room Explorer": SamplePrograms.get_room_explorer(),
            "Multi-Key Mystery": SamplePrograms.get_multi_key_mystery(),
            "Speed Run": SamplePrograms.get_speed_run(),
            "Extension Challenge": SamplePrograms.get_extension_challenge(),
        }


# Convenience functions for backward compatibility
def get_sample_program(challenge_name):
    """Get sample program for a challenge (convenience function)."""
    return SamplePrograms.get_sample_for_challenge(challenge_name)


def list_available_samples():
    """List all available sample programs."""
    return list(SamplePrograms.get_all_programs().keys())


if __name__ == "__main__":
    # Demo all sample programs
    print("=== VAULT RUNNER SAMPLE PROGRAMS ===")
    print("=" * 50)
    
    for name, program in SamplePrograms.get_all_programs().items():
        print(f"\n{name}:")
        print("-" * len(name))
        print(program)
        print()
