import json
import logging
import os
import random
import time
from datetime import datetime, timedelta, timezone
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = '/home/robin/NGSIEM-Log-Generator/config.json'
SYSLOG_FILE = '/home/robin/NGSIEM-Log-Generator/syslog.log'
EXECUTION_LOG = '/home/robin/NGSIEM-Log-Generator/generate_syslog_logs_execution.log'
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
    pri = {"info": 134, "warning": 132, "error": 131}[log_level]
    version = 1
    return f"<{pri}>{version} {timestamp} {hostname} {app_name} {procid} {msgid} - {message}"

# Generate sample syslogs
def generate_sample_syslogs():
    config = load_config()
    now = datetime.now(timezone.utc)
    log_level = config.get("log_level", "info")

    hostnames = [user['hostname'] for user in config.get('users', [])]
    users = config.get('users', [])
    observer_id = config.get('observer_id', 'observer123')

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

    network_messages = [
        "Connection established: Router happily connected user 'robin' to the birdwatching network.",
        "Routine check: Network traffic flowing smoothly, no congestion in the bird feeder livestream.",
        "System notice: User 'sparrow' successfully connected her smart birdhouse to the network.",
        "Update complete: Router firmware updated to the latest version without a hitch.",
        "Connection log: User 'finch' joined the network and streamed his favorite bird documentaries.",
        "Network check: All devices connected, and the router is feeling 'well-nested'.",
        "Log entry: User 'hawk' set up a guest network for the annual birdwatching conference.",
        "System alert: Router detected and blocked an attempt to overload the network with bird memes.",
        "Connection status: User 'owl' accessed the network and is binge-watching 'Birds of Prey' series.",
        "Routine operation: The network's daily self-check reported no issues.",
        "Network notice: User 'falcon' set up a new bird feeder monitor, and the router welcomed it warmly.",
        "Log entry: Router successfully assigned new IP addresses to all birdwatching devices.",
        "Connection log: User 'eagle' connected his drone for aerial birdwatching.",
        "System check: Router firmware is up to date, and all connections are stable.",
        "Routine alert: User 'dove' set up a smart water fountain, and the network is feeling refreshed.",
        "Log entry: User 'parrot' joined the network and shared his latest bird mimicry recordings.",
        "Connection established: User 'pigeon' connected her binoculars with Wi-Fi for instant zoom.",
        "System update: Router received and applied a minor configuration tweak.",
        "Network status: All systems operational, and the network is 'flying high'.",
        "Routine check: User 'sparrow' connected her e-reader for some late-night birdwatching tips."
    ]

    sample_logs = []
    for _ in range(80):  # 80 logs from servers
        user = random.choice(users)
        hostname = user["hostname"]
        app_name = "app"
        procid = str(random.randint(1000, 9999))
        msgid = "ID" + str(random.randint(100, 999))
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        message = random.choice(server_messages)

        log_entry = generate_syslog_message(hostname, app_name, procid, msgid, message, timestamp, log_level)
        sample_logs.append(log_entry)
    
    for _ in range(20):  # 20 logs from network devices
        hostname = random.choice(hostnames)
        app_name = "netapp"
        procid = str(random.randint(1000, 9999))
        msgid = "ID" + str(random.randint(100, 999))
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        message = random.choice(network_messages)

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
    if user_info:
        for _ in range(10):  # Generate 10 bad traffic logs every 15 minutes
            hostname = user_info['hostname']
            app_name = "auth"
            procid = str(random.randint(1000, 9999))
            msgid = "ID" + str(random.randint(100, 999))
            timestamp = (now - timedelta(minutes=random.randint(1, 5))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            message = "Failed login attempt detected for user eagle"

            log_entry = generate_syslog_message(hostname, app_name, procid, msgid, message, timestamp, "error")
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
        current_time = datetime.now(timezone.utc)
        if current_time.minute % 15 == 0:
            bad_traffic_logs = generate_bad_syslogs(config)
            all_logs.extend(bad_traffic_logs)
        
        # Write logs to file
        write_syslog_to_file(all_logs)
        
        # Log execution time
        with open(EXECUTION_LOG, 'a') as exec_log:
            exec_log.write(f"Executed at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Sleep for 1 minute before generating the next set of logs
        time.sleep(60)

if __name__ == "__main__":
    continuous_log_generation()
