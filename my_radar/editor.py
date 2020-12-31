# -*- coding: Utf-8 -*

import pygame
from pygame.math import Vector2
from typing import Type
from .entity import EntityEditor, EntityEditorGroup
from .airplane import AirplaneEditor
from .tower import TowerEditor

def create_rect_from_edge(left, top, right, bottom) -> pygame.Rect:
    return pygame.Rect(left, top, (right - left), (bottom - top))

def get_hidden_rect_between_centery(rect: pygame.Rect, height: int) -> pygame.Rect:
    rect_top = pygame.Rect(0, 0, rect.width, height)
    rect_bottom = pygame.Rect(0, 0, rect.width, height)
    rect_top.top = rect.top
    rect_bottom.bottom = rect.bottom
    rect_top.centerx = rect_bottom.centerx = rect.centerx
    return create_rect_from_edge(rect.left, rect_top.centery, rect.right, rect_bottom.centery)

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
            mouse_pos = pygame.mouse.get_pos()
            if not self.__show:
                self.__show = mouse_pos[1] == 0
            else:
                self.__show = self.__rect.collidepoint(*mouse_pos)
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


class EditorSideBoardScrollbar:

    def __init__(self, whole_box: pygame.Surface, width: int, color: pygame.Color, cursor_color: pygame.Color):
        self.__whole_box = whole_box
        self.__max_height = whole_box.get_height()
        self.__scrollbar = pygame.Surface((width, self.__max_height)).convert()
        self.__sub_surface = whole_box
        self.__cursor_rect_percent = [0, 1]
        self.__cursor_percent = 0
        self.__color = pygame.Color(color)
        self.__cursor_color = pygame.Color(cursor_color)
        self.__active = False

    def get_sub_surface(self) -> pygame.Surface:
        return self.__sub_surface

    def set_max_height(self, value: int) -> None:
        value = max(round(value), 0)
        if value != self.__max_height:
            self.__max_height = value
            self.__update_subsurface()

    def set_scrollbar_height(self, value: int):
        value = max(round(value), 0)
        if value != self.__scrollbar.get_height():
            self.__scrollbar = pygame.Surface((self.__scrollbar.get_width(), value)).convert()

    def draw(self, surface: pygame.Surface, **position) -> None:
        self.__scrollbar.fill(self.__color)
        scrollbar = self.__scrollbar.get_rect()
        cursor_rect = create_rect_from_edge(0, scrollbar.height * self.__cursor_rect_percent[0], scrollbar.width, scrollbar.height * self.__cursor_rect_percent[1])
        pygame.draw.rect(self.__scrollbar, self.__cursor_color, cursor_rect)
        surface.blit(self.__scrollbar, self.__scrollbar.get_rect(**position))

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.__cursor_rect_percent[0] == 0 and self.__cursor_rect_percent[1] == 1:
            return
        if event.type == pygame.MOUSEWHEEL:
            y = -(event.y) * 0.2
            self.__cursor_percent += y
            if self.__cursor_percent < 0:
                self.__cursor_percent = 0
            elif self.__cursor_percent > 1:
                self.__cursor_percent = 1
            self.__update_subsurface()

    def __update_subsurface(self) -> None:
        box = self.__whole_box.get_rect()
        left = 0
        right = self.__whole_box.get_width()
        top = self.__whole_box.get_height() * self.__cursor_rect_percent[0]
        bottom = self.__whole_box.get_height() * self.__cursor_rect_percent[1]
        rect = pygame.Rect(left, top, right - left, min(bottom - top, self.__max_height))
        hidden_rect = get_hidden_rect_between_centery(box, rect.height)
        rect.centery = hidden_rect.top + (self.__cursor_percent * hidden_rect.height)
        self.__sub_surface = self.__whole_box.subsurface(rect)
        self.__cursor_rect_percent = [rect.top / self.__whole_box.get_height(), rect.bottom / self.__whole_box.get_height()]

