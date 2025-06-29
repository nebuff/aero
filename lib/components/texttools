__COMPONENT_VERSION__ = "1.0.0"
__COMPONENT_NAME__ = "texttools"
__COMPONENT_DESCRIPTION__ = "Text processing tools - cat, grep, head, tail, etc."

import os
import re
import sys

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_CYAN = "\033[36m"

def cat_cmd(args):
    """Display file contents"""
    if not args or args[0] == "help":
        print(f"{COLOR_YELLOW}Cat Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}cat file{COLOR_RESET}              - Display file contents")
        print(f"  {COLOR_GREEN}cat file1 file2{COLOR_RESET}       - Display multiple files")
        print(f"  {COLOR_GREEN}cat -n file{COLOR_RESET}           - Display with line numbers")
        return
    
    show_numbers = False
    files = []
    
    for arg in args:
        if arg == "-n":
            show_numbers = True
        else:
            files.append(arg)
    
    for file in files:
        try:
            with open(file, 'r') as f:
                if show_numbers:
                    for i, line in enumerate(f, 1):
                        print(f"{i:6d}  {line}", end='')
                else:
                    print(f.read(), end='')
        except Exception as e:
            print(f"{COLOR_RED}cat: {file}: {e}{COLOR_RESET}")

def grep_cmd(args):
    """Search text patterns in files"""
    if not args or args[0] == "help":
        print(f"{COLOR_YELLOW}Grep Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}grep pattern file{COLOR_RESET}     - Search pattern in file")
        print(f"  {COLOR_GREEN}grep -i pattern file{COLOR_RESET}  - Case insensitive search")
        print(f"  {COLOR_GREEN}grep -n pattern file{COLOR_RESET}  - Show line numbers")
        print(f"  {COLOR_GREEN}grep -r pattern dir{COLOR_RESET}   - Recursive search in directory")
        return
    
    case_insensitive = False
    show_numbers = False
    recursive = False
    pattern = None
    files = []
    
    i = 0
    while i < len(args):
        if args[i] == "-i":
            case_insensitive = True
        elif args[i] == "-n":
            show_numbers = True
        elif args[i] == "-r":
            recursive = True
        elif pattern is None:
            pattern = args[i]
        else:
            files.append(args[i])
        i += 1
    
    if not pattern:
        print(f"{COLOR_RED}grep: no pattern specified{COLOR_RESET}")
        return
    
    if not files:
        print(f"{COLOR_RED}grep: no files specified{COLOR_RESET}")
        return
    
    flags = re.IGNORECASE if case_insensitive else 0
    regex = re.compile(pattern, flags)
    
    def search_file(file_path, filename_for_display):
        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if regex.search(line):
                        line = line.rstrip('\n')
                        if len(files) > 1 or recursive:
                            prefix = f"{COLOR_CYAN}{filename_for_display}{COLOR_RESET}:"
                        else:
                            prefix = ""
                        
                        if show_numbers:
                            prefix += f"{COLOR_GREEN}{line_num}{COLOR_RESET}:"
                        
                        # Highlight matches
                        highlighted = regex.sub(f"{COLOR_YELLOW}\\g<0>{COLOR_RESET}", line)
                        print(f"{prefix}{highlighted}")
        except Exception as e:
            print(f"{COLOR_RED}grep: {file_path}: {e}{COLOR_RESET}")
    
    for file in files:
        if recursive and os.path.isdir(file):
            for root, dirs, filenames in os.walk(file):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    search_file(file_path, file_path)
        else:
            search_file(file, file)

def head_cmd(args):
    """Display first lines of files"""
    if not args or args[0] == "help":
        print(f"{COLOR_YELLOW}Head Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}head file{COLOR_RESET}             - Show first 10 lines")
        print(f"  {COLOR_GREEN}head -n 20 file{COLOR_RESET}       - Show first 20 lines")
        return
    
    lines = 10
    files = []
    
    i = 0
    while i < len(args):
        if args[i] == "-n" and i + 1 < len(args):
            try:
                lines = int(args[i + 1])
                i += 2
            except ValueError:
                print(f"{COLOR_RED}head: invalid line count{COLOR_RESET}")
                return
        else:
            files.append(args[i])
            i += 1
    
    for file in files:
        try:
            if len(files) > 1:
                print(f"{COLOR_CYAN}==> {file} <=={COLOR_RESET}")
            
            with open(file, 'r') as f:
                for i, line in enumerate(f):
                    if i >= lines:
                        break
                    print(line, end='')
            
            if len(files) > 1:
                print()
                
        except Exception as e:
            print(f"{COLOR_RED}head: {file}: {e}{COLOR_RESET}")

def tail_cmd(args):
    """Display last lines of files"""
    if not args or args[0] == "help":
        print(f"{COLOR_YELLOW}Tail Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}tail file{COLOR_RESET}             - Show last 10 lines")
        print(f"  {COLOR_GREEN}tail -n 20 file{COLOR_RESET}       - Show last 20 lines")
        print(f"  {COLOR_GREEN}tail -f file{COLOR_RESET}          - Follow file (monitor changes)")
        return
    
    lines = 10
    follow = False
    files = []
    
    i = 0
    while i < len(args):
        if args[i] == "-n" and i + 1 < len(args):
            try:
                lines = int(args[i + 1])
                i += 2
            except ValueError:
                print(f"{COLOR_RED}tail: invalid line count{COLOR_RESET}")
                return
        elif args[i] == "-f":
            follow = True
            i += 1
        else:
            files.append(args[i])
            i += 1
    
    for file in files:
        try:
            if len(files) > 1:
                print(f"{COLOR_CYAN}==> {file} <=={COLOR_RESET}")
            
            with open(file, 'r') as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    print(line, end='')
            
            if follow:
                print(f"{COLOR_CYAN}Following {file} (Ctrl+C to stop)...{COLOR_RESET}")
                try:
                    import time
                    with open(file, 'r') as f:
                        f.seek(0, 2)  # Go to end
                        while True:
                            line = f.readline()
                            if line:
                                print(line, end='')
                            else:
                                time.sleep(0.1)
                except KeyboardInterrupt:
                    print(f"\n{COLOR_YELLOW}Stopped following {file}{COLOR_RESET}")
            
            if len(files) > 1:
                print()
                
        except Exception as e:
            print(f"{COLOR_RED}tail: {file}: {e}{COLOR_RESET}")

def register(commands):
    commands['cat'] = cat_cmd
    commands['grep'] = grep_cmd
    commands['head'] = head_cmd
    commands['tail'] = tail_cmd
