@echo off
playgame.py --engine_seed 42 --player_seed 42 --food none --end_wait=0.25 --verbose --log_dir game_logs --turns 5 --map_file submission_test/test.map "python3 ..\src\MyBot.py3" "python ""%~dp0sample_bots\python\LeftyBot.py""" -e --nolaunch --strict --capture_errors
