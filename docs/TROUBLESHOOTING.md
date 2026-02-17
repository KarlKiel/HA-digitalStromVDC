# Troubleshooting Guide

Comprehensive troubleshooting guide for the digitalSTROM VDC Integration.

## Table of Contents

- [Connection Issues](#connection-issues)
- [Configuration Problems](#configuration-problems)
- [Device Issues](#device-issues)
- [Entity Binding Problems](#entity-binding-problems)
- [Scene Management Issues](#scene-management-issues)
- [Performance Issues](#performance-issues)
- [Error Messages](#error-messages)
- [Debug Logging](#debug-logging)
- [Common Workflows](#common-workflows)

---

## Connection Issues

### Cannot Connect to dSS

**Symptoms:**
- Integration shows "Connection Failed" in logs
- VDC host cannot establish TCP connection
- dSS doesn't see the VDC host

**Diagnosis:**
```yaml
# Check logs for:
ERROR (MainThread) [custom_components.digitalstrom_vdc.vdc_manager] Failed to connect to dSS
WARNING (MainThread) [pyvdcapi] TCP connection timeout
```

**Solutions:**

1. **Verify Network Connectivity**
   ```bash
   # From Home Assistant host, test connectivity
   ping <dss_ip_address>
   
   # Test TCP port accessibility
   telnet <ha_ip_address> 8444
   nc -zv <ha_ip_address> 8444
   ```

2. **Check Firewall Rules**
   - Ensure port 8444 (or configured port) is open on HA host
   - Verify no firewall blocks between HA and dSS
   - Check router/switch ACLs

3. **Verify VDC Host Configuration**
   - Check integration configuration for correct port
   - Ensure port is not already in use by another service
   - Verify VDC host is started (check logs for "VDC host started")

4. **dSS Configuration**
   - Ensure dSS is configured to accept VDC connections
   - Check dSS firewall/security settings
   - Verify dSS has available connection slots

### Port Already in Use

**Symptoms:**
```
ERROR [custom_components.digitalstrom_vdc] Port 8444 already in use
OSError: [Errno 98] Address already in use
```

**Solutions:**

1. **Find Process Using Port**
   ```bash
   # Linux
   sudo lsof -i :8444
   sudo netstat -tlnp | grep 8444
   
   # Check if another VDC integration is running
   ps aux | grep vdc
   ```

2. **Change Configuration**
   - Go to Integration → Configure
   - Change TCP port to unused port (e.g., 8445, 8446)
   - Restart integration

3. **Stop Conflicting Service**
   - Identify and stop the conflicting application
   - Consider using systemd socket activation for port sharing (advanced)

### Connection Drops Frequently

**Symptoms:**
- Connection established but drops after minutes/hours
- Repeated reconnection attempts in logs
- Devices disappear from dSS intermittently

**Diagnosis:**
```yaml
# Check for pattern in logs:
INFO [custom_components.digitalstrom_vdc.vdc_manager] DSS disconnected
INFO [custom_components.digitalstrom_vdc.vdc_manager] Attempting reconnection (attempt 1/5)
```

**Solutions:**

1. **Check Network Stability**
   - Test for packet loss: `ping -c 100 <dss_ip>`
   - Check for network congestion or interference
   - Verify Ethernet cable quality (if wired)

2. **Adjust Monitoring Settings**
   - PING/PONG interval may be too aggressive
   - Check logs for PING timeout messages
   - Consider network latency in monitoring configuration

3. **Firewall Idle Timeout**
   - Some firewalls close idle connections
   - Adjust firewall settings to allow persistent connections
   - Consider keep-alive settings

4. **dSS Resource Limits**
   - Check if dSS has connection limits
   - Verify dSS logs for resource exhaustion
   - Restart dSS if memory leaks suspected

### Zeroconf/mDNS Not Working

**Symptoms:**
- Service not discoverable on network
- dSS doesn't automatically find VDC host

**Solutions:**

1. **Check Zeroconf Service**
   ```bash
   # Verify mDNS is running
   systemctl status avahi-daemon  # Linux
   
   # Check for service announcement
   avahi-browse -a | grep digitalstrom
   dns-sd -B _vdc._tcp  # macOS
   ```

2. **Network Configuration**
   - Ensure multicast is enabled on network
   - Check if VLAN/subnet isolation blocks mDNS
   - Verify port 5353 (mDNS) is not blocked

3. **Disable/Re-enable Zeroconf**
   - Go to Integration → Configure → Options
   - Disable Zeroconf, save, then re-enable
   - Check if service name conflicts exist

---

## Configuration Problems

### Invalid dsUID Generated

**Symptoms:**
- dSS rejects device announcements
- Duplicate dsUID errors in dSS logs

**Solutions:**

1. **Regenerate dsUID**
   - Remove integration
   - Re-add integration (new dsUID will be generated)
   - Alternatively, manually specify dsUID in config

2. **Check dsUID Format**
   - Must be unique 34-character hex string
   - Format: `AABBCCDDEEFF00112233445566778899AABB`
   - Use VDC-API compliant generator

### Configuration Flow Validation Errors

**Symptoms:**
- Cannot complete configuration wizard
- Port validation fails
- Name validation fails

**Solutions:**

1. **Port Validation**
   - Use ports between 1024-65535
   - Avoid well-known ports (80, 443, 22, etc.)
   - Check port is not reserved by OS

2. **Name Validation**
   - VDC name must be 1-64 characters
   - Avoid special characters
   - Use alphanumeric and spaces only

3. **Network Validation**
   - Ensure Home Assistant has network access
   - Check if running in Docker with proper network mode
   - Verify no network namespace isolation

---

## Device Issues

### Device Not Appearing in dSS

**Symptoms:**
- Device created in Home Assistant
- Not visible in dSS device list
- No errors in HA logs

**Diagnosis:**
```yaml
# Enable debug logging and check for:
DEBUG [custom_components.digitalstrom_vdc.vdc_manager] Announcing device <dsuid>
DEBUG [pyvdcapi] Device announcement sent
```

**Solutions:**

1. **Manual Device Announcement**
   ```yaml
   service: digitalstrom_vdc.announce_device
   target:
     device_id: <your_device_id>
   data:
     force: true
   ```

2. **Check VDC Host Connection**
   - Verify VDC host is connected to dSS
   - Check connection status in integration card
   - Review vdc_manager logs for connection state

3. **Verify Device Configuration**
   - Ensure device has valid dsUID
   - Check primary group is set correctly
   - Verify device is not in disabled state

4. **dSS-Side Checks**
   - Check dSS logs for rejection messages
   - Verify dSS accepts the device group type
   - Ensure dSS has available device slots
   - Check if dSS is in pairing/learning mode

### Device Shows in dSS but Not Controllable

**Symptoms:**
- Device visible in dSS
- Cannot control device from dSS
- HA entity states don't sync

**Solutions:**

1. **Check Entity Binding**
   - Verify bound entities exist in HA
   - Ensure entities are not disabled
   - Check entity state is valid (not `unavailable` or `unknown`)

2. **Review Component Configuration**
   - Ensure output channels are configured
   - Verify channel types match device expectations
   - Check for proper channel indexing

3. **Test Direct Control**
   ```yaml
   # Test channel control directly
   service: digitalstrom_vdc.dim_channel
   target:
     device_id: <device_id>
   data:
     channel: 0
     direction: 1
     duration: 5.0
   ```

### Device State Not Updating

**Symptoms:**
- Device controlled from dSS but HA state doesn't update
- HA state changes don't reflect in dSS

**Solutions:**

1. **Check Coordinator Updates**
   - Verify coordinator is running
   - Check update interval in logs
   - Ensure no coordinator errors

2. **Review Entity Binding**
   - Confirm bidirectional binding is active
   - Check for entity state listener registration
   - Verify callback registration on VDC components

3. **Enable State Change Logging**
   ```yaml
   logger:
     logs:
       custom_components.digitalstrom_vdc.entity_binding: debug
   ```

---

## Entity Binding Problems

### Binding Not Created

**Symptoms:**
- Configure entity binding during device setup
- Binding doesn't appear to work
- No sync between HA and VDC

**Solutions:**

1. **Verify Entity Exists**
   ```yaml
   # Check in Developer Tools → States
   # Ensure entity_id matches exactly (case-sensitive)
   ```

2. **Check Entity Domain**
   - Brightness channel → must bind to `light` entity
   - Position channel → must bind to `cover` entity
   - Sensor → must bind to `sensor` entity
   - Binary input → must bind to `binary_sensor` entity
   - Button → must bind to `button` entity

3. **Review Binding Configuration**
   - Ensure binding is created during device setup
   - Check options flow if modifying existing device
   - Verify syntax in binding dictionary

### State Sync Only Works One Direction

**Symptoms:**
- HA → VDC works but not VDC → HA (or vice versa)

**Solutions:**

1. **Check Callback Registration**
   ```yaml
   # Enable debug logging
   DEBUG [custom_components.digitalstrom_vdc.entity_binding] Registered callback for sensor_0
   DEBUG [pyvdcapi] Value changed callback triggered
   ```

2. **Verify Listener Setup**
   - HA state listener must be registered for HA → VDC
   - VDC callbacks must be registered for VDC → HA
   - Check for registration errors in logs

3. **Test Each Direction**
   ```yaml
   # Test HA → VDC
   service: light.turn_on
   target:
     entity_id: light.test
   data:
     brightness: 128
   
   # Then check VDC channel value in logs
   ```

### State Conversion Issues

**Symptoms:**
- State updates but with incorrect values
- Brightness appears wrong
- Position inverted

**Solutions:**

1. **Brightness Conversion**
   - HA brightness: 0-255
   - VDC brightness: 0-100
   - Check conversion factor: `vdc_value = (ha_value / 255) * 100`

2. **Position Conversion**
   - HA cover: 0 (closed) to 100 (open)
   - VDC blinds: May be inverted based on device
   - Check device-specific position semantics

3. **Temperature Conversion**
   - Ensure unit consistency (°C vs °F)
   - Check sensor configuration for unit

---

## Scene Management Issues

### Scenes Not Saving

**Symptoms:**
```yaml
service: digitalstrom_vdc.save_scene
# No error but scene not saved
```

**Solutions:**

1. **Verify Device Supports Scenes**
   - Check device configuration for scene support
   - Review device group (some groups don't support scenes)
   - Ensure output channels exist

2. **Check Scene Number Range**
   - Valid scene numbers: 0-127
   - Use documented scene numbers for standard scenes
   - Custom scenes typically: 50-127

3. **Test Scene Save**
   ```yaml
   # Set device to desired state
   service: light.turn_on
   target:
     entity_id: light.test
   data:
     brightness: 128
   
   # Wait a moment, then save
   service: digitalstrom_vdc.save_scene
   target:
     device_id: <device_id>
   data:
     scene: 50
   ```

### Scene Recall Doesn't Work

**Symptoms:**
- Call scene service executes without error
- Device state doesn't change

**Solutions:**

1. **Verify Scene Exists**
   - Must save scene before recalling
   - Check dSS for saved scenes
   - Review device scene configuration

2. **Check Force Parameter**
   ```yaml
   service: digitalstrom_vdc.call_scene
   target:
     device_id: <device_id>
   data:
     scene: 5
     force: true  # Force scene call
   ```

3. **Review Scene Group**
   - Ensure scene matches device group
   - Check for group-specific scene restrictions

---

## Performance Issues

### Slow State Updates

**Symptoms:**
- Delay between HA command and VDC state change
- Lag in state synchronization

**Solutions:**

1. **Check Coordinator Interval**
   ```yaml
   # Default update interval is in const.py
   # Can be adjusted in coordinator configuration
   ```

2. **Network Latency**
   - Test latency to dSS: `ping <dss_ip>`
   - Check for network congestion
   - Verify Wi-Fi signal strength if wireless

3. **Reduce Device Count**
   - Too many devices can slow updates
   - Consider splitting across multiple VDC instances
   - Review update patterns in logs

### High CPU Usage

**Symptoms:**
- Home Assistant CPU usage high
- Attributed to digitalstrom_vdc component

**Solutions:**

1. **Check Logging Level**
   - Disable debug logging if enabled
   - Set to INFO or WARNING only
   - Review log file size

2. **Review Update Frequency**
   - Check coordinator update interval
   - Reduce polling frequency if using polling
   - Optimize callback patterns

3. **Profile Component**
   ```yaml
   # Enable profiling in configuration.yaml
   profiler:
   ```

### Memory Leaks

**Symptoms:**
- Memory usage grows over time
- Eventual HA instability

**Solutions:**

1. **Check for Unclosed Resources**
   - Review async task cleanup
   - Verify socket connections are closed
   - Check callback deregistration

2. **Restart Integration**
   - Reload integration via UI
   - Monitor memory usage after reload

3. **Report Issue**
   - Gather logs and memory profile
   - Report on GitHub with reproduction steps

---

## Error Messages

### Common Error Messages and Solutions

#### `Port already in use`
See [Port Already in Use](#port-already-in-use)

#### `Failed to connect to DSS`
See [Cannot Connect to dSS](#cannot-connect-to-dss)

#### `Invalid dsUID format`
```
ERROR [custom_components.digitalstrom_vdc] Invalid dsUID format: <value>
```
**Solution**: dsUID must be 34-character hex string. Regenerate or manually specify valid dsUID.

#### `Entity not found`
```
WARNING [custom_components.digitalstrom_vdc.entity_binding] Entity <entity_id> not found
```
**Solution**: Verify entity exists in HA, check for typos, ensure entity is not disabled.

#### `Channel index out of range`
```
ERROR [custom_components.digitalstrom_vdc] Channel 0 does not exist on device
```
**Solution**: Device has no output channels or wrong channel index. Verify device configuration.

#### `Scene number out of range`
```
ERROR [custom_components.digitalstrom_vdc] Scene number must be 0-127
```
**Solution**: Use valid scene number in range 0-127.

#### `Template not found`
```
ERROR [custom_components.digitalstrom_vdc.template_manager] Template <name> not found
```
**Solution**: Run `refresh_templates` service or use valid template name.

#### `VDC host not initialized`
```
ERROR [custom_components.digitalstrom_vdc] VDC host not initialized
```
**Solution**: Wait for integration to fully initialize. Check for initialization errors in logs.

---

## Debug Logging

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    # Main integration
    custom_components.digitalstrom_vdc: debug
    
    # Specific components
    custom_components.digitalstrom_vdc.vdc_manager: debug
    custom_components.digitalstrom_vdc.device_manager: debug
    custom_components.digitalstrom_vdc.entity_binding: debug
    custom_components.digitalstrom_vdc.coordinator: debug
    
    # pyvdcapi library
    pyvdcapi: debug
```

Restart Home Assistant to apply.

### Reading Debug Logs

**Connection Events:**
```
DEBUG [custom_components.digitalstrom_vdc.vdc_manager] VDC host started on port 8444
DEBUG [pyvdcapi] DSS connected from <ip>:<port>
DEBUG [pyvdcapi] PING sent, awaiting PONG
```

**Device Events:**
```
DEBUG [custom_components.digitalstrom_vdc.device_manager] Creating device from template: simple_onoff_light
DEBUG [pyvdcapi] Device created with dsUID: <dsuid>
DEBUG [custom_components.digitalstrom_vdc.vdc_manager] Announcing device <dsuid>
```

**State Sync Events:**
```
DEBUG [custom_components.digitalstrom_vdc.entity_binding] HA state changed: light.test = on (brightness=128)
DEBUG [pyvdcapi] Setting channel 0 value to 50.19
DEBUG [pyvdcapi] Channel value changed callback: 50.19
```

### Collecting Logs for Issue Reports

```bash
# Get last 500 lines of debug logs
docker logs --tail 500 homeassistant | grep digitalstrom_vdc > debug.log

# Or from HA UI: Settings → System → Logs → Load Full Logs
# Filter by "digitalstrom_vdc"
```

---

## Common Workflows

### Reset Integration

1. Remove integration from UI
2. Restart Home Assistant
3. Re-add integration
4. Reconfigure devices

### Migrate Device Configuration

1. Export current device config (take screenshots or notes)
2. Remove old device
3. Create new device with same configuration
4. Update entity bindings if entity IDs changed

### Test VDC Connection Manually

```python
# Python test script
import asyncio
from pyvdcapi import VdcHost

async def test_connection():
    host = VdcHost(
        port=8444,
        vdc_name="Test VDC",
        vdc_model="Test Model"
    )
    
    try:
        await host.start()
        print("VDC host started successfully")
        await asyncio.sleep(60)  # Wait for connection
    finally:
        # Cleanup
        pass

asyncio.run(test_connection())
```

### Validate Device Configuration

```yaml
# Check device in Developer Tools → States
# Look for attributes:
# - dsuid
# - vdc_device_id
# - entity_binding
# - output_channels
```

---

## Getting Help

If issues persist after troubleshooting:

1. **GitHub Issues**: [Report a bug](https://github.com/KarlKiel/HA-digitalStromVDC/issues)
2. **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)
3. **Documentation**: [Main README](../README.md)

When reporting issues, include:
- Home Assistant version
- Integration version
- Debug logs (relevant sections)
- Configuration details (sanitize sensitive data)
- Steps to reproduce
- Expected vs actual behavior

---

**Last Updated**: February 16, 2026  
**Integration Version**: 0.1.0
