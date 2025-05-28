"""
Compliance Status Panel for the Security & Compliance Layer

This component provides a comprehensive view of compliance status across
various regulatory frameworks and internal policies for the Industriverse platform.

Key capabilities:
1. Compliance framework status visualization
2. Compliance issue tracking and management
3. Compliance evidence repository access
4. Compliance reporting and dashboard
5. Compliance remediation workflow

The Compliance Status Panel enables comprehensive monitoring and management
of compliance status across the Industriverse platform.
"""

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// Styled components for the compliance status panel
const PanelContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const PanelHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
`;

const HeaderTitle = styled.h2`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #343a40;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 12px;
`;

const ActionButton = styled.button`
  background-color: ${props => props.primary ? '#007bff' : 'transparent'};
  color: ${props => props.primary ? '#fff' : '#6c757d'};
  border: ${props => props.primary ? 'none' : '1px solid #6c757d'};
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.primary ? '#0069d9' : 'rgba(108, 117, 125, 0.1)'};
  }
`;

const TabsContainer = styled.div`
  display: flex;
  border-bottom: 1px solid #e9ecef;
`;

const Tab = styled.div`
  padding: 12px 20px;
  font-size: 14px;
  font-weight: ${props => props.active ? '600' : '400'};
  color: ${props => props.active ? '#007bff' : '#495057'};
  border-bottom: ${props => props.active ? '2px solid #007bff' : 'none'};
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    color: ${props => props.active ? '#007bff' : '#007bff'};
    background-color: ${props => props.active ? 'transparent' : 'rgba(0, 123, 255, 0.05)'};
  }
`;

const ContentContainer = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
`;

const SummaryContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
`;

const SummaryCard = styled.div`
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
`;

const CardTitle = styled.h3`
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #343a40;
`;

const ComplianceScore = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 12px;
`;

const ScoreValue = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: ${props => 
    props.score >= 90 ? '#28a745' : 
    props.score >= 70 ? '#ffc107' : 
    '#dc3545'};
  margin-right: 8px;
`;

const ScoreLabel = styled.div`
  font-size: 14px;
  color: #6c757d;
`;

const ProgressBar = styled.div`
  height: 8px;
  width: 100%;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
`;

const ProgressFill = styled.div`
  height: 100%;
  width: ${props => props.percentage}%;
  background-color: ${props => 
    props.percentage >= 90 ? '#28a745' : 
    props.percentage >= 70 ? '#ffc107' : 
    '#dc3545'};
  border-radius: 4px;
  transition: width 0.3s ease;
`;

const StatusLabel = styled.div`
  font-size: 12px;
  color: ${props => 
    props.status === 'compliant' ? '#28a745' : 
    props.status === 'partial' ? '#ffc107' : 
    '#dc3545'};
  font-weight: 600;
  display: flex;
  align-items: center;
  
  &::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: ${props => 
      props.status === 'compliant' ? '#28a745' : 
      props.status === 'partial' ? '#ffc107' : 
      '#dc3545'};
    margin-right: 6px;
  }
`;

const FrameworksContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const FrameworkItem = styled.div`
  border: 1px solid #e9ecef;
  border-radius: 6px;
  overflow: hidden;
`;

const FrameworkHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #f8f9fa;
  cursor: pointer;
  
  &:hover {
    background-color: #e9ecef;
  }
`;

const FrameworkTitle = styled.div`
  font-size: 16px;
  font-weight: 500;
  color: #343a40;
  display: flex;
  align-items: center;
`;

const FrameworkStatus = styled.div`
  display: flex;
  align-items: center;
`;

const FrameworkContent = styled(motion.div)`
  padding: 16px;
  background-color: #fff;
  border-top: 1px solid #e9ecef;
`;

const RequirementsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const RequirementItem = styled.div`
  display: flex;
  align-items: flex-start;
  padding: 8px 0;
  border-bottom: 1px solid #f8f9fa;
  
  &:last-child {
    border-bottom: none;
  }
`;

const RequirementStatus = styled.div`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: ${props => 
    props.status === 'compliant' ? '#28a745' : 
    props.status === 'partial' ? '#ffc107' : 
    '#dc3545'};
  margin-right: 12px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
`;

const RequirementDetails = styled.div`
  flex: 1;
`;

