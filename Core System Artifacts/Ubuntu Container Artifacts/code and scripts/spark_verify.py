#!/usr/bin/env python3
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("verify-parquet").getOrCreate()

src = "/opt/scidb/19.11/io/dataset/t2m_parq"
ref = "/opt/scidb/19.11/io/checks/era5_t2m"

print("== Original Parquet ==")
spark.read.parquet(src).selectExpr("count(*) as n", "min(v)", "max(v)", "avg(v)").show()

print("== SciDB Export ==")
spark.read.parquet(ref).selectExpr("count(*) as n", "min(v)", "max(v)", "avg(v)").show()

spark.stop()
