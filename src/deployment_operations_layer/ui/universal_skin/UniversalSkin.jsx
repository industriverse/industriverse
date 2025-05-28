/**
 * Universal Skin Component
 * 
 * This component implements the "Universal Skin" or "Dynamic Agent Capsules" concept
 * for the Deployment Operations Layer, inspired by the iPhone's Dynamic Island.
 * 
 * It represents live agent instances and digital twins as floating, adaptive UI nodes
 * ("Islands" or "Capsules") that provide contextual information and micro-interactions.
 */

import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';

// Styled components for the Universal Skin
const CapsuleContainer = styled(motion.div)`
  position: relative;
  background: rgba(22, 28, 36, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  color: white;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  min-height: 44px;
  max-width: 100%;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  
  &.expanded {
    border-radius: 16px;
  }
  
  &.pinned {
    border: 1px solid rgba(0, 120, 255, 0.4);
  }
`;

const AvatarContainer = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  margin: 4px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #0062ff, #00b8ff);
  display: flex;
  align-items: center;
  justify-content: center;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`;

const ContentContainer = styled.div`
  flex: 1;
  padding: 8px 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
`;

const Title = styled.div`
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const Subtitle = styled.div`
  font-size: 12px;
  opacity: 0.7;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ActionContainer = styled.div`
  display: flex;
  gap: 8px;
  padding: 0 12px;
`;

const ActionButton = styled.button`
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
  
  svg {
    width: 16px;
    height: 16px;
  }
`;

const ExpandedContent = styled(motion.div)`
  padding: 0 16px 16px;
  overflow: hidden;
`;

const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  position: absolute;
  top: 4px;
  right: 4px;
  
  &.active {
    background-color: #4caf50;
  }
  
  &.warning {
    background-color: #ff9800;
  }
  
  &.error {
    background-color: #f44336;
  }
  
  &.idle {
    background-color: #9e9e9e;
  }
`;

// Icons for actions
const PinIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
    <path d="M16,12V4H17V2H7V4H8V12L6,14V16H11.2V22H12.8V16H18V14L16,12Z" />
  </svg>
);

const ForkIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
    <path d="M6,2A3,3 0 0,1 9,5C9,6.28 8.19,7.38 7.06,7.81C7.15,8.27 7.39,8.83 8,9.63C9,10.92 11,12.83 12,14.17C13,12.83 15,10.92 16,9.63C16.61,8.83 16.85,8.27 16.94,7.81C15.81,7.38 15,6.28 15,5A3,3 0 0,1 18,2A3,3 0 0,1 21,5C21,6.32 20.14,7.45 18.95,7.85C18.87,8.37 18.64,9 18,9.83C17,11.17 15,13.08 14,14.38C13.39,15.17 13.15,15.73 13.06,16.19C14.19,16.62 15,17.72 15,19A3,3 0 0,1 12,22A3,3 0 0,1 9,19C9,17.72 9.81,16.62 10.94,16.19C10.85,15.73 10.61,15.17 10,14.38C9,13.08 7,11.17 6,9.83C5.36,9 5.13,8.37 5.05,7.85C3.86,7.45 3,6.32 3,5A3,3 0 0,1 6,2M6,4A1,1 0 0,0 5,5A1,1 0 0,0 6,6A1,1 0 0,0 7,5A1,1 0 0,0 6,4M18,4A1,1 0 0,0 17,5A1,1 0 0,0 18,6A1,1 0 0,0 19,5A1,1 0 0,0 18,4M12,18A1,1 0 0,0 11,19A1,1 0 0,0 12,20A1,1 0 0,0 13,19A1,1 0 0,0 12,18Z" />
  </svg>
);

const SuspendIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
    <path d="M14,19H18V5H14M6,19H10V5H6V19Z" />
  </svg>
);

const RescapeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z" />
    <path d="M12,20V22A10,10 0 0,0 22,12H20A8,8 0 0,1 12,20Z" />
    <path d="M19,12A7,7 0 0,0 12,5V7A5,5 0 0,1 17,12H19Z" />
    <path d="M5,12A7,7 0 0,0 12,19V17A5,5 0 0,1 7,12H5Z" />
  </svg>
);

