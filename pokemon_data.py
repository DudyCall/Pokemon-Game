"""
pokemon_data.py - Comprehensive Pokémon species, moves, items, and trainer databases.
"""

# Move Database
# Category: "Physical", "Special", "Status"
# Effect: None or dict with 'status', 'stat', 'chance', 'heal_percent', etc.
MOVES = {
    "Tackle": {
        "name": "Tackle", "type": "Normal", "power": 40, "accuracy": 100, "pp": 35,
        "category": "Physical", "effect": None, "desc": "A physical charge attack."
    },
    "Scratch": {
        "name": "Scratch", "type": "Normal", "power": 40, "accuracy": 100, "pp": 35,
        "category": "Physical", "effect": None, "desc": "Hard, pointed claws rake the foe."
    },
    "Growl": {
        "name": "Growl", "type": "Normal", "power": 0, "accuracy": 100, "pp": 40,
        "category": "Status", "effect": {"stat": "atk", "stages": -1}, "desc": "Lowers the foe's Attack."
    },
    "Tail Whip": {
        "name": "Tail Whip", "type": "Normal", "power": 0, "accuracy": 100, "pp": 30,
        "category": "Status", "effect": {"stat": "def", "stages": -1}, "desc": "Lowers the foe's Defense."
    },
    "Quick Attack": {
        "name": "Quick Attack", "type": "Normal", "power": 40, "accuracy": 100, "pp": 30,
        "category": "Physical", "priority": 1, "effect": None, "desc": "An extremely fast physical strike."
    },
    "Slam": {
        "name": "Slam", "type": "Normal", "power": 80, "accuracy": 75, "pp": 20,
        "category": "Physical", "effect": None, "desc": "Slams the foe with a long tail or vine."
    },
    "Hyper Beam": {
        "name": "Hyper Beam", "type": "Normal", "power": 120, "accuracy": 90, "pp": 5,
        "category": "Special", "effect": None, "desc": "A powerful beam of energy."
    },
    # Fire Moves
    "Ember": {
        "name": "Ember", "type": "Fire", "power": 40, "accuracy": 100, "pp": 25,
        "category": "Special", "effect": {"status": "Burn", "chance": 15}, "desc": "Small flames hit the target."
    },
    "Flamethrower": {
        "name": "Flamethrower", "type": "Fire", "power": 90, "accuracy": 100, "pp": 15,
        "category": "Special", "effect": {"status": "Burn", "chance": 20}, "desc": "A scorching stream of fire."
    },
    "Fire Spin": {
        "name": "Fire Spin", "type": "Fire", "power": 35, "accuracy": 85, "pp": 15,
        "category": "Special", "effect": None, "desc": "Traps foe in a ring of fire."
    },
    "Fire Blast": {
        "name": "Fire Blast", "type": "Fire", "power": 110, "accuracy": 85, "pp": 5,
        "category": "Special", "effect": {"status": "Burn", "chance": 30}, "desc": "An incandescent blast that incinerates."
    },
    # Water Moves
    "Water Gun": {
        "name": "Water Gun", "type": "Water", "power": 40, "accuracy": 100, "pp": 25,
        "category": "Special", "effect": None, "desc": "Squirts water to attack the target."
    },
    "Bubble": {
        "name": "Bubble", "type": "Water", "power": 40, "accuracy": 100, "pp": 30,
        "category": "Special", "effect": {"stat": "spd", "stages": -1, "chance": 20}, "desc": "Fires bubbles that may slow the foe."
    },
    "Water Pulse": {
        "name": "Water Pulse", "type": "Water", "power": 60, "accuracy": 100, "pp": 20,
        "category": "Special", "effect": None, "desc": "Attacks with ultrasonic water pulses."
    },
    "Hydro Pump": {
        "name": "Hydro Pump", "type": "Water", "power": 110, "accuracy": 80, "pp": 5,
        "category": "Special", "effect": None, "desc": "Blasts water at high volume."
    },
    # Grass Moves
    "Vine Whip": {
        "name": "Vine Whip", "type": "Grass", "power": 45, "accuracy": 100, "pp": 25,
        "category": "Physical", "effect": None, "desc": "Strikes the foe with slender vines."
    },
    "Razor Leaf": {
        "name": "Razor Leaf", "type": "Grass", "power": 55, "accuracy": 95, "pp": 25,
        "category": "Physical", "crit_bonus": True, "effect": None, "desc": "Cuts the foe with sharp leaves."
    },
    "Mega Drain": {
        "name": "Mega Drain", "type": "Grass", "power": 40, "accuracy": 100, "pp": 15,
        "category": "Special", "effect": {"drain_percent": 50}, "desc": "Drains half the damage inflicted."
    },
    "Solar Beam": {
        "name": "Solar Beam", "type": "Grass", "power": 120, "accuracy": 100, "pp": 10,
        "category": "Special", "effect": None, "desc": "Absorbs light then fires a concentrated beam."
    },
    # Electric Moves
    "Thunder Shock": {
        "name": "Thunder Shock", "type": "Electric", "power": 40, "accuracy": 100, "pp": 30,
        "category": "Special", "effect": {"status": "Paralysis", "chance": 15}, "desc": "An electric jolt that may paralyze."
    },
    "Thunderbolt": {
        "name": "Thunderbolt", "type": "Electric", "power": 90, "accuracy": 100, "pp": 15,
        "category": "Special", "effect": {"status": "Paralysis", "chance": 20}, "desc": "A strong electrical blast."
    },
    "Thunder Wave": {
        "name": "Thunder Wave", "type": "Electric", "power": 0, "accuracy": 90, "pp": 20,
        "category": "Status", "effect": {"status": "Paralysis", "chance": 100}, "desc": "A weak shock that paralyzes."
    },
    "Thunder": {
        "name": "Thunder", "type": "Electric", "power": 110, "accuracy": 70, "pp": 10,
        "category": "Special", "effect": {"status": "Paralysis", "chance": 30}, "desc": "A brutal lightning attack."
    },
    # Flying Moves
    "Gust": {
        "name": "Gust", "type": "Flying", "power": 40, "accuracy": 100, "pp": 35,
        "category": "Special", "effect": None, "desc": "Strikes the foe with wing gusts."
    },
    "Wing Attack": {
        "name": "Wing Attack", "type": "Flying", "power": 60, "accuracy": 100, "pp": 35,
        "category": "Physical", "effect": None, "desc": "Strikes the target with wide wings."
    },
    "Air Slash": {
        "name": "Air Slash", "type": "Flying", "power": 75, "accuracy": 95, "pp": 15,
        "category": "Special", "effect": None, "desc": "Attacks with a blade of air."
    },
    # Psychic Moves
    "Confusion": {
        "name": "Confusion", "type": "Psychic", "power": 50, "accuracy": 100, "pp": 25,
        "category": "Special", "effect": None, "desc": "A telekinetic wave attack."
    },
    "Psychic": {
        "name": "Psychic", "type": "Psychic", "power": 90, "accuracy": 100, "pp": 10,
        "category": "Special", "effect": {"stat": "spdef", "stages": -1, "chance": 15}, "desc": "A powerful telekinetic burst."
    },
    "Hypnosis": {
        "name": "Hypnosis", "type": "Psychic", "power": 0, "accuracy": 60, "pp": 20,
        "category": "Status", "effect": {"status": "Sleep", "chance": 100}, "desc": "Puts the foe into deep sleep."
    },
    # Ghost & Poison & Rock & Fighting Moves
    "Shadow Ball": {
        "name": "Shadow Ball", "type": "Ghost", "power": 80, "accuracy": 100, "pp": 15,
        "category": "Special", "effect": {"stat": "spdef", "stages": -1, "chance": 20}, "desc": "Hurls a shadowy blob."
    },
    "Lick": {
        "name": "Lick", "type": "Ghost", "power": 30, "accuracy": 100, "pp": 30,
        "category": "Physical", "effect": {"status": "Paralysis", "chance": 30}, "desc": "Licks with a long tongue."
    },
    "Poison Sting": {
        "name": "Poison Sting", "type": "Poison", "power": 15, "accuracy": 100, "pp": 35,
        "category": "Physical", "effect": {"status": "Poison", "chance": 30}, "desc": "Stabs with a poisonous barb."
    },
    "Sludge Bomb": {
        "name": "Sludge Bomb", "type": "Poison", "power": 90, "accuracy": 100, "pp": 10,
        "category": "Special", "effect": {"status": "Poison", "chance": 30}, "desc": "Unsanitary sludge is hurled."
    },
    "Rock Throw": {
        "name": "Rock Throw", "type": "Rock", "power": 50, "accuracy": 90, "pp": 15,
        "category": "Physical", "effect": None, "desc": "Drops small rocks on the target."
    },
    "Rock Slide": {
        "name": "Rock Slide", "type": "Rock", "power": 75, "accuracy": 90, "pp": 10,
        "category": "Physical", "effect": None, "desc": "Large boulders are hurled."
    },
    "Karate Chop": {
        "name": "Karate Chop", "type": "Fighting", "power": 50, "accuracy": 100, "pp": 25,
        "category": "Physical", "crit_bonus": True, "effect": None, "desc": "A sharp karate chop."
    },
    "Bite": {
        "name": "Bite", "type": "Dark", "power": 60, "accuracy": 100, "pp": 25,
        "category": "Physical", "effect": None, "desc": "Bites with vicious fangs."
    },
    "Dragon Claw": {
        "name": "Dragon Claw", "type": "Dragon", "power": 80, "accuracy": 100, "pp": 15,
        "category": "Physical", "effect": None, "desc": "Sharp claws slash the foe."
    },
    "Recover": {
        "name": "Recover", "type": "Normal", "power": 0, "accuracy": 100, "pp": 10,
        "category": "Status", "effect": {"heal_percent": 50}, "desc": "Restores up to half maximum HP."
    }
}

