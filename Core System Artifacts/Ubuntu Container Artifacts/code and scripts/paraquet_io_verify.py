#!/usr/bin/env python3
import time
from scidbpy import connect

DB   = "http://172.17.0.2:8080"
PATH = "/opt/scidb/19.11/io/parqtest/a10_parq_%d" % int(time.time())
URL  = "file://%s?format=parquet" % PATH

db = connect(DB)
q  = lambda afl, fetch=False: db.iquery(afl, fetch=fetch)

# 0) libraries (ok if already loaded)
q("load_library('accelerated_io_tools')")
q("load_library('bridge')")

# 1) make data
q("remove(a10)", fetch=False)
q("remove(a10_pq)", fetch=False)
q("store(build(<v:int64>[i=0:9,10,0], i), a10)", fetch=False)

# show what we actually have
print("schema(a10):", q("show(a10)", fetch=True).iloc[0,0])
print("sample a10:"); print(q("limit(scan(a10),5)", fetch=True))

# 2) write parquet and read back
q("xsave(a10, '%s')" % URL, fetch=False)
q("store(xinput('%s'), a10_pq)" % URL, fetch=False)

# show parquet echo
print("schema(a10_pq):", q("show(a10_pq)", fetch=True).iloc[0,0])
print("sample a10_pq:"); print(q("limit(scan(a10_pq),5)", fetch=True))

# 3) counts + exact diff (all DML)
cnt_a10    = q("aggregate(a10, count(*))", fetch=True).iloc[0,0]
cnt_a10_pq = q("aggregate(a10_pq, count(*))", fetch=True).iloc[0,0]
diff_sum   = q("aggregate(project(apply(join(project(apply(a10,v1,v),v1),"
              "                               project(apply(a10_pq,v2,v),v2)),"
              "                       diff, abs(v1 - v2)),diff),sum(diff))", fetch=True).iloc[0,0]

print("PATH:", PATH)
print("count(a10)   =", cnt_a10)
print("count(a10_pq)=", cnt_a10_pq)
print("sum(|v1-v2|) =", diff_sum)
print("OK" if cnt_a10==cnt_a10_pq and diff_sum==0 else "MISMATCH")