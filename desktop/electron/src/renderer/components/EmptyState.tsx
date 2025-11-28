/**
 * EmptyState Component
 * Shown when there are no capsules
 */

import React from 'react';
import './EmptyState.css';

export function EmptyState() {
  return (
    <div className="empty-state">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <circle cx="32" cy="32" r="30" stroke="currentColor" strokeWidth="2" opacity="0.2" />
        <path
          d="M32 16L36.24 28.48L48 32L36.24 35.52L32 48L27.76 35.52L16 32L27.76 28.48L32 16Z"
          fill="currentColor"
          opacity="0.3"
        />
      </svg>
      <h3 className="empty-state-title">No Capsules</h3>
      <p className="empty-state-description">
        You're all caught up! New capsules will appear here when they're created.
      </p>
    </div>
  );
}
