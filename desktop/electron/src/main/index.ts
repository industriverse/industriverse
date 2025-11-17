/**
 * Main Process Entry Point
 * Handles app lifecycle, menu bar, system tray, and IPC
 */

import { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain, globalShortcut } from 'electron';
import { join } from 'path';
import Store from 'electron-store';
import { autoUpdater } from 'electron-updater';
import { WebSocketManager } from './websocket';
import { NotificationService } from './notifications';
import { KeyboardShortcutManager } from './shortcuts';
import type { AppConfig } from '../types/capsule';
import type { IPCChannel } from '../types/ipc';

/**
 * Persistent storage for app configuration
 */
const store = new Store<AppConfig>({
  defaults: {
    apiUrl: process.env.API_URL || 'https://api.industriverse.com',
    wsUrl: process.env.WS_URL || 'wss://gateway.industriverse.com',
    userId: '',
    authToken: '',
    autoLaunch: true,
    showBadgeCount: true,
    enableNotifications: true,
    theme: 'system',
    shortcuts: {
      'toggle-window': 'CommandOrControl+Shift+C',
      'next-capsule': 'CommandOrControl+Shift+N',
      'prev-capsule': 'CommandOrControl+Shift+P',
    },
  },
});

/**
 * Global references (prevent garbage collection)
 */
let tray: Tray | null = null;
let mainWindow: BrowserWindow | null = null;
let wsManager: WebSocketManager | null = null;
let notificationService: NotificationService | null = null;
let shortcutManager: KeyboardShortcutManager | null = null;

/**
 * Platform detection
 */
const isMac = process.platform === 'darwin';
const isWin = process.platform === 'win32';
const isLinux = process.platform === 'linux';

/**
 * Create menu bar window (hidden by default)
 */
function createWindow(): BrowserWindow {
  const win = new BrowserWindow({
    width: 400,
    height: 600,
    show: false,
    frame: false,
    resizable: false,
    transparent: true,
    skipTaskbar: true,
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  // Load renderer
  if (process.env.NODE_ENV === 'development') {
    win.loadURL('http://localhost:3001');
    win.webContents.openDevTools({ mode: 'detach' });
  } else {
    win.loadFile(join(__dirname, '../renderer/index.html'));
  }

  // Hide window when it loses focus
  win.on('blur', () => {
    if (!win.webContents.isDevToolsOpened()) {
      win.hide();
    }
  });

  return win;
}

/**
 * Create system tray icon
 */
function createTray(): Tray {
  // Create tray icon (16x16 for macOS, 32x32 for Windows)
  const iconPath = isMac
    ? join(__dirname, '../../assets/tray-icon-mac.png')
    : join(__dirname, '../../assets/tray-icon-win.png');
  
  const icon = nativeImage.createFromPath(iconPath);
  const trayIcon = new Tray(icon.resize({ width: 16, height: 16 }));

  // Set tooltip
  trayIcon.setToolTip('Industriverse Capsules');

  // Click handler (toggle window)
  trayIcon.on('click', () => {
    toggleWindow();
  });

  // Right-click menu (Windows/Linux)
  if (!isMac) {
    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Show Capsules',
        click: () => toggleWindow(),
      },
      { type: 'separator' },
      {
        label: 'Preferences',
        click: () => {
          // TODO: Open preferences window
        },
      },
      { type: 'separator' },
      {
        label: 'Quit',
        click: () => app.quit(),
      },
    ]);
    trayIcon.setContextMenu(contextMenu);
  }

  return trayIcon;
}

/**
 * Toggle window visibility
 */
function toggleWindow(): void {
  if (!mainWindow) return;

  if (mainWindow.isVisible()) {
    mainWindow.hide();
  } else {
    showWindow();
  }
}

/**
 * Show window positioned below tray icon
 */
function showWindow(): void {
  if (!mainWindow || !tray) return;

  // Get tray bounds
  const trayBounds = tray.getBounds();
  const windowBounds = mainWindow.getBounds();

  // Calculate position
  let x: number;
  let y: number;

  if (isMac) {
    // macOS: Center below menu bar icon
    x = Math.round(trayBounds.x + trayBounds.width / 2 - windowBounds.width / 2);
    y = Math.round(trayBounds.y + trayBounds.height + 4);
  } else if (isWin) {
    // Windows: Position above system tray
    x = Math.round(trayBounds.x + trayBounds.width / 2 - windowBounds.width / 2);
    y = Math.round(trayBounds.y - windowBounds.height - 4);
  } else {
    // Linux: Center of screen
    const { screen } = require('electron');
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;
    x = Math.round(width / 2 - windowBounds.width / 2);
    y = Math.round(height / 2 - windowBounds.height / 2);
  }

  mainWindow.setPosition(x, y, false);
  mainWindow.show();
  mainWindow.focus();
}

/**
 * Update tray badge count (macOS only)
 */
function updateBadgeCount(count: number): void {
  if (isMac && tray) {
    if (count > 0) {
      tray.setTitle(` ${count}`);
    } else {
      tray.setTitle('');
    }
  }
}

/**
 * Initialize services
 */
