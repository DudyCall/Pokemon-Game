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

    def test_save_and_load(self):
        world = World()
        player = Player(x=5, y=5, current_map="Pallet Town")
        party = [Pokemon("Squirtle", level=8)]
        inventory = Inventory()
        inventory.money = 5500
        pokedex = Pokedex()
        pokedex.register_caught("Squirtle")
        
        ok, msg = SaveSystem.save_game(player, party, inventory, pokedex, world)
        self.assertTrue(ok)
        
        loaded_player = Player()
        loaded_world = World()
        res, msg = SaveSystem.load_game(loaded_player, loaded_world)
        self.assertIsNotNone(res)
        l_party, l_inv, l_pokedex = res
        self.assertEqual(loaded_player.grid_x, 5)
        self.assertEqual(loaded_player.grid_y, 5)
        self.assertEqual(l_party[0].species, "Squirtle")
        self.assertEqual(l_party[0].level, 8)
        self.assertEqual(l_inv.money, 5500)
        self.assertIn("Squirtle", l_pokedex.caught)

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

    def test_graphics_manager(self):
        gfx_mgr = GraphicsManager()
        sprite = gfx_mgr.get_pokemon_sprite("Pikachu", is_back=False, size=(64, 64))
        self.assertIsNotNone(sprite)
        self.assertEqual(sprite.get_size(), (64, 64))

if __name__ == "__main__":
    unittest.main()
