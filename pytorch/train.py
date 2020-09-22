from params import *
from MCTS import *
import time
import datetime
import numpy as np

from RandomAgent import RandomAgent as RandomAg
from HeuristicAgent import HeuristicAgent as HeuristicAg
from MCTSAgent import MCTSAgent as MCTSAg




#ignore original network in MCTS.py and overwrite it with trainable network
#network = Network(board_size = BS, input_frame_num = INPUT_FRAME_NUM, residual_num = RESIDUAL_NUM, is_trainable=True)

total_input_list = []
total_pi_list = []
total_z_list = []

if __name__ == '__main__':
    for iteration in range(SELF_PLAY_NUM):
        if iteration % 5 == 0 and iteration != 0:
            #"""
            x_count = 0
            o_count = 0
            draw_count = 0
            AgentA = MCTSAg()
            AgentB = RandomAg()

            for i in range(GAME_NUM):
                if i % GAME_PRINT == 0 and i!=0:
                    print("%4d  %4d %4d %4d  %f %f %f" % (i, x_count, o_count, draw_count, x_count/i, o_count/i, draw_count/i), flush=True)

                gomoku = Gomoku(BOARD_SIZE, N_IN_A_ROW)
                turn = 0
                board_state = gomoku.board

                while not gomoku.is_game_ended() and board_state.turn != BOARD_SIZE*BOARD_SIZE:
                    if board_state.turn % 2 == 0:
                        board_state = AgentA.play(board_state)
                    else:
                        board_state = AgentB.play(board_state)
                    gomoku.board = board_state
                    if gomoku.is_game_ended():
                        if board_state.turn%2*2-1 == 1:
                            x_count += 1
                        else:
                            o_count += 1
                        break
                else:
                     draw_count += 1


            print(x_count, o_count, draw_count, flush=True)
            #"""

            x_count = 0
            o_count = 0
            draw_count = 0
            AgentB = MCTSAg()
            AgentA = RandomAg()

            for i in range(GAME_NUM):
                if i % GAME_PRINT == 0 and i!=0:
                    print("%4d  %4d %4d %4d  %f %f %f" % (i, x_count, o_count, draw_count, x_count/i, o_count/i, draw_count/i), flush=True)

                gomoku = Gomoku(BOARD_SIZE, N_IN_A_ROW)
                turn = 0
                board_state = gomoku.board

                while not gomoku.is_game_ended() and board_state.turn != BOARD_SIZE*BOARD_SIZE:
                    if board_state.turn % 2 == 0:
                        board_state = AgentA.play(board_state)
                    else:
                        board_state = AgentB.play(board_state)
                    gomoku.board = board_state
                    if gomoku.is_game_ended():
                        if board_state.turn%2*2-1 == 1:
                            x_count += 1
                        else:
                            o_count += 1
                        break
                else:
                     draw_count += 1


            print(x_count, o_count, draw_count, flush=True)



            #""" 
            #1/0





        print("======================= iter: " + str(iteration) + " ===========================")
        
        input_list = []
        pi_list = []
        z_list = []
        
        if iteration == 0:
            game_iter = INIT_GAME_NUM
        else:
            game_iter = EPOCH_GAME_NUM

        x_count = 0
        o_count = 0
        draw_count = 0
        for game in range(game_iter):

            mcts = MCTS(BS, evaluate_with_network)
            node = mcts.root

            turn_cnt = 0
            while True:
                turn_cnt += 1
                if turn_cnt < TEMPER_THRES:
                    TEMPERATURE = 1
                else:
                    TEMPERATURE = TEMPER_EPS

                for i in range(MCTS_SIM_NUM):
                    mcts.search(node)
                orig_state = node.state
                orig_board = orig_state.board
                input_board = preproc_board(orig_board, orig_state.turn)
                input_list.append(input_board[0])
                
                pi = np.zeros([BS * BS])
                n_list, n_sum = node.get_pi(TEMPERATURE)
                for n in n_list:
                    idx = n.state.last_row * BS + n.state.last_col
                    pi[idx] = n_list[n] / n_sum
                pi_list.append(pi)
                
                node = mcts.play(node, TEMPERATURE)
                
                next_state = node.state
                next_board = next_state.board 
                #r = next_state.last_row
                #c = next_state.last_col

                
                if is_game_ended(next_board):
                    input_board = preproc_board(next_board, next_state.turn)
                    input_list.append(input_board[0])
                    pi = np.zeros([BS * BS])
                    n_list, n_sum = node.get_pi(TEMPERATURE)
                    for n in n_list:
                        idx = n.state.last_row * BS + n.state.last_col
                        pi[idx] = n_list[n]
                    pi_list.append(pi)
                    nst = int(next_state.turn + 1)
                    for i in range(nst):
                        if i%2*2-1 == next_state.turn%2*2-1:
                            z_list.append(torch.tensor([0.0]))
                        else:
                            z_list.append(torch.tensor([0.0]))
                
                    if next_state.turn%2*2-1 == 1:
                        winner = 'x'
                        x_count += 1
                    else:
                        winner = 'o'
                        o_count += 1
                    # print(next_state)
                    print("game: %4d  data: %5d | winner: %4s | x: %4d | o: %4d | draw: %4d | %f %f %f %s" \
                            % (game, len(input_list), \
                            winner, x_count, o_count, draw_count,\
                            x_count / (game+1), o_count / (game+1), draw_count / (game+1),
                            datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')), flush=True)
                    break
                elif next_state.turn == BS*BS:
                    break
                    input_board = preproc_board(next_board, next_state.turn)
                    input_list.append(input_board[0])
                    pi = np.zeros([BS * BS])
                    n_list, n_sum = node.get_pi(TEMPERATURE)
                    for n in n_list:
                        idx = n.state.last_row * BS + n.state.last_col
                        pi[idx] = n_list[n]
                    pi_list.append(pi)
                
                    nst = next_state.turn + 1
                    for _ in range(nst):
                        z_list.append(torch.tensor([0.0]))
                
                    winner = 'draw'
                    draw_count += 1
                    #print(next_state)
                    print("game: %4d  data: %5d | winner: %4s | x: %4d | o: %4d | draw: %4d | %f %f %f %s" \
                            % (game, len(input_list), \
                            winner, x_count, o_count, draw_count,\
                            x_count / (game+1), o_count / (game+1), draw_count / (game+1),
                            datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')), flush=True)

                    break

        #if iteration == 0:
        total_input_list = input_list
        total_pi_list = pi_list
        total_z_list = z_list
        #else:
        #    total_input_list = input_list + total_input_list[len(input_list):]
        #    total_pi_list = pi_list + total_pi_list[len(pi_list):]
        #    total_z_list = z_list + total_z_list[len(z_list):]
        
        print('!!', len(total_input_list), len(total_pi_list), len(total_z_list))
        network.train_model(total_input_list, total_pi_list, total_z_list, EPOCH, iteration)
