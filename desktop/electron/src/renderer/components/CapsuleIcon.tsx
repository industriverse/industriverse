/**
 * CapsuleIcon Component
 * Type-specific icons for capsules
 */

import React from 'react';
import { CapsuleType } from '../../types/capsule';
import './CapsuleIcon.css';

interface CapsuleIconProps {
  type: CapsuleType;
}

export function CapsuleIcon({ type }: CapsuleIconProps) {
  const icons: Record<CapsuleType, JSX.Element> = {
    task: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path
          d="M16 2H4C2.9 2 2 2.9 2 4V16C2 17.1 2.9 18 4 18H16C17.1 18 18 17.1 18 16V4C18 2.9 17.1 2 16 2ZM8 14L4 10L5.41 8.59L8 11.17L14.59 4.58L16 6L8 14Z"
          fill="currentColor"
        />
      </svg>
    ),
    alert: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path
          d="M1 17H19L10 2L1 17ZM11 14H9V12H11V14ZM11 10H9V6H11V10Z"
          fill="currentColor"
        />
      </svg>
    ),
    notification: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path
          d="M10 18C11.1 18 12 17.1 12 16H8C8 17.1 8.9 18 10 18ZM16 12V7.5C16 4.43 14.37 1.86 11.5 1.18V0.5C11.5 -0.17 10.83 -0.5 10 -0.5C9.17 -0.5 8.5 -0.17 8.5 0.5V1.18C5.64 1.86 4 4.42 4 7.5V12L2 14V15H18V14L16 12Z"
          fill="currentColor"
        />
      </svg>
    ),
    decision: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path
          d="M9 2L7.17 4H4C2.9 4 2 4.9 2 6V16C2 17.1 2.9 18 4 18H16C17.1 18 18 17.1 18 16V6C18 4.9 17.1 4 16 4H12.83L11 2H9ZM10 7C11.66 7 13 8.34 13 10C13 11.66 11.66 13 10 13C8.34 13 7 11.66 7 10C7 8.34 8.34 7 10 7Z"
          fill="currentColor"
        />
      </svg>
    ),
    status: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path
          d="M10 2C5.58 2 2 5.58 2 10C2 14.42 5.58 18 10 18C14.42 18 18 14.42 18 10C18 5.58 14.42 2 10 2ZM10 16C6.69 16 4 13.31 4 10C4 6.69 6.69 4 10 4C13.31 4 16 6.69 16 10C16 13.31 13.31 16 10 16ZM10.5 6H9V11L13.25 13.52L14 12.27L10.5 10.25V6Z"
          fill="currentColor"
        />
      </svg>
    ),
    workflow: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path
          d="M4 8H2V16C2 17.1 2.9 18 4 18H12V16H4V8ZM16 2H8C6.9 2 6 2.9 6 4V12C6 13.1 6.9 14 8 14H16C17.1 14 18 13.1 18 12V4C18 2.9 17.1 2 16 2ZM15 11H9V10H15V11ZM15 9H9V8H15V9ZM15 7H9V6H15V7Z"
          fill="currentColor"
        />
      </svg>
    ),
    custom: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path
          d="M10 2L12.12 7.88L18 10L12.12 12.12L10 18L7.88 12.12L2 10L7.88 7.88L10 2Z"
          fill="currentColor"
        />
      </svg>
    ),
  };

  return (
    <div className={`capsule-icon capsule-icon-${type}`}>
      {icons[type] || icons.custom}
    </div>
  );
}
