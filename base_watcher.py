"""
Base Watcher Class for Silver Tier AI Employee
Provides common functionality for all watchers
"""
import os
import time
import logging
from pathlib import Path
from datetime import datetime
import json

class BaseWatcher:
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # Create logs directory
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(exist_ok=True)

        handler = logging.FileHandler(log_dir / f'{self.__class__.__name__.lower()}_log.txt')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info(f"Initialized {self.__class__.__name__} with check interval {check_interval}s")

    def check_for_updates(self) -> list:
        """
        Abstract method to be implemented by subclasses
        Should return list of new items to process
        """
        raise NotImplementedError("Subclasses must implement check_for_updates")

    def create_action_file(self, item) -> str:
        """
        Abstract method to be implemented by subclasses
        Should create action file in Needs_Action folder
        """
        raise NotImplementedError("Subclasses must implement create_action_file")

    def run(self):
        """Main watcher loop"""
        self.logger.info(f"Starting {self.__class__.__name__}...")

        while True:
            try:
                # Check for updates
                new_items = self.check_for_updates()

                # Process new items
                for item in new_items:
                    try:
                        action_file = self.create_action_file(item)
                        self.logger.info(f"Created action file: {action_file}")
                    except Exception as e:
                        self.logger.error(f"Error creating action file: {e}")

                # Wait before next check
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                self.logger.info(f"{self.__class__.__name__} stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in {self.__class__.__name__} loop: {e}")
                time.sleep(self.check_interval)