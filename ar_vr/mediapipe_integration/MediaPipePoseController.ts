/**
 * MediaPipe Pose Controller for Body Language Commands
 * 
 * Implements pose-based capsule actions:
 * - Thumbs up → Acknowledge capsule
 * - Wave hand → Dismiss capsule
 * - Point at object → Select capsule
 * 
 * Based on production patterns from:
 * - https://mediapipe.readthedocs.io/en/latest/solutions/pose.html
 * - https://github.com/torinmb/mediapipe-touchdesigner
 */

import * as THREE from 'three';
import { Pose, Results as PoseResults } from '@mediapipe/pose';
import { Camera } from '@mediapipe/camera_utils';

// ============================================================================
// Types
// ============================================================================

export interface MediaPipePoseConfig {
  videoElement: HTMLVideoElement;
  onPoseDetected?: (pose: PoseData) => void;
  onBodyLanguage?: (command: BodyLanguageCommand) => void;
  modelComplexity?: 0 | 1 | 2;
  smoothLandmarks?: boolean;
  minDetectionConfidence?: number;
  minTrackingConfidence?: number;
  enableBodyLanguageRecognition?: boolean;
}

export interface PoseData {
  landmarks: THREE.Vector3[];
  worldLandmarks: THREE.Vector3[];
  posture: PostureType;
  ergonomicRisk: ErgonomicRisk;
}

export interface BodyLanguageCommand {
  type: 'thumbs_up' | 'wave_hand' | 'point_at_object' | 'crossed_arms' | 'hands_on_hips' | 'none';
  confidence: number;
  side: 'left' | 'right' | 'both';
}

export type PostureType = 'standing' | 'sitting' | 'bending' | 'reaching' | 'crouching' | 'unknown';

export interface ErgonomicRisk {
  rebaScore: number;  // Rapid Entire Body Assessment (1-15)
  rulaScore: number;  // Rapid Upper Limb Assessment (1-7)
  riskLevel: 'low' | 'medium' | 'high' | 'very_high';
}

// ============================================================================
// MediaPipe Pose Landmarks (33 points)
// ============================================================================

export enum PoseLandmark {
  NOSE = 0,
  LEFT_EYE_INNER = 1,
  LEFT_EYE = 2,
  LEFT_EYE_OUTER = 3,
  RIGHT_EYE_INNER = 4,
  RIGHT_EYE = 5,
  RIGHT_EYE_OUTER = 6,
  LEFT_EAR = 7,
  RIGHT_EAR = 8,
  MOUTH_LEFT = 9,
  MOUTH_RIGHT = 10,
  LEFT_SHOULDER = 11,
  RIGHT_SHOULDER = 12,
  LEFT_ELBOW = 13,
  RIGHT_ELBOW = 14,
  LEFT_WRIST = 15,
  RIGHT_WRIST = 16,
  LEFT_PINKY = 17,
  RIGHT_PINKY = 18,
  LEFT_INDEX = 19,
  RIGHT_INDEX = 20,
  LEFT_THUMB = 21,
  RIGHT_THUMB = 22,
  LEFT_HIP = 23,
  RIGHT_HIP = 24,
  LEFT_KNEE = 25,
  RIGHT_KNEE = 26,
  LEFT_ANKLE = 27,
  RIGHT_ANKLE = 28,
  LEFT_HEEL = 29,
  RIGHT_HEEL = 30,
  LEFT_FOOT_INDEX = 31,
  RIGHT_FOOT_INDEX = 32
}

// ============================================================================
// MediaPipePoseController
// ============================================================================

export default class MediaPipePoseController {
  private config: Required<MediaPipePoseConfig>;
  private pose: Pose;
  private camera: Camera;
  private poseData: PoseData | null = null;
  private currentCommand: BodyLanguageCommand | null = null;
  
  // Performance tracking
  private lastFrameTime: number = 0;
  private fps: number = 0;
  
  // Command debouncing
  private lastCommandTime: number = 0;
  private commandCooldown: number = 1000; // 1 second
  
