import os
import json
import subprocess
from generate_logs import load_config, save_config, generate_sample_logs, send_logs

CONFIG_FILE = 'config.json'

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

# Set cron job
def set_cron_job():
    job = "*/2 * * * * for i in {1..15}; do python3 /path/to/your/send_logs.py > /dev/null 2>&1; sleep 8; done"
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    cron_jobs = result.stdout if result.returncode == 0 else ""
    if job not in cron_jobs:
        cron_jobs += f"{job}\n"
        with open('mycron', 'w') as f:
            f.write(cron_jobs)
        subprocess.run(['crontab', 'mycron'])
        os.remove('mycron')
        print("Cron job set to send logs every 2 minutes.")
    else:
        print("Cron job already set.")

# Delete cron job
def delete_cron_job():
    job = "*/2 * * * * for i in {1..15}; do python3 /path/to/your/send_logs.py > /dev/null 2>&1; sleep 8; done"
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    cron_jobs = result.stdout if result.returncode == 0 else ""
    if job in cron_jobs:
        cron_jobs = cron_jobs.replace(f"{job}\n", "")
        with open('mycron', 'w') as f:
            f.write(cron_jobs)
        subprocess.run(['crontab', 'mycron'])
        os.remove('mycron')
        print("Cron job deleted.")
    else:
        print("No matching cron job found.")

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
║                     Zscaler Log Generator                   ║
║═════════════════════════════════════════════════════════════║
║  Welcome to the Zscaler Log Generator Menu                  ║
║  Please select an option:                                   ║
║                                                             ║
║  1. Show current configuration                              ║
║  2. Add a configuration value                               ║
║  3. Clear a configuration value                             ║
║  4. Generate sample logs                                    ║
║  5. Send logs to NGSIEM                                     ║
║  6. View cron job                                           ║
║  7. Set cron job                                            ║
║  8. Delete cron job                                         ║
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
            sample_logs = generate_sample_logs()
            pager("Sample logs generated:\n" + "\n".join(json.dumps(log, indent=4) for log in sample_logs))
        elif choice == '5':
            send_logs()
        elif choice == '6':
            view_cron_job()
        elif choice == '7':
            set_cron_job()
        elif choice == '8':
            delete_cron_job()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()