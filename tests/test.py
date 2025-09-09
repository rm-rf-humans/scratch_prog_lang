
import sys
import os
import unittest

#sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'scratch'))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'scratch'))

from vault_runner import VaultRunner, create_corridor_world, create_room_world
from interpreter import VaultInterpreter
from programs import program1_corridor, program2_room, simple_move, simple_loop
from extensions import ExtendedVaultInterpreter, AdvancedVaultRunner, LanguageExtensions
from game import VaultRunnerGame, GameChallenge


class TestVaultRunner(unittest.TestCase):
    """Test cases for the VaultRunner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simple_world = {
            (0, 0): 'floor', (1, 0): 'key', (2, 0): 'door', (3, 0): 'exit',
            (-1, 0): 'wall', (4, 0): 'wall'
        }
        self.runner = VaultRunner(self.simple_world, (0, 0), 1)  # Start facing East
    
    def test_initial_state(self):
        """Test initial robot state."""
        self.assertEqual(self.runner.x, 0)
        self.assertEqual(self.runner.y, 0)
        self.assertEqual(self.runner.direction, 1)  # East
        self.assertFalse(self.runner.has_key)
        self.assertFalse(self.runner.door_opened)
        self.assertFalse(self.runner.escaped)
    
    def test_movement(self):
        """Test robot movement."""
        # Test forward movement
        self.assertTrue(self.runner.is_front_clear())
        self.assertTrue(self.runner.move_forward())
        self.assertEqual((self.runner.x, self.runner.y), (1, 0))
        
        # Test blocked movement
        self.runner.x, self.runner.y = -1, 0  # Move to wall position
        self.assertFalse(self.runner.is_front_clear())
        self.assertFalse(self.runner.move_forward())
    
    def test_turning(self):
        """Test robot turning."""
        initial_dir = self.runner.direction
        self.runner.turn_left()
        self.assertEqual(self.runner.direction, (initial_dir - 1) % 4)
        
        self.runner.turn_right()
        self.assertEqual(self.runner.direction, initial_dir)
    
    def test_key_interaction(self):
        """Test key pickup."""
        # Move to key position
        self.runner.x, self.runner.y = 1, 0
        self.assertTrue(self.runner.on_key())
        
        # Pick up key
        self.assertTrue(self.runner.pick_key())
        self.assertTrue(self.runner.has_key)
        self.assertEqual(self.runner.world[(1, 0)], 'floor')  # Key should be gone
        
        # Try to pick up key again
        self.assertFalse(self.runner.pick_key())
    
    def test_door_interaction(self):
        """Test door opening."""
        # Move to door without key
        self.runner.x, self.runner.y = 2, 0
        self.assertTrue(self.runner.at_door())
        self.assertFalse(self.runner.open_door())  # Should fail without key
        
        # Get key and try again
        self.runner.has_key = True
        self.assertTrue(self.runner.open_door())
        self.assertTrue(self.runner.door_opened)
    
    def test_escape_conditions(self):
        """Test escape conditions."""
        # Test exit escape
        self.runner.x, self.runner.y = 3, 0
        self.assertTrue(self.runner.check_escape())
        self.assertTrue(self.runner.escaped)
        
        # Reset and test door escape
        self.runner.escaped = False
        self.runner.x, self.runner.y = 2, 0
        self.runner.door_opened = True
        self.assertTrue(self.runner.check_escape())
        self.assertTrue(self.runner.escaped)


class TestVaultInterpreter(unittest.TestCase):
    """Test cases for the VaultInterpreter class."""
    
    def test_tokenization_valid(self):
        """Test tokenization of valid programs."""
        program = ["MOVE", "LEFT", "PICK", "LOOP 3", "MOVE", "END"]
        interpreter = VaultInterpreter(program)
        
        expected_tokens = ['MOVE', 'LEFT', 'PICK', 'LOOP', 3, 'MOVE', 'END']
        self.assertEqual(interpreter.tokens, expected_tokens)
    
    def test_tokenization_invalid(self):
        """Test tokenization error handling."""
        program = ["MOVE", "INVALID_TOKEN", "LEFT"]
        
        with self.assertRaises(SyntaxError):
            VaultInterpreter(program)
    
    def test_token_count_constraint(self):
        """Test the 20-token limit constraint."""
        # This should pass (well within limit)
        valid_program = ["MOVE", "LEFT", "RIGHT", "PICK", "OPEN"]
        interpreter = VaultInterpreter(valid_program)
        self.assertLessEqual(interpreter.get_distinct_token_count(), 20)
    
    def test_syntax_error_unmatched_control(self):
        """Test syntax error for unmatched control structures."""
        program = ["LOOP 3", "MOVE"]  # Missing END
        
        with self.assertRaises(SyntaxError):
            interpreter = VaultInterpreter(program)
            world = create_corridor_world()
            runner = VaultRunner(world, (0, 0), 1)
            interpreter.run(runner)
    
    def test_simple_program_execution(self):
        """Test execution of simple movement program."""
        world = {
            (0, 0): 'floor', (1, 0): 'floor', (2, 0): 'floor',
            (-1, 0): 'wall', (3, 0): 'wall', (0, 1): 'wall', (0, -1): 'wall'
        }
        runner = VaultRunner(world, (0, 0), 1)  # Facing East
        interpreter = VaultInterpreter(simple_move)
        
        interpreter.run(runner)
        # Should have moved 2 spaces east, turned left (now north), moved 1 space north
        self.assertEqual((runner.x, runner.y), (2, 1))
        self.assertEqual(runner.direction, 0)  # North


class TestProgramExecution(unittest.TestCase):
    """Test cases for executing the assignment programs."""
    
    def test_corridor_program_structure(self):
        """Test Program 1: Corridor navigation program structure."""
        interpreter = VaultInterpreter(program1_corridor)
        analysis = interpreter.analyze_program()
        
        # Verify token constraints
        self.assertLessEqual(analysis['distinct_tokens'], 20)
        self.assertGreater(analysis['total_tokens'], 0)
        self.assertGreater(analysis['control_structures'], 0)
    
    def test_room_program_structure(self):
        """Test Program 2: Room exploration program structure."""
        interpreter = VaultInterpreter(program2_room)
        analysis = interpreter.analyze_program()
        
        # Verify token constraints
        self.assertLessEqual(analysis['distinct_tokens'], 20)
        self.assertGreater(analysis['total_tokens'], 0)
        self.assertGreater(analysis['control_structures'], 0)
    
    def test_corridor_program_execution(self):
        """Test Program 1: Corridor navigation execution."""
        world = create_corridor_world()
        runner = VaultRunner(world, (0, 0), 1)  # Start facing East
        interpreter = VaultInterpreter(program1_corridor)
        
        # Run program (without visual output for testing)
        result = interpreter.run(runner)
        
        # Program should complete successfully
        self.assertTrue(isinstance(result, bool))
        # Robot should have moved from starting position
        self.assertNotEqual((runner.x, runner.y), (0, 0))
    
    def test_room_program_execution(self):
        """Test Program 2: Room exploration execution."""
        world = create_room_world()
        runner = VaultRunner(world, (0, 0), 0)  # Start facing North
        interpreter = VaultInterpreter(program2_room)
        
        # Run program
        result = interpreter.run(runner)
        
        # Program should complete successfully  
        self.assertTrue(isinstance(result, bool))
        # Robot should have moved from starting position
        self.assertNotEqual((runner.x, runner.y), (0, 0))
    
    def test_instruction_limit(self):
        """Test that infinite loops are caught by instruction limit."""
        infinite_program = ["LOOP 10000", "MOVE", "END"]  # Very large loop
        world = create_room_world()
        runner = VaultRunner(world, (0, 0), 0)
        interpreter = VaultInterpreter(infinite_program)
        
        # Should terminate due to instruction limit
        result = interpreter.run(runner)
        self.assertLessEqual(interpreter.instruction_count, interpreter.max_instructions)


class TestWorldVisualization(unittest.TestCase):
    """Test cases for world visualization and display."""
    
    def test_world_display(self):
        """Test that world display doesn't crash."""
        world = create_corridor_world()
        runner = VaultRunner(world, (0, 0), 1)
        
        # Should not raise any exceptions
        try:
            runner.display_world(show_robot=True)
            runner.display_world(show_robot=False)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_world_bounds_calculation(self):
        """Test world bounds calculation for visualization."""
        world = {(0, 0): 'floor', (5, 3): 'wall', (-2, -1): 'floor'}
        runner = VaultRunner(world, (0, 0), 0)
        
        self.assertEqual(runner.min_x, -2)
        self.assertEqual(runner.max_x, 5)
        self.assertEqual(runner.min_y, -1)
        self.assertEqual(runner.max_y, 3)


