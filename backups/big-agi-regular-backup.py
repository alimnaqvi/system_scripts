#!/usr/bin/env python3

import argparse
import socket
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    # 1. Setup CLI Arguments
    parser = argparse.ArgumentParser(description="Backup and commit big-AGI chats.")
    parser.add_argument(
        "-d", "--downloads-dir",
        default="~/Downloads/",
        help="Directory containing the download to back up (default: ~/Downloads/)"
    )
    parser.add_argument(
        "-b", "--backup-dir",
        default="~/my_projects/LLMs/big-AGI-backups/",
        help="Directory to store the backups (default: ~/my_projects/LLMs/big-AGI-backups/)"
    )
    
    args = parser.parse_args()

    # Resolve paths (handles relative paths, absolute paths, and expands '~')
    downloads_dir = Path(args.downloads_dir).expanduser().resolve()
    backup_dir = Path(args.backup_dir).expanduser().resolve()

    # 2. Validate Directories
    if not downloads_dir.is_dir():
        print(f"Error: Downloads directory '{downloads_dir}' does not exist.")
        sys.exit(1)
    if not backup_dir.is_dir():
        print(f"Error: Backup directory '{backup_dir}' does not exist.")
        sys.exit(1)

    # 3. Find files to back up
    to_backup = list(downloads_dir.glob("backup_chats*"))

    if len(to_backup) > 1:
        print(f"Error: '{downloads_dir}' contains more than one file. Please ensure there is only one file to back up.")
        sys.exit(1)
    elif len(to_backup) == 0:
        print(f"Error: No files found in '{downloads_dir}' to back up. Ensure there is a file named 'backup_chats*' there.")
        sys.exit(1)

    source_file = to_backup[0]

    # 4. Generate new filename with the hostname
    hostname = socket.gethostname() # equivalent to `uname -n`
    file_base = source_file.name
    file_base_host = file_base.replace("backup_chats", f"backup_chats_{hostname}")
    dest_file = backup_dir / file_base_host

    # 5. Check if exactly this file already exists
    if dest_file.exists():
        print(f"Skipping file '{file_base_host}' because it already exists in '{backup_dir}'.")
        sys.exit(0)

    # 6. Delete previous backups
    old_files = list(backup_dir.glob("backup_chats*"))
    if old_files:
        print(f"Deleting previous backups in '{backup_dir}'...")
        old_file_paths = [str(f) for f in old_files]
        try:
            # Emulate `gio trash`
            subprocess.run(["gio", "trash", *old_file_paths], check=True)
        except FileNotFoundError:
            # Robust fallback: if 'gio' is not installed (e.g., Mac/Windows/Headless Linux)
            print("Warning: 'gio' command not found. Falling back to permanent deletion.")
            for f in old_files:
                f.unlink()
        except subprocess.CalledProcessError as e:
            print(f"Error while trying to trash old files: {e}")
            sys.exit(1)

    # 7. Copy the new file
    print(f"Attempting to copy '{source_file.name}' to '{dest_file}'...")
    try:
        shutil.copy2(source_file, dest_file) # copy2 preserves file metadata
    except Exception as e:
        print(f"Error copying file: {e}")
        sys.exit(1)

    # 8. Git Operations
    print("Executing Git operations...")
    try:
        subprocess.run(["git", "add", "."], cwd=backup_dir, check=True)
        subprocess.run(["git", "commit", "-m", "regular backup"], cwd=backup_dir, check=True)
        subprocess.run(["git", "push"], cwd=backup_dir, check=True)
        print("\nSuccessfully finished big-agi-regular-backup!")
    except subprocess.CalledProcessError as e:
        print(f"\nGit operation failed. Command returned non-zero exit status: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
