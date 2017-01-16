#!/usr/bin/env sh
./playgame.py --engine_seed 42 --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs -e --turns 500 --turntime=500 --food_rate 5 8 --food_turn 19 37 --food_start 75 175 --food_visible 3 5 --food symmetric --map_file "maps/random_walk/random_walk_04p_01.map" "python ../src/MyBot.py" "python ../archive/hunter/hunter.py" --fill
