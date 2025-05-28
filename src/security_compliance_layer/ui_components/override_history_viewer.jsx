"""
Override History Viewer for the Security & Compliance Layer

This component provides a comprehensive view of security and compliance policy
overrides across the Industriverse platform, enabling audit, review, and
management of override decisions.

Key capabilities:
1. Override history visualization
2. Override decision details
3. Override approval workflow
4. Override audit trail
5. Override analytics

The Override History Viewer enables comprehensive tracking and management
of security and compliance policy overrides across the Industriverse platform.
"""

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// Styled components for the override history viewer
const ViewerContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const ViewerHeader = styled.div`
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

const FiltersContainer = styled.div`
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background-color: #fff;
  border-bottom: 1px solid #e9ecef;
  gap: 16px;
  flex-wrap: wrap;
`;

const FilterGroup = styled.div`
  display: flex;
  align-items: center;
`;

const FilterLabel = styled.label`
  font-size: 14px;
  color: #495057;
  margin-right: 8px;
`;

const FilterSelect = styled.select`
  padding: 6px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  color: #495057;
  background-color: #fff;
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: #80bdff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
`;

const FilterInput = styled.input`
  padding: 6px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  color: #495057;
  
  &:focus {
    outline: none;
    border-color: #80bdff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
`;

const SearchInput = styled.input`
  padding: 6px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  color: #495057;
  width: 240px;
  
  &:focus {
    outline: none;
    border-color: #80bdff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
`;

const ContentContainer = styled.div`
  flex: 1;
  padding: 0;
  overflow-y: auto;
`;

const OverridesTable = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.thead`
  background-color: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 1;
`;

const TableHeaderCell = styled.th`
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  border-bottom: 1px solid #e9ecef;
  white-space: nowrap;
  
  &:first-child {
    padding-left: 20px;
  }
  
  &:last-child {
    padding-right: 20px;
  }
`;

const TableBody = styled.tbody``;

const TableRow = styled.tr`
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: rgba(0, 123, 255, 0.05);
  }
  
  &:not(:last-child) {
    border-bottom: 1px solid #e9ecef;
  }
`;

const TableCell = styled.td`
  padding: 12px 16px;
  font-size: 14px;
  color: #212529;
  
  &:first-child {
    padding-left: 20px;
  }
  
  &:last-child {
    padding-right: 20px;
  }
`;

const StatusBadge = styled.span`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  background-color: ${props => 
    props.status === 'approved' ? 'rgba(40, 167, 69, 0.1)' : 
    props.status === 'pending' ? 'rgba(255, 193, 7, 0.1)' : 
    props.status === 'rejected' ? 'rgba(220, 53, 69, 0.1)' : 
    props.status === 'expired' ? 'rgba(108, 117, 125, 0.1)' : 
    'rgba(23, 162, 184, 0.1)'};
  color: ${props => 
    props.status === 'approved' ? '#28a745' : 
    props.status === 'pending' ? '#ffc107' : 
    props.status === 'rejected' ? '#dc3545' : 
    props.status === 'expired' ? '#6c757d' : 
    '#17a2b8'};
`;

const PriorityBadge = styled.span`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  background-color: ${props => 
    props.priority === 'critical' ? 'rgba(220, 53, 69, 0.1)' : 
    props.priority === 'high' ? 'rgba(253, 126, 20, 0.1)' : 
    props.priority === 'medium' ? 'rgba(255, 193, 7, 0.1)' : 
    'rgba(108, 117, 125, 0.1)'};
  color: ${props => 
    props.priority === 'critical' ? '#dc3545' : 
    props.priority === 'high' ? '#fd7e14' : 
    props.priority === 'medium' ? '#ffc107' : 
    '#6c757d'};
`;

const Pagination = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background-color: #f8f9fa;
  border-top: 1px solid #e9ecef;
`;

const PaginationInfo = styled.div`
  font-size: 14px;
  color: #6c757d;
`;

const PaginationControls = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const PaginationButton = styled.button`
  background-color: ${props => props.active ? '#007bff' : '#fff'};
  color: ${props => props.active ? '#fff' : '#6c757d'};
  border: 1px solid ${props => props.active ? '#007bff' : '#ced4da'};
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 14px;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.disabled ? 0.6 : 1};
  
  &:hover:not(:disabled) {
    background-color: ${props => props.active ? '#0069d9' : '#e9ecef'};
  }
`;

const DetailModal = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const DetailPanel = styled(motion.div)`
  width: 700px;
  max-width: 90%;
  max-height: 90vh;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const DetailHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
`;

const DetailTitle = styled.h3`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #343a40;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 20px;
  color: #6c757d;
  cursor: pointer;
  
  &:hover {
    color: #343a40;
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
  color: #343a40;
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
  color: #6c757d;
  margin-bottom: 4px;
`;

const DetailValue = styled.div`
  font-size: 14px;
  color: #212529;
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
    background-color: #e9ecef;
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
    props.type === 'creation' ? '#17a2b8' : 
    props.type === 'approval' ? '#28a745' : 
    props.type === 'rejection' ? '#dc3545' : 
    props.type === 'expiration' ? '#6c757d' : 
    props.type === 'modification' ? '#fd7e14' : 
    '#007bff'};
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
  color: #343a40;
`;

const TimelineTime = styled.div`
  font-size: 12px;
  color: #6c757d;
`;

const TimelineDescription = styled.div`
  font-size: 14px;
  color: #495057;
`;

const ApprovalActions = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 24px;
  justify-content: flex-end;
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
 * Override History Viewer Component
 * 
 * This component provides a comprehensive view of security and compliance policy
 * overrides across the Industriverse platform.
 */
const OverrideHistoryViewer = ({
  overrides,
  onRefresh,
  onExport,
  onApprove,
  onReject,
  onFilter,
  onSearch
}) => {
  const [selectedOverride, setSelectedOverride] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    timeRange: '30d',
    policyType: 'all'
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  
  // Handle filter change
  const handleFilterChange = (filterName, value) => {
    const newFilters = {
      ...filters,
      [filterName]: value
    };
    
    setFilters(newFilters);
    setCurrentPage(1);
    
    if (onFilter) {
      onFilter(newFilters);
    }
  };
  
  // Handle search
  const handleSearch = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    setCurrentPage(1);
    
    if (onSearch) {
      onSearch(query);
    }
  };
  
  // Handle row click
  const handleRowClick = (override) => {
    setSelectedOverride(override);
  };
  
  // Close detail modal
  const closeDetail = () => {
    setSelectedOverride(null);
  };
  
  // Handle approve
  const handleApprove = () => {
    if (onApprove && selectedOverride) {
      onApprove(selectedOverride.id);
      closeDetail();
    }
  };
  
  // Handle reject
  const handleReject = () => {
    if (onReject && selectedOverride) {
      onReject(selectedOverride.id);
      closeDetail();
    }
  };
  
  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return '✓';
      case 'pending':
        return '⏳';
      case 'rejected':
        return '✗';
      case 'expired':
        return '⌛';
      default:
        return '?';
    }
  };
  
  // Get timeline icon
  const getTimelineIcon = (type) => {
    switch (type) {
      case 'creation':
        return '🔧';
      case 'approval':
        return '✓';
      case 'rejection':
        return '✗';
      case 'expiration':
        return '⌛';
      case 'modification':
        return '✏️';
      default:
        return '📝';
    }
  };
  
  // Calculate pagination
  const totalPages = Math.ceil((overrides?.length || 0) / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = Math.min(startIndex + itemsPerPage, overrides?.length || 0);
  const currentOverrides = overrides?.slice(startIndex, endIndex) || [];
  
  // Render pagination controls
  const renderPagination = () => {
    const pages = [];
    
    // Add first page
    pages.push(
      <PaginationButton 
        key="first"
        onClick={() => setCurrentPage(1)}
        disabled={currentPage === 1}
      >
        &laquo;
      </PaginationButton>
    );
    
    // Add previous page
    pages.push(
      <PaginationButton 
        key="prev"
        onClick={() => setCurrentPage(currentPage - 1)}
        disabled={currentPage === 1}
      >
        &lsaquo;
      </PaginationButton>
    );
    
    // Add page numbers
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <PaginationButton 
          key={i}
          active={i === currentPage}
          onClick={() => setCurrentPage(i)}
        >
          {i}
        </PaginationButton>
      );
    }
    
    // Add next page
    pages.push(
      <PaginationButton 
        key="next"
        onClick={() => setCurrentPage(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        &rsaquo;
      </PaginationButton>
    );
    
    // Add last page
    pages.push(
      <PaginationButton 
        key="last"
        onClick={() => setCurrentPage(totalPages)}
        disabled={currentPage === totalPages}
      >
        &raquo;
      </PaginationButton>
    );
    
    return pages;
  };
  
  // Render no data message
  const renderNoData = () => {
    return (
      <NoDataMessage>
        <NoDataIcon>📋</NoDataIcon>
        <NoDataText>No override records found</NoDataText>
        <NoDataSubtext>
          {searchQuery ? 
            'Try adjusting your search criteria or filters.' : 
            'No security or compliance policy overrides have been recorded.'}
        </NoDataSubtext>
      </NoDataMessage>
    );
  };
  
  return (
    <ViewerContainer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <ViewerHeader>
        <HeaderTitle>Override History</HeaderTitle>
        <HeaderActions>
          <ActionButton onClick={onRefresh}>
            Refresh
          </ActionButton>
          <ActionButton onClick={onExport}>
            Export
          </ActionButton>
        </HeaderActions>
      </ViewerHeader>
      
      <FiltersContainer>
        <FilterGroup>
          <FilterLabel htmlFor="status-filter">Status:</FilterLabel>
          <FilterSelect 
            id="status-filter"
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
          >
            <option value="all">All</option>
            <option value="approved">Approved</option>
            <option value="pending">Pending</option>
            <option value="rejected">Rejected</option>
            <option value="expired">Expired</option>
          </FilterSelect>
        </FilterGroup>
        
        <FilterGroup>
          <FilterLabel htmlFor="priority-filter">Priority:</FilterLabel>
          <FilterSelect 
            id="priority-filter"
            value={filters.priority}
            onChange={(e) => handleFilterChange('priority', e.target.value)}
          >
            <option value="all">All</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </FilterSelect>
        </FilterGroup>
        
        <FilterGroup>
          <FilterLabel htmlFor="time-filter">Time Range:</FilterLabel>
          <FilterSelect 
            id="time-filter"
            value={filters.timeRange}
            onChange={(e) => handleFilterChange('timeRange', e.target.value)}
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="365d">Last year</option>
            <option value="all">All time</option>
          </FilterSelect>
        </FilterGroup>
        
        <FilterGroup>
          <FilterLabel htmlFor="policy-filter">Policy Type:</FilterLabel>
          <FilterSelect 
            id="policy-filter"
            value={filters.policyType}
            onChange={(e) => handleFilterChange('policyType', e.target.value)}
          >
            <option value="all">All</option>
            <option value="security">Security</option>
            <option value="compliance">Compliance</option>
            <option value="access">Access Control</option>
            <option value="data">Data Security</option>
          </FilterSelect>
        </FilterGroup>
        
        <FilterGroup style={{ marginLeft: 'auto' }}>
          <SearchInput 
            type="text"
            placeholder="Search overrides..."
            value={searchQuery}
            onChange={handleSearch}
          />
        </FilterGroup>
      </FiltersContainer>
      
      <ContentContainer>
        {overrides && overrides.length > 0 ? (
          <OverridesTable>
            <TableHeader>
              <tr>
                <TableHeaderCell>ID</TableHeaderCell>
                <TableHeaderCell>Policy</TableHeaderCell>
                <TableHeaderCell>Requester</TableHeaderCell>
                <TableHeaderCell>Status</TableHeaderCell>
                <TableHeaderCell>Priority</TableHeaderCell>
                <TableHeaderCell>Created</TableHeaderCell>
                <TableHeaderCell>Expires</TableHeaderCell>
                <TableHeaderCell>Approver</TableHeaderCell>
              </tr>
            </TableHeader>
            <TableBody>
              {currentOverrides.map(override => (
                <TableRow key={override.id} onClick={() => handleRowClick(override)}>
                  <TableCell>{override.id}</TableCell>
                  <TableCell>{override.policyName}</TableCell>
                  <TableCell>{override.requesterName}</TableCell>
                  <TableCell>
                    <StatusBadge status={override.status}>
                      {override.status.charAt(0).toUpperCase() + override.status.slice(1)}
                    </StatusBadge>
                  </TableCell>
                  <TableCell>
                    <PriorityBadge priority={override.priority}>
                      {override.priority.charAt(0).toUpperCase() + override.priority.slice(1)}
                    </PriorityBadge>
                  </TableCell>
                  <TableCell>{formatDate(override.createdAt)}</TableCell>
                  <TableCell>{override.expiresAt ? formatDate(override.expiresAt) : 'N/A'}</TableCell>
                  <TableCell>{override.approverName || 'N/A'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </OverridesTable>
        ) : (
          renderNoData()
        )}
      </ContentContainer>
      
      {overrides && overrides.length > 0 && (
        <Pagination>
          <PaginationInfo>
            Showing {startIndex + 1} to {endIndex} of {overrides.length} overrides
          </PaginationInfo>
          <PaginationControls>
            {renderPagination()}
          </PaginationControls>
        </Pagination>
      )}
      
      <AnimatePresence>
        {selectedOverride && (
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
                <DetailTitle>Override Details</DetailTitle>
                <CloseButton onClick={closeDetail}>&times;</CloseButton>
              </DetailHeader>
              
              <DetailContent>
                <DetailSection>
                  <SectionTitle>Override Information</SectionTitle>
                  <DetailGrid>
                    <DetailItem>
                      <DetailLabel>Override ID</DetailLabel>
                      <DetailValue bold>{selectedOverride.id}</DetailValue>
                    </DetailItem>
                    <DetailItem>
                      <DetailLabel>Status</DetailLabel>
                      <DetailValue>
                        <StatusBadge status={selectedOverride.status}>
                          {selectedOverride.status.charAt(0).toUpperCase() + selectedOverride.status.slice(1)}
                        </StatusBadge>
                      </DetailValue>
                    </DetailItem>
                    <DetailItem>
                      <DetailLabel>Created</DetailLabel>
                      <DetailValue>{formatDate(selectedOverride.createdAt)}</DetailValue>
                    </DetailItem>
                    <DetailItem>
                      <DetailLabel>Expires</DetailLabel>
                      <DetailValue>{selectedOverride.expiresAt ? formatDate(selectedOverride.expiresAt) : 'N/A'}</DetailValue>
                    </DetailItem>
                    <DetailItem>
                      <DetailLabel>Priority</DetailLabel>
                      <DetailValue>
                        <PriorityBadge priority={selectedOverride.priority}>
                          {selectedOverride.priority.charAt(0).toUpperCase() + selectedOverride.priority.slice(1)}
                        </PriorityBadge>
                      </DetailValue>
                    </DetailItem>
                    <DetailItem>
                      <DetailLabel>Duration</DetailLabel>
                      <DetailValue>{selectedOverride.duration || 'Permanent'}</DetailValue>
                    </DetailItem>
                  </DetailGrid>
                </DetailSection>
                
                <DetailSection>
                  <SectionTitle>Policy Information</SectionTitle>
                  <DetailGrid>
                    <DetailItem>
                      <DetailLabel>Policy Name</DetailLabel>
                      <DetailValue bold>{selectedOverride.policyName}</DetailValue>
                    </DetailItem>
                    <DetailItem>
                      <DetailLabel>Policy Type</DetailLabel>
                      <DetailValue>{selectedOverride.policyType}</DetailValue>
                    </DetailItem>
                    <DetailItem>
                      <DetailLabel>Policy ID</DetailLabel>
                      <DetailValue>{selectedOverride.policyId}</DetailValue>
                    </DetailItem>
                    <DetailItem>
                      <DetailLabel>Framework</DetailLabel>
                      <DetailValue>{selectedOverride.framework || 'N/A'}</DetailValue>
                    </DetailItem>
                  </DetailGrid>
                  
                  <div style={{ marginTop: '16px' }}>
                    <DetailLabel>Policy Description</DetailLabel>
                    <DetailValue style={{ marginTop: '4px' }}>
                      {selectedOverride.policyDescription || 'No description available.'}
                    </DetailValue>
                  </div>
                </DetailSection>
                
                <DetailSection>
                  <SectionTitle>Override Details</SectionTitle>
                  <div>
                    <DetailLabel>Justification</DetailLabel>
                    <DetailValue style={{ marginTop: '4px', marginBottom: '16px' }}>
                      {selectedOverride.justification || 'No justification provided.'}
                    </DetailValue>
                  </div>
                  
                  <DetailGrid>
                    <DetailItem>
                      <DetailLabel>Requester</DetailLabel>
                      <DetailValue bold>{selectedOverride.requesterName}</DetailValue>
                    </DetailItem>
                    <DetailItem>
                      <DetailLabel>Requester ID</DetailLabel>
                      <DetailValue>{selectedOverride.requesterId}</DetailValue>
                    </DetailItem>
                    <DetailItem>
                      <DetailLabel>Approver</DetailLabel>
                      <DetailValue bold>{selectedOverride.approverName || 'N/A'}</DetailValue>
                    </DetailItem>
                    <DetailItem>
                      <DetailLabel>Approver ID</DetailLabel>
                      <DetailValue>{selectedOverride.approverId || 'N/A'}</DetailValue>
                    </DetailItem>
                  </DetailGrid>
                  
                  {selectedOverride.approvalNotes && (
                    <div style={{ marginTop: '16px' }}>
                      <DetailLabel>Approval Notes</DetailLabel>
                      <DetailValue style={{ marginTop: '4px' }}>
                        {selectedOverride.approvalNotes}
                      </DetailValue>
                    </div>
                  )}
                </DetailSection>
                
                <DetailSection>
                  <SectionTitle>Timeline</SectionTitle>
                  <TimelineContainer>
                    {selectedOverride.timeline && selectedOverride.timeline.map((event, index) => (
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
                
                {selectedOverride.status === 'pending' && (
                  <ApprovalActions>
                    <ActionButton onClick={handleReject}>
                      Reject Override
                    </ActionButton>
                    <ActionButton primary onClick={handleApprove}>
                      Approve Override
                    </ActionButton>
                  </ApprovalActions>
                )}
              </DetailContent>
            </DetailPanel>
          </DetailModal>
        )}
      </AnimatePresence>
    </ViewerContainer>
  );
};

OverrideHistoryViewer.propTypes = {
  /** Array of override records */
  overrides: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      policyId: PropTypes.string.isRequired,
      policyName: PropTypes.string.isRequired,
      policyType: PropTypes.string.isRequired,
      policyDescription: PropTypes.string,
      status: PropTypes.oneOf(['approved', 'pending', 'rejected', 'expired']).isRequired,
      priority: PropTypes.oneOf(['critical', 'high', 'medium', 'low']).isRequired,
      createdAt: PropTypes.string.isRequired,
      expiresAt: PropTypes.string,
      duration: PropTypes.string,
      requesterId: PropTypes.string.isRequired,
      requesterName: PropTypes.string.isRequired,
      approverId: PropTypes.string,
      approverName: PropTypes.string,
      justification: PropTypes.string,
      approvalNotes: PropTypes.string,
      framework: PropTypes.string,
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
  
  /** Callback when refresh button is clicked */
  onRefresh: PropTypes.func,
  
  /** Callback when export button is clicked */
  onExport: PropTypes.func,
  
  /** Callback when approve button is clicked */
  onApprove: PropTypes.func,
  
  /** Callback when reject button is clicked */
  onReject: PropTypes.func,
  
  /** Callback when filters are changed */
  onFilter: PropTypes.func,
  
  /** Callback when search is performed */
  onSearch: PropTypes.func
};

export default OverrideHistoryViewer;
