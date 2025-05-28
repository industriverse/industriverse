import React from 'react';
import { Box, Typography, Grid, Paper, LinearProgress, Chip } from '@mui/material';
import { useData } from '../../contexts/DataContext';

/**
 * Metrics Overview component that displays key system metrics and KPIs.
 * 
 * This implements the Progressive Disclosure design principle by showing
 * high-level metrics with drill-down capabilities, and the Live, Linked
 * Visuals principle by sharing a common data layer.
 */
const MetricsOverview = () => {
  const { getData, isLoading } = useData();
  
  // In a real implementation, this would fetch data from the backend
  // For now, we'll use placeholder data
  const metrics = {
    activeAgents: 128,
    totalProcesses: 56,
    runningProcesses: 23,
    systemHealth: 94,
    resourceUtilization: 78,
    anomaliesDetected: 3,
    trustScore: 92,
    capsuleEvolutions: 17
  };

  // Metric card component
  const MetricCard = ({ title, value, unit = '', color = 'primary', icon, progress = false }) => (
    <Paper 
      elevation={0} 
      sx={{ 
        p: 2, 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        borderLeft: 3,
        borderColor: `${color}.main`,
      }}
    >
      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'baseline', mb: 1 }}>
        <Typography variant="h4" component="span" fontWeight="bold">
          {value}
        </Typography>
        {unit && (
          <Typography variant="body2" component="span" color="textSecondary" sx={{ ml: 1 }}>
            {unit}
          </Typography>
        )}
      </Box>
      {progress && (
        <Box sx={{ width: '100%', mt: 'auto' }}>
          <LinearProgress 
            variant="determinate" 
            value={value} 
            color={color}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>
      )}
    </Paper>
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">System Metrics</Typography>
        <Chip 
          label={isLoading ? "Refreshing..." : "Live Data"} 
          color={isLoading ? "default" : "success"} 
          size="small" 
        />
      </Box>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="Active Agents" 
            value={metrics.activeAgents} 
            color="primary" 
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="Running Processes" 
            value={metrics.runningProcesses} 
            unit={`/ ${metrics.totalProcesses}`} 
            color="info" 
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="System Health" 
            value={metrics.systemHealth} 
            unit="%" 
            color="success" 
            progress={true} 
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="Resource Utilization" 
            value={metrics.resourceUtilization} 
            unit="%" 
            color="warning" 
            progress={true} 
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="Anomalies Detected" 
            value={metrics.anomaliesDetected} 
            color="error" 
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="Trust Score" 
            value={metrics.trustScore} 
            unit="%" 
            color="success" 
            progress={true} 
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="Capsule Evolutions" 
            value={metrics.capsuleEvolutions} 
            color="secondary" 
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard 
            title="Intelligence Market" 
            value="Active" 
            color="info" 
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default MetricsOverview;
