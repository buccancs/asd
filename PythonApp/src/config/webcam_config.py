"""
Advanced Webcam Configuration Module for Multi-Sensor Recording System

This module implements advanced configuration capabilities for Milestone 3.3 requirements including:
- Multiple camera support with camera index selection
- Recording parameter configuration (codec, resolution, frame rate)
- User-configurable preview quality settings
- Camera capability detection and validation

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.3 - Webcam Capture Integration (Advanced Configuration)
"""

import cv2
import json
import os
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Import centralized logging
from utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)


class VideoCodec(Enum):
    """Supported video codecs with fallback priority."""

    MP4V = "mp4v"
    XVID = "XVID"
    MJPG = "MJPG"
    H264 = "H264"
    X264 = "X264"


class ResolutionPreset(Enum):
    """Common resolution presets."""

    HD_720P = (1280, 720)
    HD_1080P = (1920, 1080)
    HD_480P = (854, 480)
    VGA = (640, 480)
    QVGA = (320, 240)
    UHD_4K = (3840, 2160)


@dataclass
class CameraInfo:
    """Information about an available camera."""

    index: int
    name: str
    resolution: Tuple[int, int]
    max_fps: float
    supported_resolutions: List[Tuple[int, int]]
    is_working: bool
    error_message: Optional[str] = None


@dataclass
class RecordingConfig:
    """Recording configuration parameters."""

    codec: VideoCodec = VideoCodec.MP4V
    resolution: Tuple[int, int] = (1280, 720)
    fps: int = 30
    quality: int = 80  # 0-100 quality scale
    file_format: str = "mp4"


@dataclass
class PreviewConfig:
    """Preview configuration parameters."""

    max_width: int = 640
    max_height: int = 480
    fps: int = 30
    enable_scaling: bool = True
    maintain_aspect_ratio: bool = True


@dataclass
class WebcamConfiguration:
    """Complete webcam configuration."""

    camera_index: int = 0
    camera_name: str = "Default Camera"
    recording: RecordingConfig = None
    preview: PreviewConfig = None
    auto_detect_cameras: bool = True
    fallback_codecs: List[VideoCodec] = None

    def __post_init__(self):
        if self.recording is None:
            self.recording = RecordingConfig()
        if self.preview is None:
            self.preview = PreviewConfig()
        if self.fallback_codecs is None:
            self.fallback_codecs = [VideoCodec.MP4V, VideoCodec.XVID, VideoCodec.MJPG]


