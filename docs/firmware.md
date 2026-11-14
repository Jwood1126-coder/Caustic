# Firmware

Two sketches are in [`firmware/`](../firmware/):

| Sketch | What it does |
|---|---|
| `caustic_rig/` | Main firmware. LED brightness plus a smooth sine wave on the speaker, with frequency sweeps. |
| `led_test/` | Only dims the LED on GPIO 27. Type 0 to 100. |

The board currently has `caustic_rig` flashed. It was compiled with ESP32 Arduino core 3.3.12.

## Flashing

### Arduino IDE
1. **File → Preferences → Additional boards manager URLs:** `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
2. **Tools → Board → Boards Manager:** install **esp32 by Espressif Systems**, version 3.x.
3. Open `firmware/caustic_rig/caustic_rig.ino`.
4. **Tools → Board:** DOIT ESP32 DEVKIT V1. **Tools → Port:** your ESP32's COM port (COM6 on the current PC).
5. Click **Upload**.

### arduino-cli
```bash
arduino-cli compile --fqbn esp32:esp32:esp32doit-devkit-v1 --upload -p COM6 firmware/caustic_rig
```

## Commands

Open Serial Monitor at **115200 baud**, with the line ending set to **New Line**.

| Command | Example | Effect |
|---|---|---|
| `led <0-100>` | `led 30` | LED brightness in percent. Starts at 10% on power-up. |
| `amp <0-100>` | `amp 20` | Speaker drive in percent. Starts at 0 (off). |
| `freq <hz>` | `freq 12` | Ripple frequency, 0.5 to 40 Hz. Starts at 10 Hz. |
| `sweep <from> <to> <sec>` | `sweep 5 25 20` | Glides the frequency from 5 to 25 Hz over 20 seconds. |
| `stop` | | Speaker off. LED stays on. |
| `off` | | Speaker and LED off. |
| `status` | | Prints the current settings. |

## How it works

- Both DRV8833 channels use 20 kHz PWM, which is above hearing, so nothing whines.
- The speaker gets a sine wave rather than a square wave, so the cone moves smoothly and quietly. The firmware recomputes the duty about every 0.5 ms. The positive half of the wave drives AIN1, the negative half drives AIN2, and the other input stays low.
- Phase carries over when the frequency changes, so sweeps don't click.
- BIN2 is wired to GND, so the LED can only ever be driven forwards.
