"""
ui_manager.py - Comprehensive UI screens: Title, Starter Choice, Pause Start Menu,
Pokédex, Party Summary, PokéMart Shop, and Dialogue boxes.
"""
import pygame
import math
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

            # Slot Header with Arrow Indicators & Dots
            slot_dots = " ".join(["●" if i == self.slot_preview_idx else "○" for i in range(3)])
            header_txt = gfx.fonts["large"].render(f"CONTINUE GAME  ◀  SLOT {cur_num} / 3  ▶", True, (220, 80, 0) if is_sel_cont else UI_TEXT)
            surf.blit(header_txt, (cx + 20, cy + 12))
            
            dots_txt = gfx.fonts["small"].render(slot_dots, True, (200, 80, 0) if is_sel_cont else UI_TEXT_MUTED)
            surf.blit(dots_txt, (cx + cw - dots_txt.get_width() - 20, cy + 16))

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
                emp_txt = gfx.fonts["large"].render("- Empty Save Slot -", True, (160, 170, 185))
                emp_sub = gfx.fonts["regular"].render("Press [Enter] to start a new adventure in Slot " + str(cur_num), True, UI_TEXT_MUTED)
                surf.blit(emp_txt, (cx + (cw - emp_txt.get_width()) // 2, cy + 50))
                surf.blit(emp_sub, (cx + (cw - emp_sub.get_width()) // 2, cy + 85))

            # 2. ALL SAVE SLOTS Button
            is_sel_all = (self.selected_idx == 1)
            by_all = cy + ch + 18
            bh_btn = 52
            pygame.draw.rect(surf, (240, 140, 40) if is_sel_all else UI_BORDER_LIGHT, (cx - 2, by_all - 2, cw + 4, bh_btn + 4), border_radius=10)
            pygame.draw.rect(surf, (255, 248, 230) if is_sel_all else WHITE, (cx, by_all, cw, bh_btn), border_radius=8)
            all_txt = gfx.fonts["medium"].render("VIEW ALL 3 SAVE SLOTS", True, (220, 80, 0) if is_sel_all else UI_TEXT)
            surf.blit(all_txt, (cx + (cw - all_txt.get_width()) // 2, by_all + 14))

            # 3. NEW GAME Button
            is_sel_new = (self.selected_idx == 2)
            by_new = by_all + bh_btn + 14
            pygame.draw.rect(surf, (240, 140, 40) if is_sel_new else UI_BORDER_LIGHT, (cx - 2, by_new - 2, cw + 4, bh_btn + 4), border_radius=10)
            pygame.draw.rect(surf, (255, 248, 230) if is_sel_new else WHITE, (cx, by_new, cw, bh_btn), border_radius=8)
            new_txt = gfx.fonts["medium"].render("START NEW ADVENTURE", True, (220, 80, 0) if is_sel_new else UI_TEXT)
            surf.blit(new_txt, (cx + (cw - new_txt.get_width()) // 2, by_new + 14))

            ctrl_hint = gfx.fonts["small"].render("Up/Down: Choose Menu  |  Left/Right: Switch Slot (1-3)  |  [Enter]: Start", True, LIGHT_GRAY)
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
    def __init__(self, mode="LOAD", active_slot=1, player=None, party=None, inventory=None, pokedex=None, world=None, pc_box=None):
        self.mode = mode # "LOAD", "NEW_GAME", "SAVE"
        self.active_slot = active_slot
        self.player = player
        self.party = party
        self.inventory = inventory
        self.pokedex = pokedex
        self.world = world
        self.pc_box = pc_box
        self.selected_idx = max(0, min(2, active_slot - 1))
        self.slots = []
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
        if event.type != pygame.KEYDOWN:
            return None

        # Modal Input
        if self.confirm_modal:
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
                        SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world, slot=self.target_slot_for_modal, pc_box=self.pc_box)
                        self.refresh_slots()
                        return ("SAVED", self.target_slot_for_modal)
                else:
                    self.confirm_modal = False
                    sound_mgr.play_sfx("cancel")
            return None

        # Main Slot Selection Input
        if any(event.key == k for k in KEY_UP):
            self.selected_idx = (self.selected_idx - 1) % len(self.slots)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_DOWN):
            self.selected_idx = (self.selected_idx + 1) % len(self.slots)
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
                    SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world, slot=chosen_slot, pc_box=self.pc_box)
                    sound_mgr.play_sfx("confirm")
                    self.refresh_slots()
                    return ("SAVED", chosen_slot)

        return None

    def update(self, dt):
        if self.status_timer > 0:
            self.status_timer = max(0.0, self.status_timer - dt)
            if self.status_timer == 0:
                self.status_msg = ""

    def draw(self, surf):
        surf.fill((235, 240, 248))

        # Header Titles based on mode
        if self.mode == "LOAD":
            title_str = "LOAD SAVE FILE"
            subtitle_str = "Select a save slot to continue your journey"
        elif self.mode == "NEW_GAME":
            title_str = "NEW GAME - SELECT SLOT"
            subtitle_str = "Select a slot to start your adventure"
        else: # SAVE
            title_str = "SAVE GAME PROGRESS"
            subtitle_str = f"Select a slot to save progress (Current: Slot {self.active_slot})"

        head = gfx.fonts["title"].render(title_str, True, (220, 80, 0) if self.mode == "SAVE" else UI_TEXT)
        sub = gfx.fonts["regular"].render(subtitle_str, True, UI_TEXT_MUTED)
        surf.blit(head, (SCREEN_WIDTH // 2 - head.get_width() // 2, 24))
        surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 70))

        # 3 Save Slot Cards
        card_w, card_h = 700, 115
        start_x = (SCREEN_WIDTH - card_w) // 2

        for i, s_data in enumerate(self.slots):
            slot_num = i + 1
            card_y = 110 + i * 135
            is_sel = (i == self.selected_idx)
            is_active = (self.mode == "SAVE" and slot_num == self.active_slot)

            # Card border and fill
            bdr_col = (240, 140, 40) if is_sel else (UI_BORDER_DARK if is_active else UI_BORDER_LIGHT)
            bg_col = (255, 248, 230) if is_sel else WHITE
            pygame.draw.rect(surf, bdr_col, (start_x - 2, card_y - 2, card_w + 4, card_h + 4), border_radius=12)
            pygame.draw.rect(surf, bg_col, (start_x, card_y, card_w, card_h), border_radius=10)

            # Slot Pill Badge
            slot_pill_col = (220, 80, 0) if is_sel else (40, 120, 220)
            pygame.draw.rect(surf, slot_pill_col, (start_x + 16, card_y + 14, 80, 26), border_radius=6)
            slot_lbl = gfx.fonts["small"].render(f"SLOT {slot_num}", True, WHITE)
            surf.blit(slot_lbl, (start_x + 16 + (80 - slot_lbl.get_width()) // 2, card_y + 19))

            if is_active:
                # Active slot badge
                pygame.draw.rect(surf, (40, 160, 60), (start_x + 104, card_y + 14, 90, 26), border_radius=6)
                act_lbl = gfx.fonts["small"].render("ACTIVE", True, WHITE)
                surf.blit(act_lbl, (start_x + 104 + (90 - act_lbl.get_width()) // 2, card_y + 19))

            if s_data.get("exists"):
                # Lead Pokemon Sprite
                lead_species = s_data.get("lead_species", "Pikachu")
                sp_surf = gfx.get_pokemon_sprite(lead_species, is_back=False, size=(75, 75))
                surf.blit(sp_surf, (start_x + 22, card_y + 38))

                # Main Details
                lead_name = s_data.get("lead_name", "Pokémon")
                lead_lvl = s_data.get("lead_level", 5)
                loc_name = s_data.get("map", "Pallet Town")
                lead_txt = gfx.fonts["large"].render(f"{lead_name} (Lv. {lead_lvl})", True, (200, 80, 0) if is_sel else UI_TEXT)
                loc_txt = gfx.fonts["regular"].render(f"Location: {loc_name}", True, UI_TEXT)
                surf.blit(lead_txt, (start_x + 115, card_y + 46))
                surf.blit(loc_txt, (start_x + 115, card_y + 76))

                # Stats on the right
                team_count = s_data.get("party_count", 1)
                money_val = s_data.get("money", 0)
                caught_val = s_data.get("caught_count", 0)
                stats_str = f"Team: {team_count} | Money: ${money_val} | Dex: {caught_val}/151"
                stats_txt = gfx.fonts["small"].render(stats_str, True, UI_TEXT_MUTED)
                surf.blit(stats_txt, (start_x + 360, card_y + 48))

                # Timestamp
                time_str = s_data.get("timestamp", "")
                if time_str:
                    time_txt = gfx.fonts["small"].render(f"Saved: {time_str}", True, UI_TEXT_MUTED)
                    surf.blit(time_txt, (start_x + 360, card_y + 76))
            else:
                # Empty Slot presentation
                empty_txt = gfx.fonts["large"].render("+ [ EMPTY SAVE SLOT ]", True, (200, 80, 0) if is_sel else UI_TEXT_MUTED)
                sub_empty = gfx.fonts["regular"].render("No journey recorded. Ready for a new adventure!", True, UI_TEXT_MUTED)
                surf.blit(empty_txt, (start_x + 115, card_y + 42))
                surf.blit(sub_empty, (start_x + 115, card_y + 74))

        # Status message
        if self.status_msg:
            st_surf = gfx.fonts["regular"].render(self.status_msg, True, (220, 40, 40))
            surf.blit(st_surf, (SCREEN_WIDTH // 2 - st_surf.get_width() // 2, 525))

        # Bottom Hint Bar
        nav_hint = gfx.fonts["small"].render("Up/Down: Select Slot  |  [Z / Enter]: Confirm  |  [X / ESC]: Cancel", True, UI_TEXT_MUTED)
        surf.blit(nav_hint, (SCREEN_WIDTH // 2 - nav_hint.get_width() // 2, 560))

        # Overwrite Confirmation Modal Dialog
        if self.confirm_modal:
            # Semi-transparent backdrop
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surf.blit(overlay, (0, 0))

            # Modal Box
            mw, mh = 480, 230
            mx = (SCREEN_WIDTH - mw) // 2
            my = (SCREEN_HEIGHT - mh) // 2
            pygame.draw.rect(surf, (220, 60, 60), (mx - 2, my - 2, mw + 4, mh + 4), border_radius=12)
            pygame.draw.rect(surf, WHITE, (mx, my, mw, mh), border_radius=10)

            # Warning Header
            warn_title = gfx.fonts["large"].render(f"OVERWRITE SLOT {self.target_slot_for_modal}?", True, (220, 40, 40))
            surf.blit(warn_title, (mx + (mw - warn_title.get_width()) // 2, my + 24))

            # Message
            m1 = gfx.fonts["regular"].render("This save slot already contains adventure data!", True, UI_TEXT)
            m2 = gfx.fonts["small"].render("Overwriting will permanently erase the existing save.", True, UI_TEXT_MUTED)
            surf.blit(m1, (mx + (mw - m1.get_width()) // 2, my + 75))
            surf.blit(m2, (mx + (mw - m2.get_width()) // 2, my + 105))

            # [YES - OVERWRITE] / [NO - CANCEL] buttons
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
    def __init__(self, player, party, inventory, pokedex, slot=1, pc_box=None):
        self.player = player
        self.party = party
        self.inventory = inventory
        self.pokedex = pokedex
        self.slot = slot
        self.pc_box = pc_box
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
            SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, world, slot=self.slot, pc_box=self.pc_box)
            sound_mgr.play_sfx("confirm")
            self.state = "SAVED"
            self.timer = 0.0
        elif self.state == "SAVED" and self.timer >= 1.2:
            # Automatically close after 1.2 seconds if not already closed
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
        self.options = ["POKÉDEX", "POKÉMON", "BAG", "MAP", "PC BOX", "TRAINER", "SAVE", "EXIT"]
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
        mw, mh = 210, 340
        mx = SCREEN_WIDTH - mw - 20
        my = 20
        
        pygame.draw.rect(surf, UI_BORDER_DARK, (mx - 2, my - 2, mw + 4, mh + 4), border_radius=10)
        pygame.draw.rect(surf, UI_BG, (mx, my, mw, mh), border_radius=8)
        
        for i, opt in enumerate(self.options):
            iy = my + 14 + i * 40
            is_sel = (i == self.selected_idx)
            
            if is_sel:
                pygame.draw.rect(surf, (255, 235, 180), (mx + 8, iy - 4, mw - 16, 34), border_radius=6)
                pygame.draw.rect(surf, (240, 140, 40), (mx + 8, iy - 4, mw - 16, 34), 2, border_radius=6)
                
            txt = gfx.fonts["regular"].render(opt, True, (200, 80, 0) if is_sel else UI_TEXT)
            surf.blit(txt, (mx + 20, iy))


class PokedexScreen:
    def __init__(self, pokedex):
        self.pokedex = pokedex
        self.species_list = sorted(POKEMON_SPECIES.keys(), key=lambda s: POKEMON_SPECIES[s]["id"])
        self.selected_idx = 0

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
            
        if any(event.key == k for k in KEY_UP):
            self.selected_idx = (self.selected_idx - 1) % len(self.species_list)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_DOWN):
            self.selected_idx = (self.selected_idx + 1) % len(self.species_list)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_LEFT):
            self.selected_idx = max(0, self.selected_idx - 10)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_RIGHT):
            self.selected_idx = min(len(self.species_list) - 1, self.selected_idx + 10)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_CANCEL + KEY_CONFIRM):
            sound_mgr.play_sfx("cancel")
            return "BACK"
        return None

    def draw(self, surf):
        surf.fill((235, 240, 248))
        
        # Header
        head = gfx.fonts["title"].render("POKÉDEX", True, (220, 40, 40))
        seen_count = len(self.pokedex.seen)
        caught_count = len(self.pokedex.caught)
        sub = gfx.fonts["regular"].render(f"Seen: {seen_count}   Caught: {caught_count} / {len(self.species_list)}", True, UI_TEXT_MUTED)
        surf.blit(head, (30, 20))
        surf.blit(sub, (30, 65))

        # Left list of Pokemon
        lw, lh = 280, 460
        lx, ly = 30, 105
        pygame.draw.rect(surf, UI_BORDER_DARK, (lx - 2, ly - 2, lw + 4, lh + 4), border_radius=8)
        pygame.draw.rect(surf, WHITE, (lx, ly, lw, lh), border_radius=6)
        
        # Display window of 10 items
        start_idx = max(0, min(self.selected_idx - 4, len(self.species_list) - 10))
        for i in range(start_idx, min(len(self.species_list), start_idx + 10)):
            name = self.species_list[i]
            data = POKEMON_SPECIES[name]
            p_id = data["id"]
            is_seen = name in self.pokedex.seen
            is_caught = name in self.pokedex.caught
            is_sel = (i == self.selected_idx)
            
            row_y = ly + 10 + (i - start_idx) * 44
            if is_sel:
                pygame.draw.rect(surf, (255, 235, 180), (lx + 6, row_y - 2, lw - 12, 38), border_radius=6)
                pygame.draw.rect(surf, (240, 140, 40), (lx + 6, row_y - 2, lw - 12, 38), 2, border_radius=6)
                
            # Pokeball icon if caught
            if is_caught:
                ball = gfx.item_sprites["Poke Ball"]
                surf.blit(pygame.transform.scale(ball, (18, 18)), (lx + 12, row_y + 8))
            elif is_seen:
                # Dot
                pygame.draw.circle(surf, (140, 140, 140), (lx + 20, row_y + 16), 4)

            display_name = name if is_seen else "----------"
            row_txt = gfx.fonts["regular"].render(f"No.{p_id:03d} {display_name}", True, (200, 80, 0) if is_sel else UI_TEXT)
            surf.blit(row_txt, (lx + 38, row_y + 6))

        # Right Preview Card
        curr_name = self.species_list[self.selected_idx]
        curr_data = POKEMON_SPECIES[curr_name]
        is_seen = curr_name in self.pokedex.seen
        is_caught = curr_name in self.pokedex.caught

        rx, ry, rw, rh = 340, 105, 430, 460
        pygame.draw.rect(surf, UI_BORDER_DARK, (rx - 2, ry - 2, rw + 4, rh + 4), border_radius=8)
        pygame.draw.rect(surf, WHITE, (rx, ry, rw, rh), border_radius=6)

        if is_seen:
            # Sprite
            p_surf = gfx.get_pokemon_sprite(curr_name, is_back=False, size=(160, 160))
            surf.blit(p_surf, (rx + 20, ry + 20))
            
            # Species Details
            no_txt = gfx.fonts["regular"].render(f"No. {curr_data['id']:03d}", True, UI_TEXT_MUTED)
            surf.blit(no_txt, (rx + 200, ry + 30))
            name_txt = gfx.fonts["title"].render(curr_name, True, UI_TEXT)
            surf.blit(name_txt, (rx + 200, ry + 55))
            
            # Types
            for t_idx, t_name in enumerate(curr_data["types"]):
                gfx.draw_type_badge(surf, t_name, rx + 200 + t_idx * 75, ry + 115, width=68, height=24)
                
            # Lore Description Box
            desc_y = ry + 200
            pygame.draw.rect(surf, UI_BG, (rx + 20, desc_y, rw - 40, 120), border_radius=6)
            
            # Word wrap description
            words = curr_data["desc"].split(" ")
            lines = []
            curr_line = ""
            for w in words:
                test = curr_line + (" " if curr_line else "") + w
                if gfx.fonts["regular"].size(test)[0] < rw - 60:
                    curr_line = test
                else:
                    lines.append(curr_line)
                    curr_line = w
            if curr_line:
                lines.append(curr_line)
                
            for l_idx, line_str in enumerate(lines[:4]):
                ltxt = gfx.fonts["regular"].render(line_str, True, UI_TEXT)
                surf.blit(ltxt, (rx + 30, desc_y + 15 + l_idx * 24))
        else:
            unknown_txt = gfx.fonts["large"].render("??? Unknown Pokémon", True, UI_TEXT_MUTED)
            surf.blit(unknown_txt, (rx + (rw - unknown_txt.get_width()) // 2, ry + 200))

        # Bottom navigation hint
        nav_hint = gfx.fonts["small"].render("Up/Down: Scroll  |  Left/Right: Jump 10  |  [X / Enter]: Return", True, UI_TEXT_MUTED)
        surf.blit(nav_hint, (SCREEN_WIDTH - nav_hint.get_width() - 30, 575))

class PartySummaryScreen:
    def __init__(self, party, inventory=None):
        self.party = party
        self.inventory = inventory
        self.selected_idx = 0

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
            
        if any(event.key == k for k in KEY_UP):
            self.selected_idx = (self.selected_idx - 1) % len(self.party)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_DOWN):
            self.selected_idx = (self.selected_idx + 1) % len(self.party)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_CANCEL + KEY_CONFIRM):
            sound_mgr.play_sfx("cancel")
            return "BACK"
        return None

    def draw(self, surf):
        surf.fill((235, 240, 248))
        head = gfx.fonts["title"].render("POKÉMON TEAM", True, UI_TEXT)
        surf.blit(head, (30, 20))
        
        # Display 6 Party slots
        for i, p in enumerate(self.party):
            is_sel = (i == self.selected_idx)
            row_x = 30 + (i % 2) * 380
            row_y = 90 + (i // 2) * 155
            rw, rh = 360, 140
            
            bdr_col = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
            bg_col = (255, 245, 220) if is_sel else WHITE
            pygame.draw.rect(surf, bdr_col, (row_x - 2, row_y - 2, rw + 4, rh + 4), border_radius=10)
            pygame.draw.rect(surf, bg_col, (row_x, row_y, rw, rh), border_radius=8)
            
            # Sprite
            p_surf = gfx.get_pokemon_sprite(p.species, is_back=False, size=(90, 90))
            surf.blit(p_surf, (row_x + 10, row_y + 15))
            
            # Details
            name_txt = gfx.fonts["medium"].render(p.nickname, True, UI_TEXT)
            lvl_txt = gfx.fonts["small"].render(f"Lv. {p.level}", True, UI_TEXT_MUTED)
            surf.blit(name_txt, (row_x + 105, row_y + 15))
            surf.blit(lvl_txt, (row_x + rw - lvl_txt.get_width() - 15, row_y + 18))
            
            # HP Bar
            gfx.draw_hp_bar(surf, row_x + 140, row_y + 50, 190, 10, p.current_hp, p.max_hp)
            hp_lbl = gfx.fonts["small"].render("HP", True, (240, 180, 40))
            surf.blit(hp_lbl, (row_x + 110, row_y + 46))
            
            hp_num = gfx.fonts["small"].render(f"{p.current_hp}/{p.max_hp}", True, UI_TEXT)
            surf.blit(hp_num, (row_x + rw - hp_num.get_width() - 15, row_y + 65))
            
            # Types & Status Badge
            for t_idx, t_name in enumerate(p.types):
                gfx.draw_type_badge(surf, t_name, row_x + 105 + t_idx * 60, row_y + 95, width=54, height=20)
            
            if p.is_fainted():
                gfx.draw_status_badge(surf, "Fainted", row_x + 105 + len(p.types) * 60, row_y + 95, width=48, height=20)
            elif p.status:
                gfx.draw_status_badge(surf, p.status, row_x + 105 + len(p.types) * 60, row_y + 95, width=48, height=20)

class ShopScreen:
    def __init__(self, inventory):
        self.inventory = inventory
        self.items_for_sale = ["Poke Ball", "Great Ball", "Ultra Ball", "Potion", "Super Potion", "Revive", "Antidote"]
        self.selected_idx = 0
        self.message = "Welcome to PokéMart! What would you like to buy?"

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
            
        if any(event.key == k for k in KEY_UP):
            self.selected_idx = (self.selected_idx - 1) % len(self.items_for_sale)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_DOWN):
            self.selected_idx = (self.selected_idx + 1) % len(self.items_for_sale)
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
        head = gfx.fonts["title"].render("POKÉMART", True, (40, 120, 220))
        money_txt = gfx.fonts["large"].render(f"Money: ${self.inventory.money}", True, (40, 140, 60))
        surf.blit(head, (30, 20))
        surf.blit(money_txt, (SCREEN_WIDTH - money_txt.get_width() - 30, 25))

        # Items List
        lx, ly, lw, lh = 30, 90, 420, 380
        pygame.draw.rect(surf, UI_BORDER_DARK, (lx - 2, ly - 2, lw + 4, lh + 4), border_radius=8)
        pygame.draw.rect(surf, WHITE, (lx, ly, lw, lh), border_radius=6)

        for i, name in enumerate(self.items_for_sale):
            is_sel = (i == self.selected_idx)
            iy = ly + 15 + i * 48
            price = ITEMS[name]["price"]
            
            if is_sel:
                pygame.draw.rect(surf, (255, 235, 180), (lx + 6, iy - 4, lw - 12, 40), border_radius=6)
                pygame.draw.rect(surf, (240, 140, 40), (lx + 6, iy - 4, lw - 12, 40), 2, border_radius=6)
                
            itxt = gfx.fonts["regular"].render(name, True, (200, 80, 0) if is_sel else UI_TEXT)
            ptxt = gfx.fonts["regular"].render(f"${price}", True, (40, 140, 60))
            surf.blit(itxt, (lx + 20, iy + 4))
            surf.blit(ptxt, (lx + lw - ptxt.get_width() - 20, iy + 4))

        # Right Detail Box
        rx, ry, rw, rh = 470, 90, 300, 380
        curr_name = self.items_for_sale[self.selected_idx]
        data = ITEMS[curr_name]
        pygame.draw.rect(surf, UI_BORDER_DARK, (rx - 2, ry - 2, rw + 4, rh + 4), border_radius=8)
        pygame.draw.rect(surf, WHITE, (rx, ry, rw, rh), border_radius=6)

        surf.blit(gfx.fonts["large"].render(curr_name, True, UI_TEXT), (rx + 20, ry + 20))
        surf.blit(gfx.fonts["regular"].render(f"In Bag: {self.inventory.get_count(curr_name)}", True, UI_TEXT_MUTED), (rx + 20, ry + 60))

        # Description
        words = data["desc"].split(" ")
        lines = []
        curr_line = ""
        for w in words:
            test = curr_line + (" " if curr_line else "") + w
            if gfx.fonts["regular"].size(test)[0] < rw - 40:
                curr_line = test
            else:
                lines.append(curr_line)
                curr_line = w
        if curr_line:
            lines.append(curr_line)
        for l_idx, line_str in enumerate(lines):
            ltxt = gfx.fonts["regular"].render(line_str, True, UI_TEXT)
            surf.blit(ltxt, (rx + 20, ry + 110 + l_idx * 26))

        # Bottom message box
        bx, by, bw, bh = 30, 490, SCREEN_WIDTH - 60, 80
        pygame.draw.rect(surf, UI_BORDER_DARK, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=8)
        pygame.draw.rect(surf, UI_BG, (bx, by, bw, bh), border_radius=6)
        surf.blit(gfx.fonts["regular"].render(self.message, True, UI_TEXT), (bx + 20, by + 28))

class DialogueBox:
    def __init__(self, speaker_name, text, on_complete=None):
        self.speaker = speaker_name
        self.full_text = text
        self.visible_chars = 0
        self.speed = 40.0
        self.on_complete = on_complete
        self.finished = False

    def update(self, dt):
        if not self.finished:
            self.visible_chars += self.speed * dt
            if self.visible_chars >= len(self.full_text):
                self.visible_chars = len(self.full_text)
                self.finished = True

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return False
        if any(event.key == k for k in KEY_CONFIRM):
            if not self.finished:
                self.visible_chars = len(self.full_text)
                self.finished = True
                return False
            else:
                if self.on_complete:
                    self.on_complete()
                return True
        return False

    def draw(self, surf):
        bx, by, bw, bh = 40, 420, SCREEN_WIDTH - 80, 140
        pygame.draw.rect(surf, UI_BORDER_DARK, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=10)
        pygame.draw.rect(surf, UI_BG, (bx, by, bw, bh), border_radius=8)
        
        # Speaker Name Badge
        if self.speaker:
            sw = gfx.fonts["regular"].size(self.speaker)[0] + 24
            pygame.draw.rect(surf, UI_BORDER_DARK, (bx + 16, by - 14, sw, 28), border_radius=6)
            pygame.draw.rect(surf, (255, 235, 180), (bx + 18, by - 12, sw - 4, 24), border_radius=4)
            stxt = gfx.fonts["regular"].render(self.speaker, True, (180, 60, 0))
            surf.blit(stxt, (bx + 28, by - 10))

        # Text with wrapping
        disp_text = self.full_text[:int(self.visible_chars)]
        words = disp_text.split(" ")
        lines = []
        curr_line = ""
        for w in words:
            test = curr_line + (" " if curr_line else "") + w
            if gfx.fonts["medium"].size(test)[0] < bw - 50:
                curr_line = test
            else:
                lines.append(curr_line)
                curr_line = w
        if curr_line:
            lines.append(curr_line)

        for i, l_str in enumerate(lines[:3]):
            ltxt = gfx.fonts["medium"].render(l_str, True, UI_TEXT)
            surf.blit(ltxt, (bx + 25, by + 28 + i * 32))

class PCBoxScreen:
    """
    Comprehensive Pokémon Storage System (PC Box) screen.
    Allows withdrawing, depositing, swapping, and inspecting Pokémon
    between the active party (max 6) and the storage PC box.
    """
    def __init__(self, party, pc_box):
        self.party = party
        self.pc_box = pc_box
        self.active_panel = "PARTY" if len(party) > 0 else "PC" # "PARTY" or "PC"
        self.party_idx = 0
        self.pc_idx = 0
        self.pc_scroll = 0
        self.menu_mode = "NAVIGATE" # "NAVIGATE", "ACTIONS", "SUMMARY"
        self.action_idx = 0
        self.summary_pokemon = None
        self.notification = ""
        self.notification_timer = 0.0

    def show_notification(self, text, duration=2.5):
        self.notification = text
        self.notification_timer = duration

    def update(self, dt):
        if self.notification_timer > 0:
            self.notification_timer -= dt
            if self.notification_timer <= 0:
                self.notification = ""

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        # 1. Summary Mode View
        if self.menu_mode == "SUMMARY":
            if any(event.key == k for k in KEY_CONFIRM + KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                self.menu_mode = "NAVIGATE"
                self.summary_pokemon = None
            return None

        # 2. Action Sub-Menu Mode
        if self.menu_mode == "ACTIONS":
            actions = self._get_available_actions()
            if any(event.key == k for k in KEY_UP):
                self.action_idx = (self.action_idx - 1) % len(actions)
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.action_idx = (self.action_idx + 1) % len(actions)
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                self.menu_mode = "NAVIGATE"
            elif any(event.key == k for k in KEY_CONFIRM):
                chosen_action = actions[self.action_idx]
                self._execute_action(chosen_action)
            return None

        # 3. Main Navigation Mode
        if any(event.key == k for k in KEY_LEFT):
            if self.active_panel == "PC":
                self.active_panel = "PARTY"
                sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_RIGHT):
            if self.active_panel == "PARTY":
                self.active_panel = "PC"
                sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_UP):
            if self.active_panel == "PARTY" and len(self.party) > 0:
                self.party_idx = (self.party_idx - 1) % len(self.party)
                sound_mgr.play_sfx("select")
            elif self.active_panel == "PC" and len(self.pc_box) > 0:
                self.pc_idx = (self.pc_idx - 1) % len(self.pc_box)
                self._adjust_pc_scroll()
                sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_DOWN):
            if self.active_panel == "PARTY" and len(self.party) > 0:
                self.party_idx = (self.party_idx + 1) % len(self.party)
                sound_mgr.play_sfx("select")
            elif self.active_panel == "PC" and len(self.pc_box) > 0:
                self.pc_idx = (self.pc_idx + 1) % len(self.pc_box)
                self._adjust_pc_scroll()
                sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_CONFIRM):
            if self.active_panel == "PARTY" and len(self.party) > 0:
                self.menu_mode = "ACTIONS"
                self.action_idx = 0
                sound_mgr.play_sfx("confirm")
            elif self.active_panel == "PC" and len(self.pc_box) > 0:
                self.menu_mode = "ACTIONS"
                self.action_idx = 0
                sound_mgr.play_sfx("confirm")
            else:
                self.show_notification("No Pokémon selected in this panel!")
        elif any(event.key == k for k in KEY_CANCEL):
            sound_mgr.play_sfx("cancel")
            return "EXIT"

        return None

    def _adjust_pc_scroll(self):
        if self.pc_idx < self.pc_scroll:
            self.pc_scroll = self.pc_idx
        elif self.pc_idx >= self.pc_scroll + 6:
            self.pc_scroll = self.pc_idx - 5

    def _get_available_actions(self):
        if self.active_panel == "PARTY":
            return ["DEPOSIT TO PC", "SWAP WITH PC", "SUMMARY", "CANCEL"]
        else:
            return ["WITHDRAW TO PARTY", "SWAP WITH PARTY", "SUMMARY", "CANCEL"]

    def _execute_action(self, action):
        if action == "DEPOSIT TO PC":
            if len(self.party) <= 1:
                self.show_notification("Cannot deposit your last Pokémon!")
                sound_mgr.play_sfx("cancel")
            else:
                pkmn = self.party.pop(self.party_idx)
                self.pc_box.append(pkmn)
                self.party_idx = max(0, min(len(self.party) - 1, self.party_idx))
                self.show_notification(f"Deposited {pkmn.nickname or pkmn.species} into PC Box!")
                sound_mgr.play_sfx("confirm")
                self.menu_mode = "NAVIGATE"

        elif action == "WITHDRAW TO PARTY":
            if len(self.party) >= 6:
                self.show_notification("Party is full! (Max 6). Use Swap instead.")
                sound_mgr.play_sfx("cancel")
            else:
                pkmn = self.pc_box.pop(self.pc_idx)
                self.party.append(pkmn)
                self.pc_idx = max(0, min(len(self.pc_box) - 1, self.pc_idx))
                self._adjust_pc_scroll()
                self.show_notification(f"Withdrew {pkmn.nickname or pkmn.species} to Party!")
                sound_mgr.play_sfx("confirm")
                self.menu_mode = "NAVIGATE"

        elif action in ["SWAP WITH PC", "SWAP WITH PARTY"]:
            if len(self.party) == 0 or len(self.pc_box) == 0:
                self.show_notification("Need at least 1 Pokémon in both Party and PC to swap!")
                sound_mgr.play_sfx("cancel")
            else:
                p_party = self.party[self.party_idx]
                p_pc = self.pc_box[self.pc_idx]
                self.party[self.party_idx] = p_pc
                self.pc_box[self.pc_idx] = p_party
                self.show_notification(f"Swapped {p_party.species} with {p_pc.species}!")
                sound_mgr.play_sfx("confirm")
                self.menu_mode = "NAVIGATE"

        elif action == "SUMMARY":
            if self.active_panel == "PARTY" and len(self.party) > self.party_idx:
                self.summary_pokemon = self.party[self.party_idx]
                self.menu_mode = "SUMMARY"
                sound_mgr.play_sfx("confirm")
            elif self.active_panel == "PC" and len(self.pc_box) > self.pc_idx:
                self.summary_pokemon = self.pc_box[self.pc_idx]
                self.menu_mode = "SUMMARY"
                sound_mgr.play_sfx("confirm")

        elif action == "CANCEL":
            self.menu_mode = "NAVIGATE"
            sound_mgr.play_sfx("cancel")

    def draw(self, surf):
        # Background
        surf.fill((228, 236, 248))

        # Title Header
        title_txt = gfx.fonts["title"].render("POKÉMON STORAGE SYSTEM", True, (20, 70, 160))
        sub_txt = gfx.fonts["regular"].render("Manage your active battle team & stored Pokémon in the PC box", True, UI_TEXT_MUTED)
        surf.blit(title_txt, (SCREEN_WIDTH // 2 - title_txt.get_width() // 2, 16))
        surf.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 54))

        # 1. Left Column: Active Party (Max 6)
        lx, ly, lw, lh = 35, 86, 350, 460
        is_party_active = (self.active_panel == "PARTY")
        bdr_color = (240, 140, 40) if is_party_active else UI_BORDER_LIGHT
        pygame.draw.rect(surf, bdr_color, (lx - 2, ly - 2, lw + 4, lh + 4), border_radius=12)
        pygame.draw.rect(surf, WHITE, (lx, ly, lw, lh), border_radius=10)

        p_header = gfx.fonts["large"].render(f"ACTIVE TEAM ({len(self.party)}/6)", True, (20, 80, 180) if is_party_active else UI_TEXT)
        surf.blit(p_header, (lx + 20, ly + 14))

        # Party Slot Cards (Up to 6)
        for i in range(6):
            cy = ly + 50 + i * 66
            cw, ch = lw - 30, 60
            cx = lx + 15

            if i < len(self.party):
                p = self.party[i]
                is_sel = (is_party_active and i == self.party_idx)
                card_bdr = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
                card_bg = (255, 248, 230) if is_sel else (250, 252, 255)

                pygame.draw.rect(surf, card_bdr, (cx, cy, cw, ch), border_radius=8)
                pygame.draw.rect(surf, card_bg, (cx + 1, cy + 1, cw - 2, ch - 2), border_radius=7)

                # Mini Sprite
                sprite = gfx.get_pokemon_sprite(p.species, is_back=False, size=(46, 46))
                surf.blit(sprite, (cx + 4, cy + 6))

                # Name & Level
                name_txt = gfx.fonts["regular"].render(f"{p.nickname or p.species}", True, (200, 80, 0) if is_sel else UI_TEXT)
                lvl_txt = gfx.fonts["small"].render(f"Lv.{p.level}", True, UI_TEXT_MUTED)
                surf.blit(name_txt, (cx + 56, cy + 8))
                surf.blit(lvl_txt, (cx + 56 + name_txt.get_width() + 8, cy + 10))

                # HP Bar
                hp_w = 110
                hp_pct = max(0.0, min(1.0, p.current_hp / p.max_hp))
                hp_col = HP_GREEN if hp_pct > 0.5 else (HP_YELLOW if hp_pct > 0.2 else HP_RED)
                pygame.draw.rect(surf, (200, 205, 215), (cx + 56, cy + 34, hp_w, 8), border_radius=3)
                pygame.draw.rect(surf, hp_col, (cx + 56, cy + 34, int(hp_w * hp_pct), 8), border_radius=3)

                hp_lbl = gfx.fonts["small"].render(f"{p.current_hp}/{p.max_hp}", True, UI_TEXT_MUTED)
                surf.blit(hp_lbl, (cx + 56 + hp_w + 8, cy + 30))

                # Types & Status
                p_types = POKEMON_SPECIES.get(p.species, {}).get("types", ["Normal"])
                for t_idx, t_name in enumerate(p_types):
                    gfx.draw_type_badge(surf, t_name, cx + cw - 70 + t_idx * 34, cy + 8, width=32, height=16)
                if p.is_fainted():
                    gfx.draw_status_badge(surf, "Fainted", cx + cw - 44, cy + 32, width=36, height=16)
                elif p.status:
                    gfx.draw_status_badge(surf, p.status, cx + cw - 44, cy + 32, width=36, height=16)

            else:
                # Empty Party Slot
                pygame.draw.rect(surf, (230, 235, 245), (cx, cy, cw, ch), border_radius=8)
                empty_lbl = gfx.fonts["small"].render("- Empty Slot -", True, (160, 170, 185))
                surf.blit(empty_lbl, (cx + (cw - empty_lbl.get_width()) // 2, cy + 22))

        # 2. Right Column: PC Storage Box
        rx, ry, rw, rh = 415, 86, 350, 460
        is_pc_active = (self.active_panel == "PC")
        bdr_color_pc = (240, 140, 40) if is_pc_active else UI_BORDER_LIGHT
        pygame.draw.rect(surf, bdr_color_pc, (rx - 2, ry - 2, rw + 4, rh + 4), border_radius=12)
        pygame.draw.rect(surf, WHITE, (rx, ry, rw, rh), border_radius=10)

        pc_header = gfx.fonts["large"].render(f"PC STORAGE BOX ({len(self.pc_box)})", True, (20, 80, 180) if is_pc_active else UI_TEXT)
        surf.blit(pc_header, (rx + 20, ry + 14))

        if len(self.pc_box) == 0:
            # Empty state message
            no_pkmn_txt = gfx.fonts["regular"].render("No Pokémon stored in PC Box.", True, UI_TEXT_MUTED)
            hint_txt = gfx.fonts["small"].render("Caught Pokémon will be stored here", True, UI_TEXT_MUTED)
            hint_txt2 = gfx.fonts["small"].render("when your party is full (6 Pokémon).", True, UI_TEXT_MUTED)
            surf.blit(no_pkmn_txt, (rx + (rw - no_pkmn_txt.get_width()) // 2, ry + 180))
            surf.blit(hint_txt, (rx + (rw - hint_txt.get_width()) // 2, ry + 215))
            surf.blit(hint_txt2, (rx + (rw - hint_txt2.get_width()) // 2, ry + 238))
        else:
            # Display up to 6 visible slots in scroll view
            visible_count = min(6, len(self.pc_box) - self.pc_scroll)
            for idx in range(6):
                actual_idx = self.pc_scroll + idx
                cy = ry + 50 + idx * 66
                cw, ch = rw - 30, 60
                cx = rx + 15

                if actual_idx < len(self.pc_box):
                    p = self.pc_box[actual_idx]
                    is_sel = (is_pc_active and actual_idx == self.pc_idx)
                    card_bdr = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
                    card_bg = (255, 248, 230) if is_sel else (250, 252, 255)

                    pygame.draw.rect(surf, card_bdr, (cx, cy, cw, ch), border_radius=8)
                    pygame.draw.rect(surf, card_bg, (cx + 1, cy + 1, cw - 2, ch - 2), border_radius=7)

                    # Mini Sprite
                    sprite = gfx.get_pokemon_sprite(p.species, is_back=False, size=(46, 46))
                    surf.blit(sprite, (cx + 4, cy + 6))

                    # Name & Level
                    name_txt = gfx.fonts["regular"].render(f"{p.nickname or p.species}", True, (200, 80, 0) if is_sel else UI_TEXT)
                    lvl_txt = gfx.fonts["small"].render(f"Lv.{p.level}", True, UI_TEXT_MUTED)
                    surf.blit(name_txt, (cx + 56, cy + 8))
                    surf.blit(lvl_txt, (cx + 56 + name_txt.get_width() + 8, cy + 10))

                    # HP Bar
                    hp_w = 110
                    hp_pct = max(0.0, min(1.0, p.current_hp / p.max_hp))
                    hp_col = HP_GREEN if hp_pct > 0.5 else (HP_YELLOW if hp_pct > 0.2 else HP_RED)
                    pygame.draw.rect(surf, (200, 205, 215), (cx + 56, cy + 34, hp_w, 8), border_radius=3)
                    pygame.draw.rect(surf, hp_col, (cx + 56, cy + 34, int(hp_w * hp_pct), 8), border_radius=3)

                    hp_lbl = gfx.fonts["small"].render(f"{p.current_hp}/{p.max_hp}", True, UI_TEXT_MUTED)
                    surf.blit(hp_lbl, (cx + 56 + hp_w + 8, cy + 30))

                    # Types & Status
                    p_types = POKEMON_SPECIES.get(p.species, {}).get("types", ["Normal"])
                    for t_idx, t_name in enumerate(p_types):
                        gfx.draw_type_badge(surf, t_name, cx + cw - 70 + t_idx * 34, cy + 8, width=32, height=16)
                    if p.is_fainted():
                        gfx.draw_status_badge(surf, "Fainted", cx + cw - 44, cy + 32, width=36, height=16)
                    elif p.status:
                        gfx.draw_status_badge(surf, p.status, cx + cw - 44, cy + 32, width=36, height=16)

            # Scroll indicator
            if len(self.pc_box) > 6:
                scroll_info = gfx.fonts["small"].render(f"▲ ▼ ({self.pc_idx + 1}/{len(self.pc_box)})", True, (200, 80, 0))
                surf.blit(scroll_info, (rx + rw - scroll_info.get_width() - 20, ry + 16))

        # 3. Action Modal Popup Overlay
        if self.menu_mode == "ACTIONS":
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 110))
            surf.blit(overlay, (0, 0))

            actions = self._get_available_actions()
            mw, mh = 260, 48 + len(actions) * 44
            mx = (SCREEN_WIDTH - mw) // 2
            my = (SCREEN_HEIGHT - mh) // 2

            pygame.draw.rect(surf, UI_BORDER_DARK, (mx - 2, my - 2, mw + 4, mh + 4), border_radius=12)
            pygame.draw.rect(surf, WHITE, (mx, my, mw, mh), border_radius=10)

            act_title = gfx.fonts["large"].render("CHOOSE ACTION", True, (20, 70, 160))
            surf.blit(act_title, (mx + (mw - act_title.get_width()) // 2, my + 14))

            for a_idx, act_name in enumerate(actions):
                ay = my + 48 + a_idx * 44
                is_sel = (a_idx == self.action_idx)
                bdr_col = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
                bg_col = (255, 240, 210) if is_sel else (250, 250, 252)

                pygame.draw.rect(surf, bdr_col, (mx + 16, ay, mw - 32, 36), border_radius=8)
                pygame.draw.rect(surf, bg_col, (mx + 17, ay + 1, mw - 34, 34), border_radius=7)

                atxt = gfx.fonts["regular"].render(act_name, True, (200, 80, 0) if is_sel else UI_TEXT)
                surf.blit(atxt, (mx + (mw - atxt.get_width()) // 2, ay + 8))

            # 4. Summary Card Modal Popup Overlay
        if self.menu_mode == "SUMMARY" and self.summary_pokemon:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 130))
            surf.blit(overlay, (0, 0))

            p = self.summary_pokemon
            sw, sh = 520, 390
            sx = (SCREEN_WIDTH - sw) // 2
            sy = (SCREEN_HEIGHT - sh) // 2

            pygame.draw.rect(surf, UI_BORDER_DARK, (sx - 2, sy - 2, sw + 4, sh + 4), border_radius=14)
            pygame.draw.rect(surf, WHITE, (sx, sy, sw, sh), border_radius=12)

            # Header
            shead = gfx.fonts["title"].render(f"{p.nickname or p.species} - Level {p.level}", True, (20, 70, 160))
            surf.blit(shead, (sx + 24, sy + 18))

            # Sprite & Types
            sp_surf = gfx.get_pokemon_sprite(p.species, is_back=False, size=(120, 120))
            surf.blit(sp_surf, (sx + 24, sy + 58))

            p_types = POKEMON_SPECIES.get(p.species, {}).get("types", ["Normal"])
            for t_idx, t_name in enumerate(p_types):
                gfx.draw_type_badge(surf, t_name, sx + 24 + t_idx * 70, sy + 185, width=64, height=22)
            if p.is_fainted():
                gfx.draw_status_badge(surf, "Fainted", sx + 24 + len(p_types) * 70, sy + 185, width=54, height=22)
            elif p.status:
                gfx.draw_status_badge(surf, p.status, sx + 24 + len(p_types) * 70, sy + 185, width=54, height=22)

            # Stats Column
            stat_x = sx + 170
            s_hp = gfx.fonts["regular"].render(f"HP: {p.current_hp}/{p.max_hp}", True, UI_TEXT)
            s_atk = gfx.fonts["regular"].render(f"Attack: {p.stats['atk']}", True, UI_TEXT)
            s_def = gfx.fonts["regular"].render(f"Defense: {p.stats['def']}", True, UI_TEXT)
            s_spd = gfx.fonts["regular"].render(f"Speed: {p.stats['spd']}", True, UI_TEXT)
            s_exp = gfx.fonts["small"].render(f"EXP: {p.exp}", True, UI_TEXT_MUTED)

            surf.blit(s_hp, (stat_x, sy + 65))
            surf.blit(s_atk, (stat_x, sy + 95))
            surf.blit(s_def, (stat_x, sy + 125))
            surf.blit(s_spd, (stat_x, sy + 155))
            surf.blit(s_exp, (stat_x, sy + 185))

            # Moves Box
            moves_y = sy + 225
            pygame.draw.rect(surf, (245, 248, 255), (sx + 20, moves_y, sw - 40, 115), border_radius=8)
            pygame.draw.rect(surf, UI_BORDER_LIGHT, (sx + 20, moves_y, sw - 40, 115), 1, border_radius=8)

            m_title = gfx.fonts["small"].render("KNOWN MOVES", True, (40, 100, 200))
            surf.blit(m_title, (sx + 30, moves_y + 8))

            for m_i, m in enumerate(p.moves[:4]):
                mx_pos = sx + 30 + (m_i % 2) * 240
                my_pos = moves_y + 32 + (m_i // 2) * 36
                m_name = gfx.fonts["regular"].render(m.name, True, UI_TEXT)
                m_pp = gfx.fonts["small"].render(f"PP: {m.pp}/{m.max_pp} ({m.type})", True, UI_TEXT_MUTED)
                surf.blit(m_name, (mx_pos, my_pos))
                surf.blit(m_pp, (mx_pos, my_pos + 18))

            close_hint = gfx.fonts["small"].render("Press [Z / X / Enter / ESC] to Close Summary", True, (200, 80, 0))
            surf.blit(close_hint, (sx + (sw - close_hint.get_width()) // 2, sy + 355))

        # 5. On-screen Toast Notification
        if self.notification_timer > 0:
            nw = gfx.fonts["regular"].size(self.notification)[0] + 36
            nx = (SCREEN_WIDTH - nw) // 2
            ny = 20
            pygame.draw.rect(surf, (30, 36, 50), (nx - 2, ny - 2, nw + 4, 36), border_radius=8)
            pygame.draw.rect(surf, (255, 235, 180), (nx, ny, nw, 32), border_radius=6)
            ntxt = gfx.fonts["regular"].render(self.notification, True, (180, 60, 0))
            surf.blit(ntxt, (nx + 18, ny + 5))

        # 6. Bottom Navigation Hint Bar
        hint = gfx.fonts["small"].render("Left/Right: Switch Panel  |  Up/Down: Select Pokémon  |  [Enter]: Options  |  [X]: Exit PC", True, UI_TEXT_MUTED)
        surf.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 565))

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

        # Map Nodes for Region Map
        self.map_nodes = [
            {"name": "Pewter City", "x": 220, "y": 140, "desc": "A stone gray city. Home of Leader Brock's Gym & the Museum.", "type": "CITY"},
            {"name": "Route 3", "x": 310, "y": 140, "desc": "Mountain canyon foothills leading east to Mt. Moon.", "type": "ROUTE"},
            {"name": "Mt. Moon", "x": 400, "y": 140, "desc": "Subterranean cavern rich in ancient fossils and Moon Stones.", "type": "DUNGEON"},
            {"name": "Route 4", "x": 490, "y": 140, "desc": "Scenic river canyon slopes leading to Cerulean City.", "type": "ROUTE"},
            {"name": "Cerulean City", "x": 580, "y": 140, "desc": "A floral canal metropolis. Home of Leader Misty's Gym.", "type": "CITY"},
            {"name": "Route 24", "x": 580, "y": 70, "desc": "Nugget Bridge gauntlet leading to Bill's Sea Cottage.", "type": "ROUTE"},
            {"name": "Route 9", "x": 670, "y": 140, "desc": "Rocky badlands canyon trail connecting Cerulean and Lavender.", "type": "ROUTE"},
            {"name": "Power Plant", "x": 670, "y": 70, "desc": "Industrial electric generating facility teeming with Electric Pokémon.", "type": "DUNGEON"},
            {"name": "Lavender Town", "x": 670, "y": 240, "desc": "A noble purple town enveloped in mist, home of Pokémon Tower.", "type": "TOWN"},
            {"name": "Pokémon Tower", "x": 740, "y": 240, "desc": "Sacred haunted spire where spirits of Pokémon rest in peace.", "type": "DUNGEON"},
            {"name": "Safari Zone", "x": 670, "y": 350, "desc": "Vast golden savanna reserve filled with rare wild Pokémon.", "type": "DUNGEON"},
            {"name": "Viridian Forest", "x": 220, "y": 210, "desc": "Deep woods labyrinth teeming with bug Pokémon and Pikachu.", "type": "DUNGEON"},
            {"name": "Route 22", "x": 130, "y": 280, "desc": "Foothills leading west to the Indigo Plateau League Gate.", "type": "ROUTE"},
            {"name": "Viridian City", "x": 220, "y": 280, "desc": "The gateway crossroads city with Pokémon Center and Mart.", "type": "CITY"},
            {"name": "Route 1", "x": 220, "y": 350, "desc": "Lush grassy path connecting Pallet Town and Viridian City.", "type": "ROUTE"},
            {"name": "Pallet Town", "x": 220, "y": 420, "desc": "A quiet hometown with fresh sea breezes and Prof. Oak's Lab.", "type": "TOWN"},
            {"name": "Route 21", "x": 220, "y": 490, "desc": "Vast ocean sea route south of Pallet Town filled with water Pokémon.", "type": "ROUTE"},
            {"name": "Seafoam Islands", "x": 220, "y": 520, "desc": "Sub-zero glacial ice caverns situated in the southern sea.", "type": "DUNGEON"},
            {"name": "Cinnabar Island", "x": 220, "y": 560, "desc": "A fiery volcanic island with Pokémon research laboratories.", "type": "CITY"}
        ]
        self.selected_node_idx = 0
        for idx, node in enumerate(self.map_nodes):
            if node["name"] == player.current_map:
                self.selected_node_idx = idx
                break

    def update(self, dt):
        self.timer += dt

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if any(event.key == k for k in KEY_LEFT + KEY_RIGHT):
            self.active_tab = 1 - self.active_tab
            sound_mgr.play_sfx("select")
        elif self.active_tab == 1:
            if any(event.key == k for k in KEY_UP):
                self.selected_node_idx = (self.selected_node_idx - 1) % len(self.map_nodes)
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.selected_node_idx = (self.selected_node_idx + 1) % len(self.map_nodes)
                sound_mgr.play_sfx("select")
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

        # Tab 1: Kanto Region Map & Exploration
        else:
            # Discovery Statistics Header on Left Panel
            visited_nodes = [n for n in self.map_nodes if len(self.world.explored_tiles.get(n["name"], set())) > 0]
            v_cnt = len(visited_nodes)
            tot_cnt = len(self.map_nodes)
            v_pct = int(100 * v_cnt / max(1, tot_cnt))

            lx, ly, lw, lh = cx + 12, cy + 12, 426, ch - 24
            pygame.draw.rect(surf, (248, 250, 255), (lx, ly, lw, lh), border_radius=8)
            pygame.draw.rect(surf, UI_BORDER_LIGHT, (lx, ly, lw, lh), 1, border_radius=8)

            # Discovery Progress Card at top of Left Panel
            by = ly + 8
            pygame.draw.rect(surf, (238, 244, 255), (lx + 8, by, lw - 16, 36), border_radius=6)
            pygame.draw.rect(surf, (210, 222, 245), (lx + 8, by, lw - 16, 36), 1, border_radius=6)

            p_title = gfx.fonts["small"].render(f"KANTO DISCOVERY PROGRESS: {v_cnt} / {tot_cnt} AREAS ({v_pct}%)", True, (20, 70, 160))
            surf.blit(p_title, (lx + 16, by + 5))

            # Miniature progress bar
            pb_w = lw - 32
            pb_fill = int(pb_w * (v_cnt / max(1, tot_cnt)))
            pygame.draw.rect(surf, (220, 226, 238), (lx + 16, by + 23, pb_w, 6), border_radius=3)
            pygame.draw.rect(surf, (40, 180, 80), (lx + 16, by + 23, pb_fill, 6), border_radius=3)

            # Draw Region Map Connection Routes
            map_lines = [
                # Pallet Town -> Route 1 -> Viridian City -> Route 22
                ((220, 420), (220, 350)),
                ((220, 350), (220, 280)),
                ((220, 280), (130, 280)),
                # Viridian City -> Viridian Forest -> Pewter City
                ((220, 280), (220, 210)),
                ((220, 210), (220, 140)),
                # Pewter City -> Route 3 -> Mt Moon -> Route 4 -> Cerulean City
                ((220, 140), (310, 140)),
                ((310, 140), (400, 140)),
                ((400, 140), (490, 140)),
                ((490, 140), (580, 140)),
                # Cerulean City -> Route 24
                ((580, 140), (580, 70)),
                # Cerulean City -> Route 9 -> Power Plant / Lavender Town
                ((580, 140), (670, 140)),
                ((670, 140), (670, 70)),
                ((670, 140), (670, 240)),
                # Lavender Town -> Pokémon Tower & Safari Zone
                ((670, 240), (740, 240)),
                ((670, 240), (670, 350)),
                # Pallet Town -> Route 21 -> Seafoam Islands -> Cinnabar Island
                ((220, 420), (220, 490)),
                ((220, 490), (220, 525)),
                ((220, 525), (220, 560))
            ]

            # Scale and offset for left panel card area
            map_ox, map_oy = lx + 8, by + 46
            for p1, p2 in map_lines:
                x1 = map_ox + int(p1[0] * 0.54)
                y1 = map_oy + int(p1[1] * 0.63)
                x2 = map_ox + int(p2[0] * 0.54)
                y2 = map_oy + int(p2[1] * 0.63)
                pygame.draw.line(surf, (200, 160, 100), (x1, y1), (x2, y2), 6)
                pygame.draw.line(surf, (245, 215, 150), (x1, y1), (x2, y2), 3)

            # Draw Map Nodes on Left Panel
            for n_idx, node in enumerate(self.map_nodes):
                nx = map_ox + int(node["x"] * 0.54)
                ny = map_oy + int(node["y"] * 0.63)
                is_sel = (n_idx == self.selected_node_idx)
                is_player_here = (node["name"] == self.player.current_map)
                is_visited = len(self.world.explored_tiles.get(node["name"], set())) > 0

                # Node appearance based on type & visited status
                if is_visited:
                    if node["type"] == "CITY":
                        pygame.draw.circle(surf, (220, 40, 40), (nx, ny), 8)
                        pygame.draw.circle(surf, WHITE, (nx, ny), 4)
                    elif node["type"] == "TOWN":
                        pygame.draw.circle(surf, (40, 100, 220), (nx, ny), 7)
                        pygame.draw.circle(surf, WHITE, (nx, ny), 3)
                    elif node["type"] == "DUNGEON":
                        pygame.draw.polygon(surf, (140, 80, 40), [(nx, ny - 8), (nx + 7, ny + 6), (nx - 7, ny + 6)])
                        pygame.draw.circle(surf, WHITE, (nx, ny), 2)
                    else:
                        pygame.draw.circle(surf, (50, 160, 60), (nx, ny), 5)
                else:
                    # Unvisited node: Dimmed gray with question badge
                    pygame.draw.circle(surf, (150, 160, 175), (nx, ny), 6)
                    pygame.draw.circle(surf, (75, 85, 100), (nx, ny), 4)

                # Selection Highlight ring
                if is_sel:
                    pygame.draw.circle(surf, (255, 140, 0), (nx, ny), 13, 2)

                # Blinking Player Indicator
                if is_player_here and int(self.timer * 3) % 2 == 0:
                    pygame.draw.circle(surf, (255, 230, 40), (nx, ny - 13), 5)
                    here_t = gfx.fonts["small"].render("YOU", True, (220, 40, 40))
                    surf.blit(here_t, (nx - here_t.get_width() // 2, ny - 26))

                # Node Label
                if is_visited:
                    lbl_col = (200, 80, 0) if is_sel else UI_TEXT
                    nl = gfx.fonts["small"].render(node["name"], True, lbl_col)
                else:
                    lbl_col = (220, 120, 40) if is_sel else (140, 150, 165)
                    nl = gfx.fonts["small"].render(f"? {node['name']}", True, lbl_col)
                
                # Position label to right or left depending on side
                lx_pos = (nx + 10) if node["x"] < 500 else (nx - nl.get_width() - 10)
                surf.blit(nl, (lx_pos, ny - 6))

            # =========================================================================
            # Right Panel: Selected Area Exploration Dossier & Live Minimap
            # =========================================================================
            rx, ry, rw, rh = cx + 450, cy + 12, cw - 462, ch - 24
            pygame.draw.rect(surf, (252, 252, 255), (rx, ry, rw, rh), border_radius=8)
            pygame.draw.rect(surf, UI_BORDER_LIGHT, (rx, ry, rw, rh), 1, border_radius=8)

            sel_node = self.map_nodes[self.selected_node_idx]
            node_name = sel_node["name"]
            explored_set = self.world.explored_tiles.get(node_name, set())
            is_visited = len(explored_set) > 0
            grid = self.world.maps.get(node_name, {}).get("grid", [])

            # 1. Location Header & Status Tag
            loc_title = gfx.fonts["medium"].render(node_name, True, (20, 70, 160))
            surf.blit(loc_title, (rx + 12, ry + 10))

            if is_visited:
                # Calculate map %
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

                is_cave = (node_name in ["Mt. Moon", "Seafoam Islands"])
                is_ice = (node_name == "Seafoam Islands")
                is_lavender = (node_name in ["Lavender Town", "Pokémon Tower"])
                is_power_plant = (node_name == "Power Plant")
                is_safari = (node_name == "Safari Zone")
                is_canyon = (node_name == "Route 9")
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

                # If player is in this map, draw blip
                if self.player.current_map == node_name:
                    px = gx_start + self.player.grid_x * cell_s + cell_s // 2
                    py = gy_start + self.player.grid_y * cell_s + cell_s // 2
                    pygame.draw.circle(surf, (255, 230, 40), (px, py), max(3, cell_s + 1), 1)
                    pygame.draw.circle(surf, (240, 40, 40), (px, py), max(2, cell_s))
            else:
                # Shrouded Unknown Region Mystery Card
                pygame.draw.circle(surf, (40, 48, 64), (cm_x + cm_w // 2, cm_y + cm_h // 2 - 12), 24)
                q_txt = gfx.fonts["title"].render("?", True, (130, 145, 170))
                surf.blit(q_txt, (cm_x + (cm_w - q_txt.get_width()) // 2, cm_y + cm_h // 2 - 32))
                un_t = gfx.fonts["regular"].render("UNEXPLORED TERRITORY", True, (200, 210, 230))
                un_sub = gfx.fonts["small"].render("Travel to this area to reveal map layout", True, (130, 140, 160))
                surf.blit(un_t, (cm_x + (cm_w - un_t.get_width()) // 2, cm_y + cm_h // 2 + 18))
                surf.blit(un_sub, (cm_x + (cm_w - un_sub.get_width()) // 2, cm_y + cm_h // 2 + 40))

            # 3. Location Description Card
            dx, dy, dw, dh = rx + 12, ry + 214, rw - 24, 60
            pygame.draw.rect(surf, (245, 248, 255), (dx, dy, dw, dh), border_radius=6)
            pygame.draw.rect(surf, (215, 225, 240), (dx, dy, dw, dh), 1, border_radius=6)
            
            d_desc = gfx.fonts["small"].render(sel_node["desc"], True, UI_TEXT)
            surf.blit(d_desc, (dx + 8, dy + 8))

            # 4. Known Wild Pokémon Habitats
            hx, hy, hw, hh = rx + 12, ry + 282, rw - 24, 150
            pygame.draw.rect(surf, (245, 248, 255), (hx, hy, hw, hh), border_radius=6)
            pygame.draw.rect(surf, (215, 225, 240), (hx, hy, hw, hh), 1, border_radius=6)

            h_head = gfx.fonts["small"].render("WILD POKÉMON HABITATS:", True, (20, 70, 160))
            surf.blit(h_head, (hx + 8, hy + 8))

            if is_visited:
                # Gather unique encounters
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
                    no_w = gfx.fonts["small"].render("No wild Pokémon roaming this area.", True, UI_TEXT_MUTED)
                    surf.blit(no_w, (hx + 10, hy + 35))
            else:
                un_enc = gfx.fonts["small"].render("Fauna Unknown.", True, UI_TEXT_MUTED)
                un_enc2 = gfx.fonts["small"].render("Explore this region to log wild species!", True, (140, 150, 165))
                surf.blit(un_enc, (hx + 10, hy + 35))
                surf.blit(un_enc2, (hx + 10, hy + 58))

        # Bottom Controls Hint
        hint = gfx.fonts["small"].render("Left/Right: Switch Tab  |  Up/Down: Browse Exploration Map  |  [X / Enter]: Return", True, UI_TEXT_MUTED)
        surf.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 565))

