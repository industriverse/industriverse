"""
Shadow Twin 3D Widget

Interactive 3D visualization of system digital twin
Real-time system state with spatial representation
"""

from typing import Dict, Any, List
from .widget_sdk import WidgetBase, WidgetConfig


class ShadowTwin3DWidget(WidgetBase):
    """
    3D Shadow Twin widget showing:
    - Interactive 3D system model
    - Real-time component states
    - Spatial relationships and dependencies
    - Energy flow visualization
    - Anomaly highlighting
    - Click-to-drill-down navigation
    """

    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self.nodes = []
        self.connections = []
        self.active_node = None

    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch shadow twin data"""
        return {
            'nodes': self.nodes,
            'connections': self.connections,
            'active_node': self.active_node
        }

    async def on_data_update(self, data: Dict[str, Any]):
        """Update shadow twin visualization"""
        self.nodes = data.get('nodes', [])
        self.connections = data.get('connections', [])
        self.active_node = data.get('active_node')
        self.emit('data-updated', data)

    async def render(self) -> str:
        """Render Shadow Twin 3D widget"""
        css_vars = self.get_css_variables()

        # Generate sample nodes if none provided
        if not self.nodes:
            import random
            self.nodes = [
                {
                    'id': i,
                    'name': f'Component {i+1}',
                    'type': random.choice(['compute', 'storage', 'network', 'sensor']),
                    'status': random.choice(['healthy', 'warning', 'critical']),
                    'x': random.randint(10, 90),
                    'y': random.randint(10, 90),
                    'z': random.randint(0, 100)
                }
                for i in range(12)
            ]

        html = f"""
