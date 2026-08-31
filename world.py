"""
world.py - Overworld map management, player movement, collision detection,
tall grass encounters, NPC dialogues, ground collectible items, signposts, and building interiors.
"""
import random
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, Direction,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, WHITE, BLACK
)
from graphics_manager import gfx
from sound_manager import sound_mgr
from pokemon_data import WILD_ENCOUNTERS, TRAINERS

# Tile Legend for Map Grids:
# . = Grass
# G = Tall Grass (Wild Pokemon encounter)
# # = Tree / Forest border (Solid obstacle)
# ~ = Water / Ocean (Solid obstacle)
# p = Path / Dirt road
# s = Sand / Shore
# b = Wood Bridge / Pier
# ^ = Cave Wall / Mountain Rock (Solid obstacle)
# _ = Indoor / Cave Floor
# O = Cave Entrance / Arch
# f = Fence (Solid obstacle)
# * = Red Flower
# R = PokeCenter Red Roof (Solid obstacle)
# B = Mart Blue Roof (Solid obstacle)
# W = Building Wall (Solid obstacle)
# D = Building Door (Warp)
# S = Wooden Sign (Interactive)
# C = Indoor Counter (Solid obstacle)
# N = Nurse Joy NPC
# M = Mart Clerk NPC
# P = PC Terminal
# J = Gym Arena Mat
# Y = Gym / Museum Statue (Solid obstacle)
# H = Lab Tech Desk / Furniture (Solid obstacle)
# K = Bookshelf (Solid obstacle)
# o = Ground Collectible Item Poké Ball

MAP_PALLET_TOWN = [
    "########....##########",
    "#......pppppp........#",
    "#..WW..p....p..WWWW..#",
    "#..WW..p....p..WWWW..#",
    "#..WD..p....p..WWWD..#",
    "#......pppppp........#",
    "#..**..p....p..**....#",
    "#..o...p....p........#",
    "#..ff..p....p..ff....#",
    "#......pppppp........#",
    "#..S.....pp.....S....#",
    "#........pp..........#",
    "#..ssssssssssssssss..#",
    "#..ssssssbbssssssss..#",
    "#..~~~~~~bb~~~~~~~~..#",
    "#..~~~~~~bb~~~~~~~~..#",
    "#..~~~~~~bb~~~~~~~~..#",
    "#########..###########",
]

MAP_ROUTE_1 = [
    "########....##########",
    "#........pp..........#",
    "#..GGGG..pp..GGGG....#",
    "#..GGGG..pp..GGGG....#",
    "#..GGGG..pp..GGGG....#",
    "#........pp..........#",
    "#..ffff..pp..ffff....#",
    "#..S.....pp..........#",
    "#..GGGG..pp..GGGG....#",
    "#..GGGG..pp..GGGG....#",
    "#........pp..........#",
    "#..GGGG..pp..GGGG....#",
    "#..GGGG..pp..GGGG....#",
    "#........pp..........#",
    "#..ffff..pp..ffff....#",
    "#........pp..........#",
    "#..GGGG..pp..GGGG....#",
    "#..GGGG..pp..GGGG....#",
    "#........pp..........#",
    "#..ffff..pp..........#",
    "#........pp..GGGG....#",
    "#..o.....pp..GGGG....#",
    "#..GGGG..pp..GGGG....#",
    "#..GGGG..pp..........#",
    "#........pp..........#",
    "########....##########",
]

MAP_VIRIDIAN_CITY = [
    "############....############",
    "#............pp............#",
    "#..RRRR......pp......BBBB..#",
    "#..RRRR......pp......BBBB..#",
    "#..WWWD......pp......WWWD..#",
    "#............pp............#",
    "#..S.........pp.........S..#",
    "#..pppppppppppppppppppppp..#",
    "#..p........pppp........p..#",
    "#..p..GGGG..pppp..GGGG..p..#",
    "#..p..GGGG..pppp..GGGG..p..#",
    "...p........pppp........p..#",
    "...pppppppppppppppppppppp..#",
    "...p........pppp........p..#",
    "#..p..WWWW..pppp..WWWW..p..#",
    "#..p..WWWW..pppp..WWWW..p..#",
    "#..p..WWWD..pppp..WWWD..p..#",
    "#..p........pppp........p..#",
    "#..pppppppppppppppppppppp..#",
    "#..p........pppp........p..#",
    "#..p..****..pppp..****..p..#",
    "#..pppppppppppppppppppppp..#",
    "#............pp............#",
    "############....############",
]

