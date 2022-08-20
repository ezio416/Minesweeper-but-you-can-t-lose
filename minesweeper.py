'''
Ezio416 fork of "Minesweeper but you can't lose" by Thebrowndot
Forked:   2022-08-18
Modified: 2022-08-19
'''
import numpy as np
import random
import time

import pygame
from pygame import mixer

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
cell_status = np.zeros([30, 16], dtype=int)
flag_map = np.zeros([30, 16], dtype=int)
is_chord = False
is_clock = False
is_gameover = False
no_mine_array = []
play_sound = False
total_mines = 99
flag_count = total_mines

def draw_grid() -> None:
    blockSize = 30
    for x in range(0, WINDOW_WIDTH, blockSize):
        for y in range(120, WINDOW_HEIGHT, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)

def draw_rect(a, b) -> None:
    pygame.draw.rect(screen, [180] * 3, [(a) * 30, 120 + ((b) * 30), 28, 28])

def chording_helper(tuple0, tuple1) -> None:
    global cell_status
    if not (flag_map[tuple0] or tuple1 in array):
        mine_check(*tuple1)
        if not flag:
            draw_rect(*tuple0)
            cell_status[tuple0] = 1
            floodfill(*tuple1)
        else:
            mine_render(tuple0[0] * 30, 120 + tuple0[1] * 30)
            cell_status[tuple0] = 1
    if not flag_map[tuple0] and tuple1 in array:
        cell_status[tuple0] = 1
        mine_shift(*tuple1)
        # blowup(tuple0[0] * 30, 120 + tuple0[1] * 30)

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

def floodfill_helper(tuple0, tuple1) -> None:
    global cell_status
    mine_check(*tuple0)
    if not flag and not cell_status[tuple1] and not flag_map[tuple1]:
        draw_rect(*tuple1)
        cell_status[tuple1] = 1
        floodfill(*tuple0)
    if flag and not cell_status[tuple1] and not flag_map[tuple1]:
        mine_render(tuple1[0] * 30, 120 + tuple1[1] * 30)
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

def mine_shift(a, b) -> None:
    global array
    array.remove((a, b))
    rand = lambda: (random.randint(1, 30), random.randint(1, 16))
    (mine_x, mine_y) = rand()
    while cell_status[mine_x - 1, mine_y - 1] or (mine_x, mine_y) in array:
        (mine_x, mine_y) = rand()
    array.append((mine_x, mine_y))

def mine_check(a, b) -> None:
    global flag
    flag = 0
    tuples = [(a - 1, b - 1), (a - 1, b + 1), (a + 1, b + 1), (a + 1, b - 1),
              (a, b - 1), (a, b + 1), (a + 1, b), (a - 1, b)]
    for tuple_ in tuples:
        flag += 1 if tuple_ in array else 0

def place_mine() -> list:
    global array
    rand = lambda: (random.randint(1, 30), random.randint(1, 16))
    for i in range(total_mines):
        xytuple = rand()
        new_array = no_mine_array + array if i else no_mine_array
        while xytuple in new_array:
            xytuple = rand()
        array.append(xytuple)
    return array

def mine_render(x,y):
    if flag==1:
        pygame.draw.rect(screen,[180] * 3,[x,y,28,28])
        no_of_mines=font.render(str(flag),True,(0,0,255))
        screen.blit(no_of_mines,(x+7.5,y))
    if flag==2:
        pygame.draw.rect(screen,[180] * 3,[x,y,28,28])
        no_of_mines=font.render(str(flag),True,(0,102,51))
        screen.blit(no_of_mines,(x+7.5,y))
    if flag==3:
        pygame.draw.rect(screen,[180] * 3,[x,y,28,28])
        no_of_mines=font.render(str(flag),True,(255,0,0))
        screen.blit(no_of_mines,(x+7.5,y))
    if flag==4:
        pygame.draw.rect(screen,[180] * 3,[x,y,28,28])
        no_of_mines=font.render(str(flag),True,(0,0,102))
        screen.blit(no_of_mines,(x+7.5,y))
    if flag==5:
        pygame.draw.rect(screen,[180] * 3,[x,y,28,28])
        no_of_mines=font.render(str(flag),True,(102,51,0))
        screen.blit(no_of_mines,(x+7.5,y))
    if flag==6:
        pygame.draw.rect(screen,[180] * 3,[x,y,28,28])
        no_of_mines=font.render(str(flag),True,(0,153,153))
        screen.blit(no_of_mines,(x+7.5,y))
    if flag==7:
        pygame.draw.rect(screen,[180] * 3,[x,y,28,28])
        no_of_mines=font.render(str(flag),True,(0,0,0))
        screen.blit(no_of_mines,(x+7.5,y))
    if flag==8:
        pygame.draw.rect(screen,[180] * 3,[x,y,28,28])
        no_of_mines=font.render(str(flag),True,(160,160,160))
        screen.blit(no_of_mines,(x+7.5,y))

def blowup(x,y):
    global is_clock
    global flag
    global is_gameover
    place_mine()
    screen.blit(mine_img,(x,y))
    is_clock = True
    flag=10
    is_gameover = True
    if play_sound:
        mixer.Sound('blast.wav').play()

