import os
import re
import subprocess
import json
import glob
from generate_syslog_logs import (
    generate_sample_syslogs, 
    generate_syslog_message, 
    write_syslog_to_file, 
    start_send_to_syslog_service, 
    stop_send_to_syslog_service, 
    check_send_to_syslog_service_status,
    debug_logs_enabled
)
from generate_logs import (
    display_sample_log_and_curl, 
    generate_regular_log, 
    generate_suspicious_allowed_log, 
    generate_bad_traffic_log,
    start_logging_service,
    stop_logging_service,
    check_logging_service_status
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
    filtered_config = {k: config[k] for k in ['zscaler_api_url', 'zscaler_api_key', 'observer.id'] if k in config}
    config_str = json.dumps(filtered_config, indent=4)
    pager(config_str + "\n\nPress 'q' to exit.")

# Add configuration value with special character prevention
def add_config_value():
    config = load_config()
    editable_fields = ['zscaler_api_url', 'zscaler_api_key', 'observer.id', 'encounter.alias']
    print("Select a field to add or update values for:")
    for i, field in enumerate(editable_fields, 1):
        print(f"{i}. {field}")
    choice = input("Select a field: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(editable_fields):
        field = editable_fields[int(choice) - 1]
        # Remove special characters from user input
        value = re.sub(r'[^a-zA-Z0-9._-]', '', input(f"Enter a value for {field}: ").strip()) 
        if value:
            config[field] = value
            save_config(config)
            print(f"Configuration updated: {field} set to {config[field]}")
        else:
            print("No value entered. Configuration not updated.")
    else:
        print("Invalid field choice.")

# Syslog menu with observer.id options and existing functionality
def syslog_menu():
    global debug_logs_enabled
    
    while True:
        os.system('clear')
        print(f"""
╔═════════════════════════════════════════════════════════════╗
║                     Syslog Log Actions                      ║
║═════════════════════════════════════════════════════════════║
║  Please select an option:                                   ║
║                                                             ║
║  1. Show observer ID                                        ║
║  2. Add or update observer ID                               ║
║  3. Generate sample Syslog logs                             ║
║  4. Generate logs to file                                   ║
║  5. Start sending logs to syslog server                     ║
║  6. Stop sending logs to syslog server                      ║
║  7. Check send to syslog service status                     ║
║  8. Toggle debug logs (Currently: { 'Enabled' if debug_logs_enabled else 'Disabled' })          <--
║  9. Contact Sysadmin to disable debug logs                  ║
║  0. Back to main menu                                       ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_observer_id()  # Show only the observer.id
        elif choice == '2':
            add_observer_id_value()  # Add or update observer.id
        elif choice == '3':
            sample_logs = generate_sample_syslogs()
            if sample_logs:
                sample_log_str = json.dumps(sample_logs[0], indent=4)
                pager(f"Sample log:\n{sample_log_str}")
            else:
                print("No sample logs generated.")
        elif choice == '4':
            sample_logs = generate_sample_syslogs()
            write_syslog_to_file(sample_logs)
        elif choice == '5':
            start_send_to_syslog_service()  # Start sending logs to syslog server
        elif choice == '6':
            stop_send_to_syslog_service()  # Stop sending logs to syslog server
        elif choice == '7':
            check_send_to_syslog_service_status()  # Check the status of the syslog sending service
        elif choice == '8':
            debug_logs_enabled = not debug_logs_enabled  # Toggle the debug log flag
            print(f"Debug logs {'enabled' if debug_logs_enabled else 'disabled'}")
        elif choice == '9':
            debug_logs_enabled = False
            print("You have contacted the Sysadmin. Debug logs will stop being forwarded.")
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
        # Use sudo to read the file with elevated privileges
        result = subprocess.run(['sudo', 'cat', logscale_config_path], capture_output=True, text=True)
        if result.returncode == 0:
            pager(result.stdout)
        else:
            print(f"Error viewing LogScale configuration: {result.stderr}")
    except Exception as e:
        print(f"Error viewing LogScale configuration: {e}")

# Edit token field value
def edit_token_field_value():
    logscale_config_path = "/etc/humio-log-collector/config.yaml"
    print(f"Editing token field value in {logscale_config_path}...")
    try:
        # Use sudo to read the file with elevated privileges
        result = subprocess.run(['sudo', 'cat', logscale_config_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error reading LogScale configuration: {result.stderr}")
            return

        config_content = result.stdout

        token = input("Enter the new token value: ").strip()
        # Use re.escape to escape any special characters in the token
        updated_content = re.sub(r'(token:\s*).*', rf'token: {re.escape(token)}', config_content)

        # Use sudo to write the changes to the configuration file
        subprocess.run(['sudo', 'tee', logscale_config_path], input=updated_content.encode('utf-8'))
        
        print("Token field value updated successfully.")
    except Exception as e:
        print(f"Error editing token field value: {e}")

# Edit URL field value without escaping special characters
def edit_url_field_value():
    logscale_config_path = "/etc/humio-log-collector/config.yaml"
    print(f"Editing URL field value in {logscale_config_path}...")
    try:
        # Use sudo to read the file with elevated privileges
        result = subprocess.run(['sudo', 'cat', logscale_config_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error reading LogScale configuration: {result.stderr}")
            return

        config_content = result.stdout

        url = input("Enter the new URL value: ").strip()

        # Ensure the URL does not end with '/', '/services', or '/services/collector'
        if url.endswith('/') or url.endswith('/services') or url.endswith('/services/collector'):
            print("Invalid URL format. The URL should not end with '/', '/services', or '/services/collector'.")
            return

        # Update the URL without using re.escape to avoid adding backslashes
        updated_content = re.sub(r'(url:\s*).*', f'url: {url}', config_content)

        # Use sudo to write the changes to the configuration file
        subprocess.run(['sudo', 'tee', logscale_config_path], input=updated_content.encode('utf-8'))
        
        print("URL field value updated successfully.")
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

# LogScale Log Collector Menu
def logscale_menu():
    while True:
        os.system('clear')
        print(f"""
╔═════════════════════════════════════════════════════════════╗
║      LogScale Log Collector Configuration and Controls      ║
║═════════════════════════════════════════════════════════════║
║  Please select an option:                                   ║
║                                                             ║
║  1. Install Falcon LogScale LogCollector                    ║
║  2. Set file access permissions                             ║
║  3. Set LogCollector default configuration                  ║
║  4. View LogCollector configuration                         ║
║  5. Edit token field value                                  ║
║  6. Edit URL field value                                    ║
║  7. Enable LogCollector service                             ║
║  8. Check LogCollector service status                       ║
║  9. Start LogCollector service                              ║
║  10. Stop LogCollector service                              ║
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
║                Next-Gen SIEM Log Generator                  ║
║═════════════════════════════════════════════════════════════║
║  Welcome to the Next-Gen SIEM Log Generator Menu            ║
║  Please select an option:                                   ║
║                                                             ║
║  1. Zscaler log actions                                     ║
║  2. Syslog log actions                                      ║
║  3. Falcon LogScale LogCollector Configuration and Controls ║
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
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()