# R009 G3: named-edge identity mismatch repaired by one bit
The R008 graphs have two unlabeled internal branches with edge
capacities 1 and 2, so an isomorphism may swap p and q and preserve
the weighted graph. Both have intact maxflow 3.
For the named original-edge query delete(s,p), answers are 2 and 1.
Adding one bit that says which original internal branch is p
is enough for this two-branch toy; a decoder can disambiguate queries.
This is a missing edge-ID/correspondence interface, not proof of a
new graph condensation limitation when query IDs are given.
ICALP 2024 directed weighted vital-edge sensitivity already supports
named original failing edges with known capacity.
DECISION: park standalone G3 method novelty; future end-to-end graph
condensation evaluations should still account for any correspondence
metadata as part of total bits.
CPU witness: weighted-isomorphic pair and response equality,
checked without inference/training.
