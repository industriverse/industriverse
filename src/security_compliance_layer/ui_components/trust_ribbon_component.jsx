"""
Trust Ribbon Component for the Security & Compliance Layer

This component provides a visual trust indicator that can be embedded in various
interfaces across the Industriverse platform, showing the trust level of capsules,
agents, data, and other entities.

Key capabilities:
1. Visual trust level representation
2. Trust source attribution
3. Trust verification details
4. Interactive trust inspection
5. Trust history visualization

The Trust Ribbon Component enables intuitive visualization of trust levels
for various entities in the Industriverse platform.
"""

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';

// Styled components for the trust ribbon
const RibbonContainer = styled(motion.div)`
  position: relative;
  display: flex;
  align-items: center;
  height: ${props => props.size === 'large' ? '36px' : props.size === 'medium' ? '28px' : '20px'};
  border-radius: ${props => props.size === 'large' ? '18px' : props.size === 'medium' ? '14px' : '10px'};
  background: linear-gradient(90deg, 
    ${props => getTrustGradient(props.trustLevel, props.trustSource)});
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0 ${props => props.size === 'large' ? '16px' : props.size === 'medium' ? '12px' : '8px'};
  cursor: pointer;
  overflow: hidden;
  transition: all 0.2s ease-in-out;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;

const TrustScore = styled.div`
  font-weight: bold;
  font-size: ${props => props.size === 'large' ? '16px' : props.size === 'medium' ? '14px' : '12px'};
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  margin-right: 8px;
`;

const TrustLabel = styled.div`
  font-size: ${props => props.size === 'large' ? '14px' : props.size === 'medium' ? '12px' : '10px'};
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
`;

const TrustIcon = styled.div`
  width: ${props => props.size === 'large' ? '20px' : props.size === 'medium' ? '16px' : '12px'};
  height: ${props => props.size === 'large' ? '20px' : props.size === 'medium' ? '16px' : '12px'};
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px;
  font-size: ${props => props.size === 'large' ? '12px' : props.size === 'medium' ? '10px' : '8px'};
  color: ${props => getTrustIconColor(props.trustSource)};
  font-weight: bold;
`;

const DetailPanel = styled(motion.div)`
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 280px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  padding: 16px;
  z-index: 1000;
`;

const DetailHeader = styled.div`
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 12px;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const DetailSection = styled.div`
  margin-bottom: 12px;
`;

const DetailLabel = styled.div`
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
`;

const DetailValue = styled.div`
  font-size: 14px;
  color: #333;
`;

const TrustFactors = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
`;

const TrustFactor = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const FactorLabel = styled.div`
  font-size: 12px;
  color: #333;
`;

const FactorValue = styled.div`
  font-size: 12px;
  font-weight: bold;
  color: ${props => 
    props.impact > 0 ? '#28a745' : 
    props.impact < 0 ? '#dc3545' : 
    '#6c757d'};
`;

const VerificationBadge = styled.div`
  display: inline-flex;
  align-items: center;
  background-color: ${props => 
    props.verified ? 'rgba(40, 167, 69, 0.1)' : 
    'rgba(108, 117, 125, 0.1)'};
  color: ${props => 
    props.verified ? '#28a745' : 
    '#6c757d'};
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 12px;
  margin-top: 8px;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  
  &:hover {
    color: #333;
  }
