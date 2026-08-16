"""
world.py - Overworld map management, player movement, collision detection,
tall grass encounters, NPC dialogues, and building interiors.
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
# " = Tall Grass (Wild Pokemon encounter)
# # = Tree (Solid obstacle)
# ~ = Water (Solid obstacle)
# p = Path / Sand
# f = Fence (Solid obstacle)
# * = Red Flower
# R = PokeCenter Red Roof
# B = Mart Blue Roof
# W = White Building Wall
# D = Building Door (Warp)
# S = Wooden Sign
# _ = Indoor Floor
# C = Indoor Counter
# N = Nurse Joy NPC
# M = Mart Clerk NPC
# P = PC Terminal

MAP_PALLET_TOWN = [
    "########....##########",
    "#......pppppp........#",
    "#..RR..p....p..WWWW..#",
    "#..RR..p....p..WWWW..#",
    "#..WD..p....p..WWWD..#",
    "#......p....p........#",
    "#..**..pppppp..**....#",
    "#......p....p........#",
    "#..ff..p....p..ff....#",
    "#......pppppp........#",
    "#........pp..........#",
    "#........pp..........#",
    "######################",
]

MAP_ROUTE_1 = [
    "########....##########",
    "#........pp..........#",
    "#..GGGG..pp..GGGG....#",
    "#..GGGG..pp..GGGG....#",
    "#..GGGG..pp..GGGG....#",
    "#........pp..........#",
    "#..ffff..pp..ffff....#",
    "#........pp..........#",
    "#..GGGG..pp..GGGG....#",
    "#..GGGG..pp..GGGG....#",
    "#........pp..........#",
    "#..GGGG..pp..GGGG....#",
    "#..GGGG..pp..GGGG....#",
    "#........pp..........#",
    "#..ffff..pp..........#",
    "#........pp..GGGG....#",
    "#........pp..GGGG....#",
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
    "#..********..pp..********..#",
    "#..pppppppppppppppppppppp..#",
    "#..p........pppp........p..#",
    "#..p..GGGG..pppp..GGGG..p..#",
    "#..p..GGGG..pppp..GGGG..p..#",
    "#..pppppppppppppppppppppp..#",
    "#............pp............#",
    "############....############",
]

MAP_VIRIDIAN_FOREST = [
    "################################",
    "#..............................#",
    "#..GGGG..####..GGGG..####..GG..#",
    "#..GGGG..####..GGGG..####..GG..#",
    "#..pp....####..pp....####..pp..#",
    "#..pp..........pp..........pp..#",
    "#..pppppppppppppppppppppppppp..#",
    "#..pp..........pp..........pp..#",
    "#..GG..####....GG..####....GG..#",
    "#..GG..####....GG..####....GG..#",
    "#..pppppppppppppppppppppppppp..#",
    "#..GGGG..GGGG..GGGG..GGGG..GG..#",
    "#..............................#",
    "################....############",
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

MAP_DEFINITIONS = {
    "Pallet Town": {
        "grid": MAP_PALLET_TOWN,
        "bgm": "town",
        "warps": {
            (4, 4): {"target_map": "Pokecenter", "target_x": 6, "target_y": 6},
            (18, 4): {"target_map": "Mart", "target_x": 6, "target_y": 5},
            (8, 0): {"target_map": "Route 1", "target_x": 8, "target_y": 19},
            (9, 0): {"target_map": "Route 1", "target_x": 9, "target_y": 19},
            (10, 0): {"target_map": "Route 1", "target_x": 10, "target_y": 19},
            (11, 0): {"target_map": "Route 1", "target_x": 11, "target_y": 19}
        },
        "npcs": [
            {"name": "Town Elder", "x": 5, "y": 7, "dir": Direction.DOWN, "dialog": "Welcome to Pallet Town! Take the path North to explore Route 1!"}
        ]
    },
    "Route 1": {
        "grid": MAP_ROUTE_1,
        "bgm": "town",
        "encounter_zone": "Route 1",
        "warps": {
            (8, 20): {"target_map": "Pallet Town", "target_x": 8, "target_y": 1},
            (9, 20): {"target_map": "Pallet Town", "target_x": 9, "target_y": 1},
            (10, 20): {"target_map": "Pallet Town", "target_x": 10, "target_y": 1},
            (11, 20): {"target_map": "Pallet Town", "target_x": 11, "target_y": 1},
            (8, 0): {"target_map": "Viridian City", "target_x": 12, "target_y": 12},
            (9, 0): {"target_map": "Viridian City", "target_x": 13, "target_y": 12},
            (10, 0): {"target_map": "Viridian City", "target_x": 14, "target_y": 12},
            (11, 0): {"target_map": "Viridian City", "target_x": 15, "target_y": 12}
        },
        "trainers": ["youngster_joey", "bug_catcher_sammy"]
    },
    "Viridian City": {
        "grid": MAP_VIRIDIAN_CITY,
        "bgm": "town",
        "warps": {
            (12, 13): {"target_map": "Route 1", "target_x": 8, "target_y": 1},
            (13, 13): {"target_map": "Route 1", "target_x": 9, "target_y": 1},
            (14, 13): {"target_map": "Route 1", "target_x": 10, "target_y": 1},
            (15, 13): {"target_map": "Route 1", "target_x": 11, "target_y": 1},
            (6, 4): {"target_map": "Pokecenter", "target_x": 6, "target_y": 6},
            (24, 4): {"target_map": "Mart", "target_x": 6, "target_y": 5},
            (12, 0): {"target_map": "Viridian Forest", "target_x": 16, "target_y": 12},
            (13, 0): {"target_map": "Viridian Forest", "target_x": 17, "target_y": 12},
            (14, 0): {"target_map": "Viridian Forest", "target_x": 18, "target_y": 12},
            (15, 0): {"target_map": "Viridian Forest", "target_x": 19, "target_y": 12}
        },
        "trainers": ["lass_haley"]
    },
    "Viridian Forest": {
        "grid": MAP_VIRIDIAN_FOREST,
        "bgm": "town",
        "encounter_zone": "Viridian Forest",
        "warps": {
            (16, 13): {"target_map": "Viridian City", "target_x": 12, "target_y": 1},
            (17, 13): {"target_map": "Viridian City", "target_x": 13, "target_y": 1},
            (18, 13): {"target_map": "Viridian City", "target_x": 14, "target_y": 1},
            (19, 13): {"target_map": "Viridian City", "target_x": 15, "target_y": 1}
        },
        "trainers": ["gym_leader_brock"]
    },
    "Pokecenter": {
        "grid": MAP_POKECENTER,
        "bgm": "town",
        "warps": {
            (6, 7): {"target_map": "Pallet Town", "target_x": 4, "target_y": 5}
        },
        "npcs": [
            {"name": "Nurse Joy", "x": 5, "y": 3, "dir": Direction.DOWN, "dialog": "Welcome to our Pokémon Center! We heal your Pokémon back to full health!", "is_healer": True}
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
    }
}

class Player:
    def __init__(self, x=8, y=6, current_map="Pallet Town"):
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
        grid = self.maps[map_name]["grid"]
        if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
            return grid[y][x]
        return "#"

    def is_passable(self, map_name, x, y):
        tile = self.get_tile(map_name, x, y)
        # Solid obstacle tiles
        if tile in ["#", "~", "f", "R", "B", "W", "C", "N", "M"]:
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
                if char in ["_", "C", "N", "M", "P"]:
                    surf.blit(gfx.cached_tiles["floor"], (draw_x, draw_y))
                else:
                    surf.blit(gfx.cached_tiles["grass"], (draw_x, draw_y))
                
                # Specialized tile drawing
                if char == "G":
                    surf.blit(gfx.cached_tiles["tall_grass"], (draw_x, draw_y))
                elif char == "p":
                    surf.blit(gfx.cached_tiles["path"], (draw_x, draw_y))
                elif char == "~":
                    surf.blit(gfx.cached_tiles["water"][self.water_frame], (draw_x, draw_y))
                elif char == "#":
                    # Tree
                    surf.blit(gfx.cached_tiles["tree_tl"], (draw_x, draw_y))
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
                    
        # Draw NPCs
        npcs = self.maps[map_name].get("npcs", [])
        for npc in npcs:
            nx = npc["x"] * TILE_SIZE - camera_x
            ny = npc["y"] * TILE_SIZE - camera_y
            # Draw NPC sprite
            pygame.draw.circle(surf, (240, 180, 80), (int(nx + TILE_SIZE//2), int(ny + TILE_SIZE//2)), 12)
            pygame.draw.circle(surf, WHITE, (int(nx + TILE_SIZE//2), int(ny + TILE_SIZE//2 - 4)), 6)
            
        # Draw Trainers
        trainer_ids = self.maps[map_name].get("trainers", [])
        for t_data in TRAINERS:
            if t_data["id"] in trainer_ids:
                tx = t_data["x"] * TILE_SIZE - camera_x
                ty = t_data["y"] * TILE_SIZE - camera_y
                is_def = t_data["id"] in self.defeated_trainers
                color = (100, 100, 120) if is_def else (220, 60, 60)
                pygame.draw.circle(surf, color, (int(tx + TILE_SIZE//2), int(ty + TILE_SIZE//2)), 12)
                pygame.draw.circle(surf, WHITE, (int(tx + TILE_SIZE//2), int(ty + TILE_SIZE//2 - 4)), 6)
                if not is_def:
                    # Exclamation mark indicator
                    txt = gfx.fonts["small"].render("!", True, (240, 240, 40))
                    surf.blit(txt, (tx + 12, ty - 12))

    def get_map_dimensions(self, map_name):
        grid = self.maps[map_name]["grid"]
        return len(grid[0]) * TILE_SIZE, len(grid) * TILE_SIZE
