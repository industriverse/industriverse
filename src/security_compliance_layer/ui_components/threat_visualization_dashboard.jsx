"""
Threat Visualization Dashboard for the Security & Compliance Layer

This component provides a comprehensive visualization of security threats and
vulnerabilities across the Industriverse platform, enabling intuitive monitoring,
analysis, and response to security incidents.

Key capabilities:
1. Real-time threat visualization
2. Threat intelligence integration
3. Vulnerability mapping
4. Attack vector analysis
5. Security posture assessment

The Threat Visualization Dashboard enables comprehensive monitoring and analysis
of security threats across the Industriverse platform.
"""

import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// Styled components for the threat visualization dashboard
const DashboardContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background-color: #1e2130;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  color: #e9ecef;
`;

const DashboardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background-color: #262b3e;
  border-bottom: 1px solid #343a40;
`;

const HeaderTitle = styled.h2`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #e9ecef;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 8px;
    color: #dc3545;
  }
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 12px;
`;

const ActionButton = styled.button`
  background-color: ${props => props.primary ? '#007bff' : 'rgba(255, 255, 255, 0.1)'};
  color: #e9ecef;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 6px;
  }
  
  &:hover {
    background-color: ${props => props.primary ? '#0069d9' : 'rgba(255, 255, 255, 0.15)'};
  }
`;

const FiltersContainer = styled.div`
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background-color: #262b3e;
  border-bottom: 1px solid #343a40;
  gap: 16px;
  flex-wrap: wrap;
`;

const FilterGroup = styled.div`
  display: flex;
  align-items: center;
`;

const FilterLabel = styled.label`
  font-size: 14px;
  color: #adb5bd;
  margin-right: 8px;
`;

const FilterSelect = styled.select`
  padding: 6px 12px;
  border: 1px solid #495057;
  border-radius: 4px;
  font-size: 14px;
  color: #e9ecef;
  background-color: #343a40;
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const TimeRangeSelector = styled.div`
  display: flex;
  align-items: center;
  background-color: #343a40;
  border-radius: 4px;
  overflow: hidden;
`;

const TimeRangeOption = styled.button`
  background-color: ${props => props.active ? '#007bff' : 'transparent'};
  color: ${props => props.active ? '#fff' : '#adb5bd'};
  border: none;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.active ? '#007bff' : 'rgba(0, 123, 255, 0.1)'};
  }
`;

const ContentContainer = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: auto auto auto;
  gap: 20px;
`;

const ThreatMapCard = styled.div`
  grid-column: span 8;
  grid-row: span 2;
  background-color: #262b3e;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #343a40;
  border-bottom: 1px solid #495057;
`;

const CardTitle = styled.h3`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #e9ecef;
`;

const CardContent = styled.div`
  flex: 1;
  padding: 16px;
  position: relative;
`;

const ThreatMapContainer = styled.div`
  width: 100%;
  height: 100%;
  min-height: 300px;
  position: relative;
  background-color: #1e2130;
  border-radius: 4px;
  overflow: hidden;
`;

const ThreatMapPlaceholder = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  text-align: center;
  padding: 20px;
`;

const ThreatSummaryCard = styled.div`
  grid-column: span 4;
  grid-row: span 1;
  background-color: #262b3e;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const SummaryContent = styled.div`
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const SummaryItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const SummaryLabel = styled.div`
  font-size: 14px;
  color: #adb5bd;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 8px;
    color: ${props => 
      props.severity === 'critical' ? '#dc3545' : 
      props.severity === 'high' ? '#fd7e14' : 
      props.severity === 'medium' ? '#ffc107' : 
      props.severity === 'low' ? '#28a745' : 
      '#6c757d'};
  }
`;

const SummaryValue = styled.div`
  font-size: 16px;
  font-weight: 600;
  color: #e9ecef;
`;

const ThreatActivityCard = styled.div`
  grid-column: span 4;
  grid-row: span 1;
  background-color: #262b3e;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const ActivityContent = styled.div`
  flex: 1;
  padding: 0;
  overflow-y: auto;
`;

const ActivityList = styled.div`
  display: flex;
  flex-direction: column;
`;

const ActivityItem = styled.div`
  padding: 12px 16px;
  border-bottom: 1px solid #343a40;
  transition: background-color 0.2s;
  cursor: pointer;
  
  &:hover {
    background-color: #343a40;
  }
  
  &:last-child {
    border-bottom: none;
  }
`;

const ActivityHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
`;

const ActivityTitle = styled.div`
  font-size: 14px;
  font-weight: 500;
  color: #e9ecef;
`;

const ActivityTime = styled.div`
  font-size: 12px;
  color: #6c757d;
`;

const ActivityDescription = styled.div`
  font-size: 12px;
  color: #adb5bd;
`;

