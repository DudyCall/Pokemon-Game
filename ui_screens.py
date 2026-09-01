"""
ui_screens.py - Fullscreen interfaces: Pokedex, Party Summary, Bag, PC Box, Trainer Card (Map), and Quest Log.
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

class BagScreen:
    """
    Comprehensive Player Bag & Item Explanation Screen.
    Allows browsing all acquired items by category (Medicine, Poké Balls, Evolution Stones, etc.),
    reading detailed explanations of what each item is for, and using items directly on Pokémon.
    """
    CATEGORIES = [
        ("ALL", "ALL ITEMS"),
        ("medicine", "MEDICINE"),
        ("ball", "POKÉ BALLS"),
        ("stone", "STONES"),
        ("candy", "CANDIES"),
        ("item", "SPECIAL"),
        ("valuable", "VALUABLES")
    ]

    def __init__(self, party, inventory, quest_mgr=None):
        self.party = party
        self.inventory = inventory
        self.quest_mgr = quest_mgr
        self.category_idx = 0
        self.selected_idx = 0
        self.scroll_offset = 0
        self.mode = "BAG" # "BAG" or "USE_TARGET"
        self.target_pkmn_idx = 0
        self.message = "Browse items to view their purpose and usage. [Z]: Use  [X]: Exit"
        self.success_timer = 0.0

    def update(self, dt):
        if self.success_timer > 0:
            self.success_timer -= dt

    def get_current_category(self):
        return self.CATEGORIES[self.category_idx][0]

    def get_filtered_items(self):
        cat = self.get_current_category()
        return self.inventory.get_items_list(category_filter=cat)

    def _adjust_scroll(self, total_items):
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + 7:
            self.scroll_offset = self.selected_idx - 6

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        # Mode 1: Browsing Bag
        if self.mode == "BAG":
            items = self.get_filtered_items()
            
            # Switch Category Tabs (Left / Right)
            if any(event.key == k for k in KEY_LEFT):
                self.category_idx = (self.category_idx - 1) % len(self.CATEGORIES)
                self.selected_idx = 0
                self.scroll_offset = 0
                sound_mgr.play_sfx("select")
                return None
            elif any(event.key == k for k in KEY_RIGHT):
                self.category_idx = (self.category_idx + 1) % len(self.CATEGORIES)
                self.selected_idx = 0
                self.scroll_offset = 0
                sound_mgr.play_sfx("select")
                return None

            # Navigate Item List (Up / Down)
            if any(event.key == k for k in KEY_UP):
                if items:
                    self.selected_idx = (self.selected_idx - 1) % len(items)
                    self._adjust_scroll(len(items))
                    sound_mgr.play_sfx("select")
                return None
            elif any(event.key == k for k in KEY_DOWN):
                if items:
                    self.selected_idx = (self.selected_idx + 1) % len(items)
                    self._adjust_scroll(len(items))
                    sound_mgr.play_sfx("select")
                return None

            # Exit Bag
            if any(event.key == k for k in KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                return "EXIT"

            # Use Item (Confirm)
            if any(event.key == k for k in KEY_CONFIRM):
                if not items or self.selected_idx >= len(items):
                    return None
                item_name, count, data = items[self.selected_idx]
                category = data.get("category", "")
                
                # Check if usable on Pokémon
                is_usable_on_pkmn = (
                    category in ["medicine", "candy", "stone"] or
                    data.get("is_move_reroll") or
                    "heal_hp" in data or
                    "cure_status" in data or
                    "revive_hp_percent" in data or
                    "level_up" in data or
                    "evolution" in data
                )
                
                if is_usable_on_pkmn:
                    if not self.party:
                        self.message = "No Pokémon in party to use item on!"
                        sound_mgr.play_sfx("cancel")
                        return None
                    self.mode = "USE_TARGET"
                    self.target_pkmn_idx = 0
                    self.message = f"Use {item_name} on which Pokémon? [Up/Down]: Choose, [Z]: Apply, [X]: Cancel"
                    sound_mgr.play_sfx("select")
                    return None
                elif category == "ball":
                    self.message = "Poké Balls can only be thrown during wild battles!"
                    sound_mgr.play_sfx("cancel")
                    return None
                elif category == "valuable":
                    self.message = "Valuable items can be sold at PokéMarts for high prices!"
                    sound_mgr.play_sfx("cancel")
                    return None
                else:
                    # General item use
                    ok, msg = self.inventory.use_item(item_name, quest_mgr=self.quest_mgr)
                    if ok:
                        sound_mgr.play_sfx("confirm")
                        self.message = msg
                        self.success_timer = 3.0
                        new_items = self.get_filtered_items()
                        if self.selected_idx >= len(new_items):
                            self.selected_idx = max(0, len(new_items) - 1)
                    else:
                        sound_mgr.play_sfx("cancel")
                        self.message = msg
                    return None

        # Mode 2: Selecting Pokémon Target to Apply Item
        elif self.mode == "USE_TARGET":
            if any(event.key == k for k in KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                self.mode = "BAG"
                self.message = "Browse items to view their purpose and usage. [Z]: Use  [X]: Exit"
                return None
            elif any(event.key == k for k in KEY_UP):
                self.target_pkmn_idx = (self.target_pkmn_idx - 1) % len(self.party)
                sound_mgr.play_sfx("select")
                return None
            elif any(event.key == k for k in KEY_DOWN):
                self.target_pkmn_idx = (self.target_pkmn_idx + 1) % len(self.party)
                sound_mgr.play_sfx("select")
                return None
            elif any(event.key == k for k in KEY_CONFIRM):
                items = self.get_filtered_items()
                if not items or self.selected_idx >= len(items):
                    self.mode = "BAG"
                    return None
                item_name, count, data = items[self.selected_idx]
                target_pkmn = self.party[self.target_pkmn_idx]
                
                ok, msg = self.inventory.use_item_on_pokemon(item_name, target_pkmn, quest_mgr=self.quest_mgr)
                if ok:
                    sound_mgr.play_sfx("heal" if ("heal" in item_name.lower() or "potion" in item_name.lower() or "revive" in item_name.lower()) else "confirm")
                    self.message = msg
                    self.success_timer = 3.0
                    self.mode = "BAG"
                    new_items = self.get_filtered_items()
                    if self.selected_idx >= len(new_items):
                        self.selected_idx = max(0, len(new_items) - 1)
                else:
                    sound_mgr.play_sfx("cancel")
                    self.message = msg

        return None

    def draw(self, surf):
        surf.fill((235, 240, 248))

        # 1. Top Header
        head = gfx.fonts["title"].render("TRAINER BAG & ITEM MANUAL", True, (40, 100, 200))
        money_txt = gfx.fonts["large"].render(f"💰 Money: ${self.inventory.money}", True, (40, 140, 60))
        surf.blit(head, (30, 14))
        surf.blit(money_txt, (SCREEN_WIDTH - money_txt.get_width() - 30, 18))

        # 2. Category Filter Tabs Header
        tab_y = 62
        tab_w = 100
        for c_idx, (cat_key, cat_lbl) in enumerate(self.CATEGORIES):
            tx = 30 + c_idx * (tab_w + 6)
            is_active = (c_idx == self.category_idx)
            tbdr = (220, 100, 20) if is_active else (190, 200, 215)
            tbg = (255, 235, 180) if is_active else ((250, 252, 255) if c_idx % 2 == 0 else WHITE)
            pygame.draw.rect(surf, tbdr, (tx, tab_y, tab_w, 28), border_radius=6)
            pygame.draw.rect(surf, tbg, (tx + 1, tab_y + 1, tab_w - 2, 26), border_radius=5)
            
            c_txt = gfx.fonts["small"].render(cat_lbl, True, (200, 60, 0) if is_active else UI_TEXT_MUTED)
            surf.blit(c_txt, (tx + (tab_w - c_txt.get_width()) // 2, tab_y + 6))

        # 3. Left Panel (Item List)
        lx, ly, lw, lh = 30, 96, 360, 380
        pygame.draw.rect(surf, (30, 40, 60), (lx - 2, ly - 2, lw + 4, lh + 4), border_radius=10)
        pygame.draw.rect(surf, WHITE, (lx, ly, lw, lh), border_radius=8)

        items = self.get_filtered_items()
        if not items:
            empty_msg = gfx.fonts["regular"].render("No items in this pocket!", True, UI_TEXT_MUTED)
            surf.blit(empty_msg, (lx + (lw - empty_msg.get_width()) // 2, ly + 160))
        else:
            visible_items = items[self.scroll_offset : self.scroll_offset + 7]
            for rel_idx, (name, count, data) in enumerate(visible_items):
                actual_idx = self.scroll_offset + rel_idx
                is_sel = (actual_idx == self.selected_idx)
                iy = ly + 10 + rel_idx * 52

                bdr = (240, 120, 20) if is_sel else (225, 230, 240)
                bg = (255, 238, 200) if is_sel else ((250, 252, 255) if rel_idx % 2 == 0 else WHITE)
                pygame.draw.rect(surf, bdr, (lx + 8, iy, lw - 16, 46), 2 if is_sel else 1, border_radius=8)
                pygame.draw.rect(surf, bg, (lx + 9, iy + 1, lw - 18, 44), border_radius=7)

                # Icon
                icon = gfx.get_item_sprite(name, (32, 32))
                surf.blit(icon, (lx + 16, iy + 7))

                # Name
                name_txt = gfx.fonts["regular"].render(name, True, (200, 60, 0) if is_sel else UI_TEXT)
                surf.blit(name_txt, (lx + 56, iy + 6))

                # Category mini tag & Count
                cat_tag = data.get("category", "item").upper()
                c_lbl = gfx.fonts["small"].render(cat_tag, True, UI_TEXT_MUTED)
                surf.blit(c_lbl, (lx + 56, iy + 26))

                count_pill = gfx.fonts["regular"].render(f"x{count}", True, (30, 130, 50))
                surf.blit(count_pill, (lx + lw - count_pill.get_width() - 20, iy + 12))

            # Scroll indicator
            if len(items) > 7:
                scr_info = gfx.fonts["small"].render(f"▲ ▼ ({self.selected_idx + 1}/{len(items)})", True, (200, 80, 0))
                surf.blit(scr_info, (lx + lw - scr_info.get_width() - 14, ly + lh - 22))

        # 4. Right Panel: Explanation & Purpose Card OR Party Selection Overlay
        rx, ry, rw, rh = 405, 96, 365, 380
        pygame.draw.rect(surf, (30, 40, 60), (rx - 2, ry - 2, rw + 4, rh + 4), border_radius=10)
        pygame.draw.rect(surf, WHITE, (rx, ry, rw, rh), border_radius=8)

        if self.mode == "USE_TARGET":
            # Party Target Selection Overlay
            ovr_head = gfx.fonts["regular"].render("SELECT TARGET POKÉMON", True, (220, 60, 20))
            surf.blit(ovr_head, (rx + (rw - ovr_head.get_width()) // 2, ry + 12))

            for p_idx, p in enumerate(self.party):
                py_row = ry + 40 + p_idx * 54
                is_p_sel = (p_idx == self.target_pkmn_idx)
                pbdr = (240, 100, 20) if is_p_sel else (220, 225, 235)
                pbg = (255, 235, 190) if is_p_sel else ((250, 252, 255) if p_idx % 2 == 0 else WHITE)
                
                pygame.draw.rect(surf, pbdr, (rx + 10, py_row, rw - 20, 48), 2 if is_p_sel else 1, border_radius=8)
                pygame.draw.rect(surf, pbg, (rx + 11, py_row + 1, rw - 22, 46), border_radius=7)

                # Mini Sprite
                p_spr = gfx.get_pokemon_sprite(p.species, is_back=False, size=(42, 42))
                surf.blit(p_spr, (rx + 14, py_row + 3))

                # Name & Lv
                p_lbl = gfx.fonts["small"].render(f"{p.nickname} Lv.{p.level}", True, (200, 60, 0) if is_p_sel else UI_TEXT)
                surf.blit(p_lbl, (rx + 62, py_row + 6))

                # HP Bar
                gfx.draw_hp_bar(surf, rx + 62, py_row + 26, 160, 8, p.current_hp, p.max_hp)
                hp_txt = gfx.fonts["small"].render(f"{p.current_hp}/{p.max_hp}", True, UI_TEXT_MUTED)
                surf.blit(hp_txt, (rx + 230, py_row + 24))

                # Status
                if p.is_fainted():
                    gfx.draw_status_badge(surf, "Fainted", rx + rw - 70, py_row + 6, width=48, height=18)
                elif p.status:
                    gfx.draw_status_badge(surf, p.status, rx + rw - 60, py_row + 6, width=38, height=18)

            tip = gfx.fonts["small"].render("[Z]: Apply Item   [X]: Cancel", True, (40, 100, 200))
            surf.blit(tip, (rx + (rw - tip.get_width()) // 2, ry + rh - 22))

        else:
            # Item Detail & Comprehensive Explanation
            if items and 0 <= self.selected_idx < len(items):
                curr_name, curr_cnt, curr_data = items[self.selected_idx]

                # Top item header strip
                spr = gfx.get_item_sprite(curr_name, (52, 52))
                pygame.draw.rect(surf, (244, 247, 252), (rx + 14, ry + 14, 60, 60), border_radius=8)
                pygame.draw.rect(surf, (215, 225, 240), (rx + 14, ry + 14, 60, 60), 1, border_radius=8)
                surf.blit(spr, (rx + 18, ry + 18))

                name_txt = gfx.fonts["medium"].render(curr_name, True, (30, 45, 80))
                surf.blit(name_txt, (rx + 84, ry + 16))

                cat_name = curr_data.get("category", "item").upper()
                c_pill = gfx.fonts["small"].render(f"CATEGORY: {cat_name}", True, (200, 80, 0))
                surf.blit(c_pill, (rx + 84, ry + 42))

                val_str = f"In Bag: {curr_cnt}  |  Mart Value: ${curr_data.get('price', 0)}"
                v_txt = gfx.fonts["small"].render(val_str, True, (40, 140, 60))
                surf.blit(v_txt, (rx + 84, ry + 60))

                # Section 1: PURPOSE & WHAT IT IS FOR
                p_box_y = ry + 88
                pygame.draw.rect(surf, (248, 250, 255), (rx + 12, p_box_y, rw - 24, 130), border_radius=8)
                pygame.draw.rect(surf, (220, 230, 245), (rx + 12, p_box_y, rw - 24, 130), 1, border_radius=8)
                
                p_head = gfx.fonts["small"].render("📖 PURPOSE & EFFECT:", True, (40, 80, 180))
                surf.blit(p_head, (rx + 20, p_box_y + 8))

                desc_words = curr_data.get("desc", "").split(" ")
                lines, cur = [], ""
                for w in desc_words:
                    t = cur + (" " if cur else "") + w
                    if gfx.fonts["regular"].size(t)[0] < rw - 50:
                        cur = t
                    else:
                        lines.append(cur)
                        cur = w
                if cur:
                    lines.append(cur)
                for l_idx, l_str in enumerate(lines[:4]):
                    surf.blit(gfx.fonts["regular"].render(l_str, True, UI_TEXT), (rx + 20, p_box_y + 32 + l_idx * 22))

                # Section 2: USAGE INSTRUCTIONS
                u_box_y = ry + 228
                pygame.draw.rect(surf, (255, 250, 242), (rx + 12, u_box_y, rw - 24, 105), border_radius=8)
                pygame.draw.rect(surf, (250, 225, 195), (rx + 12, u_box_y, rw - 24, 105), 1, border_radius=8)

                u_head = gfx.fonts["small"].render("⚡ HOW & WHERE TO USE:", True, (210, 80, 20))
                surf.blit(u_head, (rx + 20, u_box_y + 8))

                usage_words = curr_data.get("usage", "Select and use from Bag or in Battle.").split(" ")
                ulines, ucur = [], ""
                for w in usage_words:
                    ut = ucur + (" " if ucur else "") + w
                    if gfx.fonts["regular"].size(ut)[0] < rw - 50:
                        ucur = ut
                    else:
                        ulines.append(ucur)
                        ucur = w
                if ucur:
                    ulines.append(ucur)
                for ul_idx, ul_str in enumerate(ulines[:3]):
                    surf.blit(gfx.fonts["regular"].render(ul_str, True, (80, 70, 60)), (rx + 20, u_box_y + 32 + ul_idx * 22))

                # Bottom Action Cue
                cue = gfx.fonts["small"].render("Press [Z] to Use on Pokémon   [X]: Back", True, (40, 120, 220))
                surf.blit(cue, (rx + (rw - cue.get_width()) // 2, ry + 348))

        # 5. Bottom Message Box
        bx, by, bw, bh = 30, 492, SCREEN_WIDTH - 60, 78
        pygame.draw.rect(surf, (30, 40, 60), (bx - 2, by - 2, bw + 4, bh + 4), border_radius=8)
        pygame.draw.rect(surf, UI_BG, (bx, by, bw, bh), border_radius=6)

        msg_c = (40, 140, 60) if self.success_timer > 0 else UI_TEXT
        surf.blit(gfx.fonts["regular"].render(self.message, True, msg_c), (bx + 20, by + 26))

def get_pokemon_evolution_info(pokemon, inventory=None):
    """
    Returns structured evolution requirements and level milestones for a Pokemon:
    - target_species: str or None
    - method: 'LEVEL', 'STONE', 'NONE'
    - req_level: int or None
    - levels_left: int or None
    - is_ready: bool
    - stone_targets: list of (stone_name, target_species)
    - short_text: str (for mini badges on cards)
    """
    if not pokemon:
        return {"method": "NONE", "short_text": "Empty"}
    species = pokemon.species
    level = pokemon.level
    data = POKEMON_SPECIES.get(species, {})
    lvl_evo = data.get("evolution")

    stone_targets = []
    for s_name, mapping in STONE_EVOLUTIONS.items():
        if species in mapping:
            stone_targets.append((s_name, mapping[species]))

    if lvl_evo and lvl_evo.get("target"):
        req_lvl = lvl_evo.get("level", 100)
        target = lvl_evo.get("target")
        lvls_left = max(0, req_lvl - level)
        is_ready = (level >= req_lvl)
        if is_ready:
            short_txt = f"★ Ready! ➔ {target}"
        else:
            short_txt = f"▲ {target} in {lvls_left} Lvl{'s' if lvls_left != 1 else ''} (Lv.{req_lvl})"
        return {
            "target_species": target,
            "method": "LEVEL",
            "req_level": req_lvl,
            "levels_left": lvls_left,
            "is_ready": is_ready,
            "stone_targets": stone_targets,
            "short_text": short_txt
        }
    elif stone_targets:
        first_target = stone_targets[0][1]
        first_stone = stone_targets[0][0].replace(" Stone", "")
        if len(stone_targets) == 1:
            short_txt = f"💎 {first_stone} Stone ➔ {first_target}"
        else:
            short_txt = f"💎 {len(stone_targets)} Stone Paths"
        return {
            "target_species": first_target,
            "method": "STONE",
            "req_level": None,
            "levels_left": None,
            "is_ready": True,
            "stone_targets": stone_targets,
            "short_text": short_txt
        }
    else:
        return {
            "target_species": None,
            "method": "NONE",
            "req_level": None,
            "levels_left": None,
            "is_ready": False,
            "stone_targets": [],
            "short_text": "👑 Final Form"
        }

def get_full_evolution_tree(current_species):
    """
    Builds the full multi-stage evolution tree (past forms, current form, and future forms).
    Returns (root_species, chain) where chain is a list of node dicts.
    """
    parents = {}
    for parent, data in POKEMON_SPECIES.items():
        evo = data.get("evolution")
        if evo and evo.get("target"):
            parents[evo["target"]] = (parent, {"type": "LEVEL", "level": evo["level"]})
    for stone, mappings in STONE_EVOLUTIONS.items():
        for parent, target in mappings.items():
            if target not in parents:
                parents[target] = (parent, {"type": "STONE", "stone": stone})

    root = current_species
    visited = set()
    while root in parents and root not in visited:
        visited.add(root)
        root = parents[root][0]

    chain = []
    curr = root
    visited_fwd = set()
    while curr and curr not in visited_fwd:
        visited_fwd.add(curr)
        c_data = POKEMON_SPECIES.get(curr, {})
        lvl_evo = c_data.get("evolution")

        stone_evos = []
        for stone, mappings in STONE_EVOLUTIONS.items():
            if curr in mappings:
                stone_evos.append({"stone": stone, "target": mappings[curr]})

        chain.append({
            "species": curr,
            "level_evo": lvl_evo,
            "stone_evos": stone_evos,
            "types": c_data.get("types", ["Normal"]),
            "base_stats": c_data.get("base_stats", {}),
            "learnset": c_data.get("learnset", {})
        })

        if lvl_evo:
            curr = lvl_evo.get("target")
        else:
            curr = None

    return root, chain

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
        # Quick hotkey for Evolution Progression Chart: E, P, or Tab
        if event.key in [pygame.K_e, pygame.K_p, pygame.K_TAB]:
            sel_pkmn = self._get_current_selected_pokemon()
            if sel_pkmn:
                self.evolution_pokemon = sel_pkmn
                self.menu_mode = "EVOLUTION_CHART"
                sound_mgr.play_sfx("confirm")
            else:
                self.show_notification("No Pokémon selected!")
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
        elif any(event.key == k for k in KEY_CANCEL) or event.key in [pygame.K_ESCAPE]:
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
            return ["DEPOSIT TO PC", "SWAP WITH PC", "SUMMARY", "EVOLUTION PROGRESSION", "CANCEL"]
        else:
            return ["WITHDRAW TO PARTY", "SWAP WITH PARTY", "SUMMARY", "EVOLUTION PROGRESSION", "CANCEL"]

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
            mw, mh = 290, 48 + len(actions) * 44
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
            sw, sh = 540, 410
            sx = (SCREEN_WIDTH - sw) // 2
            sy = (SCREEN_HEIGHT - sh) // 2

            pygame.draw.rect(surf, UI_BORDER_DARK, (sx - 2, sy - 2, sw + 4, sh + 4), border_radius=14)
            pygame.draw.rect(surf, WHITE, (sx, sy, sw, sh), border_radius=12)

            # Header
            shead = gfx.fonts["title"].render(f"{p.nickname or p.species} - Level {p.level}", True, (20, 70, 160))
            surf.blit(shead, (sx + 24, sy + 16))

            # Sprite & Types
            sp_surf = gfx.get_pokemon_sprite(p.species, is_back=False, size=(110, 110))
            surf.blit(sp_surf, (sx + 24, sy + 52))

            p_types = POKEMON_SPECIES.get(p.species, {}).get("types", ["Normal"])
            for t_idx, t_name in enumerate(p_types):
                gfx.draw_type_badge(surf, t_name, sx + 24 + t_idx * 70, sy + 170, width=64, height=22)
            if p.is_fainted():
                gfx.draw_status_badge(surf, "Fainted", sx + 24 + len(p_types) * 70, sy + 170, width=54, height=22)
            elif p.status:
                gfx.draw_status_badge(surf, p.status, sx + 24 + len(p_types) * 70, sy + 170, width=54, height=22)

            # Stats Column
            stat_x = sx + 160
            s_hp = gfx.fonts["regular"].render(f"HP: {p.current_hp}/{p.max_hp}", True, UI_TEXT)
            s_atk = gfx.fonts["regular"].render(f"Attack: {p.stats['atk']}", True, UI_TEXT)
            s_def = gfx.fonts["regular"].render(f"Defense: {p.stats['def']}", True, UI_TEXT)
            s_spd = gfx.fonts["regular"].render(f"Speed: {p.stats['spd']}", True, UI_TEXT)
            s_exp = gfx.fonts["small"].render(f"EXP: {p.exp} / {p.exp_for_next_level()}", True, UI_TEXT_MUTED)

            surf.blit(s_hp, (stat_x, sy + 55))
            surf.blit(s_atk, (stat_x, sy + 82))
            surf.blit(s_def, (stat_x, sy + 109))
            surf.blit(s_spd, (stat_x, sy + 136))
            surf.blit(s_exp, (stat_x, sy + 165))

            # Evolution info preview box
            evo_info = get_pokemon_evolution_info(p, self.inventory)
            pygame.draw.rect(surf, (240, 245, 255), (sx + 300, sy + 52, sw - 324, 136), border_radius=8)
            pygame.draw.rect(surf, (200, 215, 240), (sx + 300, sy + 52, sw - 324, 136), 1, border_radius=8)

            e_head = gfx.fonts["small"].render("EVOLUTION MILESTONE", True, (20, 70, 160))
            surf.blit(e_head, (sx + 312, sy + 60))
            e_desc = gfx.fonts["regular"].render(evo_info["short_text"], True, (200, 80, 0) if evo_info["is_ready"] else UI_TEXT)
            surf.blit(e_desc, (sx + 312, sy + 84))

            e_hint = gfx.fonts["small"].render("Press [E / Tab] for Full Progression Chart", True, (40, 110, 220))
            surf.blit(e_hint, (sx + 312, sy + 155))

            # Moves Box
            moves_y = sy + 205
            pygame.draw.rect(surf, (245, 248, 255), (sx + 20, moves_y, sw - 40, 130), border_radius=8)
            pygame.draw.rect(surf, UI_BORDER_LIGHT, (sx + 20, moves_y, sw - 40, 130), 1, border_radius=8)

            m_title = gfx.fonts["small"].render("KNOWN MOVES", True, (40, 100, 200))
            surf.blit(m_title, (sx + 30, moves_y + 8))

            for m_i, m in enumerate(p.moves[:4]):
                mx_pos = sx + 30 + (m_i % 2) * 250
                my_pos = moves_y + 32 + (m_i // 2) * 44
                m_name = gfx.fonts["regular"].render(m.name, True, UI_TEXT)
                m_pp = gfx.fonts["small"].render(f"PP: {m.pp}/{m.max_pp} ({m.type})", True, UI_TEXT_MUTED)
                surf.blit(m_name, (mx_pos, my_pos))
                surf.blit(m_pp, (mx_pos, my_pos + 18))

            close_hint = gfx.fonts["small"].render("Press [Z / X / Enter / ESC] to Close Summary  |  [E / Tab]: Evolution Chart", True, (200, 80, 0))
            surf.blit(close_hint, (sx + (sw - close_hint.get_width()) // 2, sy + 375))

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
        hint = gfx.fonts["small"].render("Left/Right: Switch Panel  |  Up/Down: Select Pokémon  |  [E / Tab]: Evolution Chart  |  [Enter]: Options  |  [X]: Exit PC", True, UI_TEXT_MUTED)
        surf.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 565))

# Re-export TrainerCardScreen and QuestLogScreen for 100% backward compatibility
from ui_trainer import TrainerCardScreen, QuestLogScreen
