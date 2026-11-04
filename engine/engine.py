from parser import Parser
from highscores import Highscores
from maze_adapter import MazeAdapter
from rules import GameRules
from ghosts import GhostAI


class GameEngine:
    def __init__(self, config_path):
        self.config = Parser(config_path).get_config()
        self.highscores = Highscores(self.config["highscore_filename"])
        self.adapter = MazeAdapter(self.config)
        self.rules = GameRules(self.config)
        self.ai = GhostAI()
        self.level = None
        self.player = None
        self.ghosts = []
