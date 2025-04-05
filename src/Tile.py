"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Tile.
"""

import pygame
import math

import settings


class Tile:
    def __init__(self, i: int, j: int, color: int, variety: int, is_powerup=False) -> None:
        self.i = i
        self.j = j
        self.x = self.j * settings.TILE_SIZE
        self.y = self.i * settings.TILE_SIZE
        self.color = color
        self.variety = variety
        self.is_powerup = is_powerup
        self.alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )

        self.blink_timer = 0
        self.visible = True

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:

        # Peque;a validacion para que si el tile es un powerup parpapdee
        if self.is_powerup:
            current_time = pygame.time.get_ticks()
            if current_time - self.blink_timer >= 250:
                self.visible = not self.visible
                self.blink_timer = current_time
            
            if not self.visible:
                return

        self.alpha_surface.blit(
            settings.TEXTURES["tiles"],
            (0, 0),
            settings.FRAMES["tiles"][self.color][self.variety],
        )
        pygame.draw.rect(
            self.alpha_surface,
            (34, 32, 52, 200),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )
        surface.blit(self.alpha_surface, (self.x + 2 + offset_x, self.y + 2 + offset_y))
        surface.blit(
            settings.TEXTURES["tiles"],
            (self.x + offset_x, self.y + offset_y),
            settings.FRAMES["tiles"][self.color][self.variety],
        )


