#include "mcts_agent.h"

#include "mcts.h"

BoardState MCTSAgent::play(BoardState board_state)
{
	MCTS mcts(BOARD_SIZE, evaluate_with_heuristic);
	mcts.root = new Node(board_state, evaluate_with_heuristic);
	
	for(int i=0; i<MCTS_SEARCH_NUM; i++) {
		mcts.search(mcts.root);
	}

	Node* node = mcts.play(mcts.root, TEMPERATURE);
	board_state = node->state;

	return board_state;
}
