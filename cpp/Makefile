CC = g++
CFLAGS = -std=c++11

all: main

main: main.o gomoku.o random_agent.o heuristic_agent.o play.o
	$(CC) $(CFLAGS) -o main main.o gomoku.o random_agent.o heuristic_agent.o play.o
	rm *.o

main.o: gomoku.h random_agent.h heuristic_agent.h play.h main.cpp
gomoku.o: gomoku.h gomoku.cpp
random_agent.o: random_agent.h random_agent.cpp
heuristic_agent.o: heuristic_agent.h heuristic_agent.cpp
play.o: play.h play.cpp

run: main main.cpp
	./main

clean:
	rm main
	rm *.o
