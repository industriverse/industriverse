# Desktop Application Testing Guide

Comprehensive testing guide for the Industriverse Capsules desktop application.

## Test Environment Setup

### Prerequisites

- macOS 10.15+ / Windows 10+ / Ubuntu 20.04+
- Node.js 18+
- pnpm
- Test WebSocket server (or staging environment)

### Installation

```bash
cd desktop/electron
pnpm install
```

## Manual Testing Checklist

### 1. Application Lifecycle

#### Startup
- [ ] App launches successfully
- [ ] Tray icon appears in correct location (menu bar on macOS, system tray on Windows/Linux)
- [ ] WebSocket connects within 5 seconds
- [ ] Initial launchpad loads
- [ ] No console errors

#### Shutdown
- [ ] App quits cleanly
- [ ] WebSocket disconnects properly
- [ ] No orphan processes
- [ ] Settings are persisted

### 2. Menu Bar / System Tray

#### Icon Behavior (macOS)
- [ ] Icon appears in menu bar
- [ ] Click icon → Window appears below icon
- [ ] Click outside window → Window hides
- [ ] Badge count updates correctly (e.g., " 5")
- [ ] Icon remains visible when window is hidden

#### Icon Behavior (Windows)
- [ ] Icon appears in system tray
- [ ] Click icon → Window appears above tray
- [ ] Right-click → Context menu appears
- [ ] Context menu has "Show Capsules", "Preferences", "Quit"
- [ ] Window hides when clicking outside

#### Icon Behavior (Linux)
- [ ] Icon appears in system tray
- [ ] Click icon → Window appears
- [ ] Window positioning is reasonable

### 3. Window Behavior

#### Positioning
- [ ] Window appears near tray icon
- [ ] Window doesn't go off-screen
- [ ] Window position is consistent

#### Appearance
- [ ] Window is frameless
- [ ] Window has rounded corners
- [ ] Window has drop shadow
- [ ] Window is transparent (background)
- [ ] Window doesn't appear in taskbar/dock

#### Focus
- [ ] Window loses focus → Hides automatically
- [ ] DevTools open → Window doesn't hide on blur
- [ ] Clicking window → Window gains focus

### 4. WebSocket Connection

#### Connection
- [ ] Connects on app launch
- [ ] Connection status shows "Live" when connected
- [ ] Connection status shows "Offline" when disconnected
- [ ] Green dot indicator when connected
- [ ] Red dot indicator when disconnected

#### Reconnection
- [ ] Disconnects → Auto-reconnects within 30s
- [ ] Exponential backoff works (1s, 2s, 4s, 8s...)
- [ ] Max reconnect attempts: 10
- [ ] Reconnect after network change

#### Heartbeat
- [ ] Ping sent every 30 seconds
- [ ] Connection stays alive through firewall/proxy
- [ ] Silent disconnection detected

### 5. Capsule Display

#### Launchpad Loading
- [ ] Loading spinner shows while loading
- [ ] Capsules appear after loading
- [ ] Empty state shows when no capsules
- [ ] Error state shows on error

#### Capsule List
- [ ] Pinned capsules appear first
- [ ] "Pinned" section header shows when capsules are pinned
- [ ] "Recent" section header shows when both pinned and unpinned exist
- [ ] Capsules are sorted correctly
- [ ] Scroll works smoothly

#### Capsule Item
- [ ] Type icon shows correctly (task, alert, etc.)
- [ ] Type color matches (blue for task, red for alert, etc.)
- [ ] Title displays correctly
- [ ] Metadata displays (type, timestamp)
- [ ] Timestamp is relative ("Just now", "5m ago", "2h ago")
- [ ] Badge count shows when > 0
- [ ] Priority indicator shows for critical/high priority
- [ ] Critical priority pulses

#### Capsule Expansion
- [ ] Click "More" → Capsule expands
- [ ] Description shows when expanded
- [ ] Metadata shows when expanded
- [ ] Secondary actions show when expanded
- [ ] Click "Less" → Capsule collapses

