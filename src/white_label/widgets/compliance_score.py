"""
Compliance Score Widget

Displays compliance status for NIST, ISO, GDPR, SOC 2
Shows compliance score, framework statuses, and recommendations
"""

from typing import Dict, Any, List
from .widget_sdk import WidgetBase, WidgetConfig


class ComplianceScoreWidget(WidgetBase):
    """
    Compliance monitoring widget showing:
    - Overall compliance score
    - Individual framework status (NIST, ISO, GDPR, SOC 2)
    - Compliance trends
    - Actionable recommendations
    """

    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self.overall_score = 0
        self.frameworks = {
            'NIST': {'score': 0, 'status': 'unknown'},
            'ISO27001': {'score': 0, 'status': 'unknown'},
            'GDPR': {'score': 0, 'status': 'unknown'},
            'SOC2': {'score': 0, 'status': 'unknown'}
        }
        self.recommendations = []

    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch compliance data from API"""
        return {
            'overall_score': self.overall_score,
            'frameworks': self.frameworks,
            'recommendations': self.recommendations
        }

    async def on_data_update(self, data: Dict[str, Any]):
        """Update compliance data"""
        self.overall_score = data.get('overall_score', 0)
        self.frameworks = data.get('frameworks', self.frameworks)
        self.recommendations = data.get('recommendations', [])
        self.emit('data-updated', data)

    def _get_status_color(self, score: int) -> str:
        """Get color based on compliance score"""
        if score >= 90:
            return self.theme.colors.get('proof', {}).get('value', '#2ECC71')
        elif score >= 70:
            return self.theme.colors.get('accent', {}).get('value', '#FF6B35')
        else:
            return self.theme.colors.get('alert', {}).get('value', '#E74C3C')

    async def render(self) -> str:
        """Render Compliance Score widget"""
        css_vars = self.get_css_variables()
        overall_color = self._get_status_color(self.overall_score)

        html = f"""
<div class="compliance-score-widget" data-widget-id="{self.config.widget_id}">
    <style>
        .compliance-score-widget {{
            {css_vars}
            --widget-proof: {self.theme.colors.get('proof', {}).get('value', '#2ECC71')};
            --widget-alert: {self.theme.colors.get('alert', {}).get('value', '#E74C3C')};

            font-family: {self.theme.typography.get('fontFamily', {}).get('primary', 'Inter, sans-serif')};
            background: var(--widget-surface);
            border-radius: {self.theme.borders.get('radius', {}).get('lg', '0.5rem')};
            padding: var(--widget-spacing-lg);
            box-shadow: {self.theme.shadows.get('md', '0 4px 6px -1px rgba(0, 0, 0, 0.3)')};
            color: var(--widget-text-primary);
            min-width: 280px;
            max-width: 400px;
        }}

        .widget-header {{
            text-align: center;
            margin-bottom: var(--widget-spacing-lg);
        }}

        .widget-title {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xl', '1.25rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: var(--widget-accent);
            margin-bottom: var(--widget-spacing-md);
        }}

        .score-circle {{
            width: 120px;
            height: 120px;
            margin: 0 auto;
            border-radius: 50%;
            border: 8px solid {overall_color};
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            background: var(--widget-background);
            box-shadow: 0 0 20px rgba(255, 107, 53, 0.3);
            animation: pulse-score 2.4s ease-in-out infinite;
        }}

        @keyframes pulse-score {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}

        .score-value {{
            font-size: {self.theme.typography.get('fontSize', {}).get('4xl', '2.25rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: {overall_color};
        }}

        .score-label {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
            text-transform: uppercase;
        }}

        .frameworks-list {{
            margin-top: var(--widget-spacing-lg);
        }}

        .framework-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--widget-spacing-sm);
            margin-bottom: var(--widget-spacing-sm);
            background: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            border-left: {self.theme.borders.get('width', {}).get('thick', '4px')} solid var(--framework-color);
        }}

        .framework-name {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('medium', '500')};
            color: var(--widget-text-primary);
        }}

        .framework-score {{
            font-size: {self.theme.typography.get('fontSize', {}).get('lg', '1.125rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: var(--framework-color);
        }}

        .recommendations {{
            margin-top: var(--widget-spacing-lg);
            padding-top: var(--widget-spacing-md);
            border-top: 1px solid var(--widget-primary);
        }}

        .recommendations-title {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
            color: var(--widget-text-primary);
            margin-bottom: var(--widget-spacing-sm);
        }}

        .recommendation-item {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
            padding: {self.theme.spacing.get('xs', '0.25rem')} 0;
            line-height: {self.theme.typography.get('lineHeight', {}).get('relaxed', '1.75')};
        }}

        .recommendation-item:before {{
            content: "•";
            color: var(--widget-accent);
            margin-right: {self.theme.spacing.get('xs', '0.25rem')};
        }}
    </style>

    <div class="widget-header">
        <h2 class="widget-title">Compliance Status</h2>
        <div class="score-circle">
            <div class="score-value">{self.overall_score}</div>
            <div class="score-label">Overall</div>
        </div>
    </div>

    <div class="frameworks-list">
        {self._render_frameworks()}
    </div>

    <div class="recommendations">
        <div class="recommendations-title">Key Actions</div>
        {self._render_recommendations()}
    </div>
</div>
"""
        return html

    def _render_frameworks(self) -> str:
        """Render framework status items"""
        items_html = []
        for name, data in self.frameworks.items():
            score = data.get('score', 0)
            color = self._get_status_color(score)
            item = f'''
                <div class="framework-item" style="--framework-color: {color}">
                    <span class="framework-name">{name}</span>
                    <span class="framework-score">{score}%</span>
                </div>
            '''
            items_html.append(item)
        return '\n'.join(items_html)

    def _render_recommendations(self) -> str:
        """Render compliance recommendations"""
        if not self.recommendations:
            return '<div class="recommendation-item">All compliance checks passed</div>'

        recs_html = []
        for rec in self.recommendations[:5]:  # Show top 5
            recs_html.append(f'<div class="recommendation-item">{rec}</div>')
        return '\n'.join(recs_html)
