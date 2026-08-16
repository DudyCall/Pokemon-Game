"""
graphics_manager.py - Visual assets manager, sprite downloader & cacher, procedural tile generator,
animated player spritesheet, and battle particle effects.
"""
import os
import math
import random
import threading
import urllib.request
import pygame
from constants import (
    TILE_SIZE, WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY,
    HP_GREEN, HP_YELLOW, HP_RED, EXP_BLUE, TYPE_COLORS, Direction
)
from pokemon_data import POKEMON_SPECIES

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
FRONT_SPRITES_DIR = os.path.join(SPRITES_DIR, "front")
BACK_SPRITES_DIR = os.path.join(SPRITES_DIR, "back")

class GraphicsManager:
    def __init__(self):
        self._ensure_asset_dirs()
        self.cached_pokemon_sprites = {}
        self.cached_tiles = {}
        self.player_sprites = {}
        self.item_sprites = {}
        self.fonts = {}
        self.init_fonts()
        self.init_tiles()
        self.init_player_sprites()
        self.init_item_sprites()
        # Start background preload of top Pokemon sprites
        threading.Thread(target=self._preload_pokemon_sprites, daemon=True).start()

    def _ensure_asset_dirs(self):
        for path in [ASSETS_DIR, SPRITES_DIR, FRONT_SPRITES_DIR, BACK_SPRITES_DIR]:
            os.makedirs(path, exist_ok=True)

    def init_fonts(self):
        pygame.font.init()
        # Clean modern pixel-friendly typography
        font_names = ["Consolas", "Courier New", "Lucida Console", "Segoe UI", "Arial"]
        self.fonts["small"] = pygame.font.SysFont(font_names, 14, bold=True)
        self.fonts["regular"] = pygame.font.SysFont(font_names, 18, bold=True)
        self.fonts["medium"] = pygame.font.SysFont(font_names, 22, bold=True)
        self.fonts["large"] = pygame.font.SysFont(font_names, 28, bold=True)
        self.fonts["title"] = pygame.font.SysFont(font_names, 42, bold=True)

    def _preload_pokemon_sprites(self):
        for species_name, data in POKEMON_SPECIES.items():
            poke_id = data["id"]
            self._download_sprite_if_needed(poke_id, is_back=False)
            self._download_sprite_if_needed(poke_id, is_back=True)

    def _download_sprite_if_needed(self, poke_id, is_back=False):
        sub_dir = BACK_SPRITES_DIR if is_back else FRONT_SPRITES_DIR
        local_path = os.path.join(sub_dir, f"{poke_id}.png")
        if os.path.exists(local_path):
            return local_path
        
        url_part = f"back/{poke_id}.png" if is_back else f"{poke_id}.png"
        url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{url_part}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PokemonPygame/1.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                with open(local_path, "wb") as f:
                    f.write(resp.read())
            return local_path
        except Exception:
            return None

    def get_pokemon_sprite(self, species_name, is_back=False, size=(160, 160)):
        key = (species_name, is_back, size)
        if key in self.cached_pokemon_sprites:
            return self.cached_pokemon_sprites[key]
        
        species_data = POKEMON_SPECIES.get(species_name, POKEMON_SPECIES["Pikachu"])
        poke_id = species_data["id"]
        sub_dir = BACK_SPRITES_DIR if is_back else FRONT_SPRITES_DIR
        local_path = os.path.join(sub_dir, f"{poke_id}.png")
        
        surf = None
        if os.path.exists(local_path):
            try:
                raw_surf = pygame.image.load(local_path).convert_alpha()
                surf = pygame.transform.scale(raw_surf, size)
            except Exception:
                surf = None
                
        if surf is None:
            # Generate procedural crisp pixel sprite fallback
            surf = self._generate_procedural_pokemon_sprite(species_name, is_back, size)
            
        self.cached_pokemon_sprites[key] = surf
        return surf

    def _generate_procedural_pokemon_sprite(self, species_name, is_back, size):
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        species_data = POKEMON_SPECIES.get(species_name, POKEMON_SPECIES["Pikachu"])
        primary_type = species_data["types"][0]
        base_color = TYPE_COLORS.get(primary_type, (180, 180, 180))
        dark_shade = tuple(max(0, c - 50) for c in base_color)
        light_shade = tuple(min(255, c + 50) for c in base_color)
        
        # Draw stylized creature silhouette
        center_x, center_y = 32, 36 if not is_back else 40
        radius = 20 if not is_back else 22
        
        # Body
        pygame.draw.circle(surf, dark_shade, (center_x, center_y), radius + 2)
        pygame.draw.circle(surf, base_color, (center_x, center_y), radius)
        pygame.draw.circle(surf, light_shade, (center_x - 4, center_y - 4), radius - 6)
        
        # Ears / Horns / Features based on type or name
        if "Pikachu" in species_name or "Raichu" in species_name:
            # Long electric ears
            pygame.draw.polygon(surf, base_color, [(center_x - 14, center_y - 12), (center_x - 22, center_y - 28), (center_x - 6, center_y - 18)])
            pygame.draw.polygon(surf, BLACK, [(center_x - 22, center_y - 28), (center_x - 18, center_y - 24), (center_x - 14, center_y - 20)])
            pygame.draw.polygon(surf, base_color, [(center_x + 14, center_y - 12), (center_x + 22, center_y - 28), (center_x + 6, center_y - 18)])
            pygame.draw.polygon(surf, BLACK, [(center_x + 22, center_y - 28), (center_x + 18, center_y - 24), (center_x + 14, center_y - 20)])
            if not is_back:
                # Red cheeks
                pygame.draw.circle(surf, (240, 40, 40), (center_x - 12, center_y + 4), 4)
                pygame.draw.circle(surf, (240, 40, 40), (center_x + 12, center_y + 4), 4)
        elif "Charmander" in species_name or "Charizard" in species_name:
            # Tail flame
            pygame.draw.circle(surf, (255, 200, 0), (center_x + 18, center_y + 12), 7)
            pygame.draw.circle(surf, (255, 60, 0), (center_x + 20, center_y + 10), 4)
        elif "Bulbasaur" in species_name or "Ivysaur" in species_name:
            # Bulb on back
            pygame.draw.circle(surf, (40, 160, 70), (center_x, center_y - 14), 10)
        elif "Squirtle" in species_name or "Blastoise" in species_name:
            # Shell
            pygame.draw.ellipse(surf, (160, 90, 40), (center_x - 14, center_y - 8, 28, 20))
            
        if not is_back:
            # Eyes
            pygame.draw.circle(surf, WHITE, (center_x - 7, center_y - 2), 4)
            pygame.draw.circle(surf, BLACK, (center_x - 6, center_y - 2), 2)
            pygame.draw.circle(surf, WHITE, (center_x + 7, center_y - 2), 4)
            pygame.draw.circle(surf, BLACK, (center_x + 6, center_y - 2), 2)
            # Smile
            pygame.draw.arc(surf, BLACK, (center_x - 5, center_y + 2, 10, 6), 3.14, 0, 2)
            
        return pygame.transform.scale(surf, size)

    def init_player_sprites(self):
        """Generates 4-directional 3-frame animated walking sprites for the trainer."""
        frames = {}
        for dir_code in [Direction.DOWN, Direction.UP, Direction.LEFT, Direction.RIGHT]:
            frames[dir_code] = []
            for step in [0, 1, 2]:
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                cx, cy = TILE_SIZE // 2, TILE_SIZE // 2
                
                # Shadow
                pygame.draw.ellipse(surf, (0, 0, 0, 70), (cx - 10, TILE_SIZE - 8, 20, 7))
                
                # Leg offset for walking
                leg_offset = -3 if step == 1 else (3 if step == 2 else 0)
                
                # Pants / Legs
                pygame.draw.rect(surf, (30, 60, 120), (cx - 6, cy + 4, 5, 8 + (leg_offset if dir_code in [Direction.DOWN, Direction.UP] else 0)))
                pygame.draw.rect(surf, (30, 60, 120), (cx + 1, cy + 4, 5, 8 - (leg_offset if dir_code in [Direction.DOWN, Direction.UP] else 0)))
                # Shoes
                pygame.draw.rect(surf, (180, 40, 40), (cx - 7, cy + 11, 6, 3))
                pygame.draw.rect(surf, (180, 40, 40), (cx + 1, cy + 11, 6, 3))
                
                # Shirt / Jacket (Red trainer vest)
                pygame.draw.rect(surf, (220, 40, 40), (cx - 7, cy - 4, 14, 10), border_radius=2)
                pygame.draw.rect(surf, WHITE, (cx - 2, cy - 4, 4, 10)) # White zipper stripe
                
                # Arms
                arm_y_off = leg_offset if dir_code in [Direction.LEFT, Direction.RIGHT] else 0
                if dir_code == Direction.LEFT:
                    pygame.draw.rect(surf, (220, 40, 40), (cx - 8, cy - 3 + arm_y_off, 4, 7))
                elif dir_code == Direction.RIGHT:
                    pygame.draw.rect(surf, (220, 40, 40), (cx + 4, cy - 3 - arm_y_off, 4, 7))
                else:
                    pygame.draw.rect(surf, (220, 40, 40), (cx - 9, cy - 3, 3, 7))
                    pygame.draw.rect(surf, (220, 40, 40), (cx + 6, cy - 3, 3, 7))
                    
                # Head / Face
                pygame.draw.circle(surf, (255, 218, 185), (cx, cy - 8), 6) # Peach skin
                
                # Hat (Red cap with white visor)
                pygame.draw.arc(surf, (200, 30, 30), (cx - 7, cy - 16, 14, 12), 0, 3.14, 6)
                pygame.draw.rect(surf, (200, 30, 30), (cx - 6, cy - 14, 12, 5))
                
                if dir_code == Direction.DOWN:
                    # White visor front
                    pygame.draw.rect(surf, WHITE, (cx - 5, cy - 10, 10, 2))
                    # Eyes
                    pygame.draw.rect(surf, (40, 40, 40), (cx - 4, cy - 7, 2, 2))
                    pygame.draw.rect(surf, (40, 40, 40), (cx + 2, cy - 7, 2, 2))
                elif dir_code == Direction.UP:
                    # Back of cap (All red)
                    pygame.draw.rect(surf, (180, 20, 20), (cx - 6, cy - 14, 12, 8))
                    # Backpack
                    pygame.draw.rect(surf, (60, 140, 60), (cx - 5, cy - 3, 10, 7), border_radius=2)
                elif dir_code == Direction.LEFT:
                    # Visor pointing left
                    pygame.draw.rect(surf, WHITE, (cx - 8, cy - 10, 5, 2))
                    pygame.draw.rect(surf, (40, 40, 40), (cx - 4, cy - 7, 2, 2))
                elif dir_code == Direction.RIGHT:
                    # Visor pointing right
                    pygame.draw.rect(surf, WHITE, (cx + 3, cy - 10, 5, 2))
                    pygame.draw.rect(surf, (40, 40, 40), (cx + 2, cy - 7, 2, 2))
                    
                frames[dir_code].append(surf)
        self.player_sprites = frames

    def init_item_sprites(self):
        """Generates icons for Pokeballs, Potions, Badges, etc."""
        # Pokeball
        pb = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(pb, (220, 40, 40), (12, 12), 10) # Top red
        pygame.draw.arc(pb, WHITE, (2, 2, 20, 20), 3.14, 0, 10) # Bottom white
        pygame.draw.circle(pb, WHITE, (12, 17), 5) # Fill bottom white
        pygame.draw.line(pb, BLACK, (2, 12), (22, 12), 2)
        pygame.draw.circle(pb, BLACK, (12, 12), 4)
        pygame.draw.circle(pb, WHITE, (12, 12), 2)
        self.item_sprites["Poke Ball"] = pb
        
        # Great Ball (Blue with red accents)
        gb = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(gb, (40, 100, 220), (12, 12), 10)
        pygame.draw.circle(gb, WHITE, (12, 17), 5)
        pygame.draw.line(gb, (220, 40, 40), (6, 5), (10, 9), 2)
        pygame.draw.line(gb, (220, 40, 40), (18, 5), (14, 9), 2)
        pygame.draw.line(gb, BLACK, (2, 12), (22, 12), 2)
        pygame.draw.circle(gb, BLACK, (12, 12), 4)
        pygame.draw.circle(gb, WHITE, (12, 12), 2)
        self.item_sprites["Great Ball"] = gb

        # Ultra Ball (Black with yellow H)
        ub = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(ub, (40, 40, 50), (12, 12), 10)
        pygame.draw.circle(ub, WHITE, (12, 17), 5)
        pygame.draw.arc(ub, (240, 200, 40), (5, 4, 14, 10), 0, 3.14, 3)
        pygame.draw.line(ub, BLACK, (2, 12), (22, 12), 2)
        pygame.draw.circle(ub, BLACK, (12, 12), 4)
        pygame.draw.circle(ub, WHITE, (12, 12), 2)
        self.item_sprites["Ultra Ball"] = ub

        # Potion Spray
        pot = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.rect(pot, (160, 80, 200), (7, 10, 10, 11), border_radius=3)
        pygame.draw.rect(pot, (230, 230, 240), (9, 5, 6, 6))
        pygame.draw.rect(pot, (100, 100, 110), (13, 3, 5, 3))
        self.item_sprites["Potion"] = pot
        self.item_sprites["Super Potion"] = pot
        self.item_sprites["Max Potion"] = pot

    def init_tiles(self):
        """Generates beautiful crisp procedural pixel-art tiles."""
        T = TILE_SIZE
        
        # 1. Plain Grass
        grass = pygame.Surface((T, T))
        grass.fill((112, 200, 80)) # Lush emerald
        for _ in range(8):
            rx = random.randint(2, T - 3)
            ry = random.randint(2, T - 3)
            grass.set_at((rx, ry), (130, 220, 95))
            grass.set_at((rx + 1, ry), (90, 175, 60))
        self.cached_tiles["grass"] = grass
        
        # 2. Tall Encounter Grass
        tall_grass = grass.copy()
        for x in [4, 12, 20, 28]:
            for y in [6, 18]:
                # Draw grass blades
                pygame.draw.polygon(tall_grass, (45, 130, 40), [(x - 3, y + 10), (x, y), (x + 3, y + 10)])
                pygame.draw.polygon(tall_grass, (75, 175, 60), [(x - 2, y + 10), (x, y + 2), (x + 2, y + 10)])
        self.cached_tiles["tall_grass"] = tall_grass
        
        # 3. Path / Dirt Road
        path = pygame.Surface((T, T))
        path.fill((230, 210, 160)) # Sandy beige
        for _ in range(12):
            rx = random.randint(1, T - 2)
            ry = random.randint(1, T - 2)
            path.set_at((rx, ry), (210, 190, 140))
            if random.random() < 0.3:
                path.set_at((rx, ry), (245, 230, 190))
        self.cached_tiles["path"] = path
        
        # 4. Water (4-frame ripple animation)
        water_frames = []
        for f in range(4):
            ws = pygame.Surface((T, T))
            ws.fill((64, 136, 232))
            # Ripple waves
            phase = f * 8
            for row in range(4, T, 8):
                for col in range(0, T, 16):
                    x = (col + phase) % T
                    pygame.draw.arc(ws, (180, 220, 255), (x - 6, row, 12, 6), 0, 3.14, 2)
            water_frames.append(ws)
        self.cached_tiles["water"] = water_frames
        
        # 5. Tree (Top-Left, Top-Right, Bottom-Left, Bottom-Right 2x2)
        tree_top = pygame.Surface((T * 2, T))
        tree_top.fill((0, 0, 0))
        tree_top.set_colorkey((0, 0, 0))
        pygame.draw.circle(tree_top, (34, 120, 45), (T, T), T - 2)
        pygame.draw.circle(tree_top, (50, 160, 65), (T - 6, T - 6), T - 8)
        
        tree_bot = pygame.Surface((T * 2, T))
        tree_bot.fill((0, 0, 0))
        tree_bot.set_colorkey((0, 0, 0))
        pygame.draw.circle(tree_bot, (34, 120, 45), (T, 0), T - 2)
        pygame.draw.circle(tree_bot, (50, 160, 65), (T - 6, 0), T - 8)
        # Trunk
        pygame.draw.rect(tree_bot, (130, 80, 40), (T - 6, 8, 12, T - 8))
        pygame.draw.rect(tree_bot, (90, 50, 25), (T - 6, 8, 4, T - 8))
        
        self.cached_tiles["tree_tl"] = tree_top.subsurface((0, 0, T, T))
        self.cached_tiles["tree_tr"] = tree_top.subsurface((T, 0, T, T))
        self.cached_tiles["tree_bl"] = tree_bot.subsurface((0, 0, T, T))
        self.cached_tiles["tree_br"] = tree_bot.subsurface((T, 0, T, T))
        
        # 6. Flowers
        flower_red = grass.copy()
        pygame.draw.circle(flower_red, (240, 60, 60), (10, 12), 4)
        pygame.draw.circle(flower_red, (255, 230, 60), (10, 12), 2)
        pygame.draw.circle(flower_red, (240, 60, 60), (22, 22), 4)
        pygame.draw.circle(flower_red, (255, 230, 60), (22, 22), 2)
        self.cached_tiles["flower_red"] = flower_red
        
        # 7. Wooden Fence
        fence = grass.copy()
        pygame.draw.rect(fence, (160, 110, 60), (0, 10, T, 4))
        pygame.draw.rect(fence, (160, 110, 60), (0, 20, T, 4))
        pygame.draw.rect(fence, (120, 75, 35), (4, 6, 6, 22), border_radius=1)
        pygame.draw.rect(fence, (120, 75, 35), (22, 6, 6, 22), border_radius=1)
        self.cached_tiles["fence"] = fence
        
        # 8. PokeCenter Wall / Roof
        roof_red = pygame.Surface((T, T))
        roof_red.fill((220, 48, 48))
        pygame.draw.rect(roof_red, (255, 100, 100), (0, 0, T, 4))
        pygame.draw.line(roof_red, (160, 20, 20), (0, T - 1), (T, T - 1), 2)
        self.cached_tiles["roof_red"] = roof_red
        
        roof_blue = pygame.Surface((T, T))
        roof_blue.fill((48, 120, 220))
        pygame.draw.rect(roof_blue, (100, 170, 255), (0, 0, T, 4))
        pygame.draw.line(roof_blue, (20, 60, 160), (0, T - 1), (T, T - 1), 2)
        self.cached_tiles["roof_blue"] = roof_blue
        
        wall_white = pygame.Surface((T, T))
        wall_white.fill((240, 240, 245))
        pygame.draw.rect(wall_white, (210, 215, 225), (0, 0, T, T), 1)
        self.cached_tiles["wall_white"] = wall_white
        
        door = wall_white.copy()
        pygame.draw.rect(door, (80, 140, 220), (6, 6, 20, T - 6), border_radius=2)
        pygame.draw.rect(door, (200, 230, 255), (10, 10, 12, 12))
        self.cached_tiles["door"] = door

        # Sign
        sign = grass.copy()
        pygame.draw.rect(sign, (140, 90, 50), (6, 8, 20, 14), border_radius=2)
        pygame.draw.rect(sign, (230, 210, 160), (8, 10, 16, 10))
        pygame.draw.rect(sign, (100, 60, 30), (14, 22, 4, 10))
        self.cached_tiles["sign"] = sign
        
        # Indoor floor
        floor = pygame.Surface((T, T))
        floor.fill((235, 230, 215))
        pygame.draw.rect(floor, (215, 205, 185), (0, 0, T, T), 1)
        self.cached_tiles["floor"] = floor
        
        # Indoor Counter
        counter = pygame.Surface((T, T))
        counter.fill((160, 100, 60))
        pygame.draw.rect(counter, (200, 140, 90), (2, 2, T - 4, 6))
        pygame.draw.rect(counter, (120, 70, 35), (0, 0, T, T), 2)
        self.cached_tiles["counter"] = counter

    def draw_hp_bar(self, surf, x, y, width, height, current_hp, max_hp, label="HP"):
        """Renders an authentic HP bar with color transition (green -> yellow -> red)."""
        ratio = max(0.0, min(1.0, current_hp / max(1, max_hp)))
        
        # Outer Border Box
        pygame.draw.rect(surf, DARK_GRAY, (x - 2, y - 2, width + 4, height + 4), border_radius=4)
        pygame.draw.rect(surf, BLACK, (x, y, width, height), border_radius=3)
        
        # Fill Color based on percentage
        if ratio > 0.5:
            fill_color = HP_GREEN
        elif ratio > 0.2:
            fill_color = HP_YELLOW
        else:
            fill_color = HP_RED
            
        fill_width = int(width * ratio)
        if fill_width > 0:
            pygame.draw.rect(surf, fill_color, (x, y, fill_width, height), border_radius=3)
            # Gloss highlight
            pygame.draw.rect(surf, (255, 255, 255, 100), (x, y, fill_width, height // 3), border_radius=2)

    def draw_exp_bar(self, surf, x, y, width, height, ratio):
        """Renders the blue EXP progress bar."""
        pygame.draw.rect(surf, DARK_GRAY, (x - 1, y - 1, width + 2, height + 2), border_radius=2)
        pygame.draw.rect(surf, (30, 40, 60), (x, y, width, height), border_radius=2)
        fill_w = int(width * max(0.0, min(1.0, ratio)))
        if fill_w > 0:
            pygame.draw.rect(surf, EXP_BLUE, (x, y, fill_w, height), border_radius=2)

    def draw_type_badge(self, surf, type_name, x, y, width=64, height=22):
        """Renders a colorful Pokémon type pill badge."""
        color = TYPE_COLORS.get(type_name, (140, 140, 140))
        dark_border = tuple(max(0, c - 40) for c in color)
        
        pygame.draw.rect(surf, dark_border, (x, y, width, height), border_radius=6)
        pygame.draw.rect(surf, color, (x + 1, y + 1, width - 2, height - 2), border_radius=5)
        
        # Type Name Label
        txt = self.fonts["small"].render(type_name.upper(), True, WHITE)
        tx = x + (width - txt.get_width()) // 2
        ty = y + (height - txt.get_height()) // 2
        # Text shadow
        txt_shd = self.fonts["small"].render(type_name.upper(), True, (20, 20, 20))
        surf.blit(txt_shd, (tx + 1, ty + 1))
        surf.blit(txt, (tx, ty))

# Global Graphics Singleton
gfx = GraphicsManager()
