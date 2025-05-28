/**
 * Universal Skin API Service
 * 
 * This module provides the backend API service for the Universal Skin UI.
 * It handles agent state management, persistence, and communication with
 * the agent system in the Deployment Operations Layer.
 */

import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { UniversalSkinProvider } from './UniversalSkinContext';
import UniversalSkinContainer from './UniversalSkinContainer';

// Styled components for the app
const AppContainer = styled.div`
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
`;

/**
 * Universal Skin App Component
 * 
 * This is the main entry point for integrating the Universal Skin UI
 * into the Deployment Operations Layer dashboard.
 */
const UniversalSkinApp = ({
  apiEndpoint,
  position,
  maxWidth,
  top,
  right,
  className,
  style
}) => {
  // Handle agent actions
  const handleAgentAction = (action, agentId) => {
    console.log(`Action ${action} on agent ${agentId}`);
    // The actual implementation is handled by the UniversalSkinContext
  };
  
  return (
    <UniversalSkinProvider apiEndpoint={apiEndpoint}>
      {({ agents, isLoading, error, handleAgentAction }) => (
        <AppContainer className={className} style={style}>
          {error && <div className="error-message">{error}</div>}
          
          <UniversalSkinContainer
            agents={agents}
            position={position}
            maxWidth={maxWidth}
            top={top}
            right={right}
            onAgentAction={handleAgentAction}
          />
        </AppContainer>
      )}
    </UniversalSkinProvider>
  );
};

UniversalSkinApp.propTypes = {
  apiEndpoint: PropTypes.string.isRequired,
  position: PropTypes.string,
  maxWidth: PropTypes.string,
  top: PropTypes.string,
  right: PropTypes.string,
  className: PropTypes.string,
  style: PropTypes.object
};

UniversalSkinApp.defaultProps = {
  apiEndpoint: '/api/universal-skin',
  position: 'fixed',
  maxWidth: '360px',
  top: '20px',
  right: '20px'
};

export default UniversalSkinApp;
