# Industriverse UI/UX Layer Guide

## Introduction

The UI/UX Layer provides the visual interface and interaction patterns for the Industriverse Framework. It delivers a cohesive, intuitive user experience across all applications built on the framework, with special attention to industrial contexts and user roles. This layer implements the "Universal Skin" concept with Dynamic Agent Capsules, enabling contextual, adaptive interfaces across devices and platforms.

## Architecture Overview

The UI/UX Layer is designed as a modular, component-based system that supports multiple deployment targets while maintaining a consistent design language.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            UI/UX LAYER                                  │
│                                                                         │
│  ┌─────────────────────────┐      ┌─────────────────────────┐           │
│  │                         │      │                         │           │
│  │   Design System         │      │    Component Library    │           │
│  │   (Tokens, Patterns)    │      │    (React, Web Comp.)   │           │
│  │                         │      │                         │           │
│  └────────────┬────────────┘      └────────────┬────────────┘           │
│               │                                │                        │
│  ┌────────────┴────────────┐      ┌────────────┴────────────┐           │
│  │                         │      │                         │           │
│  │   Dynamic Agent         │      │    View Templates       │           │
│  │   Capsules              │      │    (Role-based)         │           │
│  │                         │      │                         │           │
│  └────────────┬────────────┘      └────────────┬────────────┘           │
│               │                                │                        │
│  ┌────────────┴────────────────────────────────┴────────────┐           │
│  │                                                         │           │
│  │                     Core Services                       │           │
│  │                                                         │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  │             │  │             │  │             │  │             │  │
│  │  │ State       │  │ Protocol    │  │ Theme       │  │ Layout      │  │
│  │  │ Management  │  │ Bridge      │  │ Engine      │  │ Engine      │  │
│  │  │             │  │             │  │             │  │             │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
│  │                                                         │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  │             │  │             │  │             │  │             │  │
│  │  │ Notification│  │ Auth        │  │ Analytics   │  │ Accessibility│  │
│  │  │ System      │  │ Integration │  │ Service     │  │ Service     │  │
│  │  │             │  │             │  │             │  │             │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
│  └─────────────────────────────────────────────────────────┘           │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     Platform Adapters                           │    │
│  │                                                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    
│  │  │             │  │             │  │             │  │             │  │
│  │  │ Web         │  │ Mobile      │  │ Desktop     │  │ AR/VR       │  │
│  │  │ (Browser)   │  │ (Native)    │  │ (Electron)  │  │ (WebXR)     │  │
│  │  │             │  │             │  │             │  │             │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Design System**: The foundational visual language and interaction patterns.
   - **Design Tokens**: Variables for colors, typography, spacing, etc.
   - **Interaction Patterns**: Standard behaviors for industrial contexts.
   - **Accessibility Guidelines**: Ensuring usability for all users.
   - **Industry-Specific Patterns**: Specialized UI patterns for industrial domains.

2. **Component Library**: Reusable UI building blocks.
   - **Base Components**: Buttons, inputs, cards, tables, etc.
   - **Composite Components**: Charts, dashboards, forms, etc.
   - **Industrial Components**: Equipment visualizations, process diagrams, etc.
   - **Agent Avatar Components**: Visual representations of AI agents.

3. **Dynamic Agent Capsules**: The "Universal Skin" concept.
   - **Capsule Container**: Adaptive UI element for agent representation.
   - **Context Display**: Shows agent status and current context.
   - **Action Menu**: Provides relevant actions for the agent.
   - **Notification System**: Alerts users to important events.
   - **Pinning Mechanism**: Allows capsules to be pinned to different interfaces.

4. **View Templates**: Pre-built layouts for common scenarios.
   - **Role-Based Views**: Master, Domain, Process, and Agent views.
   - **Dashboard Templates**: Monitoring, analytics, control panels.
   - **Workflow Views**: Task management, process visualization.
   - **Configuration Views**: System setup, preferences.

5. **Core Services**: Supporting functionality for the UI layer.
   - **State Management**: Manages UI state and data flow.
   - **Protocol Bridge**: Connects to MCP/A2A for data and events.
   - **Theme Engine**: Handles theming and customization.
   - **Layout Engine**: Manages responsive layouts.
   - **Notification System**: Manages alerts and notifications.
   - **Auth Integration**: Handles authentication and authorization.
   - **Analytics Service**: Tracks user interactions.
   - **Accessibility Service**: Ensures compliance with accessibility standards.

6. **Platform Adapters**: Enables deployment to different platforms.
   - **Web**: Browser-based interfaces.
   - **Mobile**: Native mobile applications.
   - **Desktop**: Electron-based desktop applications.
   - **AR/VR**: Augmented and virtual reality interfaces.

## Design System

The Design System provides a consistent visual language and interaction patterns across all Industriverse applications.

### Design Tokens

Design tokens are the atomic values that define the visual properties of the UI.

```typescript
// Example: design-tokens.ts
export const tokens = {
  colors: {
    // Primary palette
    primary: {
      50: '#E3F2FD',
      100: '#BBDEFB',
      200: '#90CAF9',
      300: '#64B5F6',
      400: '#42A5F5',
      500: '#2196F3', // Primary color
      600: '#1E88E5',
      700: '#1976D2',
      800: '#1565C0',
      900: '#0D47A1',
    },
    // Secondary palette
    secondary: {
      // ...similar structure
    },
    // Semantic colors
    semantic: {
      success: '#4CAF50',
      warning: '#FF9800',
      error: '#F44336',
      info: '#2196F3',
    },
    // Status colors for industrial contexts
    status: {
      normal: '#4CAF50',
      warning: '#FF9800',
      alarm: '#F44336',
      offline: '#9E9E9E',
      maintenance: '#673AB7',
    },
    // Neutrals
    neutral: {
      white: '#FFFFFF',
      black: '#000000',
      gray: {
        50: '#FAFAFA',
        // ...more gray shades
        900: '#212121',
      },
    },
    // Industry-specific colors
    industry: {
      manufacturing: {
        machine: '#1565C0',
        process: '#00897B',
        material: '#F57C00',
      },
      energy: {
        generation: '#7CB342',
        distribution: '#FFA000',
        consumption: '#5D4037',
      },
      // ...other industries
    },
  },
  typography: {
    fontFamily: {
      base: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      monospace: '"Roboto Mono", monospace',
    },
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      md: '1rem',       // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem',  // 36px
    },
    fontWeight: {
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.2,
      base: 1.5,
      relaxed: 1.75,
    },
  },
  spacing: {
    '0': '0',
    '1': '0.25rem',  // 4px
    '2': '0.5rem',   // 8px
    '3': '0.75rem',  // 12px
    '4': '1rem',     // 16px
    '5': '1.25rem',  // 20px
    '6': '1.5rem',   // 24px
    '8': '2rem',     // 32px
    '10': '2.5rem',  // 40px
    '12': '3rem',    // 48px
    '16': '4rem',    // 64px
    '20': '5rem',    // 80px
    '24': '6rem',    // 96px
  },
  borderRadius: {
    none: '0',
    sm: '0.125rem',  // 2px
    md: '0.25rem',   // 4px
    lg: '0.5rem',    // 8px
    xl: '1rem',      // 16px
    full: '9999px',
  },
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
  zIndex: {
    hide: -1,
    base: 0,
    raised: 1,
    dropdown: 1000,
    sticky: 1100,
    overlay: 1300,
    modal: 1400,
    popover: 1500,
    toast: 1600,
    tooltip: 1700,
  },
  // Animation tokens
  animation: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms',
    },
    easing: {
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    },
  },
};
```

