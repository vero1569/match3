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

        if self.dragging and self.dragged_tile:
            pos_x = self.dragged_tile.x + self.drag_offset_x
            pos_y = self.dragged_tile.y + self.drag_offset_y

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

            # Se obtiene la posicion del raton y la convierte en la posicion relativa del tablero
            pos_x, pos_y = input_data.position
            pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT

            # la "i" y "j" sera las posiciones relativas del tablero , se restan con self.board.xy porque self.board.xy es la posicion del tablero en la pantalla
            # y se divide por el tama;o del tile para obtener la posicion relativa del tile seleccionado, obteniendo asi la posicion "i" y "j" del tile seleccionado
            i = (pos_y - self.board.y) // settings.TILE_SIZE
            j = (pos_x - self.board.x) // settings.TILE_SIZE
            
            # Si el usuario hace click y lo mantiene presionnaddo, guardamos la posicion del tile seleccionado y se guarda en las variables "drag_start_i" y "drag_start_j"
            # Si el title selecciona es valido (es decir que este dentro de las coordenadas del tablero)

            if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:

                # guardamos sus coodenadas y ponemos el status de draggin como True
                # para saber si que se esta moviendo
                self.dragging = True
                self.drag_start_i = i
                self.drag_start_j = j

                # Guardamos tambien la posicion en la matriz de nuestro TIle
                self.dragged_tile = self.board.tiles[i][j]

                # Usaremos offset para limitar el movimiento de desplazamiento
                self.drag_offset_x = 0
                self.drag_offset_y = 0

        # Si el usuario mantiene presionado el click y lo mueve en alguno de las 4 direcciones ejecuta
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

            # Se obtiene la posicion del raton y la convierte en la posicion relativa del tablero
            pos_x, pos_y = input_data.position
            pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT

            # Aqui verificamos el tile que se selecciono primero para ser movido
            if self.dragged_tile:

                # Ponemos un limite maximo de movimiento
                max_offset = settings.TILE_SIZE

                # Calculamos el ajuste de trasicion para X del Tile
                calculate_tile_position_x = pos_x - max_offset // 2
                raw_offset_x = calculate_tile_position_x - self.dragged_tile.x

                # Calculamos el ajuste de trasicion para Y del Tile
                calculate_tile_position_y = pos_y - max_offset // 2
                raw_offset_y = calculate_tile_position_y - self.dragged_tile.y

                # verificamos el valor minimo entre el offset del xy y la maxima coordenada del Tile
                minOffset_x = min(raw_offset_x, max_offset)
                minOffset_y = min(raw_offset_y, max_offset)

                # limitamos los dezplamientos en el rango entre de los offset
                self.drag_offset_x = max(minOffset_x, -max_offset)
                self.drag_offset_y = max(minOffset_y, -max_offset)

                # Verificamos si cumple la condicion minima para iniciar el movimiento
                if (
                    abs(self.drag_offset_x) > max_offset
                    and abs(self.drag_offset_y) > max_offset
                ):

                    # Podemos determinar la direccion dominante de arrastre
                    # ya que puede mover el tile en x y en Y podemos determinar que coordenada es mayor
                    # y asi "predecir" si el usuario quiere bajar o subir el tile
                    if abs(self.drag_offset_x) > abs(self.drag_offset_y):
                        self.drag_offset_y = 0
                    else:
                        self.drag_offset_x = 0

        elif input_id == "click" and not input_data.pressed and self.dragging:

            # Se obtiene la posicion del raton y la convierte en la posicion relativa del tablero
            pos_x, pos_y = input_data.position
            pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT

            # la "i" y "j" sera las posiciones relativas del tablero , se restan con self.board.xy porque self.board.xy es la posicion del tablero en la pantalla
            # y se divide por el tama;o del tile para obtener la posicion relativa del tile seleccionado, obteniendo asi la posicion "i" y "j" del tile seleccionado
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
                # self.timer = 5000
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