<div class="shadow-twin-3d-widget" data-widget-id="{self.config.widget_id}">
    <style>
        .shadow-twin-3d-widget {{
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
            min-width: 500px;
            max-width: 900px;
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

        .view-controls {{
            display: flex;
            gap: {self.theme.spacing.get('xs', '0.25rem')};
        }}

        .control-btn {{
            padding: {self.theme.spacing.get('xs', '0.25rem')} {self.theme.spacing.get('sm', '0.5rem')};
            background: var(--widget-background);
            border: 1px solid var(--widget-primary);
            border-radius: {self.theme.borders.get('radius', {}).get('sm', '0.25rem')};
            color: var(--widget-text-secondary);
            cursor: pointer;
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            transition: all 0.2s ease;
        }}

        .control-btn:hover {{
            background: var(--widget-primary);
            color: var(--widget-text-primary);
        }}

        .control-btn.active {{
            background: var(--widget-accent);
            color: var(--widget-background);
            border-color: var(--widget-accent);
        }}

        .twin-canvas {{
            position: relative;
            width: 100%;
            height: 400px;
            background: linear-gradient(135deg, var(--widget-background) 0%, #0A0A0F 100%);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            overflow: hidden;
            border: 1px solid var(--widget-primary);
            perspective: 1000px;
        }}

        .twin-scene {{
            position: relative;
            width: 100%;
            height: 100%;
            transform-style: preserve-3d;
            animation: rotate-scene 60s linear infinite;
        }}

        @keyframes rotate-scene {{
            from {{ transform: rotateY(0deg) rotateX(10deg); }}
            to {{ transform: rotateY(360deg) rotateX(10deg); }}
        }}

        .twin-scene:hover {{
            animation-play-state: paused;
        }}

        .twin-node {{
            position: absolute;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            transform-style: preserve-3d;
            box-shadow: 0 0 20px currentColor;
            animation: float 3s ease-in-out infinite;
        }}

        @keyframes float {{
            0%, 100% {{ transform: translateZ(0); }}
            50% {{ transform: translateZ(20px); }}
        }}

        .twin-node:hover {{
            transform: scale(1.5) !important;
            z-index: 100;
        }}

        .twin-node.healthy {{
            background: var(--widget-proof);
            color: var(--widget-proof);
        }}

        .twin-node.warning {{
            background: var(--widget-accent);
            color: var(--widget-accent);
        }}

        .twin-node.critical {{
            background: var(--widget-alert);
            color: var(--widget-alert);
            animation: critical-pulse 1s ease-in-out infinite;
        }}

        @keyframes critical-pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}

        .node-icon {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-background);
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
        }}

        .node-label {{
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            margin-top: {self.theme.spacing.get('xs', '0.25rem')};
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
            white-space: nowrap;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .twin-node:hover .node-label {{
            opacity: 1;
        }}

        .connection-line {{
            position: absolute;
            height: 2px;
            background: linear-gradient(90deg, var(--widget-primary), transparent);
            opacity: 0.3;
            transform-origin: 0 0;
            pointer-events: none;
            animation: flow 3s linear infinite;
        }}

        @keyframes flow {{
            0% {{ background-position: 0 0; }}
            100% {{ background-position: 100px 0; }}
        }}

        .grid-overlay {{
            position: absolute;
            width: 100%;
            height: 100%;
            background:
                linear-gradient(90deg, rgba(10, 75, 92, 0.1) 1px, transparent 1px),
                linear-gradient(rgba(10, 75, 92, 0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            opacity: 0.5;
            pointer-events: none;
        }}

        .stats-panel {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: var(--widget-spacing-sm);
            margin-top: var(--widget-spacing-md);
        }}

        .stat-card {{
            background: var(--widget-background);
            padding: var(--widget-spacing-sm);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            text-align: center;
            border-left: {self.theme.borders.get('width', {}).get('medium', '2px')} solid var(--stat-color);
        }}

        .stat-value {{
            font-size: {self.theme.typography.get('fontSize', {}).get('lg', '1.125rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
            color: var(--stat-color);
        }}

        .stat-label {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
            text-transform: uppercase;
        }}

        .detail-panel {{
            position: absolute;
            top: var(--widget-spacing-md);
            right: var(--widget-spacing-md);
            background: var(--widget-surface);
            border: 1px solid var(--widget-accent);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            padding: var(--widget-spacing-md);
            box-shadow: {self.theme.shadows.get('xl', '0 20px 25px -5px rgba(0, 0, 0, 0.3)')};
            min-width: 200px;
            display: none;
            z-index: 200;
        }}

        .detail-panel.visible {{
            display: block;
            animation: slide-in 0.3s ease-out;
        }}

        @keyframes slide-in {{
            from {{
                opacity: 0;
                transform: translateX(20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        .detail-title {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
            color: var(--widget-accent);
            margin-bottom: var(--widget-spacing-sm);
        }}

        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: {self.theme.spacing.get('xs', '0.25rem')} 0;
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            border-bottom: 1px solid var(--widget-primary);
        }}

        .detail-row:last-child {{
            border-bottom: none;
        }}
    </style>

    <div class="widget-header">
        <h2 class="widget-title">Shadow Twin</h2>
        <div class="view-controls">
            <button class="control-btn active" data-view="3d">3D</button>
            <button class="control-btn" data-view="grid">Grid</button>
            <button class="control-btn" data-view="graph">Graph</button>
        </div>
    </div>

    <div class="twin-canvas">
        <div class="grid-overlay"></div>
        <div class="twin-scene" id="twin-scene-{self.config.widget_id}">
            {self._render_nodes()}
            {self._render_connections()}
        </div>
        <div class="detail-panel" id="detail-panel-{self.config.widget_id}">
            <div class="detail-title">Component Details</div>
            <div id="detail-content-{self.config.widget_id}"></div>
        </div>
    </div>

    <div class="stats-panel">
        {self._render_stats()}
    </div>

    <script>
        (function() {{
            const scene = document.getElementById('twin-scene-{self.config.widget_id}');
            const detailPanel = document.getElementById('detail-panel-{self.config.widget_id}');
            const detailContent = document.getElementById('detail-content-{self.config.widget_id}');
            const nodes = scene.querySelectorAll('.twin-node');

            nodes.forEach(node => {{
                node.addEventListener('click', (e) => {{
                    e.stopPropagation();
                    const nodeData = {{
                        name: node.dataset.name,
                        type: node.dataset.type,
                        status: node.dataset.status
                    }};

                    detailContent.innerHTML = `
                        <div class="detail-row">
                            <span>Name:</span>
                            <span>${{nodeData.name}}</span>
                        </div>
                        <div class="detail-row">
                            <span>Type:</span>
                            <span>${{nodeData.type}}</span>
                        </div>
                        <div class="detail-row">
                            <span>Status:</span>
                            <span>${{nodeData.status}}</span>
                        </div>
                    `;

                    detailPanel.classList.add('visible');
                }});
            }});

            document.addEventListener('click', (e) => {{
                if (!detailPanel.contains(e.target) && !e.target.closest('.twin-node')) {{
                    detailPanel.classList.remove('visible');
                }}
            }});

            // View controls
            const controls = document.querySelectorAll('.control-btn');
            controls.forEach(btn => {{
                btn.addEventListener('click', () => {{
                    controls.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    // View switching logic would go here
                }});
            }});
        }})();
    </script>
</div>
"""
        return html

    def _render_nodes(self) -> str:
        """Render 3D nodes"""
        nodes_html = []
        for node in self.nodes:
            x = node.get('x', 50)
            y = node.get('y', 50)
            z = node.get('z', 50)
            status = node.get('status', 'healthy')
            name = node.get('name', 'Node')
            node_type = node.get('type', 'compute')

            # Icon mapping
            icons = {
                'compute': '⚡',
                'storage': '💾',
                'network': '🔗',
                'sensor': '📡'
            }

            nodes_html.append(f'''
                <div class="twin-node {status}"
                     style="left: {x}%; top: {y}%; transform: translateZ({z}px);"
                     data-name="{name}"
                     data-type="{node_type}"
                     data-status="{status}">
                    <span class="node-icon">{icons.get(node_type, '•')}</span>
                    <div class="node-label">{name}</div>
                </div>
            ''')

        return '\n'.join(nodes_html)

    def _render_connections(self) -> str:
        """Render connections between nodes"""
        # Simplified connection rendering
        # In production, calculate actual positions
        return ''

    def _render_stats(self) -> str:
        """Render system statistics"""
        healthy = sum(1 for n in self.nodes if n.get('status') == 'healthy')
        warning = sum(1 for n in self.nodes if n.get('status') == 'warning')
        critical = sum(1 for n in self.nodes if n.get('status') == 'critical')
        total = len(self.nodes)

        return f'''
            <div class="stat-card" style="--stat-color: var(--widget-proof);">
                <div class="stat-value">{healthy}</div>
                <div class="stat-label">Healthy</div>
            </div>
            <div class="stat-card" style="--stat-color: var(--widget-accent);">
                <div class="stat-value">{warning}</div>
                <div class="stat-label">Warning</div>
            </div>
            <div class="stat-card" style="--stat-color: var(--widget-alert);">
                <div class="stat-value">{critical}</div>
                <div class="stat-label">Critical</div>
            </div>
            <div class="stat-card" style="--stat-color: var(--widget-primary);">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Total</div>
            </div>
        '''
