import tkinter as tk
import random
from Gomoku import Gomoku

PLAYER_TURN = 1 # -1 for black, 1 for white. Black goes first.
TRAIN_MODE = 0
PLAY_MODE = 1
game_mode = PLAY_MODE


BOARD_SIZE = 3
N_IN_A_ROW = 3
GRID_SIZE = 25
STONE_SIZE = 10
BS = max(GRID_SIZE * (BOARD_SIZE -1) + STONE_SIZE + 16 + BOARD_SIZE*3, 170)
HEIGHT = BS
WIDTH = BS

bs = (GRID_SIZE) * (BOARD_SIZE-1) + 1
sx = int(BS/2 - bs/2.0)
sy = int(BS/2 - bs/2.0)
ex = sx + bs
ey = sy + bs


gomoku = Gomoku(BOARD_SIZE, N_IN_A_ROW)

def _draw_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.draw_circle = _draw_circle

def draw_board():
    for i in range(BOARD_SIZE):
        canvas.create_line(sx+i*GRID_SIZE, sy, sx+i*GRID_SIZE, ey, fill="#FFF")
    for i in range(BOARD_SIZE):
        canvas.create_line(sx, sy+i*GRID_SIZE, ex, sy+i*GRID_SIZE, fill="#FFF")
    
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            x = sx + j*GRID_SIZE
            y = sy + i*GRID_SIZE
            if gomoku.board[i][j] == 0:
                continue
            if gomoku.board[i][j]%2*2-1 == -1:
                canvas.draw_circle(x, y, STONE_SIZE, fill="#FFF", outline="#FFF", width=1)
            elif gomoku.board[i][j]%2*2-1 == 1:
                canvas.draw_circle(x, y, STONE_SIZE, fill="#000", outline="#FFF", width=1)

def _mouse_left_up(event):
    x, y = event.x, event.y
    if game_mode == PLAY_MODE and not(gomoku.is_game_ended()) and gomoku.turn%2*2-1 == PLAYER_TURN:
        col = int((x - sx + GRID_SIZE/2.0) / GRID_SIZE)
        row = int((y - sy + GRID_SIZE/2.0) / GRID_SIZE)
        col_coor = sx + GRID_SIZE*col
        row_coor = sy + GRID_SIZE*row
        if (x-col_coor)**2 + (y-row_coor)**2 <= STONE_SIZE**2:
            if gomoku.is_valid_input(row,col):
                gomoku.put_stone(row, col)
    draw_board()
    ai_input()


def ai_input():
    if game_mode == PLAY_MODE:
        if not(gomoku.is_game_ended()) and gomoku.turn%2*2-1 != PLAYER_TURN:
            y = -1
            x = -1
            while not gomoku.is_valid_input(y,x):
                y = random.randint(0, BOARD_SIZE-1)
                x = random.randint(0, BOARD_SIZE-1)
            gomoku.put_stone(y,x)
    draw_board()


root = tk.Tk()
root.resizable(width=False, height=False)
root.bind('<ButtonRelease-1>',_mouse_left_up)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, borderwidth=0, highlightthickness=0, bg="black")
canvas.grid()


draw_board()
if PLAYER_TURN==1:
    ai_input()


root.wm_title("AlphaGomoku")
root.mainloop()



