import json
import logging
import os
import random
import requests
from datetime import datetime, timedelta
import pytz
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

# Create a sample log entry
def create_sample_log_entry(config):
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
            "urlcategory": "news",
            "serverip": random.choice(config.get('server_ips', ["192.168.1.1", "192.168.1.2"])),
            "clienttranstime": random.randint(200, 500),
            "requestmethod": "GET",
            "refererURL": "https://news.example.com",
            "useragent": random.choice(config.get('user_agents', ["Mozilla/5.0", "Chrome/91.0"])),
            "product": "NSS",
            "location": "New York",
            "ClientIP": random.choice(config.get('client_ips', ["10.0.0.1", "10.0.0.2"])),
            "status": "200",
            "user": random.choice(config.get('usernames', ["sparrow", "robin", "eagle"])),
            "url": "https://news.example.com/article",
            "vendor": "Zscaler",
            "hostname": random.choice(config.get('hostnames', ["birdserver.example.com", "eaglehost.example.com"])),
            "clientpublicIP": "203.0.113.0",
            "threatcategory": "none",
            "threatname": "none",
            "filetype": "none",
            "appname": "browser",
            "pagerisk": 10,
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
            "deviceowner": "Admin",
            "devicehostname": "workstation.example.com",
            "decrypted": "no"
        }
    }
    return log_entry

# Send log entry to NGSIEM
def send_log_entry(log_entry, config):
    if 'api_url' not in config or 'api_key' not in config:
        print("\nAPI URL and API Key are not set in the configuration.")
        return

    api_url = config['api_url']
    api_key = config['api_key']

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.post(api_url, headers=headers, json=log_entry)
    if response.status_code == 200:
        print("Log sent successfully.")
    else:
        print(f"Failed to send log: {response.status_code} {response.text}")

if __name__ == "__main__":
    config = load_config()
    sample_log_entry = create_sample_log_entry(config)
    send_log_entry(sample_log_entry, config)