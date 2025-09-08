"""
Vault Runner Game - An interactive game using the Vault Runner programming language.

This module provides a game interface where players can:
1. Write programs in the Vault Runner language
2. Test their programs in different scenarios
3. Compete in challenges
4. Learn programming concepts through gameplay
"""

import random
import time
from typing import List, Dict, Tuple, Optional
from interpreter import VaultInterpreter
from vault_runner import VaultRunner, create_corridor_world, create_room_world, create_multi_key_world


class GameChallenge:
    """Represents a single challenge in the game."""
    
    def __init__(self, name: str, description: str, world_creator, start_pos: Tuple[int, int], 
                 start_dir: int, success_condition: str, max_instructions: int = 1000):
        self.name = name
        self.description = description
        self.world_creator = world_creator
        self.start_pos = start_pos
        self.start_dir = start_dir
        self.success_condition = success_condition
        self.max_instructions = max_instructions
        self.best_score = None
        self.best_program = None
    
    def test_program(self, program_lines: List[str]) -> Dict:
        """Test a program against this challenge."""
        try:
            interpreter = VaultInterpreter(program_lines)
            interpreter.max_instructions = self.max_instructions
            
            world = self.world_creator()
            runner = VaultRunner(world, self.start_pos, self.start_dir)
            
            start_time = time.time()
            result = interpreter.run(runner, show_steps=False)
            end_time = time.time()
            
            score = self._calculate_score(interpreter, runner, end_time - start_time)
            
            return {
                'success': result,
                'score': score,
                'instructions': interpreter.instruction_count,
                'time': end_time - start_time,
                'final_position': (runner.x, runner.y),
                'has_key': runner.has_key,
                'door_opened': runner.door_opened,
                'analysis': interpreter.analyze_program()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'score': 0
            }
    
    def _calculate_score(self, interpreter: VaultInterpreter, runner: VaultRunner, execution_time: float) -> int:
        """Calculate score based on various factors."""
        base_score = 100 if runner.escaped else 0
        
        # Bonus for efficiency (fewer instructions)
        instruction_bonus = max(0, 50 - interpreter.instruction_count)
        
        # Bonus for simplicity (fewer distinct tokens)
        token_bonus = max(0, 20 - interpreter.get_distinct_token_count())
        
        # Penalty for slow execution
        time_penalty = max(0, int(execution_time * 10))
        
        return base_score + instruction_bonus + token_bonus - time_penalty


