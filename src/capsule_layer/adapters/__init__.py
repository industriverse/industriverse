"""
Platform Adapters for Deploy Anywhere Capsules (DACs)

This package contains production-ready adapters for all platforms:
- iOS (ActivityKit + Dynamic Island)
- Android (Notifications + Bubbles)
- Web (PWA + WebSocket + Push)
- Desktop (Electron + System Tray)
- Jetson Nano (GPIO + CUDA + Thermal)
- FPGA (UART/SPI + Hardware State Machine)
- RISC-V (Bare-metal + FreeRTOS)

Each adapter implements the BaseCapsuleAdapter interface and provides
platform-specific rendering and action handling.
"""

from .base_adapter import BaseCapsuleAdapter
from .ios_adapter import iOSCapsuleAdapter
from .android_adapter import AndroidCapsuleAdapter
from .web_adapter import WebCapsuleAdapter
from .desktop_adapter import DesktopCapsuleAdapter
from .jetson_adapter import JetsonNanoAdapter
from .fpga_adapter import FPGACapsuleAdapter
from .riscv_adapter import RISCVCapsuleAdapter

__all__ = [
    "BaseCapsuleAdapter",
    "iOSCapsuleAdapter",
    "AndroidCapsuleAdapter",
    "WebCapsuleAdapter",
    "DesktopCapsuleAdapter",
    "JetsonNanoAdapter",
    "FPGACapsuleAdapter",
    "RISCVCapsuleAdapter",
]
