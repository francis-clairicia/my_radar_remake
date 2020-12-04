# -*- coding: Utf-8 -*

from typing import Sequence
import pygame
from pygame.math import Vector2
from .constants import AIRPLANE_SIZE
from .clock import Clock

class Airplane(pygame.sprite.Sprite):

    def __init__(self, image: pygame.Surface, departure: Vector2, arrival: Vector2, speed: float, delay: float):
        super().__init__()
        self.__default_image = pygame.transform.smoothscale(image, AIRPLANE_SIZE)
        self.__clock = Clock()
        self.__refresh_time = 10 #milliseconds
        self.__departure = departure
        self.__arrival = arrival
        self.__center = departure
        self.__speed = (speed * self.__refresh_time) / 1000
        self.__delay = delay
        self.__direction = arrival - departure
        self.__direction.scale_to_length(self.__speed)
        self.__angle = self.__direction.angle_to(Vector2(1, 0))
        self.__image = pygame.transform.rotate(self.__default_image, self.__angle)
        self.__hitbox = HitBoxAirplane(self)

    @classmethod
    def from_script_setup(cls, image: pygame.Surface, line: Sequence[float]):
        departure_x, departure_y, arrival_x, arrival_y, speed, delay = line
        departure = Vector2(departure_x, departure_y)
        arrival = Vector2(arrival_x, arrival_y)
        return cls(image, departure, arrival, speed, delay)

    def update(self) -> None:
        if not self.__clock.elapsed_time(self.__refresh_time):
            return
        distance = (self.__arrival - self.__center).length()
        if distance > self.__speed:
            self.__center += self.__direction
        else:
            self.kill()
            self.__hitbox.kill()

    image = property(lambda self: self.__image)
    rect = property(lambda self: self.image.get_rect(center=self.__center))
    departure = property(lambda self: self.__departure)
    arrival = property(lambda self: self.__arrival)
    speed = property(lambda self: self.__speed)
    angle = property(lambda self: self.__angle)
    hitbox = property(lambda self: self.__hitbox)

class HitBoxAirplane(pygame.sprite.Sprite):

    def __init__(self, airplane: Airplane):
        super().__init__()
        self.__airplane = airplane
        self.__color = pygame.Color(46, 173, 46)
        self.__default_image = image = pygame.Surface(AIRPLANE_SIZE, flags=pygame.SRCALPHA)
        pygame.draw.rect(image, self.__color, image.get_rect(), width=3)
        self.__image = pygame.transform.rotate(image, self.__airplane.angle)

    @property
    def image(self) -> pygame.Surface:
        return self.__image

    @property
    def rect(self) -> pygame.Rect:
        return self.__airplane.rect