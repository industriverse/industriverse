import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Button, Tabs, Tab } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useData } from '../../contexts/DataContext';
import { useUIState } from '../../contexts/UIStateContext';

/**
 * Override Chain View component that visualizes how protocol events trigger
 * systemwide ripples and allows exploration of override chains.
 * 
 * This implements the Live, Linked Visuals design principle by providing
 * interactive visualization of override chains and their impacts.
 */
const OverrideChainView = () => {
  const { getData, isLoading } = useData();
  const { openModal } = useUIState();
  const [selectedChain, setSelectedChain] = useState(null);
  const [viewMode, setViewMode] = useState('timeline');
  
  // In a real implementation, this would fetch data from the backend
  // For now, we'll use placeholder data
  const overrideChains = [
    {
      id: 'chain-001',
      name: 'Resource Allocation Override',
      initiator: 'Production Manager',
      timestamp: '2025-05-25T08:15:22Z',
      status: 'active',
      impactLevel: 'medium',
      nodes: [
        { id: 'node-001', type: 'trigger', name: 'Manual Override', timestamp: '2025-05-25T08:15:22Z' },
        { id: 'node-002', type: 'process', name: 'Resource Allocation Process', timestamp: '2025-05-25T08:15:25Z' },
        { id: 'node-003', type: 'agent', name: 'Resource Manager Agent', timestamp: '2025-05-25T08:15:30Z' },
        { id: 'node-004', type: 'market', name: 'Intelligence Market Bid', timestamp: '2025-05-25T08:15:45Z' },
        { id: 'node-005', type: 'capsule', name: 'Optimization Capsule', timestamp: '2025-05-25T08:16:10Z' },
      ]
    },
    {
      id: 'chain-002',
      name: 'Maintenance Schedule Override',
      initiator: 'Maintenance Engineer',
      timestamp: '2025-05-25T07:45:12Z',
      status: 'completed',
      impactLevel: 'high',
      nodes: [
        { id: 'node-101', type: 'trigger', name: 'Manual Override', timestamp: '2025-05-25T07:45:12Z' },
        { id: 'node-102', type: 'process', name: 'Maintenance Scheduling Process', timestamp: '2025-05-25T07:45:18Z' },
        { id: 'node-103', type: 'agent', name: 'Maintenance Coordinator Agent', timestamp: '2025-05-25T07:45:25Z' },
        { id: 'node-104', type: 'twin', name: 'Equipment Digital Twin', timestamp: '2025-05-25T07:45:40Z' },
        { id: 'node-105', type: 'process', name: 'Production Planning Process', timestamp: '2025-05-25T07:46:15Z' },
        { id: 'node-106', type: 'agent', name: 'Production Scheduler Agent', timestamp: '2025-05-25T07:46:30Z' },
      ]
    },
  ];

  // Handle chain selection
  const handleChainSelect = (chainId) => {
    const chain = overrideChains.find(c => c.id === chainId);
    setSelectedChain(chain);
  };

  // Handle view mode change
  const handleViewModeChange = (event, newMode) => {
    setViewMode(newMode);
  };

  // Get node type color
  const getNodeTypeColor = (type) => {
    const typeColors = {
      trigger: '#f44336',
      process: '#2196f3',
      agent: '#4caf50',
      market: '#ff9800',
      capsule: '#9c27b0',
      twin: '#795548',
    };
    
    return typeColors[type] || '#9e9e9e';
  };

  // Get impact level color
  const getImpactLevelColor = (level) => {
    const levelColors = {
      low: '#4caf50',
      medium: '#ff9800',
      high: '#f44336',
    };
    
    return levelColors[level] || '#9e9e9e';
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

  // Styled components
  const TimelineContainer = styled(Box)(({ theme }) => ({
    position: 'relative',
    padding: theme.spacing(2, 0),
    marginLeft: theme.spacing(2),
    '&:before': {
      content: '""',
      position: 'absolute',
      top: 0,
      bottom: 0,
      left: 0,
      width: 2,
      backgroundColor: theme.palette.divider,
    },
  }));

  const TimelineNode = styled(Box)(({ theme, type }) => ({
    position: 'relative',
    marginBottom: theme.spacing(3),
    paddingLeft: theme.spacing(3),
    '&:before': {
      content: '""',
      position: 'absolute',
      top: 8,
      left: -4,
      width: 10,
      height: 10,
      borderRadius: '50%',
      backgroundColor: getNodeTypeColor(type),
      border: `2px solid ${theme.palette.background.paper}`,
      zIndex: 1,
    },
    '&:last-child': {
      marginBottom: 0,
    },
  }));

  const NetworkContainer = styled(Box)(({ theme }) => ({
    position: 'relative',
    width: '100%',
    height: 300,
    backgroundColor: theme.palette.background.default,
    borderRadius: theme.shape.borderRadius,
    padding: theme.spacing(2),
    // In a real implementation, this would be a D3.js or similar network visualization
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  }));

  // Render timeline view
  const renderTimelineView = () => {
    if (!selectedChain) return null;
    
    return (
      <TimelineContainer>
        {selectedChain.nodes.map((node) => (
          <TimelineNode key={node.id} type={node.type}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="subtitle2" fontWeight="medium">
                  {node.name}
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box
                    component="span"
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      bgcolor: getNodeTypeColor(node.type),
                      mr: 0.5,
                      display: 'inline-block',
                    }}
                  />
                  {node.type.charAt(0).toUpperCase() + node.type.slice(1)}
                </Typography>
              </Box>
              <Typography variant="caption" color="textSecondary">
                {formatRelativeTime(node.timestamp)}
              </Typography>
            </Box>
          </TimelineNode>
        ))}
      </TimelineContainer>
    );
  };

  // Render network view
  const renderNetworkView = () => {
    if (!selectedChain) return null;
    
    return (
      <NetworkContainer>
        <Typography variant="body2" color="textSecondary">
          Network visualization would be implemented here using D3.js or a similar library.
          This would show the nodes and connections in a network graph format.
        </Typography>
      </NetworkContainer>
    );
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Override Chain View
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper elevation={0} sx={{ p: 2, borderRadius: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Active Override Chains
            </Typography>
            
            {overrideChains.map((chain) => (
              <Card
                key={chain.id}
                elevation={0}
                sx={{
                  mb: 2,
                  border: 1,
                  borderColor: selectedChain?.id === chain.id ? 'primary.main' : 'divider',
                  borderRadius: 2,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: 'action.hover',
                  },
                }}
                onClick={() => handleChainSelect(chain.id)}
              >
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="subtitle2" fontWeight="medium">
                    {chain.name}
                  </Typography>
                  <Typography variant="caption" color="textSecondary" display="block">
                    Initiated by: {chain.initiator}
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                    <Typography variant="caption" color="textSecondary">
                      {formatRelativeTime(chain.timestamp)}
                    </Typography>
                    <Box
                      sx={{
                        px: 1,
                        py: 0.5,
                        borderRadius: 1,
                        fontSize: '0.7rem',
                        fontWeight: 'medium',
                        bgcolor: getImpactLevelColor(chain.impactLevel),
                        color: '#fff',
                      }}
                    >
                      {chain.impactLevel.toUpperCase()} IMPACT
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Paper elevation={0} sx={{ p: 2, borderRadius: 2 }}>
            {selectedChain ? (
              <>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle1">
                    {selectedChain.name}
                  </Typography>
                  <Button 
                    size="small" 
                    variant="outlined"
                    onClick={() => openModal('overrideDetail', { chainId: selectedChain.id })}
                  >
                    View Details
                  </Button>
                </Box>
                
                <Tabs
                  value={viewMode}
                  onChange={handleViewModeChange}
                  sx={{ mb: 2 }}
                >
                  <Tab value="timeline" label="Timeline" />
                  <Tab value="network" label="Network" />
                </Tabs>
                
                {viewMode === 'timeline' ? renderTimelineView() : renderNetworkView()}
              </>
            ) : (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="body1" color="textSecondary">
                  Select an override chain to view details
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default OverrideChainView;
