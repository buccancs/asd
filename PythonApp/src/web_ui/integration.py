#!/usr/bin/env python3
"""
Web Dashboard Integration for Multi-Sensor Recording System

This module provides integration between the new web-based dashboard and the existing
PyQt5 desktop application. It allows the desktop application to optionally start
a web server that provides real-time monitoring and control capabilities.

Author: Multi-Sensor Recording System Team
Date: 2025-08-02
"""

import logging
import os
import sys
import time
from typing import Optional, Dict, Any

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from web_ui.web_dashboard import WebDashboardServer
except ImportError:
    WebDashboardServer = None

try:
    from web_ui.web_controller import WebController, create_web_controller_with_real_components
    WEB_CONTROLLER_AVAILABLE = True
except ImportError:
    WebController = None
    create_web_controller_with_real_components = None
    WEB_CONTROLLER_AVAILABLE = False

try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback logging if utils not available
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class WebDashboardIntegration:
    """
    Integration layer between the web dashboard and existing desktop application.
    
    This class provides a bridge that allows the existing PyQt5 application to
    optionally enable web-based monitoring and control without requiring
    significant changes to the existing codebase.
    """
    
    def __init__(self, enable_web_ui: bool = True, web_port: int = 5000, 
                 main_controller=None, session_manager=None, shimmer_manager=None, 
                 android_device_manager=None):
        """
        Initialize the web dashboard integration.
        
        Args:
            enable_web_ui: Whether to enable the web UI (default: True)
            web_port: Port for the web server (default: 5000)
            main_controller: MainController instance from the desktop app (PyQt-based) or None
            session_manager: SessionManager instance from the desktop app
            shimmer_manager: ShimmerManager instance from the desktop app
            android_device_manager: AndroidDeviceManager instance from the desktop app
        """
        self.enable_web_ui = enable_web_ui
        self.web_port = web_port
        self.web_server: Optional[WebDashboardServer] = None
        self.is_running = False
        
        # Determine controller to use (PyQt MainController or WebController)
        if main_controller is not None:
            # Use provided PyQt MainController
            self.controller = main_controller
            self.using_web_controller = False
            logger.info("Using PyQt MainController")
        elif WEB_CONTROLLER_AVAILABLE:
            # Create WebController for web-only environments
            logger.info("Creating WebController for web-only environment")
            self.controller = create_web_controller_with_real_components()
            self.using_web_controller = True
        else:
            logger.error("No controller available")
            self.controller = None
            self.using_web_controller = False
        
        logger.info(f"Web Dashboard Integration initialized (enabled: {enable_web_ui})")
        logger.info(f"Controller: {'WebController' if self.using_web_controller else 'MainController' if self.controller else 'None'}")
    
    def start_web_dashboard(self) -> bool:
        """
        Start the web dashboard server.
        
        Returns:
            True if started successfully, False otherwise
        """
        if not self.enable_web_ui:
            logger.info("Web UI is disabled, not starting dashboard")
            return False
        
        if WebDashboardServer is None:
            logger.error("Web dashboard dependencies not available")
            return False
        
        if self.is_running:
            logger.warning("Web dashboard is already running")
            return True
        
        try:
            # Create and start the web server with controller integration
            self.web_server = WebDashboardServer(
                host='0.0.0.0', 
                port=self.web_port, 
                debug=False,
                controller=self.controller  # Pass controller for network protocol integration
            )
            self.web_server.start_server()
            self.is_running = True
            
            logger.info(f"Web dashboard started on http://localhost:{self.web_port}")
            
            # Connect to controller if available
            if self.controller is not None:
                self._connect_to_controller()
                logger.info(f"Connected web dashboard to {'WebController' if self.using_web_controller else 'MainController'} with network protocol integration")
            else:
                logger.warning("No controller available for real data integration")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start web dashboard: {e}")
            return False
    
    def stop_web_dashboard(self):
        """Stop the web dashboard server."""
        if not self.is_running or not self.web_server:
            return
        
        try:
            # Stop web controller monitoring if we're using it
            if self.using_web_controller and self.controller:
                self.controller.stop_monitoring()
            
            self.web_server.stop_server()
            self.web_server = None
            self.is_running = False
            logger.info("Web dashboard stopped")
        except Exception as e:
            logger.error(f"Error stopping web dashboard: {e}")
    
    def _connect_to_controller(self):
        """Connect to controller signals for real-time updates."""
        if self.controller is None:
            return
        
        try:
            # Connect to controller signals
            self.controller.device_status_received.connect(self._on_device_status_received)
            self.controller.sensor_data_received.connect(self._on_sensor_data_received)
            self.controller.session_status_changed.connect(self._on_session_status_changed)
            
            controller_type = "WebController" if self.using_web_controller else "MainController"
            logger.info(f"Connected to {controller_type} signals")
            
        except Exception as e:
            logger.error(f"Failed to connect to controller signals: {e}")
    
    def _on_device_status_received(self, device_id: str, status_data: dict):
        """Handle device status update signal."""
        if self.is_running and self.web_server:
            device_type = self._determine_device_type(device_id, status_data)
            self.web_server.update_device_status(device_type, device_id, status_data)
    
    def _on_sensor_data_received(self, device_id: str, sensor_data: dict):
        """Handle real-time sensor data."""
        if self.is_running and self.web_server:
            for sensor_type, value in sensor_data.items():
                if isinstance(value, (int, float)):
                    self.web_server.update_sensor_data(device_id, sensor_type, value)
    
    def _on_session_status_changed(self, session_id: str, is_active: bool):
        """Handle session status change signal."""
        if self.is_running and self.web_server:
            session_info = {
                'active': is_active,
                'session_id': session_id if is_active else None,
                'start_time': time.time() if is_active else None
            }
            self.web_server.session_info = session_info
            self.web_server._broadcast_session_update()
    
    def get_web_dashboard_url(self) -> Optional[str]:
        """
        Get the URL of the web dashboard.
        
        Returns:
            Dashboard URL if running, None otherwise
        """
        if self.is_running:
            return f"http://localhost:{self.web_port}"
        return None

    def _determine_device_type(self, device_id: str, status_data: dict) -> str:
        """Determine device type based on ID and status data."""
        device_type = status_data.get('type', '')
        if device_type == 'shimmer' or 'shimmer' in device_id.lower():
            return 'shimmer_sensors'
        elif device_type == 'android' or 'android' in device_id.lower():
            return 'android_devices'
        elif device_type == 'webcam' or 'webcam' in device_id.lower():
            return 'usb_webcams'
        else:
            return 'android_devices'  # Default fallback