class CameraDetector:
    """Detect and analyze available cameras."""

    def __init__(self):
        self.detected_cameras: List[CameraInfo] = []
        self.detection_complete = False

    def detect_cameras(self, max_cameras: int = 10) -> List[CameraInfo]:
        """
        Detect all available cameras and their capabilities.

        Args:
            max_cameras (int): Maximum number of camera indices to test

        Returns:
            List[CameraInfo]: List of detected cameras with their capabilities
        """
        print(f"[DEBUG_LOG] Detecting cameras (testing up to {max_cameras} indices)...")

        self.detected_cameras = []

        for camera_index in range(max_cameras):
            try:
                camera_info = self._analyze_camera(camera_index)
                if camera_info:
                    self.detected_cameras.append(camera_info)
                    print(
                        f"[DEBUG_LOG] Camera {camera_index}: {camera_info.name} - {camera_info.resolution[0]}x{camera_info.resolution[1]}"
                    )

            except Exception as e:
                print(f"[DEBUG_LOG] Error testing camera {camera_index}: {e}")

        self.detection_complete = True
        working_cameras = [cam for cam in self.detected_cameras if cam.is_working]
        print(
            f"[DEBUG_LOG] Camera detection complete: {len(working_cameras)} working cameras found"
        )

        return self.detected_cameras

    def _analyze_camera(self, camera_index: int) -> Optional[CameraInfo]:
        """
        Analyze a specific camera's capabilities.

        Args:
            camera_index (int): Camera index to analyze

        Returns:
            CameraInfo: Camera information or None if camera not available
        """
        cap = None
        try:
            cap = cv2.VideoCapture(camera_index)

            if not cap.isOpened():
                return CameraInfo(
                    index=camera_index,
                    name=f"Camera {camera_index}",
                    resolution=(0, 0),
                    max_fps=0,
                    supported_resolutions=[],
                    is_working=False,
                    error_message="Camera not accessible",
                )

            # Test if I can actually read frames
            ret, frame = cap.read()
            if not ret or frame is None:
                return CameraInfo(
                    index=camera_index,
                    name=f"Camera {camera_index}",
                    resolution=(0, 0),
                    max_fps=0,
                    supported_resolutions=[],
                    is_working=False,
                    error_message="Cannot read frames from camera",
                )

            # Get current resolution and FPS
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            # Test supported resolutions
            supported_resolutions = self._test_resolutions(cap)

            # Generate camera name
            camera_name = self._generate_camera_name(camera_index, width, height)

            return CameraInfo(
                index=camera_index,
                name=camera_name,
                resolution=(width, height),
                max_fps=fps if fps > 0 else 30,
                supported_resolutions=supported_resolutions,
                is_working=True,
            )

        except Exception as e:
            return CameraInfo(
                index=camera_index,
                name=f"Camera {camera_index}",
                resolution=(0, 0),
                max_fps=0,
                supported_resolutions=[],
                is_working=False,
                error_message=str(e),
            )
        finally:
            if cap:
                cap.release()

    def _test_resolutions(self, cap: cv2.VideoCapture) -> List[Tuple[int, int]]:
        """Test which resolutions are supported by the camera."""
        test_resolutions = [
            (320, 240),  # QVGA
            (640, 480),  # VGA
            (854, 480),  # 480p
            (1280, 720),  # 720p
            (1920, 1080),  # 1080p
            (3840, 2160),  # 4K
        ]

        supported = []
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        for width, height in test_resolutions:
            try:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

                # Check if the resolution was actually set
                actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                if actual_width == width and actual_height == height:
                    # Try to read a frame to confirm it works
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        supported.append((width, height))

            except Exception:
                continue

        # Restore original resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, original_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, original_height)

        return supported

    def _generate_camera_name(self, index: int, width: int, height: int) -> str:
        """Generate a descriptive name for the camera."""
        if index == 0:
            base_name = "Built-in Camera"
        else:
            base_name = f"USB Camera {index}"

        # Add resolution info
        if width >= 1920:
            quality = "HD"
        elif width >= 1280:
            quality = "HD"
        elif width >= 640:
            quality = "SD"
        else:
            quality = "Low"

        return f"{base_name} ({quality} {width}x{height})"

    def get_working_cameras(self) -> List[CameraInfo]:
        """Get list of working cameras."""
        return [cam for cam in self.detected_cameras if cam.is_working]

    def get_camera_by_index(self, index: int) -> Optional[CameraInfo]:
        """Get camera info by index."""
        for cam in self.detected_cameras:
            if cam.index == index:
                return cam
        return None


