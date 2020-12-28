# -*- coding: Utf-8 -*
# pylint: disable=wrong-import-position

import sys
import time
import io
from typing import Union

sys.stdout = io.StringIO()
import pygame
sys.stdout = sys.__stdout__

from .constants import BLACK, WHITE, IMG, FONT_DARK_CALIBRI
from .entity import Entity
from .airplane import Airplane, AirplaneGroup
from .tower import Tower, TowerGroup
from .parser import ScriptParser

class MyRadar:

    def __init__(self, parser: ScriptParser):
        status = pygame.init()
        if status[1] > 0:
            sys.exit("Error on pygame initialization ({} module{} failed to load)".format(status[1], "s" if status[1] > 1 else ""))
        self.screen = pygame.display.set_mode((1920, 1080), flags=pygame.RESIZABLE)
        pygame.display.set_caption("MyRadar Remake")

        # Show Loading message:
        self.screen.fill("black")
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

        # Load Airplanes
        self.airplanes_group = AirplaneGroup()
        for airplane_setup in parser.airplanes:
            self.airplanes_group.add(Airplane.from_script_setup(airplane_image, airplane_setup))
        self.airplanes_list = self.airplanes_group.sprites().copy()

        # Load Towers
        self.towers_group = TowerGroup()
        for tower_setup in parser.towers:
            self.towers_group.add(Tower.from_script_setup(tower_image, tower_setup))

        # Camera
        self.camera = Camera(self.screen)

    @property
    def rect(self) -> pygame.Rect:
        return self.screen.get_rect()

    def start(self) -> None:
        loop = True
        simulation_running = True
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l:
                        Entity.show_hitbox(not Entity.hitbox_shown())
                    if event.key == pygame.K_s:
                        Entity.show_sprite(not Entity.sprite_shown())
                    if event.key == pygame.K_p:
                        simulation_running = not simulation_running
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = self.camera.map_cursor(event.pos)
                    for airplane in self.airplanes_group:
                        if airplane.rect.collidepoint(x, y):
                            self.camera.focus(airplane)
                            break
                self.camera.handle_event(event)
            if simulation_running:
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

        # Set zoom scale
        self.camera.update()

        # Draw framerate
        text_framerate = self.font.render("{} FPS".format(int(self.clock.get_fps())), True, WHITE)
        self.screen.blit(text_framerate, text_framerate.get_rect(top=self.rect.top + 10, left=self.rect.left + 10))

        # Draw chrono
        text_chrono = self.font.render(time.strftime("%H:%M:%S", time.gmtime(self.chrono)), True, WHITE)
        self.screen.blit(text_chrono, text_chrono.get_rect(top=self.rect.top + 10, right=self.rect.right - 10))

    def show_results(self) -> None:
        land_on = 0
        destroyed = 0
        for airplane in self.airplanes_list:
            land_on += int(airplane.land_on)
            destroyed += int(airplane.destroyed)
        print("Simulation time:", time.strftime("%Hh%Mm%Ss", time.gmtime(self.chrono)))
        print("Airplanes landed on:", land_on)
        print("Airplanes destroyed:", destroyed)

class Camera:

    def __init__(self, screen: pygame.Surface):
        self.__screen = self.__surface = screen
        self.__scale = 1
        self.__rect = self.__screen.get_rect()
        self.__airplane = None
        self.__moving = False
        self.__previous_infos = dict()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEWHEEL:
            self.__scale -= (event.y) / 10
            self.__scale = max(self.__scale, 0.1)
            self.__scale = min(self.__scale, 1)
            self.__update_rect()
        elif event.type == pygame.MOUSEMOTION and event.buttons[0] and not isinstance(self.__airplane, Airplane):
            self.__moving = True
            x, y = event.rel
            self.__rect.move_ip(-x * self.__scale, -y * self.__scale)
            self.__update_rect()

    def focus(self, airplane: Union[Airplane, None]) -> None:
        if isinstance(airplane, Airplane):
            if not isinstance(self.__airplane, Airplane):
                self.__previous_infos["scale"] = self.__scale
                self.__previous_infos["rect"] = self.__rect
                self.__scale = 0.3
            self.__airplane = airplane
        else:
            self.__airplane = None
            if self.__previous_infos:
                self.__scale = self.__previous_infos["scale"]
                self.__rect = self.__previous_infos["rect"]
            self.__previous_infos.clear()
        self.__update_rect()

    def __update_rect(self) -> None:
        screen_rect = self.__screen.get_rect()
        if self.__scale == 1:
            self.__rect = screen_rect
        else:
            center = self.__rect.center
            self.__rect.size = (screen_rect.w * self.__scale, screen_rect.h * self.__scale)
            self.__rect.center = center
            self.__rect.left = max(self.__rect.left, screen_rect.left)
            self.__rect.right = min(self.__rect.right, screen_rect.right)
            self.__rect.top = max(self.__rect.top, screen_rect.top)
            self.__rect.bottom = min(self.__rect.bottom, screen_rect.bottom)
        self.__surface = self.__screen.subsurface(self.__rect)

    def update(self) -> None:
        if isinstance(self.__airplane, Airplane):
            if self.__airplane.alive():
                self.__rect.center = self.__airplane.rect.center
                self.__update_rect()
            else:
                self.focus(None)
        self.__screen.blit(pygame.transform.smoothscale(self.__surface, self.__screen.get_size()), (0, 0))

    def map_cursor(self, cursor_pos: tuple[int, int]) -> tuple[int, int]:
        return round(self.__scale * cursor_pos[0]) + self.__rect.left, round(self.__scale * cursor_pos[1]) + self.__rect.top
