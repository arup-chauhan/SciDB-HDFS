from scidbpy import connect

IP = "172.17.0.2"  # <-- replace with your SciDB container IP
db = connect(f"http://{IP}:8080")

print(db.iquery("list('instances')", fetch=True).head(2))

for n in ("a1d","a2d","a2d_from1d"):
    try: db.iquery(f"remove({n})", fetch=False)
    except: pass

db.iquery("store(build(<v:int64>[i=0:99,100,0], i), a1d)", fetch=False)
print(db.iquery("limit(scan(a1d),5)", fetch=True))
print(db.iquery("aggregate(a1d, count(*), sum(v), avg(v), min(v), max(v))", fetch=True))

db.iquery("store(build(<v:int64>[x=0:9,10,0, y=0:9,10,0], x*10+y), a2d)", fetch=False)
print(db.iquery("limit(a2d,10)", fetch=True))
print(db.iquery("aggregate(a2d, sum(v) as row_sum, x)", fetch=True).head())

db.iquery("store(redimension(project(apply(a1d, x, i/10, y, i%10), x, y, v), <v:int64>[x=0:9,10,0, y=0:9,10,0]), a2d_from1d)", fetch=False)
print(db.iquery("limit(a2d_from1d,10)", fetch=True))

print(db.iquery("between(a2d, 2,2, 4,4)", fetch=True))
print(db.iquery("limit(filter(apply(a2d, w, v*2), w%7=0), 10)", fetch=True))

# one-arg form (array variable) — what already worked:
print(db.iquery("show(a2d)", fetch=True))

# two-arg form — give a valid AFL statement as a string:
print(db.iquery("show('scan(a2d)','afl')", fetch=True))
# or:
print(db.iquery("show('project(a2d, v)','afl')", fetch=True))
