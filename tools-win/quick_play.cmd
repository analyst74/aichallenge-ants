@echo off

python "%~dp0playgame.py" --engine_seed 42 --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs --turns 50 --food_rate 4 8 -I --map_file "%~dp0maps\example\tutorial1.map" %* "python ..\src\MyBot.py" "python ..\archive\v4\v4.py" -e -I