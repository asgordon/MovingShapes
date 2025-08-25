# examples/load_data.py

import movingshapes

print("movingshapes")
print("Version: ", movingshapes.__version__)

print("Loading IEC dataset...")
iecs = movingshapes.iec()
print(f"Loaded {len(iecs)} IEC performances.")

print("Loading 1-character Charades...")
charades1c = movingshapes.charades1c()
print(f"Loaded {len(charades1c)} 1-character performances.")

print("Loading 2-character Charades...")
charades2c = movingshapes.charades2c()
print(f"Loaded {len(charades2c)} 2-character performances.")

print("Loading Triangle COPA...")
tricopa = movingshapes.tricopa()
print(f"Loaded {len(tricopa)} Triangle COPA performances.")

