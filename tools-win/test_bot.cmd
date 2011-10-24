@echo off
playgame.py --engine_seed 42 --player_seed 42 --food Random --end_wait=0.25 --verbose --log_dir game_logs --turns 50 --map_file maps/maze/maze_02p_01.map "python3 ..\src\MyBot.py3" "python3 ..\src\temp1\temp1.py3" -e --nolaunch --strict --capture_errors
