#include "heuristic_agent.h"

#include "params.h"

#include <stdlib.h>
#include <limits.h>
#include <vector>
#include <algorithm>

using namespace std;

const int dx[8] = {1, 1, 0, -1, -1, -1, 0, 1};
const int dy[8] = {0, -1, -1, -1, 0, 1, 1, 1};

pair<map<BoardState, double>, double> HeuristicAgent::evaluate(BoardState& board_state, vector<BoardState>& state_list)
{
	int idx = 0;
	int cnt_advtg = 0;

	int turn = board_state.turn + 1;
	vector<vector<int> > pos_score(BOARD_SIZE, vector<int>(BOARD_SIZE, 0));
	vector<vector<int> > neg_score(BOARD_SIZE, vector<int>(BOARD_SIZE, 0));
	vector<int> total_row(BOARD_SIZE*BOARD_SIZE, 0);
	vector<int> total_col(BOARD_SIZE*BOARD_SIZE, 0);

	for(int i=0; i<BOARD_SIZE; i++) {
		for(int j=0; j<BOARD_SIZE; j++) {
			if(board_state[i][j] != 0) continue;
			int old_board = board_state[i][j];

			board_state[i][j] = turn;

			if(is_game_ended(board_state.board)) {
				map<BoardState, double> p_dict;
				for(auto& new_state : state_list) {
					int r = new_state.last_row;
					int c = new_state.last_col;
					if(r==i && c==j)
						p_dict[new_state] = 1;
					else
						p_dict[new_state] = 0;
				}
				double v = 1;

				board_state[i][j] = old_board;
				return make_pair(p_dict, v);
			}

			board_state[i][j] = old_board;
		}
	}

	for(int i=0; i<BOARD_SIZE; i++) {
		for(int j=0; j<BOARD_SIZE; j++) {
			if(board_state[i][j] != 0) {
				pos_score[i][j] = -1;
				neg_score[i][j] = 1;
			} else {
				pos_score[i][j] = 0;
				neg_score[i][j] = 0;
			}
		}
	}

	for(int row=0; row<BOARD_SIZE; row++) {
		for(int col=0; col<BOARD_SIZE; col++) {
			int ny = row;
			int nx = col;

			if(board_state[ny][nx] != 0) continue;
			int player = board_state[ny][nx]%2*2-1;

			for(int key=0; key<8; key++) {
				ny = row;
				nx = col;
				int cnt = 0;
				for(int i=0; i<N_IN_A_ROW-1; i++) {
					cnt++;
					nx += dx[key];
					ny += dy[key];

					if( !(0 <= nx && nx < BOARD_SIZE \
						&& 0 <= ny && ny < BOARD_SIZE)) {
						break;
					}
					if(board_state[ny][nx]%2*2-1 != player) {
						if(board_state[ny][nx]==0) {
							if(((turn%2==0 && player==-1) || (turn%2==1 && player==1))
								&& pos_score[ny][nx] < cnt) {
								pos_score[ny][nx] = cnt;
							}
							if(((turn%2==0 && player==1) || (turn%2==1 && player==-1))
								&& -neg_score[ny][nx] < cnt) {
								neg_score[ny][nx] = -cnt;
							}
						}
						break;
					}
				}
			}
		}
	}

	int maxv = 0;
	for(int i=0; i<BOARD_SIZE; i++) {
		for(int j=0; j<BOARD_SIZE; j++) {
			if(maxv < pos_score[i][j]) {
				maxv = pos_score[i][j];
			}
		}
	}

	int minv = 0;
	for(int i=0; i<BOARD_SIZE; i++) {
		for(int j=0; j<BOARD_SIZE; j++) {
			if(minv > neg_score[i][j]) {
				minv = neg_score[i][j];
			}
		}
	}

	
	if(-minv > 2) {
		int row = rand() % BOARD_SIZE;
		int col = rand() % BOARD_SIZE;
		while(board_state[row][col]!=0 || neg_score[row][col] != minv) {
			row = rand() % BOARD_SIZE;
			col = rand() % BOARD_SIZE;
		}
	} else {
		for(int i=0; i<BOARD_SIZE; i++) {
			for(int j=0; j<BOARD_SIZE; j++) {
				if(i < N_IN_A_ROW-1 || j < N_IN_A_ROW-1) {
					pos_score[i][j] -= N_IN_A_ROW - min(i,j) - 1;
					neg_score[i][j] += N_IN_A_ROW - min(i,j) - 1;
				} else if(i > BOARD_SIZE - N_IN_A_ROW || j > BOARD_SIZE - N_IN_A_ROW) {
					pos_score[i][j] -= N_IN_A_ROW - (BOARD_SIZE - max(i,j));
					neg_score[i][j] += N_IN_A_ROW - (BOARD_SIZE - max(i,j));
				}
			}
		}

		int total = INT_MIN;
		total_row[0] = BOARD_SIZE/2;
		total_col[0] = BOARD_SIZE/2;

		for(int i=0; i<BOARD_SIZE; i++) {
			for(int j=0; j<BOARD_SIZE; j++) {
				if(board_state[i][j]==0 && total < pos_score[i][j] - neg_score[i][j]) {
					total = pos_score[i][j] - neg_score[i][j];
					total_row[0] = i;
					total_col[0] = j;
				}
			}
		}

		idx = 0;
		cnt_advtg = 0;
		for(int i=0; i<BOARD_SIZE; i++) {
			for(int j=0; j<BOARD_SIZE; j++) {
				if(board_state[i][j]==0 && total == pos_score[i][j] - neg_score[i][j]) {
					total_row[idx] = i;
					total_col[idx] = j;
					idx++;
					if(pos_score[i][j] > -neg_score[i][j]) cnt_advtg++;
				}
			}
		}
	}
	
	double v = 0;
	if(idx != 0) v = (cnt_advtg / (double)idx);//*2-1;
	else if(is_game_ended(board_state.board)) {
		v = (board_state.turn%2==1);
	}
	else v = 0.5;
	v = 1-v;
	
	map<BoardState, double> p_dict;
	for(auto& new_state : state_list) {
		int r = new_state.last_row;
		int c = new_state.last_col;
		for(int i=0; i<idx; i++) {
			if(total_row[i]==r && total_col[i]==c) {
				p_dict[new_state] = 1.0/idx;
				break;
			} else {
				p_dict[new_state] = 0;
			}
		}
	}

	return make_pair(p_dict, v);
}

