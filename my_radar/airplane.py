# -*- coding: Utf-8 -*

from typing import Union, Sequence
from functools import wraps
import pygame
from pygame.math import Vector2
from .entity import Entity, EntityEditor, EntityGroup
from .constants import AIRPLANE_SIZE
from .clock import Clock

class Airplane(Entity):

    def __init__(self, image: pygame.Surface, departure: Vector2, arrival: Vector2, speed: float, delay: float, take_off=False, edit=False):
        super().__init__()

        # Textures
        self.__default_airplane_image = self.__image_airplane = pygame.transform.smoothscale(image, AIRPLANE_SIZE).convert_alpha()

        self.__edit = bool(edit)
        self.__update_clock = Clock()
        self.__refresh_time = 10 #milliseconds
        self.__center = self.__departure = Vector2(departure)
        self.__arrival = Vector2(arrival)
        self.__speed = max(speed, 0)
        self.__delay = delay
        self.__land_on = self.__destroyed = False
        self.__take_off = take_off or (delay <= 0)
        self.__hitbox_points = list[Vector2]()
        self.__hitbox_edges = list[Vector2]()
        self.__hitbox_color = pygame.Color(46, 173, 46)
        self.__update_direction()

        # Towers group
        self.__towers = pygame.sprite.Group()

    @classmethod
    def from_script_setup(cls, image: pygame.Surface, line: Sequence[float], **kwargs):
        departure_x, departure_y, arrival_x, arrival_y, speed, delay = line
        departure = Vector2(departure_x, departure_y)
        arrival = Vector2(arrival_x, arrival_y)
        return cls(image, departure, arrival, speed, delay, **kwargs)

    def get_setup(self) -> list[float]:
        # pylint: disable=no-member
        return [*(self.__departure.xy), *(self.__arrival.xy), self.speed, self.__delay]

    def load_setup(self, line: list[float]) -> None:
        self.__departure.x, self.__departure.y, self.__arrival.x, self.__arrival.y, self.__speed, self.__delay = line
        self.__center = self.__departure
        self.__update_direction()

    def update(self, chrono: float) -> None:
        if not self.__take_off:
            self.__take_off = chrono >= self.__delay
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
            pygame.draw.polygon(surface, self.__hitbox_color, self.__hitbox_points, width=1)

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

    def set_alpha(self, value: int) -> None:
        self.__image_airplane.set_alpha(value)
        self.__hitbox_color.a = value

    def set_departure(self, point: Union[Vector2, Sequence[float]]) -> None:
        if not self.__edit:
            raise AttributeError("can't set attribute")
        self.__center = self.__departure = Vector2(point)
        self.__update_direction()

    def set_arrival(self, point: Union[Vector2, Sequence[float]]) -> None:
        if not self.__edit:
            raise AttributeError("can't set attribute")
        self.__arrival = Vector2(point)
        self.__update_direction()

    def set_speed(self, value: float) -> None:
        if not self.__edit:
            raise AttributeError("can't set attribute")
        self.__speed = max(value, 0)
        self.__update_direction()

    def set_delay(self, value: float) -> None:
        if not self.__edit:
            raise AttributeError("can't set attribute")
        self.__delay = float(value)

    def __update_direction(self) -> None:
        self.__direction = self.__arrival - self.__departure
        if self.__direction.length_squared() > 0:
            self.__direction.scale_to_length((self.__speed * self.__refresh_time) / 1000)
        self.__angle = self.__direction.angle_to(Vector2(1, 0))
        self.__image_airplane = pygame.transform.rotate(self.__default_airplane_image, self.__angle).convert_alpha()
        self.__update_hitbox()

    image = property(lambda self: self.__image_airplane)
    rect = property(lambda self: self.image.get_rect(center=self.__center))
    departure = property(lambda self: self.__departure, set_departure)
    arrival = property(lambda self: self.__arrival, set_arrival)
    speed = property(lambda self: self.__speed, set_speed)
    delay = property(lambda self: self.__delay, set_delay)
    angle = property(lambda self: self.__angle)
    take_off = property(lambda self: self.__take_off)
    land_on = property(lambda self: self.__land_on)
    destroyed = property(lambda self: self.__destroyed)
    flying = property(lambda self: self.__take_off and not self.__land_on and not self.__destroyed)
    towers = property(lambda self: self.__towers)
    in_a_tower_area = property(lambda self: bool(self.__towers))

