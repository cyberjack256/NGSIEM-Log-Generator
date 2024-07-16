import json
import logging
import os
import random
import requests
from datetime import datetime, timedelta
import pytz
import yaml
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = 'config.yaml'
fake = Faker()

# Load configuration
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return yaml.safe_load(file)
    return {}

# Save configuration
def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        yaml.safe_dump(config, file)

# Show current configuration
def show_config():
    config = load_config()
    print(yaml.dump(config, sort_keys=False))

# Add configuration value
def add_config_value(field, example):
    config = load_config()
    while True:
        new_value = input(f"Enter a value for {field} (e.g., {example}) or press [Enter] to return to the menu: ").strip()
        if not new_value:
            break
        if field not in config:
            config[field] = []
        config[field].append(new_value)
    save_config(config)
    print(f"Configuration updated: {field} set to {config[field]}")

# Generate sample logs
def generate_sample_logs():
    config = load_config()
    if 'api_url' not in config:
        print("\nAPI URL is not set in the configuration.")
        return
    
    api_url = config['api_url']
    now = datetime.utcnow()
    
    log_entry = {
        "sourcetype": "zscalernss-web",
        "event": {
            "datetime": (now - timedelta(minutes=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S"),
            "reason": "allowed",
            "event_id": random.randint(100000, 999999),
            "protocol": "HTTPS",
            "action": "allowed",
            "transactionsize": random.randint(1000, 2000),
            "responsesize": random.randint(500, 1000),
            "requestsize": random.randint(100, 500),
            "urlcategory": fake.word(),
            "serverip": random.choice(config.get('server_ips', [fake.ipv4()])),
            "clienttranstime": random.randint(200, 500),
            "requestmethod": random.choice(["GET", "POST"]),
            "refererURL": fake.url(),
            "useragent": random.choice(config.get('user_agents', [fake.user_agent()])),
            "product": "NSS",
            "location": fake.city(),
            "ClientIP": random.choice(config.get('client_ips', [fake.ipv4()])),
            "status": random.choice(["200", "404", "500"]),
            "user": random.choice(config.get('usernames', [fake.user_name()])),
            "url": fake.url(),
            "vendor": "Zscaler",
            "hostname": random.choice(config.get('hostnames', [fake.hostname()])),
            "clientpublicIP": fake.ipv4(),
            "threatcategory": fake.word(),
            "threatname": fake.file_name(extension='exe'),
            "filetype": "exe",
            "appname": fake.word(),
            "pagerisk": random.randint(1, 100),
            "department": fake.word(),
            "urlsupercategory": fake.word(),
            "appclass": fake.word(),
            "dlpengine": fake.word(),
            "urlclass": fake.word(),
            "threatclass": fake.word(),
            "dlpdictionaries": fake.word(),
            "fileclass": fake.word(),
            "bwthrottle": "none",
            "servertranstime": random.randint(100, 300),
            "contenttype": "application/octet-stream",
            "unscannabletype": "none",
            "deviceowner": fake.name(),
            "devicehostname": fake.hostname(),
            "decrypted": random.choice(["yes", "no"])
        }
    }

    response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=log_entry)
    if response.status_code == 200:
        print("Log sent successfully.")
    else:
        print(f"Failed to send log: {response.status_code} {response.text}")

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
║  3. Generate sample logs                                    ║
║  0. Exit                                                    ║
╚═════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            field = input("Enter the field name you want to add values to (e.g., usernames): ").strip()
            example = "example_value"  # Replace with a relevant example based on your field
            add_config_value(field, example)
        elif choice == '3':
            generate_sample_logs()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()