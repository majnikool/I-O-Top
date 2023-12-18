# README for I/O Top Monitoring Script

## Overview
This script provides a solution for monitoring high I/O (Input/Output) processes on a Linux system. It leverages `iotop`, a command-line utility that displays I/O usage information per process. The script captures and logs processes exceeding specified I/O thresholds within a defined time window.

## Features
- **Time Window Monitoring**: Runs I/O monitoring within a specified start and end time window.
- **I/O Thresholds**: Captures processes exceeding set thresholds for read and write I/O.
- **Detailed Logging**: Logs include timestamps, I/O statistics, and process details.
- **Parent Process Identification**: Extracts and logs details of parent processes for high I/O processes.
- **Continuous Monitoring**: Repeatedly checks the time window and performs monitoring accordingly.
- **Graceful Termination**: Handles SIGINT for safe and clean script termination.

## Requirements
- Python 3.x
- `iotop` installed on the system (`sudo apt-get install iotop` for Ubuntu/Debian)
- Administrative or root privileges (to run `iotop` and access process details)

## Installation
1. Ensure Python 3.x is installed on your system.
2. Install `iotop` if not already available.
3. Copy the script to a desired location on your system.

## Usage
Run the script with Python 3, specifying the start minute, end minute, I/O read threshold, and I/O write threshold as arguments. Use the 24-hour format for specifying minutes.

**Example Command**:
```
python3 io-top4.py <start_minute> <end_minute> <io_threshold_read> <io_threshold_write>
```

- `start_minute` and `end_minute`: Integer values between 0 and 59, representing the minute of the hour when monitoring starts and ends, respectively.
- `io_threshold_read` and `io_threshold_write`: Float values representing the I/O thresholds for read and write operations in kilobytes per second (K/s).

**Sample Execution**:
```
python3 io-top4.py 32 35 1000.0 1000.0
```
This command starts monitoring at the 32nd minute of the hour and ends at the 35th minute, with I/O read and write thresholds set at 1000 K/s.

## Output
The script logs the monitoring output to `/root/iotop_monitoring.log`. It includes detailed information about processes exceeding the specified I/O thresholds, along with their parent processes.

## Note
- The script requires administrative privileges to access certain system details and run `iotop`.
- The time window is checked every minute, and the script runs continuously until manually terminated.

## Author
Majid Nik