const SeverityBadge = styled.span`
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  background-color: ${props => 
    props.severity === 'critical' ? 'rgba(220, 53, 69, 0.2)' : 
    props.severity === 'high' ? 'rgba(253, 126, 20, 0.2)' : 
    props.severity === 'medium' ? 'rgba(255, 193, 7, 0.2)' : 
    props.severity === 'low' ? 'rgba(40, 167, 69, 0.2)' : 
    'rgba(108, 117, 125, 0.2)'};
  color: ${props => 
    props.severity === 'critical' ? '#dc3545' : 
    props.severity === 'high' ? '#fd7e14' : 
    props.severity === 'medium' ? '#ffc107' : 
    props.severity === 'low' ? '#28a745' : 
    '#6c757d'};
  margin-left: 8px;
`;

const VulnerabilityCard = styled.div`
  grid-column: span 6;
  grid-row: span 1;
  background-color: #262b3e;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const VulnerabilityContent = styled.div`
  flex: 1;
  padding: 0;
  overflow-y: auto;
`;

const VulnerabilityList = styled.div`
  display: flex;
  flex-direction: column;
`;

const VulnerabilityItem = styled.div`
  padding: 12px 16px;
  border-bottom: 1px solid #343a40;
  transition: background-color 0.2s;
  cursor: pointer;
  
  &:hover {
    background-color: #343a40;
  }
  
  &:last-child {
    border-bottom: none;
  }
`;

const VulnerabilityHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
`;

const VulnerabilityTitle = styled.div`
  font-size: 14px;
  font-weight: 500;
  color: #e9ecef;
  display: flex;
  align-items: center;
`;

const VulnerabilityMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const VulnerabilityDescription = styled.div`
  font-size: 12px;
  color: #adb5bd;
  margin-bottom: 8px;
`;

const VulnerabilityFooter = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const VulnerabilityTags = styled.div`
  display: flex;
  gap: 4px;
`;

const VulnerabilityTag = styled.span`
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  background-color: rgba(0, 123, 255, 0.2);
  color: #007bff;
`;

const VulnerabilityStatus = styled.span`
  font-size: 12px;
  color: ${props => 
    props.status === 'open' ? '#dc3545' : 
    props.status === 'in_progress' ? '#ffc107' : 
    props.status === 'resolved' ? '#28a745' : 
    '#6c757d'};
  display: flex;
  align-items: center;
  
  &::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: ${props => 
      props.status === 'open' ? '#dc3545' : 
      props.status === 'in_progress' ? '#ffc107' : 
      props.status === 'resolved' ? '#28a745' : 
      '#6c757d'};
    margin-right: 4px;
  }
`;

const AttackVectorCard = styled.div`
  grid-column: span 6;
  grid-row: span 1;
  background-color: #262b3e;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const AttackVectorContent = styled.div`
  flex: 1;
  padding: 16px;
  position: relative;
`;

const AttackVectorChart = styled.div`
  width: 100%;
  height: 100%;
  min-height: 200px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const DetailModal = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const DetailPanel = styled(motion.div)`
  width: 700px;
  max-width: 90%;
  max-height: 90vh;
  background-color: #262b3e;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  color: #e9ecef;
`;

const DetailHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background-color: #343a40;
  border-bottom: 1px solid #495057;
`;

const DetailTitle = styled.h3`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #e9ecef;
  display: flex;
  align-items: center;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 20px;
  color: #adb5bd;
  cursor: pointer;
  
  &:hover {
    color: #e9ecef;
  }
`;

const DetailContent = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
`;

const DetailSection = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled.h4`
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #e9ecef;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 8px;
  }
`;

const DetailGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
`;

const DetailItem = styled.div`
  display: flex;
  flex-direction: column;
`;

const DetailLabel = styled.div`
  font-size: 12px;
  color: #adb5bd;
  margin-bottom: 4px;
`;

const DetailValue = styled.div`
  font-size: 14px;
  color: #e9ecef;
  font-weight: ${props => props.bold ? '600' : '400'};
`;

const TimelineContainer = styled.div`
  margin-top: 16px;
`;

const TimelineItem = styled.div`
  display: flex;
  margin-bottom: 16px;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 24px;
    left: 10px;
    bottom: -8px;
    width: 2px;
    background-color: #343a40;
  }
  
  &:last-child::before {
    display: none;
  }
