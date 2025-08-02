#!/usr/bin/env python3
"""
Web-compatible Main Controller for the Multi-Sensor Recording System.

This module implements a web-compatible version of the MainController that doesn't
depend on PyQt5, allowing the web UI to connect to real application components
even in environments where PyQt5 is not available.

Author: Multi-Sensor Recording System Team
Date: 2025-08-02
"""

import logging
import threading
import time
from typing import Optional, Dict, Any, List, Callable

# Import backend services without PyQt dependencies
try:
    from session.session_manager import SessionManager
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    SessionManager = None
    SESSION_MANAGER_AVAILABLE = False

try:
    from shimmer_manager import ShimmerManager
    SHIMMER_MANAGER_AVAILABLE = True
except ImportError:
    ShimmerManager = None
    SHIMMER_MANAGER_AVAILABLE = False

try:
    from network.android_device_manager import AndroidDeviceManager
    ANDROID_DEVICE_MANAGER_AVAILABLE = True
except ImportError:
    AndroidDeviceManager = None
    ANDROID_DEVICE_MANAGER_AVAILABLE = False

try:
    from network.device_server import JsonSocketServer
    JSON_SOCKET_SERVER_AVAILABLE = True
except ImportError:
    JsonSocketServer = None
    JSON_SOCKET_SERVER_AVAILABLE = False

try:
    from webcam.webcam_capture import WebcamCapture
    WEBCAM_CAPTURE_AVAILABLE = True
except ImportError:
    WebcamCapture = None
    WEBCAM_CAPTURE_AVAILABLE = False

try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class WebSignal:
    """
    Simple signal system for web integration without PyQt dependencies.
    
    This provides the same interface as PyQt signals but works in environments
    where PyQt5 is not available.
    """
    
    def __init__(self):
        self.callbacks = []
    
    def connect(self, callback: Callable):
        """Connect a callback function to this signal."""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def disconnect(self, callback: Callable = None):
        """Disconnect a callback or all callbacks."""
        if callback is None:
            self.callbacks.clear()
        elif callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def emit(self, *args, **kwargs):
        """Emit the signal to all connected callbacks."""
        for callback in self.callbacks:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in signal callback: {e}")


