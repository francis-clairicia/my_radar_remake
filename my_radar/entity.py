# -*- coding: Utf-8 -*

import pygame
from typing import Union

class Entity(pygame.sprite.Sprite):

    __show_sprite = True
    __show_hitbox = True

    @staticmethod
    def show_sprite(status: bool) -> None:
        Entity.__show_sprite = bool(status)

    @staticmethod
    def sprite_shown() -> bool:
        return Entity.__show_sprite

    @staticmethod
    def show_hitbox(status: bool) -> None:
        Entity.__show_hitbox = bool(status)

    @staticmethod
    def hitbox_shown() -> bool:
        return Entity.__show_hitbox

    def draw(self, surface: pygame.Surface) -> None:
        pass

    def set_alpha(self, value: int) -> None:
        pass

class EntityEditorSelector(pygame.sprite.GroupSingle):
    pass

class EntityEditor(Entity):

    def on_click(self, mouse_pos: tuple[int, int]) -> bool:
        # pylint: disable=unused-argument
        return False

    def on_move(self, mouse_pos: tuple[int, int]) -> None:
        pass

    @property
    def selected(self) -> bool:
        return any(isinstance(group, EntityEditorSelector) for group in self.groups())

class EntityEditorGroup(pygame.sprite.Group):

    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.__selected = None
        self.__selector = EntityEditorSelector()
        self.__active = False
        self.__moving = False

    def sprites(self) -> list[EntityEditor]:
        # pylint: disable=useless-super-delegation
        return super().sprites()

    def handle_event(self, event_type: int, mouse_pos: tuple[int, int]) -> None:
        if event_type == pygame.MOUSEBUTTONDOWN and self.selected is not None:
            if self.selected.on_click(mouse_pos):
                self.__active = True
        elif event_type == pygame.MOUSEBUTTONUP:
            self.__active = self.__moving = False
        elif event_type == pygame.MOUSEMOTION and self.__active:
            self.__moving = True
            self.selected.on_move(mouse_pos)

    def select(self, entity: Union[Entity, None], active=False) -> None:
        self.__selector.empty()
        if isinstance(entity, EntityEditor):
            self.__selector.add(entity)
            if active:
                self.__active = self.__moving = True

    @property
    def selected(self) -> Union[EntityEditor, None]:
        return self.__selector.sprite

    @property
    def moving(self) -> bool:
        return self.__moving