`;

const TimelineIcon = styled.div`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: ${props => 
    props.type === 'detection' ? '#007bff' : 
    props.type === 'analysis' ? '#17a2b8' : 
    props.type === 'mitigation' ? '#28a745' : 
    props.type === 'escalation' ? '#dc3545' : 
    '#6c757d'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  margin-right: 12px;
  flex-shrink: 0;
`;

const TimelineContent = styled.div`
  flex: 1;
`;

const TimelineHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
`;

const TimelineTitle = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: #e9ecef;
`;

const TimelineTime = styled.div`
  font-size: 12px;
  color: #6c757d;
`;

const TimelineDescription = styled.div`
  font-size: 14px;
  color: #adb5bd;
`;

const ActionButtonsContainer = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 24px;
  justify-content: flex-end;
`;

/**
 * Threat Visualization Dashboard Component
 * 
 * This component provides a comprehensive visualization of security threats and
 * vulnerabilities across the Industriverse platform.
 */
const ThreatVisualizationDashboard = ({
  threatData,
  onRefresh,
  onTimeRangeChange,
  onSeverityFilter,
  onCategoryFilter,
  onThreatClick,
  onVulnerabilityClick,
  onMitigate,
  onInvestigate
}) => {
  const [timeRange, setTimeRange] = useState('24h');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [selectedThreat, setSelectedThreat] = useState(null);
  const [selectedVulnerability, setSelectedVulnerability] = useState(null);
  
  // Mock canvas for threat map visualization
  const canvasRef = useRef(null);
  
  // Handle time range change
  const handleTimeRangeChange = (range) => {
    setTimeRange(range);
    
    if (onTimeRangeChange) {
      onTimeRangeChange(range);
    }
  };
  
  // Handle severity filter change
  const handleSeverityFilterChange = (e) => {
    const severity = e.target.value;
    setSeverityFilter(severity);
    
    if (onSeverityFilter) {
      onSeverityFilter(severity);
    }
  };
  
  // Handle category filter change
  const handleCategoryFilterChange = (e) => {
    const category = e.target.value;
    setCategoryFilter(category);
    
    if (onCategoryFilter) {
      onCategoryFilter(category);
    }
  };
  
  // Handle threat click
  const handleThreatClick = (threat) => {
    setSelectedThreat(threat);
    
    if (onThreatClick) {
      onThreatClick(threat);
    }
  };
  
  // Handle vulnerability click
  const handleVulnerabilityClick = (vulnerability) => {
    setSelectedVulnerability(vulnerability);
    
    if (onVulnerabilityClick) {
      onVulnerabilityClick(vulnerability);
    }
  };
  
  // Close detail modal
  const closeDetail = () => {
    setSelectedThreat(null);
    setSelectedVulnerability(null);
  };
  
  // Handle mitigate
  const handleMitigate = (id, type) => {
    if (onMitigate) {
      onMitigate(id, type);
    }
    closeDetail();
  };
  
  // Handle investigate
  const handleInvestigate = (id, type) => {
    if (onInvestigate) {
      onInvestigate(id, type);
    }
    closeDetail();
  };
  
  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  // Get time elapsed
  const getTimeElapsed = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    if (diffDay > 0) {
      return `${diffDay}d ago`;
    } else if (diffHour > 0) {
      return `${diffHour}h ago`;
    } else if (diffMin > 0) {
      return `${diffMin}m ago`;
    } else {
      return 'Just now';
    }
  };
  
  // Get timeline icon
  const getTimelineIcon = (type) => {
    switch (type) {
      case 'detection':
        return '🔍';
      case 'analysis':
        return '📊';
      case 'mitigation':
        return '🛡️';
      case 'escalation':
        return '⚠️';
      default:
        return '📝';
    }
  };
  
  // Calculate threat summary
  const calculateThreatSummary = () => {
    if (!threatData || !threatData.threats) {
      return {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
        total: 0
      };
    }
    
    return {
      critical: threatData.threats.filter(t => t.severity === 'critical').length,
      high: threatData.threats.filter(t => t.severity === 'high').length,
      medium: threatData.threats.filter(t => t.severity === 'medium').length,
      low: threatData.threats.filter(t => t.severity === 'low').length,
      total: threatData.threats.length
    };
  };
  
  // Draw threat map
  useEffect(() => {
    if (canvasRef.current && threatData && threatData.mapData) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      const { width, height } = canvas.getBoundingClientRect();
      
      // Set canvas dimensions
      canvas.width = width;
      canvas.height = height;
      
      // Clear canvas
      ctx.fillStyle = '#1e2130';
      ctx.fillRect(0, 0, width, height);
      
      // Draw map (simplified placeholder)
      ctx.strokeStyle = '#343a40';
      ctx.lineWidth = 1;
      
      // Draw grid
      for (let x = 0; x < width; x += 50) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      
      for (let y = 0; y < height; y += 50) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }
      
      // Draw threat points
      threatData.mapData.forEach(point => {
        const x = point.x * width;
        const y = point.y * height;
        const radius = point.intensity * 20 + 5;
        
        // Draw glow
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
        
        let color;
        switch (point.severity) {
          case 'critical':
            color = '#dc3545';
            break;
          case 'high':
            color = '#fd7e14';
            break;
          case 'medium':
            color = '#ffc107';
            break;
          case 'low':
            color = '#28a745';
            break;
          default:
            color = '#6c757d';
        }
        
        gradient.addColorStop(0, `${color}CC`);
        gradient.addColorStop(1, `${color}00`);
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw center point
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fill();
      });
    }
  }, [threatData, timeRange, severityFilter, categoryFilter]);
  
  // Render threat summary
  const renderThreatSummary = () => {
    const summary = calculateThreatSummary();
    
    return (
      <SummaryContent>
        <SummaryItem>
          <SummaryLabel severity="critical">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM7 4H9V10H7V4ZM8 13C7.4 13 7 12.6 7 12C7 11.4 7.4 11 8 11C8.6 11 9 11.4 9 12C9 12.6 8.6 13 8 13Z" fill="currentColor"/>
            </svg>
            Critical Threats
          </SummaryLabel>
          <SummaryValue>{summary.critical}</SummaryValue>
        </SummaryItem>
        
        <SummaryItem>
          <SummaryLabel severity="high">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM7 4H9V10H7V4ZM8 13C7.4 13 7 12.6 7 12C7 11.4 7.4 11 8 11C8.6 11 9 11.4 9 12C9 12.6 8.6 13 8 13Z" fill="currentColor"/>
            </svg>
            High Threats
          </SummaryLabel>
          <SummaryValue>{summary.high}</SummaryValue>
        </SummaryItem>
        
        <SummaryItem>
          <SummaryLabel severity="medium">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM7 4H9V10H7V4ZM8 13C7.4 13 7 12.6 7 12C7 11.4 7.4 11 8 11C8.6 11 9 11.4 9 12C9 12.6 8.6 13 8 13Z" fill="currentColor"/>
            </svg>
            Medium Threats
          </SummaryLabel>
          <SummaryValue>{summary.medium}</SummaryValue>
        </SummaryItem>
        
        <SummaryItem>
          <SummaryLabel severity="low">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM7 4H9V10H7V4ZM8 13C7.4 13 7 12.6 7 12C7 11.4 7.4 11 8 11C8.6 11 9 11.4 9 12C9 12.6 8.6 13 8 13Z" fill="currentColor"/>
            </svg>
            Low Threats
          </SummaryLabel>
          <SummaryValue>{summary.low}</SummaryValue>
        </SummaryItem>
        
        <SummaryItem style={{ marginTop: '8px', paddingTop: '16px', borderTop: '1px solid #343a40' }}>
          <SummaryLabel>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM8 14C4.7 14 2 11.3 2 8C2 4.7 4.7 2 8 2C11.3 2 14 4.7 14 8C14 11.3 11.3 14 8 14Z" fill="currentColor"/>
              <path d="M8 4C7.4 4 7 4.4 7 5V8C7 8.6 7.4 9 8 9H10C10.6 9 11 8.6 11 8C11 7.4 10.6 7 10 7H9V5C9 4.4 8.6 4 8 4Z" fill="currentColor"/>
            </svg>
            Last Updated
          </SummaryLabel>
          <SummaryValue>{threatData?.lastUpdated ? formatDate(threatData.lastUpdated) : 'N/A'}</SummaryValue>
        </SummaryItem>
      </SummaryContent>
    );
  };
  
  // Render threat activity
  const renderThreatActivity = () => {
    if (!threatData || !threatData.activity || threatData.activity.length === 0) {
      return (
        <div style={{ padding: '20px', textAlign: 'center', color: '#6c757d' }}>
          No recent threat activity
        </div>
      );
    }
    
    return (
      <ActivityList>
        {threatData.activity.map((activity, index) => (
          <ActivityItem key={index} onClick={() => handleThreatClick(activity.threat)}>
            <ActivityHeader>
              <ActivityTitle>{activity.title}</ActivityTitle>
              <ActivityTime>{getTimeElapsed(activity.timestamp)}</ActivityTime>
            </ActivityHeader>
            <ActivityDescription>{activity.description}</ActivityDescription>
          </ActivityItem>
        ))}
      </ActivityList>
    );
  };
  
  // Render vulnerabilities
  const renderVulnerabilities = () => {
    if (!threatData || !threatData.vulnerabilities || threatData.vulnerabilities.length === 0) {
      return (
        <div style={{ padding: '20px', textAlign: 'center', color: '#6c757d' }}>
          No vulnerabilities detected
        </div>
      );
    }
    
    return (
      <VulnerabilityList>
        {threatData.vulnerabilities.map((vulnerability, index) => (
          <VulnerabilityItem key={index} onClick={() => handleVulnerabilityClick(vulnerability)}>
            <VulnerabilityHeader>
              <VulnerabilityTitle>
                {vulnerability.name}
                <SeverityBadge severity={vulnerability.severity}>
                  {vulnerability.severity.charAt(0).toUpperCase() + vulnerability.severity.slice(1)}
                </SeverityBadge>
              </VulnerabilityTitle>
              <VulnerabilityMeta>
                <span style={{ fontSize: '12px', color: '#6c757d' }}>
                  {vulnerability.id}
                </span>
              </VulnerabilityMeta>
            </VulnerabilityHeader>
            <VulnerabilityDescription>{vulnerability.description}</VulnerabilityDescription>
            <VulnerabilityFooter>
              <VulnerabilityTags>
                {vulnerability.tags.map((tag, tagIndex) => (
                  <VulnerabilityTag key={tagIndex}>{tag}</VulnerabilityTag>
                ))}
              </VulnerabilityTags>
              <VulnerabilityStatus status={vulnerability.status}>
                {vulnerability.status === 'open' ? 'Open' : 
                 vulnerability.status === 'in_progress' ? 'In Progress' : 
                 vulnerability.status === 'resolved' ? 'Resolved' : 
                 vulnerability.status}
              </VulnerabilityStatus>
            </VulnerabilityFooter>
          </VulnerabilityItem>
        ))}
      </VulnerabilityList>
    );
  };
  
  // Render attack vectors
  const renderAttackVectors = () => {
    if (!threatData || !threatData.attackVectors || threatData.attackVectors.length === 0) {
      return (
        <div style={{ padding: '20px', textAlign: 'center', color: '#6c757d' }}>
          No attack vector data available
        </div>
      );
    }
    
    // This would be implemented with a proper chart library like Chart.js or D3.js
    return (
      <AttackVectorChart>
        <div style={{ textAlign: 'center', color: '#6c757d' }}>
          Attack vector visualization would be implemented here with a proper chart library
        </div>
      </AttackVectorChart>
    );
  };
  
  // Render threat detail
  const renderThreatDetail = () => {
    if (!selectedThreat) return null;
    
    return (
      <DetailModal
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={closeDetail}
      >
        <DetailPanel
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={(e) => e.stopPropagation()}
        >
          <DetailHeader>
            <DetailTitle>
              <svg width="20" height="20" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px' }}>
                <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM7 4H9V10H7V4ZM8 13C7.4 13 7 12.6 7 12C7 11.4 7.4 11 8 11C8.6 11 9 11.4 9 12C9 12.6 8.6 13 8 13Z" fill="currentColor"/>
              </svg>
              Threat Details
            </DetailTitle>
            <CloseButton onClick={closeDetail}>&times;</CloseButton>
          </DetailHeader>
          
          <DetailContent>
            <DetailSection>
              <SectionTitle>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM8 14C4.7 14 2 11.3 2 8C2 4.7 4.7 2 8 2C11.3 2 14 4.7 14 8C14 11.3 11.3 14 8 14Z" fill="currentColor"/>
                  <path d="M7 4H9V10H7V4Z" fill="currentColor"/>
                  <path d="M7 11H9V13H7V11Z" fill="currentColor"/>
                </svg>
                Threat Information
              </SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>Threat ID</DetailLabel>
                  <DetailValue bold>{selectedThreat.id}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Severity</DetailLabel>
                  <DetailValue>
                    <SeverityBadge severity={selectedThreat.severity}>
                      {selectedThreat.severity.charAt(0).toUpperCase() + selectedThreat.severity.slice(1)}
                    </SeverityBadge>
                  </DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Category</DetailLabel>
                  <DetailValue>{selectedThreat.category}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Source</DetailLabel>
                  <DetailValue>{selectedThreat.source}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Detected</DetailLabel>
                  <DetailValue>{formatDate(selectedThreat.detectedAt)}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Status</DetailLabel>
                  <DetailValue bold style={{ color: 
                    selectedThreat.status === 'active' ? '#dc3545' : 
                    selectedThreat.status === 'mitigated' ? '#28a745' : 
                    selectedThreat.status === 'investigating' ? '#ffc107' : 
                    '#6c757d'
                  }}>
                    {selectedThreat.status.charAt(0).toUpperCase() + selectedThreat.status.slice(1)}
                  </DetailValue>
                </DetailItem>
              </DetailGrid>
              
              <div style={{ marginTop: '16px' }}>
                <DetailLabel>Description</DetailLabel>
                <DetailValue style={{ marginTop: '4px' }}>
                  {selectedThreat.description}
                </DetailValue>
              </div>
            </DetailSection>
            
            <DetailSection>
              <SectionTitle>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 0H2C0.9 0 0 0.9 0 2V14C0 15.1 0.9 16 2 16H14C15.1 16 16 15.1 16 14V2C16 0.9 15.1 0 14 0ZM14 14H2V2H14V14Z" fill="currentColor"/>
                  <path d="M7 11H9V13H7V11Z" fill="currentColor"/>
                  <path d="M7 3H9V9H7V3Z" fill="currentColor"/>
                </svg>
                Impact Assessment
              </SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>Affected Systems</DetailLabel>
                  <DetailValue>{selectedThreat.affectedSystems?.join(', ') || 'None'}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Affected Users</DetailLabel>
                  <DetailValue>{selectedThreat.affectedUsers || 'None'}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Data Impact</DetailLabel>
                  <DetailValue>{selectedThreat.dataImpact || 'None'}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Service Impact</DetailLabel>
                  <DetailValue>{selectedThreat.serviceImpact || 'None'}</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>
            
            {selectedThreat.timeline && selectedThreat.timeline.length > 0 && (
              <DetailSection>
                <SectionTitle>
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM8 14C4.7 14 2 11.3 2 8C2 4.7 4.7 2 8 2C11.3 2 14 4.7 14 8C14 11.3 11.3 14 8 14Z" fill="currentColor"/>
                    <path d="M8 4C7.4 4 7 4.4 7 5V8C7 8.6 7.4 9 8 9H10C10.6 9 11 8.6 11 8C11 7.4 10.6 7 10 7H9V5C9 4.4 8.6 4 8 4Z" fill="currentColor"/>
                  </svg>
                  Timeline
                </SectionTitle>
                <TimelineContainer>
                  {selectedThreat.timeline.map((event, index) => (
                    <TimelineItem key={index}>
                      <TimelineIcon type={event.type}>
                        {getTimelineIcon(event.type)}
                      </TimelineIcon>
                      <TimelineContent>
                        <TimelineHeader>
                          <TimelineTitle>{event.title}</TimelineTitle>
                          <TimelineTime>{formatDate(event.timestamp)}</TimelineTime>
                        </TimelineHeader>
                        <TimelineDescription>{event.description}</TimelineDescription>
                      </TimelineContent>
                    </TimelineItem>
                  ))}
                </TimelineContainer>
              </DetailSection>
            )}
            
            <ActionButtonsContainer>
              <ActionButton onClick={() => handleInvestigate(selectedThreat.id, 'threat')}>
                Investigate
              </ActionButton>
              <ActionButton primary onClick={() => handleMitigate(selectedThreat.id, 'threat')}>
                Mitigate Threat
              </ActionButton>
            </ActionButtonsContainer>
          </DetailContent>
        </DetailPanel>
      </DetailModal>
    );
  };
  
  // Render vulnerability detail
  const renderVulnerabilityDetail = () => {
    if (!selectedVulnerability) return null;
    
    return (
      <DetailModal
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={closeDetail}
      >
        <DetailPanel
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={(e) => e.stopPropagation()}
        >
          <DetailHeader>
            <DetailTitle>
              <svg width="20" height="20" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px' }}>
                <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM11.3 5.3L7.3 9.3C7.1 9.5 6.9 9.5 6.7 9.3L4.7 7.3C4.5 7.1 4.5 6.9 4.7 6.7C4.9 6.5 5.1 6.5 5.3 6.7L7 8.4L10.7 4.7C10.9 4.5 11.1 4.5 11.3 4.7C11.5 4.9 11.5 5.1 11.3 5.3Z" fill="currentColor"/>
              </svg>
              Vulnerability Details
            </DetailTitle>
            <CloseButton onClick={closeDetail}>&times;</CloseButton>
          </DetailHeader>
          
          <DetailContent>
            <DetailSection>
              <SectionTitle>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM8 14C4.7 14 2 11.3 2 8C2 4.7 4.7 2 8 2C11.3 2 14 4.7 14 8C14 11.3 11.3 14 8 14Z" fill="currentColor"/>
                  <path d="M7 4H9V10H7V4Z" fill="currentColor"/>
                  <path d="M7 11H9V13H7V11Z" fill="currentColor"/>
                </svg>
                Vulnerability Information
              </SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>Vulnerability ID</DetailLabel>
                  <DetailValue bold>{selectedVulnerability.id}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Severity</DetailLabel>
                  <DetailValue>
                    <SeverityBadge severity={selectedVulnerability.severity}>
                      {selectedVulnerability.severity.charAt(0).toUpperCase() + selectedVulnerability.severity.slice(1)}
                    </SeverityBadge>
                  </DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Category</DetailLabel>
                  <DetailValue>{selectedVulnerability.category}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>CVSS Score</DetailLabel>
                  <DetailValue>{selectedVulnerability.cvssScore || 'N/A'}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Detected</DetailLabel>
                  <DetailValue>{formatDate(selectedVulnerability.detectedAt)}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Status</DetailLabel>
                  <DetailValue bold style={{ color: 
                    selectedVulnerability.status === 'open' ? '#dc3545' : 
                    selectedVulnerability.status === 'in_progress' ? '#ffc107' : 
                    selectedVulnerability.status === 'resolved' ? '#28a745' : 
                    '#6c757d'
                  }}>
                    {selectedVulnerability.status === 'open' ? 'Open' : 
                     selectedVulnerability.status === 'in_progress' ? 'In Progress' : 
                     selectedVulnerability.status === 'resolved' ? 'Resolved' : 
                     selectedVulnerability.status}
                  </DetailValue>
                </DetailItem>
              </DetailGrid>
              
              <div style={{ marginTop: '16px' }}>
                <DetailLabel>Description</DetailLabel>
                <DetailValue style={{ marginTop: '4px' }}>
                  {selectedVulnerability.description}
                </DetailValue>
              </div>
              
              {selectedVulnerability.tags && selectedVulnerability.tags.length > 0 && (
                <div style={{ marginTop: '16px' }}>
                  <DetailLabel>Tags</DetailLabel>
                  <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '4px' }}>
                    {selectedVulnerability.tags.map((tag, index) => (
                      <VulnerabilityTag key={index}>{tag}</VulnerabilityTag>
                    ))}
                  </div>
                </div>
              )}
            </DetailSection>
            
            <DetailSection>
              <SectionTitle>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 0H2C0.9 0 0 0.9 0 2V14C0 15.1 0.9 16 2 16H14C15.1 16 16 15.1 16 14V2C16 0.9 15.1 0 14 0ZM14 14H2V2H14V14Z" fill="currentColor"/>
                  <path d="M7 11H9V13H7V11Z" fill="currentColor"/>
                  <path d="M7 3H9V9H7V3Z" fill="currentColor"/>
                </svg>
                Impact Assessment
              </SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>Affected Components</DetailLabel>
                  <DetailValue>{selectedVulnerability.affectedComponents?.join(', ') || 'None'}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Exploitability</DetailLabel>
                  <DetailValue>{selectedVulnerability.exploitability || 'Unknown'}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Attack Vector</DetailLabel>
                  <DetailValue>{selectedVulnerability.attackVector || 'Unknown'}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>Potential Impact</DetailLabel>
                  <DetailValue>{selectedVulnerability.potentialImpact || 'Unknown'}</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>
            
            {selectedVulnerability.remediation && (
              <DetailSection>
                <SectionTitle>
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM11.3 5.3L7.3 9.3C7.1 9.5 6.9 9.5 6.7 9.3L4.7 7.3C4.5 7.1 4.5 6.9 4.7 6.7C4.9 6.5 5.1 6.5 5.3 6.7L7 8.4L10.7 4.7C10.9 4.5 11.1 4.5 11.3 4.7C11.5 4.9 11.5 5.1 11.3 5.3Z" fill="currentColor"/>
                  </svg>
                  Remediation
                </SectionTitle>
                <div>
                  <DetailValue style={{ marginTop: '4px' }}>
                    {selectedVulnerability.remediation}
                  </DetailValue>
                </div>
              </DetailSection>
            )}
            
            <ActionButtonsContainer>
              <ActionButton onClick={() => handleInvestigate(selectedVulnerability.id, 'vulnerability')}>
                Investigate
              </ActionButton>
              <ActionButton primary onClick={() => handleMitigate(selectedVulnerability.id, 'vulnerability')}>
                Remediate Vulnerability
              </ActionButton>
            </ActionButtonsContainer>
          </DetailContent>
        </DetailPanel>
      </DetailModal>
    );
  };
  
  return (
    <DashboardContainer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <DashboardHeader>
        <HeaderTitle>
          <svg width="20" height="20" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8C16 3.6 12.4 0 8 0ZM7 4H9V10H7V4ZM8 13C7.4 13 7 12.6 7 12C7 11.4 7.4 11 8 11C8.6 11 9 11.4 9 12C9 12.6 8.6 13 8 13Z" fill="currentColor"/>
          </svg>
          Threat Visualization
        </HeaderTitle>
        <HeaderActions>
          <ActionButton onClick={onRefresh}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 8C14 11.3 11.3 14 8 14C4.7 14 2 11.3 2 8C2 4.7 4.7 2 8 2C9.7 2 11.2 2.7 12.3 3.8L10 6H16V0L13.7 2.3C12.2 0.9 10.2 0 8 0C3.6 0 0 3.6 0 8C0 12.4 3.6 16 8 16C12.4 16 16 12.4 16 8H14Z" fill="currentColor"/>
            </svg>
            Refresh
          </ActionButton>
          <ActionButton primary>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M15.7 7.3L8.7 0.3C8.5 0.1 8.3 0 8 0H2C0.9 0 0 0.9 0 2V8C0 8.3 0.1 8.5 0.3 8.7L7.3 15.7C7.5 15.9 7.7 16 8 16C8.3 16 8.5 15.9 8.7 15.7L15.7 8.7C15.9 8.5 16 8.3 16 8C16 7.7 15.9 7.5 15.7 7.3ZM4 6C3.4 6 3 5.6 3 5C3 4.4 3.4 4 4 4C4.6 4 5 4.4 5 5C5 5.6 4.6 6 4 6Z" fill="currentColor"/>
            </svg>
            Run Scan
          </ActionButton>
        </HeaderActions>
      </DashboardHeader>
      
      <FiltersContainer>
        <FilterGroup>
          <FilterLabel htmlFor="severity-filter">Severity:</FilterLabel>
          <FilterSelect 
            id="severity-filter"
            value={severityFilter}
            onChange={handleSeverityFilterChange}
          >
            <option value="all">All</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </FilterSelect>
        </FilterGroup>
        
        <FilterGroup>
          <FilterLabel htmlFor="category-filter">Category:</FilterLabel>
          <FilterSelect 
            id="category-filter"
            value={categoryFilter}
            onChange={handleCategoryFilterChange}
          >
            <option value="all">All</option>
            <option value="malware">Malware</option>
            <option value="intrusion">Intrusion</option>
            <option value="data_leak">Data Leak</option>
            <option value="vulnerability">Vulnerability</option>
            <option value="anomaly">Anomaly</option>
          </FilterSelect>
        </FilterGroup>
        
        <FilterGroup>
          <FilterLabel>Time Range:</FilterLabel>
          <TimeRangeSelector>
            <TimeRangeOption 
              active={timeRange === '24h'} 
              onClick={() => handleTimeRangeChange('24h')}
            >
              24h
            </TimeRangeOption>
            <TimeRangeOption 
              active={timeRange === '7d'} 
              onClick={() => handleTimeRangeChange('7d')}
            >
              7d
            </TimeRangeOption>
            <TimeRangeOption 
              active={timeRange === '30d'} 
              onClick={() => handleTimeRangeChange('30d')}
            >
              30d
            </TimeRangeOption>
            <TimeRangeOption 
              active={timeRange === '90d'} 
              onClick={() => handleTimeRangeChange('90d')}
            >
              90d
            </TimeRangeOption>
          </TimeRangeSelector>
        </FilterGroup>
      </FiltersContainer>
      
      <ContentContainer>
        <ThreatMapCard>
          <CardHeader>
            <CardTitle>Threat Map</CardTitle>
          </CardHeader>
          <CardContent>
            <ThreatMapContainer>
              {threatData && threatData.mapData ? (
                <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />
              ) : (
                <ThreatMapPlaceholder>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
                  <div style={{ fontSize: '16px', marginBottom: '8px' }}>No threat data available</div>
                  <div style={{ fontSize: '14px' }}>Run a security scan to visualize threats</div>
                </ThreatMapPlaceholder>
              )}
            </ThreatMapContainer>
          </CardContent>
        </ThreatMapCard>
        
        <ThreatSummaryCard>
          <CardHeader>
            <CardTitle>Threat Summary</CardTitle>
          </CardHeader>
          {renderThreatSummary()}
        </ThreatSummaryCard>
        
        <ThreatActivityCard>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <ActivityContent>
            {renderThreatActivity()}
          </ActivityContent>
        </ThreatActivityCard>
        
        <VulnerabilityCard>
          <CardHeader>
            <CardTitle>Vulnerabilities</CardTitle>
          </CardHeader>
          <VulnerabilityContent>
            {renderVulnerabilities()}
          </VulnerabilityContent>
        </VulnerabilityCard>
        
        <AttackVectorCard>
          <CardHeader>
            <CardTitle>Attack Vectors</CardTitle>
          </CardHeader>
          <AttackVectorContent>
            {renderAttackVectors()}
          </AttackVectorContent>
        </AttackVectorCard>
      </ContentContainer>
      
      <AnimatePresence>
        {renderThreatDetail()}
        {renderVulnerabilityDetail()}
      </AnimatePresence>
    </DashboardContainer>
  );
};

