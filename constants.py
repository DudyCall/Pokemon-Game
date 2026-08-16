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
    "Fairy": (238, 153, 172)
}

# Full 18-Type Matchup Effectiveness Matrix: Attacker -> Defender -> Multiplier
TYPE_CHART = {
    "Normal": {"Rock": 0.5, "Ghost": 0.0, "Steel": 0.5},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0},
    "Water": {"Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0, "Dragon": 0.5},
    "Electric": {"Water": 2.0, "Electric": 0.5, "Grass": 0.5, "Ground": 0.0, "Flying": 2.0, "Dragon": 0.5},
    "Grass": {"Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5, "Ground": 2.0, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0, "Dragon": 0.5, "Steel": 0.5},
    "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 0.5, "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5},
    "Fighting": {"Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2.0, "Ghost": 0.0, "Steel": 2.0, "Fairy": 0.5},
    "Poison": {"Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0.0, "Fairy": 2.0},
    "Ground": {"Fire": 2.0, "Electric": 2.0, "Grass": 0.5, "Poison": 2.0, "Flying": 0.0, "Bug": 0.5, "Rock": 2.0, "Steel": 2.0},
    "Flying": {"Electric": 0.5, "Grass": 2.0, "Fighting": 2.0, "Bug": 2.0, "Rock": 0.5, "Steel": 0.5},
    "Psychic": {"Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Steel": 0.5},
    "Bug": {"Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2.0, "Ghost": 0.5, "Steel": 0.5, "Fairy": 0.5},
    "Rock": {"Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5, "Flying": 2.0, "Bug": 2.0, "Steel": 0.5},
    "Ghost": {"Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0},
    "Dragon": {"Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0},
    "Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0, "Rock": 2.0, "Steel": 0.5, "Fairy": 2.0},
    "Fairy": {"Fire": 0.5, "Fighting": 2.0, "Poison": 0.5, "Dragon": 2.0, "Steel": 0.5}
}

# Game States
class GameState:
    TITLE = "TITLE"
    STARTER_SELECT = "STARTER_SELECT"
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
KEY_CANCEL = [pygame.K_x, pygame.K_ESCAPE, pygame.K_BACKSPACE]
KEY_MENU = [pygame.K_c, pygame.K_TAB, pygame.K_m]
KEY_QUICKSAVE = [pygame.K_F5, pygame.K_k]