def init_decorator(function):

    @wraps(function)
    def wrapper(*args, **kwargs):
        kwargs["edit"] = kwargs["take_off"] = True
        return function(*args, **kwargs)

    return wrapper

class AirplaneEditor(Airplane, EntityEditor):

    @init_decorator
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__arrowhead_rect = pygame.Rect(0, 0, 0, 0)
        self.__font = pygame.font.SysFont("calibri", 15, bold=True)
        self.__update_point = None

    def __repr__(self) -> str:
        return "<{} departure={} arrival={} speed={} delay={}>".format(
            self.__class__.__name__,
            (self.departure.x, self.departure.y),
            (self.arrival.x, self.arrival.y),
            self.speed,
            self.delay,
        )

    __str__ = __repr__

    def draw(self, surface: pygame.Surface) -> None:
        if self.selected:
            text_color = arrow_color = pygame.Color(0, 0, 150)

            #Draw arrow
            arrow_rect = pygame.draw.aaline(surface, arrow_color, self.departure, self.arrival)
            arrowhead_semi_angle = 30
            arrowhead_length = 10
            line_direction_inverted = self.departure - self.arrival
            if line_direction_inverted.length_squared() > 0:
                line_direction_inverted.scale_to_length(arrowhead_length)
                arrowhead = [
                    self.arrival,
                    self.arrival + line_direction_inverted.rotate(arrowhead_semi_angle),
                    self.arrival + line_direction_inverted.rotate(-arrowhead_semi_angle),
                ]
                self.__arrowhead_rect = pygame.draw.aalines(surface, arrow_color, True, arrowhead)

            # Draw values
            text_angle = self.angle
            if abs(text_angle) > 90:
                text_angle = 180 + text_angle
            text_move_angle = text_angle + 90
            text_move_offset = Vector2(15, 0).rotate(-text_move_angle)
            text_speed = pygame.transform.rotate(self.__font.render("Speed: {}px/sec".format(round(self.speed, 1)), True, text_color), text_angle)
            text_delay = pygame.transform.rotate(self.__font.render("Delay before taking off: {}sec".format(round(self.delay, 1)), True, text_color), text_angle)
            surface.blit(text_speed, text_speed.get_rect(center=(Vector2(arrow_rect.center) + text_move_offset)))
            surface.blit(text_delay, text_delay.get_rect(center=(Vector2(arrow_rect.center) - text_move_offset)))
        super().draw(surface)

    def on_click(self, mouse_pos: tuple[int, int]) -> bool:
        if not self.selected:
            return False
        if self.rect.collidepoint(*mouse_pos):
            self.__update_point = self.set_departure
        elif self.__arrowhead_rect.collidepoint(*mouse_pos):
            self.__update_point = self.set_arrival
        else:
            self.__update_point = None
        return callable(self.__update_point)

    def on_move(self, mouse_pos: tuple[int, int]) -> None:
        if self.selected and callable(self.__update_point):
            self.__update_point(mouse_pos)

    def on_key_press(self, key: int) -> bool:
        if key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
            if key == pygame.K_LEFT:
                self.speed -= 1
            elif key == pygame.K_RIGHT:
                self.speed += 1
            elif key == pygame.K_UP:
                self.delay += 0.1
            elif key == pygame.K_DOWN:
                self.delay -= 0.1
            return True
        return False

    @staticmethod
    def get_action_dict() -> dict[str, dict[str, str]]:
        return {
            "airplane": {
                "Left arrow": "Decrease speed value",
                "Right arrow": "Increase speed value",
                "Up arrow": "Increase delay value",
                "Down arrow": "Decrease delay value",
                "Click on airplane's sprite + Move": "Change airplane's departure point",
                "Click on airplane's arrowhead + Move": "Change airplane's arrival point"
            }
        }

class AirplaneGroup(EntityGroup):

    def __init__(self):
        super().__init__("A")

    def sprites(self) -> list[Union[Airplane, AirplaneEditor]]:
        # pylint: disable=useless-super-delegation
        return super().sprites()

    def get_airplanes_not_in_tower_area(self) -> tuple[Airplane, ...]:
        return tuple(filter(lambda airplane: not airplane.in_a_tower_area, self.sprites()))

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
