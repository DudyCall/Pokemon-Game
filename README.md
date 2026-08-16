# Pokémon - Pygame Edition

An authentic, rich, turn-based Pokémon RPG built with Pygame-CE.

## Features

- **Starter Pokémon Selection**: Choose from Charmander (Fire), Squirtle (Water), Bulbasaur (Grass), or Pikachu (Electric).
- **Overworld Exploration**:
  - Pallet Town (Starter Village & Home)
  - Route 1 (Tall Grass Wild Encounters & Trainer Battles)
  - Viridian City (Pokémon Center with Nurse Joy healing, PokéMart shopping)
  - Viridian Forest / Route 2 (Challenging Wild Pokémon and Leader Brock)
- **Turn-Based Battle System**:
  - `FIGHT`: Choose from 4 unique moves with Type, Power, Accuracy, and PP.
  - `BAG`: Use Poké Balls (Poké Ball, Great Ball, Ultra Ball) to catch wild Pokémon, or use Potions and Revives.
  - `POKÉMON`: Switch active Pokémon or manage team status.
  - `RUN`: Escape from wild battles based on speed stats.
  - Full Type Matchup matrix (Super effective / Not very effective / STAB bonuses).
  - Critical hits and secondary status effects (Burn, Paralysis, Sleep, Poison).
  - Authentic 3-shake Pokéball capture animation.
  - Animated HP and EXP growth bars.
  - Level-Up stat distribution modal and evolution system (e.g. Charmander -> Charmeleon -> Charizard).
- **Pokédex & Party Management**:
  - Track seen and caught Pokémon with lore entries, types, and stats.
  - Party summary with HP bars and type badges.
- **Audio & Visuals**:
  - Built-in procedural 8-bit chiptune sound effects and background music (Town, Battle, Victory).
  - Auto-cached official Pokémon sprites from PokeAPI (with offline procedural pixel-art fallbacks).
  - Animated 4-directional trainer walking cycles, grass rustling, and water ripple animations.
- **Persistent Save System**:
  - Save game progress anytime via the Start Menu (`save_data.json`).

## Controls

| Action | Primary Key | Alternate Key |
|---|---|---|
| **Move / Navigate** | Arrow Keys | `W`, `A`, `S`, `D` |
| **Confirm / Talk / Attack** | `Z` | `Enter` / `Space` |
| **Cancel / Back / Run** | `X` | `Escape` / `Backspace` |
| **Open Menu (Pause / Bag / Pokédex)** | `C` | `Tab` / `M` |

## How to Play

1. Run the game from the terminal:
   ```bash
   python main.py
   ```
2. Press `Enter` or `Z` at the title screen to begin your adventure.
3. Choose your starter Pokémon and explore Pallet Town, Route 1, and Viridian City!
