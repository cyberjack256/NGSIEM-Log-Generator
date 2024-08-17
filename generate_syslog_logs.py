import socket
import json
import logging
import os
import random
import time
from datetime import datetime, timedelta, timezone

# Set up logging
logging.basicConfig(level=logging.INFO)

# Paths to config files
CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/config.json')
MESSAGE_CONFIG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/message.config')
SYSLOG_FILE = os.path.expanduser('~/NGSIEM-Log-Generator/syslog.log')
EXECUTION_LOG = os.path.expanduser('~/NGSIEM-Log-Generator/generate_syslog_logs_execution.log')

# Function to resolve domain names to IP addresses
def resolve_domain_to_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        # Handle the case where the domain cannot be resolved
        logging.warning(f"Could not resolve domain: {domain}")
        return "0.0.0.0"

# List of bird conservatorship-related domains
bird_related_domains = [
    "birdlife.org",
    "audubon.org",
    "allaboutbirds.org",
    "ebird.org",
    "nestwatch.org",
    "merlin.allaboutbirds.org",
    "birdwatchingdaily.com",
    "birdsna.org"
]

# Resolve these domains to their IP addresses
bird_related_ips = [resolve_domain_to_ip(domain) for domain in bird_related_domains]

# Load configuration
def load_config(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

# Generate the PRI value based on RFC 5424
def calculate_pri(facility, severity):
    return (facility * 8) + severity

# Generate realistic sample syslogs following RFC 5424
def generate_syslog_message(template, pri, timestamp, hostname, app_name, procid, client_ip, public_ip, srcPort, username=None, mac_address=None, user_agent=None):
    return template.format(
        pri=pri,
        timestamp=timestamp,
        hostname=hostname,
        app_name=app_name,
        procid=procid,
        client_ip=client_ip,
        public_ip=public_ip,
        srcPort=srcPort,
        username=username or "",
        mac_address=mac_address or "",
        user_agent=user_agent or ""
    )

# Generate sample syslogs
def generate_sample_syslogs():
    config = load_config(CONFIG_FILE)
    message_config = load_config(MESSAGE_CONFIG_FILE)
    now = datetime.now(timezone.utc)

    hostnames = config.get('hostnames', ['server1.example.com', 'server2.example.com'])
    users = config.get('users', [])
    log_facility = 1  # User-level messages (typically facility 1)
    severity = 6  # Informational
    pri = calculate_pri(log_facility, severity)

    if not users:
        raise ValueError("No users found in the configuration.")

    messages = message_config.get('info', [])

    sample_logs = []
    for _ in range(80):  # Generate 80 logs from servers
        user = random.choice(users)
        hostname = random.choice(hostnames)
        app_name = "srv_S1_NGFW"
        procid = str(random.randint(1000, 9999))
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%b %d %H:%M:%S')
        message_template = random.choice(messages)
        srcPort = str(random.randint(1024, 65535))

        message = generate_syslog_message(
            template=message_template,
            pri=pri,
            timestamp=timestamp,
            hostname=hostname,
            app_name=app_name,
            procid=procid,
            client_ip=user["client_ip"],
            public_ip=random.choice(bird_related_ips),  # Use bird-related IP
            srcPort=srcPort,
            username=user["username"],
            mac_address=user["mac_address"],
            user_agent=user["user_agent"]
        )

        sample_logs.append(message)
    
    return sample_logs

# Generate syslogs for Eagle's bad login attempts
def generate_bad_syslogs():
    config = load_config(CONFIG_FILE)
    message_config = load_config(MESSAGE_CONFIG_FILE)
    users = config.get("users", [])
    now = datetime.now(timezone.utc)
    logs = []

    # Malicious traffic from "eagle"
    user_info = next((u for u in users if u['username'] == "eagle"), None)
    if not user_info:
        raise ValueError("User 'eagle' not found in the configuration.")
    
    log_facility = 4  # Security/authorization messages (typically facility 4)
    severity = 3  # Error
    pri = calculate_pri(log_facility, severity)

    messages = message_config.get('error', [])

    for _ in range(10):  # Generate 10 bad traffic logs
        hostname = user_info['hostname']
        app_name = "auth"
        procid = str(random.randint(1000, 9999))
        timestamp = (now - timedelta(minutes=random.randint(1, 5))).strftime('%b %d %H:%M:%S')
        message_template = random.choice(messages)
        srcPort = str(random.randint(1024, 65535))

        message = generate_syslog_message(
            template=message_template,
            pri=pri,
            timestamp=timestamp,
            hostname=hostname,
            app_name=app_name,
            procid=procid,
            client_ip=user_info["client_ip"],
            public_ip=random.choice(bird_related_ips),  # Use bird-related IP
            srcPort=srcPort,
            username=user_info["username"],
            mac_address=user_info["mac_address"],
            user_agent=user_info["user_agent"]
        )

        logs.append(message)
    
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
        bad_syslogs = generate_bad_syslogs()
        all_logs = sample_logs + bad_syslogs
        write_syslog_to_file(all_logs)
    except ValueError as e:
        print(f"Error: {e}")

# Continuous log generation
def continuous_log_generation():
    config = load_config(CONFIG_FILE)
    while True:
        all_logs = []
        
        # Generate regular syslogs every minute
        regular_logs = generate_sample_syslogs()
        all_logs.extend(regular_logs)
        
        # Generate bad traffic logs every 15 minutes
        current_time = datetime.utcnow()
        if current_time.minute % 15 == 0:
            bad_traffic_logs = generate_bad_syslogs()
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