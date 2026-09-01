"""
encounters_data.py - Wild Pokemon encounter tables by zone and biome prop.
"""

WILD_ENCOUNTERS = {
    "Route 1": [
        {"species": "Pidgey", "min_lvl": 2, "max_lvl": 5, "weight": 30},
        {"species": "Rattata", "min_lvl": 2, "max_lvl": 4, "weight": 25},
        {"species": "Caterpie", "min_lvl": 2, "max_lvl": 4, "weight": 15},
        {"species": "Weedle", "min_lvl": 2, "max_lvl": 4, "weight": 15},
        {"species": "Pikachu", "min_lvl": 3, "max_lvl": 5, "weight": 10},
        {"species": "Mankey", "min_lvl": 3, "max_lvl": 5, "weight": 5}
    ],
    "Route 22": [
        {"species": "Rattata", "min_lvl": 3, "max_lvl": 5, "weight": 25},
        {"species": "Spearow", "min_lvl": 3, "max_lvl": 6, "weight": 25},
        {"species": "Nidoran-F", "min_lvl": 3, "max_lvl": 6, "weight": 15},
        {"species": "Nidoran-M", "min_lvl": 3, "max_lvl": 6, "weight": 15},
        {"species": "Mankey", "min_lvl": 3, "max_lvl": 6, "weight": 12},
        {"species": "Poliwag", "min_lvl": 4, "max_lvl": 7, "weight": 8}
    ],
    "Viridian Forest": [
        {"species": "Caterpie", "min_lvl": 4, "max_lvl": 7, "weight": 18},
        {"species": "Weedle", "min_lvl": 4, "max_lvl": 7, "weight": 18},
        {"species": "Pikachu", "min_lvl": 5, "max_lvl": 9, "weight": 15},
        {"species": "Oddish", "min_lvl": 5, "max_lvl": 8, "weight": 10},
        {"species": "Bellsprout", "min_lvl": 5, "max_lvl": 8, "weight": 10},
        {"species": "Gastly", "min_lvl": 6, "max_lvl": 10, "weight": 8},
        {"species": "Geodude", "min_lvl": 7, "max_lvl": 11, "weight": 7},
        {"species": "Eevee", "min_lvl": 8, "max_lvl": 12, "weight": 6},
        {"species": "Scyther", "min_lvl": 9, "max_lvl": 13, "weight": 4},
        {"species": "Pinsir", "min_lvl": 9, "max_lvl": 13, "weight": 4}
    ],
    "Route 3": [
        {"species": "Pidgey", "min_lvl": 7, "max_lvl": 11, "weight": 25},
        {"species": "Spearow", "min_lvl": 8, "max_lvl": 12, "weight": 25},
        {"species": "Ekans", "min_lvl": 8, "max_lvl": 11, "weight": 15},
        {"species": "Sandshrew", "min_lvl": 8, "max_lvl": 11, "weight": 15},
        {"species": "Jigglypuff", "min_lvl": 8, "max_lvl": 12, "weight": 12},
        {"species": "Mankey", "min_lvl": 9, "max_lvl": 12, "weight": 8}
    ],
    "Mt. Moon": [
        {"species": "Zubat", "min_lvl": 9, "max_lvl": 13, "weight": 35},
        {"species": "Geodude", "min_lvl": 9, "max_lvl": 13, "weight": 25},
        {"species": "Paras", "min_lvl": 9, "max_lvl": 12, "weight": 15},
        {"species": "Clefairy", "min_lvl": 10, "max_lvl": 14, "weight": 12},
        {"species": "Sandshrew", "min_lvl": 10, "max_lvl": 13, "weight": 8},
        {"species": "Onix", "min_lvl": 11, "max_lvl": 15, "weight": 5}
    ],
    "Route 4": [
        {"species": "Rattata", "min_lvl": 11, "max_lvl": 14, "weight": 25},
        {"species": "Spearow", "min_lvl": 11, "max_lvl": 15, "weight": 25},
        {"species": "Ekans", "min_lvl": 12, "max_lvl": 15, "weight": 20},
        {"species": "Sandshrew", "min_lvl": 12, "max_lvl": 15, "weight": 15},
        {"species": "Mankey", "min_lvl": 12, "max_lvl": 16, "weight": 10},
        {"species": "Psyduck", "min_lvl": 12, "max_lvl": 16, "weight": 5}
    ],
    "Route 24": [
        {"species": "Bellsprout", "min_lvl": 13, "max_lvl": 17, "weight": 25},
        {"species": "Oddish", "min_lvl": 13, "max_lvl": 17, "weight": 25},
        {"species": "Pidgey", "min_lvl": 14, "max_lvl": 17, "weight": 20},
        {"species": "Abra", "min_lvl": 13, "max_lvl": 16, "weight": 15},
        {"species": "Venonat", "min_lvl": 14, "max_lvl": 17, "weight": 10},
        {"species": "Squirtle", "min_lvl": 12, "max_lvl": 16, "weight": 5}
    ],
    "Route 21": [
        {"species": "Tentacool", "min_lvl": 16, "max_lvl": 22, "weight": 35},
        {"species": "Magikarp", "min_lvl": 15, "max_lvl": 20, "weight": 30},
        {"species": "Goldeen", "min_lvl": 16, "max_lvl": 21, "weight": 15},
        {"species": "Shellder", "min_lvl": 17, "max_lvl": 22, "weight": 10},
        {"species": "Staryu", "min_lvl": 17, "max_lvl": 22, "weight": 7},
        {"species": "Lapras", "min_lvl": 18, "max_lvl": 23, "weight": 2},
        {"species": "Dratini", "min_lvl": 16, "max_lvl": 21, "weight": 1}
    ],
    "Cinnabar Island": [
        {"species": "Growlithe", "min_lvl": 20, "max_lvl": 26, "weight": 25},
        {"species": "Vulpix", "min_lvl": 20, "max_lvl": 26, "weight": 25},
        {"species": "Ponyta", "min_lvl": 21, "max_lvl": 26, "weight": 20},
        {"species": "Koffing", "min_lvl": 20, "max_lvl": 25, "weight": 15},
        {"species": "Grimer", "min_lvl": 20, "max_lvl": 25, "weight": 10},
        {"species": "Magmar", "min_lvl": 22, "max_lvl": 27, "weight": 5}
    ],
    "Route 9": [
        {"species": "Rattata", "min_lvl": 14, "max_lvl": 17, "weight": 25},
        {"species": "Spearow", "min_lvl": 14, "max_lvl": 18, "weight": 25},
        {"species": "Ekans", "min_lvl": 15, "max_lvl": 18, "weight": 20},
        {"species": "Sandshrew", "min_lvl": 15, "max_lvl": 18, "weight": 15},
        {"species": "Machop", "min_lvl": 15, "max_lvl": 19, "weight": 10},
        {"species": "Geodude", "min_lvl": 15, "max_lvl": 19, "weight": 5}
    ],
    "Lavender Town": [
        {"species": "Pidgeotto", "min_lvl": 18, "max_lvl": 22, "weight": 30},
        {"species": "Rattata", "min_lvl": 17, "max_lvl": 21, "weight": 30},
        {"species": "Vulpix", "min_lvl": 18, "max_lvl": 22, "weight": 20},
        {"species": "Gastly", "min_lvl": 18, "max_lvl": 22, "weight": 20}
    ],
    "Pokémon Tower": [
        {"species": "Gastly", "min_lvl": 18, "max_lvl": 24, "weight": 45},
        {"species": "Haunter", "min_lvl": 22, "max_lvl": 26, "weight": 20},
        {"species": "Cubone", "min_lvl": 19, "max_lvl": 24, "weight": 20},
        {"species": "Drowzee", "min_lvl": 19, "max_lvl": 23, "weight": 10},
        {"species": "Hypno", "min_lvl": 23, "max_lvl": 27, "weight": 5}
    ],
    "Power Plant": [
        {"species": "Voltorb", "min_lvl": 21, "max_lvl": 26, "weight": 30},
        {"species": "Magnemite", "min_lvl": 21, "max_lvl": 26, "weight": 30},
        {"species": "Pikachu", "min_lvl": 22, "max_lvl": 26, "weight": 15},
        {"species": "Electrode", "min_lvl": 25, "max_lvl": 30, "weight": 10},
        {"species": "Magneton", "min_lvl": 25, "max_lvl": 30, "weight": 10},
        {"species": "Electabuzz", "min_lvl": 26, "max_lvl": 32, "weight": 5}
    ],
    "Safari Zone": [
        {"species": "Nidorino", "min_lvl": 22, "max_lvl": 27, "weight": 15},
        {"species": "Nidorina", "min_lvl": 22, "max_lvl": 27, "weight": 15},
        {"species": "Rhyhorn", "min_lvl": 24, "max_lvl": 28, "weight": 15},
        {"species": "Exeggcute", "min_lvl": 23, "max_lvl": 27, "weight": 12},
        {"species": "Doduo", "min_lvl": 23, "max_lvl": 27, "weight": 12},
        {"species": "Kangaskhan", "min_lvl": 25, "max_lvl": 30, "weight": 8},
        {"species": "Tauros", "min_lvl": 25, "max_lvl": 30, "weight": 8},
        {"species": "Scyther", "min_lvl": 25, "max_lvl": 30, "weight": 6},
        {"species": "Pinsir", "min_lvl": 25, "max_lvl": 30, "weight": 6},
        {"species": "Chansey", "min_lvl": 26, "max_lvl": 30, "weight": 2},
        {"species": "Dratini", "min_lvl": 20, "max_lvl": 25, "weight": 1}
    ],
    "Seafoam Islands": [
        {"species": "Zubat", "min_lvl": 20, "max_lvl": 26, "weight": 25},
        {"species": "Golbat", "min_lvl": 24, "max_lvl": 28, "weight": 15},
        {"species": "Psyduck", "min_lvl": 22, "max_lvl": 27, "weight": 20},
        {"species": "Slowpoke", "min_lvl": 22, "max_lvl": 27, "weight": 15},
        {"species": "Seel", "min_lvl": 23, "max_lvl": 28, "weight": 15},
        {"species": "Shellder", "min_lvl": 23, "max_lvl": 28, "weight": 5},
        {"species": "Dewgong", "min_lvl": 28, "max_lvl": 32, "weight": 3},
        {"species": "Jynx", "min_lvl": 26, "max_lvl": 30, "weight": 2}
    ],
    "Route 5": [
        {"species": "Pidgey", "min_lvl": 13, "max_lvl": 16, "weight": 30},
        {"species": "Meowth", "min_lvl": 13, "max_lvl": 17, "weight": 25},
        {"species": "Oddish", "min_lvl": 13, "max_lvl": 16, "weight": 20},
        {"species": "Bellsprout", "min_lvl": 13, "max_lvl": 16, "weight": 20},
        {"species": "Mankey", "min_lvl": 14, "max_lvl": 17, "weight": 5}
    ],
    "Route 6": [
        {"species": "Pidgey", "min_lvl": 14, "max_lvl": 17, "weight": 30},
        {"species": "Meowth", "min_lvl": 14, "max_lvl": 17, "weight": 25},
        {"species": "Psyduck", "min_lvl": 15, "max_lvl": 18, "weight": 20},
        {"species": "Bellsprout", "min_lvl": 14, "max_lvl": 17, "weight": 15},
        {"species": "Magnemite", "min_lvl": 15, "max_lvl": 18, "weight": 10}
    ],
    "Route 11": [
        {"species": "Drowzee", "min_lvl": 15, "max_lvl": 19, "weight": 30},
        {"species": "Sandshrew", "min_lvl": 15, "max_lvl": 19, "weight": 25},
        {"species": "Spearow", "min_lvl": 15, "max_lvl": 18, "weight": 25},
        {"species": "Ekans", "min_lvl": 15, "max_lvl": 19, "weight": 15},
        {"species": "Magnemite", "min_lvl": 16, "max_lvl": 19, "weight": 5}
    ],
    "Diglett's Cave": [
        {"species": "Diglett", "min_lvl": 16, "max_lvl": 22, "weight": 85},
        {"species": "Dugtrio", "min_lvl": 28, "max_lvl": 31, "weight": 15}
    ],
    "Route 7": [
        {"species": "Pidgeotto", "min_lvl": 19, "max_lvl": 23, "weight": 30},
        {"species": "Vulpix", "min_lvl": 18, "max_lvl": 22, "weight": 25},
        {"species": "Growlithe", "min_lvl": 18, "max_lvl": 22, "weight": 25},
        {"species": "Meowth", "min_lvl": 18, "max_lvl": 22, "weight": 15},
        {"species": "Abra", "min_lvl": 17, "max_lvl": 21, "weight": 5}
    ],
    "Route 8": [
        {"species": "Pidgeotto", "min_lvl": 20, "max_lvl": 24, "weight": 25},
        {"species": "Growlithe", "min_lvl": 19, "max_lvl": 23, "weight": 25},
        {"species": "Vulpix", "min_lvl": 19, "max_lvl": 23, "weight": 25},
        {"species": "Kadabra", "min_lvl": 21, "max_lvl": 25, "weight": 15},
        {"species": "Ekans", "min_lvl": 19, "max_lvl": 23, "weight": 10}
    ],
    "Route 12": [
        {"species": "Venonat", "min_lvl": 23, "max_lvl": 27, "weight": 30},
        {"species": "Pidgeotto", "min_lvl": 23, "max_lvl": 28, "weight": 25},
        {"species": "Slowpoke", "min_lvl": 24, "max_lvl": 28, "weight": 20},
        {"species": "Gloom", "min_lvl": 24, "max_lvl": 28, "weight": 15},
        {"species": "Snorlax", "min_lvl": 30, "max_lvl": 30, "weight": 10}
    ],
    "Victory Road": [
        {"species": "Machoke", "min_lvl": 38, "max_lvl": 44, "weight": 25},
        {"species": "Graveler", "min_lvl": 38, "max_lvl": 44, "weight": 25},
        {"species": "Onix", "min_lvl": 39, "max_lvl": 45, "weight": 20},
        {"species": "Golbat", "min_lvl": 39, "max_lvl": 44, "weight": 15},
        {"species": "Marowak", "min_lvl": 40, "max_lvl": 45, "weight": 10},
        {"species": "Moltres", "min_lvl": 50, "max_lvl": 50, "weight": 5}
    ],
    "Indigo Plateau": [
        {"species": "Dragonair", "min_lvl": 44, "max_lvl": 50, "weight": 30},
        {"species": "Alakazam", "min_lvl": 45, "max_lvl": 52, "weight": 25},
        {"species": "Gengar", "min_lvl": 45, "max_lvl": 52, "weight": 20},
        {"species": "Lapras", "min_lvl": 46, "max_lvl": 52, "weight": 15},
        {"species": "Dragonite", "min_lvl": 52, "max_lvl": 58, "weight": 10}
    ],
    "Cerulean Cave": [
        {"species": "Raichu", "min_lvl": 52, "max_lvl": 58, "weight": 20},
        {"species": "Magneton", "min_lvl": 52, "max_lvl": 58, "weight": 20},
        {"species": "Rhydon", "min_lvl": 53, "max_lvl": 60, "weight": 20},
        {"species": "Chansey", "min_lvl": 54, "max_lvl": 60, "weight": 15},
        {"species": "Ditto", "min_lvl": 52, "max_lvl": 58, "weight": 15},
        {"species": "Mewtwo", "min_lvl": 70, "max_lvl": 70, "weight": 10}
    ]
}

