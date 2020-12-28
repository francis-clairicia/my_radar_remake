# -*- coding: Utf-8 -*

from typing import Sequence
import pygame
from pygame.math import Vector2
from .entity import Entity
from .airplane import Airplane

class Tower(Entity):

    def __init__(self, image: pygame.Surface, center: Vector2, radius: float):
        super().__init__()
        self.__image_area = pygame.Surface((radius * 2, radius * 2), flags=pygame.SRCALPHA).convert_alpha()
        self.__radius = float(radius)
        pygame.draw.ellipse(self.__image_area, pygame.Color(0, 0, 155), self.__image_area.get_rect(), width=2)
        self.__rect = self.__image_area.get_rect(center=center)
        self.__image_tower = image.convert_alpha()
        self.__airplanes = pygame.sprite.Group()

    @classmethod
    def from_script_setup(cls, image: pygame.Surface, line: Sequence[float]):
        center_x, center_y, radius = line
        center = Vector2(center_x, center_y)
        return cls(image, center, radius)

    def draw(self, surface: pygame.Surface) -> None:
        if self.sprite_shown():
            surface.blit(self.__image_tower, self.__image_tower.get_rect(midbottom=self.__rect.center))
        if self.hitbox_shown():
            surface.blit(self.__image_area, self.__rect)

    def update(self, airplanes_list: list[Airplane, ...]) -> None:
        for airplane in airplanes_list:
            if not airplane.flying:
                continue
            if pygame.sprite.collide_circle(self, airplane):
                self.__airplanes.add(airplane)
                airplane.towers.add(self)
            else:
                self.__airplanes.remove(airplane)
                airplane.towers.remove(self)

    image = property(lambda self: self.__image_area)
    rect = property(lambda self: self.__rect)
    radius = property(lambda self: self.__radius)

class TowerGroup(pygame.sprite.Group):

    def sprites(self) -> list[Tower]:
        # pylint: disable=useless-super-delegation
        return super().sprites()

    def draw(self, surface: pygame.Surface) -> None:
        for tower in self.sprites():
            tower.draw(surface)
