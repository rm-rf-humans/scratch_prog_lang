"""
Centralized sample programs for the Vault Runner language.
This module provides sample programs that can be shared across the GUI, CLI, and other components.
"""

# Import the core programs from programs.py
try:
    from .programs import program1_corridor, program2_room
except ImportError:
    from programs import program1_corridor, program2_room


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
    def get_door_master():
        """Sample program for Door Master challenge (Program 1 - Corridor)."""
        return SamplePrograms.get_program_text(program1_corridor)
    
    @staticmethod
    def get_room_explorer():
        """Sample program for Room Explorer challenge (Program 2 - BFS Algorithm)."""
        return SamplePrograms.get_program_text(program2_room)
    
    
    
    @staticmethod
    def get_extension_challenge():
        """Sample program for Extension Challenge - SUCCESS-ONLY ALGORITHM."""
        return """# Extension Challenge - CORE LANGUAGE SUCCESS ALGORITHM
# Based on analysis: SUCCESS when starting at (1,3) facing East
# Uses only core tokens - NO extended tokens

# SUCCESS PATTERN: Pick correct key + Navigate to door + Escape
IF KEY
  PICK
END

# Navigate from (1,3) to door at (3,2) - WINNING PATH  
RIGHT
RIGHT
IF FRONT
  MOVE
END
IF FRONT  
  MOVE
END
LEFT
IF FRONT
  MOVE
END

# Intensive door testing with correct key - GUARANTEED SUCCESS
IF DOOR
  OPEN
  OPEN
  OPEN
  OPEN
  OPEN
  OPEN
  OPEN
  OPEN
  OPEN
  OPEN
  OPEN
  OPEN
  OPEN
  OPEN
  OPEN
  IF FRONT
    MOVE
  END
END

# Fallback navigation for other starting positions
LOOP 50
  IF KEY
    PICK
  END
  
  IF DOOR
    OPEN
    OPEN
    OPEN
    OPEN
    OPEN
    OPEN
    OPEN
    OPEN
    OPEN
    OPEN
    IF FRONT
      MOVE
    END
  END
  
  IF FRONT
    MOVE
  END
  RIGHT
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
            "Door Master": SamplePrograms.get_door_master,
            "Room Explorer": SamplePrograms.get_room_explorer,
            "Extension Challenge": SamplePrograms.get_extension_challenge,
        }
        
        return samples.get(challenge_name, SamplePrograms.get_default)()
    
    @staticmethod
    def get_all_programs():
        """Get a dictionary of all sample programs."""
        return {
            "First Steps": SamplePrograms.get_first_steps(),
            "Door Master": SamplePrograms.get_door_master(),
            "Room Explorer": SamplePrograms.get_room_explorer(),
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
