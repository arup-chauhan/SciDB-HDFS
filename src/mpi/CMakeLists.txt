########################################
# BEGIN_COPYRIGHT
#
# Copyright (C) 2008-2019 SciDB, Inc.
# All Rights Reserved.
#
# SciDB is free software: you can redistribute it and/or modify
# it under the terms of the AFFERO GNU General Public License as published by
# the Free Software Foundation.
#
# SciDB is distributed "AS-IS" AND WITHOUT ANY WARRANTY OF ANY KIND,
# INCLUDING ANY IMPLIED WARRANTY OF MERCHANTABILITY,
# NON-INFRINGEMENT, OR FITNESS FOR A PARTICULAR PURPOSE. See
# the AFFERO GNU General Public License for the complete license terms.
#
# END_COPYRIGHT
########################################

message(STATUS "****************** BEGIN src/mpi/CMakeLists.txt ******************")

# ---- MPI / ScaLAPACK DISABLED ----
# Skip all real MPI/ScaLAPACK detection and build a dummy stub instead.

set(MPI_CXX_FOUND FALSE)
set(MPI_Fortran_FOUND FALSE)
set(SCALAPACK_FOUND FALSE)
set(LAPACK_FOUND FALSE)
set(BLAS_FOUND FALSE)

# Provide a dummy MPI implementation so SciDB can link cleanly.
add_library(mpi STATIC ${CMAKE_CURRENT_SOURCE_DIR}/dummy_mpi.cpp)
target_link_libraries(mpi PUBLIC scidb_msg_lib Boost::boost)

# Provide a placeholder for mpi_test so plugins referencing it do not fail.
add_library(mpi_test STATIC ${CMAKE_CURRENT_SOURCE_DIR}/pluginNoMpi.cpp)
target_link_libraries(mpi_test PUBLIC Boost::boost)

message(WARNING "MPI/ScaLAPACK functionality disabled — SciDB will build without parallel linear algebra support.")
message(STATUS "****************** END src/mpi/CMakeLists.txt ******************")

