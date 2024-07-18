# NGSIEM Log Generator

NGSIEM Log Generator is a tool designed to generate and manage log messages for Zscaler and Syslog. This tool allows you to generate sample logs, batch logs, and set up cron jobs for automated log generation. Additionally, it provides options to start, stop, and check the status of a LogScale log collector.

## Features

- **Generate Sample Logs**: Generate sample Zscaler and Syslog logs to understand their format.
- **Batch Log Generation**: Generate a batch of logs and save them to a specified log folder.
- **Automated Log Generation**: Set up cron jobs to automate log generation at specified intervals.
- **LogScale Log Collector Management**: Start, stop, and check the status of the LogScale log collector service.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cyberjack256/NGSIEM-Log-Generator.git cd NGSIEM-Log-Generator
```
2. Install the required dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

2. Run the menu script to access the main menu:
```bash
python3 menu.py
```

### Main Menu Options

1. **Zscaler Log Actions**
2. **Syslog Log Actions**
3. **Exit**

### Zscaler Log Actions

1. **Show current configuration**: Display the current configuration settings.
2. **Add a configuration value**: Add values to specific fields in the configuration.
3. **Clear a configuration value**: Clear values from specific fields in the configuration.
4. **Generate sample Zscaler logs**: Generate and display sample Zscaler logs.
5. **Send logs to NGSIEM**: Send generated logs to the NGSIEM.
6. **Set cron job for Zscaler logs**: Set up a cron job to automate Zscaler log generation.
7. **Delete cron job for Zscaler logs**: Delete the existing cron job for Zscaler logs.
8. **Back to main menu**: Return to the main menu.

### Syslog Log Actions

1. **Show current configuration**: Display the current configuration settings.
2. **Generate sample Syslog logs**: Generate and display sample Syslog logs.
3. **Generate batch of Syslog logs to log folder**: Generate a batch of Syslog logs and save them to the log folder.
4. **Set cron job for Syslogs**: Set up a cron job to automate Syslog generation.
5. **Delete cron job for Syslogs**: Delete the existing cron job for Syslogs.
6. **Start LogScale log collector**: Start the LogScale log collector service.
7. **Stop LogScale log collector**: Stop the LogScale log collector service.
8. **Status of LogScale log collector**: Check the status of the LogScale log collector service.
9. **Back to main menu**: Return to the main menu.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.