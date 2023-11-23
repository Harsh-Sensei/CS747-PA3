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

    def get_angle(self, white_ball, tball, hole):
        m = 2*self.ball_radius + math.dist(list(tball), list(hole))
        n = 2*self.ball_radius
        final_point = (((m*tball[0]) - (n*hole[0]))/(m-n), ((m*tball[1]) - (n*hole[1]))/(m-n))
        angle = math.atan2((-final_point[0] + white_ball[0]), (-final_point[1] + white_ball[1]))/math.pi

        return angle
    
    def closest_hole(self, target_ball):
        min = 9999999
        close_hole = 0
        for i in self.holes:
            if math.dist(target_ball, i) < min:
                min = math.dist(target_ball, i)
                close_hole = i
                
        return close_hole

    def action(self, ball_pos=None):
        # return (2*random.random() - 1, random.random())
        if len(ball_pos.keys()) == 2:
            return (0.5, 0.5)
        if self.curr_iter > 0:
            self.state_dict[self.curr_iter] = {"ball_pos" : ball_pos, "action" : self.prev_action}
        self.curr_iter += 1
        
        min_dist = 999999
        close_hole = None
        close_ball = None
        for h in self.holes:
            for b_idx in ball_pos.keys():
                if b_idx == 0 or b_idx == "white":
                    continue
                b = ball_pos[b_idx]
                if math.dist(b, h) < min_dist:
                    min_dist = math.dist(b, h)
                    close_hole = h
                    close_ball = b
        
        for h in self.holes:
            for b_idx in ball_pos.keys():
                if b_idx == 0 or b_idx == "white":
                    continue
                b = ball_pos[b_idx]
                angle = self.get_angle(ball_pos["white"], b, h)
                st = time.time()
                next_state = self.ns.get_next_state(ball_pos, (angle, 0.5), time.time())

                if len(next_state.keys()) < len(ball_pos.keys()):
                    close_ball = b
                    close_hole = h
                    break
                    
        angle = self.get_angle(ball_pos["white"], close_ball, close_hole)
        self.prev_action = (angle, 0.5)
        return (self.prev_action[0], self.prev_action[1])