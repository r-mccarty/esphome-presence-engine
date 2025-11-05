# Ubuntu Home Assistant Node - Setup Documentation

## Node Overview

**Hardware**: N100 Mini PC
**OS**: Ubuntu 24.04 LTS (Linux kernel 6.14.0-34-generic)
**Hostname**: `home-assistant-node`
**Primary User**: `ryan`
**Location**: Local LAN

## Network Configuration

### Local Network
- **LAN IP**: Private network (192.168.x.x range)
- **Network**: Behind router (not directly accessible from internet)

### Public Access via Cloudflare Tunnel

The node uses Cloudflare Tunnel for secure external access:
- Home Assistant: `your-domain.com` → `localhost:8123`
- SSH: `ssh.your-domain.com` → `localhost:22`

**Note**: Domain names and tunnel configuration are stored on the node in `/etc/cloudflared/config.yml`

## SSH Access Configuration

### Cloudflare Tunnel Setup

The tunnel is configured and running as a system service:

```bash
# Check tunnel status
sudo systemctl status cloudflared

# View tunnel configuration
cat /etc/cloudflared/config.yml
```

**Tunnel ingress configuration example**:
```yaml
ingress:
  - hostname: your-domain.com
    service: http://localhost:8123

  - hostname: ssh.your-domain.com
    service: ssh://localhost:22

  - service: http_status:404
```

### Connecting via SSH from Codespaces/Remote

**Prerequisites**:
- Install cloudflared client
- Have SSH key authorized on the node

**Installation** (on connecting machine):
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

**SSH Config** (~/.ssh/config):
```
Host ubuntu-node
  HostName ssh.your-domain.com
  User your-username
  IdentityFile ~/.ssh/your_key
  ProxyCommand cloudflared access ssh --hostname ssh.your-domain.com
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
```

**Connect**:
```bash
ssh ubuntu-node
```

Or directly:
```bash
ssh -i ~/.ssh/your_key -o ProxyCommand="cloudflared access ssh --hostname ssh.your-domain.com" your-username@ssh.your-domain.com
```

## User Accounts

### Development User Setup

**Username**: Varies per session (e.g., `claude-temp` for temporary access)
**Groups**: sudo, docker, dialout
**Sudo Access**: Full passwordless sudo (NOPASSWD: ALL) - for development only
**Home Directory**: `/home/your-username`

**Purpose**: Temporary user for development and testing. Should be removed after session.

**SSH Key Setup**:
- Generate SSH key pair on development machine
- Add public key to `~/.ssh/authorized_keys` on node
- Store private key securely

**Cleanup instructions** (when session ends):
```bash
sudo deluser your-username
sudo rm -rf /home/your-username
# Remove SSH public key from authorized_keys
```

### Primary User

**Username**: System owner
**Home Directory**: Varies per installation
**Home Assistant Config**: `/opt/homeassistant/config`

## Home Assistant Setup

### Docker Container

Home Assistant runs in a Docker container:

```bash
# Check container status
docker ps | grep homeassistant

# View logs
docker logs homeassistant

# Restart container
docker restart homeassistant
```

### Configuration Directory

**Location**: `/opt/homeassistant/config`
**Permissions**: Group writable by `ryan` group
**Access**: Members of `ryan` group can read/write

```bash
# Access config directory
cd /opt/homeassistant/config

# View configuration.yaml
cat /opt/homeassistant/config/configuration.yaml
```

### Web Access

- **Local**: http://YOUR_NODE_IP:8123 (find IP via `ip addr` or router DHCP list)
- **Public**: https://your-domain.com (via Cloudflare Tunnel)

### API Access

**WebSocket API**: `ws://YOUR_NODE_IP:8123/api/websocket` (local network)
**Long-Lived Access Tokens**: Create via Profile → Security → Long-Lived Access Tokens

**Note**: Store tokens securely and never commit them to git.

## ESPHome Development Environment

### Python Virtual Environment

**Location**: `/home/your-username/esphome-venv` (or wherever you set up the venv)
**Python Version**: 3.12.3
**ESPHome Version**: 2025.10.4

**Activate**:
```bash
source ~/esphome-venv/bin/activate
```

### Repository Location

**Path**: Clone the repository to your preferred location (e.g., `~/bed-presence-sensor`)

**Key directories**:
- `esphome/` - Firmware source and configuration
- `esphome/custom_components/bed_presence_engine/` - Custom C++ component
- `esphome/secrets.yaml` - WiFi credentials (gitignored)
- `tests/e2e/` - Integration tests

### ESPHome Commands

```bash
# Navigate to project
cd ~/bed-presence-sensor/esphome

# Activate virtual environment
source ~/esphome-venv/bin/activate

# Compile firmware
esphome compile bed-presence-detector.yaml

# Upload to device
esphome upload bed-presence-detector.yaml --device /dev/ttyACM0

# View logs
esphome logs bed-presence-detector.yaml --device /dev/ttyACM0

# Or compile and upload in one command
esphome run bed-presence-detector.yaml --device /dev/ttyACM0
```

