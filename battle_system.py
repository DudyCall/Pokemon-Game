"""
battle_system.py - Full turn-based battle engine for wild and trainer encounters.
Includes move execution, animations, catch mechanics, EXP gains, and party switching.
"""
import random
import math
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY,
    UI_BG, UI_BORDER_DARK, UI_BORDER_LIGHT, UI_TEXT, UI_TEXT_MUTED,
    HP_GREEN, HP_YELLOW, HP_RED, EXP_BLUE, TYPE_CHART, TYPE_COLORS, Direction,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_CONFIRM, KEY_CANCEL
)
from graphics_manager import gfx
from sound_manager import sound_mgr
from pokemon_data import MOVES, ITEMS, POKEMON_SPECIES
from battle_vfx import draw_battle_attack_vfx

class BattlePhase:
    INTRO = "INTRO"
    ACTION_MENU = "ACTION_MENU"
    MOVE_SELECT = "MOVE_SELECT"
    BAG_SELECT = "BAG_SELECT"
    PARTY_SELECT = "PARTY_SELECT"
    MESSAGE_QUEUE = "MESSAGE_QUEUE"
    ATTACK_ANIM = "ATTACK_ANIM"
    HP_ANIM = "HP_ANIM"
    EXP_ANIM = "EXP_ANIM"
    CATCH_ANIM = "CATCH_ANIM"
    LEVEL_UP_MODAL = "LEVEL_UP_MODAL"
    LEARN_MOVE_MODAL = "LEARN_MOVE_MODAL"
    VICTORY = "VICTORY"
    FAINT_SWITCH = "FAINT_SWITCH"
    BLACKOUT = "BLACKOUT"
    FINISHED = "FINISHED"

