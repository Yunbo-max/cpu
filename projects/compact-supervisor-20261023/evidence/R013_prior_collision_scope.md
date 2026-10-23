# R013 primary and closest-equivalence audit, not original algorithm acceptance
Project parent 79b064db2ecfe014a945e7284e16f41678739d3c. On 2026-10-23 sources inspected:
G1:
- Primary P-54B official NYISO outage archive https://mis.nyiso.com/public/P-54Blist.htm, CSV files exist but raw bytes could not be read in Chat web (unsupported CSV content); matching PTID/reactance/capacity graph not verified. No claims of genuine empirical failure frequencies this round.
- PyPSA official documentation https://docs.pypsa.org/latest/user-guide/optimization/power-flow/ explicitly enforces Kirchhoff current and voltage laws and linearized PTDF; canonical transport and DC power flow comparison also in https://doi.org/10.1016/j.apenergy.2022.118859 . Plain graph maxflow is a relaxed/categorical different objective.
- Baswana/Bhanja ICALP 2024 directed weighted mincut value oracle https://doi.org/10.4230/LIPIcs.ICALP.2024.17 is strong exact comparator only for simple edge-failure maxflow/cut task.
T1:
- Pinned user repository Yunbo-max/TabKG@e44fdf17f98b50ee1348392982e083a1db8f6ad7 (also latest main when inspected), reasoning/graph_validator.py, reasoning/graph_compressor.py, main.py . The stage-4 CRKG drop and graph descriptor are proven from pinned implementation; same candidate graph fixed on two inputs, no actual TabKG full LLM execution.
- Existing column dependency compression in Theoretical Computer Science 2007 https://doi.org/10.1016/j.tcs.2007.07.016 explicitly exploits dependency; missing FD function lookup is a standard metadata cost, not new theory.
- FD vs logical dependency Pattern Recognition 2025 https://doi.org/10.1016/j.patcog.2025.111459 and probabilistic approximate FD discovery UAI 2025 https://proceedings.mlr.press/v286/duan25a.html. T1 academic-method novelty park is source-backed, not formal independent scientific acceptance.
No formal Work reviewer/GPU/native agent/paid API. Science root persists even if there are zero currently executable leaves; next human wake must screen new source-grounded scientific mechanisms and cannot manufacture 3 active leaves.
