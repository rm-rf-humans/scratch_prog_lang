"""
Vault Runner GUI Game - PyQt5-based graphical interface for the Vault Runner game.

This module provides a modern GUI interface for the Vault Runner programming game,
including visual world representation, program editor, and interactive gameplay.
"""

import sys
import time
from typing import List, Dict, Tuple, Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QTextEdit, QPushButton, 
                            QLabel, QComboBox, QSpinBox, QCheckBox, QTabWidget,
                            QGroupBox, QScrollArea, QMessageBox, QProgressBar,
                            QSplitter, QFrame, QSizePolicy, QPlainTextEdit)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QPen, QBrush, QPixmap

try:
    from .interpreter import VaultInterpreter
    from .vault_runner import VaultRunner, create_corridor_world, create_room_world, create_multi_key_world
    from .game import VaultRunnerGame, GameChallenge
    from .sample_programs import SamplePrograms
except ImportError:
    from interpreter import VaultInterpreter
    from vault_runner import VaultRunner, create_corridor_world, create_room_world, create_multi_key_world
    from game import VaultRunnerGame, GameChallenge
    from sample_programs import SamplePrograms


class WorldDisplayWidget(QWidget):
    """Custom widget for displaying the robot world."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.world = None
        self.runner = None
        self.cell_size = 20
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #2b2b2b; border: 1px solid #555;")
        
    def update_world(self, world: Dict, runner: VaultRunner):
        """Update the world display with new data."""
        self.world = world
        self.runner = runner
        self.update()
        
    def paintEvent(self, event):
        """Paint the world visualization."""
        if not self.world or not self.runner:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate world bounds
        min_x = min(pos[0] for pos in self.world.keys())
        max_x = max(pos[0] for pos in self.world.keys())
        min_y = min(pos[1] for pos in self.world.keys())
        max_y = max(pos[1] for pos in self.world.keys())
        
        # Calculate offset to center the world
        world_width = (max_x - min_x + 1) * self.cell_size
        world_height = (max_y - min_y + 1) * self.cell_size
        
        offset_x = (self.width() - world_width) // 2
        offset_y = (self.height() - world_height) // 2
        
        # Draw world cells
        for (x, y), cell_type in self.world.items():
            screen_x = offset_x + (x - min_x) * self.cell_size
            # Flip Y-axis so (0,0) appears at bottom-left instead of top-left
            screen_y = offset_y + (max_y - y) * self.cell_size
            
            rect = QRect(screen_x, screen_y, self.cell_size, self.cell_size)
            
            # Set colors based on cell type
            if cell_type == 'wall':
                painter.fillRect(rect, QColor(100, 100, 100))
            elif cell_type == 'key':
                painter.fillRect(rect, QColor(255, 215, 0))  # Gold
                painter.setPen(QPen(QColor(0, 0, 0), 2))
                painter.drawText(rect, Qt.AlignCenter, "K")
            elif cell_type == 'door':
                painter.fillRect(rect, QColor(139, 69, 19))  # Brown
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                painter.drawText(rect, Qt.AlignCenter, "D")
            elif cell_type == 'exit':
                painter.fillRect(rect, QColor(0, 255, 0))  # Green
                painter.setPen(QPen(QColor(0, 0, 0), 2))
                painter.drawText(rect, Qt.AlignCenter, "E")
            else:  # empty
                painter.fillRect(rect, QColor(50, 50, 50))
                
            # Draw grid lines
            painter.setPen(QPen(QColor(80, 80, 80), 1))
            painter.drawRect(rect)
        
        # Draw robot
        if self.runner:
            robot_x = offset_x + (self.runner.x - min_x) * self.cell_size
            # Flip Y-axis for robot position to match world coordinates
            robot_y = offset_y + (max_y - self.runner.y) * self.cell_size
            
            robot_rect = QRect(robot_x + 2, robot_y + 2, self.cell_size - 4, self.cell_size - 4)
            painter.fillRect(robot_rect, QColor(255, 0, 0))  # Red robot
            
            # Draw direction indicator
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            center_x = robot_x + self.cell_size // 2
            center_y = robot_y + self.cell_size // 2
            
            # Direction arrows
            if self.runner.direction == 0:  # North
                painter.drawLine(center_x, center_y, center_x, center_y - 6)
            elif self.runner.direction == 1:  # East
                painter.drawLine(center_x, center_y, center_x + 6, center_y)
            elif self.runner.direction == 2:  # South
                painter.drawLine(center_x, center_y, center_x, center_y + 6)
            else:  # West
                painter.drawLine(center_x, center_y, center_x - 6, center_y)


class ProgramEditor(QPlainTextEdit):
    """Enhanced text editor for Vault Runner programs."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: 1px solid #555;
                padding: 5px;
            }
        """)
        self.setPlaceholderText("Enter your Vault Runner program here...\n\nExample:\nMOVE\nMOVE\nIF KEY\n  PICK\nEND")
        
    def get_program_lines(self) -> List[str]:
        """Get the program as a list of lines."""
        return [line.strip() for line in self.toPlainText().split('\n') if line.strip()]


class ExecutionThread(QThread):
    """Thread for executing programs without blocking the GUI."""
    
    finished = pyqtSignal(dict)
    step_update = pyqtSignal(dict)
    
    def __init__(self, program_lines: List[str], world_creator, start_pos: Tuple[int, int], 
                 start_dir: int, max_instructions: int = 1000):
        super().__init__()
        self.program_lines = program_lines
        self.world_creator = world_creator
        self.start_pos = start_pos
        self.start_dir = start_dir
        self.max_instructions = max_instructions
        self.should_stop = False
        
    def run(self):
        """Execute the program in a separate thread."""
        try:
            interpreter = VaultInterpreter(self.program_lines)
            interpreter.max_instructions = self.max_instructions
            
            world = self.world_creator()
            runner = VaultRunner(world, self.start_pos, self.start_dir)
            
            start_time = time.time()
            
            # Use the interpreter's built-in run method for correct execution
            # but emit step updates by overriding the display method
            original_display = runner.display_world
            
            def step_display():
                """Override display to emit step updates."""
                self.step_update.emit({
                    'world': world,
                    'runner': runner,
                    'pc': interpreter.pc,
                    'instruction_count': interpreter.instruction_count,
                    'token': 'STEP'
                })
                self.msleep(100)  # Small delay for visualization
            
            # Temporarily override display method
            runner.display_world = step_display
            
            # Execute the program
            result = interpreter.run(runner, show_steps=True)
            
            # Restore original display method
            runner.display_world = original_display
            
            end_time = time.time()
            
            self.finished.emit({
                'success': result,
                'world': world,
                'runner': runner,
                'instruction_count': interpreter.instruction_count,
                'execution_time': end_time - start_time,
                'error': None
            })
            
        except Exception as e:
            self.finished.emit({
                'success': False,
                'world': None,
                'runner': None,
                'instruction_count': 0,
                'execution_time': 0,
                'error': str(e)
            })
    
    def stop_execution(self):
        """Stop the execution."""
        self.should_stop = True


class VaultRunnerGUI(QMainWindow):
    """Main GUI window for the Vault Runner game."""
    
    def __init__(self):
        super().__init__()
        self.game = VaultRunnerGame()
        self.current_challenge = None
        self.execution_thread = None
        self.step_timer = QTimer()
        self.step_timer.timeout.connect(self.execute_next_step)
        self.step_execution_active = False
        self.step_interpreter = None
        self.step_runner = None
        self.step_paused = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Vault Runner - Programming Game")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #d4d4d4;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
            QComboBox {
                background-color: #404040;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
            }
            QLabel {
                color: #d4d4d4;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Program editor and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - World display and info
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([600, 600])
        
        # Set initial challenge after both panels are created
        self.on_challenge_changed(self.challenge_combo.currentText())
        
    def create_left_panel(self) -> QWidget:
        """Create the left panel with program editor and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Challenge selection
        challenge_group = QGroupBox("Challenge Selection")
        challenge_layout = QVBoxLayout(challenge_group)
        
        self.challenge_combo = QComboBox()
        for challenge in self.game.challenges:
            self.challenge_combo.addItem(challenge.name)
        self.challenge_combo.currentTextChanged.connect(self.on_challenge_changed)
        challenge_layout.addWidget(self.challenge_combo)
        
        # Special Extension Challenge button
        self.extension_button = QPushButton("Extension Challenge")
        self.extension_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6b35;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e55a2b;
            }
            QPushButton:pressed {
                background-color: #cc4a1f;
            }
        """)
        self.extension_button.clicked.connect(self.select_extension_challenge)
        challenge_layout.addWidget(self.extension_button)
        
        self.challenge_description = QLabel()
        self.challenge_description.setWordWrap(True)
        self.challenge_description.setStyleSheet("padding: 10px; background-color: #1e1e1e; border-radius: 4px;")
        challenge_layout.addWidget(self.challenge_description)
        
        layout.addWidget(challenge_group)
        
        # Program editor
        editor_group = QGroupBox("Program Editor")
        editor_layout = QVBoxLayout(editor_group)
        
        self.program_editor = ProgramEditor()
        editor_layout.addWidget(self.program_editor)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("Run Program")
        self.run_button.clicked.connect(self.run_program)
        button_layout.addWidget(self.run_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_program)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_program)
        button_layout.addWidget(self.clear_button)
        
        self.load_sample_button = QPushButton("Load Sample")
        self.load_sample_button.clicked.connect(self.load_sample_program)
        button_layout.addWidget(self.load_sample_button)
        
        editor_layout.addLayout(button_layout)
        layout.addWidget(editor_group)
        
        # Program analysis
        analysis_group = QGroupBox("Program Analysis")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.analysis_label = QLabel("No program loaded")
        self.analysis_label.setWordWrap(True)
        self.analysis_label.setStyleSheet("padding: 10px; background-color: #1e1e1e; border-radius: 4px;")
        analysis_layout.addWidget(self.analysis_label)
        
        layout.addWidget(analysis_group)
        
        # Position testing section - REMOVED FOR SIMPLICITY
        # # testing_group = QGroupBox("Position Testing")
        # testing_layout = QVBoxLayout(testing_group)
        #         # # Position controls
        # position_layout = QHBoxLayout()
        #         # position_layout.addWidget(QLabel("Start Position:"))
        # self.pos_x_spin = QSpinBox()
        # self.pos_x_spin.setRange(-10, 10)
        # self.pos_x_spin.setValue(0)
        # position_layout.addWidget(QLabel("X:"))
        # position_layout.addWidget(self.pos_x_spin)
        #         # self.pos_y_spin = QSpinBox()
        # self.pos_y_spin.setRange(-10, 10)
        # self.pos_y_spin.setValue(0)
        # position_layout.addWidget(QLabel("Y:"))
        # position_layout.addWidget(self.pos_y_spin)
        #         # position_layout.addWidget(QLabel("Direction:"))
        # self.direction_combo = QComboBox()
        # self.direction_combo.addItems(["North (0)", "East (1)", "South (2)", "West (3)"])
        # position_layout.addWidget(self.direction_combo)
        #         # testing_layout.addLayout(position_layout)
        #         # # Testing buttons
        # test_button_layout = QHBoxLayout()
        #         # self.test_position_button = QPushButton("Test Position")
        # self.test_position_button.clicked.connect(self.test_single_position)
        # test_button_layout.addWidget(self.test_position_button)
        #         # self.test_step_by_step_button = QPushButton("Step-by-Step Test")
        # self.test_step_by_step_button.clicked.connect(self.test_position_step_by_step)
        # self.test_step_by_step_button.setStyleSheet("""
        # QPushButton {
        # background-color: #2196F3;
        # color: white;
        # border: none;
        # padding: 8px;
        # border-radius: 4px;
        # font-weight: bold;
        # }
        # QPushButton:hover {
        # background-color: #1976D2;
        # }
        # QPushButton:pressed {
        # background-color: #0D47A1;
        # }
        # """)
        # test_button_layout.addWidget(self.test_step_by_step_button)
        #         # self.test_all_button = QPushButton("Test All Positions")
        # self.test_all_button.clicked.connect(self.test_all_positions)
        # test_button_layout.addWidget(self.test_all_button)
        #         # testing_layout.addLayout(test_button_layout)
        #         # # Step execution controls
        # step_control_layout = QHBoxLayout()
        #         # self.reset_display_button = QPushButton("Reset Display")
        # self.reset_display_button.clicked.connect(self.reset_world_display)
        # step_control_layout.addWidget(self.reset_display_button)
        #         # step_control_layout.addWidget(QLabel("Speed:"))
        # self.speed_slider = QSpinBox()
        # self.speed_slider.setRange(50, 2000)
        # self.speed_slider.setValue(500)
        # self.speed_slider.setSuffix(" ms")
        # step_control_layout.addWidget(self.speed_slider)
        #         # self.pause_button = QPushButton("Pause")
        # self.pause_button.clicked.connect(self.toggle_step_execution)
        # self.pause_button.setEnabled(False)
        # step_control_layout.addWidget(self.pause_button)
        #         # testing_layout.addLayout(step_control_layout)
        #         # # Test results display
        # self.test_results_label = QLabel("No tests run")
        # self.test_results_label.setWordWrap(True)
        # self.test_results_label.setStyleSheet("padding: 10px; background-color: #1e1e1e; border-radius: 4px; max-height: 150px;")
        # self.test_results_label.setMaximumHeight(150)
        # testing_layout.addWidget(self.test_results_label)
        #         #         layout.addWidget(testing_group)
        
        # Update analysis when program changes
        self.program_editor.textChanged.connect(self.update_analysis)
        
        return panel
        
    def create_right_panel(self) -> QWidget:
        """Create the right panel with world display and execution info."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # World display
        world_group = QGroupBox("World Visualization")
        world_layout = QVBoxLayout(world_group)
        
        self.world_display = WorldDisplayWidget()
        world_layout.addWidget(self.world_display)
        
        layout.addWidget(world_group)
        
        # Execution info
        info_group = QGroupBox("Execution Information")
        info_layout = QVBoxLayout(info_group)
        
        self.status_label = QLabel("Ready to run program")
        info_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        info_layout.addWidget(self.progress_bar)
        
        self.results_label = QLabel()
        self.results_label.setWordWrap(True)
        self.results_label.setStyleSheet("padding: 10px; background-color: #1e1e1e; border-radius: 4px;")
        info_layout.addWidget(self.results_label)
        
        layout.addWidget(info_group)
        
        return panel
        
    def on_challenge_changed(self, challenge_name: str):
        """Handle challenge selection change."""
        for challenge in self.game.challenges:
            if challenge.name == challenge_name:
                self.current_challenge = challenge
                self.challenge_description.setText(f"<b>{challenge.name}</b><br>{challenge.description}")
                self.update_world_display()
                # self._update_position_defaults(challenge_name)  # Position testing removed
                break
                
    def _update_position_defaults(self, challenge_name: str):
        """Update position control defaults based on challenge."""
        if challenge_name == "Door Master":
            # Corridor challenge - set to a corner position
            self.pos_x_spin.setValue(0)
            self.pos_y_spin.setValue(0)
            self.direction_combo.setCurrentIndex(1)  # East
        elif challenge_name in ["Extension Challenge"]:
            # Multi-key challenge - set to center
            self.pos_x_spin.setValue(2)
            self.pos_y_spin.setValue(2)
            self.direction_combo.setCurrentIndex(0)  # North
        else:
            # Default room challenge - lower-left corner
            self.pos_x_spin.setValue(0)
            self.pos_y_spin.setValue(0)
            self.direction_combo.setCurrentIndex(0)  # North
    
    def select_extension_challenge(self):
        """Select the Extension Challenge and show special info."""
        # Find and select the Extension Challenge
        for i in range(self.challenge_combo.count()):
            if self.challenge_combo.itemText(i) == "Extension Challenge":
                self.challenge_combo.setCurrentIndex(i)
                break
        
        # Show special message for Extension Challenge
        self.challenge_description.setText("""
        <b>Extension Challenge</b><br>
        <b>Challenge:</b> Solve a map with multiple keys, one door, and one exit. Only one key opens the door. Unknown starting position and direction!<br><br>
        <b>Features:</b><br>
        • 4x4 room with 3 keys (only 1 works)<br>
        • Random starting position and direction<br>
        • Must find correct key and escape<br>
        • Maximum 3000 instructions<br><br>
        <b>Success:</b> Find the correct key and escape through the door
        """)
        
        # Update the world display
        self.update_world_display()
                
    def update_world_display(self):
        """Update the world display with current challenge."""
        if self.current_challenge and hasattr(self, 'world_display'):
            world = self.current_challenge.world_creator()
            runner = VaultRunner(world, self.current_challenge.start_pos, self.current_challenge.start_dir)
            self.world_display.update_world(world, runner)
            
    def update_analysis(self):
        """Update program analysis display."""
        program_lines = self.program_editor.get_program_lines()
        if not program_lines:
            self.analysis_label.setText("No program loaded")
            return
            
        try:
            interpreter = VaultInterpreter(program_lines)
            analysis = interpreter.analyze_program()
            
            analysis_text = f"""
