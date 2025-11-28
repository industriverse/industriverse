/**
 * MediaPipe Hands Controller for Gesture-Free Capsule Selection
 * 
 * Implements "Magic Hand" interaction:
 * - Point at capsule → highlight
 * - Pinch fingers → select
 * - Open palm → dismiss
 * 
 * Based on production patterns from:
 * - https://tympanus.net/codrops/2024/10/24/creating-a-3d-hand-controller-using-a-webcam-with-mediapipe-and-three-js/
 * - https://mediapipe.readthedocs.io/en/latest/solutions/hands.html
 */

import * as THREE from 'three';
import { Hands, Results as HandsResults } from '@mediapipe/hands';
import { Camera } from '@mediapipe/camera_utils';

// ============================================================================
// Types
// ============================================================================

export interface MediaPipeHandsConfig {
  videoElement: HTMLVideoElement;
  scene: THREE.Scene;
  camera: THREE.Camera;
  onHandDetected?: (hand: HandData) => void;
  onGesture?: (gesture: GestureData) => void;
  onCapsuleSelect?: (capsule: any) => void;
  onCapsuleDismiss?: (capsule: any) => void;
  maxNumHands?: number;
  modelComplexity?: 0 | 1;
  minDetectionConfidence?: number;
  minTrackingConfidence?: number;
  enableDepthControl?: boolean;
  enableGestureRecognition?: boolean;
}

export interface HandData {
  landmarks: THREE.Vector3[];
  worldLandmarks: THREE.Vector3[];
  handedness: 'Left' | 'Right';
  cursorPosition: THREE.Vector3;
  depthZ: number;
}

export interface GestureData {
  type: 'pinch' | 'open_palm' | 'closed_fist' | 'point' | 'thumbs_up' | 'none';
  confidence: number;
  hand: 'Left' | 'Right';
}

// ============================================================================
// MediaPipe Hand Landmarks (21 points)
// ============================================================================

export enum HandLandmark {
  WRIST = 0,
  THUMB_CMC = 1,
  THUMB_MCP = 2,
  THUMB_IP = 3,
  THUMB_TIP = 4,
  INDEX_FINGER_MCP = 5,
  INDEX_FINGER_PIP = 6,
  INDEX_FINGER_DIP = 7,
  INDEX_FINGER_TIP = 8,
  MIDDLE_FINGER_MCP = 9,
  MIDDLE_FINGER_PIP = 10,
  MIDDLE_FINGER_DIP = 11,
  MIDDLE_FINGER_TIP = 12,
  RING_FINGER_MCP = 13,
  RING_FINGER_PIP = 14,
  RING_FINGER_DIP = 15,
  RING_FINGER_TIP = 16,
  PINKY_MCP = 17,
  PINKY_PIP = 18,
  PINKY_DIP = 19,
  PINKY_TIP = 20
}

// ============================================================================
// MediaPipeHandsController
// ============================================================================

export default class MediaPipeHandsController {
  private config: Required<MediaPipeHandsConfig>;
  private hands: Hands;
  private camera: Camera;
  private handData: HandData | null = null;
  private currentGesture: GestureData | null = null;

  // 3D cursor for hand position
  private cursor: THREE.Mesh;
  private cursorBox: THREE.Box3;

  // Reference objects for depth calculation
  private refObjFrom: THREE.Object3D;
  private refObjTo: THREE.Object3D;
  private depthPointA: THREE.Vector2;
  private depthPointB: THREE.Vector2;
  private depthZ: number = 0;

  // Raycaster for capsule selection
  private raycaster: THREE.Raycaster;
  private selectedCapsule: any = null;

  // Performance tracking
  private lastFrameTime: number = 0;
  private fps: number = 0;

  constructor(config: MediaPipeHandsConfig) {
    this.config = {
      maxNumHands: config.maxNumHands ?? 1,
      modelComplexity: config.modelComplexity ?? 1,
      minDetectionConfidence: config.minDetectionConfidence ?? 0.7,
      minTrackingConfidence: config.minTrackingConfidence ?? 0.7,
      enableDepthControl: config.enableDepthControl ?? true,
      enableGestureRecognition: config.enableGestureRecognition ?? true,
      ...config
    } as any;

    // Initialize MediaPipe Hands
    this.hands = new Hands({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
      }
    });

    this.hands.setOptions({
      maxNumHands: this.config.maxNumHands,
      modelComplexity: this.config.modelComplexity,
      minDetectionConfidence: this.config.minDetectionConfidence,
      minTrackingConfidence: this.config.minTrackingConfidence
    });

    this.hands.onResults((results) => this.onResults(results));

    // Initialize camera
    this.camera = new Camera(this.config.videoElement, {
      onFrame: async () => {
        await this.hands.send({ image: this.config.videoElement });
      },
      width: 1280,
      height: 720
    });

    // Create 3D cursor
    this.cursor = this.createCursor();
    this.config.scene.add(this.cursor);
    this.cursorBox = new THREE.Box3();

