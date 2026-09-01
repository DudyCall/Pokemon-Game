"""
battle_vfx.py - Rich, procedural visual particle effects for Pokémon battles.
Renders Fire, Water, Electric, Grass, Ice, Psychic, Ghost, Rock, Ground,
Flying, Dragon, and physical impact attack animations.
"""
import math
import random
import pygame
from constants import WHITE, BLACK

def _get_lerp_pos(p1, p2, t):
    return (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)

def draw_battle_attack_vfx(surf, fx_data, timer, player_pos, enemy_pos):
    """
    Renders high-impact attack animations and elemental particle effects.
    """
    if not fx_data:
        return

    m_type = fx_data.get("move_type", "Normal")
    move_name = fx_data.get("move_name", "Attack")
    is_player = fx_data.get("is_player_attacker", True)
    category = fx_data.get("category", "Physical")
    is_crit = fx_data.get("is_crit", False)
    eff = fx_data.get("effectiveness", 1.0)

    # Attacker and Defender coordinates
    if is_player:
        src_pos = player_pos # (x, y)
        tgt_pos = enemy_pos
    else:
        src_pos = enemy_pos
        tgt_pos = player_pos

    duration = 0.65
    t_norm = max(0.0, min(1.0, timer / duration))

    # Dispatch to specific elemental renderer
    if m_type == "Fire":
        _draw_fire_vfx(surf, src_pos, tgt_pos, t_norm, timer, is_crit)
    elif m_type == "Water":
        _draw_water_vfx(surf, src_pos, tgt_pos, t_norm, timer, is_crit)
    elif m_type == "Electric":
        _draw_electric_vfx(surf, src_pos, tgt_pos, t_norm, timer, is_crit)
    elif m_type == "Grass":
        _draw_grass_vfx(surf, src_pos, tgt_pos, t_norm, timer, is_crit)
    elif m_type == "Ice":
        _draw_ice_vfx(surf, src_pos, tgt_pos, t_norm, timer, is_crit)
    elif m_type in ["Psychic", "Ghost"]:
        _draw_psychic_ghost_vfx(surf, src_pos, tgt_pos, t_norm, timer, m_type)
    elif m_type in ["Rock", "Ground", "Fighting"]:
        _draw_rock_ground_vfx(surf, src_pos, tgt_pos, t_norm, timer, m_type)
    elif m_type in ["Dragon", "Flying", "Poison", "Bug", "Dark", "Steel"]:
        _draw_special_elemental_vfx(surf, src_pos, tgt_pos, t_norm, timer, m_type)
    else:
        _draw_physical_normal_vfx(surf, src_pos, tgt_pos, t_norm, timer, category, is_crit)


