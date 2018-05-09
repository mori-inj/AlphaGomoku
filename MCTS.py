from Network import Network
from Gomoku import *

class Node:
    def __init__(self, state):
        self.state = state
        self.child_list = []
        self.N = {}
        self.Q = {}
        self.W = {}
        self.P = {}
    
    def select(self, total_N):
        max_Q_U = -1
        max_child = self
        for child in child_list:
            U = 5 * P[child] * sqrt(total_N) / (1+N[child])
            if max_Q_U < Q[child] + U:
                max_Q_U = Q[child] + U
                max_child = child
        return child

    def expand(self):
        if len(child_list) > 0:
            return
        # add legal actions to child_list
        # calc P(d(child)) for each child and add to dict P
        # initialize N Q W
        # backup v
        

    def traverse(self):
        pass

    def print(self):
        pass
    
    def is_terminal_node(self):
        pass

    def is_leaf_node(self):
        pass

class MCTS:
    def __init__(self, //):
        self.root = 
