from __future__ import annotations

from pathlib import Path
from typing import Iterator, Dict, Optional


class VideoMetadata:
    """Video metadata model"""

    video_id: str
    video_path: Path

    def __init__(self, video_id: str, video_path: Path):
        self.video_id = video_id
        self.video_path = video_path


class VideoMetadataService:
    """Service to manage video metadata in memory"""

    def __init__(self):
        self._videos: Dict[str, VideoMetadata] = {}
        self._videos["1"] = VideoMetadata(
            1, Path("storage/outputs/minecraft_parkour_video.mp4")
        )

    def add_video_metadata(self, video_id: str, video_path: str) -> VideoMetadata:
        """Add a new video to the store"""
        video = VideoMetadata(video_id=video_id, video_path=video_path)
        self._videos[video_id] = video
        return video

    def get_video_metadata(self, video_id: str) -> Optional[VideoMetadata]:
        """Get video metadata by ID"""
        return self._videos.get(video_id)

    def remove_video_metadata(self, video_id: str) -> bool:
        """Remove video metadata from store. Returns True if removed, False if not found"""
        if video_id in self._videos:
            del self._videos[video_id]
            return True
        return False

    # def get_all_videos(self) -> Dict[str, VideoMetadata]:
    #     """Get all videos"""
    #     return self._videos.copy()

    def video_metadata_exists(self, video_id: str) -> bool:
        """Check if a video exists"""
        return video_id in self._videos


# Global instance
video_metadata_service = VideoMetadataService()