MAP_ROUTE_22 = [
    "############################",
    "#..^^^^^^^^^^^^^^^^^^^^^^..#",
    "#..^....................^..#",
    "#..^..GGGG........GGGG..^..#",
    "#..^..GGGG..~~~~..GGGG..^..#",
    "#..^........~~~~........^..#",
    "#..^..WWWW..~~~~..o.....^..#",
    "#..^..WWWD..~~~~........^..#",
    "#..^..S.....pppppppppppppppp",
    "#..^........p..........p....",
    "#..^..GGGG..p..~~~~....p....",
    "#..^..GGGG..p..~~~~....p...#",
    "#..^..o.....pppppppppppp...#",
    "#..^........p..........p...#",
    "#..^..GGGG..p..GGGG.....^..#",
    "#..^..GGGG..p..GGGG.....^..#",
    "#..^^^^^^^^^^^^^^^^^^^^^^..#",
    "############################",
]

MAP_VIRIDIAN_FOREST = [
    "################....############",
    "#..............................#",
    "#..GGGG..####..GGGG..####..GG..#",
    "#..GGGG..####..GGGG..####..GG..#",
    "#..pp....####..pp....####..pp..#",
    "#..pp..........pp..........pp..#",
    "#..pppppppppppppppppppppppppp..#",
    "#..pp..........pp..........pp..#",
    "#..GG..####....GG..####....GG..#",
    "#..GG..####..o.GG..####....GG..#",
    "#..pppppppppppppppppppppppppp..#",
    "#..pp..........pp..........pp..#",
    "#..GGGG..####..GGGG..####..GG..#",
    "#..GGGG..####..GGGG..####..GG..#",
    "#..pp....####..pp....####..pp..#",
    "#..pp..........pp..........pp..#",
    "#..pppppppppppppppppppppppppp..#",
    "#..pp..........pp..........pp..#",
    "#..GG..####....GG..####....GG..#",
    "#..GG..####....GG..####..o.GG..#",
    "#..pppppppppppppppppppppppppp..#",
    "#..pp..........pp..........pp..#",
    "#..GGGG..####..GGGG..####..GG..#",
    "#..GGGG..####..GGGG..####..GG..#",
    "#..pp....####..pp....####..pp..#",
    "#..pp..........pp..........pp..#",
    "#..pppppppppppppppppppppppppp..#",
    "#..o...........pp..........S...#",
    "#..GGGG..GGGG..pp..GGGG..GGGG..#",
    "#..GGGG..GGGG..pp..GGGG..GGGG..#",
    "#..............pp..............#",
    "################....############",
]

MAP_PEWTER_CITY = [
    "################################",
    "#............pp................#",
    "#..RRRR......pp......BBBB......#",
    "#..RRRR......pp......BBBB......#",
    "#..WWWD......pp......WWWD......#",
    "#............pp................#",
    "#..S.........pp.........S......#",
    "#..pppppppppppppppppppppppppppp.",
    "#..p........pppp........p.......",
    "#..p..WWWW..pppp..WWWW..p.......",
    "#..p..WWWW..pppp..WWWW..p......#",
    "#..p..WWWD..pppp..WWWD..p......#",
    "#..p..S.....pppp..S.....p.......",
    "#..pppppppppppppppppppppppppppp.",
    "#..p........pppp........p.......",
    "#..p..****..pppp..****..p......#",
    "#..pppppppppppppppppppppp......#",
    "#..p........pppp........p......#",
    "#..p..GGGG..pppp..GGGG..p......#",
    "#..p..GGGG..pppp..GGGG..p......#",
    "#..pppppppppppppppppppppp......#",
    "#............pp................#",
    "#............pp................#",
    "#############....###############",
]

