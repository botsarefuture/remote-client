Here's a comprehensive guide for setting up the `remote-client` with commands for both Linux and Windows.

---

## Remote Client Installation Guide

### Overview

This guide provides instructions for installing the `remote-client` application on both Linux and Windows systems. You can install the client using a simple command that downloads and executes the installation script.

### Prerequisites

- Ensure you have an active internet connection.
- Make sure you have the necessary permissions to run scripts.
- For Windows, ensure PowerShell is run as an administrator.

### Installation on Linux

1. **Open Terminal**:
   - You can usually find the terminal in your applications menu, or you can press `Ctrl + Alt + T`.

2. **Run the Installation Command**:
   Execute the following command in your terminal:

   ```bash
   bash <(wget -qO- https://gist.githubusercontent.com/botsarefuture/f9380380de0d0c06fd390801a2ace730/raw/install.sh)
   ```

   - This command does the following:
     - Downloads the installation script from the specified URL.
     - Executes it immediately.

3. **Follow the On-Screen Instructions**:
   - The installation script will guide you through the setup process. Follow any prompts to complete the installation.

### Installation on Windows

1. **Open PowerShell**:
   - Press `Win + X` and select **Windows PowerShell (Admin)** or **Windows Terminal (Admin)**.

2. **Run the Installation Command**:
   Copy and paste the following command into the PowerShell window:

   ```powershell
   Invoke-WebRequest -Uri "https://gist.githubusercontent.com/botsarefuture/f9380380de0d0c06fd390801a2ace730/raw/install.ps1" -OutFile "$HOME\install.ps1"; & "$HOME\install.ps1"
   ```

   - This command does the following:
     - Downloads the installation script to your home directory as `install.ps1`.
     - Executes the downloaded script.

3. **Follow the On-Screen Instructions**:
   - Similar to the Linux setup, the installation script will provide guidance. Follow the prompts to finish the setup.

### Post-Installation Steps

After installation, you may need to:

- Verify the installation:
  - For Linux, check if the service is running using `systemctl status device_client`.
  - For Windows, ensure the application is running as intended.

- Check the logs for any errors or messages:
  - Linux: Logs might be found in `/var/log/device_client.log`.
  - Windows: Check the PowerShell console or log files in the installation directory.

### Additional Notes

- **Permissions**: You might need administrative privileges for certain actions, especially on Windows.
- **Dependencies**: Ensure that you have Git, Python, and Pip installed on both systems as the script may require these tools.
- **Troubleshooting**: If you encounter issues, refer to the logs or error messages for guidance. You can also seek help in relevant forums or communities.

---

Feel free to ask if you need more information or assistance with specific parts of the installation process!