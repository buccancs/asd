"""
Simplified Main Window for Multi-Sensor Recording System Controller

This module implements a clean, tabbed interface that replaces the complex
navigation structure with a simple, intuitive design focused on the main
functional areas: Recording, Devices, Calibration, and Files.

Author: Multi-Sensor Recording System Team
Date: 2025-08-01
Purpose: Navigation Architecture Redesign - Simplicity and Cleanliness
"""

import logging
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QSplitter,
    QMessageBox,
    QAction,
    QMenuBar,
    QStatusBar,
    QFrame
)

# Import essential components
from .device_panel import DeviceStatusPanel
from .preview_panel import PreviewPanel
from .calibration_dialog import CalibrationDialog
from .common_components import (
    ModernButton, ModernGroupBox, StatusIndicator, 
    ProgressIndicator, LogViewer, ConnectionManager
)


class SimplifiedMainWindow(QMainWindow):
    """
    Simplified main window with clean tabbed interface.
    
    Replaces the complex multi-panel architecture with a simple
    tab-based navigation focusing on core functionality.
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Window setup
        self.setWindowTitle("Multi-Sensor Recording System - Simplified")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize core components
        self.setup_ui()
        self.setup_toolbar()
        self.setup_menu()
        self.setup_status_bar()
        
        self.logger.info("Simplified main window initialized")

    def setup_ui(self):
        """Setup the simplified tabbed user interface."""
        # Central widget with tab layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs for main functional areas
        self.create_recording_tab()
        self.create_devices_tab()
        self.create_calibration_tab()
        self.create_files_tab()
        
        self.logger.info("Simplified UI setup completed")

    def setup_toolbar(self):
        """Setup toolbar with quick access buttons."""
        from PyQt5.QtWidgets import QToolBar
        
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Quick record button
        self.quick_record_button = ModernButton("Quick Record", "success")
        self.quick_record_button.clicked.connect(self.quick_record)
        toolbar.addWidget(self.quick_record_button)
        
        # Quick stop button  
        self.quick_stop_button = ModernButton("Quick Stop", "danger")
        self.quick_stop_button.clicked.connect(self.quick_stop)
        self.quick_stop_button.setEnabled(False)
        toolbar.addWidget(self.quick_stop_button)
        
        toolbar.addSeparator()
        
        # Device status button
        self.device_status_button = ModernButton("Device Status", "info")
        self.device_status_button.clicked.connect(self.show_device_status)
        toolbar.addWidget(self.device_status_button)
        
        # Settings button
        self.settings_button = ModernButton("Settings", "secondary")
        self.settings_button.clicked.connect(self.show_settings)
        toolbar.addWidget(self.settings_button)

    def create_recording_tab(self):
        """Create the main recording control tab using modern components."""
        recording_widget = QWidget()
        layout = QVBoxLayout(recording_widget)
        
        # Title using modern styling
        title = QLabel("Recording Control")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Create splitter for better layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Controls using modern group box
        controls_group = ModernGroupBox("Recording Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Recording buttons using modern button components
        self.start_recording_button = ModernButton("Start Recording", "success")
        self.start_recording_button.clicked.connect(self.start_recording)
        controls_layout.addWidget(self.start_recording_button)
        
        self.stop_recording_button = ModernButton("Stop Recording", "danger")
        self.stop_recording_button.setEnabled(False)
        self.stop_recording_button.clicked.connect(self.stop_recording)
        controls_layout.addWidget(self.stop_recording_button)
        
        # Additional recording controls
        self.preview_toggle_button = ModernButton("Toggle Preview", "secondary")
        self.preview_toggle_button.clicked.connect(self.toggle_preview)
        controls_layout.addWidget(self.preview_toggle_button)
        
        self.session_settings_button = ModernButton("Session Settings", "secondary")
        self.session_settings_button.clicked.connect(self.show_session_settings)
        controls_layout.addWidget(self.session_settings_button)
        
        # Status indicators
        self.recording_status_indicator = StatusIndicator("Recording Status")
        self.recording_status_indicator.set_status(False, "Ready to record")
        controls_layout.addWidget(self.recording_status_indicator)
        
        self.preview_status_indicator = StatusIndicator("Preview Status")
        self.preview_status_indicator.set_status(True, "Preview active")
        controls_layout.addWidget(self.preview_status_indicator)
        
        self.storage_space_indicator = StatusIndicator("Storage Space")
        self.storage_space_indicator.set_status(True, "85% available")
        controls_layout.addWidget(self.storage_space_indicator)
        
        # Progress indicator for recording operations
        self.progress_indicator = ProgressIndicator("Session Progress")
        controls_layout.addWidget(self.progress_indicator)
        
        controls_layout.addStretch()
        
        # Right side - Preview
        preview_group = ModernGroupBox("Live Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_panel = PreviewPanel(self)
        preview_layout.addWidget(self.preview_panel)
        
        # Add to splitter
        splitter.addWidget(controls_group)
        splitter.addWidget(preview_group)
        splitter.setSizes([300, 700])  # Give more space to preview
        
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(recording_widget, "Recording")

    def create_devices_tab(self):
        """Create the device management tab using modern components."""
        devices_widget = QWidget()
        layout = QVBoxLayout(devices_widget)
        
        # Title
        title = QLabel("Device Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Device connection managers
        devices_group = ModernGroupBox("Connected Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        # Create connection managers for different device types
        self.connect_pc_button = ConnectionManager("PC Controller")
        self.connect_pc_button.connectionRequested.connect(lambda: self.connect_device("PC"))
        self.connect_pc_button.disconnectionRequested.connect(lambda: self.disconnect_device("PC"))
        devices_layout.addWidget(self.connect_pc_button)
        
        self.connect_android_button = ConnectionManager("Android Devices")
        self.connect_android_button.connectionRequested.connect(lambda: self.connect_device("Android"))
        self.connect_android_button.disconnectionRequested.connect(lambda: self.disconnect_device("Android"))
        devices_layout.addWidget(self.connect_android_button)
        
        self.connect_shimmer_button = ConnectionManager("Shimmer Sensors")
        self.connect_shimmer_button.connectionRequested.connect(lambda: self.connect_device("Shimmer"))
        self.connect_shimmer_button.disconnectionRequested.connect(lambda: self.disconnect_device("Shimmer"))
        devices_layout.addWidget(self.connect_shimmer_button)
        
        layout.addWidget(devices_group)
        
        # Device scanning controls
        scanning_group = ModernGroupBox("Device Discovery")
        scanning_layout = QHBoxLayout(scanning_group)
        
        self.scan_devices_button = ModernButton("Scan for Devices", "primary")
        self.scan_devices_button.clicked.connect(self.scan_devices)
        scanning_layout.addWidget(self.scan_devices_button)
        
        self.refresh_devices_button = ModernButton("Refresh Device List", "secondary")
        self.refresh_devices_button.clicked.connect(self.refresh_devices)
        scanning_layout.addWidget(self.refresh_devices_button)
        
        scanning_layout.addStretch()
        layout.addWidget(scanning_group)
        
        # Global connection controls
        controls_group = ModernGroupBox("Global Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        connect_all_button = ModernButton("Connect All", "success")
        connect_all_button.clicked.connect(self.connect_all_devices)
        controls_layout.addWidget(connect_all_button)
        
        disconnect_all_button = ModernButton("Disconnect All", "danger")
        disconnect_all_button.clicked.connect(self.disconnect_all_devices)
        controls_layout.addWidget(disconnect_all_button)
        
        controls_layout.addStretch()
        layout.addWidget(controls_group)
        
        # Device status indicators
        status_group = ModernGroupBox("Device Status")
        status_layout = QVBoxLayout(status_group)
        
        self.pc_connection_indicator = StatusIndicator("PC Controller")
        self.pc_connection_indicator.set_status(True, "Connected")
        status_layout.addWidget(self.pc_connection_indicator)
        
        self.android_connection_indicator = StatusIndicator("Android Devices")
        self.android_connection_indicator.set_status(False, "No devices connected")
        status_layout.addWidget(self.android_connection_indicator)
        
        self.shimmer_connection_indicator = StatusIndicator("Shimmer Sensors")
        self.shimmer_connection_indicator.set_status(False, "No sensors connected")
        status_layout.addWidget(self.shimmer_connection_indicator)
        
        self.device_count_indicator = StatusIndicator("Device Count")
        self.device_count_indicator.set_status(True, "1 device connected")
        status_layout.addWidget(self.device_count_indicator)
        
        layout.addWidget(status_group)
        layout.addStretch()
        
        self.tab_widget.addTab(devices_widget, "Devices")

    def create_calibration_tab(self):
        """Create the calibration tab using modern components."""
        calibration_widget = QWidget()
        layout = QVBoxLayout(calibration_widget)
        
        # Title
        title = QLabel("Camera Calibration")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Calibration controls group
        calibration_group = ModernGroupBox("Calibration Controls")
        calibration_layout = QVBoxLayout(calibration_group)
        
        # Main calibration controls
        main_controls_layout = QHBoxLayout()
        
        # Primary calibration button
        self.start_calibration_button = ModernButton("Run Calibration", "primary")
        self.start_calibration_button.clicked.connect(self.run_calibration)
        main_controls_layout.addWidget(self.start_calibration_button)
        
        # Load/Save calibration buttons
        self.load_calibration_button = ModernButton("Load Calibration", "secondary")
        self.load_calibration_button.clicked.connect(self.load_calibration)
        main_controls_layout.addWidget(self.load_calibration_button)
        
        self.save_calibration_button = ModernButton("Save Calibration", "secondary")
        self.save_calibration_button.clicked.connect(self.save_calibration)
        main_controls_layout.addWidget(self.save_calibration_button)
        
        main_controls_layout.addStretch()
        calibration_layout.addLayout(main_controls_layout)
        
        # Secondary controls
        secondary_controls_layout = QHBoxLayout()
        
        self.calibration_settings_button = ModernButton("Calibration Settings", "info")
        self.calibration_settings_button.clicked.connect(self.show_calibration_settings)
        secondary_controls_layout.addWidget(self.calibration_settings_button)
        
        self.view_results_button = ModernButton("View Results", "info")
        self.view_results_button.clicked.connect(self.view_calibration_results)
        secondary_controls_layout.addWidget(self.view_results_button)
        
        secondary_controls_layout.addStretch()
        calibration_layout.addLayout(secondary_controls_layout)
        
        layout.addWidget(calibration_group)
        
        # Calibration status group
        status_group = ModernGroupBox("Calibration Status")
        status_layout = QVBoxLayout(status_group)
        
        # Status indicators
        self.calibration_status_indicator = StatusIndicator("Calibration Status")
        self.calibration_status_indicator.set_status(False, "Ready for calibration")
        status_layout.addWidget(self.calibration_status_indicator)
        
        # Progress indicator
        self.calibration_progress_indicator = ProgressIndicator("Calibration Progress")
        status_layout.addWidget(self.calibration_progress_indicator)
        
        # Quality indicator
        self.calibration_quality_indicator = StatusIndicator("Calibration Quality")
        self.calibration_quality_indicator.set_status(False, "No calibration data")
        status_layout.addWidget(self.calibration_quality_indicator)
        
        layout.addWidget(status_group)
        layout.addStretch()
        
        self.tab_widget.addTab(calibration_widget, "Calibration")

    def create_files_tab(self):
        """Create the files management tab using modern components."""
        files_widget = QWidget()
        layout = QVBoxLayout(files_widget)
        
        # Title
        title = QLabel("File Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # File operations group
        operations_group = ModernGroupBox("File Operations")
        operations_layout = QHBoxLayout(operations_group)
        
        self.export_data_button = ModernButton("Export Data", "primary")
        self.export_data_button.clicked.connect(self.export_data)
        operations_layout.addWidget(self.export_data_button)
        
        self.open_folder_button = ModernButton("Open Recordings Folder", "secondary")
        self.open_folder_button.clicked.connect(self.open_recordings_folder)
        operations_layout.addWidget(self.open_folder_button)
        
        self.delete_session_button = ModernButton("Delete Session", "danger")
        self.delete_session_button.clicked.connect(self.delete_session)
        operations_layout.addWidget(self.delete_session_button)
        
        operations_layout.addStretch()
        layout.addWidget(operations_group)
        
        # Additional file operations
        advanced_ops_group = ModernGroupBox("Advanced Operations")
        advanced_ops_layout = QHBoxLayout(advanced_ops_group)
        
        self.browse_files_button = ModernButton("Browse Files", "info")
        self.browse_files_button.clicked.connect(self.browse_files)
        advanced_ops_layout.addWidget(self.browse_files_button)
        
        self.compress_files_button = ModernButton("Compress Files", "info")
        self.compress_files_button.clicked.connect(self.compress_files)
        advanced_ops_layout.addWidget(self.compress_files_button)
        
        advanced_ops_layout.addStretch()
        layout.addWidget(advanced_ops_group)
        
        # File status indicators
        status_group = ModernGroupBox("Storage Status")
        status_layout = QVBoxLayout(status_group)
        
        self.file_count_indicator = StatusIndicator("File Count")
        self.file_count_indicator.set_status(True, "23 files")
        status_layout.addWidget(self.file_count_indicator)
        
        self.storage_usage_indicator = StatusIndicator("Storage Usage")
        self.storage_usage_indicator.set_status(True, "4.2 GB used")
        status_layout.addWidget(self.storage_usage_indicator)
        
        self.export_status_indicator = StatusIndicator("Export Status")
        self.export_status_indicator.set_status(False, "No export in progress")
        status_layout.addWidget(self.export_status_indicator)
        
        layout.addWidget(status_group)
        
        # System log viewer
        log_group = ModernGroupBox("System Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_viewer = LogViewer("Recent Activity")
        log_layout.addWidget(self.log_viewer)
        
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(files_widget, "Files")

    def setup_menu(self):
        """Setup comprehensive menu bar with all required menus."""
        menubar = self.menuBar()
        
        # File menu
        self.file_menu = menubar.addMenu('File')
        
        new_session_action = QAction('New Session', self)
        new_session_action.triggered.connect(self.new_session)
        self.file_menu.addAction(new_session_action)
        
        open_session_action = QAction('Open Session', self)
        open_session_action.triggered.connect(self.open_session)
        self.file_menu.addAction(open_session_action)
        
        save_session_action = QAction('Save Session', self)
        save_session_action.triggered.connect(self.save_session)
        self.file_menu.addAction(save_session_action)
        
        self.file_menu.addSeparator()
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings)
        self.file_menu.addAction(settings_action)
        
        self.file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)
        
        # Edit menu
        self.edit_menu = menubar.addMenu('Edit')
        
        undo_action = QAction('Undo', self)
        undo_action.triggered.connect(self.undo_action)
        self.edit_menu.addAction(undo_action)
        
        redo_action = QAction('Redo', self)
        redo_action.triggered.connect(self.redo_action)
        self.edit_menu.addAction(redo_action)
        
        self.edit_menu.addSeparator()
        
        copy_action = QAction('Copy', self)
        copy_action.triggered.connect(self.copy_action)
        self.edit_menu.addAction(copy_action)
        
        paste_action = QAction('Paste', self)
        paste_action.triggered.connect(self.paste_action)
        self.edit_menu.addAction(paste_action)
        
        # View menu
        self.view_menu = menubar.addMenu('View')
        
        fullscreen_action = QAction('Toggle Fullscreen', self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.view_menu.addAction(fullscreen_action)
        
        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.triggered.connect(self.zoom_in)
        self.view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.triggered.connect(self.zoom_out)
        self.view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction('Reset Zoom', self)
        reset_zoom_action.triggered.connect(self.reset_zoom)
        self.view_menu.addAction(reset_zoom_action)
        
        # Tools menu
        self.tools_menu = menubar.addMenu('Tools')
        
        device_manager_action = QAction('Device Manager', self)
        device_manager_action.triggered.connect(self.show_device_manager)
        self.tools_menu.addAction(device_manager_action)
        
        calibration_tool_action = QAction('Calibration Tool', self)
        calibration_tool_action.triggered.connect(self.show_calibration_tool)
        self.tools_menu.addAction(calibration_tool_action)
        
        data_viewer_action = QAction('Data Viewer', self)
        data_viewer_action.triggered.connect(self.show_data_viewer)
        self.tools_menu.addAction(data_viewer_action)
        
        self.tools_menu.addSeparator()
        
        preferences_action = QAction('Preferences', self)
        preferences_action.triggered.connect(self.show_preferences)
        self.tools_menu.addAction(preferences_action)
        
        # Help menu
        self.help_menu = menubar.addMenu('Help')
        
        documentation_action = QAction('Documentation', self)
        documentation_action.triggered.connect(self.show_documentation)
        self.help_menu.addAction(documentation_action)
        
        shortcuts_action = QAction('Keyboard Shortcuts', self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        self.help_menu.addAction(shortcuts_action)
        
        self.help_menu.addSeparator()
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(about_action)

    def setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    # Action methods using modern components
    def start_recording(self):
        """Start recording session with enhanced feedback."""
        self.start_recording_button.setEnabled(False)
        self.stop_recording_button.setEnabled(True)
        self.recording_status_indicator.set_status(True, "Recording in progress...")
        self.progress_indicator.set_indeterminate(True)
        self.status_bar.showMessage("Recording started")
        self.logger.info("Recording started")
        
        # Update toolbar buttons
        if hasattr(self, 'quick_record_button'):
            self.quick_record_button.setEnabled(False)
        if hasattr(self, 'quick_stop_button'):
            self.quick_stop_button.setEnabled(True)
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Recording session started", "INFO")

    def stop_recording(self):
        """Stop recording session with enhanced feedback."""
        self.start_recording_button.setEnabled(True)
        self.stop_recording_button.setEnabled(False)
        self.recording_status_indicator.set_status(False, "Recording stopped")
        self.progress_indicator.set_indeterminate(False)
        self.progress_indicator.set_progress(100, "Session complete")
        self.status_bar.showMessage("Recording stopped")
        self.logger.info("Recording stopped")
        
        # Update toolbar buttons
        if hasattr(self, 'quick_record_button'):
            self.quick_record_button.setEnabled(True)
        if hasattr(self, 'quick_stop_button'):
            self.quick_stop_button.setEnabled(False)
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Recording session stopped", "INFO")

    def connect_device(self, device_type):
        """Connect to a specific device type."""
        self.status_bar.showMessage(f"Connecting to {device_type}...")
        self.logger.info(f"{device_type} connection initiated")
        
        # Simulate connection process
        QTimer.singleShot(1500, lambda: self.connection_complete(device_type, True))
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry(f"Connecting to {device_type}", "INFO")

    def disconnect_device(self, device_type):
        """Disconnect from a specific device type."""
        self.status_bar.showMessage(f"Disconnecting from {device_type}...")
        self.logger.info(f"{device_type} disconnection initiated")
        
        # Update connection manager
        if device_type == "PC" and hasattr(self, 'connect_pc_button'):
            self.connect_pc_button.set_connection_status(False, "Disconnected")
            self.pc_connection_indicator.set_status(False, "Disconnected")
        elif device_type == "Android" and hasattr(self, 'connect_android_button'):
            self.connect_android_button.set_connection_status(False, "Disconnected")
            self.android_connection_indicator.set_status(False, "Disconnected")
        elif device_type == "Shimmer" and hasattr(self, 'connect_shimmer_button'):
            self.connect_shimmer_button.set_connection_status(False, "Disconnected")
            self.shimmer_connection_indicator.set_status(False, "Disconnected")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry(f"Disconnected from {device_type}", "INFO")

    def connection_complete(self, device_type, success):
        """Handle connection completion."""
        if success:
            status_text = "Connected"
            log_level = "INFO"
            message = f"Connected to {device_type}"
        else:
            status_text = "Connection failed"
            log_level = "ERROR"
            message = f"Failed to connect to {device_type}"
        
        # Update appropriate connection manager
        if device_type == "PC" and hasattr(self, 'connect_pc_button'):
            self.connect_pc_button.set_connection_status(success, status_text)
            self.pc_connection_indicator.set_status(success, status_text)
        elif device_type == "Android" and hasattr(self, 'connect_android_button'):
            self.connect_android_button.set_connection_status(success, status_text)
            self.android_connection_indicator.set_status(success, status_text)
        elif device_type == "Shimmer" and hasattr(self, 'connect_shimmer_button'):
            self.connect_shimmer_button.set_connection_status(success, status_text)
            self.shimmer_connection_indicator.set_status(success, status_text)
        
        self.status_bar.showMessage(message)
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry(message, log_level)

    def connect_all_devices(self):
        """Connect to all devices sequentially."""
        self.logger.info("Connecting to all devices")
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Initiating connection to all devices", "INFO")
        
        # Connect to devices in sequence
        device_types = ["PC", "Android", "Shimmer"]
        for i, device_type in enumerate(device_types):
            QTimer.singleShot(i * 1000, lambda dt=device_type: self.connect_device(dt))

    def disconnect_all_devices(self):
        """Disconnect from all devices."""
        self.logger.info("Disconnecting from all devices")
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Disconnecting from all devices", "INFO")
        
        device_types = ["PC", "Android", "Shimmer"]
        for device_type in device_types:
            self.disconnect_device(device_type)

    def run_calibration(self):
        """Run calibration process with enhanced feedback."""
        self.calibration_status_indicator.set_status(True, "Running calibration...")
        self.calibration_progress_indicator.set_progress(0, "Starting calibration...")
        self.status_bar.showMessage("Calibration in progress...")
        self.logger.info("Calibration started")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Camera calibration started", "INFO")
        
        # Simulate calibration progress
        self.calibration_timer = QTimer()
        self.calibration_step = 0
        self.calibration_timer.timeout.connect(self.update_calibration_progress)
        self.calibration_timer.start(200)  # Update every 200ms

    def update_calibration_progress(self):
        """Update calibration progress indicators."""
        self.calibration_step += 1
        progress = min(100, self.calibration_step * 5)
        
        if progress < 100:
            self.calibration_progress_indicator.set_progress(progress, f"Calibrating... {progress}%")
        else:
            self.calibration_timer.stop()
            self.calibration_complete()

    def calibration_complete(self):
        """Handle calibration completion with enhanced feedback."""
        self.calibration_status_indicator.set_status(False, "Calibration completed successfully")
        self.calibration_progress_indicator.set_progress(100, "Calibration complete")
        self.calibration_quality_indicator.set_status(True, "Quality: Excellent")
        self.status_bar.showMessage("Calibration complete")
        self.logger.info("Calibration completed")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Camera calibration completed successfully", "INFO")

    def open_recordings_folder(self):
        """Open recordings folder with enhanced feedback."""
        self.status_bar.showMessage("Opening recordings folder...")
        self.logger.info("Opening recordings folder")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Opening recordings folder", "INFO")

    def export_data(self):
        """Export recorded data with enhanced feedback."""
        self.status_bar.showMessage("Exporting data...")
        self.logger.info("Data export initiated")
        
        # Add log entry
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Data export initiated", "INFO")

    def show_settings(self):
        """Show settings dialog."""
        QMessageBox.information(self, "Settings", "Settings dialog - Coming soon!")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About",
            "Multi-Sensor Recording System\n"
            "Simplified Navigation Architecture\n"
            "Version 1.0.0\n\n"
            "Focus: Simplicity and Cleanliness"
        )

    # Additional Recording Tab Actions
    def toggle_preview(self):
        """Toggle preview display."""
        if hasattr(self, 'preview_panel'):
            # Toggle preview state
            current_status = self.preview_status_indicator.is_connected
            new_status = not current_status
            self.preview_status_indicator.set_status(new_status, 
                "Preview active" if new_status else "Preview inactive")
            self.status_bar.showMessage(f"Preview {'enabled' if new_status else 'disabled'}")
            self.logger.info(f"Preview {'enabled' if new_status else 'disabled'}")

    def show_session_settings(self):
        """Show session settings dialog."""
        QMessageBox.information(self, "Session Settings", 
                              "Session settings dialog would open here.\n"
                              "Configure recording parameters, file formats, etc.")

    # Additional Device Tab Actions
    def scan_devices(self):
        """Scan for available devices."""
        self.status_bar.showMessage("Scanning for devices...")
        self.logger.info("Device scan initiated")
        
        # Update device count indicator
        QTimer.singleShot(2000, lambda: self.device_count_indicator.set_status(True, "3 devices found"))
        
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Device scan completed - 3 devices found", "INFO")

    def refresh_devices(self):
        """Refresh device list."""
        self.status_bar.showMessage("Refreshing device list...")
        self.logger.info("Device list refresh initiated")
        
        if hasattr(self, 'log_viewer'):
            self.log_viewer.add_log_entry("Device list refreshed", "INFO")

    # Additional Calibration Tab Actions
    def load_calibration(self):
        """Load existing calibration data."""
        QMessageBox.information(self, "Load Calibration", 
                              "Load calibration dialog would open here.\n"
                              "Select calibration file to load.")
        self.calibration_quality_indicator.set_status(True, "Quality: Good (Loaded)")

    def save_calibration(self):
        """Save current calibration data."""
        QMessageBox.information(self, "Save Calibration", 
                              "Save calibration dialog would open here.\n"
                              "Choose location to save calibration data.")

    def show_calibration_settings(self):
        """Show calibration settings dialog."""
        QMessageBox.information(self, "Calibration Settings", 
                              "Calibration settings dialog would open here.\n"
                              "Configure checkerboard size, detection parameters, etc.")

    def view_calibration_results(self):
        """View calibration results."""
        QMessageBox.information(self, "Calibration Results", 
                              "Calibration results viewer would open here.\n"
                              "Show reprojection error, camera matrix, distortion coefficients.")

    # Additional File Tab Actions
    def delete_session(self):
        """Delete selected session."""
        reply = QMessageBox.question(self, "Delete Session", 
                                   "Are you sure you want to delete the selected session?\n"
                                   "This action cannot be undone.")
        if reply == QMessageBox.Yes:
            self.file_count_indicator.set_status(True, "22 files")
            self.storage_usage_indicator.set_status(True, "3.8 GB used")
            self.logger.info("Session deleted")

    def browse_files(self):
        """Browse and manage files."""
        QMessageBox.information(self, "File Browser", 
                              "File browser dialog would open here.\n"
                              "Navigate and manage recording files.")

    def compress_files(self):
        """Compress files for storage."""
        self.export_status_indicator.set_status(True, "Compressing files...")
        QTimer.singleShot(3000, lambda: self.export_status_indicator.set_status(False, "Compression complete"))
        self.logger.info("File compression started")

    # Toolbar Actions
    def quick_record(self):
        """Quick record action from toolbar."""
        self.start_recording()

    def quick_stop(self):
        """Quick stop action from toolbar."""
        self.stop_recording()

    def show_device_status(self):
        """Show device status overview."""
        QMessageBox.information(self, "Device Status", 
                              "Device Status Overview:\n\n"
                              "PC Controller: Connected\n"
                              "Android Devices: 0 connected\n" 
                              "Shimmer Sensors: 0 connected\n"
                              "USB Webcams: 1 detected")

    # Menu Actions
    def new_session(self):
        """Create new recording session."""
        QMessageBox.information(self, "New Session", "New session created")
        self.logger.info("New session created")

    def open_session(self):
        """Open existing session."""
        QMessageBox.information(self, "Open Session", "Open session dialog would appear here")

    def save_session(self):
        """Save current session."""
        QMessageBox.information(self, "Save Session", "Session saved successfully")

    def undo_action(self):
        """Undo last action."""
        QMessageBox.information(self, "Undo", "Last action undone")

    def redo_action(self):
        """Redo last undone action.""" 
        QMessageBox.information(self, "Redo", "Action redone")

    def copy_action(self):
        """Copy selected content."""
        QMessageBox.information(self, "Copy", "Content copied to clipboard")

    def paste_action(self):
        """Paste content from clipboard."""
        QMessageBox.information(self, "Paste", "Content pasted from clipboard")

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def zoom_in(self):
        """Zoom in preview."""
        QMessageBox.information(self, "Zoom In", "Preview zoomed in")

    def zoom_out(self):
        """Zoom out preview."""
        QMessageBox.information(self, "Zoom Out", "Preview zoomed out")

    def reset_zoom(self):
        """Reset preview zoom."""
        QMessageBox.information(self, "Reset Zoom", "Preview zoom reset")

    def show_device_manager(self):
        """Show device manager tool."""
        QMessageBox.information(self, "Device Manager", "Device manager tool would open here")

    def show_calibration_tool(self):
        """Show calibration tool."""
        QMessageBox.information(self, "Calibration Tool", "Calibration tool would open here")

    def show_data_viewer(self):
        """Show data viewer tool."""
        QMessageBox.information(self, "Data Viewer", "Data viewer tool would open here")

    def show_preferences(self):
        """Show preferences dialog."""
        QMessageBox.information(self, "Preferences", "Preferences dialog would open here")

    def show_documentation(self):
        """Show documentation."""
        QMessageBox.information(self, "Documentation", "Documentation would open here")

    def show_shortcuts(self):
        """Show keyboard shortcuts."""
        QMessageBox.information(self, "Keyboard Shortcuts", 
                              "Keyboard Shortcuts:\n\n"
                              "Ctrl+R: Start Recording\n"
                              "Ctrl+S: Stop Recording\n"
                              "Ctrl+D: Device Manager\n"
                              "Ctrl+C: Calibration\n"
                              "F11: Toggle Fullscreen")

    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Application closing")
        event.accept()