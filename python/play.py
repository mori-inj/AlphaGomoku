from Gomoku import *
from RandomAgent import RandomAgent as RandomAg
from HeuristicAgent import HeuristicAgent as HeuristicAg
from MCTSAgent import MCTSAgent as MCTSAg


if AgA == "random":
    AgentA = RandomAg()
elif AgA == "heuristic":
    AgentA = HeuristicAg()
elif AgA == "MCTS":
    AgentA = MCTSAg()

if AgB == "random":
    AgentB = RandomAg()
elif AgB == "heuristic":
    AgentB = HeuristicAg()
elif AgB == "MCTS":
    AgentB = MCTSAg()


if SINGLE_PLAY:
    gomoku = Gomoku(BOARD_SIZE, N_IN_A_ROW)
    turn = 0
    board_state = gomoku.board

    while not gomoku.is_game_ended() and board_state.turn != BOARD_SIZE*BOARD_SIZE:
        print(board_state.turn)
        print(board_state)
        if board_state.turn % 2 == 0:
            board_state = AgentA.play(board_state)
        else:
            board_state = AgentB.play(board_state)
        gomoku.board = board_state
        if gomoku.is_game_ended():
            print(board_state)
            if board_state.turn%2*2-1 == 1:
                print("X wins")
            else:
                print("O wins")
            break
    else:
        print(board_state)
        print("draw")

else:
    x_count = 0
    o_count = 0
    draw_count = 0

    for i in range(TOTAL_GAME_NUM):
        if i % TOTAL_GAME_PRINT == 0:
            print(i, "  ", x_count, o_count, draw_count)

        gomoku = Gomoku(BOARD_SIZE, N_IN_A_ROW)
        turn = 0
        board_state = gomoku.board

        while not gomoku.is_game_ended() and board_state.turn != BOARD_SIZE*BOARD_SIZE:
            if board_state.turn % 2 == 0:
                board_state = AgentA.play(board_state)
            else:
                board_state = AgentB.play(board_state)
            gomoku.board = board_state
            if gomoku.is_game_ended():
                if board_state.turn%2*2-1 == 1:
                    x_count += 1
                else:
                    o_count += 1
                break
        else:
             draw_count += 1


    print(x_count, o_count, draw_count)
