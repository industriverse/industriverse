import React from 'react';
import { Box, Grid, Typography, Paper, Divider } from '@mui/material';
import { useUIState } from '../../contexts/UIStateContext';
import { useAuth } from '../../contexts/AuthContext';
import MetricsOverview from './MetricsOverview';
import SystemStatus from './SystemStatus';
import RecentActivity from './RecentActivity';
import AgentOverview from './AgentOverview';
import ProcessOverview from './ProcessOverview';
import ConversationalAssistant from '../common/ConversationalAssistant';

/**
 * Main dashboard component that serves as the central hub for the Overseer System.
 * Displays different content based on the selected role and view.
 * 
 * This implements the Role-First, Context-Aware design principle by
 * adapting the dashboard content based on the user's role and selected view.
 * It also implements Progressive Disclosure by showing high-level metrics
 * with drill-down capabilities.
 */
const Dashboard = () => {
  const { currentView, selectedRole } = useUIState();
  const { user } = useAuth();

  // Render different dashboard content based on the selected view
  const renderDashboardContent = () => {
    switch (currentView) {
      case 'Master':
        return renderMasterView();
      case 'Domain':
        return renderDomainView();
      case 'Process':
        return renderProcessView();
      case 'Agent':
        return renderAgentView();
      default:
        return renderMasterView();
    }
  };

  // Master view - high-level overview of the entire system
  const renderMasterView = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Master Overview
        </Typography>
        <Typography variant="subtitle1" color="textSecondary" paragraph>
          Comprehensive view of the entire Industriverse ecosystem
        </Typography>
        <Divider />
      </Grid>
      
      {/* Metrics Overview */}
      <Grid item xs={12} md={8}>
        <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
          <MetricsOverview />
        </Paper>
      </Grid>
      
      {/* System Status */}
      <Grid item xs={12} md={4}>
        <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
          <SystemStatus />
        </Paper>
      </Grid>
      
      {/* Agent Overview */}
      <Grid item xs={12} md={6}>
        <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
          <AgentOverview />
        </Paper>
      </Grid>
      
      {/* Process Overview */}
      <Grid item xs={12} md={6}>
        <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
          <ProcessOverview />
        </Paper>
      </Grid>
      
      {/* Recent Activity */}
      <Grid item xs={12}>
        <Paper elevation={0} sx={{ p: 3 }}>
          <RecentActivity />
        </Paper>
      </Grid>
    </Grid>
  );

  // Domain view - focused on specific domains within the system
  const renderDomainView = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Domain Overview
        </Typography>
        <Typography variant="subtitle1" color="textSecondary" paragraph>
          Detailed view of domain-specific operations and metrics
        </Typography>
        <Divider />
      </Grid>
      
      {/* Domain-specific components will be implemented here */}
      <Grid item xs={12}>
        <Paper elevation={0} sx={{ p: 3, minHeight: '400px' }}>
          <Typography variant="h6" gutterBottom>
            Domain Metrics
          </Typography>
          {/* Domain metrics component will be implemented here */}
        </Paper>
      </Grid>
    </Grid>
  );

  // Process view - focused on specific processes and workflows
  const renderProcessView = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Process Overview
        </Typography>
        <Typography variant="subtitle1" color="textSecondary" paragraph>
          Detailed view of process execution and workflow status
        </Typography>
        <Divider />
      </Grid>
      
      {/* Process-specific components will be implemented here */}
      <Grid item xs={12}>
        <Paper elevation={0} sx={{ p: 3, minHeight: '400px' }}>
          <Typography variant="h6" gutterBottom>
            Process Execution
          </Typography>
          {/* Process execution component will be implemented here */}
        </Paper>
      </Grid>
    </Grid>
  );

  // Agent view - focused on specific agents and their activities
  const renderAgentView = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Agent Overview
        </Typography>
        <Typography variant="subtitle1" color="textSecondary" paragraph>
          Detailed view of agent activities and performance
        </Typography>
        <Divider />
      </Grid>
      
      {/* Agent-specific components will be implemented here */}
      <Grid item xs={12}>
        <Paper elevation={0} sx={{ p: 3, minHeight: '400px' }}>
          <Typography variant="h6" gutterBottom>
            Agent Performance
          </Typography>
          {/* Agent performance component will be implemented here */}
        </Paper>
      </Grid>
    </Grid>
  );

  return (
    <Box sx={{ p: 3 }}>
      {renderDashboardContent()}
      
      {/* Conversational Assistant - fixed position at bottom right */}
      <Box sx={{ position: 'fixed', bottom: 20, right: 20, zIndex: 1000 }}>
        <ConversationalAssistant />
      </Box>
    </Box>
  );
};

export default Dashboard;
