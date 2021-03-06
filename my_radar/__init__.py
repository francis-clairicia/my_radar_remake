# -*- coding: Utf-8 -*
# pylint: disable=wrong-import-position

import os.path
import sys
import time
import io
from typing import Union

sys.stdout = io.StringIO()
import pygame
sys.stdout = sys.__stdout__

from .constants import BLACK, WHITE, IMG, FONT_DARK_CALIBRI
from .camera import Camera
from .entity import Entity, EntityEditor, EntityEditorGroup
from .airplane import Airplane, AirplaneGroup, AirplaneEditor
from .tower import Tower, TowerGroup, TowerEditor
from .parser import ScriptParser
from .editor import EditorToolbox, EditorSideBoard, EditorActionFormatter

class MyRadar:

    def __init__(self, parser: ScriptParser, editor=False):
        status = pygame.init()
        if status[1] > 0:
            sys.exit("Error on pygame initialization ({} module{} failed to load)".format(status[1], "s" if status[1] > 1 else ""))
        self.screen = pygame.display.set_mode((1920, 1080), flags=pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)
        title = "MyRadar Remake"
        if editor:
            title = "{} - Editor | file: {}".format(title, os.path.basename(parser.filepath))
        pygame.display.set_caption(title)
        pygame.key.set_repeat(500, 50)

        # Show Loading message:
        self.screen.fill(BLACK)
        text_loading = pygame.font.SysFont("calibri", 50).render("Loading...", True, "white")
        self.screen.blit(text_loading, text_loading.get_rect(center=self.rect.center))
        pygame.display.flip()

        self.clock = pygame.time.Clock()
        self.chrono = 0

        airplane_image = pygame.image.load(IMG["airplane"]).convert_alpha()
        tower_image = pygame.image.load(IMG["tower"]).convert_alpha()
        world_map_image = pygame.image.load(IMG["world_map"]).convert_alpha()

        self.background = pygame.transform.smoothscale(world_map_image, self.screen.get_size())
        self.font = pygame.font.Font(FONT_DARK_CALIBRI, 45)

        alpha_threshold = 125
        self.white_mask = pygame.Surface(self.screen.get_size(), flags=pygame.SRCALPHA).convert_alpha()
        self.white_mask.fill(pygame.Color(255, 255, 255, alpha_threshold))
        self.black_mask = pygame.Surface(self.screen.get_size(), flags=pygame.SRCALPHA).convert_alpha()
        self.black_mask.fill(pygame.Color(0, 0, 0, alpha_threshold))

        self.parser = parser

        # Editor
        self.editor = editor
        self.entity_editor_grp = EntityEditorGroup()

        # Load Airplanes
        self.airplanes_group = AirplaneGroup()
        for airplane_setup in parser.airplanes:
            AirplaneType = Airplane if not self.editor else AirplaneEditor
            airplane = AirplaneType.from_script_setup(airplane_image, airplane_setup)
            airplane.group = self.airplanes_group
            if self.editor:
                airplane.add(self.entity_editor_grp)
        self.airplanes_list = self.airplanes_group.sprites().copy() if not self.editor else list[Airplane]()

        # Load Towers
        self.towers_group = TowerGroup()
        for tower_setup in parser.towers:
            TowerType = Tower if not self.editor else TowerEditor
            tower = TowerType.from_script_setup(tower_image, tower_setup, self.rect)
            tower.group = self.towers_group
            if self.editor:
                tower.add(self.entity_editor_grp)

        # Editor stuff
        action_formatter = EditorActionFormatter.from_entity_editor
        self.toolbox = EditorToolbox(airplane_image, tower_image, self.airplanes_group, self.towers_group)
        self.sideboard = EditorSideBoard(
            action_formatter(AirplaneEditor, select=True),
            action_formatter(TowerEditor, select=True)
        )
        self.show_editor_stuff = True

        # Camera
        self.camera = Camera(self.screen)

    @property
    def rect(self) -> pygame.Rect:
        return self.screen.get_rect()

    def start(self) -> None:
        loop = True
        simulation_running = not self.editor
        self.chrono = 0
        while loop:
            self.clock.tick(60)
            if simulation_running:
                self.chrono += self.clock.get_time() / 1000
                self.airplanes_group.update(self.chrono)
            self.draw_screen()
            pygame.display.update()
            for event in pygame.event.get():
                if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    loop = False
                    break
                if event.type == pygame.KEYDOWN and not self.editor:
                    if event.key == pygame.K_l:
                        Entity.show_hitbox(not Entity.hitbox_shown())
                    elif event.key == pygame.K_s:
                        Entity.show_sprite(not Entity.sprite_shown())
                    elif event.key == pygame.K_p:
                        simulation_running = not simulation_running
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.editor:
                    x, y = self.camera.map_cursor(event.pos)
                    for airplane in self.airplanes_group.sprites():
                        if airplane.rect.collidepoint(x, y):
                            self.camera.focus(airplane)
                            break
                if self.editor:
                    self.handle_editor_event(event)
                else:
                    self.camera.handle_event(event)
            if not self.editor and simulation_running:
                self.towers_group.update(self.airplanes_group.sprites())
                self.airplanes_group.check_collisions()
                if not self.airplanes_group:
                    self.show_results()
                    loop = False
        pygame.quit()

    def draw_screen(self) -> None:
        self.screen.blit(self.background, (0, 0))

        # Draw entities
        self.towers_group.draw(self.screen)
        self.airplanes_group.draw(self.screen)
        if self.editor:
            self.screen.blit(self.white_mask, (0, 0))
            if isinstance(self.entity_editor_grp.selected, Entity):
                self.entity_editor_grp.selected.draw(self.screen)

        # Set zoom scale
        self.camera.update()

        # Draw framerate
        text_framerate = self.font.render("{} FPS".format(int(self.clock.get_fps())), True, WHITE)
        if not self.editor:
            self.screen.blit(text_framerate, text_framerate.get_rect(top=self.rect.top + 10, left=self.rect.left + 10))
        else:
            self.screen.blit(text_framerate, text_framerate.get_rect(bottom=self.rect.bottom - 10, right=self.rect.right - 10))

        if not self.editor:
            # Draw chrono
            text_chrono = self.font.render(time.strftime("%H:%M:%S", time.gmtime(self.chrono)), True, WHITE)
            self.screen.blit(text_chrono, text_chrono.get_rect(top=self.rect.top + 10, right=self.rect.right - 10))
        elif self.show_editor_stuff and not self.entity_editor_grp.moving:
            self.toolbox.draw(self.screen)
            text_script_filepath = "File: {}".format(os.path.basename(self.parser.filepath))
            if self.entity_editor_grp.modified:
                text_script_filepath += " - Modified"
            text_script_filepath = self.font.render(text_script_filepath, True, "black")
            w, h = text_script_filepath.get_size()
            box_rect = pygame.Surface((w + 20, h + 20)).get_rect(left=self.rect.left + 20, bottom=self.rect.bottom - 20)
            pygame.draw.rect(self.screen, "white", box_rect)
            pygame.draw.rect(self.screen, "black", box_rect, width=2)
            self.screen.blit(text_script_filepath, text_script_filepath.get_rect(center=box_rect.center))
            if self.sideboard.is_shown():
                self.screen.blit(self.black_mask, (0, 0))
            self.sideboard.draw(self.screen)

    def show_results(self) -> None:
        land_on = 0
        destroyed = 0
        for airplane in self.airplanes_list:
            land_on += int(airplane.land_on)
            destroyed += int(airplane.destroyed)
        print("Simulation time:", time.strftime("%Hh%Mm%Ss", time.gmtime(self.chrono)))
        print("Airplanes landed on:", land_on)
        print("Airplanes destroyed:", destroyed)

    def handle_editor_event(self, event: pygame.event.Event) -> None:
        if not self.camera.moving and not self.entity_editor_grp.moving:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F12:
                    self.show_editor_stuff = not self.show_editor_stuff
                elif event.key == pygame.K_DELETE:
                    self.entity_editor_grp.delete_selected_entity()
                elif event.key == pygame.K_s and event.mod & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
                    self.save_setup()
                self.entity_editor_grp.handle_key_event(event.key, event.mod)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if not self.toolbox.is_shown() and not self.sideboard.is_shown():
                    x, y = self.camera.map_cursor(event.pos)
                    previous = self.entity_editor_grp.selected
                    self.entity_editor_grp.select(None)
                    for entity in self.entity_editor_grp.sprites():
                        if entity.rect.collidepoint(x, y):
                            if entity is previous:
                                continue
                            self.entity_editor_grp.select(entity)
                            break
        if self.show_editor_stuff and not self.entity_editor_grp.moving:
            if not self.sideboard.is_shown():
                self.toolbox.handle_event(event, self.entity_editor_grp, self.rect)
            if not self.toolbox.is_shown():
                self.sideboard.handle_event(event, self.entity_editor_grp, self.rect)
        if not self.entity_editor_grp.moving and not self.sideboard.is_shown() and not self.toolbox.is_shown():
            self.camera.handle_event(event)
        else:
            self.camera.stop_move()
        if (event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP] and event.button == 1) or event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.entity_editor_grp.handle_mouse_event(event.type, self.camera.map_cursor(pygame.mouse.get_pos()))

    def save_setup(self) -> None:
        self.parser.update(self.airplanes_group, self.towers_group)
        if self.parser.save_in_file():
            self.entity_editor_grp.modification_saved()
