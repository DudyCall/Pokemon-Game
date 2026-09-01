"""
world.py - Overworld world manager, camera tracking, tile rendering, collision detection, and NPCs.
"""
import math
import random
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, Direction,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, WHITE, BLACK, ENCOUNTER_PROP_TILES
)
from graphics_manager import gfx
from sound_manager import sound_mgr
from pokemon_data import WILD_ENCOUNTERS, TRAINERS
from map_data import MAP_DEFINITIONS
from player import Player
from barrier_system import barrier_mgr

class World:
    def __init__(self):
        self.maps = MAP_DEFINITIONS
        self.defeated_trainers = set()
        self.collected_items = set()
        self.badges = set()
        self.unlocked_barriers = set()
        self.explored_tiles = {} # map_name -> set of (x, y) tuples
        self.timer = 0.0
        self.water_anim_timer = 0.0
        self.water_frame = 0
        self.interior_origin_map = "Pallet Town"
        self.interior_origin_coords = (4, 4)

    def update(self, dt):
        self.timer += dt
        self.water_anim_timer += dt
        if self.water_anim_timer >= 0.25:
            self.water_anim_timer = 0.0
            self.water_frame = (self.water_frame + 1) % 4

    def reveal_area(self, map_name, center_x, center_y, radius=3):
        """Reveals tiles around (center_x, center_y) for the minimap fog-of-war."""
        if map_name not in self.explored_tiles:
            self.explored_tiles[map_name] = set()
        grid = self.maps.get(map_name, {}).get("grid", [])
        if not grid:
            return
        rows = len(grid)
        cols = len(grid[0])
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx = center_x + dx
                ny = center_y + dy
                if 0 <= ny < rows and 0 <= nx < cols:
                    if dx * dx + dy * dy <= (radius + 0.5) ** 2:
                        self.explored_tiles[map_name].add((nx, ny))

    def get_tile(self, map_name, x, y):
        grid = self.maps.get(map_name, {}).get("grid", [])
        if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
            return grid[y][x]
        return "#"

    def is_passable(self, map_name, x, y, can_sail=False):
        tile = self.get_tile(map_name, x, y)
        if tile == "~":
            if not can_sail:
                return False
        elif tile in ["#", "f", "R", "B", "W", "C", "N", "M", "^", "Y", "H", "K"]:
            return False
            
        # Check Progression Barrier collisions
        if barrier_mgr.is_tile_blocked(map_name, x, y, self.unlocked_barriers):
            return False

        # Check NPC collisions
        npcs = self.maps[map_name].get("npcs", [])
        for npc in npcs:
            if npc["x"] == x and npc["y"] == y:
                return False
                
        # Check Trainer collisions
        trainer_ids = self.maps[map_name].get("trainers", [])
        for t_data in TRAINERS:
            if t_data["id"] in trainer_ids and t_data["id"] not in self.defeated_trainers:
                if t_data["x"] == x and t_data["y"] == y:
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

    def draw(self, surf, map_name, camera_x, camera_y, quest_mgr=None):
        grid = self.maps[map_name]["grid"]
        rows = len(grid)
        cols = len(grid[0])
        is_cave = (map_name in ["Mt. Moon", "Diglett's Cave", "Victory Road", "Cerulean Cave", "Seafoam Islands"])
        is_ice = (map_name == "Seafoam Islands")
        is_lavender = (map_name in ["Lavender Town", "Pokémon Tower"])
        is_tower = (map_name == "Pokémon Tower")
        is_power_plant = (map_name == "Power Plant")
        is_safari = (map_name == "Safari Zone")
        is_canyon = (map_name in ["Route 9", "Route 3", "Route 4"])
        is_house_indoor = ("House" in map_name or "Cottage" in map_name)
        is_center_indoor = ("Pokecenter" in map_name)
        is_mart_indoor = ("Mart" in map_name)
        is_lab_indoor = ("Lab" in map_name or "Silph" in map_name)
        is_gym_indoor = ("Gym" in map_name or "Dojo" in map_name)
        
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
                if is_ice:
                    surf.blit(gfx.cached_tiles["ice_floor"], (draw_x, draw_y))
                elif is_cave:
                    surf.blit(gfx.cached_tiles["cave_floor"], (draw_x, draw_y))
                elif is_power_plant:
                    surf.blit(gfx.cached_tiles["metal_floor"], (draw_x, draw_y))
                elif is_tower:
                    surf.blit(gfx.cached_tiles["spooky_floor"], (draw_x, draw_y))
                elif is_lavender:
                    surf.blit(gfx.cached_tiles["lavender_ground"], (draw_x, draw_y))
                elif is_safari:
                    surf.blit(gfx.cached_tiles["savanna_grass"], (draw_x, draw_y))
                elif is_canyon:
                    surf.blit(gfx.cached_tiles["canyon_dirt"], (draw_x, draw_y))
                elif is_house_indoor and char in ["_", "C", "N", "M", "P", "H", "K"]:
                    surf.blit(gfx.cached_tiles["floor_house"], (draw_x, draw_y))
                elif is_center_indoor and char in ["_", "C", "N", "M", "P", "H", "K"]:
                    surf.blit(gfx.cached_tiles["floor_center"], (draw_x, draw_y))
                elif is_mart_indoor and char in ["_", "C", "N", "M", "P", "H", "K"]:
                    surf.blit(gfx.cached_tiles["floor_mart"], (draw_x, draw_y))
                elif is_lab_indoor and char in ["_", "C", "N", "M", "P", "H", "K"]:
                    surf.blit(gfx.cached_tiles["floor_lab"], (draw_x, draw_y))
                elif char in ["_", "C", "N", "M", "P", "H", "K"]:
                    surf.blit(gfx.cached_tiles["floor_house"] if is_house_indoor else gfx.cached_tiles["floor_center"], (draw_x, draw_y))
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
                    surf.blit(gfx.cached_tiles["savanna_tall_grass"] if is_safari else gfx.cached_tiles["tall_grass"], (draw_x, draw_y))
                elif char == "F":
                    surf.blit(gfx.cached_tiles["flower_meadow"], (draw_x, draw_y))
                elif char == "*":
                    if is_house_indoor:
                        surf.blit(gfx.cached_tiles["potted_plant"], (draw_x, draw_y))
                    else:
                        surf.blit(gfx.cached_tiles["flower_red"], (draw_x, draw_y))
                elif char == "L":
                    surf.blit(gfx.cached_tiles["leaf_pile"], (draw_x, draw_y))
                elif char == "r":
                    surf.blit(gfx.cached_tiles["cave_rubble"], (draw_x, draw_y))
                elif char == "x":
                    surf.blit(gfx.cached_tiles["snow_drift"], (draw_x, draw_y))
                elif char == "m":
                    surf.blit(gfx.cached_tiles["spooky_mist"], (draw_x, draw_y))
                elif char == "a":
                    surf.blit(gfx.cached_tiles["volcanic_ash"], (draw_x, draw_y))
                elif char == "u":
                    surf.blit(gfx.cached_tiles["swamp_marsh"], (draw_x, draw_y))
                elif char == "e":
                    surf.blit(gfx.cached_tiles["electric_surge"], (draw_x, draw_y))
                elif char == "p":
                    surf.blit(gfx.cached_tiles["canyon_dirt"] if is_canyon else gfx.cached_tiles["path"], (draw_x, draw_y))
                elif char == "~":
                    surf.blit(gfx.cached_tiles["water"][self.water_frame], (draw_x, draw_y))
                elif char == "b":
                    surf.blit(gfx.cached_tiles["bridge"], (draw_x, draw_y))
                elif char == "s":
                    surf.blit(gfx.cached_tiles["sand"], (draw_x, draw_y))
                elif char == "#":
                    if is_lavender or is_tower:
                        surf.blit(gfx.cached_tiles["spooky_tree"], (draw_x, draw_y))
                    elif is_safari:
                        surf.blit(gfx.cached_tiles["acacia_tree"], (draw_x, draw_y))
                    elif is_cave:
                        surf.blit(gfx.cached_tiles["cave_wall"], (draw_x, draw_y))
                    else:
                        surf.blit(gfx.cached_tiles["tree_tl"], (draw_x, draw_y))
                elif char == "^":
                    if is_ice:
                        surf.blit(gfx.cached_tiles["ice_wall"], (draw_x, draw_y))
                    elif is_canyon:
                        surf.blit(gfx.cached_tiles["canyon_rock"], (draw_x, draw_y))
                    else:
                        surf.blit(gfx.cached_tiles["cave_wall"], (draw_x, draw_y))
                elif char == "O":
                    # Bespoke dungeon entrance facades
                    if is_ice or map_name in ["Seafoam Islands", "Route 21"]:
                        surf.blit(gfx.cached_tiles["cave_door_seafoam"], (draw_x, draw_y))
                    elif map_name in ["Mt. Moon", "Route 3", "Route 4"]:
                        surf.blit(gfx.cached_tiles["cave_door_mt_moon"], (draw_x, draw_y))
                    elif map_name in ["Viridian Forest", "Route 2"]:
                        surf.blit(gfx.cached_tiles["cave_door_forest"], (draw_x, draw_y))
                    elif map_name in ["Diglett's Cave", "Route 11"]:
                        surf.blit(gfx.cached_tiles["cave_door_diglett"], (draw_x, draw_y))
                    elif map_name in ["Route 9", "Power Plant"]:
                        surf.blit(gfx.cached_tiles["gate_power_plant"], (draw_x, draw_y))
                    elif map_name in ["Lavender Town", "Pokémon Tower"]:
                        surf.blit(gfx.cached_tiles["gate_pokemon_tower"], (draw_x, draw_y))
                    elif map_name in ["Fuchsia City", "Safari Zone"]:
                        surf.blit(gfx.cached_tiles["gate_safari_zone"], (draw_x, draw_y))
                    elif map_name in ["Vermilion City", "S.S. Anne"]:
                        surf.blit(gfx.cached_tiles["pier_ss_anne"], (draw_x, draw_y))
                    elif map_name in ["Route 22", "Victory Road"]:
                        surf.blit(gfx.cached_tiles["cave_door_victory"], (draw_x, draw_y))
                    elif map_name in ["Indigo Plateau"]:
                        surf.blit(gfx.cached_tiles["gate_indigo_plateau"], (draw_x, draw_y))
                    elif map_name in ["Cerulean City", "Cerulean Cave"]:
                        surf.blit(gfx.cached_tiles["cave_door_cerulean_cave"], (draw_x, draw_y))
                    else:
                        surf.blit(gfx.cached_tiles["cave_door"], (draw_x, draw_y))
                elif char == "J":
                    surf.blit(gfx.cached_tiles["gym_mat"], (draw_x, draw_y))
                elif char == "Y":
                    if is_lavender or is_tower:
                        surf.blit(gfx.cached_tiles["tombstone"], (draw_x, draw_y))
                    else:
                        surf.blit(gfx.cached_tiles["gym_statue"], (draw_x, draw_y))
                elif char == "H":
                    # Roofs on overworld vs furniture indoor
                    if is_house_indoor:
                        surf.blit(gfx.cached_tiles["kitchen_sink"], (draw_x, draw_y))
                    elif is_lab_indoor:
                        surf.blit(gfx.cached_tiles["lab_table"], (draw_x, draw_y))
                    elif is_power_plant:
                        surf.blit(gfx.cached_tiles["generator_coil"], (draw_x, draw_y))
                    elif map_name == "Pallet Town" and x >= 14:
                        surf.blit(gfx.cached_tiles["roof_oak_lab"], (draw_x, draw_y))
                    elif map_name == "Celadon City" and x >= 10 and x <= 22 and y <= 4:
                        surf.blit(gfx.cached_tiles["roof_dept_store"], (draw_x, draw_y))
                    elif map_name == "Saffron City" and y >= 12 and y <= 16:
                        surf.blit(gfx.cached_tiles["roof_silph_co"], (draw_x, draw_y))
                    elif "Gym" in map_name:
                        surf.blit(gfx.cached_tiles["roof_gym"], (draw_x, draw_y))
                    else:
                        surf.blit(gfx.cached_tiles["roof_house"], (draw_x, draw_y))
                elif char == "K":
                    surf.blit(gfx.cached_tiles["bookshelf"], (draw_x, draw_y))
                elif char == "f":
                    surf.blit(gfx.cached_tiles["fence"], (draw_x, draw_y))
                elif char == "R":
                    surf.blit(gfx.cached_tiles["roof_red"], (draw_x, draw_y))
                elif char == "B":
                    surf.blit(gfx.cached_tiles["roof_blue"], (draw_x, draw_y))
                elif char == "W":
                    if is_power_plant:
                        surf.blit(gfx.cached_tiles["warning_tile"], (draw_x, draw_y))
                    elif is_tower:
                        surf.blit(gfx.cached_tiles["spooky_tree"], (draw_x, draw_y))
                    elif map_name == "Pallet Town" and x >= 14:
                        surf.blit(gfx.cached_tiles["wall_oak_lab"], (draw_x, draw_y))
                    elif "Gym" in map_name:
                        surf.blit(gfx.cached_tiles["wall_gym"], (draw_x, draw_y))
                    elif map_name == "Celadon City" and x >= 10 and x <= 22 and y <= 6:
                        surf.blit(gfx.cached_tiles["wall_dept_store"], (draw_x, draw_y))
                    elif map_name == "Saffron City" and y >= 12 and y <= 18:
                        surf.blit(gfx.cached_tiles["wall_silph_co"], (draw_x, draw_y))
                    else:
                        # Context-aware house wall: upper wall has window & flower planter box, lower wall has brick base
                        is_upper_wall = (y + 1 < rows and grid[y + 1][x] in ["W", "D"])
                        if is_upper_wall:
                            surf.blit(gfx.cached_tiles["wall_house_window"], (draw_x, draw_y))
                        else:
                            surf.blit(gfx.cached_tiles["wall_house"], (draw_x, draw_y))
                elif char == "D":
                    if map_name == "Pallet Town" and x >= 14:
                        surf.blit(gfx.cached_tiles["door_lab"], (draw_x, draw_y))
                    elif map_name in ["Lavender Town", "Pokémon Tower"]:
                        surf.blit(gfx.cached_tiles["gate_pokemon_tower"], (draw_x, draw_y))
                    elif map_name in ["Power Plant"]:
                        surf.blit(gfx.cached_tiles["gate_power_plant"], (draw_x, draw_y))
                    elif "Gym" in map_name:
                        surf.blit(gfx.cached_tiles["door_gym"], (draw_x, draw_y))
                    else:
                        # Check if door belongs to PokeCenter (near R) or Mart (near B)
                        near_r = any(
                            0 <= cy < rows and 0 <= cx < cols and grid[cy][cx] == "R"
                            for cy in range(max(0, y - 3), min(rows, y + 1))
                            for cx in range(max(0, x - 3), min(cols, x + 4))
                        )
                        near_b = any(
                            0 <= cy < rows and 0 <= cx < cols and grid[cy][cx] == "B"
                            for cy in range(max(0, y - 3), min(rows, y + 1))
                            for cx in range(max(0, x - 3), min(cols, x + 4))
                        )
                        if near_r:
                            surf.blit(gfx.cached_tiles["door_center"], (draw_x, draw_y))
                        elif near_b:
                            surf.blit(gfx.cached_tiles["door_mart"], (draw_x, draw_y))
                        else:
                            surf.blit(gfx.cached_tiles["door_house"], (draw_x, draw_y))
                elif char == "S":
                    surf.blit(gfx.cached_tiles["sign"], (draw_x, draw_y))
                elif char == "C":
                    surf.blit(gfx.cached_tiles["counter"], (draw_x, draw_y))

                    
        # Draw Active Progression Barriers / Roadblocks
        active_barriers = barrier_mgr.get_active_barriers_for_map(map_name, self.unlocked_barriers)
        for b_data in active_barriers:
            sprite_key = b_data.get("sprite_type", "police_roadblock")
            b_surf = gfx.cached_tiles.get(sprite_key) or gfx.cached_tiles.get("police_roadblock")
            for (bx, by) in b_data["tiles"]:
                draw_bx = bx * TILE_SIZE - camera_x
                draw_by = by * TILE_SIZE - camera_y
                if -TILE_SIZE <= draw_bx <= SCREEN_WIDTH and -TILE_SIZE <= draw_by <= SCREEN_HEIGHT:
                    if b_surf:
                        surf.blit(b_surf, (draw_bx, draw_by))
                    # Floating Lock Badge Indicator
                    lx = int(draw_bx + TILE_SIZE // 2)
                    ly = int(draw_by - 6)
                    pygame.draw.circle(surf, (35, 20, 25), (lx, ly), 7)
                    pygame.draw.circle(surf, (245, 60, 60), (lx, ly), 7, 1)
                    l_txt = gfx.fonts["small"].render("!", True, (255, 80, 80))
                    surf.blit(l_txt, (lx - l_txt.get_width() // 2, ly - l_txt.get_height() // 2))

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
            elif npc.get("quest_id"):
                color = (255, 200, 50) # Amber Gold for Quest Givers
            pygame.draw.circle(surf, color, (int(nx + TILE_SIZE//2), int(ny + TILE_SIZE//2)), 12)
            pygame.draw.circle(surf, WHITE, (int(nx + TILE_SIZE//2), int(ny + TILE_SIZE//2 - 4)), 6)

            # Floating Quest Indicator for Quest Givers
            if npc.get("quest_id"):
                q_id = npc["quest_id"]
                if quest_mgr and quest_mgr.is_completed(q_id):
                    badge_char = "✓"
                    badge_color = (40, 220, 80)
                elif quest_mgr and quest_mgr.is_active(q_id):
                    badge_char = "?"
                    badge_color = (100, 200, 255)
                else:
                    badge_char = "!"
                    badge_color = (255, 230, 40)
                bx = int(nx + TILE_SIZE//2)
                by = int(ny - 6)
                pygame.draw.circle(surf, (30, 30, 45), (bx, by), 7)
                pygame.draw.circle(surf, badge_color, (bx, by), 7, 1)
                txt = gfx.fonts["small"].render(badge_char, True, badge_color)
                surf.blit(txt, (bx - txt.get_width()//2, by - txt.get_height()//2))
            
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

    def draw_minimap(self, surf, map_name, player_x, player_y):
        """Renders a minimap in the upper-left corner showing explored paths, fog-of-war, and player location."""
        grid = self.maps.get(map_name, {}).get("grid", [])
        if not grid:
            return
            
        rows = len(grid)
        cols = len(grid[0])
        
        # Ensure player area is revealed
        self.reveal_area(map_name, player_x, player_y, radius=3)
        explored = self.explored_tiles.get(map_name, set())
        
        # Dynamic cell scale based on map size
        max_canvas_w = 140
        max_canvas_h = 110
        cell_size = max(3, min(max_canvas_w // cols, max_canvas_h // rows))
        map_w = cols * cell_size
        map_h = rows * cell_size
        
        # Card bounds (upper-left)
        mx, my = 16, 16
        card_pad = 7
        header_h = 24
        card_w = max(140, map_w + card_pad * 2)
        card_h = header_h + map_h + card_pad * 2
        
        # Outer border & background card
        pygame.draw.rect(surf, (40, 48, 72), (mx - 2, my - 2, card_w + 4, card_h + 4), border_radius=8)
        pygame.draw.rect(surf, (22, 26, 38), (mx, my, card_w, card_h), border_radius=6)
        
        # Exploration percentage calculation
        walkable = sum(1 for r in range(rows) for c in range(cols) if grid[r][c] not in ["#", "^", "W", "~"])
        exp_walkable = sum(1 for (cx, cy) in explored if 0 <= cy < rows and 0 <= cx < cols and grid[cy][cx] not in ["#", "^", "W", "~"])
        pct = min(100, int(100 * exp_walkable / max(1, walkable)))
        
        # Header: Map name on left, % on right
        name_txt = gfx.fonts["small"].render(map_name, True, (240, 244, 252))
        pct_col = (70, 220, 110) if pct >= 100 else ((255, 200, 50) if pct > 50 else (200, 210, 230))
        pct_txt = gfx.fonts["small"].render(f"{pct}%", True, pct_col)
        
        surf.blit(name_txt, (mx + 8, my + 5))
        surf.blit(pct_txt, (mx + card_w - pct_txt.get_width() - 8, my + 5))
        
        # Minimap Canvas
        cx_start = mx + (card_w - map_w) // 2
        cy_start = my + header_h + card_pad
        pygame.draw.rect(surf, (14, 16, 24), (cx_start - 1, cy_start - 1, map_w + 2, map_h + 2), border_radius=3)
        
        is_cave = (map_name in ["Mt. Moon", "Seafoam Islands"])
        is_ice = (map_name == "Seafoam Islands")
        is_lavender = (map_name in ["Lavender Town", "Pokémon Tower"])
        is_power_plant = (map_name == "Power Plant")
        is_safari = (map_name == "Safari Zone")
        is_canyon = (map_name == "Route 9")
        ground_items = self.maps[map_name].get("ground_items", [])
        
        for r in range(rows):
            for c in range(cols):
                tx = cx_start + c * cell_size
                ty = cy_start + r * cell_size
                char = grid[r][c]
                is_exp = (c, r) in explored
                
                if not is_exp:
                    pygame.draw.rect(surf, (20, 24, 34), (tx, ty, cell_size, cell_size))
                    continue
                    
                # Explored tile colors
                if char == "^":
                    if is_ice:
                        col = (40, 95, 145) # Glacial Ice Wall
                    elif is_canyon:
                        col = (140, 65, 40) # Canyon Rock
                    else:
                        col = (75, 68, 62) # Cave Wall
                elif char == "#":
                    if is_lavender:
                        col = (55, 40, 65) # Spooky tree
                    elif is_safari:
                        col = (60, 110, 50) # Acacia tree
                    else:
                        col = (35, 75, 40) # Forest tree
                elif char in ["W", "R", "B"]:
                    if is_power_plant:
                        col = (235, 195, 30) # Power plant warning
                    else:
                        col = (110, 60, 60) # Building Wall/Roof
                elif char == "~":
                    col = (60, 130, 220) # Water
                elif char == "p":
                    col = (190, 125, 80) if is_canyon else (205, 180, 130) # Path
                elif char == "s":
                    col = (225, 205, 140) # Sand
                elif char == "b":
                    col = (175, 125, 75) # Bridge
                elif char in ENCOUNTER_PROP_TILES:
                    col = ENCOUNTER_PROP_TILES[char]["minimap_color"]
                    if char == "G" and is_safari:
                        col = (165, 135, 55)
                elif char == "O":
                    col = (120, 220, 255) if is_ice else (255, 215, 40) # Cave Entrance
                elif char == "D":
                    col = (255, 180, 40) # Door
                elif char == "S":
                    col = (185, 145, 85) # Signpost
                elif char in ["_", "C", "N", "M", "P", "H", "K"]:
                    if is_ice:
                        col = (150, 220, 245)
                    elif is_cave:
                        col = (135, 125, 120)
                    elif is_power_plant:
                        col = (90, 100, 115)
                    elif is_lavender:
                        col = (85, 75, 105)
                    else:
                        col = (195, 175, 140)
                elif char in ["J", "Y"]:
                    col = (145, 140, 155) if is_lavender else (175, 145, 120)
                else: # "."
                    if is_ice:
                        col = (150, 220, 245)
                    elif is_cave:
                        col = (125, 115, 110)
                    elif is_lavender:
                        col = (110, 90, 135)
                    elif is_safari:
                        col = (215, 190, 115)
                    elif is_canyon:
                        col = (190, 125, 80)
                    else:
                        col = (85, 160, 75)

                    
                pygame.draw.rect(surf, col, (tx, ty, cell_size, cell_size))
                
                # Draw collectible item indicator on explored tiles
                for g_item in ground_items:
                    if g_item["x"] == c and g_item["y"] == r and g_item["id"] not in self.collected_items:
                        pygame.draw.circle(surf, (240, 50, 50), (tx + cell_size // 2, ty + cell_size // 2), max(1, cell_size // 2))
                        
        # Player Locator Blip (with pulsing halo)
        px = cx_start + player_x * cell_size + cell_size // 2
        py = cy_start + player_y * cell_size + cell_size // 2
        
        pulse_r = max(2, cell_size // 2 + 1 + int((math.sin(self.timer * 6.0) + 1.0) * 1.2))
        pygame.draw.circle(surf, (255, 230, 60), (px, py), pulse_r, 1)
        pygame.draw.circle(surf, (240, 40, 40), (px, py), max(2, cell_size // 2 + 1))
        pygame.draw.circle(surf, WHITE, (px, py), max(1, cell_size // 2 - 1))
