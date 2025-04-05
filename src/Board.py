"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Board.
"""

from typing import List, Optional, Tuple, Any, Dict, Set

import pygame

import random

import settings
from src.Tile import Tile


class Board:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.matches: List[List[Tile]] = []
        self.tiles: List[List[Tile]] = []
        self.initialize_tiles()
        self.powerup_data: Optional[Tuple[int, int, int, bool]] = None

    def render(self, surface: pygame.Surface) -> None:
        for row in self.tiles:
            for tile in row:
                tile.render(surface, self.x, self.y)

    def __is_match_generated(self, i: int, j: int, color: int) -> bool:
        if (
            i >= 2
            and self.tiles[i - 1][j].color == color
            and self.tiles[i - 2][j].color == color
        ):
            return True

        return (
            j >= 2
            and self.tiles[i][j - 1].color == color
            and self.tiles[i][j - 2].color == color
        )

    def initialize_tiles(self) -> None:
        self.tiles = [
            [None for _ in range(settings.BOARD_WIDTH)]
            for _ in range(settings.BOARD_HEIGHT)
        ]
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                color = random.randint(0, settings.NUM_COLORS - 1)
                while self.__is_match_generated(i, j, color):
                    color = random.randint(0, settings.NUM_COLORS - 1)

                self.tiles[i][j] = Tile(
                    i, j, color, random.randint(0, settings.NUM_VARIETIES - 1)
                )

    def __calculate_match_rec(self, tile: Tile) -> Set[Tile]:
        if tile in self.in_stack:
            return []

        self.in_stack.add(tile)

        color_to_match = tile.color

        ## Check horizontal match
        h_match: List[Tile] = []

        # Check left
        if tile.j > 0:
            left = max(0, tile.j - 2)
            for j in range(tile.j - 1, left - 1, -1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        # Check right
        if tile.j < settings.BOARD_WIDTH - 1:
            right = min(settings.BOARD_WIDTH - 1, tile.j + 2)
            for j in range(tile.j + 1, right + 1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        ## Check vertical match
        v_match: List[Tile] = []

        # Check top
        if tile.i > 0:
            top = max(0, tile.i - 2)
            for i in range(tile.i - 1, top - 1, -1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        # Check bottom
        if tile.i < settings.BOARD_HEIGHT - 1:
            bottom = min(settings.BOARD_HEIGHT - 1, tile.i + 2)
            for i in range(tile.i + 1, bottom + 1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        match: List[Tile] = []

        if len(h_match) >= 2:
            for t in h_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(v_match) >= 2:
            for t in v_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(match) > 0:
            if tile not in self.in_match:
                self.in_match.add(tile)
                match.append(tile)

        for t in match:
            match += self.__calculate_match_rec(t)

        self.in_stack.remove(tile)
        return match

    def calculate_matches_for(
        self, new_tiles: List[Tile]
    ) -> Optional[List[List[Tile]]]:
        self.in_match: Set[Tile] = set()
        self.in_stack: Set[Tile] = set()

        for tile in new_tiles:
            if tile in self.in_match:
                continue
            match = self.__calculate_match_rec(tile)
            if len(match) > 0:
                self.matches.append(match)
                if not any(tile.is_powerup for tile in match):
                    if len(match) == 4:
        
                        last_tile = match[
                            -1
                        ]  
                        print("i:", last_tile.i, ",j:", last_tile.j)
                        self.powerup_data = (
                            last_tile.i,
                            last_tile.j,
                            last_tile.color,
                            False,
                        )

                    if len(match) >= 5:
                
                        last_tile = match[
                            -1
                        ]  
                        print("i:", last_tile.i, ",j:", last_tile.j)
                        self.powerup_data = (
                            last_tile.i,
                            last_tile.j,
                            last_tile.color,
                            True,
                        )
        delattr(self, "in_match")
        delattr(self, "in_stack")

        return self.matches if len(self.matches) > 0 else None

    def remove_matches(self) -> None:
        for match in self.matches:
            for tile in match:
                if (
                    self.powerup_data is not None
                    and self.powerup_data[0] == tile.i
                    and self.powerup_data[1] == tile.j
                ):
                    tile.is_powerup = True
                    print("Asigne un poder", tile.i, tile.j)
                    continue
                else:
                    self.tiles[tile.i][tile.j] = None

        self.matches = []

    def get_falling_tiles(self) -> Tuple[Any, Dict[str, Any]]:
        # List of tweens to create
        tweens: Tuple[Tile, Dict[str, Any]] = []

        # for each column, go up tile by tile until we hit a space
        for j in range(settings.BOARD_WIDTH):
            space = False
            space_i = -1
            i = settings.BOARD_HEIGHT - 1

            while i >= 0:
                tile = self.tiles[i][j]

                # if our previous tile was a space
                if space:
                    # if the current tile is not a space
                    if tile is not None:
                        self.tiles[space_i][j] = tile
                        tile.i = space_i

                        # set its prior position to None
                        self.tiles[i][j] = None

                        tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))
                        space = False
                        i = space_i
                        space_i = -1
                elif tile is None:
                    space = True

                    if space_i == -1:
                        space_i = i

                i -= 1

        # create a replacement tiles at the top of the screen
        for j in range(settings.BOARD_WIDTH):
            for i in range(settings.BOARD_HEIGHT):
                tile = self.tiles[i][j]

                if tile is None:
                    tile = Tile(
                        i,
                        j,
                        random.randint(0, settings.NUM_COLORS - 1),
                        random.randint(0, settings.NUM_VARIETIES - 1),
                    )
                    tile.y -= settings.TILE_SIZE
                    self.tiles[i][j] = tile
                    tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens

    def __check_potential_match(self, i: int, j: int, color: int) -> bool:

        # Posicion en la que se encuentra el tile en la matriz de la columna

        # validaciones para las columnas
        if j < settings.BOARD_WIDTH - 2:
            # Verificacion los tiles a la derecha de la matriz
            if self.__verify_position_in_matrix(i, j + 1, i, j + 2, color):
                return True
        if j > 1:
            # Verificacion los tiles a la izquierda de la matriz
            if self.__verify_position_in_matrix(i, j - 1, i, j - 2, color):
                return True
        if 0 < j < settings.BOARD_WIDTH - 1:
            # Verificacion los tiles a los lados del tile
            if self.__verify_position_in_matrix(i, j + 1, i, j - 1, color):
                return True

        # validaciones para las filas
        if i < settings.BOARD_HEIGHT - 2:
            # Verificacion los tiles a la abajo de la matriz
            if self.__verify_position_in_matrix(i + 1, j, i + 2, j, color):
                return True
        if i > 1:
            # Verificacion los tiles a la arriba de la matriz
            if self.__verify_position_in_matrix(i - 1, j, i - 2, j, color):
                return True
        if 0 < i < settings.BOARD_HEIGHT - 1:
            # Verificacion los tiles a los lados del tile
            if self.__verify_position_in_matrix(i - 1, j, i + 1, j, color):
                return True

        return False

    def __verify_position_in_matrix(
        self,
        positionfile1: int,
        positioncolumn1: int,
        positionfile2: int,
        positioncolumn2: int,
        color: int,
    ):
        if (
            self.tiles[positionfile1][positioncolumn1].color == color
            and self.tiles[positionfile2][positioncolumn2].color == color
        ):
            return True
        return False

    def verify_posible_match(self) -> bool:

        # Verificar si hay tablero para que no reinicie el tablero
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_HEIGHT):
                if self.tiles[i][j].is_powerup:
                    return True
        # Verificacion de posibles matches en el tablero
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH - 1):

                color1 = self.tiles[i][j].color
                color2 = self.tiles[i][j + 1].color

                self.tiles[i][j].color = color2
                self.tiles[i][j + 1].color = color1

                if self.__check_potential_match(
                    i, j, color2
                ) or self.__check_potential_match(i, j + 1, color1):

                    self.tiles[i][j].color = color1
                    self.tiles[i][j + 1].color = color2
                    return True

                self.tiles[i][j].color = color1
                self.tiles[i][j + 1].color = color2

        for i in range(settings.BOARD_HEIGHT - 1):
            for j in range(settings.BOARD_WIDTH):

                color1 = self.tiles[i][j].color
                color2 = self.tiles[i + 1][j].color

                self.tiles[i][j].color = color2
                self.tiles[i + 1][j].color = color1

                if self.__check_potential_match(
                    i, j, color2
                ) or self.__check_potential_match(i + 1, j, color1):

                    self.tiles[i][j].color = color1
                    self.tiles[i + 1][j].color = color2
                    return True

                self.tiles[i][j].color = color1
                self.tiles[i + 1][j].color = color2

        return False

    def activar_potenciador(self, tile: Tile) -> List[Tile]:
        afectados = [self.tiles[self.powerup_data[0]][self.powerup_data[1]]]
        power_tile = self.tiles[self.powerup_data[0]][self.powerup_data[1]]
        afectados = []  

        print("Activando potenciador")

        if self.powerup_data[3]:
            for j in range(settings.BOARD_WIDTH):
                for i in range(settings.BOARD_HEIGHT):
                    if self.tiles[i][j].color == self.powerup_data[2]:
                        afectados.append(self.tiles[i][j])

        else:
            # Horizontal
            for j in range(settings.BOARD_WIDTH):
                if self.tiles[tile.i][j] is not None:
                    afectados.append(self.tiles[tile.i][j])

            # Vertical
            for i in range(settings.BOARD_HEIGHT):
                if self.tiles[i][tile.j] is not None and i != tile.i:
                    afectados.append(self.tiles[i][tile.j])
   
        afectados.append(power_tile)

        self.powerup_data = None

        return afectados
