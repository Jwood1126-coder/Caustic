"""Text shared by the README and the project page: how each part mounts, the assembly order, and what the review changed."""

# part, what it goes on, what holds it, what locates it
MOUNTS = [
    ('Base bracket', 'Both rails and both uprights', '8 M5 x 10 screws with T-nuts', 'Back edge flush with the rail ends. Uprights sit against its wall.'),
    ('Uprights (2)', 'The rails', 'The base bracket wall, 2 screws each', 'Standing on the rail, against the wall.'),
    ('Outrigger feet (4)', 'Outer side slots of the rails', '1 M5 x 10 screw with T-nut each', 'Flat on the desk beside the rail.'),
    ('Stage', 'Both uprights', '4 M5 x 10 screws with T-nuts, through the side ears', 'Flange against the upright fronts, ears outside them.'),
    ('Card rails', 'Underside of the stage', '4 M3 screws that cut their own thread, or glue', 'The four screw holes.'),
    ('Window card', 'Card rails', 'Friction. It slides in from the front', 'Rear bar, lips and the stage above.'),
    ('Glass dish', 'Stage', 'Its own weight', 'Raised lip and four stops.'),
    ('Speaker', 'Stage', 'Hot glue on the rim', 'Tapered seat.'),
    ('Dipper foot', 'Speaker cone', 'Epoxy or superglue gel', 'By eye, with an arm fitted and pointing at the dish.'),
    ('Dipper arm', 'Dipper foot', 'Push fit. Add a drop of glue once you like it', 'Square socket.'),
    ('Hinge bar', 'The two stage posts', 'One M5 x 14 lock screw and one M5 x 14 pivot screw', 'Between the posts.'),
    ('Mirror tile', 'Hinge bar', 'Mirror mounting tape, with the channel as a catch', 'Channel with closed ends.'),
    ('LED sled', 'Both rails', '4 M5 x 10 screws with T-nuts', 'Raised arrow points at the uprights. Slides along the rails.'),
    ('Heatsink', 'LED sled', 'Its own weight, plus 2 M3 set screws through the cheeks', 'Ledges, cheeks and two stops.'),
    ('LED star', 'Heatsink', "The heatsink's thermal tape", 'Centred by eye.'),
    ('Snoot', 'Heatsink', 'The same thermal tape, under its flange', 'Around the star, notch over the leads.'),
    ('Breadboard', 'Base bracket', 'Its adhesive backing', 'Behind the uprights.'),
    ('Cables', 'Base bracket', 'A cable tie through the two slots', 'They pass forward through the port in the wall.'),
]

# what was wrong, what it is now
REVIEW = [
    ('The mirror tile passed between the hinge posts with 0.55 mm to spare each side.',
     'The bar is longer, the posts are further apart, and the glass channel has closed ends. The tile is centred by the bar and cannot reach a post.'),
    ('Both hinge screws clamped. Tightening the second one would have bent a post sideways by up to 0.8 mm and could crack it.',
     'One screw is now the lock and the other is only a pivot. Nothing bends when you tighten them.'),
    ('The base bracket wall sat between the breadboard and everything it powers, with no way through.',
     'A cable port in the wall between the uprights, and two slots for a cable tie.'),
    ('The rig stood on a base only 120 mm wide. By my estimate a 2 to 3 N push at the top of the mirror would tip it sideways.',
     'Four outrigger feet widen the stance to 280 mm, which roughly doubles the push it takes.'),
    ('The heatsink was held in the sled by gravity alone.', 'Two holes through the cheeks take M3 set screws that pinch it.'),
    ('The stage ears cleared the uprights by 0.15 mm, less than the flare a first layer usually has.', 'Clearance is 0.3 mm a side.'),
    ('The dish stops were 4 mm tall and caught under 3 mm of the dish, about the radius of its bottom corner.', 'Stops are 7 mm tall.'),
    ('A spill on the stage could run straight into the speaker seat.', 'A raised dam surrounds the seat, like the one around the beam hole.'),
    ('The window card could be pushed in back to front, putting the window in the wrong place.', 'A finger hole marks the end that stays out.'),
    ('The LED sled could be bolted on facing the wrong way.', 'A raised arrow points at the uprights.'),
    ('The snoot bore cleared the LED star by 1 mm, and star boards vary.', 'The base of the bore is relieved for boards up to 24 mm across.'),
    ('The dipper arm socket had 0.13 mm of clearance, which usually prints as a jam.', 'Clearance is 0.2 mm a side.'),
]

