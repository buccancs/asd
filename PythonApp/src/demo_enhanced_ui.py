#!/usr/bin/env python3
"""
Demo for Enhanced UI Main Window
Demonstrates the PsychoPy-inspired interface improvements

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
Enhancement: PsychoPy-Inspired UI Demo
"""

import os
import sys

# Set environment for headless operation
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from gui.enhanced_ui_main_window import EnhancedMainWindow


def create_enhanced_ui_demo():
    """Create and demonstrate the enhanced UI"""
    
    print("Creating PsychoPy-inspired Enhanced UI demo...")
    
    # Create application
    app = QApplication([])
    app.setStyle("Fusion")
    
    # Create enhanced main window
    window = EnhancedMainWindow()
    window.setWindowTitle("Multi-Sensor Recording System - Enhanced PsychoPy-Inspired Interface")
    
    # Show the window and process events
    window.show()
    app.processEvents()
    
    # Take screenshot
    screenshot = window.grab()
    screenshot_path = "/tmp/enhanced_ui_psychopy_inspired.png"
    screenshot.save(screenshot_path)
    print(f"Enhanced UI screenshot saved to: {screenshot_path}")
    
    # Simulate some activity for a more realistic demo
    # Connect devices
    window.connect_all_devices()
    app.processEvents()
    
    # Simulate calibration
    window.start_calibration()
    app.processEvents()
    
    # Simulate recording
    window.start_recording()
    app.processEvents()
    
    # Take another screenshot showing active state
    screenshot_active = window.grab()
    screenshot_active_path = "/tmp/enhanced_ui_active_state.png"
    screenshot_active.save(screenshot_active_path)
    print(f"Active state screenshot saved to: {screenshot_active_path}")
    
    # Cleanup
    window.close()
    app.quit()
    
    return True


if __name__ == "__main__":
    try:
        success = create_enhanced_ui_demo()
        if success:
            print("✓ Enhanced UI demo completed successfully")
        else:
            print("✗ Enhanced UI demo failed")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error creating enhanced UI demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)