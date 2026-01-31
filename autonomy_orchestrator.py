"""
Autonomy Orchestrator for Gold Tier
Coordinates the Ralph Wiggum engine, task persistence, and system operations.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import signal
import sys
from enum import Enum

from ralph_wiggum_engine import RalphWiggumEngine, TaskPriority
from task_persistence import TaskPersistenceManager


class OrchestratorStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"


class AutonomyOrchestrator:
    """Main orchestrator for the autonomy system"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Autonomy_Engine"):
        self.engine = RalphWiggumEngine(storage_path)
        self.persistence = TaskPersistenceManager()
        self.status = OrchestratorStatus.IDLE
        self.running = True
        self.background_tasks = set()

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(f"{storage_path}/orchestrator.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown()

    def create_task(self, name: str, steps: List, description: str = "", priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Create a new autonomous task"""
        task_id = self.engine.create_task(name, steps, description, priority)

        # Log task creation
        self.logger.info(f"Created task: {name} (ID: {task_id})")

        return task_id

    async def schedule_task(self, name: str, steps: List, description: str = "",
                           priority: TaskPriority = TaskPriority.NORMAL,
                           delay_seconds: int = 0) -> str:
        """Schedule a task to run after a delay"""
        task_id = self.create_task(name, steps, description, priority)

        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

        # Execute the task
        success = await self.engine.execute_task(task_id)

        status = self.engine.get_task_status(task_id)
        self.logger.info(f"Task {name} (ID: {task_id}) {'completed' if success else 'failed'}")

        return task_id

    async def resume_interrupted_tasks(self):
        """Resume any tasks that were interrupted"""
        resumable_tasks = self.persistence.get_resumable_tasks()

        if not resumable_tasks:
            self.logger.info("No interrupted tasks to resume")
            return

        self.logger.info(f"Found {len(resumable_tasks)} interrupted tasks to resume")

        for task_id in resumable_tasks:
            try:
                self.logger.info(f"Attempting to resume task {task_id}")
                success = await self.engine.resume_task(task_id)

                if success:
                    self.logger.info(f"Successfully resumed task {task_id}")
                else:
                    self.logger.warning(f"Failed to resume task {task_id}")

            except Exception as e:
                self.logger.error(f"Error resuming task {task_id}: {str(e)}")

    async def run_continuous_monitoring(self):
        """Run continuous monitoring of tasks"""
        self.logger.info("Starting continuous monitoring...")

        while self.running:
            try:
                # Check for active tasks
                active_tasks = self.engine.list_active_tasks()

                if active_tasks:
                    self.logger.debug(f"Monitoring {len(active_tasks)} active tasks")

                    for task_status in active_tasks:
                        # Log task progress periodically
                        if task_status['status'] == 'in_progress':
                            progress = f"{task_status['current_step']}/{task_status['total_steps']}"
                            self.logger.debug(f"Task {task_status['name']} progress: {progress}")

                # Clean up old tasks periodically
                self.persistence.cleanup_old_states(days_old=7)
                self.engine.cleanup_completed_tasks(days_old=7)

                # Wait before next check
                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    async def run_scheduled_tasks(self):
        """Run any scheduled tasks"""
        # This would integrate with a scheduler system
        # For now, just a placeholder
        pass

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        active_tasks = self.engine.list_active_tasks()
        resumable_tasks = self.persistence.get_resumable_tasks()

        return {
            "status": self.status.value,
            "timestamp": datetime.now().isoformat(),
            "active_tasks_count": len(active_tasks),
            "resumable_tasks_count": len(resumable_tasks),
            "uptime": self._get_uptime(),
            "engine_stats": {
                "total_tasks": len(self.engine.tasks),
                "completed_tasks": len([t for t in self.engine.tasks.values() if t.status == self.engine.TaskStatus.COMPLETED]),
                "failed_tasks": len([t for t in self.engine.tasks.values() if t.status == self.engine.TaskStatus.FAILED])
            }
        }

    def _get_uptime(self) -> str:
        """Get system uptime"""
        # For simplicity, we'll return a placeholder
        # In a real system, this would track when the orchestrator started
        return "00:15:30"  # Placeholder: 15 minutes 30 seconds

    def suspend_task(self, task_id: str) -> bool:
        """Suspend a running task"""
        success = self.engine.suspend_task(task_id)
        if success:
            self.logger.info(f"Suspended task {task_id}")
        else:
            self.logger.warning(f"Failed to suspend task {task_id}")
        return success

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        return self.engine.get_task_status(task_id)

    def list_all_tasks(self) -> List[Dict[str, Any]]:
        """Get status of all tasks"""
        active_tasks = self.engine.list_active_tasks()

        # Also include any tasks from persistence that aren't in memory
        all_task_ids = set()
        all_task_ids.update([t['task_id'] for t in active_tasks])
        all_task_ids.update(self.persistence.get_resumable_tasks())

        statuses = []
        for task_id in all_task_ids:
            status = self.get_task_status(task_id)
            if status:
                statuses.append(status)

        return statuses

    def shutdown(self):
        """Initiate graceful shutdown"""
        self.logger.info("Initiating graceful shutdown...")
        self.status = OrchestratorStatus.SHUTTING_DOWN
        self.running = False

        # Cancel all background tasks
        for task in self.background_tasks:
            task.cancel()

    async def run(self):
        """Run the autonomy orchestrator"""
        self.logger.info("Starting Autonomy Orchestrator...")
        self.status = OrchestratorStatus.RUNNING

        # Resume any interrupted tasks
        await self.resume_interrupted_tasks()

        # Start monitoring in background
        monitor_task = asyncio.create_task(self.run_continuous_monitoring())
        self.background_tasks.add(monitor_task)

        # Add done callback to remove from set
        monitor_task.add_done_callback(self.background_tasks.discard)

        try:
            # Main loop
            while self.running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received, shutting down...")
        finally:
            self.shutdown()
            self.logger.info("Autonomy Orchestrator stopped.")

    def create_complex_task_example(self) -> str:
        """Create an example of a complex multi-step task"""
        import aiohttp

        async def step_initialize_data(context):
            """Step 1: Initialize data structures"""
            print("Step 1: Initializing data structures...")
            context['state']['data'] = {'items': [], 'processed': 0, 'results': []}
            await asyncio.sleep(1)  # Simulate work
            return "Data initialized"

        async def step_fetch_external_data(context):
            """Step 2: Fetch external data"""
            print("Step 2: Fetching external data...")

            # Simulate fetching data (would be actual API call in real scenario)
            try:
                # In a real scenario, this would make actual HTTP requests
                context['state']['data']['items'] = ['item1', 'item2', 'item3']
                context['state']['data']['processed'] += 3
                await asyncio.sleep(1)  # Simulate network delay
                return f"Fetched 3 items"
            except Exception as e:
                raise Exception(f"Failed to fetch data: {str(e)}")

        async def step_process_data(context):
            """Step 3: Process the fetched data"""
            print("Step 3: Processing data...")
            items = context['state']['data']['items']

            for i, item in enumerate(items):
                # Simulate processing each item
                result = f"processed_{item}"
                context['state']['data']['results'].append(result)
                context['state']['data']['processed'] += 1
                await asyncio.sleep(0.5)  # Simulate processing time

            return f"Processed {len(items)} items"

        async def step_store_results(context):
            """Step 4: Store results"""
            print("Step 4: Storing results...")
            results = context['state']['data']['results']

            # In a real scenario, this would store to database or file
            # For simulation, just store in state
            context['state']['storage_result'] = f"Stored {len(results)} results"
            context['state']['final_result'] = f"Task completed with {len(results)} processed items"

            await asyncio.sleep(1)  # Simulate storage operation
            return f"Stored {len(results)} results"

        # Define the steps for the complex task
        complex_steps = [
            step_initialize_data,
            step_fetch_external_data,
            step_process_data,
            step_store_results
        ]

        # Create the task
        task_id = self.create_task(
            name="Complex Data Processing Task",
            steps=complex_steps,
            description="An example of a complex multi-step task that fetches, processes, and stores data with checkpointing",
            priority=TaskPriority.NORMAL
        )

        return task_id


async def main():
    """Main function to run the autonomy orchestrator"""
    print("Starting Autonomy Orchestrator for Gold Tier...")

    orchestrator = AutonomyOrchestrator()

    # Create an example complex task
    print("\nCreating an example complex task...")
    task_id = orchestrator.create_complex_task_example()
    print(f"Created example task with ID: {task_id}")

    # Execute the example task
    print(f"\nExecuting example task {task_id}...")
    success = await orchestrator.engine.execute_task(task_id)
    print(f"Example task execution: {'SUCCESS' if success else 'FAILED'}")

    # Show task status
    status = orchestrator.get_task_status(task_id)
    if status:
        print(f"Task status: {status}")

    # For this example, we'll just run the orchestrator briefly
    print("\nStarting orchestrator monitoring (will run for 30 seconds)...")

    # Start the orchestrator in the background
    orchestrator_task = asyncio.create_task(orchestrator.run())

    # Let it run for a bit
    await asyncio.sleep(30)

    # Shutdown
    orchestrator.shutdown()
    try:
        await asyncio.wait_for(orchestrator_task, timeout=5.0)
    except asyncio.TimeoutError:
        print("Orchestrator shutdown timed out")

    print("Autonomy Orchestrator example completed.")


if __name__ == "__main__":
    asyncio.run(main())