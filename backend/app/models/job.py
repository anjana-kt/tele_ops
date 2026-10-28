from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class JobStates(str, Enum):
    QUEUED = 'queued'
    RUNNING = 'running'
    PAUSED = 'paused'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


@dataclass
class Job:
    job_id: str
    device_id: str
    state: JobStates
    created_time: datetime | None = None

    allowed_state_transition = {
        JobStates.QUEUED: {JobStates.RUNNING},
        JobStates.RUNNING: {
            JobStates.PAUSED,
            JobStates.SUCCEEDED,
            JobStates.FAILED,
        },
        JobStates.PAUSED: {JobStates.RUNNING},
        JobStates.SUCCEEDED: set(),
        JobStates.FAILED: set(),
    }

    def __init__(self, device_id: str, job_id: str):
        self.job_id = job_id
        self.device_id = device_id
        self.created_time = datetime.now()
        self.state = JobStates.QUEUED


    def transition_to(self, new_state: JobStates):
        if new_state not in self.allowed_state_transition[self.state]:
            raise ValueError(f"Invalid state transition: {self.state} -> {new_state}")

        print(f"{self.state} -> {new_state}")
        self.state = new_state

