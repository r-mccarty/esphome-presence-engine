#!/usr/bin/env python3
"""
Baseline Data Collection Script for Bed Presence Sensor (Phase 1)

This script collects LD2410 still energy readings from an empty bed to calculate
baseline statistics (mean μ and standard deviation σ) for z-score based presence detection.

Usage:
    1. Ensure bed is completely empty (no people, pets, or objects)
    2. Close bedroom door to minimize external movement
    3. Run this script:
       python3 collect_baseline.py

    The script will:
    - Collect 30 samples over 60 seconds (one sample every 2 seconds)
    - Calculate mean (μ) and standard deviation (σ)
    - Display results ready to paste into bed_presence.h

Environment Variables:
    HA_URL: Home Assistant URL (default: http://localhost:8123)
    HA_TOKEN: Long-lived access token (required)
"""

import os
import sys
import time
import requests
import statistics
from typing import List, Tuple
from datetime import datetime

# ANSI color codes for better output
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


def get_ha_config() -> Tuple[str, str]:
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


def get_sensor_value(ha_url: str, ha_token: str, entity_id: str) -> float:
    """Get the current value of a sensor."""
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
            data = response.json()
            state = data.get('state')

            # Convert to float, handling 'unavailable' or 'unknown' states
            if state in ['unavailable', 'unknown', 'None']:
                raise ValueError(f"Sensor returned invalid state: {state}")

            return float(state)
        else:
            raise ConnectionError(f"HTTP {response.status_code}: {response.text}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to Home Assistant: {e}")


def collect_samples(ha_url: str, ha_token: str, entity_id: str, num_samples: int = 30, total_time: int = 60) -> List[float]:
    """
    Collect sensor readings over a specified time period.

    Args:
        ha_url: Home Assistant URL
        ha_token: Authentication token
        entity_id: Sensor entity ID to monitor
        num_samples: Number of samples to collect (default: 30)
        total_time: Total collection time in seconds (default: 60)

    Returns:
        List of sensor readings
    """
    samples = []
    interval = total_time / num_samples

    print(f"\n{Colors.OKBLUE}📊 Collecting {num_samples} samples over {total_time} seconds...{Colors.ENDC}")
    print(f"{Colors.WARNING}⏰ Please remain away from the sensor. Keep the bed empty.{Colors.ENDC}\n")

    for i in range(num_samples):
        try:
            value = get_sensor_value(ha_url, ha_token, entity_id)
            samples.append(value)

            # Progress indicator
            progress = (i + 1) / num_samples * 100
            bar_length = 40
            filled = int(bar_length * (i + 1) / num_samples)
            bar = '█' * filled + '-' * (bar_length - filled)

            print(f"\r[{bar}] {progress:.1f}% | Sample {i+1}/{num_samples}: {value:.1f}%  ", end='', flush=True)

            # Sleep until next sample (except after last sample)
            if i < num_samples - 1:
                time.sleep(interval)

        except (ValueError, ConnectionError) as e:
            print(f"\n{Colors.FAIL}❌ Error reading sensor: {e}{Colors.ENDC}")
            print(f"{Colors.WARNING}⚠️  Retrying in 2 seconds...{Colors.ENDC}")
            time.sleep(2)
            # Retry this sample
            i -= 1
            continue

    print(f"\n\n{Colors.OKGREEN}✅ Collection complete!{Colors.ENDC}\n")
    return samples


def calculate_statistics(samples: List[float]) -> Tuple[float, float, float, float]:
    """
    Calculate statistical measures from sensor samples.

    Returns:
        Tuple of (mean, stdev, median, mad) where:
        - mean: arithmetic mean (μ)
        - stdev: standard deviation (σ)
        - median: median value
        - mad: median absolute deviation
    """
    mean = statistics.mean(samples)
    stdev = statistics.stdev(samples) if len(samples) > 1 else 0.0
    median = statistics.median(samples)

    # Calculate Median Absolute Deviation (MAD)
    deviations = [abs(x - median) for x in samples]
    mad = statistics.median(deviations)

    return mean, stdev, median, mad


