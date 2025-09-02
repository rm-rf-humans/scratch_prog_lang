import time
import tracemalloc
import sys
import psutil
import os
import random

class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.peak_memory = 0
        self.initial_memory = 0
        self.instructions_executed = 0
        self.process = psutil.Process(os.getpid())
        
    def start_monitoring(self):
        tracemalloc.start()
        self.start_time = time.perf_counter()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024
        self.instructions_executed = 0
        
    def stop_monitoring(self):
        self.end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        self.peak_memory = peak / 1024 / 1024
        tracemalloc.stop()
        
    def get_metrics(self):
        execution_time = (self.end_time - self.start_time) * 1000
        final_memory = self.process.memory_info().rss / 1024 / 1024
        memory_delta = final_memory - self.initial_memory
        return {
            'execution_time_ms': round(execution_time, 3),
            'peak_memory_mb': round(self.peak_memory, 3),
            'memory_delta_mb': round(memory_delta, 3),
            'instructions_per_ms': round(self.instructions_executed / execution_time, 2) if execution_time > 0 else 0,
            'total_instructions': self.instructions_executed
        }

class VaultRunner:
    def __init__(self):
        self.x, self.y, self.dir = 0, 0, 0
        self.has_key = False
        self.door_open = False
        self.sensors = {'front_clear': True, 'on_key': False, 'at_door': False, 'at_exit': False}
        self.world = {}
        self.escaped = False
        
    def update_sensors(self):
        dx, dy = [(0, 1), (1, 0), (0, -1), (-1, 0)][self.dir]
        front_pos = (self.x + dx, self.y + dy)
        self.sensors['front_clear'] = self.world.get(front_pos, 'floor') != 'wall'
        curr_tile = self.world.get((self.x, self.y), 'floor')
        self.sensors['on_key'] = curr_tile == 'key'
        self.sensors['at_door'] = curr_tile == 'door'
        self.sensors['at_exit'] = curr_tile == 'exit'
        
    def execute_action(self, action):
        if action == 'MOVE' and self.sensors['front_clear']:
            dx, dy = [(0, 1), (1, 0), (0, -1), (-1, 0)][self.dir]
            self.x += dx
            self.y += dy
        elif action == 'LEFT':
            self.dir = (self.dir - 1) % 4
        elif action == 'RIGHT':
            self.dir = (self.dir + 1) % 4
        elif action == 'RTURN':
            self.dir = (self.dir + (1 if random.random() > 0.5 else -1)) % 4
        elif action == 'PICK' and self.sensors['on_key']:
            self.has_key = True
            self.world[(self.x, self.y)] = 'floor'
        elif action == 'OPEN' and self.sensors['at_door'] and self.has_key:
            self.door_open = True
        
        self.update_sensors()
        if self.sensors['at_exit'] or (self.sensors['at_door'] and self.door_open):
            self.escaped = True

class Interpreter:
    def __init__(self, program):
        self.program = [line.strip().upper() for line in program if line.strip()]
        self.tokens = self._tokenize()
        self.pc = 0
        self.stack = []
        self.flag = False
        self.runner = VaultRunner()
        self.monitor = PerformanceMonitor()
        
    def _tokenize(self):
        keywords = {'MOVE', 'LEFT', 'RIGHT', 'RTURN', 'PICK', 'OPEN', 'LOOP', 'END', 'IF', 'WHILE', 'SET', 'CLR', 'JMP'}
        sensors = {'FRONT', 'KEY', 'DOOR', 'EXIT'}
        tokens = []
        for line in self.program:
            parts = line.split()
            for part in parts:
                if part in keywords or part in sensors or part.isdigit():
                    tokens.append(part)
        return tokens
        
    def _find_matching_end(self, start_idx, start_kw, end_kw):
        level, i = 1, start_idx + 1
        while i < len(self.tokens) and level > 0:
            if self.tokens[i] == start_kw: level += 1
            elif self.tokens[i] == end_kw: level -= 1
            i += 1
        return i - 1 if level == 0 else -1
        
    def run(self):
        self.monitor.start_monitoring()
        while self.pc < len(self.tokens) and not self.runner.escaped:
            token = self.tokens[self.pc]
            self.monitor.instructions_executed += 1
            
            if token in ['MOVE', 'LEFT', 'RIGHT', 'RTURN', 'PICK', 'OPEN']:
                self.runner.execute_action(token)
                
            elif token == 'LOOP':
                count = int(self.tokens[self.pc + 1])
                end_pos = self._find_matching_end(self.pc, 'LOOP', 'END')
                self.stack.append((self.pc + 2, end_pos, count))
                self.pc += 1
                
            elif token == 'END':
                if self.stack:
                    start, end, count = self.stack[-1]
                    if count > 1:
                        self.stack[-1] = (start, end, count - 1)
                        self.pc = start - 1
                    else:
                        self.stack.pop()
                        
            elif token == 'WHILE':
                sensor = self.tokens[self.pc + 1]
                condition = getattr(self.runner.sensors, {'FRONT': 'front_clear', 'KEY': 'on_key', 'DOOR': 'at_door', 'EXIT': 'at_exit'}[sensor])
                if condition:
                    end_pos = self._find_matching_end(self.pc, 'WHILE', 'END')
                    self.stack.append((self.pc, end_pos, -1))
                    self.pc += 1
                else:
                    self.pc = self._find_matching_end(self.pc, 'WHILE', 'END')
                    
            elif token == 'IF':
                sensor = self.tokens[self.pc + 1]
                condition = getattr(self.runner.sensors, {'FRONT': 'front_clear', 'KEY': 'on_key', 'DOOR': 'at_door', 'EXIT': 'at_exit'}[sensor])
                if not condition:
                    self.pc = self._find_matching_end(self.pc, 'IF', 'END')
                else:
                    self.pc += 1
                    
            elif token == 'SET':
                self.flag = True
            elif token == 'CLR':
                self.flag = False
            elif token == 'JMP' and self.flag:
                self.pc = int(self.tokens[self.pc + 1]) - 1
                
            self.pc += 1
            
        self.monitor.stop_monitoring()
        return self.runner.escaped
        
    def get_performance_metrics(self):
        return self.monitor.get_metrics()
        
    def analyze_complexity(self):
        token_count = len(self.tokens)
        loop_depth = 0
        max_depth = 0
        control_structures = 0
        
        for token in self.tokens:
            if token in ['LOOP', 'WHILE', 'IF']:
                loop_depth += 1
                control_structures += 1
                max_depth = max(max_depth, loop_depth)
            elif token == 'END':
                loop_depth -= 1
                
        return {
            'token_count': token_count,
            'control_structures': control_structures,
            'max_nesting_depth': max_depth,
            'complexity_score': token_count + control_structures * 2 + max_depth * 3
        }

