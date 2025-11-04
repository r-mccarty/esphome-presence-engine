# Troubleshooting Guide

## Common Issues

### Device Not Connecting to Wi-Fi

**Symptoms**: Device doesn't appear in Home Assistant, fallback AP is active

**Solutions**:
1. Verify Wi-Fi credentials in `secrets.yaml`
2. Check that your Wi-Fi network is 2.4GHz (ESP32 doesn't support 5GHz)
3. Check Wi-Fi signal strength at the device location
4. Review logs via USB serial connection: `esphome logs bed-presence-detector.yaml`

### False Positives (Detects presence when bed is empty)

**Symptoms**: Sensor reports occupied when bed is vacant

**Solutions**:
1. Lower the occupied threshold
2. Increase the vacant threshold
3. Re-run calibration in a quieter environment
4. Increase debounce timers to filter out transient noise
5. Check for nearby movement (pets, fans, etc.)

### False Negatives (Doesn't detect presence when occupied)

**Symptoms**: Sensor reports vacant when someone is in bed

**Solutions**:
1. Raise the vacant threshold
2. Lower the occupied threshold
3. Re-run calibration
4. Verify sensor mounting position (should have clear line of sight to bed)

### Sensor Flapping Between States

**Symptoms**: Rapid switching between occupied and vacant

**Solutions**:
1. Increase debounce timers (both occupied and vacant)
2. Increase the gap between occupied and vacant thresholds (hysteresis)
3. Verify sensor is securely mounted and not vibrating

### Dashboard Not Showing Data

**Symptoms**: Dashboard loads but shows "unknown" or missing data

**Solutions**:
1. Verify all entities exist in Home Assistant
2. Check that the ESPHome device is online
3. Verify entity IDs match between dashboard and your device
4. Check Home Assistant logs for errors

### Codespaces build fails with `unable to find user vscode`

**Symptoms**: When launching a GitHub Codespace that uses a custom devcontainer image, the build fails and drops into a recovery container with the log message `unable to find user vscode: no matching entries in passwd file`.

**Solutions**:
1. Update your `.devcontainer/Dockerfile` to create a non-root user named `vscode` (UID/GID `1000` by default) and install `sudo`. Example for Debian-based images:
   ```dockerfile
   FROM debian:bullseye-slim
   ENV DEBIAN_FRONTEND=noninteractive
   RUN apt-get update \
       && apt-get -y install --no-install-recommends sudo git curl \
       && rm -rf /var/lib/apt/lists/*
   ARG USERNAME=vscode
   ARG USER_UID=1000
   ARG USER_GID=$USER_UID
   RUN groupadd --gid $USER_GID $USERNAME \
       && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
       && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
       && chmod 0440 /etc/sudoers.d/$USERNAME
   USER $USERNAME
   ```
2. Alternatively, if you are using a pre-built image that already contains a non-root user (e.g., `node`), set `"remoteUser"` in `.devcontainer/devcontainer.json` to that user.
3. After applying either change, run **Codespaces: Rebuild Container** so the new user configuration is applied.

## Diagnostic Tools

### ESPHome Logs

View real-time logs from the device:
```bash
esphome logs bed-presence-detector.yaml
```

### Home Assistant Developer Tools

Use Developer Tools → States to inspect entity values in real-time

### Web Server

The device exposes a web server at `http://<device-ip>` for quick diagnostics

## Getting Help

If you continue to experience issues:

1. Check the FAQ: [faq.md](faq.md)
2. Review the GitHub Issues page
3. Provide logs and configuration when reporting issues
