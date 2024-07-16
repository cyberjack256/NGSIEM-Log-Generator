# Zscaler and NGSIEM Log Generator

## Overview

Welcome to the Zscaler and NGSIEM Log Generator! This project is designed to help cybersecurity professionals simulate realistic web and security logs for testing and training purposes. By using this tool, you can generate detailed logs that mimic user activities, security events, and potential breaches, all tailored to fit within a Zscaler and NGSIEM environment.

## Features

- **Generate Realistic Logs**: Create web server logs, Zscaler logs, and more with customizable data inputs.
- **Simulate Security Events**: Craft detailed narratives with user activities and potential security breaches.
- **Easy Configuration**: Use simple configuration files to customize user agents, IP addresses, and more.
- **Seamless Integration**: Send logs directly to NGSIEM or other specified APIs with minimal setup.

## Getting Started

### Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.9** or later installed.
- Administrator access to the Zscaler console.
- Administrator access to the Falcon console for the respective CID.
- Valid API URL and key from your NGSIEM instance.

### Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/log-generator.git
    cd log-generator
    ```

2. **Install the Required Libraries**:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Customize your experience by editing the `config.json` file. Add new data sources, tweak parameters, and make the scripts work for your specific needs.

Here is an example of the `config.json` file:

```json
{
    "api_url": "https://your-ngsiem-api-url.com",
    "users": ["eagle", "hawk", "falcon"],
    "malicious_user": "hawk",
    "malware_name": "CatSpyware",
    "ips": ["192.168.1.10", "192.168.1.11", "192.168.1.12"],
    "user_agents": ["Mozilla/5.0", "Chrome/91.0"]
}
```

Usage

Run the scripts through the menu system. Just execute the menu.py script, and it will guide you through the various functionalities. No need to remember all the individual script names – let the menu do the work!

python3 menu.py

Menu Options

	1.	Show Current Configuration: Displays the existing configuration values.
	2.	Set Configuration Field: Allows you to input new values for specific configuration fields.
	3.	Generate Sample Logs: Executes the generate_logs.py script to produce sample logs.
	4.	Send Logs to NGSIEM API: Sends the generated logs to the specified NGSIEM API endpoint.
	5.	Exit: Gracefully exits the menu system.

Example Log Generation

You can generate a sample example log with the data that is currently fed into the system and send it to the NGSIEM API for testing.

Sample Configuration

Add the following settings to your config.json file:
```json
{
    "api_url": "https://your-ngsiem-api-url.com",
    "users": ["eagle", "hawk", "falcon"],
    "malicious_user": "hawk",
    "malware_name": "CatSpyware",
    "ips": ["192.168.1.10", "192.168.1.11", "192.168.1.12"],
    "user_agents": ["Mozilla/5.0", "Chrome/91.0"]
}
```

Generate Logs

To generate logs based on the above configuration, run:

python3 generate_logs.py

Send Logs to NGSIEM

After generating the logs, use the menu to send the logs to the NGSIEM API.

Contributing

Have ideas to make these scripts even better? Fork the repository, make your changes, and submit a pull request. We’d love to see your contributions!

License

This project is licensed under the Apache-2.0 License. See the LICENSE file for details.

Contact

Got questions or need support? Open an issue on this repository, and we’ll get back to you as soon as possible. You can also reach out via LinkedIn or email. For this project, GitHub issues are preferred.

Happy log generating! 🚀
