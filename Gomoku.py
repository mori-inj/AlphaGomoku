import numpy as np

BOARD_SIZE = 3
N_IN_A_ROW = 3
GRID_SIZE = 15#25
STONE_SIZE = 6#10
BDS = max(GRID_SIZE * (BOARD_SIZE -1) + STONE_SIZE + 16 + BOARD_SIZE*3, 170)
HEIGHT = BDS
WIDTH = BDS

bs = (GRID_SIZE) * (BOARD_SIZE-1) + 1
SX = int(BDS/2 - bs/2.0)
SY= int(BDS/2 - bs/2.0)
EX = SX + bs
EY = SY + bs



def draw_board(canvas, sx, sy, board, node=None, parent=None, selected=None):
    ex = sx + bs
    ey = sy + bs
    BOARD_SIZE = board.board_size
    if selected != None and selected == True:
        canvas.draw_circle(sx+bs/2, sy+bs/2, bs*1.1, fill="", outline="#FFF", width=1)

    for i in range(BOARD_SIZE):
        canvas.create_line(sx+i*GRID_SIZE, sy, sx+i*GRID_SIZE, ey, fill="#FFF")
    for i in range(BOARD_SIZE):
        canvas.create_line(sx, sy+i*GRID_SIZE, ex, sy+i*GRID_SIZE, fill="#FFF")
    
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            x = sx + j*GRID_SIZE
            y = sy + i*GRID_SIZE
            if board[i][j] == 0:
                continue
            if board[i][j]%2*2-1 == -1:
                canvas.draw_circle(x, y, STONE_SIZE, fill="#FFF", outline="#FFF", width=1)
            elif board[i][j]%2*2-1 == 1:
                canvas.draw_circle(x, y, STONE_SIZE, fill="#000", outline="#FFF", width=1)
    
    if node != None and parent != None:
        txt = ""
        txt += "N:%.0f\n" % parent.N[node]
        txt += "W:%.2f\n" % parent.W[node]
        txt += "Q:%.2f\n" % parent.Q[node]
        txt += "P:%.2f\n" % parent.P[node]
        ci = canvas.create_text(sx, sy+bs, anchor="nw", fill="#FFF", font=("Purisa", 10), text=txt)



def is_game_ended(board):
    turn = np.amax(board) 

    if turn==0:
        return False
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == turn:
                row = i
                col = j
                break
        else:
            continue
        break

    dx = [1, 1, 0, -1, -1, -1, 0, 1]
    dy = [0, -1, -1, -1, 0, 1, 1, 1]
    nx = col
    ny = row
    player = board[row][col]%2*2-1

    for key in range(8):
        for i in range(N_IN_A_ROW):
            nx = col - i*dx[key]
            ny = row - i*dy[key]
            for j in range(N_IN_A_ROW):
                if not (0 <= nx and nx < BOARD_SIZE and 0 <= ny and ny < BOARD_SIZE):
                    break
                if board[ny][nx]>0 and board[ny][nx]%2*2-1 != player:
                    break
                if board[ny][nx] == 0:
                    break
                nx = nx + dx[key]
                ny = ny + dy[key]
            else:
                return True
    return False






class BoardState:
    def __init__(self, board_size, turn, last_row = -1, last_col = -1):
        self.board_size = board_size
        self.board = np.zeros([board_size, board_size]).tolist()
        self.turn = turn
        self.last_row = last_row
        self.last_col = last_col
    
    def __getitem__(self, key):
        return self.board[key]
	
    def __str__(self):
        s = '['
        for i in range(self.board_size):
            s += self.board[i].__str__()
        return s + ']'


class Gomoku:
    def __init__(self, board_size, n_in_a_row):
        self.turn = 0
        self.BOARD_SIZE = board_size
        self.N_IN_A_ROW = n_in_a_row
        self.board = BoardState(board_size, 0)

   
    def is_game_ended(self):
        return is_game_ended(self.board.board)

    def is_valid_input(self, row, col):
        if not(0<=row<self.BOARD_SIZE and 0<=col<self.BOARD_SIZE):
            return False

        if self.board[row][col] != 0:
            return False
        return True

    def put_stone(self, row, col):
        self.turn += 1
        self.board[row][col] = self.turn

    def reset(self):
        self.turn = 0
        self.board = np.zeros([self.BOARD_SIZE, self.BOARD_SIZE]).tolist()


