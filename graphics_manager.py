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
        self.cached_trainer_portraits = {}
        self.cached_tiles = {}
        self.player_sprites = {}
        self.boat_sprites = {}
        self.item_sprites = {}
        self.prop_overlays = {}
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

    def get_trainer_portrait(self, identifier, size=(96, 96), is_talking=False):
        """
        Generates and caches rich, high-resolution procedural pixel-art character portraits
        for all trainers, Gym Leaders, Team Rocket, and story NPCs.
        """
        if isinstance(identifier, dict):
            raw_id = identifier.get("id") or identifier.get("name") or "trainer"
        elif identifier:
            raw_id = str(identifier)
        else:
            raw_id = "trainer"

        norm_id = raw_id.lower()
        key = (norm_id, size, is_talking)
        if key in self.cached_trainer_portraits:
            return self.cached_trainer_portraits[key]

        # Canvas Resolution: 96x96
        W, H = 96, 96
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        cx, cy = W // 2, H // 2

        # -------------------------------------------------------------
        # Determine Character Role / Class Attributes
        # -------------------------------------------------------------
        # Default Palettes
        bg_gradient_top = (45, 55, 80)
        bg_gradient_bot = (20, 25, 40)
        border_col = (180, 195, 220)
        border_highlight = (240, 245, 255)
        skin_col = (255, 218, 185) # Warm peach
        hair_col = (75, 45, 30) # Brown
        shirt_col = (220, 60, 50)
        vest_col = None
        hat_col = None
        has_glasses = False
        has_rocket_r = False
        is_female = False
        is_brock = False
        is_misty = False
        is_blue = False
        is_rocket = False
        is_nurse = False
        is_oak = False
        is_bill = False
        is_hiker = False
        is_bug_catcher = False
        is_blackbelt = False
        is_channeler = False
        is_engineer = False
        is_fisherman = False
        is_item = False
        is_sign = False

        if "brock" in norm_id:
            is_brock = True
            bg_gradient_top = (130, 120, 105)
            bg_gradient_bot = (60, 55, 50)
            border_col = (220, 180, 50) # Gym Leader Gold
            border_highlight = (255, 235, 120)
            skin_col = (215, 165, 120) # Tan
            hair_col = (55, 35, 25)
            shirt_col = (45, 105, 55) # Green vest
            vest_col = (165, 120, 65) # Tan vest

        elif "misty" in norm_id:
            is_misty = True
            is_female = True
            bg_gradient_top = (60, 160, 235)
            bg_gradient_bot = (20, 80, 160)
            border_col = (220, 180, 50) # Gym Leader Gold
            border_highlight = (255, 235, 120)
            skin_col = (255, 225, 205)
            hair_col = (240, 100, 30) # Bright orange
            shirt_col = (255, 230, 60) # Yellow top

        elif "blue" in norm_id or "rival" in norm_id:
            is_blue = True
            bg_gradient_top = (65, 75, 140)
            bg_gradient_bot = (25, 30, 75)
            border_col = (80, 200, 255) # Electric Cyan
            border_highlight = (190, 240, 255)
            skin_col = (255, 220, 185)
            hair_col = (140, 70, 30) # Auburn brown
            shirt_col = (65, 45, 95) # Dark purple long sleeve

        elif "rocket" in norm_id:
            is_rocket = True
            has_rocket_r = True
            bg_gradient_top = (50, 50, 60)
            bg_gradient_bot = (20, 20, 25)
            border_col = (220, 40, 40) # Team Rocket Red
            border_highlight = (255, 100, 100)
            skin_col = (245, 215, 195)
            hair_col = (35, 35, 45)
            shirt_col = (25, 25, 30)
            hat_col = (25, 25, 30)

        elif "youngster" in norm_id:
            bg_gradient_top = (70, 140, 220)
            bg_gradient_bot = (30, 70, 140)
            border_col = (240, 180, 50)
            border_highlight = (255, 235, 150)
            skin_col = (255, 220, 185)
            hair_col = (90, 55, 35)
            shirt_col = (240, 190, 40)
            hat_col = (220, 50, 40)

        elif "bug" in norm_id:
            is_bug_catcher = True
            bg_gradient_top = (70, 150, 65)
            bg_gradient_bot = (25, 75, 30)
            border_col = (130, 210, 80)
            border_highlight = (200, 255, 160)
            skin_col = (255, 220, 185)
            hair_col = (100, 65, 35)
            shirt_col = (245, 245, 245)
            vest_col = (65, 135, 55)
            hat_col = (225, 195, 120) # Straw hat

        elif "lass" in norm_id or "picnicker" in norm_id:
            is_female = True
            bg_gradient_top = (235, 130, 165)
            bg_gradient_bot = (140, 50, 95)
            border_col = (255, 180, 210)
            border_highlight = (255, 235, 245)
            skin_col = (255, 225, 205)
            hair_col = (120, 60, 40)
            shirt_col = (255, 120, 160)

        elif "camper" in norm_id:
            bg_gradient_top = (110, 145, 95)
            bg_gradient_bot = (45, 75, 45)
            border_col = (180, 205, 140)
            border_highlight = (235, 245, 210)
            skin_col = (255, 215, 180)
            hair_col = (85, 50, 30)
            shirt_col = (195, 175, 125) # Khaki
            hat_col = (85, 130, 75)

        elif "hiker" in norm_id:
            is_hiker = True
            bg_gradient_top = (165, 105, 60)
            bg_gradient_bot = (85, 45, 25)
            border_col = (220, 150, 90)
            border_highlight = (255, 210, 160)
            skin_col = (225, 175, 130) # Rugged tan
            hair_col = (65, 40, 25)
            shirt_col = (235, 120, 35) # Orange vest
            hat_col = (185, 160, 115) # Safari hat

        elif "blackbelt" in norm_id or "karate" in norm_id:
            is_blackbelt = True
            bg_gradient_top = (180, 50, 45)
            bg_gradient_bot = (75, 20, 20)
            border_col = (240, 90, 80)
            border_highlight = (255, 180, 170)
            skin_col = (235, 185, 145)
            hair_col = (30, 30, 35)
            shirt_col = (245, 245, 250) # White gi

        elif "swimmer" in norm_id or "fisherman" in norm_id:
            is_fisherman = True
            bg_gradient_top = (50, 140, 195)
            bg_gradient_bot = (20, 65, 115)
            border_col = (100, 195, 245)
            border_highlight = (205, 240, 255)
            skin_col = (240, 195, 155)
            hair_col = (80, 50, 35)
            shirt_col = (45, 115, 185)
            hat_col = (175, 155, 115) # Bucket hat

        elif "scientist" in norm_id or "nerd" in norm_id:
            has_glasses = True
            bg_gradient_top = (75, 115, 155)
            bg_gradient_bot = (30, 55, 80)
            border_col = (140, 190, 235)
            border_highlight = (220, 240, 255)
            skin_col = (250, 220, 195)
            hair_col = (85, 55, 40)
            shirt_col = (245, 248, 255) # Lab coat

        elif "firebreather" in norm_id:
            bg_gradient_top = (215, 75, 30)
            bg_gradient_bot = (95, 25, 15)
            border_col = (255, 140, 50)
            border_highlight = (255, 220, 120)
            skin_col = (235, 180, 140)
            hair_col = (220, 45, 20) # Fiery red
            shirt_col = (35, 35, 40) # Leather vest

        elif "channeler" in norm_id:
            is_channeler = True
            is_female = True
            bg_gradient_top = (110, 60, 160)
            bg_gradient_bot = (45, 20, 75)
            border_col = (195, 130, 245)
            border_highlight = (240, 210, 255)
            skin_col = (240, 220, 230) # Ghostly pale
            hair_col = (75, 45, 105)
            shirt_col = (95, 55, 135) # Spirit robes
            hat_col = (85, 45, 125) # Veil

        elif "engineer" in norm_id:
            is_engineer = True
            bg_gradient_top = (185, 155, 45)
            bg_gradient_bot = (65, 55, 20)
            border_col = (245, 215, 60)
            border_highlight = (255, 245, 160)
            skin_col = (230, 185, 145)
            hair_col = (60, 45, 35)
            shirt_col = (235, 125, 35) # Orange overalls
            hat_col = (245, 210, 30) # Yellow hardhat

        elif "joy" in norm_id or "nurse" in norm_id or "healer" in norm_id:
            is_nurse = True
            is_female = True
            bg_gradient_top = (255, 190, 215)
            bg_gradient_bot = (190, 100, 140)
            border_col = (255, 150, 190)
            border_highlight = (255, 230, 245)
            skin_col = (255, 228, 215)
            hair_col = (255, 130, 175) # Pink hair
            shirt_col = (255, 245, 250)

        elif "oak" in norm_id:
            is_oak = True
            bg_gradient_top = (145, 80, 65)
            bg_gradient_bot = (65, 35, 30)
            border_col = (225, 165, 115)
            border_highlight = (255, 235, 205)
            skin_col = (245, 215, 185)
            hair_col = (175, 180, 190) # Distinguished gray
            shirt_col = (190, 45, 45) # Red polo with lab coat

        elif "bill" in norm_id:
            is_bill = True
            bg_gradient_top = (45, 155, 175)
            bg_gradient_bot = (20, 75, 95)
            border_col = (80, 225, 245)
            border_highlight = (200, 255, 255)
            skin_col = (255, 220, 190)
            hair_col = (30, 185, 215) # Cyan hair
            shirt_col = (235, 210, 65)

        elif "mom" in norm_id:
            is_female = True
            bg_gradient_top = (245, 185, 145)
            bg_gradient_bot = (165, 95, 65)
            border_col = (245, 195, 155)
            border_highlight = (255, 240, 225)
            skin_col = (255, 225, 200)
            hair_col = (135, 75, 45)
            shirt_col = (240, 130, 155) # Pink cardigan

        elif "clerk" in norm_id or "mart" in norm_id:
            bg_gradient_top = (60, 120, 210)
            bg_gradient_bot = (25, 60, 130)
            border_col = (245, 205, 50)
            border_highlight = (255, 240, 150)
            skin_col = (255, 220, 185)
            hair_col = (75, 45, 30)
            shirt_col = (50, 105, 200)
            hat_col = (50, 105, 200)

        elif "item" in norm_id or "ball" in norm_id:
            is_item = True
            bg_gradient_top = (45, 75, 135)
            bg_gradient_bot = (15, 30, 65)
            border_col = (235, 70, 70)
            border_highlight = (255, 180, 180)

        elif "sign" in norm_id or "notice" in norm_id:
            is_sign = True
            bg_gradient_top = (145, 100, 55)
            bg_gradient_bot = (75, 45, 20)
            border_col = (205, 160, 100)
            border_highlight = (245, 220, 180)

        # -------------------------------------------------------------
        # 1. Background Card & Metallic Bevel Border Frame
        # -------------------------------------------------------------
        card_rect = pygame.Rect(4, 4, W - 8, H - 8)
        # Vertical gradient background
        for y in range(card_rect.top, card_rect.bottom):
            prog = (y - card_rect.top) / max(1, card_rect.height)
            r_c = int(bg_gradient_top[0] * (1 - prog) + bg_gradient_bot[0] * prog)
            g_c = int(bg_gradient_top[1] * (1 - prog) + bg_gradient_bot[1] * prog)
            b_c = int(bg_gradient_top[2] * (1 - prog) + bg_gradient_bot[2] * prog)
            pygame.draw.line(surf, (r_c, g_c, b_c), (card_rect.left, y), (card_rect.right, y))

        # -------------------------------------------------------------
        # Special Item / Sign Board Renderers
        # -------------------------------------------------------------
        if is_item:
            # Draw Giant Glowing Item Ball in Center
            pygame.draw.circle(surf, (255, 230, 120, 80), (cx, cy), 32)
            # Upper half red
            pygame.draw.arc(surf, (230, 45, 45), (cx - 24, cy - 24, 48, 48), 0, 3.14, 24)
            pygame.draw.rect(surf, (230, 45, 45), (cx - 24, cy - 12, 48, 12))
            # Lower half white
            pygame.draw.arc(surf, (240, 245, 255), (cx - 24, cy - 24, 48, 48), 3.14, 6.28, 24)
            pygame.draw.rect(surf, (240, 245, 255), (cx - 24, cy, 48, 12))
            # Black center dividing band
            pygame.draw.line(surf, (40, 40, 45), (cx - 24, cy), (cx + 24, cy), 5)
            # Center button
            pygame.draw.circle(surf, (40, 40, 45), (cx, cy), 9)
            pygame.draw.circle(surf, WHITE, (cx, cy), 6)
            pygame.draw.circle(surf, (200, 210, 225), (cx, cy), 3)
            # Gloss shine glint
            pygame.draw.circle(surf, WHITE, (cx - 12, cy - 12), 4)

        elif is_sign:
            # Wooden Plank Notice Sign
            pygame.draw.rect(surf, (160, 110, 60), (14, 18, W - 28, H - 36), border_radius=6)
            pygame.draw.rect(surf, (120, 75, 35), (14, 18, W - 28, H - 36), 2, border_radius=6)
            pygame.draw.line(surf, (135, 85, 45), (18, 38), (W - 18, 38), 2)
            pygame.draw.line(surf, (135, 85, 45), (18, 58), (W - 18, 58), 2)
            # Corner brass rivets
            for rx, ry in [(18, 22), (W - 22, 22), (18, H - 26), (W - 22, H - 26)]:
                pygame.draw.circle(surf, (240, 200, 80), (rx, ry), 2)
            # Center icon: Info / Note symbol
            pygame.draw.circle(surf, (255, 245, 220), (cx, cy), 14)
            pygame.draw.rect(surf, (120, 75, 35), (cx - 2, cy - 6, 4, 10))
            pygame.draw.circle(surf, (120, 75, 35), (cx, cy - 8), 2)

        # -------------------------------------------------------------
        # Character Bust Rendering (Torso, Head, Face, Hair, Headgear)
        # -------------------------------------------------------------
        else:
            # 1. Torso / Shoulders
            shoulder_y = cy + 16
            pygame.draw.ellipse(surf, shirt_col, (cx - 28, shoulder_y, 56, 36))
            pygame.draw.rect(surf, shirt_col, (cx - 28, shoulder_y + 12, 56, 24))

            # Lab Coat overlay for Scientist / Oak
            if has_glasses or is_oak:
                pygame.draw.polygon(surf, WHITE, [(cx - 28, shoulder_y + 10), (cx - 10, shoulder_y + 4), (cx - 12, H - 6), (cx - 28, H - 6)])
                pygame.draw.polygon(surf, WHITE, [(cx + 28, shoulder_y + 10), (cx + 10, shoulder_y + 4), (cx + 12, H - 6), (cx + 28, H - 6)])
                pygame.draw.line(surf, (200, 210, 225), (cx - 10, shoulder_y + 4), (cx - 12, H - 6), 2)
                pygame.draw.line(surf, (200, 210, 225), (cx + 10, shoulder_y + 4), (cx + 12, H - 6), 2)

            # Vest Overlay (Brock, Hiker, Bug Catcher)
            if vest_col:
                pygame.draw.polygon(surf, vest_col, [(cx - 26, shoulder_y + 8), (cx - 8, shoulder_y + 4), (cx - 10, H - 6), (cx - 26, H - 6)])
                pygame.draw.polygon(surf, vest_col, [(cx + 26, shoulder_y + 8), (cx + 8, shoulder_y + 4), (cx + 10, H - 6), (cx + 26, H - 6)])

            # Team Rocket Red 'R' on chest
            if has_rocket_r:
                pygame.draw.rect(surf, (220, 30, 30), (cx - 8, shoulder_y + 8, 4, 14))
                pygame.draw.circle(surf, (220, 30, 30), (cx - 4, shoulder_y + 11), 5)
                pygame.draw.circle(surf, (25, 25, 30), (cx - 4, shoulder_y + 11), 2)
                pygame.draw.polygon(surf, (220, 30, 30), [(cx - 8, shoulder_y + 14), (cx + 4, shoulder_y + 22), (cx + 7, shoulder_y + 22), (cx - 5, shoulder_y + 14)])

            # 2. Neck
            pygame.draw.rect(surf, skin_col, (cx - 6, cy + 4, 12, 16))

            # 3. Head & Ears
            head_y = cy - 8
            pygame.draw.circle(surf, skin_col, (cx, head_y), 18)
            # Ears
            pygame.draw.circle(surf, skin_col, (cx - 18, head_y + 2), 5)
            pygame.draw.circle(surf, skin_col, (cx + 18, head_y + 2), 5)

            # 4. Long hair back (drawn behind face for female/Misty/Lass)
            if is_female and not is_channeler:
                if is_misty:
                    # High Side Ponytail (Right)
                    pygame.draw.ellipse(surf, hair_col, (cx + 14, head_y - 26, 20, 26))
                    pygame.draw.circle(surf, (40, 180, 210), (cx + 16, head_y - 12), 4) # Teal Ribbon
                else:
                    # Twin Pigtails
                    pygame.draw.ellipse(surf, hair_col, (cx - 26, head_y - 10, 14, 26))
                    pygame.draw.ellipse(surf, hair_col, (cx + 12, head_y - 10, 14, 26))
                    pygame.draw.circle(surf, (240, 60, 80), (cx - 18, head_y + 2), 3) # Ribbon
                    pygame.draw.circle(surf, (240, 60, 80), (cx + 18, head_y + 2), 3)

            # 5. Eyes, Eyebrows & Cheeks
            # Blush
            pygame.draw.circle(surf, (255, 170, 170), (cx - 11, head_y + 4), 4)
            pygame.draw.circle(surf, (255, 170, 170), (cx + 11, head_y + 4), 4)

            if is_brock:
                # Iconic Slanted Closed Eyes
                pygame.draw.line(surf, (40, 30, 25), (cx - 14, head_y - 2), (cx - 4, head_y - 4), 3)
                pygame.draw.line(surf, (40, 30, 25), (cx + 4, head_y - 4), (cx + 14, head_y - 2), 3)
                # Thick determined brows
                pygame.draw.line(surf, (40, 30, 25), (cx - 15, head_y - 7), (cx - 3, head_y - 9), 3)
                pygame.draw.line(surf, (40, 30, 25), (cx + 3, head_y - 9), (cx + 15, head_y - 7), 3)

            elif is_channeler:
                # Glowing Spirit Eyes
                pygame.draw.circle(surf, (230, 190, 255), (cx - 8, head_y - 2), 4)
                pygame.draw.circle(surf, (230, 190, 255), (cx + 8, head_y - 2), 4)
                pygame.draw.circle(surf, WHITE, (cx - 8, head_y - 2), 2)
                pygame.draw.circle(surf, WHITE, (cx + 8, head_y - 2), 2)

            else:
                # Open Expressive Eyes
                eye_col = (40, 120, 210) if is_misty else ((50, 150, 80) if is_blue else (40, 45, 55))
                pygame.draw.rect(surf, (30, 35, 45), (cx - 12, head_y - 5, 7, 7), border_radius=2)
                pygame.draw.rect(surf, (30, 35, 45), (cx + 5, head_y - 5, 7, 7), border_radius=2)
                pygame.draw.rect(surf, eye_col, (cx - 11, head_y - 4, 5, 5), border_radius=1)
                pygame.draw.rect(surf, eye_col, (cx + 6, head_y - 4, 5, 5), border_radius=1)
                # Specular Glints
                pygame.draw.rect(surf, WHITE, (cx - 10, head_y - 4, 2, 2))
                pygame.draw.rect(surf, WHITE, (cx + 7, head_y - 4, 2, 2))
                # Eyebrows
                if is_blue or is_rocket:
                    # Confident / Menacing smirk brow
                    pygame.draw.line(surf, (40, 30, 25), (cx - 13, head_y - 8), (cx - 4, head_y - 11), 2)
                    pygame.draw.line(surf, (40, 30, 25), (cx + 4, head_y - 10), (cx + 13, head_y - 7), 2)
                else:
                    pygame.draw.line(surf, (60, 45, 35), (cx - 12, head_y - 9), (cx - 4, head_y - 9), 2)
                    pygame.draw.line(surf, (60, 45, 35), (cx + 4, head_y - 9), (cx + 12, head_y - 9), 2)

            # Glasses / Spectacles
            if has_glasses:
                pygame.draw.rect(surf, (220, 230, 245), (cx - 14, head_y - 7, 11, 9), 2, border_radius=2)
                pygame.draw.rect(surf, (220, 230, 245), (cx + 3, head_y - 7, 11, 9), 2, border_radius=2)
                pygame.draw.line(surf, (220, 230, 245), (cx - 3, head_y - 3), (cx + 3, head_y - 3), 2)
                # Glint
                pygame.draw.line(surf, WHITE, (cx - 12, head_y - 5), (cx - 8, head_y - 5), 1)
                pygame.draw.line(surf, WHITE, (cx + 5, head_y - 5), (cx + 9, head_y - 5), 1)

            # Nose
            pygame.draw.rect(surf, (225, 175, 140), (cx - 1, head_y, 2, 3))

            # Mouth (Talking / Idle Animation)
            if is_talking:
                # Open speaking mouth
                pygame.draw.ellipse(surf, (170, 40, 40), (cx - 5, head_y + 6, 10, 6))
                pygame.draw.ellipse(surf, WHITE, (cx - 3, head_y + 6, 6, 2))
            else:
                if is_blue or is_rocket:
                    # Smug / wicked smirk
                    pygame.draw.arc(surf, (150, 40, 40), (cx - 4, head_y + 3, 9, 6), 3.14, 5.8, 2)
                else:
                    # Friendly smile
                    pygame.draw.arc(surf, (150, 40, 40), (cx - 5, head_y + 4, 10, 6), 3.14, 0, 2)

            # Hiker Beard / Stubble
            if is_hiker:
                pygame.draw.arc(surf, (65, 40, 25), (cx - 12, head_y - 2, 24, 18), 3.14, 0, 4)
                pygame.draw.rect(surf, (65, 40, 25), (cx - 6, head_y + 10, 12, 5), border_radius=2)

            # 6. Hair & Headgear Front
            if is_brock:
                # Spiky Peak Hair
                pts = [
                    (cx - 20, head_y - 8), (cx - 24, head_y - 22), (cx - 14, head_y - 18),
                    (cx - 12, head_y - 28), (cx - 2, head_y - 20), (cx, head_y - 30),
                    (cx + 8, head_y - 20), (cx + 14, head_y - 28), (cx + 16, head_y - 18),
                    (cx + 24, head_y - 22), (cx + 20, head_y - 8)
                ]
                pygame.draw.polygon(surf, hair_col, pts)
                pygame.draw.rect(surf, hair_col, (cx - 16, head_y - 16, 32, 10))

            elif is_blue:
                # Tall Stylized Spiky Auburn Hair
                pts = [
                    (cx - 18, head_y - 6), (cx - 26, head_y - 20), (cx - 14, head_y - 16),
                    (cx - 16, head_y - 32), (cx - 4, head_y - 22), (cx + 4, head_y - 34),
                    (cx + 12, head_y - 22), (cx + 24, head_y - 28), (cx + 18, head_y - 14),
                    (cx + 24, head_y - 10), (cx + 18, head_y - 4)
                ]
                pygame.draw.polygon(surf, hair_col, pts)
                pygame.draw.rect(surf, hair_col, (cx - 16, head_y - 16, 32, 10))

            elif is_rocket:
                # Black Beret with Red 'R'
                pygame.draw.ellipse(surf, hat_col, (cx - 22, head_y - 28, 44, 20))
                pygame.draw.circle(surf, (220, 30, 30), (cx - 4, head_y - 18), 5)
                # Front hair fringe
                pygame.draw.polygon(surf, hair_col, [(cx - 16, head_y - 12), (cx - 8, head_y - 6), (cx - 4, head_y - 12)])

            elif is_nurse:
                # Nurse Cap with Cross
                pygame.draw.ellipse(surf, hair_col, (cx - 20, head_y - 22, 14, 14)) # Twin hair loop left
                pygame.draw.ellipse(surf, hair_col, (cx + 6, head_y - 22, 14, 14)) # Twin hair loop right
                pygame.draw.rect(surf, WHITE, (cx - 14, head_y - 24, 28, 12), border_radius=4)
                pygame.draw.line(surf, (255, 100, 140), (cx, head_y - 22), (cx, head_y - 14), 3) # Cross vert
                pygame.draw.line(surf, (255, 100, 140), (cx - 4, head_y - 18), (cx + 4, head_y - 18), 3) # Cross horiz

            elif is_bug_catcher:
                # Wide Straw Sun Hat
                pygame.draw.ellipse(surf, (215, 185, 105), (cx - 26, head_y - 20, 52, 16))
                pygame.draw.ellipse(surf, (185, 155, 80), (cx - 16, head_y - 28, 32, 18))
                pygame.draw.rect(surf, (60, 140, 55), (cx - 16, head_y - 18, 32, 4)) # Green Ribbon

            elif is_blackbelt:
                # Martial Arts Headband
                pygame.draw.circle(surf, hair_col, (cx, head_y - 14), 16)
                pygame.draw.rect(surf, WHITE, (cx - 18, head_y - 14, 36, 6))
                pygame.draw.polygon(surf, WHITE, [(cx + 16, head_y - 12), (cx + 24, head_y - 4), (cx + 20, head_y - 2)])

            elif is_channeler:
                # Ghost Veil
                pygame.draw.ellipse(surf, hat_col, (cx - 20, head_y - 28, 40, 36))
                pygame.draw.ellipse(surf, (140, 80, 190), (cx - 16, head_y - 24, 32, 28), 2)

            elif is_engineer:
                # Yellow Hardhat
                pygame.draw.ellipse(surf, hat_col, (cx - 22, head_y - 28, 44, 22))
                pygame.draw.rect(surf, (220, 180, 20), (cx - 20, head_y - 18, 40, 5), border_radius=2)
                pygame.draw.circle(surf, WHITE, (cx, head_y - 22), 4) # Lamp

            elif is_hiker or is_fisherman:
                # Bucket / Hiking Hat
                pygame.draw.ellipse(surf, hat_col, (cx - 24, head_y - 20, 48, 16))
                pygame.draw.ellipse(surf, (155, 135, 95), (cx - 16, head_y - 26, 32, 16))

            elif hat_col:
                # Baseball Cap
                pygame.draw.ellipse(surf, hat_col, (cx - 20, head_y - 26, 40, 20))
                pygame.draw.rect(surf, WHITE, (cx - 16, head_y - 18, 32, 5), border_radius=2)

            else:
                # Styled Hair
                pygame.draw.circle(surf, hair_col, (cx, head_y - 14), 16)
                # Front fringe bangs
                pygame.draw.polygon(surf, hair_col, [(cx - 16, head_y - 14), (cx - 8, head_y - 6), (cx - 4, head_y - 12)])
                pygame.draw.polygon(surf, hair_col, [(cx + 4, head_y - 12), (cx + 10, head_y - 6), (cx + 16, head_y - 14)])

        # -------------------------------------------------------------
        # 3. Outer Metallic Bevel Card Border
        # -------------------------------------------------------------
        pygame.draw.rect(surf, (30, 35, 45), (4, 4, W - 8, H - 8), 3, border_radius=8)
        pygame.draw.rect(surf, border_col, (6, 6, W - 12, H - 12), 2, border_radius=6)
        pygame.draw.line(surf, border_highlight, (10, 8), (W - 10, 8), 2)
        pygame.draw.line(surf, border_highlight, (8, 10), (8, H - 10), 2)

        # Scale to requested size and cache
        final_surf = pygame.transform.scale(surf, size)
        self.cached_trainer_portraits[key] = final_surf
        return final_surf

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
        """Generates crisp pixel-art icons for all items in the game."""
        # 1. Poke Ball
        pb = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(pb, (220, 40, 40), (12, 12), 10) # Top red
        pygame.draw.arc(pb, WHITE, (2, 2, 20, 20), 3.14, 0, 10) # Bottom white
        pygame.draw.circle(pb, WHITE, (12, 17), 5) # Fill bottom white
        pygame.draw.line(pb, BLACK, (2, 12), (22, 12), 2)
        pygame.draw.circle(pb, BLACK, (12, 12), 4)
        pygame.draw.circle(pb, WHITE, (12, 12), 2)
        self.item_sprites["Poke Ball"] = pb
        
        # 2. Great Ball (Blue with red accents)
        gb = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(gb, (40, 100, 220), (12, 12), 10)
        pygame.draw.circle(gb, WHITE, (12, 17), 5)
        pygame.draw.line(gb, (220, 40, 40), (6, 5), (10, 9), 2)
        pygame.draw.line(gb, (220, 40, 40), (18, 5), (14, 9), 2)
        pygame.draw.line(gb, BLACK, (2, 12), (22, 12), 2)
        pygame.draw.circle(gb, BLACK, (12, 12), 4)
        pygame.draw.circle(gb, WHITE, (12, 12), 2)
        self.item_sprites["Great Ball"] = gb

        # 3. Ultra Ball (Black with yellow H)
        ub = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(ub, (40, 40, 50), (12, 12), 10)
        pygame.draw.circle(ub, WHITE, (12, 17), 5)
        pygame.draw.arc(ub, (240, 200, 40), (5, 4, 14, 10), 0, 3.14, 3)
        pygame.draw.line(ub, BLACK, (2, 12), (22, 12), 2)
        pygame.draw.circle(ub, BLACK, (12, 12), 4)
        pygame.draw.circle(ub, WHITE, (12, 12), 2)
        self.item_sprites["Ultra Ball"] = ub

        # 4. Potions (Purple, Orange, Blue)
        def _make_potion_spray(body_col, cap_col=(230, 230, 240)):
            s = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.rect(s, body_col, (7, 9, 10, 12), border_radius=3)
            pygame.draw.rect(s, cap_col, (9, 5, 6, 5))
            pygame.draw.rect(s, (100, 100, 110), (13, 3, 5, 3))
            pygame.draw.line(s, (255, 255, 255, 140), (8, 10), (8, 18), 1)
            return s

        self.item_sprites["Potion"] = _make_potion_spray((160, 80, 200)) # Purple
        self.item_sprites["Super Potion"] = _make_potion_spray((240, 130, 30)) # Orange
        self.item_sprites["Max Potion"] = _make_potion_spray((40, 140, 240)) # Royal Blue

        # 5. Revive (Golden Yellow Diamond Crystal)
        rev = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.polygon(rev, (245, 190, 40), [(12, 2), (22, 12), (12, 22), (2, 12)])
        pygame.draw.polygon(rev, (255, 240, 120), [(12, 5), (19, 12), (12, 19), (5, 12)])
        pygame.draw.polygon(rev, (210, 140, 20), [(12, 12), (22, 12), (12, 22)])
        pygame.draw.polygon(rev, (255, 255, 220), [(12, 5), (15, 10), (12, 12), (9, 10)])
        self.item_sprites["Revive"] = rev

        # 6. Status Medicines
        # Antidote (Green serum bottle)
        ant = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.rect(ant, (40, 180, 80), (7, 8, 10, 13), border_radius=3)
        pygame.draw.rect(ant, (220, 220, 230), (9, 4, 6, 5))
        pygame.draw.circle(ant, (20, 120, 50), (12, 14), 2)
        self.item_sprites["Antidote"] = ant

        # Paralyze Heal (Yellow spray)
        ph = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.rect(ph, (240, 210, 40), (7, 9, 10, 12), border_radius=3)
        pygame.draw.rect(ph, (230, 230, 240), (9, 5, 6, 5))
        pygame.draw.line(ph, (180, 120, 20), (11, 11), (13, 15), 2)
        self.item_sprites["Paralyze Heal"] = ph

        # Awakening (Blue smelling bottle)
        awk = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.rect(awk, (60, 140, 220), (7, 8, 10, 13), border_radius=3)
        pygame.draw.rect(awk, (220, 220, 230), (9, 4, 6, 5))
        pygame.draw.line(awk, WHITE, (9, 12), (15, 12), 2)
        self.item_sprites["Awakening"] = awk

        # Burn Heal (Crimson salve jar)
        bh = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.rect(bh, (220, 60, 50), (6, 9, 12, 11), border_radius=3)
        pygame.draw.rect(bh, (240, 200, 60), (7, 6, 10, 4), border_radius=1)
        pygame.draw.circle(bh, (255, 200, 100), (12, 14), 2)
        self.item_sprites["Burn Heal"] = bh

        # 7. Rare Candy (Wrapped sweet with blue ribbon)
        rc = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(rc, (80, 160, 240), (12, 12), 7)
        pygame.draw.polygon(rc, (50, 110, 200), [(4, 12), (1, 8), (1, 16)])
        pygame.draw.polygon(rc, (50, 110, 200), [(20, 12), (23, 8), (23, 16)])
        pygame.draw.arc(rc, WHITE, (7, 7, 10, 10), 0.5, 3.5, 2)
        self.item_sprites["Rare Candy"] = rc

        # 8. Evolution Stones
        # Moon Stone (Pale crescent moon in cosmic black stone)
        ms = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(ms, (55, 60, 80), (3, 3, 18, 18))
        pygame.draw.circle(ms, (230, 235, 255), (11, 11), 6)
        pygame.draw.circle(ms, (55, 60, 80), (13, 10), 5)
        pygame.draw.circle(ms, (255, 255, 255, 180), (16, 7), 1)
        self.item_sprites["Moon Stone"] = ms

        # Fire Stone (Warm orange stone with flame core)
        fs = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(fs, (230, 95, 25), (3, 3, 18, 18))
        pygame.draw.polygon(fs, (255, 215, 60), [(12, 6), (16, 14), (13, 17), (11, 17), (8, 14)])
        pygame.draw.polygon(fs, (255, 255, 200), [(12, 10), (14, 14), (12, 16), (10, 14)])
        self.item_sprites["Fire Stone"] = fs

        # Water Stone (Deep blue drop gem)
        ws = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(ws, (30, 100, 200), (3, 3, 18, 18))
        pygame.draw.polygon(ws, (100, 210, 255), [(12, 5), (17, 14), (12, 18), (7, 14)])
        pygame.draw.circle(ws, WHITE, (11, 11), 2)
        self.item_sprites["Water Stone"] = ws

        # Thunder Stone (Yellow electric stone)
        ts = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(ts, (215, 180, 20), (3, 3, 18, 18))
        pygame.draw.lines(ts, (255, 255, 255), False, [(15, 6), (11, 11), (14, 11), (9, 18)], 2)
        self.item_sprites["Thunder Stone"] = ts

        # Leaf Stone (Verdant green leaf stone)
        ls = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(ls, (40, 160, 70), (3, 3, 18, 18))
        pygame.draw.ellipse(ls, (130, 230, 120), (7, 7, 10, 10))
        pygame.draw.line(ls, (30, 110, 50), (9, 9), (15, 15), 2)
        self.item_sprites["Leaf Stone"] = ls

        # 9. Nugget (Gold Ingot)
        nug = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.polygon(nug, (245, 195, 30), [(4, 9), (9, 5), (19, 5), (15, 9)])
        pygame.draw.polygon(nug, (220, 160, 20), [(15, 9), (19, 5), (19, 15), (15, 19)])
        pygame.draw.polygon(nug, (255, 225, 70), [(4, 9), (15, 9), (15, 19), (4, 19)])
        pygame.draw.polygon(nug, (255, 245, 170), [(6, 10), (13, 10), (13, 13), (6, 13)])
        self.item_sprites["Nugget"] = nug

        # 10. Escape Rope
        er = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(er, (180, 130, 70), (12, 12), 8, 3)
        pygame.draw.line(er, (140, 95, 45), (15, 15), (20, 20), 3)
        self.item_sprites["Escape Rope"] = er

        # 11. Move Reroll Disk (CD with laser rainbow sheen)
        mrd = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(mrd, (70, 80, 100), (12, 12), 10)
        pygame.draw.circle(mrd, (150, 190, 230), (12, 12), 9)
        pygame.draw.arc(mrd, (255, 120, 200), (4, 4, 16, 16), 0.5, 2.0, 2)
        pygame.draw.arc(mrd, (80, 230, 255), (4, 4, 16, 16), 3.5, 5.0, 2)
        pygame.draw.circle(mrd, WHITE, (12, 12), 3)
        pygame.draw.circle(mrd, (40, 45, 60), (12, 12), 2)
        self.item_sprites["Move Reroll Disk"] = mrd

    def get_item_sprite(self, item_name, size=(32, 32)):
        """Returns a scaled surface of the item's sprite icon."""
        base_surf = self.item_sprites.get(item_name)
        if not base_surf:
            # Clean generic fallback icon
            base_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(base_surf, (160, 170, 185), (12, 12), 9)
            pygame.draw.circle(base_surf, WHITE, (12, 12), 7)
            pygame.draw.circle(base_surf, (100, 110, 130), (12, 12), 3)
        return pygame.transform.scale(base_surf, size)

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
        
        # 8. Distinct Building Architecture Tiles
        # A. Residential House Shingle Roof
        roof_house = pygame.Surface((T, T))
        roof_house.fill((195, 75, 40)) # Warm terracotta shingle
        for sh_y in [0, 8, 16, 24]:
            pygame.draw.line(roof_house, (235, 115, 75), (0, sh_y), (T, sh_y), 2)
            pygame.draw.line(roof_house, (140, 48, 24), (0, sh_y + 7), (T, sh_y + 7), 1)
            offset = 8 if sh_y % 16 == 0 else 0
            for sh_x in range(offset, T, 16):
                pygame.draw.line(roof_house, (140, 48, 24), (sh_x, sh_y), (sh_x, sh_y + 7), 1)
        self.cached_tiles["roof_house"] = roof_house

        # B. Oak Lab / Tech Facility Solar Roof
        roof_lab = pygame.Surface((T, T))
        roof_lab.fill((140, 165, 195)) # Tech silver steel
        pygame.draw.rect(roof_lab, (180, 205, 230), (0, 0, T, T), 1)
        pygame.draw.rect(roof_lab, (40, 75, 120), (4, 4, 10, 10))
        pygame.draw.rect(roof_lab, (40, 75, 120), (18, 4, 10, 10))
        pygame.draw.rect(roof_lab, (40, 75, 120), (4, 18, 10, 10))
        pygame.draw.rect(roof_lab, (40, 75, 120), (18, 18, 10, 10))
        pygame.draw.line(roof_lab, (100, 160, 240), (6, 6), (12, 12), 1)
        pygame.draw.line(roof_lab, (100, 160, 240), (20, 6), (26, 12), 1)
        self.cached_tiles["roof_oak_lab"] = roof_lab

        # C. Grand Gym Classical Temple Roof
        roof_gym = pygame.Surface((T, T))
        roof_gym.fill((175, 140, 95)) # Classical temple stone
        pygame.draw.rect(roof_gym, (215, 180, 130), (0, 0, T, 6))
        pygame.draw.rect(roof_gym, (130, 95, 55), (0, 6, T, 4))
        for dx in range(2, T, 6):
            pygame.draw.rect(roof_gym, (245, 220, 175), (dx, 2, 3, 3))
        pygame.draw.line(roof_gym, (100, 70, 40), (0, T - 1), (T, T - 1), 2)
        self.cached_tiles["roof_gym"] = roof_gym

        # D. PokéCenter Curved Red Roof with Poké Ball Emblem
        roof_red = pygame.Surface((T, T))
        roof_red.fill((225, 45, 45))
        pygame.draw.rect(roof_red, (255, 95, 95), (0, 0, T, 5))
        pygame.draw.line(roof_red, (150, 20, 20), (0, T - 1), (T, T - 1), 2)
        cx, cy = T // 2, T // 2 + 1
        pygame.draw.circle(roof_red, WHITE, (cx, cy), 7)
        pygame.draw.arc(roof_red, (240, 40, 40), (cx - 6, cy - 6, 12, 12), 0, 3.14, 6)
        pygame.draw.circle(roof_red, WHITE, (cx, cy + 3), 3)
        pygame.draw.line(roof_red, (40, 40, 50), (cx - 7, cy), (cx + 7, cy), 1)
        pygame.draw.circle(roof_red, (40, 40, 50), (cx, cy), 2)
        pygame.draw.circle(roof_red, WHITE, (cx, cy), 1)
        self.cached_tiles["roof_red"] = roof_red

        # E. PokéMart Blue Roof with Striped Awning & Golden "M" Logo
        roof_blue = pygame.Surface((T, T))
        roof_blue.fill((35, 110, 215))
        pygame.draw.rect(roof_blue, (90, 165, 255), (0, 0, T, 5))
        for col_i in range(0, T, 8):
            c_col = (245, 245, 255) if (col_i // 8) % 2 == 0 else (25, 90, 190)
            pygame.draw.rect(roof_blue, c_col, (col_i, T - 8, 8, 8))
        pygame.draw.line(roof_blue, (15, 60, 140), (0, T - 1), (T, T - 1), 2)
        pygame.draw.circle(roof_blue, (255, 215, 40), (T // 2, 11), 6)
        pygame.draw.circle(roof_blue, (200, 150, 10), (T // 2, 11), 6, 1)
        m_txt = self.fonts["small"].render("M", True, (160, 50, 10))
        roof_blue.blit(m_txt, (T // 2 - m_txt.get_width() // 2, 4))
        self.cached_tiles["roof_blue"] = roof_blue

        # F. Celadon Mega Department Store Roof
        roof_dept = pygame.Surface((T, T))
        roof_dept.fill((215, 175, 55)) # Gold commercial
        pygame.draw.rect(roof_dept, (255, 225, 110), (0, 0, T, 6))
        pygame.draw.rect(roof_dept, (160, 120, 20), (0, 6, T, 4))
        for dx in range(0, T, 8):
            pygame.draw.rect(roof_dept, (255, 245, 180) if (dx // 8) % 2 == 0 else (180, 140, 30), (dx, T - 8, 8, 8))
        self.cached_tiles["roof_dept_store"] = roof_dept

        # G. Silph Co. Skyscraper Roof
        roof_silph = pygame.Surface((T, T))
        roof_silph.fill((80, 100, 125)) # Modern steel
        pygame.draw.rect(roof_silph, (120, 150, 185), (0, 0, T, 4))
        pygame.draw.rect(roof_silph, (40, 55, 75), (4, 6, T - 8, T - 10))
        pygame.draw.line(roof_silph, (80, 220, 255), (6, 8), (T - 6, 8), 1)
        self.cached_tiles["roof_silph_co"] = roof_silph

        # ==========================================
        # Wall Tiles
        # ==========================================
        # A. Upper House Wall with Window & Blooming Flower Planter
        wall_house_win = pygame.Surface((T, T))
        wall_house_win.fill((248, 246, 240)) # Warm cream
        for sy in [8, 16, 24]:
            pygame.draw.line(wall_house_win, (220, 215, 205), (0, sy), (T, sy), 1)
        pygame.draw.rect(wall_house_win, (120, 80, 45), (6, 3, 20, 18), border_radius=2)
        pygame.draw.rect(wall_house_win, (130, 200, 245), (8, 5, 16, 14))
        pygame.draw.line(wall_house_win, (255, 255, 255), (9, 6), (15, 12), 1)
        pygame.draw.line(wall_house_win, (120, 80, 45), (16, 5), (16, 19), 1)
        pygame.draw.line(wall_house_win, (120, 80, 45), (8, 12), (24, 12), 1)
        pygame.draw.rect(wall_house_win, (150, 95, 55), (4, 19, 24, 6), border_radius=1)
        pygame.draw.circle(wall_house_win, (240, 50, 50), (7, 18), 3)
        pygame.draw.circle(wall_house_win, (255, 220, 40), (13, 17), 3)
        pygame.draw.circle(wall_house_win, (240, 50, 50), (19, 18), 3)
        pygame.draw.circle(wall_house_win, (60, 150, 240), (25, 17), 3)
        self.cached_tiles["wall_house_window"] = wall_house_win

        # B. Lower House Wall with Red Brick Base & Brass Carriage Lantern
        wall_house = pygame.Surface((T, T))
        wall_house.fill((248, 246, 240)) # Warm cream
        pygame.draw.rect(wall_house, (180, 75, 60), (0, 16, T, 16))
        pygame.draw.line(wall_house, (140, 55, 45), (0, 16), (T, 16), 1)
        pygame.draw.line(wall_house, (140, 55, 45), (0, 24), (T, 24), 1)
        pygame.draw.line(wall_house, (140, 55, 45), (0, 31), (T, 31), 1)
        pygame.draw.line(wall_house, (140, 55, 45), (8, 16), (8, 24), 1)
        pygame.draw.line(wall_house, (140, 55, 45), (24, 16), (24, 24), 1)
        pygame.draw.line(wall_house, (140, 55, 45), (16, 24), (16, 31), 1)
        pygame.draw.rect(wall_house, (50, 45, 40), (13, 4, 6, 9), border_radius=1)
        pygame.draw.rect(wall_house, (255, 230, 110), (14, 6, 4, 5))
        self.cached_tiles["wall_house"] = wall_house

        # C. Generic Commercial / Lab Wall White
        wall_white = pygame.Surface((T, T))
        wall_white.fill((242, 244, 248))
        pygame.draw.rect(wall_white, (210, 215, 225), (0, 0, T, T), 1)
        pygame.draw.rect(wall_white, (180, 190, 205), (0, T - 6, T, 6))
        self.cached_tiles["wall_white"] = wall_white

        # D. Oak Lab Tech Wall with Observation Screen
        wall_oak = pygame.Surface((T, T))
        wall_oak.fill((225, 235, 245))
        pygame.draw.rect(wall_oak, (160, 180, 205), (0, 0, T, T), 1)
        pygame.draw.rect(wall_oak, (40, 60, 85), (6, 5, 20, 16), border_radius=2)
        pygame.draw.rect(wall_oak, (60, 180, 230), (8, 7, 16, 12))
        pygame.draw.line(wall_oak, (120, 240, 255), (9, 13), (13, 9), 1)
        pygame.draw.line(wall_oak, (120, 240, 255), (15, 15), (21, 9), 1)
        pygame.draw.circle(wall_oak, (60, 220, 80), (8, 26), 2)
        pygame.draw.circle(wall_oak, (240, 60, 60), (14, 26), 2)
        self.cached_tiles["wall_oak_lab"] = wall_oak

        # E. Gym Classical Marble Wall
        wall_gym = pygame.Surface((T, T))
        wall_gym.fill((235, 228, 215)) # Warm marble
        pygame.draw.rect(wall_gym, (200, 190, 175), (0, 0, T, T), 1)
        pygame.draw.rect(wall_gym, (215, 200, 180), (6, 0, 8, T))
        pygame.draw.rect(wall_gym, (215, 200, 180), (18, 0, 8, T))
        pygame.draw.rect(wall_gym, (240, 190, 40), (14, 10, 4, 10), border_radius=1) # Torch sconce
        pygame.draw.circle(wall_gym, (255, 120, 20), (16, 8), 3) # Flame
        self.cached_tiles["wall_gym"] = wall_gym

        # F. Department Store / Silph Co Walls
        wall_dept = pygame.Surface((T, T))
        wall_dept.fill((230, 215, 170))
        pygame.draw.rect(wall_dept, (180, 150, 90), (0, 0, T, T), 1)
        pygame.draw.rect(wall_dept, (120, 180, 230), (4, 4, T - 8, T - 10))
        pygame.draw.line(wall_dept, WHITE, (6, 6), (16, 16), 1)
        self.cached_tiles["wall_dept_store"] = wall_dept

        wall_silph = pygame.Surface((T, T))
        wall_silph.fill((60, 75, 95))
        pygame.draw.rect(wall_silph, (90, 110, 140), (0, 0, T, T), 1)
        pygame.draw.rect(wall_silph, (30, 120, 180), (4, 4, T - 8, T - 10))
        pygame.draw.line(wall_silph, (120, 220, 255), (6, 6), (20, 20), 1)
        self.cached_tiles["wall_silph_co"] = wall_silph

        # ==========================================
        # Door Tiles
        # ==========================================
        # A. Residential Warm Oak Wood Door
        door_house = wall_house.copy()
        pygame.draw.rect(door_house, (180, 175, 165), (2, 28, 28, 4), border_radius=1)
        pygame.draw.rect(door_house, (100, 60, 30), (5, 4, 22, 26), border_radius=3)
        pygame.draw.rect(door_house, (160, 105, 55), (7, 6, 18, 22), border_radius=2)
        pygame.draw.rect(door_house, (130, 80, 40), (9, 8, 6, 8), border_radius=1)
        pygame.draw.rect(door_house, (130, 80, 40), (17, 8, 6, 8), border_radius=1)
        pygame.draw.rect(door_house, (130, 80, 40), (9, 18, 6, 8), border_radius=1)
        pygame.draw.rect(door_house, (130, 80, 40), (17, 18, 6, 8), border_radius=1)
        pygame.draw.circle(door_house, (255, 215, 40), (22, 17), 2)
        self.cached_tiles["door_house"] = door_house
        self.cached_tiles["door"] = door_house # Default fallback

        # B. PokéCenter Sliding Glass Doors
        door_center = wall_white.copy()
        pygame.draw.rect(door_center, (220, 45, 45), (4, 4, 24, 28), border_radius=2)
        pygame.draw.rect(door_center, (180, 230, 255), (6, 6, 9, 24))
        pygame.draw.rect(door_center, (180, 230, 255), (17, 6, 9, 24))
        pygame.draw.line(door_center, (255, 255, 255), (8, 8), (12, 16), 1)
        pygame.draw.line(door_center, (255, 255, 255), (19, 8), (23, 16), 1)
        pygame.draw.rect(door_center, (50, 220, 60), (14, 2, 4, 2))
        self.cached_tiles["door_center"] = door_center

        # C. PokéMart Commercial Glass Door
        door_mart = wall_white.copy()
        pygame.draw.rect(door_mart, (35, 110, 215), (4, 4, 24, 28), border_radius=2)
        pygame.draw.rect(door_mart, (200, 235, 255), (6, 6, 20, 24))
        pygame.draw.line(door_mart, (255, 255, 255), (9, 8), (14, 18), 1)
        pygame.draw.rect(door_mart, (255, 215, 40), (14, 16, 4, 4))
        self.cached_tiles["door_mart"] = door_mart

        # D. Oak Lab / Silph Co Electronic Keycard Door
        door_lab = wall_white.copy()
        pygame.draw.rect(door_lab, (100, 130, 165), (4, 4, 24, 28), border_radius=2)
        pygame.draw.rect(door_lab, (60, 90, 125), (6, 6, 20, 24))
        pygame.draw.line(door_lab, (80, 230, 255), (10, 16), (22, 16), 2)
        pygame.draw.circle(door_lab, (80, 255, 120), (22, 10), 2)
        self.cached_tiles["door_lab"] = door_lab

        # E. Grand Gym Reinforced Double Doors
        door_gym = wall_white.copy()
        pygame.draw.rect(door_gym, (130, 80, 45), (4, 4, 24, 28), border_radius=2)
        pygame.draw.rect(door_gym, (165, 115, 65), (6, 6, 9, 24))
        pygame.draw.rect(door_gym, (165, 115, 65), (17, 6, 9, 24))
        pygame.draw.circle(door_gym, (240, 190, 40), (11, 16), 3, 1)
        pygame.draw.circle(door_gym, (240, 190, 40), (21, 16), 3, 1)
        self.cached_tiles["door_gym"] = door_gym

        # ==========================================
        # Distinct Dungeon & Cave Entrance Tiles
        # Sand / Beach Shore
        sand = pygame.Surface((T, T))
        sand.fill((240, 220, 160)) # Golden sand
        for _ in range(10):
            rx = random.randint(1, T - 2)
            ry = random.randint(1, T - 2)
            sand.set_at((rx, ry), (220, 200, 140))
        self.cached_tiles["sand"] = sand

        # Cave Floor (Subterranean)
        cave_floor = pygame.Surface((T, T))
        cave_floor.fill((85, 75, 70)) # Dark stone brown
        for _ in range(12):
            rx = random.randint(1, T - 2)
            ry = random.randint(1, T - 2)
            cave_floor.set_at((rx, ry), (70, 60, 55))
            if random.random() < 0.3:
                cave_floor.set_at((rx, ry), (105, 95, 90))
        self.cached_tiles["cave_floor"] = cave_floor

        # ==========================================
        # 11. Cave Wall / Mountain Rock
        cave_wall = pygame.Surface((T, T))
        cave_wall.fill((45, 40, 38))
        pygame.draw.rect(cave_wall, (65, 58, 55), (2, 2, T - 4, T - 4), border_radius=4)
        pygame.draw.polygon(cave_wall, (30, 25, 24), [(4, 4), (16, 2), (28, 8), (20, 28), (6, 24)])
        pygame.draw.polygon(cave_wall, (75, 68, 65), [(8, 8), (18, 6), (24, 12), (18, 22), (10, 18)])
        self.cached_tiles["cave_wall"] = cave_wall

        # Generic Cave Door
        cave_door = cave_wall.copy()
        pygame.draw.arc(cave_door, (10, 10, 12), (6, 4, 20, 26), 0, 3.14, 10)
        pygame.draw.rect(cave_door, (10, 10, 12), (6, 12, 20, 20))
        self.cached_tiles["cave_door"] = cave_door

        # A. Mt. Moon Cavern Entrance (Rugged Timber Mine Arch with Moon Stone Vein)
        cave_moon = cave_wall.copy()
        pygame.draw.rect(cave_moon, (10, 10, 12), (6, 10, 20, 22))
        pygame.draw.arc(cave_moon, (10, 10, 12), (6, 2, 20, 20), 0, 3.14, 10)
        # Wooden mine support beams
        pygame.draw.rect(cave_moon, (140, 90, 45), (4, 4, 4, 28))
        pygame.draw.rect(cave_moon, (140, 90, 45), (24, 4, 4, 28))
        pygame.draw.rect(cave_moon, (160, 110, 55), (2, 2, 28, 5))
        # Hanging mining lantern
        pygame.draw.rect(cave_moon, (50, 45, 40), (14, 7, 4, 6))
        pygame.draw.circle(cave_moon, (255, 225, 100), (16, 10), 2)
        # Moon Stone cyan crystal vein
        pygame.draw.polygon(cave_moon, (120, 230, 255), [(2, 10), (5, 8), (4, 14)])
        pygame.draw.polygon(cave_moon, (120, 230, 255), [(27, 14), (30, 12), (29, 18)])
        self.cached_tiles["cave_door_mt_moon"] = cave_moon

        # B. Viridian Forest Living Tree Canopy Archway
        cave_forest = grass.copy()
        pygame.draw.rect(cave_forest, (20, 30, 15), (6, 10, 20, 22))
        pygame.draw.arc(cave_forest, (20, 30, 15), (6, 4, 20, 18), 0, 3.14, 10)
        # Ancient mossy tree trunk pillars
        pygame.draw.rect(cave_forest, (100, 65, 35), (2, 2, 6, 30), border_radius=2)
        pygame.draw.rect(cave_forest, (100, 65, 35), (24, 2, 6, 30), border_radius=2)
        pygame.draw.ellipse(cave_forest, (40, 130, 50), (0, 0, T, 12)) # Leafy canopy
        pygame.draw.ellipse(cave_forest, (65, 175, 75), (4, 2, T - 8, 8))
        # Hanging vines
        pygame.draw.line(cave_forest, (50, 150, 60), (10, 10), (10, 18), 2)
        pygame.draw.line(cave_forest, (50, 150, 60), (22, 10), (22, 16), 2)
        self.cached_tiles["cave_door_forest"] = cave_forest

        # C. Diglett's Cave Earthen Burrow Entrance
        cave_diglett = grass.copy()
        # Excavated earthen dirt mound
        pygame.draw.ellipse(cave_diglett, (140, 95, 55), (2, 4, 28, 26))
        pygame.draw.ellipse(cave_diglett, (100, 65, 35), (4, 8, 24, 22))
        pygame.draw.ellipse(cave_diglett, (20, 15, 10), (7, 12, 18, 18))
        # Wooden arch header
        pygame.draw.rect(cave_diglett, (160, 110, 55), (5, 6, 22, 4), border_radius=1)
        # Diglett warning marker
        pygame.draw.rect(cave_diglett, (180, 130, 80), (12, 0, 8, 7), border_radius=1)
        pygame.draw.circle(cave_diglett, (160, 80, 40), (16, 3), 2)
        self.cached_tiles["cave_door_diglett"] = cave_diglett

        # D. Power Plant Heavy Industrial Blast Gate
        gate_power = pygame.Surface((T, T))
        gate_power.fill((70, 75, 85))
        # Yellow and black hazard chevron warning border
        for h_i in range(0, T, 8):
            h_col = (245, 215, 30) if (h_i // 8) % 2 == 0 else (30, 30, 35)
            pygame.draw.rect(gate_power, h_col, (h_i, 0, 8, 5))
        pygame.draw.rect(gate_power, (40, 45, 55), (4, 6, 24, 26), border_radius=2)
        pygame.draw.rect(gate_power, (20, 22, 28), (6, 8, 20, 24))
        # Electric lightning symbol on steel door
        pygame.draw.lines(gate_power, (255, 235, 50), False, [(16, 11), (13, 18), (17, 18), (14, 26)], 2)
        pygame.draw.circle(gate_power, (255, 80, 80), (22, 11), 2) # Warning red beacon
        self.cached_tiles["gate_power_plant"] = gate_power

        # E. Pokémon Tower Haunted Gothic Stone Spire Gate
        gate_tower = pygame.Surface((T, T))
        gate_tower.fill((55, 42, 68)) # Haunted dark purple stone
        pygame.draw.rect(gate_tower, (75, 60, 90), (0, 0, T, T), 1)
        pygame.draw.rect(gate_tower, (18, 12, 25), (6, 8, 20, 24))
        pygame.draw.arc(gate_tower, (18, 12, 25), (6, 0, 20, 20), 0, 3.14, 10)
        # Gothic gargoyle pointed keystone
        pygame.draw.polygon(gate_tower, (95, 78, 115), [(16, 0), (12, 6), (20, 6)])
        # Iron portcullis bars
        for bx in [9, 13, 17, 21]:
            pygame.draw.line(gate_tower, (110, 95, 130), (bx, 6), (bx, 30), 1)
        pygame.draw.line(gate_tower, (110, 95, 130), (7, 16), (23, 16), 1)
        # Eerie violet spirit mist at entrance base
        pygame.draw.ellipse(gate_tower, (180, 130, 255), (6, 24, 20, 8))
        self.cached_tiles["gate_pokemon_tower"] = gate_tower

        # F. Seafoam Islands Glacial Ice Cavern Grotto
        cave_seafoam = pygame.Surface((T, T))
        cave_seafoam.fill((130, 205, 238)) # Glacial ice
        pygame.draw.rect(cave_seafoam, (15, 35, 60), (6, 10, 20, 22))
        pygame.draw.arc(cave_seafoam, (15, 35, 60), (6, 2, 20, 20), 0, 3.14, 10)
        # Glistening translucent ice pillars
        pygame.draw.rect(cave_seafoam, (190, 240, 255), (2, 2, 5, 28), border_radius=2)
        pygame.draw.rect(cave_seafoam, (190, 240, 255), (25, 2, 5, 28), border_radius=2)
        # Sparkling hanging icicles
        for ix, ih in [(8, 6), (12, 10), (16, 7), (20, 9), (23, 5)]:
            pygame.draw.polygon(cave_seafoam, (240, 252, 255), [(ix - 2, 4), (ix + 2, 4), (ix, 4 + ih)])
        self.cached_tiles["cave_door_seafoam"] = cave_seafoam

        # G. Safari Zone Tribal Lodge Archway
        gate_safari = pygame.Surface((T, T))
        gate_safari.fill((215, 190, 115)) # Warm amber savanna soil
        pygame.draw.rect(gate_safari, (40, 30, 20), (6, 10, 20, 22))
        pygame.draw.arc(gate_safari, (40, 30, 20), (6, 4, 20, 18), 0, 3.14, 10)
        # Thatched savanna canopy
        pygame.draw.rect(gate_safari, (195, 155, 65), (0, 0, T, 8), border_radius=2)
        pygame.draw.rect(gate_safari, (140, 95, 40), (2, 4, 5, 26))
        pygame.draw.rect(gate_safari, (140, 95, 40), (25, 4, 5, 26))
        # Safari Zone crest
        pygame.draw.circle(gate_safari, (240, 190, 40), (16, 6), 4)
        pygame.draw.circle(gate_safari, (45, 130, 40), (16, 6), 2)
        self.cached_tiles["gate_safari_zone"] = gate_safari

        # H. S.S. Anne Luxury Cruise Ship Gangway Pier
        pier_ss = pygame.Surface((T, T))
        pier_ss.fill((64, 136, 232)) # Ocean water base
        # Wooden pier deck
        pygame.draw.rect(pier_ss, (190, 145, 95), (4, 0, 24, T))
        for py in [0, 8, 16, 24]:
            pygame.draw.line(pier_ss, (140, 95, 55), (4, py), (28, py), 1)
        # Brass ocean ship railing
        pygame.draw.line(pier_ss, (240, 200, 60), (4, 0), (4, T), 2)
        pygame.draw.line(pier_ss, (240, 200, 60), (28, 0), (28, T), 2)
        # Red and white lifebuoy on post
        pygame.draw.circle(pier_ss, (230, 50, 50), (16, 8), 5)
        pygame.draw.circle(pier_ss, WHITE, (16, 8), 2)
        self.cached_tiles["pier_ss_anne"] = pier_ss

        # I. Victory Road Epic Jagged Cavern Gate
        cave_victory = cave_wall.copy()
        pygame.draw.rect(cave_victory, (8, 8, 10), (5, 8, 22, 24))
        pygame.draw.polygon(cave_victory, (8, 8, 10), [(5, 8), (16, 0), (27, 8)])
        # League Torch Braziers
        pygame.draw.rect(cave_victory, (180, 140, 40), (1, 10, 4, 14), border_radius=1)
        pygame.draw.circle(cave_victory, (255, 100, 20), (3, 8), 3) # Torch flame
        pygame.draw.rect(cave_victory, (180, 140, 40), (27, 10, 4, 14), border_radius=1)
        pygame.draw.circle(cave_victory, (255, 100, 20), (29, 8), 3)
        self.cached_tiles["cave_door_victory"] = cave_victory

        # J. Indigo Plateau Castle Gates
        gate_indigo = pygame.Surface((T, T))
        gate_indigo.fill((160, 140, 110))
        pygame.draw.rect(gate_indigo, (15, 15, 25), (5, 6, 22, 26), border_radius=3)
        # Golden League Columns
        pygame.draw.rect(gate_indigo, (245, 215, 60), (1, 0, 5, T))
        pygame.draw.rect(gate_indigo, (245, 215, 60), (26, 0, 5, T))
        pygame.draw.rect(gate_indigo, (220, 175, 30), (0, 0, T, 6))
        # Golden Champion Star Crest
        pygame.draw.polygon(gate_indigo, (255, 235, 80), [(16, 8), (18, 13), (23, 13), (19, 16), (21, 21), (16, 18), (11, 21), (13, 16), (9, 13), (14, 13)])
        self.cached_tiles["gate_indigo_plateau"] = gate_indigo

        # K. Cerulean Cave Fissure (Mysterious Psychic Cavern)
        cave_cerul = cave_wall.copy()
        pygame.draw.rect(cave_cerul, (12, 6, 20), (6, 6, 20, 26))
        pygame.draw.polygon(cave_cerul, (12, 6, 20), [(6, 6), (16, 1), (26, 6)])
        # Glowing dark purple psychic crystals
        pygame.draw.polygon(cave_cerul, (190, 80, 255), [(3, 8), (6, 4), (5, 14)])
        pygame.draw.polygon(cave_cerul, (160, 50, 240), [(26, 8), (29, 4), (28, 14)])
        pygame.draw.polygon(cave_cerul, (220, 140, 255), [(14, 10), (16, 6), (18, 10)])
        self.cached_tiles["cave_door_cerulean_cave"] = cave_cerul

        # ==========================================
        # Indoor House Floors & Furniture Tiles
        # ==========================================
        # Parquet Hardwood House Floor
        floor_house = pygame.Surface((T, T))
        floor_house.fill((218, 170, 115)) # Warm oak parquet
        # Parquet wood plank texture
        for px in [0, 16]:
            for py in [0, 16]:
                pygame.draw.rect(floor_house, (195, 148, 95), (px, py, 16, 16), 1)
                pygame.draw.line(floor_house, (230, 185, 130), (px + 1, py + 1), (px + 15, py + 1), 1)
        self.cached_tiles["floor_house"] = floor_house
        self.cached_tiles["floor"] = floor_house
        floor = floor_house

        # Indoor Living Room Rug / Carpet
        carpet = floor_house.copy()
        pygame.draw.rect(carpet, (190, 45, 45), (2, 2, T - 4, T - 4), border_radius=3)
        pygame.draw.rect(carpet, (240, 195, 60), (4, 4, T - 8, T - 8), 1, border_radius=2)
        pygame.draw.circle(carpet, (240, 195, 60), (T // 2, T // 2), 4)
        self.cached_tiles["carpet_house"] = carpet

        # Retro CRT Television Set
        tv_set = floor_house.copy()
        pygame.draw.rect(tv_set, (80, 50, 30), (3, 4, 26, 22), border_radius=2)
        pygame.draw.rect(tv_set, (30, 35, 45), (5, 6, 16, 14), border_radius=1)
        pygame.draw.rect(tv_set, (70, 150, 220), (7, 8, 12, 10)) # Screen game display
        pygame.draw.circle(tv_set, (240, 60, 60), (13, 13), 2) # Game sprite
        pygame.draw.circle(tv_set, (180, 170, 160), (24, 9), 2) # TV dial 1
        pygame.draw.circle(tv_set, (180, 170, 160), (24, 15), 2) # TV dial 2
        pygame.draw.line(tv_set, (160, 160, 170), (10, 4), (6, 0), 1) # TV antenna
        pygame.draw.line(tv_set, (160, 160, 170), (22, 4), (26, 0), 1)
        self.cached_tiles["tv_set"] = tv_set

        # Cozy Bedroom Bed
        bed = floor_house.copy()
        pygame.draw.rect(bed, (130, 80, 40), (4, 2, 24, 28), border_radius=3) # Wooden frame
        pygame.draw.rect(bed, (220, 55, 55), (6, 8, 20, 20), border_radius=2) # Red quilt
        pygame.draw.rect(bed, (248, 248, 252), (7, 4, 18, 7), border_radius=2) # White pillow
        pygame.draw.line(bed, (180, 30, 30), (6, 16), (25, 16), 1)
        self.cached_tiles["bed"] = bed

        # Kitchen Sink / Stove Counter
        kitchen_sink = floor_house.copy()
        pygame.draw.rect(kitchen_sink, (180, 140, 100), (2, 2, T - 4, T - 4), border_radius=2)
        pygame.draw.rect(kitchen_sink, (215, 220, 225), (4, 4, 14, 14), border_radius=1) # Metal sink basin
        pygame.draw.rect(kitchen_sink, (140, 150, 160), (6, 6, 10, 10))
        pygame.draw.circle(kitchen_sink, (240, 200, 60), (11, 3), 2) # Faucet tap
        # Kettle / Stove on right
        pygame.draw.circle(kitchen_sink, (40, 40, 45), (23, 11), 4)
        pygame.draw.circle(kitchen_sink, (220, 40, 40), (23, 11), 2)
        self.cached_tiles["kitchen_sink"] = kitchen_sink

        # Potted House Plant
        potted_plant = floor_house.copy()
        pygame.draw.rect(potted_plant, (190, 85, 45), (9, 14, 14, 14), border_radius=2) # Terracotta pot
        pygame.draw.rect(potted_plant, (140, 60, 30), (8, 14, 16, 3))
        # Green leafy foliage
        pygame.draw.circle(potted_plant, (35, 130, 45), (16, 9), 7)
        pygame.draw.circle(potted_plant, (65, 180, 70), (14, 7), 5)
        pygame.draw.circle(potted_plant, (65, 180, 70), (19, 9), 4)
        self.cached_tiles["potted_plant"] = potted_plant

        # Medical Clinic Floor for PokéCenter
        floor_center = pygame.Surface((T, T))
        floor_center.fill((246, 248, 252)) # Glossy white medical clinic tile
        pygame.draw.rect(floor_center, (220, 230, 245), (0, 0, T, T), 1)
        pygame.draw.rect(floor_center, (235, 242, 255), (2, 2, T - 4, T - 4), 1)
        self.cached_tiles["floor_center"] = floor_center

        # Commercial Floor for PokéMart
        floor_mart = pygame.Surface((T, T))
        floor_mart.fill((238, 244, 252)) # Crisp commercial tile
        pygame.draw.rect(floor_mart, (195, 215, 240), (0, 0, T, T), 1)
        self.cached_tiles["floor_mart"] = floor_mart

        # High-Tech Stainless Steel Grating for Labs
        floor_lab = pygame.Surface((T, T))
        floor_lab.fill((220, 228, 238))
        for gy_i in range(0, T, 8):
            pygame.draw.line(floor_lab, (190, 200, 215), (0, gy_i), (T, gy_i), 1)
            pygame.draw.line(floor_lab, (190, 200, 215), (gy_i, 0), (gy_i, T), 1)
        self.cached_tiles["floor_lab"] = floor_lab

        # Sign
        sign = grass.copy()
        pygame.draw.rect(sign, (140, 90, 50), (6, 8, 20, 14), border_radius=2)
        pygame.draw.rect(sign, (230, 210, 160), (8, 10, 16, 10))
        pygame.draw.rect(sign, (100, 60, 30), (14, 22, 4, 10))
        self.cached_tiles["sign"] = sign

        # Indoor Counter
        counter = pygame.Surface((T, T))
        counter.fill((160, 100, 60))
        pygame.draw.rect(counter, (200, 140, 90), (2, 2, T - 4, 6))
        pygame.draw.rect(counter, (120, 70, 35), (0, 0, T, T), 2)
        self.cached_tiles["counter"] = counter

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

        # ==========================================
        # 23. WALK-THROUGH ENCOUNTER PROPS
        # ==========================================
        # A. Wildflower Meadow ('F' / '*')
        flower_meadow = grass.copy()
        # Stems and leafy foliage
        pygame.draw.line(flower_meadow, (35, 110, 30), (8, 14), (8, 22), 2)
        pygame.draw.line(flower_meadow, (35, 110, 30), (22, 10), (22, 18), 2)
        pygame.draw.line(flower_meadow, (35, 110, 30), (15, 20), (15, 28), 2)
        # Red Bloom
        pygame.draw.circle(flower_meadow, (240, 50, 60), (8, 12), 4)
        pygame.draw.circle(flower_meadow, (255, 230, 60), (8, 12), 2)
        # Sky Blue Bloom
        pygame.draw.circle(flower_meadow, (60, 165, 245), (22, 9), 4)
        pygame.draw.circle(flower_meadow, WHITE, (22, 9), 2)
        # Gold Bloom
        pygame.draw.circle(flower_meadow, (250, 205, 40), (15, 20), 4)
        pygame.draw.circle(flower_meadow, (230, 100, 20), (15, 20), 2)
        # Cherry Pink mini-blooms
        pygame.draw.circle(flower_meadow, (255, 120, 190), (25, 24), 3)
        pygame.draw.circle(flower_meadow, WHITE, (25, 24), 1)
        pygame.draw.circle(flower_meadow, (255, 120, 190), (5, 25), 3)
        pygame.draw.circle(flower_meadow, WHITE, (5, 25), 1)
        self.cached_tiles["flower_meadow"] = flower_meadow

        # B. Autumn Leaf Pile ('L')
        leaf_pile = grass.copy()
        # Scattered autumn leaves
        # Orange maple leaf
        pygame.draw.polygon(leaf_pile, (230, 115, 35), [(8, 6), (12, 12), (10, 16), (4, 14), (4, 8)])
        pygame.draw.line(leaf_pile, (170, 70, 20), (8, 8), (10, 16), 1)
        # Crimson oak leaf
        pygame.draw.polygon(leaf_pile, (200, 45, 40), [(22, 14), (26, 8), (28, 14), (24, 20), (20, 16)])
        pygame.draw.line(leaf_pile, (140, 25, 20), (24, 10), (22, 18), 1)
        # Golden aspen leaf
        pygame.draw.polygon(leaf_pile, (240, 195, 45), [(14, 18), (18, 14), (20, 22), (16, 26), (12, 22)])
        pygame.draw.line(leaf_pile, (180, 130, 25), (16, 16), (16, 24), 1)
        # Russet small leaves
        pygame.draw.ellipse(leaf_pile, (145, 75, 35), (4, 22, 7, 5))
        pygame.draw.ellipse(leaf_pile, (225, 140, 50), (22, 24, 6, 4))
        self.cached_tiles["leaf_pile"] = leaf_pile

        # C. Cave Rubble / Crags ('r')
        cave_rubble = cave_floor.copy()
        # Large jagged stone
        pygame.draw.polygon(cave_rubble, (125, 115, 110), [(6, 10), (14, 6), (18, 12), (12, 18), (4, 14)])
        pygame.draw.polygon(cave_rubble, (160, 150, 145), [(7, 9), (13, 7), (16, 11), (12, 12)])
        pygame.draw.polygon(cave_rubble, (55, 48, 45), [(4, 14), (12, 18), (10, 20), (3, 16)])
        # Medium rock
        pygame.draw.polygon(cave_rubble, (110, 100, 95), [(20, 16), (27, 13), (29, 21), (22, 25)])
        pygame.draw.polygon(cave_rubble, (145, 135, 130), [(21, 15), (26, 14), (27, 19)])
        # Small gravel & quartz chips
        pygame.draw.circle(cave_rubble, (215, 215, 225), (9, 24), 2)
        pygame.draw.circle(cave_rubble, (215, 215, 225), (22, 8), 2)
        pygame.draw.circle(cave_rubble, (80, 70, 65), (16, 26), 2)
        self.cached_tiles["cave_rubble"] = cave_rubble

        # D. Snow Drift ('x')
        snow_drift = pygame.Surface((T, T))
        snow_drift.fill((232, 246, 255)) # Soft powder snow
        # Gentle cyan drift curves
        pygame.draw.ellipse(snow_drift, (190, 225, 248), (2, 8, 28, 14))
        pygame.draw.ellipse(snow_drift, (248, 252, 255), (4, 6, 24, 12))
        pygame.draw.ellipse(snow_drift, (180, 218, 245), (6, 18, 22, 12))
        pygame.draw.ellipse(snow_drift, (255, 255, 255), (8, 16, 18, 10))
        # Glistening frost sparkles
        pygame.draw.circle(snow_drift, (255, 255, 255), (10, 10), 2)
        pygame.draw.line(snow_drift, (130, 205, 255), (10, 8), (10, 12), 1)
        pygame.draw.line(snow_drift, (130, 205, 255), (8, 10), (12, 10), 1)
        pygame.draw.circle(snow_drift, (255, 255, 255), (22, 20), 2)
        self.cached_tiles["snow_drift"] = snow_drift

        # E. Haunted Mist / Spirit Fog ('m')
        spooky_mist = lavender_ground.copy()
        mist_layer = pygame.Surface((T, T), pygame.SRCALPHA)
        # Swirling ethereal violet bands
        pygame.draw.ellipse(mist_layer, (160, 110, 210, 130), (2, 4, 28, 12))
        pygame.draw.ellipse(mist_layer, (210, 160, 255, 160), (6, 6, 20, 8))
        pygame.draw.ellipse(mist_layer, (140, 90, 190, 140), (4, 16, 26, 12))
        pygame.draw.ellipse(mist_layer, (200, 150, 250, 170), (8, 18, 18, 8))
        # Glowing spirit orbs
        pygame.draw.circle(mist_layer, (240, 210, 255, 220), (12, 10), 2)
        pygame.draw.circle(mist_layer, (240, 210, 255, 220), (22, 22), 2)
        spooky_mist.blit(mist_layer, (0, 0))
        self.cached_tiles["spooky_mist"] = spooky_mist

        # F. Volcanic Ash & Embers ('a')
        volcanic_ash = pygame.Surface((T, T))
        volcanic_ash.fill((52, 45, 50)) # Charcoal dark basalt
        # Ash soot mounds
        pygame.draw.ellipse(volcanic_ash, (78, 68, 74), (2, 6, 18, 10))
        pygame.draw.ellipse(volcanic_ash, (70, 62, 66), (14, 16, 16, 12))
        # Glowing volcanic embers
        pygame.draw.circle(volcanic_ash, (255, 60, 20), (8, 10), 3)
        pygame.draw.circle(volcanic_ash, (255, 200, 50), (8, 10), 1)
        pygame.draw.circle(volcanic_ash, (255, 80, 20), (22, 20), 3)
        pygame.draw.circle(volcanic_ash, (255, 220, 80), (22, 20), 1)
        pygame.draw.circle(volcanic_ash, (240, 40, 10), (16, 14), 2)
        self.cached_tiles["volcanic_ash"] = volcanic_ash

        # G. Swamp Marsh / Mud Bog ('u')
        swamp_marsh = pygame.Surface((T, T))
        swamp_marsh.fill((58, 105, 90)) # Deep murky marsh water
        # Mud banks
        pygame.draw.ellipse(swamp_marsh, (98, 76, 48), (0, 0, 16, 12))
        pygame.draw.ellipse(swamp_marsh, (98, 76, 48), (14, 18, 18, 14))
        # Water ripples
        pygame.draw.arc(swamp_marsh, (110, 175, 155), (4, 12, 14, 6), 0, 3.14, 1)
        pygame.draw.arc(swamp_marsh, (110, 175, 155), (16, 8, 12, 5), 0, 3.14, 1)
        # Lily pad
        pygame.draw.ellipse(swamp_marsh, (45, 155, 65), (6, 18, 9, 6))
        pygame.draw.circle(swamp_marsh, (255, 140, 180), (10, 20), 2) # Lily flower
        # Cattail reeds
        pygame.draw.line(swamp_marsh, (35, 110, 45), (25, 6), (25, 16), 2)
        pygame.draw.rect(swamp_marsh, (120, 65, 25), (24, 4, 3, 6), border_radius=1)
        self.cached_tiles["swamp_marsh"] = swamp_marsh

        # H. Electric Surge Grid ('e')
        electric_surge = pygame.Surface((T, T))
        electric_surge.fill((55, 62, 75)) # Dark industrial conduit metal
        pygame.draw.rect(electric_surge, (85, 95, 115), (0, 0, T, T), 1)
        # Glowing circuit grid lines
        pygame.draw.line(electric_surge, (40, 190, 240), (0, 16), (T, 16), 2)
        pygame.draw.line(electric_surge, (40, 190, 240), (16, 0), (16, T), 2)
        # Central energy capacitor
        pygame.draw.rect(electric_surge, (30, 35, 45), (10, 10, 12, 12), border_radius=2)
        pygame.draw.circle(electric_surge, (255, 235, 60), (16, 16), 4) # Electric core
        pygame.draw.circle(electric_surge, WHITE, (16, 16), 2)
        # Electric spark lightning bolts
        pygame.draw.lines(electric_surge, (255, 240, 80), False, [(6, 6), (10, 10), (8, 14), (12, 16)], 2)
        pygame.draw.lines(electric_surge, (120, 240, 255), False, [(26, 26), (22, 22), (24, 18), (20, 16)], 2)
        self.cached_tiles["electric_surge"] = electric_surge

        # ==========================================
        # 24. IMMERSIVE LOWER-BODY FOOT OVERLAYS
        # ==========================================
        # Rendered over the lower portion of the player when standing in walk-through props

        # Grass overlay
        ol_grass = pygame.Surface((T, T), pygame.SRCALPHA)
        for x in [4, 10, 16, 22, 28]:
            pygame.draw.polygon(ol_grass, (45, 130, 40), [(x - 2, T), (x, T - 12), (x + 2, T)])
            pygame.draw.polygon(ol_grass, (75, 175, 60), [(x - 1, T), (x, T - 10), (x + 1, T)])
        self.prop_overlays['G'] = ol_grass

        # Flower meadow overlay
        ol_flower = pygame.Surface((T, T), pygame.SRCALPHA)
        for x, col in [(6, (240, 50, 60)), (14, (60, 165, 245)), (22, (250, 205, 40)), (28, (255, 120, 190))]:
            pygame.draw.line(ol_flower, (35, 110, 30), (x, T), (x, T - 10), 2)
            pygame.draw.circle(ol_flower, col, (x, T - 10), 4)
            pygame.draw.circle(ol_flower, WHITE, (x, T - 10), 1)
        self.prop_overlays['F'] = ol_flower
        self.prop_overlays['*'] = ol_flower

        # Autumn leaves overlay
        ol_leaf = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.polygon(ol_leaf, (230, 115, 35), [(4, T - 2), (8, T - 10), (12, T - 2)])
        pygame.draw.polygon(ol_leaf, (200, 45, 40), [(14, T - 2), (18, T - 8), (22, T - 2)])
        pygame.draw.polygon(ol_leaf, (240, 195, 45), [(22, T - 2), (26, T - 9), (30, T - 2)])
        self.prop_overlays['L'] = ol_leaf

        # Cave rubble overlay
        ol_rubble = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.polygon(ol_rubble, (130, 120, 115), [(4, T), (8, T - 8), (14, T)])
        pygame.draw.polygon(ol_rubble, (110, 100, 95), [(18, T), (24, T - 7), (29, T)])
        pygame.draw.circle(ol_rubble, (215, 215, 225), (16, T - 4), 2)
        self.prop_overlays['r'] = ol_rubble

        # Snow drift overlay (snow covering boots up to shins)
        ol_snow = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.ellipse(ol_snow, (190, 225, 248), (2, T - 14, 28, 14))
        pygame.draw.ellipse(ol_snow, (255, 255, 255), (4, T - 12, 24, 12))
        pygame.draw.circle(ol_snow, (130, 205, 255), (10, T - 8), 1)
        pygame.draw.circle(ol_snow, (130, 205, 255), (22, T - 8), 1)
        self.prop_overlays['x'] = ol_snow

        # Haunted mist overlay (wisps drifting around lower body)
        ol_mist = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.ellipse(ol_mist, (160, 110, 210, 140), (2, T - 18, 28, 14))
        pygame.draw.ellipse(ol_mist, (210, 160, 255, 170), (6, T - 14, 20, 10))
        pygame.draw.circle(ol_mist, (240, 210, 255, 220), (12, T - 12), 2)
        pygame.draw.circle(ol_mist, (240, 210, 255, 220), (20, T - 10), 2)
        self.prop_overlays['m'] = ol_mist

        # Volcanic ash overlay
        ol_ash = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.ellipse(ol_ash, (78, 68, 74), (2, T - 10, 28, 10))
        pygame.draw.circle(ol_ash, (255, 60, 20), (8, T - 6), 3)
        pygame.draw.circle(ol_ash, (255, 200, 50), (8, T - 6), 1)
        pygame.draw.circle(ol_ash, (255, 80, 20), (22, T - 5), 3)
        pygame.draw.circle(ol_ash, (255, 220, 80), (22, T - 5), 1)
        self.prop_overlays['a'] = ol_ash

        # Swamp marsh overlay (mud & water splash)
        ol_marsh = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.ellipse(ol_marsh, (58, 105, 90, 180), (2, T - 12, 28, 12))
        pygame.draw.arc(ol_marsh, (120, 185, 170), (4, T - 10, 14, 6), 0, 3.14, 2)
        pygame.draw.arc(ol_marsh, (120, 185, 170), (16, T - 8, 12, 5), 0, 3.14, 2)
        pygame.draw.circle(ol_marsh, (45, 155, 65), (8, T - 6), 3)
        self.prop_overlays['u'] = ol_marsh

        # Electric surge grid overlay (static arcs around boots)
        ol_spark = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.lines(ol_spark, (255, 240, 80), False, [(6, T - 2), (10, T - 8), (8, T - 12), (12, T - 14)], 2)
        pygame.draw.lines(ol_spark, (120, 240, 255), False, [(26, T - 2), (22, T - 8), (24, T - 12), (20, T - 14)], 2)
        pygame.draw.circle(ol_spark, (255, 255, 255), (12, T - 14), 2)
        pygame.draw.circle(ol_spark, (255, 255, 255), (20, T - 14), 2)
        self.prop_overlays['e'] = ol_spark



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


