import os
import subprocess
import json
from generate_syslog_logs import generate_sample_syslogs, generate_syslog_message, write_syslog_to_file

# Paths to config files
CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/config.json')

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
    subprocess.Popen(["python3", os.path.expanduser("~/NGSIEM-Log-Generator/generate_syslog_logs.py")])
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
            generate_logs('file')
            print("Generated logs to file.")
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

if __name__ == "__main__":
    main_menu()