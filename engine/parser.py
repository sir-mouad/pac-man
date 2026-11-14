import commentjson
from typing import Any
from lark.exceptions import UnexpectedToken


DEFAULT_CONFIG: dict[str, Any] = {'highscore_filename': 'highscores.json',
                                  'levels': [{'width': 20, 'height': 15}
                                             for _ in range(11)],
                                  'lives': 10,
                                  'points_per_pacgum': 10,
                                  'points_per_super_pacgum': 50,
                                  'points_per_ghost': 200,
                                  'seed': 42,
                                  'level_max_time': 180}

NUM_LEVELS = 11


class Parser:
    """Load the JSON config and fill in defaults for bad or missing values."""

    def _read_config(self, path: Any) -> Any:
        """Read a config file, skipping lines that start with #."""
        try:
            with open(path, "r") as f:
                lines = []
                for line in f:
                    if not line.lstrip().startswith("#"):
                        lines.append(line)
                config = commentjson.loads("".join(lines))
                if not isinstance(config, dict):
                    print("WARNING: Format Valid but is not a dict ---> USE_DEFAULT_CONFIG")
                    return DEFAULT_CONFIG
            return config
        except UnexpectedToken:
            print("WARNING: Invlaid Json format ---> USE_DEFAUT_CONFIG")
        except OSError:
            print("WARNING: Warning: config.json not found "
                  "---> USE_DEFAULT_CONFIG")
        return DEFAULT_CONFIG

    def _check_arg(
            self, arg: str, values: Any) -> bool | None:
        """Check one config value; warn and return False when it is invalid."""
        try:
            if arg in ('lives', 'points_per_pacgum', 'points_per_super_pacgum',
                       'points_per_ghost', 'level_max_time', 'seed'):
                if int(values) > 0:
                    return True
                else:
                    raise ValueError
            if arg == 'highscore_filename':
                return True
            if arg == 'levels':
                for d in values:
                    for key, value in d.items():
                        if (key in ('height', 'width') and int(value) > 0):
                            continue
                        else:
                            raise ValueError
                return True
        except ValueError:
            print(f"WARNING: Invalid data in {arg} : {values}. "
                  "---> Use DEFAULT_VALUE.")
            return False
        return None

    def _build_config(self, config: Any) -> dict[str, Any]:
        """Keep valid settings and use defaults for bad or missing ones."""
        if config is DEFAULT_CONFIG:
            return config
        new_config: dict[str, Any] = {}
        for arg, value in config.items():
            if arg in DEFAULT_CONFIG:
                if self._check_arg(arg, value):
                    if arg == 'levels' and len(value) < NUM_LEVELS:
                        value.extend(
                            DEFAULT_CONFIG['levels'][:(NUM_LEVELS-len(value))])
                    if arg in ('lives', 'points_per_pacgum',
                               'points_per_super_pacgum', 'points_per_ghost',
                               'level_max_time', 'seed'):
                        value = int(value)
                else:
                    value = DEFAULT_CONFIG[arg]
                new_config[arg] = value
            else:
                print(f"WARNING: {arg} is Invalid  ---> ARG_IGNORED ")

        for ARG, VALUE in DEFAULT_CONFIG.items():
            if ARG not in new_config:
                print(f"WARNING: Missing {ARG} ---> Use DEFAULT_VALUE")
                new_config[ARG] = VALUE
        return new_config

    def get_config(self, config_path: Any = None) -> dict[str, Any]:
        """Load the config from config_path or the first argument."""
        try:
            config = self._read_config(config_path)
            new_config = self._build_config(config)
            return new_config
        except ValueError:
            print("WARNING: Invalid Json format ---> Use DEFAULT_CONFIG")
            return DEFAULT_CONFIG