def main():
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 80)
    print("  BED PRESENCE SENSOR - BASELINE DATA COLLECTION (Phase 1)")
    print("=" * 80)
    print(f"{Colors.ENDC}")

    # Get configuration
    ha_url, ha_token = get_ha_config()
    print(f"🔗 Connected to: {Colors.OKCYAN}{ha_url}{Colors.ENDC}")

    # Entity ID for LD2410 still energy sensor (with device prefix)
    entity_id = "sensor.bed_presence_detector_ld2410_still_energy"
    print(f"📡 Monitoring: {Colors.OKCYAN}{entity_id}{Colors.ENDC}")

    # Pre-flight check: verify sensor is accessible
    print(f"\n{Colors.OKBLUE}🔍 Performing pre-flight check...{Colors.ENDC}")
    try:
        initial_value = get_sensor_value(ha_url, ha_token, entity_id)
        print(f"{Colors.OKGREEN}✅ Sensor is accessible. Current value: {initial_value:.1f}%{Colors.ENDC}")
    except (ValueError, ConnectionError) as e:
        print(f"{Colors.FAIL}❌ Cannot access sensor: {e}{Colors.ENDC}")
        print(f"\nPlease ensure:")
        print(f"  1. The M5Stack device is powered on and connected to Home Assistant")
        print(f"  2. The entity ID is correct: {entity_id}")
        print(f"  3. Your HA_TOKEN is valid")
        sys.exit(1)

    # Final confirmation
    print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  IMPORTANT: Before starting collection:{Colors.ENDC}")
    print(f"{Colors.WARNING}   • Ensure the bed is COMPLETELY EMPTY (no people, pets, objects)")
    print(f"   • Close the bedroom door to minimize external movement")
    print(f"   • Keep the environment still for the next 60 seconds{Colors.ENDC}")

    input(f"\n{Colors.OKBLUE}Press ENTER when ready to start collection...{Colors.ENDC}")

    # Collect samples
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    samples = collect_samples(ha_url, ha_token, entity_id, num_samples=30, total_time=60)

    # Calculate statistics
    mean, stdev, median, mad = calculate_statistics(samples)

    # Display results
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 80)
    print("  BASELINE CALIBRATION RESULTS")
    print("=" * 80)
    print(f"{Colors.ENDC}")

    print(f"{Colors.OKGREEN}Collected {len(samples)} samples{Colors.ENDC}")
    print(f"Timestamp: {timestamp}")
    print(f"\n{Colors.OKBLUE}Statistical Analysis:{Colors.ENDC}")
    print(f"  Mean (μ):                 {mean:.2f}%")
    print(f"  Standard Deviation (σ):   {stdev:.2f}%")
    print(f"  Median:                   {median:.2f}%")
    print(f"  MAD (for Phase 3):        {mad:.2f}%")
    print(f"  Min value:                {min(samples):.2f}%")
    print(f"  Max value:                {max(samples):.2f}%")
    print(f"  Range:                    {max(samples) - min(samples):.2f}%")

    # Generate code snippet
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("=" * 80)
    print("  CODE TO PASTE INTO bed_presence.h")
    print("=" * 80)
    print(f"{Colors.ENDC}")

    print(f"{Colors.OKCYAN}")
    print(f"// Baseline calibration collected on {timestamp}")
    print(f"// Location: [Describe your sensor placement here]")
    print(f"// Conditions: Empty bed, door closed, minimal movement")
    print(f"// Statistics: mean={mean:.2f}%, stdev={stdev:.2f}%, n={len(samples)} samples")
    print(f"float mu_move_{{{mean:.1f}f}};      // Mean still energy (empty bed)")
    print(f"float sigma_move_{{{stdev:.1f}f}};  // Std dev still energy (empty bed)")
    print(f"float mu_stat_{{{mean:.1f}f}};      // Same as mu_move_ for Phase 1")
    print(f"float sigma_stat_{{{stdev:.1f}f}};  // Same as sigma_move_ for Phase 1")
    print(f"{Colors.ENDC}")

    print(f"\n{Colors.OKBLUE}📝 Next Steps:{Colors.ENDC}")
    print(f"  1. Copy the code snippet above")
    print(f"  2. Open: esphome/custom_components/bed_presence_engine/bed_presence.h")
    print(f"  3. Replace lines 43-46 with the new baseline values")
    print(f"  4. Recompile and flash the firmware")
    print(f"  5. Test presence detection with person in bed")

    # Save results to file
    results_file = os.path.join(os.path.dirname(__file__), '..', 'baseline_results.txt')
    with open(results_file, 'w') as f:
        f.write(f"Baseline Calibration Results\n")
        f.write(f"{'=' * 80}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Entity: {entity_id}\n")
        f.write(f"Samples collected: {len(samples)}\n\n")
        f.write(f"Statistics:\n")
        f.write(f"  Mean (μ):                 {mean:.2f}%\n")
        f.write(f"  Standard Deviation (σ):   {stdev:.2f}%\n")
        f.write(f"  Median:                   {median:.2f}%\n")
        f.write(f"  MAD:                      {mad:.2f}%\n")
        f.write(f"  Min:                      {min(samples):.2f}%\n")
        f.write(f"  Max:                      {max(samples):.2f}%\n")
        f.write(f"  Range:                    {max(samples) - min(samples):.2f}%\n\n")
        f.write(f"Code for bed_presence.h:\n")
        f.write(f"{'=' * 80}\n")
        f.write(f"// Baseline calibration collected on {timestamp}\n")
        f.write(f"float mu_move_{{{mean:.1f}f}};\n")
        f.write(f"float sigma_move_{{{stdev:.1f}f}};\n")
        f.write(f"float mu_stat_{{{mean:.1f}f}};\n")
        f.write(f"float sigma_stat_{{{stdev:.1f}f}};\n")

    print(f"\n{Colors.OKGREEN}💾 Results saved to: {results_file}{Colors.ENDC}")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Collection interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
