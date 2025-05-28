"""
Deployment Dashboard React Component for the Deployment Operations Layer.

This component provides a comprehensive dashboard for monitoring and managing
deployment operations across the Industriverse ecosystem.
"""

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Container, Grid, Paper, Typography, Button, Box, 
  Tabs, Tab, CircularProgress, Chip, Divider,
  Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, TablePagination,
  Dialog, DialogActions, DialogContent, DialogTitle,
  IconButton, Tooltip, Card, CardContent, CardActions,
  LinearProgress, Badge, AppBar, Toolbar
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  Undo as RollbackIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Timeline as TimelineIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Cloud as CloudIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  MoreVert as MoreIcon,
  Dashboard as DashboardIcon,
  List as ListIcon,
  History as HistoryIcon
} from '@mui/icons-material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import { format, parseISO, formatDistanceToNow } from 'date-fns';

// Import mission visualization component
import MissionVisualization from './mission_visualization';

// Define theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
});

// Status colors
const statusColors = {
  pending: '#2196f3',
  planning: '#00bcd4',
  simulating: '#9c27b0',
  executing: '#ff9800',
  paused: '#ffeb3b',
  succeeded: '#4caf50',
  failed: '#f44336',
  canceled: '#795548',
  rolling_back: '#9c27b0',
  rolled_back: '#2196f3'
};

// Status icons
const statusIcons = {
  pending: <InfoIcon />,
  planning: <TimelineIcon />,
  simulating: <MemoryIcon />,
  executing: <PlayArrow />,
  paused: <PauseIcon />,
  succeeded: <SuccessIcon />,
  failed: <ErrorIcon />,
  canceled: <StopIcon />,
  rolling_back: <RollbackIcon />,
  rolled_back: <UndoIcon />
};

/**
 * Dashboard component for the Deployment Operations Layer.
 * 
 * @param {Object} props Component props
 * @returns {JSX.Element} Dashboard component
 */
