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

# Generate email addresses based on usernames and domains
def generate_email(username, domain):
    return f"{username}@{domain}"

# Generate realistic sample logs
def generate_sample_logs():
    config = load_config()
    if 'api_url' not in config or 'api_key' not in config:
        print("\nAPI URL and API Key are not set in the configuration.")
        return [], ""

    api_url = config['api_url']
    api_key = config['api_key']
    now = datetime.utcnow()

    domains = config.get('domains', ['example.com'])
    hostnames = config.get('hostnames', ['host1.example.com'])
    usernames = config.get('usernames', ['user'])

    sample_logs = []
    for _ in range(25):
        base_domain = random.choice(domains)
        hostname = random.choice(hostnames)
        username = random.choice(usernames)
        email = generate_email(username, base_domain)

        internal_url = f"https://{base_domain}/{fake.uri_path()}"
        referer_url = f"https://{base_domain}/{fake.uri_path()}"
        external_url = fake.url()
        
        is_internal = random.choice([True, False])
        url = internal_url if is_internal else external_url
        referer = referer_url if is_internal else external_url

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
                "serverip": random.choice(config.get('server_ips', ['192.168.1.2'])),
                "clienttranstime": random.randint(200, 500),
                "requestmethod": random.choice(["GET", "POST"]),
                "refererURL": referer,
                "useragent": random.choice(config.get('user_agents', ['Mozilla/5.0'])),
                "product": "NSS",
                "location": "New York",
                "ClientIP": random.choice(config.get('client_ips', ['10.0.0.2'])),
                "status": random.choice(["200", "404", "500"]),
                "user": email,
                "url": url,
                "vendor": "Zscaler",
                "hostname": hostname,
                "clientpublicIP": fake.ipv4(),
                "threatcategory": "none",
                "threatname": "none",
                "filetype": "none",
                "appname": "browser",
                "pagerisk": random.randint(1, 100),
                "department": random.choice(["IT", "HR", "Finance"]),
                "urlsupercategory": "information",
                "appclass": "web",
                "dlpengine": "none",
                "urlclass": "news",
                "threatclass": "none",
                "dlpdictionaries": "none",
                "fileclass": "none",
                "bwthrottle": "none",
                "servertranstime": random.randint(100, 300),
                "contenttype": "application/octet-stream",
                "unscannabletype": "none",
                "deviceowner": "Admin",
                "devicehostname": hostname,
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