from Gomoku import *
import random
import numpy as np

dx = [1, 1, 0, -1, -1, -1, 0, 1]
dy = [0, -1, -1, -1, 0, 1, 1, 1]

class HeuristicAgent:
    def __init__(self):
        pass

    def evaluate(self, board_state, state_list):
        turn = board_state.turn + 1 
        pos_score = np.zeros([BOARD_SIZE, BOARD_SIZE]).tolist()
        neg_score = np.zeros([BOARD_SIZE, BOARD_SIZE]).tolist() 
        total_row = np.zeros([BOARD_SIZE*BOARD_SIZE]).tolist()
        total_col = np.zeros([BOARD_SIZE*BOARD_SIZE]).tolist()


        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if abs(board_state[i][j]) > 1e-3:
                    continue
                old_board = board_state[i][j]

                board_state[i][j] = turn
                
                if is_game_ended(board_state.board):
                    p_dict = {}
                    for new_state in state_list:
                        r = new_state.last_row
                        c = new_state.last_col
                        if r==i and c==j:
                            p_dict[new_state] = 1
                        else:
                            p_dict[new_state] = 0
                    v = 1

                    board_state[i][j] = old_board
                    return p_dict, v
                
                board_state[i][j] = old_board
        
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if abs(board_state[i][j]) > 1e-3:
                    pos_score[i][j] = -1
                    neg_score[i][j] = 1
                else:
                    pos_score[i][j] = 0
                    neg_score[i][j] = 0



        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                ny = row
                nx = col
                
                if abs(board_state[ny][nx]) > 1e-3:
                    continue
                player = board_state[ny][nx]%2*2-1

                for key in range(8):
                    ny = row
                    nx = col
                    cnt = 0
                    for i in range(N_IN_A_ROW-1):
                        cnt += 1
                        nx = nx + dx[key]
                        ny = ny + dy[key]

                        if not ((0 <= nx < BOARD_SIZE) and (0 <= ny < BOARD_SIZE)):
                            break
                        if board_state[ny][nx]%2*2-1 is not player:
                            if board_state[ny][nx] == 0:
                                if (((turn%2==0 and player==-1) or (turn%2==1 and player==1)) and pos_score[ny][nx] < cnt):
                                    pos_score[ny][nx] = cnt
                                if (((turn%2==0 and player==1) or (turn%2==1 and player==-1)) and -neg_score[ny][nx] < cnt):
                                    neg_score[ny][nx] = -cnt
                            break
        
        maxv = np.amax(np.asarray(pos_score))
        minv = np.amin(np.asarray(neg_score))

        if -minv > 2:
            row = random.randrange(0, BOARD_SIZE)
            col = random.randrange(0, BOARD_SIZE)
            while abs(board_state[row][col]) > 1e-3 or neg_score[row][col] is not minv:
                row = random.randrange(0, BOARD_SIZE)
                col = random.randrange(0, BOARD_SIZE)
        else:
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if i < N_IN_A_ROW-1 or j < N_IN_A_ROW-1:
                        pos_score[i][j] -= N_IN_A_ROW - min(i,j) - 1
                        neg_score[i][j] += N_IN_A_ROW - min(i,j) - 1
                    elif i > BOARD_SIZE - N_IN_A_ROW or j > BOARD_SIZE - N_IN_A_ROW:
                        pos_score[i][j] -= N_IN_A_ROW - (BOARD_SIZE - max(i,j))
                        neg_score[i][j] += N_IN_A_ROW - (BOARD_SIZE - max(i,j))
            
            total = -987654321
            total_row[0] = BOARD_SIZE//2
            total_col[0] = BOARD_SIZE//2

            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if board_state[i][j]==0 and total < pos_score[i][j] - neg_score[i][j]:
                        total = pos_score[i][j] - neg_score[i][j]
                        total_row[0] = i
                        total_col[0] = j
                    
            idx = 0
            cnt_advtg = 0
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if board_state[i][j]==0 and total == pos_score[i][j] - neg_score[i][j]:
                        total_row[idx] = i
                        total_col[idx] = j
                        idx += 1
                        if pos_score[i][j] > -neg_score[i][j]:
                            cnt_advtg += 1
        if idx != 0:                
            v = (cnt_advtg / idx)*2-1
        elif is_game_ended(board_state.board):
            v = 1
        else:
            v = 0
        p_dict = {}
        for new_state in state_list:
            r = new_state.last_row
            c = new_state.last_col
            for i in range(idx):
                if total_row[i]==r and total_col[i]==c:
                    p_dict[new_state] = 1/idx
                    break
            else:
                p_dict[new_state] = 0

        return p_dict, v

        

    def play(self, board_state):
        turn = board_state.turn + 1 
        pos_score = np.zeros([BOARD_SIZE, BOARD_SIZE]).tolist()
        neg_score = np.zeros([BOARD_SIZE, BOARD_SIZE]).tolist() 
        total_row = np.zeros([BOARD_SIZE*BOARD_SIZE]).tolist()
        total_col = np.zeros([BOARD_SIZE*BOARD_SIZE]).tolist()


        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if abs(board_state[i][j]) > 1e-3:
                    continue
                old_board = board_state[i][j]

                board_state[i][j] = turn
                board_state.turn = turn
                
                if is_game_ended(board_state.board):
                    return board_state
                
                board_state[i][j] = old_board
        
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if abs(board_state[i][j]) > 1e-3:
                    pos_score[i][j] = -1
                    neg_score[i][j] = 1
                else:
                    pos_score[i][j] = 0
                    neg_score[i][j] = 0



        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                ny = row
                nx = col
                
                if abs(board_state[ny][nx]) > 1e-3:
                    continue
                player = board_state[ny][nx]%2*2-1

                for key in range(8):
                    ny = row
                    nx = col
                    cnt = 0
                    for i in range(N_IN_A_ROW-1):
                        cnt += 1
                        nx = nx + dx[key]
                        ny = ny + dy[key]

                        if not ((0 <= nx < BOARD_SIZE) and (0 <= ny < BOARD_SIZE)):
                            break
                        if board_state[ny][nx]%2*2-1 is not player:
                            if board_state[ny][nx] == 0:
                                if (((turn%2==0 and player==-1) or (turn%2==1 and player==1)) and pos_score[ny][nx] < cnt):
                                    pos_score[ny][nx] = cnt
                                if (((turn%2==0 and player==1) or (turn%2==1 and player==-1)) and -neg_score[ny][nx] < cnt):
                                    neg_score[ny][nx] = -cnt
                            break
        
        maxv = np.amax(np.asarray(pos_score))
        minv = np.amin(np.asarray(neg_score))

        if -minv > 2:
            row = random.randrange(0, BOARD_SIZE)
            col = random.randrange(0, BOARD_SIZE)
            while abs(board_state[row][col]) > 1e-3 or neg_score[row][col] is not minv:
                row = random.randrange(0, BOARD_SIZE)
                col = random.randrange(0, BOARD_SIZE)
        else:
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if i < N_IN_A_ROW-1 or j < N_IN_A_ROW-1:
                        pos_score[i][j] -= N_IN_A_ROW - min(i,j) - 1
                        neg_score[i][j] += N_IN_A_ROW - min(i,j) - 1
                    elif i > BOARD_SIZE - N_IN_A_ROW or j > BOARD_SIZE - N_IN_A_ROW:
                        pos_score[i][j] -= N_IN_A_ROW - (BOARD_SIZE - max(i,j))
                        neg_score[i][j] += N_IN_A_ROW - (BOARD_SIZE - max(i,j))
            
            total = -987654321
            total_row[0] = BOARD_SIZE//2
            total_col[0] = BOARD_SIZE//2

            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if board_state[i][j]==0 and total < pos_score[i][j] - neg_score[i][j]:
                        total = pos_score[i][j] - neg_score[i][j]
                        total_row[0] = i
                        total_col[0] = j
                    
            idx = 0
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if board_state[i][j]==0 and total == pos_score[i][j] - neg_score[i][j]:
                        total_row[idx] = i
                        total_col[idx] = j
                        idx += 1
            
            idx = random.randrange(0, idx)
            row = total_row[idx]
            col = total_col[idx]

        board_state[row][col] = turn
        board_state.turn = turn

        return board_state