# Pokémon Species Database
# pokedex_id, name, types, base_stats: [hp, atk, def, spatk, spdef, spd], catch_rate, base_exp, learnset, evo
POKEMON_SPECIES = {
    "Bulbasaur": {
        "id": 1, "name": "Bulbasaur", "types": ["Grass", "Poison"],
        "base_stats": {"hp": 45, "atk": 49, "def": 49, "spatk": 65, "spdef": 65, "spd": 45},
        "catch_rate": 45, "base_exp": 64,
        "learnset": {1: ["Tackle", "Growl"], 4: ["Vine Whip"], 9: ["Poison Sting"], 13: ["Razor Leaf"], 20: ["Mega Drain"], 28: ["Solar Beam"]},
        "evolution": {"level": 16, "target": "Ivysaur"},
        "desc": "A strange seed was planted on its back at birth. The plant sprouts and grows with this Pokémon."
    },
    "Ivysaur": {
        "id": 2, "name": "Ivysaur", "types": ["Grass", "Poison"],
        "base_stats": {"hp": 60, "atk": 62, "def": 63, "spatk": 80, "spdef": 80, "spd": 60},
        "catch_rate": 45, "base_exp": 142,
        "learnset": {1: ["Tackle", "Vine Whip"], 13: ["Razor Leaf"], 20: ["Mega Drain"], 30: ["Solar Beam"]},
        "evolution": {"level": 32, "target": "Venusaur"},
        "desc": "When the bud on its back starts swelling, a sweet aroma wafts to indicate the flower's blooming."
    },
    "Venusaur": {
        "id": 3, "name": "Venusaur", "types": ["Grass", "Poison"],
        "base_stats": {"hp": 80, "atk": 82, "def": 83, "spatk": 100, "spdef": 100, "spd": 80},
        "catch_rate": 45, "base_exp": 236,
        "learnset": {1: ["Vine Whip", "Razor Leaf"], 22: ["Mega Drain"], 32: ["Solar Beam"], 40: ["Sludge Bomb"]},
        "evolution": None,
        "desc": "The plant blooms when it is absorbing solar energy. It stays on the move to seek sunlight."
    },
    "Charmander": {
        "id": 4, "name": "Charmander", "types": ["Fire"],
        "base_stats": {"hp": 39, "atk": 52, "def": 43, "spatk": 60, "spdef": 50, "spd": 65},
        "catch_rate": 45, "base_exp": 62,
        "learnset": {1: ["Scratch", "Growl"], 4: ["Ember"], 9: ["Quick Attack"], 15: ["Fire Spin"], 22: ["Flamethrower"], 30: ["Fire Blast"]},
        "evolution": {"level": 16, "target": "Charmeleon"},
        "desc": "From the day it is born, a flame burns at the tip of its tail. The flame burns brighter if it is healthy."
    },
    "Charmeleon": {
        "id": 5, "name": "Charmeleon", "types": ["Fire"],
        "base_stats": {"hp": 58, "atk": 64, "def": 58, "spatk": 80, "spdef": 65, "spd": 80},
        "catch_rate": 45, "base_exp": 142,
        "learnset": {1: ["Scratch", "Ember"], 15: ["Fire Spin"], 24: ["Flamethrower"], 34: ["Fire Blast"]},
        "evolution": {"level": 36, "target": "Charizard"},
        "desc": "It has a barbaric nature. In battle, it whips its fiery tail around and slashes away with sharp claws."
    },
    "Charizard": {
        "id": 6, "name": "Charizard", "types": ["Fire", "Flying"],
        "base_stats": {"hp": 78, "atk": 84, "def": 78, "spatk": 109, "spdef": 85, "spd": 100},
        "catch_rate": 45, "base_exp": 240,
        "learnset": {1: ["Wing Attack", "Flamethrower"], 36: ["Dragon Claw"], 42: ["Fire Blast"], 50: ["Hyper Beam"]},
        "evolution": None,
        "desc": "It flies in search of strong opponents. It breathes intense fire that can melt anything."
    },
    "Squirtle": {
        "id": 7, "name": "Squirtle", "types": ["Water"],
        "base_stats": {"hp": 44, "atk": 48, "def": 65, "spatk": 50, "spdef": 64, "spd": 43},
        "catch_rate": 45, "base_exp": 63,
        "learnset": {1: ["Tackle", "Tail Whip"], 4: ["Bubble"], 8: ["Water Gun"], 15: ["Water Pulse"], 22: ["Bite"], 28: ["Hydro Pump"]},
        "evolution": {"level": 16, "target": "Wartortle"},
        "desc": "Shoots water at prey while in the water. Withdraws into its shell when in danger."
    },
    "Wartortle": {
        "id": 8, "name": "Wartortle", "types": ["Water"],
        "base_stats": {"hp": 59, "atk": 63, "def": 80, "spatk": 65, "spdef": 80, "spd": 58},
        "catch_rate": 45, "base_exp": 142,
        "learnset": {1: ["Tackle", "Water Gun"], 15: ["Water Pulse"], 24: ["Bite"], 32: ["Hydro Pump"]},
        "evolution": {"level": 36, "target": "Blastoise"},
        "desc": "When tapped, this Pokémon will pull in its head, but its tail will still stick out a little bit."
    },
    "Blastoise": {
        "id": 9, "name": "Blastoise", "types": ["Water"],
        "base_stats": {"hp": 79, "atk": 83, "def": 100, "spatk": 85, "spdef": 105, "spd": 78},
        "catch_rate": 45, "base_exp": 239,
        "learnset": {1: ["Water Pulse", "Bite"], 36: ["Hydro Pump"], 44: ["Rock Slide"], 52: ["Hyper Beam"]},
        "evolution": None,
        "desc": "The rocket cannons on its shell fire jets of water capable of punching holes through thick steel."
    },
    "Pidgey": {
        "id": 16, "name": "Pidgey", "types": ["Normal", "Flying"],
        "base_stats": {"hp": 40, "atk": 45, "def": 40, "spatk": 35, "spdef": 35, "spd": 56},
        "catch_rate": 255, "base_exp": 50,
        "learnset": {1: ["Tackle"], 4: ["Gust"], 9: ["Quick Attack"], 15: ["Wing Attack"]},
        "evolution": {"level": 18, "target": "Pidgeotto"},
        "desc": "Very docile. If attacked, it will often kick up sand to protect itself rather than fight back."
    },
    "Pidgeotto": {
        "id": 17, "name": "Pidgeotto", "types": ["Normal", "Flying"],
        "base_stats": {"hp": 63, "atk": 60, "def": 55, "spatk": 50, "spdef": 50, "spd": 71},
        "catch_rate": 120, "base_exp": 122,
        "learnset": {1: ["Gust", "Quick Attack"], 18: ["Wing Attack"], 26: ["Air Slash"]},
        "evolution": {"level": 36, "target": "Pidgeot"},
        "desc": "This Pokémon is full of vitality. It flies constantly around in search of prey."
    },
    "Pidgeot": {
        "id": 18, "name": "Pidgeot", "types": ["Normal", "Flying"],
        "base_stats": {"hp": 83, "atk": 80, "def": 75, "spatk": 70, "spdef": 70, "spd": 101},
        "catch_rate": 45, "base_exp": 216,
        "learnset": {1: ["Wing Attack"], 36: ["Air Slash"], 45: ["Hyper Beam"]},
        "evolution": None,
        "desc": "When hunting, it skims the surface of water at high speed to pick off unwitting prey."
    },
    "Rattata": {
        "id": 19, "name": "Rattata", "types": ["Normal"],
        "base_stats": {"hp": 30, "atk": 56, "def": 35, "spatk": 25, "spdef": 35, "spd": 72},
        "catch_rate": 255, "base_exp": 51,
        "learnset": {1: ["Tackle", "Tail Whip"], 4: ["Quick Attack"], 10: ["Bite"], 16: ["Hyper Fang", "Slam"]},
        "evolution": {"level": 20, "target": "Raticate"},
        "desc": "Bites anything when it attacks. Small and very quick, it is a common sight in many places."
    },
    "Raticate": {
        "id": 20, "name": "Raticate", "types": ["Normal"],
        "base_stats": {"hp": 55, "atk": 81, "def": 60, "spatk": 50, "spdef": 70, "spd": 97},
        "catch_rate": 127, "base_exp": 145,
        "learnset": {1: ["Tackle", "Quick Attack", "Bite"], 20: ["Slam"], 30: ["Hyper Beam"]},
        "evolution": None,
        "desc": "Its hind feet are webbed, so it can swim across rivers to find prey."
    },
    "Pikachu": {
        "id": 25, "name": "Pikachu", "types": ["Electric"],
        "base_stats": {"hp": 35, "atk": 55, "def": 40, "spatk": 50, "spdef": 50, "spd": 90},
        "catch_rate": 190, "base_exp": 112,
        "learnset": {1: ["Thunder Shock", "Growl"], 6: ["Tail Whip"], 8: ["Thunder Wave"], 11: ["Quick Attack"], 18: ["Thunderbolt"], 26: ["Thunder"]},
        "evolution": {"level": 26, "target": "Raichu"},
        "desc": "When several of these Pokémon gather, their electricity could build and cause lightning storms."
    },
    "Raichu": {
        "id": 26, "name": "Raichu", "types": ["Electric"],
        "base_stats": {"hp": 60, "atk": 90, "def": 55, "spatk": 90, "spdef": 80, "spd": 110},
        "catch_rate": 75, "base_exp": 218,
        "learnset": {1: ["Thunder Shock", "Quick Attack", "Thunderbolt"], 30: ["Thunder"], 40: ["Hyper Beam"]},
        "evolution": None,
        "desc": "Its long tail serves as a ground to protect itself from its own high-voltage electrical power."
    },
    "Geodude": {
        "id": 74, "name": "Geodude", "types": ["Rock", "Ground"],
        "base_stats": {"hp": 40, "atk": 80, "def": 100, "spatk": 30, "spdef": 30, "spd": 20},
        "catch_rate": 255, "base_exp": 60,
        "learnset": {1: ["Tackle"], 6: ["Rock Throw"], 12: ["Karate Chop"], 20: ["Rock Slide"], 30: ["Slam"]},
        "evolution": {"level": 25, "target": "Graveler"},
        "desc": "Found in fields and mountains. Mistaking them for boulders, people often step or trip on them."
    },
    "Graveler": {
        "id": 75, "name": "Graveler", "types": ["Rock", "Ground"],
        "base_stats": {"hp": 55, "atk": 95, "def": 115, "spatk": 45, "spdef": 45, "spd": 35},
        "catch_rate": 120, "base_exp": 137,
        "learnset": {1: ["Rock Throw", "Tackle"], 25: ["Rock Slide"], 35: ["Slam"]},
        "evolution": {"level": 38, "target": "Golem"},
        "desc": "Rolls down slopes to move. It rolls over any obstacle without slowing or changing its direction."
    },
    "Golem": {
        "id": 76, "name": "Golem", "types": ["Rock", "Ground"],
        "base_stats": {"hp": 80, "atk": 120, "def": 130, "spatk": 55, "spdef": 65, "spd": 45},
        "catch_rate": 45, "base_exp": 223,
        "learnset": {1: ["Rock Slide", "Slam"], 40: ["Hyper Beam"]},
        "evolution": None,
        "desc": "It is enclosed in a hard shell that is as rugged as rock. It sheds its skin once a year."
    },
    "Gastly": {
        "id": 92, "name": "Gastly", "types": ["Ghost", "Poison"],
        "base_stats": {"hp": 30, "atk": 35, "def": 30, "spatk": 100, "spdef": 35, "spd": 80},
        "catch_rate": 190, "base_exp": 62,
        "learnset": {1: ["Lick", "Hypnosis"], 8: ["Poison Sting"], 15: ["Confusion"], 24: ["Shadow Ball"], 32: ["Sludge Bomb"]},
        "evolution": {"level": 25, "target": "Haunter"},
        "desc": "Almost invisible, this gaseous Pokémon cloaks the target and puts it to sleep without notice."
    },
    "Haunter": {
        "id": 93, "name": "Haunter", "types": ["Ghost", "Poison"],
        "base_stats": {"hp": 45, "atk": 50, "def": 45, "spatk": 115, "spdef": 55, "spd": 95},
        "catch_rate": 90, "base_exp": 142,
        "learnset": {1: ["Lick", "Hypnosis", "Shadow Ball"], 28: ["Sludge Bomb"], 36: ["Psychic"]},
        "evolution": {"level": 38, "target": "Gengar"},
        "desc": "Because of its ability to slip through block walls, it is said to be from another dimension."
    },
    "Gengar": {
        "id": 94, "name": "Gengar", "types": ["Ghost", "Poison"],
        "base_stats": {"hp": 60, "atk": 65, "def": 60, "spatk": 130, "spdef": 75, "spd": 110},
        "catch_rate": 45, "base_exp": 225,
        "learnset": {1: ["Shadow Ball", "Sludge Bomb", "Hypnosis"], 40: ["Psychic"], 50: ["Hyper Beam"]},
        "evolution": None,
        "desc": "Under a full moon, this Pokémon loves to mimic the shadows of people and laugh at their fright."
    },
    "Abra": {
        "id": 63, "name": "Abra", "types": ["Psychic"],
        "base_stats": {"hp": 25, "atk": 20, "def": 15, "spatk": 105, "spdef": 55, "spd": 90},
        "catch_rate": 200, "base_exp": 62,
        "learnset": {1: ["Confusion"], 10: ["Quick Attack"], 16: ["Psychic"]},
        "evolution": {"level": 16, "target": "Kadabra"},
        "desc": "Using its ability to read minds, it will identify impending danger and teleport to safety."
    },
    "Kadabra": {
        "id": 64, "name": "Kadabra", "types": ["Psychic"],
        "base_stats": {"hp": 40, "atk": 35, "def": 30, "spatk": 120, "spdef": 70, "spd": 105},
        "catch_rate": 100, "base_exp": 140,
        "learnset": {1: ["Confusion", "Psychic"], 24: ["Recover"], 34: ["Shadow Ball"]},
        "evolution": {"level": 36, "target": "Alakazam"},
        "desc": "It emits special alpha waves from its body that induce headaches in anyone nearby."
    },
    "Alakazam": {
        "id": 65, "name": "Alakazam", "types": ["Psychic"],
        "base_stats": {"hp": 55, "atk": 50, "def": 45, "spatk": 135, "spdef": 95, "spd": 120},
        "catch_rate": 50, "base_exp": 225,
        "learnset": {1: ["Psychic", "Recover", "Shadow Ball"], 42: ["Hyper Beam"]},
        "evolution": None,
        "desc": "Its brain cells multiply continually until it dies. As a result, it remembers everything."
    },
    "Eevee": {
        "id": 133, "name": "Eevee", "types": ["Normal"],
        "base_stats": {"hp": 55, "atk": 55, "def": 50, "spatk": 45, "spdef": 65, "spd": 55},
        "catch_rate": 45, "base_exp": 65,
        "learnset": {1: ["Tackle", "Tail Whip"], 5: ["Quick Attack"], 12: ["Bite"], 20: ["Slam"]},
        "evolution": {"level": 25, "target": "Vaporeon"}, # Can adapt
        "desc": "Its genetic code is irregular. It may mutate if it is exposed to radiation from element stones."
    },
    "Vaporeon": {
        "id": 134, "name": "Vaporeon", "types": ["Water"],
        "base_stats": {"hp": 130, "atk": 65, "def": 60, "spatk": 110, "spdef": 95, "spd": 65},
        "catch_rate": 45, "base_exp": 184,
        "learnset": {1: ["Water Gun", "Quick Attack", "Bite"], 25: ["Water Pulse"], 35: ["Hydro Pump"]},
        "evolution": None,
        "desc": "Lives close to water. Its long tail is ridged with a fin which is often mistaken for a mermaid's."
    },
    "Jolteon": {
        "id": 135, "name": "Jolteon", "types": ["Electric"],
        "base_stats": {"hp": 65, "atk": 65, "def": 60, "spatk": 110, "spdef": 95, "spd": 130},
        "catch_rate": 45, "base_exp": 184,
        "learnset": {1: ["Thunder Shock", "Quick Attack", "Bite"], 25: ["Thunder Wave"], 35: ["Thunderbolt"], 42: ["Thunder"]},
        "evolution": None,
        "desc": "It accumulates negative ions in the atmosphere to blast out 10,000-volt lightning bolts."
    },
    "Flareon": {
        "id": 136, "name": "Flareon", "types": ["Fire"],
        "base_stats": {"hp": 65, "atk": 130, "def": 60, "spatk": 95, "spdef": 110, "spd": 65},
        "catch_rate": 45, "base_exp": 184,
        "learnset": {1: ["Ember", "Quick Attack", "Bite"], 25: ["Fire Spin"], 35: ["Flamethrower"], 42: ["Fire Blast"]},
        "evolution": None,
        "desc": "When storing thermal energy in its body, its temperature could climb to over 1,600 degrees F."
    },
    "Snorlax": {
        "id": 143, "name": "Snorlax", "types": ["Normal"],
        "base_stats": {"hp": 160, "atk": 110, "def": 65, "spatk": 65, "spdef": 110, "spd": 30},
        "catch_rate": 25, "base_exp": 189,
        "learnset": {1: ["Tackle", "Lick"], 15: ["Bite"], 25: ["Slam"], 35: ["Hyper Beam"]},
        "evolution": None,
        "desc": "Very lazy. Just eats and sleeps. As its enormous bulk builds, it becomes even more reluctant to move."
    },
    "Dratini": {
        "id": 147, "name": "Dratini", "types": ["Dragon"],
        "base_stats": {"hp": 41, "atk": 64, "def": 45, "spatk": 50, "spdef": 50, "spd": 50},
        "catch_rate": 45, "base_exp": 60,
        "learnset": {1: ["Tackle", "Thunder Wave"], 10: ["Dragon Claw"], 20: ["Slam"], 30: ["Hyper Beam"]},
        "evolution": {"level": 30, "target": "Dragonair"},
        "desc": "Long considered a mythical Pokémon until recently when a small colony was found living underwater."
    },
    "Dragonair": {
        "id": 148, "name": "Dragonair", "types": ["Dragon"],
        "base_stats": {"hp": 61, "atk": 84, "def": 65, "spatk": 70, "spdef": 70, "spd": 70},
        "catch_rate": 45, "base_exp": 147,
        "learnset": {1: ["Dragon Claw", "Thunder Wave", "Slam"], 35: ["Flamethrower", "Thunderbolt"], 45: ["Hyper Beam"]},
        "evolution": {"level": 55, "target": "Dragonite"},
        "desc": "A mystical Pokémon that exudes a gentle aura. It has the ability to change climate freely."
    },
    "Dragonite": {
        "id": 149, "name": "Dragonite", "types": ["Dragon", "Flying"],
        "base_stats": {"hp": 91, "atk": 134, "def": 95, "spatk": 100, "spdef": 100, "spd": 80},
        "catch_rate": 45, "base_exp": 270,
        "learnset": {1: ["Wing Attack", "Dragon Claw", "Flamethrower", "Thunderbolt"], 55: ["Hyper Beam"]},
        "evolution": None,
        "desc": "An extremely rarely seen marine Pokémon. Its intelligence is said to match that of humans."
    }
}

