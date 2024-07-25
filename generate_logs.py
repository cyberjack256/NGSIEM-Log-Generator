import json
import logging
import os
import random
import requests
import time
from datetime import datetime, timedelta, timezone
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = '/home/robin/NGSIEM-Log-Generator/config.json'
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

# Generate regular logs
def generate_regular_logs(config, count):
    users = config.get("users", [])
    logs = []
    
    for _ in range(count):
        user_info = random.choice(users)
        log = generate_zscaler_log(
            config=config,
            user=user_info,
            hostname=user_info['hostname'],
            url="https://birdsite.com/home",
            referer="https://birdsite.com",
            action="allowed",
            reason="Normal traffic"
        )
        logs.append(log)
    
    return logs

# Generate bad traffic logs
def generate_bad_traffic_logs(config):
    users = config.get("users", [])
    logs = []
    
    # Malicious traffic from "eagle"
    user_info = next((u for u in users if u['username'] == "eagle"), None)
    if user_info:
        for _ in range(10):  # Generate 10 bad traffic logs every 15 minutes
            log = generate_zscaler_log(
                config=config,
                user=user_info,
                hostname=user_info['hostname'],
                url="https://adminbird.com/login",
                referer="https://birdsite.com/home",
                action="blocked",
                reason="Unauthorized access attempt"
            )
            logs.append(log)
    
    return logs

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

# Generate sample logs
def generate_sample_logs():
    config = load_config()
    all_logs = []
    
    # Generate 270 regular logs
    regular_logs = generate_regular_logs(config, 270)
    all_logs.extend(regular_logs)
    
    # Generate 30 bad traffic logs
    bad_traffic_logs = generate_bad_traffic_logs(config)
    all_logs.extend(bad_traffic_logs)
    
    # Write logs to a file
    with open('zscaler_sample_logs.json', 'w') as f:
        json.dump(all_logs, f, indent=2)

# Continuous log generation for cron job
def continuous_log_generation():
    config = load_config()
    while True:
        all_logs = []
        
        # Generate 20-30 regular logs every minute
        regular_logs = generate_regular_logs(config, random.randint(20, 30))
        all_logs.extend(regular_logs)
        
        # Generate bad traffic logs every 15 minutes
        current_time = datetime.now(timezone.utc)
        if current_time.minute % 15 == 0:
            bad_traffic_logs = generate_bad_traffic_logs(config)
            all_logs.extend(bad_traffic_logs)
        
        # Write logs to a file
        with open('zscaler_continuous_logs.json', 'a') as f:  # Append to file
            json.dump(all_logs, f, indent=2)
            f.write('\n')  # Ensure each set of logs is on a new line
        
        # Sleep for 1 minute before generating the next set of logs
        time.sleep(60)

if __name__ == "__main__":
    continuous_log_generation()
