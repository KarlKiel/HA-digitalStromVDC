"""Fixtures for digitalSTROM VDC integration tests."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant

from custom_components.digitalstrom_vdc.const import (
    CONF_ANNOUNCE_SERVICE,
    CONF_DSUID,
    CONF_SERVICE_NAME,
    CONF_VDC_NAME,
    DOMAIN,
)

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture(autouse=True)
def socket_enabled(socket_enabled):
    """Enable socket operations for all tests."""
    yield


@pytest.fixture
def mock_vdc_host():
    """Return a mocked VdcHost."""
    mock = MagicMock()
    mock.start = AsyncMock()
    mock.ping = AsyncMock()
    mock.reconnect = AsyncMock()
    mock.create_vdc = MagicMock()
    mock.on_dss_connected = None
    mock.on_dss_disconnected = None
    mock.on_message_received = None
    return mock


@pytest.fixture
def mock_vdc():
    """Return a mocked Vdc."""
    mock = MagicMock()
    mock.create_vdsd = MagicMock()
    mock.create_vdsd_from_template = MagicMock()
    mock.name = "Test VDC"
    return mock


@pytest.fixture
def mock_vdsd():
    """Return a mocked VdSD device."""
    mock = MagicMock()
    mock.dSUID = "test-dsuid-12345"
    mock.name = "Test Device"
    mock.model = "Test Model"
    mock.primary_group = 1
    mock.announce = AsyncMock()
    mock.call_scene = AsyncMock()
    mock.save_scene = AsyncMock()
    mock.undo_scene = AsyncMock()
    mock.call_min_scene = AsyncMock()
    mock.set_local_prio = AsyncMock()
    
    # Mock output
    mock.output = MagicMock()
    mock.output.channels = []
    
    # Mock sensors, inputs, buttons
    mock.sensors = []
    mock.binary_inputs = []
    mock.button_inputs = []
    
    return mock


@pytest.fixture
def mock_output_channel():
    """Return a mocked OutputChannel."""
    mock = MagicMock()
    mock.value = 0.0
    mock.channel_type = "brightness"
    mock.set_value = AsyncMock()
    mock.dim_up = AsyncMock()
    mock.dim_down = AsyncMock()
    mock.dim_stop = AsyncMock()
    return mock


@pytest.fixture
def mock_sensor():
    """Return a mocked Sensor."""
    mock = MagicMock()
    mock.value = 20.5
    mock.sensor_type = "temperature"
    mock.unit = "°C"
    mock.on_value_changed = MagicMock()
    return mock


@pytest.fixture
def mock_binary_input():
    """Return a mocked BinaryInput."""
    mock = MagicMock()
    mock.state = False
    mock.input_type = "motion"
    mock.name = "Motion Sensor"
    mock.on_state_changed = MagicMock()
    return mock


@pytest.fixture
def mock_button_input():
    """Return a mocked ButtonInput."""
    mock = MagicMock()
    mock.button_type = "single"
    mock.name = "Button"
    mock.press = AsyncMock()
    mock.on_button_pressed = MagicMock()
    mock.on_pressed = MagicMock()  # Alias for test compatibility
    return mock


@pytest.fixture
def mock_config_entry_data():
    """Return mock config entry data."""
    return {
        CONF_PORT: 8444,
        CONF_VDC_NAME: "Test VDC",
        CONF_DSUID: "test-dsuid-abcdef123456",
        CONF_ANNOUNCE_SERVICE: True,
        CONF_SERVICE_NAME: "test-vdc",
    }


@pytest.fixture
def mock_config_entry(mock_config_entry_data):
    """Return a mock config entry."""
    from homeassistant.config_entries import ConfigEntry
    from types import MappingProxyType
    
    return ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Test VDC",
        data=mock_config_entry_data,
        source="user",
        unique_id="test-unique-id",
        discovery_keys=MappingProxyType({}),
        options={},
        subentries_data=None,
    )


@pytest.fixture
def mock_setup_entry():
    """Mock setup entry."""
    with patch(
        "custom_components.digitalstrom_vdc.async_setup_entry",
        return_value=True,
    ) as mock_setup:
        yield mock_setup


@pytest.fixture
async def mock_vdc_manager(mock_vdc_host, mock_vdc, mock_config_entry_data):
    """Return a mocked VDCHostManager."""
    with patch(
        "custom_components.digitalstrom_vdc.vdc_manager.VdcHost",
        return_value=mock_vdc_host,
    ):
        mock_vdc_host.create_vdc.return_value = mock_vdc
        from custom_components.digitalstrom_vdc.vdc_manager import VDCHostManager
        
        manager = VDCHostManager(MagicMock(), mock_config_entry_data)
        
        yield manager


@pytest.fixture
def mock_coordinator():
    """Return a mocked coordinator."""
    mock = MagicMock()
    mock.async_request_refresh = AsyncMock()
    mock.data = {}
    return mock


@pytest.fixture
async def integration_setup(
    hass: HomeAssistant,
    mock_config_entry,
):
    """Set up the integration with a mocked config entry."""
    return mock_config_entry
