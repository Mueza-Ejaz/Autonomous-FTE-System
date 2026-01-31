"""
Ralph Wiggum Autonomy Engine for Gold Tier
Implements persistent task execution with checkpointing, interruption recovery, and state management.
"""

import json
import asyncio
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import pickle
import os


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CHECKPOINTED = "checkpointed"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class TaskPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskCheckpoint:
    """Represents a checkpoint in a task's execution"""

    def __init__(self, checkpoint_id: str, task_id: str, step: int, data: Dict[str, Any], timestamp: datetime):
        self.checkpoint_id = checkpoint_id
        self.task_id = task_id
        self.step = step
        self.data = data  # Serialized state data
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "checkpoint_id": self.checkpoint_id,
            "task_id": self.task_id,
            "step": self.step,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            checkpoint_id=data["checkpoint_id"],
            task_id=data["task_id"],
            step=data["step"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class AutonomyTask:
    """Represents a task managed by the Ralph Wiggum engine"""

    def __init__(self, task_id: str, name: str, steps: List[Callable], description: str = ""):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.steps = steps  # List of callable functions representing steps
        self.status = TaskStatus.PENDING
        self.priority = TaskPriority.NORMAL
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.current_step = 0
        self.checkpoints: List[TaskCheckpoint] = []
        self.state_data: Dict[str, Any] = {}
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.max_retries = 3
        self.retry_count = 0

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "current_step": self.current_step,
            "checkpoints": [ckpt.to_dict() for ckpt in self.checkpoints],
            "state_data": self.state_data,
            "result": self.result,
            "error": self.error,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        # We can't reconstruct the actual step functions from dict, so we'll create a skeleton
        task = cls.__new__(cls)
        task.task_id = data["task_id"]
        task.name = data["name"]
        task.description = data["description"]
        task.status = TaskStatus(data["status"])
        task.priority = TaskPriority(data["priority"])
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.started_at = datetime.fromisoformat(data["started_at"]) if data["started_at"] else None
        task.completed_at = datetime.fromisoformat(data["completed_at"]) if data["completed_at"] else None
        task.current_step = data["current_step"]
        task.checkpoints = [TaskCheckpoint.from_dict(ckpt) for ckpt in data["checkpoints"]]
        task.state_data = data["state_data"]
        task.result = data["result"]
        task.error = data["error"]
        task.max_retries = data["max_retries"]
        task.retry_count = data["retry_count"]
        task.steps = []  # Functions need to be reconstructed separately
        return task


class RalphWiggumEngine:
    """The Ralph Wiggum Autonomy Engine - Persistent task execution with recovery"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Autonomy_Engine"):
        self.storage_path = Path(storage_path)
        self.tasks: Dict[str, AutonomyTask] = {}
        self.active_tasks: List[str] = []
        self.checkpoint_interval = 5  # Checkpoint every N steps
        self.recovery_enabled = True

        # Create necessary directories
        self.storage_path.mkdir(parents=True, exist_ok=True)
        (self.storage_path / "Task_Queues").mkdir(exist_ok=True)
        (self.storage_path / "Checkpoints").mkdir(exist_ok=True)
        (self.storage_path / "State_Logs").mkdir(exist_ok=True)
        (self.storage_path / "Recovery").mkdir(exist_ok=True)

    def create_task(self, name: str, steps: List[Callable], description: str = "", priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Create a new task with the specified steps"""
        task_id = str(uuid.uuid4())
        task = AutonomyTask(task_id, name, steps, description)
        task.priority = priority
        self.tasks[task_id] = task

        # Save the task to storage
        self._save_task(task)

        print(f"Created task '{name}' with ID: {task_id}")
        return task_id

    def _save_task(self, task: AutonomyTask):
        """Save task state to persistent storage"""
        task_file = self.storage_path / "Task_Queues" / f"{task.task_id}.json"
        with open(task_file, 'w') as f:
            json.dump(task.to_dict(), f, indent=2)

    def _load_task(self, task_id: str) -> Optional[AutonomyTask]:
        """Load task state from persistent storage"""
        task_file = self.storage_path / "Task_Queues" / f"{task_id}.json"
        if task_file.exists():
            with open(task_file, 'r') as f:
                task_data = json.load(f)
            return AutonomyTask.from_dict(task_data)
        return None

    def _save_checkpoint(self, task: AutonomyTask):
        """Save a checkpoint of the current task state"""
        checkpoint_id = str(uuid.uuid4())
        checkpoint = TaskCheckpoint(
            checkpoint_id=checkpoint_id,
            task_id=task.task_id,
            step=task.current_step,
            data=task.state_data.copy(),
            timestamp=datetime.now()
        )

        task.checkpoints.append(checkpoint)

        # Save checkpoint to storage
        checkpoint_file = self.storage_path / "Checkpoints" / f"{task.task_id}_checkpoint_{checkpoint_id}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint.to_dict(), f, indent=2)

        print(f"Checkpoint saved for task {task.task_id} at step {task.current_step}")

    def _restore_from_checkpoint(self, task: AutonomyTask) -> bool:
        """Restore task state from the latest checkpoint"""
        if not task.checkpoints:
            return False

        # Get the most recent checkpoint
        latest_checkpoint = max(task.checkpoints, key=lambda c: c.timestamp)

        # Restore state
        task.current_step = latest_checkpoint.step
        task.state_data = latest_checkpoint.data.copy()
        task.status = TaskStatus.CHECKPOINTED

        print(f"Restored task {task.task_id} from checkpoint at step {task.current_step}")
        return True

    async def execute_task(self, task_id: str) -> bool:
        """Execute a task with checkpointing and recovery"""
        if task_id not in self.tasks:
            task = self._load_task(task_id)
            if not task:
                print(f"Task {task_id} not found")
                return False
            self.tasks[task_id] = task
        else:
            task = self.tasks[task_id]

        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            print(f"Task {task_id} is already {task.status.value}")
            return task.status == TaskStatus.COMPLETED

        # Mark as started if not already
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            self.active_tasks.append(task_id)

        print(f"Starting execution of task '{task.name}' (ID: {task_id})")

        try:
            # Execute steps one by one
            while task.current_step < len(task.steps):
                step_func = task.steps[task.current_step]

                try:
                    print(f"Executing step {task.current_step + 1}/{len(task.steps)}: {step_func.__name__ if hasattr(step_func, '__name__') else 'unknown'}")

                    # Execute the step
                    result = await self._execute_step(task, step_func, task.current_step)

                    # Store result in state data
                    task.state_data[f"step_{task.current_step}_result"] = result

                    # Checkpoint periodically
                    if (task.current_step + 1) % self.checkpoint_interval == 0:
                        self._save_checkpoint(task)

                    task.current_step += 1

                except Exception as e:
                    print(f"Error in step {task.current_step}: {str(e)}")
                    task.error = str(e)

                    # Check if we should retry
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        print(f"Retrying step {task.current_step} (attempt {task.retry_count}/{task.max_retries})")
                        continue
                    else:
                        task.status = TaskStatus.FAILED
                        self._save_task(task)
                        return False

            # All steps completed successfully
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = task.state_data.get("final_result", "Task completed successfully")

            # Remove from active tasks
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)

            self._save_task(task)
            print(f"Task '{task.name}' (ID: {task_id}) completed successfully")
            return True

        except KeyboardInterrupt:
            print(f"\nTask {task_id} interrupted by user")
            task.status = TaskStatus.INTERRUPTED
            self._save_checkpoint(task)
            self._save_task(task)
            return False
        except Exception as e:
            print(f"Unexpected error executing task {task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self._save_task(task)
            return False

    async def _execute_step(self, task: AutonomyTask, step_func: Callable, step_index: int):
        """Execute a single step with error handling"""
        # Prepare step context
        step_context = {
            'task_id': task.task_id,
            'step_index': step_index,
            'total_steps': len(task.steps),
            'state': task.state_data,
            'engine': self
        }

        # If the function expects a context parameter, pass it
        import inspect
        sig = inspect.signature(step_func)
        if len(sig.parameters) > 0:
            return await step_func(step_context) if asyncio.iscoroutinefunction(step_func) else step_func(step_context)
        else:
            return await step_func() if asyncio.iscoroutinefunction(step_func) else step_func()

    async def resume_task(self, task_id: str) -> bool:
        """Resume a task from its last checkpoint or interruption"""
        if task_id not in self.tasks:
            task = self._load_task(task_id)
            if not task:
                print(f"Task {task_id} not found")
                return False
            self.tasks[task_id] = task
        else:
            task = self.tasks[task_id]

        print(f"Resuming task '{task.name}' (ID: {task_id})")

        # If the task was interrupted, try to restore from checkpoint
        if task.status == TaskStatus.INTERRUPTED or task.status == TaskStatus.SUSPENDED:
            if self._restore_from_checkpoint(task):
                task.status = TaskStatus.IN_PROGRESS
                return await self.execute_task(task_id)
            else:
                print(f"No checkpoint found for task {task_id}, restarting from beginning")
                task.current_step = 0
                task.status = TaskStatus.IN_PROGRESS
                return await self.execute_task(task_id)
        else:
            print(f"Task {task_id} is not in a resumable state ({task.status.value})")
            return False

    def suspend_task(self, task_id: str) -> bool:
        """Suspend a running task"""
        if task_id not in self.tasks:
            print(f"Task {task_id} not found")
            return False

        task = self.tasks[task_id]
        if task.status != TaskStatus.IN_PROGRESS:
            print(f"Task {task_id} is not currently running")
            return False

        task.status = TaskStatus.SUSPENDED
        self._save_checkpoint(task)
        self._save_task(task)

        # Remove from active tasks
        if task_id in self.active_tasks:
            self.active_tasks.remove(task_id)

        print(f"Suspended task {task_id}")
        return True

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        if task_id not in self.tasks:
            task = self._load_task(task_id)
            if not task:
                return None
            self.tasks[task_id] = task

        task = self.tasks[task_id]
        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status.value,
            "progress": f"{task.current_step}/{len(task.steps)}",
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "current_step": task.current_step,
            "total_steps": len(task.steps),
            "error": task.error
        }

    def list_active_tasks(self) -> List[Dict[str, Any]]:
        """List all active tasks"""
        active_list = []
        for task_id in self.active_tasks:
            if task_id in self.tasks:
                status = self.get_task_status(task_id)
                if status:
                    active_list.append(status)
        return active_list

    async def run_pending_tasks(self):
        """Run all pending tasks"""
        pending_tasks = [tid for tid, task in self.tasks.items() if task.status == TaskStatus.PENDING]

        for task_id in pending_tasks:
            await self.execute_task(task_id)

    def cleanup_completed_tasks(self, days_old: int = 7):
        """Remove completed tasks older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        to_remove = []

        for task_id, task in self.tasks.items():
            if (task.status == TaskStatus.COMPLETED and
                task.completed_at and
                task.completed_at < cutoff_date):
                to_remove.append(task_id)

        for task_id in to_remove:
            del self.tasks[task_id]
            # Remove from storage
            task_file = self.storage_path / "Task_Queues" / f"{task_id}.json"
            if task_file.exists():
                task_file.unlink()

        print(f"Cleaned up {len(to_remove)} completed tasks older than {days_old} days")


# Example usage and test functions
async def example_step_1(context):
    """Example step 1: Initialize data"""
    print("Step 1: Initializing task data...")
    context['state']['initialized'] = True
    context['state']['data'] = {"items": [], "counter": 0}
    await asyncio.sleep(1)  # Simulate work
    return "Initialized successfully"

async def example_step_2(context):
    """Example step 2: Process data"""
    print("Step 2: Processing data...")
    context['state']['data']['counter'] += 1
    context['state']['data']['items'].append(f"Item {context['state']['data']['counter']}")
    await asyncio.sleep(1)  # Simulate work
    return f"Processed item {context['state']['data']['counter']}"

async def example_step_3(context):
    """Example step 3: Finalize task"""
    print("Step 3: Finalizing task...")
    context['state']['final_result'] = f"Completed with {len(context['state']['data']['items'])} items processed"
    await asyncio.sleep(1)  # Simulate work
    return context['state']['final_result']


async def test_ralph_wiggum_engine():
    """Test the Ralph Wiggum engine"""
    print("Testing Ralph Wiggum Autonomy Engine...")

    # Create the engine
    engine = RalphWiggumEngine()

    # Define example steps for a multi-step task
    example_steps = [
        example_step_1,
        example_step_2,
        example_step_3
    ]

    # Create a task
    task_id = engine.create_task(
        name="Example Multi-Step Task",
        steps=example_steps,
        description="This is an example of a multi-step task that demonstrates the Ralph Wiggum autonomy engine",
        priority=TaskPriority.NORMAL
    )

    print(f"Created task with ID: {task_id}")

    # Check task status
    status = engine.get_task_status(task_id)
    print(f"Initial status: {status}")

    # Execute the task
    success = await engine.execute_task(task_id)

    print(f"Task execution {'succeeded' if success else 'failed'}")

    # Check final status
    final_status = engine.get_task_status(task_id)
    print(f"Final status: {final_status}")

    return success


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_ralph_wiggum_engine())