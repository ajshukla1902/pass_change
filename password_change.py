import os
import subprocess
import socket
import paramiko

# Function to read user input with a prompt
def read_user_input(prompt):
    return input(prompt).strip()

# Function to execute a command on the SSH connection
def execute_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.readlines()

# Function to add the RSA key to authorized_keys if not already present
def add_rsa_key_to_authorized_keys(ssh, rsa_token, authorized_keys_path):
    command = f'cat {rsa_token}'
    rsa_key = execute_command(ssh, command)
    rsa_key = ''.join(rsa_key).strip()
    
    command = f'cat {authorized_keys_path}'
    authorized_keys = execute_command(ssh, command)
    authorized_keys = ''.join(authorized_keys)

    if rsa_key not in authorized_keys:
        command = f'echo "{rsa_key}" >> {authorized_keys_path}'
        execute_command(ssh, command)

# Function to change password and optionally add RSA key to authorized_keys
def pass_change(host_name, user_name, old_pass_word, new_pass_word, keys):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to the host using SSH
        ssh.connect(host_name, username=user_name, password=old_pass_word)
    except paramiko.AuthenticationException:
        return f'Authentication failed for {host_name}'
    except socket.error:
        return f'{host_name} is not accessible'
    
    # Get the hostname of the server
    command = 'hostname'
    outlines = execute_command(ssh, command)
    resph = ''.join(outlines).strip()

    if old_pass_word != new_pass_word:
        # Change the password
        command = f'echo "{new_pass_word}\n{new_pass_word}" | passwd'
        execute_command(ssh, command)

        if keys.lower() == 'yes':
            # Add RSA key to authorized_keys if requested
            add_rsa_key_to_authorized_keys(ssh, '/root/.ssh/id_rsa.pub', '/root/.ssh/authorized_keys')
    
    ssh.close()
    return f'Password changed successfully for {host_name}'

def main():
    # Get user inputs
    user_name = read_user_input('Enter the username: ')
    old_pass_word = read_user_input('Enter the Password: ')
    new_pass_word = read_user_input('Enter the New Password: ')
    keys = read_user_input('Do you want to add all the users RSA key to authorized_keys (Yes/No): ')

    # Read hostnames from a file and loop through them
    with open("hostname.txt", "r") as f:
        for host_name in f:
            host_name = host_name.strip()
            # Call pass_change function for each hostname
            result = pass_change(host_name, user_name, old_pass_word, new_pass_word, keys)
            print(result)

if __name__ == "__main__":
    main()
