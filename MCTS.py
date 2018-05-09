from Network import Network
from Gomoku import *
import copy
import tkinter as tk
import random

network = Network(board_size = 3, input_frame_num = 5, residual_num = 10)
# input_frame_num = 5 means, past 2 mover per each player + 1

MCTS_WINDOW_WIDTH = 1600
MCTS_WINDOW_HEIGHT = 1000

def get_next_board_state(state):
    sl = []
    board_size = state.board_size
    turn = state.turn() + 1

    for i in range(board_size):
        for j in range(board_size):
            if state[i][j] == 0:
                new_state = copy.deepcopy(state)
                new_state[i][j] = turn
                sl.append(new_state)
    return sl

def preproc_board(board, bs, turn):
    frame = network.input_frame_num
    
    s = []
    for fn in range((frame-1)//2):
        f = np.zeros([bs,bs])
        for i in range(bs):
            for j in range(bs):
                if board[i][j] > 0 and board[i][j] % 2 == turn % 2 and \
                    board[i][j] <= turn - fn*2:
                    f[i][j] = 1
        s.append(f)
    
    for fn in range((frame-1)//2):
        f = np.zeros([bs,bs])
        for i in range(bs):
            for j in range(bs):
                if board[i][j] > 0 and board[i][j] % 2 != turn % 2 and \
                    board[i][j] <= turn - fn*2:
                    f[i][j] = 1
        s.append(f)

    if turn % 2 == 0:
        s.append(np.zeros([bs, bs]))
    else:
        s.append(np.ones([bs, bs]))
    
    s = np.asarray([s])
    s = np.transpose(s, [0, 2, 3, 1])
    return s


class Node:
    def __init__(self, state, parent=None):
        self.parent = parent
        self.state = state
        self.child_list = []
        self.N = {}
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
        N_sum = 0
        for n in self.N:
            N_sum += self.N[n]
        
        U_dict = {}
        for child in self.child_list:
            U = 5 * self.P[child] * N_sum**0.5 / (1+self.N[child])
            U_dict[child] = self.Q[child] + U
            if max_Q_U < self.Q[child] + U:
                max_Q_U = self.Q[child] + U
        
        max_child_list = []
        for u in U_dict:
            if abs(U_dict[u] - max_Q_U) < 1e-4:
                max_child_list.append(u)
        if len(max_child_list) > 0:
            max_child = random.choice(max_child_list)
        return max_child

    def expand(self, get_next_states):
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
        bs = state.board_size
        turn = state.turn()
        s = preproc_board(board, bs, turn)
        p,v = network.get_output(s)
        p = np.reshape(p,(bs,bs))
        p = self.dihedral_reflection(-i, p)
        p_dict = {}
        for new_state in state_list:
            ns = np.asarray(new_state.board)
            s = np.asarray(state.board)
            idx = np.argmax(ns - s)
            p_dict[new_state] = p[idx//bs][idx%bs]
        return p_dict,v
        """
        board = np.zeros([3,3]).tolist()
        for i in range(3):
            for j in range(3):
                board[i][j] = state[i][j]%2*2-1
        v = 0
        for i in range(3):
            a = 0
            b = 0
            for j in range(3):
                if board[i][j] > 0:
                    a += 1
                elif board[i][j] < 0:
                    b += 1
            v += 2**a - 2**b
        for i in range(3):
            a = 0
            b = 0
            for j in range(3):
                if board[j][i] > 0:
                    a += 1
                elif board[j][i] < 0:
                    b += 1
            v += 2**a - 2**b
        p = [[0.1,0.2,0.3],[0.4,0.5,0.6],[0.7,0.8,0.9]]
        p_dict = {}
        for new_state in state_list:
            ns = np.asarray(new_state.board)
            s = np.asarray(state.board)
            idx = np.argmax(ns - s)
            bs = state.board_size
            p_dict[new_state] = p[idx//bs][idx%bs]

        return p_dict, (v / (8*6) + 1 ) / 2
        """

    def backup(self, v, child):
        self.N[child] += 1
        self.W[child] += v
        self.Q[child] = self.W[child] / self.N[child]
        if self.parent != None:
            self.parent.backup(v, self)
   
    def play(self, t):
        N_list = []
        for n in self.N:
            N_list.append((self.N[n] ** (1/t), n))
        N_sum = N_list[-1][0]
        r = np.random.uniform(0, N_sum)
        for i in range(len(N_list)):
            if N_list[i][0] >= r:
                return N_list[i][1]
        return N_list[-1][1]
    
    def draw(self,x,y,flag):
        draw_board(mcts_canvas, x, y, self.state, self, self.parent, flag)
        if flag == False:
            return
        p = 20
        s = x #MCTS_WINDOW_WIDTH/2
        s -= (len(self.child_list) * (bs + p) + p) / 2
        i = 0
        for child in self.child_list:
            child.draw(s + p + (bs+p) * i, y + bs + 90, child==self.selected_child)
            i += 1

class MCTS:
    def __init__(self, board_size):
        self.board_size = board_size
        self.root = Node(BoardState(board_size))

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
        self.root.draw(MCTS_WINDOW_WIDTH/2 - bs/2, 10, True)



DRAWABLE_MODE = True

if DRAWABLE_MODE == True:
    mcts = MCTS(3)
    next_node = mcts.root

    def _mouse_left_up(event):
        global next_node
        x, y = event.x, event.y

        print(next_node)
        for i in range(16):
            mcts.search(next_node)
        next_node = mcts.play(next_node, 0.7)
        # check if game ended using next_node
        mcts.draw()

    def _draw_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    tk.Canvas.draw_circle = _draw_circle

    mcts_tk = tk.Tk()
    mcts_tk.resizable(width=False, height=False)
    mcts_tk.bind('<ButtonRelease-1>', _mouse_left_up)
    mcts_canvas = tk.Canvas(mcts_tk, width=MCTS_WINDOW_WIDTH, height=MCTS_WINDOW_HEIGHT, borderwidth=0, highlightthickness=0, bg="black")
    mcts_canvas.grid()

    mcts.draw()


    mcts_tk.wm_title("AlphaGomoku - MCTS")
    mcts_tk.mainloop()

else:
    for iteration in range(25000):
        mcts = MCTS(3)
        next_node = mcts.root
        print("iter: ", iteration)
        
        while True:
            for i in range(1600):
                mcts.search(next_node)
            # save pi MCTS(next_node) and state of next_node
            next_node = mcts.play(next_node, 0.7)
            # check if game ended using state of next_node
                # save z
                # break
        # train network using states, pi, z