### Interaction Patterns

Standardized interaction patterns ensure consistency across the framework.

```typescript
// Example: interaction-patterns.ts
export const interactionPatterns = {
  // Hover states
  hover: {
    scale: 1.02,
    transition: `transform ${tokens.animation.duration.fast} ${tokens.animation.easing.easeOut}`,
  },
  
  // Focus states
  focus: {
    outlineColor: tokens.colors.primary[500],
    outlineWidth: '2px',
    outlineOffset: '2px',
    outlineStyle: 'solid',
  },
  
  // Active states
  active: {
    scale: 0.98,
  },
  
  // Drag and drop
  dragAndDrop: {
    dragStart: {
      scale: 1.05,
      opacity: 0.8,
      shadow: tokens.shadows.lg,
    },
    dragOver: {
      borderColor: tokens.colors.primary[500],
      backgroundColor: tokens.colors.primary[50],
    },
  },
  
  // Industrial-specific patterns
  industrial: {
    // Confirmation for critical actions
    criticalAction: {
      confirmationRequired: true,
      confirmationStyle: 'modal', // or 'inline'
      confirmationTimeout: 5000, // ms
    },
    
    // Equipment status indication
    equipmentStatus: {
      normal: {
        borderColor: tokens.colors.status.normal,
        pulseAnimation: false,
      },
      warning: {
        borderColor: tokens.colors.status.warning,
        pulseAnimation: true,
        pulseSpeed: tokens.animation.duration.slow,
      },
      alarm: {
        borderColor: tokens.colors.status.alarm,
        pulseAnimation: true,
        pulseSpeed: tokens.animation.duration.fast,
      },
    },
  },
};
```

## Component Library

The Component Library provides reusable UI building blocks for constructing Industriverse applications.

### Base Components

```tsx
// Example: Button.tsx
import React from 'react';
import { tokens } from '../design-system/design-tokens';

type ButtonVariant = 'primary' | 'secondary' | 'tertiary' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps {
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  onClick,
  children,
}) => {
  // Styles based on variant
  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: tokens.colors.primary[500],
          color: tokens.colors.neutral.white,
          borderColor: tokens.colors.primary[500],
          '&:hover': {
            backgroundColor: tokens.colors.primary[600],
          },
        };
      case 'secondary':
        return {
          backgroundColor: 'transparent',
          color: tokens.colors.primary[500],
          borderColor: tokens.colors.primary[500],
          '&:hover': {
            backgroundColor: tokens.colors.primary[50],
          },
        };
      case 'tertiary':
        return {
          backgroundColor: 'transparent',
          color: tokens.colors.primary[500],
          borderColor: 'transparent',
          '&:hover': {
            backgroundColor: tokens.colors.primary[50],
          },
        };
      case 'danger':
        return {
          backgroundColor: tokens.colors.semantic.error,
          color: tokens.colors.neutral.white,
          borderColor: tokens.colors.semantic.error,
          '&:hover': {
            backgroundColor: '#D32F2F', // Darker red
          },
        };
    }
  };

  // Styles based on size
  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return {
          padding: `${tokens.spacing[1]} ${tokens.spacing[2]}`,
          fontSize: tokens.typography.fontSize.sm,
        };
      case 'md':
        return {
          padding: `${tokens.spacing[2]} ${tokens.spacing[4]}`,
          fontSize: tokens.typography.fontSize.md,
        };
      case 'lg':
        return {
          padding: `${tokens.spacing[3]} ${tokens.spacing[6]}`,
          fontSize: tokens.typography.fontSize.lg,
        };
    }
  };

  // Combined styles
  const buttonStyles = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: tokens.borderRadius.md,
    fontWeight: tokens.typography.fontWeight.medium,
    border: '1px solid',
    transition: `all ${tokens.animation.duration.fast} ${tokens.animation.easing.easeInOut}`,
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.6 : 1,
    width: fullWidth ? '100%' : 'auto',
    ...getVariantStyles(),
    ...getSizeStyles(),
  };

  // Loading indicator
  const LoadingSpinner = () => (
    <svg
      className="animate-spin -ml-1 mr-2 h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      ></circle>
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
    </svg>
  );

  return (
    <button
      style={buttonStyles as React.CSSProperties}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading && <LoadingSpinner />}
      {icon && iconPosition === 'left' && !loading && (
        <span style={{ marginRight: tokens.spacing[2] }}>{icon}</span>
      )}
      {children}
      {icon && iconPosition === 'right' && (
        <span style={{ marginLeft: tokens.spacing[2] }}>{icon}</span>
      )}
    </button>
  );
};
```

### Industrial Components

