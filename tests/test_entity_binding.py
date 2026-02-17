"""Tests for Entity Binding."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant, State


async def test_binding_registry_initialization():
    """Test binding registry initialization."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    
    hass = MagicMock()
    registry = BindingRegistry(hass)
    
    assert registry.hass == hass
    assert len(registry._bindings) == 0


async def test_register_channel_binding(mock_output_channel):
    """Test registering channel binding."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    
    hass = MagicMock()
    registry = BindingRegistry(hass)
    
    await registry.register_channel_binding(
        entity_id="light.living_room",
        channel=mock_output_channel,
        vdc_device_id="device1",
    )
    
    assert "light.living_room" in registry._bindings
    assert registry._bindings["light.living_room"]["channel"] == mock_output_channel


async def test_register_sensor_binding(mock_sensor):
    """Test registering sensor binding."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    
    hass = MagicMock()
    registry = BindingRegistry(hass)
    
    await registry.register_sensor_binding(
        entity_id="sensor.temperature",
        sensor=mock_sensor,
        vdc_device_id="device1",
    )
    
    assert "sensor.temperature" in registry._bindings
    assert registry._bindings["sensor.temperature"]["sensor"] == mock_sensor


async def test_ha_to_vdc_light_sync(mock_output_channel):
    """Test HA to VDC light synchronization."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    
    hass = MagicMock()
    hass.states = MagicMock()
    
    # Mock HA state
    ha_state = State("light.living_room", STATE_ON, {"brightness": 128})
    hass.states.get = MagicMock(return_value=ha_state)
    
    mock_output_channel.set_value = AsyncMock()
    
    registry = BindingRegistry(hass)
    await registry.register_channel_binding(
        entity_id="light.living_room",
        channel=mock_output_channel,
        vdc_device_id="device1",
    )
    
    # Simulate HA state change
    await registry._handle_ha_state_change(
        "light.living_room",
        None,
        ha_state,
    )
    
    # Should convert brightness 128 to ~50% (128/255 * 100)
    mock_output_channel.set_value.assert_called()


async def test_vdc_to_ha_sensor_callback(mock_sensor):
    """Test VDC to HA sensor callback."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    
    hass = MagicMock()
    hass.bus = MagicMock()
    hass.bus.async_fire = MagicMock()
    
    registry = BindingRegistry(hass)
    await registry.register_sensor_binding(
        entity_id="sensor.temperature",
        sensor=mock_sensor,
        vdc_device_id="device1",
    )
    
    # Simulate VDC sensor value change
    callback = mock_sensor.on_value_changed.call_args[0][0]
    await callback(25.0)
    
    # Should fire state changed event
    hass.bus.async_fire.assert_called()


async def test_vdc_to_ha_binary_input_callback(mock_binary_input):
    """Test VDC to HA binary input callback."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    
    hass = MagicMock()
    hass.bus = MagicMock()
    hass.bus.async_fire = MagicMock()
    
    registry = BindingRegistry(hass)
    await registry.register_binary_input_binding(
        entity_id="binary_sensor.motion",
        binary_input=mock_binary_input,
        vdc_device_id="device1",
    )
    
    # Simulate VDC binary input state change
    callback = mock_binary_input.on_state_changed.call_args[0][0]
    await callback(True)
    
    # Should fire state changed event
    hass.bus.async_fire.assert_called()


async def test_vdc_to_ha_button_callback(mock_button_input):
    """Test VDC to HA button callback."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    
    hass = MagicMock()
    hass.bus = MagicMock()
    hass.bus.async_fire = MagicMock()
    
    registry = BindingRegistry(hass)
    await registry.register_button_binding(
        entity_id="button.doorbell",
        button_input=mock_button_input,
        vdc_device_id="device1",
    )
    
    # Simulate VDC button press
    callback = mock_button_input.on_pressed.call_args[0][0]
    await callback()
    
    # Should fire button pressed event
    hass.bus.async_fire.assert_called()


async def test_unregister_binding(mock_output_channel):
    """Test unregistering binding."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    
    hass = MagicMock()
    registry = BindingRegistry(hass)
    
    await registry.register_channel_binding(
        entity_id="light.living_room",
        channel=mock_output_channel,
        vdc_device_id="device1",
    )
    
    assert "light.living_room" in registry._bindings
    
    await registry.unregister_binding("light.living_room")
    
    assert "light.living_room" not in registry._bindings


async def test_binding_cleanup():
    """Test binding cleanup on shutdown."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    
    hass = MagicMock()
    registry = BindingRegistry(hass)
    
    # Add some bindings
    registry._bindings = {
        "light.test": {"channel": MagicMock()},
        "sensor.test": {"sensor": MagicMock()},
    }
    
    await registry.async_cleanup()
    
    assert len(registry._bindings) == 0


async def test_concurrent_binding_operations(mock_output_channel, mock_sensor):
    """Test concurrent binding operations."""
    from custom_components.digitalstrom_vdc.entity_binding import BindingRegistry
    import asyncio
    
    hass = MagicMock()
    registry = BindingRegistry(hass)
    
    # Register multiple bindings concurrently
    await asyncio.gather(
        registry.register_channel_binding(
            entity_id="light.room1",
            channel=mock_output_channel,
            vdc_device_id="device1",
        ),
        registry.register_sensor_binding(
            entity_id="sensor.temp1",
            sensor=mock_sensor,
            vdc_device_id="device1",
        ),
    )
    
    assert len(registry._bindings) == 2
