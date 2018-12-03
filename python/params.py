#Gomoku
BOARD_SIZE = 3#9
N_IN_A_ROW = 3#5

#MCTS
C_PUCT = 5
EPSILON = 0#0.25 #0.1
DIR_ALPHA = 0.5 #0.3

MCTS_SIM_NUM = 128 #512
TEMPER_EPS = 1#1e-1
TEMPERATURE = 1#TEMPER_EPS

#network
INPUT_FRAME_NUM = 5
RESIDUAL_NUM = 9

#play
#EVALUATE = "constant"
#EVALUATE = "random"
#EVALUATE = "heuristic"
EVALUATE = "network"

AgA = "random"
#AgA = "heuristic"
#AgA = "MCTS"

#AgB = "random"
#AgB = "heuristic"
AgB = "MCTS"

SINGLE_PLAY = False

TOTAL_GAME_NUM = 10000
TOTAL_GAME_PRINT = 100

#train
SELF_PLAY_NUM = 2000
TRAIN_ITER = 150#500
PRINT_ITER = 50#100

BATCH_SIZE = 100#1024#20#2048
MINI_BATCH_SIZE = 10#32#10#32

GAME_NUM = 200#10#100
GAME_PRINT = 10#2#5
