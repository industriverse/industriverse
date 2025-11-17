/**
 * AR/VR Interaction Controller
 * 
 * Handles multi-platform interaction for capsule selection and manipulation:
 * - Mobile AR: Touch gestures (tap, long press, pinch, swipe)
 * - VR Headsets: Controller input (gaze + trigger, ray pointing, hand tracking)
 * - Voice Commands: Speech recognition for hands-free interaction
 * - Spatial Anchoring: Persist capsule positions across sessions
 * 
 * Platform Support:
 * - iOS ARKit (iPhone 12+)
 * - Android ARCore (Android 7+)
 * - Meta Quest 2/3/Pro
 * - Apple Vision Pro
 * - HTC Vive
 * 
 * Dependencies:
 * - WebXR Device API
 * - Web Speech API
 * - Three.js
 */

import * as THREE from 'three';

// ============================================================================
// Type Definitions
// ============================================================================

export interface ARVRInteractionConfig {
  /** Three.js scene */
  scene: THREE.Scene;
  
  /** Three.js camera */
  camera: THREE.Camera;
  
  /** Three.js renderer */
  renderer: THREE.WebGLRenderer;
  
  /** Enable AR mode */
  enableAR?: boolean;
  
  /** Enable VR mode */
  enableVR?: boolean;
  
  /** Enable voice commands */
  enableVoice?: boolean;
  
  /** Enable spatial anchoring */
  enableAnchoring?: boolean;
  
  /** Interaction callbacks */
  onCapsuleSelect?: (capsule: any) => void;
  onCapsuleLongPress?: (capsule: any) => void;
  onCapsuleSwipe?: (capsule: any, direction: 'left' | 'right' | 'up' | 'down') => void;
  onVoiceCommand?: (command: string, capsule?: any) => void;
}

export interface GestureState {
  isPressed: boolean;
  pressStartTime: number;
  pressStartPosition: THREE.Vector2;
  currentPosition: THREE.Vector2;
  isPinching: boolean;
  pinchScale: number;
}

export interface VRControllerState {
  controller: THREE.Group;
  grip: THREE.Group;
  targetRaySpace: THREE.XRTargetRaySpace;
  isSelecting: boolean;
  isSqueezing: boolean;
}

// ============================================================================
// AR/VR Interaction Controller
// ============================================================================

export class ARVRInteractionController {
  private config: Required<ARVRInteractionConfig>;
  private raycaster: THREE.Raycaster = new THREE.Raycaster();
  
  // Gesture tracking
  private gestureState: GestureState = {
    isPressed: false,
    pressStartTime: 0,
    pressStartPosition: new THREE.Vector2(),
    currentPosition: new THREE.Vector2(),
    isPinching: false,
    pinchScale: 1.0
  };
  
  // VR controllers
  private vrControllers: VRControllerState[] = [];
  
  // Voice recognition
  private speechRecognition?: SpeechRecognition;
  private isListening: boolean = false;
  
  // Spatial anchors (AR)
  private spatialAnchors: Map<string, XRAnchor> = new Map();
  
  // XR session
  private xrSession?: XRSession;
  private xrReferenceSpace?: XRReferenceSpace;
  
  constructor(config: ARVRInteractionConfig) {
    this.config = {
      scene: config.scene,
      camera: config.camera,
      renderer: config.renderer,
      enableAR: config.enableAR ?? false,
      enableVR: config.enableVR ?? false,
      enableVoice: config.enableVoice ?? false,
      enableAnchoring: config.enableAnchoring ?? false,
      onCapsuleSelect: config.onCapsuleSelect ?? (() => {}),
      onCapsuleLongPress: config.onCapsuleLongPress ?? (() => {}),
      onCapsuleSwipe: config.onCapsuleSwipe ?? (() => {}),
      onVoiceCommand: config.onVoiceCommand ?? (() => {})
    };
    
    this.initialize();
  }
  
  /**
   * Initialize interaction handlers
   */
  private initialize() {
    console.log('Initializing AR/VR Interaction Controller');
    
    // Set up touch/mouse handlers
    this.setupTouchHandlers();
    
    // Set up VR controllers if enabled
    if (this.config.enableVR) {
      this.setupVRControllers();
    }
    
    // Set up voice recognition if enabled
    if (this.config.enableVoice) {
      this.setupVoiceRecognition();
    }
    
    console.log('AR/VR Interaction Controller initialized');
  }
  
