import pygame

import collisions
import event
import gamestate
import graphics
import config
import time
import numpy
import argparse


def parser():
    parser = argparse.ArgumentParser(description='Billiards')
    parser.add_argument('--no-render', action='store_true')
    parser.add_argument('--generate-traces', action='store_true')
    parser.add_argument('--generate-stats', action='store_true')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--level-all', action='store_true')
    parser.add_argument('--level-x', type=int, default=0)
    parser.add_argument('--seed', type=int, default=73)
    parser.add_argument('--trace-file-prefix', type=str, default="traces/trace")

    return parser.parse_args()


if __name__ == "__main__":
    
    was_closed = False
    args = parser()
    numpy.random.seed(args.seed)
    start_time = 0
    levels_passed = 0
    marks = 0
    
    events = {"closed" : False, "quit_to_main_menu" : False}
    stats = {"mean_tries" : 0, "total_simulation_time" : 0, "average_episode_time" : 0, "number_episodes_played" : 0}
    
    MARKS = [0.4]*3 + [0.6]*4 + [0.8]*3
    
    config.debug = args.debug
    
    if args.level_all:
        MAX_TRIES = list(range(30, 30 - 2*config.num_levels, -2))
        print(MAX_TRIES)
        num_tries_arr = []
        start_time = time.time()
        num_runs = config.num_levels
        print(f"Running the agent on {num_runs} runs")
        for eps in range(num_runs):
            config.curr_level = eps
            curr_tries = 0
            frame_num = 0
            print("MAX_TRIES :", MAX_TRIES[eps])
            game = gamestate.GameState(not args.no_render)
            game.start_pool(level = eps)
            if not args.no_render:
                events = event.events()
            while not (events["closed"] or game.is_game_over or events["quit_to_main_menu"]):
                if curr_tries > MAX_TRIES[eps]:
                    num_tries_arr.append(MAX_TRIES[eps])
                    break
                frame_num += 1
                if not args.no_render:
                    events = event.events()
                                
                collisions.resolve_all_collisions(game.balls, game.holes, game.table_sides)
                
                game.redraw_all()
                
                if game.all_not_moving():

                    game.check_pool_rules()
                    if not args.no_render:
                        game.cue.make_visible(game.current_player)

                    while not (
                        (events["closed"] or events["quit_to_main_menu"]) or game.is_game_over) and game.all_not_moving():
                        
                        if not args.no_render:
                            game.redraw_all()

                        if not args.no_render:
                            events = event.events()
                        game.cue.cue_is_active(game, events, not args.no_render, debug=args.debug)
                        curr_tries += 1

            if game.is_game_over:
                num_tries_arr.append(curr_tries)
                if not (curr_tries > MAX_TRIES[eps]):
                    marks += MARKS[eps]
                    levels_passed += 1
                    print(f"Level {eps} passed")
                    print(f"Tries : {curr_tries}")
                    print()
            if curr_tries > MAX_TRIES[eps]:
                print(f"Level {eps} failed")
                print()

            if args.generate_traces:
                fname = args.trace_file_prefix + f"{eps}" +".json"
                game.cue.save_trace_dict(fname)
            if curr_tries > MAX_TRIES[eps] : 
                print("Max tries reached, moving to the next level")
                print()
            was_closed = events["closed"]
            if was_closed:
                break
            
        time_elapsed = time.time() - start_time
        if args.generate_stats:
            stats["mean_tries"] = sum(num_tries_arr) / len(num_tries_arr) if len(num_tries_arr) != 0 else 0
            stats["total_simulation_time"] = time_elapsed
            stats["average_episode_time"] = time_elapsed / (eps + 1)
            stats["number_episodes_played"] = eps + 1
            print(stats)
            
        print(f"#### Levels passed : {levels_passed} out of {num_runs} ####")
        print(f"#### Marks : {int(marks*10)/10} out of {sum(MARKS)} ####")

    else:
        assert args.level_x < config.num_levels and args.level_x >= 0, "Invalid level chosen"
        MAX_TRIES = 30 - 2*args.level_x
        num_tries_arr = []
        eps = args.level_x
        config.curr_level = eps
        num_runs = 1
        curr_tries = 0
        frame_num = 0
        start_time = time.time()
        
        print(f"Running the agent on {num_runs} runs")
        print("MAX_TRIES :", MAX_TRIES)
        
        game = gamestate.GameState(not args.no_render)
        game.start_pool(level = eps)
        if not args.no_render:
            events = event.events()
        while not (events["closed"] or game.is_game_over or events["quit_to_main_menu"]):
            if curr_tries > MAX_TRIES:
                num_tries_arr.append(MAX_TRIES)
                break
            frame_num += 1
            if not args.no_render:
                events = event.events()           
            collisions.resolve_all_collisions(game.balls, game.holes, game.table_sides)
            game.redraw_all()
            
            if game.all_not_moving():

                game.check_pool_rules()
                if not args.no_render:
                    game.cue.make_visible(game.current_player)

                while not (
                    (events["closed"] or events["quit_to_main_menu"]) or game.is_game_over) and game.all_not_moving():
                    
                    if not args.no_render:
                        game.redraw_all()

                    if not args.no_render:
                        events = event.events()
                    game.cue.cue_is_active(game, events, not args.no_render, debug=args.debug)
                    curr_tries += 1

        if game.is_game_over:
            num_tries_arr.append(curr_tries)
            if not curr_tries > MAX_TRIES:
                print(f"Level {eps} passed")
                print(f"Tries : {curr_tries}")
                levels_passed += 1
                print()
        if curr_tries > MAX_TRIES:
            print(f"Level {eps} failed")
            print()

        if args.generate_traces:
            fname = args.trace_file_prefix + f"{eps}" +".json"
            game.cue.save_trace_dict(fname)
        if curr_tries > MAX_TRIES : 
            print("Max tries reached, moving to the next level")
            print()

        time_elapsed = time.time() - start_time
        if args.generate_stats:
            stats["mean_tries"] = sum(num_tries_arr) / len(num_tries_arr) if len(num_tries_arr) != 0 else 0
            stats["total_simulation_time"] = time_elapsed
            stats["average_episode_time"] = time_elapsed / (1)
            stats["number_episodes_played"] = 1
            print(stats)
            
        print(f"#### Levels passed : {levels_passed} out of {num_runs} ####")
    
    pygame.quit()
    exit(0)


