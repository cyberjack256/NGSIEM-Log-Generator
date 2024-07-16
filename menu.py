import json
import os
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = 'config.json'

REQUIRED_FIELDS = {
    'zscaler': ['api_url', 'api_key', 'usernames', 'ips', 'mac_addresses', 'user_agents']
}

# Field examples
FIELD_EXAMPLES = {
    'api_url': 'e.g., https://api.yourservice.com/v1/ingest/logs',
    'api_key': 'e.g., your_api_key_here',
    'usernames': 'e.g., hawk, eagle, falcon',
    'ips': 'e.g., 192.168.1.1, 192.168.1.2',
    'mac_addresses': 'e.g., 00:14:22:01:23:45, 00:14:22:01:23:46',
    'user_agents': 'e.g., Mozilla/5.0, Chrome/91.0'
}

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
    print(f"\nCurrent configuration:")
    for field in REQUIRED_FIELDS['zscaler']:
        value = config.get(field, 'Not set')
        print(f"{field}: {value}")

# Set configuration field
def set_config_field(field):
    config = load_config()
    example = FIELD_EXAMPLES.get(field, '')
    new_value = input(f"Enter the value for {field} ({example}):\n").strip()
    config[field] = new_value
    save_config(config)
    print(f"Configuration updated: {field} set to {config[field]}")

# Validate configuration
def validate_config():
    config = load_config()
    missing_fields = [field for field in REQUIRED_FIELDS['zscaler'] if field not in config or config[field] == '' or config[field] == 'REPLACEME']
    if missing_fields:
        print(f"\nMissing required fields: {', '.join(missing_fields)}")
        return False
    return True

# Run script
def run_script(script_name):
    if not validate_config():
        print("\nPlease set the missing configuration fields.")
        return
    result = subprocess.run(['python3', script_name], capture_output=True, text=True)
    with open('script_output.txt', 'w') as f:
        f.write(result.stdout)
        f.write(result.stderr)
    subprocess.run(['less', 'script_output.txt'])

# Main menu
def main_menu():
    while True:
        os.system('clear')
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                              Zscaler Log Generator                         ║
║════════════════════════════════════════════════════════════════════════════║
║ Welcome to the Zscaler Log Generator Menu                                  ║
║ Please select an option:                                                   ║
║                                                                            ║
║  1. Show current configuration                                             ║
║  2. Set a configuration field                                              ║
║  3. Generate sample logs                                                   ║
║  4. Exit                                                                   ║
╚════════════════════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            sorted_fields = sorted(FIELD_EXAMPLES.keys())
            for i, field in enumerate(sorted_fields, 1):
                print(f"{i}. {field}")
            field_choice = input("\nEnter the number of the field you want to set: ").strip()
            if field_choice.isdigit() and 1 <= int(field_choice) <= len(sorted_fields):
                field = sorted_fields[int(field_choice) - 1]
                set_config_field(field)
            else:
                print("Invalid choice. Please enter a number from the list.")
        elif choice == '3':
            run_script('generate_logs.py')
        elif choice == '4' or choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()