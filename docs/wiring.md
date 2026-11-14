# Wiring

**Testing on a breadboard first?** Use the [breadboard layout](breadboard.md).

![Wiring diagram](wiring-diagram.svg)

## The idea, simply

- **ESP32 = the brain.** It decides how bright the light is and how fast the water ripples. It only sends tiny signals.
- **DRV8833 = the muscle.** It takes those tiny signals and switches the real power to the LED and the speaker.
- **Charger = the food.** It plugs into the ESP32, and the ESP32's VIN pin passes 5 V on to the driver.
- **Resistors = the brakes.** They stop too much current from rushing through.
- **Heatsink = the radiator.** The LED gets very hot without it.

Don't wire the ESP32 straight to the LED. A pin gives about 0.02 A, and the LED needs about 0.5 A.

## Before you start

- Unplug everything.
- Stick the LED star onto the heatsink's thermal tape.
- Solder a short wire to each of the LED star's **+** and **−** pads, and to each speaker terminal.
- Push the ESP32 and the DRV8833 into the breadboard so their pins land in separate rows.
- Look at the labels printed on your DRV8833. Cheap boards say **IN1–IN4, OUT1–OUT4, EEP, VCC**. Pololu boards say **AIN1, BIN1, AOUT1, SLP, VIN**. The diagram shows both names.

## Your board (WWZMDiB black DRV8833)

| Left side, top to bottom | Connects to | Step |
|---|---|---|
| IN4 | GND | 6 |
| IN3 | ESP32 D27 | 5 |
| GND | ESP32 GND | 1 |
| VCC | ESP32 VIN | 11 |
| IN2 | ESP32 D26 | 4 |
| IN1 | ESP32 D25 | 3 |

| Right side, top to bottom | Connects to | Step |
|---|---|---|
| EEP | ESP32 3V3 | 2 |
| OUT1 | Speaker | 9 |
| OUT2 | Speaker, other lead | 10 |
| OUT3 | LED resistor → LED + | 7 |
| OUT4 | LED − | 8 |
| ULT | Nothing. It's a fault signal and can stay unconnected. | |

## Steps

The numbers match the circles on the diagram.

| # | From | To | What it's for |
|---|---|---|---|
| 1 | ESP32 **GND** | DRV8833 **GND** | Shared ground. Everything has to share it. |
| 2 | ESP32 **3V3** | DRV8833 **SLP / EEP** | Switches the driver on |
| 3 | ESP32 **D25** | DRV8833 **IN1 / AIN1** | Speaker signal, first half of the wave |
| 4 | ESP32 **D26** | DRV8833 **IN2 / AIN2** | Speaker signal, second half of the wave |
| 5 | ESP32 **D27** | DRV8833 **IN3 / BIN1** | LED brightness signal |
| 6 | DRV8833 **IN4 / BIN2** | The GND wire from step 1 | Keeps the LED from ever running backwards |
| 7 | DRV8833 **OUT3 / BOUT1** | One **3 Ω** resistor → LED **+** | LED power |
| 8 | LED **−** | DRV8833 **OUT4 / BOUT2** | LED return |
| 9 | DRV8833 **OUT1 / AOUT1** | Speaker | Speaker power. No resistors: the firmware caps it at 40% for this 4 Ω 3 W speaker. |
| 10 | Speaker's other terminal | DRV8833 **OUT2 / AOUT2** | Speaker return. The speaker can go either way round. |
| 11 | ESP32 **VIN** | DRV8833 **VCC / VM** | 5 V power from the charger, passed through the ESP32 board |

Then:

1. Check the LED's **+** and **−** one more time. Backwards can damage it.
2. Plug a **5 V, 2 A or more** charger into the ESP32's USB port. Use a charger with a USB-A port and a USB-A to USB-C (or micro-USB) cable. USB-C to USB-C chargers may not turn on for this board.
3. The LED comes on dim, at 10%. Open the control page to adjust it. See [control-page.md](control-page.md).

When the ESP32 is plugged into your PC instead of a charger, the PC powers everything. Some PC ports cut out above
about 0.5 A, so keep the light low then and use the charger for real light tests.

## Things not to do

- Don't add a second power supply to VIN or VCC. The ESP32's USB port is the only power input.
- Don't run the LED without its heatsink.
- Don't look straight into the LED. It's bright enough to hurt your eyes.
- Keep the breadboard away from the water.

## LED-only test without the driver

To check the LED, resistor and heatsink before the DRV8833 is wired, with the ESP32 on a charger: ESP32 **VIN** → 3 Ω resistor → LED **+**, and LED **−** → ESP32 **GND**.
The LED runs at full brightness, about 0.5 A, with no dimming. Unplug it if the heatsink gets too hot to hold.
