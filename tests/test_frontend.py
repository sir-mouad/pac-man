"""Integration checks using the real engine and SDL's headless display."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame  # noqa: E402

from engine.engine import GameEngine  # noqa: E402
from engine.highscores import Highscores  # noqa: E402
from engine.shared import Direction, State  # noqa: E402
from frontend.app import Application, Screen  # noqa: E402
from frontend.paths import default_config, score_path  # noqa: E402


ROOT = Path(__file__).resolve().parent.parent


class FrontendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.scores = self.folder / "nested/scores.json"
        self.engine = GameEngine(ROOT / "config.json", self.scores)
        self.app = Application(self.engine)

    def tearDown(self) -> None:
        pygame.quit()
        self.temp.cleanup()

    def key(self, key: int) -> None:
        self.app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))

    def text(self, text: str) -> None:
        self.app.handle_event(pygame.event.Event(pygame.TEXTINPUT, text=text))

    def start_moving(self) -> None:
        self.app.start()
        x, y = self.app.snapshot.player
        walls = self.app.snapshot.walls[y][x]
        keys = (pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT)
        self.key(next(key for key, wall in zip(keys, walls) if not wall))
        for _ in range(12):
            self.app.update(1 / 60)

    def test_menu_keyboard_routes_and_wraps(self) -> None:
        self.key(pygame.K_UP)
        self.assertEqual(self.app.selected, 3)
        self.key(pygame.K_DOWN)
        self.key(pygame.K_DOWN)
        self.key(pygame.K_RETURN)
        self.assertIs(self.app.screen, Screen.SCORES)
        self.key(pygame.K_ESCAPE)
        self.key(pygame.K_s)
        self.key(pygame.K_s)
        self.key(pygame.K_RETURN)
        self.assertIs(self.app.screen, Screen.INSTRUCTIONS)
        self.key(pygame.K_ESCAPE)
        self.key(pygame.K_RETURN)
        self.assertIs(self.app.screen, Screen.PLAYING)

    def test_all_movement_keys_reach_engine(self) -> None:
        self.app.start()
        for keys, direction in (
                ((pygame.K_UP, pygame.K_w), Direction.UP),
                ((pygame.K_DOWN, pygame.K_s), Direction.DOWN),
                ((pygame.K_LEFT, pygame.K_a), Direction.LEFT),
                ((pygame.K_RIGHT, pygame.K_d), Direction.RIGHT)):
            for key in keys:
                self.key(key)
                self.assertIs(self.engine.player.requested_direction, direction)

    def test_pause_freezes_engine_and_resume_moves_again(self) -> None:
        self.start_moving()
        self.key(pygame.K_p)
        before = self.engine.snapshot()
        self.assertIs(before.state, State.PAUSED)
        for _ in range(90):
            self.app.update(1 / 60)
        after = self.engine.snapshot()
        self.assertEqual(before, after)
        self.key(pygame.K_p)
        self.app.update(1 / 60)
        self.assertLess(self.app.snapshot.time_left, before.time_left)

    def test_focus_loss_pauses_and_menu_restart_resets(self) -> None:
        self.start_moving()
        self.app.handle_event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        self.assertIs(self.app.screen, Screen.PAUSED)
        self.key(pygame.K_DOWN)
        self.key(pygame.K_RETURN)
        self.assertIs(self.app.screen, Screen.MENU)
        self.app.start()
        self.assertEqual(self.app.snapshot.score, 0)
        self.assertIs(self.app.snapshot.state, State.PLAYING)
        self.assertIsNone(self.app.snapshot.player_direction)

    def test_victory_name_errors_and_persistent_save(self) -> None:
        self.app.start()
        self.engine.cheat("end_game")
        self.app.update(1 / 60)
        self.assertIs(self.app.screen, Screen.RESULT)
        self.assertIs(self.app.snapshot.state, State.VICTORY)
        self.key(pygame.K_RETURN)
        self.assertTrue(self.app.error)
        self.assertIs(self.app.screen, Screen.RESULT)
        self.text("é")
        self.assertIn("English", self.app.error)
        self.text("ABCDEFGHIJK")
        self.assertIn("10", self.app.error)
        self.text("PLAYER 1")
        self.key(pygame.K_BACKSPACE)
        self.text("2")
        score = self.app.snapshot.score
        self.key(pygame.K_RETURN)
        self.assertIs(self.app.screen, Screen.MENU)
        self.assertEqual(Highscores(self.scores).top(),
                         [{"name": "PLAYER 2", "score": score}])

    def test_game_over_and_skip_does_not_save(self) -> None:
        self.app.start()
        # A backend state change is a fixture, never frontend game logic.
        self.engine.rules.lives = 0
        self.app.update(1 / 60)
        self.assertIs(self.app.snapshot.state, State.GAME_OVER)
        self.assertIs(self.app.screen, Screen.RESULT)
        self.key(pygame.K_ESCAPE)
        self.assertIs(self.app.screen, Screen.MENU)
        self.assertFalse(self.scores.exists())

    def test_write_failure_stays_on_entry_and_can_retry(self) -> None:
        self.engine.highscores.submit("PREVIOUS", 123)
        previous = self.scores.read_bytes()
        self.app.start()
        self.engine.cheat("end_game")
        self.app.update(1 / 60)
        self.text("PLAYER")
        with patch("engine.highscores.os.replace", side_effect=OSError("full")):
            self.key(pygame.K_RETURN)
        self.assertIs(self.app.screen, Screen.RESULT)
        self.assertIn("save", self.app.error)
        self.assertEqual(self.engine.highscores.top(),
                         [{"name": "PREVIOUS", "score": 123}])
        self.assertEqual(self.scores.read_bytes(), previous)
        self.assertEqual(list(self.scores.parent.glob("*.tmp")), [])
        self.key(pygame.K_RETURN)
        self.assertTrue(self.scores.is_file())

    def test_top_ten_sorted_and_loaded_after_restart(self) -> None:
        for i in range(12):
            self.assertTrue(self.engine.highscores.submit(f"P{i}", i * 10))
        scores = Highscores(self.scores).top()
        self.assertEqual(len(scores), 10)
        self.assertEqual(scores[0]["score"], 110)
        self.assertEqual(scores[-1]["score"], 20)
        self.app.navigate(Screen.SCORES)
        self.app.draw()

    def test_resized_mouse_hit_testing_and_letterboxing(self) -> None:
        self.app.window = pygame.display.set_mode((900, 500), pygame.RESIZABLE)
        self.app.present()
        viewport = self.app.viewport
        position = (viewport.x + (56 + 30) * viewport.width / 1280,
                    viewport.y + (454 + 20) * viewport.height / 840)
        self.app.handle_event(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, pos=position, button=1))
        self.assertIs(self.app.screen, Screen.PLAYING)
        self.assertEqual(viewport.height, 500)
        self.assertGreater(viewport.x, 0)

    def test_large_frame_is_bounded(self) -> None:
        self.start_moving()
        before = self.app.snapshot.time_left
        self.app.update(20)
        self.assertGreaterEqual(self.app.snapshot.time_left, before - .101)

    def test_custom_maze_sizes_render_all_screens(self) -> None:
        custom = self.folder / "config.json"
        custom.write_text(json.dumps({
            "levels": [{"width": 15, "height": 20}] * 10,
        }))
        app = Application(GameEngine(custom, self.scores))
        for screen in Screen:
            app.navigate(screen)
            app.draw()
            app.present()
        self.assertEqual((app.snapshot.width, app.snapshot.height), (15, 20))

    def test_close_event_exits(self) -> None:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.app.run()
        self.assertFalse(self.app.running)


class PathTests(unittest.TestCase):
    def test_explicit_config_resolves_relative_score_next_to_config(self) -> None:
        config = Path("/tmp/arcade-config/settings.json")
        self.assertEqual(score_path("scores/top.json", config),
                         Path("/tmp/arcade-config/scores/top.json").resolve())

    def test_default_and_user_config_from_another_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"PACMAN_DATA_DIR": directory}):
                self.assertEqual(default_config(), ROOT / "config.json")
                self.assertEqual(score_path("scores.json", None),
                                 Path(directory).resolve() / "scores.json")
                (Path(directory) / "config.json").write_text("{}")
                self.assertEqual(default_config(),
                                 Path(directory).resolve() / "config.json")
            (Path(directory) / "config.json").unlink()
            env = dict(os.environ, PACMAN_DATA_DIR=directory)
            result = subprocess.run(
                [sys.executable, str(ROOT / "pac-man.py"), "--smoke-test"],
                cwd=directory, env=env, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("20x15; 4 ghosts", result.stdout)
            self.assertIn(str(ROOT / "config.json"), result.stdout)


if __name__ == "__main__":
    unittest.main()
