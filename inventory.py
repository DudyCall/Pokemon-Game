"""
inventory.py - Player inventory and bag management.
"""
from pokemon_data import ITEMS, POKEMON_SPECIES, STONE_EVOLUTIONS

class Inventory:
    def __init__(self):
        self.money = 3000
        # Default starting items
        self.items = {
            "Poke Ball": 10,
            "Potion": 5,
            "Antidote": 2,
            "Revive": 1
        }

    def add_money(self, amount):
        self.money = max(0, self.money + amount)
        return self.money

    def remove_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def add_item(self, item_name, count=1):
        if item_name in ITEMS:
            self.items[item_name] = self.items.get(item_name, 0) + count
            return True
        return False

    def remove_item(self, item_name, count=1):
        if item_name in self.items and self.items[item_name] >= count:
            self.items[item_name] -= count
            if self.items[item_name] <= 0:
                del self.items[item_name]
            return True
        return False

    def get_count(self, item_name):
        return self.items.get(item_name, 0)

    def get_items_list(self, category_filter=None):
        """Returns list of (name, count, item_data) for non-zero items, optionally filtered by category."""
        res = []
        for name, count in self.items.items():
            if count > 0 and name in ITEMS:
                item_data = ITEMS[name]
                if category_filter is None or category_filter == "ALL" or item_data.get("category") == category_filter:
                    res.append((name, count, item_data))
        return res

    def use_item_on_pokemon(self, item_name, pokemon, quest_mgr=None):
        """
        Uses an item on a given Pokemon object.
        Returns (success: bool, message: str)
        """
        if self.get_count(item_name) <= 0:
            return False, "You don't have any of that item!"

        data = ITEMS.get(item_name)
        if not data:
            return False, "Unknown item."

        # Revive
        if "revive_hp_percent" in data:
            if not pokemon.is_fainted():
                return False, f"{pokemon.nickname} is not fainted!"
            revive_amount = max(1, int(pokemon.max_hp * (data["revive_hp_percent"] / 100.0)))
            pokemon.current_hp = revive_amount
            pokemon.status = None
            self.remove_item(item_name, 1)
            return True, f"{pokemon.nickname} was revived with {revive_amount} HP!"

        # Healing Items (Potion, Super Potion, Max Potion)
        if "heal_hp" in data:
            if pokemon.is_fainted():
                return False, f"{pokemon.nickname} is fainted!"
            if pokemon.current_hp >= pokemon.max_hp:
                return False, f"{pokemon.nickname}'s HP is already full!"
            healed = pokemon.heal(data["heal_hp"])
            self.remove_item(item_name, 1)
            return True, f"{pokemon.nickname} recovered {healed} HP!"

        # Status Cures (Antidote, Paralyze Heal, Awakening, Burn Heal)
        if "cure_status" in data:
            if pokemon.status != data["cure_status"]:
                return False, f"{pokemon.nickname} is not afflicted with {data['cure_status']}!"
            pokemon.cure_status()
            self.remove_item(item_name, 1)
            return True, f"{pokemon.nickname}'s {data['cure_status']} was cured!"

        # Rare Candy
        if "level_up" in data:
            if pokemon.level >= 100:
                return False, f"{pokemon.nickname} is already at level 100!"
            exp_needed = pokemon.exp_for_next_level() - pokemon.exp
            events = pokemon.gain_exp(exp_needed)
            self.remove_item(item_name, 1)
            return True, f"{pokemon.nickname} grew to Level {pokemon.level}!"

        # Evolution Stones (Moon Stone, Fire Stone, Water Stone, Thunder Stone, Leaf Stone)
        if "stone_type" in data:
            stone_type = data["stone_type"]
            target_species = STONE_EVOLUTIONS.get(stone_type, {}).get(pokemon.species)
            if not target_species or target_species not in POKEMON_SPECIES:
                return False, f"{pokemon.nickname} isn't affected by {item_name}!"
            old_species = pokemon.species
            pokemon.species = target_species
            pokemon.species_data = POKEMON_SPECIES[target_species]
            pokemon.types = list(pokemon.species_data["types"])
            pokemon.recalculate_stats()
            self.remove_item(item_name, 1)
            if quest_mgr is not None:
                quest_mgr.on_item_used(item_name, pokemon, self)
            return True, f"What?! {pokemon.nickname} evolved into {target_species}!"

        # Move Reroll Disk
        if data.get("is_move_reroll"):
            ok, new_m, old_m, msg = pokemon.reroll_move()
            if ok:
                self.remove_item(item_name, 1)
                return True, msg
            return False, msg

        return False, "This item cannot be used this way."

    def to_dict(self):
        return {
            "money": self.money,
            "items": dict(self.items)
        }

    @classmethod
    def from_dict(cls, data):
        inv = cls()
        inv.money = data.get("money", 3000)
        inv.items = data.get("items", {})
        return inv
