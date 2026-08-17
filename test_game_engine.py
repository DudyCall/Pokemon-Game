"""
test_game_engine.py - Automated Headless Verification Suite for Pokemon Game Engine.
"""
import os
import sys
import unittest
import pygame

# Set headless dummy video and audio drivers for tests
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from constants import TYPE_CHART, TYPE_COLORS, Direction
from pokemon_data import POKEMON_SPECIES, MOVES, ITEMS, WILD_ENCOUNTERS, TRAINERS
from pokemon import Pokemon
from inventory import Inventory
from world import World, Player
from save_system import SaveSystem, Pokedex
from sound_manager import SoundManager
from graphics_manager import GraphicsManager

class TestPokemonEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

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
        lp1, li1, lpd1 = res1
        self.assertEqual(loaded_p1.grid_x, 5)
        self.assertEqual(loaded_p1.current_map, "Pallet Town")
        self.assertEqual(lp1[0].species, "Squirtle")
        self.assertEqual(li1.money, 5500)
        self.assertIn("Squirtle", lpd1.caught)

        # Verify Slot 2 Load
        loaded_p2 = Player()
        res2, msg = SaveSystem.load_game(loaded_p2, World(), slot=2)
        self.assertIsNotNone(res2)
        lp2, li2, lpd2 = res2
        self.assertEqual(loaded_p2.grid_x, 12)
        self.assertEqual(loaded_p2.current_map, "Route 1")
        self.assertEqual(len(lp2), 2)
        self.assertEqual(lp2[0].species, "Charmander")
        self.assertEqual(li2.money, 8200)
        self.assertIn("Charmander", lpd2.caught)
        self.assertIn("Pikachu", lpd2.caught)

        # Verify Slot summaries
        summaries = SaveSystem.get_all_slots_summary()
        self.assertEqual(len(summaries), 3)
        self.assertTrue(summaries[0]["exists"])
        self.assertEqual(summaries[0]["lead_species"], "Squirtle")
        self.assertTrue(summaries[1]["exists"])
        self.assertEqual(summaries[1]["lead_species"], "Charmander")
        self.assertEqual(summaries[1]["party_count"], 2)

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

    def test_instantiate_diverse_roster(self):
        sample_species = ["Mewtwo", "Gyarados", "Scyther", "Gengar", "Dragonite", "Snorlax", "Butterfree", "Machamp", "Zapdos"]
        for sp in sample_species:
            p = Pokemon(sp, level=50)
            self.assertEqual(p.species, sp)
            self.assertEqual(p.level, 50)
            self.assertGreater(p.max_hp, 50)
            self.assertEqual(p.current_hp, p.max_hp)
            self.assertGreaterEqual(len(p.moves), 1)

if __name__ == "__main__":
    unittest.main()
