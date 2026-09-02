"""
player.py - Player character entity, grid movement, and animations.
"""
import math
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, Direction, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, WHITE, BLACK, ENCOUNTER_PROP_TILES
from graphics_manager import gfx
from sound_manager import sound_mgr

class FollowerPokemon:
    """
    Overworld Following/Partner Pokémon entity.
    Follows behind the player, mirroring movement steps, facing directions,
    swimming in water, and offering interactive partner dialogue and emotes.
    """
    def __init__(self, x=8, y=5):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        self.target_x = x
        self.target_y = y
        self.facing = Direction.DOWN
        self.is_moving = False
        self.move_progress = 0.0
        self.move_speed = 4.0
        self.walk_frame = 0
        self.step_counter = 0.0
        self.anim_timer = 0.0
        self.emote_type = None # "heart", "music", "happy", "sweat", "exclamation"
        self.emote_timer = 0.0
        self.current_pokemon = None

    def sync_with_party(self, party):
        """Finds the first non-fainted Pokemon in the active party to be the follower."""
        self.current_pokemon = None
        if party:
            for p in party:
                if not p.is_fainted():
                    self.current_pokemon = p
                    break

    def teleport_to_player(self, player):
        """Teleports follower directly behind the player's current tile and facing direction."""
        dx, dy = 0, 0
        if player.facing == Direction.UP:
            dy = 1
        elif player.facing == Direction.DOWN:
            dy = -1
        elif player.facing == Direction.LEFT:
            dx = 1
        elif player.facing == Direction.RIGHT:
            dx = -1
        self.grid_x = player.grid_x + dx
        self.grid_y = player.grid_y + dy
        self.target_x = self.grid_x
        self.target_y = self.grid_y
        self.pixel_x = self.grid_x * TILE_SIZE
        self.pixel_y = self.grid_y * TILE_SIZE
        self.facing = player.facing
        self.is_moving = False
        self.move_progress = 0.0

    def start_step_behind_player(self, old_player_x, old_player_y):
        """Called right before the player begins moving to a new tile."""
        if (self.grid_x, self.grid_y) != (old_player_x, old_player_y):
            self.target_x = old_player_x
            self.target_y = old_player_y
            self.is_moving = True
            self.move_progress = 0.0
            
            # Determine follower facing direction
            dx = self.target_x - self.grid_x
            dy = self.target_y - self.grid_y
            if abs(dx) > abs(dy):
                self.facing = Direction.RIGHT if dx > 0 else Direction.LEFT
            elif dy != 0:
                self.facing = Direction.DOWN if dy > 0 else Direction.UP

    def update(self, dt, player):
        self.anim_timer += dt
        if self.emote_timer > 0:
            self.emote_timer -= dt
            if self.emote_timer <= 0:
                self.emote_type = None

        self.move_speed = getattr(player, "move_speed", 4.0)

        if self.is_moving:
            self.move_progress += self.move_speed * dt
            if self.move_progress >= 1.0:
                self.move_progress = 0.0
                self.is_moving = False
                self.grid_x = self.target_x
                self.grid_y = self.target_y
                self.pixel_x = self.grid_x * TILE_SIZE
                self.pixel_y = self.grid_y * TILE_SIZE
            else:
                self.pixel_x = (self.grid_x + (self.target_x - self.grid_x) * self.move_progress) * TILE_SIZE
                self.pixel_y = (self.grid_y + (self.target_y - self.grid_y) * self.move_progress) * TILE_SIZE

            anim_rate = 14 if getattr(player, "is_running", False) else 8
            self.step_counter += dt * anim_rate
            self.walk_frame = int(self.step_counter) % 2
        else:
            self.walk_frame = 0
            self.pixel_x = self.grid_x * TILE_SIZE
            self.pixel_y = self.grid_y * TILE_SIZE

    def trigger_emote(self, emote_type="heart", duration=2.5):
        self.emote_type = emote_type
        self.emote_timer = duration

    def draw(self, surf, camera_x, camera_y, is_sailing=False):
        if not self.current_pokemon:
            return

        draw_x = int(self.pixel_x - camera_x)
        draw_y = int(self.pixel_y - camera_y)

        species_name = self.current_pokemon.species
        
        # Subtle bounce/hop offset
        if self.is_moving:
            hop_y = -int(abs(math.sin(self.move_progress * math.pi)) * 5)
        else:
            hop_y = -int(abs(math.sin(self.anim_timer * 3.0)) * 2)

        # 1. Ground Shadow or Water Ripple
        if not is_sailing:
            shadow_surf = pygame.Surface((22, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, 22, 8))
            surf.blit(shadow_surf, (draw_x + 5, draw_y + 24))
        else:
            ripple_w = 26 + int(math.sin(self.anim_timer * 6.0) * 3)
            ripple_surf = pygame.Surface((ripple_w, 10), pygame.SRCALPHA)
            pygame.draw.ellipse(ripple_surf, (220, 240, 255, 140), (0, 0, ripple_w, 10), 2)
            surf.blit(ripple_surf, (draw_x + (32 - ripple_w) // 2, draw_y + 22))

        # 2. Pokémon Sprite
        pkmn_surf = gfx.get_pokemon_sprite(species_name, is_back=False, size=(30, 30))
        if pkmn_surf:
            if self.facing == Direction.LEFT:
                pkmn_surf = pygame.transform.flip(pkmn_surf, True, False)
            elif self.facing == Direction.UP:
                pkmn_surf = pygame.transform.scale(pkmn_surf, (30, 28))
            surf.blit(pkmn_surf, (draw_x + 1, draw_y + 2 + hop_y))

        # 3. Emote Bubble (if active)
        if self.emote_type and self.emote_timer > 0:
            ew, eh = 22, 20
            ex = draw_x + 16
            ey = draw_y - 14 + hop_y
            pygame.draw.rect(surf, (30, 36, 50), (ex - 1, ey - 1, ew + 2, eh + 2), border_radius=6)
            pygame.draw.rect(surf, WHITE, (ex, ey, ew, eh), border_radius=5)
            
            if self.emote_type == "heart":
                htxt = gfx.fonts["small"].render("♥", True, (230, 40, 60))
            elif self.emote_type == "music":
                htxt = gfx.fonts["small"].render("♪", True, (40, 140, 240))
            elif self.emote_type == "happy":
                htxt = gfx.fonts["small"].render("★", True, (240, 180, 20))
            else:
                htxt = gfx.fonts["small"].render("!", True, (200, 80, 0))
            surf.blit(htxt, (ex + (ew - htxt.get_width()) // 2, ey + 2))


class Player:
    def __init__(self, x=8, y=6, current_map="Pallet Town", name="Red", gender="Boy", outfit_theme="Classic Red", hat_style="Trainer Cap", hair_color="Dark Brown"):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        self.facing = Direction.DOWN
        self.is_moving = False
        self.move_progress = 0.0 # 0.0 to 1.0
        self.target_x = x
        self.target_y = y
        self.walk_speed = 4.0 # standard walking speed (tiles per second)
        self.run_speed = 8.0  # running shoes speed when holding SPACE / SHIFT
        self.move_speed = 4.0
        self.is_running = False
        self.walk_frame = 0
        self.step_counter = 0
        self.current_map = current_map
        self.current_prop = None
        self.in_tall_grass = False
        self.has_boat = True
        self.is_sailing = False
        self.sail_timer = 0.0
        self.last_overworld_map = "Pallet Town"
        self.last_overworld_pos = (8, 6)
        
        # Following Partner Pokémon
        self.follower = FollowerPokemon(x=x, y=y - 1)
        
        # Trainer Customization
        self.name = name
        self.gender = gender
        self.outfit_theme = outfit_theme
        self.hat_style = hat_style
        self.hair_color = hair_color
        
        # Sync graphics manager sprites
        gfx.set_custom_player_appearance(self.gender, self.outfit_theme, self.hat_style, self.hair_color)

    def update(self, dt, world, is_running=False):
        self.is_running = is_running
        self.move_speed = self.run_speed if self.is_running else self.walk_speed
        self.sail_timer += dt * (1.5 if self.is_running else 1.0)
        
        # Update follower entity
        if self.follower:
            self.follower.update(dt, self)
            
        if self.is_moving:
            self.move_progress += self.move_speed * dt
            if self.move_progress >= 1.0:
                self.move_progress = 0.0
                self.is_moving = False
                self.grid_x = self.target_x
                self.grid_y = self.target_y
                self.pixel_x = self.grid_x * TILE_SIZE
                self.pixel_y = self.grid_y * TILE_SIZE
                
                # Reveal newly reached area on minimap
                world.reveal_area(self.current_map, self.grid_x, self.grid_y)
                
                # Check tile stepped on
                tile = world.get_tile(self.current_map, self.grid_x, self.grid_y)
                was_sailing = self.is_sailing
                self.is_sailing = (tile == '~')
                self.current_prop = tile if tile in ENCOUNTER_PROP_TILES else None
                self.in_tall_grass = (self.current_prop is not None)
                
                # Step sound in walk-through props or sailing
                if self.current_prop:
                    prop_info = ENCOUNTER_PROP_TILES.get(self.current_prop)
                    if prop_info:
                        sound_mgr.play_sfx(prop_info["sfx"])
                elif not was_sailing and self.is_sailing:
                    sound_mgr.play_sfx("select")
            else:
                self.pixel_x = (self.grid_x + (self.target_x - self.grid_x) * self.move_progress) * TILE_SIZE
                self.pixel_y = (self.grid_y + (self.target_y - self.grid_y) * self.move_progress) * TILE_SIZE
                
            # Update walk/run animation frame
            anim_rate = 14 if self.is_running else 8
            self.step_counter += dt * anim_rate
            self.walk_frame = int(self.step_counter) % 3
        else:
            self.walk_frame = 0
            self.pixel_x = self.grid_x * TILE_SIZE
            self.pixel_y = self.grid_y * TILE_SIZE

    def move(self, direction, world):
        if self.is_moving:
            return False
            
        self.facing = direction
        dx, dy = 0, 0
        if direction == Direction.UP:
            dy = -1
        elif direction == Direction.DOWN:
            dy = 1
        elif direction == Direction.LEFT:
            dx = -1
        elif direction == Direction.RIGHT:
            dx = 1
            
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        
        # Check collision (allow sailing if player has boat or is currently sailing)
        can_sail = self.has_boat or self.is_sailing
        if world.is_passable(self.current_map, new_x, new_y, can_sail=can_sail):
            old_x, old_y = self.grid_x, self.grid_y
            self.target_x = new_x
            self.target_y = new_y
            self.is_moving = True
            self.move_progress = 0.0
            
            # Follower steps to player's previous tile
            if self.follower:
                self.follower.start_step_behind_player(old_x, old_y)
            return True
        return False

    def _draw_player_sprite(self, surf, camera_x, camera_y):
        draw_x = int(self.pixel_x - camera_x)
        draw_y = int(self.pixel_y - camera_y)
        
        if self.is_sailing:
            bob_y = int(math.sin(self.sail_timer * 5.0) * 1.5)
            boat_sprite = gfx.boat_sprites.get(self.facing)
            if boat_sprite:
                surf.blit(boat_sprite, (draw_x - 5, draw_y - 5 + bob_y))
            player_sprite = gfx.player_sprites[self.facing][self.walk_frame]
            player_upper = player_sprite.subsurface((0, 0, TILE_SIZE, 20))
            surf.blit(player_upper, (draw_x, draw_y - 4 + bob_y))
        else:
            sprite = gfx.player_sprites[self.facing][self.walk_frame]
            surf.blit(sprite, (draw_x, draw_y))
            
            # If in walk-through prop, draw foot overlay
            if self.in_tall_grass and not self.is_moving:
                overlay = gfx.prop_overlays.get(self.current_prop) if self.current_prop else None
                if overlay:
                    surf.blit(overlay, (draw_x, draw_y))
                else:
                    grass_cover = gfx.cached_tiles["tall_grass"].subsurface((0, 16, TILE_SIZE, 16))
                    surf.blit(grass_cover, (draw_x, draw_y + 16))

    def draw(self, surf, camera_x, camera_y):
        # Y-sorted rendering between Player and Follower Pokemon
        has_follower = (self.follower and self.follower.current_pokemon)
        
        if has_follower and self.follower.pixel_y < self.pixel_y:
            self.follower.draw(surf, camera_x, camera_y, is_sailing=self.is_sailing)
            self._draw_player_sprite(surf, camera_x, camera_y)
        else:
            self._draw_player_sprite(surf, camera_x, camera_y)
            if has_follower:
                self.follower.draw(surf, camera_x, camera_y, is_sailing=self.is_sailing)
