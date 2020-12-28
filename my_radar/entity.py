# -*- coding: Utf-8 -*

import pygame

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