const RequirementTitle = styled.div`
  font-size: 14px;
  font-weight: 500;
  color: #343a40;
  margin-bottom: 4px;
`;

const RequirementDescription = styled.div`
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 8px;
`;

const RequirementActions = styled.div`
  display: flex;
  gap: 8px;
`;

const RequirementAction = styled.button`
  background-color: transparent;
  color: #007bff;
  border: none;
  padding: 0;
  font-size: 12px;
  cursor: pointer;
  
  &:hover {
    text-decoration: underline;
  }
`;

const IssuesContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const IssueItem = styled.div`
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 16px;
  background-color: #fff;
`;

const IssueHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
`;

const IssueTitle = styled.div`
  font-size: 16px;
  font-weight: 500;
  color: #343a40;
`;

const IssueSeverity = styled.div`
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  background-color: ${props => 
    props.severity === 'critical' ? 'rgba(220, 53, 69, 0.1)' : 
    props.severity === 'high' ? 'rgba(253, 126, 20, 0.1)' : 
    props.severity === 'medium' ? 'rgba(255, 193, 7, 0.1)' : 
    'rgba(108, 117, 125, 0.1)'};
  color: ${props => 
    props.severity === 'critical' ? '#dc3545' : 
    props.severity === 'high' ? '#fd7e14' : 
    props.severity === 'medium' ? '#ffc107' : 
    '#6c757d'};
`;

const IssueDetails = styled.div`
  font-size: 14px;
  color: #495057;
  margin-bottom: 12px;
`;

const IssueMetadata = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
`;

const MetadataItem = styled.div`
  display: flex;
  flex-direction: column;
`;

const MetadataLabel = styled.div`
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 2px;
`;

const MetadataValue = styled.div`
  font-size: 14px;
  color: #343a40;
`;

const IssueActions = styled.div`
  display: flex;
  gap: 8px;
`;

const NoDataMessage = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #6c757d;
  text-align: center;
`;

const NoDataIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
  color: #e9ecef;
`;

const NoDataText = styled.div`
  font-size: 16px;
  margin-bottom: 8px;
`;

const NoDataSubtext = styled.div`
  font-size: 14px;
  max-width: 400px;
`;

/**
 * Compliance Status Panel Component
 * 
 * This component provides a comprehensive view of compliance status across
 * various regulatory frameworks and internal policies.
 */
