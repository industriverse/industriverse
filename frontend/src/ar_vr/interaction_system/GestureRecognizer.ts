/**
 * Gesture Recognizer
 * 
 * Advanced gesture recognition for mobile AR interactions:
 * - Tap (single, double, triple)
 * - Long press (with haptic feedback)
 * - Swipe (4 directions with velocity)
 * - Pinch (zoom in/out)
 * - Rotate (two-finger rotation)
 * - Pan (two-finger pan)
 * 
 * Based on production patterns from:
 * - Hammer.js (gesture recognition library)
 * - iOS UIGestureRecognizer
 * - Android GestureDetector
 */

import * as THREE from 'three';

// ============================================================================
// Type Definitions
// ============================================================================

export type GestureType =
  | 'tap'
  | 'double-tap'
  | 'triple-tap'
  | 'long-press'
  | 'swipe-left'
  | 'swipe-right'
  | 'swipe-up'
  | 'swipe-down'
  | 'pinch-in'
  | 'pinch-out'
  | 'rotate-cw'
  | 'rotate-ccw'
  | 'pan';

export interface GestureEvent {
  type: GestureType;
  position: THREE.Vector2;
  deltaPosition?: THREE.Vector2;
  scale?: number;
  rotation?: number;
  velocity?: number;
  timestamp: number;
}

export interface GestureRecognizerConfig {
  /** DOM element to attach listeners */
  element: HTMLElement;
  
  /** Gesture callbacks */
  onGesture?: (event: GestureEvent) => void;
  
  /** Tap threshold (ms) */
  tapThreshold?: number;
  
  /** Long press threshold (ms) */
  longPressThreshold?: number;
  
  /** Swipe velocity threshold (px/ms) */
  swipeVelocityThreshold?: number;
  
  /** Enable haptic feedback */
  enableHaptics?: boolean;
}

interface TouchPoint {
  id: number;
  position: THREE.Vector2;
  timestamp: number;
}

// ============================================================================
// Gesture Recognizer
// ============================================================================

export class GestureRecognizer {
  private config: Required<GestureRecognizerConfig>;
  
  // Touch tracking
  private touches: Map<number, TouchPoint> = new Map();
  private lastTapTime: number = 0;
  private tapCount: number = 0;
  
  // Gesture state
  private isLongPressing: boolean = false;
  private longPressTimer?: number;
  
  private isPinching: boolean = false;
  private initialPinchDistance: number = 0;
  
  private isRotating: boolean = false;
  private initialRotationAngle: number = 0;
  
  private isPanning: boolean = false;
  private panStartPosition: THREE.Vector2 = new THREE.Vector2();
  
  constructor(config: GestureRecognizerConfig) {
    this.config = {
      element: config.element,
      onGesture: config.onGesture ?? (() => {}),
      tapThreshold: config.tapThreshold ?? 300,
      longPressThreshold: config.longPressThreshold ?? 500,
      swipeVelocityThreshold: config.swipeVelocityThreshold ?? 0.5,
      enableHaptics: config.enableHaptics ?? true
    };
    
    this.attachListeners();
  }
  
  /**
   * Attach touch event listeners
   */
  private attachListeners() {
    this.config.element.addEventListener('touchstart', this.onTouchStart.bind(this), { passive: false });
    this.config.element.addEventListener('touchmove', this.onTouchMove.bind(this), { passive: false });
    this.config.element.addEventListener('touchend', this.onTouchEnd.bind(this), { passive: false });
    this.config.element.addEventListener('touchcancel', this.onTouchCancel.bind(this), { passive: false });
  }
  
  /**
   * Handle touch start
   */
  private onTouchStart(event: TouchEvent) {
    event.preventDefault();
    
    const timestamp = Date.now();
    
    // Add new touches
    for (let i = 0; i < event.changedTouches.length; i++) {
      const touch = event.changedTouches[i];
      const position = this.getTouchPosition(touch);
      
      this.touches.set(touch.identifier, {
        id: touch.identifier,
        position,
        timestamp
      });
    }
    
    // Handle single touch
    if (this.touches.size === 1) {
      this.handleSingleTouchStart(timestamp);
    }
    
    // Handle two-finger gestures
    if (this.touches.size === 2) {
      this.handleTwoFingerStart();
    }
  }
  
