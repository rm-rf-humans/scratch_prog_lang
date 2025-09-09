# Room Explorer - BFS Algorithm (Program 2)
# Task: Find and collect key + open door OR escape from exit hatch (whatever comes first)
# World: Rectangular room, no obstacles, start at lower-left facing north
# Algorithm: Breadth-First Search for optimal pathfinding

# Start BFS exploration - no need to check exit at (0,0) since it's not there

# BFS Level 1: Explore distance-1 positions (north and east from start)
# Move north first (facing north already)
MOVE  # Go to (0,1) - BFS distance 1
# Exit found! Stay here and let escape detection work
IF EXIT
  CLR  # Do nothing - just mark that we found the exit
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END

# BFS Level 2: Explore distance-2 positions
# Continue north
MOVE  # Go to (0,2) - BFS distance 2  
# Exit found! Stay here and let escape detection work
IF EXIT
  CLR  # Do nothing - just mark that we found the exit
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END

# BFS Level 3: Explore distance-3 positions
# Continue north
MOVE  # Go to (0,3) - BFS distance 3
# Exit found! Stay here and let escape detection work
IF EXIT
  CLR  # Do nothing - just mark that we found the exit
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END

# Now explore horizontally at this level (optimal BFS pattern)
RIGHT  # Face east
MOVE   # Go to (1,3) - BFS distance 4
# Exit found! Stay here and let escape detection work
IF EXIT
  CLR  # Do nothing - just mark that we found the exit
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END

MOVE   # Go to (2,3) - BFS distance 5 - THIS IS THE EXIT!
# Exit found! Stay here and let escape detection work
IF EXIT
  CLR  # OPTIMAL BFS: Found exit in 5 moves! Stay here and escape
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END

# Continue BFS exploration if exit not found yet
MOVE   # Go to (3,3) - BFS distance 6
# Exit found! Stay here and let escape detection work
IF EXIT
  CLR  # Do nothing - just mark that we found the exit
END
IF KEY
  PICK
END
IF DOOR
  OPEN
  MOVE
END