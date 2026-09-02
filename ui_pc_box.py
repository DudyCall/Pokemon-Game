"""
ui_pc_box.py - Pokémon Storage System (PC Box) Screen.
Includes interactive Evolution & Level Progression Chart, Active Starter assignment,
and moving / reordering between Party and PC Box.
"""
import math
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY,
    UI_BG, UI_BORDER_DARK, UI_BORDER_LIGHT, UI_TEXT, UI_TEXT_MUTED,
    HP_GREEN, HP_YELLOW, HP_RED, EXP_BLUE, TYPE_COLORS,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_CONFIRM, KEY_CANCEL, KEY_MENU
)
from graphics_manager import gfx
from sound_manager import sound_mgr
from pokemon_data import (
    POKEMON_SPECIES, ITEMS, MOVES, STONE_EVOLUTIONS,
    get_pokemon_evolution_info, get_full_evolution_tree
)

class PCBoxScreen:
    """
    Comprehensive Pokémon Storage System (PC Box) screen with interactive
    Evolution & Level Progression Chart.
    Allows withdrawing, depositing, swapping, inspecting stats, and tracking
    evolution level milestones and stone requirements for all active & stored Pokémon.
    """
    def __init__(self, party, pc_box, inventory=None):
        self.party = party
        self.pc_box = pc_box
        self.inventory = inventory
        self.active_panel = "PARTY" if len(party) > 0 else "PC" # "PARTY" or "PC"
        self.party_idx = 0
        self.pc_idx = 0
        self.pc_scroll = 0
        self.menu_mode = "NAVIGATE" # "NAVIGATE", "ACTIONS", "SUMMARY", "EVOLUTION_CHART"
        self.action_idx = 0
        self.summary_pokemon = None
        self.evolution_pokemon = None
        self.moving_source = None  # None or ("PARTY"|"PC", index)
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

    def _get_current_selected_pokemon(self):
        if self.active_panel == "PARTY" and len(self.party) > self.party_idx:
            return self.party[self.party_idx]
        elif self.active_panel == "PC" and len(self.pc_box) > self.pc_idx:
            return self.pc_box[self.pc_idx]
        return None

    def _start_move(self):
        sel = self._get_current_selected_pokemon()
        if not sel:
            self.show_notification("No Pokémon selected to move!")
            sound_mgr.play_sfx("cancel")
            return
        idx = self.party_idx if self.active_panel == "PARTY" else self.pc_idx
        self.moving_source = (self.active_panel, idx)
        name = sel.nickname or sel.species
        self.show_notification(f"Moving {name}! Navigate to target slot and press [Z/Enter] to place.")
        sound_mgr.play_sfx("select")

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        # 1. Evolution Progression Chart Mode View
        if self.menu_mode == "EVOLUTION_CHART":
            if any(event.key == k for k in KEY_CONFIRM + KEY_CANCEL) or event.key in [pygame.K_ESCAPE, pygame.K_e, pygame.K_p, pygame.K_TAB]:
                sound_mgr.play_sfx("cancel")
                self.menu_mode = "NAVIGATE"
                self.evolution_pokemon = None
            elif any(event.key == k for k in KEY_UP):
                if self.active_panel == "PARTY" and len(self.party) > 0:
                    self.party_idx = (self.party_idx - 1) % len(self.party)
                    self.evolution_pokemon = self.party[self.party_idx]
                    sound_mgr.play_sfx("select")
                elif self.active_panel == "PC" and len(self.pc_box) > 0:
                    self.pc_idx = (self.pc_idx - 1) % len(self.pc_box)
                    self._adjust_pc_scroll()
                    self.evolution_pokemon = self.pc_box[self.pc_idx]
                    sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                if self.active_panel == "PARTY" and len(self.party) > 0:
                    self.party_idx = (self.party_idx + 1) % len(self.party)
                    self.evolution_pokemon = self.party[self.party_idx]
                    sound_mgr.play_sfx("select")
                elif self.active_panel == "PC" and len(self.pc_box) > 0:
                    self.pc_idx = (self.pc_idx + 1) % len(self.pc_box)
                    self._adjust_pc_scroll()
                    self.evolution_pokemon = self.pc_box[self.pc_idx]
                    sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_LEFT):
                if self.active_panel == "PC" and len(self.party) > 0:
                    self.active_panel = "PARTY"
                    self.party_idx = min(self.party_idx, len(self.party) - 1)
                    self.evolution_pokemon = self.party[self.party_idx]
                    sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_RIGHT):
                if self.active_panel == "PARTY" and len(self.pc_box) > 0:
                    self.active_panel = "PC"
                    self.pc_idx = min(self.pc_idx, len(self.pc_box) - 1)
                    self._adjust_pc_scroll()
                    self.evolution_pokemon = self.pc_box[self.pc_idx]
                    sound_mgr.play_sfx("select")
            return None

        # 2. Summary Mode View
        if self.menu_mode == "SUMMARY":
            if any(event.key == k for k in KEY_CONFIRM + KEY_CANCEL) or event.key in [pygame.K_ESCAPE]:
                sound_mgr.play_sfx("cancel")
                self.menu_mode = "NAVIGATE"
                self.summary_pokemon = None
            elif event.key in [pygame.K_e, pygame.K_p, pygame.K_TAB]:
                # Switch directly to evolution progression chart from summary
                sound_mgr.play_sfx("confirm")
                self.evolution_pokemon = self.summary_pokemon
                self.menu_mode = "EVOLUTION_CHART"
            return None

        # 3. Action Sub-Menu Mode
        if self.menu_mode == "ACTIONS":
            actions = self._get_available_actions()
            if any(event.key == k for k in KEY_UP):
                self.action_idx = (self.action_idx - 1) % len(actions)
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.action_idx = (self.action_idx + 1) % len(actions)
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_CANCEL) or event.key in [pygame.K_ESCAPE]:
                sound_mgr.play_sfx("cancel")
                self.menu_mode = "NAVIGATE"
            elif any(event.key == k for k in KEY_CONFIRM):
                chosen_action = actions[self.action_idx]
                self._execute_action(chosen_action)
            return None

        # 4. Main Navigation Mode
        # Quick hotkey for Evolution / Progression Chart: E, P, or Tab
        # Quick hotkey for Evolution / Progression Chart: E, P, or Tab
        if event.key in [pygame.K_e, pygame.K_p, pygame.K_TAB]:
            sel_pkmn = self._get_current_selected_pokemon()
            if sel_pkmn:
                tgt = sel_pkmn.check_evolution()
                if tgt:
                    old_name = sel_pkmn.nickname
                    sel_pkmn.evolve(tgt)
                    sound_mgr.play_sfx("level_up")
                    self.show_notification(f"★ Congratulations! {old_name} evolved into {tgt.upper()}!")
                else:
                    self.evolution_pokemon = sel_pkmn
                    self.menu_mode = "EVOLUTION_CHART"
                    sound_mgr.play_sfx("confirm")
            else:
                self.show_notification("No Pokémon selected!")
            return None

        # Quick hotkey to Move / Reorder: M
        if event.key == pygame.K_m:
            if self.moving_source is not None:
                self.moving_source = None
                self.show_notification("Move cancelled.")
                sound_mgr.play_sfx("cancel")
            else:
                self._start_move()
            return None

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
            if self.moving_source is not None:
                # Execute move / swap
                src_panel, src_idx = self.moving_source
                dst_panel = self.active_panel
                dst_idx = self.party_idx if dst_panel == "PARTY" else self.pc_idx

                if src_panel == dst_panel and src_idx == dst_idx:
                    self.moving_source = None
                    self.show_notification("Placed back in same slot.")
                    sound_mgr.play_sfx("confirm")
                    return None

                if src_panel == "PARTY" and dst_panel == "PARTY":
                    if src_idx < len(self.party) and dst_idx < len(self.party):
                        p_src = self.party[src_idx]
                        p_dst = self.party[dst_idx]
                        self.party[src_idx], self.party[dst_idx] = self.party[dst_idx], self.party[src_idx]
                        s_note = " (Now Battle Starter!)" if dst_idx == 0 else ""
                        self.show_notification(f"Swapped {p_src.nickname or p_src.species} with {p_dst.nickname or p_dst.species}!{s_note}")
                        sound_mgr.play_sfx("confirm")
                elif src_panel == "PC" and dst_panel == "PC":
                    if src_idx < len(self.pc_box) and dst_idx < len(self.pc_box):
                        p_src = self.pc_box[src_idx]
                        p_dst = self.pc_box[dst_idx]
                        self.pc_box[src_idx], self.pc_box[dst_idx] = self.pc_box[dst_idx], self.pc_box[src_idx]
                        self.show_notification(f"Reordered {p_src.nickname or p_src.species} and {p_dst.nickname or p_dst.species} in PC!")
                        sound_mgr.play_sfx("confirm")
                elif src_panel == "PARTY" and dst_panel == "PC":
                    if len(self.party) <= 1 and dst_idx >= len(self.pc_box):
                        self.show_notification("Cannot deposit your only Pokémon!")
                        sound_mgr.play_sfx("cancel")
                    elif dst_idx < len(self.pc_box):
                        p_party = self.party[src_idx]
                        p_pc = self.pc_box[dst_idx]
                        self.party[src_idx] = p_pc
                        self.pc_box[dst_idx] = p_party
                        self.show_notification(f"Swapped {p_party.nickname or p_party.species} with {p_pc.nickname or p_pc.species}!")
                        sound_mgr.play_sfx("confirm")
                    else:
                        if len(self.party) <= 1:
                            self.show_notification("Cannot deposit your last Pokémon!")
                            sound_mgr.play_sfx("cancel")
                        else:
                            p_party = self.party.pop(src_idx)
                            self.pc_box.append(p_party)
                            self.party_idx = max(0, min(len(self.party) - 1, self.party_idx))
                            self.show_notification(f"Deposited {p_party.nickname or p_party.species} into PC!")
                            sound_mgr.play_sfx("confirm")
                elif src_panel == "PC" and dst_panel == "PARTY":
                    if dst_idx < len(self.party):
                        p_pc = self.pc_box[src_idx]
                        p_party = self.party[dst_idx]
                        self.pc_box[src_idx] = p_party
                        self.party[dst_idx] = p_pc
                        s_note = " (Now Battle Starter!)" if dst_idx == 0 else ""
                        self.show_notification(f"Swapped {p_pc.nickname or p_pc.species} with {p_party.nickname or p_party.species}!{s_note}")
                        sound_mgr.play_sfx("confirm")
                    elif len(self.party) < 6:
                        p_pc = self.pc_box.pop(src_idx)
                        self.party.append(p_pc)
                        self.pc_idx = max(0, min(len(self.pc_box) - 1, self.pc_idx))
                        self._adjust_pc_scroll()
                        self.show_notification(f"Withdrew {p_pc.nickname or p_pc.species} to Party!")
                        sound_mgr.play_sfx("confirm")

                self.moving_source = None
                return None

            if (self.active_panel == "PARTY" and len(self.party) > 0) or (self.active_panel == "PC" and len(self.pc_box) > 0):
                self.menu_mode = "ACTIONS"
                self.action_idx = 0
                sound_mgr.play_sfx("confirm")
            else:
                self.show_notification("No Pokémon selected in this panel!")
        elif any(event.key == k for k in KEY_CANCEL) or event.key in [pygame.K_ESCAPE]:
            if self.moving_source is not None:
                self.moving_source = None
                self.show_notification("Move cancelled.")
                sound_mgr.play_sfx("cancel")
                return None
            sound_mgr.play_sfx("cancel")
            return "EXIT"

        return None

    def _adjust_pc_scroll(self):
        if self.pc_idx < self.pc_scroll:
            self.pc_scroll = self.pc_idx
        elif self.pc_idx >= self.pc_scroll + 6:
            self.pc_scroll = self.pc_idx - 5

    def _get_available_actions(self):
        sel = self._get_current_selected_pokemon()
        evo_act = [f"★ EVOLVE INTO {sel.check_evolution().upper()}!"] if (sel and sel.check_evolution()) else []
        if self.active_panel == "PARTY":
            starter_act = ["SET AS STARTER (SLOT 1)"] if self.party_idx != 0 else []
            return evo_act + starter_act + ["MOVE / REORDER POKEMON", "DEPOSIT TO PC", "SWAP WITH PC", "SUMMARY", "EVOLUTION PROGRESSION", "CANCEL"]
        else:
            starter_act = ["SET AS STARTER (WITHDRAW TO LEAD)"]
            return evo_act + starter_act + ["MOVE / REORDER POKEMON", "WITHDRAW TO PARTY", "SWAP WITH PARTY", "SUMMARY", "EVOLUTION PROGRESSION", "CANCEL"]

    def _execute_action(self, action):
        if "EVOLVE INTO" in action:
            sel = self._get_current_selected_pokemon()
            if sel and sel.check_evolution():
                tgt = sel.check_evolution()
                old_name = sel.nickname
                sel.evolve(tgt)
                sound_mgr.play_sfx("level_up")
                self.show_notification(f"★ Congratulations! {old_name} evolved into {tgt.upper()}!")
                self.menu_mode = "NAVIGATE"
        elif "SET AS STARTER" in action:
            if self.active_panel == "PARTY":
                if self.party_idx == 0:
                    self.show_notification(f"{self.party[0].nickname or self.party[0].species} is already your Starter!")
                    sound_mgr.play_sfx("cancel")
                else:
                    pkmn = self.party.pop(self.party_idx)
                    self.party.insert(0, pkmn)
                    self.party_idx = 0
                    self.show_notification(f"★ {pkmn.nickname or pkmn.species} is now your Battle Starter (Slot 1)!")
                    sound_mgr.play_sfx("confirm")
            elif self.active_panel == "PC":
                if len(self.pc_box) > self.pc_idx:
                    p_pc = self.pc_box.pop(self.pc_idx)
                    if len(self.party) >= 6:
                        p_old_lead = self.party[0]
                        self.party[0] = p_pc
                        self.pc_box.insert(self.pc_idx, p_old_lead)
                        self.show_notification(f"★ {p_pc.nickname or p_pc.species} is now Starter (swapped with {p_old_lead.species})!")
                    else:
                        self.party.insert(0, p_pc)
                        self.show_notification(f"★ {p_pc.nickname or p_pc.species} withdrawn as Battle Starter (Slot 1)!")
                    self.active_panel = "PARTY"
                    self.party_idx = 0
                    self._adjust_pc_scroll()
                    sound_mgr.play_sfx("confirm")
            self.menu_mode = "NAVIGATE"

        elif "MOVE / REORDER" in action:
            self.menu_mode = "NAVIGATE"
            self._start_move()

        elif action == "DEPOSIT TO PC":
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
            sel = self._get_current_selected_pokemon()
            if sel:
                self.summary_pokemon = sel
                self.menu_mode = "SUMMARY"
                sound_mgr.play_sfx("confirm")

        elif action == "EVOLUTION PROGRESSION":
            sel = self._get_current_selected_pokemon()
            if sel:
                self.evolution_pokemon = sel
                self.menu_mode = "EVOLUTION_CHART"
                sound_mgr.play_sfx("confirm")

        elif action == "CANCEL":
            self.menu_mode = "NAVIGATE"
            sound_mgr.play_sfx("cancel")

    def draw(self, surf):
        # Background
        surf.fill((228, 236, 248))

        # Title Header
        title_txt = gfx.fonts["title"].render("POKÉMON STORAGE SYSTEM", True, (20, 70, 160))
        sub_txt = gfx.fonts["regular"].render("Manage battle team, storage PC box & track evolution level requirements", True, UI_TEXT_MUTED)
        surf.blit(title_txt, (SCREEN_WIDTH // 2 - title_txt.get_width() // 2, 14))
        surf.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 50))

        # 1. Left Column: Active Party (Max 6)
        lx, ly, lw, lh = 35, 82, 350, 468
        is_party_active = (self.active_panel == "PARTY")
        bdr_color = (240, 140, 40) if is_party_active else UI_BORDER_LIGHT
        pygame.draw.rect(surf, bdr_color, (lx - 2, ly - 2, lw + 4, lh + 4), border_radius=12)
        pygame.draw.rect(surf, WHITE, (lx, ly, lw, lh), border_radius=10)

        p_header = gfx.fonts["large"].render(f"ACTIVE TEAM ({len(self.party)}/6)", True, (20, 80, 180) if is_party_active else UI_TEXT)
        surf.blit(p_header, (lx + 20, ly + 12))

        # Party Slot Cards (Up to 6)
        for i in range(6):
            cy = ly + 46 + i * 68
            cw, ch = lw - 30, 62
            cx = lx + 15

            if i < len(self.party):
                p = self.party[i]
                is_sel = (is_party_active and i == self.party_idx)
                is_being_moved = (self.moving_source == ("PARTY", i))
                if is_being_moved:
                    card_bdr = (255, 140, 0)
                    card_bg = (255, 230, 180)
                else:
                    card_bdr = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
                    card_bg = (255, 248, 230) if is_sel else (250, 252, 255)

                pygame.draw.rect(surf, card_bdr, (cx, cy, cw, ch), border_radius=8)
                pygame.draw.rect(surf, card_bg, (cx + 1, cy + 1, cw - 2, ch - 2), border_radius=7)

                if is_being_moved:
                    m_tag = gfx.fonts["small"].render("HOLDING", True, (210, 60, 0))
                    surf.blit(m_tag, (cx + cw - 70 - m_tag.get_width() - 8, cy + 6))
                elif i == 0:
                    s_tag = gfx.fonts["small"].render("STARTER", True, (210, 120, 10))
                    surf.blit(s_tag, (cx + cw - 70 - s_tag.get_width() - 8, cy + 6))

                # Mini Sprite
                sprite = gfx.get_pokemon_sprite(p.species, is_back=False, size=(46, 46))
                surf.blit(sprite, (cx + 4, cy + 6))

                # Name & Level
                name_txt = gfx.fonts["regular"].render(f"{p.nickname or p.species}", True, (200, 80, 0) if is_sel else UI_TEXT)
                lvl_txt = gfx.fonts["small"].render(f"Lv.{p.level}", True, UI_TEXT_MUTED)
                surf.blit(name_txt, (cx + 54, cy + 5))
                surf.blit(lvl_txt, (cx + 54 + name_txt.get_width() + 6, cy + 7))

                # HP Bar
                hp_w = 90
                hp_pct = max(0.0, min(1.0, p.current_hp / p.max_hp))
                hp_col = HP_GREEN if hp_pct > 0.5 else (HP_YELLOW if hp_pct > 0.2 else HP_RED)
                pygame.draw.rect(surf, (200, 205, 215), (cx + 54, cy + 24, hp_w, 6), border_radius=3)
                pygame.draw.rect(surf, hp_col, (cx + 54, cy + 24, int(hp_w * hp_pct), 6), border_radius=3)

                hp_lbl = gfx.fonts["small"].render(f"{p.current_hp}/{p.max_hp}", True, UI_TEXT_MUTED)
                surf.blit(hp_lbl, (cx + 54 + hp_w + 6, cy + 20))

                # Types & Status
                p_types = POKEMON_SPECIES.get(p.species, {}).get("types", ["Normal"])
                for t_idx, t_name in enumerate(p_types):
                    gfx.draw_type_badge(surf, t_name, cx + cw - 70 + t_idx * 34, cy + 5, width=32, height=16)
                if p.is_fainted():
                    gfx.draw_status_badge(surf, "Fainted", cx + cw - 44, cy + 23, width=36, height=16)
                elif p.status:
                    gfx.draw_status_badge(surf, p.status, cx + cw - 44, cy + 23, width=36, height=16)

                # Evolution Level Milestone Badge Pill
                evo_info = get_pokemon_evolution_info(p, self.inventory)
                if evo_info["method"] == "LEVEL":
                    if evo_info["is_ready"]:
                        pill_bg = (225, 248, 230)
                        pill_bdr = (50, 180, 80)
                        pill_col = (20, 130, 45)
                    else:
                        pill_bg = (235, 245, 255)
                        pill_bdr = (140, 180, 240)
                        pill_col = (20, 90, 190)
                elif evo_info["method"] == "STONE":
                    pill_bg = (255, 240, 250)
                    pill_bdr = (210, 140, 190)
                    pill_col = (150, 40, 140)
                else:
                    pill_bg = (248, 246, 238)
                    pill_bdr = (210, 195, 150)
                    pill_col = (130, 110, 50)

                evo_txt = gfx.fonts["small"].render(evo_info["short_text"], True, pill_col)
                pill_w = min(cw - 64, evo_txt.get_width() + 10)
                pygame.draw.rect(surf, pill_bg, (cx + 54, cy + 39, pill_w, 17), border_radius=4)
                pygame.draw.rect(surf, pill_bdr, (cx + 54, cy + 39, pill_w, 17), 1, border_radius=4)
                surf.blit(evo_txt, (cx + 59, cy + 40))

            else:
                # Empty Party Slot
                pygame.draw.rect(surf, (230, 235, 245), (cx, cy, cw, ch), border_radius=8)
                empty_lbl = gfx.fonts["small"].render("- Empty Slot -", True, (160, 170, 185))
                surf.blit(empty_lbl, (cx + (cw - empty_lbl.get_width()) // 2, cy + 22))

        # 2. Right Column: PC Storage Box
        rx, ry, rw, rh = 415, 82, 350, 468
        is_pc_active = (self.active_panel == "PC")
        bdr_color_pc = (240, 140, 40) if is_pc_active else UI_BORDER_LIGHT
        pygame.draw.rect(surf, bdr_color_pc, (rx - 2, ry - 2, rw + 4, rh + 4), border_radius=12)
        pygame.draw.rect(surf, WHITE, (rx, ry, rw, rh), border_radius=10)

        pc_header = gfx.fonts["large"].render(f"PC STORAGE BOX ({len(self.pc_box)})", True, (20, 80, 180) if is_pc_active else UI_TEXT)
        surf.blit(pc_header, (rx + 20, ry + 12))

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
                cy = ry + 46 + idx * 68
                cw, ch = rw - 30, 62
                cx = rx + 15

                if actual_idx < len(self.pc_box):
                    p = self.pc_box[actual_idx]
                    is_sel = (is_pc_active and actual_idx == self.pc_idx)
                    is_being_moved = (self.moving_source == ("PC", actual_idx))
                    if is_being_moved:
                        card_bdr = (255, 140, 0)
                        card_bg = (255, 230, 180)
                    else:
                        card_bdr = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
                        card_bg = (255, 248, 230) if is_sel else (250, 252, 255)

                    pygame.draw.rect(surf, card_bdr, (cx, cy, cw, ch), border_radius=8)
                    pygame.draw.rect(surf, card_bg, (cx + 1, cy + 1, cw - 2, ch - 2), border_radius=7)

                    if is_being_moved:
                        m_tag = gfx.fonts["small"].render("HOLDING", True, (210, 60, 0))
                        surf.blit(m_tag, (cx + cw - 70 - m_tag.get_width() - 8, cy + 6))

                    # Mini Sprite
                    sprite = gfx.get_pokemon_sprite(p.species, is_back=False, size=(46, 46))
                    surf.blit(sprite, (cx + 4, cy + 6))

                    # Name & Level
                    name_txt = gfx.fonts["regular"].render(f"{p.nickname or p.species}", True, (200, 80, 0) if is_sel else UI_TEXT)
                    lvl_txt = gfx.fonts["small"].render(f"Lv.{p.level}", True, UI_TEXT_MUTED)
                    surf.blit(name_txt, (cx + 54, cy + 5))
                    surf.blit(lvl_txt, (cx + 54 + name_txt.get_width() + 6, cy + 7))

                    # HP Bar
                    hp_w = 90
                    hp_pct = max(0.0, min(1.0, p.current_hp / p.max_hp))
                    hp_col = HP_GREEN if hp_pct > 0.5 else (HP_YELLOW if hp_pct > 0.2 else HP_RED)
                    pygame.draw.rect(surf, (200, 205, 215), (cx + 54, cy + 24, hp_w, 6), border_radius=3)
                    pygame.draw.rect(surf, hp_col, (cx + 54, cy + 24, int(hp_w * hp_pct), 6), border_radius=3)

                    hp_lbl = gfx.fonts["small"].render(f"{p.current_hp}/{p.max_hp}", True, UI_TEXT_MUTED)
                    surf.blit(hp_lbl, (cx + 54 + hp_w + 6, cy + 20))

                    # Types & Status
                    p_types = POKEMON_SPECIES.get(p.species, {}).get("types", ["Normal"])
                    for t_idx, t_name in enumerate(p_types):
                        gfx.draw_type_badge(surf, t_name, cx + cw - 70 + t_idx * 34, cy + 5, width=32, height=16)
                    if p.is_fainted():
                        gfx.draw_status_badge(surf, "Fainted", cx + cw - 44, cy + 23, width=36, height=16)
                    elif p.status:
                        gfx.draw_status_badge(surf, p.status, cx + cw - 44, cy + 23, width=36, height=16)

                    # Evolution Level Milestone Badge Pill
                    evo_info = get_pokemon_evolution_info(p, self.inventory)
                    if evo_info["method"] == "LEVEL":
                        if evo_info["is_ready"]:
                            pill_bg = (225, 248, 230)
                            pill_bdr = (50, 180, 80)
                            pill_col = (20, 130, 45)
                        else:
                            pill_bg = (235, 245, 255)
                            pill_bdr = (140, 180, 240)
                            pill_col = (20, 90, 190)
                    elif evo_info["method"] == "STONE":
                        pill_bg = (255, 240, 250)
                        pill_bdr = (210, 140, 190)
                        pill_col = (150, 40, 140)
                    else:
                        pill_bg = (248, 246, 238)
                        pill_bdr = (210, 195, 150)
                        pill_col = (130, 110, 50)

                    evo_txt = gfx.fonts["small"].render(evo_info["short_text"], True, pill_col)
                    pill_w = min(cw - 64, evo_txt.get_width() + 10)
                    pygame.draw.rect(surf, pill_bg, (cx + 54, cy + 39, pill_w, 17), border_radius=4)
                    pygame.draw.rect(surf, pill_bdr, (cx + 54, cy + 39, pill_w, 17), 1, border_radius=4)
                    surf.blit(evo_txt, (cx + 59, cy + 40))

            # Scroll indicator
            if len(self.pc_box) > 6:
                scroll_info = gfx.fonts["small"].render(f"▲ ▼ ({self.pc_idx + 1}/{len(self.pc_box)})", True, (200, 80, 0))
                surf.blit(scroll_info, (rx + rw - scroll_info.get_width() - 20, ry + 14))

        # 3. Action Modal Popup Overlay
        if self.menu_mode == "ACTIONS":
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 110))
            surf.blit(overlay, (0, 0))

            actions = self._get_available_actions()
            mw, mh = 330, 48 + len(actions) * 44
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
            overlay.fill((0, 0, 0, 140))
            surf.blit(overlay, (0, 0))

            p = self.summary_pokemon
            sw, sh = 720, 510
            sx = (SCREEN_WIDTH - sw) // 2
            sy = (SCREEN_HEIGHT - sh) // 2

            # Main Card Box
            pygame.draw.rect(surf, (30, 45, 80), (sx - 3, sy - 3, sw + 6, sh + 6), border_radius=16)
            pygame.draw.rect(surf, (248, 250, 255), (sx, sy, sw, sh), border_radius=14)

            # 1. Header Banner
            pygame.draw.rect(surf, (230, 238, 252), (sx, sy, sw, 52), border_top_left_radius=14, border_top_right_radius=14)
            pygame.draw.line(surf, (190, 210, 240), (sx, sy + 52), (sx + sw, sy + 52), 2)

            p_id = getattr(p, "pokedex_id", POKEMON_SPECIES.get(p.species, {}).get("id", 1))
            shead = gfx.fonts["title"].render(f"{p.nickname or p.species}", True, (20, 70, 160))
            lvl_pill = gfx.fonts["medium"].render(f"Lv. {p.level}", True, (220, 80, 0))
            id_txt = gfx.fonts["regular"].render(f"No. {p_id:03d}", True, UI_TEXT_MUTED)

            surf.blit(shead, (sx + 20, sy + 12))
            surf.blit(lvl_pill, (sx + 30 + shead.get_width(), sy + 16))
            surf.blit(id_txt, (sx + 45 + shead.get_width() + lvl_pill.get_width(), sy + 18))

            close_tag = gfx.fonts["small"].render("[ESC / Z / X] Close", True, (120, 140, 170))
            surf.blit(close_tag, (sx + sw - close_tag.get_width() - 20, sy + 18))

            # 2. Upper Left: Sprite & Types
            sp_w, sp_h = 160, 195
            pygame.draw.rect(surf, (242, 246, 254), (sx + 16, sy + 64, sp_w, sp_h), border_radius=10)
            pygame.draw.rect(surf, (215, 225, 242), (sx + 16, sy + 64, sp_w, sp_h), 1, border_radius=10)

            sp_surf = gfx.get_pokemon_sprite(p.species, is_back=False, size=(110, 110))
            surf.blit(sp_surf, (sx + 16 + (sp_w - 110) // 2, sy + 70))

            p_types = POKEMON_SPECIES.get(p.species, {}).get("types", ["Normal"])
            total_type_w = len(p_types) * 60 + (len(p_types) - 1) * 6
            start_tx = sx + 16 + (sp_w - total_type_w) // 2
            for t_idx, t_name in enumerate(p_types):
                gfx.draw_type_badge(surf, t_name, start_tx + t_idx * 66, sy + 186, width=60, height=22)

            if p.is_fainted():
                gfx.draw_status_badge(surf, "Fainted", sx + 16 + (sp_w - 54) // 2, sy + 218, width=54, height=20)
            elif p.status:
                gfx.draw_status_badge(surf, p.status, sx + 16 + (sp_w - 54) // 2, sy + 218, width=54, height=20)

            # 3. Upper Middle: Stats Table & EXP Progress
            stat_w, stat_h = 240, 195
            stat_x = sx + 188
            pygame.draw.rect(surf, WHITE, (stat_x, sy + 64, stat_w, stat_h), border_radius=10)
            pygame.draw.rect(surf, (215, 225, 242), (stat_x, sy + 64, stat_w, stat_h), 1, border_radius=10)

            stat_head = gfx.fonts["small"].render("COMBAT ATTRIBUTES", True, (40, 80, 160))
            surf.blit(stat_head, (stat_x + 12, sy + 72))

            stats_rows = [
                ("HP", f"{p.current_hp} / {p.max_hp}", (230, 70, 70)),
                ("Attack", str(p.stats.get("atk", 10)), (240, 130, 30)),
                ("Defense", str(p.stats.get("def", 10)), (230, 190, 40)),
                ("Sp. Atk", str(p.stats.get("spatk", 10)), (60, 140, 240)),
                ("Sp. Def", str(p.stats.get("spdef", 10)), (70, 190, 90)),
                ("Speed", str(p.stats.get("spd", 10)), (230, 90, 180)),
            ]

            for s_i, (s_lbl, s_val, s_col) in enumerate(stats_rows):
                s_row_y = sy + 94 + s_i * 22
                pygame.draw.rect(surf, s_col, (stat_x + 12, s_row_y, 50, 18), border_radius=3)
                l_txt = gfx.fonts["small"].render(s_lbl, True, WHITE)
                surf.blit(l_txt, (stat_x + 12 + (50 - l_txt.get_width()) // 2, s_row_y + 2))

                v_txt = gfx.fonts["small"].render(s_val, True, UI_TEXT)
                surf.blit(v_txt, (stat_x + stat_w - v_txt.get_width() - 14, s_row_y + 2))

            # EXP Bar inside stats card
            exp_y = sy + 232
            exp_progress = p.exp_progress_ratio() if hasattr(p, "exp_progress_ratio") else 0.5
            gfx.draw_exp_bar(surf, stat_x + 12, exp_y, stat_w - 24, 6, exp_progress)
            exp_txt = gfx.fonts["small"].render(f"EXP: {p.exp} / {p.exp_for_next_level()}", True, UI_TEXT_MUTED)
            surf.blit(exp_txt, (stat_x + (stat_w - exp_txt.get_width()) // 2, exp_y + 8))

            # 4. Upper Right: Evolution Milestone Card
            evo_w, evo_h = 260, 195
            evo_x = sx + 440
            pygame.draw.rect(surf, (244, 248, 255), (evo_x, sy + 64, evo_w, evo_h), border_radius=10)
            pygame.draw.rect(surf, (200, 215, 240), (evo_x, sy + 64, evo_w, evo_h), 1, border_radius=10)

            e_head = gfx.fonts["small"].render("EVOLUTION MILESTONE", True, (20, 70, 160))
            surf.blit(e_head, (evo_x + 14, sy + 72))

            evo_info = get_pokemon_evolution_info(p, self.inventory)
            
            # Evolution Short Text (Word Wrapped)
            evo_text_str = evo_info.get("short_text", "Fully evolved form.")
            e_words = evo_text_str.split(" ")
            e_lines, cur_line = [], ""
            for w in e_words:
                test = cur_line + (" " if cur_line else "") + w
                if gfx.fonts["regular"].size(test)[0] < evo_w - 28:
                    cur_line = test
                else:
                    e_lines.append(cur_line)
                    cur_line = w
            if cur_line:
                e_lines.append(cur_line)

            for l_i, l_str in enumerate(e_lines[:3]):
                e_col = (210, 70, 0) if evo_info.get("is_ready") else UI_TEXT
                l_surf = gfx.fonts["regular"].render(l_str, True, e_col)
                surf.blit(l_surf, (evo_x + 14, sy + 98 + l_i * 24))

            # Target species preview tag if available
            target_species = evo_info.get("target")
            if target_species:
                t_sp_icon = gfx.get_pokemon_sprite(target_species, is_back=False, size=(38, 38))
                surf.blit(t_sp_icon, (evo_x + 14, sy + 155))
                t_lbl = gfx.fonts["small"].render(f"Target: {target_species}", True, (40, 90, 180))
                surf.blit(t_lbl, (evo_x + 58, sy + 165))

            # Interactive Chart Button
            btn_chart_y = sy + 215
            pygame.draw.rect(surf, (220, 235, 255), (evo_x + 10, btn_chart_y, evo_w - 20, 30), border_radius=6)
            pygame.draw.rect(surf, (100, 160, 240), (evo_x + 10, btn_chart_y, evo_w - 20, 30), 1, border_radius=6)
            e_hint = gfx.fonts["small"].render("[E / Tab]: Full Evolution Chart", True, (20, 80, 190))
            surf.blit(e_hint, (evo_x + (evo_w - e_hint.get_width()) // 2, btn_chart_y + 7))

            # 5. Lower Section: Known Moves (4 Slots)
            moves_box_y = sy + 270
            moves_w, moves_h = sw - 32, 190
            pygame.draw.rect(surf, WHITE, (sx + 16, moves_box_y, moves_w, moves_h), border_radius=10)
            pygame.draw.rect(surf, (215, 225, 242), (sx + 16, moves_box_y, moves_w, moves_h), 1, border_radius=10)

            m_title = gfx.fonts["small"].render("KNOWN MOVES & TECHNIQUES", True, (40, 100, 200))
            surf.blit(m_title, (sx + 28, moves_box_y + 10))

            card_move_w = (moves_w - 36) // 2
            card_move_h = 62

            for m_i in range(4):
                col_i = m_i % 2
                row_i = m_i // 2
                mx_pos = sx + 24 + col_i * (card_move_w + 12)
                my_pos = moves_box_y + 34 + row_i * (card_move_h + 8)

                if m_i < len(p.moves):
                    m = p.moves[m_i]
                    m_name_str = m["name"] if isinstance(m, dict) else getattr(m, "name", "Tackle")
                    m_pp_val = m.get("pp", 35) if isinstance(m, dict) else getattr(m, "pp", 35)
                    m_max_pp = m.get("max_pp", 35) if isinstance(m, dict) else getattr(m, "max_pp", 35)
                    m_type = m.get("type", "Normal") if isinstance(m, dict) else getattr(m, "type", "Normal")
                    m_cat = m.get("category", "Physical") if isinstance(m, dict) else getattr(m, "category", "Physical")
                    m_pwr = m.get("power", 0) if isinstance(m, dict) else getattr(m, "power", 0)

                    # Move Card Background
                    pygame.draw.rect(surf, (250, 252, 255), (mx_pos, my_pos, card_move_w, card_move_h), border_radius=8)
                    pygame.draw.rect(surf, (220, 230, 245), (mx_pos, my_pos, card_move_w, card_move_h), 1, border_radius=8)

                    # Slot index tag
                    pygame.draw.rect(surf, (40, 100, 180), (mx_pos + 8, my_pos + 8, 22, 22), border_radius=4)
                    idx_txt = gfx.fonts["small"].render(str(m_i + 1), True, WHITE)
                    surf.blit(idx_txt, (mx_pos + 8 + (22 - idx_txt.get_width()) // 2, my_pos + 11))

                    # Move Name
                    m_name_surf = gfx.fonts["regular"].render(m_name_str, True, UI_TEXT)
                    surf.blit(m_name_surf, (mx_pos + 36, my_pos + 8))

                    # Type Badge & Category
                    gfx.draw_type_badge(surf, m_type, mx_pos + 36, my_pos + 34, width=54, height=18)
                    cat_txt = gfx.fonts["small"].render(m_cat.upper(), True, UI_TEXT_MUTED)
                    surf.blit(cat_txt, (mx_pos + 96, my_pos + 36))

                    # Power & PP on the right
                    pwr_str = f"Pwr: {m_pwr}" if m_pwr > 0 else "Pwr: --"
                    pwr_txt = gfx.fonts["small"].render(pwr_str, True, UI_TEXT_MUTED)
                    pp_str = f"PP: {m_pp_val}/{m_max_pp}"
                    pp_txt = gfx.fonts["regular"].render(pp_str, True, (40, 120, 220) if m_pp_val > 0 else (220, 40, 40))

                    surf.blit(pwr_txt, (mx_pos + card_move_w - pwr_txt.get_width() - 14, my_pos + 8))
                    surf.blit(pp_txt, (mx_pos + card_move_w - pp_txt.get_width() - 14, my_pos + 32))
                else:
                    # Empty Move Slot
                    pygame.draw.rect(surf, (246, 248, 252), (mx_pos, my_pos, card_move_w, card_move_h), border_radius=8)
                    pygame.draw.rect(surf, (230, 235, 245), (mx_pos, my_pos, card_move_w, card_move_h), 1, border_radius=8)
                    emp_txt = gfx.fonts["small"].render("- Empty Move Slot -", True, (160, 175, 195))
                    surf.blit(emp_txt, (mx_pos + (card_move_w - emp_txt.get_width()) // 2, my_pos + 22))

            # 6. Bottom Navigation Hint
            close_hint = gfx.fonts["small"].render("Press [Z / X / Enter / ESC] to Close  |  [E / Tab]: Evolution Progression Chart", True, (180, 70, 0))
            surf.blit(close_hint, (sx + (sw - close_hint.get_width()) // 2, sy + sh - 28))

        # 5. Evolution Progression Chart Modal Popup Overlay
        if self.menu_mode == "EVOLUTION_CHART" and self.evolution_pokemon:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            surf.blit(overlay, (0, 0))

            p = self.evolution_pokemon
            mw, mh = 700, 480
            mx = (SCREEN_WIDTH - mw) // 2
            my = (SCREEN_HEIGHT - mh) // 2

            pygame.draw.rect(surf, (30, 45, 80), (mx - 3, my - 3, mw + 6, mh + 6), border_radius=16)
            pygame.draw.rect(surf, (246, 249, 255), (mx, my, mw, mh), border_radius=14)

            # Header Banner
            pygame.draw.rect(surf, (230, 238, 252), (mx, my, mw, 52), border_top_left_radius=14, border_top_right_radius=14)
            pygame.draw.line(surf, (190, 210, 240), (mx, my + 52), (mx + mw, my + 52), 2)

            chart_title = gfx.fonts["title"].render("POKÉMON EVOLUTION PROGRESSION", True, (20, 70, 160))
            surf.blit(chart_title, (mx + 20, my + 14))

            # Close tag in header
            close_tag = gfx.fonts["small"].render("[ESC / Z / X] Close", True, (120, 140, 170))
            surf.blit(close_tag, (mx + mw - close_tag.get_width() - 20, my + 18))

            root_sp, chain = get_full_evolution_tree(p.species)
            evo_info = get_pokemon_evolution_info(p, self.inventory)

            # Section 1: Horizontal Evolution Stage Flow
            num_stages = max(1, len(chain))
            card_w = min(180, (mw - 60 - (num_stages - 1) * 60) // num_stages)
            card_h = 125
            total_stages_w = num_stages * card_w + (num_stages - 1) * 60
            start_sx = mx + (mw - total_stages_w) // 2

            curr_stage_idx = 0
            for s_idx, node in enumerate(chain):
                if node["species"] == p.species:
                    curr_stage_idx = s_idx

            for s_idx, node in enumerate(chain):
                cx = start_sx + s_idx * (card_w + 60)
                cy = my + 64
                sp_name = node["species"]
                is_curr = (sp_name == p.species)
                is_past = (s_idx < curr_stage_idx)

                # Card background and border styling
                if is_curr:
                    card_bg = (255, 248, 225)
                    card_bdr = (240, 150, 20)
                    tag_bg = (240, 150, 20)
                    tag_txt = f"★ CURRENT (Lv.{p.level})"
                    tag_col = WHITE
                elif is_past:
                    card_bg = (245, 252, 245)
                    card_bdr = (120, 190, 130)
                    tag_bg = (100, 180, 110)
                    tag_txt = "✓ PREVIOUS FORM"
                    tag_col = WHITE
                else: # is_future
                    card_bg = (250, 252, 255)
                    card_bdr = (100, 160, 240)
                    tag_bg = (60, 130, 230)
                    tag_txt = "▲ NEXT FORM" if s_idx == curr_stage_idx + 1 else "▲ FINAL FORM"
                    tag_col = WHITE

                pygame.draw.rect(surf, card_bdr, (cx - 2, cy - 2, card_w + 4, card_h + 4), border_radius=10)
                pygame.draw.rect(surf, card_bg, (cx, cy, card_w, card_h), border_radius=8)

                # Top Stage Header Tag
                tag_surf = gfx.fonts["small"].render(tag_txt, True, tag_col)
                tw, th = tag_surf.get_width() + 10, 18
                tx = cx + (card_w - tw) // 2
                pygame.draw.rect(surf, tag_bg, (tx, cy + 6, tw, th), border_radius=4)
                surf.blit(tag_surf, (tx + 5, cy + 7))

                # Sprite
                sp_img = gfx.get_pokemon_sprite(sp_name, is_back=False, size=(48, 48))
                surf.blit(sp_img, (cx + (card_w - 48) // 2, cy + 28))

                # Species Name
                sname_txt = gfx.fonts["regular"].render(sp_name, True, UI_TEXT)
                surf.blit(sname_txt, (cx + (card_w - sname_txt.get_width()) // 2, cy + 78))

                # Types Badges
                stypes = node["types"]
                for t_i, t_name in enumerate(stypes):
                    gfx.draw_type_badge(surf, t_name, cx + (card_w - len(stypes) * 36) // 2 + t_i * 36, cy + 100, width=32, height=16)

                # Connecting Flow Arrow to Next Stage
                if s_idx < num_stages - 1:
                    ax = cx + card_w + 6
                    ay = cy + 40
                    arrow_w = 48
                    arrow_sym = gfx.fonts["large"].render("➔", True, (120, 150, 200))
                    surf.blit(arrow_sym, (ax + (arrow_w - arrow_sym.get_width()) // 2, ay - 8))

                    req_lvl_info = node.get("level_evo")
                    if req_lvl_info:
                        lvl_req = req_lvl_info.get("level", 100)
                        lbl1 = gfx.fonts["small"].render(f"Lv.{lvl_req}", True, (20, 70, 160))
                        surf.blit(lbl1, (ax + (arrow_w - lbl1.get_width()) // 2, ay + 18))
                        if is_curr:
                            if p.level >= lvl_req:
                                lbl2 = gfx.fonts["small"].render("READY!", True, (40, 180, 70))
                            else:
                                diff = lvl_req - p.level
                                lbl2 = gfx.fonts["small"].render(f"-{diff} lvls", True, (200, 80, 0))
                            surf.blit(lbl2, (ax + (arrow_w - lbl2.get_width()) // 2, ay + 32))
                    elif node.get("stone_evos"):
                        stn_name = node["stone_evos"][0]["stone"].replace(" Stone", "")
                        lbl1 = gfx.fonts["small"].render(f"{stn_name}", True, (160, 60, 180))
                        surf.blit(lbl1, (ax + (arrow_w - lbl1.get_width()) // 2, ay + 18))

            # Section 2: Live Level Progression Gauge
            gy = my + 200
            gw, gh = mw - 40, 120
            gx = mx + 20
            pygame.draw.rect(surf, (220, 230, 245), (gx - 1, gy - 1, gw + 2, gh + 2), border_radius=10)
            pygame.draw.rect(surf, WHITE, (gx, gy, gw, gh), border_radius=9)

            if evo_info["method"] == "LEVEL":
                req_lvl = evo_info["req_level"]
                target_name = evo_info["target_species"]
                lvls_left = evo_info["levels_left"]
                is_ready = evo_info["is_ready"]

                # Title
                g_title = gfx.fonts["regular"].render(f"LEVEL PROGRESSION TO {target_name.upper()}", True, (20, 70, 160))
                surf.blit(g_title, (gx + 16, gy + 12))

                # Large Progress Bar
                bar_x = gx + 16
                bar_y = gy + 38
                bar_w = gw - 32
                bar_h = 22

                pct = 1.0 if is_ready else max(0.05, min(0.99, p.level / max(1, req_lvl)))
                pygame.draw.rect(surf, (225, 232, 244), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
                bar_col = (50, 205, 90) if is_ready else (40, 130, 240)
                pygame.draw.rect(surf, bar_col, (bar_x, bar_y, int(bar_w * pct), bar_h), border_radius=6)
                pygame.draw.rect(surf, (180, 195, 215), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=6)

                # Progress text inside bar
                if is_ready:
                    p_txt = gfx.fonts["small"].render(f"Level {p.level} / Required Level {req_lvl}  (100% - Ready to Evolve!)", True, WHITE)
                else:
                    p_txt = gfx.fonts["small"].render(f"Level {p.level} / Required Level {req_lvl}  ({int(pct * 100)}% - {lvls_left} Level{'s' if lvls_left != 1 else ''} to go!)", True, (20, 40, 80) if pct < 0.6 else WHITE)
                surf.blit(p_txt, (bar_x + (bar_w - p_txt.get_width()) // 2, bar_y + 3))

                # Status info message
                if is_ready:
                    msg_txt = gfx.fonts["regular"].render(f"★ {p.nickname or p.species} is ready to evolve into {target_name}! (Gain 1 level in battle or use a Rare Candy)", True, (30, 150, 60))
                else:
                    msg_txt = gfx.fonts["regular"].render(f"Gain {lvls_left} more level{'s' if lvls_left != 1 else ''} to evolve {p.nickname or p.species} into {target_name} at Level {req_lvl}.", True, (40, 80, 150))
                surf.blit(msg_txt, (gx + 16, gy + 68))

                # Stone alternative note or EXP note
                if evo_info.get("stone_targets"):
                    stone_list_str = ", ".join([f"{st[0]} (-> {st[1]})" for st in evo_info["stone_targets"]])
                    stn_note = gfx.fonts["small"].render(f"Optional Alternative: Evolves immediately with {stone_list_str}", True, (140, 60, 170))
                    surf.blit(stn_note, (gx + 16, gy + 94))
                else:
                    exp_note = gfx.fonts["small"].render(f"Current EXP: {p.exp}  |  Next Level at: {p.exp_for_next_level()} EXP ({p.exp_for_next_level() - p.exp} EXP needed)", True, UI_TEXT_MUTED)
                    surf.blit(exp_note, (gx + 16, gy + 94))

            elif evo_info["method"] == "STONE":
                st_targets = evo_info["stone_targets"]
                g_title = gfx.fonts["regular"].render("EVOLUTIONARY STONE REQUIREMENTS", True, (150, 50, 170))
                surf.blit(g_title, (gx + 16, gy + 12))

                for st_idx, (stone_name, target_name) in enumerate(st_targets[:3]):
                    sy_pos = gy + 38 + st_idx * 26
                    stone_cnt = self.inventory.get_count(stone_name) if self.inventory else 0
                    cnt_col = (40, 160, 60) if stone_cnt > 0 else (200, 80, 80)
                    cnt_str = f"[In Bag: {stone_cnt}x - Ready!]" if stone_cnt > 0 else "[In Bag: 0x - Need Item]"

                    line_txt = gfx.fonts["regular"].render(f"💎 {stone_name}  ➔  {target_name}", True, UI_TEXT)
                    cnt_txt = gfx.fonts["small"].render(cnt_str, True, cnt_col)
                    surf.blit(line_txt, (gx + 16, sy_pos))
                    surf.blit(cnt_txt, (gx + 340, sy_pos + 2))

                if len(st_targets) <= 2:
                    hint_stn = gfx.fonts["small"].render("Evolution stones can be purchased at Celadon Department Store or found across Kanto.", True, UI_TEXT_MUTED)
                    surf.blit(hint_stn, (gx + 16, gy + 94))

            else: # Final form / No evolution
                g_title = gfx.fonts["large"].render("👑 MAXIMUM EVOLUTION STAGE ACHIEVED", True, (200, 130, 20))
                surf.blit(g_title, (gx + 16, gy + 16))

                f_desc1 = gfx.fonts["regular"].render(f"{p.nickname or p.species} has reached its ultimate evolutionary form and cannot evolve further.", True, UI_TEXT)
                f_desc2 = gfx.fonts["small"].render("All combat base stats are at peak evolutionary potential. Level up to 100 to maximize battle power!", True, UI_TEXT_MUTED)
                surf.blit(f_desc1, (gx + 16, gy + 48))
                surf.blit(f_desc2, (gx + 16, gy + 74))

            # Section 3: Stat Potential & Combat Analysis
            sy = my + 330
            sw_card, sh_card = mw - 40, 95
            sx_card = mx + 20
            pygame.draw.rect(surf, (235, 242, 255), (sx_card - 1, sy - 1, sw_card + 2, sh_card + 2), border_radius=10)
            pygame.draw.rect(surf, (248, 250, 255), (sx_card, sy, sw_card, sh_card), border_radius=9)

            if evo_info["method"] in ["LEVEL", "STONE"] and evo_info["target_species"]:
                target_name = evo_info["target_species"]
                tgt_data = POKEMON_SPECIES.get(target_name, {})
                curr_data = POKEMON_SPECIES.get(p.species, {})

                stat_head = gfx.fonts["small"].render(f"BASE STAT BOOST PREVIEW UPON EVOLVING INTO {target_name.upper()}", True, (20, 70, 160))
                surf.blit(stat_head, (sx_card + 16, sy + 10))

                c_bst = curr_data.get("base_stats", {})
                t_bst = tgt_data.get("base_stats", {})
                stat_keys = [("HP", "hp"), ("Atk", "atk"), ("Def", "def"), ("Sp.Atk", "spatk"), ("Sp.Def", "spdef"), ("Spd", "spd")]

                for s_i, (s_label, s_k) in enumerate(stat_keys):
                    bx_pos = sx_card + 16 + s_i * 105
                    by_pos = sy + 32
                    c_val = c_bst.get(s_k, 0)
                    t_val = t_bst.get(s_k, 0)
                    diff = t_val - c_val
                    lbl = gfx.fonts["small"].render(s_label, True, UI_TEXT_MUTED)
                    val_txt = gfx.fonts["regular"].render(f"{c_val} ➔ {t_val}", True, UI_TEXT)
                    diff_txt = gfx.fonts["small"].render(f"(+{diff})", True, (40, 170, 60) if diff > 0 else UI_TEXT_MUTED)
                    surf.blit(lbl, (bx_pos, by_pos))
                    surf.blit(val_txt, (bx_pos, by_pos + 16))
                    surf.blit(diff_txt, (bx_pos, by_pos + 36))

            else:
                stat_head = gfx.fonts["small"].render("CURRENT COMBAT BASE STATS", True, (20, 70, 160))
                surf.blit(stat_head, (sx_card + 16, sy + 10))

                curr_data = POKEMON_SPECIES.get(p.species, {})
                c_bst = curr_data.get("base_stats", {})
                stat_keys = [("HP", "hp"), ("Attack", "atk"), ("Defense", "def"), ("Sp. Atk", "spatk"), ("Sp. Def", "spdef"), ("Speed", "spd")]
                for s_i, (s_label, s_k) in enumerate(stat_keys):
                    bx_pos = sx_card + 16 + s_i * 105
                    by_pos = sy + 32
                    c_val = c_bst.get(s_k, 0)
                    lbl = gfx.fonts["small"].render(s_label, True, UI_TEXT_MUTED)
                    val_txt = gfx.fonts["large"].render(f"{c_val}", True, (20, 70, 160))
                    surf.blit(lbl, (bx_pos, by_pos))
                    surf.blit(val_txt, (bx_pos, by_pos + 18))

            # Footer navigation bar inside modal
            f_hint = gfx.fonts["small"].render("Left/Right: Switch Panel  |  Up/Down: Select Pokémon  |  [Z / X / Enter / ESC / E]: Back to Storage Box", True, UI_TEXT_MUTED)
            surf.blit(f_hint, (mx + (mw - f_hint.get_width()) // 2, my + mh - 26))

        # 6. On-screen Toast Notification
        if self.notification_timer > 0:
            nw = gfx.fonts["regular"].size(self.notification)[0] + 36
            nx = (SCREEN_WIDTH - nw) // 2
            ny = 20
            pygame.draw.rect(surf, (30, 36, 50), (nx - 2, ny - 2, nw + 4, 36), border_radius=8)
            pygame.draw.rect(surf, (255, 235, 180), (nx, ny, nw, 32), border_radius=6)
            ntxt = gfx.fonts["regular"].render(self.notification, True, (180, 60, 0))
            surf.blit(ntxt, (nx + 18, ny + 5))

        # 7. Bottom Navigation Hint Bar
        if self.moving_source is not None:
            hint = gfx.fonts["small"].render("MOVING POKÉMON: Select target slot with Arrows  |  [Z / Enter]: Place / Swap  |  [X]: Cancel", True, (210, 80, 0))
        else:
            hint = gfx.fonts["small"].render("Arrows: Navigate  |  [M]: Move/Reorder  |  [Enter]: Options (Set Starter)  |  [E/Tab]: Evo Chart  |  [X]: Exit", True, UI_TEXT_MUTED)
        surf.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 565))

# Re-export TrainerCardScreen and QuestLogScreen for 100% backward compatibility
from ui_trainer import TrainerCardScreen, QuestLogScreen
