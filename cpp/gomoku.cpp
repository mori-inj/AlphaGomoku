#include "gomoku.h"

#include <stdio.h>

BoardState::BoardState(int bs, int t)
{
	board_size = bs;
	board = vector<vector<int> >(bs, vector<int>(bs, 0));
	turn = t;
	last_row = -1;
	last_col = -1;
}

BoardState::BoardState(int bs, int t, int lr, int lc)
{
	board_size = bs;
	board = vector<vector<int> >(bs, vector<int>(bs, 0));
	turn = t;
	last_row = lr;
	last_col = lc;
}

vector<int>& BoardState::operator[] (const int index)
{
	return board[index];
}

void BoardState::print()
{
	for(int i=0; i<board_size; i++) {
		for(int j=0; j<board_size; j++) {
			if(board[i][j] == 0) {
				printf("| ");
			} else if(board[i][j]%2*2-1 == 1) {
				printf("|x");
			} else {
				printf("|o");
			}
		}
		printf("|\n");
	}
	printf("\n");
}



Gomoku::Gomoku(int bs, int nir) : board(bs, 0)
{
	turn = 0;
	this->BOARD_SIZE = bs;
	this->N_IN_A_ROW = nir;
}

bool Gomoku::is_game_ended()
{
	return ::is_game_ended(board.board);
}

bool Gomoku::is_valid_input(int row, int col)
{
	if( !(0 <= row && row < this->BOARD_SIZE \
		&& 0 <= col && col < this->BOARD_SIZE)) {
		return false;
	}
	if(board[row][col] != 0) {
		return false;
	}
	return true;
}

void Gomoku::put_stone(int row, int col)
{
	turn++;
	board[row][col] = turn;
}

void Gomoku::reset()
{
	turn = 0;
	board = BoardState(this->BOARD_SIZE, 0);
}




bool is_game_ended(Board& board)
{
	int turn = -1;
	int row = -1, col = -1;

	for(int i=0; i<BOARD_SIZE; i++) {
		for(int j=0; j<BOARD_SIZE; j++) {
			if(turn < board[i][j]) {
				turn = board[i][j];
				row = i;
				col = j;
			}
		}
	}
	if(turn==0) return false;
	const int dx[8] = {1, 1, 0, -1, -1, -1, 0, 1};
	const int dy[8] = {0, -1, -1, -1, 0, 1, 1, 1};
	int nx = col;
	int ny = row;
	int player = board[row][col]%2*2-1;

	for(int key=0; key<8; key++) {
		for(int i=0; i<N_IN_A_ROW; i++) {
			nx = col - i*dx[key];
			ny = row - i*dy[key];
			int j;
			for(j=0; j<N_IN_A_ROW; j++) {
				if(!((0 <= nx && nx < BOARD_SIZE) \
					&& (0<= ny && ny < BOARD_SIZE))) {
					break;
				}
				if(board[ny][nx] > 0 && board[ny][nx]%2*2-1 != player) {
					break;
				}
				if(board[ny][nx] == 0) {
					break;
				}
				ny += dy[key];
				nx += dx[key];
			}
			if(j == N_IN_A_ROW) {
				return true;
			}
		}
	}
	return false;			
}

bool is_same_board(BoardState& a, BoardState& b)
{
	for(int i=0; i<BOARD_SIZE; i++) {
		for(int j=0; j<BOARD_SIZE; j++) {
			if(a[i][j] != b[i][j]) {
				return false;
			}
		}
	}
	return true;
}

