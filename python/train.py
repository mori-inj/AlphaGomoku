from MCTS import *
import tkinter as tk

MCTS_SEARCH_NUM = 128
SELF_PLAY_NUM = 2000 #25000 # number of games
AFTER_NUM = 100 # number of epochs to train network after self play
SELF_PLAY_ITER = 10
TRAIN_ITER = 500
PRINT_ITER = 100

SELF_PLAY_BATCH_SIZE = 200
TRAIN_BATCH_SIZE = 1000

TEMPER_EPS = 1e-2
TEMPERATURE = TEMPER_EPS

#ignore original network in MCTS.py and overwrite it with trainable network
network = Network(board_size = BS, input_frame_num = 3, residual_num = 9, is_trainable=True)

input_list = []
pi_list = []
z_list = []
t_list = []

for iteration in range(SELF_PLAY_NUM):
    mcts = MCTS(BS, evaluate_with_heuristic)
    node = mcts.root
    print("======================= iter: " + str(iteration) + " ===========================")

    turn_cnt = 0
    while True:
        turn_cnt += 1
        if turn_cnt <= 2:
            TEMPERATURE = 1
        else:
            TEMPERATURE = TEMPER_EPS

        for i in range(MCTS_SEARCH_NUM):
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
        r = next_state.last_row
        c = next_state.last_col

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
                t_list.append([float(next_state.turn)])
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
                t_list.append([float(next_state.turn)])
            break

    if iteration % SELF_PLAY_ITER == 0:
        l = len(input_list) - 9
        index = []
        i = random.randrange(0, max(1, len(input_list)//SELF_PLAY_BATCH_SIZE))
        while i < l:
            index.append(i)
            i += random.randrange(1, max(2, len(input_list)//SELF_PLAY_BATCH_SIZE))
        while i < len(input_list):
            index.append(i)
            i += 1
        random.shuffle(index)
        print('data size: ', len(index))
        input_ = np.asarray([input_list[idx] for idx in index])
        pi_ = np.asarray([pi_list[idx] for idx in index])
        z_ = np.asarray([z_list[idx] for idx in index])
        t_ = np.asarray([t_list[idx] for idx in index])
    
    """ 
    print('==========input========')
    print(len(input_list), np.transpose(input_list,[0,3,1,2]))
    print('============pi=========')
    print(len(pi_list), pi_list)
    print('============z==========')
    print(len(z_list), z_list)
    print('=======================')
    """
    print(len(input_list), len(pi_list), len(z_list))
    """
    input_list_t = np.transpose(input_list, [0,3,1,2])
    for i in range(len(input_list)):
        frame = network.input_frame_num
        bd = np.zeros([BS,BS])
        for y in range(BS):
            for x in range(BS):
                if input_list_t[i][0][y][x] == 1:
                    bd[y][x] = 1
                elif input_list_t[i][(frame-1)//2][y][x] == 1:
                    bd[y][x] = -1
        pi_t = np.reshape(np.asarray(pi_list[i]),[BS,BS]).tolist()
        st = ""
        for j in range(BS):
            for k in range(BS):
                if (i % 2 == 0 and bd[j][k] == 1) or (i % 2 == 1 and bd[j][k] == -1):
                    st += "o "
                elif (i % 2 == 0 and bd[j][k] == -1) or (i % 2 == 1 and bd[j][k] == 1):
                    st += "x "
                else:
                    st += "  "
            st += "    "
            for k in range(BS):
                st += "%.2f " % pi_t[j][k]
            if j != BS-1:
                st += "\n"
        print(st)
        print(z_list[i])
        print()
    """

    if iteration % SELF_PLAY_ITER == 0:
        network.train(input_, pi_, z_, t_, TRAIN_ITER, PRINT_ITER) 

for iteration in range(AFTER_NUM):
    print('============ iter:' + str(iteration) + '=============')
    l = len(input_list) - 9
    index = []
    i = random.randrange(0, max(1, len(input_list)//TRAIN_BATCH_SIZE))
    while i < l:
        index.append(i)
        i += random.randrange(1, max(2, len(input_list)//TRAIN_BATCH_SIZE))
    while i < len(input_list):
        index.append(i)
        i += 1
    random.shuffle(index) 
    
    input_ = np.asarray([input_list[idx] for idx in index])
    pi_ = np.asarray([pi_list[idx] for idx in index])
    z_ = np.asarray([z_list[idx] for idx in index])
    t_ = np.asarray([t_list[idx] for idx in index])
    network.train(input_, pi_, z_, t_, TRAIN_ITER, PRINT_ITER)
