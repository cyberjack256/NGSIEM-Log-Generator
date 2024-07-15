import json
import os
import subprocess

CONFIG_FILE = 'config.json'
LOGSCALE_URL = 'https://your-logscale-instance.com/api/v1/ingest/logs'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

def show_config():
    config = load_config()
    print("\nCurrent configuration:")
    for key, value in config.items():
        print(f"{key}: {value}")

def set_config_field(field):
    config = load_config()
    new_value = input(f"Enter the value for {field}: ").strip()
    config[field] = new_value
    save_config(config)
    print(f"Configuration updated: {field} set to {config[field]}")

def validate_config():
    config = load_config()
    required_fields = ["logscale_api_token", "logscale_url"]
    missing_fields = [field for field in required_fields if field not in config or config[field] == ""]
    if missing_fields:
        print(f"\nMissing required fields: {', '.join(missing_fields)}")
        return False
    return True

def run_script(script_name):
    if not validate_config():
        print("\nPlease set the missing configuration fields using the menu.")
        return
    result = subprocess.run(['python3', script_name], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

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
║  3. Run the log generation script                                          ║
║  0. Exit                                                                   ║
╚════════════════════════════════════════════════════════════════════════════╝
        """)
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            show_config()
        elif choice == '2':
            field = input("Enter the name of the field to set: ").strip()
            set_config_field(field)
        elif choice == '3':
            run_script('generate_logs.py')
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()