# Printing and assembly

## Printing

Print on the Bambu P1S. Import the STEP files (smoother curves) or STL files from [`cad/`](../cad/) into Bambu Studio.
Each part is already turned to its print orientation, so don't rotate it.

- 0.4 mm nozzle, 0.2 mm layers, 3 walls, 15% infill
- **No supports on any part.** Sideways holes are teardrop-shaped for this reason.
- Brim only on `hinge_bar`.
- Print the small parts first and check their fit before the stage.
- For PLA parts on the textured PEI plate, open the door or take off the top glass to avoid heat-creep clogs.

| File | Qty | Size on the bed, mm | Filament | Notes |
|---|---|---|---|---|
| `stage` | 1 | 163 x 195 x 52 | 124 g | PETG. Plate, dish seat, speaker seat, hinge posts and clamp ears in one piece. |
| `card_rails` | 1 | 88 x 100 x 4 | 9 g | Any filament. Lips face the bed. |
| `window_card_24x34` | 1 | 108 x 85 x 2 | 19 g | Black. |
| `window_card_32x44` | 1 | 108 x 85 x 2 | 18 g | Black. |
| `window_card_40x56` | 1 | 108 x 85 x 2 | 16 g | Black. |
| `window_card_slit_8x56` | 1 | 108 x 85 x 2 | 20 g | Black. |
| `hinge_bar` | 1 | 12 x 157 x 54 | 42 g | PETG. Prints standing on its narrow edge. Add a 5 mm brim. |
| `led_sled` | 1 | 72 x 120 x 34 | 35 g | PETG. It sits next to a warm heatsink. |
| `snoot` | 1 | 38 x 38 x 38 | 8 g | Matte black. Line it with black paper if the inside looks shiny. |
| `base_bracket` | 1 | 130 x 120 x 90 | 103 g | PETG or PLA. The breadboard sticks on top. |
| `dipper_foot` | 1 | 12 x 12 x 8 | under 1 g | PLA. Glued to the speaker cone. |
| `dipper_arm_wedge` | 1 | 42 x 36 x 3 | 1 g | PLA. The riser is 10 mm long so you can trim it. |
| `dipper_arm_paddle` | 1 | 42 x 36 x 3 | 1 g | PLA. |
| `dipper_arm_pin` | 1 | 42 x 36 x 3 | 1 g | PLA. |
| `outrigger_foot` | 4 | 24 x 80 x 20 | 40 g | Any filament. Print four. |

## How every part mounts

| Part | Goes on | Held by | Located by |
|---|---|---|---|
| Base bracket | Both rails and both uprights | 8 M5 x 10 screws with T-nuts | Back edge flush with the rail ends. Uprights sit against its wall. |
| Uprights (2) | The rails | The base bracket wall, 2 screws each | Standing on the rail, against the wall. |
| Outrigger feet (4) | Outer side slots of the rails | 1 M5 x 10 screw with T-nut each | Flat on the desk beside the rail. |
| Stage | Both uprights | 4 M5 x 10 screws with T-nuts, through the side ears | Flange against the upright fronts, ears outside them. |
| Card rails | Underside of the stage | 4 M3 screws that cut their own thread, or glue | The four screw holes. |
| Window card | Card rails | Friction. It slides in from the front | Rear bar, lips and the stage above. |
| Glass dish | Stage | Its own weight | Raised lip and four stops. |
| Speaker | Stage | Hot glue on the rim | Tapered seat. |
| Dipper foot | Speaker cone | Epoxy or superglue gel | By eye, with an arm fitted and pointing at the dish. |
| Dipper arm | Dipper foot | Push fit. Add a drop of glue once you like it | Square socket. |
| Hinge bar | The two stage posts | One M5 x 14 lock screw and one M5 x 14 pivot screw | Between the posts. |
| Mirror tile | Hinge bar | Mirror mounting tape, with the channel as a catch | Channel with closed ends. |
| LED sled | Both rails | 4 M5 x 10 screws with T-nuts | Raised arrow points at the uprights. Slides along the rails. |
| Heatsink | LED sled | Its own weight, plus 2 M3 screws through the cheeks | Ledges, cheeks and two stops. |
| LED star | Heatsink | The heatsink's thermal tape | Centred by eye. |
| Snoot | Heatsink | The same thermal tape, under its flange | Around the star, notch over the leads. |
| Breadboard | Base bracket | Its adhesive backing | Behind the uprights. |
| Cables | Base bracket | A cable tie through the two slots | They pass forward through the port in the wall. |

## Assembly steps

1. **Frame.** Lay two extrusions parallel, 100 mm apart centre to centre, a slot facing up. Set the base bracket on top with its back edge flush with the rail ends and fix it with four M5 x 10 screws and T-nuts. Stand the other two extrusions on the rails against the bracket wall and fix each with two screws into its rear slot. Leave these four slightly loose for now.
2. **Feet.** Bolt the four outrigger feet to the outer side slots of the rails, two near the back and two near the front, flat on the desk.
3. **Stage.** Screw the card rails under the stage, lips down, open end to the front. Push the stage onto the uprights from the front so its ears sit outside them. Drop T-nuts into the outer slots, set the underside of the stage plate 162 mm above the top of the rails and tighten the four side screws. Now tighten the upright screws. Add a spare T-nut and screw under each ear as a safety stop.
4. **Wave driver.** Push a dipper arm into the dipper foot, then glue the foot to the centre of the speaker cone with the arm pointing at the dish, and let it set. Solder the leads on. Drop the speaker into its tapered seat with the terminals in the notch and fix the rim with hot glue. Trim the bottom of the arm riser until the arm clears the dish rim by 3 to 5 mm.
5. **Light.** Solder leads to the LED star and stick it to the centre of the heatsink's thermal tape. Stick the snoot's flange around it with the notch over the leads. Lay the heatsink in the sled, low end against the two stops, and nip it with two M3 screws through the cheeks. Bolt the sled across the rails with its arrow pointing at the uprights and its rear edge 115 mm in front of them.
6. **Mirror.** Put mirror tape on the tall pad of the hinge bar. Stand the bottom edge of the tile in the channel and press it onto the tape. Lower the bar between the two posts. On the side away from the speaker, run an M5 x 14 screw through the post into the bar: this is the lock. On the speaker side, run the other M5 x 14 into the post until its head is snug: this one is only a pivot.
7. **Electronics.** Stick the breadboard on the base bracket. Wire it as in [wiring.md](wiring.md). Pass the LED and speaker leads forward through the port in the bracket wall and tie the cables down through the two slots.
8. **Water.** Slide in a window card with its finger hole toward you, set the dish on the raised lip between the four stops, and add water until the dipper tip is about half under.

## Adjusting

- **LED-to-water distance:** loosen the four stage side screws and slide the stage.
- **Lean:** loosen the sled and slide it along the rails.
- **Mirror tilt:** hold the mirror, loosen the lock screw, move it and retighten. It's glass above water, so always hold it.
