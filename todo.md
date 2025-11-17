# Capsule Pins PWA - Week 7 TODO

## Phase 1: Design Capsule UI and Create React Components

- [x] Design capsule pill UI (collapsed state)
- [x] Design capsule expanded UI (medium state)
- [x] Design capsule full UI (detailed state)
- [x] Create CapsulePill component with three states
- [x] Add Tailwind CSS styling with animations
- [x] Create responsive layouts for mobile/tablet/desktop
- [x] Add capsule status indicators (active, warning, critical)
- [x] Implement state transitions with smooth animations

## Phase 2: Implement WebSocket Service

- [ ] Create CapsuleWebSocket service class
- [ ] Implement WebSocket connection with authentication
- [ ] Add message handling for capsule updates
- [ ] Implement reconnection logic with exponential backoff
- [ ] Add heartbeat mechanism to keep connection alive
- [ ] Create React hook for WebSocket integration (useCapsuleWebSocket)
- [ ] Handle connection states (connecting, connected, disconnected, error)
- [ ] Add message queue for offline actions

## Phase 3: Configure PWA

- [ ] Create manifest.json with app metadata
- [ ] Add app icons (192x192, 512x512, maskable)
- [ ] Create service worker for caching
- [ ] Implement cache strategies (cache-first for static, network-first for API)
- [ ] Add offline fallback page
- [ ] Configure workbox for advanced caching
- [ ] Test "Add to Home Screen" on iOS and Android
- [ ] Add install prompt for desktop

## Phase 4: Add Action Handlers and API Integration

- [ ] Create API service for Capsule Gateway REST endpoints
- [ ] Implement action handlers (mitigate, inspect, dismiss, etc.)
- [ ] Add action confirmation dialogs
- [ ] Implement optimistic UI updates
- [ ] Add error handling and retry logic
- [ ] Create loading states for actions
- [ ] Add success/error toast notifications
- [ ] Implement action history tracking

## Phase 5: Cross-Browser Testing and Optimization

- [ ] Test on Chrome (desktop + mobile)
- [ ] Test on Safari (desktop + iOS)
- [ ] Test on Firefox (desktop + mobile)
- [ ] Test on Edge
- [ ] Run Lighthouse audit (target: all scores > 90)
- [ ] Optimize bundle size (code splitting, lazy loading)
- [ ] Optimize images (WebP, responsive images)
- [ ] Add performance monitoring
- [ ] Fix accessibility issues (WCAG 2.1 AA)
- [ ] Test keyboard navigation
- [ ] Test screen reader compatibility

## Phase 6: Documentation and Checkpoint

- [ ] Write component API documentation
- [ ] Document WebSocket protocol
- [ ] Create PWA setup guide
- [ ] Write deployment guide
- [ ] Add inline code comments
- [ ] Create Storybook stories for components
- [ ] Write integration test guide
- [ ] Save project checkpoint

## Additional Features (Nice to Have)

- [ ] Add capsule search and filtering
- [ ] Implement capsule grouping by status
- [ ] Add dark mode support
- [ ] Create capsule detail modal
- [ ] Add capsule history timeline
- [ ] Implement push notifications
- [ ] Add analytics tracking
- [ ] Create admin dashboard for capsule management


## Design Changes

- [x] Change color scheme from blue/purple to dark grey/metallic
- [x] Update status colors to slate greys, silver, charcoal
- [x] Add metallic sheen effects
- [x] Use steel blue for active, amber for warning, crimson for critical
