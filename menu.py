import json
import os
import logging
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = 'config.json'

REQUIRED_FIELDS = ['api_url', 'usernames', 'mac_addresses', 'ip_addresses', 'user_agents']

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
    print("\nCurrent configuration:")
    for field in REQUIRED_FIELDS:
        value = config.get(field, 'Not set')
        print(f"{field}: {value}")

# Set configuration field
def set_config_field(field):
    config = load_config()
    new_value = input(f"Enter the value for {field}: ").strip()
    config[field] = new_value
    save_config(config)
    print(f"Configuration updated: {field} set to {config[field]}")

# Validate configuration
def validate_config():
    config = load_config()
    missing_fields = [field for field in REQUIRED_FIELDS if field not in config or config[field] == '']
    if missing_fields:
        print(f"\nMissing required fields: {', '.join(missing_fields)}")
        return False
    return True

# Generate sample logs
def generate_sample_logs():
    if not validate_config():
        print("\nPlease set the missing configuration fields using option 2.")
        return
    # Generate logs based on the config
    config = load_config()
    logs = [
        {
            "sourcetype": "zscalernss-web",
            "event": {
                "datetime": "2024-07-16 10:20:30",
                "reason": "allowed",
                "event_id": 123456789,
                "protocol": "HTTPS",
                "action": "allowed",
                "transactionsize": 512,
                "responsesize": 256,
                "requestsize": 128,
                "urlcategory": "business",
                "serverip": "192.168.1.100",
                "clienttranstime": 123,
                "requestmethod": "GET",
                "refererURL": "https://example.com",
                "useragent": config['user_agents'][0],
                "product": "NSS",
                "location": "Office",
                "ClientIP": config['ip_addresses'][0],
                "status": "200",
                "user": config['usernames'][0],
                "url": "https://malicious-site.com",
                "vendor": "Zscaler",
                "hostname": "malicious-site.com",
                "clientpublicIP": config['ip_addresses'][0],
                "threatcategory": "malware",
                "threatname": "MaliciousFile.exe",
                "filetype": "exe",
                "appname": "MalwareApp",
                "pagerisk": 100,
                "department": "IT",
                "urlsupercategory": "malicious",
                "appclass": "unknown",
                "dlpengine": "engine1",
                "urlclass": "malicious",
                "threatclass": "malware",
                "dlpdictionaries": "dict1",
                "fileclass": "malware",
                "bwthrottle": "none",
                "servertranstime": 200,
                "contenttype": "application/octet-stream",
                "unscannabletype": "none",
                "deviceowner": "admin",
                "devicehostname": "host1",
                "decrypted": "no"
            }
        }
    ]
    print("\nGenerated logs:")
    for log in logs:
        print(json.dumps(log, indent=4))

    # Example command to send logs to NGSIEM
    api_url = config['api_url']
    for log in logs:
        command = f'curl -X POST {api_url} -H "Content-Type: application/json" -d \'{json.dumps(log)}\''
        print(f"\nSending log with command: {command}")
        subprocess.run(command, shell=True)

# Main menu
def main_menu():
    while True:
        os.system('clear')
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                           Zscaler Log Generator                            ║
║════════════════════════════════════════════════════════════════════════════║
║ Please select an option:                                                   ║
║  1. Show current configuration                                             ║
║  2. Set a configuration field                                              ║
║  3. Generate sample logs                                                   ║
║  0. Exit                                                                   ║
╚════════════════════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            for i, field in enumerate(REQUIRED_FIELDS, 1):
                print(f"{i}. {field}")
            field_choice = input("\nEnter the number of the field you want to set: ").strip()
            if field_choice.isdigit() and 1 <= int(field_choice) <= len(REQUIRED_FIELDS):
                field = REQUIRED_FIELDS[int(field_choice) - 1]
                set_config_field(field)
            else:
                print("Invalid choice. Please enter a number from the list.")
        elif choice == '3':
            generate_sample_logs()
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()