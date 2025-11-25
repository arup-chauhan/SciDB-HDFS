# SciDB Optimization

This is an end-to-end system built around SciDB 19.11 that supports distributed ingestion, multi-layer query processing, with a form of multi-tenant query isolation, load simulation, variant-based benchmarking, and a prototype machine learning framework for adaptive query optimization.

The system is fully containerized and provides a reproducible workflow for handling large scientific datasets, generating parallel load, and experimenting with learned cost models and scheduling policies.

---

## 1. Project Overview

The project consists of four major layers:

### 1. Environment Layer

Reproducible SciDB and Spark environment with all dependencies rebuilt and configured.

### 2. Distributed I/O and Ingestion Layer

Support for ingesting large datasets into SciDB using Accelerated I/O with interoperability through Arrow and Parquet.

### 3. Query Control Plane

A custom canonicalization and variant generation pipeline implemented in C++ that standardizes incoming queries and produces alternate execution formulations.

### 4. Benchmarking and ML Layer

A Python benchmarking engine that collects execution metrics and an experimental ML module that uses those metrics to evaluate and improve query performance.

This architecture allows experiments on workload behavior, plan selection, tail latency, and multi-tenant scheduling.

---

## 2. Architecture Diagram

            +------------------------------+
            |        Client Queries        |
            +---------------+--------------+
                            |
                            v
           +------------------------------------+
           |         Query Control Plane         |
           |  Canonicalizer + Variant Generator  |
           +----------------+--------------------+
                            |
                 AFL Variants + Metadata
                            |
                            v
        +----------------------------------------+
        |        Benchmark Execution Layer       |
        |   SciDB Runner + Metrics Collector     |
        +----------------+------------------------+
                            |
                     Metrics + Features
                            |
                            v
            +-------------------------------+
            |       ML Analysis Layer       |
            |    SVM + DQN (Prototype)      |
            +-------------------------------+
                            |
                            v
            +-------------------------------+
            |       Performance Insights     |
            +-------------------------------+

---

## 3. Environment Setup

The system runs on two coordinated containers:

### SciDB Environment

- SciDB 19.11
- Shim service
- Accelerated I/O support
- Arrow and Parquet runtime libraries

### Spark Environment

- Spark 3.3.2
- Java 17
- Python 3.10
- Used to generate synthetic data and simulate concurrent workloads

Both containers share a mounted directory that acts as the I/O workspace. This avoids distributed filesystem dependencies and keeps ingest paths fast and simple.

---

## 4. Distributed I/O and Ingestion

### CSV and NetCDF Support

- Conversion utilities for NetCDF to long-form CSV
- Ingestion scripts for structured CSV and dimensional redimensioning in SciDB

### Accelerated I/O Integration

SciDB Accelerated I/O (AIO) is used to:

- Import CSV at scale
- Export arrays as Parquet shards
- Maintain parallelism by allowing each SciDB instance to read or write its region independently

### Arrow and Parquet Interoperability

Arrow C++ and Parquet C++ libraries are built into the environment so that:

- Data exported by SciDB can be consumed by Spark and Python directly
- Future ingestion formats can be evaluated for performance benefits

---

## 5. Query Control Plane

A standalone C++ module handles query processing before execution on SciDB. It includes:

### Canonical Parser (Flex/Bison)

- Parses AQL/AFL queries
- Produces a deterministic AST format
- Normalizes ordering of joins, filters, projections, and identifiers

### Variant Generation

- Generates alternate logical formulations of the same query
- Supports transformations like join reordering, predicate pushdown, and projection pruning
- Produces executable AFL strings through a grammar-based emitter

### Metadata Management

- Assigns lightweight tags for tracking
- Stores canonical and variant forms for benchmarking

This layer ensures all queries entering the system follow a consistent, analyzable format suitable for ML-driven evaluation.

---

## 6. Benchmark Runner

A Python-based execution module performs:

### Variant Execution

- Executes each AFL variant against a SciDB sandbox instance
- Tracks per-run information with unique identifiers

### Metrics Collection

Measured values include:

- Latency
- CPU usage
- Memory footprint
- Disk I/O
- CPU skew

### Feature Store Integration

All records are stored in a PostgreSQL schema designed for:

- Benchmark aggregation
- ML model training
- Drift analysis and reproducibility

---

## 7. Machine Learning Module

A prototype ML layer evaluates and predicts plan performance.

### SVM Cost Model

- Uses benchmark data to classify plan variants
- Identifies variants likely to perform well under given constraints

### DQN Policy Model

- Accepts live system indicators
- Suggests a variant to execute based on expected latency behavior
- Focuses on reducing tail latency and maintaining plan quality under changing load

This module is an early-stage research component intended for experimentation rather than production deployment.

---

## 8. Observability

The system provides observability across all components through:

### Prometheus

- Each service exposes metrics on an HTTP endpoint
- Collects periodic system and query performance metrics

### Grafana

- Dashboards visualize latency, resource utilization, and workload trends

### CloudWatch (Optional)

- Used when deploying on EKS or EC2
- Supports autoscaling experiments and deeper system insights

---

## 9. Dataset Workflow Example

A common workflow looks like:

1. Use Spark to generate a dataset or load an existing one
2. Write CSV or Parquet into the shared workspace
3. Use AIO to ingest data into SciDB
4. Convert long CSV into an n-dimensional array through redimension
5. Generate canonical AST and variants
6. Execute variants using the benchmark runner
7. Collect metrics and store them in the feature store
8. Analyze with ML or visualization dashboards

This end-to-end flow is reproducible and designed for iterative experimentation.

---

## 10. Status and Roadmap

### Completed

- Containerized environment
- Distributed I/O integration
- Spark workload simulation
- Canonicalizer and variant engine
- Benchmark runner with full metrics
- ML prototype
- Observability stack

### In Progress

- Integrating ML inference directly into runtime scheduling
- Expanding workload generation tools
- Optional Kubernetes deployment scripts

---

## 11. How to Use This Repository

1. Build or pull the SciDB and Spark containers
2. Start both containers with a shared I/O mount
3. Generate data or place datasets in the shared directory
4. Use ingestion scripts to import into SciDB
5. Run canonicalizer to prepare variants
6. Use the benchmark runner to execute and capture metrics
7. Explore metrics in the dashboards or feed them into ML modules

Scripts and examples are provided within the respective folders.
