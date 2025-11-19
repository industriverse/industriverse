"""
Energy Flow Graph Widget

Operational thermodynamics visualization showing energy consumption,
waste heat, and efficiency metrics across system components
"""

from typing import Dict, Any, List
from .widget_sdk import WidgetBase, WidgetConfig


class EnergyFlowGraphWidget(WidgetBase):
    """
    Energy flow visualization showing:
    - Power consumption by component
    - Thermal dissipation
    - Efficiency metrics
    - Temporal energy trends
    - Anomaly detection
    """

    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self.energy_data = []
        self.total_power = 0.0
        self.efficiency = 0.0
        self.anomalies_detected = 0

    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch energy flow data"""
        return {
            'energy_data': self.energy_data,
            'total_power': self.total_power,
            'efficiency': self.efficiency,
            'anomalies_detected': self.anomalies_detected
        }

    async def on_data_update(self, data: Dict[str, Any]):
        """Update energy flow data"""
        self.energy_data = data.get('energy_data', [])
        self.total_power = data.get('total_power', 0.0)
        self.efficiency = data.get('efficiency', 0.0)
        self.anomalies_detected = data.get('anomalies_detected', 0)
        self.emit('data-updated', data)

    async def render(self) -> str:
        """Render Energy Flow Graph widget"""
        css_vars = self.get_css_variables()

        # Generate sample data if none provided
        if not self.energy_data:
            import random
            self.energy_data = [
                {'time': f'{i}s', 'value': 200 + random.randint(-50, 50)}
                for i in range(20)
            ]
            self.total_power = 250.5
            self.efficiency = 87.3

        html = f"""
<div class="energy-flow-widget" data-widget-id="{self.config.widget_id}">
    <style>
        .energy-flow-widget {{
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
            min-width: 400px;
            max-width: 700px;
        }}

        .widget-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--widget-spacing-lg);
        }}

        .widget-title {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xl', '1.25rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: var(--widget-accent);
        }}

        .efficiency-badge {{
            padding: {self.theme.spacing.get('xs', '0.25rem')} {self.theme.spacing.get('sm', '0.5rem')};
            background: {self._get_efficiency_color()};
            color: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('full', '9999px')};
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
        }}

        .graph-container {{
            position: relative;
            width: 100%;
            height: 200px;
            background: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            padding: var(--widget-spacing-md);
            margin-bottom: var(--widget-spacing-lg);
            overflow: hidden;
        }}

        .graph-svg {{
            width: 100%;
            height: 100%;
        }}

        .energy-line {{
            fill: none;
            stroke: var(--widget-accent);
            stroke-width: 2;
            filter: drop-shadow(0 0 8px var(--widget-accent));
            animation: draw-line 2s ease-out;
        }}

        @keyframes draw-line {{
            from {{
                stroke-dasharray: 1000;
                stroke-dashoffset: 1000;
            }}
            to {{
                stroke-dasharray: 1000;
                stroke-dashoffset: 0;
            }}
        }}

        .energy-fill {{
            fill: url(#energy-gradient);
            opacity: 0.3;
        }}

        .grid-line {{
            stroke: var(--widget-primary);
            stroke-width: 0.5;
            opacity: 0.3;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--widget-spacing-md);
        }}

        .metric-card {{
            background: var(--widget-background);
            border-left: {self.theme.borders.get('width', {}).get('thick', '4px')} solid var(--metric-color);
            padding: var(--widget-spacing-sm) var(--widget-spacing-md);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
        }}

        .metric-label {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
            text-transform: uppercase;
            margin-bottom: {self.theme.spacing.get('xs', '0.25rem')};
        }}

        .metric-value {{
            font-size: {self.theme.typography.get('fontSize', {}).get('2xl', '1.5rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: var(--metric-color);
        }}

        .metric-unit {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            color: var(--widget-text-secondary);
            margin-left: {self.theme.spacing.get('xs', '0.25rem')};
        }}

        .anomaly-indicator {{
            display: flex;
            align-items: center;
            gap: {self.theme.spacing.get('xs', '0.25rem')};
            margin-top: var(--widget-spacing-md);
            padding: var(--widget-spacing-sm);
            background: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            border-left: {self.theme.borders.get('width', {}).get('thick', '4px')} solid var(--widget-entropy);
        }}

        .anomaly-icon {{
            width: 16px;
            height: 16px;
            background: var(--widget-entropy);
            border-radius: 50%;
            animation: blink 1.5s ease-in-out infinite;
        }}

        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.3; }}
        }}

        .anomaly-text {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            color: var(--widget-text-primary);
        }}
    </style>

    <div class="widget-header">
        <h2 class="widget-title">Energy Flow</h2>
        <span class="efficiency-badge">{self.efficiency:.1f}% Efficiency</span>
    </div>

    <div class="graph-container">
        <svg class="graph-svg" viewBox="0 0 600 150" preserveAspectRatio="none">
            <defs>
                <linearGradient id="energy-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:{self.theme.colors.get('accent', {}).get('value', '#FF6B35')};stop-opacity:0.6" />
                    <stop offset="100%" style="stop-color:{self.theme.colors.get('accent', {}).get('value', '#FF6B35')};stop-opacity:0.1" />
                </linearGradient>
            </defs>

            <!-- Grid lines -->
            {self._render_grid_lines()}

            <!-- Energy flow line and fill -->
            {self._render_energy_path()}
        </svg>
    </div>

    <div class="metrics-grid">
        <div class="metric-card" style="--metric-color: var(--widget-accent);">
            <div class="metric-label">Total Power</div>
            <div class="metric-value">{self.total_power:.1f}<span class="metric-unit">W</span></div>
        </div>
        <div class="metric-card" style="--metric-color: var(--widget-proof);">
            <div class="metric-label">Efficiency</div>
            <div class="metric-value">{self.efficiency:.1f}<span class="metric-unit">%</span></div>
        </div>
        <div class="metric-card" style="--metric-color: var(--widget-entropy);">
            <div class="metric-label">Waste Heat</div>
            <div class="metric-value">{self.total_power * (1 - self.efficiency/100):.1f}<span class="metric-unit">W</span></div>
        </div>
    </div>

    {self._render_anomaly_indicator()}