# Wild Water / Sailing Encounters by Zone
WILD_WATER_ENCOUNTERS = {
    "Route 21": [
        {"species": "Tentacool", "min_lvl": 16, "max_lvl": 22, "weight": 35},
        {"species": "Magikarp", "min_lvl": 15, "max_lvl": 20, "weight": 30},
        {"species": "Goldeen", "min_lvl": 16, "max_lvl": 21, "weight": 15},
        {"species": "Shellder", "min_lvl": 17, "max_lvl": 22, "weight": 10},
        {"species": "Staryu", "min_lvl": 17, "max_lvl": 22, "weight": 7},
        {"species": "Lapras", "min_lvl": 18, "max_lvl": 23, "weight": 2},
        {"species": "Dratini", "min_lvl": 16, "max_lvl": 21, "weight": 1}
    ],
    "Vermilion City": [
        {"species": "Tentacool", "min_lvl": 15, "max_lvl": 20, "weight": 40},
        {"species": "Shellder", "min_lvl": 15, "max_lvl": 20, "weight": 30},
        {"species": "Krabby", "min_lvl": 15, "max_lvl": 20, "weight": 20},
        {"species": "Staryu", "min_lvl": 16, "max_lvl": 21, "weight": 10}
    ],
    "Route 12": [
        {"species": "Tentacool", "min_lvl": 22, "max_lvl": 27, "weight": 30},
        {"species": "Krabby", "min_lvl": 22, "max_lvl": 27, "weight": 25},
        {"species": "Kingler", "min_lvl": 26, "max_lvl": 30, "weight": 20},
        {"species": "Goldeen", "min_lvl": 22, "max_lvl": 27, "weight": 15},
        {"species": "Seaking", "min_lvl": 26, "max_lvl": 31, "weight": 10}
    ],
    "Pallet Town": [
        {"species": "Tentacool", "min_lvl": 5, "max_lvl": 10, "weight": 40},
        {"species": "Magikarp", "min_lvl": 5, "max_lvl": 10, "weight": 40},
        {"species": "Poliwag", "min_lvl": 6, "max_lvl": 10, "weight": 20}
    ],
    "Cerulean City": [
        {"species": "Psyduck", "min_lvl": 14, "max_lvl": 18, "weight": 35},
        {"species": "Goldeen", "min_lvl": 14, "max_lvl": 18, "weight": 35},
        {"species": "Poliwhirl", "min_lvl": 15, "max_lvl": 19, "weight": 20},
        {"species": "Staryu", "min_lvl": 15, "max_lvl": 19, "weight": 10}
    ],
    "Route 24": [
        {"species": "Psyduck", "min_lvl": 14, "max_lvl": 18, "weight": 30},
        {"species": "Goldeen", "min_lvl": 14, "max_lvl": 18, "weight": 30},
        {"species": "Slowpoke", "min_lvl": 14, "max_lvl": 18, "weight": 25},
        {"species": "Magikarp", "min_lvl": 12, "max_lvl": 16, "weight": 15}
    ],
    "Safari Zone": [
        {"species": "Psyduck", "min_lvl": 22, "max_lvl": 26, "weight": 25},
        {"species": "Slowpoke", "min_lvl": 22, "max_lvl": 26, "weight": 25},
        {"species": "Goldeen", "min_lvl": 23, "max_lvl": 27, "weight": 20},
        {"species": "Seaking", "min_lvl": 25, "max_lvl": 30, "weight": 15},
        {"species": "Dratini", "min_lvl": 22, "max_lvl": 26, "weight": 10},
        {"species": "Dragonair", "min_lvl": 28, "max_lvl": 33, "weight": 5}
    ],
    "Cinnabar Island": [
        {"species": "Tentacool", "min_lvl": 20, "max_lvl": 26, "weight": 35},
        {"species": "Tentacruel", "min_lvl": 26, "max_lvl": 32, "weight": 20},
        {"species": "Shellder", "min_lvl": 22, "max_lvl": 27, "weight": 20},
        {"species": "Horsea", "min_lvl": 22, "max_lvl": 27, "weight": 15},
        {"species": "Gyarados", "min_lvl": 28, "max_lvl": 34, "weight": 10}
    ]
}