# Items Database
ITEMS = {
    "Poke Ball": {
        "name": "Poké Ball", "category": "ball", "catch_mult": 1.0, "price": 200,
        "desc": "A device for catching wild Pokémon. It is thrown like a ball."
    },
    "Great Ball": {
        "name": "Great Ball", "category": "ball", "catch_mult": 1.5, "price": 600,
        "desc": "A good, high-performance Ball that provides a higher catch rate."
    },
    "Ultra Ball": {
        "name": "Ultra Ball", "category": "ball", "catch_mult": 2.0, "price": 1200,
        "desc": "An ultra-performance Ball with a superior catch rate."
    },
    "Potion": {
        "name": "Potion", "category": "medicine", "heal_hp": 20, "price": 300,
        "desc": "A spray-type medicine that restores the HP of one Pokémon by 20 points."
    },
    "Super Potion": {
        "name": "Super Potion", "category": "medicine", "heal_hp": 50, "price": 700,
        "desc": "A spray-type medicine that restores the HP of one Pokémon by 50 points."
    },
    "Max Potion": {
        "name": "Max Potion", "category": "medicine", "heal_hp": 9999, "price": 2500,
        "desc": "Fully restores the HP of one Pokémon."
    },
    "Revive": {
        "name": "Revive", "category": "medicine", "revive_hp_percent": 50, "price": 1500,
        "desc": "Revives a fainted Pokémon and restores half of its maximum HP."
    },
    "Antidote": {
        "name": "Antidote", "category": "medicine", "cure_status": "Poison", "price": 100,
        "desc": "Cures a Pokémon of poison."
    },
    "Paralyze Heal": {
        "name": "Paralyze Heal", "category": "medicine", "cure_status": "Paralysis", "price": 200,
        "desc": "Heals a paralyzed Pokémon."
    },
    "Awakening": {
        "name": "Awakening", "category": "medicine", "cure_status": "Sleep", "price": 250,
        "desc": "Awakens a sleeping Pokémon."
    },
    "Rare Candy": {
        "name": "Rare Candy", "category": "candy", "level_up": 1, "price": 4800,
        "desc": "A candy that raises the level of a single Pokémon by one."
    }
}

