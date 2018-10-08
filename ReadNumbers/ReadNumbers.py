"""
Read Numbers game
v1---完成基本的游戏逻辑
    1, game start --- the start screen
        start button
    2, game playing --- the main game loop, init game data, deal with game logic
        show game board
        show time consuming
    3, game end --- the end screen, choose next operation
        show final time
        replay button
        quit button
        next button - not work currently
v1.2
    修正数字方块位置计算问题
    加入级别提升功能，状态栏显示级别
    调整字体大小
    将游戏结束画面从game playing中独立出来，形成start/playing/end三个独立阶段
"""

import pygame
from pygame.locals import *
import sys
import random
import time

# 窗口及方块尺寸
WINDOWWIDTH = 800
WINDOWHEIGHT = 600
STATUSHEIGHT = 80  # 状态栏高度，显示时间
GAMEMARGIN = 20  # 方块区距离状态栏距离


TEXTSIZE = 60  # 字体大小
BUTTONTEXTSIZE = 60

FPS = 30

# RGB
GRAY = (100, 100, 100)
LIGHTGRAY = (250, 250, 250)
NAVYBLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128,   0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)

BGCOLOR = WHITE  # 窗口背景色
LIGHTBOXCOLOR = NAVYBLUE  # 翻转的方块背景色
BOXCOLOR = WHITE  # 方块背景色
BOXBORDERCOLOR = BLACK
TEXTCOLOR = BLACK  # 文字颜色
BUTTONCOLOR = GRAY  # 方块边框颜色


def draw_button(text, centerx, centery):
    button_rect = Rect(0, 0, 250, 100)
    button_rect.center = (centerx, centery)
    draw_rect(button_rect, text, BUTTONTEXTSIZE, BGCOLOR, BUTTONCOLOR)
    return button_rect


