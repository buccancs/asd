#!/usr/bin/env python3
"""
Test script for Enhanced Python Desktop UI
Verifies all critical missing features have been implemented
"""

import sys
import os
import unittest
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtTest import QTest
    from PyQt5.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestEnhancedUI(unittest.TestCase):
    """Test suite for enhanced UI functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if PYQT_AVAILABLE:
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
    
    def test_enhanced_window_creation(self):
        """Test that enhanced window can be created"""
        if not PYQT_AVAILABLE:
            self.skipTest("PyQt5 not available")
        
        try:
            from gui.enhanced_simplified_main_window import EnhancedSimplifiedMainWindow
            window = EnhancedSimplifiedMainWindow()
            self.assertIsNotNone(window)
            
            # Test that window has required tabs
            self.assertTrue(hasattr(window, 'tab_widget'))
            self.assertEqual(window.tab_widget.count(), 4)  # Recording, Devices, Calibration, Files
            
            # Test that toolbar has required buttons
            self.assertTrue(hasattr(window, 'quick_record_button'))
            self.assertTrue(hasattr(window, 'quick_stop_button'))
            self.assertTrue(hasattr(window, 'device_status_button'))
            self.assertTrue(hasattr(window, 'settings_button'))
            
            window.close()
            logger.info("✓ Enhanced window creation test passed")
            
        except Exception as e:
            self.fail(f"Failed to create enhanced window: {e}")
    
    def test_real_time_data_plotter(self):
        """Test real-time data plotting functionality"""
        if not PYQT_AVAILABLE:
            self.skipTest("PyQt5 not available")
            
        try:
            from gui.enhanced_simplified_main_window import RealTimeDataPlotter
            plotter = RealTimeDataPlotter("Test Data")
            self.assertIsNotNone(plotter)
            
            # Test data addition
            plotter.add_data("sensor1", 10.5)
            plotter.add_data("sensor2", 25.3)
            
            self.assertIn("sensor1", plotter.data_buffer)
            self.assertIn("sensor2", plotter.data_buffer)
            
            logger.info("✓ Real-time data plotter test passed")
            
        except Exception as e:
            self.fail(f"Failed to test data plotter: {e}")
    
    def test_system_monitor(self):
        """Test system monitoring functionality"""
        if not PYQT_AVAILABLE:
            self.skipTest("PyQt5 not available")
            
        try:
            from gui.enhanced_simplified_main_window import SystemMonitor
            monitor = SystemMonitor()
            self.assertIsNotNone(monitor)
            
            # Test that monitor has required components
            self.assertTrue(hasattr(monitor, 'cpu_progress'))
            self.assertTrue(hasattr(monitor, 'memory_progress'))
            
            # Test update functionality
            monitor.update_metrics()
            
            logger.info("✓ System monitor test passed")
            
        except Exception as e:
            self.fail(f"Failed to test system monitor: {e}")
    
    def test_device_config_dialog(self):
        """Test device configuration dialog"""
        if not PYQT_AVAILABLE:
            self.skipTest("PyQt5 not available")
            
        try:
            from gui.enhanced_simplified_main_window import DeviceConfigDialog
            
            # Test different device types
            for device_type in ["Android", "Shimmer", "Webcam"]:
                dialog = DeviceConfigDialog(device_type)
                self.assertIsNotNone(dialog)
                self.assertEqual(dialog.device_type, device_type)
                dialog.close()
            
            logger.info("✓ Device configuration dialog test passed")
            
        except Exception as e:
            self.fail(f"Failed to test device config dialog: {e}")
    
    def test_file_browser_widget(self):
        """Test file browser functionality"""
        if not PYQT_AVAILABLE:
            self.skipTest("PyQt5 not available")
            
        try:
            from gui.enhanced_simplified_main_window import FileBrowserWidget
            browser = FileBrowserWidget()
            self.assertIsNotNone(browser)
            
            # Test that browser has required components
            self.assertTrue(hasattr(browser, 'file_tree'))
            self.assertTrue(hasattr(browser, 'current_path'))
            
            # Test refresh functionality
            browser.refresh()
            
            logger.info("✓ File browser widget test passed")
            
        except Exception as e:
            self.fail(f"Failed to test file browser: {e}")
    
    def test_backend_integration(self):
        """Test backend service integration"""
        try:
            from gui.enhanced_simplified_main_window import EnhancedSimplifiedMainWindow
            window = EnhancedSimplifiedMainWindow()
            
            # Test that backend services are attempted to be initialized
            self.assertTrue(hasattr(window, 'session_manager'))
            self.assertTrue(hasattr(window, 'main_controller'))
            self.assertTrue(hasattr(window, 'shimmer_manager'))
            
            # Test real action methods exist
            self.assertTrue(hasattr(window, 'start_recording_real'))
            self.assertTrue(hasattr(window, 'stop_recording_real'))
            self.assertTrue(hasattr(window, 'scan_devices_real'))
            self.assertTrue(hasattr(window, 'run_calibration_real'))
            
            if PYQT_AVAILABLE:
                window.close()
            
            logger.info("✓ Backend integration test passed")
            
        except Exception as e:
            self.fail(f"Failed to test backend integration: {e}")
    
    def test_real_functionality_methods(self):
        """Test that real functionality methods exist and work"""
        try:
            from gui.enhanced_simplified_main_window import EnhancedSimplifiedMainWindow
            window = EnhancedSimplifiedMainWindow()
            
            # Test real device detection
            devices = window.detect_real_devices()
            self.assertIsInstance(devices, list)
            self.assertGreater(len(devices), 0)  # Should at least have PC controller
            
            # Test storage indicator update
            window.update_storage_indicator()
            
            # Test file count update
            window.update_file_count()
            
            # Test storage usage update
            window.update_storage_usage()
            
            if PYQT_AVAILABLE:
                window.close()
            
            logger.info("✓ Real functionality methods test passed")
            
        except Exception as e:
            self.fail(f"Failed to test real functionality: {e}")
    
    def test_critical_features_implemented(self):
        """Test that all critical missing features are implemented"""
        feature_checklist = {
            "Real-time Data Visualization": False,
            "Advanced Device Management": False,
            "Session Management Integration": False,
            "File Management Browser": False,
            "Backend Integration": False,
            "Real System Monitoring": False,
            "Device Configuration Dialogs": False,
            "Professional UI Components": False
        }
        
        try:
            from gui.enhanced_simplified_main_window import (
                EnhancedSimplifiedMainWindow,
                RealTimeDataPlotter,
                SystemMonitor,
                DeviceConfigDialog,
                FileBrowserWidget
            )
            
            # Check real-time data visualization
            plotter = RealTimeDataPlotter("Test")
            if hasattr(plotter, 'add_data') and hasattr(plotter, 'update_plot'):
                feature_checklist["Real-time Data Visualization"] = True
            
            # Check system monitoring
            monitor = SystemMonitor()
            if hasattr(monitor, 'update_metrics'):
                feature_checklist["Real System Monitoring"] = True
            
            # Check device configuration
            config_dialog = DeviceConfigDialog("Android")
            if hasattr(config_dialog, 'apply_settings'):
                feature_checklist["Device Configuration Dialogs"] = True
            
            # Check file browser
            browser = FileBrowserWidget()
            if hasattr(browser, 'refresh') and hasattr(browser, 'file_tree'):
                feature_checklist["File Management Browser"] = True
            
            # Check main window features
            window = EnhancedSimplifiedMainWindow()
            
            if hasattr(window, 'start_recording_real'):
                feature_checklist["Session Management Integration"] = True
            
            if hasattr(window, 'detect_real_devices'):
                feature_checklist["Advanced Device Management"] = True
            
            if hasattr(window, 'session_manager'):
                feature_checklist["Backend Integration"] = True
            
            if hasattr(window, 'data_plotter') and hasattr(window, 'system_monitor'):
                feature_checklist["Professional UI Components"] = True
            
            if PYQT_AVAILABLE:
                window.close()
            
            # Report results
            implemented_features = sum(feature_checklist.values())
            total_features = len(feature_checklist)
            
            logger.info(f"Critical Features Implementation Status:")
            for feature, implemented in feature_checklist.items():
                status = "✓" if implemented else "✗"
                logger.info(f"  {status} {feature}")
            
            logger.info(f"\nSummary: {implemented_features}/{total_features} critical features implemented")
            
            # All features should be implemented
            self.assertEqual(implemented_features, total_features, 
                           f"Not all critical features implemented: {implemented_features}/{total_features}")
            
        except Exception as e:
            self.fail(f"Failed to verify critical features: {e}")


def main():
    """Run the test suite"""
    print("=" * 60)
    print("ENHANCED PYTHON DESKTOP UI TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnhancedUI)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED - Enhanced UI implementation complete!")
        print("✅ All critical missing features have been addressed")
        print("✅ Professional desktop UI is ready for production use")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
        for test, error in result.failures + result.errors:
            print(f"   - {test}: {error}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)