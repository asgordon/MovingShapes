# examples/save_movie.py

import movingshapes

iec = movingshapes.iec()
performance = iec[-1] # last performance in iec dataset
movie = movingshapes.Movie(performance)
movie.save("out.mp4")