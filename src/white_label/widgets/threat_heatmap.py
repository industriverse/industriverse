"""
Threat Heatmap Widget

Thermodynamic visualization of security threats across system topology
Uses color intensity to show threat density and severity
"""

from typing import Dict, Any, List
from .widget_sdk import WidgetBase, WidgetConfig


class ThreatHeatmapWidget(WidgetBase):
    """
    Threat heatmap visualization showing:
    - System topology with threat overlays
    - Thermodynamic color mapping (cool to hot)
    - Interactive threat zones
    - Temporal threat evolution
    """

    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self.threat_zones = []
        self.max_severity = 0

    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch threat heatmap data"""
        return {
            'threat_zones': self.threat_zones,
            'max_severity': self.max_severity
        }

    async def on_data_update(self, data: Dict[str, Any]):
        """Update heatmap data"""
        self.threat_zones = data.get('threat_zones', [])
        self.max_severity = data.get('max_severity', 0)
        self.emit('data-updated', data)

    def _get_heat_color(self, severity: float) -> str:
        """Calculate thermodynamic color based on severity"""
        # Cool (blue/green) to hot (orange/red) gradient
        if severity < 0.3:
            return self.theme.colors.get('proof', {}).get('value', '#2ECC71')  # Green (safe)
        elif severity < 0.6:
            return self.theme.colors.get('accent', {}).get('value', '#FF6B35')  # Orange (warm)
        else:
            return self.theme.colors.get('alert', {}).get('value', '#E74C3C')  # Red (hot)

    async def render(self) -> str:
        """Render Threat Heatmap widget"""
        css_vars = self.get_css_variables()

        html = f"""
<div class="threat-heatmap-widget" data-widget-id="{self.config.widget_id}">
    <style>
        .threat-heatmap-widget {{
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
            max-width: 800px;
        }}

        .heatmap-header {{
            margin-bottom: var(--widget-spacing-lg);
        }}

        .heatmap-title {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xl', '1.25rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: var(--widget-accent);
        }}

        .heatmap-canvas {{
            position: relative;
            width: 100%;
            height: 300px;
            background: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            overflow: hidden;
            border: 1px solid var(--widget-primary);
        }}

        .threat-zone {{
            position: absolute;
            border-radius: 50%;
            opacity: 0.6;
            transition: all 0.3s ease;
            cursor: pointer;
            animation: threat-pulse 2s ease-in-out infinite;
        }}

        .threat-zone:hover {{
            opacity: 0.9;
            transform: scale(1.1);
            z-index: 10;
        }}

        @keyframes threat-pulse {{
            0%, 100% {{ box-shadow: 0 0 0 0 currentColor; }}
            50% {{ box-shadow: 0 0 20px 10px currentColor; }}
        }}

        .legend {{
            display: flex;
            justify-content: space-around;
            margin-top: var(--widget-spacing-md);
            padding: var(--widget-spacing-sm);
            background: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: {self.theme.spacing.get('xs', '0.25rem')};
        }}

        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
        }}

        .legend-label {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--widget-spacing-sm);
            margin-top: var(--widget-spacing-md);
        }}

        .stat-card {{
            background: var(--widget-background);
            padding: var(--widget-spacing-sm);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            text-align: center;
        }}

        .stat-value {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xl', '1.25rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: var(--widget-accent);
        }}

        .stat-label {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
        }}

        .tooltip {{
            position: absolute;
            background: var(--widget-surface);
            border: 1px solid var(--widget-accent);
            border-radius: {self.theme.borders.get('radius', {}).get('sm', '0.25rem')};
            padding: {self.theme.spacing.get('xs', '0.25rem')} {self.theme.spacing.get('sm', '0.5rem')};
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            pointer-events: none;
            z-index: 100;
            display: none;
        }}
    </style>

    <div class="heatmap-header">
        <h2 class="heatmap-title">Threat Topology</h2>
    </div>

    <div class="heatmap-canvas" id="heatmap-canvas-{self.config.widget_id}">
        {self._render_threat_zones()}
        <div class="tooltip" id="tooltip-{self.config.widget_id}"></div>
    </div>

    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: {self.theme.colors.get('proof', {}).get('value', '#2ECC71')};"></div>
            <span class="legend-label">Low</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: {self.theme.colors.get('accent', {}).get('value', '#FF6B35')};"></div>
            <span class="legend-label">Medium</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: {self.theme.colors.get('alert', {}).get('value', '#E74C3C')};"></div>
            <span class="legend-label">High</span>
        </div>
    </div>

    <div class="stats">
        {self._render_stats()}
    </div>

    <script>
        (function() {{
            const canvas = document.getElementById('heatmap-canvas-{self.config.widget_id}');
            const tooltip = document.getElementById('tooltip-{self.config.widget_id}');

            canvas.addEventListener('mousemove', (e) => {{
                const zone = e.target.closest('.threat-zone');
                if (zone) {{
                    tooltip.style.display = 'block';
                    tooltip.style.left = e.offsetX + 10 + 'px';
                    tooltip.style.top = e.offsetY + 10 + 'px';
                    tooltip.textContent = zone.dataset.info;
                }} else {{
                    tooltip.style.display = 'none';
                }}
            }});
        }})();
    </script>
</div>
"""
        return html

    def _render_threat_zones(self) -> str:
        """Render threat zones on heatmap"""
        if not self.threat_zones:
            # Generate sample zones for demo
            import random
            zones_html = []
            for i in range(8):
                severity = random.random()
                x = random.randint(10, 80)
                y = random.randint(10, 80)
                size = 40 + severity * 60
                color = self._get_heat_color(severity)

                zones_html.append(f'''
                    <div class="threat-zone"
                         style="left: {x}%; top: {y}%; width: {size}px; height: {size}px; background: {color}; color: {color};"
                         data-info="Threat Level: {severity:.2f} | Zone {i+1}">
                    </div>
                ''')
            return '\n'.join(zones_html)

        zones_html = []
        for zone in self.threat_zones:
            severity = zone.get('severity', 0)
            x = zone.get('x', 50)
            y = zone.get('y', 50)
            size = 30 + severity * 70
            color = self._get_heat_color(severity)

            zones_html.append(f'''
                <div class="threat-zone"
                     style="left: {x}%; top: {y}%; width: {size}px; height: {size}px; background: {color}; color: {color};"
                     data-info="{zone.get('info', 'Threat Zone')}">
                </div>
            ''')
        return '\n'.join(zones_html)

    def _render_stats(self) -> str:
        """Render threat statistics"""
        total_zones = len(self.threat_zones) if self.threat_zones else 8
        high_severity = sum(1 for z in self.threat_zones if z.get('severity', 0) > 0.6) if self.threat_zones else 2

        return f'''
            <div class="stat-card">
                <div class="stat-value">{total_zones}</div>
                <div class="stat-label">Active Zones</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{high_severity}</div>
                <div class="stat-label">Critical</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.max_severity:.1f}</div>
                <div class="stat-label">Max Severity</div>
            </div>
        '''
