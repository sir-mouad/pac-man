from engine.parser import Parser
from engine.highscores import Highscores
from engine.maze_adapter import MazeAdapter
from engine.rules import GameRules
from engine.ghosts import GhostAI, BlinkyBehavior, PinkyBehavior, InkyBehavior, ClydeBehavior
from engine.movement import Player, Ghost
from engine.contracts import State, Direction, GameSnapshot, GhostView


class GameEngine:
    def __init__(self, config_path):
        self.parser = Parser()
        self.config = self.parser.get_config()
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
        self.player.set_direction(direction)

    def pause_game(self):
        if self.rules.status is State.PLAYING:
            self.rules.status = State.PAUSED
        elif self.rules.status is State.PAUSED:
            self.rules.status = State.PLAYING

    def update(self, dt):
        if self.rules.status is not State.PLAYING:
            return
        self.player.step(self.level, dt)

        self.ai.update(self.level, self.player, self.ghosts, dt)

        for g in self.ghosts:
            g.step(self.level, dt)
        eaten = []
        for g in self.ghosts:
            if g.edible and g.position == self.player.position:
                eaten.append(g)
        self._handle_eaten_ghosts(eaten)
        self.rules.collect_items(self.level, self.player, self.ghosts)
        self.rules.check_ghost_contact(self.player, self.ghosts)
        self.rules.tick(dt)
        self.rules.check_end(self.level)
        if not self.level.pacgums and not self.level.super_pacgums:
            if not self.rules.is_last_level():
                self.rules.next_level()
                self._start_level(self.rules.level_number)

    def cheat(self, action):
        if action == "skip_level":
            self.level.pacgums.clear()
            self.level.super_pacgums.clear()
        elif action == "walk_through_walls":
            self.player.walk_through_walls = True
        elif action == "all_super":
            self.level.super_pacgums |= self.level.pacgums
            self.level.pacgums.clear()
        elif action == "end_game":
            self.rules.score = 133333333333337
            self.rules.status = State.VICTORY
        elif action == "invincible":
            self.rules.invincible = True

    def submit_name(self, raw_name):
        return self.highscores.submit(raw_name, self.rules.score)

    def snapshot(self):
        game_snapshot = GameSnapshot(state=self.rules.status,
                                     score=self.rules.score,
                                     lives=self.rules.lives,
                                     level=self.rules.level_number,
                                     time_left=self.rules.time_left,
                                     player=self.player.position,
                                     player_direction=self.player.direction,
                                     ghosts=[GhostView(g.position, g.edible)
                                             for g in self.ghosts],
                                     walls=self.level.walls,
                                     pacgums=set(self.level.pacgums),
                                     super_pacgums=set(
                                         self.level.super_pacgums),
                                     width=self.level.width,
                                     height=self.level.height,
                                     cheats_active=set(),
                                     message=None)
        return game_snapshot

    def _start_level(self, index):
        self.level = self.adapter.generate_level(index)
        self.player = Player(self.level.player_start)
        self.ghosts = self._create_ghosts(self.level)
        self.ai.waiting.clear()
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
        for ghost in eaten:
            self.rules.eat_ghost(ghost)
            self.ai.start_respawn(ghost)
