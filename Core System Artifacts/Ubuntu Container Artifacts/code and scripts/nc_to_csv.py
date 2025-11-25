#!/usr/bin/env python3
import sys, numpy as np, pandas as pd, xarray as xr, os
if len(sys.argv) < 3:
    print("usage: nc_to_csv.py <in.nc> <out.csv> [var_name]", file=sys.stderr); sys.exit(2)
in_nc, out_csv = sys.argv[1], sys.argv[2]
var_name = sys.argv[3] if len(sys.argv) > 3 else None
ds = xr.open_dataset(in_nc)
if var_name is None:
    var_name = next(iter(ds.data_vars.keys()))
da = ds[var_name].astype('float64')
shape = da.shape; nd = len(shape)
vals = da.values.reshape(-1)
idx = np.indices(shape, dtype=np.int64).reshape(nd, -1).T
cols = {f'd{k}': idx[:, k] for k in range(nd)}; cols['v'] = vals
df = pd.DataFrame(cols)
os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
df.to_csv(out_csv, index=False, header=False)
with open(out_csv + ".schema.txt", "w") as f:
    dims = ", ".join([f"d{k}=0:*:0:1000" for k in range(nd)])
    f.write(f"<v:double>[{dims}]\n")
print(f"WROTE rows={len(df)} ndims={nd} shape={shape} var='{var_name}' -> {out_csv}")
