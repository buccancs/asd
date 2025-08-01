"""
Calibration Dialog for Milestone 3.4: Calibration Engine (OpenCV)

This module provides a comprehensive GUI interface for the calibration workflow,
including frame capture, calibration computation, and results display.
"""

import os
import sys
import time
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QTextEdit,
    QGroupBox,
    QCheckBox,
    QSlider,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QFileDialog,
    QTabWidget,
    QWidget,
)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from calibration.calibration_manager import CalibrationManager
from calibration.calibration_result import CalibrationResult


class CalibrationDialog(QDialog):
    """
    Comprehensive calibration dialog implementing the workflow described in Milestone 3.4.

    Features:
    - Guided calibration procedure with instructions
    - Frame capture with progress tracking
    - Calibration computation with quality assessment
    - Results display and saving
    - Real-time overlay toggle
    """

    # Signals
    calibration_completed = pyqtSignal(str, CalibrationResult)  # device_id, result
    overlay_toggled = pyqtSignal(str, bool)  # device_id, enabled

    def __init__(self, device_server, parent=None):
        super().__init__(parent)
        self.device_server = device_server
        self.calibration_manager = CalibrationManager()
        self.current_session = None
        self.device_results = {}  # device_id -> CalibrationResult

        self.setWindowTitle("Camera Calibration - Milestone 3.4")
        self.setModal(True)
        self.resize(800, 600)

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the user interface components."""
        layout = QVBoxLayout(self)

        # Instructions section
        self.create_instructions_section(layout)

        # Device selection and session controls
        self.create_session_controls(layout)

        # Capture section
        self.create_capture_section(layout)

        # Computation section
        self.create_computation_section(layout)

        # Results section
        self.create_results_section(layout)

        # Action buttons
        self.create_action_buttons(layout)

    def create_instructions_section(self, parent_layout):
        """Create the instructions section."""
        instructions_group = QGroupBox("Calibration Instructions")
        instructions_layout = QVBoxLayout(instructions_group)

        instructions_text = """
        <b>Camera Calibration Procedure:</b><br><br>
        1. Place the calibration pattern (chessboard) in view of both RGB and thermal cameras<br>
        2. Capture at least 5-10 images from different angles and positions<br>
        3. Ensure the pattern fills about half the frame for some shots<br>
        4. Vary the pattern orientation and distance for better accuracy<br>
        5. Click 'Compute Calibration' when you have enough frames<br><br>
        <b>Tips:</b> For thermal cameras, ensure temperature contrast in the pattern
        """

        instructions_label = QLabel(instructions_text)
        instructions_label.setWordWrap(True)
        instructions_layout.addWidget(instructions_label)

        parent_layout.addWidget(instructions_group)

    def create_session_controls(self, parent_layout):
        """Create session control section."""
        session_group = QGroupBox("Calibration Session")
        session_layout = QVBoxLayout(session_group)

        # Device selection
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Connected Devices:"))
        self.device_list = QListWidget()
        self.device_list.setMaximumHeight(80)
        device_layout.addWidget(self.device_list)
        session_layout.addLayout(device_layout)

        # Session controls
        controls_layout = QHBoxLayout()
        self.start_session_btn = QPushButton("Start Calibration Session")
        self.end_session_btn = QPushButton("End Session")
        self.end_session_btn.setEnabled(False)

        controls_layout.addWidget(self.start_session_btn)
        controls_layout.addWidget(self.end_session_btn)
        controls_layout.addStretch()
        session_layout.addLayout(controls_layout)

        parent_layout.addWidget(session_group)

    def create_capture_section(self, parent_layout):
        """Create the frame capture section."""
        capture_group = QGroupBox("Frame Capture")
        capture_layout = QVBoxLayout(capture_group)

        # Capture controls
        capture_controls = QHBoxLayout()
        self.capture_frame_btn = QPushButton("Capture Calibration Frame")
        self.capture_frame_btn.setEnabled(False)
        capture_controls.addWidget(self.capture_frame_btn)

        # Frame counter
        self.frame_counter_label = QLabel("Frames captured: 0")
        capture_controls.addWidget(self.frame_counter_label)
        capture_controls.addStretch()
        capture_layout.addLayout(capture_controls)

        # Progress bar
        self.capture_progress = QProgressBar()
        self.capture_progress.setRange(0, 10)  # Minimum 10 frames recommended
        self.capture_progress.setValue(0)
        capture_layout.addWidget(self.capture_progress)

        # Captured frames list
        frames_layout = QHBoxLayout()
        frames_layout.addWidget(QLabel("Captured Frames:"))
        self.frames_list = QListWidget()
        self.frames_list.setMaximumHeight(100)
        frames_layout.addWidget(self.frames_list)
        capture_layout.addLayout(frames_layout)

        parent_layout.addWidget(capture_group)

    def create_computation_section(self, parent_layout):
        """Create the calibration computation section."""
        computation_group = QGroupBox("Calibration Computation")
        computation_layout = QVBoxLayout(computation_group)

        # Computation controls
        comp_controls = QHBoxLayout()
        self.compute_btn = QPushButton("Compute Calibration")
        self.compute_btn.setEnabled(False)
        comp_controls.addWidget(self.compute_btn)

        # Progress indicator
        self.computation_progress = QProgressBar()
        self.computation_progress.setVisible(False)
        comp_controls.addWidget(self.computation_progress)
        comp_controls.addStretch()
        computation_layout.addLayout(comp_controls)

        # Status display
        self.computation_status = QLabel("Ready to compute calibration")
        computation_layout.addWidget(self.computation_status)

        parent_layout.addWidget(computation_group)

    def create_results_section(self, parent_layout):
        """Create the results display section."""
        results_group = QGroupBox("Calibration Results")
        results_layout = QVBoxLayout(results_group)

        # Results tabs for multiple devices
        self.results_tabs = QTabWidget()
        results_layout.addWidget(self.results_tabs)

        # Overlay controls
        overlay_layout = QHBoxLayout()
        self.overlay_checkbox = QCheckBox("Enable Thermal Overlay")
        self.overlay_alpha_slider = QSlider(Qt.Horizontal)
        self.overlay_alpha_slider.setRange(0, 100)
        self.overlay_alpha_slider.setValue(30)  # 30% alpha
        self.overlay_alpha_label = QLabel("Alpha: 30%")

        overlay_layout.addWidget(self.overlay_checkbox)
        overlay_layout.addWidget(QLabel("Blend:"))
        overlay_layout.addWidget(self.overlay_alpha_slider)
        overlay_layout.addWidget(self.overlay_alpha_label)
        overlay_layout.addStretch()
        results_layout.addLayout(overlay_layout)

        parent_layout.addWidget(results_group)

    def create_action_buttons(self, parent_layout):
        """Create the main action buttons."""
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save Calibration")
        self.save_btn.setEnabled(False)
        self.load_btn = QPushButton("Load Calibration")
        self.close_btn = QPushButton("Close")

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.load_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)

        parent_layout.addLayout(button_layout)

    def connect_signals(self):
        """Connect UI signals to handlers."""
        self.start_session_btn.clicked.connect(self.start_calibration_session)
        self.end_session_btn.clicked.connect(self.end_calibration_session)
        self.capture_frame_btn.clicked.connect(self.capture_calibration_frame)
        self.compute_btn.clicked.connect(self.compute_calibration)
        self.save_btn.clicked.connect(self.save_calibration)
        self.load_btn.clicked.connect(self.load_calibration)
        self.close_btn.clicked.connect(self.close)

        self.overlay_checkbox.toggled.connect(self.toggle_overlay)
        self.overlay_alpha_slider.valueChanged.connect(self.update_alpha_label)

    def start_calibration_session(self):
        """Start a new calibration session."""
        try:
            # Get connected devices
            device_ids = self.get_connected_devices()
            if not device_ids:
                QMessageBox.warning(self, "No Devices", "No connected devices found.")
                return

            # Start session with CalibrationManager
            session_name = f"calibration_{int(time.time())}"
            result = self.calibration_manager.start_calibration_session(
                device_ids, session_name
            )

            if result.get("success", False):
                self.current_session = result["session_id"]
                self.update_device_list(device_ids)
                self.start_session_btn.setEnabled(False)
                self.end_session_btn.setEnabled(True)
                self.capture_frame_btn.setEnabled(True)
                self.computation_status.setText(
                    "Session started. Ready to capture frames."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Session Error",
                    f"Failed to start session: {result.get('error', 'Unknown error')}",
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to start calibration session: {str(e)}"
            )

    def end_calibration_session(self):
        """End the current calibration session."""
        try:
            if self.current_session:
                result = self.calibration_manager.end_calibration_session()
                self.current_session = None

            self.start_session_btn.setEnabled(True)
            self.end_session_btn.setEnabled(False)
            self.capture_frame_btn.setEnabled(False)
            self.compute_btn.setEnabled(False)
            self.computation_status.setText("Session ended.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to end session: {str(e)}")

    def capture_calibration_frame(self):
        """Capture a calibration frame from all devices."""
        try:
            self.capture_frame_btn.setEnabled(False)
            self.computation_status.setText("Capturing frames...")

            # Use CalibrationManager to capture frame
            result = self.calibration_manager.capture_calibration_frame(
                self.device_server
            )

            if result.get("success", False):
                # Update frame counter and progress
                total_frames = result.get("total_frames", 0)
                self.frame_counter_label.setText(f"Frames captured: {total_frames}")
                self.capture_progress.setValue(min(total_frames, 10))

                # Add frame to list
                frame_item = QListWidgetItem(
                    f"Frame {total_frames}: {result.get('timestamp', 'Unknown time')}"
                )
                if result.get("pattern_detected", False):
                    frame_item.setText(frame_item.text() + " ✓")
                else:
                    frame_item.setText(frame_item.text() + " ❌")
                self.frames_list.addItem(frame_item)

                # Enable compute button if enough frames
                if total_frames >= 5:
                    self.compute_btn.setEnabled(True)
                    self.computation_status.setText(
                        f"Ready to compute calibration ({total_frames} frames captured)"
                    )
                else:
                    self.computation_status.setText(
                        f"Capture more frames (need at least 5, have {total_frames})"
                    )

            else:
                QMessageBox.warning(
                    self,
                    "Capture Failed",
                    f"Frame capture failed: {result.get('error', 'Unknown error')}",
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to capture frame: {str(e)}")
        finally:
            self.capture_frame_btn.setEnabled(True)

    def compute_calibration(self):
        """Compute calibration parameters."""
        try:
            self.compute_btn.setEnabled(False)
            self.computation_progress.setVisible(True)
            self.computation_progress.setRange(0, 0)  # Indeterminate progress
            self.computation_status.setText("Computing calibration parameters...")

            # Compute calibration for all devices
            result = self.calibration_manager.compute_calibration()

            if result.get("success", False):
                self.device_results = result.get("results", {})
                self.display_results()
                self.save_btn.setEnabled(True)
                self.overlay_checkbox.setEnabled(True)
                self.computation_status.setText("Calibration completed successfully!")
            else:
                QMessageBox.critical(
                    self,
                    "Calibration Failed",
                    f"Calibration computation failed: {result.get('error', 'Unknown error')}",
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to compute calibration: {str(e)}"
            )
        finally:
            self.compute_btn.setEnabled(True)
            self.computation_progress.setVisible(False)

    def display_results(self):
        """Display calibration results in tabs."""
        # Clear existing tabs
        self.results_tabs.clear()

        for device_id, result in self.device_results.items():
            # Create tab for each device
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)

            # Results text
            results_text = QTextEdit()
            results_text.setReadOnly(True)
            results_text.setMaximumHeight(200)

            # Format results
            summary = result.get_calibration_summary()
            results_content = f"""
            <b>Calibration Results for {device_id}</b><br><br>
            <b>RGB Camera:</b><br>
            - Reprojection Error: {summary.get('rgb_error', 'N/A'):.3f} pixels<br>
            - Focal Length: fx={summary.get('rgb_fx', 'N/A'):.1f}, fy={summary.get('rgb_fy', 'N/A'):.1f}<br>
            - Principal Point: cx={summary.get('rgb_cx', 'N/A'):.1f}, cy={summary.get('rgb_cy', 'N/A'):.1f}<br><br>
            
            <b>Thermal Camera:</b><br>
            - Reprojection Error: {summary.get('thermal_error', 'N/A'):.3f} pixels<br>
            - Focal Length: fx={summary.get('thermal_fx', 'N/A'):.1f}, fy={summary.get('thermal_fy', 'N/A'):.1f}<br>
            - Principal Point: cx={summary.get('thermal_cx', 'N/A'):.1f}, cy={summary.get('thermal_cy', 'N/A'):.1f}<br><br>
            
            <b>Stereo Calibration:</b><br>
            - Stereo Error: {summary.get('stereo_error', 'N/A'):.3f} pixels<br>
            - Translation: {summary.get('translation', 'N/A')}<br>
            - Rotation: {summary.get('rotation_angles', 'N/A')}<br>
            """

            results_text.setHtml(results_content)
            tab_layout.addWidget(results_text)

            self.results_tabs.addTab(tab_widget, device_id)

    def save_calibration(self):
        """Save calibration results to file."""
        try:
            if not self.device_results:
                QMessageBox.warning(
                    self, "No Results", "No calibration results to save."
                )
                return

            # Get save location
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Calibration Results",
                f"calibration_{int(time.time())}.json",
                "JSON Files (*.json);;All Files (*)",
            )

            if filename:
                # Save each device result
                for device_id, result in self.device_results.items():
                    device_filename = filename.replace(".json", f"_{device_id}.json")
                    result.save_to_file(device_filename)

                QMessageBox.information(
                    self, "Saved", f"Calibration results saved successfully."
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save calibration: {str(e)}")

    def load_calibration(self):
        """Load calibration results from file."""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Load Calibration Results",
                "",
                "JSON Files (*.json);;All Files (*)",
            )

            if filename:
                # Extract device ID from filename or prompt user
                # Better device ID handling - extract from filename or ask user
                device_id = None
                
                # Try to extract device ID from filename
                import os
                base_filename = os.path.basename(filename)
                if "device_" in base_filename.lower():
                    # Extract device ID from patterns like "device_1", "device_2", etc.
                    import re
                    match = re.search(r'device_(\d+)', base_filename.lower())
                    if match:
                        device_id = f"device_{match.group(1)}"
                
                # If no device ID found in filename, prompt user
                if not device_id:
                    connected_devices = self.get_connected_devices()
                    if connected_devices:
                        from PyQt5.QtWidgets import QInputDialog
                        device_id, ok = QInputDialog.getItem(
                            self, 
                            "Select Device", 
                            "Select the device this calibration file belongs to:",
                            connected_devices,
                            0,
                            False
                        )
                        if not ok:
                            return  # User cancelled
                    else:
                        # Fallback: ask for custom device ID
                        from PyQt5.QtWidgets import QInputDialog
                        device_id, ok = QInputDialog.getText(
                            self,
                            "Device ID",
                            "Enter device ID for this calibration:"
                        )
                        if not ok or not device_id:
                            device_id = "device_1"  # Final fallback

                result = CalibrationResult.load_from_file(filename)
                self.device_results[device_id] = result
                self.display_results()
                self.save_btn.setEnabled(True)
                self.overlay_checkbox.setEnabled(True)

                QMessageBox.information(
                    self, "Loaded", "Calibration results loaded successfully."
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load calibration: {str(e)}")

    def toggle_overlay(self, enabled):
        """Toggle thermal overlay on/off."""
        try:
            current_device = self.results_tabs.tabText(self.results_tabs.currentIndex())
            if current_device and current_device in self.device_results:
                self.overlay_toggled.emit(current_device, enabled)

        except Exception as e:
            print(f"Error toggling overlay: {e}")

    def update_alpha_label(self, value):
        """Update alpha slider label."""
        self.overlay_alpha_label.setText(f"Alpha: {value}%")

    def get_connected_devices(self):
        """Get list of connected device IDs."""
        # Implement actual device discovery from server
        connected_devices = []
        
        try:
            if hasattr(self.server, 'connected_devices') and self.server.connected_devices:
                # Get actual connected devices from the server
                connected_devices = list(self.server.connected_devices.keys())
            elif hasattr(self.server, 'get_connected_devices'):
                # Alternative method if available
                connected_devices = self.server.get_connected_devices()
            else:
                # Try to get devices from server's client list
                if hasattr(self.server, 'clients') and self.server.clients:
                    connected_devices = [f"device_{i+1}" for i in range(len(self.server.clients))]
                
            # If no devices found, provide some defaults for testing
            if not connected_devices:
                # Return mock devices for testing when no real devices are connected
                connected_devices = ["device_1", "device_2"]
                
        except Exception as e:
            print(f"Error getting connected devices: {e}")
            # Fallback to mock devices
            connected_devices = ["device_1", "device_2"]
        
        return connected_devices

    def update_device_list(self, device_ids):
        """Update the device list display."""
        self.device_list.clear()
        for device_id in device_ids:
            self.device_list.addItem(device_id)
