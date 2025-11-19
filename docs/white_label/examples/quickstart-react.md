# Quick Start: React Integration

Complete example of integrating Industriverse widgets into a React application.

## Prerequisites

- Node.js 16+ and npm
- Partner API credentials
- React 17+ application

## Step 1: Install SDK

```bash
npm install @industriverse/react-widgets @industriverse/sdk
```

## Step 2: Configure Environment

Create `.env.local`:

```bash
REACT_APP_INDUSTRIVERSE_PARTNER_ID=acme-corp
REACT_APP_INDUSTRIVERSE_API_KEY=iv_your_api_key_here
```

**⚠️ Important**: Never commit API keys to version control!

## Step 3: Create Provider Component

`src/providers/IndustriverseProvider.tsx`:

```tsx
import React, { createContext, useContext } from 'react';
import { IndustriverseClient } from '@industriverse/sdk';

interface IndustriverseContextValue {
  client: IndustriverseClient;
  partnerId: string;
}

const IndustriverseContext = createContext<IndustriverseContextValue | null>(null);

export function IndustriverseProvider({ children }: { children: React.ReactNode }) {
  const partnerId = process.env.REACT_APP_INDUSTRIVERSE_PARTNER_ID!;
  const apiKey = process.env.REACT_APP_INDUSTRIVERSE_API_KEY!;

  const client = new IndustriverseClient({
    apiKey,
    partnerId,
    // Optional: Configure theme
    theme: {
      base: 'cosmic',
      customColors: {
        primary: '#1E40AF',
        accent: '#F59E0B',
      },
    },
  });

  return (
    <IndustriverseContext.Provider value={{ client, partnerId }}>
      {children}
    </IndustriverseContext.Provider>
  );
}

export function useIndustriverse() {
  const context = useContext(IndustriverseContext);
  if (!context) {
    throw new Error('useIndustriverse must be used within IndustriverseProvider');
  }
  return context;
}
```

## Step 4: Wrap App with Provider

`src/App.tsx`:

```tsx
import { IndustriverseProvider } from './providers/IndustriverseProvider';
import SecurityDashboard from './pages/SecurityDashboard';

function App() {
  return (
    <IndustriverseProvider>
      <div className="App">
        <SecurityDashboard />
      </div>
    </IndustriverseProvider>
  );
}

export default App;
```

## Step 5: Use Widgets in Components

`src/pages/SecurityDashboard.tsx`:

```tsx
import React from 'react';
import {
  AIShieldDashboard,
  ComplianceScore,
  ThreatHeatmap,
  SecurityOrb,
} from '@industriverse/react-widgets';
import { useIndustriverse } from '../providers/IndustriverseProvider';

export default function SecurityDashboard() {
  const { partnerId, client } = useIndustriverse();

  const handleThreatDetected = (threat: any) => {
    console.log('Threat detected:', threat);

    // Send notification
    client.notifications.send({
      type: 'threat_alert',
      severity: threat.severity,
      message: threat.description,
    });

    // Or trigger your own logic
    if (threat.severity === 'critical') {
      alert(`Critical threat detected: ${threat.description}`);
    }
  };

  return (
    <div className="security-dashboard">
      <header>
        <h1>Security Dashboard</h1>
        <SecurityOrb partnerId={partnerId} size="small" />
      </header>

      <div className="grid grid-cols-2 gap-4">
        {/* Main threat monitoring */}
        <div className="col-span-2">
          <AIShieldDashboard
            partnerId={partnerId}
            theme="cosmic"
            refreshInterval={5000}
            enableWebSocket={true}
            onThreatDetected={handleThreatDetected}
            onDataUpdate={(data) => {
              console.log('Shield updated:', data);
            }}
          />
        </div>

        {/* Compliance tracking */}
        <div>
          <ComplianceScore
            partnerId={partnerId}
            frameworks={['NIST', 'ISO27001', 'GDPR', 'SOC2']}
            showDetails={true}
            onScoreChange={(score) => {
              console.log('Compliance score:', score);
            }}
          />
        </div>

        {/* Threat topology */}
        <div>
          <ThreatHeatmap
            partnerId={partnerId}
            enableInteractive={true}
            showLegend={true}
          />
        </div>
      </div>
    </div>
  );
}
```

