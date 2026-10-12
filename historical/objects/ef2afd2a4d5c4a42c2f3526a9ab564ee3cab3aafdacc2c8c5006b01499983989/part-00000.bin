# CPU-only paper selection and measured feasibility check

## Selected paper
**Boosting Frank-Wolfe by Chasing Gradients**, Cyrille W. Combettes and Sebastian Pokutta, ICML 2020, PMLR 119:2111–2121.

- Official proceedings: https://proceedings.mlr.press/v119/combettes20a.html
- Paper: https://proceedings.mlr.press/v119/combettes20a/combettes20a.pdf
- Author code: https://github.com/cyrillewcombettes/boostfw
- Inspected commit: `309f5fa2af04790f15d24c96bc42e7178cc63b55`
- Inspected notebook blob: `11781a7a74b52b71abcd113c886c2785066ecd9a`

## Primary-source evidence
Section 4, printed page 7: the authors report Python experiments on an Ubuntu 18.04 laptop, Intel Core i7 3.5 GHz, 8 GB RAM. This is evidence for an 8 GB machine, not evidence of a stated eight-core experiment.

Section 4.1 and author notebook lines 829–900 specify signal recovery with m=200, n=500, Gaussian noise sigma=0.05, a 2n-dimensional simplex formulation, exact quadratic line search, objective-improvement tolerance 1e-6, and BoostFW alignment tolerance 1e-3. The notebook uses a randomly generated dense ground-truth vector; this probe preserves that actual released generator rather than inventing a new sparse generator. Seeds are fixed here because upstream does not pin them in this cell.

The repository also contains Gisette, MovieLens100K and a preprocessed video co-localization file. These real-data cases were not downloaded or executed in this session. Section 4.4 reports that the AFW-L baseline encountered a memory error around 250 seconds on MovieLens, and was therefore allotted a shorter run. Do not infer unrestricted feasibility of every baseline from the laptop statement.

## Executed scope
9 bounded CPU runs: vanilla Frank-Wolfe, Away-Step Frank-Wolfe, and Boosted Frank-Wolfe, each on seeds 0, 1 and 2. This is a **resource/compatibility diagnostic**, not full-paper replication, a new method, a ranking of the algorithms, or a convergence certificate.

Implementation adaptations are explicit in `resource_probe.py` and `results/summary.json`: NumPy and the exact analytical gradient replace unavailable autograd; quadratic line search is directly specialized; finite-value/feasibility safeguards and true oracle counters are added; compute budget is 2 CPU seconds per method/seed rather than the upstream 50 seconds. This is not the original notebook executed unchanged. CPU timings include diagnostics. The same generated inputs are reused across methods within each seed; initialization otherwise follows the reviewed code, including BoostFW's extra initial oracle step.

3 AFW runs ended at the imposed compute budget, not at convergence. The other 6 runs reached the published objective-improvement stopping tolerance. Small objective change is not a small certified optimality gap: see the recorded final Frank-Wolfe gaps.

## Observed resources
- Host CPU quota: `400000 100000` (4 CPU-equivalents); affinity: 5 CPUs.
- Host memory limit: 4 GiB.
- BLAS thread setting: 1.
- Peak resident memory of this probe process across all runs: **153.39 MiB**. This is not peak whole-host usage and not an isolated per-method peak.
- Total measured wall time, including dataset setup and checks: **10.211 seconds**.

## Verification and artifacts
The execution includes finite-difference gradient checks, a Hessian directional check, feasible-domain and descent assertions. Saved iterates were reloaded and objectives/gaps recomputed; trace lengths and input hashes were verified. This is mathematical/software diagnosis, not independent scientific review.

- `results/summary.json`: all settings, changes, environment, metrics and measured resources.
- `results/run.log`: actual execution output.
- `results/*_trace.csv`: per-iteration raw trajectories.
- `results/*_final.npy`: final iterates.
- `results/readback_verification.json`: saved-output verification.
- `checkpoint.json`: source-bound completed selection and pending replication scope.

## Re-run
Requires Python and NumPy already installed; no GPU, paid model API or Docker.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python resource_probe.py --out results_new --seconds 2
```

## Access limitations retained
Direct container network access failed DNS resolution. The download tool could not retrieve the notebook or paper PDF. The GitHub connector successfully returned the pinned source sections. Web supplied the full parsed paper, but its PDF screenshot endpoint failed. No real-data download, unchanged-notebook run, full 50-second baseline suite or independent-review claim is made.

## Decision
The paper is selected as a CPU-only reproducibility starting point. The specific published signal-recovery setting is measured to fit well within the requested 8-core / 8-GB ceiling on a smaller host. Published hardware evidence supports broader study, but all other experiment and baseline memory costs remain unmeasured here. It is a 2020 paper, not a newly published 2025/2026 contribution. New research would need an updated closest-work audit before novelty could be claimed.
