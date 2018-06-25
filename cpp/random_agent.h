#ifndef __RANDOM_AGENT__
#define __RANDOM_AGENT__

#include "gomoku.h"

class RandomAgent
{
	public:
		RandomAgent() {};
		BoardState play(BoardState board_state);
};

#endif
