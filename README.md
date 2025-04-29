# Python RPG Terminal Monster Hunter

A text-based, turn-based Role-Playing Game played entirely within the terminal. Explore dungeon levels, battle monsters and bosses, gain experience, and upgrade your hunter!

## Features

*   **Turn-Based Combat:** Engage in tactical battles against various monsters.
*   **Dungeon Crawling:** Navigate through connected locations within distinct dungeon levels (5 levels included).
*   **Monster Variety:** Encounter different monsters with unique stats and simple combat tactics on each level.
*   **Level Bosses:** Face a challenging boss at the end of each level after defeating enough regular monsters.
*   **Player Progression:** Gain Experience Points (XP) from defeating monsters. (Basic level-up implemented with stat increases).
*   **Skill System:** Utilize basic attacks and special skills (Fireball, Heal, Shield Bash) with MP costs and cooldown timers. Includes an Ultimate skill (Dragon Breath).
*   **Item System:** Use basic Health and Mana Potions found in your inventory.
*   **Milestone Rewards:** After defeating 10 monsters on a level, choose an item reward and a skill upgrade.
*   **Retro Text-Based HUD:** A persistent status bar at the bottom displays HP, MP, Level, Cooldowns, and Buffs in a classic 8-bit style.
*   **Final Boss:** A challenging multi-tactic Shadow Dragon awaits at the end of Level 5.

## Technologies Used

*   Python 3

## Setup and Installation

1.  **Ensure Python 3 is installed** on your system.
2.  Clone the repository:
    ```bash
    git clone [Your GitHub Repository Link]
    ```
3.  Navigate into the project directory:
    ```bash
    cd python-rpg-terminal # Or your actual folder name
    ```
4.  Run the game from your terminal:
    ```bash
    python game.py # IMPORTANT: Replace 'game.py' with the actual name of your Python script file!
    ```

## How to Play

1.  Run the script using Python.
2.  Follow the text prompts displayed in the terminal.
3.  **Exploration:** When in a location, you'll be presented with numbered paths to connected locations. Enter the number corresponding to the path you wish to take.
4.  **Combat:** When combat starts, a HUD will appear at the bottom.
    *   You'll be prompted to choose an action (e.g., 'a' for basic attack, '1' for Fireball, '5' for Health Potion).
    *   Enter the corresponding letter or number.
    *   Skills cost MP and have cooldowns, indicated in the HUD.
    *   Items are consumed on use.
    *   Defeat the enemy before your HP reaches zero!
5.  **Progression:** Defeat 10 regular monsters on a level to unlock the path to the boss and receive a milestone reward (item + skill upgrade). Defeat the boss to progress to the next level.
6.  Defeat the final boss on Level 5 to win the game.

## Future Improvements (Optional)

*   Implement saving and loading game progress.
*   Add more complex monster AI and tactics.
*   Expand the skill tree and add more diverse skills.
*   Introduce equipment (weapons, armor) and stats (strength, defense, magic power).
*   Flesh out status effects (poison, burn, etc.).
*   Add more detailed level-up choices.
*   Implement shops or merchants.
