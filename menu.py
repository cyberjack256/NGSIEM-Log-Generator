import os
import json
from generate_logs import load_config, save_config, create_sample_log_entry

CONFIG_FILE = 'config.json'

def show_config():
    config = load_config()
    print(json.dumps(config, indent=4))

def clear_config_value(field):
    config = load_config()
    if field in config:
        config[field] = [] if isinstance(config[field], list) else ""
        save_config(config)
        print(f"Configuration cleared: {field} is now {config[field]}")
    else:
        print(f"Field '{field}' not found in configuration.")
    input("\nPress Enter to return to the main menu...")

def add_config_value(field, example):
    config = load_config()
    print(f"\nYou are updating the '{field}' field. Example: {example}")
    print("Enter a comma-separated list of values, or press [Enter] without typing anything to return to the main menu.\n")

    while True:
        new_value = input(f"Enter values for {field} (or press [Enter] to finish): ").strip()
        if not new_value:
            break
        if ',' in new_value:
            values = [val.strip() for val in new_value.split(',')]
        else:
            values = [new_value]
        
        if isinstance(config[field], list):
            config[field].extend(values)
            config[field] = list(set(config[field]))  # Remove duplicates
        else:
            config[field] = values[0]

        save_config(config)
        print(f"\nConfiguration updated: {field} set to {config[field]}")
        input("\nPress Enter to return to the main menu...")

def generate_sample_logs():
    config = load_config()
    sample_log_entry = create_sample_log_entry(config)
    print("\nSample Log Entry:")
    print(json.dumps(sample_log_entry, indent=4))
    print("\nSample CURL Command:")
    api_url = config.get('api_url', 'https://your-ngsiem-api-url')
    api_key = config.get('api_key', 'your_api_key')
    curl_command = f"curl -X POST {api_url} -H 'Content-Type: application/json' -H 'Authorization: Bearer {api_key}' -d '{json.dumps(sample_log_entry)}'"
    print(curl_command)
    input("\nPress Q to return to the main menu...")

def send_logs_to_ngsiem():
    from generate_logs import send_log_entry
    config = load_config()
    sample_log_entry = create_sample_log_entry(config)
    send_log_entry(sample_log_entry, config)
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
║  3. Clear a configuration value                             ║
║  4. Generate sample logs                                    ║
║  5. Send logs to NGSIEM                                     ║
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
                '3': ('usernames', 'alice, bob'),
                '4': ('mac_addresses', '00:1A:2B:3C:4D:5E, 11:22:33:44:55:66'),
                '5': ('user_agents', 'Mozilla/5.0, Chrome/91.0'),
                '6': ('server_ips', '192.168.1.1, 192.168.1.2'),
                '7': ('client_ips', '10.0.0.1, 10.0.0.2'),
                '8': ('hostnames', 'server1.example.com, server2.example.com')
            }
            field_choice = input("Select a field: ").strip()
            if field_choice in field_map:
                field, example = field_map[field_choice]
                add_config_value(field, example)
            else:
                print("Invalid field choice. Press Enter to return to the main menu.")
                input()
        elif choice == '3':
            print("""
            Select a field to clear values from:
            1. api_url
            2. api_key
            3. usernames
            4. mac_addresses
            5. user_agents
            6. server_ips
            7. client_ips
            8. hostnames
            """)
            field_map = {
                '1': 'api_url',
                '2': 'api_key',
                '3': 'usernames',
                '4': 'mac_addresses',
                '5': 'user_agents',
                '6': 'server_ips',
                '7': 'client_ips',
                '8': 'hostnames'
            }
            field_choice = input("Select a field: ").strip()
            if field_choice in field_map:
                field = field_map[field_choice]
                clear_config_value(field)
            else:
                print("Invalid field choice. Press Enter to return to the main menu.")
                input()
        elif choice == '4':
            generate_sample_logs()
        elif choice == '5':
            send_logs_to_ngsiem()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()