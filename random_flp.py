#!/usr/bin/env python3
"""
Random FLP Selector & Launcher
------------------------------
1. Scans project folders for FL Studio (.flp) files (ignoring backups by default).
2. Randomly selects a project folder.
3. If the selected folder contains multiple .flp files, picks the most recently modified one.
4. Opens either the .flp file in FL Studio OR opens the folder/file in macOS Finder based on options.
"""

import sys
import os
import glob
import random
import subprocess
import argparse
import datetime
import json
from collections import defaultdict

HISTORY_FILE = ".flp_history.json"

def load_history(target_dir):
    history_path = os.path.join(target_dir, HISTORY_FILE)
    if os.path.exists(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
        except Exception:
            pass
    return set()

def save_history(target_dir, history_set):
    history_path = os.path.join(target_dir, HISTORY_FILE)
    try:
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(sorted(list(history_set)), f, indent=2)
    except Exception as e:
        print(f"⚠️ Warning: Could not save history: {e}")

def reset_history(target_dir):
    history_path = os.path.join(target_dir, HISTORY_FILE)
    if os.path.exists(history_path):
        try:
            os.remove(history_path)
            print("🔄 History tracking has been reset. All projects are available again.")
        except Exception as e:
            print(f"⚠️ Warning: Could not reset history: {e}")
    else:
        print("ℹ️ History is already empty.")

def get_fl_studio_app():
    """Find installed FL Studio application versions in /Applications."""
    apps = glob.glob("/Applications/FL Studio*.app")
    if apps:
        apps.sort(reverse=True)
        return apps[0]
    return None

def find_flp_files_by_folder(root_dir, include_backups=False):
    """
    Returns a dict mapping folder_path -> list of flp_file_paths.
    Ignores backup directories and auto-saved files unless include_backups is True.
    """
    folder_map = defaultdict(list)
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        rel_path = os.path.relpath(dirpath, root_dir)
        path_parts = [p.lower() for p in rel_path.split(os.sep)]
        
        if not include_backups:
            if any(part in ['backup', 'backups', '.trash', '__macosx'] for part in path_parts):
                continue

        for filename in filenames:
            if filename.lower().endswith('.flp'):
                if not include_backups and any(kw in filename.lower() for kw in ['autosaved', 'overwritten', 'backup']):
                    continue
                full_path = os.path.join(dirpath, filename)
                folder_map[dirpath].append(full_path)

    return folder_map

def send_macos_notification(title, message):
    try:
        safe_msg = message.replace('"', '\\"')
        safe_title = title.replace('"', '\\"')
        script = f'display notification "{safe_msg}" with title "{safe_title}"'
        subprocess.run(["osascript", "-e", script], check=False)
    except Exception:
        pass

def copy_to_clipboard(text):
    """Attempt to copy text to system clipboard."""
    try:
        if sys.platform == "darwin":
            cmd = ["pbcopy"]
        elif sys.platform == "linux":
            cmd = ["xclip", "-selection", "clipboard"]
        else:
            cmd = ["clip"]
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        process.communicate(text.encode("utf-8"))
        return process.returncode == 0
    except Exception:
        return False

def open_in_finder(path, reveal_file=True):
    """Opens Finder targeting the folder or revealing the file."""
    if reveal_file and os.path.isfile(path):
        cmd = ["open", "-R", path]
    else:
        folder = path if os.path.isdir(path) else os.path.dirname(path)
        cmd = ["open", folder]
    
    subprocess.run(cmd)

def open_file_in_fl_studio(flp_path, app_override=None):
    fl_app = app_override or get_fl_studio_app()
    
    if fl_app:
        print(f"📱 Opening with: {os.path.basename(fl_app)}")
        cmd = ["open", "-a", fl_app, flp_path]
    else:
        print("📱 Opening with default FL Studio association...")
        cmd = ["open", flp_path]

    res = subprocess.run(cmd, capture_output=True, text=True)
    
    if res.returncode != 0 and fl_app:
        print("⚠️ Trying fallback launch with system default application...")
        res = subprocess.run(["open", flp_path], capture_output=True, text=True)

    if res.returncode != 0 and res.stderr:
        print(f"⚠️ Notice: {res.stderr.strip()}")
    else:
        print("✅ Command executed successfully!")

def main():
    parser = argparse.ArgumentParser(description="Pick a random FL Studio project folder and open the latest FLP inside.")
    parser.add_argument("directory", nargs="?", default=".", help="Path to folder containing projects (default: current directory)")
    parser.add_argument("-u", "--unique", "--no-repeat", action="store_true", dest="no_repeat",
                        help="Avoid choosing the same project again until all have been opened")
    parser.add_argument("--reset-history", action="store_true",
                        help="Reset the history of opened projects")
    parser.add_argument("-f", "--finder", action="store_true", help="Open project folder in macOS Finder instead of FL Studio")
    parser.add_argument("-r", "--reveal", action="store_true", help="Open Finder and select/highlight the .flp file")
    parser.add_argument("-l", "--list", action="store_true",
                        help="Print a list of project names (one per line)")
    parser.add_argument("-c", "--clip", action="store_true",
                        help="Copy the list of project names to the clipboard (use with -l)")
    parser.add_argument("--include-backups", action="store_true", help="Include files inside Backup folders")
    parser.add_argument("--app", help="Custom FL Studio application path or name")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    if args.directory == ".":
        target_dir = script_dir
    else:
        target_dir = os.path.abspath(args.directory)

    if not os.path.exists(target_dir):
        print(f"❌ Error: Directory '{target_dir}' does not exist.")
        sys.exit(1)

    if args.reset_history:
        reset_history(target_dir)
        sys.exit(0)

    if not args.list:
        print(f"🔍 Searching for project folders in:\n   {target_dir}\n")

    folder_map = find_flp_files_by_folder(target_dir, include_backups=args.include_backups)

    if not folder_map:
        if args.list:
            print("No project folders containing .flp files were found.", file=sys.stderr)
        else:
            print("⚠️ No project folders containing .flp files were found.")
        sys.exit(0)

    total_folders = len(folder_map)
    available_folders = list(folder_map.keys())

    if args.no_repeat:
        history = load_history(target_dir)
        # Check folders not yet opened
        unopened = [f for f in available_folders if os.path.abspath(f) not in history]
        if not unopened:
            if not args.list:
                print("🎉 All projects have been opened once! Cycling reset — starting a fresh round.\n")
            history = set()
            unopened = available_folders
        available_folders = unopened
        if not args.list:
            print(f"🎯 No-repeat mode active: {total_folders - len(available_folders) + 1} of {total_folders} project(s) this round.")

    if args.list:
        names = []
        for folder in sorted(available_folders):
            if folder == target_dir:
                for flp in sorted(folder_map[folder]):
                    names.append(os.path.splitext(os.path.basename(flp))[0])
            else:
                names.append(os.path.basename(folder))

        output = "\n".join(names)
        print(output)

        if args.clip:
            if copy_to_clipboard(output):
                print("\n📋 Copied to clipboard!", file=sys.stderr)
            else:
                print("\n⚠️ Could not copy to clipboard", file=sys.stderr)
        sys.exit(0)

    # Step 1: Pick a random project folder
    selected_folder = random.choice(available_folders)
    folder_flps = folder_map[selected_folder]

    # Step 2: If multiple FLPs in selected folder, pick the most recently modified/added one
    selected_flp = max(folder_flps, key=lambda p: os.path.getmtime(p))

    if args.no_repeat:
        history.add(os.path.abspath(selected_folder))
        save_history(target_dir, history)
    
    folder_name = os.path.basename(selected_folder)
    filename = os.path.basename(selected_flp)

    stat = os.stat(selected_flp)
    # On macOS, st_birthtime is the creation date; fallback to st_ctime if not present
    created_ts = getattr(stat, "st_birthtime", stat.st_ctime)
    modified_ts = stat.st_mtime

    created_str = datetime.datetime.fromtimestamp(created_ts).strftime("%Y-%m-%d %I:%M:%S %p")
    modified_str = datetime.datetime.fromtimestamp(modified_ts).strftime("%Y-%m-%d %I:%M:%S %p")

    print("🎲 " + "="*55)
    print(f"📁 Selected Folder : {folder_name}")
    print(f"✨ Selected Project: {filename}")
    print(f"📅 Date Created    : {created_str}")
    print(f"🕒 Date Modified   : {modified_str}")
    if len(folder_flps) > 1:
        print(f"ℹ️ (Picked latest of {len(folder_flps)} .flp files in folder)")
    if args.no_repeat:
        print(f"📊 Progress        : {len(history)} / {total_folders} opened")
    print(f"📍 Full Path       : {selected_flp}")
    print("🎲 " + "="*55)

    if args.finder or args.reveal:
        print(f"\n📂 Opening in Finder...")
        send_macos_notification("Finder Launcher", f"Opening folder: {folder_name}")
        open_in_finder(selected_flp, reveal_file=args.reveal or args.finder)
    else:
        send_macos_notification("FL Studio Loader", f"Opening: {filename}")
        open_file_in_fl_studio(selected_flp, app_override=args.app)

if __name__ == "__main__":
    main()