class VaultRunnerGame:
    """Main game class for the Vault Runner programming game."""
    
    def __init__(self):
        self.challenges = self._create_challenges()
        self.player_name = "Player"
        self.current_challenge = None
        self.score_history = []
    
    def _create_challenges(self) -> List[GameChallenge]:
        """Create the game challenges."""
        challenges = [
            GameChallenge(
                name="First Steps",
                description="Move forward 3 steps and turn around. Learn basic movement!",
                world_creator=lambda: self._create_simple_corridor(),
                start_pos=(0, 0),
                start_dir=1,  # East
                success_condition="Reach the end of the corridor",
                max_instructions=50
            ),
            
            GameChallenge(
                name="Key Collector",
                description="Find and collect the key in the room. Watch out for walls!",
                world_creator=lambda: self._create_key_room(),
                start_pos=(0, 0),
                start_dir=0,  # North
                success_condition="Collect the key",
                max_instructions=200
            ),
            
            GameChallenge(
                name="Door Master",
                description="Collect the key and open the door to escape!",
                world_creator=create_corridor_world,
                start_pos=(0, 0),
                start_dir=1,  # East
                success_condition="Escape through the door",
                max_instructions=500
            ),
            
            GameChallenge(
                name="Room Explorer",
                description="Navigate the entire room and find the exit. Use loops efficiently!",
                world_creator=create_room_world,
                start_pos=(0, 0),
                start_dir=0,  # North
                success_condition="Find and reach the exit",
                max_instructions=1000
            ),
            
            GameChallenge(
                name="Multi-Key Mystery",
                description="Multiple keys exist, but only one opens the door. Find the right one!",
                world_creator=create_multi_key_world,
                start_pos=(4, 3),
                start_dir=0,  # North
                success_condition="Escape using the correct key",
                max_instructions=2000
            ),
            
            GameChallenge(
                name="Speed Run",
                description="Escape as quickly as possible! Efficiency is key.",
                world_creator=create_corridor_world,
                start_pos=(0, 0),
                start_dir=1,  # East
                success_condition="Escape in minimum instructions",
                max_instructions=100
            )
        ]
        
        return challenges
    
    def _create_simple_corridor(self):
        """Create a simple corridor for the first challenge."""
        return {
            (0, 0): 'floor', (1, 0): 'floor', (2, 0): 'floor', (3, 0): 'exit',
            (-1, 0): 'wall', (4, 0): 'wall',
            (0, 1): 'wall', (1, 1): 'wall', (2, 1): 'wall', (3, 1): 'wall',
            (0, -1): 'wall', (1, -1): 'wall', (2, -1): 'wall', (3, -1): 'wall'
        }
    
    def _create_key_room(self):
        """Create a room with a key to collect."""
        world = {}
        # 5x3 room
        for x in range(5):
            for y in range(3):
                world[(x, y)] = 'floor'
        
        # Walls
        for x in range(-1, 6):
            world[(x, -1)] = 'wall'
            world[(x, 3)] = 'wall'
        for y in range(-1, 4):
            world[(-1, y)] = 'wall'
            world[(5, y)] = 'wall'
        
        # Key in the middle
        world[(2, 1)] = 'key'
        
        return world
    
    def start_game(self):
        """Start the interactive game."""
        print("=" * 70)
        print(" VAULT RUNNER PROGRAMMING GAME ")
        print("=" * 70)
        print("Welcome to the Vault Runner programming game!")
        print("Write programs to control a robot and solve challenges.")
        print()
        
        self.player_name = input("Enter your name: ").strip() or "Player"
        print(f"Hello, {self.player_name}! Let's start programming!")
        
        self._show_tutorial()
        self._main_menu()
    
    def _show_tutorial(self):
        """Show the game tutorial."""
        print("\n" + "=" * 50)
        print(" TUTORIAL")
        print("=" * 50)
        print("Available commands:")
        print("  Movement: MOVE, LEFT, RIGHT, RTURN")
        print("  Actions:  PICK, OPEN")
        print("  Control:  LOOP <n>, WHILE <sensor>, IF <sensor>, END")
        print("  Sensors:  FRONT, KEY, DOOR, EXIT")
        print("  State:    SET, CLR")
        print()
        print("Example program:")
        print("  MOVE")
        print("  MOVE")
        print("  IF KEY")
        print("    PICK")
        print("  END")
        print()
        input("Press Enter to continue...")
    
    def _main_menu(self):
        """Show the main game menu."""
        while True:
            print("\n" + "=" * 50)
            print(" MAIN MENU")
            print("=" * 50)
            print("1. View Challenges")
            print("2. Play Challenge")
            print("3. View Leaderboard")
            print("4. Practice Mode")
            print("5. Exit Game")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                self._show_challenges()
            elif choice == '2':
                self._play_challenge()
            elif choice == '3':
                self._show_leaderboard()
            elif choice == '4':
                self._practice_mode()
            elif choice == '5':
                print(f"Thanks for playing, {self.player_name}!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _show_challenges(self):
        """Show all available challenges."""
        print("\n" + "=" * 50)
        print("🏆 CHALLENGES")
        print("=" * 50)
        
        for i, challenge in enumerate(self.challenges, 1):
            status = "" if challenge.best_score else "⭕"
            print(f"{i}. {status} {challenge.name}")
            print(f"   {challenge.description}")
            if challenge.best_score:
                print(f"   Best Score: {challenge.best_score}")
            print()
    
    def _play_challenge(self):
        """Play a selected challenge."""
        print("\n" + "=" * 50)
        print(" SELECT CHALLENGE")
        print("=" * 50)
        
        for i, challenge in enumerate(self.challenges, 1):
            status = "" if challenge.best_score else "⭕"
            print(f"{i}. {status} {challenge.name}")
        
        try:
            choice = int(input("\nEnter challenge number: ")) - 1
            if 0 <= choice < len(self.challenges):
                self.current_challenge = self.challenges[choice]
                self._run_challenge()
            else:
                print("Invalid challenge number.")
        except ValueError:
            print("Please enter a valid number.")
    
    def _run_challenge(self):
        """Run the selected challenge."""
        challenge = self.current_challenge
        
        print(f"\n" + "=" * 50)
        print(f" CHALLENGE: {challenge.name}")
        print("=" * 50)
        print(f"Description: {challenge.description}")
        print(f"Success Condition: {challenge.success_condition}")
        print(f"Max Instructions: {challenge.max_instructions}")
        
        # Show the world
        world = challenge.world_creator()
        runner = VaultRunner(world, challenge.start_pos, challenge.start_dir)
        print("\nInitial world state:")
        runner.display_world()
        
        print("\nEnter your program (one command per line, empty line to finish):")
        print("Available commands: MOVE, LEFT, RIGHT, RTURN, PICK, OPEN, LOOP <n>, WHILE <sensor>, IF <sensor>, END, SET, CLR")
        print("Sensors: FRONT, KEY, DOOR, EXIT")
        
        program_lines = []
        while True:
            line = input("> ").strip()
            if not line:
                break
            program_lines.append(line)
        
        if not program_lines:
            print("No program entered.")
            return
        
        # Test the program
        print("\n" + "=" * 30)
        print(" TESTING PROGRAM")
        print("=" * 30)
        
        result = challenge.test_program(program_lines)
        
        if 'error' in result:
            print(f" Program Error: {result['error']}")
            return
        
        print(f"Success: {' YES' if result['success'] else ' NO'}")
        print(f"Score: {result['score']}")
        print(f"Instructions Used: {result['instructions']}")
        print(f"Execution Time: {result['time']:.3f}s")
        print(f"Final Position: {result['final_position']}")
        print(f"Has Key: {result['has_key']}")
        print(f"Door Opened: {result['door_opened']}")
        
        # Show program analysis
        analysis = result['analysis']
        print(f"\nProgram Analysis:")
        print(f"  Total Tokens: {analysis['total_tokens']}")
        print(f"  Distinct Tokens: {analysis['distinct_tokens']}/20")
        print(f"  Control Structures: {analysis['control_structures']}")
        print(f"  Max Nesting Depth: {analysis['max_nesting_depth']}")
        print(f"  Complexity Score: {analysis['complexity_score']}")
        
        # Update best score
        if result['score'] > (challenge.best_score or 0):
            challenge.best_score = result['score']
            challenge.best_program = program_lines.copy()
            print(f"\n NEW BEST SCORE: {result['score']}!")
        
        # Record score
        self.score_history.append({
            'challenge': challenge.name,
            'score': result['score'],
            'success': result['success'],
            'timestamp': time.time()
        })
        
        input("\nPress Enter to continue...")
    
    def _show_leaderboard(self):
        """Show the leaderboard."""
        print("\n" + "=" * 50)
        print("🏆 LEADERBOARD")
        print("=" * 50)
        
        if not any(c.best_score for c in self.challenges):
            print("No scores yet. Complete some challenges!")
            return
        
        # Sort challenges by best score
        scored_challenges = [(c.name, c.best_score) for c in self.challenges if c.best_score]
        scored_challenges.sort(key=lambda x: x[1], reverse=True)
        
        print(f"Player: {self.player_name}")
        print()
        for i, (name, score) in enumerate(scored_challenges, 1):
            print(f"{i}. {name}: {score} points")
        
        total_score = sum(score for _, score in scored_challenges)
        print(f"\nTotal Score: {total_score} points")
    
    def _practice_mode(self):
        """Practice mode for testing programs."""
        print("\n" + "=" * 50)
        print(" PRACTICE MODE")
        print("=" * 50)
        print("Test your programs in different worlds without scoring.")
        
        print("\nSelect world:")
        print("1. Simple Corridor")
        print("2. Key Room")
        print("3. Corridor World")
        print("4. Room World")
        print("5. Multi-Key World")
        
        try:
            choice = int(input("Enter choice (1-5): "))
            world_creators = [
                lambda: self._create_simple_corridor(),
                lambda: self._create_key_room(),
                create_corridor_world,
                create_room_world,
                create_multi_key_world
            ]
            
            if 1 <= choice <= 5:
                world = world_creators[choice - 1]()
                runner = VaultRunner(world, (0, 0), 1)
                
                print("\nWorld state:")
                runner.display_world()
                
                print("\nEnter your program:")
                program_lines = []
                while True:
                    line = input("> ").strip()
                    if not line:
                        break
                    program_lines.append(line)
                
                if program_lines:
                    try:
                        interpreter = VaultInterpreter(program_lines)
                        result = interpreter.run(runner, show_steps=True)
                        print(f"\nResult: {'SUCCESS' if result else 'COMPLETED'}")
                    except Exception as e:
                        print(f"Error: {e}")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    """Main entry point for the game."""
    game = VaultRunnerGame()
    game.start_game()


if __name__ == "__main__":
    main()
