import os
import json
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO)

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
    if not config:
        print("\nNo configuration found.")
    else:
        print("\nCurrent configuration:")
        for key, value in config.items():
            print(f"{key}: {value}")

# Set configuration field
def set_config_field(field):
    config = load_config()
    new_value = input(f"Enter the value for {field}: ").strip()
    config[field] = new_value
    save_config(config)
    print(f"Configuration updated: {field} set to {config[field]}")

# Generate sample logs
def generate_sample_logs():
    print("\nGenerating sample logs...")
    subprocess.run(['python3', 'generate_logs.py'], check=True)

# Send logs to NGSIEM API
def send_logs_to_ngsiem():
    config = load_config()
    if 'api_url' not in config:
        print("\nAPI URL is not set in the configuration.")
        return
    api_url = config['api_url']
    headers = {"Content-Type": "application/json"}
    with open('sample_log.json', 'r') as log_file:
        logs = json.load(log_file)
    response = requests.post(api_url, json=logs, headers=headers)
    print(f"\nResponse from NGSIEM API: {response.status_code}")

# Main menu
def main_menu():
    while True:
        os.system('clear')
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                Log Generator Menu                          ║
║════════════════════════════════════════════════════════════════════════════║
║ Please select an option:                                                   ║
║                                                                            ║
║  1. Show current configuration                                             ║
║  2. Set configuration field                                                ║
║  3. Generate sample logs                                                   ║
║  4. Send logs to NGSIEM API                                                ║
║  0. Exit                                                                   ║
╚════════════════════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            field = input("\nEnter the configuration field you want to set: ").strip()
            set_config_field(field)
        elif choice == '3':
            generate_sample_logs()
        elif choice == '4':
            send_logs_to_ngsiem()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()