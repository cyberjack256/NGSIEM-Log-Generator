import os
import json
from generate_logs import load_config, save_config, generate_sample_logs

CONFIG_FILE = 'config.json'

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
    print(json.dumps(config, indent=4))

def add_config_value(field, example):
    config = load_config()
    print(f"\nYou are updating the '{field}' field. Example: {example}")
    print("Press [Enter] without typing anything to stop adding values and return to the main menu.\n")

    if field not in config:
        config[field] = []

    while True:
        new_value = input(f"Enter a value for {field} (or press [Enter] to finish): ").strip()
        if not new_value:
            break
        if new_value in config[field]:
            print(f"'{new_value}' is already in the '{field}' list. Try another value.")
        else:
            config[field].append(new_value)
            print(f"'{new_value}' added to the '{field}' list.")

    save_config(config)
    print(f"\nConfiguration updated: {field} set to {config[field]}")
    input("\nPress Enter to return to the main menu...")

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
            input("\nPress Enter to return to the main menu...")
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
                print("Invalid field choice. Press Enter to return to the main menu.")
                input()
        elif choice == '3':
            generate_sample_logs()
            input("\nPress Enter to return to the main menu...")
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()