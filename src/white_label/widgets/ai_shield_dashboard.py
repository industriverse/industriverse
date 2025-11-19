"""
AI Shield Dashboard Widget

Real-time threat monitoring and security status display.
Shows active threats, security score, and recent events.
"""

from typing import Dict, Any
import json
from .widget_sdk import WidgetBase, WidgetConfig


class AIShieldDashboardWidget(WidgetBase):
    """
    Main security dashboard widget showing:
    - Real-time threat count
    - Security health score
    - Active alerts
    - Recent security events
    - System status indicators
    """

    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self.threat_count = 0
        self.security_score = 100
        self.active_alerts = []
        self.recent_events = []

    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch security dashboard data from API"""
        # API call would go here
        # For now, returning mock structure
        return {
            'threat_count': self.threat_count,
            'security_score': self.security_score,
            'active_alerts': self.active_alerts,
            'recent_events': self.recent_events,
            'system_status': 'operational'
        }

    async def on_data_update(self, data: Dict[str, Any]):
        """Update dashboard with new data"""
        self.threat_count = data.get('threat_count', 0)
        self.security_score = data.get('security_score', 100)
        self.active_alerts = data.get('active_alerts', [])
        self.recent_events = data.get('recent_events', [])

        self.emit('data-updated', data)

        # Trigger re-render if animations enabled
        if self.config.enable_animations:
            await self.render()

    async def render(self) -> str:
        """Render AI Shield Dashboard widget"""
        css_vars = self.get_css_variables()

        # Get animation settings from theme
        pulse_duration = self.theme.motion.get('animations', {}).get('pulse_energy', {}).get('duration', '2.4s')
        threat_duration = self.theme.motion.get('animations', {}).get('threat_alert', {}).get('duration', '800ms')

        # Determine status color based on security score
        status_color = 'var(--widget-proof)' if self.security_score > 80 else \
                      'var(--widget-accent)' if self.security_score > 50 else \
                      'var(--widget-alert)'

        html = f"""
