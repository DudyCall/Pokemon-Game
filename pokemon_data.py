"""
pokemon_data.py - Aggregator for Pokémon species, moves, items, encounters, and trainer databases.
Provides 100% backward compatibility for all modules importing from pokemon_data.
"""
from moves_data import MOVES
from species_data import POKEMON_SPECIES
from items_data import ITEMS, STONE_EVOLUTIONS
from encounters_data import (
    WILD_ENCOUNTERS,
    WILD_WATER_ENCOUNTERS,
    WILD_PROP_ENCOUNTERS,
    get_wild_encounters_for_prop
)
from trainers_data import TRAINERS

__all__ = [
    "MOVES",
    "POKEMON_SPECIES",
    "ITEMS",
    "STONE_EVOLUTIONS",
    "WILD_ENCOUNTERS",
    "WILD_WATER_ENCOUNTERS",
    "WILD_PROP_ENCOUNTERS",
    "get_wild_encounters_for_prop",
    "TRAINERS",
]
