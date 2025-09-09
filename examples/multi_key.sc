# Multi-Key Challenge - Program 3
# Only one key opens the door, robot starts at unknown position
SET
LOOP 100
  IF FRONT
    MOVE
  END
  RTURN
  IF KEY
    PICK
    IF DOOR
      OPEN
      CLR
    END
  END
  IF DOOR
    OPEN
  END
END
