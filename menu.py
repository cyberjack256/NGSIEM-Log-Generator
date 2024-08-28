import os
import subprocess
import json
from generate_syslog_logs import generate_sample_syslogs, generate_syslog_message, write_syslog_to_file
from generate_logs import (
    display_sample_log_and_curl, 
    generate_regular_log, 
    generate_suspicious_allowed_log, 
    generate_bad_traffic_log,
    run_as_service,  # New function for running as a service
    stop_service     # New function to stop the service
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
║  3. Generate sample Zscaler logs                            ║
║  4. Start generating logs as a service                      ║
║  5. Stop log generation service                             ║
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
            run_as_service()  # New function to start generating logs as a service
        elif choice == '5':
            stop_service()    # New function to stop the service
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