# -------------------------------------------------------------
# 1. 🔥 FIRE VFX (Ember, Flamethrower, Fire Blast, Fire Spin)
# -------------------------------------------------------------
def _draw_fire_vfx(surf, src_pos, tgt_pos, t_norm, timer, is_crit):
    tx, ty = tgt_pos
    sx, sy = src_pos

    # Phase A: Blazing Fireball Projectile Stream (0.0 to 0.45)
    if t_norm <= 0.5:
        proj_t = min(1.0, t_norm / 0.45)
        # Main fireballs stream (3 chained fireballs)
        for f_idx in range(3):
            delay = f_idx * 0.12
            cur_p = max(0.0, min(1.0, (proj_t - delay) / 0.88)) if proj_t > delay else 0.0
            if cur_p <= 0.0:
                continue

            # Arc trajectory
            arc_y = -math.sin(cur_p * math.pi) * 35
            fx = sx + (tx - sx) * cur_p
            fy = sy + (ty - sy) * cur_p + arc_y

            # Fireball core & glow
            rad_outer = 16 + int(math.sin((timer + f_idx) * 20.0) * 4)
            rad_mid = 10
            rad_core = 5

            # Glowing flame surface
            flame_surf = pygame.Surface((rad_outer * 2 + 4, rad_outer * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(flame_surf, (240, 60, 20, 160), (rad_outer + 2, rad_outer + 2), rad_outer)
            pygame.draw.circle(flame_surf, (255, 160, 30, 220), (rad_outer + 2, rad_outer + 2), rad_mid)
            pygame.draw.circle(flame_surf, (255, 255, 200, 255), (rad_outer + 2, rad_outer + 2), rad_core)
            surf.blit(flame_surf, (int(fx - rad_outer - 2), int(fy - rad_outer - 2)))

            # Trailing ember sparks
            for s_i in range(4):
                spark_t = cur_p - 0.05 * (s_i + 1)
                if spark_t > 0:
                    sp_x = sx + (tx - sx) * spark_t + (math.sin(s_i * 3 + timer * 15) * 12)
                    sp_y = sy + (ty - sy) * spark_t + arc_y + (math.cos(s_i * 3 + timer * 15) * 12)
                    pygame.draw.circle(surf, (255, 120, 20), (int(sp_x), int(sp_y)), 3 - (s_i // 2))

    # Phase B: Fiery Explosion Burst & Rising Flame Pillars (0.35 to 1.0)
    if t_norm >= 0.35:
        exp_t = (t_norm - 0.35) / 0.65

        # 1. Warm red-orange screen ambient flash on defender
        flash_alpha = max(0, int(120 * (1.0 - exp_t)))
        flash_surf = pygame.Surface((180, 180), pygame.SRCALPHA)
        pygame.draw.circle(flash_surf, (255, 80, 20, flash_alpha), (90, 90), 85)
        surf.blit(flash_surf, (tx - 90, ty - 90))

        # 2. Expanding Combustion Shockwave Ring
        ring_rad = int(20 + exp_t * 60)
        ring_surf = pygame.Surface((ring_rad * 2 + 4, ring_rad * 2 + 4), pygame.SRCALPHA)
        ring_alpha = max(0, int(220 * (1.0 - exp_t)))
        pygame.draw.circle(ring_surf, (255, 180, 30, ring_alpha), (ring_rad + 2, ring_rad + 2), ring_rad, 4)
        surf.blit(ring_surf, (tx - ring_rad - 2, ty - ring_rad - 2))

        # 3. Rising Flame Spires around target (6 spires)
        for i in range(6):
            ang = i * (math.pi / 3) + timer * 2.0
            spire_dist = 24 + int(math.sin(exp_t * 5.0) * 8)
            spire_x = tx + math.cos(ang) * spire_dist
            spire_y = ty + math.sin(ang) * (spire_dist * 0.6) - exp_t * 45

            spire_h = int(30 * (1.0 - exp_t * 0.7))
            spire_w = int(14 * (1.0 - exp_t * 0.5))
            if spire_h > 4 and spire_w > 2:
                flame_pts = [
                    (spire_x, spire_y - spire_h),
                    (spire_x + spire_w // 2, spire_y),
                    (spire_x - spire_w // 2, spire_y)
                ]
                pygame.draw.polygon(surf, (255, 60, 20), flame_pts)
                inner_pts = [
                    (spire_x, spire_y - int(spire_h * 0.7)),
                    (spire_x + spire_w // 4, spire_y),
                    (spire_x - spire_w // 4, spire_y)
                ]
                pygame.draw.polygon(surf, (255, 230, 80), inner_pts)


# -------------------------------------------------------------
# 2. 💧 WATER VFX (Water Gun, Hydro Pump, Bubble, Surf)
# -------------------------------------------------------------
def _draw_water_vfx(surf, src_pos, tgt_pos, t_norm, timer, is_crit):
    tx, ty = tgt_pos
    sx, sy = src_pos

    # Phase A: High-Pressure Water Torrent & Foam Bubbles (0.0 to 0.5)
    if t_norm <= 0.55:
        jet_t = min(1.0, t_norm / 0.5)
        # Rushing water streams (multiple curved streams)
        num_drops = 14
        for d_i in range(num_drops):
            offset_t = d_i / num_drops
            cur_p = max(0.0, min(1.0, (jet_t - offset_t * 0.3) / 0.7)) if jet_t > offset_t * 0.3 else 0.0
            if cur_p <= 0.0:
                continue

            wave_offset = math.sin(cur_p * 8.0 + timer * 15.0 + d_i) * 16
            wx = sx + (tx - sx) * cur_p
            wy = sy + (ty - sy) * cur_p + wave_offset

            # Water droplet / orb
            w_rad = 7 + (d_i % 4)
            w_surf = pygame.Surface((w_rad * 2 + 2, w_rad * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(w_surf, (30, 130, 240, 190), (w_rad + 1, w_rad + 1), w_rad)
            pygame.draw.circle(w_surf, (160, 230, 255, 230), (w_rad + 1, w_rad + 1), max(2, w_rad - 3))
            pygame.draw.circle(w_surf, (255, 255, 255, 255), (w_rad - 1, w_rad - 1), 2)
            surf.blit(w_surf, (int(wx - w_rad - 1), int(wy - w_rad - 1)))

    # Phase B: Giant Aquatic Splash & Expanding Tidal Waves (0.3 to 1.0)
    if t_norm >= 0.3:
        splash_t = (t_norm - 0.3) / 0.7

        # 1. Expanding Aqua Shockwave Rings
        for r_i in range(3):
            delay = r_i * 0.15
            cur_r_t = max(0.0, (splash_t - delay) / 0.7) if splash_t > delay else 0.0
            if cur_r_t <= 0.0:
                continue

            rw = int(30 + cur_r_t * 90)
            rh = int(14 + cur_r_t * 40)
            ring_alpha = max(0, int(200 * (1.0 - cur_r_t)))
            r_surf = pygame.Surface((rw * 2 + 4, rh * 2 + 4), pygame.SRCALPHA)
            pygame.draw.ellipse(r_surf, (50, 170, 255, ring_alpha), (2, 2, rw * 2, rh * 2), 3)
            pygame.draw.ellipse(r_surf, (220, 245, 255, ring_alpha), (4, 4, rw * 2 - 4, rh * 2 - 4), 1)
            surf.blit(r_surf, (tx - rw - 2, ty + 20 - rh // 2))

        # 2. Upward Water Splash Geysers (8 droplets shooting up)
        for i in range(8):
            ang = i * (math.pi / 4)
            dist_x = math.cos(ang) * (30 * splash_t)
            dist_y = -math.sin(splash_t * math.pi) * (50 + (i % 3) * 15)

            drop_x = tx + dist_x
            drop_y = ty + dist_y
            drop_rad = max(2, int(6 * (1.0 - splash_t * 0.7)))
            pygame.draw.circle(surf, (60, 180, 255), (int(drop_x), int(drop_y)), drop_rad)
            pygame.draw.circle(surf, (240, 250, 255), (int(drop_x - 1), int(drop_y - 1)), max(1, drop_rad - 2))


# -------------------------------------------------------------
# 3. ⚡ ELECTRIC VFX (Thunderbolt, ThunderShock, Thunder, Spark)
# -------------------------------------------------------------
def _draw_electric_vfx(surf, src_pos, tgt_pos, t_norm, timer, is_crit):
    tx, ty = tgt_pos
    sx, sy = src_pos

    # High-voltage flashing ambient
    if int(timer * 25.0) % 2 == 0:
        flash_surf = pygame.Surface((160, 160), pygame.SRCALPHA)
        pygame.draw.circle(flash_surf, (255, 255, 140, 80), (80, 80), 75)
        surf.blit(flash_surf, (tx - 80, ty - 80))

    # Phase A: Plasma Surge connecting Attacker & Defender
    if t_norm <= 0.4:
        for b_idx in range(3):
            pts = [src_pos]
            steps = 5
            for st in range(1, steps):
                t_step = st / steps
                bx = sx + (tx - sx) * t_step + random.randint(-18, 18)
                by = sy + (ty - sy) * t_step + random.randint(-18, 18)
                pts.append((bx, by))
            pts.append(tgt_pos)
            pygame.draw.lines(surf, (255, 240, 40), False, pts, 3)
            pygame.draw.lines(surf, (255, 255, 255), False, pts, 1)

    # Phase B: Giant Lightning Bolts striking down onto target
    if t_norm >= 0.2:
        top_y = max(10, ty - 140)
        # 3 lightning bolts striking down
        for l_i in range(3):
            bolt_x = tx + (l_i - 1) * 26
            pts = [(bolt_x + random.randint(-10, 10), top_y)]
            cur_y = top_y
            while cur_y < ty + 20:
                cur_y += random.randint(18, 30)
                cur_x = pts[-1][0] + random.randint(-16, 16)
                pts.append((cur_x, min(ty + 20, cur_y)))

            pygame.draw.lines(surf, (240, 220, 20), False, pts, 4)
            pygame.draw.lines(surf, (255, 255, 255), False, pts, 2)

        # Spreading electric sparks around target
        for sp in range(10):
            ang = random.random() * 6.28
            dist = random.randint(15, 48)
            sp_x = tx + math.cos(ang) * dist
            sp_y = ty + math.sin(ang) * dist
            pygame.draw.line(surf, (255, 255, 200), (sp_x, sp_y), (sp_x + random.randint(-6, 6), sp_y + random.randint(-6, 6)), 2)
            pygame.draw.circle(surf, (255, 255, 255), (int(sp_x), int(sp_y)), 2)


# -------------------------------------------------------------
# 4. 🌿 GRASS VFX (Razor Leaf, Vine Whip, Solar Beam, Petal Dance)
# -------------------------------------------------------------
def _draw_grass_vfx(surf, src_pos, tgt_pos, t_norm, timer, is_crit):
    tx, ty = tgt_pos
    sx, sy = src_pos

    # Phase A: Whirling Razor Leaves streaming to target (0.0 to 0.5)
    num_leaves = 8
    for i in range(num_leaves):
        delay = i * 0.05
        cur_p = max(0.0, min(1.0, (t_norm - delay) / 0.55)) if t_norm > delay else 0.0
        if cur_p <= 0.0 or cur_p >= 1.0:
            continue

        spiral_ang = cur_p * 8.0 + i * 1.2
        spiral_r = math.sin(cur_p * math.pi) * 22
        lx = sx + (tx - sx) * cur_p + math.cos(spiral_ang) * spiral_r
        ly = sy + (ty - sy) * cur_p + math.sin(spiral_ang) * spiral_r

        # Draw pointed sharp razor leaf
        leaf_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(leaf_surf, (40, 190, 70), (2, 5, 16, 10))
        pygame.draw.ellipse(leaf_surf, (150, 245, 120), (4, 7, 12, 6))
        pygame.draw.line(leaf_surf, (255, 255, 255), (2, 10), (18, 10), 1)

        rot_leaf = pygame.transform.rotate(leaf_surf, math.degrees(spiral_ang * 2.0))
        surf.blit(rot_leaf, (int(lx - rot_leaf.get_width() // 2), int(ly - rot_leaf.get_height() // 2)))

    # Phase B: Slicing Nature Slash & Bursting Floral Petals (0.35 to 1.0)
    if t_norm >= 0.35:
        sl_t = (t_norm - 0.35) / 0.65

        # Double Emerald Energy Slashes across Defender (X pattern)
        slash_len = int(sl_t * 60)
        s_alpha = max(0, int(240 * (1.0 - sl_t)))
        s_surf = pygame.Surface((140, 140), pygame.SRCALPHA)

        pygame.draw.line(s_surf, (50, 230, 90, s_alpha), (70 - slash_len, 70 - slash_len), (70 + slash_len, 70 + slash_len), 4)
        pygame.draw.line(s_surf, (200, 255, 180, s_alpha), (70 - slash_len, 70 - slash_len), (70 + slash_len, 70 + slash_len), 2)

        pygame.draw.line(s_surf, (50, 230, 90, s_alpha), (70 + slash_len, 70 - slash_len), (70 - slash_len, 70 + slash_len), 4)
        pygame.draw.line(s_surf, (200, 255, 180, s_alpha), (70 + slash_len, 70 - slash_len), (70 - slash_len, 70 + slash_len), 2)
        surf.blit(s_surf, (tx - 70, ty - 70))

        # Bursting nature sparks
        for p in range(8):
            ang = p * (math.pi / 4) + timer * 3.0
            dist = 20 + sl_t * 40
            px = tx + math.cos(ang) * dist
            py = ty + math.sin(ang) * dist
            pygame.draw.circle(surf, (80, 220, 100), (int(px), int(py)), 3)


# -------------------------------------------------------------
# 5. ❄️ ICE VFX (Ice Beam, Blizzard, Aurora Beam, Ice Punch)
# -------------------------------------------------------------
def _draw_ice_vfx(surf, src_pos, tgt_pos, t_norm, timer, is_crit):
    tx, ty = tgt_pos
    sx, sy = src_pos

    # Phase A: Freezing Glacial Crystals flying to target
    if t_norm <= 0.5:
        beam_t = min(1.0, t_norm / 0.45)
        for i in range(6):
            cur_p = max(0.0, min(1.0, (beam_t - i * 0.08) / 0.6)) if beam_t > i * 0.08 else 0.0
            if cur_p <= 0.0:
                continue

            ix = sx + (tx - sx) * cur_p + math.sin(cur_p * 6.0 + i) * 12
            iy = sy + (ty - sy) * cur_p + math.cos(cur_p * 6.0 + i) * 12

            pts = [(ix, iy - 8), (ix + 6, iy), (ix, iy + 8), (ix - 6, iy)]
            pygame.draw.polygon(surf, (120, 220, 255), pts)
            pygame.draw.polygon(surf, WHITE, pts, 1)

    # Phase B: Erupting Glacial Ice Spires around Target
    if t_norm >= 0.3:
        ice_t = (t_norm - 0.3) / 0.7
        for i in range(4):
            offset_x = (i - 1.5) * 22
            base_x = tx + offset_x
            base_y = ty + 25

            spire_h = int(min(1.0, ice_t * 2.5) * (45 - abs(offset_x) * 0.5))
            spire_pts = [
                (base_x, base_y - spire_h),
                (base_x + 9, base_y),
                (base_x - 9, base_y)
            ]
            pygame.draw.polygon(surf, (150, 230, 255), spire_pts)
            pygame.draw.polygon(surf, (220, 250, 255), spire_pts, 1)

        for s_i in range(8):
            ang = s_i * (math.pi / 4) + timer * 2.0
            dist = 24 + ice_t * 35
            sx_p = tx + math.cos(ang) * dist
            sy_p = ty + math.sin(ang) * (dist * 0.7)
            pygame.draw.circle(surf, WHITE, (int(sx_p), int(sy_p)), 2)


# -------------------------------------------------------------
# 6. 🔮 PSYCHIC / GHOST VFX (Psychic, Shadow Ball, Night Shade)
# -------------------------------------------------------------
def _draw_psychic_ghost_vfx(surf, src_pos, tgt_pos, t_norm, timer, m_type):
    tx, ty = tgt_pos
    sx, sy = src_pos

    col_primary = (180, 50, 220) if m_type == "Psychic" else (110, 40, 160)
    col_core = (255, 160, 255) if m_type == "Psychic" else (180, 130, 230)

    for r_i in range(4):
        delay = r_i * 0.12
        cur_t = max(0.0, min(1.0, (t_norm - delay) / 0.6)) if t_norm > delay else 0.0
        if cur_t <= 0.0:
            continue

        rx = sx + (tx - sx) * cur_t
        ry = sy + (ty - sy) * cur_t

        rad = int(12 + cur_t * 30)
        ring_alpha = max(0, int(220 * (1.0 - cur_t * 0.7)))
        r_surf = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(r_surf, (*col_primary, ring_alpha), (rad + 2, rad + 2), rad, 3)
        pygame.draw.circle(r_surf, (*col_core, ring_alpha), (rad + 2, rad + 2), max(1, rad - 4), 1)
        surf.blit(r_surf, (int(rx - rad - 2), int(ry - rad - 2)))

    if t_norm >= 0.35:
        exp_t = (t_norm - 0.35) / 0.65
        for s in range(6):
            ang = s * (math.pi / 3) + timer * 6.0
            dist = 20 + exp_t * 35
            star_x = tx + math.cos(ang) * dist
            star_y = ty + math.sin(ang) * dist
            pygame.draw.circle(surf, col_core, (int(star_x), int(star_y)), 3)


# -------------------------------------------------------------
# 7. 🪨 ROCK / GROUND / FIGHTING VFX (Rock Slide, Earthquake)
# -------------------------------------------------------------
def _draw_rock_ground_vfx(surf, src_pos, tgt_pos, t_norm, timer, m_type):
    tx, ty = tgt_pos

    if t_norm >= 0.2:
        imp_t = (t_norm - 0.2) / 0.8

        crack_len = int(imp_t * 40)
        crack_col = (130, 90, 50)
        for c_ang in [0.2, 0.9, 1.8, 2.5, 3.4, 4.2, 5.1]:
            cx_end = tx + math.cos(c_ang) * crack_len
            cy_end = ty + 20 + math.sin(c_ang) * (crack_len * 0.5)
            pygame.draw.line(surf, crack_col, (tx, ty + 20), (int(cx_end), int(cy_end)), 2)

        for r_i in range(6):
            r_ang = r_i * 1.05 + timer * 3.0
            dist = imp_t * 45
            rx = tx + math.cos(r_ang) * dist
            ry = ty + 20 - math.sin(imp_t * math.pi) * 35 + math.sin(r_ang) * (dist * 0.4)
            sz = 4 + (r_i % 3) * 2
            pygame.draw.rect(surf, (150, 115, 80), (int(rx), int(ry), sz, sz))
            pygame.draw.rect(surf, (90, 65, 40), (int(rx), int(ry), sz, sz), 1)


# -------------------------------------------------------------
# 8. 🐉 SPECIAL ELEMENTAL VFX (Dragon, Flying, Poison, Bug)
# -------------------------------------------------------------
def _draw_special_elemental_vfx(surf, src_pos, tgt_pos, t_norm, timer, m_type):
    tx, ty = tgt_pos
    sx, sy = src_pos

    if m_type == "Dragon":
        col = (100, 70, 240)
        core_col = (240, 120, 255)
    elif m_type == "Poison":
        col = (160, 40, 180)
        core_col = (220, 140, 240)
    elif m_type == "Flying":
        col = (160, 200, 240)
        core_col = (255, 255, 255)
    else:
        col = (150, 180, 40)
        core_col = (220, 240, 100)

    cur_p = min(1.0, t_norm / 0.5)
    ex = sx + (tx - sx) * cur_p
    ey = sy + (ty - sy) * cur_p
    pygame.draw.circle(surf, col, (int(ex), int(ey)), 14)
    pygame.draw.circle(surf, core_col, (int(ex), int(ey)), 8)
    pygame.draw.circle(surf, WHITE, (int(ex), int(ey)), 4)

    if t_norm >= 0.35:
        exp_t = (t_norm - 0.35) / 0.65
        for s in range(8):
            ang = s * (math.pi / 4)
            dist = exp_t * 40
            px = tx + math.cos(ang) * dist
            py = ty + math.sin(ang) * dist
            pygame.draw.circle(surf, col, (int(px), int(py)), 3)


# -------------------------------------------------------------
# 9. ⚔️ PHYSICAL / NORMAL VFX (Slash, Tackle, Punch, Hyper Beam)
# -------------------------------------------------------------
def _draw_physical_normal_vfx(surf, src_pos, tgt_pos, t_norm, timer, category, is_crit):
    tx, ty = tgt_pos

    if category == "Special":
        beam_w = int(math.sin(t_norm * math.pi) * 20)
        if beam_w > 0:
            pygame.draw.line(surf, (255, 255, 180), src_pos, tgt_pos, beam_w)
            pygame.draw.line(surf, WHITE, src_pos, tgt_pos, max(2, beam_w // 2))
    else:
        slash_t = min(1.0, t_norm / 0.6)
        sl_len = int(slash_t * 50)
        sl_alpha = max(0, int(240 * (1.0 - t_norm)))
        sl_surf = pygame.Surface((120, 120), pygame.SRCALPHA)

        for offset in [-14, 0, 14]:
            pygame.draw.line(
                sl_surf, (255, 255, 255, sl_alpha),
                (60 - sl_len + offset, 60 - sl_len),
                (60 + sl_len + offset, 60 + sl_len),
                3
            )
            pygame.draw.line(
                sl_surf, (240, 200, 80, sl_alpha),
                (60 - sl_len + offset, 60 - sl_len),
                (60 + sl_len + offset, 60 + sl_len),
                1
            )
        surf.blit(sl_surf, (tx - 60, ty - 60))

    if 0.25 <= t_norm <= 0.75:
        star_t = (t_norm - 0.25) / 0.5
        star_rad = int(24 * (1.0 - abs(star_t - 0.5) * 2))
        if star_rad > 2:
            star_pts = []
            for p_i in range(8):
                ang = p_i * (math.pi / 4) + timer * 5.0
                r = star_rad if (p_i % 2 == 0) else (star_rad // 2)
                star_pts.append((tx + math.cos(ang) * r, ty + math.sin(ang) * r))
            pygame.draw.polygon(surf, (255, 230, 40), star_pts)
            pygame.draw.polygon(surf, WHITE, star_pts, 2)
