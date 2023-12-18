import argparse
import subprocess
import time
import re
import signal
from datetime import datetime

def log(message, file=None):
    """ Helper function to log messages with timestamp and flush output. """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = f"{timestamp} - {message}\n"
    print(output, end='', flush=True)  # Flush output to ensure real-time logging
    if file:
        file.write(output)
        file.flush()  # Flush file output as well

def get_process_details(pid, file=None):
    """ Function to get specific details of a process given its PID with error handling. """
    try:
        fields = "user,pid,ppid,%cpu,%mem,cmd"
        result = subprocess.run(["ps", "-p", str(pid), "-o", fields], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.stderr:
            log(f"Warning: Error getting process details for PID {pid}: {result.stderr.strip()}", file)
            return None
        return result.stdout.strip()
    except Exception as e:
        log(f"Warning: Exception while getting process details for PID {pid}: {e}", file)
        return None

def run_iotop(duration, output_file, io_threshold_read, io_threshold_write):
    """ Function to run iotop, log the output, and parse for high I/O processes """
    logged_pids = set()  # Track logged PIDs to avoid duplicates
    last_log_time = {}  # Dictionary to track last log time of processes

    log(f"Running iotop for {duration} seconds")
    with open(output_file, "a") as file:
        file.write(f"\nStarting I/O monitoring at {datetime.now()}\n")
        with subprocess.Popen(["timeout", str(duration), "iotop", "-botqqk", "-d", "1", "-P"], stdout=subprocess.PIPE, universal_newlines=True) as proc:
            for line in proc.stdout:
                if "Total DISK READ" in line or "Actual DISK READ" in line:
                    log(f"\n{'=' * 40}\nIotop Summary: {line.strip()}\n{'=' * 40}\n", file)

                # Original regular expression for parsing process details
                match = re.search(r'(\d+) be/\d+ .+?(\d+\.\d+ K/s)\s+(\d+\.\d+ K/s) (.+)', line)
                if match:
                    pid, read, write, command = match.groups()
                    read_value = float(read.split()[0])
                    write_value = float(write.split()[0])

                    if read_value > io_threshold_read or write_value > io_threshold_write:
                        log(f"\nHigh I/O Process Detected: PID {pid}, Read {read}, Write {write}, Command: {command}\n", file)
                        process_details = get_process_details(pid, file)
                        log(f"Process Details (ps):\n{process_details}\n{'-' * 40}\n", file)

                        # Extract and log parent process details
                        process_detail_lines = process_details.split('\n')
                        if len(process_detail_lines) > 1:
                            parent_pid = process_detail_lines[1].split()[2]  # Extract PPID from the second line
                            parent_process_details = get_process_details(parent_pid, file)
                            log(f"Parent Process Details (ps):\n{parent_process_details}\n{'=' * 40}\n", file)
                        else:
                            log("Unable to extract parent process details.\n", file)
                else:
                    # Optionally handle or log lines without a matching PID
                    pass

        file.write(f"\nI/O monitoring ended at {datetime.now()}\n")
    log("Iotop monitoring finished\n")


def main(start_minute, end_minute, io_threshold_read, io_threshold_write):
    OUTPUT_FILE = "/root/iotop_monitoring.log"
    log("I/O monitoring script started. Continuously running.\n")

    while True:
        current_minute = datetime.now().minute
        log(f"Current time check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Current minute: {current_minute}\n")

        if start_minute <= current_minute < end_minute:
            duration = (end_minute - start_minute) * 60
            log(f"Within specified time window ({start_minute}-{end_minute}). Starting I/O monitoring.\n")
            run_iotop(duration, OUTPUT_FILE, io_threshold_read, io_threshold_write)
            log("Completed I/O monitoring for this window.\n")
        else:
            log(f"Outside specified time window ({start_minute}-{end_minute}).\n")

        time.sleep(1)  # Wait for a minute before checking again

def validate_args(args):
    """ Validate command-line arguments """
    if args.end_minute <= args.start_minute:
        print("Error: End minute must be greater than start minute.")
        exit(1)
    if args.io_threshold_read < 0 or args.io_threshold_write < 0:
        print("Error: I/O thresholds must be positive.")
        exit(1)

def graceful_exit(signal_received, frame):
    """ Handle SIGINT (Ctrl+C) for graceful termination """
    log("Script terminated by user. Exiting gracefully.")
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, graceful_exit)  # Setup signal handler

    parser = argparse.ArgumentParser(description="I/O Monitoring Script")
    parser.add_argument("start_minute", type=int, help="Minute of the hour when monitoring starts (0-59)")
    parser.add_argument("end_minute", type=int, help="Minute of the hour when monitoring ends (0-59)")
    parser.add_argument("io_threshold_read", type=float, help="I/O read threshold in K/s")
    parser.add_argument("io_threshold_write", type=float, help="I/O write threshold in K/s")

    args = parser.parse_args()
    validate_args(args)

    main(args.start_minute, args.end_minute, args.io_threshold_read, args.io_threshold_write)