from Gomoku import *
from MCTS import *

MCTS_SEARCH_NUM = 128

TEMPER_EPS = 1e-2
TEMPERATURE = TEMPER_EPS

class MCTSAgent:
    def __init__(self):
        pass

    def play(self, board_state):
        mcts = MCTS(BOARD_SIZE, evaluate_with_heuristic)
        mcts.root = Node(board_state, evaluate_with_heuristic)

        for i in range(MCTS_SEARCH_NUM):
            mcts.search(mcts.root)

        node = mcts.play(mcts.root, TEMPERATURE)
        board_state = node.state
        
        return board_state
