import json
import logging
import os
import random
import time
from datetime import datetime, timedelta
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = '~/NGSIEM-Log-Generator/config.json'
SYSLOG_FILE = '~/NGSIEM-Log-Generator/syslog.log'
EXECUTION_LOG = '~/NGSIEM-Log-Generator/generate_syslog_logs_execution.log'
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
    now = datetime.utcnow()

    hostnames = config.get('hostnames', ['server1.example.com', 'server2.example.com'])
    users = config.get('users', [])
    log_level = config.get('log_level', 'info')

    server_messages = [
        "Routine check: User 'robin' logged in to update the bird photo gallery.",
        "Maintenance alert: Server uptime confirmed by a cheerful chirp from the CPU.",
        "System notification: User 'sparrow' changed the default homepage to a picture of a red cardinal.",
        "Backup complete: All server data safely stored, including the secret bird watching spots.",
        "Update success: The server successfully updated to the latest version of 'FeatherOS'.",
        "Log entry: User 'eagle' set a reminder to refill the bird feeders through the server.",
        "System notice: The server is feeling fresh after a routine cleanup and reboot.",
        "Access granted: User 'hawk' accessed the server to check on the nest cam live feed.",
        "Routine operation: The server automatically cleared out old logs and freed up space for more bird data.",
        "Notification: User 'finch' uploaded a new background image of a beautiful hummingbird for the login screen.",
        "System check: CPU temperature is normal, and it reports feeling 'as cool as a penguin'.",
        "Log entry: User 'owl' scheduled a meeting reminder via the server calendar to discuss nocturnal bird behavior.",
        "Backup status: All files backed up, including the rare bird call recordings.",
        "Update complete: The server's antivirus definitions are now up to date with the latest birdwatching threats.",
        "Access log: User 'parrot' successfully changed his password to 'pollywantsacracker'.",
        "Routine maintenance: Server disk cleanup completed, files neatly organized like a bird's nest.",
        "System alert: User 'falcon' configured the server to send daily bird facts.",
        "Security check: All systems are secure and running smoothly, like a well-fed pigeon.",
        "Log entry: User 'dove' added her birdwatching events to the server calendar.",
        "System notice: The server's self-check returned a status of 'all feathers intact'."
    ]

    sample_logs = []
    for _ in range(80):  # 80 logs from servers
        user = random.choice(users)
        hostname = random.choice(hostnames)
        app_name = "app"
        procid = str(random.randint(1000, 9999))
        msgid = "ID" + str(random.randint(100, 999))
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        message = random.choice(server_messages)

        log_entry = generate_syslog_message(hostname, app_name, procid, msgid, message, timestamp, log_level)
        sample_logs.append(log_entry)
    
    return sample_logs

# Generate syslogs for Eagle's bad login attempts
def generate_bad_syslogs(config):
    users = config.get("users", [])
    now = datetime.utcnow()
    logs = []

    # Malicious traffic from "eagle"
    user_info = next((u for u in users if u['username'] == "eagle"), None)
    if user_info:
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