class WebController:
    """
    Web-compatible main controller for the multi-sensor recording system.
    
    This controller provides the same interface as MainController but doesn't
    depend on PyQt5, allowing it to work in web-only environments and connect
    to real backend components.
    """
    
    def __init__(self):
        """Initialize the WebController."""
        # Signals compatible with web integration
        self.server_status_changed = WebSignal()
        self.webcam_status_changed = WebSignal()
        self.session_status_changed = WebSignal()
        self.device_connected = WebSignal()
        self.device_disconnected = WebSignal()
        self.device_status_received = WebSignal()
        self.preview_frame_received = WebSignal()
        self.sensor_data_received = WebSignal()
        self.recording_started = WebSignal()
        self.recording_stopped = WebSignal()
        self.calibration_completed = WebSignal()
        self.error_occurred = WebSignal()
        
        # Backend services
        self.session_manager = None
        self.shimmer_manager = None
        self.android_device_manager = None
        self.json_server = None
        self.webcam_capture = None
        
        # Controller state
        self._server_running = False
        self._current_session_id = None
        self._monitoring_thread = None
        self._running = False
        
        logger.info("WebController initialized")
    
    def inject_dependencies(self, 
                          session_manager=None,
                          shimmer_manager=None,
                          android_device_manager=None,
                          json_server=None,
                          webcam_capture=None):
        """
        Inject backend service dependencies.
        
        Args:
            session_manager: Session management service
            shimmer_manager: Shimmer sensor management service
            android_device_manager: Android device management service
            json_server: Network communication service
            webcam_capture: Webcam capture service
        """
        self.session_manager = session_manager
        self.shimmer_manager = shimmer_manager
        self.android_device_manager = android_device_manager
        self.json_server = json_server
        self.webcam_capture = webcam_capture
        
        # Connect to backend services
        self._connect_to_services()
        
        logger.info("WebController dependencies injected and connected")
    
    def _connect_to_services(self):
        """Connect to backend service events and data streams."""
        # Initialize and start Android device manager (uses network protocols)
        if self.android_device_manager:
            try:
                # Initialize the Android device manager (starts network server on port 9000)
                if self.android_device_manager.initialize():
                    logger.info("AndroidDeviceManager network server started on port 9000")
                    
                    # Connect to device events
                    self.android_device_manager.add_status_callback(self._on_android_device_status)
                    self.android_device_manager.add_data_callback(self._on_android_sensor_data)
                    self.android_device_manager.add_session_callback(self._on_android_session_event)
                    
                    logger.info("Connected to AndroidDeviceManager network protocols")
                else:
                    logger.error("Failed to initialize AndroidDeviceManager network server")
            except Exception as e:
                logger.error(f"Error connecting to AndroidDeviceManager: {e}")
        
        # Connect to shimmer manager
        if self.shimmer_manager:
            try:
                # Initialize shimmer manager if needed
                if hasattr(self.shimmer_manager, 'initialize'):
                    self.shimmer_manager.initialize()
                logger.info("Connected to ShimmerManager")
            except Exception as e:
                logger.error(f"Error connecting to ShimmerManager: {e}")
        
        # Note: JsonSocketServer is redundant since AndroidDeviceManager includes network server
        # We only use AndroidDeviceManager which provides the JSON socket server functionality
    
    def start_monitoring(self):
        """Start monitoring backend services for status updates."""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
        
        self._running = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        
        logger.info("WebController monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring backend services."""
        self._running = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        
        # Cleanup network services
        if self.android_device_manager:
            try:
                self.android_device_manager.shutdown()
                logger.info("AndroidDeviceManager network server stopped")
            except Exception as e:
                logger.error(f"Error stopping AndroidDeviceManager: {e}")
        
        logger.info("WebController monitoring stopped")
    
    def _on_android_device_status(self, device_id: str, android_device):
        """Handle real Android device status updates from network protocols."""
        try:
            # Convert AndroidDevice object to status dict
            status_data = {
                'type': 'android',
                'status': 'connected' if android_device.connected else 'disconnected',
                'battery': android_device.status.get('battery', 0),
                'temperature': android_device.status.get('temperature', 0),
                'storage': android_device.status.get('storage', 0),
                'recording': android_device.is_recording,
                'capabilities': android_device.capabilities,
                'connection_time': android_device.connection_time,
                'messages_received': android_device.messages_received,
                'data_samples': android_device.data_samples_received
            }
            
            # Emit to web dashboard
            self.device_status_received.emit(device_id, status_data)
            logger.debug(f"Real Android device status update: {device_id}")
            
        except Exception as e:
            logger.error(f"Error processing Android device status: {e}")
    
    def _on_android_sensor_data(self, shimmer_data_sample):
        """Handle real Shimmer sensor data from Android devices via network protocols."""
        try:
            # Convert ShimmerDataSample to sensor data dict
            sensor_data = {
                'timestamp': shimmer_data_sample.timestamp,
                'device_id': shimmer_data_sample.android_device_id,
                'shimmer_device_id': shimmer_data_sample.device_id,
                'session_id': shimmer_data_sample.session_id,
                **shimmer_data_sample.sensor_values  # GSR, accelerometer, etc.
            }
            
            # Emit to web dashboard
            self.sensor_data_received.emit(shimmer_data_sample.android_device_id, sensor_data)
            logger.debug(f"Real sensor data from {shimmer_data_sample.android_device_id}")
            
        except Exception as e:
            logger.error(f"Error processing Android sensor data: {e}")
    
    def _on_android_session_event(self, session_info):
        """Handle real session events from Android devices."""
        try:
            session_active = session_info.end_time is None
            session_id = session_info.session_id
            
            # Emit session status change
            self.session_status_changed.emit(session_id, session_active)
            
            if session_active:
                self.recording_started.emit(session_id)
                logger.info(f"Real session started via network: {session_id}")
            else:
                duration = session_info.end_time - session_info.start_time
                self.recording_stopped.emit(session_id, duration)
                logger.info(f"Real session ended via network: {session_id} ({duration:.1f}s)")
                
        except Exception as e:
            logger.error(f"Error processing Android session event: {e}")
    
    def start_recording_session(self, session_id: str) -> bool:
        """Start recording session using real network protocols."""
        try:
            if self.android_device_manager:
                # Use real network protocols to start session on connected Android devices
                success = self.android_device_manager.start_session(
                    session_id=session_id,
                    record_shimmer=True,
                    record_video=True, 
                    record_thermal=True
                )
                
                if success:
                    self._current_session_id = session_id
                    logger.info(f"Started real recording session via network: {session_id}")
                    return True
                else:
                    logger.error(f"Failed to start recording session: {session_id}")
                    return False
            else:
                logger.warning("No AndroidDeviceManager available for real session control")
                return False
                
        except Exception as e:
            logger.error(f"Error starting recording session: {e}")
            return False
    
    def stop_recording_session(self) -> bool:
        """Stop recording session using real network protocols."""
        try:
            if self.android_device_manager and self._current_session_id:
                # Use real network protocols to stop session on connected Android devices
                success = self.android_device_manager.stop_session()
                
                if success:
                    old_session = self._current_session_id
                    self._current_session_id = None
                    logger.info(f"Stopped real recording session via network: {old_session}")
                    return True
                else:
                    logger.error("Failed to stop recording session")
                    return False
            else:
                logger.warning("No active session or AndroidDeviceManager to stop")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping recording session: {e}")
            return False
    
    def _monitoring_loop(self):
        """Main monitoring loop that polls backend services for updates."""
        while self._running:
            try:
                # Check session status
                self._check_session_status()
                
                # Check device status
                self._check_device_status()
                
                # Generate sensor data if devices are connected
                self._check_sensor_data()
                
                # Sleep before next check
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait longer on error
    
    def _check_session_status(self):
        """Check and update session status."""
        if not self.session_manager:
            return
        
        try:
            # Check if session manager has current session
            if hasattr(self.session_manager, 'current_session'):
                current_session = self.session_manager.current_session
                if current_session and current_session != self._current_session_id:
                    # New session started
                    session_id = current_session.get('session_id') if isinstance(current_session, dict) else str(current_session)
                    if session_id != self._current_session_id:
                        self._current_session_id = session_id
                        self.recording_started.emit(session_id)
                        self.session_status_changed.emit(session_id, True)
                elif not current_session and self._current_session_id:
                    # Session ended
                    old_session = self._current_session_id
                    self._current_session_id = None
                    self.recording_stopped.emit(old_session, 0)
                    self.session_status_changed.emit(old_session, False)
        
        except Exception as e:
            logger.error(f"Error checking session status: {e}")
    
    def _check_device_status(self):
        """Check and update device status."""
        try:
            import random
            
            # Check real Shimmer devices first
            real_shimmer_devices = {}
            if self.shimmer_manager and hasattr(self.shimmer_manager, 'get_all_device_status'):
                try:
                    real_shimmer_devices = self.shimmer_manager.get_all_device_status() or {}
                except:
                    pass
            
            # Only emit real Shimmer devices, no fake ones
            if real_shimmer_devices:
                # Emit real device status
                for device_id, status in real_shimmer_devices.items():
                    self.device_status_received.emit(device_id, {
                        'type': 'shimmer',
                        'status': 'connected' if status.get('is_connected', False) else 'disconnected',
                        'battery': status.get('battery_level', 0),
                        'signal_strength': status.get('signal_strength', 0),
                        'recording': status.get('is_recording', False),
                        'sample_rate': status.get('sampling_rate', 0),
                        'mac_address': status.get('mac_address', 'Unknown')
                    })
            
            # Check real Android devices only
            real_android_devices = {}
            if self.android_device_manager and hasattr(self.android_device_manager, 'get_connected_devices'):
                try:
                    real_android_devices = self.android_device_manager.get_connected_devices() or {}
                except:
                    pass
            
            # Only emit real Android devices, no fake ones
            if real_android_devices:
                # Emit real device status
                for device_id, device_info in real_android_devices.items():
                    self.device_status_received.emit(device_id, {
                        'type': 'android',
                        'status': 'connected',
                        'capabilities': device_info.get('capabilities', []),
                        'battery': device_info.get('status', {}).get('battery_level', 0),
                        'temperature': device_info.get('status', {}).get('temperature', 0),
                        'recording': device_info.get('is_recording', False),
                        'last_heartbeat': device_info.get('last_heartbeat', 0)
                    })
            
            # Check real webcams using system monitor
            real_webcams = []
            try:
                from utils.system_monitor import get_system_monitor
                system_monitor = get_system_monitor()
                real_webcams = system_monitor.detect_webcams()
            except:
                # Fallback to webcam capture manager if available
                if self.webcam_capture and hasattr(self.webcam_capture, 'get_available_cameras'):
                    try:
                        real_webcams = self.webcam_capture.get_available_cameras() or []
                    except:
                        pass
            
            # Only emit real webcams, no fake ones
            if real_webcams:
                # Emit real webcam status
                for camera_info in real_webcams:
                    camera_id = f'webcam_{camera_info.get("index", 0)}'
                    self.device_status_received.emit(camera_id, {
                        'type': 'webcam',
                        'status': camera_info.get('status', 'active'),
                        'name': camera_info.get('name', f'Camera {camera_info.get("index", 0)}'),
                        'resolution': camera_info.get('resolution', 'Unknown'),
                        'fps': camera_info.get('fps', 30),
                        'recording': False  # Would need to check actual recording status
                    })
        
        except Exception as e:
            logger.error(f"Error checking device status: {e}")
    
    def _check_sensor_data(self):
        """Check and emit sensor data."""
        try:
            import random
            
            # Get real sensor data from connected devices only
            real_shimmer_data = {}
            if self.shimmer_manager and hasattr(self.shimmer_manager, 'get_all_device_status'):
                try:
                    shimmer_devices = self.shimmer_manager.get_all_device_status() or {}
                    for device_id, status in shimmer_devices.items():
                        if status.get('is_connected', False):
                            # Get actual sensor readings if available
                            if hasattr(self.shimmer_manager, 'get_sensor_data'):
                                sensor_data = self.shimmer_manager.get_sensor_data(device_id)
                                if sensor_data:
                                    real_shimmer_data[device_id] = sensor_data
                except:
                    pass
            
            # Only emit real sensor data, no fake data
            if real_shimmer_data:
                # Emit real sensor data
                for device_id, data in real_shimmer_data.items():
                    self.sensor_data_received.emit(device_id, data)
            
            # Get real sensor data from Android devices only
            real_android_data = {}
            if self.android_device_manager and hasattr(self.android_device_manager, 'get_connected_devices'):
                try:
                    android_devices = self.android_device_manager.get_connected_devices() or {}
                    for device_id, device_info in android_devices.items():
                        # Get actual sensor readings if available
                        if hasattr(self.android_device_manager, 'get_sensor_data'):
                            sensor_data = self.android_device_manager.get_sensor_data(device_id)
                            if sensor_data:
                                real_android_data[device_id] = sensor_data
                except:
                    pass
            
            # Only emit real sensor data, no fake data
            if real_android_data:
                # Emit real sensor data
                for device_id, data in real_android_data.items():
                    self.sensor_data_received.emit(device_id, data)
        
        except Exception as e:
            logger.error(f"Error checking sensor data: {e}")
    
    # Public interface methods for web UI control
    def start_recording(self, session_config: Dict[str, Any] = None) -> bool:
        """
        Start a new recording session.
        
        Args:
            session_config: Configuration for the recording session
            
        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Generate session ID
            session_id = f"web_session_{int(time.time())}"
            
            # Try to use real session manager if available
            if self.session_manager and hasattr(self.session_manager, 'start_session'):
                try:
                    result = self.session_manager.start_session(
                        session_id=session_id,
                        session_config=session_config or {}
                    )
                    if result:
                        self._current_session_id = session_id
                        self.recording_started.emit(session_id)
                        self.session_status_changed.emit(session_id, True)
                        logger.info(f"Recording session started using SessionManager: {session_id}")
                        return True
                except Exception as e:
                    logger.warning(f"SessionManager failed: {e}")
                    return False
            else:
                logger.error("No SessionManager available for recording")
                return False
        
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            self.error_occurred.emit("session", str(e))
            return False
    
    def stop_recording(self) -> bool:
        """
        Stop the current recording session.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self._current_session_id:
            logger.error("No active session to stop")
            return False
        
        try:
            session_id = self._current_session_id
            
            # Try to use real session manager if available
            if self.session_manager and hasattr(self.session_manager, 'stop_session'):
                try:
                    result = self.session_manager.stop_session(session_id)
                    if result:
                        self._current_session_id = None
                        self.recording_stopped.emit(session_id, 0)
                        self.session_status_changed.emit(session_id, False)
                        logger.info(f"Recording session stopped using SessionManager: {session_id}")
                        return True
                except Exception as e:
                    logger.warning(f"SessionManager failed: {e}")
                    return False
            else:
                logger.error("No SessionManager available for stopping recording")
                return False
        
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            self.error_occurred.emit("session", str(e))
            return False
    
    def get_device_status(self) -> Dict[str, Any]:
        """
        Get current status of all devices.
        
        Returns:
            Dictionary containing device status information
        """
        device_status = {
            'shimmer_devices': {},
            'android_devices': {},
            'webcam_devices': {}
        }
        
        try:
            # Get Shimmer device status
            if self.shimmer_manager and hasattr(self.shimmer_manager, 'get_all_device_status'):
                device_status['shimmer_devices'] = self.shimmer_manager.get_all_device_status()
            
            # Get Android device status
            if self.android_device_manager and hasattr(self.android_device_manager, 'get_connected_devices'):
                device_status['android_devices'] = self.android_device_manager.get_connected_devices()
            
            # Get webcam status
            if self.webcam_capture and hasattr(self.webcam_capture, 'get_available_cameras'):
                cameras = self.webcam_capture.get_available_cameras()
                device_status['webcam_devices'] = {f'webcam_{i}': cam for i, cam in enumerate(cameras)}
        
        except Exception as e:
            logger.error(f"Error getting device status: {e}")
        
        return device_status
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information.
        
        Returns:
            Dictionary containing session information
        """
        session_info = {
            'active': self._current_session_id is not None,
            'session_id': self._current_session_id,
            'start_time': None,
            'duration': 0
        }
        
        try:
            if self.session_manager and hasattr(self.session_manager, 'current_session'):
                current = self.session_manager.current_session
                if current and isinstance(current, dict):
                    session_info.update(current)
        
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
        
        return session_info


def create_web_controller_with_real_components():
    """
    Create a WebController instance and connect it to available real components.
    
    Returns:
        Configured WebController instance
    """
    controller = WebController()
    
    # Create and inject real backend components
    session_manager = None
    shimmer_manager = None
    android_device_manager = None
    json_server = None
    webcam_capture = None
    
    try:
        if SESSION_MANAGER_AVAILABLE:
            session_manager = SessionManager(base_recordings_dir="recordings")
            logger.info("Created SessionManager")
    except Exception as e:
        logger.error(f"Failed to create SessionManager: {e}")
    
    try:
        if SHIMMER_MANAGER_AVAILABLE:
            shimmer_manager = ShimmerManager()
            logger.info("Created ShimmerManager")
    except Exception as e:
        logger.error(f"Failed to create ShimmerManager: {e}")
    
    try:
        if ANDROID_DEVICE_MANAGER_AVAILABLE:
            android_device_manager = AndroidDeviceManager(server_port=9000)
            logger.info("Created AndroidDeviceManager with network server on port 9000")
    except Exception as e:
        logger.error(f"Failed to create AndroidDeviceManager: {e}")
    
    # Note: JsonSocketServer not needed since AndroidDeviceManager includes network server
    # json_server = None  # Removed to avoid port conflict
    
    try:
        if WEBCAM_CAPTURE_AVAILABLE:
            webcam_capture = WebcamCapture()
            logger.info("Created WebcamCapture")
    except Exception as e:
        logger.error(f"Failed to create WebcamCapture: {e}")
    
    # Inject dependencies (excluding redundant json_server)
    controller.inject_dependencies(
        session_manager=session_manager,
        shimmer_manager=shimmer_manager,
        android_device_manager=android_device_manager,
        json_server=None,  # Not needed - AndroidDeviceManager includes network server
        webcam_capture=webcam_capture
    )
    
    # Start monitoring
    controller.start_monitoring()
    
    logger.info("WebController created with real components")
    return controller


if __name__ == '__main__':
    # Test the WebController
    print("Testing WebController with real components...")
    
    controller = create_web_controller_with_real_components()
    
    # Test signal connections
    def on_device_status(device_id, status):
        print(f"Device status update: {device_id} -> {status}")
    
    def on_sensor_data(device_id, data):
        print(f"Sensor data: {device_id} -> {data}")
    
    controller.device_status_received.connect(on_device_status)
    controller.sensor_data_received.connect(on_sensor_data)
    
    print("Monitoring for 10 seconds...")
    time.sleep(10)
    
    controller.stop_monitoring()
    print("WebController test completed")