  // ==========================================================================
  // Touch/Mouse Interaction (Mobile AR + Desktop)
  // ==========================================================================
  
  /**
   * Set up touch and mouse event handlers
   */
  private setupTouchHandlers() {
    const canvas = this.config.renderer.domElement;
    
    // Mouse events (desktop)
    canvas.addEventListener('mousedown', this.onPointerDown.bind(this));
    canvas.addEventListener('mousemove', this.onPointerMove.bind(this));
    canvas.addEventListener('mouseup', this.onPointerUp.bind(this));
    
    // Touch events (mobile AR)
    canvas.addEventListener('touchstart', this.onTouchStart.bind(this), { passive: false });
    canvas.addEventListener('touchmove', this.onTouchMove.bind(this), { passive: false });
    canvas.addEventListener('touchend', this.onTouchEnd.bind(this), { passive: false });
    
    // Prevent context menu on long press
    canvas.addEventListener('contextmenu', (e) => e.preventDefault());
  }
  
  /**
   * Handle pointer down (mouse/touch start)
   */
  private onPointerDown(event: MouseEvent) {
    this.gestureState.isPressed = true;
    this.gestureState.pressStartTime = Date.now();
    
    const rect = this.config.renderer.domElement.getBoundingClientRect();
    this.gestureState.pressStartPosition.set(
      ((event.clientX - rect.left) / rect.width) * 2 - 1,
      -((event.clientY - rect.top) / rect.height) * 2 + 1
    );
    
    this.gestureState.currentPosition.copy(this.gestureState.pressStartPosition);
  }
  
  /**
   * Handle pointer move
   */
  private onPointerMove(event: MouseEvent) {
    if (!this.gestureState.isPressed) return;
    
    const rect = this.config.renderer.domElement.getBoundingClientRect();
    this.gestureState.currentPosition.set(
      ((event.clientX - rect.left) / rect.width) * 2 - 1,
      -((event.clientY - rect.top) / rect.height) * 2 + 1
    );
  }
  
  /**
   * Handle pointer up (mouse/touch end)
   */
  private onPointerUp(event: MouseEvent) {
    if (!this.gestureState.isPressed) return;
    
    const pressDuration = Date.now() - this.gestureState.pressStartTime;
    const moveDistance = this.gestureState.currentPosition.distanceTo(
      this.gestureState.pressStartPosition
    );
    
    // Determine gesture type
    if (pressDuration > 500 && moveDistance < 0.05) {
      // Long press
      this.handleLongPress(this.gestureState.pressStartPosition);
    } else if (moveDistance > 0.1) {
      // Swipe
      this.handleSwipe(
        this.gestureState.pressStartPosition,
        this.gestureState.currentPosition
      );
    } else {
      // Tap
      this.handleTap(this.gestureState.pressStartPosition);
    }
    
    this.gestureState.isPressed = false;
  }
  
  /**
   * Handle touch start (mobile)
   */
  private onTouchStart(event: TouchEvent) {
    event.preventDefault();
    
    if (event.touches.length === 1) {
      // Single touch - treat as pointer down
      const touch = event.touches[0];
      const mouseEvent = new MouseEvent('mousedown', {
        clientX: touch.clientX,
        clientY: touch.clientY
      });
      this.onPointerDown(mouseEvent);
    } else if (event.touches.length === 2) {
      // Two-finger pinch
      this.gestureState.isPinching = true;
      this.gestureState.pinchScale = this.getTouchDistance(event.touches);
    }
  }
  
  /**
   * Handle touch move (mobile)
   */
  private onTouchMove(event: TouchEvent) {
    event.preventDefault();
    
    if (event.touches.length === 1 && this.gestureState.isPressed) {
      // Single touch move
      const touch = event.touches[0];
      const mouseEvent = new MouseEvent('mousemove', {
        clientX: touch.clientX,
        clientY: touch.clientY
      });
      this.onPointerMove(mouseEvent);
    } else if (event.touches.length === 2 && this.gestureState.isPinching) {
      // Pinch zoom
      const newDistance = this.getTouchDistance(event.touches);
      const scaleChange = newDistance / this.gestureState.pinchScale;
      this.handlePinch(scaleChange);
      this.gestureState.pinchScale = newDistance;
    }
  }
  
