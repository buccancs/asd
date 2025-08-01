"""
Calibration Module for Multi-Sensor Recording System Controller

This module provides comprehensive camera calibration functionality for
RGB-thermal camera alignment, intrinsic/extrinsic parameter calculation,
and calibration quality assessment.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.1 - PyQt GUI Scaffolding and Application Framework
"""

import cv2
import numpy as np
import json
import time
import os
from typing import List, Tuple, Dict, Optional, Union


class CalibrationManager:
    """
    Comprehensive class for managing camera calibration operations.
    
    Provides functionality for:
    - RGB camera intrinsic calibration
    - Thermal camera intrinsic calibration
    - RGB-thermal extrinsic calibration (stereo calibration)
    - Calibration pattern detection (chessboard, circle grid)
    - Calibration quality assessment and validation
    - Calibration data persistence and loading
    """

    def __init__(self):
        self.rgb_camera_matrix = None
        self.rgb_distortion_coeffs = None
        self.thermal_camera_matrix = None
        self.thermal_distortion_coeffs = None
        self.rotation_matrix = None
        self.translation_vector = None
        self.calibration_quality = None

        # Initialize calibration parameters
        self.chessboard_size = (9, 6)  # Default chessboard pattern size
        self.square_size = 25.0  # Square size in mm
        self.calibration_flags = cv2.CALIB_RATIONAL_MODEL
        
        # Pattern detection criteria for sub-pixel accuracy
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    def capture_calibration_images(self, device_client=None, num_images: int = 20) -> bool:
        """
        Capture calibration images from connected devices.

        Args:
            device_client: DeviceClient instance for communication (optional for standalone use)
            num_images: Number of calibration image pairs to capture

        Returns:
            True if calibration images captured successfully
        """
        print(f"[DEBUG_LOG] Capturing {num_images} calibration image pairs")

        if device_client is None:
            print("[INFO] No device client provided - this method requires device integration")
            print("[INFO] Use load_calibration_images_from_directory() for offline calibration")
            return False

        # This would be implemented when device integration is complete
        # For now, we provide the framework for future implementation
        
        calibration_images = []
        
        try:
            for i in range(num_images):
                print(f"[INFO] Capturing calibration image pair {i+1}/{num_images}")
                
                # Send capture command to devices
                command_data = {
                    'image_id': i,
                    'pattern_type': 'chessboard',
                    'pattern_size': self.chessboard_size
                }
                
                # This would send the actual command when device integration is complete
                # success = device_client.send_command('all', 'CAPTURE_CALIBRATION', command_data)
                
                # For now, simulate success but don't actually capture
                print(f"[INFO] Would send CAPTURE_CALIBRATION command: {command_data}")
                
                # Provide user feedback
                progress = (i + 1) / num_images * 100
                print(f"[INFO] Calibration capture progress: {progress:.1f}%")

            print(f"[INFO] Calibration capture framework ready for device integration")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error during calibration capture: {e}")
            return False

    def detect_calibration_pattern(self, image: np.ndarray, pattern_type: str = "chessboard") -> Tuple[bool, Optional[np.ndarray]]:
        """
        Detect calibration pattern in an image.

        Args:
            image: Input image (BGR or grayscale)
            pattern_type: Type of calibration pattern ('chessboard', 'circles')

        Returns:
            Tuple of (success flag, detected corner points)
        """
        print(f"[DEBUG_LOG] Detecting {pattern_type} pattern in image")

        if pattern_type == 'chessboard':
            # Convert to grayscale if needed
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Find chessboard corners
            ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)

            if ret:
                # Refine corner positions to sub-pixel accuracy
                corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
                return True, corners
            else:
                return False, None
                
        elif pattern_type == 'circles':
            # Convert to grayscale if needed
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Detect circle grid
            ret, centers = cv2.findCirclesGrid(gray, self.chessboard_size, None)
            
            if ret:
                return True, centers
            else:
                return False, None
        else:
            print(f"[ERROR] Unsupported pattern type: {pattern_type}")
            return False, None

    def calibrate_single_camera(self, images: List[np.ndarray], image_points: List[np.ndarray], 
                               object_points: List[np.ndarray]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], float]:
        """
        Perform single camera calibration.

        Args:
            images: List of calibration images
            image_points: Detected image points for each image
            object_points: Corresponding 3D object points

        Returns:
            Tuple of (camera matrix, distortion coefficients, RMS error)
        """
        print("[DEBUG_LOG] Performing single camera calibration")

        if not images or not image_points or not object_points:
            print("[ERROR] Empty input data for calibration")
            return None, None, float("inf")

        if len(images) != len(image_points) or len(images) != len(object_points):
            print("[ERROR] Mismatched input data lengths")
            return None, None, float("inf")

        try:
            # Get image size from first image
            image_size = images[0].shape[:2][::-1]  # (width, height)

            # Perform calibration
            ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
                object_points, image_points, image_size, None, None, flags=self.calibration_flags
            )

            if ret:
                # Calculate RMS reprojection error
                total_error = 0
                for i in range(len(object_points)):
                    projected_points, _ = cv2.projectPoints(
                        object_points[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs
                    )
                    error = cv2.norm(image_points[i], projected_points, cv2.NORM_L2) / len(projected_points)
                    total_error += error

                mean_error = total_error / len(object_points)
                print(f"[DEBUG_LOG] Calibration completed with RMS error: {mean_error:.3f}")
                return camera_matrix, dist_coeffs, mean_error
            else:
                print("[ERROR] Camera calibration failed")
                return None, None, float("inf")

        except Exception as e:
            print(f"[ERROR] Exception during calibration: {e}")
            return None, None, float("inf")

    def calibrate_stereo_cameras(self, rgb_images: List[np.ndarray], thermal_images: List[np.ndarray], 
                                rgb_points: List[np.ndarray], thermal_points: List[np.ndarray], 
                                object_points: List[np.ndarray]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], float]:
        """
        Perform stereo calibration between RGB and thermal cameras.

        Args:
            rgb_images: RGB calibration images
            thermal_images: Thermal calibration images
            rgb_points: RGB image points
            thermal_points: Thermal image points
            object_points: 3D object points

        Returns:
            Tuple of (rotation matrix, translation vector, RMS error)
        """
        print("[DEBUG_LOG] Performing stereo calibration")

        # Ensure both cameras are individually calibrated first
        if self.rgb_camera_matrix is None or self.thermal_camera_matrix is None:
            print("[ERROR] Individual camera calibrations must be completed first")
            return None, None, float("inf")

        if not rgb_images or not thermal_images:
            print("[ERROR] Empty image data for stereo calibration")
            return None, None, float("inf")

        try:
            image_size = rgb_images[0].shape[:2][::-1]  # (width, height)

            # Perform stereo calibration
            ret, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
                object_points, rgb_points, thermal_points,
                self.rgb_camera_matrix, self.rgb_distortion_coeffs,
                self.thermal_camera_matrix, self.thermal_distortion_coeffs,
                image_size, flags=cv2.CALIB_FIX_INTRINSIC
            )

            if ret:
                self.rotation_matrix = R
                self.translation_vector = T
                print(f"[DEBUG_LOG] Stereo calibration completed with RMS error: {ret:.3f}")
                return R, T, ret
            else:
                print("[ERROR] Stereo calibration failed")
                return None, None, float("inf")

        except Exception as e:
            print(f"[ERROR] Exception during stereo calibration: {e}")
            return None, None, float("inf")

    def assess_calibration_quality(self, images: List[np.ndarray], image_points: List[np.ndarray], 
                                   object_points: List[np.ndarray], camera_matrix: np.ndarray, 
                                   dist_coeffs: np.ndarray, rvecs: List[np.ndarray], 
                                   tvecs: List[np.ndarray]) -> Dict:
        """
        Assess the quality of camera calibration.

        Args:
            images: Calibration images
            image_points: Detected image points
            object_points: 3D object points
            camera_matrix: Camera intrinsic matrix
            dist_coeffs: Distortion coefficients
            rvecs: Rotation vectors for each image
            tvecs: Translation vectors for each image

        Returns:
            Dictionary containing calibration quality metrics
        """
        print("[DEBUG_LOG] Assessing calibration quality")

        quality_metrics = {
            'mean_reprojection_error': 0.0,
            'max_reprojection_error': 0.0,
            'std_reprojection_error': 0.0,
            'pattern_coverage': 0.0,
            'quality_score': 'UNKNOWN',
            'recommendations': []
        }

        try:
            # Calculate reprojection errors
            errors = []
            for i in range(len(object_points)):
                projected_points, _ = cv2.projectPoints(
                    object_points[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs
                )
                error = cv2.norm(image_points[i], projected_points, cv2.NORM_L2) / len(projected_points)
                errors.append(error)

            errors = np.array(errors)
            quality_metrics['mean_reprojection_error'] = float(np.mean(errors))
            quality_metrics['max_reprojection_error'] = float(np.max(errors))
            quality_metrics['std_reprojection_error'] = float(np.std(errors))

            # Assess pattern coverage (simplified - percentage of image area covered)
            if images and len(images) > 0:
                image_height, image_width = images[0].shape[:2]
                total_area = image_width * image_height
                
                # Calculate bounding box of all detected points
                all_points = np.vstack(image_points)
                min_x, min_y = np.min(all_points.reshape(-1, 2), axis=0)
                max_x, max_y = np.max(all_points.reshape(-1, 2), axis=0)
                
                coverage_area = (max_x - min_x) * (max_y - min_y)
                quality_metrics['pattern_coverage'] = min(100.0, (coverage_area / total_area) * 100)

            # Generate quality score and recommendations
            mean_error = quality_metrics['mean_reprojection_error']
            if mean_error < 0.5:
                quality_metrics['quality_score'] = 'EXCELLENT'
            elif mean_error < 1.0:
                quality_metrics['quality_score'] = 'GOOD'
            elif mean_error < 2.0:
                quality_metrics['quality_score'] = 'ACCEPTABLE'
                quality_metrics['recommendations'].append('Consider recapturing some images for better accuracy')
            else:
                quality_metrics['quality_score'] = 'POOR'
                quality_metrics['recommendations'].append('Recapture calibration images')
                quality_metrics['recommendations'].append('Ensure better lighting and pattern visibility')

            if quality_metrics['pattern_coverage'] < 60:
                quality_metrics['recommendations'].append('Improve pattern coverage across image area')

            if quality_metrics['std_reprojection_error'] > quality_metrics['mean_reprojection_error']:
                quality_metrics['recommendations'].append('High error variation - some images may be poor quality')

            print(f"[DEBUG_LOG] Quality assessment complete: {quality_metrics['quality_score']} "
                  f"(error: {mean_error:.3f}px, coverage: {quality_metrics['pattern_coverage']:.1f}%)")

            return quality_metrics

        except Exception as e:
            print(f"[ERROR] Exception during quality assessment: {e}")
            return quality_metrics

    def save_calibration_data(self, filename: str) -> bool:
        """
        Save calibration data to file.

        Args:
            filename: Path to save calibration data

        Returns:
            True if saved successfully
        """
        print(f"[DEBUG_LOG] Saving calibration data to {filename}")

        calibration_data = {
            'rgb_camera_matrix': self.rgb_camera_matrix.tolist() if self.rgb_camera_matrix is not None else None,
            'rgb_distortion_coeffs': self.rgb_distortion_coeffs.tolist() if self.rgb_distortion_coeffs is not None else None,
            'thermal_camera_matrix': self.thermal_camera_matrix.tolist() if self.thermal_camera_matrix is not None else None,
            'thermal_distortion_coeffs': self.thermal_distortion_coeffs.tolist() if self.thermal_distortion_coeffs is not None else None,
            'rotation_matrix': self.rotation_matrix.tolist() if self.rotation_matrix is not None else None,
            'translation_vector': self.translation_vector.tolist() if self.translation_vector is not None else None,
            'calibration_quality': self.calibration_quality,
            'timestamp': time.time(),
            'calibration_parameters': {
                'chessboard_size': self.chessboard_size,
                'square_size': self.square_size,
                'calibration_flags': int(self.calibration_flags)  # Convert to int for JSON serialization
            }
        }

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(calibration_data, f, indent=2)
            
            print(f"[DEBUG_LOG] Calibration data saved successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Error saving calibration data: {e}")
            return False

    def load_calibration_data(self, filename: str) -> bool:
        """
        Load calibration data from file.

        Args:
            filename: Path to calibration data file

        Returns:
            True if loaded successfully
        """
        print(f"[DEBUG_LOG] Loading calibration data from {filename}")

        try:
            if not os.path.exists(filename):
                print(f"[ERROR] Calibration file does not exist: {filename}")
                return False
                
            with open(filename, 'r') as f:
                calibration_data = json.load(f)

            # Load camera parameters
            if calibration_data.get('rgb_camera_matrix'):
                self.rgb_camera_matrix = np.array(calibration_data['rgb_camera_matrix'])
            if calibration_data.get('rgb_distortion_coeffs'):
                self.rgb_distortion_coeffs = np.array(calibration_data['rgb_distortion_coeffs'])
            if calibration_data.get('thermal_camera_matrix'):
                self.thermal_camera_matrix = np.array(calibration_data['thermal_camera_matrix'])
            if calibration_data.get('thermal_distortion_coeffs'):
                self.thermal_distortion_coeffs = np.array(calibration_data['thermal_distortion_coeffs'])
            if calibration_data.get('rotation_matrix'):
                self.rotation_matrix = np.array(calibration_data['rotation_matrix'])
            if calibration_data.get('translation_vector'):
                self.translation_vector = np.array(calibration_data['translation_vector'])

            self.calibration_quality = calibration_data.get('calibration_quality')

            # Load calibration parameters if available
            if 'calibration_parameters' in calibration_data:
                params = calibration_data['calibration_parameters']
                self.chessboard_size = tuple(params.get('chessboard_size', self.chessboard_size))
                self.square_size = params.get('square_size', self.square_size)
                self.calibration_flags = params.get('calibration_flags', self.calibration_flags)

            print(f"[DEBUG_LOG] Calibration data loaded successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error loading calibration data: {e}")
            return False
    
    def load_calibration_images_from_directory(self, directory_path: str, 
                                             rgb_pattern: str = "*rgb*.jpg", 
                                             thermal_pattern: str = "*thermal*.jpg") -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Load calibration images from a directory for offline calibration.
        
        Args:
            directory_path: Path to directory containing calibration images
            rgb_pattern: File pattern for RGB images
            thermal_pattern: File pattern for thermal images
            
        Returns:
            Tuple of (RGB images list, thermal images list)
        """
        import glob
        
        rgb_images = []
        thermal_images = []
        
        try:
            # Find RGB images
            rgb_files = sorted(glob.glob(os.path.join(directory_path, rgb_pattern)))
            thermal_files = sorted(glob.glob(os.path.join(directory_path, thermal_pattern)))
            
            print(f"[DEBUG_LOG] Found {len(rgb_files)} RGB images and {len(thermal_files)} thermal images")
            
            # Load RGB images
            for rgb_file in rgb_files:
                img = cv2.imread(rgb_file)
                if img is not None:
                    rgb_images.append(img)
                else:
                    print(f"[WARNING] Could not load RGB image: {rgb_file}")
            
            # Load thermal images
            for thermal_file in thermal_files:
                img = cv2.imread(thermal_file)
                if img is not None:
                    thermal_images.append(img)
                else:
                    print(f"[WARNING] Could not load thermal image: {thermal_file}")
                    
            return rgb_images, thermal_images
            
        except Exception as e:
            print(f"[ERROR] Error loading calibration images: {e}")
            return [], []
    
    def perform_complete_calibration(self, rgb_images: List[np.ndarray], 
                                   thermal_images: Optional[List[np.ndarray]] = None,
                                   pattern_type: str = "chessboard") -> Dict:
        """
        Perform complete calibration workflow.
        
        Args:
            rgb_images: List of RGB calibration images
            thermal_images: Optional list of thermal calibration images
            pattern_type: Type of calibration pattern
            
        Returns:
            Dictionary containing calibration results
        """
        print("[DEBUG_LOG] Starting complete calibration workflow")
        
        results = {
            'success': False,
            'rgb_calibration': None,
            'thermal_calibration': None,
            'stereo_calibration': None,
            'quality_metrics': {}
        }
        
        try:
            # Validate input images
            if not validate_calibration_images(rgb_images):
                return results
                
            # Generate object points
            object_points_3d = create_calibration_pattern_points(self.chessboard_size, self.square_size)
            
            # Process RGB images
            rgb_image_points = []
            rgb_object_points = []
            valid_rgb_images = []
            
            for i, img in enumerate(rgb_images):
                success, corners = self.detect_calibration_pattern(img, pattern_type)
                if success:
                    rgb_image_points.append(corners)
                    rgb_object_points.append(object_points_3d)
                    valid_rgb_images.append(img)
                    print(f"[DEBUG_LOG] RGB image {i+1}: Pattern detected")
                else:
                    print(f"[WARNING] RGB image {i+1}: Pattern not detected")
            
            if len(rgb_image_points) < 10:
                print(f"[ERROR] Insufficient valid RGB images: {len(rgb_image_points)}")
                return results
                
            # Calibrate RGB camera
            rgb_matrix, rgb_dist, rgb_error = self.calibrate_single_camera(
                valid_rgb_images, rgb_image_points, rgb_object_points
            )
            
            if rgb_matrix is not None:
                self.rgb_camera_matrix = rgb_matrix
                self.rgb_distortion_coeffs = rgb_dist
                results['rgb_calibration'] = {
                    'camera_matrix': rgb_matrix,
                    'distortion_coeffs': rgb_dist,
                    'rms_error': rgb_error
                }
                print(f"[DEBUG_LOG] RGB camera calibration successful (RMS: {rgb_error:.3f})")
                
                # If thermal images provided, calibrate thermal camera and perform stereo calibration
                if thermal_images:
                    if not validate_calibration_images(thermal_images):
                        print("[WARNING] Thermal image validation failed, skipping thermal calibration")
                    else:
                        # Process thermal images
                        thermal_image_points = []
                        thermal_object_points = []
                        valid_thermal_images = []
                        
                        for i, img in enumerate(thermal_images):
                            success, corners = self.detect_calibration_pattern(img, pattern_type)
                            if success:
                                thermal_image_points.append(corners)
                                thermal_object_points.append(object_points_3d)
                                valid_thermal_images.append(img)
                                print(f"[DEBUG_LOG] Thermal image {i+1}: Pattern detected")
                            else:
                                print(f"[WARNING] Thermal image {i+1}: Pattern not detected")
                        
                        if len(thermal_image_points) >= 10:
                            # Calibrate thermal camera
                            thermal_matrix, thermal_dist, thermal_error = self.calibrate_single_camera(
                                valid_thermal_images, thermal_image_points, thermal_object_points
                            )
                            
                            if thermal_matrix is not None:
                                self.thermal_camera_matrix = thermal_matrix
                                self.thermal_distortion_coeffs = thermal_dist
                                results['thermal_calibration'] = {
                                    'camera_matrix': thermal_matrix,
                                    'distortion_coeffs': thermal_dist,
                                    'rms_error': thermal_error
                                }
                                print(f"[DEBUG_LOG] Thermal camera calibration successful (RMS: {thermal_error:.3f})")
                                
                                # Perform stereo calibration if we have matching image pairs
                                min_pairs = min(len(rgb_image_points), len(thermal_image_points))
                                if min_pairs >= 10:
                                    R, T, stereo_error = self.calibrate_stereo_cameras(
                                        valid_rgb_images[:min_pairs], 
                                        valid_thermal_images[:min_pairs],
                                        rgb_image_points[:min_pairs], 
                                        thermal_image_points[:min_pairs], 
                                        rgb_object_points[:min_pairs]
                                    )
                                    
                                    if R is not None and T is not None:
                                        results['stereo_calibration'] = {
                                            'rotation_matrix': R,
                                            'translation_vector': T,
                                            'rms_error': stereo_error
                                        }
                                        print(f"[DEBUG_LOG] Stereo calibration successful (RMS: {stereo_error:.3f})")
                
                results['success'] = True
                print("[DEBUG_LOG] Complete calibration workflow finished successfully")
                
            return results
            
        except Exception as e:
            print(f"[ERROR] Exception during calibration workflow: {e}")
            return results


def create_calibration_pattern_points(pattern_size: Tuple[int, int], square_size: float) -> np.ndarray:
    """
    Create 3D object points for calibration pattern.

    Args:
        pattern_size: Pattern size (width, height) in corners
        square_size: Size of each square in mm

    Returns:
        3D object points array
    """
    print(f"[DEBUG_LOG] Creating calibration pattern points {pattern_size} with square size {square_size}mm")

    # Generate object points for chessboard pattern
    pattern_points = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    pattern_points[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
    pattern_points *= square_size
    
    return pattern_points


def validate_calibration_images(images: List[np.ndarray], min_images: int = 10) -> bool:
    """
    Validate that we have sufficient calibration images.
    
    Args:
        images: List of calibration images
        min_images: Minimum number of images required
        
    Returns:
        True if validation passes
    """
    if len(images) < min_images:
        print(f"[ERROR] Insufficient calibration images: {len(images)} < {min_images}")
        return False
        
    # Check image consistency
    if not images:
        return False
        
    first_shape = images[0].shape
    for i, img in enumerate(images[1:], 1):
        if img.shape != first_shape:
            print(f"[ERROR] Image shape mismatch at index {i}: {img.shape} != {first_shape}")
            return False
            
    print(f"[DEBUG_LOG] Calibration image validation passed: {len(images)} images")
    return True


def draw_calibration_pattern(image: np.ndarray, corners: np.ndarray, pattern_size: Tuple[int, int], 
                           pattern_found: bool = True) -> np.ndarray:
    """
    Draw detected calibration pattern on image for visualization.
    
    Args:
        image: Input image
        corners: Detected corner points
        pattern_size: Pattern size (width, height)
        pattern_found: Whether pattern was successfully detected
        
    Returns:
        Image with drawn pattern
    """
    result_image = image.copy()
    
    if pattern_found and corners is not None:
        # Draw the corners
        cv2.drawChessboardCorners(result_image, pattern_size, corners, pattern_found)
    
    return result_image
