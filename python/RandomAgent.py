from Gomoku import *
import random

class RandomAgent:
    def __init__(self):
        pass
    
    def play(self, board_state):
        row = random.randrange(0, BOARD_SIZE)
        col = random.randrange(0, BOARD_SIZE)
        while abs(board_state[row][col]) > 1e-3:
            row = random.randrange(0, BOARD_SIZE)
            col = random.randrange(0, BOARD_SIZE)
       
        board_state.turn += 1
        board_state[row][col] = board_state.turn
        board_state.last_row = row
        board_state.last_col = col

        return board_state
       

