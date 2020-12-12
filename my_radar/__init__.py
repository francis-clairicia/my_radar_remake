# -*- coding: Utf-8 -*
# pylint: disable=wrong-import-position

import sys
import time
import io

sys.stdout = io.StringIO()
import pygame
sys.stdout = sys.__stdout__

from .constants import BLACK, WHITE, IMG, FONT_DARK_CALIBRI
from .airplane import Airplane
from .tower import Tower
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
        self.airplanes_group = pygame.sprite.Group()
        for airplane_setup in parser.airplanes:
            self.airplanes_group.add(Airplane.from_script_setup(airplane_image, airplane_setup))
        self.airplanes_list = tuple[Airplane, ...](self.airplanes_group.sprites())

        # Load Towers
        self.towers_group = pygame.sprite.Group()
        for tower_setup in parser.towers:
            self.towers_group.add(Tower.from_script_setup(tower_image, tower_setup))
        self.towers_list = tuple[Tower, ...](self.towers_group.sprites())

    @property
    def rect(self) -> pygame.Rect:
        return self.screen.get_rect()

    def start(self) -> None:
        loop = True
        start_time = time.time()
        self.update(first=True)
        while loop:
            self.clock.tick(60)
            self.chrono = time.time() - start_time
            self.screen.fill(BLACK)
            self.draw_screen()
            pygame.display.update()
            for event in pygame.event.get():
                if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    loop = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l:
                        Airplane.show_hitbox(not Airplane.hitbox_shown())
                        Tower.show_hitbox(not Tower.hitbox_shown())
                    if event.key == pygame.K_s:
                        Airplane.show_sprite(not Airplane.sprite_shown())
                        Tower.show_sprite(not Tower.sprite_shown())
            self.update()
            if not self.airplanes_group:
                loop = False
        pygame.quit()

    def update(self, first=False) -> None:
        # Update airplanes' position
        self.airplanes_group.update()

        # Update towers' area control
        self.towers_group.update(self.airplanes_list)

        if first:
            return

        # Check for airplane collision
        for index, airplane in enumerate(self.airplanes_list):
            if not airplane.flying or airplane.in_a_tower_area:
                continue
            group = self.get_airplanes_group_for_collision(index, airplane)
            destroyed_airplane = pygame.sprite.spritecollideany(airplane, group, collided=pygame.sprite.collide_mask)
            if destroyed_airplane is not None:
                airplane.destroy()
                destroyed_airplane.destroy()

    def draw_screen(self) -> None:
        self.screen.blit(self.background, self.background.get_rect())

        # Draw framerate
        text_framerate = self.font.render("{} FPS".format(int(self.clock.get_fps())), True, WHITE)
        self.screen.blit(text_framerate, text_framerate.get_rect(top=self.rect.top + 10, left=self.rect.left + 10))

        # Draw chrono
        text_chrono = self.font.render(time.strftime("%H:%M:%S", time.gmtime(self.chrono)), True, WHITE)
        self.screen.blit(text_chrono, text_chrono.get_rect(top=self.rect.top + 10, right=self.rect.right - 10))

        # Draw entities
        for tower in self.towers_list:
            tower.draw(self.screen)
        for airplane in self.airplanes_list:
            airplane.draw(self.screen)

    def get_airplanes_group_for_collision(self, index: int, target: Airplane) -> pygame.sprite.Group:
        airplane_list = self.airplanes_list[index + 1:]
        return pygame.sprite.Group(filter(lambda airplane: airplane != target and airplane.flying, airplane_list))
