"""
pokemon.py - Pokemon entity class handling stats, leveling, moves, status, and evolution.
"""
import random
import math
from pokemon_data import POKEMON_SPECIES, MOVES

class Pokemon:
    def __init__(self, species_name, level=5, nickname=None, current_hp=None, moves=None, exp=None, status=None):
        if species_name not in POKEMON_SPECIES:
            species_name = "Pikachu"
        self.species_data = POKEMON_SPECIES[species_name]
        self.species = species_name
        self.nickname = nickname or species_name
        self.level = level
        self.types = list(self.species_data["types"])
        self.pokedex_id = self.species_data["id"]
        
        # IVs (Individual Values 0-31)
        self.ivs = {
            "hp": random.randint(10, 31),
            "atk": random.randint(10, 31),
            "def": random.randint(10, 31),
            "spatk": random.randint(10, 31),
            "spdef": random.randint(10, 31),
            "spd": random.randint(10, 31)
        }
        
        # Calculate stats
        self.stats = {}
        self.max_hp = 0
        self.recalculate_stats()
        
        self.current_hp = current_hp if current_hp is not None else self.max_hp
        self.status = status # "Burn", "Paralysis", "Sleep", "Poison", None
        self.sleep_turns = random.randint(1, 3) if status == "Sleep" else 0
        
        # EXP System (Medium-Fast: level^3)
        self.exp = exp if exp is not None else self.calc_exp_for_level(self.level)
        
        # Moves
        if moves is not None:
            self.moves = moves
        else:
            self.moves = self.init_moves_for_level()

    def calc_exp_for_level(self, lvl):
        return int(lvl ** 3)

    def exp_for_next_level(self):
        if self.level >= 100:
            return self.exp
        return self.calc_exp_for_level(self.level + 1)

    def exp_progress_ratio(self):
        curr_lvl_exp = self.calc_exp_for_level(self.level)
        next_lvl_exp = self.exp_for_next_level()
        if next_lvl_exp <= curr_lvl_exp:
            return 1.0
        return min(1.0, max(0.0, (self.exp - curr_lvl_exp) / (next_lvl_exp - curr_lvl_exp)))

    def recalculate_stats(self):
        base = self.species_data["base_stats"]
        prev_max_hp = self.max_hp
        
        # Classic Stat Formula: ((2 * Base + IV) * Level / 100) + Level + 10 (for HP)
        self.max_hp = math.floor(((2 * base["hp"] + self.ivs["hp"]) * self.level) / 100) + self.level + 10
        
        for stat in ["atk", "def", "spatk", "spdef", "spd"]:
            self.stats[stat] = math.floor(((2 * base[stat] + self.ivs[stat]) * self.level) / 100) + 5
            
        if prev_max_hp > 0 and hasattr(self, 'current_hp'):
            hp_diff = self.max_hp - prev_max_hp
            self.current_hp = min(self.max_hp, self.current_hp + hp_diff)

    def init_moves_for_level(self):
        available_moves = []
        learnset = self.species_data.get("learnset", {})
        for lvl in sorted(int(k) for k in learnset.keys()):
            if lvl <= self.level:
                moves_at_lvl = learnset.get(lvl) or learnset.get(str(lvl), [])
                for move_name in moves_at_lvl:
                    if move_name in MOVES and move_name not in [m["name"] for m in available_moves]:
                        available_moves.append(self.create_move_slot(move_name))
        
        if not available_moves:
            available_moves.append(self.create_move_slot("Tackle"))
            
        # Keep latest 4 moves
        return available_moves[-4:]

    def create_move_slot(self, move_name):
        data = MOVES.get(move_name, MOVES["Tackle"])
        return {
            "name": data["name"],
            "type": data["type"],
            "power": data["power"],
            "accuracy": data["accuracy"],
            "category": data["category"],
            "max_pp": data["pp"],
            "pp": data["pp"],
            "desc": data["desc"],
            "effect": data.get("effect"),
            "crit_bonus": data.get("crit_bonus", False)
        }

    def swap_moves(self, idx1, idx2):
        """Swaps the positions of two move slots on this Pokémon."""
        if 0 <= idx1 < len(self.moves) and 0 <= idx2 < len(self.moves) and idx1 != idx2:
            self.moves[idx1], self.moves[idx2] = self.moves[idx2], self.moves[idx1]
            return True
        return False

    def gain_exp(self, amount):
        """Gains EXP and returns a list of events: ('LEVEL_UP', lvl, stat_diffs), ('LEARN_MOVE', move_name), ('EVOLVE', target)"""
        events = []
        self.exp += amount
        
        while self.level < 100 and self.exp >= self.exp_for_next_level():
            self.level += 1
            old_stats = dict(self.stats)
            old_stats["hp"] = self.max_hp
            
            self.recalculate_stats()
            
            stat_diffs = {
                "hp": self.max_hp - old_stats["hp"],
                "atk": self.stats["atk"] - old_stats["atk"],
                "def": self.stats["def"] - old_stats["def"],
                "spatk": self.stats["spatk"] - old_stats["spatk"],
                "spdef": self.stats["spdef"] - old_stats["spdef"],
                "spd": self.stats["spd"] - old_stats["spd"]
            }
            events.append(("LEVEL_UP", self.level, stat_diffs))
            
            # Check for new moves
            learnset = self.species_data.get("learnset", {})
            new_moves = learnset.get(self.level) or learnset.get(str(self.level), [])
            for m_name in new_moves:
                if m_name in MOVES and m_name not in [m["name"] for m in self.moves]:
                    events.append(("LEARN_MOVE", m_name))
            
            # Check evolution
            evo = self.species_data.get("evolution")
            if evo and self.level >= evo["level"]:
                events.append(("EVOLVE", evo["target"]))
                
        return events

    def learn_move(self, move_name, replace_idx=None):
        new_move = self.create_move_slot(move_name)
        if len(self.moves) < 4:
            self.moves.append(new_move)
            return True, f"{self.nickname} learned {move_name}!"
        elif replace_idx is not None and 0 <= replace_idx < 4:
            old = self.moves[replace_idx]["name"]
            self.moves[replace_idx] = new_move
            return True, f"1, 2, and... Poof! {self.nickname} forgot {old} and learned {move_name}!"
        return False, "Moves are full."

    def get_rerollable_moves(self):
        """
        Returns a list of candidate move names available for this Pokémon to learn/reroll,
        drawn from its species learnset and compatible elemental technique repertoire.
        """
        known_moves = {m["name"] for m in self.moves}
        candidates = []

        # 1. Species Full Learnset
        learnset = self.species_data.get("learnset", {})
        for lvl, m_list in learnset.items():
            for m_name in m_list:
                if m_name in MOVES and m_name not in known_moves and m_name not in candidates:
                    candidates.append(m_name)

        # 2. Type-compatible & coverage techniques from Move Database
        for m_name, m_data in MOVES.items():
            if m_name in known_moves or m_name in candidates:
                continue
            m_type = m_data.get("type", "Normal")
            # If move type matches Pokémon types, or is a staple technique
            if m_type in self.types or (m_type in ["Normal", "Psychic", "Ground", "Fighting"] and m_data.get("power", 0) >= 40):
                candidates.append(m_name)

        # Sort candidates: STAB & high power first, then alphabetical
        def move_sort_key(name):
            d = MOVES.get(name, {})
            is_stab = 1 if d.get("type") in self.types else 0
            power = d.get("power", 0)
            return (-is_stab, -power, name)

        candidates.sort(key=move_sort_key)
        return candidates

    def reroll_move(self, replace_idx=None, specific_move=None):
        """
        Rerolls or teaches a new move to this Pokémon.
        If specific_move is provided, teaches that move; otherwise picks a random candidate.
        Returns (success, new_move_name, old_move_name, message).
        """
        candidates = self.get_rerollable_moves()
        if specific_move and specific_move in MOVES:
            target_move = specific_move
        elif candidates:
            target_move = random.choice(candidates)
        else:
            return False, None, None, f"{self.nickname} cannot learn any new moves right now!"

        old_move_name = None
        if len(self.moves) < 4:
            new_slot = self.create_move_slot(target_move)
            self.moves.append(new_slot)
            msg = f"{self.nickname} learned {target_move}!"
            return True, target_move, None, msg
        else:
            target_idx = replace_idx if (replace_idx is not None and 0 <= replace_idx < 4) else 0
            old_move_name = self.moves[target_idx]["name"]
            new_slot = self.create_move_slot(target_move)
            self.moves[target_idx] = new_slot
            msg = f"1, 2, and... Poof! {self.nickname} forgot {old_move_name} and learned {target_move}!"
            return True, target_move, old_move_name, msg


    def evolve(self, target_species):
        if target_species in POKEMON_SPECIES:
            old_name = self.species
            self.species = target_species
            self.species_data = POKEMON_SPECIES[target_species]
            self.types = list(self.species_data["types"])
            self.pokedex_id = self.species_data["id"]
            if self.nickname == old_name:
                self.nickname = target_species
            self.recalculate_stats()
            return True
        return False

    def is_fainted(self):
        return self.current_hp <= 0

    def take_damage(self, amount):
        dmg = max(1, int(amount))
        self.current_hp = max(0, self.current_hp - dmg)
        return self.current_hp

    def heal(self, amount):
        prev = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - prev

    def full_restore(self):
        self.current_hp = self.max_hp
        self.status = None
        self.sleep_turns = 0
        self.restore_all_pp()

    def restore_all_pp(self):
        for m in self.moves:
            m["pp"] = m["max_pp"]

    def cure_status(self):
        self.status = None
        self.sleep_turns = 0

    def apply_status(self, new_status):
        if self.status is not None or self.is_fainted():
            return False
        self.status = new_status
        if new_status == "Sleep":
            self.sleep_turns = random.randint(2, 4)
        return True

    def to_dict(self):
        return {
            "species": self.species,
            "nickname": self.nickname,
            "level": self.level,
            "current_hp": self.current_hp,
            "exp": self.exp,
            "status": self.status,
            "ivs": self.ivs,
            "moves": self.moves
        }

    @classmethod
    def from_dict(cls, data):
        p = cls(
            species_name=data["species"],
            level=data.get("level", 5),
            nickname=data.get("nickname"),
            current_hp=data.get("current_hp"),
            moves=data.get("moves"),
            exp=data.get("exp"),
            status=data.get("status")
        )
        if "ivs" in data:
            p.ivs = data["ivs"]
            p.recalculate_stats()
            if "current_hp" in data:
                p.current_hp = data["current_hp"]
        return p
