#include "mcts_agent.h"

MCTSAgent::MCTSAgent() : mcts(BOARD_SIZE, evaluate_with_heuristic)
{
	mcts.root = NULL;
}

BoardState MCTSAgent::play(BoardState board_state)
{
	if(mcts.root == NULL) {
		mcts.root = new Node(board_state, evaluate_with_heuristic);
	} else {
		Node* next_node = NULL;
		for(auto& child : mcts.root->child_list) {
			if(is_same_board(board_state, child->state)) {
				next_node = child;
				break;
			}
		}
		mcts.root = next_node;
	}
	
	for(int i=0; i<MCTS_SEARCH_NUM; i++) {
		mcts.search(mcts.root);
	}

	mcts.root = mcts.play(mcts.root, TEMPERATURE);
	board_state = mcts.root->state;

	return board_state;
}
