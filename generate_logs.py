import os
import json
import random
import requests
import logging
from datetime import datetime, timedelta
import time

# Set up logging
logging.basicConfig(level=logging.INFO)

# Paths to config files
CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/config.json')
ZS_LOG_EXECUTION_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/generate_logs_execution.log')

# Load configuration from the config file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    logging.error("Configuration file not found.")
    return {}

# Generate additional users based on global locations
def generate_additional_users():
    regions = {
        "US": ["192.168.1.", "192.168.2."],
        "Japan": ["203.0.113.", "198.51.100."],
        "Australia": ["203.0.114.", "198.51.101."],
        "Africa": ["203.0.115.", "198.51.102."],
        "South America": ["203.0.116.", "198.51.103."]
    }
    
    additional_users = []
    for region, ip_bases in regions.items():
        for i in range(1, 101):  # 100 users per region
            user = {
                "username": f"user_{region.lower()}_{i}",
                "client_ip": f"{random.choice(ip_bases)}{random.randint(1, 254)}",
                "location": region,
                "mac_address": f"00:1A:2B:{random.randint(10, 99)}:{random.randint(10, 99)}:{random.randint(10, 99)}",
                "user_agent": random.choice(["Mozilla/5.0", "Chrome/58.0", "Safari/537.36"])
            }
            additional_users.append(user)
    return additional_users

# Generate a regular Zscaler log entry
def generate_regular_log(config):
    return generate_zscaler_logs(config, log_type="regular")

# Generate a bad traffic Zscaler log entry
def generate_bad_traffic_log(config):
    return generate_zscaler_logs(config, log_type="bad_traffic")

# Generate a variety of Zscaler log entries
def generate_zscaler_logs(config, log_type="regular"):
    all_users = config['users'] + generate_additional_users()
    user = random.choice(all_users)
    timestamp = (datetime.utcnow() - timedelta(minutes=random.randint(0, 59))).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    log_entry = {
        "timestamp": timestamp,
        "client_ip": user['client_ip'],
        "username": user['username'],
        "mac_address": user['mac_address'],
        "user_agent": user['user_agent'],
        "action": random.choice(["allowed", "blocked"]),
        "url": random.choice(config.get('resources', {}).get('urls', [
            "http://safe-site.com",
            "http://worksite.aviantech.local",
            "http://api.internal.aviantech.net"
        ])),
        "app_name": random.choice(["Zscaler Internet Access", "Zscaler Private Access"]),
        "category": random.choice([
            "safe browsing", "data upload", "internal api access", "admin login"
        ])
    }
    
    # Customize log type
    if log_type == "bad_traffic":
        log_entry.update({
            "action": "blocked",
            "url": "http://malicious-site.com",
            "category": "malware"
        })
    elif log_type == "admin_action":
        log_entry.update({
            "action": "allowed",
            "url": "http://admin.aviantech.local",
            "category": "admin panel access"
        })
    
    logging.info(f"Generated {log_type} log: {log_entry}")
    return log_entry

# Send logs to NGSIEM using Zscaler API
def send_logs(api_url, api_key, logs):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    for log in logs:
        try:
            response = requests.post(api_url, headers=headers, json=log)
            if response.status_code == 200:
                logging.info(f"Log sent successfully: {log}")
            else:
                logging.error(f"Failed to send log: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending log: {e}")

# Generate and send logs at a high volume
def generate_and_send_logs(config):
    if not config:
        logging.error("Configuration could not be loaded. Exiting.")
        return

    logs_per_minute = 100  # Adjust to generate hundreds of logs per minute
    log_types = ["regular", "bad_traffic", "admin_action", "general"]
    
    while True:
        logs = []
        for _ in range(logs_per_minute):
            log_type = random.choices(log_types, weights=[70, 5, 10, 15], k=1)[0]  # Weighted randomness
            logs.append(generate_zscaler_logs(config, log_type))

        send_logs(config['zscaler_api_url'], config['zscaler_api_key'], logs)
        
        with open(ZS_LOG_EXECUTION_FILE, 'a') as exec_log:
            exec_log.write(f"Logs sent at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")

        time.sleep(60)  # Wait for a minute before sending the next batch

# Generate sample Zscaler logs for testing purposes
def display_sample_log_and_curl():
    config = load_config()
    sample_log = generate_zscaler_logs(config, log_type="regular")
    print(f"Sample Zscaler log: {sample_log}")
    
    curl_command = (
        f"curl -X POST -H 'Content-Type: application/json' "
        f"-H 'Authorization: Bearer {config['zscaler_api_key']}' "
        f"-d '{json.dumps(sample_log)}' {config['zscaler_api_url']}"
    )
    print(f"\nCurl command for testing:\n{curl_command}\n")

if __name__ == "__main__":
    config = load_config()
    generate_and_send_logs(config)