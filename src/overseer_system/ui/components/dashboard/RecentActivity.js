import React from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemText, ListItemAvatar, Avatar, Divider } from '@mui/material';
import { useData } from '../../contexts/DataContext';

/**
 * Recent Activity component that displays the latest system activities and events.
 * 
 * This implements the Live, Linked Visuals design principle by providing
 * real-time activity information with a common data layer.
 */
const RecentActivity = () => {
  const { getData, isLoading } = useData();
  
  // In a real implementation, this would fetch data from the backend
  // For now, we'll use placeholder data
  const activities = [
    {
      id: 1,
      type: 'agent',
      action: 'created',
      subject: 'Manufacturing Process Agent',
      timestamp: '2025-05-25T08:32:15Z',
      actor: 'System Administrator',
    },
    {
      id: 2,
      type: 'process',
      action: 'started',
      subject: 'Quality Control Workflow',
      timestamp: '2025-05-25T08:25:43Z',
      actor: 'Production Manager',
    },
    {
      id: 3,
      type: 'capsule',
      action: 'evolved',
      subject: 'Predictive Maintenance Capsule',
      timestamp: '2025-05-25T08:15:22Z',
      actor: 'Capsule Evolution Service',
    },
    {
      id: 4,
      type: 'market',
      action: 'transaction',
      subject: 'Resource Allocation Bid',
      timestamp: '2025-05-25T08:10:05Z',
      actor: 'Intelligence Market',
    },
    {
      id: 5,
      type: 'twin',
      action: 'negotiation',
      subject: 'Production Line Digital Twin',
      timestamp: '2025-05-25T08:05:37Z',
      actor: 'Twin Negotiation Agent',
    },
    {
      id: 6,
      type: 'system',
      action: 'alert',
      subject: 'Resource Utilization Threshold',
      timestamp: '2025-05-25T07:58:12Z',
      actor: 'Monitoring Service',
    },
  ];

  // Get avatar and color based on activity type
  const getActivityTypeInfo = (type) => {
    const typeConfig = {
      agent: { 
        icon: '🤖', 
        color: '#1976d2',
        label: 'Agent'
      },
      process: { 
        icon: '⚙️', 
        color: '#2196f3',
        label: 'Process'
      },
      capsule: { 
        icon: '🧬', 
        color: '#9c27b0',
        label: 'Capsule'
      },
      market: { 
        icon: '💹', 
        color: '#4caf50',
        label: 'Market'
      },
      twin: { 
        icon: '👥', 
        color: '#ff9800',
        label: 'Twin'
      },
      system: { 
        icon: '🖥️', 
        color: '#f44336',
        label: 'System'
      },
    };

    return typeConfig[type] || { icon: '❓', color: '#757575', label: 'Unknown' };
  };

  // Format timestamp to relative time
  const formatRelativeTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.round(diffMs / 1000);
    const diffMin = Math.round(diffSec / 60);
    const diffHour = Math.round(diffMin / 60);
    
    if (diffSec < 60) return `${diffSec} seconds ago`;
    if (diffMin < 60) return `${diffMin} minutes ago`;
    if (diffHour < 24) return `${diffHour} hours ago`;
    
    return date.toLocaleString();
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Recent Activity
      </Typography>
      
      <Paper elevation={0} sx={{ borderRadius: 2, overflow: 'hidden' }}>
        <List sx={{ width: '100%', p: 0 }}>
          {activities.map((activity, index) => {
            const typeInfo = getActivityTypeInfo(activity.type);
            
            return (
              <React.Fragment key={activity.id}>
                <ListItem alignItems="flex-start" sx={{ py: 1.5 }}>
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: typeInfo.color }}>
                      {typeInfo.icon}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Typography variant="body1" fontWeight="medium">
                        {activity.subject}
                      </Typography>
                    }
                    secondary={
                      <>
                        <Typography variant="body2" component="span" color="textSecondary">
                          {`${typeInfo.label} ${activity.action} by ${activity.actor}`}
                        </Typography>
                        <Typography variant="caption" component="div" color="textSecondary" sx={{ mt: 0.5 }}>
                          {formatRelativeTime(activity.timestamp)}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
                {index < activities.length - 1 && <Divider variant="inset" component="li" />}
              </React.Fragment>
            );
          })}
        </List>
      </Paper>
    </Box>
  );
};

export default RecentActivity;
