import json
import logging
import os
import random
import requests
from datetime import datetime, timedelta, timezone
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO)

# Dynamically get the user home directory
CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/config.json')
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

# Generate Zscaler log
def generate_zscaler_log(config, user, hostname, url, referer, action, reason):
    now = datetime.now(timezone.utc)
    log_entry = {
        "sourcetype": "zscalernss-web",
        "event": {
            "datetime": (now - timedelta(minutes=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S"),
            "reason": reason,
            "event_id": random.randint(100000, 999999),
            "protocol": "HTTPS",
            "action": action,
            "transactionsize": random.randint(1000, 2000),
            "responsesize": random.randint(500, 1000),
            "requestsize": random.randint(100, 500),
            "urlcategory": "news" if "birdsite.com" in url else "external",
            "serverip": random.choice(config.get('server_ips', ['192.168.1.2'])),
            "clienttranstime": random.randint(200, 500),
            "requestmethod": random.choice(["GET", "POST"]),
            "refererURL": referer,
            "useragent": random.choice(config.get('user_agents', ['Mozilla/5.0'])),
            "product": "NSS",
            "location": "New York",
            "ClientIP": user["client_ip"],
            "status": random.choice(["200", "404", "500"]),
            "user": user["email"],
            "url": url,
            "vendor": "Zscaler",
            "hostname": hostname,
            "clientpublicIP": fake.ipv4(),
            "threatcategory": "none",
            "threatname": "none",
            "filetype": "none",
            "appname": "browser",
            "pagerisk": random.randint(1, 100),
            "department": random.choice(["IT", "SOC", "Help-Desk"]),
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
            "decrypted": random.choice(["yes", "no"]),
            "resource_accessed": url if "sensitive-data" in url else "N/A"
        }
    }
    return log_entry

# Generate regular log
def generate_regular_log(config):
    users = config.get("users", [])
    if not users:
        raise ValueError("No users found in the configuration.")
    user_info = random.choice(users)
    url = f"https://{random.choice(['birdsite.com', 'adminbird.com', 'birdnet.org'])}/{random.choice(['home', 'photos', 'posts', 'videos', 'articles'])}"
    log = generate_zscaler_log(
        config=config,
        user=user_info,
        hostname=user_info['hostname'],
        url=url,
        referer="https://birdsite.com",
        action="allowed",
        reason="Normal traffic"
    )
    return log

# Generate bad traffic log
def generate_bad_traffic_log(config):
    user_info = next((u for u in config.get("users", []) if u['username'] == "eagle"), None)
    if not user_info:
        raise ValueError("User 'eagle' not found in the configuration.")
    log = generate_zscaler_log(
        config=config,
        user=user_info,
        hostname=user_info['hostname'],
        url="https://adminbird.com/login",
        referer="https://birdsite.com/home",
        action="blocked",
        reason="Unauthorized access attempt"
    )
    return log

# Send logs to NGSIEM
def send_logs(api_url, api_key, logs):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    for log in logs:
        response = requests.post(api_url, headers=headers, json=log)
        if response.status_code == 200:
            print("Log sent successfully.")
        else:
            print(f"Failed to send log: {response.status_code} {response.text}")

# Display sample log and curl command
def display_sample_log_and_curl():
    try:
        config = load_config()
        if not check_required_fields(config):
            return
        
        good_log = generate_regular_log(config)
        bad_log = generate_bad_traffic_log(config)

        sample_logs = {
            "Good Traffic Log": good_log,
            "Bad Traffic Log": bad_log
        }

        for log_type, log in sample_logs.items():
            log_str = json.dumps(log, indent=4)
            print(f"\n--- {log_type} ---")
            print(log_str)
            api_url = config.get('zscaler_api_url')
            api_key = config.get('zscaler_api_key')
            curl_command = f"curl -X POST {api_url} -H 'Content-Type: application/json' -H 'Authorization: Bearer {api_key}' -d '{log_str}'"
            print(f"\nCurl command to send the {log_type.lower()} to NGSIEM:\n\n{curl_command}\n")

        print("\nNote: The logs above are samples and have not been sent to NGSIEM. The curl commands provided can be used to send these logs to NGSIEM.\n")
    except ValueError as e:
        print(f"Error: {e}")

# Check required fields
def check_required_fields(config):
    required_fields = ['zscaler_api_url', 'zscaler_api_key', 'observer.id', 'encounter.alias']
    missing_fields = [field for field in required_fields if field not in config or not config[field]]
    if missing_fields:
        print(f"Missing required configuration fields: {', '.join(missing_fields)}")
        return False
    return True

if __name__ == "__main__":
    display_sample_log_and_curl()