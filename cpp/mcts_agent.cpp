#include "mcts_agent.h"

#define EVALUATE evaluate_with_network //evaluate_with_heuristic

MCTSAgent::MCTSAgent() : mcts(BOARD_SIZE, EVALUATE)
{
	delete(mcts.root);
	mcts.root = NULL;
}

BoardState MCTSAgent::play(BoardState board_state)
{
	if(mcts.root == NULL) {
		mcts.root = new Node(board_state, EVALUATE);
	} else {
		Node* next_node = NULL;
		for(auto& child : mcts.root->child_list) {
			if(is_same_board(board_state, child->state)) {
				next_node = child;
				break;
			}
		}
		for(auto& child : mcts.root->child_list) {
			if(child != next_node) {
				child->clear();
			}
		}
		delete(mcts.root);
		mcts.root = next_node;
		mcts.root->parent = NULL;
	}
	
	for(int i=0; i<MCTS_SEARCH_NUM; i++) {
		mcts.search(mcts.root);
	}
	
	Node* old_node = mcts.root;
	mcts.root = mcts.play(mcts.root, TEMPERATURE);
	for(auto& child : old_node->child_list) {
		if(child != mcts.root) {
			child->clear();
		}
	}
	delete(old_node);
	board_state = mcts.root->state;

	return board_state;
}

void MCTSAgent::clear()
{
	mcts.root->clear();
}
