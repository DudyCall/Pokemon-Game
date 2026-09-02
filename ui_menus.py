"""
ui_menus.py - Menus: Title Screen, Save Dialogs, Pause Menu, Trainer Customization, and Shop.
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
from pokemon_data import POKEMON_SPECIES, ITEMS, MOVES, WILD_ENCOUNTERS, WILD_WATER_ENCOUNTERS
from save_system import NUM_SAVE_SLOTS

class TitleScreen:
    """
    Polished Pokémon Title Screen with interactive save slot carousel preview,
    authentic multi-layer branding, dynamic ambient background, and vector UI chevrons.
    """
    def __init__(self):
        self.timer = 0.0
        self.starter_index = 0
        self.starters = ["Charmander", "Squirtle", "Bulbasaur", "Pikachu"]
        self.menu_options = ["CONTINUE", "ALL_SLOTS", "NEW_GAME"]
        self.selected_idx = 0
        self.slot_preview_idx = 0
        self.slots = []
        self.has_save = False
        
        # Interactive pulse effects for slot switching
        self.arrow_pulse_left = 0.0
        self.arrow_pulse_right = 0.0
        
        # Pre-render background gradient for fast, smooth 60fps rendering
        self.bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._init_background_gradient()

        # Stylized Pokéball watermark
        self.pokeball_watermark = pygame.Surface((340, 340), pygame.SRCALPHA)
        self._init_watermark()

        # Ambient floating luminous motes
        self.particles = [
            {
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(0, SCREEN_HEIGHT),
                "speed": random.uniform(14, 32),
                "size": random.uniform(1.5, 3.5),
                "alpha": random.randint(30, 110),
                "phase": random.uniform(0, 6.28)
            }
            for _ in range(22)
        ]

        self.refresh_save_status()

    def _init_background_gradient(self):
        """Creates a modern deep midnight sapphire gradient background."""
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            if ratio < 0.5:
                sub_r = ratio / 0.5
                r = int(14 + 10 * sub_r)
                g = int(20 + 14 * sub_r)
                b = int(44 + 28 * sub_r)
            else:
                sub_r = (ratio - 0.5) / 0.5
                r = int(24 - 12 * sub_r)
                g = int(34 - 18 * sub_r)
                b = int(72 - 38 * sub_r)
            pygame.draw.line(self.bg_surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def _init_watermark(self):
        """Pre-renders an authentic stylized Pokéball watermark."""
        cx, cy, r = 170, 170, 145
        # Top hemisphere tint
        pygame.draw.arc(self.pokeball_watermark, (235, 75, 75, 20), (cx - r, cy - r, r * 2, r * 2), 0, math.pi, 8)
        # Bottom hemisphere tint
        pygame.draw.arc(self.pokeball_watermark, (255, 255, 255, 16), (cx - r, cy - r, r * 2, r * 2), math.pi, math.pi * 2, 8)
        # Horizontal middle seam
        pygame.draw.line(self.pokeball_watermark, (255, 255, 255, 20), (cx - r, cy), (cx + r, cy), 8)
        # Center button
        pygame.draw.circle(self.pokeball_watermark, (255, 255, 255, 24), (cx, cy), 40, 8)
        pygame.draw.circle(self.pokeball_watermark, (255, 255, 255, 16), (cx, cy), 20)

    def refresh_save_status(self):
        from save_system import SaveSystem
        self.slots = SaveSystem.get_all_slots_summary()
        self.has_save = any(s.get("exists") for s in self.slots)
        
        # Pick first active slot by default
        for i, s in enumerate(self.slots):
            if s.get("exists"):
                self.slot_preview_idx = i
                break

        if not self.has_save:
            self.menu_options = ["NEW_GAME"]
            self.selected_idx = 0
        else:
            self.menu_options = ["CONTINUE", "ALL_SLOTS", "NEW_GAME"]

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if self.has_save:
            if any(event.key == k for k in KEY_UP):
                self.selected_idx = (self.selected_idx - 1) % len(self.menu_options)
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.selected_idx = (self.selected_idx + 1) % len(self.menu_options)
                sound_mgr.play_sfx("select")
            elif self.selected_idx == 0: # On CONTINUE slot preview
                if any(event.key == k for k in KEY_LEFT):
                    self.slot_preview_idx = (self.slot_preview_idx - 1) % len(self.slots)
                    self.arrow_pulse_left = 0.28
                    sound_mgr.play_sfx("select")
                elif any(event.key == k for k in KEY_RIGHT):
                    self.slot_preview_idx = (self.slot_preview_idx + 1) % len(self.slots)
                    self.arrow_pulse_right = 0.28
                    sound_mgr.play_sfx("select")

        if any(event.key == k for k in KEY_CONFIRM):
            sound_mgr.play_sfx("confirm")
            chosen_opt = self.menu_options[self.selected_idx]
            chosen_slot_num = self.slot_preview_idx + 1
            curr_slot_data = self.slots[self.slot_preview_idx]

            if chosen_opt == "CONTINUE":
                if curr_slot_data.get("exists"):
                    return ("LOAD_SLOT", chosen_slot_num)
                else:
                    return ("NEW_GAME", chosen_slot_num)
            elif chosen_opt == "ALL_SLOTS":
                return ("SELECT_SLOT", chosen_slot_num)
            elif chosen_opt == "NEW_GAME":
                return ("NEW_GAME", chosen_slot_num)

        return None

    def update(self, dt):
        self.timer += dt
        self.starter_index = int(self.timer / 2.0) % len(self.starters)
        if self.arrow_pulse_left > 0:
            self.arrow_pulse_left = max(0.0, self.arrow_pulse_left - dt)
        if self.arrow_pulse_right > 0:
            self.arrow_pulse_right = max(0.0, self.arrow_pulse_right - dt)

        # Update ambient drifting particles
        for p in self.particles:
            p["y"] -= p["speed"] * dt
            if p["y"] < -10:
                p["y"] = SCREEN_HEIGHT + 10
                p["x"] = random.uniform(0, SCREEN_WIDTH)

    def draw(self, surf):
        # 1. Background Gradient
        surf.blit(self.bg_surface, (0, 0))

        # 2. Pokéball Watermark
        surf.blit(self.pokeball_watermark, (SCREEN_WIDTH // 2 - 170 + 80, 110))

        # 3. Ambient Drifting Motes
        for p in self.particles:
            sway = math.sin(self.timer * 1.5 + p["phase"]) * 10
            px = int(p["x"] + sway)
            py = int(p["y"])
            alpha = int(p["alpha"] * (0.7 + 0.3 * math.sin(self.timer * 2.0 + p["phase"])))
            sp_surf = pygame.Surface((int(p["size"] * 2 + 2), int(p["size"] * 2 + 2)), pygame.SRCALPHA)
            pygame.draw.circle(sp_surf, (200, 225, 255, alpha), (sp_surf.get_width() // 2, sp_surf.get_height() // 2), int(p["size"]))
            surf.blit(sp_surf, (px, py))

        # 4. Multi-Layer Pokémon Title Logo
        title_bob = int(math.sin(self.timer * 1.8) * 3)
        title_y = 36 + title_bob
        self._draw_pokemon_logo(surf, SCREEN_WIDTH // 2, title_y)

        # 5. Main Interactive Content
        if self.has_save:
            self._draw_main_menu(surf)
        else:
            self._draw_starter_showcase(surf)

        # 6. Console Keycap Controls Bar
        self._draw_controls_bar(surf)

    def _draw_pokemon_logo(self, surf, center_x, title_y):
        """Renders Pokémon logo with blue outline, drop shadow, gold face, and banner badge."""
        logo_font = gfx.fonts["title"]
        title_str = "POKÉMON"

        # Drop shadow
        shd_surf = logo_font.render(title_str, True, (12, 16, 28))
        surf.blit(shd_surf, (center_x - shd_surf.get_width() // 2 + 3, title_y + 5))

        # Thick 8-direction blue outline (Iconic Pokémon blue)
        outline_col = (38, 70, 160)
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (-3, 0), (3, 0), (0, -3), (0, 3)]:
            out_surf = logo_font.render(title_str, True, outline_col)
            surf.blit(out_surf, (center_x - out_surf.get_width() // 2 + dx, title_y + dy))

        # Core Pikachu gold face
        gold_surf = logo_font.render(title_str, True, (255, 218, 24))
        surf.blit(gold_surf, (center_x - gold_surf.get_width() // 2, title_y))

        # Subtitle Pill Badge: ★ PYGAME EDITION ★
        sub_str = "★  PYGAME EDITION  ★"
        sub_font = gfx.fonts["regular"]
        sub_txt = sub_font.render(sub_str, True, (255, 245, 220))

        badge_w = sub_txt.get_width() + 32
        badge_h = 24
        badge_x = center_x - badge_w // 2
        badge_y = title_y + 46

        pygame.draw.rect(surf, (15, 18, 30), (badge_x - 1, badge_y - 1, badge_w + 2, badge_h + 2), border_radius=12)
        pygame.draw.rect(surf, (170, 24, 38), (badge_x, badge_y, badge_w, badge_h), border_radius=11)
        pygame.draw.rect(surf, (255, 200, 50), (badge_x, badge_y, badge_w, badge_h), 1, border_radius=11)
        surf.blit(sub_txt, (badge_x + (badge_w - sub_txt.get_width()) // 2, badge_y + (badge_h - sub_txt.get_height()) // 2))

    def _draw_main_menu(self, surf):
        cw = 540
        ch = 146
        cx = (SCREEN_WIDTH - cw) // 2
        cy = 158

        cur_slot = self.slots[self.slot_preview_idx]
        cur_num = self.slot_preview_idx + 1
        is_sel_cont = (self.selected_idx == 0)

        # -------------------------------------------------------------
        # 1. CONTINUE GAME (Interactive Slot Carousel Card)
        # -------------------------------------------------------------
        if is_sel_cont:
            glow_surf = pygame.Surface((cw + 12, ch + 12), pygame.SRCALPHA)
            pulse_a = int(55 + 25 * math.sin(self.timer * 4.0))
            pygame.draw.rect(glow_surf, (255, 175, 45, pulse_a), (0, 0, cw + 12, ch + 12), border_radius=14)
            surf.blit(glow_surf, (cx - 6, cy - 6))

        border_col = (245, 140, 25) if is_sel_cont else (65, 85, 120)
        bg_col = (255, 252, 246) if is_sel_cont else (22, 32, 52)
        pygame.draw.rect(surf, border_col, (cx - 2, cy - 2, cw + 4, ch + 4), border_radius=12)
        pygame.draw.rect(surf, bg_col, (cx, cy, cw, ch), border_radius=10)

        if is_sel_cont:
            pygame.draw.rect(surf, (240, 110, 20), (cx + 4, cy + 8, 4, ch - 16), border_radius=2)

        # Header Title
        header_text = "CONTINUE GAME" if cur_slot.get("exists") else "EMPTY SAVE SLOT"
        header_col = (220, 75, 10) if is_sel_cont else (240, 244, 255)
        lbl_head = gfx.fonts["large"].render(header_text, True, header_col)
        surf.blit(lbl_head, (cx + 18, cy + 12))

        # Slot Navigation Widget: [ < ]  SLOT 04 / 99  [ > ]
        self._draw_slot_carousel_header(surf, cx + cw - 195, cy + 12, cur_num, is_sel_cont)

        # Card Details
        if cur_slot.get("exists"):
            lead_species = cur_slot.get("lead_species", "Pikachu")
            lead_level = cur_slot.get("lead_level", 5)
            lead_name = cur_slot.get("lead_name", lead_species)
            trainer_name = cur_slot.get("trainer_name", "Red")
            gender = cur_slot.get("gender", "Boy")
            map_name = cur_slot.get("map", "Pallet Town")
            party_count = cur_slot.get("party_count", 1)
            money = cur_slot.get("money", 0)
            caught_count = cur_slot.get("caught_count", 0)
            timestamp = cur_slot.get("timestamp", "")

            # Pokémon Showcase Pedestal
            ped_x, ped_y, ped_w, ped_h = cx + 18, cy + 44, 82, 92
            ped_bg = (242, 246, 252) if is_sel_cont else (28, 40, 64)
            ped_bdr = (210, 222, 240) if is_sel_cont else (55, 75, 105)
            pygame.draw.rect(surf, ped_bdr, (ped_x - 1, ped_y - 1, ped_w + 2, ped_h + 2), border_radius=8)
            pygame.draw.rect(surf, ped_bg, (ped_x, ped_y, ped_w, ped_h), border_radius=7)

            sp = gfx.get_pokemon_sprite(lead_species, is_back=False, size=(68, 68))
            bob = int(math.sin(self.timer * 3.5) * 2.5) if is_sel_cont else 0
            surf.blit(sp, (ped_x + (ped_w - 68) // 2, ped_y + 4 + bob))

            lvl_txt = gfx.fonts["small"].render(f"Lv.{lead_level}", True, WHITE)
            lvl_bw = max(44, lvl_txt.get_width() + 10)
            lvl_bx = ped_x + (ped_w - lvl_bw) // 2
            lvl_by = ped_y + ped_h - 20
            pygame.draw.rect(surf, (35, 45, 65), (lvl_bx, lvl_by, lvl_bw, 16), border_radius=4)
            surf.blit(lvl_txt, (lvl_bx + (lvl_bw - lvl_txt.get_width()) // 2, lvl_by + 1))

            text_dark = (20, 26, 38) if is_sel_cont else (235, 242, 255)
            text_sub = (90, 105, 130) if is_sel_cont else (160, 175, 205)

            # Line 1: Trainer & Map Location
            gen_col = (50, 120, 240) if gender == "Boy" else (240, 80, 140)
            t_str = f"Trainer: {trainer_name} "
            t_surf = gfx.fonts["regular"].render(t_str, True, text_dark)
            surf.blit(t_surf, (cx + 114, cy + 46))

            g_surf = gfx.fonts["small"].render(f"({gender})", True, gen_col)
            surf.blit(g_surf, (cx + 114 + t_surf.get_width(), cy + 48))

            map_str = f"  |  📍 {map_name}"
            map_surf = gfx.fonts["regular"].render(map_str, True, (40, 140, 70) if is_sel_cont else (90, 210, 130))
            surf.blit(map_surf, (cx + 114 + t_surf.get_width() + g_surf.get_width(), cy + 46))

            # Line 2: Lead Pokémon & Type Badge
            lead_lbl = gfx.fonts["regular"].render(f"Lead: {lead_name}", True, (20, 90, 210) if is_sel_cont else (100, 180, 255))
            surf.blit(lead_lbl, (cx + 114, cy + 74))

            sp_data = POKEMON_SPECIES.get(lead_species, {})
            p_types = sp_data.get("types", ["Normal"])
            if p_types:
                gfx.draw_type_badge(surf, p_types[0], cx + 120 + lead_lbl.get_width(), cy + 73, width=54, height=18)

            # Line 3: Stat Badges Row
            stat_y = cy + 104
            self._draw_mini_stat_badge(surf, cx + 114, stat_y, f"Team: {party_count}/6", is_sel_cont)
            self._draw_mini_stat_badge(surf, cx + 206, stat_y, f"${money:,}", is_sel_cont, text_color=(35, 140, 50) if is_sel_cont else (80, 210, 110))
            self._draw_mini_stat_badge(surf, cx + 294, stat_y, f"Dex: {caught_count}/151", is_sel_cont)

            if timestamp:
                ts_txt = gfx.fonts["small"].render(timestamp, True, text_sub)
                surf.blit(ts_txt, (cx + cw - ts_txt.get_width() - 14, stat_y + 2))

        else:
            emp_col = (130, 145, 165) if is_sel_cont else (140, 155, 185)
            emp_title = gfx.fonts["medium"].render(f"Save Slot {cur_num:02d} is Empty", True, (80, 100, 130) if is_sel_cont else (180, 195, 220))
            emp_sub = gfx.fonts["regular"].render("Press [Enter] or [Z] to begin a new journey in this slot", True, emp_col)
            surf.blit(emp_title, (cx + (cw - emp_title.get_width()) // 2, cy + 54))
            surf.blit(emp_sub, (cx + (cw - emp_sub.get_width()) // 2, cy + 86))

        # -------------------------------------------------------------
        # 2. ALL SAVE SLOTS Button
        # -------------------------------------------------------------
        btn_y1 = cy + ch + 14
        self._draw_action_button(surf, cx, btn_y1, cw, 46, "📂  VIEW ALL 99 SAVE SLOTS", is_selected=(self.selected_idx == 1))

        # -------------------------------------------------------------
        # 3. NEW GAME Button
        # -------------------------------------------------------------
        btn_y2 = btn_y1 + 46 + 10
        self._draw_action_button(surf, cx, btn_y2, cw, 46, "✨  START NEW ADVENTURE", is_selected=(self.selected_idx == 2))

    def _draw_slot_carousel_header(self, surf, x, y, cur_num, is_sel_cont):
        """Renders crisp vector chevrons and slot counter badge: [ < ]  SLOT 04 / 99  [ > ]"""
        box_bg = (240, 245, 252) if is_sel_cont else (28, 38, 58)
        box_bdr = (210, 222, 240) if is_sel_cont else (55, 75, 105)

        bw, bh = 185, 26
        pygame.draw.rect(surf, box_bdr, (x, y, bw, bh), border_radius=6)
        pygame.draw.rect(surf, box_bg, (x + 1, y + 1, bw - 2, bh - 2), border_radius=5)

        # Left Vector Chevron Button
        l_btn_x = x + 4
        l_active = (self.arrow_pulse_left > 0)
        l_col = (255, 120, 20) if l_active else ((220, 80, 10) if is_sel_cont else (180, 205, 240))
        pts_left = [
            (l_btn_x + 12, y + 6),
            (l_btn_x + 4, y + 13),
            (l_btn_x + 12, y + 20)
        ]
        pygame.draw.polygon(surf, l_col, pts_left)

        # Slot Counter Text: SLOT 04 / 99
        cnt_col = (20, 30, 50) if is_sel_cont else (240, 246, 255)
        cnt_str = f"SLOT {cur_num:02d} / {len(self.slots)}"
        cnt_txt = gfx.fonts["regular"].render(cnt_str, True, cnt_col)
        surf.blit(cnt_txt, (x + (bw - cnt_txt.get_width()) // 2, y + 3))

        # Right Vector Chevron Button
        r_btn_x = x + bw - 18
        r_active = (self.arrow_pulse_right > 0)
        r_col = (255, 120, 20) if r_active else ((220, 80, 10) if is_sel_cont else (180, 205, 240))
        pts_right = [
            (r_btn_x + 2, y + 6),
            (r_btn_x + 10, y + 13),
            (r_btn_x + 2, y + 20)
        ]
        pygame.draw.polygon(surf, r_col, pts_right)

    def _draw_mini_stat_badge(self, surf, x, y, text, is_sel_cont, text_color=None):
        """Renders small rounded info tags for party count, money, etc."""
        f = gfx.fonts["small"]
        txt = f.render(text, True, text_color or ((30, 40, 60) if is_sel_cont else (210, 225, 245)))
        bw = txt.get_width() + 14
        bh = 20
        bg_col = (236, 242, 250) if is_sel_cont else (32, 44, 68)
        bdr_col = (210, 222, 238) if is_sel_cont else (55, 75, 105)
        pygame.draw.rect(surf, bdr_col, (x, y, bw, bh), border_radius=5)
        pygame.draw.rect(surf, bg_col, (x + 1, y + 1, bw - 2, bh - 2), border_radius=4)
        surf.blit(txt, (x + 7, y + 2))

    def _draw_action_button(self, surf, x, y, w, h, text, is_selected):
        """Renders a sleek button with hover halo, responsive selection, and indicator."""
        if is_selected:
            glow_surf = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
            pulse_a = int(50 + 20 * math.sin(self.timer * 4.0))
            pygame.draw.rect(glow_surf, (255, 175, 45, pulse_a), (0, 0, w + 8, h + 8), border_radius=11)
            surf.blit(glow_surf, (x - 4, y - 4))

            border_col = (245, 140, 25)
            bg_col = (255, 252, 246)
            text_col = (215, 60, 10)
        else:
            border_col = (58, 76, 110)
            bg_col = (22, 32, 52)
            text_col = (215, 228, 245)

        pygame.draw.rect(surf, border_col, (x - 1, y - 1, w + 2, h + 2), border_radius=10)
        pygame.draw.rect(surf, bg_col, (x, y, w, h), border_radius=9)

        if is_selected:
            pointer_x = x + 16 + int(math.sin(self.timer * 6.0) * 2.5)
            pts = [(pointer_x, y + h // 2 - 6), (pointer_x + 8, y + h // 2), (pointer_x, y + h // 2 + 6)]
            pygame.draw.polygon(surf, (240, 100, 20), pts)

        lbl = gfx.fonts["medium"].render(text, True, text_col)
        surf.blit(lbl, (x + (w - lbl.get_width()) // 2, y + (h - lbl.get_height()) // 2))

    def _draw_starter_showcase(self, surf):
        """Showcases featured starter Pokémon on a glowing pedestal when starting fresh."""
        feat_species = self.starters[self.starter_index]

        ped_cx, ped_cy = SCREEN_WIDTH // 2, 280
        ped_w, ped_h = 240, 190
        ped_x = ped_cx - ped_w // 2
        ped_y = ped_cy - ped_h // 2

        pygame.draw.rect(surf, (60, 85, 125), (ped_x - 2, ped_y - 2, ped_w + 4, ped_h + 4), border_radius=14)
        pygame.draw.rect(surf, (20, 30, 50), (ped_x, ped_y, ped_w, ped_h), border_radius=12)

        p_surf = gfx.get_pokemon_sprite(feat_species, is_back=False, size=(160, 160))
        bob = int(math.sin(self.timer * 3.0) * 5)
        surf.blit(p_surf, (ped_cx - 80, ped_cy - 90 + bob))

        name_txt = gfx.fonts["large"].render(feat_species.upper(), True, (255, 220, 50))
        surf.blit(name_txt, (ped_cx - name_txt.get_width() // 2, ped_y + ped_h - 36))

        sp_data = POKEMON_SPECIES.get(feat_species, {})
        p_types = sp_data.get("types", ["Normal"])
        if p_types:
            gfx.draw_type_badge(surf, p_types[0], ped_cx + name_txt.get_width() // 2 + 8, ped_y + ped_h - 36, width=54, height=18)

        prompt_y = 425
        prompt_w = 420
        prompt_h = 50
        prompt_x = (SCREEN_WIDTH - prompt_w) // 2

        pulse_a = int(60 + 30 * math.sin(self.timer * 4.0))
        glow_surf = pygame.Surface((prompt_w + 10, prompt_h + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 180, 50, pulse_a), (0, 0, prompt_w + 10, prompt_h + 10), border_radius=12)
        surf.blit(glow_surf, (prompt_x - 5, prompt_y - 5))

        pygame.draw.rect(surf, (250, 150, 30), (prompt_x - 2, prompt_y - 2, prompt_w + 4, prompt_h + 4), border_radius=10)
        pygame.draw.rect(surf, (255, 252, 246), (prompt_x, prompt_y, prompt_w, prompt_h), border_radius=8)

        start_txt = gfx.fonts["medium"].render("PRESS [ENTER] OR [Z] TO START", True, (220, 70, 10))
        surf.blit(start_txt, (SCREEN_WIDTH // 2 - start_txt.get_width() // 2, prompt_y + 14))

    def _draw_controls_bar(self, surf):
        """Renders arcade/console keycap pill indicators at the bottom."""
        by = 556
        badges = [
            ("↑/↓", "Select"),
            ("←/→", "Switch Slot (1-99)"),
            ("Z / Enter", "Confirm")
        ]

        total_w = 0
        items = []
        for key_txt, desc_txt in badges:
            k_surf = gfx.fonts["small"].render(key_txt, True, WHITE)
            d_surf = gfx.fonts["small"].render(desc_txt, True, (160, 175, 200))
            kw = k_surf.get_width() + 10
            dw = d_surf.get_width()
            item_w = kw + 6 + dw + 18
            items.append((k_surf, d_surf, kw, dw, item_w))
            total_w += item_w

        start_x = (SCREEN_WIDTH - total_w) // 2
        for k_surf, d_surf, kw, dw, item_w in items:
            pygame.draw.rect(surf, (55, 70, 100), (start_x, by, kw, 20), border_radius=4)
            pygame.draw.rect(surf, (20, 26, 42), (start_x + 1, by + 1, kw - 2, 18), border_radius=3)
            surf.blit(k_surf, (start_x + (kw - k_surf.get_width()) // 2, by + 2))

            surf.blit(d_surf, (start_x + kw + 6, by + 2))
            start_x += item_w

class SaveSlotSelectScreen:
    """
    UI for managing multiple save slots (Slots 1, 2, 3).
    Modes:
      - 'LOAD': User picks an existing save to resume.
      - 'NEW_GAME': User picks a slot to start a new journey.
      - 'SAVE': In-game menu to save into any slot.
    """
    def __init__(self, mode="LOAD", active_slot=1, player=None, party=None, inventory=None, pokedex=None, world=None, pc_box=None, quest_mgr=None):
        self.mode = mode # "LOAD", "NEW_GAME", "SAVE"
        self.active_slot = active_slot
        self.player = player
        self.party = party
        self.inventory = inventory
        self.pokedex = pokedex
        self.world = world
        self.pc_box = pc_box
        self.quest_mgr = quest_mgr
        self.selected_idx = max(0, min(NUM_SAVE_SLOTS - 1, active_slot - 1))
        self.scroll_offset = max(0, min(NUM_SAVE_SLOTS - 4, self.selected_idx - 1))
        self.slots = []
        self.anim_timer = 0.0
        self.refresh_slots()
        
        # Overwrite Confirmation Modal
        self.confirm_modal = False
        self.modal_selected_yes = False
        self.target_slot_for_modal = 1
        
        # Status message
        self.status_msg = ""
        self.status_timer = 0.0

    def refresh_slots(self):
        from save_system import SaveSystem
        self.slots = SaveSystem.get_all_slots_summary()

    def handle_input(self, event):
        if event.type not in [pygame.KEYDOWN, pygame.MOUSEWHEEL]:
            return None

        # Modal Input
        if self.confirm_modal:
            if event.type == pygame.KEYDOWN:
                if any(event.key == k for k in KEY_LEFT + KEY_RIGHT + KEY_UP + KEY_DOWN):
                    self.modal_selected_yes = not self.modal_selected_yes
                    sound_mgr.play_sfx("select")
                elif any(event.key == k for k in KEY_CANCEL):
                    self.confirm_modal = False
                    sound_mgr.play_sfx("cancel")
                elif any(event.key == k for k in KEY_CONFIRM):
                    if self.modal_selected_yes:
                        self.confirm_modal = False
                        sound_mgr.play_sfx("confirm")
                        if self.mode == "NEW_GAME":
                            return ("NEW_GAME", self.target_slot_for_modal)
                        elif self.mode == "SAVE":
                            from save_system import SaveSystem
                            SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world, slot=self.target_slot_for_modal, pc_box=self.pc_box, quest_mgr=self.quest_mgr)
                            self.refresh_slots()
                            return ("SAVED", self.target_slot_for_modal)
                    else:
                        self.confirm_modal = False
                        sound_mgr.play_sfx("cancel")
            return None

        # Mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            if event.y != 0:
                self.selected_idx = max(0, min(len(self.slots) - 1, self.selected_idx - event.y))
                self._update_scroll_bounds()
                sound_mgr.play_sfx("select")
            return None

        # Main Slot Selection Input (Keyboard)
        if any(event.key == k for k in KEY_UP):
            self.selected_idx = (self.selected_idx - 1) % len(self.slots)
            self._update_scroll_bounds()
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_DOWN):
            self.selected_idx = (self.selected_idx + 1) % len(self.slots)
            self._update_scroll_bounds()
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_LEFT) or event.key == pygame.K_PAGEUP:
            # Jump up 4 slots (1 page)
            self.selected_idx = max(0, self.selected_idx - 4)
            self._update_scroll_bounds()
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_RIGHT) or event.key == pygame.K_PAGEDOWN:
            # Jump down 4 slots (1 page)
            self.selected_idx = min(len(self.slots) - 1, self.selected_idx + 4)
            self._update_scroll_bounds()
            sound_mgr.play_sfx("select")
        elif event.key == pygame.K_HOME:
            self.selected_idx = 0
            self._update_scroll_bounds()
            sound_mgr.play_sfx("select")
        elif event.key == pygame.K_END:
            self.selected_idx = len(self.slots) - 1
            self._update_scroll_bounds()
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_CANCEL):
            sound_mgr.play_sfx("cancel")
            return ("CANCEL", None)
        elif any(event.key == k for k in KEY_CONFIRM):
            chosen_slot = self.selected_idx + 1
            slot_data = self.slots[self.selected_idx]

            if self.mode == "LOAD":
                if not slot_data.get("exists"):
                    sound_mgr.play_sfx("cancel")
                    self.status_msg = f"Slot {chosen_slot} is empty! Please choose a saved game."
                    self.status_timer = 2.5
                else:
                    sound_mgr.play_sfx("confirm")
                    return ("LOAD", chosen_slot)

            elif self.mode == "NEW_GAME":
                if slot_data.get("exists"):
                    sound_mgr.play_sfx("select")
                    self.target_slot_for_modal = chosen_slot
                    self.confirm_modal = True
                    self.modal_selected_yes = False
                else:
                    sound_mgr.play_sfx("confirm")
                    return ("NEW_GAME", chosen_slot)

            elif self.mode == "SAVE":
                if slot_data.get("exists") and chosen_slot != self.active_slot:
                    sound_mgr.play_sfx("select")
                    self.target_slot_for_modal = chosen_slot
                    self.confirm_modal = True
                    self.modal_selected_yes = False
                else:
                    from save_system import SaveSystem
                    SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world, slot=chosen_slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr)
                    sound_mgr.play_sfx("confirm")
                    self.refresh_slots()
                    return ("SAVED", chosen_slot)

        return None

    def _update_scroll_bounds(self):
        visible_count = 4
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + visible_count:
            self.scroll_offset = self.selected_idx - visible_count + 1
        self.scroll_offset = max(0, min(len(self.slots) - visible_count, self.scroll_offset))

    def update(self, dt):
        self.anim_timer += dt
        if self.status_timer > 0:
            self.status_timer = max(0.0, self.status_timer - dt)
            if self.status_timer == 0:
                self.status_msg = ""

    def draw(self, surf):
        surf.fill((235, 240, 248))

        # Header Titles based on mode
        if self.mode == "LOAD":
            title_str = "LOAD SAVE FILE (SLOTS 1 - 99)"
            subtitle_str = "Select a save slot to continue your journey"
        elif self.mode == "NEW_GAME":
            title_str = "NEW GAME - SELECT SLOT (1 - 99)"
            subtitle_str = "Select a slot to start your adventure"
        else: # SAVE
            title_str = "SAVE GAME PROGRESS (SLOTS 1 - 99)"
            subtitle_str = f"Select a slot to save progress (Current: Slot {self.active_slot})"

        head = gfx.fonts["title"].render(title_str, True, (220, 80, 0) if self.mode == "SAVE" else UI_TEXT)
        sub = gfx.fonts["regular"].render(subtitle_str, True, UI_TEXT_MUTED)
        surf.blit(head, (SCREEN_WIDTH // 2 - head.get_width() // 2, 20))
        surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 60))

        # Top Right Slot Counter Pill
        counter_txt = f"SLOT {self.selected_idx + 1} / {len(self.slots)}"
        pill_surf = gfx.fonts["small"].render(counter_txt, True, WHITE)
        pill_w = pill_surf.get_width() + 20
        pygame.draw.rect(surf, (45, 60, 85), (SCREEN_WIDTH - pill_w - 40, 24, pill_w, 28), border_radius=14)
        surf.blit(pill_surf, (SCREEN_WIDTH - pill_w - 40 + 10, 29))

        # Scrollable 4 Visible Cards Window
        card_w, card_h = 680, 96
        start_x = (SCREEN_WIDTH - card_w) // 2 - 8
        visible_count = 4

        for vi in range(visible_count):
            i = self.scroll_offset + vi
            if i >= len(self.slots):
                break

            s_data = self.slots[i]
            slot_num = i + 1
            card_y = 96 + vi * 108
            is_sel = (i == self.selected_idx)
            is_active = (self.mode == "SAVE" and slot_num == self.active_slot)

            # Card border and fill
            bdr_col = (240, 140, 40) if is_sel else (UI_BORDER_DARK if is_active else UI_BORDER_LIGHT)
            bg_col = (255, 250, 235) if is_sel else WHITE
            pygame.draw.rect(surf, bdr_col, (start_x - 2, card_y - 2, card_w + 4, card_h + 4), border_radius=10)
            pygame.draw.rect(surf, bg_col, (start_x, card_y, card_w, card_h), border_radius=8)

            # Left Selection Accent Bar
            if is_sel:
                pygame.draw.rect(surf, (230, 80, 20), (start_x, card_y, 6, card_h), border_top_left_radius=8, border_bottom_left_radius=8)

            # Slot Pill Badge
            slot_pill_col = (220, 80, 0) if is_sel else (45, 110, 200)
            pygame.draw.rect(surf, slot_pill_col, (start_x + 16, card_y + 12, 76, 24), border_radius=5)
            slot_lbl = gfx.fonts["small"].render(f"SLOT {slot_num:02d}", True, WHITE)
            surf.blit(slot_lbl, (start_x + 16 + (76 - slot_lbl.get_width()) // 2, card_y + 16))

            if is_active:
                # Active slot badge
                pygame.draw.rect(surf, (40, 160, 60), (start_x + 98, card_y + 12, 80, 24), border_radius=5)
                act_lbl = gfx.fonts["small"].render("ACTIVE", True, WHITE)
                surf.blit(act_lbl, (start_x + 98 + (80 - act_lbl.get_width()) // 2, card_y + 16))

            if s_data.get("exists"):
                # Lead Pokemon Sprite with animated bobbing if selected
                lead_species = s_data.get("lead_species", "Pikachu")
                sp_surf = gfx.get_pokemon_sprite(lead_species, is_back=False, size=(60, 60))
                hop_y = -int(abs(math.sin(self.anim_timer * 4.0)) * 3) if is_sel else 0
                surf.blit(sp_surf, (start_x + 16, card_y + 36 + hop_y))

                # Main Details
                lead_name = s_data.get("lead_name", "Pokémon")
                lead_lvl = s_data.get("lead_level", 5)
                loc_name = s_data.get("map", "Pallet Town")
                lead_txt = gfx.fonts["regular"].render(f"{lead_name} (Lv. {lead_lvl})", True, (210, 70, 0) if is_sel else UI_TEXT)
                loc_txt = gfx.fonts["small"].render(f"📍 {loc_name}", True, UI_TEXT_MUTED)
                surf.blit(lead_txt, (start_x + 88, card_y + 40))
                surf.blit(loc_txt, (start_x + 88, card_y + 66))

                # Stats on the right
                team_count = s_data.get("party_count", 1)
                money_val = s_data.get("money", 0)
                caught_val = s_data.get("caught_count", 0)
                stats_str = f"Party: {team_count} | Money: ${money_val} | Dex: {caught_val}/151"
                stats_txt = gfx.fonts["small"].render(stats_str, True, UI_TEXT)
                surf.blit(stats_txt, (start_x + 340, card_y + 38))

                # Timestamp
                time_str = s_data.get("timestamp", "")
                if time_str:
                    time_txt = gfx.fonts["small"].render(f"Saved: {time_str}", True, UI_TEXT_MUTED)
                    surf.blit(time_txt, (start_x + 340, card_y + 66))
            else:
                # Empty Slot presentation
                empty_txt = gfx.fonts["regular"].render(f"+ [ EMPTY SAVE SLOT {slot_num} ]", True, (200, 80, 0) if is_sel else UI_TEXT_MUTED)
                sub_empty = gfx.fonts["small"].render("No adventure recorded in this slot. Ready to begin!", True, UI_TEXT_MUTED)
                surf.blit(empty_txt, (start_x + 104, card_y + 38))
                surf.blit(sub_empty, (start_x + 104, card_y + 66))

        # Vertical Scrollbar on Right
        track_x = start_x + card_w + 14
        track_y = 96
        track_w = 8
        track_h = visible_count * 108 - 12
        pygame.draw.rect(surf, (215, 225, 238), (track_x, track_y, track_w, track_h), border_radius=4)

        max_scroll = max(1, len(self.slots) - visible_count)
        thumb_h = max(28, int(track_h * (visible_count / len(self.slots))))
        thumb_y = track_y + int((track_h - thumb_h) * (self.scroll_offset / max_scroll))
        thumb_col = (230, 110, 30) if self.selected_idx >= 0 else (150, 170, 195)
        pygame.draw.rect(surf, thumb_col, (track_x, thumb_y, track_w, thumb_h), border_radius=4)

        # Status message
        if self.status_msg:
            st_surf = gfx.fonts["regular"].render(self.status_msg, True, (220, 40, 40))
            surf.blit(st_surf, (SCREEN_WIDTH // 2 - st_surf.get_width() // 2, 532))

        # Bottom Hint Bar
        nav_hint = gfx.fonts["small"].render("▲/▼: Scroll Slot  |  ◀/▶ or PgUp/PgDn: Jump Page (±4)  |  [Z / Enter]: Confirm  |  [X / ESC]: Cancel", True, UI_TEXT_MUTED)
        surf.blit(nav_hint, (SCREEN_WIDTH // 2 - nav_hint.get_width() // 2, 564))

        # Overwrite Confirmation Modal Dialog
        if self.confirm_modal:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surf.blit(overlay, (0, 0))

            mw, mh = 480, 230
            mx = (SCREEN_WIDTH - mw) // 2
            my = (SCREEN_HEIGHT - mh) // 2
            pygame.draw.rect(surf, (220, 60, 60), (mx - 2, my - 2, mw + 4, mh + 4), border_radius=12)
            pygame.draw.rect(surf, WHITE, (mx, my, mw, mh), border_radius=10)

            warn_title = gfx.fonts["large"].render(f"OVERWRITE SLOT {self.target_slot_for_modal}?", True, (220, 60, 60))
            surf.blit(warn_title, (mx + (mw - warn_title.get_width()) // 2, my + 24))

            m1 = gfx.fonts["regular"].render("This save slot already contains adventure data!", True, UI_TEXT)
            m2 = gfx.fonts["small"].render("Overwriting will permanently replace the existing save.", True, UI_TEXT_MUTED)
            surf.blit(m1, (mx + (mw - m1.get_width()) // 2, my + 75))
            surf.blit(m2, (mx + (mw - m2.get_width()) // 2, my + 105))

            for i, opt in enumerate(["YES, OVERWRITE", "NO, CANCEL"]):
                is_btn_sel = (i == 0 and self.modal_selected_yes) or (i == 1 and not self.modal_selected_yes)
                btn_w, btn_h = 160, 40
                btn_x = mx + 55 + i * 210
                btn_y = my + 155

                b_bdr = (220, 60, 60) if (is_btn_sel and i == 0) else ((240, 140, 40) if is_btn_sel else UI_BORDER_LIGHT)
                b_bg = (255, 230, 230) if (is_btn_sel and i == 0) else ((255, 245, 220) if is_btn_sel else UI_BG)
                pygame.draw.rect(surf, b_bdr, (btn_x, btn_y, btn_w, btn_h), border_radius=6)
                pygame.draw.rect(surf, b_bg, (btn_x + 1, btn_y + 1, btn_w - 2, btn_h - 2), border_radius=5)

                btxt = gfx.fonts["regular"].render(opt, True, (200, 40, 40) if (is_btn_sel and i == 0) else UI_TEXT)
                surf.blit(btxt, (btn_x + (btn_w - btxt.get_width()) // 2, btn_y + (btn_h - btxt.get_height()) // 2))

class SaveDialog:
    def __init__(self, player, party, inventory, pokedex, slot=1, pc_box=None, quest_mgr=None):
        self.player = player
        self.party = party
        self.inventory = inventory
        self.pokedex = pokedex
        self.slot = slot
        self.pc_box = pc_box
        self.quest_mgr = quest_mgr
        self.selected_yes = True
        self.state = "CONFIRM" # "CONFIRM", "SAVING", "SAVED"
        self.timer = 0.0

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
            
        if self.state == "CONFIRM":
            if any(event.key == k for k in KEY_LEFT + KEY_RIGHT + KEY_UP + KEY_DOWN):
                self.selected_yes = not self.selected_yes
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                return "CANCEL"
            elif any(event.key == k for k in KEY_CONFIRM):
                if self.selected_yes:
                    self.state = "SAVING"
                    self.timer = 0.0
                else:
                    sound_mgr.play_sfx("cancel")
                    return "CANCEL"
        elif self.state == "SAVED":
            if any(event.key == k for k in KEY_CONFIRM + KEY_CANCEL + KEY_MENU):
                return "DONE"
        return None

    def update(self, dt, world):
        self.timer += dt
        if self.state == "SAVING" and self.timer >= 0.2:
            from save_system import SaveSystem
            SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, world, slot=self.slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr)
            sound_mgr.play_sfx("confirm")
            self.state = "SAVED"
            self.timer = 0.0
        elif self.state == "SAVED" and self.timer >= 1.2:
            return "DONE"
        return None

    def draw(self, surf):
        # Center Save Card
        bw, bh = 480, 260
        bx = (SCREEN_WIDTH - bw) // 2
        by = (SCREEN_HEIGHT - bh) // 2
        
        pygame.draw.rect(surf, UI_BORDER_DARK, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=12)
        pygame.draw.rect(surf, WHITE, (bx, by, bw, bh), border_radius=10)
        
        # Header
        head = gfx.fonts["title"].render(f"SAVE GAME (SLOT {self.slot})", True, (220, 80, 0))
        surf.blit(head, (bx + (bw - head.get_width()) // 2, by + 18))
        
        if self.state == "CONFIRM":
            # Info Box
            lead_name = self.party[0].nickname if self.party else "None"
            lead_lvl = self.party[0].level if self.party else 5
            loc_str = f"Location: {self.player.current_map}"
            team_str = f"Leader: {lead_name} (Lv.{lead_lvl}) | Team: {len(self.party)}"
            money_str = f"Money: ${self.inventory.money} | Pokédex: {len(self.pokedex.caught)}/151"
            
            surf.blit(gfx.fonts["regular"].render(loc_str, True, UI_TEXT), (bx + 30, by + 75))
            surf.blit(gfx.fonts["regular"].render(team_str, True, UI_TEXT), (bx + 30, by + 105))
            surf.blit(gfx.fonts["small"].render(money_str, True, UI_TEXT_MUTED), (bx + 30, by + 135))
            
            q_txt = gfx.fonts["regular"].render(f"Save progress into Slot {self.slot}?", True, UI_TEXT)
            surf.blit(q_txt, (bx + (bw - q_txt.get_width()) // 2, by + 168))
            
            # [YES] / [NO] buttons
            for i, opt in enumerate(["YES", "NO"]):
                is_sel = (i == 0 and self.selected_yes) or (i == 1 and not self.selected_yes)
                btn_w, btn_h = 100, 36
                btn_x = bx + 120 + i * 140
                btn_y = by + 205
                
                bdr = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
                bg = (255, 235, 180) if is_sel else UI_BG
                pygame.draw.rect(surf, bdr, (btn_x, btn_y, btn_w, btn_h), border_radius=6)
                pygame.draw.rect(surf, bg, (btn_x + 1, btn_y + 1, btn_w - 2, btn_h - 2), border_radius=5)
                
                btxt = gfx.fonts["regular"].render(opt, True, (200, 80, 0) if is_sel else UI_TEXT)
                surf.blit(btxt, (btn_x + (btn_w - btxt.get_width()) // 2, btn_y + (btn_h - btxt.get_height()) // 2))
        elif self.state == "SAVING":
            stxt = gfx.fonts["large"].render(f"Saving to Slot {self.slot}...", True, UI_TEXT)
            surf.blit(stxt, (bx + (bw - stxt.get_width()) // 2, by + 120))
        elif self.state == "SAVED":
            stxt = gfx.fonts["large"].render(f"Saved to Slot {self.slot} successfully!", True, (40, 140, 60))
            surf.blit(stxt, (bx + (bw - stxt.get_width()) // 2, by + 110))
            hint = gfx.fonts["small"].render("Press [Z / Enter] to continue", True, UI_TEXT_MUTED)
            surf.blit(hint, (bx + (bw - hint.get_width()) // 2, by + 160))

class TrainerCustomizationScreen:
    """
    Interactive Trainer Customization Start Menu.
    Allows configuring:
      - Trainer Name (with live typing and backspace)
      - Gender (Boy / Girl)
      - Outfit Color Theme
      - Headwear / Hat Style
      - Hair Color
      - Starter Companion Pokémon (Charmander, Squirtle, Bulbasaur, Pikachu, Eevee)
    Features real-time animated preview of the customized trainer and companion Pokémon.
    """
    def __init__(self):
        self.genders = ["Boy", "Girl"]
        self.gender_idx = 0
        
        self.outfits = list(OUTFIT_THEMES.keys())
        self.outfit_idx = 0
        
        self.hat_styles = list(HAT_STYLES)
        self.hat_idx = 0
        
        self.hair_colors = list(HAIR_COLORS.keys())
        self.hair_idx = 0
        
        self.starters = list(STARTER_CHOICES)
        self.starter_idx = 0
        
        self.name = "Red"
        self.is_editing_name = False
        
        self.selected_row = 0
        self.total_rows = 7
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        # Text input mode for name
        if self.is_editing_name:
            if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                self.is_editing_name = False
                sound_mgr.play_sfx("confirm")
                if not self.name.strip():
                    self.name = "Red" if self.genders[self.gender_idx] == "Boy" else "Leaf"
            elif event.key == pygame.K_ESCAPE:
                self.is_editing_name = False
                sound_mgr.play_sfx("cancel")
            elif event.key == pygame.K_BACKSPACE:
                if len(self.name) > 0:
                    self.name = self.name[:-1]
                    sound_mgr.play_sfx("select")
            else:
                if event.unicode and event.unicode.isprintable() and len(self.name) < 10:
                    if event.unicode not in ["\r", "\n", "\t"]:
                        self.name += event.unicode
                        sound_mgr.play_sfx("select")
            return None

        # Navigation mode
        if any(event.key == k for k in KEY_UP):
            self.selected_row = (self.selected_row - 1) % self.total_rows
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_DOWN):
            self.selected_row = (self.selected_row + 1) % self.total_rows
            sound_mgr.play_sfx("select")

        elif any(event.key == k for k in KEY_LEFT):
            if self.selected_row == 0:
                self.is_editing_name = True
                sound_mgr.play_sfx("select")
            elif self.selected_row == 1:
                self.gender_idx = (self.gender_idx - 1) % len(self.genders)
                if self.name in ["Red", "Leaf"]:
                    self.name = "Red" if self.genders[self.gender_idx] == "Boy" else "Leaf"
                sound_mgr.play_sfx("select")
            elif self.selected_row == 2:
                self.outfit_idx = (self.outfit_idx - 1) % len(self.outfits)
                sound_mgr.play_sfx("select")
            elif self.selected_row == 3:
                self.hat_idx = (self.hat_idx - 1) % len(self.hat_styles)
                sound_mgr.play_sfx("select")
            elif self.selected_row == 4:
                self.hair_idx = (self.hair_idx - 1) % len(self.hair_colors)
                sound_mgr.play_sfx("select")
            elif self.selected_row == 5:
                self.starter_idx = (self.starter_idx - 1) % len(self.starters)
                sound_mgr.play_sfx("select")

        elif any(event.key == k for k in KEY_RIGHT):
            if self.selected_row == 0:
                self.is_editing_name = True
                sound_mgr.play_sfx("select")
            elif self.selected_row == 1:
                self.gender_idx = (self.gender_idx + 1) % len(self.genders)
                if self.name in ["Red", "Leaf"]:
                    self.name = "Red" if self.genders[self.gender_idx] == "Boy" else "Leaf"
                sound_mgr.play_sfx("select")
            elif self.selected_row == 2:
                self.outfit_idx = (self.outfit_idx + 1) % len(self.outfits)
                sound_mgr.play_sfx("select")
            elif self.selected_row == 3:
                self.hat_idx = (self.hat_idx + 1) % len(self.hat_styles)
                sound_mgr.play_sfx("select")
            elif self.selected_row == 4:
                self.hair_idx = (self.hair_idx + 1) % len(self.hair_colors)
                sound_mgr.play_sfx("select")
            elif self.selected_row == 5:
                self.starter_idx = (self.starter_idx + 1) % len(self.starters)
                sound_mgr.play_sfx("select")

        elif any(event.key == k for k in KEY_CONFIRM):
            if self.selected_row == 0:
                self.is_editing_name = True
                sound_mgr.play_sfx("select")
            elif self.selected_row in [1, 2, 3, 4, 5]:
                # Advance option on Enter
                if self.selected_row == 1:
                    self.gender_idx = (self.gender_idx + 1) % len(self.genders)
                    if self.name in ["Red", "Leaf"]:
                        self.name = "Red" if self.genders[self.gender_idx] == "Boy" else "Leaf"
                elif self.selected_row == 2:
                    self.outfit_idx = (self.outfit_idx + 1) % len(self.outfits)
                elif self.selected_row == 3:
                    self.hat_idx = (self.hat_idx + 1) % len(self.hat_styles)
                elif self.selected_row == 4:
                    self.hair_idx = (self.hair_idx + 1) % len(self.hair_colors)
                elif self.selected_row == 5:
                    self.starter_idx = (self.starter_idx + 1) % len(self.starters)
                sound_mgr.play_sfx("select")
            elif self.selected_row == 6:
                # Start Adventure!
                sound_mgr.play_sfx("confirm")
                final_name = self.name.strip() or ("Red" if self.genders[self.gender_idx] == "Boy" else "Leaf")
                return {
                    "name": final_name,
                    "gender": self.genders[self.gender_idx],
                    "outfit_theme": self.outfits[self.outfit_idx],
                    "hat_style": self.hat_styles[self.hat_idx],
                    "hair_color": self.hair_colors[self.hair_idx],
                    "starter_species": self.starters[self.starter_idx]
                }

        elif any(event.key == k for k in KEY_CANCEL):
            sound_mgr.play_sfx("cancel")
            return "CANCEL"

        return None

    def draw(self, surf):
        surf.fill((235, 240, 248))

        # Header
        head_txt = gfx.fonts["title"].render("TRAINER REGISTRATION", True, (220, 40, 40))
        sub_txt = gfx.fonts["regular"].render("Customize your trainer profile & choose your first companion Pokémon!", True, UI_TEXT_MUTED)
        surf.blit(head_txt, (SCREEN_WIDTH // 2 - head_txt.get_width() // 2, 18))
        surf.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 60))

        # Left Column: Live Character & Starter Preview
        px, py, pw, ph = 35, 95, 330, 460
        pygame.draw.rect(surf, UI_BORDER_DARK, (px - 2, py - 2, pw + 4, ph + 4), border_radius=12)
        pygame.draw.rect(surf, WHITE, (px, py, pw, ph), border_radius=10)

        # Preview Header
        phead = gfx.fonts["large"].render("TRAINER PREVIEW", True, (200, 80, 0))
        surf.blit(phead, (px + (pw - phead.get_width()) // 2, py + 14))

        # Trainer High-Res Portrait
        t_gender = self.genders[self.gender_idx]
        t_outfit = self.outfits[self.outfit_idx]
        t_hat = self.hat_styles[self.hat_idx]
        t_hair = self.hair_colors[self.hair_idx]
        trainer_surf = gfx.get_trainer_preview_sprite(t_gender, t_outfit, t_hat, t_hair, size=(130, 130))
        surf.blit(trainer_surf, (px + 20, py + 48))

        # Starter Companion Sprite
        curr_starter = self.starters[self.starter_idx]
        starter_surf = gfx.get_pokemon_sprite(curr_starter, is_back=False, size=(110, 110))
        surf.blit(starter_surf, (px + 185, py + 58))

        # Companion Info Box
        comp_y = py + 185
        pygame.draw.rect(surf, (245, 248, 255), (px + 14, comp_y, pw - 28, 250), border_radius=8)
        pygame.draw.rect(surf, UI_BORDER_LIGHT, (px + 14, comp_y, pw - 28, 250), 1, border_radius=8)

        st_data = POKEMON_SPECIES[curr_starter]
        st_name_txt = gfx.fonts["large"].render(f"Starter: {curr_starter}", True, UI_TEXT)
        surf.blit(st_name_txt, (px + 24, comp_y + 12))

        # Type Badges
        for t_idx, t_name in enumerate(st_data["types"]):
            gfx.draw_type_badge(surf, t_name, px + 24 + t_idx * 70, comp_y + 44, width=64, height=22)

        # Base Stats
        hp_val = st_data["base_stats"]["hp"]
        atk_val = st_data["base_stats"]["atk"]
        def_val = st_data["base_stats"]["def"]
        spd_val = st_data["base_stats"]["spd"]
        stat_line1 = gfx.fonts["regular"].render(f"Base HP: {hp_val}   ATK: {atk_val}", True, UI_TEXT)
        stat_line2 = gfx.fonts["regular"].render(f"Base DEF: {def_val}   SPD: {spd_val}", True, UI_TEXT)
        surf.blit(stat_line1, (px + 24, comp_y + 78))
        surf.blit(stat_line2, (px + 24, comp_y + 104))

        # Initial Moves
        init_moves = st_data.get("learnset", {}).get(1, ["Tackle"])
        moves_str = f"Initial Moves: {', '.join(init_moves[:2])}"
        moves_txt = gfx.fonts["small"].render(moves_str, True, (40, 120, 220))
        surf.blit(moves_txt, (px + 24, comp_y + 138))

        # Lore description snippet
        desc_snippet = st_data.get("desc", "")[:80] + "..."
        desc_txt = gfx.fonts["small"].render(desc_snippet, True, UI_TEXT_MUTED)
        surf.blit(desc_txt, (px + 24, comp_y + 168))

        # Right Column: Customization Controls
        rx, ry, rw, rh = 390, 95, 375, 460
        pygame.draw.rect(surf, UI_BORDER_DARK, (rx - 2, ry - 2, rw + 4, rh + 4), border_radius=12)
        pygame.draw.rect(surf, WHITE, (rx, ry, rw, rh), border_radius=10)

        # Rows Setup
        row_labels = [
            ("Trainer Name", self.name + ("|" if (self.is_editing_name and int(self.timer * 3) % 2 == 0) else "")),
            ("Gender", self.genders[self.gender_idx]),
            ("Outfit Theme", self.outfits[self.outfit_idx]),
            ("Headwear", self.hat_styles[self.hat_idx]),
            ("Hair Color", self.hair_colors[self.hair_idx]),
            ("Starter Pokémon", self.starters[self.starter_idx])
        ]

        for i, (lbl, val) in enumerate(row_labels):
            row_y = ry + 16 + i * 58
            is_sel = (i == self.selected_row)
            
            # Row container
            bdr = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
            bg = (255, 245, 220) if is_sel else (250, 250, 252)
            pygame.draw.rect(surf, bdr, (rx + 12, row_y, rw - 24, 48), border_radius=8)
            pygame.draw.rect(surf, bg, (rx + 13, row_y + 1, rw - 26, 46), border_radius=7)

            # Label
            ltxt = gfx.fonts["small"].render(lbl, True, (200, 80, 0) if is_sel else UI_TEXT_MUTED)
            surf.blit(ltxt, (rx + 22, row_y + 6))

            # Value with arrows
            if i == 0:
                # Name text
                hint = " [Click / Enter to Type]" if not self.is_editing_name and is_sel else ""
                val_txt = gfx.fonts["regular"].render(f"{val}{hint}", True, (220, 40, 40) if self.is_editing_name else UI_TEXT)
                surf.blit(val_txt, (rx + 22, row_y + 24))
            else:
                # Arrow controls
                val_txt = gfx.fonts["regular"].render(f"<  {val}  >", True, (200, 80, 0) if is_sel else UI_TEXT)
                surf.blit(val_txt, (rx + 22, row_y + 24))

                # Visual Color Swatches for Outfit and Hair
                if i == 2:
                    swatch_col = OUTFIT_THEMES[self.outfits[self.outfit_idx]]["shirt"]
                    pygame.draw.rect(surf, swatch_col, (rx + rw - 44, row_y + 15, 18, 18), border_radius=4)
                    pygame.draw.rect(surf, BLACK, (rx + rw - 44, row_y + 15, 18, 18), 1, border_radius=4)
                elif i == 4:
                    hair_swatch = HAIR_COLORS[self.hair_colors[self.hair_idx]]
                    pygame.draw.circle(surf, hair_swatch, (rx + rw - 35, row_y + 24), 9)
                    pygame.draw.circle(surf, BLACK, (rx + rw - 35, row_y + 24), 9, 1)

        # Row 6: [ START ADVENTURE ] Button
        btn_y = ry + 372
        btn_is_sel = (self.selected_row == 6)
        btn_bdr = (240, 140, 40) if btn_is_sel else (40, 160, 60)
        btn_bg = (255, 235, 180) if btn_is_sel else (45, 180, 75)
        
        pygame.draw.rect(surf, btn_bdr, (rx + 12, btn_y, rw - 24, 58), border_radius=10)
        pygame.draw.rect(surf, btn_bg, (rx + 14, btn_y + 2, rw - 28, 54), border_radius=8)

        start_btn_txt = gfx.fonts["title"].render("START ADVENTURE!", True, (200, 40, 40) if btn_is_sel else WHITE)
        surf.blit(start_btn_txt, (rx + 12 + (rw - 24 - start_btn_txt.get_width()) // 2, btn_y + 12))

        # Bottom Hint Bar
        if self.is_editing_name:
            hint = gfx.fonts["small"].render("Type name on keyboard  |  [Enter]: Confirm Name  |  [ESC]: Cancel", True, (220, 40, 40))
        else:
            hint = gfx.fonts["small"].render("Up/Down: Select  |  Left/Right: Change Option  |  [Enter]: Start  |  [X]: Back", True, UI_TEXT_MUTED)
        surf.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 568))

StarterSelectScreen = TrainerCustomizationScreen

class PauseMenu:
    def __init__(self):
        self.options = ["POKÉDEX", "POKÉMON", "BAG", "QUESTS", "MAP", "PC BOX", "TRAINER", "SAVE", "EXIT"]
        self.selected_idx = 0

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
            
        if any(event.key == k for k in KEY_UP):
            self.selected_idx = (self.selected_idx - 1) % len(self.options)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_DOWN):
            self.selected_idx = (self.selected_idx + 1) % len(self.options)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_CANCEL):
            sound_mgr.play_sfx("cancel")
            return "EXIT"
        elif any(event.key == k for k in KEY_CONFIRM):
            sound_mgr.play_sfx("confirm")
            return self.options[self.selected_idx]
        return None

    def draw(self, surf):
        # Draw on top-right of screen
        mw, mh = 210, 380
        mx = SCREEN_WIDTH - mw - 20
        my = 15
        
        pygame.draw.rect(surf, UI_BORDER_DARK, (mx - 2, my - 2, mw + 4, mh + 4), border_radius=10)
        pygame.draw.rect(surf, UI_BG, (mx, my, mw, mh), border_radius=8)
        
        for i, opt in enumerate(self.options):
            iy = my + 10 + i * 40
            is_sel = (i == self.selected_idx)
            
            if is_sel:
                pygame.draw.rect(surf, (255, 235, 180), (mx + 8, iy - 4, mw - 16, 34), border_radius=6)
                pygame.draw.rect(surf, (240, 140, 40), (mx + 8, iy - 4, mw - 16, 34), 2, border_radius=6)
                
            txt = gfx.fonts["regular"].render(opt, True, (200, 80, 0) if is_sel else UI_TEXT)
            surf.blit(txt, (mx + 20, iy))

class ShopScreen:
    def __init__(self, inventory):
        self.inventory = inventory
        self.mode = "BUY"  # "BUY" or "SELL"
        self.items_for_sale = [
            "Poke Ball", "Great Ball", "Ultra Ball",
            "Potion", "Super Potion", "Max Potion", "Revive",
            "Antidote", "Paralyze Heal", "Awakening", "Burn Heal",
            "Rare Candy", "Escape Rope", "Move Reroll Disk",
            "Moon Stone", "Fire Stone", "Water Stone", "Thunder Stone", "Leaf Stone"
        ]
        self.selected_idx = 0
        self.scroll_offset = 0
        self.message = "Welcome to PokéMart! [Left/Right]: Switch Buy/Sell  [Z]: Select  [X]: Exit"

    def get_sellable_items(self):
        """Returns list of (name, count, item_data, sell_price) from player's inventory."""
        items = []
        for name, count, data in self.inventory.get_items_list():
            if name in ["Poke Flute", "Bicycle", "Town Map", "Old Rod", "Good Rod", "Super Rod", "Silph Scope"]:
                continue
            cat = data.get("category", "")
            base_price = data.get("price", 0)
            if cat == "valuable":
                sell_price = base_price
            else:
                sell_price = max(1, base_price // 2)
            items.append((name, count, data, sell_price))
        return items

    def _get_list_length(self):
        if self.mode == "BUY":
            return len(self.items_for_sale)
        else:
            return len(self.get_sellable_items())

    def _adjust_scroll(self):
        total = self._get_list_length()
        if total == 0:
            self.selected_idx = 0
            self.scroll_offset = 0
            return
        if self.selected_idx >= total:
            self.selected_idx = total - 1
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + 7:
            self.scroll_offset = self.selected_idx - 6

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        # Mode toggle: Left/Right or Tab
        if any(event.key == k for k in KEY_LEFT) or any(event.key == k for k in KEY_RIGHT) or event.key == pygame.K_TAB:
            self.mode = "SELL" if self.mode == "BUY" else "BUY"
            self.selected_idx = 0
            self.scroll_offset = 0
            sound_mgr.play_sfx("select")
            if self.mode == "BUY":
                self.message = "PokéMart Catalogue: Select an item to buy with [Z]! [Left/Right]: Switch to Sell"
            else:
                self.message = "Your Bag Items: Select an item to sell for cash with [Z]! [Left/Right]: Switch to Buy"
            return None

        total = self._get_list_length()

        if any(event.key == k for k in KEY_UP):
            if total > 0:
                self.selected_idx = (self.selected_idx - 1) % total
                self._adjust_scroll()
                sound_mgr.play_sfx("select")
            return None
        elif any(event.key == k for k in KEY_DOWN):
            if total > 0:
                self.selected_idx = (self.selected_idx + 1) % total
                self._adjust_scroll()
                sound_mgr.play_sfx("select")
            return None
        elif any(event.key == k for k in KEY_CANCEL):
            sound_mgr.play_sfx("cancel")
            return "EXIT"
        elif any(event.key == k for k in KEY_CONFIRM):
            if self.mode == "BUY":
                item_name = self.items_for_sale[self.selected_idx]
                price = ITEMS[item_name]["price"]
                if self.inventory.money >= price:
                    self.inventory.money -= price
                    self.inventory.add_item(item_name, 1)
                    sound_mgr.play_sfx("confirm")
                    self.message = f"Bought 1 {item_name} for ${price}! (Money: ${self.inventory.money})"
                else:
                    sound_mgr.play_sfx("cancel")
                    self.message = "You don't have enough money for that!"
            else:
                sell_items = self.get_sellable_items()
                if not sell_items or self.selected_idx >= len(sell_items):
                    sound_mgr.play_sfx("cancel")
                    self.message = "You don't have any items to sell!"
                    return None
                name, count, data, sell_price = sell_items[self.selected_idx]
                self.inventory.money += sell_price
                self.inventory.remove_item(name, 1)
                sound_mgr.play_sfx("confirm")
                self.message = f"Sold 1 {name} for ${sell_price}! (Money: ${self.inventory.money})"
                new_items = self.get_sellable_items()
                if self.selected_idx >= len(new_items):
                    self.selected_idx = max(0, len(new_items) - 1)
                self._adjust_scroll()
        return None

    def draw(self, surf):
        surf.fill((235, 240, 248))
        head = gfx.fonts["title"].render("POKÉMART & ITEM CATALOGUE", True, (40, 120, 220))
        money_txt = gfx.fonts["large"].render(f"💰 Money: ${self.inventory.money}", True, (40, 140, 60))
        surf.blit(head, (30, 16))
        surf.blit(money_txt, (SCREEN_WIDTH - money_txt.get_width() - 30, 20))

        # Mode Select Tabs: [BUY ITEMS] and [SELL ITEMS]
        tab_y = 56
        tab_w = 175
        for t_idx, (t_mode, t_label) in enumerate([("BUY", "BUY ITEMS"), ("SELL", "SELL ITEMS")]):
            tx = 30 + t_idx * (tab_w + 10)
            is_active = (self.mode == t_mode)
            tbdr = (240, 120, 20) if is_active else (190, 205, 220)
            tbg = (255, 235, 180) if is_active else (245, 248, 252)
            pygame.draw.rect(surf, tbdr, (tx, tab_y, tab_w, 28), border_radius=6)
            pygame.draw.rect(surf, tbg, (tx + 1, tab_y + 1, tab_w - 2, 26), border_radius=5)
            t_col = (200, 60, 0) if is_active else UI_TEXT_MUTED
            t_txt = gfx.fonts["small"].render(t_label, True, t_col)
            surf.blit(t_txt, (tx + (tab_w - t_txt.get_width()) // 2, tab_y + 6))

        hint_tab = gfx.fonts["small"].render("[◀ / ▶]: Switch Tab", True, (100, 120, 150))
        surf.blit(hint_tab, (30 + 2 * tab_w + 30, tab_y + 7))

        # Left Box (Items List)
        lx, ly, lw, lh = 30, 92, 380, 385
        pygame.draw.rect(surf, UI_BORDER_DARK, (lx - 2, ly - 2, lw + 4, lh + 4), border_radius=8)
        pygame.draw.rect(surf, WHITE, (lx, ly, lw, lh), border_radius=6)

        if self.mode == "BUY":
            items = self.items_for_sale
            total_items = len(items)
            visible_items = items[self.scroll_offset : self.scroll_offset + 7]
            for rel_idx, name in enumerate(visible_items):
                actual_idx = self.scroll_offset + rel_idx
                is_sel = (actual_idx == self.selected_idx)
                iy = ly + 8 + rel_idx * 52
                price = ITEMS[name]["price"]
                
                bdr = (240, 140, 40) if is_sel else (225, 230, 240)
                bg = (255, 235, 180) if is_sel else ((250, 252, 255) if rel_idx % 2 == 0 else WHITE)
                pygame.draw.rect(surf, bdr, (lx + 6, iy, lw - 12, 46), 2 if is_sel else 1, border_radius=6)
                pygame.draw.rect(surf, bg, (lx + 7, iy + 1, lw - 14, 44), border_radius=5)
                
                icon = gfx.get_item_sprite(name, (30, 30))
                surf.blit(icon, (lx + 14, iy + 8))

                itxt = gfx.fonts["regular"].render(name, True, (200, 80, 0) if is_sel else UI_TEXT)
                ptxt = gfx.fonts["regular"].render(f"${price}", True, (40, 140, 60))
                surf.blit(itxt, (lx + 52, iy + 12))
                surf.blit(ptxt, (lx + lw - ptxt.get_width() - 16, iy + 12))
        else:
            sell_items = self.get_sellable_items()
            total_items = len(sell_items)
            if not sell_items:
                no_txt = gfx.fonts["regular"].render("Your Bag has no items to sell!", True, UI_TEXT_MUTED)
                surf.blit(no_txt, (lx + (lw - no_txt.get_width()) // 2, ly + 160))
            else:
                visible_items = sell_items[self.scroll_offset : self.scroll_offset + 7]
                for rel_idx, (name, count, data, sell_price) in enumerate(visible_items):
                    actual_idx = self.scroll_offset + rel_idx
                    is_sel = (actual_idx == self.selected_idx)
                    iy = ly + 8 + rel_idx * 52

                    bdr = (240, 140, 40) if is_sel else (225, 230, 240)
                    bg = (255, 235, 180) if is_sel else ((250, 252, 255) if rel_idx % 2 == 0 else WHITE)
                    pygame.draw.rect(surf, bdr, (lx + 6, iy, lw - 12, 46), 2 if is_sel else 1, border_radius=6)
                    pygame.draw.rect(surf, bg, (lx + 7, iy + 1, lw - 14, 44), border_radius=5)

                    icon = gfx.get_item_sprite(name, (30, 30))
                    surf.blit(icon, (lx + 14, iy + 8))

                    itxt = gfx.fonts["regular"].render(name, True, (200, 80, 0) if is_sel else UI_TEXT)
                    cnt_lbl = gfx.fonts["small"].render(f"x{count}", True, UI_TEXT_MUTED)
                    ptxt = gfx.fonts["regular"].render(f"+${sell_price}", True, (30, 140, 50))
                    surf.blit(itxt, (lx + 52, iy + 5))
                    surf.blit(cnt_lbl, (lx + 52, iy + 25))
                    surf.blit(ptxt, (lx + lw - ptxt.get_width() - 16, iy + 12))

        # Scroll indicator
        if total_items > 7:
            scr_info = gfx.fonts["small"].render(f"▲ ▼ ({self.selected_idx + 1}/{total_items})", True, (200, 80, 0))
            surf.blit(scr_info, (lx + lw - scr_info.get_width() - 14, ly + lh - 18))

        # Right Detail Box
        rx, ry, rw, rh = 430, 92, 340, 385
        pygame.draw.rect(surf, UI_BORDER_DARK, (rx - 2, ry - 2, rw + 4, rh + 4), border_radius=8)
        pygame.draw.rect(surf, WHITE, (rx, ry, rw, rh), border_radius=6)

        curr_name, curr_data, curr_price_str = None, None, ""
        if self.mode == "BUY" and self.items_for_sale:
            curr_name = self.items_for_sale[self.selected_idx]
            curr_data = ITEMS[curr_name]
            curr_price_str = f"Buy Price: ${curr_data.get('price', 0)}"
        elif self.mode == "SELL":
            sell_items = self.get_sellable_items()
            if sell_items and 0 <= self.selected_idx < len(sell_items):
                curr_name, count, curr_data, sell_price = sell_items[self.selected_idx]
                curr_price_str = f"Sell Value: ${sell_price} (In Bag: {count})"

        if curr_name and curr_data:
            spr = gfx.get_item_sprite(curr_name, (48, 48))
            surf.blit(spr, (rx + 16, ry + 16))

            surf.blit(gfx.fonts["large"].render(curr_name, True, (30, 50, 90)), (rx + 72, ry + 16))
            surf.blit(gfx.fonts["small"].render(f"Category: {curr_data.get('category', 'item').upper()}", True, (200, 80, 0)), (rx + 72, ry + 42))
            surf.blit(gfx.fonts["small"].render(curr_price_str, True, (40, 140, 60)), (rx + 72, ry + 58))

            # Purpose & Description
            pygame.draw.rect(surf, (246, 249, 255), (rx + 12, ry + 84, rw - 24, 135), border_radius=6)
            surf.blit(gfx.fonts["small"].render("📖 PURPOSE & EFFECT:", True, (40, 80, 180)), (rx + 20, ry + 92))

            words = curr_data.get("desc", "").split(" ")
            lines, cur = [], ""
            for w in words:
                test = cur + (" " if cur else "") + w
                if gfx.fonts["regular"].size(test)[0] < rw - 50:
                    cur = test
                else:
                    lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)
            for l_idx, line_str in enumerate(lines[:5]):
                surf.blit(gfx.fonts["regular"].render(line_str, True, UI_TEXT), (rx + 20, ry + 114 + l_idx * 21))

            # Usage
            pygame.draw.rect(surf, (255, 250, 242), (rx + 12, ry + 228, rw - 24, 95), border_radius=6)
            surf.blit(gfx.fonts["small"].render("⚡ HOW TO USE:", True, (210, 80, 20)), (rx + 20, ry + 234))

            uwords = curr_data.get("usage", "Select to transact.").split(" ")
            ulines, ucur = [], ""
            for w in uwords:
                utest = ucur + (" " if ucur else "") + w
                if gfx.fonts["regular"].size(utest)[0] < rw - 50:
                    ucur = utest
                else:
                    ulines.append(ucur)
                    ucur = w
            if ucur:
                ulines.append(ucur)
            for ul_idx, uline_str in enumerate(ulines[:3]):
                surf.blit(gfx.fonts["regular"].render(uline_str, True, (80, 70, 60)), (rx + 20, ry + 256 + ul_idx * 21))

            cue_txt = "Press [Z] to Buy 1  [X]: Exit" if self.mode == "BUY" else "Press [Z] to Sell 1 for Cash!  [X]: Exit"
            cue = gfx.fonts["small"].render(cue_txt, True, (40, 120, 220) if self.mode == "BUY" else (30, 140, 50))
            surf.blit(cue, (rx + (rw - cue.get_width()) // 2, ry + 348))
        else:
            empty_det = gfx.fonts["regular"].render("No item selected", True, UI_TEXT_MUTED)
            surf.blit(empty_det, (rx + (rw - empty_det.get_width()) // 2, ry + 160))

        # Bottom message box
        bx, by, bw, bh = 30, 490, SCREEN_WIDTH - 60, 80
        pygame.draw.rect(surf, UI_BORDER_DARK, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=8)
        pygame.draw.rect(surf, UI_BG, (bx, by, bw, bh), border_radius=6)
        surf.blit(gfx.fonts["regular"].render(self.message, True, UI_TEXT), (bx + 20, by + 28))
