import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Button, Slider, IconButton, Tooltip } from '@mui/material';
import { styled } from '@mui/material/styles';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import SkipNextIcon from '@mui/icons-material/SkipNext';
import SkipPreviousIcon from '@mui/icons-material/SkipPrevious';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import { useData } from '../../contexts/DataContext';
import { useUIState } from '../../contexts/UIStateContext';

/**
 * Simulation Snapshot Spinner component that allows running "what if" scenarios
 * with policy shifts or workflow variants.
 * 
 * This implements the Human-in-the-Loop Flow design principle by providing
 * interactive simulation capabilities for decision support.
 */
const SimulationSnapshotSpinner = () => {
  const { getData, isLoading } = useData();
  const { openModal } = useUIState();
  const [selectedSimulation, setSelectedSimulation] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  
  // In a real implementation, this would fetch data from the backend
  // For now, we'll use placeholder data
  const simulations = [
    {
      id: 'sim-001',
      name: 'Production Line Optimization',
      description: 'Simulates different configurations of the production line to optimize throughput',
      creator: 'Process Engineer',
      timestamp: '2025-05-25T08:30:00Z',
      status: 'ready',
      steps: 12,
      variants: 3,
    },
    {
      id: 'sim-002',
      name: 'Resource Allocation Scenario',
      description: 'Tests different resource allocation strategies under varying demand conditions',
      creator: 'Resource Manager',
      timestamp: '2025-05-25T07:45:12Z',
      status: 'ready',
      steps: 8,
      variants: 4,
    },
    {
      id: 'sim-003',
      name: 'Supply Chain Disruption Response',
      description: 'Evaluates response strategies to potential supply chain disruptions',
      creator: 'Supply Chain Analyst',
      timestamp: '2025-05-24T15:20:45Z',
      status: 'ready',
      steps: 15,
      variants: 5,
    },
  ];

  // Simulation step data (would be fetched from backend in real implementation)
  const simulationSteps = {
    'sim-001': Array.from({ length: 12 }, (_, i) => ({
      id: `step-${i+1}`,
      name: `Step ${i+1}`,
      description: `Simulation step ${i+1} description`,
      metrics: {
        throughput: 100 + (i * 5) + (Math.random() * 10 - 5),
        efficiency: 85 + (i * 1.2) + (Math.random() * 5 - 2.5),
        cost: 10000 - (i * 200) + (Math.random() * 300 - 150),
      },
      variants: [
        { id: 'var-1', name: 'Baseline', color: '#1976d2' },
        { id: 'var-2', name: 'Optimized', color: '#4caf50' },
        { id: 'var-3', name: 'Cost-saving', color: '#ff9800' },
      ]
    })),
    'sim-002': Array.from({ length: 8 }, (_, i) => ({
      id: `step-${i+1}`,
      name: `Step ${i+1}`,
      description: `Simulation step ${i+1} description`,
      metrics: {
        utilization: 75 + (i * 2) + (Math.random() * 5 - 2.5),
        waitTime: 25 - (i * 2) + (Math.random() * 4 - 2),
        throughput: 90 + (i * 3) + (Math.random() * 6 - 3),
      },
      variants: [
        { id: 'var-1', name: 'Current', color: '#1976d2' },
        { id: 'var-2', name: 'Balanced', color: '#4caf50' },
        { id: 'var-3', name: 'Aggressive', color: '#f44336' },
        { id: 'var-4', name: 'Conservative', color: '#ff9800' },
      ]
    })),
    'sim-003': Array.from({ length: 15 }, (_, i) => ({
      id: `step-${i+1}`,
      name: `Step ${i+1}`,
      description: `Simulation step ${i+1} description`,
      metrics: {
        deliveryTime: 48 - (i * 1.5) + (Math.random() * 3 - 1.5),
        stockLevels: 65 + (i * 1) + (Math.random() * 8 - 4),
        cost: 15000 + (i * 100) + (Math.random() * 500 - 250),
      },
      variants: [
        { id: 'var-1', name: 'No Disruption', color: '#4caf50' },
        { id: 'var-2', name: 'Minor Disruption', color: '#ff9800' },
        { id: 'var-3', name: 'Major Disruption', color: '#f44336' },
        { id: 'var-4', name: 'Rapid Response', color: '#2196f3' },
        { id: 'var-5', name: 'Delayed Response', color: '#9c27b0' },
      ]
    })),
  };

  // Handle simulation selection
  const handleSimulationSelect = (simulationId) => {
    const simulation = simulations.find(s => s.id === simulationId);
    setSelectedSimulation(simulation);
    setCurrentStep(0);
    setIsPlaying(false);
  };

  // Handle play/pause
  const togglePlayback = () => {
    setIsPlaying(!isPlaying);
  };

  // Handle step change
  const handleStepChange = (event, newValue) => {
    setCurrentStep(newValue);
  };

  // Handle next step
  const handleNextStep = () => {
    if (!selectedSimulation) return;
    
    const steps = simulationSteps[selectedSimulation.id];
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  // Handle previous step
  const handlePrevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // Handle reset
  const handleReset = () => {
    setCurrentStep(0);
    setIsPlaying(false);
  };

  // Handle playback speed change
  const handleSpeedChange = (event, newValue) => {
    setPlaybackSpeed(newValue);
  };

  // Auto-advance steps when playing
  useEffect(() => {
    if (!isPlaying || !selectedSimulation) return;
    
    const steps = simulationSteps[selectedSimulation.id];
    const interval = setInterval(() => {
      setCurrentStep(prevStep => {
        if (prevStep < steps.length - 1) {
          return prevStep + 1;
        } else {
          setIsPlaying(false);
          return prevStep;
        }
      });
    }, 2000 / playbackSpeed);
    
    return () => clearInterval(interval);
  }, [isPlaying, selectedSimulation, playbackSpeed]);

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
    
    return date.toLocaleDateString();
  };

  // Render current step visualization
  const renderStepVisualization = () => {
    if (!selectedSimulation) return null;
    
    const steps = simulationSteps[selectedSimulation.id];
    const step = steps[currentStep];
    
    return (
      <Box sx={{ mt: 3 }}>
        <Paper elevation={0} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom>
            {step.name}
          </Typography>
          <Typography variant="body2" color="textSecondary" paragraph>
            {step.description}
          </Typography>
          
          <Grid container spacing={3} sx={{ mt: 1 }}>
            {Object.entries(step.metrics).map(([key, value]) => (
              <Grid item xs={12} sm={4} key={key}>
                <Card elevation={0} sx={{ bgcolor: 'background.default', borderRadius: 2 }}>
                  <CardContent>
                    <Typography variant="overline" color="textSecondary">
                      {key.charAt(0).toUpperCase() + key.slice(1)}
                    </Typography>
                    <Typography variant="h5" component="div">
                      {typeof value === 'number' ? value.toFixed(1) : value}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          <Box sx={{ mt: 4 }}>
            <Typography variant="subtitle2" gutterBottom>
              Variant Comparison
            </Typography>
            <Box sx={{ height: 200, bgcolor: 'background.default', borderRadius: 2, p: 2 }}>
              <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center', pt: 4 }}>
                Variant comparison visualization would be implemented here using D3.js or a similar library.
                This would show metrics for each variant at the current simulation step.
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                {step.variants.map(variant => (
                  <Box 
                    key={variant.id}
                    sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      mx: 1,
                    }}
                  >
                    <Box 
                      sx={{ 
                        width: 12, 
                        height: 12, 
                        borderRadius: '50%', 
                        bgcolor: variant.color,
                        mr: 0.5 
                      }} 
                    />
                    <Typography variant="caption">
                      {variant.name}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          </Box>
        </Paper>
      </Box>
    );
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Simulation Snapshot Spinner
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper elevation={0} sx={{ p: 2, borderRadius: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Available Simulations
            </Typography>
            
            {simulations.map((simulation) => (
              <Card
                key={simulation.id}
                elevation={0}
                sx={{
                  mb: 2,
                  border: 1,
                  borderColor: selectedSimulation?.id === simulation.id ? 'primary.main' : 'divider',
                  borderRadius: 2,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: 'action.hover',
                  },
                }}
                onClick={() => handleSimulationSelect(simulation.id)}
              >
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="subtitle2" fontWeight="medium">
                    {simulation.name}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 0.5 }}>
                    {simulation.description}
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1.5 }}>
                    <Typography variant="caption" color="textSecondary">
                      Created: {formatRelativeTime(simulation.timestamp)}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Steps: {simulation.steps}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Paper elevation={0} sx={{ p: 2, borderRadius: 2 }}>
            {selectedSimulation ? (
              <>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle1">
                    {selectedSimulation.name}
                  </Typography>
                  <Button 
                    size="small" 
                    variant="outlined"
                    onClick={() => openModal('simulationDetail', { simulationId: selectedSimulation.id })}
                  >
                    View Details
                  </Button>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <IconButton onClick={handleReset} size="small">
                    <RestartAltIcon />
                  </IconButton>
                  <IconButton onClick={handlePrevStep} size="small" disabled={currentStep === 0}>
                    <SkipPreviousIcon />
                  </IconButton>
                  <IconButton onClick={togglePlayback} color="primary">
                    {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
                  </IconButton>
                  <IconButton 
                    onClick={handleNextStep} 
                    size="small" 
                    disabled={currentStep === simulationSteps[selectedSimulation.id].length - 1}
                  >
                    <SkipNextIcon />
                  </IconButton>
                  
                  <Box sx={{ width: 200, ml: 2 }}>
                    <Slider
                      value={currentStep}
                      onChange={handleStepChange}
                      min={0}
                      max={simulationSteps[selectedSimulation.id].length - 1}
                      step={1}
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="caption" color="textSecondary" sx={{ ml: 2, minWidth: 60 }}>
                    Step {currentStep + 1}/{simulationSteps[selectedSimulation.id].length}
                  </Typography>
                  
                  <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center' }}>
                    <Typography variant="caption" color="textSecondary" sx={{ mr: 1 }}>
                      Speed:
                    </Typography>
                    <Box sx={{ width: 80 }}>
                      <Slider
                        value={playbackSpeed}
                        onChange={handleSpeedChange}
                        min={0.5}
                        max={3}
                        step={0.5}
                        size="small"
                        marks
                      />
                    </Box>
                    <Typography variant="caption" color="textSecondary" sx={{ ml: 1, minWidth: 20 }}>
                      {playbackSpeed}x
                    </Typography>
                  </Box>
                </Box>
                
                {renderStepVisualization()}
              </>
            ) : (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="body1" color="textSecondary">
                  Select a simulation to begin
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SimulationSnapshotSpinner;
