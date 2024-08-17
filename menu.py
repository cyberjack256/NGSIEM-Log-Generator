import json
import logging
import os
import subprocess
from datetime import datetime
from generate_logs import display_sample_log_and_curl, generate_regular_log, generate_bad_traffic_log, send_logs
from generate_syslog_logs import generate_sample_syslogs, write_syslog_to_file

# Set up logging
logging.basicConfig(level=logging.INFO)

# Dynamically get the user home directory
CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/config.json')
ZS_LOG_EXECUTION_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/generate_logs_execution.log')
SYSLOG_EXECUTION_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/generate_syslog_logs_execution.log')

# Load configuration
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save configuration
def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

# Show current configuration
def show_config():
    config = load_config()
    config_str = json.dumps(config, indent=4)
    pager(config_str)

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
    subprocess.Popen(["python3", "/path/to/generate_syslog_logs.py"])
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

# Start LogScale log collector
def start_logshipper():
    subprocess.run(['sudo', 'systemctl', 'start', 'humio-log-collector.service'])
    print("LogScale log collector started.")

# Stop LogScale log collector
def stop_logshipper():
    subprocess.run(['sudo', 'systemctl', 'stop', 'humio-log-collector.service'])
    print("LogScale log collector stopped.")

# Status of LogScale log collector
def status_logshipper():
    result = subprocess.run(['sudo', 'systemctl', 'status', 'humio-log-collector.service'], capture_output=True, text=True)
    pager(result.stdout)

# Use less for scrolling output
def pager(content):
    pager_process = subprocess.Popen(['less'], stdin=subprocess.PIPE)
    pager_process.communicate(input=content.encode('utf-8'))

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
║  6. Set cron job for Zscaler logs                           ║
║  7. Delete cron job for Zscaler logs                        ║
║  8. View last execution time of Zscaler cron job            ║
║  0. Back to main menu                                       ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            print("""
            Select a field to add values to:
            1. api_url for Zscaler (e.g., https://your-ngsiem-api-url)
            2. api_key for Zscaler (e.g., your_api_key)
            3. observer.id (e.g., observer123)
            4. encounter.alias (e.g., encounterX)
            """)
            field_map = {
                '1': ('zscaler_api_url', 'https://your-ngsiem-api-url'),
                '2': ('zscaler_api_key', 'your_api_key'),
                '3': ('observer.id', 'observer123'),
                '4': ('encounter.alias', 'encounterX')
            }
            field_choice = input("Select a field: ").strip()
            if field_choice in field_map:
                field, example = field_map[field_choice]
                add_config_value(field, example)
            else:
                print("Invalid field choice.")
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
        elif choice == '6':
            set_cron_job('generate_logs.py', 2)
        elif choice == '7':
            delete_cron_job('generate_logs.py', 2)
        elif choice == '8':
            last_execution = get_last_execution_time(ZS_LOG_EXECUTION_FILE)
            print(f"Last execution time of Zscaler cron job: {last_execution}")
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
║  3. Start logging service                                   ║
║  4. Stop logging service                                    ║
║  5. Check logging service status                            ║
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
            start_logging_service()
        elif choice == '4':
            stop_logging_service()
        elif choice == '5':
            check_logging_service_status()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

# LogScale Configuration and Controls
def logscale_menu():
    while True:
        os.system('clear')
        print(f"""
╔═════════════════════════════════════════════════════════════╗
║               LogScale Configuration and Controls           ║
║═════════════════════════════════════════════════════════════║
║  Please select an option:                                   ║
║                                                             ║
║  1. Start LogScale log collector                            ║
║  2. Stop LogScale log collector                             ║
║  3. Check LogScale log collector status                     ║
║  4. Edit LogScale configuration file                        ║
║  0. Back to main menu                                       ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            start_logshipper()
        elif choice == '2':
            stop_logshipper()
        elif choice == '3':
            status_logshipper()
        elif choice == '4':
            edit_logscale_config()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

# Edit LogScale Configuration
def edit_logscale_config():
    logscale_config_path = "/etc/humio-logcollector/config.yaml"
    if os.path.exists(logscale_config_path):
        subprocess.run(['sudo', 'nano', logscale_config_path])
    else:
        print("LogScale configuration file not found.")

# Check required fields
def check_required_fields(config):
    required_fields = ['zscaler_api_url', 'zscaler_api_key', 'observer.id', 'encounter.alias']
    missing_fields = [field for field in required_fields if field not in config or not config[field]]
    if missing_fields:
        print(f"Missing required configuration fields: {', '.join(missing_fields)}")
        return False
    return True

if __name__ == "__main__":
    main_menu()
