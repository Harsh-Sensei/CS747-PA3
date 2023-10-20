import os
import sys
import random 
import json
import math
import utils
import time
random.seed(73)

class Agent:
    def __init__(self, table_config) -> None:
        self.table_config = table_config
        self.prev_action = None
        self.curr_iter = 0
        self.state_dict = {}
        self.holes =[]
        self.ns = utils.NextState()


    def set_holes(self, holes_x, holes_y, radius):
        for x in holes_x:
            for y in holes_y:
                self.holes.append((x[0], y[0]))
        self.ball_radius = radius


    def action(self, ball_pos=None):
        ## Code you agent here ##
        ## You can define other function in this file, but do not create other files
        ## Access the parameters of the simulation from config.py (do not change ady)
        
        return (2*random.random() - 1, random.random())
