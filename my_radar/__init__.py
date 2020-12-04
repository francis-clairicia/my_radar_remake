# -*- coding: Utf-8 -*

import sys
import pygame
from .constants import BLACK, WHITE, IMG, FONT_DARK_CALIBRI

class MyRadar:

    def __init__(self):
        status = pygame.init()
        if status[1] > 0:
            sys.exit("Error on pygame initialization ({} module{} failed to load)".format(status[1], "s" if status[1] > 1 else ""))
        self.screen = pygame.display.set_mode((1920, 1080), flags=pygame.RESIZABLE)
        pygame.display.set_caption("MyRadar Remake")

        self.clock = pygame.time.Clock()

        self.airplane_image = pygame.image.load(IMG["airplane"]).convert_alpha()
        self.tower_image = pygame.image.load(IMG["tower"]).convert_alpha()
        self.world_map_image = pygame.image.load(IMG["world_map"]).convert_alpha()

        self.background = pygame.transform.smoothscale(self.world_map_image, self.screen.get_size())
        self.font = pygame.font.Font(FONT_DARK_CALIBRI, 40)

    @property
    def rect(self) -> pygame.Rect:
        return self.screen.get_rect()

    def start(self) -> None:
        loop = True
        while loop:
            self.clock.tick(60)
            self.screen.fill(BLACK)
            self.draw_screen()
            pygame.display.update()
            for event in pygame.event.get():
                if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    loop = False
                    break
        pygame.quit()

    def draw_screen(self) -> None:
        self.screen.blit(self.background, self.background.get_rect())
        text_framerate = self.font.render("{} FPS".format(int(self.clock.get_fps())), True, WHITE)
        self.screen.blit(text_framerate, text_framerate.get_rect(top=self.rect.top + 10, left=self.rect.left + 10))