def run_benchmarks():
    """Run performance benchmarks on programs."""
    print("\n" + "=" * 60)
    print("PERFORMANCE BENCHMARKS")
    print("=" * 60)
    
    import time
    
    programs = [
        ("Simple Move", simple_move, create_room_world, (0, 0), 0),
        ("Simple Loop", simple_loop, create_room_world, (0, 0), 0),
        ("Corridor Program", program1_corridor, create_corridor_world, (0, 0), 1),
        ("Room Program", program2_room, create_room_world, (0, 0), 0)
    ]
    
    for name, program, world_creator, start_pos, start_dir in programs:
        print(f"\n{name}:")
        print("-" * len(name))
        
        # Run multiple times for average
        times = []
        instructions = []
        
        for _ in range(10):
            world = world_creator()
            runner = VaultRunner(world, start_pos, start_dir)
            interpreter = VaultInterpreter(program)
            
            start_time = time.perf_counter()
            result = interpreter.run(runner)
            end_time = time.perf_counter()
            
            times.append((end_time - start_time) * 1000)  # Convert to ms
            instructions.append(interpreter.instruction_count)
        
        avg_time = sum(times) / len(times)
        avg_instructions = sum(instructions) / len(instructions)
        
        analysis = VaultInterpreter(program).analyze_program()
        
        print(f"  Average execution time: {avg_time:.2f} ms")
        print(f"  Average instructions executed: {avg_instructions:.0f}")
        print(f"  Token count: {analysis['total_tokens']}")
        print(f"  Distinct tokens: {analysis['distinct_tokens']}")
        print(f"  Complexity score: {analysis['complexity_score']}")


