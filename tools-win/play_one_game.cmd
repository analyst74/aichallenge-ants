@echo off

python "%~dp0playgame.py" --engine_seed 42 --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs -e --turns 30 --food_rate 4 8 --map_file "%~dp0maps\maze\maze_03p_01.map" %* "python ..\src\MyBot.py" "python ..\archive\v4\v4.py" "python3 ..\archive\v3\v3.py3"