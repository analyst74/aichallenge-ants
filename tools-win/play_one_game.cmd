@echo off
python "%~dp0playgame.py" --engine_seed 42 --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs -e --turns 300 --turntime=500 --food_rate 5 11 --food_turn 19 37 --food_start 75 175 --food_visible 3 5 --food symmetric --map_file "%~dp0maps\random_walk\random_walk_05p_01.map" %* "python ..\src\MyBot.py" "python ..\archive\v5.3\v5.3.py" "python sample_bots\python\HoldBot.py" --fill
