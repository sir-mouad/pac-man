from engine.contracts import State


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
            self.edible_time_left = self.edible_duration
            for ghost in ghosts:
                ghost.edible = True

    def check_ghost_contact(self, player, ghosts):
        if self.invincible:
            return
        for ghost in ghosts:
            if ghost.position != player.position:
                continue
            if ghost.edible:
                self.eat_ghost(ghost)
            else:
                self.lose_life(player)
                return

    def tick(self, dt):
        if self.status is not State.PLAYING:
            return
        self.time_left = max(0.0, self.time_left - dt)
        if self.edible_time_left > 0:
            self.edible_time_left = max(0.0, self.edible_time_left - dt)
            if self.edible_time_left == 0:
                pass

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

    def lose_life(self, player):
        self.lives -= 1
        player.reset(player.position)

    def next_level(self):
        self.level_number += 1
        self.lives = self.lives

    def is_last_level(self):
        return self.level_number >= len(self.config["levels"])
