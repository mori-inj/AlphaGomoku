from params import *
from MCTS import *
import time
import datetime

from RandomAgent import RandomAgent as RandomAg
from HeuristicAgent import HeuristicAgent as HeuristicAg
from MCTSAgent import MCTSAgent as MCTSAg




#ignore original network in MCTS.py and overwrite it with trainable network
network = Network(board_size = BS, input_frame_num = INPUT_FRAME_NUM, residual_num = RESIDUAL_NUM, is_trainable=True)


for iteration in range(SELF_PLAY_NUM):
    print("======================= iter: " + str(iteration) + " ===========================")
    
    input_list = []
    pi_list = []
    z_list = []
    
    game = 0
    while len(input_list) < 2*BATCH_SIZE:
        print("game: ",game," data: ",len(input_list), datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        game += 1

        mcts = MCTS(BS, evaluate_with_network)
        node = mcts.root

        turn_cnt = 0
        while True:
            turn_cnt += 1
            if turn_cnt <= 2:
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
                pi[idx] = n_list[n]
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
                    if i %2*2-1 == next_state.turn%2*2-1:
                        z_list.append([1])
                    else:
                        z_list.append([-1])
                break
            elif next_state.turn == BS*BS:
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
                    z_list.append([0])
                break


    

    index = list(range(len(input_list)))
    random.shuffle(index)
    print('data size: ', len(index))
    index = index[:BATCH_SIZE]
    input_ = np.asarray([input_list[idx] for idx in index])
    pi_ = np.asarray([pi_list[idx] for idx in index])
    z_ = np.asarray([z_list[idx] for idx in index])
    
    
    network.train(input_, pi_, z_, TRAIN_ITER, PRINT_ITER) 

    """
    x_count = 0
    o_count = 0
    draw_count = 0
    AgentA = RandomAg()
    AgentB = MCTSAg()

    for i in range(GAME_NUM):
        if i % GAME_PRINT == 0:
            print(i, "  ", x_count, o_count, draw_count)

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


    print(x_count, o_count, draw_count)


    """
