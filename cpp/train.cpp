#include "train.h"

#include "gomoku.h"
#include "mcts_agent.h"
#include "heuristic_agent.h"
#include "network.h"

#include <stdlib.h>
#include <time.h>
#include <vector>
#include <algorithm>

using namespace std;

const int ITER = 1000;

const int MCTS_SEARCH_NUM = 2;//150;
const int SELF_PLAY_NUM = 2000; //number of games
const int AFTER_NUM = 100; // number of epochs to train after self play
const int SELF_PLAY_ITER = 10;
const int TRAIN_ITER = 500;
const int PRINT_ITER = 100;

const int SELF_PLAY_BATCH_SIZE = 200;
const int TRAIN_BATCH_SIZE = 1000;

const double TEMPER_EPS = 2e-1;

extern Network network;

void train()
{
	srand((unsigned)time(NULL));

	network = Network(BOARD_SIZE, 5, 9, true);

	vector<vector<Board> > input_list;
	vector<vector<vector<double> > > pi_list;
	vector<double> z_list;
	
	for(int iteration=0; iteration<SELF_PLAY_NUM; iteration++) {
		MCTSAgent mcts_agent(MCTS_SEARCH_NUM, TEMPER_EPS);
		BoardState board_state(BOARD_SIZE, 0);
		printf("========== iter: %d ==========\n",iteration);

		while(1) {
			input_list.push_back(preproc_board(board_state.board, board_state.turn));
			auto ret = mcts_agent.get_pi_and_play(board_state);
			pi_list.push_back(ret.first);
			board_state = ret.second;

			if(is_game_ended(board_state.board)) {
				input_list.push_back(preproc_board(board_state.board, board_state.turn));
				pi_list.push_back(mcts_agent.get_pi());
				int nst = board_state.turn + 1;
				for(int i=0; i<nst; i++) {
					if(i%2*2-1 == board_state.turn%2*2-1) {
						z_list.push_back(1);
					} else {
						z_list.push_back(-1);
					}
				}
				break;
			} else if(board_state.turn == BOARD_SIZE * BOARD_SIZE) {
				input_list.push_back(preproc_board(board_state.board, board_state.turn));
				pi_list.push_back(mcts_agent.get_pi());
				int nst = board_state.turn + 1;
				for(int i=0; i<nst; i++) {
					z_list.push_back(0);
				}
				break;
			}

		}
		
		if(iteration % SELF_PLAY_ITER == 0) {
			int l = (int)input_list.size() - 9;
			vector<int> index;
			int i = rand() % max(1, (int)input_list.size() / SELF_PLAY_BATCH_SIZE);
			while(i<l) {
				index.push_back(i);
				i += rand() % (max(2, (int)input_list.size() / SELF_PLAY_BATCH_SIZE)-1)+1; 
			}
			while(i<(int)input_list.size()) {
				index.push_back(i);
				i++;
			}
			
			int len = (int)index.size();
			for(int i=0; i<len*10; i++) {
				int s = rand() % len;
				int e = rand() % len;
				int temp = index[s];
				index[s] = index[e];
				index[e] = temp;
			}
			printf("data size: %d\n",(int)index.size());			
		}

		printf("%d %d %d\n",(int)input_list.size(), (int)pi_list.size(), (int)z_list.size());

		if(iteration % SELF_PLAY_ITER == 0) {
			network.train(input_list, pi_list, z_list, TRAIN_ITER, PRINT_ITER);
			network.wait_training();


			int x_count = 0;
			int o_count = 0;
			int draw_count = 0;

			for(int i=0; i<ITER; i++) {
				HeuristicAgent AgentA;
				MCTSAgent AgentB;

				Gomoku gomoku(BOARD_SIZE, N_IN_A_ROW);
				int turn = 0;
				bool draw_flag = true;
				BoardState board_state = gomoku.board;

				while(!gomoku.is_game_ended() && board_state.turn != BOARD_SIZE*BOARD_SIZE) {
					if(board_state.turn % 2 == 0) {
						board_state = AgentA.play(board_state);
					} else {
						board_state = AgentB.play(board_state);
					}
					gomoku.board = board_state;

					if(gomoku.is_game_ended()) {
						if(board_state.turn%2*2-1 == 1) {
							x_count++;
						} else {
							o_count++;
						}
						draw_flag = false;
						break;
					}
				}
				if(draw_flag) {
					draw_count++;
				}

				AgentA.clear();
				AgentB.clear();
			}
			printf("win rate: %d %d %d\n\n",x_count, o_count, draw_count);

		}
	}
	for(int iteration=0; iteration<AFTER_NUM; iteration++) {
		printf("========== iter: %d ============\n",iteration);
		int l = (int)input_list.size() - 9;
		vector<int> index;
		int i = rand() % max(1, (int)input_list.size() / SELF_PLAY_BATCH_SIZE);
		while(i<l) {
			index.push_back(i);
			i += rand() % (max(2, (int)input_list.size() / SELF_PLAY_BATCH_SIZE)-1)+1; 
		}
		while(i<(int)input_list.size()) {
			index.push_back(i);
			i++;
		}
		
		int len = (int)index.size();
		for(int i=0; i<len*10; i++) {
			int s = rand() % len;
			int e = rand() % len;
			int temp = index[s];
			index[s] = index[e];
			index[e] = temp;
		}

		network.train(input_list, pi_list, z_list, TRAIN_ITER, PRINT_ITER);
		network.wait_training();
	}
}
