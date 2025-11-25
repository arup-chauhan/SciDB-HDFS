#!/usr/bin/env python3
import sys, os, json
import numpy as np, pandas as pd
from scipy.io import netcdf
import pyarrow as pa, pyarrow.parquet as pq

if len(sys.argv) < 3:
    print("usage: nc_to_parquet.py <in.nc> <out_dir> [var]")
    sys.exit(2)

in_nc, out_dir = sys.argv[1], sys.argv[2]
var = sys.argv[3] if len(sys.argv) > 3 else None
os.makedirs(out_dir, exist_ok=True)

with netcdf.netcdf_file(in_nc, 'r') as ds:
    if var is None:
        var = list(ds.variables.keys())[0]
    arr = ds.variables[var].data.copy()

shape = arr.shape
nd = arr.ndim
vals = arr.reshape(-1)
idx = np.indices(shape).reshape(nd, -1).T
df = pd.DataFrame(idx, columns=[f"d{k}" for k in range(nd)])
df["v"] = vals.astype(float)

table = pa.Table.from_pandas(df, preserve_index=False)
pq.write_to_dataset(table, root_path=out_dir)
json.dump({"var": var, "shape": list(map(int, shape))},
          open(os.path.join(out_dir, "_shape.json"), "w"))
print(out_dir)