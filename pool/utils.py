import pygame
import collisions
import event
import gamestate
import graphics
import config
import time

import argparse


class NextState:
    def __init__(self) -> None:
        self.speculative_gamestate = gamestate.GameState(0, True, None)
        
    def get_next_state(self, state, action, seed):
        config.speculation = True
        events = {"closed" : False, "quit_to_main_menu" : False}
        ret_state = {}
        self.speculative_gamestate.state = state
        self.speculative_gamestate.start_pool()
        ret_state = {elem.number : (elem.ball.pos[0], elem.ball.pos[1]) for i, elem in enumerate(self.speculative_gamestate.balls)}
        ret_state["white"] = (self.speculative_gamestate.cue.target_ball.ball.pos[0], self.speculative_gamestate.cue.target_ball.ball.pos[1])
        # print("ret_state from get_next_state" ,ret_state)
        curr_tries = 0  
        while not self.speculative_gamestate.is_game_over:
            if curr_tries > 1 :
                config.speculation = False 
                return ret_state

            collisions.resolve_all_collisions(self.speculative_gamestate.balls, self.speculative_gamestate.holes, self.speculative_gamestate.table_sides)
            self.speculative_gamestate.redraw_all()
            if self.speculative_gamestate.all_not_moving():

                self.speculative_gamestate.check_pool_rules()

                while not (
                    (events["closed"] or events["quit_to_main_menu"]) or self.speculative_gamestate.is_game_over) and self.speculative_gamestate.all_not_moving():
                    
                    self.speculative_gamestate.cue.cue_is_active(self.speculative_gamestate, events, 0, action, seed, debug=config.debug)
                    ret_state = {elem.number : (elem.ball.pos[0], elem.ball.pos[1]) for i, elem in enumerate(self.speculative_gamestate.balls)}
                    ret_state["white"] = (self.speculative_gamestate.cue.target_ball.ball.pos[0], self.speculative_gamestate.cue.target_ball.ball.pos[1])
                    self.speculative_gamestate.state = ret_state
                    curr_tries += 1
                
                
    