def benchmark_test(name, program, iterations=1000):
    total_time = 0
    total_memory = 0
    total_instructions = 0
    
    for _ in range(iterations):
        interpreter = Interpreter(program)
        result = interpreter.run()
        metrics = interpreter.get_performance_metrics()
        total_time += metrics['execution_time_ms']
        total_memory += metrics['peak_memory_mb']
        total_instructions += metrics['total_instructions']
    
    complexity = interpreter.analyze_complexity()
    
    print(f"\n=== {name} Benchmark ===")
    print(f"Iterations: {iterations}")
    print(f"Avg execution time: {total_time/iterations:.3f}ms")
    print(f"Avg peak memory: {total_memory/iterations:.3f}MB")
    print(f"Avg instructions: {total_instructions/iterations}")
    print(f"Token count: {complexity['token_count']}")
    print(f"Control structures: {complexity['control_structures']}")
    print(f"Max nesting depth: {complexity['max_nesting_depth']}")
    print(f"Complexity score: {complexity['complexity_score']}")
    print(f"Memory efficiency: {(total_instructions/iterations)/(total_memory/iterations):.2f} inst/MB")
    return total_time/iterations, total_memory/iterations

def test_corridor():
    program = [
        "WHILE FRONT", "MOVE", "END",
        "RIGHT", "WHILE FRONT", "MOVE", "END",
        "LEFT", "WHILE FRONT", "MOVE",
        "IF KEY", "PICK", "END",
        "IF DOOR", "OPEN", "END",
        "IF EXIT", "SET", "END",
        "END"
    ]
    interpreter = Interpreter(program)
    result = interpreter.run()
    metrics = interpreter.get_performance_metrics()
    complexity = interpreter.analyze_complexity()
    print(f"Corridor test: {result}")
    print(f"Performance: {metrics}")
    print(f"Complexity: {complexity}")
    return result

def test_room():
    program = [
        "LOOP 50",
        "IF FRONT", "MOVE", "END",
        "RIGHT",
        "IF KEY", "PICK", "END",
        "IF DOOR", "OPEN", "END",
        "END"
    ]
    interpreter = Interpreter(program)
    result = interpreter.run()
    metrics = interpreter.get_performance_metrics()
    complexity = interpreter.analyze_complexity()
    print(f"Room test: {result}")
    print(f"Performance: {metrics}")
    print(f"Complexity: {complexity}")
    return result

def test_syntax_error():
    program = ["INVALID_COMMAND"]
    try:
        interpreter = Interpreter(program)
        interpreter.run()
        return False
    except:
        return True

if __name__ == "__main__":
    print("=== Basic Tests ===")
    test_corridor()
    test_room() 
    print(f"Syntax error test: {test_syntax_error()}")
    
    corridor_program = ["WHILE FRONT", "MOVE", "END", "RIGHT", "WHILE FRONT", "MOVE", "END"]
    room_program = ["LOOP 50", "IF FRONT", "MOVE", "END", "RIGHT", "IF KEY", "PICK", "END", "END"]
    simple_program = ["MOVE", "LEFT", "MOVE", "RIGHT"]
    
    benchmark_test("Corridor Navigation", corridor_program, 100)
    benchmark_test("Room Exploration", room_program, 100)
    benchmark_test("Simple Movement", simple_program, 1000)
    
    print("\n=== Memory Footprint Analysis ===")
    interpreter = Interpreter(corridor_program)
    base_size = sys.getsizeof(interpreter)
    tokens_size = sys.getsizeof(interpreter.tokens) + sum(sys.getsizeof(t) for t in interpreter.tokens)
    runner_size = sys.getsizeof(interpreter.runner) + sys.getsizeof(interpreter.runner.sensors) + sys.getsizeof(interpreter.runner.world)
    
    print(f"Interpreter base size: {base_size} bytes")
    print(f"Tokens size: {tokens_size} bytes")  
    print(f"Runner state size: {runner_size} bytes")
    print(f"Total memory footprint: {base_size + tokens_size + runner_size} bytes")