MAP_ROUTE_3 = [
    "############################O###",
    "#..........................p...#",
    "#..^^^^^^^^^^^^^^^^^^^^^^..p...#",
    "#..^....................^..p...#",
    "#..^..GGGG..^^^^..GGGG..^..p...#",
    "#..^..GGGG..^^^^..GGGG..^..p...#",
    "#..^........^^^^........^..p...#",
    "...ppppppppppppppppppppppppp...#",
    "...p........^^^^........p......#",
    "...p..GGGG..^^^^..GGGG..p......#",
    "#..p..GGGG..^^^^..GGGG..p..o...#",
    "...p........^^^^........p......#",
    "...pppppppppppppppppppppp......#",
    "...S........^^^^........S......#",
    "#..GGGG..GGGG..GGGG..GGGG......#",
    "#..GGGG..GGGG..GGGG..GGGG......#",
    "#..............................#",
    "################################",
]

MAP_MT_MOON = [
    "################################",
    "#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#",
    "#^_.......^^^^^^^^........_^^^O#",
    "#^_..____.^^^^^^^^.____..._^^^^#",
    "#^_.._o__.^^^^^^^^._o__..._^^^^#",
    "#^_..____..........____..._^^^^#",
    "#^_......................._^^^^#",
    "#^_____________________________#",
    "#^_.......^^^^^^^^........_^^^^#",
    "#^_..____.^^^^^^^^.____..._^^^^#",
    "#^_..____.^^^^^^^^.____..._^^^^#",
    "#^_..____.^^^^^^^^.____..._^^^^#",
    "#^_____________________________#",
    "#^_......................._^^^^#",
    "#^_.......^^^^^^^^........_^^^^#",
    "#^_..____.^^^^^^^^.____..._^^^^#",
    "#^_..____.^^^^^^^^.____..._^^^^#",
    "#^_..____.^^^^^^^^.____..._^^^^#",
    "#^_____________________________#",
    "#^_.......^^^^^^^^..o....._^^^^#",
    "#^_S......^^^^^^^^........_^^^^#",
    "#O^^.....................^^^^^^#",
    "#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#",
    "################################",
]

MAP_ROUTE_4 = [
    "###O########################",
    "#..p.......................#",
    "#..p..~~~~~~~~~~~~~~~~~~~..#",
    "#..p..~~~~~~~~~~~~~~~~~~~..#",
    "#..pppppppppppppppppppppppp.",
    "#..p..~~~~~~~~~~~~~~~~~~~...",
    "#..p..~~~~~~~~~~~~~~~~~~~...",
    "#..p..GGGG..^^^^..GGGG..p..#",
    "#..p..GGGG..^^^^..GGGG..p..#",
    "#..pppppppppppppppppppppp..#",
    "#..S........^^^^........S..#",
    "#..GGGG..o..^^^^..GGGG.....#",
    "#..GGGG.....^^^^..GGGG.....#",
    "#..........................#",
    "#..........................#",
    "############################",
]

MAP_CERULEAN_CITY = [
    "############....################",
    "#............pp................#",
    "#..RRRR......pp......BBBB......#",
    "#..RRRR......pp......BBBB......#",
    "#..WWWD......pp......WWWD......#",
    "#............pp................#",
    "#..S.........pp.........S......#",
    "#..pppppppppppppppppppppp......#",
    "#..p........pppp........p......#",
    "#..p..WWWW..pppp..WWWW..p......#",
    "#..p..WWWW..pppp..WWWW..p......#",
    "...p..WWWD..pppp..WWWD..p......#",
    "...pppppppppppppppppppppp......#",
    "...p..S.....pppp..S.....p......#",
    "#..p........pppp........p......#",
    "#..p..~~~~..pppp..~~~~..p......#",
    "#..p..~~~~..pppp..~~~~..p......#",
    "#..pppppppppppppppppppppp......#",
    "#..p........pppp........p......#",
    "#..p..****..pppp..****..p......#",
    "#..pppppppppppppppppppppp......#",
    "#............pp................#",
    "#............pp................#",
    "################################",
]

