"""
Security Orb Widget

Ambient threat level indicator with pulsing visual feedback
Minimalist design for at-a-glance security status
"""

from typing import Dict, Any
from .widget_sdk import WidgetBase, WidgetConfig


class SecurityOrbWidget(WidgetBase):
    """
    Ambient security orb showing:
    - Overall system security state (color-coded)
    - Pulsing animation reflecting threat level
    - Minimalist design for peripheral awareness
    - Click-to-expand for details
    """

    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self.threat_level = 0.0  # 0.0 (safe) to 1.0 (critical)
        self.status_text = "Secure"
        self.active_threats = 0

    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch security status data"""
        return {
            'threat_level': self.threat_level,
            'status_text': self.status_text,
            'active_threats': self.active_threats
        }

    async def on_data_update(self, data: Dict[str, Any]):
        """Update security orb state"""
        self.threat_level = data.get('threat_level', 0.0)
        self.status_text = data.get('status_text', 'Secure')
        self.active_threats = data.get('active_threats', 0)
        self.emit('data-updated', data)

    def _get_orb_color(self) -> str:
        """Get orb color based on threat level"""
        if self.threat_level < 0.3:
            return self.theme.colors.get('proof', {}).get('value', '#2ECC71')  # Green
        elif self.threat_level < 0.7:
            return self.theme.colors.get('accent', {}).get('value', '#FF6B35')  # Orange
        else:
            return self.theme.colors.get('alert', {}).get('value', '#E74C3C')  # Red

    def _get_pulse_speed(self) -> str:
        """Get pulse animation speed based on threat level"""
        if self.threat_level < 0.3:
            return "3s"  # Slow, calm
        elif self.threat_level < 0.7:
            return "1.5s"  # Medium
        else:
            return "0.8s"  # Fast, urgent

    async def render(self) -> str:
        """Render Security Orb widget"""
        css_vars = self.get_css_variables()
        orb_color = self._get_orb_color()
        pulse_speed = self._get_pulse_speed()

        html = f"""
<div class="security-orb-widget" data-widget-id="{self.config.widget_id}">
    <style>
        .security-orb-widget {{
            {css_vars}
            font-family: {self.theme.typography.get('fontFamily', {}).get('primary', 'Inter, sans-serif')};
            display: inline-block;
            cursor: pointer;
            user-select: none;
        }}

        .orb-container {{
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: var(--widget-spacing-sm);
        }}

        .orb {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: {orb_color};
            box-shadow:
                0 0 20px {orb_color},
                0 0 40px {orb_color},
                inset 0 0 20px rgba(255, 255, 255, 0.1);
            animation: orb-pulse {pulse_speed} ease-in-out infinite;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .orb:hover {{
            transform: scale(1.1);
            box-shadow:
                0 0 30px {orb_color},
                0 0 60px {orb_color},
                inset 0 0 20px rgba(255, 255, 255, 0.2);
        }}

        @keyframes orb-pulse {{
            0%, 100% {{
                transform: scale(1);
                opacity: 1;
            }}
            50% {{
                transform: scale(1.05);
                opacity: 0.8;
            }}
        }}

        .orb::before {{
            content: '';
            position: absolute;
            top: 10%;
            left: 10%;
            width: 40%;
            height: 40%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.6) 0%, transparent 70%);
            border-radius: 50%;
            animation: shimmer 3s ease-in-out infinite;
        }}

        @keyframes shimmer {{
            0%, 100% {{ opacity: 0.6; }}
            50% {{ opacity: 1; }}
        }}

        .orb-rings {{
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 2px solid {orb_color};
            opacity: 0.3;
            animation: ring-expand {pulse_speed} ease-out infinite;
        }}

        @keyframes ring-expand {{
            0% {{
                transform: scale(1);
                opacity: 0.3;
            }}
            100% {{
                transform: scale(1.8);
                opacity: 0;
            }}
        }}

        .status-label {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('medium', '500')};
            color: {orb_color};
            text-align: center;
        }}

        .threat-count {{
            position: absolute;
            top: -8px;
            right: -8px;
            background: var(--widget-alert);
            color: var(--widget-background);
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            animation: badge-pulse 1s ease-in-out infinite;
        }}

        @keyframes badge-pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}

        .details-panel {{
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            margin-top: var(--widget-spacing-sm);
            background: var(--widget-surface);
            border: 1px solid {orb_color};
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            padding: var(--widget-spacing-md);
            box-shadow: {self.theme.shadows.get('lg', '0 10px 15px -3px rgba(0, 0, 0, 0.3)')};
            display: none;
            min-width: 200px;
            z-index: 1000;
        }}

        .security-orb-widget.expanded .details-panel {{
            display: block;
            animation: slide-down 0.3s ease-out;
        }}

        @keyframes slide-down {{
            from {{
                opacity: 0;
                transform: translateX(-50%) translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateX(-50%) translateY(0);
            }}
        }}

        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: {self.theme.spacing.get('xs', '0.25rem')} 0;
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            color: var(--widget-text-primary);
            border-bottom: 1px solid var(--widget-primary);
        }}

        .detail-row:last-child {{
            border-bottom: none;
        }}

        .detail-label {{
            color: var(--widget-text-secondary);
        }}

        .detail-value {{
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
            color: {orb_color};
        }}
    </style>

    <div class="orb-container">
        <div class="orb">
            <div class="orb-rings"></div>
            {f'<div class="threat-count">{self.active_threats}</div>' if self.active_threats > 0 else ''}
        </div>
        <div class="status-label">{self.status_text}</div>

        <div class="details-panel">
            <div class="detail-row">
                <span class="detail-label">Threat Level</span>
                <span class="detail-value">{int(self.threat_level * 100)}%</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Active Threats</span>
                <span class="detail-value">{self.active_threats}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Status</span>
                <span class="detail-value">{self.status_text}</span>
            </div>
        </div>
    </div>

    <script>
        (function() {{
            const widget = document.querySelector('.security-orb-widget[data-widget-id="{self.config.widget_id}"]');
            const orb = widget.querySelector('.orb');

            orb.addEventListener('click', () => {{
                widget.classList.toggle('expanded');
            }});

            // Close on click outside
            document.addEventListener('click', (e) => {{
                if (!widget.contains(e.target)) {{
                    widget.classList.remove('expanded');
                }}
            }});
        }})();
    </script>
</div>
"""
        return html
