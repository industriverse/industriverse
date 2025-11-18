/**
 * MediaPipe Hands Controller
 * 
 * Gesture-free capsule interaction using hand tracking
 * - Point at capsule → highlight
 * - Pinch fingers → select
 * - Open palm → dismiss
 */

import { useEffect, useRef, useState } from 'react';
import { Hands, Results } from '@mediapipe/hands';
import { Camera } from '@mediapipe/camera_utils';

export interface HandGesture {
  type: 'point' | 'pinch' | 'open_palm' | 'closed_fist' | 'thumbs_up' | 'none';
  position: { x: number; y: number; z: number };
  confidence: number;
}

export interface MediaPipeHandsControllerProps {
  onGesture?: (gesture: HandGesture) => void;
  onHandTracking?: (landmarks: any[]) => void;
  enabled?: boolean;
  videoWidth?: number;
  videoHeight?: number;
}

export function MediaPipeHandsController({
  onGesture,
  onHandTracking,
  enabled = true,
  videoWidth = 640,
  videoHeight = 480,
}: MediaPipeHandsControllerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const handsRef = useRef<Hands | null>(null);
  const cameraRef = useRef<Camera | null>(null);

  useEffect(() => {
    if (!enabled) {
      cleanup();
      return;
    }

    initializeMediaPipe();

    return () => {
      cleanup();
    };
  }, [enabled]);

  /**
   * Initialize MediaPipe Hands
   */
  const initializeMediaPipe = async () => {
    try {
      if (!videoRef.current) {
        throw new Error('Video element not found');
      }

      console.log('[MediaPipeHands] Initializing...');

      // Create Hands instance
      const hands = new Hands({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
        },
      });

      hands.setOptions({
        maxNumHands: 2,
        modelComplexity: 1,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });

      hands.onResults(onResults);

      handsRef.current = hands;

      // Initialize camera
      const camera = new Camera(videoRef.current, {
        onFrame: async () => {
          if (videoRef.current && handsRef.current) {
            await handsRef.current.send({ image: videoRef.current });
          }
        },
        width: videoWidth,
        height: videoHeight,
      });

      await camera.start();
      cameraRef.current = camera;

      setIsInitialized(true);
      console.log('[MediaPipeHands] Initialized successfully');

    } catch (err) {
      console.error('[MediaPipeHands] Initialization failed:', err);
      setError((err as Error).message);
    }
  };

  /**
   * Handle MediaPipe results
   */
  const onResults = (results: Results) => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw video frame
    if (results.image) {
      ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);
    }

    // Process hand landmarks
    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      for (const landmarks of results.multiHandLandmarks) {
        // Draw hand landmarks
        drawHandLandmarks(ctx, landmarks);

        // Detect gesture
        const gesture = detectGesture(landmarks);
        
        if (gesture.type !== 'none' && onGesture) {
          onGesture(gesture);
        }

        // Emit landmarks for external processing
        if (onHandTracking) {
          onHandTracking(landmarks);
        }
      }
    }
  };

  /**
   * Draw hand landmarks on canvas
   */
  const drawHandLandmarks = (ctx: CanvasRenderingContext2D, landmarks: any[]) => {
    // Draw connections
    const connections = [
      [0, 1], [1, 2], [2, 3], [3, 4], // Thumb
      [0, 5], [5, 6], [6, 7], [7, 8], // Index
      [0, 9], [9, 10], [10, 11], [11, 12], // Middle
      [0, 13], [13, 14], [14, 15], [15, 16], // Ring
      [0, 17], [17, 18], [18, 19], [19, 20], // Pinky
      [5, 9], [9, 13], [13, 17], // Palm
    ];

    ctx.strokeStyle = '#00ffff';
    ctx.lineWidth = 2;

    for (const [start, end] of connections) {
      const startPoint = landmarks[start];
      const endPoint = landmarks[end];

      ctx.beginPath();
      ctx.moveTo(startPoint.x * canvasRef.current!.width, startPoint.y * canvasRef.current!.height);
      ctx.lineTo(endPoint.x * canvasRef.current!.width, endPoint.y * canvasRef.current!.height);
      ctx.stroke();
    }

    // Draw landmarks
    ctx.fillStyle = '#ff00ff';
    for (const landmark of landmarks) {
      ctx.beginPath();
      ctx.arc(
        landmark.x * canvasRef.current!.width,
        landmark.y * canvasRef.current!.height,
        5,
        0,
        2 * Math.PI
      );
      ctx.fill();
    }
  };

  /**
   * Detect hand gesture from landmarks
   */
  const detectGesture = (landmarks: any[]): HandGesture => {
    // Extract key landmarks
    const wrist = landmarks[0];
    const thumb_tip = landmarks[4];
    const index_tip = landmarks[8];
    const middle_tip = landmarks[12];
    const ring_tip = landmarks[16];
    const pinky_tip = landmarks[20];
    const index_mcp = landmarks[5];
    const middle_mcp = landmarks[9];

    // Calculate distances
    const thumbIndexDistance = distance3D(thumb_tip, index_tip);
    const palmSize = distance3D(wrist, middle_mcp);
    const fingersExtended = [
      index_tip.y < index_mcp.y,
      middle_tip.y < middle_mcp.y,
      ring_tip.y < landmarks[13].y,
      pinky_tip.y < landmarks[17].y,
    ];

    // Detect pinch (thumb + index close)
    if (thumbIndexDistance < palmSize * 0.3) {
      return {
        type: 'pinch',
        position: {
          x: (thumb_tip.x + index_tip.x) / 2,
          y: (thumb_tip.y + index_tip.y) / 2,
          z: (thumb_tip.z + index_tip.z) / 2,
        },
        confidence: 0.9,
      };
    }

    // Detect point (only index extended)
    if (
      fingersExtended[0] && // Index extended
      !fingersExtended[1] && // Middle not extended
      !fingersExtended[2] && // Ring not extended
      !fingersExtended[3] // Pinky not extended
    ) {
      return {
        type: 'point',
        position: {
          x: index_tip.x,
          y: index_tip.y,
          z: index_tip.z,
        },
        confidence: 0.85,
      };
    }

    // Detect open palm (all fingers extended)
    if (fingersExtended.every((extended) => extended)) {
      const palmCenter = {
        x: (wrist.x + middle_mcp.x) / 2,
        y: (wrist.y + middle_mcp.y) / 2,
        z: (wrist.z + middle_mcp.z) / 2,
      };

      return {
        type: 'open_palm',
        position: palmCenter,
        confidence: 0.8,
      };
    }

    // Detect closed fist (no fingers extended)
    if (fingersExtended.every((extended) => !extended)) {
      return {
        type: 'closed_fist',
        position: {
          x: wrist.x,
          y: wrist.y,
          z: wrist.z,
        },
        confidence: 0.75,
      };
    }

    // Detect thumbs up
    if (
      thumb_tip.y < wrist.y && // Thumb above wrist
      !fingersExtended[0] && // Index not extended
      !fingersExtended[1] && // Middle not extended
      !fingersExtended[2] && // Ring not extended
      !fingersExtended[3] // Pinky not extended
    ) {
      return {
        type: 'thumbs_up',
        position: {
          x: thumb_tip.x,
          y: thumb_tip.y,
          z: thumb_tip.z,
        },
        confidence: 0.85,
      };
    }

    return {
      type: 'none',
      position: { x: 0, y: 0, z: 0 },
      confidence: 0,
    };
  };

  /**
   * Calculate 3D distance between two landmarks
   */
  const distance3D = (a: any, b: any): number => {
    return Math.sqrt(
      Math.pow(a.x - b.x, 2) +
      Math.pow(a.y - b.y, 2) +
      Math.pow(a.z - b.z, 2)
    );
  };

  /**
   * Cleanup resources
   */
  const cleanup = () => {
    if (cameraRef.current) {
      cameraRef.current.stop();
      cameraRef.current = null;
    }

    if (handsRef.current) {
      handsRef.current.close();
      handsRef.current = null;
    }

    setIsInitialized(false);
  };

  return (
    <div className="relative">
      {/* Video element (hidden) */}
      <video
        ref={videoRef}
        className="hidden"
        playsInline
      />

      {/* Canvas for visualization */}
      <canvas
        ref={canvasRef}
        width={videoWidth}
        height={videoHeight}
        className="rounded-lg border border-border"
      />

      {/* Status indicators */}
      {error && (
        <div className="absolute top-2 left-2 bg-destructive text-destructive-foreground px-3 py-1 rounded text-sm">
          Error: {error}
        </div>
      )}

      {!isInitialized && !error && (
        <div className="absolute top-2 left-2 bg-muted text-muted-foreground px-3 py-1 rounded text-sm">
          Initializing hand tracking...
        </div>
      )}

      {isInitialized && (
        <div className="absolute top-2 left-2 bg-primary text-primary-foreground px-3 py-1 rounded text-sm">
          ✓ Hand tracking active
        </div>
      )}
    </div>
  );
}