MAP_ROUTE_24 = [
    "#################WWWD###",
    "#...............WWWW...#",
    "#..~~~~~~~~~~~~~WWWW...#",
    "#..~~~~~~~~~~~~~S......#",
    "#..~~~~~~~~~~~~~pppp...#",
    "#..~~~~~~bb~~~~~p......#",
    "#..~~~~~~bb~~~~~p..o...#",
    "#..~~~~~~bb~~~~~p......#",
    "#..~~~~~~bb~~~~~pppp...#",
    "#..~~~~~~bb~~~~~p......#",
    "#..~~~~~~bb~~~~~p..GG..#",
    "#..~~~~~~bb~~~~~p..GG..#",
    "#..~~~~~~bb~~~~~p......#",
    "#..~~~~~~bb~~~~~pppp...#",
    "#..~~~~~~bb~~~~~p......#",
    "#..~~~~~~bb~~~~~p..GG..#",
    "#..~~~~~~bb~~~~~p..GG..#",
    "#..~~~~~~bb~~~~~p......#",
    "#..~~~~~~bb~~~~~pppp...#",
    "#..~~~~~~bb~~~~~p......#",
    "#..~~~~~~bb~~~~~p..GG..#",
    "#..~~~~~~bb~~~~~p..GG..#",
    "#..~~~~~~bb~~~~~p......#",
    "#..~~~~~~bb~~~~~pppp...#",
    "#..S.....bb.....p......#",
    "#........bb............#",
    "#........bb............#",
    "#########..#############",
]

MAP_ROUTE_21 = [
    "#########..#############",
    "#........bb............#",
    "#........bb............#",
    "#..~~~~~~bb~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~ssss~~~~~~~~..#",
    "#..~~~~~~ssss~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~ssss~~~~~~~~~~~~..#",
    "#..~~sso~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~ssss~~..#",
    "#..~~~~~~~~~~~~ssss~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..~~~~~~~~~~~~~~~~~~..#",
    "#..ssssssssssssssssss..#",
    "#..ssssssssssssssssss..#",
    "#........pp............#",
    "#########..#############",
]

MAP_CINNABAR_ISLAND = [
    "##########..##############",
    "#.........pp.............#",
    "#..RRRR...pp...BBBB......#",
    "#..RRRR...pp...BBBB......#",
    "#..WWWD...pp...WWWD......#",
    "#.........pp.............#",
    "#..S......pp...S.........#",
    "#..pppppppppppppppppppp..#",
    "#..p......pppp........p..#",
    "#..p..WWWWpppp..WWWW..p..#",
    "#..p..WWWWpppp..WWWW..p..#",
    "#..p..WWWDpppp..WWWD..p..#",
    "#..p......pppp........p..#",
    "#..pppppppppppppppppppp..#",
    "#..p......pppp........p..#",
    "#..p..GGGGpppp..GGGG..p..#",
    "#..p..GGGGpppp..GGGG..p..#",
    "#..p..o...pppp...o....p..#",
    "#..pppppppppppppppppppp..#",
    "#..ssssssssssssssssssss..#",
    "#..ssssssssssssssssssss..#",
    "##########################",
]

MAP_POKECENTER = [
    "############",
    "#..........#",
    "#...CCCC...#",
    "#...CNCC...#",
    "#..........#",
    "#.._....P..#",
    "#.._.......#",
    "#.....D....#",
]

MAP_MART = [
    "############",
    "#..........#",
    "#...CCCC...#",
    "#...CMCC...#",
    "#..........#",
    "#.._.......#",
    "#.....D....#",
    "############",
]

MAP_OAKS_LAB = [
    "############",
    "#K..HHHH..K#",
    "#K..HHHH..K#",
    "#..........#",
    "#...HHHH...#",
    "#...HHHH...#",
    "#..........#",
    "#.._....P..#",
    "#.....D....#",
    "############",
]

MAP_PEWTER_GYM = [
    "############",
    "#Y...^^...Y#",
    "#Y...^^...Y#",
    "#....JJ....#",
    "#....JJ....#",
    "#..........#",
    "#....JJ....#",
    "#....JJ....#",
    "#.....D....#",
    "############",
]

