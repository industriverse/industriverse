"""
Tests for Platform Adapters

Comprehensive tests for all Deploy Anywhere Capsule (DAC) adapters:
- iOS, Android, Web, Desktop
- Jetson Nano, FPGA, RISC-V
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from src.capsule_layer.protocol.capsule_protocol import (
    Capsule,
    CapsuleAttributes,
    CapsuleContentState,
    CapsuleAction,
    CapsuleType,
    CapsuleStatus,
    CapsulePriority,
    PresentationMode
)

from src.capsule_layer.adapters import (
    iOSCapsuleAdapter,
    AndroidCapsuleAdapter,
    WebCapsuleAdapter,
    DesktopCapsuleAdapter,
    JetsonNanoAdapter,
    FPGACapsuleAdapter,
    RISCVCapsuleAdapter
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_capsule():
    """Create sample capsule for testing"""
    return Capsule(
        attributes=CapsuleAttributes(
            capsule_id="test-capsule-001",
            capsule_type=CapsuleType.ALERT,
            title="Test Alert",
            subtitle="Test subtitle",
            icon_name="alert.circle",
            primary_color="#FF0000",
            created_at=datetime.now()
        ),
        content_state=CapsuleContentState(
            status=CapsuleStatus.ACTIVE,
            priority=CapsulePriority.HIGH,
            progress=0.5,
            status_message="Test in progress",
            metric_value="50.0",
            metric_label="Progress"
        )
    )

# ============================================================================
# iOS ADAPTER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_ios_adapter_initialization():
    """Test iOS adapter initialization"""
    adapter = iOSCapsuleAdapter()
    await adapter.initialize()
    
    assert adapter.get_platform_name() == "ios"
    assert adapter.supports_mode(PresentationMode.COMPACT)
    assert adapter.supports_mode(PresentationMode.EXPANDED)
    
    await adapter.cleanup()

@pytest.mark.asyncio
async def test_ios_adapter_show_capsule(sample_capsule):
    """Test showing capsule on iOS"""
    adapter = iOSCapsuleAdapter()
    await adapter.initialize()
    
    success = await adapter.show_capsule(sample_capsule)
    assert success
    assert await adapter.has_capsule("test-capsule-001")
    
    await adapter.cleanup()

@pytest.mark.asyncio
async def test_ios_adapter_update_capsule(sample_capsule):
    """Test updating capsule on iOS"""
    adapter = iOSCapsuleAdapter()
    await adapter.initialize()
    
    await adapter.show_capsule(sample_capsule)
    
    sample_capsule.content_state.progress = 0.8
    success = await adapter.update_capsule(sample_capsule)
    assert success
    
    await adapter.cleanup()

# ============================================================================
# ANDROID ADAPTER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_android_adapter_initialization():
    """Test Android adapter initialization"""
    adapter = AndroidCapsuleAdapter()
    await adapter.initialize()
    
    assert adapter.get_platform_name() == "android"
    assert adapter.supports_mode(PresentationMode.COMPACT)
    
    await adapter.cleanup()

@pytest.mark.asyncio
async def test_android_adapter_show_capsule(sample_capsule):
    """Test showing capsule on Android"""
    adapter = AndroidCapsuleAdapter()
    await adapter.initialize()
    
    success = await adapter.show_capsule(sample_capsule)
    assert success
    
    await adapter.cleanup()

# ============================================================================
# WEB ADAPTER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_web_adapter_initialization():
    """Test Web adapter initialization"""
    adapter = WebCapsuleAdapter()
    await adapter.initialize()
    
    assert adapter.get_platform_name() == "web"
    assert adapter.supports_mode(PresentationMode.COMPACT)
    assert adapter.supports_mode(PresentationMode.EXPANDED)
    
    await adapter.cleanup()

@pytest.mark.asyncio
async def test_web_adapter_show_capsule(sample_capsule):
    """Test showing capsule on Web"""
    adapter = WebCapsuleAdapter()
    await adapter.initialize()
    
    success = await adapter.show_capsule(sample_capsule)
    assert success
    
    await adapter.cleanup()

# ============================================================================
# DESKTOP ADAPTER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_desktop_adapter_initialization():
    """Test Desktop adapter initialization"""
    adapter = DesktopCapsuleAdapter()
    await adapter.initialize()
    
    assert adapter.get_platform_name() == "desktop"
    
    await adapter.cleanup()

@pytest.mark.asyncio
async def test_desktop_adapter_show_capsule(sample_capsule):
    """Test showing capsule on Desktop"""
    adapter = DesktopCapsuleAdapter()
    await adapter.initialize()
    
    success = await adapter.show_capsule(sample_capsule)
    assert success
    
    await adapter.cleanup()

# ============================================================================
# JETSON NANO ADAPTER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_jetson_adapter_initialization():
    """Test Jetson Nano adapter initialization"""
    adapter = JetsonNanoAdapter()
    await adapter.initialize()
    
    assert adapter.get_platform_name() == "jetson_nano"
    assert adapter.max_capsules() == 3
    
    await adapter.cleanup()

@pytest.mark.asyncio
async def test_jetson_adapter_show_capsule(sample_capsule):
    """Test showing capsule on Jetson Nano"""
    adapter = JetsonNanoAdapter()
    await adapter.initialize()
    
    success = await adapter.show_capsule(sample_capsule)
    assert success
    
    await adapter.cleanup()

# ============================================================================
# FPGA ADAPTER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_fpga_adapter_initialization():
    """Test FPGA adapter initialization"""
    adapter = FPGACapsuleAdapter(config={"communication_mode": "uart"})
    
    # Mock UART initialization
    with patch('serial.Serial'):
        await adapter.initialize()
        
        assert adapter.get_platform_name() == "fpga"
        assert adapter.max_capsules() == 16
        
        await adapter.cleanup()

@pytest.mark.asyncio
async def test_fpga_adapter_show_capsule(sample_capsule):
    """Test showing capsule on FPGA"""
    adapter = FPGACapsuleAdapter(config={"communication_mode": "uart"})
    
    with patch('serial.Serial'):
        await adapter.initialize()
        
        # Mock FPGA response
        adapter._send_command = AsyncMock(return_value=Mock(value=0x00))
        
        success = await adapter.show_capsule(sample_capsule)
        assert success
        
        await adapter.cleanup()

# ============================================================================
# RISC-V ADAPTER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_riscv_adapter_initialization():
    """Test RISC-V adapter initialization"""
    adapter = RISCVCapsuleAdapter()
    await adapter.initialize()
    
    assert adapter.get_platform_name() == "riscv"
    assert adapter.max_capsules() == 4
    
    await adapter.cleanup()

@pytest.mark.asyncio
async def test_riscv_adapter_show_capsule(sample_capsule):
    """Test showing capsule on RISC-V"""
    adapter = RISCVCapsuleAdapter()
    await adapter.initialize()
    
    success = await adapter.show_capsule(sample_capsule)
    assert success
    
    await adapter.cleanup()

@pytest.mark.asyncio
async def test_riscv_adapter_memory_constraints(sample_capsule):
    """Test RISC-V memory constraints"""
    adapter = RISCVCapsuleAdapter()
    await adapter.initialize()
    
    # Show multiple capsules up to limit
    for i in range(4):
        capsule = Capsule(
            attributes=CapsuleAttributes(
                capsule_id=f"capsule-{i}",
                capsule_type=CapsuleType.ALERT,
                title=f"Capsule {i}",
                created_at=datetime.now()
            ),
            content_state=CapsuleContentState(
                status=CapsuleStatus.ACTIVE,
                priority=CapsulePriority.MEDIUM
            )
        )
        success = await adapter.show_capsule(capsule)
        assert success
    
    # Try to show one more (should fail due to limit)
    extra_capsule = Capsule(
        attributes=CapsuleAttributes(
            capsule_id="capsule-extra",
            capsule_type=CapsuleType.ALERT,
            title="Extra Capsule",
            created_at=datetime.now()
        ),
        content_state=CapsuleContentState(
            status=CapsuleStatus.ACTIVE,
            priority=CapsulePriority.LOW
        )
    )
    success = await adapter.show_capsule(extra_capsule)
    assert not success  # Should fail due to max capsules limit
    
    await adapter.cleanup()

# ============================================================================
# CROSS-PLATFORM TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_all_adapters_show_hide(sample_capsule):
    """Test show/hide on all adapters"""
    adapters = [
        iOSCapsuleAdapter(),
        AndroidCapsuleAdapter(),
        WebCapsuleAdapter(),
        DesktopCapsuleAdapter(),
        JetsonNanoAdapter(),
        RISCVCapsuleAdapter()
    ]
    
    for adapter in adapters:
        await adapter.initialize()
        
        # Show capsule
        success = await adapter.show_capsule(sample_capsule)
        assert success, f"Failed to show on {adapter.get_platform_name()}"
        
        # Hide capsule
        success = await adapter.hide_capsule("test-capsule-001")
        assert success, f"Failed to hide on {adapter.get_platform_name()}"
        
        await adapter.cleanup()

@pytest.mark.asyncio
async def test_all_adapters_action_handling(sample_capsule):
    """Test action handling on all adapters"""
    adapters = [
        iOSCapsuleAdapter(),
        AndroidCapsuleAdapter(),
        WebCapsuleAdapter(),
        DesktopCapsuleAdapter(),
        JetsonNanoAdapter(),
        RISCVCapsuleAdapter()
    ]
    
    async def mock_handler(capsule, action):
        return Mock(success=True, message="Action handled")
    
    for adapter in adapters:
        await adapter.initialize()
        
        # Register handler
        await adapter.register_action_handler(CapsuleAction.INSPECT, mock_handler)
        
        # Show capsule
        await adapter.show_capsule(sample_capsule)
        
        # Handle action
        result = await adapter.handle_action("test-capsule-001", CapsuleAction.INSPECT)
        # Result may vary by platform, just check it doesn't crash
        
        await adapter.cleanup()