```tsx
// Example: EquipmentStatusCard.tsx
import React from 'react';
import { tokens } from '../design-system/design-tokens';
import { interactionPatterns } from '../design-system/interaction-patterns';
import { Card } from './Card';
import { Text } from './Text';
import { Badge } from './Badge';
import { Icon } from './Icon';

type EquipmentStatus = 'normal' | 'warning' | 'alarm' | 'offline' | 'maintenance';

interface EquipmentStatusCardProps {
  equipmentId: string;
  equipmentName: string;
  status: EquipmentStatus;
  lastUpdated: string;
  metrics?: {
    label: string;
    value: string | number;
    unit?: string;
  }[];
  onClick?: () => void;
}

export const EquipmentStatusCard: React.FC<EquipmentStatusCardProps> = ({
  equipmentId,
  equipmentName,
  status,
  lastUpdated,
  metrics = [],
  onClick,
}) => {
  // Get status color and icon
  const getStatusInfo = () => {
    switch (status) {
      case 'normal':
        return {
          color: tokens.colors.status.normal,
          icon: 'check-circle',
          label: 'Normal',
        };
      case 'warning':
        return {
          color: tokens.colors.status.warning,
          icon: 'alert-triangle',
          label: 'Warning',
        };
      case 'alarm':
        return {
          color: tokens.colors.status.alarm,
          icon: 'alert-octagon',
          label: 'Alarm',
        };
      case 'offline':
        return {
          color: tokens.colors.status.offline,
          icon: 'power-off',
          label: 'Offline',
        };
      case 'maintenance':
        return {
          color: tokens.colors.status.maintenance,
          icon: 'tool',
          label: 'Maintenance',
        };
    }
  };

  const statusInfo = getStatusInfo();

  // Animation for warning and alarm states
  const getPulseAnimation = () => {
    if (status === 'warning' || status === 'alarm') {
      const duration = status === 'alarm' 
        ? interactionPatterns.industrial.equipmentStatus.alarm.pulseSpeed
        : interactionPatterns.industrial.equipmentStatus.warning.pulseSpeed;
      
      return {
        animation: `pulse ${duration} infinite`,
        '@keyframes pulse': {
          '0%': {
            boxShadow: `0 0 0 0 ${statusInfo.color}40`,
          },
          '70%': {
            boxShadow: `0 0 0 10px ${statusInfo.color}00`,
          },
          '100%': {
            boxShadow: `0 0 0 0 ${statusInfo.color}00`,
          },
        },
      };
    }
    return {};
  };

  return (
    <Card
      onClick={onClick}
      style={{
        borderLeft: `4px solid ${statusInfo.color}`,
        cursor: onClick ? 'pointer' : 'default',
        transition: `all ${tokens.animation.duration.normal} ${tokens.animation.easing.easeInOut}`,
        ...getPulseAnimation(),
      }}
    >
      <div style={{ padding: tokens.spacing[4] }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: tokens.spacing[3]
        }}>
          <div>
            <Text variant="sm" color={tokens.colors.neutral.gray[600]}>
              ID: {equipmentId}
            </Text>
            <Text variant="xl" weight="semibold">
              {equipmentName}
            </Text>
          </div>
          <Badge 
            color={statusInfo.color}
            icon={statusInfo.icon}
          >
            {statusInfo.label}
          </Badge>
        </div>
        
        {metrics.length > 0 && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: `repeat(${Math.min(metrics.length, 3)}, 1fr)`,
            gap: tokens.spacing[4],
            marginBottom: tokens.spacing[3]
          }}>
            {metrics.map((metric, index) => (
              <div key={index}>
                <Text variant="sm" color={tokens.colors.neutral.gray[600]}>
                  {metric.label}
                </Text>
                <Text variant="lg" weight="medium">
                  {metric.value}
                  {metric.unit && (
                    <Text as="span" variant="sm" color={tokens.colors.neutral.gray[600]}>
                      {' '}{metric.unit}
                    </Text>
                  )}
                </Text>
              </div>
            ))}
          </div>
        )}
        
        <div style={{ 
          display: 'flex', 
          justifyContent: 'flex-end',
          alignItems: 'center',
          marginTop: tokens.spacing[2]
        }}>
          <Icon name="clock" size={16} color={tokens.colors.neutral.gray[400]} />
          <Text variant="xs" color={tokens.colors.neutral.gray[400]} style={{ marginLeft: tokens.spacing[1] }}>
            Updated: {lastUpdated}
          </Text>
        </div>
      </div>
    </Card>
  );
};
```

## Dynamic Agent Capsules

The Dynamic Agent Capsules implement the "Universal Skin" concept, providing a consistent way to represent and interact with AI agents across the framework.

### Capsule Container

```tsx
// Example: AgentCapsule.tsx
import React, { useState } from 'react';
import { tokens } from '../design-system/design-tokens';
import { Avatar } from './Avatar';
import { Icon } from './Icon';
import { Text } from './Text';
import { Menu, MenuItem } from './Menu';

interface AgentCapsuleProps {
  agentId: string;
  agentName: string;
  avatarUrl: string;
  status: 'idle' | 'working' | 'error' | 'success';
  contextSummary: string;
  sourceContext?: string;
  onAction?: (action: string) => void;
  isPinned?: boolean;
  onTogglePin?: () => void;
  size?: 'sm' | 'md' | 'lg';
}

export const AgentCapsule: React.FC<AgentCapsuleProps> = ({
  agentId,
  agentName,
  avatarUrl,
  status,
  contextSummary,
  sourceContext,
  onAction,
  isPinned = false,
  onTogglePin,
  size = 'md',
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  
  // Get status color and animation
  const getStatusStyles = () => {
    switch (status) {
      case 'idle':
        return {
          color: tokens.colors.neutral.gray[400],
          animation: 'none',
        };
      case 'working':
        return {
          color: tokens.colors.primary[500],
          animation: `pulse 2s infinite ${tokens.animation.easing.easeInOut}`,
        };
      case 'error':
        return {
          color: tokens.colors.semantic.error,
          animation: 'none',
        };
      case 'success':
        return {
          color: tokens.colors.semantic.success,
          animation: 'none',
        };
    }
  };
  
  // Size-based styles
  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return {
          height: '40px',
          expandedHeight: '120px',
          avatarSize: 28,
          fontSize: tokens.typography.fontSize.xs,
        };
      case 'md':
        return {
          height: '56px',
          expandedHeight: '160px',
          avatarSize: 40,
          fontSize: tokens.typography.fontSize.sm,
        };
      case 'lg':
        return {
          height: '72px',
          expandedHeight: '200px',
          avatarSize: 56,
          fontSize: tokens.typography.fontSize.md,
        };
    }
  };
  
  const statusStyles = getStatusStyles();
  const sizeStyles = getSizeStyles();
  
  // Actions menu items
  const actionItems = [
    { id: 'fork', label: 'Fork', icon: 'git-branch' },
    { id: 'migrate', label: 'Migrate', icon: 'move' },
    { id: 'suspend', label: 'Suspend', icon: 'pause' },
    { id: 'rescope', label: 'Rescope', icon: 'edit' },
  ];
  
  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: '360px',
        height: isExpanded ? sizeStyles.expandedHeight : sizeStyles.height,
        backgroundColor: tokens.colors.neutral.white,
        borderRadius: tokens.borderRadius.lg,
        boxShadow: tokens.shadows.md,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        transition: `all ${tokens.animation.duration.normal} ${tokens.animation.easing.easeInOut}`,
        border: `1px solid ${tokens.colors.neutral.gray[200]}`,
        borderLeft: `3px solid ${statusStyles.color}`,
      }}
    >
      {/* Header - Always visible */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          padding: `${tokens.spacing[2]} ${tokens.spacing[3]}`,
          height: sizeStyles.height,
          cursor: 'pointer',
          borderBottom: isExpanded ? `1px solid ${tokens.colors.neutral.gray[200]}` : 'none',
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {/* Status indicator and avatar */}
        <div style={{ position: 'relative', marginRight: tokens.spacing[3] }}>
          <Avatar
            src={avatarUrl}
            alt={agentName}
            size={sizeStyles.avatarSize}
          />
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              right: 0,
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: statusStyles.color,
              border: `2px solid ${tokens.colors.neutral.white}`,
              animation: statusStyles.animation,
            }}
          />
        </div>
        
        {/* Agent name and context summary */}
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <Text variant="sm" weight="semibold" truncate>
            {agentName}
          </Text>
          <Text variant="xs" color={tokens.colors.neutral.gray[600]} truncate>
            {contextSummary}
          </Text>
        </div>
        
        {/* Action buttons */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
          {onTogglePin && (
            <button
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: tokens.spacing[1],
                marginRight: tokens.spacing[1],
                color: isPinned ? tokens.colors.primary[500] : tokens.colors.neutral.gray[400],
              }}
              onClick={(e) => {
                e.stopPropagation();
                onTogglePin();
              }}
            >
              <Icon name={isPinned ? 'pin' : 'pin-outline'} size={16} />
            </button>
          )}
          
          <button
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: tokens.spacing[1],
              color: tokens.colors.neutral.gray[400],
            }}
            onClick={(e) => {
              e.stopPropagation();
              setMenuOpen(!menuOpen);
            }}
          >
            <Icon name="more-vertical" size={16} />
          </button>
          
          {menuOpen && (
            <Menu
              items={actionItems}
              onSelect={(id) => {
                setMenuOpen(false);
                onAction && onAction(id);
              }}
              onClose={() => setMenuOpen(false)}
            />
          )}
          
          <button
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: tokens.spacing[1],
              marginLeft: tokens.spacing[1],
              color: tokens.colors.neutral.gray[400],
              transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: `transform ${tokens.animation.duration.fast} ${tokens.animation.easing.easeInOut}`,
            }}
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
          >
            <Icon name="chevron-down" size={16} />
          </button>
        </div>
      </div>
      
      {/* Expanded content */}
      {isExpanded && (
        <div style={{ padding: tokens.spacing[3], overflow: 'auto' }}>
          {sourceContext && (
            <div style={{ marginBottom: tokens.spacing[3] }}>
              <Text variant="xs" weight="medium" color={tokens.colors.neutral.gray[500]}>
                Source Context
              </Text>
              <Text variant="sm" style={{ marginTop: tokens.spacing[1] }}>
                {sourceContext}
              </Text>
            </div>
          )}
          
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: tokens.spacing[2] }}>
            {actionItems.map((item) => (
              <button
                key={item.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: `${tokens.spacing[1]} ${tokens.spacing[2]}`,
                  backgroundColor: tokens.colors.neutral.gray[100],
                  border: 'none',
                  borderRadius: tokens.borderRadius.md,
                  cursor: 'pointer',
                  fontSize: tokens.typography.fontSize.xs,
                  color: tokens.colors.neutral.gray[800],
                }}
                onClick={() => onAction && onAction(item.id)}
              >
                <Icon name={item.icon} size={14} style={{ marginRight: tokens.spacing[1] }} />
                {item.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

### Capsule Manager

```tsx
// Example: AgentCapsuleManager.tsx
import React, { useState, useEffect } from 'react';
import { tokens } from '../design-system/design-tokens';
import { AgentCapsule } from './AgentCapsule';

