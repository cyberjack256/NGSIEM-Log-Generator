import os
import subprocess
import json
import glob
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

# Show current configuration
def show_config():
    config = load_config()
    filtered_config = {k: config[k] for k in ['zscaler_api_url', 'zscaler_api_key', 'observer.id', 'encounter.alias'] if k in config}
    config_str = json.dumps(filtered_config, indent=4)
    pager(config_str + "\n\nPress 'q' to exit.")

# Add configuration value
def add_config_value():
    config = load_config()
    editable_fields = ['zscaler_api_url', 'zscaler_api_key', 'observer.id', 'encounter.alias']
    print("Select a field to add or update values for:")
    for i, field in enumerate(editable_fields, 1):
        print(f"{i}. {field}")
    choice = input("Select a field: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(editable_fields):
        field = editable_fields[int(choice) - 1]
        value = input(f"Enter a value for {field}: ").strip()
        if value:
            config[field] = value
            save_config(config)
            print(f"Configuration updated: {field} set to {config[field]}")
        else:
            print("No value entered. Configuration not updated.")
    else:
        print("Invalid field choice.")

# Zscaler menu
def zscaler_menu():
    while True:
        os.system('clear')
        print(f"""
╔═════════════════════════════════════════════════════════════╗
║                     Zscaler Log Actions                     ║
║═════════════════════════════════════════════════════════════║
║  Please select an option:                                   ║
║                                                             ║
║  1. Show current configuration                              ║
║  2. Add a configuration value                               ║
║  3. Generate sample Zscaler logs                            ║
║  4. Start generating logs as a service                      ║
║  5. Stop log generation service                             ║
║  6. Check log generation service status                     ║
║  0. Back to main menu                                       ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            add_config_value()
        elif choice == '3':
            display_sample_log_and_curl()
        elif choice == '4':
            start_logging_service()  # Start generating logs as a service
        elif choice == '5':
            stop_logging_service()    # Stop the log generation service
        elif choice == '6':
            check_logging_service_status()  # Check status of the log generation service
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

# Syslog menu
def syslog_menu():
    while True:
        os.system('clear')
        print(f"""
╔═════════════════════════════════════════════════════════════╗
║                     Syslog Log Actions                      ║
║═════════════════════════════════════════════════════════════║
║  Please select an option:                                   ║
║                                                             ║
║  1. Show current configuration                              ║
║  2. Generate sample Syslog logs                             ║
║  3. Generate logs to file                                   ║
║  4. Start sending logs to syslog server                     ║
║  5. Stop sending logs to syslog server                      ║
║  6. Check logging service status                            ║
║  0. Back to main menu                                       ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            sample_logs = generate_sample_syslogs()
            if sample_logs:
                sample_log_str = json.dumps(sample_logs[0], indent=4)
                pager(f"Sample log:\n{sample_log_str}")
            else:
                print("No sample logs generated.")
        elif choice == '3':
            sample_logs = generate_sample_syslogs()
            write_syslog_to_file(sample_logs)
        elif choice == '4':
            start_logging_service()
        elif choice == '5':
            stop_logging_service()
        elif choice == '6':
            check_logging_service_status()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

# Install LogScale log collector
def install_logscale_collector():
    print("Installing LogScale log collector...")
    try:
        os.chdir(LOG_COLLECTOR_DIR)
        print(f"Changed directory to {LOG_COLLECTOR_DIR}")

        # Use glob to find the file with a dynamic version in its name
        files = glob.glob("humio-log-collector*")
        if not files:
            print("No humio-log-collector package found in the directory. Please ensure the package is available.")
            return

        # Assuming you want the first match
        package_file = files[0]
        print(f"Found humio-log-collector package: {package_file}")
        
        # Rename the file to a consistent name
        subprocess.run(["mv", package_file, "humio-log-collector.deb"], check=True)
        print("Renamed humio-log-collector package.")
        
        # Install the renamed package
        subprocess.run(["sudo", "dpkg", "-i", "humio-log-collector.deb"], check=True)
        print("Installed humio-log-collector.deb.")
        
        # Change ownership of the directory
        subprocess.run(["sudo", "chown", "-R", "humio-log-collector:humio-log-collector", "/var/lib/humio-log-collector"], check=True)
        print("Changed ownership of /var/lib/humio-log-collector.")
        
        print("LogScale log collector installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during LogScale log collector installation: {e}")
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

# View LogScale Configuration
def view_logscale_config():
    logscale_config_path = "/etc/humio-log-collector/config.yaml"
    print(f"Viewing LogScale configuration at {logscale_config_path}...")
    try:
        with open(logscale_config_path, 'r') as file:
            config_content = file.read()
        pager(config_content)
    except FileNotFoundError:
        print("LogScale configuration file not found.")
    except Exception as e:
        print(f"Error viewing LogScale configuration: {e}")

# Edit token field value
def edit_token_field_value():
    logscale_config_path = "/etc/humio-log-collector/config.yaml"
    print(f"Editing token field value in {logscale_config_path}...")
    try:
        with open(logscale_config_path, 'r') as file:
            config_content = file.readlines()

        token = input("Enter the new token value: ").strip()
        config_content = [
            re.sub(r'(token:\s*)(.*)', rf'\1{token}', line) if 'token:' in line else line 
            for line in config_content
        ]

        with open(logscale_config_path, 'w') as file:
            file.writelines(config_content)
        
        print("Token field value updated successfully.")
    except FileNotFoundError:
        print("LogScale configuration file not found.")
    except Exception as e:
        print(f"Error editing token field value: {e}")

# Edit URL field value
def edit_url_field_value():
    logscale_config_path = "/etc/humio-log-collector/config.yaml"
    print(f"Editing URL field value in {logscale_config_path}...")
    try:
        with open(logscale_config_path, 'r') as file:
            config_content = file.readlines()

        url = input("Enter the new URL value: ").strip()
        config_content = [
            re.sub(r'(url:\s*)(.*)', rf'\1{url}', line) if 'url:' in line else line 
            for line in config_content
        ]

        with open(logscale_config_path, 'w') as file:
            file.writelines(config_content)
        
        print("URL field value updated successfully.")
    except FileNotFoundError:
        print("LogScale configuration file not found.")
    except Exception as e:
        print(f"Error editing URL field value: {e}")

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
║  1. Install Falcon Log Collector                            ║
║  2. Set file access permissions                             ║
║  3. Set Falcon Log Collector default configuration          ║
║  4. View Falcon Log Collector configuration                 ║
║  5. Edit token field value                                  ║
║  6. Edit URL field value                                    ║
║  7. Enable Falcon Log Collector service                     ║
║  8. Check Falcon Log Collector service status               ║
║  9. Start Falcon Log Collector service                      ║
║  10. Stop Falcon Log Collector service                      ║
║  0. Back to main menu                                       ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            install_logscale_collector()
        elif choice == '2':
            set_file_access_permissions()
        elif choice == '3':
            set_logscale_config()
        elif choice == '4':
            view_logscale_config()
        elif choice == '5':
            edit_token_field_value()
        elif choice == '6':
            edit_url_field_value()
        elif choice == '7':
            enable_logscale_service()
        elif choice == '8':
            check_logscale_service_status()
        elif choice == '9':
            start_logscale_service()
        elif choice == '10':
            stop_logscale_service()
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
║  3. LogScale Configuration and Controls                     ║
║  4. Set log level                                           ║
║  0. Exit                                                    ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            zscaler_menu()
        elif choice == '2':
            syslog_menu()
        elif choice == '3':
            logscale_menu()
        elif choice == '4':
            set_log_level()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()
