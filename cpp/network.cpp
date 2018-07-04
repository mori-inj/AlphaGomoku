#include "network.h"

#include <stdlib.h>
#include <string.h>

Network::Network(int bs, int ifn, int rn, bool it)
{
	board_size = bs;
	input_frame_num = ifn;
	residual_num = rn;
	is_trainable = it;

	system("rm con_*");
	system("touch con_python_enable");
	char str[2048] = "";
	//sprintf(str,"python3 -c \"from Network import *; network = Network(board_size = %d, input_frame_num = %d, residual_num = %d, is_trainable=%s)\" &", bs,ifn, rn, it?"True":"False");
	sprintf(str,"python3 -c \"from Network import *; network = Network(board_size = %d, input_frame_num = %d, residual_num = %d, is_trainable=True)\" &", bs,ifn, rn);
	system(str);

	FILE* fp;
	while(!(fp = fopen("con_network_ready","r"))) {
		printf("\rinitializing network");
	}
	printf("\ninitialized\n");
	fclose(fp);
	system("rm con_network_ready");

}

pair<vector<vector<double> >, double> Network::get_output(vector<Board>& s)
{
	FILE* fp = fopen("con_network_input.txt", "w");
	for(int f=0; f<(int)s.size(); f++) {
		for(int i=0; i<board_size; i++) {
			for(int j=0; j<board_size; j++) {
				fprintf(fp, "%d ",s[f][i][j]);
			}
			fprintf(fp, "\n");
		}
		fprintf(fp, "\n");
	}
	fclose(fp);
	while(!(fp = fopen("con_network_output.txt","r")));
	auto P = vector<vector<double> > (board_size, vector<double>(board_size, 0.0));
	double V;
	for(int i=0; i<board_size; i++) {
		for(int j=0; j<board_size; j++) {
			fscanf(fp, "%lf", &P[i][j]);
		}
	}
	fscanf(fp, "%lf", &V);
	fclose(fp);
	system("rm con_network_output.txt");

	return make_pair(P,V);
}