## Step 6: Add Styling (Optional)

`src/styles/dashboard.css`:

```css
.security-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
  padding: 2rem;
}

.security-dashboard header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.security-dashboard h1 {
  color: #fff;
  font-size: 2rem;
  font-weight: 700;
}

.grid {
  display: grid;
  gap: 1.5rem;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.col-span-2 {
  grid-column: span 2;
}

@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: 1fr;
  }

  .col-span-2 {
    grid-column: span 1;
  }
}
```

## Step 7: Advanced - Custom Event Handling

`src/hooks/useSecurityEvents.ts`:

```tsx
import { useEffect, useRef } from 'react';
import { useIndustriverse } from '../providers/IndustriverseProvider';

export function useSecurityEvents() {
  const { client } = useIndustriverse();
  const eventHandlers = useRef<Map<string, Function>>(new Map());

  useEffect(() => {
    // Subscribe to real-time events via WebSocket
    const unsubscribe = client.events.subscribe({
      onThreatDetected: (threat) => {
        eventHandlers.current.get('threat')?.call(null, threat);
      },
      onComplianceChange: (compliance) => {
        eventHandlers.current.get('compliance')?.call(null, compliance);
      },
      onAnomalyDetected: (anomaly) => {
        eventHandlers.current.get('anomaly')?.call(null, anomaly);
      },
    });

    return () => {
      unsubscribe();
    };
  }, [client]);

  const on = (event: string, handler: Function) => {
    eventHandlers.current.set(event, handler);
  };

  return { on };
}
```

Usage:

```tsx
function SecurityDashboard() {
  const events = useSecurityEvents();

  useEffect(() => {
    events.on('threat', (threat) => {
      // Handle threat
      console.log('Threat:', threat);
    });

    events.on('compliance', (compliance) => {
      // Handle compliance change
      console.log('Compliance:', compliance);
    });
  }, [events]);

  return <div>...</div>;
}
```

## Step 8: TypeScript Types (Optional)

`src/types/industriverse.ts`:

```typescript
export interface Threat {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  type: string;
  description: string;
  timestamp: string;
  source: string;
  mitigationSteps?: string[];
}

export interface ComplianceFramework {
  name: string;
  score: number;
  maxScore: number;
  percentage: number;
  controls: {
    total: number;
    passing: number;
    failing: number;
  };
}

export interface WidgetConfig {
  partnerId: string;
  theme?: 'cosmic' | 'chrome' | 'light';
  refreshInterval?: number;
  enableAnimations?: boolean;
  enableWebSocket?: boolean;
}
```

## Step 9: Error Handling

`src/components/WidgetErrorBoundary.tsx`:

```tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class WidgetErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Widget error:', error, errorInfo);

    // Report to error tracking service
    // Sentry.captureException(error);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="widget-error">
            <h3>Widget failed to load</h3>
            <p>{this.state.error?.message}</p>
            <button onClick={() => this.setState({ hasError: false })}>
              Retry
            </button>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
```

Usage:

```tsx
<WidgetErrorBoundary>
  <AIShieldDashboard partnerId={partnerId} />
</WidgetErrorBoundary>
```

## Step 10: Testing

`src/pages/__tests__/SecurityDashboard.test.tsx`:

```tsx
import { render, screen, waitFor } from '@testing-library/react';
import { IndustriverseProvider } from '../../providers/IndustriverseProvider';
import SecurityDashboard from '../SecurityDashboard';

// Mock the SDK
jest.mock('@industriverse/sdk');

describe('SecurityDashboard', () => {
  it('renders all widgets', async () => {
    render(
      <IndustriverseProvider>
        <SecurityDashboard />
      </IndustriverseProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    });

    // Check widgets are mounted
    expect(screen.getByTestId('ai-shield-dashboard')).toBeInTheDocument();
    expect(screen.getByTestId('compliance-score')).toBeInTheDocument();
  });

  it('handles threat detection', async () => {
    const mockThreat = {
      id: 'threat-1',
      severity: 'high',
      description: 'SQL Injection attempt',
    };

    // Test threat handling logic
    // ...
  });
});
```

## Full Example - Production Ready

`src/App.tsx`:

