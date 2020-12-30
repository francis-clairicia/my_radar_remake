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

    @property
    def selected(self) -> bool:
        return any(isinstance(group, EntityEditorSelector) for group in self.groups())

class EntityEditorGroup(pygame.sprite.Group):

    def __init__(self, *sprites, alpha_threshold=255):
        super().__init__(*sprites)
        self.__selected = None
        self.__selector = EntityEditorSelector()
        self.__alpha_threshold = int(alpha_threshold)

    def sprites(self) -> list[EntityEditor]:
        # pylint: disable=useless-super-delegation
        return super().sprites()

    def select(self, entity: Union[Entity, None]) -> None:
        if isinstance(self.__selected, EntityEditor):
            self.selected.set_alpha(255)
        self.__selector.empty()
        if isinstance(entity, EntityEditor):
            self.__selector.add(entity)
            entity.set_alpha(self.__alpha_threshold)

    @property
    def selected(self) -> Union[EntityEditor, None]:
        return self.__selector.sprite
