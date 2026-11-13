from typing import Any

from engine.highscores import Highscores
from engine.maze_adapter import MazeAdapter
from engine.rules import GameRules
from engine.ghosts import GhostAI, BlinkyBehavior, PinkyBehavior, \
    InkyBehavior, ClydeBehavior
from engine.movement import Player, Ghost
from engine.shared import State, GameSnapshot, GhostView, Cheat


class GameEngine:
    """Runs one game session: maze, rules, ghosts, player, and highscores."""
    def __init__(self, config: dict[str, Any],
                 highscore_path: Any = None) -> None:
        """Create the engine and set where highscores are stored."""
        self.config = config
        self.highscores = Highscores(
            highscore_path or self.config["highscore_filename"])
        self.adapter = MazeAdapter(self.config)
        self.rules = GameRules(self.config)
        self.ai = GhostAI()
        self.level: Any = None
        self.player: Any = None
        self.ghosts: list[Any] = []

    def start_new_game(self) -> None:
        """Reset the rules and start level 1."""
        self.rules.reset()
        self.ai.waiting.clear()
        self._start_level(1)

    def set_direction(self, direction: Any) -> None:
        """Store the direction the player asked to move."""
        self.player.set_direction(direction)

    def pause_game(self) -> None:
        """Pause a running game, or resume a paused one."""
        if self.rules.status is State.PLAYING:
            self.rules.status = State.PAUSED
        elif self.rules.status is State.PAUSED:
            self.rules.status = State.PLAYING

    def update(self, frame_time: float) -> None:
        """Advance the game by one time step."""
        if self.rules.status is not State.PLAYING:
            return
        player_before = self.player.position
        ghosts_before = [g.position for g in self.ghosts]
        self.player.step(self.level, frame_time)
        if self.player.direction is not None:
            self.ai.update(self.level, self.player, self.ghosts, frame_time)
            self.rules.updtae_times(frame_time, self.ghosts)
        for g in self.ghosts:
            g.step(self.level, frame_time)
        eaten: list[Any] = []
        met = {
            id(g) for g, before in zip(self.ghosts, ghosts_before)
            if g.position == self.player.position
            or (before == self.player.position
                and g.position == player_before)
        }
        eaten = [g for g in self.ghosts
                 if id(g) in met and g.edible and g.protected_time == 0]
        self._handle_eaten_ghosts(eaten)
        met -= {id(g) for g in eaten}
        self.rules.collect_items(self.level, self.player, self.ghosts)
        for g in self.ghosts:
            if g.protected_time > 0:
                g.protected_time = max(0.0, g.protected_time - frame_time)
        self.rules.check_ghost_contact(self.player, self.ghosts, met)
        self.rules.check_end(self.level)
        if not self.level.pacgums and not self.level.super_pacgums:
            if not self.rules.is_last_level():
                self.rules.next_level()
                self._start_level(self.rules.level_number)

    def cheat(self, action: Any) -> None:
        """Apply a cheat action, such as skipping the level."""
        if action is Cheat.SKIP:
            self.level.pacgums.clear()
            self.level.super_pacgums.clear()
        elif action is Cheat.NOCLIP:
            self.player.walk_through_walls = True
        elif action is Cheat.SUPER:
            self.level.super_pacgums |= self.level.pacgums
            self.level.pacgums.clear()
        elif action is Cheat.Immortal:
            self.rules.invincible = True
        elif action is Cheat.AutoWin:
            self.rules.score = 133333333333337
            self.rules.status = State.VICTORY
        elif action is Cheat.Reset:
            corners = [
                (0, 0),
                (self.level.width - 1, 0),
                (0, self.level.height - 1),
                (self.level.width - 1, self.level.height - 1),
            ]
            self.player.walk_through_walls = False
            restore: set[tuple[int, int]] = set()
            for pac_gums in self.level.super_pacgums:
                if pac_gums not in corners:
                    self.level.pacgums.add(pac_gums)
                else:
                    restore.add(pac_gums)
            self.level.super_pacgums = restore
            self.rules.invincible = False

    def submit_name(self, raw_name: str) -> bool:
        """Save the player's name with their score; return True if accepted."""
        return self.highscores.submit(raw_name, self.rules.score)

    def snapshot(self) -> GameSnapshot:
        """Return a copy of the current state for the frontend to draw."""
        game_snapshot = GameSnapshot(state=self.rules.status,
                                     score=self.rules.score,
                                     lives=self.rules.lives,
                                     level=self.rules.level_number,
                                     time_left=self.rules.time_left,
                                     player=self.player.position,
                                     player_direction=self.player.direction,
                                     ghosts=[GhostView(g.position, g.edible,
                                                       g.seconds_per_cell)
                                             for g in self.ghosts],
                                     walls=self.level.walls,
                                     pacgums=set(self.level.pacgums),
                                     super_pacgums=set(
                                         self.level.super_pacgums),
                                     width=self.level.width,
                                     height=self.level.height
                                     )
        return game_snapshot

    def _start_level(self, index: int) -> None:
        """Generate a level and place the player, ghosts, and timers."""
        self.level = self.adapter.generate_level(index)
        self.player = Player(self.level.player_start)
        self.ghosts = self._create_ghosts(self.level)
        self.ai.waiting.clear()
        self.rules.start_level(self.level, self.player, self.ghosts)

    def _create_ghosts(self, level: Any) -> list[Ghost]:
        """Create the four ghosts, each with its own chase behavior."""
        ghosts: list[Ghost] = []
        for corner in level.ghost_starts:
            ghosts.append(Ghost(corner, self.rules.level_number))
        ghosts[0].behavior = BlinkyBehavior()
        ghosts[1].behavior = PinkyBehavior()
        ghosts[2].behavior = InkyBehavior()
        ghosts[3].behavior = ClydeBehavior(ghosts[3])
        return ghosts

    def _handle_eaten_ghosts(self, eaten: list[Any]) -> None:
        """Score each eaten ghost, respawn it, and protect it briefly."""
        for ghost in eaten:
            self.rules.eat_ghost(ghost)
            self.ai.start_respawn(ghost)
            ghost.protected_time = 5.0
