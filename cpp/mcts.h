#ifndef __MCTS__
#define __MCTS__

#include <vector>
#include <map>
#include <tuple>
#include "gomoku.h"

using namespace std;

const int BS = BOARD_SIZE;
const double C_PUCT = 5;
const double EPSILON = 0.25;
const double DIR_ALPHA = 0.5;

const bool IS_TRAINABLE = false;
//input_frame_num = 5 means, past 2 mover per each player + 1

typedef tuple<int, double, double, double, double> NQWPU_type;
typedef map<BoardState, double> Dict;
typedef pair<Dict, double> PV_pair;
vector<BoardState> get_next_states(BoardState& state);
//vector<Board> preproc_board(Board& board, int turn);
Board dihedral_reflection(int i, Board& x);
//PV_pair evaluate_with_network(BoardState& state, vector<BoardState>& state_list);
PV_pair evaluate_with_heuristic(BoardState& state, vector<BoardState>& state_list);

class Node
{
	public:
		Node(
			BoardState s, 
			PV_pair (*f) (BoardState& board_state, vector<BoardState>& state_list), 
			Node* p=NULL
		);
		PV_pair (*evaluate) (BoardState& board_state, vector<BoardState>& state_list);
		Node* parent;
		BoardState state;
		vector<Node*> child_list;
		int N_sum;
		
		int N;
		double Q;
		double W;
		double P;
		double U;

		/*
		map<Node*, tuple<int, double, double, double, double> > NQWPU;
		int& N(Node* child) { return get<0>(NQWPU[child]); }
		double& Q(Node* child) { return get<1>(NQWPU[child]); }
		double& W(Node* child) { return get<2>(NQWPU[child]); }
		double& P(Node* child) { return get<3>(NQWPU[child]); }
		double& U(Node* child) { return get<4>(NQWPU[child]); }
		
		int& N(NQWPU_type& nqwpu) { return get<0>(nqwpu); }
		double& Q(NQWPU_type& nqwpu) { return get<1>(nqwpu); }
		double& W(NQWPU_type& nqwpu) { return get<2>(nqwpu); }
		double& P(NQWPU_type& nqwpu) { return get<3>(nqwpu); }
		double& U(NQWPU_type& nqwpu) { return get<4>(nqwpu); }
		*/

		/*
		map<Node*, int> N;
		map<Node*, double> Q;
		map<Node*, double> W;
		map<Node*, double> P;
		map<Node*, double> U;
		*/
		Node* selected_child;

		void search();
		Node* select();
		void expand();
		void backup(double v, Node* child);
		pair<map<Node*, long double>, long double> get_pi(double t);
		Node* play(double t);
};

class MCTS
{
	public:
		MCTS(
			int board_size, 
			PV_pair (*evaluate) (BoardState& board_state, vector<BoardState>& state_list)
		);
		Node* root;

		void search(Node* node=NULL);
		Node* play(Node* node, double t);
};

#endif
