import os
import sys
import tkinter as tk
import threading
import uvicorn
import configparser
import webbrowser
from datetime import datetime
from loguru import logger
from database import init_db

# Needed for multiprocessing with PyInstaller
import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()

# Fix for PyInstaller packages
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Running as PyInstaller bundle
    bundle_dir = sys._MEIPASS
    os.chdir(os.path.dirname(sys.executable))
    sys.path.append(os.path.dirname(sys.executable))

# Make sure we can use the application as a module
parent_dir = os.path.dirname(os.path.realpath(__file__))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Global variables
server_thread = None
is_server_running = False


# Simple console logger for the GUI app
class SimpleLogger:
    def __init__(self):
        pass

    def write(self, message):
        """Log to console"""
        print(message)

    def flush(self):
        """Flush the stream"""
        sys.stdout.flush()


def create_required_directories():
    """Create required directories for the application"""
    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Create data directory from config
    config = configparser.ConfigParser()
    config.read("config.ini")
    data_folder = config.get("storage", "save_folder", fallback="data")
    os.makedirs(data_folder, exist_ok=True)


def setup_logging():
    """Setup logger with daily rotation"""
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    log_file = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"

    logger.remove()  # Remove default handler
    logger.add(log_file, rotation="00:00", format=log_format, level="INFO")

    # Add console handler
    logger.add(lambda msg: print(msg), format=log_format, level="INFO")


def start_server(host, port):
    """Start the FastAPI server"""
    global is_server_running

    try:
        # Initialize database
        init_db()

        # Start the server
        logger.info(f"Starting Dikontenin Helper server at http://{host}:{port}")

        # Set server running flag
        is_server_running = True

        # Check if API module can be found in different locations
        import os

        # Try to find the api.py file
        api_file = "api.py"
        if not os.path.exists(api_file) and getattr(sys, "frozen", False):
            api_file = os.path.join(os.path.dirname(sys.executable), "api.py")
            logger.info(f"Looking for API module at {api_file}")

        if os.path.exists(api_file):
            logger.info(f"Found API module at {api_file}")
        else:
            logger.info(f"API module not found at {api_file}")
            # Look in other common locations
            possible_paths = [
                ".",
                os.path.dirname(sys.executable),
                getattr(sys, "_MEIPASS", ""),
            ]

            for path in possible_paths:
                test_path = os.path.join(path, "api.py")
                if os.path.exists(test_path):
                    api_file = test_path
                    logger.info(f"Found API module at {api_file}")
                    break

        # Run uvicorn
        uvicorn.run("api:app", host=host, port=port, log_level="warning")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
    finally:
        is_server_running = False


