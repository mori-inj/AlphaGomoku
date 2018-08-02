#include "train.h"

#include "params.h"
#include "gomoku.h"
#include "random_agent.h"
#include "mcts_agent.h"
#include "heuristic_agent.h"
#include "network.h"

#include <stdlib.h>
#include <time.h>
#include <ctime>
#include <vector>
#include <algorithm>

using namespace std;


extern Network network;

void train()
{
	srand((unsigned)time(NULL));

	network = Network(BOARD_SIZE, 5, 9, true);

	
	for(int iteration=0; iteration<SELF_PLAY_NUM; iteration++) {
		printf("========== iter: %d ==========\n",iteration);

		vector<vector<Board> > input_list;
		vector<vector<vector<double> > > pi_list;
		vector<double> z_list;

		int game = 0;
		while((int)input_list.size() < 2*BATCH_SIZE) {
			time_t t = time(0);
			tm* now = localtime(&t);
			if(game % GAME_PRINT == 0) {
				printf("game:  %d  data:  %d  %d-%d-%d %d:%d:%d\n",game,(int)input_list.size(),\
						now->tm_year + 1900,now->tm_mon + 1,now->tm_mday,now->tm_hour,now->tm_min,now->tm_sec);
			}
			game++;

			MCTSAgent mcts_agent(MCTS_SIM_NUM);
			BoardState board_state(BOARD_SIZE, 0);

			int turn_cnt = 0;
			while(1) {
				turn_cnt++;
				
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
		}
		
		vector<int> index;	
		int len = (int)input_list.size();
		for(int i=0; i<len; i++){
			index.push_back(i);
		}

		for(int i=0; i<len*10; i++) {
			int s = rand() % len;
			int e = rand() % len;
			int temp = index[s];
			index[s] = index[e];
			index[e] = temp;
		}
		printf("data size: %d\n",(int)index.size());
		
		vector<vector<Board> > input_;
		vector<vector<vector<double> > > pi_;
		vector<double> z_;

		for(int i=0; i<BATCH_SIZE; i++) {
			int idx = index[i];
			input_.push_back(input_list[idx]);
			pi_.push_back(pi_list[idx]);
			z_.push_back(z_list[idx]);
		}

		network.train(input_, pi_, z_, TRAIN_ITER, PRINT_ITER);
		network.wait_training();


		int x_count = 0;
		int o_count = 0;
		int draw_count = 0;

		for(int i=0; i<GAME_NUM; i++) {
			if(i % GAME_PRINT == 0) {
				printf("%d  %d %d %d\n",i,x_count,o_count,draw_count);
			}
			RandomAgent AgentA;
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
		printf("win rate: %d(random) %d(mcts) %d\n\n",x_count, o_count, draw_count);

		x_count = 0;
		o_count = 0;
		draw_count = 0;

		for(int i=0; i<GAME_NUM; i++) {
			if(i % GAME_PRINT == 0) {
				printf("%d  %d %d %d\n",i,x_count,o_count,draw_count);
			}
			RandomAgent AgentB;
			MCTSAgent AgentA;

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
		printf("win rate: %d(mcts) %d(random) %d\n\n",x_count, o_count, draw_count);


	}

}
