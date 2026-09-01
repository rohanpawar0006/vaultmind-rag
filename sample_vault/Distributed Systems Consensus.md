---
title: Distributed Systems Consensus
tags:
  - distributed-systems
  - consensus
  - fault-tolerance
date: 2026-08-20
status: completed
---

# Distributed Consensus: Fundamentals

Consensus in distributed systems is the process of agreeing on a shared state or log of transactions among multiple nodes across an unreliable network where nodes may crash and messages may be delayed, lost, or reordered.

## The Consensus Problem
Given a set of $N$ nodes, a consensus algorithm guarantees:
- **Agreement**: All non-faulty nodes decide on the same value.
- **Validity**: If a node decides a value $v$, then $v$ must have been proposed by some node.
- **Termination (Liveness)**: All non-faulty nodes eventually decide upon a value.

## Leading Algorithms
- [[Paxos Algorithm]]: The classical theoretical foundation introduced by Leslie Lamport. Renowned for its conceptual difficulty.
- [[Raft Protocol]]: An understandable, state-machine-replication consensus protocol designed by Ongaro & Ousterhout.

## Relationship to CAP
Per the [[CAP Theorem]], under network partitions ($P$), a consensus system must choose between Consistency ($C$) and Availability ($A$). Both Raft and Paxos choose Consistency ($CP$).
