/**
 * Header Component
 * Top bar showing capsule count and connection status
 */

import React from 'react';
import './Header.css';

interface HeaderProps {
  capsuleCount: number;
  wsConnected: boolean;
  onRefresh: () => void;
}

export function Header({ capsuleCount, wsConnected, onRefresh }: HeaderProps) {
  return (
    <div className="header">
      <div className="header-left">
        <h1 className="header-title">Capsules</h1>
        {capsuleCount > 0 && (
          <span className="header-badge">{capsuleCount}</span>
        )}
      </div>

      <div className="header-right">
        <div className={`connection-status ${wsConnected ? 'connected' : 'disconnected'}`}>
          <div className="connection-dot" />
          <span className="connection-text">
            {wsConnected ? 'Live' : 'Offline'}
          </span>
        </div>

        <button
          className="refresh-button"
          onClick={onRefresh}
          title="Refresh capsules"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M13.65 2.35C12.2 0.9 10.21 0 8 0 3.58 0 0.01 3.58 0.01 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L9 7h7V0l-2.35 2.35z"
              fill="currentColor"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
