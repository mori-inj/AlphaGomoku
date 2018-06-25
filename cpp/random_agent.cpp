#include "random_agent.h"

#include <stdlib.h>

BoardState RandomAgent::play(BoardState board_state)
{
	int row = rand() % BOARD_SIZE;
	int col = rand() % BOARD_SIZE;

	while(board_state[row][col] != 0) {
		row = rand() % BOARD_SIZE;
		col = rand() % BOARD_SIZE;
	}

	board_state.turn++;
	board_state[row][col] = board_state.turn;
	board_state.last_row = row;
	board_state.last_col = col;

	return board_state;
}
