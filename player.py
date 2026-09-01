"""
player.py - Player character entity, grid movement, and animations.
"""
import math
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, Direction, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, WHITE, BLACK, ENCOUNTER_PROP_TILES
from graphics_manager import gfx
from sound_manager import sound_mgr

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
        self.move_speed = 4.0 # tiles per second
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
        
        # Trainer Customization
        self.name = name
        self.gender = gender
        self.outfit_theme = outfit_theme
        self.hat_style = hat_style
        self.hair_color = hair_color
        
        # Sync graphics manager sprites
        gfx.set_custom_player_appearance(self.gender, self.outfit_theme, self.hat_style, self.hair_color)

    def update(self, dt, world):
        self.sail_timer += dt
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
                
            # Update walk animation frame
            self.step_counter += dt * 8
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
            self.target_x = new_x
            self.target_y = new_y
            self.is_moving = True
            self.move_progress = 0.0
            return True
        return False

    def draw(self, surf, camera_x, camera_y):
        draw_x = int(self.pixel_x - camera_x)
        draw_y = int(self.pixel_y - camera_y)
        
        if self.is_sailing:
            # Water bobbing oscillation
            bob_y = int(math.sin(self.sail_timer * 5.0) * 1.5)
            boat_sprite = gfx.boat_sprites.get(self.facing)
            if boat_sprite:
                surf.blit(boat_sprite, (draw_x - 5, draw_y - 5 + bob_y))
            # Draw player upper torso seated/standing inside boat
            player_sprite = gfx.player_sprites[self.facing][self.walk_frame]
            player_upper = player_sprite.subsurface((0, 0, TILE_SIZE, 20))
            surf.blit(player_upper, (draw_x, draw_y - 4 + bob_y))
        else:
            sprite = gfx.player_sprites[self.facing][self.walk_frame]
            surf.blit(sprite, (draw_x, draw_y))
            
            # If in walk-through prop, draw immersive foot overlay
            if self.in_tall_grass and not self.is_moving:
                overlay = gfx.prop_overlays.get(self.current_prop) if self.current_prop else None
                if overlay:
                    surf.blit(overlay, (draw_x, draw_y))
                else:
                    grass_cover = gfx.cached_tiles["tall_grass"].subsurface((0, 16, TILE_SIZE, 16))
                    surf.blit(grass_cover, (draw_x, draw_y + 16))