### 6. Capsule Actions

#### Primary Action
- [ ] Primary action button shows
- [ ] Click primary action → Action executes
- [ ] Window hides after action
- [ ] Launchpad refreshes after action

#### Secondary Actions
- [ ] Secondary action buttons show when expanded
- [ ] Click secondary action → Action executes
- [ ] Confirmation shows if required

#### Context Menu
- [ ] Click menu button (three dots) → Menu appears
- [ ] Menu positioned correctly (below button)
- [ ] Click outside menu → Menu closes
- [ ] Press Escape → Menu closes

#### Pin/Unpin
- [ ] Click "Pin" → Capsule moves to pinned section
- [ ] Click "Unpin" → Capsule moves to recent section
- [ ] Pin state persists

#### Hide
- [ ] Click "Hide" → Capsule disappears
- [ ] Hidden capsule doesn't reappear on refresh

#### Snooze
- [ ] Click "Snooze 1 hour" → Capsule disappears
- [ ] Click "Snooze 4 hours" → Capsule disappears
- [ ] Click "Snooze 1 day" → Capsule disappears
- [ ] Snoozed capsule reappears after duration

### 7. Real-Time Updates

#### Capsule Updates
- [ ] New capsule → Appears in launchpad
- [ ] Capsule updated → Updates in launchpad
- [ ] Capsule deleted → Disappears from launchpad
- [ ] Badge count updates in real-time

#### Launchpad Refresh
- [ ] Click refresh button → Launchpad reloads
- [ ] Refresh button spins during reload
- [ ] No duplicate capsules after refresh

### 8. Keyboard Shortcuts

#### Global Shortcuts
- [ ] Cmd/Ctrl + Shift + C → Toggle window
- [ ] Cmd/Ctrl + Shift + N → Next capsule
- [ ] Cmd/Ctrl + Shift + P → Previous capsule
- [ ] Shortcuts work when app is not focused

#### Local Shortcuts
- [ ] Escape → Hide window
- [ ] Escape → Close context menu
- [ ] Enter → Execute primary action (when capsule focused)
- [ ] Arrow keys → Navigate capsules

### 9. Notifications

#### System Notifications
- [ ] New alert capsule → Notification shows
- [ ] Click notification → Window shows, capsule focused
- [ ] Notification appears in notification center
- [ ] Notification sound plays (if enabled)

#### Notification Permissions
- [ ] App requests notification permission on first launch
- [ ] Notifications disabled → No notifications show
- [ ] Notifications enabled → Notifications show

### 10. Settings / Configuration

#### Persistence
- [ ] Settings persist across app restarts
- [ ] Auth token persists
- [ ] User ID persists
- [ ] Shortcuts persist

#### Configuration
- [ ] API URL configurable
- [ ] WebSocket URL configurable
- [ ] Auto-launch configurable
- [ ] Notifications configurable
- [ ] Theme configurable (if implemented)

### 11. Performance

#### Startup Performance
- [ ] Cold start < 2 seconds
- [ ] WebSocket connect < 5 seconds
- [ ] Initial launchpad load < 3 seconds

#### Runtime Performance
- [ ] Memory usage < 80MB (foreground)
- [ ] Memory usage < 50MB (background)
- [ ] CPU usage < 1% (idle)
- [ ] No memory leaks after 1 hour

#### UI Performance
- [ ] Smooth scrolling (60 FPS)
- [ ] Smooth animations
- [ ] No jank on capsule expand/collapse
- [ ] Fast action execution (< 500ms)

### 12. Error Handling

#### Network Errors
- [ ] No internet → Shows offline status
- [ ] Server down → Shows error state
- [ ] Timeout → Shows error with retry button
- [ ] Click retry → Retries request