</div>
"""
        return html

    def _get_efficiency_color(self) -> str:
        """Get color based on efficiency"""
        if self.efficiency >= 80:
            return self.theme.colors.get('proof', {}).get('value', '#2ECC71')
        elif self.efficiency >= 60:
            return self.theme.colors.get('accent', {}).get('value', '#FF6B35')
        else:
            return self.theme.colors.get('alert', {}).get('value', '#E74C3C')

    def _render_grid_lines(self) -> str:
        """Render SVG grid lines"""
        lines = []
        for i in range(5):
            y = i * 37.5  # 150 / 4
            lines.append(f'<line class="grid-line" x1="0" y1="{y}" x2="600" y2="{y}" />')
        return '\n'.join(lines)

    def _render_energy_path(self) -> str:
        """Render energy flow path"""
        if not self.energy_data:
            return ''

        # Calculate points
        width = 600
        height = 150
        step = width / max(len(self.energy_data) - 1, 1)

        values = [d['value'] for d in self.energy_data]
        max_value = max(values) if values else 1
        min_value = min(values) if values else 0
        value_range = max_value - min_value if max_value != min_value else 1

        # Generate path
        line_points = []
        fill_points = []

        for i, data_point in enumerate(self.energy_data):
            x = i * step
            normalized = (data_point['value'] - min_value) / value_range
            y = height - (normalized * (height * 0.8) + height * 0.1)

            line_points.append(f"{x},{y}")
            if i == 0:
                fill_points.append(f"{x},{height}")
            fill_points.append(f"{x},{y}")
            if i == len(self.energy_data) - 1:
                fill_points.append(f"{x},{height}")

        line_path = "M " + " L ".join(line_points)
        fill_path = "M " + " L ".join(fill_points) + " Z"

        return f'''
            <path class="energy-fill" d="{fill_path}" />
            <path class="energy-line" d="{line_path}" />
        '''

    def _render_anomaly_indicator(self) -> str:
        """Render anomaly detection indicator"""
        if self.anomalies_detected > 0:
            return f'''
                <div class="anomaly-indicator">
                    <div class="anomaly-icon"></div>
                    <span class="anomaly-text">
                        {self.anomalies_detected} energy anomal{'y' if self.anomalies_detected == 1 else 'ies'} detected
                    </span>
                </div>
            '''
        return ''