  /**
   * Handle touch end (mobile)
   */
  private onTouchEnd(event: TouchEvent) {
    event.preventDefault();
    
    if (event.touches.length === 0) {
      if (this.gestureState.isPinching) {
        this.gestureState.isPinching = false;
      } else if (this.gestureState.isPressed) {
        const touch = event.changedTouches[0];
        const mouseEvent = new MouseEvent('mouseup', {
          clientX: touch.clientX,
          clientY: touch.clientY
        });
        this.onPointerUp(mouseEvent);
      }
    }
  }
  
  /**
   * Get distance between two touch points
   */
  private getTouchDistance(touches: TouchList): number {
    const dx = touches[0].clientX - touches[1].clientX;
    const dy = touches[0].clientY - touches[1].clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }
  
  /**
   * Handle tap gesture
   */
  private handleTap(position: THREE.Vector2) {
    const capsule = this.raycastCapsule(position);
    
    if (capsule) {
      console.log('Tap on capsule:', capsule.id);
      this.config.onCapsuleSelect(capsule);
    }
  }
  
  /**
   * Handle long press gesture
   */
  private handleLongPress(position: THREE.Vector2) {
    const capsule = this.raycastCapsule(position);
    
    if (capsule) {
      console.log('Long press on capsule:', capsule.id);
      this.config.onCapsuleLongPress(capsule);
    }
  }
  
  /**
   * Handle swipe gesture
   */
  private handleSwipe(start: THREE.Vector2, end: THREE.Vector2) {
    const delta = new THREE.Vector2().subVectors(end, start);
    
    let direction: 'left' | 'right' | 'up' | 'down';
    
    if (Math.abs(delta.x) > Math.abs(delta.y)) {
      direction = delta.x > 0 ? 'right' : 'left';
    } else {
      direction = delta.y > 0 ? 'up' : 'down';
    }
    
    const capsule = this.raycastCapsule(start);
    
    if (capsule) {
      console.log(`Swipe ${direction} on capsule:`, capsule.id);
      this.config.onCapsuleSwipe(capsule, direction);
    }
  }
  
  /**
   * Handle pinch gesture (zoom)
   */
  private handlePinch(scaleChange: number) {
    // Adjust camera zoom or model scale
    if (this.config.camera instanceof THREE.PerspectiveCamera) {
      this.config.camera.zoom *= scaleChange;
      this.config.camera.updateProjectionMatrix();
    }
  }
  
  /**
   * Raycast to find capsule at screen position
   */
  private raycastCapsule(screenPosition: THREE.Vector2): any | null {
    this.raycaster.setFromCamera(screenPosition, this.config.camera);
    
    // Get all capsule meshes from scene
    const capsuleMeshes: THREE.Object3D[] = [];
    this.config.scene.traverse((object) => {
      if (object.userData.type === 'capsule_overlay') {
        capsuleMeshes.push(object);
      }
    });
    
    const intersects = this.raycaster.intersectObjects(capsuleMeshes);
    
    if (intersects.length > 0) {
      return intersects[0].object.userData.capsule;
    }
    
    return null;
  }
  
  // ==========================================================================
  // VR Controller Interaction
  // ==========================================================================
  
  /**
   * Set up VR controllers
   */
  private setupVRControllers() {
    // Controller 0 (left hand)
    const controller0 = this.config.renderer.xr.getController(0);
    controller0.addEventListener('selectstart', () => this.onVRSelectStart(0));
    controller0.addEventListener('selectend', () => this.onVRSelectEnd(0));
    this.config.scene.add(controller0);
    
    const grip0 = this.config.renderer.xr.getControllerGrip(0);
    this.config.scene.add(grip0);
    
    // Controller 1 (right hand)
    const controller1 = this.config.renderer.xr.getController(1);
    controller1.addEventListener('selectstart', () => this.onVRSelectStart(1));
    controller1.addEventListener('selectend', () => this.onVRSelectEnd(1));
    this.config.scene.add(controller1);
    
    const grip1 = this.config.renderer.xr.getControllerGrip(1);
    this.config.scene.add(grip1);
    
    // Add controller ray visualizations
    this.addControllerRay(controller0);
    this.addControllerRay(controller1);
    
    // Store controller states
    this.vrControllers = [
      {
        controller: controller0,
        grip: grip0,
        targetRaySpace: controller0 as any,
        isSelecting: false,
        isSqueezing: false
      },
      {
        controller: controller1,
        grip: grip1,
        targetRaySpace: controller1 as any,
        isSelecting: false,
        isSqueezing: false
      }
    ];
    
    console.log('VR controllers initialized');
  }
  
