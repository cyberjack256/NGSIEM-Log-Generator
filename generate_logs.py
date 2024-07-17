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
    now = datetime.utcnow()
    sample_logs = []

    for _ in range(random.randint(5, 10)):
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
                "urlcategory": "news",
                "serverip": random.choice(config.get('server_ips', [fake.ipv4()])),
                "clienttranstime": random.randint(200, 500),
                "requestmethod": random.choice(["GET", "POST"]),
                "refererURL": fake.url(),
                "useragent": random.choice(config.get('user_agents', [fake.user_agent()])),
                "product": "NSS",
                "location": "New York",
                "ClientIP": random.choice(config.get('client_ips', [fake.ipv4()])),
                "status": random.choice(["200", "404", "500"]),
                "user": random.choice(config.get('usernames', [fake.user_name()])),
                "url": fake.url(),
                "vendor": "Zscaler",
                "hostname": random.choice(config.get('hostnames', [fake.hostname()])),
                "clientpublicIP": fake.ipv4(),
                "threatcategory": "none",
                "threatname": "none",
                "filetype": "none",
                "appname": "browser",
                "pagerisk": random.randint(1, 100),
                "department": "IT",
                "urlsupercategory": "information",
                "appclass": "web",
                "dlpengine": "none",
                "urlclass": "news",
                "threatclass": "none",
                "dlpdictionaries": "none",
                "fileclass": "none",
                "bwthrottle": "none",
                "servertranstime": random.randint(100, 300),
                "contenttype": "text/html",
                "unscannabletype": "none",
                "deviceowner": fake.name(),
                "devicehostname": fake.hostname(),
                "decrypted": random.choice(["yes", "no"])
            }
        }
        sample_logs.append(log_entry)

    return sample_logs

# Send logs to NGSIEM
def send_logs():
    config = load_config()
    if 'api_url' not in config or 'api_key' not in config:
        print("\nAPI URL and API Key are not set in the configuration.")
        return
    
    api_url = config['api_url']
    api_key = config['api_key']
    sample_logs = generate_sample_logs()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    for log_entry in sample_logs:
        response = requests.post(api_url, headers=headers, json=log_entry)
        if response.status_code == 200:
            print("Log sent successfully.")
        else:
            print(f"Failed to send log: {response.status_code} {response.text}")

    # Output example message and curl command
    example_log = json.dumps(sample_logs[0], indent=4)
    example_curl = f"curl -X POST {api_url} -H 'Content-Type: application/json' -H 'Authorization: Bearer {api_key}' -d '{json.dumps(sample_logs[0])}'"

    print("\nExample log message:")
    print(example_log)
    print("\nExample curl command:")
    print(example_curl)