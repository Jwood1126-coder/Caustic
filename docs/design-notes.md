# Design notes

## Open items

- [ ] Nothing has been printed yet. Real tolerances on the P1S may need one more adjustment.
- [ ] Measure the speaker. If its body is wider than 37 mm, it sits higher in the seat. Hot glue is the only thing holding it.
- [ ] Check the DRV8833 board's pin labels against [wiring.md](wiring.md) when it arrives.
- [ ] Test the firmware with the real LED and speaker attached.
- [ ] Stick felt or rubber pads under the rails and feet.
- The mirror lock is friction only. Hold the mirror whenever you loosen the lock screw.
- The lock screw cuts its thread in plastic, which wears with heavy use. If it strips, a longer M5 screw reaches fresh plastic.
- The stage stays up by clamp friction. Put a spare T-nut and screw in each upright just under an ear as a safety stop.

## Assumptions about parts not yet measured

| Part | Assumed | If yours differs |
|---|---|---|
| Speaker | 40 mm rim, body under 37 mm across below the rim | It sits higher in the seat. That still works. Trim the dipper riser to suit. |
| Speaker cone | Centre about 1 mm below the stage top | The dipper riser is printed 10 mm long for this. |
| Glass dish | 88 to 103 mm across, up to 20 mm tall | Change the seat in `cad/source/rig.py` and regenerate. |
| Mirror tile | 152.4 x 152.4 x 3 mm | The channel is 153.4 mm long and takes glass up to 3.4 mm thick with 1 mm tape. |
| Heatsink | 40 x 40 x 20 mm | The cradle is 40.6 mm wide. |
| LED star | Up to 24 mm across | |
| Extrusion | 2020 with 6 mm slots for M5 T-nuts | |
| The 40 mm acrylic box | Too tall to use as the dish | Its lid may work as a tray. |

## Revision 2 design review

| What was wrong | What it is now |
|---|---|
| The mirror tile passed between the hinge posts with 0.55 mm to spare each side. | The bar is longer, the posts are further apart, and the glass channel has closed ends. |
| Both hinge screws clamped, which could bend or crack a post. | One screw is the lock and the other is only a pivot. |
| The base bracket wall blocked cables between the breadboard and the loads. | A cable port in the wall, and two slots for a cable tie. |
| The rig stood on a base only 120 mm wide and could tip sideways. | Four outrigger feet widen the stance to 280 mm. |
| The heatsink was held in the sled by gravity alone. | Two M3 screws through the cheeks pinch it. |
| The stage ears cleared the uprights by only 0.15 mm. | Clearance is 0.3 mm a side. |
| The dish stops were 4 mm tall, too short to hold the dish. | Stops are 7 mm tall. |
| A spill could run into the speaker seat. | A raised dam surrounds the seat. |
| The window card could go in back to front. | A finger hole marks the end that stays out. |
| The LED sled could be bolted on facing the wrong way. | A raised arrow points at the uprights. |
| The snoot bore cleared the LED star by only 1 mm. | Relieved for boards up to 24 mm across. |
| The dipper arm socket had 0.13 mm of clearance, likely to jam. | Clearance is 0.2 mm a side. |

## How the CAD was checked

93 automatic checks pass. They are checks on the files only. Nothing has been printed or assembled.

- No two parts overlap, and the mirror clears everything at four tilts.
- Every screw lines up with its hole and its slot or thread.
- Every part is located by something, and every sliding fit has its design clearance.
- The beam lands on the flat of the mirror for every window card and tilt.
- Every STL is a single watertight solid according to PrusaSlicer and ADMesh. A test slice with automatic supports switched on placed no support on any part.
- The tipping figures are estimates from rough part weights, not measurements.

## Electronics design choices

- One DRV8833 drives both loads: channel A for the speaker, channel B for the LED.
- 20 kHz PWM on both channels, above hearing.
- The speaker gets a sine wave, not a square wave, so it moves the water without making noise.
- BIN2 is wired to GND, so the LED can never be driven backwards.
- One 3 Ω resistor sets the LED current at about 0.5 A. The speaker (4 Ω 3 W) has no resistor. The firmware caps its duty at 60%, about 0.75 A peak. All power passes through the ESP32 board's USB diode (about 1 A), so full light plus full ripple is near its limit. For more ripple power, feed 5 V straight to VIN and VCC (v2 perfboard).