class CodecValidator:
    """Validate and test video codecs."""

    @staticmethod
    def test_codec(codec: VideoCodec, resolution: Tuple[int, int] = (640, 480)) -> bool:
        """
        Test if a codec is available and working.

        Args:
            codec (VideoCodec): Codec to test
            resolution (Tuple[int, int]): Test resolution

        Returns:
            bool: True if codec is working
        """
        try:
            # Create a temporary test file
            test_file = "codec_test.mp4"
            fourcc = cv2.VideoWriter_fourcc(*codec.value)

            writer = cv2.VideoWriter(test_file, fourcc, 30.0, resolution)

            if not writer.isOpened():
                return False

            # Create a test frame
            import numpy as np

            test_frame = np.zeros((resolution[1], resolution[0], 3), dtype=np.uint8)

            # Write a few frames
            for _ in range(5):
                writer.write(test_frame)

            writer.release()

            # Try to read the file back
            cap = cv2.VideoCapture(test_file)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()

                # Clean up test file
                try:
                    os.remove(test_file)
                except:
                    pass

                return ret and frame is not None

            return False

        except Exception as e:
            print(f"[DEBUG_LOG] Codec test failed for {codec.value}: {e}")
            return False
        finally:
            # Ensure cleanup
            try:
                if os.path.exists(test_file):
                    os.remove(test_file)
            except:
                pass

    @staticmethod
    def get_available_codecs() -> List[VideoCodec]:
        """Get list of available and working codecs."""
        available = []

        for codec in VideoCodec:
            if CodecValidator.test_codec(codec):
                available.append(codec)
                print(f"[DEBUG_LOG] Codec {codec.value} is available")
            else:
                print(f"[DEBUG_LOG] Codec {codec.value} is not available")

        return available

    @staticmethod
    def get_fallback_codec(preferred_codecs: List[VideoCodec]) -> Optional[VideoCodec]:
        """
        Get the first available codec from a list of preferred codecs.

        Args:
            preferred_codecs (List[VideoCodec]): List of codecs in order of preference

        Returns:
            VideoCodec: First available codec or None if none available
        """
        for codec in preferred_codecs:
            if CodecValidator.test_codec(codec):
                return codec

        return None


