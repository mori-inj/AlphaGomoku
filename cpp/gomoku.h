#ifndef __GOMOKU__
#define __GOMOKU__

#include <vector>

using namespace std;

const int BOARD_SIZE = 3;
const int N_IN_A_ROW = 3;

typedef vector<vector<int> > Board;

bool is_game_ended(Board& board);

class BoardState
{
	public:
		BoardState() {};
		BoardState(int bs, int t);
		BoardState(int bs, int t, int lr, int lc);
		int board_size;
		Board board;
		int turn;
		int last_row;
		int last_col;
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
		Gomoku(int bs, int nir);
		int turn;
		int BOARD_SIZE;
		int N_IN_A_ROW;
		BoardState board;
		bool is_game_ended();
		bool is_valid_input(int row, int col);
		void put_stone(int row, int col);
		void reset();
};

#endif
