/**
 * 27 Capsule Types Taxonomy
 * Week 8: White-Label Platform
 * 
 * Based on Document 70: Executive View - 27 Strategic Sub-Areas
 * Each capsule type maps to an Industriverse service family
 */

export const CAPSULE_CATEGORIES = {
  // 1. Semiconductor Manufacturing (6 sub-areas)
  THERMAL_MANAGEMENT: 'thermal_management',
  PLASMA_DYNAMICS: 'plasma_dynamics',
  RESIST_DIFFUSION: 'resist_diffusion',
  YIELD_OPTIMIZATION: 'yield_optimization',
  DEFECT_DETECTION: 'defect_detection',
  PROCESS_CONTROL: 'process_control',

  // 2. Energy & Sustainability (5 sub-areas)
  ENERGY_OPTIMIZATION: 'energy_optimization',
  CARBON_TRACKING: 'carbon_tracking',
  RENEWABLE_INTEGRATION: 'renewable_integration',
  GRID_BALANCING: 'grid_balancing',
  ENERGY_STORAGE: 'energy_storage',

  // 3. Edge Computing & IoT (4 sub-areas)
  EDGE_ADAPTATION: 'edge_adaptation',
  SENSOR_FUSION: 'sensor_fusion',
  PREDICTIVE_MAINTENANCE: 'predictive_maintenance',
  ANOMALY_DETECTION: 'anomaly_detection',

  // 4. Supply Chain & Logistics (3 sub-areas)
  INVENTORY_OPTIMIZATION: 'inventory_optimization',
  DEMAND_FORECASTING: 'demand_forecasting',
  ROUTE_OPTIMIZATION: 'route_optimization',

  // 5. Quality & Compliance (3 sub-areas)
  QUALITY_ASSURANCE: 'quality_assurance',
  REGULATORY_COMPLIANCE: 'regulatory_compliance',
  AUDIT_TRAIL: 'audit_trail',

  // 6. Financial Operations (3 sub-areas)
  COST_OPTIMIZATION: 'cost_optimization',
  REVENUE_FORECASTING: 'revenue_forecasting',
  RISK_MANAGEMENT: 'risk_management',

  // 7. Human Capital (3 sub-areas)
  WORKFORCE_SCHEDULING: 'workforce_scheduling',
  SKILLS_MATCHING: 'skills_matching',
  SAFETY_MONITORING: 'safety_monitoring',
} as const;

export type CapsuleCategory = typeof CAPSULE_CATEGORIES[keyof typeof CAPSULE_CATEGORIES];

export interface CapsuleCategoryMetadata {
  id: CapsuleCategory;
  name: string;
  description: string;
  icon: string;
  color: string;
  serviceFamily: string;
  whiteLabelWidget: string;
  examples: string[];
}

