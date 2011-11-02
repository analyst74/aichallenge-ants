@echo off
python "%~dp0playgame.py" -So --engine_seed 42 --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs --turns 1000 --map_file "%~dp0maps\random_walk\random_walk_04p_01.map" %* "python3 ..\src\MyBot.py3" "python ""%~dp0sample_bots\python\HunterBot.py""" "python3 ..\src\v2\v2.py3" "python3 ..\src\v3\v3.py3" | java -jar visualizer.jar

