'''
Ezio416 fork of "Minesweeper but you can't lose" by Thebrowndot
Forked:   2022-08-18
Modified: 2022-08-20
'''
import numpy as np
import random
import time

import pygame
from pygame import mixer

play_sound = False

pygame.init()
pygame.display.set_caption('Minesweeper')
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)
mine_img = pygame.image.load('mine.png')
font = pygame.font.Font('freesansbold.ttf', 29)
flag_img = pygame.image.load('flag.png')
WINDOW_WIDTH, WINDOW_HEIGHT = 900, 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

array = []
board_config = np.zeros([16, 30], dtype=int)
cell_status = np.zeros([30, 16], dtype=int)
flag = 0
flag_map = np.zeros([30, 16], dtype=int)
is_chord = False
is_clock = False
is_gameover = False
is_mouse = 0
is_right_mouse = False
no_mine_array = []
start_time = 0
total_mines = 99
flag_count = total_mines

def blowup(x, y):
    global flag
    global is_clock
    global is_gameover
    place_mine()
    screen.blit(mine_img, (x, y))
    flag = 10
    is_clock = True
    is_gameover = True
    if play_sound:
        mixer.Sound('blast.wav').play()

def board_update():
    global board_config
    for a in range(1, 31):
        for b in range(1, 17):
            if cell_status[a - 1, b - 1]:
                mine_check(a, b)
                board_config[b - 1, a - 1] = flag
                if flag:
                    mine_render((a - 1) * 30, (b - 1) * 30 + 120)
                else:
                    draw_rect(a - 1, b - 1)

def chording_helper(tuple0, tuple1) -> None:
    global cell_status
    if not (flag_map[tuple0] or tuple1 in array):
        mine_check(*tuple1)
        if not flag:
            draw_rect(*tuple0)
            cell_status[tuple0] = 1
            floodfill(*tuple1)
        else:
            mine_render(tuple0[0] * 30, tuple0[1] * 30 + 120)
            cell_status[tuple0] = 1
    if not flag_map[tuple0] and tuple1 in array:
        cell_status[tuple0] = 1
        mine_shift(*tuple1)
        #blowup(tuple0[0] * 30, tuple0[1] * 30 + 120)

def chording(a, b) -> None:
    flag1 = 0
    if a > 1 and b > 1:
        flag1 += 1 if flag_map[a - 2, b - 2] else 0
    if a > 1 and b < 16:
        flag1 += 1 if flag_map[a - 2, b] else 0
    if a < 30 and b < 16:
        flag1 += 1 if flag_map[a, b] else 0
    if a < 30 and b > 1:
        flag1 += 1 if flag_map[a, b - 2] else 0
    if b > 1:
        flag1 += 1 if flag_map[a - 1, b - 2] else 0
    if b < 16:
        flag1 += 1 if flag_map[a - 1, b] else 0
    if a < 30:
        flag1 += 1 if flag_map[a, b - 1] else 0
    if a > 1:
        flag1 += 1 if flag_map[a - 2, b - 1] else 0
    mine_check(a, b)
    if flag1 == flag:
        if a > 1 and b > 1:
            chording_helper((a - 2, b - 2), (a - 1, b - 1))
        if a > 1:
            chording_helper((a - 2, b - 1), (a - 1, b))
        if b < 16:
            chording_helper((a - 1, b), (a, b + 1))
        if a < 30 and b < 16:
            chording_helper((a, b), (a + 1, b + 1))
        if a < 30:
            chording_helper((a, b - 1), (a + 1, b))
        if b > 1:
            chording_helper((a - 1, b - 2), (a, b - 1))
        if a > 1 and b < 16:
            chording_helper((a - 2, b), (a - 1, b + 1))
        if a < 30 and b > 1:
            chording_helper((a, b - 2), (a + 1, b - 1))
        if play_sound:
            mixer.Sound('chord.wav').play()

def clock():
    global is_clock
    if np.sum(cell_status) >= 381:
        is_clock = True
    if not is_clock:
        pygame.draw.rect(screen, [210, 210, 210], [428, 50, 57, 28])
        pygame.draw.rect(screen, [0, 0, 0], [428, 50, 57, 28], 2)
        screen.blit(font.render(str('%03d'%(time.time() - start_time)), True, (255, 0, 0)), (430, 50))