# things the files cannot fix
OPEN = [
    'Nothing has been printed. Real tolerances on your printer may need one more adjustment.',
    'Your speaker is still unmeasured, and hot glue is the only thing holding it. If its body is wider than 37 mm it sits higher in the seat.',
    'The mirror lock is friction only. Hold the mirror whenever you loosen the lock screw. It is glass above a dish of water.',
    'The lock screw cuts its thread in plastic. That wears with heavy use. If it strips, a longer M5 screw reaches fresh plastic.',
    'The stage stays up by clamp friction. Put a spare T-nut and screw in each upright just under an ear as a safety stop.',
    'The rails sit directly on the desk. Stick felt or rubber pads under them and under the feet.',
    'The stage is the largest part at about 124 g. Print the small parts first and check their fit before committing to it.',
]

NOTE = {
    'stage': 'PETG. Plate, dish seat, speaker seat, hinge posts and clamp ears in one piece.',
    'base_bracket': 'PETG or PLA. Squares the two rails and two uprights. The breadboard sticks on top.',
    'hinge_bar': 'PETG. Prints standing on its narrow edge, so add a 5 mm brim.',
    'led_sled': 'PETG. It sits next to a warm heatsink.',
    'snoot': 'Matte black. Line it with black paper if the inside looks shiny.',
    'card_rails': 'Any filament. Lips face the bed.',
    'dipper_foot': 'PLA. Glued to the centre of the speaker cone.',
    'outrigger_foot': 'Any filament. Print four.',
}
CARD_NOTE = 'Black. Slides in under the stage, finger hole outward.'
ARM_NOTE = 'PLA. Prints flat. The riser is 10 mm longer than needed so you can trim it.'


def steps(stage_height, sled_offset):
    return [
        'Frame. Lay two extrusions parallel, 100 mm apart centre to centre, a slot facing up. Set the base bracket on top with its back edge flush with the rail ends and fix it with four M5 x 10 screws and T-nuts. '
        'Stand the other two extrusions on the rails against the bracket wall and fix each with two screws into its rear slot. Leave these four slightly loose for now.',
        'Feet. Bolt the four outrigger feet to the outer side slots of the rails, two near the back and two near the front, flat on the desk.',
        f'Stage. Screw the card rails under the stage, lips down, open end to the front. Push the stage onto the uprights from the front so its ears sit outside them. Drop T-nuts into the outer slots, '
        f'set the underside of the stage plate {stage_height:.0f} mm above the top of the rails and tighten the four side screws. Now tighten the upright screws.',
        'Wave driver. Push a dipper arm into the dipper foot, then glue the foot to the centre of the speaker cone with the arm pointing at the dish, and let it set. Solder the leads on. '
        'Drop the speaker into its tapered seat with the terminals in the notch and fix the rim with hot glue. Trim the bottom of the arm riser until the arm clears the dish rim by 3 to 5 mm.',
        f"Light. Solder leads to the LED star and stick it to the centre of the heatsink's thermal tape. Stick the snoot's flange around it with the notch over the leads. Lay the heatsink in the sled, low end against the two stops, "
        f"and nip it with two M3 screws through the cheeks. Bolt the sled across the rails with its arrow pointing at the uprights and its rear edge {sled_offset:.0f} mm in front of them.",
        'Mirror. Put mirror tape on the tall pad of the hinge bar. Stand the bottom edge of the tile in the channel and press it onto the tape. Lower the bar between the two posts. '
        'On the side away from the speaker, run an M5 x 14 screw through the post into the bar: this is the lock. On the speaker side, run the other M5 x 14 into the post until its head is snug: this one is only a pivot.',
        'Electronics. Stick the breadboard on the base bracket. Pass the LED and speaker leads forward through the port in the bracket wall and tie the cables down through the two slots.',
        'Water. Slide in a window card with its finger hole toward you, set the dish on the raised lip between the four stops, and add water until the dipper tip is about half under.',
    ]


HARDWARE = [
    '20 M5 x 10 screws with drop-in T-nuts, from your kit: 8 for the base bracket, 4 for the stage, 4 for the LED sled and 4 for the feet. Use the 10 mm length. A 12 mm screw bottoms out in the slot before it clamps.',
    '2 M5 x 14 screws, from your kit, for the mirror hinge.',
    '4 M3 x 8 or M3 x 10 screws for the card rails, and 2 M3 x 8 for the heatsink.',
    'Mirror mounting tape, hot glue, epoxy or superglue gel, and one cable tie.',
    'No heat-set inserts. Your corner brackets are not needed, but you can add them at the front of the uprights.',
]
