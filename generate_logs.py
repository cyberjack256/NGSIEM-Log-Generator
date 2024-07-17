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

# Generate random URL within a domain
def generate_random_url(domain):
    paths = ["news", "articles", "blog", "posts", "updates"]
    return f"https://{domain}/{random.choice(paths)}"

# Generate sample logs
def generate_sample_logs():
    config = load_config()
    if 'api_url' not in config or 'api_key' not in config:
        print("\nAPI URL and API Key are not set in the configuration.")
        return

    api_url = config['api_url']
    api_key = config['api_key']
    now = datetime.utcnow()
    user = random.choice(config['users'])

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
            "serverip": random.choice(config['server_ips']),
            "clienttranstime": random.randint(200, 500),
            "requestmethod": random.choice(["GET", "POST"]),
            "refererURL": generate_random_url(random.choice(config['domains'])),
            "useragent": random.choice(config['user_agents']),
            "product": "NSS",
            "location": fake.city(),
            "ClientIP": random.choice(config['client_ips']),
            "status": random.choice(["200", "404", "500"]),
            "user": user['email'],
            "url": generate_random_url(random.choice(config['domains'])),
            "vendor": "Zscaler",
            "hostname": user['hostname'],
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
            "devicehostname": user['hostname'],
            "decrypted": random.choice(["yes", "no"])
        }
    }

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
    generate_sample_logs()