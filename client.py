import requests
import time
import psutil
import json
import zipfile
import os
import subprocess
import sys

SERVER_URL = 'http://95.217.132.134:5000'  # Replace with your server address
DEVICE_ID_FILE = 'device_id.txt'  # File to store the device ID
DEVICE_NAME = 'MyDevice'
DEVICE_TYPE = 'laptop'
COMMANDS_CHECK_INTERVAL = 5  # In seconds

class DeviceClient:
    def __init__(self):
        self.device_id = self.load_device_id()  # Load device ID from file
        self.logging_enabled = True  # Flag to control logging
        self.device_location = self.get_device_location()  # Get device location

    def get_device_location(self):
        """Get device location based on conditions."""
        if self.device_id:
            return "MEOW" if not self.is_interactive() else None
        else:
            return input("Please enter the device location: ")

    def is_interactive(self):
        """Check if the script is running in an interactive environment."""
        return sys.stdin.isatty()

    def load_device_id(self):
        """Load device ID from a file."""
        if os.path.exists(DEVICE_ID_FILE):
            with open(DEVICE_ID_FILE, 'r') as file:
                return file.read().strip()
        return None

    def save_device_id(self, device_id):
        """Save device ID to a file."""
        with open(DEVICE_ID_FILE, 'w') as file:
            file.write(device_id)

    def register(self):
        """Register the device with the server."""
        if self.device_id:
            self.log(f'Device already registered with ID: {self.device_id}')
            return

        payload = {
            "name": DEVICE_NAME,
            "device_type": DEVICE_TYPE,
            "location": self.device_location  # Use the determined location
        }

        while True:
            try:
                response = requests.post(f'{SERVER_URL}/register', json=payload)
                if response.status_code == 200:
                    self.device_id = response.json()['device_id']
                    self.save_device_id(self.device_id)  # Save the device ID
                    self.log(f'Device registered successfully with ID: {self.device_id}')
                    break
                else:
                    self.log(f'Failed to register device: {response.text}')
                    break
            except requests.exceptions.ConnectionError:
                self.log("Server not reachable. Retrying in 5 seconds...")
                time.sleep(5)

    def log(self, message):
        """Log messages if logging is enabled."""
        if self.logging_enabled:
            print(message)

    def get_system_status(self):
        """Get current system status including CPU, RAM, and memory usage."""
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        memory_usage = psutil.disk_usage('/').percent

        return {
            "cpu_usage": f"{cpu_usage}%",
            "ram_usage": f"{ram_usage}%",
            "memory_usage": f"{memory_usage}%"
        }

    def report_status(self):
        """Report the current status to the server and check for commands."""
        if self.device_id is None:
            self.log("Device not registered. Cannot report status.")
            return

        status = self.get_system_status()

        payload = {
            "device_id": self.device_id,
            "status": "active",  # Change based on actual status
            "cpu_usage": status["cpu_usage"],
            "ram_usage": status["ram_usage"],
            "memory_usage": status["memory_usage"]
        }

        while True:
            try:
                response = requests.post(f'{SERVER_URL}/report_status', json=payload)
                if response.status_code == 200:
                    data = response.json()
                    commands = data.get('commands', [])
                    if commands:
                        for command in commands:
                            self.execute_command(command)
                    break
                else:
                    self.log(f"Failed to report status: {response.text}")
                    break
            except requests.exceptions.ConnectionError:
                self.log("Server not reachable. Retrying in 5 seconds...")
                time.sleep(5)

    def execute_command(self, command):
        """Execute a command received from the server."""
        self.log(f"Executing command: {command}")

        if command["command"] == "update":
            version = command.get("version", "latest")
            result = self.update(version)
        elif command["command"] == "/disableLogging":
            self.logging_enabled = False
            result = "Logging disabled."
            self.log(result)
        else:
            result = f"Unknown command: {command}"

        self.send_command_result(command, result)

    def update(self, version):
        """Download and apply the update from GitHub, then send status to server."""
        self.log(f"Starting update to version {version}...")
        try:
            # Download the update
            if version == "latest":
                url = 'https://github.com/botsarefuture/remote-client/archive/refs/heads/main.zip'
            else:
                url = f'https://github.com/botsarefuture/remote-client/archive/refs/tags/{version}.zip'

            response = requests.get(url)
            if response.status_code == 200:
                with open('update.zip', 'wb') as file:
                    file.write(response.content)
                self.log(f"Downloaded version {version}.")

                # Extract the update
                with zipfile.ZipFile('update.zip', 'r') as zip_ref:
                    zip_ref.extractall('update_folder')
                self.log(f"Extracted version {version}.")

                # Clean up zip file
                os.remove('update.zip')

                # Send success status to the server
                self.send_command_result({"action": "update"}, f"Updated to version {version} successfully.")
                
                # Restart the application
                self.restart_client()

            else:
                raise Exception(f"Failed to download version {version}: {response.status_code}")

        except Exception as e:
            self.log(f"Update failed: {e}")
            self.send_command_result({"action": "update"}, f"Update to version {version} failed. Error: {str(e)}")
            self.rollback_update()

    def send_command_result(self, command, result):
        """Send the result of the executed command back to the server."""
        payload = {
            "device_id": self.device_id,
            "command": command,
            "result": result
        }

        while True:
            try:
                response = requests.post(f'{SERVER_URL}/command_result', json=payload)
                if response.status_code == 200:
                    self.log(f"Command result sent successfully: {result}")
                    break
                else:
                    self.log(f"Failed to send command result: {response.text}")
                    break
            except requests.exceptions.ConnectionError:
                self.log("Server not reachable. Retrying in 5 seconds...")
                time.sleep(5)

    def restart_client(self):
        """Restart the client after updating."""
        self.log("Restarting client...")
        subprocess.call(['python3', __file__])  # Adjust if using a different Python version or environment

    def rollback_update(self):
        """Rollback the update if it fails."""
        self.log("Rolling back the update...")
        # Logic to revert back to the previous state or version

    def query(self):
        """Periodically query the server to check for commands."""
        while True:
            self.report_status()
            self.log("Waiting for next command check...")
            time.sleep(COMMANDS_CHECK_INTERVAL)

if __name__ == '__main__':
    client = DeviceClient()

    # Step 1: Register the device with the server
    client.register()

    # Step 2: Query the server every few seconds to report status and check for commands
    client.query()
