# Testing

## Bench tests

Run these on the breadboard before anything is mounted on the rig.

1. **Firmware alive.** Plug in the ESP32 and open Serial Monitor at 115200. You should see `Caustic rig ready.` Type `status`.
2. **LED.** With the LED on its heatsink, type `led 10`, then step up through `led 25`, `led 50` and `led 100`. Feel the heatsink after a minute at each step. Warm is fine. Too hot to hold is not.
3. **Speaker.** Type `amp 10` and `freq 10`. You should feel the cone move, with little or no sound. Try `sweep 5 25 20`. Type `stop` when you're done.
4. **Both together.** Set `led 50` and `amp 20` and leave them running for five minutes. Check that the resistors and heatsink stay warm, not hot.

## Rig tests

In order, with the room dark:

1. **Mirror flipped up.** The pattern goes straight to the ceiling with no mirror involved. This is your reference for sharpness.
2. **Ripples.** Sweep the speaker from 5 to 25 Hz at low power (`amp 10`, `sweep 5 25 30`), then try 1 to 2 Hz, where the whole dish sloshes. Start with ripples you can barely see.
3. **Mirror down.** Set the tilt, then move the rig between 0.5 and 2 m from the wall.
4. **LED distance.** Loosen the four side screws and slide the stage. A closer LED gives a bigger, softer pattern. A farther LED gives a smaller, sharper one.
5. **Window cards.** Go larger until the beam spills off the mirror.
6. **Lean.** Slide the LED sled along the rails and re-aim the mirror.

## Expected pattern size

Estimates from straight-line ray geometry, assuming a 180 lm LED with 78% getting through the glass, water and mirror.

| Mirror | Wall at 0.5 m | Wall at 1 m | Wall at 2 m |
|---|---|---|---|
| Low (throws 5°) | 0.41 x 0.25 m, 50 lux | 0.63 x 0.38 m, 21 lux | 1.08 x 0.65 m, 7 lux |
| Middle (throws 20°) | 0.45 x 0.28 m, 41 lux | 0.70 x 0.43 m, 17 lux | 1.19 x 0.74 m, 6 lux |
| High (throws 35°) | 0.54 x 0.37 m, 27 lux | 0.84 x 0.57 m, 11 lux | 1.43 x 0.98 m, 4 lux |