<b>Program Analysis:</b><br>
• Total tokens: {analysis['total_tokens']}<br>
• Distinct tokens: {analysis['distinct_tokens']}/20<br>
• Control structures: {analysis['control_structures']}<br>
• Max nesting depth: {analysis['max_nesting_depth']}<br>
• Complexity score: {analysis['complexity_score']}
            """.strip()
            
            self.analysis_label.setText(analysis_text)
            
        except Exception as e:
            self.analysis_label.setText(f"<b>Analysis Error:</b><br>{str(e)}")
    
    def load_sample_program(self):
        """Load a sample program for the current challenge."""
        if not self.current_challenge:
            QMessageBox.warning(self, "No Challenge", "Please select a challenge first.")
            return
        
        # Get sample program from centralized module
        sample_program = SamplePrograms.get_sample_for_challenge(self.current_challenge.name)
        
        self.program_editor.setPlainText(sample_program)
        self.update_analysis()
            
    def run_program(self):
        """Run the current program."""
        if not self.current_challenge:
            QMessageBox.warning(self, "No Challenge", "Please select a challenge first.")
            return
            
        program_lines = self.program_editor.get_program_lines()
        if not program_lines:
            QMessageBox.warning(self, "No Program", "Please enter a program first.")
            return
            
        # Disable run button and enable stop button
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Create and start execution thread
        self.execution_thread = ExecutionThread(
            program_lines,
            self.current_challenge.world_creator,
            self.current_challenge.start_pos,
            self.current_challenge.start_dir,
            self.current_challenge.max_instructions
        )
        
        self.execution_thread.step_update.connect(self.on_step_update)
        self.execution_thread.finished.connect(self.on_execution_finished)
        self.execution_thread.start()
        
        self.status_label.setText("Executing program...")
        
    def stop_program(self):
        """Stop the current program execution."""
        if self.execution_thread and self.execution_thread.isRunning():
            self.execution_thread.stop_execution()
            self.execution_thread.wait()
            
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Execution stopped")
        
    def on_step_update(self, data: dict):
        """Handle step update from execution thread."""
        if data.get('world') and data.get('runner'):
            self.world_display.update_world(data['world'], data['runner'])
        self.status_label.setText(f"Step {data.get('instruction_count', 0)}: {data.get('token', 'Unknown')}")
        
    def on_execution_finished(self, result: dict):
        """Handle execution completion."""
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if result['error']:
            self.status_label.setText("Execution failed")
            self.results_label.setText(f"<b>Error:</b><br>{result['error']}")
            QMessageBox.critical(self, "Execution Error", result['error'])
        else:
            success = result['success']
            self.status_label.setText("Execution completed")
            
            if result['runner']:
                results_text = f"""
