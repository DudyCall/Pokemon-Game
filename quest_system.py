"""
quest_system.py - Quest Engine, Quest Givers, Auto-Tracking, and Instant Reward Distribution.
Supports diverse quest types (catching specific species/types, defeating types/trainers, using items)
with automatic completion on the spot and immediate reward delivery.
"""
import datetime
from pokemon_data import POKEMON_SPECIES

QUEST_DEFINITIONS = {
    "oak_bug_hunt": {
        "id": "oak_bug_hunt",
        "title": "Bug Researcher's Survey",
        "giver_name": "Prof. Oak's Aide",
        "location": "Pallet Town & Viridian Forest",
        "objective_type": "CATCH_TYPE",
        "target_criteria": ["Bug"],
        "target_count": 3,
        "description": "Prof. Oak needs field data on wild forest insects. Catch 3 Bug-type Pokémon!",
        "rewards": {
            "money": 1000,
            "items": [("Great Ball", 5), ("Rare Candy", 1)]
        }
    },
    "bird_watcher_avian": {
        "id": "bird_watcher_avian",
        "title": "Skies of Kanto",
        "giver_name": "Bird Watcher",
        "location": "Route 1",
        "objective_type": "DEFEAT_TYPE",
        "target_criteria": ["Flying"],
        "target_count": 3,
        "description": "Test your battle skills against airborne opponents! Defeat 3 Flying-type Pokémon in battle.",
        "rewards": {
            "money": 1200,
            "items": [("Super Potion", 3), ("Rare Candy", 1)]
        }
    },
    "sparky_electric_charge": {
        "id": "sparky_electric_charge",
        "title": "High Voltage Research",
        "giver_name": "Electrician Sparky",
        "location": "Vermilion City",
        "objective_type": "CATCH_SPECIES",
        "target_criteria": ["Pikachu", "Voltorb", "Magnemite", "Electabuzz"],
        "target_count": 1,
        "description": "The Vermilion power grid needs energy samples. Catch a Pikachu, Voltorb, Magnemite, or Electabuzz!",
        "rewards": {
            "money": 2000,
            "items": [("Thunder Stone", 1), ("Ultra Ball", 3)]
        }
    },
    "fossil_moon_mystery": {
        "id": "fossil_moon_mystery",
        "title": "Mysteries of Mt. Moon",
        "giver_name": "Fossil Maniac",
        "location": "Pewter City & Mt. Moon",
        "objective_type": "CATCH_SPECIES",
        "target_criteria": ["Clefairy", "Geodude", "Onix", "Paras", "Zubat"],
        "target_count": 2,
        "description": "Uncover ancient cavern secrets! Catch 2 mountain Pokémon (Clefairy, Geodude, Onix, Paras, or Zubat).",
        "rewards": {
            "money": 2500,
            "items": [("Moon Stone", 1), ("Nugget", 1)]
        }
    },
    "karate_spirit": {
        "id": "karate_spirit",
        "title": "Way of the Martial Artist",
        "giver_name": "Black Belt Kenji",
        "location": "Saffron City Fighting Dojo",
        "objective_type": "DEFEAT_TYPE",
        "target_criteria": ["Fighting", "Rock"],
        "target_count": 4,
        "description": "Hone your fighting spirit! Defeat 4 Fighting or Rock-type Pokémon in battle.",
        "rewards": {
            "money": 3000,
            "items": [("Move Reroll Disk", 1), ("Max Potion", 2)]
        }
    },
    "celadon_evolution_mastery": {
        "id": "celadon_evolution_mastery",
        "title": "Elemental Evolution Catalyst",
        "giver_name": "Stone Connoisseur",
        "location": "Celadon Department Store",
        "objective_type": "USE_EVOLUTION_STONE",
        "target_criteria": ["Moon Stone", "Fire Stone", "Water Stone", "Thunder Stone", "Leaf Stone"],
        "target_count": 1,
        "description": "Harness the power of elemental stones! Evolve any Pokémon using an Evolution Stone.",
        "rewards": {
            "money": 3500,
            "items": [("Rare Candy", 3), ("Nugget", 1)]
        }
    },
    "ninja_toxic_challenge": {
        "id": "ninja_toxic_challenge",
        "title": "Shadows & Toxic Mists",
        "giver_name": "Ninja Scout",
        "location": "Fuchsia City",
        "objective_type": "DEFEAT_TYPE",
        "target_criteria": ["Poison"],
        "target_count": 4,
        "description": "Master the art of surviving poisonous strikes! Defeat 4 Poison-type Pokémon in battle.",
        "rewards": {
            "money": 4000,
            "items": [("Max Revive", 2), ("Ultra Ball", 5)]
        }
    },
    "safari_wildlife_reserve": {
        "id": "safari_wildlife_reserve",
        "title": "Savanna Rare Species Hunt",
        "giver_name": "Safari Ranger",
        "location": "Safari Zone Sanctuary",
        "objective_type": "CATCH_SPECIES",
        "target_criteria": ["Dratini", "Dragonair", "Kangaskhan", "Tauros", "Scyther", "Pinsir", "Chansey"],
        "target_count": 1,
        "description": "Spot and capture a rare apex Pokémon roaming the golden savanna wildlife reserve!",
        "rewards": {
            "money": 5000,
            "items": [("Master Ball", 1), ("Rare Candy", 2)]
        }
    },
    "sea_fisherman_harvest": {
        "id": "sea_fisherman_harvest",
        "title": "Ocean Tides Harvest",
        "giver_name": "Old Fisherman Barny",
        "location": "Vermilion Port & Route 21",
        "objective_type": "CATCH_TYPE",
        "target_criteria": ["Water"],
        "target_count": 3,
        "description": "The ocean currents bring bountiful sea creatures! Catch 3 Water-type Pokémon.",
        "rewards": {
            "money": 2200,
            "items": [("Water Stone", 1), ("Great Ball", 4)]
        }
    },
    "champion_road_trial": {
        "id": "champion_road_trial",
        "title": "Trial of the Indigo Champions",
        "giver_name": "Veteran Ace Trainer",
        "location": "Route 22 & Victory Road",
        "objective_type": "DEFEAT_TRAINERS",
        "target_criteria": [],
        "target_count": 5,
        "description": "Prove you have what it takes to challenge the Indigo Plateau! Defeat 5 Trainer opponents in battle.",
        "rewards": {
            "money": 6000,
            "items": [("Rare Candy", 5), ("Nugget", 2)]
        }
    }
}

