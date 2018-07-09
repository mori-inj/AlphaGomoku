#include "mcts_agent.h"

#define EVALUATE evaluate_with_network //evaluate_with_heuristic

MCTSAgent::MCTSAgent() : mcts(BOARD_SIZE, EVALUATE)
{
	delete(mcts.root);
	mcts.root = NULL;

	MCTS_SEARCH_NUM = 2;//150;
	TEMPER_EPS = 2e-1;
	TEMPERATURE = TEMPER_EPS;
}

MCTSAgent::MCTSAgent(int msn, double te) : mcts(BOARD_SIZE, EVALUATE)
{
	delete(mcts.root);
	mcts.root = NULL;

	MCTS_SEARCH_NUM = msn;
	TEMPER_EPS = te;
	TEMPERATURE = TEMPER_EPS;
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
		if(next_node != NULL) {
			for(auto& child : mcts.root->child_list) {
				if(child != next_node) {
					child->clear();
				}
			}
			delete(mcts.root);
			mcts.root = next_node;
			mcts.root->parent = NULL;
		}
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

pair<vector<vector<double> >, BoardState> MCTSAgent::get_pi_and_play(BoardState board_state)
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
		if(next_node != NULL) {
			for(auto& child : mcts.root->child_list) {
				if(child != next_node) {
					child->clear();
				}
			}
			delete(mcts.root);
			mcts.root = next_node;
			mcts.root->parent = NULL;
		} else {
			mcts.root->parent = NULL;
		}
	}

	for(int i=0; i<MCTS_SEARCH_NUM; i++) {
		mcts.search(mcts.root);
	}

	vector<vector<double> > pi = get_pi(); 	
	
	Node* old_node = mcts.root;
	mcts.root = mcts.play(mcts.root, TEMPERATURE);
	for(auto& child : old_node->child_list) {
		if(child != mcts.root) {
			child->clear();
		}
	}
	delete(old_node);
	board_state = mcts.root->state;
	
	return make_pair(pi, board_state);
}

vector<vector<double> > MCTSAgent::get_pi()
{
	map<Node*, long double> pi_ = mcts.root->get_pi(TEMPERATURE).first;
	vector<vector<double> > pi = vector<vector<double> >(BOARD_SIZE, vector<double>(BOARD_SIZE, 0.0));
	for(auto& n : pi_) {
		pi[n.first->state.last_row][n.first->state.last_col] = n.second;
	}
	return pi;
}

void MCTSAgent::clear()
{
	mcts.root->clear();
}
