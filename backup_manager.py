"""
Backup Manager for Gold Tier
Manages system backups, data preservation, and recovery capabilities.
"""

import asyncio
import json
import shutil
import zipfile
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import tarfile
import gzip
from enum import Enum


class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class BackupManager:
    """System for managing backups and recovery"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Security"):
        self.storage_path = Path(storage_path)
        (self.storage_path / "Backups").mkdir(parents=True, exist_ok=True)
        (self.storage_path / "Audit_Logs").mkdir(exist_ok=True)

        # Backup configuration
        self.backup_config = {
            "retention_days": 30,
            "full_backup_interval_days": 7,
            "incremental_backup_interval_hours": 24,
            "compression_level": 6,
            "max_backup_size_gb": 10,
            "backup_locations": [
                "AI_Employee_Vault/",
                ".env",
                "orchestrator*.py",
                "email_mcp_server.py",
                "odoo_mcp_server.py",
                "ralph_wiggum_engine.py",
                "autonomy_orchestrator.py",
                "error_recovery_system.py",
                "health_monitor.py"
            ]
        }

        # Set up logging
        self.logger = self._setup_logging()

        # Track ongoing backups
        self.active_backups = {}

    def _setup_logging(self) -> logging.Logger:
        """Set up backup manager logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = self.storage_path / "Audit_Logs" / "backup_manager.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def create_backup(self, backup_type: BackupType = BackupType.INCREMENTAL,
                     description: str = "") -> str:
        """Create a new backup"""
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_type.value}"

        backup_info = {
            "backup_id": backup_id,
            "type": backup_type.value,
            "status": BackupStatus.IN_PROGRESS.value,
            "created_at": datetime.now().isoformat(),
            "description": description,
            "size_bytes": 0,
            "files_backed_up": [],
            "source_directories": self.backup_config["backup_locations"]
        }

        # Save initial backup info
        backup_info_file = self.storage_path / "Backups" / f"{backup_id}.json"
        with open(backup_info_file, 'w') as f:
            json.dump(backup_info, f, indent=2)

        self.logger.info(f"Started {backup_type.value} backup: {backup_id}")

        try:
            # Determine backup file path
            backup_file = self.storage_path / "Backups" / f"{backup_id}.tar.gz"

            # Create the backup
            if backup_type == BackupType.FULL:
                success = self._create_full_backup(backup_file, backup_info)
            elif backup_type == BackupType.INCREMENTAL:
                success = self._create_incremental_backup(backup_file, backup_info)
            else:  # SNAPSHOT
                success = self._create_snapshot_backup(backup_file, backup_info)

            if success:
                # Update backup info
                backup_info["status"] = BackupStatus.COMPLETED.value
                backup_info["completed_at"] = datetime.now().isoformat()

                # Get backup size
                if backup_file.exists():
                    backup_info["size_bytes"] = backup_file.stat().st_size

                with open(backup_info_file, 'w') as f:
                    json.dump(backup_info, f, indent=2)

                self.logger.info(f"Completed {backup_type.value} backup: {backup_id}, size: {backup_info['size_bytes']} bytes")
                return backup_id
            else:
                backup_info["status"] = BackupStatus.FAILED.value
                backup_info["failed_at"] = datetime.now().isoformat()

                with open(backup_info_file, 'w') as f:
                    json.dump(backup_info, f, indent=2)

                self.logger.error(f"Failed {backup_type.value} backup: {backup_id}")
                return None

        except Exception as e:
            backup_info["status"] = BackupStatus.FAILED.value
            backup_info["failed_at"] = datetime.now().isoformat()
            backup_info["error"] = str(e)

            with open(backup_info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)

            self.logger.error(f"Exception during backup {backup_id}: {str(e)}")
            return None

    def _create_full_backup(self, backup_file: Path, backup_info: Dict[str, Any]) -> bool:
        """Create a full backup of all specified locations"""
        try:
            with tarfile.open(backup_file, "w:gz", compresslevel=self.backup_config["compression_level"]) as tar:
                for location_pattern in self.backup_config["backup_locations"]:
                    # Handle wildcard patterns
                    if "*" in location_pattern or "?" in location_pattern:
                        matches = list(Path(".").glob(location_pattern))
                        for match in matches:
                            if match.exists():
                                self.logger.debug(f"Adding to backup: {match}")
                                tar.add(match, arcname=match.as_posix())
                                backup_info["files_backed_up"].append(match.as_posix())
                    else:
                        path = Path(location_pattern)
                        if path.exists():
                            self.logger.debug(f"Adding to backup: {path}")
                            tar.add(path, arcname=path.as_posix())
                            backup_info["files_backed_up"].append(path.as_posix())

            return True
        except Exception as e:
            self.logger.error(f"Error creating full backup: {str(e)}")
            return False

    def _create_incremental_backup(self, backup_file: Path, backup_info: Dict[str, Any]) -> bool:
        """Create an incremental backup of changed files"""
        try:
            # For incremental backup, we'll back up files that have changed since the last backup
            # In a real implementation, we'd track file modification times
            # For this implementation, we'll do a full backup but mark it as incremental

            # Find the most recent completed backup to compare against
            last_backup_time = self._get_last_backup_time()

            with tarfile.open(backup_file, "w:gz", compresslevel=self.backup_config["compression_level"]) as tar:
                for location_pattern in self.backup_config["backup_locations"]:
                    if "*" in location_pattern or "?" in location_pattern:
                        matches = list(Path(".").glob(location_pattern))
                        for match in matches:
                            if match.exists():
                                # Check if file is newer than last backup
                                if self._is_file_newer_than(match, last_backup_time):
                                    self.logger.debug(f"Adding to incremental backup: {match}")
                                    tar.add(match, arcname=match.as_posix())
                                    backup_info["files_backed_up"].append(match.as_posix())
                    else:
                        path = Path(location_pattern)
                        if path.exists() and self._is_file_newer_than(path, last_backup_time):
                            self.logger.debug(f"Adding to incremental backup: {path}")
                            tar.add(path, arcname=path.as_posix())
                            backup_info["files_backed_up"].append(path.as_posix())

            return True
        except Exception as e:
            self.logger.error(f"Error creating incremental backup: {str(e)}")
            return False

    def _create_snapshot_backup(self, backup_file: Path, backup_info: Dict[str, Any]) -> bool:
        """Create a snapshot backup (lightweight point-in-time backup)"""
        try:
            # For snapshot, we'll create a backup of critical configuration and state files
            critical_files = [
                ".env",
                "AI_Employee_Vault/Dashboard.md",
                "AI_Employee_Vault/Briefings/",
                "AI_Employee_Vault/Needs_Action/",
                "AI_Employee_Vault/Done/",
                "AI_Employee_Vault/Gold_Tier/Autonomy_Engine/State_Logs/",
                "AI_Employee_Vault/Gold_Tier/Odoo_Integration/",
            ]

            with tarfile.open(backup_file, "w:gz", compresslevel=self.backup_config["compression_level"]) as tar:
                for location in critical_files:
                    path = Path(location)
                    if path.exists():
                        if path.is_file():
                            self.logger.debug(f"Adding to snapshot: {path}")
                            tar.add(path, arcname=path.as_posix())
                            backup_info["files_backed_up"].append(path.as_posix())
                        elif path.is_dir():
                            # Add the directory and its contents
                            for root, dirs, files in os.walk(path):
                                for file in files:
                                    file_path = Path(root) / file
                                    if self._is_file_newer_than(file_path, datetime.now() - timedelta(hours=24)):
                                        rel_path = file_path.relative_to(Path("."))
                                        self.logger.debug(f"Adding to snapshot: {rel_path}")
                                        tar.add(file_path, arcname=rel_path.as_posix())
                                        backup_info["files_backed_up"].append(rel_path.as_posix())

            return True
        except Exception as e:
            self.logger.error(f"Error creating snapshot backup: {str(e)}")
            return False

    def _is_file_newer_than(self, file_path: Path, reference_time: datetime) -> bool:
        """Check if a file is newer than the reference time"""
        try:
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            return file_time > reference_time
        except:
            # If we can't access the file time, assume it's newer
            return True

    def _get_last_backup_time(self) -> datetime:
        """Get the time of the most recent completed backup"""
        backup_files = list((self.storage_path / "Backups").glob("backup_*.json"))
        if not backup_files:
            return datetime.min

        latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
        try:
            with open(latest_backup, 'r') as f:
                backup_info = json.load(f)
                if backup_info.get("status") == BackupStatus.COMPLETED.value and "completed_at" in backup_info:
                    return datetime.fromisoformat(backup_info["completed_at"])
        except:
            pass

        # Fallback to file modification time
        return datetime.fromtimestamp(latest_backup.stat().st_mtime)

    def restore_backup(self, backup_id: str, restore_path: str = "./restored_backup/") -> bool:
        """Restore a backup to the specified path"""
        backup_file = self.storage_path / "Backups" / f"{backup_id}.tar.gz"
        backup_info_file = self.storage_path / "Backups" / f"{backup_id}.json"

        if not backup_file.exists():
            self.logger.error(f"Backup file not found: {backup_file}")
            return False

        try:
            # Load backup info
            with open(backup_info_file, 'r') as f:
                backup_info = json.load(f)

            if backup_info["status"] != BackupStatus.COMPLETED.value:
                self.logger.error(f"Cannot restore incomplete backup: {backup_id}")
                return False

            # Create restore directory
            restore_dir = Path(restore_path)
            restore_dir.mkdir(parents=True, exist_ok=True)

            # Extract backup
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(path=restore_dir)

            self.logger.info(f"Successfully restored backup {backup_id} to {restore_dir}")
            return True

        except Exception as e:
            self.logger.error(f"Error restoring backup {backup_id}: {str(e)}")
            return False

    def get_backup_list(self) -> List[Dict[str, Any]]:
        """Get a list of all backups"""
        backup_files = list((self.storage_path / "Backups").glob("backup_*.json"))
        backups = []

        for backup_file in backup_files:
            try:
                with open(backup_file, 'r') as f:
                    backup_info = json.load(f)
                    backups.append(backup_info)
            except Exception as e:
                self.logger.error(f"Error reading backup info {backup_file}: {str(e)}")

        # Sort by creation time, newest first
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return backups

    def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific backup"""
        backup_info_file = self.storage_path / "Backups" / f"{backup_id}.json"

        if not backup_info_file.exists():
            return None

        try:
            with open(backup_info_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error reading backup info {backup_id}: {str(e)}")
            return None

    def cleanup_old_backups(self) -> int:
        """Remove backups older than the retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.backup_config["retention_days"])
        backup_files = list((self.storage_path / "Backups").glob("backup_*.json"))

        deleted_count = 0
        for backup_file in backup_files:
            try:
                with open(backup_file, 'r') as f:
                    backup_info = json.load(f)

                created_at = datetime.fromisoformat(backup_info["created_at"])
                if created_at < cutoff_date:
                    # Delete both the info file and the backup file
                    backup_id = backup_info["backup_id"]
                    backup_data_file = self.storage_path / "Backups" / f"{backup_id}.tar.gz"

                    backup_file.unlink()
                    if backup_data_file.exists():
                        backup_data_file.unlink()

                    deleted_count += 1
                    self.logger.info(f"Deleted old backup: {backup_id}")
            except Exception as e:
                self.logger.error(f"Error processing backup file {backup_file}: {str(e)}")

        self.logger.info(f"Cleaned up {deleted_count} old backups")
        return deleted_count

    def schedule_regular_backups(self):
        """Schedule regular backups based on configuration"""
        # This would typically be integrated with a scheduler
        # For now, we'll just return the schedule configuration
        return {
            "full_backup_interval_days": self.backup_config["full_backup_interval_days"],
            "incremental_backup_interval_hours": self.backup_config["incremental_backup_interval_hours"],
            "retention_days": self.backup_config["retention_days"]
        }

    def verify_backup_integrity(self, backup_id: str) -> Dict[str, Any]:
        """Verify the integrity of a backup"""
        backup_file = self.storage_path / "Backups" / f"{backup_id}.tar.gz"

        if not backup_file.exists():
            return {"valid": False, "error": "Backup file not found"}

        try:
            # Try to open the archive to verify it's not corrupted
            with tarfile.open(backup_file, "r:gz") as tar:
                members = tar.getmembers()
                file_count = len(members)

                # Verify we can read the first few members
                for i, member in enumerate(members[:5]):  # Check first 5 files
                    if member.isfile():
                        try:
                            tar.extractfile(member)
                        except:
                            return {"valid": False, "error": f"Corrupted file in backup: {member.name}", "file_count": file_count}

            return {
                "valid": True,
                "file_count": file_count,
                "size_bytes": backup_file.stat().st_size
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def run_backup_monitoring(self, interval: int = 3600):  # Run every hour
        """Run continuous backup monitoring and scheduling"""
        self.logger.info("Starting backup monitoring...")

        while True:
            try:
                # Check if it's time for a full backup
                last_full_backup = self._get_last_full_backup_time()
                if (datetime.now() - last_full_backup).days >= self.backup_config["full_backup_interval_days"]:
                    self.logger.info("Time for scheduled full backup")
                    self.create_backup(BackupType.FULL, "Scheduled full backup")

                # Check if it's time for an incremental backup
                last_backup = self._get_last_backup_time()
                if (datetime.now() - last_backup).seconds >= (self.backup_config["incremental_backup_interval_hours"] * 3600):
                    self.logger.info("Time for scheduled incremental backup")
                    self.create_backup(BackupType.INCREMENTAL, "Scheduled incremental backup")

                # Clean up old backups
                self.cleanup_old_backups()

                # Wait for next check
                await asyncio.sleep(interval)

            except Exception as e:
                self.logger.error(f"Error in backup monitoring: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    def _get_last_full_backup_time(self) -> datetime:
        """Get the time of the most recent full backup"""
        backup_files = list((self.storage_path / "Backups").glob("backup_*.json"))
        full_backups = []

        for backup_file in backup_files:
            try:
                with open(backup_file, 'r') as f:
                    backup_info = json.load(f)
                    if backup_info.get("type") == "full" and backup_info.get("status") == BackupStatus.COMPLETED.value:
                        if "completed_at" in backup_info:
                            full_backups.append(datetime.fromisoformat(backup_info["completed_at"]))
            except:
                continue

        return max(full_backups) if full_backups else datetime.min


async def test_backup_manager():
    """Test the backup manager"""
    print("Testing Backup Manager...")

    manager = BackupManager()

    # Create a test backup
    print("\n1. Creating a test incremental backup...")
    backup_id = manager.create_backup(BackupType.INCREMENTAL, "Test incremental backup")

    if backup_id:
        print(f"Created backup with ID: {backup_id}")

        # Get backup info
        print("\n2. Getting backup information...")
        backup_info = manager.get_backup_info(backup_id)
        if backup_info:
            print(f"Backup status: {backup_info['status']}")
            print(f"Files backed up: {len(backup_info['files_backed_up'])}")
            print(f"Backup size: {backup_info['size_bytes']} bytes")

        # Verify backup integrity
        print("\n3. Verifying backup integrity...")
        integrity_check = manager.verify_backup_integrity(backup_id)
        print(f"Backup integrity: {'Valid' if integrity_check['valid'] else 'Invalid'}")
        if not integrity_check['valid']:
            print(f"Error: {integrity_check['error']}")

        # Get backup list
        print("\n4. Getting backup list...")
        backups = manager.get_backup_list()
        print(f"Total backups: {len(backups)}")
        for backup in backups:
            print(f"  - {backup['backup_id']}: {backup['status']} ({backup['type']})")
    else:
        print("Failed to create backup")

    # Show backup schedule
    print("\n5. Backup schedule configuration:")
    schedule = manager.schedule_regular_backups()
    print(f"  Full backup interval: {schedule['full_backup_interval_days']} days")
    print(f"  Incremental backup interval: {schedule['incremental_backup_interval_hours']} hours")
    print(f"  Retention period: {schedule['retention_days']} days")

    # Show cleanup capability (without actually deleting)
    print(f"\n6. Would clean up backups older than {manager.backup_config['retention_days']} days")

    return True


if __name__ == "__main__":
    asyncio.run(test_backup_manager())