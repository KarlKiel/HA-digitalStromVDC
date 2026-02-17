"""Tests for Device Manager."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant


async def test_device_manager_initialization(mock_vdc):
    """Test device manager initialization."""
    from custom_components.digitalstrom_vdc.device_manager import DeviceManager
    
    hass = MagicMock()
    manager = DeviceManager(mock_vdc, hass)
    
    assert manager.vdc == mock_vdc
    assert manager.hass == hass
    assert len(manager._devices) == 0


async def test_create_device_from_template(mock_vdc, mock_vdsd):
    """Test creating device from template."""
    from custom_components.digitalstrom_vdc.device_manager import DeviceManager
    
    hass = MagicMock()
    mock_vdc.create_vdsd_from_template = MagicMock(return_value=mock_vdsd)
    
    manager = DeviceManager(mock_vdc, hass)
    
    device = await manager.create_device_from_template(
        template_name="light_dimmer",
        instance_name="Living Room Light",
        parameters={"channel_type": "brightness"},
        entity_bindings={"output_channel_0": "light.living_room"},
    )
    
    assert device == mock_vdsd
    mock_vdc.create_vdsd_from_template.assert_called_once()
    assert mock_vdsd.dSUID in manager._devices


async def test_create_device_manual(mock_vdc, mock_vdsd):
    """Test creating device manually."""
    from custom_components.digitalstrom_vdc.device_manager import DeviceManager
    
    hass = MagicMock()
    mock_vdc.create_vdsd = MagicMock(return_value=mock_vdsd)
    
    # Mock methods on vdsd
    mock_vdsd.add_button_input = MagicMock()
    mock_vdsd.add_binary_input = MagicMock()
    mock_vdsd.add_sensor = MagicMock()
    mock_vdsd.create_output = MagicMock()
    
    manager = DeviceManager(mock_vdc, hass)
    
    device_config = {
        "name": "Test Device",
        "primary_group": 1,
    }
    
    inputs = [
        {"type": "button", "button_type": "single", "name": "Button 1"},
    ]
    
    outputs = [
        {
            "channels": [
                {"channel_type": "brightness", "min_value": 0, "max_value": 100}
            ]
        }
    ]
    
    device = await manager.create_device_manual(
        device_config=device_config,
        inputs=inputs,
        outputs=outputs,
        entity_bindings={},
    )
    
    assert device == mock_vdsd
    mock_vdc.create_vdsd.assert_called_once()
    mock_vdsd.add_button_input.assert_called_once()


async def test_add_input_to_device_button(mock_vdsd):
    """Test adding button input to device."""
    from custom_components.digitalstrom_vdc.device_manager import DeviceManager
    
    hass = MagicMock()
    mock_vdc = MagicMock()
    manager = DeviceManager(mock_vdc, hass)
    
    mock_vdsd.add_button_input = MagicMock()
    
    input_config = {
        "type": "button",
        "button_type": "single",
        "name": "Test Button",
    }
    
    await manager._add_input_to_device(mock_vdsd, input_config)
    
    mock_vdsd.add_button_input.assert_called_once_with(
        button_type="single",
        name="Test Button",
    )


async def test_add_input_to_device_sensor(mock_vdsd):
    """Test adding sensor to device."""
    from custom_components.digitalstrom_vdc.device_manager import DeviceManager
    
    hass = MagicMock()
    mock_vdc = MagicMock()
    manager = DeviceManager(mock_vdc, hass)
    
    mock_vdsd.add_sensor = MagicMock()
    
    input_config = {
        "type": "sensor",
        "sensor_type": "temperature",
        "min_value": -40.0,
        "max_value": 80.0,
        "unit": "°C",
    }
    
    await manager._add_input_to_device(mock_vdsd, input_config)
    
    mock_vdsd.add_sensor.assert_called_once()


async def test_add_output_to_device(mock_vdsd):
    """Test adding output to device."""
    from custom_components.digitalstrom_vdc.device_manager import DeviceManager
    
    hass = MagicMock()
    mock_vdc = MagicMock()
    manager = DeviceManager(mock_vdc, hass)
    
    mock_output = MagicMock()
    mock_output.add_output_channel = MagicMock()
    mock_vdsd.create_output = MagicMock(return_value=mock_output)
    
    output_config = {
        "channels": [
            {
                "channel_type": "brightness",
                "min_value": 0.0,
                "max_value": 100.0,
                "initial_value": 0.0,
            }
        ]
    }
    
    await manager._add_output_to_device(mock_vdsd, output_config)
    
    mock_vdsd.create_output.assert_called_once()
    mock_output.add_output_channel.assert_called_once()


async def test_get_all_devices(mock_vdc, mock_vdsd):
    """Test getting all devices."""
    from custom_components.digitalstrom_vdc.device_manager import DeviceManager
    
    hass = MagicMock()
    manager = DeviceManager(mock_vdc, hass)
    
    manager._devices["device1"] = mock_vdsd
    manager._devices["device2"] = mock_vdsd
    
    devices = manager.get_all_devices()
    
    assert len(devices) == 2
    assert all(d == mock_vdsd for d in devices)
