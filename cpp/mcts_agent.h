#ifndef __MCTS_AGENT__
#define __MCTS_AGENT__

#include "gomoku.h"

#include "mcts.h"

const int MCTS_SEARCH_NUM = 128;//256;
const double TEMPER_EPS = 2e-1;
const double TEMPERATURE = TEMPER_EPS;

class MCTSAgent
{
	public:
		MCTS mcts;
		MCTSAgent();
		BoardState play(BoardState board_state);
		void clear();
};

#endif
