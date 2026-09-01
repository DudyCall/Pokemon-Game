"""
main.py - Main entry point and game loop for the Turn-Based Pokémon RPG.
"""
import sys
import random
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GameState, Direction,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_CONFIRM, KEY_CANCEL, KEY_MENU, KEY_QUICKSAVE
)
from graphics_manager import gfx
from sound_manager import sound_mgr
from pokemon_data import WILD_ENCOUNTERS, WILD_WATER_ENCOUNTERS, get_wild_encounters_for_prop, ITEMS
from pokemon import Pokemon
from inventory import Inventory
from world import World, Player
from battle_system import BattleSystem
from save_system import SaveSystem, Pokedex
from quest_system import QuestManager
from barrier_system import barrier_mgr
from ui_manager import (
    TitleScreen, StarterSelectScreen, TrainerCustomizationScreen, PauseMenu, PokedexScreen,
    PartySummaryScreen, ShopScreen, DialogueBox, SaveDialog, SaveSlotSelectScreen, PCBoxScreen,
    TrainerCardScreen, MoveRerollScreen, BagScreen, QuestLogScreen
)
from input_manager import InputManager

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pokémon - Pygame Edition")
        self.fullscreen = True
        self.screen = self._create_display()
        self.clock = pygame.time.Clock()
        self.running = True
        self.input_mgr = InputManager()
        
        # Game State
        self.state = GameState.TITLE
        self.current_save_slot = 1
        self.world = World()
        self.player = Player(x=8, y=6, current_map="Pallet Town")
        self.party = []
        self.pc_box = []
        self.inventory = Inventory()
        self.pokedex = Pokedex()
        self.quest_mgr = QuestManager()
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # UI Sub-screens
        self.title_screen = TitleScreen()
        self.starter_screen = StarterSelectScreen()
        self.trainer_customize_screen = TrainerCustomizationScreen()
        self.pc_box_screen = None
        self.save_slot_screen = None
        self.pause_menu = PauseMenu()
        self.save_dialog = None
        self.pokedex_screen = None
        self.party_screen = None
        self.trainer_card_screen = None
        self.shop_screen = None
        self.bag_screen = None
        self.move_reroll_screen = None
        self.quest_log_screen = None
        self.current_dialogue = None
        self.battle_system = None
        
        # Notifications / Overworld text
        self.notification_text = ""
        self.notification_timer = 0.0
        if self.input_mgr.connected:
            self.show_notification(f"Controller connected: {self.input_mgr.joystick.get_name()}")

    def _create_display(self):
        flags = pygame.SCALED
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.screen = self._create_display()

    def show_notification(self, text, duration=2.5):
        self.notification_text = text
        self.notification_timer = duration

    def start_new_game(self, custom_data):
        if isinstance(custom_data, str):
            starter_species = custom_data
            t_name, t_gender, t_outfit, t_hat, t_hair = "Red", "Boy", "Classic Red", "Trainer Cap", "Dark Brown"
        else:
            starter_species = custom_data.get("starter_species", "Charmander")
            t_name = custom_data.get("name", "Red")
            t_gender = custom_data.get("gender", "Boy")
            t_outfit = custom_data.get("outfit_theme", "Classic Red")
            t_hat = custom_data.get("hat_style", "Trainer Cap")
            t_hair = custom_data.get("hair_color", "Dark Brown")

        starter = Pokemon(starter_species, level=5)
        self.party = [starter]
        self.pc_box = []
        self.pokedex = Pokedex()
        self.pokedex.register_caught(starter_species)
        self.world = World()
        self.player = Player(
            x=8, y=6, current_map="Pallet Town",
            name=t_name, gender=t_gender, outfit_theme=t_outfit, hat_style=t_hat, hair_color=t_hair
        )
        if self.player.follower:
            self.player.follower.sync_with_party(self.party)
            self.player.follower.teleport_to_player(self.player)
        self.inventory = Inventory()
        self.quest_mgr = QuestManager()
        self.world.reveal_area(self.player.current_map, self.player.grid_x, self.player.grid_y)
        self.state = GameState.OVERWORLD
        sound_mgr.play_bgm("town")
        # Save initial game state to selected slot
        SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world, slot=self.current_save_slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr)
        self.show_notification(f"Welcome, {self.player.name}! Received {starter_species}!")

    def start_wild_battle(self, encounter_zone, is_water=False, prop_type=None):
        table = get_wild_encounters_for_prop(encounter_zone, prop_type, is_water=is_water)
        if not table:
            return
            
        total_weight = sum(item["weight"] for item in table)
        r = random.randint(1, total_weight)
        cum = 0
        chosen_entry = table[0]
        for item in table:
            cum += item["weight"]
            if r <= cum:
                chosen_entry = item
                break
                
        lvl = random.randint(chosen_entry["min_lvl"], chosen_entry["max_lvl"])
        wild_pkmn = Pokemon(chosen_entry["species"], level=lvl)
        
        sound_mgr.play_sfx("wild_encounter")
        self.battle_system = BattleSystem(
            player_party=self.party,
            opponent_pokemon_or_trainer=wild_pkmn,
            is_trainer=False,
            inventory=self.inventory,
            pokedex=self.pokedex,
            pc_box=self.pc_box,
            quest_mgr=self.quest_mgr
        )
        self.state = GameState.BATTLE


    def start_trainer_battle(self, trainer_data):
        sound_mgr.play_sfx("wild_encounter")
        self.battle_system = BattleSystem(
            player_party=self.party,
            opponent_pokemon_or_trainer=trainer_data,
            is_trainer=True,
            inventory=self.inventory,
            pokedex=self.pokedex,
            pc_box=self.pc_box,
            quest_mgr=self.quest_mgr
        )
        self.state = GameState.BATTLE

    def handle_input(self, dt):
        raw_events = list(pygame.event.get())
        extra, notices = self.input_mgr.process(raw_events, dt)
        for msg in notices:
            self.show_notification(msg)
        for event in raw_events + extra:
            if event.type == pygame.QUIT:
                if self.state != GameState.TITLE and hasattr(self, 'player') and hasattr(self, 'quest_mgr'):
                    SaveSystem.save_game(
                        self.player, self.party, self.inventory, self.pokedex, self.world,
                        slot=self.current_save_slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr
                    )
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                alt_enter = event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT)
                if event.key == pygame.K_F11 or alt_enter:
                    self._toggle_fullscreen()
                    continue

            # Title State
            if self.state == GameState.TITLE:
                action_data = self.title_screen.handle_input(event)
                if action_data:
                    if isinstance(action_data, tuple):
                        opt, chosen_slot = action_data
                    else:
                        opt, chosen_slot = action_data, 1

                    if opt == "LOAD_SLOT":
                        self.current_save_slot = chosen_slot
                        res, msg = SaveSystem.load_game(self.player, self.world, slot=chosen_slot)
                        if res:
                            if len(res) >= 5:
                                self.party, self.inventory, self.pokedex, self.pc_box, q_data = res[:5]
                                self.quest_mgr = QuestManager.from_dict(q_data)
                            elif len(res) == 4:
                                self.party, self.inventory, self.pokedex, self.pc_box = res
                                self.quest_mgr = QuestManager()
                            else:
                                self.party, self.inventory, self.pokedex = res[:3]
                                self.pc_box = []
                                self.quest_mgr = QuestManager()
                            if self.player.follower:
                                self.player.follower.sync_with_party(self.party)
                                self.player.follower.teleport_to_player(self.player)
                            self.state = GameState.OVERWORLD
                            sound_mgr.play_bgm("town")
                            self.show_notification(f"Slot {chosen_slot} loaded successfully!")
                        else:
                            self.save_slot_screen = SaveSlotSelectScreen(mode="LOAD", active_slot=chosen_slot)
                            self.state = GameState.SAVE_SLOTS
                    elif opt in ["SELECT_SLOT", "ALL_SLOTS", "CONTINUE"]:
                        self.save_slot_screen = SaveSlotSelectScreen(mode="LOAD", active_slot=chosen_slot)
                        self.state = GameState.SAVE_SLOTS
                    elif opt in ["NEW_GAME", "NEW GAME"]:
                        self.save_slot_screen = SaveSlotSelectScreen(mode="NEW_GAME", active_slot=chosen_slot)
                        self.state = GameState.SAVE_SLOTS
                continue

            # Save Slots Selection State
            if self.state == GameState.SAVE_SLOTS:
                if self.save_slot_screen:
                    action_data = self.save_slot_screen.handle_input(event)
                    if action_data:
                        action, chosen_slot = action_data
                        if action == "LOAD":
                            self.current_save_slot = chosen_slot
                            res, msg = SaveSystem.load_game(self.player, self.world, slot=chosen_slot)
                            if res:
                                if len(res) >= 5:
                                    self.party, self.inventory, self.pokedex, self.pc_box, q_data = res[:5]
                                    self.quest_mgr = QuestManager.from_dict(q_data)
                                elif len(res) == 4:
                                    self.party, self.inventory, self.pokedex, self.pc_box = res
                                    self.quest_mgr = QuestManager()
                                else:
                                    self.party, self.inventory, self.pokedex = res[:3]
                                    self.pc_box = []
                                    self.quest_mgr = QuestManager()
                                if self.player.follower:
                                    self.player.follower.sync_with_party(self.party)
                                    self.player.follower.teleport_to_player(self.player)
                                self.save_slot_screen = None
                                self.state = GameState.OVERWORLD
                                sound_mgr.play_bgm("town")
                                self.show_notification(f"Slot {chosen_slot} loaded successfully!")
                            else:
                                self.show_notification("Failed to load save file.")
                        elif action == "NEW_GAME":
                            self.current_save_slot = chosen_slot
                            self.save_slot_screen = None
                            self.trainer_customize_screen = TrainerCustomizationScreen()
                            self.state = GameState.TRAINER_CUSTOMIZE
                        elif action == "SAVED":
                            self.current_save_slot = chosen_slot
                            self.save_slot_screen = None
                            self.state = GameState.OVERWORLD
                            self.show_notification(f"Game saved to Slot {chosen_slot}!")
                        elif action == "CANCEL":
                            self.save_slot_screen = None
                            if self.party: # In-game
                                self.state = GameState.OVERWORLD
                            else: # Title
                                self.title_screen.refresh_save_status()
                                self.state = GameState.TITLE
                continue

            # Trainer Customization State
            if self.state == GameState.TRAINER_CUSTOMIZE:
                custom_result = self.trainer_customize_screen.handle_input(event)
                if isinstance(custom_result, dict):
                    self.start_new_game(custom_result)
                elif custom_result == "CANCEL":
                    self.save_slot_screen = SaveSlotSelectScreen(mode="NEW_GAME", active_slot=self.current_save_slot)
                    self.state = GameState.SAVE_SLOTS
                continue

            # Starter Select State
            if self.state == GameState.STARTER_SELECT:
                choice = self.starter_screen.handle_input(event)
                if choice:
                    self.start_new_game(choice)
                continue

            # Overworld State
            if self.state == GameState.OVERWORLD:
                if event.type == pygame.KEYDOWN:
                    # Quick Save (F5 or K)
                    if any(event.key == k for k in KEY_QUICKSAVE):
                        ok, msg = SaveSystem.save_game(
                            self.player, self.party, self.inventory, self.pokedex, self.world,
                            slot=self.current_save_slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr
                        )
                        sound_mgr.play_sfx("confirm" if ok else "cancel")
                        self.show_notification(f"Quick-Saved to Slot {self.current_save_slot}!")
                        continue

                    # Open Pause Menu
                    if any(event.key == k for k in KEY_MENU):
                        sound_mgr.play_sfx("select")
                        self.state = GameState.PARTY_MENU
                        self.pause_menu.selected_idx = 0
                        continue
                        
                    # Interaction Key (Talk to NPC / Check Sign / Enter)
                    if any(event.key == k for k in KEY_CONFIRM):
                        self._handle_overworld_interaction()
                continue

            # Pause Menu State
            if self.state == GameState.PARTY_MENU:
                action = self.pause_menu.handle_input(event)
                if action == "EXIT":
                    self.state = GameState.OVERWORLD
                elif action == "POKÉDEX":
                    self.pokedex_screen = PokedexScreen(self.pokedex)
                    self.state = GameState.POKEDEX
                elif action == "POKÉMON":
                    self.party_screen = PartySummaryScreen(self.party, self.inventory)
                    self.trainer_card_screen = None
                    self.state = GameState.TRAINER_CARD
                elif action == "BAG":
                    self.bag_screen = BagScreen(self.party, self.inventory, self.quest_mgr)
                    self.state = GameState.BAG_MENU
                elif action in ["QUESTS", "QUEST LOG", "MISSIONS"]:
                    self.quest_log_screen = QuestLogScreen(self.quest_mgr, self.player)
                    self.state = GameState.QUEST_LOG
                elif action in ["MAP", "TOWN MAP"]:
                    self.party_screen = None
                    self.trainer_card_screen = TrainerCardScreen(self.player, self.world, self.inventory, self.pokedex, initial_tab=1)
                    self.state = GameState.TRAINER_CARD
                elif action in ["TRAINER", "TRAINER CARD"]:
                    self.party_screen = None
                    self.trainer_card_screen = TrainerCardScreen(self.player, self.world, self.inventory, self.pokedex, initial_tab=0)
                    self.state = GameState.TRAINER_CARD
                elif action == "PC BOX":
                    self.pc_box_screen = PCBoxScreen(self.party, self.pc_box, inventory=self.inventory)
                    self.state = GameState.PC_BOX
                elif action == "SAVE":
                    self.save_slot_screen = SaveSlotSelectScreen(
                        mode="SAVE",
                        active_slot=self.current_save_slot,
                        player=self.player,
                        party=self.party,
                        inventory=self.inventory,
                        pokedex=self.pokedex,
                        world=self.world,
                        pc_box=self.pc_box,
                        quest_mgr=self.quest_mgr
                    )
                    self.state = GameState.SAVE_SLOTS
                continue

            # Quest Log View State
            if self.state == GameState.QUEST_LOG:
                if self.quest_log_screen:
                    res = self.quest_log_screen.handle_input(event)
                    if res == "CLOSE":
                        self.quest_log_screen = None
                        self.state = GameState.OVERWORLD
                continue

            # PC Box State
            if self.state == GameState.PC_BOX:
                if self.pc_box_screen:
                    res = self.pc_box_screen.handle_input(event)
                    if res == "EXIT":
                        self.pc_box_screen = None
                        self.state = GameState.OVERWORLD
                continue

            # Save Dialog State
            if self.state == GameState.SAVE:
                if self.save_dialog:
                    res = self.save_dialog.handle_input(event)
                    if res in ["DONE", "CANCEL"]:
                        self.save_dialog = None
                        self.state = GameState.OVERWORLD
                        if res == "DONE":
                            self.show_notification("Game saved successfully!")
                continue

            # Pokédex View State
            if self.state == GameState.POKEDEX:
                if self.pokedex_screen:
                    res = self.pokedex_screen.handle_input(event)
                    if res == "BACK":
                        self.state = GameState.OVERWORLD
                continue

            # Party / Trainer Card / Town Map View State
            if self.state == GameState.TRAINER_CARD:
                if self.trainer_card_screen:
                    res = self.trainer_card_screen.handle_input(event)
                    if res == "BACK":
                        self.trainer_card_screen = None
                        self.state = GameState.OVERWORLD
                elif self.party_screen:
                    res = self.party_screen.handle_input(event)
                    if res == "BACK":
                        self.party_screen = None
                        self.state = GameState.OVERWORLD
                continue

            # Bag View State
            if self.state == GameState.BAG_MENU:
                if self.bag_screen:
                    res = self.bag_screen.handle_input(event)
                    if res == "EXIT":
                        self.bag_screen = None
                        self.state = GameState.OVERWORLD
                continue

            # Shop View State
            if self.state == GameState.SHOP:
                if self.shop_screen:
                    res = self.shop_screen.handle_input(event)
                    if res == "EXIT":
                        self.state = GameState.OVERWORLD
                continue

            # Move Reroll & Tutor State
            if self.state == GameState.MOVE_RELEARN:
                if self.move_reroll_screen:
                    res = self.move_reroll_screen.handle_input(event)
                    if res == "EXIT":
                        self.state = GameState.OVERWORLD
                continue

            # Dialogue State
            if self.state == GameState.DIALOGUE:
                if self.current_dialogue:
                    done = self.current_dialogue.handle_input(event)
                    if done:
                        self.current_dialogue = None
                        if self.state == GameState.DIALOGUE:
                            self.state = GameState.OVERWORLD
                continue

            # Battle State
            if self.state == GameState.BATTLE:
                if self.battle_system:
                    self.battle_system.handle_input(event)
                continue

    def _generate_partner_dialogue(self, partner):
        name = partner.nickname or partner.species
        hp_ratio = partner.current_hp / max(1, partner.max_hp)
        
        phrases = []
        if partner.status in ["Poison", "Poisoned", "Toxic"]:
            phrases.append(f"{name} is shivering from the poison, looking to you for care and comfort!")
        elif partner.status in ["Paralyze", "Paralysis"]:
            phrases.append(f"{name} has tiny sparks crackling and is trying its best to keep up!")
        elif partner.status in ["Burn", "Burned"]:
            phrases.append(f"{name} is wincing from its burn, but staying bravely by your side!")
        elif partner.status in ["Sleep", "Asleep"]:
            phrases.append(f"{name} is nodding off sleepily, walking in its sleep with you! zzz")
        elif hp_ratio <= 0.3:
            phrases.append(f"{name} is breathing heavily and tired from battle, but determined to keep going!")
            phrases.append(f"{name} leaned gently against your leg to rest for a moment.")
        elif self.player.is_sailing:
            phrases.append(f"{name} is splashing excitedly in the cool water! ♪")
            phrases.append(f"{name} looked over the side of the boat and let out a cheerful cry! ♥")
        elif "Cave" in self.player.current_map or "Moon" in self.player.current_map or "Tunnel" in self.player.current_map:
            phrases.append(f"{name} is listening closely to the mysterious echoes in the dark cave!")
            phrases.append(f"{name} stayed extra close to you, keeping watch on the shadows.")
        elif "Gym" in self.player.current_map:
            phrases.append(f"{name} is staring intensely ahead, full of fiery fighting spirit for the Gym challenge!")
        elif "Tower" in self.player.current_map:
            phrases.append(f"{name} felt a chilly ghostly breeze and snuggled closer to you.")
        else:
            phrases.append(f"{name} looked up at you with happy, sparkling eyes! ♥")
            phrases.append(f"{name} is happily skipping along, matching your footsteps!")
            phrases.append(f"{name} nudged your hand affectionately! It loves traveling with you.")
            phrases.append(f"{name} is scanning the surroundings with great focus, ready for any battle!")

        selected_phrase = random.choice(phrases)
        status_info = f"\n\n[Partner: Lv.{partner.level} {partner.species} | HP: {partner.current_hp}/{partner.max_hp} | Friendship: ♥♥♥♥♥]"
        return selected_phrase + status_info

    def _handle_overworld_interaction(self):
        # Determine facing tile coordinate
        fx, fy = self.player.grid_x, self.player.grid_y
        if self.player.facing == Direction.UP:
            fy -= 1
        elif self.player.facing == Direction.DOWN:
            fy += 1
        elif self.player.facing == Direction.LEFT:
            fx -= 1
        elif self.player.facing == Direction.RIGHT:
            fx += 1

        # 0. Check Following Partner Pokémon interaction
        if self.player.follower and self.player.follower.current_pokemon:
            f_x = self.player.follower.grid_x
            f_y = self.player.follower.grid_y
            if (fx, fy) == (f_x, f_y) or (self.player.grid_x, self.player.grid_y) == (f_x, f_y):
                partner = self.player.follower.current_pokemon
                sound_mgr.play_sfx("confirm")
                self.player.follower.trigger_emote("heart", duration=3.0)
                dialog_text = self._generate_partner_dialogue(partner)
                self.current_dialogue = DialogueBox(
                    partner.nickname or partner.species,
                    dialog_text,
                    on_complete=None,
                    portrait_key=partner.species
                )
                self.state = GameState.DIALOGUE
                return

        # 1. Check Ground Collectible Item (at player tile or facing tile)
        g_item = self.world.get_ground_item_at(self.player.current_map, self.player.grid_x, self.player.grid_y) or self.world.get_ground_item_at(self.player.current_map, fx, fy)
        if g_item:
            item_id = g_item["id"]
            item_name = g_item["item"]
            item_cnt = g_item.get("count", 1)
            self.world.collected_items.add(item_id)
            self.inventory.add_item(item_name, item_cnt)
            sound_mgr.play_sfx("confirm")
            self.show_notification(f"Found {item_cnt}x {item_name}!")
            SaveSystem.save_game(
                self.player, self.party, self.inventory, self.pokedex, self.world,
                slot=self.current_save_slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr
            )
            item_desc = ITEMS.get(item_name, {}).get("desc", "")
            pickup_text = f"{self.player.name} found {item_cnt}x {item_name} and put it in the Bag!\n\n{item_desc}" if item_desc else f"{self.player.name} found {item_cnt}x {item_name} and put it in the Bag!"
            self.current_dialogue = DialogueBox("Item Found", pickup_text, on_complete=None, portrait_key="item")
            self.state = GameState.DIALOGUE
            return

        # 2. Check Sign at facing tile
        sign_msg = self.world.get_sign_at(self.player.current_map, fx, fy)
        if sign_msg:
            sound_mgr.play_sfx("confirm")
            self.current_dialogue = DialogueBox("Notice", sign_msg, on_complete=None, portrait_key="sign")
            self.state = GameState.DIALOGUE
            return

        # 3. Check PC Terminal tile or interaction in Pokecenter
        if self.player.current_map == "Pokecenter" and fx == 8 and fy in [4, 5]:
            sound_mgr.play_sfx("confirm")
            self.pc_box_screen = PCBoxScreen(self.party, self.pc_box, inventory=self.inventory)
            self.state = GameState.PC_BOX
            return

        # 4. Check Progression Barriers & Roadblocks
        b_data = barrier_mgr.get_barrier_at(self.player.current_map, fx, fy, self.world.unlocked_barriers)
        if b_data:
            b_id = b_data["id"]
            is_met, prog = barrier_mgr.evaluate_condition(
                b_id, self.player, self.party, self.world, self.quest_mgr, self.pokedex, self.inventory
            )
            if is_met:
                self.world.unlocked_barriers.add(b_id)
                sound_mgr.play_sfx("confirm")
                self.show_notification(f"Cleared: {b_data['name']}!")
                SaveSystem.save_game(
                    self.player, self.party, self.inventory, self.pokedex, self.world,
                    slot=self.current_save_slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr
                )
                self.current_dialogue = DialogueBox(
                    b_data["cleared_title"],
                    b_data["cleared_message"],
                    on_complete=None,
                    portrait_key=b_data.get("name")
                )
            else:
                sound_mgr.play_sfx("select")
                blocked_full = f"{b_data['blocked_message']}\n\nRequirements Status:\n{prog}"
                self.current_dialogue = DialogueBox(
                    b_data["blocked_title"],
                    blocked_full,
                    on_complete=None,
                    portrait_key=b_data.get("name")
                )
            self.state = GameState.DIALOGUE
            return

        # 5. Check NPC
        npc = self.world.get_npc_at(self.player.current_map, fx, fy)
        if npc:
            sound_mgr.play_sfx("confirm")
            if npc.get("is_pc"):
                self.pc_box_screen = PCBoxScreen(self.party, self.pc_box, inventory=self.inventory)
                self.state = GameState.PC_BOX
            elif npc.get("is_healer"):
                # Nurse Joy / Mom Healer
                for p in self.party:
                    p.full_restore()
                # Auto-save
                SaveSystem.save_game(
                    self.player, self.party, self.inventory, self.pokedex, self.world,
                    slot=self.current_save_slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr
                )
                sound_mgr.play_sfx("heal")
                healer_name = npc.get("name", "Nurse Joy")
                self.current_dialogue = DialogueBox(
                    healer_name,
                    f"Your Pokémon are fully healed and your progress was saved to Slot {self.current_save_slot}!",
                    on_complete=None,
                    portrait_key=healer_name
                )
                self.state = GameState.DIALOGUE
            elif npc.get("is_shop"):
                # Open Mart
                self.shop_screen = ShopScreen(self.inventory)
                self.state = GameState.SHOP
            elif npc.get("is_oak"):
                # Prof. Oak Pokédex Evaluation
                seen_n = len(self.pokedex.seen)
                caught_n = len(self.pokedex.caught)
                if caught_n >= 20:
                    eval_msg = f"Astounding, {self.player.name}! You have caught {caught_n} species! You are well on your way to becoming a Pokémon Master!"
                elif caught_n >= 6:
                    eval_msg = f"Great work, {self.player.name}! You have caught {caught_n} species and seen {seen_n}. Keep exploring new routes and caves!"
                else:
                    eval_msg = f"You have caught {caught_n} species and seen {seen_n}. Make sure to explore all routes, caves, and waters to find wild Pokémon!"
                self.current_dialogue = DialogueBox("Prof. Oak", eval_msg, on_complete=None, portrait_key="Prof. Oak")
                self.state = GameState.DIALOGUE
            elif npc.get("is_bill"):
                # Bill Gift (Eevee)
                if "bill_eevee_gift" not in self.world.collected_items:
                    self.world.collected_items.add("bill_eevee_gift")
                    eevee = Pokemon("Eevee", level=15)
                    if len(self.party) < 6:
                        self.party.append(eevee)
                        dest = "your party"
                    else:
                        self.pc_box.append(eevee)
                        dest = "your PC Storage Box"
                    self.pokedex.register_caught("Eevee")
                    SaveSystem.save_game(
                        self.player, self.party, self.inventory, self.pokedex, self.world,
                        slot=self.current_save_slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr
                    )
                    self.current_dialogue = DialogueBox("Bill", f"Thanks for visiting my Sea Cottage! Take this rare Eevee! It was sent to {dest}!", on_complete=None, portrait_key="Bill")
                else:
                    self.current_dialogue = DialogueBox("Bill", "Eevee has many wonderful evolutions with elemental stones! Take good care of it!", on_complete=None, portrait_key="Bill")
                self.state = GameState.DIALOGUE
            elif npc.get("is_move_tutor") or npc.get("name") == "Move Master":
                # Open Move Reroll & Tutor Screen ($3,000)
                self.move_reroll_screen = MoveRerollScreen(self.party, self.inventory)
                self.state = GameState.MOVE_RELEARN
            elif npc.get("quest_id"):
                from quest_system import QUEST_DEFINITIONS
                q_id = npc["quest_id"]
                q_def = QUEST_DEFINITIONS.get(q_id, {})
                q_name = q_def.get("title", "Mission")
                giver_name = npc.get("name", "Quest Giver")

                if self.quest_mgr.is_completed(q_id):
                    d_text = f"Outstanding job on '{q_name}'!\n\nThank you so much for your help, {self.player.name}!"
                elif self.quest_mgr.is_active(q_id):
                    curr_p = self.quest_mgr.get_progress(q_id)
                    tgt_p = q_def.get("target_count", 1)
                    d_text = f"Mission in Progress: '{q_name}'\n\n{q_def.get('description', '')}\n\nCurrent Progress: {curr_p} / {tgt_p}\n\n⭐ Rewards deliver automatically the moment you finish!"
                else:
                    # Accept quest!
                    self.quest_mgr.accept_quest(q_id)
                    self.show_notification(f"Quest Accepted: {q_name}!")
                    sound_mgr.play_sfx("confirm")
                    SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world, slot=self.current_save_slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr)
                    d_text = f"QUEST ACCEPTED: '{q_name}'!\n\n{npc.get('dialog', '')}\n\n⭐ Auto-Turn-In: Rewards will be delivered directly to your Bag the instant objectives are met!"

                self.current_dialogue = DialogueBox(giver_name, d_text, on_complete=None, portrait_key=giver_name)
                self.state = GameState.DIALOGUE
            else:
                self.current_dialogue = DialogueBox(npc.get("name", "NPC"), npc.get("dialog", "Hello!"), on_complete=None, portrait_key=npc.get("name"))
                self.state = GameState.DIALOGUE
            return

        # 5. Check Trainer talk
        trainer = self.world.get_any_trainer_at(self.player.current_map, fx, fy)
        if trainer:
            sound_mgr.play_sfx("confirm")
            if trainer["id"] in self.world.defeated_trainers:
                # Already defeated -> talk with portrait
                self.current_dialogue = DialogueBox(
                    trainer["name"],
                    trainer.get("dialog_after", "Good battle!"),
                    on_complete=None,
                    portrait_key=trainer.get("id"),
                    trainer_data=trainer
                )
                self.state = GameState.DIALOGUE
            else:
                # Undefeated -> talk before battle with portrait, then start battle on confirm
                dialog_text = trainer.get("dialog_before", "Let's battle!")
                self.current_dialogue = DialogueBox(
                    trainer["name"],
                    dialog_text,
                    on_complete=lambda t=trainer: self.start_trainer_battle(t),
                    portrait_key=trainer.get("id"),
                    trainer_data=trainer
                )
                self.state = GameState.DIALOGUE
            return


        # 6. Check Door / Warp interaction directly in front of player
        warp = self.world.get_warp_target(self.player.current_map, fx, fy)
        if warp:
            self.execute_warp(warp)
            return

    def execute_warp(self, warp):
        sound_mgr.play_sfx("confirm")
        target_map = warp["target_map"]
        target_x = warp["target_x"]
        target_y = warp["target_y"]
        
        interiors = ["Pokecenter", "Mart", "Oak's Lab", "Player's House", "Pewter Gym", "Cerulean Gym", "Bill's Cottage", "Museum"]
        # If entering interior, record origin
        if target_map in interiors and self.player.current_map not in interiors:
            self.world.interior_origin_map = self.player.current_map
            self.world.interior_origin_coords = (self.player.grid_x, self.player.grid_y)
        # If exiting interior, return to recorded origin or fallback
        elif target_map not in interiors and self.player.current_map in interiors:
            target_map = getattr(self.world, "interior_origin_map", target_map)
            coords = getattr(self.world, "interior_origin_coords", (target_x, target_y))
            target_x, target_y = coords
            target_y += 1 # step 1 tile down outside the door

        self.player.current_map = target_map
        self.player.grid_x = target_x
        self.player.grid_y = target_y
        self.player.pixel_x = target_x * 32
        self.player.pixel_y = target_y * 32
        self.player.is_moving = False
        self.player.move_progress = 0.0
        if self.player.follower:
            self.player.follower.teleport_to_player(self.player)
        self.world.reveal_area(self.player.current_map, self.player.grid_x, self.player.grid_y)


    def update(self, dt):
        self.world.update(dt)
        # Update notification timer
        if self.notification_timer > 0:
            self.notification_timer = max(0.0, self.notification_timer - dt)

        # Title State update
        if self.state == GameState.TITLE:
            self.title_screen.update(dt)

        # Save Dialog State update
        elif self.state == GameState.SAVE:
            if self.save_dialog:
                auto_res = self.save_dialog.update(dt, self.world)
                if auto_res == "DONE":
                    self.save_dialog = None
                    self.state = GameState.OVERWORLD
                    self.show_notification("Game saved successfully!")

        # Overworld & Sub-Menus update
        elif self.state in [GameState.OVERWORLD, GameState.PARTY_MENU]:
            # Sync following partner Pokemon with active party leader
            if self.player.follower:
                self.player.follower.sync_with_party(self.party)

            # Continuous grid movement
            if not self.player.is_moving and self.state == GameState.OVERWORLD:
                keys = pygame.key.get_pressed()
                pad = self.input_mgr.get_held_directions()
                if any(keys[k] for k in KEY_UP) or Direction.UP in pad:
                    self.player.move(Direction.UP, self.world)
                elif any(keys[k] for k in KEY_DOWN) or Direction.DOWN in pad:
                    self.player.move(Direction.DOWN, self.world)
                elif any(keys[k] for k in KEY_LEFT) or Direction.LEFT in pad:
                    self.player.move(Direction.LEFT, self.world)
                elif any(keys[k] for k in KEY_RIGHT) or Direction.RIGHT in pad:
                    self.player.move(Direction.RIGHT, self.world)

            was_moving = self.player.is_moving
            self.player.update(dt, self.world)
            
            # If player just finished a step
            if was_moving and not self.player.is_moving:
                # 1. Check Warp Gate / Door
                warp = self.world.get_warp_target(self.player.current_map, self.player.grid_x, self.player.grid_y)
                if warp:
                    self.execute_warp(warp)
                    return
                    
                # 2. Check Wild Encounter
                # A: Walk-Through Prop Wild Encounter (14% chance per step)
                if self.player.current_prop or self.player.in_tall_grass:
                    zone = self.world.maps[self.player.current_map].get("encounter_zone")
                    if zone and random.random() < 0.14:
                        self.start_wild_battle(zone, is_water=False, prop_type=self.player.current_prop)
                        return
                        
                # B: Water Sailing Wild Encounter (14% chance per step on water)
                if self.player.is_sailing:
                    zone = self.world.maps[self.player.current_map].get("encounter_zone")
                    if zone and random.random() < 0.14:
                        self.start_wild_battle(zone, is_water=True)
                        return

                        
                # 3. Check Trainer Line of Sight
                spotted_trainer = self.world.check_trainer_line_of_sight(self.player.current_map, self.player.grid_x, self.player.grid_y)
                if spotted_trainer:
                    sound_mgr.play_sfx("confirm")
                    dialog_text = spotted_trainer.get("dialog_before", "Let's battle!")
                    self.current_dialogue = DialogueBox(
                        spotted_trainer["name"],
                        dialog_text,
                        on_complete=lambda t=spotted_trainer: self.start_trainer_battle(t),
                        portrait_key=spotted_trainer.get("id"),
                        trainer_data=spotted_trainer
                    )
                    self.state = GameState.DIALOGUE
                    return


            # Smooth Camera Tracking centered on player
            map_w, map_h = self.world.get_map_dimensions(self.player.current_map)
            target_cam_x = self.player.pixel_x + 16 - SCREEN_WIDTH // 2
            target_cam_y = self.player.pixel_y + 16 - SCREEN_HEIGHT // 2
            
            # Clamp camera to map bounds
            self.camera_x = max(0, min(map_w - SCREEN_WIDTH, target_cam_x)) if map_w > SCREEN_WIDTH else (map_w - SCREEN_WIDTH) // 2
            self.camera_y = max(0, min(map_h - SCREEN_HEIGHT, target_cam_y)) if map_h > SCREEN_HEIGHT else (map_h - SCREEN_HEIGHT) // 2

        # Check Quest Notifications
        if self.quest_mgr:
            for notif in self.quest_mgr.pop_notifications():
                sound_mgr.play_sfx("level_up")
                self.show_notification(notif, duration=4.5)
                # Auto save on quest completion
                SaveSystem.save_game(
                    self.player, self.party, self.inventory, self.pokedex, self.world,
                    slot=self.current_save_slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr
                )

        # Save Slot Select Screen State update
        if self.state == GameState.SAVE_SLOTS and self.save_slot_screen:
            self.save_slot_screen.update(dt)

        # Trainer Customization State update
        elif self.state == GameState.TRAINER_CUSTOMIZE and self.trainer_customize_screen:
            self.trainer_customize_screen.update(dt)

        # PC Box State update
        elif self.state == GameState.PC_BOX and self.pc_box_screen:
            self.pc_box_screen.update(dt)

        # Move Reroll & Tutor State update
        elif self.state == GameState.MOVE_RELEARN and self.move_reroll_screen:
            self.move_reroll_screen.update(dt)

        # Bag Inventory State update
        elif self.state == GameState.BAG_MENU and self.bag_screen:
            self.bag_screen.update(dt)

        # Quest Log State update
        elif self.state == GameState.QUEST_LOG and self.quest_log_screen:
            self.quest_log_screen.update(dt)

        # Dialogue State update
        elif self.state == GameState.DIALOGUE:
            if self.current_dialogue:
                self.current_dialogue.update(dt)

        # Trainer Card / Region Map update
        elif self.state == GameState.TRAINER_CARD:
            if self.trainer_card_screen:
                self.trainer_card_screen.update(dt)

        # Battle State update
        elif self.state == GameState.BATTLE:
            if self.battle_system:
                self.battle_system.update(dt)
                
                # Check Battle Completion
                if self.battle_system.phase == "FINISHED":
                    if self.battle_system.is_trainer:
                        t_data = self.battle_system.trainer_data or {}
                        t_id = t_data.get("id")
                        if t_id:
                            self.world.defeated_trainers.add(t_id)
                        # Award Gym Badge if victorious against a gym leader
                        badge_name = t_data.get("reward_badge")
                        if badge_name:
                            self.world.badges.add(badge_name)
                            self.show_notification(f"Earned the {badge_name}!")
                    # Save game progress immediately so defeated trainers, catches, EXP, and quest progress stay saved
                    SaveSystem.save_game(
                        self.player, self.party, self.inventory, self.pokedex, self.world,
                        slot=self.current_save_slot, pc_box=self.pc_box, quest_mgr=self.quest_mgr
                    )
                    self.battle_system = None
                    self.state = GameState.OVERWORLD
                    sound_mgr.play_bgm("town")
                elif self.battle_system.phase == "BLACKOUT":
                    # Respawn at Pokemon Center fully healed
                    for p in self.party:
                        p.full_restore()
                    self.player.current_map = "Pokecenter"
                    self.player.grid_x = 6
                    self.player.grid_y = 6
                    self.player.pixel_x = 6 * 32
                    self.player.pixel_y = 6 * 32
                    self.battle_system = None
                    self.state = GameState.OVERWORLD
                    sound_mgr.play_bgm("town")
                    self.show_notification("Your team was fully restored at the Pokémon Center.")

    def draw(self):
        # 1. Title State
        if self.state == GameState.TITLE:
            self.title_screen.draw(self.screen)

        # 2. Trainer Customization State
        elif self.state == GameState.TRAINER_CUSTOMIZE and self.trainer_customize_screen:
            self.trainer_customize_screen.draw(self.screen)

        # 3. PC Box Storage Screen
        elif self.state == GameState.PC_BOX and self.pc_box_screen:
            self.pc_box_screen.draw(self.screen)

        # 4. Starter Select State (Fallback)
        elif self.state == GameState.STARTER_SELECT:
            self.starter_screen.draw(self.screen)

        # 5. Save Slots Screen State
        elif self.state == GameState.SAVE_SLOTS and self.save_slot_screen:
            self.save_slot_screen.draw(self.screen)

        # 6. Overworld & Sub-Menus & Save
        elif self.state in [GameState.OVERWORLD, GameState.PARTY_MENU, GameState.DIALOGUE, GameState.SAVE]:
            self.world.draw(self.screen, self.player.current_map, self.camera_x, self.camera_y, quest_mgr=self.quest_mgr)
            self.player.draw(self.screen, self.camera_x, self.camera_y)
            
            # Interactive Fog-of-War Minimap in the upper-left corner
            self.world.draw_minimap(self.screen, self.player.current_map, self.player.grid_x, self.player.grid_y)

            # Dialogue Box Overlay
            if self.state == GameState.DIALOGUE and self.current_dialogue:
                self.current_dialogue.draw(self.screen)

            # Pause Menu Overlay
            if self.state == GameState.PARTY_MENU:
                self.pause_menu.draw(self.screen)

            # Save Dialog Overlay
            if self.state == GameState.SAVE and self.save_dialog:
                self.save_dialog.draw(self.screen)

        # 7. Pokédex Screen
        elif self.state == GameState.POKEDEX and self.pokedex_screen:
            self.pokedex_screen.draw(self.screen)

        # 8. Party Summary / Trainer Card / Region Map Screen
        elif self.state == GameState.TRAINER_CARD:
            if self.trainer_card_screen:
                self.trainer_card_screen.draw(self.screen)
            elif self.party_screen:
                self.party_screen.draw(self.screen)

        # 9. Bag Inventory & Item Manual Screen
        elif self.state == GameState.BAG_MENU and self.bag_screen:
            self.bag_screen.draw(self.screen)

        # 10. Quest Log Screen
        elif self.state == GameState.QUEST_LOG and self.quest_log_screen:
            self.quest_log_screen.draw(self.screen)

        # 11. Shop Screen
        elif self.state == GameState.SHOP and self.shop_screen:
            self.shop_screen.draw(self.screen)

        # 12. Move Master & Reroll Tutor Screen
        elif self.state == GameState.MOVE_RELEARN and self.move_reroll_screen:
            self.move_reroll_screen.draw(self.screen)

        # 13. Battle Screen
        elif self.state == GameState.BATTLE and self.battle_system:
            self.battle_system.draw(self.screen)


        # On-screen Notification Banner
        if self.notification_timer > 0:
            nw = gfx.fonts["regular"].size(self.notification_text)[0] + 36
            nx = (SCREEN_WIDTH - nw) // 2
            ny = 20
            pygame.draw.rect(self.screen, (30, 36, 50), (nx - 2, ny - 2, nw + 4, 36), border_radius=8)
            pygame.draw.rect(self.screen, (255, 235, 180), (nx, ny, nw, 32), border_radius=6)
            ntxt = gfx.fonts["regular"].render(self.notification_text, True, (180, 60, 0))
            self.screen.blit(ntxt, (nx + 18, ny + 5))

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            # Limit dt to prevent large frame skips
            dt = min(0.05, dt)
            self.handle_input(dt)
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()

def start():
    game = Game()
    game.run()


if __name__ == "__main__":
    start()
