"""Tests for VDC Manager."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.digitalstrom_vdc.const import (
    CONF_ANNOUNCE_SERVICE,
    CONF_DSUID,
    CONF_PORT,
    CONF_SERVICE_NAME,
    CONF_VDC_NAME,
    STATE_ACTIVE,
    STATE_CONNECTED,
    STATE_DISCONNECTED,
)


async def test_vdc_manager_initialization(mock_vdc_host, mock_vdc):
    """Test VDC manager initialization."""
    from custom_components.digitalstrom_vdc.vdc_manager import VDCHostManager
    
    with patch(
        "custom_components.digitalstrom_vdc.vdc_manager.VdcHost",
        return_value=mock_vdc_host,
    ):
        mock_vdc_host.create_vdc.return_value = mock_vdc
        
        config = {
            CONF_PORT: 8444,
            CONF_VDC_NAME: "Test VDC",
            CONF_DSUID: "test-dsuid-123",
            CONF_ANNOUNCE_SERVICE: False,
        }
        
        manager = VDCHostManager(MagicMock(), config)
        
        assert manager._config == config
        assert manager.connection_state == STATE_DISCONNECTED


async def test_vdc_manager_async_initialize(mock_vdc_host, mock_vdc):
    """Test VDC manager async initialization."""
    from custom_components.digitalstrom_vdc.vdc_manager import VDCHostManager
    
    with patch(
        "custom_components.digitalstrom_vdc.vdc_manager.VdcHost",
        return_value=mock_vdc_host,
    ):
        mock_vdc_host.create_vdc.return_value = mock_vdc
        mock_vdc_host.start = AsyncMock()
        
        config = {
            CONF_PORT: 8444,
            CONF_VDC_NAME: "Test VDC",
            CONF_DSUID: "test-dsuid-123",
            CONF_ANNOUNCE_SERVICE: False,
        }
        
        manager = VDCHostManager(MagicMock(), config)
        result = await manager.async_initialize()
        
        assert result is True
        mock_vdc_host.start.assert_called_once()
        assert manager.connection_state == STATE_ACTIVE


async def test_vdc_manager_connection_monitoring(mock_vdc_host, mock_vdc):
    """Test VDC manager connection monitoring."""
    from custom_components.digitalstrom_vdc.vdc_manager import VDCHostManager
    
    with patch(
        "custom_components.digitalstrom_vdc.vdc_manager.VdcHost",
        return_value=mock_vdc_host,
    ):
        mock_vdc_host.create_vdc.return_value = mock_vdc
        mock_vdc_host.ping = AsyncMock()
        
        config = {
            CONF_PORT: 8444,
            CONF_VDC_NAME: "Test VDC",
            CONF_DSUID: "test-dsuid-123",
        }
        
        manager = VDCHostManager(MagicMock(), config)
        manager._connection_state = STATE_ACTIVE
        manager._host = mock_vdc_host
        
        # Start monitoring in background
        import asyncio
        task = asyncio.create_task(manager.async_maintain_connection())
        
        # Let it run briefly
        await asyncio.sleep(0.1)
        
        # Cancel the task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def test_vdc_manager_shutdown(mock_vdc_host, mock_vdc):
    """Test VDC manager graceful shutdown."""
    from custom_components.digitalstrom_vdc.vdc_manager import VDCHostManager
    
    with patch(
        "custom_components.digitalstrom_vdc.vdc_manager.VdcHost",
        return_value=mock_vdc_host,
    ):
        mock_vdc_host.create_vdc.return_value = mock_vdc
        
        config = {
            CONF_PORT: 8444,
            CONF_VDC_NAME: "Test VDC",
            CONF_DSUID: "test-dsuid-123",
        }
        
        manager = VDCHostManager(MagicMock(), config)
        manager._host = mock_vdc_host
        
        await manager.async_shutdown()
        
        assert manager.connection_state == STATE_DISCONNECTED


async def test_dss_connected_callback(mock_vdc_host, mock_vdc):
    """Test DSS connected callback."""
    from custom_components.digitalstrom_vdc.vdc_manager import VDCHostManager
    
    hass = MagicMock()
    hass.bus = MagicMock()
    hass.bus.async_fire = MagicMock()
    
    with patch(
        "custom_components.digitalstrom_vdc.vdc_manager.VdcHost",
        return_value=mock_vdc_host,
    ):
        mock_vdc_host.create_vdc.return_value = mock_vdc
        
        config = {
            CONF_PORT: 8444,
            CONF_VDC_NAME: "Test VDC",
            CONF_DSUID: "test-dsuid-123",
        }
        
        manager = VDCHostManager(hass, config)
        
        # Trigger connected callback
        await manager._on_dss_connected("session-123")
        
        assert manager.connection_state == STATE_ACTIVE
        hass.bus.async_fire.assert_called_once()


async def test_dss_disconnected_callback(mock_vdc_host, mock_vdc):
    """Test DSS disconnected callback."""
    from custom_components.digitalstrom_vdc.vdc_manager import VDCHostManager
    
    hass = MagicMock()
    hass.bus = MagicMock()
    hass.bus.async_fire = MagicMock()
    
    with patch(
        "custom_components.digitalstrom_vdc.vdc_manager.VdcHost",
        return_value=mock_vdc_host,
    ):
        mock_vdc_host.create_vdc.return_value = mock_vdc
        # Make reconnect fail to test disconnected state
        mock_vdc_host.reconnect = AsyncMock(side_effect=Exception("Connection failed"))
        
        config = {
            CONF_PORT: 8444,
            CONF_VDC_NAME: "Test VDC",
            CONF_DSUID: "test-dsuid-123",
        }
        
        manager = VDCHostManager(hass, config)
        manager._host = mock_vdc_host
        
        # Patch asyncio.sleep to avoid waiting in test
        with patch("asyncio.sleep", return_value=None):
            # Trigger disconnected callback
            await manager._on_dss_disconnected()
        
        # After failed reconnection attempts, should be disconnected
        assert manager.connection_state == STATE_DISCONNECTED
        # Event should be fired
        assert hass.bus.async_fire.call_count >= 1
