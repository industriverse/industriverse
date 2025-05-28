/**
 * Universal Skin API Service
 * 
 * This module provides the backend API service for the Universal Skin UI.
 * It handles agent state management, persistence, and communication with
 * the agent system in the Deployment Operations Layer.
 */

import axios from 'axios';

class UniversalSkinAPI {
  /**
   * Initialize the Universal Skin API service
   * 
   * @param {string} baseURL - Base URL for the API
   * @param {Object} options - Additional options
   */
  constructor(baseURL, options = {}) {
    this.client = axios.create({
      baseURL,
      timeout: options.timeout || 10000,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    });
    
    this.onError = options.onError || console.error;
  }
  
  /**
   * Get all agents
   * 
   * @returns {Promise<Array>} List of agents
   */
  async getAgents() {
    try {
      const response = await this.client.get('/agents');
      return response.data.agents || [];
    } catch (error) {
      this.onError('Error fetching agents:', error);
      throw error;
    }
  }
  
  /**
   * Get a specific agent by ID
   * 
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Agent data
   */
  async getAgent(agentId) {
    try {
      const response = await this.client.get(`/agents/${agentId}`);
      return response.data.agent;
    } catch (error) {
      this.onError(`Error fetching agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Create a new agent
   * 
   * @param {Object} agentData - Agent data
   * @returns {Promise<Object>} Created agent
   */
  async createAgent(agentData) {
    try {
      const response = await this.client.post('/agents', agentData);
      return response.data.agent;
    } catch (error) {
      this.onError('Error creating agent:', error);
      throw error;
    }
  }
  
  /**
   * Update an existing agent
   * 
   * @param {string} agentId - Agent ID
   * @param {Object} agentData - Updated agent data
   * @returns {Promise<Object>} Updated agent
   */
  async updateAgent(agentId, agentData) {
    try {
      const response = await this.client.put(`/agents/${agentId}`, agentData);
      return response.data.agent;
    } catch (error) {
      this.onError(`Error updating agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Delete an agent
   * 
   * @param {string} agentId - Agent ID
   * @returns {Promise<boolean>} Success status
   */
  async deleteAgent(agentId) {
    try {
      await this.client.delete(`/agents/${agentId}`);
      return true;
    } catch (error) {
      this.onError(`Error deleting agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Perform an action on an agent
   * 
   * @param {string} agentId - Agent ID
   * @param {string} action - Action to perform
   * @param {Object} params - Action parameters
   * @returns {Promise<Object>} Action result
   */
  async performAgentAction(agentId, action, params = {}) {
    try {
      const response = await this.client.post(`/agents/${agentId}/actions`, {
        action,
        params
      });
      return response.data;
    } catch (error) {
      this.onError(`Error performing action ${action} on agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Get agent metrics
   * 
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Agent metrics
   */
  async getAgentMetrics(agentId) {
    try {
      const response = await this.client.get(`/agents/${agentId}/metrics`);
      return response.data.metrics;
    } catch (error) {
      this.onError(`Error fetching metrics for agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Get agent status
   * 
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Agent status
   */
  async getAgentStatus(agentId) {
    try {
      const response = await this.client.get(`/agents/${agentId}/status`);
      return response.data.status;
    } catch (error) {
      this.onError(`Error fetching status for agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Pin an agent
   * 
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Updated agent
   */
  async pinAgent(agentId) {
    return this.performAgentAction(agentId, 'pin');
  }
  
  /**
   * Fork an agent
   * 
   * @param {string} agentId - Agent ID
   * @param {Object} params - Fork parameters
   * @returns {Promise<Object>} Forked agent
   */
  async forkAgent(agentId, params = {}) {
    return this.performAgentAction(agentId, 'fork', params);
  }
  
  /**
   * Suspend an agent
   * 
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Updated agent
   */
  async suspendAgent(agentId) {
    return this.performAgentAction(agentId, 'suspend');
  }
  
  /**
   * Rescope an agent
   * 
   * @param {string} agentId - Agent ID
   * @param {Object} params - Rescope parameters
   * @returns {Promise<Object>} Updated agent
   */
  async rescopeAgent(agentId, params = {}) {
    return this.performAgentAction(agentId, 'rescope', params);
  }
}

export default UniversalSkinAPI;