interface Agent {
  id: string;
  name: string;
  avatarUrl: string;
  status: 'idle' | 'working' | 'error' | 'success';
  contextSummary: string;
  sourceContext?: string;
}

interface AgentCapsuleManagerProps {
  agents: Agent[];
  onAgentAction: (agentId: string, action: string) => void;
  layout?: 'dock' | 'grid' | 'list';
  maxVisible?: number;
}

export const AgentCapsuleManager: React.FC<AgentCapsuleManagerProps> = ({
  agents,
  onAgentAction,
  layout = 'dock',
  maxVisible = 5,
}) => {
  const [pinnedAgents, setPinnedAgents] = useState<string[]>([]);
  const [visibleAgents, setVisibleAgents] = useState<Agent[]>([]);
  const [hiddenCount, setHiddenCount] = useState(0);
  
  // Update visible agents based on pinned status and maxVisible
  useEffect(() => {
    // First, include all pinned agents
    const pinned = agents.filter(agent => pinnedAgents.includes(agent.id));
    
    // Then add non-pinned agents until we reach maxVisible
    const nonPinned = agents.filter(agent => !pinnedAgents.includes(agent.id));
    const visible = [...pinned];
    
    const remainingSlots = maxVisible - pinned.length;
    if (remainingSlots > 0) {
      visible.push(...nonPinned.slice(0, remainingSlots));
    }
    
    setVisibleAgents(visible);
    setHiddenCount(Math.max(0, agents.length - visible.length));
  }, [agents, pinnedAgents, maxVisible]);
  
  // Toggle pin status for an agent
  const handleTogglePin = (agentId: string) => {
    setPinnedAgents(prev => 
      prev.includes(agentId)
        ? prev.filter(id => id !== agentId)
        : [...prev, agentId]
    );
  };
  
  // Get layout-specific styles
  const getLayoutStyles = () => {
    switch (layout) {
      case 'dock':
        return {
          container: {
            display: 'flex',
            flexDirection: 'row' as const,
            gap: tokens.spacing[2],
            overflowX: 'auto' as const,
            padding: tokens.spacing[2],
          },
          capsule: {
            width: '280px',
            flexShrink: 0,
          },
        };
      case 'grid':
        return {
          container: {
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: tokens.spacing[4],
            padding: tokens.spacing[4],
          },
          capsule: {},
        };
      case 'list':
        return {
          container: {
            display: 'flex',
            flexDirection: 'column' as const,
            gap: tokens.spacing[2],
            padding: tokens.spacing[2],
          },
          capsule: {
            width: '100%',
          },
        };
    }
  };
  
  const layoutStyles = getLayoutStyles();
  
  return (
    <div>
      <div style={layoutStyles.container}>
        {visibleAgents.map(agent => (
          <div key={agent.id} style={layoutStyles.capsule}>
            <AgentCapsule
              agentId={agent.id}
              agentName={agent.name}
              avatarUrl={agent.avatarUrl}
              status={agent.status}
              contextSummary={agent.contextSummary}
              sourceContext={agent.sourceContext}
              isPinned={pinnedAgents.includes(agent.id)}
              onTogglePin={() => handleTogglePin(agent.id)}
              onAction={(action) => onAgentAction(agent.id, action)}
              size={layout === 'list' ? 'sm' : 'md'}
            />
          </div>
        ))}
        
        {hiddenCount > 0 && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: tokens.colors.neutral.gray[100],
              borderRadius: tokens.borderRadius.lg,
              padding: tokens.spacing[3],
              fontSize: tokens.typography.fontSize.sm,
              color: tokens.colors.neutral.gray[600],
              cursor: 'pointer',
              ...(layout === 'dock' ? { width: '120px', flexShrink: 0 } : {}),
            }}
            onClick={() => {/* Show all agents dialog */}}
          >
            +{hiddenCount} more
          </div>
        )}
      </div>
    </div>
  );
};
```

## View Templates

View templates provide pre-built layouts for common scenarios, with a focus on role-based views.

### Role-Based Dashboard

```tsx
// Example: RoleBasedDashboard.tsx
import React, { useState } from 'react';
import { tokens } from '../design-system/design-tokens';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Card } from './Card';
import { Text } from './Text';
import { Tabs, Tab } from './Tabs';
import { AgentCapsuleManager } from './AgentCapsuleManager';
import { EquipmentStatusCard } from './EquipmentStatusCard';
import { MetricsChart } from './MetricsChart';
import { AlertsList } from './AlertsList';

type UserRole = 'master' | 'domain' | 'process' | 'agent';

interface RoleBasedDashboardProps {
  userRole: UserRole;
  userName: string;
  userAvatar?: string;
  agents: any[]; // Agent data
  equipment?: any[]; // Equipment data
  metrics?: any[]; // Metrics data
  alerts?: any[]; // Alerts data
  onAgentAction: (agentId: string, action: string) => void;
  onEquipmentSelect?: (equipmentId: string) => void;
  onAlertAction?: (alertId: string, action: string) => void;
}

