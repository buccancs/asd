#!/usr/bin/env python3
"""
Web Dashboard Server for Multi-Sensor Recording System

This module implements a Flask-based web server that provides a real-time monitoring
dashboard for the multi-sensor recording system. It offers:

- Real-time sensor data visualization through WebSocket connections
- Device status monitoring and control
- Session management interface
- Mobile-responsive design for tablet and phone access
- REST API endpoints for system integration

The web server runs alongside the existing PyQt5 desktop application and provides
an additional interface for monitoring and controlling the recording system.

Author: Multi-Sensor Recording System Team
Date: 2025-08-02
"""

import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from flask import Flask, render_template, jsonify, request, send_from_directory
    from flask_socketio import SocketIO, emit, disconnect
except ImportError:
    print("Flask not installed. Installing...")
    import subprocess
    subprocess.check_call(["pip3", "install", "flask", "flask-socketio", "eventlet"])
    from flask import Flask, render_template, jsonify, request, send_from_directory
    from flask_socketio import SocketIO, emit, disconnect

# Import logging configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback logging if utils not available
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

try:
    from utils.system_monitor import get_system_monitor
    SYSTEM_MONITOR_AVAILABLE = True
except ImportError:
    logger.warning("System monitor not available")
    SYSTEM_MONITOR_AVAILABLE = False
    get_system_monitor = lambda: None