BoardState HeuristicAgent::play(BoardState board_state)
{
	int idx = 0;
	int final_row, final_col;

	int turn = board_state.turn + 1;
	vector<vector<int> > pos_score(BOARD_SIZE, vector<int>(BOARD_SIZE, 0));
	vector<vector<int> > neg_score(BOARD_SIZE, vector<int>(BOARD_SIZE, 0));
	vector<int> total_row(BOARD_SIZE*BOARD_SIZE, 0);
	vector<int> total_col(BOARD_SIZE*BOARD_SIZE, 0);

	for(int i=0; i<BOARD_SIZE; i++) {
		for(int j=0; j<BOARD_SIZE; j++) {
			if(board_state[i][j] != 0) continue;
			int old_board = board_state[i][j];

			board_state[i][j] = turn;
			board_state.turn = turn;

			if(is_game_ended(board_state.board)) {
				return board_state;
			}

			board_state[i][j] = old_board;
		}
	}

	for(int i=0; i<BOARD_SIZE; i++) {
		for(int j=0; j<BOARD_SIZE; j++) {
			if(board_state[i][j] != 0) {
				pos_score[i][j] = -1;
				neg_score[i][j] = 1;
			} else {
				pos_score[i][j] = 0;
				neg_score[i][j] = 0;
			}
		}
	}

	for(int row=0; row<BOARD_SIZE; row++) {
		for(int col=0; col<BOARD_SIZE; col++) {
			int ny = row;
			int nx = col;

			if(board_state[ny][nx] != 0) continue;
			int player = board_state[ny][nx]%2*2-1;

			for(int key=0; key<8; key++) {
				ny = row;
				nx = col;
				int cnt = 0;
				for(int i=0; i<N_IN_A_ROW-1; i++) {
					cnt++;
					nx += dx[key];
					ny += dy[key];

					if( !(0 <= nx && nx < BOARD_SIZE \
						&& 0 <= ny && ny < BOARD_SIZE)) {
						break;
					}
					if(board_state[ny][nx]%2*2-1 != player) {
						if(board_state[ny][nx]==0) {
							if(((turn%2==0 && player==-1) || (turn%2==1 && player==1))
								&& pos_score[ny][nx] < cnt) {
								pos_score[ny][nx] = cnt;
							}
							if(((turn%2==0 && player==1) || (turn%2==1 && player==-1))
								&& -neg_score[ny][nx] < cnt) {
								neg_score[ny][nx] = -cnt;
							}
						}
						break;
					}
				}
			}
		}
	}

	int maxv = 0;
	for(int i=0; i<BOARD_SIZE; i++) {
		for(int j=0; j<BOARD_SIZE; j++) {
			if(maxv < pos_score[i][j]) {
				maxv = pos_score[i][j];
			}
		}
	}

	int minv = 0;
	for(int i=0; i<BOARD_SIZE; i++) {
		for(int j=0; j<BOARD_SIZE; j++) {
			if(minv > neg_score[i][j]) {
				minv = neg_score[i][j];
			}
		}
	}

	
	if(-minv > 2) {
		int row = rand() % BOARD_SIZE;
		int col = rand() % BOARD_SIZE;
		while(board_state[row][col]!=0 || neg_score[row][col] != minv) {
			row = rand() % BOARD_SIZE;
			col = rand() % BOARD_SIZE;
		}
	} else {
		for(int i=0; i<BOARD_SIZE; i++) {
			for(int j=0; j<BOARD_SIZE; j++) {
				if(i < N_IN_A_ROW-1 || j < N_IN_A_ROW-1) {
					pos_score[i][j] -= N_IN_A_ROW - min(i,j) - 1;
					neg_score[i][j] += N_IN_A_ROW - min(i,j) - 1;
				} else if(i > BOARD_SIZE - N_IN_A_ROW || j > BOARD_SIZE - N_IN_A_ROW) {
					pos_score[i][j] -= N_IN_A_ROW - (BOARD_SIZE - max(i,j));
					neg_score[i][j] += N_IN_A_ROW - (BOARD_SIZE - max(i,j));
				}
			}
		}

		int total = INT_MIN;
		total_row[0] = BOARD_SIZE/2;
		total_col[0] = BOARD_SIZE/2;

		for(int i=0; i<BOARD_SIZE; i++) {
			for(int j=0; j<BOARD_SIZE; j++) {
				if(board_state[i][j]==0 && total < pos_score[i][j] - neg_score[i][j]) {
					total = pos_score[i][j] - neg_score[i][j];
					total_row[0] = i;
					total_col[0] = j;
				}
			}
		}

		idx = 0;
		for(int i=0; i<BOARD_SIZE; i++) {
			for(int j=0; j<BOARD_SIZE; j++) {
				if(board_state[i][j]==0 && total == pos_score[i][j] - neg_score[i][j]) {
					total_row[idx] = i;
					total_col[idx] = j;
					idx++;
				}
			}
		}

		idx = rand() % idx;
		final_row = total_row[idx];
		final_col = total_col[idx];
	}

	board_state[final_row][final_col] = turn;
	board_state.turn = turn;

	return board_state;
}
