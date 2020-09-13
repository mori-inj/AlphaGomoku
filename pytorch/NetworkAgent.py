from params import *
from Gomoku import *
from MCTS import *
from Network import Network
import numpy as np
import torch
import random

class NetworkAgent:
    def __init__(self):
        self.network = Network(board_size=BS, input_frame_num=INPUT_FRAME_NUM, residual_num=RESIDUAL_NUM, is_trainable=True).cuda() #False
        #self.softmax = torch.nn.Softmax()

    def play(self, board_state):
        state = board_state
        turn = state.turn
        state_list = get_next_states(state)
        s = preproc_board(board_state.board, turn)
        p,v = self.network.get_output(s)
        #p = self.softmax(p)
        p = p.reshape(BS, BS)

        p_dict = {}
        for new_state in state_list:
            r = new_state.last_row
            c = new_state.last_col
            p_dict[new_state] = p[r][c]

        if is_game_ended(state.board):
            v = 1

        p_list = []
        for s in p_dict:
            p_list.append([p_dict[s], s])
        #random.shuffle(p_list)
        for i in range(1, len(p_list)):
            p_list[i][0] += p_list[i-1][0]
        r = np.random.uniform() * p_list[-1][0]
        for i in range(len(p_list)):
            if p_list[i][0] >= r:
                """
                ls = p_list[i][1]
                r = ls.last_row
                c = ls.last_col


                board_state.turn += 1
                board_state[r][c] = board_state.turn
                board_state.last_row = r
                board_state.last_col = c
                return board_state
                """
                return p_list[i][1]

