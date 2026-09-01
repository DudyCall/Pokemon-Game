"""
constants.py - Global constants, color palettes, type chart, and control mappings.
"""
import pygame

# Screen Configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
FPS = 60

# Color Palette (GBA / Classic inspired)
BLACK = (16, 16, 20)
WHITE = (248, 248, 252)
GRAY = (140, 145, 160)
DARK_GRAY = (48, 52, 64)
LIGHT_GRAY = (216, 220, 230)

# UI Colors
UI_BG = (240, 244, 248)
UI_BORDER_DARK = (40, 48, 72)
UI_BORDER_LIGHT = (112, 136, 180)
UI_TEXT = (24, 28, 40)
UI_TEXT_MUTED = (100, 110, 130)

# HP & Status Colors
HP_GREEN = (64, 208, 96)
HP_YELLOW = (240, 192, 48)
HP_RED = (232, 64, 64)
EXP_BLUE = (64, 160, 240)

# Status Condition Badge Colors & Abbreviations
STATUS_COLORS = {
    "Paralysis": {"abbr": "PAR", "bg": (235, 180, 20), "border": (170, 120, 0), "text": (255, 255, 255), "shadow": (60, 40, 0)},
    "Burn": {"abbr": "BRN", "bg": (235, 75, 30), "border": (160, 30, 10), "text": (255, 255, 255), "shadow": (60, 10, 0)},
    "Poison": {"abbr": "PSN", "bg": (160, 60, 180), "border": (100, 20, 120), "text": (255, 255, 255), "shadow": (40, 10, 50)},
    "Sleep": {"abbr": "SLP", "bg": (120, 135, 155), "border": (75, 85, 105), "text": (255, 255, 255), "shadow": (30, 35, 45)},
    "Freeze": {"abbr": "FRZ", "bg": (50, 190, 220), "border": (20, 130, 160), "text": (255, 255, 255), "shadow": (10, 50, 70)},
    "Frozen": {"abbr": "FRZ", "bg": (50, 190, 220), "border": (20, 130, 160), "text": (255, 255, 255), "shadow": (10, 50, 70)},
    "Fainted": {"abbr": "FNT", "bg": (130, 40, 40), "border": (80, 20, 20), "text": (255, 255, 255), "shadow": (30, 10, 10)}
}

# Type Colors
TYPE_COLORS = {
    "Normal": (168, 168, 120),
    "Fire": (240, 128, 48),
    "Water": (104, 144, 240),
    "Electric": (248, 208, 48),
    "Grass": (120, 200, 80),
    "Ice": (152, 216, 216),
    "Fighting": (192, 48, 40),
    "Poison": (160, 64, 160),
    "Ground": (224, 192, 104),
    "Flying": (168, 144, 240),
    "Psychic": (248, 88, 136),
    "Bug": (168, 184, 32),
    "Rock": (184, 160, 56),
    "Ghost": (112, 88, 152),
    "Dragon": (112, 56, 248),
    "Steel": (184, 184, 208),
    "Fairy": (238, 153, 172),
    "Dark": (112, 88, 72)
}

