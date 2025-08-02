#!/usr/bin/env python3
"""
Web Dashboard Launcher for Multi-Sensor Recording System

This script provides a standalone launcher for the web-based dashboard.
It can be used to start the web interface independently of the main
PyQt5 desktop application.

Usage:
    python web_launcher.py [--port PORT] [--host HOST] [--debug]

Author: Multi-Sensor Recording System Team
Date: 2025-08-02
"""

import argparse
import os
import sys
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from web_ui.integration import WebDashboardIntegration
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError as e:
    print(f"Import error: {e}")
    print("Installing required dependencies...")
    
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-socketio", "eventlet"])
        print("Dependencies installed. Please run the script again.")
        sys.exit(0)
    except Exception as install_error:
        print(f"Failed to install dependencies: {install_error}")
        sys.exit(1)


def main():
    """Main entry point for the web dashboard launcher."""
    parser = argparse.ArgumentParser(
        description="Multi-Sensor Recording System Web Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python web_launcher.py                    # Start with default settings
  python web_launcher.py --port 8080       # Start on port 8080
  python web_launcher.py --host 0.0.0.0    # Allow external connections
  python web_launcher.py --debug           # Enable debug mode
        """
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=5000,
        help="Port to run the web server on (default: 5000)"
    )
    
    parser.add_argument(
        "--host", "-H",
        type=str,
        default="0.0.0.0",
        help="Host address to bind to (default: 0.0.0.0 for all interfaces)"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--no-demo-data",
        action="store_true",
        help="Disable demo data generation"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Multi-Sensor Recording System - Web Dashboard")
    print("=" * 60)
    print(f"Starting web dashboard on {args.host}:{args.port}")
    print(f"Debug mode: {'Enabled' if args.debug else 'Disabled'}")
    print(f"Demo data: {'Disabled' if args.no_demo_data else 'Enabled'}")
    print()
    
    # Create and start the web dashboard
    try:
        integration = WebDashboardIntegration(
            enable_web_ui=True,
            web_port=args.port
        )
        
        if integration.start_web_dashboard():
            dashboard_url = integration.get_web_dashboard_url()
            print(f"✓ Web dashboard started successfully!")
            print(f"✓ Access the dashboard at: {dashboard_url}")
            print()
            print("Available pages:")
            print(f"  • Main Dashboard: {dashboard_url}/")
            print(f"  • Device Management: {dashboard_url}/devices")
            print(f"  • Session History: {dashboard_url}/sessions")
            print()
            
            if not args.no_demo_data:
                print("📊 Demo data generation is active")
                print("   - Simulated device status updates")
                print("   - Real-time sensor data streams")
                print("   - Mock session information")
                print()
            
            print("Press Ctrl+C to stop the server...")
            print("-" * 60)
            
            # Keep the server running
            try:
                while integration.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n" + "=" * 60)
                print("Shutting down web dashboard...")
                integration.stop_web_dashboard()
                print("✓ Web dashboard stopped successfully")
                print("Thank you for using the Multi-Sensor Recording System!")
                print("=" * 60)
        
        else:
            print("✗ Failed to start web dashboard")
            print("Please check the logs for more information")
            sys.exit(1)
    
    except Exception as e:
        print(f"✗ Error starting web dashboard: {e}")
        logger.error(f"Web dashboard startup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()