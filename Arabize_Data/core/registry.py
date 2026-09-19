from pathlib import Path
import json, importlib.util
class GameRegistry:
    def __init__(self, path):
        self.base = Path(path).resolve().parent
        self.games = json.loads(Path(path).read_text(encoding='utf-8'))['games']
    def load(self, game):
        path = self.base / game['plugin']
        spec = importlib.util.spec_from_file_location('arabize_cotw_plugin', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