export const RoleBasedDashboard: React.FC<RoleBasedDashboardProps> = ({
  userRole,
  userName,
  userAvatar,
  agents,
  equipment = [],
  metrics = [],
  alerts = [],
  onAgentAction,
  onEquipmentSelect,
  onAlertAction,
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Role-specific configurations
  const getRoleConfig = () => {
    switch (userRole) {
      case 'master':
        return {
          title: 'Master Dashboard',
          description: 'Enterprise-wide overview and strategic insights',
          tabs: [
            { id: 'overview', label: 'Overview' },
            { id: 'domains', label: 'Domains' },
            { id: 'analytics', label: 'Analytics' },
            { id: 'governance', label: 'Governance' },
          ],
          metricsTitle: 'Enterprise Metrics',
          equipmentTitle: 'Critical Systems',
          alertsTitle: 'High Priority Alerts',
        };
      case 'domain':
        return {
          title: 'Domain Dashboard',
          description: 'Domain-specific monitoring and management',
          tabs: [
            { id: 'overview', label: 'Overview' },
            { id: 'processes', label: 'Processes' },
            { id: 'resources', label: 'Resources' },
            { id: 'performance', label: 'Performance' },
          ],
          metricsTitle: 'Domain Metrics',
          equipmentTitle: 'Domain Equipment',
          alertsTitle: 'Domain Alerts',
        };
      case 'process':
        return {
          title: 'Process Dashboard',
          description: 'Process monitoring and operational control',
          tabs: [
            { id: 'overview', label: 'Overview' },
            { id: 'equipment', label: 'Equipment' },
            { id: 'workflow', label: 'Workflow' },
            { id: 'maintenance', label: 'Maintenance' },
          ],
          metricsTitle: 'Process Metrics',
          equipmentTitle: 'Process Equipment',
          alertsTitle: 'Process Alerts',
        };
      case 'agent':
        return {
          title: 'Agent Dashboard',
          description: 'Agent monitoring and task management',
          tabs: [
            { id: 'overview', label: 'Overview' },
            { id: 'tasks', label: 'Tasks' },
            { id: 'history', label: 'History' },
            { id: 'settings', label: 'Settings' },
          ],
          metricsTitle: 'Agent Metrics',
          equipmentTitle: 'Assigned Equipment',
          alertsTitle: 'Agent Alerts',
        };
    }
  };
  
  const roleConfig = getRoleConfig();
  
  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: tokens.colors.neutral.gray[100] }}>
      {/* Sidebar */}
      <Sidebar userRole={userRole} userName={userName} userAvatar={userAvatar} />
      
      {/* Main content */}
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Header title={roleConfig.title} description={roleConfig.description} />
        
        {/* Tabs */}
        <Tabs activeTab={activeTab} onChange={setActiveTab}>
          {roleConfig.tabs.map(tab => (
            <Tab key={tab.id} id={tab.id} label={tab.label} />
          ))}
        </Tabs>
        
        {/* Dashboard content */}
        <div style={{ flex: 1, overflow: 'auto', padding: tokens.spacing[4] }}>
          {activeTab === 'overview' && (
            <>
              {/* Agent Capsules */}
              <Card style={{ marginBottom: tokens.spacing[4] }}>
                <div style={{ padding: tokens.spacing[4] }}>
                  <Text variant="lg" weight="semibold" style={{ marginBottom: tokens.spacing[3] }}>
                    Active Agents
                  </Text>
                  <AgentCapsuleManager
                    agents={agents}
                    onAgentAction={onAgentAction}
                    layout="dock"
                    maxVisible={5}
                  />
                </div>
              </Card>
              
              {/* Metrics */}
              <Card style={{ marginBottom: tokens.spacing[4] }}>
                <div style={{ padding: tokens.spacing[4] }}>
                  <Text variant="lg" weight="semibold" style={{ marginBottom: tokens.spacing[3] }}>
                    {roleConfig.metricsTitle}
                  </Text>
                  <div style={{ height: '300px' }}>
                    <MetricsChart data={metrics} />
                  </div>
                </div>
              </Card>
              
              {/* Two-column layout for equipment and alerts */}
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
                gap: tokens.spacing[4] 
              }}>
                {/* Equipment */}
                <Card>
                  <div style={{ padding: tokens.spacing[4] }}>
                    <Text variant="lg" weight="semibold" style={{ marginBottom: tokens.spacing[3] }}>
                      {roleConfig.equipmentTitle}
                    </Text>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: tokens.spacing[3] }}>
                      {equipment.slice(0, 3).map(item => (
                        <EquipmentStatusCard
                          key={item.id}
                          equipmentId={item.id}
                          equipmentName={item.name}
                          status={item.status}
                          lastUpdated={item.lastUpdated}
                          metrics={item.metrics}
                          onClick={() => onEquipmentSelect && onEquipmentSelect(item.id)}
                        />
                      ))}
                    </div>
                  </div>
                </Card>
                
                {/* Alerts */}
                <Card>
                  <div style={{ padding: tokens.spacing[4] }}>
                    <Text variant="lg" weight="semibold" style={{ marginBottom: tokens.spacing[3] }}>
                      {roleConfig.alertsTitle}
                    </Text>
                    <AlertsList
                      alerts={alerts}
                      onAction={onAlertAction}
                      maxItems={5}
                    />
                  </div>
                </Card>
              </div>
            </>
          )}
          
          {/* Other tab content would be implemented here */}
        </div>
      </div>
    </div>
  );
};
```

## Core Services

Core services provide supporting functionality for the UI layer.

### Protocol Bridge

The Protocol Bridge connects the UI layer to the Protocol Layer (MCP/A2A) for data and events.

```typescript
// Example: protocol-bridge.ts
import { MCPClient, MCPMessage, MCPContext } from '../../protocol/mcp';
import { A2AClient } from '../../protocol/a2a';

// Event types for UI updates
export type UIUpdateEvent = {
  type: string;
  payload: any;
  source?: string;
  timestamp: string;
};

// Callback type for event listeners
export type UIUpdateCallback = (event: UIUpdateEvent) => void;

export class ProtocolBridge {
  private static instance: ProtocolBridge;
  private mcpClient: MCPClient;
  private a2aClient: A2AClient;
  private eventListeners: Map<string, UIUpdateCallback[]> = new Map();
  
  private constructor() {
    // Initialize MCP client
    this.mcpClient = new MCPClient({
      componentId: 'ui-layer',
      componentType: 'service',
      layer: 'ui-ux',
      brokerUrl: process.env.MCP_BROKER_URL || 'mcp://mcp-broker:8080'
    });
    
    // Initialize A2A client
    this.a2aClient = new A2AClient({
      clientId: 'ui-layer',
      authConfig: {
        type: 'oauth2',
        clientId: process.env.A2A_CLIENT_ID,
        clientSecret: process.env.A2A_CLIENT_SECRET,
        tokenUrl: process.env.A2A_TOKEN_URL
      }
    });
    
    // Set up MCP event listeners
    this.setupMCPListeners();
  }
  
  public static getInstance(): ProtocolBridge {
    if (!ProtocolBridge.instance) {
      ProtocolBridge.instance = new ProtocolBridge();
    }
    return ProtocolBridge.instance;
  }
  
