import os
import json
import subprocess
from generate_logs import load_config, save_config, generate_sample_logs, send_logs

CONFIG_FILE = '/home/ec2-user/NGSIEM-Log-Generator/config.json'

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
def add_config_value(field, example):
    config = load_config()
    values = []
    print(f"You are updating the '{field}' field. Example: {example}")
    print("Press [Enter] without typing anything to stop adding values and return to the main menu.")
    while True:
        new_value = input(f"Enter a value for {field} (or press [Enter] to finish): ").strip()
        if not new_value:
            break
        values.append(new_value)
    if values:
        if isinstance(config.get(field), list):
            config[field].extend(values)
        else:
            config[field] = values if len(values) > 1 else values[0]
        save_config(config)
        print(f"Configuration updated: {field} set to {config[field]}")

# Clear configuration value
def clear_config_value():
    config = load_config()
    print("Select a field to clear values from:")
    fields = list(config.keys())
    for i, field in enumerate(fields, 1):
        print(f"{i}. {field}")
    choice = input("Select a field: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(fields):
        field = fields[int(choice) - 1]
        config[field] = [] if isinstance(config[field], list) else ""
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

# Set cron job for Zscaler logs
def set_cron_job_zscaler():
    job = "*/2 * * * * for i in {1..15}; do python3 /home/ec2-user/NGSIEM-Log-Generator/generate_logs.py > /dev/null 2>&1; sleep 8; done"
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    cron_jobs = result.stdout if result.returncode == 0 else ""
    if job not in cron_jobs:
        cron_jobs += f"{job}\n"
        with open('mycron', 'w') as f:
            f.write(cron_jobs)
        subprocess.run(['crontab', 'mycron'])
        os.remove('mycron')
        print("Cron job set to send Zscaler logs every 2 minutes.")
    else:
        print("Cron job already set.")

# Delete cron job for Zscaler logs
def delete_cron_job_zscaler():
    job = "*/2 * * * * for i in {1..15}; do python3 /home/ec2-user/NGSIEM-Log-Generator/generate_logs.py > /dev/null 2>&1; sleep 8; done"
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    cron_jobs = result.stdout if result.returncode == 0 else ""
    if job in cron_jobs:
        cron_jobs = cron_jobs.replace(f"{job}\n", "")
        with open('mycron', 'w') as f:
            f.write(cron_jobs)
        subprocess.run(['crontab', 'mycron'])
        os.remove('mycron')
        print("Cron job for Zscaler logs deleted.")
    else:
        print("No matching cron job found.")

# Set cron job for Syslog
def set_cron_job_syslog():
    job = "*/2 * * * * for i in {1..15}; do python3 /home/ec2-user/NGSIEM-Log-Generator/generate_syslogs.py > /dev/null 2>&1; sleep 8; done"
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    cron_jobs = result.stdout if result.returncode == 0 else ""
    if job not in cron_jobs:
        cron_jobs += f"{job}\n"
        with open('mycron', 'w') as f:
            f.write(cron_jobs)
        subprocess.run(['crontab', 'mycron'])
        os.remove('mycron')
        print("Cron job set to send Syslogs every 2 minutes.")
    else:
        print("Cron job already set.")

# Delete cron job for Syslog
def delete_cron_job_syslog():
    job = "*/2 * * * * for i in {1..15}; do python3 /home/ec2-user/NGSIEM-Log-Generator/generate_syslogs.py > /dev/null 2>&1; sleep 8; done"
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    cron_jobs = result.stdout if result.returncode == 0 else ""
    if job in cron_jobs:
        cron_jobs = cron_jobs.replace(f"{job}\n", "")
        with open('mycron', 'w') as f:
            f.write(cron_jobs)
        subprocess.run(['crontab', 'mycron'])
        os.remove('mycron')
        print("Cron job for Syslogs deleted.")
    else:
        print("No matching cron job found.")

# Start LogScale log collector
def start_logshipper():
    result = subprocess.run(['start-logshipper'], capture_output=True, text=True)
    if result.returncode == 0:
        print("LogScale log collector started successfully.")
    else:
        print(f"Failed to start LogScale log collector: {result.stderr}")

# Stop LogScale log collector
def stop_logshipper():
    result = subprocess.run(['stop-logshipper'], capture_output=True, text=True)
    if result.returncode == 0:
        print("LogScale log collector stopped successfully.")
    else:
        print(f"Failed to stop LogScale log collector: {result.stderr}")

# Status of LogScale log collector
def status_logshipper():
    result = subprocess.run(['status-logshipper'], capture_output=True, text=True)
    if result.returncode == 0:
        print("LogScale log collector status:\n" + result.stdout)
    else:
        print(f"Failed to get LogScale log collector status: {result.stderr}")

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
║  1. Show current configuration                              ║
║  2. Add a configuration value                               ║
║  3. Clear a configuration value                             ║
║  4. Generate sample logs                                    ║
║  5. Generate sample syslogs                                 ║
║  6. Send logs to NGSIEM                                     ║
║  7. View cron job                                           ║
║  8. Set cron job for Zscaler logs                           ║
║  9. Delete cron job for Zscaler logs                        ║
║ 10. Set cron job for Syslogs                                ║
║ 11. Delete cron job for Syslogs                             ║
║ 12. Start LogScale log collector                            ║
║ 13. Stop LogScale log collector                             ║
║ 14. Status of LogScale log collector                        ║
║  0. Exit                                                    ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            print("""
            Select a field to add values to:
            1. api_url (e.g., https://your-ngsiem-api-url)
            2. api_key (e.g., your_api_key)
            3. usernames (e.g., alice, bob)
            4. mac_addresses (e.g., 00:1A:2B:3C:4D:5E)
            5. user_agents (e.g., Mozilla/5.0)
            6. server_ips (e.g., 192.168.1.1)
            7. client_ips (e.g., 192.168.1.2)
            8. hostnames (e.g., server1.example.com)
            """)
            field_map = {
                '1': ('api_url', 'https://your-ngsiem-api-url'),
                '2': ('api_key', 'your_api_key'),
                '3': ('usernames', 'alice'),
                '4': ('mac_addresses', '00:1A:2B:3C:4D:5E'),
                '5': ('user_agents', 'Mozilla/5.0'),
                '6': ('server_ips', '192.168.1.1'),
                '7': ('client_ips', '192.168.1.2'),
                '8': ('hostnames', 'server1.example.com')
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
            sample_logs, curl_command = generate_sample_logs()
            sample_log_str = json.dumps(sample_logs[0], indent=4)
            pager(f"Sample log:\n{sample_log_str}\n\nCurl command:\n{curl_command}")
        elif choice == '5':
            # Implement generate_sample_syslogs here
            pass
        elif choice == '6':
            send_logs()
        elif choice == '7':
            view_cron_job()
        elif choice == '8':
            set_cron_job_zscaler()
        elif choice == '9':
            delete_cron_job_zscaler()
        elif choice == '10':
            set_cron_job_syslog()
        elif choice == '11':
            delete_cron_job_syslog()
        elif choice == '12':
            start_logshipper()
        elif choice == '13':
            stop_logshipper()
        elif choice == '14':
            status_logshipper()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()
