"""
ui_screens.py - Fullscreen interfaces: Pokedex, Party Summary, Bag, and PC Box.
Modularly re-exports BagScreen and PCBoxScreen for 100% backward compatibility.
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
from pokemon_data import (
    POKEMON_SPECIES, ITEMS, MOVES, WILD_ENCOUNTERS, WILD_WATER_ENCOUNTERS, STONE_EVOLUTIONS,
    get_pokemon_evolution_info, get_full_evolution_tree
)

# Modular Screen Imports (Re-exported for backward compatibility)
from ui_bag import BagScreen
from ui_pc_box import PCBoxScreen
from ui_trainer import TrainerCardScreen, QuestLogScreen

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
    """
    Interactive Pokémon Party & Move Reordering Screen.
    Allows viewing party members, inspecting full stats, and switching/reordering move slots.
    """
    def __init__(self, party, inventory=None):
        self.party = party
        self.inventory = inventory
        self.selected_idx = 0
        self.mode = "PARTY_LIST" # "PARTY_LIST" or "SUMMARY_MOVES"
        self.selected_move_idx = 0
        self.move_swap_source = None # index of move picked up for swapping
        self.party_swap_source = None # index of pokemon picked up for party order swap
        self.notice_msg = ""
        self.notice_timer = 0.0
        self.anim_timer = 0.0

    def update(self, dt):
        self.anim_timer += dt
        if self.notice_timer > 0:
            self.notice_timer = max(0.0, self.notice_timer - dt)
            if self.notice_timer == 0:
                self.notice_msg = ""

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if not self.party:
            if any(event.key == k for k in KEY_CANCEL + KEY_CONFIRM):
                sound_mgr.play_sfx("cancel")
                return "BACK"
            return None

        # MODE 1: PARTY OVERVIEW LIST
        if self.mode == "PARTY_LIST":
            # Navigation in 2x3 grid
            if any(event.key == k for k in KEY_UP):
                if self.selected_idx >= 2:
                    self.selected_idx -= 2
                    sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                if self.selected_idx + 2 < len(self.party):
                    self.selected_idx += 2
                    sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_LEFT):
                if self.selected_idx % 2 == 1:
                    self.selected_idx -= 1
                    sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_RIGHT):
                if self.selected_idx % 2 == 0 and self.selected_idx + 1 < len(self.party):
                    self.selected_idx += 1
                    sound_mgr.play_sfx("select")
            elif event.key in [pygame.K_s, pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_TAB]:
                # Toggle Party Pokémon Swap Mode
                if self.party_swap_source is None:
                    self.party_swap_source = self.selected_idx
                    self.notice_msg = f"Switching {self.party[self.selected_idx].nickname}! Select new position..."
                    self.notice_timer = 3.0
                    sound_mgr.play_sfx("select")
                else:
                    if self.party_swap_source != self.selected_idx:
                        self.party[self.party_swap_source], self.party[self.selected_idx] = self.party[self.selected_idx], self.party[self.party_swap_source]
                        self.notice_msg = f"Swapped party positions!"
                        self.notice_timer = 2.5
                        sound_mgr.play_sfx("confirm")
                    self.party_swap_source = None
            elif any(event.key == k for k in KEY_CANCEL):
                if self.party_swap_source is not None:
                    self.party_swap_source = None
                    self.notice_msg = ""
                    sound_mgr.play_sfx("cancel")
                else:
                    sound_mgr.play_sfx("cancel")
                    return "BACK"
            elif event.key in [pygame.K_e, pygame.K_TAB]:
                sel_p = self.party[self.selected_idx]
                tgt = sel_p.check_evolution()
                if tgt:
                    old_name = sel_p.nickname
                    sel_p.evolve(tgt)
                    sound_mgr.play_sfx("level_up")
                    self.notice_msg = f"★ Congratulations! {old_name} evolved into {tgt.upper()}!"
                    self.notice_timer = 5.0
                    return None
            elif any(event.key == k for k in KEY_CONFIRM):
                if self.party_swap_source is not None:
                    if self.party_swap_source != self.selected_idx:
                        self.party[self.party_swap_source], self.party[self.selected_idx] = self.party[self.selected_idx], self.party[self.party_swap_source]
                        self.notice_msg = f"Swapped party positions!"
                        self.notice_timer = 2.5
                        sound_mgr.play_sfx("confirm")
                    self.party_swap_source = None
                else:
                    # Open full Summary & Moves View
                    self.mode = "SUMMARY_MOVES"
                    self.selected_move_idx = 0
                    self.move_swap_source = None
                    self.notice_msg = "Select a move with [Z / Enter] to swap its order!"
                    self.notice_timer = 3.0
                    sound_mgr.play_sfx("confirm")

        # MODE 2: POKÉMON SUMMARY & MOVE REORDERING
        elif self.mode == "SUMMARY_MOVES":
            curr_pkmn = self.party[self.selected_idx]
            num_moves = len(curr_pkmn.moves)

            if event.key in [pygame.K_e, pygame.K_TAB]:
                tgt = curr_pkmn.check_evolution()
                if tgt:
                    old_name = curr_pkmn.nickname
                    curr_pkmn.evolve(tgt)
                    sound_mgr.play_sfx("level_up")
                    self.notice_msg = f"★ Congratulations! {old_name} evolved into {tgt.upper()}!"
                    self.notice_timer = 5.0
                    return None

            # Move selection navigation (Up / Down)
            if any(event.key == k for k in KEY_UP):
                if num_moves > 0:
                    self.selected_move_idx = (self.selected_move_idx - 1) % num_moves
                    sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                if num_moves > 0:
                    self.selected_move_idx = (self.selected_move_idx + 1) % num_moves
                    sound_mgr.play_sfx("select")

            # Switch between Pokémon in party (Left / Right)
            elif any(event.key == k for k in KEY_LEFT):
                if self.move_swap_source is None and len(self.party) > 1:
                    self.selected_idx = (self.selected_idx - 1) % len(self.party)
                    self.selected_move_idx = min(self.selected_move_idx, len(self.party[self.selected_idx].moves) - 1)
                    sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_RIGHT):
                if self.move_swap_source is None and len(self.party) > 1:
                    self.selected_idx = (self.selected_idx + 1) % len(self.party)
                    self.selected_move_idx = min(self.selected_move_idx, len(self.party[self.selected_idx].moves) - 1)
                    sound_mgr.play_sfx("select")

            # Cancel / Back
            elif any(event.key == k for k in KEY_CANCEL):
                if self.move_swap_source is not None:
                    self.move_swap_source = None
                    self.notice_msg = "Move swap canceled."
                    self.notice_timer = 1.5
                    sound_mgr.play_sfx("cancel")
                else:
                    self.mode = "PARTY_LIST"
                    self.move_swap_source = None
                    self.notice_msg = ""
                    sound_mgr.play_sfx("cancel")

            # Confirm / Move Swap
            elif any(event.key == k for k in KEY_CONFIRM):
                if num_moves <= 1:
                    self.notice_msg = f"{curr_pkmn.nickname} only has 1 move!"
                    self.notice_timer = 2.0
                    sound_mgr.play_sfx("cancel")
                    return None

                if self.move_swap_source is None:
                    # Pick up source move
                    self.move_swap_source = self.selected_move_idx
                    m_name = curr_pkmn.moves[self.selected_move_idx]["name"]
                    self.notice_msg = f"Move [{m_name}] selected! Pick another move to swap with."
                    self.notice_timer = 4.0
                    sound_mgr.play_sfx("select")
                else:
                    # Swap with destination move
                    src_idx = self.move_swap_source
                    dst_idx = self.selected_move_idx
                    if src_idx != dst_idx:
                        m1 = curr_pkmn.moves[src_idx]["name"]
                        m2 = curr_pkmn.moves[dst_idx]["name"]
                        curr_pkmn.swap_moves(src_idx, dst_idx)
                        self.notice_msg = f"Swapped [{m1}] and [{m2}]!"
                        self.notice_timer = 3.0
                        sound_mgr.play_sfx("confirm")
                    self.move_swap_source = None

        return None

    def draw(self, surf):
        surf.fill((235, 240, 248))

        if self.mode == "PARTY_LIST":
            self._draw_party_list(surf)
        else:
            self._draw_summary_moves(surf)

    def _draw_party_list(self, surf):
        head = gfx.fonts["title"].render("POKÉMON TEAM", True, UI_TEXT)
        sub = gfx.fonts["regular"].render("Select a Pokémon for Summary & Move Switching", True, UI_TEXT_MUTED)
        surf.blit(head, (30, 16))
        surf.blit(sub, (30, 56))

        # Right-aligned quick hint
        hint_str = "[S / Shift]: Swap Party Order  |  [Z]: Summary & Moves  |  [X]: Exit"
        hint_surf = gfx.fonts["small"].render(hint_str, True, (40, 100, 180))
        surf.blit(hint_surf, (SCREEN_WIDTH - hint_surf.get_width() - 30, 24))

        # Notice message banner if active
        if self.notice_msg:
            n_box = pygame.Surface((SCREEN_WIDTH - 60, 26), pygame.SRCALPHA)
            n_box.fill((255, 240, 210, 230))
            surf.blit(n_box, (30, 60))
            pygame.draw.rect(surf, (240, 140, 40), (30, 60, SCREEN_WIDTH - 60, 26), 1, border_radius=4)
            n_txt = gfx.fonts["small"].render(self.notice_msg, True, (210, 70, 0))
            surf.blit(n_txt, (SCREEN_WIDTH // 2 - n_txt.get_width() // 2, 65))

        # Display 6 Party slots
        for i, p in enumerate(self.party):
            is_sel = (i == self.selected_idx)
            is_swap_src = (i == self.party_swap_source)
            row_x = 30 + (i % 2) * 380
            row_y = 92 + (i // 2) * 150
            rw, rh = 360, 138

            if is_swap_src:
                bdr_col = (230, 50, 50)
                bg_col = (255, 235, 235)
            elif is_sel:
                bdr_col = (240, 140, 40)
                bg_col = (255, 248, 230)
            else:
                bdr_col = UI_BORDER_LIGHT
                bg_col = WHITE

            pygame.draw.rect(surf, bdr_col, (row_x - 2, row_y - 2, rw + 4, rh + 4), border_radius=10)
            pygame.draw.rect(surf, bg_col, (row_x, row_y, rw, rh), border_radius=8)

            if is_sel or is_swap_src:
                bar_col = (230, 50, 50) if is_swap_src else (240, 120, 20)
                pygame.draw.rect(surf, bar_col, (row_x, row_y, 6, rh), border_top_left_radius=8, border_bottom_left_radius=8)

            # Sprite
            hop_y = -int(abs(math.sin(self.anim_timer * 4.0)) * 3) if is_sel else 0
            p_surf = gfx.get_pokemon_sprite(p.species, is_back=False, size=(85, 85))
            surf.blit(p_surf, (row_x + 10, row_y + 12 + hop_y))

            # Details
            name_col = (220, 60, 0) if is_sel else UI_TEXT
            name_txt = gfx.fonts["medium"].render(p.nickname, True, name_col)
            lvl_txt = gfx.fonts["small"].render(f"Lv. {p.level}", True, UI_TEXT_MUTED)
            surf.blit(name_txt, (row_x + 100, row_y + 12))
            surf.blit(lvl_txt, (row_x + rw - lvl_txt.get_width() - 15, row_y + 15))

            # HP Bar
            gfx.draw_hp_bar(surf, row_x + 130, row_y + 46, 170, 10, p.current_hp, p.max_hp)
            hp_lbl = gfx.fonts["small"].render("HP", True, (240, 160, 20))
            surf.blit(hp_lbl, (row_x + 105, row_y + 42))

            hp_num = gfx.fonts["small"].render(f"{p.current_hp}/{p.max_hp}", True, UI_TEXT)
            surf.blit(hp_num, (row_x + rw - hp_num.get_width() - 15, row_y + 60))

            # Types & Status Badge
            for t_idx, t_name in enumerate(p.types):
                gfx.draw_type_badge(surf, t_name, row_x + 100 + t_idx * 58, row_y + 88, width=52, height=20)

            if p.is_fainted():
                gfx.draw_status_badge(surf, "Fainted", row_x + 100 + len(p.types) * 58, row_y + 88, width=48, height=20)
            elif p.status:
                gfx.draw_status_badge(surf, p.status, row_x + 100 + len(p.types) * 58, row_y + 88, width=48, height=20)

            tgt_evo = p.check_evolution()
            if tgt_evo:
                evo_txt = gfx.fonts["small"].render(f"★ [E]: EVOLVE ➔ {tgt_evo}", True, (20, 150, 50))
                surf.blit(evo_txt, (row_x + rw - evo_txt.get_width() - 15, row_y + 90))
            else:
                m_count_txt = gfx.fonts["small"].render(f"Moves: {len(p.moves)}/4", True, UI_TEXT_MUTED)
                surf.blit(m_count_txt, (row_x + rw - m_count_txt.get_width() - 15, row_y + 90))

        # Bottom Hint Bar
        nav_hint = gfx.fonts["small"].render("Arrows: Select  |  [Z]: Inspect & Reorder  |  [E]: Evolve Ready  |  [S]: Swap Order  |  [X]: Exit", True, UI_TEXT_MUTED)
        surf.blit(nav_hint, (SCREEN_WIDTH // 2 - nav_hint.get_width() // 2, 568))

    def _draw_summary_moves(self, surf):
        curr_pkmn = self.party[self.selected_idx]

        # Top Header
        header_title = f"{curr_pkmn.nickname.upper()}'S SUMMARY & MOVESET"
        head = gfx.fonts["title"].render(header_title, True, (40, 100, 200))
        nav_pkmn = gfx.fonts["regular"].render(f"◀  Pokémon {self.selected_idx + 1}/{len(self.party)}  ▶", True, (220, 80, 0))
        surf.blit(head, (30, 16))
        surf.blit(nav_pkmn, (SCREEN_WIDTH - nav_pkmn.get_width() - 30, 22))

        # Notice Banner
        if self.notice_msg:
            n_txt = gfx.fonts["regular"].render(self.notice_msg, True, (220, 60, 0))
            surf.blit(n_txt, (30, 56))
        else:
            tgt_evo = curr_pkmn.check_evolution()
            if tgt_evo:
                sub_txt = gfx.fonts["regular"].render(f"★ READY TO EVOLVE! Press [E / Tab] to evolve into {tgt_evo.upper()}!", True, (30, 150, 60))
            else:
                sub_txt = gfx.fonts["small"].render("Use [▲/▼] to select moves. Press [Z/Enter] to pick up and swap move positions!", True, UI_TEXT_MUTED)
            surf.blit(sub_txt, (30, 58))

        # 1. Left Panel: Pokemon Profile & Stats
        lx, ly, lw, lh = 30, 88, 320, 460
        pygame.draw.rect(surf, (35, 45, 65), (lx - 2, ly - 2, lw + 4, lh + 4), border_radius=10)
        pygame.draw.rect(surf, WHITE, (lx, ly, lw, lh), border_radius=8)

        # Sprite Card
        p_surf = gfx.get_pokemon_sprite(curr_pkmn.species, is_back=False, size=(120, 120))
        hop_y = -int(abs(math.sin(self.anim_timer * 3.5)) * 4)
        surf.blit(p_surf, (lx + 15, ly + 10 + hop_y))

        # Basic Info
        no_str = f"No. {curr_pkmn.pokedex_id:03d}  Lv. {curr_pkmn.level}"
        no_txt = gfx.fonts["small"].render(no_str, True, UI_TEXT_MUTED)
        name_txt = gfx.fonts["large"].render(curr_pkmn.nickname, True, UI_TEXT)
        surf.blit(no_txt, (lx + 145, ly + 20))
        surf.blit(name_txt, (lx + 145, ly + 42))

        # Types
        for t_i, t_n in enumerate(curr_pkmn.types):
            gfx.draw_type_badge(surf, t_n, lx + 145 + t_i * 64, ly + 76, width=58, height=22)

        # Divider
        pygame.draw.line(surf, (225, 230, 240), (lx + 15, ly + 120), (lx + lw - 15, ly + 120), 2)

        # Stats Table
        stats_data = [
            ("HP", f"{curr_pkmn.current_hp} / {curr_pkmn.max_hp}", (230, 70, 70)),
            ("Attack", str(curr_pkmn.stats.get("atk", 10)), (240, 130, 30)),
            ("Defense", str(curr_pkmn.stats.get("def", 10)), (230, 190, 40)),
            ("Sp. Atk", str(curr_pkmn.stats.get("spatk", 10)), (60, 140, 240)),
            ("Sp. Def", str(curr_pkmn.stats.get("spdef", 10)), (70, 190, 90)),
            ("Speed", str(curr_pkmn.stats.get("spd", 10)), (230, 90, 180)),
        ]

        stat_start_y = ly + 130
        for s_idx, (s_label, s_val, s_col) in enumerate(stats_data):
            sy = stat_start_y + s_idx * 34
            pygame.draw.rect(surf, (250, 252, 255), (lx + 15, sy, lw - 30, 28), border_radius=6)
            pygame.draw.rect(surf, (230, 235, 245), (lx + 15, sy, lw - 30, 28), 1, border_radius=6)

            # Stat Pill Tag
            pygame.draw.rect(surf, s_col, (lx + 20, sy + 4, 70, 20), border_radius=4)
            lbl_surf = gfx.fonts["small"].render(s_label, True, WHITE)
            surf.blit(lbl_surf, (lx + 20 + (70 - lbl_surf.get_width()) // 2, sy + 6))

            val_surf = gfx.fonts["regular"].render(s_val, True, UI_TEXT)
            surf.blit(val_surf, (lx + lw - val_surf.get_width() - 25, sy + 4))

        # EXP Progress Bar
        exp_y = stat_start_y + len(stats_data) * 34 + 10
        exp_lbl = gfx.fonts["small"].render("EXP PROGRESS", True, UI_TEXT_MUTED)
        surf.blit(exp_lbl, (lx + 18, exp_y))
        gfx.draw_exp_bar(surf, lx + 18, exp_y + 18, lw - 36, 8, curr_pkmn.exp_progress_ratio())

        # 2. Right Panel: 4 Move Slots & Move Details
        rx, ry, rw, rh = 370, 88, 400, 460
        pygame.draw.rect(surf, (35, 45, 65), (rx - 2, ry - 2, rw + 4, rh + 4), border_radius=10)
        pygame.draw.rect(surf, WHITE, (rx, ry, rw, rh), border_radius=8)

        # Moves List Header
        move_header = gfx.fonts["large"].render("KNOWN MOVES (SWAP ORDER)", True, (220, 80, 0))
        surf.blit(move_header, (rx + 16, ry + 12))

        for m_idx in range(4):
            my = ry + 44 + m_idx * 64
            is_sel_move = (m_idx == self.selected_move_idx)
            is_swap_src = (m_idx == self.move_swap_source)

            if m_idx < len(curr_pkmn.moves):
                m_data = curr_pkmn.moves[m_idx]
                m_name = m_data.get("name", "Tackle")
                m_type = m_data.get("type", "Normal")
                m_cat = m_data.get("category", "Physical")
                m_pp = m_data.get("pp", 35)
                m_max_pp = m_data.get("max_pp", 35)
                m_pwr = m_data.get("power", 0)

                # Card Colors
                if is_swap_src:
                    bdr_col = (230, 50, 50)
                    bg_col = (255, 230, 230)
                elif is_sel_move:
                    bdr_col = (240, 130, 30)
                    bg_col = (255, 248, 225)
                else:
                    bdr_col = (215, 225, 238)
                    bg_col = (250, 252, 255)

                pygame.draw.rect(surf, bdr_col, (rx + 12, my, rw - 24, 56), 2 if is_sel_move else 1, border_radius=8)
                pygame.draw.rect(surf, bg_col, (rx + 13, my + 1, rw - 26, 54), border_radius=7)

                # Slot Number Pill
                slot_pill_col = (230, 50, 50) if is_swap_src else ((240, 120, 20) if is_sel_move else (50, 100, 180))
                pygame.draw.rect(surf, slot_pill_col, (rx + 20, my + 10, 30, 36), border_radius=5)
                s_num_txt = gfx.fonts["medium"].render(str(m_idx + 1), True, WHITE)
                surf.blit(s_num_txt, (rx + 20 + (30 - s_num_txt.get_width()) // 2, my + 18))

                # Move Name
                m_txt_col = (210, 60, 0) if is_sel_move else UI_TEXT
                m_txt = gfx.fonts["regular"].render(m_name, True, m_txt_col)
                surf.blit(m_txt, (rx + 58, my + 8))

                # Type & Category badges
                gfx.draw_type_badge(surf, m_type, rx + 58, my + 30, width=54, height=18)
                cat_lbl = gfx.fonts["small"].render(m_cat.upper(), True, UI_TEXT_MUTED)
                surf.blit(cat_lbl, (rx + 118, my + 32))

                # Power & PP on the right
                pwr_str = f"Pwr: {m_pwr}" if m_pwr > 0 else "Pwr: --"
                pwr_txt = gfx.fonts["small"].render(pwr_str, True, UI_TEXT)
                pp_str = f"PP {m_pp}/{m_max_pp}"
                pp_txt = gfx.fonts["regular"].render(pp_str, True, (40, 120, 220) if m_pp > 0 else (220, 40, 40))

                surf.blit(pwr_txt, (rx + rw - 130, my + 8))
                surf.blit(pp_txt, (rx + rw - pp_txt.get_width() - 20, my + 28))

                if is_swap_src:
                    swap_tag = gfx.fonts["small"].render("SWAPPING...", True, (220, 40, 40))
                    surf.blit(swap_tag, (rx + rw - swap_tag.get_width() - 20, my + 8))

            else:
                # Empty Move Slot
                pygame.draw.rect(surf, (225, 230, 240), (rx + 12, my, rw - 24, 56), 1, border_radius=8)
                pygame.draw.rect(surf, (245, 248, 252), (rx + 13, my + 1, rw - 26, 54), border_radius=7)
                emp_m = gfx.fonts["regular"].render("- Empty Move Slot -", True, (160, 175, 195))
                surf.blit(emp_m, (rx + (rw - emp_m.get_width()) // 2, my + 18))

        # 3. Selected Move Description Card
        if self.selected_move_idx < len(curr_pkmn.moves):
            sel_move_data = curr_pkmn.moves[self.selected_move_idx]
            acc_val = sel_move_data.get("accuracy", 100)
            acc_str = f"{acc_val}%" if acc_val else "--"
            crit_str = " (High Crit)" if sel_move_data.get("crit_bonus") else ""

            desc_y = ry + 306
            pygame.draw.rect(surf, (245, 248, 255), (rx + 12, desc_y, rw - 24, 140), border_radius=8)
            pygame.draw.rect(surf, (215, 225, 238), (rx + 12, desc_y, rw - 24, 140), 1, border_radius=8)

            d_head = gfx.fonts["small"].render(f"Accuracy: {acc_str}{crit_str}  |  Category: {sel_move_data.get('category', 'Physical')}", True, (50, 100, 180))
            surf.blit(d_head, (rx + 22, desc_y + 10))

            m_desc_str = sel_move_data.get("desc", "No description available.")
            # Word wrap within description box
            words = m_desc_str.split(" ")
            lines = []
            curr_line = ""
            for w in words:
                test = curr_line + (" " if curr_line else "") + w
                if gfx.fonts["small"].size(test)[0] < (rw - 48):
                    curr_line = test
                else:
                    if curr_line:
                        lines.append(curr_line)
                    curr_line = w
            if curr_line:
                lines.append(curr_line)

            for l_i, l_text in enumerate(lines[:4]):
                d_surf = gfx.fonts["small"].render(l_text, True, UI_TEXT)
                surf.blit(d_surf, (rx + 22, desc_y + 32 + l_i * 18))

            # Status effect info if applicable
            eff = sel_move_data.get("effect")
            if eff:
                eff_txt = gfx.fonts["small"].render(f"Effect: {eff.get('status', eff.get('stat', 'Special Effect'))}", True, (210, 80, 0))
                surf.blit(eff_txt, (rx + 22, desc_y + 114))

        # Bottom Hint Bar
        bot_hint = gfx.fonts["small"].render("▲/▼: Select Move  |  [Z/Enter]: Pick up & Swap Move  |  ◀/▶: Prev/Next Pokémon  |  [X]: Back", True, UI_TEXT_MUTED)
        surf.blit(bot_hint, (SCREEN_WIDTH // 2 - bot_hint.get_width() // 2, 568))

