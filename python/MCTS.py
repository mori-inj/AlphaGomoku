from params import *
from Gomoku import *
from Network import Network
from HeuristicAgent import HeuristicAgent
import random
import math

BS = BOARD_SIZE

heuristic = HeuristicAgent()

network = Network(board_size = BS, input_frame_num = INPUT_FRAME_NUM, residual_num = RESIDUAL_NUM, is_trainable=True) #False
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
    frame = INPUT_FRAME_NUM
    turn_parity = turn % 2
    half_frame = (frame-1)//2
    
    s = np.zeros([1, BS, BS, frame])
    for i in range(BS):
        for j in range(BS):
            if 0 == board[i][j]:
                continue
            for fn in range(half_frame):
                limit = turn - fn*2
                if board[i][j] <= limit:
                    if board[i][j] % 2 == turn_parity:
                        s[0][i][j][fn] = 1
                    else:
                        s[0][i][j][fn+half_frame] = 1
        
    if turn_parity == 1:
        s[0,:,:,-1] = np.ones([BS, BS]) 
    
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

    if is_game_ended(state.board):
        v = 1

    return p_dict,v

def evaluate_with_constant(state, state_list):
    if is_game_ended(state.board):
        v = state.turn%2==0 #1 when mcts starts first, 0 when mcts starts later
    else:
        v = 0.5
    
    p_dict = {}
    p_sum = 0
    for new_state in state_list:
        r = new_state.last_row
        c = new_state.last_col
        p_dict[new_state] = 1
        p_sum += 1

    for p in p_dict:
        p_dict[p] /= p_sum

    return p_dict,v


def evaluate_with_random(state, state_list):
    v = random.uniform(-1, 1)
    p_dict = {}
    p_sum = 0
    for new_state in state_list:
        r = new_state.last_row
        c = new_state.last_col
        p = random.uniform(0, 1)
        p_dict[new_state] = p
        p_sum += p

    for p in p_dict:
        p_dict[p] /= p_sum

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
        self.N = 0
        self.N_sum = 0
        self.Q = 0
        self.W = 0
        self.P = 0
        self.U = 0
        self.selected_child = None
    
    def search(self):
        max_child = self.select()
        if max_child == self:
            max_child.expand()
        else:
            #self.selected_child = max_child
            max_child.search()
    
    def select(self):
        N_sum = self.N_sum
        COMP_EPSILON = 1-EPSILON
        child_list = self.child_list
        child_num = len(child_list)
        
        if child_num == 0:
            return self

        const = C_PUCT * (N_sum**0.5)
        
        if self.parent == None:
            noise = np.random.dirichlet([DIR_ALPHA] * child_num)
            idx = 0
            for child in child_list:
                P = COMP_EPSILON*child.P + EPSILON*noise[idx]
                idx += 1
                
                child.U = P * const / (1 + child.N)
        else:
            for child in child_list:
                child.U = child.P * const / (1 + child.N)

        return max(child_list, key=lambda x: x.Q + x.U)

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
            new_node.P = p[state]
        if self.parent != None:
            self.parent.backup(v, self)

    def backup(self, v, child):
        child.N += 1
        self.N_sum += 1
        child.W+= v
        child.Q = child.W / child.N
        if self.parent != None:
            self.parent.backup(-v, self)
    
    def get_pi(self, t):
        pi = {}
        N_s = 1e-9
        if t == 0:
            max_n = 0
            for n in self.child_list:
                if max_n < n.N:
                    max_n = n.N
                    max_child = n
            for n in self.child_list:
                if n == max_child:
                    pi[n] = 1
                else:
                    pi[n] = 0
            N_s = 1
        else:
            for n in self.child_list:
                pi[n] = n.N ** (1/t)
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
        
        print('Exception on \'play\' line:196 ', len(self.child_list))
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