MAP_CERULEAN_GYM = [
    "############",
    "#Y...~~...Y#",
    "#Y...~~...Y#",
    "#....JJ....#",
    "#....JJ....#",
    "#.~~~~~~~~.#",
    "#....JJ....#",
    "#....JJ....#",
    "#.....D....#",
    "############",
]

MAP_BILLS_COTTAGE = [
    "############",
    "#K..HHHH..K#",
    "#..........#",
    "#.._....P..#",
    "#.._.......#",
    "#..........#",
    "#.....D....#",
    "############",
]

MAP_PLAYERS_HOUSE = [
    "##########",
    "#K..HH..K#",
    "#........#",
    "#.._..P..#",
    "#.._.....#",
    "#........#",
    "#....D...#",
    "##########",
]

MAP_MUSEUM = [
    "############",
    "#K..YYYY..K#",
    "#..........#",
    "#...YYYY...#",
    "#..........#",
    "#..........#",
    "#.....D....#",
    "############",
]

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
            {"name": "Town Elder", "x": 5, "y": 7, "dir": Direction.DOWN, "dialog": "Welcome to Pallet Town! Take the path North to explore Route 1, or visit Prof. Oak's Lab!"}
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
            (27, 10): {"target_map": "Viridian City", "target_x": 1, "target_y": 13}
        },
        "trainers": ["rival_blue", "hiker_franklin"],
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
            (16, 31): {"target_map": "Viridian City", "target_x": 12, "target_y": 1},
            (17, 31): {"target_map": "Viridian City", "target_x": 13, "target_y": 1},
            (18, 31): {"target_map": "Viridian City", "target_x": 14, "target_y": 1},
            (19, 31): {"target_map": "Viridian City", "target_x": 15, "target_y": 1},
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
            {"name": "Museum Guide", "x": 20, "y": 15, "dir": Direction.LEFT, "dialog": "Welcome to Pewter City! Check out the Museum of Science, or challenge Leader Brock at the Gym!"}
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
            (12, 0): {"target_map": "Route 24", "target_x": 9, "target_y": 26},
            (13, 0): {"target_map": "Route 24", "target_x": 9, "target_y": 26},
            (14, 0): {"target_map": "Route 24", "target_x": 10, "target_y": 26},
            (15, 0): {"target_map": "Route 24", "target_x": 10, "target_y": 26}
        },
        "npcs": [
            {"name": "Officer Jenny", "x": 18, "y": 9, "dir": Direction.DOWN, "dialog": "Keep an eye out for suspicious Team Rocket grunts! North of here is the famous Nugget Bridge!"}
        ],
        "signs": {
            (3, 6): "Cerulean City - A Mysterious Blue Aura",
            (24, 6): "Cerulean PokéMart",
            (6, 13): "Cerulean Gym - Leader: Misty (The Tomboyish Mermaid!)"
        }
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
    }
}

