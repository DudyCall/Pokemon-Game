"""
tile_graphics.py - Procedural pixel-art tile generation for overworld, biomes, buildings, and dungeons.
"""
import random
import pygame
from constants import TILE_SIZE, WHITE, BLACK

def generate_tiles(fonts):
    """Generates beautiful crisp procedural pixel-art tiles."""
    cached_tiles = {}
    prop_overlays = {}
    T = TILE_SIZE
    
    # 1. Plain Grass
    grass = pygame.Surface((T, T))
    grass.fill((112, 200, 80)) # Lush emerald
    for _ in range(8):
        rx = random.randint(2, T - 3)
        ry = random.randint(2, T - 3)
        grass.set_at((rx, ry), (130, 220, 95))
        grass.set_at((rx + 1, ry), (90, 175, 60))
    cached_tiles["grass"] = grass
    
    # 2. Tall Encounter Grass
    tall_grass = grass.copy()
    for x in [4, 12, 20, 28]:
        for y in [6, 18]:
            # Draw grass blades
            pygame.draw.polygon(tall_grass, (45, 130, 40), [(x - 3, y + 10), (x, y), (x + 3, y + 10)])
            pygame.draw.polygon(tall_grass, (75, 175, 60), [(x - 2, y + 10), (x, y + 2), (x + 2, y + 10)])
    cached_tiles["tall_grass"] = tall_grass
    
    # 3. Path / Dirt Road
    path = pygame.Surface((T, T))
    path.fill((230, 210, 160)) # Sandy beige
    for _ in range(12):
        rx = random.randint(1, T - 2)
        ry = random.randint(1, T - 2)
        path.set_at((rx, ry), (210, 190, 140))
        if random.random() < 0.3:
            path.set_at((rx, ry), (245, 230, 190))
    cached_tiles["path"] = path
    
    # 4. Water (4-frame ripple animation)
    water_frames = []
    for f in range(4):
        ws = pygame.Surface((T, T))
        ws.fill((64, 136, 232))
        # Ripple waves
        phase = f * 8
        for row in range(4, T, 8):
            for col in range(0, T, 16):
                x = (col + phase) % T
                pygame.draw.arc(ws, (180, 220, 255), (x - 6, row, 12, 6), 0, 3.14, 2)
        water_frames.append(ws)
    cached_tiles["water"] = water_frames
    
    # 5. Tree (Top-Left, Top-Right, Bottom-Left, Bottom-Right 2x2)
    tree_top = pygame.Surface((T * 2, T))
    tree_top.fill((0, 0, 0))
    tree_top.set_colorkey((0, 0, 0))
    pygame.draw.circle(tree_top, (34, 120, 45), (T, T), T - 2)
    pygame.draw.circle(tree_top, (50, 160, 65), (T - 6, T - 6), T - 8)
    
    tree_bot = pygame.Surface((T * 2, T))
    tree_bot.fill((0, 0, 0))
    tree_bot.set_colorkey((0, 0, 0))
    pygame.draw.circle(tree_bot, (34, 120, 45), (T, 0), T - 2)
    pygame.draw.circle(tree_bot, (50, 160, 65), (T - 6, 0), T - 8)
    # Trunk
    pygame.draw.rect(tree_bot, (130, 80, 40), (T - 6, 8, 12, T - 8))
    pygame.draw.rect(tree_bot, (90, 50, 25), (T - 6, 8, 4, T - 8))
    
    cached_tiles["tree_tl"] = tree_top.subsurface((0, 0, T, T))
    cached_tiles["tree_tr"] = tree_top.subsurface((T, 0, T, T))
    cached_tiles["tree_bl"] = tree_bot.subsurface((0, 0, T, T))
    cached_tiles["tree_br"] = tree_bot.subsurface((T, 0, T, T))
    
    # 6. Flowers
    flower_red = grass.copy()
    pygame.draw.circle(flower_red, (240, 60, 60), (10, 12), 4)
    pygame.draw.circle(flower_red, (255, 230, 60), (10, 12), 2)
    pygame.draw.circle(flower_red, (240, 60, 60), (22, 22), 4)
    pygame.draw.circle(flower_red, (255, 230, 60), (22, 22), 2)
    cached_tiles["flower_red"] = flower_red
    
    # 7. Wooden Fence
    fence = grass.copy()
    pygame.draw.rect(fence, (160, 110, 60), (0, 10, T, 4))
    pygame.draw.rect(fence, (160, 110, 60), (0, 20, T, 4))
    pygame.draw.rect(fence, (120, 75, 35), (4, 6, 6, 22), border_radius=1)
    pygame.draw.rect(fence, (120, 75, 35), (22, 6, 6, 22), border_radius=1)
    cached_tiles["fence"] = fence
    
    # 8. Distinct Building Architecture Tiles
    # A. Residential House Shingle Roof
    roof_house = pygame.Surface((T, T))
    roof_house.fill((195, 75, 40)) # Warm terracotta shingle
    for sh_y in [0, 8, 16, 24]:
        pygame.draw.line(roof_house, (235, 115, 75), (0, sh_y), (T, sh_y), 2)
        pygame.draw.line(roof_house, (140, 48, 24), (0, sh_y + 7), (T, sh_y + 7), 1)
        offset = 8 if sh_y % 16 == 0 else 0
        for sh_x in range(offset, T, 16):
            pygame.draw.line(roof_house, (140, 48, 24), (sh_x, sh_y), (sh_x, sh_y + 7), 1)
    cached_tiles["roof_house"] = roof_house

    # B. Oak Lab / Tech Facility Solar Roof
    roof_lab = pygame.Surface((T, T))
    roof_lab.fill((140, 165, 195)) # Tech silver steel
    pygame.draw.rect(roof_lab, (180, 205, 230), (0, 0, T, T), 1)
    pygame.draw.rect(roof_lab, (40, 75, 120), (4, 4, 10, 10))
    pygame.draw.rect(roof_lab, (40, 75, 120), (18, 4, 10, 10))
    pygame.draw.rect(roof_lab, (40, 75, 120), (4, 18, 10, 10))
    pygame.draw.rect(roof_lab, (40, 75, 120), (18, 18, 10, 10))
    pygame.draw.line(roof_lab, (100, 160, 240), (6, 6), (12, 12), 1)
    pygame.draw.line(roof_lab, (100, 160, 240), (20, 6), (26, 12), 1)
    cached_tiles["roof_oak_lab"] = roof_lab

    # C. Grand Gym Classical Temple Roof
    roof_gym = pygame.Surface((T, T))
    roof_gym.fill((175, 140, 95)) # Classical temple stone
    pygame.draw.rect(roof_gym, (215, 180, 130), (0, 0, T, 6))
    pygame.draw.rect(roof_gym, (130, 95, 55), (0, 6, T, 4))
    for dx in range(2, T, 6):
        pygame.draw.rect(roof_gym, (245, 220, 175), (dx, 2, 3, 3))
    pygame.draw.line(roof_gym, (100, 70, 40), (0, T - 1), (T, T - 1), 2)
    cached_tiles["roof_gym"] = roof_gym

    # D. PokéCenter Curved Red Roof with Poké Ball Emblem
    roof_red = pygame.Surface((T, T))
    roof_red.fill((225, 45, 45))
    pygame.draw.rect(roof_red, (255, 95, 95), (0, 0, T, 5))
    pygame.draw.line(roof_red, (150, 20, 20), (0, T - 1), (T, T - 1), 2)
    cx, cy = T // 2, T // 2 + 1
    pygame.draw.circle(roof_red, WHITE, (cx, cy), 7)
    pygame.draw.arc(roof_red, (240, 40, 40), (cx - 6, cy - 6, 12, 12), 0, 3.14, 6)
    pygame.draw.circle(roof_red, WHITE, (cx, cy + 3), 3)
    pygame.draw.line(roof_red, (40, 40, 50), (cx - 7, cy), (cx + 7, cy), 1)
    pygame.draw.circle(roof_red, (40, 40, 50), (cx, cy), 2)
    pygame.draw.circle(roof_red, WHITE, (cx, cy), 1)
    cached_tiles["roof_red"] = roof_red

    # E. PokéMart Blue Roof with Striped Awning & Golden "M" Logo
    roof_blue = pygame.Surface((T, T))
    roof_blue.fill((35, 110, 215))
    pygame.draw.rect(roof_blue, (90, 165, 255), (0, 0, T, 5))
    for col_i in range(0, T, 8):
        c_col = (245, 245, 255) if (col_i // 8) % 2 == 0 else (25, 90, 190)
        pygame.draw.rect(roof_blue, c_col, (col_i, T - 8, 8, 8))
    pygame.draw.line(roof_blue, (15, 60, 140), (0, T - 1), (T, T - 1), 2)
    pygame.draw.circle(roof_blue, (255, 215, 40), (T // 2, 11), 6)
    pygame.draw.circle(roof_blue, (200, 150, 10), (T // 2, 11), 6, 1)
    m_txt = fonts["small"].render("M", True, (160, 50, 10))
    roof_blue.blit(m_txt, (T // 2 - m_txt.get_width() // 2, 4))
    cached_tiles["roof_blue"] = roof_blue

    # F. Celadon Mega Department Store Roof
    roof_dept = pygame.Surface((T, T))
    roof_dept.fill((215, 175, 55)) # Gold commercial
    pygame.draw.rect(roof_dept, (255, 225, 110), (0, 0, T, 6))
    pygame.draw.rect(roof_dept, (160, 120, 20), (0, 6, T, 4))
    for dx in range(0, T, 8):
        pygame.draw.rect(roof_dept, (255, 245, 180) if (dx // 8) % 2 == 0 else (180, 140, 30), (dx, T - 8, 8, 8))
    cached_tiles["roof_dept_store"] = roof_dept

    # G. Silph Co. Skyscraper Roof
    roof_silph = pygame.Surface((T, T))
    roof_silph.fill((80, 100, 125)) # Modern steel
    pygame.draw.rect(roof_silph, (120, 150, 185), (0, 0, T, 4))
    pygame.draw.rect(roof_silph, (40, 55, 75), (4, 6, T - 8, T - 10))
    pygame.draw.line(roof_silph, (80, 220, 255), (6, 8), (T - 6, 8), 1)
    cached_tiles["roof_silph_co"] = roof_silph

    # ==========================================
    # Wall Tiles
    # ==========================================
    # A. Upper House Wall with Window & Blooming Flower Planter
    wall_house_win = pygame.Surface((T, T))
    wall_house_win.fill((248, 246, 240)) # Warm cream
    for sy in [8, 16, 24]:
        pygame.draw.line(wall_house_win, (220, 215, 205), (0, sy), (T, sy), 1)
    pygame.draw.rect(wall_house_win, (120, 80, 45), (6, 3, 20, 18), border_radius=2)
    pygame.draw.rect(wall_house_win, (130, 200, 245), (8, 5, 16, 14))
    pygame.draw.line(wall_house_win, (255, 255, 255), (9, 6), (15, 12), 1)
    pygame.draw.line(wall_house_win, (120, 80, 45), (16, 5), (16, 19), 1)
    pygame.draw.line(wall_house_win, (120, 80, 45), (8, 12), (24, 12), 1)
    pygame.draw.rect(wall_house_win, (150, 95, 55), (4, 19, 24, 6), border_radius=1)
    pygame.draw.circle(wall_house_win, (240, 50, 50), (7, 18), 3)
    pygame.draw.circle(wall_house_win, (255, 220, 40), (13, 17), 3)
    pygame.draw.circle(wall_house_win, (240, 50, 50), (19, 18), 3)
    pygame.draw.circle(wall_house_win, (60, 150, 240), (25, 17), 3)
    cached_tiles["wall_house_window"] = wall_house_win

    # B. Lower House Wall with Red Brick Base & Brass Carriage Lantern
    wall_house = pygame.Surface((T, T))
    wall_house.fill((248, 246, 240)) # Warm cream
    pygame.draw.rect(wall_house, (180, 75, 60), (0, 16, T, 16))
    pygame.draw.line(wall_house, (140, 55, 45), (0, 16), (T, 16), 1)
    pygame.draw.line(wall_house, (140, 55, 45), (0, 24), (T, 24), 1)
    pygame.draw.line(wall_house, (140, 55, 45), (0, 31), (T, 31), 1)
    pygame.draw.line(wall_house, (140, 55, 45), (8, 16), (8, 24), 1)
    pygame.draw.line(wall_house, (140, 55, 45), (24, 16), (24, 24), 1)
    pygame.draw.line(wall_house, (140, 55, 45), (16, 24), (16, 31), 1)
    pygame.draw.rect(wall_house, (50, 45, 40), (13, 4, 6, 9), border_radius=1)
    pygame.draw.rect(wall_house, (255, 230, 110), (14, 6, 4, 5))
    cached_tiles["wall_house"] = wall_house

    # C. Generic Commercial / Lab Wall White
    wall_white = pygame.Surface((T, T))
    wall_white.fill((242, 244, 248))
    pygame.draw.rect(wall_white, (210, 215, 225), (0, 0, T, T), 1)
    pygame.draw.rect(wall_white, (180, 190, 205), (0, T - 6, T, 6))
    cached_tiles["wall_white"] = wall_white

    # D. Oak Lab Tech Wall with Observation Screen
    wall_oak = pygame.Surface((T, T))
    wall_oak.fill((225, 235, 245))
    pygame.draw.rect(wall_oak, (160, 180, 205), (0, 0, T, T), 1)
    pygame.draw.rect(wall_oak, (40, 60, 85), (6, 5, 20, 16), border_radius=2)
    pygame.draw.rect(wall_oak, (60, 180, 230), (8, 7, 16, 12))
    pygame.draw.line(wall_oak, (120, 240, 255), (9, 13), (13, 9), 1)
    pygame.draw.line(wall_oak, (120, 240, 255), (15, 15), (21, 9), 1)
    pygame.draw.circle(wall_oak, (60, 220, 80), (8, 26), 2)
    pygame.draw.circle(wall_oak, (240, 60, 60), (14, 26), 2)
    cached_tiles["wall_oak_lab"] = wall_oak

    # E. Gym Classical Marble Wall
    wall_gym = pygame.Surface((T, T))
    wall_gym.fill((235, 228, 215)) # Warm marble
    pygame.draw.rect(wall_gym, (200, 190, 175), (0, 0, T, T), 1)
    pygame.draw.rect(wall_gym, (215, 200, 180), (6, 0, 8, T))
    pygame.draw.rect(wall_gym, (215, 200, 180), (18, 0, 8, T))
    pygame.draw.rect(wall_gym, (240, 190, 40), (14, 10, 4, 10), border_radius=1) # Torch sconce
    pygame.draw.circle(wall_gym, (255, 120, 20), (16, 8), 3) # Flame
    cached_tiles["wall_gym"] = wall_gym

    # F. Department Store / Silph Co Walls
    wall_dept = pygame.Surface((T, T))
    wall_dept.fill((230, 215, 170))
    pygame.draw.rect(wall_dept, (180, 150, 90), (0, 0, T, T), 1)
    pygame.draw.rect(wall_dept, (120, 180, 230), (4, 4, T - 8, T - 10))
    pygame.draw.line(wall_dept, WHITE, (6, 6), (16, 16), 1)
    cached_tiles["wall_dept_store"] = wall_dept

    wall_silph = pygame.Surface((T, T))
    wall_silph.fill((60, 75, 95))
    pygame.draw.rect(wall_silph, (90, 110, 140), (0, 0, T, T), 1)
    pygame.draw.rect(wall_silph, (30, 120, 180), (4, 4, T - 8, T - 10))
    pygame.draw.line(wall_silph, (120, 220, 255), (6, 6), (20, 20), 1)
    cached_tiles["wall_silph_co"] = wall_silph

    # ==========================================
    # Door Tiles
    # ==========================================
    # A. Residential Warm Oak Wood Door
    door_house = wall_house.copy()
    pygame.draw.rect(door_house, (180, 175, 165), (2, 28, 28, 4), border_radius=1)
    pygame.draw.rect(door_house, (100, 60, 30), (5, 4, 22, 26), border_radius=3)
    pygame.draw.rect(door_house, (160, 105, 55), (7, 6, 18, 22), border_radius=2)
    pygame.draw.rect(door_house, (130, 80, 40), (9, 8, 6, 8), border_radius=1)
    pygame.draw.rect(door_house, (130, 80, 40), (17, 8, 6, 8), border_radius=1)
    pygame.draw.rect(door_house, (130, 80, 40), (9, 18, 6, 8), border_radius=1)
    pygame.draw.rect(door_house, (130, 80, 40), (17, 18, 6, 8), border_radius=1)
    pygame.draw.circle(door_house, (255, 215, 40), (22, 17), 2)
    cached_tiles["door_house"] = door_house
    cached_tiles["door"] = door_house # Default fallback

    # B. PokéCenter Sliding Glass Doors
    door_center = wall_white.copy()
    pygame.draw.rect(door_center, (220, 45, 45), (4, 4, 24, 28), border_radius=2)
    pygame.draw.rect(door_center, (180, 230, 255), (6, 6, 9, 24))
    pygame.draw.rect(door_center, (180, 230, 255), (17, 6, 9, 24))
    pygame.draw.line(door_center, (255, 255, 255), (8, 8), (12, 16), 1)
    pygame.draw.line(door_center, (255, 255, 255), (19, 8), (23, 16), 1)
    pygame.draw.rect(door_center, (50, 220, 60), (14, 2, 4, 2))
    cached_tiles["door_center"] = door_center

    # C. PokéMart Commercial Glass Door
    door_mart = wall_white.copy()
    pygame.draw.rect(door_mart, (35, 110, 215), (4, 4, 24, 28), border_radius=2)
    pygame.draw.rect(door_mart, (200, 235, 255), (6, 6, 20, 24))
    pygame.draw.line(door_mart, (255, 255, 255), (9, 8), (14, 18), 1)
    pygame.draw.rect(door_mart, (255, 215, 40), (14, 16, 4, 4))
    cached_tiles["door_mart"] = door_mart

    # D. Oak Lab / Silph Co Electronic Keycard Door
    door_lab = wall_white.copy()
    pygame.draw.rect(door_lab, (100, 130, 165), (4, 4, 24, 28), border_radius=2)
    pygame.draw.rect(door_lab, (60, 90, 125), (6, 6, 20, 24))
    pygame.draw.line(door_lab, (80, 230, 255), (10, 16), (22, 16), 2)
    pygame.draw.circle(door_lab, (80, 255, 120), (22, 10), 2)
    cached_tiles["door_lab"] = door_lab

    # E. Grand Gym Reinforced Double Doors
    door_gym = wall_white.copy()
    pygame.draw.rect(door_gym, (130, 80, 45), (4, 4, 24, 28), border_radius=2)
    pygame.draw.rect(door_gym, (165, 115, 65), (6, 6, 9, 24))
    pygame.draw.rect(door_gym, (165, 115, 65), (17, 6, 9, 24))
    pygame.draw.circle(door_gym, (240, 190, 40), (11, 16), 3, 1)
    pygame.draw.circle(door_gym, (240, 190, 40), (21, 16), 3, 1)
    cached_tiles["door_gym"] = door_gym

    # ==========================================
    # Distinct Dungeon & Cave Entrance Tiles
    # Sand / Beach Shore
    sand = pygame.Surface((T, T))
    sand.fill((240, 220, 160)) # Golden sand
    for _ in range(10):
        rx = random.randint(1, T - 2)
        ry = random.randint(1, T - 2)
        sand.set_at((rx, ry), (220, 200, 140))
    cached_tiles["sand"] = sand

    # Cave Floor (Subterranean)
    cave_floor = pygame.Surface((T, T))
    cave_floor.fill((85, 75, 70)) # Dark stone brown
    for _ in range(12):
        rx = random.randint(1, T - 2)
        ry = random.randint(1, T - 2)
        cave_floor.set_at((rx, ry), (70, 60, 55))
        if random.random() < 0.3:
            cave_floor.set_at((rx, ry), (105, 95, 90))
    cached_tiles["cave_floor"] = cave_floor

    # ==========================================
    # 11. Cave Wall / Mountain Rock
    cave_wall = pygame.Surface((T, T))
    cave_wall.fill((45, 40, 38))
    pygame.draw.rect(cave_wall, (65, 58, 55), (2, 2, T - 4, T - 4), border_radius=4)
    pygame.draw.polygon(cave_wall, (30, 25, 24), [(4, 4), (16, 2), (28, 8), (20, 28), (6, 24)])
    pygame.draw.polygon(cave_wall, (75, 68, 65), [(8, 8), (18, 6), (24, 12), (18, 22), (10, 18)])
    cached_tiles["cave_wall"] = cave_wall

    # Generic Cave Door
    cave_door = cave_wall.copy()
    pygame.draw.arc(cave_door, (10, 10, 12), (6, 4, 20, 26), 0, 3.14, 10)
    pygame.draw.rect(cave_door, (10, 10, 12), (6, 12, 20, 20))
    cached_tiles["cave_door"] = cave_door

    # A. Mt. Moon Cavern Entrance (Rugged Timber Mine Arch with Moon Stone Vein)
    cave_moon = cave_wall.copy()
    pygame.draw.rect(cave_moon, (10, 10, 12), (6, 10, 20, 22))
    pygame.draw.arc(cave_moon, (10, 10, 12), (6, 2, 20, 20), 0, 3.14, 10)
    # Wooden mine support beams
    pygame.draw.rect(cave_moon, (140, 90, 45), (4, 4, 4, 28))
    pygame.draw.rect(cave_moon, (140, 90, 45), (24, 4, 4, 28))
    pygame.draw.rect(cave_moon, (160, 110, 55), (2, 2, 28, 5))
    # Hanging mining lantern
    pygame.draw.rect(cave_moon, (50, 45, 40), (14, 7, 4, 6))
    pygame.draw.circle(cave_moon, (255, 225, 100), (16, 10), 2)
    # Moon Stone cyan crystal vein
    pygame.draw.polygon(cave_moon, (120, 230, 255), [(2, 10), (5, 8), (4, 14)])
    pygame.draw.polygon(cave_moon, (120, 230, 255), [(27, 14), (30, 12), (29, 18)])
    cached_tiles["cave_door_mt_moon"] = cave_moon

    # B. Viridian Forest Living Tree Canopy Archway
    cave_forest = grass.copy()
    pygame.draw.rect(cave_forest, (20, 30, 15), (6, 10, 20, 22))
    pygame.draw.arc(cave_forest, (20, 30, 15), (6, 4, 20, 18), 0, 3.14, 10)
    # Ancient mossy tree trunk pillars
    pygame.draw.rect(cave_forest, (100, 65, 35), (2, 2, 6, 30), border_radius=2)
    pygame.draw.rect(cave_forest, (100, 65, 35), (24, 2, 6, 30), border_radius=2)
    pygame.draw.ellipse(cave_forest, (40, 130, 50), (0, 0, T, 12)) # Leafy canopy
    pygame.draw.ellipse(cave_forest, (65, 175, 75), (4, 2, T - 8, 8))
    # Hanging vines
    pygame.draw.line(cave_forest, (50, 150, 60), (10, 10), (10, 18), 2)
    pygame.draw.line(cave_forest, (50, 150, 60), (22, 10), (22, 16), 2)
    cached_tiles["cave_door_forest"] = cave_forest

    # C. Diglett's Cave Earthen Burrow Entrance
    cave_diglett = grass.copy()
    # Excavated earthen dirt mound
    pygame.draw.ellipse(cave_diglett, (140, 95, 55), (2, 4, 28, 26))
    pygame.draw.ellipse(cave_diglett, (100, 65, 35), (4, 8, 24, 22))
    pygame.draw.ellipse(cave_diglett, (20, 15, 10), (7, 12, 18, 18))
    # Wooden arch header
    pygame.draw.rect(cave_diglett, (160, 110, 55), (5, 6, 22, 4), border_radius=1)
    # Diglett warning marker
    pygame.draw.rect(cave_diglett, (180, 130, 80), (12, 0, 8, 7), border_radius=1)
    pygame.draw.circle(cave_diglett, (160, 80, 40), (16, 3), 2)
    cached_tiles["cave_door_diglett"] = cave_diglett

    # D. Power Plant Heavy Industrial Blast Gate
    gate_power = pygame.Surface((T, T))
    gate_power.fill((70, 75, 85))
    # Yellow and black hazard chevron warning border
    for h_i in range(0, T, 8):
        h_col = (245, 215, 30) if (h_i // 8) % 2 == 0 else (30, 30, 35)
        pygame.draw.rect(gate_power, h_col, (h_i, 0, 8, 5))
    pygame.draw.rect(gate_power, (40, 45, 55), (4, 6, 24, 26), border_radius=2)
    pygame.draw.rect(gate_power, (20, 22, 28), (6, 8, 20, 24))
    # Electric lightning symbol on steel door
    pygame.draw.lines(gate_power, (255, 235, 50), False, [(16, 11), (13, 18), (17, 18), (14, 26)], 2)
    pygame.draw.circle(gate_power, (255, 80, 80), (22, 11), 2) # Warning red beacon
    cached_tiles["gate_power_plant"] = gate_power

    # E. Pokémon Tower Haunted Gothic Stone Spire Gate
    gate_tower = pygame.Surface((T, T))
    gate_tower.fill((55, 42, 68)) # Haunted dark purple stone
    pygame.draw.rect(gate_tower, (75, 60, 90), (0, 0, T, T), 1)
    pygame.draw.rect(gate_tower, (18, 12, 25), (6, 8, 20, 24))
    pygame.draw.arc(gate_tower, (18, 12, 25), (6, 0, 20, 20), 0, 3.14, 10)
    # Gothic gargoyle pointed keystone
    pygame.draw.polygon(gate_tower, (95, 78, 115), [(16, 0), (12, 6), (20, 6)])
    # Iron portcullis bars
    for bx in [9, 13, 17, 21]:
        pygame.draw.line(gate_tower, (110, 95, 130), (bx, 6), (bx, 30), 1)
    pygame.draw.line(gate_tower, (110, 95, 130), (7, 16), (23, 16), 1)
    # Eerie violet spirit mist at entrance base
    pygame.draw.ellipse(gate_tower, (180, 130, 255), (6, 24, 20, 8))
    cached_tiles["gate_pokemon_tower"] = gate_tower

    # F. Seafoam Islands Glacial Ice Cavern Grotto
    cave_seafoam = pygame.Surface((T, T))
    cave_seafoam.fill((130, 205, 238)) # Glacial ice
    pygame.draw.rect(cave_seafoam, (15, 35, 60), (6, 10, 20, 22))
    pygame.draw.arc(cave_seafoam, (15, 35, 60), (6, 2, 20, 20), 0, 3.14, 10)
    # Glistening translucent ice pillars
    pygame.draw.rect(cave_seafoam, (190, 240, 255), (2, 2, 5, 28), border_radius=2)
    pygame.draw.rect(cave_seafoam, (190, 240, 255), (25, 2, 5, 28), border_radius=2)
    # Sparkling hanging icicles
    for ix, ih in [(8, 6), (12, 10), (16, 7), (20, 9), (23, 5)]:
        pygame.draw.polygon(cave_seafoam, (240, 252, 255), [(ix - 2, 4), (ix + 2, 4), (ix, 4 + ih)])
    cached_tiles["cave_door_seafoam"] = cave_seafoam

    # G. Safari Zone Tribal Lodge Archway
    gate_safari = pygame.Surface((T, T))
    gate_safari.fill((215, 190, 115)) # Warm amber savanna soil
    pygame.draw.rect(gate_safari, (40, 30, 20), (6, 10, 20, 22))
    pygame.draw.arc(gate_safari, (40, 30, 20), (6, 4, 20, 18), 0, 3.14, 10)
    # Thatched savanna canopy
    pygame.draw.rect(gate_safari, (195, 155, 65), (0, 0, T, 8), border_radius=2)
    pygame.draw.rect(gate_safari, (140, 95, 40), (2, 4, 5, 26))
    pygame.draw.rect(gate_safari, (140, 95, 40), (25, 4, 5, 26))
    # Safari Zone crest
    pygame.draw.circle(gate_safari, (240, 190, 40), (16, 6), 4)
    pygame.draw.circle(gate_safari, (45, 130, 40), (16, 6), 2)
    cached_tiles["gate_safari_zone"] = gate_safari

    # H. S.S. Anne Luxury Cruise Ship Gangway Pier
    pier_ss = pygame.Surface((T, T))
    pier_ss.fill((64, 136, 232)) # Ocean water base
    # Wooden pier deck
    pygame.draw.rect(pier_ss, (190, 145, 95), (4, 0, 24, T))
    for py in [0, 8, 16, 24]:
        pygame.draw.line(pier_ss, (140, 95, 55), (4, py), (28, py), 1)
    # Brass ocean ship railing
    pygame.draw.line(pier_ss, (240, 200, 60), (4, 0), (4, T), 2)
    pygame.draw.line(pier_ss, (240, 200, 60), (28, 0), (28, T), 2)
    # Red and white lifebuoy on post
    pygame.draw.circle(pier_ss, (230, 50, 50), (16, 8), 5)
    pygame.draw.circle(pier_ss, WHITE, (16, 8), 2)
    cached_tiles["pier_ss_anne"] = pier_ss

    # I. Victory Road Epic Jagged Cavern Gate
    cave_victory = cave_wall.copy()
    pygame.draw.rect(cave_victory, (8, 8, 10), (5, 8, 22, 24))
    pygame.draw.polygon(cave_victory, (8, 8, 10), [(5, 8), (16, 0), (27, 8)])
    # League Torch Braziers
    pygame.draw.rect(cave_victory, (180, 140, 40), (1, 10, 4, 14), border_radius=1)
    pygame.draw.circle(cave_victory, (255, 100, 20), (3, 8), 3) # Torch flame
    pygame.draw.rect(cave_victory, (180, 140, 40), (27, 10, 4, 14), border_radius=1)
    pygame.draw.circle(cave_victory, (255, 100, 20), (29, 8), 3)
    cached_tiles["cave_door_victory"] = cave_victory

    # J. Indigo Plateau Castle Gates
    gate_indigo = pygame.Surface((T, T))
    gate_indigo.fill((160, 140, 110))
    pygame.draw.rect(gate_indigo, (15, 15, 25), (5, 6, 22, 26), border_radius=3)
    # Golden League Columns
    pygame.draw.rect(gate_indigo, (245, 215, 60), (1, 0, 5, T))
    pygame.draw.rect(gate_indigo, (245, 215, 60), (26, 0, 5, T))
    pygame.draw.rect(gate_indigo, (220, 175, 30), (0, 0, T, 6))
    # Golden Champion Star Crest
    pygame.draw.polygon(gate_indigo, (255, 235, 80), [(16, 8), (18, 13), (23, 13), (19, 16), (21, 21), (16, 18), (11, 21), (13, 16), (9, 13), (14, 13)])
    cached_tiles["gate_indigo_plateau"] = gate_indigo

    # K. Cerulean Cave Fissure (Mysterious Psychic Cavern)
    cave_cerul = cave_wall.copy()
    pygame.draw.rect(cave_cerul, (12, 6, 20), (6, 6, 20, 26))
    pygame.draw.polygon(cave_cerul, (12, 6, 20), [(6, 6), (16, 1), (26, 6)])
    # Glowing dark purple psychic crystals
    pygame.draw.polygon(cave_cerul, (190, 80, 255), [(3, 8), (6, 4), (5, 14)])
    pygame.draw.polygon(cave_cerul, (160, 50, 240), [(26, 8), (29, 4), (28, 14)])
    pygame.draw.polygon(cave_cerul, (220, 140, 255), [(14, 10), (16, 6), (18, 10)])
    cached_tiles["cave_door_cerulean_cave"] = cave_cerul

    # ==========================================
    # Indoor House Floors & Furniture Tiles
    # ==========================================
    # Parquet Hardwood House Floor
    floor_house = pygame.Surface((T, T))
    floor_house.fill((218, 170, 115)) # Warm oak parquet
    # Parquet wood plank texture
    for px in [0, 16]:
        for py in [0, 16]:
            pygame.draw.rect(floor_house, (195, 148, 95), (px, py, 16, 16), 1)
            pygame.draw.line(floor_house, (230, 185, 130), (px + 1, py + 1), (px + 15, py + 1), 1)
    cached_tiles["floor_house"] = floor_house
    cached_tiles["floor"] = floor_house
    floor = floor_house

    # Indoor Living Room Rug / Carpet
    carpet = floor_house.copy()
    pygame.draw.rect(carpet, (190, 45, 45), (2, 2, T - 4, T - 4), border_radius=3)
    pygame.draw.rect(carpet, (240, 195, 60), (4, 4, T - 8, T - 8), 1, border_radius=2)
    pygame.draw.circle(carpet, (240, 195, 60), (T // 2, T // 2), 4)
    cached_tiles["carpet_house"] = carpet

    # Retro CRT Television Set
    tv_set = floor_house.copy()
    pygame.draw.rect(tv_set, (80, 50, 30), (3, 4, 26, 22), border_radius=2)
    pygame.draw.rect(tv_set, (30, 35, 45), (5, 6, 16, 14), border_radius=1)
    pygame.draw.rect(tv_set, (70, 150, 220), (7, 8, 12, 10)) # Screen game display
    pygame.draw.circle(tv_set, (240, 60, 60), (13, 13), 2) # Game sprite
    pygame.draw.circle(tv_set, (180, 170, 160), (24, 9), 2) # TV dial 1
    pygame.draw.circle(tv_set, (180, 170, 160), (24, 15), 2) # TV dial 2
    pygame.draw.line(tv_set, (160, 160, 170), (10, 4), (6, 0), 1) # TV antenna
    pygame.draw.line(tv_set, (160, 160, 170), (22, 4), (26, 0), 1)
    cached_tiles["tv_set"] = tv_set

    # Cozy Bedroom Bed
    bed = floor_house.copy()
    pygame.draw.rect(bed, (130, 80, 40), (4, 2, 24, 28), border_radius=3) # Wooden frame
    pygame.draw.rect(bed, (220, 55, 55), (6, 8, 20, 20), border_radius=2) # Red quilt
    pygame.draw.rect(bed, (248, 248, 252), (7, 4, 18, 7), border_radius=2) # White pillow
    pygame.draw.line(bed, (180, 30, 30), (6, 16), (25, 16), 1)
    cached_tiles["bed"] = bed

    # Kitchen Sink / Stove Counter
    kitchen_sink = floor_house.copy()
    pygame.draw.rect(kitchen_sink, (180, 140, 100), (2, 2, T - 4, T - 4), border_radius=2)
    pygame.draw.rect(kitchen_sink, (215, 220, 225), (4, 4, 14, 14), border_radius=1) # Metal sink basin
    pygame.draw.rect(kitchen_sink, (140, 150, 160), (6, 6, 10, 10))
    pygame.draw.circle(kitchen_sink, (240, 200, 60), (11, 3), 2) # Faucet tap
    # Kettle / Stove on right
    pygame.draw.circle(kitchen_sink, (40, 40, 45), (23, 11), 4)
    pygame.draw.circle(kitchen_sink, (220, 40, 40), (23, 11), 2)
    cached_tiles["kitchen_sink"] = kitchen_sink

    # Potted House Plant
    potted_plant = floor_house.copy()
    pygame.draw.rect(potted_plant, (190, 85, 45), (9, 14, 14, 14), border_radius=2) # Terracotta pot
    pygame.draw.rect(potted_plant, (140, 60, 30), (8, 14, 16, 3))
    # Green leafy foliage
    pygame.draw.circle(potted_plant, (35, 130, 45), (16, 9), 7)
    pygame.draw.circle(potted_plant, (65, 180, 70), (14, 7), 5)
    pygame.draw.circle(potted_plant, (65, 180, 70), (19, 9), 4)
    cached_tiles["potted_plant"] = potted_plant

    # Medical Clinic Floor for PokéCenter
    floor_center = pygame.Surface((T, T))
    floor_center.fill((246, 248, 252)) # Glossy white medical clinic tile
    pygame.draw.rect(floor_center, (220, 230, 245), (0, 0, T, T), 1)
    pygame.draw.rect(floor_center, (235, 242, 255), (2, 2, T - 4, T - 4), 1)
    cached_tiles["floor_center"] = floor_center

    # Commercial Floor for PokéMart
    floor_mart = pygame.Surface((T, T))
    floor_mart.fill((238, 244, 252)) # Crisp commercial tile
    pygame.draw.rect(floor_mart, (195, 215, 240), (0, 0, T, T), 1)
    cached_tiles["floor_mart"] = floor_mart

    # High-Tech Stainless Steel Grating for Labs
    floor_lab = pygame.Surface((T, T))
    floor_lab.fill((220, 228, 238))
    for gy_i in range(0, T, 8):
        pygame.draw.line(floor_lab, (190, 200, 215), (0, gy_i), (T, gy_i), 1)
        pygame.draw.line(floor_lab, (190, 200, 215), (gy_i, 0), (gy_i, T), 1)
    cached_tiles["floor_lab"] = floor_lab

    # Sign
    sign = grass.copy()
    pygame.draw.rect(sign, (140, 90, 50), (6, 8, 20, 14), border_radius=2)
    pygame.draw.rect(sign, (230, 210, 160), (8, 10, 16, 10))
    pygame.draw.rect(sign, (100, 60, 30), (14, 22, 4, 10))
    cached_tiles["sign"] = sign

    # Indoor Counter
    counter = pygame.Surface((T, T))
    counter.fill((160, 100, 60))
    pygame.draw.rect(counter, (200, 140, 90), (2, 2, T - 4, 6))
    pygame.draw.rect(counter, (120, 70, 35), (0, 0, T, T), 2)
    cached_tiles["counter"] = counter

    # 13. Bridge / Wood Pier
    bridge = pygame.Surface((T, T))
    bridge.fill((190, 145, 95)) # Warm wood
    pygame.draw.line(bridge, (140, 95, 55), (0, 0), (T, 0), 2)
    pygame.draw.line(bridge, (140, 95, 55), (0, T // 2), (T, T // 2), 2)
    pygame.draw.line(bridge, (140, 95, 55), (0, T - 1), (T, T - 1), 2)
    pygame.draw.line(bridge, (100, 65, 35), (8, 0), (8, T), 1)
    pygame.draw.line(bridge, (100, 65, 35), (24, 0), (24, T), 1)
    cached_tiles["bridge"] = bridge

    # 14. Gym Arena Floor & Mat
    gym_floor = pygame.Surface((T, T))
    gym_floor.fill((215, 180, 130)) # Polished gym hardwood
    pygame.draw.line(gym_floor, (185, 150, 100), (0, 0), (T, 0), 1)
    pygame.draw.line(gym_floor, (185, 150, 100), (0, T - 1), (T, T - 1), 1)
    cached_tiles["gym_floor"] = gym_floor

    gym_mat = gym_floor.copy()
    pygame.draw.circle(gym_mat, (220, 50, 50), (T // 2, T // 2), 12)
    pygame.draw.circle(gym_mat, WHITE, (T // 2, T // 2), 6)
    pygame.draw.circle(gym_mat, BLACK, (T // 2, T // 2), 2)
    cached_tiles["gym_mat"] = gym_mat

    # 15. Gym Statue
    gym_statue = gym_floor.copy()
    pygame.draw.rect(gym_statue, (140, 140, 150), (6, 12, 20, 18), border_radius=2)
    pygame.draw.polygon(gym_statue, (170, 170, 180), [(16, 2), (6, 14), (26, 14)])
    pygame.draw.rect(gym_statue, (240, 200, 60), (10, 20, 12, 6)) # Gold plaque
    cached_tiles["gym_statue"] = gym_statue

    # 16. Oak Lab Furniture (Table, Bookshelf)
    lab_floor = floor.copy()
    table = lab_floor.copy()
    pygame.draw.rect(table, (100, 140, 180), (4, 4, T - 8, T - 8), border_radius=3)
    pygame.draw.rect(table, (200, 230, 255), (8, 8, 8, 8)) # Screen
    pygame.draw.circle(table, (220, 60, 60), (22, 12), 3) # Red bulb
    cached_tiles["lab_table"] = table

    bookshelf = floor.copy()
    pygame.draw.rect(bookshelf, (130, 80, 45), (2, 2, T - 4, T - 4), border_radius=2)
    pygame.draw.rect(bookshelf, (200, 70, 70), (4, 6, 6, 8))
    pygame.draw.rect(bookshelf, (70, 120, 200), (12, 6, 6, 8))
    pygame.draw.rect(bookshelf, (70, 180, 90), (20, 6, 6, 8))
    pygame.draw.rect(bookshelf, (220, 180, 50), (4, 18, 7, 8))
    pygame.draw.rect(bookshelf, (160, 90, 180), (13, 18, 7, 8))
    cached_tiles["bookshelf"] = bookshelf

    # 17. Overworld Item Pokeball
    item_ball = grass.copy()
    cx, cy = T // 2, T // 2 + 2
    pygame.draw.ellipse(item_ball, (0, 0, 0, 80), (cx - 7, cy + 4, 14, 5))
    pygame.draw.circle(item_ball, (225, 45, 45), (cx, cy), 6) # Top red
    pygame.draw.arc(item_ball, WHITE, (cx - 6, cy - 6, 12, 12), 3.14, 0, 6)
    pygame.draw.circle(item_ball, WHITE, (cx, cy + 3), 3)
    pygame.draw.line(item_ball, BLACK, (cx - 6, cy), (cx + 6, cy), 1)
    pygame.draw.circle(item_ball, BLACK, (cx, cy), 2)
    pygame.draw.circle(item_ball, WHITE, (cx, cy), 1)
    cached_tiles["item_ball"] = item_ball

    # ==========================================
    # 18. BIOME: Glacial Ice Cavern (Seafoam Islands)
    # ==========================================
    ice_floor = pygame.Surface((T, T))
    ice_floor.fill((150, 220, 245)) # Glistening frozen ice
    pygame.draw.line(ice_floor, (210, 245, 255), (2, 4), (18, 4), 2)
    pygame.draw.line(ice_floor, (210, 245, 255), (14, 18), (28, 18), 2)
    pygame.draw.line(ice_floor, (110, 180, 215), (0, T - 1), (T, T - 1), 1)
    for _ in range(6):
        rx, ry = random.randint(2, T - 4), random.randint(2, T - 4)
        ice_floor.set_at((rx, ry), (240, 252, 255))
    cached_tiles["ice_floor"] = ice_floor

    ice_wall = pygame.Surface((T, T))
    ice_wall.fill((40, 95, 145))
    pygame.draw.rect(ice_wall, (70, 145, 200), (2, 2, T - 4, T - 4), border_radius=4)
    pygame.draw.polygon(ice_wall, (25, 65, 105), [(4, 4), (16, 2), (28, 8), (20, 28), (6, 24)])
    pygame.draw.polygon(ice_wall, (120, 205, 245), [(8, 8), (18, 6), (24, 12), (18, 22), (10, 18)])
    pygame.draw.line(ice_wall, (220, 245, 255), (10, 8), (16, 6), 2)
    cached_tiles["ice_wall"] = ice_wall

    ice_door = ice_wall.copy()
    pygame.draw.arc(ice_door, (15, 35, 60), (6, 4, 20, 26), 0, 3.14, 10)
    pygame.draw.rect(ice_door, (15, 35, 60), (6, 12, 20, 20))
    cached_tiles["ice_door"] = ice_door

    # ==========================================
    # 19. BIOME: Spooky Lavender Mist & Ghost Tower
    # ==========================================
    lavender_ground = pygame.Surface((T, T))
    lavender_ground.fill((110, 90, 135)) # Eerie purple soil
    for _ in range(8):
        rx, ry = random.randint(2, T - 3), random.randint(2, T - 3)
        lavender_ground.set_at((rx, ry), (135, 115, 165))
        lavender_ground.set_at((rx + 1, ry), (85, 65, 110))
    cached_tiles["lavender_ground"] = lavender_ground

    spooky_floor = pygame.Surface((T, T))
    spooky_floor.fill((85, 75, 105)) # Haunted purple-grey floorboards
    pygame.draw.line(spooky_floor, (60, 50, 75), (0, 0), (T, 0), 1)
    pygame.draw.line(spooky_floor, (60, 50, 75), (0, T - 1), (T, T - 1), 1)
    cached_tiles["spooky_floor"] = spooky_floor

    tombstone = spooky_floor.copy()
    pygame.draw.rect(tombstone, (145, 140, 155), (8, 8, 16, 20), border_radius=4)
    pygame.draw.rect(tombstone, (110, 105, 120), (6, 24, 20, 6), border_radius=2)
    pygame.draw.line(tombstone, (75, 70, 85), (16, 11), (16, 21), 2) # Cross vertical
    pygame.draw.line(tombstone, (75, 70, 85), (12, 14), (20, 14), 2) # Cross horizontal
    cached_tiles["tombstone"] = tombstone

    spooky_tree = lavender_ground.copy()
    pygame.draw.rect(spooky_tree, (45, 30, 55), (13, 10, 6, 18), border_radius=2)
    pygame.draw.circle(spooky_tree, (55, 40, 65), (16, 10), 10)
    pygame.draw.circle(spooky_tree, (75, 55, 90), (14, 8), 6)
    cached_tiles["spooky_tree"] = spooky_tree

    # ==========================================
    # 20. BIOME: Industrial Electric Power Plant
    # ==========================================
    metal_floor = pygame.Surface((T, T))
    metal_floor.fill((90, 100, 115)) # Steel diamond plate
    pygame.draw.rect(metal_floor, (120, 130, 145), (0, 0, T, T), 1)
    for dx in [6, 22]:
        for dy in [6, 22]:
            pygame.draw.rect(metal_floor, (60, 65, 75), (dx, dy, 4, 4))
            pygame.draw.rect(metal_floor, (140, 150, 165), (dx, dy, 2, 2))
    cached_tiles["metal_floor"] = metal_floor

    generator_coil = metal_floor.copy()
    pygame.draw.rect(generator_coil, (40, 45, 55), (4, 4, T - 8, T - 8), border_radius=3)
    pygame.draw.circle(generator_coil, (220, 140, 40), (16, 16), 9) # Copper core
    pygame.draw.circle(generator_coil, (255, 220, 60), (16, 16), 5) # Glowing electrical spark
    pygame.draw.circle(generator_coil, WHITE, (16, 16), 2)
    cached_tiles["generator_coil"] = generator_coil

    warning_tile = pygame.Surface((T, T))
    warning_tile.fill((235, 195, 30)) # Caution yellow
    for offset in range(-T, T * 2, 8):
        pygame.draw.polygon(warning_tile, (35, 35, 40), [(offset, 0), (offset + 4, 0), (offset + 4 + T, T), (offset + T, T)])
    cached_tiles["warning_tile"] = warning_tile

    # ==========================================
    # 21. BIOME: Golden Savanna Safari Zone
    # ==========================================
    savanna_grass = pygame.Surface((T, T))
    savanna_grass.fill((215, 190, 115)) # Warm amber savanna soil
    for _ in range(8):
        rx, ry = random.randint(2, T - 3), random.randint(2, T - 3)
        savanna_grass.set_at((rx, ry), (235, 210, 135))
        savanna_grass.set_at((rx + 1, ry), (185, 160, 90))
    cached_tiles["savanna_grass"] = savanna_grass

    savanna_tall_grass = savanna_grass.copy()
    for x in [4, 12, 20, 28]:
        for y in [6, 18]:
            pygame.draw.polygon(savanna_tall_grass, (165, 135, 55), [(x - 3, y + 10), (x, y), (x + 3, y + 10)])
            pygame.draw.polygon(savanna_tall_grass, (200, 170, 75), [(x - 2, y + 10), (x, y + 2), (x + 2, y + 10)])
    cached_tiles["savanna_tall_grass"] = savanna_tall_grass

    acacia_tree = savanna_grass.copy()
    pygame.draw.rect(acacia_tree, (110, 70, 40), (14, 12, 4, 18))
    pygame.draw.ellipse(acacia_tree, (60, 110, 50), (4, 4, 24, 10))
    pygame.draw.ellipse(acacia_tree, (80, 140, 65), (6, 2, 20, 8))
    cached_tiles["acacia_tree"] = acacia_tree

    # ==========================================
    # 22. BIOME: Canyon / Badlands
    # ==========================================
    canyon_dirt = pygame.Surface((T, T))
    canyon_dirt.fill((190, 125, 80)) # Reddish desert trail
    for _ in range(10):
        rx, ry = random.randint(1, T - 2), random.randint(1, T - 2)
        canyon_dirt.set_at((rx, ry), (170, 105, 65))
        if random.random() < 0.3:
            canyon_dirt.set_at((rx, ry), (215, 150, 105))
    cached_tiles["canyon_dirt"] = canyon_dirt

    canyon_rock = pygame.Surface((T, T))
    canyon_rock.fill((140, 65, 40)) # Terraced sedimentary canyon rock
    pygame.draw.rect(canyon_rock, (170, 85, 55), (2, 2, T - 4, T - 4), border_radius=3)
    pygame.draw.line(canyon_rock, (110, 45, 25), (0, 10), (T, 10), 2)
    pygame.draw.line(canyon_rock, (200, 105, 70), (0, 18), (T, 18), 2)
    cached_tiles["canyon_rock"] = canyon_rock

    # ==========================================
    # 23. WALK-THROUGH ENCOUNTER PROPS
    # ==========================================
    # A. Wildflower Meadow ('F' / '*')
    flower_meadow = grass.copy()
    # Stems and leafy foliage
    pygame.draw.line(flower_meadow, (35, 110, 30), (8, 14), (8, 22), 2)
    pygame.draw.line(flower_meadow, (35, 110, 30), (22, 10), (22, 18), 2)
    pygame.draw.line(flower_meadow, (35, 110, 30), (15, 20), (15, 28), 2)
    # Red Bloom
    pygame.draw.circle(flower_meadow, (240, 50, 60), (8, 12), 4)
    pygame.draw.circle(flower_meadow, (255, 230, 60), (8, 12), 2)
    # Sky Blue Bloom
    pygame.draw.circle(flower_meadow, (60, 165, 245), (22, 9), 4)
    pygame.draw.circle(flower_meadow, WHITE, (22, 9), 2)
    # Gold Bloom
    pygame.draw.circle(flower_meadow, (250, 205, 40), (15, 20), 4)
    pygame.draw.circle(flower_meadow, (230, 100, 20), (15, 20), 2)
    # Cherry Pink mini-blooms
    pygame.draw.circle(flower_meadow, (255, 120, 190), (25, 24), 3)
    pygame.draw.circle(flower_meadow, WHITE, (25, 24), 1)
    pygame.draw.circle(flower_meadow, (255, 120, 190), (5, 25), 3)
    pygame.draw.circle(flower_meadow, WHITE, (5, 25), 1)
    cached_tiles["flower_meadow"] = flower_meadow

    # B. Autumn Leaf Pile ('L')
    leaf_pile = grass.copy()
    # Scattered autumn leaves
    # Orange maple leaf
    pygame.draw.polygon(leaf_pile, (230, 115, 35), [(8, 6), (12, 12), (10, 16), (4, 14), (4, 8)])
    pygame.draw.line(leaf_pile, (170, 70, 20), (8, 8), (10, 16), 1)
    # Crimson oak leaf
    pygame.draw.polygon(leaf_pile, (200, 45, 40), [(22, 14), (26, 8), (28, 14), (24, 20), (20, 16)])
    pygame.draw.line(leaf_pile, (140, 25, 20), (24, 10), (22, 18), 1)
    # Golden aspen leaf
    pygame.draw.polygon(leaf_pile, (240, 195, 45), [(14, 18), (18, 14), (20, 22), (16, 26), (12, 22)])
    pygame.draw.line(leaf_pile, (180, 130, 25), (16, 16), (16, 24), 1)
    # Russet small leaves
    pygame.draw.ellipse(leaf_pile, (145, 75, 35), (4, 22, 7, 5))
    pygame.draw.ellipse(leaf_pile, (225, 140, 50), (22, 24, 6, 4))
    cached_tiles["leaf_pile"] = leaf_pile

    # C. Cave Rubble / Crags ('r')
    cave_rubble = cave_floor.copy()
    # Large jagged stone
    pygame.draw.polygon(cave_rubble, (125, 115, 110), [(6, 10), (14, 6), (18, 12), (12, 18), (4, 14)])
    pygame.draw.polygon(cave_rubble, (160, 150, 145), [(7, 9), (13, 7), (16, 11), (12, 12)])
    pygame.draw.polygon(cave_rubble, (55, 48, 45), [(4, 14), (12, 18), (10, 20), (3, 16)])
    # Medium rock
    pygame.draw.polygon(cave_rubble, (110, 100, 95), [(20, 16), (27, 13), (29, 21), (22, 25)])
    pygame.draw.polygon(cave_rubble, (145, 135, 130), [(21, 15), (26, 14), (27, 19)])
    # Small gravel & quartz chips
    pygame.draw.circle(cave_rubble, (215, 215, 225), (9, 24), 2)
    pygame.draw.circle(cave_rubble, (215, 215, 225), (22, 8), 2)
    pygame.draw.circle(cave_rubble, (80, 70, 65), (16, 26), 2)
    cached_tiles["cave_rubble"] = cave_rubble

    # D. Snow Drift ('x')
    snow_drift = pygame.Surface((T, T))
    snow_drift.fill((232, 246, 255)) # Soft powder snow
    # Gentle cyan drift curves
    pygame.draw.ellipse(snow_drift, (190, 225, 248), (2, 8, 28, 14))
    pygame.draw.ellipse(snow_drift, (248, 252, 255), (4, 6, 24, 12))
    pygame.draw.ellipse(snow_drift, (180, 218, 245), (6, 18, 22, 12))
    pygame.draw.ellipse(snow_drift, (255, 255, 255), (8, 16, 18, 10))
    # Glistening frost sparkles
    pygame.draw.circle(snow_drift, (255, 255, 255), (10, 10), 2)
    pygame.draw.line(snow_drift, (130, 205, 255), (10, 8), (10, 12), 1)
    pygame.draw.line(snow_drift, (130, 205, 255), (8, 10), (12, 10), 1)
    pygame.draw.circle(snow_drift, (255, 255, 255), (22, 20), 2)
    cached_tiles["snow_drift"] = snow_drift

    # E. Haunted Mist / Spirit Fog ('m')
    spooky_mist = lavender_ground.copy()
    mist_layer = pygame.Surface((T, T), pygame.SRCALPHA)
    # Swirling ethereal violet bands
    pygame.draw.ellipse(mist_layer, (160, 110, 210, 130), (2, 4, 28, 12))
    pygame.draw.ellipse(mist_layer, (210, 160, 255, 160), (6, 6, 20, 8))
    pygame.draw.ellipse(mist_layer, (140, 90, 190, 140), (4, 16, 26, 12))
    pygame.draw.ellipse(mist_layer, (200, 150, 250, 170), (8, 18, 18, 8))
    # Glowing spirit orbs
    pygame.draw.circle(mist_layer, (240, 210, 255, 220), (12, 10), 2)
    pygame.draw.circle(mist_layer, (240, 210, 255, 220), (22, 22), 2)
    spooky_mist.blit(mist_layer, (0, 0))
    cached_tiles["spooky_mist"] = spooky_mist

    # F. Volcanic Ash & Embers ('a')
    volcanic_ash = pygame.Surface((T, T))
    volcanic_ash.fill((52, 45, 50)) # Charcoal dark basalt
    # Ash soot mounds
    pygame.draw.ellipse(volcanic_ash, (78, 68, 74), (2, 6, 18, 10))
    pygame.draw.ellipse(volcanic_ash, (70, 62, 66), (14, 16, 16, 12))
    # Glowing volcanic embers
    pygame.draw.circle(volcanic_ash, (255, 60, 20), (8, 10), 3)
    pygame.draw.circle(volcanic_ash, (255, 200, 50), (8, 10), 1)
    pygame.draw.circle(volcanic_ash, (255, 80, 20), (22, 20), 3)
    pygame.draw.circle(volcanic_ash, (255, 220, 80), (22, 20), 1)
    pygame.draw.circle(volcanic_ash, (240, 40, 10), (16, 14), 2)
    cached_tiles["volcanic_ash"] = volcanic_ash

    # G. Swamp Marsh / Mud Bog ('u')
    swamp_marsh = pygame.Surface((T, T))
    swamp_marsh.fill((58, 105, 90)) # Deep murky marsh water
    # Mud banks
    pygame.draw.ellipse(swamp_marsh, (98, 76, 48), (0, 0, 16, 12))
    pygame.draw.ellipse(swamp_marsh, (98, 76, 48), (14, 18, 18, 14))
    # Water ripples
    pygame.draw.arc(swamp_marsh, (110, 175, 155), (4, 12, 14, 6), 0, 3.14, 1)
    pygame.draw.arc(swamp_marsh, (110, 175, 155), (16, 8, 12, 5), 0, 3.14, 1)
    # Lily pad
    pygame.draw.ellipse(swamp_marsh, (45, 155, 65), (6, 18, 9, 6))
    pygame.draw.circle(swamp_marsh, (255, 140, 180), (10, 20), 2) # Lily flower
    # Cattail reeds
    pygame.draw.line(swamp_marsh, (35, 110, 45), (25, 6), (25, 16), 2)
    pygame.draw.rect(swamp_marsh, (120, 65, 25), (24, 4, 3, 6), border_radius=1)
    cached_tiles["swamp_marsh"] = swamp_marsh

    # H. Electric Surge Grid ('e')
    electric_surge = pygame.Surface((T, T))
    electric_surge.fill((55, 62, 75)) # Dark industrial conduit metal
    pygame.draw.rect(electric_surge, (85, 95, 115), (0, 0, T, T), 1)
    # Glowing circuit grid lines
    pygame.draw.line(electric_surge, (40, 190, 240), (0, 16), (T, 16), 2)
    pygame.draw.line(electric_surge, (40, 190, 240), (16, 0), (16, T), 2)
    # Central energy capacitor
    pygame.draw.rect(electric_surge, (30, 35, 45), (10, 10, 12, 12), border_radius=2)
    pygame.draw.circle(electric_surge, (255, 235, 60), (16, 16), 4) # Electric core
    pygame.draw.circle(electric_surge, WHITE, (16, 16), 2)
    # Electric spark lightning bolts
    pygame.draw.lines(electric_surge, (255, 240, 80), False, [(6, 6), (10, 10), (8, 14), (12, 16)], 2)
    pygame.draw.lines(electric_surge, (120, 240, 255), False, [(26, 26), (22, 22), (24, 18), (20, 16)], 2)
    cached_tiles["electric_surge"] = electric_surge

    # ==========================================
    # 24. IMMERSIVE LOWER-BODY FOOT OVERLAYS
    # ==========================================
    # Rendered over the lower portion of the player when standing in walk-through props

    # Grass overlay
    ol_grass = pygame.Surface((T, T), pygame.SRCALPHA)
    for x in [4, 10, 16, 22, 28]:
        pygame.draw.polygon(ol_grass, (45, 130, 40), [(x - 2, T), (x, T - 12), (x + 2, T)])
        pygame.draw.polygon(ol_grass, (75, 175, 60), [(x - 1, T), (x, T - 10), (x + 1, T)])
    prop_overlays['G'] = ol_grass

    # Flower meadow overlay
    ol_flower = pygame.Surface((T, T), pygame.SRCALPHA)
    for x, col in [(6, (240, 50, 60)), (14, (60, 165, 245)), (22, (250, 205, 40)), (28, (255, 120, 190))]:
        pygame.draw.line(ol_flower, (35, 110, 30), (x, T), (x, T - 10), 2)
        pygame.draw.circle(ol_flower, col, (x, T - 10), 4)
        pygame.draw.circle(ol_flower, WHITE, (x, T - 10), 1)
    prop_overlays['F'] = ol_flower
    prop_overlays['*'] = ol_flower

    # Autumn leaves overlay
    ol_leaf = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.polygon(ol_leaf, (230, 115, 35), [(4, T - 2), (8, T - 10), (12, T - 2)])
    pygame.draw.polygon(ol_leaf, (200, 45, 40), [(14, T - 2), (18, T - 8), (22, T - 2)])
    pygame.draw.polygon(ol_leaf, (240, 195, 45), [(22, T - 2), (26, T - 9), (30, T - 2)])
    prop_overlays['L'] = ol_leaf

    # Cave rubble overlay
    ol_rubble = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.polygon(ol_rubble, (130, 120, 115), [(4, T), (8, T - 8), (14, T)])
    pygame.draw.polygon(ol_rubble, (110, 100, 95), [(18, T), (24, T - 7), (29, T)])
    pygame.draw.circle(ol_rubble, (215, 215, 225), (16, T - 4), 2)
    prop_overlays['r'] = ol_rubble

    # Snow drift overlay (snow covering boots up to shins)
    ol_snow = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.ellipse(ol_snow, (190, 225, 248), (2, T - 14, 28, 14))
    pygame.draw.ellipse(ol_snow, (255, 255, 255), (4, T - 12, 24, 12))
    pygame.draw.circle(ol_snow, (130, 205, 255), (10, T - 8), 1)
    pygame.draw.circle(ol_snow, (130, 205, 255), (22, T - 8), 1)
    prop_overlays['x'] = ol_snow

    # Haunted mist overlay (wisps drifting around lower body)
    ol_mist = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.ellipse(ol_mist, (160, 110, 210, 140), (2, T - 18, 28, 14))
    pygame.draw.ellipse(ol_mist, (210, 160, 255, 170), (6, T - 14, 20, 10))
    pygame.draw.circle(ol_mist, (240, 210, 255, 220), (12, T - 12), 2)
    pygame.draw.circle(ol_mist, (240, 210, 255, 220), (20, T - 10), 2)
    prop_overlays['m'] = ol_mist

    # Volcanic ash overlay
    ol_ash = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.ellipse(ol_ash, (78, 68, 74), (2, T - 10, 28, 10))
    pygame.draw.circle(ol_ash, (255, 60, 20), (8, T - 6), 3)
    pygame.draw.circle(ol_ash, (255, 200, 50), (8, T - 6), 1)
    pygame.draw.circle(ol_ash, (255, 80, 20), (22, T - 5), 3)
    pygame.draw.circle(ol_ash, (255, 220, 80), (22, T - 5), 1)
    prop_overlays['a'] = ol_ash

    # Swamp marsh overlay (mud & water splash)
    ol_marsh = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.ellipse(ol_marsh, (58, 105, 90, 180), (2, T - 12, 28, 12))
    pygame.draw.arc(ol_marsh, (120, 185, 170), (4, T - 10, 14, 6), 0, 3.14, 2)
    pygame.draw.arc(ol_marsh, (120, 185, 170), (16, T - 8, 12, 5), 0, 3.14, 2)
    pygame.draw.circle(ol_marsh, (45, 155, 65), (8, T - 6), 3)
    prop_overlays['u'] = ol_marsh

    # Electric surge grid overlay (static arcs around boots)
    ol_spark = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.lines(ol_spark, (255, 240, 80), False, [(6, T - 2), (10, T - 8), (8, T - 12), (12, T - 14)], 2)
    pygame.draw.lines(ol_spark, (120, 240, 255), False, [(26, T - 2), (22, T - 8), (24, T - 12), (20, T - 14)], 2)
    pygame.draw.circle(ol_spark, (255, 255, 255), (12, T - 14), 2)
    pygame.draw.circle(ol_spark, (255, 255, 255), (20, T - 14), 2)
    prop_overlays['e'] = ol_spark




    return cached_tiles, prop_overlays
