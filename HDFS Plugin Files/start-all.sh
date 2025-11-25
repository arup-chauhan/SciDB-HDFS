#!/bin/bash
source /etc/profile
$HADOOP_HOME/bin/hdfs namenode -format -force
$HADOOP_HOME/sbin/start-dfs.sh
/opt/scidb/19.11/bin/scidbctl.py start scidb
tail -f /opt/scidb/19.11/DB-scidb/0/0/scidb-stdout.log

