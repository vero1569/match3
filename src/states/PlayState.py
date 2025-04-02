"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # Position in the grid which we are highlighting
        self.board_highlight_i1 = -1
        self.board_highlight_j1 = -1
        self.board_highlight_i2 = -1
        self.board_highlight_j2 = -1

        self.highlighted_tile = False

        self.active = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 1.25 * 1000

        # Variables para el arrastre
        self.dragging = False
        self.dragged_tile = None
        self.drag_start_i = -1
        self.drag_start_j = -1
        self.drag_offset_x = 0  # Nuevo: offset para el arrastre suave
        self.drag_offset_y = 0

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        self.__check_board_state()

        Timer.every(1, decrement_timer)

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        # Renderizar el tile que se está arrastrando al final
        if self.dragging and self.dragged_tile:
            pos_x = self.dragged_tile.x + self.drag_offset_x
            pos_y = self.dragged_tile.y + self.drag_offset_y
            # self.dragged_tile.render_at(surface, pos_x, pos_y)

        if self.highlighted_tile:
            x = self.highlighted_j1 * settings.TILE_SIZE + self.board.x
            y = self.highlighted_i1 * settings.TILE_SIZE + self.board.y
            # surface.blit(self.tile_alpha_surface, (x, y))

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return

        if input_id == "click" and input_data.pressed:
            pos_x, pos_y = input_data.position
            pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            i = (pos_y - self.board.y) // settings.TILE_SIZE
            j = (pos_x - self.board.x) // settings.TILE_SIZE

            if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                self.dragging = True
                self.drag_start_i = i
                self.drag_start_j = j
                self.dragged_tile = self.board.tiles[i][j]
                # Inicializar offset en 0
                self.drag_offset_x = 0
                self.drag_offset_y = 0

        elif (
            input_id
            in [
                "mouse_motion_left",
                "mouse_motion_right",
                "mouse_motion_up",
                "mouse_motion_down",
            ]
            and self.dragging
        ):
            pos_x, pos_y = input_data.position
            pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT

            if self.dragged_tile:
                # Calcular el offset máximo permitido (un tile de distancia)
                max_offset = settings.TILE_SIZE

                # Calcular offsets relativos a la posición original
                raw_offset_x = (pos_x - settings.TILE_SIZE // 2) - self.dragged_tile.x
                raw_offset_y = (pos_y - settings.TILE_SIZE // 2) - self.dragged_tile.y

                # Limitar los offsets al rango permitido
                self.drag_offset_x = max(min(raw_offset_x, max_offset), -max_offset)
                self.drag_offset_y = max(min(raw_offset_y, max_offset), -max_offset)

                # Si ambos offsets son significativos, priorizar el mayor
                if (
                    abs(self.drag_offset_x) > settings.TILE_SIZE * 0.1
                    and abs(self.drag_offset_y) > settings.TILE_SIZE * 0.1
                ):
                    if abs(self.drag_offset_x) > abs(self.drag_offset_y):
                        self.drag_offset_y = 0
                    else:
                        self.drag_offset_x = 0

        elif input_id == "click" and not input_data.pressed and self.dragging:
            pos_x, pos_y = input_data.position
            pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            i = (pos_y - self.board.y) // settings.TILE_SIZE
            j = (pos_x - self.board.x) // settings.TILE_SIZE

            if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                di = abs(i - self.drag_start_i)
                dj = abs(j - self.drag_start_j)

                if di <= 1 and dj <= 1 and di != dj:
                    self.active = False
                    tile1 = self.board.tiles[self.drag_start_i][self.drag_start_j]
                    tile2 = self.board.tiles[i][j]

                    def arrive():
                        (
                            self.board.tiles[tile1.i][tile1.j],
                            self.board.tiles[tile2.i][tile2.j],
                        ) = (
                            self.board.tiles[tile2.i][tile2.j],
                            self.board.tiles[tile1.i][tile1.j],
                        )
                        tile1.i, tile1.j, tile2.i, tile2.j = (
                            tile2.i,
                            tile2.j,
                            tile1.i,
                            tile1.j,
                        )
                        self.__calculate_matches([tile1, tile2])

                    Timer.tween(
                        0.25,
                        [
                            (tile1, {"x": tile2.x, "y": tile2.y}),
                            (tile2, {"x": tile1.x, "y": tile1.y}),
                        ],
                        on_finish=arrive,
                    )

            # Resetear el estado de arrastre
            self.dragging = False
            self.dragged_tile = None
            self.drag_offset_x = 0
            self.drag_offset_y = 0

    def __calculate_matches(self, tiles: List) -> None:
        matches = self.board.calculate_matches_for(tiles)

        if matches is None:
            if len(tiles) == 2:
                tile1, tile2 = tiles

                def revert_finish():
                    (
                        self.board.tiles[tile1.i][tile1.j],
                        self.board.tiles[tile2.i][tile2.j],
                    ) = (
                        self.board.tiles[tile2.i][tile2.j],
                        self.board.tiles[tile1.i][tile1.j],
                    )
                    tile1.i, tile1.j, tile2.i, tile2.j = (
                        tile2.i,
                        tile2.j,
                        tile1.i,
                        tile1.j,
                    )
                    settings.SOUNDS["error"].play()
                    self.active = True
                    self.__check_board_state()

                Timer.tween(
                    0.25,
                    [
                        (tile1, {"x": tile2.x, "y": tile2.y}),
                        (tile2, {"x": tile1.x, "y": tile1.y}),
                    ],
                    on_finish=lambda: Timer.tween(
                        0.25,
                        [
                            (tile1, {"x": tile1.x, "y": tile1.y}),
                            (tile2, {"x": tile2.x, "y": tile2.y}),
                        ],
                        on_finish=revert_finish,
                    ),
                )
            else:
                self.active = True
                self.__check_board_state()
            return

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        for match in matches:
            self.score += len(match) * 50

        self.board.remove_matches()
        falling_tiles = self.board.get_falling_tiles()

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=lambda: self.__calculate_matches(
                [item[0] for item in falling_tiles]
            ),
        )

    def __check_board_state(self) -> None:
        if not self.board.verify_posible_match():

            def reset_board():
                print("NOS JODIMOS")
                #self.timer = 5000
                self.__initialize_new_board()
                settings.SOUNDS["next-level"].play()
                self.active = True

            self.active = False
            Timer.after(0.5, reset_board)

    def __initialize_new_board(self) -> None:
        self.board.initialize_tiles()
        # Verificar que el nuevo tablero tenga movimientos válidos
        while not self.board.verify_posible_match():
            self.board.initialize_tiles()
