import React from 'react';
import { Box, Typography, Paper, Grid, Chip, CircularProgress } from '@mui/material';
import { useData } from '../../contexts/DataContext';

/**
 * System Status component that displays the current status of all system components.
 * 
 * This implements the Live, Linked Visuals design principle by providing
 * real-time status information with a common data layer.
 */
const SystemStatus = () => {
  const { getData, isLoading } = useData();
  
  // In a real implementation, this would fetch data from the backend
  // For now, we'll use placeholder data
  const systemComponents = [
    { name: 'Agent Management', status: 'healthy', uptime: '99.98%' },
    { name: 'Process Management', status: 'healthy', uptime: '99.95%' },
    { name: 'Monitoring & Analytics', status: 'healthy', uptime: '100%' },
    { name: 'Capsule Governance', status: 'warning', uptime: '98.72%' },
    { name: 'Trust Management', status: 'healthy', uptime: '99.91%' },
    { name: 'Capsule Evolution', status: 'healthy', uptime: '99.87%' },
    { name: 'Intelligence Market', status: 'healthy', uptime: '99.93%' },
    { name: 'Digital Twin Diplomacy', status: 'error', uptime: '97.45%' },
  ];

  // Status chip component
  const StatusChip = ({ status }) => {
    const statusConfig = {
      healthy: { label: 'Healthy', color: 'success' },
      warning: { label: 'Warning', color: 'warning' },
      error: { label: 'Error', color: 'error' },
      unknown: { label: 'Unknown', color: 'default' },
    };

    const config = statusConfig[status] || statusConfig.unknown;

    return (
      <Chip
        label={config.label}
        color={config.color}
        size="small"
        sx={{ minWidth: 80 }}
      />
    );
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">System Status</Typography>
        {isLoading ? (
          <CircularProgress size={20} />
        ) : (
          <Chip 
            label="Live Status" 
            color="success" 
            size="small" 
          />
        )}
      </Box>
      
      <Paper elevation={0} sx={{ p: 0, borderRadius: 2, overflow: 'hidden' }}>
        {systemComponents.map((component, index) => (
          <Box 
            key={component.name}
            sx={{ 
              p: 2, 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              borderBottom: index < systemComponents.length - 1 ? 1 : 0,
              borderColor: 'divider',
              bgcolor: index % 2 === 0 ? 'background.default' : 'background.paper',
            }}
          >
            <Box>
              <Typography variant="body2" fontWeight="medium">
                {component.name}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Uptime: {component.uptime}
              </Typography>
            </Box>
            <StatusChip status={component.status} />
          </Box>
        ))}
      </Paper>
      
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <Typography variant="caption" color="textSecondary">
          Last updated: {new Date().toLocaleTimeString()}
        </Typography>
      </Box>
    </Box>
  );
};

export default SystemStatus;