# Wild Encounters by Zone / Route
WILD_ENCOUNTERS = {
    "Route 1": [
        {"species": "Pidgey", "min_lvl": 2, "max_lvl": 5, "weight": 50},
        {"species": "Rattata", "min_lvl": 2, "max_lvl": 4, "weight": 40},
        {"species": "Pikachu", "min_lvl": 3, "max_lvl": 5, "weight": 10}
    ],
    "Route 2": [
        {"species": "Pidgey", "min_lvl": 4, "max_lvl": 7, "weight": 35},
        {"species": "Rattata", "min_lvl": 4, "max_lvl": 6, "weight": 30},
        {"species": "Bulbasaur", "min_lvl": 5, "max_lvl": 7, "weight": 10},
        {"species": "Charmander", "min_lvl": 5, "max_lvl": 7, "weight": 10},
        {"species": "Squirtle", "min_lvl": 5, "max_lvl": 7, "weight": 10},
        {"species": "Abra", "min_lvl": 6, "max_lvl": 8, "weight": 5}
    ],
    "Viridian Forest": [
        {"species": "Pikachu", "min_lvl": 5, "max_lvl": 9, "weight": 25},
        {"species": "Gastly", "min_lvl": 6, "max_lvl": 10, "weight": 25},
        {"species": "Geodude", "min_lvl": 7, "max_lvl": 11, "weight": 25},
        {"species": "Eevee", "min_lvl": 8, "max_lvl": 12, "weight": 15},
        {"species": "Snorlax", "min_lvl": 12, "max_lvl": 15, "weight": 10}
    ]
}

