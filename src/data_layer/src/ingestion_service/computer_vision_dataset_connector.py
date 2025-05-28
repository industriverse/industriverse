"""
Computer Vision Dataset Connector for Industriverse Data Layer

This module implements a protocol-native connector for computer vision datasets
(PPE Detection and Excavator Detection), supporting MCP/A2A integration for
industrial vision applications.
"""

import json
import logging
import os
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
import shutil
import cv2
from PIL import Image

from .dataset_connector_base import DatasetConnectorBase

logger = logging.getLogger(__name__)

class ComputerVisionDatasetConnector(DatasetConnectorBase):
    """
    Connector for Computer Vision Datasets (PPE Detection, Excavator Detection).
    
    This connector provides protocol-native ingestion, validation, and
    transformation for computer vision datasets, with support for
    object detection and safety monitoring use cases.
    """
    
    def __init__(
        self,
        connector_id: str = "vision-connector",
        dataset_type: str = "ppe_detection",  # or "excavator_detection"
        config: Optional[Dict[str, Any]] = None,
        secrets_manager: Optional[Any] = None,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the Computer Vision dataset connector.
        
        Args:
            connector_id: Unique identifier for this connector
            dataset_type: Type of vision dataset ("ppe_detection" or "excavator_detection")
            config: Optional configuration dictionary
            secrets_manager: Optional secrets manager instance
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for connector files
        """
        # Validate dataset type
        if dataset_type not in ["ppe_detection", "excavator_detection"]:
            raise ValueError(f"Unsupported dataset type: {dataset_type}. Must be 'ppe_detection' or 'excavator_detection'")
        
        # Default configuration based on dataset type
        if dataset_type == "ppe_detection":
            default_config = {
                "industry_tags": ["manufacturing", "safety", "compliance", "worker_protection"],
                "intelligence_type": "safety_monitoring",
                "classes": ["helmet", "vest", "mask", "gloves", "boots", "goggles", "harness"],
                "image_size": [640, 640],
                "confidence_threshold": 0.5,
                "iou_threshold": 0.45,
                "max_detections": 100
            }
        else:  # excavator_detection
            default_config = {
                "industry_tags": ["construction", "heavy_machinery", "equipment_monitoring"],
                "intelligence_type": "equipment_tracking",
                "classes": ["excavator", "bulldozer", "loader", "dump_truck", "crane"],
                "image_size": [640, 640],
                "confidence_threshold": 0.5,
                "iou_threshold": 0.45,
                "max_detections": 50
            }
        
        # Merge with provided config
        merged_config = default_config.copy()
        if config:
            merged_config.update(config)
        
        # Initialize base class
        super().__init__(
            connector_id=connector_id,
            dataset_name=dataset_type,
            dataset_type="image",
            config=merged_config,
            secrets_manager=secrets_manager,
            manifest_path=manifest_path,
            base_dir=base_dir
        )
        
        # Set up dataset-specific directories
        self.images_dir = os.path.join(self.base_dir, "images")
        self.annotations_dir = os.path.join(self.base_dir, "annotations")
        self.processed_dir = os.path.join(self.base_dir, "processed")
        self.models_dir = os.path.join(self.base_dir, "models")
        
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.annotations_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        logger.info(f"Initialized Computer Vision dataset connector for {dataset_type}")
    
    def ingest_dataset(
        self,
        data_path: str,
        validate: bool = True,
        transform: bool = True,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest the Computer Vision dataset.
        
        Args:
            data_path: Path to the dataset directory
            validate: Whether to validate the data
            transform: Whether to transform the data
            emit_events: Whether to emit protocol events
            
        Returns:
            Ingestion result information
        """
        try:
            # Start ingestion
            start_time = time.time()
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_ingestion_started",
                        "dataset": self.dataset_name,
                        "data_path": data_path
                    }
                )
            
            # Ingest data
            result = self.ingest_data(
                source_path=data_path,
                validate=validate,
                transform=transform,
                emit_events=False
            )
            
            # Complete ingestion
            end_time = time.time()
            duration = end_time - start_time
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_ingestion_completed" if result["success"] else "dataset_ingestion_failed",
                        "dataset": self.dataset_name,
                        "statistics": self.metadata["statistics"] if "statistics" in self.metadata else {},
                        "duration": duration
                    }
                )
            
            logger.info(f"Completed dataset ingestion for {self.dataset_name} in {duration:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Failed to ingest dataset: {str(e)}")
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_ingestion_failed",
                        "dataset": self.dataset_name,
                        "error": str(e)
                    }
                )
            
            return {
                "success": False,
                "status": "dataset_ingestion_failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    def _load_data(self, source_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load data from source path.
        
        Args:
            source_path: Path to the source data
            metadata: Optional metadata about the data being loaded
            
        Returns:
            Dictionary containing loaded data information
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source path not found: {source_path}")
        
        # Determine if source is a directory or a zip file
        if os.path.isdir(source_path):
            # Directory structure
            return self._load_from_directory(source_path)
        elif source_path.endswith('.zip'):
            # Zip file
            import zipfile
            
            # Create a temporary directory
            temp_dir = os.path.join(self.base_dir, "temp_extract")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract the zip file
            with zipfile.ZipFile(source_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Load from the extracted directory
            result = self._load_from_directory(temp_dir)
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            return result
        else:
            raise ValueError(f"Unsupported source format: {source_path}")
    
    def _load_from_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Load data from a directory.
        
        Args:
            directory_path: Path to the directory containing the dataset
            
        Returns:
            Dictionary containing loaded data information
        """
        # Check for common directory structures
        
        # Structure 1: images/ and labels/ directories
        images_dir = os.path.join(directory_path, "images")
        labels_dir = os.path.join(directory_path, "labels")
        
        if os.path.exists(images_dir) and os.path.exists(labels_dir):
            return self._load_from_images_labels_dirs(images_dir, labels_dir)
        
        # Structure 2: train/, val/, test/ directories
        train_dir = os.path.join(directory_path, "train")
        val_dir = os.path.join(directory_path, "val")
        test_dir = os.path.join(directory_path, "test")
        
        if os.path.exists(train_dir):
            # Combine train, val, test data
            result = {"images": [], "annotations": [], "split": {}}
            
            # Load train data
            train_data = self._load_split_directory(train_dir)
            result["images"].extend(train_data["images"])
            result["annotations"].extend(train_data["annotations"])
            result["split"]["train"] = list(range(len(train_data["images"])))
            
            # Load val data if exists
            if os.path.exists(val_dir):
                val_data = self._load_split_directory(val_dir)
                val_start = len(result["images"])
                result["images"].extend(val_data["images"])
                result["annotations"].extend(val_data["annotations"])
                result["split"]["val"] = list(range(val_start, val_start + len(val_data["images"])))
            
            # Load test data if exists
            if os.path.exists(test_dir):
                test_data = self._load_split_directory(test_dir)
                test_start = len(result["images"])
                result["images"].extend(test_data["images"])
                result["annotations"].extend(test_data["annotations"])
                result["split"]["test"] = list(range(test_start, test_start + len(test_data["images"])))
            
            return result
        
        # Structure 3: Flat directory with images and annotations
        image_files = [f for f in os.listdir(directory_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        if image_files:
            # Look for annotation files
            annotation_files = []
            
            # Check for YOLO format (.txt with same name as image)
            txt_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.txt') and not f.startswith('.')]
            
            if txt_files:
                # Match image files with annotation files
                images = []
                annotations = []
                
                for img_file in image_files:
                    img_path = os.path.join(directory_path, img_file)
                    base_name = os.path.splitext(img_file)[0]
                    txt_file = f"{base_name}.txt"
                    
                    if txt_file in txt_files:
                        txt_path = os.path.join(directory_path, txt_file)
                        
                        # Copy image to images directory
                        dest_img_path = os.path.join(self.images_dir, img_file)
                        shutil.copy2(img_path, dest_img_path)
                        
                        # Copy annotation to annotations directory
                        dest_txt_path = os.path.join(self.annotations_dir, txt_file)
                        shutil.copy2(txt_path, dest_txt_path)
                        
                        images.append(dest_img_path)
                        annotations.append(dest_txt_path)
                
                return {
                    "images": images,
                    "annotations": annotations,
                    "format": "yolo"
                }
            
            # If no matching annotations found, just copy images
            images = []
            for img_file in image_files:
                img_path = os.path.join(directory_path, img_file)
                dest_img_path = os.path.join(self.images_dir, img_file)
                shutil.copy2(img_path, dest_img_path)
                images.append(dest_img_path)
            
            return {
                "images": images,
                "annotations": [],
                "format": "images_only"
            }
        
        # If no recognized structure, raise error
        raise ValueError(f"Could not determine dataset structure in directory: {directory_path}")
    
    def _load_split_directory(self, split_dir: str) -> Dict[str, Any]:
        """
        Load data from a train/val/test split directory.
        
        Args:
            split_dir: Path to the split directory
            
        Returns:
            Dictionary containing loaded data information
        """
        # Check for images/ and labels/ subdirectories
        images_subdir = os.path.join(split_dir, "images")
        labels_subdir = os.path.join(split_dir, "labels")
        
        if os.path.exists(images_subdir) and os.path.exists(labels_subdir):
            return self._load_from_images_labels_dirs(images_subdir, labels_subdir)
        
        # Otherwise, treat as flat directory
        image_files = [f for f in os.listdir(split_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        if image_files:
            # Look for annotation files
            txt_files = [f for f in os.listdir(split_dir) if f.lower().endswith('.txt') and not f.startswith('.')]
            
            if txt_files:
                # Match image files with annotation files
                images = []
                annotations = []
                
                for img_file in image_files:
                    img_path = os.path.join(split_dir, img_file)
                    base_name = os.path.splitext(img_file)[0]
                    txt_file = f"{base_name}.txt"
                    
                    if txt_file in txt_files:
                        txt_path = os.path.join(split_dir, txt_file)
                        
                        # Copy image to images directory
                        dest_img_path = os.path.join(self.images_dir, img_file)
                        shutil.copy2(img_path, dest_img_path)
                        
                        # Copy annotation to annotations directory
                        dest_txt_path = os.path.join(self.annotations_dir, txt_file)
                        shutil.copy2(txt_path, dest_txt_path)
                        
                        images.append(dest_img_path)
                        annotations.append(dest_txt_path)
                
                return {
                    "images": images,
                    "annotations": annotations,
                    "format": "yolo"
                }
        
        # If no recognized structure, raise error
        raise ValueError(f"Could not determine dataset structure in directory: {split_dir}")
    
    def _load_from_images_labels_dirs(self, images_dir: str, labels_dir: str) -> Dict[str, Any]:
        """
        Load data from images/ and labels/ directories.
        
        Args:
            images_dir: Path to the images directory
            labels_dir: Path to the labels directory
            
        Returns:
            Dictionary containing loaded data information
        """
        # Get all image files
        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        if not image_files:
            raise ValueError(f"No image files found in directory: {images_dir}")
        
        # Match image files with annotation files
        images = []
        annotations = []
        
        for img_file in image_files:
            img_path = os.path.join(images_dir, img_file)
            base_name = os.path.splitext(img_file)[0]
            txt_file = f"{base_name}.txt"
            txt_path = os.path.join(labels_dir, txt_file)
            
            if os.path.exists(txt_path):
                # Copy image to images directory
                dest_img_path = os.path.join(self.images_dir, img_file)
                shutil.copy2(img_path, dest_img_path)
                
                # Copy annotation to annotations directory
                dest_txt_path = os.path.join(self.annotations_dir, txt_file)
                shutil.copy2(txt_path, dest_txt_path)
                
                images.append(dest_img_path)
                annotations.append(dest_txt_path)
        
        return {
            "images": images,
            "annotations": annotations,
            "format": "yolo"
        }
    
    def _validate_data(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate the Computer Vision dataset.
        
        Args:
            data: Data to validate
            metadata: Optional metadata about the data being validated
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        # Check if data is empty
        if not data or "images" not in data or not data["images"]:
            errors.append("No images found in dataset")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings
            }
        
        # Check image files
        invalid_images = []
        image_sizes = []
        
        for img_path in data["images"]:
            if not os.path.exists(img_path):
                invalid_images.append(img_path)
                continue
            
            try:
                # Check if image can be opened
                img = Image.open(img_path)
                image_sizes.append(img.size)
            except Exception as e:
                invalid_images.append(f"{img_path} (Error: {str(e)})")
        
        if invalid_images:
            errors.append(f"Invalid image files: {invalid_images}")
        
        # Check annotations if present
        if "annotations" in data and data["annotations"]:
            invalid_annotations = []
            class_counts = {}
            
            for ann_path in data["annotations"]:
                if not os.path.exists(ann_path):
                    invalid_annotations.append(ann_path)
                    continue
                
                try:
                    # Check if annotation file can be read
                    with open(ann_path, 'r') as f:
                        lines = f.readlines()
                    
                    # Parse YOLO format annotations
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            class_id = int(parts[0])
                            
                            # Count class occurrences
                            if class_id not in class_counts:
                                class_counts[class_id] = 0
                            class_counts[class_id] += 1
                            
                            # Check if class ID is valid
                            if class_id >= len(self.config["classes"]):
                                warnings.append(f"Class ID {class_id} in {ann_path} exceeds number of classes in config")
                except Exception as e:
                    invalid_annotations.append(f"{ann_path} (Error: {str(e)})")
            
            if invalid_annotations:
                errors.append(f"Invalid annotation files: {invalid_annotations}")
            
            # Check class distribution
            if class_counts:
                # Check for missing classes
                missing_classes = []
                for i, class_name in enumerate(self.config["classes"]):
                    if i not in class_counts:
                        missing_classes.append(class_name)
                
                if missing_classes:
                    warnings.append(f"Missing classes in annotations: {missing_classes}")
                
                # Check for class imbalance
                total_annotations = sum(class_counts.values())
                imbalanced_classes = []
                
                for class_id, count in class_counts.items():
                    if class_id < len(self.config["classes"]):
                        class_name = self.config["classes"][class_id]
                        percentage = (count / total_annotations) * 100
                        
                        if percentage < 5:  # Less than 5% of annotations
                            imbalanced_classes.append(f"{class_name} ({percentage:.1f}%)")
                
                if imbalanced_classes:
                    warnings.append(f"Class imbalance detected: {imbalanced_classes}")
        
        # Check image size consistency
        if image_sizes:
            unique_sizes = set(image_sizes)
            if len(unique_sizes) > 1:
                warnings.append(f"Inconsistent image sizes detected: {unique_sizes}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "statistics": {
                "image_count": len(data["images"]),
                "annotation_count": len(data.get("annotations", [])),
                "class_distribution": class_counts if "class_counts" in locals() else {},
                "image_sizes": list(unique_sizes) if "unique_sizes" in locals() else []
            }
        }
    
    def _transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform the Computer Vision dataset.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        # Create a copy to avoid modifying the original
        transformed_data = data.copy()
        
        # Create a dataset index file
        dataset_index = []
        
        for i, img_path in enumerate(data["images"]):
            item = {
                "id": i,
                "image_path": img_path,
                "file_name": os.path.basename(img_path)
            }
            
            # Add annotation path if available
            if "annotations" in data and i < len(data["annotations"]):
                item["annotation_path"] = data["annotations"][i]
            
            # Add split information if available
            if "split" in data:
                for split_name, indices in data["split"].items():
                    if i in indices:
                        item["split"] = split_name
                        break
            
            # Extract image dimensions
            try:
                img = Image.open(img_path)
                item["width"] = img.width
                item["height"] = img.height
                item["channels"] = len(img.getbands())
            except Exception as e:
                logger.warning(f"Could not read image dimensions for {img_path}: {str(e)}")
            
            # Parse annotations if available
            if "annotation_path" in item:
                try:
                    with open(item["annotation_path"], 'r') as f:
                        lines = f.readlines()
                    
                    # Parse YOLO format annotations
                    item["annotations"] = []
                    
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            class_id = int(parts[0])
                            x_center = float(parts[1])
                            y_center = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])
                            
                            # Convert to class name if available
                            class_name = self.config["classes"][class_id] if class_id < len(self.config["classes"]) else f"class_{class_id}"
                            
                            # Add to annotations
                            item["annotations"].append({
                                "class_id": class_id,
                                "class_name": class_name,
                                "x_center": x_center,
                                "y_center": y_center,
                                "width": width,
                                "height": height
                            })
                except Exception as e:
                    logger.warning(f"Could not parse annotations for {item['annotation_path']}: {str(e)}")
            
            dataset_index.append(item)
        
        # Save dataset index
        index_path = os.path.join(self.processed_dir, "dataset_index.json")
        with open(index_path, 'w') as f:
            json.dump(dataset_index, f, indent=2)
        
        # Create class index
        class_index = {i: name for i, name in enumerate(self.config["classes"])}
        class_index_path = os.path.join(self.processed_dir, "class_index.json")
        with open(class_index_path, 'w') as f:
            json.dump(class_index, f, indent=2)
        
        # Create dataset splits if not already defined
        if "split" not in data:
            # Create random train/val/test split (80/10/10)
            import random
            random.seed(42)
            
            indices = list(range(len(dataset_index)))
            random.shuffle(indices)
            
            train_size = int(0.8 * len(indices))
            val_size = int(0.1 * len(indices))
            
            train_indices = indices[:train_size]
            val_indices = indices[train_size:train_size + val_size]
            test_indices = indices[train_size + val_size:]
            
            splits = {
                "train": train_indices,
                "val": val_indices,
                "test": test_indices
            }
            
            # Update dataset index with split information
            for i, item in enumerate(dataset_index):
                for split_name, indices in splits.items():
                    if i in indices:
                        item["split"] = split_name
                        break
            
            # Save updated dataset index
            with open(index_path, 'w') as f:
                json.dump(dataset_index, f, indent=2)
            
            # Add splits to transformed data
            transformed_data["split"] = splits
        
        # Create dataset statistics
        statistics = {
            "image_count": len(dataset_index),
            "class_distribution": {},
            "split_distribution": {}
        }
        
        # Count annotations per class
        for item in dataset_index:
            if "annotations" in item:
                for ann in item["annotations"]:
                    class_name = ann["class_name"]
                    if class_name not in statistics["class_distribution"]:
                        statistics["class_distribution"][class_name] = 0
                    statistics["class_distribution"][class_name] += 1
        
        # Count images per split
        for item in dataset_index:
            if "split" in item:
                split_name = item["split"]
                if split_name not in statistics["split_distribution"]:
                    statistics["split_distribution"][split_name] = 0
                statistics["split_distribution"][split_name] += 1
        
        # Save statistics
        statistics_path = os.path.join(self.processed_dir, "dataset_statistics.json")
        with open(statistics_path, 'w') as f:
            json.dump(statistics, f, indent=2)
        
        # Add paths to transformed data
        transformed_data["index_path"] = index_path
        transformed_data["class_index_path"] = class_index_path
        transformed_data["statistics_path"] = statistics_path
        
        return transformed_data
    
    def get_dataset_for_offer(self, offer_id: str) -> Dict[str, Any]:
        """
        Get dataset prepared for a specific offer.
        
        Args:
            offer_id: ID of the offer to prepare data for
            
        Returns:
            Dictionary with prepared dataset information
        """
        try:
            # Map offer IDs to specific data preparation methods
            offer_mappings = {
                "safety_monitoring": self._prepare_safety_monitoring,
                "ppe_detection": self._prepare_ppe_detection,
                "equipment_tracking": self._prepare_equipment_tracking,
                "excavator_detection": self._prepare_excavator_detection,
                "construction_site_monitoring": self._prepare_construction_site_monitoring
            }
            
            # Find the appropriate preparation method
            preparation_method = None
            for offer_prefix, method in offer_mappings.items():
                if offer_id.startswith(offer_prefix):
                    preparation_method = method
                    break
            
            # Use default method if no specific method found
            if preparation_method is None:
                if self.dataset_name == "ppe_detection":
                    preparation_method = self._prepare_ppe_detection
                else:  # excavator_detection
                    preparation_method = self._prepare_excavator_detection
            
            # Prepare the dataset
            result = preparation_method(offer_id)
            
            # Emit event
            self.emit_event(
                event_type="observe",
                payload={
                    "status": "dataset_prepared_for_offer",
                    "dataset": self.dataset_name,
                    "offer_id": offer_id,
                    "preparation_method": preparation_method.__name__
                }
            )
            
            return result
        except Exception as e:
            logger.error(f"Failed to prepare dataset for offer {offer_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _prepare_safety_monitoring(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for safety monitoring offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Check if dataset is PPE detection
        if self.dataset_name != "ppe_detection":
            return {
                "success": False,
                "error": f"Safety monitoring offer requires PPE detection dataset, but got {self.dataset_name}"
            }
        
        # Find the dataset index
        index_path = os.path.join(self.processed_dir, "dataset_index.json")
        if not os.path.exists(index_path):
            return {"success": False, "error": "Dataset index not found"}
        
        # Load the dataset index
        with open(index_path, 'r') as f:
            dataset_index = json.load(f)
        
        # Filter for images with safety equipment annotations
        safety_classes = ["helmet", "vest", "mask", "gloves", "boots", "goggles", "harness"]
        safety_class_ids = [self.config["classes"].index(cls) for cls in safety_classes if cls in self.config["classes"]]
        
        safety_items = []
        for item in dataset_index:
            if "annotations" in item:
                # Check if item has safety equipment annotations
                has_safety_equipment = False
                for ann in item["annotations"]:
                    if ann["class_id"] in safety_class_ids:
                        has_safety_equipment = True
                        break
                
                if has_safety_equipment:
                    safety_items.append(item)
        
        # Create a balanced dataset with both compliant and non-compliant examples
        compliant_items = []
        non_compliant_items = []
        
        for item in safety_items:
            # Check if all required PPE is present
            required_ppe = {"helmet", "vest"}  # Minimum required PPE
            present_ppe = set()
            
            for ann in item["annotations"]:
                if ann["class_id"] in safety_class_ids:
                    class_name = self.config["classes"][ann["class_id"]]
                    present_ppe.add(class_name)
            
            if required_ppe.issubset(present_ppe):
                item["compliance_status"] = "compliant"
                compliant_items.append(item)
            else:
                item["compliance_status"] = "non_compliant"
                non_compliant_items.append(item)
        
        # Balance the dataset
        max_items = min(len(compliant_items), len(non_compliant_items), 100)  # Limit to 100 items per class
        
        import random
        random.seed(42)
        
        if len(compliant_items) > max_items:
            compliant_items = random.sample(compliant_items, max_items)
        
        if len(non_compliant_items) > max_items:
            non_compliant_items = random.sample(non_compliant_items, max_items)
        
        # Combine and shuffle
        prepared_items = compliant_items + non_compliant_items
        random.shuffle(prepared_items)
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.json")
        with open(output_path, 'w') as f:
            json.dump(prepared_items, f, indent=2)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "safety_monitoring",
            "total_items": len(prepared_items),
            "compliant_items": len(compliant_items),
            "non_compliant_items": len(non_compliant_items),
            "required_ppe": list(required_ppe),
            "file_path": output_path
        }
        
        # Save metadata
        metadata_path = os.path.join(output_dir, f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "dataset_path": output_path,
            "metadata_path": metadata_path,
            "metadata": metadata
        }
    
    def _prepare_ppe_detection(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for PPE detection offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Check if dataset is PPE detection
        if self.dataset_name != "ppe_detection":
            return {
                "success": False,
                "error": f"PPE detection offer requires PPE detection dataset, but got {self.dataset_name}"
            }
        
        # Find the dataset index
        index_path = os.path.join(self.processed_dir, "dataset_index.json")
        if not os.path.exists(index_path):
            return {"success": False, "error": "Dataset index not found"}
        
        # Load the dataset index
        with open(index_path, 'r') as f:
            dataset_index = json.load(f)
        
        # Create train/val/test splits if not already defined
        splits = {}
        for item in dataset_index:
            if "split" in item:
                split_name = item["split"]
                if split_name not in splits:
                    splits[split_name] = []
                splits[split_name].append(item)
        
        if not splits:
            # Create random train/val/test split (80/10/10)
            import random
            random.seed(42)
            
            indices = list(range(len(dataset_index)))
            random.shuffle(indices)
            
            train_size = int(0.8 * len(indices))
            val_size = int(0.1 * len(indices))
            
            train_indices = indices[:train_size]
            val_indices = indices[train_size:train_size + val_size]
            test_indices = indices[train_size + val_size:]
            
            splits = {
                "train": [dataset_index[i] for i in train_indices],
                "val": [dataset_index[i] for i in val_indices],
                "test": [dataset_index[i] for i in test_indices]
            }
        
        # Create YOLO format dataset
        output_dir = os.path.join(self.processed_dir, "offers", offer_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create directories for each split
        for split_name in splits.keys():
            os.makedirs(os.path.join(output_dir, split_name, "images"), exist_ok=True)
            os.makedirs(os.path.join(output_dir, split_name, "labels"), exist_ok=True)
        
        # Copy images and labels to split directories
        for split_name, items in splits.items():
            for item in items:
                # Copy image
                img_path = item["image_path"]
                img_filename = os.path.basename(img_path)
                dest_img_path = os.path.join(output_dir, split_name, "images", img_filename)
                shutil.copy2(img_path, dest_img_path)
                
                # Copy or create label
                if "annotation_path" in item:
                    ann_path = item["annotation_path"]
                    ann_filename = os.path.basename(ann_path)
                    dest_ann_path = os.path.join(output_dir, split_name, "labels", ann_filename)
                    shutil.copy2(ann_path, dest_ann_path)
        
        # Create dataset.yaml file
        yaml_content = {
            "path": output_dir,
            "train": f"{output_dir}/train/images",
            "val": f"{output_dir}/val/images",
            "test": f"{output_dir}/test/images",
            "nc": len(self.config["classes"]),
            "names": self.config["classes"]
        }
        
        import yaml
        yaml_path = os.path.join(output_dir, "dataset.yaml")
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "ppe_detection",
            "splits": {split_name: len(items) for split_name, items in splits.items()},
            "classes": self.config["classes"],
            "yaml_path": yaml_path,
            "dataset_dir": output_dir
        }
        
        # Save metadata
        metadata_path = os.path.join(self.processed_dir, "offers", f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "dataset_dir": output_dir,
            "yaml_path": yaml_path,
            "metadata_path": metadata_path,
            "metadata": metadata
        }
    
    def _prepare_equipment_tracking(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for equipment tracking offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Check if dataset is excavator detection
        if self.dataset_name != "excavator_detection":
            return {
                "success": False,
                "error": f"Equipment tracking offer requires excavator detection dataset, but got {self.dataset_name}"
            }
        
        # Find the dataset index
        index_path = os.path.join(self.processed_dir, "dataset_index.json")
        if not os.path.exists(index_path):
            return {"success": False, "error": "Dataset index not found"}
        
        # Load the dataset index
        with open(index_path, 'r') as f:
            dataset_index = json.load(f)
        
        # Filter for images with equipment annotations
        equipment_classes = ["excavator", "bulldozer", "loader", "dump_truck", "crane"]
        equipment_class_ids = [self.config["classes"].index(cls) for cls in equipment_classes if cls in self.config["classes"]]
        
        equipment_items = []
        for item in dataset_index:
            if "annotations" in item:
                # Check if item has equipment annotations
                has_equipment = False
                for ann in item["annotations"]:
                    if ann["class_id"] in equipment_class_ids:
                        has_equipment = True
                        break
                
                if has_equipment:
                    equipment_items.append(item)
        
        # Create a dataset with equipment tracking information
        for item in equipment_items:
            # Add equipment counts
            item["equipment_counts"] = {}
            
            for ann in item["annotations"]:
                if ann["class_id"] in equipment_class_ids:
                    class_name = self.config["classes"][ann["class_id"]]
                    if class_name not in item["equipment_counts"]:
                        item["equipment_counts"][class_name] = 0
                    item["equipment_counts"][class_name] += 1
            
            # Add total equipment count
            item["total_equipment"] = sum(item["equipment_counts"].values())
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.json")
        with open(output_path, 'w') as f:
            json.dump(equipment_items, f, indent=2)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "equipment_tracking",
            "total_items": len(equipment_items),
            "equipment_classes": [cls for cls in equipment_classes if cls in self.config["classes"]],
            "equipment_distribution": {},
            "file_path": output_path
        }
        
        # Calculate equipment distribution
        for item in equipment_items:
            for equip_type, count in item["equipment_counts"].items():
                if equip_type not in metadata["equipment_distribution"]:
                    metadata["equipment_distribution"][equip_type] = 0
                metadata["equipment_distribution"][equip_type] += count
        
        # Save metadata
        metadata_path = os.path.join(output_dir, f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "dataset_path": output_path,
            "metadata_path": metadata_path,
            "metadata": metadata
        }
    
    def _prepare_excavator_detection(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for excavator detection offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Check if dataset is excavator detection
        if self.dataset_name != "excavator_detection":
            return {
                "success": False,
                "error": f"Excavator detection offer requires excavator detection dataset, but got {self.dataset_name}"
            }
        
        # Find the dataset index
        index_path = os.path.join(self.processed_dir, "dataset_index.json")
        if not os.path.exists(index_path):
            return {"success": False, "error": "Dataset index not found"}
        
        # Load the dataset index
        with open(index_path, 'r') as f:
            dataset_index = json.load(f)
        
        # Create train/val/test splits if not already defined
        splits = {}
        for item in dataset_index:
            if "split" in item:
                split_name = item["split"]
                if split_name not in splits:
                    splits[split_name] = []
                splits[split_name].append(item)
        
        if not splits:
            # Create random train/val/test split (80/10/10)
            import random
            random.seed(42)
            
            indices = list(range(len(dataset_index)))
            random.shuffle(indices)
            
            train_size = int(0.8 * len(indices))
            val_size = int(0.1 * len(indices))
            
            train_indices = indices[:train_size]
            val_indices = indices[train_size:train_size + val_size]
            test_indices = indices[train_size + val_size:]
            
            splits = {
                "train": [dataset_index[i] for i in train_indices],
                "val": [dataset_index[i] for i in val_indices],
                "test": [dataset_index[i] for i in test_indices]
            }
        
        # Create YOLO format dataset
        output_dir = os.path.join(self.processed_dir, "offers", offer_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create directories for each split
        for split_name in splits.keys():
            os.makedirs(os.path.join(output_dir, split_name, "images"), exist_ok=True)
            os.makedirs(os.path.join(output_dir, split_name, "labels"), exist_ok=True)
        
        # Copy images and labels to split directories
        for split_name, items in splits.items():
            for item in items:
                # Copy image
                img_path = item["image_path"]
                img_filename = os.path.basename(img_path)
                dest_img_path = os.path.join(output_dir, split_name, "images", img_filename)
                shutil.copy2(img_path, dest_img_path)
                
                # Copy or create label
                if "annotation_path" in item:
                    ann_path = item["annotation_path"]
                    ann_filename = os.path.basename(ann_path)
                    dest_ann_path = os.path.join(output_dir, split_name, "labels", ann_filename)
                    shutil.copy2(ann_path, dest_ann_path)
        
        # Create dataset.yaml file
        yaml_content = {
            "path": output_dir,
            "train": f"{output_dir}/train/images",
            "val": f"{output_dir}/val/images",
            "test": f"{output_dir}/test/images",
            "nc": len(self.config["classes"]),
            "names": self.config["classes"]
        }
        
        import yaml
        yaml_path = os.path.join(output_dir, "dataset.yaml")
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "excavator_detection",
            "splits": {split_name: len(items) for split_name, items in splits.items()},
            "classes": self.config["classes"],
            "yaml_path": yaml_path,
            "dataset_dir": output_dir
        }
        
        # Save metadata
        metadata_path = os.path.join(self.processed_dir, "offers", f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "dataset_dir": output_dir,
            "yaml_path": yaml_path,
            "metadata_path": metadata_path,
            "metadata": metadata
        }
    
    def _prepare_construction_site_monitoring(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for construction site monitoring offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # This offer can work with either dataset
        if self.dataset_name not in ["ppe_detection", "excavator_detection"]:
            return {
                "success": False,
                "error": f"Construction site monitoring offer requires PPE detection or excavator detection dataset, but got {self.dataset_name}"
            }
        
        # Find the dataset index
        index_path = os.path.join(self.processed_dir, "dataset_index.json")
        if not os.path.exists(index_path):
            return {"success": False, "error": "Dataset index not found"}
        
        # Load the dataset index
        with open(index_path, 'r') as f:
            dataset_index = json.load(f)
        
        # Prepare dataset based on type
        if self.dataset_name == "ppe_detection":
            # For PPE detection, focus on safety compliance
            return self._prepare_safety_monitoring(offer_id)
        else:  # excavator_detection
            # For excavator detection, focus on equipment tracking
            return self._prepare_equipment_tracking(offer_id)


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create PPE detection dataset connector
    connector = ComputerVisionDatasetConnector(dataset_type="ppe_detection")
    
    # Initialize connector
    connector.initialize()
    
    # Ingest dataset
    result = connector.ingest_dataset(
        data_path="path/to/ppe_detection_dataset"
    )
    
    print(f"Ingestion result: {json.dumps(result, indent=2)}")
    
    # Prepare dataset for an offer
    offer_result = connector.get_dataset_for_offer("safety_monitoring_001")
    print(f"Offer dataset preparation: {json.dumps(offer_result, indent=2)}")
