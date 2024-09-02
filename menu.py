import os
import subprocess
import json
from generate_syslog_logs import generate_sample_syslogs, generate_syslog_message, write_syslog_to_file
from generate_logs import (
    display_sample_log_and_curl, 
    generate_regular_log, 
    generate_suspicious_allowed_log, 
    generate_bad_traffic_log,
    start_logging_service,  # New function for starting the log service
    stop_logging_service,   # New function to stop the log service
    check_logging_service_status  # New function to check the log service status
)

# Paths to config files and directories
CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/config.json')
LOG_GENERATOR_DIR = os.path.expanduser('~/NGSIEM-Log-Generator')
LOG_COLLECTOR_DIR = os.path.expanduser('~/')

# Base LogScale configuration
BASE_LOGSCALE_CONFIG = """
dataDirectory: /var/lib/humio-log-collector
sources:
  syslogfile:
    type: syslog
    mode: udp
    port: 514
    sink: syslogsink
sinks:
  syslogsink:
    type: hec
    proxy: none
    token: <API_key_generated_during_connector_setup>
    url: <generated_API_URL>
"""

# Load configuration
def load_config():
    print("Loading configuration...")
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    print("Config file not found. Returning empty config.")
    return {}

# Save configuration
def save_config(config):
    print("Saving configuration...")
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)
    print("Configuration saved.")

# Use less for scrolling output
def pager(content):
    try:
        pager_process = subprocess.Popen(['less'], stdin=subprocess.PIPE)
        pager_process.communicate(input=content.encode('utf-8'))
    except Exception as e:
        print(f"Error using pager: {e}")

# Install LogScale log collector
def install_logscale_collector():
    print("Installing LogScale log collector...")
    try:
        os.chdir(LOG_COLLECTOR_DIR)
        print(f"Changed directory to {LOG_COLLECTOR_DIR}")
        subprocess.run(["mv", "humio-log-collector*", "humio-log-collector.deb"], check=True)
        print("Renamed humio-log-collector package.")
        subprocess.run(["sudo", "dpkg", "-i", "humio-log-collector.deb"], check=True)
        print("Installed humio-log-collector.deb.")
        subprocess.run(["sudo", "chown", "-R", "humio-log-collector:humio-log-collector", "/var/lib/humio-log-collector"], check=True)
        print("Changed ownership of /var/lib/humio-log-collector.")
        print("LogScale log collector installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during LogScale log collector installation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Edit LogScale Configuration
def edit_logscale_config():
    logscale_config_path = "/etc/humio-log-collector/config.yaml"
    print(f"Attempting to edit LogScale configuration at {logscale_config_path}...")
    try:
        check_file_exists_command = f"sudo test -f {logscale_config_path}"
        check_file_exists = subprocess.run(check_file_exists_command, shell=True, check=True)
        print("LogScale configuration file exists. Opening for editing...")
        subprocess.run(['sudo', 'nano', logscale_config_path], check=True)
        print("Configuration file edited successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to open or check configuration file: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Set LogScale configuration
def set_logscale_config():
    logscale_config_path = "/etc/humio-log-collector/config.yaml"
    print(f"Setting LogScale configuration at {logscale_config_path}...")
    confirmation = input("Proceed with setting the configuration? (yes/no): ").strip().lower()
    if confirmation == "yes":
        try:
            temp_config_path = os.path.join(LOG_GENERATOR_DIR, "temp_config.yaml")
            print(f"Creating temporary config file at {temp_config_path}...")
            with open(temp_config_path, 'w') as temp_file:
                temp_file.write(BASE_LOGSCALE_CONFIG)
            subprocess.run(['sudo', 'cp', temp_config_path, logscale_config_path], check=True)
            os.remove(temp_config_path)
            print("LogScale configuration set successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to copy configuration: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    else:
        print("Operation canceled.")

# Set file access permissions
def set_file_access_permissions():
    print("Setting file access permissions...")
    try:
        subprocess.run(['sudo', 'setcap', 'cap_dac_read_search,cap_net_bind_service+ep', '/usr/bin/humio-log-collector'], check=True)
        subprocess.run(['sudo', 'systemctl', 'restart', 'humio-log-collector'], check=True)
        print("File access permissions set and service restarted.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting file access permissions or restarting service: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Enable LogScale service
def enable_logscale_service():
    print("Enabling LogScale service...")
    try:
        subprocess.run(['sudo', 'systemctl', 'enable', '--now', 'humio-log-collector.service'], check=True)
        print("LogScale service enabled.")
    except subprocess.CalledProcessError as e:
        print(f"Error enabling LogScale service: {e}")

# Start LogScale service
def start_logscale_service():
    print("Starting LogScale service...")
    try:
        subprocess.run(['sudo', 'systemctl', 'start', 'humio-log-collector.service'], check=True)
        print("LogScale service started.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting LogScale service: {e}")

# Stop LogScale service
def stop_logscale_service():
    print("Stopping LogScale service...")
    try:
        subprocess.run(['sudo', 'systemctl', 'stop', 'humio-log-collector.service'], check=True)
        print("LogScale service stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping LogScale service: {e}")

# Check LogScale service status
def check_logscale_service_status():
    print("Checking LogScale service status...")
    try:
        result = subprocess.run(['sudo', 'systemctl', 'status', 'humio-log-collector.service'], capture_output=True, text=True, check=True)
        pager(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error checking LogScale service status: {e}")

def logscale_menu():
    while True:
        os.system('clear')
        print(f"""
╔═════════════════════════════════════════════════════════════╗
║              LogScale Configuration and Controls            ║
║═════════════════════════════════════════════════════════════║
║  Please select an option:                                   ║
║                                                             ║
║  1. Install LogScale log collector                          ║
║  2. Edit LogScale configuration file                        ║
║  3. Set file access permissions                             ║
║  4. Enable LogScale service                                 ║
║  5. Start LogScale service                                  ║
║  6. Stop LogScale service                                   ║
║  7. Check LogScale service status                           ║
║  8. Set LogScale configuration                              ║
║  0. Back to main menu                                       ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            install_logscale_collector()
        elif choice == '2':
            edit_logscale_config()
        elif choice == '3':
            set_file_access_permissions()
        elif choice == '4':
            enable_logscale_service()
        elif choice == '5':
            start_logscale_service()
        elif choice == '6':
            stop_logscale_service()
        elif choice == '7':
            check_logscale_service_status()
        elif choice == '8':
            set_logscale_config()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

# Main menu
def main_menu():
    while True:
        os.system('clear')
        print("""
╔═════════════════════════════════════════════════════════════╗
║                     NGSIEM Log Generator                    ║
║═════════════════════════════════════════════════════════════║
║  Welcome to the NGSIEM Log Generator Menu                   ║
║  Please select an option:                                   ║
║                                                             ║
║  1. Zscaler log actions                                     ║
║  2. Syslog log actions                                      ║
║  3. LogScale Configuration and Controls                    