  // Set up MCP event listeners
  private setupMCPListeners(): void {
    // Listen for equipment status updates
    this.mcpClient.subscribe(
      'data-layer',
      'equipment.status_change',
      (message: MCPMessage) => {
        this.notifyListeners({
          type: 'equipment.status_change',
          payload: message.payload,
          source: message.source?.id,
          timestamp: message.context?.timestamp || new Date().toISOString()
        });
      }
    );
    
    // Listen for alerts
    this.mcpClient.subscribe(
      'core-ai-layer',
      'anomaly.detected',
      (message: MCPMessage) => {
        this.notifyListeners({
          type: 'anomaly.detected',
          payload: message.payload,
          source: message.source?.id,
          timestamp: message.context?.timestamp || new Date().toISOString()
        });
      }
    );
    
    // Listen for workflow status updates
    this.mcpClient.subscribe(
      'workflow-automation-layer',
      'workflow.status_change',
      (message: MCPMessage) => {
        this.notifyListeners({
          type: 'workflow.status_change',
          payload: message.payload,
          source: message.source?.id,
          timestamp: message.context?.timestamp || new Date().toISOString()
        });
      }
    );
  }
  
  // Add event listener
  public addEventListener(eventType: string, callback: UIUpdateCallback): void {
    if (!this.eventListeners.has(eventType)) {
      this.eventListeners.set(eventType, []);
    }
    this.eventListeners.get(eventType)?.push(callback);
  }
  
  // Remove event listener
  public removeEventListener(eventType: string, callback: UIUpdateCallback): void {
    if (!this.eventListeners.has(eventType)) return;
    
    const listeners = this.eventListeners.get(eventType);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index !== -1) {
        listeners.splice(index, 1);
      }
    }
  }
  
  // Notify all listeners of an event
  private notifyListeners(event: UIUpdateEvent): void {
    const listeners = this.eventListeners.get(event.type) || [];
    listeners.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error(`Error in event listener for ${event.type}:`, error);
      }
    });
    
    // Also notify 'all' listeners
    const allListeners = this.eventListeners.get('all') || [];
    allListeners.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error(`Error in 'all' event listener for ${event.type}:`, error);
      }
    });
  }
  
  // Send MCP request
  public async sendMCPRequest(
    targetLayer: string,
    capability: string,
    payload: any,
    context?: Partial<MCPContext>
  ): Promise<any> {
    try {
      const response = await this.mcpClient.request(
        `${targetLayer}-service`,
        targetLayer,
        capability,
        payload,
        context
      );
      
      if (response.isSuccess()) {
        return response.getPayload();
      } else {
        const error = response.getError();
        throw new Error(`MCP request failed: ${error.code} - ${error.message}`);
      }
    } catch (error) {
      console.error(`Error sending MCP request to ${targetLayer}:`, error);
      throw error;
    }
  }
  
  // Discover A2A agents
  public async discoverAgents(capability?: string, industryTags?: string[]): Promise<any[]> {
    try {
      return await this.a2aClient.discoverAgents(capability, industryTags);
    } catch (error) {
      console.error('Error discovering A2A agents:', error);
      throw error;
    }
  }
  
  // Create A2A task
  public async createA2ATask(
    agentId: string,
    capability: string,
    inputs: any,
    priority: string = 'normal'
  ): Promise<any> {
    try {
      return await this.a2aClient.createTask(agentId, capability, inputs, priority);
    } catch (error) {
      console.error('Error creating A2A task:', error);
      throw error;
    }
  }
  
  // Get A2A task status
  public async getA2ATaskStatus(taskId: string): Promise<any> {
    try {
      return await this.a2aClient.getTaskStatus(taskId);
    } catch (error) {
      console.error('Error getting A2A task status:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const protocolBridge = ProtocolBridge.getInstance();
```

### State Management

The State Management Service manages UI state and data flow.

```typescript
// Example: state-management.ts
import { createContext, useContext, useReducer, ReactNode } from 'react';
import { protocolBridge, UIUpdateEvent } from './protocol-bridge';

// State types
export interface UIState {
  user: {
    id: string;
    name: string;
    role: string;
    avatar?: string;
  };
  agents: any[];
  equipment: any[];
  alerts: any[];
  metrics: any[];
  workflows: any[];
  loading: {
    [key: string]: boolean;
  };
  errors: {
    [key: string]: string | null;
  };
}

// Action types
type UIAction = 
  | { type: 'SET_USER', payload: Partial<UIState['user']> }
  | { type: 'SET_AGENTS', payload: any[] }
  | { type: 'UPDATE_AGENT', payload: { id: string, updates: any } }
  | { type: 'SET_EQUIPMENT', payload: any[] }
  | { type: 'UPDATE_EQUIPMENT', payload: { id: string, updates: any } }
  | { type: 'SET_ALERTS', payload: any[] }
  | { type: 'ADD_ALERT', payload: any }
  | { type: 'REMOVE_ALERT', payload: string }
  | { type: 'SET_METRICS', payload: any[] }
  | { type: 'SET_WORKFLOWS', payload: any[] }
  | { type: 'UPDATE_WORKFLOW', payload: { id: string, updates: any } }
  | { type: 'SET_LOADING', payload: { key: string, isLoading: boolean } }
  | { type: 'SET_ERROR', payload: { key: string, error: string | null } }
  | { type: 'HANDLE_MCP_EVENT', payload: UIUpdateEvent };

// Initial state
const initialState: UIState = {
  user: {
    id: '',
    name: '',
    role: '',
  },
  agents: [],
  equipment: [],
  alerts: [],
  metrics: [],
  workflows: [],
  loading: {},
  errors: {},
};

// Reducer function
function uiReducer(state: UIState, action: UIAction): UIState {
  switch (action.type) {
    case 'SET_USER':
      return {
        ...state,
        user: {
          ...state.user,
          ...action.payload,
        },
      };
    
    case 'SET_AGENTS':
      return {
        ...state,
        agents: action.payload,
      };
    
    case 'UPDATE_AGENT':
      return {
        ...state,
        agents: state.agents.map(agent => 
          agent.id === action.payload.id
            ? { ...agent, ...action.payload.updates }
            : agent
        ),
      };
    
    case 'SET_EQUIPMENT':
      return {
        ...state,
        equipment: action.payload,
      };
    
    case 'UPDATE_EQUIPMENT':
      return {
        ...state,
        equipment: state.equipment.map(item => 
          item.id === action.payload.id
            ? { ...item, ...action.payload.updates }
            : item
        ),
      };
    
    case 'SET_ALERTS':
      return {
        ...state,
        alerts: action.payload,
      };
    
    case 'ADD_ALERT':
      return {
        ...state,
        alerts: [action.payload, ...state.alerts],
      };
    
    case 'REMOVE_ALERT':
      return {
        ...state,
        alerts: state.alerts.filter(alert => alert.id !== action.payload),
      };
    
    case 'SET_METRICS':
      return {
        ...state,
        metrics: action.payload,
      };
    
    case 'SET_WORKFLOWS':
      return {
        ...state,
        workflows: action.payload,
      };
    
    case 'UPDATE_WORKFLOW':
      return {
        ...state,
        workflows: state.workflows.map(workflow => 
          workflow.id === action.payload.id
            ? { ...workflow, ...action.payload.updates }
            : workflow
        ),
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        loading: {
          ...state.loading,
          [action.payload.key]: action.payload.isLoading,
        },
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        errors: {
          ...state.errors,
          [action.payload.key]: action.payload.error,
        },
      };
    
    case 'HANDLE_MCP_EVENT':
      // Handle different event types
      switch (action.payload.type) {
        case 'equipment.status_change':
          return {
            ...state,
            equipment: state.equipment.map(item => 
              item.id === action.payload.payload.equipment_id
                ? { 
                    ...item, 
                    status: action.payload.payload.status,
                    lastUpdated: action.payload.timestamp,
                  }
                : item
            ),
          };
        
        case 'anomaly.detected':
          // Add a new alert for the anomaly
          const newAlert = {
            id: `alert-${Date.now()}`,
            type: 'anomaly',
            severity: action.payload.payload.severity || 'warning',
            message: `Anomaly detected: ${action.payload.payload.anomaly_type}`,
            equipmentId: action.payload.payload.equipment_id,
            timestamp: action.payload.timestamp,
            details: action.payload.payload.details || {},
          };
          return {
            ...state,
            alerts: [newAlert, ...state.alerts],
          };
        
        case 'workflow.status_change':
          return {
            ...state,
            workflows: state.workflows.map(workflow => 
              workflow.id === action.payload.payload.workflow_id
                ? { 
                    ...workflow, 
                    status: action.payload.payload.status,
                    lastUpdated: action.payload.timestamp,
                  }
                : workflow
            ),
          };
        
        default:
          return state;
      }
    
    default:
      return state;
  }
}

// Create context
const UIStateContext = createContext<{
  state: UIState;
  dispatch: React.Dispatch<UIAction>;
} | undefined>(undefined);

// Provider component
export function UIStateProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(uiReducer, initialState);
  
  // Set up event listeners
  useEffect(() => {
    // Handle MCP events
    const handleMCPEvent = (event: UIUpdateEvent) => {
      dispatch({ type: 'HANDLE_MCP_EVENT', payload: event });
    };
    
    // Subscribe to all events
    protocolBridge.addEventListener('all', handleMCPEvent);
    
    // Clean up on unmount
    return () => {
      protocolBridge.removeEventListener('all', handleMCPEvent);
    };
  }, []);
  
  return (
    <UIStateContext.Provider value={{ state, dispatch }}>
      {children}
    </UIStateContext.Provider>
  );
}

// Hook for using the state
export function useUIState() {
  const context = useContext(UIStateContext);
  if (context === undefined) {
    throw new Error('useUIState must be used within a UIStateProvider');
  }
  return context;
}

// Data fetching hooks
export function useEquipment() {
  const { state, dispatch } = useUIState();
  
  const fetchEquipment = useCallback(async () => {
    dispatch({ type: 'SET_LOADING', payload: { key: 'equipment', isLoading: true } });
    dispatch({ type: 'SET_ERROR', payload: { key: 'equipment', error: null } });
    
    try {
      const result = await protocolBridge.sendMCPRequest(
        'data',
        'data.query',
        { query: 'SELECT * FROM equipment' }
      );
      
      dispatch({ type: 'SET_EQUIPMENT', payload: result.data });
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: { 
          key: 'equipment', 
          error: error instanceof Error ? error.message : 'Failed to fetch equipment' 
        } 
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { key: 'equipment', isLoading: false } });
    }
  };
  
  return {
    equipment: state.equipment,
    loading: state.loading.equipment || false,
    error: state.errors.equipment,
    fetchEquipment,
  };
}

// Similar hooks for agents, alerts, metrics, workflows, etc.
```

## Platform Adapters

Platform Adapters enable deployment to different platforms.

### Web Adapter

```typescript
// Example: web-adapter.ts
import { createRoot } from 'react-dom/client';
import { App } from '../App';
import { UIStateProvider } from '../core/state-management';
import { ThemeProvider } from '../core/theme-engine';

export class WebAdapter {
  private rootElement: HTMLElement | null = null;
  
  constructor(rootElementId: string = 'root') {
    this.rootElement = document.getElementById(rootElementId);
    
    if (!this.rootElement) {
      console.error(`Root element with ID "${rootElementId}" not found.`);
      return;
    }
  }
  
  public initialize(): void {
    if (!this.rootElement) return;
    
    const root = createRoot(this.rootElement);
    
    root.render(
      <ThemeProvider>
        <UIStateProvider>
          <App />
        </UIStateProvider>
      </ThemeProvider>
    );
    
    console.log('Web adapter initialized');
  }
  
  public static detectViewportType(): 'mobile' | 'tablet' | 'desktop' {
    const width = window.innerWidth;
    
    if (width < 768) {
      return 'mobile';
    } else if (width < 1024) {
      return 'tablet';
    } else {
      return 'desktop';
    }
  }
  
  public static registerServiceWorker(): void {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
          .then(registration => {
            console.log('ServiceWorker registration successful with scope: ', registration.scope);
          })
          .catch(error => {
            console.error('ServiceWorker registration failed: ', error);
          });
      });
    }
  }
}

