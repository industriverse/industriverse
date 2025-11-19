"""
Research Explorer Widget

Knowledge graph browser for I³ (Industrial Internet of Intelligence)
Enables exploration of research papers, discoveries, and insights
"""

from typing import Dict, Any, List
from .widget_sdk import WidgetBase, WidgetConfig


class ResearchExplorerWidget(WidgetBase):
    """
    Research explorer widget showing:
    - Knowledge graph visualization
    - Paper ingestion from RDR (Real Deep Research)
    - Insight discovery and connections
    - UTID marketplace integration
    - Proof-of-Insight tracking
    - 6D embedding space navigation
    """

    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self.papers = []
        self.insights = []
        self.connections = []
        self.active_topic = None

    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch research and knowledge graph data"""
        return {
            'papers': self.papers,
            'insights': self.insights,
            'connections': self.connections,
            'active_topic': self.active_topic
        }

    async def on_data_update(self, data: Dict[str, Any]):
        """Update research explorer data"""
        self.papers = data.get('papers', [])
        self.insights = data.get('insights', [])
        self.connections = data.get('connections', [])
        self.active_topic = data.get('active_topic')
        self.emit('data-updated', data)

    async def render(self) -> str:
        """Render Research Explorer widget"""
        css_vars = self.get_css_variables()

        # Generate sample data if none provided
        if not self.papers:
            self.papers = [
                {
                    'id': 'paper1',
                    'title': 'Thermodynamic Security Primitives',
                    'authors': 'Smith et al.',
                    'year': 2024,
                    'citations': 45,
                    'insights': 3
                },
                {
                    'id': 'paper2',
                    'title': 'Power Analysis Attack Detection',
                    'authors': 'Johnson et al.',
                    'year': 2023,
                    'citations': 87,
                    'insights': 5
                },
                {
                    'id': 'paper3',
                    'title': 'Quantum-Resistant AI Architectures',
                    'authors': 'Chen et al.',
                    'year': 2024,
                    'citations': 32,
                    'insights': 2
                },
            ]
            self.insights = [
                {
                    'id': 'insight1',
                    'text': 'Entropy-based detection outperforms traditional methods by 40%',
                    'confidence': 0.92,
                    'papers': ['paper1', 'paper2']
                },
                {
                    'id': 'insight2',
                    'text': 'Thermal signatures reveal hardware trojans',
                    'confidence': 0.88,
                    'papers': ['paper1']
                },
            ]

        html = f"""