const ComplianceStatusPanel = ({
  complianceData,
  onRefresh,
  onExport,
  onRemediate,
  onViewEvidence,
  onConfigureFramework
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedFrameworks, setExpandedFrameworks] = useState({});
  
  // Calculate overall compliance score
  const calculateOverallScore = () => {
    if (!complianceData || !complianceData.frameworks || complianceData.frameworks.length === 0) {
      return 0;
    }
    
    const totalScore = complianceData.frameworks.reduce((sum, framework) => sum + framework.score, 0);
    return Math.round(totalScore / complianceData.frameworks.length);
  };
  
  // Toggle framework expansion
  const toggleFramework = (frameworkId) => {
    setExpandedFrameworks(prev => ({
      ...prev,
      [frameworkId]: !prev[frameworkId]
    }));
  };
  
  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'compliant':
        return '✓';
      case 'partial':
        return '!';
      case 'non_compliant':
        return '✗';
      default:
        return '?';
    }
  };
  
  // Render the overview tab
  const renderOverview = () => {
    if (!complianceData || !complianceData.frameworks || complianceData.frameworks.length === 0) {
      return renderNoData('No compliance data available', 'Configure compliance frameworks to start monitoring compliance status.');
    }
    
    const overallScore = calculateOverallScore();
    
    return (
      <>
        <SummaryContainer>
          <SummaryCard>
            <CardTitle>Overall Compliance</CardTitle>
            <ComplianceScore>
              <ScoreValue score={overallScore}>{overallScore}%</ScoreValue>
              <ScoreLabel>Compliance Score</ScoreLabel>
            </ComplianceScore>
            <ProgressBar>
              <ProgressFill percentage={overallScore} />
            </ProgressBar>
            <StatusLabel status={
              overallScore >= 90 ? 'compliant' : 
              overallScore >= 70 ? 'partial' : 
              'non_compliant'
            }>
              {overallScore >= 90 ? 'Compliant' : 
               overallScore >= 70 ? 'Partially Compliant' : 
               'Non-Compliant'}
            </StatusLabel>
          </SummaryCard>
          
          <SummaryCard>
            <CardTitle>Frameworks</CardTitle>
            <div style={{ fontSize: '24px', fontWeight: '700', marginBottom: '12px' }}>
              {complianceData.frameworks.length}
            </div>
            <div style={{ fontSize: '14px', color: '#6c757d', marginBottom: '12px' }}>
              Active compliance frameworks
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', fontSize: '12px', color: '#28a745' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#28a745', marginRight: '4px' }}></div>
                {complianceData.frameworks.filter(f => f.status === 'compliant').length} Compliant
              </div>
              <div style={{ display: 'flex', alignItems: 'center', fontSize: '12px', color: '#ffc107' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ffc107', marginRight: '4px' }}></div>
                {complianceData.frameworks.filter(f => f.status === 'partial').length} Partial
              </div>
              <div style={{ display: 'flex', alignItems: 'center', fontSize: '12px', color: '#dc3545' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#dc3545', marginRight: '4px' }}></div>
                {complianceData.frameworks.filter(f => f.status === 'non_compliant').length} Non-Compliant
              </div>
            </div>
          </SummaryCard>
          
          <SummaryCard>
            <CardTitle>Issues</CardTitle>
            <div style={{ fontSize: '24px', fontWeight: '700', marginBottom: '12px' }}>
              {complianceData.issues ? complianceData.issues.length : 0}
            </div>
            <div style={{ fontSize: '14px', color: '#6c757d', marginBottom: '12px' }}>
              Active compliance issues
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              {complianceData.issues && (
                <>
                  <div style={{ display: 'flex', alignItems: 'center', fontSize: '12px', color: '#dc3545' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#dc3545', marginRight: '4px' }}></div>
                    {complianceData.issues.filter(i => i.severity === 'critical').length} Critical
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', fontSize: '12px', color: '#fd7e14' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#fd7e14', marginRight: '4px' }}></div>
                    {complianceData.issues.filter(i => i.severity === 'high').length} High
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', fontSize: '12px', color: '#ffc107' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ffc107', marginRight: '4px' }}></div>
                    {complianceData.issues.filter(i => i.severity === 'medium').length} Medium
                  </div>
                </>
              )}
            </div>
          </SummaryCard>
          
          <SummaryCard>
            <CardTitle>Last Assessment</CardTitle>
            <div style={{ fontSize: '16px', fontWeight: '500', marginBottom: '12px' }}>
              {complianceData.lastAssessment ? new Date(complianceData.lastAssessment).toLocaleString() : 'Never'}
            </div>
            <div style={{ fontSize: '14px', color: '#6c757d', marginBottom: '12px' }}>
              {complianceData.nextAssessment ? `Next assessment: ${new Date(complianceData.nextAssessment).toLocaleString()}` : 'No scheduled assessment'}
            </div>
            <ActionButton primary onClick={onRefresh} style={{ alignSelf: 'flex-start' }}>
              Run Assessment Now
            </ActionButton>
          </SummaryCard>
        </SummaryContainer>
        
        <CardTitle>Compliance Frameworks</CardTitle>
        <FrameworksContainer>
          {complianceData.frameworks.map(framework => (
            <FrameworkItem key={framework.id}>
              <FrameworkHeader onClick={() => toggleFramework(framework.id)}>
                <FrameworkTitle>
                  {framework.name}
                  {framework.version && <span style={{ fontSize: '12px', color: '#6c757d', marginLeft: '8px' }}>v{framework.version}</span>}
                </FrameworkTitle>
                <FrameworkStatus>
                  <StatusLabel status={framework.status}>
                    {framework.status === 'compliant' ? 'Compliant' : 
                     framework.status === 'partial' ? 'Partially Compliant' : 
                     'Non-Compliant'}
                  </StatusLabel>
                  <div style={{ marginLeft: '12px', transform: expandedFrameworks[framework.id] ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s' }}>
                    ▼
                  </div>
                </FrameworkStatus>
              </FrameworkHeader>
              
              <AnimatePresence>
                {expandedFrameworks[framework.id] && (
                  <FrameworkContent
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                      <div>
                        <div style={{ fontSize: '14px', color: '#6c757d', marginBottom: '4px' }}>Compliance Score</div>
                        <div style={{ fontSize: '18px', fontWeight: '600', color: framework.score >= 90 ? '#28a745' : framework.score >= 70 ? '#ffc107' : '#dc3545' }}>
                          {framework.score}%
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '14px', color: '#6c757d', marginBottom: '4px' }}>Requirements</div>
                        <div style={{ fontSize: '18px', fontWeight: '600' }}>
                          {framework.requirements.filter(r => r.status === 'compliant').length} / {framework.requirements.length} Compliant
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '14px', color: '#6c757d', marginBottom: '4px' }}>Last Updated</div>
                        <div style={{ fontSize: '14px' }}>
                          {framework.lastUpdated ? new Date(framework.lastUpdated).toLocaleDateString() : 'Never'}
                        </div>
                      </div>
                    </div>
                    
                    <RequirementsList>
                      {framework.requirements.map(requirement => (
                        <RequirementItem key={requirement.id}>
                          <RequirementStatus status={requirement.status}>
                            {getStatusIcon(requirement.status)}
                          </RequirementStatus>
                          <RequirementDetails>
                            <RequirementTitle>{requirement.name}</RequirementTitle>
                            <RequirementDescription>{requirement.description}</RequirementDescription>
                            <RequirementActions>
                              <RequirementAction onClick={() => onViewEvidence(framework.id, requirement.id)}>
                                View Evidence
                              </RequirementAction>
                              {requirement.status !== 'compliant' && (
                                <RequirementAction onClick={() => onRemediate(framework.id, requirement.id)}>
                                  Remediate
                                </RequirementAction>
                              )}
                            </RequirementActions>
                          </RequirementDetails>
                        </RequirementItem>
                      ))}
                    </RequirementsList>
                    
                    <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
                      <ActionButton onClick={() => onConfigureFramework(framework.id)}>
                        Configure Framework
                      </ActionButton>
                    </div>
                  </FrameworkContent>
                )}
              </AnimatePresence>
            </FrameworkItem>
          ))}
        </FrameworksContainer>
      </>
    );
  };
  
  // Render the issues tab
  const renderIssues = () => {
    if (!complianceData || !complianceData.issues || complianceData.issues.length === 0) {
      return renderNoData('No compliance issues found', 'All compliance requirements are currently being met.');
    }
    
    return (
      <IssuesContainer>
        {complianceData.issues.map(issue => (
          <IssueItem key={issue.id}>
            <IssueHeader>
              <IssueTitle>{issue.title}</IssueTitle>
              <IssueSeverity severity={issue.severity}>
                {issue.severity.charAt(0).toUpperCase() + issue.severity.slice(1)}
              </IssueSeverity>
            </IssueHeader>
            
            <IssueDetails>{issue.description}</IssueDetails>
            
            <IssueMetadata>
              <MetadataItem>
                <MetadataLabel>Framework</MetadataLabel>
                <MetadataValue>{issue.framework}</MetadataValue>
              </MetadataItem>
              <MetadataItem>
                <MetadataLabel>Requirement</MetadataLabel>
                <MetadataValue>{issue.requirement}</MetadataValue>
              </MetadataItem>
              <MetadataItem>
                <MetadataLabel>Detected</MetadataLabel>
                <MetadataValue>{new Date(issue.detectedAt).toLocaleDateString()}</MetadataValue>
              </MetadataItem>
              <MetadataItem>
                <MetadataLabel>Due Date</MetadataLabel>
                <MetadataValue>{issue.dueDate ? new Date(issue.dueDate).toLocaleDateString() : 'Not set'}</MetadataValue>
              </MetadataItem>
            </IssueMetadata>
            
            <IssueActions>
              <ActionButton primary onClick={() => onRemediate(issue.frameworkId, issue.requirementId)}>
                Remediate
              </ActionButton>
              <ActionButton onClick={() => onViewEvidence(issue.frameworkId, issue.requirementId)}>
                View Evidence
              </ActionButton>
            </IssueActions>
          </IssueItem>
        ))}
      </IssuesContainer>
    );
  };
  
  // Render the evidence tab
  const renderEvidence = () => {
    if (!complianceData || !complianceData.evidence || complianceData.evidence.length === 0) {
      return renderNoData('No compliance evidence available', 'Run a compliance assessment to collect evidence.');
    }
    
    // This would be implemented with a table or list of evidence items
    return (
      <div>Evidence repository implementation</div>
    );
  };
  
  // Render the reports tab
  const renderReports = () => {
    if (!complianceData || !complianceData.reports || complianceData.reports.length === 0) {
      return renderNoData('No compliance reports available', 'Generate a compliance report to view historical compliance data.');
    }
    
    // This would be implemented with a list of available reports
    return (
      <div>Reports implementation</div>
    );
  };
  
  // Render no data message
  const renderNoData = (message, subMessage) => {
    return (
      <NoDataMessage>
        <NoDataIcon>📋</NoDataIcon>
        <NoDataText>{message}</NoDataText>
        <NoDataSubtext>{subMessage}</NoDataSubtext>
      </NoDataMessage>
    );
  };
  
  // Render the active tab content
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'issues':
        return renderIssues();
      case 'evidence':
        return renderEvidence();
      case 'reports':
        return renderReports();
      default:
        return renderOverview();
    }
  };
  
  return (
    <PanelContainer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <PanelHeader>
        <HeaderTitle>Compliance Status</HeaderTitle>
        <HeaderActions>
          <ActionButton onClick={onRefresh}>
            Refresh
          </ActionButton>
          <ActionButton onClick={onExport}>
            Export
          </ActionButton>
          <ActionButton primary onClick={() => onConfigureFramework()}>
            Configure
          </ActionButton>
        </HeaderActions>
      </PanelHeader>
      
      <TabsContainer>
        <Tab 
          active={activeTab === 'overview'} 
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </Tab>
        <Tab 
          active={activeTab === 'issues'} 
          onClick={() => setActiveTab('issues')}
        >
          Issues {complianceData && complianceData.issues && complianceData.issues.length > 0 && `(${complianceData.issues.length})`}
        </Tab>
        <Tab 
          active={activeTab === 'evidence'} 
          onClick={() => setActiveTab('evidence')}
        >
          Evidence
        </Tab>
        <Tab 
          active={activeTab === 'reports'} 
          onClick={() => setActiveTab('reports')}
        >
          Reports
        </Tab>
      </TabsContainer>
      
      <ContentContainer>
        {renderTabContent()}
      </ContentContainer>
    </PanelContainer>
  );
};

ComplianceStatusPanel.propTypes = {
  /** Compliance data object */
  complianceData: PropTypes.shape({
    frameworks: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        version: PropTypes.string,
        status: PropTypes.oneOf(['compliant', 'partial', 'non_compliant']).isRequired,
        score: PropTypes.number.isRequired,
        lastUpdated: PropTypes.string,
        requirements: PropTypes.arrayOf(
          PropTypes.shape({
            id: PropTypes.string.isRequired,
            name: PropTypes.string.isRequired,
            description: PropTypes.string,
            status: PropTypes.oneOf(['compliant', 'partial', 'non_compliant']).isRequired
          })
        ).isRequired
      })
    ),
    issues: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string.isRequired,
        title: PropTypes.string.isRequired,
        description: PropTypes.string,
        severity: PropTypes.oneOf(['critical', 'high', 'medium', 'low']).isRequired,
        framework: PropTypes.string.isRequired,
        frameworkId: PropTypes.string.isRequired,
        requirement: PropTypes.string.isRequired,
        requirementId: PropTypes.string.isRequired,
        detectedAt: PropTypes.string.isRequired,
        dueDate: PropTypes.string
      })
    ),
    lastAssessment: PropTypes.string,
    nextAssessment: PropTypes.string
  }),
  
  /** Callback when refresh button is clicked */
  onRefresh: PropTypes.func,
  
  /** Callback when export button is clicked */
  onExport: PropTypes.func,
  
  /** Callback when remediate button is clicked */
  onRemediate: PropTypes.func,
  
  /** Callback when view evidence button is clicked */
  onViewEvidence: PropTypes.func,
  
  /** Callback when configure framework button is clicked */
  onConfigureFramework: PropTypes.func
};

export default ComplianceStatusPanel;
