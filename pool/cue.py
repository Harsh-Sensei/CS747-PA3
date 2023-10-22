import math

import numpy as np
import pygame
import json

import config
import event
import gamestate
import physics
import agent
import time

class Cue(pygame.sprite.Sprite):
    def __init__(self, target, next_state_function):
        pygame.sprite.Sprite.__init__(self)
        self.angle = 0
        self.color = config.player1_cue_color
        self.target_ball = target
        self.visible = False
        self.displacement = config.ball_radius
        self.sprite_size = np.repeat(
            [config.cue_length + config.cue_max_displacement], 2)
        self.clear_canvas()
        if not next_state_function:
            self.agent = agent.Agent(None)
            
        self.next_state_function = next_state_function
        self.trace_dict = {}
        self.curr_iter = 0
        self.max_time = -1
        self.agent_angle = None
        self.agent_dis = None

    def clear_canvas(self):
        # create empty surface as a placeholder for the cue
        self.image = pygame.Surface(2 * self.sprite_size)
        self.image.fill((200, 200, 200))
        self.image.set_colorkey((200, 200, 200))
        self.rect = self.image.get_rect()
        self.rect.center = self.target_ball.ball.pos.tolist()

    def update(self, *args):
        if self.visible:
            self.image = pygame.Surface(2 * self.sprite_size)
            # color which will be ignored
            self.image.fill((200, 200, 200))
            self.image.set_colorkey((200, 200, 200))

            sin_cos = np.array([math.sin(self.angle), math.cos(self.angle)])
            initial_coords = np.array([math.sin(self.angle + 0.5 * math.pi), math.cos(self.angle +
                                                                                      0.5 * math.pi)]) * config.cue_thickness
            coord_diff = sin_cos * config.cue_length
            rectangle_points = np.array((initial_coords, -initial_coords,
                                         -initial_coords + coord_diff, initial_coords + coord_diff))
            rectangle_points_from_circle = rectangle_points + self.displacement * sin_cos
            pygame.draw.polygon(self.image, self.color,
                                rectangle_points_from_circle + self.sprite_size)

            self.points_on_screen = rectangle_points_from_circle + self.target_ball.ball.pos
            self.rect = self.image.get_rect()
            self.rect.center = self.target_ball.ball.pos.tolist()
        else:
            self.clear_canvas()

    def is_point_in_cue(self, point):
        # this algorithm splits up the rectangle into 4 triangles using the point provided
        # if the point provided is inside the triangle the sum of triangle
        # areas should be equal to that of the rectangle
        rect_sides = [config.cue_thickness * 2, config.cue_length] * 2
        triangle_sides = np.apply_along_axis(
            physics.point_distance, 1, self.points_on_screen, point)
        calc_area = np.vectorize(physics.triangle_area)
        triangle_areas = np.sum(
            calc_area(triangle_sides, np.roll(triangle_sides, -1), rect_sides))
        rect_area = rect_sides[0] * rect_sides[1]
        # +1 to prevent rounding errors
        return rect_area + 1 >= triangle_areas

    def update_cue_displacement(self, mouse_pos, initial_mouse_dist):
        displacement = physics.point_distance(
            mouse_pos, self.target_ball.ball.pos) - initial_mouse_dist + config.ball_radius
        if displacement > config.cue_max_displacement:
            self.displacement = config.cue_max_displacement
        elif displacement < config.ball_radius:
            self.displacement = config.ball_radius
        else:
            self.displacement = displacement

    def draw_lines(self, game_state, target_ball, angle, color):
        cur_pos = np.copy(target_ball.ball.pos)
        diff = np.array([math.sin(angle), math.cos(angle)])

        while config.resolution[1] > cur_pos[1] > 0 and config.resolution[0] > cur_pos[0] > 0:
            cur_pos += config.aiming_line_length * diff * 2
            pygame.draw.line(game_state.canvas.surface, color, cur_pos,
                             (cur_pos + config.aiming_line_length * diff))

    def is_clicked(self, events):
        return events["clicked"] and self.is_point_in_cue(events["mouse_pos"])

    def make_visible(self, current_player):
        if current_player == gamestate.Player.Player1:
            self.color = config.player1_cue_color
        else:
            self.color = config.player2_cue_color
        self.visible = True
        self.update()

    def make_invisible(self):
        self.visible = False

    def cue_is_active(self, game_state, events, render=True, action_for_next_state=None, seed=0, debug=False):
        self.update_cue(game_state, action_for_next_state, seed, debug)

        # undraw leftover aiming lines
        if render:
            self.draw_lines(game_state, self.target_ball, self.angle +
                            math.pi, config.table_color)

        self.ball_hit()

    def ball_hit(self):
        new_velocity = -(self.displacement - config.ball_radius - config.cue_safe_displacement) * \
                       config.cue_hit_power * np.array([math.sin(self.angle), math.cos(self.angle)])
        change_in_disp = np.hypot(*new_velocity) * 0.1
        while self.displacement - change_in_disp > config.ball_radius:
            self.displacement -= change_in_disp
            self.update()
            pygame.display.flip()
        self.target_ball.ball.apply_force(new_velocity)
        self.displacement = config.ball_radius
        self.visible = False

    def update_cue(self, game_state, action_temp, seed, debug):
        # updates cue position
        state = {elem.number : (elem.ball.pos[0], elem.ball.pos[1]) for i, elem in enumerate(game_state.balls)}
        state["white"] = (self.target_ball.ball.pos[0], self.target_ball.ball.pos[1])
        if self.curr_iter > 0: 
            self.trace_dict[self.curr_iter] = {"action" : [self.agent_angle, self.agent_dis], "state" : state}
        self.curr_iter += 1
        
        if game_state.next_state_function:
            angle = action_temp[0]
            dis = action_temp[1]
        else:
            start_time = time.time()
            angle, dis = self.agent.action(state) 
            x = time.time() - start_time
            if x > self.max_time:
                self.max_time = x
            state = {i : (elem.ball.pos[0], elem.ball.pos[1]) for i, elem in enumerate(game_state.balls)}
            state["white"] = (self.target_ball.ball.pos[0], self.target_ball.ball.pos[1])

        dis = np.clip(dis, 0, 1)
        angle = np.clip(angle, -1, 1)

        self.agent_angle = angle
        self.agent_dis = dis
        prev_angle = self.angle

        error_var = dis
        if game_state.next_state_function:
            rng = np.random.default_rng(int(seed))
            error = (np.pi/180)*np.clip(rng.normal(0, error_var), -2.5, 2.5) if debug == False else 0
        else:
            error = (np.pi/180)*np.clip(np.random.normal(0, error_var), -2.5, 2.5) if debug == False else 0
        
        self.displacement = (config.cue_max_displacement - config.ball_radius) * dis + config.ball_radius
        self.angle = angle * math.pi + error

        game_state.redraw_all(update=False)
        if game_state.render :
            self.draw_lines(game_state, self.target_ball, prev_angle +
                            math.pi, config.table_color)
            self.draw_lines(game_state, self.target_ball, self.angle +
                            math.pi, (255, 255, 255))
        pygame.display.flip()

    def save_trace_dict(self, filename="trace.json"):
        with open(filename, "w") as f:
            json.dump(self.trace_dict, f)
        