class QuestManager:
    def __init__(self):
        self.active_quests = {}    # {quest_id: {"progress": int}}
        self.completed_quests = {} # {quest_id: {"completed_at": str}}
        self.pending_notifications = []

    def is_active(self, quest_id):
        return quest_id in self.active_quests

    def is_completed(self, quest_id):
        return quest_id in self.completed_quests

    def get_progress(self, quest_id):
        if quest_id in self.completed_quests:
            q = QUEST_DEFINITIONS.get(quest_id, {})
            return q.get("target_count", 1)
        if quest_id in self.active_quests:
            return self.active_quests[quest_id].get("progress", 0)
        return 0

    def get_target_count(self, quest_id):
        q = QUEST_DEFINITIONS.get(quest_id, {})
        return q.get("target_count", 1)

    def accept_quest(self, quest_id):
        if quest_id not in QUEST_DEFINITIONS:
            return False, "Quest does not exist."
        if self.is_completed(quest_id):
            return False, "Quest already completed."
        if self.is_active(quest_id):
            return False, "Quest already active."

        self.active_quests[quest_id] = {"progress": 0}
        q_data = QUEST_DEFINITIONS[quest_id]
        return True, f"Quest Accepted: {q_data['title']}!"

    def _complete_quest(self, quest_id, inventory):
        if quest_id not in self.active_quests:
            return None

        del self.active_quests[quest_id]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.completed_quests[quest_id] = {"completed_at": timestamp}

        q_data = QUEST_DEFINITIONS.get(quest_id, {})
        rewards = q_data.get("rewards", {})
        reward_strs = []

        # Deliver Money
        money = rewards.get("money", 0)
        if money > 0 and inventory is not None:
            inventory.add_money(money)
            reward_strs.append(f"+${money} Coins")

        # Deliver Items
        for item_name, count in rewards.get("items", []):
            if inventory is not None:
                inventory.add_item(item_name, count)
            reward_strs.append(f"{count}x {item_name}")

        reward_summary = ", ".join(reward_strs) if reward_strs else "None"
        banner_msg = f"🏆 QUEST COMPLETE: {q_data['title']}! Rewards: {reward_summary}"
        self.pending_notifications.append(banner_msg)
        return banner_msg

    def on_pokemon_caught(self, pokemon_obj, inventory):
        """Called immediately when a Pokémon is successfully caught."""
        if not pokemon_obj:
            return []
        
        if isinstance(pokemon_obj, str):
            species = pokemon_obj
            species_types = POKEMON_SPECIES.get(species, {}).get("types", [])
        else:
            species = getattr(pokemon_obj, "species", "")
            species_types = getattr(pokemon_obj, "types", [])
            if not species_types and species in POKEMON_SPECIES:
                species_types = POKEMON_SPECIES[species].get("types", [])

        completed_msgs = []
        for q_id in list(self.active_quests.keys()):
            q_def = QUEST_DEFINITIONS.get(q_id, {})
            obj_type = q_def.get("objective_type")
            criteria = q_def.get("target_criteria", [])
            target_count = q_def.get("target_count", 1)

            matched = False
            if obj_type == "CATCH_TYPE":
                if any(t in criteria for t in species_types):
                    matched = True
            elif obj_type == "CATCH_SPECIES":
                if species in criteria:
                    matched = True

            if matched:
                self.active_quests[q_id]["progress"] += 1
                if self.active_quests[q_id]["progress"] >= target_count:
                    msg = self._complete_quest(q_id, inventory)
                    if msg:
                        completed_msgs.append(msg)

        return completed_msgs

    def on_pokemon_defeated(self, enemy_pokemon_obj, inventory, is_trainer=False):
        """Called immediately when an enemy Pokémon faints in battle."""
        if not enemy_pokemon_obj:
            return []

        if isinstance(enemy_pokemon_obj, str):
            species = enemy_pokemon_obj
            species_types = POKEMON_SPECIES.get(species, {}).get("types", [])
        else:
            species = getattr(enemy_pokemon_obj, "species", "")
            species_types = getattr(enemy_pokemon_obj, "types", [])
            if not species_types and species in POKEMON_SPECIES:
                species_types = POKEMON_SPECIES[species].get("types", [])

        completed_msgs = []
        for q_id in list(self.active_quests.keys()):
            q_def = QUEST_DEFINITIONS.get(q_id, {})
            obj_type = q_def.get("objective_type")
            criteria = q_def.get("target_criteria", [])
            target_count = q_def.get("target_count", 1)

            matched = False
            if obj_type == "DEFEAT_TYPE":
                if any(t in criteria for t in species_types):
                    matched = True
            elif obj_type == "DEFEAT_SPECIES":
                if species in criteria:
                    matched = True

            if matched:
                self.active_quests[q_id]["progress"] += 1
                if self.active_quests[q_id]["progress"] >= target_count:
                    msg = self._complete_quest(q_id, inventory)
                    if msg:
                        completed_msgs.append(msg)

        return completed_msgs

    def on_trainer_defeated(self, trainer_id, inventory):
        """Called immediately when a trainer battle is won."""
        completed_msgs = []
        for q_id in list(self.active_quests.keys()):
            q_def = QUEST_DEFINITIONS.get(q_id, {})
            obj_type = q_def.get("objective_type")
            target_count = q_def.get("target_count", 1)

            if obj_type == "DEFEAT_TRAINERS":
                self.active_quests[q_id]["progress"] += 1
                if self.active_quests[q_id]["progress"] >= target_count:
                    msg = self._complete_quest(q_id, inventory)
                    if msg:
                        completed_msgs.append(msg)

        return completed_msgs

    def on_item_used(self, item_name, *args, **kwargs):
        """Called when an item (like an evolution stone) is used on a Pokémon."""
        inventory = None
        for a in args:
            if hasattr(a, "add_item"):
                inventory = a
        if "inventory" in kwargs:
            inventory = kwargs["inventory"]

        completed_msgs = []
        for q_id in list(self.active_quests.keys()):
            q_def = QUEST_DEFINITIONS.get(q_id, {})
            obj_type = q_def.get("objective_type")
            criteria = q_def.get("target_criteria", [])
            target_count = q_def.get("target_count", 1)

            if obj_type == "USE_EVOLUTION_STONE":
                if not criteria or item_name in criteria or any(stone in item_name for stone in ["Stone", "stone"]):
                    self.active_quests[q_id]["progress"] += 1
                    if self.active_quests[q_id]["progress"] >= target_count:
                        msg = self._complete_quest(q_id, inventory)
                        if msg:
                            completed_msgs.append(msg)

        return completed_msgs

    def pop_notifications(self):
        notifs = list(self.pending_notifications)
        self.pending_notifications.clear()
        return notifs

    def to_dict(self):
        return {
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests
        }

    @classmethod
    def from_dict(cls, data):
        mgr = cls()
        if not data:
            return mgr
        mgr.active_quests = data.get("active_quests", {})
        mgr.completed_quests = data.get("completed_quests", {})
        return mgr
