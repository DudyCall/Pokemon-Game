"""
ui_trainer.py - Trainer Card, Kanto Interactive Region Map, and Quest Log interfaces.
"""
import math
import random
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY,
    UI_BG, UI_BORDER_DARK, UI_BORDER_LIGHT, UI_TEXT, UI_TEXT_MUTED,
    HP_GREEN, HP_YELLOW, HP_RED, EXP_BLUE, TYPE_COLORS,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_CONFIRM, KEY_CANCEL, KEY_MENU,
    OUTFIT_THEMES, HAIR_COLORS, HAT_STYLES, STARTER_CHOICES
)
from graphics_manager import gfx
from sound_manager import sound_mgr
from pokemon_data import POKEMON_SPECIES, ITEMS, MOVES, WILD_ENCOUNTERS, WILD_WATER_ENCOUNTERS, STONE_EVOLUTIONS

class TrainerCardScreen:
    """
    Comprehensive Trainer Card and Interactive Region Map Screen.
    Displays trainer identity, money, Pokédex count, official Gym Badges,
    and a full graphical Kanto Region Map highlighting the player's current location.
    """
    def __init__(self, player, world, inventory, pokedex, initial_tab=0):
        self.player = player
        self.world = world
        self.inventory = inventory
        self.pokedex = pokedex
        self.active_tab = initial_tab # 0: Trainer Card, 1: Region Map
        self.timer = 0.0

        self.kanto_badges = [
            ("Boulder Badge", "Pewter Gym", "Leader Brock (Rock)"),
            ("Cascade Badge", "Cerulean Gym", "Leader Misty (Water)"),
            ("Thunder Badge", "Vermilion Gym", "Leader Surge (Electric)"),
            ("Rainbow Badge", "Celadon Gym", "Leader Erika (Grass)"),
            ("Soul Badge", "Fuchsia Gym", "Leader Koga (Poison)"),
            ("Marsh Badge", "Saffron Gym", "Leader Sabrina (Psychic)"),
            ("Volcano Badge", "Cinnabar Gym", "Leader Blaine (Fire)"),
            ("Earth Badge", "Viridian Gym", "Leader Giovanni (Ground)")
        ]

        # Structured Grid Map Nodes for Kanto Region Map (gx: 0..8, gy: 0..7)
        self.map_nodes = [
            {"name": "Indigo Plateau", "gx": 0, "gy": 0, "x": 130, "y": 70, "label_pos": "bottom", "short_label": "INDIGO", "desc": "Supreme Pokémon League Headquarters where Champion Blue awaits.", "type": "CITY"},
            {"name": "Victory Road", "gx": 0, "gy": 1, "x": 130, "y": 160, "label_pos": "right", "short_label": "VIC. ROAD", "desc": "Epic cavern testing trainers who conquered all 8 Kanto Gyms.", "type": "DUNGEON"},
            {"name": "Route 22", "gx": 0, "gy": 3, "x": 130, "y": 280, "label_pos": "none", "short_label": "", "desc": "Foothills leading west to the Indigo Plateau League Gate.", "type": "ROUTE"},
            {"name": "Viridian City", "gx": 2, "gy": 3, "x": 220, "y": 280, "label_pos": "left", "short_label": "VIRIDIAN", "desc": "The gateway crossroads city with Pokémon Center and Mart.", "type": "CITY"},
            {"name": "Viridian Forest", "gx": 2, "gy": 2, "x": 220, "y": 210, "label_pos": "left", "short_label": "V. FOREST", "desc": "Deep woods labyrinth teeming with bug Pokémon and Pikachu.", "type": "DUNGEON"},
            {"name": "Pewter City", "gx": 2, "gy": 1, "x": 220, "y": 140, "label_pos": "top", "short_label": "PEWTER", "desc": "A stone gray city. Home of Leader Brock's Gym & the Museum.", "type": "CITY"},
            {"name": "Route 3", "gx": 3, "gy": 1, "x": 310, "y": 140, "label_pos": "none", "short_label": "", "desc": "Mountain canyon foothills leading east to Mt. Moon.", "type": "ROUTE"},
            {"name": "Mt. Moon", "gx": 4, "gy": 1, "x": 400, "y": 140, "label_pos": "top", "short_label": "MT. MOON", "desc": "Subterranean cavern rich in ancient fossils and Moon Stones.", "type": "DUNGEON"},
            {"name": "Route 4", "gx": 5, "gy": 1, "x": 490, "y": 140, "label_pos": "none", "short_label": "", "desc": "Scenic river canyon slopes leading to Cerulean City.", "type": "ROUTE"},
            {"name": "Cerulean City", "gx": 6, "gy": 1, "x": 580, "y": 140, "label_pos": "top", "short_label": "CERULEAN", "desc": "A floral canal metropolis. Home of Leader Misty's Gym.", "type": "CITY"},
            {"name": "Cerulean Cave", "gx": 6, "gy": 0, "x": 580, "y": 70, "label_pos": "left", "short_label": "C. CAVE", "desc": "Mysterious subterranean lair of legendary wild Pokémon and Mewtwo.", "type": "DUNGEON"},
            {"name": "Route 24", "gx": 7, "gy": 0, "x": 670, "y": 70, "label_pos": "top", "short_label": "RT 24", "desc": "Nugget Bridge gauntlet leading north to Bill's Sea Cottage.", "type": "ROUTE"},
            {"name": "Route 9", "gx": 7, "gy": 1, "x": 670, "y": 140, "label_pos": "none", "short_label": "", "desc": "Rocky badlands canyon trail connecting Cerulean and Lavender.", "type": "ROUTE"},
            {"name": "Power Plant", "gx": 8, "gy": 1, "x": 750, "y": 140, "label_pos": "top", "short_label": "POWER PL.", "desc": "Industrial electric generating facility teeming with Electric Pokémon.", "type": "DUNGEON"},
            {"name": "Route 5", "gx": 6, "gy": 2, "x": 580, "y": 210, "label_pos": "none", "short_label": "", "desc": "Grassy highway connecting Cerulean City south to Saffron City.", "type": "ROUTE"},
            {"name": "Celadon City", "gx": 4, "gy": 3, "x": 450, "y": 280, "label_pos": "left", "short_label": "CELADON", "desc": "Bustling rainbow metropolis with Mega Department Store & Erika's Gym.", "type": "CITY"},
            {"name": "Route 7", "gx": 5, "gy": 3, "x": 510, "y": 280, "label_pos": "none", "short_label": "", "desc": "Road connecting Celadon City east to the Saffron Metropolis.", "type": "ROUTE"},
            {"name": "Saffron City", "gx": 6, "gy": 3, "x": 580, "y": 280, "label_pos": "bottom", "short_label": "SAFFRON", "desc": "Golden mega-city crossroad with Silph Co. & Sabrina's Psychic Gym.", "type": "CITY"},
            {"name": "Route 8", "gx": 7, "gy": 3, "x": 670, "y": 280, "label_pos": "none", "short_label": "", "desc": "Road connecting Saffron City east to Lavender Town.", "type": "ROUTE"},
            {"name": "Lavender Town", "gx": 8, "gy": 3, "x": 750, "y": 280, "label_pos": "right", "short_label": "LAVENDER", "desc": "A noble purple town enveloped in mist, home of Pokémon Tower.", "type": "TOWN"},
            {"name": "Pokémon Tower", "gx": 8, "gy": 2, "x": 750, "y": 210, "label_pos": "right", "short_label": "TOWER", "desc": "Sacred haunted spire where spirits of Pokémon rest in peace.", "type": "DUNGEON"},
            {"name": "Route 6", "gx": 6, "gy": 4, "x": 580, "y": 350, "label_pos": "none", "short_label": "", "desc": "Waterway route connecting Saffron City south to Vermilion Harbor.", "type": "ROUTE"},
            {"name": "Vermilion City", "gx": 6, "gy": 5, "x": 580, "y": 420, "label_pos": "left", "short_label": "VERMILION", "desc": "Sunset harbor city with Lt. Surge's Gym & the luxury S.S. Anne.", "type": "CITY"},
            {"name": "S.S. Anne", "gx": 6, "gy": 6, "x": 580, "y": 490, "label_pos": "left", "short_label": "S.S. ANNE", "desc": "Grand luxury world cruise liner docked at Vermilion Harbor Pier.", "type": "DUNGEON"},
            {"name": "Route 11", "gx": 7, "gy": 5, "x": 670, "y": 420, "label_pos": "none", "short_label": "", "desc": "East meadow route with Diglett's Cave entrance leading to Route 12.", "type": "ROUTE"},
            {"name": "Diglett's Cave", "gx": 8, "gy": 5, "x": 310, "y": 280, "label_pos": "right", "short_label": "DIGLETT", "desc": "Underground mountain tunnel dug by wild Diglett connecting Route 11 and Pewter.", "type": "DUNGEON"},
            {"name": "Route 12", "gx": 8, "gy": 4, "x": 750, "y": 420, "label_pos": "none", "short_label": "", "desc": "Scenic Silence Bridge over ocean waters connecting to Fuchsia City.", "type": "ROUTE"},
            {"name": "Fuchsia City", "gx": 8, "gy": 7, "x": 750, "y": 490, "label_pos": "right", "short_label": "FUCHSIA", "desc": "Historic ninja town with Koga's Poison Gym & the Safari Zone.", "type": "CITY"},
            {"name": "Safari Zone", "gx": 7, "gy": 7, "x": 670, "y": 490, "label_pos": "top", "short_label": "SAFARI", "desc": "Vast golden savanna reserve filled with rare wild Pokémon.", "type": "DUNGEON"},
            {"name": "Pallet Town", "gx": 2, "gy": 5, "x": 220, "y": 420, "label_pos": "left", "short_label": "PALLET", "desc": "A quiet hometown with fresh sea breezes and Prof. Oak's Lab.", "type": "TOWN"},
            {"name": "Route 1", "gx": 2, "gy": 4, "x": 220, "y": 350, "label_pos": "none", "short_label": "", "desc": "Lush grassy path connecting Pallet Town and Viridian City.", "type": "ROUTE"},
            {"name": "Route 21", "gx": 2, "gy": 6, "x": 220, "y": 490, "label_pos": "none", "short_label": "", "desc": "Vast ocean sea route south of Pallet Town filled with water Pokémon.", "type": "ROUTE"},
            {"name": "Cinnabar Island", "gx": 2, "gy": 7, "x": 220, "y": 570, "label_pos": "left", "short_label": "CINNABAR", "desc": "A fiery volcanic island with Pokémon research laboratories and Blaine's Gym.", "type": "CITY"},
            {"name": "Seafoam Islands", "gx": 4, "gy": 7, "x": 220, "y": 530, "label_pos": "bottom", "short_label": "SEAFOAM", "desc": "Sub-zero glacial ice caverns situated in the southern sea.", "type": "DUNGEON"}
        ]
        self.selected_node_idx = 0
        for idx, node in enumerate(self.map_nodes):
            if node["name"] == player.current_map:
                self.selected_node_idx = idx
                break

    def update(self, dt):
        self.timer += dt

    def _navigate_direction(self, dir_name):
        curr_node = self.map_nodes[self.selected_node_idx]
        cgx, cgy = curr_node["gx"], curr_node["gy"]
        best_idx = None
        best_dist = float('inf')

        for idx, other in enumerate(self.map_nodes):
            if idx == self.selected_node_idx:
                continue
            ogx, ogy = other["gx"], other["gy"]
            dx = ogx - cgx
            dy = ogy - cgy

            if dir_name == "UP" and dy < 0:
                dist = abs(dy) * 2.0 + abs(dx) * 3.5
                if dist < best_dist:
                    best_dist = dist
                    best_idx = idx
            elif dir_name == "DOWN" and dy > 0:
                dist = abs(dy) * 2.0 + abs(dx) * 3.5
                if dist < best_dist:
                    best_dist = dist
                    best_idx = idx
            elif dir_name == "LEFT" and dx < 0:
                dist = abs(dx) * 2.0 + abs(dy) * 3.5
                if dist < best_dist:
                    best_dist = dist
                    best_idx = idx
            elif dir_name == "RIGHT" and dx > 0:
                dist = abs(dx) * 2.0 + abs(dy) * 3.5
                if dist < best_dist:
                    best_dist = dist
                    best_idx = idx

        if best_idx is not None:
            self.selected_node_idx = best_idx
            sound_mgr.play_sfx("select")
        else:
            step = -1 if dir_name in ["UP", "LEFT"] else 1
            self.selected_node_idx = (self.selected_node_idx + step) % len(self.map_nodes)
            sound_mgr.play_sfx("select")

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        # Tab switching with Left/Right when on Tab 0, or Tab key anytime
        if event.key in [pygame.K_TAB, pygame.K_q, pygame.K_e]:
            self.active_tab = 1 - self.active_tab
            sound_mgr.play_sfx("select")
            return None

        if self.active_tab == 0:
            if any(event.key == k for k in KEY_RIGHT + KEY_CONFIRM):
                self.active_tab = 1
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                return "BACK"
        elif self.active_tab == 1:
            if any(event.key == k for k in KEY_UP):
                self._navigate_direction("UP")
            elif any(event.key == k for k in KEY_DOWN):
                self._navigate_direction("DOWN")
            elif any(event.key == k for k in KEY_LEFT):
                self._navigate_direction("LEFT")
            elif any(event.key == k for k in KEY_RIGHT):
                self._navigate_direction("RIGHT")
            elif any(event.key == k for k in KEY_CANCEL + KEY_CONFIRM):
                sound_mgr.play_sfx("cancel")
                return "BACK"

        return None

    def draw(self, surf):
        surf.fill((232, 238, 248))

        # 1. Top Header Tabs
        tab_y = 18
        for t_idx, t_name in enumerate(["TRAINER CARD & BADGES", "KANTO REGION MAP"]):
            is_active = (self.active_tab == t_idx)
            tx = 35 + t_idx * 270
            tw = 250
            th = 40
            pygame.draw.rect(surf, (240, 140, 40) if is_active else UI_BORDER_LIGHT, (tx - 2, tab_y - 2, tw + 4, th + 4), border_radius=8)
            pygame.draw.rect(surf, (255, 248, 230) if is_active else WHITE, (tx, tab_y, tw, th), border_radius=6)
            ttxt = gfx.fonts["regular"].render(t_name, True, (220, 80, 0) if is_active else UI_TEXT)
            surf.blit(ttxt, (tx + (tw - ttxt.get_width()) // 2, tab_y + 10))

        # 2. Main Content Card
        cx, cy, cw, ch = 35, 75, SCREEN_WIDTH - 70, SCREEN_HEIGHT - 95
        pygame.draw.rect(surf, UI_BORDER_LIGHT, (cx - 2, cy - 2, cw + 4, ch + 4), border_radius=12)
        pygame.draw.rect(surf, WHITE, (cx, cy, cw, ch), border_radius=10)

        # Tab 0: Trainer Card
        if self.active_tab == 0:
            # Left Sub-Panel: Trainer Profile & Stats
            lx, ly, lw, lh = cx + 18, cy + 18, 320, ch - 36
            pygame.draw.rect(surf, (246, 249, 255), (lx, ly, lw, lh), border_radius=8)
            pygame.draw.rect(surf, UI_BORDER_LIGHT, (lx, ly, lw, lh), 1, border_radius=8)

            head_t = gfx.fonts["large"].render("TRAINER PASSPORT", True, (20, 70, 160))
            surf.blit(head_t, (lx + (lw - head_t.get_width()) // 2, ly + 14))

            # Full-length Trainer Character Portrait
            preview_sprite = gfx.get_trainer_preview_sprite(
                self.player.gender, self.player.outfit_theme, self.player.hat_style, self.player.hair_color, size=(110, 110)
            )
            surf.blit(preview_sprite, (lx + (lw - 110) // 2, ly + 46))

            # Info List
            badge_cnt = len(self.world.badges)
            caught_cnt = len(self.pokedex.caught)
            seen_cnt = len(self.pokedex.seen)
            money_val = self.inventory.money

            stats = [
                ("NAME", self.player.name),
                ("MONEY", f"${money_val}"),
                ("BADGES", f"{badge_cnt} / 8"),
                ("POKÉDEX", f"Seen: {seen_cnt}  Own: {caught_cnt}"),
                ("PLAY TIME", "02:45"),
                ("CURRENT AREA", self.player.current_map)
            ]

            sy = ly + 165
            for lbl, val in stats:
                lbl_t = gfx.fonts["small"].render(lbl, True, UI_TEXT_MUTED)
                val_t = gfx.fonts["regular"].render(val, True, (200, 80, 0) if lbl == "NAME" else UI_TEXT)
                surf.blit(lbl_t, (lx + 20, sy))
                surf.blit(val_t, (lx + 20, sy + 16))
                sy += 40

            # Right Sub-Panel: Official 8 Kanto Badges
            rx, ry, rw, rh = cx + 356, cy + 18, 356, ch - 36
            pygame.draw.rect(surf, (252, 252, 255), (rx, ry, rw, rh), border_radius=8)
            pygame.draw.rect(surf, UI_BORDER_LIGHT, (rx, ry, rw, rh), 1, border_radius=8)

            b_head = gfx.fonts["large"].render("KANTO GYM BADGES", True, (20, 70, 160))
            surf.blit(b_head, (rx + (rw - b_head.get_width()) // 2, ry + 14))

            # 4x2 Badge Grid
            for b_idx, (b_name, b_gym, b_leader) in enumerate(self.kanto_badges):
                col = b_idx % 2
                row = b_idx // 2
                bx = rx + 16 + col * 165
                by = ry + 54 + row * 92
                bw, bh = 155, 82

                is_earned = b_name in self.world.badges
                bdr_c = (240, 180, 40) if is_earned else (220, 225, 235)
                bg_c = (255, 250, 235) if is_earned else (245, 246, 250)

                pygame.draw.rect(surf, bdr_c, (bx, by, bw, bh), border_radius=6)
                pygame.draw.rect(surf, bg_c, (bx + 1, by + 1, bw - 2, bh - 2), border_radius=5)

                gfx.draw_gym_badge(surf, b_name, bx + 8, by + 20, size=40, is_earned=is_earned)

                name_t = gfx.fonts["small"].render(b_name.replace(" Badge", ""), True, (200, 80, 0) if is_earned else UI_TEXT_MUTED)
                gym_t = gfx.fonts["small"].render(b_gym.split()[0], True, UI_TEXT)
                stat_t = gfx.fonts["small"].render("OBTAINED" if is_earned else "LOCKED", True, (40, 160, 60) if is_earned else (160, 165, 175))

                surf.blit(name_t, (bx + 54, by + 12))
                surf.blit(gym_t, (bx + 54, by + 30))
                surf.blit(stat_t, (bx + 54, by + 50))

        # Tab 1: Structured Kanto Region Map & Exploration
        else:
            visited_nodes = [n for n in self.map_nodes if len(self.world.explored_tiles.get(n["name"], set())) > 0]
            v_cnt = len(visited_nodes)
            tot_cnt = len(self.map_nodes)
            v_pct = int(100 * v_cnt / max(1, tot_cnt))

            # Left Panel: Cartographic Kanto Region Map
            lx, ly, lw, lh = cx + 12, cy + 12, 426, ch - 24
            pygame.draw.rect(surf, (246, 250, 255), (lx, ly, lw, lh), border_radius=8)
            pygame.draw.rect(surf, UI_BORDER_LIGHT, (lx, ly, lw, lh), 1, border_radius=8)

            # Discovery Progress Header
            by = ly + 8
            pygame.draw.rect(surf, (238, 244, 255), (lx + 8, by, lw - 16, 36), border_radius=6)
            pygame.draw.rect(surf, (210, 222, 245), (lx + 8, by, lw - 16, 36), 1, border_radius=6)

            p_title = gfx.fonts["small"].render(f"KANTO DISCOVERY: {v_cnt} / {tot_cnt} AREAS ({v_pct}%)", True, (20, 70, 160))
            surf.blit(p_title, (lx + 16, by + 5))

            pb_w = lw - 32
            pb_fill = int(pb_w * (v_cnt / max(1, tot_cnt)))
            pygame.draw.rect(surf, (220, 226, 238), (lx + 16, by + 23, pb_w, 6), border_radius=3)
            pygame.draw.rect(surf, (40, 180, 80), (lx + 16, by + 23, pb_fill, 6), border_radius=3)

            # Map Canvas Area
            map_ox, map_oy = lx + 12, by + 44
            map_w, map_h = lw - 24, lh - 56

            # 1. Cartographic Water & Land Background
            # Ocean Background
            pygame.draw.rect(surf, (190, 225, 245), (map_ox, map_oy, map_w, map_h), border_radius=6)
            
            # Gentle Ocean Wave Details in south & east
            for wave_x, wave_y in [(map_ox + 40, map_oy + 320), (map_ox + 160, map_oy + 340), (map_ox + 320, map_oy + 280), (map_ox + 350, map_oy + 350)]:
                pygame.draw.arc(surf, (165, 210, 235), (wave_x, wave_y, 24, 10), 3.14, 6.28, 2)

            # Main Kanto Landmass
            col_step = (map_w - 44) / 8.0
            row_step = (map_h - 44) / 7.0

            def get_pixel_pos(gx, gy):
                return (map_ox + 22 + int(gx * col_step), map_oy + 22 + int(gy * row_step))

            # Landmass Shapes
            # Western Main Corridor (Viridian to Pewter & Pallet)
            p_west_tl = get_pixel_pos(1.4, 0.4)
            p_west_br = get_pixel_pos(2.6, 5.6)
            pygame.draw.rect(surf, (224, 240, 216), (p_west_tl[0], p_west_tl[1], p_west_br[0] - p_west_tl[0], p_west_br[1] - p_west_tl[1]), border_radius=12)

            # Northern Canyon Corridor (Pewter across Mt Moon to Cerulean & Power Plant)
            p_north_tl = get_pixel_pos(1.4, 0.4)
            p_north_br = get_pixel_pos(8.6, 1.6)
            pygame.draw.rect(surf, (224, 240, 216), (p_north_tl[0], p_north_tl[1], p_north_br[0] - p_north_tl[0], p_north_br[1] - p_north_tl[1]), border_radius=12)

            # Central Metropolis Region (Celadon, Saffron, Lavender, Vermilion)
            p_cent_tl = get_pixel_pos(3.4, 2.4)
            p_cent_br = get_pixel_pos(8.6, 5.6)
            pygame.draw.rect(surf, (224, 240, 216), (p_cent_tl[0], p_cent_tl[1], p_cent_br[0] - p_cent_tl[0], p_cent_br[1] - p_cent_tl[1]), border_radius=14)

            # Northwest Mountain Plateau (Indigo Plateau & Victory Road)
            p_mt_tl = get_pixel_pos(-0.5, -0.4)
            p_mt_br = get_pixel_pos(0.6, 3.6)
            pygame.draw.rect(surf, (222, 212, 196), (p_mt_tl[0], p_mt_tl[1], p_mt_br[0] - p_mt_tl[0], p_mt_br[1] - p_mt_tl[1]), border_radius=10)

            # Fuchsia & Safari Southern Peninsula
            p_fuch_tl = get_pixel_pos(6.4, 6.4)
            p_fuch_br = get_pixel_pos(8.6, 7.6)
            pygame.draw.rect(surf, (224, 240, 216), (p_fuch_tl[0], p_fuch_tl[1], p_fuch_br[0] - p_fuch_tl[0], p_fuch_br[1] - p_fuch_tl[1]), border_radius=10)

            # Cinnabar Island Landmass
            p_cin_tl = get_pixel_pos(1.4, 6.5)
            p_cin_br = get_pixel_pos(2.6, 7.6)
            pygame.draw.rect(surf, (232, 222, 198), (p_cin_tl[0], p_cin_tl[1], p_cin_br[0] - p_cin_tl[0], p_cin_br[1] - p_cin_tl[1]), border_radius=8)

            # Seafoam Glacial Islet
            p_sea_tl = get_pixel_pos(3.6, 6.6)
            p_sea_br = get_pixel_pos(4.4, 7.4)
            pygame.draw.rect(surf, (210, 235, 250), (p_sea_tl[0], p_sea_tl[1], p_sea_br[0] - p_sea_tl[0], p_sea_br[1] - p_sea_tl[1]), border_radius=6)

            # Outer Border for Map Canvas
            pygame.draw.rect(surf, (190, 205, 225), (map_ox, map_oy, map_w, map_h), 1, border_radius=6)

            # 2. Road Network Connections
            # Land Routes (warm sand with brown borders)
            land_routes = [
                # Western Highway
                ((0, 0), (0, 1)), ((0, 1), (0, 3)), ((0, 3), (2, 3)),
                ((2, 1), (2, 2)), ((2, 2), (2, 3)), ((2, 3), (2, 4)), ((2, 4), (2, 5)),
                # Northern Highway
                ((2, 1), (3, 1)), ((3, 1), (4, 1)), ((4, 1), (5, 1)), ((5, 1), (6, 1)),
                ((6, 1), (6, 0)), ((6, 1), (7, 0)), ((6, 1), (7, 1)), ((7, 1), (8, 1)),
                # Central Highway
                ((6, 1), (6, 2)), ((6, 2), (6, 3)), ((6, 3), (6, 4)), ((6, 4), (6, 5)), ((6, 5), (6, 6)),
                # East-West Highway
                ((4, 3), (5, 3)), ((5, 3), (6, 3)), ((6, 3), (7, 3)), ((7, 3), (8, 3)),
                # Eastern Corridor
                ((8, 1), (8, 3)), ((8, 3), (8, 2)), ((6, 5), (7, 5)), ((7, 5), (8, 5)),
                ((8, 3), (8, 4)), ((8, 4), (8, 5)), ((8, 5), (8, 7)), ((7, 7), (8, 7))
            ]

            for (gx1, gy1), (gx2, gy2) in land_routes:
                x1, y1 = get_pixel_pos(gx1, gy1)
                x2, y2 = get_pixel_pos(gx2, gy2)
                pygame.draw.line(surf, (155, 125, 75), (x1, y1), (x2, y2), 7)
                pygame.draw.line(surf, (250, 228, 160), (x1, y1), (x2, y2), 3)

            # Water Routes (Southern Ocean Route 21, Seafoam channel, Safari coast)
            water_routes = [
                ((2, 5), (2, 6)), ((2, 6), (2, 7)), ((2, 7), (4, 7)), ((4, 7), (7, 7))
            ]
            for (gx1, gy1), (gx2, gy2) in water_routes:
                x1, y1 = get_pixel_pos(gx1, gy1)
                x2, y2 = get_pixel_pos(gx2, gy2)
                pygame.draw.line(surf, (130, 185, 225), (x1, y1), (x2, y2), 5)
                pygame.draw.line(surf, (255, 255, 255), (x1, y1), (x2, y2), 2)

            # 3. Draw All Map Nodes & Anchor Labels
            for n_idx, node in enumerate(self.map_nodes):
                nx, ny = get_pixel_pos(node["gx"], node["gy"])
                is_sel = (n_idx == self.selected_node_idx)
                is_player_here = (node["name"] == self.player.current_map)
                is_visited = len(self.world.explored_tiles.get(node["name"], set())) > 0

                # Render node icon by type
                if is_visited:
                    if node["type"] == "CITY":
                        # Red City Badge
                        pygame.draw.rect(surf, (170, 25, 25), (nx - 8, ny - 8, 16, 16), border_radius=4)
                        pygame.draw.rect(surf, (235, 45, 45), (nx - 7, ny - 7, 14, 14), border_radius=3)
                        pygame.draw.rect(surf, WHITE, (nx - 4, ny - 4, 8, 8), border_radius=2)
                        pygame.draw.rect(surf, (220, 40, 40), (nx - 2, ny - 2, 4, 4))
                    elif node["type"] == "TOWN":
                        # Blue Town Badge
                        pygame.draw.rect(surf, (25, 75, 175), (nx - 7, ny - 7, 14, 14), border_radius=3)
                        pygame.draw.rect(surf, (45, 125, 235), (nx - 6, ny - 6, 12, 12), border_radius=2)
                        pygame.draw.rect(surf, WHITE, (nx - 3, ny - 3, 6, 6), border_radius=1)
                    elif node["type"] == "DUNGEON":
                        # Amber Mountain Diamond
                        pygame.draw.polygon(surf, (145, 70, 25), [(nx, ny - 8), (nx + 7, ny + 6), (nx - 7, ny + 6)])
                        pygame.draw.polygon(surf, (215, 115, 45), [(nx, ny - 6), (nx + 5, ny + 4), (nx - 5, ny + 4)])
                        pygame.draw.circle(surf, WHITE, (nx, ny + 1), 2)
                    else:
                        # Green Route Milestone
                        pygame.draw.circle(surf, (35, 115, 50), (nx, ny), 5)
                        pygame.draw.circle(surf, (60, 180, 80), (nx, ny), 4)
                        pygame.draw.circle(surf, WHITE, (nx, ny), 2)
                else:
                    # Unvisited Slate Marker
                    pygame.draw.circle(surf, (110, 120, 135), (nx, ny), 6)
                    pygame.draw.circle(surf, (190, 200, 215), (nx, ny), 4)
                    pygame.draw.circle(surf, (90, 100, 115), (nx, ny), 2)

                # Draw Anchor Label if configured
                short_lbl = node.get("short_label", "")
                lbl_pos = node.get("label_pos", "none")
                if short_lbl and lbl_pos != "none":
                    lbl_col = (30, 40, 60) if is_visited else (120, 130, 145)
                    st = gfx.fonts["small"].render(short_lbl, True, lbl_col)
                    if lbl_pos == "top":
                        lx_p = nx - st.get_width() // 2
                        ly_p = ny - 18
                    elif lbl_pos == "bottom":
                        lx_p = nx - st.get_width() // 2
                        ly_p = ny + 10
                    elif lbl_pos == "left":
                        lx_p = nx - st.get_width() - 11
                        ly_p = ny - 6
                    elif lbl_pos == "right":
                        lx_p = nx + 11
                        ly_p = ny - 6
                    else:
                        lx_p = nx + 10
                        ly_p = ny - 6

                    surf.blit(st, (lx_p, ly_p))

            # 4. Animated Selection Target Reticle & Floating Callout Tooltip
            sel_node = self.map_nodes[self.selected_node_idx]
            snx, sny = get_pixel_pos(sel_node["gx"], sel_node["gy"])
            
            # Pulsing Selection Ring
            pulse = math.sin(self.timer * 6) * 2
            ret_r = int(12 + pulse)
            pygame.draw.circle(surf, (255, 140, 0), (snx, sny), ret_r, 2)
            # Reticle corner brackets
            b_s = 6
            for dx_b, dy_b in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                bx_c = snx + dx_b * (ret_r + 2)
                by_c = sny + dy_b * (ret_r + 2)
                pygame.draw.line(surf, (255, 160, 20), (bx_c, by_c), (bx_c - dx_b * b_s, by_c), 2)
                pygame.draw.line(surf, (255, 160, 20), (bx_c, by_c), (bx_c, by_c - dy_b * b_s), 2)

            # Floating Tooltip Pill for Selected Location
            sel_visited = len(self.world.explored_tiles.get(sel_node["name"], set())) > 0
            callout_title = sel_node["name"] if sel_visited else f"? {sel_node['name']}"
            c_txt = gfx.fonts["regular"].render(callout_title, True, (20, 40, 80))
            badge_txt = gfx.fonts["small"].render(f"[{sel_node['type']}]", True, (220, 100, 20) if sel_visited else (130, 140, 155))
            
            cw_tip = max(c_txt.get_width() + badge_txt.get_width() + 24, 130)
            ch_tip = 32
            # Tooltip placement (keep inside canvas)
            tip_x = snx + 16 if snx + 16 + cw_tip <= map_ox + map_w - 4 else snx - 16 - cw_tip
            tip_y = sny - 16 if sny - 16 >= map_oy + 4 else sny + 16

            pygame.draw.rect(surf, (0, 0, 0, 50), (tip_x + 2, tip_y + 2, cw_tip, ch_tip), border_radius=6)
            pygame.draw.rect(surf, WHITE, (tip_x, tip_y, cw_tip, ch_tip), border_radius=6)
            pygame.draw.rect(surf, (255, 140, 40), (tip_x, tip_y, cw_tip, ch_tip), 2, border_radius=6)
            surf.blit(c_txt, (tip_x + 8, tip_y + 7))
            surf.blit(badge_txt, (tip_x + c_txt.get_width() + 14, tip_y + 9))

            # 5. High-Visibility Player Location Pin ("YOU")
            for node in self.map_nodes:
                if node["name"] == self.player.current_map:
                    pnx, pny = get_pixel_pos(node["gx"], node["gy"])
                    # Pulsing radar ping wave
                    ping_phase = (self.timer * 2.5) % 1.0
                    ping_r = int(6 + ping_phase * 16)
                    pygame.draw.circle(surf, (255, 215, 40), (pnx, pny), ping_r, 1)

                    # Player Pin
                    pygame.draw.circle(surf, (220, 40, 40), (pnx, pny - 12), 6)
                    pygame.draw.circle(surf, (255, 230, 60), (pnx, pny - 12), 4)
                    pygame.draw.polygon(surf, (220, 40, 40), [(pnx - 4, pny - 10), (pnx + 4, pny - 10), (pnx, pny - 3)])
                    
                    if int(self.timer * 3) % 2 == 0:
                        you_t = gfx.fonts["small"].render("YOU", True, (220, 30, 30))
                        surf.blit(you_t, (pnx - you_t.get_width() // 2, pny - 26))
                    break

            # =========================================================================
            # Right Panel: Selected Area Exploration Dossier & Live Minimap
            # =========================================================================
            rx, ry, rw, rh = cx + 450, cy + 12, cw - 462, ch - 24
            pygame.draw.rect(surf, (252, 252, 255), (rx, ry, rw, rh), border_radius=8)
            pygame.draw.rect(surf, UI_BORDER_LIGHT, (rx, ry, rw, rh), 1, border_radius=8)

            node_name = sel_node["name"]
            explored_set = self.world.explored_tiles.get(node_name, set())
            is_visited = len(explored_set) > 0
            grid = self.world.maps.get(node_name, {}).get("grid", [])

            # 1. Location Header & Status Tag
            loc_title = gfx.fonts["medium"].render(node_name, True, (20, 70, 160))
            surf.blit(loc_title, (rx + 12, ry + 10))

            if is_visited:
                if grid:
                    walkable = sum(1 for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] not in ["#", "^", "W", "~"])
                    exp_walkable = sum(1 for (cx_t, cy_t) in explored_set if 0 <= cy_t < len(grid) and 0 <= cx_t < len(grid[0]) and grid[cy_t][cx_t] not in ["#", "^", "W", "~"])
                    pct = min(100, int(100 * exp_walkable / max(1, walkable)))
                else:
                    pct = 100
                status_txt = f"VISITED ({pct}% MAPPED)"
                status_col = (40, 160, 60) if pct >= 100 else (220, 140, 20)
            else:
                status_txt = "UNEXPLORED (0% MAPPED)"
                status_col = (150, 155, 170)

            st_surf = gfx.fonts["small"].render(f"[{sel_node['type']}] - {status_txt}", True, status_col)
            surf.blit(st_surf, (rx + 12, ry + 34))

            # 2. Live Fog-of-War Area Minimap Canvas
            cm_x, cm_y, cm_w, cm_h = rx + 12, ry + 54, rw - 24, 150
            pygame.draw.rect(surf, (14, 16, 24), (cm_x - 1, cm_y - 1, cm_w + 2, cm_h + 2), border_radius=6)

            if is_visited and grid:
                rows = len(grid)
                cols = len(grid[0])
                cell_s = max(2, min(cm_w // cols, cm_h // rows))
                g_w = cols * cell_s
                g_h = rows * cell_s
                gx_start = cm_x + (cm_w - g_w) // 2
                gy_start = cm_y + (cm_h - g_h) // 2

                is_cave = (node_name in ["Mt. Moon", "Seafoam Islands", "Victory Road", "Cerulean Cave", "Diglett's Cave"])
                is_ice = (node_name == "Seafoam Islands")
                is_lavender = (node_name in ["Lavender Town", "Pokémon Tower"])
                is_power_plant = (node_name == "Power Plant")
                is_safari = (node_name == "Safari Zone")
                is_canyon = (node_name in ["Route 9", "Route 3", "Route 4"])
                ground_items = self.world.maps.get(node_name, {}).get("ground_items", [])

                for r in range(rows):
                    for c in range(cols):
                        tx = gx_start + c * cell_s
                        ty = gy_start + r * cell_s
                        char = grid[r][c]
                        if (c, r) not in explored_set:
                            pygame.draw.rect(surf, (20, 24, 34), (tx, ty, cell_s, cell_s))
                            continue

                        # Explored terrain colors
                        if char == "^":
                            col = (40, 95, 145) if is_ice else ((140, 65, 40) if is_canyon else (75, 68, 62))
                        elif char == "#":
                            col = (55, 40, 65) if is_lavender else ((60, 110, 50) if is_safari else (35, 75, 40))
                        elif char in ["W", "R", "B"]:
                            col = (235, 195, 30) if is_power_plant else (110, 60, 60)
                        elif char == "~":
                            col = (60, 130, 220)
                        elif char == "p":
                            col = (190, 125, 80) if is_canyon else (205, 180, 130)
                        elif char == "s":
                            col = (225, 205, 140)
                        elif char == "b":
                            col = (175, 125, 75)
                        elif char == "G":
                            col = (165, 135, 55) if is_safari else (45, 135, 40)
                        elif char == "O":
                            col = (120, 220, 255) if is_ice else (255, 215, 40)
                        elif char == "D":
                            col = (255, 180, 40)
                        elif char == "S":
                            col = (185, 145, 85)
                        elif char in ["_", "C", "N", "M", "P", "H", "K"]:
                            col = (150, 220, 245) if is_ice else ((90, 100, 115) if is_power_plant else ((85, 75, 105) if is_lavender else (195, 175, 140)))
                        elif char in ["J", "Y"]:
                            col = (145, 140, 155) if is_lavender else (175, 145, 120)
                        elif char == "*":
                            col = (220, 70, 70)
                        else:
                            col = (150, 220, 245) if is_ice else ((110, 90, 135) if is_lavender else ((215, 190, 115) if is_safari else ((190, 125, 80) if is_canyon else (85, 160, 75))))

                        pygame.draw.rect(surf, col, (tx, ty, cell_s, cell_s))

                        for g_item in ground_items:
                            if g_item["x"] == c and g_item["y"] == r and g_item["id"] not in self.world.collected_items:
                                pygame.draw.circle(surf, (240, 50, 50), (tx + cell_s // 2, ty + cell_s // 2), max(1, cell_s // 2))

                if self.player.current_map == node_name:
                    px = gx_start + self.player.grid_x * cell_s + cell_s // 2
                    py = gy_start + self.player.grid_y * cell_s + cell_s // 2
                    pygame.draw.circle(surf, (255, 230, 40), (px, py), max(3, cell_s + 1), 1)
                    pygame.draw.circle(surf, (240, 40, 40), (px, py), max(2, cell_s))
            else:
                pygame.draw.circle(surf, (40, 48, 64), (cm_x + cm_w // 2, cm_y + cm_h // 2 - 12), 24)
                q_txt = gfx.fonts["title"].render("?", True, (130, 145, 170))
                surf.blit(q_txt, (cm_x + (cm_w - q_txt.get_width()) // 2, cm_y + cm_h // 2 - 32))
                un_t = gfx.fonts["regular"].render("UNEXPLORED TERRITORY", True, (200, 210, 230))
                un_sub = gfx.fonts["small"].render("Travel to this area to reveal map layout", True, (130, 140, 160))
                surf.blit(un_t, (cm_x + (cm_w - un_t.get_width()) // 2, cm_y + cm_h // 2 + 18))
                surf.blit(un_sub, (cm_x + (cm_w - un_sub.get_width()) // 2, cm_y + cm_h // 2 + 40))

            # 3. Location Description Card (with multi-line word wrap)
            dx, dy, dw, dh = rx + 12, ry + 214, rw - 24, 60
            pygame.draw.rect(surf, (245, 248, 255), (dx, dy, dw, dh), border_radius=6)
            pygame.draw.rect(surf, (215, 225, 240), (dx, dy, dw, dh), 1, border_radius=6)
            
            # Word-wrap description lines
            words = sel_node["desc"].split(" ")
            d_lines = []
            cur_line = []
            for w in words:
                test_line = " ".join(cur_line + [w])
                if gfx.fonts["small"].size(test_line)[0] < dw - 16:
                    cur_line.append(w)
                else:
                    d_lines.append(" ".join(cur_line))
                    cur_line = [w]
            if cur_line:
                d_lines.append(" ".join(cur_line))

            for l_i, line_str in enumerate(d_lines[:3]):
                dl_surf = gfx.fonts["small"].render(line_str, True, UI_TEXT)
                surf.blit(dl_surf, (dx + 8, dy + 8 + l_i * 17))

            # 4. Known Wild Pokémon Habitats
            hx, hy, hw, hh = rx + 12, ry + 282, rw - 24, 150
            pygame.draw.rect(surf, (245, 248, 255), (hx, hy, hw, hh), border_radius=6)
            pygame.draw.rect(surf, (215, 225, 240), (hx, hy, hw, hh), 1, border_radius=6)

            h_head = gfx.fonts["small"].render("WILD POKÉMON HABITATS:", True, (20, 70, 160))
            surf.blit(h_head, (hx + 8, hy + 8))

            if is_visited:
                all_encs = []
                seen_species = set()
                for enc in WILD_ENCOUNTERS.get(node_name, []) + WILD_WATER_ENCOUNTERS.get(node_name, []):
                    if enc["species"] not in seen_species:
                        seen_species.add(enc["species"])
                        all_encs.append(enc["species"])

                if all_encs:
                    for i, sp in enumerate(all_encs[:8]):
                        col_idx = i % 2
                        row_idx = i // 2
                        cx_p = hx + 10 + col_idx * 115
                        cy_p = hy + 28 + row_idx * 28

                        is_caught = sp in self.pokedex.caught
                        is_seen = sp in self.pokedex.seen
                        tag_bg = (230, 250, 235) if is_caught else ((255, 248, 230) if is_seen else (235, 238, 245))
                        tag_bdr = (70, 180, 90) if is_caught else ((240, 170, 40) if is_seen else (200, 205, 220))
                        tag_txt_c = (20, 120, 40) if is_caught else ((180, 100, 10) if is_seen else (100, 110, 125))

                        pygame.draw.rect(surf, tag_bg, (cx_p, cy_p, 110, 24), border_radius=4)
                        pygame.draw.rect(surf, tag_bdr, (cx_p, cy_p, 110, 24), 1, border_radius=4)

                        status_mark = "✔ " if is_caught else ("? " if is_seen else "• ")
                        sp_txt = gfx.fonts["small"].render(f"{status_mark}{sp}", True, tag_txt_c)
                        surf.blit(sp_txt, (cx_p + 6, cy_p + 4))
                else:
                    safe_msg = "Peaceful Settlement. Pokémon Center & PokéMart available." if sel_node["type"] in ["CITY", "TOWN"] else "No wild Pokémon roaming this area."
                    no_w = gfx.fonts["small"].render(safe_msg, True, UI_TEXT_MUTED)
                    surf.blit(no_w, (hx + 10, hy + 35))
            else:
                un_enc = gfx.fonts["small"].render("Fauna Unknown. Explore area to record wild habitats.", True, UI_TEXT_MUTED)
                surf.blit(un_enc, (hx + 10, hy + 35))

        # Bottom Controls Hint
        hint = gfx.fonts["small"].render("D-Pad / Arrows: Move Cursor  |  [Tab]: Switch Tab  |  [X / Enter]: Return", True, UI_TEXT_MUTED)
        surf.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 565))

class QuestLogScreen:
    """
    Comprehensive Quest Log Screen with Active Missions and Completed Archive tabs,
    real-time progress tracking, quest giver info, location, backstory, and rewards showcase.
    """
    def __init__(self, quest_mgr, player):
        self.quest_mgr = quest_mgr
        self.player = player
        self.active_tab = 0 # 0: ACTIVE, 1: COMPLETED
        self.selected_idx = 0
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt

    def get_current_list(self):
        from quest_system import QUEST_DEFINITIONS
        if self.active_tab == 0:
            q_ids = list(self.quest_mgr.active_quests.keys())
            return [QUEST_DEFINITIONS[qid] for qid in q_ids if qid in QUEST_DEFINITIONS]
        else:
            q_ids = list(self.quest_mgr.completed_quests.keys())
            return [QUEST_DEFINITIONS[qid] for qid in q_ids if qid in QUEST_DEFINITIONS]

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        curr_list = self.get_current_list()
        if any(event.key == k for k in KEY_LEFT + KEY_RIGHT):
            self.active_tab = 1 - self.active_tab
            self.selected_idx = 0
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_UP):
            if curr_list:
                self.selected_idx = (self.selected_idx - 1) % len(curr_list)
                sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_DOWN):
            if curr_list:
                self.selected_idx = (self.selected_idx + 1) % len(curr_list)
                sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_CANCEL + KEY_MENU):
            sound_mgr.play_sfx("cancel")
            return "CLOSE"
        elif any(event.key == k for k in KEY_CONFIRM):
            sound_mgr.play_sfx("select")

        return None

    def draw(self, surf):
        surf.fill(UI_BG)

        # Header Bar
        pygame.draw.rect(surf, (230, 235, 245), (0, 0, SCREEN_WIDTH, 56))
        pygame.draw.line(surf, UI_BORDER_LIGHT, (0, 56), (SCREEN_WIDTH, 56), 2)

        title_txt = gfx.fonts["title"].render("KANTO QUEST LOG & MISSIONS", True, (200, 80, 0))
        surf.blit(title_txt, (28, 14))

        # Tab Buttons
        active_cnt = len(self.quest_mgr.active_quests)
        completed_cnt = len(self.quest_mgr.completed_quests)
        tabs = [f"ACTIVE MISSIONS ({active_cnt})", f"COMPLETED ARCHIVE ({completed_cnt})"]

        for i, t_label in enumerate(tabs):
            tx = 420 + i * 180
            ty = 12
            tw, th = 170, 36
            is_tab_sel = (i == self.active_tab)

            t_bg = (255, 245, 220) if is_tab_sel else (240, 242, 248)
            t_bdr = (240, 140, 40) if is_tab_sel else UI_BORDER_LIGHT
            t_txt_c = (200, 80, 0) if is_tab_sel else UI_TEXT_MUTED

            pygame.draw.rect(surf, t_bdr, (tx, ty, tw, th), border_radius=6)
            pygame.draw.rect(surf, t_bg, (tx + 1, ty + 1, tw - 2, th - 2), border_radius=5)
            ttxt = gfx.fonts["small"].render(t_label, True, t_txt_c)
            surf.blit(ttxt, (tx + (tw - ttxt.get_width()) // 2, ty + 10))

        curr_list = self.get_current_list()
        if self.selected_idx >= len(curr_list) and curr_list:
            self.selected_idx = 0

        # Main Layout Container
        cx, cy, cw, ch = 20, 68, SCREEN_WIDTH - 40, 490
        pygame.draw.rect(surf, WHITE, (cx, cy, cw, ch), border_radius=10)
        pygame.draw.rect(surf, UI_BORDER_LIGHT, (cx, cy, cw, ch), 2, border_radius=10)

        # Left Panel: Quest List (width: 320)
        lx, ly, lw, lh = cx + 10, cy + 10, 320, ch - 20
        pygame.draw.rect(surf, (248, 250, 255), (lx, ly, lw, lh), border_radius=8)
        pygame.draw.rect(surf, UI_BORDER_LIGHT, (lx, ly, lw, lh), 1, border_radius=8)

        if not curr_list:
            if self.active_tab == 0:
                empty_t1 = gfx.fonts["regular"].render("No Active Quests", True, UI_TEXT)
                empty_t2 = gfx.fonts["small"].render("Explore Kanto towns & routes", True, UI_TEXT_MUTED)
                empty_t3 = gfx.fonts["small"].render("to meet NPCs offering quests!", True, UI_TEXT_MUTED)
                empty_t4 = gfx.fonts["small"].render("(Look for gold [!] markers!)", True, (220, 140, 20))
                surf.blit(empty_t1, (lx + 20, ly + 60))
                surf.blit(empty_t2, (lx + 20, ly + 95))
                surf.blit(empty_t3, (lx + 20, ly + 115))
                surf.blit(empty_t4, (lx + 20, ly + 145))
            else:
                empty_t1 = gfx.fonts["regular"].render("No Completed Quests", True, UI_TEXT)
                empty_t2 = gfx.fonts["small"].render("Completed quests will be archived", True, UI_TEXT_MUTED)
                empty_t3 = gfx.fonts["small"].render("here with reward records.", True, UI_TEXT_MUTED)
                surf.blit(empty_t1, (lx + 20, ly + 60))
                surf.blit(empty_t2, (lx + 20, ly + 95))
                surf.blit(empty_t3, (lx + 20, ly + 115))
        else:
            for idx, q_data in enumerate(curr_list):
                qy = ly + 8 + idx * 72
                is_sel = (idx == self.selected_idx)
                q_id = q_data["id"]
                curr_prog = self.quest_mgr.get_progress(q_id)
                target_cnt = q_data.get("target_count", 1)

                q_bg = (255, 242, 215) if is_sel else ((235, 250, 235) if self.active_tab == 1 else WHITE)
                q_bdr = (240, 140, 40) if is_sel else ((70, 180, 90) if self.active_tab == 1 else UI_BORDER_LIGHT)

                pygame.draw.rect(surf, q_bdr, (lx + 6, qy, lw - 12, 64), border_radius=6)
                pygame.draw.rect(surf, q_bg, (lx + 7, qy + 1, lw - 14, 62), border_radius=5)

                # Category Badge
                obj_t = q_data.get("objective_type", "QUEST")
                cat_tag = "CATCH" if "CATCH" in obj_t else ("DEFEAT" if "DEFEAT" in obj_t else ("EVOLVE" if "STONE" in obj_t else "SPECIAL"))
                cat_c = (20, 100, 220) if cat_tag == "CATCH" else ((220, 60, 40) if cat_tag == "DEFEAT" else ((160, 60, 200) if cat_tag == "EVOLVE" else (40, 160, 60)))
                pygame.draw.rect(surf, cat_c, (lx + 12, qy + 8, 48, 16), border_radius=3)
                cat_txt = gfx.fonts["small"].render(cat_tag, True, WHITE)
                surf.blit(cat_txt, (lx + 15, qy + 9))

                # Title
                q_title = gfx.fonts["small"].render(q_data["title"][:22], True, (200, 80, 0) if is_sel else UI_TEXT)
                surf.blit(q_title, (lx + 66, qy + 8))

                # Giver Info
                g_txt = gfx.fonts["small"].render(f"{q_data['giver_name']}", True, UI_TEXT_MUTED)
                surf.blit(g_txt, (lx + 12, qy + 27))

                # Progress Bar / Status
                if self.active_tab == 0:
                    prog_str = f"[{curr_prog}/{target_cnt}]"
                    prog_txt = gfx.fonts["small"].render(prog_str, True, (40, 140, 60) if curr_prog >= target_cnt else (200, 80, 0))
                    surf.blit(prog_txt, (lx + lw - 18 - prog_txt.get_width(), qy + 44))

                    # Mini progress bar
                    pb_w = lw - 80
                    pb_fill = int(pb_w * min(1.0, curr_prog / max(1, target_cnt)))
                    pygame.draw.rect(surf, (220, 226, 238), (lx + 12, qy + 48, pb_w, 6), border_radius=3)
                    pygame.draw.rect(surf, (40, 180, 80), (lx + 12, qy + 48, pb_fill, 6), border_radius=3)
                else:
                    done_txt = gfx.fonts["small"].render("✓ COMPLETED", True, (40, 160, 60))
                    surf.blit(done_txt, (lx + 12, qy + 44))

        # Right Panel: Selected Quest Details Briefing (width: 400)
        rx, ry, rw, rh = cx + 340, cy + 10, cw - 350, ch - 20
        pygame.draw.rect(surf, (252, 253, 255), (rx, ry, rw, rh), border_radius=8)
        pygame.draw.rect(surf, UI_BORDER_LIGHT, (rx, ry, rw, rh), 1, border_radius=8)

        if curr_list and self.selected_idx < len(curr_list):
            sel_q = curr_list[self.selected_idx]
            q_id = sel_q["id"]
            curr_prog = self.quest_mgr.get_progress(q_id)
            target_cnt = sel_q.get("target_count", 1)

            # Details Header Banner
            pygame.draw.rect(surf, (255, 240, 210), (rx + 8, ry + 8, rw - 16, 52), border_radius=6)
            pygame.draw.rect(surf, (240, 180, 80), (rx + 8, ry + 8, rw - 16, 52), 1, border_radius=6)

            d_title = gfx.fonts["regular"].render(sel_q["title"], True, (200, 80, 0))
            surf.blit(d_title, (rx + 16, ry + 12))

            loc_txt = gfx.fonts["small"].render(f"📍 {sel_q['location']}  |  👤 Giver: {sel_q['giver_name']}", True, (120, 80, 20))
            surf.blit(loc_txt, (rx + 16, ry + 36))

            # Story Briefing Box
            by = ry + 68
            pygame.draw.rect(surf, WHITE, (rx + 8, by, rw - 16, 85), border_radius=6)
            pygame.draw.rect(surf, UI_BORDER_LIGHT, (rx + 8, by, rw - 16, 85), 1, border_radius=6)

            b_head = gfx.fonts["small"].render("MISSION BRIEFING", True, (20, 70, 160))
            surf.blit(b_head, (rx + 16, by + 6))

            # Multi-line word wrap for description
            words = sel_q["description"].split()
            lines = []
            curr_line = ""
            for w in words:
                test_l = (curr_line + " " + w).strip()
                if gfx.fonts["small"].size(test_l)[0] < rw - 44:
                    curr_line = test_l
                else:
                    lines.append(curr_line)
                    curr_line = w
            if curr_line:
                lines.append(curr_line)

            for li, line in enumerate(lines[:3]):
                d_line = gfx.fonts["small"].render(line, True, UI_TEXT)
                surf.blit(d_line, (rx + 16, by + 26 + li * 18))

            # Objective & Progress Card
            oy = by + 93
            pygame.draw.rect(surf, (245, 248, 255), (rx + 8, oy, rw - 16, 88), border_radius=6)
            pygame.draw.rect(surf, (210, 225, 250), (rx + 8, oy, rw - 16, 88), 1, border_radius=6)

            o_head = gfx.fonts["small"].render("OBJECTIVE STATUS", True, (20, 70, 160))
            surf.blit(o_head, (rx + 16, oy + 8))

            pct = int(100 * min(1.0, curr_prog / max(1, target_cnt)))
            status_text = f"COMPLETED (100%)" if self.active_tab == 1 or curr_prog >= target_cnt else f"IN PROGRESS: {curr_prog} / {target_cnt} ({pct}%)"
            st_col = (40, 160, 60) if self.active_tab == 1 or curr_prog >= target_cnt else (200, 80, 0)
            st_rend = gfx.fonts["regular"].render(status_text, True, st_col)
            surf.blit(st_rend, (rx + 16, oy + 28))

            # Big Progress Bar
            big_pb_w = rw - 36
            big_pb_fill = int(big_pb_w * min(1.0, curr_prog / max(1, target_cnt)))
            pygame.draw.rect(surf, (220, 226, 238), (rx + 16, oy + 58, big_pb_w, 14), border_radius=7)
            pygame.draw.rect(surf, (40, 180, 80), (rx + 16, oy + 58, big_pb_fill, 14), border_radius=7)

            # Rewards Showcase Box
            wy = oy + 96
            pygame.draw.rect(surf, (255, 252, 240), (rx + 8, wy, rw - 16, 110), border_radius=6)
            pygame.draw.rect(surf, (245, 220, 150), (rx + 8, wy, rw - 16, 110), 1, border_radius=6)

            r_head = gfx.fonts["small"].render("REWARDS REPERTORY", True, (200, 80, 0))
            surf.blit(r_head, (rx + 16, wy + 8))

            rewards = sel_q.get("rewards", {})
            money = rewards.get("money", 0)
            m_txt = gfx.fonts["regular"].render(f"+${money} Coins", True, (220, 140, 20))
            surf.blit(m_txt, (rx + 16, wy + 28))

            for ii, (it_name, it_cnt) in enumerate(rewards.get("items", [])):
                ix_p = rx + 16 + ii * 180
                iy_p = wy + 58
                pygame.draw.rect(surf, WHITE, (ix_p, iy_p, 170, 36), border_radius=4)
                pygame.draw.rect(surf, (230, 200, 140), (ix_p, iy_p, 170, 36), 1, border_radius=4)
                
                # Draw item sprite
                spr = gfx.get_item_sprite(it_name, (28, 28))
                surf.blit(spr, (ix_p + 4, iy_p + 4))
                it_t = gfx.fonts["small"].render(f"{it_cnt}x {it_name}", True, UI_TEXT)
                surf.blit(it_t, (ix_p + 36, iy_p + 10))

            # Auto-completion footer notice
            fy = wy + 118
            auto_t = gfx.fonts["small"].render("⭐ Instant Auto-Completion: Rewards are delivered straight to your Bag!", True, (40, 140, 60))
            surf.blit(auto_t, (rx + 10, fy))

        # Bottom Controls Hint
        hint = gfx.fonts["small"].render("Left/Right: Switch Tab  |  Up/Down: Select Quest  |  [X / Enter]: Return", True, UI_TEXT_MUTED)
        surf.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 565))
