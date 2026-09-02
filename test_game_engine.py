"""
test_game_engine.py - Automated Unit Test Runner.
Combines TestCoreMixin, TestWorldGameplayMixin, and TestSystemsMixin into TestPokemonEngine.
"""
import os
import sys
import unittest
import tempfile
import shutil
import pygame

# Set headless dummy video and audio drivers for tests
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from save_system import SaveSystem
from tests_core import TestCoreMixin
from tests_world_gameplay import TestWorldGameplayMixin
from tests_systems import TestSystemsMixin


class TestPokemonEngine(TestCoreMixin, TestWorldGameplayMixin, TestSystemsMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.test_dir = tempfile.mkdtemp()
        SaveSystem.set_saves_dir(cls.test_dir)

    @classmethod
    def tearDownClass(cls):
        SaveSystem.reset_saves_dir()
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    def setUp(self):
        SaveSystem.set_saves_dir(self.test_dir)


if __name__ == "__main__":
    unittest.main()
