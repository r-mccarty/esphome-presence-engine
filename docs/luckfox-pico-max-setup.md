# Luckfox Pico Max Setup Guide

This guide covers connecting and accessing the Luckfox Pico Max (RV1106G3) development
board from the N100 node and Coder workspaces.

## Hardware Overview

| Component | Details |
|-----------|---------|
| Board | Luckfox Pico Max |
| SoC | Rockchip RV1106G3 |
| Connection | USB-C (RNDIS + ADB) |
| Host | N100 Mini PC (ubuntu-node) |

## Network Configuration

### RNDIS (USB Networking)

When connected via USB-C, the Luckfox presents itself as a USB network device using RNDIS
(Remote Network Driver Interface Specification).

| Parameter | Value |
|-----------|-------|
| **Luckfox IP** | `172.32.0.93` (static) |
| **Host IP** | `172.32.0.1/24` |
| **Interface** | `enx*` (USB ethernet, e.g., `enx5aef472011ac`) |
| **Subnet** | `172.32.0.0/24` |

### USB Device Identification

```
Bus 001 Device 003: ID 2207:0019 Fuzhou Rockchip Electronics Company rk3xxx
```

## Host Configuration (N100)

### Automatic Interface Setup

When the Luckfox is plugged in, the RNDIS interface appears but needs an IP address:

```bash
# Find the interface name
ip link show | grep enx

# Assign static IP to host side
sudo ip addr add 172.32.0.1/24 dev enxXXXXXXXXXXXX

# Verify connectivity
ping 172.32.0.93
```

### Persistent Configuration (NetworkManager)

To make the IP assignment persistent:

```bash
# Create NetworkManager connection
sudo nmcli con add type ethernet con-name luckfox ifname enx* \
  ipv4.method manual ipv4.addresses 172.32.0.1/24

# Or create a udev rule for automatic setup
sudo tee /etc/udev/rules.d/99-luckfox.rules << 'EOF'
ACTION=="add", SUBSYSTEM=="net", DRIVERS=="rndis_host", RUN+="/sbin/ip addr add 172.32.0.1/24 dev %k"
EOF
sudo udevadm control --reload-rules
```

## Accessing the Luckfox

### SSH Access

```bash
ssh root@172.32.0.93
# Default password: luckfox
```

### From Coder Workspace

Coder workspaces using the `opticworks-dev` template have:
- **Host network mode**: Direct access to `172.32.0.x` subnet
- **Privileged mode**: Full USB/device access
- **Serial tools**: `picocom`, `minicom`, `screen`

```bash
# From inside a Coder workspace terminal
ssh root@172.32.0.93

# Or use ADB if board is in USB boot mode
adb devices
adb shell
```

### Serial Console (if needed)

If the board exposes a serial port:

```bash
# Find the serial device
ls /dev/ttyUSB* /dev/ttyACM*

# Connect with picocom
picocom -b 115200 /dev/ttyUSB0
```

## Flashing Firmware

### Using rkdeveloptool (Rockchip)

```bash
# Install rkdeveloptool
sudo apt install rkdeveloptool

# Check device in maskrom/loader mode
sudo rkdeveloptool ld

# Flash firmware
sudo rkdeveloptool db MiniLoaderAll.bin
sudo rkdeveloptool wl 0 firmware.img
sudo rkdeveloptool rd
```

### Using ADB Sideload

```bash
adb reboot bootloader
adb sideload update.zip
```

## Direct Ethernet Connection

For higher bandwidth or when USB is unavailable, connect the Luckfox directly to the N100
via Ethernet:

1. Connect Ethernet cable between Luckfox and N100's `enp1s0` port
2. Configure static IP on N100:
   ```bash
   sudo ip addr add 192.168.1.1/24 dev enp1s0
   ```
3. Configure Luckfox (via SSH over RNDIS first):
   ```bash
   # On Luckfox
   ip addr add 192.168.1.100/24 dev eth0
   ```

---

## USB Host Mode (for USB Peripherals)

The Luckfox USB-C port is **device-only by default** (for ADB/RNDIS). To connect USB
peripherals (cameras, storage, etc.), switch to **host mode**.

### Prerequisites

Before switching, set up Ethernet since RNDIS will be lost:

