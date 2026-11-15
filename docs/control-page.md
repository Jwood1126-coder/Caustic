# Control page

The ESP32 hosts its own control page. Use it from your phone, tablet or laptop to change the light and ripples while you watch.

## Connect, the quick way (no setup)

1. Power the rig.
2. On your phone, open Wi-Fi settings and join **Caustic-Rig**. The password is **causticrig**.
   Your phone may warn that this network has no internet. That's expected. Choose to stay connected.
3. Open a browser and go to **http://192.168.4.1**

## Connect over your home Wi-Fi (optional, one-time setup)

This lets you use the page without switching networks.

1. Connect the quick way above.
2. At the bottom of the page, open **Home Wi-Fi**, enter your network name and password, and tap **Save and restart**.
3. Switch your phone back to your home Wi-Fi.
4. Go to **http://caustic.local**. If that doesn't load (some Android phones don't support `.local` names), open the
   Serial Monitor at 115200 baud and restart the ESP32. It prints its home IP address, for example `http://192.168.1.42`.

The **Caustic-Rig** network keeps working either way. To remove the saved network, tap **Forget home Wi-Fi**.

## What the controls do

| Control | What it does | Good starting point |
|---|---|---|
| **Light** | LED brightness, 0–100% | 10–25% while testing. Feel the heatsink. |
| **Ripple strength** | How hard the speaker taps the water | Around 10% |
| **Ripple speed** | Taps per second (Hz) | 1–2 Hz sloshes the whole dish. 5–25 Hz makes fine ripples. |
| **Patterns** | 30 looping speed patterns: flicks, slow rises, wobbles, pulses. The list is in [firmware.md](firmware.md#ripple-patterns). | Start with 1 Flick, 13 Slow rise or 30 Shuffle |
| **Sweep** | Glides the speed from one value to another | 5 → 25 Hz over 20 s, to find what looks best |
| **Flicker fix** | Keeps the light level while the speaker runs. Saved on the rig. | Set speed to 2 Hz, raise until the light stops pulsing (about 30%) |
| **Stop ripples** | Turns the speaker off. The light stays on. | |
| **Everything off** | Light and speaker off | |

The page checks in with the rig every second. The pill at the top says **connected** or **not connected**.

## Troubleshooting

| Problem | Try this |
|---|---|
| Can't find **Caustic-Rig** in Wi-Fi settings | Check the ESP32 has power (its red LED is on). Wait 5 seconds after power-up. |
| Page won't load | Make sure you typed **http://** and not https://. Turn off mobile data for a moment so the phone uses the rig's Wi-Fi. |
| Page says **not connected** | The phone left the Caustic-Rig network. Rejoin it. |
| Slider moves but the LED doesn't change | Check wires 2, 5, 7, 8 and 11 in [wiring.md](wiring.md), and that the 5 V charger is plugged in. |
| Speaker does nothing | Check wires 3, 4, 9 and 10. Raise Ripple strength above 10%. |
