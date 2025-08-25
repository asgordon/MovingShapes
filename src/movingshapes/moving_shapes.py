# moving_shapes.py
# Animation datasets from Charades and HSIT web applications
# Andrew S. Gordon

import json, re, pkgutil, importlib.resources

COLUMN_LABELS = ['ms', 'btx', 'bty', 'btr', 'ltx', 'lty', 'ltr', 'cx', 'cy', 'cr', 'dr']
STAGES = ['bt', 'bt-lt', 'box-bt-lt-c']


CHARADES_2C_LABELS = ['accompany', 'argue with', 'avoid', 'block', 'capture', 'chase', 'creep up on', 'encircle', 'follow', 'herd', 'hit', 'huddle with', 'kiss', 'lead', 'leave', 'mimic', 'poke', 'pull', 'push', 'scratch', 'throw', 'flirt with', 'hug', 'talk to', 'play with', 'approach', 'bother', 'escape', 'tickle', 'examine', 'ignore', 'fight']
CHARADES_1C_LABELS = ['accelerate', 'bolt', 'bow', 'creep', 'dance', 'drift', 'flinch', 'fly', 'gallop', 'glide', 'hop', 'jump', 'limp', 'march', 'meander', 'nod', 'roam', 'roll', 'run', 'scurry', 'shake', 'decelerate', 'stroll', 'strut', 'stumble', 'swim', 'trudge', 'turn', 'waddle', 'wave', 'spin']

def _get_data(filename):
    data = pkgutil.get_data("movingshapes", filename)
    if data is None:
        raise FileNotFoundError(f"Data file not found: {filename}")
    return data.decode("utf-8")

def _parse(raw):
    result = []
    for line in raw.splitlines():
        parts = line.split()
        values = [int(parts[0])] + [float(part) for part in parts[1:]]
        result.append(values)
    return result

class Performance():

    def __init__(self, id = None, stage = None, data = None, title = None, narrative = None, label = None):
        self.id = id
        self.stage = stage
        self.data = data
        self.title = title
        self.narrative = narrative
        self.label = label

def iec():
    '''returns a list of 131 Performance objects representing the IEC dataset'''
    res = []
    json_data = _get_data("iec/extra-credit-text-only.json")
    iec_json = json.loads(json_data)
    for d in iec_json:
        id = d['id']
        title = d['title']
        narrative = d['note']
        data = _parse(_get_data(f"iec/data/{id}.txt"))
        stage = 'box-bt-lt-c'
        res.append(Performance(id = id, stage = stage, data = data, title = title, narrative = narrative))
    return res

def _get_datum_paths(directory):
    try:
        data_dir = importlib.resources.files("movingshapes").joinpath(directory)
        return [f.name for f in data_dir.iterdir() if f.is_file()]
    except Exception as e:
        print(f"Error: {e}")
        return []

def charades1c():
    '''returns a list of 2611 Performance objects representing the 1-character Triangle Charades dataset'''
    res = []
    pattern = r".+\.txt$"
    for label in CHARADES_1C_LABELS:
        for filename in _get_datum_paths(f"charades/1-character-data/{label}"):
            match = re.search(pattern, filename) # looking for "###.txt"
            if match:
                id = ''.join([c for c in filename if c.isdigit()])
                stage = 'bt'
                data = _parse(_get_data(f"charades/1-character-data/{label}/{filename}"))
                res.append(Performance(id=id, stage=stage, data=data, label=label))
    return res

def charades2c():
    '''returns a list of 1319 Performance objects representing the 2-character Triangle Charades dataset'''
    res = []
    pattern = r".+\.txt$"
    for label in CHARADES_2C_LABELS:
        for filename in _get_datum_paths(f"charades/2-character-data/{label}"):
            match = re.search(pattern, filename) # looking for "###.txt"
            if match:
                id = ''.join([char for char in filename if char.isdigit()])
                stage = 'bt-lt'
                data = _parse(_get_data(f"charades/2-character-data/{label}/{filename}"))
                res.append(Performance(id = id, stage = stage, data = data, label = label))
    return res

def tricopa():
    '''returns a list of 100 Performance objects representing each of the 100 Triangle COPA animations'''
    res = []
    ids = {}
    ids_data = _get_data("trianglecopa/performance_ids.txt")
    lines = ids_data.splitlines()
    for line in lines[1:]:
        parts = line.split()
        ids[parts[0]] = parts[1]
    for i in range(100): # 0 to 99
        question = str(i + 1)
        id = ids[question]
        data = _parse(_get_data(f"trianglecopa/data/{id}.txt"))
        stage = 'box-bt-lt-c'
        title = "Question " + question
        res.append(Performance(id = id, stage = stage, data = data, title = title ))
    return res
