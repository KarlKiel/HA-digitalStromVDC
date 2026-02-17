# Installation Guide

This guide provides detailed installation instructions for the digitalSTROM VDC Integration for Home Assistant.

## Prerequisites

Before installing the integration, ensure you have:

1. **Home Assistant** 2024.1.0 or newer
2. **digitalSTROM Smart Service (dSS)** installed and running on your network
3. **Network access** between Home Assistant and dSS
4. **HACS** installed (for HACS installation method)

## Installation Methods

### Method 1: HACS Installation (Recommended)

HACS (Home Assistant Community Store) is the easiest way to install and maintain custom integrations.

#### Step 1: Add Custom Repository

1. Open Home Assistant
2. Navigate to **HACS** → **Integrations**
3. Click the **three dots** (⋮) in the top right corner
4. Select **Custom repositories**
5. Enter the repository URL: `https://github.com/KarlKiel/HA-digitalStromVDC`
6. Select **Integration** as the category
7. Click **Add**

#### Step 2: Install Integration

1. Search for "digitalSTROM VDC" in HACS
2. Click on the integration
3. Click **Download**
4. Select the latest version
5. Click **Download** again

#### Step 3: Restart Home Assistant

1. Go to **Settings** → **System**
2. Click **Restart**
3. Wait for Home Assistant to restart

### Method 2: Manual Installation

#### Step 1: Download Release

1. Go to the [releases page](https://github.com/KarlKiel/HA-digitalStromVDC/releases)
2. Download the latest `digitalstrom_vdc.zip` file

#### Step 2: Extract Files

1. Extract the ZIP file
2. You should see a `custom_components/digitalstrom_vdc` folder

#### Step 3: Copy to Home Assistant

1. Connect to your Home Assistant instance (via Samba, SSH, or file editor)
2. Navigate to your `config` directory
3. If it doesn't exist, create a `custom_components` folder
4. Copy the `digitalstrom_vdc` folder into `custom_components`

Your directory structure should look like:
```
config/
└── custom_components/
    └── digitalstrom_vdc/
        ├── __init__.py
        ├── manifest.json
        ├── config_flow.py
        └── ... (other files)
```

#### Step 4: Restart Home Assistant

1. Go to **Settings** → **System**
2. Click **Restart**
3. Wait for Home Assistant to restart

## Initial Configuration

### Step 1: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for "digitalSTROM VDC"
4. Click on the integration to start setup

### Step 2: Configure TCP Port

1. Enter the TCP port for the VDC server (default: **8444**)
2. Click **Submit**

**Note**: Ensure this port is not blocked by your firewall and is not in use by another service.

### Step 3: Initialize VDC Host

1. Review the detected Home Assistant IP address
2. Review the generated dsUID (unique identifier)
3. Optionally change the VDC name (default: "Home Assistant VDC")
4. Click **Submit**

### Step 4: Configure Service Discovery

1. Choose whether to enable service announcement (recommended: **Yes**)
2. Set service name for Zeroconf (default: "ha-vdc")
3. Click **Submit**

**Note**: Service announcement enables automatic discovery by dSS.

### Step 5: Connect to DSS

1. Review the configuration summary
2. Click **Submit** to complete setup
3. The integration is now ready to accept connections from dSS

## Configure dSS

After setting up the Home Assistant integration, you need to configure your dSS to connect to it.

### Option 1: Automatic Discovery (Zeroconf)

If you enabled service announcement, dSS should automatically discover the VDC:

1. Open the dSS web interface
2. Navigate to **System** → **Virtual Device Connectors**
3. Look for your VDC (e.g., "Home Assistant VDC")
4. Click **Connect** or **Approve**

### Option 2: Manual Configuration

If automatic discovery doesn't work:

1. Open the dSS web interface
2. Navigate to **System** → **Virtual Device Connectors**
3. Click **Add VDC**
4. Enter:
   - **Host**: Home Assistant IP address
   - **Port**: The port you configured (default: 8444)
   - **Name**: Home Assistant VDC
5. Click **Add**
6. Click **Connect**

## Verify Installation

### Check Integration Status

1. Go to **Settings** → **Devices & Services**
2. Find "digitalSTROM VDC" in the list
3. Status should show as **Connected**

### Check Logs

Enable debug logging to verify everything is working:

```yaml
logger:
  default: info
  logs:
    custom_components.digitalstrom_vdc: debug
```

Check the logs for:
- VDC host initialization
- TCP server started
- Service announcement (if enabled)
- Connection from dSS

## Troubleshooting

### Integration Not Appearing

**Problem**: Can't find "digitalSTROM VDC" in Add Integration dialog  
**Solution**:
- Verify files are in correct location: `config/custom_components/digitalstrom_vdc/`
- Restart Home Assistant again
- Check logs for errors loading the integration

### Port Already in Use

**Problem**: Error during setup: "Port is already in use"  
**Solution**:
- Choose a different port number
- Check what's using the port: `sudo netstat -tulpn | grep <port>`
- Stop the conflicting service or use another port

### Connection Failed

**Problem**: Integration setup completes but dSS can't connect  
**Solution**:
- Verify firewall settings allow TCP traffic on the configured port
- Check network connectivity: `ping <home-assistant-ip>` from dSS host
- Verify Home Assistant and dSS are on the same network or routable subnet
- Check Home Assistant logs for connection attempts

### Service Not Announced

**Problem**: dSS doesn't discover VDC automatically  
**Solution**:
- Verify Zeroconf is enabled in configuration
- Check network supports mDNS/Zeroconf
- Some networks block mDNS traffic - use manual configuration instead
- Restart both Home Assistant and dSS

## Next Steps

After successful installation:

1. [Add your first device](docs/DEVICE_SETUP.md)
2. [Configure entity bindings](docs/ENTITY_BINDING.md)
3. [Explore templates](docs/TEMPLATES.md)
4. [Set up automations](docs/AUTOMATIONS.md)

## Uninstallation

To remove the integration:

1. Go to **Settings** → **Devices & Services**
2. Find "digitalSTROM VDC"
3. Click the **three dots** (⋮)
4. Select **Delete**
5. Confirm deletion

To completely remove files:
- **HACS**: Remove via HACS interface
- **Manual**: Delete `custom_components/digitalstrom_vdc` folder and restart

---

For additional help, see [Troubleshooting Guide](docs/TROUBLESHOOTING.md) or [open an issue](https://github.com/KarlKiel/HA-digitalStromVDC/issues).
