# R011 G1: An exact sparse-response baseline on pinned Sioux Falls
Parent: G1, coordination SHA 56c7198d5c6f7bb12a1883ce81df1112652897be. Dataset pins, method and original numeric receipt in evidence/R011_G1_SiouxFalls_receipt.json.

Sioux Falls standard traffic assignment network has 24 nodes, 76 directed arcs, capacity attributes and OD demands. OD demands select terminal pairs only and are NOT sampled edge failure frequencies. Select five highest OD-demand pairs, merging swapped endpoints so reciprocal pairs don't use up all five slots: (10,16), (10,11), (10,15), (10,17), (9,10). For each pair compute exact scaled-integer baseline maxflow and all 76 single-edge-deletion maxflows (385 maxflow calls).

| OD pair | Demand | k affected edges / 76 | Unaffected | Exact sparse payload bits | Full 76x64 table bits |
|---|---:|---:|---:|---:|---:|
| 10->16 | 4400 | 17 | 59 (77.63%) | 1278 | 4864 |
| 10->11 | 4000 | 4 | 72 (94.74%) | 355 | 4864 |
| 10->15 | 4000 | 12 | 64 (84.21%) | 923 | 4864 |
| 10->17 | 3900 | 3 | 73 (96.05%) | 284 | 4864 |
| 9->10 | 2800 | 6 | 70 (92.11%) | 497 | 4864 |

Exact sparse payload specification: 64-bit baseline maximum flow, 7-bit k, k tuples of (7-bit original-edge ID, 64-bit exact loss), hence B=71+71k. A full edge response array uses 76*64=4864 bits. This is a CONDITIONAL response-payload comparison assuming global edge ordering shared by BOTH; not a measured compressed graph size, actual query index, executable, or theorem-general data structure. Dynamic dictionary/run-length encodings and published O(n)-space directed weighted single-edge oracles may be even stronger. Under this fixed topology, many deletions have zero effect; this is negative baseline pressure on learning-style joint coding, not evidence for a new coder.

Source: bstabler/TransportationNetworks@d1639b4ef218c17928ba573e806ddf8ba5e7ae6d, SiouxFalls/SiouxFalls_net.tntp blob 66d0eca4ddcfb82f861bea040060deab7a741b2f, SiouxFalls_trips.tntp blob db70eda57738877811e9ac07c25a567973d3b6a0. License/data provenance must be checked for derived redistribution; only aggregate calculated results and independent code are committed, not original raw TNTP files.

Falsifier: a real held-out query distribution never justifies any added learning/sketch bits over this lossless sparse oracle, entropy coder and ICALP 2024 baseline when full storage/latency/accuracy are matched. No real failures, benchmarked published oracle implementation, gradient training, GPU or independent Work reviewer this round. Original JavaScript data probe was executed in connected tool, standalone equivalent reproducible source provided at evidence/R011_G1_sparse_reproduce.js but not itself executed against raw files.
