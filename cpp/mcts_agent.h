#ifndef __MCTS_AGENT__
#define __MCTS_AGENT__

#include "gomoku.h"

#include "mcts.h"


class MCTSAgent
{
	public:
		MCTSAgent();
		MCTSAgent(int msn, double te);
		MCTS mcts;
		int MCTS_SEARCH_NUM;
		double TEMPER_EPS;
		double TEMPERATURE;
		BoardState play(BoardState board_state);
		pair<vector<vector<double> >, BoardState> get_pi_and_play(BoardState board_state);
		vector<vector<double> > get_pi();
		void clear();
};

#endif
