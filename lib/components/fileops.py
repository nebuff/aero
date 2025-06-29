__COMPONENT_VERSION__ = "1.0.0"
__COMPONENT_NAME__ = "fileops"
__COMPONENT_DESCRIPTION__ = "File operations - cp, mv, rm, mkdir, etc."

import os
import shutil
import glob
import sys

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_CYAN = "\033[36m"

def cp_cmd(args):
    """Copy files or directories"""
    if not args or len(args) < 2 or args[0] == "help":
        print(f"{COLOR_YELLOW}Copy Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}cp source dest{COLOR_RESET}        - Copy file")
        print(f"  {COLOR_GREEN}cp -r source dest{COLOR_RESET}     - Copy directory recursively")
        print(f"  {COLOR_GREEN}cp file1 file2 dir{COLOR_RESET}    - Copy multiple files to directory")
        return
    
    recursive = False
    if args[0] == "-r":
        recursive = True
        args = args[1:]
        if len(args) < 2:
            print(f"{COLOR_RED}cp: missing destination{COLOR_RESET}")
            return
    
    try:
        if len(args) == 2:
            src, dest = args
            if os.path.isdir(src) and recursive:
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
            print(f"{COLOR_GREEN}Copied {src} to {dest}{COLOR_RESET}")
        else:
            # Multiple sources to directory
            dest = args[-1]
            sources = args[:-1]
            if not os.path.isdir(dest):
                print(f"{COLOR_RED}cp: destination must be a directory for multiple sources{COLOR_RESET}")
                return
            for src in sources:
                if os.path.isdir(src) and recursive:
                    shutil.copytree(src, os.path.join(dest, os.path.basename(src)))
                else:
                    shutil.copy2(src, dest)
                print(f"{COLOR_GREEN}Copied {src} to {dest}{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}cp: {e}{COLOR_RESET}")

def mv_cmd(args):
    """Move/rename files or directories"""
    if not args or len(args) < 2 or args[0] == "help":
        print(f"{COLOR_YELLOW}Move Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}mv source dest{COLOR_RESET}        - Move/rename file or directory")
        print(f"  {COLOR_GREEN}mv file1 file2 dir{COLOR_RESET}    - Move multiple files to directory")
        return
    
    try:
        if len(args) == 2:
            src, dest = args
            shutil.move(src, dest)
            print(f"{COLOR_GREEN}Moved {src} to {dest}{COLOR_RESET}")
        else:
            dest = args[-1]
            sources = args[:-1]
            if not os.path.isdir(dest):
                print(f"{COLOR_RED}mv: destination must be a directory for multiple sources{COLOR_RESET}")
                return
            for src in sources:
                shutil.move(src, dest)
                print(f"{COLOR_GREEN}Moved {src} to {dest}{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}mv: {e}{COLOR_RESET}")

def rm_cmd(args):
    """Remove files or directories"""
    if not args or args[0] == "help":
        print(f"{COLOR_YELLOW}Remove Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}rm file{COLOR_RESET}               - Remove file")
        print(f"  {COLOR_GREEN}rm -r dir{COLOR_RESET}             - Remove directory recursively")
        print(f"  {COLOR_GREEN}rm -f file{COLOR_RESET}            - Force remove (ignore errors)")
        return
    
    recursive = False
    force = False
    files = []
    
    for arg in args:
        if arg == "-r":
            recursive = True
        elif arg == "-f":
            force = True
        elif arg == "-rf" or arg == "-fr":
            recursive = True
            force = True
        else:
            files.append(arg)
    
    if not files:
        print(f"{COLOR_RED}rm: no files specified{COLOR_RESET}")
        return
    
    for file in files:
        try:
            if os.path.isdir(file):
                if recursive:
                    shutil.rmtree(file)
                    print(f"{COLOR_GREEN}Removed directory {file}{COLOR_RESET}")
                else:
                    print(f"{COLOR_RED}rm: {file} is a directory (use -r){COLOR_RESET}")
            else:
                os.remove(file)
                print(f"{COLOR_GREEN}Removed {file}{COLOR_RESET}")
        except Exception as e:
            if not force:
                print(f"{COLOR_RED}rm: {e}{COLOR_RESET}")

def mkdir_cmd(args):
    """Create directories"""
    if not args or args[0] == "help":
        print(f"{COLOR_YELLOW}Mkdir Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}mkdir dir{COLOR_RESET}             - Create directory")
        print(f"  {COLOR_GREEN}mkdir -p path/to/dir{COLOR_RESET}  - Create parent directories as needed")
        return
    
    parents = False
    dirs = []
    
    for arg in args:
        if arg == "-p":
            parents = True
        else:
            dirs.append(arg)
    
    for dir_path in dirs:
        try:
            if parents:
                os.makedirs(dir_path, exist_ok=True)
            else:
                os.mkdir(dir_path)
            print(f"{COLOR_GREEN}Created directory {dir_path}{COLOR_RESET}")
        except Exception as e:
            print(f"{COLOR_RED}mkdir: {e}{COLOR_RESET}")

def register(commands):
    commands['cp'] = cp_cmd
    commands['mv'] = mv_cmd
    commands['rm'] = rm_cmd
    commands['mkdir'] = mkdir_cmd
