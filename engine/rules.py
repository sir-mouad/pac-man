from engine.shared import State


class GameRules:
    def __init__(self, config):
        self.config = config
        self.score = 0
        self.lives = config["lives"]
        self.level_number = 1
        self.time_left = config["level_max_time"]
        self.status = State.PLAYING
        self.edible_time_left = 0.0
        self.points_per_pacgum = config["points_per_pacgum"]
        self.points_per_super_pacgum = config["points_per_super_pacgum"]
        self.points_per_ghost = config["points_per_ghost"]
        self.edible_duration = 8.0
        self.invincible = False

    def start_level(self, level, player, ghosts):
        self.time_left = self.config["level_max_time"]
        self.edible_time_left = 0.0
        self.status = State.PLAYING
        player.reset(level.player_start)
        for ghost, start in zip(ghosts, level.ghost_starts):
            ghost.corner = start
            ghost.respawn()

    def reset(self):
        self.score = 0
        self.lives = self.config["lives"]
        self.level_number = 1
        self.time_left = self.config["level_max_time"]
        self.status = State.PLAYING
        self.edible_time_left = 0.0
        self.invincible = False

    def collect_items(self, level, player, ghosts):
        cell = player.position
        if cell in level.pacgums:
            level.pacgums.remove(cell)
            self.score += self.points_per_pacgum
        if cell in level.super_pacgums:
            level.super_pacgums.remove(cell)
            self.score += self.points_per_super_pacgum
            if self.level_number <= 10:
                self.edible_time_left = self.edible_duration
                for ghost in ghosts:
                    if not ghost.edible:
                        if self.level_number <= 7:
                            lowering = ghost.seconds_per_cell * 0.40
                        else:
                            lowering = ghost.seconds_per_cell * 0.20
                        ghost.seconds_per_cell = ghost.seconds_per_cell + lowering
                    ghost.edible = True

    def check_ghost_contact(self, player, ghosts, met):
        if self.invincible:
            return
        for ghost in ghosts:
            if id(ghost) not in met:
                continue
            if ghost.edible:
                self.eat_ghost(ghost)
            if ghost.protected_time > 0:
                continue
            else:
                self.lose_life(player, ghosts)
                return

    def updtae_times(self, frame_time, ghosts):
        if self.status is not State.PLAYING:
            return
        self.time_left = max(0.0, self.time_left - frame_time)
        if self.edible_time_left > 0:
            self.edible_time_left = max(
                0.0, self.edible_time_left - frame_time)
            if self.edible_time_left == 0:
                for ghost in ghosts:
                    ghost.edible = False
                    if self.level_number <= 7:
                        self.seconds_per_cell = ghost.first_seconds - \
                            (self.level_number - 1) * 0.01
                    elif self.level_number <= 11:
                        self.seconds_per_cell = ghost.first_seconds - \
                            (self.level_number - 1) * 0.02
                    else:
                        self.seconds_per_cell = ghost.first_seconds - \
                            10 * 0.02

    def check_end(self, level):
        if self.lives <= 0:
            self.status = State.GAME_OVER
        elif not level.pacgums and not level.super_pacgums:
            if self.is_last_level():
                self.status = State.VICTORY
            else:
                self.status = State.PLAYING
        elif self.time_left <= 0:
            self.status = State.GAME_OVER

    def eat_ghost(self, ghost):
        self.score += self.points_per_ghost
        ghost.respawn()

    def lose_life(self, player, ghosts):
        self.lives -= 1
        player.reset(player.start)
        for ghost in ghosts:
            ghost.respawn()

    def next_level(self):
        self.level_number += 1

    def is_last_level(self):
        return self.level_number >= len(self.config["levels"])
