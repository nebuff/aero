import os
import sys
import shutil
import urllib.request
import importlib.util
import re

__PLUGIN_VERSION__ = "1.2.1"

AERO_REPO_URL = "https://github.com/nebuff/aero.git"
AERO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_DIR = os.path.join(AERO_DIR, "plugins")
CONFIG_PATH = os.path.join(AERO_DIR, "config.json")
VERSIONS_DIR = os.path.join(AERO_DIR, "versions")
AERO_EXEC = os.path.join(AERO_DIR, "aero")
REPO_PLUGINS_URL = "https://raw.githubusercontent.com/nebuff/aero/main/plugins"

def get_current_version():
    try:
        with open(AERO_EXEC, "r") as f:
            for line in f:
                if "__AERO_VERSION__" in line:
                    return line.split("=")[1].strip().strip('"\'')
    except Exception:
        pass
    return None

def parse_version(ver):
    # Example: aero-stable-1.0.2 -> ('stable', [1,0,2])
    m = re.match(r"aero-(stable|beta|pre)-([\d\.]+)", ver)
    if not m:
        return None, []
    typ = m.group(1)
    nums = [int(x) for x in m.group(2).split(".")]
    return typ, nums

def compare_versions(a, b):
    # Returns 1 if a > b, -1 if a < b, 0 if equal
    for x, y in zip(a, b):
        if x > y:
            return 1
        if x < y:
            return -1
    if len(a) > len(b):
        return 1
    if len(a) < len(b):
        return -1
    return 0

def fetch_versions():
    import ssl
    import json as _json
    try:
        api_url = "https://api.github.com/repos/nebuff/aero/contents/versions"
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(api_url, context=context) as resp:
            data = resp.read().decode()
        files = _json.loads(data)
        return [f.get("name", "") for f in files if f.get("name", "").startswith("aero-")]
    except Exception:
        return []

def update_core(selected_version):
    import tempfile
    tmpdir = tempfile.mkdtemp()
    os.system(f"git clone {AERO_REPO_URL} {tmpdir} > /dev/null 2>&1")
    versions_path = os.path.join(tmpdir, "versions")
    src = os.path.join(versions_path, selected_version)
    dst = os.path.join(AERO_DIR, "aero")
    if not os.path.isfile(src):
        shutil.rmtree(tmpdir)
        return False, f"Version {selected_version} not found in repo."
    shutil.copy2(src, dst)
    os.chmod(dst, 0o755)
    shutil.rmtree(tmpdir)
    return True, f"Updated Aero core to {selected_version}"

def get_remote_plugin_version(plugin_name):
    import ssl
    url = f"{REPO_PLUGINS_URL}/{plugin_name}.py"
    try:
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=context) as resp:
            for line in resp:
                line = line.decode("utf-8")
                if "__PLUGIN_VERSION__" in line:
                    return line.split("=")[1].strip().strip('"\'')
    except Exception:
        pass
    return None

def get_local_plugin_version(filepath):
    try:
        with open(filepath, "r") as f:
            for line in f:
                if "__PLUGIN_VERSION__" in line:
                    return line.split("=")[1].strip().strip('"\'')
    except Exception:
        pass
    return None

def update_plugins():
    import ssl
    import json as _json
    updated = []
    try:
        api_url = "https://api.github.com/repos/nebuff/aero/contents/plugins"
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(api_url, context=context) as resp:
            data = resp.read().decode()
        files = _json.loads(data)
        for f in files:
            name = f.get("name", "")
            if name.endswith(".py"):
                plugin_name = name[:-3]
                local_path = os.path.join(PLUGINS_DIR, name)
                url = f"{REPO_PLUGINS_URL}/{name}"
                remote_ver = get_remote_plugin_version(plugin_name)
                local_ver = get_local_plugin_version(local_path) if os.path.isfile(local_path) else None
                # Update if plugin exists locally and remote version is newer or different
                if os.path.isfile(local_path):
                    if remote_ver is not None and local_ver != remote_ver:
                        with urllib.request.urlopen(url, context=context) as response, open(local_path, "wb") as out_file:
                            out_file.write(response.read())
                        updated.append(f"{plugin_name} ({local_ver} → {remote_ver})")
    except Exception as e:
        return False, f"Plugin update failed: {e}"
    return True, updated

def updater_command(args):
    print("\033[33mAero Updater\033[0m")
    current_version = get_current_version()
    if not current_version:
        print("\033[31mCould not detect current Aero version.\033[0m")
        return
    print(f"Current Aero version: \033[36m{current_version}\033[0m")
    cur_type, cur_nums = parse_version(current_version)
    if not cur_type:
        print("\033[31mCould not parse current Aero version.\033[0m")
        return

    all_versions = fetch_versions()
    filtered = []
    for v in all_versions:
        typ, nums = parse_version(v)
        if typ == cur_type and compare_versions(nums, cur_nums) == 1:
            filtered.append((nums, v))
    filtered.sort()
    if not filtered:
        print(f"\033[32mNo newer {cur_type} versions available. You are up to date!\033[0m")
        # Still update plugins even if core is up to date
        print("Checking for plugin updates...")
        ok, updated = update_plugins()
        if ok:
            if updated:
                print(f"\033[32mUpdated plugins: {', '.join(updated)}\033[0m")
            else:
                print("\033[33mNo plugins needed updating.\033[0m")
        else:
            print(f"\033[31m{updated}\033[0m")
        print("\n\033[32mUpdate Complete, Reopen Aero!\033[0m")
        sys.exit(0)

    print(f"Available newer {cur_type} versions:")
    for i, (nums, v) in enumerate(filtered, 1):
        print(f"  {i}. {v}")
    print()
    print(f"Press Enter to update to the latest {cur_type} version ({filtered[-1][1]}), or type a number to pick a version.")
    sel = input("Version to update to (default latest): ").strip()
    if sel == "":
        selected_version = filtered[-1][1]
    else:
        try:
            idx = int(sel) - 1
            selected_version = filtered[idx][1]
        except Exception:
            print("\033[31mInvalid selection.\033[0m")
            return

    confirm = input(f"Do you want to update Aero to {selected_version} and update all plugins? (y/n): ").strip().lower()
    if confirm != "y":
        print("Update cancelled.")
        return

    print(f"Updating Aero core to {selected_version}...")
    ok, msg = update_core(selected_version)
    if ok:
        print(f"\033[32m{msg}\033[0m")
    else:
        print(f"\033[31m{msg}\033[0m")
    print("Updating plugins...")
    ok, updated = update_plugins()
    if ok:
        if updated:
            print(f"\033[32mUpdated plugins: {', '.join(updated)}\033[0m")
        else:
            print("\033[33mNo plugins needed updating.\033[0m")
    else:
        print(f"\033[31m{updated}\033[0m")
    print("\n\033[32mUpdate Complete, Reopen Aero!\033[0m")
    sys.exit(0)

def register(COMMANDS):
    COMMANDS["update"] = updater_command
