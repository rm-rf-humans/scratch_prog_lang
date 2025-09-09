class VaultInterpreter:
    """
    Interpreter for the Vault Runner programming language.
    
    This interpreter executes programs written in a simple language designed
    to control a robot in a 2D-vault environment. The language supports
    movement, sensing, control flow, and state management within strict
    constraints (max 20 distinct tokens).
    """
    
    def __init__(self, program_lines):
        """
        Initialize the interpreter with a program.
        
        Args:
            program_lines: List of strings representing the program code
        """
        self.program = [line.strip().upper() for line in program_lines if line.strip()]
        self.tokens = self._tokenize()
        self.pc = 0  # Program counter
        self.call_stack = []  # For loops and control structures
        self.flag = False  # Single accumulator/flag as per constraints
        self.runner = None
        self.max_instructions = 10000  # Safety limit
        self.instruction_count = 0
        self.debug_mode = False
        self.execution_history = []  # Track execution for debugging
    
    def _tokenize(self):
        """Convert program lines into tokens."""
        valid_keywords = {
            # Actions (6)
            'MOVE', 'LEFT', 'RIGHT', 'RTURN', 'PICK', 'OPEN',
            # Control structures (4) 
            'LOOP', 'END', 'IF', 'WHILE',
            # Sensors (4)
            'FRONT', 'KEY', 'DOOR', 'EXIT',
            # State management (2)
            'SET', 'CLR'
        }
        
        tokens = []
        line_num = 0
        
        for line in self.program:
            line_num += 1
            # Handle indentation by removing it
            line = line.strip()
            if not line:
                continue
            
            # Handle comments - ignore everything after #
            if '#' in line:
                line = line.split('#')[0].strip()
                if not line:  # If entire line was a comment, skip it
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
    
    def _find_matching_end(self, start_pc):
        """Find the matching END for a control structure."""
        level = 1
        pc = start_pc + 1
        start_token = self.tokens[start_pc]
        
        while pc < len(self.tokens) and level > 0:
            token = self.tokens[pc]
            if token in ['LOOP', 'IF', 'WHILE']:
                level += 1
            elif token == 'END':
                level -= 1
            pc += 1
        
        if level != 0:
            raise SyntaxError(f"Unmatched {start_token} - missing END")
        
        return pc - 1
    
    def _evaluate_sensor(self, sensor_token):
        """Evaluate sensor conditions."""
        if sensor_token == 'FRONT':
            return self.runner.is_front_clear()
        elif sensor_token == 'KEY':
            return self.runner.on_key()
        elif sensor_token == 'DOOR':
            return self.runner.at_door()
        elif sensor_token == 'EXIT':
            return self.runner.at_exit()
        else:
            raise RuntimeError(f"Unknown sensor: {sensor_token}")
    
    def set_debug_mode(self, enabled=True):
        """Enable or disable debug output."""
        self.debug_mode = enabled
    
    def run(self, runner, show_steps=False):
        """
        Execute the program with the given robot.
        
        Args:
            runner: VaultRunner instance to control
            show_steps: Whether to display world state after each step
            
        Returns:
            bool: True if robot escaped, False otherwise
        """
        self.runner = runner
        self.pc = 0
        self.call_stack = []
        self.flag = False
        self.instruction_count = 0
        self.execution_history = []
        
        print("=== Starting program execution ===")
        if show_steps:
            self.runner.display_world()
        
        try:
            while self.pc < len(self.tokens) and not self.runner.escaped:
                if self.instruction_count >= self.max_instructions:
                    print(f"Program terminated - exceeded maximum instructions ({self.max_instructions})")
                    break
                
                self.instruction_count += 1
                token = self.tokens[self.pc]
                
                # Record execution step for debugging
                step_info = {
                    'pc': self.pc,
                    'token': token,
                    'position': (self.runner.x, self.runner.y),
                    'direction': self.runner.direction,
                    'has_key': self.runner.has_key,
                    'door_opened': self.runner.door_opened
                }
                self.execution_history.append(step_info)
                
                if self.debug_mode:
                    print(f"PC: {self.pc:3d}, Token: {token:6s}, Pos: ({self.runner.x}, {self.runner.y}), Dir: {self.runner.direction}")
                
                # Execute the current instruction
                self._execute_instruction(token, show_steps)
                
                self.pc += 1
                self.runner.check_escape()
                
        except Exception as e:
            print(f"Execution error at PC {self.pc}: {e}")
            if self.debug_mode:
                print("Execution history:")
                for i, step in enumerate(self.execution_history[-5:]):  # Show last 5 steps
                    print(f"  Step {i}: {step}")
            raise
        
        print(f"\n=== Program execution completed ===")
        print(f"Instructions executed: {self.instruction_count}")
        print(f"Robot escaped: {self.runner.escaped}")
        print(f"Robot has key: {self.runner.has_key}")
        print(f"Door opened: {self.runner.door_opened}")
        print(f"Final position: ({self.runner.x}, {self.runner.y})")
        
        if show_steps:
            print("\nFinal world state:")
            self.runner.display_world()
        
        return self.runner.escaped
    
    def _execute_instruction(self, token, show_steps):
        """Execute a single instruction."""
        # Action commands
        if token == 'MOVE':
            old_pos = (self.runner.x, self.runner.y)
            self.runner.move_forward()
            if show_steps and (self.runner.x, self.runner.y) != old_pos:
                self.runner.display_world()
                
        elif token == 'LEFT':
            self.runner.turn_left()
            
        elif token == 'RIGHT':
            self.runner.turn_right()
            
        elif token == 'RTURN':
            self.runner.random_turn()
            
        elif token == 'PICK':
            had_key = self.runner.has_key
            # Check if this is the extension challenge
            if hasattr(self.runner, 'correct_key_pos'):
                self.runner.pick_key_extension(self.runner.correct_key_pos)
            else:
                self.runner.pick_key()
            if show_steps and not had_key and self.runner.has_key:
                print("Key collected!")
                self.runner.display_world()
            
        elif token == 'OPEN':
            was_opened = self.runner.door_opened
            self.runner.open_door()
            if show_steps and not was_opened and self.runner.door_opened:
                print("Door opened!")
                self.runner.display_world()
        
        # Control structures
        elif token == 'LOOP':
            count = self.tokens[self.pc + 1]
            end_pc = self._find_matching_end(self.pc)
            self.call_stack.append(('LOOP', self.pc + 2, end_pc, count))
            self.pc += 1  # Skip the count
            
        elif token == 'WHILE':
            sensor = self.tokens[self.pc + 1]
            condition = self._evaluate_sensor(sensor)
            end_pc = self._find_matching_end(self.pc)
            
            if condition:
                self.call_stack.append(('WHILE', self.pc, end_pc, sensor))
                self.pc += 1  # Skip the sensor
            else:
                self.pc = end_pc
                
        elif token == 'IF':
            sensor = self.tokens[self.pc + 1]
            condition = self._evaluate_sensor(sensor)
            end_pc = self._find_matching_end(self.pc)
            
            if condition:
                self.pc += 1  # Skip the sensor, continue with IF body
            else:
                self.pc = end_pc  # Skip to END
                
        elif token == 'END':
            if self.call_stack:
                structure_type, start_pc, end_pc, data = self.call_stack[-1]
                
                if structure_type == 'LOOP':
                    count = data - 1
                    if count > 0:
                        self.call_stack[-1] = ('LOOP', start_pc, end_pc, count)
                        self.pc = start_pc - 1
                    else:
                        self.call_stack.pop()
                        
                elif structure_type == 'WHILE':
                    sensor = data
                    condition = self._evaluate_sensor(sensor)
                    if condition:
                        self.pc = start_pc
                    else:
                        self.call_stack.pop()
                
                else:  # IF
                    self.call_stack.pop()
        
        # Flag operations
        elif token == 'SET':
            self.flag = True
            
        elif token == 'CLR':
            self.flag = False

        elif token in ['FRONT', 'KEY', 'DOOR', 'EXIT']:
            # Skip sensor tokens when they appear after control structures
            if not self.call_stack or self.call_stack[-1][0] not in ['IF', 'WHILE']:
                raise RuntimeError(f"Sensor '{token}' can only be used with IF or WHILE")

        else:
            if not isinstance(token, int):  # Skip numbers that are parameters
                raise RuntimeError(f"Unknown command: {token}")
    
    def get_token_count(self):
        """Return the total number of tokens in the program."""
        return len(self.tokens)
    
    def get_distinct_token_count(self):
        """Return the number of distinct tokens used."""
        return len(set(str(token) for token in self.tokens if isinstance(token, str)))
    
    def analyze_program(self):
        """Analyze program structure and complexity."""
        token_count = len(self.tokens)
        distinct_tokens = set(str(token) for token in self.tokens if isinstance(token, str))
        
        # Count control structures
        control_count = sum(1 for token in self.tokens if token in ['LOOP', 'IF', 'WHILE'])
        
        # Calculate maximum nesting depth
        depth = 0
        max_depth = 0
        for token in self.tokens:
            if token in ['LOOP', 'IF', 'WHILE']:
                depth += 1
                max_depth = max(max_depth, depth)
            elif token == 'END':
                depth -= 1
        
        return {
            'total_tokens': token_count,
            'distinct_tokens': len(distinct_tokens),
            'distinct_token_list': sorted(distinct_tokens),
            'control_structures': control_count,
            'max_nesting_depth': max_depth,
            'complexity_score': token_count + control_count * 2 + max_depth * 3
        }


if __name__ == "__main__":
    # Test the interpreter with a simple program
    test_program = [
        "MOVE",
        "MOVE", 
        "LEFT",
        "MOVE"
    ]
    
    from vault_runner import VaultRunner, create_corridor_world
    
    # Create interpreter and runner
    interpreter = VaultInterpreter(test_program)
    world = create_corridor_world()
    runner = VaultRunner(world, (0, 0), 1)  # Start facing East
    
    # Analyze program
    analysis = interpreter.analyze_program()
    print("=== Program Analysis ===")
    for key, value in analysis.items():
        print(f"{key}: {value}")
    
    # Run program with visualization
    interpreter.set_debug_mode(True)
    result = interpreter.run(runner, show_steps=True)
    print(f"\nProgram result: {result}")
