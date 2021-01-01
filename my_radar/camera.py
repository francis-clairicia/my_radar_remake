# -*- coding: Utf-8 -*

import pygame
from typing import Union
from .airplane import Airplane

class Camera:

    def __init__(self, screen: pygame.Surface):
        self.__screen = self.__surface = screen
        self.__scale = 1
        self.__rect = self.__screen.get_rect()
        self.__airplane = None
        self.__moving = False
        self.__previous_infos = dict()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEWHEEL:
            new_scale = self.__scale - (event.y) / 10
            if new_scale >= 0.1 and new_scale <= 1:
                self.__scale = new_scale
                self.__rect.center = pygame.mouse.get_pos()
                self.__update_rect()
        elif event.type == pygame.MOUSEMOTION and event.buttons[0] and not isinstance(self.__airplane, Airplane):
            self.__moving = True
            x, y = event.rel
            self.__rect.move_ip(-x * self.__scale, -y * self.__scale)
            self.__update_rect()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.__moving = False

    def stop_move(self) -> None:
        self.__moving = False

    def focus(self, airplane: Union[Airplane, None]) -> None:
        if isinstance(airplane, Airplane):
            if not isinstance(self.__airplane, Airplane):
                self.__previous_infos["scale"] = self.__scale
                self.__previous_infos["rect"] = self.__rect
                self.__scale = 0.3
            self.__airplane = airplane
        else:
            self.__airplane = None
            if self.__previous_infos:
                self.__scale = self.__previous_infos["scale"]
                self.__rect = self.__previous_infos["rect"]
            self.__previous_infos.clear()
        self.__update_rect()

    def __update_rect(self) -> None:
        screen_rect = self.__screen.get_rect()
        if self.__scale == 1:
            self.__rect = screen_rect
        else:
            center = self.__rect.center
            self.__rect.size = (screen_rect.w * self.__scale, screen_rect.h * self.__scale)
            self.__rect.center = center
            self.__rect.left = max(self.__rect.left, screen_rect.left)
            self.__rect.right = min(self.__rect.right, screen_rect.right)
            self.__rect.top = max(self.__rect.top, screen_rect.top)
            self.__rect.bottom = min(self.__rect.bottom, screen_rect.bottom)
        self.__surface = self.__screen.subsurface(self.__rect)

    def update(self) -> None:
        if isinstance(self.__airplane, Airplane):
            if self.__airplane.alive():
                self.__rect.center = self.__airplane.rect.center
                self.__update_rect()
            else:
                self.focus(None)
        self.__screen.blit(pygame.transform.smoothscale(self.__surface, self.__screen.get_size()), (0, 0))

    def map_cursor(self, cursor_pos: tuple[int, int]) -> tuple[int, int]:
        return round(self.__scale * cursor_pos[0]) + self.__rect.left, round(self.__scale * cursor_pos[1]) + self.__rect.top

    moving = property(lambda self: self.__moving)
