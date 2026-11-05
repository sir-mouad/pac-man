from parser import Parser
from highscores import Highscores
from maze_adapter import MazeAdapter
from rules import GameRules
from ghosts import GhostAI, BlinkyBehavior, PinkyBehavior, InkyBehavior, ClydeBehavior
from movement import Player, Ghost


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

    def start_new_game(self):
        self.rules.reset()
        self.ai.waiting.clear()
        self._start_level(1)

    def set_direction(self, direction):
        ...

    def toggle_pause(self):
        ...

    def update(self, dt):
        ...

    def cheat(self, action):
        ...

    def submit_name(self, raw_name):
        ...

    def snapshot(self):
        ...

    def _start_level(self, index):
        self.level = self.adapter.generate_level(index)
        self.player = Player(self.level.player_start)
        self.ghosts = self._create_ghosts(self.level)
        self.rules.waiting.clear()
        self.rules.start_level(self.level, self.player, self.ghosts)


    def _create_ghosts(self, level):
        ghosts = []
        for corner in level.ghost_starts:
            ghosts.append(Ghost(corner))
        ghosts[0].behavior = BlinkyBehavior()
        ghosts[1].behavior = PinkyBehavior()
        ghosts[2].behavior = InkyBehavior()
        ghosts[3].behavior = ClydeBehavior(ghosts[3])
        return ghosts

    def _handle_eaten_ghosts(self, eaten):
        ...