<b>Execution Results:</b><br>
• Success: {'Yes' if success else 'No'}<br>
• Instructions executed: {result['instruction_count']}<br>
• Execution time: {result['execution_time']:.2f}s<br>
• Final position: ({result['runner'].x}, {result['runner'].y})<br>
• Has key: {'Yes' if result['runner'].has_key else 'No'}<br>
• Door opened: {'Yes' if result['runner'].door_opened else 'No'}
                """.strip()
            else:
                results_text = f"""
<b>Execution Results:</b><br>
• Success: {'Yes' if success else 'No'}<br>
• Instructions executed: {result['instruction_count']}<br>
• Execution time: {result['execution_time']:.2f}s<br>
• Final position: N/A<br>
• Has key: N/A<br>
• Door opened: N/A
                """.strip()
            
            self.results_label.setText(results_text)
            
            if success:
                QMessageBox.information(self, "Success!", "Congratulations! You completed the challenge!")
            else:
                QMessageBox.warning(self, "Challenge Failed", "The program did not complete the challenge successfully.")
                
    def clear_program(self):
        """Clear the program editor."""
        self.program_editor.clear()
        
    def reset_world_display(self):
        """Reset the world display to the default challenge state."""
        # Stop any running step execution
        self.stop_step_execution()
        self.update_world_display()
        self.test_results_label.setText("World display reset to default challenge state")
        self.status_label.setText("World display reset")
        
    def test_single_position(self):
        """Test the current program from a specific position and direction."""
        if not self.current_challenge:
            QMessageBox.warning(self, "No Challenge", "Please select a challenge first.")
            return
            
        program_text = self.program_editor.toPlainText().strip()
        if not program_text:
            QMessageBox.warning(self, "No Program", "Please enter a program to test.")
            return
            
        # Get test position and direction
        test_x = self.pos_x_spin.value()
        test_y = self.pos_y_spin.value()
        test_dir = self.direction_combo.currentIndex()
        
        self.status_label.setText(f"Testing position ({test_x}, {test_y}), direction {test_dir}...")
        
        try:
            # Run the test and get the final runner state
            result, final_runner = self._run_position_test_with_display(program_text, test_x, test_y, test_dir)
            
            # Update the world display with the final state
            if final_runner:
                world_creator = self._get_world_creator()
                world = world_creator()
                self.world_display.update_world(world, final_runner)
            
            # Display results
            success_text = "SUCCESS" if result['success'] else "FAILED"
            color = "#4CAF50" if result['success'] else "#f44336"
            
            results_html = f"""
