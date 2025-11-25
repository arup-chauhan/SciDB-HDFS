#!/usr/bin/python3.5
from netCDF4 import Dataset
import sys, csv, numpy as np
if len(sys.argv)<3:
    print("usage: nc_to_csv_sys35.py <in.nc> <out.csv> [var]", file=sys.stderr); sys.exit(2)
fn,out=sys.argv[1],sys.argv[2]
var=sys.argv[3] if len(sys.argv)>3 else None
ds=Dataset(fn,"r")
if var is None:
    data_vars=[k for k,v in ds.variables.items() if getattr(v,'ndim',0)>0 and k not in ds.dimensions]
    var=data_vars[0]
da=ds.variables[var][:]
shape=da.shape; nd=len(shape)
vals=da.reshape(-1)
idx=np.indices(shape).reshape(nd,-1).T
with open(out,"w") as f:
    w=csv.writer(f)
    for row,val in zip(idx,vals): w.writerow(list(map(int,row))+[float(val)])
open(out+".schema.txt","w").write("<v:double>["+ ", ".join("d{}=0:*:0:1000000".format(k) for k in range(nd)) +"]")
print(var)
