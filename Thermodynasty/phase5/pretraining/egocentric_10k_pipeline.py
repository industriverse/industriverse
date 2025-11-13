"""
Egocentric-10K Data Pipeline

Streaming data loader for the Egocentric-10K dataset (16.4TB, 1.08B frames)
Dataset: https://huggingface.co/datasets/builddotai/Egocentric-10K

Features:
- 10,050 hours of egocentric videos from 85 factories
- 2,138 workers performing 450+ task types
- 1.08 billion frames at 30 FPS
- H.265 encoded (16.4TB total size)
- WebDataset format for efficient streaming

Usage for EIL pretraining:
- Extract factory-specific physics patterns
- Train LeJEPA encoder on industrial visual representations
- Learn contact-rich manipulation regimes
"""

import numpy as np
from typing import Iterator, Dict, Any, List, Optional, Tuple
from pathlib import Path
import json
from dataclasses import dataclass
import warnings

# Import datasets with fallback
try:
    from datasets import load_dataset, IterableDataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    warnings.warn("HuggingFace datasets not installed. Will use simulated data.")

# Import cv2 with fallback
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    warnings.warn("OpenCV (cv2) not installed. Some features will be limited.")


@dataclass
class EgocentricConfig:
    """Configuration for Egocentric-10K dataset"""
    dataset_name: str = "builddotai/Egocentric-10K"
    cache_dir: Optional[str] = None  # Set to your 20TB drive path
    streaming: bool = True  # Always use streaming for 16.4TB dataset
    num_factories: int = 85  # Total factories available
    fps: int = 30  # Frames per second
    resolution: Tuple[int, int] = (1920, 1080)  # 1080p HD
    video_format: str = "H.265"  # Compression format


@dataclass
class VideoSample:
    """Single video sample from Egocentric-10K"""
    video_id: str
    factory_id: int
    worker_id: int
    task_type: str
    frames: np.ndarray  # [num_frames, height, width, 3]
    timestamp: float
    metadata: Dict[str, Any]


