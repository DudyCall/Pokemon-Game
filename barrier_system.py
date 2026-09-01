"""
barrier_system.py - Zone Progression Barriers, Gated Checkpoints, and Sleeping Pokemon Obstacles.
Manages physical roadblocks across Kanto unlocked via Quests, Gym Badges, Level Milestones, Pokédex Progress, and Key Items.
"""
import pygame
from constants import TILE_SIZE, WHITE, BLACK, GRAY, DARK_GRAY

BARRIER_DEFINITIONS = {
    "barrier_route2_survey": {
        "id": "barrier_route2_survey",
        "map_name": "Viridian City",
        "name": "Route 2 Roadblock Officer",
        "sprite_type": "police_roadblock",
        "tiles": [(12, 1), (13, 1), (14, 1), (15, 1)],
        "interaction_tiles": [(12, 2), (13, 2), (14, 2), (15, 2), (12, 0), (13, 0), (14, 0), (15, 0)],
        "condition_type": "QUEST_OR_CAUGHT",
        "required_quest": "oak_bug_hunt",
        "required_caught": 3,
        "blocked_title": "Route 2 Checkpoint",
        "blocked_message": (
            "HALT! Route 2 and Viridian Forest are closed for ecological field research!\n\n"
            "Prof. Oak needs survey data on local insect species before opening the route.\n"
            "Complete the 'Bug Researcher's Survey' quest or catch at least 3 Pokémon to pass!"
        ),
        "cleared_title": "Route 2 Open",
        "cleared_message": (
            "Inspection Complete!\n\n"
            "Superb job assisting Prof. Oak with field research!\n"
            "The checkpoint is now clear. You may proceed north to Route 2 and Viridian Forest!"
        ),
    },
    "barrier_pewter_boulder": {
        "id": "barrier_pewter_boulder",
        "map_name": "Pewter City",
        "name": "Pewter League Guard",
        "sprite_type": "league_guard",
        "tiles": [(26, 7), (26, 8), (26, 9), (26, 12), (26, 13), (26, 14)],
        "interaction_tiles": [(25, 7), (25, 8), (25, 9), (25, 12), (25, 13), (25, 14), (27, 7), (27, 8), (27, 9), (27, 12), (27, 13), (27, 14)],
        "condition_type": "BADGE",
        "required_badge": "boulder",
        "blocked_title": "Pewter City Checkpoint",
        "blocked_message": (
            "HALT! The path to Route 3 and Mt. Moon is treacherous!\n\n"
            "Only trainers who have proven their battle mastery against Gym Leader Brock and earned the BOULDER BADGE may pass!"
        ),
        "cleared_title": "Route 3 Cleared",
        "cleared_message": (
            "That's Brock's Boulder Badge glistening on your vest!\n\n"
            "Outstanding victory, Trainer! The road east to Route 3 and Mt. Moon is now open to you!"
        ),
    },
    "barrier_cerulean_bridge": {
        "id": "barrier_cerulean_bridge",
        "map_name": "Cerulean City",
        "name": "Cerulean Bridge Security",
        "sprite_type": "police_roadblock",
        "tiles": [(13, 5), (14, 5)],
        "interaction_tiles": [(13, 6), (14, 6), (13, 4), (14, 4)],
        "condition_type": "BADGE_OR_LEVEL",
        "required_badge": "cascade",
        "required_level": 18,
        "blocked_title": "Nugget Bridge Security",
        "blocked_message": (
            "ATTENTION! Route 24 and the Nugget Bridge are on high security alert due to suspicious Team Rocket activity!\n\n"
            "You need the CASCADE BADGE from Gym Leader Misty or a Pokémon trained to Level 18+ to proceed north!"
        ),
        "cleared_title": "Nugget Bridge Open",
        "cleared_message": (
            "Your battle credentials check out!\n\n"
            "You are strong enough to handle any trouble ahead. The bridge to Route 24 and Bill's Sea Cottage is open!"
        ),
    },
    "barrier_vermilion_power": {
        "id": "barrier_vermilion_power",
        "map_name": "Vermilion City",
        "name": "Power Grid Repairman",
        "sprite_type": "electric_gate",
        "tiles": [(26, 11), (26, 12)],
        "interaction_tiles": [(25, 11), (25, 12), (27, 11), (27, 12)],
        "condition_type": "QUEST_OR_BADGE",
        "required_quest": "sparky_electric_charge",
        "required_badge": "thunder",
        "blocked_title": "High Voltage Hazard",
        "blocked_message": (
            "DANGER: High-Voltage Power Lines are currently being overhauled across Route 11!\n\n"
            "Assist Electrician Sparky with the 'High Voltage Research' quest or prove electrical safety with the THUNDER BADGE to pass!"
        ),
        "cleared_title": "Route 11 Cleared",
        "cleared_message": (
            "All electrical tests passed!\n\n"
            "The surge lines are stabilized. The eastern gate to Route 11 and Diglett's Cave is officially open!"
        ),
    },
    "barrier_snorlax_route12": {
        "id": "barrier_snorlax_route12",
        "map_name": "Route 12",
        "name": "Sleeping Snorlax",
        "sprite_type": "snorlax_sleep",
        "tiles": [(8, 10), (9, 10), (10, 10), (11, 10)],
        "interaction_tiles": [(8, 9), (9, 9), (10, 9), (11, 9), (8, 11), (9, 11), (10, 11), (11, 11)],
        "condition_type": "ITEM_OR_LEVEL",
        "required_item": "Poke Flute",
        "required_level": 25,
        "blocked_title": "Sleeping Pokémon",
        "blocked_message": (
            "A colossal Pokémon is sound asleep right in the middle of the bridge!\n\n"
            "It's snoring peacefully: 'Zzz... Gwaaah... Zzz...'\n"
            "You need a POKÉ FLUTE or a seasoned party with a Pokémon at Level 25+ to awaken it!"
        ),
        "cleared_title": "Snorlax Awakened!",
        "cleared_message": (
            "You played a lively tune on the Poké Flute!\n\n"
            "Snorlax woke up, yawned heartily, stretched with immense joy, and lumbered back to the mountain forests!\n"
            "The coastal path to Fuchsia City is completely clear!"
        ),
    },
    "barrier_safari_fuchsia": {
        "id": "barrier_safari_fuchsia",
        "map_name": "Fuchsia City",
        "name": "Safari Zone Warden",
        "sprite_type": "safari_gate",
        "tiles": [(4, 4), (5, 4), (24, 4), (25, 4)],
        "interaction_tiles": [(4, 5), (5, 5), (24, 5), (25, 5), (4, 3), (5, 3), (24, 3), (25, 3)],
        "condition_type": "POKEDEX_AND_BADGE",
        "required_caught": 20,
        "required_badge": "soul",
        "required_quest": "ninja_toxic_challenge",
        "blocked_title": "Safari Zone Gate",
        "blocked_message": (
            "Safari Zone Ranger Station:\n\n"
            "The Safari Zone is a protected wild Pokémon reserve. Entry is restricted to certified field researchers!\n"
            "Requirements: At least 20 registered Pokédex species AND (SOUL BADGE or 'Shadows & Toxic Mists' quest completion)!"
        ),
        "cleared_title": "Safari Access Granted",
        "cleared_message": (
            "Welcome, Certified Pokémon Ranger!\n\n"
            "Your Pokédex and badges demonstrate exceptional mastery. Enjoy exploring the Golden Savanna Safari Zone!"
        ),
    },
    "barrier_power_plant": {
        "id": "barrier_power_plant",
        "map_name": "Route 9",
        "name": "Power Plant Security Gate",
        "sprite_type": "electric_gate",
        "tiles": [(18, 3)],
        "interaction_tiles": [(18, 4), (18, 2)],
        "condition_type": "QUEST_OR_LEVEL",
        "required_quest": "celadon_evolution_mastery",
        "required_level": 35,
        "blocked_title": "Industrial High Voltage Reactor",
        "blocked_message": (
            "WARNING: Experimental High-Voltage Generator Complex!\n\n"
            "Active magnetic storms require elemental evolution expertise or high battle power.\n"
            "Complete 'Elemental Evolution Catalyst' or train a Pokémon to Level 35+ to enter!"
        ),
        "cleared_title": "Power Plant Unlocked",
        "cleared_message": (
            "Industrial Blast Gate Unlocked!\n\n"
            "Facility security systems disarmed. Proceed with caution inside the Power Plant!"
        ),
    },
    "barrier_seafoam_grotto": {
        "id": "barrier_seafoam_grotto",
        "map_name": "Route 21",
        "name": "Glacial Frost Seal",
        "sprite_type": "boulder",
        "tiles": [(9, 16), (10, 16)],
        "interaction_tiles": [(9, 15), (10, 15), (9, 17), (10, 17)],
        "condition_type": "BADGE_COUNT_OR_LEVEL",
        "required_badge_count": 6,
        "required_level": 40,
        "blocked_title": "Sub-Zero Glacial Ice Barrier",
        "blocked_message": (
            "Arctic gale-force blizzards howl out of the glacial cavern!\n\n"
            "The sheer cold prevents entry. You need at least 6 Kanto Gym Badges or a Pokémon at Level 40+ to withstand the freeze!"
        ),
        "cleared_title": "Seafoam Grotto Open",
        "cleared_message": (
            "Your fiery battle spirit melts the sub-zero ice barrier!\n\n"
            "The glacial cavern mouth of Seafoam Islands is now accessible!"
        ),
    },
    "barrier_victory_road": {
        "id": "barrier_victory_road",
        "map_name": "Route 22",
        "name": "Pokémon League Elite Guard",
        "sprite_type": "league_guard",
        "tiles": [(9, 8)],
        "interaction_tiles": [(9, 9), (9, 7)],
        "condition_type": "BADGE_COUNT_AND_LEVEL",
        "required_badge_count": 7,
        "required_level": 45,
        "blocked_title": "Pokémon League Checkpoint",
        "blocked_message": (
            "HALT! This is the Indigo Plateau Pokémon League Checkpoint!\n\n"
            "Only master trainers who possess at least 7 Kanto Gym Badges and a Pokémon trained to Level 45+ may enter Victory Road!"
        ),
        "cleared_title": "Victory Road Open",
        "cleared_message": (
            "Seven Gym Badges confirmed and your team's battle power is immense!\n\n"
            "Pass through, champion in the making! Victory Road and the Indigo Plateau await you!"
        ),
    },
    "barrier_cerulean_cave": {
        "id": "barrier_cerulean_cave",
        "map_name": "Cerulean City",
        "name": "Mystic Psychic Barrier",
        "sprite_type": "psychic_seal",
        "tiles": [(4, 2)],
        "interaction_tiles": [(4, 3), (4, 1)],
        "condition_type": "ALL_BADGES_AND_LEVEL",
        "required_badge_count": 8,
        "required_level": 55,
        "blocked_title": "Mysterious Psychic Seal",
        "blocked_message": (
            "A colossal, pulsing psychic barrier seals the entrance to Cerulean Cave!\n\n"
            "Inconceivably dangerous legendary Pokémon dwell within.\n"
            "Requirements: All 8 Kanto Gym Badges AND a Pokémon trained to Level 55+!"
        ),
        "cleared_title": "Cerulean Cave Unlocked",
        "cleared_message": (
            "The 8 Kanto Badges resonate with brilliant light, shattering the psychic seal!\n\n"
            "Cerulean Cave is open. Prepare yourself for the ultimate battle!"
        ),
    },
}


