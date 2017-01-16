Bill's Bot for Google AI Challenge 2011 - Ants
====================

Pre-requisites:
--------------------
- Python 2.x
- Cython
- Numpy


Run the game:
--------------------
- go to /src and run `python setup.py build_ext --inplace`
- go to /tools-win and run `./play_one_game.sh`
- watch game being executed
- once game is completed, a browser window will open with visualized replay

You can modify `play_one_game.sh` script to change the map or other parameters. By default, the game is played by Bill's Bot and a few other instances of a simplistic hunter bot.

Architecture:
--------------------
Core of the architecture relies on Influence Mapping, which is constructed by planner and used by individual ants to make decision on what to do.
The design does not follow any particular paradigm, but do try to seperate different concerns:
- MyBot.py is just used a simple shell for bot initiation
- gamestate.py is used to track all possible states
- rest of the modules shall be stateless functions

Key Concepts:
--------------------
### Influence Mapping
http://aigamedev.com/open/tutorial/influence-map-mechanics/

### Specialized Combat Logic
TODO: write up the combat logic once it's stabilized

Code Structure:
--------------------
- /src                - root folder for all source code
- /src/MyBot.py       - contains MyBot class required by contest to initiate the bot
- /src/core.py        - common stuff shared by modules, AI configuration (heuristics and etc)
- /src/path.py        - pathfinding algorithms
- /src/gamestate.py   - stuff related to game state management, including I/O with game engine
- /src/planner.py     - strategic planner
- /src/influence.py   - influence mapping implementation

# following modules are created as need arises
- /src/combat/        - combat modules, keep past working combat modules for comparison with newer ones
- /src/raze.py        - hill razing logic
- /src/explore.py     - explore logic
- /src/gather.py      - food gather logic

Module Dependency:
--------------------
- format: module -> dependency
- TODO: replace this manual management with dependency generation graph
- core -> None
- path -> None
- gamestate -> core
- MyBot -> core, gamestate, path
