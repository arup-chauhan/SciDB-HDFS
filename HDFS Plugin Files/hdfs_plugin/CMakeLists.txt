cmake_minimum_required(VERSION 2.8)
project(hdfs_plugin)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
add_definitions(-DPROJECT_ROOT=\"/opt/scidb/19.11/\")

include_directories(
  /opt/scidb/19.11/include
  /opt/scidb/19.11/include/util
  /opt/scidb/19.11/include/extern
  /usr/local/include/hdfs
)

link_directories(/usr/local/hadoop/lib/native)

add_library(hdfs SHARED hdfs_loader.cpp)
