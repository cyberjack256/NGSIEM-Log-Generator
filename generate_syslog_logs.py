import json
import logging
import os
import random
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
    now = datetime.utcnow()

    hostnames = config.get('hostnames', ['host1.example.com'])
    users = config.get('users', [])
    observer_id = config.get('observer_id', 'observer123')

    sample_logs = []
    for _ in range(1000):
        user = random.choice(users)
        hostname = user['hostname']
        username = user['username']
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%b %d %H:%M:%S')

        log_entry = f"{timestamp} {hostname} {username} [{observer_id}] Sample syslog message"

        sample_logs.append(log_entry)

    return sample_logs

# Write syslog to file
def write_syslog_to_file(log_entries):
    log_dir = "/home/ec2-user/NGSIEM-Log-Generator"
    log_file_path = os.path.join(log_dir, "syslog.log")
    
    with open(log_file_path, "a") as log_file:
        for log_entry in log_entries:
            log_file.write(log_entry + "\n")

if __name__ == "__main__":
    sample_logs = generate_sample_syslogs()
    write_syslog_to_file(sample_logs)