class EgocentricDataLoader:
    """Streaming data loader for Egocentric-10K

    Efficiently streams from HuggingFace without downloading entire 16.4TB.
    Supports factory-specific filtering and temporal sampling.
    """

    def __init__(self, config: EgocentricConfig):
        self.config = config
        self.dataset = None
        self._is_initialized = False

    def initialize(self):
        """Initialize HuggingFace dataset connection

        Note: First call may take a few minutes to establish connection
        """
        if self._is_initialized:
            return

        if not DATASETS_AVAILABLE:
            print(f"⚠️  HuggingFace datasets not available, using simulated data")
            self._use_simulated_data()
            return

        try:
            print(f"🔄 Connecting to Egocentric-10K dataset...")
            print(f"   Dataset: {self.config.dataset_name}")
            print(f"   Streaming: {self.config.streaming}")

            # Load dataset in streaming mode
            self.dataset = load_dataset(
                self.config.dataset_name,
                streaming=self.config.streaming,
                cache_dir=self.config.cache_dir
            )

            self._is_initialized = True

            print(f"✅ Egocentric-10K connected successfully")
            print(f"   Total factories: {self.config.num_factories}")
            print(f"   Total hours: 10,050")
            print(f"   Total frames: 1.08 billion")

        except Exception as e:
            warnings.warn(f"Failed to load Egocentric-10K: {e}")
            print(f"⚠️  Using simulated data for development")
            self._use_simulated_data()

    def _use_simulated_data(self):
        """Fallback to simulated data for development/testing"""
        self.dataset = None
        self._is_initialized = True
        print(f"✅ Simulated Egocentric-10K initialized")

    def stream_factory(
        self,
        factory_id: int,
        num_videos: Optional[int] = None,
        task_filter: Optional[List[str]] = None
    ) -> Iterator[VideoSample]:
        """Stream videos from specific factory

        Args:
            factory_id: Factory ID (0-84)
            num_videos: Max videos to stream (None = unlimited)
            task_filter: List of task types to include

        Yields:
            VideoSample objects with frames and metadata
        """
        if not self._is_initialized:
            self.initialize()

        if self.dataset is None:
            # Simulated data
            yield from self._stream_simulated_factory(factory_id, num_videos)
            return

        count = 0
        for sample in self.dataset['train']:
            # Filter by factory
            if sample.get('factory_id') != factory_id:
                continue

            # Filter by task type
            if task_filter and sample.get('task_type') not in task_filter:
                continue

            # Decode video frames
            frames = self._decode_video(sample['video_bytes'])

            yield VideoSample(
                video_id=sample['video_id'],
                factory_id=sample['factory_id'],
                worker_id=sample['worker_id'],
                task_type=sample['task_type'],
                frames=frames,
                timestamp=sample['timestamp'],
                metadata=sample.get('metadata', {})
            )

            count += 1
            if num_videos and count >= num_videos:
                break

    def stream_all_factories(
        self,
        num_videos_per_factory: int = 100
    ) -> Iterator[VideoSample]:
        """Stream videos from all 85 factories

        Args:
            num_videos_per_factory: Videos to sample per factory

        Yields:
            VideoSample objects
        """
        for factory_id in range(self.config.num_factories):
            print(f"📹 Streaming from factory {factory_id+1}/85...")
            yield from self.stream_factory(
                factory_id=factory_id,
                num_videos=num_videos_per_factory
            )

    def _stream_simulated_factory(
        self,
        factory_id: int,
        num_videos: Optional[int]
    ) -> Iterator[VideoSample]:
        """Simulate factory video data for testing"""
        num_videos = num_videos or 10

        for i in range(num_videos):
            # Generate synthetic video frames
            num_frames = 60  # 2 seconds at 30fps
            frames = np.random.randint(
                0, 255,
                (num_frames, 224, 224, 3),
                dtype=np.uint8
            )

            yield VideoSample(
                video_id=f"sim_factory{factory_id}_video{i}",
                factory_id=factory_id,
                worker_id=i % 10,
                task_type="simulated_task",
                frames=frames,
                timestamp=float(i),
                metadata={'simulated': True}
            )

    @staticmethod
    def _decode_video(video_bytes: bytes) -> np.ndarray:
        """Decode H.265 video bytes to frames

        Args:
            video_bytes: Compressed video data

        Returns:
            frames: [num_frames, height, width, 3]
        """
        if not CV2_AVAILABLE:
            # Fallback: Return dummy frames
            warnings.warn("OpenCV not available, returning simulated frames")
            return np.random.randint(0, 255, (30, 224, 224, 3), dtype=np.uint8)

        # Write to temporary file
        temp_path = "/tmp/temp_video.mp4"
        with open(temp_path, 'wb') as f:
            f.write(video_bytes)

        # Read with OpenCV
        cap = cv2.VideoCapture(temp_path)
        frames = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)

        cap.release()

        return np.array(frames)

    def get_factory_statistics(self, factory_id: int, num_samples: int = 100) -> Dict[str, Any]:
        """Compute statistics for a factory

        Args:
            factory_id: Factory ID
            num_samples: Number of videos to sample

        Returns:
            Dictionary of statistics
        """
        task_types = []
        total_frames = 0
        worker_ids = set()

        for sample in self.stream_factory(factory_id, num_videos=num_samples):
            task_types.append(sample.task_type)
            total_frames += len(sample.frames)
            worker_ids.add(sample.worker_id)

        unique_tasks = len(set(task_types))
        avg_frames_per_video = total_frames / num_samples if num_samples > 0 else 0

        return {
            'factory_id': factory_id,
            'num_videos_sampled': num_samples,
            'unique_task_types': unique_tasks,
            'unique_workers': len(worker_ids),
            'total_frames': total_frames,
            'avg_frames_per_video': avg_frames_per_video,
            'avg_duration_seconds': avg_frames_per_video / self.config.fps
        }


