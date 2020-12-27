# -*- coding: Utf-8 -*

from typing import Sequence
import pygame
from pygame.math import Vector2
from .constants import AIRPLANE_SIZE
from .clock import Clock

class Airplane(pygame.sprite.Sprite):

    __show_sprite = True
    __show_hitbox = True

    def __init__(self, image: pygame.Surface, departure: Vector2, arrival: Vector2, speed: float, delay: float):
        super().__init__()

        # Textures
        self.__default_airplane_image = pygame.transform.smoothscale(image, AIRPLANE_SIZE)
        self.__default_hitbox_image = pygame.Surface(AIRPLANE_SIZE, flags=pygame.SRCALPHA)
        pygame.draw.rect(self.__default_hitbox_image, pygame.Color(46, 173, 46), self.__default_hitbox_image.get_rect(), width=3)

        self.__update_clock = Clock()
        self.__departure_clock = Clock()
        self.__take_off = self.__land_on = self.__destroyed = False
        self.__refresh_time = 10 #milliseconds
        self.__departure = departure
        self.__arrival = arrival
        self.__center = departure
        self.__speed = (speed * self.__refresh_time) / 1000
        self.__delay = delay * 1000
        self.__direction = arrival - departure
        self.__direction.scale_to_length(self.__speed)
        self.__angle = self.__direction.angle_to(Vector2(1, 0))

        # Entities
        self.__image_airplane = pygame.transform.rotate(self.__default_airplane_image, self.__angle)
        self.__image_hitbox = pygame.transform.rotate(self.__default_hitbox_image, self.__angle)

        # Towers group
        self.__towers = pygame.sprite.Group()

    @classmethod
    def from_script_setup(cls, image: pygame.Surface, line: Sequence[float]):
        departure_x, departure_y, arrival_x, arrival_y, speed, delay = line
        departure = Vector2(departure_x, departure_y)
        arrival = Vector2(arrival_x, arrival_y)
        return cls(image, departure, arrival, speed, delay)

    @staticmethod
    def show_sprite(status: bool) -> None:
        Airplane.__show_sprite = bool(status)

    @staticmethod
    def sprite_shown() -> bool:
        return Airplane.__show_sprite

    @staticmethod
    def show_hitbox(status: bool) -> None:
        Airplane.__show_hitbox = bool(status)

    @staticmethod
    def hitbox_shown() -> bool:
        return Airplane.__show_hitbox

    def update(self, update_position=True) -> None:
        if not self.__take_off:
            if not update_position:
                self.__departure_clock.tick()
            else:
                self.__take_off = self.__departure_clock.elapsed_time(self.__delay, restart=False)
            return
        if not update_position or (self.flying and not self.__update_clock.elapsed_time(self.__refresh_time)):
            return
        distance = (self.__arrival - self.__center).length()
        if distance > self.__speed:
            self.__center += self.__direction
        else:
            self.kill()
            self.__land_on = True

    def draw(self, surface: pygame.Surface) -> None:
        if not self.flying:
            return
        if self.sprite_shown():
            surface.blit(self.__image_airplane, self.__image_airplane.get_rect(center=self.__center))
        if self.hitbox_shown():
            surface.blit(self.__image_hitbox, self.__image_hitbox.get_rect(center=self.__center))

    def destroy(self) -> None:
        self.__destroyed = True
        self.kill()

    image = property(lambda self: self.__image_hitbox)
    rect = property(lambda self: self.image.get_rect(center=self.__center))
    departure = property(lambda self: self.__departure)
    arrival = property(lambda self: self.__arrival)
    speed = property(lambda self: self.__speed)
    angle = property(lambda self: self.__angle)
    take_off = property(lambda self: self.__take_off)
    land_on = property(lambda self: self.__land_on)
    destroyed = property(lambda self: self.__destroyed)
    flying = property(lambda self: self.__take_off and not self.__land_on and not self.__destroyed)
    towers = property(lambda self: self.__towers)
    in_a_tower_area = property(lambda self: bool(self.__towers))
