# Industriverse Capsules - Desktop Application

Deploy Anywhere Capsules desktop application for macOS, Windows, and Linux.

## Overview

The desktop application provides a **menu bar/system tray interface** for accessing Capsule Pins directly from the desktop. It features:

- **Menu Bar Integration** (macOS) / **System Tray** (Windows/Linux)
- **Real-time WebSocket Updates** from Capsule Gateway
- **Native Notifications** for capsule alerts
- **Global Keyboard Shortcuts** for quick actions
- **Auto-Update Mechanism** for seamless updates
- **Cross-Platform Support** (macOS, Windows, Linux)

## Architecture

### Three-Process Model

1. **Main Process** (Node.js)
   - System tray/menu bar management
   - WebSocket connection to Capsule Gateway
   - IPC communication with renderer
   - Native API access (notifications, shortcuts, auto-update)

2. **Renderer Process** (React)
   - UI rendering (capsule launchpad)
   - User interactions
   - Communicates with main via IPC

3. **Preload Script**
   - Secure bridge between main and renderer
   - Exposes type-safe `electronAPI` to renderer
   - Prevents direct Node.js access from renderer (security)

### Security

- **Context Isolation**: Enabled
- **Node Integration**: Disabled in renderer
- **Sandbox**: Enabled
- **Content Security Policy**: Enforced
- **Preload Script**: Only exposes whitelisted APIs

## Technology Stack

- **Electron 27**: Desktop app framework
- **TypeScript**: Type safety across all processes
- **React 18**: Renderer UI
- **Vite**: Fast dev server and bundler
- **electron-builder**: Cross-platform packaging
- **electron-updater**: Auto-update mechanism
- **electron-store**: Persistent configuration storage
- **ws**: WebSocket client

## Project Structure

```
desktop/electron/
├── src/
│   ├── main/              # Main process (Node.js)
│   │   ├── index.ts       # Entry point, app lifecycle
│   │   ├── websocket.ts   # WebSocket manager
│   │   ├── notifications.ts # Notification service
│   │   └── shortcuts.ts   # Keyboard shortcut manager
│   ├── renderer/          # Renderer process (React)
│   │   ├── index.tsx      # React entry point
│   │   ├── App.tsx        # Main app component
│   │   ├── App.css        # App styles
│   │   ├── index.css      # Global styles
│   │   └── components/    # React components
│   ├── preload/           # Preload script
│   │   └── index.ts       # IPC bridge
│   ├── types/             # Shared TypeScript types
│   │   ├── capsule.ts     # Capsule data models
│   │   └── ipc.ts         # IPC types
│   └── utils/             # Utility functions
├── assets/                # Icons and images
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript config (base)
├── tsconfig.main.json     # TypeScript config (main)
├── vite.config.ts         # Vite config (renderer)
└── README.md              # This file
```

## Development

### Prerequisites

- Node.js 18+
- pnpm (or npm/yarn)

### Install Dependencies

```bash
cd desktop/electron
pnpm install
```

### Run Development Server

```bash
pnpm dev
```

This starts:
1. Vite dev server for renderer (port 3001)
2. TypeScript compiler for main process
3. Electron app

### Build for Production

```bash
# Build all
pnpm build

# Package for current platform
pnpm package

# Package for specific platform
pnpm package:mac    # macOS (.dmg)
pnpm package:win    # Windows (.exe)
pnpm package:linux  # Linux (.AppImage, .deb)
```

## Configuration

Configuration is stored in `electron-store` (persistent JSON file):

```typescript
interface AppConfig {
  apiUrl: string;              // API endpoint
  wsUrl: string;               // WebSocket endpoint
  userId: string;              // User ID
  authToken: string;           // Auth token
  autoLaunch: boolean;         // Launch on system startup
  showBadgeCount: boolean;     // Show badge count in menu bar
  enableNotifications: boolean; // Enable native notifications
  theme: 'light' | 'dark' | 'system';
  shortcuts: Record<string, string>; // Keyboard shortcuts
}
```

### Default Shortcuts

- `Cmd/Ctrl + Shift + C`: Toggle capsule launchpad
- `Cmd/Ctrl + Shift + N`: Next capsule
- `Cmd/Ctrl + Shift + P`: Previous capsule
- `Escape`: Hide launchpad

## Features

### Menu Bar Integration

**macOS:**
- Icon appears in menu bar (top-right)
- Click icon → Dropdown window appears below icon
- Badge count shows active capsules (e.g., " 5")

**Windows:**
- Icon appears in system tray (bottom-right)
- Click icon → Popup window appears above tray
- Right-click → Context menu

**Linux:**
- Icon appears in system tray
- Click icon → Popup window appears

### Real-Time Updates

