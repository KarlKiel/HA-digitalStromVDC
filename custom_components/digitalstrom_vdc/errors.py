"""Custom exceptions for digitalSTROM VDC integration."""


class DigitalStromVDCError(Exception):
    """Base exception for digitalSTROM VDC integration."""


class CannotConnect(DigitalStromVDCError):
    """Error to indicate we cannot connect to DSS."""


class InvalidPort(DigitalStromVDCError):
    """Error to indicate invalid port number."""


class PortInUse(DigitalStromVDCError):
    """Error to indicate port is already in use."""


class DSSHandshakeFailed(DigitalStromVDCError):
    """Error to indicate DSS handshake failed."""


class InvalidDsUID(DigitalStromVDCError):
    """Error to indicate invalid dsUID."""


class DeviceNotFound(DigitalStromVDCError):
    """Error to indicate device not found."""


class TemplateNotFound(DigitalStromVDCError):
    """Error to indicate template not found."""


class InvalidTemplate(DigitalStromVDCError):
    """Error to indicate invalid template configuration."""


class BindingError(DigitalStromVDCError):
    """Error to indicate entity binding failed."""


class DeviceAnnounceFailed(DigitalStromVDCError):
    """Error to indicate device announcement to DSS failed."""
