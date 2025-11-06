#!/usr/bin/env python3
"""
Real-Time Presence Detection Monitor

This script monitors the bed presence sensor in real-time, displaying:
- LD2410 still energy readings
- Calculated z-score
- Current presence state
- Threshold values

Usage:
    python3 monitor_presence.py

Environment Variables:
    HA_URL: Home Assistant URL (default: http://localhost:8123)
    HA_TOKEN: Long-lived access token (required)
"""

import os
import sys
import time
import requests
from datetime import datetime
from typing import Dict, Optional

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_ha_config() -> tuple[str, str]:
    """Get Home Assistant URL and token from environment or .env.local file."""
    ha_url = os.getenv('HA_URL')
    ha_token = os.getenv('HA_TOKEN')

    # If not in environment, try to load from .env.local
    if not ha_url or not ha_token:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(script_dir, '..', '.env.local')

        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('HA_URL=') and not ha_url:
                        ha_url = line.split('=', 1)[1].strip()
                    elif line.startswith('HA_TOKEN=') and not ha_token:
                        ha_token = line.split('=', 1)[1].strip()

    # Use localhost if running on HA host
    if not ha_url:
        ha_url = 'http://localhost:8123'

    if not ha_token:
        print(f"{Colors.FAIL}ERROR: HA_TOKEN not found in environment or .env.local{Colors.ENDC}")
        print(f"Please set the HA_TOKEN environment variable or add it to .env.local")
        sys.exit(1)

    return ha_url, ha_token


def get_entity_state(ha_url: str, ha_token: str, entity_id: str) -> Optional[Dict]:
    """Get the current state of an entity."""
    headers = {
        'Authorization': f'Bearer {ha_token}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.get(
            f'{ha_url}/api/states/{entity_id}',
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except requests.exceptions.RequestException:
        return None


def calculate_z_score(energy: float, mu: float, sigma: float) -> float:
    """Calculate z-score: (energy - μ) / σ"""
    if sigma <= 0.001:
        return 0.0
    return (energy - mu) / sigma


def format_state(state: str) -> str:
    """Format presence state with color."""
    if state == 'on':
        return f"{Colors.OKGREEN}{Colors.BOLD}OCCUPIED{Colors.ENDC}"
    elif state == 'off':
        return f"{Colors.OKCYAN}VACANT{Colors.ENDC}"
    else:
        return f"{Colors.WARNING}{state.upper()}{Colors.ENDC}"


def format_z_score(z: float, k_on: float, k_off: float) -> str:
    """Format z-score with color based on threshold comparison."""
    if z > k_on:
        color = Colors.OKGREEN
        indicator = ">>>"
    elif z < k_off:
        color = Colors.OKCYAN
        indicator = "<<<"
    else:
        color = Colors.WARNING
        indicator = "~~~"

    return f"{color}{z:6.2f} {indicator}{Colors.ENDC}"


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header():
    """Print the header."""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 80)
    print("  BED PRESENCE DETECTION - REAL-TIME MONITOR")
    print("=" * 80)
    print(f"{Colors.ENDC}")


def print_baseline_info(mu: float, sigma: float):
    """Print baseline calibration info."""
    print(f"{Colors.OKBLUE}Baseline Calibration:{Colors.ENDC}")
    print(f"  Mean (μ):              {mu:.2f}%")
    print(f"  Std Dev (σ):           {sigma:.2f}%")
    print()


def print_thresholds(k_on: float, k_off: float):
    """Print threshold values."""
    print(f"{Colors.OKBLUE}Detection Thresholds:{Colors.ENDC}")
    print(f"  k_on (turn ON):        {k_on:.1f} std deviations")
    print(f"  k_off (turn OFF):      {k_off:.1f} std deviations")
    print(f"  Hysteresis gap:        {k_on - k_off:.1f} std deviations")
    print()


def print_sensor_data(still_energy: float, z_score: float, state: str,
                      k_on: float, k_off: float, reason: str):
    """Print current sensor readings."""
    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"{Colors.BOLD}Current Readings ({timestamp}):{Colors.ENDC}")
    print(f"  Still Energy:          {still_energy:.1f}%")
    print(f"  Z-Score:               {format_z_score(z_score, k_on, k_off)} (k_on={k_on:.1f}, k_off={k_off:.1f})")
    print(f"  Presence State:        {format_state(state)}")
    if reason:
        print(f"  State Reason:          {reason}")
    print()


