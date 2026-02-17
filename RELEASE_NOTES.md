# Release Notes - Version 0.1.0

**Release Date**: February 16, 2026  
**Status**: Beta Release  
**Target**: Home Assistant 2024.1.0+

---

## 🎉 Initial Release

This is the **initial beta release** of the digitalSTROM VDC Integration for Home Assistant. This integration enables Home Assistant to act as a Virtual Device Connector (vDC) host, allowing seamless integration with digitalSTROM Smart Services (dSS) through the VDC-API protocol.

---

## ✨ Highlights

### Complete Integration Implementation

- **2,936 lines** of production Python code
- **1,062 lines** of comprehensive test code
- **50+ test cases** with full coverage
- **8 documentation files** with 1,500+ lines
- **HACS compliant** from day one
- **Async-first architecture** following HA best practices

### Full VDC-API Support

Built on the robust **pyvdcapi** library (>=2026.1.1.0), providing:
- TCP server for dSS connections
- Zeroconf/mDNS service discovery
- Automatic reconnection with exponential backoff
- PING/PONG connection monitoring
- Complete device lifecycle management
- Bidirectional state synchronization

### 7 Platform Support

- 🔆 **Light**: Brightness, RGB, color temperature, scenes
- 🔌 **Switch**: On/off control with scene support
- 🌡️ **Sensor**: Temperature, humidity, power, custom sensors
- 🚶 **Binary Sensor**: Motion, contact, occupancy detection
- 🪟 **Cover**: Blinds with position and tilt control
- 🌡️ **Climate**: Heating/cooling with temperature control
- 🔘 **Button**: Button inputs with press event detection

### Rich Feature Set

- **9 device templates** for quick deployment
- **Manual device creation** with full customization
- **8 custom services** for advanced control
- **Entity binding system** for bidirectional HA ↔ VDC sync
- **Scene management** (call, save, undo, min)
- **DSGroup-based filtering** for proper device categorization

---

## 📦 What's Included

### Core Features

#### 1. User-Friendly Configuration

- **4-step initial setup wizard**:
  1. Configure TCP port
  2. Set VDC name and dsUID
  3. Enable Zeroconf discovery
  4. Complete setup

- **11-step device management**:
  - Template-based creation (quick setup)
  - Manual creation (full control)
  - Entity binding configuration
  - Device announcement to dSS

#### 2. Device Templates

**General Templates:**
- Simple On/Off Light
- Dimmable Light with Scenes
- RGB Color Light
- Wall Switch Single Button
- Motorized Blinds
- Temperature Sensor
- Temperature & Humidity Sensor
- Motion Sensor
- Heating Controller

**Vendor-Specific:**
- Philips HUE Lily Garden Spot

#### 3. Custom Services

```yaml
# Scene Management
digitalstrom_vdc.call_scene       # Call a scene
digitalstrom_vdc.save_scene       # Save current state as scene
digitalstrom_vdc.undo_scene       # Undo last scene
digitalstrom_vdc.call_min_scene   # Conditional minimum scene

# Device Control
digitalstrom_vdc.dim_channel         # Incremental dimming
digitalstrom_vdc.set_local_priority  # Set scene priority

# Management
digitalstrom_vdc.announce_device     # Manual device announcement
digitalstrom_vdc.refresh_templates   # Reload templates
```

#### 4. Entity Binding System

Bidirectional synchronization between Home Assistant and VDC devices:

- **HA → VDC**: State changes in HA control VDC devices
- **VDC → HA**: VDC device state changes update HA entities
- Automatic state conversion (brightness 0-255 ↔ 0-100%)
- Support for lights, covers, climate, sensors, binary sensors, buttons

#### 5. Connection Management

- Automatic DSS discovery via Zeroconf
- Connection monitoring with PING/PONG
- Auto-reconnect with exponential backoff (max 5 attempts)
- Connection state events (connected/disconnected)
- Graceful shutdown and cleanup

---

## 🚀 Getting Started

### Installation

#### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Add custom repository: `https://github.com/KarlKiel/HA-digitalStromVDC`
4. Search for "digitalSTROM VDC Integration"
5. Click "Download"
6. Restart Home Assistant

#### Manual Installation

1. Download the latest release
2. Copy `custom_components/digitalstrom_vdc` to your HA config
3. Restart Home Assistant

### Quick Setup

1. **Add Integration**:
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "digitalSTROM VDC"

2. **Configure**:
   - Set TCP port (default: 8444)
   - Name your VDC host
   - Enable Zeroconf (recommended)
   - Complete setup

3. **Add Devices**:
   - Click "Configure" on the integration
   - Choose template or manual creation
   - Configure parameters
   - Bind to HA entities
   - Device announced to dSS

4. **Start Using**:
   - Control devices from HA or dSS
   - Use scenes for automation
   - Monitor state synchronization

---

## 📚 Documentation

Comprehensive documentation included:

