"""
map_data.py - Map definitions, warps, NPC spawns, signs, and ground item placements.
Re-exports all map grids from map_grids for 100% backward compatibility.
"""
from constants import Direction
from map_grids import *

MAP_DEFINITIONS = {
    "Pallet Town": {
        "grid": MAP_PALLET_TOWN,
        "bgm": "town",
        "warps": {
            (4, 4): {"target_map": "Player's House", "target_x": 5, "target_y": 6},
            (18, 4): {"target_map": "Oak's Lab", "target_x": 6, "target_y": 8},
            (8, 0): {"target_map": "Route 1", "target_x": 8, "target_y": 24},
            (9, 0): {"target_map": "Route 1", "target_x": 9, "target_y": 24},
            (10, 0): {"target_map": "Route 1", "target_x": 10, "target_y": 24},
            (11, 0): {"target_map": "Route 1", "target_x": 11, "target_y": 24},
            (9, 17): {"target_map": "Route 21", "target_x": 9, "target_y": 1},
            (10, 17): {"target_map": "Route 21", "target_x": 10, "target_y": 1}
        },
        "npcs": [
            {"name": "Town Elder", "x": 5, "y": 7, "dir": Direction.DOWN, "dialog": "Welcome to Pallet Town! Take the path North to explore Route 1, or visit Prof. Oak's Lab!"},
            {"name": "Prof. Oak's Aide", "x": 14, "y": 7, "dir": Direction.DOWN, "quest_id": "oak_bug_hunt", "dialog": "Hello trainer! Prof. Oak needs field data on wild insects. Can you catch 3 Bug-type Pokémon for our research? (Reward: $1000, 5x Great Ball, 1x Rare Candy)"}
        ],
        "signs": {
            (3, 10): "Pallet Town - Shades of your journey await!",
            (16, 10): "Prof. Oak's Pokémon Research Lab"
        },
        "ground_items": [
            {"id": "pallet_potion", "x": 3, "y": 7, "item": "Potion", "count": 1}
        ]
    },
    "Route 1": {
        "grid": MAP_ROUTE_1,
        "bgm": "town",
        "encounter_zone": "Route 1",
        "warps": {
            (8, 25): {"target_map": "Pallet Town", "target_x": 8, "target_y": 1},
            (9, 25): {"target_map": "Pallet Town", "target_x": 9, "target_y": 1},
            (10, 25): {"target_map": "Pallet Town", "target_x": 10, "target_y": 1},
            (11, 25): {"target_map": "Pallet Town", "target_x": 11, "target_y": 1},
            (8, 0): {"target_map": "Viridian City", "target_x": 12, "target_y": 22},
            (9, 0): {"target_map": "Viridian City", "target_x": 13, "target_y": 22},
            (10, 0): {"target_map": "Viridian City", "target_x": 14, "target_y": 22},
            (11, 0): {"target_map": "Viridian City", "target_x": 15, "target_y": 22}
        },
        "trainers": ["youngster_joey", "bug_catcher_sammy"],
        "npcs": [
            {"name": "Bird Watcher", "x": 14, "y": 14, "dir": Direction.LEFT, "quest_id": "bird_watcher_avian", "dialog": "I study avian Pokémon aerial maneuvers! Defeat 3 Flying-type Pokémon in battle to test your battle skills! (Reward: $1200, 3x Super Potion, 1x Rare Candy)"}
        ],
        "signs": {
            (3, 7): "Route 1 - Connecting Pallet Town and Viridian City."
        },
        "ground_items": [
            {"id": "route1_potion", "x": 3, "y": 21, "item": "Potion", "count": 1}
        ]
    },
    "Viridian City": {
        "grid": MAP_VIRIDIAN_CITY,
        "bgm": "town",
        "warps": {
            (12, 23): {"target_map": "Route 1", "target_x": 8, "target_y": 1},
            (13, 23): {"target_map": "Route 1", "target_x": 9, "target_y": 1},
            (14, 23): {"target_map": "Route 1", "target_x": 10, "target_y": 1},
            (15, 23): {"target_map": "Route 1", "target_x": 11, "target_y": 1},
            (6, 4): {"target_map": "Pokecenter", "target_x": 6, "target_y": 6},
            (24, 4): {"target_map": "Mart", "target_x": 6, "target_y": 5},
            (0, 11): {"target_map": "Route 22", "target_x": 26, "target_y": 8},
            (0, 12): {"target_map": "Route 22", "target_x": 26, "target_y": 9},
            (0, 13): {"target_map": "Route 22", "target_x": 26, "target_y": 10},
            (12, 0): {"target_map": "Viridian Forest", "target_x": 16, "target_y": 30},
            (13, 0): {"target_map": "Viridian Forest", "target_x": 17, "target_y": 30},
            (14, 0): {"target_map": "Viridian Forest", "target_x": 18, "target_y": 30},
            (15, 0): {"target_map": "Viridian Forest", "target_x": 19, "target_y": 30}
        },
        "npcs": [
            {"name": "Old Man", "x": 18, "y": 9, "dir": Direction.DOWN, "dialog": "Viridian Forest to the north is a lush maze! Head west to Route 22 if you want to test your strength."}
        ],
        "signs": {
            (3, 6): "Viridian City - The Eternally Green Paradise",
            (24, 6): "Trainer Academy - Learn battle tactics and type matchups!"
        }
    },
    "Route 22": {
        "grid": MAP_ROUTE_22,
        "bgm": "town",
        "encounter_zone": "Route 22",
        "warps": {
            (27, 8): {"target_map": "Viridian City", "target_x": 1, "target_y": 11},
            (27, 9): {"target_map": "Viridian City", "target_x": 1, "target_y": 12},
            (27, 10): {"target_map": "Viridian City", "target_x": 1, "target_y": 13},
            (9, 7): {"target_map": "Victory Road", "target_x": 15, "target_y": 24}
        },
        "trainers": ["rival_blue", "hiker_franklin"],
        "npcs": [
            {"name": "Veteran Ace Trainer", "x": 14, "y": 8, "dir": Direction.DOWN, "quest_id": "champion_road_trial", "dialog": "On the road to the Pokémon League, only the strongest survive! Defeat 5 Trainer opponents in battle! (Reward: $6000, 5x Rare Candy, 2x Nugget)"}
        ],
        "signs": {
            (6, 8): "Route 22 - Indigo Plateau Pokémon League Front Gate."
        },
        "ground_items": [
            {"id": "route22_greatball", "x": 18, "y": 6, "item": "Great Ball", "count": 2},
            {"id": "route22_potion", "x": 6, "y": 12, "item": "Super Potion", "count": 1}
        ]
    },
    "Viridian Forest": {
        "grid": MAP_VIRIDIAN_FOREST,
        "bgm": "town",
        "encounter_zone": "Viridian Forest",
        "warps": {
            (16, 31): {"target_map": "Viridian City", "target_x": 12, "target_y": 0},
            (17, 31): {"target_map": "Viridian City", "target_x": 13, "target_y": 0},
            (18, 31): {"target_map": "Viridian City", "target_x": 14, "target_y": 0},
            (19, 31): {"target_map": "Viridian City", "target_x": 15, "target_y": 0},
            (16, 0): {"target_map": "Pewter City", "target_x": 13, "target_y": 22},
            (17, 0): {"target_map": "Pewter City", "target_x": 14, "target_y": 22},
            (18, 0): {"target_map": "Pewter City", "target_x": 15, "target_y": 22},
            (19, 0): {"target_map": "Pewter City", "target_x": 16, "target_y": 22}
        },
        "trainers": ["bug_catcher_colton", "bug_catcher_rick", "lass_haley"],
        "signs": {
            (27, 27): "Viridian Forest - Beware of Poison Sting and rare Electric Pikachu in the trees!"
        },
        "ground_items": [
            {"id": "forest_antidote", "x": 13, "y": 9, "item": "Antidote", "count": 2},
            {"id": "forest_pokeball", "x": 25, "y": 19, "item": "Poke Ball", "count": 3},
            {"id": "forest_candy", "x": 3, "y": 27, "item": "Rare Candy", "count": 1}
        ]
    },
    "Pewter City": {
        "grid": MAP_PEWTER_CITY,
        "bgm": "town",
        "warps": {
            (13, 23): {"target_map": "Viridian Forest", "target_x": 16, "target_y": 1},
            (14, 23): {"target_map": "Viridian Forest", "target_x": 17, "target_y": 1},
            (15, 23): {"target_map": "Viridian Forest", "target_x": 18, "target_y": 1},
            (16, 23): {"target_map": "Viridian Forest", "target_x": 19, "target_y": 1},
            (6, 4): {"target_map": "Pokecenter", "target_x": 6, "target_y": 6},
            (24, 4): {"target_map": "Mart", "target_x": 6, "target_y": 5},
            (9, 11): {"target_map": "Pewter Gym", "target_x": 6, "target_y": 8},
            (21, 11): {"target_map": "Museum", "target_x": 6, "target_y": 6},
            (31, 7): {"target_map": "Route 3", "target_x": 1, "target_y": 7},
            (31, 8): {"target_map": "Route 3", "target_x": 1, "target_y": 8},
            (31, 9): {"target_map": "Route 3", "target_x": 1, "target_y": 9},
            (31, 12): {"target_map": "Route 3", "target_x": 1, "target_y": 11},
            (31, 13): {"target_map": "Route 3", "target_x": 1, "target_y": 12},
            (31, 14): {"target_map": "Route 3", "target_x": 1, "target_y": 13}
        },
        "npcs": [
            {"name": "Museum Guide", "x": 20, "y": 15, "dir": Direction.LEFT, "dialog": "Welcome to Pewter City! Check out the Museum of Science, or challenge Leader Brock at the Gym!"},
            {"name": "Fossil Maniac", "x": 16, "y": 12, "dir": Direction.DOWN, "quest_id": "fossil_moon_mystery", "dialog": "Mt. Moon holds ancient lunar secrets! Catch 2 mountain Pokémon (Clefairy, Geodude, Onix, Paras, or Zubat). (Reward: $2500, Moon Stone, Nugget)"}
        ],
        "signs": {
            (3, 6): "Pewter City - A Stone Gray City",
            (24, 6): "Pewter City PokéMart - Quality Items for Mountain Climbing",
            (6, 12): "Pewter City Gym - Leader: Brock (The Rock-Solid Pokémon Trainer!)",
            (18, 12): "Pewter Museum of Science - Ancient Fossils & Moon Stones"
        }
    },
    "Route 3": {
        "grid": MAP_ROUTE_3,
        "bgm": "town",
        "encounter_zone": "Route 3",
        "warps": {
            (0, 7): {"target_map": "Pewter City", "target_x": 30, "target_y": 7},
            (0, 8): {"target_map": "Pewter City", "target_x": 30, "target_y": 8},
            (0, 9): {"target_map": "Pewter City", "target_x": 30, "target_y": 9},
            (0, 11): {"target_map": "Pewter City", "target_x": 30, "target_y": 12},
            (0, 12): {"target_map": "Pewter City", "target_x": 30, "target_y": 13},
            (0, 13): {"target_map": "Pewter City", "target_x": 30, "target_y": 14},
            (28, 0): {"target_map": "Mt. Moon", "target_x": 1, "target_y": 21}
        },
        "trainers": ["lass_janice", "youngster_ben", "hiker_wayne"],
        "signs": {
            (3, 13): "Route 3 - Foot of Mt. Moon",
            (24, 13): "Mt. Moon Entrance - Dark Tunnels Ahead!"
        },
        "ground_items": [
            {"id": "route3_superpotion", "x": 27, "y": 10, "item": "Super Potion", "count": 1}
        ]
    },
    "Mt. Moon": {
        "grid": MAP_MT_MOON,
        "bgm": "town",
        "encounter_zone": "Mt. Moon",
        "warps": {
            (1, 21): {"target_map": "Route 3", "target_x": 28, "target_y": 1},
            (30, 2): {"target_map": "Route 4", "target_x": 3, "target_y": 1}
        },
        "trainers": ["rocket_grunt_1", "super_nerd_miguel", "hiker_marcos"],
        "signs": {
            (3, 20): "Mt. Moon Caverns - Rare Clefairy and Moon Stones have been sighted here!"
        },
        "ground_items": [
            {"id": "mtmoon_moonstone", "x": 6, "y": 4, "item": "Moon Stone", "count": 1},
            {"id": "mtmoon_escaperope", "x": 20, "y": 4, "item": "Escape Rope", "count": 1},
            {"id": "mtmoon_candy", "x": 20, "y": 19, "item": "Rare Candy", "count": 1}
        ]
    },
    "Route 4": {
        "grid": MAP_ROUTE_4,
        "bgm": "town",
        "encounter_zone": "Route 4",
        "warps": {
            (3, 0): {"target_map": "Mt. Moon", "target_x": 30, "target_y": 2},
            (27, 4): {"target_map": "Cerulean City", "target_x": 1, "target_y": 11},
            (27, 5): {"target_map": "Cerulean City", "target_x": 1, "target_y": 12},
            (27, 6): {"target_map": "Cerulean City", "target_x": 1, "target_y": 13}
        },
        "trainers": ["lass_crissy", "blackbelt_koji"],
        "signs": {
            (3, 10): "Route 4 - Mt. Moon to Cerulean City River Slopes",
            (24, 10): "Cerulean City Ahead!"
        },
        "ground_items": [
            {"id": "route4_greatball", "x": 9, "y": 11, "item": "Great Ball", "count": 2}
        ]
    },
    "Cerulean City": {
        "grid": MAP_CERULEAN_CITY,
        "bgm": "town",
        "warps": {
            (0, 11): {"target_map": "Route 4", "target_x": 26, "target_y": 4},
            (0, 12): {"target_map": "Route 4", "target_x": 26, "target_y": 5},
            (0, 13): {"target_map": "Route 4", "target_x": 26, "target_y": 6},
            (6, 4): {"target_map": "Pokecenter", "target_x": 6, "target_y": 6},
            (24, 4): {"target_map": "Mart", "target_x": 6, "target_y": 5},
            (9, 11): {"target_map": "Cerulean Gym", "target_x": 6, "target_y": 8},
            (4, 0): {"target_map": "Cerulean Cave", "target_x": 12, "target_y": 20},
            (12, 0): {"target_map": "Route 24", "target_x": 9, "target_y": 26},
            (13, 0): {"target_map": "Route 24", "target_x": 9, "target_y": 26},
            (14, 0): {"target_map": "Route 24", "target_x": 10, "target_y": 26},
            (15, 0): {"target_map": "Route 24", "target_x": 10, "target_y": 26},
            (12, 23): {"target_map": "Route 5", "target_x": 12, "target_y": 1},
            (13, 23): {"target_map": "Route 5", "target_x": 13, "target_y": 1},
            (14, 23): {"target_map": "Route 5", "target_x": 14, "target_y": 1},
            (15, 23): {"target_map": "Route 5", "target_x": 15, "target_y": 1},
            (31, 11): {"target_map": "Route 9", "target_x": 1, "target_y": 8},
            (31, 12): {"target_map": "Route 9", "target_x": 1, "target_y": 9},
            (31, 13): {"target_map": "Route 9", "target_x": 1, "target_y": 10}
        },
        "npcs": [
            {"name": "Officer Jenny", "x": 18, "y": 9, "dir": Direction.DOWN, "dialog": "Keep an eye out for suspicious Team Rocket grunts! North is Nugget Bridge, and East leads to Route 9 Rock Canyon!"}
        ],
        "signs": {
            (3, 1): "Cerulean Cave Ahead - Caution: High-Level Subterranean Pokémon & Legendary Secrets!",
            (3, 6): "Cerulean City - A Mysterious Blue Aura",
            (24, 6): "Cerulean PokéMart",
            (6, 13): "Cerulean Gym - Leader: Misty (The Tomboyish Mermaid!)",
            (24, 13): "Route 9 Rock Canyon & Lavender Town Ahead!"
        }
    },
    "Route 9": {
        "grid": MAP_ROUTE_9,
        "bgm": "town",
        "encounter_zone": "Route 9",
        "warps": {
            (0, 8): {"target_map": "Cerulean City", "target_x": 30, "target_y": 11},
            (0, 9): {"target_map": "Cerulean City", "target_x": 30, "target_y": 12},
            (0, 10): {"target_map": "Cerulean City", "target_x": 30, "target_y": 13},
            (31, 8): {"target_map": "Lavender Town", "target_x": 13, "target_y": 1},
            (31, 9): {"target_map": "Lavender Town", "target_x": 14, "target_y": 1},
            (31, 10): {"target_map": "Lavender Town", "target_x": 14, "target_y": 1},
            (18, 0): {"target_map": "Power Plant", "target_x": 13, "target_y": 20}
        },
        "trainers": ["camper_drew", "picnicker_alicia", "hiker_alan"],
        "signs": {
            (3, 14): "Route 9 - Rocky Canyon Pass to Lavender Town",
            (27, 14): "Notice: High voltage Power Plant to the North"
        },
        "ground_items": [
            {"id": "route9_tm", "x": 15, "y": 14, "item": "Super Potion", "count": 2}
        ]
    },
    "Lavender Town": {
        "grid": MAP_LAVENDER_TOWN,
        "bgm": "town",
        "encounter_zone": "Lavender Town",
        "warps": {
            (12, 0): {"target_map": "Route 9", "target_x": 30, "target_y": 8},
            (13, 0): {"target_map": "Route 9", "target_x": 30, "target_y": 9},
            (14, 0): {"target_map": "Route 9", "target_x": 30, "target_y": 9},
            (15, 0): {"target_map": "Route 9", "target_x": 30, "target_y": 10},
            (0, 11): {"target_map": "Route 8", "target_x": 30, "target_y": 8},
            (0, 12): {"target_map": "Route 8", "target_x": 30, "target_y": 9},
            (0, 13): {"target_map": "Route 8", "target_x": 30, "target_y": 10},
            (6, 4): {"target_map": "Pokecenter", "target_x": 6, "target_y": 6},
            (24, 4): {"target_map": "Mart", "target_x": 6, "target_y": 5},
            (9, 10): {"target_map": "Pokémon Tower", "target_x": 13, "target_y": 20},
            (12, 23): {"target_map": "Route 12", "target_x": 9, "target_y": 1},
            (13, 23): {"target_map": "Route 12", "target_x": 10, "target_y": 1},
            (14, 23): {"target_map": "Route 12", "target_x": 10, "target_y": 1},
            (15, 23): {"target_map": "Route 12", "target_x": 11, "target_y": 1}
        },
        "npcs": [
            {"name": "Town Elder", "x": 16, "y": 8, "dir": Direction.DOWN, "dialog": "This is Lavender Town. Many trainers come here to pay their respects at Pokémon Tower."}
        ],
        "signs": {
            (3, 6): "Lavender Town - The Noble Purple Town",
            (22, 6): "Lavender PokéMart",
            (18, 6): "Pokémon Tower - Resting Place for Beloved Pokémon"
        },
        "ground_items": [
            {"id": "lavender_superball", "x": 5, "y": 20, "item": "Great Ball", "count": 3},
            {"id": "lavender_elixir", "x": 19, "y": 20, "item": "Max Potion", "count": 1}
        ]
    },
    "Pokémon Tower": {
        "grid": MAP_POKEMON_TOWER,
        "bgm": "town",
        "encounter_zone": "Pokémon Tower",
        "warps": {
            (13, 21): {"target_map": "Lavender Town", "target_x": 9, "target_y": 11}
        },
        "trainers": ["channeler_patricia", "channeler_carly", "channeler_hope"],
        "signs": {
            (3, 20): "Pokémon Tower - May the spirits of all Pokémon rest in peace."
        },
        "ground_items": [
            {"id": "tower_revive", "x": 6, "y": 4, "item": "Revive", "count": 1},
            {"id": "tower_candy", "x": 20, "y": 4, "item": "Rare Candy", "count": 1},
            {"id": "tower_escape", "x": 20, "y": 19, "item": "Escape Rope", "count": 1}
        ]
    },
    "Power Plant": {
        "grid": MAP_POWER_PLANT,
        "bgm": "town",
        "encounter_zone": "Power Plant",
        "warps": {
            (13, 21): {"target_map": "Route 9", "target_x": 18, "target_y": 1}
        },
        "trainers": ["scientist_bray", "pokemaniac_mark", "engineer_bucky"],
        "signs": {
            (3, 20): "Abandoned Power Plant - Danger! High Electric Current!"
        },
        "ground_items": [
            {"id": "powerplant_thunderstone", "x": 6, "y": 4, "item": "Thunder Stone", "count": 1},
            {"id": "powerplant_magnet", "x": 20, "y": 4, "item": "Magnet", "count": 1},
            {"id": "powerplant_ultraball", "x": 20, "y": 19, "item": "Ultra Ball", "count": 3}
        ]
    },
    "Safari Zone": {
        "grid": MAP_SAFARI_ZONE,
        "bgm": "town",
        "encounter_zone": "Safari Zone",
        "warps": {
            (14, 0): {"target_map": "Lavender Town", "target_x": 12, "target_y": 22},
            (15, 0): {"target_map": "Lavender Town", "target_x": 13, "target_y": 22},
            (16, 0): {"target_map": "Lavender Town", "target_x": 14, "target_y": 22},
            (17, 0): {"target_map": "Lavender Town", "target_x": 15, "target_y": 22}
        },
        "npcs": [
            {"name": "Safari Ranger", "x": 18, "y": 1, "dir": Direction.LEFT, "dialog": "Welcome to the Safari Wildlife Sanctuary! Catch rare wild Pokémon roaming the golden savanna!"}
        ],
        "signs": {
            (3, 28): "Safari Zone - Savanna Wildlife Sanctuary",
            (27, 28): "Rare Pokémon habitats: Waterhole, Amber Grass, and Acacia Groves."
        },
        "ground_items": [
            {"id": "safari_ball1", "x": 15, "y": 16, "item": "Ultra Ball", "count": 5},
            {"id": "safari_ball2", "x": 15, "y": 25, "item": "Rare Candy", "count": 2}
        ]
    },
    "Seafoam Islands": {
        "grid": MAP_SEAFOAM_ISLANDS,
        "bgm": "town",
        "encounter_zone": "Seafoam Islands",
        "warps": {
            (1, 21): {"target_map": "Route 21", "target_x": 11, "target_y": 17},
            (30, 2): {"target_map": "Route 21", "target_x": 11, "target_y": 15}
        },
        "trainers": ["skier_dianne", "boarder_felix"],
        "signs": {
            (3, 20): "Seafoam Islands - Sub-Zero Ice Cavern"
        },
        "ground_items": [
            {"id": "seafoam_waterstone", "x": 6, "y": 4, "item": "Water Stone", "count": 1},
            {"id": "seafoam_iceheal", "x": 20, "y": 4, "item": "Ice Heal", "count": 3},
            {"id": "seafoam_candy", "x": 20, "y": 19, "item": "Rare Candy", "count": 1}
        ]
    },
    "Route 24": {
        "grid": MAP_ROUTE_24,
        "bgm": "town",
        "encounter_zone": "Route 24",
        "warps": {
            (9, 27): {"target_map": "Cerulean City", "target_x": 13, "target_y": 1},
            (10, 27): {"target_map": "Cerulean City", "target_x": 14, "target_y": 1},
            (20, 0): {"target_map": "Bill's Cottage", "target_x": 6, "target_y": 6}
        },
        "trainers": [
            "bridge_challenger_1", "bridge_challenger_2", "bridge_challenger_3",
            "bridge_challenger_4", "bridge_challenger_5"
        ],
        "signs": {
            (3, 24): "Nugget Bridge - Defeat 5 consecutive Trainers to win a fabulous prize!",
            (16, 3): "Sea Cottage - Bill's Research Residence"
        },
        "ground_items": [
            {"id": "route24_nugget", "x": 19, "y": 6, "item": "Nugget", "count": 1}
        ]
    },
    "Route 21": {
        "grid": MAP_ROUTE_21,
        "bgm": "town",
        "encounter_zone": "Route 21",
        "warps": {
            (9, 0): {"target_map": "Pallet Town", "target_x": 9, "target_y": 16},
            (10, 0): {"target_map": "Pallet Town", "target_x": 10, "target_y": 16},
            (11, 16): {"target_map": "Seafoam Islands", "target_x": 1, "target_y": 21},
            (9, 31): {"target_map": "Cinnabar Island", "target_x": 10, "target_y": 1},
            (10, 31): {"target_map": "Cinnabar Island", "target_x": 11, "target_y": 1}
        },
        "trainers": ["swimmer_douglas", "fisherman_barny"],
        "ground_items": [
            {"id": "route21_ultraball", "x": 5, "y": 14, "item": "Ultra Ball", "count": 2}
        ]
    },
    "Cinnabar Island": {
        "grid": MAP_CINNABAR_ISLAND,
        "bgm": "town",
        "encounter_zone": "Cinnabar Island",
        "warps": {
            (10, 0): {"target_map": "Route 21", "target_x": 9, "target_y": 30},
            (11, 0): {"target_map": "Route 21", "target_x": 10, "target_y": 30},
            (6, 4): {"target_map": "Pokecenter", "target_x": 6, "target_y": 6},
            (18, 4): {"target_map": "Mart", "target_x": 6, "target_y": 5}
        },
        "trainers": ["scientist_ted", "firebreather_dick"],
        "signs": {
            (3, 6): "Cinnabar Island - The Fiery Town of Burning Desire",
            (15, 6): "Cinnabar PokéMart"
        },
        "ground_items": [
            {"id": "cinnabar_candy", "x": 6, "y": 17, "item": "Rare Candy", "count": 1},
            {"id": "cinnabar_maxpotion", "x": 17, "y": 17, "item": "Max Potion", "count": 1}
        ]
    },
    "Pokecenter": {
        "grid": MAP_POKECENTER,
        "bgm": "town",
        "warps": {
            (6, 7): {"target_map": "Pallet Town", "target_x": 4, "target_y": 5}
        },
        "npcs": [
            {"name": "Nurse Joy", "x": 5, "y": 3, "dir": Direction.DOWN, "dialog": "Welcome to our Pokémon Center! We heal your Pokémon back to full health!", "is_healer": True},
            {"name": "Move Master", "x": 2, "y": 5, "dir": Direction.RIGHT, "dialog": "I am the Move Master! For 3,000 coins, I can teach your Pokémon powerful new techniques or reroll their moveset!", "is_move_tutor": True},
            {"name": "PC Storage Terminal", "x": 8, "y": 5, "dir": Direction.DOWN, "dialog": "Booting up Pokémon Storage System...", "is_pc": True}
        ]
    },
    "Mart": {
        "grid": MAP_MART,
        "bgm": "town",
        "warps": {
            (6, 6): {"target_map": "Pallet Town", "target_x": 18, "target_y": 5}
        },
        "npcs": [
            {"name": "Clerk", "x": 5, "y": 3, "dir": Direction.DOWN, "dialog": "Hi there! Welcome to the PokéMart!", "is_shop": True}
        ]
    },
    "Oak's Lab": {
        "grid": MAP_OAKS_LAB,
        "bgm": "town",
        "warps": {
            (6, 8): {"target_map": "Pallet Town", "target_x": 18, "target_y": 5}
        },
        "npcs": [
            {"name": "Prof. Oak", "x": 6, "y": 3, "dir": Direction.DOWN, "is_oak": True, "dialog": "Hello there! Exploring the world and filling your Pokédex is the true spirit of Pokémon! Come see me anytime to evaluate your progress!"},
            {"name": "Lab Aide", "x": 2, "y": 5, "dir": Direction.RIGHT, "dialog": "Prof. Oak is the leading authority on Pokémon behavior and regional Pokédex data!"}
        ]
    },
    "Player's House": {
        "grid": MAP_PLAYERS_HOUSE,
        "bgm": "town",
        "warps": {
            (5, 6): {"target_map": "Pallet Town", "target_x": 4, "target_y": 5}
        },
        "npcs": [
            {"name": "Mom", "x": 4, "y": 3, "dir": Direction.DOWN, "is_healer": True, "dialog": "Hi honey! You're working so hard on your Pokémon journey! Rest here for a moment."}
        ]
    },
    "Pewter Gym": {
        "grid": MAP_PEWTER_GYM,
        "bgm": "town",
        "warps": {
            (6, 8): {"target_map": "Pewter City", "target_x": 9, "target_y": 12}
        },
        "trainers": ["camper_liam", "gym_leader_brock"]
    },
    "Cerulean Gym": {
        "grid": MAP_CERULEAN_GYM,
        "bgm": "town",
        "warps": {
            (6, 8): {"target_map": "Cerulean City", "target_x": 9, "target_y": 12}
        },
        "trainers": ["swimmer_luis", "gym_leader_misty"]
    },
    "Bill's Cottage": {
        "grid": MAP_BILLS_COTTAGE,
        "bgm": "town",
        "warps": {
            (6, 6): {"target_map": "Route 24", "target_x": 20, "target_y": 1}
        },
        "npcs": [
            {"name": "Bill", "x": 6, "y": 3, "dir": Direction.DOWN, "is_bill": True, "dialog": "Yeeha! I'm Bill the PokéManiac! I invented the PC Storage Box System! Thanks for stopping by my Sea Cottage!"}
        ]
    },
    "Museum": {
        "grid": MAP_MUSEUM,
        "bgm": "town",
        "warps": {
            (6, 6): {"target_map": "Pewter City", "target_x": 21, "target_y": 12}
        },
        "npcs": [
            {"name": "Museum Scientist", "x": 6, "y": 3, "dir": Direction.DOWN, "dialog": "We have authentic Moon Stone meteorites and ancient Aerodactyl fossils on display!"}
        ]
    },
    "Route 5": {
        "grid": MAP_ROUTE_5,
        "bgm": "town",
        "encounter_zone": "Route 5",
        "warps": {
            (12, 0): {"target_map": "Cerulean City", "target_x": 12, "target_y": 22},
            (13, 0): {"target_map": "Cerulean City", "target_x": 13, "target_y": 22},
            (14, 0): {"target_map": "Cerulean City", "target_x": 14, "target_y": 22},
            (15, 0): {"target_map": "Cerulean City", "target_x": 15, "target_y": 22},
            (12, 23): {"target_map": "Saffron City", "target_x": 14, "target_y": 1},
            (13, 23): {"target_map": "Saffron City", "target_x": 15, "target_y": 1},
            (14, 23): {"target_map": "Saffron City", "target_x": 16, "target_y": 1},
            (15, 23): {"target_map": "Saffron City", "target_x": 17, "target_y": 1}
        },
        "signs": {
            (3, 7): "Route 5 - North to Cerulean City, South to Saffron City & Underground Path."
        },
        "ground_items": [
            {"id": "route5_superpotion", "x": 3, "y": 20, "item": "Super Potion", "count": 2}
        ]
    },
    "Route 6": {
        "grid": MAP_ROUTE_6,
        "bgm": "town",
        "encounter_zone": "Route 6",
        "warps": {
            (12, 0): {"target_map": "Saffron City", "target_x": 14, "target_y": 30},
            (13, 0): {"target_map": "Saffron City", "target_x": 15, "target_y": 30},
            (14, 0): {"target_map": "Saffron City", "target_x": 16, "target_y": 30},
            (15, 0): {"target_map": "Saffron City", "target_x": 17, "target_y": 30},
            (12, 23): {"target_map": "Vermilion City", "target_x": 14, "target_y": 1},
            (13, 23): {"target_map": "Vermilion City", "target_x": 15, "target_y": 1},
            (14, 23): {"target_map": "Vermilion City", "target_x": 16, "target_y": 1},
            (15, 23): {"target_map": "Vermilion City", "target_x": 17, "target_y": 1}
        },
        "trainers": ["camper_jeff"],
        "signs": {
            (3, 11): "Route 6 - North to Saffron City, South to Vermilion Port."
        },
        "ground_items": [
            {"id": "route6_greatball", "x": 17, "y": 19, "item": "Great Ball", "count": 3}
        ]
    },
    "Vermilion City": {
        "grid": MAP_VERMILION_CITY,
        "bgm": "town",
        "encounter_zone": "Vermilion City",
        "warps": {
            (14, 0): {"target_map": "Route 6", "target_x": 14, "target_y": 22},
            (15, 0): {"target_map": "Route 6", "target_x": 15, "target_y": 22},
            (16, 0): {"target_map": "Route 6", "target_x": 16, "target_y": 22},
            (17, 0): {"target_map": "Route 6", "target_x": 17, "target_y": 22},
            (6, 4): {"target_map": "Pokecenter", "target_x": 6, "target_y": 6},
            (24, 4): {"target_map": "Mart", "target_x": 6, "target_y": 5},
            (9, 11): {"target_map": "Vermilion Gym", "target_x": 6, "target_y": 8},
            (14, 23): {"target_map": "S.S. Anne", "target_x": 14, "target_y": 18},
            (15, 23): {"target_map": "S.S. Anne", "target_x": 15, "target_y": 18},
            (31, 11): {"target_map": "Route 11", "target_x": 1, "target_y": 9},
            (31, 12): {"target_map": "Route 11", "target_x": 1, "target_y": 9},
            (31, 13): {"target_map": "Route 11", "target_x": 1, "target_y": 10},
            (31, 14): {"target_map": "Route 11", "target_x": 1, "target_y": 10}
        },
        "trainers": ["sailor_eddie"],
        "npcs": [
            {"name": "Fishing Guru", "x": 18, "y": 9, "dir": Direction.DOWN, "dialog": "I love fishing in the sea! Cast your lines off the pier or board the luxury cruise liner S.S. Anne!"},
            {"name": "Electrician Sparky", "x": 12, "y": 9, "dir": Direction.RIGHT, "quest_id": "sparky_electric_charge", "dialog": "Zzzzt! Our generators need electric charge samples! Catch a Pikachu, Voltorb, Magnemite, or Electabuzz! (Reward: $2000, Thunder Stone, 3x Ultra Ball)"},
            {"name": "Old Fisherman Barny", "x": 22, "y": 15, "dir": Direction.DOWN, "quest_id": "sea_fisherman_harvest", "dialog": "The ocean tides bring great bounties! Catch 3 Water-type Pokémon from rivers or seas! (Reward: $2200, Water Stone, 4x Great Ball)"}
        ],
        "signs": {
            (3, 6): "Vermilion City - The Port of Exquisite Sunsets",
            (24, 6): "Vermilion PokéMart",
            (6, 12): "Vermilion Gym - Leader: Lt. Surge (The Lightning American!)",
            (24, 12): "S.S. Anne Harbor Pier - Luxury World Cruise"
        },
        "ground_items": [
            {"id": "vermilion_thunderstone", "x": 6, "y": 17, "item": "Thunder Stone", "count": 1},
            {"id": "vermilion_superpotion", "x": 18, "y": 17, "item": "Super Potion", "count": 2}
        ]
    },
    "Vermilion Gym": {
        "grid": MAP_VERMILION_GYM,
        "bgm": "town",
        "warps": {
            (6, 8): {"target_map": "Vermilion City", "target_x": 9, "target_y": 12}
        },
        "trainers": ["rocker_gene", "gym_leader_surge"]
    },
    "S.S. Anne": {
        "grid": MAP_SS_ANNE,
        "bgm": "town",
        "warps": {
            (14, 19): {"target_map": "Vermilion City", "target_x": 14, "target_y": 22},
            (15, 19): {"target_map": "Vermilion City", "target_x": 15, "target_y": 22}
        },
        "trainers": ["sailor_dwayne", "gentleman_thomas"],
        "npcs": [
            {"name": "Captain", "x": 14, "y": 4, "dir": Direction.DOWN, "dialog": "Ahoy matey! Welcome to the Captain's Bridge! Here, take good care of your Pokémon during our voyage!"}
        ],
        "ground_items": [
            {"id": "ssanne_nugget", "x": 6, "y": 10, "item": "Nugget", "count": 1},
            {"id": "ssanne_candy", "x": 20, "y": 10, "item": "Rare Candy", "count": 1}
        ]
    },
    "Route 11": {
        "grid": MAP_ROUTE_11,
        "bgm": "town",
        "encounter_zone": "Route 11",
        "warps": {
            (0, 8): {"target_map": "Vermilion City", "target_x": 30, "target_y": 12},
            (0, 9): {"target_map": "Vermilion City", "target_x": 30, "target_y": 12},
            (0, 10): {"target_map": "Vermilion City", "target_x": 30, "target_y": 13},
            (0, 11): {"target_map": "Vermilion City", "target_x": 30, "target_y": 13},
            (23, 7): {"target_map": "Diglett's Cave", "target_x": 12, "target_y": 22},
            (31, 8): {"target_map": "Route 12", "target_x": 9, "target_y": 10},
            (31, 9): {"target_map": "Route 12", "target_x": 10, "target_y": 10},
            (31, 10): {"target_map": "Route 12", "target_x": 10, "target_y": 11},
            (31, 11): {"target_map": "Route 12", "target_x": 11, "target_y": 11}
        },
        "trainers": ["engineer_bernie"],
        "signs": {
            (3, 7): "Route 11 - Connecting Vermilion City and Silence Bridge.",
            (27, 7): "Diglett's Cave Entrance - Subterranean Tunnel Pass"
        },
        "ground_items": [
            {"id": "route11_ultraball", "x": 3, "y": 15, "item": "Ultra Ball", "count": 3},
            {"id": "route11_candy", "x": 14, "y": 15, "item": "Rare Candy", "count": 1}
        ]
    },
    "Diglett's Cave": {
        "grid": MAP_DIGLETTS_CAVE,
        "bgm": "town",
        "encounter_zone": "Diglett's Cave",
        "warps": {
            (12, 23): {"target_map": "Route 11", "target_x": 23, "target_y": 8},
            (13, 23): {"target_map": "Route 11", "target_x": 23, "target_y": 8},
            (12, 0): {"target_map": "Viridian City", "target_x": 6, "target_y": 18},
            (13, 0): {"target_map": "Viridian City", "target_x": 7, "target_y": 18}
        },
        "signs": {
            (12, 10): "Diglett's Cave - Underground Mountain Highway"
        },
        "ground_items": [
            {"id": "diglett_nugget", "x": 3, "y": 21, "item": "Nugget", "count": 1},
            {"id": "diglett_escaperope", "x": 19, "y": 21, "item": "Escape Rope", "count": 2}
        ]
    },
    "Route 7": {
        "grid": MAP_ROUTE_7,
        "bgm": "town",
        "encounter_zone": "Route 7",
        "warps": {
            (0, 7): {"target_map": "Celadon City", "target_x": 30, "target_y": 11},
            (0, 8): {"target_map": "Celadon City", "target_x": 30, "target_y": 12},
            (0, 9): {"target_map": "Celadon City", "target_x": 30, "target_y": 13},
            (23, 7): {"target_map": "Saffron City", "target_x": 1, "target_y": 15},
            (23, 8): {"target_map": "Saffron City", "target_x": 1, "target_y": 16},
            (23, 9): {"target_map": "Saffron City", "target_x": 1, "target_y": 16}
        },
        "signs": {
            (3, 10): "Route 7 - Connecting Saffron City and Celadon City.",
            (20, 10): "Celadon City Ahead!"
        },
        "ground_items": [
            {"id": "route7_firestone", "x": 3, "y": 13, "item": "Fire Stone", "count": 1}
        ]
    },
    "Route 8": {
        "grid": MAP_ROUTE_8,
        "bgm": "town",
        "encounter_zone": "Route 8",
        "warps": {
            (0, 7): {"target_map": "Saffron City", "target_x": 30, "target_y": 15},
            (0, 8): {"target_map": "Saffron City", "target_x": 30, "target_y": 16},
            (0, 9): {"target_map": "Saffron City", "target_x": 30, "target_y": 16},
            (0, 10): {"target_map": "Saffron City", "target_x": 30, "target_y": 17},
            (31, 7): {"target_map": "Lavender Town", "target_x": 1, "target_y": 11},
            (31, 8): {"target_map": "Lavender Town", "target_x": 1, "target_y": 11},
            (31, 9): {"target_map": "Lavender Town", "target_x": 1, "target_y": 12},
            (31, 10): {"target_map": "Lavender Town", "target_x": 1, "target_y": 13}
        },
        "trainers": ["gambler_rich", "super_nerd_glenn"],
        "signs": {
            (3, 11): "Route 8 - Connecting Saffron City and Lavender Town.",
            (27, 11): "Lavender Town East Ahead!"
        },
        "ground_items": [
            {"id": "route8_maxpotion", "x": 3, "y": 14, "item": "Max Potion", "count": 1},
            {"id": "route8_candy", "x": 15, "y": 14, "item": "Rare Candy", "count": 1}
        ]
    },
    "Celadon City": {
        "grid": MAP_CELADON_CITY,
        "bgm": "town",
        "warps": {
            (6, 4): {"target_map": "Pokecenter", "target_x": 6, "target_y": 6},
            (28, 4): {"target_map": "Mart", "target_x": 6, "target_y": 5},
            (9, 18): {"target_map": "Celadon Gym", "target_x": 6, "target_y": 7},
            (31, 10): {"target_map": "Route 7", "target_x": 1, "target_y": 8},
            (31, 11): {"target_map": "Route 7", "target_x": 1, "target_y": 8},
            (31, 12): {"target_map": "Route 7", "target_x": 1, "target_y": 9},
            (31, 13): {"target_map": "Route 7", "target_x": 1, "target_y": 9}
        },
        "trainers": ["lass_kay"],
        "npcs": [
            {"name": "Game Corner Clerk", "x": 16, "y": 9, "dir": Direction.DOWN, "dialog": "Welcome to Celadon City! Visit our multi-floor Department Store or test your team at Erika's Botanical Gym!"},
            {"name": "Stone Connoisseur", "x": 20, "y": 12, "dir": Direction.DOWN, "quest_id": "celadon_evolution_mastery", "dialog": "Evolution stones hold the essence of nature! Evolve any Pokémon using an Evolution Stone! (Reward: $3500, 3x Rare Candy, Nugget)"}
        ],
        "signs": {
            (3, 6): "Celadon City - The City of Rainbow Dreams",
            (24, 6): "Celadon Mega Department Store - All Evolution Stones & Battle Goods!",
            (6, 18): "Celadon Gym - Leader: Erika (The Nature-Loving Princess!)"
        },
        "ground_items": [
            {"id": "celadon_leafstone", "x": 6, "y": 19, "item": "Leaf Stone", "count": 1},
            {"id": "celadon_waterstone", "x": 23, "y": 19, "item": "Water Stone", "count": 1}
        ]
    },
    "Celadon Gym": {
        "grid": MAP_CELADON_GYM,
        "bgm": "town",
        "warps": {
            (6, 8): {"target_map": "Celadon City", "target_x": 9, "target_y": 19}
        },
        "trainers": ["beauty_tamia", "gym_leader_erika"]
    },
    "Saffron City": {
        "grid": MAP_SAFFRON_CITY,
        "bgm": "town",
        "warps": {
            (14, 0): {"target_map": "Route 5", "target_x": 13, "target_y": 22},
            (15, 0): {"target_map": "Route 5", "target_x": 14, "target_y": 22},
            (16, 0): {"target_map": "Route 5", "target_x": 15, "target_y": 22},
            (17, 0): {"target_map": "Route 5", "target_x": 15, "target_y": 22},
            (14, 31): {"target_map": "Route 6", "target_x": 13, "target_y": 1},
            (15, 31): {"target_map": "Route 6", "target_x": 14, "target_y": 1},
            (16, 31): {"target_map": "Route 6", "target_x": 15, "target_y": 1},
            (17, 31): {"target_map": "Route 6", "target_x": 15, "target_y": 1},
            (0, 14): {"target_map": "Route 7", "target_x": 22, "target_y": 8},
            (0, 15): {"target_map": "Route 7", "target_x": 22, "target_y": 8},
            (0, 16): {"target_map": "Route 7", "target_x": 22, "target_y": 9},
            (0, 17): {"target_map": "Route 7", "target_x": 22, "target_y": 9},
            (31, 14): {"target_map": "Route 8", "target_x": 1, "target_y": 8},
            (31, 15): {"target_map": "Route 8", "target_x": 1, "target_y": 9},
            (31, 16): {"target_map": "Route 8", "target_x": 1, "target_y": 9},
            (31, 17): {"target_map": "Route 8", "target_x": 1, "target_y": 10},
            (6, 4): {"target_map": "Pokecenter", "target_x": 6, "target_y": 6},
            (28, 4): {"target_map": "Mart", "target_x": 6, "target_y": 5},
            (17, 16): {"target_map": "Silph Co.", "target_x": 14, "target_y": 8},
            (25, 21): {"target_map": "Saffron Gym", "target_x": 7, "target_y": 9}
        },
        "trainers": ["blackbelt_nob"],
        "npcs": [
            {"name": "Saffron Guide", "x": 16, "y": 8, "dir": Direction.DOWN, "dialog": "Welcome to Saffron City! Silph Co. headquarters is located in the center of the metropolis, and Sabrina's Gym is to the south!"},
            {"name": "Black Belt Kenji", "x": 12, "y": 21, "dir": Direction.DOWN, "quest_id": "karate_spirit", "dialog": "Hi-yah! True mastery comes through hard training! Defeat 4 Fighting or Rock-type Pokémon in battle! (Reward: $3000, Move Reroll Disk, 2x Max Potion)"}
        ],
        "signs": {
            (3, 6): "Saffron City - Shining Golden Metropolis Crossroads",
            (24, 6): "Saffron PokéMart",
            (15, 17): "Silph Co. Headquarters - Cutting-Edge Technology & Master Balls",
            (24, 23): "Saffron Gym - Leader: Sabrina (Master of Psychic Pokémon!)"
        },
        "ground_items": [
            {"id": "saffron_ultraball", "x": 6, "y": 27, "item": "Ultra Ball", "count": 3},
            {"id": "saffron_candy", "x": 24, "y": 27, "item": "Rare Candy", "count": 2}
        ]
    },
    "Silph Co.": {
        "grid": MAP_SILPH_CO,
        "bgm": "town",
        "warps": {
            (14, 8): {"target_map": "Saffron City", "target_x": 17, "target_y": 17}
        },
        "npcs": [
            {"name": "Silph President", "x": 14, "y": 3, "dir": Direction.DOWN, "dialog": "Welcome to Silph Co. Corporate Headquarters! We develop Master Balls, Silph Scopes, and state-of-the-art battle equipment for trainers across Kanto!"},
            {"name": "Lead Scientist", "x": 6, "y": 5, "dir": Direction.RIGHT, "dialog": "Our research laboratory engineered the Master Ball—a prototype ball with a 100% capture rate on any Pokémon!"},
            {"name": "Silph Engineer", "x": 21, "y": 5, "dir": Direction.LEFT, "dialog": "We manage the wireless communications network connecting Pokémon Centers and PC Storage boxes throughout Kanto."}
        ],
        "signs": {
            (14, 1): "Silph Co. Central Server Mainframe - Highly Confidential"
        },
        "ground_items": [
            {"id": "silph_masterball", "x": 3, "y": 7, "item": "Master Ball", "count": 1},
            {"id": "silph_candy", "x": 24, "y": 7, "item": "Rare Candy", "count": 2}
        ]
    },
    "Saffron Gym": {
        "grid": MAP_SAFFRON_GYM,
        "bgm": "town",
        "warps": {
            (7, 10): {"target_map": "Saffron City", "target_x": 25, "target_y": 22}
        },
        "trainers": ["psychic_johan", "gym_leader_sabrina"]
    },
    "Route 12": {
        "grid": MAP_ROUTE_12,
        "bgm": "town",
        "encounter_zone": "Route 12",
        "warps": {
            (9, 0): {"target_map": "Lavender Town", "target_x": 13, "target_y": 22},
            (10, 0): {"target_map": "Lavender Town", "target_x": 14, "target_y": 22},
            (11, 0): {"target_map": "Lavender Town", "target_x": 15, "target_y": 22},
            (9, 35): {"target_map": "Fuchsia City", "target_x": 28, "target_y": 1},
            (10, 35): {"target_map": "Fuchsia City", "target_x": 29, "target_y": 1},
            (11, 35): {"target_map": "Fuchsia City", "target_x": 30, "target_y": 1}
        },
        "trainers": ["bird_keeper_rod"],
        "signs": {
            (3, 33): "Route 12 - Silence Bridge. North to Lavender, South to Fuchsia City."
        },
        "ground_items": [
            {"id": "route12_snorlax_candy", "x": 8, "y": 11, "item": "Rare Candy", "count": 2}
        ]
    },
    "Fuchsia City": {
        "grid": MAP_FUCHSIA_CITY,
        "bgm": "town",
        "warps": {
            (28, 0): {"target_map": "Route 12", "target_x": 10, "target_y": 34},
            (29, 0): {"target_map": "Route 12", "target_x": 10, "target_y": 34},
            (30, 0): {"target_map": "Route 12", "target_x": 11, "target_y": 34},
            (4, 0): {"target_map": "Safari Zone", "target_x": 15, "target_y": 28},
            (5, 0): {"target_map": "Safari Zone", "target_x": 16, "target_y": 28},
            (6, 0): {"target_map": "Safari Zone", "target_x": 16, "target_y": 28},
            (7, 0): {"target_map": "Safari Zone", "target_x": 17, "target_y": 28},
            (13, 4): {"target_map": "Pokecenter", "target_x": 6, "target_y": 6},
            (21, 4): {"target_map": "Mart", "target_x": 6, "target_y": 5},
            (13, 17): {"target_map": "Fuchsia Gym", "target_x": 6, "target_y": 7}
        },
        "npcs": [
            {"name": "Safari Warden", "x": 16, "y": 9, "dir": Direction.DOWN, "dialog": "Welcome to Fuchsia City! North gate leads straight to the grand Safari Zone Sanctuary!"},
            {"name": "Ninja Scout", "x": 14, "y": 12, "dir": Direction.DOWN, "quest_id": "ninja_toxic_challenge", "dialog": "A shinobi must conquer toxic hazards! Defeat 4 Poison-type Pokémon in battle! (Reward: $4000, 2x Max Revive, 5x Ultra Ball)"},
            {"name": "Safari Ranger", "x": 8, "y": 9, "dir": Direction.RIGHT, "quest_id": "safari_wildlife_reserve", "dialog": "The Safari Zone sanctuary protects majestic creatures! Spot and catch a rare savanna Pokémon (Dratini, Kangaskhan, Tauros, Scyther, or Pinsir)! (Reward: $5000, Master Ball, 2x Rare Candy)"}
        ],
        "signs": {
            (7, 6): "Fuchsia City - Behold! It's Passion Pink!",
            (22, 6): "Fuchsia PokéMart",
            (6, 17): "Fuchsia Gym - Leader: Koga (The Poisonous Ninja Master!)"
        },
        "ground_items": [
            {"id": "fuchsia_maxpotion", "x": 6, "y": 18, "item": "Max Potion", "count": 2},
            {"id": "fuchsia_candy", "x": 24, "y": 18, "item": "Rare Candy", "count": 1}
        ]
    },
    "Fuchsia Gym": {
        "grid": MAP_FUCHSIA_GYM,
        "bgm": "town",
        "warps": {
            (6, 8): {"target_map": "Fuchsia City", "target_x": 13, "target_y": 18}
        },
        "trainers": ["juggler_nate", "gym_leader_koga"]
    },
    "Victory Road": {
        "grid": MAP_VICTORY_ROAD,
        "bgm": "town",
        "encounter_zone": "Victory Road",
        "warps": {
            (15, 25): {"target_map": "Route 22", "target_x": 9, "target_y": 8},
            (16, 25): {"target_map": "Route 22", "target_x": 9, "target_y": 8},
            (15, 0): {"target_map": "Indigo Plateau", "target_x": 13, "target_y": 22},
            (16, 0): {"target_map": "Indigo Plateau", "target_x": 14, "target_y": 22}
        },
        "trainers": ["cooltrainer_sam", "cooltrainer_brooke"],
        "signs": {
            (15, 23): "Victory Road - Final Trial of the Pokémon League!"
        },
        "ground_items": [
            {"id": "victory_maxrevive", "x": 3, "y": 22, "item": "Max Revive", "count": 2},
            {"id": "victory_candy", "x": 28, "y": 22, "item": "Rare Candy", "count": 3}
        ]
    },
    "Indigo Plateau": {
        "grid": MAP_INDIGO_PLATEAU,
        "bgm": "town",
        "encounter_zone": "Indigo Plateau",
        "warps": {
            (13, 23): {"target_map": "Victory Road", "target_x": 15, "target_y": 1},
            (14, 23): {"target_map": "Victory Road", "target_x": 16, "target_y": 1}
        },
        "trainers": ["champion_blue"],
        "npcs": [
            {"name": "League Guide", "x": 6, "y": 20, "dir": Direction.RIGHT, "dialog": "Welcome to the Indigo Plateau Pokémon League! Face Champion Blue on the throne to claim the Championship!"}
        ],
        "signs": {
            (13, 10): "Indigo Plateau - Supreme Pokémon League Headquarters"
        }
    },
    "Cerulean Cave": {
        "grid": MAP_CERULEAN_CAVE,
        "bgm": "town",
        "encounter_zone": "Cerulean Cave",
        "warps": {
            (12, 21): {"target_map": "Cerulean City", "target_x": 4, "target_y": 1},
            (13, 21): {"target_map": "Cerulean City", "target_x": 4, "target_y": 1}
        },
        "signs": {
            (12, 19): "Cerulean Cave - Unexplored Subterranean Depths. Danger!"
        },
        "ground_items": [
            {"id": "ceruleancave_ultraball", "x": 6, "y": 19, "item": "Ultra Ball", "count": 5},
            {"id": "ceruleancave_candy", "x": 19, "y": 19, "item": "Rare Candy", "count": 3}
        ]
    }
}