class Player:
    def __init__(self, x=8, y=6, current_map="Pallet Town", name="Red", gender="Boy", outfit_theme="Classic Red", hat_style="Trainer Cap", hair_color="Dark Brown"):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        self.facing = Direction.DOWN
        self.is_moving = False
        self.move_progress = 0.0 # 0.0 to 1.0
        self.target_x = x
        self.target_y = y
        self.move_speed = 4.0 # tiles per second
        self.walk_frame = 0
        self.step_counter = 0
        self.current_map = current_map
        self.in_tall_grass = False
        self.last_overworld_map = "Pallet Town"
        self.last_overworld_pos = (8, 6)
        
        # Trainer Customization
        self.name = name
        self.gender = gender
        self.outfit_theme = outfit_theme
        self.hat_style = hat_style
        self.hair_color = hair_color
        
        # Sync graphics manager sprites
        gfx.set_custom_player_appearance(self.gender, self.outfit_theme, self.hat_style, self.hair_color)

    def update(self, dt, world):
        if self.is_moving:
            self.move_progress += self.move_speed * dt
            if self.move_progress >= 1.0:
                self.move_progress = 0.0
                self.is_moving = False
                self.grid_x = self.target_x
                self.grid_y = self.target_y
                self.pixel_x = self.grid_x * TILE_SIZE
                self.pixel_y = self.grid_y * TILE_SIZE
                
                # Check tile stepped on
                tile = world.get_tile(self.current_map, self.grid_x, self.grid_y)
                self.in_tall_grass = (tile == 'G')
                
                # Step sound in tall grass
                if self.in_tall_grass:
                    sound_mgr.play_sfx("rustle")
            else:
                self.pixel_x = (self.grid_x + (self.target_x - self.grid_x) * self.move_progress) * TILE_SIZE
                self.pixel_y = (self.grid_y + (self.target_y - self.grid_y) * self.move_progress) * TILE_SIZE
                
            # Update walk animation frame
            self.step_counter += dt * 8
            self.walk_frame = int(self.step_counter) % 3
        else:
            self.walk_frame = 0
            self.pixel_x = self.grid_x * TILE_SIZE
            self.pixel_y = self.grid_y * TILE_SIZE

    def move(self, direction, world):
        if self.is_moving:
            return False
            
        self.facing = direction
        dx, dy = 0, 0
        if direction == Direction.UP:
            dy = -1
        elif direction == Direction.DOWN:
            dy = 1
        elif direction == Direction.LEFT:
            dx = -1
        elif direction == Direction.RIGHT:
            dx = 1
            
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        
        # Check collision
        if world.is_passable(self.current_map, new_x, new_y):
            self.target_x = new_x
            self.target_y = new_y
            self.is_moving = True
            self.move_progress = 0.0
            return True
        return False

    def draw(self, surf, camera_x, camera_y):
        sprite = gfx.player_sprites[self.facing][self.walk_frame]
        draw_x = int(self.pixel_x - camera_x)
        draw_y = int(self.pixel_y - camera_y)
        
        surf.blit(sprite, (draw_x, draw_y))
        
        # If in tall grass, draw grass covering lower feet
        if self.in_tall_grass and not self.is_moving:
            grass_cover = gfx.cached_tiles["tall_grass"].subsurface((0, 16, TILE_SIZE, 16))
            surf.blit(grass_cover, (draw_x, draw_y + 16))