// Initialize the web adapter
const webAdapter = new WebAdapter();
webAdapter.initialize();
WebAdapter.registerServiceWorker();
```

## Integration with Other Layers

### Data Layer Integration

The UI/UX Layer integrates with the Data Layer to display and manipulate data.

```typescript
// Example: data-layer-integration.ts
import { protocolBridge } from '../core/protocol-bridge';

export class DataLayerIntegration {
  // Fetch equipment data
  public static async fetchEquipment(filters?: any): Promise<any[]> {
    try {
      const query = filters 
        ? `SELECT * FROM equipment WHERE ${this.buildFilterClause(filters)}`
        : 'SELECT * FROM equipment';
      
      const result = await protocolBridge.sendMCPRequest(
        'data',
        'data.query',
        { query }
      );
      
      return result.data || [];
    } catch (error) {
      console.error('Error fetching equipment data:', error);
      throw error;
    }
  }
  
  // Fetch telemetry data
  public static async fetchTelemetry(equipmentId: string, timeRange: { start: string, end: string }): Promise<any[]> {
    try {
      const query = `
        SELECT * FROM telemetry 
        WHERE equipment_id = '${equipmentId}' 
        AND timestamp BETWEEN '${timeRange.start}' AND '${timeRange.end}'
        ORDER BY timestamp ASC
      `;
      
      const result = await protocolBridge.sendMCPRequest(
        'data',
        'data.query',
        { query }
      );
      
      return result.data || [];
    } catch (error) {
      console.error('Error fetching telemetry data:', error);
      throw error;
    }
  }
  
  // Update equipment data
  public static async updateEquipment(equipmentId: string, updates: any): Promise<boolean> {
    try {
      await protocolBridge.sendMCPRequest(
        'data',
        'data.update',
        {
          table: 'equipment',
          id: equipmentId,
          updates
        }
      );
      
      return true;
    } catch (error) {
      console.error('Error updating equipment data:', error);
      throw error;
    }
  }
  