board_config=np.zeros([16,30],dtype=int)
def board_update():
    global flag
    for a in range(1, 31):
        for b in range(1, 17):
            if cell_status[a - 1, b - 1] == 1:
                mine_check(a, b)
                board_config[b - 1, a - 1] = flag
                if flag:
                    mine_render((a - 1) * 30, 120 + ((b - 1) * 30))
                else:
                    draw_rect(a - 1, b - 1)

def main_game():
    global flag
    global mouse_pos
    global is_clock
    global is_gameover
    global is_chord
    global is_mouse
    global no_mine_array
    global flag_count
    global array
    blockSize = 30
    a=0
    for x in range(0, WINDOW_WIDTH, blockSize):
        a+=1
        b=0
        for y in range(120, WINDOW_HEIGHT, blockSize):
            flag=0
            b+=1
            if mouse_pos[0]<=x+blockSize and mouse_pos[1]<=y+blockSize and mouse_pos[0]>=x and mouse_pos[1]>=y:
                if is_mouse == 1:
                    no_mine_array = [(a, b), (a - 1, b), (a, b - 1), (a - 1, b - 1), (a + 1, b),
                                     (a, b + 1), (a + 1, b + 1), (a + 1, b - 1), (a - 1, b + 1)]
                    place_mine()
                    is_mouse += 1
                two_right_click = 0
                if is_right_mouse and flag_map[a - 1, b - 1] == 1 and not is_chord:
                    if play_sound:
                        mixer.Sound('flag.wav').play()
                    pygame.draw.rect(screen, [210] * 3, [x, y + 1, 28, 28])
                    flag_map[a-1,b-1]=0
                    two_right_click=1
                    flag_count += 1
                if is_right_mouse and cell_status[a-1,b-1]==0 and flag_map[a-1,b-1]==0 and two_right_click==0 and not is_chord:
                    if play_sound:
                        mixer.Sound('flag.wav').play()
                    screen.blit (flag_img,(x,y))
                    flag_map[a-1,b-1]=1
                    flag_count -= 1
                if not is_right_mouse and flag_map[a-1,b-1]==0 and not is_chord and cell_status[a-1,b-1]==0:
                    if (a,b) in array:
                        cell_status[a-1,b-1]=1
                        mine_shift(a,b)
                        #blowup(x,y)
                    else:
                        mine_check(a,b)
                        if flag and flag!=10:
                            if not cell_status[a - 1, b - 1] and play_sound:
                                mixer.Sound('click.wav').play()
                            mine_render(x,y)
                            cell_status[a-1,b-1]=1
                        if not flag:
                            if not cell_status[a - 1, b - 1] and play_sound:
                                mixer.Sound('empty_cell.wav').play()
                            pygame.draw.rect(screen,[180] * 3,[(a-1)*30,120+((b-1)*30),28,28])
                            cell_status[a-1,b-1]=1
                            floodfill(a,b)
                if is_chord and flag_map[a-1,b-1]==0:
                    chording(a,b)
                    is_chord = False
                mouse_pos=(0,0)
            pygame.draw.rect(screen,[210,210,210],[420,10,73,30])
            pygame.draw.rect(screen,[0,0,0],[420,10,73,30],2)
            screen.blit (flag_img,(420,10))
            flag_font=font.render(str(flag_count),True,(0,0,0))
            screen.blit(flag_font,(455,11))

def clock():
    global is_clock
    if np.sum(cell_status)>=381:
        is_clock=1
    if not is_clock:
        pygame.draw.rect(screen,[210,210,210],[428,50,57,28])
        pygame.draw.rect(screen,[0,0,0],[428,50,57,28],2)
        time_font=font.render(str("%03d"%(time.time()-start_time)),True,(255,0,0))
        screen.blit(time_font,(430,50))

def game_over():
    if is_gameover:
        font_ = font.render("GAME OVER", True, (0, 0, 0))
        screen.blit(font_, (360, 85))
    else:
        font_ = font.render("YOU WIN", True, (0, 0, 0))
        screen.blit(font_, (390, 85))
        if play_sound:
            mixer.Sound('win.wav').play()

is_mouse=0
start_time=0
screen.fill((210,210,210))
draw_grid()
while True:
    for event in pygame.event.get():
        mouse_presses=pygame.mouse.get_pressed()
        if event.type==pygame.QUIT:
            raise Exception
        if event.type==pygame.MOUSEBUTTONDOWN:
            if (event.button==1 and mouse_presses[2]) or (event.button==3 and mouse_presses[0]):
                mouse_pos=pygame.mouse.get_pos()
                is_chord = True
                if not is_gameover and not is_clock:
                    main_game()
            elif mouse_presses[0] and not is_chord:
                mouse_pos=pygame.mouse.get_pos()
                if mouse_pos[1]>120:
                    is_mouse=is_mouse+1
                if is_mouse==1:
                    start_time=time.time()
                if not is_gameover and not is_clock:
                    main_game()
            elif mouse_presses[2] and not is_chord:
                is_right_mouse = True
                mouse_pos=pygame.mouse.get_pos()
                if not is_gameover and not is_clock:
                    main_game()
    is_right_mouse = False
    is_chord = False
    if is_mouse >= 1:
        clock()
    if is_clock:
        game_over()
    board_update()
    pygame.display.update()