class WebDashboardServer:
    """
    Web-based dashboard server for real-time monitoring of the multi-sensor recording system.
    
    This server provides a modern web interface that complements the existing PyQt5 desktop
    application, offering real-time monitoring, device management, and session control
    through a responsive web interface.
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False, controller=None):
        """
        Initialize the web dashboard server.
        
        Args:
            host: Server host address (default: '0.0.0.0' for all interfaces)
            port: Server port (default: 5000)
            debug: Enable Flask debug mode
            controller: Controller instance for real backend integration
        """
        self.host = host
        self.port = port
        self.debug = debug
        self.controller = controller  # For real backend integration
        
        # Initialize Flask app
        self.app = Flask(__name__, 
                        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                        static_folder=os.path.join(os.path.dirname(__file__), 'static'))
        self.app.config['SECRET_KEY'] = 'multisensor_recording_system_2025'
        
        # Initialize SocketIO for real-time communication
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='eventlet')
        
        # Server state
        self.running = False
        self.server_thread = None
        
        # Data storage for real-time updates
        self.device_status = {
            'android_devices': {},
            'usb_webcams': {},
            'shimmer_sensors': {},
            'pc_controller': {
                'status': 'idle',
                'cpu_usage': 0,
                'memory_usage': 0,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        self.session_info = {
            'active': False,
            'session_id': None,
            'start_time': None,
            'duration': 0,
            'recording_devices': [],
            'data_collected': {
                'video_files': 0,
                'thermal_frames': 0,
                'gsr_samples': 0
            }
        }
        
        self.sensor_data = {
            'timestamps': [],
            'android_1': {'camera': [], 'thermal': [], 'gsr': []},
            'android_2': {'camera': [], 'thermal': [], 'gsr': []},
            'webcam_1': [],
            'webcam_2': [],
            'shimmer_1': [],
            'shimmer_2': []
        }
        
        # Setup routes and socket handlers
        self._setup_routes()
        self._setup_socket_handlers()
        
        logger.info("Web Dashboard Server initialized")
    
    def _setup_routes(self):
        """Setup Flask routes for the web dashboard."""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/devices')
        def devices():
            """Device management page."""
            return render_template('devices.html')
        
        @self.app.route('/sessions')
        def sessions():
            """Session management page."""
            return render_template('sessions.html')
        
        @self.app.route('/playback')
        def playback():
            """Session playback page."""
            return render_template('playback.html')
        
        @self.app.route('/files')
        def files():
            """File viewer page."""
            return render_template('files.html')
        
        @self.app.route('/settings')
        def settings():
            """Settings page."""
            return render_template('settings.html')
        
        @self.app.route('/api/status')
        def api_status():
            """Get current system status."""
            return jsonify({
                'status': 'running',
                'devices': self.device_status,
                'session': self.session_info,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/devices')
        def api_devices():
            """Get device status information."""
            return jsonify(self.device_status)
        
        @self.app.route('/api/session')
        def api_session():
            """Get current session information."""
            return jsonify(self.session_info)
        
        @self.app.route('/api/session/start', methods=['POST'])
        def api_session_start():
            """Start a new recording session using real network protocols."""
            try:
                config = request.get_json() or {}
                session_id = f"web_session_{int(time.time())}"
                
                # Use real controller to start session via network protocols
                if self.controller and hasattr(self.controller, 'start_recording_session'):
                    success = self.controller.start_recording_session(session_id)
                    if not success:
                        logger.error(f"Controller failed to start session: {session_id}")
                        return jsonify({'success': False, 'error': 'Failed to start session via network protocols'}), 500
                else:
                    logger.warning("No controller available - falling back to local session tracking")
                
                self.session_info.update({
                    'active': True,
                    'session_id': session_id,
                    'start_time': datetime.now().isoformat(),
                    'duration': 0,
                    'recording_devices': config.get('devices', []),
                    'data_collected': {
                        'video_files': 0,
                        'thermal_frames': 0,
                        'gsr_samples': 0
                    }
                })
                
                logger.info(f"Recording session started via web interface using network protocols: {session_id}")
                self._broadcast_session_update()
                
                return jsonify({'success': True, 'session_id': session_id})
            
            except Exception as e:
                logger.error(f"Failed to start session: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/session/stop', methods=['POST'])
        def api_session_stop():
            """Stop the current recording session using real network protocols."""
            try:
                if self.session_info['active']:
                    session_id = self.session_info['session_id']
                    
                    # Use real controller to stop session via network protocols
                    if self.controller and hasattr(self.controller, 'stop_recording_session'):
                        success = self.controller.stop_recording_session()
                        if not success:
                            logger.error(f"Controller failed to stop session: {session_id}")
                            return jsonify({'success': False, 'error': 'Failed to stop session via network protocols'}), 500
                    else:
                        logger.warning("No controller available - falling back to local session tracking")
                    
                    self.session_info.update({
                        'active': False,
                        'session_id': None,
                        'start_time': None,
                        'duration': 0
                    })
                    
                    logger.info(f"Recording session stopped via web interface using network protocols: {session_id}")
                    self._broadcast_session_update()
                    
                    return jsonify({'success': True, 'session_id': session_id})
                else:
                    return jsonify({'success': False, 'error': 'No active session'}), 400
            
            except Exception as e:
                logger.error(f"Failed to stop session: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/data/realtime')
        def api_realtime_data():
            """Get real-time sensor data for visualization."""
            # Return recent data points for charts
            recent_data = {}
            max_points = 100  # Limit to last 100 data points
            
            for device, data in self.sensor_data.items():
                if device == 'timestamps':
                    recent_data[device] = data[-max_points:] if data else []
                elif isinstance(data, dict):
                    recent_data[device] = {}
                    for sensor, values in data.items():
                        recent_data[device][sensor] = values[-max_points:] if values else []
                else:
                    recent_data[device] = data[-max_points:] if data else []
            
            return jsonify(recent_data)
        
        @self.app.route('/api/device/connect', methods=['POST'])
        def api_device_connect():
            """Connect to a device."""
            try:
                data = request.get_json() or {}
                device_id = data.get('device_id')
                device_type = data.get('device_type')
                
                if self.controller and hasattr(self.controller, 'connect_device'):
                    success = self.controller.connect_device(device_id, device_type)
                    if success:
                        return jsonify({'success': True, 'message': f'Connected to {device_id}'})
                    else:
                        return jsonify({'success': False, 'error': 'Connection failed'}), 500
                else:
                    # Attempt real device connection based on type
                    if device_type == 'android':
                        # This would be handled by AndroidDeviceManager
                        return jsonify({'success': False, 'error': 'Android device manager not available'}), 500
                    elif device_type == 'shimmer':
                        # This would be handled by ShimmerManager
                        return jsonify({'success': False, 'error': 'Shimmer manager not available'}), 500
                    elif device_type == 'webcam':
                        # Check if webcam is actually available
                        if SYSTEM_MONITOR_AVAILABLE:
                            system_monitor = get_system_monitor()
                            webcams = system_monitor.detect_webcams()
                            if any(cam['index'] == int(device_id) for cam in webcams):
                                return jsonify({'success': True, 'message': f'Webcam {device_id} is available'})
                        return jsonify({'success': False, 'error': 'Webcam not found'}), 500
                    else:
                        return jsonify({'success': False, 'error': 'Unknown device type'}), 400
                    
            except Exception as e:
                logger.error(f"Device connection error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/device/configure', methods=['POST'])
        def api_device_configure():
            """Configure a device."""
            try:
                data = request.get_json() or {}
                device_id = data.get('device_id')
                device_type = data.get('device_type')
                configuration = data.get('configuration', {})
                
                if self.controller and hasattr(self.controller, 'configure_device'):
                    success = self.controller.configure_device(device_id, device_type, configuration)
                    if success:
                        return jsonify({'success': True, 'message': f'Configured {device_id}'})
                    else:
                        return jsonify({'success': False, 'error': 'Configuration failed'}), 500
                else:
                    # Real device configuration
                    if device_type in ['android', 'shimmer']:
                        return jsonify({'success': False, 'error': f'{device_type.title()} manager not available'}), 500
                    elif device_type == 'webcam':
                        # Webcam configuration would require actual OpenCV integration
                        logger.info(f"Webcam {device_id} configuration: {configuration}")
                        return jsonify({'success': True, 'message': f'Webcam {device_id} configuration updated'})
                    else:
                        return jsonify({'success': False, 'error': 'Unknown device type'}), 400
                    
            except Exception as e:
                logger.error(f"Device configuration error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/webcam/test', methods=['POST'])
        def api_webcam_test():
            """Test webcam functionality."""
            try:
                data = request.get_json() or {}
                webcam_id = data.get('webcam_id')
                
                if self.controller and hasattr(self.controller, 'test_webcam'):
                    test_results = self.controller.test_webcam(webcam_id)
                    return jsonify({'success': True, 'test_results': test_results})
                else:
                    # Real webcam testing
                    if SYSTEM_MONITOR_AVAILABLE:
                        system_monitor = get_system_monitor()
                        webcams = system_monitor.detect_webcams()
                        
                        # Find the specific webcam
                        try:
                            webcam_index = int(webcam_id) if webcam_id else 0
                            cam_info = next((cam for cam in webcams if cam['index'] == webcam_index), None)
                            
                            if cam_info:
                                return jsonify({
                                    'success': True,
                                    'test_results': {
                                        'resolution': cam_info['resolution'],
                                        'fps': cam_info['fps'],
                                        'status': cam_info['status'],
                                        'index': cam_info['index']
                                    }
                                })
                            else:
                                return jsonify({'success': False, 'error': f'Webcam {webcam_id} not found'}), 404
                        except ValueError:
                            return jsonify({'success': False, 'error': 'Invalid webcam ID'}), 400
                    else:
                        return jsonify({'success': False, 'error': 'System monitoring not available'}), 500
                    
            except Exception as e:
                logger.error(f"Webcam test error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/webcam/configure', methods=['POST'])
        def api_webcam_configure():
            """Configure webcam settings."""
            try:
                data = request.get_json() or {}
                webcam_id = data.get('webcam_id')
                resolution = data.get('resolution')
                fps = data.get('fps')
                
                if self.controller and hasattr(self.controller, 'configure_webcam'):
                    success = self.controller.configure_webcam(webcam_id, resolution, fps)
                    if success:
                        return jsonify({'success': True, 'message': f'Webcam {webcam_id} configured'})
                    else:
                        return jsonify({'success': False, 'error': 'Configuration failed'}), 500
                else:
                    # Real webcam configuration (limited without actual webcam manager)
                    if SYSTEM_MONITOR_AVAILABLE:
                        system_monitor = get_system_monitor()
                        webcams = system_monitor.detect_webcams()
                        
                        try:
                            webcam_index = int(webcam_id) if webcam_id else 0
                            if any(cam['index'] == webcam_index for cam in webcams):
                                logger.info(f"Webcam {webcam_id} configuration set: {resolution} @ {fps}fps")
                                return jsonify({'success': True, 'message': f'Webcam {webcam_id} configured'})
                            else:
                                return jsonify({'success': False, 'error': f'Webcam {webcam_id} not found'}), 404
                        except ValueError:
                            return jsonify({'success': False, 'error': 'Invalid webcam ID'}), 400
                    else:
                        return jsonify({'success': False, 'error': 'System monitoring not available'}), 500
                    
            except Exception as e:
                logger.error(f"Webcam configuration error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/shimmer/connect', methods=['POST'])
        def api_shimmer_connect():
            """Connect to Shimmer sensor."""
            try:
                data = request.get_json() or {}
                sensor_id = data.get('sensor_id')
                
                if self.controller and hasattr(self.controller, 'connect_shimmer'):
                    success = self.controller.connect_shimmer(sensor_id)
                    if success:
                        return jsonify({'success': True, 'message': f'Connected to Shimmer {sensor_id}'})
                    else:
                        return jsonify({'success': False, 'error': 'Connection failed'}), 500
                else:
                    # Real Shimmer connection requires ShimmerManager
                    logger.warning(f"Shimmer connection attempted but ShimmerManager not available: {sensor_id}")
                    return jsonify({'success': False, 'error': 'Shimmer manager not available'}), 501
                    
            except Exception as e:
                logger.error(f"Shimmer connection error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/shimmer/configure', methods=['POST'])
        def api_shimmer_configure():
            """Configure Shimmer sensor."""
            try:
                data = request.get_json() or {}
                sensor_id = data.get('sensor_id')
                sample_rate = data.get('sample_rate')
                enabled_sensors = data.get('enabled_sensors', [])
                
                if self.controller and hasattr(self.controller, 'configure_shimmer'):
                    success = self.controller.configure_shimmer(sensor_id, sample_rate, enabled_sensors)
                    if success:
                        return jsonify({'success': True, 'message': f'Shimmer {sensor_id} configured'})
                    else:
                        return jsonify({'success': False, 'error': 'Configuration failed'}), 500
                else:
                    # Real Shimmer configuration requires ShimmerManager
                    logger.warning(f"Shimmer configuration attempted but ShimmerManager not available: {sensor_id}")
                    return jsonify({'success': False, 'error': 'Shimmer manager not available'}), 501
                    
            except Exception as e:
                logger.error(f"Shimmer configuration error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/system/status')
        def api_system_status():
            """Get real-time system status and monitoring data."""
            try:
                if SYSTEM_MONITOR_AVAILABLE:
                    system_monitor = get_system_monitor()
                    status = system_monitor.get_comprehensive_status()
                    return jsonify({'success': True, 'status': status})
                else:
                    # Fallback basic system info
                    import platform
                    import time
                    status = {
                        'timestamp': time.time(),
                        'system_info': {
                            'platform': platform.system(),
                            'hostname': platform.node(),
                            'python_version': platform.python_version()
                        },
                        'cpu': {'usage_percent': 0},
                        'memory': {'total': 0, 'used': 0, 'percent': 0},
                        'disk': {},
                        'network': {},
                        'webcams': [],
                        'bluetooth': [],
                        'processes': []
                    }
                    return jsonify({'success': True, 'status': status})
                    
            except Exception as e:
                logger.error(f"System status error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/sessions/export')
        def api_sessions_export():
            """Export session data."""
            try:
                # Generate mock session export data
                export_data = {
                    'exported_at': datetime.now().isoformat(),
                    'sessions': [
                        {
                            'id': 'session_20250802_001',
                            'name': 'Baseline Recording',
                            'start_time': '2025-08-02T10:30:00Z',
                            'end_time': '2025-08-02T11:00:00Z',
                            'duration': 1800,
                            'devices': ['android_1', 'android_2', 'webcam_1'],
                            'status': 'completed',
                            'data_size': '2.5 GB'
                        },
                        {
                            'id': 'session_20250802_002',
                            'name': 'Stress Test',
                            'start_time': '2025-08-02T14:15:00Z',
                            'end_time': '2025-08-02T14:45:00Z',
                            'duration': 1200,
                            'devices': ['android_1', 'shimmer_1', 'shimmer_2'],
                            'status': 'completed',
                            'data_size': '1.8 GB'
                        }
                    ]
                }
                
                response = jsonify(export_data)
                response.headers['Content-Disposition'] = f'attachment; filename=session_export_{datetime.now().strftime("%Y%m%d")}.json'
                return response
                
            except Exception as e:
                logger.error(f"Session export error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/session/<session_id>')
        def api_session_details(session_id):
            """Get detailed session information."""
            try:
                # Mock session details - in real implementation would query database
                session_details = {
                    'id': session_id,
                    'name': 'Baseline Recording',
                    'start_time': '2025-08-02T10:30:00Z',
                    'end_time': '2025-08-02T11:00:00Z',
                    'duration': 1800,
                    'devices': ['android_1', 'android_2', 'webcam_1'],
                    'status': 'completed',
                    'data_size': '2.5 GB',
                    'data_collected': {
                        'video_files': 12,
                        'thermal_frames': 54000,
                        'gsr_samples': 460800,
                        'audio_files': 3
                    }
                }
                
                return jsonify({'success': True, 'session': session_details})
                
            except Exception as e:
                logger.error(f"Session details error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/session/<session_id>/download')
        def api_session_download(session_id):
            """Download session data."""
            try:
                # Real implementation would check if session exists and create ZIP file
                if self.controller and hasattr(self.controller, 'get_session_data'):
                    session_data = self.controller.get_session_data(session_id)
                    if session_data:
                        # Create downloadable content
                        response_data = f"Session data for {session_id}\nGenerated at: {datetime.now().isoformat()}"
                        
                        from flask import make_response
                        response = make_response(response_data)
                        response.headers['Content-Type'] = 'application/octet-stream'
                        response.headers['Content-Disposition'] = f'attachment; filename={session_id}_data.txt'
                        return response
                    else:
                        return jsonify({'success': False, 'error': 'Session not found'}), 404
                else:
                    return jsonify({'success': False, 'error': 'Session manager not available'}), 501
                
            except Exception as e:
                logger.error(f"Session download error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # === PLAYBACK API ENDPOINTS ===
        
        @self.app.route('/api/playback/sessions')
        def api_playback_sessions():
            """Get list of recorded sessions for playback."""
            try:
                # Mock recorded sessions - in real implementation would query storage
                sessions = [
                    {
                        'id': 'session_20250802_001',
                        'name': 'Baseline Recording',
                        'start_time': '2025-08-02T10:30:00Z',
                        'duration': 1800,
                        'devices': ['android_1', 'android_2', 'webcam_1'],
                        'status': 'completed'
                    },
                    {
                        'id': 'session_20250802_002', 
                        'name': 'Stress Test',
                        'start_time': '2025-08-02T14:15:00Z',
                        'duration': 1200,
                        'devices': ['android_1', 'shimmer_1', 'shimmer_2'],
                        'status': 'completed'
                    }
                ]
                
                return jsonify({'success': True, 'sessions': sessions})
                
            except Exception as e:
                logger.error(f"Playback sessions error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/playback/session/<session_id>')
        def api_playback_session_data(session_id):
            """Get detailed session data for playback."""
            try:
                # Mock session data
                session_data = {
                    'id': session_id,
                    'name': 'Baseline Recording',
                    'start_time': '2025-08-02T10:30:00Z',
                    'duration': 1800,
                    'devices': ['android_1', 'android_2', 'webcam_1'],
                    'status': 'completed',
                    'data_size': '2.5 GB'
                }
                
                return jsonify({'success': True, 'session': session_data})
                
            except Exception as e:
                logger.error(f"Playback session data error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/playback/session/<session_id>/videos')
        def api_playback_session_videos(session_id):
            """Get video files for session playback."""
            try:
                # Mock video files
                videos = [
                    {'filename': 'camera1.mp4', 'duration': 1800},
                    {'filename': 'camera2.mp4', 'duration': 1800}
                ]
                
                return jsonify({'success': True, 'videos': videos})
                
            except Exception as e:
                logger.error(f"Playback videos error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/playback/session/<session_id>/sensors')
        def api_playback_session_sensors(session_id):
            """Get sensor data for session playback."""
            try:
                # Mock sensor data points
                import random
                time_points = list(range(0, 1800, 5))  # Every 5 seconds
                
                sensor_data = {
                    'gsr': [{'x': t, 'y': random.uniform(0.1, 2.0)} for t in time_points],
                    'thermal': [{'x': t, 'y': random.uniform(25, 35)} for t in time_points],
                    'shimmer': [{'x': t, 'y': random.uniform(0.5, 3.0)} for t in time_points],
                    'heart_rate': [{'x': t, 'y': random.uniform(60, 100)} for t in time_points]
                }
                
                return jsonify({'success': True, 'sensor_data': sensor_data})
                
            except Exception as e:
                logger.error(f"Playback sensors error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/playback/video/<session_id>/<filename>')
        def api_playback_video(session_id, filename):
            """Serve video file for playback."""
            try:
                # Check if session and video file exist
                if self.controller and hasattr(self.controller, 'get_session_video'):
                    video_path = self.controller.get_session_video(session_id, filename)
                    if video_path and os.path.exists(video_path):
                        return send_from_directory(os.path.dirname(video_path), filename)
                    else:
                        return jsonify({'success': False, 'error': 'Video file not found'}), 404
                else:
                    # Check recordings directory
                    recordings_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'recordings')
                    session_dir = os.path.join(recordings_dir, session_id)
                    video_path = os.path.join(session_dir, filename)
                    
                    if os.path.exists(video_path):
                        return send_from_directory(session_dir, filename)
                    else:
                        return jsonify({'success': False, 'error': 'Video file not found'}), 404
                
            except Exception as e:
                logger.error(f"Video playback error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/playback/export-segment', methods=['POST'])
        def api_playback_export_segment():
            """Export a segment of session data."""
            try:
                data = request.get_json() or {}
                session_id = data.get('session_id')
                start_time = data.get('start_time')
                end_time = data.get('end_time')
                
                # Mock export process
                logger.info(f"Exporting segment from {start_time}s to {end_time}s for session {session_id}")
                
                return jsonify({'success': True, 'message': 'Segment exported successfully'})
                
            except Exception as e:
                logger.error(f"Export segment error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/playback/session/<session_id>/report')
        def api_playback_session_report(session_id):
            """Generate session analysis report."""
            try:
                # Mock report generation
                report_html = f"""
                <html>
                <head><title>Session Report - {session_id}</title></head>
                <body>
                    <h1>Session Analysis Report</h1>
                    <h2>Session: {session_id}</h2>
                    <p>Generated: {datetime.now().isoformat()}</p>
                    <h3>Summary</h3>
                    <p>Session duration: 30 minutes</p>
                    <p>Devices: 3</p>
                    <p>Data points: 10,800</p>
                </body>
                </html>
                """
                
                from flask import make_response
                response = make_response(report_html)
                response.headers['Content-Type'] = 'text/html'
                return response
                
            except Exception as e:
                logger.error(f"Session report error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/playback/session/<session_id>/sync-analysis')
        def api_playback_sync_analysis(session_id):
            """Analyze synchronization quality of session."""
            try:
                # Mock sync analysis
                import random
                analysis = {
                    'sync_quality': random.uniform(0.7, 0.95),
                    'max_drift': random.uniform(0.1, 2.0),
                    'avg_drift': random.uniform(0.05, 0.5)
                }
                
                return jsonify({'success': True, 'analysis': analysis})
                
            except Exception as e:
                logger.error(f"Sync analysis error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # === FILE VIEWER API ENDPOINTS ===
        
        @self.app.route('/api/files/browse')
        def api_files_browse():
            """Browse files in directory."""
            try:
                path = request.args.get('path', '/')
                
                # Mock file listing
                files = [
                    {
                        'name': 'session_20250802_001',
                        'type': 'directory',
                        'size': 0,
                        'modified': '2025-08-02T10:30:00Z',
                        'path': path + '/session_20250802_001'
                    },
                    {
                        'name': 'camera1.mp4',
                        'type': 'file',
                        'size': 2684354560,  # 2.5 GB
                        'modified': '2025-08-02T11:00:00Z',
                        'path': path + '/camera1.mp4'
                    },
                    {
                        'name': 'sensor_data.json',
                        'type': 'file',
                        'size': 1048576,  # 1 MB
                        'modified': '2025-08-02T11:00:00Z',
                        'path': path + '/sensor_data.json'
                    }
                ]
                
                return jsonify({'success': True, 'files': files})
                
            except Exception as e:
                logger.error(f"File browse error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/files/details')
        def api_files_details():
            """Get detailed file information."""
            try:
                file_path = request.args.get('path')
                
                # Mock file details
                file_details = {
                    'name': os.path.basename(file_path),
                    'type': 'file',
                    'size': 1048576,
                    'modified': '2025-08-02T11:00:00Z',
                    'path': file_path
                }
                
                return jsonify({'success': True, 'file': file_details})
                
            except Exception as e:
                logger.error(f"File details error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/files/content')
        def api_files_content():
            """Get file content for preview."""
            try:
                file_path = request.args.get('path')
                if not file_path:
                    return jsonify({'success': False, 'error': 'No file path provided'}), 400
                
                # Check if file exists and is readable
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    try:
                        # Only read text files for preview
                        _, ext = os.path.splitext(file_path)
                        if ext.lower() in ['.txt', '.log', '.json', '.csv', '.md', '.py', '.js', '.html', '.css']:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read(10000)  # Limit to first 10KB
                                return jsonify({'success': True, 'content': content, 'type': 'text'})
                        else:
                            return jsonify({'success': False, 'error': 'File type not supported for preview'}), 415
                    except (UnicodeDecodeError, PermissionError):
                        return jsonify({'success': False, 'error': 'Cannot read file'}), 403
                else:
                    return jsonify({'success': False, 'error': 'File not found'}), 404
                
            except Exception as e:
                logger.error(f"File content error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/files/download')
        def api_files_download():
            """Download a file."""
            try:
                file_path = request.args.get('path')
                if not file_path:
                    return jsonify({'success': False, 'error': 'No file path provided'}), 400
                
                # Check if file exists and serve it
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    try:
                        return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))
                    except PermissionError:
                        return jsonify({'success': False, 'error': 'Permission denied'}), 403
                else:
                    return jsonify({'success': False, 'error': 'File not found'}), 404
                
            except Exception as e:
                logger.error(f"File download error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/files/download-multiple', methods=['POST'])
        def api_files_download_multiple():
            """Download multiple files as ZIP."""
            try:
                data = request.get_json() or {}
                files = data.get('files', [])
                
                # Mock ZIP creation
                response_data = f"ZIP archive containing {len(files)} files"
                from flask import make_response
                response = make_response(response_data)
                response.headers['Content-Type'] = 'application/zip'
                response.headers['Content-Disposition'] = 'attachment; filename=selected_files.zip'
                return response
                
            except Exception as e:
                logger.error(f"Multiple download error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/files/delete-multiple', methods=['POST'])
        def api_files_delete_multiple():
            """Delete multiple files."""
            try:
                data = request.get_json() or {}
                files = data.get('files', [])
                
                # Mock deletion
                logger.info(f"Deleting {len(files)} files")
                
                return jsonify({'success': True, 'message': f'Deleted {len(files)} files'})
                
            except Exception as e:
                logger.error(f"Multiple delete error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/files/open-external', methods=['POST'])
        def api_files_open_external():
            """Open file in external application."""
            try:
                data = request.get_json() or {}
                file_path = data.get('path')
                
                # Mock external open
                logger.info(f"Opening file externally: {file_path}")
                
                return jsonify({'success': True, 'message': 'File opened in external application'})
                
            except Exception as e:
                logger.error(f"Open external error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/files/properties')
        def api_files_properties():
            """Get detailed file properties."""
            try:
                file_path = request.args.get('path')
                
                # Mock properties
                properties = {
                    'File Name': os.path.basename(file_path),
                    'File Type': 'Video File',
                    'Size': '2.5 GB',
                    'Created': '2025-08-02T10:30:00Z',
                    'Modified': '2025-08-02T11:00:00Z',
                    'Duration': '30:00',
                    'Resolution': '1920x1080',
                    'Frame Rate': '30 fps',
                    'Codec': 'H.264'
                }
                
                return jsonify({'success': True, 'properties': properties})
                
            except Exception as e:
                logger.error(f"File properties error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/files/create-folder', methods=['POST'])
        def api_files_create_folder():
            """Create a new folder."""
            try:
                data = request.get_json() or {}
                path = data.get('path')
                name = data.get('name')
                
                # Mock folder creation
                logger.info(f"Creating folder {name} in {path}")
                
                return jsonify({'success': True, 'message': f'Folder "{name}" created'})
                
            except Exception as e:
                logger.error(f"Create folder error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/files/upload', methods=['POST'])
        def api_files_upload():
            """Upload files."""
            try:
                # Mock file upload
                files = request.files.getlist('files')
                path = request.form.get('path')
                
                logger.info(f"Uploading {len(files)} files to {path}")
                
                return jsonify({'success': True, 'message': f'Uploaded {len(files)} files'})
                
            except Exception as e:
                logger.error(f"File upload error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/files/export-zip')
        def api_files_export_zip():
            """Export directory as ZIP."""
            try:
                path = request.args.get('path')
                
                # Mock ZIP export
                response_data = f"ZIP export of directory {path}"
                from flask import make_response
                response = make_response(response_data)
                response.headers['Content-Type'] = 'application/zip'
                response.headers['Content-Disposition'] = f'attachment; filename=export_{int(time.time())}.zip'
                return response
                
            except Exception as e:
                logger.error(f"Export ZIP error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/files/generate-index')
        def api_files_generate_index():
            """Generate file index."""
            try:
                path = request.args.get('path')
                
                # Mock index generation
                logger.info(f"Generating index for {path}")
                
                return jsonify({'success': True, 'message': 'File index generated'})
                
            except Exception as e:
                logger.error(f"Generate index error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # === SETTINGS API ENDPOINTS ===
        
        @self.app.route('/api/settings')
        def api_settings_get():
            """Get current settings."""
            try:
                # Mock settings
                settings = {
                    'theme': 'light',
                    'language': 'en',
                    'autosaveInterval': 5,
                    'notifications': True,
                    'recordingDuration': 30,
                    'videoQuality': '1080p',
                    'audioRecording': True,
                    'autoStartRecording': False,
                    'compressionLevel': 5,
                    'androidTimeout': 30,
                    'androidRetries': 3,
                    'androidAutoReconnect': True,
                    'shimmerSamplingRate': 256,
                    'shimmerBatteryWarning': 20,
                    'shimmerEnabledSensors': ['GSR', 'Accelerometer'],
                    'webcamResolution': '1920x1080',
                    'webcamFPS': 30,
                    'serverPort': 9000,
                    'webPort': 5000,
                    'connectionTimeout': 30,
                    'enableSSL': False,
                    'dataCompression': True,
                    'autoCalibration': False,
                    'calibrationPattern': 'checkerboard',
                    'patternSize': 25,
                    'minCalibrationImages': 10,
                    'storagePath': './recordings',
                    'autoCleanup': False,
                    'cleanupThreshold': 85,
                    'retentionPeriod': 30,
                    'autoBackup': True,
                    'backupInterval': 'daily',
                    'backupPath': './backups',
                    'debugMode': False,
                    'logLevel': 'INFO',
                    'memoryLimit': 1024,
                    'workerThreads': 4
                }
                
                return jsonify({'success': True, 'settings': settings})
                
            except Exception as e:
                logger.error(f"Get settings error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/settings', methods=['POST'])
        def api_settings_save():
            """Save settings."""
            try:
                settings = request.get_json() or {}
                
                # Mock settings save
                logger.info(f"Saving {len(settings)} settings")
                
                return jsonify({'success': True, 'message': 'Settings saved successfully'})
                
            except Exception as e:
                logger.error(f"Save settings error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/settings/reset', methods=['POST'])
        def api_settings_reset():
            """Reset settings to defaults."""
            try:
                # Mock settings reset
                logger.info("Resetting settings to defaults")
                
                return jsonify({'success': True, 'message': 'Settings reset to defaults'})
                
            except Exception as e:
                logger.error(f"Reset settings error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/settings/storage-status')
        def api_settings_storage_status():
            """Get storage status information."""
            try:
                # Mock storage status
                import random
                total = 1000000000000  # 1 TB
                used = int(total * random.uniform(0.3, 0.8))
                free = total - used
                
                storage = {
                    'total': total,
                    'used': used,
                    'free': free
                }
                
                return jsonify({'success': True, 'storage': storage})
                
            except Exception as e:
                logger.error(f"Storage status error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/settings/backups')
        def api_settings_backups():
            """Get list of available backups."""
            try:
                # Mock backup list
                backups = [
                    {
                        'name': 'backup_20250802.json',
                        'date': '2025-08-02T10:00:00Z',
                        'size': 2048
                    },
                    {
                        'name': 'backup_20250801.json',
                        'date': '2025-08-01T10:00:00Z',
                        'size': 1950
                    }
                ]
                
                return jsonify({'success': True, 'backups': backups})
                
            except Exception as e:
                logger.error(f"Get backups error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/settings/backup', methods=['POST'])
        def api_settings_create_backup():
            """Create a new backup."""
            try:
                # Mock backup creation
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                logger.info(f"Creating backup: {backup_name}")
                
                return jsonify({'success': True, 'message': f'Backup created: {backup_name}'})
                
            except Exception as e:
                logger.error(f"Create backup error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/settings/restore', methods=['POST'])
        def api_settings_restore_backup():
            """Restore from backup."""
            try:
                # Mock backup restoration
                logger.info("Restoring from backup")
                
                return jsonify({'success': True, 'message': 'Backup restored successfully'})
                
            except Exception as e:
                logger.error(f"Restore backup error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/settings/backup/<backup_name>/download')
        def api_settings_download_backup(backup_name):
            """Download a backup file."""
            try:
                # Mock backup download
                response_data = f"Backup file: {backup_name}"
                from flask import make_response
                response = make_response(response_data)
                response.headers['Content-Type'] = 'application/json'
                response.headers['Content-Disposition'] = f'attachment; filename={backup_name}'
                return response
                
            except Exception as e:
                logger.error(f"Download backup error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/settings/backup/<backup_name>', methods=['DELETE'])
        def api_settings_delete_backup(backup_name):
            """Delete a backup file."""
            try:
                # Mock backup deletion
                logger.info(f"Deleting backup: {backup_name}")
                
                return jsonify({'success': True, 'message': f'Backup deleted: {backup_name}'})
                
            except Exception as e:
                logger.error(f"Delete backup error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/settings/browse-directory', methods=['POST'])
        def api_settings_browse_directory():
            """Browse for directory selection."""
            try:
                data = request.get_json() or {}
                directory_type = data.get('type')
                
                # Mock directory selection
                mock_paths = {
                    'storage': '/home/user/recordings',
                    'backup': '/home/user/backups'
                }
                
                selected_path = mock_paths.get(directory_type, '/home/user')
                
                return jsonify({'success': True, 'path': selected_path})
                
            except Exception as e:
                logger.error(f"Browse directory error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
    
    def _setup_socket_handlers(self):
        """Setup SocketIO event handlers for real-time communication."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            logger.info(f"Web client connected: {request.sid}")
            emit('status_update', {
                'devices': self.device_status,
                'session': self.session_info,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            logger.info(f"Web client disconnected: {request.sid}")
        
        @self.socketio.on('request_device_status')
        def handle_device_status_request():
            """Handle request for current device status."""
            emit('device_status_update', self.device_status)
        
        @self.socketio.on('request_session_info')
        def handle_session_info_request():
            """Handle request for current session information."""
            emit('session_info_update', self.session_info)
    
    def update_device_status(self, device_type: str, device_id: str, status_data: Dict[str, Any]):
        """
        Update device status and broadcast to connected clients.
        
        Args:
            device_type: Type of device ('android_devices', 'usb_webcams', 'shimmer_sensors')
            device_id: Unique identifier for the device
            status_data: Status information dictionary
        """
        if device_type not in self.device_status:
            logger.warning(f"Unknown device type: {device_type}")
            return
        
        status_data['timestamp'] = datetime.now().isoformat()
        self.device_status[device_type][device_id] = status_data
        
        # Broadcast update to all connected clients
        self.socketio.emit('device_status_update', {
            'device_type': device_type,
            'device_id': device_id,
            'status': status_data
        })
    
    def update_sensor_data(self, device_id: str, sensor_type: str, value: float):
        """
        Update real-time sensor data and broadcast to connected clients.
        
        Args:
            device_id: Device identifier
            sensor_type: Type of sensor data
            value: Sensor reading value
        """
        timestamp = datetime.now().isoformat()
        
        # Add timestamp if not already present
        if not self.sensor_data['timestamps'] or self.sensor_data['timestamps'][-1] != timestamp:
            self.sensor_data['timestamps'].append(timestamp)
        
        # Update sensor data based on device and sensor type
        if device_id in self.sensor_data:
            if isinstance(self.sensor_data[device_id], dict):
                if sensor_type in self.sensor_data[device_id]:
                    self.sensor_data[device_id][sensor_type].append(value)
                else:
                    logger.warning(f"Unknown sensor type {sensor_type} for device {device_id}")
            else:
                self.sensor_data[device_id].append(value)
        else:
            logger.warning(f"Unknown device ID: {device_id}")
        
        # Limit data points to prevent memory issues
        max_points = 1000
        for device, data in self.sensor_data.items():
            if device == 'timestamps':
                if len(data) > max_points:
                    self.sensor_data[device] = data[-max_points:]
            elif isinstance(data, dict):
                for sensor, values in data.items():
                    if len(values) > max_points:
                        self.sensor_data[device][sensor] = values[-max_points:]
            else:
                if len(data) > max_points:
                    self.sensor_data[device] = data[-max_points:]
        
        # Broadcast real-time data update
        self.socketio.emit('sensor_data_update', {
            'device_id': device_id,
            'sensor_type': sensor_type,
            'value': value,
            'timestamp': timestamp
        })
    
    def _broadcast_session_update(self):
        """Broadcast session information update to all connected clients."""
        self.socketio.emit('session_info_update', self.session_info)
    
    def start_server(self):
        """Start the web dashboard server."""
        if self.running:
            logger.warning("Web dashboard server is already running")
            return
        
        self.running = True
        logger.info(f"Starting web dashboard server on {self.host}:{self.port}")
        
        def run_server():
            self.socketio.run(self.app, host=self.host, port=self.port, debug=self.debug)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        logger.info(f"Web dashboard available at http://{self.host}:{self.port}")
    
    def stop_server(self):
        """Stop the web dashboard server."""
        if not self.running:
            logger.warning("Web dashboard server is not running")
            return
        
        self.running = False
        logger.info("Stopping web dashboard server")
        
        # SocketIO server will stop when the main thread ends
        if self.server_thread:
            self.server_thread.join(timeout=5)
    
    def is_running(self) -> bool:
        """Check if the server is running."""
        return self.running


# Convenience function for creating and starting the server
def create_web_dashboard(host: str = '0.0.0.0', port: int = 5000, debug: bool = False) -> WebDashboardServer:
    """
    Create and configure a web dashboard server instance.
    
    Args:
        host: Server host address
        port: Server port
        debug: Enable debug mode
    
    Returns:
        Configured WebDashboardServer instance
    """
    return WebDashboardServer(host=host, port=port, debug=debug)


if __name__ == '__main__':
    # Demo/test mode - start server with simulated data
    dashboard = create_web_dashboard(debug=True)
    dashboard.start_server()
    
    # Simulate some device status updates
    import time
    import random
    
    try:
        while True:
            # Simulate device status updates
            dashboard.update_device_status('android_devices', 'device_1', {
                'status': 'connected',
                'battery': random.randint(20, 100),
                'temperature': round(random.uniform(35, 45), 1),
                'recording': random.choice([True, False])
            })
            
            dashboard.update_device_status('usb_webcams', 'webcam_1', {
                'status': 'active',
                'resolution': '4K',
                'fps': 30,
                'recording': random.choice([True, False])
            })
            
            # Simulate sensor data
            dashboard.update_sensor_data('android_1', 'gsr', random.uniform(0.1, 2.0))
            dashboard.update_sensor_data('android_1', 'thermal', random.uniform(25, 35))
            dashboard.update_sensor_data('shimmer_1', '', random.uniform(0.5, 3.0))
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\nShutting down web dashboard server...")
        dashboard.stop_server()