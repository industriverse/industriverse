"""
Dynamic Agent Capsules UI Component for the Deployment Operations Layer

This module implements the Universal Skin concept for the Deployment Operations Layer,
providing a dynamic, adaptive UI representation for agent capsules that offers
contextual information and micro-interactions.

The Dynamic Agent Capsules UI serves as a modern, intuitive interface for interacting
with deployment agents, missions, and operations across the Industriverse ecosystem.
"""

import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';

// Styled components for the Dynamic Agent Capsule
const CapsuleContainer = styled(motion.div)`
  position: relative;
  display: flex;
  align-items: center;
  background: ${props => props.theme.capsuleBackground || 'linear-gradient(135deg, #1E2A78 0%, #3E4491 100%)'};
  border-radius: 24px;
  padding: ${props => props.expanded ? '16px 24px' : '8px 16px'};
  color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  overflow: hidden;
  width: ${props => props.expanded ? '320px' : '180px'};
  height: ${props => props.expanded ? 'auto' : '48px'};
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.2);
  }
`;

const AvatarContainer = styled(motion.div)`
  width: ${props => props.expanded ? '48px' : '32px'};
  height: ${props => props.expanded ? '48px' : '32px'};
  border-radius: 50%;
  background: ${props => props.theme.avatarBackground || 'rgba(255, 255, 255, 0.2)'};
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
`;

const Avatar = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

const ContentContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const Title = styled.h3`
  margin: 0;
  font-size: ${props => props.expanded ? '16px' : '14px'};
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const Subtitle = styled.p`
  margin: 4px 0 0;
  font-size: 12px;
  opacity: 0.8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ExpandedContent = styled(motion.div)`
  margin-top: 12px;
  font-size: 14px;
`;

const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${props => {
    switch (props.status) {
      case 'active': return '#34A853';
      case 'warning': return '#FBBC05';
      case 'error': return '#EA4335';
      case 'inactive': return '#9AA0A6';
      default: return '#9AA0A6';
    }
  }};
  margin-left: 8px;
`;

const ActionButton = styled(motion.button)`
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 16px;
  color: white;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  margin-right: 8px;
  margin-top: 8px;
  transition: background 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.25);
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.5);
  }
`;

const ActionButtonsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  margin-top: 8px;
`;

const ProgressContainer = styled.div`
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  margin-top: 12px;
  overflow: hidden;
`;

const ProgressBar = styled(motion.div)`
  height: 100%;
  background: ${props => props.theme.progressColor || '#34A853'};
  border-radius: 2px;
`;

const MetricsContainer = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
`;

const MetricItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const MetricValue = styled.span`
  font-size: 16px;
  font-weight: 600;
`;

const MetricLabel = styled.span`
  font-size: 10px;
  opacity: 0.7;
  margin-top: 2px;
