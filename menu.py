import os
import json
from generate_logs import load_config, save_config, generate_sample_logs

PRESETS_FILE = 'presets.json'
CONFIG_FILE = 'config.json'

# Load presets from a separate JSON file
def load_presets():
    with open(PRESETS_FILE, 'r') as file:
        return json.load(file)

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

# Load preset configuration
def load_preset(preset):
    config = load_config()
    presets = load_presets()
    print(f"Available presets: {presets}")  # Debug print to show available presets
    preset_key = str(preset)  # Ensure preset key is a string
    if preset_key in presets:
        print(f"Loading preset {preset_key}...")  # Debug print to indicate loading preset
        config.update(presets[preset_key])
        save_config(config)
        print(f"Preset {preset_key} loaded successfully.")
    else:
        print("Invalid preset selected.")

# Add configuration value
def add_config_value(field, example):
    config = load_config()
    values = []
    while True:
        new_value = input(f"Enter a value for {field} (e.g., {example}) or press [Enter] to return to the menu: ").strip()
        if not new_value:
            break
        values.append(new_value)
    if values:
        config[field] = values
        save_config(config)
        print(f"Configuration updated: {field} set to {config[field]}")

# Show current configuration
def show_config():
    config = load_config()
    print(json.dumps(config, indent=4))

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
║  4. Load preset configuration                               ║
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
            generate_sample_logs()
        elif choice == '4':
            print("""
            1. Bird Names and Comical Bird Adversaries
            2. CrowdStrike Adversaries and Cool Analyst Names
            3. Celestial Body Names and Comical Celestial Adversaries
            """)
            preset_choice = input("Select a preset: ").strip()
            load_preset(preset_choice)
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_menu()