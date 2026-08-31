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
    HP_GREEN, HP_YELLOW, HP_RED, EXP_BLUE, TYPE_COLORS, STATUS_COLORS, Direction
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
        self.boat_sprites = {}
        self.item_sprites = {}
        self.fonts = {}
        self.init_fonts()
        self.init_tiles()
        self.init_player_sprites()
        self.init_boat_sprites()
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

    def generate_player_sprites(self, gender="Boy", outfit_theme="Classic Red", hat_style="Trainer Cap", hair_color_name="Dark Brown"):
        """Generates 4-directional 3-frame animated walking sprites based on trainer customization."""
        from constants import OUTFIT_THEMES, HAIR_COLORS
        theme = OUTFIT_THEMES.get(outfit_theme, OUTFIT_THEMES["Classic Red"])
        shirt_col = theme["shirt"]
        pants_col = theme["pants"]
        hat_col = theme["hat"]
        accent_col = theme.get("accent", WHITE)
        hair_col = HAIR_COLORS.get(hair_color_name, HAIR_COLORS["Dark Brown"])
        is_female = (str(gender).lower() in ["girl", "female"])

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
                if is_female:
                    # Skirt / Shorts
                    pygame.draw.rect(surf, pants_col, (cx - 7, cy + 3, 14, 4), border_radius=1)
                    # Legs
                    pygame.draw.rect(surf, (255, 218, 185), (cx - 5, cy + 7, 4, 5 + (leg_offset if dir_code in [Direction.DOWN, Direction.UP] else 0)))
                    pygame.draw.rect(surf, (255, 218, 185), (cx + 1, cy + 7, 4, 5 - (leg_offset if dir_code in [Direction.DOWN, Direction.UP] else 0)))
                    # Socks & Shoes
                    pygame.draw.rect(surf, WHITE, (cx - 5, cy + 10, 4, 2))
                    pygame.draw.rect(surf, WHITE, (cx + 1, cy + 10, 4, 2))
                    pygame.draw.rect(surf, hat_col, (cx - 6, cy + 11, 5, 3))
                    pygame.draw.rect(surf, hat_col, (cx + 1, cy + 11, 5, 3))
                else:
                    # Pants
                    pygame.draw.rect(surf, pants_col, (cx - 6, cy + 4, 5, 8 + (leg_offset if dir_code in [Direction.DOWN, Direction.UP] else 0)))
                    pygame.draw.rect(surf, pants_col, (cx + 1, cy + 4, 5, 8 - (leg_offset if dir_code in [Direction.DOWN, Direction.UP] else 0)))
                    # Shoes
                    pygame.draw.rect(surf, (180, 40, 40), (cx - 7, cy + 11, 6, 3))
                    pygame.draw.rect(surf, (180, 40, 40), (cx + 1, cy + 11, 6, 3))
                
                # Shirt / Jacket
                pygame.draw.rect(surf, shirt_col, (cx - 7, cy - 4, 14, 9), border_radius=2)
                pygame.draw.rect(surf, accent_col, (cx - 2, cy - 4, 4, 9)) # Accent stripe
                
                # Arms
                arm_y_off = leg_offset if dir_code in [Direction.LEFT, Direction.RIGHT] else 0
                if dir_code == Direction.LEFT:
                    pygame.draw.rect(surf, shirt_col, (cx - 8, cy - 3 + arm_y_off, 4, 7))
                    pygame.draw.circle(surf, (255, 218, 185), (cx - 6, cy + 4 + arm_y_off), 2)
                elif dir_code == Direction.RIGHT:
                    pygame.draw.rect(surf, shirt_col, (cx + 4, cy - 3 - arm_y_off, 4, 7))
                    pygame.draw.circle(surf, (255, 218, 185), (cx + 6, cy + 4 - arm_y_off), 2)
                else:
                    pygame.draw.rect(surf, shirt_col, (cx - 9, cy - 3, 3, 7))
                    pygame.draw.rect(surf, shirt_col, (cx + 6, cy - 3, 3, 7))
                    pygame.draw.circle(surf, (255, 218, 185), (cx - 8, cy + 4), 2)
                    pygame.draw.circle(surf, (255, 218, 185), (cx + 7, cy + 4), 2)
                    
                # Hair Back (drawn before head for long hair/female)
                if is_female:
                    if dir_code == Direction.UP:
                        # Ponytail down the back
                        pygame.draw.rect(surf, hair_col, (cx - 3, cy - 12, 6, 12), border_radius=3)
                        pygame.draw.circle(surf, accent_col, (cx, cy - 11), 3) # Hair tie
                    elif dir_code == Direction.LEFT:
                        pygame.draw.rect(surf, hair_col, (cx + 2, cy - 11, 4, 9), border_radius=2)
                    elif dir_code == Direction.RIGHT:
                        pygame.draw.rect(surf, hair_col, (cx - 6, cy - 11, 4, 9), border_radius=2)
                    else:
                        # Side hair locks
                        pygame.draw.rect(surf, hair_col, (cx - 8, cy - 11, 3, 9), border_radius=1)
                        pygame.draw.rect(surf, hair_col, (cx + 5, cy - 11, 3, 9), border_radius=1)
                
                # Head / Face
                pygame.draw.circle(surf, (255, 218, 185), (cx, cy - 8), 6) # Peach skin
                
                # Hat & Hair rendering
                if hat_style == "Trainer Cap":
                    # Cap body
                    pygame.draw.arc(surf, hat_col, (cx - 7, cy - 16, 14, 12), 0, 3.14, 6)
                    pygame.draw.rect(surf, hat_col, (cx - 6, cy - 14, 12, 5))
                    if dir_code == Direction.DOWN:
                        pygame.draw.rect(surf, accent_col, (cx - 5, cy - 10, 10, 2)) # Visor front
                        pygame.draw.rect(surf, (40, 40, 40), (cx - 4, cy - 7, 2, 2))
                        pygame.draw.rect(surf, (40, 40, 40), (cx + 2, cy - 7, 2, 2))
                    elif dir_code == Direction.UP:
                        pygame.draw.rect(surf, hat_col, (cx - 6, cy - 14, 12, 8))
                        # Backpack
                        pygame.draw.rect(surf, (60, 140, 60), (cx - 5, cy - 3, 10, 7), border_radius=2)
                    elif dir_code == Direction.LEFT:
                        pygame.draw.rect(surf, accent_col, (cx - 8, cy - 10, 5, 2))
                        pygame.draw.rect(surf, (40, 40, 40), (cx - 4, cy - 7, 2, 2))
                    elif dir_code == Direction.RIGHT:
                        pygame.draw.rect(surf, accent_col, (cx + 3, cy - 10, 5, 2))
                        pygame.draw.rect(surf, (40, 40, 40), (cx + 2, cy - 7, 2, 2))

                elif hat_style == "Bandana":
                    pygame.draw.rect(surf, hat_col, (cx - 7, cy - 14, 14, 6), border_radius=2)
                    pygame.draw.rect(surf, hair_col, (cx - 6, cy - 16, 12, 4), border_radius=2)
                    if dir_code == Direction.DOWN:
                        pygame.draw.rect(surf, (40, 40, 40), (cx - 4, cy - 7, 2, 2))
                        pygame.draw.rect(surf, (40, 40, 40), (cx + 2, cy - 7, 2, 2))
                    elif dir_code == Direction.UP:
                        pygame.draw.rect(surf, accent_col, (cx - 3, cy - 13, 6, 4), border_radius=2)
                        pygame.draw.rect(surf, (60, 140, 60), (cx - 5, cy - 3, 10, 7), border_radius=2)
                    elif dir_code in [Direction.LEFT, Direction.RIGHT]:
                        eye_x = (cx - 4) if dir_code == Direction.LEFT else (cx + 2)
                        pygame.draw.rect(surf, (40, 40, 40), (eye_x, cy - 7, 2, 2))

                elif hat_style == "Beanie":
                    pygame.draw.ellipse(surf, hat_col, (cx - 7, cy - 17, 14, 12))
                    pygame.draw.circle(surf, accent_col, (cx, cy - 16), 3) # Pom-pom
                    if dir_code == Direction.DOWN:
                        pygame.draw.rect(surf, (40, 40, 40), (cx - 4, cy - 7, 2, 2))
                        pygame.draw.rect(surf, (40, 40, 40), (cx + 2, cy - 7, 2, 2))
                    elif dir_code == Direction.UP:
                        pygame.draw.rect(surf, (60, 140, 60), (cx - 5, cy - 3, 10, 7), border_radius=2)
                    elif dir_code in [Direction.LEFT, Direction.RIGHT]:
                        eye_x = (cx - 4) if dir_code == Direction.LEFT else (cx + 2)
                        pygame.draw.rect(surf, (40, 40, 40), (eye_x, cy - 7, 2, 2))

                else: # No Hat / Styled Hair
                    pygame.draw.circle(surf, hair_col, (cx, cy - 10), 7)
                    if dir_code == Direction.DOWN:
                        pygame.draw.rect(surf, hair_col, (cx - 6, cy - 12, 12, 4), border_radius=1)
                        pygame.draw.rect(surf, (40, 40, 40), (cx - 4, cy - 7, 2, 2))
                        pygame.draw.rect(surf, (40, 40, 40), (cx + 2, cy - 7, 2, 2))
                    elif dir_code == Direction.UP:
                        pygame.draw.rect(surf, hair_col, (cx - 6, cy - 14, 12, 8), border_radius=3)
                        pygame.draw.rect(surf, (60, 140, 60), (cx - 5, cy - 3, 10, 7), border_radius=2)
                    elif dir_code in [Direction.LEFT, Direction.RIGHT]:
                        eye_x = (cx - 4) if dir_code == Direction.LEFT else (cx + 2)
                        pygame.draw.rect(surf, (40, 40, 40), (eye_x, cy - 7, 2, 2))

                frames[dir_code].append(surf)
        return frames

    def get_trainer_preview_sprite(self, gender="Boy", outfit_theme="Classic Red", hat_style="Trainer Cap", hair_color_name="Dark Brown", size=(160, 160)):
        """Renders a high-resolution detailed front portrait/standing sprite for the customization menu."""
        from constants import OUTFIT_THEMES, HAIR_COLORS
        theme = OUTFIT_THEMES.get(outfit_theme, OUTFIT_THEMES["Classic Red"])
        shirt_col = theme["shirt"]
        pants_col = theme["pants"]
        hat_col = theme["hat"]
        accent_col = theme.get("accent", WHITE)
        hair_col = HAIR_COLORS.get(hair_color_name, HAIR_COLORS["Dark Brown"])
        is_female = (str(gender).lower() in ["girl", "female"])

        base_w, base_h = 64, 64
        surf = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
        cx, cy = 32, 32

        # Shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 60), (cx - 20, base_h - 10, 40, 10))

        # Legs / Pants
        if is_female:
            # Skirt / Shorts
            pygame.draw.rect(surf, pants_col, (cx - 14, cy + 6, 28, 10), border_radius=2)
            # Legs
            pygame.draw.rect(surf, (255, 218, 185), (cx - 10, cy + 16, 8, 12))
            pygame.draw.rect(surf, (255, 218, 185), (cx + 2, cy + 16, 8, 12))
            # Socks & Shoes
            pygame.draw.rect(surf, WHITE, (cx - 10, cy + 22, 8, 4))
            pygame.draw.rect(surf, WHITE, (cx + 2, cy + 22, 8, 4))
            pygame.draw.rect(surf, hat_col, (cx - 12, cy + 25, 10, 6), border_radius=2)
            pygame.draw.rect(surf, hat_col, (cx + 2, cy + 25, 10, 6), border_radius=2)
        else:
            # Pants
            pygame.draw.rect(surf, pants_col, (cx - 12, cy + 8, 10, 18), border_radius=2)
            pygame.draw.rect(surf, pants_col, (cx + 2, cy + 8, 10, 18), border_radius=2)
            # Shoes
            pygame.draw.rect(surf, (180, 40, 40), (cx - 14, cy + 24, 12, 7), border_radius=2)
            pygame.draw.rect(surf, (180, 40, 40), (cx + 2, cy + 24, 12, 7), border_radius=2)

        # Torso / Jacket
        pygame.draw.rect(surf, shirt_col, (cx - 14, cy - 8, 28, 18), border_radius=4)
        pygame.draw.rect(surf, accent_col, (cx - 4, cy - 8, 8, 18)) # Accent zipper
        # Belt
        pygame.draw.rect(surf, (30, 30, 35), (cx - 14, cy + 6, 28, 4))
        pygame.draw.rect(surf, (220, 200, 80), (cx - 3, cy + 5, 6, 6), border_radius=1)

        # Arms
        pygame.draw.rect(surf, shirt_col, (cx - 18, cy - 6, 6, 14), border_radius=2)
        pygame.draw.rect(surf, shirt_col, (cx + 12, cy - 6, 6, 14), border_radius=2)
        pygame.draw.circle(surf, (255, 218, 185), (cx - 15, cy + 8), 4)
        pygame.draw.circle(surf, (255, 218, 185), (cx + 15, cy + 8), 4)

        # Hair Back / Locks
        if is_female:
            pygame.draw.rect(surf, hair_col, (cx - 16, cy - 20, 6, 20), border_radius=3)
            pygame.draw.rect(surf, hair_col, (cx + 10, cy - 20, 6, 20), border_radius=3)

        # Head / Neck
        pygame.draw.rect(surf, (255, 218, 185), (cx - 4, cy - 10, 8, 4))
        pygame.draw.circle(surf, (255, 218, 185), (cx, cy - 16), 12)

        # Eyes & Smile
        pygame.draw.rect(surf, (30, 40, 50), (cx - 8, cy - 17, 4, 4), border_radius=1)
        pygame.draw.rect(surf, (30, 40, 50), (cx + 4, cy - 17, 4, 4), border_radius=1)
        pygame.draw.rect(surf, WHITE, (cx - 7, cy - 18, 2, 2))
        pygame.draw.rect(surf, WHITE, (cx + 5, cy - 18, 2, 2))
        # Blush
        pygame.draw.circle(surf, (255, 170, 170), (cx - 9, cy - 12), 3)
        pygame.draw.circle(surf, (255, 170, 170), (cx + 9, cy - 12), 3)
        # Smile
        pygame.draw.arc(surf, (160, 40, 40), (cx - 4, cy - 14, 8, 5), 3.14, 0, 2)

        # Hat / Hair Headgear
        if hat_style == "Trainer Cap":
            pygame.draw.arc(surf, hat_col, (cx - 14, cy - 30, 28, 22), 0, 3.14, 11)
            pygame.draw.rect(surf, hat_col, (cx - 12, cy - 26, 24, 10))
            pygame.draw.rect(surf, accent_col, (cx - 12, cy - 19, 24, 4), border_radius=2) # Visor
            # Pokeball logo on cap
            pygame.draw.circle(surf, WHITE, (cx, cy - 24), 4)
            pygame.draw.circle(surf, (220, 40, 40), (cx, cy - 24), 2)
        elif hat_style == "Bandana":
            pygame.draw.rect(surf, hat_col, (cx - 14, cy - 26, 28, 10), border_radius=3)
            pygame.draw.rect(surf, hair_col, (cx - 12, cy - 30, 24, 6), border_radius=3)
            pygame.draw.rect(surf, accent_col, (cx - 12, cy - 22, 24, 2))
        elif hat_style == "Beanie":
            pygame.draw.ellipse(surf, hat_col, (cx - 14, cy - 32, 28, 24))
            pygame.draw.circle(surf, accent_col, (cx, cy - 30), 5) # Pom-pom
            pygame.draw.rect(surf, accent_col, (cx - 13, cy - 21, 26, 3))
        else: # No Hat / Styled Hair
            pygame.draw.circle(surf, hair_col, (cx, cy - 20), 14)
            pygame.draw.rect(surf, hair_col, (cx - 12, cy - 24, 24, 8), border_radius=2)

        return pygame.transform.scale(surf, size)

    def init_player_sprites(self):
        """Generates default 4-directional 3-frame animated walking sprites for the trainer."""
        self.player_sprites = self.generate_player_sprites()

    def set_custom_player_appearance(self, gender="Boy", outfit_theme="Classic Red", hat_style="Trainer Cap", hair_color_name="Dark Brown"):
        """Updates active player sprites to match the trainer customization."""
        self.player_sprites = self.generate_player_sprites(gender, outfit_theme, hat_style, hair_color_name)

    def init_boat_sprites(self):
        """Generates 4-directional procedural boat sprites with wooden hull, deck, windshield, and water wake."""
        self.boat_sprites = {}
        for dir_code in [Direction.DOWN, Direction.UP, Direction.LEFT, Direction.RIGHT]:
            surf = pygame.Surface((TILE_SIZE + 10, TILE_SIZE + 10), pygame.SRCALPHA)
            bx, by = (TILE_SIZE + 10) // 2, (TILE_SIZE + 10) // 2
            
            # Water wake froth
            pygame.draw.ellipse(surf, (200, 235, 255, 130), (bx - 15, by - 6, 30, 22))
            pygame.draw.ellipse(surf, (255, 255, 255, 180), (bx - 12, by - 4, 24, 18))
            
            if dir_code == Direction.DOWN:
                # Bow pointing DOWN
                pygame.draw.polygon(surf, (130, 75, 30), [
                    (bx - 12, by - 12), (bx + 12, by - 12),
                    (bx + 12, by + 4), (bx + 7, by + 13),
                    (bx, by + 16), (bx - 7, by + 13),
                    (bx - 12, by + 4)
                ])
                pygame.draw.polygon(surf, (230, 205, 155), [
                    (bx - 9, by - 9), (bx + 9, by - 9),
                    (bx + 9, by + 3), (bx + 5, by + 10),
                    (bx, by + 12), (bx - 5, by + 10),
                    (bx - 9, by + 3)
                ])
                # Windshield
                pygame.draw.polygon(surf, (90, 190, 255, 220), [
                    (bx - 7, by + 1), (bx + 7, by + 1),
                    (bx + 5, by + 6), (bx - 5, by + 6)
                ])
                # Outboard motor at stern
                pygame.draw.rect(surf, (50, 55, 65), (bx - 4, by - 14, 8, 4), border_radius=1)
                
            elif dir_code == Direction.UP:
                # Bow pointing UP
                pygame.draw.polygon(surf, (130, 75, 30), [
                    (bx - 12, by + 12), (bx + 12, by + 12),
                    (bx + 12, by - 4), (bx + 7, by - 13),
                    (bx, by - 16), (bx - 7, by - 13),
                    (bx - 12, by - 4)
                ])
                pygame.draw.polygon(surf, (230, 205, 155), [
                    (bx - 9, by + 9), (bx + 9, by + 9),
                    (bx + 9, by - 3), (bx + 5, by - 10),
                    (bx, by - 12), (bx - 5, by - 10),
                    (bx - 9, by - 3)
                ])
                # Windshield
                pygame.draw.polygon(surf, (90, 190, 255, 220), [
                    (bx - 7, by - 1), (bx + 7, by - 1),
                    (bx + 5, by - 6), (bx - 5, by - 6)
                ])
                # Outboard motor at stern
                pygame.draw.rect(surf, (50, 55, 65), (bx - 4, by + 10, 8, 4), border_radius=1)
                
            elif dir_code == Direction.LEFT:
                # Bow pointing LEFT
                pygame.draw.polygon(surf, (130, 75, 30), [
                    (bx + 12, by - 11), (bx + 12, by + 11),
                    (bx - 4, by + 11), (bx - 13, by + 7),
                    (bx - 16, by), (bx - 13, by - 7),
                    (bx - 4, by - 11)
                ])
                pygame.draw.polygon(surf, (230, 205, 155), [
                    (bx + 9, by - 8), (bx + 9, by + 8),
                    (bx - 3, by + 8), (bx - 10, by + 5),
                    (bx - 12, by), (bx - 10, by - 5),
                    (bx - 3, by - 8)
                ])
                # Windshield
                pygame.draw.rect(surf, (90, 190, 255, 220), (bx - 6, by - 6, 4, 12), border_radius=1)
                # Outboard motor
                pygame.draw.rect(surf, (50, 55, 65), (bx + 10, by - 4, 4, 8), border_radius=1)
                
            else: # Direction.RIGHT
                # Bow pointing RIGHT
                pygame.draw.polygon(surf, (130, 75, 30), [
                    (bx - 12, by - 11), (bx - 12, by + 11),
                    (bx + 4, by + 11), (bx + 13, by + 7),
                    (bx + 16, by), (bx + 13, by - 7),
                    (bx + 4, by - 11)
                ])
                pygame.draw.polygon(surf, (230, 205, 155), [
                    (bx - 9, by - 8), (bx - 9, by + 8),
                    (bx + 3, by + 8), (bx + 10, by + 5),
                    (bx + 12, by), (bx + 10, by - 5),
                    (bx + 3, by - 8)
                ])
                # Windshield
                pygame.draw.rect(surf, (90, 190, 255, 220), (bx + 2, by - 6, 4, 12), border_radius=1)
                # Outboard motor
                pygame.draw.rect(surf, (50, 55, 65), (bx - 14, by - 4, 4, 8), border_radius=1)
                
            self.boat_sprites[dir_code] = surf

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

        # 9. Sand / Beach Shore
        sand = pygame.Surface((T, T))
        sand.fill((240, 220, 160)) # Golden sand
        for _ in range(10):
            rx = random.randint(1, T - 2)
            ry = random.randint(1, T - 2)
            sand.set_at((rx, ry), (220, 200, 140))
        self.cached_tiles["sand"] = sand

        # 10. Cave Floor (Subterranean)
        cave_floor = pygame.Surface((T, T))
        cave_floor.fill((85, 75, 70)) # Dark stone brown
        for _ in range(12):
            rx = random.randint(1, T - 2)
            ry = random.randint(1, T - 2)
            cave_floor.set_at((rx, ry), (70, 60, 55))
            if random.random() < 0.3:
                cave_floor.set_at((rx, ry), (105, 95, 90))
        self.cached_tiles["cave_floor"] = cave_floor

        # 11. Cave Wall / Mountain Rock (Solid)
        cave_wall = pygame.Surface((T, T))
        cave_wall.fill((45, 40, 38))
        pygame.draw.rect(cave_wall, (65, 58, 55), (2, 2, T - 4, T - 4), border_radius=4)
        pygame.draw.polygon(cave_wall, (30, 25, 24), [(4, 4), (16, 2), (28, 8), (20, 28), (6, 24)])
        pygame.draw.polygon(cave_wall, (75, 68, 65), [(8, 8), (18, 6), (24, 12), (18, 22), (10, 18)])
        self.cached_tiles["cave_wall"] = cave_wall

        # 12. Cave Entrance / Arch
        cave_door = cave_wall.copy()
        pygame.draw.arc(cave_door, (10, 10, 12), (6, 4, 20, 26), 0, 3.14, 10)
        pygame.draw.rect(cave_door, (10, 10, 12), (6, 12, 20, 20))
        self.cached_tiles["cave_door"] = cave_door

        # 13. Bridge / Wood Pier
        bridge = pygame.Surface((T, T))
        bridge.fill((190, 145, 95)) # Warm wood
        pygame.draw.line(bridge, (140, 95, 55), (0, 0), (T, 0), 2)
        pygame.draw.line(bridge, (140, 95, 55), (0, T // 2), (T, T // 2), 2)
        pygame.draw.line(bridge, (140, 95, 55), (0, T - 1), (T, T - 1), 2)
        pygame.draw.line(bridge, (100, 65, 35), (8, 0), (8, T), 1)
        pygame.draw.line(bridge, (100, 65, 35), (24, 0), (24, T), 1)
        self.cached_tiles["bridge"] = bridge

        # 14. Gym Arena Floor & Mat
        gym_floor = pygame.Surface((T, T))
        gym_floor.fill((215, 180, 130)) # Polished gym hardwood
        pygame.draw.line(gym_floor, (185, 150, 100), (0, 0), (T, 0), 1)
        pygame.draw.line(gym_floor, (185, 150, 100), (0, T - 1), (T, T - 1), 1)
        self.cached_tiles["gym_floor"] = gym_floor

        gym_mat = gym_floor.copy()
        pygame.draw.circle(gym_mat, (220, 50, 50), (T // 2, T // 2), 12)
        pygame.draw.circle(gym_mat, WHITE, (T // 2, T // 2), 6)
        pygame.draw.circle(gym_mat, BLACK, (T // 2, T // 2), 2)
        self.cached_tiles["gym_mat"] = gym_mat

        # 15. Gym Statue
        gym_statue = gym_floor.copy()
        pygame.draw.rect(gym_statue, (140, 140, 150), (6, 12, 20, 18), border_radius=2)
        pygame.draw.polygon(gym_statue, (170, 170, 180), [(16, 2), (6, 14), (26, 14)])
        pygame.draw.rect(gym_statue, (240, 200, 60), (10, 20, 12, 6)) # Gold plaque
        self.cached_tiles["gym_statue"] = gym_statue

        # 16. Oak Lab Furniture (Table, Bookshelf)
        lab_floor = floor.copy()
        table = lab_floor.copy()
        pygame.draw.rect(table, (100, 140, 180), (4, 4, T - 8, T - 8), border_radius=3)
        pygame.draw.rect(table, (200, 230, 255), (8, 8, 8, 8)) # Screen
        pygame.draw.circle(table, (220, 60, 60), (22, 12), 3) # Red bulb
        self.cached_tiles["lab_table"] = table

        bookshelf = floor.copy()
        pygame.draw.rect(bookshelf, (130, 80, 45), (2, 2, T - 4, T - 4), border_radius=2)
        pygame.draw.rect(bookshelf, (200, 70, 70), (4, 6, 6, 8))
        pygame.draw.rect(bookshelf, (70, 120, 200), (12, 6, 6, 8))
        pygame.draw.rect(bookshelf, (70, 180, 90), (20, 6, 6, 8))
        pygame.draw.rect(bookshelf, (220, 180, 50), (4, 18, 7, 8))
        pygame.draw.rect(bookshelf, (160, 90, 180), (13, 18, 7, 8))
        self.cached_tiles["bookshelf"] = bookshelf

        # 17. Overworld Item Pokeball
        item_ball = grass.copy()
        cx, cy = T // 2, T // 2 + 2
        pygame.draw.ellipse(item_ball, (0, 0, 0, 80), (cx - 7, cy + 4, 14, 5))
        pygame.draw.circle(item_ball, (225, 45, 45), (cx, cy), 6) # Top red
        pygame.draw.arc(item_ball, WHITE, (cx - 6, cy - 6, 12, 12), 3.14, 0, 6)
        pygame.draw.circle(item_ball, WHITE, (cx, cy + 3), 3)
        pygame.draw.line(item_ball, BLACK, (cx - 6, cy), (cx + 6, cy), 1)
        pygame.draw.circle(item_ball, BLACK, (cx, cy), 2)
        pygame.draw.circle(item_ball, WHITE, (cx, cy), 1)
        self.cached_tiles["item_ball"] = item_ball

        # ==========================================
        # 18. BIOME: Glacial Ice Cavern (Seafoam Islands)
        # ==========================================
        ice_floor = pygame.Surface((T, T))
        ice_floor.fill((150, 220, 245)) # Glistening frozen ice
        pygame.draw.line(ice_floor, (210, 245, 255), (2, 4), (18, 4), 2)
        pygame.draw.line(ice_floor, (210, 245, 255), (14, 18), (28, 18), 2)
        pygame.draw.line(ice_floor, (110, 180, 215), (0, T - 1), (T, T - 1), 1)
        for _ in range(6):
            rx, ry = random.randint(2, T - 4), random.randint(2, T - 4)
            ice_floor.set_at((rx, ry), (240, 252, 255))
        self.cached_tiles["ice_floor"] = ice_floor

        ice_wall = pygame.Surface((T, T))
        ice_wall.fill((40, 95, 145))
        pygame.draw.rect(ice_wall, (70, 145, 200), (2, 2, T - 4, T - 4), border_radius=4)
        pygame.draw.polygon(ice_wall, (25, 65, 105), [(4, 4), (16, 2), (28, 8), (20, 28), (6, 24)])
        pygame.draw.polygon(ice_wall, (120, 205, 245), [(8, 8), (18, 6), (24, 12), (18, 22), (10, 18)])
        pygame.draw.line(ice_wall, (220, 245, 255), (10, 8), (16, 6), 2)
        self.cached_tiles["ice_wall"] = ice_wall

        ice_door = ice_wall.copy()
        pygame.draw.arc(ice_door, (15, 35, 60), (6, 4, 20, 26), 0, 3.14, 10)
        pygame.draw.rect(ice_door, (15, 35, 60), (6, 12, 20, 20))
        self.cached_tiles["ice_door"] = ice_door

        # ==========================================
        # 19. BIOME: Spooky Lavender Mist & Ghost Tower
        # ==========================================
        lavender_ground = pygame.Surface((T, T))
        lavender_ground.fill((110, 90, 135)) # Eerie purple soil
        for _ in range(8):
            rx, ry = random.randint(2, T - 3), random.randint(2, T - 3)
            lavender_ground.set_at((rx, ry), (135, 115, 165))
            lavender_ground.set_at((rx + 1, ry), (85, 65, 110))
        self.cached_tiles["lavender_ground"] = lavender_ground

        spooky_floor = pygame.Surface((T, T))
        spooky_floor.fill((85, 75, 105)) # Haunted purple-grey floorboards
        pygame.draw.line(spooky_floor, (60, 50, 75), (0, 0), (T, 0), 1)
        pygame.draw.line(spooky_floor, (60, 50, 75), (0, T - 1), (T, T - 1), 1)
        self.cached_tiles["spooky_floor"] = spooky_floor

        tombstone = spooky_floor.copy()
        pygame.draw.rect(tombstone, (145, 140, 155), (8, 8, 16, 20), border_radius=4)
        pygame.draw.rect(tombstone, (110, 105, 120), (6, 24, 20, 6), border_radius=2)
        pygame.draw.line(tombstone, (75, 70, 85), (16, 11), (16, 21), 2) # Cross vertical
        pygame.draw.line(tombstone, (75, 70, 85), (12, 14), (20, 14), 2) # Cross horizontal
        self.cached_tiles["tombstone"] = tombstone

        spooky_tree = lavender_ground.copy()
        pygame.draw.rect(spooky_tree, (45, 30, 55), (13, 10, 6, 18), border_radius=2)
        pygame.draw.circle(spooky_tree, (55, 40, 65), (16, 10), 10)
        pygame.draw.circle(spooky_tree, (75, 55, 90), (14, 8), 6)
        self.cached_tiles["spooky_tree"] = spooky_tree

        # ==========================================
        # 20. BIOME: Industrial Electric Power Plant
        # ==========================================
        metal_floor = pygame.Surface((T, T))
        metal_floor.fill((90, 100, 115)) # Steel diamond plate
        pygame.draw.rect(metal_floor, (120, 130, 145), (0, 0, T, T), 1)
        for dx in [6, 22]:
            for dy in [6, 22]:
                pygame.draw.rect(metal_floor, (60, 65, 75), (dx, dy, 4, 4))
                pygame.draw.rect(metal_floor, (140, 150, 165), (dx, dy, 2, 2))
        self.cached_tiles["metal_floor"] = metal_floor

        generator_coil = metal_floor.copy()
        pygame.draw.rect(generator_coil, (40, 45, 55), (4, 4, T - 8, T - 8), border_radius=3)
        pygame.draw.circle(generator_coil, (220, 140, 40), (16, 16), 9) # Copper core
        pygame.draw.circle(generator_coil, (255, 220, 60), (16, 16), 5) # Glowing electrical spark
        pygame.draw.circle(generator_coil, WHITE, (16, 16), 2)
        self.cached_tiles["generator_coil"] = generator_coil

        warning_tile = pygame.Surface((T, T))
        warning_tile.fill((235, 195, 30)) # Caution yellow
        for offset in range(-T, T * 2, 8):
            pygame.draw.polygon(warning_tile, (35, 35, 40), [(offset, 0), (offset + 4, 0), (offset + 4 + T, T), (offset + T, T)])
        self.cached_tiles["warning_tile"] = warning_tile

        # ==========================================
        # 21. BIOME: Golden Savanna Safari Zone
        # ==========================================
        savanna_grass = pygame.Surface((T, T))
        savanna_grass.fill((215, 190, 115)) # Warm amber savanna soil
        for _ in range(8):
            rx, ry = random.randint(2, T - 3), random.randint(2, T - 3)
            savanna_grass.set_at((rx, ry), (235, 210, 135))
            savanna_grass.set_at((rx + 1, ry), (185, 160, 90))
        self.cached_tiles["savanna_grass"] = savanna_grass

        savanna_tall_grass = savanna_grass.copy()
        for x in [4, 12, 20, 28]:
            for y in [6, 18]:
                pygame.draw.polygon(savanna_tall_grass, (165, 135, 55), [(x - 3, y + 10), (x, y), (x + 3, y + 10)])
                pygame.draw.polygon(savanna_tall_grass, (200, 170, 75), [(x - 2, y + 10), (x, y + 2), (x + 2, y + 10)])
        self.cached_tiles["savanna_tall_grass"] = savanna_tall_grass

        acacia_tree = savanna_grass.copy()
        pygame.draw.rect(acacia_tree, (110, 70, 40), (14, 12, 4, 18))
        pygame.draw.ellipse(acacia_tree, (60, 110, 50), (4, 4, 24, 10))
        pygame.draw.ellipse(acacia_tree, (80, 140, 65), (6, 2, 20, 8))
        self.cached_tiles["acacia_tree"] = acacia_tree

        # ==========================================
        # 22. BIOME: Canyon / Badlands
        # ==========================================
        canyon_dirt = pygame.Surface((T, T))
        canyon_dirt.fill((190, 125, 80)) # Reddish desert trail
        for _ in range(10):
            rx, ry = random.randint(1, T - 2), random.randint(1, T - 2)
            canyon_dirt.set_at((rx, ry), (170, 105, 65))
            if random.random() < 0.3:
                canyon_dirt.set_at((rx, ry), (215, 150, 105))
        self.cached_tiles["canyon_dirt"] = canyon_dirt

        canyon_rock = pygame.Surface((T, T))
        canyon_rock.fill((140, 65, 40)) # Terraced sedimentary canyon rock
        pygame.draw.rect(canyon_rock, (170, 85, 55), (2, 2, T - 4, T - 4), border_radius=3)
        pygame.draw.line(canyon_rock, (110, 45, 25), (0, 10), (T, 10), 2)
        pygame.draw.line(canyon_rock, (200, 105, 70), (0, 18), (T, 18), 2)
        self.cached_tiles["canyon_rock"] = canyon_rock


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

    def draw_gym_badge(self, surf, badge_name, x, y, size=40, is_earned=True):
        """Renders shiny official Gym Badges on the Trainer Card."""
        cx = x + size // 2
        cy = y + size // 2
        
        if not is_earned:
            # Unearned empty socket
            pygame.draw.circle(surf, (50, 55, 65), (cx, cy), size // 2, 2)
            pygame.draw.circle(surf, (30, 35, 45), (cx, cy), size // 2 - 2)
            dash = self.fonts["small"].render("?", True, (80, 90, 110))
            surf.blit(dash, (cx - dash.get_width() // 2, cy - dash.get_height() // 2))
            return

        if badge_name == "Boulder Badge":
            # Grey stone octagon with bevel
            pts = [
                (cx - 14, cy - 6), (cx - 6, cy - 14), (cx + 6, cy - 14), (cx + 14, cy - 6),
                (cx + 14, cy + 6), (cx + 6, cy + 14), (cx - 6, cy + 14), (cx - 14, cy + 6)
            ]
            pygame.draw.polygon(surf, (160, 165, 175), pts)
            pygame.draw.polygon(surf, (220, 225, 235), pts, 2)
            # Inner bevel facets
            pygame.draw.polygon(surf, (120, 125, 135), [(cx - 8, cy - 3), (cx - 3, cy - 8), (cx + 3, cy - 8), (cx + 8, cy - 3), (cx + 8, cy + 3), (cx + 3, cy + 8), (cx - 3, cy + 8), (cx - 8, cy + 3)])
            pygame.draw.polygon(surf, (240, 245, 255), [(cx - 3, cy - 8), (cx + 3, cy - 8), (cx, cy)])

        elif badge_name == "Cascade Badge":
            # Sky-blue crystal teardrop
            pts = [(cx, cy - 16), (cx + 14, cy + 6), (cx + 8, cy + 14), (cx - 8, cy + 14), (cx - 14, cy + 6)]
            pygame.draw.polygon(surf, (70, 180, 240), pts)
            pygame.draw.polygon(surf, (200, 240, 255), pts, 2)
            pygame.draw.polygon(surf, (30, 130, 200), [(cx, cy - 8), (cx + 8, cy + 8), (cx - 8, cy + 8)])
            pygame.draw.circle(surf, WHITE, (cx - 3, cy - 2), 3)

        else:
            # Gold Star Badge fallback
            pygame.draw.circle(surf, (240, 200, 40), (cx, cy), size // 2 - 2)
            pygame.draw.circle(surf, WHITE, (cx, cy), size // 2 - 2, 2)

    def draw_status_badge(self, surf, status_name, x, y, width=44, height=18):
        """Renders a colorful, modern Pokémon status condition pill badge."""
        if not status_name:
            return
            
        cfg = STATUS_COLORS.get(status_name, {
            "abbr": status_name[:3].upper(),
            "bg": (140, 140, 140),
            "border": (80, 80, 80),
            "text": WHITE,
            "shadow": (30, 30, 30)
        })
        
        # Pill Background & Outer Border
        pygame.draw.rect(surf, cfg["border"], (x, y, width, height), border_radius=4)
        pygame.draw.rect(surf, cfg["bg"], (x + 1, y + 1, width - 2, height - 2), border_radius=3)
        
        # Subtle glossy top highlight
        gloss = pygame.Surface((width - 2, max(2, height // 2)), pygame.SRCALPHA)
        gloss.fill((255, 255, 255, 60))
        surf.blit(gloss, (x + 1, y + 1))
        
        # Status Abbreviation Text
        abbr_text = cfg["abbr"]
        txt_surf = self.fonts["small"].render(abbr_text, True, cfg["text"])
        shd_surf = self.fonts["small"].render(abbr_text, True, cfg.get("shadow", BLACK))
        
        tx = x + (width - txt_surf.get_width()) // 2
        ty = y + (height - txt_surf.get_height()) // 2
        surf.blit(shd_surf, (tx + 1, ty + 1))
        surf.blit(txt_surf, (tx, ty))

    def draw_pokemon_with_status_effects(self, surf, pokemon, center_x, center_y, sprite_surf, anim_time, is_back=False):
        """
        Renders a Pokémon sprite with animated status visual effects and particle systems:
        - Paralysis: Yellow electric sparks, crackling lightning bolts, jitter twitching, and golden aura.
        - Burn: Rising fire embers, burning flame particles, and warm red-orange heat glow.
        - Poison: Rising toxic purple bubbles, popping rings, and violet haze.
        - Sleep: Drifting animated 'Z' letters, drowsy breathing motion, and night-blue tint.
        - Freeze: Frost glints, ice crystal shards, and icy cyan tint.
        """
        status = getattr(pokemon, "status", None)
        draw_x = center_x - sprite_surf.get_width() // 2
        draw_y = center_y - sprite_surf.get_height() // 2
        
        # 1. Status Specific Positional / Pose Offsets
        offset_x = 0
        offset_y = 0
        
        if status == "Paralysis":
            # Occasional quick muscle twitch / spasm
            if math.sin(anim_time * 8.0) > 0.65:
                offset_x = math.sin(anim_time * 45.0) * 2.5
        elif status == "Sleep":
            # Slow, drowsy breathing slump
            offset_y = math.sin(anim_time * 2.5) * 3.0
            
        final_draw_x = int(draw_x + offset_x)
        final_draw_y = int(draw_y + offset_y)
        
        # 2. Draw Base Sprite
        surf.blit(sprite_surf, (final_draw_x, final_draw_y))
        
        # If no status active, we are done
        if not status:
            return

        sw = sprite_surf.get_width()
        sh = sprite_surf.get_height()
        
        # 3. Status Glow / Tint Overlay
        tint_overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        
        if status == "Paralysis":
            pulse = int(55 + 40 * math.sin(anim_time * 12.0))
            tint_overlay.fill((255, 230, 40, pulse))
            # Blit sprite alpha onto tint overlay so it only covers the Pokemon
            tint_overlay.blit(sprite_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(tint_overlay, (final_draw_x, final_draw_y), special_flags=pygame.BLEND_RGB_ADD)
            
            # Draw Crackling Lightning Bolts & Electric Sparks
            num_bolts = 5
            for i in range(num_bolts):
                bolt_seed = int(anim_time * 14.0) + i * 3
                rnd = random.Random(bolt_seed)
                
                # Origin point near body
                ang = rnd.uniform(0, 6.28)
                rad = rnd.uniform(15, 38)
                bx = center_x + math.cos(ang) * rad
                by = center_y + math.sin(ang) * rad
                
                # Zig-zag segments
                pts = [(bx, by)]
                seg_count = rnd.randint(2, 4)
                for _ in range(seg_count):
                    bx += rnd.uniform(-16, 16)
                    by += rnd.uniform(-16, 16)
                    pts.append((bx, by))
                    
                if len(pts) >= 2:
                    # Outer electric yellow bolt
                    pygame.draw.lines(surf, (255, 240, 60), False, pts, 3)
                    # Inner white-hot bolt core
                    pygame.draw.lines(surf, (255, 255, 240), False, pts, 1)
                    
                # Electric diamond spark at end point
                spk_x, spk_y = pts[-1]
                spk_size = rnd.randint(3, 6)
                pygame.draw.polygon(surf, (255, 255, 200), [
                    (spk_x, spk_y - spk_size), (spk_x + spk_size, spk_y),
                    (spk_x, spk_y + spk_size), (spk_x - spk_size, spk_y)
                ])

        elif status == "Burn":
            pulse = int(50 + 35 * math.sin(anim_time * 6.0))
            tint_overlay.fill((255, 75, 20, pulse))
            tint_overlay.blit(sprite_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(tint_overlay, (final_draw_x, final_draw_y), special_flags=pygame.BLEND_RGB_ADD)
            
            # Draw Rising Flame & Ember Particles
            num_flames = 8
            for i in range(num_flames):
                phase = (anim_time * 1.1 + i * (1.0 / num_flames)) % 1.0
                fx = center_x + math.sin(anim_time * 3.5 + i * 2.3) * 26 + ((i % 5 - 2) * 12)
                fy = (center_y + 35) - phase * 80
                
                # Size shrinks as it rises
                size = max(1.5, (1.0 - phase) * 7.0)
                
                # Flame color transition: Red -> Orange -> Yellow
                if phase < 0.35:
                    col_outer = (255, 60, 20)
                    col_inner = (255, 200, 40)
                elif phase < 0.7:
                    col_outer = (255, 120, 20)
                    col_inner = (255, 240, 80)
                else:
                    col_outer = (240, 160, 40)
                    col_inner = (255, 255, 200)
                    
                pygame.draw.circle(surf, col_outer, (int(fx), int(fy)), int(size))
                if size > 2.5:
                    pygame.draw.circle(surf, col_inner, (int(fx), int(fy - 1)), int(size * 0.5))

        elif status == "Poison":
            pulse = int(50 + 40 * math.sin(anim_time * 4.5))
            tint_overlay.fill((180, 40, 220, pulse))
            tint_overlay.blit(sprite_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(tint_overlay, (final_draw_x, final_draw_y), special_flags=pygame.BLEND_RGB_ADD)
            
            # Draw Rising Toxic Bubbles
            num_bubbles = 7
            for i in range(num_bubbles):
                phase = (anim_time * 0.75 + i * (1.0 / num_bubbles)) % 1.0
                bx = center_x + math.cos(anim_time * 2.8 + i * 1.9) * 28 + ((i % 4 - 1.5) * 14)
                by = (center_y + 30) - phase * 75
                
                if phase < 0.85:
                    r = int(3.5 + (i % 3) * 1.5)
                    # Semi-transparent purple bubble
                    bub_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
                    pygame.draw.circle(bub_surf, (190, 50, 240, 200), (r + 1, r + 1), r)
                    pygame.draw.circle(bub_surf, (120, 20, 160, 240), (r + 1, r + 1), r, 1)
                    # Glint shine
                    pygame.draw.circle(bub_surf, (255, 230, 255, 220), (r - 1, r - 1), max(1, r // 3))
                    surf.blit(bub_surf, (int(bx - r - 1), int(by - r - 1)))
                else:
                    # Popping splash ring
                    pop_r = int((phase - 0.85) / 0.15 * 10) + 3
                    pop_alpha = max(0, int(255 * (1.0 - (phase - 0.85) / 0.15)))
                    if pop_r > 0:
                        pop_surf = pygame.Surface((pop_r * 2 + 4, pop_r * 2 + 4), pygame.SRCALPHA)
                        pygame.draw.circle(pop_surf, (210, 80, 255, pop_alpha), (pop_r + 2, pop_r + 2), pop_r, 1)
                        surf.blit(pop_surf, (int(bx - pop_r - 2), int(by - pop_r - 2)))

        elif status == "Sleep":
            # Night blue calming tint
            tint_overlay.fill((50, 70, 140, 35))
            tint_overlay.blit(sprite_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(tint_overlay, (final_draw_x, final_draw_y))
            
            # Floating Z's
            for i in range(3):
                phase = (anim_time * 0.6 + i * 0.33) % 1.0
                dir_mult = 1 if is_back else -1
                zx = center_x + (dir_mult * 30) + math.sin(phase * 4.0 + i) * 14 + (phase * 22 * dir_mult)
                zy = (center_y - 35) - phase * 50
                
                alpha = max(0, min(255, int(255 * (1.0 - (phase ** 1.5)))))
                z_font = self.fonts["medium"] if i == 0 else (self.fonts["regular"] if i == 1 else self.fonts["small"])
                z_txt = "Z" if i == 0 else ("z" if i == 1 else "·")
                
                z_surf = z_font.render(z_txt, True, (180, 220, 255))
                z_shd = z_font.render(z_txt, True, (40, 60, 100))
                
                z_alpha_surf = pygame.Surface((z_surf.get_width() + 4, z_surf.get_height() + 4), pygame.SRCALPHA)
                z_alpha_surf.blit(z_shd, (2, 2))
                z_alpha_surf.blit(z_surf, (1, 1))
                z_alpha_surf.set_alpha(alpha)
                surf.blit(z_alpha_surf, (int(zx), int(zy)))

        elif status in ["Freeze", "Frozen"]:
            pulse = int(50 + 25 * math.sin(anim_time * 5.0))
            tint_overlay.fill((80, 210, 255, pulse))
            tint_overlay.blit(sprite_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(tint_overlay, (final_draw_x, final_draw_y), special_flags=pygame.BLEND_RGB_ADD)
            
            # Ice crystal diamond sparkles
            for i in range(6):
                ang = anim_time * 0.8 + i * (6.28 / 6)
                cx_ice = center_x + math.cos(ang) * (34 + (i % 2) * 8)
                cy_ice = center_y + math.sin(ang) * (28 + (i % 2) * 8)
                sz = 5 + (i % 3) * 2
                pts = [
                    (cx_ice, cy_ice - sz), (cx_ice + sz * 0.6, cy_ice),
                    (cx_ice, cy_ice + sz), (cx_ice - sz * 0.6, cy_ice)
                ]
                pygame.draw.polygon(surf, (160, 235, 255), pts)
                pygame.draw.polygon(surf, WHITE, pts, 1)
                pygame.draw.circle(surf, WHITE, (int(cx_ice), int(cy_ice)), 1)

# Global Graphics Singleton
gfx = GraphicsManager()


