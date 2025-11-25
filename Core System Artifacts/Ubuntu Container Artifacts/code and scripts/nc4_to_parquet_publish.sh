#!/usr/bin/env bash
set -euo pipefail
NC="${1:-/opt/scidb/19.11/io/initial_data.nc}"
VAR="${2:-t2m}"
OUT="/opt/scidb/19.11/io/dataset/t2m_parq"

python3 /opt/tools/nc4_to_parquet.py "$NC" "$OUT" "$VAR"
tar -C /opt/scidb/19.11/io/dataset -czf /tmp/t2m_parq.tgz t2m_parq
pgrep -f "http.server 8000" >/dev/null || nohup python3 -m http.server 8000 --directory /tmp >/dev/null 2>&1 &

H="$(hostname)"
IP="$(hostname -I | awk '{print $1}')"
echo "http://$H:8000/t2m_parq.tgz"
echo "http://$IP:8000/t2m_parq.tgz"