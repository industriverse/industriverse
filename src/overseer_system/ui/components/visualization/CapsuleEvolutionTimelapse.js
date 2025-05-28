import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Button, Slider, IconButton, Tooltip, Chip } from '@mui/material';
import { styled } from '@mui/material/styles';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import SkipNextIcon from '@mui/icons-material/SkipNext';
import SkipPreviousIcon from '@mui/icons-material/SkipPrevious';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import TimelineIcon from '@mui/icons-material/Timeline';
import { useData } from '../../contexts/DataContext';
import { useUIState } from '../../contexts/UIStateContext';

/**
 * Capsule Evolution Timelapse component that provides a visual replay of a capsule's
 * mutations, trust votes, and upgrades over time.
 * 
 * This implements the Live, Linked Visuals design principle by providing
 * interactive visualization of capsule evolution history.
 */
const CapsuleEvolutionTimelapse = () => {
  const { getData, isLoading } = useData();
  const { openModal } = useUIState();
  const [selectedCapsule, setSelectedCapsule] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentGeneration, setCurrentGeneration] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  
  // In a real implementation, this would fetch data from the backend
  // For now, we'll use placeholder data
  const capsules = [
    {
      id: 'capsule-001',
      name: 'Manufacturing Optimization Capsule',
      description: 'Optimizes manufacturing processes for efficiency and quality',
      creator: 'Capsule Evolution Service',
      initialTimestamp: '2025-04-15T10:30:00Z',
      latestTimestamp: '2025-05-25T08:15:22Z',
      status: 'active',
      generations: 12,
      currentGeneration: 12,
      trustScore: 94,
    },
    {
      id: 'capsule-002',
      name: 'Predictive Maintenance Capsule',
      description: 'Predicts equipment failures and schedules maintenance',
      creator: 'Maintenance Engineer',
      initialTimestamp: '2025-04-20T14:45:12Z',
      latestTimestamp: '2025-05-24T16:30:45Z',
      status: 'active',
      generations: 8,
      currentGeneration: 8,
      trustScore: 92,
    },
    {
      id: 'capsule-003',
      name: 'Supply Chain Optimization Capsule',
      description: 'Optimizes supply chain operations and inventory management',
      creator: 'Supply Chain Manager',
      initialTimestamp: '2025-04-25T09:15:30Z',
      latestTimestamp: '2025-05-23T11:20:15Z',
      status: 'active',
      generations: 6,
      currentGeneration: 6,
      trustScore: 88,
    },
  ];

  // Capsule evolution data (would be fetched from backend in real implementation)
  const capsuleEvolutions = {
    'capsule-001': Array.from({ length: 12 }, (_, i) => ({
      generation: i + 1,
      timestamp: new Date(new Date('2025-04-15T10:30:00Z').getTime() + (i * 3 * 24 * 60 * 60 * 1000)).toISOString(),
      trustScore: 70 + (i * 2) + (Math.random() * 4 - 2),
      mutations: i === 0 ? [] : [
        {
          type: Math.random() > 0.5 ? 'trait' : 'capability',
          name: `${Math.random() > 0.5 ? 'Enhanced' : 'Improved'} ${Math.random() > 0.5 ? 'Efficiency' : 'Accuracy'}`,
          impact: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low',
        }
      ],
      parentCapsules: i === 0 ? [] : i === 1 ? ['Base Capsule'] : ['capsule-001'],
      performanceMetrics: {
        efficiency: 75 + (i * 1.8) + (Math.random() * 5 - 2.5),
        accuracy: 80 + (i * 1.2) + (Math.random() * 4 - 2),
        adaptability: 65 + (i * 2.5) + (Math.random() * 6 - 3),
      }
    })),
    'capsule-002': Array.from({ length: 8 }, (_, i) => ({
      generation: i + 1,
      timestamp: new Date(new Date('2025-04-20T14:45:12Z').getTime() + (i * 4 * 24 * 60 * 60 * 1000)).toISOString(),
      trustScore: 75 + (i * 2.5) + (Math.random() * 4 - 2),
      mutations: i === 0 ? [] : [
        {
          type: Math.random() > 0.5 ? 'trait' : 'capability',
          name: `${Math.random() > 0.5 ? 'Enhanced' : 'Improved'} ${Math.random() > 0.5 ? 'Prediction' : 'Detection'}`,
          impact: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low',
        }
      ],
      parentCapsules: i === 0 ? [] : i === 1 ? ['Base Capsule'] : ['capsule-002'],
      performanceMetrics: {
        prediction: 70 + (i * 2.5) + (Math.random() * 5 - 2.5),
        reliability: 75 + (i * 2) + (Math.random() * 4 - 2),
        efficiency: 80 + (i * 1.5) + (Math.random() * 6 - 3),
      }
    })),
    'capsule-003': Array.from({ length: 6 }, (_, i) => ({
      generation: i + 1,
      timestamp: new Date(new Date('2025-04-25T09:15:30Z').getTime() + (i * 5 * 24 * 60 * 60 * 1000)).toISOString(),
      trustScore: 72 + (i * 3) + (Math.random() * 4 - 2),
      mutations: i === 0 ? [] : [
        {
          type: Math.random() > 0.5 ? 'trait' : 'capability',
          name: `${Math.random() > 0.5 ? 'Enhanced' : 'Improved'} ${Math.random() > 0.5 ? 'Optimization' : 'Forecasting'}`,
          impact: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low',
        }
      ],
      parentCapsules: i === 0 ? [] : i === 1 ? ['Base Capsule'] : ['capsule-003'],
      performanceMetrics: {
        optimization: 65 + (i * 3.5) + (Math.random() * 5 - 2.5),
        forecasting: 70 + (i * 3) + (Math.random() * 4 - 2),
        adaptability: 75 + (i * 2) + (Math.random() * 6 - 3),
      }
    })),
  };

  // Handle capsule selection
  const handleCapsuleSelect = (capsuleId) => {
    const capsule = capsules.find(c => c.id === capsuleId);
    setSelectedCapsule(capsule);
    setCurrentGeneration(0);
    setIsPlaying(false);
  };

  // Handle play/pause
  const togglePlayback = () => {
    setIsPlaying(!isPlaying);
  };

  // Handle generation change
  const handleGenerationChange = (event, newValue) => {
    setCurrentGeneration(newValue);
  };

  // Handle next generation
  const handleNextGeneration = () => {
    if (!selectedCapsule) return;
    
    const generations = capsuleEvolutions[selectedCapsule.id];
    if (currentGeneration < generations.length - 1) {
      setCurrentGeneration(currentGeneration + 1);
    }
  };

  // Handle previous generation
  const handlePrevGeneration = () => {
    if (currentGeneration > 0) {
      setCurrentGeneration(currentGeneration - 1);
    }
  };

  // Handle reset
  const handleReset = () => {
    setCurrentGeneration(0);
    setIsPlaying(false);
  };

  // Handle playback speed change
  const handleSpeedChange = (event, newValue) => {
    setPlaybackSpeed(newValue);
  };

  // Auto-advance generations when playing
  useEffect(() => {
    if (!isPlaying || !selectedCapsule) return;
    
    const generations = capsuleEvolutions[selectedCapsule.id];
    const interval = setInterval(() => {
      setCurrentGeneration(prevGen => {
        if (prevGen < generations.length - 1) {
          return prevGen + 1;
        } else {
          setIsPlaying(false);
          return prevGen;
        }
      });
    }, 2000 / playbackSpeed);
    
    return () => clearInterval(interval);
  }, [isPlaying, selectedCapsule, playbackSpeed]);

  // Format timestamp to date
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Get impact color
  const getImpactColor = (impact) => {
    const impactColors = {
      high: '#f44336',
      medium: '#ff9800',
      low: '#4caf50',
    };
    
    return impactColors[impact] || '#9e9e9e';
  };

  // Render current generation visualization
  const renderGenerationVisualization = () => {
    if (!selectedCapsule) return null;
    
    const generations = capsuleEvolutions[selectedCapsule.id];
    const generation = generations[currentGeneration];
    
    return (
      <Box sx={{ mt: 3 }}>
        <Paper elevation={0} sx={{ p: 3, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Generation {generation.generation}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {formatTimestamp(generation.timestamp)}
            </Typography>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card elevation={0} sx={{ bgcolor: 'background.default', borderRadius: 2, height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>
                    Trust Score
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'baseline' }}>
                    <Typography variant="h3" component="div" color={generation.trustScore > 90 ? 'success.main' : generation.trustScore > 80 ? 'primary.main' : 'warning.main'}>
                      {generation.trustScore.toFixed(1)}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ ml: 1 }}>
                      / 100
                    </Typography>
                  </Box>
                  
                  {currentGeneration > 0 && (
                    <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                      <TimelineIcon fontSize="small" color="action" sx={{ mr: 1 }} />
                      <Typography variant="body2" color="textSecondary">
                        {(generation.trustScore - generations[currentGeneration - 1].trustScore).toFixed(1) > 0 ? '+' : ''}
                        {(generation.trustScore - generations[currentGeneration - 1].trustScore).toFixed(1)} from previous
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={8}>
              <Card elevation={0} sx={{ bgcolor: 'background.default', borderRadius: 2, height: '100%' }}>
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>
                    Performance Metrics
                  </Typography>
                  <Grid container spacing={2} sx={{ mt: 1 }}>
                    {Object.entries(generation.performanceMetrics).map(([key, value]) => (
                      <Grid item xs={4} key={key}>
                        <Typography variant="body2" color="textSecondary">
                          {key.charAt(0).toUpperCase() + key.slice(1)}
                        </Typography>
                        <Typography variant="h6">
                          {value.toFixed(1)}%
                        </Typography>
                        {currentGeneration > 0 && (
                          <Typography 
                            variant="caption" 
                            color={
                              value - generations[currentGeneration - 1].performanceMetrics[key] > 0 
                                ? 'success.main' 
                                : 'error.main'
                            }
                          >
                            {(value - generations[currentGeneration - 1].performanceMetrics[key]).toFixed(1) > 0 ? '+' : ''}
                            {(value - generations[currentGeneration - 1].performanceMetrics[key]).toFixed(1)}%
                          </Typography>
                        )}
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12}>
              <Card elevation={0} sx={{ bgcolor: 'background.default', borderRadius: 2 }}>
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>
                    Mutations
                  </Typography>
                  
                  {generation.mutations.length > 0 ? (
                    <Box sx={{ mt: 1 }}>
                      {generation.mutations.map((mutation, index) => (
                        <Box 
                          key={index}
                          sx={{ 
                            display: 'flex', 
                            alignItems: 'center',
                            mb: 1,
                          }}
                        >
                          <Chip 
                            label={mutation.type} 
                            size="small" 
                            color="primary" 
                            sx={{ mr: 1, textTransform: 'capitalize' }} 
                          />
                          <Typography variant="body2">
                            {mutation.name}
                          </Typography>
                          <Chip 
                            label={mutation.impact} 
                            size="small" 
                            sx={{ 
                              ml: 'auto', 
                              bgcolor: getImpactColor(mutation.impact),
                              color: 'white',
                              textTransform: 'uppercase',
                              fontSize: '0.7rem',
                            }} 
                          />
                        </Box>
                      ))}
                    </Box>
                  ) : (
                    <Typography variant="body2" color="textSecondary">
                      Base generation - no mutations
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Paper>
      </Box>
    );
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Capsule Evolution Timelapse
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper elevation={0} sx={{ p: 2, borderRadius: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Available Capsules
            </Typography>
            
            {capsules.map((capsule) => (
              <Card
                key={capsule.id}
                elevation={0}
                sx={{
                  mb: 2,
                  border: 1,
                  borderColor: selectedCapsule?.id === capsule.id ? 'primary.main' : 'divider',
                  borderRadius: 2,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: 'action.hover',
                  },
                }}
                onClick={() => handleCapsuleSelect(capsule.id)}
              >
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="subtitle2" fontWeight="medium">
                    {capsule.name}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 0.5 }}>
                    {capsule.description}
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1.5 }}>
                    <Chip 
                      label={`Gen ${capsule.currentGeneration}`} 
                      size="small" 
                      color="primary" 
                    />
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: capsule.trustScore > 90 ? 'success.main' : capsule.trustScore > 80 ? 'primary.main' : 'warning.main',
                        fontWeight: 'medium',
                      }}
                    >
                      Trust: {capsule.trustScore}%
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Paper elevation={0} sx={{ p: 2, borderRadius: 2 }}>
            {selectedCapsule ? (
              <>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle1">
                    {selectedCapsule.name}
                  </Typography>
                  <Button 
                    size="small" 
                    variant="outlined"
                    onClick={() => openModal('capsuleDetail', { capsuleId: selectedCapsule.id })}
                  >
                    View Details
                  </Button>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <IconButton onClick={handleReset} size="small">
                    <RestartAltIcon />
                  </IconButton>
                  <IconButton onClick={handlePrevGeneration} size="small" disabled={currentGeneration === 0}>
                    <SkipPreviousIcon />
                  </IconButton>
                  <IconButton onClick={togglePlayback} color="primary">
                    {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
                  </IconButton>
                  <IconButton 
                    onClick={handleNextGeneration} 
                    size="small" 
                    disabled={currentGeneration === capsuleEvolutions[selectedCapsule.id].length - 1}
                  >
                    <SkipNextIcon />
                  </IconButton>
                  
                  <Box sx={{ width: 200, ml: 2 }}>
                    <Slider
                      value={currentGeneration}
                      onChange={handleGenerationChange}
                      min={0}
                      max={capsuleEvolutions[selectedCapsule.id].length - 1}
                      step={1}
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="caption" color="textSecondary" sx={{ ml: 2, minWidth: 60 }}>
                    Gen {currentGeneration + 1}/{capsuleEvolutions[selectedCapsule.id].length}
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
                
                {renderGenerationVisualization()}
              </>
            ) : (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="body1" color="textSecondary">
                  Select a capsule to view its evolution
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CapsuleEvolutionTimelapse;
