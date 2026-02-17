"""Data update coordinator for digitalSTROM VDC integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL
from .vdc_manager import VDCHostManager

_LOGGER = logging.getLogger(__name__)


class DigitalStromVDCCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching digitalSTROM VDC data."""

    def __init__(self, hass: HomeAssistant, vdc_manager: VDCHostManager, config_entry: ConfigEntry | None = None) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
            config_entry=config_entry,
        )
        self.vdc_manager = vdc_manager

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from VDC."""
        try:
            # Query device states and return updated data
            # This will be expanded when devices are implemented
            return {
                "connection_state": self.vdc_manager.connection_state,
                "devices": {},  # Will be populated with actual device data
            }
        except Exception as err:
            _LOGGER.error("Error updating VDC data: %s", err)
            raise UpdateFailed(f"Error communicating with VDC: {err}") from err
