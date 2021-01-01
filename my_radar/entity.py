# -*- coding: Utf-8 -*

import pygame
from typing import Union, Callable

class Entity(pygame.sprite.Sprite):

    __show_sprite = True
    __show_hitbox = True

    def __init__(self):
        super().__init__()
        self.__default_group = pygame.sprite.Group(self)

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

    def get_setup(self) -> list[float]:
        return list()

    def load_setup(self, line: list[float]) -> None:
        pass

    def __set_group(self, group: pygame.sprite.Group) -> None:
        self.__default_group.remove(self)
        self.__default_group = group
        self.__default_group.add(self)

    def revive(self, *groups) -> None:
        self.add(self.__default_group, *groups)

    group = property(lambda self: self.__default_group, __set_group)

class EntityEditorSelector(pygame.sprite.GroupSingle):
    pass

class EntityEditor(Entity):

    def on_click(self, mouse_pos: tuple[int, int]) -> bool:
        # pylint: disable=unused-argument
        return False

    def on_move(self, mouse_pos: tuple[int, int]) -> None:
        pass

    def on_key_press(self, key: int) -> bool:
        # pylint: disable=unused-argument
        return False

    @staticmethod
    def get_action_dict() -> dict[str, dict[str, str]]:
        return {str(): dict()}

    @property
    def selected(self) -> bool:
        return any(isinstance(group, EntityEditorSelector) for group in self.groups())

class EntityGroup(pygame.sprite.Group):

    def __init__(self, letter: str):
        super().__init__()
        self.__letter = letter

    def sprites(self) -> list[Union[Entity, EntityEditor]]:
        # pylint: disable=useless-super-delegation
        return super().sprites()

    def draw(self, surface: pygame.Surface) -> None:
        for entity in self.sprites():
            if isinstance(entity, EntityEditor) and entity.selected:
                continue
            entity.draw(surface)

    letter = property(lambda self: self.__letter)

class EntityEditorGroup(pygame.sprite.Group):

    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.__selected = None
        self.__selector = EntityEditorSelector()
        self.__history = EntityEditorHistory(self)
        self.__active = False
        self.__moving = False
        self.__modified = False

    def sprites(self) -> list[EntityEditor]:
        # pylint: disable=useless-super-delegation
        return super().sprites()

    def handle_mouse_event(self, event_type: int, mouse_pos: tuple[int, int]) -> None:
        if event_type == pygame.MOUSEBUTTONDOWN and self.selected is not None:
            if self.selected.on_click(mouse_pos):
                self.__active = True
        elif event_type == pygame.MOUSEBUTTONUP:
            self.__active = self.__moving = False
        elif event_type == pygame.MOUSEMOTION and self.__active:
            if not self.__moving:
                self.__history.action_modify(self.selected)
            self.__modified = self.__moving = True
            self.selected.on_move(mouse_pos)

    def handle_key_event(self, key: int, modifiers: int) -> None:
        if modifiers & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
            if key == pygame.K_z:
                self.history.undo()
            elif key == pygame.K_y:
                self.history.redo()
        elif self.selected is not None:
            setup = self.selected.get_setup()
            if self.selected.on_key_press(key):
                self.__modified = True
                self.history.action_modify(self.selected, setup=setup)

    def select(self, entity: Union[Entity, None], active=False) -> None:
        self.__selector.empty()
        if isinstance(entity, EntityEditor):
            self.__selector.add(entity)
            if active:
                self.__modified = self.__active = self.__moving = True

    def delete_selected_entity(self) -> None:
        if self.selected is not None:
            self.history.action_delete(self.selected)
            self.selected.kill()
            self.__modified = True

    @property
    def selected(self) -> Union[EntityEditor, None]:
        return self.__selector.sprite

    def modification_saved(self) -> None:
        self.__modified = False

    history = property(lambda self: self.__history)
    moving = property(lambda self: self.__moving)
    modified = property(lambda self: self.__modified)

class EntityEditorHistory:

    ACTION_ADD = "add"
    ACTION_MOD = "modify"
    ACTION_DEL = "delete"

    def __init__(self, group: EntityEditorGroup):
        self.__group = group
        self.__actions_undo = list[tuple[str, EntityEditor, tuple]]()
        self.__actions_redo = list[tuple[str, EntityEditor, tuple]]()
        self.__undo_dict = {
            self.ACTION_ADD: self.__exec_action_del,
            self.ACTION_MOD: self.__exec_action_mod,
            self.ACTION_DEL: self.__exec_action_add
        }
        self.__redo_dict = {
            self.ACTION_ADD: self.__exec_action_add,
            self.ACTION_MOD: self.__exec_action_mod,
            self.ACTION_DEL: self.__exec_action_del
        }
        self.__register_dict = {
            self.ACTION_ADD: self.__register_action_add,
            self.ACTION_MOD: self.__register_action_mod,
            self.ACTION_DEL: self.__register_action_del
        }

    def __register_action_undo(self, action_type: str, entity: EntityEditor, *additionnal_infos) -> None:
        self.__actions_undo.append((action_type, entity, additionnal_infos))

    def __register_action_redo(self, action_type: str, entity: EntityEditor, *additionnal_infos) -> None:
        self.__actions_redo.append((action_type, entity, additionnal_infos))

    def __register_action(self, action_type: str, entity: EntityEditor, *additionnal_infos) -> None:
        self.__register_action_undo(action_type, entity, *additionnal_infos)
        self.__actions_redo.clear()

    def action_add(self, entity: EntityEditor) -> None:
        self.__register_action_add(self.__register_action, entity)

    def action_modify(self, entity: EntityEditor, setup=None) -> None:
        self.__register_action_mod(self.__register_action, entity, setup=setup)

    def action_delete(self, entity: EntityEditor) -> None:
        self.__register_action_del(self.__register_action, entity)

    def __register_action_add(self, callback: Callable[[str, EntityEditor, tuple], None], entity: EntityEditor) -> None:
        callback(self.ACTION_ADD, entity)

    def __register_action_mod(self, callback: Callable[[str, EntityEditor, tuple], None], entity: EntityEditor, setup=None) -> None:
        callback(self.ACTION_MOD, entity, setup or entity.get_setup())

    def __register_action_del(self, callback: Callable[[str, EntityEditor, tuple], None], entity: EntityEditor) -> None:
        callback(self.ACTION_DEL, entity)

    def __exec_action_add(self, entity: EntityEditor) -> None:
        entity.revive(self.__group)
        self.__group.select(entity)

    def __exec_action_mod(self, entity: EntityEditor, line_setup: list[float]) -> None:
        entity.load_setup(line_setup)

    def __exec_action_del(self, entity: EntityEditor) -> None:
        entity.kill()

    def __action_to_do(self, history_action_type: str) -> None:
        history_actions = {
            "undo": [
                self.__actions_undo,
                self.__undo_dict,
                self.__register_action_redo,
            ],
            "redo": [
                self.__actions_redo,
                self.__redo_dict,
                self.__register_action_undo,
            ]
        }
        action_list, action_dict, register_callback = history_actions[history_action_type]
        if action_list:
            prev_action, entity, additionnal_infos = action_list.pop()
            self.__register_dict[prev_action](register_callback, entity)
            action_dict[prev_action](entity, *additionnal_infos)


    def undo(self) -> None:
        self.__action_to_do("undo")

    def redo(self) -> None:
        self.__action_to_do("redo")
