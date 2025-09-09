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
            screen_y = offset_y + (y - min_y) * self.cell_size
            
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
            robot_y = offset_y + (self.runner.y - min_y) * self.cell_size
            
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
                break
    
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
        
    def closeEvent(self, event):
        """Handle window close event."""
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
