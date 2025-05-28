import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Avatar, LinearProgress, Chip, Divider } from '@mui/material';
import { useData } from '../../contexts/DataContext';

/**
 * Process Overview component that displays information about active processes in the system.
 * 
 * This implements the Progressive Disclosure design principle by showing
 * high-level process information with drill-down capabilities, and the
 * Live, Linked Visuals principle by sharing a common data layer.
 */
const ProcessOverview = () => {
  const { getData, isLoading } = useData();
  
  // In a real implementation, this would fetch data from the backend
  // For now, we'll use placeholder data
  const processes = [
    {
      id: 'process-001',
      name: 'Manufacturing Line Optimization',
      type: 'Optimization',
      status: 'running',
      progress: 65,
      startTime: '2025-05-25T08:30:00Z',
      estimatedCompletion: '2025-05-25T10:45:00Z',
    },
    {
      id: 'process-002',
      name: 'Quality Control Workflow',
      type: 'Workflow',
      status: 'running',
      progress: 42,
      startTime: '2025-05-25T08:25:43Z',
      estimatedCompletion: '2025-05-25T11:15:00Z',
    },
    {
      id: 'process-003',
      name: 'Predictive Maintenance Analysis',
      type: 'Analysis',
      status: 'running',
      progress: 78,
      startTime: '2025-05-25T08:15:22Z',
      estimatedCompletion: '2025-05-25T09:55:00Z',
    },
    {
      id: 'process-004',
      name: 'Supply Chain Optimization',
      type: 'Optimization',
      status: 'paused',
      progress: 35,
      startTime: '2025-05-25T08:05:37Z',
      estimatedCompletion: '2025-05-25T12:30:00Z',
    },
  ];

  // Get status color
  const getStatusColor = (status) => {
    const statusColors = {
      running: 'success',
      paused: 'warning',
      failed: 'error',
      completed: 'info',
      scheduled: 'default',
    };
    
    return statusColors[status] || 'default';
  };

  // Get process type color
  const getProcessTypeColor = (type) => {
    const typeColors = {
      Optimization: '#1976d2',
      Workflow: '#4caf50',
      Analysis: '#9c27b0',
      Simulation: '#ff9800',
      Maintenance: '#f44336',
    };
    
    return typeColors[type] || '#757575';
  };

  // Format time remaining
  const formatTimeRemaining = (estimatedCompletion) => {
    const now = new Date();
    const completion = new Date(estimatedCompletion);
    const diffMs = completion - now;
    
    if (diffMs <= 0) return 'Completed';
    
    const diffMin = Math.floor(diffMs / 60000);
    const hours = Math.floor(diffMin / 60);
    const minutes = diffMin % 60;
    
    return `${hours}h ${minutes}m remaining`;
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">Process Overview</Typography>
        <Chip 
          label={`${processes.filter(p => p.status === 'running').length} Running Processes`} 
          color="primary" 
          size="small" 
        />
      </Box>
      
      <Paper elevation={0} sx={{ borderRadius: 2, overflow: 'hidden' }}>
        {processes.map((process, index) => (
          <React.Fragment key={process.id}>
            <Box sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar 
                    sx={{ 
                      bgcolor: getProcessTypeColor(process.type),
                      width: 40,
                      height: 40,
                      mr: 2,
                    }}
                  >
                    {process.name.charAt(0)}
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle1" fontWeight="medium">
                      {process.name}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Chip 
                        label={process.type} 
                        size="small" 
                        sx={{ 
                          height: 20, 
                          fontSize: '0.7rem',
                          bgcolor: getProcessTypeColor(process.type),
                          color: 'white',
                          mr: 1,
                        }} 
                      />
                      <Chip 
                        label={process.status} 
                        size="small" 
                        color={getStatusColor(process.status)} 
                        sx={{ height: 20, fontSize: '0.7rem' }} 
                      />
                    </Box>
                  </Box>
                </Box>
                <Typography variant="caption" color="textSecondary">
                  {formatTimeRemaining(process.estimatedCompletion)}
                </Typography>
              </Box>
              
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                  <Typography variant="caption" color="textSecondary">
                    Progress
                  </Typography>
                  <Typography variant="caption" fontWeight="medium">
                    {process.progress}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={process.progress} 
                  color={process.status === 'running' ? 'primary' : process.status === 'paused' ? 'warning' : 'error'}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
            </Box>
            {index < processes.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </Paper>
    </Box>
  );
};

export default ProcessOverview;
