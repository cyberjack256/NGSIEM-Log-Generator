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
SYSLOG_FILE = '/home/ec2-user/NGSIEM-Log-Generator/syslog.log'
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

# Generate realistic sample syslogs following RFC 5424
def generate_syslog_message(hostname, app_name, procid, msgid, message, timestamp):
    pri = 134  # Example priority value for local use
    version = 1
    return f"<{pri}>{version} {timestamp} {hostname} {app_name} {procid} {msgid} - {message}"

# Generate sample syslogs
def generate_sample_syslogs():
    config = load_config()
    now = datetime.utcnow()

    hostnames = config.get('hostnames', ['server1.example.com', 'server2.example.com'])
    network_devices = ["bldg1-room1-rack1", "bldg1-room1-rack2", "bldg2-room1-rack1", "bldg2-room2-rack1"]
    users = config.get('users', [])
    observer_id = config.get('observer_id', 'observer123')

    sample_logs = []
    for _ in range(80):  # 80 logs from servers
        user = random.choice(users)
        hostname = random.choice(hostnames)
        app_name = "app"
        procid = str(random.randint(1000, 9999))
        msgid = "ID" + str(random.randint(100, 999))
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        message = "Sample syslog message from server"

        log_entry = generate_syslog_message(hostname, app_name, procid, msgid, message, timestamp)
        sample_logs.append(log_entry)
    
    for _ in range(20):  # 20 logs from network devices
        hostname = random.choice(network_devices)
        app_name = "netapp"
        procid = str(random.randint(1000, 9999))
        msgid = "ID" + str(random.randint(100, 999))
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        message = "Sample syslog message from network device"

        log_entry = generate_syslog_message(hostname, app_name, procid, msgid, message, timestamp)
        sample_logs.append(log_entry)

    return sample_logs

# Generate syslogs for Eagle's bad login attempts
def generate_bad_syslogs(config):
    users = config.get("users", [])
    network_devices = ["bldg1-room1-rack1", "bldg1-room1-rack2", "bldg2-room1-rack1", "bldg2-room2-rack1"]
    now = datetime.utcnow()
    logs = []

    # Malicious traffic from "eagle"
    user_info = next((u for u in users if u['username'] == "eagle"), None)
    if user_info:
        for _ in range(10):  # Generate 10 bad traffic logs every 15 minutes
            hostname = random.choice(network_devices + config.get('hostnames', []))
            app_name = "auth"
            procid = str(random.randint(1000, 9999))
            msgid = "ID" + str(random.randint(100, 999))
            timestamp = (now - timedelta(minutes=random.randint(1, 5))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            message = "Failed login attempt detected for user eagle"

            log_entry = generate_syslog_message(hostname, app_name, procid, msgid, message, timestamp)
            logs.append(log_entry)
    
    return logs

# Write syslog to file
def write_syslog_to_file(logs):
    log_dir = os.path.dirname(SYSLOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    with open(SYSLOG_FILE, "a") as log_file:
        for log_entry in logs:
            log_file.write(log_entry + "\n")

# Generate sample syslogs
def generate_sample_syslogs_main():
    sample_logs = generate_sample_syslogs()
    bad_syslogs = generate_bad_syslogs(load_config())
    all_logs = sample_logs + bad_syslogs
    write_syslog_to_file(all_logs)

# Continuous log generation for cron job
def continuous_log_generation():
    config = load_config()
    while True:
        all_logs = []
        
        # Generate regular syslogs every minute
        regular_logs = generate_sample_syslogs()
        all_logs.extend(regular_logs)
        
        # Generate bad traffic logs every 15 minutes
        current_time = datetime.utcnow()
        if current_time.minute % 15 == 0:
            bad_traffic_logs = generate_bad_syslogs(config)
            all_logs.extend(bad_traffic_logs)
        
        # Write logs to file
        write_syslog_to_file(all_logs)
        
        # Log execution time
        with open(EXECUTION_LOG, 'a') as exec_log:
            exec_log.write(f"Executed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Sleep for 1 minute before generating the next set of logs
        time.sleep(60)

if __name__ == "__main__":
    continuous_log_generation()
