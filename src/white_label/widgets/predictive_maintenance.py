"""
Predictive Maintenance Widget

AI-powered failure forecasting and maintenance scheduling
Uses thermodynamic indicators to predict component failures
"""

from typing import Dict, Any, List
from .widget_sdk import WidgetBase, WidgetConfig


class PredictiveMaintenanceWidget(WidgetBase):
    """
    Predictive maintenance widget showing:
    - Component health scores
    - Failure probability predictions
    - Maintenance recommendations
    - Time-to-failure estimates
    - Historical reliability data
    """

    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self.components = []
        self.maintenance_alerts = []
        self.next_maintenance = None

    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch predictive maintenance data"""
        return {
            'components': self.components,
            'maintenance_alerts': self.maintenance_alerts,
            'next_maintenance': self.next_maintenance
        }

    async def on_data_update(self, data: Dict[str, Any]):
        """Update maintenance predictions"""
        self.components = data.get('components', [])
        self.maintenance_alerts = data.get('maintenance_alerts', [])
        self.next_maintenance = data.get('next_maintenance')
        self.emit('data-updated', data)

    def _get_health_color(self, health: float) -> str:
        """Get color based on component health (0-100)"""
        if health >= 80:
            return self.theme.colors.get('proof', {}).get('value', '#2ECC71')
        elif health >= 50:
            return self.theme.colors.get('accent', {}).get('value', '#FF6B35')
        else:
            return self.theme.colors.get('alert', {}).get('value', '#E74C3C')

    async def render(self) -> str:
        """Render Predictive Maintenance widget"""
        css_vars = self.get_css_variables()

        # Generate sample data if none provided
        if not self.components:
            self.components = [
                {'name': 'Cooling System', 'health': 85, 'ttf': '45 days', 'confidence': 92},
                {'name': 'Power Supply Unit', 'health': 92, 'ttf': '120 days', 'confidence': 88},
                {'name': 'Network Interface', 'health': 65, 'ttf': '15 days', 'confidence': 95},
                {'name': 'Storage Array', 'health': 78, 'ttf': '60 days', 'confidence': 85},
            ]
            self.maintenance_alerts = [
                'Network Interface requires attention within 2 weeks',
                'Schedule cooling system inspection',
            ]
            self.next_maintenance = '2024-12-15'

        html = f"""
