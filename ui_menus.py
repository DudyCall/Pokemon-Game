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
    Title screen with interactive save slot carousel preview.
    Allows cycling through all 3 save slots directly on the main screen,
    loading any slot instantly, or starting a new adventure in any slot.
    """
    def __init__(self):
        self.timer = 0.0
        self.starter_index = 0
        self.starters = ["Charmander", "Squirtle", "Bulbasaur", "Pikachu"]
        self.menu_options = ["CONTINUE", "ALL_SLOTS", "NEW_GAME"]
        self.selected_idx = 0
        self.slot_preview_idx = 0 # 0: Slot 1, 1: Slot 2, 2: Slot 3
        self.slots = []
        self.has_save = False
        self.refresh_save_status()

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
                    sound_mgr.play_sfx("select")
                elif any(event.key == k for k in KEY_RIGHT):
                    self.slot_preview_idx = (self.slot_preview_idx + 1) % len(self.slots)
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
                    # Slot is empty -> start new game in this slot
                    return ("NEW_GAME", chosen_slot_num)
            elif chosen_opt == "ALL_SLOTS":
                return ("SELECT_SLOT", chosen_slot_num)
            elif chosen_opt == "NEW_GAME":
                return ("NEW_GAME", chosen_slot_num)

        return None

    def update(self, dt):
        self.timer += dt
        self.starter_index = int(self.timer / 2.0) % len(self.starters)

    def draw(self, surf):
        # Radiant Gradient Background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            col = (
                int(24 + 16 * ratio),
                int(32 + 24 * ratio),
                int(64 + 48 * ratio)
            )
            pygame.draw.line(surf, col, (0, y), (SCREEN_WIDTH, y))

        # Title Card
        title_y = 45 + int(math.sin(self.timer * 2.0) * 5)
        title_txt = gfx.fonts["title"].render("POKÉMON", True, (255, 215, 0)) # Gold
        sub_txt = gfx.fonts["large"].render("PYGAME EDITION", True, (240, 60, 60)) # Red
        
        # Shadow & Glow
        surf.blit(gfx.fonts["title"].render("POKÉMON", True, (30, 30, 40)), (SCREEN_WIDTH // 2 - title_txt.get_width() // 2 + 4, title_y + 4))
        surf.blit(title_txt, (SCREEN_WIDTH // 2 - title_txt.get_width() // 2, title_y))
        surf.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, title_y + 50))

        if self.has_save:
            # 1. CONTINUE (Slot Carousel Card)
            cur_slot = self.slots[self.slot_preview_idx]
            cur_num = self.slot_preview_idx + 1
            is_sel_cont = (self.selected_idx == 0)
            
            cw, ch = 520, 135
            cx = (SCREEN_WIDTH - cw) // 2
            cy = 180

            pygame.draw.rect(surf, (240, 140, 40) if is_sel_cont else UI_BORDER_LIGHT, (cx - 2, cy - 2, cw + 4, ch + 4), border_radius=12)
            pygame.draw.rect(surf, (255, 248, 230) if is_sel_cont else WHITE, (cx, cy, cw, ch), border_radius=10)

            # Slot Header with Arrow Indicators & Counter
            header_txt = gfx.fonts["large"].render(f"CONTINUE GAME  ◀  SLOT {cur_num:02d} / {len(self.slots)}  ▶", True, (220, 80, 0) if is_sel_cont else UI_TEXT)
            surf.blit(header_txt, (cx + 20, cy + 12))

            if cur_slot.get("exists"):
                # Lead Pokémon Sprite
                lead_sp = gfx.get_pokemon_sprite(cur_slot.get("lead_species", "Pikachu"), is_back=False, size=(75, 75))
                surf.blit(lead_sp, (cx + 15, cy + 45))

                # Trainer & Location Details
                t_name = cur_slot.get("trainer_name", "Red")
                t_gender = cur_slot.get("gender", "Boy")
                info_l1 = gfx.fonts["regular"].render(f"Trainer: {t_name} ({t_gender})  |  Map: {cur_slot.get('map', 'Pallet Town')}", True, UI_TEXT)
                info_l2 = gfx.fonts["regular"].render(f"Lead: {cur_slot.get('lead_name', 'Pokémon')} (Lv.{cur_slot.get('lead_level', 5)})", True, (40, 120, 220))
                info_l3 = gfx.fonts["small"].render(f"Team: {cur_slot.get('party_count', 1)} | Money: ${cur_slot.get('money', 0)} | Pokédex: {cur_slot.get('caught_count', 0)}/151 | {cur_slot.get('timestamp', '')}", True, UI_TEXT_MUTED)
                
                surf.blit(info_l1, (cx + 98, cy + 46))
                surf.blit(info_l2, (cx + 98, cy + 72))
                surf.blit(info_l3, (cx + 98, cy + 98))
            else:
                # Empty Slot state
                emp_txt = gfx.fonts["large"].render(f"- Empty Save Slot {cur_num} -", True, (160, 170, 185))
                emp_sub = gfx.fonts["regular"].render("Press [Enter] to start a new adventure in Slot " + str(cur_num), True, UI_TEXT_MUTED)
                surf.blit(emp_txt, (cx + (cw - emp_txt.get_width()) // 2, cy + 50))
                surf.blit(emp_sub, (cx + (cw - emp_sub.get_width()) // 2, cy + 85))

            # 2. ALL SAVE SLOTS Button
            is_sel_all = (self.selected_idx == 1)
            by_all = cy + ch + 18
            bh_btn = 52
            pygame.draw.rect(surf, (240, 140, 40) if is_sel_all else UI_BORDER_LIGHT, (cx - 2, by_all - 2, cw + 4, bh_btn + 4), border_radius=10)
            pygame.draw.rect(surf, (255, 248, 230) if is_sel_all else WHITE, (cx, by_all, cw, bh_btn), border_radius=8)
            all_txt = gfx.fonts["medium"].render("VIEW ALL 99 SAVE SLOTS", True, (220, 80, 0) if is_sel_all else UI_TEXT)
            surf.blit(all_txt, (cx + (cw - all_txt.get_width()) // 2, by_all + 14))

            # 3. NEW GAME Button
            is_sel_new = (self.selected_idx == 2)
            by_new = by_all + bh_btn + 14
            pygame.draw.rect(surf, (240, 140, 40) if is_sel_new else UI_BORDER_LIGHT, (cx - 2, by_new - 2, cw + 4, bh_btn + 4), border_radius=10)
            pygame.draw.rect(surf, (255, 248, 230) if is_sel_new else WHITE, (cx, by_new, cw, bh_btn), border_radius=8)
            new_txt = gfx.fonts["medium"].render("START NEW ADVENTURE", True, (220, 80, 0) if is_sel_new else UI_TEXT)
            surf.blit(new_txt, (cx + (cw - new_txt.get_width()) // 2, by_new + 14))

            ctrl_hint = gfx.fonts["small"].render("Up/Down: Choose Menu  |  Left/Right: Switch Slot (1-99)  |  [Enter]: Start", True, LIGHT_GRAY)
            surf.blit(ctrl_hint, (SCREEN_WIDTH // 2 - ctrl_hint.get_width() // 2, 560))

        else:
            # Featured Starter Sprite for fresh start
            feat_species = self.starters[self.starter_index]
            p_surf = gfx.get_pokemon_sprite(feat_species, is_back=False, size=(200, 200))
            surf.blit(p_surf, (SCREEN_WIDTH // 2 - 100, 195))

            # Blinking "PRESS ENTER OR Z TO START"
            if int(self.timer * 2) % 2 == 0:
                start_txt = gfx.fonts["medium"].render("PRESS [ENTER] OR [Z] TO START", True, WHITE)
                surf.blit(start_txt, (SCREEN_WIDTH // 2 - start_txt.get_width() // 2, 460))
                
            ctrl_hint = gfx.fonts["small"].render("Arrows/D-Pad: Move  |  Z/B: Confirm  |  X/A: Back  |  C/Start: Menu  |  F5/Select: Save", True, LIGHT_GRAY)
            surf.blit(ctrl_hint, (SCREEN_WIDTH // 2 - ctrl_hint.get_width() // 2, 545))

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
        self.items_for_sale = [
            "Poke Ball", "Great Ball", "Ultra Ball",
            "Potion", "Super Potion", "Max Potion", "Revive",
            "Antidote", "Paralyze Heal", "Awakening", "Burn Heal",
            "Rare Candy", "Escape Rope", "Move Reroll Disk",
            "Moon Stone", "Fire Stone", "Water Stone", "Thunder Stone", "Leaf Stone"
        ]
        self.selected_idx = 0
        self.scroll_offset = 0
        self.message = "Welcome to PokéMart! What would you like to buy?"

    def _adjust_scroll(self):
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + 7:
            self.scroll_offset = self.selected_idx - 6

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
            
        if any(event.key == k for k in KEY_UP):
            self.selected_idx = (self.selected_idx - 1) % len(self.items_for_sale)
            self._adjust_scroll()
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_DOWN):
            self.selected_idx = (self.selected_idx + 1) % len(self.items_for_sale)
            self._adjust_scroll()
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_CANCEL):
            sound_mgr.play_sfx("cancel")
            return "EXIT"
        elif any(event.key == k for k in KEY_CONFIRM):
            item_name = self.items_for_sale[self.selected_idx]
            price = ITEMS[item_name]["price"]
            if self.inventory.money >= price:
                self.inventory.money -= price
                self.inventory.add_item(item_name, 1)
                sound_mgr.play_sfx("confirm")
                self.message = f"Bought 1 {item_name} for ${price}!"
            else:
                sound_mgr.play_sfx("cancel")
                self.message = "You don't have enough money for that!"
        return None

    def draw(self, surf):
        surf.fill((235, 240, 248))
        head = gfx.fonts["title"].render("POKÉMART & ITEM CATALOGUE", True, (40, 120, 220))
        money_txt = gfx.fonts["large"].render(f"💰 Money: ${self.inventory.money}", True, (40, 140, 60))
        surf.blit(head, (30, 20))
        surf.blit(money_txt, (SCREEN_WIDTH - money_txt.get_width() - 30, 25))

        # Items List (Left Box)
        lx, ly, lw, lh = 30, 85, 380, 390
        pygame.draw.rect(surf, UI_BORDER_DARK, (lx - 2, ly - 2, lw + 4, lh + 4), border_radius=8)
        pygame.draw.rect(surf, WHITE, (lx, ly, lw, lh), border_radius=6)

        visible_items = self.items_for_sale[self.scroll_offset : self.scroll_offset + 7]
        for rel_idx, name in enumerate(visible_items):
            actual_idx = self.scroll_offset + rel_idx
            is_sel = (actual_idx == self.selected_idx)
            iy = ly + 10 + rel_idx * 52
            price = ITEMS[name]["price"]
            
            bdr = (240, 140, 40) if is_sel else (225, 230, 240)
            bg = (255, 235, 180) if is_sel else ((250, 252, 255) if rel_idx % 2 == 0 else WHITE)
            pygame.draw.rect(surf, bdr, (lx + 6, iy, lw - 12, 46), 2 if is_sel else 1, border_radius=6)
            pygame.draw.rect(surf, bg, (lx + 7, iy + 1, lw - 14, 44), border_radius=5)
            
            # Icon
            icon = gfx.get_item_sprite(name, (30, 30))
            surf.blit(icon, (lx + 14, iy + 8))

            itxt = gfx.fonts["regular"].render(name, True, (200, 80, 0) if is_sel else UI_TEXT)
            ptxt = gfx.fonts["regular"].render(f"${price}", True, (40, 140, 60))
            surf.blit(itxt, (lx + 52, iy + 12))
            surf.blit(ptxt, (lx + lw - ptxt.get_width() - 16, iy + 12))

        # Scroll indicator
        if len(self.items_for_sale) > 7:
            scr_info = gfx.fonts["small"].render(f"▲ ▼ ({self.selected_idx + 1}/{len(self.items_for_sale)})", True, (200, 80, 0))
            surf.blit(scr_info, (lx + lw - scr_info.get_width() - 14, ly + lh - 20))

        # Right Detail & Explanation Box
        rx, ry, rw, rh = 430, 85, 340, 390
        curr_name = self.items_for_sale[self.selected_idx]
        data = ITEMS[curr_name]
        pygame.draw.rect(surf, UI_BORDER_DARK, (rx - 2, ry - 2, rw + 4, rh + 4), border_radius=8)
        pygame.draw.rect(surf, WHITE, (rx, ry, rw, rh), border_radius=6)

        # Header with icon
        spr = gfx.get_item_sprite(curr_name, (48, 48))
        surf.blit(spr, (rx + 16, ry + 16))

        surf.blit(gfx.fonts["large"].render(curr_name, True, (30, 50, 90)), (rx + 72, ry + 16))
        surf.blit(gfx.fonts["small"].render(f"Category: {data.get('category', 'item').upper()}", True, (200, 80, 0)), (rx + 72, ry + 44))
        surf.blit(gfx.fonts["small"].render(f"In Bag: {self.inventory.get_count(curr_name)}  |  Price: ${data.get('price', 0)}", True, (40, 140, 60)), (rx + 72, ry + 60))

        # Purpose & Description
        pygame.draw.rect(surf, (246, 249, 255), (rx + 12, ry + 86, rw - 24, 140), border_radius=6)
        surf.blit(gfx.fonts["small"].render("📖 PURPOSE & EFFECT:", True, (40, 80, 180)), (rx + 20, ry + 94))

        words = data.get("desc", "").split(" ")
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
            ltxt = gfx.fonts["regular"].render(line_str, True, UI_TEXT)
            surf.blit(ltxt, (rx + 20, ry + 118 + l_idx * 22))

        # Usage
        pygame.draw.rect(surf, (255, 250, 242), (rx + 12, ry + 236, rw - 24, 100), border_radius=6)
        surf.blit(gfx.fonts["small"].render("⚡ HOW TO USE:", True, (210, 80, 20)), (rx + 20, ry + 244))

        uwords = data.get("usage", "Select to purchase.").split(" ")
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
            ultxt = gfx.fonts["regular"].render(uline_str, True, (80, 70, 60))
            surf.blit(ultxt, (rx + 20, ry + 268 + ul_idx * 22))

        cue = gfx.fonts["small"].render("Press [Z] to Buy  [X]: Exit", True, (40, 120, 220))
        surf.blit(cue, (rx + (rw - cue.get_width()) // 2, ry + 354))

        # Bottom message box
        bx, by, bw, bh = 30, 490, SCREEN_WIDTH - 60, 80
        pygame.draw.rect(surf, UI_BORDER_DARK, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=8)
        pygame.draw.rect(surf, UI_BG, (bx, by, bw, bh), border_radius=6)
        surf.blit(gfx.fonts["regular"].render(self.message, True, UI_TEXT), (bx + 20, by + 28))
