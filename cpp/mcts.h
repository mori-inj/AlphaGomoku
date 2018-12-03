#ifndef __MCTS__
#define __MCTS__

#include <vector>
#include <map>
#include <tuple>
#include "gomoku.h"

using namespace std;

typedef map<BoardState, double> Dict;
typedef pair<Dict, double> PV_pair;
vector<BoardState> get_next_states(BoardState& state);
vector<Board> preproc_board(Board& board, int turn);
Board dihedral_reflection_rotation(int i, Board x);
vector<vector<double> > dihedral_reflection_rotation(int i, vector<vector<double> > x);
PV_pair evaluate_with_network(BoardState& state, vector<BoardState>& state_list);
PV_pair evaluate_with_constant(BoardState& state, vector<BoardState>& state_list);
PV_pair evaluate_with_random(BoardState& state, vector<BoardState>& state_list);
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

		Node* selected_child;

		void search();
		Node* select();
		void expand();
		void backup(double v, Node* child);
		pair<map<Node*, long double>, long double> get_pi(double t);
		Node* play(double t);

		void clear();
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