ThreatVisualizationDashboard.propTypes = {
  /** Threat data object */
  threatData: PropTypes.shape({
    threats: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        description: PropTypes.string,
        severity: PropTypes.oneOf(['critical', 'high', 'medium', 'low']).isRequired,
        category: PropTypes.string.isRequired,
        source: PropTypes.string,
        detectedAt: PropTypes.string.isRequired,
        status: PropTypes.string.isRequired,
        affectedSystems: PropTypes.arrayOf(PropTypes.string),
        affectedUsers: PropTypes.string,
        dataImpact: PropTypes.string,
        serviceImpact: PropTypes.string,
        timeline: PropTypes.arrayOf(
          PropTypes.shape({
            type: PropTypes.string.isRequired,
            title: PropTypes.string.isRequired,
            description: PropTypes.string,
            timestamp: PropTypes.string.isRequired
          })
        )
      })
    ),
    vulnerabilities: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        description: PropTypes.string,
        severity: PropTypes.oneOf(['critical', 'high', 'medium', 'low']).isRequired,
        category: PropTypes.string,
        cvssScore: PropTypes.number,
        detectedAt: PropTypes.string.isRequired,
        status: PropTypes.oneOf(['open', 'in_progress', 'resolved']).isRequired,
        tags: PropTypes.arrayOf(PropTypes.string),
        affectedComponents: PropTypes.arrayOf(PropTypes.string),
        exploitability: PropTypes.string,
        attackVector: PropTypes.string,
        potentialImpact: PropTypes.string,
        remediation: PropTypes.string
      })
    ),
    activity: PropTypes.arrayOf(
      PropTypes.shape({
        title: PropTypes.string.isRequired,
        description: PropTypes.string,
        timestamp: PropTypes.string.isRequired,
        threat: PropTypes.object
      })
    ),
    mapData: PropTypes.arrayOf(
      PropTypes.shape({
        x: PropTypes.number.isRequired,
        y: PropTypes.number.isRequired,
        severity: PropTypes.oneOf(['critical', 'high', 'medium', 'low']).isRequired,
        intensity: PropTypes.number.isRequired
      })
    ),
    attackVectors: PropTypes.array,
    lastUpdated: PropTypes.string
  }),
  
  /** Callback when refresh button is clicked */
  onRefresh: PropTypes.func,
  
  /** Callback when time range is changed */
  onTimeRangeChange: PropTypes.func,
  
  /** Callback when severity filter is changed */
  onSeverityFilter: PropTypes.func,
  
  /** Callback when category filter is changed */
  onCategoryFilter: PropTypes.func,
  
  /** Callback when a threat is clicked */
  onThreatClick: PropTypes.func,
  
  /** Callback when a vulnerability is clicked */
  onVulnerabilityClick: PropTypes.func,
  
  /** Callback when mitigate button is clicked */
  onMitigate: PropTypes.func,
  
  /** Callback when investigate button is clicked */
  onInvestigate: PropTypes.func
};

export default ThreatVisualizationDashboard;
