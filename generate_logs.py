import json
import requests
from datetime import datetime
import random
import os
import sys

CONFIG_FILE = 'config.json'

def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def generate_log(user, url, action, threat_name, category, additional_info=None):
    log = {
        "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "source_ip": user["ip"],
        "destination_ip": "203.0.113.10" if "malicious" in url else "93.184.216.34",
        "url": url,
        "action": action,
        "user_agent": user["user_agent"],
        "bytes_sent": random.randint(100, 500),
        "bytes_received": random.randint(500, 2000),
        "category": category,
        "threat_name": threat_name,
        "event_name": "Network Threshold Policy Violation",
        "srcPostNAT": user["ip"],
        "realm": "Location 1",
        "usrName": user["name"],
        "srcBytes": random.randint(100, 500),
        "dstBytes": random.randint(500, 2000),
        "role": "Unauthenticated Transactions",
        "policy": "Policy violation: Malware detected",
        "urlcategory": "Malware",
        "urlsupercategory": "Advanced Security",
        "urlclass": "Advanced Security Risk",
        "appclass": "General Browsing",
        "appname": "generalbrowsing",
        "malwaretype": "Clean Transaction",
        "malwareclass": "Clean Transaction",
        "threatname": "Win32.PUA.Jeefo",
        "riskscore": 100,
        "dlpdict": "None",
        "dlpeng": "None",
        "fileclass": "None",
        "filetype": "None",
        "reqmethod": "POST",
        "respcode": "200",
        "recordid": random.randint(1000000000, 9999999999)
    }
    if additional_info:
        log.update(additional_info)
    return log

def send_to_logscale(log, config):
    headers = {
        "Authorization": f"Bearer {config['logscale_api_token']}",
        "Content-Type": "application/json"
    }
    response = requests.post(config['logscale_url'], json=[log], headers=headers)
    return response.status_code, response.text

def simulate_web_access(user, url):
    os.system(f'curl -A "{user["user_agent"]}" {url} > /dev/null 2>&1')

def generate_windows_event_logs():
    # PowerShell script to generate Windows Event logs
    powershell_script = '''
    # Create process creation log
    Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File C:\\Users\\Eagle\\Downloads\\malware.ps1'

    # Simulate file creation
    New-Item -Path "C:\\Users\\Eagle\\Downloads" -Name "malware.exe" -ItemType "File"

    # Simulate registry modification
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" -Name "MaliciousApp" -Value "C:\\Users\\Eagle\\Downloads\\malware.exe"
    '''
    with open('generate_event_logs.ps1', 'w') as file:
        file.write(powershell_script)
    os.system('powershell -ExecutionPolicy Bypass -File generate_event_logs.ps1')

def test_commands():
    print("Testing curl command...")
    response = os.system('curl --version')
    if response == 0:
        print("Curl is installed and working.")
    else:
        print("Curl is not installed or not working. Please install curl.")
        sys.exit(1)

def main():
    config = load_config()
    logs = []

    if config.get("test_mode", False):
        test_commands()

    users = config["users"]
    narratives = [
        {"user": users[0], "url": config["malicious_urls"][0], "action": "allowed", "threat_name": "Bad Patch Site", "category": "Malware"},
        {"user": users[0], "url": config["malicious_urls"][1], "action": "allowed", "threat_name": "Malicious Email Link", "category": "Phishing"},
        {"user": users[0], "url": config["malicious_file_url"], "action": "allowed", "threat_name": "Known Malicious File", "category": "Malware", "additional_info": {"file_hash": config["malicious_file_hash"]}},
        {"user": users[1], "url": config["legitimate_urls"][0], "action": "allowed", "threat_name": "", "category": "Patch Management"},
        {"user": users[1], "url": config["legitimate_urls"][1], "action": "allowed", "threat_name": "", "category": "Patch Management"},
        {"user": users[0], "url": config["fake_website_url"], "action": "allowed", "threat_name": "", "category": "Business"},
        {"user": users[1], "url": config["fake_website_url"], "action": "allowed", "threat_name": "", "category": "Business"}
    ]

    selected_narrative = random.choice(narratives)
    simulate_web_access(selected_narrative["user"], selected_narrative["url"])

    log = generate_log(
        selected_narrative["user"],
        selected_narrative["url"],
        selected_narrative["action"],
        selected_narrative["threat_name"],
        selected_narrative["category"],
        selected_narrative.get("additional_info")
    )
    logs.append(log)

    for log in logs:
        status, response = send_to_logscale(log, config)
        print(f"Sent log: {json.dumps(log, indent=4)}")
        print(f"Response: {status}, {response}")

    # Generate corresponding Windows Event logs
    generate_windows_event_logs()

if __name__ == "__main__":
    main()