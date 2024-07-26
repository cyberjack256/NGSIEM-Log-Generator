import json
import logging
import os
import random
import time
from datetime import datetime, timedelta, timezone
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO)

# Dynamically get the user home directory
CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/config.json')
SYSLOG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/syslog.log')
EXECUTION_LOG = os.path.expanduser('~/NGSIEM-Log-Generator/generate_syslog_logs_execution.log')
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
def generate_syslog_message(hostname, app_name, procid, msgid, message, timestamp, log_level):
    pri = {
        'info': 6,
        'warning': 4,
        'error': 3
    }[log_level]
    version = 1
    return f"<{pri}>{version} {timestamp} {hostname} {app_name} {procid} {msgid} - {message}"

# Generate sample syslogs
def generate_sample_syslogs():
    config = load_config()
    now = datetime.now(timezone.utc)

    hostnames = config.get('hostnames', ['server1.example.com', 'server2.example.com'])
    users = config.get('users', [])
    log_level = config.get('log_level', 'info')

    if not users:
        raise ValueError("No users found in the configuration.")
    if log_level not in ['info', 'warning', 'error']:
        raise ValueError("Invalid log level in the configuration. Choose from 'info', 'warning', or 'error'.")

    messages = {
        'info': [
            "Routine check: User 'robin' logged in to update the bird photo gallery.",
            "Maintenance alert: Server uptime confirmed by a cheerful chirp from the CPU.",
            "System notification: User 'sparrow' changed the default homepage to a picture of a red cardinal.",
            "Backup complete: All server data safely stored, including the secret bird watching spots.",
            "Update success: The server successfully updated to the latest version of 'FeatherOS'.",
            "Log entry: User 'eagle' set a reminder to refill the bird feeders through the server.",
            "System notice: The server is feeling fresh after a routine cleanup and reboot.",
            "Access granted: User 'hawk' accessed the server to check on the nest cam live feed.",
            "Routine operation: The server automatically cleared out old logs and freed up space for more bird data.",
            "Notification: User 'finch' uploaded a new background image of a beautiful hummingbird for the login screen."
        ],
        'warning': [
            "Warning: High memory usage detected, considering flying south for the winter.",
            "System warning: User 'robin' attempted to upload a large bird photo, exceeding the size limit.",
            "Warning: Disk space running low, feathers may start to ruffle.",
            "Alert: Unusual login pattern detected for user 'eagle'.",
            "Warning: Potential phishing attempt detected in the email logs.",
            "System alert: User 'sparrow' attempted to access restricted files.",
            "Warning: CPU temperature rising, consider cooling measures.",
            "System warning: Multiple failed login attempts detected.",
            "Warning: Network traffic spike detected, possible DDoS attack.",
            "Alert: Unauthorized access attempt detected on port 22."
        ],
        'error': [
            "Error: User 'eagle' failed to login after multiple attempts.",
            "Critical error: Server disk failure detected.",
            "Error: Backup process failed for the bird watching spots data.",
            "System error: Unable to update to the latest version of 'FeatherOS'.",
            "Error: Unauthorized access attempt detected and blocked.",
            "Critical alert: Server overheating, immediate action required.",
            "Error: User 'sparrow' attempted to access restricted files and was blocked.",
            "System failure: Network interface down.",
            "Error: Malware detected in the email attachments.",
            "Critical error: Database connection failed, services impacted."
        ]
    }

    sample_logs = []
    for _ in range(80):  # 80 logs from servers
        user = random.choice(users)
        hostname = random.choice(hostnames)
        app_name = "app"
        procid = str(random.randint(1000, 9999))
        msgid = "ID" + str(random.randint(100, 999))
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        message = random.choice(messages[log_level])

        log_entry = generate_syslog_message(hostname, app_name, procid, msgid, message, timestamp, log_level)
        sample_logs.append(log_entry)
    
    return sample_logs

# Generate syslogs for Eagle's bad login attempts
def generate_bad_syslogs(config):
    users = config.get("users", [])
    now = datetime.now(timezone.utc)
    logs = []

    # Malicious traffic from "eagle"
    user_info = next((u for u in users if u['username'] == "eagle"), None)
    if not user_info:
        raise ValueError("User 'eagle' not found in the configuration.")
    for _ in range(10):  # Generate 10 bad traffic logs every 15 minutes
        hostname = user_info['hostname']
        app_name = "auth"
        procid = str(random.randint(1000, 9999))
        msgid = "ID" + str(random.randint(100, 999))
        timestamp = (now - timedelta(minutes=random.randint(1, 5))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        message = "Failed login attempt detected for user eagle"

        log_entry = generate_syslog_message(hostname, app_name, procid, msgid, message, timestamp, 'error')
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
    try:
        sample_logs = generate_sample_syslogs()
        bad_syslogs = generate_bad_syslogs(load_config())
        all_logs = sample_logs + bad_syslogs
        write_syslog_to_file(all_logs)
    except ValueError as e:
        print(f"Error: {e}")

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
