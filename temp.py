from Network import Network
import tkinter as tk
import random
import numpy as np
from Gomoku import *

PLAYER_TURN = 1 # -1 for black, 1 for white. Black goes first.
TRAIN_MODE = 0
PLAY_MODE = 1
game_mode = PLAY_MODE

BS = BOARD_SIZE

network = Network(board_size = BS, input_frame_num = 3, residual_num = 9, is_trainable=False)
def preproc_board(board, turn):
    frame = network.input_frame_num
    
    s = [0] * frame
    for fn in range((frame-1)//2):
        f = np.zeros([BS, BS])
        for i in range(BS):
            for j in range(BS):
                if board[i][j] > 0 and board[i][j] % 2 == turn % 2 and \
                    board[i][j] <= turn - fn*2:
                    f[i][j] = 1
        s[fn] = f
    
    for fn in range((frame-1)//2):
        f = np.zeros([BS, BS])
        for i in range(BS):
            for j in range(BS):
                if board[i][j] > 0 and board[i][j] % 2 != turn % 2 and \
                    board[i][j] <= turn - fn*2:
                    f[i][j] = 1
        s[fn + (frame-1)//2] = f

    if turn % 2 == 0:
        s[-1] = np.zeros([BS, BS]) #s.append(np.zeros([BS, BS]))
    else:
        s[-1] = np.ones([BS, BS]) #s.append(np.ones([BS, BS]))
    
    s = np.asarray([s])
    s = np.transpose(s, [0, 2, 3, 1])
    return s





gomoku = Gomoku(BOARD_SIZE, N_IN_A_ROW)

def _draw_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.draw_circle = _draw_circle

def _mouse_left_up(event):
    x, y = event.x, event.y
    if game_mode == PLAY_MODE and not(gomoku.is_game_ended()) :#and gomoku.turn%2*2-1 == PLAYER_TURN:
        col = int((x - SX + GRID_SIZE/2.0) / GRID_SIZE)
        row = int((y - SY + GRID_SIZE/2.0) / GRID_SIZE)
        col_coor = SX + GRID_SIZE*col
        row_coor = SY + GRID_SIZE*row
        if (x-col_coor)**2 + (y-row_coor)**2 <= STONE_SIZE**2:
            if gomoku.is_valid_input(row,col):
                gomoku.put_stone(row, col)
    draw_board(canvas, SX, SY, gomoku.board)
    
    s = preproc_board(gomoku.board, gomoku.turn)
    p,v = network.get_output(s)
    p = p.reshape([BS,BS]).tolist()
    s = ""
    for i in range(BS):
        s += "\n["
        for j in range(BS):
            s += "%.2f " % p[i][j]
        s += "]"
    print(s)
    print(v)
    #ai_input()


def ai_input():
    if game_mode == PLAY_MODE:
        if not(gomoku.is_game_ended()) and gomoku.turn%2*2-1 != PLAYER_TURN:
            y = -1
            x = -1
            while not gomoku.is_valid_input(y,x):
                y = random.randint(0, BOARD_SIZE-1)
                x = random.randint(0, BOARD_SIZE-1)
            gomoku.put_stone(y,x)
    draw_board(canvas, SX, SY, gomoku.board)


root = tk.Tk()
root.resizable(width=False, height=False)
root.bind('<ButtonRelease-1>', _mouse_left_up)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, borderwidth=0, highlightthickness=0, bg="black")
canvas.grid()


draw_board(canvas, SX, SY, gomoku.board)
#if PLAYER_TURN==1:
#    ai_input()


root.wm_title("AlphaGomoku")
root.mainloop()



