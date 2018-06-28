#include "play.h"

#include "gomoku.h"
#include "random_agent.h"
#include "heuristic_agent.h"
#include "mcts_agent.h"

#include <stdlib.h>
#include <time.h>

void play()
{
	srand((unsigned)time(NULL));

	//RandomAgent AgentA;
	//RandomAgent AgentB;
	HeuristicAgent AgentA;
	HeuristicAgent AgentB;
	//MCTSAgent AgentA;
	//MCTSAgent AgentB;
	
	/*
	bool draw_flag = true;
	Gomoku gomoku(BOARD_SIZE, N_IN_A_ROW);
	int turn = 0;
	BoardState board_state = gomoku.board;

	while(!gomoku.is_game_ended() && board_state.turn != BOARD_SIZE*BOARD_SIZE) {
		printf("%d\n",board_state.turn);
		board_state.print();
		if(board_state.turn%2 == 0) {
			board_state = AgentA.play(board_state);
		} else {
			board_state = AgentB.play(board_state);
		}
		gomoku.board = board_state;

		if(gomoku.is_game_ended()) {
			board_state.print();
			if(board_state.turn%2*2-1 == 1) {
				printf("X wins\n");
			} else {
				printf("O wins\n");
			}
			draw_flag = false;
			break;
		}
	}
	if(draw_flag) {
		board_state.print();
		printf("draw\n");
	}
	*/

	///*
	int x_count = 0;
	int o_count = 0;
	int draw_count = 0;

	for(int i=0; i<100; i++) {
		if(i%10==0) printf("%d\n",i);
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
	}
	printf("%d %d %d\n\n",x_count, o_count, draw_count);
	//*/
}
