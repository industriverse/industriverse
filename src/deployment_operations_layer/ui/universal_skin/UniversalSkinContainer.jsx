/**
 * Universal Skin Container Component
 * 
 * This component manages multiple Dynamic Agent Capsules in the Universal Skin UI.
 * It provides the container and management logic for displaying, arranging, and
 * interacting with multiple agent capsules across different contexts.
 */

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import UniversalSkin from './UniversalSkin';

// Styled components for the container
const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  max-width: ${props => props.maxWidth || '360px'};
  position: ${props => props.position || 'fixed'};
  top: ${props => props.top || '20px'};
  right: ${props => props.right || '20px'};
  z-index: 1000;
  pointer-events: none;
  
  & > * {
    pointer-events: auto;
  }
`;

const DockContainer = styled.div`
  display: flex;
  flex-direction: row;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
  margin-bottom: 16px;
`;

const PinnedContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
`;

const CapsuleWrapper = styled(motion.div)`
  width: 100%;
`;

/**
 * Universal Skin Container Component
 */
const UniversalSkinContainer = ({
  agents,
  position,
  maxWidth,
  top,
  right,
  onAgentAction,
  className,
  style
}) => {
  const [pinnedAgents, setPinnedAgents] = useState([]);
  const [dockedAgents, setDockedAgents] = useState([]);
  const [activeAgents, setActiveAgents] = useState([]);
  
  // Process agents into appropriate categories
  useEffect(() => {
    if (!agents || !agents.length) return;
    
    const pinned = [];
    const docked = [];
    const active = [];
    
    agents.forEach(agent => {
      if (agent.isPinned) {
        pinned.push(agent);
      } else if (agent.isDocked) {
        docked.push(agent);
      } else if (agent.status !== 'idle') {
        active.push(agent);
      }
    });
    
    setPinnedAgents(pinned);
    setDockedAgents(docked);
    setActiveAgents(active);
  }, [agents]);
  
  // Handle agent actions
  const handlePin = (agentId) => {
    if (onAgentAction) {
      onAgentAction('pin', agentId);
    }
  };
  
  const handleFork = (agentId) => {
    if (onAgentAction) {
      onAgentAction('fork', agentId);
    }
  };
  
  const handleSuspend = (agentId) => {
    if (onAgentAction) {
      onAgentAction('suspend', agentId);
    }
  };
  
  const handleRescope = (agentId) => {
    if (onAgentAction) {
      onAgentAction('rescope', agentId);
    }
  };
  
  // Animation variants
  const itemVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: { opacity: 1, y: 0 },
    exit: { opacity: 0, x: 20 }
  };
  
  return (
    <Container 
      position={position}
      maxWidth={maxWidth}
      top={top}
      right={right}
      className={className}
      style={style}
    >
      {/* Pinned agents section */}
      {pinnedAgents.length > 0 && (
        <PinnedContainer>
          <AnimatePresence>
            {pinnedAgents.map(agent => (
              <CapsuleWrapper
                key={agent.id}
                variants={itemVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                layout
              >
                <UniversalSkin
                  agent={agent}
                  status={agent.status}
                  isPinned={true}
                  onPin={handlePin}
                  onFork={handleFork}
                  onSuspend={handleSuspend}
                  onRescope={handleRescope}
                />
              </CapsuleWrapper>
            ))}
          </AnimatePresence>
        </PinnedContainer>
      )}
      
      {/* Docked agents section */}
      {dockedAgents.length > 0 && (
        <DockContainer>
          <AnimatePresence>
            {dockedAgents.map(agent => (
              <CapsuleWrapper
                key={agent.id}
                variants={itemVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                layout
                style={{ width: 'auto', maxWidth: '180px' }}
              >
                <UniversalSkin
                  agent={agent}
                  status={agent.status}
                  isPinned={false}
                  onPin={handlePin}
                  onFork={handleFork}
                  onSuspend={handleSuspend}
                  onRescope={handleRescope}
                />
              </CapsuleWrapper>
            ))}
          </AnimatePresence>
        </DockContainer>
      )}
      
      {/* Active agents section */}
      <AnimatePresence>
        {activeAgents.map(agent => (
          <CapsuleWrapper
            key={agent.id}
            variants={itemVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            layout
          >
            <UniversalSkin
              agent={agent}
              status={agent.status}
              isPinned={false}
              onPin={handlePin}
              onFork={handleFork}
              onSuspend={handleSuspend}
              onRescope={handleRescope}
            />
          </CapsuleWrapper>
        ))}
      </AnimatePresence>
    </Container>
  );
};

UniversalSkinContainer.propTypes = {
  agents: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      description: PropTypes.string,
      avatarUrl: PropTypes.string,
      currentTask: PropTypes.string,
      context: PropTypes.string,
      statusMessage: PropTypes.string,
      status: PropTypes.oneOf(['active', 'warning', 'error', 'idle']),
      isPinned: PropTypes.bool,
      isDocked: PropTypes.bool,
      metrics: PropTypes.object
    })
  ).isRequired,
  position: PropTypes.string,
  maxWidth: PropTypes.string,
  top: PropTypes.string,
  right: PropTypes.string,
  onAgentAction: PropTypes.func,
  className: PropTypes.string,
  style: PropTypes.object
};

UniversalSkinContainer.defaultProps = {
  position: 'fixed',
  maxWidth: '360px',
  top: '20px',
  right: '20px'
};

export default UniversalSkinContainer;
