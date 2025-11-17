/**
 * ErrorState Component
 * Shown when there's an error loading capsules
 */

import React from 'react';
import './ErrorState.css';

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="error-state">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <circle cx="32" cy="32" r="30" stroke="currentColor" strokeWidth="2" opacity="0.2" />
        <path
          d="M32 16L34 40H30L32 16Z"
          fill="currentColor"
          opacity="0.5"
        />
        <circle cx="32" cy="48" r="2" fill="currentColor" opacity="0.5" />
      </svg>
      <h3 className="error-state-title">Something went wrong</h3>
      <p className="error-state-message">{message}</p>
      <button className="error-state-button" onClick={onRetry}>
        Try Again
      </button>
    </div>
  );
}