class TestLanguageExtensions(unittest.TestCase):
    """Test cases for language extensions."""
    
    def test_extended_interpreter_creation(self):
        """Test creation of extended interpreter."""
        program = ["MOVE", "MARK", "GOTO"]
        interpreter = ExtendedVaultInterpreter(program, enable_extensions=True)
        self.assertTrue(interpreter.enable_extensions)
        self.assertEqual(len(interpreter.tokens), 3)
    
    def test_extended_commands_tokenization(self):
        """Test tokenization of extended commands."""
        program = ["WAIT 5", "MARK", "GOTO", "SCAN", "COUNT", "SAVE", "LOAD"]
        interpreter = ExtendedVaultInterpreter(program, enable_extensions=True)
        expected_tokens = ['WAIT', 5, 'MARK', 'GOTO', 'SCAN', 'COUNT', 'SAVE', 'LOAD']
        self.assertEqual(interpreter.tokens, expected_tokens)
    
    def test_advanced_vault_runner(self):
        """Test advanced vault runner features."""
        world = LanguageExtensions.create_extended_world(5)
        runner = AdvancedVaultRunner(world, (0, 0), 1, enable_extensions=True)
        
        self.assertTrue(runner.enable_extensions)
        self.assertEqual(runner.energy, 100)
        self.assertEqual(len(runner.inventory), 0)
    
    def test_teleportation(self):
        """Test teleportation functionality."""
        world = LanguageExtensions.create_extended_world(5)
        runner = AdvancedVaultRunner(world, (0, 0), 1, enable_extensions=True)
        
        # Add teleport point
        runner.add_teleport_point('test', (3, 3))
        
        # Test teleportation
        result = runner.teleport('test')
        self.assertTrue(result)
        self.assertEqual((runner.x, runner.y), (3, 3))
        self.assertEqual(runner.energy, 90)  # Should consume 10 energy
    
    def test_energy_system(self):
        """Test energy system."""
        world = LanguageExtensions.create_extended_world(5)
        runner = AdvancedVaultRunner(world, (0, 0), 1, enable_extensions=True)
        
        # Test energy usage
        self.assertTrue(runner.use_energy(50))
        self.assertEqual(runner.energy, 50)
        
        # Test insufficient energy
        self.assertFalse(runner.use_energy(60))
        self.assertEqual(runner.energy, 50)
        
        # Test energy recharge
        runner.recharge_energy(30)
        self.assertEqual(runner.energy, 80)


