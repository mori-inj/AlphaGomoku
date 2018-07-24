#include "mcts.h"

#include "params.h"
#include "network.h"
#include "heuristic_agent.h"

#include <math.h>
#include <cfloat>
#include <functional>
#include <random>

const int BS = BOARD_SIZE;

Network network;
//input_frame_num = 5 means, past 2 moves per each player + 1

HeuristicAgent heuristic;

vector<BoardState> get_next_states(BoardState& state)
{
	vector<BoardState> sl;
	int turn = state.turn + 1;

	for(int i=0; i<BS; i++) {
		for(int j=0; j<BS; j++) {
			if(state[i][j] == 0) {
				BoardState new_state = BoardState(state.board_size, turn, i, j);
				new_state.board = state.board;
				new_state[i][j] = turn;
				sl.push_back(new_state);
			}
		}
	}

	return sl;
}


vector<Board> preproc_board(Board& board, int turn)
{
	int frame = INPUT_FRAME_NUM;
	vector<Board> s(frame, vector<vector<int> > (BS, vector<int>(BS, 0)));
	for(int fn=0; fn<(frame-1)/2; fn++) {
		for(int i=0; i<BS; i++) {
			for(int j=0; j<BS; j++) {
				if(board[i][j] > 0 && board[i][j]%2 == turn%2 && board[i][j] <= turn - fn*2) {
					s[fn][i][j] = 1;
				}
			}
		}
	}
	for(int fn=0; fn<(frame-1)/2; fn++) {
		for(int i=0; i<BS; i++) {
			for(int j=0; j<BS; j++) {
				if(board[i][j] > 0 && board[i][j]%2 != turn%2 && board[i][j] <= turn - fn*2) {
					s[fn + (frame-1)/2][i][j] = 1;
				}
			}
		}
	}

	if(turn%2 == 0) {
		s[frame-1] = vector<vector<int> > (BS, vector<int>(BS, 0));
	} else {
		s[frame-1] = vector<vector<int> > (BS, vector<int>(BS, 1));
	}

	return s;
}

Board dihedral_reflection_rotation(int i, Board x)
{
	function<Board(Board&)> fliplr = [](Board& x)->Board{
		int bs = (int)x.size();
		Board ret = vector<vector<int> > (bs, vector<int>(bs, 0));
		for(int ii=0; ii<bs; ii++) {
			for(int jj=0; jj<bs; jj++) {
				ret[ii][jj] = x[ii][bs-jj-1];
			}
		}
		return ret;
	};
	function<Board(Board&)> rot90 = [](Board& x)->Board{
		int bs = (int)x.size();
		Board ret = vector<vector<int> > (bs, vector<int>(bs, 0));
		for(int ii=0; ii<bs; ii++) {
			for(int jj=0; jj<bs; jj++) {
				ret[bs-jj-1][ii] = x[ii][jj];
			}
		}
		return ret;
	};

	if(i > 0) {
		if(i > 4) {
			x = fliplr(x);
			i -= 4;
		}
		for(int j=0; j<i; j++) {
			x = rot90(x);
		}
	} else if(i < 0) {
		int ii = -i;
		if(ii > 4) {
			ii -= 4;
		}
		for(int j=0; j<4-ii; j++) {
			x = rot90(x);
		}

		if(i < -4) {
			x = fliplr(x);
		}
	}
	return x;
}

vector<vector<double> > dihedral_reflection_rotation(int i, vector<vector<double> > x)
{
	typedef vector<vector<double> > VVD;
	function<VVD(VVD&)> fliplr = [](VVD& x)->VVD{
		int bs = (int)x.size();
		VVD ret = vector<vector<double> > (bs, vector<double>(bs, 0));
		for(int ii=0; ii<bs; ii++) {
			for(int jj=0; jj<bs; jj++) {
				ret[ii][jj] = x[ii][bs-jj-1];
			}
		}
		return ret;
	};
	function<VVD(VVD&)> rot90 = [](VVD& x)->VVD{
		int bs = (int)x.size();
		VVD ret = vector<vector<double> > (bs, vector<double>(bs, 0));
		for(int ii=0; ii<bs; ii++) {
			for(int jj=0; jj<bs; jj++) {
				ret[bs-jj-1][ii] = x[ii][jj];
			}
		}
		return ret;
	};

	if(i > 0) {
		if(i > 4) {
			x = fliplr(x);
			i -= 4;
		}
		for(int j=0; j<i; j++) {
			x = rot90(x);
		}
	} else if(i < 0) {
		int ii = -i;
		if(ii > 4) {
			ii -= 4;
		}
		for(int j=0; j<4-ii; j++) {
			x = rot90(x);
		}

		if(i < -4) {
			x = fliplr(x);
		}
	}
	return x;
}




PV_pair evaluate_with_network(BoardState& state, vector<BoardState>& state_list)
{
	int i = rand()%8 + 1;
	Board board = dihedral_reflection_rotation(i, state.board);
	int turn = state.turn;
	vector<Board> s = preproc_board(board, turn);

	pair<vector<vector<double> >, double> pv = network.get_output(s);
	auto p = pv.first;
	double v = pv.second;
	p = dihedral_reflection_rotation(-i, p);
	map<BoardState, double> p_dict;
	for(auto& new_state : state_list) {
		int r = new_state.last_row;
		int c = new_state.last_col;
		p_dict[new_state] = p[r][c];
	}
	return make_pair(p_dict, v);
}



