# Capsule Pins PWA

**Real-time industrial intelligence at your fingertips**

A production-ready Progressive Web App for displaying and managing capsules from the Industriverse platform. Built with React 19, TypeScript, and Tailwind CSS 4.

---

## Features

### Core Functionality

**Real-Time Updates**
- WebSocket connection to Capsule Gateway Service with automatic reconnection and exponential backoff
- Live capsule state updates with optimistic UI
- Connection status indicator with visual feedback

**Progressive Web App**
- Installable on iOS, Android, and desktop platforms
- Offline functionality with service worker caching
- Background sync for queued actions when connection is restored
- Push notification support for critical alerts

**Capsule Management**
- Three-state capsule display: pill (collapsed), expanded (medium), full (detailed)
- Status-based color coding: active (cyan), warning (amber), critical (rose), resolved (emerald)
- Action handlers: mitigate, inspect, dismiss, escalate, acknowledge
- Optimistic UI updates with error recovery

**Performance**
- Code-split bundles for optimal loading
- React vendor chunk: 314KB (97KB gzipped)
- UI vendor chunk: 40KB (11KB gzipped)
- App chunk: 152KB (43KB gzipped)
- Total gzipped: ~151KB

---

## Architecture

### Technology Stack

**Frontend**
- React 19 with TypeScript
- Tailwind CSS 4 for styling
- Vite for build tooling
- Wouter for client-side routing

**Services**
- CapsuleWebSocket: Real-time WebSocket client
- CapsuleAPI: REST API client for Capsule Gateway
- Service Worker: Offline caching and background sync

**Integration**
- Capsule Gateway Service (WebSocket + REST)
- Complete Industriverse vertical stack:
  - Remix Lab (DAC creation)
  - A2A (Agent orchestration)
  - MCP (Context sharing)
  - Thermodynamic Computing (JAX/Jasmin/Thermodynasty)
  - DAC Factory (Build/deploy/scale)

---

## Getting Started

### Prerequisites

- Node.js 22+
- pnpm 9+

### Installation

```bash
# Clone repository
git clone <repository-url>
cd capsule-pins-pwa

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

### Environment Variables

Create `.env` file:

```env
# Capsule Gateway endpoints
VITE_CAPSULE_GATEWAY_API=https://capsule-gateway.industriverse.io
VITE_CAPSULE_GATEWAY_WS=wss://capsule-gateway.industriverse.io/ws

# Authentication
VITE_AUTH_TOKEN=your_jwt_token_here

# App configuration
VITE_APP_TITLE=Capsule Pins
VITE_APP_LOGO=/logo.png
```

### Development

```bash
# Start dev server (http://localhost:3000)
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview

# Type checking
pnpm typecheck

# Linting
pnpm lint
```

---

## Component API

### CapsulePill

Main component for displaying capsule state.

**Props:**
```typescript
interface CapsulePillProps {
  capsule: CapsuleData;
  initialState?: CapsuleViewState; // 'pill' | 'expanded' | 'full'
  onAction?: (action: CapsuleAction, capsuleId: string) => void;
  onStateChange?: (state: CapsuleViewState) => void;
}
```

**Usage:**
```tsx
<CapsulePill
  capsule={capsuleData}
  initialState="pill"
  onAction={handleAction}
  onStateChange={handleStateChange}
/>
```

### useCapsuleWebSocket

React hook for WebSocket integration.

**Options:**
```typescript
interface UseCapsuleWebSocketOptions {
  url: string;
  authToken?: string;
  autoConnect?: boolean;
  onCapsuleUpdate?: (update: CapsuleUpdate) => void;
  onCapsuleNew?: (capsule: CapsuleData) => void;
  onCapsuleRemoved?: (capsuleId: string) => void;
  onError?: (error: Error) => void;
}
```

**Usage:**
```tsx
const { connectionState, connect, disconnect, isConnected } = useCapsuleWebSocket({
  url: 'wss://capsule-gateway.industriverse.io/ws',
  authToken: 'your_token',
  autoConnect: true,
  onCapsuleUpdate: (update) => {
    console.log('Capsule updated:', update);
  }
});
```

---

## WebSocket Protocol

### Connection

```
wss://capsule-gateway.industriverse.io/ws?token=JWT_TOKEN
```

### Message Types

**Incoming Messages:**

```typescript
// Capsule update
{
  type: 'capsule_update',
  data: {
    capsuleId: string,
    updates: Partial<CapsuleData>
  }
}

// New capsule
{
  type: 'capsule_new',
  data: CapsuleData
}

// Capsule removed
{
  type: 'capsule_removed',
  data: { capsuleId: string }
}

// Heartbeat response
{
  type: 'heartbeat',
  data: { timestamp: string }
}
```

**Outgoing Messages:**

```typescript
// Heartbeat
{
  type: 'heartbeat',
  timestamp: string
}

