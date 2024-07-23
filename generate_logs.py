import json
import logging
import os
import random
import time
from datetime import datetime, timedelta
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = '/home/ec2-user/NGSIEM-Log-Generator/config.json'
ZSCL_FILE = '/home/ec2-user/NGSIEM-Log-Generator/zscaler.log'
EXECUTION_LOG = '/home/ec2-user/NGSIEM-Log-Generator/generate_logs_execution.log'
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

# Generate realistic Zscaler logs
def generate_zscaler_log(user, action, url, status, method, category, location):
    now = datetime.utcnow()
    timestamp = now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    log_entry = {
        "datetime": timestamp,
        "reason": "allowed" if action == "allowed" else "blocked",
        "event_id": random.randint(100000, 999999),
        "protocol": "HTTPS",
        "action": action,
        "transactionsize": random.randint(1000, 2000),
        "responsesize": random.randint(500, 1000),
        "requestsize": random.randint(100, 500),
        "urlcategory": category,
        "serverip": random.choice(["192.168.1.1", "192.168.1.2"]),
        "clienttranstime": random.randint(200, 500),
        "requestmethod": method,
        "refererURL": f"https://{random.choice(['birdsite.com', 'adminbird.com', 'birdnet.org'])}/",
        "useragent": user["user_agent"],
        "product": "NSS",
        "location": location,
        "ClientIP": user["client_ip"],
        "status": status,
        "user": user["email"],
        "url": url,
        "vendor": "Zscaler",
        "hostname": user["hostname"],
        "clientpublicIP": user["client_ip"],
        "threatcategory": "none",
        "threatname": "none",
        "filetype": "none",
        "appname": "browser",
        "pagerisk": random.randint(1, 100),
        "department": random.choice(["IT", "SOC", "Help-Desk"]),
        "urlsupercategory": "information",
        "appclass": "web",
        "dlpengine": "none",
        "urlclass": category,
        "threatclass": "none",
        "dlpdictionaries": "none",
        "fileclass": "none",
        "bwthrottle": "none",
        "servertranstime": random.randint(100, 300),
        "contenttype": "application/octet-stream",
        "unscannabletype": "none",
        "deviceowner": "Admin",
        "devicehostname": user["hostname"],
        "decrypted": random.choice(["yes", "no"])
    }
    return log_entry

# Generate sample Zscaler logs
def generate_sample_zscaler_logs():
    config = load_config()
    users = config.get('users', [])

    actions = ["allowed", "blocked"]
    statuses = ["200", "404", "500"]
    methods = ["GET", "POST"]
    categories = ["news", "social media", "entertainment", "education"]
    locations = {
        "Austin": "10.0.0.",
        "Singapore": "10.0.1."
    }

    sample_logs = []
    for _ in range(100):
        user = random.choice(users)
        action = random.choice(actions)
        url = f"https://{random.choice(['birdsite.com', 'adminbird.com', 'birdnet.org'])}/{random.choice(['photos', 'posts', 'videos', 'articles'])}"
        status = random.choices(statuses, weights=[80, 10, 10], k=1)[0]
        method = random.choice(methods)
        category = random.choices(categories, weights=[30, 30, 10, 30], k=1)[0]

        location = "Austin" if user["client_ip"].startswith("10.0.0.") else "Singapore"

        log_entry = generate_zscaler_log(user, action, url, status, method, category, location)
        sample_logs.append(log_entry)

    return sample_logs

# Generate Zscaler logs for Eagle's bad attempts
def generate_bad_zscaler_logs(config):
    users = config.get("users", [])
    now = datetime.utcnow()
    logs = []

    # Malicious traffic from "eagle"
    user_info = next((u for u in users if u['username'] == "eagle"), None)
    if user_info:
        for _ in range(10):  # Generate 10 bad traffic logs every 15 minutes
            action = "blocked"
            url = f"https://{random.choice(['adminbird.com'])}/suspicious"
            status = random.choice(["403", "401"])
            method = random.choice(["POST", "GET"])
            category = "malicious"
            location = "Austin" if user_info["client_ip"].startswith("10.0.0.") else "Singapore"

            log_entry = generate_zscaler_log(user_info, action, url, status, method, category, location)
            logs.append(log_entry)
    
    return logs

# Write Zscaler logs to file
def write_zscaler_to_file(logs):
    log_dir = os.path.dirname(ZSCL_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    with open(ZSCL_FILE, "a") as log_file:
        for log_entry in logs:
            log_file.write(json.dumps(log_entry) + "\n")

# Generate sample Zscaler logs
def generate_sample_zscaler_logs_main():
    sample_logs = generate_sample_zscaler_logs()
    bad_zscaler_logs = generate_bad_zscaler_logs(load_config())
    all_logs = sample_logs + bad_zscaler_logs
    write_zscaler_to_file(all_logs)

# Continuous log generation for cron job
def continuous_log_generation():
    config = load_config()
    while True:
        all_logs = []
        
        # Generate regular Zscaler logs every minute
        regular_logs = generate_sample_zscaler_logs()
        all_logs.extend(regular_logs)
        
        # Generate bad traffic logs every 15 minutes
        current_time = datetime.utcnow()
        if current_time.minute % 15 == 0:
            bad_traffic_logs = generate_bad_zscaler_logs(config)
            all_logs.extend(bad_traffic_logs)
        
        # Write logs to file
        write_zscaler_to_file(all_logs)
        
        # Log execution time
        with open(EXECUTION_LOG, 'a') as exec_log:
            exec_log.write(f"Executed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Sleep for 1 minute before generating the next set of logs
        time.sleep(60)

if __name__ == "__main__":
    continuous_log_generation()
