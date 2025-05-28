/**
 * Universal Skin Context Provider
 * 
 * This component provides a React context for managing the Universal Skin state
 * across the application. It handles agent state management, communication with
 * backend services, and provides hooks for components to interact with the
 * Universal Skin system.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

// Create context
const UniversalSkinContext = createContext(null);

/**
 * Universal Skin Provider Component
 */
export const UniversalSkinProvider = ({ children, apiEndpoint }) => {
  const [agents, setAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Fetch agents from API
  const fetchAgents = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiEndpoint}/agents`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      setAgents(data.agents || []);
    } catch (err) {
      console.error('Error fetching agents:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [apiEndpoint]);
  
  // Initialize on mount
  useEffect(() => {
    fetchAgents();
    
    // Set up polling for updates
    const intervalId = setInterval(fetchAgents, 10000); // Poll every 10 seconds
    
    return () => clearInterval(intervalId);
  }, [fetchAgents]);
  
  // Handle agent actions
  const handleAgentAction = useCallback(async (action, agentId) => {
    try {
      const response = await fetch(`${apiEndpoint}/agents/${agentId}/actions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action }),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      // Update local state based on action
      setAgents(prevAgents => {
        return prevAgents.map(agent => {
          if (agent.id === agentId) {
            switch (action) {
              case 'pin':
                return { ...agent, isPinned: !agent.isPinned };
              case 'suspend':
                return { ...agent, status: 'idle', statusMessage: 'Suspended' };
              case 'fork':
                // Fork is handled by the API, which will create a new agent
                return agent;
              case 'rescope':
                return { ...agent, statusMessage: 'Rescoping...' };
              default:
                return agent;
            }
          }
          return agent;
        });
      });
      
      // Refresh agents after action
      fetchAgents();
      
      return true;
    } catch (err) {
      console.error(`Error performing ${action} on agent ${agentId}:`, err);
      setError(err.message);
      return false;
    }
  }, [apiEndpoint, fetchAgents]);
  
  // Add a new agent
  const addAgent = useCallback(async (agentData) => {
    try {
      const response = await fetch(`${apiEndpoint}/agents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(agentData),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      // Refresh agents
      fetchAgents();
      
      return true;
    } catch (err) {
      console.error('Error adding agent:', err);
      setError(err.message);
      return false;
    }
  }, [apiEndpoint, fetchAgents]);
  
  // Remove an agent
  const removeAgent = useCallback(async (agentId) => {
    try {
      const response = await fetch(`${apiEndpoint}/agents/${agentId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      // Update local state
      setAgents(prevAgents => prevAgents.filter(agent => agent.id !== agentId));
      
      return true;
    } catch (err) {
      console.error(`Error removing agent ${agentId}:`, err);
      setError(err.message);
      return false;
    }
  }, [apiEndpoint]);
  
  // Context value
  const contextValue = {
    agents,
    isLoading,
    error,
    fetchAgents,
    handleAgentAction,
    addAgent,
    removeAgent,
  };
  
  return (
    <UniversalSkinContext.Provider value={contextValue}>
      {children}
    </UniversalSkinContext.Provider>
  );
};

UniversalSkinProvider.propTypes = {
  children: PropTypes.node.isRequired,
  apiEndpoint: PropTypes.string.isRequired,
};

/**
 * Hook for using the Universal Skin context
 */
export const useUniversalSkin = () => {
  const context = useContext(UniversalSkinContext);
  if (!context) {
    throw new Error('useUniversalSkin must be used within a UniversalSkinProvider');
  }
  return context;
};

export default UniversalSkinContext;
