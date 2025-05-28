"""
Security & Compliance Avatar Interface for the Security & Compliance Layer

This component provides the avatar interface for the Security & Compliance Layer,
enabling intuitive interaction with security and compliance capabilities through
an embodied AI avatar representation.

Key capabilities:
1. Avatar visualization and animation
2. Contextual security status representation
3. Natural language security interaction
4. Security alert visualization
5. Compliance status representation

The Security & Compliance Avatar Interface enables intuitive interaction with
security and compliance capabilities through an embodied AI representation.
"""

import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';

// Styled components for the avatar interface
const AvatarContainer = styled(motion.div)`
  position: relative;
  width: ${props => props.expanded ? '320px' : '64px'};
  height: ${props => props.expanded ? '240px' : '64px'};
  border-radius: ${props => props.expanded ? '16px' : '32px'};
  background: linear-gradient(135deg, 
    ${props => props.securityStatus === 'critical' ? 'rgba(220, 53, 69, 0.95)' : 
    props.securityStatus === 'warning' ? 'rgba(255, 193, 7, 0.95)' : 
    props.securityStatus === 'secure' ? 'rgba(40, 167, 69, 0.95)' : 'rgba(23, 162, 184, 0.95)'}, 
    ${props => props.securityStatus === 'critical' ? 'rgba(220, 53, 69, 0.8)' : 
    props.securityStatus === 'warning' ? 'rgba(255, 193, 7, 0.8)' : 
    props.securityStatus === 'secure' ? 'rgba(40, 167, 69, 0.8)' : 'rgba(23, 162, 184, 0.8)'});
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: ${props => props.expanded ? 'flex-start' : 'center'};
  padding: ${props => props.expanded ? '16px' : '8px'};
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  z-index: 1000;
  
  &:hover {
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.2);
  }
`;

const AvatarFace = styled(motion.div)`
  width: ${props => props.expanded ? '80px' : '48px'};
  height: ${props => props.expanded ? '80px' : '48px'};
  border-radius: 50%;
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: ${props => props.expanded ? '16px' : '0'};
  position: relative;
  overflow: hidden;
`;

const AvatarExpression = styled.div`
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;

const AvatarEyes = styled(motion.div)`
  display: flex;
  width: 60%;
  justify-content: space-between;
  margin-bottom: 8px;
`;

const AvatarEye = styled(motion.div)`
  width: ${props => props.expanded ? '12px' : '8px'};
  height: ${props => props.expanded ? '12px' : '8px'};
  border-radius: 50%;
  background-color: #333;
`;

const AvatarMouth = styled(motion.div)`
  width: 40%;
  height: ${props => props.expression === 'happy' ? '10px' : 
    props.expression === 'sad' ? '10px' : 
    props.expression === 'neutral' ? '4px' : 
    props.expression === 'surprised' ? '12px' : '6px'};
  border-radius: ${props => props.expression === 'happy' ? '0 0 10px 10px' : 
    props.expression === 'sad' ? '10px 10px 0 0' : 
    props.expression === 'surprised' ? '50%' : '4px'};
  background-color: #333;
`;

const SecurityStatusBadge = styled(motion.div)`
  position: absolute;
  top: ${props => props.expanded ? '16px' : '0'};
  right: ${props => props.expanded ? '16px' : '0'};
  width: ${props => props.expanded ? '24px' : '16px'};
  height: ${props => props.expanded ? '24px' : '16px'};
  border-radius: 50%;
  background-color: ${props => 
    props.status === 'critical' ? '#dc3545' : 
    props.status === 'warning' ? '#ffc107' : 
    props.status === 'secure' ? '#28a745' : '#17a2b8'};
  border: 2px solid #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: ${props => props.expanded ? '14px' : '10px'};
  color: #fff;
  font-weight: bold;
`;

const ContentContainer = styled(motion.div)`
  width: 100%;
  display: ${props => props.expanded ? 'flex' : 'none'};
  flex-direction: column;
  align-items: center;
  overflow: hidden;
`;

const StatusText = styled.h3`
  margin: 0 0 12px 0;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
`;

const ActionButtons = styled.div`
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
`;

const ActionButton = styled.button`
  background-color: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 4px;
  color: #fff;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.3);
  }
  
  &:active {
    background-color: rgba(255, 255, 255, 0.4);
  }
`;

const AlertBadge = styled(motion.div)`
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: #dc3545;
  border: 2px solid #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: #fff;
  font-weight: bold;