class BarrierManager:
    def __init__(self):
        self.definitions = BARRIER_DEFINITIONS

    def is_tile_blocked(self, map_name, x, y, unlocked_barriers):
        for b_id, b_data in self.definitions.items():
            if b_data["map_name"] == map_name and (x, y) in b_data["tiles"]:
                if b_id not in unlocked_barriers:
                    return True
        return False

    def get_barrier_at(self, map_name, x, y, unlocked_barriers=None):
        for b_id, b_data in self.definitions.items():
            if b_data["map_name"] == map_name:
                if (x, y) in b_data["tiles"] or (x, y) in b_data["interaction_tiles"]:
                    if unlocked_barriers is None or b_id not in unlocked_barriers:
                        return b_data
        return None

    def evaluate_condition(self, barrier_id, player, party, world, quest_mgr, pokedex, inventory):
        b_data = self.definitions.get(barrier_id)
        if not b_data:
            return True, "No condition"

        c_type = b_data.get("condition_type")
        max_level = max([p.level for p in party], default=1)
        badge_count = len(getattr(world, "badges", set()))
        caught_count = len(getattr(pokedex, "caught", set()))

        if c_type == "QUEST_OR_CAUGHT":
            req_quest = b_data.get("required_quest")
            req_caught = b_data.get("required_caught", 3)
            q_ok = quest_mgr.is_completed(req_quest) if quest_mgr else False
            c_ok = caught_count >= req_caught
            is_met = q_ok or c_ok
            prog = f"[Bug Survey Quest: {'Done' if q_ok else 'Incomplete'} | Caught: {caught_count}/{req_caught}]"
            return is_met, prog

        elif c_type == "BADGE":
            req_badge = b_data.get("required_badge")
            is_met = req_badge in getattr(world, "badges", set())
            prog = f"[{req_badge.capitalize()} Badge: {'Earned' if is_met else 'Not Earned'}]"
            return is_met, prog

        elif c_type == "BADGE_OR_LEVEL":
            req_badge = b_data.get("required_badge")
            req_level = b_data.get("required_level", 18)
            b_ok = req_badge in getattr(world, "badges", set())
            l_ok = max_level >= req_level
            is_met = b_ok or l_ok
            prog = f"[{req_badge.capitalize()} Badge: {'Earned' if b_ok else 'None'} | Highest Lv: {max_level}/{req_level}]"
            return is_met, prog

        elif c_type == "QUEST_OR_BADGE":
            req_quest = b_data.get("required_quest")
            req_badge = b_data.get("required_badge")
            q_ok = quest_mgr.is_completed(req_quest) if quest_mgr else False
            b_ok = req_badge in getattr(world, "badges", set())
            is_met = q_ok or b_ok
            prog = f"[Quest: {'Done' if q_ok else 'Incomplete'} | {req_badge.capitalize()} Badge: {'Earned' if b_ok else 'None'}]"
            return is_met, prog

        elif c_type == "ITEM_OR_LEVEL":
            req_item = b_data.get("required_item")
            req_level = b_data.get("required_level", 25)
            i_ok = inventory.get_count(req_item) > 0 if inventory else False
            l_ok = max_level >= req_level
            is_met = i_ok or l_ok
            prog = f"[{req_item}: {'In Bag' if i_ok else 'Missing'} | Highest Lv: {max_level}/{req_level}]"
            return is_met, prog

        elif c_type == "POKEDEX_AND_BADGE":
            req_caught = b_data.get("required_caught", 20)
            req_badge = b_data.get("required_badge")
            req_quest = b_data.get("required_quest")
            c_ok = caught_count >= req_caught
            b_ok = req_badge in getattr(world, "badges", set())
            q_ok = quest_mgr.is_completed(req_quest) if quest_mgr else False
            is_met = c_ok and (b_ok or q_ok)
            prog = f"[Pokédex: {caught_count}/{req_caught} | Badge/Quest: {'Ready' if (b_ok or q_ok) else 'Incomplete'}]"
            return is_met, prog

        elif c_type == "QUEST_OR_LEVEL":
            req_quest = b_data.get("required_quest")
            req_level = b_data.get("required_level", 35)
            q_ok = quest_mgr.is_completed(req_quest) if quest_mgr else False
            l_ok = max_level >= req_level
            is_met = q_ok or l_ok
            prog = f"[Quest: {'Done' if q_ok else 'Incomplete'} | Highest Lv: {max_level}/{req_level}]"
            return is_met, prog

        elif c_type == "BADGE_COUNT_OR_LEVEL":
            req_count = b_data.get("required_badge_count", 6)
            req_level = b_data.get("required_level", 40)
            b_ok = badge_count >= req_count
            l_ok = max_level >= req_level
            is_met = b_ok or l_ok
            prog = f"[Badges: {badge_count}/{req_count} | Highest Lv: {max_level}/{req_level}]"
            return is_met, prog

        elif c_type == "BADGE_COUNT_AND_LEVEL":
            req_count = b_data.get("required_badge_count", 7)
            req_level = b_data.get("required_level", 45)
            b_ok = badge_count >= req_count
            l_ok = max_level >= req_level
            is_met = b_ok and l_ok
            prog = f"[Badges: {badge_count}/{req_count} | Highest Lv: {max_level}/{req_level}]"
            return is_met, prog

        elif c_type == "ALL_BADGES_AND_LEVEL":
            req_count = b_data.get("required_badge_count", 8)
            req_level = b_data.get("required_level", 55)
            b_ok = badge_count >= req_count
            l_ok = max_level >= req_level
            is_met = b_ok and l_ok
            prog = f"[Badges: {badge_count}/{req_count} | Highest Lv: {max_level}/{req_level}]"
            return is_met, prog

        return True, "Ready"

    def get_active_barriers_for_map(self, map_name, unlocked_barriers):
        active = []
        for b_id, b_data in self.definitions.items():
            if b_data["map_name"] == map_name and b_id not in unlocked_barriers:
                active.append(b_data)
        return active


barrier_mgr = BarrierManager()
