import os
import json
import subprocess
from generate_logs import generate_regular_log, generate_bad_traffic_log, display_sample_log_and_curl
from generate_syslog_logs import generate_sample_syslogs_main as generate_syslog_logs, write_syslog_to_file

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

# Check required configuration values
def check_required_fields(config):
    required_fields = ['zscaler_api_url', 'zscaler_api_key', 'observer.id', 'encounter.alias']
    missing_fields = [field for field in required_fields if field not in config or not config[field]]
    if missing_fields:
        print(f"Missing required configuration fields: {', '.join(missing_fields)}")
        return False
    return True

# Show current configuration
def show_config():
    config = load_config()
    config_str = json.dumps(config, indent=4)
    pager(config_str)

# Add configuration value
def add_config_value(field, example):
    config = load_config()
    if field in config and config[field]:
        print(f"The '{field}' field already has a value: {config[field]}. Only one value per field is allowed.")
        return
    print(f"You are updating the '{field}' field. Example: {example}")
    new_value = input(f"Enter a value for {field}: ").strip()
    if new_value:
        config[field] = new_value
        save_config(config)
        print(f"Configuration updated: {field} set to {config[field]}")
    else:
        print("No value entered. Returning to the main menu.")

# Clear configuration value
def clear_config_value():
    config = load_config()
    print("Select a field to clear values from:")
    fields = ['zscaler_api_url', 'zscaler_api_key', 'observer.id', 'encounter.alias']
    for i, field in enumerate(fields, 1):
        print(f"{i}. {field}")
    choice = input("Select a field: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(fields):
        field = fields[int(choice) - 1]
        config[field] = ""
        save_config(config)
        print(f"Configuration cleared for field: {field}")
    else:
        print("Invalid field choice.")

# View cron job
def view_cron_job():
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    if result.returncode == 0:
        pager("Current cron jobs:\n" + result.stdout)
    else:
        print("No cron jobs set.")

# Set cron job
def set_cron_job(script_name, interval):
    job = f"*/{interval} * * * * for i in {{1..200}}; do python3 /home/ubuntu/NGSIEM-Log-Generator/{script_name} > /dev/null 2>&1; sleep 1; done"
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    cron_jobs = result.stdout if result.returncode == 0 else ""
    if job not in cron_jobs:
        cron_jobs += f"{job}\n"
        with open('mycron', 'w') as f:
            f.write(cron_jobs)
        subprocess.run(['crontab', 'mycron'])
        os.remove('mycron')
        print(f"Cron job set to run {script_name} every {interval} minutes.")
    else:
        print("Cron job already set.")

# Delete cron job
def delete_cron_job(script_name, interval):
    job = f"*/{interval} * * * * for i in {{1..200}}; do python3 /home/ubuntu/NGSIEM-Log-Generator/{script_name} > /dev/null 2>&1; sleep 1; done"
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    cron_jobs = result.stdout if result.returncode == 0 else ""
    if job in cron_jobs:
        cron_jobs = cron_jobs.replace(f"{job}\n", "")
        with open('mycron', 'w') as f:
            f.write(cron_jobs)
        subprocess.run(['crontab', 'mycron'])
        os.remove('mycron')
        print(f"Cron job deleted for {script_name}.")
    else:
        print("No matching cron job found.")

# Get last execution time
def get_last_execution_time(log_file):
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            lines = file.readlines()
        if lines:
            return lines[-1].strip()
    return "No execution log found."

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

# Set log level
def set_log_level():
    config = load_config()
    print("Select log level to set:")
    log_levels = ["info", "warning", "error"]
    for i, level in enumerate(log_levels, 1):
        print(f"{i}. {level}")
    choice = input("Select a log level: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(log_levels):
        config['log_level'] = log_levels[int(choice) - 1]
        save_config(config)
        print(f"Log level set to: {config['log_level']}")
    else:
        print("Invalid choice.")

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
║  3. Edit LogScale Configuration                             ║
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
            edit_logscale_config()
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
            if check_required_fields(config):
                api_url = config.get('zscaler_api_url')
                api_key = config.get('zscaler_api_key')
                sample_logs = [generate_regular_log(config), generate_bad_traffic_log(config)]
                send_logs(api_url, api_key, sample_logs)
            else:
                input("\nPress Enter to return to the main menu...")
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
║  3. Generate batch of Syslog logs to log folder             ║
║  4. Set cron job for Syslogs                                ║
║  5. Delete cron job for Syslogs                             ║
║  6. View last execution time of Syslog cron job             ║
║  7. Start LogScale log collector                            ║
║  8. Stop LogScale log collector                             ║
║  9. Status of LogScale log collector                        ║
║  0. Back to main menu                                       ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            sample_logs = generate_syslog_logs()
            if sample_logs:
                sample_log_str = json.dumps(sample_logs[0], indent=4)
                pager(f"Sample log:\n{sample_log_str}")
            else:
                print("No sample logs generated.")
        elif choice == '3':
            write_syslog_to_file(generate_syslog_logs())
            print("Batch of syslog logs generated and saved to log folder.")
        elif choice == '4':
            set_cron_job('generate_syslog_logs.py', 15)
        elif choice == '5':
            delete_cron_job('generate_syslog_logs.py', 15)
        elif choice == '6':
            last_execution = get_last_execution_time(SYSLOG_EXECUTION_FILE)
            print(f"Last execution time of Syslog cron job: {last_execution}")
        elif choice == '7':
            start_logshipper()
        elif choice == '8':
            stop_logshipper()
        elif choice == '9':
            status_logshipper()
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

if __name__ == "__main__":
    main_menu()
