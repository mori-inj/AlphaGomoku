#ifndef __NETWORK__
#define __NETWORK__

#include "gomoku.h"

class Network
{
	public:
		Network() {};
		Network(int bs, int ifn, int rn, bool it);
		int board_size;
		int input_frame_num;
		int residual_num;
		bool is_trainable;
		
		//void train(); TODO
		//bool is_training();
		//void wait_training();
		pair<vector<vector<double> >, double> get_output(vector<Board>& s);
};

#endif
