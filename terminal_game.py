import random
import time
import sys # Used for text printing effect

# Helper function for slightly slower text printing
def slow_print(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print() # Newline at the end

# ==================================
# GAME DATA (Monsters, Skills, Items, Locations)
# ==================================

# --- Player Skills ---
# Cooldown resets at the START of the player's turn
PLAYER_SKILLS = {
    "slash": {"name": "Basic Slash", "cost": 0, "damage": (8, 12), "cooldown": 0, "max_cooldown": 0, "type": "attack"},
    "fireball": {"name": "Fireball", "cost": 15, "damage": (15, 25), "cooldown": 0, "max_cooldown": 2, "type": "magic"},
    "heal_light": {"name": "Minor Heal", "cost": 20, "heal": (20, 30), "cooldown": 0, "max_cooldown": 2, "type": "heal"},
    "shield_bash": {"name": "Shield Bash", "cost": 10, "damage": (5, 8), "effect": "stun", "duration": 1, "cooldown": 0, "max_cooldown": 2, "type": "utility"}, # Stuns for 1 enemy turn
    "dragon_breath": {"name": "Dragon Breath", "cost": 40, "damage": (40, 60), "cooldown": 0, "max_cooldown": 4, "type": "ultimate"}
}

# --- Monsters ---
# Tactics guide enemy AI: 'attack', 'heavy_attack', 'defend', 'special'
MONSTERS = {
    "level1": [
        {"name": "Giant Rat", "hp": 25, "attack": (3, 6), "xp": 10, "tactics": ["attack"]},
        {"name": "Goblin Skirmisher", "hp": 40, "attack": (5, 8), "xp": 15, "tactics": ["attack", "attack", "defend"]},
        {"name": "Cave Bat", "hp": 30, "attack": (4, 7), "xp": 12, "tactics": ["attack"]},
    ],
    "level2": [
        {"name": "Orc Grunt", "hp": 60, "attack": (8, 14), "xp": 25, "tactics": ["attack", "heavy_attack"]},
        {"name": "Skeleton Warrior", "hp": 50, "attack": (7, 12), "xp": 20, "tactics": ["attack", "attack"]},
        {"name": "Dark Spider", "hp": 45, "attack": (6, 10), "effect": "poison", "xp": 22, "tactics": ["attack", "special"]}, # Special could be poison
    ],
    "level3": [
        {"name": "Troll", "hp": 100, "attack": (12, 20), "xp": 40, "tactics": ["heavy_attack", "heavy_attack", "attack"]},
        {"name": "Gargoyle", "hp": 80, "attack": (10, 16), "defense_buff": 5, "xp": 35, "tactics": ["attack", "defend", "attack"]}, # Defend could buff itself
        {"name": "Shadow Imp", "hp": 60, "attack": (9, 15), "effect": "curse", "xp": 38, "tactics": ["attack", "special", "attack"]}, # Special could curse (reduce player attack?)
    ],
    "level4": [
        {"name": "Ogre Magi", "hp": 120, "attack": (10, 15), "magic_attack": (15, 25), "xp": 60, "tactics": ["attack", "special", "attack"]}, # Special = magic attack
        {"name": "Stone Golem", "hp": 150, "attack": (14, 22), "resistance": "physical", "xp": 70, "tactics": ["heavy_attack", "attack"]}, # Might need resistance logic
        {"name": "Harpy", "hp": 90, "attack": (13, 19), "xp": 55, "tactics": ["attack", "attack", "special"]}, # Special could be dive bomb?
    ],
    "level5": [
        {"name": "Dread Knight", "hp": 180, "attack": (18, 28), "xp": 100, "tactics": ["heavy_attack", "attack", "defend"]},
        {"name": "Wyvern Hatchling", "hp": 160, "attack": (16, 26), "effect": "burn", "xp": 90, "tactics": ["attack", "special", "attack"]},
        {"name": "Mind Flayer Spawn", "hp": 140, "attack": (15, 24), "effect": "confusion", "xp": 95, "tactics": ["special", "attack", "special"]},
    ]
}

# --- Bosses ---
BOSSES = {
    1: {"name": "Goblin Chieftain", "hp": 100, "attack": (10, 16), "xp": 50, "tactics": ["heavy_attack", "attack", "summon_goblin"]}, # Summon could add a weak goblin
    2: {"name": "Necromancer Apprentice", "hp": 150, "attack": (8, 12), "magic_attack": (15, 25), "xp": 75, "tactics": ["special", "summon_skeleton", "attack"]}, # Special = magic, summon adds skeleton
    3: {"name": "Cave Hydra", "hp": 250, "attack": (15, 24), "xp": 120, "tactics": ["multi_attack", "heavy_attack", "special"]}, # Multi-attack hits multiple times? Special = breath weapon?
    4: {"name": "Elemental Lord (Stone)", "hp": 300, "attack": (20, 30), "resistance": "physical", "xp": 180, "tactics": ["heavy_attack", "special", "defend"]}, # Special = earthquake?
    5: {"name": "Shadow Dragon", "hp": 500, "attack": (25, 35), "magic_attack": (30, 45), "xp": 300, "tactics": ["heavy_attack", "special_breath", "fear_roar", "attack", "defend", "tail_swipe"]}, # Final boss tactics
}

# --- Locations (Simple Map per Level) ---
# Locations lead to other locations or trigger fights/events
LOCATIONS = {
    1: {
        "Forgotten Trail": {"description": "An overgrown path leads into shadows.", "connections": ["Murky Cave Entrance"], "event": None},
        "Murky Cave Entrance": {"description": "Water drips, the air is damp. Strange noises echo within.", "connections": ["Forgotten Trail", "Goblin Guardroom"], "event": "fight"},
        "Goblin Guardroom": {"description": "Crude beds and discarded bones litter the floor.", "connections": ["Murky Cave Entrance", "Chieftain's Lair"], "event": "fight"},
        "Chieftain's Lair": {"description": "A large, foul-smelling chamber. The boss awaits.", "connections": ["Goblin Guardroom"], "event": "boss"}
    },
    # Add levels 2-5 similarly...
    2: {
        "Ancient Crypt Door": {"description": "A heavy stone door, slightly ajar.", "connections": ["Dusty Antechamber"], "event": None},
        "Dusty Antechamber": {"description": "Cobwebs hang thick, the scent of decay is strong.", "connections": ["Ancient Crypt Door", "Skeletal Barracks", "Trapped Hallway"], "event": "fight"},
        "Skeletal Barracks": {"description": "Armored bones lie scattered, some still twitching.", "connections": ["Dusty Antechamber"], "event": "fight"},
        "Trapped Hallway": {"description": "Pressure plates and dart holes line the walls.", "connections": ["Dusty Antechamber", "Necromancer's Study"], "event": "fight"}, # Maybe add a trap event?
        "Necromancer's Study": {"description": "Books bound in strange leather line the shelves. A figure chants.", "connections": ["Trapped Hallway"], "event": "boss"}
    },
     3: {
        "Humid Jungle Path": {"description": "Thick vines and giant leaves obscure the way.", "connections": ["Troll Bridge"], "event": None},
        "Troll Bridge": {"description": "A crudely built bridge spans a chasm. A large shadow looms.", "connections": ["Humid Jungle Path", "Gargoyle Roost", "Hidden Spring"], "event": "fight"}, # Could be a guaranteed Troll fight
        "Gargoyle Roost": {"description": "Sharp rocks form ledges high above. Stone figures watch silently.", "connections": ["Troll Bridge"], "event": "fight"},
        "Hidden Spring": {"description": "A clear spring bubbles, surrounded by glowing moss.", "connections": ["Troll Bridge", "Hydra's Grotto"], "event": "fight"}, # Maybe a Shadow Imp here?
        "Hydra's Grotto": {"description": "A vast, damp cavern filled with deep pools. Multiple heads rise from the water.", "connections": ["Hidden Spring"], "event": "boss"}
    },
    4: {
        "Windy Mountain Pass": {"description": "Loose scree shifts underfoot. The wind howls.", "connections": ["Ogre Encampment"], "event": None},
        "Ogre Encampment": {"description": "Large, crude tents surround a roaring bonfire.", "connections": ["Windy Mountain Pass", "Golem Workshop", "Harpy Crag"], "event": "fight"},
        "Golem Workshop": {"description": "Half-finished stone figures stand amidst carving tools.", "connections": ["Ogre Encampment"], "event": "fight"},
        "Harpy Crag": {"description": "High cliffs offer nesting grounds. Screeches echo.", "connections": ["Ogre Encampment", "Elemental Gate"], "event": "fight"},
        "Elemental Gate": {"description": "A shimmering portal pulses with raw, stony energy.", "connections": ["Harpy Crag"], "event": "boss"}
    },
    5: {
        "Shadowfell Approach": {"description": "The light dims, the air grows cold. Twisted trees grasp at you.", "connections": ["Knight's Outpost"], "event": None},
        "Knight's Outpost": {"description": "A ruined guard tower manned by an unnerving armored figure.", "connections": ["Shadowfell Approach", "Wyvern Nesting Grounds", "Mind Flayer Caverns"], "event": "fight"},
        "Wyvern Nesting Grounds": {"description": "Large nests made of bone and shadow lie scattered.", "connections": ["Knight's Outpost"], "event": "fight"},
        "Mind Flayer Caverns": {"description": "Strange symbols glow on damp walls. A low hum vibrates the air.", "connections": ["Knight's Outpost", "Dragon's Sanctum"], "event": "fight"},
        "Dragon's Sanctum": {"description": "A colossal cavern filled with obsidian shards. A massive shadow uncoils.", "connections": ["Mind Flayer Caverns"], "event": "boss"}
    }

}

# --- Items ---
ITEMS = {
    "health_potion": {"name": "Health Potion", "effect": "heal", "value": 40, "description": "Restores 40 HP."},
    "mana_potion": {"name": "Mana Potion", "effect": "mana", "value": 30, "description": "Restores 30 MP."},
    "whetstone": {"name": "Whetstone", "effect": "buff", "stat": "attack", "value": 3, "duration": 3, "description": "Temporarily sharpens your blade (+3 Attack for 3 turns)."}
}

# ==================================
# PLAYER STATE
# ==================================
player = {
    "name": "Hunter",
    "hp": 100,
    "max_hp": 100,
    "mp": 50,
    "max_mp": 50,
    "base_attack": 10, # Base damage, modified by skill
    "level": 1,
    "xp": 0,
    "skills": PLAYER_SKILLS,
    "inventory": {"health_potion": 2, "mana_potion": 1},
    "current_location_id": "Forgotten Trail", # Start at level 1 entrance
    "current_level": 1,
    "fights_this_level": 0,
    "stunned_turns": 0, # For enemy stun effect
    "buffs": {} # Store active buffs like {'attack': {'value': 3, 'turns_left': 3}}
}

# ==================================
# GAME HELPER FUNCTIONS
# ==================================

def clear_screen():
    # Simple way to add spacing, less jarring than os.system('cls')/'clear'
    print("\n" * 30)

def display_player_status():
    slow_print(f"--- {player['name']} | Level {player['level']} ---", delay=0.01)
    slow_print(f"HP: {player['hp']}/{player['max_hp']} | MP: {player['mp']}/{player['max_mp']}", delay=0.01)
    # Display Cooldowns
    cooldowns = []
    for key, skill in player['skills'].items():
        if skill['max_cooldown'] > 0:
            ready = "Ready" if skill['cooldown'] == 0 else f"{skill['cooldown']} turns"
            cooldowns.append(f"{skill['name']}: {ready}")
    if cooldowns:
        slow_print("Cooldowns: " + " | ".join(cooldowns), delay=0.01)
    # Display Buffs
    active_buffs = []
    for key, buff in player['buffs'].items():
        active_buffs.append(f"{key.capitalize()} +{buff['value']} ({buff['turns_left']} turns)")
    if active_buffs:
        slow_print("Active Buffs: " + " | ".join(active_buffs), delay=0.01)
    print("-" * 20)


def display_enemy_status(enemy):
    slow_print(f"--- {enemy['name']} ---", delay=0.01)
    slow_print(f"HP: {enemy['hp']}", delay=0.01)
    print("-" * 20)

def get_valid_input(prompt, valid_options):
    while True:
        choice = input(prompt).lower()
        if choice in valid_options:
            return choice
        else:
            slow_print("Invalid choice. Please select from the available options.")

def calculate_damage(base_damage_range):
    return random.randint(base_damage_range[0], base_damage_range[1])

def apply_status_effect(target, effect, duration):
    # Basic example - expand with more effects
    if effect == "stun" and 'stunned_turns' in target:
        target['stunned_turns'] = max(target.get('stunned_turns', 0), duration) # Apply longest duration
        slow_print(f"{target.get('name', 'Target')} is stunned for {duration} turn(s)!", 0.02)
    elif effect == "poison":
        # Implement poison damage over time if desired
        slow_print(f"{target.get('name', 'Target')} is poisoned!", 0.02)
        pass
    elif effect == "burn":
        slow_print(f"{target.get('name', 'Target')} is burning!", 0.02)
        pass
    elif effect == "confusion":
         slow_print(f"{target.get('name', 'Target')} looks confused!", 0.02)
         # Could make enemy attack itself sometimes
         pass
    # Add more effects (curse, fear, etc.)

def update_buffs(target):
    keys_to_delete = []
    for key, buff in target['buffs'].items():
        buff['turns_left'] -= 1
        if buff['turns_left'] <= 0:
            keys_to_delete.append(key)
            slow_print(f"{target['name']}'s {key} buff wore off.", 0.02)
    for key in keys_to_delete:
        del target['buffs'][key]

def get_player_attack():
    base = player['base_attack']
    buff_mod = player['buffs'].get('attack', {}).get('value', 0)
    return base + buff_mod

# ==================================
# COMBAT FUNCTIONS
# ==================================

def player_turn(enemy):
    global player # Allow modification of player state

    # Decrement cooldowns at the START of the turn
    for key, skill in player['skills'].items():
        if skill['cooldown'] > 0:
            skill['cooldown'] -= 1

    # Update and apply buffs/debuffs
    update_buffs(player) # Update player buffs

    # Check if player is stunned
    if player.get('stunned_turns', 0) > 0:
        slow_print(f"{player['name']} is stunned and cannot act!", 0.02)
        player['stunned_turns'] -= 1
        return # Skip turn

    display_player_status()
    display_enemy_status(enemy)

    slow_print("Choose your action:")
    options = {"a": "Attack (Basic Slash)"}
    valid_choices = ["a"]

    # Add spells if affordable and off cooldown
    skill_index = 1
    skill_map = {} # Map '1', '2', etc. back to skill key
    for key, skill in player['skills'].items():
        if key == "slash": continue # Skip basic attack here
        cost = skill.get('cost', 0)
        cooldown = skill.get('cooldown', 0)
        is_affordable = player['mp'] >= cost
        is_ready = cooldown == 0
        option_text = f"{skill['name']} (Cost: {cost} MP"
        if skill['max_cooldown'] > 0:
             option_text += f", CD: {'Ready' if is_ready else str(cooldown)+'t'})"
        else:
             option_text += ")"

        if is_affordable and is_ready:
            options[str(skill_index)] = option_text
            valid_choices.append(str(skill_index))
            skill_map[str(skill_index)] = key
        else:
            # Show unusable skills grayed out or similar (simple print for now)
            print(f"   ({skill_index}) {option_text} - {'Not Ready' if not is_ready else 'Not Enough MP'}")

        skill_index += 1

    # Add items
    item_index_start = skill_index
    item_map = {}
    for item_key, count in player['inventory'].items():
        if count > 0:
            item_data = ITEMS.get(item_key)
            if item_data:
                option_text = f"Use {item_data['name']} ({count} left)"
                options[str(skill_index)] = option_text
                valid_choices.append(str(skill_index))
                item_map[str(skill_index)] = item_key
                skill_index += 1

    # Print available options
    for key, text in options.items():
        slow_print(f"   {key}. {text}", 0.01)

    # Get player choice
    action = get_valid_input("Your choice: ", valid_choices)

    # Execute action
    if action == 'a': # Basic Attack
        damage = calculate_damage(player['skills']['slash']['damage']) + get_player_attack() - player['base_attack'] # Add attack stat bonus
        enemy['hp'] -= damage
        slow_print(f"You slash the {enemy['name']} for {damage} damage!", 0.02)
    elif action in skill_map: # Used a Skill
        skill_key = skill_map[action]
        skill = player['skills'][skill_key]
        player['mp'] -= skill['cost']
        skill['cooldown'] = skill['max_cooldown'] # Set cooldown

        slow_print(f"You cast {skill['name']}!", 0.02)
        if skill.get('damage'):
            damage = calculate_damage(skill['damage'])
            # Add potential magic power modifier later if needed
            enemy['hp'] -= damage
            slow_print(f"It hits the {enemy['name']} for {damage} damage!", 0.02)
        if skill.get('heal'):
            heal_amount = calculate_damage(skill['heal'])
            player['hp'] = min(player['max_hp'], player['hp'] + heal_amount)
            slow_print(f"You heal yourself for {heal_amount} HP.", 0.02)
        if skill.get('effect'):
            apply_status_effect(enemy, skill['effect'], skill.get('duration', 1))

    elif action in item_map: # Used an Item
        item_key = item_map[action]
        item = ITEMS[item_key]
        player['inventory'][item_key] -= 1

        slow_print(f"You used a {item['name']}.", 0.02)
        if item['effect'] == 'heal':
            player['hp'] = min(player['max_hp'], player['hp'] + item['value'])
            slow_print(f"Restored {item['value']} HP.", 0.02)
        elif item['effect'] == 'mana':
            player['mp'] = min(player['max_mp'], player['mp'] + item['value'])
            slow_print(f"Restored {item['value']} MP.", 0.02)
        elif item['effect'] == 'buff':
             # Apply or refresh buff
             player['buffs'][item['stat']] = {'value': item['value'], 'turns_left': item['duration']}
             slow_print(f"{item['description']}", 0.02)


    # Prevent HP/MP from going below zero visually
    enemy['hp'] = max(0, enemy['hp'])
    player['hp'] = max(0, player['hp'])
    player['mp'] = max(0, player['mp'])

    time.sleep(0.5) # Pause after player action


def enemy_turn(enemy):
    global player

    # Check if enemy is stunned
    if enemy.get('stunned_turns', 0) > 0:
        slow_print(f"The {enemy['name']} is stunned!", 0.02)
        enemy['stunned_turns'] -= 1
        return # Skip turn

    # Basic AI: Choose randomly from tactics
    tactic = random.choice(enemy.get('tactics', ['attack'])) # Default to basic attack

    slow_print(f"The {enemy['name']} prepares to act...", 0.02)
    time.sleep(0.5)

    if tactic == 'attack' or tactic == 'heavy_attack':
        damage_mod = 1.5 if tactic == 'heavy_attack' else 1.0
        base_damage = calculate_damage(enemy['attack'])
        damage = int(base_damage * damage_mod)
        player['hp'] -= damage
        action_verb = "attacks" if tactic == 'attack' else "performs a heavy attack"
        slow_print(f"The {enemy['name']} {action_verb} you for {damage} damage!", 0.02)
    elif tactic == 'defend':
         # Implement defense buff if desired
         slow_print(f"The {enemy['name']} takes a defensive stance.", 0.02)
         pass
    elif tactic == 'special':
        # Use specific special ability based on enemy
        if enemy.get('magic_attack'):
            damage = calculate_damage(enemy['magic_attack'])
            player['hp'] -= damage
            slow_print(f"The {enemy['name']} casts a spell, hitting you for {damage} damage!", 0.02)
        elif enemy.get('effect'):
             apply_status_effect(player, enemy['effect'], 2) # Example duration
        elif enemy.get('name') == "Goblin Chieftain": # Boss specific
            slow_print(f"The {enemy['name']} calls for help!", 0.02)
            # Add logic to potentially add a weak goblin to the fight (more complex)
            pass
        elif enemy.get('name') == "Necromancer Apprentice":
            slow_print(f"The {enemy['name']} raises a skeletal hand!", 0.02)
            # Add logic to summon skeleton
            pass
        elif enemy.get('name') == "Cave Hydra":
            slow_print(f"The {enemy['name']}'s heads strike out!", 0.02)
            # Logic for multi-attack or breath weapon
            damage = calculate_damage(enemy['attack']) + 5 # Example breath
            player['hp'] -= damage
            slow_print(f"A wave of acid breath washes over you for {damage} damage!", 0.02)
        elif enemy.get('name') == "Elemental Lord (Stone)":
             slow_print(f"The {enemy['name']} slams the ground!", 0.02)
             damage = calculate_damage(enemy['attack']) + 10
             player['hp'] -= damage
             slow_print(f"Rocks erupt, hitting you for {damage} damage!", 0.02)
        elif enemy.get('name') == "Shadow Dragon":
            sub_tactic = random.choice(["special_breath", "fear_roar", "tail_swipe"])
            if sub_tactic == "special_breath":
                slow_print(f"The {enemy['name']} unleashes shadowy breath!", 0.02)
                damage = calculate_damage(enemy['magic_attack'])
                player['hp'] -= damage
                slow_print(f"Shadow energy burns you for {damage} damage!", 0.02)
            elif sub_tactic == "fear_roar":
                 slow_print(f"The {enemy['name']} lets out a terrifying roar!", 0.02)
                 apply_status_effect(player, "stun", 1) # Example fear = stun
            elif sub_tactic == "tail_swipe":
                 slow_print(f"The {enemy['name']}'s tail sweeps across the ground!", 0.02)
                 damage = calculate_damage(enemy['attack']) - 5 # Less damage than main attack
                 player['hp'] -= damage
                 slow_print(f"You are knocked back for {damage} damage!", 0.02)
        else:
             # Default special if not defined: basic attack
             damage = calculate_damage(enemy['attack'])
             player['hp'] -= damage
             slow_print(f"The {enemy['name']} uses a special technique, hitting you for {damage} damage!", 0.02)

    # Prevent HP from going below zero visually
    player['hp'] = max(0, player['hp'])
    time.sleep(0.5) # Pause after enemy action

def start_combat(enemy_data):
    global player, fight_counter # Allow modification

    clear_screen()
    enemy = enemy_data.copy() # Fight a copy!
    slow_print(f"--- Encounter! ---", 0.02)
    slow_print(f"A wild {enemy['name']} appears!", 0.03)
    time.sleep(1)

    turn = 1
    while player['hp'] > 0 and enemy['hp'] > 0:
        clear_screen()
        slow_print(f"--- Turn {turn} ---", 0.01)

        # Player's turn
        player_turn(enemy)
        if enemy['hp'] <= 0:
            slow_print(f"\nYou have defeated the {enemy['name']}!", 0.02)
            xp_gain = enemy.get('xp', 0)
            player['xp'] += xp_gain
            slow_print(f"Gained {xp_gain} XP.", 0.02)
            # Check for level up (simple example)
            # Add proper level up logic later
            time.sleep(1.5)
            return "win"

        # Enemy's turn
        enemy_turn(enemy)
        if player['hp'] <= 0:
            clear_screen()
            slow_print(f"\nYou have been defeated by the {enemy['name']}...", 0.03)
            slow_print("--- GAME OVER ---", 0.05)
            time.sleep(2)
            return "loss"

        turn += 1
        slow_print("\nPress Enter to continue...", 0.01)
        input() # Wait for player input before next turn

    # Should not be reached if win/loss handled inside loop
    return "draw" # Should theoretically not happen in PvE

# ==================================
# MILESTONE / UPGRADE FUNCTIONS
# ==================================

def offer_milestone_reward():
    global player
    clear_screen()
    slow_print("--- Milestone Reached! ---", 0.03)
    slow_print("You feel stronger after overcoming many challenges.", 0.02)
    time.sleep(1)

    # --- Item Choice ---
    available_items = ["health_potion", "mana_potion", "whetstone"] # Example items
    slow_print("\nChoose a reward item:")
    item_options = {}
    for i, item_key in enumerate(available_items):
        item_data = ITEMS.get(item_key)
        if item_data:
            item_options[str(i + 1)] = item_key
            slow_print(f"  {i+1}. {item_data['name']} - {item_data['description']}", 0.01)

    item_choice_key = get_valid_input("Select item number: ", list(item_options.keys()))
    chosen_item = item_options[item_choice_key]
    player['inventory'][chosen_item] = player['inventory'].get(chosen_item, 0) + 1
    slow_print(f"You received a {ITEMS[chosen_item]['name']}!", 0.02)
    time.sleep(1)

    # --- Skill Upgrade Choice ---
    upgradable_skills = ["fireball", "heal_light", "shield_bash", "dragon_breath"] # Exclude basic slash
    slow_print("\nChoose a skill to enhance:")
    skill_options = {}
    for i, skill_key in enumerate(upgradable_skills):
        skill_data = player['skills'].get(skill_key)
        if skill_data:
            skill_options[str(i + 1)] = skill_key
            # Show current stats briefly
            current_stats = f" (DMG: {skill_data.get('damage','N/A')}, Cost: {skill_data['cost']}, CD: {skill_data['max_cooldown']})"
            if skill_data.get('heal'): current_stats = f" (Heal: {skill_data['heal']}, Cost: {skill_data['cost']}, CD: {skill_data['max_cooldown']})"
            slow_print(f"  {i+1}. {skill_data['name']}{current_stats}", 0.01)

    skill_choice_key = get_valid_input("Select skill number to upgrade: ", list(skill_options.keys()))
    chosen_skill = skill_options[skill_choice_key]

    # Simple Upgrade Example: Increase damage/heal slightly OR reduce cost/cooldown
    skill_to_upgrade = player['skills'][chosen_skill]
    upgrade_type = random.choice(['power', 'efficiency'])

    if upgrade_type == 'power' and skill_to_upgrade.get('damage'):
        dmg_increase = random.randint(2, 5)
        min_dmg, max_dmg = skill_to_upgrade['damage']
        skill_to_upgrade['damage'] = (min_dmg + dmg_increase, max_dmg + dmg_increase)
        slow_print(f"{skill_to_upgrade['name']} damage increased!", 0.02)
    elif upgrade_type == 'power' and skill_to_upgrade.get('heal'):
         heal_increase = random.randint(5, 10)
         min_heal, max_heal = skill_to_upgrade['heal']
         skill_to_upgrade['heal'] = (min_heal + heal_increase, max_heal + heal_increase)
         slow_print(f"{skill_to_upgrade['name']} healing increased!", 0.02)
    elif upgrade_type == 'efficiency' and skill_to_upgrade['cost'] > 5:
        cost_reduction = random.randint(2, 5)
        skill_to_upgrade['cost'] = max(5, skill_to_upgrade['cost'] - cost_reduction) # Min cost of 5
        slow_print(f"{skill_to_upgrade['name']} MP cost reduced!", 0.02)
    elif upgrade_type == 'efficiency' and skill_to_upgrade['max_cooldown'] > 1:
        skill_to_upgrade['max_cooldown'] -= 1
        slow_print(f"{skill_to_upgrade['name']} cooldown reduced!", 0.02)
    else:
         # Fallback if random choice wasn't applicable (e.g., trying to reduce cost of 0 cost skill)
         if skill_to_upgrade.get('damage'):
             dmg_increase = random.randint(2, 5)
             min_dmg, max_dmg = skill_to_upgrade['damage']
             skill_to_upgrade['damage'] = (min_dmg + dmg_increase, max_dmg + dmg_increase)
             slow_print(f"{skill_to_upgrade['name']} damage increased! (Fallback)", 0.02)
         else:
             slow_print("Minor refinement made to the skill's technique.", 0.02) # Generic message


    slow_print("\nPress Enter to continue your hunt...", 0.01)
    input()


# ==================================
# NAVIGATION & GAME FLOW FUNCTIONS
# ==================================

def display_location_info():
    location_data = LOCATIONS.get(player['current_level'], {}).get(player['current_location_id'])
    if location_data:
        clear_screen()
        slow_print(f"--- Location: {player['current_location_id'].replace('_', ' ').title()} (Level {player['current_level']}) ---", 0.02)
        slow_print(location_data['description'], 0.03)
        print("-" * (len(player['current_location_id']) + 14)) # Match title length
    else:
        slow_print("Error: Unknown location.", 0.02)

def get_monsters_for_level(level):
    return MONSTERS.get(f"level{level}", MONSTERS["level1"]) # Default to level 1 if level data missing

def get_boss_for_level(level):
     return BOSSES.get(level)


def main_game_loop():
    global player, fight_counter, current_location_id, current_level # Ensure global state access

    while player['current_level'] <= 5:
        display_location_info()
        current_map = LOCATIONS.get(player['current_level'])
        current_location_data = current_map.get(player['current_location_id'])

        if not current_location_data:
            slow_print("Error: Current location data not found. Resetting.", 0.03)
            # Handle error - maybe reset to level start?
            player['current_location_id'] = list(current_map.keys())[0] # Go to first location of level
            continue # Skip rest of loop iteration

        # --- Player Action: Move ---
        slow_print("\nWhere do you want to go?", 0.01)
        move_options = {}
        valid_moves = []
        for i, connection in enumerate(current_location_data['connections']):
             move_options[str(i+1)] = connection
             valid_moves.append(str(i+1))
             slow_print(f"  {i+1}. Go to {connection.replace('_', ' ').title()}", 0.01)

        move_choice = get_valid_input("Choose a path: ", valid_moves)
        next_location_id = move_options[move_choice]
        player['current_location_id'] = next_location_id
        next_location_data = current_map.get(next_location_id)

        if not next_location_data:
             slow_print(f"Error: Data for location '{next_location_id}' missing. Returning.", 0.03)
             player['current_location_id'] = list(current_map.keys())[0] # Go back to start of level
             continue

        # --- Trigger Event (Fight/Boss) ---
        event = next_location_data['event']
        combat_result = "win" # Assume win if no fight

        if event == "fight":
            if player['fights_this_level'] < 10:
                enemy_list = get_monsters_for_level(player['current_level'])
                enemy_to_fight = random.choice(enemy_list)
                combat_result = start_combat(enemy_to_fight)
                if combat_result == "win":
                    player['fights_this_level'] += 1
                    # Check for milestone every 10 fights (except after boss)
                    if player['fights_this_level'] > 0 and player['fights_this_level'] % 10 == 0:
                       offer_milestone_reward()

            else:
                 slow_print("The area seems clear for now...", 0.02) # Already fought 10 monsters
                 time.sleep(1)

        elif event == "boss":
            if player['fights_this_level'] >= 10: # Only fight boss after 10 normal fights
                 boss_data = get_boss_for_level(player['current_level'])
                 if boss_data:
                     slow_print(f"\nYou sense a powerful presence... The {boss_data['name']} blocks your path!", 0.03)
                     time.sleep(1.5)
                     combat_result = start_combat(boss_data)
                     if combat_result == "win":
                         slow_print(f"\n--- LEVEL {player['current_level']} CLEARED! ---", 0.04)
                         # --- Level Up & Transition ---
                         player['current_level'] += 1
                         player['fights_this_level'] = 0 # Reset fight counter
                         # Basic stat increase on level up
                         player['max_hp'] += 15
                         player['max_mp'] += 10
                         player['base_attack'] += 2
                         player['hp'] = player['max_hp'] # Full heal on level up
                         player['mp'] = player['max_mp']
                         slow_print(f"You reached Level {player['current_level']}!", 0.02)
                         display_player_status() # Show new stats
                         time.sleep(2)

                         if player['current_level'] > 5:
                              # Final Victory
                              clear_screen()
                              slow_print("*************************************", 0.05)
                              slow_print("* CONGRATULATIONS, MASTER HUNTER! *", 0.05)
                              slow_print("*************************************", 0.05)
                              slow_print("\nYou have vanquished the Shadow Dragon and cleared all the dungeons.", 0.03)
                              slow_print("Your legend will echo through the ages!", 0.03)
                              break # Exit the main game loop
                         else:
                             # Find the starting location for the *next* level
                             next_level_map = LOCATIONS.get(player['current_level'])
                             if next_level_map:
                                 player['current_location_id'] = list(next_level_map.keys())[0] # Go to first location of next level
                                 slow_print(f"\nYou proceed to Level {player['current_level']}...", 0.03)
                                 time.sleep(1.5)
                             else:
                                  slow_print("Error: Cannot find data for the next level. Game ends.", 0.03)
                                  break # Exit loop if next level data missing
                 else:
                     slow_print("Error: Boss data missing for this level.", 0.03)
                     # Decide how to handle this - maybe let player pass? For now, stops progress.
                     break

            else:
                 slow_print("You sense a powerful presence, but you must clear the area first.", 0.02)
                 # Force player back? Or just let them explore other paths?
                 # For simplicity, let's send them back to the previous location
                 player['current_location_id'] = current_location_data['connections'][0] # Assumes first connection is 'back'
                 slow_print("You retreat for now.", 0.02)
                 time.sleep(1.5)


        # Check for game over after combat
        if combat_result == "loss":
            break # Exit the main game loop

    # --- End of Game ---
    if player['hp'] > 0 and player['current_level'] <= 5: # If loop exited without winning/losing (e.g., error)
        slow_print("\nYour journey ends unexpectedly.", 0.03)
    elif player['hp'] <= 0:
         slow_print("\nPerhaps another hunter will succeed where you failed.", 0.03)

    slow_print("\nPress Enter to exit the game.", 0.02)
    input()


# ==================================
# START THE GAME
# ==================================
if __name__ == "__main__":
    clear_screen()
    slow_print("Welcome, Monster Hunter!", 0.04)
    slow_print("Dark dungeons await. Prepare yourself.", 0.03)
    time.sleep(1.5)
    main_game_loop()