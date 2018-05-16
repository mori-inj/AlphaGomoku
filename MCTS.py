from Network import Network
from Gomoku import *
import copy
import tkinter as tk
import random
import math


DRAWABLE_MODE = False#True
BS = BOARD_SIZE
MCTS_SEARCH_NUM = 64 #1600
SELF_PLAY_NUM = 5000 #25000
SELF_PLAY_ITER = 50
TRAIN_ITER = 1000
PRINT_ITER = 200
TEMPER_EPS = 1e-2
SELF_PLAY_BATCH_SIZE = 200
TRAIN_BATCH_SIZE = 1000
C_PUCT = 5
TEMPERATURE = TEMPER_EPS
network = Network(board_size = BS, input_frame_num = 3, residual_num = 9, is_trainable=not DRAWABLE_MODE)

# input_frame_num = 5 means, past 2 mover per each player + 1

MCTS_WINDOW_WIDTH = 1600
MCTS_WINDOW_HEIGHT = 1000

def get_next_board_state(state):
    sl = []
    turn = state.turn + 1

    for i in range(BS):
        for j in range(BS):
            if state[i][j] == 0:
                new_state = copy.deepcopy(state)
                new_state[i][j] = turn
                new_state.turn = turn
                new_state.last_row = i
                new_state.last_col = j
                sl.append(new_state)
    return sl

