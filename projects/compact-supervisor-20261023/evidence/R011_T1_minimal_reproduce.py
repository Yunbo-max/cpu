#!/usr/bin/env python3
"""Minimal CPU reproduction of inspected pinned TabKG stages (not full pipeline).
TabKG@e44fdf17f98b50ee1348392982e083a1db8f6ad7.
Models the relevant semantic validator, DAG edge, and main.py Stage-4 column drop.
"""
import json
import math
import pandas as pd

df = pd.DataFrame({"region": ["a", "a", "b", "b"], "price": [1, 3, 2, 4]})
rule = "IF region == 'a' THEN price > 0"
subset = df[df.eval("region == 'a'")]
score = float(subset.eval("price > 0").mean()) if len(subset) else 1.0
edge = {"source": "region", "target": "price", "type": "semantic",
        "rule": rule, "validation_score": round(score, 4)}
accepted = [edge] if score >= 0.90 else []
nodes = list(df.columns)
indegree = {node: 0 for node in nodes}
for e in accepted:
    indegree[e["target"]] += 1
kept = sorted(n for n in nodes if indegree[n] == 0)
dropped = sorted(n for n in nodes if indegree[n] > 0)
compressed = df.drop(columns=dropped)
entropy = sum(len(g) / len(df) * math.log2(g.price.nunique())
              for _, g in df.groupby("region"))
max_accuracy = sum(g.price.value_counts().max()
                   for _, g in df.groupby("region")) / len(df)
assert accepted and dropped == ["price"]
assert entropy == 1 and max_accuracy == .5
print(json.dumps({"validation_score": score, "kept": kept, "dropped": dropped,
                  "remaining_values": compressed.to_dict(orient="list"),
                  "H_price_given_region_bits": entropy,
                  "best_exact_reconstruction_accuracy": max_accuracy,
                  "full_llm_diffusion_decompressor_run": False}, indent=2))
