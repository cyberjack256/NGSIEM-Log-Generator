import json
import logging
import os
import random
import requests
from datetime import datetime, timedelta
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = 'config.json'
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

# Generate sample logs
def generate_sample_logs():
    config = load_config()
    if 'api_url' not in config or 'api_key' not in config:
        print("\nAPI URL and API Key are not set in the configuration.")
        return [], ""

    api_url = config['api_url']
    api_key = config['api_key']
    now = datetime.utcnow()

    internal_sites = config.get('hostnames', ['example.com'])
    external_sites = [fake.url() for _ in range(5)]

    sample_logs = []
    for _ in range(25):
        is_internal = random.choice([True, False])
        if is_internal:
            base_url = random.choice(internal_sites)
            url = f"https://{base_url}/{fake.uri_path()}"
            referer = f"https://{base_url}/{fake.uri_path()}"
        else:
            url = fake.url()
            referer = fake.url()

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
                "urlcategory": "news" if is_internal else "external",
                "serverip": random.choice(config.get('server_ips', [fake.ipv4()])),
                "clienttranstime": random.randint(200, 500),
                "requestmethod": random.choice(["GET", "POST"]),
                "refererURL": referer,
                "useragent": random.choice(config.get('user_agents', [fake.user_agent()])),
                "product": "NSS",
                "location": fake.city(),
                "ClientIP": random.choice(config.get('client_ips', [fake.ipv4()])),
                "status": random.choice(["200", "404", "500"]),
                "user": random.choice(config.get('usernames', [fake.user_name()])),
                "url": url,
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
        sample_logs.append(log_entry)

    curl_command = f"curl -X POST {api_url} -H 'Content-Type: application/json' -H 'Authorization: Bearer {api_key}' -d '{json.dumps(sample_logs[0])}'"

    return sample_logs, curl_command

# Send logs
def send_logs():
    sample_logs, _ = generate_sample_logs()
    config = load_config()
    if 'api_url' not in config or 'api_key' not in config:
        print("\nAPI URL and API Key are not set in the configuration.")
        return

    api_url = config['api_url']
    api_key = config['api_key']
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    for log in sample_logs:
        response = requests.post(api_url, headers=headers, json=log)
        if response.status_code == 200:
            print("Log sent successfully.")
        else:
            print(f"Failed to send log: {response.status_code} {response.text}")

if __name__ == "__main__":
    generate_sample_logs()