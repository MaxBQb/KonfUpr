from pathlib import Path
from json import dumps
_gdata = dict()
exec(Path("config.py").read_text(), _gdata)
print(dumps(_gdata['users'], indent=2))
