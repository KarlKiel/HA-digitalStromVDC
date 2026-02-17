"""Tests for platform entities."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.light import ColorMode
from homeassistant.core import HomeAssistant


async def test_light_entity_initialization(mock_coordinator, mock_vdsd, mock_output_channel):
    """Test light entity initialization."""
    from custom_components.digitalstrom_vdc.light import DigitalStromVDCLight
    
    mock_vdsd.output.channels = [mock_output_channel]
    
    light = DigitalStromVDCLight(mock_coordinator, mock_vdsd)
    
    assert light._vdc_device == mock_vdsd
    assert light.coordinator == mock_coordinator
    assert ColorMode.BRIGHTNESS in light.supported_color_modes


async def test_light_turn_on(mock_coordinator, mock_vdsd, mock_output_channel):
    """Test turning on light."""
    from custom_components.digitalstrom_vdc.light import DigitalStromVDCLight
    
    mock_vdsd.output.channels = [mock_output_channel]
    mock_output_channel.set_value = AsyncMock()
    
    light = DigitalStromVDCLight(mock_coordinator, mock_vdsd)
    
    await light.async_turn_on(brightness=255)
    
    mock_output_channel.set_value.assert_called_once_with(100.0)
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_light_turn_off(mock_coordinator, mock_vdsd, mock_output_channel):
    """Test turning off light."""
    from custom_components.digitalstrom_vdc.light import DigitalStromVDCLight
    
    mock_vdsd.output.channels = [mock_output_channel]
    mock_output_channel.set_value = AsyncMock()
    
    light = DigitalStromVDCLight(mock_coordinator, mock_vdsd)
    
    await light.async_turn_off()
    
    mock_output_channel.set_value.assert_called_once_with(0.0)


async def test_switch_entity_initialization(mock_coordinator, mock_vdsd, mock_output_channel):
    """Test switch entity initialization."""
    from custom_components.digitalstrom_vdc.switch import DigitalStromVDCSwitch
    
    mock_vdsd.output.channels = [mock_output_channel]
    
    switch = DigitalStromVDCSwitch(mock_coordinator, mock_vdsd)
    
    assert switch._vdc_device == mock_vdsd
    assert switch.coordinator == mock_coordinator


async def test_switch_turn_on(mock_coordinator, mock_vdsd, mock_output_channel):
    """Test turning on switch."""
    from custom_components.digitalstrom_vdc.switch import DigitalStromVDCSwitch
    
    mock_vdsd.output.channels = [mock_output_channel]
    mock_output_channel.set_value = AsyncMock()
    
    switch = DigitalStromVDCSwitch(mock_coordinator, mock_vdsd)
    
    await switch.async_turn_on()
    
    mock_output_channel.set_value.assert_called_once_with(100.0)


async def test_sensor_entity_value(mock_coordinator, mock_vdsd, mock_sensor):
    """Test sensor entity value."""
    from custom_components.digitalstrom_vdc.sensor import DigitalStromVDCSensor
    
    sensor_entity = DigitalStromVDCSensor(mock_coordinator, mock_vdsd, mock_sensor)
    
    assert sensor_entity.native_value == 20.5


async def test_binary_sensor_state(mock_coordinator, mock_vdsd, mock_binary_input):
    """Test binary sensor state."""
    from custom_components.digitalstrom_vdc.binary_sensor import DigitalStromVDCBinarySensor
    
    binary_sensor = DigitalStromVDCBinarySensor(mock_coordinator, mock_vdsd, mock_binary_input)
    
    assert binary_sensor.is_on is False
    
    mock_binary_input.state = True
    assert binary_sensor.is_on is True


async def test_cover_position(mock_coordinator, mock_vdsd, mock_output_channel):
    """Test cover position."""
    from custom_components.digitalstrom_vdc.cover import DigitalStromVDCCover
    
    mock_vdsd.output.channels = [mock_output_channel]
    mock_output_channel.value = 50.0
    
    cover = DigitalStromVDCCover(mock_coordinator, mock_vdsd)
    
    assert cover.current_cover_position == 50


async def test_cover_open(mock_coordinator, mock_vdsd, mock_output_channel):
    """Test opening cover."""
    from custom_components.digitalstrom_vdc.cover import DigitalStromVDCCover
    
    mock_vdsd.output.channels = [mock_output_channel]
    mock_output_channel.set_value = AsyncMock()
    
    cover = DigitalStromVDCCover(mock_coordinator, mock_vdsd)
    
    await cover.async_open_cover()
    
    mock_output_channel.set_value.assert_called_once_with(100.0)


async def test_climate_temperature(mock_coordinator, mock_vdsd, mock_output_channel, mock_sensor):
    """Test climate temperature."""
    from custom_components.digitalstrom_vdc.climate import DigitalStromVDCClimate
    
    mock_vdsd.output.channels = [mock_output_channel]
    mock_vdsd.sensors = [mock_sensor]
    mock_output_channel.value = 21.0
    
    climate = DigitalStromVDCClimate(mock_coordinator, mock_vdsd)
    
    assert climate.current_temperature == 20.5
    assert climate.target_temperature == 21.0


async def test_button_press(mock_coordinator, mock_vdsd, mock_button_input):
    """Test button press."""
    from custom_components.digitalstrom_vdc.button import DigitalStromVDCButton
    
    hass = MagicMock()
    hass.bus = MagicMock()
    hass.bus.async_fire = MagicMock()
    
    mock_coordinator.hass = hass
    mock_button_input.press = AsyncMock()
    
    button = DigitalStromVDCButton(mock_coordinator, mock_vdsd, mock_button_input)
    button.hass = hass
    
    await button.async_press()
    
    hass.bus.async_fire.assert_called_once()
