"""
File System Watcher for Silver Tier AI Employee
Monitors file system for new files and creates tasks
"""
import os
import time
import shutil
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

class FileDropHandler(BaseWatcher):
    def __init__(self, vault_path, watch_folder):
        super().__init__(vault_path, check_interval=60)
        self.watch_folder = Path(watch_folder)
        self.watch_folder.mkdir(exist_ok=True)

        # Supported file types
        self.supported_types = ['.txt', '.pdf', '.doc', '.docx', '.md', '.csv', '.xlsx', '.xls']

    def check_for_updates(self):
        """Check for new files in the watch folder"""
        new_files = []

        for file_path in self.watch_folder.iterdir():
            if file_path.is_file() and file_path.suffix in self.supported_types:
                # Check if file is recent (within last 5 minutes to avoid processing old files)
                file_age = time.time() - file_path.stat().st_mtime
                if file_age < 300:  # 5 minutes
                    new_files.append(file_path)

        return new_files

    def create_action_file(self, file_path):
        """Create task file for new file"""
        task_id = f"FILE_{int(time.time())}_{file_path.name}"
        task_file = self.needs_action / f"{task_id}.md"

        content = f"""---
type: file_drop
original_name: {file_path.name}
source_path: {str(file_path)}
size: {file_path.stat().st_size} bytes
detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
priority: medium
status: pending
---

# New File Detected: {file_path.name}

## File Information
- **Name**: {file_path.name}
- **Type**: {file_path.suffix}
- **Size**: {file_path.stat().st_size} bytes
- **Location**: {str(file_path)}

## Processing Instructions
1. Read the file content
2. Determine what type of file it is
3. Decide appropriate action
"""
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(content)
        self.logger.info(f"Created task for new file: {file_path.name}")

        # Move file to vault for processing
        vault_copy = self.needs_action / file_path.name
        shutil.copy2(file_path, vault_copy)

        # Remove original file from watch folder
        file_path.unlink()

        return str(task_file)

def start_file_watcher(vault_path, watch_folder):
    """Start watching a folder for new files"""
    watcher = FileDropHandler(vault_path, watch_folder)
    print("File System Watcher started")
    print(f"Monitoring: {watch_folder}")
    print(f"Check interval: {watcher.check_interval} seconds")
    print("Drop files in the watch folder to trigger tasks.")
    watcher.run()  # Uncommented for production use

if __name__ == "__main__":
    # Configure these paths
    VAULT_PATH = "D:/Autonomous-FTE-System/AI_Employee_Vault"
    WATCH_FOLDER = "D:/Autonomous-FTE-System/Drop_Folder"

    # Create watch folder if it doesn't exist
    os.makedirs(WATCH_FOLDER, exist_ok=True)

    print("Starting File System Watcher...")
    print(f"Vault: {VAULT_PATH}")
    print(f"Watch Folder: {WATCH_FOLDER}")
    print("Drop files in the watch folder to trigger tasks.")

    start_file_watcher(VAULT_PATH, WATCH_FOLDER)