"""
Vault Runner Language Extensions

This module provides extended functionality for the Vault Runner programming language,
including new commands, advanced features, and enhanced capabilities while maintaining
compatibility with the core language constraints.
"""

import random
import time
from typing import List, Dict, Any, Optional
from .interpreter import VaultInterpreter
from .vault_runner import VaultRunner


class ExtendedVaultInterpreter(VaultInterpreter):
    """
    Extended interpreter with additional commands and features.
    
    New commands added:
    - WAIT: Pause execution for a specified number of steps
    - MARK: Mark current position for later reference
    - GOTO: Move to a previously marked position
    - SCAN: Check multiple directions at once
    - COUNT: Count items in current area
    - SAVE: Save current state
    - LOAD: Restore saved state
    """
    
    def __init__(self, program_lines, enable_extensions=True):
        """
        Initialize extended interpreter.
        
        Args:
            program_lines: List of program lines
            enable_extensions: Whether to enable extended commands
        """
        self.enable_extensions = enable_extensions
        self.marks = {}  # Store marked positions
        self.saved_states = []  # Store saved states
        self.wait_counter = 0  # Counter for WAIT command
        self.scan_results = {}  # Store scan results
        
        # Initialize parent class
        super().__init__(program_lines)
        
        if enable_extensions:
            self._extend_valid_keywords()
    
    def _extend_valid_keywords(self):
        """Add extended keywords to the valid set."""
        extended_keywords = {
            'WAIT', 'MARK', 'GOTO', 'SCAN', 'COUNT', 'SAVE', 'LOAD',
            'NORTH', 'SOUTH', 'EAST', 'WEST', 'ALL', 'ITEMS'
        }
        
        # Update the tokenizer to include extended keywords
        # This is done by modifying the tokenization process
        pass
    
    def _tokenize(self):
        """Extended tokenization with new keywords."""
        if not self.enable_extensions:
            return super()._tokenize()
        
        valid_keywords = {
            # Original commands
            'MOVE', 'LEFT', 'RIGHT', 'RTURN', 'PICK', 'OPEN',
            'LOOP', 'END', 'IF', 'WHILE',
            'FRONT', 'KEY', 'DOOR', 'EXIT',
            'SET', 'CLR',
            # Extended commands
            'WAIT', 'MARK', 'GOTO', 'SCAN', 'COUNT', 'SAVE', 'LOAD',
            'NORTH', 'SOUTH', 'EAST', 'WEST', 'ALL', 'ITEMS'
        }
        
        tokens = []
        line_num = 0
        
        for line in self.program:
            line_num += 1
            line = line.strip()
            if not line:
                continue
                
            parts = line.split()
            
            for part in parts:
                if part in valid_keywords:
                    tokens.append(part)
                elif part.isdigit():
                    tokens.append(int(part))
                else:
                    raise SyntaxError(f"Invalid token '{part}' on line {line_num}")
        
        # Validate token count constraint (max 20 distinct symbols)
        distinct_tokens = set(str(token) for token in tokens if isinstance(token, str))
        if len(distinct_tokens) > 20:
            raise SyntaxError(f"Too many distinct tokens: {len(distinct_tokens)} (max 20 allowed)")
        
        return tokens
    
    def _execute_instruction(self, token, show_steps):
        """Execute instruction with extended commands."""
        if not self.enable_extensions:
            return super()._execute_instruction(token, show_steps)
        
        # Handle extended commands
        if token == 'WAIT':
            self._execute_wait()
        elif token == 'MARK':
            self._execute_mark()
        elif token == 'GOTO':
            self._execute_goto()
        elif token == 'SCAN':
            self._execute_scan()
        elif token == 'COUNT':
            self._execute_count()
        elif token == 'SAVE':
            self._execute_save()
        elif token == 'LOAD':
            self._execute_load()
        else:
            # Fall back to original instruction execution
            super()._execute_instruction(token, show_steps)
    
    def _execute_wait(self):
        """Execute WAIT command - pause execution."""
        if self.wait_counter > 0:
            self.wait_counter -= 1
            # Don't advance PC, stay on WAIT command
            self.pc -= 1
        else:
            # Get wait duration from next token
            if self.pc + 1 < len(self.tokens) and isinstance(self.tokens[self.pc + 1], int):
                self.wait_counter = self.tokens[self.pc + 1]
                self.pc += 1  # Skip the duration parameter
            else:
                self.wait_counter = 1  # Default wait of 1 step
    
    def _execute_mark(self):
        """Execute MARK command - mark current position."""
        mark_name = f"mark_{len(self.marks)}"  # Auto-generate mark name
        self.marks[mark_name] = (self.runner.x, self.runner.y)
        # Note: show_steps is not available in this context, so we skip the print
    
    def _execute_goto(self):
        """Execute GOTO command - move to marked position."""
        if not self.marks:
            return
        
        # Use the most recent mark
        mark_name = list(self.marks.keys())[-1]
        target_x, target_y = self.marks[mark_name]
        
        # Simple pathfinding - move towards target
        dx = target_x - self.runner.x
        dy = target_y - self.runner.y
        
        if dx != 0 or dy != 0:
            # Turn towards target
            if dx > 0 and self.runner.direction != 1:  # Need to face East
                self.runner.turn_right()
            elif dx < 0 and self.runner.direction != 3:  # Need to face West
                self.runner.turn_left()
            elif dy > 0 and self.runner.direction != 0:  # Need to face North
                self.runner.turn_left()
            elif dy < 0 and self.runner.direction != 2:  # Need to face South
                self.runner.turn_right()
            else:
                # Facing correct direction, try to move
                if self.runner.is_front_clear():
                    self.runner.move_forward()
    
    def _execute_scan(self):
        """Execute SCAN command - check multiple directions."""
        directions = ['NORTH', 'EAST', 'SOUTH', 'WEST']
        scan_result = {}
        
        original_dir = self.runner.direction
        
        for i, direction in enumerate(directions):
            self.runner.direction = i
            scan_result[direction] = {
                'front_clear': self.runner.is_front_clear(),
                'on_key': self.runner.on_key(),
                'at_door': self.runner.at_door(),
                'at_exit': self.runner.at_exit()
            }
        
        # Restore original direction
        self.runner.direction = original_dir
        
        self.scan_results = scan_result
    
    def _execute_count(self):
        """Execute COUNT command - count items in current area."""
        # Count items in a 3x3 area around current position
        count = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                pos = (self.runner.x + dx, self.runner.y + dy)
                tile = self.runner.world.get(pos, 'void')
                if tile in ['key', 'door', 'exit']:
                    count += 1
        
        # Count is stored in scan_results for later use
    
    def _execute_save(self):
        """Execute SAVE command - save current state."""
        state = {
            'position': (self.runner.x, self.runner.y),
            'direction': self.runner.direction,
            'has_key': self.runner.has_key,
            'door_opened': self.runner.door_opened,
            'world': self.runner.world.copy(),
            'marks': self.marks.copy(),
            'flag': self.flag
        }
        self.saved_states.append(state)
    
    def _execute_load(self):
        """Execute LOAD command - restore saved state."""
        if not self.saved_states:
            return
        
        state = self.saved_states.pop()
        self.runner.x, self.runner.y = state['position']
        self.runner.direction = state['direction']
        self.runner.has_key = state['has_key']
        self.runner.door_opened = state['door_opened']
        self.runner.world = state['world'].copy()
        self.marks = state['marks'].copy()
        self.flag = state['flag']


