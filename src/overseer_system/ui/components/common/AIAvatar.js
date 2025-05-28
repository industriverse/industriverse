import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Avatar, Tooltip, IconButton } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useEventBus } from '../../contexts/EventBusContext';
import { useData } from '../../contexts/DataContext';

/**
 * AI Avatar component that provides a visual representation of an IFF layer
 * with interactive capabilities and status information.
 * 
 * This implements the Universal Skin concept and supports the Role-First, Context-Aware
 * design principle by providing contextual information about IFF layers.
 */
const AIAvatar = ({ layer, size = 'medium', interactive = true }) => {
  const { subscribe } = useEventBus();
  const { getData } = useData();
  const [avatarState, setAvatarState] = useState({
    status: layer.status || 'normal',
    activity: layer.activity || 'idle',
    expression: layer.expression || 'neutral',
  });
  const [pulseAnimation, setPulseAnimation] = useState(false);

  // Layer configuration
  const layerConfig = {
    'data': {
      name: 'Data Layer',
      color: '#2196f3',
      icon: '📊',
      description: 'Manages data ingestion, processing, and storage'
    },
    'core-ai': {
      name: 'Core AI Layer',
      color: '#9c27b0',
      icon: '🧠',
      description: 'Provides foundational AI capabilities'
    },
    'protocol': {
      name: 'Protocol Layer',
      color: '#4caf50',
      icon: '🔄',
      description: 'Handles communication protocols and standards'
    },
    'security': {
      name: 'Security & Compliance Layer',
      color: '#f44336',
      icon: '🔒',
      description: 'Ensures security and regulatory compliance'
    },
    'generative': {
      name: 'Generative Layer',
      color: '#ff9800',
      icon: '✨',
      description: 'Creates and manages generative content'
    },
    'application': {
      name: 'Application Layer',
      color: '#795548',
      icon: '📱',
      description: 'Hosts applications and services'
    },
    'workflow': {
      name: 'Workflow Automation Layer',
      color: '#607d8b',
      icon: '⚙️',
      description: 'Automates and orchestrates workflows'
    },
    'ui-ux': {
      name: 'UI/UX Layer',
      color: '#e91e63',
      icon: '🖌️',
      description: 'Provides user interfaces and experiences'
    }
  };

  const config = layerConfig[layer.id] || {
    name: layer.name || 'Unknown Layer',
    color: '#9e9e9e',
    icon: '❓',
    description: 'Layer information unavailable'
  };

  // Subscribe to layer events
  useEffect(() => {
    const unsubscribe = subscribe(`layer:${layer.id}`, (event) => {
      // Update avatar state based on event
      setAvatarState(prevState => ({
        ...prevState,
        status: event.payload.status || prevState.status,
        activity: event.payload.activity || prevState.activity,
        expression: event.payload.expression || prevState.expression,
      }));
      
      // Trigger pulse animation
      setPulseAnimation(true);
      setTimeout(() => setPulseAnimation(false), 1500);
    });
    
    return () => unsubscribe();
  }, [layer.id, subscribe]);

  // Get status color
  const getStatusColor = (status) => {
    const statusColors = {
      normal: config.color,
      active: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      inactive: '#9e9e9e',
    };
    
    return statusColors[status] || statusColors.normal;
  };

  // Get avatar size
  const getAvatarSize = (size) => {
    const sizes = {
      small: 40,
      medium: 64,
      large: 96,
    };
    
    return sizes[size] || sizes.medium;
  };

  // Get expression
  const getExpression = (expression) => {
    const expressions = {
      neutral: config.icon,
      happy: '😊',
      sad: '😔',
      surprised: '😲',
      confused: '😕',
      busy: '🔄',
      alert: '⚠️',
    };
    
    return expressions[expression] || expressions.neutral;
  };

  // Styled components
  const AvatarContainer = styled(Box)(({ theme, status, pulse }) => ({
    position: 'relative',
    display: 'inline-flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    '&:after': pulse ? {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      borderRadius: '50%',
      border: `2px solid ${getStatusColor(status)}`,
      animation: 'pulse 1.5s ease-out',
    } : {},
    '@keyframes pulse': {
      '0%': {
        opacity: 1,
        transform: 'scale(1)',
      },
      '100%': {
        opacity: 0,
        transform: 'scale(1.5)',
      },
    },
  }));

  const StyledAvatar = styled(Avatar)(({ theme, status, size }) => ({
    width: getAvatarSize(size),
    height: getAvatarSize(size),
    backgroundColor: getStatusColor(status),
    color: '#fff',
    fontSize: size === 'large' ? 36 : size === 'small' ? 18 : 24,
    boxShadow: `0 0 12px ${getStatusColor(status)}`,
    transition: 'all 0.3s ease',
    cursor: interactive ? 'pointer' : 'default',
    '&:hover': interactive ? {
      transform: 'scale(1.05)',
    } : {},
  }));

  const StatusIndicator = styled('div')(({ theme, status }) => ({
    width: size === 'small' ? 8 : 12,
    height: size === 'small' ? 8 : 12,
    borderRadius: '50%',
    backgroundColor: getStatusColor(status),
    position: 'absolute',
    bottom: 0,
    right: 0,
    border: `2px solid ${theme.palette.background.paper}`,
    boxShadow: `0 0 8px ${getStatusColor(status)}`,
  }));

  return (
    <Tooltip title={`${config.name}: ${config.description}`} arrow>
      <AvatarContainer status={avatarState.status} pulse={pulseAnimation}>
        <StyledAvatar 
          status={avatarState.status} 
          size={size}
        >
          {getExpression(avatarState.expression)}
        </StyledAvatar>
        <StatusIndicator status={avatarState.status} />
        {size !== 'small' && (
          <Typography 
            variant={size === 'large' ? 'subtitle1' : 'caption'} 
            sx={{ mt: 1, fontWeight: 'medium' }}
          >
            {config.name}
          </Typography>
        )}
      </AvatarContainer>
    </Tooltip>
  );
};

export default AIAvatar;