WebSocket connection to Capsule Gateway provides:
- **Capsule Updates**: Real-time capsule state changes
- **Capsule Spawning**: New capsules appear instantly
- **Launchpad Refresh**: Automatic launchpad updates
- **Auto-Reconnect**: Exponential backoff on disconnect
- **Heartbeat**: Keeps connection alive (ping every 30s)

### Native Notifications

System-level notifications for:
- New capsule alerts
- Capsule state changes
- Action completions

**Features:**
- Click notification → Show capsule in launchpad
- Platform-specific notification centers (macOS Notification Center, Windows Action Center)

### Keyboard Shortcuts

Global shortcuts work even when app is not focused:
- **Toggle Window**: `Cmd/Ctrl + Shift + C`
- **Next Capsule**: `Cmd/Ctrl + Shift + N`
- **Previous Capsule**: `Cmd/Ctrl + Shift + P`

Customizable via preferences.

### Auto-Update

Automatic updates using `electron-updater`:
1. App checks for updates on launch
2. Downloads update in background
3. Prompts user to restart
4. Installs update on restart

**Update Channels:**
- `latest`: Stable releases
- `beta`: Beta releases

## IPC Communication

Type-safe IPC between main and renderer:

### Renderer → Main (Invoke)

```typescript
// Get launchpad
const launchpad = await window.electronAPI.invoke('capsule:get-launchpad', {
  userId: 'user123',
});

// Execute action
const result = await window.electronAPI.invoke('capsule:execute-action', {
  capsuleId: 'capsule123',
  actionId: 'approve',
});
```

### Main → Renderer (Send)

```typescript
// WebSocket connected
window.electronAPI.on('ws:connected', () => {
  console.log('Connected!');
});

// WebSocket message
window.electronAPI.on('ws:message', (message) => {
  console.log('Message:', message);
});
```

## Platform-Specific Considerations

### macOS

- **Menu Bar Icon**: 16x16 template image (black with transparency)
- **Badge Count**: Shows in menu bar title (e.g., " 5")
- **Notifications**: macOS Notification Center
- **Auto-Launch**: Login Items

### Windows

- **System Tray Icon**: 32x32 image
- **Context Menu**: Right-click tray icon
- **Notifications**: Windows Action Center
- **Auto-Launch**: Registry (Run key)

### Linux

- **System Tray Icon**: 32x32 image
- **Notification**: libnotify
- **Auto-Launch**: .desktop file in autostart

## Performance

### Metrics

- **Cold Start**: < 2 seconds
- **WebSocket Connect**: < 5 seconds
- **Memory (Foreground)**: < 80MB
- **Memory (Background)**: < 50MB
- **CPU (Idle)**: < 1%
- **Battery Impact**: < 2% per hour

### Optimization

- **Lazy Loading**: Components loaded on demand
- **Virtualization**: Large capsule lists virtualized
- **Debouncing**: User input debounced
- **Caching**: API responses cached
- **WebSocket Pooling**: Single connection shared

## Security

### Electron Security Best Practices

✅ **Context Isolation**: Enabled  
✅ **Node Integration**: Disabled in renderer  
✅ **Sandbox**: Enabled  
✅ **Content Security Policy**: Enforced  
✅ **Preload Script**: Only exposes whitelisted APIs  
✅ **HTTPS**: All API calls over HTTPS  
✅ **WebSocket TLS**: WSS (not WS)  
✅ **Code Signing**: macOS and Windows binaries signed  

### Authentication

- **JWT Tokens**: Stored in `electron-store` (encrypted)
- **Token Refresh**: Automatic token refresh
- **Logout**: Clears all stored credentials

## Troubleshooting

### App Won't Start

1. Check Node.js version (18+)
2. Delete `node_modules` and reinstall
3. Check console for errors

### WebSocket Won't Connect

1. Check `wsUrl` in config
2. Check auth token validity
3. Check firewall/proxy settings
4. Check server status

### Notifications Not Showing

1. Check system notification settings
2. Check `enableNotifications` in config
3. Check notification permissions

### Shortcuts Not Working

1. Check for conflicting shortcuts
2. Check `shortcuts` in config
3. Try unregistering and re-registering

## Known Limitations

- **Linux**: System tray support varies by desktop environment
- **Windows**: Tray icon may not appear in overflow area
- **macOS**: Menu bar space limited (may hide icon if too many apps)

## Roadmap

- [ ] Preferences window
- [ ] Multiple account support
- [ ] Capsule search/filter
- [ ] Capsule history
- [ ] Offline mode
- [ ] Custom themes
- [ ] Plugin system

## License

Proprietary - Industriverse

## Support

For issues or questions, contact: support@industriverse.com