def draw_grid() -> None:
    blockSize = 30
    for x in range(0, WINDOW_WIDTH, blockSize):
        for y in range(120, WINDOW_HEIGHT, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)

def draw_rect(a, b) -> None:
    pygame.draw.rect(screen, [180] * 3, [a * 30, b * 30 + 120, 28, 28])

def floodfill_helper(tuple0, tuple1) -> None:
    global cell_status
    mine_check(*tuple0)
    if not flag and not cell_status[tuple1] and not flag_map[tuple1]:
        draw_rect(*tuple1)
        cell_status[tuple1] = 1
        floodfill(*tuple0)
    if flag and not cell_status[tuple1] and not flag_map[tuple1]:
        mine_render(tuple1[0] * 30, tuple1[1] * 30 + 120)
        cell_status[tuple1] = 1

def floodfill(a, b) -> None:
    if a + 1 <= 30 and b >= 1 and a + 1 >= 1 and b <= 16:
        floodfill_helper((a + 1, b), (a, b - 1))
    if a >= 1 and a <= 30 and b + 1 >= 1 and b + 1 <= 16:
        floodfill_helper((a, b + 1), (a - 1, b))
    if a + 1 >= 1 and a + 1 <= 30 and b + 1 >= 1 and b + 1 <= 16:
        floodfill_helper((a + 1, b + 1), (a, b))
    if a + 1 >= 1 and a + 1 <= 30 and b - 1 >= 1 and b - 1 <= 16:
        floodfill_helper((a + 1, b - 1), (a, b - 2))
    if a - 1 >= 1 and a - 1 <= 30 and b >= 1 and b <= 16:
        floodfill_helper((a - 1, b), (a - 2, b - 1))
    if a >= 1 and a <= 30 and b - 1 >= 1 and b - 1 <= 16:
        floodfill_helper((a, b - 1), (a - 1, b - 2))
    if a - 1 >= 1 and a - 1 <= 30 and b - 1 >= 1 and b - 1 <= 16:
        floodfill_helper((a - 1, b - 1), (a - 2, b - 2))
    if a - 1 >= 1 and a - 1 <= 30 and b + 1 >= 1 and b + 1 <= 16:
        floodfill_helper((a - 1, b + 1), (a - 2, b))

def game():
    global array, flag, flag_count, is_chord, is_gameover, is_clock, is_mouse, mouse_pos, no_mine_array
    a = 0
    blockSize = 30
    for x in range(0, WINDOW_WIDTH, blockSize):
        a += 1
        b = 0
        for y in range(120, WINDOW_HEIGHT, blockSize):
            flag = 0
            b += 1
            if x <= mouse_pos[0] <= x + blockSize and y <= mouse_pos[1] <= y + blockSize:
                if is_mouse == 1:
                    is_mouse += 1
                    place_mine()
                    no_mine_array = [(a - 1, b + 1), (a, b + 1), (a + 1, b + 1), (a - 1, b),
                                     (a, b), (a + 1, b), (a - 1, b - 1), (a, b - 1), (a + 1, b - 1)]
                two_right_click = False
                if is_right_mouse and flag_map[a - 1, b - 1] and not is_chord:
                    if play_sound:
                        mixer.Sound('flag.wav').play()
                    pygame.draw.rect(screen, [210] * 3, [x, y + 1, 28, 28])
                    flag_count += 1
                    flag_map[a - 1, b - 1] = 0
                    two_right_click = True
                if is_right_mouse and not any([cell_status[a - 1, b - 1], flag_map[a - 1, b - 1], is_chord, two_right_click]):
                    if play_sound:
                        mixer.Sound('flag.wav').play()
                    screen.blit(flag_img, (x, y))
                    flag_map[a - 1, b - 1] = 1
                    flag_count -= 1
                if not any([cell_status[a - 1, b - 1], flag_map[a - 1, b - 1], is_chord, is_right_mouse]):
                    if (a, b) in array:
                        cell_status[a - 1, b - 1] = 1
                        mine_shift(a, b)
                        #blowup(x, y)
                    else:
                        mine_check(a, b)
                        if flag and flag != 10:
                            if not cell_status[a - 1, b - 1] and play_sound:
                                mixer.Sound('click.wav').play()
                            mine_render(x, y)
                            cell_status[a - 1, b - 1] = 1
                        if not flag:
                            if not cell_status[a - 1, b - 1] and play_sound:
                                mixer.Sound('empty_cell.wav').play()
                            pygame.draw.rect(screen, [180] * 3, [(a - 1) * 30, (b - 1) * 30 + 120, 28, 28])
                            cell_status[a - 1, b - 1] = 1
                            floodfill(a, b)
                if is_chord and not flag_map[a - 1, b - 1]:
                    chording(a, b)
                    is_chord = False
                mouse_pos = (0, 0)
            pygame.draw.rect(screen, [210] * 3,[420, 10, 73, 30])
            pygame.draw.rect(screen, [0] * 3, [420, 10, 73, 30], 2)
            screen.blit(flag_img, (420, 10))
            screen.blit(font.render(str(flag_count), True, (0, 0, 0)), (455, 11))