# Overworld Trainers
TRAINERS = [
    {
        "id": "youngster_joey",
        "name": "Youngster Joey",
        "map": "Route 1",
        "x": 12, "y": 8,
        "direction": "DOWN",
        "dialog_before": "Hi! I like shorts! They're comfy and easy to wear! Let's battle!",
        "dialog_after": "My Rattata is in the top percentage of Rattata!",
        "reward_money": 120,
        "party": [
            {"species": "Rattata", "level": 4},
            {"species": "Pidgey", "level": 4}
        ]
    },
    {
        "id": "bug_catcher_sammy",
        "name": "Bug Catcher Sammy",
        "map": "Route 1",
        "x": 6, "y": 18,
        "direction": "RIGHT",
        "dialog_before": "Stop right there! You caught wild Pokémon too?",
        "dialog_after": "Aw man! My Pokémon weren't fast enough!",
        "reward_money": 160,
        "party": [
            {"species": "Pidgey", "level": 5},
            {"species": "Bulbasaur", "level": 6}
        ]
    },
    {
        "id": "lass_haley",
        "name": "Lass Haley",
        "map": "Route 2",
        "x": 14, "y": 10,
        "direction": "LEFT",
        "dialog_before": "You look like a tough trainer! Can you defeat my Pikachu?",
        "dialog_after": "You are indeed very strong!",
        "reward_money": 240,
        "party": [
            {"species": "Pikachu", "level": 8},
            {"species": "Eevee", "level": 8}
        ]
    },
    {
        "id": "gym_leader_brock",
        "name": "Leader Brock",
        "map": "Viridian Forest",
        "x": 10, "y": 4,
        "direction": "DOWN",
        "dialog_before": "I am Brock! My rock-hard willpower is evident even in my Pokémon!",
        "dialog_after": "I took you for granted! As proof of your victory, take this prize!",
        "reward_money": 1000,
        "party": [
            {"species": "Geodude", "level": 12},
            {"species": "Graveler", "level": 14},
            {"species": "Dragonair", "level": 15}
        ]
    }
]