def draw_start_screen():
    DISPLAYSURF.fill(BGCOLOR)
    # draw title
    font = pygame.font.Font(r".\sources\ArchitectsDaughter-Regular.ttf", 80)
    text_surf = font.render(u'Count The Numbers', True, RED)
    text_rect = text_surf.get_rect()
    text_rect.center = (400, 200)
    DISPLAYSURF.blit(text_surf, text_rect)
    # draw button
    start_rect = draw_button('START', 400, 400)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_s:
                return True
            elif event.type == MOUSEBUTTONDOWN:
                mousex, mousey = event.pos
                if start_rect.collidepoint(mousex, mousey):
                    return True
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def draw_end_screen(score):
    DISPLAYSURF.fill(BGCOLOR)
    replay_rect = draw_button('REPLAY', 400, 280)
    next_rect = draw_button('NEXT', 400, 400)
    quit_rect = draw_button('QUIT', 400, 520)
    font = pygame.font.Font(".\sources\ArchitectsDaughter-Regular.ttf", 40)
    text_surf = font.render('Your Score is:  '+str(score) + '   seconds.', True, BLUE)
    text_rect = text_surf.get_rect()
    text_rect.center = (400, 100)
    DISPLAYSURF.blit(text_surf, text_rect)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                mousex, mousey = event.pos
                if replay_rect.collidepoint(mousex, mousey):
                    return 'replay'
                elif next_rect.collidepoint(mousex, mousey):
                    return 'next'
                elif quit_rect.collidepoint(mousex, mousey):
                    return 'quit'
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def game_playing(level=1):
    # 初始化
    board_nums, board_colors, board_rects, begin_time, cur_num, win_num = init_game(level)
    mousex, mousey = 0, 0
    total_time = 0

    while True:  # main game loop
        mouse_clicked = False
        DISPLAYSURF.fill(BGCOLOR)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_clicked = True
                mousex, mousey = event.pos
        if mouse_clicked:
            # 检查点击正确方块
            for i, box in enumerate(board_rects):
                if box.collidepoint(mousex, mousey) and board_nums[i] == cur_num:
                    board_colors[i] = LIGHTBOXCOLOR
                    if cur_num == win_num:  # 判断是否获胜
                        return 'win', total_time
                    else:
                        cur_num += 1
        draw_gameboard(board_rects, board_colors, board_nums)
        total_time = draw_status(level, begin_time)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def init_game(level=1):
    """
    :param level: 游戏级别
    :return: nums, box_colors, box_rect: 游戏区域方块包含的数字，颜色，位置
            start_time: 本局游戏的开始时间
            start_number: 开始需要点击的方块数字
            numbers: 方块数量，用于判断胜利条件，是否全部点击
    """
    row = 2 + level // 3  # 纵向方块数量
    column = 2 + level - level // 3  # 横向方块数量
    totalboxsize = min(WINDOWWIDTH // column, (WINDOWHEIGHT - STATUSHEIGHT) // row)  # 方块加上周围MARGIN的尺寸
    boxmargin = int(totalboxsize * 0.1)  # 方块外围的MARGIN，是方块间距离的一半
    boxsize = totalboxsize - 2 * boxmargin  # 实际方块的尺寸
    boardwidth = 5  # 方块边框宽度

    margintop = STATUSHEIGHT + (WINDOWHEIGHT - STATUSHEIGHT - totalboxsize * row) // 2  # 方块区距离窗口上边的距离
    marginleft = (WINDOWWIDTH - totalboxsize * column) // 2  # 方块区距离窗口左边的距离

    numbers = column * row  # 方块数量

    nums = [i + 1 for i in range(numbers)]
    random.shuffle(nums)
    box_colors = [BOXCOLOR] * numbers  # 方块颜色
    box_rects = []  # 方块位置 Rect对象
    for i in range(numbers):
        box = Rect(marginleft + totalboxsize * (i % column) + boxmargin, margintop + totalboxsize * (i // column) + boxmargin, boxsize, boxsize)
        box_rects.append(box)
    start_time = time.time()
    start_number = 1
    return nums, box_colors, box_rects, start_time, start_number, numbers


def draw_status(level, begin_time):
    pygame.draw.rect(DISPLAYSURF, LIGHTGRAY, (0, 0, WINDOWWIDTH, STATUSHEIGHT))
    font = pygame.font.SysFont("", 60)
    level_surf = font.render('LEVLE {}'.format(level), True, RED)
    level_rect = level_surf.get_rect()
    level_rect.midleft = 20, STATUSHEIGHT // 2
    DISPLAYSURF.blit(level_surf, level_rect)
    return draw_time_consuming(begin_time)


def draw_time_consuming(begin_time):
    total_time = int(time.time() - begin_time)
    font = pygame.font.SysFont("", 60)
    time_surf = font.render("TIME: "+str(total_time), True, RED)
    time_rect = time_surf.get_rect()
    time_rect.midright = WINDOWWIDTH - 20, STATUSHEIGHT // 2
    DISPLAYSURF.blit(time_surf, time_rect)
    return total_time


def draw_gameboard(box_rects, box_colors, box_nums):
    for rect, bgcolor, num in zip(box_rects, box_colors, box_nums):
        draw_rect(rect, num, TEXTSIZE, bgcolor)


def draw_rect(box_rect, num, text_size, bgcolor, border_color=BOXBORDERCOLOR):
    pygame.draw.rect(DISPLAYSURF, border_color, box_rect, 5)
    pygame.draw.rect(DISPLAYSURF, bgcolor, box_rect.inflate(-5, -5))
    font = pygame.font.Font(".\sources\ArchitectsDaughter-Regular.ttf", text_size)
    text_surf = font.render(str(num), True, TEXTCOLOR)
    text_rect = text_surf.get_rect()
    text_rect.center = box_rect.center
    DISPLAYSURF.blit(text_surf, text_rect)


if __name__ == "__main__":
    global DISPLAYSURF, FPSCLOCK
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((800, 600))
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Read The Numbers!')

    # 开始画面
    draw_start_screen()
    level = 1  # 初始级别为1

    while True:
        # 游戏进行
        game_result, total_time = game_playing(level)
        # 结束画面，选择下一动作
        next_operation = draw_end_screen(total_time)
        if next_operation == 'replay':
            pass
        elif next_operation == 'next':
            level += 1
        elif next_operation == 'quit':
            pygame.quit()
sys.exit()