  /**
   * Handle touch move
   */
  private onTouchMove(event: TouchEvent) {
    event.preventDefault();
    
    // Update touch positions
    for (let i = 0; i < event.changedTouches.length; i++) {
      const touch = event.changedTouches[i];
      const position = this.getTouchPosition(touch);
      
      const existingTouch = this.touches.get(touch.identifier);
      if (existingTouch) {
        existingTouch.position = position;
      }
    }
    
    // Cancel long press if touch moved
    if (this.isLongPressing && this.touches.size === 1) {
      const touch = Array.from(this.touches.values())[0];
      const moveDistance = touch.position.distanceTo(this.panStartPosition);
      
      if (moveDistance > 0.05) {
        this.cancelLongPress();
      }
    }
    
    // Handle two-finger gestures
    if (this.touches.size === 2) {
      this.handleTwoFingerMove();
    }
  }
  
  /**
   * Handle touch end
   */
  private onTouchEnd(event: TouchEvent) {
    event.preventDefault();
    
    const timestamp = Date.now();
    
    // Handle single touch end
    if (this.touches.size === 1 && event.changedTouches.length === 1) {
      this.handleSingleTouchEnd(timestamp);
    }
    
    // Remove ended touches
    for (let i = 0; i < event.changedTouches.length; i++) {
      const touch = event.changedTouches[i];
      this.touches.delete(touch.identifier);
    }
    
    // Reset two-finger gesture states
    if (this.touches.size < 2) {
      this.isPinching = false;
      this.isRotating = false;
      this.isPanning = false;
    }
  }
  
  /**
   * Handle touch cancel
   */
  private onTouchCancel(event: TouchEvent) {
    this.cancelLongPress();
    this.touches.clear();
    this.isPinching = false;
    this.isRotating = false;
    this.isPanning = false;
  }
  
  /**
   * Handle single touch start
   */
  private handleSingleTouchStart(timestamp: number) {
    const touch = Array.from(this.touches.values())[0];
    this.panStartPosition.copy(touch.position);
    
    // Start long press timer
    this.longPressTimer = window.setTimeout(() => {
      this.handleLongPress(touch.position);
    }, this.config.longPressThreshold);
    
    this.isLongPressing = true;
  }
  
  /**
   * Handle single touch end
   */
  private handleSingleTouchEnd(timestamp: number) {
    const touch = Array.from(this.touches.values())[0];
    const duration = timestamp - touch.timestamp;
    const moveDistance = touch.position.distanceTo(this.panStartPosition);
    
    // Cancel long press
    this.cancelLongPress();
    
    // Detect tap or swipe
    if (duration < this.config.tapThreshold && moveDistance < 0.05) {
      this.handleTap(touch.position, timestamp);
    } else if (moveDistance > 0.1) {
      this.handleSwipe(this.panStartPosition, touch.position, duration);
    }
  }
  
  /**
   * Handle tap gesture
   */
  private handleTap(position: THREE.Vector2, timestamp: number) {
    const timeSinceLastTap = timestamp - this.lastTapTime;
    
    if (timeSinceLastTap < this.config.tapThreshold) {
      this.tapCount++;
    } else {
      this.tapCount = 1;
    }
    
    this.lastTapTime = timestamp;
    
    // Emit tap event after delay to detect multi-tap
    setTimeout(() => {
      if (this.tapCount === 1) {
        this.emitGesture({
          type: 'tap',
          position,
          timestamp
        });
      } else if (this.tapCount === 2) {
        this.emitGesture({
          type: 'double-tap',
          position,
          timestamp
        });
      } else if (this.tapCount >= 3) {
        this.emitGesture({
          type: 'triple-tap',
          position,
          timestamp
        });
      }
      
      this.tapCount = 0;
    }, this.config.tapThreshold);
  }
  
  /**
   * Handle long press gesture
   */
  private handleLongPress(position: THREE.Vector2) {
    this.emitGesture({
      type: 'long-press',
      position,
      timestamp: Date.now()
    });
    
    // Haptic feedback
    this.triggerHapticFeedback('medium');
  }
  