<b style="color: {color};">Position Test: {success_text}</b><br>
<b>Start Position:</b> ({test_x}, {test_y}), Direction: {test_dir}<br>
<b>Final Position:</b> {result.get('final_position', 'N/A')}<br>
<b>Instructions:</b> {result.get('instructions', 'N/A')}<br>
<b>Time:</b> {result.get('time', 0):.2f}s<br>
<b>Has Key:</b> {result.get('has_key', False)}<br>
<b>Door Opened:</b> {result.get('door_opened', False)}<br>
<b>Escape Via:</b> {result.get('escape_via', 'none')}
            """.strip()
            
            if 'error' in result:
                results_html += f"<br><b>Error:</b> {result['error']}"
                
            self.test_results_label.setText(results_html)
            self.status_label.setText("Position test completed - see world display")
            
        except Exception as e:
            QMessageBox.critical(self, "Test Error", f"Error running position test: {str(e)}")
            self.status_label.setText("Position test failed")

    def test_all_positions(self):
        """Test the current program from all valid positions and directions."""
        if not self.current_challenge:
            QMessageBox.warning(self, "No Challenge", "Please select a challenge first.")
            return
            
        program_text = self.program_editor.toPlainText().strip()
        if not program_text:
            QMessageBox.warning(self, "No Program", "Please enter a program to test.")
            return
            
        self.status_label.setText("Running comprehensive position tests...")
        self.test_results_label.setText("Testing all positions...")
        
        try:
            # Get all valid positions for the current challenge
            world_creator = self._get_world_creator()
            world = world_creator()
            
            # Find all valid floor positions
            valid_positions = []
            for pos, tile in world.items():
                if tile in ['floor', 'key', 'door', 'exit']:
                    valid_positions.append(pos)
            
            # Test all combinations
            total_tests = len(valid_positions) * 4  # 4 directions
            successes = 0
            failures = []
            
            for i, pos in enumerate(valid_positions):
                for direction in range(4):
                    result = self._run_position_test(program_text, pos[0], pos[1], direction)
                    if result['success']:
                        successes += 1
                    else:
                        failures.append((pos, direction, result.get('error', 'Failed')))
            
            # Display comprehensive results
            success_rate = (successes / total_tests) * 100 if total_tests > 0 else 0
            color = "#4CAF50" if success_rate >= 80 else "#FFC107" if success_rate >= 50 else "#f44336"
            
            results_html = f"""
