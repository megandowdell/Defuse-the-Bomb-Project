import random

colors = ["brown", "red", "orange", "yellow", "blue"]
non_simon_discommands = []
non_simon_recommands = []
simon_discommands = []
simon_recommands = []

for color in colors:
    non_simon_discommands.append(f"Disconnect the {color} wire")
    non_simon_recommands.append(f"Reconnect the {color} wire")
    simon_discommands.append(f"Simon says disconnect the {color} wire")
    simon_recommands.append(f"Simon says reconnect the {color} wire")

# Wire state: True = connected (1), False = disconnected (0)
wire_states = {color: True for color in colors}

# Track wires that were affected by valid Simon commands
simon_disconnected = set()
simon_reconnected = set()

commands = []

def display_wire_states():
    """Return wire state as a 5-digit string: brown-red-orange-yellow-blue"""
    return ''.join(['1' if wire_states[color] else '0' for color in colors])

def display_individual_wire_states():
    """Return individual wire states in the format '11111' for all wires."""
    return ''.join(['1' if wire_states[color] else '0' for color in colors])

# Step 1: Ensure the first command is a valid "Simon says disconnect"
first_color = random.choice(colors)
print(f"Wire states: {display_individual_wire_states()}")
print(simon_discommands[colors.index(first_color)])
wire_states[first_color] = False
simon_disconnected.add(first_color)
commands.append(simon_discommands[colors.index(first_color)])

# Step 2: Generate 9 more commands
while len(commands) < 10:
    valid_actions = []

    # Add valid Simon says disconnects
    for color in colors:
        if wire_states[color] and color not in simon_disconnected:
            valid_actions.append(("simon_disconnect", color))

    # Add valid Simon says reconnects
    for color in simon_disconnected:
        if not wire_states[color] and color not in simon_reconnected:
            valid_actions.append(("simon_reconnect", color))

    # Decide on next action
    if valid_actions and random.random() < 0.6:
        action, color = random.choice(valid_actions)
        print(f"Wire states: {display_individual_wire_states()}")
        if action == "simon_disconnect":
            command = simon_discommands[colors.index(color)]
            wire_states[color] = False
            simon_disconnected.add(color)
        elif action == "simon_reconnect":
            command = simon_recommands[colors.index(color)]
            wire_states[color] = True
            simon_reconnected.add(color)
        print(command)
        commands.append(command)
    else:
        # Add a valid non-Simon command (filler) — only if logically allowed
        cmd = None
        if random.choice(["disconnect", "reconnect"]) == "disconnect":
            valid = [c for c in colors if wire_states[c]]
            if valid:
                color = random.choice(valid)
                cmd = non_simon_discommands[colors.index(color)]
        else:
            valid = [c for c in simon_disconnected if not wire_states[c] and c not in simon_reconnected]
            if valid:
                color = random.choice(valid)
                cmd = non_simon_recommands[colors.index(color)]

        if cmd:
            print(f"Wire states: {display_individual_wire_states()}")
            print(cmd)
            commands.append(cmd)
