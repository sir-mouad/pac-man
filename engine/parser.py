import sys
import commentjson
from pathlib import Path

CONFIG_PATH = sys.argv[1]

DEFAULT_CONFIG = {'highscore_filename': 'highscores.json',
                  'levels': [{'width': 20, 'height': 15} for _ in range(10)],
                  'lives': 3,
                  'points_per_pacgum': 10,
                  'points_per_super_pacgum': 50,
                  'points_per_ghost': 200,
                  'seed': 42,
                  'level_max_time': 90}


class Parser:
    def _read_config(self, path=CONFIG_PATH):
        with open(path, "r") as f:
            lines = []
            for line in f:
                if not line.lstrip().startswith("#"):
                    lines.append(line)
        return commentjson.loads("".join(lines))

    def _check_arg(self, arg, values):
        try:
            if arg in ('lives', 'points_per_pacgum', 'points_per_super_pacgum', 'points_per_ghost', 'level_max_time', 'seed'):
                int(values)
                return True
            if arg == 'highscore_filename':
                if Path(values).suffix == ".json":
                    return True
            if arg == 'levels':
                for d in values:
                    for key, value in d.items():
                        if (key in ('height', 'width') and int(value)):
                            continue
                        else:
                            raise ValueError
                return True
        except ValueError:
            print(f"WARNING: Invalid data in {arg} : {values}. "
                  "---> Use DEFAULT_VALUE.")
            return False

    def _build_config(self, config):
        new_config = {}
        for arg, value in config.items():
            if arg in DEFAULT_CONFIG:
                if self._check_arg(arg, value):
                    if arg == 'levels' and len(value) < 10:
                        value.extend(
                            DEFAULT_CONFIG['levels'][:(10-len(value))])
                    if arg in ('lives', 'points_per_pacgum', 'points_per_super_pacgum', 'points_per_ghost', 'level_max_time', 'seed'):
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

    def get_config(self):
        try:
            config = self._read_config()
            new_config = self._build_config(config)
            return new_config
        except ValueError as e:
            print(f"WARNING: Invalid Json format ---> Use DEFAULT_CONFIG")
            return DEFAULT_CONFIG