/**
 * Universal Skin / Dynamic Agent Capsule Component
 */
const UniversalSkin = ({
  agent,
  status,
  onPin,
  onFork,
  onSuspend,
  onRescope,
  isPinned,
  className,
  style
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [animation, setAnimation] = useState('idle');
  const containerRef = useRef(null);
  
  // Handle animation effects based on agent activity
  useEffect(() => {
    if (agent.activity && agent.activity !== 'idle') {
      setAnimation('pulse');
      const timer = setTimeout(() => {
        setAnimation('idle');
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [agent.activity]);
  
  // Animation variants
  const containerVariants = {
    idle: {
      scale: 1
    },
    pulse: {
      scale: [1, 1.03, 1],
      transition: {
        duration: 0.5
      }
    }
  };
  
  const expandedVariants = {
    hidden: {
      height: 0,
      opacity: 0
    },
    visible: {
      height: 'auto',
      opacity: 1,
      transition: {
        duration: 0.3
      }
    }
  };
  
  // Handle click to toggle expanded state
  const handleClick = () => {
    setIsExpanded(!isExpanded);
  };
  
  return (
    <CapsuleContainer
      ref={containerRef}
      className={`${className || ''} ${isExpanded ? 'expanded' : ''} ${isPinned ? 'pinned' : ''}`}
      style={style}
      onClick={handleClick}
      variants={containerVariants}
      animate={animation}
      initial="idle"
    >
      <AvatarContainer>
        {agent.avatarUrl ? (
          <img src={agent.avatarUrl} alt={agent.name} />
        ) : (
          <span>{agent.name.charAt(0)}</span>
        )}
      </AvatarContainer>
      
      <ContentContainer>
        <Title>{agent.name}</Title>
        <Subtitle>{agent.currentTask || agent.description}</Subtitle>
      </ContentContainer>
      
      <ActionContainer>
        <ActionButton onClick={(e) => { e.stopPropagation(); onPin(agent.id); }}>
          <PinIcon />
        </ActionButton>
        <ActionButton onClick={(e) => { e.stopPropagation(); onFork(agent.id); }}>
          <ForkIcon />
        </ActionButton>
        <ActionButton onClick={(e) => { e.stopPropagation(); onSuspend(agent.id); }}>
          <SuspendIcon />
        </ActionButton>
        <ActionButton onClick={(e) => { e.stopPropagation(); onRescope(agent.id); }}>
          <RescapeIcon />
        </ActionButton>
      </ActionContainer>
      
      <StatusIndicator className={status} />
      
      <AnimatePresence>
        {isExpanded && (
          <ExpandedContent
            variants={expandedVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
          >
            <div>
              <h4>Context</h4>
              <p>{agent.context || 'No context available'}</p>
            </div>
            
            <div>
              <h4>Status</h4>
              <p>{agent.statusMessage || 'No status available'}</p>
            </div>
            
            {agent.metrics && (
              <div>
                <h4>Metrics</h4>
                <ul>
                  {Object.entries(agent.metrics).map(([key, value]) => (
                    <li key={key}>{key}: {value}</li>
                  ))}
                </ul>
              </div>
            )}
          </ExpandedContent>
        )}
      </AnimatePresence>
    </CapsuleContainer>
  );
};

UniversalSkin.propTypes = {
  agent: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
    avatarUrl: PropTypes.string,
    currentTask: PropTypes.string,
    context: PropTypes.string,
    statusMessage: PropTypes.string,
    activity: PropTypes.string,
    metrics: PropTypes.object
  }).isRequired,
  status: PropTypes.oneOf(['active', 'warning', 'error', 'idle']),
  onPin: PropTypes.func.isRequired,
  onFork: PropTypes.func.isRequired,
  onSuspend: PropTypes.func.isRequired,
  onRescope: PropTypes.func.isRequired,
  isPinned: PropTypes.bool,
  className: PropTypes.string,
  style: PropTypes.object
};

UniversalSkin.defaultProps = {
  status: 'idle',
  isPinned: false
};

export default UniversalSkin;
