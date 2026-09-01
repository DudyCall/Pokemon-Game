"""
items_data.py - Item database and evolutionary stone requirements.
"""

ITEMS = {
    "Poke Ball": {
        "name": "Poké Ball", "category": "ball", "catch_mult": 1.0, "price": 200,
        "desc": "A standard capsule for capturing wild Pokémon in battle. Throw it at weakened wild Pokémon to catch them.",
        "usage": "Use during wild Pokémon battles. Best when target has low HP or a status condition."
    },
    "Great Ball": {
        "name": "Great Ball", "category": "ball", "catch_mult": 1.5, "price": 600,
        "desc": "A high-performance capsule providing a 1.5x higher catch rate than a standard Poké Ball.",
        "usage": "Use during wild Pokémon battles for tough or higher-level targets."
    },
    "Ultra Ball": {
        "name": "Ultra Ball", "category": "ball", "catch_mult": 2.0, "price": 1200,
        "desc": "An ultra-grade capsule providing a superior 2.0x catch rate for capturing rare, powerful, or elusive wild Pokémon.",
        "usage": "Use during battle against rare species or Legendary Pokémon for maximum catch probability."
    },
    "Potion": {
        "name": "Potion", "category": "medicine", "heal_hp": 20, "price": 300,
        "desc": "A spray-type wound medicine that restores 20 HP to a single injured Pokémon.",
        "usage": "Use from the Bag or during battle on any damaged Pokémon."
    },
    "Super Potion": {
        "name": "Super Potion", "category": "medicine", "heal_hp": 50, "price": 700,
        "desc": "An advanced medical spray that restores 50 HP to a single injured Pokémon.",
        "usage": "Use from the Bag or during battle to heal moderate battle damage."
    },
    "Max Potion": {
        "name": "Max Potion", "category": "medicine", "heal_hp": 9999, "price": 2500,
        "desc": "A fully concentrated pharmaceutical spray that completely restores 100% of a Pokémon's maximum HP.",
        "usage": "Use from the Bag or during battle on heavily injured high-level Pokémon."
    },
    "Revive": {
        "name": "Revive", "category": "medicine", "revive_hp_percent": 50, "price": 1500,
        "desc": "A revitalizing medicine that revives a fainted Pokémon (0 HP) and restores half of its maximum HP.",
        "usage": "Use from the Bag or during battle on a fainted Pokémon to bring it back into action."
    },
    "Antidote": {
        "name": "Antidote", "category": "medicine", "cure_status": "Poison", "price": 100,
        "desc": "A specialized serum that cures a Pokémon of Poison status and stops residual poison damage.",
        "usage": "Use from the Bag or during battle whenever a Pokémon is afflicted with Poison."
    },
    "Paralyze Heal": {
        "name": "Paralyze Heal", "category": "medicine", "cure_status": "Paralysis", "price": 200,
        "desc": "A spray medicine that cures Paralysis, restoring full Speed and eliminating the chance of full paralysis.",
        "usage": "Use from the Bag or during battle whenever a Pokémon is paralyzed."
    },
    "Awakening": {
        "name": "Awakening", "category": "medicine", "cure_status": "Sleep", "price": 250,
        "desc": "An aromatic smelling-salts spray that immediately awakens a Pokémon from Sleep status.",
        "usage": "Use from the Bag or during battle whenever a Pokémon has fallen asleep."
    },
    "Burn Heal": {
        "name": "Burn Heal", "category": "medicine", "cure_status": "Burn", "price": 250,
        "desc": "A cooling salve that cures Burn status, stopping burn damage and restoring physical Attack power.",
        "usage": "Use from the Bag or during battle whenever a Pokémon is burned."
    },
    "Rare Candy": {
        "name": "Rare Candy", "category": "candy", "level_up": 1, "price": 4800,
        "desc": "A legendary energy-dense candy that instantly raises a single Pokémon's level by 1 and boosts all stats.",
        "usage": "Use from the Bag on any Pokémon below Level 100 to level up immediately."
    },
    "Moon Stone": {
        "name": "Moon Stone", "category": "stone", "price": 5000, "stone_type": "Moon Stone",
        "desc": "A cosmic lunar stone that radiates a pale glow. Triggers evolution for Clefairy, Jigglypuff, Nidorina, and Nidorino.",
        "usage": "Use from the Bag on Clefairy (-> Clefable), Nidorina (-> Nidoqueen), or Nidorino (-> Nidoking)."
    },
    "Fire Stone": {
        "name": "Fire Stone", "category": "stone", "price": 5000, "stone_type": "Fire Stone",
        "desc": "A warm elemental stone with an inner flame core. Triggers evolution for Vulpix, Growlithe, and Eevee.",
        "usage": "Use from the Bag on Vulpix (-> Ninetales), Growlithe (-> Arcanine), or Eevee (-> Flareon)."
    },
    "Water Stone": {
        "name": "Water Stone", "category": "stone", "price": 5000, "stone_type": "Water Stone",
        "desc": "A clear blue crystalline stone. Triggers evolution for Poliwhirl, Shellder, Staryu, and Eevee.",
        "usage": "Use from the Bag on Poliwhirl (-> Poliwrath), Shellder (-> Cloyster), Staryu (-> Starmie), or Eevee (-> Vaporeon)."
    },
    "Thunder Stone": {
        "name": "Thunder Stone", "category": "stone", "price": 5000, "stone_type": "Thunder Stone",
        "desc": "An electric stone crackling with lightning sparks. Triggers evolution for Pikachu and Eevee.",
        "usage": "Use from the Bag on Pikachu (-> Raichu) or Eevee (-> Jolteon)."
    },
    "Leaf Stone": {
        "name": "Leaf Stone", "category": "stone", "price": 5000, "stone_type": "Leaf Stone",
        "desc": "A verdant woodland stone with a leaf imprint. Triggers evolution for Gloom, Weepinbell, and Exeggcute.",
        "usage": "Use from the Bag on Gloom (-> Vileplume), Weepinbell (-> Victreebel), or Exeggcute (-> Exeggutor)."
    },
    "Nugget": {
        "name": "Nugget", "category": "valuable", "price": 5000,
        "desc": "A gleaming nugget of pure 24-karat gold with no battle effect. Can be sold at any PokéMart for $5,000 coins!",
        "usage": "Sell at the PokéMart to fund items, Poké Balls, or Move Master technique rerolls."
    },
    "Escape Rope": {
        "name": "Escape Rope", "category": "item", "price": 550,
        "desc": "A long, durable woven rope that immediately warps the player out of any cave, dungeon, or dark tunnel back to the entrance.",
        "usage": "Use from the Bag inside caves (Mt. Moon, Rock Tunnel, Seafoam Islands) for emergency extraction."
    },
    "Move Reroll Disk": {
        "name": "Move Reroll Disk", "category": "item", "price": 3000, "is_move_reroll": True,
        "desc": "A high-tech data disk containing rare techniques that allows a Pokémon to learn or reroll a new move from its species learnset.",
        "usage": "Use from the Bag on any party Pokémon or visit the Move Master in the PokéCenter."
    }
}

# Stone Evolution Compatibility Map
STONE_EVOLUTIONS = {
    "Moon Stone": {
        "Nidorina": "Nidoqueen",
        "Nidorino": "Nidoking",
        "Clefairy": "Clefable",
        "Jigglypuff": "Wigglytuff"
    },
    "Fire Stone": {
        "Vulpix": "Ninetales",
        "Growlithe": "Arcanine",
        "Eevee": "Flareon"
    },
    "Water Stone": {
        "Poliwhirl": "Poliwrath",
        "Shellder": "Cloyster",
        "Staryu": "Starmie",
        "Eevee": "Vaporeon"
    },
    "Thunder Stone": {
        "Pikachu": "Raichu",
        "Eevee": "Jolteon"
    },
    "Leaf Stone": {
        "Gloom": "Vileplume",
        "Weepinbell": "Victreebel",
        "Exeggcute": "Exeggutor"
    }
}

# Wild Encounters by Zone / Route
