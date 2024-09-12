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

# Add configuration value with validation to prevent special characters
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

        # Validate input to avoid adding special characters or empty values
        if re.match("^[a-zA-Z0-9._-]+$", value):
            if value:
                config[field] = value
                save_config(config)
                print(f"Configuration updated: {field} set to {config[field]}")
            else:
                print("No value entered. Configuration not updated.")
        else:
            print("Invalid input. Please avoid using special characters.")
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

# Show observer.id
def show_observer_id():
    config = load_config()
    filtered_config = {k: config[k] for k in ['observer.id'] if k in config}
    config_str = json.dumps(filtered_config, indent=4)
    pager(config_str + "\n\nPress 'q' to exit.")

# Add or update observer.id
def add_observer_id_value():
    config = load_config()
    value = input("Enter a value for observer.id: ").strip()

    # Ensure valid input and prevent special characters or empty values
    if re.match("^[a-zA-Z0-9._-]+$", value):
        if value:
            config['observer.id'] = value
            save_config(config)
            print(f"Configuration updated: observer.id set to {config['observer.id']}")
        else:
            print("No value entered. Configuration not updated.")
    else:
        print("Invalid input. Please avoid using special characters.")

# Syslog menu
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