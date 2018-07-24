#include "mcts_agent.h"

#include "params.h"

MCTSAgent::MCTSAgent() : mcts(BOARD_SIZE, EVALUATE)
{
	temperature = TEMPER_EPS;
	delete(mcts.root);
	mcts.root = NULL;
}

MCTSAgent::MCTSAgent(int msn) : mcts(BOARD_SIZE, EVALUATE)
{
	temperature = TEMPER_EPS;
	delete(mcts.root);
	mcts.root = NULL;
}

BoardState MCTSAgent::play(BoardState board_state)
{
	if(mcts.root != NULL && mcts.root->state.turn <= TEMPER_THRS) {
		temperature = 1;
	}

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
	
	for(int i=0; i<MCTS_SIM_NUM; i++) {
		mcts.search(mcts.root);
	}
	
	Node* old_node = mcts.root;
	mcts.root = mcts.play(mcts.root, temperature);
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
	if(mcts.root != NULL && mcts.root->state.turn <= TEMPER_THRS) {
		temperature = 1;
	}

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

	for(int i=0; i<MCTS_SIM_NUM; i++) {
		mcts.search(mcts.root);
	}

	vector<vector<double> > pi = get_pi(); 	
	
	Node* old_node = mcts.root;
	mcts.root = mcts.play(mcts.root, temperature);
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
	if(mcts.root != NULL && mcts.root->state.turn <= TEMPER_THRS) {
		temperature = 1;
	}

	map<Node*, long double> pi_ = mcts.root->get_pi(temperature).first;
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
