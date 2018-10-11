import sys
import pygame
import random
from pygame.locals import *
from itertools import cycle

FPS = 30
SCREENWIDTH = 288
SCREENHEIGHT = 512

PIPEGAPSIZE = 100
BASEY = 0.79 * SCREENHEIGHT

IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        'res/images/redbird-upflap.png',
        'res/images/redbird-midflap.png',
        'res/images/redbird-downflap.png',
    ),
    # blue bird
    (
        'res/images/bluebird-upflap.png',
        'res/images/bluebird-midflap.png',
        'res/images/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'res/images/yellowbird-upflap.png',
        'res/images/yellowbird-midflap.png',
        'res/images/yellowbird-downflap.png',
    ),
)
# list of backgrounds
BACKGROUNDS_LIST = (
    'res/images/background-day.png',
    'res/images/background-night.png',
)
# list of pipes
PIPES_LIST = (
    'res/images/pipe-green.png',
    'res/images/pipe-red.png',
)


class Bird(pygame.sprite.Sprite):
    def __init__(self, images, x, y):
        pygame.sprite.Sprite.__init__(self)
        self._img_list = images
        self._img_index = 0
        self._img_index_gen = cycle([0, 1, 2, 1])
        self._loop_iter = 0
        self.image = self._img_list[self._img_index]
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.mask = pygame.mask.from_surface(self.image)

        self._hover_vals = {'val': 0, 'dir': 1}

        self.velocity_y = -9  # 速度 只有y方向
        self.max_vel_y = 10  # 最大速度
        self.min_vel_y = -8  # 最低速度
        self.acceleration_y = 1  # 向下加速度
        self.rotation = 45  # 角度
        self.vel_rotate = 3  # 转动速度
        self.rotation_threshold = 20  # 角度显示门限
        self.flap_acceleration = -9  # 拍动加速度,即拍动后的速度
        self.flapped = False  # 是否拍动

    def hover(self):
        '''停在空中 上下移动'''
        if abs(self._hover_vals['val']) == 8:
            self._hover_vals['dir'] *= -1
        self._hover_vals['val'] += self._hover_vals['dir']
        self.rect.top += self._hover_vals['dir']

    def draw(self, surface, flying=False):
        if (self._loop_iter+1) % 5 == 0:
            self._img_index = next(self._img_index_gen)
            self.image = self._img_list[self._img_index]
            self.mask = pygame.mask.from_surface(self.image)
        self._loop_iter = (self._loop_iter + 1) % 30
        if not flying:
            surface.blit(self.image, self.rect)
        else:
            visible_rot = min(self.rotation, self.rotation_threshold)
            show_image = pygame.transform.rotate(self.image, visible_rot)
            surface.blit(show_image, self.rect)

    def flap_once(self):
        self.velocity_y = self.flap_acceleration
        self.rotation = 45

    def crash(self):
        # 碰撞后加速下落
        self.acceleration_y = 2
        self.vel_rotate = 7
        self.max_vel_y = 15

    def on_ground(self):
        if self.rect.top + self.rect.height >= BASEY - 1:
            return True
        return False

    def update(self):
        if not self.on_ground() and self.rotation > -90:
            self.rotation -= self.vel_rotate
        if self.velocity_y < self.max_vel_y:
            self.velocity_y += self.acceleration_y
        if self.rect.top + self.rect.height < BASEY - 1:
            self.rect.top += min(self.velocity_y, BASEY - self.rect.top - self.rect.height)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.mask = pygame.mask.from_surface(self.image)
        self.velocity = -4

    def update(self):
        self.rect.left += self.velocity


