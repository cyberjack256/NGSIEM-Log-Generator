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

# Load configuration
def load_config(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

# Function to resolve domain names to IP addresses
def resolve_domain_to_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        # Handle the case where the domain cannot be resolved
        logging.warning(f"Could not resolve domain: {domain}")
        return "0.0.0.0"

# Function to generate a single syslog message
def generate_syslog_message(template, **kwargs):
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logging.error(f"Missing key in template: {e}")
        return None

# Generate sample syslogs
def generate_sample_syslogs():
    config = load_config(CONFIG_FILE)
    message_config = load_config(MESSAGE_CONFIG_FILE)
    now = datetime.now(timezone.utc)

    hostnames = [
        "birdcentral.nest.local",
        "nestaccess.adminbird.net",
        "birdwatch.cams.net",
        "birdnet.secure.local",
        "nestwall.firewall.local"
    ]
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
        app_name = random.choice([
            "NestAccess",
            "BirdNet",
            "BirdWatch",
            "NestWall",
            "BirdCentral"
        ])
        procid = str(random.randint(1000, 9999))
        timestamp = (now - timedelta(minutes=random.randint(1, 30))).strftime('%Y-%m-%dT%H:%M:%SZ')
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

        if message:
            sample_logs.append(message)
    
    return sample_logs

# Send logs via UDP to a syslog server
def send_logs_to_syslog_server(logs, server_ip='127.0.0.1', port=514):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for log in logs:
        sock.sendto(log.encode(), (server_ip, port))
    sock.close()

# Write syslog to file
def write_syslog_to_file(logs):
    log_dir = os.path.dirname(SYSLOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    with open(SYSLOG_FILE, "a") as log_file:
        for log_entry in logs:
            log_file.write(log_entry + "\n")

# Generate logs to file or send to syslog server
def generate_logs(destination='file'):
    sample_logs = generate_sample_syslogs()
    bad_logs = generate_bad_syslogs()
    all_logs = sample_logs + bad_logs

    if destination == 'file':
        write_syslog_to_file(all_logs)
    elif destination == 'syslog':
        send_logs_to_syslog_server(all_logs)

# Main function to generate logs
def generate_logs_main():
    try:
        generate_logs('file')  # Generate logs to file
        generate_logs('syslog')  # Send logs to syslog server
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_logs_main()