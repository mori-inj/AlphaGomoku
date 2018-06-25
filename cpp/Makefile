CC = g++
CFLAGS = -std=c++11

all: main

main: main.o play.o gomoku.o heuristic_agent.o
	$(CC) $(CFLAGS) -o main main.o play.o gomoku.o heuristic_agent.o
	rm *.o

main.o: play.h gomoku.h heuristic_agent.h main.cpp
play.o: play.h play.cpp
gomoku.o: gomoku.h gomoku.cpp
heuristic_agent.o: heuristic_agent.h heuristic_agent.cpp

run: main main.cpp
	./main

clean:
	rm main
	rm *.o