const Dashboard = (props) => {
  // State
  const [loading, setLoading] = useState(true);
  const [engineStatus, setEngineStatus] = useState({});
  const [missions, setMissions] = useState([]);
  const [selectedMission, setSelectedMission] = useState(null);
  const [missionDialogOpen, setMissionDialogOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [statusFilter, setStatusFilter] = useState('');
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds
  const [metrics, setMetrics] = useState({
    missionsByStatus: {},
    missionsByType: {},
    executionTimes: [],
    resourceUsage: []
  });
  const [alerts, setAlerts] = useState([]);
  
  // Fetch engine status
  const fetchEngineStatus = useCallback(async () => {
    try {
      const response = await fetch('/api/deployment/engine/status');
      const data = await response.json();
      
      if (data.status === 'success') {
        setEngineStatus(data);
      } else {
        console.error('Error fetching engine status:', data.message);
      }
    } catch (error) {
      console.error('Error fetching engine status:', error);
    }
  }, []);
  
  // Fetch missions
  const fetchMissions = useCallback(async () => {
    try {
      const response = await fetch(`/api/deployment/missions?status=${statusFilter}&limit=${rowsPerPage}&offset=${page * rowsPerPage}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setMissions(data.missions || []);
      } else {
        console.error('Error fetching missions:', data.message);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching missions:', error);
      setLoading(false);
    }
  }, [statusFilter, rowsPerPage, page]);
  
  // Fetch metrics
  const fetchMetrics = useCallback(async () => {
    try {
      const response = await fetch('/api/deployment/metrics');
      const data = await response.json();
      
      if (data.status === 'success') {
        setMetrics(data.metrics || {
          missionsByStatus: {},
          missionsByType: {},
          executionTimes: [],
          resourceUsage: []
        });
      } else {
        console.error('Error fetching metrics:', data.message);
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  }, []);
  
  // Fetch alerts
  const fetchAlerts = useCallback(async () => {
    try {
      const response = await fetch('/api/deployment/alerts');
      const data = await response.json();
      
      if (data.status === 'success') {
        setAlerts(data.alerts || []);
      } else {
        console.error('Error fetching alerts:', data.message);
      }
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  }, []);
  
  // Fetch mission details
  const fetchMissionDetails = useCallback(async (missionId) => {
    try {
      const response = await fetch(`/api/deployment/missions/${missionId}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setSelectedMission(data.mission);
        setMissionDialogOpen(true);
      } else {
        console.error('Error fetching mission details:', data.message);
      }
    } catch (error) {
      console.error('Error fetching mission details:', error);
    }
  }, []);
  
  // Start engine
  const startEngine = useCallback(async () => {
    try {
      const response = await fetch('/api/deployment/engine/start', {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchEngineStatus();
      } else {
        console.error('Error starting engine:', data.message);
      }
    } catch (error) {
      console.error('Error starting engine:', error);
    }
  }, [fetchEngineStatus]);
  
  // Stop engine
  const stopEngine = useCallback(async () => {
    try {
      const response = await fetch('/api/deployment/engine/stop', {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchEngineStatus();
      } else {
        console.error('Error stopping engine:', data.message);
      }
    } catch (error) {
      console.error('Error stopping engine:', error);
    }
  }, [fetchEngineStatus]);
  
  // Cancel mission
  const cancelMission = useCallback(async (missionId) => {
    try {
      const response = await fetch(`/api/deployment/missions/${missionId}/cancel`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchMissions();
        if (selectedMission && selectedMission.mission_id === missionId) {
          fetchMissionDetails(missionId);
        }
      } else {
        console.error('Error canceling mission:', data.message);
      }
    } catch (error) {
      console.error('Error canceling mission:', error);
    }
  }, [fetchMissions, fetchMissionDetails, selectedMission]);
  
  // Pause mission
  const pauseMission = useCallback(async (missionId) => {
    try {
      const response = await fetch(`/api/deployment/missions/${missionId}/pause`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchMissions();
        if (selectedMission && selectedMission.mission_id === missionId) {
          fetchMissionDetails(missionId);
        }
      } else {
        console.error('Error pausing mission:', data.message);
      }
    } catch (error) {
      console.error('Error pausing mission:', error);
    }
  }, [fetchMissions, fetchMissionDetails, selectedMission]);
  
  // Resume mission
  const resumeMission = useCallback(async (missionId) => {
    try {
      const response = await fetch(`/api/deployment/missions/${missionId}/resume`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchMissions();
        if (selectedMission && selectedMission.mission_id === missionId) {
          fetchMissionDetails(missionId);
        }
      } else {
        console.error('Error resuming mission:', data.message);
      }
    } catch (error) {
      console.error('Error resuming mission:', error);
    }
  }, [fetchMissions, fetchMissionDetails, selectedMission]);
  
  // Rollback mission
  const rollbackMission = useCallback(async (missionId) => {
    try {
      const response = await fetch(`/api/deployment/missions/${missionId}/rollback`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchMissions();
        if (selectedMission && selectedMission.mission_id === missionId) {
          fetchMissionDetails(missionId);
        }
      } else {
        console.error('Error rolling back mission:', data.message);
      }
    } catch (error) {
      console.error('Error rolling back mission:', error);
    }
  }, [fetchMissions, fetchMissionDetails, selectedMission]);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Handle page change
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  // Handle rows per page change
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // Handle status filter change
  const handleStatusFilterChange = (status) => {
    setStatusFilter(status);
    setPage(0);
  };
  
  // Handle refresh interval change
  const handleRefreshIntervalChange = (interval) => {
    setRefreshInterval(interval);
  };
  
  // Handle mission click
  const handleMissionClick = (missionId) => {
    fetchMissionDetails(missionId);
  };
  
  // Handle mission dialog close
  const handleMissionDialogClose = () => {
    setMissionDialogOpen(false);
  };
  
  // Handle refresh
  const handleRefresh = () => {
    setLoading(true);
    fetchEngineStatus();
    fetchMissions();
    fetchMetrics();
    fetchAlerts();
  };
  
  // Effect for initial data loading
  useEffect(() => {
    fetchEngineStatus();
    fetchMissions();
    fetchMetrics();
    fetchAlerts();
  }, [fetchEngineStatus, fetchMissions, fetchMetrics, fetchAlerts]);
  
  // Effect for auto-refresh
  useEffect(() => {
    const interval = setInterval(() => {
      fetchEngineStatus();
      fetchMissions();
      fetchMetrics();
      fetchAlerts();
    }, refreshInterval);
    
    return () => clearInterval(interval);
  }, [refreshInterval, fetchEngineStatus, fetchMissions, fetchMetrics, fetchAlerts]);
  
  // Effect for status filter changes
  useEffect(() => {
    fetchMissions();
  }, [statusFilter, page, rowsPerPage, fetchMissions]);
  
  // Prepare chart data for missions by status
  const missionsByStatusData = {
    labels: Object.keys(metrics.missionsByStatus),
    datasets: [
      {
        data: Object.values(metrics.missionsByStatus),
        backgroundColor: Object.keys(metrics.missionsByStatus).map(status => statusColors[status]),
        borderWidth: 1
      }
    ]
  };
  
  // Prepare chart data for missions by type
  const missionsByTypeData = {
    labels: Object.keys(metrics.missionsByType),
    datasets: [
      {
        data: Object.values(metrics.missionsByType),
        backgroundColor: [
          '#1976d2',
          '#dc004e',
          '#4caf50',
          '#ff9800',
          '#9c27b0',
          '#00bcd4',
          '#795548',
          '#607d8b'
        ],
        borderWidth: 1
      }
    ]
  };
  
  // Prepare chart data for execution times
  const executionTimesData = {
    labels: metrics.executionTimes.map(item => format(parseISO(item.timestamp), 'HH:mm')),
    datasets: [
      {
        label: 'Execution Time (seconds)',
        data: metrics.executionTimes.map(item => item.duration),
        fill: false,
        borderColor: '#1976d2',
        tension: 0.1
      }
    ]
  };
  
  // Prepare chart data for resource usage
  const resourceUsageData = {
    labels: metrics.resourceUsage.map(item => format(parseISO(item.timestamp), 'HH:mm')),
    datasets: [
      {
        label: 'CPU Usage (%)',
        data: metrics.resourceUsage.map(item => item.cpu),
        fill: false,
        borderColor: '#4caf50',
        tension: 0.1
      },
      {
        label: 'Memory Usage (%)',
        data: metrics.resourceUsage.map(item => item.memory),
        fill: false,
        borderColor: '#f44336',
        tension: 0.1
      }
    ]
  };
  
  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <DashboardIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Deployment Operations Dashboard
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Tooltip title="Refresh">
                <IconButton color="inherit" onClick={handleRefresh}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Settings">
                <IconButton color="inherit">
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Notifications">
                <IconButton color="inherit">
                  <Badge badgeContent={alerts.length} color="error">
                    <NotificationsIcon />
                  </Badge>
                </IconButton>
              </Tooltip>
            </Box>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          {/* Engine Status */}
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography component="h2" variant="h6" color="primary" gutterBottom>
                    Engine Status
                  </Typography>
                  <Box>
                    {engineStatus.is_running ? (
                      <Button
                        variant="contained"
                        color="error"
                        startIcon={<StopIcon />}
                        onClick={stopEngine}
                      >
                        Stop Engine
                      </Button>
                    ) : (
                      <Button
                        variant="contained"
                        color="primary"
                        startIcon={<StartIcon />}
                        onClick={startEngine}
                      >
                        Start Engine
                      </Button>
                    )}
                  </Box>
                </Box>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Status
                        </Typography>
                        <Typography variant="h5" component="div">
                          {engineStatus.is_running ? (
                            <Chip
                              icon={<CheckCircle />}
                              label="Running"
                              color="success"
                              variant="outlined"
                            />
                          ) : (
                            <Chip
                              icon={<StopIcon />}
                              label="Stopped"
                              color="error"
                              variant="outlined"
                            />
                          )}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Queue Size
                        </Typography>
                        <Typography variant="h5" component="div">
                          {engineStatus.queue_size || 0}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Active Missions
                        </Typography>
                        <Typography variant="h5" component="div">
                          {engineStatus.active_mission_count || 0}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          Workers
                        </Typography>
                        <Typography variant="h5" component="div">
                          {engineStatus.active_worker_count || 0} / {engineStatus.worker_count || 0}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          </Grid>
          
          {/* Tabs */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mt: 4 }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="dashboard tabs">
              <Tab label="Missions" icon={<ListIcon />} iconPosition="start" />
              <Tab label="Analytics" icon={<TimelineIcon />} iconPosition="start" />
              <Tab label="Alerts" icon={<WarningIcon />} iconPosition="start" />
            </Tabs>
          </Box>
          
          {/* Missions Tab */}
          {tabValue === 0 && (
            <Box sx={{ mt: 2 }}>
              <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography component="h2" variant="h6" color="primary" gutterBottom>
                    Missions
                  </Typography>
                  <Box>
                    <Button
                      variant="outlined"
                      startIcon={<FilterIcon />}
                      onClick={() => handleStatusFilterChange('')}
                      sx={{ mr: 1 }}
                    >
                      All
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<PlayArrow />}
                      onClick={() => handleStatusFilterChange('executing')}
                      sx={{ mr: 1 }}
                    >
                      Executing
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<SuccessIcon />}
                      onClick={() => handleStatusFilterChange('succeeded')}
                      sx={{ mr: 1 }}
                    >
                      Succeeded
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<ErrorIcon />}
                      onClick={() => handleStatusFilterChange('failed')}
                    >
                      Failed
                    </Button>
                  </Box>
                </Box>
                
                {loading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Mission ID</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Timestamp</TableCell>
                            <TableCell>Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {missions.map((mission) => (
                            <TableRow key={mission.mission_id}>
                              <TableCell>
                                <Button
                                  color="primary"
                                  onClick={() => handleMissionClick(mission.mission_id)}
                                >
                                  {mission.mission_id}
                                </Button>
                              </TableCell>
                              <TableCell>{mission.type || 'generic'}</TableCell>
                              <TableCell>
                                <Chip
                                  icon={statusIcons[mission.status]}
                                  label={mission.status}
                                  style={{
                                    backgroundColor: statusColors[mission.status],
                                    color: '#fff'
                                  }}
                                />
                              </TableCell>
                              <TableCell>
                                {mission.timestamp ? (
                                  <Tooltip title={format(parseISO(mission.timestamp), 'PPpp')}>
                                    <span>{formatDistanceToNow(parseISO(mission.timestamp), { addSuffix: true })}</span>
                                  </Tooltip>
                                ) : (
                                  'N/A'
                                )}
                              </TableCell>
                              <TableCell>
                                <Box>
                                  {mission.status === 'executing' && (
                                    <Tooltip title="Pause">
                                      <IconButton
                                        color="primary"
                                        onClick={() => pauseMission(mission.mission_id)}
                                      >
                                        <PauseIcon />
                                      </IconButton>
                                    </Tooltip>
                                  )}
                                  
                                  {mission.status === 'paused' && (
                                    <Tooltip title="Resume">
                                      <IconButton
                                        color="primary"
                                        onClick={() => resumeMission(mission.mission_id)}
                                      >
                                        <PlayArrow />
                                      </IconButton>
                                    </Tooltip>
                                  )}
                                  
                                  {['executing', 'paused'].includes(mission.status) && (
                                    <Tooltip title="Cancel">
                                      <IconButton
                                        color="error"
                                        onClick={() => cancelMission(mission.mission_id)}
                                      >
                                        <StopIcon />
                                      </IconButton>
                                    </Tooltip>
                                  )}
                                  
                                  {['succeeded', 'failed', 'executing'].includes(mission.status) && (
                                    <Tooltip title="Rollback">
                                      <IconButton
                                        color="secondary"
                                        onClick={() => rollbackMission(mission.mission_id)}
                                      >
                                        <RollbackIcon />
                                      </IconButton>
                                    </Tooltip>
                                  )}
                                  
                                  <Tooltip title="Details">
                                    <IconButton
                                      color="primary"
                                      onClick={() => handleMissionClick(mission.mission_id)}
                                    >
                                      <InfoIcon />
                                    </IconButton>
                                  </Tooltip>
                                </Box>
                              </TableCell>
                            </TableRow>
                          ))}
                          
                          {missions.length === 0 && (
                            <TableRow>
                              <TableCell colSpan={5} align="center">
                                No missions found
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </TableContainer>
                    
                    <TablePagination
                      rowsPerPageOptions={[5, 10, 25]}
                      component="div"
                      count={-1}
                      rowsPerPage={rowsPerPage}
                      page={page}
                      onPageChange={handleChangePage}
                      onRowsPerPageChange={handleChangeRowsPerPage}
                    />
                  </>
                )}
              </Paper>
            </Box>
          )}
          
          {/* Analytics Tab */}
          {tabValue === 1 && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 300 }}>
                    <Typography component="h2" variant="h6" color="primary" gutterBottom>
                      Missions by Status
                    </Typography>
                    <Box sx={{ flexGrow: 1 }}>
                      <Doughnut data={missionsByStatusData} options={{ maintainAspectRatio: false }} />
                    </Box>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 300 }}>
                    <Typography component="h2" variant="h6" color="primary" gutterBottom>
                      Missions by Type
                    </Typography>
                    <Box sx={{ flexGrow: 1 }}>
                      <Pie data={missionsByTypeData} options={{ maintainAspectRatio: false }} />
                    </Box>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 300 }}>
                    <Typography component="h2" variant="h6" color="primary" gutterBottom>
                      Execution Times
                    </Typography>
                    <Box sx={{ flexGrow: 1 }}>
                      <Line data={executionTimesData} options={{ maintainAspectRatio: false }} />
                    </Box>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 300 }}>
                    <Typography component="h2" variant="h6" color="primary" gutterBottom>
                      Resource Usage
                    </Typography>
                    <Box sx={{ flexGrow: 1 }}>
                      <Line data={resourceUsageData} options={{ maintainAspectRatio: false }} />
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          )}
          
          {/* Alerts Tab */}
          {tabValue === 2 && (
            <Box sx={{ mt: 2 }}>
              <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
                <Typography component="h2" variant="h6" color="primary" gutterBottom>
                  Alerts
                </Typography>
                
                {alerts.length === 0 ? (
                  <Box sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="body1">No alerts found</Typography>
                  </Box>
                ) : (
                  <List>
                    {alerts.map((alert) => (
                      <ListItem key={alert.id}>
                        <ListItemIcon>
                          {alert.severity === 'error' && <ErrorIcon color="error" />}
                          {alert.severity === 'warning' && <WarningIcon color="warning" />}
                          {alert.severity === 'info' && <InfoIcon color="info" />}
                        </ListItemIcon>
                        <ListItemText
                          primary={alert.message}
                          secondary={
                            <>
                              {alert.timestamp && (
                                <Typography
                                  component="span"
                                  variant="body2"
                                  color="textSecondary"
                                >
                                  {format(parseISO(alert.timestamp), 'PPpp')}
                                </Typography>
                              )}
                              {alert.details && (
                                <Typography
                                  component="span"
                                  variant="body2"
                                  color="textSecondary"
                                  sx={{ display: 'block' }}
                                >
                                  {alert.details}
                                </Typography>
                              )}
                            </>
                          }
                        />
                        <ListItemSecondaryAction>
                          <IconButton edge="end" aria-label="delete">
                            <DeleteIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                )}
              </Paper>
            </Box>
          )}
          
          {/* Mission Dialog */}
          <Dialog
            open={missionDialogOpen}
            onClose={handleMissionDialogClose}
            maxWidth="lg"
            fullWidth
          >
            {selectedMission && (
              <>
                <DialogTitle>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="h6">
                      Mission Details: {selectedMission.mission_id}
                    </Typography>
                    <Chip
                      icon={statusIcons[selectedMission.status]}
                      label={selectedMission.status}
                      style={{
                        backgroundColor: statusColors[selectedMission.status],
                        color: '#fff'
                      }}
                    />
                  </Box>
                </DialogTitle>
                <DialogContent dividers>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" gutterBottom>
                        Basic Information
                      </Typography>
                      <TableContainer component={Paper} variant="outlined">
                        <Table size="small">
                          <TableBody>
                            <TableRow>
                              <TableCell component="th" scope="row">Type</TableCell>
                              <TableCell>{selectedMission.type || 'generic'}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell component="th" scope="row">Priority</TableCell>
                              <TableCell>{selectedMission.priority}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell component="th" scope="row">Timestamp</TableCell>
                              <TableCell>
                                {selectedMission.timestamp ? format(parseISO(selectedMission.timestamp), 'PPpp') : 'N/A'}
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell component="th" scope="row">Engine ID</TableCell>
                              <TableCell>{selectedMission.engine_id}</TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </TableContainer>
                      
                      <Typography variant="subtitle1" gutterBottom sx={{ mt: 3 }}>
                        Timeline
                      </Typography>
                      <TableContainer component={Paper} variant="outlined">
                        <Table size="small">
                          <TableBody>
                            {selectedMission.planning_started_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Planning Started</TableCell>
                                <TableCell>{format(parseISO(selectedMission.planning_started_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.planning_completed_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Planning Completed</TableCell>
                                <TableCell>{format(parseISO(selectedMission.planning_completed_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.simulation_started_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Simulation Started</TableCell>
                                <TableCell>{format(parseISO(selectedMission.simulation_started_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.simulation_completed_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Simulation Completed</TableCell>
                                <TableCell>{format(parseISO(selectedMission.simulation_completed_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.execution_started_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Execution Started</TableCell>
                                <TableCell>{format(parseISO(selectedMission.execution_started_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.execution_completed_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Execution Completed</TableCell>
                                <TableCell>{format(parseISO(selectedMission.execution_completed_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.succeeded_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Succeeded At</TableCell>
                                <TableCell>{format(parseISO(selectedMission.succeeded_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.failed_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Failed At</TableCell>
                                <TableCell>{format(parseISO(selectedMission.failed_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.canceled_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Canceled At</TableCell>
                                <TableCell>{format(parseISO(selectedMission.canceled_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.paused_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Paused At</TableCell>
                                <TableCell>{format(parseISO(selectedMission.paused_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.resumed_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Resumed At</TableCell>
                                <TableCell>{format(parseISO(selectedMission.resumed_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.rollback_started_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Rollback Started</TableCell>
                                <TableCell>{format(parseISO(selectedMission.rollback_started_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                            {selectedMission.rollback_completed_at && (
                              <TableRow>
                                <TableCell component="th" scope="row">Rollback Completed</TableCell>
                                <TableCell>{format(parseISO(selectedMission.rollback_completed_at), 'PPpp')}</TableCell>
                              </TableRow>
                            )}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" gutterBottom>
                        Mission Visualization
                      </Typography>
                      <Paper variant="outlined" sx={{ p: 2, height: 300 }}>
                        <MissionVisualization mission={selectedMission} />
                      </Paper>
                      
                      {selectedMission.error && (
                        <Box sx={{ mt: 3 }}>
                          <Typography variant="subtitle1" gutterBottom color="error">
                            Error
                          </Typography>
                          <Paper variant="outlined" sx={{ p: 2, bgcolor: '#fff8f8' }}>
                            <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                              {selectedMission.error}
                            </Typography>
                          </Paper>
                        </Box>
                      )}
                      
                      {selectedMission.plan_summary && (
                        <Box sx={{ mt: 3 }}>
                          <Typography variant="subtitle1" gutterBottom>
                            Plan Summary
                          </Typography>
                          <Paper variant="outlined" sx={{ p: 2 }}>
                            <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                              {selectedMission.plan_summary}
                            </Typography>
                          </Paper>
                        </Box>
                      )}
                      
                      {selectedMission.simulation_summary && (
                        <Box sx={{ mt: 3 }}>
                          <Typography variant="subtitle1" gutterBottom>
                            Simulation Summary
                          </Typography>
                          <Paper variant="outlined" sx={{ p: 2 }}>
                            <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                              {selectedMission.simulation_summary}
                            </Typography>
                          </Paper>
                        </Box>
                      )}
                      
                      {selectedMission.execution_summary && (
                        <Box sx={{ mt: 3 }}>
                          <Typography variant="subtitle1" gutterBottom>
                            Execution Summary
                          </Typography>
                          <Paper variant="outlined" sx={{ p: 2 }}>
                            <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                              {selectedMission.execution_summary}
                            </Typography>
                          </Paper>
                        </Box>
                      )}
                    </Grid>
                  </Grid>
                </DialogContent>
                <DialogActions>
                  {['executing', 'paused'].includes(selectedMission.status) && (
                    <Button
                      color="error"
                      onClick={() => {
                        cancelMission(selectedMission.mission_id);
                        handleMissionDialogClose();
                      }}
                    >
                      Cancel Mission
                    </Button>
                  )}
                  
                  {selectedMission.status === 'executing' && (
                    <Button
                      color="primary"
                      onClick={() => {
                        pauseMission(selectedMission.mission_id);
                      }}
                    >
                      Pause Mission
                    </Button>
                  )}
                  
                  {selectedMission.status === 'paused' && (
                    <Button
                      color="primary"
                      onClick={() => {
                        resumeMission(selectedMission.mission_id);
                      }}
                    >
                      Resume Mission
                    </Button>
                  )}
                  
                  {['succeeded', 'failed', 'executing'].includes(selectedMission.status) && (
                    <Button
                      color="secondary"
                      onClick={() => {
                        rollbackMission(selectedMission.mission_id);
                      }}
                    >
                      Rollback Mission
                    </Button>
                  )}
                  
                  <Button onClick={handleMissionDialogClose}>Close</Button>
                </DialogActions>
              </>
            )}
          </Dialog>
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default Dashboard;
