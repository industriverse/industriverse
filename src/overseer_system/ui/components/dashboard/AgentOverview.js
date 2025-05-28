import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Avatar, LinearProgress, Chip } from '@mui/material';
import { useData } from '../../contexts/DataContext';

/**
 * Agent Overview component that displays information about active agents in the system.
 * 
 * This implements the Progressive Disclosure design principle by showing
 * high-level agent information with drill-down capabilities, and the
 * Live, Linked Visuals principle by sharing a common data layer.
 */
const AgentOverview = () => {
  const { getData, isLoading } = useData();
  
  // In a real implementation, this would fetch data from the backend
  // For now, we'll use placeholder data
  const agents = [
    {
      id: 'agent-001',
      name: 'Trust Bootstrap Agent',
      type: 'Core',
      status: 'active',
      trustScore: 98,
      lastActivity: '2025-05-25T09:15:22Z',
    },
    {
      id: 'agent-002',
      name: 'Capsule Instantiator Agent',
      type: 'Core',
      status: 'active',
      trustScore: 95,
      lastActivity: '2025-05-25T09:12:45Z',
    },
    {
      id: 'agent-003',
      name: 'Environment Resolver Agent',
      type: 'Core',
      status: 'active',
      trustScore: 97,
      lastActivity: '2025-05-25T09:10:18Z',
    },
    {
      id: 'agent-004',
      name: 'Breeding Strategy Agent',
      type: 'Evolution',
      status: 'active',
      trustScore: 92,
      lastActivity: '2025-05-25T09:05:33Z',
    },
  ];

  // Get status color
  const getStatusColor = (status) => {
    const statusColors = {
      active: 'success',
      warning: 'warning',
      error: 'error',
      inactive: 'default',
    };
    
    return statusColors[status] || 'default';
  };

  // Get agent type color
  const getAgentTypeColor = (type) => {
    const typeColors = {
      Core: '#1976d2',
      Evolution: '#9c27b0',
      Market: '#4caf50',
      Diplomacy: '#ff9800',
      Governance: '#f44336',
    };
    
    return typeColors[type] || '#757575';
  };

  // Format timestamp to relative time
  const formatRelativeTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.round(diffMs / 1000);
    const diffMin = Math.round(diffSec / 60);
    
    if (diffSec < 60) return `${diffSec} seconds ago`;
    if (diffMin < 60) return `${diffMin} minutes ago`;
    
    return date.toLocaleTimeString();
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">Agent Overview</Typography>
        <Chip 
          label={`${agents.length} Active Agents`} 
          color="primary" 
          size="small" 
        />
      </Box>
      
      <Grid container spacing={2}>
        {agents.map((agent) => (
          <Grid item xs={12} sm={6} key={agent.id}>
            <Card 
              elevation={0} 
              sx={{ 
                borderRadius: 2,
                border: 1,
                borderColor: 'divider',
              }}
            >
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                  <Avatar 
                    sx={{ 
                      bgcolor: getAgentTypeColor(agent.type),
                      width: 40,
                      height: 40,
                      mr: 2,
                    }}
                  >
                    {agent.name.charAt(0)}
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle1" fontWeight="medium" noWrap>
                      {agent.name}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Chip 
                        label={agent.type} 
                        size="small" 
                        sx={{ 
                          height: 20, 
                          fontSize: '0.7rem',
                          bgcolor: getAgentTypeColor(agent.type),
                          color: 'white',
                          mr: 1,
                        }} 
                      />
                      <Chip 
                        label={agent.status} 
                        size="small" 
                        color={getStatusColor(agent.status)} 
                        sx={{ height: 20, fontSize: '0.7rem' }} 
                      />
                    </Box>
                  </Box>
                </Box>
                
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                    <Typography variant="caption" color="textSecondary">
                      Trust Score
                    </Typography>
                    <Typography variant="caption" fontWeight="medium">
                      {agent.trustScore}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={agent.trustScore} 
                    color={agent.trustScore > 90 ? 'success' : agent.trustScore > 70 ? 'warning' : 'error'}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
                
                <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mt: 1.5, textAlign: 'right' }}>
                  Last activity: {formatRelativeTime(agent.lastActivity)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default AgentOverview;
