import pygame
from pygame.locals import *
import sys
import random

WINDOWWIDTH = 300
WINDOWHEIGHT = 400
PADDLEWIDTH = 60
PADDLEHEIGHT = 20
FRUITSIZE = 10

FPS = 60

PADDLECOLOR = (255, 0, 0)
FRUITCOLOR = (0, 0, 255)


class Paddle(pygame.sprite.Sprite):
    def __init__(self, window_width, window_height, width, height, color):
        pygame.sprite.Sprite.__init__(self)
        self.window_width = window_width
        self.window_height = window_height
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (window_width//2, window_height - 2*height)
        self.speed = 5
        self.moving = False
        self.direction = 0

    def start_moving(self):
        self.moving = True

    def stop_moving(self):
        self.moving = False

    def set_direction(self, direction):
        if direction == 'left':
            self.direction = -1
        elif direction == 'right':
            self.direction = 1

    def reset(self):
        self.rect.centerx = self.window_width // 2
        self.moving = False
        self.direction = 0

    def update(self):
        if self.moving:
            _cx = self.rect.centerx + self.direction * self.speed
            if _cx > self.window_width:
                _cx = self.window_width
            elif _cx < 0:
                _cx = 0
            self.rect.centerx = _cx

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Fruit(pygame.sprite.Sprite):
    def __init__(self, window_width, window_height, size, color):
        pygame.sprite.Sprite.__init__(self)
        self.window_width = window_width
        self.window_height = window_height
        self.speed = random.randint(1, 5)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        self.rect.center = (random.randint(0, self.window_width), 0)
        self.speed = random.randint(1, 5)

    def update(self):
        self.rect.centery = self.rect.centery + self.speed


class Catcher:
    def __init__(self, screen, window_width, window_height, width, height, color):
        self.screen = screen
        self.paddle = Paddle(window_width, window_height, width, height, color)
        self.fruits_group = pygame.sprite.Group()
        self.score = 0
        self.missed = 0

    def reset(self):
        self.paddle.reset()
        self.fruits_group.empty()
        self.score = 0
        self.missed = 0

    def _handle_event(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_d:
                self.paddle.start_moving()
                self.paddle.set_direction('right')
            elif event.type == KEYUP and event.key == K_d:
                self.paddle.stop_moving()
            elif event.type == KEYDOWN and event.key == K_a:
                self.paddle.start_moving()
                self.paddle.set_direction('left')
            elif event.type == KEYUP and event.key == K_a:
                self.paddle.stop_moving()

    def add_fruit(self):
        if len(self.fruits_group.sprites()) < 10:
            self.fruits_group.add(Fruit(WINDOWWIDTH, WINDOWHEIGHT, FRUITSIZE, FRUITCOLOR))

    def step(self):
        self._handle_event()
        # move the paddle and fruits
        self.fruits_group.update()
        self.paddle.update()
        # determine if paddle is collided with fruits
        collide_list = pygame.sprite.spritecollide(self.paddle, self.fruits_group, True)
        if collide_list:
            self.score += len(collide_list)
        # determine if fruits fall down
        for fruit in self.fruits_group.sprites():
            if fruit.rect.centery > WINDOWHEIGHT:
                fruit.reset()
                self.missed += 1

        self.screen.fill((0, 0, 0))
        self.fruits_group.draw(self.screen)
        self.paddle.draw(self.screen)

    def show_scores(self):
        font = pygame.font.SysFont('Arial', 16)
        score_surf = font.render("CATCH: "+str(self.score), True, (0, 255, 0))
        score_rect = score_surf.get_rect()
        score_rect.topleft = (40, 40)
        self.screen.blit(score_surf, score_rect)
        miss_surf = font.render("MISS: "+str(self.missed), True, (0, 255, 0))
        miss_rect = miss_surf.get_rect()
        miss_rect.topright = (WINDOWWIDTH-40, 40)
        self.screen.blit(miss_surf, miss_rect)


if __name__ == "__main__":
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Catcher')

    game = Catcher(DISPLAYSURF, WINDOWWIDTH, WINDOWHEIGHT, PADDLEWIDTH, PADDLEHEIGHT, PADDLECOLOR)
    generator = 0
    while True:
        if generator == 100:
            game.add_fruit()
            generator = 0
        else:
            generator += 1
        game.step()
        game.show_scores()
        pygame.display.update()
        FPSCLOCK.tick(FPS)
