import uuid
import threading
import subprocess
import asyncio
from typing import Dict, List
from enum import Enum
from starlette.concurrency import run_in_threadpool


class TaskStatus(Enum):
    CREATED = 0
    RUNNING = 1
    FINISHED = 2
    TERMINATED = 3


class Task:
    def __init__(self, task_id, command):
        self.task_id = task_id
        self.lock = threading.Lock()
        self.command = command
        self.status = TaskStatus.CREATED

    def wait(self):
        self.process.wait()
        self.status = TaskStatus.FINISHED

    def execute(self):
        self.status = TaskStatus.RUNNING
        self.process = subprocess.Popen(self.command)

    def terminate(self):
        self.process.kill()
        self.status = TaskStatus.TERMINATED


class TaskManager:
    def __init__(self, max_concurrent=1) -> None:
        self.max_concurrent = max_concurrent
        self.tasks: Dict[Task] = {}
        # self.tasks: List[Task] = []

    def create_task(self, command):
        if len(self.tasks) >= self.max_concurrent:
            print("Too many tasks running")
            return None
        task_id = uuid.uuid4()
        task = Task(task_id=task_id, command=command)
        self.tasks[task_id] = task
        task.execute()
        print(f"Task {task_id} created")
        return task_id

    def add_task(self, task_id: str, task: Task):
        self.tasks[task_id] = task

    def terminate_task(self, task_id: str):
        task = self.tasks[task_id]
        task.terminate()

    def wait_for_process(self, task_id: str):
        task: Task = self.tasks[task_id]
        task.wait()

    def json(self):
        return {
            "tasks": [
                {
                    "task_id": task.task_id,
                    "status": task.status.name,
                }
                for task in self.tasks.values()
            ]
        }


tm = TaskManager()
