"""Template manager for digitalSTROM VDC integration."""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class TemplateManager:
    """Manage device templates from pyvdcapi."""

    def __init__(self) -> None:
        """Initialize template manager."""
        self._available_templates: dict[str, dict[str, Any]] = {}

    async def load_templates(self) -> None:
        """Load available templates from pyvdcapi."""
        _LOGGER.info("Loading device templates")
        
        try:
            # In a real implementation, we would:
            # 1. Scan pyvdcapi/templates/ directory
            # 2. Parse template YAML files
            # 3. Extract template descriptions
            # 4. Build UI-friendly template list
            
            # For now, we'll define some common templates based on pyvdcapi docs
            self._available_templates = {
                "simple_onoff_light": {
                    "type": "deviceType",
                    "name": "Simple On/Off Light",
                    "description": "Basic on/off light with brightness (0-100%)",
                    "parameters": [],
                    "bindings": ["brightness"],
                },
                "dimmable_light_with_scenes": {
                    "type": "deviceType",
                    "name": "Dimmable Light with Scenes",
                    "description": "Dimmer with scene presets",
                    "parameters": [],
                    "bindings": ["brightness"],
                },
                "wall_switch_single_button": {
                    "type": "deviceType",
                    "name": "Wall Switch (Single Button)",
                    "description": "Single button wall switch",
                    "parameters": [],
                    "bindings": ["button"],
                },
                "motorized_blinds": {
                    "type": "deviceType",
                    "name": "Motorized Blinds",
                    "description": "Position-controlled blinds",
                    "parameters": [],
                    "bindings": ["position"],
                },
                "temperature_humidity_sensor": {
                    "type": "deviceType",
                    "name": "Temperature & Humidity Sensor",
                    "description": "Combined climate sensor",
                    "parameters": [],
                    "bindings": ["temperature", "humidity"],
                },
                "philips_hue_lily_garden_spot": {
                    "type": "vendorType",
                    "name": "Philips HUE Lily Garden Spot",
                    "description": "Philips HUE RGB+White outdoor spotlight",
                    "parameters": [],
                    "bindings": ["brightness", "hue", "saturation"],
                },
            }
            
            _LOGGER.info("Loaded %d templates", len(self._available_templates))
            
        except Exception as err:
            _LOGGER.error("Failed to load templates: %s", err)
            self._available_templates = {}

    def get_available_templates(self) -> dict[str, dict[str, Any]]:
        """Get all available templates."""
        return self._available_templates

    def get_template(self, template_name: str) -> dict[str, Any] | None:
        """Get specific template by name."""
        return self._available_templates.get(template_name)

    def get_template_parameters(self, template_name: str) -> list[dict[str, Any]]:
        """Get required parameters for template."""
        template = self.get_template(template_name)
        if template:
            return template.get("parameters", [])
        return []

    def get_template_bindings(self, template_name: str) -> list[str]:
        """Get required entity bindings for template."""
        template = self.get_template(template_name)
        if template:
            return template.get("bindings", [])
        return []

    def get_templates_by_type(self, template_type: str) -> dict[str, dict[str, Any]]:
        """Get templates filtered by type (deviceType or vendorType)."""
        return {
            name: template
            for name, template in self._available_templates.items()
            if template.get("type") == template_type
        }
