# -*- coding: Utf-8 -*

from typing import Sequence
import pygame
from pygame.math import Vector2
from .entity import Entity
from .airplane import Airplane

class TowerArea(pygame.sprite.Sprite):

    def __init__(self, radius: float, outline: int, outline_color: pygame.Color, **position):
        super().__init__()
        self.__image = pygame.Surface((radius * 2, radius * 2), flags=pygame.SRCALPHA).convert_alpha()
        self.__rect = self.__image.get_rect(**position)
        self.__radius = radius
        pygame.draw.ellipse(self.__image, outline_color, self.__image.get_rect(), width=outline)

    image = property(lambda self: self.__image)
    rect = property(lambda self: self.__rect)
    radius = property(lambda self: self.__radius)

class Tower(Entity):

    def __init__(self, image: pygame.Surface, center: Vector2, radius: float, screen_rect: pygame.Rect):
        super().__init__()
        self.__area_outline = area_outline = 2
        self.__area_color = area_color = pygame.Color(0, 0, 155)
        self.__image_area = TowerArea(radius, area_outline, area_color, center=center)
        self.__area = pygame.sprite.Group()
        self.__image_tower = image.convert_alpha()
        self.__airplanes = pygame.sprite.Group()
        self.update_area(screen_rect)

    @classmethod
    def from_script_setup(cls, image: pygame.Surface, line: Sequence[float], screen_rect: pygame.Rect):
        center_x, center_y, radius = line
        center = Vector2(center_x, center_y)
        return cls(image, center, radius, screen_rect)

    def draw(self, surface: pygame.Surface) -> None:
        if self.sprite_shown():
            surface.blit(self.__image_tower, self.__image_tower.get_rect(midbottom=self.rect.center))
        if self.hitbox_shown():
            self.__area.draw(surface)

    def update(self, airplanes_list: list[Airplane, ...]) -> None:
        for airplane in airplanes_list:
            if not airplane.flying:
                continue
            if pygame.sprite.spritecollideany(airplane, self.__area, collided=pygame.sprite.collide_circle) is not None:
                self.__airplanes.add(airplane)
                airplane.towers.add(self)
            else:
                self.__airplanes.remove(airplane)
                airplane.towers.remove(self)

    def update_area(self, screen_rect: pygame.Rect) -> None:
        self.__area.empty()
        self.__area.add(self.__image_area)
        area_rect = self.__image_area.rect
        area_check = [
            (area_rect.top < screen_rect.top,       {"centerx": area_rect.centerx, "top": screen_rect.bottom - abs(screen_rect.top - area_rect.top)}),
            (area_rect.bottom > screen_rect.bottom, {"centerx": area_rect.centerx, "bottom": screen_rect.top + abs(screen_rect.bottom - area_rect.bottom)}),
            (area_rect.left < screen_rect.left,     {"centery": area_rect.centery, "left": screen_rect.right - abs(screen_rect.left - area_rect.left)}),
            (area_rect.right > screen_rect.right,   {"centery": area_rect.centery, "right": screen_rect.left + abs(screen_rect.right - area_rect.right)})
        ]
        for area_out_of_screen, new_area_pos in area_check:
            if area_out_of_screen:
                self.__area.add(TowerArea(self.__image_area.radius, self.__area_outline, self.__area_color, **new_area_pos))

    image = property(lambda self: self.__image_area.image)
    rect = property(lambda self: self.__image_area.rect)
    radius = property(lambda self: self.__image_area.radius)

class TowerGroup(pygame.sprite.Group):

    def sprites(self) -> list[Tower]:
        # pylint: disable=useless-super-delegation
        return super().sprites()

    def draw(self, surface: pygame.Surface) -> None:
        for tower in self.sprites():
            tower.draw(surface)