<div class="ai-shield-dashboard" data-widget-id="{self.config.widget_id}">
    <style>
        .ai-shield-dashboard {{
            {css_vars}
            --widget-proof: {self.theme.colors.get('proof', {}).get('value', '#2ECC71')};
            --widget-alert: {self.theme.colors.get('alert', {}).get('value', '#E74C3C')};
            --widget-entropy: {self.theme.colors.get('entropy', {}).get('value', '#9B59B6')};

            font-family: {self.theme.typography.get('fontFamily', {}).get('primary', 'Inter, sans-serif')};
            background: var(--widget-surface);
            border-radius: {self.theme.borders.get('radius', {}).get('lg', '0.5rem')};
            padding: var(--widget-spacing-lg);
            box-shadow: {self.theme.shadows.get('lg', '0 10px 15px -3px rgba(0, 0, 0, 0.3)')};
            color: var(--widget-text-primary);
            min-width: 320px;
            max-width: 600px;
        }}

        .dashboard-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--widget-spacing-lg);
            border-bottom: 2px solid var(--widget-primary);
            padding-bottom: var(--widget-spacing-md);
        }}

        .dashboard-title {{
            font-size: {self.theme.typography.get('fontSize', {}).get('2xl', '1.5rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: var(--widget-accent);
        }}

        .status-badge {{
            padding: {self.theme.spacing.get('xs', '0.25rem')} {self.theme.spacing.get('sm', '0.5rem')};
            border-radius: {self.theme.borders.get('radius', {}).get('full', '9999px')};
            background: {status_color};
            color: var(--widget-background);
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
            animation: pulse-status {pulse_duration} ease-in-out infinite;
        }}

        @keyframes pulse-status {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: var(--widget-spacing-md);
            margin-bottom: var(--widget-spacing-lg);
        }}

        .metric-card {{
            background: var(--widget-background);
            border: {self.theme.borders.get('width', {}).get('thin', '1px')} solid var(--widget-primary);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            padding: var(--widget-spacing-md);
            text-align: center;
        }}

        .metric-value {{
            font-size: {self.theme.typography.get('fontSize', {}).get('3xl', '1.875rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: var(--widget-accent);
            margin-bottom: {self.theme.spacing.get('xs', '0.25rem')};
        }}

        .metric-label {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            color: var(--widget-text-secondary);
        }}

        .alerts-section {{
            margin-top: var(--widget-spacing-lg);
        }}

        .section-title {{
            font-size: {self.theme.typography.get('fontSize', {}).get('lg', '1.125rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
            margin-bottom: var(--widget-spacing-sm);
            color: var(--widget-text-primary);
        }}

        .alert-item {{
            background: var(--widget-background);
            border-left: {self.theme.borders.get('width', {}).get('thick', '4px')} solid var(--widget-alert);
            padding: var(--widget-spacing-sm) var(--widget-spacing-md);
            margin-bottom: var(--widget-spacing-sm);
            border-radius: {self.theme.borders.get('radius', {}).get('sm', '0.25rem')};
            animation: threat-pulse {threat_duration} ease-in-out infinite;
        }}

        @keyframes threat-pulse {{
            0%, 100% {{ background: var(--widget-background); }}
            50% {{ background: rgba(231, 76, 60, 0.1); }}
        }}

        .alert-message {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            color: var(--widget-text-primary);
        }}

        .events-list {{
            max-height: 200px;
            overflow-y: auto;
        }}

        .event-item {{
            display: flex;
            justify-content: space-between;
            padding: var(--widget-spacing-sm);
            border-bottom: 1px solid var(--widget-primary);
        }}

        .event-item:last-child {{
            border-bottom: none;
        }}

        .event-message {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            color: var(--widget-text-primary);
        }}

        .event-time {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
        }}

        .powered-by {{
            margin-top: var(--widget-spacing-lg);
            text-align: center;
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
        }}
    </style>

    <div class="dashboard-header">
        <h2 class="dashboard-title">AI Shield</h2>
        <span class="status-badge">Score: {self.security_score}</span>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{self.threat_count}</div>
            <div class="metric-label">Active Threats</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(self.active_alerts)}</div>
            <div class="metric-label">Alerts</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(self.recent_events)}</div>
            <div class="metric-label">Recent Events</div>
        </div>
    </div>

    <div class="alerts-section">
        <h3 class="section-title">Active Alerts</h3>
        {self._render_alerts()}
    </div>

    <div class="alerts-section">
        <h3 class="section-title">Recent Events</h3>
        <div class="events-list">
            {self._render_events()}
        </div>
    </div>

    {self._render_branding()}
</div>
"""
        return html

    def _render_alerts(self) -> str:
        """Render active alerts"""
        if not self.active_alerts:
            return '<p class="alert-message" style="color: var(--widget-text-secondary);">No active alerts</p>'

        alerts_html = []
        for alert in self.active_alerts[:5]:  # Show max 5
            alerts_html.append(f'<div class="alert-item"><p class="alert-message">{alert}</p></div>')

        return '\n'.join(alerts_html)

    def _render_events(self) -> str:
        """Render recent events"""
        if not self.recent_events:
            return '<p class="event-message" style="color: var(--widget-text-secondary); padding: var(--widget-spacing-sm);">No recent events</p>'

        events_html = []
        for event in self.recent_events[:10]:  # Show max 10
            events_html.append(f'''
                <div class="event-item">
                    <span class="event-message">{event.get('message', 'Event')}</span>
                    <span class="event-time">{event.get('time', 'Just now')}</span>
                </div>
            ''')

        return '\n'.join(events_html)

    def _render_branding(self) -> str:
        """Render partner branding or default"""
        if self.config.custom_branding:
            logo = self.config.custom_branding.get('logo_url')
            if logo:
                return f'<div class="powered-by"><img src="{logo}" alt="Partner Logo" style="max-height: 32px;"></div>'

        return '<div class="powered-by">Powered by Industriverse AI Shield</div>'