class AdvancedVaultRunner(VaultRunner):
    """
    Extended VaultRunner with additional capabilities.
    
    New features:
    - Multiple keys support
    - Teleportation
    - Item inventory
    - Advanced sensors
    """
    
    def __init__(self, world_map=None, start_pos=(0, 0), start_dir=0, enable_extensions=True):
        super().__init__(world_map, start_pos, start_dir)
        self.enable_extensions = enable_extensions
        self.inventory = []  # Store collected items
        self.teleport_points = {}  # Store teleportation points
        self.energy = 100  # Energy system
        self.vision_range = 1  # How far the robot can see
        
        if enable_extensions:
            self._setup_extended_world()
    
    def _setup_extended_world(self):
        """Setup extended world features."""
        # Add teleportation points
        self.teleport_points = {
            'A': (0, 0),
            'B': (5, 5)
        }
    
    def teleport(self, point_name: str) -> bool:
        """Teleport to a named point."""
        if point_name in self.teleport_points:
            self.x, self.y = self.teleport_points[point_name]
            self.energy -= 10  # Teleportation costs energy
            return True
        return False
    
    def add_teleport_point(self, name: str, position: tuple):
        """Add a new teleportation point."""
        self.teleport_points[name] = position
    
    def get_vision(self) -> Dict:
        """Get vision information in all directions."""
        vision = {}
        directions = ['NORTH', 'EAST', 'SOUTH', 'WEST']
        
        original_dir = self.direction
        
        for i, direction in enumerate(directions):
            self.direction = i
            vision[direction] = []
            
            for distance in range(1, self.vision_range + 1):
                front_pos = self.get_front_position()
                tile = self.world.get(front_pos, 'void')
                vision[direction].append(tile)
        
        self.direction = original_dir
        return vision
    
    def use_energy(self, amount: int) -> bool:
        """Use energy for actions."""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False
    
    def recharge_energy(self, amount: int):
        """Recharge energy."""
        self.energy = min(100, self.energy + amount)


