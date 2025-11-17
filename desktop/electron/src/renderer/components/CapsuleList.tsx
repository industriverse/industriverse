/**
 * CapsuleList Component
 * Scrollable list of capsules
 */

import React from 'react';
import { Capsule } from '../../types/capsule';
import { CapsuleItem } from './CapsuleItem';
import './CapsuleList.css';

interface CapsuleListProps {
  capsules: Capsule[];
  onAction: (capsuleId: string, actionId: string) => void;
  onPin: (capsuleId: string, pinned: boolean) => void;
  onHide: (capsuleId: string) => void;
  onSnooze: (capsuleId: string, duration: number) => void;
}

export function CapsuleList({
  capsules,
  onAction,
  onPin,
  onHide,
  onSnooze,
}: CapsuleListProps) {
  // Separate pinned and unpinned capsules
  const pinnedCapsules = capsules.filter((c) => c.isPinned);
  const unpinnedCapsules = capsules.filter((c) => !c.isPinned);

  return (
    <div className="capsule-list">
      {/* Pinned capsules */}
      {pinnedCapsules.length > 0 && (
        <div className="capsule-section">
          <div className="capsule-section-header">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path
                d="M8.5 0L7.29 1.21L9.09 3.01L3.5 8.6V11H5.9L11.49 5.41L13.29 7.21L14.5 6L8.5 0Z"
                fill="currentColor"
              />
            </svg>
            <span>Pinned</span>
          </div>
          {pinnedCapsules.map((capsule) => (
            <CapsuleItem
              key={capsule.id}
              capsule={capsule}
              onAction={onAction}
              onPin={onPin}
              onHide={onHide}
              onSnooze={onSnooze}
            />
          ))}
        </div>
      )}

      {/* Unpinned capsules */}
      {unpinnedCapsules.length > 0 && (
        <div className="capsule-section">
          {pinnedCapsules.length > 0 && (
            <div className="capsule-section-header">
              <span>Recent</span>
            </div>
          )}
          {unpinnedCapsules.map((capsule) => (
            <CapsuleItem
              key={capsule.id}
              capsule={capsule}
              onAction={onAction}
              onPin={onPin}
              onHide={onHide}
              onSnooze={onSnooze}
            />
          ))}
        </div>
      )}
    </div>
  );
}
