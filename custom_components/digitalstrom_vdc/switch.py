"""Switch platform for digitalSTROM VDC integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DATA_DEVICE_MANAGER, DOMAIN
from .coordinator import DigitalStromVDCCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up digitalSTROM VDC switches from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: DigitalStromVDCCoordinator = data[DATA_COORDINATOR]
    device_manager = data[DATA_DEVICE_MANAGER]

    # Get all devices with output channels suitable for switches
    entities = []
    for device in device_manager.get_all_devices():
        # Check if device is suitable for switch (on/off only)
        # This would be based on output channel configuration
        # For now, we'll skip to avoid duplicates with lights
        pass

    async_add_entities(entities)


class DigitalStromVDCSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a digitalSTROM VDC switch."""

    def __init__(
        self,
        coordinator: DigitalStromVDCCoordinator,
        vdc_device: Any,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._vdc_device = vdc_device
        self._attr_unique_id = vdc_device.dSUID
        self._attr_name = vdc_device.name

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        # Get state from VDC device output channel
        return self._get_state() > 0

    def _get_state(self) -> float:
        """Get state value from VDC device."""
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            return 0.0
            
        # Get state from first output channel
        primary_channel = self._vdc_device.output.channels[0]
        return float(primary_channel.value)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.debug("Turning on switch: %s", self.name)
        
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            _LOGGER.error("Device %s has no output channels", self.name)
            return
        
        # Set output channel to 100 (full on)
        primary_channel = self._vdc_device.output.channels[0]
        await primary_channel.set_value(100.0)
        
        # Request coordinator update
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.debug("Turning off switch: %s", self.name)
        
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            _LOGGER.error("Device %s has no output channels", self.name)
            return
        
        # Set output channel to 0 (off)
        primary_channel = self._vdc_device.output.channels[0]
        await primary_channel.set_value(0.0)
        
        # Request coordinator update
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._vdc_device.dSUID)},
            "name": self._vdc_device.name,
            "manufacturer": "digitalSTROM VDC",
            "model": self._vdc_device.model,
            "via_device": (DOMAIN, self.coordinator.vdc_manager.host.dSUID),
        }
