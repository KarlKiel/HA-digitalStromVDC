"""Button platform for digitalSTROM VDC integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
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
    """Set up digitalSTROM VDC buttons from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: DigitalStromVDCCoordinator = data[DATA_COORDINATOR]
    device_manager = data[DATA_DEVICE_MANAGER]

    # Get all devices with button inputs
    entities = []
    for device in device_manager.get_all_devices():
        # Check if device has button input components
        if hasattr(device, 'button_inputs') and device.button_inputs:
            # For each button, create a button entity
            for button_input in device.button_inputs:
                entities.append(
                    DigitalStromVDCButton(coordinator, device, button_input)
                )

    async_add_entities(entities)


class DigitalStromVDCButton(CoordinatorEntity, ButtonEntity):
    """Representation of a digitalSTROM VDC button."""

    def __init__(
        self,
        coordinator: DigitalStromVDCCoordinator,
        vdc_device: Any,
        button_input: Any,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._vdc_device = vdc_device
        self._button_input = button_input
        self._attr_unique_id = f"{vdc_device.dSUID}_{button_input.button_type}"
        self._attr_name = f"{vdc_device.name} {button_input.name}"

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("Button pressed: %s", self.name)
        
        # Trigger button press on VDC device if available
        if hasattr(self._button_input, 'press'):
            await self._button_input.press()
        
        # Fire event for automations
        self.hass.bus.async_fire(
            f"{DOMAIN}_button_press",
            {
                "device_id": self._vdc_device.dSUID,
                "button_name": self.name,
            },
        )

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
