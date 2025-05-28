"""
Mission Control Dashboard React Component for the Deployment Operations Layer

This component provides a comprehensive dashboard for monitoring and controlling
deployment operations across the Industriverse ecosystem.
"""

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Container, Grid, Paper, Typography, Box, Button, Chip, 
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Tabs, Tab, IconButton, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, MenuItem, Select, FormControl,
  InputLabel, Switch, FormControlLabel, Snackbar, Alert, Divider,
  Card, CardContent, CardActions, Tooltip, LinearProgress
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  Cancel as CancelIcon,
  Pause as PauseIcon,
  PlayArrow as ResumeIcon,
  Undo as RollbackIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Timeline as TimelineIcon,
  Storage as StorageIcon,
  Code as CodeIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Settings as SettingsIcon,
  Layers as LayersIcon,
  Dashboard as DashboardIcon
} from '@mui/icons-material';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, 
  Legend, ResponsiveContainer 
} from 'recharts';

// Mock API service - would be replaced with actual API calls
const apiService = {
  getEngineStatus: async () => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return {
      is_running: true,
      queue_size: 3,
      active_mission_count: 2,
      worker_count: 5,
      active_worker_count: 3,
      uptime_seconds: 3600,
      version: '1.0.0'
    };
  },
  
  getMissions: async (status, limit, offset) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const missions = [
      {
        mission_id: 'mission-12345678',
        type: 'DEPLOY',
        status: 'executing',
        priority: 1,
        target_layers: ['data-layer', 'core-ai-layer', 'application-layer'],
        timestamp: '2025-05-24T12:30:45',
        description: 'Deploy new data processing pipeline'
      },
      {
        mission_id: 'mission-87654321',
        type: 'UPDATE',
        status: 'planning',
        priority: 3,
        target_layers: ['ui-ux-layer'],
        timestamp: '2025-05-24T13:15:22',
        description: 'Update dashboard components'
      },
      {
        mission_id: 'mission-abcdef12',
        type: 'HEALTH_CHECK',
        status: 'succeeded',
        priority: 5,
        target_layers: ['protocol-layer', 'workflow-layer'],
        timestamp: '2025-05-24T11:45:10',
        description: 'Routine health check'
      },
      {
        mission_id: 'mission-12abcdef',
        type: 'SECURITY_SCAN',
        status: 'failed',
        priority: 2,
        target_layers: ['security-compliance-layer'],
        timestamp: '2025-05-24T10:20:33',
        description: 'Security vulnerability scan'
      },
      {
        mission_id: 'mission-a1b2c3d4',
        type: 'SCALE',
        status: 'pending',
        priority: 4,
        target_layers: ['application-layer'],
        timestamp: '2025-05-24T14:05:18',
        description: 'Scale application instances'
      }
    ];
    
    // Filter by status if provided
    const filteredMissions = status 
      ? missions.filter(m => m.status === status)
      : missions;
    
    // Apply pagination
    const paginatedMissions = filteredMissions.slice(offset, offset + limit);
    
    return {
      missions: paginatedMissions,
      total: filteredMissions.length
    };
  },
  
  getMission: async (missionId) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      mission_id: missionId,
      type: 'DEPLOY',
      status: 'executing',
      priority: 1,
      timestamp: '2025-05-24T12:30:45',
      engine_id: 'engine-1',
      target_layers: ['data-layer', 'core-ai-layer', 'application-layer'],
      configuration: {
        resources: {
          cpu: '2',
          memory: '4Gi'
        },
        replicas: 3,
        version: '1.2.0'
      },
      simulation_required: true,
      rollback_on_failure: true,
      timeout_seconds: 600,
      description: 'Deploy new data processing pipeline',
      planning_started_at: '2025-05-24T12:31:00',
      planning_completed_at: '2025-05-24T12:32:30',
      simulation_started_at: '2025-05-24T12:32:45',
      simulation_completed_at: '2025-05-24T12:35:15',
      execution_started_at: '2025-05-24T12:35:30',
      execution_completed_at: null,
      succeeded_at: null,
      failed_at: null,
      canceled_at: null,
      paused_at: null,
      resumed_at: null,
      rollback_started_at: null,
      rollback_completed_at: null,
      error: null,
      plan_summary: 'Deploy data processing pipeline to 3 target layers with 3 replicas',
      simulation_summary: 'Simulation successful with 0 errors and 2 warnings',
      execution_summary: 'Execution in progress (65%)',
      timeline: [
        {
          timestamp: '2025-05-24T12:30:45',
          event: 'Mission Created',
          status: 'info',
          details: 'Mission created with ID mission-12345678'
        },
        {
          timestamp: '2025-05-24T12:31:00',
          event: 'Planning Started',
          status: 'info',
          details: 'Mission planning started'
        },
        {
          timestamp: '2025-05-24T12:32:30',
          event: 'Planning Completed',
          status: 'success',
          details: 'Mission planning completed successfully'
        },
        {
          timestamp: '2025-05-24T12:32:45',
          event: 'Simulation Started',
          status: 'info',
          details: 'Mission simulation started'
        },
        {
          timestamp: '2025-05-24T12:34:15',
          event: 'Simulation Warning',
          status: 'warning',
          details: 'Network latency detected in data-layer'
        },
        {
          timestamp: '2025-05-24T12:34:45',
          event: 'Simulation Warning',
          status: 'warning',
          details: 'Resource contention possible in core-ai-layer'
        },
        {
          timestamp: '2025-05-24T12:35:15',
          event: 'Simulation Completed',
          status: 'success',
          details: 'Mission simulation completed successfully with 2 warnings'
        },
        {
          timestamp: '2025-05-24T12:35:30',
          event: 'Execution Started',
          status: 'info',
          details: 'Mission execution started'
        },
        {
          timestamp: '2025-05-24T12:37:45',
          event: 'Deployment Progress',
          status: 'info',
          details: 'Data layer deployment completed (33%)'
        },
        {
          timestamp: '2025-05-24T12:40:15',
          event: 'Deployment Progress',
          status: 'info',
          details: 'Core AI layer deployment completed (66%)'
        }
      ],
      resources: {
        pods: [
          { name: 'data-processor-0', status: 'Running', ready: true },
          { name: 'data-processor-1', status: 'Running', ready: true },
          { name: 'data-processor-2', status: 'Running', ready: true },
          { name: 'core-ai-model-0', status: 'Running', ready: true },
          { name: 'core-ai-model-1', status: 'Running', ready: true },
          { name: 'core-ai-model-2', status: 'Running', ready: true },
          { name: 'app-server-0', status: 'Pending', ready: false },
          { name: 'app-server-1', status: 'Pending', ready: false },
          { name: 'app-server-2', status: 'Pending', ready: false }
        ]
      },
      capsules: [
        { id: 'capsule-1', name: 'Data Processor', type: 'data-processor', layer: 'data-layer', status: 'active' },
        { id: 'capsule-2', name: 'Core AI Model', type: 'ai-model', layer: 'core-ai-layer', status: 'active' },
        { id: 'capsule-3', name: 'Application Server', type: 'app-server', layer: 'application-layer', status: 'pending' }
      ],
      layers: [
        { id: 'data-layer', name: 'Data Layer', status: 'active', progress: 100 },
        { id: 'core-ai-layer', name: 'Core AI Layer', status: 'active', progress: 100 },
        { id: 'application-layer', name: 'Application Layer', status: 'pending', progress: 0 }
      ],
      validation_results: {
        security: [
          { name: 'Authentication', status: 'passed', details: 'All authentication checks passed' },
          { name: 'Authorization', status: 'passed', details: 'All authorization checks passed' },
          { name: 'Encryption', status: 'passed', details: 'All encryption checks passed' }
        ],
        performance: [
          { name: 'Latency', status: 'warning', details: 'Latency slightly above threshold' },
          { name: 'Throughput', status: 'passed', details: 'Throughput meets requirements' },
          { name: 'Resource Usage', status: 'passed', details: 'Resource usage within limits' }
        ]
      }
    };
  },
  
  getLayers: async () => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 700));
    
    return {
      layers: [
        { id: 'data-layer', name: 'Data Layer', status: 'active', capsule_count: 12 },
        { id: 'core-ai-layer', name: 'Core AI Layer', status: 'active', capsule_count: 8 },
        { id: 'generative-layer', name: 'Generative Layer', status: 'active', capsule_count: 5 },
        { id: 'application-layer', name: 'Application Layer', status: 'active', capsule_count: 15 },
        { id: 'protocol-layer', name: 'Protocol Layer', status: 'active', capsule_count: 7 },
        { id: 'workflow-layer', name: 'Workflow Layer', status: 'active', capsule_count: 10 },
        { id: 'ui-ux-layer', name: 'UI/UX Layer', status: 'active', capsule_count: 20 },
        { id: 'security-compliance-layer', name: 'Security & Compliance Layer', status: 'active', capsule_count: 9 },
        { id: 'deployment-ops-layer', name: 'Deployment Operations Layer', status: 'active', capsule_count: 6 },
        { id: 'native-app-layer', name: 'Native App Layer', status: 'active', capsule_count: 4 }
      ]
    };
  },
  
  getCapsules: async (layerId, status) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const capsules = [
      { id: 'capsule-1', name: 'Data Processor', type: 'data-processor', layer: 'data-layer', status: 'active' },
      { id: 'capsule-2', name: 'Data Storage', type: 'data-storage', layer: 'data-layer', status: 'active' },
      { id: 'capsule-3', name: 'Core AI Model', type: 'ai-model', layer: 'core-ai-layer', status: 'active' },
      { id: 'capsule-4', name: 'Application Server', type: 'app-server', layer: 'application-layer', status: 'active' },
      { id: 'capsule-5', name: 'UI Dashboard', type: 'ui-component', layer: 'ui-ux-layer', status: 'active' },
      { id: 'capsule-6', name: 'Security Scanner', type: 'security-tool', layer: 'security-compliance-layer', status: 'inactive' },
      { id: 'capsule-7', name: 'Workflow Engine', type: 'workflow-engine', layer: 'workflow-layer', status: 'active' },
      { id: 'capsule-8', name: 'Protocol Bridge', type: 'protocol-bridge', layer: 'protocol-layer', status: 'active' },
      { id: 'capsule-9', name: 'Deployment Agent', type: 'deployment-agent', layer: 'deployment-ops-layer', status: 'active' },
      { id: 'capsule-10', name: 'Mobile App', type: 'native-app', layer: 'native-app-layer', status: 'active' }
    ];
    
    // Filter by layer if provided
    let filteredCapsules = capsules;
    if (layerId) {
      filteredCapsules = capsules.filter(c => c.layer === layerId);
    }
    
    // Filter by status if provided
    if (status) {
      filteredCapsules = filteredCapsules.filter(c => c.status === status);
    }
    
    return {
      capsules: filteredCapsules
    };
  },
  
  getTemplates: async () => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 600));
    
    return {
      templates: [
        { id: 'template-1', name: 'Standard Deployment', type: 'DEPLOY', description: 'Standard deployment template' },
        { id: 'template-2', name: 'High Availability', type: 'DEPLOY', description: 'High availability deployment template' },
        { id: 'template-3', name: 'Edge Deployment', type: 'DEPLOY', description: 'Edge device deployment template' },
        { id: 'template-4', name: 'Standard Update', type: 'UPDATE', description: 'Standard update template' },
        { id: 'template-5', name: 'Rolling Update', type: 'UPDATE', description: 'Rolling update template' },
        { id: 'template-6', name: 'Standard Rollback', type: 'ROLLBACK', description: 'Standard rollback template' },
        { id: 'template-7', name: 'Standard Scale', type: 'SCALE', description: 'Standard scaling template' },
        { id: 'template-8', name: 'Auto-scaling', type: 'SCALE', description: 'Auto-scaling template' },
        { id: 'template-9', name: 'Standard Backup', type: 'BACKUP', description: 'Standard backup template' },
        { id: 'template-10', name: 'Standard Restore', type: 'RESTORE', description: 'Standard restore template' }
      ]
    };
  },
  
  createMission: async (mission) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1200));
    
    return {
      mission_id: `mission-${Math.random().toString(36).substring(2, 10)}`,
      status: 'submitted',
      message: 'Mission submitted successfully'
    };
  },
  
  cancelMission: async (missionId) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    return {
      mission_id: missionId,
      status: 'canceled',
      message: 'Mission canceled successfully'
    };
  },
  
  pauseMission: async (missionId) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    return {
      mission_id: missionId,
      status: 'paused',
      message: 'Mission paused successfully'
    };
  },
  
  resumeMission: async (missionId) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    return {
      mission_id: missionId,
      status: 'resumed',
      message: 'Mission resumed successfully'
    };
  },
  
  rollbackMission: async (missionId) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    return {
      mission_id: missionId,
      status: 'rollback_initiated',
      message: 'Mission rollback initiated successfully'
    };
  }
};

