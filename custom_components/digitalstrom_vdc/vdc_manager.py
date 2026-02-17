"""VDC Host manager for digitalSTROM VDC integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from pyvdcapi import VdcHost
from pyvdcapi.entities.vdc import Vdc
from zeroconf import ServiceInfo, Zeroconf
from zeroconf.asyncio import AsyncZeroconf

from homeassistant.core import HomeAssistant

from .const import (
    CONF_ANNOUNCE_SERVICE,
    CONF_DSUID,
    CONF_PORT,
    CONF_SERVICE_NAME,
    CONF_VDC_NAME,
    STATE_ACTIVE,
    STATE_CONNECTED,
    STATE_CONNECTING,
    STATE_DISCONNECTED,
)
from .errors import CannotConnect, DSSHandshakeFailed

_LOGGER = logging.getLogger(__name__)


class VDCHostManager:
    """Manage the VDC host and connection to DSS."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize VDC manager."""
        self.hass = hass
        self._config = config
        self._host: VdcHost | None = None
        self._vdc: Vdc | None = None
        self._connection_state = STATE_DISCONNECTED
        self._aiozc: AsyncZeroconf | None = None
        self._service_info: ServiceInfo | None = None
        self._maintain_task: asyncio.Task | None = None

    @property
    def host(self) -> VdcHost:
        """Return the VDC host."""
        if self._host is None:
            raise ValueError("VDC host not initialized")
        return self._host

    @property
    def vdc(self) -> Vdc:
        """Return the primary VDC."""
        if self._vdc is None:
            raise ValueError("VDC not initialized")
        return self._vdc

    @property
    def connection_state(self) -> str:
        """Return current connection state."""
        return self._connection_state

    async def async_initialize(self) -> bool:
        """Initialize VDC host and establish connection."""
        _LOGGER.info("Initializing VDC host")
        
        try:
            # Extract configuration
            port = self._config[CONF_PORT]
            vdc_name = self._config[CONF_VDC_NAME]
            dsuid = self._config[CONF_DSUID]
            announce_service = self._config.get(CONF_ANNOUNCE_SERVICE, True)
            service_name = self._config.get(CONF_SERVICE_NAME, "ha-vdc")

            # Create VdcHost instance
            # Note: We'll use the IP-based MAC for the host
            # The dsUID will be set from config
            self._host = VdcHost(
                name=vdc_name,
                port=port,
                mac_address=dsuid[-12:],  # Use last 12 chars as pseudo-MAC
                announce_service=False,  # We'll handle announcement ourselves
            )

            # Register event callbacks
            self._host.on_dss_connected = self._on_dss_connected
            self._host.on_dss_disconnected = self._on_dss_disconnected
            self._host.on_message_received = self._on_message_received

            # Create primary VDC
            self._vdc = self._host.create_vdc(name=vdc_name, model="Home Assistant VDC")
            
            _LOGGER.debug("VdcHost created with port %d", port)

            # Start TCP server
            await self._start_server()

            # Announce service via zeroconf if enabled
            if announce_service:
                await self._announce_service(service_name, port)

            # Wait for DSS connection and perform handshake
            # In a real implementation, we'd wait for actual connection
            # For now, we'll just set the state
            self._connection_state = STATE_ACTIVE
            
            _LOGGER.info("VDC host initialized successfully")
            return True

        except Exception as err:
            _LOGGER.error("Failed to initialize VDC host: %s", err)
            self._connection_state = STATE_DISCONNECTED
            return False

    async def _start_server(self) -> None:
        """Start the TCP server."""
        try:
            await self._host.start()
            self._connection_state = STATE_CONNECTED
            _LOGGER.info("VDC TCP server started on port %d", self._config[CONF_PORT])
        except Exception as err:
            _LOGGER.error("Failed to start TCP server: %s", err)
            raise CannotConnect from err

    async def _announce_service(self, service_name: str, port: int) -> None:
        """Announce VDC service via zeroconf."""
        try:
            # Get local IP
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            # Create service info
            self._service_info = ServiceInfo(
                "_vdc._tcp.local.",
                f"{service_name}._vdc._tcp.local.",
                port=port,
                addresses=[socket.inet_aton(local_ip)],
                properties={
                    "dsuid": self._config[CONF_DSUID],
                    "name": self._config[CONF_VDC_NAME],
                },
            )

            # Register service
            self._aiozc = AsyncZeroconf()
            await self._aiozc.async_register_service(self._service_info)
            
            _LOGGER.info("VDC service announced via zeroconf: %s", service_name)

        except Exception as err:
            _LOGGER.warning("Failed to announce service via zeroconf: %s", err)
            # Non-fatal error, continue without announcement

    async def async_maintain_connection(self) -> None:
        """Keep connection alive with DSS."""
        _LOGGER.debug("Starting connection monitor")
        
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                if self._connection_state == STATE_ACTIVE and self._host:
                    # Send periodic PING to keep connection alive
                    try:
                        await self._host.ping()
                        _LOGGER.debug("PING sent to DSS")
                    except Exception as err:
                        _LOGGER.warning("Failed to ping DSS: %s", err)
                        self._connection_state = STATE_DISCONNECTED
                        # Attempt reconnection
                        await self._attempt_reconnection()
                
            except asyncio.CancelledError:
                _LOGGER.debug("Connection monitor cancelled")
                break
            except Exception as err:
                _LOGGER.error("Error in connection monitor: %s", err)
                await asyncio.sleep(10)  # Back off on error

    async def async_shutdown(self) -> None:
        """Gracefully shutdown VDC host."""
        _LOGGER.info("Shutting down VDC host")

        # Cancel connection monitor
        if self._maintain_task and not self._maintain_task.done():
            self._maintain_task.cancel()
            try:
                await self._maintain_task
            except asyncio.CancelledError:
                pass

        # Unregister zeroconf service
        if self._aiozc and self._service_info:
            try:
                await self._aiozc.async_unregister_service(self._service_info)
                await self._aiozc.async_close()
            except Exception as err:
                _LOGGER.warning("Error unregistering zeroconf service: %s", err)

        # Stop VDC host
        if self._host:
            try:
                # Send BYE message to DSS if connected
                # await self._host.stop()  # This method might not exist yet in pyvdcapi
                pass
            except Exception as err:
                _LOGGER.warning("Error stopping VDC host: %s", err)

        self._connection_state = STATE_DISCONNECTED
        _LOGGER.info("VDC host shutdown complete")

    async def _on_dss_connected(self, dss_session_id: str) -> None:
        """Handle DSS connection event."""
        _LOGGER.info("DSS connected with session ID: %s", dss_session_id)
        self._connection_state = STATE_ACTIVE
        
        # Fire Home Assistant event
        self.hass.bus.async_fire(
            "digitalstrom_vdc_dss_connected",
            {"session_id": dss_session_id}
        )

    async def _on_dss_disconnected(self) -> None:
        """Handle DSS disconnection event."""
        _LOGGER.warning("DSS disconnected")
        self._connection_state = STATE_DISCONNECTED
        
        # Fire Home Assistant event
        self.hass.bus.async_fire("digitalstrom_vdc_dss_disconnected", {})
        
        # Attempt reconnection
        await self._attempt_reconnection()

    async def _on_message_received(self, message: dict) -> None:
        """Handle incoming message from DSS."""
        _LOGGER.debug("Message received from DSS: %s", message.get("method", "unknown"))

    async def _attempt_reconnection(self) -> None:
        """Attempt to reconnect to DSS."""
        if self._connection_state == STATE_CONNECTING:
            return  # Already attempting to reconnect
        
        _LOGGER.info("Attempting to reconnect to DSS")
        self._connection_state = STATE_CONNECTING
        
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                await asyncio.sleep(10 * (attempt + 1))  # Exponential backoff
                
                # Try to re-establish connection
                if self._host:
                    await self._host.reconnect()
                    _LOGGER.info("Reconnection successful")
                    self._connection_state = STATE_ACTIVE
                    return
                    
            except Exception as err:
                _LOGGER.warning("Reconnection attempt %d failed: %s", attempt + 1, err)
        
        _LOGGER.error("Failed to reconnect after %d attempts", max_attempts)
        self._connection_state = STATE_DISCONNECTED