# Singleton instance for easy access
_web_integration_instance: Optional[WebDashboardIntegration] = None


def get_web_integration(enable_web_ui: bool = True, web_port: int = 5000, 
                       main_controller=None, session_manager=None, shimmer_manager=None, 
                       android_device_manager=None) -> WebDashboardIntegration:
    """
    Get or create the web dashboard integration instance.
    
    Args:
        enable_web_ui: Whether to enable the web UI
        web_port: Port for the web server
        main_controller: MainController instance from the desktop app
        session_manager: SessionManager instance from the desktop app
        shimmer_manager: ShimmerManager instance from the desktop app
        android_device_manager: AndroidDeviceManager instance from the desktop app
    
    Returns:
        WebDashboardIntegration instance
    """
    global _web_integration_instance
    
    if _web_integration_instance is None:
        _web_integration_instance = WebDashboardIntegration(
            enable_web_ui, web_port, main_controller, session_manager, 
            shimmer_manager, android_device_manager
        )
    
    return _web_integration_instance


def start_web_dashboard(enable_web_ui: bool = True, web_port: int = 5000,
                       main_controller=None, session_manager=None, shimmer_manager=None, 
                       android_device_manager=None) -> bool:
    """
    Convenience function to start the web dashboard.
    
    Args:
        enable_web_ui: Whether to enable the web UI
        web_port: Port for the web server
        main_controller: MainController instance from the desktop app
        session_manager: SessionManager instance from the desktop app
        shimmer_manager: ShimmerManager instance from the desktop app
        android_device_manager: AndroidDeviceManager instance from the desktop app
    
    Returns:
        True if started successfully, False otherwise
    """
    integration = get_web_integration(
        enable_web_ui, web_port, main_controller, session_manager, 
        shimmer_manager, android_device_manager
    )
    return integration.start_web_dashboard()


def stop_web_dashboard():
    """Convenience function to stop the web dashboard."""
    global _web_integration_instance
    
    if _web_integration_instance:
        _web_integration_instance.stop_web_dashboard()


if __name__ == '__main__':
    # Demo mode - start web dashboard with WebController
    print("Starting Web Dashboard Integration Demo...")
    
    integration = WebDashboardIntegration(enable_web_ui=True, web_port=5000)
    
    if integration.start_web_dashboard():
        print(f"Web dashboard available at: {integration.get_web_dashboard_url()}")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping web dashboard...")
            integration.stop_web_dashboard()
            print("Demo completed.")
    else:
        print("Failed to start web dashboard")