// Status color mapping
const getStatusColor = (status) => {
  switch (status) {
    case 'active':
    case 'succeeded':
    case 'success':
    case 'passed':
      return '#4caf50'; // Green
    case 'failed':
    case 'inactive':
    case 'error':
      return '#f44336'; // Red
    case 'pending':
    case 'paused':
    case 'rolling_back':
    case 'rolled_back':
    case 'warning':
      return '#ff9800'; // Orange
    case 'planning':
    case 'simulating':
    case 'executing':
    case 'info':
      return '#2196f3'; // Blue
    default:
      return '#9e9e9e'; // Grey
  }
};

// Status icon mapping
const getStatusIcon = (status) => {
  switch (status) {
    case 'active':
    case 'succeeded':
    case 'success':
    case 'passed':
      return <SuccessIcon style={{ color: getStatusColor(status) }} />;
    case 'failed':
    case 'inactive':
    case 'error':
      return <ErrorIcon style={{ color: getStatusColor(status) }} />;
    case 'pending':
    case 'paused':
    case 'rolling_back':
    case 'rolled_back':
    case 'warning':
      return <WarningIcon style={{ color: getStatusColor(status) }} />;
    case 'planning':
    case 'simulating':
    case 'executing':
    case 'info':
      return <InfoIcon style={{ color: getStatusColor(status) }} />;
    default:
      return <InfoIcon style={{ color: getStatusColor(status) }} />;
  }
};