  constructor(config: MediaPipePoseConfig) {
    this.config = {
      modelComplexity: config.modelComplexity ?? 1,
      smoothLandmarks: config.smoothLandmarks ?? true,
      minDetectionConfidence: config.minDetectionConfidence ?? 0.5,
      minTrackingConfidence: config.minTrackingConfidence ?? 0.5,
      enableBodyLanguageRecognition: config.enableBodyLanguageRecognition ?? true,
      ...config
    };
    
    // Initialize MediaPipe Pose
    this.pose = new Pose({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
      }
    });
    
    this.pose.setOptions({
      modelComplexity: this.config.modelComplexity,
      smoothLandmarks: this.config.smoothLandmarks,
      minDetectionConfidence: this.config.minDetectionConfidence,
      minTrackingConfidence: this.config.minTrackingConfidence
    });
    
    this.pose.onResults((results) => this.onResults(results));
    
    // Initialize camera
    this.camera = new Camera(this.config.videoElement, {
      onFrame: async () => {
        await this.pose.send({ image: this.config.videoElement });
      },
      width: 1280,
      height: 720
    });
  }
  
  /**
   * Start pose tracking
   */
  start(): void {
    this.camera.start();
  }
  
  /**
   * Stop pose tracking
   */
  stop(): void {
    this.camera.stop();
  }
  
  /**
   * Process MediaPipe Pose results
   */
  private onResults(results: PoseResults): void {
    // Calculate FPS
    const now = performance.now();
    if (this.lastFrameTime > 0) {
      this.fps = 1000 / (now - this.lastFrameTime);
    }
    this.lastFrameTime = now;
    
    // No pose detected
    if (!results.poseLandmarks) {
      this.poseData = null;
      this.currentCommand = null;
      return;
    }
    
    // Convert landmarks to Three.js Vector3
    const landmarks = this.convertLandmarksToVector3(results.poseLandmarks);
    const worldLandmarks = results.poseWorldLandmarks 
      ? this.convertWorldLandmarksToVector3(results.poseWorldLandmarks)
      : [];
    
    // Classify posture
    const posture = this.classifyPosture(landmarks);
    
    // Calculate ergonomic risk
    const ergonomicRisk = this.calculateErgonomicRisk(landmarks);
    
    // Update pose data
    this.poseData = {
      landmarks,
      worldLandmarks,
      posture,
      ergonomicRisk
    };
    
    // Emit pose detected event
    if (this.config.onPoseDetected) {
      this.config.onPoseDetected(this.poseData);
    }
    
    // Body language recognition
    if (this.config.enableBodyLanguageRecognition) {
      this.currentCommand = this.recognizeBodyLanguage(landmarks);
      
      // Emit command (with debouncing)
      if (this.currentCommand && this.currentCommand.type !== 'none') {
        const timeSinceLastCommand = now - this.lastCommandTime;
        
        if (timeSinceLastCommand > this.commandCooldown) {
          if (this.config.onBodyLanguage) {
            this.config.onBodyLanguage(this.currentCommand);
          }
          
          this.lastCommandTime = now;
        }
      }
    }
  }
  
  /**
   * Convert MediaPipe landmarks to Three.js Vector3
   */
  private convertLandmarksToVector3(landmarks: any[]): THREE.Vector3[] {
    return landmarks.map((landmark) => {
      return new THREE.Vector3(
        landmark.x,
        landmark.y,
        landmark.z
      );
    });
  }
  
  /**
   * Convert MediaPipe world landmarks to Three.js Vector3
   */
  private convertWorldLandmarksToVector3(landmarks: any[]): THREE.Vector3[] {
    return landmarks.map((landmark) => {
      return new THREE.Vector3(
        landmark.x,
        landmark.y,
        landmark.z
      );
    });
  }
  
  /**
   * Classify body posture
   */
  private classifyPosture(landmarks: THREE.Vector3[]): PostureType {
    const nose = landmarks[PoseLandmark.NOSE];
    const leftHip = landmarks[PoseLandmark.LEFT_HIP];
    const rightHip = landmarks[PoseLandmark.RIGHT_HIP];
    const leftKnee = landmarks[PoseLandmark.LEFT_KNEE];
    const rightKnee = landmarks[PoseLandmark.RIGHT_KNEE];
    const leftAnkle = landmarks[PoseLandmark.LEFT_ANKLE];
    const rightAnkle = landmarks[PoseLandmark.RIGHT_ANKLE];
    
    // Calculate hip center
    const hipCenter = new THREE.Vector3().addVectors(leftHip, rightHip).multiplyScalar(0.5);
    
    // Calculate knee center
    const kneeCenter = new THREE.Vector3().addVectors(leftKnee, rightKnee).multiplyScalar(0.5);
    
    // Calculate ankle center
    const ankleCenter = new THREE.Vector3().addVectors(leftAnkle, rightAnkle).multiplyScalar(0.5);
    
    // Torso angle (nose to hip)
    const torsoAngle = Math.abs(nose.y - hipCenter.y);
    
    // Leg angle (hip to ankle)
    const legAngle = Math.abs(hipCenter.y - ankleCenter.y);
    
    // Knee bend (hip to knee to ankle)
    const kneeBend = Math.abs(hipCenter.y - kneeCenter.y) / Math.abs(kneeCenter.y - ankleCenter.y);
    
    // Classify posture
    if (torsoAngle < 0.3) {
      return 'bending';
    } else if (kneeBend < 0.5) {
      return 'crouching';
    } else if (legAngle > 0.6) {
      return 'standing';
    } else if (legAngle < 0.4) {
      return 'sitting';
    } else {
      return 'unknown';
    }
  }
  
  /**
   * Calculate ergonomic risk (REBA/RULA scores)
   */
  private calculateErgonomicRisk(landmarks: THREE.Vector3[]): ErgonomicRisk {
    // Simplified REBA/RULA calculation
    // In production, use full REBA/RULA assessment algorithms
    
    const nose = landmarks[PoseLandmark.NOSE];
    const leftShoulder = landmarks[PoseLandmark.LEFT_SHOULDER];
    const rightShoulder = landmarks[PoseLandmark.RIGHT_SHOULDER];
    const leftElbow = landmarks[PoseLandmark.LEFT_ELBOW];
    const rightElbow = landmarks[PoseLandmark.RIGHT_ELBOW];
    const leftHip = landmarks[PoseLandmark.LEFT_HIP];
    const rightHip = landmarks[PoseLandmark.RIGHT_HIP];
    
    // Calculate shoulder center
    const shoulderCenter = new THREE.Vector3().addVectors(leftShoulder, rightShoulder).multiplyScalar(0.5);
    
    // Calculate hip center
    const hipCenter = new THREE.Vector3().addVectors(leftHip, rightHip).multiplyScalar(0.5);
    
    // Neck angle (nose to shoulder)
    const neckAngle = Math.abs(nose.y - shoulderCenter.y);
    
    // Trunk angle (shoulder to hip)
    const trunkAngle = Math.abs(shoulderCenter.y - hipCenter.y);
    
    // Arm elevation (shoulder to elbow)
    const leftArmElevation = Math.abs(leftShoulder.y - leftElbow.y);
    const rightArmElevation = Math.abs(rightShoulder.y - rightElbow.y);
    const maxArmElevation = Math.max(leftArmElevation, rightArmElevation);
    
    // Calculate REBA score (1-15)
    let rebaScore = 1;
    
    if (neckAngle < 0.1) rebaScore += 2;  // Neck flexion
    if (trunkAngle < 0.4) rebaScore += 3;  // Trunk flexion
    if (maxArmElevation > 0.3) rebaScore += 2;  // Arm elevation
    
    // Calculate RULA score (1-7)
    let rulaScore = 1;
    
    if (neckAngle < 0.1) rulaScore += 1;
    if (maxArmElevation > 0.3) rulaScore += 2;
    
    // Determine risk level
    let riskLevel: 'low' | 'medium' | 'high' | 'very_high';
    
    if (rebaScore <= 3) {
      riskLevel = 'low';
    } else if (rebaScore <= 7) {
      riskLevel = 'medium';
    } else if (rebaScore <= 10) {
      riskLevel = 'high';
    } else {
      riskLevel = 'very_high';
    }
    
    return {
      rebaScore,
      rulaScore,
      riskLevel
    };
  }
  
  /**
   * Recognize body language command
   */
  private recognizeBodyLanguage(landmarks: THREE.Vector3[]): BodyLanguageCommand {
    // Thumbs up (thumb extended upward, fist closed)
    const leftThumb = landmarks[PoseLandmark.LEFT_THUMB];
    const rightThumb = landmarks[PoseLandmark.RIGHT_THUMB];
    const leftWrist = landmarks[PoseLandmark.LEFT_WRIST];
    const rightWrist = landmarks[PoseLandmark.RIGHT_WRIST];
    const leftShoulder = landmarks[PoseLandmark.LEFT_SHOULDER];
    const rightShoulder = landmarks[PoseLandmark.RIGHT_SHOULDER];
    
    // Left thumbs up
    if (leftThumb.y < leftWrist.y && leftThumb.y < leftShoulder.y) {
      return {
        type: 'thumbs_up',
        confidence: 0.8,
        side: 'left'
      };
    }
    
    // Right thumbs up
    if (rightThumb.y < rightWrist.y && rightThumb.y < rightShoulder.y) {
      return {
        type: 'thumbs_up',
        confidence: 0.8,
        side: 'right'
      };
    }
    
    // Wave hand (wrist moving side to side)
    const leftWristX = leftWrist.x;
    const rightWristX = rightWrist.x;
    
    // Simplified wave detection (in production, track wrist movement over time)
    if (Math.abs(leftWristX - leftShoulder.x) > 0.3) {
      return {
        type: 'wave_hand',
        confidence: 0.7,
        side: 'left'
      };
    }
    
    if (Math.abs(rightWristX - rightShoulder.x) > 0.3) {
      return {
        type: 'wave_hand',
        confidence: 0.7,
        side: 'right'
      };
    }
    
    // Point at object (index finger extended)
    const leftIndex = landmarks[PoseLandmark.LEFT_INDEX];
    const rightIndex = landmarks[PoseLandmark.RIGHT_INDEX];
    
    const leftPointDistance = leftIndex.distanceTo(leftWrist);
    const rightPointDistance = rightIndex.distanceTo(rightWrist);
    
    if (leftPointDistance > 0.2) {
      return {
        type: 'point_at_object',
        confidence: 0.8,
        side: 'left'
      };
    }
    
    if (rightPointDistance > 0.2) {
      return {
        type: 'point_at_object',
        confidence: 0.8,
        side: 'right'
      };
    }
    
    // Crossed arms (wrists crossed in front of chest)
    const wristDistance = leftWrist.distanceTo(rightWrist);
    const shoulderDistance = leftShoulder.distanceTo(rightShoulder);
    
    if (wristDistance < shoulderDistance * 0.5) {
      return {
        type: 'crossed_arms',
        confidence: 0.7,
        side: 'both'
      };
    }
    
    // Hands on hips (wrists near hips)
    const leftHip = landmarks[PoseLandmark.LEFT_HIP];
    const rightHip = landmarks[PoseLandmark.RIGHT_HIP];
    
    const leftWristToHip = leftWrist.distanceTo(leftHip);
    const rightWristToHip = rightWrist.distanceTo(rightHip);
    
    if (leftWristToHip < 0.2 && rightWristToHip < 0.2) {
      return {
        type: 'hands_on_hips',
        confidence: 0.7,
        side: 'both'
      };
    }
    
    return {
      type: 'none',
      confidence: 0,
      side: 'both'
    };
  }
  
  /**
   * Get current pose data
   */
  getPoseData(): PoseData | null {
    return this.poseData;
  }
  
  /**
   * Get current body language command
   */
  getCurrentCommand(): BodyLanguageCommand | null {
    return this.currentCommand;
  }
  
  /**
   * Get current FPS
   */
  getFPS(): number {
    return this.fps;
  }
  
  /**
   * Dispose controller
   */
  dispose(): void {
    this.stop();
  }
}
