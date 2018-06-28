CC = g++
CFLAGS = -std=c++11
CXXFLAGS = -std=c++11

all: main

main: main.o gomoku.o random_agent.o heuristic_agent.o mcts.o mcts_agent.o play.o
	$(CC) $(CFLAGS) -o main main.o gomoku.o random_agent.o heuristic_agent.o mcts.o mcts_agent.o play.o
	rm *.o

main.o: gomoku.h random_agent.h heuristic_agent.h mcts.h mcts_agent.h play.h main.cpp
gomoku.o: gomoku.h gomoku.cpp
random_agent.o: random_agent.h random_agent.cpp
heuristic_agent.o: heuristic_agent.h heuristic_agent.cpp
mcst.o: mcts.h mcts.cpp
mcts_agent.o: mcts_agent.h mcts_agent.cpp
play.o: play.h play.cpp

run: main main.cpp
	./main
	rm main

clean:
	rm main
	rm *.o

