#ifndef __MCTS_AGENT__
#define __MCTS_AGENT__

#include "gomoku.h"

const int MCTS_SEARCH_NUM = 128;//256;
const double TEMPER_EPS = 2e-1;
const double TEMPERATURE = TEMPER_EPS;

class MCTSAgent
{
	public:
		MCTSAgent() {};
		BoardState play(BoardState board_state);
};

#endif
