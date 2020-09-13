from params import *
from Gomoku import *
from MCTS import *


if EVALUATE == "constant":
    EVALUATE = evaluate_with_constant
elif EVALUATE == "random":
    EVALUATE = evaluate_with_random
elif EVALUATE == "heuristic":
    EVALUATE = evaluate_with_heuristic
elif EVALUATE == "network":
    EVALUATE = evaluate_with_network


class MCTSAgent:
    def __init__(self):
        pass

    def play(self, board_state):
        mcts = MCTS(BOARD_SIZE, EVALUATE)
        mcts.root = Node(board_state, EVALUATE)

        if board_state.turn < TEMPER_THRES:
            TEMPERATURE = 1
        else:
            TEMPERATURE = TEMPER_EPS


        for i in range(MCTS_SIM_NUM):
            mcts.search(mcts.root)

        node = mcts.play(mcts.root, TEMPERATURE)
        board_state = node.state
        
        return board_state
