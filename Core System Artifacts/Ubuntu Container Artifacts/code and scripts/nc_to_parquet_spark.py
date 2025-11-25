#!/usr/bin/env python3
"""
nc_to_parquet_spark.py

Convert a NetCDF4/HDF5 dataset to SciDB-bridge compatible Parquet using PySpark.
Schema: d0(int64), d1(int64), ... , v(double)

Usage:
  spark-submit nc_to_parquet_spark.py <in.nc4> <out_dir> <var> [--row-group-size 1000000]

Notes:
- Reads the NetCDF variable on the driver (netCDF4/h5py), flattens to long form,
  then parallelizes + writes Parquet with Snappy compression and controllable
  row group size (via parquet.block.size).
- Produces a sidecar JSON at <out_dir>/_shape.json with original shape + var.
"""
import argparse, json, os
from typing import List

import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, LongType, DoubleType
from pyspark.sql import Row

try:
    import netCDF4 as nc
except Exception:
    nc = None
try:
    import h5py  # fallback
except Exception:
    h5py = None


def read_nc_variable(path: str, var: str):
    """Return (ndarray values as float64, shape tuple). Prefer netCDF4, else h5py."""
    if nc is not None:
        ds = nc.Dataset(path, mode="r")
        try:
            v = ds.variables[var][:]
            arr = np.array(v)
            return arr.astype(np.float64, copy=False), tuple(arr.shape)
        finally:
            ds.close()
    if h5py is not None:
        with h5py.File(path, "r") as f:
            if var not in f:
                # try common group paths
                for k in f.keys():
                    if isinstance(f[k], h5py.Group) and var in f[k]:
                        dset = f[k][var]
                        break
                else:
                    dset = f[var]  # will raise
            else:
                dset = f[var]
            arr = dset[()]
            return np.array(arr, dtype=np.float64, copy=False), tuple(arr.shape)
    raise RuntimeError("Neither netCDF4 nor h5py available to read NetCDF/HDF5")


def chunk_indices(total: int, chunk_size: int):
    i = 0
    while i < total:
        j = min(i + chunk_size, total)
        yield i, j
        i = j


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("in_nc")
    ap.add_argument("out_dir")
    ap.add_argument("var")
    ap.add_argument("--row-group-size", type=int, default=1_000_000,
                    help="Approx rows per Parquet row group (controls parquet.block.size)")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Start Spark
    spark = (
        SparkSession.builder
        .appName("nc→parquet(scidb)")
        .config("spark.sql.parquet.compression.codec", "snappy")
        # parquet.block.size ≈ row-group-size * row-width (bytes); we just hint
        .config("parquet.block.size", str(128 * 1024 * 1024))
        .getOrCreate()
    )
    sc = spark.sparkContext

    # Load on driver and flatten
    arr, shape = read_nc_variable(args.in_nc, args.var)
    nd = len(shape)
    total = int(np.prod(shape))

    # Precompute all index tuples as int64 columns without materializing full ndarray of tuples
    # We generate ranges per-dimension and compute indices arithmetically in partitions.
    dims: List[int] = list(map(int, shape))

    # Broadcast essentials
    b_dims = sc.broadcast(dims)

    def make_rows(span):
        start, end = span
        dims = b_dims.value
        nd = len(dims)
        stride = [1]*nd
        for k in range(nd-2, -1, -1):
            stride[k] = stride[k+1]*dims[k+1]
        rows = []
        # Use memoryview over the flattened array segment for speed
        flat = arr.reshape(-1)
        for linear in range(start, end):
            rem = linear
            idx = [0]*nd
            for k in range(nd):
                q, rem = divmod(rem, stride[k]) if k < nd-1 else (rem, 0)
                idx[k] = q if k < nd-1 else rem
            v = float(flat[linear])
            rows.append(tuple(idx) + (v,))
        return rows

    # Partition spans roughly matching requested row-group size
    chunk = max(10_000, min(args.row_group_size, total))
    spans = list(chunk_indices(total, chunk))
    rdd = sc.parallelize(spans, numSlices=max(1, len(spans)))
    row_rdd = rdd.flatMap(make_rows)

    # Build schema d0..d{nd-1}, v
    fields = [StructField(f"d{k}", LongType(), False) for k in range(nd)] + [StructField("v", DoubleType(), True)]
    schema = StructType(fields)
    df = spark.createDataFrame(row_rdd.map(lambda t: Row(*t)), schema=schema)

    # Write Parquet dataset (files directly under out_dir)
    (df
     .repartition(max(1, df.rdd.getNumPartitions()))
     .write
     .mode("overwrite")
     .parquet(args.out_dir))

    # Sidecar shape
    with open(os.path.join(args.out_dir, "_shape.json"), "w") as f:
        json.dump({"var": args.var, "shape": [int(x) for x in shape]}, f)

    print(args.out_dir)
    spark.stop()


if __name__ == "__main__":
    main()