class FactoryPhysicsExtractor:
    """Extract physics patterns from factory videos

    Analyzes egocentric videos to identify:
    - Contact-rich manipulation (assembly, welding)
    - Free-space motion (transport, inspection)
    - Tool usage patterns
    - Object interaction dynamics
    """

    def __init__(self, data_loader: EgocentricDataLoader):
        self.data_loader = data_loader

    def extract_contact_density(self, frames: np.ndarray) -> float:
        """Estimate contact density from optical flow

        High optical flow variance = contact-rich manipulation
        Low variance = free-space motion

        Args:
            frames: Video frames [num_frames, height, width, 3]

        Returns:
            contact_density: 0.0 (free-space) to 1.0 (high-contact)
        """
        if len(frames) < 2:
            return 0.0

        # Compute optical flow between consecutive frames
        flow_magnitudes = []

        if CV2_AVAILABLE:
            for i in range(len(frames) - 1):
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
                gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_RGB2GRAY)

                # Farneback optical flow
                flow = cv2.calcOpticalFlowFarneback(
                    gray1, gray2,
                    None,
                    pyr_scale=0.5,
                    levels=3,
                    winsize=15,
                    iterations=3,
                    poly_n=5,
                    poly_sigma=1.2,
                    flags=0
                )

                # Flow magnitude
                magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                flow_magnitudes.append(np.mean(magnitude))
        else:
            # Fallback: Simple frame differencing
            for i in range(len(frames) - 1):
                gray1 = np.mean(frames[i], axis=2)
                gray2 = np.mean(frames[i + 1], axis=2)
                diff = np.abs(gray2 - gray1)
                flow_magnitudes.append(np.mean(diff))

        # High variance in flow = contact-rich
        flow_std = float(np.std(flow_magnitudes))
        contact_density = np.clip(flow_std / 10.0, 0.0, 1.0)

        return contact_density

    def classify_regime(self, video: VideoSample) -> str:
        """Classify industrial regime from video

        Args:
            video: VideoSample with frames

        Returns:
            regime: One of the industrial regime types
        """
        contact_density = self.extract_contact_density(video.frames)

        # Classify based on contact density
        if contact_density > 0.7:
            return "contact_rich_stable"
        elif contact_density > 0.4:
            return "transitional_contact"
        else:
            return "free_motion_predictable"

    def extract_energy_map_proxy(self, frames: np.ndarray, grid_size: int = 64) -> np.ndarray:
        """Extract coarse energy map from video motion

        Spatially discretizes motion into grid cells as proxy for
        thermodynamic energy distribution.

        Args:
            frames: Video frames [num_frames, height, width, 3]
            grid_size: Output grid resolution

        Returns:
            energy_map: [grid_size, grid_size] proxy energy distribution
        """
        if len(frames) < 2:
            return np.ones((grid_size, grid_size))

        # Accumulate motion across all frames
        height, width = frames[0].shape[:2]
        motion_accumulator = np.zeros((height, width))

        if CV2_AVAILABLE:
            for i in range(len(frames) - 1):
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
                gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_RGB2GRAY)

                # Simple frame differencing
                diff = np.abs(gray2.astype(float) - gray1.astype(float))
                motion_accumulator += diff
        else:
            # Fallback: Simple grayscale differencing
            for i in range(len(frames) - 1):
                gray1 = np.mean(frames[i], axis=2).astype(float)
                gray2 = np.mean(frames[i + 1], axis=2).astype(float)

                # Simple frame differencing
                diff = np.abs(gray2 - gray1)
                motion_accumulator += diff

        # Downsample to grid
        cell_height = height // grid_size
        cell_width = width // grid_size

        energy_map = np.zeros((grid_size, grid_size))
        for i in range(grid_size):
            for j in range(grid_size):
                cell = motion_accumulator[
                    i * cell_height:(i + 1) * cell_height,
                    j * cell_width:(j + 1) * cell_width
                ]
                energy_map[i, j] = np.mean(cell)

        # Normalize
        energy_map = energy_map / (np.max(energy_map) + 1e-8)

        return energy_map

    def process_factory_for_eil(
        self,
        factory_id: int,
        num_videos: int = 100
    ) -> List[Dict[str, Any]]:
        """Process factory videos for EIL training

        Args:
            factory_id: Factory to process
            num_videos: Number of videos to process

        Returns:
            List of training samples with energy maps and regimes
        """
        training_samples = []

        for video in self.data_loader.stream_factory(factory_id, num_videos):
            # Extract physics features
            contact_density = self.extract_contact_density(video.frames)
            regime = self.classify_regime(video)
            energy_map = self.extract_energy_map_proxy(video.frames)

            training_samples.append({
                'video_id': video.video_id,
                'factory_id': factory_id,
                'task_type': video.task_type,
                'energy_map': energy_map,
                'regime': regime,
                'contact_density': contact_density,
                'timestamp': video.timestamp
            })

        return training_samples