def print_legend():
    """Print legend for z-score indicators."""
    print(f"{Colors.BOLD}Legend:{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}>>> GREEN{Colors.ENDC}  : z-score > k_on  (should be OCCUPIED)")
    print(f"  {Colors.OKCYAN}<<< CYAN{Colors.ENDC}   : z-score < k_off (should be VACANT)")
    print(f"  {Colors.WARNING}~~~ YELLOW{Colors.ENDC} : k_off < z-score < k_on (hysteresis zone)")
    print()
    print(f"{Colors.WARNING}Press Ctrl+C to stop monitoring{Colors.ENDC}")
    print()


def monitor_loop(ha_url: str, ha_token: str):
    """Main monitoring loop."""
    # Hardcoded baseline from calibration
    MU = 6.3
    SIGMA = 2.6

    # Entity IDs
    STILL_ENERGY = "sensor.bed_presence_detector_ld2410_still_energy"
    BED_OCCUPIED = "binary_sensor.bed_presence_detector_bed_occupied"
    K_ON = "number.bed_presence_detector_k_on_on_threshold_multiplier"
    K_OFF = "number.bed_presence_detector_k_off_off_threshold_multiplier"
    STATE_REASON = "sensor.bed_presence_detector_presence_state_reason"

    print_header()
    print_baseline_info(MU, SIGMA)

    # Get initial threshold values
    k_on_state = get_entity_state(ha_url, ha_token, K_ON)
    k_off_state = get_entity_state(ha_url, ha_token, K_OFF)

    if not k_on_state or not k_off_state:
        print(f"{Colors.FAIL}ERROR: Could not fetch threshold entities{Colors.ENDC}")
        print(f"Make sure the device is online and entity names are correct.")
        sys.exit(1)

    k_on_val = float(k_on_state['state'])
    k_off_val = float(k_off_state['state'])

    print_thresholds(k_on_val, k_off_val)
    print_legend()

    print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
    print()

    # Monitoring loop
    last_thresholds = (k_on_val, k_off_val)

    while True:
        try:
            # Fetch current values
            energy_state = get_entity_state(ha_url, ha_token, STILL_ENERGY)
            occupied_state = get_entity_state(ha_url, ha_token, BED_OCCUPIED)
            k_on_state = get_entity_state(ha_url, ha_token, K_ON)
            k_off_state = get_entity_state(ha_url, ha_token, K_OFF)
            reason_state = get_entity_state(ha_url, ha_token, STATE_REASON)

            if not energy_state or not occupied_state:
                print(f"{Colors.FAIL}ERROR: Could not fetch entity states{Colors.ENDC}")
                time.sleep(2)
                continue

            # Parse values
            energy = float(energy_state['state'])
            state = occupied_state['state']
            k_on_val = float(k_on_state['state']) if k_on_state else last_thresholds[0]
            k_off_val = float(k_off_state['state']) if k_off_state else last_thresholds[1]
            reason = reason_state['state'] if reason_state else ""

            # Calculate z-score
            z_score = calculate_z_score(energy, MU, SIGMA)

            # Check if thresholds changed
            current_thresholds = (k_on_val, k_off_val)
            if current_thresholds != last_thresholds:
                # Move cursor up and reprint threshold info
                print(f"\033[7A")  # Move up 7 lines
                print_thresholds(k_on_val, k_off_val)
                print_legend()
                print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
                print()
                last_thresholds = current_thresholds

            # Print sensor data
            print_sensor_data(energy, z_score, state, k_on_val, k_off_val, reason)

            # Wait before next update
            time.sleep(1)

            # Move cursor up to overwrite previous reading
            print(f"\033[{7 if reason else 6}A", end='')

        except KeyboardInterrupt:
            print(f"\n\n{Colors.OKGREEN}Monitoring stopped by user{Colors.ENDC}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Colors.FAIL}ERROR: {e}{Colors.ENDC}")
            time.sleep(2)


def main():
    """Main entry point."""
    ha_url, ha_token = get_ha_config()

    print(f"\n{Colors.OKCYAN}Connecting to Home Assistant at {ha_url}...{Colors.ENDC}\n")

    # Verify connection
    try:
        response = requests.get(f"{ha_url}/api/", headers={
            'Authorization': f'Bearer {ha_token}'
        }, timeout=5)

        if response.status_code != 200:
            print(f"{Colors.FAIL}ERROR: Could not connect to Home Assistant{Colors.ENDC}")
            print(f"HTTP {response.status_code}: {response.text}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}ERROR: Connection failed: {e}{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.OKGREEN}✓ Connected successfully{Colors.ENDC}\n")
    time.sleep(1)

    clear_screen()
    monitor_loop(ha_url, ha_token)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Monitoring interrupted{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
