from params import *
import numpy as np

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
        s = ''
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j]==0:
                    s += "| "
                elif self.board[i][j]%2*2-1 == 1:
                    s += "|x"
                else:
                    s += "|o"
            s += '|\n'
        return s


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
        self.board = BoardState(board_size, 0)


