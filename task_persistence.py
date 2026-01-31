"""
Task Persistence System for Ralph Wiggum Autonomy Engine
Handles persistent storage and retrieval of task states across system restarts.
"""

import json
import pickle
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import asyncio
import uuid


class TaskDatabase:
    """SQLite database for storing task information"""

    def __init__(self, db_path: str = "AI_Employee_Vault/Gold_Tier/Autonomy_Engine/task_database.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.init_database()

    def init_database(self):
        """Initialize the database tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    current_step INTEGER DEFAULT 0,
                    total_steps INTEGER DEFAULT 0,
                    result TEXT,
                    error TEXT,
                    max_retries INTEGER DEFAULT 3,
                    retry_count INTEGER DEFAULT 0
                )
            """)

            # Task checkpoints table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    step_number INTEGER NOT NULL,
                    checkpoint_data BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            """)

            # Task state data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_state (
                    task_id TEXT PRIMARY KEY,
                    state_data BLOB,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            """)

            conn.commit()
            conn.close()

    def save_task(self, task_data: Dict[str, Any]):
        """Save task information to the database"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert or update task
            cursor.execute("""
                INSERT OR REPLACE INTO tasks
                (id, name, description, status, priority, created_at, started_at, completed_at,
                 current_step, total_steps, result, error, max_retries, retry_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_data['task_id'],
                task_data['name'],
                task_data['description'],
                task_data['status'],
                task_data['priority'],
                task_data['created_at'],
                task_data['started_at'],
                task_data['completed_at'],
                task_data['current_step'],
                task_data['total_steps'],
                task_data['result'],
                task_data['error'],
                task_data['max_retries'],
                task_data['retry_count']
            ))

            conn.commit()
            conn.close()

    def load_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load task information from the database"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()

            if row:
                columns = [description[0] for description in cursor.description]
                task_data = dict(zip(columns, row))

                conn.close()
                return task_data

            conn.close()
            return None

    def save_checkpoint(self, task_id: str, step_number: int, checkpoint_data: Any):
        """Save a checkpoint for a task"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            checkpoint_id = str(uuid.uuid4())
            serialized_data = pickle.dumps(checkpoint_data)

            cursor.execute("""
                INSERT INTO checkpoints (id, task_id, step_number, checkpoint_data)
                VALUES (?, ?, ?, ?)
            """, (checkpoint_id, task_id, step_number, sqlite3.Binary(serialized_data)))

            conn.commit()
            conn.close()

    def load_latest_checkpoint(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load the latest checkpoint for a task"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, step_number, checkpoint_data, created_at
                FROM checkpoints
                WHERE task_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (task_id,))

            row = cursor.fetchone()

            if row:
                checkpoint_id, step_number, checkpoint_data, created_at = row
                deserialized_data = pickle.loads(checkpoint_data)

                result = {
                    'checkpoint_id': checkpoint_id,
                    'step_number': step_number,
                    'checkpoint_data': deserialized_data,
                    'created_at': created_at
                }

                conn.close()
                return result

            conn.close()
            return None

    def save_task_state(self, task_id: str, state_data: Any):
        """Save the current state data for a task"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            serialized_state = pickle.dumps(state_data)

            cursor.execute("""
                INSERT OR REPLACE INTO task_state (task_id, state_data)
                VALUES (?, ?)
            """, (task_id, sqlite3.Binary(serialized_state)))

            conn.commit()
            conn.close()

    def load_task_state(self, task_id: str) -> Optional[Any]:
        """Load the state data for a task"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT state_data FROM task_state WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()

            if row:
                state_data = pickle.loads(row[0])
                conn.close()
                return state_data

            conn.close()
            return None

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all active tasks (not completed or failed)"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tasks
                WHERE status IN ('pending', 'in_progress', 'checkpointed', 'suspended', 'interrupted')
            """)

            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]

            tasks = []
            for row in rows:
                tasks.append(dict(zip(columns, row)))

            conn.close()
            return tasks

    def cleanup_old_tasks(self, days_old: int = 30):
        """Remove completed tasks older than specified days"""
        with self.lock:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).strftime('%Y-%m-%d')

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete old completed tasks
            cursor.execute("""
                DELETE FROM tasks
                WHERE status = 'completed' AND completed_at < ?
            """, (cutoff_date,))

            # Delete associated checkpoints and state data
            cursor.execute("""
                DELETE FROM checkpoints
                WHERE task_id NOT IN (SELECT id FROM tasks)
            """)

            cursor.execute("""
                DELETE FROM task_state
                WHERE task_id NOT IN (SELECT id FROM tasks)
            """)

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            print(f"Cleaned up {deleted_count} old completed tasks")