class BattleSystem:
    def __init__(self, player_party, opponent_pokemon_or_trainer, is_trainer=False, inventory=None, pokedex=None, pc_box=None, quest_mgr=None):
        self.player_party = player_party
        self.inventory = inventory
        self.pokedex = pokedex
        self.pc_box = pc_box if pc_box is not None else []
        self.quest_mgr = quest_mgr
        self.is_trainer = is_trainer
        self.trainer_data = opponent_pokemon_or_trainer if is_trainer else None
        
        # Determine opponent team
        if is_trainer:
            from pokemon import Pokemon
            self.opponent_party = [
                Pokemon(p["species"], level=p["level"]) for p in self.trainer_data["party"]
            ]
            self.opponent_index = 0
            self.enemy_pokemon = self.opponent_party[0]
        else:
            self.opponent_party = [opponent_pokemon_or_trainer]
            self.opponent_index = 0
            self.enemy_pokemon = opponent_pokemon_or_trainer
            
        # Register enemy seen in pokedex
        if self.pokedex:
            self.pokedex.register_seen(self.enemy_pokemon.species)
            
        # Find first conscious player pokemon
        self.player_index = 0
        for i, p in enumerate(self.player_party):
            if not p.is_fainted():
                self.player_index = i
                break
        self.player_pokemon = self.player_party[self.player_index]
        
        # State & Menu Variables
        self.phase = BattlePhase.INTRO
        self.action_index = 0 # 0: FIGHT, 1: BAG, 2: POKEMON, 3: RUN
        self.move_index = 0
        self.bag_index = 0
        self.bag_scroll = 0
        self.party_menu_index = 0
        self.party_scroll = 0
        
        # Animations & Transitions
        self.timer = 0.0
        self.messages = []
        self.current_message = ""
        self.msg_char_index = 0
        self.msg_typewriter_speed = 40.0 # chars per second
        self.on_message_complete = None
        
        # Positions
        self.player_pos_x = -150
        self.enemy_pos_x = SCREEN_WIDTH + 150
        self.target_player_x = 100
        self.target_enemy_x = 520
        
        # Move Reorder Mode
        self.move_swap_source = None
        
        # Attack FX
        self.active_fx = None
        self.fx_timer = 0.0
        self.on_status_fx_done = None
        self.screen_shake = 0
        
        # HP drain animation
        self.animating_hp = False
        self.hp_target = 0
        self.hp_target_pokemon = None
        self.hp_is_player = True
        
        # EXP bar animation
        self.animating_exp = False
        self.exp_start_ratio = 0.0
        self.exp_target_ratio = 0.0
        self.exp_curr_ratio = 0.0
        
        # Catch Animation
        self.catch_phase = 0
        self.catch_timer = 0.0
        self.catch_shakes = 0
        self.catch_successful = False
        self.active_ball_type = "Poke Ball"
        
        # Level up event queue
        self.pending_level_events = []
        self.current_stat_diffs = None
        
        # Play battle music
        sound_mgr.play_bgm("battle")
        
        # Queue initial intro messages
        if self.is_trainer:
            self.queue_message(f"{self.trainer_data['name']} wants to battle!", on_done=self._intro_trainer_sendout)
        else:
            self.queue_message(f"Wild {self.enemy_pokemon.species.upper()} appeared!", on_done=self._intro_player_sendout)

    def _intro_trainer_sendout(self):
        self.queue_message(f"{self.trainer_data['name']} sent out {self.enemy_pokemon.species.upper()}!", on_done=self._intro_player_sendout)

    def _intro_player_sendout(self):
        self.queue_message(f"Go! {self.player_pokemon.nickname.upper()}!", on_done=self._start_action_menu)

    def _start_action_menu(self):
        self.phase = BattlePhase.ACTION_MENU
        self.action_index = 0

    def queue_message(self, text, on_done=None):
        self.messages.append((text, on_done))
        if self.phase != BattlePhase.MESSAGE_QUEUE:
            self.advance_message_queue()

    def advance_message_queue(self):
        if self.messages:
            self.current_message, self.on_message_complete = self.messages.pop(0)
            self.msg_char_index = 0
            self.phase = BattlePhase.MESSAGE_QUEUE
        else:
            if self.on_message_complete:
                cb = self.on_message_complete
                self.on_message_complete = None
                cb()
                # If callback queued new messages, pop immediately
                if self.messages and self.phase == BattlePhase.MESSAGE_QUEUE:
                    self.current_message, self.on_message_complete = self.messages.pop(0)
                    self.msg_char_index = 0
            else:
                self.phase = BattlePhase.ACTION_MENU

    def update(self, dt):
        self.timer += dt
        
        # Screen shake decay
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - int(dt * 30))
            
        # Sprite entry slide during Intro
        if self.phase in [BattlePhase.INTRO, BattlePhase.MESSAGE_QUEUE, BattlePhase.ACTION_MENU]:
            if self.player_pos_x < self.target_player_x:
                self.player_pos_x = min(self.target_player_x, self.player_pos_x + int(dt * 800))
            if self.enemy_pos_x > self.target_enemy_x:
                self.enemy_pos_x = max(self.target_enemy_x, self.enemy_pos_x - int(dt * 800))

        # Message typewriter
        if self.phase in [BattlePhase.MESSAGE_QUEUE, BattlePhase.INTRO]:
            if self.msg_char_index < len(self.current_message):
                self.msg_char_index += self.msg_typewriter_speed * dt
                if self.msg_char_index >= len(self.current_message):
                    self.msg_char_index = len(self.current_message)

        # Screen shake decay
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - int(dt * 15))

        # Attack Particle Effect update
        if self.phase == BattlePhase.ATTACK_ANIM:
            self.fx_timer += dt
            if self.fx_timer >= 0.65: # FX duration
                if self.hp_target_pokemon is not None:
                    self.phase = BattlePhase.HP_ANIM
                elif self.on_status_fx_done:
                    cb = self.on_status_fx_done
                    self.on_status_fx_done = None
                    cb()
                else:
                    self.phase = BattlePhase.MESSAGE_QUEUE

        # Smooth HP drain animation
        if self.phase == BattlePhase.HP_ANIM:
            p = self.hp_target_pokemon
            if p:
                if p.current_hp > self.hp_target:
                    p.current_hp = max(self.hp_target, p.current_hp - max(1, int(dt * 40)))
                elif p.current_hp < self.hp_target:
                    p.current_hp = min(self.hp_target, p.current_hp + max(1, int(dt * 40)))
                else:
                    self._after_hp_animation()

        # EXP Bar Growth Animation
        if self.phase == BattlePhase.EXP_ANIM:
            if self.exp_curr_ratio < self.exp_target_ratio:
                self.exp_curr_ratio = min(self.exp_target_ratio, self.exp_curr_ratio + dt * 0.8)
            else:
                self._after_exp_animation()

        # Catch Animation
        if self.phase == BattlePhase.CATCH_ANIM:
            self.catch_timer += dt
            if self.catch_phase == 0: # Ball flying
                if self.catch_timer >= 0.5:
                    self.catch_phase = 1
                    self.catch_timer = 0.0
                    sound_mgr.play_sfx("ball_shake")
            elif self.catch_phase == 1: # Shaking (3 shakes)
                if self.catch_timer >= 0.7:
                    self.catch_timer = 0.0
                    self.catch_shakes += 1
                    if self.catch_shakes < 3:
                        sound_mgr.play_sfx("ball_shake")
                    else:
                        # Final resolution
                        if self.catch_successful:
                            self.catch_phase = 2 # Caught!
                            sound_mgr.play_sfx("catch_success")
                            if self.pokedex:
                                self.pokedex.register_caught(self.enemy_pokemon.species)
                            if self.quest_mgr:
                                self.quest_mgr.on_pokemon_caught(self.enemy_pokemon, self.inventory)
                            if len(self.player_party) < 6:
                                self.player_party.append(self.enemy_pokemon)
                                self.queue_message(f"Gotcha! {self.enemy_pokemon.species.upper()} was caught!", on_done=self._end_battle_victory)
                            else:
                                self.pc_box.append(self.enemy_pokemon)
                                self.queue_message(f"{self.enemy_pokemon.species.upper()} was sent to PC Box!", on_done=self._end_battle_victory)
                        else:
                            self.catch_phase = 3 # Break out!
                            sound_mgr.play_sfx("hit")
                            self.queue_message(f"Oh no! {self.enemy_pokemon.species.upper()} broke free!", on_done=self._enemy_turn_after_item)

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # Advance message box
        if self.phase == BattlePhase.MESSAGE_QUEUE:
            if any(event.key == k for k in KEY_CONFIRM):
                if self.msg_char_index < len(self.current_message):
                    self.msg_char_index = len(self.current_message) # instant reveal
                else:
                    self.advance_message_queue()
            return

        # Main Action Menu (FIGHT, BAG, POKEMON, RUN)
        if self.phase == BattlePhase.ACTION_MENU:
            if any(event.key == k for k in KEY_UP):
                self.action_index = (self.action_index - 2) % 4
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.action_index = (self.action_index + 2) % 4
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_LEFT):
                self.action_index = (self.action_index - 1) % 4
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_RIGHT):
                self.action_index = (self.action_index + 1) % 4
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_CONFIRM):
                sound_mgr.play_sfx("confirm")
                if self.action_index == 0: # FIGHT
                    self.phase = BattlePhase.MOVE_SELECT
                    self.move_index = 0
                elif self.action_index == 1: # BAG
                    self.phase = BattlePhase.BAG_SELECT
                    self.bag_index = 0
                    self.bag_scroll = 0
                elif self.action_index == 2: # POKEMON
                    self.phase = BattlePhase.PARTY_SELECT
                    self.party_menu_index = 0
                    self.party_scroll = 0
                elif self.action_index == 3: # RUN
                    self._attempt_run()

        # Move Selection Menu
        elif self.phase == BattlePhase.MOVE_SELECT:
            num_moves = len(self.player_pokemon.moves)
            if any(event.key == k for k in KEY_UP):
                self.move_index = (self.move_index - 2) % num_moves
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.move_index = (self.move_index + 2) % num_moves
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_LEFT):
                self.move_index = (self.move_index - 1) % num_moves
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_RIGHT):
                self.move_index = (self.move_index + 1) % num_moves
                sound_mgr.play_sfx("select")
            elif event.key in [pygame.K_s, pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_TAB]:
                # Toggle Move Swap Mode
                if self.move_swap_source is None:
                    self.move_swap_source = self.move_index
                    sound_mgr.play_sfx("select")
                else:
                    if self.move_swap_source != self.move_index:
                        self.player_pokemon.swap_moves(self.move_swap_source, self.move_index)
                        sound_mgr.play_sfx("confirm")
                    self.move_swap_source = None
            elif any(event.key == k for k in KEY_CANCEL):
                if self.move_swap_source is not None:
                    self.move_swap_source = None
                    sound_mgr.play_sfx("cancel")
                else:
                    sound_mgr.play_sfx("cancel")
                    self.phase = BattlePhase.ACTION_MENU
            elif any(event.key == k for k in KEY_CONFIRM):
                if self.move_swap_source is not None:
                    if self.move_swap_source != self.move_index:
                        self.player_pokemon.swap_moves(self.move_swap_source, self.move_index)
                        sound_mgr.play_sfx("confirm")
                    self.move_swap_source = None
                    return
                chosen_move = self.player_pokemon.moves[self.move_index]
                if chosen_move["pp"] <= 0:
                    sound_mgr.play_sfx("cancel")
                    # No PP left
                    return
                sound_mgr.play_sfx("confirm")
                self._execute_turn(player_move=chosen_move)

        # Bag Selection Menu
        elif self.phase == BattlePhase.BAG_SELECT:
            items_list = self.inventory.get_items_list() if self.inventory else []
            if not items_list:
                if any(event.key == k for k in KEY_CANCEL + KEY_CONFIRM):
                    self.phase = BattlePhase.ACTION_MENU
                return
                
            if any(event.key == k for k in KEY_UP):
                self.bag_index = (self.bag_index - 1) % len(items_list)
                self._adjust_bag_scroll()
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.bag_index = (self.bag_index + 1) % len(items_list)
                self._adjust_bag_scroll()
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                self.phase = BattlePhase.ACTION_MENU
            elif any(event.key == k for k in KEY_CONFIRM):
                item_name, count, data = items_list[self.bag_index]
                if data.get("category") == "ball":
                    if self.is_trainer:
                        self.queue_message("The trainer blocked your Poké Ball! Don't be a thief!")
                    else:
                        self._use_pokeball(item_name)
                elif data.get("category") in ["medicine", "candy"]:
                    # Use on active pokemon or open party target
                    success, msg = self.inventory.use_item_on_pokemon(item_name, self.player_pokemon)
                    if success:
                        sound_mgr.play_sfx("heal")
                        self.queue_message(msg, on_done=self._enemy_turn_after_item)
                    else:
                        sound_mgr.play_sfx("cancel")

        # Party Selection Menu
        elif self.phase == BattlePhase.PARTY_SELECT:
            if any(event.key == k for k in KEY_UP):
                self.party_menu_index = (self.party_menu_index - 1) % len(self.player_party)
                self._adjust_party_scroll()
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.party_menu_index = (self.party_menu_index + 1) % len(self.player_party)
                self._adjust_party_scroll()
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_CANCEL):
                sound_mgr.play_sfx("cancel")
                self.phase = BattlePhase.ACTION_MENU
            elif any(event.key == k for k in KEY_CONFIRM):
                selected = self.player_party[self.party_menu_index]
                if selected == self.player_pokemon:
                    # Already in battle
                    return
                if selected.is_fainted():
                    sound_mgr.play_sfx("cancel")
                    return
                sound_mgr.play_sfx("confirm")
                self._switch_player_pokemon(self.party_menu_index)

        # Faint Switch Selection
        elif self.phase == BattlePhase.FAINT_SWITCH:
            if any(event.key == k for k in KEY_UP):
                self.party_menu_index = (self.party_menu_index - 1) % len(self.player_party)
                self._adjust_party_scroll()
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_DOWN):
                self.party_menu_index = (self.party_menu_index + 1) % len(self.player_party)
                self._adjust_party_scroll()
                sound_mgr.play_sfx("select")
            elif any(event.key == k for k in KEY_CONFIRM):
                selected = self.player_party[self.party_menu_index]
                if not selected.is_fainted():
                    sound_mgr.play_sfx("confirm")
                    self.player_index = self.party_menu_index
                    self.player_pokemon = selected
                    self.queue_message(f"Go! {self.player_pokemon.nickname.upper()}!", on_done=self._start_action_menu)

        # Level Up Modal
        elif self.phase == BattlePhase.LEVEL_UP_MODAL:
            if any(event.key == k for k in KEY_CONFIRM):
                sound_mgr.play_sfx("confirm")
                self._process_next_level_event()

    def _attempt_run(self):
        if self.is_trainer:
            self.queue_message("No! There's no running from a Trainer battle!")
            return
            
        p_spd = self.player_pokemon.stats.get("spd", 50)
        e_spd = self.enemy_pokemon.stats.get("spd", 50)
        escape_chance = ((p_spd * 128) / max(1, e_spd) + 30) % 256
        
        if random.randint(0, 255) < escape_chance or p_spd >= e_spd:
            sound_mgr.play_sfx("confirm")
            self.queue_message("Got away safely!", on_done=self._end_battle_run)
        else:
            self.queue_message("Can't escape!", on_done=self._enemy_turn_after_item)

    def _use_pokeball(self, ball_name):
        self.inventory.remove_item(ball_name, 1)
        self.active_ball_type = ball_name
        ball_data = ITEMS.get(ball_name, {"catch_mult": 1.0})
        ball_mult = ball_data.get("catch_mult", 1.0)
        
        # Official Pokemon Catch Rate Formula
        max_hp = self.enemy_pokemon.max_hp
        curr_hp = self.enemy_pokemon.current_hp
        catch_rate = self.enemy_pokemon.species_data.get("catch_rate", 45)
        
        status_mult = 1.0
        if self.enemy_pokemon.status in ["Sleep"]:
            status_mult = 2.0
        elif self.enemy_pokemon.status in ["Paralysis", "Poison", "Burn"]:
            status_mult = 1.5
            
        a = (((3 * max_hp - 2 * curr_hp) * catch_rate * ball_mult) / (3 * max_hp)) * status_mult
        
        if a >= 255:
            self.catch_successful = True
        else:
            b = 65536 / ((255 / a) ** 0.1875)
            self.catch_successful = all(random.randint(0, 65535) < b for _ in range(4))
            
        self.phase = BattlePhase.CATCH_ANIM
        self.catch_phase = 0
        self.catch_timer = 0.0
        self.catch_shakes = 0
        sound_mgr.play_sfx("throw")

    def _switch_player_pokemon(self, new_index):
        old_name = self.player_pokemon.nickname
        self.player_index = new_index
        self.player_pokemon = self.player_party[self.player_index]
        self.queue_message(f"Come back, {old_name}!", on_done=lambda: self.queue_message(
            f"Go! {self.player_pokemon.nickname}!", on_done=self._enemy_turn_after_item
        ))

    def _execute_turn(self, player_move):
        # Deduct PP
        player_move["pp"] = max(0, player_move["pp"] - 1)
        
        # Pick enemy move
        enemy_move = random.choice(self.enemy_pokemon.moves)
        enemy_move["pp"] = max(0, enemy_move["pp"] - 1)
        
        # Speed Priority calculation
        p_spd = self.player_pokemon.stats.get("spd", 50)
        e_spd = self.enemy_pokemon.stats.get("spd", 50)
        
        p_prio = player_move.get("priority", 0)
        e_prio = enemy_move.get("priority", 0)
        
        player_first = (p_prio > e_prio) or (p_prio == e_prio and p_spd >= e_spd)
        
        if player_first:
            self._queue_attack(self.player_pokemon, self.enemy_pokemon, player_move, is_player=True,
                               next_attack=lambda: self._queue_attack(self.enemy_pokemon, self.player_pokemon, enemy_move, is_player=False))
        else:
            self._queue_attack(self.enemy_pokemon, self.player_pokemon, enemy_move, is_player=False,
                               next_attack=lambda: self._queue_attack(self.player_pokemon, self.enemy_pokemon, player_move, is_player=True))

    def _enemy_turn_after_item(self):
        if self.enemy_pokemon.is_fainted():
            self._handle_enemy_faint()
            return
        enemy_move = random.choice(self.enemy_pokemon.moves)
        self._queue_attack(self.enemy_pokemon, self.player_pokemon, enemy_move, is_player=False)

    def _queue_attack(self, attacker, defender, move, is_player, next_attack=None):
        if attacker.is_fainted():
            return
            
        # Check Sleep / Paralysis
        if attacker.status == "Sleep":
            attacker.sleep_turns -= 1
            if attacker.sleep_turns > 0:
                self.queue_message(f"{attacker.nickname} is fast asleep.", on_done=next_attack)
                return
            else:
                attacker.cure_status()
                self.queue_message(f"{attacker.nickname} woke up!")
                
        if attacker.status == "Paralysis" and random.random() < 0.25:
            self.queue_message(f"{attacker.nickname} is fully paralyzed! It can't move!", on_done=next_attack)
            return

        def perform_move():
            # Check accuracy
            acc = move.get("accuracy", 100)
            if random.randint(1, 100) > acc:
                self.queue_message(f"{attacker.nickname}'s attack missed!", on_done=next_attack)
                return
                
            # Play move sound
            m_type = move.get("type", "Normal")
            if m_type == "Fire":
                sound_mgr.play_sfx("fire")
            elif m_type == "Water":
                sound_mgr.play_sfx("water")
            elif m_type == "Electric":
                sound_mgr.play_sfx("electric")
            elif m_type == "Grass":
                sound_mgr.play_sfx("grass")
            else:
                sound_mgr.play_sfx("hit")

            # Damage Calculation
            power = move.get("power", 0)
            category = move.get("category", "Physical")
            
            if power > 0:
                is_crit = random.random() < (0.125 if move.get("crit_bonus") else 0.0625)
                
                # Attack vs Defense stats
                if category == "Physical":
                    atk = attacker.stats.get("atk", 50)
                    defn = defender.stats.get("def", 50)
                else: # Special
                    atk = attacker.stats.get("spatk", 50)
                    defn = defender.stats.get("spdef", 50)
                    
                # Type Effectiveness
                effectiveness = 1.0
                for def_type in defender.types:
                    mult = TYPE_CHART.get(m_type, {}).get(def_type, 1.0)
                    effectiveness *= mult
                    
                # STAB (Same Type Attack Bonus)
                stab = 1.5 if m_type in attacker.types else 1.0
                
                # Random factor 85% to 100%
                rand_factor = random.uniform(0.85, 1.0)
                
                dmg = math.floor((((2 * attacker.level / 5 + 2) * power * (atk / max(1, defn))) / 50 + 2) * stab * effectiveness * (1.5 if is_crit else 1.0) * rand_factor)
                dmg = max(1, dmg)
                
                # Apply damage with animation
                self.hp_target = max(0, defender.current_hp - dmg)
                self.hp_target_pokemon = defender
                self.hp_is_player = not is_player
                self.screen_shake = 8 if is_crit or effectiveness > 1.0 else 4
                self.active_fx = {
                    "move_name": move.get("name", "Attack"),
                    "move_type": m_type,
                    "is_player_attacker": is_player,
                    "is_crit": is_crit,
                    "effectiveness": effectiveness,
                    "category": category
                }
                self.fx_timer = 0.0
                self.phase = BattlePhase.ATTACK_ANIM
                
                # Post attack comments
                def on_damage_applied():
                    if is_crit:
                        self.queue_message("A critical hit!")
                    if effectiveness > 1.0:
                        sound_mgr.play_sfx("super_hit")
                        self.queue_message("It's super effective!")
                    elif 0 < effectiveness < 1.0:
                        self.queue_message("It's not very effective...")
                    elif effectiveness == 0.0:
                        self.queue_message("It had no effect!")
                        
                    # Check Secondary Status Effect
                    eff = move.get("effect")
                    if eff and "status" in eff:
                        if random.randint(1, 100) <= eff.get("chance", 100):
                            if defender.apply_status(eff["status"]):
                                self.queue_message(f"{defender.nickname} became {eff['status']}ed!")
                                
                    # Check Drain
                    if eff and "drain_percent" in eff:
                        heal_amt = int(dmg * (eff["drain_percent"] / 100))
                        attacker.heal(heal_amt)
                        self.queue_message(f"{attacker.nickname} regained {heal_amt} HP!")

                    # Check Faint
                    if defender.is_fainted():
                        sound_mgr.play_sfx("faint")
                        is_player_fainted = (defender in self.player_party)
                        self.queue_message(f"{defender.nickname} fainted!", on_done=self._handle_faint(defender, is_player_fainted))
                    elif next_attack:
                        next_attack()
                    else:
                        self._check_end_of_turn_status()
                        
                self.on_hp_done = on_damage_applied
            else:
                # Status only move (e.g. Growl, Tail Whip, Recover, Leech Seed)
                self.hp_target_pokemon = None
                self.active_fx = {
                    "move_name": move.get("name", "Status"),
                    "move_type": m_type,
                    "is_player_attacker": is_player,
                    "is_crit": False,
                    "effectiveness": 1.0,
                    "category": "Special"
                }
                self.fx_timer = 0.0

                def apply_status_move_outcome():
                    on_next = next_attack if next_attack else self._check_end_of_turn_status
                    eff = move.get("effect") or {}
                    if "heal_percent" in eff:
                        healed = attacker.heal(int(attacker.max_hp * (eff["heal_percent"] / 100)))
                        self.queue_message(f"{attacker.nickname} restored {healed} HP!", on_done=on_next)
                    elif "status" in eff:
                        if defender.apply_status(eff["status"]):
                            self.queue_message(f"{defender.nickname} became {eff['status']}ed!", on_done=on_next)
                        else:
                            self.queue_message("But it failed!", on_done=on_next)
                    elif "stat" in eff and "stages" in eff:
                        stat_name = eff["stat"].upper()
                        stages = eff["stages"]
                        target = defender if stages < 0 else attacker
                        change_word = "harshly fell" if stages <= -2 else ("fell" if stages < 0 else ("sharply rose" if stages >= 2 else "rose"))
                        self.queue_message(f"{target.nickname}'s {stat_name} {change_word}!", on_done=on_next)
                    else:
                        self.queue_message(f"{attacker.nickname}'s {move['name']} was successful!", on_done=on_next)

                self.on_status_fx_done = apply_status_move_outcome
                self.phase = BattlePhase.ATTACK_ANIM

        self.queue_message(f"{attacker.nickname} used {move['name']}!", on_done=perform_move)

    def _check_end_of_turn_status(self):
        """Processes end-of-turn residual status effects like Poison and Burn damage."""
        if self.enemy_pokemon.is_fainted() or self.player_pokemon.is_fainted() or self.phase in [BattlePhase.FINISHED, BattlePhase.BLACKOUT]:
            return

        status_events = []
        
        # 1. Player Status Tick
        if not self.player_pokemon.is_fainted():
            if self.player_pokemon.status == "Poison":
                p_dmg = max(1, self.player_pokemon.max_hp // 8)
                status_events.append(("player", p_dmg, f"{self.player_pokemon.nickname} is hurt by poison!"))
            elif self.player_pokemon.status == "Burn":
                p_dmg = max(1, self.player_pokemon.max_hp // 16)
                status_events.append(("player", p_dmg, f"{self.player_pokemon.nickname} is hurt by its burn!"))

        # 2. Enemy Status Tick
        if not self.enemy_pokemon.is_fainted():
            if self.enemy_pokemon.status == "Poison":
                e_dmg = max(1, self.enemy_pokemon.max_hp // 8)
                status_events.append(("enemy", e_dmg, f"{self.enemy_pokemon.species.upper()} is hurt by poison!"))
            elif self.enemy_pokemon.status == "Burn":
                e_dmg = max(1, self.enemy_pokemon.max_hp // 16)
                status_events.append(("enemy", e_dmg, f"{self.enemy_pokemon.species.upper()} is hurt by its burn!"))

        def process_next_event():
            if not status_events or self.enemy_pokemon.is_fainted() or self.player_pokemon.is_fainted():
                self.phase = BattlePhase.ACTION_MENU
                return
                
            side, dmg, msg = status_events.pop(0)
            target = self.player_pokemon if side == "player" else self.enemy_pokemon
            
            if target.is_fainted():
                process_next_event()
                return
                
            sound_mgr.play_sfx("hit")
            self.hp_target = max(0, target.current_hp - dmg)
            self.hp_target_pokemon = target
            self.hp_is_player = (side == "player")
            self.screen_shake = 4
            self.phase = BattlePhase.HP_ANIM
            
            def after_tick():
                if target.is_fainted():
                    sound_mgr.play_sfx("faint")
                    is_player = (side == "player")
                    self.queue_message(f"{target.nickname} fainted!", on_done=self._handle_faint(target, is_player))
                else:
                    self.queue_message(msg, on_done=process_next_event)
                    
            self.on_hp_done = after_tick

        if status_events:
            process_next_event()
        else:
            self.phase = BattlePhase.ACTION_MENU

    def _after_hp_animation(self):
        if hasattr(self, 'on_hp_done') and self.on_hp_done:
            cb = self.on_hp_done
            self.on_hp_done = None
            cb()
        else:
            self.phase = BattlePhase.ACTION_MENU

    def _handle_faint(self, fainted_pkmn, is_player_fainted=None):
        if is_player_fainted is None:
            is_player_fainted = (fainted_pkmn in self.player_party)
            
        def handler():
            if is_player_fainted:
                # Player Pokemon fainted
                alive_pkmn = [p for p in self.player_party if not p.is_fainted()]
                if alive_pkmn:
                    self.phase = BattlePhase.FAINT_SWITCH
                    self.party_menu_index = 0
                    self.party_scroll = 0
                else:
                    # Blackout
                    sound_mgr.play_sfx("faint")
                    self.queue_message("You are out of usable Pokémon!", on_done=lambda: self.queue_message(
                        "You whited out and rushed to the Pokémon Center...", on_done=self._end_battle_blackout
                    ))
            else:
                # Enemy Pokemon fainted -> Gain EXP
                if self.quest_mgr:
                    self.quest_mgr.on_pokemon_defeated(self.enemy_pokemon, self.inventory, is_trainer=self.is_trainer)
                self._award_exp()
        return handler

    def _award_exp(self):
        base_exp = self.enemy_pokemon.species_data.get("base_exp", 60)
        trainer_bonus = 1.5 if self.is_trainer else 1.0
        exp_gain = math.floor((base_exp * self.enemy_pokemon.level * trainer_bonus) / 7)
        exp_gain = max(10, exp_gain)
        
        self.queue_message(f"{self.player_pokemon.nickname} gained {exp_gain} EXP. Points!", on_done=lambda: self._start_exp_animation(exp_gain))

    def _start_exp_animation(self, exp_gain):
        self.exp_start_ratio = self.player_pokemon.exp_progress_ratio()
        self.pending_level_events = self.player_pokemon.gain_exp(exp_gain)
        self.exp_target_ratio = self.player_pokemon.exp_progress_ratio()
        self.exp_curr_ratio = self.exp_start_ratio
        self.phase = BattlePhase.EXP_ANIM

    def _after_exp_animation(self):
        if self.pending_level_events:
            self._process_next_level_event()
        else:
            self._check_next_enemy_or_victory()

    def _process_next_level_event(self):
        if not self.pending_level_events:
            self._check_next_enemy_or_victory()
            return
            
        event_type, *args = self.pending_level_events.pop(0)
        if event_type == "LEVEL_UP":
            lvl, stat_diffs = args
            sound_mgr.play_sfx("level_up")
            self.current_stat_diffs = stat_diffs
            self.phase = BattlePhase.LEVEL_UP_MODAL
        elif event_type == "LEARN_MOVE":
            move_name = args[0]
            success, msg = self.player_pokemon.learn_move(move_name)
            self.queue_message(msg, on_done=self._process_next_level_event)
        elif event_type == "EVOLVE":
            target_species = args[0]
            self.player_pokemon.evolve(target_species)
            sound_mgr.play_sfx("level_up")
            self.queue_message(f"What? {self.player_pokemon.nickname} is evolving!", on_done=lambda: self.queue_message(
                f"Congratulations! Your Pokémon evolved into {target_species.upper()}!", on_done=self._process_next_level_event
            ))

    def _check_next_enemy_or_victory(self):
        if self.is_trainer:
            self.opponent_index += 1
            if self.opponent_index < len(self.opponent_party):
                self.enemy_pokemon = self.opponent_party[self.opponent_index]
                self.queue_message(f"{self.trainer_data['name']} sent out {self.enemy_pokemon.species.upper()}!", on_done=self._start_action_menu)
                return
                
        # Victory!
        self._end_battle_victory()

    def _end_battle_victory(self):
        sound_mgr.play_bgm("victory", loop=False)
        if self.is_trainer:
            prize = self.trainer_data.get("reward_money", 200)
            if self.inventory:
                self.inventory.money += prize
            if self.quest_mgr and self.trainer_data:
                self.quest_mgr.on_trainer_defeated(self.trainer_data.get("id"), self.inventory)
            self.queue_message(f"You defeated {self.trainer_data['name']}!", on_done=lambda: self.queue_message(
                f"You got ${prize} for winning!", on_done=self._finish_battle
            ))
        else:
            self.queue_message(f"Defeated wild {self.enemy_pokemon.species.upper()}!", on_done=self._finish_battle)

    def _end_battle_run(self):
        self._finish_battle()

    def _end_battle_blackout(self):
        self.phase = BattlePhase.BLACKOUT
        self.result = "BLACKOUT"

    def _finish_battle(self):
        self.phase = BattlePhase.FINISHED
        self.result = "VICTORY"

    def _adjust_bag_scroll(self):
        items_list = self.inventory.get_items_list() if self.inventory else []
        total = len(items_list)
        if total <= 4:
            self.bag_scroll = 0
            return
        if self.bag_index < self.bag_scroll:
            self.bag_scroll = self.bag_index
        elif self.bag_index >= self.bag_scroll + 4:
            self.bag_scroll = self.bag_index - 3

    def _adjust_party_scroll(self):
        total = len(self.player_party)
        if total <= 4:
            self.party_scroll = 0
            return
        if self.party_menu_index < self.party_scroll:
            self.party_scroll = self.party_menu_index
        elif self.party_menu_index >= self.party_scroll + 4:
            self.party_scroll = self.party_menu_index - 3

    def draw(self, surf):
        # Battle Background (Sky & Grass Platform)
        surf.fill((216, 240, 248)) # Soft sky blue
        
        # Ground Platform Circles
        enemy_plat_x = self.target_enemy_x - 30
        enemy_plat_y = 190
        pygame.draw.ellipse(surf, (150, 200, 140), (enemy_plat_x, enemy_plat_y, 220, 50))
        pygame.draw.ellipse(surf, (120, 180, 110), (enemy_plat_x + 4, enemy_plat_y + 4, 212, 42))

        player_plat_x = self.target_player_x - 50
        player_plat_y = 350
        pygame.draw.ellipse(surf, (150, 200, 140), (player_plat_x, player_plat_y, 260, 60))
        pygame.draw.ellipse(surf, (120, 180, 110), (player_plat_x + 6, player_plat_y + 4, 248, 52))

        # Draw Enemy Pokemon
        if not self.enemy_pokemon.is_fainted() and self.catch_phase != 2:
            e_surf = gfx.get_pokemon_sprite(self.enemy_pokemon.species, is_back=False, size=(160, 160))
            e_draw_y = 70
            gfx.draw_pokemon_with_status_effects(
                surf, self.enemy_pokemon, int(self.enemy_pos_x), e_draw_y + 80, e_surf, self.timer, is_back=False
            )

        # Draw Player Pokemon
        if not self.player_pokemon.is_fainted():
            p_surf = gfx.get_pokemon_sprite(self.player_pokemon.species, is_back=True, size=(180, 180))
            p_draw_y = 200
            gfx.draw_pokemon_with_status_effects(
                surf, self.player_pokemon, int(self.player_pos_x), p_draw_y + 90, p_surf, self.timer, is_back=True
            )

        # Draw Catch Pokéball Animation
        if self.phase == BattlePhase.CATCH_ANIM:
            ball_icon = gfx.item_sprites.get(self.active_ball_type, gfx.item_sprites["Poke Ball"])
            bx = enemy_plat_x + 80
            by = enemy_plat_y + 10
            if self.catch_phase == 0:
                # Arc throw
                t = self.catch_timer / 0.5
                bx = player_plat_x + 100 + (enemy_plat_x + 80 - (player_plat_x + 100)) * t
                by = player_plat_y - math.sin(t * 3.14) * 120
            elif self.catch_phase == 1:
                # Wiggle
                bx += math.sin(self.catch_timer * 15) * 6
            surf.blit(ball_icon, (int(bx), int(by)))

        # Draw Attack Particle & Elemental Visual Effects Overlay
        if self.phase == BattlePhase.ATTACK_ANIM and self.active_fx:
            player_center = (int(self.player_pos_x) + 90, 200 + 90)
            enemy_center = (int(self.enemy_pos_x) + 80, 70 + 80)
            draw_battle_attack_vfx(surf, self.active_fx, self.fx_timer, player_center, enemy_center)

        # Draw HUD Cards (Enemy Top-Left, Player Bottom-Right)
        self._draw_enemy_hud(surf)
        self._draw_player_hud(surf)

        # Draw Bottom Battle Dialogue / Action Area
        self._draw_bottom_panel(surf)

        # Draw Level Up Stat Modal if active
        if self.phase == BattlePhase.LEVEL_UP_MODAL:
            self._draw_level_up_modal(surf)

    def _draw_enemy_hud(self, surf):
        x, y, w, h = 40, 40, 260, 75
        # Background card
        pygame.draw.rect(surf, UI_BORDER_DARK, (x - 2, y - 2, w + 4, h + 4), border_radius=8)
        pygame.draw.rect(surf, UI_BG, (x, y, w, h), border_radius=6)
        
        # Enemy Name & Level
        name_txt = gfx.fonts["regular"].render(self.enemy_pokemon.species.upper(), True, UI_TEXT)
        lvl_txt = gfx.fonts["small"].render(f"Lv.{self.enemy_pokemon.level}", True, UI_TEXT_MUTED)
        surf.blit(name_txt, (x + 12, y + 10))
        surf.blit(lvl_txt, (x + w - lvl_txt.get_width() - 12, y + 12))
        
        # HP Bar
        bar_w = 180 if not self.enemy_pokemon.status else 136
        gfx.draw_hp_bar(surf, x + 50, y + 42, bar_w, 10, self.enemy_pokemon.current_hp, self.enemy_pokemon.max_hp)
        hp_lbl = gfx.fonts["small"].render("HP", True, (240, 180, 40))
        surf.blit(hp_lbl, (x + 22, y + 38))
        
        # Enemy Status Badge
        if self.enemy_pokemon.status:
            gfx.draw_status_badge(surf, self.enemy_pokemon.status, x + 50 + bar_w + 6, y + 38, width=38, height=18)

    def _draw_player_hud(self, surf):
        x, y, w, h = 480, 250, 280, 110
        pygame.draw.rect(surf, UI_BORDER_DARK, (x - 2, y - 2, w + 4, h + 4), border_radius=8)
        pygame.draw.rect(surf, UI_BG, (x, y, w, h), border_radius=6)
        
        # Player Nickname & Level
        name_txt = gfx.fonts["regular"].render(self.player_pokemon.nickname.upper(), True, UI_TEXT)
        lvl_txt = gfx.fonts["small"].render(f"Lv.{self.player_pokemon.level}", True, UI_TEXT_MUTED)
        surf.blit(name_txt, (x + 12, y + 10))
        surf.blit(lvl_txt, (x + w - lvl_txt.get_width() - 12, y + 12))
        
        # HP Bar
        gfx.draw_hp_bar(surf, x + 50, y + 38, 200, 10, self.player_pokemon.current_hp, self.player_pokemon.max_hp)
        hp_lbl = gfx.fonts["small"].render("HP", True, (240, 180, 40))
        surf.blit(hp_lbl, (x + 22, y + 34))
        
        # Player Status Badge
        if self.player_pokemon.status:
            gfx.draw_status_badge(surf, self.player_pokemon.status, x + 50, y + 52, width=38, height=18)
        
        # Numeric HP
        hp_num = gfx.fonts["small"].render(f"{self.player_pokemon.current_hp} / {self.player_pokemon.max_hp}", True, UI_TEXT)
        surf.blit(hp_num, (x + w - hp_num.get_width() - 14, y + 52))
        
        # EXP Bar
        ratio = self.exp_curr_ratio if self.phase == BattlePhase.EXP_ANIM else self.player_pokemon.exp_progress_ratio()
        gfx.draw_exp_bar(surf, x + 50, y + 74, 200, 6, ratio)
        exp_lbl = gfx.fonts["small"].render("EXP", True, EXP_BLUE)
        surf.blit(exp_lbl, (x + 16, y + 68))

        # Numeric EXP
        if self.player_pokemon.level >= 100:
            exp_str = f"{self.player_pokemon.exp} / MAX"
        elif self.phase == BattlePhase.EXP_ANIM:
            curr_lvl_exp = self.player_pokemon.calc_exp_for_level(self.player_pokemon.level)
            next_lvl_exp = self.player_pokemon.exp_for_next_level()
            anim_exp = int(curr_lvl_exp + self.exp_curr_ratio * max(1, next_lvl_exp - curr_lvl_exp))
            exp_str = f"{anim_exp} / {next_lvl_exp}"
        else:
            exp_str = f"{self.player_pokemon.exp} / {self.player_pokemon.exp_for_next_level()}"

        exp_num = gfx.fonts["small"].render(exp_str, True, UI_TEXT)
        surf.blit(exp_num, (x + w - exp_num.get_width() - 14, y + 84))

    def _draw_bottom_panel(self, surf):
        bx, by, bw, bh = 20, 400, SCREEN_WIDTH - 40, 180
        pygame.draw.rect(surf, UI_BORDER_DARK, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=10)
        pygame.draw.rect(surf, UI_BG, (bx, by, bw, bh), border_radius=8)
        
        # Message Display
        if self.phase in [BattlePhase.MESSAGE_QUEUE, BattlePhase.INTRO, BattlePhase.HP_ANIM, BattlePhase.EXP_ANIM, BattlePhase.CATCH_ANIM]:
            visible_text = self.current_message[:int(self.msg_char_index)]
            txt = gfx.fonts["medium"].render(visible_text, True, UI_TEXT)
            surf.blit(txt, (bx + 24, by + 40))
            return

        # Main Action Menu
        if self.phase == BattlePhase.ACTION_MENU:
            prompt = gfx.fonts["medium"].render(f"What will {self.player_pokemon.nickname} do?", True, UI_TEXT)
            surf.blit(prompt, (bx + 24, by + 40))
            
            # 4 Action buttons (FIGHT, BAG, POKEMON, RUN)
            btn_w, btn_h = 140, 50
            positions = [
                (bw - 320, 25), (bw - 160, 25),
                (bw - 320, 95), (bw - 160, 95)
            ]
            labels = ["FIGHT", "BAG", "POKÉMON", "RUN"]
            
            for i, (lx, ly) in enumerate(positions):
                rx = bx + lx
                ry = by + ly
                is_sel = (self.action_index == i)
                bg_col = (255, 235, 180) if is_sel else WHITE
                bdr_col = (240, 140, 40) if is_sel else UI_BORDER_LIGHT
                pygame.draw.rect(surf, bdr_col, (rx, ry, btn_w, btn_h), border_radius=8)
                pygame.draw.rect(surf, bg_col, (rx + 2, ry + 2, btn_w - 4, btn_h - 4), border_radius=6)
                
                ltxt = gfx.fonts["regular"].render(labels[i], True, UI_TEXT if not is_sel else (180, 60, 0))
                surf.blit(ltxt, (rx + (btn_w - ltxt.get_width()) // 2, ry + (btn_h - ltxt.get_height()) // 2))

        # Move Selection Sub-Menu
        elif self.phase == BattlePhase.MOVE_SELECT:
            btn_w, btn_h = 240, 60
            positions = [(30, 20), (290, 20), (30, 95), (290, 95)]
            
            for i, move in enumerate(self.player_pokemon.moves):
                lx, ly = positions[i]
                rx = bx + lx
                ry = by + ly
                is_sel = (self.move_index == i)
                is_swap = (self.move_swap_source == i)

                if is_swap:
                    bg_col = (255, 225, 225)
                    bdr_col = (230, 50, 50)
                elif is_sel:
                    bg_col = (255, 245, 210)
                    bdr_col = (240, 140, 40)
                else:
                    bg_col = WHITE
                    bdr_col = UI_BORDER_LIGHT

                pygame.draw.rect(surf, bdr_col, (rx, ry, btn_w, btn_h), 2 if (is_sel or is_swap) else 1, border_radius=8)
                pygame.draw.rect(surf, bg_col, (rx + 2, ry + 2, btn_w - 4, btn_h - 4), border_radius=6)
                
                # Move Name
                mtxt = gfx.fonts["regular"].render(move["name"], True, (210, 60, 0) if is_sel else UI_TEXT)
                surf.blit(mtxt, (rx + 12, ry + 10))
                
                # Type badge & PP
                gfx.draw_type_badge(surf, move["type"], rx + 12, ry + 32, width=60, height=20)
                pp_txt = gfx.fonts["small"].render(f"PP {move['pp']}/{move['max_pp']}", True, UI_TEXT_MUTED)
                surf.blit(pp_txt, (rx + btn_w - pp_txt.get_width() - 12, ry + 34))

                if is_swap:
                    sw_lbl = gfx.fonts["small"].render("SWAP", True, (230, 50, 50))
                    surf.blit(sw_lbl, (rx + btn_w - sw_lbl.get_width() - 12, ry + 10))

            # Bottom Hint
            swap_hint = gfx.fonts["small"].render("[S / Shift / Tab]: Swap Move Positions  |  [X]: Back", True, (40, 100, 180))
            surf.blit(swap_hint, (bx + 20, by + bh - 18))

        # Bag Selection Sub-Menu with Live Item Explanation Tooltip
        elif self.phase == BattlePhase.BAG_SELECT:
            items_list = self.inventory.get_items_list() if self.inventory else []
            title = gfx.fonts["medium"].render("Select an Item to Use:", True, (40, 80, 160))
            surf.blit(title, (bx + 20, by + 12))
            
            if not items_list:
                empty_txt = gfx.fonts["regular"].render("Your bag is empty!", True, UI_TEXT_MUTED)
                surf.blit(empty_txt, (bx + 20, by + 60))
            else:
                self._adjust_bag_scroll()
                visible_items = items_list[self.bag_scroll : self.bag_scroll + 4]
                
                # Left Column: Item Selector
                for rel_idx, (name, count, data) in enumerate(visible_items):
                    actual_idx = self.bag_scroll + rel_idx
                    iy = by + 45 + rel_idx * 30
                    is_sel = (self.bag_index == actual_idx)
                    
                    if is_sel:
                        pygame.draw.rect(surf, (255, 235, 180), (bx + 16, iy - 3, 310, 28), border_radius=5)
                        pygame.draw.rect(surf, (240, 140, 40), (bx + 16, iy - 3, 310, 28), 1, border_radius=5)
                    
                    # Mini Icon
                    icon = gfx.get_item_sprite(name, (22, 22))
                    surf.blit(icon, (bx + 22, iy))

                    itxt = gfx.fonts["regular"].render(name, True, (200, 60, 0) if is_sel else UI_TEXT)
                    c_txt = gfx.fonts["regular"].render(f"x{count}", True, (30, 130, 50))
                    surf.blit(itxt, (bx + 50, iy))
                    surf.blit(c_txt, (bx + 280, iy))

                if len(items_list) > 4:
                    scroll_info = gfx.fonts["small"].render(f"▲ ▼ ({self.bag_index + 1}/{len(items_list)})", True, (200, 80, 0))
                    surf.blit(scroll_info, (bx + 250, by + 14))

                # Right Column: Live Item Explanation Tooltip Card
                if 0 <= self.bag_index < len(items_list):
                    sel_name, sel_cnt, sel_data = items_list[self.bag_index]
                    tx, ty, tw, th = bx + 340, by + 10, bw - 360, bh - 20
                    
                    pygame.draw.rect(surf, (244, 247, 252), (tx, ty, tw, th), border_radius=8)
                    pygame.draw.rect(surf, (215, 225, 240), (tx, ty, tw, th), 1, border_radius=8)

                    # Icon & Name
                    sel_icon = gfx.get_item_sprite(sel_name, (36, 36))
                    surf.blit(sel_icon, (tx + 10, ty + 10))

                    name_lbl = gfx.fonts["regular"].render(sel_name, True, (30, 50, 90))
                    surf.blit(name_lbl, (tx + 52, ty + 8))

                    cat_lbl = gfx.fonts["small"].render(f"[{sel_data.get('category', 'item').upper()}]", True, (200, 80, 0))
                    surf.blit(cat_lbl, (tx + 52, ty + 28))

                    # Explanation Text
                    desc_words = sel_data.get("desc", "").split(" ")
                    lines, cur = [], ""
                    for w in desc_words:
                        t = cur + (" " if cur else "") + w
                        if gfx.fonts["small"].size(t)[0] < tw - 24:
                            cur = t
                        else:
                            lines.append(cur)
                            cur = w
                    if cur:
                        lines.append(cur)
                    for l_idx, l_str in enumerate(lines[:3]):
                        surf.blit(gfx.fonts["small"].render(l_str, True, UI_TEXT), (tx + 12, ty + 54 + l_idx * 20))

                    # Usage summary
                    usage_txt = sel_data.get("usage", "")
                    if usage_txt:
                        u_surf = gfx.fonts["small"].render(f"▶ {usage_txt[:50]}...", True, (40, 120, 200)) if len(usage_txt) > 50 else gfx.fonts["small"].render(f"▶ {usage_txt}", True, (40, 120, 200))
                        surf.blit(u_surf, (tx + 12, ty + th - 24))

        # Party Selection Sub-Menu
        elif self.phase in [BattlePhase.PARTY_SELECT, BattlePhase.FAINT_SWITCH]:
            title = gfx.fonts["medium"].render("Choose a Pokémon to switch:", True, UI_TEXT)
            surf.blit(title, (bx + 20, by + 15))
            
            self._adjust_party_scroll()
            visible_party = self.player_party[self.party_scroll : self.party_scroll + 4]
            for rel_idx, p in enumerate(visible_party):
                actual_idx = self.party_scroll + rel_idx
                iy = by + 50 + rel_idx * 28
                is_sel = (self.party_menu_index == actual_idx)
                marker = "> " if is_sel else "  "
                status_str = f"({p.status})" if p.status else ""
                col = (200, 80, 0) if is_sel else ((160, 160, 160) if p.is_fainted() else UI_TEXT)
                ptxt = gfx.fonts["regular"].render(f"{marker}{p.nickname} Lv.{p.level} - HP {p.current_hp}/{p.max_hp} {status_str}", True, col)
                surf.blit(ptxt, (bx + 20, iy))

            if len(self.player_party) > 4:
                scroll_info = gfx.fonts["small"].render(f"▲ ▼ ({self.party_menu_index + 1}/{len(self.player_party)})", True, (200, 80, 0))
                surf.blit(scroll_info, (bx + bw - scroll_info.get_width() - 25, by + 18))

    def _draw_level_up_modal(self, surf):
        mx, my, mw, mh = 250, 120, 300, 320
        pygame.draw.rect(surf, UI_BORDER_DARK, (mx - 2, my - 2, mw + 4, mh + 4), border_radius=10)
        pygame.draw.rect(surf, WHITE, (mx, my, mw, mh), border_radius=8)
        
        # Header
        head = gfx.fonts["medium"].render(f"{self.player_pokemon.nickname} grew to Lv. {self.player_pokemon.level}!", True, (220, 80, 0))
        surf.blit(head, (mx + (mw - head.get_width()) // 2, my + 20))
        
        # Stat Diff Table
        if self.current_stat_diffs:
            stats = [
                ("Max HP", self.player_pokemon.max_hp, self.current_stat_diffs.get("hp", 0)),
                ("Attack", self.player_pokemon.stats["atk"], self.current_stat_diffs.get("atk", 0)),
                ("Defense", self.player_pokemon.stats["def"], self.current_stat_diffs.get("def", 0)),
                ("Sp. Atk", self.player_pokemon.stats["spatk"], self.current_stat_diffs.get("spatk", 0)),
                ("Sp. Def", self.player_pokemon.stats["spdef"], self.current_stat_diffs.get("spdef", 0)),
                ("Speed", self.player_pokemon.stats["spd"], self.current_stat_diffs.get("spd", 0)),
            ]
            for idx, (lbl, val, diff) in enumerate(stats):
                sy = my + 65 + idx * 34
                ltxt = gfx.fonts["regular"].render(lbl, True, UI_TEXT)
                vtxt = gfx.fonts["regular"].render(f"{val} (+{diff})", True, (40, 140, 60))
                surf.blit(ltxt, (mx + 25, sy))
                surf.blit(vtxt, (mx + mw - vtxt.get_width() - 25, sy))
                
        prompt = gfx.fonts["small"].render("Press [Z / Enter] to continue", True, UI_TEXT_MUTED)
        surf.blit(prompt, (mx + (mw - prompt.get_width()) // 2, my + mh - 30))
