# R010 G1 graph benchmark availability and scope
FlowBanzhaf https://huggingface.co/datasets/FlowBanzhaf/FlowBanzhaf
has edge_index and edge_attr with normalized capacities plus agent
assignments, PyG graph samples, synthetic ER/BA/WS and nine SNAP
real-world graph topologies, and held-out structural shift splits.
Even SNAP subgraphs have randomly generated capacities and owner
labels. Banzhaf normalized marginal contribution is NOT the same
supervision as a named original-edge fault-response vector.
The benchmark does NOT contain observed failure event frequencies
or industrial outage loss distribution. Its dataset viewer does
not automatically preview its PyTorch .pt chunks. No dataset bytes
have been loaded into this Work session.
Alternative https://zenodo.org/records/18929874 contains
79 DIMACS maxflow instances from eight families, but no
verified real fault query workload.
Next: only a preregistered synthetic workload stress test until
independent observed outages and source licenses become available.
All baselines must count network description, edge-ID map,
codebook, query latency, and decoder computation.
Strong exact oracles ICALP 2024 and ITCS 2026 remain essential.
No actual graph test was executed in R010.