    // Create reference objects for depth calculation
    this.refObjFrom = new THREE.Object3D();
    this.refObjTo = new THREE.Object3D();
    this.depthPointA = new THREE.Vector2();
    this.depthPointB = new THREE.Vector2();

    // Initialize raycaster
    this.raycaster = new THREE.Raycaster();
  }

  /**
   * Start hand tracking
   */
  start(): void {
    this.camera.start();
  }

  /**
   * Stop hand tracking
   */
  stop(): void {
    this.camera.stop();
  }

  /**
   * Create 3D cursor mesh
   */
  private createCursor(): THREE.Mesh {
    const geometry = new THREE.SphereGeometry(0.05, 32, 32);
    const material = new THREE.MeshStandardMaterial({
      color: 0x00d4ff,
      emissive: 0x00d4ff,
      emissiveIntensity: 0.5,
      transparent: true,
      opacity: 0.8
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.visible = false;

    return mesh;
  }

  /**
   * Process MediaPipe Hands results
   */
  private onResults(results: HandsResults): void {
    // Calculate FPS
    const now = performance.now();
    if (this.lastFrameTime > 0) {
      this.fps = 1000 / (now - this.lastFrameTime);
    }
    this.lastFrameTime = now;

    // No hands detected
    if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
      this.cursor.visible = false;
      this.handData = null;
      this.currentGesture = null;
      return;
    }

    // Process first hand
    const landmarks = results.multiHandLandmarks[0];
    const worldLandmarks = results.multiHandWorldLandmarks?.[0];
    const handedness = results.multiHandedness?.[0]?.label as 'Left' | 'Right' || 'Right';

    // Convert landmarks to Three.js Vector3
    const landmarks3D = this.convertLandmarksToVector3(landmarks);
    const worldLandmarks3D = worldLandmarks ? this.convertWorldLandmarksToVector3(worldLandmarks) : [];

    // Calculate cursor position (using MIDDLE_FINGER_MCP as center point)
    const centerPoint = landmarks3D[HandLandmark.MIDDLE_FINGER_MCP];

    // Calculate depth (2D to 3D conversion)
    if (this.config.enableDepthControl) {
      this.depthZ = this.calculateDepth(landmarks3D);
    }

    // Update cursor position
    this.cursor.position.set(
      centerPoint.x,
      centerPoint.y,
      -this.depthZ
    );
    this.cursor.visible = true;

    // Update hand data
    this.handData = {
      landmarks: landmarks3D,
      worldLandmarks: worldLandmarks3D,
      handedness,
      cursorPosition: this.cursor.position.clone(),
      depthZ: this.depthZ
    };

    // Emit hand detected event
    if (this.config.onHandDetected) {
      this.config.onHandDetected(this.handData);
    }

    // Gesture recognition
    if (this.config.enableGestureRecognition) {
      this.currentGesture = this.recognizeGesture(landmarks3D, handedness);

      if (this.currentGesture && this.config.onGesture) {
        this.config.onGesture(this.currentGesture);
      }

      // Handle capsule interaction
      this.handleCapsuleInteraction();
    }
  }

  /**
   * Convert MediaPipe landmarks to Three.js Vector3
   */
  private convertLandmarksToVector3(landmarks: any[]): THREE.Vector3[] {
    return landmarks.map((landmark) => {
      return new THREE.Vector3(
        -landmark.x + 0.5,  // Invert X, center at 0
        -landmark.y + 0.5,  // Invert Y, center at 0
        -landmark.z          // Invert Z for correct depth
      ).multiplyScalar(4);  // Scale to world space
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
   * Calculate depth using 2D distance between two landmarks
   * 
   * Pattern from: https://tympanus.net/codrops/2024/10/24/creating-a-3d-hand-controller-using-a-webcam-with-mediapipe-and-three-js/
   */
  private calculateDepth(landmarks: THREE.Vector3[]): number {
    // Use WRIST and MIDDLE_FINGER_PIP as reference points
    const wrist = landmarks[HandLandmark.WRIST];
    const middleFinger = landmarks[HandLandmark.MIDDLE_FINGER_PIP];

    // Convert 3D positions to 2D screen space
    this.refObjFrom.position.copy(wrist);
    const depthA = this.to2D(this.refObjFrom);
    this.depthPointA.set(depthA.x, depthA.y);

    this.refObjTo.position.copy(middleFinger);
    const depthB = this.to2D(this.refObjTo);
    this.depthPointB.set(depthB.x, depthB.y);

    // Calculate 2D distance
    const depthDistance = this.depthPointA.distanceTo(this.depthPointB);

    // Map to 3D depth range (-2 to 4)
    const depth = THREE.MathUtils.clamp(
      THREE.MathUtils.mapLinear(depthDistance, 0, 1000, -3, 5),
      -2,
      4
    );

    return depth;
  }

  /**
   * Convert 3D position to 2D screen space
   */
  private to2D(object: THREE.Object3D): THREE.Vector2 {
    const vector = object.position.clone();
    vector.project(this.config.camera);

    return new THREE.Vector2(
      (vector.x + 1) / 2 * window.innerWidth,
      -(vector.y - 1) / 2 * window.innerHeight
    );
  }

  /**
   * Recognize hand gesture
   */
  private recognizeGesture(landmarks: THREE.Vector3[], handedness: 'Left' | 'Right'): GestureData {
    // Pinch gesture (thumb tip + index finger tip distance)
    const thumbTip = landmarks[HandLandmark.THUMB_TIP];
    const indexTip = landmarks[HandLandmark.INDEX_FINGER_TIP];
    const pinchDistance = thumbTip.distanceTo(indexTip);

    if (pinchDistance < 0.3) {
      return {
        type: 'pinch',
        confidence: THREE.MathUtils.mapLinear(pinchDistance, 0, 0.3, 1, 0),
        hand: handedness
      };
    }

    // Closed fist gesture (middle finger base + tip distance)
    const fingerBase = landmarks[HandLandmark.MIDDLE_FINGER_MCP];
    const fingerTip = landmarks[HandLandmark.MIDDLE_FINGER_TIP];
    const fistDistance = fingerBase.distanceTo(fingerTip);

    if (fistDistance < 0.35) {
      return {
        type: 'closed_fist',
        confidence: THREE.MathUtils.mapLinear(fistDistance, 0, 0.35, 1, 0),
        hand: handedness
      };
    }

    // Open palm gesture (all fingers extended)
    const wrist = landmarks[HandLandmark.WRIST];
    const middleTip = landmarks[HandLandmark.MIDDLE_FINGER_TIP];
    const palmDistance = wrist.distanceTo(middleTip);

    if (palmDistance > 1.2) {
      return {
        type: 'open_palm',
        confidence: THREE.MathUtils.mapLinear(palmDistance, 1.2, 2, 0, 1),
        hand: handedness
      };
    }

    // Point gesture (index finger extended, others closed)
    const indexMCP = landmarks[HandLandmark.INDEX_FINGER_MCP];
    const indexExtension = indexTip.distanceTo(indexMCP);
    const middleExtension = fingerTip.distanceTo(fingerBase);

    if (indexExtension > 0.8 && middleExtension < 0.5) {
      return {
        type: 'point',
        confidence: 0.8,
        hand: handedness
      };
    }

    // Thumbs up gesture (thumb extended upward)
    const thumbMCP = landmarks[HandLandmark.THUMB_MCP];
    const thumbExtension = thumbTip.y - thumbMCP.y;

    if (thumbExtension > 0.5 && fistDistance < 0.5) {
      return {
        type: 'thumbs_up',
        confidence: 0.8,
        hand: handedness
      };
    }

    return {
      type: 'none',
      confidence: 0,
      hand: handedness
    };
  }

  /**
   * Handle capsule interaction based on gesture
   */
  private handleCapsuleInteraction(): void {
    if (!this.currentGesture) return;

    // Update cursor box for collision detection
    this.cursorBox.setFromObject(this.cursor);

    // Find capsules in scene
    const capsules = this.findCapsulesInScene();

    // Check for collision
    let hoveredCapsule: any = null;

    for (const capsule of capsules) {
      const capsuleBox = new THREE.Box3().setFromObject(capsule);

      if (this.cursorBox.intersectsBox(capsuleBox)) {
        hoveredCapsule = capsule;
        break;
      }
    }

    // Handle gestures
    if (this.currentGesture.type === 'pinch' && hoveredCapsule) {
      // Select capsule
      if (this.selectedCapsule !== hoveredCapsule) {
        this.selectedCapsule = hoveredCapsule;

        if (this.config.onCapsuleSelect) {
          this.config.onCapsuleSelect(hoveredCapsule);
        }
      }
    } else if (this.currentGesture.type === 'open_palm' && this.selectedCapsule) {
      // Dismiss capsule
      if (this.config.onCapsuleDismiss) {
        this.config.onCapsuleDismiss(this.selectedCapsule);
      }

      this.selectedCapsule = null;
    }
  }

  /**
   * Find all capsule overlays in scene
   */
  private findCapsulesInScene(): THREE.Object3D[] {
    const capsules: THREE.Object3D[] = [];

    this.config.scene.traverse((object) => {
      if (object.userData.type === 'capsule_overlay') {
        capsules.push(object);
      }
    });

    return capsules;
  }

  /**
   * Get current hand data
   */
  getHandData(): HandData | null {
    return this.handData;
  }

  /**
   * Get current gesture
   */
  getCurrentGesture(): GestureData | null {
    return this.currentGesture;
  }

  /**
   * Get current FPS
   */
  getFPS(): number {
    return this.fps;
  }

  /**
   * Get selected capsule
   */
  getSelectedCapsule(): any {
    return this.selectedCapsule;
  }

  /**
   * Dispose controller
   */
  dispose(): void {
    this.stop();
    this.config.scene.remove(this.cursor);
    this.cursor.geometry.dispose();
    (this.cursor.material as THREE.Material).dispose();
  }
}