<div class="research-explorer-widget" data-widget-id="{self.config.widget_id}">
    <style>
        .research-explorer-widget {{
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
            min-width: 500px;
            max-width: 800px;
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

        .i3-badge {{
            display: inline-flex;
            align-items: center;
            gap: {self.theme.spacing.get('xs', '0.25rem')};
            padding: {self.theme.spacing.get('xs', '0.25rem')} {self.theme.spacing.get('sm', '0.5rem')};
            background: var(--widget-entropy);
            color: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('full', '9999px')};
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('bold', '700')};
        }}

        .search-bar {{
            display: flex;
            gap: var(--widget-spacing-sm);
            margin-bottom: var(--widget-spacing-lg);
        }}

        .search-input {{
            flex: 1;
            padding: var(--widget-spacing-sm) var(--widget-spacing-md);
            background: var(--widget-background);
            border: 1px solid var(--widget-primary);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            color: var(--widget-text-primary);
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            font-family: {self.theme.typography.get('fontFamily', {}).get('primary', 'Inter, sans-serif')};
        }}

        .search-input:focus {{
            outline: none;
            border-color: var(--widget-accent);
            box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.2);
        }}

        .search-btn {{
            padding: var(--widget-spacing-sm) var(--widget-spacing-lg);
            background: var(--widget-accent);
            border: none;
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            color: var(--widget-background);
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .search-btn:hover {{
            filter: brightness(1.1);
            box-shadow: 0 0 15px var(--widget-accent);
        }}

        .content-tabs {{
            display: flex;
            gap: var(--widget-spacing-sm);
            margin-bottom: var(--widget-spacing-md);
        }}

        .tab-btn {{
            padding: var(--widget-spacing-sm) var(--widget-spacing-md);
            background: var(--widget-background);
            border: 1px solid var(--widget-primary);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            color: var(--widget-text-secondary);
            cursor: pointer;
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            transition: all 0.2s ease;
        }}

        .tab-btn:hover {{
            background: var(--widget-primary);
            color: var(--widget-text-primary);
        }}

        .tab-btn.active {{
            background: var(--widget-accent);
            color: var(--widget-background);
            border-color: var(--widget-accent);
        }}

        .content-area {{
            min-height: 300px;
            max-height: 400px;
            overflow-y: auto;
        }}

        .paper-card {{
            background: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            padding: var(--widget-spacing-md);
            margin-bottom: var(--widget-spacing-sm);
            border-left: {self.theme.borders.get('width', {}).get('thick', '4px')} solid var(--widget-primary);
            transition: all 0.2s ease;
            cursor: pointer;
        }}

        .paper-card:hover {{
            border-left-color: var(--widget-accent);
            transform: translateX(4px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}

        .paper-title {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            font-weight: {self.theme.typography.get('fontWeight', {}).get('semibold', '600')};
            color: var(--widget-text-primary);
            margin-bottom: {self.theme.spacing.get('xs', '0.25rem')};
        }}

        .paper-meta {{
            display: flex;
            gap: var(--widget-spacing-md);
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
        }}

        .paper-meta span {{
            display: flex;
            align-items: center;
            gap: {self.theme.spacing.get('xs', '0.25rem')};
        }}

        .insight-card {{
            background: linear-gradient(135deg, var(--widget-background) 0%, rgba(155, 89, 182, 0.1) 100%);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            padding: var(--widget-spacing-md);
            margin-bottom: var(--widget-spacing-sm);
            border-left: {self.theme.borders.get('width', {}).get('thick', '4px')} solid var(--widget-entropy);
        }}

        .insight-text {{
            font-size: {self.theme.typography.get('fontSize', {}).get('sm', '0.875rem')};
            color: var(--widget-text-primary);
            margin-bottom: var(--widget-spacing-sm);
            line-height: {self.theme.typography.get('lineHeight', {}).get('relaxed', '1.75')};
        }}

        .insight-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .confidence-bar {{
            flex: 1;
            height: 4px;
            background: var(--widget-surface);
            border-radius: {self.theme.borders.get('radius', {}).get('full', '9999px')};
            overflow: hidden;
            margin-right: var(--widget-spacing-sm);
        }}

        .confidence-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--widget-accent), var(--widget-proof));
            transition: width 1s ease-out;
        }}

        .confidence-label {{
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            color: var(--widget-text-secondary);
        }}

        .linked-papers {{
            display: flex;
            gap: {self.theme.spacing.get('xs', '0.25rem')};
            margin-top: {self.theme.spacing.get('xs', '0.25rem')};
        }}

        .paper-link {{
            padding: 2px 6px;
            background: var(--widget-entropy);
            color: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('sm', '0.25rem')};
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .paper-link:hover {{
            filter: brightness(1.2);
        }}

        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--widget-spacing-sm);
            margin-top: var(--widget-spacing-lg);
            padding-top: var(--widget-spacing-md);
            border-top: 1px solid var(--widget-primary);
        }}

        .stat-item {{
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
            text-transform: uppercase;
        }}

        .graph-viz {{
            display: none;
            background: var(--widget-background);
            border-radius: {self.theme.borders.get('radius', {}).get('md', '0.375rem')};
            padding: var(--widget-spacing-lg);
            min-height: 300px;
            position: relative;
        }}

        .graph-viz.active {{
            display: block;
        }}

        .graph-node {{
            position: absolute;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: var(--widget-entropy);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--widget-background);
            font-size: {self.theme.typography.get('fontSize', {}).get('xs', '0.75rem')};
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 20px var(--widget-entropy);
        }}

        .graph-node:hover {{
            transform: scale(1.2);
        }}
    </style>

    <div class="widget-header">
        <h2 class="widget-title">Research Explorer</h2>
        <div class="i3-badge">
            <span>I³</span>
            <span>Powered</span>
        </div>
    </div>

    <div class="search-bar">
        <input type="text"
               class="search-input"
               placeholder="Search papers, insights, topics..."
               id="search-input-{self.config.widget_id}">
        <button class="search-btn">Explore</button>
    </div>

    <div class="content-tabs">
        <button class="tab-btn active" data-tab="papers">Papers</button>
        <button class="tab-btn" data-tab="insights">Insights</button>
        <button class="tab-btn" data-tab="graph">Knowledge Graph</button>
    </div>

    <div class="content-area">
        <div class="papers-list" data-content="papers">
            {self._render_papers()}
        </div>
        <div class="insights-list" data-content="insights" style="display: none;">
            {self._render_insights()}
        </div>
        <div class="graph-viz" data-content="graph">
            <p style="color: var(--widget-text-secondary); text-align: center; padding: var(--widget-spacing-xl);">
                Interactive knowledge graph visualization<br>
                <small>Click nodes to explore connections</small>
            </p>
        </div>
    </div>

    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">{len(self.papers)}</div>
            <div class="stat-label">Papers</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{len(self.insights)}</div>
            <div class="stat-label">Insights</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{sum(p.get('citations', 0) for p in self.papers)}</div>
            <div class="stat-label">Citations</div>
        </div>
    </div>

    <script>
        (function() {{
            const tabs = document.querySelectorAll('.tab-btn');
            const contents = document.querySelectorAll('[data-content]');

            tabs.forEach(tab => {{
                tab.addEventListener('click', () => {{
                    const targetTab = tab.dataset.tab;

                    tabs.forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');

                    contents.forEach(content => {{
                        content.style.display = content.dataset.content === targetTab ? 'block' : 'none';
                    }});
                }});
            }});
        }})();
    </script>
