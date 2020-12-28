# -*- coding: Utf-8 -*

from typing import Sequence
import pygame
from pygame.math import Vector2
from .entity import Entity
from .constants import AIRPLANE_SIZE
from .clock import Clock

class Airplane(Entity):

    def __init__(self, image: pygame.Surface, departure: Vector2, arrival: Vector2, speed: float, delay: float):
        super().__init__()

        # Textures
        self.__default_airplane_image = pygame.transform.smoothscale(image, AIRPLANE_SIZE).convert_alpha()

        self.__update_clock = Clock()
        self.__take_off = self.__land_on = self.__destroyed = False
        self.__refresh_time = 10 #milliseconds
        self.__departure = departure
        self.__arrival = arrival
        self.__center = departure
        self.__speed = (speed * self.__refresh_time) / 1000
        self.__delay = delay
        self.__direction = arrival - departure
        self.__direction.scale_to_length(self.__speed)
        self.__angle = self.__direction.angle_to(Vector2(1, 0))
        self.__hitbox_points = list[Vector2]()
        self.__hitbox_edges = list[Vector2]()
        self.__update_hitbox()

        # Entities
        self.__image_airplane = pygame.transform.rotate(self.__default_airplane_image, self.__angle).convert_alpha()

        # Towers group
        self.__towers = pygame.sprite.Group()

    @classmethod
    def from_script_setup(cls, image: pygame.Surface, line: Sequence[float]):
        departure_x, departure_y, arrival_x, arrival_y, speed, delay = line
        departure = Vector2(departure_x, departure_y)
        arrival = Vector2(arrival_x, arrival_y)
        return cls(image, departure, arrival, speed, delay)

    def update(self, chrono: float) -> None:
        if not self.__take_off:
            self.__take_off = chrono >= self.__delay
            return
        if self.flying and not self.__update_clock.elapsed_time(self.__refresh_time):
            return
        distance = (self.__arrival - self.__center).length()
        if distance > self.__speed:
            self.__center += self.__direction
            self.__update_hitbox()
        else:
            self.kill()
            self.__land_on = True

    def draw(self, surface: pygame.Surface) -> None:
        if not self.flying:
            return
        if self.sprite_shown():
            surface.blit(self.__image_airplane, self.__image_airplane.get_rect(center=self.__center))
        if self.hitbox_shown():
            pygame.draw.polygon(surface, pygame.Color(46, 173, 46), self.__hitbox_points, width=1)

    def destroy(self) -> None:
        self.__destroyed = True
        self.kill()

    def __update_hitbox(self) -> None:
        rect = self.__default_airplane_image.get_rect(center=self.__center)
        center = Vector2(rect.center)
        all_points = list()
        for point in [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]:
            point = Vector2(point)
            direction = point - center
            all_points.append(center + direction.rotate(-self.__angle))
        self.__hitbox_points = all_points
        nb_points = len(all_points)
        edges = list()
        for i in range(nb_points):
            edges.append(all_points[(i + 1) % nb_points] - all_points[i])
        self.__hitbox_edges = edges

    def get_hitbox_points(self) -> list[Vector2]:
        return self.__hitbox_points

    def get_hitbox_edges(self) -> list[Vector2]:
        return self.__hitbox_edges

    image = property(lambda self: self.__image_airplane)
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

class AirplaneGroup(pygame.sprite.Group):

    def sprites(self) -> list[Airplane]:
        # pylint: disable=useless-super-delegation
        return super().sprites()

    def get_airplanes_not_in_tower_area(self) -> tuple[Airplane, ...]:
        return tuple(filter(lambda airplane: not airplane.in_a_tower_area, self.sprites()))

    def draw(self, surface: pygame.Surface) -> None:
        for airplane in self.sprites():
            airplane.draw(surface)

    def check_collisions(self) -> None:
        airplanes_list = self.get_airplanes_not_in_tower_area()
        nb_airplanes = len(airplanes_list)
        for i in range(nb_airplanes):
            airplane_1 = airplanes_list[i]
            if not airplane_1.flying:
                continue
            for j in range(i + 1, nb_airplanes):
                airplane_2 = airplanes_list[j]
                if not airplane_2.flying:
                    continue
                if airplane_collision(airplane_1, airplane_2):
                    airplane_1.destroy()
                    airplane_2.destroy()
                    break

def airplane_collision(airplane_1: Airplane, airplane_2: Airplane) -> bool:
    points_1 = airplane_1.get_hitbox_points()
    edges_1 = airplane_1.get_hitbox_edges()

    points_2 = airplane_2.get_hitbox_points()
    edges_2 = airplane_2.get_hitbox_edges()

    collision = separating_axis_collision_method

    return collision(edges_1, points_1, points_2) or collision(edges_2, points_2, points_1)

def separating_axis_collision_method(edges_first: list[Vector2], points_first: list[Vector2], points_second: list[Vector2]) -> bool:

    def project_shape(axis: Vector2, points: list[Vector2]) -> tuple[float, float]:
        dot_products = [axis.dot(point) for point in points]
        return min(dot_products), max(dot_products)

    def interval_distance(minA, maxA, minB, maxB) -> float:
        return minB - maxA if minA < minB else minA - maxB

    for edge in edges_first:
        axis = Vector2(-edge.y, edge.x).normalize()
        minA, maxA = project_shape(axis, points_first)
        minB, maxB = project_shape(axis, points_second)
        if interval_distance(minA, maxA, minB, maxB) > 0:
            return False
    return True
