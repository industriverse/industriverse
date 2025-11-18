/**
 * AR/VR Container
 * 
 * Wraps capsule list with AR/VR interaction modes
 */

import { useState, useEffect } from 'react';
import { MediaPipeHandsController, type HandGesture } from './MediaPipeHandsController';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

export type ARVRMode = '2d' | '3d' | 'ar' | 'vr';

export interface ARVRContainerProps {
  mode: ARVRMode;
  onModeChange?: (mode: ARVRMode) => void;
  children: React.ReactNode;
}

export function ARVRContainer({
  mode,
  onModeChange,
  children,
}: ARVRContainerProps) {
  const [gestureEnabled, setGestureEnabled] = useState(false);
  const [lastGesture, setLastGesture] = useState<HandGesture | null>(null);
  const [selectedCapsuleId, setSelectedCapsuleId] = useState<string | null>(null);

  /**
   * Handle gesture from MediaPipe
   */
  const handleGesture = (gesture: HandGesture) => {
    setLastGesture(gesture);

    switch (gesture.type) {
      case 'point':
        // Highlight capsule at gesture position
        handlePointGesture(gesture.position);
        break;

      case 'pinch':
        // Select highlighted capsule
        handlePinchGesture();
        break;

      case 'open_palm':
        // Dismiss selected capsule
        handleOpenPalmGesture();
        break;

      case 'thumbs_up':
        // Acknowledge selected capsule
        handleThumbsUpGesture();
        break;

      case 'closed_fist':
        // Execute action on selected capsule
        handleClosedFistGesture();
        break;
    }
  };

  /**
   * Handle point gesture (highlight capsule)
   */
  const handlePointGesture = (position: { x: number; y: number; z: number }) => {
    // Convert gesture position to screen coordinates
    const screenX = position.x * window.innerWidth;
    const screenY = position.y * window.innerHeight;

    // Find capsule element at position
    const element = document.elementFromPoint(screenX, screenY);
    const capsuleElement = element?.closest('[data-capsule-id]');

    if (capsuleElement) {
      const capsuleId = capsuleElement.getAttribute('data-capsule-id');
      if (capsuleId && capsuleId !== selectedCapsuleId) {
        setSelectedCapsuleId(capsuleId);
        
        // Add highlight effect
        capsuleElement.classList.add('ring-2', 'ring-primary');
        
        // Remove highlight from previous selection
        document.querySelectorAll('[data-capsule-id]').forEach((el) => {
          if (el !== capsuleElement) {
            el.classList.remove('ring-2', 'ring-primary');
          }
        });
      }
    }
  };

  /**
   * Handle pinch gesture (select capsule)
   */
  const handlePinchGesture = () => {
    if (selectedCapsuleId) {
      toast.success(`Capsule ${selectedCapsuleId} selected`);
      
      // Trigger capsule expansion
      const capsuleElement = document.querySelector(`[data-capsule-id="${selectedCapsuleId}"]`);
      if (capsuleElement) {
        (capsuleElement as HTMLElement).click();
      }
    }
  };

  /**
   * Handle open palm gesture (dismiss capsule)
   */
  const handleOpenPalmGesture = () => {
    if (selectedCapsuleId) {
      toast.info(`Capsule ${selectedCapsuleId} dismissed`);
      
      // Trigger dismiss action
      const dismissButton = document.querySelector(
        `[data-capsule-id="${selectedCapsuleId}"] [data-action="dismiss"]`
      );
      if (dismissButton) {
        (dismissButton as HTMLElement).click();
      }

      setSelectedCapsuleId(null);
    }
  };

  /**
   * Handle thumbs up gesture (acknowledge capsule)
   */
  const handleThumbsUpGesture = () => {
    if (selectedCapsuleId) {
      toast.success(`Capsule ${selectedCapsuleId} acknowledged`);
      
      // Trigger acknowledge action
      const acknowledgeButton = document.querySelector(
        `[data-capsule-id="${selectedCapsuleId}"] [data-action="acknowledge"]`
      );
      if (acknowledgeButton) {
        (acknowledgeButton as HTMLElement).click();
      }
    }
  };

  /**
   * Handle closed fist gesture (execute action)
   */
  const handleClosedFistGesture = () => {
    if (selectedCapsuleId) {
      toast.info(`Executing action on capsule ${selectedCapsuleId}`);
      
      // Trigger primary action
      const executeButton = document.querySelector(
        `[data-capsule-id="${selectedCapsuleId}"] [data-action="mitigate"]`
      );
      if (executeButton) {
        (executeButton as HTMLElement).click();
      }
    }
  };

  /**
   * Toggle gesture control
   */
  const toggleGestureControl = () => {
    setGestureEnabled(!gestureEnabled);
    
    if (!gestureEnabled) {
      toast.success('Gesture control enabled', {
        description: 'Use hand gestures to interact with capsules',
      });
    } else {
      toast.info('Gesture control disabled');
      setSelectedCapsuleId(null);
      
      // Remove all highlights
      document.querySelectorAll('[data-capsule-id]').forEach((el) => {
        el.classList.remove('ring-2', 'ring-primary');
      });
    }
  };

  return (
    <div className="relative">
      {/* AR/VR Mode Controls */}
      <div className="fixed top-20 right-4 z-50 flex flex-col gap-2">
        <Button
          variant={gestureEnabled ? 'default' : 'outline'}
          size="sm"
          onClick={toggleGestureControl}
          className="shadow-lg"
        >
          {gestureEnabled ? '✋ Gesture ON' : '✋ Gesture OFF'}
        </Button>

        {mode !== '2d' && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onModeChange?.('2d')}
            className="shadow-lg"
          >
            ← Back to 2D
          </Button>
        )}
      </div>

      {/* Gesture Visualization */}
      {gestureEnabled && (
        <div className="fixed bottom-4 right-4 z-50">
          <MediaPipeHandsController
            onGesture={handleGesture}
            enabled={gestureEnabled}
            videoWidth={320}
            videoHeight={240}
          />

          {/* Gesture Status */}
          {lastGesture && lastGesture.type !== 'none' && (
            <div className="mt-2 bg-background/90 backdrop-blur-sm border border-border rounded-lg p-3">
              <div className="text-sm font-medium">
                Gesture: <span className="text-primary">{lastGesture.type.replace('_', ' ')}</span>
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                Confidence: {(lastGesture.confidence * 100).toFixed(0)}%
              </div>
              {selectedCapsuleId && (
                <div className="text-xs text-muted-foreground mt-1">
                  Selected: {selectedCapsuleId}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Main Content */}
      <div className={gestureEnabled ? 'pr-80' : ''}>
        {children}
      </div>

      {/* Gesture Instructions */}
      {gestureEnabled && (
        <div className="fixed bottom-4 left-4 z-50 bg-background/90 backdrop-blur-sm border border-border rounded-lg p-4 max-w-xs">
          <h3 className="font-semibold text-sm mb-2">Gesture Controls</h3>
          <ul className="text-xs space-y-1 text-muted-foreground">
            <li>👉 <strong>Point:</strong> Highlight capsule</li>
            <li>🤏 <strong>Pinch:</strong> Select capsule</li>
            <li>✋ <strong>Open Palm:</strong> Dismiss capsule</li>
            <li>👍 <strong>Thumbs Up:</strong> Acknowledge</li>
            <li>✊ <strong>Closed Fist:</strong> Execute action</li>
          </ul>
        </div>
      )}
    </div>
  );
}
