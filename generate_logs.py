import json
import random
import requests
from datetime import datetime

CONFIG_FILE = 'config.json'

def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def generate_web_log_entry(config, user, url, user_agent, ip, action="allowed"):
    timestamp = datetime.utcnow().isoformat() + "Z"
    log_entry = {
        "Vendor": {
            "datetime": timestamp,
            "recordid": random.randint(100000, 999999),
            "action": action,
            "url": url,
            "hostname": url.split("//")[1],
            "protocol": "HTTP",
            "requestsize": random.randint(200, 2000),
            "responsesize": random.randint(500, 5000),
            "contenttype": "text/html",
            "useragent": user_agent,
            "ClientIP": ip,
            "serverip": "203.0.113.1",
            "elogin": user
        },
        "event": {
            "report_time": timestamp,
            "created": timestamp,
            "module": "zia",
            "dataset": "zia.web"
        },
        "attributes": {
            "geo": {
                "city_name": "Sample City",
                "country_name": "Sample Country",
                "location": {
                    "lat": 0.0,
                    "lon": 0.0
                }
            },
            "observer": {
                "alias": "SampleAlias",
                "id": "SampleID"
            },
            "ecs": {
                "version": "8.11.0"
            }
        }
    }
    
    return log_entry

def send_log_to_api(log_entry, api_url):
    response = requests.post(api_url, json=log_entry)
    if response.status_code == 200:
        print(f"Successfully sent log entry: {log_entry}")
    else:
        print(f"Failed to send log entry: {log_entry}")

def main():
    config = load_config()
    api_url = config['ngsiem_api_url']

    # Generate logs for normal users
    for user in config['users']:
        log_entry = generate_web_log_entry(
            config,
            user=user,
            url="https://goodpatch.example.com",
            user_agent=random.choice(config['user_agents']),
            ip=random.choice(config['ips'])
        )
        send_log_to_api(log_entry, api_url)

    # Generate logs for the malicious user
    malicious_log_entry = generate_web_log_entry(
        config,
        user=config['malicious_user'],
        url=config['malicious_site'],
        user_agent=random.choice(config['user_agents']),
        ip=random.choice(config['ips']),
        action="blocked"  # Indicating malicious activity
    )
    malicious_log_entry['Vendor']['malware_hash'] = config['malicious_hash']
    send_log_to_api(malicious_log_entry, api_url)

if __name__ == "__main__":
    main()