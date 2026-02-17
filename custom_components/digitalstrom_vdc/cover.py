"""Cover platform for digitalSTROM VDC integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverEntity,
    CoverEntityFeature,
)
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
    """Set up digitalSTROM VDC covers from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: DigitalStromVDCCoordinator = data[DATA_COORDINATOR]
    device_manager = data[DATA_DEVICE_MANAGER]

    # Get all devices with cover/blind outputs
    entities = []
    for device in device_manager.get_all_devices():
        # Check if device is in blind group (DSGroup.BLIND)
        # DSGroup.BLIND = 4 in digitalSTROM
        if hasattr(device, 'primary_group') and device.primary_group == 4:
            entities.append(DigitalStromVDCCover(coordinator, device))
        # Also check for devices with shade/blind capabilities
        elif hasattr(device, 'output') and device.output:
            # Check if device has position control (typical for covers)
            if any(hasattr(ch, 'channel_type') and 'position' in ch.channel_type.lower() 
                   for ch in device.output.channels):
                entities.append(DigitalStromVDCCover(coordinator, device))

    async_add_entities(entities)


class DigitalStromVDCCover(CoordinatorEntity, CoverEntity):
    """Representation of a digitalSTROM VDC cover."""

    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(
        self,
        coordinator: DigitalStromVDCCoordinator,
        vdc_device: Any,
    ) -> None:
        """Initialize the cover."""
        super().__init__(coordinator)
        self._vdc_device = vdc_device
        self._attr_unique_id = vdc_device.dSUID
        self._attr_name = vdc_device.name

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of cover (0 closed, 100 open)."""
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            return None
            
        # Get position from first output channel
        primary_channel = self._vdc_device.output.channels[0]
        return int(primary_channel.value)

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        position = self.current_cover_position
        if position is None:
            return None
        return position == 0

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        _LOGGER.debug("Opening cover: %s", self.name)
        
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            _LOGGER.error("Device %s has no output channels", self.name)
            return
        
        # Set position to 100 (fully open)
        primary_channel = self._vdc_device.output.channels[0]
        await primary_channel.set_value(100.0)
        
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        _LOGGER.debug("Closing cover: %s", self.name)
        
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            _LOGGER.error("Device %s has no output channels", self.name)
            return
        
        # Set position to 0 (fully closed)
        primary_channel = self._vdc_device.output.channels[0]
        await primary_channel.set_value(0.0)
        
        await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        _LOGGER.debug("Stopping cover: %s", self.name)
        
        # Stop command - keep current position
        
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        position = kwargs.get(ATTR_POSITION)
        _LOGGER.debug("Setting cover %s position to %s", self.name, position)
        
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            _LOGGER.error("Device %s has no output channels", self.name)
            return
        
        # Set position value (0-100)
        primary_channel = self._vdc_device.output.channels[0]
        await primary_channel.set_value(float(position))
        
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