// Subscribe to capsule updates
{
  type: 'subscribe',
  capsuleIds: string[]
}
```

---

## REST API

### Endpoints

**Get All Capsules**
```
GET /api/v1/capsules
Response: CapsuleData[]
```

**Get Capsule by ID**
```
GET /api/v1/capsules/:id
Response: CapsuleData
```

**Execute Action**
```
POST /api/v1/capsule/action
Body: {
  capsuleId: string,
  action: CapsuleAction,
  metadata?: Record<string, any>
}
Response: ActionResponse
```

**Get Statistics**
```
GET /api/v1/capsules/statistics
Response: {
  total: number,
  active: number,
  warning: number,
  critical: number,
  resolved: number,
  dismissed: number
}
```

---

## PWA Configuration

### Manifest

Located at `/public/manifest.json`:

```json
{
  "name": "Capsule Pins - Industrial Intelligence",
  "short_name": "Capsule Pins",
  "display": "standalone",
  "background_color": "#0f1419",
  "theme_color": "#1e2936"
}
```

### Service Worker

Located at `/public/sw.js`:

**Caching Strategies:**
- Cache-first for static assets (HTML, CSS, JS, images)
- Network-first for API calls with cache fallback
- Background sync for offline actions

**Features:**
- Automatic cache updates on new versions
- Offline page fallback
- Push notification handling
- Background sync for queued actions

---

## Deployment

### Build

```bash
# Production build
pnpm build

# Output: dist/public/
```

### Deploy to Manus Platform

```bash
# Create checkpoint
# Use Management UI → Publish button
```

### Deploy to Custom Server

```bash
# Build
pnpm build

# Serve dist/public/ directory
# Ensure HTTPS for PWA features
# Configure CORS for Capsule Gateway
```

---

## Browser Support

**Desktop:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Mobile:**
- iOS Safari 14+
- Chrome Android 90+
- Samsung Internet 14+

**PWA Features:**
- Service Worker: All modern browsers
- Push Notifications: Chrome, Firefox, Edge (not iOS Safari)
- Background Sync: Chrome, Edge
- Install Prompt: All platforms

---

## Performance

**Lighthouse Scores (Target):**
- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90
- PWA: 100

**Bundle Analysis:**
- Total gzipped: ~151KB
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.0s
- Largest Contentful Paint: < 2.5s

---

## Security

**Authentication:**
- JWT tokens for API and WebSocket
- Token refresh on expiration
- Secure token storage

**HTTPS:**
- Required for PWA features
- Service Worker requires HTTPS
- WebSocket over TLS (wss://)

**CORS:**
- Configured for Capsule Gateway domain
- Credentials included in requests

---

## Troubleshooting

### WebSocket Connection Issues

**Problem:** Connection fails or disconnects frequently

**Solutions:**
1. Check auth token validity
2. Verify WebSocket URL is correct (wss://)
3. Check network connectivity
4. Review browser console for errors
5. Ensure server supports WebSocket

### Service Worker Not Registering

**Problem:** PWA features not working

**Solutions:**
1. Ensure HTTPS (required for service worker)
2. Check browser console for registration errors
3. Clear browser cache and reload
4. Verify sw.js is accessible at /sw.js
5. Check browser compatibility

### Offline Functionality Not Working

**Problem:** App doesn't work offline

**Solutions:**
1. Ensure service worker is registered
2. Visit app while online first (to cache assets)
3. Check Application → Service Workers in DevTools
4. Verify cache storage in DevTools
5. Test with DevTools offline mode

---

## Development Notes

### Code Structure

```
client/
├── src/
│   ├── components/      # React components
│   │   ├── CapsulePill.tsx
│   │   └── ui/         # shadcn/ui components
│   ├── hooks/          # Custom React hooks
│   │   └── useCapsuleWebSocket.ts
│   ├── services/       # API and WebSocket services
│   │   ├── CapsuleAPI.ts
│   │   └── CapsuleWebSocket.ts
│   ├── types/          # TypeScript types
│   │   └── capsule.ts
│   ├── lib/            # Utilities
│   │   └── sw-register.ts
│   ├── pages/          # Page components
│   │   └── Home.tsx
│   └── App.tsx         # Root component
└── public/             # Static assets
    ├── manifest.json
    └── sw.js
```

### Adding New Features

1. Update types in `types/capsule.ts`
2. Add service methods in `services/`
3. Create components in `components/`
4. Update Home page or add new routes
5. Test offline functionality
6. Update documentation

---

## Week 7 Completion

**Phases Completed:**
1. ✅ Design capsule UI and create React components
2. ✅ Implement WebSocket service for real-time updates
3. ✅ Configure PWA with service worker and offline caching
4. ✅ Add action handlers and API integration
5. ✅ Cross-browser testing and Lighthouse optimization
6. ✅ Complete documentation and create checkpoint

**Next: Week 8 - Whitelabel Stage**
- Native iOS app with Dynamic Island
- Native Android app with notification channels
- Live Activities for long-running workflows
- Whitelabel customization system

---

## License

Proprietary - Industriverse Platform

---

## Support

For issues or questions:
- Documentation: https://docs.industriverse.io
- Support: https://help.manus.im
- GitHub: [repository-url]

---

**Built with discipline and diligence for Week 7 of the Industriverse 16-week plan.**
