"""
tests_systems.py - Advanced systems unit tests: Quests, barriers, evolution chart,
dialogue transitions, following partner Pokémon, VFX, pagination, items (Rare Candy, Revive),
move disks, and running mechanics.
"""
import os
import sys
import unittest
import tempfile
import shutil
import pygame

from constants import (
    TYPE_CHART, TYPE_COLORS, Direction, KEY_CONFIRM, KEY_CANCEL, KEY_MENU,
    KEY_QUICKSAVE, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_RUN
)
from pokemon_data import (
    POKEMON_SPECIES, MOVES, ITEMS, WILD_ENCOUNTERS, WILD_WATER_ENCOUNTERS,
    TRAINERS, STONE_EVOLUTIONS
)
from pokemon import Pokemon
from inventory import Inventory
from world import World, Player
from save_system import SaveSystem, Pokedex
from sound_manager import SoundManager, sound_mgr
from graphics_manager import GraphicsManager, gfx
from quest_system import QuestManager
from barrier_system import barrier_mgr
from battle_system import BattleSystem, BattlePhase
from ui_screens import PartySummaryScreen, PCBoxScreen, BagScreen
from ui_trainer import TrainerCardScreen
from input_manager import InputManager
from ui_dialogs import DialogueBox


class TestSystemsMixin:
    def test_quest_system_catch_progression_and_auto_completion(self):
        from quest_system import QuestManager, QUEST_DEFINITIONS
        q_mgr = QuestManager()
        inv = Inventory()
        inv.money = 500

        # 1. Accept bug hunt quest
        self.assertTrue(q_mgr.accept_quest("oak_bug_hunt"))
        self.assertTrue(q_mgr.is_active("oak_bug_hunt"))
        self.assertEqual(q_mgr.get_progress("oak_bug_hunt"), 0)

        # 2. Catch Non-Bug Pokemon (e.g. Pidgey) -> No progress
        q_mgr.on_pokemon_caught("Pidgey", inv)
        self.assertEqual(q_mgr.get_progress("oak_bug_hunt"), 0)

        # 3. Catch Bug Pokemon 1 (Caterpie)
        q_mgr.on_pokemon_caught("Caterpie", inv)
        self.assertEqual(q_mgr.get_progress("oak_bug_hunt"), 1)
        self.assertFalse(q_mgr.is_completed("oak_bug_hunt"))

        # 4. Catch Bug Pokemon 2 (Weedle)
        q_mgr.on_pokemon_caught("Weedle", inv)
        self.assertEqual(q_mgr.get_progress("oak_bug_hunt"), 2)

        # 5. Catch Bug Pokemon 3 (Butterfree) -> Meets target (3) -> Auto-completes instantly!
        q_mgr.on_pokemon_caught("Butterfree", inv)
        self.assertFalse(q_mgr.is_active("oak_bug_hunt"))
        self.assertTrue(q_mgr.is_completed("oak_bug_hunt"))

        # 6. Verify Instant Rewards Delivery
        # Oak bug hunt rewards: $1000, 5x Great Ball, 1x Rare Candy
        self.assertEqual(inv.money, 1500)
        self.assertEqual(inv.get_count("Great Ball"), 5)
        self.assertEqual(inv.get_count("Rare Candy"), 1)

        # 7. Verify Notification
        notifs = q_mgr.pop_notifications()
        self.assertEqual(len(notifs), 1)
        self.assertIn("QUEST COMPLETE", notifs[0])
        self.assertIn("Bug Researcher's Survey", notifs[0])

    def test_quest_system_defeat_and_trainer_triggers(self):
        from quest_system import QuestManager
        q_mgr = QuestManager()
        inv = Inventory()
        inv.money = 0

        # Accept karate spirit quest (Defeat 4 Fighting or Rock Pokémon)
        q_mgr.accept_quest("karate_spirit")
        self.assertTrue(q_mgr.is_active("karate_spirit"))

        # Defeat Water Pokemon -> No progress
        q_mgr.on_pokemon_defeated("Squirtle", inv)
        self.assertEqual(q_mgr.get_progress("karate_spirit"), 0)

        # Defeat Fighting/Rock Pokemon
        q_mgr.on_pokemon_defeated("Mankey", inv) # Fighting
        q_mgr.on_pokemon_defeated("Geodude", inv) # Rock
        q_mgr.on_pokemon_defeated("Machop", inv) # Fighting
        self.assertEqual(q_mgr.get_progress("karate_spirit"), 3)

        q_mgr.on_pokemon_defeated("Onix", inv) # Rock -> 4/4!
        self.assertTrue(q_mgr.is_completed("karate_spirit"))
        self.assertEqual(inv.money, 3000)
        self.assertEqual(inv.get_count("Move Reroll Disk"), 1)
        self.assertEqual(inv.get_count("Max Potion"), 2)

        # Accept and complete Trainer trials quest (Defeat 5 trainers)
        q_mgr.accept_quest("champion_road_trial")
        for i in range(5):
            q_mgr.on_trainer_defeated(f"trainer_{i}", inv)
        self.assertTrue(q_mgr.is_completed("champion_road_trial"))
        self.assertEqual(inv.get_count("Rare Candy"), 5)
        self.assertEqual(inv.get_count("Nugget"), 2)

    def test_quest_system_stone_evolution_trigger(self):
        from quest_system import QuestManager
        q_mgr = QuestManager()
        inv = Inventory()
        inv.money = 0

        q_mgr.accept_quest("celadon_evolution_mastery")
        self.assertTrue(q_mgr.is_active("celadon_evolution_mastery"))

        # Use Potion -> No progress
        q_mgr.on_item_used("Potion", inv, is_evolution_stone=False)
        self.assertEqual(q_mgr.get_progress("celadon_evolution_mastery"), 0)

        # Use Water Stone -> Completes quest!
        q_mgr.on_item_used("Water Stone", inv, is_evolution_stone=True)
        self.assertTrue(q_mgr.is_completed("celadon_evolution_mastery"))
        self.assertEqual(inv.money, 3500)
        self.assertEqual(inv.get_count("Rare Candy"), 3)
        self.assertEqual(inv.get_count("Nugget"), 1)

    def test_quest_persistence_save_and_load(self):
        from quest_system import QuestManager
        world = World()
        player = Player(x=8, y=6, current_map="Pallet Town")
        party = [Pokemon("Pikachu", level=12)]
        inv = Inventory()
        dex = Pokedex()
        q_mgr = QuestManager()

        # Set up active quest with partial progress and one completed quest
        q_mgr.accept_quest("oak_bug_hunt")
        q_mgr.active_quests["oak_bug_hunt"]["progress"] = 2
        q_mgr.completed_quests["sparky_electric_charge"] = {"completed_at": "2026-09-01 12:00:00"}

        SaveSystem.save_game(player, party, inv, dex, world, slot=2, quest_mgr=q_mgr)

        loaded_player = Player()
        loaded_world = World()
        res, msg = SaveSystem.load_game(loaded_player, loaded_world, slot=2)
        self.assertIsNotNone(res)
        self.assertGreaterEqual(len(res), 5)
        loaded_party, loaded_inv, loaded_dex, loaded_pc, loaded_q_data = res[:5]

        loaded_q_mgr = QuestManager.from_dict(loaded_q_data)
        self.assertTrue(loaded_q_mgr.is_active("oak_bug_hunt"))
        self.assertEqual(loaded_q_mgr.get_progress("oak_bug_hunt"), 2)
        self.assertTrue(loaded_q_mgr.is_completed("sparky_electric_charge"))
        self.assertFalse(loaded_q_mgr.is_active("sparky_electric_charge"))

    def test_quest_log_ui_screen_and_map_indicators(self):
        from quest_system import QuestManager
        from ui_manager import QuestLogScreen, PauseMenu
        surf = pygame.Surface((800, 600))
        q_mgr = QuestManager()
        player = Player(x=8, y=6, current_map="Pallet Town")
        world = World()

        # Pause menu contains QUESTS option
        p_menu = PauseMenu()
        self.assertIn("QUESTS", p_menu.options)

        # Empty Quest log draw
        screen = QuestLogScreen(q_mgr, player)
        screen.draw(surf)

        # Accept active quest and complete another
        q_mgr.accept_quest("oak_bug_hunt")
        q_mgr.active_quests["oak_bug_hunt"]["progress"] = 1
        q_mgr.completed_quests["bird_watcher_avian"] = {"completed_at": "2026-09-01"}

        # Draw active tab
        self.assertEqual(screen.active_tab, 0)
        screen.draw(surf)

        # Switch to Completed tab
        event_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        screen.handle_input(event_right)
        self.assertEqual(screen.active_tab, 1)
        screen.draw(surf)

        # World draw with quest indicator badges
        world.draw(surf, "Pallet Town", 0, 0, quest_mgr=q_mgr)
        world.draw(surf, "Route 1", 0, 0, quest_mgr=q_mgr)
        world.draw(surf, "Pewter City", 0, 0, quest_mgr=q_mgr)
        world.draw(surf, "Vermilion City", 0, 0, quest_mgr=q_mgr)

    def test_zone_barriers_and_gated_progression(self):
        """Tests that zone barriers properly block movement, evaluate conditions, and persist unlocks."""
        world = World()
        player = Player(x=13, y=1, current_map="Viridian City")
        party = [Pokemon("Charmander", level=5)]
        inv = Inventory()
        pokedex = Pokedex()
        q_mgr = QuestManager()

        # 1. Test Viridian City north barrier (Route 2 / Viridian Forest)
        # Initially blocked
        self.assertTrue(barrier_mgr.is_tile_blocked("Viridian City", 13, 1, world.unlocked_barriers))
        self.assertFalse(world.is_passable("Viridian City", 13, 1))

        # Evaluate condition initially (False because quest not done and <3 caught)
        is_met, prog = barrier_mgr.evaluate_condition("barrier_route2_survey", player, party, world, q_mgr, pokedex, inv)
        self.assertFalse(is_met)

        # Catch 3 Pokemon to satisfy requirement
        pokedex.register_caught("Caterpie")
        pokedex.register_caught("Weedle")
        pokedex.register_caught("Pidgey")
        is_met, prog = barrier_mgr.evaluate_condition("barrier_route2_survey", player, party, world, q_mgr, pokedex, inv)
        self.assertTrue(is_met)

        # Unlock barrier
        world.unlocked_barriers.add("barrier_route2_survey")
        self.assertFalse(barrier_mgr.is_tile_blocked("Viridian City", 13, 1, world.unlocked_barriers))
        self.assertTrue(world.is_passable("Viridian City", 13, 1))

        # 2. Test Pewter City Boulder Badge Barrier
        self.assertTrue(barrier_mgr.is_tile_blocked("Pewter City", 26, 7, world.unlocked_barriers))
        is_met, _ = barrier_mgr.evaluate_condition("barrier_pewter_boulder", player, party, world, q_mgr, pokedex, inv)
        self.assertFalse(is_met)
        # Earn Boulder Badge
        world.badges.add("boulder")
        is_met, _ = barrier_mgr.evaluate_condition("barrier_pewter_boulder", player, party, world, q_mgr, pokedex, inv)
        self.assertTrue(is_met)

        # 3. Test Route 12 Sleeping Snorlax Barrier
        self.assertTrue(barrier_mgr.is_tile_blocked("Route 12", 8, 10, world.unlocked_barriers))
        is_met, _ = barrier_mgr.evaluate_condition("barrier_snorlax_route12", player, party, world, q_mgr, pokedex, inv)
        self.assertFalse(is_met)
        # Level up to 25
        party[0].level = 25
        is_met, _ = barrier_mgr.evaluate_condition("barrier_snorlax_route12", player, party, world, q_mgr, pokedex, inv)
        self.assertTrue(is_met)
        # Or have Poke Flute
        party[0].level = 10
        inv.add_item("Poke Flute", 1)
        is_met, _ = barrier_mgr.evaluate_condition("barrier_snorlax_route12", player, party, world, q_mgr, pokedex, inv)
        self.assertTrue(is_met)

        # 4. Test Victory Road 7-Badge + Level 45 Barrier
        is_met, _ = barrier_mgr.evaluate_condition("barrier_victory_road", player, party, world, q_mgr, pokedex, inv)
        self.assertFalse(is_met)
        for b in ["boulder", "cascade", "thunder", "rainbow", "soul", "marsh", "volcano"]:
            world.badges.add(b)
        party[0].level = 46
        is_met, _ = barrier_mgr.evaluate_condition("barrier_victory_road", player, party, world, q_mgr, pokedex, inv)
        self.assertTrue(is_met)

        # 5. Test Persistence across Save & Load
        world.unlocked_barriers.add("barrier_pewter_boulder")
        world.unlocked_barriers.add("barrier_snorlax_route12")
        SaveSystem.save_game(player, party, inv, pokedex, world, slot=1, quest_mgr=q_mgr)

        new_player = Player()
        new_world = World()
        res, msg = SaveSystem.load_game(new_player, new_world, slot=1)
        self.assertIsNotNone(res)
        self.assertIn("barrier_route2_survey", new_world.unlocked_barriers)
        self.assertIn("barrier_pewter_boulder", new_world.unlocked_barriers)
        self.assertIn("barrier_snorlax_route12", new_world.unlocked_barriers)

        # 6. Test Barrier rendering on overworld
        surf = pygame.Surface((320, 240))
        new_world.draw(surf, "Viridian City", 0, 0, quest_mgr=q_mgr)
        new_world.draw(surf, "Pewter City", 0, 0, quest_mgr=q_mgr)
        new_world.draw(surf, "Route 12", 0, 0, quest_mgr=q_mgr)

    def test_pc_box_evolution_progression_chart(self):
        """Tests evolution info calculations, family tree generation, and PC Box evolution progression chart modal."""
        from ui_screens import get_pokemon_evolution_info, get_full_evolution_tree, PCBoxScreen

        # 1. Test get_pokemon_evolution_info on various Pokemon
        bulba = Pokemon("Bulbasaur", level=5)
        e_bulba = get_pokemon_evolution_info(bulba)
        self.assertEqual(e_bulba["method"], "LEVEL")
        self.assertEqual(e_bulba["target_species"], "Ivysaur")
        self.assertEqual(e_bulba["req_level"], 16)
        self.assertEqual(e_bulba["levels_left"], 11)
        self.assertFalse(e_bulba["is_ready"])

        ivy = Pokemon("Ivysaur", level=32)
        e_ivy = get_pokemon_evolution_info(ivy)
        self.assertEqual(e_ivy["method"], "LEVEL")
        self.assertEqual(e_ivy["target_species"], "Venusaur")
        self.assertTrue(e_ivy["is_ready"])
        self.assertEqual(e_ivy["levels_left"], 0)

        venu = Pokemon("Venusaur", level=45)
        e_venu = get_pokemon_evolution_info(venu)
        self.assertEqual(e_venu["method"], "NONE")
        self.assertIn("Final Form", e_venu["short_text"])

        # 2. Test get_full_evolution_tree
        root, chain = get_full_evolution_tree("Venusaur")
        self.assertEqual(root, "Bulbasaur")
        self.assertEqual(len(chain), 3)
        self.assertEqual([node["species"] for node in chain], ["Bulbasaur", "Ivysaur", "Venusaur"])

        root_eevee, chain_eevee = get_full_evolution_tree("Vaporeon")
        self.assertEqual(root_eevee, "Eevee")
        self.assertEqual(chain_eevee[0]["species"], "Eevee")

        # 3. Test PCBoxScreen with Evolution Progression Chart
        party = [Pokemon("Charmander", level=12), Pokemon("Pikachu", level=20)]
        pc_box = [Pokemon("Caterpie", level=3), Pokemon("Snorlax", level=30)]
        inv = Inventory()
        screen = PCBoxScreen(party, pc_box, inventory=inv)

        # Draw main PC Box screen (renders cards with evolution pills)
        surf = pygame.Surface((800, 600))
        screen.draw(surf)

        # Open Action menu and select EVOLUTION PROGRESSION
        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        self.assertEqual(screen.menu_mode, "ACTIONS")
        actions = screen._get_available_actions()
        self.assertIn("EVOLUTION PROGRESSION", actions)
        evo_idx = actions.index("EVOLUTION PROGRESSION")
        screen.action_idx = evo_idx

        # Confirm action -> opens EVOLUTION_CHART
        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        self.assertEqual(screen.menu_mode, "EVOLUTION_CHART")
        self.assertIsNotNone(screen.evolution_pokemon)
        self.assertEqual(screen.evolution_pokemon.species, "Charmander")

        # Draw Evolution Progression Chart modal
        screen.draw(surf)

        # Navigate between Pokemon in Evolution Chart
        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
        self.assertEqual(screen.evolution_pokemon.species, "Pikachu")
        screen.draw(surf)

        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
        self.assertEqual(screen.active_panel, "PC")
        self.assertEqual(screen.evolution_pokemon.species, "Caterpie")
        screen.draw(surf)

        # Close Evolution Chart
        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertEqual(screen.menu_mode, "NAVIGATE")
        self.assertIsNone(screen.evolution_pokemon)

        # Direct Hotkey [E] / [Tab]
        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
        self.assertEqual(screen.menu_mode, "EVOLUTION_CHART")
        screen.draw(surf)

    def test_trainer_encounter_dialogue_and_battle_transition(self):
        """Tests that approaching or talking to an undefeated trainer starts dialogue and transitions to GameState.BATTLE."""
        from main import Game
        from constants import GameState
        from ui_dialogs import DialogueBox

        game = Game()
        # Initialize with player and party
        game.player = Player(x=8, y=20, current_map="Route 1")
        game.party = [Pokemon("Bulbasaur", level=8)]
        game.state = GameState.OVERWORLD

        # Check line of sight: Bug Catcher Sammy is at (6, 20) facing RIGHT, player at (8, 20)
        spotted = game.world.check_trainer_line_of_sight("Route 1", 8, 20)
        self.assertIsNotNone(spotted)
        self.assertEqual(spotted["id"], "bug_catcher_sammy")

        # Simulate line of sight trigger in main loop
        dialog_text = spotted.get("dialog_before", "Let's battle!")
        game.current_dialogue = DialogueBox(
            spotted["name"],
            dialog_text,
            on_complete=lambda t=spotted: game.start_trainer_battle(t),
            portrait_key=spotted.get("id"),
            trainer_data=spotted
        )
        game.state = GameState.DIALOGUE

        # Player skips typewriter text (first press)
        evt_confirm = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)
        if game.state == GameState.DIALOGUE and game.current_dialogue:
            done = game.current_dialogue.handle_input(evt_confirm)
            if done:
                game.current_dialogue = None
                if game.state == GameState.DIALOGUE:
                    game.state = GameState.OVERWORLD

        self.assertTrue(game.current_dialogue.finished)
        self.assertEqual(game.state, GameState.DIALOGUE)

        # Player confirms finished text (second press) -> should transition to BATTLE!
        if game.state == GameState.DIALOGUE and game.current_dialogue:
            done = game.current_dialogue.handle_input(evt_confirm)
            if done:
                game.current_dialogue = None
                if game.state == GameState.DIALOGUE:
                    game.state = GameState.OVERWORLD

        # Verify state is BATTLE and battle system is active
        self.assertEqual(game.state, GameState.BATTLE)
        self.assertIsNotNone(game.battle_system)
        self.assertTrue(game.battle_system.is_trainer)
        self.assertEqual(game.battle_system.trainer_data["id"], "bug_catcher_sammy")
        self.assertEqual(game.battle_system.enemy_pokemon.species, "Caterpie")

    def test_following_partner_pokemon(self):
        """Tests that the first non-fainted party Pokemon follows the player, trails movement, updates on faint, and interacts."""
        from player import FollowerPokemon, Player
        from main import Game
        from constants import Direction, GameState

        # 1. Test FollowerPokemon syncing with party
        p1 = Pokemon("Pikachu", level=15)
        p2 = Pokemon("Charmander", level=12)
        party = [p1, p2]

        follower = FollowerPokemon(x=8, y=5)
        follower.sync_with_party(party)
        self.assertEqual(follower.current_pokemon.species, "Pikachu")

        # When leader faints, follower switches to next conscious Pokemon
        p1.current_hp = 0
        self.assertTrue(p1.is_fainted())
        follower.sync_with_party(party)
        self.assertEqual(follower.current_pokemon.species, 'Charmander')

        # When all faint, follower has no active pokemon
        p2.current_hp = 0
        follower.sync_with_party(party)
        self.assertIsNone(follower.current_pokemon)

        # Revive and heal
        p1.full_restore()
        follower.sync_with_party(party)
        self.assertEqual(follower.current_pokemon.species, 'Pikachu')

        # 2. Test Follower trailing behind Player movement
        world = World()
        player = Player(x=8, y=6, current_map='Pallet Town')
        player.follower.sync_with_party(party)
        player.follower.teleport_to_player(player)

        # Player moves DOWN (from (8,6) to (8,7))
        moved = player.move(Direction.DOWN, world)
        self.assertTrue(moved)
        self.assertTrue(player.is_moving)
        self.assertTrue(player.follower.is_moving)
        self.assertEqual(player.follower.target_x, 8)
        self.assertEqual(player.follower.target_y, 6)

        # Update until movement completes
        player.update(0.3, world)
        self.assertFalse(player.is_moving)
        self.assertFalse(player.follower.is_moving)
        self.assertEqual((player.grid_x, player.grid_y), (8, 7))
        self.assertEqual((player.follower.grid_x, player.follower.grid_y), (8, 6))

        # 3. Test Follower drawing and Emotes
        surf = pygame.Surface((320, 240))
        player.follower.trigger_emote('heart', duration=2.0)
        self.assertEqual(player.follower.emote_type, 'heart')
        player.draw(surf, 0, 0)

        # 4. Test Overworld Partner Interaction in Game
        game = Game()
        game.party = [Pokemon('Squirtle', level=10)]
        game.player = Player(x=8, y=6, current_map='Pallet Town')
        game.player.follower.sync_with_party(game.party)
        game.player.follower.grid_x = 8
        game.player.follower.grid_y = 5
        game.player.facing = Direction.UP
        game.state = GameState.OVERWORLD
        game._handle_overworld_interaction()
        self.assertEqual(game.state, GameState.DIALOGUE)
        self.assertIsNotNone(game.current_dialogue)
        self.assertIn('Squirtle', game.current_dialogue.full_text)
        self.assertEqual(game.current_dialogue.portrait_key, 'Squirtle')

    def test_battle_attack_elemental_vfx(self):
        from battle_system import BattleSystem, BattlePhase
        from battle_vfx import draw_battle_attack_vfx
        p_pkmn = Pokemon('Charmander', level=10)
        e_pkmn = Pokemon('Bulbasaur', level=10)
        battle = BattleSystem([p_pkmn], e_pkmn)
        while battle.messages or battle.phase == BattlePhase.MESSAGE_QUEUE:
            battle.advance_message_queue()
        battle._queue_attack(p_pkmn, e_pkmn, {'name': 'Ember', 'type': 'Fire', 'power': 40, 'accuracy': 100, 'category': 'Special'}, is_player=True)
        battle.advance_message_queue()
        self.assertEqual(battle.phase, BattlePhase.ATTACK_ANIM)
        surf = pygame.Surface((800, 600))
        draw_battle_attack_vfx(surf, {'move_name': 'Fire Strike', 'move_type': 'Fire', 'is_player_attacker': True, 'is_crit': True, 'effectiveness': 2.0, 'category': 'Special'}, timer=0.25, player_pos=(200, 300), enemy_pos=(600, 150))
        battle.draw(surf)
        battle.update(0.7)
        self.assertEqual(battle.phase, BattlePhase.HP_ANIM)

    def test_active_quest_persistence_on_save_and_exit(self):
        test_dir = tempfile.mkdtemp()
        SaveSystem.set_saves_dir(test_dir)
        try:
            player = Player(name='Ash', x=8, y=6)
            party = [Pokemon('Pikachu', level=10)]
            inv = Inventory()
            pokedex = Pokedex()
            world = World()
            q_mgr = QuestManager()
            q_mgr.accept_quest('oak_bug_hunt')
            caterpie = Pokemon('Caterpie', level=4)
            q_mgr.on_pokemon_caught(caterpie, inv)
            q_mgr.on_pokemon_caught(caterpie, inv)
            self.assertEqual(q_mgr.get_progress('oak_bug_hunt'), 2)
            self.assertTrue(q_mgr.is_active('oak_bug_hunt'))
            ok, msg = SaveSystem.save_game(player, party, inv, pokedex, world, slot=1, pc_box=[], quest_mgr=q_mgr)
            self.assertTrue(ok)
            ok2, msg2 = SaveSystem.save_game(player, party, inv, pokedex, world, slot=1, pc_box=[], quest_mgr=None)
            self.assertTrue(ok2)
            new_player = Player()
            new_world = World()
            res, load_msg = SaveSystem.load_game(new_player, new_world, slot=1)
            self.assertIsNotNone(res)
            new_party, new_inv, new_pdx, new_pc_box, q_data = res[:5]
            restored_q_mgr = QuestManager.from_dict(q_data)
            self.assertTrue(restored_q_mgr.is_active('oak_bug_hunt'))
            self.assertEqual(restored_q_mgr.get_progress('oak_bug_hunt'), 2)
            self.assertFalse(restored_q_mgr.is_completed('oak_bug_hunt'))
            msgs = restored_q_mgr.on_pokemon_caught(caterpie, new_inv)
            self.assertTrue(restored_q_mgr.is_completed('oak_bug_hunt'))
            self.assertFalse(restored_q_mgr.is_active('oak_bug_hunt'))
            self.assertGreater(len(msgs), 0)
        finally:
            SaveSystem.set_saves_dir(self.test_dir)

    def test_pokemon_move_swapping_and_summary_ui(self):
        from ui_screens import PartySummaryScreen
        from battle_system import BattleSystem, BattlePhase
        scyther = Pokemon('Scyther', level=42)
        m0, m1 = scyther.moves[0]['name'], scyther.moves[1]['name']
        self.assertTrue(scyther.swap_moves(0, 1))
        self.assertEqual(scyther.moves[0]['name'], m1)
        self.assertFalse(scyther.swap_moves(0, 0))

        party = [scyther, Pokemon('Pikachu', level=20)]
        screen = PartySummaryScreen(party)
        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        self.assertEqual(scyther.moves[0]["name"], m0)
        surf = pygame.Surface((800, 600))
        screen.draw(surf)

        # 3. Test BattleSystem in-battle move swapping
        battle = BattleSystem(party, Pokemon("Geodude", level=15), is_trainer=False)
        battle.phase = BattlePhase.MOVE_SELECT
        battle.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LSHIFT))
        battle.move_index = 1
        battle.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        self.assertEqual(scyther.moves[0]["name"], m1)
        battle.draw(surf)

    def test_battle_enemy_hp_and_damage_forecast(self):
        """Tests enemy numerical HP rendering, damage range forecasting, and combat damage numbers."""
        from battle_system import BattleSystem, BattlePhase
        battle = BattleSystem([Pokemon("Charmander", level=10)], Pokemon("Rattata", level=5), is_trainer=False)
        min_d, max_d, eff = battle.calculate_damage_range(battle.player_pokemon.moves[0])
        self.assertTrue(min_d > 0 and max_d >= min_d and eff == 1.0)
        min_g, max_g, _ = battle.calculate_damage_range({"name": "Growl", "type": "Normal", "power": 0, "category": "Status"})
        self.assertEqual(min_g, 0)
        surf = pygame.Surface((800, 600))
        battle.phase = BattlePhase.MOVE_SELECT
        battle.draw(surf)
        battle.floating_texts.append({"text": "-15", "x": 550, "y": 100, "timer": 1.4, "color": (255, 60, 60)})
        battle.update(0.1)
        battle.draw(surf)

    def test_dialogue_box_multi_page_pagination(self):
        """Tests that long dialogues are paginated across multiple pages and navigated with [Z/Enter]."""
        from ui_dialogs import DialogueBox
        text = "Line 1: Hello!\nLine 2: How are you?\nLine 3: Welcome to the region!\nLine 4: This is page two.\nLine 5: Enjoy your adventure!"
        completed = []
        box = DialogueBox("Guide", text, on_complete=lambda: completed.append(True), portrait_key="police_roadblock")
        self.assertEqual(len(box.pages), 2)
        # 1. First Z finishes typing page 1
        self.assertFalse(box.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)))
        self.assertTrue(box.finished_page)
        self.assertEqual(box.current_page_idx, 0)
        # 2. Second Z advances to page 2
        self.assertFalse(box.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)))
        self.assertEqual(box.current_page_idx, 1)
        # 3. Third Z finishes typing page 2
        self.assertFalse(box.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)))
        self.assertTrue(box.finished_page)
        # 4. Fourth Z closes dialogue and fires on_complete callback
        self.assertTrue(box.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)))
        self.assertEqual(len(completed), 1)

    def test_rare_candy_and_ready_evolution(self):
        """Tests that using Rare Candy triggers evolution when reaching level milestone, and ready evolution triggers."""
        inv = Inventory()
        inv.add_item("Rare Candy", 2)
        charmander = Pokemon("Charmander", level=15)
        self.assertIsNone(charmander.check_evolution())

        # 1. Use Rare Candy from Lv 15 to 16 -> should level up AND evolve to Charmeleon
        ok, msg = inv.use_item_on_pokemon("Rare Candy", charmander)
        self.assertTrue(ok)
        self.assertEqual(charmander.level, 16)
        self.assertEqual(charmander.species, "Charmeleon")
        self.assertIn("CHARMELEON", msg)

        # 2. Test already ready Pokémon (e.g. Squirtle at Lv 16)
        squirtle = Pokemon("Squirtle", level=16)
        self.assertEqual(squirtle.check_evolution(), "Wartortle")
        from ui_screens import PartySummaryScreen
        screen = PartySummaryScreen([squirtle])
        # Press [E] on ready Squirtle in party
        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
        self.assertEqual(squirtle.species, "Wartortle")
        self.assertIn("WARTORTLE", screen.notice_msg)

    def test_revive_and_max_revive_mechanics(self):
        """Tests that Revive and Max Revive revive fainted Pokémon in inventory, BagScreen, and Battle."""
        from battle_system import BattleSystem, BattlePhase
        from ui_screens import BagScreen

        # 1. Test Inventory use_item_on_pokemon with Revive and Max Revive
        inv = Inventory()
        inv.items = {}
        inv.add_item("Revive", 2)
        inv.add_item("Max Revive", 1)
        p1 = Pokemon("Pikachu", level=20)
        p2 = Pokemon("Bulbasaur", level=20)
        
        # Non-fainted -> Revive fails
        ok, msg = inv.use_item_on_pokemon("Revive", p1)
        self.assertFalse(ok)
        self.assertIn("not fainted", msg)

        # Fainted p1 -> Revive restores 50% HP
        p1.current_hp = 0
        self.assertTrue(p1.is_fainted())
        ok, msg = inv.use_item_on_pokemon("Revive", p1)
        self.assertTrue(ok)
        self.assertFalse(p1.is_fainted())
        self.assertEqual(p1.current_hp, p1.max_hp // 2)
        self.assertEqual(inv.get_count("Revive"), 1)

        # Fainted p2 -> Max Revive restores 100% HP
        p2.current_hp = 0
        self.assertTrue(p2.is_fainted())
        ok, msg = inv.use_item_on_pokemon("Max Revive", p2)
        self.assertTrue(ok)
        self.assertFalse(p2.is_fainted())
        self.assertEqual(p2.current_hp, p2.max_hp)
        self.assertEqual(inv.get_count("Max Revive"), 0)

        # 2. Test Revive in BattleSystem
        party = [Pokemon("Charmander", level=10), Pokemon("Squirtle", level=10)]
        party[1].current_hp = 0 # Squirtle is fainted
        battle_inv = Inventory()
        battle_inv.items = {"Revive": 1}
        enemy = Pokemon("Pidgey", level=5)
        battle = BattleSystem(party, enemy, is_trainer=False, inventory=battle_inv)
        battle.phase = BattlePhase.BAG_SELECT
        battle.bag_index = 0 # Select Revive

        # Press Confirm on Revive -> should enter PARTY_ITEM_SELECT
        battle.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        self.assertEqual(battle.phase, BattlePhase.PARTY_ITEM_SELECT)
        self.assertEqual(battle.selected_item_for_party, "Revive")

        # Navigate down to Squirtle (fainted) and press confirm
        battle.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
        self.assertEqual(battle.party_menu_index, 1)
        battle.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        
        # Squirtle should now be revived!
        self.assertFalse(party[1].is_fainted())
        self.assertEqual(party[1].current_hp, party[1].max_hp // 2)
        self.assertEqual(battle_inv.get_count("Revive"), 0)

        # 3. Test Revive in BagScreen (Overworld)
        bag_party = [Pokemon("Pikachu", level=10), Pokemon("Geodude", level=10)]
        bag_party[1].current_hp = 0 # Geodude fainted
        bag_inv = Inventory()
        bag_inv.items = {"Revive": 1}
        bag_screen = BagScreen(bag_party, bag_inv)
        
        # Find Revive index
        items = bag_screen.get_filtered_items()
        rev_idx = next(i for i, (n, c, d) in enumerate(items) if n == "Revive")
        bag_screen.selected_idx = rev_idx
        
        # Press Z on Revive -> enters USE_TARGET
        bag_screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        self.assertEqual(bag_screen.mode, "USE_TARGET")
        self.assertEqual(bag_screen.selected_item_name, "Revive")

        # Select Geodude and press Z
        bag_screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
        self.assertEqual(bag_screen.target_pkmn_idx, 1)
        bag_screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        
        self.assertFalse(bag_party[1].is_fainted())
        self.assertEqual(bag_party[1].current_hp, bag_party[1].max_hp // 2)
        self.assertEqual(bag_inv.get_count("Revive"), 0)

    def test_move_reroll_disk_select_move_slot(self):
        """Tests that Move Reroll Disk allows choosing which specific move slot to replace."""
        from ui_screens import BagScreen
        
        # 1. Setup Pokémon with 4 known moves
        char = Pokemon("Charmander", level=30)
        char.moves = [
            char.create_move_slot("Scratch"),
            char.create_move_slot("Ember"),
            char.create_move_slot("Flamethrower"),
            char.create_move_slot("Slash")
        ]
        self.assertEqual(len(char.moves), 4)

        # 2. Test Inventory use_item_on_pokemon with replace_idx
        inv = Inventory()
        inv.items = {"Move Reroll Disk": 2}
        
        # Replace move slot 2 ("Flamethrower") with "Fire Blast"
        ok, msg = inv.use_item_on_pokemon("Move Reroll Disk", char, replace_idx=2, specific_move="Fire Blast")
        self.assertTrue(ok)
        self.assertEqual(char.moves[2]["name"], "Fire Blast")
        self.assertEqual(char.moves[0]["name"], "Scratch") # Slot 0 untouched!
        self.assertEqual(inv.get_count("Move Reroll Disk"), 1)

        # 3. Test BagScreen interactive slot selection
        bag_screen = BagScreen([char], inv)
        items = bag_screen.get_filtered_items()
        mrd_idx = next(i for i, (n, c, d) in enumerate(items) if n == "Move Reroll Disk")
        bag_screen.selected_idx = mrd_idx

        # Press Z on Move Reroll Disk -> enters USE_TARGET
        bag_screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        self.assertEqual(bag_screen.mode, "USE_TARGET")

        # Press Z to apply on Charmander -> enters CHOOSE_MOVE_TO_REPLACE mode!
        bag_screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        self.assertEqual(bag_screen.mode, "CHOOSE_MOVE_TO_REPLACE")
        self.assertIsNotNone(bag_screen.pending_move)
        rolled_move = bag_screen.pending_move

        # Navigate down to slot 1 ("Ember") and press Z to replace
        bag_screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
        self.assertEqual(bag_screen.selected_move_slot, 1)
        bag_screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))

        # Check result
        self.assertEqual(bag_screen.mode, "BAG")
        self.assertEqual(char.moves[1]["name"], rolled_move)
        self.assertEqual(char.moves[0]["name"], "Scratch") # Slot 0 still untouched!
        self.assertEqual(inv.get_count("Move Reroll Disk"), 0)

    def test_running_mechanics_and_speed(self):
        """Tests that holding SPACE/running increases player & follower speed to 8.0 tiles/sec."""
        from constants import KEY_RUN
        self.assertIn(pygame.K_SPACE, KEY_RUN)
        self.assertIn(pygame.K_LSHIFT, KEY_RUN)

        world = World()
        player = Player(x=8, y=6, current_map="Pallet Town")
        follower_pkmn = Pokemon("Pikachu", level=10)
        player.follower.sync_with_party([follower_pkmn])
        player.follower.teleport_to_player(player)

        # 1. Default Walking Speed = 4.0
        player.update(0.1, world, is_running=False)
        self.assertFalse(player.is_running)
        self.assertEqual(player.move_speed, 4.0)
        self.assertEqual(player.follower.move_speed, 4.0)

        # 2. Running Speed (holding SPACE) = 8.0
        player.update(0.1, world, is_running=True)
        self.assertTrue(player.is_running)
        self.assertEqual(player.move_speed, 8.0)
        self.assertEqual(player.follower.move_speed, 8.0)

        # 3. Running Movement completes in half the time (0.125s vs 0.25s)
        player.move(Direction.DOWN, world)
        self.assertTrue(player.is_moving)
        # Advance 0.13 seconds at 8.0 tiles/sec -> 0.13 * 8.0 = 1.04 >= 1.0 (step complete!)
        player.update(0.13, world, is_running=True)
        self.assertFalse(player.is_moving)
        self.assertEqual((player.grid_x, player.grid_y), (8, 7))

if __name__ == "__main__":
    unittest.main()