async function initializeServices(): Promise<void> {
  const config = store.store;

  // Initialize WebSocket manager
  wsManager = new WebSocketManager(config.wsUrl, config.authToken);
  
  wsManager.on('connected', () => {
    console.log('[Main] WebSocket connected');
    mainWindow?.webContents.send('ws:connected');
  });

  wsManager.on('disconnected', () => {
    console.log('[Main] WebSocket disconnected');
    mainWindow?.webContents.send('ws:disconnected');
  });

  wsManager.on('message', (message) => {
    console.log('[Main] WebSocket message:', message.type);
    mainWindow?.webContents.send('ws:message', message);
    
    // Update badge count if capsule update
    if (message.type === 'launchpad_refresh' && message.payload.activeCount !== undefined) {
      updateBadgeCount(message.payload.activeCount);
    }
  });

  wsManager.on('error', (error) => {
    console.error('[Main] WebSocket error:', error);
    mainWindow?.webContents.send('ws:error', { error: error.message });
  });

  // Connect to WebSocket
  await wsManager.connect();

  // Initialize notification service
  notificationService = new NotificationService();

  // Initialize keyboard shortcut manager
  shortcutManager = new KeyboardShortcutManager();
  shortcutManager.registerShortcut(config.shortcuts['toggle-window'], () => toggleWindow());
}

/**
 * Setup IPC handlers
 */
function setupIPCHandlers(): void {
  // Get launchpad
  ipcMain.handle('capsule:get-launchpad', async (_event, data) => {
    if (!wsManager) throw new Error('WebSocket not initialized');
    return await wsManager.getLaunchpad(data.userId);
  });

  // Execute action
  ipcMain.handle('capsule:execute-action', async (_event, data) => {
    if (!wsManager) throw new Error('WebSocket not initialized');
    const result = await wsManager.executeAction(data.capsuleId, data.actionId);
    
    // Hide window after action
    if (result.success) {
      mainWindow?.hide();
    }
    
    return result;
  });

  // Pin capsule
  ipcMain.handle('capsule:pin', async (_event, data) => {
    if (!wsManager) throw new Error('WebSocket not initialized');
    return await wsManager.pinCapsule(data.capsuleId, data.pinned);
  });

  // Hide capsule
  ipcMain.handle('capsule:hide', async (_event, data) => {
    if (!wsManager) throw new Error('WebSocket not initialized');
    return await wsManager.hideCapsule(data.capsuleId);
  });

  // Snooze capsule
  ipcMain.handle('capsule:snooze', async (_event, data) => {
    if (!wsManager) throw new Error('WebSocket not initialized');
    return await wsManager.snoozeCapsule(data.capsuleId, data.duration);
  });

  // Get config
  ipcMain.handle('config:get', async () => {
    return store.store;
  });

  // Set config
  ipcMain.handle('config:set', async (_event, data) => {
    store.set(data);
    return { success: true };
  });

  // Show notification
  ipcMain.handle('notification:show', async (_event, data) => {
    if (!notificationService) throw new Error('Notification service not initialized');
    notificationService.show(data.title, data.body, data.capsuleId);
    return { success: true };
  });

  // Register shortcut
  ipcMain.handle('shortcut:register', async (_event, data) => {
    if (!shortcutManager) throw new Error('Shortcut manager not initialized');
    const success = shortcutManager.registerShortcut(data.key, () => {
      // TODO: Execute action based on data.action
    });
    return { success };
  });

  // Unregister shortcut
  ipcMain.handle('shortcut:unregister', async (_event, data) => {
    if (!shortcutManager) throw new Error('Shortcut manager not initialized');
    shortcutManager.unregisterShortcut(data.key);
    return { success: true };
  });

  // Window management
  ipcMain.on('window:show', () => showWindow());
  ipcMain.on('window:hide', () => mainWindow?.hide());
  ipcMain.on('window:toggle', () => toggleWindow());
}

/**
 * App ready handler
 */
app.whenReady().then(async () => {
  // Create window and tray
  mainWindow = createWindow();
  tray = createTray();

  // Setup IPC handlers
  setupIPCHandlers();

  // Initialize services
  await initializeServices();

  // Check for updates (production only)
  if (process.env.NODE_ENV === 'production') {
    autoUpdater.checkForUpdatesAndNotify();
  }

  console.log('[Main] App ready');
});

/**
 * Quit when all windows are closed (except macOS)
 */
app.on('window-all-closed', () => {
  if (!isMac) {
    app.quit();
  }
});

/**
 * macOS: Re-create window when dock icon is clicked
 */
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    mainWindow = createWindow();
  }
});

/**
 * Cleanup before quit
 */
app.on('before-quit', () => {
  // Disconnect WebSocket
  wsManager?.disconnect();

  // Unregister all shortcuts
  globalShortcut.unregisterAll();

  console.log('[Main] App quitting');
});

/**
 * Handle uncaught exceptions
 */
process.on('uncaughtException', (error) => {
  console.error('[Main] Uncaught exception:', error);
});

process.on('unhandledRejection', (reason) => {
  console.error('[Main] Unhandled rejection:', reason);
});
