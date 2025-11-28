/**
 * CapsuleItem Component
 * Individual capsule card with actions
 */

import React, { useState } from 'react';
import { Capsule, CapsuleType, CapsulePriority } from '../../types/capsule';
import { CapsuleIcon } from './CapsuleIcon';
import { ActionMenu } from './ActionMenu';
import './CapsuleItem.css';

interface CapsuleItemProps {
  capsule: Capsule;
  onAction: (capsuleId: string, actionId: string) => void;
  onPin: (capsuleId: string, pinned: boolean) => void;
  onHide: (capsuleId: string) => void;
  onSnooze: (capsuleId: string, duration: number) => void;
}

export function CapsuleItem({
  capsule,
  onAction,
  onPin,
  onHide,
  onSnooze,
}: CapsuleItemProps) {
  const [showMenu, setShowMenu] = useState(false);
  const [expanded, setExpanded] = useState(false);

  /**
   * Get capsule type color
   */
  function getTypeColor(type: CapsuleType): string {
    const colors: Record<CapsuleType, string> = {
      task: 'var(--color-task)',
      alert: 'var(--color-alert)',
      notification: 'var(--color-notification)',
      decision: 'var(--color-decision)',
      status: 'var(--color-status)',
      workflow: 'var(--color-workflow)',
      custom: 'var(--color-accent)',
    };
    return colors[type] || 'var(--color-accent)';
  }

  /**
   * Get priority label
   */
  function getPriorityLabel(priority: CapsulePriority): string {
    const labels: Record<CapsulePriority, string> = {
      critical: '🔴 Critical',
      high: '🟠 High',
      normal: '🟢 Normal',
      low: '⚪ Low',
    };
    return labels[priority] || '';
  }

  /**
   * Format timestamp
   */
  function formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  }

  /**
   * Handle primary action click
   */
  function handlePrimaryAction() {
    const primaryAction = capsule.actions.find((a) => a.type === 'primary');
    if (primaryAction) {
      onAction(capsule.id, primaryAction.id);
    }
  }

  /**
   * Handle menu action
   */
  function handleMenuAction(action: string) {
    setShowMenu(false);

    switch (action) {
      case 'pin':
        onPin(capsule.id, !capsule.isPinned);
        break;
      case 'hide':
        onHide(capsule.id);
        break;
      case 'snooze-1h':
        onSnooze(capsule.id, 3600);
        break;
      case 'snooze-4h':
        onSnooze(capsule.id, 14400);
        break;
      case 'snooze-1d':
        onSnooze(capsule.id, 86400);
        break;
      default:
        // Custom action
        onAction(capsule.id, action);
    }
  }

  const primaryAction = capsule.actions.find((a) => a.type === 'primary');
  const secondaryActions = capsule.actions.filter((a) => a.type === 'secondary');

  return (
    <div
      className={`capsule-item ${expanded ? 'expanded' : ''} priority-${capsule.priority}`}
      style={{ '--capsule-color': getTypeColor(capsule.type) } as React.CSSProperties}
    >
      {/* Header */}
      <div className="capsule-header">
        <div className="capsule-header-left">
          <CapsuleIcon type={capsule.type} />
          <div className="capsule-info">
            <h3 className="capsule-title">{capsule.title}</h3>
            <div className="capsule-meta">
              <span className="capsule-type">{capsule.type}</span>
              <span className="capsule-separator">•</span>
              <span className="capsule-time">{formatTimestamp(capsule.updatedAt)}</span>
            </div>
          </div>
        </div>

        <div className="capsule-header-right">
          {capsule.badgeCount && capsule.badgeCount > 0 && (
            <span className="capsule-badge">{capsule.badgeCount}</span>
          )}
          
          <button
            className="capsule-menu-button"
            onClick={() => setShowMenu(!showMenu)}
            title="More options"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="3" r="1.5" fill="currentColor" />
              <circle cx="8" cy="8" r="1.5" fill="currentColor" />
              <circle cx="8" cy="13" r="1.5" fill="currentColor" />
            </svg>
          </button>
        </div>
      </div>

      {/* Description (if expanded) */}
      {expanded && capsule.description && (
        <div className="capsule-description">
          {capsule.description}
        </div>
      )}

      {/* Metadata (if expanded) */}
      {expanded && capsule.metadata && Object.keys(capsule.metadata).length > 0 && (
        <div className="capsule-metadata">
          {Object.entries(capsule.metadata).map(([key, value]) => (
            <div key={key} className="capsule-metadata-item">
              <span className="capsule-metadata-key">{key}:</span>
              <span className="capsule-metadata-value">{String(value)}</span>
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="capsule-actions">
        {primaryAction && (
          <button
            className="capsule-action-button primary"
            onClick={handlePrimaryAction}
          >
            {primaryAction.label}
          </button>
        )}

        {secondaryActions.length > 0 && (
          <button
            className="capsule-action-button secondary"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? 'Less' : 'More'}
          </button>
        )}
      </div>

      {/* Secondary actions (if expanded) */}
      {expanded && secondaryActions.length > 0 && (
        <div className="capsule-secondary-actions">
          {secondaryActions.map((action) => (
            <button
              key={action.id}
              className="capsule-action-button secondary"
              onClick={() => onAction(capsule.id, action.id)}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}

      {/* Action menu */}
      {showMenu && (
        <ActionMenu
          capsule={capsule}
          onAction={handleMenuAction}
          onClose={() => setShowMenu(false)}
        />
      )}

      {/* Priority indicator */}
      {capsule.priority !== 'normal' && (
        <div className="capsule-priority-indicator" />
      )}
    </div>
  );
}