class EditorSideBoard:

    def __init__(self, *custom_actions: dict[str, dict[str, str]]):
        actions = {
            "key": {
                "Escape": "Close editor",
                "F12": "Show/hide editor stuff",
                "Delete": "Remove selected entity",
                "Ctrl+S": "Save in file",
            },
            "mouse": {
                "Click on entity": "Select entity",
                "Click + Move": "- on selected entity: Action on entity\n- on map: Move the camera",
                "Mouse wheel": "Zoom in/out camera"
            }
        }
        for action in custom_actions:
            actions |= action

        font = ("calibri", 20)
        action_font = pygame.font.SysFont(*font)
        description_font = pygame.font.SysFont(font[0], font[1] - 4)
        title_font = pygame.font.SysFont(*font, bold=True)
        title_font.set_underline(True)
        line_blank = pygame.Surface(action_font.size("|"), flags=pygame.SRCALPHA).convert_alpha()
        space_between = 5 #px

        rendered_lines = list[pygame.Surface]()
        rendered_lines.append(line_blank)
        for action_title, action_dict in actions.items():
            rendered_lines.append(title_font.render("{} actions:".format(action_title.title()), True, "black"))
            for action, action_description in action_dict.items():
                rendered_lines.append(action_font.render(f"'{action}' :", True, "black"))
                for line in action_description.splitlines():
                    rendered_lines.append(description_font.render(line, True, "black"))
                rendered_lines.append(line_blank)

        box_width = max(line.get_width() for line in rendered_lines)
        box_height = sum(line.get_height() for line in rendered_lines) + (space_between * (len(rendered_lines) - 1))
        self.__box = pygame.Surface((box_width, box_height), flags=pygame.SRCALPHA).convert_alpha()
        top = 0
        for line in rendered_lines:
            rect = self.__box.blit(line, line.get_rect(left=0, top=top))
            top = rect.bottom + space_between

        self.__scrollbar = EditorSideBoardScrollbar(self.__box, 20, pygame.Color(230, 230, 230), pygame.Color(120, 120, 120))
        self.__box_rect = pygame.Rect(0, 0, 0, 0)
        self.__strip_rect = pygame.Rect(0, 0, 0, 0)
        self.__mouse_on_strip = False
        self.__show = False

    def draw(self, surface: pygame.Surface) -> None:
        surface_rect = surface.get_rect()
        if self.__show:
            self.__box_rect = pygame.Rect(0, 0, self.__box.get_width() + 100, surface.get_height())
            pygame.draw.rect(surface, "white", self.__box_rect)
            pygame.draw.rect(surface, "black", self.__box_rect, width=1)
            self.__scrollbar.set_scrollbar_height(surface.get_height())
            self.__scrollbar.set_max_height(self.__box_rect.height)
            box = self.__scrollbar.get_sub_surface()
            box_rect = surface.blit(box, box.get_rect(right=self.__box_rect.right - 10, top=self.__box_rect.top))
            self.__scrollbar.draw(surface)
        else:
            self.__strip_rect = box_rect = pygame.Surface((10, 100)).get_rect(left=surface_rect.left + 10, centery=surface_rect.centery)
            if self.__mouse_on_strip:
                box_rect = box_rect.move(10, 0)
            pygame.draw.rect(surface, "white", box_rect)
            pygame.draw.rect(surface, "black", box_rect, width=1)

    def is_shown(self) -> bool:
        return self.__show

    def handle_event(self, event: pygame.event.Event, entity_editor_grp: EntityEditorGroup, screen_rect: pygame.Rect) -> None:
        if not entity_editor_grp.moving:
            if not self.__show:
                mouse_pos = pygame.mouse.get_pos()
                value_between = lambda x, min_x, max_x: x >= min_x and x <= max_x
                self.__mouse_on_strip = value_between(mouse_pos[0], screen_rect.left, self.__strip_rect.right) and value_between(mouse_pos[1], self.__strip_rect.top, self.__strip_rect.bottom)
                if self.__mouse_on_strip:
                    self.__show = mouse_pos[0] == 0
            else:
                self.__show = self.__box_rect.collidepoint(*pygame.mouse.get_pos())
        else:
            self.__show = False
        self.__scrollbar.handle_event(event)