<b style="color: {color};">Comprehensive Test Results</b><br>
<b>Success Rate:</b> {successes}/{total_tests} ({success_rate:.1f}%)<br>
<b>Valid Positions Tested:</b> {len(valid_positions)}<br>
<b>Directions per Position:</b> 4<br>
            """.strip()
            
            if failures and len(failures) <= 5:
                results_html += "<br><b>Failed Cases:</b><br>"
                for pos, direction, error in failures:
                    results_html += f"• {pos} dir {direction}: {error}<br>"
            elif failures:
                results_html += f"<br><b>Failed Cases:</b> {len(failures)} (showing first 3)<br>"
                for pos, direction, error in failures[:3]:
                    results_html += f"• {pos} dir {direction}: {error}<br>"
                    
            self.test_results_label.setText(results_html)
            self.status_label.setText(f"All position tests completed: {success_rate:.1f}% success rate")
            
        except Exception as e:
            QMessageBox.critical(self, "Test Error", f"Error running comprehensive tests: {str(e)}")
            self.status_label.setText("Comprehensive test failed")

    def test_position_step_by_step(self):
        """Test the current program with step-by-step visual execution."""
        if not self.current_challenge:
            QMessageBox.warning(self, "No Challenge", "Please select a challenge first.")
            return
            
        program_text = self.program_editor.toPlainText().strip()
        if not program_text:
            QMessageBox.warning(self, "No Program", "Please enter a program to test.")
            return
            
        # Stop any existing step execution
        self.stop_step_execution()
        
        # Get test position and direction
        # For Room Explorer (BFS challenge), ensure we use bottom-left (0,0) facing North
        if self.current_challenge.name == "Room Explorer":
            test_x = 0  # Bottom-left X
            test_y = 0  # Bottom-left Y  
            test_dir = 0  # North
            # Update the GUI controls to show correct values
            self.pos_x_spin.setValue(test_x)
            self.pos_y_spin.setValue(test_y)
            self.direction_combo.setCurrentIndex(test_dir)
        else:
            test_x = self.pos_x_spin.value()
            test_y = self.pos_y_spin.value()
            test_dir = self.direction_combo.currentIndex()
        
        try:
            # Parse program
            program_lines = [line.strip() for line in program_text.split('\n') 
                           if line.strip() and not line.strip().startswith('#')]
            
            self.step_interpreter = VaultInterpreter(program_lines)
            self.step_interpreter.max_instructions = 1000
            
            # Create world and runner
            world_creator = self._get_world_creator()
            world = world_creator()
            
            # Handle special cases for Extension Challenge
            if self.current_challenge.name == "Extension Challenge":
                import random
                valid_positions = [(x, y) for x in range(4) for y in range(4)]
                if (test_x, test_y) not in valid_positions:
                    test_x, test_y = random.choice(valid_positions)
                self.step_runner = VaultRunner(world, (test_x, test_y), test_dir)
                self.step_runner.correct_key_pos = (1, 3)
            else:
                self.step_runner = VaultRunner(world, (test_x, test_y), test_dir)
            
            # Verify runner was created successfully
            if self.step_runner is None:
                raise Exception("Failed to create runner object")
            
            # Set up interpreter with runner reference
            self.step_interpreter.runner = self.step_runner
            
            # Set up custom display function for step updates
            self.step_runner.display_world = self.update_step_display
            
            # Start step execution
            self.step_execution_active = True
            self.step_paused = False
            # self.pause_button.setEnabled(True)  # Position testing removed
            # self.pause_button.setText("Pause")  # Position testing removed
            # self.test_step_by_step_button.setEnabled(False)  # Position testing removed
            
            # Update display with initial state
            self.world_display.update_world(world, self.step_runner)
            
            self.status_label.setText(f"Step-by-step execution started from ({test_x}, {test_y}), direction {test_dir}")
            
            # Enhanced status for BFS challenge
            if self.current_challenge.name == "Room Explorer":
                challenge_info = "<br><b>BFS Challenge:</b> Find shortest path to exit from bottom-left"
            else:
                challenge_info = ""
                
            self.test_results_label.setText(f"<b>Step-by-Step Execution</b><br>Starting at ({test_x}, {test_y}), direction {test_dir}<br>Instructions executed: 0<br>Program length: {len(program_lines)} lines{challenge_info}")
            
            # Start the step timer
            # self.step_timer.start(self.speed_slider.value())  # Position testing removed
            
        except Exception as e:
            QMessageBox.critical(self, "Step Execution Error", f"Error starting step execution: {str(e)}")
            self.stop_step_execution()

    def execute_next_step(self):
        """Execute the next step in the program."""
        if not self.step_execution_active or self.step_paused or not self.step_interpreter or not self.step_runner:
            self.stop_step_execution()
            return
            
        try:
            # Double check that runner is still valid
            if self.step_runner is None:
                self.complete_step_execution("Error: Runner object became None")
                return
                
            # Check if program is complete
            if self.step_interpreter.pc >= len(self.step_interpreter.tokens) or self.step_runner.escaped:
                print(f"DEBUG: Completing execution - PC: {self.step_interpreter.pc}/{len(self.step_interpreter.tokens)}, Escaped: {self.step_runner.escaped}")
                self.complete_step_execution()
                return
                
            # Execute one instruction
            if self.step_interpreter.instruction_count >= self.step_interpreter.max_instructions:
                self.complete_step_execution("Maximum instructions reached")
                return
                
            # Get current instruction for display
            if self.step_interpreter.pc >= len(self.step_interpreter.tokens):
                self.complete_step_execution()
                return
                
            current_token = self.step_interpreter.tokens[self.step_interpreter.pc]
            print(f"DEBUG: Step {self.step_interpreter.instruction_count} - PC: {self.step_interpreter.pc}, Token: {current_token}, Pos: ({self.step_runner.x}, {self.step_runner.y})")
            
            # Ensure interpreter has the runner reference
            if not hasattr(self.step_interpreter, 'runner') or self.step_interpreter.runner != self.step_runner:
                self.step_interpreter.runner = self.step_runner
            
            # Execute the instruction safely
            old_pc = self.step_interpreter.pc
            try:
                # Increment instruction count (like the normal run loop)
                self.step_interpreter.instruction_count += 1
                
                # Record execution step for debugging (like the normal run loop)
                step_info = {
                    'pc': self.step_interpreter.pc,
                    'token': current_token,
                    'position': (self.step_runner.x, self.step_runner.y),
                    'direction': self.step_runner.direction,
                    'has_key': self.step_runner.has_key,
                    'door_opened': self.step_runner.door_opened
                }
                self.step_interpreter.execution_history.append(step_info)
                
                # The _execute_instruction method expects (token, show_steps)
                # It uses self.runner internally, so we need to make sure it's set
                self.step_interpreter._execute_instruction(current_token, True)
                
                # Advance program counter (like the normal run loop)
                # The _execute_instruction method handles control flow PC changes internally
                self.step_interpreter.pc += 1
                
                # Update the world display after each instruction
                self.update_step_display()
                
            except Exception as exec_error:
                self.complete_step_execution(f"Execution error: {str(exec_error)}")
                return
            
            # Verify runner is still valid after instruction
            if self.step_runner is None:
                self.complete_step_execution("Error: Runner object became None during execution")
                return
            
            # Update the timer interval if speed changed
            # if self.step_timer.interval() != self.speed_slider.value():  # Position testing removed
                # self.step_timer.start(self.speed_slider.value())  # Position testing removed
            
            # Update status
            escape_status = " - ESCAPED!" if self.step_runner.escaped else ""
            self.status_label.setText(f"Executed: {current_token} | Position: ({self.step_runner.x}, {self.step_runner.y}){escape_status}")
            
            # Update results display
            escape_via = getattr(self.step_runner, 'escape_via', 'none')
            results_html = f"""
