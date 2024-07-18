import json
import logging
import os
import random
import requests
from datetime import datetime, timedelta
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = '/home/ec2-user/NGSIEM-Log-Generator/config.json'
fake = Faker()

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

# Generate realistic sample syslogs
def generate_sample_syslogs():
    config = load_config()
    if 'syslog_api_url' not in config or 'syslog_api_key' not in config:
        print("\nAPI URL and API Key are not set in the configuration.")
        return [], ""

    api_url = config['syslog_api_url']
    api_key = config['syslog_api_key']
    now = datetime.utcnow()

    hostnames = config.get('hostnames', ['host1.example.com'])
    users = config.get('users', [])

    sample_logs = []
    for _ in range(1000):
        user = random.choice(users)
        hostname = user['hostname']
        username = user['username']

        log_entry = f"<134>{(now - timedelta(minutes=random.randint(1, 30))).strftime('%b %d %H:%M:%S')} {hostname} {username}: Sample syslog message"

        sample_logs.append(log_entry)

    curl_command = f"curl -X POST {api_url} -H 'Content-Type: application/json' -H 'Authorization: Bearer {api_key}' -d '{json.dumps(sample_logs[0])}'"

    return sample_logs, curl_command

# Write syslog to file
def write_syslog_to_file(log_entry):
    log_dir = "/home/ec2-user/NGSIEM-Log-Generator/var/log"
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "syslog.log")
    
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry + "\n")

# Send syslogs
def send_syslogs(api_url_key, api_key_key):
    config = load_config()
    if api_url_key not in config or api_key_key not in config:
        print(f"\nAPI URL and API Key are not set in the configuration for {api_url_key} and {api_key_key}.")
        return

    api_url = config[api_url_key]
    api_key = config[api_key_key]
    sample_logs, _ = generate_sample_syslogs()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    for log in sample_logs:
        write_syslog_to_file(log)
        response = requests.post(api_url, headers=headers, json={"log": log})
        if response.status_code == 200:
            print("Log sent successfully.")
        else:
            print(f"Failed to send log: {response.status_code} {response.text}")

if __name__ == "__main__":
    generate_sample_syslogs()