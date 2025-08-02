#!/usr/bin/env python3
"""
Real System Monitoring Module for Multi-Sensor Recording System

This module provides actual system monitoring capabilities including:
- Real hardware device detection (webcams, Bluetooth devices)
- System resource monitoring (CPU, memory, disk, network)
- Platform information and hardware specifications
- Process monitoring and performance metrics

Author: Multi-Sensor Recording System Team
Date: 2025-08-02
"""

import os
import platform
import subprocess
import sys
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    import psutil
except ImportError:
    print("psutil not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class SystemMonitor:
    """Real system monitoring and hardware detection."""
    
    def __init__(self):
        """Initialize the system monitor."""
        self.monitoring = False
        self.monitor_thread = None
        self.system_info = self._get_system_info()
        self._last_update = time.time()
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        try:
            return {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'hostname': platform.node(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'memory_total': psutil.virtual_memory().total,
                'boot_time': psutil.boot_time(),
                'opencv_available': OPENCV_AVAILABLE
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def get_cpu_usage(self) -> Dict[str, Any]:
        """Get current CPU usage information."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            cpu_stats = psutil.cpu_stats()
            
            return {
                'usage_percent': cpu_percent,
                'frequency_current': cpu_freq.current if cpu_freq else 0,
                'frequency_min': cpu_freq.min if cpu_freq else 0,
                'frequency_max': cpu_freq.max if cpu_freq else 0,
                'ctx_switches': cpu_stats.ctx_switches,
                'interrupts': cpu_stats.interrupts,
                'soft_interrupts': cpu_stats.soft_interrupts,
                'syscalls': cpu_stats.syscalls,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            return {'usage_percent': 0}
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage information."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'buffers': getattr(memory, 'buffers', 0),
                'cached': getattr(memory, 'cached', 0),
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {'total': 0, 'used': 0, 'percent': 0}
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information for all mounted drives."""
        try:
            disk_info = {}
            
            # Get disk usage for all partitions
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': round((usage.used / usage.total) * 100, 2) if usage.total > 0 else 0
                    }
                except (PermissionError, OSError):
                    # Skip inaccessible partitions
                    continue
            
            # Get disk I/O statistics
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    disk_info['io_stats'] = {
                        'read_count': disk_io.read_count,
                        'write_count': disk_io.write_count,
                        'read_bytes': disk_io.read_bytes,
                        'write_bytes': disk_io.write_bytes,
                        'read_time': disk_io.read_time,
                        'write_time': disk_io.write_time
                    }
            except Exception:
                pass
            
            return disk_info
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network interface and usage information."""
        try:
            network_info = {}
            
            # Get network interface statistics
            net_io = psutil.net_io_counters(pernic=True)
            for interface, stats in net_io.items():
                network_info[interface] = {
                    'bytes_sent': stats.bytes_sent,
                    'bytes_recv': stats.bytes_recv,
                    'packets_sent': stats.packets_sent,
                    'packets_recv': stats.packets_recv,
                    'errin': stats.errin,
                    'errout': stats.errout,
                    'dropin': stats.dropin,
                    'dropout': stats.dropout
                }
            
            # Get network addresses
            try:
                net_addrs = psutil.net_if_addrs()
                for interface, addrs in net_addrs.items():
                    if interface in network_info:
                        network_info[interface]['addresses'] = []
                        for addr in addrs:
                            network_info[interface]['addresses'].append({
                                'family': str(addr.family),
                                'address': addr.address,
                                'netmask': addr.netmask,
                                'broadcast': addr.broadcast
                            })
            except Exception:
                pass
            
            return network_info
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
            return {}
    
    def detect_webcams(self) -> List[Dict[str, Any]]:
        """Detect available webcams using OpenCV."""
        if not OPENCV_AVAILABLE:
            logger.warning("OpenCV not available, cannot detect webcams")
            return []
        
        webcams = []
        try:
            # Test up to 10 possible camera indices
            for index in range(10):
                cap = cv2.VideoCapture(index)
                if cap.isOpened():
                    # Get camera properties
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    
                    webcams.append({
                        'index': index,
                        'name': f"Camera {index}",
                        'resolution': f"{width}x{height}",
                        'fps': fps,
                        'status': 'available'
                    })
                    cap.release()
                else:
                    cap.release()
                    break  # Stop checking once we find a gap
            
            logger.info(f"Detected {len(webcams)} webcam(s)")
            return webcams
        except Exception as e:
            logger.error(f"Error detecting webcams: {e}")
            return []
    
    def detect_bluetooth_devices(self) -> List[Dict[str, Any]]:
        """Detect available Bluetooth devices."""
        bluetooth_devices = []
        try:
            if platform.system() == "Linux":
                # Use bluetoothctl on Linux
                try:
                    result = subprocess.run(['bluetoothctl', 'list'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'Controller' in line:
                                parts = line.split()
                                if len(parts) >= 3:
                                    mac = parts[1]
                                    name = ' '.join(parts[2:])
                                    bluetooth_devices.append({
                                        'mac': mac,
                                        'name': name,
                                        'type': 'controller',
                                        'status': 'available'
                                    })
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            
            elif platform.system() == "Windows":
                # Use PowerShell on Windows to detect Bluetooth devices
                try:
                    result = subprocess.run([
                        'powershell', '-Command',
                        'Get-PnpDevice | Where-Object {$_.Class -eq "Bluetooth"} | Select-Object Name, Status'
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')[3:]  # Skip header
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('-'):
                                parts = line.split()
                                if len(parts) >= 2:
                                    status = parts[-1]
                                    name = ' '.join(parts[:-1])
                                    bluetooth_devices.append({
                                        'name': name,
                                        'status': status.lower(),
                                        'type': 'device'
                                    })
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            
            logger.info(f"Detected {len(bluetooth_devices)} Bluetooth device(s)")
            return bluetooth_devices
        except Exception as e:
            logger.error(f"Error detecting Bluetooth devices: {e}")
            return []
    
    def get_process_info(self) -> List[Dict[str, Any]]:
        """Get information about running processes related to our application."""
        try:
            processes = []
            current_pid = os.getpid()
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    proc_info = proc.info
                    # Include Python processes and our own process
                    if (proc_info['name'].lower().startswith('python') or 
                        proc_info['pid'] == current_pid or
                        'bucika' in proc_info['name'].lower()):
                        
                        processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'cpu_percent': proc_info['cpu_percent'],
                            'memory_percent': proc_info['memory_percent'],
                            'create_time': proc_info['create_time'],
                            'is_current': proc_info['pid'] == current_pid
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return processes
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            return []
    
    def get_temperature_info(self) -> Dict[str, Any]:
        """Get system temperature information if available."""
        try:
            temps = {}
            if hasattr(psutil, 'sensors_temperatures'):
                temperatures = psutil.sensors_temperatures()
                for name, entries in temperatures.items():
                    temps[name] = []
                    for entry in entries:
                        temps[name].append({
                            'label': entry.label,
                            'current': entry.current,
                            'high': entry.high,
                            'critical': entry.critical
                        })
            return temps
        except Exception as e:
            logger.error(f"Error getting temperature info: {e}")
            return {}
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including all monitored metrics."""
        current_time = time.time()
        
        status = {
            'timestamp': current_time,
            'system_info': self.system_info,
            'cpu': self.get_cpu_usage(),
            'memory': self.get_memory_usage(),
            'disk': self.get_disk_usage(),
            'network': self.get_network_info(),
            'webcams': self.detect_webcams(),
            'bluetooth': self.detect_bluetooth_devices(),
            'processes': self.get_process_info(),
            'temperature': self.get_temperature_info(),
            'uptime': current_time - self.system_info.get('boot_time', current_time)
        }
        
        self._last_update = current_time
        return status


# Global system monitor instance
_system_monitor = None

def get_system_monitor() -> SystemMonitor:
    """Get the global system monitor instance."""
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
    return _system_monitor