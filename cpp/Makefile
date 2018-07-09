CC = g++
CFLAGS = -O3 -std=c++11
CXXFLAGS = -O3 -std=c++11

all: main

main: main.o gomoku.o random_agent.o heuristic_agent.o mcts.o mcts_agent.o network.o play.o train.o
	$(CC) $(CFLAGS) -o main main.o gomoku.o random_agent.o heuristic_agent.o mcts.o mcts_agent.o network.o play.o train.o
	rm *.o

main.o: gomoku.h random_agent.h heuristic_agent.h mcts.h mcts_agent.h network.h play.h train.h main.cpp
gomoku.o: gomoku.h gomoku.cpp
random_agent.o: random_agent.h random_agent.cpp
heuristic_agent.o: heuristic_agent.h heuristic_agent.cpp
mcst.o: mcts.h mcts.cpp
mcts_agent.o: mcts_agent.h mcts_agent.cpp
network.o: network.h network.cpp
play.o: play.h play.cpp
train.o: train.h train.cpp

run: main main.cpp
	./main
	rm main

clean:
	rm main
	rm *.o

