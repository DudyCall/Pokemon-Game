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
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_CONFIRM, KEY_CANCEL, KEY_MENU
)
from graphics_manager import gfx
from sound_manager import sound_mgr
from pokemon_data import POKEMON_SPECIES, ITEMS

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
        self.save_summary = SaveSystem.get_save_summary()
        self.has_save = (self.save_summary is not None)
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
                    head_txt = gfx.fonts["large"].render("CONTINUE", True, (220, 80, 0) if is_sel else UI_TEXT)
                    surf.blit(head_txt, (bx + 20, by + 12))
                    
                    # Lead Pokemon Sprite
                    lead_sp = gfx.get_pokemon_sprite(self.save_summary["lead_species"], is_back=False, size=(70, 70))
                    surf.blit(lead_sp, (bx + 20, by + 40))
                    
                    # Details
                    loc_txt = gfx.fonts["regular"].render(f"Location: {self.save_summary['map']}", True, UI_TEXT)
                    lead_txt = gfx.fonts["regular"].render(f"{self.save_summary['lead_name']} (Lv.{self.save_summary['lead_level']})", True, (40, 120, 220))
                    stat_txt = gfx.fonts["small"].render(f"Team: {self.save_summary['party_count']} | Money: ${self.save_summary['money']} | Pokédex: {self.save_summary['caught_count']}", True, UI_TEXT_MUTED)
                    
                    surf.blit(loc_txt, (bx + 105, by + 40))
                    surf.blit(lead_txt, (bx + 105, by + 64))
                    surf.blit(stat_txt, (bx + 105, by + 88))
                else:
                    # New Game Card
                    opt_txt = gfx.fonts["large"].render("NEW GAME", True, (220, 80, 0) if is_sel else UI_TEXT)
                    surf.blit(opt_txt, (bx + (bw - opt_txt.get_width()) // 2, by + (bh - opt_txt.get_height()) // 2))
                    
            ctrl_hint = gfx.fonts["small"].render("Arrow Keys: Select  |  [Z / Enter]: Confirm", True, LIGHT_GRAY)
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

class SaveDialog:
    def __init__(self, player, party, inventory, pokedex):
        self.player = player
        self.party = party
        self.inventory = inventory
        self.pokedex = pokedex
        self.selected_yes = True
        self.state = "CONFIRM" # "CONFIRM", "SAVING", "SAVED"
        self.timer = 0.0

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
            
        if self.state == "CONFIRM":
            if any(event.key == k for k in KEY_LEFT or event.key == k for k in KEY_RIGHT or event.key == k for k in KEY_UP or event.key == k for k in KEY_DOWN):
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
            if any(event.key == k for k in KEY_CONFIRM or event.key == k for k in KEY_CANCEL):
                return "DONE"
        return None

    def update(self, dt, world):
        self.timer += dt
        if self.state == "SAVING" and self.timer >= 0.4:
            from save_system import SaveSystem
            SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, world)
            sound_mgr.play_sfx("confirm")
            self.state = "SAVED"
            self.timer = 0.0

    def draw(self, surf):
        # Center Save Card
        bw, bh = 460, 260
        bx = (SCREEN_WIDTH - bw) // 2
        by = (SCREEN_HEIGHT - bh) // 2
        
        pygame.draw.rect(surf, UI_BORDER_DARK, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=12)
        pygame.draw.rect(surf, WHITE, (bx, by, bw, bh), border_radius=10)
        
        # Header
        head = gfx.fonts["title"].render("SAVE GAME", True, (220, 80, 0))
        surf.blit(head, (bx + (bw - head.get_width()) // 2, by + 18))
        
        if self.state == "CONFIRM":
            # Info Box
            lead_name = self.party[0].nickname if self.party else "None"
            lead_lvl = self.party[0].level if self.party else 5
            loc_str = f"Location: {self.player.current_map}"
            team_str = f"Leader: {lead_name} (Lv.{lead_lvl}) | Team: {len(self.party)}"
            money_str = f"Money: ${self.inventory.money} | Badges: 0"
            
            surf.blit(gfx.fonts["regular"].render(loc_str, True, UI_TEXT), (bx + 30, by + 75))
            surf.blit(gfx.fonts["regular"].render(team_str, True, UI_TEXT), (bx + 30, by + 105))
            surf.blit(gfx.fonts["small"].render(money_str, True, UI_TEXT_MUTED), (bx + 30, by + 135))
            
            q_txt = gfx.fonts["regular"].render("Would you like to save your progress?", True, UI_TEXT)
            surf.blit(q_txt, (bx + (bw - q_txt.get_width()) // 2, by + 168))
            
            # [YES] / [NO] buttons
            for i, opt in enumerate(["YES", "NO"]):
                is_sel = (i == 0 and self.selected_yes) or (i == 1 and not self.selected_yes)
                btn_w, btn_h = 100, 36
                btn_x = bx + 110 + i * 140
                btn_y = by + 205
                
                bdr = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
                bg = (255, 235, 180) if is_sel else UI_BG
                pygame.draw.rect(surf, bdr, (btn_x, btn_y, btn_w, btn_h), border_radius=6)
                pygame.draw.rect(surf, bg, (btn_x + 1, btn_y + 1, btn_w - 2, btn_h - 2), border_radius=5)
                
                btxt = gfx.fonts["regular"].render(opt, True, (200, 80, 0) if is_sel else UI_TEXT)
                surf.blit(btxt, (btn_x + (btn_w - btxt.get_width()) // 2, btn_y + (btn_h - btxt.get_height()) // 2))
        elif self.state == "SAVING":
            stxt = gfx.fonts["large"].render("Saving game progress...", True, UI_TEXT)
            surf.blit(stxt, (bx + (bw - stxt.get_width()) // 2, by + 120))
        elif self.state == "SAVED":
            stxt = gfx.fonts["large"].render("Game saved successfully!", True, (40, 140, 60))
            surf.blit(stxt, (bx + (bw - stxt.get_width()) // 2, by + 110))
            hint = gfx.fonts["small"].render("Press [Z / Enter] to continue", True, UI_TEXT_MUTED)
            surf.blit(hint, (bx + (bw - hint.get_width()) // 2, by + 160))

class StarterSelectScreen:
    def __init__(self):
        self.starters = ["Charmander", "Squirtle", "Bulbasaur", "Pikachu"]
        self.selected_idx = 0
        self.confirmed = False

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
            
        if any(event.key == k for k in KEY_LEFT):
            self.selected_idx = (self.selected_idx - 1) % len(self.starters)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_RIGHT):
            self.selected_idx = (self.selected_idx + 1) % len(self.starters)
            sound_mgr.play_sfx("select")
        elif any(event.key == k for k in KEY_CONFIRM):
            sound_mgr.play_sfx("confirm")
            return self.starters[self.selected_idx]
        return None

    def draw(self, surf):
        surf.fill((235, 240, 248))
        
        # Header
        head_txt = gfx.fonts["title"].render("CHOOSE YOUR STARTER", True, UI_TEXT)
        surf.blit(head_txt, (SCREEN_WIDTH // 2 - head_txt.get_width() // 2, 40))
        
        sub_txt = gfx.fonts["regular"].render("Professor Oak: Which Pokémon will you begin your journey with?", True, UI_TEXT_MUTED)
        surf.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 90))

        # 4 Starter Cards
        card_w, card_h = 160, 300
        start_x = (SCREEN_WIDTH - (len(self.starters) * 175)) // 2 + 10
        
        for i, name in enumerate(self.starters):
            cx = start_x + i * 175
            cy = 140
            is_sel = (i == self.selected_idx)
            
            # Card Background
            bdr_col = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
            bg_col = (255, 248, 230) if is_sel else WHITE
            pygame.draw.rect(surf, bdr_col, (cx - 2, cy - 2, card_w + 4, card_h + 4), border_radius=12)
            pygame.draw.rect(surf, bg_col, (cx, cy, card_w, card_h), border_radius=10)
            
            if is_sel:
                # Selector highlight crown
                pygame.draw.polygon(surf, (240, 140, 40), [(cx + card_w // 2 - 10, cy - 12), (cx + card_w // 2 + 10, cy - 12), (cx + card_w // 2, cy - 4)])
            
            # Pokemon Sprite
            p_surf = gfx.get_pokemon_sprite(name, is_back=False, size=(120, 120))
            surf.blit(p_surf, (cx + 20, cy + 20))
            
            # Name
            ntxt = gfx.fonts["regular"].render(name, True, UI_TEXT)
            surf.blit(ntxt, (cx + (card_w - ntxt.get_width()) // 2, cy + 150))
            
            # Types
            data = POKEMON_SPECIES[name]
            for t_idx, t_name in enumerate(data["types"]):
                gfx.draw_type_badge(surf, t_name, cx + 25 + t_idx * 55, cy + 185, width=50, height=20)
                
            # Base Stats Preview
            base_hp = data["base_stats"]["hp"]
            base_atk = data["base_stats"]["atk"]
            base_spd = data["base_stats"]["spd"]
            stat_lbl = gfx.fonts["small"].render(f"HP: {base_hp}  ATK: {base_atk}", True, UI_TEXT_MUTED)
            surf.blit(stat_lbl, (cx + (card_w - stat_lbl.get_width()) // 2, cy + 225))
            spd_lbl = gfx.fonts["small"].render(f"SPD: {base_spd}", True, UI_TEXT_MUTED)
            surf.blit(spd_lbl, (cx + (card_w - spd_lbl.get_width()) // 2, cy + 245))

        prompt = gfx.fonts["medium"].render("Press [Z / Enter] to Confirm Starter Choice", True, (200, 80, 0))
        surf.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 490))

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
        sub = gfx.fonts["regular"].render(f"Seen: {seen_count}   Caught: {caught_count}", True, UI_TEXT_MUTED)
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

        # Bottom back hint
        back_hint = gfx.fonts["small"].render("Press [X / ESC / ENTER] to return", True, UI_TEXT_MUTED)
        surf.blit(back_hint, (SCREEN_WIDTH - back_hint.get_width() - 30, 575))

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