def main():
    global FPSCLOCK, SCREEN
    # init pygame
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption("Flappy Bird")
    icon = pygame.image.load('flappy.ico').convert_alpha()
    pygame.display.set_icon(icon)

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('res/images/0.png').convert_alpha(),
        pygame.image.load('res/images/1.png').convert_alpha(),
        pygame.image.load('res/images/2.png').convert_alpha(),
        pygame.image.load('res/images/3.png').convert_alpha(),
        pygame.image.load('res/images/4.png').convert_alpha(),
        pygame.image.load('res/images/5.png').convert_alpha(),
        pygame.image.load('res/images/6.png').convert_alpha(),
        pygame.image.load('res/images/7.png').convert_alpha(),
        pygame.image.load('res/images/8.png').convert_alpha(),
        pygame.image.load('res/images/9.png').convert_alpha()
    )
    # game over sprite
    IMAGES['gameover'] = pygame.image.load('res/images/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('res/images/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('res/images/base.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die'] = pygame.mixer.Sound('res/audio/die' + soundExt)
    SOUNDS['hit'] = pygame.mixer.Sound('res/audio/hit' + soundExt)
    SOUNDS['point'] = pygame.mixer.Sound('res/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('res/audio/swoosh' + soundExt)
    SOUNDS['wing'] = pygame.mixer.Sound('res/audio/wing' + soundExt)

    while True:
        # 选择背景
        randBg = random.randint(0, len(BACKGROUNDS_LIST)-1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()
        # 随机选择小鸟图案
        randPlayer = random.randint(0, len(PLAYERS_LIST)-1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )
        # 小鸟的初始位置
        playerx = int(SCREENWIDTH * 0.2)
        playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)
        player = Bird(IMAGES['player'], playerx, playery)

        # 随机选择柱子图案
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hit mask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # hit mask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )

        # show welcome screen
        movement_info = show_welcome_animation(player)

        # main game loop
        crash_info = main_game(movement_info, player)

        # game over screen
        showGameOverScreen(crash_info, player)


def show_welcome_animation(player):
    # 欢迎消息的位置
    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    # base的初始位置及可以向左移动的最大距离
    basex = 0
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                # start game, quit welcome screen
                SOUNDS['wing'].play()
                return {'basex': basex}

        # adjust basex
        basex = -((-basex + 4) % baseShift)  # base向左移动4
        # 小鸟上下飞动
        player.hover()

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))
        player.draw(SCREEN)
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def main_game(movement_info, player):
    score = 0
    basex = movement_info['basex']
    base_shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    upper_pipes_group = pygame.sprite.Group()
    lower_pipes_group = pygame.sprite.Group()

    # get 2 new pipes to add to upperPipes lowerPipes list
    get_random_pipes(upper_pipes_group, lower_pipes_group, SCREENWIDTH + 200)
    get_random_pipes(upper_pipes_group, lower_pipes_group, SCREENWIDTH + 200 + SCREENWIDTH // 2)


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if player.rect.y > -2 * IMAGES['player'][0].get_height():
                    player.flap_once()
                    SOUNDS['wing'].play()

        # check for crash
        crashTest = check_crash(player, upper_pipes_group, lower_pipes_group)
        if crashTest[0]:
            player.crash()
            return {
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upper_pipes_group,
                'lowerPipes': lower_pipes_group,
                'score': score,
            }

        # check for scores, 再pipe中点及之后4个距离内加1分，4应该是移动的速度
        playerMidPos = player.rect.x + IMAGES['player'][0].get_width() / 2
        for pipe in upper_pipes_group:
            pipeMidPos = pipe.rect.x + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                SOUNDS['point'].play()

        basex = -((-basex + 100) % base_shift)

        # move pipes to left

        # add new pipe when first pipe is about to touch left of screen
        upper_pipes_list = upper_pipes_group.sprites()
        if 0 < upper_pipes_list[0].rect.left < 5:
            get_random_pipes(upper_pipes_group, lower_pipes_group, SCREENWIDTH + 10)

        # remove first pipe if its out of the screen
        upper_pipes_list = upper_pipes_group.sprites()
        lower_pipes_list = lower_pipes_group.sprites()
        if upper_pipes_list[0].rect.left < -IMAGES['pipe'][0].get_width():
            upper_pipes_list[0].remove(upper_pipes_group)
            lower_pipes_list[0].remove(lower_pipes_group)

        player.update()
        upper_pipes_group.update()
        lower_pipes_group.update()

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))

        upper_pipes_group.draw(SCREEN)
        lower_pipes_group.draw(SCREEN)

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        showScore(score)

        player.draw(SCREEN, True)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0  # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def showGameOverScreen(crashInfo, player):
    """crashes the player down and shows gameover image"""
    score = crashInfo['score']
    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die sounds
    SOUNDS['hit'].play()
    if not crashInfo['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player.on_ground():
                    return

        player.update()

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))

        upperPipes.draw(SCREEN)
        lowerPipes.draw(SCREEN)

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        player.draw(SCREEN)

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def get_random_pipes(upper_group, lower_group, posx):
    """returns a randomly generated upper and lower pipes"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()

    Pipe(IMAGES['pipe'][0], posx, gapY - pipeHeight).add(upper_group)  # upper pipe
    Pipe(IMAGES['pipe'][1], posx, gapY + PIPEGAPSIZE).add(lower_group)  # lower pipe


def check_crash(player, upper_pipes, lower_pipes):
    if player.rect.y + player.rect.height >= BASEY - 1:
        return [True, True]
    else:
        for pipe in upper_pipes:
            if pygame.sprite.collide_mask(player, pipe):
                return [True, False]
        for pipe in lower_pipes:
            if pygame.sprite.collide_mask(player, pipe):
                return [True, False]
    return [False, False]



def check_crash_old(player, upper_pipes, lower_pipes):
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:
        player_rect = pygame.Rect(player['x'], player['y'], player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upper_pipes, lower_pipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(player_rect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(player_rect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False


def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


if __name__ == "__main__":
    main()
