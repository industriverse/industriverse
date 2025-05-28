import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, IconButton, Avatar, Tooltip, Badge } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useEventBus } from '../../contexts/EventBusContext';
import { useData } from '../../contexts/DataContext';
import { useUIState } from '../../contexts/UIStateContext';

/**
 * Dynamic Agent Capsule component that provides a floating, adaptive UI node
 * representing a live agent instance or digital twin, inspired by iPhone's Dynamic Island.
 * 
 * This implements the Universal Skin concept and supports the Role-First, Context-Aware
 * design principle by providing contextual information about agents and twins.
 */
const DynamicAgentCapsule = ({ agent, onExpand, expanded = false }) => {
  const { subscribe } = useEventBus();
  const { getData } = useData();
  const { openModal } = useUIState();
  const [isActive, setIsActive] = useState(false);
  const [pulseAnimation, setPulseAnimation] = useState(false);
  const [capsuleState, setCapsuleState] = useState({
    status: agent.status || 'idle',
    activity: agent.activity || 'none',
    alerts: agent.alerts || 0,
  });

  // Subscribe to agent events
  useEffect(() => {
    const unsubscribe = subscribe(`agent:${agent.id}`, (event) => {
      // Update capsule state based on event
      setCapsuleState(prevState => ({
        ...prevState,
        status: event.payload.status || prevState.status,
        activity: event.payload.activity || prevState.activity,
        alerts: event.payload.alerts || prevState.alerts,
      }));
      
      // Trigger pulse animation
      setPulseAnimation(true);
      setTimeout(() => setPulseAnimation(false), 1500);
    });
    
    return () => unsubscribe();
  }, [agent.id, subscribe]);

  // Get status color
  const getStatusColor = (status) => {
    const statusColors = {
      active: '#4caf50',
      processing: '#2196f3',
      warning: '#ff9800',
      error: '#f44336',
      idle: '#9e9e9e',
    };
    
    return statusColors[status] || statusColors.idle;
  };

  // Handle click event
  const handleClick = () => {
    if (expanded) {
      // If already expanded, open detailed modal
      openModal('agentDetail', { agentId: agent.id });
    } else {
      // If collapsed, expand the capsule
      onExpand(agent.id);
    }
  };

  // Styled components
  const CapsuleContainer = styled(Paper)(({ theme, expanded, status, pulse }) => ({
    display: 'flex',
    alignItems: 'center',
    padding: expanded ? theme.spacing(1.5, 2) : theme.spacing(1, 1.5),
    borderRadius: 24,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    color: '#fff',
    boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.15)',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
    width: expanded ? 280 : 'auto',
    position: 'relative',
    overflow: 'hidden',
    '&:hover': {
      backgroundColor: 'rgba(0, 0, 0, 0.85)',
      transform: 'translateY(-2px)',
    },
    '&:after': pulse ? {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      borderRadius: 24,
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
        transform: 'scale(1.2)',
      },
    },
  }));

  const StatusIndicator = styled('div')(({ theme, status }) => ({
    width: 10,
    height: 10,
    borderRadius: '50%',
    backgroundColor: getStatusColor(status),
    marginRight: theme.spacing(1),
    boxShadow: `0 0 8px ${getStatusColor(status)}`,
  }));

  return (
    <CapsuleContainer 
      expanded={expanded} 
      status={capsuleState.status}
      pulse={pulseAnimation}
      onClick={handleClick}
      elevation={3}
    >
      <StatusIndicator status={capsuleState.status} />
      
      <Badge 
        badgeContent={capsuleState.alerts} 
        color="error"
        overlap="circular"
        invisible={capsuleState.alerts === 0}
      >
        <Avatar 
          sx={{ 
            width: 32, 
            height: 32, 
            bgcolor: agent.avatarColor || 'primary.main',
            mr: expanded ? 1.5 : 0,
          }}
        >
          {agent.name.charAt(0)}
        </Avatar>
      </Badge>
      
      {expanded && (
        <Box sx={{ ml: 1, flexGrow: 1, overflow: 'hidden' }}>
          <Typography variant="subtitle2" noWrap>
            {agent.name}
          </Typography>
          <Typography variant="caption" color="rgba(255, 255, 255, 0.7)" noWrap>
            {capsuleState.activity !== 'none' 
              ? `${capsuleState.activity}`
              : `Status: ${capsuleState.status}`
            }
          </Typography>
        </Box>
      )}
    </CapsuleContainer>
  );
};

export default DynamicAgentCapsule;