def game_over():
    if is_gameover:
        screen.blit(font.render('GAME OVER', True, (0, 0, 0)), (360, 85))
    else:
        screen.blit(font.render('YOU WIN', True, (0, 0, 0)), (390, 85))
        if play_sound:
            mixer.Sound('win.wav').play()

def mine_check(a, b) -> None:
    global flag
    flag = 0
    tuples = [(a - 1, b - 1), (a - 1, b + 1), (a + 1, b + 1), (a + 1, b - 1),
              (a, b - 1), (a, b + 1), (a + 1, b), (a - 1, b)]
    for tuple_ in tuples:
        flag += 1 if tuple_ in array else 0

def mine_render(x, y):
    tuples = [(0, 0, 255), (0, 102, 51), (255, 0, 0), (0, 0, 102),
              (102, 51, 0), (0, 153, 153), (0, 0, 0), (160, 160, 160)]
    for i, tuple_ in enumerate(tuples, 1):
        if flag == i:
            pygame.draw.rect(screen, [180] * 3, [x, y, 28, 28])
            screen.blit(font.render(str(flag), True, tuple_), (x + 7.5, y))

def mine_shift(a, b) -> None:
    global array
    array.remove((a, b))
    (mine_x, mine_y) = random_pos()
    while cell_status[mine_x - 1, mine_y - 1] or (mine_x, mine_y) in array:
        (mine_x, mine_y) = random_pos()
    array.append((mine_x, mine_y))

def place_mine() -> None:
    global array
    for i in range(total_mines):
        xytuple = random_pos()
        new_array = no_mine_array + array if i else no_mine_array
        while xytuple in new_array:
            xytuple = random_pos()
        array.append(xytuple)

def random_pos():
    return (random.randint(1, 30), random.randint(1, 16))

def main():
    global is_chord, is_gameover, is_mouse, is_right_mouse, mouse_pos, start_time
    screen.fill((210, 210, 210))
    draw_grid()
    while True:
        for event in pygame.event.get():
            mouse_presses = pygame.mouse.get_pressed()
            if event.type == pygame.QUIT:
                raise Exception
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (event.button == 1 and mouse_presses[2]) or (event.button == 3 and mouse_presses[0]):
                    mouse_pos = pygame.mouse.get_pos()
                    is_chord = True
                    if not is_gameover and not is_clock:
                        game()
                elif mouse_presses[0] and not is_chord:
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[1] > 120:
                        is_mouse += 1
                    if is_mouse == 1:
                        start_time = time.time()
                    if not is_gameover and not is_clock:
                        game()
                elif mouse_presses[2] and not is_chord:
                    is_right_mouse = True
                    mouse_pos = pygame.mouse.get_pos()
                    if not is_gameover and not is_clock:
                        game()
        is_right_mouse = False
        is_chord = False
        if is_mouse >= 1:
            clock()
        if is_clock:
            game_over()
        board_update()
        pygame.display.update()

if __name__ == '__main__':
    main()