// Mission creation dialog component
const CreateMissionDialog = ({ open, onClose, onSubmit }) => {
  const [missionType, setMissionType] = useState('DEPLOY');
  const [priority, setPriority] = useState(5);
  const [targetLayers, setTargetLayers] = useState([]);
  const [description, setDescription] = useState('');
  const [simulationRequired, setSimulationRequired] = useState(true);
  const [rollbackOnFailure, setRollbackOnFailure] = useState(true);
  const [timeout, setTimeout] = useState('');
  const [template, setTemplate] = useState('');
  const [templates, setTemplates] = useState([]);
  const [layers, setLayers] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Mission types
  const missionTypes = [
    'DEPLOY', 'UPDATE', 'ROLLBACK', 'SCALE', 'MIGRATE', 
    'BACKUP', 'RESTORE', 'HEALTH_CHECK', 'SECURITY_SCAN', 'COMPLIANCE_CHECK'
  ];
  
  // Load templates and layers
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [templatesResponse, layersResponse] = await Promise.all([
          apiService.getTemplates(),
          apiService.getLayers()
        ]);
        
        setTemplates(templatesResponse.templates);
        setLayers(layersResponse.layers);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (open) {
      loadData();
    }
  }, [open]);
  
  // Handle layer selection
  const handleLayerChange = (event) => {
    setTargetLayers(event.target.value);
  };
  
  // Handle form submission
  const handleSubmit = () => {
    const mission = {
      mission_type: missionType,
      priority: priority,
      target_layers: targetLayers,
      configuration: {},
      simulation_required: simulationRequired,
      rollback_on_failure: rollbackOnFailure,
      timeout_seconds: timeout ? parseInt(timeout) : null,
      description: description || null,
      template: template || null
    };
    
    onSubmit(mission);
  };
  
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New Mission</DialogTitle>
      <DialogContent>
        {loading ? (
          <Box display="flex" justifyContent="center" my={4}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Mission Type</InputLabel>
                <Select
                  value={missionType}
                  onChange={(e) => setMissionType(e.target.value)}
                  label="Mission Type"
                >
                  {missionTypes.map((type) => (
                    <MenuItem key={type} value={type}>{type}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  label="Priority"
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((p) => (
                    <MenuItem key={p} value={p}>{p} {p === 1 ? '(Highest)' : p === 10 ? '(Lowest)' : ''}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Target Layers</InputLabel>
                <Select
                  multiple
                  value={targetLayers}
                  onChange={handleLayerChange}
                  label="Target Layers"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={layers.find(l => l.id === value)?.name || value} />
                      ))}
                    </Box>
                  )}
                >
                  {layers.map((layer) => (
                    <MenuItem key={layer.id} value={layer.id}>
                      {layer.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                multiline
                rows={2}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Template (Optional)</InputLabel>
                <Select
                  value={template}
                  onChange={(e) => setTemplate(e.target.value)}
                  label="Template (Optional)"
                >
                  <MenuItem value="">None</MenuItem>
                  {templates
                    .filter(t => t.type === missionType)
                    .map((t) => (
                      <MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>
                    ))
                  }
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Timeout (seconds, optional)"
                value={timeout}
                onChange={(e) => setTimeout(e.target.value)}
                type="number"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={simulationRequired}
                    onChange={(e) => setSimulationRequired(e.target.checked)}
                  />
                }
                label="Require Simulation"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={rollbackOnFailure}
                    onChange={(e) => setRollbackOnFailure(e.target.checked)}
                  />
                }
                label="Rollback on Failure"
              />
            </Grid>
          </Grid>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          color="primary"
          disabled={loading || targetLayers.length === 0}
        >
          Create Mission
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Mission details dialog component
const MissionDetailsDialog = ({ open, onClose, missionId }) => {
  const [mission, setMission] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  
  // Load mission details
  useEffect(() => {
    const loadMission = async () => {
      if (!missionId) return;
      
      setLoading(true);
      try {
        const missionData = await apiService.getMission(missionId);
        setMission(missionData);
      } catch (error) {
        console.error('Error loading mission:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (open && missionId) {
      loadMission();
    }
  }, [open, missionId]);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Calculate mission progress
  const calculateProgress = () => {
    if (!mission) return 0;
    
    if (mission.status === 'succeeded') return 100;
    if (mission.status === 'failed') return 100;
    if (mission.status === 'planning') return 10;
    if (mission.status === 'simulating') return 30;
    
    if (mission.status === 'executing') {
      // Calculate based on layer progress
      if (mission.layers && mission.layers.length > 0) {
        const totalProgress = mission.layers.reduce((sum, layer) => sum + layer.progress, 0);
        return Math.floor(totalProgress / mission.layers.length);
      }
      
      // Default to 50% if no layer progress available
      return 50;
    }
    
    return 0;
  };
  
  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        Mission Details
        {mission && (
          <Typography variant="subtitle1" component="span" sx={{ ml: 1 }}>
            {mission.mission_id}
          </Typography>
        )}
      </DialogTitle>
      <DialogContent>
        {loading ? (
          <Box display="flex" justifyContent="center" my={4}>
            <CircularProgress />
          </Box>
        ) : mission ? (
          <Box>
            {/* Mission header */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={8}>
                <Typography variant="h6">{mission.description || mission.type}</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <Chip 
                    label={mission.status} 
                    sx={{ 
                      backgroundColor: getStatusColor(mission.status),
                      color: 'white',
                      mr: 1
                    }} 
                  />
                  <Typography variant="body2">
                    Priority: {mission.priority}
                  </Typography>
                  <Typography variant="body2" sx={{ ml: 2 }}>
                    Created: {new Date(mission.timestamp).toLocaleString()}
                  </Typography>
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    Target Layers: {mission.target_layers.join(', ')}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="h4">{calculateProgress()}%</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={calculateProgress()} 
                    sx={{ height: 10, borderRadius: 5, mt: 1 }}
                  />
                  <Box sx={{ mt: 2 }}>
                    <Button 
                      variant="outlined" 
                      color="error" 
                      startIcon={<CancelIcon />}
                      sx={{ mr: 1 }}
                      disabled={['succeeded', 'failed', 'canceled'].includes(mission.status)}
                    >
                      Cancel
                    </Button>
                    {mission.status === 'executing' && (
                      <Button 
                        variant="outlined" 
                        color="warning" 
                        startIcon={<PauseIcon />}
                        sx={{ mr: 1 }}
                      >
                        Pause
                      </Button>
                    )}
                    {mission.status === 'paused' && (
                      <Button 
                        variant="outlined" 
                        color="primary" 
                        startIcon={<ResumeIcon />}
                        sx={{ mr: 1 }}
                      >
                        Resume
                      </Button>
                    )}
                    {['executing', 'succeeded'].includes(mission.status) && (
                      <Button 
                        variant="outlined" 
                        color="secondary" 
                        startIcon={<RollbackIcon />}
                      >
                        Rollback
                      </Button>
                    )}
                  </Box>
                </Box>
              </Grid>
            </Grid>
            
            {/* Mission tabs */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={activeTab} onChange={handleTabChange}>
                <Tab label="Timeline" icon={<TimelineIcon />} iconPosition="start" />
                <Tab label="Resources" icon={<StorageIcon />} iconPosition="start" />
                <Tab label="Configuration" icon={<CodeIcon />} iconPosition="start" />
                <Tab label="Validation" icon={<SecurityIcon />} iconPosition="start" />
                <Tab label="Metrics" icon={<SpeedIcon />} iconPosition="start" />
              </Tabs>
            </Box>
            
            {/* Timeline tab */}
            {activeTab === 0 && (
              <Box sx={{ py: 2 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Mission Timeline</Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>Event</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Details</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {mission.timeline.map((event, index) => (
                        <TableRow key={index}>
                          <TableCell>{new Date(event.timestamp).toLocaleString()}</TableCell>
                          <TableCell>{event.event}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              {getStatusIcon(event.status)}
                              <Typography sx={{ ml: 1 }}>{event.status}</Typography>
                            </Box>
                          </TableCell>
                          <TableCell>{event.details}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
            
            {/* Resources tab */}
            {activeTab === 1 && (
              <Box sx={{ py: 2 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Capsules</Typography>
                <TableContainer component={Paper} variant="outlined" sx={{ mb: 4 }}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>ID</TableCell>
                        <TableCell>Name</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Layer</TableCell>
                        <TableCell>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {mission.capsules.map((capsule) => (
                        <TableRow key={capsule.id}>
                          <TableCell>{capsule.id}</TableCell>
                          <TableCell>{capsule.name}</TableCell>
                          <TableCell>{capsule.type}</TableCell>
                          <TableCell>{capsule.layer}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              {getStatusIcon(capsule.status)}
                              <Typography sx={{ ml: 1 }}>{capsule.status}</Typography>
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                
                <Typography variant="h6" sx={{ mb: 2 }}>Pods</Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Ready</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {mission.resources.pods.map((pod) => (
                        <TableRow key={pod.name}>
                          <TableCell>{pod.name}</TableCell>
                          <TableCell>{pod.status}</TableCell>
                          <TableCell>
                            {pod.ready ? (
                              <SuccessIcon style={{ color: '#4caf50' }} />
                            ) : (
                              <ErrorIcon style={{ color: '#f44336' }} />
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
            
            {/* Configuration tab */}
            {activeTab === 2 && (
              <Box sx={{ py: 2 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Mission Configuration</Typography>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <pre style={{ overflow: 'auto', maxHeight: '400px' }}>
                    {JSON.stringify(mission.configuration, null, 2)}
                  </pre>
                </Paper>
                
                <Grid container spacing={2} sx={{ mt: 2 }}>
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="subtitle1" sx={{ mb: 1 }}>Mission Settings</Typography>
                      <Typography variant="body2">
                        Simulation Required: {mission.simulation_required ? 'Yes' : 'No'}
                      </Typography>
                      <Typography variant="body2">
                        Rollback on Failure: {mission.rollback_on_failure ? 'Yes' : 'No'}
                      </Typography>
                      <Typography variant="body2">
                        Timeout: {mission.timeout_seconds ? `${mission.timeout_seconds} seconds` : 'None'}
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="subtitle1" sx={{ mb: 1 }}>Summary</Typography>
                      <Typography variant="body2">
                        Plan: {mission.plan_summary || 'N/A'}
                      </Typography>
                      <Typography variant="body2">
                        Simulation: {mission.simulation_summary || 'N/A'}
                      </Typography>
                      <Typography variant="body2">
                        Execution: {mission.execution_summary || 'N/A'}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Box>
            )}
            
            {/* Validation tab */}
            {activeTab === 3 && (
              <Box sx={{ py: 2 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Validation Results</Typography>
                
                <Typography variant="subtitle1" sx={{ mb: 1 }}>Security</Typography>
                <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Check</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Details</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {mission.validation_results.security.map((check, index) => (
                        <TableRow key={index}>
                          <TableCell>{check.name}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              {getStatusIcon(check.status)}
                              <Typography sx={{ ml: 1 }}>{check.status}</Typography>
                            </Box>
                          </TableCell>
                          <TableCell>{check.details}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                
                <Typography variant="subtitle1" sx={{ mb: 1 }}>Performance</Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Check</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Details</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {mission.validation_results.performance.map((check, index) => (
                        <TableRow key={index}>
                          <TableCell>{check.name}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              {getStatusIcon(check.status)}
                              <Typography sx={{ ml: 1 }}>{check.status}</Typography>
                            </Box>
                          </TableCell>
                          <TableCell>{check.details}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
            
            {/* Metrics tab */}
            {activeTab === 4 && (
              <Box sx={{ py: 2 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Mission Metrics</Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="subtitle1" sx={{ mb: 2 }}>Layer Progress</Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart
                          data={mission.layers}
                          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <RechartsTooltip />
                          <Legend />
                          <Bar dataKey="progress" name="Progress (%)" fill="#8884d8" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="subtitle1" sx={{ mb: 2 }}>Timeline Distribution</Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={[
                              { name: 'Planning', value: 10 },
                              { name: 'Simulation', value: 20 },
                              { name: 'Execution', value: 70 }
                            ]}
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          >
                            <Cell fill="#8884d8" />
                            <Cell fill="#82ca9d" />
                            <Cell fill="#ffc658" />
                          </Pie>
                          <RechartsTooltip />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </Paper>
                  </Grid>
                </Grid>
              </Box>
            )}
          </Box>
        ) : (
          <Typography>No mission data available</Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

// Main dashboard component
const MissionControlDashboard = () => {
  const [engineStatus, setEngineStatus] = useState(null);
  const [missions, setMissions] = useState([]);
  const [totalMissions, setTotalMissions] = useState(0);
  const [layers, setLayers] = useState([]);
  const [capsules, setCapsules] = useState([]);
  const [loading, setLoading] = useState({
    status: false,
    missions: false,
    layers: false,
    capsules: false
  });
  const [activeTab, setActiveTab] = useState(0);
  const [missionFilter, setMissionFilter] = useState('');
  const [missionLimit, setMissionLimit] = useState(5);
  const [missionOffset, setMissionOffset] = useState(0);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [selectedMissionId, setSelectedMissionId] = useState(null);
  const [notification, setNotification] = useState({
    open: false,
    message: '',
    severity: 'info'
  });
  
  // Load initial data
  useEffect(() => {
    loadEngineStatus();
    loadMissions();
    loadLayers();
    loadCapsules();
    
    // Set up refresh interval
    const intervalId = setInterval(() => {
      loadEngineStatus();
      if (activeTab === 0) loadMissions();
      if (activeTab === 1) loadLayers();
      if (activeTab === 2) loadCapsules();
    }, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(intervalId);
  }, []);
  
  // Load engine status
  const loadEngineStatus = async () => {
    setLoading(prev => ({ ...prev, status: true }));
    try {
      const status = await apiService.getEngineStatus();
      setEngineStatus(status);
    } catch (error) {
      console.error('Error loading engine status:', error);
      showNotification('Error loading engine status', 'error');
    } finally {
      setLoading(prev => ({ ...prev, status: false }));
    }
  };
  
  // Load missions
  const loadMissions = async () => {
    setLoading(prev => ({ ...prev, missions: true }));
    try {
      const { missions, total } = await apiService.getMissions(missionFilter, missionLimit, missionOffset);
      setMissions(missions);
      setTotalMissions(total);
    } catch (error) {
      console.error('Error loading missions:', error);
      showNotification('Error loading missions', 'error');
    } finally {
      setLoading(prev => ({ ...prev, missions: false }));
    }
  };
  
  // Load layers
  const loadLayers = async () => {
    setLoading(prev => ({ ...prev, layers: true }));
    try {
      const { layers } = await apiService.getLayers();
      setLayers(layers);
    } catch (error) {
      console.error('Error loading layers:', error);
      showNotification('Error loading layers', 'error');
    } finally {
      setLoading(prev => ({ ...prev, layers: false }));
    }
  };
  
  // Load capsules
  const loadCapsules = async () => {
    setLoading(prev => ({ ...prev, capsules: true }));
    try {
      const { capsules } = await apiService.getCapsules();
      setCapsules(capsules);
    } catch (error) {
      console.error('Error loading capsules:', error);
      showNotification('Error loading capsules', 'error');
    } finally {
      setLoading(prev => ({ ...prev, capsules: false }));
    }
  };
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    
    // Load data for the selected tab
    if (newValue === 0) loadMissions();
    if (newValue === 1) loadLayers();
    if (newValue === 2) loadCapsules();
  };
  
  // Handle mission filter change
  const handleMissionFilterChange = (event) => {
    setMissionFilter(event.target.value);
    setMissionOffset(0); // Reset offset when filter changes
    
    // Load missions with new filter
    setTimeout(() => {
      loadMissions();
    }, 100);
  };
  
  // Handle mission creation
  const handleCreateMission = async (mission) => {
    try {
      const result = await apiService.createMission(mission);
      showNotification(`Mission ${result.mission_id} created successfully`, 'success');
      setCreateDialogOpen(false);
      loadMissions(); // Reload missions
    } catch (error) {
      console.error('Error creating mission:', error);
      showNotification('Error creating mission', 'error');
    }
  };
  
  // Handle mission action (cancel, pause, resume, rollback)
  const handleMissionAction = async (action, missionId) => {
    try {
      let result;
      
      switch (action) {
        case 'cancel':
          result = await apiService.cancelMission(missionId);
          break;
        case 'pause':
          result = await apiService.pauseMission(missionId);
          break;
        case 'resume':
          result = await apiService.resumeMission(missionId);
          break;
        case 'rollback':
          result = await apiService.rollbackMission(missionId);
          break;
        default:
          throw new Error(`Unknown action: ${action}`);
      }
      
      showNotification(result.message, 'success');
      loadMissions(); // Reload missions
    } catch (error) {
      console.error(`Error ${action} mission:`, error);
      showNotification(`Error ${action} mission`, 'error');
    }
  };
  
  // Show notification
  const showNotification = (message, severity = 'info') => {
    setNotification({
      open: true,
      message,
      severity
    });
  };
  
  // Handle notification close
  const handleNotificationClose = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };
  
  // Handle mission details
  const handleMissionDetails = (missionId) => {
    setSelectedMissionId(missionId);
    setDetailsDialogOpen(true);
  };
  
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Grid container spacing={3} alignItems="center" sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Typography variant="h4" component="h1" gutterBottom>
            Mission Control Dashboard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Deployment Operations Layer Command Center
          </Typography>
        </Grid>
        <Grid item xs={12} md={4} sx={{ textAlign: 'right' }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ mr: 1 }}
          >
            New Mission
          </Button>
          <IconButton onClick={() => {
            loadEngineStatus();
            loadMissions();
            loadLayers();
            loadCapsules();
          }}>
            <RefreshIcon />
          </IconButton>
        </Grid>
      </Grid>
      
      {/* Status Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
            }}
          >
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Engine Status
            </Typography>
            {loading.status ? (
              <Box display="flex" justifyContent="center" alignItems="center" flexGrow={1}>
                <CircularProgress size={24} />
              </Box>
            ) : engineStatus ? (
              <Box sx={{ mt: 1 }}>
                <Typography component="p" variant="h4">
                  {engineStatus.is_running ? 'Running' : 'Stopped'}
                </Typography>
                <Typography color="text.secondary" sx={{ flex: 1 }}>
                  Uptime: {engineStatus.uptime_seconds 
                    ? new Date(engineStatus.uptime_seconds * 1000).toISOString().substr(11, 8)
                    : 'N/A'
                  }
                </Typography>
              </Box>
            ) : (
              <Typography color="text.secondary">No data available</Typography>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
            }}
          >
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Active Missions
            </Typography>
            {loading.status ? (
              <Box display="flex" justifyContent="center" alignItems="center" flexGrow={1}>
                <CircularProgress size={24} />
              </Box>
            ) : engineStatus ? (
              <Box sx={{ mt: 1 }}>
                <Typography component="p" variant="h4">
                  {engineStatus.active_mission_count}
                </Typography>
                <Typography color="text.secondary" sx={{ flex: 1 }}>
                  Queue Size: {engineStatus.queue_size}
                </Typography>
              </Box>
            ) : (
              <Typography color="text.secondary">No data available</Typography>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
            }}
          >
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Workers
            </Typography>
            {loading.status ? (
              <Box display="flex" justifyContent="center" alignItems="center" flexGrow={1}>
                <CircularProgress size={24} />
              </Box>
            ) : engineStatus ? (
              <Box sx={{ mt: 1 }}>
                <Typography component="p" variant="h4">
                  {engineStatus.active_worker_count}/{engineStatus.worker_count}
                </Typography>
                <Typography color="text.secondary" sx={{ flex: 1 }}>
                  Active/Total
                </Typography>
              </Box>
            ) : (
              <Typography color="text.secondary">No data available</Typography>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
            }}
          >
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Total Capsules
            </Typography>
            {loading.capsules ? (
              <Box display="flex" justifyContent="center" alignItems="center" flexGrow={1}>
                <CircularProgress size={24} />
              </Box>
            ) : (
              <Box sx={{ mt: 1 }}>
                <Typography component="p" variant="h4">
                  {capsules.length}
                </Typography>
                <Typography color="text.secondary" sx={{ flex: 1 }}>
                  Across {layers.length} layers
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
      
      {/* Main Content */}
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Missions" icon={<DashboardIcon />} iconPosition="start" />
            <Tab label="Layers" icon={<LayersIcon />} iconPosition="start" />
            <Tab label="Capsules" icon={<StorageIcon />} iconPosition="start" />
            <Tab label="Settings" icon={<SettingsIcon />} iconPosition="start" />
          </Tabs>
        </Box>
        
        {/* Missions Tab */}
        {activeTab === 0 && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel>Status Filter</InputLabel>
                <Select
                  value={missionFilter}
                  onChange={handleMissionFilterChange}
                  label="Status Filter"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="planning">Planning</MenuItem>
                  <MenuItem value="simulating">Simulating</MenuItem>
                  <MenuItem value="executing">Executing</MenuItem>
                  <MenuItem value="succeeded">Succeeded</MenuItem>
                  <MenuItem value="failed">Failed</MenuItem>
                  <MenuItem value="canceled">Canceled</MenuItem>
                  <MenuItem value="paused">Paused</MenuItem>
                </Select>
              </FormControl>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadMissions}
              >
                Refresh
              </Button>
            </Box>
            
            {loading.missions ? (
              <Box display="flex" justifyContent="center" my={4}>
                <CircularProgress />
              </Box>
            ) : missions.length > 0 ? (
              <>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>ID</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Priority</TableCell>
                        <TableCell>Target Layers</TableCell>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {missions.map((mission) => (
                        <TableRow key={mission.mission_id}>
                          <TableCell>{mission.mission_id}</TableCell>
                          <TableCell>{mission.type}</TableCell>
                          <TableCell>
                            <Chip 
                              label={mission.status} 
                              sx={{ 
                                backgroundColor: getStatusColor(mission.status),
                                color: 'white'
                              }} 
                            />
                          </TableCell>
                          <TableCell>{mission.priority}</TableCell>
                          <TableCell>
                            {mission.target_layers.length > 2
                              ? `${mission.target_layers.slice(0, 2).join(', ')}...`
                              : mission.target_layers.join(', ')}
                          </TableCell>
                          <TableCell>{new Date(mission.timestamp).toLocaleString()}</TableCell>
                          <TableCell>
                            <IconButton 
                              size="small" 
                              onClick={() => handleMissionDetails(mission.mission_id)}
                              title="View Details"
                            >
                              <InfoIcon />
                            </IconButton>
                            
                            {!['succeeded', 'failed', 'canceled'].includes(mission.status) && (
                              <IconButton 
                                size="small" 
                                onClick={() => handleMissionAction('cancel', mission.mission_id)}
                                title="Cancel Mission"
                                color="error"
                              >
                                <CancelIcon />
                              </IconButton>
                            )}
                            
                            {mission.status === 'executing' && (
                              <IconButton 
                                size="small" 
                                onClick={() => handleMissionAction('pause', mission.mission_id)}
                                title="Pause Mission"
                                color="warning"
                              >
                                <PauseIcon />
                              </IconButton>
                            )}
                            
                            {mission.status === 'paused' && (
                              <IconButton 
                                size="small" 
                                onClick={() => handleMissionAction('resume', mission.mission_id)}
                                title="Resume Mission"
                                color="primary"
                              >
                                <ResumeIcon />
                              </IconButton>
                            )}
                            
                            {['executing', 'succeeded'].includes(mission.status) && (
                              <IconButton 
                                size="small" 
                                onClick={() => handleMissionAction('rollback', mission.mission_id)}
                                title="Rollback Mission"
                                color="secondary"
                              >
                                <RollbackIcon />
                              </IconButton>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                
                {/* Pagination */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                  <Typography variant="body2">
                    Showing {missionOffset + 1}-{Math.min(missionOffset + missionLimit, totalMissions)} of {totalMissions} missions
                  </Typography>
                  <Box>
                    <Button 
                      disabled={missionOffset === 0}
                      onClick={() => {
                        const newOffset = Math.max(0, missionOffset - missionLimit);
                        setMissionOffset(newOffset);
                        setTimeout(() => loadMissions(), 100);
                      }}
                    >
                      Previous
                    </Button>
                    <Button 
                      disabled={missionOffset + missionLimit >= totalMissions}
                      onClick={() => {
                        const newOffset = missionOffset + missionLimit;
                        setMissionOffset(newOffset);
                        setTimeout(() => loadMissions(), 100);
                      }}
                    >
                      Next
                    </Button>
                  </Box>
                </Box>
              </>
            ) : (
              <Typography align="center" sx={{ my: 4 }}>
                No missions found
              </Typography>
            )}
          </Box>
        )}
        
        {/* Layers Tab */}
        {activeTab === 1 && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadLayers}
              >
                Refresh
              </Button>
            </Box>
            
            {loading.layers ? (
              <Box display="flex" justifyContent="center" my={4}>
                <CircularProgress />
              </Box>
            ) : layers.length > 0 ? (
              <Grid container spacing={3}>
                {layers.map((layer) => (
                  <Grid item xs={12} sm={6} md={4} key={layer.id}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" component="div">
                          {layer.name}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                          <Chip 
                            label={layer.status} 
                            size="small"
                            sx={{ 
                              backgroundColor: getStatusColor(layer.status),
                              color: 'white',
                              mr: 1
                            }} 
                          />
                          <Typography variant="body2" color="text.secondary">
                            {layer.capsule_count} capsules
                          </Typography>
                        </Box>
                      </CardContent>
                      <CardActions>
                        <Button size="small">View Details</Button>
                        <Button size="small">View Capsules</Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Typography align="center" sx={{ my: 4 }}>
                No layers found
              </Typography>
            )}
          </Box>
        )}
        
        {/* Capsules Tab */}
        {activeTab === 2 && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadCapsules}
              >
                Refresh
              </Button>
            </Box>
            
            {loading.capsules ? (
              <Box display="flex" justifyContent="center" my={4}>
                <CircularProgress />
              </Box>
            ) : capsules.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Layer</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {capsules.map((capsule) => (
                      <TableRow key={capsule.id}>
                        <TableCell>{capsule.id}</TableCell>
                        <TableCell>{capsule.name}</TableCell>
                        <TableCell>{capsule.type}</TableCell>
                        <TableCell>{capsule.layer}</TableCell>
                        <TableCell>
                          <Chip 
                            label={capsule.status} 
                            sx={{ 
                              backgroundColor: getStatusColor(capsule.status),
                              color: 'white'
                            }} 
                          />
                        </TableCell>
                        <TableCell>
                          <IconButton size="small" title="View Details">
                            <InfoIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography align="center" sx={{ my: 4 }}>
                No capsules found
              </Typography>
            )}
          </Box>
        )}
        
        {/* Settings Tab */}
        {activeTab === 3 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Dashboard Settings
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Auto-Refresh Settings
                  </Typography>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Enable auto-refresh"
                  />
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Refresh interval (seconds)
                    </Typography>
                    <TextField
                      type="number"
                      defaultValue={30}
                      InputProps={{ inputProps: { min: 5, max: 300 } }}
                      size="small"
                    />
                  </Box>
                </Paper>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Display Settings
                  </Typography>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Show status cards"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Show mission details"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Enable dark mode"
                  />
                </Paper>
              </Grid>
              
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Engine Settings
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Worker Count
                    </Typography>
                    <TextField
                      type="number"
                      defaultValue={5}
                      InputProps={{ inputProps: { min: 1, max: 20 } }}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button variant="contained" color="primary">
                      Save Settings
                    </Button>
                    <Button variant="outlined" color="secondary">
                      Reset to Defaults
                    </Button>
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>
      
      {/* Create Mission Dialog */}
      <CreateMissionDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSubmit={handleCreateMission}
      />
      
      {/* Mission Details Dialog */}
      <MissionDetailsDialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        missionId={selectedMissionId}
      />
      
      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleNotificationClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleNotificationClose}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default MissionControlDashboard;
