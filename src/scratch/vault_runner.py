class VaultRunner:
    def __init__(self, world_map=None, start_pos=(0, 0), start_dir=0):
        self.x, self.y = start_pos
        self.direction = start_dir  # 0=North, 1=East, 2=South, 3=West
        self.has_key = False
        self.door_opened = False
        self.escaped = False
        self.escape_via = None  # 'exit' or 'door'
        self.original_world = None
        
        # Use provided world or create default
        if world_map is None:
            world_map = self._create_default_world()
        
        self.world = world_map.copy()
        self.original_world = world_map.copy()  # For reset functionality
        self.actions_log = []
        
        # Calculate world bounds for visualization
        self._calculate_bounds()
    
    def _create_default_world(self):
        """Create a simple default world for testing."""
        return {
            (0, 0): 'floor', (1, 0): 'key', (2, 0): 'door', (3, 0): 'exit',
            (-1, 0): 'wall', (4, 0): 'wall'
        }
    
    def _calculate_bounds(self):
        """Calculate the bounds of the world for visualization."""
        if not self.world:
            self.min_x = self.max_x = self.min_y = self.max_y = 0
            return
            
        xs = [pos[0] for pos in self.world.keys()]
        ys = [pos[1] for pos in self.world.keys()]
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)
    
    def get_front_position(self):
        """Calculate the position in front of the robot."""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # N, E, S, W
        dx, dy = directions[self.direction]
        return (self.x + dx, self.y + dy)
    
    def is_front_clear(self):
        """Check if the front tile is clear (not a wall)."""
        front_pos = self.get_front_position()
        tile = self.world.get(front_pos, 'wall')
        return tile != 'wall'
    
    def on_key(self):
        """Check if robot is on a key tile."""
        current_tile = self.world.get((self.x, self.y), 'floor')
        return current_tile == 'key'
    
    def at_door(self):
        """Check if robot is at a door tile."""
        current_tile = self.world.get((self.x, self.y), 'floor')
        return current_tile == 'door'
    
    def at_exit(self):
        """Check if robot is at an exit tile.""" 
        current_tile = self.world.get((self.x, self.y), 'floor')
        return current_tile == 'exit'
    
    def move_forward(self):
        """Move the robot forward if possible."""
        if self.is_front_clear():
            front_pos = self.get_front_position()
            self.x, self.y = front_pos
            self.actions_log.append(f"Moved to ({self.x}, {self.y})")
            return True
        else:
            self.actions_log.append("Cannot move forward - blocked")
            return False
    
    def turn_left(self):
        """Turn the robot left."""
        self.direction = (self.direction - 1) % 4
        directions = ['North', 'East', 'South', 'West']
        self.actions_log.append(f"Turned left, now facing {directions[self.direction]}")
    
    def turn_right(self):
        """Turn the robot right."""
        self.direction = (self.direction + 1) % 4
        directions = ['North', 'East', 'South', 'West']
        self.actions_log.append(f"Turned right, now facing {directions[self.direction]}")
    
    def random_turn(self):
        """Randomly turn left or right."""
        import random
        if random.random() < 0.5:
            self.turn_left()
        else:
            self.turn_right()
    
    def pick_key(self):
        """Pick up a key if on one."""
        if self.on_key() and not self.has_key:
            self.has_key = True
            self.world[(self.x, self.y)] = 'floor'
            self.actions_log.append("Picked up key")
            return True
        else:
            self.actions_log.append("Cannot pick key - not on key tile or already have key")
            return False
    
    def pick_key_extension(self, correct_key_pos):
        """Pick up a key for extension challenge - only the correct key works."""
        if self.on_key() and not self.has_key:
            current_pos = (self.x, self.y)
            if current_pos == correct_key_pos:
                self.has_key = True
                self.world[(self.x, self.y)] = 'floor'
                self.actions_log.append("Picked up correct key")
                return True
            else:
                self.actions_log.append("Picked up wrong key - door won't open")
                return False
        else:
            self.actions_log.append("Cannot pick key - not on key tile or already have key")
            return False
    
    def open_door(self):
        """Open door if at door and have key."""
        if self.at_door() and self.has_key:
            self.door_opened = True
            self.actions_log.append("Opened door with key")
            return True
        else:
            self.actions_log.append("Cannot open door - not at door or no key")
            return False
    
    def check_escape(self):
        """Check if robot has escaped."""
        if self.at_exit():
            self.escaped = True
            self.escape_via = 'exit'
            self.actions_log.append("Escaped through exit!")
        elif self.at_door() and self.door_opened:
            self.escaped = True
            self.escape_via = 'door'
            self.actions_log.append("Escaped through opened door!")
        return self.escaped
    
    def display_world(self, show_robot=True):
        """Display the current world state with robot position."""
        print(f"\n=== World State ===")
        print(f"Robot at ({self.x}, {self.y}) facing {['North', 'East', 'South', 'West'][self.direction]}")
        print(f"Has key: {self.has_key}, Door opened: {self.door_opened}, Escaped: {self.escaped}")
        print()
        
        # Create grid representation
        for y in range(self.max_y, self.min_y - 1, -1):
            row = ""
            for x in range(self.min_x, self.max_x + 1):
                pos = (x, y)
                
                # Show robot position
                if show_robot and pos == (self.x, self.y):
                    robot_chars = ['^', '>', 'v', '<']
                    row += f"[{robot_chars[self.direction]}]"
                else:
                    tile = self.world.get(pos, 'void')
                    tile_chars = {
                        'wall': '███',
                        'floor': ' · ',
                        'key': ' K ',
                        'door': ' D ',
                        'exit': ' E ',
                        'void': '   '
                    }
                    row += tile_chars.get(tile, ' ? ')
            print(f"y={y:2d} |{row}|")
        
        # Print x-axis labels
        x_labels = "    |"
        for x in range(self.min_x, self.max_x + 1):
            x_labels += f"{x:3d}"
        print(x_labels + "|")
        print()
    
    def reset(self):
        """Reset the robot and world to initial state."""
        self.x, self.y = 0, 0
        self.direction = 0
        self.has_key = False
        self.door_opened = False
        self.escaped = False
        self.world = self.original_world.copy()
        self.actions_log = []


