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
    TitleScreen, StarterSelectScreen, PauseMenu, PokedexScreen,
    PartySummaryScreen, ShopScreen, DialogueBox, SaveDialog
)

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pokémon - Pygame Edition")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game State
        self.state = GameState.TITLE
        self.world = World()
        self.player = Player(x=8, y=6, current_map="Pallet Town")
        self.party = []
        self.inventory = Inventory()
        self.pokedex = Pokedex()
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # UI Sub-screens
        self.title_screen = TitleScreen()
        self.starter_screen = StarterSelectScreen()
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

    def show_notification(self, text, duration=2.5):
        self.notification_text = text
        self.notification_timer = duration

    def start_new_game(self, starter_species):
        starter = Pokemon(starter_species, level=5)
        self.party = [starter]
        self.pokedex.register_caught(starter_species)
        self.player = Player(x=8, y=6, current_map="Pallet Town")
        self.inventory = Inventory()
        self.state = GameState.OVERWORLD
        sound_mgr.play_bgm("town")
        # Save initial game state
        SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world)
        self.show_notification(f"Received {starter_species}! Your adventure begins!")

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
            pokedex=self.pokedex
        )
        self.state = GameState.BATTLE

    def start_trainer_battle(self, trainer_data):
        sound_mgr.play_sfx("wild_encounter")
        self.battle_system = BattleSystem(
            player_party=self.party,
            opponent_pokemon_or_trainer=trainer_data,
            is_trainer=True,
            inventory=self.inventory,
            pokedex=self.pokedex
        )
        self.state = GameState.BATTLE

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Title State
            if self.state == GameState.TITLE:
                opt = self.title_screen.handle_input(event)
                if opt == "CONTINUE":
                    res, msg = SaveSystem.load_game(self.player, self.world)
                    if res:
                        self.party, self.inventory, self.pokedex = res
                        self.state = GameState.OVERWORLD
                        sound_mgr.play_bgm("town")
                        self.show_notification("Game loaded successfully!")
                    else:
                        self.show_notification("Failed to load save file.")
                elif opt == "NEW GAME":
                    self.state = GameState.STARTER_SELECT
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
                        ok, msg = SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world)
                        sound_mgr.play_sfx("confirm" if ok else "cancel")
                        self.show_notification("Quick-Saved game progress!")
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
                elif action == "SAVE":
                    self.save_dialog = SaveDialog(self.player, self.party, self.inventory, self.pokedex)
                    self.state = GameState.SAVE
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
            
        # Check NPC
        npc = self.world.get_npc_at(self.player.current_map, fx, fy)
        if npc:
            sound_mgr.play_sfx("confirm")
            if npc.get("is_healer"):
                # Nurse Joy Healer
                for p in self.party:
                    p.full_restore()
                # Auto-save at Pokemon Center
                SaveSystem.save_game(self.player, self.party, self.inventory, self.pokedex, self.world)
                sound_mgr.play_sfx("heal")
                self.current_dialogue = DialogueBox("Nurse Joy", "Your Pokémon are fully healed and your progress was saved! We hope to see you again!", on_complete=None)
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
                if any(keys[k] for k in KEY_UP):
                    self.player.move(Direction.UP, self.world)
                elif any(keys[k] for k in KEY_DOWN):
                    self.player.move(Direction.DOWN, self.world)
                elif any(keys[k] for k in KEY_LEFT):
                    self.player.move(Direction.LEFT, self.world)
                elif any(keys[k] for k in KEY_RIGHT):
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
                        self.world.defeated_trainers.add(self.battle_system.trainer_data["id"])
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

        # 2. Starter Select State
        elif self.state == GameState.STARTER_SELECT:
            self.starter_screen.draw(self.screen)

        # 3. Overworld & Sub-Menus & Save
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

        # 4. Pokédex Screen
        elif self.state == GameState.POKEDEX and self.pokedex_screen:
            self.pokedex_screen.draw(self.screen)

        # 5. Party Summary Screen
        elif self.state == GameState.TRAINER_CARD and self.party_screen:
            self.party_screen.draw(self.screen)

        # 6. Shop Screen
        elif self.state == GameState.SHOP and self.shop_screen:
            self.shop_screen.draw(self.screen)

        # 7. Battle Screen
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
            self.handle_input()
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
