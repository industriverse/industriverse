"""
Mission Visualization React component for the Deployment Operations Layer.

This React component provides a visualization of deployment missions,
including mission status, timeline, and execution details.
"""

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Button, 
  Tabs, 
  Tab, 
  CircularProgress,
  Chip,
  Divider,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  CardHeader,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
  Alert,
  AlertTitle,
  LinearProgress
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Pause as PauseIcon,
  PlayCircleOutline as ResumeIcon,
  Undo as RollbackIcon,
  Visibility as VisibilityIcon,
  Timeline as TimelineIcon,
  Storage as StorageIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  CloudUpload as CloudUploadIcon,
  CloudDownload as CloudDownloadIcon,
  Security as SecurityIcon,
  Code as CodeIcon,
  BugReport as BugReportIcon,
  Layers as LayersIcon,
  Dns as DnsIcon,
  Api as ApiIcon,
  Devices as DevicesIcon,
  Assessment as AssessmentIcon,
  Healing as HealingIcon,
  Sync as SyncIcon,
  Bolt as BoltIcon,
  Eco as EcoIcon,
  Fingerprint as FingerprintIcon,
  Explore as ExploreIcon,
  Backup as BackupIcon,
  Tune as TuneIcon,
  Equalizer as EqualizerIcon,
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon,
  Language as LanguageIcon,
  Public as PublicIcon,
  Apartment as ApartmentIcon,
  Biotech as BiotechIcon,
  Science as ScienceIcon,
  Psychology as PsychologyIcon,
  SmartToy as SmartToyIcon,
  Hub as HubIcon,
  Sensors as SensorsIcon,
  DataObject as DataObjectIcon,
  DataArray as DataArrayIcon,
  DataUsage as DataUsageIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  DonutLarge as DonutLargeIcon,
  BubbleChart as BubbleChartIcon,
  ScatterPlot as ScatterPlotIcon,
  TableChart as TableChartIcon,
  ViewQuilt as ViewQuiltIcon,
  ViewModule as ViewModuleIcon,
  ViewCompact as ViewCompactIcon,
  ViewStream as ViewStreamIcon,
  ViewDay as ViewDayIcon,
  ViewWeek as ViewWeekIcon,
  ViewAgenda as ViewAgendaIcon,
  ViewList as ViewListIcon,
  ViewHeadline as ViewHeadlineIcon,
  ViewColumn as ViewColumnIcon,
  ViewComfy as ViewComfyIcon,
  ViewCarousel as ViewCarouselIcon,
  ViewArray as ViewArrayIcon,
  ViewSidebar as ViewSidebarIcon,
  ViewTimeline as ViewTimelineIcon,
  ViewKanban as ViewKanbanIcon,
  ViewInAr as ViewInArIcon,
  ViewCompactAlt as ViewCompactAltIcon,
  ViewCozy as ViewCozyIcon,
  ViewQuilt as ViewQuiltIcon,
  ViewSidebar as ViewSidebarIcon,
  ViewTimeline as ViewTimelineIcon,
  ViewKanban as ViewKanbanIcon,
  ViewInAr as ViewInArIcon,
  ViewCompactAlt as ViewCompactAltIcon,
  ViewCozy as ViewCozyIcon,
} from '@mui/icons-material';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  Legend, 
  ResponsiveContainer,
  Sankey,
  Scatter,
  ScatterChart,
  ZAxis,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { styled } from '@mui/material/styles';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap, 
  Handle, 
  Position,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';

// Styled components
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

const StatusChip = styled(Chip)(({ theme, status }) => {
  const statusColors = {
    active: theme.palette.success.main,
    inactive: theme.palette.error.main,
    pending: theme.palette.warning.main,
    executing: theme.palette.info.main,
    succeeded: theme.palette.success.main,
    failed: theme.palette.error.main,
    paused: theme.palette.warning.main,
    canceled: theme.palette.error.main,
    planning: theme.palette.info.main,
    simulating: theme.palette.info.main,
    rolling_back: theme.palette.warning.main,
    rolled_back: theme.palette.error.main,
  };

  return {
    backgroundColor: statusColors[status] || theme.palette.grey[500],
    color: theme.palette.getContrastText(statusColors[status] || theme.palette.grey[500]),
  };
});

