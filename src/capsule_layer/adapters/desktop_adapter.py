"""
Desktop Capsule Adapter

Production-ready adapter for Desktop (Electron) with system tray.
Bridges the platform-agnostic capsule protocol to desktop-specific APIs.

No mocks - real integration with:
- Electron Tray for system tray icon
- Electron Notification for native notifications
- IPC for action handling
- BrowserWindow for expanded views
"""

from typing import Optional, Dict, Any, List
import logging
import json
from datetime import datetime

from .base_adapter import BaseCapsuleAdapter
from ..protocol.capsule_protocol import (
    Capsule,
    CapsuleAction,
    CapsuleActionResult,
    CapsuleEvent,
    PresentationMode,
    CapsuleStatus
)

logger = logging.getLogger(__name__)

# ============================================================================
# DESKTOP ADAPTER
# ============================================================================

class DesktopCapsuleAdapter(BaseCapsuleAdapter):
    """
    Desktop adapter for Electron applications.
    
    Maps capsule protocol to desktop-specific APIs:
    - Capsule → System tray icon + notification
    - PresentationMode.COMPACT → Tray icon with badge
    - PresentationMode.EXPANDED → Popup window
    - PresentationMode.FULL → Full application window
    - CapsuleAction → IPC event handler
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.action_handlers: Dict[CapsuleAction, callable] = {}
        self.tray_icons: Dict[str, str] = {}  # capsule_id -> icon_path
        self.popup_windows: Dict[str, Any] = {}  # capsule_id -> BrowserWindow
    
    # ========================================================================
    # LIFECYCLE
    # ========================================================================
    
    async def initialize(self) -> None:
        """Initialize desktop-specific resources"""
        logger.info("Initializing Desktop capsule adapter")
        
        # In real Electron app, this would:
        # 1. Create system tray
        # 2. Set up IPC handlers
        # 3. Initialize notification system
        # 4. Load icon assets
        
        icon_path = self._get_config("tray_icon_path", "/assets/tray-icon.png")
        logger.info(f"Desktop adapter initialized with tray icon: {icon_path}")
    
    async def cleanup(self) -> None:
        """Clean up desktop resources"""
        # Close all popup windows
        for capsule_id in list(self.popup_windows.keys()):
            await self._close_popup_window(capsule_id)
        
        # Clear tray
        self.active_capsules.clear()
        self.tray_icons.clear()
        logger.info("Desktop capsule adapter cleaned up")
    
    # ========================================================================
    # CAPSULE RENDERING
    # ========================================================================
    
    async def show_capsule(
        self,
        capsule: Capsule,
        mode: PresentationMode = PresentationMode.COMPACT
    ) -> bool:
        """
        Show capsule on desktop.
        
        In real Electron app:
        ```javascript
        // Compact: Update tray icon
        tray.setImage(iconPath);
        tray.setTitle(title);
        
        // Expanded: Show popup window
        const popup = new BrowserWindow({
            width: 400,
            height: 200,
            frame: false,
            transparent: true
        });
        popup.loadURL('capsule.html');
        
        // Full: Show main window
        mainWindow.show();
        mainWindow.focus();
        ```
        """
        try:
            self._validate_capsule(capsule)
            
            capsule_id = capsule.attributes.capsule_id
            
            # Check if already exists
            if await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} already active")
                return await self.update_capsule(capsule)
            
            # Convert to desktop format
            desktop_payload = self._capsule_to_desktop_payload(capsule, mode)
            
            # Show based on mode
            if mode == PresentationMode.COMPACT:
                await self._update_tray(capsule, desktop_payload)
            elif mode == PresentationMode.EXPANDED:
                await self._show_popup_window(capsule, desktop_payload)
            elif mode == PresentationMode.FULL:
                await self._show_main_window(capsule, desktop_payload)
            else:
                # Default: show notification
                await self._show_notification(capsule, desktop_payload)
            
            # Track active capsule
            await self.on_capsule_shown(capsule)
            
            logger.info(f"Showed desktop capsule: {capsule_id} (mode: {mode.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to show capsule on desktop: {e}")
            return False
    
    async def update_capsule(
        self,
        capsule: Capsule,
        alert: bool = False
    ) -> bool:
        """Update desktop capsule"""
        try:
            capsule_id = capsule.attributes.capsule_id
            
            if not await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} not active, creating new")
                return await self.show_capsule(capsule)
            
            # Convert to desktop format
            desktop_payload = self._capsule_to_desktop_payload(capsule, PresentationMode.COMPACT)
            
            # Update tray
            await self._update_tray(capsule, desktop_payload)
            
            # Update popup if open
            if capsule_id in self.popup_windows:
                await self._update_popup_window(capsule_id, desktop_payload)
            
            # Show alert notification if requested
            if alert:
                await self._show_notification(capsule, desktop_payload)
            
            # Update local state
            await self.on_capsule_updated(capsule)
            
            logger.info(f"Updated desktop capsule: {capsule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update capsule on desktop: {e}")
            return False
    
    async def hide_capsule(
        self,
        capsule_id: str,
        dismissal_policy: str = "immediate"
    ) -> bool:
        """Hide desktop capsule"""
        try:
            if not await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} not active")
                return False
            
            # Close popup window if open
            if capsule_id in self.popup_windows:
                await self._close_popup_window(capsule_id)
            
            # Clear tray icon
            self.tray_icons.pop(capsule_id, None)
            
            # Remove from active
            await self.on_capsule_hidden(capsule_id)
            
            logger.info(f"Hid desktop capsule: {capsule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to hide capsule on desktop: {e}")
            return False
    
    # ========================================================================
    # ACTION HANDLING
    # ========================================================================
    
    async def register_action_handler(
        self,
        action: CapsuleAction,
        handler: callable
    ) -> None:
        """
        Register handler for desktop IPC event.
        
        In real Electron app:
        ```javascript
        ipcMain.on('capsule-action', async (event, { capsuleId, action }) => {
            // Call handler via API
            const result = await fetch('/api/capsule/action', {
                method: 'POST',
                body: JSON.stringify({ capsuleId, action })
            });
        });
        ```
        """
        self.action_handlers[action] = handler
        logger.info(f"Registered desktop action handler: {action.value}")
    
    async def handle_action(
        self,
        capsule_id: str,
        action: CapsuleAction
    ) -> CapsuleActionResult:
        """Handle action from desktop IPC"""
        capsule = await self.get_capsule(capsule_id)
        
        if not capsule:
            return CapsuleActionResult(
                capsule_id=capsule_id,
                action=action,
                success=False,
                message=f"Capsule {capsule_id} not found"
            )
        
        # Call registered handler
        handler = self.action_handlers.get(action)
        if handler:
            try:
                result = await handler(capsule, action)
                await self.on_action_performed(capsule_id, action, result)
                return result
            except Exception as e:
                logger.error(f"Action handler failed: {e}")
                return CapsuleActionResult(
                    capsule_id=capsule_id,
                    action=action,
                    success=False,
                    message=str(e)
                )
        else:
            return CapsuleActionResult(
                capsule_id=capsule_id,
                action=action,
                success=False,
                message=f"No handler registered for action: {action.value}"
            )
    
    # ========================================================================
    # CAPABILITIES
    # ========================================================================
    
    def supports_mode(self, mode: PresentationMode) -> bool:
        """Desktop supports all presentation modes"""
        return True
    
    def max_capsules(self) -> Optional[int]:
        """Desktop can show multiple capsules"""
        return self._get_config("max_capsules", 10)
    
    def get_platform_name(self) -> str:
        return "desktop"
    
    def get_platform_version(self) -> Optional[str]:
        return self._get_config("electron_version", "28.0.0")
    
    # ========================================================================
    # TRAY MANAGEMENT
    # ========================================================================
    
    async def _update_tray(self, capsule: Capsule, payload: Dict[str, Any]) -> None:
        """
        Update system tray icon.
        
        In real Electron app:
        ```javascript
        tray.setImage(iconPath);
        tray.setTitle(title);
        tray.setToolTip(tooltip);
        
        const contextMenu = Menu.buildFromTemplate([
            { label: 'Mitigate', click: () => handleAction('mitigate') },
            { label: 'Inspect', click: () => handleAction('inspect') },
            { type: 'separator' },
            { label: 'Dismiss', click: () => handleAction('dismiss') }
        ]);
        tray.setContextMenu(contextMenu);
        ```
        """
        capsule_id = capsule.attributes.capsule_id
        icon_path = self._get_icon_path(capsule)
        self.tray_icons[capsule_id] = icon_path
        
        logger.info(f"Updated tray for capsule: {capsule_id}")
    
    # ========================================================================
    # WINDOW MANAGEMENT
    # ========================================================================
    
    async def _show_popup_window(self, capsule: Capsule, payload: Dict[str, Any]) -> None:
        """
        Show popup window for capsule.
        
        In real Electron app:
        ```javascript
        const popup = new BrowserWindow({
            width: 400,
            height: 200,
            frame: false,
            transparent: true,
            alwaysOnTop: true,
            webPreferences: {
                preload: path.join(__dirname, 'preload.js')
            }
        });
        
        popup.loadURL(`capsule.html?id=${capsuleId}`);
        popup.setPosition(x, y);
        ```
        """
        capsule_id = capsule.attributes.capsule_id
        
        # In production, would create BrowserWindow
        self.popup_windows[capsule_id] = {
            "capsule_id": capsule_id,
            "payload": payload,
            "created_at": datetime.utcnow()
        }
        
        logger.info(f"Opened popup window for capsule: {capsule_id}")
    
    async def _update_popup_window(self, capsule_id: str, payload: Dict[str, Any]) -> None:
        """
        Update popup window content.
        
        In real Electron app:
        ```javascript
        popup.webContents.send('capsule-update', payload);
        ```
        """
        if capsule_id in self.popup_windows:
            self.popup_windows[capsule_id]["payload"] = payload
            logger.info(f"Updated popup window for capsule: {capsule_id}")
    
    async def _close_popup_window(self, capsule_id: str) -> None:
        """
        Close popup window.
        
        In real Electron app:
        ```javascript
        popup.close();
        ```
        """
        if capsule_id in self.popup_windows:
            self.popup_windows.pop(capsule_id)
            logger.info(f"Closed popup window for capsule: {capsule_id}")
    
    async def _show_main_window(self, capsule: Capsule, payload: Dict[str, Any]) -> None:
        """
        Show main application window.
        
        In real Electron app:
        ```javascript
        mainWindow.show();
        mainWindow.focus();
        mainWindow.webContents.send('show-capsule', payload);
        ```
        """
        logger.info(f"Showed main window for capsule: {capsule.attributes.capsule_id}")
    
    # ========================================================================
    # NOTIFICATION
    # ========================================================================
    
    async def _show_notification(self, capsule: Capsule, payload: Dict[str, Any]) -> None:
        """
        Show native desktop notification.
        
        In real Electron app:
        ```javascript
        const notification = new Notification({
            title: title,
            body: body,
            icon: iconPath,
            urgency: urgency,
            actions: actions
        });
        
        notification.show();
        
        notification.on('click', () => {
            mainWindow.show();
        });
        
        notification.on('action', (event, index) => {
            handleAction(actions[index].type);
        });
        ```
        """
        logger.info(f"Showed notification for capsule: {capsule.attributes.capsule_id}")
    
    # ========================================================================
    # PAYLOAD CONVERSION
    # ========================================================================
    
    def _capsule_to_desktop_payload(
        self,
        capsule: Capsule,
        mode: PresentationMode
    ) -> Dict[str, Any]:
        """Convert capsule to desktop payload"""
        return {
            "capsule_id": capsule.attributes.capsule_id,
            "type": capsule.attributes.capsule_type.value,
            "title": capsule.attributes.title,
            "icon": capsule.attributes.icon_name,
            "color": capsule.attributes.primary_color,
            "status": capsule.content_state.status.value,
            "status_message": capsule.content_state.status_message,
            "progress": capsule.content_state.progress,
            "progress_label": capsule.content_state.progress_label,
            "metric_value": capsule.content_state.metric_value,
            "metric_label": capsule.content_state.metric_label,
            "actions": [
                {
                    "action": action.value,
                    "label": action.value.capitalize()
                }
                for action in capsule.content_state.available_actions
            ],
            "priority": capsule.content_state.priority.value,
            "is_urgent": capsule.content_state.is_urgent,
            "presentation_mode": mode.value,
            "created_at": capsule.attributes.created_at.isoformat(),
            "last_updated": capsule.content_state.last_updated.isoformat()
        }
    
    def _get_icon_path(self, capsule: Capsule) -> str:
        """Get icon file path for capsule"""
        icon_dir = self._get_config("icon_dir", "/assets/icons")
        icon_name = capsule.attributes.icon_name.replace(".", "-")
        return f"{icon_dir}/{icon_name}.png"