<div class="predictive-maintenance-widget" data-widget-id="{self.config.widget_id}">
    <style>
        .predictive-maintenance-widget {{
            {css_vars}
            --widget-proof: {self.theme.colors.get('proof', {}).get('value', '#2ECC71')};
            --widget-alert: {self.theme.colors.get('alert', {}).get('value', '#E74C3C')};
            --widget-entropy: {self.theme.colors.get('entropy', {}).get('value', '#9B59B6')};

            font-family: {self.theme.typography.get('fontFamily', {}).get('primary', 'Inter, sans-serif')};
            background: var(--widget-surface);
            border-radius: {self.theme.borders.get('radius', {}).get('lg', '0.5rem')};
            padding: var(--widget-spacing-lg);
            box-shadow: {self.theme.shadows.get('md', '0 4px 6px -1px rgba(0, 0, 0, 0.3)')};
            color: var(--widget-text-primary);
            min-width: 380px;
            max-width: 600px;
        }}

        .widget-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--widget-spacing-lg);
            padding-bottom: var(--widget-spacing-md);
            border-bottom: 2px solid var(--widget-primary);
        }}

        .widget-title {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xl', '1.25rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: var(--widget-accent);
        }}

        .next-maintenance {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
        }}

        .next-maintenance-date {{
            display: block;
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
            color: var(--widget-accent);
        }}

        .components-list {{
            margin-bottom: var(--widget-spacing-lg);
        }}

        .component-item {{
            background: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            padding: var(--widget-spacing-md);
            margin-bottom: var(--widget-spacing-sm);
            border-left: {self.theme.borders.get('width', {}).get('thick', '4px')} solid var(--component-color);
        }}

        .component-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--widget-spacing-sm);
        }}

        .component-name {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
            color: var(--widget-text-primary);
        }}

        .component-health {{
            font-size: {self.theme.typography.get('fontSize', {}).get('lg', '1.125rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: var(--component-color);
        }}

        .health-bar {{
            width: 100%;
            height: 6px;
            background: var(--widget-surface);
            border-radius: {self.theme.borders.get('radius', {}).get('full', '9999px')};
            overflow: hidden;
            margin-bottom: var(--widget-spacing-xs);
        }}

        .health-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--component-color), var(--component-color-light));
            border-radius: {self.theme.borders.get('radius', {}).get('full', '9999px')};
            transition: width 1s ease-out;
            animation: fill-bar 1s ease-out;
        }}

        @keyframes fill-bar {{
            from {{ width: 0; }}
        }}

        .component-details {{
            display: flex;
            justify-content: space-between;
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
        }}

        .detail-item {{
            display: flex;
            flex-direction: column;
        }}

        .detail-label {{
            text-transform: uppercase;
            margin-bottom: 2px;
        }}

        .detail-value {{
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
            color: var(--widget-text-primary);
        }}

        .alerts-section {{
            background: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            padding: var(--widget-spacing-md);
            border-left: {self.theme.borders.get('width', {}).get('thick', '4px')} solid var(--widget-entropy);
        }}

        .alerts-title {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
            color: var(--widget-text-primary);
            margin-bottom: var(--widget-spacing-sm);
            display: flex;
            align-items: center;
            gap: {self.theme.spacing.get('xs', '0.25rem')};
        }}

        .alerts-icon {{
            width: 16px;
            height: 16px;
            background: var(--widget-entropy);
            border-radius: 50%;
            display: inline-block;
            animation: pulse-alert 1.5s ease-in-out infinite;
        }}

        @keyframes pulse-alert {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.6; transform: scale(1.1); }}
        }}

        .alert-item {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
            padding: {self.theme.spacing.get('xs', '0.25rem')} 0;
            line-height: {self.theme.typography.get('lineHeight', {}).get('relaxed', '1.75')};
        }}

        .alert-item:before {{
            content: "→";
            color: var(--widget-entropy);
            margin-right: {self.theme.spacing.get('xs', '0.25rem')};
        }}

        .ai-badge {{
            display: inline-block;
            padding: 2px 6px;
            background: var(--widget-entropy);
            color: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('sm', '0.25rem')};
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            margin-left: {self.theme.spacing.get('xs', '0.25rem')};
        }}
    </style>

    <div class="widget-header">
        <div>
            <h2 class="widget-title">
                Predictive Maintenance
                <span class="ai-badge">AI</span>
            </h2>
        </div>
        {self._render_next_maintenance()}
    </div>

    <div class="components-list">
        {self._render_components()}
    </div>

    {self._render_alerts()}
</div>
"""
        return html

    def _render_next_maintenance(self) -> str:
        """Render next scheduled maintenance"""
        if self.next_maintenance:
            return f'''
                <div class="next-maintenance">
                    Next Scheduled:
                    <span class="next-maintenance-date">{self.next_maintenance}</span>
                </div>
            '''
        return ''

    def _render_components(self) -> str:
        """Render component health list"""
        if not self.components:
            return '<p style="color: var(--widget-text-secondary); text-align: center;">No component data available</p>'

        components_html = []
        for comp in self.components:
            health = comp.get('health', 0)
            color = self._get_health_color(health)
            # Lighter version for gradient
            color_light = color.replace(')', ', 0.6)').replace('rgb', 'rgba').replace('#', 'rgba(')

            component_html = f'''
                <div class="component-item" style="--component-color: {color}; --component-color-light: {color};">
                    <div class="component-header">
                        <span class="component-name">{comp.get('name', 'Unknown')}</span>
                        <span class="component-health">{health}%</span>
                    </div>
                    <div class="health-bar">
                        <div class="health-bar-fill" style="width: {health}%;"></div>
                    </div>
                    <div class="component-details">
                        <div class="detail-item">
                            <span class="detail-label">Time to Failure</span>
                            <span class="detail-value">{comp.get('ttf', 'Unknown')}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Confidence</span>
                            <span class="detail-value">{comp.get('confidence', 0)}%</span>
                        </div>
                    </div>
                </div>
            '''
            components_html.append(component_html)

        return '\n'.join(components_html)

    def _render_alerts(self) -> str:
        """Render maintenance alerts"""
        if not self.maintenance_alerts:
            return ''

        alerts_html = []
        for alert in self.maintenance_alerts:
            alerts_html.append(f'<div class="alert-item">{alert}</div>')

        return f'''
            <div class="alerts-section">
                <div class="alerts-title">
                    <span class="alerts-icon"></span>
                    Maintenance Recommendations
                </div>
                {''.join(alerts_html)}
            </div>
        '''
