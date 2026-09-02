"""
tests_core.py - Core engine unit tests: Stats, battle damage, healing, inventory,
type effectiveness, multi-slot saves, collision, sound, species, and status effects.
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


class TestCoreMixin:
    def test_pokemon_creation_and_stats(self):
        p = Pokemon("Charmander", level=5)
        self.assertEqual(p.species, "Charmander")
        self.assertEqual(p.level, 5)
        self.assertGreater(p.max_hp, 15)
        self.assertEqual(p.current_hp, p.max_hp)
        self.assertGreater(len(p.moves), 0)
        self.assertIn("Fire", p.types)

    def test_level_up_and_evolution(self):
        p = Pokemon("Charmander", level=15)
        # Advance to level 16
        exp_needed = p.exp_for_next_level() - p.exp
        events = p.gain_exp(exp_needed)
        self.assertEqual(p.level, 16)
        
        # Check evolution event
        evo_events = [e for e in events if e[0] == "EVOLVE"]
        self.assertTrue(len(evo_events) > 0)
        target = evo_events[0][1]
        self.assertEqual(target, "Charmeleon")
        
        # Execute evolution
        p.evolve(target)
        self.assertEqual(p.species, "Charmeleon")

    def test_damage_and_healing(self):
        p = Pokemon("Pikachu", level=10)
        max_hp = p.max_hp
        p.take_damage(10)
        self.assertEqual(p.current_hp, max_hp - 10)
        self.assertFalse(p.is_fainted())
        
        # Heal
        healed = p.heal(5)
        self.assertEqual(healed, 5)
        self.assertEqual(p.current_hp, max_hp - 5)
        
        # Faint
        p.take_damage(999)
        self.assertTrue(p.is_fainted())
        self.assertEqual(p.current_hp, 0)

    def test_inventory_mechanics(self):
        inv = Inventory()
        self.assertGreater(inv.money, 0)
        self.assertTrue(inv.get_count("Poke Ball") > 0)
        
        # Test potion healing
        p = Pokemon("Bulbasaur", level=10)
        p.take_damage(15)
        prev_hp = p.current_hp
        ok, msg = inv.use_item_on_pokemon("Potion", p)
        self.assertTrue(ok)
        self.assertGreater(p.current_hp, prev_hp)

    def test_type_effectiveness_matrix(self):
        # Water vs Fire = 2.0x
        self.assertEqual(TYPE_CHART["Water"]["Fire"], 2.0)
        # Fire vs Grass = 2.0x
        self.assertEqual(TYPE_CHART["Fire"]["Grass"], 2.0)
        # Electric vs Ground = 0.0x
        self.assertEqual(TYPE_CHART["Electric"]["Ground"], 0.0)

    def test_multi_slot_save_and_load(self):
        world = World()
        
        # Save Slot 1: Squirtle
        player1 = Player(x=5, y=5, current_map="Pallet Town")
        party1 = [Pokemon("Squirtle", level=8)]
        inv1 = Inventory()
        inv1.money = 5500
        pdx1 = Pokedex()
        pdx1.register_caught("Squirtle")
        ok1, msg1 = SaveSystem.save_game(player1, party1, inv1, pdx1, world, slot=1)
        self.assertTrue(ok1)
        
        # Save Slot 2: Charmander
        player2 = Player(x=12, y=8, current_map="Route 1")
        party2 = [Pokemon("Charmander", level=12), Pokemon("Pikachu", level=10)]
        inv2 = Inventory()
        inv2.money = 8200
        pdx2 = Pokedex()
        pdx2.register_caught("Charmander")
        pdx2.register_caught("Pikachu")
        ok2, msg2 = SaveSystem.save_game(player2, party2, inv2, pdx2, world, slot=2)
        self.assertTrue(ok2)

        # Verify Slot 1 Load
        loaded_p1 = Player()
        res1, msg = SaveSystem.load_game(loaded_p1, World(), slot=1)
        self.assertIsNotNone(res1)
        lp1, li1, lpd1, lpc1 = res1[:4]
        self.assertEqual(loaded_p1.grid_x, 5)
        self.assertEqual(loaded_p1.current_map, "Pallet Town")
        self.assertEqual(lp1[0].species, "Squirtle")
        self.assertEqual(li1.money, 5500)
        self.assertIn("Squirtle", lpd1.caught)

        # Verify Slot 2 Load
        loaded_p2 = Player()
        res2, msg = SaveSystem.load_game(loaded_p2, World(), slot=2)
        self.assertIsNotNone(res2)
        lp2, li2, lpd2, lpc2 = res2[:4]
        self.assertEqual(loaded_p2.grid_x, 12)
        self.assertEqual(loaded_p2.current_map, "Route 1")
        self.assertEqual(len(lp2), 2)
        self.assertEqual(lp2[0].species, "Charmander")
        self.assertEqual(li2.money, 8200)
        self.assertIn("Charmander", lpd2.caught)
        self.assertIn("Pikachu", lpd2.caught)

        # Verify Slot summaries
        summaries = SaveSystem.get_all_slots_summary()
        self.assertEqual(len(summaries), 99)
        self.assertTrue(summaries[0]["exists"])
        self.assertEqual(summaries[0]["lead_species"], "Squirtle")
        self.assertTrue(summaries[1]["exists"])
        self.assertEqual(summaries[1]["lead_species"], "Charmander")
        self.assertEqual(summaries[1]["party_count"], 2)

    def test_99_save_slots_and_persistence(self):
        """Tests saving and loading across up to 99 slots, including Slot 99 and dual sync."""
        world = World()
        player = Player(x=8, y=6, current_map="Pallet Town", name="Red")
        party = [Pokemon("Scyther", level=42)]
        inv = Inventory()
        inv.money = 99999
        pdx = Pokedex()
        pdx.register_caught("Scyther")

        # Save to Slot 99
        ok, msg = SaveSystem.save_game(player, party, inv, pdx, world, slot=99)
        self.assertTrue(ok)

        # Load from Slot 99
        loaded_player = Player()
        res, msg = SaveSystem.load_game(loaded_player, World(), slot=99)
        self.assertIsNotNone(res)
        l_party, l_inv, l_pdx, l_pc = res[:4]
        self.assertEqual(l_party[0].species, "Scyther")
        self.assertEqual(l_party[0].level, 42)
        self.assertEqual(l_inv.money, 99999)

        # Verify summary for Slot 99
        summary_99 = SaveSystem.get_slot_summary(99)
        self.assertIsNotNone(summary_99)
        self.assertTrue(summary_99["exists"])
        self.assertEqual(summary_99["lead_species"], "Scyther")
        self.assertEqual(summary_99["lead_level"], 42)

        # Test SaveSlotSelectScreen 99-slot scroll navigation
        from ui_menus import SaveSlotSelectScreen
        screen = SaveSlotSelectScreen(mode="LOAD", active_slot=1)
        self.assertEqual(len(screen.slots), 99)
        self.assertEqual(screen.selected_idx, 0)
        self.assertEqual(screen.scroll_offset, 0)

        # Move Down
        event_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        screen.handle_input(event_down)
        self.assertEqual(screen.selected_idx, 1)

        # Page Down Jump (+4)
        event_pgdn = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEDOWN)
        screen.handle_input(event_pgdn)
        self.assertEqual(screen.selected_idx, 5)
        self.assertGreaterEqual(screen.scroll_offset, 1)

        # End key (Jump to Slot 99)
        event_end = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_END)
        screen.handle_input(event_end)
        self.assertEqual(screen.selected_idx, 98)
        self.assertEqual(screen.scroll_offset, 95) # 99 - 4

        # Home key (Jump to Slot 1)
        event_home = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_HOME)
        screen.handle_input(event_home)
        self.assertEqual(screen.selected_idx, 0)
        self.assertEqual(screen.scroll_offset, 0)

    def test_world_movement_and_collision(self):
        world = World()
        player = Player(x=8, y=6, current_map="Pallet Town")
        # Step down onto path
        moved = player.move(Direction.DOWN, world)
        self.assertTrue(moved)
        self.assertTrue(player.is_moving)

    def test_sound_manager_synthesis(self):
        snd_mgr = SoundManager()
        self.assertIn("hit", snd_mgr.sounds)
        self.assertIn("confirm", snd_mgr.sounds)
        self.assertIn("bgm_battle", snd_mgr.sounds)

    def test_all_151_species_present_and_valid(self):
        self.assertEqual(len(POKEMON_SPECIES), 151)
        found_ids = set()
        for name, data in POKEMON_SPECIES.items():
            poke_id = data["id"]
            found_ids.add(poke_id)
            # Base stats
            for stat in ["hp", "atk", "def", "spatk", "spdef", "spd"]:
                self.assertIn(stat, data["base_stats"], f"{name} missing stat {stat}")
                self.assertGreater(data["base_stats"][stat], 0, f"{name} stat {stat} must be > 0")
            # Types
            for t in data["types"]:
                self.assertIn(t, TYPE_COLORS, f"{name} has unknown type {t}")
                self.assertIn(t, TYPE_CHART, f"{name} has unknown type in chart: {t}")
            # Learnset moves
            for lvl, moves in data.get("learnset", {}).items():
                for m in moves:
                    self.assertIn(m, MOVES, f"{name} has unknown move {m} at level {lvl}")
            # Evolution
            if data.get("evolution"):
                target = data["evolution"]["target"]
                self.assertIn(target, POKEMON_SPECIES, f"{name} evolves into unknown species {target}")

        self.assertEqual(found_ids, set(range(1, 152)), "All IDs 1 to 151 must be present")

    def test_trainer_customization_and_persistence(self):
        world = World()
        # Create customized player
        custom_player = Player(
            x=7, y=7, current_map="Viridian City",
            name="Dawn", gender="Girl", outfit_theme="Cherry Pink",
            hat_style="Beanie", hair_color="Golden Blonde"
        )
        self.assertEqual(custom_player.name, "Dawn")
        self.assertEqual(custom_player.gender, "Girl")
        self.assertEqual(custom_player.outfit_theme, "Cherry Pink")
        self.assertEqual(custom_player.hat_style, "Beanie")
        self.assertEqual(custom_player.hair_color, "Golden Blonde")

        # Save to Slot 3
        party = [Pokemon("Eevee", level=5)]
        inv = Inventory()
        pdx = Pokedex()
        pdx.register_caught("Eevee")
        ok, msg = SaveSystem.save_game(custom_player, party, inv, pdx, world, slot=3)
        self.assertTrue(ok)

        # Load from Slot 3
        loaded_player = Player()
        res, msg = SaveSystem.load_game(loaded_player, World(), slot=3)
        self.assertIsNotNone(res)
        self.assertEqual(loaded_player.name, "Dawn")
        self.assertEqual(loaded_player.gender, "Girl")
        self.assertEqual(loaded_player.outfit_theme, "Cherry Pink")
        self.assertEqual(loaded_player.hat_style, "Beanie")
        self.assertEqual(loaded_player.hair_color, "Golden Blonde")

        # Verify summary includes trainer metadata
        summary = SaveSystem.get_slot_summary(3)
        self.assertIsNotNone(summary)
        self.assertEqual(summary["trainer_name"], "Dawn")
        self.assertEqual(summary["gender"], "Girl")
        self.assertEqual(summary["outfit_theme"], "Cherry Pink")

    def test_pc_box_overflow_and_operations(self):
        # 1. Test 6-Pokemon party overflow into PC Box
        party = [
            Pokemon("Bulbasaur", level=11),
            Pokemon("Pidgey", level=6),
            Pokemon("Rattata", level=8),
            Pokemon("Weedle", level=3),
            Pokemon("Bellsprout", level=8),
            Pokemon("Oddish", level=5)
        ]
        self.assertEqual(len(party), 6)
        
        pc_box = []
        pokedex = Pokedex()
        for p in party:
            pokedex.register_caught(p.species)

        # Simulate catching 7th Pokemon (Pikachu)
        wild_pikachu = Pokemon("Pikachu", level=10)
        from battle_system import BattleSystem
        battle = BattleSystem(player_party=party, opponent_pokemon_or_trainer=wild_pikachu, is_trainer=False, pokedex=pokedex, pc_box=pc_box)
        
        # Test catch resolution when party is full
        self.assertEqual(len(party), 6)
        if len(battle.player_party) < 6:
            battle.player_party.append(wild_pikachu)
        else:
            battle.pc_box.append(wild_pikachu)
            
        self.assertEqual(len(party), 6)
        self.assertEqual(len(pc_box), 1)
        self.assertEqual(pc_box[0].species, "Pikachu")

        # 2. Test PC Box Screen Withdraw / Deposit / Swap
        from ui_manager import PCBoxScreen
        screen = PCBoxScreen(party, pc_box)
        
        # Deposit Weedle from party to PC Box
        screen.active_panel = "PARTY"
        screen.party_idx = 3 # Weedle
        screen._execute_action("DEPOSIT TO PC")
        self.assertEqual(len(party), 5)
        self.assertEqual(len(pc_box), 2)
        self.assertEqual(pc_box[-1].species, "Weedle")

        # Withdraw Pikachu to party
        screen.active_panel = "PC"
        screen.pc_idx = 0 # Pikachu
        screen._execute_action("WITHDRAW TO PARTY")
        self.assertEqual(len(party), 6)
        self.assertEqual(party[-1].species, "Pikachu")
        self.assertEqual(len(pc_box), 1)
        self.assertEqual(pc_box[0].species, "Weedle")

        # Swap Bulbasaur with Weedle
        screen.party_idx = 0 # Bulbasaur
        screen.pc_idx = 0 # Weedle
        screen._execute_action("SWAP WITH PC")
        self.assertEqual(party[0].species, "Weedle")
        self.assertEqual(pc_box[0].species, "Bulbasaur")

        # 3. Test Save/Load Persistence of PC Box
        player = Player(x=6, y=6, current_map="Pokecenter")
        inv = Inventory()
        world = World()
        ok, msg = SaveSystem.save_game(player, party, inv, pokedex, world, slot=2, pc_box=pc_box)
        self.assertTrue(ok)

        loaded_player = Player()
        res, msg = SaveSystem.load_game(loaded_player, World(), slot=2)
        self.assertIsNotNone(res)
        l_party, l_inv, l_pdx, l_pc = res[:4]
        self.assertEqual(len(l_party), 6)
        self.assertEqual(l_party[-1].species, "Pikachu")
        self.assertEqual(len(l_pc), 1)
        self.assertEqual(l_pc[0].species, "Bulbasaur")

    def test_status_move_execution_all_moves(self):
        from battle_system import BattleSystem
        bulba = Pokemon("Bulbasaur", level=11)
        rattata = Pokemon("Rattata", level=5)
        pokedex = Pokedex()
        battle = BattleSystem([bulba], rattata, is_trainer=False, pokedex=pokedex)

        # Test using Growl, Leech Seed, Tail Whip, Thunder Wave, Recover
        test_moves = ["Growl", "Leech Seed", "Tail Whip", "Thunder Wave", "Recover", "Agility"]
        for m_name in test_moves:
            if m_name in MOVES:
                move_obj = MOVES[m_name]
                battle._queue_attack(bulba, rattata, move_obj, is_player=True, next_attack=None)
                # Drain messages to trigger perform_move callback
                for _ in range(10):
                    if battle.messages or battle.on_message_complete:
                        battle.advance_message_queue()
                    else:
                        break

    def test_status_effects_rendering_and_badges(self):
        from graphics_manager import gfx
        import pygame
        surf = pygame.Surface((800, 600))
        
        statuses = ["Paralysis", "Burn", "Poison", "Sleep", "Freeze", "Fainted"]
        for st in statuses:
            p = Pokemon("Pikachu", level=10, status=st)
            sprite = gfx.get_pokemon_sprite("Pikachu", is_back=False, size=(160, 160))
            # Test status visual effects drawing on sprite
            gfx.draw_pokemon_with_status_effects(surf, p, 400, 300, sprite, anim_time=1.5, is_back=False)
            gfx.draw_pokemon_with_status_effects(surf, p, 400, 300, sprite, anim_time=2.0, is_back=True)
            # Test status badge rendering
            gfx.draw_status_badge(surf, st, 100, 100, width=44, height=18)

    def test_end_of_turn_status_damage(self):
        from battle_system import BattleSystem
        char = Pokemon("Charmander", level=10, status="Poison")
        pika = Pokemon("Pikachu", level=10, status="Burn")
        battle = BattleSystem([char], pika, is_trainer=False)
        
        initial_pika_hp = pika.current_hp
        initial_char_hp = char.current_hp
        
        battle._check_end_of_turn_status()
        # Drain player status damage animation
        battle.update(1.0)
        self.assertLess(char.current_hp, initial_char_hp)
        
        # Complete player status animation & advance message queue to trigger enemy status tick
        battle.update(0.1)
        battle.advance_message_queue()
        battle.update(1.0)
        self.assertLess(pika.current_hp, initial_pika_hp)

    def test_defeated_trainers_save_and_reload_persistence(self):
        # 1. Create a world and mark trainers as defeated
        world = World()
        self.assertEqual(len(world.defeated_trainers), 0)
        
        # Test line of sight before defeat: Joey is at (12, 14) facing DOWN
        spotted = world.check_trainer_line_of_sight("Route 1", 12, 16)
        self.assertIsNotNone(spotted)
        self.assertEqual(spotted["id"], "youngster_joey")
        
        # Mark youngster_joey and gym_leader_brock as defeated
        world.defeated_trainers.add("youngster_joey")
        world.defeated_trainers.add("gym_leader_brock")
        
        # Test line of sight after defeat: Joey should NOT spot the player
        spotted_after = world.check_trainer_line_of_sight("Route 1", 12, 16)
        self.assertIsNone(spotted_after)
        
        # 2. Save game with defeated trainers to Slot 1
        player = Player(x=8, y=6, current_map="Route 1")
        party = [Pokemon("Squirtle", level=10)]
        inv = Inventory()
        pokedex = Pokedex()
        pokedex.register_caught("Squirtle")
        
        ok, msg = SaveSystem.save_game(player, party, inv, pokedex, world, slot=1)
        self.assertTrue(ok)
        
        # 3. Reload into a fresh World instance
        loaded_player = Player()
        loaded_world = World()
        self.assertEqual(len(loaded_world.defeated_trainers), 0)
        
        res, msg = SaveSystem.load_game(loaded_player, loaded_world, slot=1)
        self.assertIsNotNone(res)
        
        # 4. Verify defeated trainers persisted into loaded world
        self.assertIn("youngster_joey", loaded_world.defeated_trainers)
        self.assertIn("gym_leader_brock", loaded_world.defeated_trainers)
        self.assertNotIn("bug_catcher_sammy", loaded_world.defeated_trainers)
        
        # 5. Verify line of sight on loaded world
        self.assertIsNone(loaded_world.check_trainer_line_of_sight("Route 1", 12, 16))
        # Sammy (6, 20 facing RIGHT) is undefeated, should spot player at (8, 20)
        sammy_spotted = loaded_world.check_trainer_line_of_sight("Route 1", 8, 20)
        self.assertIsNotNone(sammy_spotted)
        self.assertEqual(sammy_spotted["id"], "bug_catcher_sammy")


