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
from pokemon_data import WILD_ENCOUNTERS
from pokemon import Pokemon
from inventory import Inventory
from world import World, Player
from battle_system import BattleSystem
from save_system import SaveSystem, Pokedex
from ui_manager import (
    TitleScreen, StarterSelectScreen, TrainerCustomizationScreen, PauseMenu, PokedexScreen,
    PartySummaryScreen, ShopScreen, DialogueBox, SaveDialog, SaveSlotSelectScreen, PCBoxScreen
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
        self.shop_screen = None
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
        self.inventory = Inventory()
        self.state = GameState.OVERWORLD
        sound_mgr.play_bgm("town")
        # Save initial game state to selected slot
        SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world, slot=self.current_save_slot, pc_box=self.pc_box)
        self.show_notification(f"Welcome, {self.player.name}! Received {starter_species}!")

    def start_wild_battle(self, encounter_zone):
        table = WILD_ENCOUNTERS.get(encounter_zone, WILD_ENCOUNTERS["Route 1"])
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
            pc_box=self.pc_box
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
            pc_box=self.pc_box
        )
        self.state = GameState.BATTLE

    def handle_input(self, dt):
        raw_events = list(pygame.event.get())
        extra, notices = self.input_mgr.process(raw_events, dt)
        for msg in notices:
            self.show_notification(msg)
        for event in raw_events + extra:
            if event.type == pygame.QUIT:
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
                            if len(res) == 4:
                                self.party, self.inventory, self.pokedex, self.pc_box = res
                            else:
                                self.party, self.inventory, self.pokedex = res[:3]
                                self.pc_box = []
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
                                if len(res) == 4:
                                    self.party, self.inventory, self.pokedex, self.pc_box = res
                                else:
                                    self.party, self.inventory, self.pokedex = res[:3]
                                    self.pc_box = []
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
                        ok, msg = SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world, slot=self.current_save_slot, pc_box=self.pc_box)
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
                    self.state = GameState.TRAINER_CARD
                elif action == "BAG":
                    self.shop_screen = ShopScreen(self.inventory)
                    self.state = GameState.SHOP
                elif action == "PC BOX":
                    self.pc_box_screen = PCBoxScreen(self.party, self.pc_box)
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
                        pc_box=self.pc_box
                    )
                    self.state = GameState.SAVE_SLOTS
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

            # Party Summary View State
            if self.state == GameState.TRAINER_CARD:
                if self.party_screen:
                    res = self.party_screen.handle_input(event)
                    if res == "BACK":
                        self.state = GameState.OVERWORLD
                continue

            # Shop View State
            if self.state == GameState.SHOP:
                if self.shop_screen:
                    res = self.shop_screen.handle_input(event)
                    if res == "EXIT":
                        self.state = GameState.OVERWORLD
                continue

            # Dialogue State
            if self.state == GameState.DIALOGUE:
                if self.current_dialogue:
                    done = self.current_dialogue.handle_input(event)
                    if done:
                        self.current_dialogue = None
                        self.state = GameState.OVERWORLD
                continue

            # Battle State
            if self.state == GameState.BATTLE:
                if self.battle_system:
                    self.battle_system.handle_input(event)
                continue

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
            
        # Check PC Terminal tile or interaction in Pokecenter
        if self.player.current_map == "Pokecenter" and fx == 8 and fy in [4, 5]:
            sound_mgr.play_sfx("confirm")
            self.pc_box_screen = PCBoxScreen(self.party, self.pc_box)
            self.state = GameState.PC_BOX
            return

        # Check NPC
        npc = self.world.get_npc_at(self.player.current_map, fx, fy)
        if npc:
            sound_mgr.play_sfx("confirm")
            if npc.get("is_pc"):
                self.pc_box_screen = PCBoxScreen(self.party, self.pc_box)
                self.state = GameState.PC_BOX
            elif npc.get("is_healer"):
                # Nurse Joy Healer
                for p in self.party:
                    p.full_restore()
                # Auto-save at Pokemon Center
                SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world, slot=self.current_save_slot, pc_box=self.pc_box)
                sound_mgr.play_sfx("heal")
                self.current_dialogue = DialogueBox("Nurse Joy", f"Your Pokémon are fully healed and your progress was saved to Slot {self.current_save_slot}!", on_complete=None)
                self.state = GameState.DIALOGUE
            elif npc.get("is_shop"):
                # Open Mart
                self.shop_screen = ShopScreen(self.inventory)
                self.state = GameState.SHOP
            else:
                self.current_dialogue = DialogueBox(npc.get("name", "NPC"), npc.get("dialog", "Hello!"), on_complete=None)
                self.state = GameState.DIALOGUE
            return

        # Check Trainer talk
        trainer = self.world.get_any_trainer_at(self.player.current_map, fx, fy)
        if trainer:
            sound_mgr.play_sfx("confirm")
            if trainer["id"] in self.world.defeated_trainers:
                # Already defeated -> talk
                self.current_dialogue = DialogueBox(trainer["name"], trainer.get("dialog_after", "Good battle!"), on_complete=None)
                self.state = GameState.DIALOGUE
            else:
                # Undefeated -> start battle
                self.start_trainer_battle(trainer)
            return

        # Check Door / Warp interaction directly in front of player
        warp = self.world.get_warp_target(self.player.current_map, fx, fy)
        if warp:
            self.execute_warp(warp)
            return

    def execute_warp(self, warp):
        sound_mgr.play_sfx("confirm")
        target_map = warp["target_map"]
        target_x = warp["target_x"]
        target_y = warp["target_y"]
        
        # If entering interior, record origin
        if target_map in ["Pokecenter", "Mart"] and self.player.current_map not in ["Pokecenter", "Mart"]:
            self.world.interior_origin_map = self.player.current_map
            self.world.interior_origin_coords = (self.player.grid_x, self.player.grid_y)
        # If exiting interior, return to recorded origin or fallback
        elif target_map in ["Route 1", "Viridian City", "Pallet Town", "Viridian Forest"] and self.player.current_map in ["Pokecenter", "Mart"]:
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
                    
                # 2. Check Tall Grass Wild Encounter (14% chance per step)
                if self.player.in_tall_grass:
                    zone = self.world.maps[self.player.current_map].get("encounter_zone")
                    if zone and random.random() < 0.14:
                        self.start_wild_battle(zone)
                        return
                        
                # 3. Check Trainer Line of Sight
                spotted_trainer = self.world.check_trainer_line_of_sight(self.player.current_map, self.player.grid_x, self.player.grid_y)
                if spotted_trainer:
                    self.start_trainer_battle(spotted_trainer)
                    return

            # Smooth Camera Tracking centered on player
            map_w, map_h = self.world.get_map_dimensions(self.player.current_map)
            target_cam_x = self.player.pixel_x + 16 - SCREEN_WIDTH // 2
            target_cam_y = self.player.pixel_y + 16 - SCREEN_HEIGHT // 2
            
            # Clamp camera to map bounds
            self.camera_x = max(0, min(map_w - SCREEN_WIDTH, target_cam_x)) if map_w > SCREEN_WIDTH else (map_w - SCREEN_WIDTH) // 2
            self.camera_y = max(0, min(map_h - SCREEN_HEIGHT, target_cam_y)) if map_h > SCREEN_HEIGHT else (map_h - SCREEN_HEIGHT) // 2

        # Save Slot Select Screen State update
        elif self.state == GameState.SAVE_SLOTS and self.save_slot_screen:
            self.save_slot_screen.update(dt)

        # Trainer Customization State update
        elif self.state == GameState.TRAINER_CUSTOMIZE and self.trainer_customize_screen:
            self.trainer_customize_screen.update(dt)

        # PC Box State update
        elif self.state == GameState.PC_BOX and self.pc_box_screen:
            self.pc_box_screen.update(dt)

        # Dialogue State update
        elif self.state == GameState.DIALOGUE:
            if self.current_dialogue:
                self.current_dialogue.update(dt)

        # Battle State update
        elif self.state == GameState.BATTLE:
            if self.battle_system:
                self.battle_system.update(dt)
                
                # Check Battle Completion
                if self.battle_system.phase == "FINISHED":
                    if self.battle_system.is_trainer:
                        t_id = self.battle_system.trainer_data.get("id") if self.battle_system.trainer_data else None
                        if t_id:
                            self.world.defeated_trainers.add(t_id)
                        # Save game progress immediately so defeated trainers stay defeated across reloads
                        SaveSystem.save_game(
                            self.player, self.party, self.inventory, self.pokedex, self.world,
                            slot=self.current_save_slot, pc_box=self.pc_box
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
            self.world.draw(self.screen, self.player.current_map, self.camera_x, self.camera_y)
            self.player.draw(self.screen, self.camera_x, self.camera_y)
            
            # Map location badge (top-left)
            loc_name = self.player.current_map
            pygame.draw.rect(self.screen, (20, 24, 36, 180), (16, 16, gfx.fonts["regular"].size(loc_name)[0] + 24, 30), border_radius=6)
            ltxt = gfx.fonts["regular"].render(loc_name, True, (240, 244, 250))
            self.screen.blit(ltxt, (28, 20))

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

        # 8. Party Summary Screen
        elif self.state == GameState.TRAINER_CARD and self.party_screen:
            self.party_screen.draw(self.screen)

        # 9. Shop Screen
        elif self.state == GameState.SHOP and self.shop_screen:
            self.shop_screen.draw(self.screen)

        # 10. Battle Screen
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
