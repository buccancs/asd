# Multi-Sensor Recording System - Web Dashboard

A comprehensive web-based monitoring and control interface for the multi-sensor recording system, providing real-time device monitoring, session management, file operations, and system configuration through a modern browser interface.

![Web Dashboard](https://github.com/user-attachments/assets/57b0d263-e6f8-4040-a43d-c0ec3f226090)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation & Setup](#installation--setup)
- [Quick Start Guide](#quick-start-guide)
- [Tab-by-Tab Feature Guide](#tab-by-tab-feature-guide)
- [API Documentation](#api-documentation)
- [System Monitoring](#system-monitoring)
- [Network Protocol Integration](#network-protocol-integration)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Technical Architecture](#technical-architecture)

## Overview

The Web Dashboard provides a modern, responsive web interface that complements the existing PyQt5 desktop application. It enables remote monitoring and control of the multi-sensor recording system through any modern web browser, making it ideal for:

- **Remote monitoring** of recording sessions
- **Mobile device access** via tablets and smartphones
- **Headless server deployments** without GUI requirements
- **Multi-user access** for team collaboration
- **Real-time system monitoring** and device status tracking

## Features

### 🎯 Complete Feature Parity
- All desktop application functionality available through web interface
- Real-time data streaming and device status monitoring
- Session management with start/stop controls
- Comprehensive device configuration and testing
- File management and data export capabilities

### 📱 Modern Web Interface
- **Responsive design** - Works on desktop, tablet, and mobile devices
- **Real-time updates** - WebSocket-powered live data streaming
- **Progressive enhancement** - Graceful fallback for older browsers
- **Dark/light themes** - Customizable interface appearance

### 🔌 Hardware Integration
- **Real device detection** - Actual webcam, Bluetooth, and system monitoring
- **Live sensor data** - Real-time GSR, thermal, and physiological data
- **Network protocol compliance** - Direct integration with Android app communication
- **System resource monitoring** - CPU, memory, disk, and network usage

## Installation & Setup

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Required Python packages
pip install flask flask-socketio eventlet psutil opencv-python
```

### Installation Steps

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/buccancs/bucika_gsr.git
   cd bucika_gsr/PythonApp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # OR individual packages:
   pip install flask flask-socketio eventlet psutil opencv-python
   ```

3. **Verify system monitoring**:
   ```bash
   python -c "from src.utils.system_monitor import get_system_monitor; print('System monitoring available')"
   ```

### Launch Options

#### Option 1: Standalone Web Server
```bash
cd PythonApp/src
python web_launcher.py
```

#### Option 2: Integrated with Desktop App
```bash
cd PythonApp/src
python enhanced_main_with_web.py --enable-web
```

#### Option 3: Web-Only Mode
```bash
cd PythonApp/src/web_ui
python web_dashboard.py
```

## Quick Start Guide

### 1. Access the Dashboard
Open your web browser and navigate to:
```
http://localhost:5000
```

### 2. System Status Check
- Visit the **Dashboard** tab to see real-time system status
- Check device connections in the **Devices** tab
- Verify system monitoring data is updating

### 3. Connect Devices
- **Android Devices**: Use network discovery in Devices tab
- **Shimmer Sensors**: Pair via Bluetooth in Devices tab  
- **USB Webcams**: Auto-detected and listed in Devices tab

### 4. Start Recording
- Go to **Sessions** tab
- Click "New Session" and configure settings
- Select connected devices
- Click "Start Recording"

### 5. Monitor Progress
- Real-time session monitoring in Dashboard tab
- Live sensor data visualization
- Device status and connection monitoring

## Tab-by-Tab Feature Guide

### 🏠 Dashboard Tab
**Primary monitoring interface with real-time system overview**

**Features:**
- **Session Controls**: Start/stop recording with one-click
- **Device Status Grid**: Live status of all connected devices
- **System Metrics**: CPU, memory, disk, network monitoring  
- **Sensor Data Visualization**: Real-time GSR, thermal, heart rate charts
- **Connection Status**: Network connectivity and device health
- **Quick Actions**: Fast access to common operations

**Usage:**
1. Monitor overall system health at a glance
2. Start/stop recording sessions quickly
3. View live sensor data from all devices
4. Check system resource usage

### 📱 Devices Tab
**Comprehensive device management and configuration**

**Features:**
- **Android Device Management**:
  - Network discovery and connection
  - Device configuration (GSR, thermal, camera settings)
  - Battery and connection status monitoring
  - Sensor calibration and testing
  
- **USB Webcam Control**:
  - Automatic detection of available cameras
  - Resolution and FPS configuration
  - Live preview and testing
  - Format and codec selection
  
- **Shimmer Sensor Integration**:
  - Bluetooth pairing and connection
  - Sample rate and sensor configuration
  - Battery level monitoring
  - Signal quality assessment
  
- **PC System Monitoring**:
  - Real-time CPU, memory, disk usage
  - Network interface statistics
  - Process monitoring
  - Temperature sensors (if available)

**Usage:**
1. **Connect Android Device**: Click "Connect" → Enter IP address → Configure sensors
2. **Setup Webcam**: Select camera → Test functionality → Configure quality settings
3. **Pair Shimmer**: Enable Bluetooth discovery → Select sensor → Configure sampling
4. **Monitor System**: View real-time PC performance metrics

### 📝 Sessions Tab
**Complete session lifecycle management**

**Features:**
- **Current Session Monitoring**:
  - Live session statistics and duration
  - Real-time device recording status
  - Data size and quality metrics
  - Session timeline visualization
  
- **Session History**:
  - Browse all recorded sessions
  - Session metadata and statistics
  - Quick preview of session data
  - Export and sharing options
  
- **Session Creation**:
  - Guided session setup wizard
  - Device selection and configuration
  - Recording parameters and quality settings
  - Schedule and automation options

**Usage:**
1. **New Session**: Click "New Session" → Name session → Select devices → Configure settings → Start
2. **Monitor Active**: View progress, data rates, and device status during recording
3. **Browse History**: Review past sessions, view metadata, export data
4. **Session Analysis**: Quick metrics and data quality assessment

### 🎬 Playback Tab
**Advanced session analysis and data replay**

**Features:**
- **Multi-Camera Video Synchronization**:
  - Synchronized playback of multiple video streams
  - Frame-accurate seeking and navigation
  - Speed control (0.25x to 4x playback speed)
  - Picture-in-picture viewing modes
  
- **Sensor Data Visualization**:
  - Real-time sensor data overlay during playback
  - Interactive charts for GSR, thermal, physiological data
  - Data correlation and trend analysis
  - Custom time range selection
  
- **Session Analysis Tools**:
  - Export specific time segments
  - Data quality assessment and sync analysis
  - Statistical analysis and reporting
  - Custom annotation and marking

**Usage:**
1. **Load Session**: Select session from dropdown → Load video and sensor data
2. **Synchronized Playback**: Play multiple camera streams in sync with sensor data
3. **Analysis**: Use timeline controls to analyze specific events
4. **Export**: Select time ranges and export video/data segments

### 📁 File Viewer Tab
**Comprehensive file management and data browser**

**Features:**
- **File Browser**:
  - Navigate recording directories
  - Breadcrumb navigation
  - File type filtering and search
  - Grid and list view modes
  
- **File Preview**:
  - Video preview with thumbnails
  - Text file content display
  - JSON data formatting and syntax highlighting
  - Image preview and metadata
  
- **Bulk Operations**:
  - Multi-file selection and operations
  - Bulk download as ZIP archives
  - Batch delete and organization
  - Copy and move operations
  
- **Upload and Management**:
  - Drag-and-drop file uploads
  - Folder creation and organization
  - File properties and metadata editing
  - Storage usage monitoring

**Usage:**
1. **Browse Files**: Navigate through recording directories using breadcrumbs
2. **Preview Content**: Click files to preview videos, images, or text content
3. **Bulk Operations**: Select multiple files → Download as ZIP or delete
4. **Upload Data**: Drag files to upload area or use upload button

### ⚙️ Settings Tab
**Complete system configuration and preferences**

**Features:**
- **General Settings**:
  - Interface theme (dark/light mode)
  - Language and localization
  - Auto-save preferences
  - Notification settings
  
- **Recording Configuration**:
  - Default video quality and resolution
  - Audio recording settings
  - Compression levels and formats
  - Maximum session duration
  
- **Device-Specific Settings**:
  - Android app communication ports
  - Shimmer sensor default configurations
  - Webcam quality presets
  - Connection timeout settings
  
- **Network Configuration**:
  - Server ports and addresses
  - SSL/TLS encryption settings
  - Data compression options
  - Network discovery settings
  
- **Storage Management**:
  - Recording storage locations
  - Automatic cleanup policies
  - Disk space monitoring
  - Backup configurations
  
- **System Settings**:
  - Debug mode and logging levels
  - Memory usage limits
  - Worker thread configuration
  - Performance optimization

**Usage:**
1. **Interface**: Customize theme, language, and UI preferences
2. **Recording**: Set default quality, format, and duration settings
3. **Network**: Configure ports, security, and communication settings
4. **Storage**: Manage disk usage, cleanup policies, and backup options

## API Documentation

### REST API Endpoints

#### Device Management
```http
POST /api/device/connect
{
  "device_id": "android_1",
  "device_type": "android"
}

POST /api/device/configure
{
  "device_id": "webcam_0",
  "device_type": "webcam",
  "configuration": {
    "resolution": "1920x1080",
    "fps": 30
  }
}

GET /api/system/status
# Returns comprehensive system monitoring data
```

#### Session Control
```http
POST /api/session/start
{
  "session_id": "session_20250802_001",
  "devices": ["android_1", "webcam_0"]
}

POST /api/session/stop
{
  "session_id": "session_20250802_001"
}

GET /api/sessions
# Returns list of all sessions
```

#### File Operations
```http
GET /api/files/browse?path=/recordings
# Browse files in directory

GET /api/files/content?path=/path/to/file.txt
# Get file content for preview

GET /api/files/download?path=/path/to/file.mp4
# Download file
```

### WebSocket Events

#### Real-time Data Streaming
```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Device status updates
socket.on('device_status', (data) => {
  console.log('Device status:', data);
});

// Sensor data streaming
socket.on('sensor_data', (data) => {
  console.log('Sensor data:', data);
});

// Session status changes
socket.on('session_status', (data) => {
  console.log('Session status:', data);
});
```

## System Monitoring

### Real-Time Metrics

The web dashboard provides comprehensive system monitoring through the integrated SystemMonitor class:

**CPU Monitoring:**
- Real-time usage percentage
- Core-specific metrics
- Frequency and load average
- Context switches and interrupts

**Memory Monitoring:**
- Total, used, and available memory
- Swap usage statistics
- Buffer and cache information
- Memory percentage utilization

**Disk Monitoring:**
- Per-partition usage statistics
- I/O operations and bandwidth
- Free space monitoring
- Read/write performance metrics

**Network Monitoring:**
- Interface-specific statistics
- Bytes sent/received counters
- Packet loss and error rates
- Network address information

**Device Detection:**
- Real webcam detection via OpenCV
- Bluetooth device discovery
- Hardware sensor monitoring
- Process monitoring and tracking

### Hardware Integration

**Webcam Detection:**
```python
# Automatic detection of available cameras
webcams = system_monitor.detect_webcams()
# Returns: [{'index': 0, 'name': 'Camera 0', 'resolution': '1920x1080', 'fps': 30.0}]
```

**Bluetooth Devices:**
```python
# Cross-platform Bluetooth discovery
bluetooth_devices = system_monitor.detect_bluetooth_devices()
# Returns device list with MAC addresses and capabilities
```

**System Resources:**
```python
# Comprehensive system status
status = system_monitor.get_comprehensive_status()
# Returns CPU, memory, disk, network, temperature, and process info
```

## Network Protocol Integration

### Android Device Communication

The web dashboard integrates with the existing JSON socket protocol for Android device communication:

**Connection Flow:**
1. **Discovery**: Web UI scans for Android devices on local network
2. **Handshake**: Establishes connection using JSON socket protocol
3. **Configuration**: Sends device-specific settings via JSON messages
4. **Data Streaming**: Receives real-time sensor data from Android apps
5. **Session Control**: Sends start/stop recording commands

**Message Format:**
```json
{
  "type": "session_control",
  "action": "start_recording",
  "session_id": "session_20250802_001",
  "timestamp": 1659456789.123,
  "parameters": {
    "duration": 1800,
    "sensors": ["gsr", "thermal", "camera"]
  }
}
```

### Real-Time Data Flow

**Sensor Data Streaming:**
- **GSR Data**: Real-time galvanic skin response measurements
- **Thermal Data**: Infrared temperature readings
- **Physiological Data**: Heart rate and related metrics
- **Video Streams**: Live camera feeds from Android devices

**WebSocket Integration:**
- Bidirectional communication between web UI and Python backend
- Real-time device status updates
- Live sensor data visualization
- Session progress monitoring

## Troubleshooting

### Common Issues

#### 1. Web Server Won't Start
```bash
# Check if port is already in use
netstat -an | grep :5000

# Try different port
python web_dashboard.py --port 5001
```

#### 2. No Devices Detected
```bash
# Verify system monitoring dependencies
pip install psutil opencv-python

# Test device detection
python -c "from src.utils.system_monitor import get_system_monitor; print(get_system_monitor().detect_webcams())"
```

#### 3. Android Devices Not Connecting
- Ensure devices are on same network
- Check firewall settings (port 9000)
- Verify Android app is running and configured
- Check network discovery in Devices tab

#### 4. WebSocket Connection Failed
- Check browser console for errors
- Verify Flask-SocketIO is installed
- Try refreshing the page
- Check network connectivity

#### 5. System Monitoring Not Working
```bash
# Install missing dependencies
pip install psutil

# For webcam detection
pip install opencv-python

# Test system monitor
python -c "from src.utils.system_monitor import SystemMonitor; s = SystemMonitor(); print(s.get_cpu_usage())"
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set environment variable
export WEB_DEBUG=true

# Or pass command line argument
python web_dashboard.py --debug
```

## Technical Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Web Browser                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │Dashboard│ │ Devices │ │Sessions │ │Playback │ ...  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │
└─────────────────────────────────────────────────────────┘
                           │
                    WebSocket + REST API
                           │
┌─────────────────────────────────────────────────────────┐
│                Web Dashboard Server                     │
│  ┌─────────────────┐    ┌─────────────────┐           │
│  │  Flask Server   │    │   SocketIO      │           │
│  │  (REST API)     │    │ (Real-time)     │           │
│  └─────────────────┘    └─────────────────┘           │
└─────────────────────────────────────────────────────────┘
                           │
                   Python Backend
                           │
┌─────────────────────────────────────────────────────────┐
│                Backend Services                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │SessionMngr  │ │ShimmerMngr  │ │AndroidMngr  │ ...  │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
└─────────────────────────────────────────────────────────┘
                           │
                   Hardware Layer
                           │
┌─────────────────────────────────────────────────────────┐
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │   Webcams   │ │  Shimmer    │ │  Android    │      │
│  │             │ │  Sensors    │ │  Devices    │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
└─────────────────────────────────────────────────────────┘
```

**Multi-Sensor Recording System Web Dashboard** - Providing comprehensive web-based monitoring and control for multi-sensor research applications.

Once the server is running, access the dashboard at:
- **Main Dashboard**: `http://localhost:5000/`
- **Device Management**: `http://localhost:5000/devices`
- **Session History**: `http://localhost:5000/sessions`

### Main Dashboard Features

1. **Session Control Panel**
   - Start/stop recording sessions
   - View current session status and duration
   - Monitor active recording devices

2. **System Overview Cards**
   - Device count summaries
   - Connection status indicators
   - System health metrics

3. **Device Status Grids**
   - Android devices with battery and temperature info
   - USB webcams with resolution and frame rate details
   - PC controller system resources

4. **Real-time Data Visualization**
   - GSR sensor data charts with multiple device support
   - Thermal data visualization
   - Live updating charts with smooth animations

### Device Management

- **Android Devices**: Connection status, battery level, temperature monitoring
- **USB Webcams**: Resolution settings, frame rate configuration, recording status
- **Shimmer Sensors**: Bluetooth connectivity, battery status, signal strength
- **PC Controller**: CPU usage, memory consumption, system status

### Session Management

- **Start New Sessions**: Configure devices and recording parameters
- **Monitor Progress**: Real-time session statistics and data collection metrics
- **Session History**: Browse past sessions with detailed information
- **Data Export**: Access recorded data and session logs

## API Endpoints

### Device Status
- `GET /api/status` - Overall system status
- `GET /api/devices` - All device information

### Session Management
- `GET /api/session` - Current session info
- `POST /api/session/start` - Start new recording session
- `POST /api/session/stop` - Stop current session

### Real-time Data
- `GET /api/data/realtime` - Recent sensor data for visualization

## WebSocket Events

### Client to Server
- `connect` - Client connection
- `request_device_status` - Request current device status
- `request_session_info` - Request session information

### Server to Client
- `status_update` - Complete system status update
- `device_status_update` - Individual device status change
- `sensor_data_update` - Real-time sensor data point
- `session_info_update` - Session information change

## Integration with Existing System

The web UI is designed to complement, not replace, the existing PyQt5 desktop application. Integration options include:

### 1. Minimal Integration
Add web dashboard as an optional feature:

```python
from web_ui.integration import get_web_integration

# In your main application
web_integration = get_web_integration(enable_web_ui=True)
web_integration.start_web_dashboard()
```

### 2. Status Synchronization
Keep web dashboard updated with desktop application state:

```python
# Update device status
web_integration.update_device_status('android_devices', 'device_1', {
    'status': 'connected',
    'battery': 85,
    'recording': True
})

# Update session information
web_integration.update_session_info({
    'active': True,
    'session_id': 'session_123',
    'start_time': datetime.now().isoformat()
})

# Send real-time sensor data
web_integration.update_sensor_data('android_1', 'gsr', 1.23)
```

### 3. Menu Integration
Add web dashboard controls to desktop application menus (see `enhanced_main_with_web.py` for example).

## Configuration

### Server Settings
- **Host**: Default `0.0.0.0` (all interfaces)
- **Port**: Default `5000`
- **Debug Mode**: Disabled by default

### Demo Data
The web dashboard includes demo data generation for testing:
- Simulated device status updates
- Real-time sensor data streams
- Mock session information

Disable demo data with `--no-demo-data` flag.

## Security Considerations

- The web server binds to all interfaces (`0.0.0.0`) by default for network access
- Consider firewall rules for production deployments
- HTTPS not implemented - use reverse proxy if needed
- No authentication system - intended for trusted network environments

## Browser Compatibility

The web interface supports modern browsers with:
- Bootstrap 5.3.0 for responsive design
- Font Awesome 6.4.0 for icons
- Chart.js 4.3.0 for data visualization
- Socket.IO 4.7.2 for real-time communication

Tested on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Real-time updates every 2 seconds
- Chart data limited to last 50 points for performance
- WebSocket connections automatically managed
- Responsive design optimized for mobile devices

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```
   Error: [Errno 98] Address already in use
   ```
   Solution: Use different port with `--port` option

2. **Import errors**
   ```
   ImportError: No module named 'flask'
   ```
   Solution: Install dependencies with `pip install flask flask-socketio eventlet`

3. **Connection refused**
   - Check if server is running
   - Verify port number
   - Check firewall settings

### Debug Mode

Enable debug mode for detailed error information:
```bash
python web_launcher.py --debug
```

### Logs

Check application logs in `PythonApp/logs/` directory for detailed troubleshooting information.

## Development

### Adding New Features

1. **New API Endpoints**: Add routes to `web_dashboard.py`
2. **WebSocket Events**: Add handlers in `_setup_socket_handlers()`
3. **Frontend Features**: Modify HTML templates and JavaScript
4. **Integration**: Update `integration.py` for desktop app connectivity

### Testing

Test the web interface:
```bash
# Start with demo data
python web_launcher.py --debug

# Test API endpoints
curl http://localhost:5000/api/status

# Test WebSocket connection in browser console
var socket = io();
socket.on('connect', () => console.log('Connected'));
```

## Future Enhancements

Planned improvements include:
- User authentication and access control
- Data export functionality
- Advanced visualization options
- Mobile application integration
- Cloud deployment options
- Real-time collaboration features

## Summary

The web-based dashboard provides a modern, accessible interface for monitoring and controlling the Multi-Sensor Recording System. It complements the existing desktop application while offering new capabilities for remote monitoring and cross-platform access.

Key benefits:
- **Accessibility**: Use from any device with a web browser
- **Real-time Updates**: Live data visualization and status monitoring
- **Modern Interface**: Clean, responsive design with professional appearance
- **Easy Integration**: Minimal changes required to existing codebase
- **Standalone Operation**: Can run independently or integrated with desktop app