```tsx
import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { IndustriverseProvider } from './providers/IndustriverseProvider';
import { WidgetErrorBoundary } from './components/WidgetErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';

// Lazy load pages
const SecurityDashboard = lazy(() => import('./pages/SecurityDashboard'));
const CompliancePage = lazy(() => import('./pages/CompliancePage'));
const ThreatAnalytics = lazy(() => import('./pages/ThreatAnalytics'));

function App() {
  return (
    <BrowserRouter>
      <IndustriverseProvider>
        <div className="app">
          <nav className="sidebar">
            <a href="/dashboard">Dashboard</a>
            <a href="/compliance">Compliance</a>
            <a href="/threats">Threats</a>
          </nav>

          <main className="content">
            <WidgetErrorBoundary>
              <Suspense fallback={<LoadingSpinner />}>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" />} />
                  <Route path="/dashboard" element={<SecurityDashboard />} />
                  <Route path="/compliance" element={<CompliancePage />} />
                  <Route path="/threats" element={<ThreatAnalytics />} />
                </Routes>
              </Suspense>
            </WidgetErrorBoundary>
          </main>
        </div>
      </IndustriverseProvider>
    </BrowserRouter>
  );
}

export default App;
```

## Build and Deploy

### Development

```bash
npm start
```

Access at `http://localhost:3000`

### Production Build

```bash
npm run build
```

Outputs to `build/` directory.

### Docker Deploy

`Dockerfile`:

```dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

`nginx.conf`:

```nginx
server {
  listen 80;
  server_name _;

  root /usr/share/nginx/html;
  index index.html;

  # SPA routing
  location / {
    try_files $uri $uri/ /index.html;
  }

  # Gzip compression
  gzip on;
  gzip_types text/css application/javascript application/json;

  # Security headers
  add_header X-Frame-Options "SAMEORIGIN";
  add_header X-Content-Type-Options "nosniff";
  add_header X-XSS-Protection "1; mode=block";
}
```

Build and run:

```bash
docker build -t acme-security-dashboard .
docker run -p 8080:80 acme-security-dashboard
```

## Performance Optimization

### 1. Code Splitting

```tsx
// Lazy load widgets
const AIShieldDashboard = lazy(() =>
  import('@industriverse/react-widgets').then(module => ({
    default: module.AIShieldDashboard
  }))
);
```

### 2. Memoization

```tsx
import { memo, useMemo } from 'react';

const SecurityDashboard = memo(function SecurityDashboard({ partnerId }) {
  const widgetConfig = useMemo(
    () => ({
      partnerId,
      theme: 'cosmic',
      refreshInterval: 5000,
    }),
    [partnerId]
  );

  return <AIShieldDashboard {...widgetConfig} />;
});
```

### 3. WebSocket Connection Management

```tsx
function useWebSocketConnection() {
  const { client } = useIndustriverse();

  useEffect(() => {
    // Connect when component mounts
    client.connect();

    return () => {
      // Disconnect when component unmounts
      client.disconnect();
    };
  }, [client]);
}
```

## Troubleshooting

### Issue: Widgets not loading

**Check**:
1. API key is valid: `curl -H "X-API-Key: your_key" https://api.industriverse.ai/v2/partner/info`
2. Partner ID is correct
3. Network can reach `api.industriverse.ai` and `cdn.industriverse.ai`
4. Browser console for errors

### Issue: Real-time updates not working

**Check**:
1. WebSocket is enabled: `enableWebSocket={true}`
2. Firewall allows WebSocket connections
3. Browser supports WebSockets
4. Check WebSocket connection in Network tab

### Issue: Theme not applying

**Check**:
1. Theme customization is configured via API
2. Allowed color overrides (see API docs)
3. CSS specificity (use `!important` if needed)

## Next Steps

- **Add more widgets**: See [Widget Catalog](../WIDGET_CATALOG.md)
- **Customize theme**: See [Theme Guide](../THEME_GUIDE.md)
- **Deploy DAC**: See [DAC Deployment](../DAC_DEPLOYMENT.md)
- **Monitor analytics**: See [Analytics Guide](../ANALYTICS.md)

## Resources

- **React Widgets Docs**: https://docs.industriverse.ai/react-widgets
- **API Reference**: https://docs.industriverse.ai/api
- **Example Repo**: https://github.com/industriverse/examples/react
- **Support**: support@industriverse.ai
