"""
Base Capsule Adapter

Abstract base class for platform-specific capsule adapters.
Defines the interface that all platform adapters must implement.

Platforms:
- iOS (ActivityKit Live Activities)
- Android (Notifications + Widgets)
- Web (PWA + Push Notifications)
- Desktop (Electron + System Notifications)
- CLI (Terminal UI)
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..protocol.capsule_protocol import (
    Capsule,
    CapsuleAction,
    CapsuleActionResult,
    CapsuleEvent,
    PresentationMode
)

# ============================================================================
# BASE ADAPTER
# ============================================================================

class BaseCapsuleAdapter(ABC):
    """
    Abstract base adapter for rendering capsules on different platforms.
    
    All platform-specific adapters must implement these methods to ensure
    consistent behavior across iOS, Android, Web, Desktop, etc.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize adapter with platform-specific configuration.
        
        Args:
            config: Platform-specific configuration
        """
        self.config = config or {}
        self.active_capsules: Dict[str, Capsule] = {}
    
    # ========================================================================
    # LIFECYCLE METHODS (Required)
    # ========================================================================
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize platform-specific resources.
        
        Examples:
        - iOS: Check ActivityKit authorization
        - Android: Create notification channels
        - Web: Register service worker
        - Desktop: Initialize system tray
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up platform-specific resources.
        
        Examples:
        - Close connections
        - Unregister listeners
        - Clear caches
        """
        pass
    
    # ========================================================================
    # CAPSULE RENDERING (Required)
    # ========================================================================
    
    @abstractmethod
    async def show_capsule(
        self,
        capsule: Capsule,
        mode: PresentationMode = PresentationMode.COMPACT
    ) -> bool:
        """
        Show capsule on platform.
        
        Args:
            capsule: Capsule to show
            mode: Presentation mode
            
        Returns:
            True if successful
            
        Platform Examples:
        - iOS: Activity.request() with ActivityKit
        - Android: NotificationManager.notify()
        - Web: ServiceWorker.showNotification()
        - Desktop: Tray.displayBalloon()
        """
        pass
    
    @abstractmethod
    async def update_capsule(
        self,
        capsule: Capsule,
        alert: bool = False
    ) -> bool:
        """
        Update existing capsule.
        
        Args:
            capsule: Updated capsule
            alert: Whether to show alert/sound
            
        Returns:
            True if successful
            
        Platform Examples:
        - iOS: activity.update() with AlertConfiguration
        - Android: NotificationManager.notify() with same ID
        - Web: ServiceWorker postMessage
        - Desktop: Update tray icon/text
        """
        pass
    
    @abstractmethod
    async def hide_capsule(
        self,
        capsule_id: str,
        dismissal_policy: str = "immediate"
    ) -> bool:
        """
        Hide/dismiss capsule.
        
        Args:
            capsule_id: ID of capsule to hide
            dismissal_policy: When to dismiss ("immediate", "after_delay", etc.)
            
        Returns:
            True if successful
            
        Platform Examples:
        - iOS: activity.end()
        - Android: NotificationManager.cancel()
        - Web: ServiceWorker close notification
        - Desktop: Remove from tray
        """
        pass
    
    # ========================================================================
    # ACTION HANDLING (Required)
    # ========================================================================
    
    @abstractmethod
    async def register_action_handler(
        self,
        action: CapsuleAction,
        handler: callable
    ) -> None:
        """
        Register handler for capsule action.
        
        Args:
            action: Action type
            handler: Async function to call when action is performed
            
        Platform Examples:
        - iOS: App Intent with perform() method
        - Android: PendingIntent with BroadcastReceiver
        - Web: ServiceWorker message handler
        - Desktop: IPC event handler
        """
        pass
    
    @abstractmethod
    async def handle_action(
        self,
        capsule_id: str,
        action: CapsuleAction
    ) -> CapsuleActionResult:
        """
        Handle action performed on capsule.
        
        Args:
            capsule_id: ID of capsule
            action: Action performed
            
        Returns:
            Action result
        """
        pass
    
    # ========================================================================
    # CAPABILITIES (Optional - Override if needed)
    # ========================================================================
    
    def supports_mode(self, mode: PresentationMode) -> bool:
        """
        Check if platform supports presentation mode.
        
        Args:
            mode: Presentation mode to check
            
        Returns:
            True if supported
        """
        # Default: support all modes
        return True
    
    def get_supported_modes(self) -> List[PresentationMode]:
        """Get list of supported presentation modes"""
        return [mode for mode in PresentationMode if self.supports_mode(mode)]
    
    def supports_actions(self) -> bool:
        """Check if platform supports interactive actions"""
        return True
    
    def supports_rich_content(self) -> bool:
        """Check if platform supports rich content (images, progress bars, etc.)"""
        return True
    
    def supports_sound(self) -> bool:
        """Check if platform supports sound/haptics"""
        return True
    
    def max_capsules(self) -> Optional[int]:
        """
        Get maximum number of simultaneous capsules.
        
        Returns:
            Max capsules, or None if unlimited
        """
        return None  # Default: unlimited
    
    # ========================================================================
    # STATE MANAGEMENT (Optional - Override if needed)
    # ========================================================================
    
    async def get_active_capsules(self) -> List[Capsule]:
        """Get list of currently active capsules"""
        return list(self.active_capsules.values())
    
    async def get_capsule(self, capsule_id: str) -> Optional[Capsule]:
        """Get specific capsule by ID"""
        return self.active_capsules.get(capsule_id)
    
    async def has_capsule(self, capsule_id: str) -> bool:
        """Check if capsule is active"""
        return capsule_id in self.active_capsules
    
    # ========================================================================
    # PLATFORM INFO (Optional - Override if needed)
    # ========================================================================
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Get platform name (e.g., 'ios', 'android', 'web', 'desktop')"""
        pass
    
    def get_platform_version(self) -> Optional[str]:
        """Get platform version (e.g., iOS 17.0, Android 14)"""
        return None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get platform capabilities.
        
        Returns:
            Dictionary of capabilities
        """
        return {
            "platform": self.get_platform_name(),
            "version": self.get_platform_version(),
            "supported_modes": [mode.value for mode in self.get_supported_modes()],
            "supports_actions": self.supports_actions(),
            "supports_rich_content": self.supports_rich_content(),
            "supports_sound": self.supports_sound(),
            "max_capsules": self.max_capsules()
        }
    
    # ========================================================================
    # EVENT HANDLING (Optional - Override if needed)
    # ========================================================================
    
    async def on_capsule_shown(self, capsule: Capsule) -> None:
        """Called when capsule is shown"""
        self.active_capsules[capsule.attributes.capsule_id] = capsule
    
    async def on_capsule_updated(self, capsule: Capsule) -> None:
        """Called when capsule is updated"""
        self.active_capsules[capsule.attributes.capsule_id] = capsule
    
    async def on_capsule_hidden(self, capsule_id: str) -> None:
        """Called when capsule is hidden"""
        self.active_capsules.pop(capsule_id, None)
    
    async def on_action_performed(
        self,
        capsule_id: str,
        action: CapsuleAction,
        result: CapsuleActionResult
    ) -> None:
        """Called when action is performed"""
        pass
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def _validate_capsule(self, capsule: Capsule) -> None:
        """
        Validate capsule before rendering.
        
        Args:
            capsule: Capsule to validate
            
        Raises:
            ValueError: If capsule is invalid
        """
        if not capsule.attributes.capsule_id:
            raise ValueError("Capsule ID is required")
        
        if not capsule.attributes.title:
            raise ValueError("Capsule title is required")
        
        if capsule.is_expired:
            raise ValueError("Cannot show expired capsule")


# ============================================================================
# ADAPTER REGISTRY
# ============================================================================

class AdapterRegistry:
    """Registry for platform adapters"""
    
    def __init__(self):
        self._adapters: Dict[str, BaseCapsuleAdapter] = {}
    
    def register(self, platform: str, adapter: BaseCapsuleAdapter) -> None:
        """Register adapter for platform"""
        self._adapters[platform] = adapter
    
    def get(self, platform: str) -> Optional[BaseCapsuleAdapter]:
        """Get adapter for platform"""
        return self._adapters.get(platform)
    
    def get_all(self) -> Dict[str, BaseCapsuleAdapter]:
        """Get all registered adapters"""
        return self._adapters.copy()
    
    def has(self, platform: str) -> bool:
        """Check if platform has registered adapter"""
        return platform in self._adapters


# Global registry instance
_registry: Optional[AdapterRegistry] = None

def get_adapter_registry() -> AdapterRegistry:
    """Get global adapter registry"""
    global _registry
    if _registry is None:
        _registry = AdapterRegistry()
    return _registry
