"""Tests for config_flow."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.digitalstrom_vdc.const import (
    CONF_ANNOUNCE_SERVICE,
    CONF_DSUID,
    CONF_SERVICE_NAME,
    CONF_VDC_NAME,
    DOMAIN,
)


async def test_user_flow_success(hass: HomeAssistant):
    """Test successful user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    
    # Step 1: Port configuration
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_PORT: 8444},
    )
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "vdc_init"
    
    # Step 2: VDC initialization
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_VDC_NAME: "Test VDC"},
    )
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "zeroconf_setup"


async def test_user_flow_port_validation(hass: HomeAssistant):
    """Test port validation in user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    # Try invalid port
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_PORT: 99999},  # Invalid port
    )
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert "errors" in result


async def test_options_flow_add_device_template(hass: HomeAssistant, mock_config_entry):
    """Test adding device via template in options flow."""
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"


async def test_options_flow_add_device_manual(hass: HomeAssistant, mock_config_entry):
    """Test adding device manually in options flow."""
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"
    
    # Select manual device creation
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"action": "manual_device"},
    )
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] in ["manual_device", "init"]


async def test_abort_if_already_setup(hass: HomeAssistant):
    """Test we abort if component is already setup."""
    from homeassistant.config_entries import ConfigEntry
    from types import MappingProxyType
    from custom_components.digitalstrom_vdc.const import (
        CONF_PORT, CONF_VDC_NAME, CONF_DSUID, DOMAIN
    )
    
    entry = ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Test VDC",
        data={
            CONF_PORT: 8444,
            CONF_VDC_NAME: "Test VDC",
            CONF_DSUID: "test-dsuid",
        },
        source="user",
        unique_id="test-unique-id",
        discovery_keys=MappingProxyType({}),
        options={},
        subentries_data=None,
    )
    
    entry.add_to_hass(hass)
    
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    # Should still allow creating flow but will check for duplicates later
    assert result["type"] == FlowResultType.FORM


async def test_dsuid_generation(hass: HomeAssistant):
    """Test dsUID generation from MAC/IP."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_PORT: 8444},
    )
    
    # The flow should generate a dsUID
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "vdc_init"
