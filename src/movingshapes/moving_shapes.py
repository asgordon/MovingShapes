# moving_shapes.py
# Animation datasets from Charades and HSIT web applications
# Andrew S. Gordon

import os, json, re

COLUMN_LABELS = ['ms', 'btx', 'bty', 'btr', 'ltx', 'lty', 'ltr', 'cx', 'cy', 'cr', 'dr']
STAGES = ['bt', 'bt-lt', 'box-bt-lt-c']

IEC_PATH = os.path.join(os.path.dirname(__file__), 'iec')
IEC_DATA_PATH = os.path.join(IEC_PATH, 'data')
IEC_JSON_PATH = os.path.join(IEC_PATH, 'extra-credit-text-only.json')
IEC_IDS_PATH = os.path.join(IEC_PATH, 'ids.txt')

CHARADES_PATH = os.path.join(os.path.dirname(__file__), 'charades')
CHARADES_1C_PATH = os.path.join(CHARADES_PATH, '1-character-data')
CHARADES_2C_PATH = os.path.join(CHARADES_PATH, '2-character-data')
CHARADES_2C_LABELS = ['accompany', 'argue with', 'avoid', 'block', 'capture', 'chase', 'creep up on', 'encircle', 'follow', 'herd', 'hit', 'huddle with', 'kiss', 'lead', 'leave', 'mimic', 'poke', 'pull', 'push', 'scratch', 'throw', 'flirt with', 'hug', 'talk to', 'play with', 'approach', 'bother', 'escape', 'tickle', 'examine', 'ignore', 'fight']
CHARADES_1C_LABELS = ['accelerate', 'bolt', 'bow', 'creep', 'dance', 'drift', 'flinch', 'fly', 'gallop', 'glide', 'hop', 'jump', 'limp', 'march', 'meander', 'nod', 'roam', 'roll', 'run', 'scurry', 'shake', 'decelerate', 'stroll', 'strut', 'stumble', 'swim', 'trudge', 'turn', 'waddle', 'wave', 'spin']

TRICOPA_PATH = os.path.join(os.path.dirname(__file__), 'trianglecopa')
TRICOPA_DATA_PATH = os.path.join(TRICOPA_PATH, 'data')
TRICOPA_ID_PATH = os.path.join(TRICOPA_PATH, 'performance_ids.txt')

def load_data(fn):
    with open(fn) as file: result = _parse(file.read())
    return result

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
    with open(IEC_JSON_PATH) as f: iec_json = json.load(f)
    for d in iec_json:
        id = d['id']
        title = d['title']
        narrative = d['note']
        data = load_data(os.path.join(IEC_DATA_PATH, "{}.txt".format(str(id))))
        stage = 'box-bt-lt-c'
        res.append(Performance(id = id, stage = stage, data = data, title = title, narrative = narrative))
    return res

def _get_datum_paths(directory):
    file_paths = []
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            file_paths.append(file_path)
    return file_paths

def charades1c():
    '''returns a list of 2611 Performance objects representing the 1-character Triangle Charades dataset'''
    res = []
    pattern = r".+\.txt$"
    for label in CHARADES_1C_LABELS:
        for datum_path in _get_datum_paths(os.path.join(CHARADES_1C_PATH, label)):
            basename = os.path.basename(datum_path)
            match = re.search(pattern, basename) # looking for "###.txt"
            if match:
                id = ''.join([char for char in basename if char.isnumeric()])
                stage = 'bt'
                data = load_data(datum_path)
                res.append(Performance(id = id, stage = stage, data = data, label = label))
    return res

def charades2c():
    '''returns a list of 1319 Performance objects representing the 2-character Triangle Charades dataset'''
    res = []
    pattern = r".+\.txt$"
    for label in CHARADES_2C_LABELS:
        for datum_path in _get_datum_paths(os.path.join(CHARADES_2C_PATH, label)):
            basename = os.path.basename(datum_path)
            match = re.search(pattern, basename) # looking for "###.txt"
            if match:
                id = ''.join([char for char in basename if char.isnumeric()])
                stage = 'bt-lt'
                data = load_data(datum_path)
                res.append(Performance(id = id, stage = stage, data = data, label = label))
    return res

def tricopa():
    '''returns a list of 100 Performance objects representing each of the 100 Triangle COPA animations'''
    res = []
    ids = {}
    with open(TRICOPA_ID_PATH) as f:
        lines = f.readlines()
        for line in lines[1:]:
            parts = line.split()
            ids[parts[0]] = parts[1]
    for i in range(100): # 0 to 99
        question = str(i + 1)
        id = ids[question]
        data = load_data(os.path.join(TRICOPA_DATA_PATH, "{}.txt".format(id)))
        stage = 'box-bt-lt-c'
        title = "Question " + question
        res.append(Performance(id = id, stage = stage, data = data, title = title ))
    return res