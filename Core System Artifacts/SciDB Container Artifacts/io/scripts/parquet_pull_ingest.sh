#!/usr/bin/env bash
set -euo pipefail

SRC_URL="${1:?usage: parquet_pull_ingest.sh http://<ubuntu-ip>:8000/t2m_parq.tgz}"
DEST_DIR="/opt/scidb/19.11/io/dataset"
TMP="/tmp/t2m_parq.tgz"
PARQ_DIR="$DEST_DIR/t2m_parq"
IQUERY="/opt/scidb/19.11/bin/iquery"

command -v curl >/dev/null || (apt-get update && apt-get install -y curl)

mkdir -p "$DEST_DIR"
curl -fsSL "$SRC_URL" -o "$TMP"

rm -rf "$PARQ_DIR"
tar -C "$DEST_DIR" -xzf "$TMP"
ls -lah "$PARQ_DIR" | head

# make sure path is whitelisted (you already did this once; harmless if repeated)
grep -qxF "$DEST_DIR" /opt/scidb/19.11/etc/io-paths-list || echo "$DEST_DIR" >> /opt/scidb/19.11/etc/io-paths-list

# libs
$IQUERY -aq "load_library('accelerated_io_tools')" >/dev/null

# clean any old arrays
$IQUERY -naq "remove(t2m_long)" || true
$IQUERY -naq "remove(era5_t2m)" || true

# >>> ingest generic Parquet directory with AIO (NOT xinput) <<<
$IQUERY -naq "store(aio_input('file://$PARQ_DIR','parquet'), t2m_long)"

# redimension (3D d0,d1,d2 -> adjust if needed)
$IQUERY -naq "
store(
  redimension(
    project(
      apply(t2m_long,
            d0_i,int64(d0),
            d1_i,int64(d1),
            d2_i,int64(d2),
            v_d,double(v)),
      d0_i,d1_i,d2_i,v_d
    ),
    <v:double>[d0_i=0:*:0:16, d1_i=0:*:0:256, d2_i=0:*:0:256]
  ),
  era5_t2m
)"

# sanity
$IQUERY -aq "aggregate(t2m_long, count(*), min(v), max(v), avg(v))"
$IQUERY -aq "aggregate(era5_t2m, count(*), min(v), max(v), avg(v))"
$IQUERY -aq "limit(era5_t2m, 5)"