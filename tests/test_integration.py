"""Integration tests for digitalstrom_vdc."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant


@pytest.mark.integration
async def test_integration_setup(hass: HomeAssistant, mock_config_entry):
    """Test integration setup."""
    from custom_components.digitalstrom_vdc import async_setup_entry
    
    # Add the config entry to hass
    hass.config_entries._entries[mock_config_entry.entry_id] = mock_config_entry
    
    with patch("custom_components.digitalstrom_vdc.VDCHostManager") as mock_manager:
        mock_instance = MagicMock()
        mock_instance.async_initialize = AsyncMock()
        mock_manager.return_value = mock_instance
        
        result = await async_setup_entry(hass, mock_config_entry)
        
        assert result is True
        assert mock_config_entry.entry_id in hass.data["digitalstrom_vdc"]
        mock_instance.async_initialize.assert_called_once()


@pytest.mark.integration
async def test_integration_unload(hass: HomeAssistant, mock_config_entry):
    """Test integration unload."""
    from custom_components.digitalstrom_vdc import async_unload_entry
    
    # Setup mock data
    hass.data["digitalstrom_vdc"] = {
        mock_config_entry.entry_id: {
            "vdc_manager": MagicMock(async_shutdown=AsyncMock()),
            "binding_registry": MagicMock(async_cleanup=AsyncMock()),
        }
    }
    
    with patch("homeassistant.config_entries.ConfigEntries.async_unload_platforms", return_value=True):
        result = await async_unload_entry(hass, mock_config_entry)
        
        assert result is True


@pytest.mark.integration
async def test_service_call_scene(hass: HomeAssistant, mock_config_entry, mock_vdsd):
    """Test calling scene service."""
    from custom_components.digitalstrom_vdc import async_call_scene
    
    # Setup mock data
    mock_device_manager = MagicMock()
    mock_device_manager.get_all_devices = MagicMock(return_value=[mock_vdsd])
    
    hass.data["digitalstrom_vdc"] = {
        mock_config_entry.entry_id: {
            "device_manager": mock_device_manager,
        }
    }
    
    mock_vdsd.call_scene = AsyncMock()
    
    service_data = {
        "device_id": mock_vdsd.dSUID,
        "scene": 5,
        "force": False,
    }
    
    await async_call_scene(hass, service_data)
    
    mock_vdsd.call_scene.assert_called_once_with(scene_id=5, force=False)


@pytest.mark.integration
async def test_service_dim_channel(hass: HomeAssistant, mock_config_entry, mock_vdsd, mock_output_channel):
    """Test dim channel service."""
    from custom_components.digitalstrom_vdc import async_dim_channel
    
    # Setup mock data
    mock_device_manager = MagicMock()
    mock_device_manager.get_all_devices = MagicMock(return_value=[mock_vdsd])
    
    mock_vdsd.output.channels = [mock_output_channel]
    
    hass.data["digitalstrom_vdc"] = {
        mock_config_entry.entry_id: {
            "device_manager": mock_device_manager,
        }
    }
    
    mock_output_channel.dim = AsyncMock()
    
    service_data = {
        "device_id": mock_vdsd.dSUID,
        "channel": 0,
        "direction": 1,
        "duration": 5.0,
    }
    
    await async_dim_channel(hass, service_data)
    
    mock_output_channel.dim.assert_called_once_with(direction=1, duration=5.0)


@pytest.mark.integration
async def test_end_to_end_light_control(hass: HomeAssistant, mock_config_entry, mock_vdsd, mock_output_channel):
    """Test end-to-end light control from HA to VDC."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    
    # Setup binding registry
    binding_registry = BindingRegistry(hass)
    
    mock_output_channel.set_value = AsyncMock()
    
    await binding_registry.register_channel_binding(
        entity_id="light.test",
        channel=mock_output_channel,
        vdc_device_id=mock_vdsd.dSUID,
    )
    
    # Simulate HA turning on light
    from homeassistant.core import State
    new_state = State("light.test", STATE_ON, {"brightness": 255})
    
    await binding_registry._handle_ha_state_change(
        "light.test",
        None,
        new_state,
    )
    
    # Should set VDC channel to 100%
    mock_output_channel.set_value.assert_called_with(100.0)


@pytest.mark.integration
async def test_end_to_end_sensor_update(hass: HomeAssistant, mock_vdsd, mock_sensor):
    """Test end-to-end sensor update from VDC to HA."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    
    # Setup binding registry
    binding_registry = BindingRegistry(hass)
    hass.bus = MagicMock()
    hass.bus.async_fire = MagicMock()
    
    await binding_registry.register_sensor_binding(
        entity_id="sensor.temperature",
        sensor=mock_sensor,
        vdc_device_id=mock_vdsd.dSUID,
    )
    
    # Simulate VDC sensor value change
    callback = mock_sensor.on_value_changed.call_args[0][0]
    await callback(22.5)
    
    # Should fire state changed event in HA
    hass.bus.async_fire.assert_called()
    event_type = hass.bus.async_fire.call_args[0][0]
    assert event_type == "digitalstrom_vdc_sensor_changed"


@pytest.mark.integration
async def test_connection_lifecycle(hass: HomeAssistant, mock_config_entry):
    """Test VDC connection lifecycle."""
    from custom_components.digitalstrom_vdc.vdc_manager import VDCHostManager
    
    with patch("custom_components.digitalstrom_vdc.vdc_manager.VdcHost") as mock_vdc_host:
        mock_host_instance = MagicMock()
        mock_host_instance.start = AsyncMock()
        mock_host_instance.ping = AsyncMock()
        mock_vdc_host.return_value = mock_host_instance
        
        manager = VDCHostManager(hass, mock_config_entry.data)
        
        # Initialize
        await manager.async_initialize()
        mock_host_instance.start.assert_called_once()
        
        # Shutdown
        await manager.async_shutdown()
        assert manager._monitoring_task is None
