---
title: Consistent Hashing
tags:
  - hashing
  - distributed-systems
  - partitioning
date: 2026-08-24
status: completed
---

# Consistent Hashing in Distributed Systems

Consistent Hashing is a distributed hashing scheme that minimizes key remapping when the hash table or node cluster size changes.

## The Modulo Problem ($K \pmod N$)
In traditional modulo hashing:
$$\text{node} = \text{hash}(key) \pmod N$$
When $N$ changes (due to node addition or failure), almost all keys ($N / (N+1)$) are remapped to new servers, causing massive cache invalidation and severe cache stampedes.

## The Consistent Hash Ring
Consistent hashing places both nodes and cache keys on an abstract circular ring with space range $[0, 2^{32}-1]$:
1. Each node is hashed by its ID or IP onto the ring.
2. A key is assigned to the nearest server clockwise along the ring.
3. When a node is added or removed, only $K/N$ keys on average need to be migrated.

## Virtual Nodes (Vnodes)
To avoid hotspotting and non-uniform key distribution, each physical node is mapped to multiple pseudo-random positions (virtual nodes, typically 100–250 per physical server). This evenly balances load across heterogeneous hardware.

Used extensively in distributed caching layers and vector retrieval architectures (see [[Vector Databases]] and [[Semantic Caching]]).