if __name__ == "__main__":
    print("=" * 70)
    print("Egocentric-10K Data Pipeline Test")
    print("=" * 70)

    # Initialize data loader
    config = EgocentricConfig(
        streaming=True,
        cache_dir=None  # Will use simulated data
    )

    loader = EgocentricDataLoader(config)
    loader.initialize()

    print(f"\n📊 Testing factory streaming...")

    # Stream from factory 0
    factory_id = 0
    num_videos = 5

    video_count = 0
    for video in loader.stream_factory(factory_id, num_videos=num_videos):
        video_count += 1
        print(f"\n📹 Video {video_count}/{num_videos}")
        print(f"   ID: {video.video_id}")
        print(f"   Factory: {video.factory_id}")
        print(f"   Worker: {video.worker_id}")
        print(f"   Task: {video.task_type}")
        print(f"   Frames: {video.frames.shape}")

    # Test physics extraction
    print(f"\n🔬 Testing physics extraction...")
    extractor = FactoryPhysicsExtractor(loader)

    for video in loader.stream_factory(factory_id, num_videos=2):
        contact_density = extractor.extract_contact_density(video.frames)
        regime = extractor.classify_regime(video)
        energy_map = extractor.extract_energy_map_proxy(video.frames, grid_size=64)

        print(f"\n📹 Video: {video.video_id}")
        print(f"   Contact density: {contact_density:.3f}")
        print(f"   Regime: {regime}")
        print(f"   Energy map: {energy_map.shape}, range [{energy_map.min():.3f}, {energy_map.max():.3f}]")

    # Test EIL training data generation
    print(f"\n🎯 Generating EIL training samples...")
    training_samples = extractor.process_factory_for_eil(factory_id, num_videos=3)

    print(f"\n✅ Generated {len(training_samples)} training samples")
    for i, sample in enumerate(training_samples[:2]):
        print(f"\n   Sample {i+1}:")
        print(f"      Regime: {sample['regime']}")
        print(f"      Energy map shape: {sample['energy_map'].shape}")
        print(f"      Contact density: {sample['contact_density']:.3f}")

    # Get factory statistics
    print(f"\n📈 Computing factory statistics...")
    stats = loader.get_factory_statistics(factory_id, num_samples=5)

    print(f"\n✅ Factory {factory_id} Statistics:")
    print(f"   Videos sampled: {stats['num_videos_sampled']}")
    print(f"   Unique tasks: {stats['unique_task_types']}")
    print(f"   Unique workers: {stats['unique_workers']}")
    print(f"   Total frames: {stats['total_frames']}")
    print(f"   Avg duration: {stats['avg_duration_seconds']:.1f} seconds")

    print("\n" + "=" * 70)
    print("✅ EGOCENTRIC-10K PIPELINE COMPLETE")
    print("=" * 70)
