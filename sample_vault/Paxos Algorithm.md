---
title: Paxos Algorithm
tags:
  - paxos
  - consensus
  - distributed-systems
date: 2026-08-22
status: completed
---

# The Paxos Consensus Algorithm

Introduced by Leslie Lamport in 1998 (*The Part-Time Parliament*), Paxos is a family of protocols for solving consensus in a network of unreliable processors.

## Single-Decree Paxos (Synod)
Single-decree Paxos agrees on a single value through two phases:

### Phase 1 (Prepare / Promise)
1. **Proposer** selects a unique proposal number $n$ ($n > \text{any previously seen proposal}$) and sends `Prepare(n)` to a majority of Acceptors.
2. **Acceptor** receives `Prepare(n)`. If $n > \text{highest promised number}$, it returns `Promise(n, max_accepted_val, max_accepted_n)` and promises never to accept proposals numbered less than $n$.

### Phase 2 (Accept / Acknowledged)
1. **Proposer** receives promises from a quorum. It sets the proposal value $v$ to the value of the highest-numbered proposal among the responses (or its own value if none were accepted). It broadcasts `Accept(n, v)` to acceptors.
2. **Acceptor** accepts `(n, v)` if $n \ge \text{highest promised number}$.

## Multi-Paxos
Single-decree Paxos requires 2 round-trips for every value. **Multi-Paxos** amortizes the Prepare phase by electing a stable leader, reducing subsequent log consensus to a single round-trip (Phase 2 only).

Contrast with [[Raft Protocol]] which enforces strong leader-centric invariants.
