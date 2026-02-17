# digitalSTROM VDC Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/KarlKiel/HA-digitalStromVDC.svg)](https://github.com/KarlKiel/HA-digitalStromVDC/releases)
[![License](https://img.shields.io/github/license/KarlKiel/HA-digitalStromVDC.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/codecov/c/github/KarlKiel/HA-digitalStromVDC)](https://codecov.io/gh/KarlKiel/HA-digitalStromVDC)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A complete, production-ready Home Assistant integration for the digitalSTROM VDC-API. This integration enables Home Assistant to act as a Virtual Device Connector (vDC) host, allowing seamless integration with digitalSTROM Smart Services (dSS) through the VDC-API protocol.

**Built with:** `pyvdcapi` | **Integration Type:** Hub | **IoT Class:** Local Push | **Platforms:** 7

## Features

✅ **HACS Compliant** - Easy installation via HACS  
✅ **Async-First** - Built on asyncio for optimal performance  
✅ **Config Flow Based** - UI-based configuration, no YAML editing  
✅ **Template System** - Quick device deployment using predefined templates  
✅ **Manual Device Creation** - Full control over device configuration  
✅ **Bidirectional Sync** - HA ↔ dSS state synchronization  
✅ **Zeroconf Discovery** - Automatic service announcement  
✅ **Multiple Platforms** - Light, Switch, Sensor, Binary Sensor, Cover, Climate, Button  
✅ **Scene Management** - Save, recall, and manage digitalSTROM scenes  
✅ **Local Push** - Real-time updates via VDC-API protocol

## Supported Platforms

- **Light** - Brightness, RGB, RGBW lights
- **Switch** - On/off devices
- **Sensor** - Temperature, humidity, power sensors
- **Binary Sensor** - Motion, contact, occupancy sensors
- **Cover** - Blinds, shades with position control
- **Climate** - Heating/cooling devices
- **Button** - Button inputs with click detection

## Prerequisites

- Home Assistant 2024.1.0 or newer
- digitalSTROM Smart Service (dSS) on your network
- Network connectivity between Home Assistant and dSS

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository: `https://github.com/KarlKiel/HA-digitalStromVDC`
6. Select category "Integration"
7. Click "Add"
8. Find "digitalSTROM VDC Integration" in HACS
9. Click "Download"
10. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/KarlKiel/HA-digitalStromVDC/releases)
2. Extract the `custom_components/digitalstrom_vdc` directory to your Home Assistant's `custom_components` folder
3. Restart Home Assistant

## Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "digitalSTROM VDC"
4. Follow the configuration wizard:
   - **Step 1**: Configure TCP port (default: 8444)
   - **Step 2**: Set VDC name and confirm generated dsUID
   - **Step 3**: Configure Zeroconf service announcement
   - **Step 4**: Complete setup and connect to dSS

### Adding Devices

After initial setup, you can add devices:

1. Go to the integration page
2. Click **Configure** on your digitalSTROM VDC integration
3. Choose device creation method:
   - **From Template**: Quick setup using predefined templates
   - **Manual**: Full control over device configuration

#### Template-Based Device Creation

1. Select a template (e.g., "Simple On/Off Light")
2. Configure template parameters
3. Bind to Home Assistant entities
4. Device is created and announced to dSS

#### Manual Device Creation

1. Configure general device parameters (name, group, zone)
2. Add inputs (buttons, binary inputs, sensors)
3. Add output channels
4. Bind components to Home Assistant entities
5. Device is created and announced to dSS

## Available Templates

### Device Type Templates
- `simple_onoff_light` - Basic on/off light (0-100%)
- `dimmable_light_with_scenes` - Dimmer with scene presets
- `wall_switch_single_button` - Single button wall switch
- `motorized_blinds` - Position-controlled blinds
- `temperature_humidity_sensor` - Combined climate sensor

### Vendor Type Templates
- `philips_hue_lily_garden_spot` - Philips HUE RGB+White outdoor spotlight

## Services

The integration provides 8 services for advanced control:

### Scene Management

#### `digitalstrom_vdc.call_scene`
Call a digitalSTROM scene on a device.

```yaml
service: digitalstrom_vdc.call_scene
target:
  device_id: abc123...
data:
  scene: 17  # Scene number (0-127)
  force: false  # Optional: force scene call
```

#### `digitalstrom_vdc.save_scene`
Save current device state as a scene.

```yaml
service: digitalstrom_vdc.save_scene
target:
  device_id: abc123...
data:
  scene: 50  # Scene number to save to
```

#### `digitalstrom_vdc.undo_scene`
Undo the last scene call.

```yaml
service: digitalstrom_vdc.undo_scene
target:
  device_id: abc123...
data:
  scene: 17
```

#### `digitalstrom_vdc.call_min_scene`
Call minimum scene value.

```yaml
service: digitalstrom_vdc.call_min_scene
target:
  device_id: abc123...
data:
  scene: 5
  channel: 0
```

### Device Control

#### `digitalstrom_vdc.dim_channel`
Dim output channel in specified direction.

```yaml
service: digitalstrom_vdc.dim_channel
target:
  device_id: abc123...
data:
  channel: 0  # Channel index
  direction: 1  # 1 = up, -1 = down
  duration: 5.0  # Dimming duration in seconds
```

#### `digitalstrom_vdc.set_local_priority`
Set local priority for a device.

```yaml
service: digitalstrom_vdc.set_local_priority
target:
  device_id: abc123...
data:
  priority: true
```

### Management Services

#### `digitalstrom_vdc.announce_device`
Manually announce a device to dSS.

```yaml
service: digitalstrom_vdc.announce_device
target:
  device_id: abc123...
data:
  force: true  # Force re-announcement
```

#### `digitalstrom_vdc.refresh_templates`
Reload available device templates from configuration.

```yaml
service: digitalstrom_vdc.refresh_templates
# No parameters required
```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to dSS  
**Solution**: 
- Verify network connectivity between Home Assistant and dSS
- Check that the configured port is not blocked by firewall
- Ensure dSS is configured to accept VDC connections
- Verify the VDC host is started (check HA logs)
- Test TCP connectivity: `telnet <ha_ip> 8444`

**Problem**: Port already in use  
**Solution**: 
- Choose a different port in configuration
- Check if another integration is using the same port
- Verify no other VDC applications are running

**Problem**: Connection drops frequently  
**Solution**:
- Check network stability between HA and dSS
- Review PING/PONG interval settings in logs
- Verify firewall is not closing idle connections
- Check if dSS has connection limits

### Device Issues

**Problem**: Device not appearing in dSS  
**Solution**:
- Use the `announce_device` service to manually trigger announcement
- Check dSS logs for connection errors
- Verify device configuration in Home Assistant
- Ensure device has valid dsUID (check integration config)
- Verify primary group assignment matches dSS expectations

**Problem**: Entity binding not working  
**Solution**:
- Check that bound entity exists in Home Assistant
- Verify entity domain matches channel type (e.g., light for brightness)
- Review entity binding configuration in device options
- Enable debug logging to see sync events

**Problem**: Scenes not working  
**Solution**:
- Verify device supports scenes (check device capabilities)
- Ensure scene numbers are in valid range (0-127)
- Check if device is in a scene-compatible group
- Use `save_scene` service to create scenes first

### Performance Issues

**Problem**: Slow state updates  
**Solution**:
- Check coordinator update interval in logs
- Verify network latency to dSS
- Review number of devices and bindings
- Consider reducing polling frequency if not using push updates

### Debug Logging

Enable debug logging to troubleshoot issues:

```yaml
logger:
  default: info
  logs:
    custom_components.digitalstrom_vdc: debug
    pyvdcapi: debug
```

For more detailed troubleshooting, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Development

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## Architecture

This integration leverages the [`pyvdcapi`](https://github.com/KarlKiel/pyvdcapi) library for VDC-API protocol implementation. The architecture consists of:

- **VDC Host Manager** - Manages TCP server and dSS connection
- **Device Manager** - Handles device lifecycle and creation
- **Template Manager** - Provides template-based device deployment
- **Coordinator** - Manages data updates and state synchronization
- **Entity Bindings** - Bidirectional HA ↔ VDC synchronization

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Credits

- **pyvdcapi** library by [@KarlKiel](https://github.com/KarlKiel)
- digitalSTROM VDC-API specification

## Support

- **Issues**: [GitHub Issues](https://github.com/KarlKiel/HA-digitalStromVDC/issues)
- **Discussions**: [Home Assistant Community](https://community.home-assistant.io/)
- **Documentation**: [docs/](docs/)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**Version**: 0.1.0  
**Status**: Beta - Testing Phase  
**Test Coverage**: 50+ tests, 1,062 test lines  
**Last Updated**: February 16, 2026