def create_gui():
    """Create ultra-compact GUI window with minimal controls"""
    # Create basic root window
    root = tk.Tk()
    root.title("Dikontenin Helper")
    root.geometry("320x120")  # Much smaller
    root.resizable(False, False)
    
    # Set the window icon to use favicon.ico
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "favicon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    else:
        logger.warning(f"Icon file not found at {icon_path}")

    # Read configuration
    config = configparser.ConfigParser()
    config.read("config.ini")
    default_host = config.get("server", "host", fallback="127.0.0.1")
    default_port = config.get("server", "port", fallback="8000")

    # Create frames with absolute minimal padding
    top_frame = tk.Frame(root)
    top_frame.pack(fill=tk.X, padx=2, pady=1)

    # Host and port in one line
    tk.Label(top_frame, text="Host:").grid(row=0, column=0)
    host_entry = tk.Entry(top_frame, width=15)
    host_entry.grid(row=0, column=1, padx=2)
    host_entry.insert(0, default_host)

    tk.Label(top_frame, text="Port:").grid(row=0, column=2, padx=1)
    port_entry = tk.Entry(top_frame, width=5)
    port_entry.grid(row=0, column=3)
    port_entry.insert(0, default_port)

    # Status display
    status_frame = tk.Frame(root)
    status_frame.pack(fill=tk.X, pady=1)

    tk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
    status_var = tk.StringVar()
    status_var.set("Ready")
    status_label = tk.Label(status_frame, textvariable=status_var)
    status_label.pack(side=tk.LEFT)

    # Button frame with no padding
    button_frame = tk.Frame(root)
    button_frame.pack(fill=tk.X)

    # Second button frame for utility buttons
    util_frame = tk.Frame(root)
    util_frame.pack(fill=tk.X, pady=1)

    def start_server_click():
        """Start server button callback"""
        global server_thread, is_server_running

        # Double-check server status before starting
        if check_server_status():
            logger.info("Server is already running!")
            return

        # Temporarily disable both buttons during startup
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.DISABLED)
        status_var.set("Starting...")

        # Get host and port
        host = host_entry.get().strip()
        try:
            port = int(port_entry.get().strip())
        except ValueError:
            logger.error("Error: Port must be a number")
            status_var.set("Error: Port must be a number")
            start_button.config(state=tk.NORMAL)
            return

        # Check if port is available before trying to start
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.bind((host, port))
            sock.close()
        except OSError:
            logger.error(f"Port {port} is already in use or not available")
            status_var.set(f"Error: Port {port} in use")
            start_button.config(state=tk.NORMAL)
            return

        # Save configuration
        config = configparser.ConfigParser()
        config.read("config.ini")
        if not config.has_section("server"):
            config.add_section("server")
        config.set("server", "host", host)
        config.set("server", "port", str(port))
        with open("config.ini", "w") as f:
            config.write(f)

        # Start server in a thread
        server_thread = threading.Thread(
            target=start_server, args=(host, port), daemon=True
        )
        server_thread.start()

        # Wait a moment then check if server actually started
        def check_startup_status():
            import time

            time.sleep(2)  # Give the server time to start
            if check_server_status():
                logger.info("Server successfully started")
            else:
                logger.error("Server failed to start properly")
                status_var.set("Error: Failed to start")
                start_button.config(state=tk.NORMAL)
                stop_button.config(state=tk.DISABLED)

        threading.Thread(target=check_startup_status, daemon=True).start()

    def check_server_status():
        """Check if server is responding and update UI accordingly"""
        global is_server_running
        host = host_entry.get().strip()
        port = port_entry.get().strip()

        try:
            import socket
            import urllib.request
            import urllib.error

            # Try to connect to the server with a short timeout
            try:
                response = urllib.request.urlopen(
                    f"http://{host}:{port}/api/status", timeout=0.5
                )
                if response.getcode() == 200:
                    is_server_running = True
                    start_button.config(state=tk.DISABLED)
                    stop_button.config(state=tk.NORMAL)
                    browser_button.config(state=tk.NORMAL)
                    status_var.set("Running")
                    return True
            except (urllib.error.URLError, ConnectionRefusedError, socket.timeout):
                # Server is not responding
                pass

            # Server is not running
            is_server_running = False
            start_button.config(state=tk.NORMAL)
            stop_button.config(state=tk.DISABLED)
            browser_button.config(state=tk.DISABLED)
            status_var.set("Stopped")
            return False

        except Exception as e:
            logger.error(f"Error checking server status: {str(e)}")
            return False

    def stop_server_click():
        """Stop server button callback"""
        global server_thread, is_server_running

        if not is_server_running:
            logger.info("Server is not running!")
            return

        # Disable both buttons during shutdown to prevent double-clicking
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.DISABLED)
        status_var.set("Stopping...")

        # Get server config for the shutdown URL
        host = host_entry.get().strip()
        port = port_entry.get().strip()

        # Call the API shutdown endpoint to properly close Chrome
        try:
            import urllib.request

            shutdown_url = f"http://{host}:{port}/api/shutdown"
            logger.info(f"Sending shutdown request to {shutdown_url}")
            urllib.request.urlopen(shutdown_url)
            logger.info("Sent shutdown request to close browser")
        except Exception as e:
            logger.error(f"Failed to send shutdown request: {str(e)}")

        # Stop server
        logger.info("Stopping server...")
        is_server_running = False
        server_thread = None

        # Wait a moment for the server to actually stop
        def update_ui_after_shutdown():
            # Wait a bit for the port to be released
            import time

            time.sleep(1.5)

            # Check actual server status and update UI
            if not check_server_status():
                logger.info("Server stopped.")
            else:
                logger.error("Server failed to stop properly!")
                # Force the UI to show correct state
                is_server_running = False
                start_button.config(state=tk.NORMAL)
                stop_button.config(state=tk.DISABLED)
                browser_button.config(state=tk.DISABLED)
                status_var.set("Error - Restart App")

        # Run the UI update in a separate thread to not block the GUI
        threading.Thread(target=update_ui_after_shutdown, daemon=True).start()

    def open_browser():
        """Open browser to access the web interface"""
        host = host_entry.get()
        port = port_entry.get()
        url = f"http://{host}:{port}"
        webbrowser.open(url)

    def open_config():
        """Open the configuration file in default text editor"""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "config.ini"
            )
            os.startfile(config_path)
        except Exception as e:
            logger.error(f"Error opening config file: {str(e)}")

    # Plain basic buttons with explicit border and height to ensure visibility
    start_button = tk.Button(
        button_frame,
        text="START",
        command=start_server_click,
        bg="#9dff9d",
        height=2,
        borderwidth=2,
    )
    start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1, pady=1)

    stop_button = tk.Button(
        button_frame,
        text="STOP",
        command=stop_server_click,
        bg="#ff9d9d",
        height=2,
        borderwidth=2,
        state=tk.DISABLED,
    )
    stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1, pady=1)

    browser_button = tk.Button(
        button_frame,
        text="BROWSER",
        command=open_browser,
        bg="#9d9dff",
        height=2,
        borderwidth=2,
        state=tk.DISABLED,
    )
    browser_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1, pady=1)

    # Config button - utility button to open config file
    config_button = tk.Button(
        util_frame,
        text="EDIT CONFIG",
        command=open_config,
        bg="#f0f0f0",
        height=1,
        borderwidth=1,
    )
    config_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1, pady=1)

    # Create a minimalist footer with version
    footer = tk.Label(root, text="Dikontenin Helper v1.0", font=("Arial", 7))
    footer.pack(side=tk.BOTTOM, pady=0)

    # Create directories
    create_required_directories()
    setup_logging()

    return root


def main():
    """Main entry point for the application"""
    try:
        # Create and start the GUI
        root = create_gui()
        root.mainloop()

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
