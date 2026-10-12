# B15 source and design record

SciPy LOBPCG at commit `95e01a4004e2781c91a26d9836d82c103dd8513c`
(blob `500db09374082fd24944fbcf936ffc492c28004c`) accepts a mandatory
initial block, performs Rayleigh--Ritz updates, and stops using residual norms.
Using the previous endpoint as that block is therefore an existing warm-start
comparator, not a novel mechanism. SciPy also documents/implements a dense
fallback when the problem dimension is too small relative to block size; B15
freezes the explicit `t<5k` fallback so it is counted rather than hidden.

The comparator changes only the endpoint refresh routine in the already audited
B09 V2 cached-Gram policy. Exact Gram OPT queries, the gate, input, rank, eta and
thread limits remain identical. A runtime fallback after `t>=5k` is allowed only
from the solver's own nonfinite/residual signal and is counted; the exact audit
loss is not available to the runtime decision. Post-run comparison to exact loss
therefore cannot silently repair the treatment.

The frozen claim is deliberately stronger than an average speed statement:
every paired repeat must be faster, both eta trajectories must have identical
query/update masks, and every endpoint must meet the unchanged energy-scaled
`1e-10` objective tolerance. Failure retires this comparator as a paper-speed
route but does not invalidate LOBPCG as an established eigensolver.
