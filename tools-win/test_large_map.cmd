@echo off
python "%~dp0playgame.py" --engine_seed 42 --player_seed 42 --food Random --end_wait=0.25 --verbose --log_dir game_logs --turns 500 --turntime 500 --serial --map_file "%~dp0maps\maze\maze_08p_01.map" "python ..\src\MyBot.py" "python ..\archive\v5-militant\v5-m.py" "python ..\archive\v5.1\v5.1.py" "python sample_bots\python\HunterBot.py" --fill -e --strict --capture_errors