import os
import subprocess
import json
from generate_syslog_logs import generate_sample_syslogs, generate_syslog_message, write_syslog_to_file
from generate_logs import display_sample_log_and_curl, generate_regular_log, generate_bad_traffic_log, send_logs

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
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}

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

# Save configuration
def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

# Clear configuration value
def clear_config_value():
    config = load_config()
    editable_fields = ['zscaler_api_url', 'zscaler_api_key', 'observer.id', 'encounter.alias']
    print("Select a field to clear values from:")
    for i, field in enumerate(editable_fields, 1):
        print(f"{i}. {field}")
    choice = input("Select a field: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(editable_fields):
        field = editable_fields[int(choice) - 1]
        config[field] = ""
        save_config(config)
        print(f"Configuration cleared for field: {field}")
    else:
        print("Invalid field choice.")

# Start logging service
def start_logging_service():
    subprocess.Popen(["python3", os.path.join(LOG_GENERATOR_DIR, "generate_syslog_logs.py")])
    print("Logging service started.")

# Stop logging service
def stop_logging_service():
    subprocess.run(["pkill", "-f", "generate_syslog_logs.py"])
    print("Logging service stopped.")

# Check logging service status
def check_logging_service_status():
    result = subprocess.run(["pgrep", "-fl", "generate_syslog_logs.py"], capture_output=True, text=True)
    if result.stdout:
        print("Logging service is running.")
    else:
        print("Logging service is not running.")

# Use less for scrolling output
def pager(content):
    pager_process = subprocess.Popen(['less'], stdin=subprocess.PIPE)
    pager_process.communicate(input=content.encode('utf-8'))

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
║  3. Clear a configuration value                             ║
║  4. Generate sample Zscaler logs                            ║
║  5. Send logs to NGSIEM                                     ║
║  0. Back to main menu                                       ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            add_config_value()
        elif choice == '3':
            clear_config_value()
        elif choice == '4':
            display_sample_log_and_curl()
        elif choice == '5':
            config = load_config()
            api_url = config.get('zscaler_api_url')
            api_key = config.get('zscaler_api_key')
            if api_url and api_key and check_required_fields(config):
                sample_logs = [generate_regular_log(config), generate_bad_traffic_log(config)]
                send_logs(api_url, api_key, sample_logs)
            else:
                print("API URL or API Key is missing from configuration.")
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

# LogScale menu
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

# Install LogScale log collector
def install_logscale_collector():
    print("Installing LogScale log collector...")
    os.chdir(LOG_COLLECTOR_DIR)  # Change to the directory containing the collector package
    subprocess.run(["mv", "humio-log-collector*", "humio-log-collector.deb"])
    subprocess.run(["sudo", "dpkg", "-i", "humio-log-collector.deb"])
    subprocess.run(["sudo", "chown", "-R", "humio-log-collector:humio-log-collector", "/var/lib/humio-log-collector"])
    print("LogScale log collector installed.")

# Edit LogScale Configuration
def edit_logscale_config():
    logscale_config_path = "/etc/humio-log-collector/config.yaml"
    
    # Use sudo to check if the file exists, since ubuntu user can't see the file
    check_file_exists_command = f"sudo test -f {logscale_config_path}"
    check_file_exists = subprocess.run(check_file_exists_command, shell=True)
    
    if check_file_exists.returncode == 0:
        try:
            print("Opening LogScale configuration for editing...")
            # Use sudo to run nano with elevated privileges
            subprocess.run(['sudo', 'nano', logscale_config_path])
        except subprocess.CalledProcessError as e:
            print(f"Failed to open the configuration file: {e}")
    else:
        print("LogScale configuration file not found or you don't have the necessary permissions.")
      
# Set LogScale configuration
def set_logscale_config():
    logscale_config_path = "/etc/humio-log-collector/config.yaml"
    confirmation = input("If this is your first time setting the configuration, proceed. If not, note that this will overwrite the existing config. Proceed? (yes/no): ").strip().lower()
    if confirmation == "yes":
        try:
            temp_config_path = os.path.join(LOG_GENERATOR_DIR, "temp_config.yaml")
            with open(temp_config_path, 'w') as temp_file:
                temp_file.write(BASE_LOGSCALE_CONFIG)
            subprocess.run(['sudo', 'cp', temp_config_path, logscale_config_path])
            os.remove(temp_config_path)  # Clean up temp file
            print("LogScale configuration has been set.")
        except Exception as e:
            print(f"Failed to set configuration: {e}")
    else:
        print("Operation canceled.")

# Set file access permissions
def set_file_access_permissions():
    print("Setting file access permissions...")
    subprocess.run(['sudo', 'setcap', 'cap_dac_read_search,cap_net_bind_service+ep', '/usr/bin/humio-log-collector'])
    subprocess.run(['sudo', 'systemctl', 'restart', 'humio-log-collector'])
    print("File access permissions set.")

# Enable LogScale service
def enable_logscale_service():
    print("Enabling LogScale service...")
    subprocess.run(['sudo', 'systemctl', 'enable', '--now', 'humio-log-collector.service'])
    print("LogScale service enabled.")

# Start LogScale service
def start_logscale_service():
    print("Starting LogScale service...")
    subprocess.run(['sudo', 'systemctl', 'start', 'humio-log-collector.service'])
    print("LogScale service started.")

# Stop LogScale service
def stop_logscale_service():
    print("Stopping LogScale service...")
    subprocess.run(['sudo', 'systemctl', 'stop', 'humio-log-collector.service'])
    print("LogScale service stopped.")

# Check LogScale service status
def check_logscale_service_status():
    print("Checking LogScale service status...")
    result = subprocess.run(['sudo', 'systemctl', 'status', 'humio-log-collector.service'], capture_output=True, text=True)
    pager(result.stdout)

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