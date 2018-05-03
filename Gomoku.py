import numpy as np

class BoardState:
    def __init__(self, board_size):
        self.board_size = board_size
        self.board = np.zeros([board_size, board_size]).tolist()
    def __getitem__(self, key):
        return self.board[key]

class Gomoku:
    def __init__(self, board_size, n_in_a_row):
        self.turn = 0
        self.BOARD_SIZE = board_size
        self.N_IN_A_ROW = n_in_a_row
        self.board = BoardState(board_size)

   
    def is_game_ended(self, row=-1, col=-1):
        if row < 0 and col < 0:
            if self.turn==0:
                return False
            for i in range(self.BOARD_SIZE):
                for j in range(self.BOARD_SIZE):
                    if self.board[i][j] == self.turn:
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
        player = self.board[row][col]%2*2-1

        for key in range(8):
            for i in range(self.N_IN_A_ROW):
                nx = col - i*dx[key]
                ny = row - i*dy[key]
                for j in range(self.N_IN_A_ROW):
                    if not (0 <= nx and nx < self.BOARD_SIZE and 0 <= ny and ny < self.BOARD_SIZE):
                        break
                    if self.board[ny][nx]>0 and self.board[ny][nx]%2*2-1 != player:
                        break
                    if self.board[ny][nx] == 0:
                        break
                    nx = nx + dx[key]
                    ny = ny + dy[key]
                else:
                    return True
        return False

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


