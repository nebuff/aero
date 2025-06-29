__COMPONENT_VERSION__ = "1.0.0"
__COMPONENT_NAME__ = "ssh"
__COMPONENT_DESCRIPTION__ = "SSH client for remote connections"

import os
import subprocess
import sys

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_CYAN = "\033[36m"

def ssh_cmd(args):
    """SSH client command"""
    if not args or args[0] == "help":
        print(f"{COLOR_YELLOW}SSH Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}ssh user@host{COLOR_RESET}              - Connect to remote host")
        print(f"  {COLOR_GREEN}ssh user@host command{COLOR_RESET}      - Execute command on remote host")
        print(f"  {COLOR_GREEN}ssh -p port user@host{COLOR_RESET}      - Connect with custom port")
        print(f"  {COLOR_GREEN}ssh -i keyfile user@host{COLOR_RESET}   - Connect with private key")
        print(f"  {COLOR_GREEN}ssh help{COLOR_RESET}                   - Show this help")
        return
    
    # Check if ssh is available
    if not subprocess.run(['which', 'ssh'], capture_output=True).returncode == 0:
        print(f"{COLOR_RED}ssh: SSH client not found. Please install OpenSSH client.{COLOR_RESET}")
        return
    
    try:
        print(f"{COLOR_CYAN}Connecting via SSH...{COLOR_RESET}")
        cmd = ['ssh'] + args
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(f"\n{COLOR_YELLOW}SSH connection interrupted{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}ssh: Error: {e}{COLOR_RESET}")

def scp_cmd(args):
    """SCP file transfer command"""
    if not args or args[0] == "help":
        print(f"{COLOR_YELLOW}SCP Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}scp file user@host:/path{COLOR_RESET}     - Copy file to remote")
        print(f"  {COLOR_GREEN}scp user@host:/path file{COLOR_RESET}     - Copy file from remote")
        print(f"  {COLOR_GREEN}scp -r dir user@host:/path{COLOR_RESET}   - Copy directory recursively")
        print(f"  {COLOR_GREEN}scp help{COLOR_RESET}                     - Show this help")
        return
    
    if not subprocess.run(['which', 'scp'], capture_output=True).returncode == 0:
        print(f"{COLOR_RED}scp: SCP client not found. Please install OpenSSH client.{COLOR_RESET}")
        return
    
    try:
        print(f"{COLOR_CYAN}Transferring files via SCP...{COLOR_RESET}")
        cmd = ['scp'] + args
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print(f"{COLOR_GREEN}Transfer completed successfully{COLOR_RESET}")
    except KeyboardInterrupt:
        print(f"\n{COLOR_YELLOW}Transfer interrupted{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}scp: Error: {e}{COLOR_RESET}")

def register(commands):
    commands['ssh'] = ssh_cmd
    commands['scp'] = scp_cmd