## M5Stack Device Configuration

### Hardware Details

**Device**: M5Stack Basic
**Board**: m5stack-core-esp32
**Chip**: ESP32-D0WDQ6-V3 (revision v3.1)
**MAC Address**: Unique per device (viewable in ESPHome logs)
**Flash Size**: 16MB

### USB Connection

**Serial Device**: `/dev/ttyACM0` (may vary - check with `ls /dev/tty*`)
**USB Vendor ID**: 1a86 (QinHeng Electronics)
**USB Product ID**: 55d4 (USB Single Serial)
**Baud Rate**: 115200

**Check connection**:
```bash
ls -la /dev/ttyACM*
lsusb | grep 1a86
```

### Network Configuration

**WiFi Network**: Configured in `secrets.yaml` (gitignored)
**IP Address**: Assigned by DHCP (viewable in Home Assistant or router)
**Hostname**: bed-presence-detector.local
**mDNS**: Yes (ESPHome API on port 6053)

**Note**: WiFi credentials are stored locally in `esphome/secrets.yaml` and should never be committed to git.

### LD2410 Sensor Configuration

**Connection**: UART
**TX Pin**: GPIO16
**RX Pin**: GPIO17
**Baud Rate**: 256000

**Sensor Details**:
- **Model**: LD2410 mmWave Radar
- **Purpose**: Presence detection via still energy readings
- **Key Sensor**: `sensor.ld2410_still_energy`

## Home Assistant Entities

### Binary Sensors
- `binary_sensor.bed_occupied` - Phase 1 presence detection
- `binary_sensor.ld2410_presence` - Raw LD2410 presence
- `binary_sensor.ld2410_moving_target` - Moving detection
- `binary_sensor.ld2410_still_target` - Still detection

### Sensors
- `sensor.ld2410_still_energy` - **Primary input for presence engine**
- `sensor.ld2410_moving_energy` - Moving energy reading
- `sensor.ld2410_detection_distance` - Distance to detected target
- `sensor.ld2410_still_distance` - Still target distance
- `sensor.ld2410_moving_distance` - Moving target distance

### Number Entities (Tunable Thresholds)
- `number.k_on_on_threshold_multiplier` - Turn ON when z > k_on (default: 4.0)
- `number.k_off_off_threshold_multiplier` - Turn OFF when z < k_off (default: 2.0)

### Text Sensors
- `text_sensor.presence_state_reason` - Debug info showing z-scores
- `text_sensor.ip_address` - Device IP address

## Secrets Configuration

**File**: `esphome/secrets.yaml` (gitignored - never commit this file!)

**Template** (use `esphome/secrets.yaml.example` as reference):
```yaml
wifi_ssid: "Your_WiFi_Network"
wifi_password: "your_wifi_password"
ap_password: "fallback-hotspot-password"  # Min 8 characters
api_encryption_key: "generate_with_command_below"
ota_password: "your_ota_password"
```

**Generate encryption key**:
```bash
python3 -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

**Security Notes**:
- This file contains sensitive credentials and is gitignored
- Never commit `secrets.yaml` to version control
- Store credentials securely (password manager recommended)
- Use strong, unique passwords for `ap_password` and `ota_password`
- The `api_encryption_key` must match what Home Assistant expects

## Development Workflow

### 1. Connect to Node via SSH

```bash
ssh ubuntu-node
```

### 2. Navigate to Project

```bash
cd ~/bed-presence-sensor/esphome
source ~/esphome-venv/bin/activate
```

### 3. Make Code Changes

Edit files in `custom_components/bed_presence_engine/` or YAML configurations.

### 4. Test and Flash

```bash
# Run unit tests (fast, no hardware needed)
cd ~/bed-presence-sensor/esphome
platformio test -e native

# Compile and flash to device
esphome run bed-presence-detector.yaml --device /dev/ttyACM0
```

### 5. Monitor Device

```bash
# View live logs
esphome logs bed-presence-detector.yaml --device /dev/ttyACM0

# Or view in Home Assistant
# Go to Settings → Devices → Bed Presence Detector → Logs
```

### 6. Test in Home Assistant

- Check sensor values: Developer Tools → States
- Test threshold tuning: Adjust `k_on` and `k_off` numbers
- Monitor presence state: `binary_sensor.bed_occupied`

## E2E Testing Setup

### Prerequisites

```bash
cd ~/bed-presence-sensor/tests/e2e
pip install -r requirements.txt
```

### Environment Variables

```bash
export HA_URL="ws://YOUR_NODE_IP:8123/api/websocket"  # Local network
# or
export HA_URL="ws://your-domain.com:8123/api/websocket"  # Via Cloudflare

