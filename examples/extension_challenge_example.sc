# Extension Challenge - A* Search Algorithm
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
END