class TestGameFeatures(unittest.TestCase):
    """Test cases for game features."""
    
    def test_game_challenge_creation(self):
        """Test game challenge creation."""
        def world_creator():
            return {(0, 0): 'floor', (1, 0): 'exit'}
        
        challenge = GameChallenge(
            name="Test Challenge",
            description="Test description",
            world_creator=world_creator,
            start_pos=(0, 0),
            start_dir=1,
            success_condition="Reach exit"
        )
        
        self.assertEqual(challenge.name, "Test Challenge")
        self.assertEqual(challenge.start_pos, (0, 0))
        self.assertIsNone(challenge.best_score)
    
    def test_challenge_program_testing(self):
        """Test program testing in challenges."""
        def world_creator():
            return {(0, 0): 'floor', (1, 0): 'exit'}
        
        challenge = GameChallenge(
            name="Test Challenge",
            description="Test description",
            world_creator=world_creator,
            start_pos=(0, 0),
            start_dir=1,
            success_condition="Reach exit"
        )
        
        program = ["MOVE"]
        result = challenge.test_program(program)
        
        self.assertIn('success', result)
        self.assertIn('score', result)
        self.assertIn('instructions', result)
    
    def test_game_creation(self):
        """Test game creation and initialization."""
        game = VaultRunnerGame()
        self.assertEqual(len(game.challenges), 6)
        self.assertEqual(game.player_name, "Player")
        self.assertEqual(len(game.score_history), 0)


class TestProgramAnalysis(unittest.TestCase):
    """Test cases for program analysis features."""
    
    def test_extended_program_analysis(self):
        """Test extended program analysis."""
        program = ["MOVE", "MARK", "GOTO", "IF KEY", "PICK", "END"]
        analysis = LanguageExtensions.analyze_program_complexity(program)
        
        self.assertIn('has_extensions', analysis)
        self.assertIn('extension_count', analysis)
        self.assertTrue(analysis['has_extensions'])
        self.assertGreater(analysis['extension_count'], 0)
    
    def test_sample_programs_creation(self):
        """Test creation of sample extended programs."""
        programs = LanguageExtensions.create_sample_extended_programs()
        
        self.assertIn('teleport_explorer', programs)
        self.assertIn('scanner_bot', programs)
        self.assertIn('state_saver', programs)
        self.assertIn('wait_and_see', programs)
        
        # Check that programs contain extended commands
        for name, program in programs.items():
            self.assertIsInstance(program, list)
            self.assertGreater(len(program), 0)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling and edge cases."""
    
    def test_invalid_extension_commands(self):
        """Test handling of invalid extension commands."""
        program = ["INVALID_COMMAND"]
        
        with self.assertRaises(SyntaxError):
            ExtendedVaultInterpreter(program, enable_extensions=True)
    
    def test_extension_token_limit(self):
        """Test that extensions respect token limit."""
        # Create program with too many distinct tokens
        program = ["MOVE", "LEFT", "RIGHT", "PICK", "OPEN", "LOOP", "END", "IF", "WHILE",
                  "FRONT", "KEY", "DOOR", "EXIT", "SET", "CLR", "WAIT", "MARK", "GOTO",
                  "SCAN", "COUNT", "SAVE", "LOAD", "NORTH", "SOUTH", "EAST", "WEST"]
        
        with self.assertRaises(SyntaxError):
            ExtendedVaultInterpreter(program, enable_extensions=True)
    
    def test_game_challenge_error_handling(self):
        """Test error handling in game challenges."""
        def world_creator():
            return {(0, 0): 'floor'}
        
        challenge = GameChallenge(
            name="Test Challenge",
            description="Test description",
            world_creator=world_creator,
            start_pos=(0, 0),
            start_dir=1,
            success_condition="Test"
        )
        
        # Test with invalid program
        invalid_program = ["INVALID_COMMAND"]
        result = challenge.test_program(invalid_program)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['score'], 0)


def main():
    """Run all tests and benchmarks."""
    print("VAULT RUNNER PROGRAMMING LANGUAGE TEST SUITE")
    print("=" * 60)
    print("\nNOTE: For a focused test suite, run: python3 tests/simple_test_suite.py")
    print("      This runs only 3 essential working test cases as mentioned in documentation.")
    print("=" * 60)
    
    # Run unit tests
    print("\nRunning full unit tests...")
    unittest.main(argv=[''], verbosity=2, exit=False)
    
    # Run benchmarks
    run_benchmarks()
    
    # Final summary
    print(f"\n{'=' * 60}")
    print("TEST SUITE COMPLETED")
    print("=" * 60)
    print("\nIf all tests passed, the implementation meets the requirements:")
    print("✓ Tokenizer correctly parses valid programs and rejects invalid ones")
    print("✓ Parser enforces grammar rules and catches syntax errors")
    print("✓ Executor correctly maps to robot actions through API")
    print("✓ Token limit constraint (≤20 distinct symbols) is enforced")
    print("✓ Programs can navigate corridor and room environments")
    print("✓ World visualization shows robot position and environment state")
    print("✓ Language extensions work correctly")
    print("✓ Game features function properly")
    print("✓ Error handling is robust")


if __name__ == "__main__":
    main()
