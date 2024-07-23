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
EXECUTION_LOG = '/home/ec2-user/NGSIEM-Log-Generator/generate_syslog_logs_execution.log'
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
def generate_syslog_message(hostname, app_name, procid, msgid, message, severity, timestamp):
    pri = 134  # Example priority value for local use
    version = 1
    return f"<{pri}>{version} {timestamp} {hostname} {app_name} {procid} {msgid} [{severity}] - {message}"

# Generate sample syslogs
def generate_sample_syslogs():
    config = load_config()
    now = datetime.utcnow()

    log_levels = config.get('log_levels', ['info'])
    hostnames = config.get('hostnames', ['server1.example.com', 'server2.example.com'])
    network_devices = config.get('network_devices', ["bldg1-room1-rack1", "bldg1-room1-rack2"])
    users = config.get('users', [])
    observer_id = config.get('observer_id', 'observer123')

    info_messages = [
        "Routine check: User '{user}' logged in to update the bird photo gallery.",
        "Maintenance alert: Server uptime confirmed by a cheerful chirp from the CPU.",
        "System notification: User '{user}' changed the default homepage to a picture of a red cardinal.",
        "Backup complete: All server data safely stored, including the secret bird watching spots.",
        "Update success: The server successfully updated to the latest version of 'FeatherOS'.",
        "Log entry: User '{user}' set a reminder to refill the bird feeders through the server.",
        "System notice: The server is feeling fresh after a routine cleanup and reboot.",
        "Access granted: User '{user}' accessed the server to check on the nest cam live feed.",
        "Routine operation: The server automatically cleared out old logs and freed up space for more bird data.",
        "Notification: User '{user}' uploaded a new background image of a beautiful hummingbird for the login screen."
    ]

    warning_messages = [
        "High memory usage detected on server, consider checking running processes.",
        "Unusual login pattern detected for user '{user}', further investigation recommended.",
        "Disk space running low on server, cleaning up unnecessary files.",
        "Multiple failed login attempts detected, possible brute force attack.",
        "High CPU usage detected, performance may be degraded."
    ]

    error_messages = [
        "Failed login attempt detected for user 'eagle'.",
        "Critical disk space issue, server unable to save logs.",
        "Unexpected server reboot, possible hardware failure.",
        "Unauthorized access attempt detected from IP: {client_ip}.",
        "Data corruption detected in database, restoration required."
    ]

    sample_logs = []

    for _ in range(80):  # 80 logs from servers
        user = random.choice(users)
        hostname = random.choice(hostnames)
        app_name = "app"
        procid = str(random.randint(1000, 9999))
        msgid = "ID" + str(random.randint(100, 999))
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        log_level = random.choice(log_levels)
        if log_level == 'info':
            message_template = random.choice(info_messages)
            message = message_template.format(user=user['username'])
            severity = "info"
        elif log_level == 'warning':
            message_template = random.choice(warning_messages)
            message = message_template.format(user=user['username'], client_ip=user.get('client_ip', 'Unknown IP'))
            severity = "warning"
        else:
            message_template = random.choice(error_messages)
            message = message_template.format(user=user['username'], client_ip=user.get('client_ip', 'Unknown IP'))
            severity = "error"

        log_entry = generate_syslog_message(hostname, app_name, procid, msgid, message, severity, timestamp)
        sample_logs.append(log_entry)
    
    for _ in range(20):  # 20 logs from network devices
        user = random.choice(users)
        hostname = random.choice(network_devices)
        app_name = "netapp"
        procid = str(random.randint(1000, 9999))
        msgid = "ID" + str(random.randint(100, 999))
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        log_level = random.choice(log_levels)
        if log_level == 'info':
            message_template = random.choice(info_messages)
            message = message_template.format(user=user['username'])
            severity = "info"
        elif log_level == 'warning':
            message_template = random.choice(warning_messages)
            message = message_template.format(user=user['username'], client_ip=user.get('client_ip', 'Unknown IP'))
            severity = "warning"
        else:
            message_template = random.choice(error_messages)
            message = message_template.format(user=user['username'], client_ip=user.get('client_ip', 'Unknown IP'))
            severity = "error"

        log_entry = generate_syslog_message(hostname, app_name, procid, msgid, message, severity, timestamp)
        sample_logs.append(log_entry)

    return sample_logs

# Generate syslogs for Eagle's bad login attempts
def generate_bad_syslogs(config):
    users = config.get("users", [])
    network_devices = config.get('network_devices', ["bldg1-room1-rack1", "bldg1-room1-rack2"])
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
            severity = "error"

            log_entry = generate_syslog_message(hostname, app_name, procid, msgid, message, severity, timestamp)
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
