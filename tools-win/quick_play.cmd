@echo off

python "%~dp0playgame.py" --engine_seed 42 --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs --turns 500 --food_rate 4 8 -I --map_file "%~dp0maps\example\tutorial1.map" %* "python3 ..\src\MyBot.py3" "python3 ..\src\v3\v3.py3" -e -I