`;

/**
 * Security & Compliance Avatar Interface Component
 * 
 * This component provides an interactive avatar interface for the Security & Compliance Layer,
 * displaying security status, alerts, and providing access to security and compliance actions.
 */
const SecurityComplianceAvatar = ({
  securityStatus = 'normal',
  complianceStatus = 'compliant',
  alertCount = 0,
  onAvatarClick,
  onActionClick,
  position = 'bottom-right',
  initialExpanded = false,
  avatarName = 'SecGuard',
  animationEnabled = true
}) => {
  const [expanded, setExpanded] = useState(initialExpanded);
  const [expression, setExpression] = useState('neutral');
  const [blinking, setBlinking] = useState(false);
  const blinkTimerRef = useRef(null);
  
  // Set avatar expression based on security status
  useEffect(() => {
    switch (securityStatus) {
      case 'critical':
        setExpression('sad');
        break;
      case 'warning':
        setExpression('concerned');
        break;
      case 'secure':
        setExpression('happy');
        break;
      default:
        setExpression('neutral');
    }
  }, [securityStatus]);
  
  // Handle random blinking for the avatar
  useEffect(() => {
    if (animationEnabled) {
      const startBlinkTimer = () => {
        const randomTime = Math.floor(Math.random() * 4000) + 2000; // 2-6 seconds
        blinkTimerRef.current = setTimeout(() => {
          setBlinking(true);
          setTimeout(() => {
            setBlinking(false);
            startBlinkTimer();
          }, 200);
        }, randomTime);
      };
      
      startBlinkTimer();
      
      return () => {
        if (blinkTimerRef.current) {
          clearTimeout(blinkTimerRef.current);
        }
      };
    }
  }, [animationEnabled]);
  
  // Handle avatar click
  const handleAvatarClick = () => {
    setExpanded(!expanded);
    if (onAvatarClick) {
      onAvatarClick(!expanded);
    }
  };
  
  // Handle action button click
  const handleActionClick = (action) => {
    if (onActionClick) {
      onActionClick(action);
    }
  };
  
  // Get status icon based on security status
  const getStatusIcon = (status) => {
    switch (status) {
      case 'critical':
        return '!';
      case 'warning':
        return '⚠';
      case 'secure':
        return '✓';
      default:
        return 'i';
    }
  };
  
  // Get status text based on security and compliance status
  const getStatusText = () => {
    if (securityStatus === 'critical') {
      return 'Critical Security Alert';
    } else if (securityStatus === 'warning') {
      return 'Security Warning';
    } else if (securityStatus === 'secure' && complianceStatus === 'compliant') {
      return 'Systems Secure & Compliant';
    } else if (securityStatus === 'secure' && complianceStatus !== 'compliant') {
      return 'Secure but Compliance Issues';
    } else if (complianceStatus !== 'compliant') {
      return 'Compliance Issues Detected';
    } else {
      return 'Security Status Normal';
    }
  };
  
  // Position the avatar based on the position prop
  const getPositionStyles = () => {
    switch (position) {
      case 'top-left':
        return { top: '20px', left: '20px' };
      case 'top-right':
        return { top: '20px', right: '20px' };
      case 'bottom-left':
        return { bottom: '20px', left: '20px' };
      case 'bottom-right':
      default:
        return { bottom: '20px', right: '20px' };
    }
  };
  
  return (
    <AvatarContainer
      expanded={expanded}
      securityStatus={securityStatus}
      onClick={handleAvatarClick}
      style={{ position: 'fixed', ...getPositionStyles() }}
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <AvatarFace expanded={expanded}>
        <AvatarExpression>
          <AvatarEyes>
            <AvatarEye 
              expanded={expanded}
              animate={{ scaleY: blinking ? 0.1 : 1 }}
              transition={{ duration: 0.1 }}
            />
            <AvatarEye 
              expanded={expanded}
              animate={{ scaleY: blinking ? 0.1 : 1 }}
              transition={{ duration: 0.1 }}
            />
          </AvatarEyes>
          <AvatarMouth expression={expression} />
        </AvatarExpression>
        
        {alertCount > 0 && !expanded && (
          <AlertBadge
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          >
            {alertCount > 9 ? '9+' : alertCount}
          </AlertBadge>
        )}
      </AvatarFace>
      
      <SecurityStatusBadge 
        status={securityStatus}
        expanded={expanded}
      >
        {getStatusIcon(securityStatus)}
      </SecurityStatusBadge>
      
      <AnimatePresence>
        {expanded && (
          <ContentContainer
            expanded={expanded}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <StatusText>{getStatusText()}</StatusText>
            
            {alertCount > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  marginBottom: '12px'
                }}
              >
                <span style={{ color: '#fff', fontSize: '14px' }}>
                  {alertCount} {alertCount === 1 ? 'alert' : 'alerts'} requiring attention
                </span>
              </motion.div>
            )}
            
            <ActionButtons>
              <ActionButton onClick={() => handleActionClick('viewAlerts')}>
                View Alerts
              </ActionButton>
              <ActionButton onClick={() => handleActionClick('runScan')}>
                Run Scan
              </ActionButton>
              <ActionButton onClick={() => handleActionClick('settings')}>
                Settings
              </ActionButton>
            </ActionButtons>
          </ContentContainer>
        )}
      </AnimatePresence>
    </AvatarContainer>
  );
};

SecurityComplianceAvatar.propTypes = {
  /** Current security status: 'critical', 'warning', 'secure', or 'normal' */
  securityStatus: PropTypes.oneOf(['critical', 'warning', 'secure', 'normal']),
  
  /** Current compliance status: 'compliant', 'partial', or 'non_compliant' */
  complianceStatus: PropTypes.oneOf(['compliant', 'partial', 'non_compliant']),
  
  /** Number of active alerts */
  alertCount: PropTypes.number,
  
  /** Callback when avatar is clicked */
  onAvatarClick: PropTypes.func,
  
  /** Callback when an action button is clicked */
  onActionClick: PropTypes.func,
  
  /** Position of the avatar on the screen */
  position: PropTypes.oneOf(['top-left', 'top-right', 'bottom-left', 'bottom-right']),
  
  /** Whether the avatar should be initially expanded */
  initialExpanded: PropTypes.bool,
  
  /** Name of the avatar */
  avatarName: PropTypes.string,
  
  /** Whether animations are enabled */
  animationEnabled: PropTypes.bool
};

export default SecurityComplianceAvatar;