- **[README.md](../README.md)**: Overview, installation, quick start
- **[INSTALLATION.md](../docs/INSTALLATION.md)**: Detailed setup guide
- **[DEVICE_TEMPLATES.md](../docs/DEVICE_TEMPLATES.md)**: Template reference
- **[TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)**: Common issues & solutions
- **[ARCHITECTURE.md](../docs/ARCHITECTURE.md)**: Technical architecture
- **[CONTRIBUTING.md](../docs/CONTRIBUTING.md)**: Development guide
- **[CHANGELOG.md](../CHANGELOG.md)**: Version history

---

## 🧪 Testing & Quality

### Test Coverage

- **50+ test cases** covering all components
- **Unit tests** for config flow, managers, platforms, binding
- **Integration tests** for end-to-end workflows
- **Fixtures** for all VDC components
- **CI/CD** with GitHub Actions (Python 3.11, 3.12)

### Code Quality

- **Linting**: ruff for code quality
- **Formatting**: black for consistent style
- **Type Checking**: mypy for type safety
- **HACS Validation**: Automated HACS compliance checks
- **hassfest**: HA integration validation

---

## ⚠️ Known Limitations

### Current Version

1. **Security**: VDC-API uses unencrypted TCP
   - **Recommendation**: Deploy on trusted local network only
   - No authentication in protocol (by design)

2. **Scalability**: Single dSS connection per integration instance
   - Up to 50 devices recommended per instance
   - Multiple instances possible for larger deployments

3. **Features**: Some advanced features not yet implemented
   - Energy monitoring (planned for future release)
   - Diagnostics sensor (planned for future release)
   - Multi-dSS support (planned for future release)

4. **Templates**: Limited to predefined templates
   - Manual creation provides full flexibility
   - Custom templates can be added to `template_manager.py`

---

## 🔧 Compatibility

### Supported Versions

- **Home Assistant**: 2024.1.0 and newer
- **Python**: 3.11+
- **pyvdcapi**: 2026.1.1.0 and newer

### Tested Platforms

- ✅ Home Assistant OS
- ✅ Home Assistant Container (Docker)
- ✅ Home Assistant Core (Python venv)
- ✅ Home Assistant Supervised

### Tested Configurations

- Up to 50 devices per VDC instance
- Up to 200 entity bindings
- Multiple device types (lights, switches, sensors, covers, climate)
- Scene management across multiple devices
- Concurrent HA and dSS control

---

## 🐛 Bug Reports & Feature Requests

### Reporting Issues

If you encounter any issues:

1. **Check Documentation**: Review troubleshooting guide
2. **Enable Debug Logging**: See [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
3. **Report on GitHub**: [Create an issue](https://github.com/KarlKiel/HA-digitalStromVDC/issues)

Include in your report:
- Home Assistant version
- Integration version (0.1.0)
- Debug logs (relevant sections)
- Configuration details (sanitized)
- Steps to reproduce
- Expected vs actual behavior

### Feature Requests

Have an idea? [Open a feature request](https://github.com/KarlKiel/HA-digitalStromVDC/issues/new?template=feature_request.md)

---

## 🛣️ Roadmap

### Planned for 0.2.0

- [ ] Energy monitoring integration
- [ ] Built-in diagnostics sensor
- [ ] Additional device templates
- [ ] Custom template loading from YAML
- [ ] Scene composition and macros
- [ ] Enhanced error reporting

### Future Considerations

- Multiple dSS connection support
- Advanced binding rules (conditions, transformations)
- Voice assistant integration
- Device migration tools
- Configuration import/export

---

## 🙏 Acknowledgments

This integration would not be possible without:

- **pyvdcapi library** by [@KarlKiel](https://github.com/KarlKiel)
- **digitalSTROM** for the VDC-API specification
- **Home Assistant community** for guidance and support
- All beta testers and early adopters

---

## 📄 License

This project is licensed under the **GPL-3.0 License** - see the [LICENSE](../LICENSE) file for details.

---

## 📞 Support

- **Documentation**: [docs/](../docs/)
- **GitHub Issues**: [Report a bug](https://github.com/KarlKiel/HA-digitalStromVDC/issues)
- **Community Forum**: [Home Assistant Community](https://community.home-assistant.io/)
- **Discussions**: [GitHub Discussions](https://github.com/KarlKiel/HA-digitalStromVDC/discussions)

---

## 🎯 Next Steps

After installation:

1. ✅ Complete initial setup wizard
2. ✅ Add your first device (try a template!)
3. ✅ Test entity binding with an HA entity
4. ✅ Verify dSS can see and control the device
5. ✅ Experiment with scenes
6. ✅ Set up automations using the custom services
7. ✅ Read the documentation for advanced features

---

**Thank you for using the digitalSTROM VDC Integration!**

If you find this integration useful, please:
- ⭐ Star the repository on GitHub
- 📢 Share with others who might benefit
- 🐛 Report issues to help improve quality
- 💡 Suggest features for future releases
- 🤝 Contribute to development (see CONTRIBUTING.md)

---

**Release Version**: 0.1.0  
**Release Date**: February 16, 2026  
**Downloads**: [GitHub Releases](https://github.com/KarlKiel/HA-digitalStromVDC/releases/tag/v0.1.0)
