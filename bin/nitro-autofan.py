#!/usr/bin/env python3
"""
Acer Nitro AN515-45 Smart Fan Controller Daemon
Monitors CPU & GPU thermals and dynamically manages fan speeds.
Properly supports manual override, turbo, and smart auto modes.
"""

import glob
import os
import sys
import time

OVERRIDE_FILE = "/tmp/nitro-fan-override"

def find_ec_hwmon():
    for path in glob.glob("/sys/class/hwmon/hwmon*"):
        name_path = os.path.join(path, "name")
        if os.path.exists(name_path):
            try:
                with open(name_path, "r") as f:
                    if f.read().strip() == "acer_nitro_ec":
                        return path
            except Exception:
                pass
    return None

def read_val(path, default=0):
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except Exception:
        return default

def write_val(path, val):
    try:
        with open(path, "w") as f:
            f.write(str(val))
    except Exception:
        pass

def main():
    hwmon = find_ec_hwmon()
    if not hwmon:
        time.sleep(2)
        hwmon = find_ec_hwmon()
        if not hwmon:
            sys.stderr.write("acer_nitro_ec hwmon device not found.\n")
            sys.exit(1)

    pwm1_enable = os.path.join(hwmon, "pwm1_enable")
    pwm2_enable = os.path.join(hwmon, "pwm2_enable")
    pwm1 = os.path.join(hwmon, "pwm1")
    pwm2 = os.path.join(hwmon, "pwm2")
    temp1 = os.path.join(hwmon, "temp1_input")
    temp2 = os.path.join(hwmon, "temp2_input")

    cooldown_counter = 0

    while True:
        try:
            # 1. Check manual override from GUI
            if os.path.exists(OVERRIDE_FILE):
                try:
                    with open(OVERRIDE_FILE, "r") as f:
                        mode = f.read().strip().lower()

                    hw_mode = read_val(pwm1_enable, -1)

                    if mode == "turbo":
                        if hw_mode != 0:
                            write_val(pwm1_enable, 0)
                            write_val(pwm2_enable, 0)
                        time.sleep(1)
                        continue
                    elif mode == "auto":
                        if hw_mode != 2:
                            write_val(pwm1_enable, 2)
                            write_val(pwm2_enable, 2)
                        time.sleep(1)
                        continue
                    elif mode.startswith("manual:"):
                        _, s1, s2 = mode.split(":")
                        val1 = int(s1)
                        val2 = int(s2)
                        if hw_mode != 1:
                            write_val(pwm1_enable, 1)
                            write_val(pwm2_enable, 1)
                        hw_s1 = read_val(pwm1, -1)
                        hw_s2 = read_val(pwm2, -1)
                        if abs(hw_s1 - val1) > 4:
                            write_val(pwm1, val1)
                        if abs(hw_s2 - val2) > 4:
                            write_val(pwm2, val2)
                        time.sleep(1)
                        continue
                except Exception:
                    pass

            # 2. Smart Dynamic Mode (when no override file exists)
            t_cpu = read_val(temp1, 50000) / 1000.0
            t_gpu = read_val(temp2, 50000) / 1000.0
            max_t = max(t_cpu, t_gpu)

            # Smart target based on temperatures:
            # >= 82C -> Turbo mode (0)
            # >= 72C -> High speed (85% pwm = 220)
            # >= 64C -> Medium speed (65% pwm = 170)
            # < 60C  -> Auto mode (2)
            target_mode = 2
            target_pwm = 0

            if max_t >= 82.0:
                target_mode = 0  # Turbo
            elif max_t >= 72.0:
                target_mode = 1  # High
                target_pwm = 220
            elif max_t >= 64.0:
                target_mode = 1  # Medium
                target_pwm = 170
            else:
                target_mode = 2  # Auto (Factory EC curve)

            hw_mode = read_val(pwm1_enable, -1)
            hw_pwm = read_val(pwm1, -1)

            needs_change = False
            if hw_mode != target_mode:
                if target_mode == 2 and hw_mode in (0, 1):
                    cooldown_counter += 1
                    if cooldown_counter >= 2:
                        needs_change = True
                        cooldown_counter = 0
                else:
                    needs_change = True
                    cooldown_counter = 0
            elif target_mode == 1 and abs(hw_pwm - target_pwm) > 15:
                needs_change = True

            if needs_change:
                if target_mode == 0:
                    write_val(pwm1_enable, 0)
                    write_val(pwm2_enable, 0)
                elif target_mode == 1:
                    write_val(pwm1_enable, 1)
                    write_val(pwm1, target_pwm)
                    write_val(pwm2_enable, 1)
                    write_val(pwm2, target_pwm)
                elif target_mode == 2:
                    write_val(pwm1_enable, 2)
                    write_val(pwm2_enable, 2)

            time.sleep(1)
        except Exception:
            time.sleep(1)

if __name__ == "__main__":
    main()
