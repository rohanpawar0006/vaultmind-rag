---
title: CAP Theorem
tags:
  - cap-theorem
  - distributed-systems
  - consistency
date: 2026-08-23
status: completed
---

# The CAP Theorem (Brewer's Theorem)

Formulated by Eric Brewer and formally proven by Seth Gilbert and Nancy Lynch in 2002, the CAP theorem states that a distributed data store can simultaneously provide at most two of the following three guarantees:

1. **Consistency ($C$)**: Every read receives the most recent write or an error (Linearizability).
2. **Availability ($A$)**: Every non-failing node returns a non-error response for every request, without guarantee that it contains the latest write.
3. **Partition Tolerance ($P$)**: The system continues to operate despite an arbitrary number of messages being dropped or delayed by the network between nodes.

## The Reality of Partition Tolerance
In real-world networks, network partitions are inevitable physical realities. Therefore, real distributed systems can never choose $CA$. Instead, systems must choose between:
- **CP Systems** (e.g., [[Raft Protocol]], [[Paxos Algorithm]], ZooKeeper, etcd): Prioritize absolute consistency by rejecting writes during network partitions.
- **AP Systems** (e.g., DynamoDB, Apache Cassandra, CouchDB): Prioritize uptime and availability by accepting writes on both sides of a partition, resolving conflicts later using vector clocks or CRDTs.
