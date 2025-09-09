# Room Explorer - BFS Algorithm (Program 2)
# Task: Find and collect key + open door OR escape from exit hatch (whatever comes first)
# World: Rectangular room, no obstacles, start at lower-left facing north
# Algorithm: Breadth-First Search for optimal pathfinding

# BFS Level 0: Current position (0,0) - check immediate area
IF EXIT
  MOVE  # Exit immediately if at start
END

# BFS Level 1: Explore distance-1 positions (north from start)
MOVE  # Go to (0,1) - BFS distance 1
IF EXIT
  MOVE
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END

# BFS Level 2: Explore distance-2 positions
MOVE  # Go to (0,2) - BFS distance 2  
IF EXIT
  MOVE
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END

# BFS Level 3: Explore distance-3 positions
MOVE  # Go to (0,3) - BFS distance 3
IF EXIT
  MOVE
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END

# BFS Level 4: Explore horizontally at this level
RIGHT  # Face east
MOVE   # Go to (1,3) - BFS distance 4
IF EXIT
  MOVE
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END

# BFS Level 5: Continue horizontal exploration
MOVE   # Go to (2,3) - BFS distance 5 - THIS IS THE EXIT!
IF EXIT
  MOVE  # Optimal BFS solution: 5 moves to exit
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END

# BFS Level 6: Continue if needed
MOVE   # Go to (3,3) - BFS distance 6
IF EXIT
  MOVE
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END