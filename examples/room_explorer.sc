# Room Explorer - Program 2
# Robot starts at lower-left facing north
# Room has no obstacles, contains key, door, and exit
LOOP 50
  IF FRONT
    MOVE
  END
  RIGHT
  IF KEY
    PICK
  END
  IF DOOR
    OPEN
  END
END
