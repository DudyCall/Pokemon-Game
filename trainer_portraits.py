"""
trainer_portraits.py - Procedural pixel-art character portraits for trainers and Gym Leaders.
"""
import pygame
from constants import WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY, TILE_SIZE

def generate_trainer_portrait(identifier, size=(96, 96), is_talking=False):
    """
    Generates and caches rich, high-resolution procedural pixel-art character portraits
    for all trainers, Gym Leaders, Team Rocket, and story NPCs.
    """
    if isinstance(identifier, dict):
        raw_id = identifier.get("id") or identifier.get("name") or "trainer"
    elif identifier:
        raw_id = str(identifier)
    else:
        raw_id = "trainer"

    norm_id = raw_id.lower()

    # Canvas Resolution: 96x96
    W, H = 96, 96
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx, cy = W // 2, H // 2

    # -------------------------------------------------------------
    # Determine Character Role / Class Attributes
    # -------------------------------------------------------------
    # Default Palettes
    bg_gradient_top = (45, 55, 80)
    bg_gradient_bot = (20, 25, 40)
    border_col = (180, 195, 220)
    border_highlight = (240, 245, 255)
    skin_col = (255, 218, 185) # Warm peach
    hair_col = (75, 45, 30) # Brown
    shirt_col = (220, 60, 50)
    vest_col = None
    hat_col = None
    has_glasses = False
    has_rocket_r = False
    is_female = False
    is_brock = False
    is_misty = False
    is_blue = False
    is_rocket = False
    is_nurse = False
    is_oak = False
    is_bill = False
    is_hiker = False
    is_bug_catcher = False
    is_blackbelt = False
    is_channeler = False
    is_engineer = False
    is_fisherman = False
    is_item = False
    is_sign = False

    if "brock" in norm_id:
        is_brock = True
        bg_gradient_top = (130, 120, 105)
        bg_gradient_bot = (60, 55, 50)
        border_col = (220, 180, 50) # Gym Leader Gold
        border_highlight = (255, 235, 120)
        skin_col = (215, 165, 120) # Tan
        hair_col = (55, 35, 25)
        shirt_col = (45, 105, 55) # Green vest
        vest_col = (165, 120, 65) # Tan vest

    elif "misty" in norm_id:
        is_misty = True
        is_female = True
        bg_gradient_top = (60, 160, 235)
        bg_gradient_bot = (20, 80, 160)
        border_col = (220, 180, 50) # Gym Leader Gold
        border_highlight = (255, 235, 120)
        skin_col = (255, 225, 205)
        hair_col = (240, 100, 30) # Bright orange
        shirt_col = (255, 230, 60) # Yellow top

    elif "blue" in norm_id or "rival" in norm_id:
        is_blue = True
        bg_gradient_top = (65, 75, 140)
        bg_gradient_bot = (25, 30, 75)
        border_col = (80, 200, 255) # Electric Cyan
        border_highlight = (190, 240, 255)
        skin_col = (255, 220, 185)
        hair_col = (140, 70, 30) # Auburn brown
        shirt_col = (65, 45, 95) # Dark purple long sleeve

    elif "rocket" in norm_id:
        is_rocket = True
        has_rocket_r = True
        bg_gradient_top = (50, 50, 60)
        bg_gradient_bot = (20, 20, 25)
        border_col = (220, 40, 40) # Team Rocket Red
        border_highlight = (255, 100, 100)
        skin_col = (245, 215, 195)
        hair_col = (35, 35, 45)
        shirt_col = (25, 25, 30)
        hat_col = (25, 25, 30)

    elif "youngster" in norm_id:
        bg_gradient_top = (70, 140, 220)
        bg_gradient_bot = (30, 70, 140)
        border_col = (240, 180, 50)
        border_highlight = (255, 235, 150)
        skin_col = (255, 220, 185)
        hair_col = (90, 55, 35)
        shirt_col = (240, 190, 40)
        hat_col = (220, 50, 40)

    elif "bug" in norm_id:
        is_bug_catcher = True
        bg_gradient_top = (70, 150, 65)
        bg_gradient_bot = (25, 75, 30)
        border_col = (130, 210, 80)
        border_highlight = (200, 255, 160)
        skin_col = (255, 220, 185)
        hair_col = (100, 65, 35)
        shirt_col = (245, 245, 245)
        vest_col = (65, 135, 55)
        hat_col = (225, 195, 120) # Straw hat

    elif "lass" in norm_id or "picnicker" in norm_id:
        is_female = True
        bg_gradient_top = (235, 130, 165)
        bg_gradient_bot = (140, 50, 95)
        border_col = (255, 180, 210)
        border_highlight = (255, 235, 245)
        skin_col = (255, 225, 205)
        hair_col = (120, 60, 40)
        shirt_col = (255, 120, 160)

    elif "camper" in norm_id:
        bg_gradient_top = (110, 145, 95)
        bg_gradient_bot = (45, 75, 45)
        border_col = (180, 205, 140)
        border_highlight = (235, 245, 210)
        skin_col = (255, 215, 180)
        hair_col = (85, 50, 30)
        shirt_col = (195, 175, 125) # Khaki
        hat_col = (85, 130, 75)

    elif "hiker" in norm_id:
        is_hiker = True
        bg_gradient_top = (165, 105, 60)
        bg_gradient_bot = (85, 45, 25)
        border_col = (220, 150, 90)
        border_highlight = (255, 210, 160)
        skin_col = (225, 175, 130) # Rugged tan
        hair_col = (65, 40, 25)
        shirt_col = (235, 120, 35) # Orange vest
        hat_col = (185, 160, 115) # Safari hat

    elif "blackbelt" in norm_id or "karate" in norm_id:
        is_blackbelt = True
        bg_gradient_top = (180, 50, 45)
        bg_gradient_bot = (75, 20, 20)
        border_col = (240, 90, 80)
        border_highlight = (255, 180, 170)
        skin_col = (235, 185, 145)
        hair_col = (30, 30, 35)
        shirt_col = (245, 245, 250) # White gi

    elif "swimmer" in norm_id or "fisherman" in norm_id:
        is_fisherman = True
        bg_gradient_top = (50, 140, 195)
        bg_gradient_bot = (20, 65, 115)
        border_col = (100, 195, 245)
        border_highlight = (205, 240, 255)
        skin_col = (240, 195, 155)
        hair_col = (80, 50, 35)
        shirt_col = (45, 115, 185)
        hat_col = (175, 155, 115) # Bucket hat

    elif "scientist" in norm_id or "nerd" in norm_id:
        has_glasses = True
        bg_gradient_top = (75, 115, 155)
        bg_gradient_bot = (30, 55, 80)
        border_col = (140, 190, 235)
        border_highlight = (220, 240, 255)
        skin_col = (250, 220, 195)
        hair_col = (85, 55, 40)
        shirt_col = (245, 248, 255) # Lab coat

    elif "firebreather" in norm_id:
        bg_gradient_top = (215, 75, 30)
        bg_gradient_bot = (95, 25, 15)
        border_col = (255, 140, 50)
        border_highlight = (255, 220, 120)
        skin_col = (235, 180, 140)
        hair_col = (220, 45, 20) # Fiery red
        shirt_col = (35, 35, 40) # Leather vest

    elif "channeler" in norm_id:
        is_channeler = True
        is_female = True
        bg_gradient_top = (110, 60, 160)
        bg_gradient_bot = (45, 20, 75)
        border_col = (195, 130, 245)
        border_highlight = (240, 210, 255)
        skin_col = (240, 220, 230) # Ghostly pale
        hair_col = (75, 45, 105)
        shirt_col = (95, 55, 135) # Spirit robes
        hat_col = (85, 45, 125) # Veil

    elif "engineer" in norm_id:
        is_engineer = True
        bg_gradient_top = (185, 155, 45)
        bg_gradient_bot = (65, 55, 20)
        border_col = (245, 215, 60)
        border_highlight = (255, 245, 160)
        skin_col = (230, 185, 145)
        hair_col = (60, 45, 35)
        shirt_col = (235, 125, 35) # Orange overalls
        hat_col = (245, 210, 30) # Yellow hardhat

    elif "joy" in norm_id or "nurse" in norm_id or "healer" in norm_id:
        is_nurse = True
        is_female = True
        bg_gradient_top = (255, 190, 215)
        bg_gradient_bot = (190, 100, 140)
        border_col = (255, 150, 190)
        border_highlight = (255, 230, 245)
        skin_col = (255, 228, 215)
        hair_col = (255, 130, 175) # Pink hair
        shirt_col = (255, 245, 250)

    elif "oak" in norm_id:
        is_oak = True
        bg_gradient_top = (145, 80, 65)
        bg_gradient_bot = (65, 35, 30)
        border_col = (225, 165, 115)
        border_highlight = (255, 235, 205)
        skin_col = (245, 215, 185)
        hair_col = (175, 180, 190) # Distinguished gray
        shirt_col = (190, 45, 45) # Red polo with lab coat

    elif "bill" in norm_id:
        is_bill = True
        bg_gradient_top = (45, 155, 175)
        bg_gradient_bot = (20, 75, 95)
        border_col = (80, 225, 245)
        border_highlight = (200, 255, 255)
        skin_col = (255, 220, 190)
        hair_col = (30, 185, 215) # Cyan hair
        shirt_col = (235, 210, 65)

    elif "mom" in norm_id:
        is_female = True
        bg_gradient_top = (245, 185, 145)
        bg_gradient_bot = (165, 95, 65)
        border_col = (245, 195, 155)
        border_highlight = (255, 240, 225)
        skin_col = (255, 225, 200)
        hair_col = (135, 75, 45)
        shirt_col = (240, 130, 155) # Pink cardigan

    elif "clerk" in norm_id or "mart" in norm_id:
        bg_gradient_top = (60, 120, 210)
        bg_gradient_bot = (25, 60, 130)
        border_col = (245, 205, 50)
        border_highlight = (255, 240, 150)
        skin_col = (255, 220, 185)
        hair_col = (75, 45, 30)
        shirt_col = (50, 105, 200)
        hat_col = (50, 105, 200)

    elif "item" in norm_id or "ball" in norm_id:
        is_item = True
        bg_gradient_top = (45, 75, 135)
        bg_gradient_bot = (15, 30, 65)
        border_col = (235, 70, 70)
        border_highlight = (255, 180, 180)

    elif "sign" in norm_id or "notice" in norm_id:
        is_sign = True
        bg_gradient_top = (145, 100, 55)
        bg_gradient_bot = (75, 45, 20)
        border_col = (205, 160, 100)
        border_highlight = (245, 220, 180)

    # -------------------------------------------------------------
    # 1. Background Card & Metallic Bevel Border Frame
    # -------------------------------------------------------------
    card_rect = pygame.Rect(4, 4, W - 8, H - 8)
    # Vertical gradient background
    for y in range(card_rect.top, card_rect.bottom):
        prog = (y - card_rect.top) / max(1, card_rect.height)
        r_c = int(bg_gradient_top[0] * (1 - prog) + bg_gradient_bot[0] * prog)
        g_c = int(bg_gradient_top[1] * (1 - prog) + bg_gradient_bot[1] * prog)
        b_c = int(bg_gradient_top[2] * (1 - prog) + bg_gradient_bot[2] * prog)
        pygame.draw.line(surf, (r_c, g_c, b_c), (card_rect.left, y), (card_rect.right, y))

    # -------------------------------------------------------------
    # Special Item / Sign Board Renderers
    # -------------------------------------------------------------
    if is_item:
        # Draw Giant Glowing Item Ball in Center
        pygame.draw.circle(surf, (255, 230, 120, 80), (cx, cy), 32)
        # Upper half red
        pygame.draw.arc(surf, (230, 45, 45), (cx - 24, cy - 24, 48, 48), 0, 3.14, 24)
        pygame.draw.rect(surf, (230, 45, 45), (cx - 24, cy - 12, 48, 12))
        # Lower half white
        pygame.draw.arc(surf, (240, 245, 255), (cx - 24, cy - 24, 48, 48), 3.14, 6.28, 24)
        pygame.draw.rect(surf, (240, 245, 255), (cx - 24, cy, 48, 12))
        # Black center dividing band
        pygame.draw.line(surf, (40, 40, 45), (cx - 24, cy), (cx + 24, cy), 5)
        # Center button
        pygame.draw.circle(surf, (40, 40, 45), (cx, cy), 9)
        pygame.draw.circle(surf, WHITE, (cx, cy), 6)
        pygame.draw.circle(surf, (200, 210, 225), (cx, cy), 3)
        # Gloss shine glint
        pygame.draw.circle(surf, WHITE, (cx - 12, cy - 12), 4)

    elif is_sign:
        # Wooden Plank Notice Sign
        pygame.draw.rect(surf, (160, 110, 60), (14, 18, W - 28, H - 36), border_radius=6)
        pygame.draw.rect(surf, (120, 75, 35), (14, 18, W - 28, H - 36), 2, border_radius=6)
        pygame.draw.line(surf, (135, 85, 45), (18, 38), (W - 18, 38), 2)
        pygame.draw.line(surf, (135, 85, 45), (18, 58), (W - 18, 58), 2)
        # Corner brass rivets
        for rx, ry in [(18, 22), (W - 22, 22), (18, H - 26), (W - 22, H - 26)]:
            pygame.draw.circle(surf, (240, 200, 80), (rx, ry), 2)
        # Center icon: Info / Note symbol
        pygame.draw.circle(surf, (255, 245, 220), (cx, cy), 14)
        pygame.draw.rect(surf, (120, 75, 35), (cx - 2, cy - 6, 4, 10))
        pygame.draw.circle(surf, (120, 75, 35), (cx, cy - 8), 2)

    # -------------------------------------------------------------
    # Character Bust Rendering (Torso, Head, Face, Hair, Headgear)
    # -------------------------------------------------------------
    else:
        # 1. Torso / Shoulders
        shoulder_y = cy + 16
        pygame.draw.ellipse(surf, shirt_col, (cx - 28, shoulder_y, 56, 36))
        pygame.draw.rect(surf, shirt_col, (cx - 28, shoulder_y + 12, 56, 24))

        # Lab Coat overlay for Scientist / Oak
        if has_glasses or is_oak:
            pygame.draw.polygon(surf, WHITE, [(cx - 28, shoulder_y + 10), (cx - 10, shoulder_y + 4), (cx - 12, H - 6), (cx - 28, H - 6)])
            pygame.draw.polygon(surf, WHITE, [(cx + 28, shoulder_y + 10), (cx + 10, shoulder_y + 4), (cx + 12, H - 6), (cx + 28, H - 6)])
            pygame.draw.line(surf, (200, 210, 225), (cx - 10, shoulder_y + 4), (cx - 12, H - 6), 2)
            pygame.draw.line(surf, (200, 210, 225), (cx + 10, shoulder_y + 4), (cx + 12, H - 6), 2)

        # Vest Overlay (Brock, Hiker, Bug Catcher)
        if vest_col:
            pygame.draw.polygon(surf, vest_col, [(cx - 26, shoulder_y + 8), (cx - 8, shoulder_y + 4), (cx - 10, H - 6), (cx - 26, H - 6)])
            pygame.draw.polygon(surf, vest_col, [(cx + 26, shoulder_y + 8), (cx + 8, shoulder_y + 4), (cx + 10, H - 6), (cx + 26, H - 6)])

        # Team Rocket Red 'R' on chest
        if has_rocket_r:
            pygame.draw.rect(surf, (220, 30, 30), (cx - 8, shoulder_y + 8, 4, 14))
            pygame.draw.circle(surf, (220, 30, 30), (cx - 4, shoulder_y + 11), 5)
            pygame.draw.circle(surf, (25, 25, 30), (cx - 4, shoulder_y + 11), 2)
            pygame.draw.polygon(surf, (220, 30, 30), [(cx - 8, shoulder_y + 14), (cx + 4, shoulder_y + 22), (cx + 7, shoulder_y + 22), (cx - 5, shoulder_y + 14)])

        # 2. Neck
        pygame.draw.rect(surf, skin_col, (cx - 6, cy + 4, 12, 16))

        # 3. Head & Ears
        head_y = cy - 8
        pygame.draw.circle(surf, skin_col, (cx, head_y), 18)
        # Ears
        pygame.draw.circle(surf, skin_col, (cx - 18, head_y + 2), 5)
        pygame.draw.circle(surf, skin_col, (cx + 18, head_y + 2), 5)

        # 4. Long hair back (drawn behind face for female/Misty/Lass)
        if is_female and not is_channeler:
            if is_misty:
                # High Side Ponytail (Right)
                pygame.draw.ellipse(surf, hair_col, (cx + 14, head_y - 26, 20, 26))
                pygame.draw.circle(surf, (40, 180, 210), (cx + 16, head_y - 12), 4) # Teal Ribbon
            else:
                # Twin Pigtails
                pygame.draw.ellipse(surf, hair_col, (cx - 26, head_y - 10, 14, 26))
                pygame.draw.ellipse(surf, hair_col, (cx + 12, head_y - 10, 14, 26))
                pygame.draw.circle(surf, (240, 60, 80), (cx - 18, head_y + 2), 3) # Ribbon
                pygame.draw.circle(surf, (240, 60, 80), (cx + 18, head_y + 2), 3)

        # 5. Eyes, Eyebrows & Cheeks
        # Blush
        pygame.draw.circle(surf, (255, 170, 170), (cx - 11, head_y + 4), 4)
        pygame.draw.circle(surf, (255, 170, 170), (cx + 11, head_y + 4), 4)

        if is_brock:
            # Iconic Slanted Closed Eyes
            pygame.draw.line(surf, (40, 30, 25), (cx - 14, head_y - 2), (cx - 4, head_y - 4), 3)
            pygame.draw.line(surf, (40, 30, 25), (cx + 4, head_y - 4), (cx + 14, head_y - 2), 3)
            # Thick determined brows
            pygame.draw.line(surf, (40, 30, 25), (cx - 15, head_y - 7), (cx - 3, head_y - 9), 3)
            pygame.draw.line(surf, (40, 30, 25), (cx + 3, head_y - 9), (cx + 15, head_y - 7), 3)

        elif is_channeler:
            # Glowing Spirit Eyes
            pygame.draw.circle(surf, (230, 190, 255), (cx - 8, head_y - 2), 4)
            pygame.draw.circle(surf, (230, 190, 255), (cx + 8, head_y - 2), 4)
            pygame.draw.circle(surf, WHITE, (cx - 8, head_y - 2), 2)
            pygame.draw.circle(surf, WHITE, (cx + 8, head_y - 2), 2)

        else:
            # Open Expressive Eyes
            eye_col = (40, 120, 210) if is_misty else ((50, 150, 80) if is_blue else (40, 45, 55))
            pygame.draw.rect(surf, (30, 35, 45), (cx - 12, head_y - 5, 7, 7), border_radius=2)
            pygame.draw.rect(surf, (30, 35, 45), (cx + 5, head_y - 5, 7, 7), border_radius=2)
            pygame.draw.rect(surf, eye_col, (cx - 11, head_y - 4, 5, 5), border_radius=1)
            pygame.draw.rect(surf, eye_col, (cx + 6, head_y - 4, 5, 5), border_radius=1)
            # Specular Glints
            pygame.draw.rect(surf, WHITE, (cx - 10, head_y - 4, 2, 2))
            pygame.draw.rect(surf, WHITE, (cx + 7, head_y - 4, 2, 2))
            # Eyebrows
            if is_blue or is_rocket:
                # Confident / Menacing smirk brow
                pygame.draw.line(surf, (40, 30, 25), (cx - 13, head_y - 8), (cx - 4, head_y - 11), 2)
                pygame.draw.line(surf, (40, 30, 25), (cx + 4, head_y - 10), (cx + 13, head_y - 7), 2)
            else:
                pygame.draw.line(surf, (60, 45, 35), (cx - 12, head_y - 9), (cx - 4, head_y - 9), 2)
                pygame.draw.line(surf, (60, 45, 35), (cx + 4, head_y - 9), (cx + 12, head_y - 9), 2)

        # Glasses / Spectacles
        if has_glasses:
            pygame.draw.rect(surf, (220, 230, 245), (cx - 14, head_y - 7, 11, 9), 2, border_radius=2)
            pygame.draw.rect(surf, (220, 230, 245), (cx + 3, head_y - 7, 11, 9), 2, border_radius=2)
            pygame.draw.line(surf, (220, 230, 245), (cx - 3, head_y - 3), (cx + 3, head_y - 3), 2)
            # Glint
            pygame.draw.line(surf, WHITE, (cx - 12, head_y - 5), (cx - 8, head_y - 5), 1)
            pygame.draw.line(surf, WHITE, (cx + 5, head_y - 5), (cx + 9, head_y - 5), 1)

        # Nose
        pygame.draw.rect(surf, (225, 175, 140), (cx - 1, head_y, 2, 3))

        # Mouth (Talking / Idle Animation)
        if is_talking:
            # Open speaking mouth
            pygame.draw.ellipse(surf, (170, 40, 40), (cx - 5, head_y + 6, 10, 6))
            pygame.draw.ellipse(surf, WHITE, (cx - 3, head_y + 6, 6, 2))
        else:
            if is_blue or is_rocket:
                # Smug / wicked smirk
                pygame.draw.arc(surf, (150, 40, 40), (cx - 4, head_y + 3, 9, 6), 3.14, 5.8, 2)
            else:
                # Friendly smile
                pygame.draw.arc(surf, (150, 40, 40), (cx - 5, head_y + 4, 10, 6), 3.14, 0, 2)

        # Hiker Beard / Stubble
        if is_hiker:
            pygame.draw.arc(surf, (65, 40, 25), (cx - 12, head_y - 2, 24, 18), 3.14, 0, 4)
            pygame.draw.rect(surf, (65, 40, 25), (cx - 6, head_y + 10, 12, 5), border_radius=2)

        # 6. Hair & Headgear Front
        if is_brock:
            # Spiky Peak Hair
            pts = [
                (cx - 20, head_y - 8), (cx - 24, head_y - 22), (cx - 14, head_y - 18),
                (cx - 12, head_y - 28), (cx - 2, head_y - 20), (cx, head_y - 30),
                (cx + 8, head_y - 20), (cx + 14, head_y - 28), (cx + 16, head_y - 18),
                (cx + 24, head_y - 22), (cx + 20, head_y - 8)
            ]
            pygame.draw.polygon(surf, hair_col, pts)
            pygame.draw.rect(surf, hair_col, (cx - 16, head_y - 16, 32, 10))

        elif is_blue:
            # Tall Stylized Spiky Auburn Hair
            pts = [
                (cx - 18, head_y - 6), (cx - 26, head_y - 20), (cx - 14, head_y - 16),
                (cx - 16, head_y - 32), (cx - 4, head_y - 22), (cx + 4, head_y - 34),
                (cx + 12, head_y - 22), (cx + 24, head_y - 28), (cx + 18, head_y - 14),
                (cx + 24, head_y - 10), (cx + 18, head_y - 4)
            ]
            pygame.draw.polygon(surf, hair_col, pts)
            pygame.draw.rect(surf, hair_col, (cx - 16, head_y - 16, 32, 10))

        elif is_rocket:
            # Black Beret with Red 'R'
            pygame.draw.ellipse(surf, hat_col, (cx - 22, head_y - 28, 44, 20))
            pygame.draw.circle(surf, (220, 30, 30), (cx - 4, head_y - 18), 5)
            # Front hair fringe
            pygame.draw.polygon(surf, hair_col, [(cx - 16, head_y - 12), (cx - 8, head_y - 6), (cx - 4, head_y - 12)])

        elif is_nurse:
            # Nurse Cap with Cross
            pygame.draw.ellipse(surf, hair_col, (cx - 20, head_y - 22, 14, 14)) # Twin hair loop left
            pygame.draw.ellipse(surf, hair_col, (cx + 6, head_y - 22, 14, 14)) # Twin hair loop right
            pygame.draw.rect(surf, WHITE, (cx - 14, head_y - 24, 28, 12), border_radius=4)
            pygame.draw.line(surf, (255, 100, 140), (cx, head_y - 22), (cx, head_y - 14), 3) # Cross vert
            pygame.draw.line(surf, (255, 100, 140), (cx - 4, head_y - 18), (cx + 4, head_y - 18), 3) # Cross horiz

        elif is_bug_catcher:
            # Wide Straw Sun Hat
            pygame.draw.ellipse(surf, (215, 185, 105), (cx - 26, head_y - 20, 52, 16))
            pygame.draw.ellipse(surf, (185, 155, 80), (cx - 16, head_y - 28, 32, 18))
            pygame.draw.rect(surf, (60, 140, 55), (cx - 16, head_y - 18, 32, 4)) # Green Ribbon

        elif is_blackbelt:
            # Martial Arts Headband
            pygame.draw.circle(surf, hair_col, (cx, head_y - 14), 16)
            pygame.draw.rect(surf, WHITE, (cx - 18, head_y - 14, 36, 6))
            pygame.draw.polygon(surf, WHITE, [(cx + 16, head_y - 12), (cx + 24, head_y - 4), (cx + 20, head_y - 2)])

        elif is_channeler:
            # Ghost Veil
            pygame.draw.ellipse(surf, hat_col, (cx - 20, head_y - 28, 40, 36))
            pygame.draw.ellipse(surf, (140, 80, 190), (cx - 16, head_y - 24, 32, 28), 2)

        elif is_engineer:
            # Yellow Hardhat
            pygame.draw.ellipse(surf, hat_col, (cx - 22, head_y - 28, 44, 22))
            pygame.draw.rect(surf, (220, 180, 20), (cx - 20, head_y - 18, 40, 5), border_radius=2)
            pygame.draw.circle(surf, WHITE, (cx, head_y - 22), 4) # Lamp

        elif is_hiker or is_fisherman:
            # Bucket / Hiking Hat
            pygame.draw.ellipse(surf, hat_col, (cx - 24, head_y - 20, 48, 16))
            pygame.draw.ellipse(surf, (155, 135, 95), (cx - 16, head_y - 26, 32, 16))

        elif hat_col:
            # Baseball Cap
            pygame.draw.ellipse(surf, hat_col, (cx - 20, head_y - 26, 40, 20))
            pygame.draw.rect(surf, WHITE, (cx - 16, head_y - 18, 32, 5), border_radius=2)

        else:
            # Styled Hair
            pygame.draw.circle(surf, hair_col, (cx, head_y - 14), 16)
            # Front fringe bangs
            pygame.draw.polygon(surf, hair_col, [(cx - 16, head_y - 14), (cx - 8, head_y - 6), (cx - 4, head_y - 12)])
            pygame.draw.polygon(surf, hair_col, [(cx + 4, head_y - 12), (cx + 10, head_y - 6), (cx + 16, head_y - 14)])

    # -------------------------------------------------------------
    # 3. Outer Metallic Bevel Card Border
    # -------------------------------------------------------------
    pygame.draw.rect(surf, (30, 35, 45), (4, 4, W - 8, H - 8), 3, border_radius=8)
    pygame.draw.rect(surf, border_col, (6, 6, W - 12, H - 12), 2, border_radius=6)
    pygame.draw.line(surf, border_highlight, (10, 8), (W - 10, 8), 2)
    pygame.draw.line(surf, border_highlight, (8, 10), (8, H - 10), 2)

    # Scale to requested size and cache
    final_surf = pygame.transform.scale(surf, size)
    return final_surf

