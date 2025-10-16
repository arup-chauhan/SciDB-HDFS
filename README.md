# **SciDB with HDFS Integration**

A scalable extension to **SciDB 19.11**, enabling **direct read/write operations on Hadoop Distributed File System (HDFS)** — bridging array databases with distributed storage systems.

---

## **Table of Contents**

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Solution — Custom HDFS Plugin](#solution--custom-hdfs-plugin)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Repository Structure](#repository-structure)
- [License](#license)

---

## **Project Overview**

**SciDB** is an open-source, array-based database designed for managing and analyzing large-scale multidimensional scientific data.
It provides versioned arrays, efficient parallel query execution, and a declarative language (AFL/AQL) optimized for high-dimensional analytics.

While powerful for structured analytical workloads, SciDB traditionally depends on **local file systems** or MPI-based I/O. This creates friction when integrating with modern distributed data environments built on **HDFS** and **Spark**.

---

## **Problem Statement**

Most scientific workflows today rely on distributed storage like **HDFS** for scalable ingestion, persistence, and interoperability with machine-learning pipelines.
However, SciDB’s default setup lacked native HDFS support, forcing manual data movement between systems and limiting its ability to participate in multi-node, data-intensive pipelines.

---

## **Solution — Custom HDFS Plugin**

We developed a **custom HDFS I/O plugin** that enables SciDB to:

- Seamlessly read and write array data directly from HDFS.
- Replace MPI-based transfer mechanisms with distributed HDFS operations.
- Integrate cleanly into containerized or cloud-based SciDB deployments.
- Support binary formats like **NetCDF**, CSV, and compressed block storage.

This plugin removes redundancy between HDFS and SciDB storage layers, achieving **data locality**, **streamed ingestion**, and **parallel I/O** suitable for large ML and analytics workloads.

---

## **Architecture**

```plaintext
                +---------------------------+
                |        HDFS Storage       |
                +---------------------------+
                           ↑      ↓
                    [ Custom HDFS Plugin ]
                           ↑      ↓
                +---------------------------+
                |          SciDB            |
                | (AFL/AQL, Array Engine)   |
                +---------------------------+
                           ↑
                +---------------------------+
                |   ML / Analytics Layer    |
                |  (Spark, Dask, TensorFlow)|
                +---------------------------+
```

- **Data Flow:** HDFS ↔ Plugin ↔ SciDB Arrays ↔ ML Pipelines
- **Built with:** C++ (Boost, libhdfs), Bash install scripts, Docker build support

---

## **Installation & Setup**

### **Prerequisites**

- Ubuntu 16.04 (Xenial)
- SciDB 19.11 Community Edition packages (`.deb`)
- Optional tarball (`scidb-19.11.tar.gz`)
- Hadoop 2.7+ or HDFS cluster
- Docker (optional for container deployment)

### **Steps**

```bash
# Clone repository
git clone https://github.com/<your-user>/SciDB-HDFS-Integration.git
cd SciDB-HDFS-Integration

# Install SciDB CE (if not installed)
chmod +x install-scidb-ce.sh
sudo ./install-scidb-ce.sh

# Build and register plugin
mkdir build && cd build
cmake ..
make
sudo make install
```

---

## **Usage**

```bash
# Example AFL query loading data from HDFS
iquery -aq "load(hdfs('/data/array_chunk_01.nc'), 'array_schema')"

# Export SciDB array back to HDFS
iquery -aq "save(array_name, hdfs('/exports/array_result.bin'))"
```

This allows two-way data exchange between SciDB and Hadoop without intermediate local copies.

---

## **Repository Structure**

```plaintext
SciDB-HDFS-Integration/
├── Dockerfile
├── install-scidb-ce.sh
├── scidb-19.11-xenial/
│   ├── *.deb
│   └── scidb-19.11.tar.gz
├── hdfs-plugin/
│   ├── CMakeLists.txt
│   ├── src/
│   ├── include/
│   └── README.md
└── docs/
    └── architecture.png
```

---

## **License**

This project follows the **AGPL v3** license, consistent with SciDB Community Edition.

---
