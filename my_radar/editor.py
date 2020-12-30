# -*- coding: Utf-8 -*

import pygame
from pygame.math import Vector2
from typing import Type
from .entity import EntityEditor, EntityEditorGroup
from .airplane import AirplaneEditor
from .tower import TowerEditor

class EditorToolboxButton:

    def __init__(self, width: int, height: int, image: pygame.Surface, entity: Type[EntityEditor], group: pygame.sprite.Group, **position):
        self.__rect = pygame.Surface((width, height)).get_rect(**position)
        w, h = image.get_size()
        max_width = round(0.9 * width)
        max_height = round(0.9 * height)
        scale_w = max_width / w
        scale_h = max_height / h
        if scale_w >= 1 and scale_h >= 1:
            new_width, new_height = max_width, max_height
        else:
            scale = min(scale_w, scale_h)
            new_width = round(w * scale)
            new_height = round(h * scale)
        self.__image_entity = image
        self.__image_button = pygame.transform.smoothscale(image, (new_width, new_height)).convert_alpha()
        self.__entity = entity
        self.__group = group

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, "black", self.__rect, width=2)
        surface.blit(self.__image_button, self.__image_button.get_rect(center=self.__rect.center))

    def click(self, mouse_pos: tuple[int, int]) -> bool:
        return self.__rect.collidepoint(*mouse_pos)

    image = property(lambda self: self.__image_entity)
    entity = property(lambda self: self.__entity)
    group = property(lambda self: self.__group)

class EditorToolbox:

    def __init__(self, airplane_image: pygame.Surface, tower_image: pygame.Surface, airplanes_group: pygame.sprite.Group, towers_group: pygame.sprite.Group):
        self.__show = False
        self.__rect = pygame.Rect(0, 0, 0, 100)

        self.__buttons = list[EditorToolboxButton]()
        centery = self.__rect.centery
        left = 30
        width = height = 60
        buttons = [
            (AirplaneEditor, airplane_image, airplanes_group),
            (TowerEditor, tower_image, towers_group)
        ]
        for entity, image, group in buttons:
            self.__buttons.append(EditorToolboxButton(width, height, image, entity, group, left=left, centery=centery))
            left += width + 20

    def draw(self, surface: pygame.Surface) -> None:
        if self.__show:
            self.__rect.width = surface.get_width()
            pygame.draw.rect(surface, "white", self.__rect, border_bottom_left_radius=30, border_bottom_right_radius=30)
            pygame.draw.rect(surface, "black", self.__rect, width=2, border_bottom_left_radius=30, border_bottom_right_radius=30)
            for button in self.__buttons:
                button.draw(surface)
        else:
            pygame.draw.rect(surface, "white", (0, 0, surface.get_width(), 20), border_bottom_left_radius=30, border_bottom_right_radius=30)
            pygame.draw.rect(surface, "black", (0, 0, surface.get_width(), 20), width=2, border_bottom_left_radius=30, border_bottom_right_radius=30)

    def handle_event(self, event: pygame.event.Event, entity_editor_grp: EntityEditorGroup, screen_rect: pygame.Rect) -> None:
        if not entity_editor_grp.moving:
            if not self.__show:
                self.__show = pygame.mouse.get_pos()[1] == 0
            else:
                self.__show = self.__rect.collidepoint(*pygame.mouse.get_pos())
        else:
            self.__show = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.__show:
            entity = None
            button = None
            for button in self.__buttons:
                if button.click(event.pos):
                    if button.entity is AirplaneEditor:
                        entity = AirplaneEditor(button.image, Vector2(event.pos), Vector2(screen_rect.center), 10, 0)
                        break
                    if button.entity is TowerEditor:
                        entity = TowerEditor(button.image, Vector2(event.pos), 100, screen_rect)
            if isinstance(entity, EntityEditor):
                entity.add(button.group, entity_editor_grp)
                entity.on_click(event.pos)
                entity_editor_grp.select(entity, active=True)
                self.__show = False

    def is_shown(self) -> bool:
        return self.__show
