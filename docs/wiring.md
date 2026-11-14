# Wiring

## The idea

The ESP32 can't power the LED or the speaker directly. A pin gives about 0.02 A, and the LED needs about 0.5 A.
So the ESP32 only sends signals, and the DRV8833 driver switches the real power from the 5 V charger.

- **ESP32** sends signals to the DRV8833.
- **DRV8833** passes 5 V power to the LED and the speaker.
- **Resistors** limit how much current flows.
- **USB-C socket** brings in 5 V from a charger.

## Pin map

| ESP32 pin | DRV8833 pin (Pololu name / cheap-board name) | Purpose |
|---|---|---|
| GPIO 25 | AIN1 / IN1 | Speaker, positive half of the wave |
| GPIO 26 | AIN2 / IN2 | Speaker, negative half of the wave |
| GPIO 27 | BIN1 / IN3 | LED brightness |
| GND | BIN2 / IN4 | Held low, so the LED can never be driven backwards |
| 3V3 | SLP / nSLEEP / EEP | Turns the driver on. Many boards stay off without it. |
| GND | GND | Shared ground. Everything must share it. |

## Power and loads

| From | To | Note |
|---|---|---|
| USB-C socket VBUS (+) | DRV8833 VM / VCC | 5 V for the loads |
| USB-C socket GND (−) | GND rail | Shared ground |
| DRV8833 BOUT1 / OUT3 | 3 ohm resistor → LED + | About 0.5 A |
| LED − | DRV8833 BOUT2 / OUT4 | Check the + and − marks on the star |
| DRV8833 AOUT1 / OUT1 | Three 3 ohm resistors in series → speaker | Peak about 0.35 A |
| Speaker other lead | DRV8833 AOUT2 / OUT2 | |

## Powering the ESP32

- **While it's plugged into the PC:** leave the ESP32's 5V/VIN pin unconnected. It runs from USB, and the loads run from the USB-C socket. Only the grounds are joined.
- **Running on its own:** connect the 5 V rail to the ESP32's 5V/VIN pin and unplug the PC cable. Use one power source at a time unless you've confirmed your board has a diode on its 5V pin.

## Step by step

1. Stick the LED star onto the heatsink's thermal tape. Solder leads to the star's + and − pads and to the speaker.
2. Push the ESP32 and the DRV8833 into the breadboard.
3. ESP32 GND → GND rail. DRV8833 GND → GND rail.
4. ESP32 3V3 → DRV8833 SLP/EEP.
5. ESP32 GPIO 25 → AIN1/IN1. GPIO 26 → AIN2/IN2. GPIO 27 → BIN1/IN3.
6. DRV8833 BIN2/IN4 → GND rail.
7. BOUT1/OUT3 → 3 ohm resistor → LED +. LED − → BOUT2/OUT4.
8. AOUT1/OUT1 → three 3 ohm resistors in series → speaker. Speaker → AOUT2/OUT2.
9. USB-C socket + → DRV8833 VM/VCC. USB-C socket − → GND rail.
10. Plug the ESP32 into the PC and the charger into the USB-C socket.

## LED-only test without the driver

To check the LED, resistor and heatsink before the DRV8833 arrives:
USB-C + → 3 ohm resistor → LED + and LED − → USB-C −. The LED runs at full brightness, about 0.5 A, with no dimming.
Unplug it if the heatsink gets too hot to hold.

## Safety

- The 3 W LED is bright enough to hurt your eyes. Don't look straight into it.
- Keep the breadboard behind the uprights, away from the water.
- The power resistors get warm. Keep them off the breadboard plastic if they run hot.
