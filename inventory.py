"""
inventory.py - Player inventory and bag management.
"""
from pokemon_data import ITEMS

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

    def add_item(self, item_name, count=1):
        if item_name in ITEMS:
            self.items[item_name] = self.items.get(item_name, 0) + count
            return True
        return False

    def remove_item(self, item_name, count=1):
        if self.items.get(item_name, 0) >= count:
            self.items[item_name] -= count
            if self.items[item_name] <= 0:
                del self.items[item_name]
            return True
        return False

    def get_count(self, item_name):
        return self.items.get(item_name, 0)

    def get_items_list(self, category_filter=None):
        """Returns list of (item_name, count, item_data)"""
        result = []
        for name, count in self.items.items():
            data = ITEMS.get(name, {})
            if category_filter is None or data.get("category") == category_filter:
                result.append((name, count, data))
        return result

    def use_item_on_pokemon(self, item_name, pokemon):
        """Applies item effect to a target Pokemon. Returns (success, message)"""
        if item_name not in self.items or self.items[item_name] <= 0:
            return False, "You don't have any left!"
            
        data = ITEMS.get(item_name)
        if not data:
            return False, "Unknown item."
            
        # Revive
        if "revive_hp_percent" in data:
            if not pokemon.is_fainted():
                return False, f"{pokemon.nickname} doesn't need to be revived!"
            revive_amount = max(1, int(pokemon.max_hp * (data["revive_hp_percent"] / 100)))
            pokemon.current_hp = revive_amount
            pokemon.cure_status()
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

        # Status Cures
        if "cure_status" in data:
            if pokemon.status != data["cure_status"]:
                return False, f"{pokemon.nickname} is not {data['cure_status'].lower()}ed!"
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
