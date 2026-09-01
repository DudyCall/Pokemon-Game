"""
save_system.py - Persistent Multi-Slot JSON Save & Load System.
Supports multiple save slots with rich metadata, timestamps, and legacy save migration.
"""
import os
import json
import datetime
from pokemon import Pokemon
from inventory import Inventory

BASE_DIR = os.path.dirname(__file__)
SAVES_DIR = os.path.join(BASE_DIR, "saves")
LEGACY_SAVE_FILE = os.path.join(BASE_DIR, "save_data.json")
NUM_SAVE_SLOTS = 3

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
    _active_slot = 1
    _saves_dir = SAVES_DIR

    @classmethod
    def set_saves_dir(cls, dir_path):
        cls._saves_dir = dir_path
        os.makedirs(cls._saves_dir, exist_ok=True)

    @classmethod
    def reset_saves_dir(cls):
        cls._saves_dir = SAVES_DIR

    @classmethod
    def _ensure_saves_dir(cls):
        os.makedirs(cls._saves_dir, exist_ok=True)
        # Check and migrate legacy single save file to Slot 1 if needed
        slot1_path = cls.get_slot_path(1)
        if os.path.exists(LEGACY_SAVE_FILE) and not os.path.exists(slot1_path):
            try:
                with open(LEGACY_SAVE_FILE, "r", encoding="utf-8") as src:
                    data = json.load(src)
                data["slot"] = 1
                data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                with open(slot1_path, "w", encoding="utf-8") as dst:
                    json.dump(data, dst, indent=2)
            except Exception:
                pass

    @classmethod
    def get_slot_path(cls, slot=1):
        slot_num = max(1, min(NUM_SAVE_SLOTS, int(slot)))
        return os.path.join(cls._saves_dir, f"slot_{slot_num}.json")

    @classmethod
    def set_active_slot(cls, slot):
        cls._active_slot = max(1, min(NUM_SAVE_SLOTS, int(slot)))

    @classmethod
    def get_active_slot(cls):
        return cls._active_slot

    @classmethod
    def save_game(cls, player, party, inventory, pokedex, world, slot=None, pc_box=None, quest_mgr=None):
        cls._ensure_saves_dir()
        target_slot = slot if slot is not None else cls._active_slot
        target_slot = max(1, min(NUM_SAVE_SLOTS, int(target_slot)))
        cls._active_slot = target_slot

        defeated = list(getattr(world, "defeated_trainers", [])) if world is not None else []
        collected = list(getattr(world, "collected_items", [])) if world is not None else []
        badges = list(getattr(world, "badges", [])) if world is not None else []
        unlocked_barriers = list(getattr(world, "unlocked_barriers", [])) if world is not None else []
        explored = {k: [list(pt) for pt in v] for k, v in getattr(world, "explored_tiles", {}).items()} if world is not None else {}
        quests_data = quest_mgr.to_dict() if quest_mgr is not None else {}
        data = {
            "slot": target_slot,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "player": {
                "name": getattr(player, "name", "Red"),
                "gender": getattr(player, "gender", "Boy"),
                "outfit_theme": getattr(player, "outfit_theme", "Classic Red"),
                "hat_style": getattr(player, "hat_style", "Trainer Cap"),
                "hair_color": getattr(player, "hair_color", "Dark Brown"),
                "grid_x": player.grid_x,
                "grid_y": player.grid_y,
                "map": player.current_map,
                "facing": player.facing,
                "has_boat": getattr(player, "has_boat", True),
                "is_sailing": getattr(player, "is_sailing", False)
            },
            "party": [p.to_dict() for p in party],
            "pc_box": [p.to_dict() for p in (pc_box or [])],
            "inventory": inventory.to_dict(),
            "pokedex": pokedex.to_dict(),
            "defeated_trainers": defeated,
            "collected_items": collected,
            "badges": badges,
            "unlocked_barriers": unlocked_barriers,
            "explored_tiles": explored,
            "quests": quests_data
        }
        try:
            slot_path = cls.get_slot_path(target_slot)
            with open(slot_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            # Also keep legacy save file updated if slot 1
            if target_slot == 1:
                try:
                    with open(LEGACY_SAVE_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                except Exception:
                    pass
            return True, f"Game successfully saved to Slot {target_slot}!"
        except Exception as e:
            return False, f"Failed to save game to Slot {target_slot}: {e}"

    @classmethod
    def load_game(cls, player, world=None, slot=None):
        cls._ensure_saves_dir()
        target_slot = slot if slot is not None else cls._active_slot
        target_slot = max(1, min(NUM_SAVE_SLOTS, int(target_slot)))
        slot_path = cls.get_slot_path(target_slot)

        if not os.path.exists(slot_path):
            # Fallback to legacy file if loading slot 1 and slot 1 file not yet created
            if target_slot == 1 and os.path.exists(LEGACY_SAVE_FILE):
                slot_path = LEGACY_SAVE_FILE
            else:
                return None, f"No save data found in Slot {target_slot}."

        try:
            with open(slot_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            p_data = data["player"]
            player.name = p_data.get("name", "Red")
            player.gender = p_data.get("gender", "Boy")
            player.outfit_theme = p_data.get("outfit_theme", "Classic Red")
            player.hat_style = p_data.get("hat_style", "Trainer Cap")
            player.hair_color = p_data.get("hair_color", "Dark Brown")
            player.grid_x = p_data.get("grid_x", 8)
            player.grid_y = p_data.get("grid_y", 6)
            player.current_map = p_data.get("map", "Pallet Town")
            player.facing = p_data.get("facing", 0)
            player.pixel_x = player.grid_x * 32
            player.pixel_y = player.grid_y * 32
            player.has_boat = p_data.get("has_boat", True)
            if world is not None:
                tile = world.get_tile(player.current_map, player.grid_x, player.grid_y)
                player.is_sailing = (tile == '~')
            else:
                player.is_sailing = p_data.get("is_sailing", False)

            from graphics_manager import gfx
            gfx.set_custom_player_appearance(player.gender, player.outfit_theme, player.hat_style, player.hair_color)

            party = [Pokemon.from_dict(pd) for pd in data.get("party", [])]
            pc_box = [Pokemon.from_dict(pd) for pd in data.get("pc_box", [])]
            inventory = Inventory.from_dict(data.get("inventory", {}))
            pokedex = Pokedex.from_dict(data.get("pokedex", {}))
            quests_data = data.get("quests", {})
            if world is not None:
                world.defeated_trainers = set(data.get("defeated_trainers", []))
                world.collected_items = set(data.get("collected_items", []))
                world.badges = set(data.get("badges", []))
                world.unlocked_barriers = set(data.get("unlocked_barriers", []))
                raw_exp = data.get("explored_tiles", {})
                world.explored_tiles = {k: set(tuple(pt) for pt in v) for k, v in raw_exp.items()}
                world.reveal_area(player.current_map, player.grid_x, player.grid_y)

            # Auto-recovery: If Pikachu is in caught Pokédex but not in party or PC box, restore Pikachu to PC box!
            all_species = [p.species for p in party] + [p.species for p in pc_box]
            if "Pikachu" in pokedex.caught and "Pikachu" not in all_species:
                pc_box.append(Pokemon("Pikachu", level=10))

            cls._active_slot = target_slot
            return (party, inventory, pokedex, pc_box, quests_data), f"Slot {target_slot} loaded successfully!"
        except Exception as e:
            return None, f"Error loading Slot {target_slot}: {e}"

    @classmethod
    def delete_slot(cls, slot):
        cls._ensure_saves_dir()
        slot_path = cls.get_slot_path(slot)
        if os.path.exists(slot_path):
            try:
                os.remove(slot_path)
                return True
            except Exception:
                return False
        return False

    @classmethod
    def has_save(cls, slot=None):
        cls._ensure_saves_dir()
        if slot is not None:
            target_slot = max(1, min(NUM_SAVE_SLOTS, int(slot)))
            slot_path = cls.get_slot_path(target_slot)
            return os.path.exists(slot_path) or (target_slot == 1 and os.path.exists(LEGACY_SAVE_FILE))
        # Any save exists
        for s in range(1, NUM_SAVE_SLOTS + 1):
            if os.path.exists(cls.get_slot_path(s)):
                return True
        return os.path.exists(LEGACY_SAVE_FILE)

    @classmethod
    def get_slot_summary(cls, slot=1):
        cls._ensure_saves_dir()
        target_slot = max(1, min(NUM_SAVE_SLOTS, int(slot)))
        slot_path = cls.get_slot_path(target_slot)

        if not os.path.exists(slot_path):
            if target_slot == 1 and os.path.exists(LEGACY_SAVE_FILE):
                slot_path = LEGACY_SAVE_FILE
            else:
                return None

        try:
            with open(slot_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            p_data = data.get("player", {})
            party_data = data.get("party", [])
            inv_data = data.get("inventory", {})
            pdx_data = data.get("pokedex", {})

            lead_name = party_data[0]["nickname"] if party_data else "None"
            lead_species = party_data[0]["species"] if party_data else "Pikachu"
            lead_lvl = party_data[0].get("level", 5) if party_data else 5

            return {
                "slot": target_slot,
                "exists": True,
                "trainer_name": p_data.get("name", "Red"),
                "gender": p_data.get("gender", "Boy"),
                "outfit_theme": p_data.get("outfit_theme", "Classic Red"),
                "hat_style": p_data.get("hat_style", "Trainer Cap"),
                "hair_color": p_data.get("hair_color", "Dark Brown"),
                "timestamp": data.get("timestamp", "Unknown Date"),
                "map": p_data.get("map", "Pallet Town"),
                "party_count": len(party_data),
                "pc_count": len(data.get("pc_box", [])),
                "lead_name": lead_name,
                "lead_species": lead_species,
                "lead_level": lead_lvl,
                "money": inv_data.get("money", 3000),
                "seen_count": len(pdx_data.get("seen", [])),
                "caught_count": len(pdx_data.get("caught", []))
            }
        except Exception:
            return None

    @classmethod
    def get_save_summary(cls):
        """Returns summary of active slot (or slot 1) for backward compatibility."""
        return cls.get_slot_summary(cls._active_slot) or cls.get_slot_summary(1)

    @classmethod
    def get_all_slots_summary(cls):
        cls._ensure_saves_dir()
        summaries = []
        for s in range(1, NUM_SAVE_SLOTS + 1):
            summary = cls.get_slot_summary(s)
            if summary is None:
                summaries.append({
                    "slot": s,
                    "exists": False,
                    "timestamp": "",
                    "map": "",
                    "party_count": 0,
                    "lead_name": "",
                    "lead_species": "Pikachu",
                    "lead_level": 0,
                    "money": 0,
                    "seen_count": 0,
                    "caught_count": 0
                })
            else:
                summaries.append(summary)
        return summaries