class WebcamConfigManager:
    """Manage webcam configuration with persistence."""

    def __init__(self, config_file: str = "webcam_config.json"):
        self.config_file = Path(config_file)
        self.config = WebcamConfiguration()
        self.camera_detector = CameraDetector()
        self.available_cameras: List[CameraInfo] = []
        self.available_codecs: List[VideoCodec] = []

        # Load existing configuration
        self.load_config()

    def detect_and_configure_cameras(self) -> List[CameraInfo]:
        """Detect cameras and update configuration."""
        print("[DEBUG_LOG] Detecting and configuring cameras...")

        self.available_cameras = self.camera_detector.detect_cameras()
        working_cameras = self.camera_detector.get_working_cameras()

        if working_cameras:
            # Update default camera to first working camera
            self.config.camera_index = working_cameras[0].index
            self.config.camera_name = working_cameras[0].name

            # Update recording resolution to camera's native resolution
            if working_cameras[0].supported_resolutions:
                # Choose best supported resolution
                best_resolution = max(
                    working_cameras[0].supported_resolutions, key=lambda r: r[0] * r[1]
                )
                self.config.recording.resolution = best_resolution

        return self.available_cameras

    def detect_and_configure_codecs(self) -> List[VideoCodec]:
        """Detect available codecs and update configuration."""
        print("[DEBUG_LOG] Detecting and configuring codecs...")

        self.available_codecs = CodecValidator.get_available_codecs()

        if self.available_codecs:
            # Update fallback codecs to only include available ones
            self.config.fallback_codecs = self.available_codecs

            # Set primary codec to first available
            if self.config.recording.codec not in self.available_codecs:
                self.config.recording.codec = self.available_codecs[0]

        return self.available_codecs

    def auto_configure(self) -> Dict[str, Any]:
        """Automatically configure webcam settings based on detected capabilities."""
        print("[DEBUG_LOG] Auto-configuring webcam settings...")

        # Detect cameras and codecs
        cameras = self.detect_and_configure_cameras()
        codecs = self.detect_and_configure_codecs()

        working_cameras = [cam for cam in cameras if cam.is_working]

        config_summary = {
            "cameras_detected": len(cameras),
            "working_cameras": len(working_cameras),
            "available_codecs": [codec.value for codec in codecs],
            "selected_camera": {
                "index": self.config.camera_index,
                "name": self.config.camera_name,
                "resolution": self.config.recording.resolution,
            },
            "selected_codec": self.config.recording.codec.value,
            "fallback_codecs": [codec.value for codec in self.config.fallback_codecs],
        }

        # Save updated configuration
        self.save_config()

        print(
            f"[DEBUG_LOG] Auto-configuration complete: {len(working_cameras)} cameras, {len(codecs)} codecs"
        )
        return config_summary

    def set_camera(self, camera_index: int) -> bool:
        """
        Set the active camera by index.

        Args:
            camera_index (int): Camera index to use

        Returns:
            bool: True if camera was set successfully
        """
        camera_info = self.camera_detector.get_camera_by_index(camera_index)

        if camera_info and camera_info.is_working:
            self.config.camera_index = camera_index
            self.config.camera_name = camera_info.name

            # Update recording resolution to camera's best supported resolution
            if camera_info.supported_resolutions:
                best_resolution = max(
                    camera_info.supported_resolutions, key=lambda r: r[0] * r[1]
                )
                self.config.recording.resolution = best_resolution

            self.save_config()
            print(f"[DEBUG_LOG] Camera set to index {camera_index}: {camera_info.name}")
            return True

        print(
            f"[DEBUG_LOG] Failed to set camera index {camera_index}: camera not available"
        )
        return False

    def set_recording_config(self, **kwargs) -> bool:
        """
        Update recording configuration.

        Args:
            **kwargs: Recording configuration parameters

        Returns:
            bool: True if configuration was updated successfully
        """
        try:
            if "codec" in kwargs:
                codec_value = kwargs["codec"]
                if isinstance(codec_value, str):
                    codec = VideoCodec(codec_value)
                else:
                    codec = codec_value

                # Validate codec is available
                if codec in self.available_codecs:
                    self.config.recording.codec = codec
                else:
                    print(
                        f"[DEBUG_LOG] Codec {codec.value} not available, using fallback"
                    )
                    fallback = CodecValidator.get_fallback_codec(
                        self.config.fallback_codecs
                    )
                    if fallback:
                        self.config.recording.codec = fallback

            if "resolution" in kwargs:
                resolution = kwargs["resolution"]
                if isinstance(resolution, str):
                    # Parse resolution string like "1280x720"
                    width, height = map(int, resolution.split("x"))
                    resolution = (width, height)
                self.config.recording.resolution = resolution

            if "fps" in kwargs:
                self.config.recording.fps = int(kwargs["fps"])

            if "quality" in kwargs:
                quality = max(0, min(100, int(kwargs["quality"])))
                self.config.recording.quality = quality

            if "file_format" in kwargs:
                self.config.recording.file_format = kwargs["file_format"]

            self.save_config()
            print("[DEBUG_LOG] Recording configuration updated")
            return True

        except Exception as e:
            print(f"[DEBUG_LOG] Failed to update recording configuration: {e}")
            return False

    def set_preview_config(self, **kwargs) -> bool:
        """
        Update preview configuration.

        Args:
            **kwargs: Preview configuration parameters

        Returns:
            bool: True if configuration was updated successfully
        """
        try:
            if "max_width" in kwargs:
                self.config.preview.max_width = int(kwargs["max_width"])

            if "max_height" in kwargs:
                self.config.preview.max_height = int(kwargs["max_height"])

            if "fps" in kwargs:
                self.config.preview.fps = int(kwargs["fps"])

            if "enable_scaling" in kwargs:
                self.config.preview.enable_scaling = bool(kwargs["enable_scaling"])

            if "maintain_aspect_ratio" in kwargs:
                self.config.preview.maintain_aspect_ratio = bool(
                    kwargs["maintain_aspect_ratio"]
                )

            self.save_config()
            print("[DEBUG_LOG] Preview configuration updated")
            return True

        except Exception as e:
            print(f"[DEBUG_LOG] Failed to update preview configuration: {e}")
            return False

    def get_config(self) -> WebcamConfiguration:
        """Get current configuration."""
        return self.config

    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return {
            "camera_index": self.config.camera_index,
            "camera_name": self.config.camera_name,
            "recording": asdict(self.config.recording),
            "preview": asdict(self.config.preview),
            "auto_detect_cameras": self.config.auto_detect_cameras,
            "fallback_codecs": [codec.value for codec in self.config.fallback_codecs],
            "available_cameras": [asdict(cam) for cam in self.available_cameras],
            "available_codecs": [codec.value for codec in self.available_codecs],
        }

    def save_config(self):
        """Save configuration to file."""
        try:
            config_dict = {
                "camera_index": self.config.camera_index,
                "camera_name": self.config.camera_name,
                "recording": {
                    "codec": self.config.recording.codec.value,
                    "resolution": self.config.recording.resolution,
                    "fps": self.config.recording.fps,
                    "quality": self.config.recording.quality,
                    "file_format": self.config.recording.file_format,
                },
                "preview": asdict(self.config.preview),
                "auto_detect_cameras": self.config.auto_detect_cameras,
                "fallback_codecs": [
                    codec.value for codec in self.config.fallback_codecs
                ],
            }

            with open(self.config_file, "w") as f:
                json.dump(config_dict, f, indent=2)

            print(f"[DEBUG_LOG] Configuration saved to {self.config_file}")

        except Exception as e:
            print(f"[DEBUG_LOG] Failed to save configuration: {e}")

    def load_config(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    config_dict = json.load(f)

                # Load basic settings
                self.config.camera_index = config_dict.get("camera_index", 0)
                self.config.camera_name = config_dict.get(
                    "camera_name", "Default Camera"
                )
                self.config.auto_detect_cameras = config_dict.get(
                    "auto_detect_cameras", True
                )

                # Load recording config
                recording_dict = config_dict.get("recording", {})
                self.config.recording.codec = VideoCodec(
                    recording_dict.get("codec", "mp4v")
                )
                self.config.recording.resolution = tuple(
                    recording_dict.get("resolution", [1280, 720])
                )
                self.config.recording.fps = recording_dict.get("fps", 30)
                self.config.recording.quality = recording_dict.get("quality", 80)
                self.config.recording.file_format = recording_dict.get(
                    "file_format", "mp4"
                )

                # Load preview config
                preview_dict = config_dict.get("preview", {})
                self.config.preview.max_width = preview_dict.get("max_width", 640)
                self.config.preview.max_height = preview_dict.get("max_height", 480)
                self.config.preview.fps = preview_dict.get("fps", 30)
                self.config.preview.enable_scaling = preview_dict.get(
                    "enable_scaling", True
                )
                self.config.preview.maintain_aspect_ratio = preview_dict.get(
                    "maintain_aspect_ratio", True
                )

                # Load fallback codecs
                fallback_codec_names = config_dict.get(
                    "fallback_codecs", ["mp4v", "XVID", "MJPG"]
                )
                self.config.fallback_codecs = [
                    VideoCodec(name) for name in fallback_codec_names
                ]

                print(f"[DEBUG_LOG] Configuration loaded from {self.config_file}")
            else:
                print("[DEBUG_LOG] No existing configuration file, using defaults")

        except Exception as e:
            print(f"[DEBUG_LOG] Failed to load configuration: {e}, using defaults")
            self.config = WebcamConfiguration()


def create_default_config() -> WebcamConfiguration:
    """Create a default webcam configuration."""
    return WebcamConfiguration()


if __name__ == "__main__":
    # Test configuration system
    print("[DEBUG_LOG] Testing Webcam Configuration System...")

    config_manager = WebcamConfigManager("test_webcam_config.json")

    # Auto-configure
    summary = config_manager.auto_configure()
    print(f"[DEBUG_LOG] Auto-configuration summary: {summary}")

    # Test camera selection
    working_cameras = config_manager.camera_detector.get_working_cameras()
    if working_cameras:
        print(
            f"[DEBUG_LOG] Testing camera selection with camera {working_cameras[0].index}"
        )
        config_manager.set_camera(working_cameras[0].index)

    # Test recording configuration
    config_manager.set_recording_config(resolution="1280x720", fps=30, quality=85)

    # Test preview configuration
    config_manager.set_preview_config(max_width=800, max_height=600, fps=25)

    # Display final configuration
    final_config = config_manager.get_config_dict()
    print("[DEBUG_LOG] Final configuration:")
    print(json.dumps(final_config, indent=2))

    print("[DEBUG_LOG] Webcam configuration system test completed successfully")