class LanguageExtensions:
    """
    Collection of language extensions and utilities.
    """
    
    @staticmethod
    def create_extended_world(size: int = 10) -> Dict:
        """Create an extended world with more features."""
        world = {}
        
        # Create a larger world
        for x in range(size):
            for y in range(size):
                world[(x, y)] = 'floor'
        
        # Add walls around the perimeter
        for x in range(-1, size + 1):
            world[(x, -1)] = 'wall'
            world[(x, size)] = 'wall'
        for y in range(-1, size + 1):
            world[(-1, y)] = 'wall'
            world[(size, y)] = 'wall'
        
        # Add some obstacles
        for i in range(3):
            x, y = random.randint(1, size-2), random.randint(1, size-2)
            world[(x, y)] = 'wall'
        
        # Add multiple keys
        for i in range(3):
            x, y = random.randint(1, size-2), random.randint(1, size-2)
            if world.get((x, y), 'wall') == 'floor':
                world[(x, y)] = 'key'
        
        # Add doors
        for i in range(2):
            x, y = random.randint(1, size-2), random.randint(1, size-2)
            if world.get((x, y), 'wall') == 'floor':
                world[(x, y)] = 'door'
        
        # Add exit
        x, y = random.randint(1, size-2), random.randint(1, size-2)
        if world.get((x, y), 'wall') == 'floor':
            world[(x, y)] = 'exit'
        
        return world
    
    @staticmethod
    def analyze_program_complexity(program_lines: List[str]) -> Dict:
        """Analyze program complexity with extended metrics."""
        try:
            interpreter = ExtendedVaultInterpreter(program_lines, enable_extensions=True)
            analysis = interpreter.analyze_program()
            
            # Add extended analysis
            extended_analysis = analysis.copy()
            extended_analysis['has_extensions'] = any(
                token in ['WAIT', 'MARK', 'GOTO', 'SCAN', 'COUNT', 'SAVE', 'LOAD']
                for token in interpreter.tokens
            )
            extended_analysis['extension_count'] = sum(
                1 for token in interpreter.tokens
                if token in ['WAIT', 'MARK', 'GOTO', 'SCAN', 'COUNT', 'SAVE', 'LOAD']
            )
            
            return extended_analysis
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def create_sample_extended_programs() -> Dict[str, List[str]]:
        """Create sample programs using extended features."""
        return {
            'teleport_explorer': [
                "MARK",
                "MOVE",
                "MOVE", 
                "IF KEY",
                "  PICK",
                "END",
                "GOTO",
                "IF DOOR",
                "  OPEN",
                "END"
            ],
            
            'scanner_bot': [
                "SCAN",
                "IF FRONT",
                "  MOVE",
                "END",
                "COUNT",
                "IF KEY",
                "  PICK",
                "END"
            ],
            
            'state_saver': [
                "SAVE",
                "MOVE",
                "MOVE",
                "IF KEY",
                "  PICK",
                "  SAVE",
                "END",
                "LOAD",
                "OPEN"
            ],
            
            'wait_and_see': [
                "WAIT 5",
                "MOVE",
                "WAIT 3",
                "IF KEY",
                "  PICK",
                "END"
            ]
        }


def demo_extensions():
    """Demonstrate the language extensions."""
    print("=" * 60)
    print("VAULT RUNNER LANGUAGE EXTENSIONS DEMO")
    print("=" * 60)
    
    # Create extended world
    world = LanguageExtensions.create_extended_world(8)
    runner = AdvancedVaultRunner(world, (0, 0), 1, enable_extensions=True)
    
    print("Extended world created:")
    runner.display_world()
    
    # Test extended programs
    sample_programs = LanguageExtensions.create_sample_extended_programs()
    
    for name, program in sample_programs.items():
        print(f"\n--- Testing {name} ---")
        try:
            interpreter = ExtendedVaultInterpreter(program, enable_extensions=True)
            result = interpreter.run(runner, show_steps=False)
            print(f"Result: {'SUCCESS' if result else 'COMPLETED'}")
            
            # Analyze with extensions
            analysis = LanguageExtensions.analyze_program_complexity(program)
            print(f"Has extensions: {analysis.get('has_extensions', False)}")
            print(f"Extension count: {analysis.get('extension_count', 0)}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        # Reset runner
        runner.reset()


if __name__ == "__main__":
    demo_extensions()
