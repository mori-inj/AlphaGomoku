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
	sprintf(str,"python3 -c \"from Network import *; network = Network(board_size = %d, input_frame_num = %d, residual_num = %d, is_trainable=%s)\" &", bs,ifn, rn, it?"True":"False");
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
	FILE* fp = fopen("con_network_input.txt_", "w");
	for(int f=0; f<input_frame_num; f++) {
		for(int i=0; i<board_size; i++) {
			for(int j=0; j<board_size; j++) {
				fprintf(fp, "%d ",s[f][i][j]);
			}
			fprintf(fp, "\n");
		}
		fprintf(fp, "\n");
	}
	fclose(fp);
	system("mv con_network_input.txt_ con_network_input.txt");

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

void Network::train(
	vector<vector<Board> > X,
	vector<vector<vector<double> > > P,
	vector<double> Z,
	int iter,
	int print_iter
)
{
	const int data_num = (int)X.size();
	if((int)P.size() != data_num || (int)Z.size() != data_num) {
		printf("can not train\n");
		return;
	}

	FILE* fp = fopen("con_train_data.txt_","w");
	fprintf(fp, "%d %d %d\n",data_num, iter, print_iter);
	for(int n=0; n<data_num; n++) {
		for(int f=0; f<input_frame_num; f++) {
			for(int i=0; i<board_size; i++) {
				for(int j=0; j<board_size; j++) {
					fprintf(fp, "%d ", X[n][f][i][j]);
				}
				fprintf(fp, "\n");
			}
			fprintf(fp, "\n");
		}
		for(int i=0; i<board_size; i++) {
			for(int j=0; j<board_size; j++) {
				fprintf(fp, "%lf ", P[n][i][j]);
			}
			fprintf(fp, "\n");
		}
		fprintf(fp, "%lf\n",Z[n]);
		fprintf(fp, "\n");
	}
	fclose(fp);
	system("mv con_train_data.txt_ con_train_data.txt");
}

bool Network::is_training()
{
	FILE* fp = fopen("con_network_training","r");
	if(fp==NULL) {
		fclose(fp);
		return false;
	}
	fclose(fp);
	return true;
}

void Network::wait_training()
{
	FILE* fp;
	while((fp = fopen("con_network_training","r"))) fclose(fp);
}
