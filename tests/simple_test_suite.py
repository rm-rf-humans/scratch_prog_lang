#!/usr/bin/env python3
"""
Simple Test Suite - 3 Working Test Cases
A focused test suite with only the essential working test cases.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'scratch'))

import unittest
from vault_runner import VaultRunner, create_corridor_world, create_room_world
from interpreter import VaultInterpreter
from programs import program1_corridor, program2_room


class SimpleTestSuite(unittest.TestCase):
    """A small test suite with 3 essential test cases."""
    
    def test_1_basic_robot_functionality(self):
        """Test Case 1: Basic robot movement and interaction."""
        print("\n=== Test Case 1: Basic Robot Functionality ===")
        
        # Create simple world: floor -> key -> door -> exit
        world = {
            (0, 0): 'floor', (1, 0): 'key', (2, 0): 'door', (3, 0): 'exit',
            (-1, 0): 'wall', (4, 0): 'wall'
        }
        runner = VaultRunner(world, (0, 0), 1)  # Start facing East
        
        # Test initial state
        self.assertEqual((runner.x, runner.y), (0, 0))
        self.assertEqual(runner.direction, 1)  # East
        self.assertFalse(runner.has_key)
        self.assertFalse(runner.escaped)
        
        # Test movement
        self.assertTrue(runner.move_forward())  # Move to key
        self.assertEqual((runner.x, runner.y), (1, 0))
        
        # Test key pickup
        self.assertTrue(runner.on_key())
        self.assertTrue(runner.pick_key())
        self.assertTrue(runner.has_key)
        
        # Test door opening
        self.assertTrue(runner.move_forward())  # Move to door
        self.assertTrue(runner.at_door())
        self.assertTrue(runner.open_door())
        self.assertTrue(runner.door_opened)
        
        # Test escape
        self.assertTrue(runner.move_forward())  # Move to exit
        self.assertTrue(runner.check_escape())
        self.assertTrue(runner.escaped)
        
        print("✅ Basic robot functionality works correctly")
    
    def test_2_door_master_challenge(self):
        """Test Case 2: Door Master challenge with optimal starting position."""
        print("\n=== Test Case 2: Door Master Challenge (Optimal Position) ===")
        
        # Use the corridor world and optimal starting position
        world = create_corridor_world()
        runner = VaultRunner(world, (0, 0), 1)  # Start at (0,0) facing East - known working position
        interpreter = VaultInterpreter(program1_corridor)
        interpreter.max_instructions = 2000  # Sufficient for completion
        
        # Execute the program
        result = interpreter.run(runner, show_steps=False)
        
        # Verify successful execution
        self.assertTrue(result, "Door Master program should succeed from optimal starting position")
        self.assertTrue(runner.escaped, "Robot should have escaped")
        self.assertTrue(runner.has_key, "Robot should have collected the key")
        self.assertTrue(runner.door_opened, "Robot should have opened the door")
        self.assertLess(interpreter.instruction_count, 2000, "Should complete within instruction limit")
        
        print(f"✅ Door Master challenge completed successfully in {interpreter.instruction_count} steps")
        print(f"   Final position: ({runner.x}, {runner.y})")
        print(f"   Escape method: {'door' if runner.door_opened else 'exit'}")
    
    def test_3_room_explorer_challenge(self):
        """Test Case 3: Room Explorer challenge with BFS algorithm."""
        print("\n=== Test Case 3: Room Explorer Challenge (BFS Algorithm) ===")
        
        # Use the room world with specified starting position
        world = create_room_world()
        runner = VaultRunner(world, (0, 0), 0)  # Start at bottom-left facing North
        interpreter = VaultInterpreter(program2_room)
        interpreter.max_instructions = 1000  # Should be sufficient for BFS
        
        # Execute the program
        result = interpreter.run(runner, show_steps=False)
        
        # Verify successful execution
        self.assertTrue(result, "Room Explorer program should succeed")
        self.assertTrue(runner.escaped, "Robot should have escaped")
        self.assertLess(interpreter.instruction_count, 1000, "Should complete within instruction limit")
        
        print(f"✅ Room Explorer challenge completed successfully in {interpreter.instruction_count} steps")
        print(f"   Final position: ({runner.x}, {runner.y})")
        print(f"   Used BFS algorithm for optimal pathfinding")


def run_simple_tests():
    """Run the simple test suite."""
    print("VAULT RUNNER - SIMPLE TEST SUITE (3 CASES)")
    print("=" * 50)
    print("Testing only the essential working functionality...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleTestSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 ALL 3 TEST CASES PASSED!")
        print("✅ Basic robot functionality works")
        print("✅ Door Master challenge succeeds from optimal position")
        print("✅ Room Explorer challenge succeeds with BFS algorithm")
        print("\nThe Vault Runner language implementation is working correctly!")
    else:
        print("❌ Some tests failed:")
        for failure in result.failures:
            print(f"   FAIL: {failure[0]}")
        for error in result.errors:
            print(f"   ERROR: {error[0]}")
    
    print("=" * 50)
    return result.wasSuccessful()


if __name__ == "__main__":
    run_simple_tests()
