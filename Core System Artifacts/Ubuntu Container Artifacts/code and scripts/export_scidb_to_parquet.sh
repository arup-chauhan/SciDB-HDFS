#!/bin/bash
/opt/scidb/19.11/bin/iquery -aq \
"aio_save(era5_t2m, 'file:///opt/scidb/19.11/io/checks/era5_t2m', 'format=parquet instances=(0)')"
