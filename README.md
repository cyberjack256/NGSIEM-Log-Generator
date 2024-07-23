# NGSIEM Log Generator

The NGSIEM Log Generator is a versatile tool designed for cybersecurity professionals to generate and manage log messages for Zscaler and Syslog. It allows for the creation of realistic log data, configuration of automated log generation, and management of LogScale log collectors.

## Features

- **Generate Sample Logs**: Create sample Zscaler and Syslog logs to understand their structure and format.
- **Batch Log Generation**: Generate and save a batch of logs to a specified folder.
- **Automated Log Generation**: Set up cron jobs to automate the generation of logs at regular intervals.
- **LogScale Log Collector Management**: Start, stop, and check the status of the LogScale log collector service.
- **Dynamic Log Levels**: Configure and generate logs with different severity levels (info, warning, error) based on your needs.

## Installation

1. Clone the repository:
```bash
    git clone https://github.com/cyberjack256/NGSIEM-Log-Generator.git
    cd NGSIEM-Log-Generator
```
3. Install the required dependencies:
 ```bash
    pip3 install -r requirements.txt
```
## Usage

Run the menu script to access the main menu:
```bash
    python3 menu.py
```
### Main Menu Options

1. **Zscaler Log Actions**
2. **Syslog Log Actions**
3. **Edit LogScale Configuration**
4. **Exit**

### Zscaler Log Actions

1. **Show current configuration**: Display the current configuration settings.
2. **Add a configuration value**: Add values to specific fields in the configuration.
3. **Clear a configuration value**: Clear values from specific fields in the configuration.
4. **Generate sample Zscaler logs**: Generate and display sample Zscaler logs.
5. **Send logs to NGSIEM**: Send generated logs to the NGSIEM.
6. **Set cron job for Zscaler logs**: Set up a cron job to automate Zscaler log generation.
7. **Delete cron job for Zscaler logs**: Delete the existing cron job for Zscaler logs.
8. **View last execution time of Zscaler cron job**: Check the last execution time of the Zscaler cron job.
9. **Back to main menu**: Return to the main menu.

### Syslog Log Actions

1. **Show current configuration**: Display the current configuration settings.
2. **Generate sample Syslog logs**: Generate and display sample Syslog logs.
3. **Generate batch of Syslog logs to log folder**: Generate a batch of Syslog logs and save them to the log folder.
4. **Set cron job for Syslogs**: Set up a cron job to automate Syslog generation.
5. **Delete cron job for Syslogs**: Delete the existing cron job for Syslogs.
6. **View last execution time of Syslog cron job**: Check the last execution time of the Syslog cron job.
7. **Start LogScale log collector**: Start the LogScale log collector service.
8. **Stop LogScale log collector**: Stop the LogScale log collector service.
9. **Status of LogScale log collector**: Check the status of the LogScale log collector service.
10. **Set Syslog log levels**: Configure log levels (info, warning, error) for Syslog generation.
11. **Back to main menu**: Return to the main menu.

### Edit LogScale Configuration

1. **Edit LogScale configuration file**: Use nano to edit the LogScale configuration file stored in /etc/humio-logcollector/config.yaml.

## Configuration

The `config.json` file is used to store configuration settings. Update this file with your specific settings for API URLs, API keys, users, and other relevant data. Here is an example:
```json
{
  "zscaler_api_url": "https://your-ngsiem-api-url",
  "zscaler_api_key": "your_api_key",
  "observer_id": "your_observer_id",
  "domains": ["birdsite.com", "adminbird.com", "birdnet.org"],
  "users": [
    {
      "username": "robin",
      "email": "robin@birdsite.com",
      "hostname": "workstation.birdsite.com",
      "mac_address": "00:1A:2B:3C:4D:5E",
      "client_ip": "10.0.0.1",
      "user_agent": "Mozilla/5.0"
    },
    {
      "username": "sparrow",
      "email": "sparrow@birdsite.com",
      "hostname": "workstation2.birdsite.com",
      "mac_address": "11:22:33:44:55:66",
      "client_ip": "10.0.0.2",
      "user_agent": "Chrome/91.0"
    },
    {
      "username": "eagle",
      "email": "eagle@adminbird.com",
      "hostname": "adminworkstation.adminbird.com",
      "mac_address": "22:33:44:55:66:77",
      "client_ip": "10.0.0.3",
      "user_agent": "Mozilla/5.0"
    }
  ],
  "server_ips": ["192.168.1.1", "192.168.1.2"],
  "log_levels": ["info", "warning", "error"]
}
```
## Contributing

We welcome contributions! Please fork the repository and submit your pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