PV_pair evaluate_with_random(BoardState& state, vector<BoardState>& state_list)
{
	double v = (rand()%2000)/1000.0 - 1;
	map<BoardState, double> p_dict;
	double p_sum = 0;
	for(auto& new_state : state_list) {
		int r = new_state.last_row;
		int c = new_state.last_col;
		double p = (rand()%1000)/1000.0;
		p_dict[new_state] = p;
		p_sum += p;
	}

	for(auto& p : p_dict) {
		p.second /= p_sum;
	}

	return make_pair(p_dict, v);
}



PV_pair evaluate_with_heuristic(BoardState& state, vector<BoardState>& state_list)
{
	return heuristic.evaluate(state, state_list);
}



Node::Node(
	BoardState s, 
	PV_pair (*f) (BoardState& board_state, vector<BoardState>& state_list), 
	Node* p
)
{
	evaluate = f;
	parent = p;
	state = s;
	N = 0;
	N_sum = 0;
	Q = 0;
	W = 0;
	P = 0;
	U = 0;
	selected_child = NULL;
}

void Node::search()
{
	Node* max_child = select();
	if(max_child == this) {
		max_child->expand();
	} else {
		max_child->search();
	}
}

vector<double> Dirichlet(double alpha, int size)
{
	default_random_engine generator;
	gamma_distribution<double> distribution(alpha, 1);
	vector<double> noise = vector<double>(size, 0);
	double sum = 0;
	for(int i=0; i<size; i++) {
		noise[i] = distribution(generator);
		sum += noise[i];
	}
	for(int i=0; i<size; i++) {
		noise[i] /= sum;
	}

	return noise;
}

Node* Node::select()
{
	double p, u;
	Node* max_child = this;
	
	if((int)child_list.size() == 0)
		return max_child;

	double QU_max = -DBL_MIN;
	const double constant = C_PUCT * sqrt(N_sum);
	vector<double> noise = Dirichlet(DIR_ALPHA, (int)child_list.size());
	int idx = 0;
	for(auto& child : child_list) {
		if(parent == NULL) {
			p = (1-EPSILON)*(child->P) + EPSILON*noise[idx++];
		} else {
			p = (child->P);
		}
		u = p * constant / (1 + (child->N));
		child->U = u;
		double QU = child->Q + u;
		if(QU_max < QU) {
			QU_max = QU;
			max_child = child;
		}
	}
	return max_child;
}

void Node::expand()
{
	if(is_game_ended(state.board)) {
		vector<BoardState> emp(0);
		double v = evaluate(state, emp).second;
		if(parent != NULL) {
			parent->backup(v, this);
		}
		return;
	}

	vector<BoardState> state_list = get_next_states(state);
	PV_pair pv = evaluate(state, state_list);
	Dict p = pv.first;
	double v = pv.second;
	for(auto& state : state_list) {
		Node* new_node = new Node(state, evaluate, this);
		child_list.push_back(new_node);
		new_node->P = p[state];
	}
	if(parent != NULL) {
		parent->backup(v, this);
	}	
}

void Node::backup(double v, Node* child)
{
	child->N += 1;
	N_sum++;
	child->W += v;
	child->Q = child->W / child->N;
	if(parent != NULL) {
		parent->backup(v, this);
	}
}

pair<map<Node*, long double>, long double> Node::get_pi(double t)
{
	map<Node*, long double> pi;
	long double N_s = 1e-9;
	for(auto& n : child_list) {
		pi[n] = powl((long double)n->N, (long double)1.0/t);
		N_s += pi[n];
	}

	for(auto& n : pi) {
		n.second /= N_s;
	}

	return make_pair(pi, N_s);
}

Node* Node::play(double t)
{
	pair<map<Node*, long double>, long double> pi_n = get_pi(t);
	map<Node*, long double> pi = pi_n.first;
	long double N_sum = pi_n.second;
	vector<pair<long double, Node*> > N_list;
	for(auto& n : pi) {
		N_list.push_back(make_pair(n.second, n.first));
	}
	for(int i=1; i<(int)N_list.size(); i++) {
		N_list[i].first += N_list[i-1].first;
	}
	long double r = rand() / (long double)RAND_MAX;
	for(int i=0; i<(int)N_list.size(); i++) {
		if(N_list[i].first >= r) {
			return N_list[i].second;
		}
	}

	printf("Exception on \'play\' %d\n", (int)child_list.size());
	printf("Exception on \'play\' %d\n", (int)N_list.size());
	printf("Exception on \'play\' %d\n", (int)pi.size());

	return N_list[-1].second;
}

void Node::clear()
{
	for(auto& child : child_list) {
		child->clear();
	}
	delete(this);
}



MCTS::MCTS(
	int board_size, 
	PV_pair (*evaluate) (BoardState& board_state, vector<BoardState>& state_list)
)
{
	root = new Node(BoardState(board_size, 0), evaluate);
	//network = Network(BS, 5, 9, false); //FIXME
}

void MCTS::search(Node* node)
{
	if(node==NULL) {
		root->search();
	} else {
		node->search();
	}
}

Node* MCTS::play(Node* node, double t)
{
	Node* next_node = node->play(t);
	node->selected_child = next_node;
	return next_node;
}