  // Helper method to build filter clause
  private static buildFilterClause(filters: any): string {
    return Object.entries(filters)
      .map(([key, value]) => {
        if (Array.isArray(value)) {
          return `${key} IN (${value.map(v => `'${v}'`).join(', ')})`;
        } else {
          return `${key} = '${value}'`;
        }
      })
      .join(' AND ');
  }
}
```

### Core AI Layer Integration

The UI/UX Layer integrates with the Core AI Layer to display AI model results and insights.

```typescript
// Example: core-ai-layer-integration.ts
import { protocolBridge } from '../core/protocol-bridge';

export class CoreAILayerIntegration {
  // Invoke a model for inference
  public static async invokeModel(modelId: string, inputData: any): Promise<any> {
    try {
      const result = await protocolBridge.sendMCPRequest(
        'core-ai',
        'model.inference',
        {
          model_id: modelId,
          input_data: inputData
        }
      );
      
      return result;
    } catch (error) {
      console.error(`Error invoking model ${modelId}:`, error);
      throw error;
    }
  }
  
  // Get anomaly detection for equipment
  public static async detectAnomalies(equipmentId: string, sensorData: any[]): Promise<any[]> {
    try {
      const result = await this.invokeModel(
        'anomaly-detection-v1',
        {
          equipment_id: equipmentId,
          sensor_readings: sensorData
        }
      );
      
      return result.anomalies || [];
    } catch (error) {
      console.error('Error detecting anomalies:', error);
      throw error;
    }
  }
  
  // Get remaining useful life prediction
  public static async predictRUL(equipmentId: string, sensorData: any[]): Promise<any> {
    try {
      const result = await this.invokeModel(
        'rul-prediction-v1',
        {
          equipment_id: equipmentId,
          sensor_readings: sensorData
        }
      );
      
      return {
        remainingDays: result.remaining_useful_life_days,
        confidence: result.confidence,
        nextMaintenanceDate: result.next_maintenance_date,
        componentsToCheck: result.components_to_check || []
      };
    } catch (error) {
      console.error('Error predicting RUL:', error);
      throw error;
    }
  }
  
  // Get model explanations (explainable AI)
  public static async getModelExplanation(modelId: string, predictionId: string): Promise<any> {
    try {
      const result = await protocolBridge.sendMCPRequest(
        'core-ai',
        'model.explain',
        {
          model_id: modelId,
          prediction_id: predictionId
        }
      );
      
      return result.explanation;
    } catch (error) {
      console.error('Error getting model explanation:', error);
      throw error;
    }
  }
}
```

## Deployment and Configuration

### Manifest Configuration

```yaml
apiVersion: industriverse.io/v1
kind: Layer
metadata:
  name: ui-ux-layer
  version: 1.0.0
spec:
  type: ui-ux
  enabled: true
  components:
    - name: design-system
      version: 1.0.0
      enabled: true
    - name: component-library
      version: 1.0.0
      enabled: true
    - name: dynamic-agent-capsules
      version: 1.0.0
      enabled: true
    - name: view-templates
      version: 1.0.0
      enabled: true
    - name: core-services
      version: 1.0.0
      enabled: true
      config:
        protocol_bridge:
          mcp_broker_url: "mcp://mcp-broker:8080"
          a2a_broker_url: "a2a://a2a-broker:8081"
        state_management:
          enabled: true
        theme_engine:
          enabled: true
          default_theme: "light"
        layout_engine:
          enabled: true
        notification_system:
          enabled: true
        auth_integration:
          enabled: true
        analytics_service:
          enabled: true
        accessibility_service:
          enabled: true
    - name: platform-adapters
      version: 1.0.0
      enabled: true
      config:
        web:
          enabled: true
        mobile:
          enabled: false
        desktop:
          enabled: false
        ar_vr:
          enabled: false
  
  integrations:
    - layer: data
      enabled: true
      config:
        data_access:
          enabled: true
          mode: read-write
    - layer: core-ai
      enabled: true
      config:
        model_access:
          enabled: true
          models: ["*"]
    - layer: protocol
      enabled: true
      config:
        protocols: ["mcp", "a2a"]
    - layer: workflow-automation
      enabled: true
      config:
        workflow_triggers:
          enabled: true
    - layer: security
      enabled: true
      config:
        authentication:
          enabled: true
        authorization:
          enabled: true
    - layer: overseer
      enabled: true
      config:
        monitoring:
          enabled: true
```

### Kubernetes Deployment

```yaml
# Example Deployment for UI/UX Layer (Simplified)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ui-ux-layer
  namespace: industriverse
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ui-ux-layer
  template:
    metadata:
      labels:
        app: ui-ux-layer
    spec:
      containers:
      - name: ui-ux-layer
        image: industriverse/ui-ux-layer:1.0.0
        ports:
        - containerPort: 80
          name: http
        env:
        - name: MCP_BROKER_URL
          value: "mcp://mcp-broker.industriverse:8080"
        - name: A2A_BROKER_URL
          value: "a2a://a2a-broker.industriverse:8081"
        - name: DEFAULT_THEME
          value: "light"
        - name: ENABLE_ANALYTICS
          value: "true"
        resources:
          requests:
            cpu: "200m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: ui-ux-layer
  namespace: industriverse
spec:
  selector:
    app: ui-ux-layer
  ports:
  - name: http
    port: 80
    targetPort: 80
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ui-ux-layer-ingress
  namespace: industriverse
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
  - host: ui.industriverse.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ui-ux-layer
            port:
              name: http
  tls:
  - hosts:
    - ui.industriverse.example.com
    secretName: ui-tls-secret
```

## Best Practices

1. **Design System First**: Start with a comprehensive design system before building components.
2. **Component-Based Architecture**: Build UI from reusable, composable components.
3. **Responsive Design**: Ensure all interfaces work across device sizes.
4. **Accessibility**: Follow WCAG guidelines for accessibility.
5. **Performance**: Optimize for performance, especially for industrial environments.
6. **Consistent Interaction Patterns**: Use consistent interaction patterns across the framework.
7. **Progressive Disclosure**: Show high-level information first, with drill-down capabilities.
8. **Role-Based Views**: Tailor interfaces to user roles.
9. **Real-Time Updates**: Use the Protocol Bridge to receive real-time updates.
10. **Error Handling**: Implement robust error handling and recovery.

## Troubleshooting

- **UI Not Updating**: Check Protocol Bridge connection, event listeners, and state management.
- **Component Styling Issues**: Verify design token usage and theme configuration.
- **Performance Problems**: Check for unnecessary re-renders, optimize component memoization.
- **Integration Issues**: Verify Protocol Layer connectivity and message formats.
- **Accessibility Issues**: Run accessibility audits and fix violations.

## Next Steps

- Explore the [Security & Compliance Layer Guide](09_security_compliance_layer_guide.md) for securing UI interactions.
- See the [Deployment Operations Layer Guide](10_deployment_operations_layer_guide.md) for deploying UI components.
- Consult the [Overseer System Guide](11_overseer_system_guide.md) for monitoring UI performance.

## Related Guides

- [Protocol Layer Guide](06_protocol_layer_guide.md)
- [Workflow Automation Layer Guide](07_workflow_automation_layer_guide.md)
- [Application Layer Guide](05_application_layer_guide.md)
