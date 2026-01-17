from enum import Enum
from typing import Dict, Optional
from pathlib import Path


class JobStatus(Enum):
    """Enum for job statuses"""

    PROCESSING = "processing"
    DONE = "done"


class JobService:
    """Service to manage job statuses in memory"""

    def __init__(self):
        self._jobs: Dict[str, JobStatus] = {}
        self._job_to_vids: Dict[str, str] = {}

    def create_job(self, job_id: str) -> None:
        """Create a new job with PROCESSING status"""
        self._jobs[job_id] = JobStatus.PROCESSING

    def update_status(self, job_id: str, status: JobStatus) -> None:
        """Update the status of a job"""
        if job_id not in self._jobs:
            raise ValueError(f"Job {job_id} not found")
        self._jobs[job_id] = status

    def get_status(self, job_id: str) -> Optional[JobStatus]:
        """Get the status of a job"""
        return self._jobs.get(job_id)

    def mark_done(self, job_id: str) -> None:
        """Mark a job as done"""
        self.update_status(job_id, JobStatus.DONE)

    def add_video(self, job_id: str, vid_id: str) -> None:
        """Add a video to a job"""
        if job_id not in self._jobs:
            raise ValueError(f"Job {job_id} not found")
        if job_id not in self._job_to_vids:
            self._job_to_vids[job_id] = []
        self._job_to_vids[job_id].append(vid_id)

    def get_videos(self, job_id: str) -> list[Path]:
        """Get all videos for a job"""
        return self._job_to_vids.get(job_id, [])

    def set_videos(self, job_id: str, vid_ids: list[str]) -> None:
        """Set all videos for a job (replaces existing list)"""
        if job_id not in self._jobs:
            raise ValueError(f"Job {job_id} not found")
        self._job_to_vids[job_id] = vid_ids

    # def get_all_jobs(self) -> Dict[str, JobStatus]:
    #     """Get all jobs and their statuses"""
    #     return self._jobs.copy()

    # def job_exists(self, job_id: str) -> bool:
    #     """Check if a job exists"""
    #     return job_id in self._jobs


# Global instance
job_service = JobService()
