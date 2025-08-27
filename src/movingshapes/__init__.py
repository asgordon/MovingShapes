# src/movingshapes/__init__.py

__version__ = "0.1.0"

from .moving_shapes import iec, charades1c, charades2c, tricopa
from .moving_shapes import Performance
from .moving_shapes import COLUMN_LABELS, STAGES

from .movie import Movie

# Define public API
__all__ = [
    "iec",
    "charades1c",
    "charades2c",
    "tricopa",
    "Performance",
    "COLUMN_LABELS",
    "STAGES",
    "Movie",
    "__version__",
]

