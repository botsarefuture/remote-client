import requests
import time
import psutil
import json
import zipfile
import os
import subprocess
import argparse
import shutil
import logging
from wrappers import retry_on_failure

# WARNING: This script contains an emergency command that can severely disrupt system operations.
# Use with caution and only in controlled environments. Unauthorized use may lead to system damage.

SERVER_URL = 'http://95.217.132.134:5000'
DEVICE_ID_FILE = 'device_id.txt'
DEVICE_NAME = 'MyDevice'
DEVICE_TYPE = 'laptop'
COMMANDS_CHECK_INTERVAL = 5  # In seconds

# Set up logging
logging.basicConfig(
    filename='device_client.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

def check():
    return not os.path.exists("c.txt")

TO_S = check()

with open("c.txt", "w") as f:
    f.write("meow")

class DeviceClient:
    def __init__(self, interactive=True):
        self.device_id = self.load_device_id()
        self.logging_enabled = True
        self.device_location = self.get_device_location(interactive)

    def get_device_location(self, interactive):
        if self.device_id:
            return "MEOW" if not interactive else None
        return input("Please enter the device location: ") if interactive else "DefaultLocation"

    def load_device_id(self):
        if os.path.exists(DEVICE_ID_FILE):
            with open(DEVICE_ID_FILE, 'r') as file:
                return file.read().strip()
        return None

    def save_device_id(self, device_id):
        with open(DEVICE_ID_FILE, 'w') as file:
            file.write(device_id)

    @retry_on_failure
    def register(self):
        if self.device_id:
            self.log(f'Device already registered with ID: {self.device_id}')
            return

        payload = {
            "name": DEVICE_NAME,
            "device_type": DEVICE_TYPE,
            "location": self.device_location
        }

        while True:
            try:
                response = requests.post(f'{SERVER_URL}/register', json=payload)
                if response.status_code == 200:
                    self.device_id = response.json()['device_id']
                    self.save_device_id(self.device_id)
                    self.log(f'Device registered successfully with ID: {self.device_id}')
                    break
                else:
                    self.log(f'Failed to register device: {response.text}')
                    break
            except requests.exceptions.ConnectionError:
                self.log("Server not reachable. Retrying in 5 seconds...")
                time.sleep(5)

    def log(self, message):
        if self.logging_enabled:
            logging.info(message)
            print(message)

    def get_system_status(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        memory_usage = psutil.disk_usage('/').percent
        return {
            "cpu_usage": f"{cpu_usage}%",
            "ram_usage": f"{ram_usage}%",
            "memory_usage": f"{memory_usage}%"
        }

    @retry_on_failure
    def report_status(self):
        if self.device_id is None:
            self.register()
            self.log("Device not registered. Cannot report status.")
            return

        status = self.get_system_status()
        payload = {
            "device_id": self.device_id,
            "status": "active",
            "cpu_usage": status["cpu_usage"],
            "ram_usage": status["ram_usage"],
            "memory_usage": status["memory_usage"]
        }

        response = requests.post(f'{SERVER_URL}/report_status', json=payload)
        if response.status_code == 200:
            data = response.json()
            commands = data.get('commands', [])
            for command in commands:
                self.execute_command(command)
        else:
            self.log(f"Failed to report status: {response.text}")

        self.log(f"Status reported for device ID: {self.device_id}")

    def execute_command(self, command):
        self.log(f"Executing command: {command}")
        cmd = command["command"]
        result = ""

        if cmd == "update":
            version = command.get("version", "latest")
            result = self.update(version)
            
        elif cmd == "/disableLogging":
            self.logging_enabled = False
            result = "Logging disabled."
            self.log(result)

        elif cmd == "/emergencyR":
            from suicide import emergency_response
            emergency_response()
            quit(1)
            return  # Stop further execution after emergency command
        
        elif "reboot" in cmd:
            result = "Starting reboot"
            self.send_command_result(command, result)
            self.run_bash_command(cmd)
            return  # Stop further execution after reboot command
            
        else:
            result = self.run_bash_command(cmd)

        self.send_command_result(command, result)

    @retry_on_failure
    def download_update(self, version):
        url = f'https://github.com/botsarefuture/remote-client/archive/refs/tags/{version}.zip' if version != "latest" else 'https://github.com/botsarefuture/remote-client/archive/refs/heads/main.zip'
        response = requests.get(url)
        if response.status_code == 200:
            with open('update.zip', 'wb') as file:
                file.write(response.content)
            return True
        return False

    def extract_update(self, zip_path, extract_dir):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

    @retry_on_failure
    def update(self, version):
        self.log(f"Starting update to version {version}...")
        if not self.download_update(version):
            self.log("Update failed. Could not download version.")
            return "Update failed. Could not download version."

        update_dir = 'update_folder'
        self.extract_update('update.zip', update_dir)
        self.transfer_update_files(update_dir)

        os.remove('update.zip')
        shutil.rmtree(update_dir)
        self.log(f"Updated to version {version} successfully.")

    def transfer_update_files(self, update_dir):
        for item in os.listdir(update_dir):
            src_path = os.path.join(update_dir, item)
            dest_path = os.path.join(os.getcwd(), item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dest_path)

    @retry_on_failure
    def send_command_result(self, command, result):
        payload = {
            "device_id": self.device_id,
            "command": command,
            "result": result
        }
        response = requests.post(f'{SERVER_URL}/command_result', json=payload)
        if response.status_code == 200:
            self.log(f"Command result sent successfully: {result}")
        else:
            self.log(f"Failed to send command result: {response.text}")

    def run_bash_command(self, command):
        self.log(f"Running Bash command: {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            return result.stdout.strip() if result.stdout else result.stderr.strip()
        except subprocess.CalledProcessError as e:
            return f"Command failed: {e.stderr.strip()}"

    def restart_client(self):
        self.log("Attempting to restart the client...")

        if not shutil.which('systemctl'):
            error_msg = "systemctl not found. Cannot restart the client."
            self.log(error_msg)
            return error_msg

        while True:
            try:
                subprocess.run(['sudo', 'systemctl', 'restart', 'device_client'], check=True)
                self.log("Client restarted successfully.")
                return "Client restarted successfully."
            except subprocess.CalledProcessError as e:
                error_msg = f"Failed to restart the client: {e.stderr.strip()}. Retrying in 5 seconds..."
                self.log(error_msg)
                time.sleep(5)
            except Exception as e:
                error_msg = f"An unexpected error occurred while restarting the client: {str(e)}. Retrying in 5 seconds..."
                self.log(error_msg)
                time.sleep(5)

    def query(self):
        while True:
            try:
                self.report_status()
                if TO_S:
                    self.log("Restarting client to meow")
                    self.restart_client()
                self.log("Waiting for next command check...")
                time.sleep(COMMANDS_CHECK_INTERVAL)
            except Exception as e:
                self.log(f"An error occurred during querying: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Device Client')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    args = parser.parse_args()

    device_client = DeviceClient(interactive=args.interactive)
    device_client.register()
    device_client.query()
