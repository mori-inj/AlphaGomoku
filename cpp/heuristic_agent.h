#ifndef __HEURISTIC_AGENT__
#define __HEURISTIC_AGENT__

#include <vector>
#include <utility>
#include <map>
#include "gomoku.h"

using namespace std;

class HeuristicAgent
{
	public:
		HeuristicAgent() {};
		pair<map<BoardState, double>, double> evalutate(BoardState& board_state, vector<BoardState>& state_list);
		BoardState play(BoardState board_state);
};
#endif