</div>
"""
        return html

    def _render_papers(self) -> str:
        """Render paper cards"""
        if not self.papers:
            return '<p style="color: var(--widget-text-secondary); text-align: center; padding: var(--widget-spacing-xl);">No papers found</p>'

        papers_html = []
        for paper in self.papers:
            papers_html.append(f'''
                <div class="paper-card">
                    <div class="paper-title">{paper.get('title', 'Untitled')}</div>
                    <div class="paper-meta">
                        <span>👥 {paper.get('authors', 'Unknown')}</span>
                        <span>📅 {paper.get('year', 'N/A')}</span>
                        <span>📊 {paper.get('citations', 0)} citations</span>
                        <span>💡 {paper.get('insights', 0)} insights</span>
                    </div>
                </div>
            ''')

        return '\n'.join(papers_html)

    def _render_insights(self) -> str:
        """Render insight cards"""
        if not self.insights:
            return '<p style="color: var(--widget-text-secondary); text-align: center; padding: var(--widget-spacing-xl);">No insights discovered yet</p>'

        insights_html = []
        for insight in self.insights:
            confidence = insight.get('confidence', 0)
            linked_papers = insight.get('papers', [])

            insights_html.append(f'''
                <div class="insight-card">
                    <div class="insight-text">{insight.get('text', '')}</div>
                    <div class="insight-footer">
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: {confidence * 100}%;"></div>
                        </div>
                        <span class="confidence-label">{confidence * 100:.0f}% confidence</span>
                    </div>
                    <div class="linked-papers">
                        {' '.join([f'<span class="paper-link">{p}</span>' for p in linked_papers])}
                    </div>
                </div>
            ''')

        return '\n'.join(insights_html)