  /**
   * Add ray visualization to VR controller
   */
  private addControllerRay(controller: THREE.Group) {
    const geometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(0, 0, -5)
    ]);
    
    const material = new THREE.LineBasicMaterial({
      color: 0x00d4ff,
      linewidth: 2
    });
    
    const line = new THREE.Line(geometry, material);
    controller.add(line);
  }
  
  /**
   * Handle VR controller select start
   */
  private onVRSelectStart(controllerIndex: number) {
    const controller = this.vrControllers[controllerIndex];
    controller.isSelecting = true;
    
    // Raycast from controller
    const capsule = this.raycastFromController(controller.controller);
    
    if (capsule) {
      console.log('VR controller selected capsule:', capsule.id);
      this.config.onCapsuleSelect(capsule);
    }
  }
  
  /**
   * Handle VR controller select end
   */
  private onVRSelectEnd(controllerIndex: number) {
    const controller = this.vrControllers[controllerIndex];
    controller.isSelecting = false;
  }
  
  /**
   * Raycast from VR controller
   */
  private raycastFromController(controller: THREE.Group): any | null {
    // Set raycaster from controller position and direction
    const tempMatrix = new THREE.Matrix4();
    tempMatrix.identity().extractRotation(controller.matrixWorld);
    
    this.raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
    this.raycaster.ray.direction.set(0, 0, -1).applyMatrix4(tempMatrix);
    
    // Get all capsule meshes
    const capsuleMeshes: THREE.Object3D[] = [];
    this.config.scene.traverse((object) => {
      if (object.userData.type === 'capsule_overlay') {
        capsuleMeshes.push(object);
      }
    });
    
    const intersects = this.raycaster.intersectObjects(capsuleMeshes);
    
    if (intersects.length > 0) {
      return intersects[0].object.userData.capsule;
    }
    
    return null;
  }
  
  // ==========================================================================
  // Voice Commands
  // ==========================================================================
  
  /**
   * Set up voice recognition
   */
  private setupVoiceRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('Speech recognition not supported in this browser');
      return;
    }
    
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    this.speechRecognition = new SpeechRecognition();
    
    this.speechRecognition.continuous = true;
    this.speechRecognition.interimResults = false;
    this.speechRecognition.lang = 'en-US';
    
    this.speechRecognition.onresult = (event: SpeechRecognitionEvent) => {
      const last = event.results.length - 1;
      const command = event.results[last][0].transcript.toLowerCase().trim();
      
      console.log('Voice command:', command);
      this.handleVoiceCommand(command);
    };
    
    this.speechRecognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
    };
    
    console.log('Voice recognition initialized');
  }
  
  /**
   * Start listening for voice commands
   */
  public startVoiceRecognition() {
    if (!this.speechRecognition) {
      console.warn('Voice recognition not available');
      return;
    }
    
    if (!this.isListening) {
      this.speechRecognition.start();
      this.isListening = true;
      console.log('Voice recognition started');
    }
  }
  
  /**
   * Stop listening for voice commands
   */
  public stopVoiceRecognition() {
    if (this.speechRecognition && this.isListening) {
      this.speechRecognition.stop();
      this.isListening = false;
      console.log('Voice recognition stopped');
    }
  }
  
  /**
   * Handle voice command
   */
  private handleVoiceCommand(command: string) {
    // Parse command
    if (command.includes('execute') || command.includes('run')) {
      this.config.onVoiceCommand('execute');
    } else if (command.includes('hide') || command.includes('dismiss')) {
      this.config.onVoiceCommand('hide');
    } else if (command.includes('show') || command.includes('display')) {
      this.config.onVoiceCommand('show');
    } else if (command.includes('acknowledge') || command.includes('confirm')) {
      this.config.onVoiceCommand('acknowledge');
    } else {
      console.warn('Unknown voice command:', command);
    }
  }
  
  // ==========================================================================
  // Spatial Anchoring (AR)
  // ==========================================================================
  
  /**
   * Create spatial anchor at position
   */
  public async createSpatialAnchor(
    capsuleId: string,
    position: THREE.Vector3
  ): Promise<boolean> {
    if (!this.config.enableAnchoring) {
      console.warn('Spatial anchoring not enabled');
      return false;
    }
    
    if (!this.xrSession || !this.xrReferenceSpace) {
      console.warn('XR session not active');
      return false;
    }
    
    try {
      // Create XR anchor
      const pose = new XRRigidTransform({
        x: position.x,
        y: position.y,
        z: position.z
      });
      
      const anchor = await this.xrSession.requestReferenceSpace('local')
        .then((space) => (this.xrSession as any).createAnchor(pose, space));
      
      this.spatialAnchors.set(capsuleId, anchor);
      console.log(`Spatial anchor created for capsule: ${capsuleId}`);
      
      return true;
    } catch (error) {
      console.error('Failed to create spatial anchor:', error);
      return false;
    }
  }
  
  /**
   * Remove spatial anchor
   */
  public removeSpatialAnchor(capsuleId: string) {
    const anchor = this.spatialAnchors.get(capsuleId);
    
    if (anchor) {
      anchor.delete();
      this.spatialAnchors.delete(capsuleId);
      console.log(`Spatial anchor removed for capsule: ${capsuleId}`);
    }
  }
  
  /**
   * Get all spatial anchors
   */
  public getSpatialAnchors(): Map<string, XRAnchor> {
    return this.spatialAnchors;
  }
  
  // ==========================================================================
  // XR Session Management
  // ==========================================================================
  
  /**
   * Start AR session
   */
  public async startARSession(): Promise<boolean> {
    if (!navigator.xr) {
      console.error('WebXR not supported');
      return false;
    }
    
    try {
      const session = await navigator.xr.requestSession('immersive-ar', {
        requiredFeatures: ['local', 'hit-test'],
        optionalFeatures: ['anchors', 'dom-overlay']
      });
      
      await this.config.renderer.xr.setSession(session);
      this.xrSession = session;
      
      this.xrReferenceSpace = await session.requestReferenceSpace('local');
      
      console.log('AR session started');
      return true;
    } catch (error) {
      console.error('Failed to start AR session:', error);
      return false;
    }
  }
  
  /**
   * Start VR session
   */
  public async startVRSession(): Promise<boolean> {
    if (!navigator.xr) {
      console.error('WebXR not supported');
      return false;
    }
    
    try {
      const session = await navigator.xr.requestSession('immersive-vr', {
        requiredFeatures: ['local']
      });
      
      await this.config.renderer.xr.setSession(session);
      this.xrSession = session;
      
      this.xrReferenceSpace = await session.requestReferenceSpace('local');
      
      console.log('VR session started');
      return true;
    } catch (error) {
      console.error('Failed to start VR session:', error);
      return false;
    }
  }
  
  /**
   * End XR session
   */
  public async endXRSession() {
    if (this.xrSession) {
      await this.xrSession.end();
      this.xrSession = undefined;
      this.xrReferenceSpace = undefined;
      console.log('XR session ended');
    }
  }
  
  // ==========================================================================
  // Cleanup
  // ==========================================================================
  
  /**
   * Dispose controller and clean up resources
   */
  public dispose() {
    // Stop voice recognition
    this.stopVoiceRecognition();
    
    // Remove spatial anchors
    for (const capsuleId of this.spatialAnchors.keys()) {
      this.removeSpatialAnchor(capsuleId);
    }
    
    // End XR session
    this.endXRSession();
    
    console.log('AR/VR Interaction Controller disposed');
  }
}

// ============================================================================
// Export
// ============================================================================

export default ARVRInteractionController;