export const CAPSULE_CATEGORY_METADATA: Record<CapsuleCategory, CapsuleCategoryMetadata> = {
  // Semiconductor Manufacturing
  [CAPSULE_CATEGORIES.THERMAL_MANAGEMENT]: {
    id: CAPSULE_CATEGORIES.THERMAL_MANAGEMENT,
    name: 'Thermal Management',
    description: 'Real-time thermal monitoring and optimization for semiconductor fabrication',
    icon: '🌡️',
    color: '#ef4444',
    serviceFamily: 'ThermalSampler',
    whiteLabelWidget: '<iv-thermal-monitor>',
    examples: ['Temperature spike alerts', 'Cooling system optimization', 'Hotspot detection'],
  },
  
  [CAPSULE_CATEGORIES.PLASMA_DYNAMICS]: {
    id: CAPSULE_CATEGORIES.PLASMA_DYNAMICS,
    name: 'Plasma Dynamics',
    description: 'Plasma etching and deposition process optimization',
    icon: '⚡',
    color: '#8b5cf6',
    serviceFamily: 'WorldModel',
    whiteLabelWidget: '<iv-plasma-monitor>',
    examples: ['Etching uniformity', 'Plasma stability', 'Chamber condition monitoring'],
  },

  [CAPSULE_CATEGORIES.RESIST_DIFFUSION]: {
    id: CAPSULE_CATEGORIES.RESIST_DIFFUSION,
    name: 'Resist Diffusion',
    description: 'Photoresist application and diffusion modeling',
    icon: '🔬',
    color: '#06b6d4',
    serviceFamily: 'WorldModel',
    whiteLabelWidget: '<iv-resist-monitor>',
    examples: ['Coating thickness', 'Diffusion patterns', 'Exposure optimization'],
  },

  [CAPSULE_CATEGORIES.YIELD_OPTIMIZATION]: {
    id: CAPSULE_CATEGORIES.YIELD_OPTIMIZATION,
    name: 'Yield Optimization',
    description: 'Manufacturing yield improvement through data-driven insights',
    icon: '📈',
    color: '#10b981',
    serviceFamily: 'ProofEconomy',
    whiteLabelWidget: '<iv-yield-tracker>',
    examples: ['Yield trending', 'Root cause analysis', 'Process optimization'],
  },

  [CAPSULE_CATEGORIES.DEFECT_DETECTION]: {
    id: CAPSULE_CATEGORIES.DEFECT_DETECTION,
    name: 'Defect Detection',
    description: 'Automated defect identification and classification',
    icon: '🔍',
    color: '#f59e0b',
    serviceFamily: 'MicroAdaptEdge',
    whiteLabelWidget: '<iv-defect-scanner>',
    examples: ['Wafer inspection', 'Pattern recognition', 'Defect clustering'],
  },

  [CAPSULE_CATEGORIES.PROCESS_CONTROL]: {
    id: CAPSULE_CATEGORIES.PROCESS_CONTROL,
    name: 'Process Control',
    description: 'Advanced process control and statistical process control',
    icon: '🎛️',
    color: '#3b82f6',
    serviceFamily: 'DACOrchestrator',
    whiteLabelWidget: '<iv-process-controller>',
    examples: ['SPC charts', 'Control limits', 'Process capability'],
  },

  // Energy & Sustainability
  [CAPSULE_CATEGORIES.ENERGY_OPTIMIZATION]: {
    id: CAPSULE_CATEGORIES.ENERGY_OPTIMIZATION,
    name: 'Energy Optimization',
    description: 'Real-time energy consumption optimization',
    icon: '⚡',
    color: '#eab308',
    serviceFamily: 'EnergyAtlas',
    whiteLabelWidget: '<iv-energy-optimizer>',
    examples: ['Load balancing', 'Peak shaving', 'Demand response'],
  },

  [CAPSULE_CATEGORIES.CARBON_TRACKING]: {
    id: CAPSULE_CATEGORIES.CARBON_TRACKING,
    name: 'Carbon Tracking',
    description: 'Carbon footprint monitoring and reduction',
    icon: '🌱',
    color: '#22c55e',
    serviceFamily: 'EnergyAtlas',
    whiteLabelWidget: '<iv-carbon-tracker>',
    examples: ['Emissions monitoring', 'Carbon credits', 'Sustainability reporting'],
  },

  [CAPSULE_CATEGORIES.RENEWABLE_INTEGRATION]: {
    id: CAPSULE_CATEGORIES.RENEWABLE_INTEGRATION,
    name: 'Renewable Integration',
    description: 'Renewable energy source integration and management',
    icon: '☀️',
    color: '#f59e0b',
    serviceFamily: 'EnergyAtlas',
    whiteLabelWidget: '<iv-renewable-monitor>',
    examples: ['Solar forecasting', 'Wind integration', 'Battery storage'],
  },

  [CAPSULE_CATEGORIES.GRID_BALANCING]: {
    id: CAPSULE_CATEGORIES.GRID_BALANCING,
    name: 'Grid Balancing',
    description: 'Power grid load balancing and stability',
    icon: '⚖️',
    color: '#6366f1',
    serviceFamily: 'ThermalSampler',
    whiteLabelWidget: '<iv-grid-balancer>',
    examples: ['Frequency regulation', 'Voltage control', 'Reactive power'],
  },

  [CAPSULE_CATEGORIES.ENERGY_STORAGE]: {
    id: CAPSULE_CATEGORIES.ENERGY_STORAGE,
    name: 'Energy Storage',
    description: 'Battery and energy storage system optimization',
    icon: '🔋',
    color: '#14b8a6',
    serviceFamily: 'MicroAdaptEdge',
    whiteLabelWidget: '<iv-storage-manager>',
    examples: ['Battery health', 'Charge cycles', 'Storage optimization'],
  },

  // Edge Computing & IoT
  [CAPSULE_CATEGORIES.EDGE_ADAPTATION]: {
    id: CAPSULE_CATEGORIES.EDGE_ADAPTATION,
    name: 'Edge Adaptation',
    description: 'Self-evolutionary edge device adaptation',
    icon: '🔄',
    color: '#8b5cf6',
    serviceFamily: 'MicroAdaptEdge',
    whiteLabelWidget: '<iv-edge-adapter>',
    examples: ['Regime detection', 'Model adaptation', 'Edge intelligence'],
  },

  [CAPSULE_CATEGORIES.SENSOR_FUSION]: {
    id: CAPSULE_CATEGORIES.SENSOR_FUSION,
    name: 'Sensor Fusion',
    description: 'Multi-sensor data fusion and correlation',
    icon: '📡',
    color: '#06b6d4',
    serviceFamily: 'SimulatedSnapshot',
    whiteLabelWidget: '<iv-sensor-fusion>',
    examples: ['Data correlation', 'Sensor calibration', 'Multi-modal fusion'],
  },

  [CAPSULE_CATEGORIES.PREDICTIVE_MAINTENANCE]: {
    id: CAPSULE_CATEGORIES.PREDICTIVE_MAINTENANCE,
    name: 'Predictive Maintenance',
    description: 'Equipment failure prediction and maintenance scheduling',
    icon: '🔧',
    color: '#f59e0b',
    serviceFamily: 'WorldModel',
    whiteLabelWidget: '<iv-maintenance-predictor>',
    examples: ['Failure prediction', 'Maintenance scheduling', 'Asset health'],
  },

  [CAPSULE_CATEGORIES.ANOMALY_DETECTION]: {
    id: CAPSULE_CATEGORIES.ANOMALY_DETECTION,
    name: 'Anomaly Detection',
    description: 'Real-time anomaly detection and alerting',
    icon: '🚨',
    color: '#ef4444',
    serviceFamily: 'MicroAdaptEdge',
    whiteLabelWidget: '<iv-anomaly-detector>',
    examples: ['Pattern deviation', 'Outlier detection', 'Behavioral analysis'],
  },

  // Supply Chain & Logistics
  [CAPSULE_CATEGORIES.INVENTORY_OPTIMIZATION]: {
    id: CAPSULE_CATEGORIES.INVENTORY_OPTIMIZATION,
    name: 'Inventory Optimization',
    description: 'Inventory level optimization and stock management',
    icon: '📦',
    color: '#3b82f6',
    serviceFamily: 'ThermalSampler',
    whiteLabelWidget: '<iv-inventory-optimizer>',
    examples: ['Stock levels', 'Reorder points', 'Safety stock'],
  },

  [CAPSULE_CATEGORIES.DEMAND_FORECASTING]: {
    id: CAPSULE_CATEGORIES.DEMAND_FORECASTING,
    name: 'Demand Forecasting',
    description: 'Demand prediction and capacity planning',
    icon: '📊',
    color: '#10b981',
    serviceFamily: 'WorldModel',
    whiteLabelWidget: '<iv-demand-forecaster>',
    examples: ['Sales forecasting', 'Capacity planning', 'Trend analysis'],
  },

  [CAPSULE_CATEGORIES.ROUTE_OPTIMIZATION]: {
    id: CAPSULE_CATEGORIES.ROUTE_OPTIMIZATION,
    name: 'Route Optimization',
    description: 'Logistics route optimization and fleet management',
    icon: '🚚',
    color: '#06b6d4',
    serviceFamily: 'ThermalSampler',
    whiteLabelWidget: '<iv-route-optimizer>',
    examples: ['Delivery routes', 'Fleet tracking', 'Fuel optimization'],
  },

  // Quality & Compliance
  [CAPSULE_CATEGORIES.QUALITY_ASSURANCE]: {
    id: CAPSULE_CATEGORIES.QUALITY_ASSURANCE,
    name: 'Quality Assurance',
    description: 'Quality control and assurance monitoring',
    icon: '✅',
    color: '#10b981',
    serviceFamily: 'ProofEconomy',
    whiteLabelWidget: '<iv-quality-monitor>',
    examples: ['Quality metrics', 'Inspection results', 'Non-conformance tracking'],
  },

  [CAPSULE_CATEGORIES.REGULATORY_COMPLIANCE]: {
    id: CAPSULE_CATEGORIES.REGULATORY_COMPLIANCE,
    name: 'Regulatory Compliance',
    description: 'Regulatory compliance monitoring and reporting',
    icon: '📋',
    color: '#6366f1',
    serviceFamily: 'EnergyAtlas',
    whiteLabelWidget: '<iv-compliance-tracker>',
    examples: ['Compliance status', 'Audit preparation', 'Regulatory updates'],
  },

  [CAPSULE_CATEGORIES.AUDIT_TRAIL]: {
    id: CAPSULE_CATEGORIES.AUDIT_TRAIL,
    name: 'Audit Trail',
    description: 'Comprehensive audit trail and provenance tracking',
    icon: '📜',
    color: '#8b5cf6',
    serviceFamily: 'EnergyAtlas',
    whiteLabelWidget: '<iv-audit-trail>',
    examples: ['Change history', 'User actions', 'Data lineage'],
  },

  // Financial Operations
  [CAPSULE_CATEGORIES.COST_OPTIMIZATION]: {
    id: CAPSULE_CATEGORIES.COST_OPTIMIZATION,
    name: 'Cost Optimization',
    description: 'Operational cost reduction and optimization',
    icon: '💰',
    color: '#10b981',
    serviceFamily: 'ProofEconomy',
    whiteLabelWidget: '<iv-cost-optimizer>',
    examples: ['Cost analysis', 'Budget tracking', 'Savings opportunities'],
  },

  [CAPSULE_CATEGORIES.REVENUE_FORECASTING]: {
    id: CAPSULE_CATEGORIES.REVENUE_FORECASTING,
    name: 'Revenue Forecasting',
    description: 'Revenue prediction and financial planning',
    icon: '💵',
    color: '#22c55e',
    serviceFamily: 'WorldModel',
    whiteLabelWidget: '<iv-revenue-forecaster>',
    examples: ['Revenue trends', 'Financial projections', 'Growth modeling'],
  },

  [CAPSULE_CATEGORIES.RISK_MANAGEMENT]: {
    id: CAPSULE_CATEGORIES.RISK_MANAGEMENT,
    name: 'Risk Management',
    description: 'Risk identification, assessment, and mitigation',
    icon: '⚠️',
    color: '#f59e0b',
    serviceFamily: 'ThermalSampler',
    whiteLabelWidget: '<iv-risk-manager>',
    examples: ['Risk assessment', 'Mitigation strategies', 'Risk monitoring'],
  },

  // Human Capital
  [CAPSULE_CATEGORIES.WORKFORCE_SCHEDULING]: {
    id: CAPSULE_CATEGORIES.WORKFORCE_SCHEDULING,
    name: 'Workforce Scheduling',
    description: 'Employee scheduling and workforce optimization',
    icon: '👥',
    color: '#3b82f6',
    serviceFamily: 'ThermalSampler',
    whiteLabelWidget: '<iv-workforce-scheduler>',
    examples: ['Shift planning', 'Resource allocation', 'Availability tracking'],
  },

  [CAPSULE_CATEGORIES.SKILLS_MATCHING]: {
    id: CAPSULE_CATEGORIES.SKILLS_MATCHING,
    name: 'Skills Matching',
    description: 'Skills-based task assignment and talent matching',
    icon: '🎯',
    color: '#8b5cf6',
    serviceFamily: 'A2AHostAgent',
    whiteLabelWidget: '<iv-skills-matcher>',
    examples: ['Task assignment', 'Skills gap analysis', 'Training recommendations'],
  },

  [CAPSULE_CATEGORIES.SAFETY_MONITORING]: {
    id: CAPSULE_CATEGORIES.SAFETY_MONITORING,
    name: 'Safety Monitoring',
    description: 'Workplace safety monitoring and incident prevention',
    icon: '🦺',
    color: '#ef4444',
    serviceFamily: 'MicroAdaptEdge',
    whiteLabelWidget: '<iv-safety-monitor>',
    examples: ['Safety incidents', 'Hazard detection', 'Compliance tracking'],
  },
};

/**
 * Get all capsule categories
 */
export function getAllCategories(): CapsuleCategoryMetadata[] {
  return Object.values(CAPSULE_CATEGORY_METADATA);
}

/**
 * Get categories by service family
 */
export function getCategoriesByServiceFamily(serviceFamily: string): CapsuleCategoryMetadata[] {
  return getAllCategories().filter(cat => cat.serviceFamily === serviceFamily);
}

/**
 * Get category by ID
 */
export function getCategoryById(id: CapsuleCategory): CapsuleCategoryMetadata | undefined {
  return CAPSULE_CATEGORY_METADATA[id];
}

/**
 * Search categories by name or description
 */
export function searchCategories(query: string): CapsuleCategoryMetadata[] {
  const lowerQuery = query.toLowerCase();
  return getAllCategories().filter(cat => 
    cat.name.toLowerCase().includes(lowerQuery) ||
    cat.description.toLowerCase().includes(lowerQuery) ||
    cat.examples.some(ex => ex.toLowerCase().includes(lowerQuery))
  );
}
