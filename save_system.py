"""
save_system.py - Persistent JSON save and load system.
"""
import os
import json
from pokemon import Pokemon
from inventory import Inventory

SAVE_FILE_PATH = os.path.join(os.path.dirname(__file__), "save_data.json")

class Pokedex:
    def __init__(self, seen=None, caught=None):
        self.seen = set(seen) if seen else set()
        self.caught = set(caught) if caught else set()

    def register_seen(self, species_name):
        self.seen.add(species_name)

    def register_caught(self, species_name):
        self.seen.add(species_name)
        self.caught.add(species_name)

    def to_dict(self):
        return {
            "seen": list(self.seen),
            "caught": list(self.caught)
        }

    @classmethod
    def from_dict(cls, data):
        return cls(seen=data.get("seen", []), caught=data.get("caught", []))

class SaveSystem:
    @staticmethod
    def save_game(player, party, inventory, pokedex, world):
        data = {
            "player": {
                "grid_x": player.grid_x,
                "grid_y": player.grid_y,
                "map": player.current_map,
                "facing": player.facing
            },
            "party": [p.to_dict() for p in party],
            "inventory": inventory.to_dict(),
            "pokedex": pokedex.to_dict(),
            "defeated_trainers": list(world.defeated_trainers)
        }
        try:
            with open(SAVE_FILE_PATH, "w") as f:
                json.dump(data, f, indent=2)
            return True, "Game successfully saved!"
        except Exception as e:
            return False, f"Failed to save game: {e}"

    @staticmethod
    def load_game(player, world):
        if not os.path.exists(SAVE_FILE_PATH):
            return None, "No save file found."
            
        try:
            with open(SAVE_FILE_PATH, "r") as f:
                data = json.load(f)
                
            p_data = data["player"]
            player.grid_x = p_data.get("grid_x", 8)
            player.grid_y = p_data.get("grid_y", 6)
            player.current_map = p_data.get("map", "Pallet Town")
            player.facing = p_data.get("facing", 0)
            player.pixel_x = player.grid_x * 32
            player.pixel_y = player.grid_y * 32
            
            party = [Pokemon.from_dict(pd) for pd in data.get("party", [])]
            inventory = Inventory.from_dict(data.get("inventory", {}))
            pokedex = Pokedex.from_dict(data.get("pokedex", {}))
            world.defeated_trainers = set(data.get("defeated_trainers", []))
            
            return (party, inventory, pokedex), "Game loaded successfully!"
        except Exception as e:
            return None, f"Error loading save file: {e}"

    @staticmethod
    def has_save():
        return os.path.exists(SAVE_FILE_PATH)

    @staticmethod
    def get_save_summary():
        if not os.path.exists(SAVE_FILE_PATH):
            return None
        try:
            with open(SAVE_FILE_PATH, "r") as f:
                data = json.load(f)
            p_data = data.get("player", {})
            party_data = data.get("party", [])
            inv_data = data.get("inventory", {})
            pdx_data = data.get("pokedex", {})
            
            lead_name = party_data[0]["nickname"] if party_data else "None"
            lead_species = party_data[0]["species"] if party_data else "Pikachu"
            lead_lvl = party_data[0].get("level", 5) if party_data else 5
            
            return {
                "map": p_data.get("map", "Pallet Town"),
                "party_count": len(party_data),
                "lead_name": lead_name,
                "lead_species": lead_species,
                "lead_level": lead_lvl,
                "money": inv_data.get("money", 3000),
                "seen_count": len(pdx_data.get("seen", [])),
                "caught_count": len(pdx_data.get("caught", []))
            }
        except Exception:
            return None
