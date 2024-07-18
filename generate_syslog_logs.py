import json
import logging
import os
import random
import requests
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

# Generate email addresses based on usernames and domains
def generate_email(username, domain):
    return f"{username}@{domain}"

# Generate realistic syslog sample logs
def generate_sample_syslog_logs():
    config = load_config()
    if 'syslog_api_url' not in config or 'syslog_api_key' not in config:
        print("\nSyslog API URL and API Key are not set in the configuration.")
        return [], ""

    api_url = config['syslog_api_url']
    api_key = config['syslog_api_key']
    now = datetime.utcnow()

    domains = config.get('domains', ['example.com'])
    users = config.get('users', [{'username': 'user', 'email': 'user@example.com', 'hostname': 'host1.example.com'}])

    sample_logs = []
    for _ in range(200):  # Generating more logs for syslog
        user = random.choice(users)
        base_domain = user['email'].split('@')[-1]
        username = user['username']
        hostname = user['hostname']
        email = user['email']

        internal_url = f"https://{base_domain}/{fake.uri_path()}"
        referer_url = f"https://{base_domain}/{fake.uri_path()}"
        external_url = fake.url()
        
        is_internal = random.choice([True, False])
        url = internal_url if is_internal else external_url
        referer = referer_url if is_internal else external_url

        log_entry = {
            "syslog": {
                "datetime": (now - timedelta(minutes=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S"),
                "hostname": hostname,
                "appname": "syslog",
                "procid": str(random.randint(1000, 9999)),
                "msgid": "ID" + str(random.randint(1000, 9999)),
                "message": f"{username} accessed {url} from {hostname} with {random.choice(['success', 'failure'])}",
                "severity": random.choice(["info", "warning", "error"]),
                "facility": random.choice(["auth", "authpriv", "cron", "daemon", "kern", "lpr", "mail", "news", "syslog", "user", "uucp", "local0", "local1", "local2", "local3", "local4", "local5", "local6", "local7"])
            }
        }
        sample_logs.append(log_entry)

    curl_command = f"curl -X POST {api_url} -H 'Content-Type: application/json' -H 'Authorization: Bearer {api_key}' -d '{json.dumps(sample_logs[0])}'"

    return sample_logs, curl_command

# Send syslog logs
def send_syslog_logs():
    sample_logs, _ = generate_sample_syslog_logs()
    config = load_config()
    if 'syslog_api_url' not in config or 'syslog_api_key' not in config:
        print("\nSyslog API URL and API Key are not set in the configuration.")
        return

    api_url = config['syslog_api_url']
    api_key = config['syslog_api_key']
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    for log in sample_logs:
        response = requests.post(api_url, headers=headers, json=log)
        if response.status_code == 200:
            print("Log sent successfully.")
        else:
            print(f"Failed to send log: {response.status_code} {response.text}")

if __name__ == "__main__":
    generate_sample_syslog_logs()