#### API Errors
- [ ] 401 Unauthorized → Shows auth error
- [ ] 500 Server Error → Shows error state
- [ ] Invalid response → Shows error state
- [ ] Error message is user-friendly

#### WebSocket Errors
- [ ] Connection failed → Shows offline status
- [ ] Connection dropped → Auto-reconnects
- [ ] Invalid message → Logged, doesn't crash app

### 13. Security

#### IPC Security
- [ ] Renderer cannot access Node.js APIs directly
- [ ] Only whitelisted IPC channels work
- [ ] Invalid IPC calls are rejected

#### Content Security Policy
- [ ] CSP enforced in renderer
- [ ] No inline scripts
- [ ] No eval()

#### Authentication
- [ ] Auth token stored securely
- [ ] Token not exposed in logs
- [ ] Token refreshed automatically

### 14. Platform-Specific

#### macOS
- [ ] App signed with Developer ID
- [ ] App notarized
- [ ] .dmg installer works
- [ ] App opens after install
- [ ] Auto-launch works (Login Items)
- [ ] Uninstall works (drag to Trash)

#### Windows
- [ ] App signed with code signing certificate
- [ ] .exe installer works
- [ ] App opens after install
- [ ] Auto-launch works (Registry Run key)
- [ ] Uninstall works (Add/Remove Programs)

#### Linux
- [ ] .AppImage works
- [ ] .deb package installs
- [ ] App opens after install
- [ ] Auto-launch works (.desktop file)
- [ ] Uninstall works (package manager)

### 15. Auto-Update

#### Update Check
- [ ] App checks for updates on launch
- [ ] Update available → Notification shows
- [ ] Update downloaded in background

#### Update Installation
- [ ] Click "Install Update" → App restarts
- [ ] Update installs successfully
- [ ] App launches with new version
- [ ] Settings persist after update

## Automated Testing

### Unit Tests

```bash
# Run unit tests
pnpm test

# Run with coverage
pnpm test:coverage
```

### Integration Tests

```bash
# Run integration tests
pnpm test:integration
```

### E2E Tests

```bash
# Run end-to-end tests
pnpm test:e2e
```

## Performance Testing

### Memory Profiling

```bash
# Start app with memory profiler
pnpm dev --inspect

# Open chrome://inspect in Chrome
# Take heap snapshots
```

### CPU Profiling

```bash
# Start app with CPU profiler
pnpm dev --inspect

# Record CPU profile in DevTools
```

## Bug Reporting

### Information to Include

1. **Environment:**
   - OS version
   - App version
   - Node.js version

2. **Steps to Reproduce:**
   - Detailed steps
   - Expected behavior
   - Actual behavior

3. **Logs:**
   - Console logs
   - Main process logs
   - Renderer logs

4. **Screenshots/Videos:**
   - Screenshot of error
   - Screen recording of bug

### Log Locations

**macOS:**
```
~/Library/Logs/Industriverse Capsules/
```

**Windows:**
```
%APPDATA%\Industriverse Capsules\logs\
```

**Linux:**
```
~/.config/Industriverse Capsules/logs/
```

## Known Issues

### macOS
- [ ] Menu bar icon may not appear if too many apps in menu bar
- [ ] Window may appear off-screen on multi-monitor setups

### Windows
- [ ] Tray icon may appear in overflow area
- [ ] Window positioning may be incorrect on high-DPI displays

### Linux
- [ ] System tray support varies by desktop environment
- [ ] Some DEs don't support tray icons

## Testing Checklist Summary

- [ ] All manual tests pass
- [ ] All automated tests pass
- [ ] Performance targets met
- [ ] No console errors
- [ ] No memory leaks
- [ ] Platform-specific features work
- [ ] Auto-update works
- [ ] Security checks pass
- [ ] Documentation is accurate

## Sign-Off

**Tested by:** _______________  
**Date:** _______________  
**Version:** _______________  
**Platform:** _______________  
**Result:** ☐ Pass ☐ Fail  

**Notes:**
