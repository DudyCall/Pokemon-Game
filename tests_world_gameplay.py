"""
tests_world_gameplay.py - World & gameplay unit tests: Maps, warps, ground items,
gym badges, wild encounters, trainer card, region map, gamepad, scrolling, fog of war,
biomes, sailing, encounter props, trainer portraits, and move tutor.
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


class TestWorldGameplayMixin:
    def test_expanded_world_maps_and_warps(self):
        world = World()
        expected_maps = [
            "Pallet Town", "Route 1", "Viridian City", "Route 22", "Viridian Forest",
            "Pewter City", "Route 3", "Mt. Moon", "Route 4", "Cerulean City",
            "Route 9", "Lavender Town", "Pokémon Tower", "Power Plant", "Safari Zone",
            "Route 24", "Route 21", "Seafoam Islands", "Cinnabar Island",
            "Pokecenter", "Mart", "Oak's Lab", "Player's House", "Pewter Gym", "Cerulean Gym",
            "Bill's Cottage", "Museum"
        ]
        
        for m_name in expected_maps:
            self.assertIn(m_name, world.maps, f"Map '{m_name}' must exist in world.maps")
            grid = world.maps[m_name]["grid"]
            self.assertGreater(len(grid), 0, f"Map '{m_name}' has empty grid")
            row_len = len(grid[0])
            for r_idx, row in enumerate(grid):
                self.assertEqual(len(row), row_len, f"Map '{m_name}' row {r_idx} length mismatch ({len(row)} vs {row_len})")
                
            # Verify warps
            warps = world.maps[m_name].get("warps", {})
            for (wx, wy), wdata in warps.items():
                self.assertIn("target_map", wdata, f"Warp at ({wx}, {wy}) on {m_name} missing target_map")
                target_map = wdata["target_map"]
                self.assertIn(target_map, world.maps, f"Warp at ({wx}, {wy}) on {m_name} points to unknown map {target_map}")
                # Ensure warp source tile is passable so player can trigger it
                self.assertTrue(world.is_passable(m_name, wx, wy), f"Warp source ({wx}, {wy}) on map '{m_name}' is not passable! Tile: '{world.get_tile(m_name, wx, wy)}'")
                # Ensure warp target destination tile is passable
                tx, ty = wdata["target_x"], wdata["target_y"]
                self.assertTrue(world.is_passable(target_map, tx, ty), f"Warp destination ({tx}, {ty}) on map '{target_map}' from '{m_name}' is not passable! Tile: '{world.get_tile(target_map, tx, ty)}'")

    def test_route_22_viridian_city_transitions(self):
        world = World()
        # Test Viridian City -> Route 22 warps
        v_warps = world.maps["Viridian City"]["warps"]
        self.assertIn((0, 11), v_warps)
        self.assertEqual(v_warps[(0, 11)]["target_map"], "Route 22")
        self.assertEqual(v_warps[(0, 11)]["target_x"], 26)
        self.assertEqual(v_warps[(0, 11)]["target_y"], 8)
        
        # Test Route 22 -> Viridian City warps and exits
        r22_warps = world.maps["Route 22"]["warps"]
        self.assertIn((27, 8), r22_warps)
        self.assertIn((27, 9), r22_warps)
        self.assertIn((27, 10), r22_warps)
        self.assertEqual(r22_warps[(27, 8)]["target_map"], "Viridian City")
        self.assertEqual(r22_warps[(27, 8)]["target_x"], 1)
        self.assertEqual(r22_warps[(27, 8)]["target_y"], 11)
        
        # Ensure (27, 8), (27, 9), (27, 10) are walkable
        self.assertTrue(world.is_passable("Route 22", 27, 8))
        self.assertTrue(world.is_passable("Route 22", 27, 9))
        self.assertTrue(world.is_passable("Route 22", 27, 10))

    def test_ground_items_and_signs(self):
        world = World()
        # Test item lookup
        item_data = world.get_ground_item_at("Pallet Town", 3, 7)
        self.assertIsNotNone(item_data)
        self.assertEqual(item_data["item"], "Potion")
        
        # Test item collection
        world.collected_items.add(item_data["id"])
        self.assertIsNone(world.get_ground_item_at("Pallet Town", 3, 7))
        
        # Test sign lookup
        sign_txt = world.get_sign_at("Pallet Town", 3, 10)
        self.assertIsNotNone(sign_txt)
        self.assertIn("Pallet Town", sign_txt)

    def test_gym_badges_and_trainers(self):
        world = World()
        # Leader Brock
        brock = [t for t in TRAINERS if t["id"] == "gym_leader_brock"][0]
        self.assertEqual(brock["reward_badge"], "Boulder Badge")
        self.assertEqual(brock["map"], "Pewter Gym")
        
        # Leader Misty
        misty = [t for t in TRAINERS if t["id"] == "gym_leader_misty"][0]
        self.assertEqual(misty["reward_badge"], "Cascade Badge")
        self.assertEqual(misty["map"], "Cerulean Gym")
        
        # Badge persistence
        world.badges.add("Boulder Badge")
        world.badges.add("Cascade Badge")
        
        player = Player(current_map="Pewter City")
        party = [Pokemon("Charmander", level=18)]
        inv = Inventory()
        pdx = Pokedex()
        
        SaveSystem.save_game(player, party, inv, pdx, world, slot=1)
        
        loaded_world = World()
        SaveSystem.load_game(Player(), loaded_world, slot=1)
        self.assertIn("Boulder Badge", loaded_world.badges)
        self.assertIn("Cascade Badge", loaded_world.badges)

    def test_all_wild_encounter_zones(self):
        for zone_name, encounters in WILD_ENCOUNTERS.items():
            self.assertGreater(len(encounters), 0, f"Zone '{zone_name}' has no encounters")
            for enc in encounters:
                species = enc["species"]
                self.assertIn(species, POKEMON_SPECIES, f"Unknown species '{species}' in encounter zone '{zone_name}'")
                self.assertLessEqual(enc["min_lvl"], enc["max_lvl"], f"Min level > Max level for '{species}' in '{zone_name}'")
                self.assertGreater(enc["weight"], 0, f"Weight must be > 0 for '{species}' in '{zone_name}'")

    def test_trainer_card_and_region_map_screen(self):
        from ui_manager import TrainerCardScreen, PauseMenu
        player = Player(x=8, y=6, current_map="Viridian City")
        world = World()
        world.badges.add("Boulder Badge")
        world.explored_tiles["Pallet Town"] = {(8, 6), (9, 6), (10, 6)}
        inv = Inventory()
        pdx = Pokedex()
        
        # Test PauseMenu option
        pause_menu = PauseMenu()
        self.assertIn("MAP", pause_menu.options)
        
        screen = TrainerCardScreen(player, world, inv, pdx, initial_tab=0)
        self.assertEqual(screen.active_tab, 0)
        
        # Switch tab to Exploration Map
        event_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        screen.handle_input(event_right)
        self.assertEqual(screen.active_tab, 1)
        
        # Test spatial navigation
        initial_node = screen.map_nodes[screen.selected_node_idx]
        event_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        screen.handle_input(event_up)
        # Verify node has gx and gy
        self.assertIn("gx", screen.map_nodes[screen.selected_node_idx])
        self.assertIn("gy", screen.map_nodes[screen.selected_node_idx])

        surf = pygame.Surface((800, 600))
        # Test draw all nodes (visited and unvisited) without crash
        for node_idx in range(len(screen.map_nodes)):
            screen.selected_node_idx = node_idx
            screen.draw(surf)

    def test_gpad_button_to_key(self):
        from input_manager import button_to_key, GPAD_CONFIRM, GPAD_CANCEL, GPAD_START, GPAD_SELECT
        self.assertEqual(button_to_key(GPAD_CONFIRM), KEY_CONFIRM[0])
        self.assertEqual(button_to_key(GPAD_CANCEL), KEY_CANCEL[0])
        self.assertEqual(button_to_key(GPAD_START), KEY_MENU[0])
        self.assertEqual(button_to_key(GPAD_SELECT), KEY_QUICKSAVE[0])
        self.assertIsNone(button_to_key(2))  # X unused
        self.assertIsNone(button_to_key(99))

    def test_gpad_hat_and_stick_deadzone(self):
        from input_manager import hat_to_direction, stick_to_direction, STICK_DEADZONE
        self.assertEqual(hat_to_direction(0, 1), Direction.UP)
        self.assertEqual(hat_to_direction(0, -1), Direction.DOWN)
        self.assertEqual(hat_to_direction(-1, 0), Direction.LEFT)
        self.assertEqual(hat_to_direction(1, 0), Direction.RIGHT)
        self.assertIsNone(hat_to_direction(0, 0))
        self.assertEqual(hat_to_direction(1, 1), Direction.UP)  # up/down beat left/right

        self.assertIsNone(stick_to_direction(0.0, 0.0))
        self.assertIsNone(stick_to_direction(STICK_DEADZONE - 0.01, 0.0))
        self.assertIsNone(stick_to_direction(0.0, STICK_DEADZONE - 0.01))
        self.assertEqual(stick_to_direction(0.0, -0.8), Direction.UP)
        self.assertEqual(stick_to_direction(0.0, 0.8), Direction.DOWN)
        self.assertEqual(stick_to_direction(-0.8, 0.0), Direction.LEFT)
        self.assertEqual(stick_to_direction(0.8, 0.0), Direction.RIGHT)
        # Dominant axis wins on diagonals
        self.assertEqual(stick_to_direction(0.4, -0.9), Direction.UP)
        self.assertEqual(stick_to_direction(0.9, -0.4), Direction.RIGHT)

    def test_gpad_direction_repeat(self):
        from input_manager import InputManager, REPEAT_DELAY, REPEAT_RATE, direction_to_key, make_keydown
        mgr = InputManager()
        first = mgr._update_repeat(Direction.UP, 0.0)
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0].type, pygame.KEYDOWN)
        self.assertEqual(first[0].key, KEY_UP[0])
        self.assertEqual(mgr.get_held_directions(), {Direction.UP})

        none_yet = mgr._update_repeat(Direction.UP, REPEAT_DELAY - 0.05)
        self.assertEqual(none_yet, [])

        delayed = mgr._update_repeat(Direction.UP, 0.05)
        self.assertEqual(len(delayed), 1)
        self.assertEqual(delayed[0].key, KEY_UP[0])

        none_rate = mgr._update_repeat(Direction.UP, REPEAT_RATE - 0.01)
        self.assertEqual(none_rate, [])
        pulsed = mgr._update_repeat(Direction.UP, 0.02)
        self.assertEqual(len(pulsed), 1)

        switched = mgr._update_repeat(Direction.LEFT, 0.0)
        self.assertEqual(len(switched), 1)
        self.assertEqual(switched[0].key, KEY_LEFT[0])
        self.assertEqual(mgr.get_held_directions(), {Direction.LEFT})

        released = mgr._update_repeat(None, 0.0)
        self.assertEqual(released, [])
        self.assertEqual(mgr.get_held_directions(), set())

        evt = make_keydown(KEY_CONFIRM[0])
        self.assertEqual(evt.type, pygame.KEYDOWN)
        self.assertEqual(evt.key, KEY_CONFIRM[0])
        self.assertEqual(direction_to_key(Direction.DOWN), KEY_DOWN[0])
        self.assertEqual(direction_to_key(Direction.RIGHT), KEY_RIGHT[0])

    def test_battle_party_and_bag_scrolling(self):
        from battle_system import BattleSystem, BattlePhase
        # Setup party with 6 Pokemon
        party = [
            Pokemon("Pikachu", level=10),
            Pokemon("Charmander", level=10),
            Pokemon("Squirtle", level=10),
            Pokemon("Bulbasaur", level=10),
            Pokemon("Pidgey", level=10),
            Pokemon("Rattata", level=10),
        ]
        inv = Inventory()
        # Ensure inventory has 6 items
        inv.items = {
            "Poke Ball": 5,
            "Great Ball": 3,
            "Ultra Ball": 2,
            "Potion": 4,
            "Super Potion": 2,
            "Revive": 1,
            "Antidote": 3,
        }
        enemy = Pokemon("Caterpie", level=3)
        battle = BattleSystem(player_party=party, opponent_pokemon_or_trainer=enemy, is_trainer=False, inventory=inv)

        # 1. Test Party selection scrolling
        battle.phase = BattlePhase.PARTY_SELECT
        battle.party_menu_index = 0
        battle.party_scroll = 0
        
        down_event = pygame.event.Event(pygame.KEYDOWN, key=KEY_DOWN[0])
        up_event = pygame.event.Event(pygame.KEYDOWN, key=KEY_UP[0])
        
        # Navigate down from 0 to 3 -> scroll should stay 0
        for i in range(1, 4):
            battle.handle_input(down_event)
            self.assertEqual(battle.party_menu_index, i)
            self.assertEqual(battle.party_scroll, 0)
            
        # Navigate down to index 4 -> scroll should become 1
        battle.handle_input(down_event)
        self.assertEqual(battle.party_menu_index, 4)
        self.assertEqual(battle.party_scroll, 1)

        # Navigate down to index 5 -> scroll should become 2
        battle.handle_input(down_event)
        self.assertEqual(battle.party_menu_index, 5)
        self.assertEqual(battle.party_scroll, 2)

        # Wrap around down to index 0 -> scroll should adjust to 0
        battle.handle_input(down_event)
        self.assertEqual(battle.party_menu_index, 0)
        self.assertEqual(battle.party_scroll, 0)

        # Wrap around up to index 5 -> scroll should adjust to 2
        battle.handle_input(up_event)
        self.assertEqual(battle.party_menu_index, 5)
        self.assertEqual(battle.party_scroll, 2)

        # Test battle draw in party select mode
        surf = pygame.Surface((800, 600))
        battle.draw(surf)

        # 2. Test Bag selection scrolling
        battle.phase = BattlePhase.BAG_SELECT
        battle.bag_index = 0
        battle.bag_scroll = 0
        total_items = len(inv.get_items_list())
        self.assertGreater(total_items, 4)

        # Navigate down to 4
        for _ in range(4):
            battle.handle_input(down_event)
        self.assertEqual(battle.bag_index, 4)
        self.assertEqual(battle.bag_scroll, 1)

        # Test battle draw in bag select mode
        battle.draw(surf)

    def test_mt_moon_and_all_map_passability(self):
        world = World()
        player = Player(x=1, y=21, current_map="Mt. Moon")

        # Verify Mt. Moon entrance at (1, 21) can move right
        self.assertTrue(world.is_passable("Mt. Moon", 2, 21), "Mt. Moon entrance (1, 21) right tile (2, 21) must be passable")
        self.assertTrue(player.move(Direction.RIGHT, world))
        player.update(1.0, world)
        self.assertEqual((player.grid_x, player.grid_y), (2, 21))

        # Verify Mt. Moon exit at (30, 2) can move left
        self.assertTrue(world.is_passable("Mt. Moon", 30, 2), "Mt. Moon exit (30, 2) must be passable")
        self.assertTrue(world.is_passable("Mt. Moon", 29, 2), "Mt. Moon exit left tile (29, 2) must be passable")

        # Verify all map trainers and ground items are on passable tiles
        for map_name, map_data in world.maps.items():
            for item in map_data.get("ground_items", []):
                self.assertTrue(
                    world.is_passable(map_name, item["x"], item["y"]),
                    f"Ground item '{item['id']}' in '{map_name}' is on an impassable tile ({item['x']}, {item['y']})"
                )

    def test_fog_of_war_minimap(self):
        world = World()
        player = Player(x=8, y=6, current_map="Pallet Town")
        
        # Initial reveal
        world.reveal_area("Pallet Town", 8, 6, radius=3)
        self.assertIn("Pallet Town", world.explored_tiles)
        self.assertIn((8, 6), world.explored_tiles["Pallet Town"])
        self.assertIn((7, 6), world.explored_tiles["Pallet Town"])
        self.assertIn((9, 6), world.explored_tiles["Pallet Town"])
        
        # Test minimap rendering on multiple map types
        surf = pygame.Surface((800, 600))
        world.draw_minimap(surf, "Pallet Town", player.grid_x, player.grid_y)
        world.draw_minimap(surf, "Mt. Moon", 1, 21)
        world.draw_minimap(surf, "Viridian Forest", 16, 30)
        world.draw_minimap(surf, "Pokecenter", 6, 6)

        # Test save & load of explored_tiles
        party = [Pokemon("Pikachu", level=10)]
        inv = Inventory()
        pdx = Pokedex()
        world.explored_tiles["Mt. Moon"] = {(1, 21), (2, 21), (3, 21)}
        SaveSystem.save_game(player, party, inv, pdx, world, slot=1)

        loaded_world = World()
        SaveSystem.load_game(Player(), loaded_world, slot=1)
        self.assertIn("Mt. Moon", loaded_world.explored_tiles)
        self.assertIn((1, 21), loaded_world.explored_tiles["Mt. Moon"])
        self.assertIn((2, 21), loaded_world.explored_tiles["Mt. Moon"])

    def test_new_biomes_and_maps(self):
        world = World()
        new_maps = ["Route 9", "Lavender Town", "Pokémon Tower", "Power Plant", "Safari Zone", "Seafoam Islands"]
        
        # Test all new maps exist and render properly
        surf = pygame.Surface((800, 600))
        for m_name in new_maps:
            self.assertIn(m_name, world.maps)
            grid = world.maps[m_name]["grid"]
            self.assertGreater(len(grid), 0)
            
            # Test draw and minimap for each new map
            world.draw(surf, m_name, 0, 0)
            world.draw_minimap(surf, m_name, 5, 5)
            
            # Test encounter table
            enc_zone = world.maps[m_name].get("encounter_zone")
            self.assertIn(enc_zone, WILD_ENCOUNTERS)
            self.assertGreater(len(WILD_ENCOUNTERS[enc_zone]), 0)

        # Test new trainers exist and are valid
        new_trainer_ids = [
            "camper_drew", "picnicker_alicia", "hiker_alan",
            "channeler_patricia", "channeler_carly", "channeler_hope",
            "scientist_bray", "pokemaniac_mark", "engineer_bucky",
            "skier_dianne", "boarder_felix"
        ]
        registered_trainer_ids = {t["id"] for t in TRAINERS}
        for tid in new_trainer_ids:
            self.assertIn(tid, registered_trainer_ids, f"Trainer '{tid}' not found in TRAINERS list")
            t_data = [t for t in TRAINERS if t["id"] == tid][0]
            self.assertGreater(len(t_data["party"]), 0)
            for p_member in t_data["party"]:
                self.assertIn(p_member["species"], POKEMON_SPECIES)
                self.assertGreater(p_member["level"], 0)

        # Test custom procedural biome textures exist in gfx.cached_tiles
        expected_tiles = [
            "ice_floor", "ice_wall", "ice_door",
            "lavender_ground", "spooky_floor", "tombstone", "spooky_tree",
            "metal_floor", "generator_coil", "warning_tile",
            "savanna_grass", "savanna_tall_grass", "acacia_tree",
            "canyon_dirt", "canyon_rock"
        ]
        for t_name in expected_tiles:
            self.assertIn(t_name, gfx.cached_tiles, f"Tile '{t_name}' missing from gfx.cached_tiles")

    def test_boat_sailing_and_water_mechanics(self):
        world = World()
        player = Player(x=9, y=3, current_map="Route 21") # Bridge tile
        
        # Test water collision with can_sail flag
        # (8, 3) is water (~)
        tile_water = world.get_tile("Route 21", 8, 3)
        self.assertEqual(tile_water, "~")
        self.assertFalse(world.is_passable("Route 21", 8, 3, can_sail=False))
        self.assertTrue(world.is_passable("Route 21", 8, 3, can_sail=True))
        
        # Test player boarding boat by moving onto water
        self.assertFalse(player.is_sailing)
        self.assertTrue(player.has_boat)
        player.move(Direction.LEFT, world)
        self.assertTrue(player.is_moving)
        self.assertEqual(player.target_x, 8)
        
        # Finish step
        player.update(0.5, world)
        self.assertFalse(player.is_moving)
        self.assertTrue(player.is_sailing, "Player should be sailing after stepping onto water")
        
        # Test drawing player on boat without error
        surf = pygame.Surface((800, 600))
        for d in [Direction.DOWN, Direction.UP, Direction.LEFT, Direction.RIGHT]:
            player.facing = d
            player.draw(surf, 0, 0)
            self.assertIn(d, gfx.boat_sprites)
            self.assertIsInstance(gfx.boat_sprites[d], pygame.Surface)

        # Test disembarking boat onto land
        # Move from water (8, 3) back right to bridge (9, 3)
        player.move(Direction.RIGHT, world)
        player.update(0.5, world)
        self.assertFalse(player.is_sailing, "Player should disembark when moving onto land")

        # Test water wild encounters
        self.assertGreater(len(WILD_WATER_ENCOUNTERS), 0)
        for zone_name, encounters in WILD_WATER_ENCOUNTERS.items():
            self.assertGreater(len(encounters), 0, f"Water zone '{zone_name}' has empty encounter table")
            for enc in encounters:
                species = enc["species"]
                self.assertIn(species, POKEMON_SPECIES, f"Unknown species '{species}' in water zone '{zone_name}'")
                self.assertLessEqual(enc["min_lvl"], enc["max_lvl"])
                self.assertGreater(enc["weight"], 0)

        # Test Save & Load of boat status
        party = [Pokemon("Lapras", level=20)]
        inv = Inventory()
        pdx = Pokedex()
        player.is_sailing = True
        player.grid_x, player.grid_y = 8, 3
        SaveSystem.save_game(player, party, inv, pdx, world, slot=1)
        
        loaded_player = Player()
        loaded_world = World()
        SaveSystem.load_game(loaded_player, loaded_world, slot=1)
        self.assertTrue(loaded_player.has_boat)
        self.assertTrue(loaded_player.is_sailing)

    def test_walk_through_encounter_props(self):
        from constants import ENCOUNTER_PROP_TILES
        from pokemon_data import WILD_PROP_ENCOUNTERS, get_wild_encounters_for_prop
        world = World()
        player = Player(x=8, y=6, current_map="Pallet Town")
        
        # 1. Verify ENCOUNTER_PROP_TILES registry completeness
        expected_props = ['G', 'F', '*', 'L', 'r', 'x', 'm', 'a', 'u', 'e']
        for p_code in expected_props:
            self.assertIn(p_code, ENCOUNTER_PROP_TILES, f"Prop '{p_code}' missing from ENCOUNTER_PROP_TILES")
            info = ENCOUNTER_PROP_TILES[p_code]
            self.assertIn("name", info)
            self.assertIn("sfx", info)
            self.assertIn("minimap_color", info)

        # 2. Verify all prop tiles exist in gfx.cached_tiles and gfx.prop_overlays
        expected_tiles = [
            "tall_grass", "flower_meadow", "flower_red", "leaf_pile",
            "cave_rubble", "snow_drift", "spooky_mist", "volcanic_ash",
            "swamp_marsh", "electric_surge"
        ]
        for t_name in expected_tiles:
            self.assertIn(t_name, gfx.cached_tiles, f"Cached tile '{t_name}' missing from gfx")
            self.assertIsInstance(gfx.cached_tiles[t_name], pygame.Surface)

        for p_code in expected_props:
            self.assertIn(p_code, gfx.prop_overlays, f"Prop overlay '{p_code}' missing from gfx")
            self.assertIsInstance(gfx.prop_overlays[p_code], pygame.Surface)

        # 3. Verify all procedural step sounds are generated
        for p_code in expected_props:
            sfx_name = ENCOUNTER_PROP_TILES[p_code]["sfx"]
            self.assertIn(sfx_name, sound_mgr.sounds, f"Step SFX '{sfx_name}' missing from sound_mgr")
            # Verify playing SFX does not error
            sound_mgr.play_sfx(sfx_name)

        # 4. Verify player detection and foot immersion overlay rendering on each prop
        surf = pygame.Surface((800, 600))
        for p_code in expected_props:
            player.current_prop = p_code
            player.in_tall_grass = True
            player.is_moving = False
            player.draw(surf, 0, 0)
            self.assertEqual(player.current_prop, p_code)

        # 5. Verify passability across maps containing new props
        # Route 1: (3, 2) is F (Wildflower), (3, 4) is L (Leaf pile)
        self.assertEqual(world.get_tile("Route 1", 3, 2), "G")
        self.assertEqual(world.get_tile("Route 1", 13, 2), "F")
        self.assertTrue(world.is_passable("Route 1", 13, 2))
        self.assertEqual(world.get_tile("Route 1", 3, 4), "L")
        self.assertTrue(world.is_passable("Route 1", 3, 4))
        
        # Route 22: (6, 5) is u (Swamp marsh), (18, 3) is r (Cave rubble)
        self.assertEqual(world.get_tile("Route 22", 6, 5), "u")
        self.assertTrue(world.is_passable("Route 22", 6, 5))
        self.assertEqual(world.get_tile("Route 22", 18, 3), "r")
        self.assertTrue(world.is_passable("Route 22", 18, 3))

        # Mt. Moon: (6, 3) is r (Cave rubble), (19, 3) is e (Electric surge / crystal)
        self.assertEqual(world.get_tile("Mt. Moon", 6, 3), "r")
        self.assertTrue(world.is_passable("Mt. Moon", 6, 3))
        self.assertEqual(world.get_tile("Mt. Moon", 19, 3), "e")
        self.assertTrue(world.is_passable("Mt. Moon", 19, 3))

        # Seafoam Islands: (6, 3) is x (Deep snow drift)
        self.assertEqual(world.get_tile("Seafoam Islands", 6, 3), "x")
        self.assertTrue(world.is_passable("Seafoam Islands", 6, 3))

        # Pokémon Tower: (6, 3) is m (Haunted mist)
        self.assertEqual(world.get_tile("Pokémon Tower", 6, 3), "m")
        self.assertTrue(world.is_passable("Pokémon Tower", 6, 3))

        # Cinnabar Island: (6, 15) is a (Volcanic ash)
        self.assertEqual(world.get_tile("Cinnabar Island", 6, 15), "a")
        self.assertTrue(world.is_passable("Cinnabar Island", 6, 15))

        # 6. Verify WILD_PROP_ENCOUNTERS database integrity
        for zone_name, props_dict in WILD_PROP_ENCOUNTERS.items():
            for p_code, encounters in props_dict.items():
                self.assertIn(p_code, ENCOUNTER_PROP_TILES, f"Unknown prop '{p_code}' in WILD_PROP_ENCOUNTERS['{zone_name}']")
                self.assertGreater(len(encounters), 0, f"Empty encounters for '{p_code}' in '{zone_name}'")
                for enc in encounters:
                    species = enc["species"]
                    self.assertIn(species, POKEMON_SPECIES, f"Unknown species '{species}' in prop '{p_code}' of '{zone_name}'")
                    self.assertLessEqual(enc["min_lvl"], enc["max_lvl"])
                    self.assertGreater(enc["weight"], 0)

        # 7. Verify get_wild_encounters_for_prop resolution
        table_flower = get_wild_encounters_for_prop("Route 1", "F")
        self.assertGreater(len(table_flower), 0)
        self.assertTrue(any(e["species"] == "Butterfree" for e in table_flower))

        table_ash = get_wild_encounters_for_prop("Cinnabar Island", "a")
        self.assertGreater(len(table_ash), 0)
        self.assertTrue(any(e["species"] == "Magmar" for e in table_ash))

        table_mist = get_wild_encounters_for_prop("Pokémon Tower", "m")
        self.assertGreater(len(table_mist), 0)
        self.assertTrue(any(e["species"] == "Gastly" for e in table_mist))

        table_spark = get_wild_encounters_for_prop("Power Plant", "e")
        self.assertGreater(len(table_spark), 0)
        self.assertTrue(any(e["species"] == "Voltorb" for e in table_spark))

        table_snow = get_wild_encounters_for_prop("Seafoam Islands", "x")
        self.assertGreater(len(table_snow), 0)
        self.assertTrue(any(e["species"] == "Seel" for e in table_snow))

        # 8. Test drawing world and minimap across all maps with new props
        all_maps = list(world.maps.keys())
        for m_name in all_maps:
            world.draw(surf, m_name, 0, 0)
            world.draw_minimap(surf, m_name, 5, 5)

    def test_trainer_portraits_and_pre_battle_dialogue(self):
        from ui_manager import DialogueBox
        surf = pygame.Surface((800, 600))
        
        # 1. Test portrait generation for every registered trainer
        for t in TRAINERS:
            t_id = t["id"]
            # Idle portrait
            p_idle = gfx.get_trainer_portrait(t_id, size=(96, 96), is_talking=False)
            self.assertIsInstance(p_idle, pygame.Surface)
            self.assertEqual(p_idle.get_size(), (96, 96))
            
            # Talking animated portrait
            p_talk = gfx.get_trainer_portrait(t_id, size=(96, 96), is_talking=True)
            self.assertIsInstance(p_talk, pygame.Surface)
            self.assertEqual(p_talk.get_size(), (96, 96))

        # 2. Test NPC and Special Portraits
        npc_keys = ["Nurse Joy", "Prof. Oak", "Bill", "Mom", "Mart Clerk", "Museum Scientist", "item", "sign"]
        for key in npc_keys:
            p_surf = gfx.get_trainer_portrait(key, size=(96, 96))
            self.assertIsInstance(p_surf, pygame.Surface)
            self.assertEqual(p_surf.get_size(), (96, 96))

        # 3. Test DialogueBox functionality with trainer portrait
        joey = [t for t in TRAINERS if t["id"] == "youngster_joey"][0]
        battle_started = []
        
        def on_battle_trigger():
            battle_started.append(True)

        diag = DialogueBox(
            joey["name"],
            joey["dialog_before"],
            on_complete=on_battle_trigger,
            portrait_key=joey["id"],
            trainer_data=joey
        )

        self.assertEqual(diag.speaker, "Youngster Joey")
        self.assertEqual(diag.portrait_key, "youngster_joey")
        self.assertFalse(diag.finished)
        self.assertEqual(diag.visible_chars, 0)

        # Update dialogue typing
        diag.update(0.5)
        self.assertGreater(diag.visible_chars, 0)
        self.assertFalse(diag.finished)

        # Draw dialogue window with portrait
        diag.draw(surf)

        # Confirm to finish text instantly
        event_confirm = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)
        done = diag.handle_input(event_confirm)
        self.assertFalse(done) # First confirm completes typewriter text
        self.assertTrue(diag.finished)
        self.assertEqual(diag.visible_chars, len(joey["dialog_before"]))
        self.assertEqual(len(battle_started), 0)

        # Second confirm triggers on_complete callback (battle launch)
        diag.draw(surf)
        done = diag.handle_input(event_confirm)
        self.assertTrue(done)
        self.assertEqual(len(battle_started), 1)

        # 4. Test Gym Leader and Team Rocket badge headers
        brock = [t for t in TRAINERS if t["id"] == "gym_leader_brock"][0]
        diag_brock = DialogueBox(brock["name"], brock["dialog_before"], portrait_key=brock["id"])
        diag_brock.draw(surf)

        rocket = [t for t in TRAINERS if t["id"] == "rocket_grunt_1"][0]
        diag_rocket = DialogueBox(rocket["name"], rocket["dialog_before"], portrait_key=rocket["id"])
        diag_rocket.draw(surf)

    def test_pokemon_move_reroll_and_tutor_system(self):
        from ui_manager import MoveRerollScreen
        from world import World
        surf = pygame.Surface((800, 600))
        
        # 1. Test get_rerollable_moves for various species
        charmander = Pokemon("Charmander", level=10)
        c_moves = charmander.get_rerollable_moves()
        self.assertGreater(len(c_moves), 0)
        # Should not contain currently known moves
        known = {m["name"] for m in charmander.moves}
        for km in known:
            self.assertNotIn(km, c_moves)
            
        # 2. Test reroll_move when having < 4 moves
        charmander.moves = [charmander.create_move_slot("Scratch")]
        ok, new_m, old_m, msg = charmander.reroll_move(specific_move="Flamethrower")
        self.assertTrue(ok)
        self.assertEqual(new_m, "Flamethrower")
        self.assertIsNone(old_m)
        self.assertEqual(len(charmander.moves), 2)
        self.assertEqual(charmander.moves[1]["name"], "Flamethrower")

        # 3. Test reroll_move when having 4 moves (replacing slot 1)
        charmander.moves = [
            charmander.create_move_slot("Scratch"),
            charmander.create_move_slot("Growl"),
            charmander.create_move_slot("Ember"),
            charmander.create_move_slot("Dragon Breath")
        ]
        ok, new_m, old_m, msg = charmander.reroll_move(replace_idx=1, specific_move="Fire Blast")
        self.assertTrue(ok)
        self.assertEqual(new_m, "Fire Blast")
        self.assertEqual(old_m, "Growl")
        self.assertEqual(len(charmander.moves), 4)
        self.assertEqual(charmander.moves[1]["name"], "Fire Blast")

        # 4. Test Move Master NPC in Pokecenter
        w = World()
        pc_npcs = w.maps["Pokecenter"]["npcs"]
        move_master = [n for n in pc_npcs if n.get("name") == "Move Master"]
        self.assertEqual(len(move_master), 1)
        self.assertTrue(move_master[0].get("is_move_tutor"))

        # 5. Test Move Reroll Disk item in ITEMS and Inventory usage
        self.assertIn("Move Reroll Disk", ITEMS)
        self.assertEqual(ITEMS["Move Reroll Disk"]["price"], 3000)

        inv = Inventory()
        inv.money = 10000
        inv.add_item("Move Reroll Disk", 1)
        ok, msg = inv.use_item_on_pokemon("Move Reroll Disk", charmander)
        self.assertTrue(ok)
        self.assertEqual(inv.get_count("Move Reroll Disk"), 0)

        # 6. Test MoveRerollScreen navigation and 3000 coin transactions
        screen = MoveRerollScreen([charmander], inv)
        self.assertEqual(screen.cost, 3000)
        
        # Test Drawing UI
        screen.draw(surf)
        
        # Test Random Reroll ($3,000)
        initial_money = inv.money
        # Press Confirm on option 0 (Random Reroll)
        event_confirm = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)
        screen.handle_input(event_confirm)
        
        # If 4 moves, screen enters REPLACE_SLOT mode
        self.assertEqual(screen.mode, "REPLACE_SLOT")
        self.assertIsNotNone(screen.pending_move)
        
        # Select slot 0 to replace
        screen.handle_input(event_confirm)
        self.assertEqual(screen.mode, "MENU")
        self.assertEqual(inv.money, initial_money - 3000)
        
        # Test Catalogue Mode
        event_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        screen.handle_input(event_down) # Highlight option 1 (Catalogue)
        screen.handle_input(event_confirm) # Enter Catalogue
        self.assertEqual(screen.mode, "CATALOGUE")
        screen.draw(surf)
        
        # Cancel back to Menu
        event_cancel = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x)
        screen.handle_input(event_cancel)
        self.assertEqual(screen.mode, "MENU")

        # Test Insufficient Funds ($0 balance)
        inv.money = 500
        screen.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)) # Back to Random Reroll
        screen.handle_input(event_confirm)
        self.assertEqual(screen.mode, "MENU")
        self.assertIn("You need 3000 coins", screen.message)
        self.assertEqual(inv.money, 500) # No money deducted

    def test_item_explanations_and_bag_screen(self):
        from ui_manager import BagScreen, ShopScreen
        from battle_system import BattleSystem, BattlePhase
        surf = pygame.Surface((800, 600))
        
        # 1. Verify every item in ITEMS has full explanations and metadata
        self.assertGreater(len(ITEMS), 10)
        for item_name, data in ITEMS.items():
            self.assertIn("name", data, f"{item_name} missing name")
            self.assertIn("category", data, f"{item_name} missing category")
            self.assertIn("desc", data, f"{item_name} missing explanation desc")
            self.assertGreater(len(data["desc"]), 10, f"{item_name} explanation desc is too short")
            self.assertIn("usage", data, f"{item_name} missing usage instructions")
            self.assertGreater(len(data["usage"]), 5, f"{item_name} usage is too short")
            self.assertIn("price", data, f"{item_name} missing price")

        # 2. Test evolution stone item usage (e.g. Eevee -> Flareon with Fire Stone)
        eevee = Pokemon("Eevee", level=20)
        inv = Inventory()
        inv.add_item("Fire Stone", 1)
        inv.add_item("Burn Heal", 1)
        inv.add_item("Potion", 5)

        # Test Evolution Stone
        ok, msg = inv.use_item_on_pokemon("Fire Stone", eevee)
        self.assertTrue(ok)
        self.assertEqual(eevee.species, "Flareon")
        self.assertEqual(inv.get_count("Fire Stone"), 0)

        # Test Incompatible Stone
        inv.add_item("Water Stone", 1)
        ok, msg = inv.use_item_on_pokemon("Water Stone", eevee) # Flareon cannot evolve with Water Stone
        self.assertFalse(ok)
        self.assertIn("isn't affected", msg)

        # Test Burn Heal
        eevee.status = "Burn"
        ok, msg = inv.use_item_on_pokemon("Burn Heal", eevee)
        self.assertTrue(ok)
        self.assertIsNone(eevee.status)

        # 3. Test BagScreen navigation, category filtering, and drawing
        bag = BagScreen([eevee], inv)
        self.assertEqual(bag.mode, "BAG")
        
        # Draw Bag Screen
        bag.draw(surf)
        
        # Switch category tab (Right arrow)
        bag.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
        self.assertEqual(bag.category_idx, 1)
        bag.draw(surf)
        
        # Switch back to ALL tab
        bag.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
        self.assertEqual(bag.category_idx, 0)
        
        # Test item usage flow in BagScreen (Using Potion on damaged Pokemon)
        eevee.current_hp = 10
        potion_idx = [i for i, (n, c, d) in enumerate(bag.get_filtered_items()) if n == "Potion"][0]
        bag.selected_idx = potion_idx
        
        # Press Confirm to enter USE_TARGET mode
        bag.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        self.assertEqual(bag.mode, "USE_TARGET")
        bag.draw(surf) # Verify target selection overlay draws
        
        # Confirm target Pokemon 0
        bag.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
        self.assertEqual(bag.mode, "BAG")
        self.assertGreater(eevee.current_hp, 10) # Potion healed 20 HP
        
        # 4. Test In-Battle Bag Select Item Explanation Card
        wild_pidgey = Pokemon("Pidgey", level=3)
        battle = BattleSystem([eevee], wild_pidgey, is_trainer=False, inventory=inv)
        battle.phase = BattlePhase.BAG_SELECT
        battle.bag_index = 0
        battle._draw_bottom_panel(surf) # Must draw item selector and live explanation card without error

    def test_expanded_world_maps_and_gym_leaders(self):
        from world import MAP_DEFINITIONS, World, Player
        from ui_manager import TrainerCardScreen
        from save_system import Pokedex
        surf = pygame.Surface((800, 600))
        
        # 1. Test MAP_DEFINITIONS integrity
        expected_new_maps = [
            "Route 5", "Route 6", "Vermilion City", "Vermilion Gym", "S.S. Anne",
            "Route 11", "Diglett's Cave", "Route 7", "Route 8", "Celadon City",
            "Celadon Gym", "Saffron City", "Saffron Gym", "Silph Co.", "Route 12",
            "Fuchsia City", "Fuchsia Gym", "Victory Road", "Indigo Plateau", "Cerulean Cave"
        ]
        for m_name in expected_new_maps:
            self.assertIn(m_name, MAP_DEFINITIONS, f"Map '{m_name}' not found in MAP_DEFINITIONS")
            m_data = MAP_DEFINITIONS[m_name]
            grid = m_data["grid"]
            self.assertGreater(len(grid), 0)
            row_len = len(grid[0])
            for r_idx, row in enumerate(grid):
                self.assertEqual(len(row), row_len, f"Inconsistent row length in {m_name} row {r_idx}")

        # 2. Test Warps validity
        for m_name, m_data in MAP_DEFINITIONS.items():
            warps = m_data.get("warps", {})
            for (wx, wy), w_info in warps.items():
                tgt_map = w_info["target_map"]
                self.assertIn(tgt_map, MAP_DEFINITIONS, f"Warp in {m_name} at ({wx},{wy}) points to nonexistent map {tgt_map}")
                tgt_grid = MAP_DEFINITIONS[tgt_map]["grid"]
                tgt_h = len(tgt_grid)
                tgt_w = len(tgt_grid[0])
                tx, ty = w_info["target_x"], w_info["target_y"]
                self.assertTrue(0 <= tx < tgt_w, f"Warp in {m_name} has invalid target_x {tx} for {tgt_map} (width {tgt_w})")
                self.assertTrue(0 <= ty < tgt_h, f"Warp in {m_name} has invalid target_y {ty} for {tgt_map} (height {tgt_h})")

        # 3. Test Gym Leaders & League Champion existence
        gym_leader_ids = [
            "gym_leader_brock", "gym_leader_misty", "gym_leader_surge",
            "gym_leader_erika", "gym_leader_sabrina", "gym_leader_koga", "champion_blue"
        ]
        trainer_ids = {t["id"]: t for t in TRAINERS}
        for gl_id in gym_leader_ids:
            self.assertIn(gl_id, trainer_ids, f"Leader/Champion {gl_id} missing in TRAINERS")
            t_entry = trainer_ids[gl_id]
            self.assertGreater(len(t_entry["party"]), 0)
            self.assertTrue("reward_badge" in t_entry or "reward_money" in t_entry)

        # 4. Test TrainerCardScreen Region Map Drawing
        world = World()
        player = Player(x=8, y=6, current_map="Vermilion City")
        inv = Inventory()
        dex = Pokedex()
        card_screen = TrainerCardScreen(player, world, inv, dex, initial_tab=1)
        self.assertEqual(card_screen.active_tab, 1)
        self.assertGreater(len(card_screen.map_nodes), 30)
        card_screen.draw(surf)