def create_corridor_world():
    """Create a fixed twisting corridor world for Program 1."""
    return {
        # Main horizontal corridor (y=0)
        (0, 0): 'floor', (1, 0): 'floor', (2, 0): 'floor', 
        (3, 0): 'floor', (4, 0): 'floor', (5, 0): 'key',
        
        # Vertical turn section
        (5, 1): 'floor', (5, 2): 'door', (5, 3): 'floor', (5, 4): 'exit',
        
        # Walls - horizontal corridor boundaries
        (0, 1): 'wall', (1, 1): 'wall', (2, 1): 'wall', 
        (3, 1): 'wall', (4, 1): 'wall',
        (0, -1): 'wall', (1, -1): 'wall', (2, -1): 'wall', 
        (3, -1): 'wall', (4, -1): 'wall', (5, -1): 'wall',
        
        # Walls - vertical section boundaries
        (4, 1): 'wall', (4, 2): 'wall', (4, 3): 'wall', (4, 4): 'wall',
        (6, 1): 'wall', (6, 2): 'wall', (6, 3): 'wall', (6, 4): 'wall',
        
        # End walls
        (-1, 0): 'wall', (-1, -1): 'wall', (-1, 1): 'wall',
        (5, 5): 'wall', (4, 5): 'wall', (6, 5): 'wall'
    }


def create_room_world():
    """Create a fixed rectangular room world for Program 2."""
    world = {}
    
    # 6x4 room interior
    for x in range(6):
        for y in range(4):
            world[(x, y)] = 'floor'
    
    # Surrounding walls
    for x in range(-1, 7):
        world[(x, -1)] = 'wall'  # Bottom wall
        world[(x, 4)] = 'wall'   # Top wall
    for y in range(-1, 5):
        world[(-1, y)] = 'wall'  # Left wall  
        world[(6, y)] = 'wall'   # Right wall
    
    # Fixed positions for key, door, and exit
    world[(4, 2)] = 'key'
    world[(5, 1)] = 'door' 
    world[(2, 3)] = 'exit'
    
    return world


def create_multi_key_world():
    """Create a world with multiple keys for optional Program 3."""
    world = {}
    
    # 8x6 room interior
    for x in range(8):
        for y in range(6):
            world[(x, y)] = 'floor'
    
    # Surrounding walls
    for x in range(-1, 9):
        world[(x, -1)] = 'wall'
        world[(x, 6)] = 'wall'
    for y in range(-1, 7):
        world[(-1, y)] = 'wall'
        world[(8, y)] = 'wall'
    
    # Multiple keys - only one will work
    world[(1, 1)] = 'key'  # Wrong key
    world[(3, 4)] = 'key'  # Wrong key  
    world[(6, 2)] = 'key'  # Correct key (this would need special handling)
    world[(7, 4)] = 'door'
    world[(4, 5)] = 'exit'
    
    return world


if __name__ == "__main__":
    # Demo the world visualization
    print("=== Corridor World ===")
    corridor_world = create_corridor_world()
    runner = VaultRunner(corridor_world, (0, 0), 1)  # Start facing East
    runner.display_world()
    
    print("\n=== Room World ===") 
    room_world = create_room_world()
    runner2 = VaultRunner(room_world, (0, 0), 0)  # Start facing North
    runner2.display_world()
    
    print("\n=== Multi-key World ===")
    multi_world = create_multi_key_world()
    runner3 = VaultRunner(multi_world, (4, 3), 0)  # Random start position
    runner3.display_world()
