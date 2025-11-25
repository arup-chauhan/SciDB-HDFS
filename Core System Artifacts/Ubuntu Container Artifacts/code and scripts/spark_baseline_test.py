from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("check-parq").getOrCreate()

src = "/opt/scidb/19.11/io/dataset/t2m_parq"
df  = spark.read.parquet(src)
df.selectExpr("count(*) as n", "min(v)", "max(v)", "avg(v)").show()
