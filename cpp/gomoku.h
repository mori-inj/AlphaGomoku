#ifndef __GOMOKU__
#define __GOMOKU__

#include <vector>

using namespace std;

const int BOARD_SIZE = 3;
const int N_IN_A_ROW = 3;

class BoardState
{
	public:
		int board_size;
		vector<vector<int> > board;
		int turn;
		int last_row;
		int last_col;
		BoardState(int bs, int t);
		BoardState(int bs, int t, int lr, int lc);
		vector<int>& operator[] (const int index);
		inline bool operator< (const BoardState& that) const
		{
			for(int i=0; i<board_size; i++) {
				for(int j=0; j<board_size; j++) {
					if(board[i][j] < that.board[i][j])
						return true;
					else if(board[i][j] > that.board[i][j])
						return false;
				}
			}
			return false;
		};
		void print();
};

class Gomoku
{
	public:
		int turn;
		int BOARD_SIZE;
		int N_IN_A_ROW;
		BoardState board;
		Gomoku(int bs, int nir);
		bool is_game_ended();
		bool is_valid_input(int row, int col);
		void put_stone(int row, int col);
		void reset();
};

bool is_game_ended(vector<vector<int> >& board);

#endif
