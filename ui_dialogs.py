"""
ui_dialogs.py - In-game Dialogue Box overlay and Move Reroll interface.
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

class MoveRerollScreen:
    """
    Interactive Pokémon Move Master & Reroll Tutor Screen.
    Allows inspecting party Pokémon, viewing their active moves with stats and descriptions,
    and rerolling or choosing new techniques from species learnsets for 3,000 coins.
    """
    def __init__(self, party, inventory):
        self.party = party
        self.inventory = inventory
        self.selected_pkmn_idx = 0
        self.mode = "MENU" # "MENU", "REPLACE_SLOT", "CATALOGUE"
        self.menu_idx = 0 # 0: REROLL RANDOM ($3,000), 1: BROWSE CATALOGUE ($3,000), 2: CANCEL
        self.selected_slot = 0 # 0-3 for current moves
        self.catalogue_idx = 0
        self.catalogue_scroll = 0
        self.pending_move = None
        self.cost = 3000
        self.message = "Choose a Pokémon to reroll or learn a new move for 3,000 coins!"
        self.success_timer = 0.0

    def update(self, dt):
        if self.success_timer > 0:
            self.success_timer -= dt

    def get_active_pokemon(self):
        if self.party and 0 <= self.selected_pkmn_idx < len(self.party):
            return self.party[self.selected_pkmn_idx]
        return None

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        pkmn = self.get_active_pokemon()
        if not pkmn:
            if any(event.key == k for k in KEY_CANCEL + KEY_CONFIRM):
                return "EXIT"
            return None

        # Mode 1: Main Menu & Party Selection
        if self.mode == "MENU":
            if any(event.key == k for k in KEY_LEFT):
                self.selected_pkmn_idx = (self.selected_pkmn_idx - 1) % len(self.party)
                self.catalogue_idx = 0
                self.catalogue_scroll = 0
                self.message = f"Selected {self.get_active_pokemon().nickname}. Choose an action below."
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_RIGHT):
                self.selected_pkmn_idx = (self.selected_pkmn_idx + 1) % len(self.party)
                self.catalogue_idx = 0
                self.catalogue_scroll = 0
                self.message = f"Selected {self.get_active_pokemon().nickname}. Choose an action below."
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_UP):
                self.menu_idx = (self.menu_idx - 1) % 3
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.menu_idx = (self.menu_idx + 1) % 3
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                return "EXIT"
            elif any(event.key == k for k in KEY_CONFIRM):
                if self.menu_idx == 0: # Random Reroll ($3,000)
                    if self.inventory.money < self.cost:
                        sound_mgr.play_sfx("cancel")
                        self.message = f"You need {self.cost} coins! Current Balance: ${self.inventory.money}"
                        return None
                    candidates = pkmn.get_rerollable_moves()
                    if not candidates:
                        sound_mgr.play_sfx("cancel")
                        self.message = f"{pkmn.nickname} already knows all available moves!"
                        return None
                    self.pending_move = random.choice(candidates)
                    if len(pkmn.moves) < 4:
                        self.inventory.money -= self.cost
                        ok, new_m, old_m, msg = pkmn.reroll_move(specific_move=self.pending_move)
                        sound_mgr.play_sfx("confirm")
                        self.message = f"Success! {pkmn.nickname} learned {new_m} for ${self.cost}!"
                        self.success_timer = 3.0
                    else:
                        sound_mgr.play_sfx("select")
                        self.mode = "REPLACE_SLOT"
                        self.selected_slot = 0
                        self.message = f"Rolled '{self.pending_move}'! Select which move to replace:"
                elif self.menu_idx == 1: # Browse Catalogue ($3,000)
                    candidates = pkmn.get_rerollable_moves()
                    if not candidates:
                        sound_mgr.play_sfx("cancel")
                        self.message = f"{pkmn.nickname} already knows all available moves!"
                        return None
                    sound_mgr.play_sfx("select")
                    self.mode = "CATALOGUE"
                    self.catalogue_idx = 0
                    self.catalogue_scroll = 0
                    self.message = f"Browse {pkmn.nickname}'s compatible techniques. [Z]: Teach for ${self.cost}"
                elif self.menu_idx == 2: # Cancel
                    sound_mgr.play_sfx("cancel")
                    return "EXIT"

        # Mode 2: Selecting Slot to Overwrite (0-3)
        elif self.mode == "REPLACE_SLOT":
            if any(event.key == k for k in KEY_UP):
                self.selected_slot = (self.selected_slot - 1) % len(pkmn.moves)
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.selected_slot = (self.selected_slot + 1) % len(pkmn.moves)
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                self.mode = "MENU"
                self.pending_move = None
                self.message = "Reroll cancelled."
            elif any(event.key == k for k in KEY_CONFIRM):
                if self.inventory.money < self.cost:
                    sound_mgr.play_sfx("cancel")
                    self.message = f"You need {self.cost} coins! Current Balance: ${self.inventory.money}"
                    self.mode = "MENU"
                    return None
                self.inventory.money -= self.cost
                ok, new_m, old_m, msg = pkmn.reroll_move(replace_idx=self.selected_slot, specific_move=self.pending_move)
                sound_mgr.play_sfx("confirm")
                self.message = f"Success! {pkmn.nickname} forgot {old_m} and learned {new_m}!"
                self.success_timer = 3.0
                self.mode = "MENU"
                self.pending_move = None

        # Mode 3: Browse Technique Catalogue
        elif self.mode == "CATALOGUE":
            candidates = pkmn.get_rerollable_moves()
            if not candidates:
                self.mode = "MENU"
                return None
            if any(event.key == k for k in KEY_UP):
                self.catalogue_idx = (self.catalogue_idx - 1) % len(candidates)
                self._adjust_catalogue_scroll(len(candidates))
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.catalogue_idx = (self.catalogue_idx + 1) % len(candidates)
                self._adjust_catalogue_scroll(len(candidates))
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                self.mode = "MENU"
                self.message = "Choose an action below."
            elif any(event.key == k for k in KEY_CONFIRM):
                if self.inventory.money < self.cost:
                    sound_mgr.play_sfx("cancel")
                    self.message = f"You need {self.cost} coins to teach this move! Balance: ${self.inventory.money}"
                    return None
                chosen_move = candidates[self.catalogue_idx]
                self.pending_move = chosen_move
                if len(pkmn.moves) < 4:
                    self.inventory.money -= self.cost
                    ok, new_m, old_m, msg = pkmn.reroll_move(specific_move=self.pending_move)
                    sound_mgr.play_sfx("confirm")
                    self.message = f"Success! {pkmn.nickname} learned {new_m} for ${self.cost}!"
                    self.success_timer = 3.0
                    self.mode = "MENU"
                    self.pending_move = None
                else:
                    sound_mgr.play_sfx("select")
                    self.mode = "REPLACE_SLOT"
                    self.selected_slot = 0
                    self.message = f"Teaching '{self.pending_move}'! Select which current move to replace:"

        return None

    def _adjust_catalogue_scroll(self, total_items):
        if self.catalogue_idx < self.catalogue_scroll:
            self.catalogue_scroll = self.catalogue_idx
        elif self.catalogue_idx >= self.catalogue_scroll + 5:
            self.catalogue_scroll = self.catalogue_idx - 4

    def draw(self, surf):
        surf.fill((235, 240, 248))

        # 1. Top Header
        head = gfx.fonts["title"].render("MOVE MASTER & REROLL TUTOR", True, (210, 80, 20))
        surf.blit(head, (30, 16))

        # Balance & Cost Indicators
        money_txt = gfx.fonts["regular"].render(f"💰 Money: ${self.inventory.money}", True, (30, 140, 50))
        cost_txt = gfx.fonts["regular"].render("⚡ Cost: $3,000", True, (200, 120, 20))
        surf.blit(money_txt, (SCREEN_WIDTH - 380, 20))
        surf.blit(cost_txt, (SCREEN_WIDTH - 180, 20))

        pkmn = self.get_active_pokemon()
        if not pkmn:
            no_pkmn = gfx.fonts["large"].render("No Pokémon in Party!", True, UI_TEXT_MUTED)
            surf.blit(no_pkmn, (SCREEN_WIDTH // 2 - no_pkmn.get_width() // 2, 280))
            return

        # 2. Left Panel: Pokémon Card & Party Carousel
        lx, ly, lw, lh = 30, 68, 240, 412
        pygame.draw.rect(surf, (30, 40, 60), (lx - 2, ly - 2, lw + 4, lh + 4), border_radius=10)
        pygame.draw.rect(surf, WHITE, (lx, ly, lw, lh), border_radius=8)

        # Party Navigation Header
        p_nav = f"◄  {pkmn.nickname} ({self.selected_pkmn_idx + 1}/{len(self.party)})  ►"
        p_nav_txt = gfx.fonts["regular"].render(p_nav, True, (200, 80, 0))
        surf.blit(p_nav_txt, (lx + (lw - p_nav_txt.get_width()) // 2, ly + 14))

        # Sprite
        p_surf = gfx.get_pokemon_sprite(pkmn.species, is_back=False, size=(120, 120))
        surf.blit(p_surf, (lx + (lw - 120) // 2, ly + 44))

        # Details
        lvl_txt = gfx.fonts["regular"].render(f"Lv. {pkmn.level} {pkmn.species}", True, UI_TEXT)
        surf.blit(lvl_txt, (lx + (lw - lvl_txt.get_width()) // 2, ly + 172))

        # Types
        for t_idx, t_name in enumerate(pkmn.types):
            tw = 58
            tx = lx + (lw - len(pkmn.types) * (tw + 6)) // 2 + t_idx * (tw + 6)
            gfx.draw_type_badge(surf, t_name, tx, ly + 204, width=tw, height=22)

        # HP Bar
        gfx.draw_hp_bar(surf, lx + 30, ly + 242, lw - 60, 8, pkmn.current_hp, pkmn.max_hp)
        hp_lbl = gfx.fonts["small"].render(f"HP: {pkmn.current_hp}/{pkmn.max_hp}", True, UI_TEXT_MUTED)
        surf.blit(hp_lbl, (lx + (lw - hp_lbl.get_width()) // 2, ly + 256))

        # Action Buttons on Left Panel
        if self.mode == "MENU":
            btn_labels = ["🎲 RANDOM REROLL ($3,000)", "📖 BROWSE TECHNIQUES", "⬅ RETURN"]
            for b_idx, b_lbl in enumerate(btn_labels):
                is_sel = (b_idx == self.menu_idx)
                by = ly + 285 + b_idx * 38
                bdr = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
                bg = (255, 238, 200) if is_sel else (246, 248, 252)
                pygame.draw.rect(surf, bdr, (lx + 10, by, lw - 20, 32), border_radius=6)
                pygame.draw.rect(surf, bg, (lx + 11, by + 1, lw - 22, 30), border_radius=5)
                b_txt = gfx.fonts["small"].render(b_lbl, True, (200, 80, 0) if is_sel else UI_TEXT)
                surf.blit(b_txt, (lx + (lw - b_txt.get_width()) // 2, by + 7))

        # 3. Center Panel: Current Moves (4 Slots)
        cx, cy, cw, ch = 285, 68, 245, 412
        pygame.draw.rect(surf, (30, 40, 60), (cx - 2, cy - 2, cw + 4, ch + 4), border_radius=10)
        pygame.draw.rect(surf, WHITE, (cx, cy, cw, ch), border_radius=8)

        moves_head = gfx.fonts["regular"].render("CURRENT MOVESET", True, (40, 80, 160))
        surf.blit(moves_head, (cx + (cw - moves_head.get_width()) // 2, cy + 12))

        for m_idx in range(4):
            slot_y = cy + 42 + m_idx * 90
            is_slot_sel = (self.mode == "REPLACE_SLOT" and m_idx == self.selected_slot)
            
            card_bdr = (240, 100, 20) if is_slot_sel else (UI_BORDER_LIGHT if m_idx < len(pkmn.moves) else (210, 215, 225))
            card_bg = (255, 235, 190) if is_slot_sel else ((250, 252, 255) if m_idx < len(pkmn.moves) else (240, 242, 245))

            pygame.draw.rect(surf, card_bdr, (cx + 10, slot_y, cw - 20, 82), 2 if is_slot_sel else 1, border_radius=8)
            pygame.draw.rect(surf, card_bg, (cx + 11, slot_y + 1, cw - 22, 80), border_radius=7)

            if m_idx < len(pkmn.moves):
                m_data = pkmn.moves[m_idx]
                # Move Name
                m_name_txt = gfx.fonts["medium"].render(m_data["name"], True, (200, 60, 0) if is_slot_sel else UI_TEXT)
                surf.blit(m_name_txt, (cx + 18, slot_y + 8))
                
                # Type Badge & Category
                gfx.draw_type_badge(surf, m_data.get("type", "Normal"), cx + 18, slot_y + 34, width=54, height=18)
                cat_txt = gfx.fonts["small"].render(m_data.get("category", "Physical"), True, UI_TEXT_MUTED)
                surf.blit(cat_txt, (cx + 80, slot_y + 36))

                # Power, Acc, PP
                pwr = m_data.get("power", 0)
                pwr_str = f"Pwr: {pwr if pwr > 0 else '--'}"
                acc_str = f"Acc: {m_data.get('accuracy', 100)}%"
                pp_str = f"PP: {m_data.get('pp', 0)}/{m_data.get('max_pp', 0)}"

                stat_line = f"{pwr_str}  {acc_str}  {pp_str}"
                stat_txt = gfx.fonts["small"].render(stat_line, True, UI_TEXT_MUTED)
                surf.blit(stat_txt, (cx + 18, slot_y + 58))
                
                if is_slot_sel:
                    ovr_txt = gfx.fonts["small"].render("▶ REPLACE THIS ◀", True, (220, 40, 20))
                    surf.blit(ovr_txt, (cx + cw - ovr_txt.get_width() - 18, slot_y + 10))
            else:
                empty_txt = gfx.fonts["regular"].render("- Empty Slot -", True, (160, 165, 175))
                surf.blit(empty_txt, (cx + (cw - empty_txt.get_width()) // 2, slot_y + 30))

        # 4. Right Panel: Technique Catalogue / Move Detail / Action Box
        rx, ry, rw, rh = 545, 68, 225, 412
        pygame.draw.rect(surf, (30, 40, 60), (rx - 2, ry - 2, rw + 4, rh + 4), border_radius=10)
        pygame.draw.rect(surf, WHITE, (rx, ry, rw, rh), border_radius=8)

        candidates = pkmn.get_rerollable_moves()

        if self.mode == "CATALOGUE":
            cat_head = gfx.fonts["regular"].render("TECHNIQUE POOL", True, (40, 120, 220))
            surf.blit(cat_head, (rx + (rw - cat_head.get_width()) // 2, ry + 12))

            visible_cnt = min(5, len(candidates))
            for i in range(visible_cnt):
                idx = self.catalogue_scroll + i
                if idx >= len(candidates):
                    break
                m_name = candidates[idx]
                m_info = MOVES.get(m_name, {})
                is_cat_sel = (idx == self.catalogue_idx)

                cy_row = ry + 42 + i * 44
                cbdr = (240, 140, 40) if is_cat_sel else (220, 225, 235)
                cbg = (255, 235, 180) if is_cat_sel else ((248, 250, 255) if i % 2 == 0 else WHITE)

                pygame.draw.rect(surf, cbdr, (rx + 8, cy_row, rw - 16, 40), 2 if is_cat_sel else 1, border_radius=6)
                pygame.draw.rect(surf, cbg, (rx + 9, cy_row + 1, rw - 18, 38), border_radius=5)

                mtxt = gfx.fonts["small"].render(m_name, True, (200, 80, 0) if is_cat_sel else UI_TEXT)
                surf.blit(mtxt, (rx + 14, cy_row + 4))

                m_t = m_info.get("type", "Normal")
                gfx.draw_type_badge(surf, m_t, rx + 14, cy_row + 20, width=44, height=16)

                pw = m_info.get("power", 0)
                pw_txt = gfx.fonts["small"].render(f"Pwr:{pw if pw > 0 else '--'}", True, UI_TEXT_MUTED)
                surf.blit(pw_txt, (rx + rw - pw_txt.get_width() - 14, cy_row + 20))

            # Selected Move Preview at bottom of right card
            if candidates and 0 <= self.catalogue_idx < len(candidates):
                sel_m = candidates[self.catalogue_idx]
                sel_d = MOVES.get(sel_m, {})
                desc_y = ry + 270
                pygame.draw.rect(surf, (244, 247, 252), (rx + 8, desc_y, rw - 16, 130), border_radius=6)
                
                # Word wrap
                words = sel_d.get("desc", "").split(" ")
                lines, cur = [], ""
                for w in words:
                    t = cur + (" " if cur else "") + w
                    if gfx.fonts["small"].size(t)[0] < rw - 32:
                        cur = t
                    else:
                        lines.append(cur)
                        cur = w
                if cur:
                    lines.append(cur)
                for l_idx, l_str in enumerate(lines[:4]):
                    surf.blit(gfx.fonts["small"].render(l_str, True, UI_TEXT), (rx + 14, desc_y + 8 + l_idx * 18))

                teach_hint = gfx.fonts["small"].render("Press [Z] to Teach ($3,000)", True, (220, 80, 0))
                surf.blit(teach_hint, (rx + (rw - teach_hint.get_width()) // 2, desc_y + 104))

        elif self.mode == "REPLACE_SLOT":
            p_head = gfx.fonts["regular"].render("NEW TECHNIQUE", True, (220, 60, 20))
            surf.blit(p_head, (rx + (rw - p_head.get_width()) // 2, ry + 16))

            if self.pending_move:
                p_data = MOVES.get(self.pending_move, {})
                pn_txt = gfx.fonts["large"].render(self.pending_move, True, (200, 60, 0))
                surf.blit(pn_txt, (rx + (rw - pn_txt.get_width()) // 2, ry + 50))

                gfx.draw_type_badge(surf, p_data.get("type", "Normal"), rx + 20, ry + 90, width=58, height=22)
                p_pwr = p_data.get("power", 0)
                pwr_l = gfx.fonts["regular"].render(f"Power: {p_pwr if p_pwr > 0 else '--'}", True, UI_TEXT)
                acc_l = gfx.fonts["regular"].render(f"Accuracy: {p_data.get('accuracy', 100)}%", True, UI_TEXT)
                cat_l = gfx.fonts["regular"].render(f"Category: {p_data.get('category', 'Physical')}", True, UI_TEXT_MUTED)
                surf.blit(pwr_l, (rx + 20, ry + 125))
                surf.blit(acc_l, (rx + 20, ry + 155))
                surf.blit(cat_l, (rx + 20, ry + 185))

                # Instructions
                inst = gfx.fonts["small"].render("Choose a slot in Center", True, (40, 80, 160))
                inst2 = gfx.fonts["small"].render("to overwrite with this move!", True, (40, 80, 160))
                surf.blit(inst, (rx + (rw - inst.get_width()) // 2, ry + 260))
                surf.blit(inst2, (rx + (rw - inst2.get_width()) // 2, ry + 282))

        else: # MENU mode on right
            info_head = gfx.fonts["regular"].render("TUTOR GUIDE", True, (40, 120, 220))
            surf.blit(info_head, (rx + (rw - info_head.get_width()) // 2, ry + 16))

            guide_lines = [
                "The Move Master can",
                "teach any technique",
                "from your species' full",
                "learnset & elemental",
                "technique repertoire!",
                "",
                "★ Fee: $3,000 per move",
                "★ Replace any of the 4",
                "   active move slots",
                "★ Unlimited rerolls!"
            ]
            for g_idx, g_str in enumerate(guide_lines):
                c = (200, 80, 0) if "★" in g_str else UI_TEXT_MUTED
                f = gfx.fonts["small"]
                gtxt = f.render(g_str, True, c)
                surf.blit(gtxt, (rx + 16, ry + 54 + g_idx * 22))

        # 5. Bottom Message Box
        bx, by, bw, bh = 30, 492, SCREEN_WIDTH - 60, 78
        pygame.draw.rect(surf, (30, 40, 60), (bx - 2, by - 2, bw + 4, bh + 4), border_radius=8)
        pygame.draw.rect(surf, UI_BG, (bx, by, bw, bh), border_radius=6)

        msg_c = (40, 140, 60) if self.success_timer > 0 else UI_TEXT
        surf.blit(gfx.fonts["regular"].render(self.message, True, msg_c), (bx + 20, by + 26))

class DialogueBox:
    def __init__(self, speaker_name, text, on_complete=None, portrait_key=None, trainer_data=None):
        self.speaker = speaker_name
        self.full_text = text
        self.visible_chars = 0
        self.speed = 40.0
        self.on_complete = on_complete
        self.finished = False
        self.portrait_key = portrait_key or (trainer_data.get("id") if isinstance(trainer_data, dict) else speaker_name)
        self.trainer_data = trainer_data
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt
        if not self.finished:
            self.visible_chars += self.speed * dt
            if self.visible_chars >= len(self.full_text):
                self.visible_chars = len(self.full_text)
                self.finished = True

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return False
        if any(event.key == k for k in KEY_CONFIRM + KEY_CANCEL) or event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_z, pygame.K_x]:
            if not self.finished:
                self.visible_chars = len(self.full_text)
                self.finished = True
                sound_mgr.play_sfx("select")
                return False
            else:
                sound_mgr.play_sfx("confirm")
                if self.on_complete:
                    self.on_complete()
                return True
        return False

    def draw(self, surf):
        # Frame dimensions
        bx, by, bw, bh = 30, 410, SCREEN_WIDTH - 60, 160
        
        # Dialogue Box Base & Shadow
        pygame.draw.rect(surf, (20, 24, 35), (bx - 2, by - 2, bw + 4, bh + 4), border_radius=12)
        pygame.draw.rect(surf, (252, 252, 255), (bx, by, bw, bh), border_radius=10)
        pygame.draw.rect(surf, UI_BORDER_LIGHT, (bx, by, bw, bh), 2, border_radius=10)

        # 1. Portrait Frame (Left Side)
        has_portrait = bool(self.portrait_key)
        # Determine if mouth is currently talking (animating between open/closed while streaming text)
        is_talking = (not self.finished) and (int(self.visible_chars * 3.5) % 2 == 1)
        
        text_start_x = bx + 24
        text_max_w = bw - 48
        
        if has_portrait:
            portrait_size = (110, 110)
            if self.portrait_key in POKEMON_SPECIES:
                port_surf = gfx.get_pokemon_sprite(self.portrait_key, is_back=False, size=portrait_size)
            else:
                port_surf = gfx.get_trainer_portrait(self.portrait_key, size=portrait_size, is_talking=is_talking)
            
            px = bx + 16
            py = by + (bh - portrait_size[1]) // 2 + 6
            
            # Subtle card drop shadow behind portrait
            pygame.draw.rect(surf, (30, 36, 48), (px - 3, py - 3, portrait_size[0] + 6, portrait_size[1] + 6), border_radius=10)
            pygame.draw.rect(surf, (245, 248, 255), (px - 1, py - 1, portrait_size[0] + 2, portrait_size[1] + 2), border_radius=8)
            surf.blit(port_surf, (px, py))
            
            # Adjust text margins
            text_start_x = px + portrait_size[0] + 22
            text_max_w = bw - (text_start_x - bx) - 24

        # 2. Speaker Name Tag Badge
        if self.speaker:
            # Customize badge colors based on character identity
            sp_lower = self.speaker.lower()
            if "leader" in sp_lower or "brock" in sp_lower or "misty" in sp_lower:
                badge_bg = (255, 245, 210)
                badge_bdr = (220, 175, 40)
                badge_txt_c = (190, 110, 10)
            elif "rocket" in sp_lower:
                badge_bg = (255, 230, 230)
                badge_bdr = (220, 40, 40)
                badge_txt_c = (180, 20, 20)
            elif "rival" in sp_lower or "blue" in sp_lower:
                badge_bg = (230, 245, 255)
                badge_bdr = (60, 170, 240)
                badge_txt_c = (20, 90, 180)
            elif "item" in sp_lower:
                badge_bg = (255, 240, 220)
                badge_bdr = (240, 100, 40)
                badge_txt_c = (200, 60, 0)
            elif "notice" in sp_lower or "sign" in sp_lower:
                badge_bg = (245, 235, 215)
                badge_bdr = (160, 110, 60)
                badge_txt_c = (120, 70, 25)
            else:
                badge_bg = (255, 242, 220)
                badge_bdr = (240, 140, 40)
                badge_txt_c = (180, 60, 0)

            speaker_display = f"{self.speaker}"
            sw = gfx.fonts["regular"].size(speaker_display)[0] + 28
            sx = bx + 20
            sy = by - 16
            
            pygame.draw.rect(surf, (30, 36, 50), (sx - 2, sy - 2, sw + 4, 32), border_radius=7)
            pygame.draw.rect(surf, badge_bg, (sx, sy, sw, 28), border_radius=6)
            pygame.draw.rect(surf, badge_bdr, (sx, sy, sw, 28), 2, border_radius=6)
            stxt = gfx.fonts["regular"].render(speaker_display, True, badge_txt_c)
            surf.blit(stxt, (sx + 14, sy + 4))

        # 3. Typewriter Text Rendering with Line Wrapping
        disp_text = self.full_text[:int(self.visible_chars)]
        words = disp_text.split(" ")
        lines = []
        curr_line = ""
        for w in words:
            test = curr_line + (" " if curr_line else "") + w
            if gfx.fonts["medium"].size(test)[0] < text_max_w:
                curr_line = test
            else:
                lines.append(curr_line)
                curr_line = w
        if curr_line:
            lines.append(curr_line)

        for i, l_str in enumerate(lines[:3]):
            ltxt = gfx.fonts["medium"].render(l_str, True, UI_TEXT)
            surf.blit(ltxt, (text_start_x, by + 26 + i * 34))

        # 4. Blinking Continue Arrow Indicator
        if self.finished:
            if int(self.timer * 4.0) % 2 == 0:
                arrow_surf = gfx.fonts["small"].render("[Z / Enter] ▼", True, (220, 90, 20))
                surf.blit(arrow_surf, (bx + bw - arrow_surf.get_width() - 20, by + bh - 24))