// Custom node components for ReactFlow
const CapsuleNode = ({ data }) => {
  return (
    <div style={{ 
      padding: '10px', 
      borderRadius: '5px', 
      background: '#fff', 
      border: '1px solid #ddd',
      width: 180,
      boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
    }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        marginBottom: '8px',
        borderBottom: '1px solid #eee',
        paddingBottom: '8px'
      }}>
        <div style={{ 
          width: 30, 
          height: 30, 
          borderRadius: '50%', 
          background: data.color || '#1976d2',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginRight: '8px'
        }}>
          {data.icon}
        </div>
        <div>
          <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{data.label}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>{data.type}</div>
        </div>
      </div>
      <div style={{ fontSize: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span>Status:</span>
          <span style={{ 
            padding: '2px 6px', 
            borderRadius: '10px', 
            background: data.status === 'active' ? '#4caf50' : '#f44336',
            color: 'white',
            fontSize: '10px'
          }}>
            {data.status}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span>CPU:</span>
          <span>{data.metrics?.cpu || 'N/A'}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Memory:</span>
          <span>{data.metrics?.memory || 'N/A'}</span>
        </div>
      </div>
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  );
};

const LayerNode = ({ data }) => {
  return (
    <div style={{ 
      padding: '10px', 
      borderRadius: '5px', 
      background: data.color || '#e3f2fd', 
      border: '1px solid #90caf9',
      width: 220,
      boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
    }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        marginBottom: '8px',
        borderBottom: '1px solid #bbdefb',
        paddingBottom: '8px'
      }}>
        <div style={{ 
          width: 36, 
          height: 36, 
          borderRadius: '50%', 
          background: '#1976d2',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginRight: '8px',
          color: 'white'
        }}>
          {data.icon}
        </div>
        <div>
          <div style={{ fontWeight: 'bold', fontSize: '16px' }}>{data.label}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>{data.capsuleCount} capsules</div>
        </div>
      </div>
      <div style={{ fontSize: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span>Status:</span>
          <span style={{ 
            padding: '2px 6px', 
            borderRadius: '10px', 
            background: data.status === 'active' ? '#4caf50' : '#f44336',
            color: 'white',
            fontSize: '10px'
          }}>
            {data.status}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span>CPU:</span>
          <span>{data.metrics?.cpu || 'N/A'}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Memory:</span>
          <span>{data.metrics?.memory || 'N/A'}</span>
        </div>
      </div>
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  );
};

// Mock data for demonstration
const mockMission = {
  id: 'm-001',
  type: 'deploy',
  status: 'succeeded',
  priority: 1,
  timestamp: '2025-05-24T10:00:00Z',
  engine_id: 'engine-001',
  target_layers: ['data-layer', 'core-ai-layer'],
  description: 'Deploy data and core AI layer capsules to production',
  planning_started_at: '2025-05-24T10:00:05Z',
  planning_completed_at: '2025-05-24T10:00:15Z',
  simulation_started_at: '2025-05-24T10:00:20Z',
  simulation_completed_at: '2025-05-24T10:00:30Z',
  execution_started_at: '2025-05-24T10:00:35Z',
  execution_completed_at: '2025-05-24T10:01:00Z',
  succeeded_at: '2025-05-24T10:01:05Z',
  plan_summary: 'Deploy data layer capsules to production environment',
  simulation_summary: 'Simulation successful with no issues detected',
  execution_summary: 'Deployment completed successfully',
  timeline: [
    {
      timestamp: '2025-05-24T10:00:00Z',
      event: 'Mission created',
      details: 'Mission created by admin user',
      status: 'info'
    },
    {
      timestamp: '2025-05-24T10:00:05Z',
      event: 'Planning started',
      details: 'Mission planning phase initiated',
      status: 'info'
    },
    {
      timestamp: '2025-05-24T10:00:15Z',
      event: 'Planning completed',
      details: 'Mission plan generated successfully',
      status: 'success'
    },
    {
      timestamp: '2025-05-24T10:00:20Z',
      event: 'Simulation started',
      details: 'Pre-deployment simulation initiated',
      status: 'info'
    },
    {
      timestamp: '2025-05-24T10:00:30Z',
      event: 'Simulation completed',
      details: 'Simulation completed successfully with no issues detected',
      status: 'success'
    },
    {
      timestamp: '2025-05-24T10:00:35Z',
      event: 'Execution started',
      details: 'Deployment execution initiated',
      status: 'info'
    },
    {
      timestamp: '2025-05-24T10:00:40Z',
      event: 'Data layer deployment started',
      details: 'Deploying data-ingestion and data-processing capsules',
      status: 'info'
    },
    {
      timestamp: '2025-05-24T10:00:50Z',
      event: 'Data layer deployment completed',
      details: 'Data layer capsules deployed successfully',
      status: 'success'
    },
    {
      timestamp: '2025-05-24T10:00:55Z',
      event: 'Core AI layer deployment started',
      details: 'Deploying model-serving capsule',
      status: 'info'
    },
    {
      timestamp: '2025-05-24T10:01:00Z',
      event: 'Core AI layer deployment completed',
      details: 'Core AI layer capsules deployed successfully',
      status: 'success'
    },
    {
      timestamp: '2025-05-24T10:01:05Z',
      event: 'Mission succeeded',
      details: 'All deployment operations completed successfully',
      status: 'success'
    }
  ],
  resources: {
    cpu_usage: [
      { timestamp: '2025-05-24T10:00:35Z', value: 10 },
      { timestamp: '2025-05-24T10:00:40Z', value: 30 },
      { timestamp: '2025-05-24T10:00:45Z', value: 45 },
      { timestamp: '2025-05-24T10:00:50Z', value: 60 },
      { timestamp: '2025-05-24T10:00:55Z', value: 40 },
      { timestamp: '2025-05-24T10:01:00Z', value: 25 },
      { timestamp: '2025-05-24T10:01:05Z', value: 15 }
    ],
    memory_usage: [
      { timestamp: '2025-05-24T10:00:35Z', value: 15 },
      { timestamp: '2025-05-24T10:00:40Z', value: 25 },
      { timestamp: '2025-05-24T10:00:45Z', value: 40 },
      { timestamp: '2025-05-24T10:00:50Z', value: 55 },
      { timestamp: '2025-05-24T10:00:55Z', value: 45 },
      { timestamp: '2025-05-24T10:01:00Z', value: 30 },
      { timestamp: '2025-05-24T10:01:05Z', value: 20 }
    ],
    network_usage: [
      { timestamp: '2025-05-24T10:00:35Z', value: 5 },
      { timestamp: '2025-05-24T10:00:40Z', value: 20 },
      { timestamp: '2025-05-24T10:00:45Z', value: 35 },
      { timestamp: '2025-05-24T10:00:50Z', value: 25 },
      { timestamp: '2025-05-24T10:00:55Z', value: 30 },
      { timestamp: '2025-05-24T10:01:00Z', value: 15 },
      { timestamp: '2025-05-24T10:01:05Z', value: 5 }
    ]
  },
  capsules: [
    {
      id: 'c-001',
      name: 'data-ingestion-prod',
      type: 'data-ingestion',
      layer: 'data-layer',
      status: 'active',
      metrics: {
        cpu: '10%',
        memory: '256MB'
      }
    },
    {
      id: 'c-002',
      name: 'data-processing-prod',
      type: 'data-processing',
      layer: 'data-layer',
      status: 'active',
      metrics: {
        cpu: '25%',
        memory: '512MB'
      }
    },
    {
      id: 'c-003',
      name: 'model-serving-prod',
      type: 'model-serving',
      layer: 'core-ai-layer',
      status: 'active',
      metrics: {
        cpu: '60%',
        memory: '4GB'
      }
    }
  ],
  layers: [
    {
      id: 'data-layer',
      name: 'Data Layer',
      status: 'active',
      capsuleCount: 2,
      metrics: {
        cpu: '35%',
        memory: '768MB'
      }
    },
    {
      id: 'core-ai-layer',
      name: 'Core AI Layer',
      status: 'active',
      capsuleCount: 1,
      metrics: {
        cpu: '60%',
        memory: '4GB'
      }
    }
  ],
  validation_results: {
    resource_validation: [
      {
        name: 'CPU Resources',
        status: 'passed',
        message: 'Sufficient CPU resources available'
      },
      {
        name: 'Memory Resources',
        status: 'passed',
        message: 'Sufficient memory resources available'
      },
      {
        name: 'Storage Resources',
        status: 'passed',
        message: 'Sufficient storage resources available'
      }
    ],
    dependency_validation: [
      {
        name: 'Layer Dependencies',
        status: 'passed',
        message: 'All layer dependencies are satisfied'
      },
      {
        name: 'Version Compatibility',
        status: 'passed',
        message: 'All version requirements are compatible'
      }
    ],
    security_validation: [
      {
        name: 'Security Policies',
        status: 'passed',
        message: 'All security policies are satisfied'
      },
      {
        name: 'Crypto Zone Compliance',
        status: 'passed',
        message: 'Deployment complies with crypto zone requirements'
      }
    ]
  }
};

// Main component
const MissionVisualization = ({ missionId }) => {
  // State
  const [loading, setLoading] = useState(false);
  const [mission, setMission] = useState(mockMission);
  const [tabValue, setTabValue] = useState(0);
  const [flowNodes, setFlowNodes] = useState([]);
  const [flowEdges, setFlowEdges] = useState([]);

  // Effects
  useEffect(() => {
    // Fetch mission data
    fetchMissionData();
    
    // Generate flow data
    generateFlowData();
  }, [missionId]);

  // Fetch mission data
  const fetchMissionData = () => {
    setLoading(true);
    
    // In a real implementation, this would fetch data from the API
    // For now, we'll use mock data and simulate a delay
    setTimeout(() => {
      setMission(mockMission);
      setLoading(false);
    }, 500);
  };

  // Generate flow data for ReactFlow
  const generateFlowData = () => {
    if (!mission) return;
    
    const nodes = [];
    const edges = [];
    
    // Add layer nodes
    mission.layers.forEach((layer, index) => {
      const layerIcons = {
        'data-layer': <StorageIcon fontSize="small" />,
        'core-ai-layer': <PsychologyIcon fontSize="small" />,
        'generative-layer': <BiotechIcon fontSize="small" />,
        'application-layer': <ViewModuleIcon fontSize="small" />,
        'protocol-layer': <ApiIcon fontSize="small" />,
        'workflow-layer': <TimelineIcon fontSize="small" />,
        'ui-ux-layer': <ViewQuiltIcon fontSize="small" />,
        'security-compliance-layer': <SecurityIcon fontSize="small" />,
        'deployment-ops-layer': <CloudUploadIcon fontSize="small" />,
        'native-app-layer': <DevicesIcon fontSize="small" />,
      };
      
      const layerColors = {
        'data-layer': '#e3f2fd',
        'core-ai-layer': '#e8f5e9',
        'generative-layer': '#f3e5f5',
        'application-layer': '#e8eaf6',
        'protocol-layer': '#fff3e0',
        'workflow-layer': '#e0f7fa',
        'ui-ux-layer': '#fce4ec',
        'security-compliance-layer': '#f1f8e9',
        'deployment-ops-layer': '#fffde7',
        'native-app-layer': '#e0f2f1',
      };
      
      nodes.push({
        id: layer.id,
        type: 'layerNode',
        position: { x: 250, y: 100 + index * 300 },
        data: {
          label: layer.name,
          capsuleCount: layer.capsuleCount,
          status: layer.status,
          metrics: layer.metrics,
          icon: layerIcons[layer.id] || <LayersIcon fontSize="small" />,
          color: layerColors[layer.id]
        }
      });
    });
    
    // Add capsule nodes
    mission.capsules.forEach((capsule, index) => {
      const capsuleIcons = {
        'data-ingestion': <DataObjectIcon fontSize="small" style={{ color: 'white' }} />,
        'data-processing': <DataArrayIcon fontSize="small" style={{ color: 'white' }} />,
        'model-serving': <PsychologyIcon fontSize="small" style={{ color: 'white' }} />,
        'inference-api': <ApiIcon fontSize="small" style={{ color: 'white' }} />,
      };
      
      const capsuleColors = {
        'data-ingestion': '#1976d2',
        'data-processing': '#2196f3',
        'model-serving': '#4caf50',
        'inference-api': '#8bc34a',
      };
      
      const layerIndex = mission.layers.findIndex(l => l.id === capsule.layer);
      
      nodes.push({
        id: capsule.id,
        type: 'capsuleNode',
        position: { x: 600, y: 100 + layerIndex * 300 + (index % 2) * 150 },
        data: {
          label: capsule.name,
          type: capsule.type,
          status: capsule.status,
          metrics: capsule.metrics,
          icon: capsuleIcons[capsule.type] || <ViewModuleIcon fontSize="small" style={{ color: 'white' }} />,
          color: capsuleColors[capsule.type]
        }
      });
      
      // Add edge from layer to capsule
      edges.push({
        id: `${capsule.layer}-${capsule.id}`,
        source: capsule.layer,
        target: capsule.id,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#555' },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: '#555',
        },
      });
    });
    
    // Add dependencies between capsules if they exist
    if (mission.capsules.length > 1) {
      edges.push({
        id: `${mission.capsules[0].id}-${mission.capsules[1].id}`,
        source: mission.capsules[0].id,
        target: mission.capsules[1].id,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#555' },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: '#555',
        },
      });
    }
    
    setFlowNodes(nodes);
    setFlowEdges(edges);
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };

  // Calculate duration between timestamps
  const calculateDuration = (start, end) => {
    if (!start || !end) return 'N/A';
    
    const startTime = new Date(start).getTime();
    const endTime = new Date(end).getTime();
    const durationMs = endTime - startTime;
    
    if (durationMs < 1000) {
      return `${durationMs}ms`;
    } else if (durationMs < 60000) {
      return `${Math.floor(durationMs / 1000)}s`;
    } else {
      const minutes = Math.floor(durationMs / 60000);
      const seconds = Math.floor((durationMs % 60000) / 1000);
      return `${minutes}m ${seconds}s`;
    }
  };

  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckIcon fontSize="small" style={{ color: '#4caf50' }} />;
      case 'error':
        return <CloseIcon fontSize="small" style={{ color: '#f44336' }} />;
      case 'warning':
        return <WarningIcon fontSize="small" style={{ color: '#ff9800' }} />;
      case 'info':
      default:
        return <InfoIcon fontSize="small" style={{ color: '#2196f3' }} />;
    }
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return '#4caf50';
      case 'error':
        return '#f44336';
      case 'warning':
        return '#ff9800';
      case 'info':
      default:
        return '#2196f3';
    }
  };

  // Render overview tab
  const renderOverviewTab = () => (
    <Grid container spacing={3}>
      {/* Mission Details */}
      <Grid item xs={12} md={6}>
        <StyledPaper>
          <Typography variant="h6" mb={2}>Mission Details</Typography>
          <Grid container spacing={2}>
            <Grid item xs={4}>
              <Typography variant="body2" color="textSecondary">ID</Typography>
              <Typography variant="body1">{mission.id}</Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="body2" color="textSecondary">Type</Typography>
              <Typography variant="body1">{mission.type}</Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="body2" color="textSecondary">Status</Typography>
              <StatusChip label={mission.status} status={mission.status} />
            </Grid>
            <Grid item xs={4}>
              <Typography variant="body2" color="textSecondary">Priority</Typography>
              <Typography variant="body1">{mission.priority}</Typography>
            </Grid>
            <Grid item xs={8}>
              <Typography variant="body2" color="textSecondary">Timestamp</Typography>
              <Typography variant="body1">{formatTimestamp(mission.timestamp)}</Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="body2" color="textSecondary">Description</Typography>
              <Typography variant="body1">{mission.description}</Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="body2" color="textSecondary">Target Layers</Typography>
              <Box mt={1}>
                {mission.target_layers.map((layer) => (
                  <Chip 
                    key={layer} 
                    label={layer} 
                    size="small" 
                    style={{ marginRight: 8, marginBottom: 8 }} 
                  />
                ))}
              </Box>
            </Grid>
          </Grid>
        </StyledPaper>
      </Grid>

      {/* Mission Timeline */}
      <Grid item xs={12} md={6}>
        <StyledPaper>
          <Typography variant="h6" mb={2}>Mission Timeline</Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">Planning</Typography>
              <Typography variant="body1">
                {calculateDuration(mission.planning_started_at, mission.planning_completed_at)}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">Simulation</Typography>
              <Typography variant="body1">
                {calculateDuration(mission.simulation_started_at, mission.simulation_completed_at)}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">Execution</Typography>
              <Typography variant="body1">
                {calculateDuration(mission.execution_started_at, mission.execution_completed_at)}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">Total</Typography>
              <Typography variant="body1">
                {calculateDuration(mission.planning_started_at, mission.succeeded_at || mission.failed_at || mission.execution_completed_at)}
              </Typography>
            </Grid>
          </Grid>
          <Divider sx={{ my: 2 }} />
          <Box>
            <Stepper orientation="vertical" activeStep={
              mission.status === 'succeeded' ? 3 : 
              mission.status === 'executing' ? 2 :
              mission.status === 'simulating' ? 1 :
              mission.status === 'planning' ? 0 : 3
            }>
              <Step completed={Boolean(mission.planning_completed_at)}>
                <StepLabel>Planning</StepLabel>
                <StepContent>
                  <Typography variant="body2">
                    {mission.plan_summary || 'Mission planning phase'}
                  </Typography>
                  <Box mt={1}>
                    <Typography variant="caption">
                      Started: {formatTimestamp(mission.planning_started_at)}
                    </Typography>
                  </Box>
                  {mission.planning_completed_at && (
                    <Box mt={1}>
                      <Typography variant="caption">
                        Completed: {formatTimestamp(mission.planning_completed_at)}
                      </Typography>
                    </Box>
                  )}
                </StepContent>
              </Step>
              <Step completed={Boolean(mission.simulation_completed_at)}>
                <StepLabel>Simulation</StepLabel>
                <StepContent>
                  <Typography variant="body2">
                    {mission.simulation_summary || 'Pre-deployment simulation phase'}
                  </Typography>
                  <Box mt={1}>
                    <Typography variant="caption">
                      Started: {formatTimestamp(mission.simulation_started_at)}
                    </Typography>
                  </Box>
                  {mission.simulation_completed_at && (
                    <Box mt={1}>
                      <Typography variant="caption">
                        Completed: {formatTimestamp(mission.simulation_completed_at)}
                      </Typography>
                    </Box>
                  )}
                </StepContent>
              </Step>
              <Step completed={Boolean(mission.execution_completed_at)}>
                <StepLabel>Execution</StepLabel>
                <StepContent>
                  <Typography variant="body2">
                    {mission.execution_summary || 'Deployment execution phase'}
                  </Typography>
                  <Box mt={1}>
                    <Typography variant="caption">
                      Started: {formatTimestamp(mission.execution_started_at)}
                    </Typography>
                  </Box>
                  {mission.execution_completed_at && (
                    <Box mt={1}>
                      <Typography variant="caption">
                        Completed: {formatTimestamp(mission.execution_completed_at)}
                      </Typography>
                    </Box>
                  )}
                </StepContent>
              </Step>
              <Step completed={Boolean(mission.succeeded_at)}>
                <StepLabel>Completion</StepLabel>
                <StepContent>
                  <Typography variant="body2">
                    {mission.status === 'succeeded' 
                      ? 'Mission completed successfully' 
                      : mission.status === 'failed'
                        ? 'Mission failed'
                        : 'Awaiting completion'}
                  </Typography>
                  {mission.succeeded_at && (
                    <Box mt={1}>
                      <Typography variant="caption">
                        Succeeded: {formatTimestamp(mission.succeeded_at)}
                      </Typography>
                    </Box>
                  )}
                  {mission.failed_at && (
                    <Box mt={1}>
                      <Typography variant="caption">
                        Failed: {formatTimestamp(mission.failed_at)}
                      </Typography>
                    </Box>
                  )}
                </StepContent>
              </Step>
            </Stepper>
          </Box>
        </StyledPaper>
      </Grid>

      {/* Resource Usage */}
      <Grid item xs={12}>
        <StyledPaper>
          <Typography variant="h6" mb={2}>Resource Usage</Typography>
          <Box height={300}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={mission.resources.cpu_usage.map((cpu, index) => ({
                  timestamp: cpu.timestamp,
                  cpu: cpu.value,
                  memory: mission.resources.memory_usage[index].value,
                  network: mission.resources.network_usage[index].value
                }))}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()} 
                />
                <YAxis label={{ value: 'Usage (%)', angle: -90, position: 'insideLeft' }} />
                <RechartsTooltip 
                  formatter={(value, name) => [`${value}%`, name]}
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                />
                <Legend />
                <Line type="monotone" dataKey="cpu" name="CPU" stroke="#8884d8" activeDot={{ r: 8 }} />
                <Line type="monotone" dataKey="memory" name="Memory" stroke="#82ca9d" activeDot={{ r: 8 }} />
                <Line type="monotone" dataKey="network" name="Network" stroke="#ffc658" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </StyledPaper>
      </Grid>
    </Grid>
  );

  // Render timeline tab
  const renderTimelineTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <StyledPaper>
          <Typography variant="h6" mb={2}>Detailed Timeline</Typography>
          <Timeline position="alternate">
            {mission.timeline.map((event, index) => (
              <TimelineItem key={index}>
                <TimelineOppositeContent color="text.secondary">
                  {formatTimestamp(event.timestamp)}
                </TimelineOppositeContent>
                <TimelineSeparator>
                  <TimelineDot style={{ backgroundColor: getStatusColor(event.status) }}>
                    {getStatusIcon(event.status)}
                  </TimelineDot>
                  {index < mission.timeline.length - 1 && <TimelineConnector />}
                </TimelineSeparator>
                <TimelineContent>
                  <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
                    <Typography variant="h6" component="h3">
                      {event.event}
                    </Typography>
                    <Typography>{event.details}</Typography>
                  </Paper>
                </TimelineContent>
              </TimelineItem>
            ))}
          </Timeline>
        </StyledPaper>
      </Grid>
    </Grid>
  );

  // Render topology tab
  const renderTopologyTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <StyledPaper>
          <Typography variant="h6" mb={2}>Deployment Topology</Typography>
          <Box height={600}>
            <ReactFlow
              nodes={flowNodes}
              edges={flowEdges}
              nodeTypes={{ capsuleNode: CapsuleNode, layerNode: LayerNode }}
              fitView
            >
              <Background />
              <Controls />
              <MiniMap />
            </ReactFlow>
          </Box>
        </StyledPaper>
      </Grid>
    </Grid>
  );

  // Render validation tab
  const renderValidationTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <StyledPaper>
          <Typography variant="h6" mb={2}>Resource Validation</Typography>
          {mission.validation_results.resource_validation.map((validation, index) => (
            <Alert 
              key={index} 
              severity={validation.status === 'passed' ? 'success' : 'error'}
              sx={{ mb: 2 }}
            >
              <AlertTitle>{validation.name}</AlertTitle>
              {validation.message}
            </Alert>
          ))}
        </StyledPaper>
      </Grid>
      <Grid item xs={12} md={4}>
        <StyledPaper>
          <Typography variant="h6" mb={2}>Dependency Validation</Typography>
          {mission.validation_results.dependency_validation.map((validation, index) => (
            <Alert 
              key={index} 
              severity={validation.status === 'passed' ? 'success' : 'error'}
              sx={{ mb: 2 }}
            >
              <AlertTitle>{validation.name}</AlertTitle>
              {validation.message}
            </Alert>
          ))}
        </StyledPaper>
      </Grid>
      <Grid item xs={12} md={4}>
        <StyledPaper>
          <Typography variant="h6" mb={2}>Security Validation</Typography>
          {mission.validation_results.security_validation.map((validation, index) => (
            <Alert 
              key={index} 
              severity={validation.status === 'passed' ? 'success' : 'error'}
              sx={{ mb: 2 }}
            >
              <AlertTitle>{validation.name}</AlertTitle>
              {validation.message}
            </Alert>
          ))}
        </StyledPaper>
      </Grid>
    </Grid>
  );

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          <TimelineIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
          Mission Visualization
        </Typography>
        <Box>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchMissionData}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <StatusChip 
            label={mission.status} 
            status={mission.status} 
            sx={{ ml: 1 }}
          />
        </Box>
      </Box>

      {/* Loading indicator */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="mission visualization tabs">
          <Tab icon={<DashboardIcon />} label="Overview" />
          <Tab icon={<TimelineIcon />} label="Timeline" />
          <Tab icon={<HubIcon />} label="Topology" />
          <Tab icon={<CheckIcon />} label="Validation" />
        </Tabs>
      </Box>

      {/* Tab content */}
      {tabValue === 0 && renderOverviewTab()}
      {tabValue === 1 && renderTimelineTab()}
      {tabValue === 2 && renderTopologyTab()}
      {tabValue === 3 && renderValidationTab()}
    </Box>
  );
};

export default MissionVisualization;
