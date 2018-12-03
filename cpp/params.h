#ifndef __PARAMS__
#define __PARAMS__

//gomoku
const int BOARD_SIZE = 3;//9;
const int N_IN_A_ROW = 3;//5;

//mcts
const double C_PUCT = 5;
const double EPSILON = 0;//0.1; //0.25;
const double DIR_ALPHA = 0.3; //0.5;

const int MCTS_SIM_NUM = 128;//1600;//800;//128;
const double TEMPER_EPS = 1;//1e-1;
const int TEMPER_THRS = 1;//2;

//network
const int INPUT_FRAME_NUM = 5;
const int RESIDUAL_NUM = 9;

//play
#define E_RANDOM 0
#define E_HEURISTIC 1
#define E_NETWORK 2

#define A_RANDOM 10
#define A_HEURISTIC 11
#define A_MCTS 12 // with EVALUATE
#define A_NETWORK 13


#define EVALUATE evaluate_with_constant
//#define EVALUATE evaluate_with_random
//#define EVALUATE evaluate_with_heuristic
//#define EVALUATE evaluate_with_network

//#define AA RandomAgent
//#define AA HeuristicAgent
#define AA MCTSAgent

#define BB RandomAgent
//#define BB HeuristicAgent
//#define BB MCTSAgent

const bool SINGLE_PLAY = false;

const int TOTAL_GAME_NUM = 20000;
const int TOTAL_GAME_PRINT = 200;

//train
const int SELF_PLAY_NUM = 2000;
const int TRAIN_ITER = 100;
const int PRINT_ITER = 30;

const int BATCH_SIZE = 512;
const int MINI_BATCH_SIZE = 32;

const int GAME_NUM = 10000;
const int GAME_PRINT = 1000;

#endif