<b>Step-by-Step Execution</b><br>
<b>Current Position:</b> ({self.step_runner.x}, {self.step_runner.y})<br>
<b>Direction:</b> {self.step_runner.direction}<br>
<b>Instructions Executed:</b> {self.step_interpreter.instruction_count}<br>
<b>Current Instruction:</b> {current_token}<br>
<b>Has Key:</b> {self.step_runner.has_key}<br>
<b>Door Opened:</b> {self.step_runner.door_opened}<br>
<b>Escaped:</b> {self.step_runner.escaped}<br>
<b>Escape Via:</b> {escape_via}
            """.strip()
            
            self.test_results_label.setText(results_html)
            
        except Exception as e:
            self.complete_step_execution(f"Error: {str(e)}")

    def update_step_display(self, show_steps=True):
        """Custom display function for step-by-step execution."""
        if self.step_runner:
            world_creator = self._get_world_creator()
            world = world_creator()
            self.world_display.update_world(world, self.step_runner)

    def complete_step_execution(self, message=""):
        """Complete the step-by-step execution."""
        success = self.step_runner.escaped if self.step_runner else False
        
        # Determine success based on challenge
        if self.current_challenge.name == "Extension Challenge" and self.step_runner:
            success = self.step_runner.escaped and getattr(self.step_runner, 'escape_via', '') == 'door'
        
        success_text = "SUCCESS" if success else "FAILED"
        color = "#4CAF50" if success else "#f44336"
        
        final_message = message if message else ("Program completed successfully!" if success else "Program failed to complete challenge.")
        
        results_html = f"""