export HA_TOKEN="your-long-lived-access-token-here"
```

**Note**: Get the access token from Home Assistant: Profile → Security → Long-Lived Access Tokens

### Run Tests

```bash
cd ~/bed-presence-sensor/tests/e2e
pytest -v
```

## Baseline Calibration Workflow

### 1. Collect Baseline Data

With an empty bed, monitor `sensor.ld2410_still_energy` for 30-60 seconds:

```bash
# In Home Assistant Developer Tools → States
# Record values of sensor.ld2410_still_energy
```

Or via API:
```bash
# Get sensor value
curl -H "Authorization: Bearer $HA_TOKEN" \
     -H "Content-Type: application/json" \
     http://YOUR_NODE_IP:8123/api/states/sensor.ld2410_still_energy
```

### 2. Calculate Statistics

Calculate mean (μ) and standard deviation (σ) from recorded values.

### 3. Update Firmware

Edit `esphome/custom_components/bed_presence_engine/bed_presence.h`:

```cpp
float mu_move_{100.0f};   // Replace with calculated mean
float sigma_move_{20.0f}; // Replace with calculated std dev
```

### 4. Reflash

```bash
cd ~/bed-presence-sensor/esphome
source ~/esphome-venv/bin/activate
esphome run bed-presence-detector.yaml --device /dev/ttyACM0
```

## Troubleshooting

### Device Not Detected

```bash
# Check USB device
ls -la /dev/ttyACM0
lsusb

# Check dmesg for USB events
sudo dmesg | grep -i usb | tail -20
```

### WiFi Connection Issues

```bash
# View device logs
esphome logs bed-presence-detector.yaml --device /dev/ttyACM0

# Check WiFi credentials
cat ~/bed-presence-sensor/esphome/secrets.yaml
```

### Home Assistant Connection Issues

```bash
# Check if device is reachable (get IP from HA or router)
ping YOUR_DEVICE_IP

# Check if API port is open
nc -zv YOUR_DEVICE_IP 6053

# View ESPHome logs in HA
# Settings → Devices & Services → ESPHome → Bed Presence Detector → Logs
```

### Cloudflare Tunnel Issues

```bash
# Check tunnel status
sudo systemctl status cloudflared

# Restart tunnel
sudo systemctl restart cloudflared

# View tunnel logs
sudo journalctl -u cloudflared -f
```

## Security Considerations

### Temporary Access

The `claude-temp` user is intended for temporary development only:
- Full sudo access (NOPASSWD: ALL)
- Should be removed after development session
- SSH key should be revoked

### Cleanup After Session

```bash
# Remove temporary user
sudo deluser claude-temp
sudo rm -rf /home/claude-temp

# Remove SSH key from authorized_keys
# Edit ~/.ssh/authorized_keys and remove the temporary session key

# Optional: Disable Cloudflare SSH tunnel access
# Edit /etc/cloudflared/config.yml and remove SSH ingress rule
# Then: sudo systemctl restart cloudflared
```

### API Token Security

- Long-lived access tokens should be treated as passwords
- Revoke tokens after development: Profile → Security → Long-Lived Access Tokens → Revoke
- Don't commit tokens to git

## Backup and Recovery

### Important Files to Backup

1. **Home Assistant Configuration**: `/opt/homeassistant/config/`
2. **ESPHome Secrets**: `~/bed-presence-sensor/esphome/secrets.yaml`
3. **Cloudflare Tunnel Config**: `/etc/cloudflared/config.yml`
4. **Custom Component Code**: `~/bed-presence-sensor/esphome/custom_components/`

### Recovery Steps

If the M5Stack needs to be reflashed from scratch:

1. SSH into the node
2. Navigate to project: `cd ~/bed-presence-sensor/esphome`
3. Activate venv: `source ~/esphome-venv/bin/activate`
4. Flash device: `esphome run bed-presence-detector.yaml --device /dev/ttyACM0`
5. Re-add to Home Assistant using encryption key from secrets.yaml

## Quick Reference Commands

```bash
# Connect via SSH
ssh ubuntu-node

# Activate ESPHome environment
cd ~/bed-presence-sensor/esphome
source ~/esphome-venv/bin/activate

# Flash firmware
esphome run bed-presence-detector.yaml --device /dev/ttyACM0

# View device logs
esphome logs bed-presence-detector.yaml --device /dev/ttyACM0

# Check device connection
ls -la /dev/ttyACM*

# Run unit tests
cd ~/bed-presence-sensor/esphome && platformio test -e native

# Run e2e tests
cd ~/bed-presence-sensor/tests/e2e && pytest -v

# Check Home Assistant container
docker ps | grep homeassistant

# View Cloudflare tunnel status
sudo systemctl status cloudflared
```

---

**Last Updated**: 2025-11-05
**M5Stack Firmware Version**: Phase 1 (z-score based detection)
**ESPHome Version**: 2025.10.4

**Note**: This document is sanitized for public repositories. Actual credentials, IP addresses, and domain names are stored locally on the node and in development environments.
