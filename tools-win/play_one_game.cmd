@echo off
python "%~dp0playgame.py" --engine_seed 42 --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs -e -I --turns 1000 --turntime=1000 --food_rate 5 8 --food_turn 19 37 --food_start 75 175 --food_visible 3 5 --food symmetric --map_file "maps\random_walk\random_walk_03p_01.map" %* "python ..\src\MyBot.py" "python ..\archive\v11.0\v11.0.py"  --fill
