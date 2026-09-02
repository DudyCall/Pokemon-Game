"""
ui_bag.py - Player Bag and Item Explanation Screen.
Allows browsing items by category, inspecting details, and using items on party Pokémon.
"""
import random
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY,
    UI_BG, UI_BORDER_DARK, UI_BORDER_LIGHT, UI_TEXT, UI_TEXT_MUTED,
    HP_GREEN, HP_YELLOW, HP_RED, EXP_BLUE, TYPE_COLORS,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_CONFIRM, KEY_CANCEL, KEY_MENU
)
from graphics_manager import gfx
from sound_manager import sound_mgr
from pokemon_data import ITEMS, POKEMON_SPECIES, STONE_EVOLUTIONS, MOVES

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
        self.mode = "BAG" # "BAG", "USE_TARGET", or "CHOOSE_MOVE_TO_REPLACE"
        self.target_pkmn_idx = 0
        self.selected_move_slot = 0
        self.pending_move = None
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
                    self.selected_item_name = item_name
                    self.target_pkmn_idx = 0
                    self.message = f"Use {item_name} on which Pokémon? [Up/Down]: Choose, [Z]: Apply, [X]: Cancel"
                    sound_mgr.play_sfx("select")
                    return None
                elif category == "ball":
                    self.message = "Poké Balls can only be thrown during wild battles!"
                    sound_mgr.play_sfx("cancel")
                    return None
                elif category == "valuable":
                    sell_val = data.get("price", 5000)
                    self.inventory.money += sell_val
                    self.inventory.remove_item(item_name, 1)
                    sound_mgr.play_sfx("confirm")
                    self.message = f"Sold 1 {item_name} for ${sell_val}! (Total Money: ${self.inventory.money})"
                    self.success_timer = 3.0
                    new_items = self.get_filtered_items()
                    if self.selected_idx >= len(new_items):
                        self.selected_idx = max(0, len(new_items) - 1)
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
                item_name = getattr(self, "selected_item_name", None)
                if not item_name or self.inventory.get_count(item_name) <= 0:
                    self.mode = "BAG"
                    return None
                target_pkmn = self.party[self.target_pkmn_idx]
                
                # Special handling for Move Reroll Disk:
                if ITEMS.get(item_name, {}).get("is_move_reroll"):
                    candidates = target_pkmn.get_rerollable_moves()
                    if not candidates:
                        sound_mgr.play_sfx("cancel")
                        self.message = f"{target_pkmn.nickname} already knows all available moves!"
                        return None
                    if len(target_pkmn.moves) < 4:
                        ok, msg = self.inventory.use_item_on_pokemon(item_name, target_pkmn, quest_mgr=self.quest_mgr)
                        if ok:
                            sound_mgr.play_sfx("confirm")
                            self.message = msg
                            self.success_timer = 3.5
                            self.mode = "BAG"
                            new_items = self.get_filtered_items()
                            if self.selected_idx >= len(new_items):
                                self.selected_idx = max(0, len(new_items) - 1)
                        else:
                            sound_mgr.play_sfx("cancel")
                            self.message = msg
                    else:
                        self.pending_move = random.choice(candidates)
                        self.selected_move_slot = 0
                        self.mode = "CHOOSE_MOVE_TO_REPLACE"
                        self.message = f"Rolled '{self.pending_move}'! Select which move {target_pkmn.nickname} should forget: [Up/Down]: Choose, [Z]: Replace, [X]: Cancel"
                        sound_mgr.play_sfx("select")
                    return None

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

        # Mode 3: Selecting Move Slot to Overwrite for Move Reroll Disk
        elif self.mode == "CHOOSE_MOVE_TO_REPLACE":
            target_pkmn = self.party[self.target_pkmn_idx]
            if any(event.key == k for k in KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                self.mode = "USE_TARGET"
                self.pending_move = None
                self.message = f"Use {getattr(self, 'selected_item_name', 'Item')} on which Pokémon? [Up/Down]: Choose, [Z]: Apply, [X]: Cancel"
                return None
            elif any(event.key == k for k in KEY_UP):
                self.selected_move_slot = (self.selected_move_slot - 1) % len(target_pkmn.moves)
                sound_mgr.play_sfx("select")
                return None
            elif any(event.key == k for k in KEY_DOWN):
                self.selected_move_slot = (self.selected_move_slot + 1) % len(target_pkmn.moves)
                sound_mgr.play_sfx("select")
                return None
            elif any(event.key == k for k in KEY_CONFIRM):
                item_name = getattr(self, "selected_item_name", "Move Reroll Disk")
                if self.inventory.get_count(item_name) <= 0:
                    self.mode = "BAG"
                    return None
                ok, msg = self.inventory.use_item_on_pokemon(
                    item_name, target_pkmn, quest_mgr=self.quest_mgr,
                    replace_idx=self.selected_move_slot, specific_move=self.pending_move
                )
                if ok:
                    sound_mgr.play_sfx("confirm")
                    self.message = msg
                    self.success_timer = 3.5
                    self.mode = "BAG"
                    self.pending_move = None
                    new_items = self.get_filtered_items()
                    if self.selected_idx >= len(new_items):
                        self.selected_idx = max(0, len(new_items) - 1)
                else:
                    sound_mgr.play_sfx("cancel")
                    self.message = msg
                return None

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

        elif self.mode == "CHOOSE_MOVE_TO_REPLACE":
            # Move Slot Overwrite Selection Overlay
            target_pkmn = self.party[self.target_pkmn_idx]
            ovr_head = gfx.fonts["regular"].render("SELECT MOVE TO FORGET", True, (220, 60, 20))
            surf.blit(ovr_head, (rx + (rw - ovr_head.get_width()) // 2, ry + 10))

            # 1. New Candidate Technique Box
            m_new = self.pending_move or "New Technique"
            m_data = MOVES.get(m_new, {})
            m_type = m_data.get("type", "Normal")
            m_cat = m_data.get("category", "Physical")
            m_pwr = m_data.get("power", "--")
            m_acc = m_data.get("accuracy", "--")
            m_pp = m_data.get("pp", "--")

            cand_box_y = ry + 32
            pygame.draw.rect(surf, (235, 245, 255), (rx + 10, cand_box_y, rw - 20, 56), border_radius=8)
            pygame.draw.rect(surf, (140, 180, 240), (rx + 10, cand_box_y, rw - 20, 56), 2, border_radius=8)

            lbl_new = gfx.fonts["medium"].render(f"⭐ New Move: {m_new}", True, (20, 60, 140))
            surf.blit(lbl_new, (rx + 18, cand_box_y + 6))

            gfx.draw_type_badge(surf, m_type, rx + 18, cand_box_y + 30, width=54, height=18)
            stat_str = f"Pwr: {m_pwr}  |  Acc: {m_acc}%  |  PP: {m_pp}  |  {m_cat}"
            stat_lbl = gfx.fonts["small"].render(stat_str, True, (60, 80, 120))
            surf.blit(stat_lbl, (rx + 78, cand_box_y + 32))

            # 2. Existing Moves List
            for m_idx, m in enumerate(target_pkmn.moves):
                my_row = ry + 94 + m_idx * 58
                is_m_sel = (m_idx == self.selected_move_slot)
                mbdr = (240, 100, 20) if is_m_sel else (220, 225, 235)
                mbg = (255, 235, 190) if is_m_sel else ((250, 252, 255) if m_idx % 2 == 0 else WHITE)

                pygame.draw.rect(surf, mbdr, (rx + 10, my_row, rw - 20, 52), 2 if is_m_sel else 1, border_radius=8)
                pygame.draw.rect(surf, mbg, (rx + 11, my_row + 1, rw - 22, 50), border_radius=7)

                arrow = "▶ " if is_m_sel else "   "
                m_lbl = gfx.fonts["medium"].render(f"{arrow}{m['name']}", True, (200, 60, 0) if is_m_sel else UI_TEXT)
                surf.blit(m_lbl, (rx + 14, my_row + 5))

                gfx.draw_type_badge(surf, m.get("type", "Normal"), rx + rw - 70, my_row + 6, width=50, height=18)

                m_details = f"Pwr {m.get('power', '--')}   Acc {m.get('accuracy', '--')}%   PP {m['pp']}/{m['max_pp']}   {m.get('category', 'Physical')}"
                m_det_lbl = gfx.fonts["small"].render(m_details, True, UI_TEXT_MUTED)
                surf.blit(m_det_lbl, (rx + 30, my_row + 29))

            tip = gfx.fonts["small"].render("[Z]: Replace Selected Move   [X]: Cancel", True, (40, 100, 200))
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
                if curr_data.get("category") == "valuable":
                    cue = gfx.fonts["small"].render(f"Press [Z] to Sell for ${curr_data.get('price', 5000)}   [X]: Back", True, (40, 140, 60))
                else:
                    cue = gfx.fonts["small"].render("Press [Z] to Use on Pokémon   [X]: Back", True, (40, 120, 220))
                surf.blit(cue, (rx + (rw - cue.get_width()) // 2, ry + 348))

        # 5. Bottom Message Box
        bx, by, bw, bh = 30, 492, SCREEN_WIDTH - 60, 78
        pygame.draw.rect(surf, (30, 40, 60), (bx - 2, by - 2, bw + 4, bh + 4), border_radius=8)
        pygame.draw.rect(surf, UI_BG, (bx, by, bw, bh), border_radius=6)

        msg_c = (40, 140, 60) if self.success_timer > 0 else UI_TEXT
        surf.blit(gfx.fonts["regular"].render(self.message, True, msg_c), (bx + 20, by + 26))


if __name__ == "__main__":
    from main import start
    start()

