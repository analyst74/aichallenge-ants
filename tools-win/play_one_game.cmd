@echo off

python "%~dp0playgame.py" --engine_seed 42 --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs --turns 500 --map_file "%~dp0maps\random_walk\random_walk_05p_01.map" %* "python3 ..\src\MyBot.py3" "python3 ..\src\temp1\temp1.py3" "python3 ..\src\temp2\temp2.py3" "python3 ..\src\temp3\temp3.py3" "python ""%~dp0sample_bots\python\HunterBot.py""" 