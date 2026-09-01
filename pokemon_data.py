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

def get_pokemon_evolution_info(pokemon, inventory=None):
    """
    Returns structured evolution requirements and level milestones for a Pokemon:
    - target_species: str or None
    - method: 'LEVEL', 'STONE', 'NONE'
    - req_level: int or None
    - levels_left: int or None
    - is_ready: bool
    - stone_targets: list of (stone_name, target_species)
    - short_text: str (for mini badges on cards)
    """
    if not pokemon:
        return {"method": "NONE", "short_text": "Empty"}
    species = pokemon.species
    level = pokemon.level
    data = POKEMON_SPECIES.get(species, {})
    lvl_evo = data.get("evolution")

    stone_targets = []
    for s_name, mapping in STONE_EVOLUTIONS.items():
        if species in mapping:
            stone_targets.append((s_name, mapping[species]))

    if lvl_evo and lvl_evo.get("target"):
        req_lvl = lvl_evo.get("level", 100)
        target = lvl_evo.get("target")
        lvls_left = max(0, req_lvl - level)
        is_ready = (level >= req_lvl)
        if is_ready:
            short_txt = f"★ Ready! ➔ {target}"
        else:
            short_txt = f"▲ {target} in {lvls_left} Lvl{'s' if lvls_left != 1 else ''} (Lv.{req_lvl})"
        return {
            "target_species": target,
            "method": "LEVEL",
            "req_level": req_lvl,
            "levels_left": lvls_left,
            "is_ready": is_ready,
            "stone_targets": stone_targets,
            "short_text": short_txt
        }
    elif stone_targets:
        first_target = stone_targets[0][1]
        first_stone = stone_targets[0][0].replace(" Stone", "")
        if len(stone_targets) == 1:
            short_txt = f"💎 {first_stone} Stone ➔ {first_target}"
        else:
            short_txt = f"💎 {len(stone_targets)} Stone Paths"
        return {
            "target_species": first_target,
            "method": "STONE",
            "req_level": None,
            "levels_left": None,
            "is_ready": True,
            "stone_targets": stone_targets,
            "short_text": short_txt
        }
    else:
        return {
            "target_species": None,
            "method": "NONE",
            "req_level": None,
            "levels_left": None,
            "is_ready": False,
            "stone_targets": [],
            "short_text": "👑 Final Form"
        }

def get_full_evolution_tree(current_species):
    """
    Builds the full multi-stage evolution tree (past forms, current form, and future forms).
    Returns (root_species, chain) where chain is a list of node dicts.
    """
    parents = {}
    for parent, data in POKEMON_SPECIES.items():
        evo = data.get("evolution")
        if evo and evo.get("target"):
            parents[evo["target"]] = (parent, {"type": "LEVEL", "level": evo["level"]})
    for stone, mappings in STONE_EVOLUTIONS.items():
        for parent, target in mappings.items():
            if target not in parents:
                parents[target] = (parent, {"type": "STONE", "stone": stone})

    root = current_species
    visited = set()
    while root in parents and root not in visited:
        visited.add(root)
        root = parents[root][0]

    chain = []
    curr = root
    visited_fwd = set()
    while curr and curr not in visited_fwd:
        visited_fwd.add(curr)
        c_data = POKEMON_SPECIES.get(curr, {})
        lvl_evo = c_data.get("evolution")

        stone_evos = []
        for stone, mappings in STONE_EVOLUTIONS.items():
            if curr in mappings:
                stone_evos.append({"stone": stone, "target": mappings[curr]})

        chain.append({
            "species": curr,
            "level_evo": lvl_evo,
            "stone_evos": stone_evos,
            "types": c_data.get("types", ["Normal"]),
            "base_stats": c_data.get("base_stats", {}),
            "learnset": c_data.get("learnset", {})
        })

        if lvl_evo:
            curr = lvl_evo.get("target")
        else:
            curr = None

    return root, chain

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
    "get_pokemon_evolution_info",
    "get_full_evolution_tree"
]