<b style="color: {color};">Step Execution Complete: {success_text}</b><br>
<b>Final Position:</b> ({self.step_runner.x}, {self.step_runner.y})<br>
<b>Total Instructions:</b> {self.step_interpreter.instruction_count}<br>
<b>Has Key:</b> {self.step_runner.has_key}<br>
<b>Door Opened:</b> {self.step_runner.door_opened}<br>
<b>Escaped:</b> {self.step_runner.escaped}<br>
<b>Escape Via:</b> {getattr(self.step_runner, 'escape_via', 'none')}<br>
<b>Result:</b> {final_message}
        """.strip()
        
        self.test_results_label.setText(results_html)
        self.status_label.setText(f"Step execution completed: {success_text}")
        
        self.stop_step_execution()

    def toggle_step_execution(self):
        """Toggle pause/resume for step execution."""
        if not self.step_execution_active:
            return
            
        self.step_paused = not self.step_paused
        if self.step_paused:
            # self.step_timer.stop()  # Position testing removed
            # self.pause_button.setText("Resume")  # Position testing removed
            self.status_label.setText("Step execution paused")
        else:
            # self.step_timer.start(self.speed_slider.value())  # Position testing removed
            # self.pause_button.setText("Pause")  # Position testing removed
            self.status_label.setText("Step execution resumed")

    def stop_step_execution(self):
        """Stop the step-by-step execution."""
        self.step_execution_active = False
        self.step_paused = False
        # self.step_timer.stop()  # Position testing removed
        # self.pause_button.setEnabled(False)  # Position testing removed
        # self.pause_button.setText("Pause")  # Position testing removed
        # self.test_step_by_step_button.setEnabled(True)  # Position testing removed
        self.step_interpreter = None
        self.step_runner = None

    def _run_position_test(self, program_text: str, x: int, y: int, direction: int) -> dict:
        """Run a single position test and return results."""
        result, _ = self._run_position_test_with_display(program_text, x, y, direction)
        return result

    def _run_position_test_with_display(self, program_text: str, x: int, y: int, direction: int) -> tuple:
        """Run a single position test and return results plus final runner state."""
        try:
            # Parse program
            program_lines = [line.strip() for line in program_text.split('\n') 
                           if line.strip() and not line.strip().startswith('#')]
            
            interpreter = VaultInterpreter(program_lines)
            interpreter.max_instructions = 1000  # Reasonable limit for testing
            
            # Create world and runner
            world_creator = self._get_world_creator()
            world = world_creator()
            
            # Handle special cases for Extension Challenge
            if self.current_challenge.name == "Extension Challenge":
                import random
                # For extension challenge, use random position if requested position is invalid
                valid_positions = [(x, y) for x in range(4) for y in range(4)]
                if (x, y) not in valid_positions:
                    x, y = random.choice(valid_positions)
                runner = VaultRunner(world, (x, y), direction)
                runner.correct_key_pos = (1, 3)  # Set correct key position
            else:
                runner = VaultRunner(world, (x, y), direction)
            
            # Run the program
            start_time = time.time()
            result = interpreter.run(runner, show_steps=False)
            end_time = time.time()
            
            # Determine success based on challenge
            success = False
            if self.current_challenge.name == "Extension Challenge":
                success = runner.escaped and getattr(runner, 'escape_via', '') == 'door'
            else:
                success = runner.escaped
                
            result_dict = {
                'success': success,
                'instructions': interpreter.instruction_count,
                'time': end_time - start_time,
                'final_position': (runner.x, runner.y),
                'has_key': runner.has_key,
                'door_opened': runner.door_opened,
                'escape_via': getattr(runner, 'escape_via', 'none')
            }
            
            return result_dict, runner
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'instructions': 0,
                'time': 0,
                'final_position': (x, y),
                'has_key': False,
                'door_opened': False,
                'escape_via': 'none'
            }
            return error_result, None

    def _get_world_creator(self):
        """Get the appropriate world creator for the current challenge."""
        if not self.current_challenge:
            return create_room_world
            
        challenge_name = self.current_challenge.name
        if challenge_name in ["Door Master"]:
            return create_corridor_world
        elif challenge_name in ["Extension Challenge"]:
            return create_multi_key_world
        else:
            return create_room_world

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop step execution
        self.stop_step_execution()
        
        # Stop regular execution thread
        if self.execution_thread and self.execution_thread.isRunning():
            self.execution_thread.stop_execution()
            self.execution_thread.wait()
        event.accept()


def main():
    """Main function to run the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Vault Runner")
    app.setApplicationVersion("1.0")
    
    # Set application style
    app.setStyle('Fusion')
    
    window = VaultRunnerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
