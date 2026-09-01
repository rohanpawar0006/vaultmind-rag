---
title: Raft Protocol
tags:
  - raft
  - consensus
  - distributed-systems
date: 2026-08-21
status: completed
---

# The Raft Consensus Protocol

Raft is a consensus algorithm designed as an alternative to Multi-Paxos with a primary design goal of **understandability**. It decomposes the consensus problem into three independent subproblems:

## 1. Leader Election
- Nodes exist in one of three states: **Leader**, **Follower**, or **Candidate**.
- If a Follower receives no heartbeats within an election timeout (typically randomized between 150ms–300ms), it transitions to Candidate and broadcasts `RequestVote` RPCs.
- A node is elected Leader when it receives votes from a strict majority ($\lfloor N/2 \rfloor + 1$) of cluster nodes.

## 2. Log Replication
- The Leader accepts client commands, appends them to its local log, and issues `AppendEntries` RPCs to all followers.
- When an entry has been safely replicated to a majority of nodes, the Leader commits the entry and applies it to its state machine.

## 3. Safety Properties
- **Election Safety**: At most one leader can be elected in a given term.
- **Leader Append-Only**: A leader never overwrites or truncates its entries; it only appends new entries.
- **Log Matching Property**: If two logs contain an entry with the same index and term, they are identical up to that point.
- **Leader Completeness**: If a log entry is committed in a given term, that entry will be present in the logs of the leaders for all higher-numbered terms.

Compare with [[Paxos Algorithm]] and [[Distributed Systems Consensus]].
