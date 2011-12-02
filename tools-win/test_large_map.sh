#!/usr/bin/env sh
./playgame.py --engine_seed 42 --player_seed 42 --food symmetric --end_wait=0.25 --verbose --log_dir game_logs --turns 1000 --turntime 500 --serial --map_file "maps/random_walk/random_walk_10p_02.map" "python ../src/MyBot.py" "python ../archive/v9.2/v9.2.py" "python sample_bots/python/HunterBot.py" --fill -e --strict --capture_errors --nolaunch --food_rate 8 13