class TaskPersistenceManager:
    """Manager for handling task persistence across system restarts"""

    def __init__(self):
        self.database = TaskDatabase()
        self.state_dir = Path("AI_Employee_Vault/Gold_Tier/Autonomy_Engine/State_Logs")
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def save_task_checkpoint(self, task_id: str, step_number: int, state_data: Any):
        """Save a checkpoint for a task"""
        # Save to database
        self.database.save_checkpoint(task_id, step_number, state_data)

        # Also save to file as backup
        checkpoint_file = self.state_dir / f"{task_id}_checkpoint_{step_number}.pkl"
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(state_data, f)

        print(f"Saved checkpoint for task {task_id} at step {step_number}")

    def load_task_checkpoint(self, task_id: str) -> Optional[tuple]:
        """Load the latest checkpoint for a task, returning (step_number, state_data)"""
        # Try database first
        checkpoint = self.database.load_latest_checkpoint(task_id)

        if checkpoint:
            return checkpoint['step_number'], checkpoint['checkpoint_data']

        # If not in database, try files
        checkpoint_files = list(self.state_dir.glob(f"{task_id}_checkpoint_*.pkl"))
        if checkpoint_files:
            # Get the one with the highest step number
            latest_file = max(checkpoint_files, key=lambda f: int(f.stem.split('_')[-1]))
            step_number = int(latest_file.stem.split('_')[-1])

            with open(latest_file, 'rb') as f:
                state_data = pickle.load(f)

            return step_number, state_data

        return None

    def save_task_state(self, task_id: str, task_data: Dict[str, Any], state_data: Any):
        """Save complete task state"""
        # Save task info to database
        self.database.save_task(task_data)

        # Save state data to database
        self.database.save_task_state(task_id, state_data)

        # Save to file as backup
        state_file = self.state_dir / f"{task_id}_state.json"
        with open(state_file, 'w') as f:
            json.dump({
                'task_data': task_data,
                'state_data': state_data,
                'saved_at': datetime.now().isoformat()
            }, f, indent=2)

    def load_task_state(self, task_id: str) -> Optional[tuple]:
        """Load complete task state, returning (task_data, state_data)"""
        # Try database first
        task_data = self.database.load_task(task_id)
        state_data = self.database.load_task_state(task_id)

        if task_data and state_data:
            return task_data, state_data

        # If not in database, try file backup
        state_file = self.state_dir / f"{task_id}_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                data = json.load(f)
                return data['task_data'], data['state_data']

        return None

    def get_resumable_tasks(self) -> List[str]:
        """Get list of task IDs that can be resumed"""
        # From database
        active_tasks = self.database.get_active_tasks()
        resumable_ids = [task['id'] for task in active_tasks
                         if task['status'] in ['in_progress', 'checkpointed', 'suspended', 'interrupted']]

        # Also check for any state files that aren't in DB
        state_files = list(self.state_dir.glob("*_state.json"))
        for file in state_files:
            task_id = file.name.replace("_state.json", "")
            if task_id not in resumable_ids:
                # Load to check status
                with open(file, 'r') as f:
                    data = json.load(f)
                    if data['task_data']['status'] in ['in_progress', 'checkpointed', 'suspended', 'interrupted']:
                        resumable_ids.append(task_id)

        return resumable_ids

    def cleanup_old_states(self, days_old: int = 7):
        """Remove old state files"""
        cutoff_time = datetime.now() - timedelta(days=days_old)

        for file in self.state_dir.glob("*.json"):
            if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_time:
                file.unlink()
                print(f"Removed old state file: {file}")

        for file in self.state_dir.glob("*.pkl"):
            if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_time:
                file.unlink()
                print(f"Removed old checkpoint file: {file}")

        # Also clean up database
        self.database.cleanup_old_tasks(days_old)


async def test_task_persistence():
    """Test the task persistence system"""
    print("Testing Task Persistence System...")

    manager = TaskPersistenceManager()

    # Create a sample task
    task_id = "test_task_" + str(uuid.uuid4())
    sample_task_data = {
        'task_id': task_id,
        'name': 'Test Task',
        'description': 'A test task for persistence',
        'status': 'in_progress',
        'priority': 'normal',
        'created_at': datetime.now().isoformat(),
        'started_at': datetime.now().isoformat(),
        'completed_at': None,
        'current_step': 2,
        'total_steps': 5,
        'result': None,
        'error': None,
        'max_retries': 3,
        'retry_count': 0
    }

    sample_state_data = {
        'step_results': ['result1', 'result2'],
        'current_data': {'key': 'value'},
        'processed_items': [1, 2, 3, 4]
    }

    # Save the task state
    manager.save_task_state(task_id, sample_task_data, sample_state_data)
    print(f"Saved task state for {task_id}")

    # Load the task state
    loaded_task_data, loaded_state_data = manager.load_task_state(task_id)
    print(f"Loaded task state for {task_id}")

    if loaded_task_data and loaded_state_data:
        print(f"Task name: {loaded_task_data['name']}")
        print(f"State keys: {list(loaded_state_data.keys())}")
        print("✓ Task persistence test passed")
    else:
        print("✗ Task persistence test failed - could not load state")

    # Test checkpoint functionality
    manager.save_task_checkpoint(task_id, 2, {'checkpoint_data': 'test'})
    checkpoint_result = manager.load_task_checkpoint(task_id)

    if checkpoint_result:
        step_num, data = checkpoint_result
        print(f"Loaded checkpoint for step {step_num}: {data}")
        print("✓ Checkpoint functionality test passed")
    else:
        print("✗ Checkpoint functionality test failed")

    # Test resumable tasks
    resumable = manager.get_resumable_tasks()
    print(f"Resumable tasks: {resumable}")

    return True


if __name__ == "__main__":
    asyncio.run(test_task_persistence())