`;

/**
 * Dynamic Agent Capsule component that implements the Universal Skin concept
 * for representing agent instances and digital twins as floating, adaptive UI nodes.
 */
const DynamicAgentCapsule = ({
  id,
  title,
  subtitle,
  status,
  type,
  progress,
  metrics,
  actions,
  avatar,
  content,
  theme,
  onAction,
  onExpand,
  initialExpanded = false,
  pinned = false,
  className,
}) => {
  const [expanded, setExpanded] = useState(initialExpanded);
  const [animating, setAnimating] = useState(false);
  const containerRef = useRef(null);
  
  // Handle expansion toggle
  const toggleExpand = () => {
    if (!animating) {
      setAnimating(true);
      setExpanded(!expanded);
      if (onExpand) {
        onExpand(id, !expanded);
      }
    }
  };
  
  // Handle animation complete
  const handleAnimationComplete = () => {
    setAnimating(false);
  };
  
  // Handle action button click
  const handleActionClick = (e, action) => {
    e.stopPropagation();
    if (onAction) {
      onAction(id, action);
    }
  };
  
  // Animation variants
  const containerVariants = {
    collapsed: {
      height: '48px',
      width: '180px',
    },
    expanded: {
      height: 'auto',
      width: '320px',
    }
  };
  
  const contentVariants = {
    collapsed: {
      opacity: 0,
      height: 0,
    },
    expanded: {
      opacity: 1,
      height: 'auto',
    }
  };
  
  // Determine capsule background based on type
  const getCapsuleBackground = () => {
    switch (type) {
      case 'mission':
        return 'linear-gradient(135deg, #1E2A78 0%, #3E4491 100%)';
      case 'deployment':
        return 'linear-gradient(135deg, #0B5345 0%, #117A65 100%)';
      case 'agent':
        return 'linear-gradient(135deg, #6A1B9A 0%, #8E24AA 100%)';
      case 'layer':
        return 'linear-gradient(135deg, #B71C1C 0%, #D32F2F 100%)';
      case 'analytics':
        return 'linear-gradient(135deg, #1565C0 0%, #1976D2 100%)';
      default:
        return theme?.capsuleBackground || 'linear-gradient(135deg, #1E2A78 0%, #3E4491 100%)';
    }
  };
  
  // Custom theme with type-specific background
  const capsuleTheme = {
    ...theme,
    capsuleBackground: getCapsuleBackground(),
  };
  
  return (
    <CapsuleContainer
      ref={containerRef}
      expanded={expanded}
      onClick={toggleExpand}
      theme={capsuleTheme}
      className={className}
      initial={initialExpanded ? "expanded" : "collapsed"}
      animate={expanded ? "expanded" : "collapsed"}
      variants={containerVariants}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      onAnimationComplete={handleAnimationComplete}
      layout
    >
      <AvatarContainer expanded={expanded} theme={capsuleTheme}>
        {avatar ? (
          <Avatar src={avatar} alt={title} />
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="white" />
          </svg>
        )}
      </AvatarContainer>
      
      <ContentContainer>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Title expanded={expanded}>{title}</Title>
          <StatusIndicator status={status} />
        </div>
        <Subtitle>{subtitle}</Subtitle>
        
        <AnimatePresence>
          {expanded && (
            <ExpandedContent
              initial="collapsed"
              animate="expanded"
              exit="collapsed"
              variants={contentVariants}
              transition={{ duration: 0.2, ease: "easeInOut" }}
            >
              {content && <p>{content}</p>}
              
              {progress !== undefined && (
                <ProgressContainer>
                  <ProgressBar 
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5 }}
                    theme={capsuleTheme}
                  />
                </ProgressContainer>
              )}
              
              {metrics && (
                <MetricsContainer>
                  {Object.entries(metrics).map(([key, value]) => (
                    <MetricItem key={key}>
                      <MetricValue>{value}</MetricValue>
                      <MetricLabel>{key}</MetricLabel>
                    </MetricItem>
                  ))}
                </MetricsContainer>
              )}
              
              {actions && actions.length > 0 && (
                <ActionButtonsContainer>
                  {actions.map((action, index) => (
                    <ActionButton
                      key={index}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={(e) => handleActionClick(e, action)}
                    >
                      {action.label}
                    </ActionButton>
                  ))}
                </ActionButtonsContainer>
              )}
            </ExpandedContent>
          )}
        </AnimatePresence>
      </ContentContainer>
    </CapsuleContainer>
  );
};

DynamicAgentCapsule.propTypes = {
  id: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  status: PropTypes.oneOf(['active', 'warning', 'error', 'inactive']),
  type: PropTypes.oneOf(['mission', 'deployment', 'agent', 'layer', 'analytics']),
  progress: PropTypes.number,
  metrics: PropTypes.object,
  actions: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
  })),
  avatar: PropTypes.string,
  content: PropTypes.string,
  theme: PropTypes.object,
  onAction: PropTypes.func,
  onExpand: PropTypes.func,
  initialExpanded: PropTypes.bool,
  pinned: PropTypes.bool,
  className: PropTypes.string,
};

/**
 * Container component for managing multiple Dynamic Agent Capsules
 */
const DynamicAgentCapsulesContainer = ({
  capsules,
  onCapsuleAction,
  onCapsuleExpand,
  theme,
  className,
}) => {
  return (
    <div className={className}>
      {capsules.map((capsule) => (
        <DynamicAgentCapsule
          key={capsule.id}
          {...capsule}
          theme={theme}
          onAction={onCapsuleAction}
          onExpand={onCapsuleExpand}
        />
      ))}
    </div>
  );
};

DynamicAgentCapsulesContainer.propTypes = {
  capsules: PropTypes.arrayOf(PropTypes.object).isRequired,
  onCapsuleAction: PropTypes.func,
  onCapsuleExpand: PropTypes.func,
  theme: PropTypes.object,
  className: PropTypes.string,
};

export { DynamicAgentCapsule, DynamicAgentCapsulesContainer };
