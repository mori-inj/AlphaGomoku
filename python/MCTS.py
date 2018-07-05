from Gomoku import *
from Network import Network
from HeuristicAgent import HeuristicAgent
import random
import math

BS = BOARD_SIZE
C_PUCT = 5
EPSILON = 0.25
DIR_ALPHA = 0.5


heuristic = HeuristicAgent()

network = Network(board_size = BS, input_frame_num = 3, residual_num = 9, is_trainable=False)
# input_frame_num = 5 means, past 2 mover per each player + 1

def get_next_states(state):
    sl = []
    turn = state.turn + 1

    for i in range(BS):
        for j in range(BS):
            if state[i][j] == 0:
                new_state = BoardState(state.board_size, turn, i, j)
                new_state.board = np.copy(state.board)
                new_state[i][j] = turn
                sl.append(new_state)
    return sl

def preproc_board(board, turn):
    frame = network.input_frame_num
    
    s = [0] * frame
    for fn in range((frame-1)//2):
        f = np.zeros([BS, BS])
        for i in range(BS):
            for j in range(BS):
                if board[i][j] > 0 and board[i][j] % 2 == turn % 2 and \
                    board[i][j] <= turn - fn*2:
                    f[i][j] = 1
        s[fn] = f
    
    for fn in range((frame-1)//2):
        f = np.zeros([BS, BS])
        for i in range(BS):
            for j in range(BS):
                if board[i][j] > 0 and board[i][j] % 2 != turn % 2 and \
                    board[i][j] <= turn - fn*2:
                    f[i][j] = 1
        s[fn + (frame-1)//2] = f

    if turn % 2 == 0:
        s[-1] = np.zeros([BS, BS]) 
    else:
        s[-1] = np.ones([BS, BS]) 
    
    s = np.asarray([s])
    s = np.transpose(s, [0, 2, 3, 1])
    return s

def dihedral_reflection_rotation(i, x):
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

def evaluate_with_network(state, state_list):
    i = random.randrange(1, 9)
    board = dihedral_reflection_rotation(i, np.asarray(state.board))
    turn = state.turn
    s = preproc_board(board, turn)
    p,v = network.get_output(s)
    p = np.reshape(p, (BS, BS))
    p = dihedral_reflection_rotation(-i, p)
    p_dict = {}
    for new_state in state_list:
        r = new_state.last_row
        c = new_state.last_col
        p_dict[new_state] = p[r][c]
    return p_dict,v

def evaluate_with_heuristic(state, state_list):
    p_dict, v = heuristic.evaluate(state, state_list)
    return p_dict, v

class Node:
    def __init__(self, state, evaluate, parent=None):
        self.evaluate = evaluate
        self.parent = parent
        self.state = state
        self.child_list = []
        self.N = {}
        self.N_sum = 0
        self.Q = {}
        self.W = {}
        self.P = {}
        self.U = {}
        self.selected_child = None
    
    def search(self):
        max_child = self.select()
        if max_child == self:
            max_child.expand()
        else:
            #self.selected_child = max_child
            max_child.search()
    
    def select(self):
        max_child = self
        N_sum = self.N_sum
        
        if len(self.child_list) == 0:
            return max_child

        QU_max = -float('Inf')
        const = C_PUCT * math.sqrt(N_sum)
        noise = np.random.dirichlet([DIR_ALPHA] * len(self.child_list))
        idx = 0
        for child in self.child_list:
            if self.parent == None: # node is root
                P = (1-EPSILON)*self.P[child] + EPSILON*noise[idx]
                idx += 1
            else:
                P = self.P[child]
            U = P * const / (1 + self.N[child])
            self.U[child] = U
            QU = self.Q[child] + U
            if QU_max < QU:
                QU_max = QU
                max_child = child
        
        return max_child

    def expand(self):
        if is_game_ended(self.state.board): # FIXME Gomoku specific
            _,v = self.evaluate(self.state, [])
            if self.parent != None:
                self.parent.backup(v, self)
            return

        state_list = get_next_states(self.state)
        p,v = self.evaluate(self.state, state_list)
        for state in state_list:
            new_node = Node(state, self.evaluate, self)
            self.child_list.append(new_node)
            self.N[new_node] = 0
            self.Q[new_node] = 0
            self.W[new_node] = 0
            self.P[new_node] = p[state]
            self.U[new_node] = 0
        if self.parent != None:
            self.parent.backup(v, self)

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
        
        print('Exception on \'play\' line:196 ', len(self.N))
        print('Exception on \'play\' line:197 ', len(N_list))
        print('Exception on \'play\' line:198 ', len(pi))
        return N_list[-1][1]
    
    
class MCTS:
    def __init__(self, board_size, evaluate):
        self.root = Node(BoardState(board_size, 0), evaluate)

    def search(self, node=None):
        if node == None:
            self.root.search()
        else:
            node.search()

    def play(self, node, t):
        next_node = node.play(t)
        node.selected_child = next_node
        return next_node


