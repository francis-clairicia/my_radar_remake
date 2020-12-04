# -*- coding: Utf-8 -*

import sys
import time
import pygame
from .constants import BLACK, WHITE, IMG, FONT_DARK_CALIBRI
from .airplane import Airplane

class MyRadar:

    def __init__(self):
        status = pygame.init()
        if status[1] > 0:
            sys.exit("Error on pygame initialization ({} module{} failed to load)".format(status[1], "s" if status[1] > 1 else ""))
        self.screen = pygame.display.set_mode((1920, 1080), flags=pygame.RESIZABLE)
        pygame.display.set_caption("MyRadar Remake")

        self.clock = pygame.time.Clock()
        self.chrono = 0

        airplane_image = pygame.image.load(IMG["airplane"]).convert_alpha()
        # tower_image = pygame.image.load(IMG["tower"]).convert_alpha()
        world_map_image = pygame.image.load(IMG["world_map"]).convert_alpha()

        self.background = pygame.transform.smoothscale(world_map_image, self.screen.get_size())
        self.font = pygame.font.Font(FONT_DARK_CALIBRI, 45)

        self.airplanes = pygame.sprite.Group()
        self.hitboxes_airplane = pygame.sprite.Group()

        airplane = Airplane.from_script_setup(airplane_image, [1583, 682, 626, 737, 135, 0])
        self.airplanes.add(airplane)
        self.hitboxes_airplane.add(airplane.hitbox)

        self.show_hitbox = self.show_sprites = True

    @property
    def rect(self) -> pygame.Rect:
        return self.screen.get_rect()

    def start(self) -> None:
        loop = True
        start_time = time.time()
        while loop:
            self.clock.tick(120)
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
                        self.show_hitbox = not self.show_hitbox
                    if event.key == pygame.K_s:
                        self.show_sprites = not self.show_sprites
        pygame.quit()

    def draw_screen(self) -> None:
        self.screen.blit(self.background, self.background.get_rect())

        # Draw framerate
        text_framerate = self.font.render("{} FPS".format(int(self.clock.get_fps())), True, WHITE)
        self.screen.blit(text_framerate, text_framerate.get_rect(top=self.rect.top + 10, left=self.rect.left + 10))

        # Draw chrono
        text_chrono = self.font.render(time.strftime("%H:%M:%S", time.gmtime(self.chrono)), True, WHITE)
        self.screen.blit(text_chrono, text_chrono.get_rect(top=self.rect.top + 10, right=self.rect.right - 10))

        # Draw entites
        groups = [
            (self.airplanes, self.hitboxes_airplane)
        ]
        for sprite_group, outline_group in groups:
            sprite_group.update()
            outline_group.update()
            if self.show_sprites:
                sprite_group.draw(self.screen)
            if self.show_hitbox:
                outline_group.draw(self.screen)
