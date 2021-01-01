# -*- coding: Utf-8 -*

from typing import Sequence, Union
import pygame
from pygame.math import Vector2
from .entity import Entity, EntityEditor, EntityGroup
from .airplane import Airplane

class TowerArea(pygame.sprite.Sprite):

    def __init__(self, radius: float, outline: int, outline_color: pygame.Color, **position):
        super().__init__()
        self.__outline = outline
        self.__outline_color = outline_color
        self.__position = position
        self.set_radius(radius)

    def set_center(self, center: Union[Vector2, Sequence[float]]) -> None:
        self.__position = {"center": center}

    def set_radius(self, radius: float) -> None:
        radius = float(radius)
        self.__image = pygame.Surface((radius * 2, radius * 2), flags=pygame.SRCALPHA).convert_alpha()
        self.__radius = radius
        pygame.draw.ellipse(self.__image, self.__outline_color, self.__image.get_rect(), width=self.__outline)

    image = property(lambda self: self.__image)
    rect = property(lambda self: self.__image.get_rect(**self.__position))
    center = property(lambda self: Vector2(self.rect.center), set_center)
    radius = property(lambda self: self.__radius, set_radius)
    color = property(lambda self: self.__outline_color)

class Tower(Entity):

    def __init__(self, image: pygame.Surface, center: Vector2, radius: float, screen_rect: pygame.Rect):
        super().__init__()
        self.__area_outline = area_outline = 2
        self.__area_color = area_color = pygame.Color(0, 0, 155)
        self.__image_area = TowerArea(radius, area_outline, area_color, center=center)
        self.__area = pygame.sprite.Group()
        self.__image_tower = image.convert_alpha()
        self.__airplanes = pygame.sprite.Group()
        self.__screen_rect = screen_rect
        self.update_area()

    @classmethod
    def from_script_setup(cls, image: pygame.Surface, line: Sequence[float], screen_rect: pygame.Rect):
        center_x, center_y, radius = line
        center = Vector2(center_x, center_y)
        return cls(image, center, radius, screen_rect)

    def get_setup(self) -> list[float]:
        # pylint: disable=no-member
        return [*(self.area.center.xy), self.area.radius]

    def load_setup(self, line: list[float]) -> None:
        center_x, center_y, radius = line
        self.__image_area.set_center((center_x, center_y))
        self.__image_area.set_radius(radius)
        self.update_area()

    def draw(self, surface: pygame.Surface) -> None:
        if self.sprite_shown():
            surface.blit(self.image, self.rect)
        if self.hitbox_shown():
            self.__area.draw(surface)

    def update(self, airplanes_list: list[Airplane, ...]) -> None:
        for airplane in airplanes_list:
            if not airplane.flying:
                continue
            if any(airplane_in_area(airplane, area) for area in self.__area):
                self.__airplanes.add(airplane)
                airplane.towers.add(self)
            else:
                self.__airplanes.remove(airplane)
                airplane.towers.remove(self)

    def update_area(self) -> None:
        screen_rect = self.__screen_rect
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

    def set_alpha(self, value: int) -> None:
        for area in self.__area:
            area.image.set_alpha(value)
        self.__image_tower.set_alpha(value)
        self.__area_color.a = value

    image = property(lambda self: self.__image_tower)
    rect = property(lambda self: self.__image_tower.get_rect(midbottom=self.__image_area.rect.center))
    area = property(lambda self: self.__image_area)

class TowerEditor(Tower, EntityEditor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__update_point = None
        self.__font = pygame.font.SysFont("calibri", 15, bold=True)

    def __repr__(self) -> str:
        return "<{} center={} radius={}>".format(
            self.__class__.__name__,
            (self.area.center.x, self.area.center.y),
            self.area.radius
        )

    __str__ = __repr__

    def draw(self, surface: pygame.Surface) -> None:
        if self.selected:
            text_radius = self.__font.render("{}px".format(round(self.area.radius, 1)), True, self.area.color)
            line_rect = pygame.draw.line(surface, self.area.color, self.area.center, self.area.rect.midright, width=2)
            surface.blit(text_radius, text_radius.get_rect(centerx=line_rect.centerx, bottom=line_rect.top - 5))
        super().draw(surface)

    def on_click(self, mouse_pos: tuple[int, int]) -> bool:
        if not self.selected:
            return False

        value_between = lambda x, min_x, max_x: x >= min_x and x <= max_x

        if value_between(self.area.center.distance_to(mouse_pos), round(0.9 * self.area.radius), round(1.1 * self.area.radius)):
            self.__update_point = self.__update_area_radius
        elif self.rect.collidepoint(*mouse_pos):
            self.__update_point = self.__update_area_center
        else:
            self.__update_point = None
        return callable(self.__update_point)

    def on_move(self, mouse_pos: tuple[int, int]) -> None:
        if callable(self.__update_point):
            self.__update_point(mouse_pos)
        else:
            self.__update_area_center(mouse_pos)

    def __update_area_center(self, mouse_pos: tuple[int, int]) -> None:
        self.area.center = mouse_pos
        self.update_area()

    def __update_area_radius(self, mouse_pos: tuple[int, int]) -> None:
        self.area.radius = self.area.center.distance_to(mouse_pos)
        self.update_area()

    def on_key_press(self, key: int) -> bool:
        if key in [pygame.K_LEFT, pygame.K_RIGHT]:
            if key == pygame.K_LEFT:
                self.area.radius = max(self.area.radius - 5, 0)
            elif key == pygame.K_RIGHT:
                self.area.radius += 5
            return True
        return False

    @staticmethod
    def get_action_dict() -> dict[str, dict[str, str]]:
        return {
            "tower": {
                "Left arrow": "Decrease area radius",
                "Right arrow": "Increase area radius",
                "Click on tower's sprite + Move": "Change tower's area center",
                "Click on tower's area circle + Move": "Change tower's area raidus",
            }
        }


class TowerGroup(EntityGroup):

    def __init__(self):
        super().__init__("T")

    def sprites(self) -> list[Union[Tower, TowerEditor]]:
        # pylint: disable=useless-super-delegation
        return super().sprites()


def airplane_in_area(airplane: Airplane, area: TowerArea) -> bool:
    # segments = [(point, point + edge) for point, edge in zip(airplane.get_hitbox_points(), airplane.get_hitbox_edges())]
    # area_center = Vector2(area.rect.center)
    # area_radius = area.radius
    # for point_1, point_2 in segments:
    #     distance_p1_center = point_1.distance_to(area_center)
    #     distance_p2_center = point_2.distance_to(area_center)
    #     if distance_p1_center <= area_radius or distance_p2_center <= area_radius:
    #         return True
    #     direction_p1_p2 = (point_2 - point_1).normalize()
    #     vector_p1_center = area_center - point_1
    #     if abs(direction_p1_p2.cross(vector_p1_center)) <= area_radius:
    #         return True
    # return False
    return Vector2(airplane.rect.center).distance_to(area.center) <= area.radius
