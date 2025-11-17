/**
 * LoadingState Component
 * Shown while loading capsules
 */

import React from 'react';
import './LoadingState.css';

export function LoadingState() {
  return (
    <div className="loading-state">
      <div className="loading-spinner">
        <div className="loading-spinner-circle" />
      </div>
      <p className="loading-state-text">Loading capsules...</p>
    </div>
  );
}
