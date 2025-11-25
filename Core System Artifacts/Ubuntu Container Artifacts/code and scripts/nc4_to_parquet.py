#!/usr/bin/env python3
import sys, os, json, subprocess, re, numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq

if len(sys.argv) < 4:
    print("usage: nc4_to_parquet.py <in.nc4> <out_dir> <var>"); sys.exit(2)
in_nc, out_dir, var = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out_dir, exist_ok=True)

# 1) Read header for shape & dtype
hdr = subprocess.check_output(["h5dump", "-H", "-d", var, in_nc], text=True)
# Example lines contain: DATATYPE  H5T_IEEE_F32LE  or H5T_IEEE_F64LE / H5T_STD_I32LE, etc.
dtype_map = {
    "H5T_IEEE_F32": np.float32, "H5T_IEEE_F64": np.float64,
    "H5T_STD_I8": np.int8, "H5T_STD_I16": np.int16, "H5T_STD_I32": np.int32, "H5T_STD_I64": np.int64,
    "H5T_STD_U8": np.uint8, "H5T_STD_U16": np.uint16, "H5T_STD_U32": np.uint32, "H5T_STD_U64": np.uint64,
}
dtype_key = None
for k in dtype_map:
    if k in hdr: dtype_key = k; break
if dtype_key is None: raise SystemExit("Unsupported dtype in HDF5 header")

# Parse shape: look for 'DATASPACE  SIMPLE { (dim0, dim1, ...)}'
m = re.search(r"SIMPLE\s*\{\s*\(([^)]*)\)", hdr)
if not m: raise SystemExit("Could not parse dataspace shape")
shape = tuple(int(x.strip()) for x in m.group(1).split(","))

# 2) Dump raw binary of the dataset
bin_path = os.path.join(out_dir, "_tmp.bin")
subprocess.check_call(["h5dump", "-d", var, "-b", "LE", "-o", bin_path, in_nc])

# 3) Load binary into numpy
arr = np.fromfile(bin_path, dtype=dtype_map[dtype_key]).reshape(shape)
os.remove(bin_path)

# 4) Flatten to long form and write Parquet
nd = arr.ndim
vals = arr.reshape(-1)
idx = np.indices(shape).reshape(nd, -1).T
df = pd.DataFrame(idx, columns=[f"d{k}" for k in range(nd)])
# Cast to float64 for uniform downstream (SciDB expects double in our pipeline)
df["v"] = vals.astype(np.float64)

table = pa.Table.from_pandas(df, preserve_index=False)
pq.write_to_dataset(table, root_path=out_dir)
json.dump({"var": var, "shape": list(map(int, shape))}, open(os.path.join(out_dir, "_shape.json"), "w"))
print(out_dir)