```bash
# 1. Configure N100 ethernet
sudo ip addr add 192.168.1.1/24 dev enp1s0

# 2. Configure Luckfox ethernet (via ADB)
sudo adb shell 'ip addr add 192.168.1.100/24 dev eth0 && ip link set eth0 up'

# 3. Test connectivity
ping 192.168.1.100
```

### Enable Host Mode

```bash
# On Luckfox (via ADB or SSH)
luckfox-config
# Navigate: Advanced Options → USB → select "host"
# Reboot
```

### Connection Status After Host Mode

| Connection | Status |
|------------|--------|
| USB RNDIS | ❌ Lost |
| ADB | ❌ Lost |
| Ethernet SSH | ✅ Primary |
| Serial console | ✅ Backup |

---

## Power via GPIO Header

When USB-C is in host mode, it cannot provide power. Use GPIO header pins instead.

### Power Pinout

| Pin | Name | Description |
|-----|------|-------------|
| 36 | VBUS | 5V output (device mode only) |
| 38 | GND | Ground |
| **39** | **VSYS** | **5V input (recommended)** |
| 40 | GND | Ground |

### Wiring

```
5V USB Power Adapter                    Luckfox Pico Max
┌─────────────────┐                    ┌─────────────────┐
│                 │                    │   GPIO Header   │
│    +5V (Red) ───┼────────────────────┼──► Pin 39 (VSYS)│
│                 │                    │                 │
│    GND (Black)──┼────────────────────┼──► Pin 38 (GND) │
│                 │                    │                 │
└─────────────────┘                    └─────────────────┘
```

> **Warning**: Double-check polarity before connecting. Reversing power will damage the board.

### Requirements

- 5V 2A USB power adapter (or better)
- Dupont jumper wires (F-F) or spliced USB cable

---

## Complete USB Host Setup

For connecting USB cameras or other peripherals:

```
┌──────────────┐    Ethernet       ┌─────────────────────────────┐
│    N100      ├───────────────────┤      Luckfox Pico Max       │
│ 192.168.1.1  │                   │      192.168.1.100          │
└──────────────┘                   │                             │
                                   │  USB-C ──► OTG ──► USB Cam  │
┌──────────────┐   Pin 39 + 38     │                             │
│  5V Power    ├───────────────────┤  GPIO Header (Power In)     │
└──────────────┘                   └─────────────────────────────┘
```

### Quick Start

```bash
# 1. Set up ethernet (while still in device mode)
sudo ip addr add 192.168.1.1/24 dev enp1s0
sudo adb shell 'ip addr add 192.168.1.100/24 dev eth0 && ip link set eth0 up'

# 2. Enable USB host mode
sudo adb shell 'luckfox-config'
# Select: Advanced Options → USB → host → Reboot

# 3. Power off, then connect:
#    - 5V power to Pin 39 (VSYS) + Pin 38 (GND)
#    - USB peripheral via USB-C OTG adapter
#    - Ethernet cable

# 4. Power on and access via SSH
ssh root@192.168.1.100
```

---

## Troubleshooting

### Interface Not Appearing

```bash
# Check USB device detection
lsusb | grep Rockchip
dmesg | tail -20

# Reload RNDIS driver
sudo modprobe -r rndis_host
sudo modprobe rndis_host
```

### Cannot Ping Luckfox

```bash
# Verify interface has IP
ip addr show | grep 172.32

# Check if Luckfox is responding to ARP
arping -I enxXXX 172.32.0.93

# Try different default IPs (varies by firmware)
ping 172.32.0.93    # Common default
ping 192.168.123.1  # Alternative
```

### SSH Connection Refused

```bash
# Check if SSH is running on Luckfox (via serial console)
systemctl status sshd

# Or try ADB shell
adb shell
```

## Coder Integration

The `opticworks-dev` Coder template is pre-configured for Luckfox access:

| Feature | Configuration |
|---------|---------------|
| Network | `network_mode = "host"` |
| Devices | `/dev` mounted with full access |
| Privileges | `privileged = true` |
| Tools | ADB, picocom, minicom, screen |

Create a workspace at https://coder.hardwareos.com and select the `opticworks-dev` template
with USB/Hardware Access enabled.