# Specialized Wild Encounter Tables by Walk-Through Prop Type & Zone
WILD_PROP_ENCOUNTERS = {
    "Pallet Town": {
        "F": [
            {"species": "Butterfree", "min_lvl": 4, "max_lvl": 7, "weight": 25},
            {"species": "Oddish", "min_lvl": 3, "max_lvl": 6, "weight": 35},
            {"species": "Bellsprout", "min_lvl": 3, "max_lvl": 6, "weight": 30},
            {"species": "Pidgey", "min_lvl": 3, "max_lvl": 5, "weight": 10}
        ],
        "*": [
            {"species": "Oddish", "min_lvl": 3, "max_lvl": 6, "weight": 50},
            {"species": "Bellsprout", "min_lvl": 3, "max_lvl": 6, "weight": 50}
        ]
    },
    "Route 1": {
        "F": [
            {"species": "Butterfree", "min_lvl": 4, "max_lvl": 7, "weight": 20},
            {"species": "Oddish", "min_lvl": 3, "max_lvl": 6, "weight": 30},
            {"species": "Bellsprout", "min_lvl": 3, "max_lvl": 6, "weight": 30},
            {"species": "Pikachu", "min_lvl": 3, "max_lvl": 6, "weight": 15},
            {"species": "Clefairy", "min_lvl": 4, "max_lvl": 7, "weight": 5}
        ],
        "L": [
            {"species": "Pidgey", "min_lvl": 3, "max_lvl": 6, "weight": 35},
            {"species": "Spearow", "min_lvl": 3, "max_lvl": 6, "weight": 30},
            {"species": "Rattata", "min_lvl": 2, "max_lvl": 5, "weight": 20},
            {"species": "Mankey", "min_lvl": 3, "max_lvl": 6, "weight": 15}
        ]
    },
    "Viridian City": {
        "F": [
            {"species": "Butterfree", "min_lvl": 5, "max_lvl": 8, "weight": 30},
            {"species": "Beedrill", "min_lvl": 5, "max_lvl": 8, "weight": 25},
            {"species": "Oddish", "min_lvl": 4, "max_lvl": 7, "weight": 25},
            {"species": "Jigglypuff", "min_lvl": 5, "max_lvl": 8, "weight": 20}
        ],
        "L": [
            {"species": "Pidgey", "min_lvl": 4, "max_lvl": 7, "weight": 40},
            {"species": "Rattata", "min_lvl": 4, "max_lvl": 7, "weight": 30},
            {"species": "Spearow", "min_lvl": 4, "max_lvl": 7, "weight": 30}
        ]
    },
    "Route 22": {
        "u": [
            {"species": "Poliwag", "min_lvl": 5, "max_lvl": 8, "weight": 40},
            {"species": "Psyduck", "min_lvl": 5, "max_lvl": 8, "weight": 30},
            {"species": "Nidoran-F", "min_lvl": 4, "max_lvl": 7, "weight": 15},
            {"species": "Nidoran-M", "min_lvl": 4, "max_lvl": 7, "weight": 15}
        ],
        "r": [
            {"species": "Geodude", "min_lvl": 4, "max_lvl": 7, "weight": 35},
            {"species": "Mankey", "min_lvl": 4, "max_lvl": 7, "weight": 35},
            {"species": "Sandshrew", "min_lvl": 4, "max_lvl": 7, "weight": 30}
        ]
    },
    "Viridian Forest": {
        "F": [
            {"species": "Butterfree", "min_lvl": 7, "max_lvl": 11, "weight": 25},
            {"species": "Beedrill", "min_lvl": 7, "max_lvl": 11, "weight": 25},
            {"species": "Pikachu", "min_lvl": 6, "max_lvl": 10, "weight": 20},
            {"species": "Oddish", "min_lvl": 6, "max_lvl": 9, "weight": 15},
            {"species": "Bellsprout", "min_lvl": 6, "max_lvl": 9, "weight": 15}
        ],
        "L": [
            {"species": "Pinsir", "min_lvl": 8, "max_lvl": 13, "weight": 20},
            {"species": "Scyther", "min_lvl": 8, "max_lvl": 13, "weight": 20},
            {"species": "Eevee", "min_lvl": 7, "max_lvl": 11, "weight": 20},
            {"species": "Caterpie", "min_lvl": 5, "max_lvl": 8, "weight": 20},
            {"species": "Weedle", "min_lvl": 5, "max_lvl": 8, "weight": 20}
        ],
        "u": [
            {"species": "Psyduck", "min_lvl": 6, "max_lvl": 10, "weight": 40},
            {"species": "Poliwag", "min_lvl": 6, "max_lvl": 10, "weight": 35},
            {"species": "Oddish", "min_lvl": 6, "max_lvl": 9, "weight": 25}
        ]
    },
    "Pewter City": {
        "r": [
            {"species": "Geodude", "min_lvl": 7, "max_lvl": 11, "weight": 45},
            {"species": "Onix", "min_lvl": 8, "max_lvl": 12, "weight": 25},
            {"species": "Sandshrew", "min_lvl": 7, "max_lvl": 11, "weight": 30}
        ],
        "F": [
            {"species": "Butterfree", "min_lvl": 7, "max_lvl": 11, "weight": 35},
            {"species": "Jigglypuff", "min_lvl": 7, "max_lvl": 11, "weight": 35},
            {"species": "Clefairy", "min_lvl": 8, "max_lvl": 12, "weight": 30}
        ]
    },
    "Route 3": {
        "r": [
            {"species": "Geodude", "min_lvl": 8, "max_lvl": 12, "weight": 35},
            {"species": "Sandshrew", "min_lvl": 8, "max_lvl": 12, "weight": 30},
            {"species": "Mankey", "min_lvl": 9, "max_lvl": 12, "weight": 20},
            {"species": "Machop", "min_lvl": 9, "max_lvl": 13, "weight": 15}
        ],
        "L": [
            {"species": "Spearow", "min_lvl": 8, "max_lvl": 12, "weight": 35},
            {"species": "Pidgey", "min_lvl": 8, "max_lvl": 12, "weight": 35},
            {"species": "Jigglypuff", "min_lvl": 8, "max_lvl": 12, "weight": 20},
            {"species": "Ekans", "min_lvl": 8, "max_lvl": 11, "weight": 10}
        ]
    },
    "Mt. Moon": {
        "r": [
            {"species": "Onix", "min_lvl": 10, "max_lvl": 15, "weight": 25},
            {"species": "Geodude", "min_lvl": 9, "max_lvl": 14, "weight": 35},
            {"species": "Sandshrew", "min_lvl": 9, "max_lvl": 13, "weight": 20},
            {"species": "Paras", "min_lvl": 9, "max_lvl": 13, "weight": 20}
        ],
        "e": [
            {"species": "Clefairy", "min_lvl": 10, "max_lvl": 15, "weight": 45},
            {"species": "Magnemite", "min_lvl": 9, "max_lvl": 14, "weight": 30},
            {"species": "Zubat", "min_lvl": 9, "max_lvl": 13, "weight": 25}
        ]
    },
    "Route 4": {
        "r": [
            {"species": "Sandshrew", "min_lvl": 11, "max_lvl": 15, "weight": 35},
            {"species": "Geodude", "min_lvl": 11, "max_lvl": 15, "weight": 35},
            {"species": "Ekans", "min_lvl": 12, "max_lvl": 15, "weight": 30}
        ],
        "u": [
            {"species": "Psyduck", "min_lvl": 12, "max_lvl": 16, "weight": 45},
            {"species": "Poliwag", "min_lvl": 12, "max_lvl": 16, "weight": 35},
            {"species": "Magikarp", "min_lvl": 10, "max_lvl": 15, "weight": 20}
        ]
    },
    "Cerulean City": {
        "F": [
            {"species": "Oddish", "min_lvl": 12, "max_lvl": 16, "weight": 35},
            {"species": "Bellsprout", "min_lvl": 12, "max_lvl": 16, "weight": 35},
            {"species": "Jigglypuff", "min_lvl": 12, "max_lvl": 16, "weight": 20},
            {"species": "Butterfree", "min_lvl": 13, "max_lvl": 17, "weight": 10}
        ],
        "u": [
            {"species": "Psyduck", "min_lvl": 13, "max_lvl": 17, "weight": 40},
            {"species": "Poliwag", "min_lvl": 13, "max_lvl": 17, "weight": 35},
            {"species": "Slowpoke", "min_lvl": 13, "max_lvl": 17, "weight": 25}
        ]
    },
    "Route 24": {
        "F": [
            {"species": "Butterfree", "min_lvl": 14, "max_lvl": 18, "weight": 25},
            {"species": "Oddish", "min_lvl": 13, "max_lvl": 17, "weight": 25},
            {"species": "Bellsprout", "min_lvl": 13, "max_lvl": 17, "weight": 25},
            {"species": "Abra", "min_lvl": 13, "max_lvl": 16, "weight": 20},
            {"species": "Bulbasaur", "min_lvl": 12, "max_lvl": 16, "weight": 5}
        ],
        "u": [
            {"species": "Psyduck", "min_lvl": 13, "max_lvl": 17, "weight": 35},
            {"species": "Slowpoke", "min_lvl": 13, "max_lvl": 17, "weight": 30},
            {"species": "Poliwag", "min_lvl": 13, "max_lvl": 17, "weight": 25},
            {"species": "Squirtle", "min_lvl": 12, "max_lvl": 16, "weight": 10}
        ]
    },
    "Route 9": {
        "r": [
            {"species": "Geodude", "min_lvl": 15, "max_lvl": 19, "weight": 30},
            {"species": "Machop", "min_lvl": 15, "max_lvl": 19, "weight": 30},
            {"species": "Sandshrew", "min_lvl": 15, "max_lvl": 18, "weight": 25},
            {"species": "Onix", "min_lvl": 16, "max_lvl": 20, "weight": 15}
        ],
        "L": [
            {"species": "Spearow", "min_lvl": 14, "max_lvl": 18, "weight": 35},
            {"species": "Rattata", "min_lvl": 14, "max_lvl": 17, "weight": 30},
            {"species": "Ekans", "min_lvl": 15, "max_lvl": 18, "weight": 20},
            {"species": "Doduo", "min_lvl": 15, "max_lvl": 19, "weight": 15}
        ]
    },
    "Lavender Town": {
        "m": [
            {"species": "Gastly", "min_lvl": 18, "max_lvl": 23, "weight": 50},
            {"species": "Haunter", "min_lvl": 21, "max_lvl": 25, "weight": 25},
            {"species": "Cubone", "min_lvl": 18, "max_lvl": 22, "weight": 25}
        ],
        "F": [
            {"species": "Vulpix", "min_lvl": 18, "max_lvl": 22, "weight": 40},
            {"species": "Pidgeotto", "min_lvl": 18, "max_lvl": 22, "weight": 35},
            {"species": "Gastly", "min_lvl": 18, "max_lvl": 22, "weight": 25}
        ]
    },
    "Pokémon Tower": {
        "m": [
            {"species": "Gastly", "min_lvl": 19, "max_lvl": 25, "weight": 45},
            {"species": "Haunter", "min_lvl": 23, "max_lvl": 28, "weight": 30},
            {"species": "Cubone", "min_lvl": 19, "max_lvl": 24, "weight": 15},
            {"species": "Drowzee", "min_lvl": 20, "max_lvl": 24, "weight": 10}
        ]
    },
    "Power Plant": {
        "e": [
            {"species": "Voltorb", "min_lvl": 22, "max_lvl": 27, "weight": 25},
            {"species": "Magnemite", "min_lvl": 22, "max_lvl": 27, "weight": 25},
            {"species": "Pikachu", "min_lvl": 23, "max_lvl": 28, "weight": 20},
            {"species": "Electrode", "min_lvl": 26, "max_lvl": 31, "weight": 12},
            {"species": "Magneton", "min_lvl": 26, "max_lvl": 31, "weight": 12},
            {"species": "Electabuzz", "min_lvl": 27, "max_lvl": 33, "weight": 6}
        ]
    },
    "Safari Zone": {
        "u": [
            {"species": "Dratini", "min_lvl": 22, "max_lvl": 27, "weight": 20},
            {"species": "Psyduck", "min_lvl": 22, "max_lvl": 26, "weight": 30},
            {"species": "Slowpoke", "min_lvl": 22, "max_lvl": 26, "weight": 30},
            {"species": "Dragonair", "min_lvl": 28, "max_lvl": 33, "weight": 10},
            {"species": "Poliwag", "min_lvl": 21, "max_lvl": 25, "weight": 10}
        ],
        "F": [
            {"species": "Exeggcute", "min_lvl": 23, "max_lvl": 28, "weight": 30},
            {"species": "Chansey", "min_lvl": 26, "max_lvl": 30, "weight": 15},
            {"species": "Scyther", "min_lvl": 25, "max_lvl": 30, "weight": 20},
            {"species": "Pinsir", "min_lvl": 25, "max_lvl": 30, "weight": 20},
            {"species": "Tangela", "min_lvl": 24, "max_lvl": 28, "weight": 15}
        ],
        "L": [
            {"species": "Doduo", "min_lvl": 23, "max_lvl": 27, "weight": 30},
            {"species": "Kangaskhan", "min_lvl": 25, "max_lvl": 30, "weight": 25},
            {"species": "Tauros", "min_lvl": 25, "max_lvl": 30, "weight": 25},
            {"species": "Rhyhorn", "min_lvl": 24, "max_lvl": 28, "weight": 20}
        ]
    },
    "Seafoam Islands": {
        "x": [
            {"species": "Seel", "min_lvl": 23, "max_lvl": 28, "weight": 30},
            {"species": "Dewgong", "min_lvl": 28, "max_lvl": 33, "weight": 20},
            {"species": "Jynx", "min_lvl": 26, "max_lvl": 31, "weight": 20},
            {"species": "Shellder", "min_lvl": 23, "max_lvl": 28, "weight": 15},
            {"species": "Lapras", "min_lvl": 27, "max_lvl": 32, "weight": 15}
        ],
        "r": [
            {"species": "Zubat", "min_lvl": 20, "max_lvl": 26, "weight": 40},
            {"species": "Golbat", "min_lvl": 24, "max_lvl": 28, "weight": 30},
            {"species": "Geodude", "min_lvl": 21, "max_lvl": 26, "weight": 30}
        ]
    },
    "Cinnabar Island": {
        "a": [
            {"species": "Magmar", "min_lvl": 23, "max_lvl": 28, "weight": 25},
            {"species": "Growlithe", "min_lvl": 21, "max_lvl": 26, "weight": 25},
            {"species": "Vulpix", "min_lvl": 21, "max_lvl": 26, "weight": 25},
            {"species": "Ponyta", "min_lvl": 22, "max_lvl": 27, "weight": 15},
            {"species": "Charmander", "min_lvl": 20, "max_lvl": 25, "weight": 10}
        ],
        "r": [
            {"species": "Koffing", "min_lvl": 21, "max_lvl": 26, "weight": 35},
            {"species": "Grimer", "min_lvl": 21, "max_lvl": 26, "weight": 35},
            {"species": "Rhyhorn", "min_lvl": 22, "max_lvl": 27, "weight": 30}
        ]
    }
}

def get_wild_encounters_for_prop(zone, prop_char, is_water=False):
    """Returns the encounter table for a specific zone and prop character."""
    if is_water:
        return WILD_WATER_ENCOUNTERS.get(zone, WILD_WATER_ENCOUNTERS.get("Route 21", []))
    
    # Check specific prop encounter table for this zone
    if zone in WILD_PROP_ENCOUNTERS and prop_char in WILD_PROP_ENCOUNTERS[zone]:
        return WILD_PROP_ENCOUNTERS[zone][prop_char]
    
    # Fallback to general zone encounter table
    return WILD_ENCOUNTERS.get(zone, WILD_ENCOUNTERS.get("Route 1", []))

# Overworld Trainers