`;

// Helper functions
const getTrustGradient = (level, source) => {
  // Base colors for different trust levels
  const colors = {
    high: '#28a745',
    medium: '#ffc107',
    low: '#dc3545',
    unknown: '#6c757d'
  };
  
  // Adjust colors based on trust source
  const sourceAdjustment = {
    'zk-proof': { saturation: 1.1, lightness: 0.95 },
    'blockchain': { saturation: 1.05, lightness: 0.97 },
    'ai-verified': { saturation: 1, lightness: 1 },
    'human-verified': { saturation: 0.95, lightness: 1.02 },
    'system': { saturation: 0.9, lightness: 1.05 },
    'third-party': { saturation: 0.85, lightness: 1.1 }
  };
  
  const baseColor = colors[level] || colors.unknown;
  const adjustment = sourceAdjustment[source] || { saturation: 1, lightness: 1 };
  
  // For simplicity, we're just using the base color with opacity
  // In a real implementation, you would apply the saturation and lightness adjustments
  return `${baseColor}CC, ${baseColor}`;
};

const getTrustIconColor = (source) => {
  const sourceColors = {
    'zk-proof': '#6610f2',
    'blockchain': '#fd7e14',
    'ai-verified': '#17a2b8',
    'human-verified': '#28a745',
    'system': '#6c757d',
    'third-party': '#007bff'
  };
  
  return sourceColors[source] || '#6c757d';
};

const getTrustSourceIcon = (source) => {
  const sourceIcons = {
    'zk-proof': 'ZK',
    'blockchain': 'BC',
    'ai-verified': 'AI',
    'human-verified': 'HV',
    'system': 'SY',
    'third-party': '3P'
  };
  
  return sourceIcons[source] || '?';
};

const getTrustLevelLabel = (level) => {
  const labels = {
    high: 'High Trust',
    medium: 'Medium Trust',
    low: 'Low Trust',
    unknown: 'Unknown Trust'
  };
  
  return labels[level] || 'Unknown Trust';
};

/**
 * Trust Ribbon Component
 * 
 * This component provides a visual trust indicator that can be embedded in various
 * interfaces across the Industriverse platform.
 */
const TrustRibbon = ({
  entityId,
  entityType,
  trustLevel = 'unknown',
  trustScore = 0,
  trustSource = 'system',
  verificationDetails = null,
  trustFactors = [],
  size = 'medium',
  onClick,
  className,
  style
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [detailsPosition, setDetailsPosition] = useState('bottom');
  
  // Handle click on the trust ribbon
  const handleClick = (e) => {
    setShowDetails(!showDetails);
    
    if (onClick) {
      onClick(entityId, entityType, trustLevel);
    }
    
    // Determine the position of the detail panel
    const rect = e.currentTarget.getBoundingClientRect();
    const spaceBelow = window.innerHeight - rect.bottom;
    
    if (spaceBelow < 300) {
      setDetailsPosition('top');
    } else {
      setDetailsPosition('bottom');
    }
  };
  
  // Close the detail panel when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (showDetails && !e.target.closest('.trust-ribbon-container')) {
        setShowDetails(false);
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [showDetails]);
  
  return (
    <div className="trust-ribbon-container" style={{ position: 'relative', ...style }}>
      <RibbonContainer
        className={className}
        trustLevel={trustLevel}
        trustSource={trustSource}
        size={size}
        onClick={handleClick}
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2 }}
      >
        <TrustScore size={size}>{trustScore}</TrustScore>
        <TrustLabel size={size}>{getTrustLevelLabel(trustLevel)}</TrustLabel>
        <TrustIcon 
          size={size} 
          trustSource={trustSource}
        >
          {getTrustSourceIcon(trustSource)}
        </TrustIcon>
      </RibbonContainer>
      
      <AnimatePresence>
        {showDetails && (
          <DetailPanel
            initial={{ opacity: 0, y: detailsPosition === 'top' ? 10 : -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: detailsPosition === 'top' ? 10 : -10 }}
            transition={{ duration: 0.2 }}
            style={{ 
              top: detailsPosition === 'top' ? 'auto' : 'calc(100% + 8px)',
              bottom: detailsPosition === 'top' ? 'calc(100% + 8px)' : 'auto'
            }}
          >
            <DetailHeader>
              Trust Details
              <CloseButton onClick={() => setShowDetails(false)}>×</CloseButton>
            </DetailHeader>
            
            <DetailSection>
              <DetailLabel>Entity Type</DetailLabel>
              <DetailValue>{entityType}</DetailValue>
            </DetailSection>
            
            <DetailSection>
              <DetailLabel>Trust Score</DetailLabel>
              <DetailValue>{trustScore} / 100</DetailValue>
            </DetailSection>
            
            <DetailSection>
              <DetailLabel>Trust Source</DetailLabel>
              <DetailValue>
                {trustSource.charAt(0).toUpperCase() + trustSource.slice(1).replace(/-/g, ' ')}
              </DetailValue>
              
              {verificationDetails && (
                <VerificationBadge verified={verificationDetails.verified}>
                  {verificationDetails.verified ? '✓ Verified' : '⚠ Unverified'} 
                  {verificationDetails.timestamp && ` • ${new Date(verificationDetails.timestamp).toLocaleString()}`}
                </VerificationBadge>
              )}
            </DetailSection>
            
            {trustFactors.length > 0 && (
              <DetailSection>
                <DetailLabel>Trust Factors</DetailLabel>
                <TrustFactors>
                  {trustFactors.map((factor, index) => (
                    <TrustFactor key={index}>
                      <FactorLabel>{factor.name}</FactorLabel>
                      <FactorValue impact={factor.impact}>
                        {factor.impact > 0 ? '+' : ''}{factor.impact}
                      </FactorValue>
                    </TrustFactor>
                  ))}
                </TrustFactors>
              </DetailSection>
            )}
          </DetailPanel>
        )}
      </AnimatePresence>
    </div>
  );
};

TrustRibbon.propTypes = {
  /** Unique identifier for the entity */
  entityId: PropTypes.string.isRequired,
  
  /** Type of entity (e.g., 'capsule', 'agent', 'data') */
  entityType: PropTypes.string.isRequired,
  
  /** Trust level: 'high', 'medium', 'low', or 'unknown' */
  trustLevel: PropTypes.oneOf(['high', 'medium', 'low', 'unknown']),
  
  /** Numeric trust score (0-100) */
  trustScore: PropTypes.number,
  
  /** Source of trust verification */
  trustSource: PropTypes.oneOf([
    'zk-proof', 
    'blockchain', 
    'ai-verified', 
    'human-verified', 
    'system', 
    'third-party'
  ]),
  
  /** Verification details */
  verificationDetails: PropTypes.shape({
    verified: PropTypes.bool,
    verifier: PropTypes.string,
    timestamp: PropTypes.string,
    method: PropTypes.string
  }),
  
  /** Factors affecting trust score */
  trustFactors: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      impact: PropTypes.number.isRequired,
      description: PropTypes.string
    })
  ),
  
  /** Size of the trust ribbon */
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  
  /** Click handler */
  onClick: PropTypes.func,
  
  /** Additional CSS class */
  className: PropTypes.string,
  
  /** Additional inline styles */
  style: PropTypes.object
};

export default TrustRibbon;