# Full 18-Type Matchup Effectiveness Matrix: Attacker -> Defender -> Multiplier
TYPE_CHART = {
    "Normal": {"Rock": 0.5, "Ghost": 0.0, "Steel": 0.5},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0},
    "Water": {"Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0, "Dragon": 0.5},
    "Electric": {"Water": 2.0, "Electric": 0.5, "Grass": 0.5, "Ground": 0.0, "Flying": 2.0, "Dragon": 0.5},
    "Grass": {"Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5, "Ground": 2.0, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0, "Dragon": 0.5, "Steel": 0.5},
    "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 0.5, "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5},
    "Fighting": {"Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2.0, "Ghost": 0.0, "Steel": 2.0, "Fairy": 0.5, "Dark": 2.0},
    "Poison": {"Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0.0, "Fairy": 2.0},
    "Ground": {"Fire": 2.0, "Electric": 2.0, "Grass": 0.5, "Poison": 2.0, "Flying": 0.0, "Bug": 0.5, "Rock": 2.0, "Steel": 2.0},
    "Flying": {"Electric": 0.5, "Grass": 2.0, "Fighting": 2.0, "Bug": 2.0, "Rock": 0.5, "Steel": 0.5},
    "Psychic": {"Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Steel": 0.5, "Dark": 0.0},
    "Bug": {"Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2.0, "Ghost": 0.5, "Steel": 0.5, "Fairy": 0.5, "Dark": 2.0},
    "Rock": {"Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5, "Flying": 2.0, "Bug": 2.0, "Steel": 0.5},
    "Ghost": {"Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5},
    "Dragon": {"Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0},
    "Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0, "Rock": 2.0, "Steel": 0.5, "Fairy": 2.0},
    "Fairy": {"Fire": 0.5, "Fighting": 2.0, "Poison": 0.5, "Dragon": 2.0, "Steel": 0.5, "Dark": 2.0},
    "Dark": {"Psychic": 2.0, "Ghost": 2.0, "Fighting": 0.5, "Dark": 0.5, "Fairy": 0.5}
}

# Game States
class GameState:
    TITLE = "TITLE"
    TRAINER_CUSTOMIZE = "TRAINER_CUSTOMIZE"
    STARTER_SELECT = "STARTER_SELECT"
    SAVE_SLOTS = "SAVE_SLOTS"
    OVERWORLD = "OVERWORLD"
    BATTLE = "BATTLE"
    PARTY_MENU = "PARTY_MENU"
    BAG_MENU = "BAG_MENU"
    POKEDEX = "POKEDEX"
    DIALOGUE = "DIALOGUE"
    SHOP = "SHOP"
    EVOLUTION = "EVOLUTION"
    TRAINER_CARD = "TRAINER_CARD"
    SAVE = "SAVE"
    PC_BOX = "PC_BOX"
    MOVE_RELEARN = "MOVE_RELEARN"
    QUEST_LOG = "QUEST_LOG"

# Trainer Customization Presets
OUTFIT_THEMES = {
    "Classic Red": {"shirt": (220, 40, 40), "pants": (30, 60, 120), "hat": (200, 30, 30), "accent": WHITE},
    "Ocean Blue": {"shirt": (30, 100, 220), "pants": (20, 30, 60), "hat": (20, 80, 190), "accent": (240, 240, 255)},
    "Emerald Green": {"shirt": (30, 160, 60), "pants": (70, 50, 40), "hat": (20, 130, 50), "accent": (255, 230, 120)},
    "Shadow Black": {"shirt": (40, 40, 45), "pants": (25, 25, 30), "hat": (35, 35, 40), "accent": (220, 60, 60)},
    "Electric Gold": {"shirt": (240, 180, 20), "pants": (50, 50, 60), "hat": (220, 160, 10), "accent": (30, 30, 30)},
    "Cherry Pink": {"shirt": (230, 70, 130), "pants": (240, 240, 245), "hat": (220, 50, 110), "accent": WHITE},
    "Lavender Purple": {"shirt": (140, 80, 200), "pants": (40, 40, 60), "hat": (120, 60, 180), "accent": (255, 215, 0)}
}

HAIR_COLORS = {
    "Dark Brown": (70, 40, 20),
    "Golden Blonde": (235, 195, 75),
    "Raven Black": (25, 25, 30),
    "Auburn Red": (160, 55, 25),
    "Silver Gray": (180, 185, 195)
}

HAT_STYLES = ["Trainer Cap", "Bandana", "Beanie", "No Hat"]
STARTER_CHOICES = ["Charmander", "Squirtle", "Bulbasaur", "Pikachu", "Eevee"]

# Directions
class Direction:
    DOWN = 0
    UP = 1
    LEFT = 2
    RIGHT = 3

# Key Controls
KEY_UP = [pygame.K_UP, pygame.K_w]
KEY_DOWN = [pygame.K_DOWN, pygame.K_s]
KEY_LEFT = [pygame.K_LEFT, pygame.K_a]
KEY_RIGHT = [pygame.K_RIGHT, pygame.K_d]
KEY_CONFIRM = [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]
KEY_CANCEL = [pygame.K_x, pygame.K_ESCAPE]
KEY_MENU = [pygame.K_c, pygame.K_m, pygame.K_TAB]
KEY_QUICKSAVE = [pygame.K_F5, pygame.K_k]

# Walk-Through Wild Encounter Props
ENCOUNTER_PROP_TILES = {
    'G': {"name": "Tall Grass", "sfx": "rustle", "minimap_color": (45, 135, 40), "desc": "Wild grass habitat"},
    'F': {"name": "Wildflower Meadow", "sfx": "flower_step", "minimap_color": (245, 110, 180), "desc": "Blooming flower meadow"},
    '*': {"name": "Wildflower Patch", "sfx": "flower_step", "minimap_color": (245, 110, 180), "desc": "Blooming flower patch"},
    'L': {"name": "Autumn Leaf Pile", "sfx": "leaves_step", "minimap_color": (225, 130, 45), "desc": "Crisp rustling fallen leaves"},
    'r': {"name": "Cave Rubble", "sfx": "rubble_step", "minimap_color": (150, 125, 105), "desc": "Fractured rocks and mineral gravel"},
    'x': {"name": "Snow Drift", "sfx": "snow_step", "minimap_color": (220, 245, 255), "desc": "Deep powdery snow drift"},
    'm': {"name": "Haunted Mist", "sfx": "mist_step", "minimap_color": (165, 105, 215), "desc": "Swirling spiritual mist wisps"},
    'a': {"name": "Volcanic Ash", "sfx": "ash_step", "minimap_color": (195, 60, 50), "desc": "Warm volcanic ash with embers"},
    'u': {"name": "Swamp Marsh", "sfx": "mud_step", "minimap_color": (70, 140, 115), "desc": "Murky marsh water and mud"},
    'e': {"name": "Electric Surge Grid", "sfx": "spark_step", "minimap_color": (245, 220, 50), "desc": "Charged electrical static conduit"}
}

