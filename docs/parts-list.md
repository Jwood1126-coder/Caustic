# Parts list

## Electronics

| Part | Qty | What it does |
|---|---|---|
| ESP32 DevKit V1 (ESP32-WROOM-32, CP2102 USB) | 1 | The brain. Decides LED brightness and ripple frequency. |
| DRV8833 dual motor driver board | 1 | The muscle. A power switch with two channels: A drives the speaker, B drives the LED. |
| 3 W LED on a star board (about 180 lm) | 1 | The light. Needs about 0.5 A, far more than an ESP32 pin can give. |
| Heatsink, 40 x 40 x 20 mm, with thermal tape | 1 | Keeps the LED from overheating. Never run the LED without it. |
| Speaker, 40 mm | 1 | Taps the water to make ripples. |
| Power resistor, 3 ohm, 5 W (cement, sold in 10-packs) | 4 | One in series with the LED, three in series with the speaker. They limit the current. |
| USB charger, 5 V, 2 A or more, with a USB-A port | 1 | The power. Plugs into the ESP32, which passes 5 V to the driver through its VIN pin. |
| USB-A to USB-C (or micro-USB) cable | 1 | USB-C to USB-C chargers may not turn on for this board. |
| Breadboard with adhesive back | 1 | Holds the electronics. Sticks on the base bracket. |
| Jumper wires | About 12 | Connections. |
| Hook-up wire | Short lengths | Soldered to the LED star and speaker. |

## Frame and hardware

| Part | Qty | Used for |
|---|---|---|
| 2020 aluminium extrusion, 400 mm | 4 | Two rails on the desk, two uprights |
| M5 x 10 screws with drop-in T-nuts | 20 | 8 base bracket, 4 stage, 4 LED sled, 4 feet. Use 10 mm: a 12 mm screw bottoms out before it clamps. |
| M5 x 14 screws | 2 | Mirror hinge (one lock, one pivot) |
| M3 x 8 or M3 x 10 screws | 4 | Card rails under the stage |
| M3 x 8 screws | 2 | Pinch the heatsink in the sled |
| Mirror tile, 6 x 6 in (152.4 mm), 3 mm glass | 1 | Throws the pattern |
| Glass petri dish, about 100 mm across, up to 20 mm tall | 1 | Holds the water |
| Spare M5 screws and T-nuts | 2 | Safety stops under the stage ears |
| Felt or rubber pads | A few | Under the rails and feet |

## Supplies

Mirror mounting tape, hot glue, epoxy or superglue gel, one cable tie, solder.

## Printed parts

See the table in [assembly.md](assembly.md#printing). 15 files, 18 pieces, about 436 g, mostly PETG.