  /**
   * Cancel long press
   */
  private cancelLongPress() {
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer);
      this.longPressTimer = undefined;
    }
    this.isLongPressing = false;
  }
  
  /**
   * Handle swipe gesture
   */
  private handleSwipe(start: THREE.Vector2, end: THREE.Vector2, duration: number) {
    const delta = new THREE.Vector2().subVectors(end, start);
    const velocity = delta.length() / duration;
    
    if (velocity < this.config.swipeVelocityThreshold) {
      return; // Too slow to be a swipe
    }
    
    let type: GestureType;
    
    if (Math.abs(delta.x) > Math.abs(delta.y)) {
      type = delta.x > 0 ? 'swipe-right' : 'swipe-left';
    } else {
      type = delta.y > 0 ? 'swipe-down' : 'swipe-up';
    }
    
    this.emitGesture({
      type,
      position: start,
      deltaPosition: delta,
      velocity,
      timestamp: Date.now()
    });
    
    // Haptic feedback
    this.triggerHapticFeedback('light');
  }
  
  /**
   * Handle two-finger gesture start
   */
  private handleTwoFingerStart() {
    const touches = Array.from(this.touches.values());
    
    // Initialize pinch
    this.initialPinchDistance = this.getTouchDistance(touches[0], touches[1]);
    this.isPinching = true;
    
    // Initialize rotation
    this.initialRotationAngle = this.getTouchAngle(touches[0], touches[1]);
    this.isRotating = true;
    
    // Initialize pan
    this.panStartPosition = this.getTouchCenter(touches[0], touches[1]);
    this.isPanning = true;
  }
  
  /**
   * Handle two-finger gesture move
   */
  private handleTwoFingerMove() {
    const touches = Array.from(this.touches.values());
    
    if (touches.length !== 2) return;
    
    // Detect pinch
    if (this.isPinching) {
      const currentDistance = this.getTouchDistance(touches[0], touches[1]);
      const scale = currentDistance / this.initialPinchDistance;
      
      const type: GestureType = scale > 1 ? 'pinch-out' : 'pinch-in';
      
      this.emitGesture({
        type,
        position: this.getTouchCenter(touches[0], touches[1]),
        scale,
        timestamp: Date.now()
      });
    }
    
    // Detect rotation
    if (this.isRotating) {
      const currentAngle = this.getTouchAngle(touches[0], touches[1]);
      const rotation = currentAngle - this.initialRotationAngle;
      
      const type: GestureType = rotation > 0 ? 'rotate-cw' : 'rotate-ccw';
      
      if (Math.abs(rotation) > 5) { // Minimum 5 degrees
        this.emitGesture({
          type,
          position: this.getTouchCenter(touches[0], touches[1]),
          rotation,
          timestamp: Date.now()
        });
      }
    }
    
    // Detect pan
    if (this.isPanning) {
      const currentCenter = this.getTouchCenter(touches[0], touches[1]);
      const delta = new THREE.Vector2().subVectors(currentCenter, this.panStartPosition);
      
      if (delta.length() > 0.05) {
        this.emitGesture({
          type: 'pan',
          position: currentCenter,
          deltaPosition: delta,
          timestamp: Date.now()
        });
      }
    }
  }
  
  /**
   * Get touch position in normalized device coordinates
   */
  private getTouchPosition(touch: Touch): THREE.Vector2 {
    const rect = this.config.element.getBoundingClientRect();
    
    return new THREE.Vector2(
      ((touch.clientX - rect.left) / rect.width) * 2 - 1,
      -((touch.clientY - rect.top) / rect.height) * 2 + 1
    );
  }
  
  /**
   * Get distance between two touches
   */
  private getTouchDistance(touch1: TouchPoint, touch2: TouchPoint): number {
    return touch1.position.distanceTo(touch2.position);
  }
  
  /**
   * Get angle between two touches (in degrees)
   */
  private getTouchAngle(touch1: TouchPoint, touch2: TouchPoint): number {
    const delta = new THREE.Vector2().subVectors(touch2.position, touch1.position);
    return Math.atan2(delta.y, delta.x) * (180 / Math.PI);
  }
  
  /**
   * Get center point between two touches
   */
  private getTouchCenter(touch1: TouchPoint, touch2: TouchPoint): THREE.Vector2 {
    return new THREE.Vector2(
      (touch1.position.x + touch2.position.x) / 2,
      (touch1.position.y + touch2.position.y) / 2
    );
  }
  
  /**
   * Emit gesture event
   */
  private emitGesture(event: GestureEvent) {
    console.log('Gesture detected:', event.type);
    this.config.onGesture(event);
  }
  
  /**
   * Trigger haptic feedback
   */
  private triggerHapticFeedback(intensity: 'light' | 'medium' | 'heavy') {
    if (!this.config.enableHaptics) return;
    
    if (navigator.vibrate) {
      const duration = intensity === 'light' ? 10 : intensity === 'medium' ? 20 : 50;
      navigator.vibrate(duration);
    }
  }
  
  /**
   * Dispose gesture recognizer
   */
  public dispose() {
    this.cancelLongPress();
    this.touches.clear();
    
    // Remove event listeners
    this.config.element.removeEventListener('touchstart', this.onTouchStart.bind(this));
    this.config.element.removeEventListener('touchmove', this.onTouchMove.bind(this));
    this.config.element.removeEventListener('touchend', this.onTouchEnd.bind(this));
    this.config.element.removeEventListener('touchcancel', this.onTouchCancel.bind(this));
    
    console.log('Gesture recognizer disposed');
  }
}

// ============================================================================
// Export
// ============================================================================

export default GestureRecognizer;
