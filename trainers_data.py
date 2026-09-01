"""
trainers_data.py - NPC Trainer rosters, teams, and dialogues.
"""

TRAINERS = [
    # Route 1
    {
        "id": "youngster_joey",
        "name": "Youngster Joey",
        "map": "Route 1",
        "x": 12, "y": 14,
        "direction": "DOWN",
        "dialog_before": "Hi! I like shorts! They're comfy and easy to wear! Let's battle!",
        "dialog_after": "My Rattata is in the top percentage of Rattata!",
        "reward_money": 120,
        "party": [
            {"species": "Rattata", "level": 4},
            {"species": "Pidgey", "level": 4}
        ]
    },
    {
        "id": "bug_catcher_sammy",
        "name": "Bug Catcher Sammy",
        "map": "Route 1",
        "x": 6, "y": 20,
        "direction": "RIGHT",
        "dialog_before": "Stop right there! You caught wild Pokémon too?",
        "dialog_after": "Aw man! My Pokémon weren't fast enough!",
        "reward_money": 160,
        "party": [
            {"species": "Caterpie", "level": 5},
            {"species": "Weedle", "level": 5},
            {"species": "Butterfree", "level": 6}
        ]
    },
    # Route 22
    {
        "id": "rival_blue",
        "name": "Rival Blue",
        "map": "Route 22",
        "x": 18, "y": 8,
        "direction": "LEFT",
        "dialog_before": "Hey there! Heading to the Pokémon League? You're not ready yet! Let's test your team!",
        "dialog_after": "Hmph! You got lucky. Smell ya later!",
        "reward_money": 450,
        "party": [
            {"species": "Pidgey", "level": 8},
            {"species": "Rattata", "level": 8},
            {"species": "Squirtle", "level": 9}
        ]
    },
    {
        "id": "hiker_franklin",
        "name": "Hiker Franklin",
        "map": "Route 22",
        "x": 8, "y": 11,
        "direction": "DOWN",
        "dialog_before": "Climbing mountains toughens up my Rock and Ground Pokémon!",
        "dialog_after": "Your Pokémon have solid fundamentals!",
        "reward_money": 320,
        "party": [
            {"species": "Geodude", "level": 8},
            {"species": "Machop", "level": 8}
        ]
    },
    # Viridian Forest
    {
        "id": "bug_catcher_colton",
        "name": "Bug Catcher Colton",
        "map": "Viridian Forest",
        "x": 8, "y": 14,
        "direction": "RIGHT",
        "dialog_before": "I came to Viridian Forest with my friends to catch bug Pokémon!",
        "dialog_after": "I ran out of Poké Balls, but that was fun!",
        "reward_money": 200,
        "party": [
            {"species": "Caterpie", "level": 6},
            {"species": "Metapod", "level": 7},
            {"species": "Butterfree", "level": 8}
        ]
    },
    {
        "id": "bug_catcher_rick",
        "name": "Bug Catcher Rick",
        "map": "Viridian Forest",
        "x": 22, "y": 20,
        "direction": "LEFT",
        "dialog_before": "Watch out for poison stings from Weedle and Beedrill!",
        "dialog_after": "My Beedrill's poison sting failed!",
        "reward_money": 220,
        "party": [
            {"species": "Weedle", "level": 6},
            {"species": "Kakuna", "level": 7},
            {"species": "Beedrill", "level": 8}
        ]
    },
    {
        "id": "lass_haley",
        "name": "Lass Haley",
        "map": "Viridian Forest",
        "x": 18, "y": 7,
        "direction": "DOWN",
        "dialog_before": "You look like a tough trainer! Can you defeat my cute team?",
        "dialog_after": "You are indeed very strong!",
        "reward_money": 280,
        "party": [
            {"species": "Pikachu", "level": 8},
            {"species": "Clefairy", "level": 8},
            {"species": "Eevee", "level": 9}
        ]
    },
    # Pewter Gym
    {
        "id": "camper_liam",
        "name": "Camper Liam",
        "map": "Pewter Gym",
        "x": 6, "y": 6,
        "direction": "DOWN",
        "dialog_before": "You're still light-years away from facing Brock!",
        "dialog_after": "Light-years isn't time... it measures distance!",
        "reward_money": 350,
        "party": [
            {"species": "Geodude", "level": 10},
            {"species": "Sandshrew", "level": 11}
        ]
    },
    {
        "id": "gym_leader_brock",
        "name": "Leader Brock",
        "map": "Pewter Gym",
        "x": 6, "y": 3,
        "direction": "DOWN",
        "dialog_before": "I am Brock! The Pewter City Gym Leader! My rock-hard willpower is evident in my Pokémon! Are you ready?",
        "dialog_after": "I took you for granted! As proof of your victory, accept the Boulder Badge!",
        "reward_badge": "Boulder Badge",
        "reward_money": 1500,
        "party": [
            {"species": "Geodude", "level": 12},
            {"species": "Onix", "level": 14},
            {"species": "Graveler", "level": 15}
        ]
    },
    # Route 3
    {
        "id": "lass_janice",
        "name": "Lass Janice",
        "map": "Route 3",
        "x": 10, "y": 6,
        "direction": "DOWN",
        "dialog_before": "I love cute Pokémon! Have you seen any Jigglypuff?",
        "dialog_after": "Your Pokémon are cute and strong!",
        "reward_money": 320,
        "party": [
            {"species": "Pidgey", "level": 9},
            {"species": "Rattata", "level": 10},
            {"species": "Jigglypuff", "level": 11}
        ]
    },
    {
        "id": "youngster_ben",
        "name": "Youngster Ben",
        "map": "Route 3",
        "x": 18, "y": 8,
        "direction": "LEFT",
        "dialog_before": "I'm training hard to conquer Mt. Moon!",
        "dialog_after": "I need to train more before heading into the cave.",
        "reward_money": 300,
        "party": [
            {"species": "Spearow", "level": 11},
            {"species": "Raticate", "level": 12}
        ]
    },
    {
        "id": "hiker_wayne",
        "name": "Hiker Wayne",
        "map": "Route 3",
        "x": 25, "y": 5,
        "direction": "DOWN",
        "dialog_before": "Mt. Moon is just ahead! It's full of rocks and ancient fossils!",
        "dialog_after": "Gwah! My rocks crumbled!",
        "reward_money": 380,
        "party": [
            {"species": "Onix", "level": 11},
            {"species": "Geodude", "level": 12}
        ]
    },
    # Mt. Moon
    {
        "id": "rocket_grunt_1",
        "name": "Team Rocket Grunt",
        "map": "Mt. Moon",
        "x": 14, "y": 6,
        "direction": "DOWN",
        "dialog_before": "Team Rocket is mining all the Moon Stones in this cave! Get lost, kid!",
        "dialog_after": "Blast it! Don't mess with Team Rocket!",
        "reward_money": 500,
        "party": [
            {"species": "Zubat", "level": 11},
            {"species": "Koffing", "level": 12},
            {"species": "Raticate", "level": 12}
        ]
    },
    {
        "id": "super_nerd_miguel",
        "name": "Super Nerd Miguel",
        "map": "Mt. Moon",
        "x": 22, "y": 14,
        "direction": "LEFT",
        "dialog_before": "I found rare fossils and Moon Stones in this crater!",
        "dialog_after": "We each get to keep our discoveries!",
        "reward_money": 420,
        "party": [
            {"species": "Grimer", "level": 12},
            {"species": "Voltorb", "level": 12},
            {"species": "Koffing", "level": 13}
        ]
    },
    {
        "id": "hiker_marcos",
        "name": "Hiker Marcos",
        "map": "Mt. Moon",
        "x": 8, "y": 20,
        "direction": "RIGHT",
        "dialog_before": "It's easy to get lost in these dark tunnels! Let's see your spirit!",
        "dialog_after": "You navigated that battle like a pro!",
        "reward_money": 460,
        "party": [
            {"species": "Geodude", "level": 13},
            {"species": "Machop", "level": 13},
            {"species": "Onix", "level": 14}
        ]
    },
    # Route 4
    {
        "id": "lass_crissy",
        "name": "Lass Crissy",
        "map": "Route 4",
        "x": 12, "y": 6,
        "direction": "DOWN",
        "dialog_before": "We just made it through Mt. Moon! Cerulean City is right over there!",
        "dialog_after": "Time to visit the Cerulean Pokémon Center!",
        "reward_money": 360,
        "party": [
            {"species": "Paras", "level": 13},
            {"species": "Gloom", "level": 14}
        ]
    },
    {
        "id": "blackbelt_koji",
        "name": "Black Belt Koji",
        "map": "Route 4",
        "x": 20, "y": 8,
        "direction": "LEFT",
        "dialog_before": "Karate and Pokémon training go hand in hand! Hii-yah!",
        "dialog_after": "Your technique was flawless!",
        "reward_money": 450,
        "party": [
            {"species": "Mankey", "level": 14},
            {"species": "Primeape", "level": 15}
        ]
    },
    # Cerulean Gym
    {
        "id": "swimmer_luis",
        "name": "Swimmer Luis",
        "map": "Cerulean Gym",
        "x": 6, "y": 6,
        "direction": "DOWN",
        "dialog_before": "Splash! Misty is a master of Water Pokémon! Can you swim past me?",
        "dialog_after": "You made quite a splash!",
        "reward_money": 450,
        "party": [
            {"species": "Horsea", "level": 14},
            {"species": "Goldeen", "level": 15}
        ]
    },
    {
        "id": "gym_leader_misty",
        "name": "Leader Misty",
        "map": "Cerulean Gym",
        "x": 6, "y": 3,
        "direction": "DOWN",
        "dialog_before": "Hi, I'm Misty! The Tomboyish Mermaid! My Water-type Pokémon are graceful and deadly!",
        "dialog_after": "You are remarkably skilled! You've earned the Cascade Badge!",
        "reward_badge": "Cascade Badge",
        "reward_money": 2100,
        "party": [
            {"species": "Staryu", "level": 18},
            {"species": "Golduck", "level": 19},
            {"species": "Starmie", "level": 21}
        ]
    },
    # Route 24 (Nugget Bridge)
    {
        "id": "bridge_challenger_1",
        "name": "Bug Catcher Cale",
        "map": "Route 24",
        "x": 10, "y": 22,
        "direction": "LEFT",
        "dialog_before": "Welcome to the 5-Trainer Nugget Bridge! Defeat all 5 to win a fabulous prize!",
        "dialog_after": "You beat Challenger No. 1!",
        "reward_money": 300,
        "party": [
            {"species": "Caterpie", "level": 14},
            {"species": "Butterfree", "level": 16}
        ]
    },
    {
        "id": "bridge_challenger_2",
        "name": "Lass Ali",
        "map": "Route 24",
        "x": 10, "y": 18,
        "direction": "RIGHT",
        "dialog_before": "I'm Challenger No. 2! I won't go down easily!",
        "dialog_after": "You beat Challenger No. 2!",
        "reward_money": 340,
        "party": [
            {"species": "Pidgey", "level": 15},
            {"species": "Oddish", "level": 16}
        ]
    },
    {
        "id": "bridge_challenger_3",
        "name": "Youngster Timmy",
        "map": "Route 24",
        "x": 10, "y": 14,
        "direction": "LEFT",
        "dialog_before": "Challenger No. 3 here! My Pokémon are quick on their feet!",
        "dialog_after": "You beat Challenger No. 3!",
        "reward_money": 360,
        "party": [
            {"species": "Sandshrew", "level": 15},
            {"species": "Ekans", "level": 16}
        ]
    },
    {
        "id": "bridge_challenger_4",
        "name": "Camper Ethan",
        "map": "Route 24",
        "x": 10, "y": 10,
        "direction": "RIGHT",
        "dialog_before": "I'm Challenger No. 4! You're almost at the end of the bridge!",
        "dialog_after": "You beat Challenger No. 4!",
        "reward_money": 400,
        "party": [
            {"species": "Mankey", "level": 16},
            {"species": "Growlithe", "level": 16}
        ]
    },
    {
        "id": "bridge_challenger_5",
        "name": "Rocket Recruiter",
        "map": "Route 24",
        "x": 10, "y": 6,
        "direction": "DOWN",
        "dialog_before": "Congratulations on beating the 5 trainers! How about joining Team Rocket? No? Then taste defeat!",
        "dialog_after": "Blast! You're too tough. Take this Nugget and move along to Bill's Sea Cottage!",
        "reward_money": 1200,
        "party": [
            {"species": "Ekans", "level": 17},
            {"species": "Zubat", "level": 17}
        ]
    },
    # Route 21 (Ocean Route)
    {
        "id": "swimmer_douglas",
        "name": "Swimmer Douglas",
        "map": "Route 21",
        "x": 10, "y": 12,
        "direction": "RIGHT",
        "dialog_before": "The open sea south of Pallet Town is so refreshing! Let's battle in the water!",
        "dialog_after": "You swam circles around me!",
        "reward_money": 520,
        "party": [
            {"species": "Tentacool", "level": 18},
            {"species": "Shellder", "level": 19},
            {"species": "Seadra", "level": 20}
        ]
    },
    {
        "id": "fisherman_barny",
        "name": "Fisherman Barny",
        "map": "Route 21",
        "x": 16, "y": 24,
        "direction": "LEFT",
        "dialog_before": "I've been reeling in some giant sea Pokémon! Check out my catch!",
        "dialog_after": "The one that got away!",
        "reward_money": 580,
        "party": [
            {"species": "Magikarp", "level": 20},
            {"species": "Gyarados", "level": 22},
            {"species": "Seaking", "level": 21}
        ]
    },
    # Cinnabar Island
    {
        "id": "scientist_ted",
        "name": "Scientist Ted",
        "map": "Cinnabar Island",
        "x": 8, "y": 12,
        "direction": "RIGHT",
        "dialog_before": "Cinnabar Island is home to cutting-edge Pokémon research and fossil resurrection!",
        "dialog_after": "Astounding! Your Pokémon demonstrate remarkable evolutionary power!",
        "reward_money": 750,
        "party": [
            {"species": "Magneton", "level": 22},
            {"species": "Electrode", "level": 23},
            {"species": "Porygon", "level": 24}
        ]
    },
    {
        "id": "firebreather_dick",
        "name": "Firebreather Dick",
        "map": "Cinnabar Island",
        "x": 18, "y": 14,
        "direction": "LEFT",
        "dialog_before": "The volcanic heat of Cinnabar fuels my fiery passion!",
        "dialog_after": "You put out my flames!",
        "reward_money": 800,
        "party": [
            {"species": "Magmar", "level": 24},
            {"species": "Ninetales", "level": 25},
            {"species": "Rapidash", "level": 26}
        ]
    },
    # Route 9 (Rock Canyon)
    {
        "id": "camper_drew",
        "name": "Camper Drew",
        "map": "Route 9",
        "x": 8, "y": 9,
        "direction": "DOWN",
        "dialog_before": "I'm hiking through the rugged canyon to Lavender Town!",
        "dialog_after": "My hiking gear couldn't save me!",
        "reward_money": 420,
        "party": [
            {"species": "Mankey", "level": 17},
            {"species": "Sandslash", "level": 18}
        ]
    },
    {
        "id": "picnicker_alicia",
        "name": "Picnicker Alicia",
        "map": "Route 9",
        "x": 18, "y": 9,
        "direction": "UP",
        "dialog_before": "Don't disturb my canyon picnic with my cute Pokémon!",
        "dialog_after": "You have quite an appetite for victory!",
        "reward_money": 400,
        "party": [
            {"species": "Nidorina", "level": 17},
            {"species": "Clefairy", "level": 18}
        ]
    },
    {
        "id": "hiker_alan",
        "name": "Hiker Alan",
        "map": "Route 9",
        "x": 26, "y": 9,
        "direction": "LEFT",
        "dialog_before": "These red canyon rocks are as tough as my Pokémon!",
        "dialog_after": "Grounded!",
        "reward_money": 460,
        "party": [
            {"species": "Geodude", "level": 18},
            {"species": "Graveler", "level": 19},
            {"species": "Machop", "level": 18}
        ]
    },
    # Pokémon Tower
    {
        "id": "channeler_patricia",
        "name": "Channeler Patricia",
        "map": "Pokémon Tower",
        "x": 6, "y": 8,
        "direction": "DOWN",
        "dialog_before": "Give... me... your... soul...! Kekeke!",
        "dialog_after": "The spirits have been cleansed!",
        "reward_money": 520,
        "party": [
            {"species": "Gastly", "level": 20},
            {"species": "Haunter", "level": 22}
        ]
    },
    {
        "id": "channeler_carly",
        "name": "Channeler Carly",
        "map": "Pokémon Tower",
        "x": 20, "y": 8,
        "direction": "DOWN",
        "dialog_before": "Do you feel the supernatural chill in the air?",
        "dialog_after": "The eerie fog lifts...",
        "reward_money": 500,
        "party": [
            {"species": "Gastly", "level": 21},
            {"species": "Drowzee", "level": 21}
        ]
    },
    {
        "id": "channeler_hope",
        "name": "Channeler Hope",
        "map": "Pokémon Tower",
        "x": 13, "y": 13,
        "direction": "DOWN",
        "dialog_before": "Begone, living intruder! The spirits demand silence!",
        "dialog_after": "Hah! I am finally released from the trance!",
        "reward_money": 540,
        "party": [
            {"species": "Haunter", "level": 23},
            {"species": "Hypno", "level": 24}
        ]
    },
    # Power Plant
    {
        "id": "scientist_bray",
        "name": "Scientist Bray",
        "map": "Power Plant",
        "x": 6, "y": 8,
        "direction": "DOWN",
        "dialog_before": "We are conducting high-voltage energy experiments! Watch out!",
        "dialog_after": "Short circuit!",
        "reward_money": 650,
        "party": [
            {"species": "Magnemite", "level": 24},
            {"species": "Magneton", "level": 26}
        ]
    },
    {
        "id": "pokemaniac_mark",
        "name": "PokéManiac Mark",
        "map": "Power Plant",
        "x": 20, "y": 8,
        "direction": "DOWN",
        "dialog_before": "I came to this abandoned plant to catch rare Electric Pokémon!",
        "dialog_after": "Electrifying battle!",
        "reward_money": 600,
        "party": [
            {"species": "Voltorb", "level": 23},
            {"species": "Electrode", "level": 25}
        ]
    },
    {
        "id": "engineer_bucky",
        "name": "Engineer Bucky",
        "map": "Power Plant",
        "x": 13, "y": 13,
        "direction": "RIGHT",
        "dialog_before": "I'm rewiring the backup generator! Don't shock me!",
        "dialog_after": "The power surged right back at me!",
        "reward_money": 620,
        "party": [
            {"species": "Electabuzz", "level": 26},
            {"species": "Raichu", "level": 27}
        ]
    },
    # Seafoam Islands
    {
        "id": "skier_dianne",
        "name": "Skier Dianne",
        "map": "Seafoam Islands",
        "x": 6, "y": 8,
        "direction": "DOWN",
        "dialog_before": "Sliding across the ice is so exhilarating! Let's battle on the ice!",
        "dialog_after": "Wiped out on the ice!",
        "reward_money": 680,
        "party": [
            {"species": "Seel", "level": 25},
            {"species": "Dewgong", "level": 27}
        ]
    },
    {
        "id": "boarder_felix",
        "name": "Boarder Felix",
        "map": "Seafoam Islands",
        "x": 20, "y": 8,
        "direction": "LEFT",
        "dialog_before": "These sub-zero ice caves freeze unprepared trainers in their tracks!",
        "dialog_after": "My ice was melted!",
        "reward_money": 700,
        "party": [
            {"species": "Shellder", "level": 26},
            {"species": "Cloyster", "level": 28},
            {"species": "Jynx", "level": 28}
        ]
    },
    # Vermilion City & S.S. Anne
    {
        "id": "sailor_eddie",
        "name": "Sailor Eddie",
        "map": "Vermilion City",
        "x": 20, "y": 14,
        "direction": "LEFT",
        "dialog_before": "Ahoy! The sea air keeps me and my Water Pokémon energized!",
        "dialog_after": "Washed overboard!",
        "reward_money": 560,
        "party": [
            {"species": "Poliwhirl", "level": 20},
            {"species": "Shellder", "level": 21}
        ]
    },
    {
        "id": "sailor_dwayne",
        "name": "Sailor Dwayne",
        "map": "S.S. Anne",
        "x": 12, "y": 6,
        "direction": "DOWN",
        "dialog_before": "Welcome aboard the luxury cruise liner S.S. Anne! Let's spar!",
        "dialog_after": "You are a first-rate passenger!",
        "reward_money": 640,
        "party": [
            {"species": "Machop", "level": 20},
            {"species": "Tentacool", "level": 21}
        ]
    },
    {
        "id": "gentleman_thomas",
        "name": "Gentleman Thomas",
        "map": "S.S. Anne",
        "x": 22, "y": 6,
        "direction": "LEFT",
        "dialog_before": "Pardon me! Traveling around the world with Pokémon is the finest pastime!",
        "dialog_after": "Splendid match, young trainer!",
        "reward_money": 1200,
        "party": [
            {"species": "Growlithe", "level": 21},
            {"species": "Ponyta", "level": 21}
        ]
    },
    # Vermilion Gym
    {
        "id": "rocker_gene",
        "name": "Rocker Gene",
        "map": "Vermilion Gym",
        "x": 6, "y": 6,
        "direction": "DOWN",
        "dialog_before": "Lt. Surge was my commanding officer! His Electric Pokémon pack real voltage!",
        "dialog_after": "Blown fuse!",
        "reward_money": 580,
        "party": [
            {"species": "Voltorb", "level": 20},
            {"species": "Magnemite", "level": 20}
        ]
    },
    {
        "id": "gym_leader_surge",
        "name": "Leader Lt. Surge",
        "map": "Vermilion Gym",
        "x": 6, "y": 3,
        "direction": "DOWN",
        "dialog_before": "Hey kid! What do you think you're doing? I tell you, Electric Pokémon saved me in war! You won't shock me!",
        "dialog_after": "Whoa! You're the real deal, kid! Take the Thunder Badge!",
        "reward_badge": "Thunder Badge",
        "reward_money": 2400,
        "party": [
            {"species": "Voltorb", "level": 21},
            {"species": "Pikachu", "level": 22},
            {"species": "Raichu", "level": 24}
        ]
    },
    # Route 6 & Route 11
    {
        "id": "camper_jeff",
        "name": "Camper Jeff",
        "map": "Route 6",
        "x": 8, "y": 10,
        "direction": "RIGHT",
        "dialog_before": "I'm heading south to Vermilion Harbor! Let's battle on the path!",
        "dialog_after": "Good game!",
        "reward_money": 440,
        "party": [
            {"species": "Spearow", "level": 16},
            {"species": "Raticate", "level": 17}
        ]
    },
    {
        "id": "engineer_bernie",
        "name": "Engineer Bernie",
        "map": "Route 11",
        "x": 16, "y": 7,
        "direction": "DOWN",
        "dialog_before": "Diglett's Cave is right ahead! Diglett dug that massive tunnel through the mountains!",
        "dialog_after": "Overloaded!",
        "reward_money": 520,
        "party": [
            {"species": "Magnemite", "level": 18},
            {"species": "Magneton", "level": 20}
        ]
    },
    # Celadon City & Celadon Gym
    {
        "id": "lass_kay",
        "name": "Lass Kay",
        "map": "Celadon City",
        "x": 14, "y": 14,
        "direction": "DOWN",
        "dialog_before": "Celadon Department Store has every evolution stone and TM you could dream of!",
        "dialog_after": "I'm off to do more shopping!",
        "reward_money": 600,
        "party": [
            {"species": "Clefairy", "level": 23},
            {"species": "Wigglytuff", "level": 25}
        ]
    },
    {
        "id": "beauty_tamia",
        "name": "Beauty Tamia",
        "map": "Celadon Gym",
        "x": 6, "y": 6,
        "direction": "DOWN",
        "dialog_before": "Erika's flower arrangements and Grass Pokémon are truly exquisite!",
        "dialog_after": "Scattered petals!",
        "reward_money": 680,
        "party": [
            {"species": "Bellsprout", "level": 24},
            {"species": "Weepinbell", "level": 26}
        ]
    },
    {
        "id": "gym_leader_erika",
        "name": "Leader Erika",
        "map": "Celadon Gym",
        "x": 6, "y": 3,
        "direction": "DOWN",
        "dialog_before": "Hello... Lovely weather, isn't it? I am Erika, the Nature-Loving Princess. My fragrant Pokémon will soothe your soul.",
        "dialog_after": "Oh dear, I must concede defeat. You are remarkably strong. I proudly confer the Rainbow Badge upon you.",
        "reward_badge": "Rainbow Badge",
        "reward_money": 2900,
        "party": [
            {"species": "Victreebel", "level": 29},
            {"species": "Tangela", "level": 27},
            {"species": "Vileplume", "level": 30}
        ]
    },
    # Route 8
    {
        "id": "gambler_rich",
        "name": "Gambler Rich",
        "map": "Route 8",
        "x": 14, "y": 8,
        "direction": "DOWN",
        "dialog_before": "I'm on a roll from Celadon Game Corner! Double or nothing!",
        "dialog_after": "Snake eyes!",
        "reward_money": 900,
        "party": [
            {"species": "Growlithe", "level": 23},
            {"species": "Vulpix", "level": 23}
        ]
    },
    {
        "id": "super_nerd_glenn",
        "name": "Super Nerd Glenn",
        "map": "Route 8",
        "x": 22, "y": 8,
        "direction": "LEFT",
        "dialog_before": "Saffron City is directly to the west! Let me test my chemical formulas on you!",
        "dialog_after": "Reaction failed!",
        "reward_money": 620,
        "party": [
            {"species": "Grimer", "level": 23},
            {"species": "Muk", "level": 25}
        ]
    },
    # Saffron City & Saffron Gym
    {
        "id": "blackbelt_nob",
        "name": "Black Belt Nob",
        "map": "Saffron City",
        "x": 8, "y": 14,
        "direction": "RIGHT",
        "dialog_before": "We practice relentless martial arts discipline here in Saffron!",
        "dialog_after": "Your spirit is unbreakable!",
        "reward_money": 750,
        "party": [
            {"species": "Hitmonlee", "level": 33},
            {"species": "Hitmonchan", "level": 33}
        ]
    },
    {
        "id": "psychic_johan",
        "name": "Psychic Johan",
        "map": "Saffron Gym",
        "x": 6, "y": 6,
        "direction": "DOWN",
        "dialog_before": "I foresaw your arrival with telepathic clarity! Can you bypass psychic energy?",
        "dialog_after": "My telepathy failed to predict that power!",
        "reward_money": 820,
        "party": [
            {"species": "Slowpoke", "level": 33},
            {"species": "Kadabra", "level": 35}
        ]
    },
    {
        "id": "gym_leader_sabrina",
        "name": "Leader Sabrina",
        "map": "Saffron Gym",
        "x": 6, "y": 3,
        "direction": "DOWN",
        "dialog_before": "I had a vision of your arrival. I dislike battling, but it is my duty as Gym Leader. Behold psychic mastery!",
        "dialog_after": "I am shocked... but your victory is absolute. Take the Marsh Badge!",
        "reward_badge": "Marsh Badge",
        "reward_money": 3800,
        "party": [
            {"species": "Kadabra", "level": 36},
            {"species": "Mr. Mime", "level": 35},
            {"species": "Alakazam", "level": 38}
        ]
    },
    # Route 12 & Fuchsia Gym
    {
        "id": "bird_keeper_rod",
        "name": "Bird Keeper Rod",
        "map": "Route 12",
        "x": 10, "y": 14,
        "direction": "DOWN",
        "dialog_before": "Silence Bridge gives my flying Pokémon endless open skies!",
        "dialog_after": "Grounded safely!",
        "reward_money": 780,
        "party": [
            {"species": "Pidgeotto", "level": 28},
            {"species": "Doduo", "level": 29}
        ]
    },
    {
        "id": "juggler_nate",
        "name": "Juggler Nate",
        "map": "Fuchsia Gym",
        "x": 6, "y": 6,
        "direction": "DOWN",
        "dialog_before": "Fuchsia Gym is protected by invisible walls and toxic ninjas!",
        "dialog_after": "Dropped the ball!",
        "reward_money": 880,
        "party": [
            {"species": "Drowzee", "level": 34},
            {"species": "Hypno", "level": 36}
        ]
    },
    {
        "id": "gym_leader_koga",
        "name": "Leader Koga",
        "map": "Fuchsia Gym",
        "x": 6, "y": 3,
        "direction": "DOWN",
        "dialog_before": "Fwahahaha! A mere child challenges the Poisonous Ninja Master? Witness our ancient techniques and toxic venom!",
        "dialog_after": "Humph! You have proven your worth. You have earned the Soul Badge!",
        "reward_badge": "Soul Badge",
        "reward_money": 4200,
        "party": [
            {"species": "Koffing", "level": 37},
            {"species": "Muk", "level": 39},
            {"species": "Venomoth", "level": 40},
            {"species": "Weezing", "level": 42}
        ]
    },
    # Victory Road & Indigo Plateau
    {
        "id": "cooltrainer_sam",
        "name": "Cooltrainer Sam",
        "map": "Victory Road",
        "x": 10, "y": 12,
        "direction": "DOWN",
        "dialog_before": "Only the strongest trainers who conquered all 8 Kanto Gyms can pass Victory Road!",
        "dialog_after": "You truly have the heart of a Champion!",
        "reward_money": 1500,
        "party": [
            {"species": "Sandslash", "level": 43},
            {"species": "Kingler", "level": 44},
            {"species": "Charizard", "level": 46}
        ]
    },
    {
        "id": "cooltrainer_brooke",
        "name": "Cooltrainer Brooke",
        "map": "Victory Road",
        "x": 22, "y": 12,
        "direction": "LEFT",
        "dialog_before": "The Indigo Plateau League Champion awaits at the summit! Can you defeat me first?",
        "dialog_after": "Incredible strength!",
        "reward_money": 1600,
        "party": [
            {"species": "Cloyster", "level": 44},
            {"species": "Raichu", "level": 45},
            {"species": "Blastoise", "level": 47}
        ]
    },
    {
        "id": "champion_blue",
        "name": "Champion Blue",
        "map": "Indigo Plateau",
        "x": 13, "y": 6,
        "direction": "DOWN",
        "dialog_before": "Hey! I was waiting for you! I conquered the Elite Four and became the Pokémon League Champion! Let's see who is the greatest trainer in all of Kanto!",
        "dialog_after": "NO! That can't be! My ultimate team was defeated... You truly are the Pokémon League Champion!",
        "reward_badge": "League Champion Trophy",
        "reward_money": 9900,
        "party": [
            {"species": "Pidgeot", "level": 55},
            {"species": "Alakazam", "level": 56},
            {"species": "Rhydon", "level": 56},
            {"species": "Arcanine", "level": 57},
            {"species": "Exeggutor", "level": 57},
            {"species": "Charizard", "level": 60}
        ]
    }
]
