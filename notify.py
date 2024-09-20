import subprocess
import gi
import os
import sys

# Method 1: Using notify-send
def notify_send_notification(message):
    command = f'notify-send "Emergency Alert" "{message}"'
    subprocess.run(command, shell=True)

# Method 2: Using GObject Introspection (gi)
def gi_notification(message):
    gi.require_version("Notify", "0.7")
    from gi.repository import Notify

    Notify.init("Emergency Alert")
    notification = Notify.Notification.new("Emergency Alert", message)
    notification.show()

# Method 3: Using zenity
def zenity_notification(message):
    subprocess.run(["zenity", "--info", "--text", message])

# Method 4: Using kdialog (for KDE users)
def kdialog_notification(message):
    subprocess.run(["kdialog", "--msgbox", message])

# Method 5: Using os module with shell commands
def os_system_notification(message):
    os.system(f'notify-send "Emergency Alert" "{message}"')

# Function to remove the script file
def remove_script_file():
    script_path = os.path.abspath(__file__)
    try:
        os.remove(script_path)
        print(f"Removed script file: {script_path}")
    except Exception as e:
        print(f"Failed to remove script file: {str(e)}")

# Example usage
def send_all_notifications(message):
    notify_send_notification(message)
    gi_notification(message)
    zenity_notification(message)
    kdialog_notification(message)  # This will only work if you're using KDE
    os_system_notification(message)
    remove_script_file()


# Call the function with your message
if __name__ == "__main__":
    notification_message = "Emergency procedures initiated. Please follow safety protocols."
    send_all_notifications(notification_message)
