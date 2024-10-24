"""
TO DO:
-Theoretically, this would take a long time to complete, even with multithreading  
to make this tool viable, cloud  computing resources would need to be used to speed up the bruteforcing process  
-Add user input variables to determine length of unlock code and save time bruteforcing  
"""

import subprocess
import time
import itertools
import string
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Safe delay between attempts (to prevent lockout or rate-limiting)
INITIAL_DELAY = 1  # Start with a 1-second delay
MIN_DELAY = 0.001  # Absolute minimum delay to prevent bricking
DELAY_DECREMENT = 0.2  # Amount to decrease the delay each time
DEVICE_WAIT_TIME = 5  # Wait time between device checks
REBOOT_WAIT_TIME = 10  # Time to wait after rebooting into fastboot mode
MAX_THREADS = 5  # Max number of threads for brute-forcing

# Regular expression to detect 3 or more consecutive identical characters
consecutive_pattern = re.compile(r"(.)\1\1")

# Lock for thread-safe printing
print_lock = threading.Lock()

# Define a method to check if the device is available via ADB
def is_device_connected_via_adb():
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        if "device" in result.stdout and not "unauthorized" in result.stdout.lower():
            with print_lock:
                print("ADB: Device detected.")
            return True
        with print_lock:
            print("ADB: Device not detected or unauthorized.")
        return False
    except Exception as e:
        print(f"ADB Error: {e}")
        return False

# Define a method to check if the device is in fastboot mode
def is_device_connected_via_fastboot():
    try:
        result = subprocess.run(["fastboot", "devices"], capture_output=True, text=True)
        if result.stdout.strip():
            with print_lock:
                print("Fastboot: Device detected.")
            return True
        with print_lock:
            print("Fastboot: No device detected.")
        return False
    except Exception as e:
        print(f"Fastboot Error: {e}")
        return False

# Method to reboot the device into fastboot mode via ADB
def reboot_device_into_fastboot():
    try:
        subprocess.run(["adb", "reboot", "bootloader"], capture_output=True, text=True)
        with print_lock:
            print("Rebooting into fastboot mode...")
        time.sleep(REBOOT_WAIT_TIME)  # Wait longer for the device to enter fastboot mode
    except Exception as e:
        print(f"Error rebooting into fastboot: {e}")

# Method to send a password via fastboot (as a brute-force attempt)
def send_fastboot_password(password):
    try:
        result = subprocess.run(
            ["fastboot", "oem", f"unlock {password}"],
            capture_output=True,
            text=True
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        return stdout, stderr  # Return both output streams for analysis
    except Exception as e:
        print(f"Error sending password via fastboot: {e}")
        return None, None

# Method to check if a password has 3 or more consecutive identical characters
def has_consecutive_characters(password):
    return bool(consecutive_pattern.search(password))

# Brute-force password generator (numeric and alphanumeric)
def password_generator(max_length=6):
    characters = string.digits + string.ascii_lowercase  # alphanumeric brute-forcing
    for length in range(4, max_length + 1):  # Start with 4 digits, then increase
        for attempt in itertools.product(characters, repeat=length):
            password = ''.join(attempt)
            if not has_consecutive_characters(password):  # Skip passwords with 3+ consecutive chars
                yield password

# Task executed by each thread
def brute_force_password_task(password, delay_between_attempts):
    stdout, stderr = send_fastboot_password(password)

    with print_lock:
        if stdout:
            print(f"Fastboot stdout: {stdout}")
        if stderr:
            print(f"Fastboot stderr: {stderr}")

        # Handle specific error message for incorrect password
        if stderr and "unlock bootloader fail" in stderr.lower():
            print(f"Password incorrect: {password}")
        # Check for any indication of successful unlock
        elif stdout and "unlock successful" in stdout.lower():
            print(f"Password found: {password}")
            return True  # Signal to stop once the password is found

        time.sleep(delay_between_attempts)  # Rate limiting between attempts

    return False

# Main brute-force loop with multithreading
def brute_force(max_length=6):
    adb_rebooted = False  # Track if the device has been rebooted into fastboot from ADB
    delay_between_attempts = INITIAL_DELAY

    # Start the password brute-forcing
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_password = {}

        while True:
            # First, try ADB communication only if the device hasn't rebooted yet
            if not adb_rebooted and is_device_connected_via_adb():
                print("Device detected via ADB. Rebooting into fastboot mode.")
                reboot_device_into_fastboot()
                adb_rebooted = True  # Set flag to avoid repeated reboots

            # Once rebooted, check if the device is in fastboot mode
            elif adb_rebooted and is_device_connected_via_fastboot():
                print("Device detected in fastboot mode.")
                
                # Initial check: Send a dummy password to confirm communication works
                dummy_password = "0000"
                print(f"Trying initial password: {dummy_password}")
                stdout, stderr = send_fastboot_password(dummy_password)

                if stderr and "unlock bootloader fail" in stderr.lower():
                    print(f"Initial password attempt failed as expected. Fastboot communication is working.")
                elif stdout and "unlock successful" in stdout.lower():
                    print(f"Initial password unexpectedly succeeded. Bootloader might already be unlocked.")
                    return

                # Start submitting password brute-forcing tasks
                for password in password_generator(max_length):
                    future = executor.submit(brute_force_password_task, password, delay_between_attempts)
                    future_to_password[future] = password

                for future in as_completed(future_to_password):
                    if future.result():  # If a password is found, terminate early
                        print(f"Password {future_to_password[future]} is correct. Stopping brute-force attack.")
                        executor.shutdown(wait=False)  # Stop other threads immediately
                        return

                # Reduce delay incrementally after each attempt
                if delay_between_attempts > MIN_DELAY:
                    delay_between_attempts = max(MIN_DELAY, delay_between_attempts - DELAY_DECREMENT)

            elif not adb_rebooted:
                print("No device detected via ADB or Fastboot. Please connect the device.")
                time.sleep(DEVICE_WAIT_TIME)  # Retry every few seconds if no device is detected
            else:
                print("Waiting for fastboot mode to be detected...")
                time.sleep(DEVICE_WAIT_TIME)  # Wait for fastboot to show up after reboot

# Main function
if __name__ == "__main__":
    try:
        print("Starting brute-force tool...")
        brute_force(max_length=8)  # Try passwords up to 8 characters long (adjustable)
    except KeyboardInterrupt:
        print("\nBrute-force operation interrupted by user.")
