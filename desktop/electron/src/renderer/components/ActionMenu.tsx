/**
 * ActionMenu Component
 * Context menu for capsule actions (pin, hide, snooze)
 */

import React, { useEffect, useRef } from 'react';
import { Capsule } from '../../types/capsule';
import './ActionMenu.css';

interface ActionMenuProps {
  capsule: Capsule;
  onAction: (action: string) => void;
  onClose: () => void;
}

export function ActionMenu({ capsule, onAction, onClose }: ActionMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  /**
   * Close menu when clicking outside
   */
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  /**
   * Close menu on Escape key
   */
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        onClose();
      }
    }

    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  return (
    <div className="action-menu" ref={menuRef}>
      <button
        className="action-menu-item"
        onClick={() => onAction('pin')}
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M8.5 0L7.29 1.21L9.09 3.01L3.5 8.6V11H5.9L11.49 5.41L13.29 7.21L14.5 6L8.5 0Z"
            fill="currentColor"
          />
        </svg>
        <span>{capsule.isPinned ? 'Unpin' : 'Pin'}</span>
      </button>

      <div className="action-menu-separator" />

      <button
        className="action-menu-item"
        onClick={() => onAction('snooze-1h')}
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M8 0C3.58 0 0 3.58 0 8C0 12.42 3.58 16 8 16C12.42 16 16 12.42 16 8C16 3.58 12.42 0 8 0ZM8 14C4.69 14 2 11.31 2 8C2 4.69 4.69 2 8 2C11.31 2 14 4.69 14 8C14 11.31 11.31 14 8 14ZM8.5 4H7V9L11.25 11.52L12 10.27L8.5 8.25V4Z"
            fill="currentColor"
          />
        </svg>
        <span>Snooze 1 hour</span>
      </button>

      <button
        className="action-menu-item"
        onClick={() => onAction('snooze-4h')}
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M8 0C3.58 0 0 3.58 0 8C0 12.42 3.58 16 8 16C12.42 16 16 12.42 16 8C16 3.58 12.42 0 8 0ZM8 14C4.69 14 2 11.31 2 8C2 4.69 4.69 2 8 2C11.31 2 14 4.69 14 8C14 11.31 11.31 14 8 14ZM8.5 4H7V9L11.25 11.52L12 10.27L8.5 8.25V4Z"
            fill="currentColor"
          />
        </svg>
        <span>Snooze 4 hours</span>
      </button>

      <button
        className="action-menu-item"
        onClick={() => onAction('snooze-1d')}
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M8 0C3.58 0 0 3.58 0 8C0 12.42 3.58 16 8 16C12.42 16 16 12.42 16 8C16 3.58 12.42 0 8 0ZM8 14C4.69 14 2 11.31 2 8C2 4.69 4.69 2 8 2C11.31 2 14 4.69 14 8C14 11.31 11.31 14 8 14ZM8.5 4H7V9L11.25 11.52L12 10.27L8.5 8.25V4Z"
            fill="currentColor"
          />
        </svg>
        <span>Snooze 1 day</span>
      </button>

      <div className="action-menu-separator" />

      <button
        className="action-menu-item destructive"
        onClick={() => onAction('hide')}
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M8 3C3 3 0 8 0 8C0 8 3 13 8 13C13 13 16 8 16 8C16 8 13 3 8 3ZM8 11.5C6.07 11.5 4.5 9.93 4.5 8C4.5 6.07 6.07 4.5 8 4.5C9.93 4.5 11.5 6.07 11.5 8C11.5 9.93 9.93 11.5 8 11.5ZM8 6C6.9 6 6 6.9 6 8C6 9.1 6.9 10 8 10C9.1 10 10 9.1 10 8C10 6.9 9.1 6 8 6Z"
            fill="currentColor"
          />
          <line x1="2" y1="2" x2="14" y2="14" stroke="currentColor" strokeWidth="2" />
        </svg>
        <span>Hide</span>
      </button>
    </div>
  );
}
