# Firmware

Two sketches are in [`firmware/`](../firmware/):

| Sketch | What it does |
|---|---|
| `caustic_rig/` | Main firmware. LED brightness plus a smooth sine wave on the speaker, with frequency sweeps. Hosts the Wi-Fi [control page](control-page.md) (`page.h`) and also takes Serial commands. |
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

## Wi-Fi and web API

The easiest way to control the rig is the [control page](control-page.md). The ESP32 always runs its own network,
**Caustic-Rig** (password `causticrig`), at `http://192.168.4.1`. If you save a home network on the page, it also joins that
network as `http://caustic.local`. The home network is stored in the ESP32's flash, not in this repo.

The page talks to these endpoints, which you can also call from scripts:

| Method and path | Parameters | Effect |
|---|---|---|
| `GET /api/status` | | JSON with `led`, `amp`, `freq`, `comp`, `pattern` (0 = none), `sweeping`, `home_ssid`, `home_ip` |
| `POST /api/set` | any of `led`, `amp`, `freq`, `comp` | Sets values |
| `POST /api/sweep` | `from`, `to`, `sec` | Starts a sweep |
| `GET /api/patterns` | | JSON list of pattern names |
| `POST /api/pattern` | `n` (1 to 30) | Plays a pattern |
| `POST /api/stop` | | Speaker off, pattern ends |
| `POST /api/off` | | Speaker and LED off |
| `POST /api/wifi` | `ssid`, `pass` | Saves the home network and restarts |
| `POST /api/wifi/forget` | | Forgets the home network and restarts |

## Serial commands

Open Serial Monitor at **115200 baud**, with the line ending set to **New Line**.

| Command | Example | Effect |
|---|---|---|
| `led <0-100>` | `led 30` | LED brightness in percent. Starts at 100% on power-up. |
| `amp <0-100>` | `amp 20` | Speaker drive in percent. Starts at 0 (off). |
| `freq <hz>` | `freq 12` | Ripple frequency, 0.5 to 40 Hz. Starts at 10 Hz. |
| `sweep <from> <to> <sec>` | `sweep 5 25 20` | Glides the frequency from 5 to 25 Hz over 20 seconds. |
| `pattern <1-30>` | `pattern 1` | Plays a ripple pattern (see below). Speed, sweep or stop ends it. |
| `patterns` | | Lists the 30 patterns. |
| `comp <0-100>` | `comp 30` | Flicker fix strength. Saved on the rig. Default 30. |
| `stop` | | Speaker off. LED stays on. |
| `off` | | Speaker and LED off. |
| `status` | | Prints the current settings. |

## How it works

- Both DRV8833 channels use 20 kHz PWM, which is above hearing, so nothing whines.
- The speaker gets a sine wave rather than a square wave, so the cone moves smoothly and quietly. The firmware recomputes the duty about every 0.5 ms. The positive half of the wave drives AIN1, the negative half drives AIN2, and the other input stays low.
- Phase carries over when the frequency changes, so sweeps don't click.
- **Flicker fix:** the speaker and LED share one 5 V supply, so the LED dims a little each time the speaker pulls current. `comp` dims the LED by the matching amount when the speaker isn't pulling, so the light stays level. Tune it at 2 Hz until the pulsing stops.
- BIN2 is wired to GND, so the LED can only ever be driven forwards.
- The speaker is wired without resistors. `SPK_LIMIT` (0.60) caps its PWM duty, so 100% on the slider is about 0.75 A peak into the 4 Ω 3 W speaker. Use the 5 V 2 A charger at high settings; a PC port may brown out.
- The waveform runs in its own FreeRTOS task, so serving the web page can't stall it. A stall used to freeze the cone and then jump it, which clicked. `diag` prints the longest gaps.

## Ripple patterns

Defined in [`patterns.h`](../firmware/caustic_rig/patterns.h). Each pattern is a list of segments that glide the ripple speed
(and sometimes the strength) and then loops. To add one, add a segment list and a `PAT(...)` line.

| # | Pattern | What it does |
|---|---|---|
| 1 | Flick | 2 Hz, with a 20 Hz flick for 0.12 s every 1.5 s |
| 2 | Double flick | Two quick 20 Hz flicks, then rest |
| 3 | Ping | 1 Hz, with a 30 Hz ping every second |
| 4 | Raindrops | Random flicks (15–35 Hz) at random times |
| 5 | Heartbeat | Two flicks, lub-dub |
| 6 | Shiver | 3 Hz, with a 40 Hz shiver twice a second |
| 7 | Stutter | Three fast flicks in a row, then rest |
| 8 | Thunder | Long calm, then a rumble that dies away |
| 9 | Flick ladder | Flicks that climb 10, 15, 20, 25, 30 Hz |
| 10 | Flick storm | 25 Hz flicks every 0.4 s |
| 11 | Chirp | Quick rising chirp, then rest |
| 12 | Down chirp | Quick falling chirp, then rest |
| 13 | Slow rise | 1 to 25 Hz over 20 s |
| 14 | Rise and fall | 1 to 25 Hz and back, 30 s |
| 15 | Full sweep | 0.5 to 40 Hz over 30 s |
| 16 | Fast climb | 2 to 30 Hz in 4 s |
| 17 | Long fall | 30 to 1 Hz over 10 s |
| 18 | Tide | 2 to 8 Hz and back, strength swells with it |
| 19 | Stairs | 2 to 16 Hz in 2 Hz steps, then back down |
| 20 | Evolve (2 min) | 0.5 to 12 Hz over a minute, then back |
| 21 | Wobble | Smooth 6 to 14 Hz wobble |
| 22 | Deep wobble | Smooth 2 to 22 Hz wobble |
| 23 | Warble | Fast 15 to 25 Hz warble |
| 24 | Siren | 5 to 25 Hz, once a second |
| 25 | Drift | Wanders smoothly between 3 and 20 Hz at random |
| 26 | Pulse | 8 Hz, on and off |
| 27 | Swell | 6 Hz, strength rises and falls |
| 28 | Taps | Short 15 Hz taps once a second |
| 29 | Knock | Tiny 25 Hz knocks |
| 30 | Shuffle | A random pattern every 20 s |
