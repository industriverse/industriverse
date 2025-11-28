/**
 * Main App Component
 * Capsule Launchpad UI
 */

import React, { useState, useEffect } from 'react';
import { Capsule, CapsuleLaunchpad } from '../types/capsule';
import { CapsuleList } from './components/CapsuleList';
import { Header } from './components/Header';
import { EmptyState } from './components/EmptyState';
import { LoadingState } from './components/LoadingState';
import { ErrorState } from './components/ErrorState';
import './App.css';

export default function App() {
  const [launchpad, setLaunchpad] = useState<CapsuleLaunchpad | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);

  /**
   * Load launchpad on mount
   */
  useEffect(() => {
    loadLaunchpad();
  }, []);

  /**
   * Setup WebSocket listeners
   */
  useEffect(() => {
    // WebSocket connected
    const unsubConnected = window.electronAPI.on('ws:connected', () => {
      console.log('[Renderer] WebSocket connected');
      setWsConnected(true);
      loadLaunchpad();
    });

    // WebSocket disconnected
    const unsubDisconnected = window.electronAPI.on('ws:disconnected', () => {
      console.log('[Renderer] WebSocket disconnected');
      setWsConnected(false);
    });

    // WebSocket message
    const unsubMessage = window.electronAPI.on('ws:message', (message) => {
      console.log('[Renderer] WebSocket message:', message.type);
      
      // Refresh launchpad on updates
      if (message.type === 'launchpad_refresh' || message.type === 'capsule_update') {
        loadLaunchpad();
      }
    });

    // WebSocket error
    const unsubError = window.electronAPI.on('ws:error', (data) => {
      console.error('[Renderer] WebSocket error:', data.error);
      setError(data.error);
    });

    // Cleanup
    return () => {
      unsubConnected();
      unsubDisconnected();
      unsubMessage();
      unsubError();
    };
  }, []);

  /**
   * Load launchpad from API
   */
  async function loadLaunchpad() {
    try {
      setLoading(true);
      setError(null);

      const config = await window.electronAPI.invoke('config:get', undefined);
      const data = await window.electronAPI.invoke('capsule:get-launchpad', {
        userId: config.userId,
      });

      setLaunchpad(data);
    } catch (err) {
      console.error('[Renderer] Failed to load launchpad:', err);
      setError(err instanceof Error ? err.message : 'Failed to load capsules');
    } finally {
      setLoading(false);
    }
  }

  /**
   * Execute capsule action
   */
  async function handleAction(capsuleId: string, actionId: string) {
    try {
      const result = await window.electronAPI.invoke('capsule:execute-action', {
        capsuleId,
        actionId,
      });

      if (result.success) {
        // Refresh launchpad
        await loadLaunchpad();
      } else {
        setError(result.message || 'Action failed');
      }
    } catch (err) {
      console.error('[Renderer] Failed to execute action:', err);
      setError(err instanceof Error ? err.message : 'Action failed');
    }
  }

  /**
   * Pin/unpin capsule
   */
  async function handlePin(capsuleId: string, pinned: boolean) {
    try {
      const result = await window.electronAPI.invoke('capsule:pin', {
        capsuleId,
        pinned,
      });

      if (result.success) {
        await loadLaunchpad();
      }
    } catch (err) {
      console.error('[Renderer] Failed to pin capsule:', err);
    }
  }

  /**
   * Hide capsule
   */
  async function handleHide(capsuleId: string) {
    try {
      const result = await window.electronAPI.invoke('capsule:hide', {
        capsuleId,
      });

      if (result.success) {
        await loadLaunchpad();
      }
    } catch (err) {
      console.error('[Renderer] Failed to hide capsule:', err);
    }
  }

  /**
   * Snooze capsule
   */
  async function handleSnooze(capsuleId: string, duration: number) {
    try {
      const result = await window.electronAPI.invoke('capsule:snooze', {
        capsuleId,
        duration,
      });

      if (result.success) {
        await loadLaunchpad();
      }
    } catch (err) {
      console.error('[Renderer] Failed to snooze capsule:', err);
    }
  }

  /**
   * Render
   */
  return (
    <div className="app">
      <Header
        capsuleCount={launchpad?.activeCount || 0}
        wsConnected={wsConnected}
        onRefresh={loadLaunchpad}
      />

      <div className="app-content">
        {loading && <LoadingState />}
        
        {!loading && error && (
          <ErrorState message={error} onRetry={loadLaunchpad} />
        )}
        
        {!loading && !error && launchpad && launchpad.capsules.length === 0 && (
          <EmptyState />
        )}
        
        {!loading && !error && launchpad && launchpad.capsules.length > 0 && (
          <CapsuleList
            capsules={launchpad.capsules}
            onAction={handleAction}
            onPin={handlePin}
            onHide={handleHide}
            onSnooze={handleSnooze}
          />
        )}
      </div>
    </div>
  );
}
