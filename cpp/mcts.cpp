#include "mcts.h"

#include "heuristic_agent.h"

#include <math.h>
#include <cfloat>
#include <functional>
#include <random>

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


/*vector<Board> preproc_board(Board& board, int turn)
{
}
*/

Board dihedral_reflection(int i, Board& x)
{
	function<Board(Board&)> fliplr = [](Board& x)->Board{
		int bs = (int)x.size();
		Board ret = vector<vector<int> > (bs, vector<int>(bs, 0));
		for(int i=0; i<bs; i++) {
			for(int j=0; j<bs; j++) {
				ret[i][j] = x[i][bs-j-1];
			}
		}
		return ret;
	};
	function<Board(Board&)> rot90 = [](Board& x)->Board{
		int bs = (int)x.size();
		Board ret = vector<vector<int> > (bs, vector<int>(bs, 0));
		for(int i=0; i<bs; i++) {
			for(int j=0; j<bs; j++) {
				ret[i][j] = x[j][bs-i-1];
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

		if(i <- 4) {
			x = fliplr(x);
		}
	}
	
	return x;
}


/*
PV_pair evaluate_with_network(BoardState& board_state, vector<BoardState>& state_list)
{
}
*/


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
	N_sum = 0;
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
		NQWPU_type& nqwpu = NQWPU[child];

		if(parent == NULL) {
			p = (1-EPSILON)*P(nqwpu) + EPSILON*noise[idx++];
		} else {
			p = P(nqwpu);
		}
		u = p * constant / (1 + N(nqwpu));
		U(nqwpu) = u;
		double QU = Q(nqwpu) + u;
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
		NQWPU[new_node] = make_tuple(0, 0, 0, p[state], 0);
		/*
		N[new_node] = 0;
		Q[new_node] = 0;
		W[new_node] = 0;
		P[new_node] = p[state];
		U[new_node] = 0;
		*/
	}
	if(parent != NULL) {
		parent->backup(v, this);
	}	
}

void Node::backup(double v, Node* child)
{
	NQWPU_type& nqwpu = NQWPU[child];

	N(nqwpu) += 1;
	N_sum++;
	W(nqwpu) += v;
	Q(nqwpu) = W(nqwpu) / N(nqwpu);
	if(parent != NULL) {
		parent->backup(v, this);
	}
}

pair<map<Node*, long double>, long double> Node::get_pi(double t)
{
	map<Node*, long double> pi;
	long double N_s = 1e-9;
	for(auto& n : child_list) {
		pi[n] = powl((long double)N(n), (long double)1.0/t);
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

	printf("Exception on \'play\' %d\n", (int)NQWPU.size());
	printf("Exception on \'play\' %d\n", (int)N_list.size());
	printf("Exception on \'play\' %d\n", (int)pi.size());

	return N_list[-1].second;
}



MCTS::MCTS(
	int board_size, 
	PV_pair (*evaluate) (BoardState& board_state, vector<BoardState>& state_list)
)
{
	root = new Node(BoardState(board_size, 0), evaluate);
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

