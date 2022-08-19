'''
Ezio416 fork of "Minesweeper but you can't lose" by Thebrowndot
Forked:   2022-08-18
Modified: 2022-08-18
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
chord_flag = False
clock_flag = 0
game_over_flag = 0
no_mine_array = []
play_sound = False
running = True
total_mines = 99
flag_number = total_mines
win_flag = 0

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

def draw_grid() -> None:
    blockSize = 30
    for x in range(0, WINDOW_WIDTH, blockSize):
        for y in range(120, WINDOW_HEIGHT, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)

def mine_shift(a, b) -> None:
    global array
    array.remove((a, b))
    rand = lambda: (random.randint(1, 30), random.randint(1, 16))
    (mine_x, mine_y) = rand()
    while cell_status[mine_x - 1, mine_y - 1] or (mine_x, mine_y) in array:
        (mine_x, mine_y) = rand()
    array.append((mine_x, mine_y))

def chording(a,b):
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
        draw = lambda var_a, var_b: pygame.draw.rect(screen, [180] * 3, [(var_a) * 30, 120 + ((var_b) * 30), 28, 28])
        if a > 1 and b > 1:
            if not (flag_map[a - 2, b - 2] or (a - 1, b - 1) in array):
                mine_check(a - 1, b - 1)
                if not flag:
                    draw(a - 2, b - 2)
                    cell_status[a - 2, b - 2] = 1
                    floodfill(a - 1, b - 1)
                else:
                    mine_render((a - 2) * 30, 120 + (b - 2) * 30)
                    cell_status[a - 2, b - 2] = 1
            if not flag_map[a - 2, b - 2] and (a - 1, b - 1) in array:
                cell_status[a - 2, b - 2] = 1
                mine_shift(a - 1, b - 1)
                #blowup((a-2)*30,120+(b-2)*30)
        if a > 1:
            if not (flag_map[a - 2, b - 1] or (a - 1, b) in array):
                mine_check(a - 1, b)
                if not flag:
                    draw(a - 2, b - 1)
                    cell_status[a - 2, b - 1] = 1
                    floodfill(a - 1, b)
                else:
                    mine_render((a - 2) * 30, 120 + (b - 1) * 30)
                    cell_status[a - 2, b - 1] = 1
            if not flag_map[a - 2, b - 1] and (a - 1, b) in array:
                cell_status[a - 2, b - 1] = 1
                mine_shift(a - 1, b)
                #blowup((a-2)*30,120+(b-1)*30)
        if b<16:
            if flag_map[a-1,b]==0 and (a,b+1) not in array:
                mine_check(a,b+1)
                if not flag:
                    draw(a - 1, b)
                    cell_status[a-1,b]=1
                    floodfill(a,b+1)
                else:
                    mine_render((a-1)*30,120+(b)*30)
                    cell_status[a-1,b]=1
            if flag_map[a-1,b]==0 and (a,b+1) in array:
                cell_status[a-1,b]=1
                mine_shift(a,b+1)
                #blowup((a-1)*30,120+(b)*30)
        if a<30 and b<16:
            if flag_map[a,b]==0 and (a+1,b+1) not in array:
                mine_check(a+1,b+1)
                if not flag:
                    draw(a, b)
                    cell_status[a,b]=1
                    floodfill(a+1,b+1) 
                else:
                    mine_render((a)*30,120+(b)*30)
                    cell_status[a,b]=1
            if flag_map[a,b]==0 and (a+1,b+1) in array:
                cell_status[a,b]=1
                mine_shift(a+1,b+1)
                #blowup((a)*30,120+(b)*30)
        if a<30:
            if flag_map[a,b-1]==0 and (a+1,b) not in array:
                mine_check(a+1,b)
                if not flag:
                    draw(a, b - 1)
                    cell_status[a,b-1]=1
                    floodfill(a+1,b) 
                else:
                    mine_render((a)*30,120+(b-1)*30)
                    cell_status[a,b-1]=1
            if flag_map[a,b-1]==0 and (a+1,b) in array:
                cell_status[a,b-1]=1
                mine_shift(a+1,b)
                #blowup((a)*30,120+(b-1)*30)
        if b>1:
            if flag_map[a-1,b-2]==0 and (a,b-1) not in array:
                mine_check(a,b-1)
                if not flag:
                    draw(a - 1, b - 2)
                    cell_status[a-1,b-2]=1
                    floodfill(a,b-1)
                else:
                    mine_render((a-1)*30,120+(b-2)*30)
                    cell_status[a-1,b-2]=1
            if flag_map[a-1,b-2]==0 and (a,b-1) in array:
                cell_status[a-1,b-2]=1
                mine_shift(a,b-1)
                #blowup((a-1)*30,120+(b-2)*30)
        if a>1 and b<16:
            if flag_map[a-2,b]==0 and (a-1,b+1) not in array:
                mine_check(a-1,b+1)
                if not flag:
                    draw(a - 2, b)
                    cell_status[a-2,b]=1
                    floodfill(a-1,b+1)
                else:
                    mine_render((a-2)*30,120+(b)*30)
                    cell_status[a-2,b]=1
            if flag_map[a-2,b]==0 and (a-1,b+1) in array:
                cell_status[a-2,b]=1
                mine_shift(a-1,b+1)
                #blowup((a-2)*30,120+(b)*30)
        if a<30 and b>1:
            if flag_map[a,b-2]==0 and (a+1,b-1) not in array:
                mine_check(a+1,b-1)
                if not flag:
                    draw(a, b - 2)
                    cell_status[a,b-2]=1
                    floodfill(a+1,b-1)
                else:
                    mine_render((a)*30,120+(b-2)*30)
                    cell_status[a,b-2]=1
            if flag_map[a,b-2]==0 and (a+1,b-1) in array:
                cell_status[a,b-2]=1
                mine_shift(a+1,b-1)
                #blowup((a)*30,120+(b-2)*30)
        if play_sound:
            mixer.Sound('chord.wav').play()

def mine_check(a,b):
    global flag
    flag=0
    if (a - 1, b - 1) in array:
        flag += 1
    if (a - 1, b + 1) in array:
        flag += 1
    if (a + 1, b + 1) in array:
        flag += 1
    if (a + 1, b - 1) in array:
        flag += 1
    if (a, b - 1) in array:
        flag += 1
    if (a, b + 1) in array:
        flag += 1
    if (a + 1, b) in array:
        flag += 1
    if (a - 1, b) in array:
        flag += 1
cell_status=np.zeros([30,16],dtype=int)
flag_map=np.zeros([30,16],dtype=int)
def floodfill(k,l):
    if k+1<=30 and l>=1 and k+1>=1 and l<=16:
        mine_check(k+1,l)
        if not flag and cell_status[k,l-1]==0 and flag_map[k,l-1]==0:
            pygame.draw.rect(screen,[180] * 3,[(k)*30,120+((l-1)*30),28,28])
            cell_status[k,l-1]=1
            floodfill(k+1,l)
        if flag!=0 and cell_status[k,l-1]==0 and flag_map[k,l-1]==0:
            mine_render((k)*30,120+((l-1)*30))
            cell_status[k,l-1]=1
    if k>=1 and k<=30 and l+1>=1 and l+1<=16:
        mine_check(k,l+1)
        if not flag and cell_status[k-1,l]==0 and flag_map[k-1,l]==0:
            pygame.draw.rect(screen,[180] * 3,[(k-1)*30,120+((l)*30),28,28])
            cell_status[k-1,l]=1
            floodfill(k,l+1)
        if flag!=0 and cell_status[k-1,l]==0 and flag_map[k-1,l]==0:
            mine_render((k-1)*30,120+((l)*30))
            cell_status[k-1,l]=1
    if k+1>=1 and k+1<=30 and l+1>=1 and l+1<=16:
        mine_check(k+1,l+1)
        if not flag and cell_status[k,l]==0 and flag_map[k,l]==0:
            pygame.draw.rect(screen,[180] * 3,[(k)*30,120+((l)*30),28,28])
            cell_status[k,l]=1
            floodfill(k+1,l+1)
        if flag!=0 and cell_status[k,l]==0 and flag_map[k,l]==0:
            mine_render((k)*30,120+((l)*30))
            cell_status[k,l]=1
    if k+1>=1 and k+1<=30 and l-1>=1 and l-1<=16:
        mine_check(k+1,l-1)
        if not flag and cell_status[k,l-2]==0 and flag_map[k,l-2]==0:
            pygame.draw.rect(screen,[180] * 3,[(k)*30,120+((l-2)*30),28,28])
            cell_status[k,l-2]=1
            floodfill(k+1,l-1) 
        if flag!=0 and cell_status[k,l-2]==0 and flag_map[k,l-2]==0:
           mine_render((k)*30,120+((l-2)*30))
           cell_status[k,l-2]=1
    if k-1>=1 and k-1<=30 and l>=1 and l<=16:
        mine_check(k-1,l)
        if not flag and cell_status[k-2,l-1]==0 and flag_map[k-2,l-1]==0:
            pygame.draw.rect(screen,[180] * 3,[(k-2)*30,120+((l-1)*30),28,28])
            cell_status[k-2,l-1]=1
            floodfill(k-1,l) 
        if flag!=0 and cell_status[k-2,l-1]==0 and flag_map[k-2,l-1]==0:
            mine_render((k-2)*30,120+((l-1)*30))
            cell_status[k-2,l-1]=1  
    if k>=1 and k<=30 and l-1>=1 and l-1<=16:
        mine_check(k,l-1)
        if not flag and cell_status[k-1,l-2]==0 and flag_map[k-1,l-2]==0:
            pygame.draw.rect(screen,[180] * 3,[(k-1)*30,120+((l-2)*30),28,28])
            cell_status[k-1,l-2]=1
            floodfill(k,l-1)
        if flag!=0 and cell_status[k-1,l-2]==0 and flag_map[k-1,l-2]==0:
            mine_render((k-1)*30,120+((l-2)*30))
            cell_status[k-1,l-2]=1
    if k-1>=1 and k-1<=30 and l-1>=1 and l-1<=16:
        mine_check(k-1,l-1)
        if not flag and cell_status[k-2,l-2]==0 and flag_map[k-2,l-2]==0:
            pygame.draw.rect(screen,[180] * 3,[(k-2)*30,120+((l-2)*30),28,28])
            cell_status[k-2,l-2]=1
            floodfill(k-1,l-1)
        if flag!=0 and cell_status[k-2,l-2]==0 and flag_map[k-2,l-2]==0:
            mine_render((k-2)*30,120+((l-2)*30))
            cell_status[k-2,l-2]=1
    if k-1>=1 and k-1<=30 and l+1>=1 and l+1<=16:
        mine_check(k-1,l+1)
        if not flag and cell_status[k-2,l]==0 and flag_map[k-2,l]==0:
            pygame.draw.rect(screen,[180] * 3,[(k-2)*30,120+((l)*30),28,28])
            cell_status[k-2,l]=1
            floodfill(k-1,l+1)
        if flag!=0 and cell_status[k-2,l]==0 and flag_map[k-2,l]==0:
            mine_render((k-2)*30,120+((l)*30))
            cell_status[k-2,l]=1
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
    global clock_flag
    global flag
    global game_over_flag
    place_mine()
    screen.blit(mine_img,(x,y))
    clock_flag=1
    flag=10
    game_over_flag=1
    if play_sound:
        mixer.Sound('blast.wav').play()

board_config=np.zeros([16,30],dtype=int)
def board_update():
    global flag
    for a in range(1,31):
        for b in range(1,17):
            if cell_status[a-1,b-1]==1:
                mine_check(a,b)
                board_config[b-1,a-1]=flag
                if not flag:
                    pygame.draw.rect(screen,[180] * 3,[(a-1)*30,120+((b-1)*30),28,28])
                else:
                    mine_render((a-1)*30,120+((b-1)*30))
def main_game():
    global flag
    global mouse_pos
    global clock_flag
    global game_over_flag
    global chord_flag
    global mouse_flag
    global no_mine_array
    global flag_number
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
                if mouse_flag==1:
                    no_mine_array=[(a,b),(a-1,b),(a,b-1),(a-1,b-1),(a+1,b),(a,b+1),(a+1,b+1),(a+1,b-1),(a-1,b+1)]
                    place_mine()
                    mouse_flag=mouse_flag+1
                two_right_click=0
                if right_mouse_flag==1 and flag_map[a-1,b-1]==1 and not chord_flag:
                    if play_sound:
                        mixer.Sound('flag.wav').play()
                    pygame.draw.rect(screen,[210,210,210],[x,y+1,28,28])
                    flag_map[a-1,b-1]=0
                    two_right_click=1
                    flag_number=flag_number+1

                if right_mouse_flag==1 and cell_status[a-1,b-1]==0 and flag_map[a-1,b-1]==0 and two_right_click==0 and not chord_flag:
                    if play_sound:
                        mixer.Sound('flag.wav').play()
                    screen.blit (flag_img,(x,y))
                    flag_map[a-1,b-1]=1
                    flag_number=flag_number-1
            
                if right_mouse_flag!=1 and flag_map[a-1,b-1]==0 and not chord_flag and cell_status[a-1,b-1]==0:
                    if (a,b) in array:
                        cell_status[a-1,b-1]=1
                        mine_shift(a,b)
                        #blowup(x,y)
                    else: 
                        mine_check(a,b)
                        
                        if flag!=0 and flag!=10:
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
                
                if chord_flag and flag_map[a-1,b-1]==0:
                    chording(a,b)
                    chord_flag = False
                mouse_pos=(0,0)
            pygame.draw.rect(screen,[210,210,210],[420,10,73,30])
            pygame.draw.rect(screen,[0,0,0],[420,10,73,30],2)
            screen.blit (flag_img,(420,10))
            flag_font=font.render(str(flag_number),True,(0,0,0))
            screen.blit(flag_font,(455,11))
def clock():
    global clock_flag
    if np.sum(cell_status)>=381:
        clock_flag=1
    if not clock_flag:
        pygame.draw.rect(screen,[210,210,210],[428,50,57,28])
        pygame.draw.rect(screen,[0,0,0],[428,50,57,28],2)
        time_font=font.render(str("%03d"%(time.time()-start_time)),True,(255,0,0))
        screen.blit(time_font,(430,50))

def game_over():
    global win_flag
    if game_over_flag == 1:
        game_over_font = font.render("GAME OVER", True, (0, 0, 0))
        screen.blit(game_over_font, (360, 85))
    else:  
        you_win_font = font.render("YOU WIN", True, (0, 0, 0))
        screen.blit(you_win_font, (390, 85))
        win_flag += 1
        if win_flag and play_sound:
            mixer.Sound('win.wav').play()

mouse_flag=0
start_time=0
screen.fill((210,210,210))
draw_grid()
while running:
    for event in pygame.event.get():
        mouse_presses=pygame.mouse.get_pressed()
        if event.type==pygame.QUIT:
            running=False
        if event.type==pygame.MOUSEBUTTONDOWN:
            if (event.button==1 and mouse_presses[2]) or (event.button==3 and mouse_presses[0]):
                mouse_pos=pygame.mouse.get_pos()
                chord_flag = True
                if not game_over_flag and not clock_flag:
                    main_game()
            elif mouse_presses[0] and not chord_flag:
                mouse_pos=pygame.mouse.get_pos()
                if mouse_pos[1]>120:
                    mouse_flag=mouse_flag+1
                if mouse_flag==1:
                    start_time=time.time()
                if not game_over_flag and not clock_flag:
                    main_game()
            elif mouse_presses[2] and not chord_flag:
                right_mouse_flag=1
                mouse_pos=pygame.mouse.get_pos()
                if not game_over_flag and not clock_flag:
                    main_game()
    right_mouse_flag=0
    chord_flag = False
    if mouse_flag>=1:
        clock()
    if clock_flag==1:
        game_over()
    board_update()
    pygame.display.update()