def preproc_board(board, turn):
    frame = network.input_frame_num
    
    s = []
    for fn in range((frame-1)//2):
        f = np.zeros([BS, BS])
        for i in range(BS):
            for j in range(BS):
                if board[i][j] > 0 and board[i][j] % 2 == turn % 2 and \
                    board[i][j] <= turn - fn*2:
                    f[i][j] = 1
        s.append(f)
    
    for fn in range((frame-1)//2):
        f = np.zeros([BS, BS])
        for i in range(BS):
            for j in range(BS):
                if board[i][j] > 0 and board[i][j] % 2 != turn % 2 and \
                    board[i][j] <= turn - fn*2:
                    f[i][j] = 1
        s.append(f)

    if turn % 2 == 0:
        s.append(np.zeros([BS, BS]))
    else:
        s.append(np.ones([BS, BS]))
    
    s = np.asarray([s])
    s = np.transpose(s, [0, 2, 3, 1])
    return s


class Node:
    def __init__(self, state, parent=None):
        self.parent = parent
        self.state = state
        self.child_list = []
        self.N = {}
        self.N_sum = 0
        self.Q = {}
        self.W = {}
        self.P = {}
        self.selected_child = None
    
    def search(self):
        max_child = self.select()
        if max_child == self:
            max_child.expand(get_next_board_state)
        else:
            self.selected_child = max_child
            max_child.search()

    def select(self):
        max_Q_U = -1
        max_child = self
        N_sum = self.N_sum
        
        if len(self.child_list) == 0:
            return max_child

        QU_max = -float('Inf')
        const = C_PUCT * math.sqrt(N_sum)
        for child in self.child_list:
            U = self.P[child] * const / (1 + self.N[child])
            QU = self.Q[child] + U
            if QU_max < QU:
                QU_max = QU
                max_child = child
        
        return max_child

    def expand(self, get_next_states):
        if is_game_ended(self.state.board):
            _,v = self.evaluate(self.state, [])
            if self.parent != None:
                self.parent.backup(v, self)
            return

        state_list = get_next_states(self.state)
        p,v = self.evaluate(self.state, state_list)
        for state in state_list:
            new_node = Node(state, self)
            self.child_list.append(new_node)
            self.N[new_node] = 0
            self.Q[new_node] = 0
            self.W[new_node] = 0
            self.P[new_node] = p[state]
        if self.parent != None:
            self.parent.backup(v, self)

    def dihedral_reflection(self, i, x):
        if i > 0:
            if i > 4:
                x = np.fliplr(x)
                i -= 4
            for _ in range(i):
                x = np.rot90(x)
        elif i < 0:
            ii = -i
            if ii > 4:
                ii -= 4
            for _ in range(4 - ii):
                x = np.rot90(x)

            if i < -4:
                x = np.fliplr(x)
        return x

    def evaluate(self, state, state_list):
        i = random.randrange(1, 9)
        board = self.dihedral_reflection(i, np.asarray(state.board))
        turn = state.turn
        s = preproc_board(board, turn)
        p,v = network.get_output(s)
        p = np.reshape(p, (BS, BS))
        p = self.dihedral_reflection(-i, p)
        p_dict = {}
        for new_state in state_list:
            r = new_state.last_row
            c = new_state.last_col
            p_dict[new_state] = p[r][c]
        return p_dict,v
        
    def backup(self, v, child):
        self.N[child] += 1
        self.N_sum += 1
        self.W[child] += v
        self.Q[child] = self.W[child] / self.N[child]
        if self.parent != None:
            self.parent.backup(v, self)
    
    def get_pi(self, t):
        pi = {}
        N_s = 1e-9
        for n in self.N:
            pi[n] = self.N[n] ** (1/t)
            N_s += pi[n]
        
        for n in pi:
            pi[n] /= N_s

        return pi, N_s

    def play(self, t):
        pi, N_sum = self.get_pi(t)
        N_list = []
        for n in pi:
            N_list.append([pi[n],n])
        for i in range(1, len(N_list)):
            N_list[i][0] += N_list[i-1][0]
        r = np.random.uniform(0, 1)
        for i in range(len(N_list)):
            if N_list[i][0] >= r:
                return N_list[i][1]
        print(len(self.N))
        print(len(N_list))
        print(len(pi))
        return N_list[-1][1]
    
    def draw(self,x,y,flag):
        draw_board(mcts_canvas, x, y, self.state, self, self.parent, flag)
        if flag == False:
            return
        p = 60
        s = MCTS_WINDOW_HEIGHT/2
        s -= (len(self.child_list) * (bs+p)) / 2
        i = 0
        for child in self.child_list:
            child.draw(x + bs + p, s + (bs+p) * i, child==self.selected_child)
            i += 1

class MCTS:
    def __init__(self, board_size):
        self.board_size = board_size
        self.root = Node(BoardState(board_size, 0))

    def search(self, node=None):
        if node == None:
            self.root.search()
        else:
            node.search()

    def play(self, node, t):
        next_node = node.play(t)
        node.selected_child = next_node
        return next_node

    def draw(self):
        mcts_canvas.delete("all")
        mcts_canvas.create_rectangle(0, 0, MCTS_WINDOW_WIDTH, MCTS_WINDOW_HEIGHT, fill="#000")
        self.root.draw(10, MCTS_WINDOW_HEIGHT/2 - BS/2, True)


if DRAWABLE_MODE:
    mcts = MCTS(BS)
    next_node = mcts.root

    def _mouse_left_up(event):
        global next_node
        global mcts
        x, y = event.x, event.y

        print(next_node)
        for i in range(MCTS_SEARCH_NUM): #FIXME step by step
            mcts.search(next_node)

        orig_board = next_node.state.board
        next_node = mcts.play(next_node, TEMPERATURE)
        next_board = next_node.state.board
        
        mcts.draw()
        
        if is_game_ended(next_board):
            mcts = MCTS(BS)
            next_node = mcts.root
            print('===============================')
        
        if next_node.state.turn == BS*BS:
            mcts = MCTS(BS)
            next_node = mcts.root
            print('===============================')

    def _draw_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    tk.Canvas.draw_circle = _draw_circle

    mcts_tk = tk.Tk()
    mcts_tk.resizable(width=False, height=False)
    mcts_tk.bind('<ButtonRelease-1>', _mouse_left_up)
    mcts_canvas = tk.Canvas(mcts_tk,
                            width=MCTS_WINDOW_WIDTH,
                            height=MCTS_WINDOW_HEIGHT,
                            borderwidth=0,
                            highlightthickness=0,
                            bg="black")
    mcts_canvas.grid()

    mcts.draw()

    mcts_tk.wm_title("AlphaGomoku - MCTS")
    mcts_tk.mainloop()

else:
    input_list = []
    pi_list = []
    z_list = []
    t_list = []

    for iteration in range(SELF_PLAY_NUM):
        mcts = MCTS(BS)
        node = mcts.root
        print("======================= iter: " + str(iteration) + " ===========================")

        turn_cnt = 0
        while True:
            turn_cnt += 1
            if turn_cnt <= 2:
                TEMPERATURE = 1
            else:
                TEMPERATURE = TEMPER_EPS

            for i in range(MCTS_SEARCH_NUM):
                mcts.search(node)
            orig_state = node.state
            orig_board = orig_state.board
            input_board = preproc_board(orig_board, orig_state.turn)
            input_list.append(input_board[0])
            
            pi = np.zeros([BS * BS])
            n_list, n_sum = node.get_pi(TEMPERATURE)
            for n in n_list:
                idx = n.state.last_row * BS + n.state.last_col
                pi[idx] = n_list[n]
            pi_list.append(pi)
            
            node = mcts.play(node, TEMPERATURE)
            
            next_state = node.state
            next_board = next_state.board 
            r = next_state.last_row
            c = next_state.last_col

            if is_game_ended(next_board):
                input_board = preproc_board(next_board, next_state.turn)
                input_list.append(input_board[0])
                pi = np.zeros([BS * BS])
                n_list, n_sum = node.get_pi(TEMPERATURE)
                for n in n_list:
                    idx = n.state.last_row * BS + n.state.last_col
                    pi[idx] = n_list[n]
                pi_list.append(pi)
                nst = int(next_state.turn + 1)
                for i in range(nst):
                    if i %2*2-1 == next_state.turn%2*2-1:
                    	z_list.append([1])
                    else:
                        z_list.append([-1])
                    t_list.append([float(next_state.turn)])
                break
            elif next_state.turn == BS*BS:
                input_board = preproc_board(next_board, next_state.turn)
                input_list.append(input_board[0])
                pi = np.zeros([BS * BS])
                n_list, n_sum = node.get_pi(TEMPERATURE)
                for n in n_list:
                    idx = n.state.last_row * BS + n.state.last_col
                    pi[idx] = n_list[n]
                pi_list.append(pi)
            
                nst = next_state.turn + 1
                for _ in range(nst):
                    z_list.append([-1])
                    t_list.append([float(next_state.turn)])
                break

        if iteration % SELF_PLAY_ITER == 0:
            l = len(input_list) - 9
            index = []
            i = random.randrange(0, max(1, len(input_list)//SELF_PLAY_BATCH_SIZE))
            while i < l:
                index.append(i)
                i += random.randrange(1, max(2, len(input_list)//SELF_PLAY_BATCH_SIZE))
            while i < len(input_list):
                index.append(i)
                i += 1
            random.shuffle(index)
            print(len(index))
            input_ = np.asarray([input_list[idx] for idx in index])
            pi_ = np.asarray([pi_list[idx] for idx in index])
            z_ = np.asarray([z_list[idx] for idx in index])
            t_ = np.asarray([t_list[idx] for idx in index])
        
        """ 
        print('==========input========')
        print(len(input_list), np.transpose(input_list,[0,3,1,2]))
        print('============pi=========')
        print(len(pi_list), pi_list)
        print('============z==========')
        print(len(z_list), z_list)
        print('=======================')
        """
        print(len(input_list), len(pi_list), len(z_list))
        """
        input_list_t = np.transpose(input_list, [0,3,1,2])
        for i in range(len(input_list)):
            frame = network.input_frame_num
            bd = np.zeros([BS,BS])
            for y in range(BS):
                for x in range(BS):
                    if input_list_t[i][0][y][x] == 1:
                        bd[y][x] = 1
                    elif input_list_t[i][(frame-1)//2][y][x] == 1:
                        bd[y][x] = -1
            pi_t = np.reshape(np.asarray(pi_list[i]),[BS,BS]).tolist()
            st = ""
            for j in range(BS):
                for k in range(BS):
                    if (i % 2 == 0 and bd[j][k] == 1) or (i % 2 == 1 and bd[j][k] == -1):
                        st += "o "
                    elif (i % 2 == 0 and bd[j][k] == -1) or (i % 2 == 1 and bd[j][k] == 1):
                        st += "x "
                    else:
                        st += "  "
                st += "    "
                for k in range(BS):
                    st += "%.2f " % pi_t[j][k]
                if j != BS-1:
                    st += "\n"
            print(st)
            print(z_list[i])
            print()
        """

        if iteration % SELF_PLAY_ITER == 0:
            network.train(input_, pi_, z_, t_, TRAIN_ITER, PRINT_ITER) 

    for iteration in range(SELF_PLAY_NUM):
        print('============ iter:' + str(iteration) + '=============')
        l = len(input_list) - 9
        index = []
        i = random.randrange(0, max(1, len(input_list)//TRAIN_BATCH_SIZE))
        while i < l:
            index.append(i)
            i += random.randrange(1, max(2, len(input_list)//TRAIN_BATCH_SIZE))
        while i < len(input_list):
            index.append(i)
            i += 1
        random.shuffle(index) 
        
        input_ = np.asarray([input_list[idx] for idx in index])
        pi_ = np.asarray([pi_list[idx] for idx in index])
        z_ = np.asarray([z_list[idx] for idx in index])
        t_ = np.asarray([t_list[idx] for idx in index])
        network.train(input_, pi_, z_, t_, TRAIN_ITER, PRINT_ITER)