class World:
    def __init__(self):
        self.maps = MAP_DEFINITIONS
        self.defeated_trainers = set()
        self.collected_items = set()
        self.badges = set()
        self.water_anim_timer = 0.0
        self.water_frame = 0
        self.interior_origin_map = "Pallet Town"
        self.interior_origin_coords = (4, 4)

    def update(self, dt):
        self.water_anim_timer += dt
        if self.water_anim_timer >= 0.25:
            self.water_anim_timer = 0.0
            self.water_frame = (self.water_frame + 1) % 4

    def get_tile(self, map_name, x, y):
        grid = self.maps.get(map_name, {}).get("grid", [])
        if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
            return grid[y][x]
        return "#"

    def is_passable(self, map_name, x, y):
        tile = self.get_tile(map_name, x, y)
        # Solid obstacle tiles
        if tile in ["#", "~", "f", "R", "B", "W", "C", "N", "M", "^", "Y", "H", "K"]:
            return False
            
        # Check NPC collisions
        npcs = self.maps[map_name].get("npcs", [])
        for npc in npcs:
            if npc["x"] == x and npc["y"] == y:
                return False
                
        # Check Trainer collisions
        trainer_ids = self.maps[map_name].get("trainers", [])
        for t_data in TRAINERS:
            if t_data["id"] in trainer_ids and t_data["x"] == x and t_data["y"] == y:
                return False
                
        return True

    def get_warp_target(self, map_name, x, y):
        warps = self.maps[map_name].get("warps", {})
        return warps.get((x, y))

    def get_npc_at(self, map_name, x, y):
        npcs = self.maps[map_name].get("npcs", [])
        for npc in npcs:
            if npc["x"] == x and npc["y"] == y:
                return npc
        return None

    def get_trainer_at(self, map_name, x, y):
        trainer_ids = self.maps[map_name].get("trainers", [])
        for t_data in TRAINERS:
            if t_data["id"] in trainer_ids and t_data["id"] not in self.defeated_trainers:
                if t_data["x"] == x and t_data["y"] == y:
                    return t_data
        return None

    def get_any_trainer_at(self, map_name, x, y):
        trainer_ids = self.maps[map_name].get("trainers", [])
        for t_data in TRAINERS:
            if t_data["id"] in trainer_ids and t_data["x"] == x and t_data["y"] == y:
                return t_data
        return None

    def get_sign_at(self, map_name, x, y):
        signs = self.maps[map_name].get("signs", {})
        return signs.get((x, y))

    def get_ground_item_at(self, map_name, x, y):
        items = self.maps[map_name].get("ground_items", [])
        for item_data in items:
            if item_data["x"] == x and item_data["y"] == y and item_data["id"] not in self.collected_items:
                return item_data
        return None

    def check_trainer_line_of_sight(self, map_name, player_x, player_y):
        """Checks if an undefeated trainer spots the player."""
        trainer_ids = self.maps[map_name].get("trainers", [])
        for t_data in TRAINERS:
            if t_data["id"] in trainer_ids and t_data["id"] not in self.defeated_trainers:
                tx, ty = t_data["x"], t_data["y"]
                tdir = t_data["direction"]
                
                # Check direct sight lines up to 4 tiles
                if tdir == "DOWN" and tx == player_x and 0 < player_y - ty <= 4:
                    return t_data
                elif tdir == "UP" and tx == player_x and 0 < ty - player_y <= 4:
                    return t_data
                elif tdir == "LEFT" and ty == player_y and 0 < tx - player_x <= 4:
                    return t_data
                elif tdir == "RIGHT" and ty == player_y and 0 < player_x - tx <= 4:
                    return t_data
        return None

    def draw(self, surf, map_name, camera_x, camera_y):
        grid = self.maps[map_name]["grid"]
        rows = len(grid)
        cols = len(grid[0])
        is_cave = (map_name == "Mt. Moon")
        
        # Calculate visible tile range
        start_col = max(0, int(camera_x // TILE_SIZE))
        end_col = min(cols, int((camera_x + SCREEN_WIDTH) // TILE_SIZE) + 2)
        start_row = max(0, int(camera_y // TILE_SIZE))
        end_row = min(rows, int((camera_y + SCREEN_HEIGHT) // TILE_SIZE) + 2)
        
        for y in range(start_row, end_row):
            for x in range(start_col, end_col):
                char = grid[y][x]
                draw_x = x * TILE_SIZE - camera_x
                draw_y = y * TILE_SIZE - camera_y
                
                # Base ground tile
                if is_cave:
                    surf.blit(gfx.cached_tiles["cave_floor"], (draw_x, draw_y))
                elif char in ["_", "C", "N", "M", "P", "H", "K"]:
                    surf.blit(gfx.cached_tiles["floor"], (draw_x, draw_y))
                elif char in ["J", "Y"]:
                    surf.blit(gfx.cached_tiles["gym_floor"], (draw_x, draw_y))
                elif char in ["s"]:
                    surf.blit(gfx.cached_tiles["sand"], (draw_x, draw_y))
                elif char in ["b"]:
                    surf.blit(gfx.cached_tiles["water"][self.water_frame], (draw_x, draw_y))
                else:
                    surf.blit(gfx.cached_tiles["grass"], (draw_x, draw_y))
                
                # Specialized tile drawing
                if char == "G":
                    surf.blit(gfx.cached_tiles["tall_grass"], (draw_x, draw_y))
                elif char == "p":
                    surf.blit(gfx.cached_tiles["path"], (draw_x, draw_y))
                elif char == "~":
                    surf.blit(gfx.cached_tiles["water"][self.water_frame], (draw_x, draw_y))
                elif char == "b":
                    surf.blit(gfx.cached_tiles["bridge"], (draw_x, draw_y))
                elif char == "s":
                    surf.blit(gfx.cached_tiles["sand"], (draw_x, draw_y))
                elif char == "#":
                    surf.blit(gfx.cached_tiles["tree_tl"], (draw_x, draw_y))
                elif char == "^":
                    surf.blit(gfx.cached_tiles["cave_wall"], (draw_x, draw_y))
                elif char == "O":
                    surf.blit(gfx.cached_tiles["cave_door"], (draw_x, draw_y))
                elif char == "J":
                    surf.blit(gfx.cached_tiles["gym_mat"], (draw_x, draw_y))
                elif char == "Y":
                    surf.blit(gfx.cached_tiles["gym_statue"], (draw_x, draw_y))
                elif char == "H":
                    surf.blit(gfx.cached_tiles["lab_table"], (draw_x, draw_y))
                elif char == "K":
                    surf.blit(gfx.cached_tiles["bookshelf"], (draw_x, draw_y))
                elif char == "f":
                    surf.blit(gfx.cached_tiles["fence"], (draw_x, draw_y))
                elif char == "*":
                    surf.blit(gfx.cached_tiles["flower_red"], (draw_x, draw_y))
                elif char == "R":
                    surf.blit(gfx.cached_tiles["roof_red"], (draw_x, draw_y))
                elif char == "B":
                    surf.blit(gfx.cached_tiles["roof_blue"], (draw_x, draw_y))
                elif char == "W":
                    surf.blit(gfx.cached_tiles["wall_white"], (draw_x, draw_y))
                elif char == "D":
                    surf.blit(gfx.cached_tiles["door"], (draw_x, draw_y))
                elif char == "S":
                    surf.blit(gfx.cached_tiles["sign"], (draw_x, draw_y))
                elif char == "C":
                    surf.blit(gfx.cached_tiles["counter"], (draw_x, draw_y))
                    
        # Draw Ground Collectible Items (if not yet collected)
        ground_items = self.maps[map_name].get("ground_items", [])
        for g_item in ground_items:
            if g_item["id"] not in self.collected_items:
                ix = g_item["x"] * TILE_SIZE - camera_x
                iy = g_item["y"] * TILE_SIZE - camera_y
                surf.blit(gfx.cached_tiles["item_ball"], (ix, iy))

        # Draw NPCs
        npcs = self.maps[map_name].get("npcs", [])
        for npc in npcs:
            nx = npc["x"] * TILE_SIZE - camera_x
            ny = npc["y"] * TILE_SIZE - camera_y
            # Draw NPC sprite
            color = (240, 180, 80)
            if npc.get("is_healer"):
                color = (240, 120, 160) # Pink for Nurse Joy / Mom
            elif npc.get("is_oak"):
                color = (180, 140, 220) # Purple for Prof. Oak
            elif npc.get("is_bill"):
                color = (60, 180, 240) # Cyan for Bill
            pygame.draw.circle(surf, color, (int(nx + TILE_SIZE//2), int(ny + TILE_SIZE//2)), 12)
            pygame.draw.circle(surf, WHITE, (int(nx + TILE_SIZE//2), int(ny + TILE_SIZE//2 - 4)), 6)
            
        # Draw Trainers
        trainer_ids = self.maps[map_name].get("trainers", [])
        for t_data in TRAINERS:
            if t_data["id"] in trainer_ids:
                tx = t_data["x"] * TILE_SIZE - camera_x
                ty = t_data["y"] * TILE_SIZE - camera_y
                is_def = t_data["id"] in self.defeated_trainers
                is_gym_leader = "gym_leader" in t_data["id"]
                
                if is_def:
                    color = (100, 100, 120)
                elif is_gym_leader:
                    color = (240, 180, 20) # Gold for Gym Leaders
                else:
                    color = (220, 60, 60) # Red for standard challengers
                    
                pygame.draw.circle(surf, color, (int(tx + TILE_SIZE//2), int(ty + TILE_SIZE//2)), 13)
                pygame.draw.circle(surf, WHITE, (int(tx + TILE_SIZE//2), int(ty + TILE_SIZE//2 - 4)), 6)
                if not is_def:
                    # Exclamation mark indicator
                    excl_col = (255, 240, 60) if not is_gym_leader else (255, 80, 40)
                    txt = gfx.fonts["small"].render("!", True, excl_col)
                    surf.blit(txt, (tx + 12, ty - 12))

    def get_map_dimensions(self, map_name):
        grid = self.maps[map_name]["grid"]
        return len(grid[0]) * TILE_SIZE, len(grid) * TILE_SIZE
