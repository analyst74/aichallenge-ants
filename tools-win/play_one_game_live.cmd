@echo off
python "%~dp0playgame.py" -So --engine_seed 42 --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs --turns 1000 --map_file "%~dp0maps\maze\maze_04p_01.map" %* "python ..\src\MyBot.py" "python ..\archive\v4\v4.py" "python3 ..\archive\v3\v3.py3" "python ""%~dp0sample_bots\python\HunterBot.py""" | java -jar visualizer.jar

