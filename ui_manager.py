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
from pokemon_data import POKEMON_SPECIES, ITEMS, MOVES

class TitleScreen:
    def __init__(self):
        self.timer = 0.0
        self.starter_index = 0
        self.starters = ["Charmander", "Squirtle", "Bulbasaur", "Pikachu"]
        self.menu_options = ["CONTINUE", "NEW GAME"]
        self.selected_idx = 0
        self.has_save = False
        self.save_summary = None
        self.refresh_save_status()

    def refresh_save_status(self):
        from save_system import SaveSystem
        self.has_save = SaveSystem.has_save()
        self.save_summary = SaveSystem.get_save_summary()
        if not self.has_save:
            self.menu_options = ["NEW GAME"]
            self.selected_idx = 0
        else:
            self.menu_options = ["CONTINUE", "NEW GAME"]

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
                
        if any(event.key == k for k in KEY_CONFIRM):
            sound_mgr.play_sfx("confirm")
            return self.menu_options[self.selected_idx]
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
        title_y = 60 + int(math.sin(self.timer * 2.0) * 6)
        title_txt = gfx.fonts["title"].render("POKÉMON", True, (255, 215, 0)) # Gold
        sub_txt = gfx.fonts["large"].render("PYGAME EDITION", True, (240, 60, 60)) # Red
        
        # Shadow & Glow
        surf.blit(gfx.fonts["title"].render("POKÉMON", True, (30, 30, 40)), (SCREEN_WIDTH // 2 - title_txt.get_width() // 2 + 4, title_y + 4))
        surf.blit(title_txt, (SCREEN_WIDTH // 2 - title_txt.get_width() // 2, title_y))
        surf.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, title_y + 55))

        if self.has_save:
            # Show Save Card and Continue / New Game
            for i, opt in enumerate(self.menu_options):
                by = 220 + i * 140
                is_sel = (i == self.selected_idx)
                bw, bh = 480, 115 if opt == "CONTINUE" else 65
                bx = (SCREEN_WIDTH - bw) // 2
                
                bdr_col = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
                bg_col = (255, 248, 230) if is_sel else WHITE
                pygame.draw.rect(surf, bdr_col, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=10)
                pygame.draw.rect(surf, bg_col, (bx, by, bw, bh), border_radius=8)
                
                if opt == "CONTINUE" and self.save_summary:
                    # Continue Card Details
                    head_txt = gfx.fonts["large"].render(f"CONTINUE (Slot {self.save_summary.get('slot', 1)})", True, (220, 80, 0) if is_sel else UI_TEXT)
                    surf.blit(head_txt, (bx + 20, by + 12))
                    
                    # Lead Pokemon Sprite
                    lead_sp = gfx.get_pokemon_sprite(self.save_summary.get("lead_species", "Pikachu"), is_back=False, size=(70, 70))
                    surf.blit(lead_sp, (bx + 20, by + 40))
                    
                    # Details
                    loc_txt = gfx.fonts["regular"].render(f"Location: {self.save_summary.get('map', 'Pallet Town')}", True, UI_TEXT)
                    lead_txt = gfx.fonts["regular"].render(f"{self.save_summary.get('lead_name', 'Pokémon')} (Lv.{self.save_summary.get('lead_level', 5)})", True, (40, 120, 220))
                    stat_txt = gfx.fonts["small"].render(f"Team: {self.save_summary.get('party_count', 1)} | Money: ${self.save_summary.get('money', 0)} | Pokédex: {self.save_summary.get('caught_count', 0)}/151", True, UI_TEXT_MUTED)
                    
                    surf.blit(loc_txt, (bx + 105, by + 40))
                    surf.blit(lead_txt, (bx + 105, by + 64))
                    surf.blit(stat_txt, (bx + 105, by + 88))
                else:
                    # New Game Card
                    opt_txt = gfx.fonts["large"].render("NEW GAME", True, (220, 80, 0) if is_sel else UI_TEXT)
                    surf.blit(opt_txt, (bx + (bw - opt_txt.get_width()) // 2, by + (bh - opt_txt.get_height()) // 2))
                    
            ctrl_hint = gfx.fonts["small"].render("Arrow Keys: Select  |  [Z / Enter]: Choose Save Slot", True, LIGHT_GRAY)
            surf.blit(ctrl_hint, (SCREEN_WIDTH // 2 - ctrl_hint.get_width() // 2, 550))
        else:
            # Featured Starter Sprite
            feat_species = self.starters[self.starter_index]
            p_surf = gfx.get_pokemon_sprite(feat_species, is_back=False, size=(200, 200))
            surf.blit(p_surf, (SCREEN_WIDTH // 2 - 100, 210))

            # Blinking "PRESS ENTER OR Z TO START"
            if int(self.timer * 2) % 2 == 0:
                start_txt = gfx.fonts["medium"].render("PRESS [ENTER] OR [Z] TO START", True, WHITE)
                surf.blit(start_txt, (SCREEN_WIDTH // 2 - start_txt.get_width() // 2, 470))
                
            ctrl_hint = gfx.fonts["small"].render("Arrow Keys: Move  |  Z: Confirm  |  X: Back  |  C: Menu  |  F5: Quick Save", True, LIGHT_GRAY)
            surf.blit(ctrl_hint, (SCREEN_WIDTH // 2 - ctrl_hint.get_width() // 2, 545))

class SaveSlotSelectScreen:
    """
    UI for managing multiple save slots (Slots 1, 2, 3).
    Modes:
      - 'LOAD': User picks an existing save to resume.
      - 'NEW_GAME': User picks a slot to start a new journey.
      - 'SAVE': In-game menu to save into any slot.
    """
    def __init__(self, mode="LOAD", active_slot=1, player=None, party=None, inventory=None, pokedex=None, world=None):
        self.mode = mode # "LOAD", "NEW_GAME", "SAVE"
        self.active_slot = active_slot
        self.player = player
        self.party = party
        self.inventory = inventory
        self.pokedex = pokedex
        self.world = world
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
                        SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world, slot=self.target_slot_for_modal)
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
                    SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world, slot=chosen_slot)
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
    def __init__(self, player, party, inventory, pokedex, slot=1):
        self.player = player
        self.party = party
        self.inventory = inventory
        self.pokedex = pokedex
        self.slot = slot
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
            SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, world, slot=self.slot)
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
        self.options = ["POKÉDEX", "POKÉMON", "BAG", "TRAINER", "SAVE", "EXIT"]
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
        mw, mh = 200, 260
        mx = SCREEN_WIDTH - mw - 20
        my = 20
        
        pygame.draw.rect(surf, UI_BORDER_DARK, (mx - 2, my - 2, mw + 4, mh + 4), border_radius=10)
        pygame.draw.rect(surf, UI_BG, (mx, my, mw, mh), border_radius=8)
        
        for i, opt in enumerate(self.options):
            iy = my + 18 + i * 38
            is_sel = (i == self.selected_idx)
            
            if is_sel:
                pygame.draw.rect(surf, (255, 235, 180), (mx + 8, iy - 4, mw - 16, 32), border_radius=6)
                pygame.draw.rect(surf, (240, 140, 40), (mx + 8, iy - 4, mw - 16, 32), 2, border_radius=6)
                
            txt = gfx.fonts["regular"].render(opt, True, (200, 80, 0) if is_sel else UI_TEXT)
            surf.blit(txt, (mx + 25, iy))

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
            
            # Types
            for t_idx, t_name in enumerate(p.types):
                gfx.draw_type_badge(surf, t_name, row_x + 105 + t_idx * 60, row_y + 95, width=54, height=20)

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
