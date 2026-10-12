# Wake 6 read-only conditional-shift decomposition review

Reviewed at: 2026-10-11T23:31:23Z  
Request: `wake6-conditional-shift-review`  
Delegation: `pa-bpe-wake6-conditional-shift-review`  
Status: **completed; all six bound inputs hash-matched before review**  
Scope: mathematical/protocol review only. No experiment, runner/journal/checkpoint/plan/result change, method selection, or further delegation was performed.

## Binding and input integrity

The assignment binds this review to checkpoint generation 6, active idea `pa-bpe-domain-robustness` revision 1, manifest SHA-256 `ca709d80394c9e7baceb49983151ca4c489ceaba4397459c895ad0f1e895695d`, runner digest `e2b9d1c04fdb680bdf6e069ec387d84ec8f92efed5c44f59b7724ab446db5ae8`, and Research Autopilot Simple `0.3.0-simple.9`.

| Bound input | Assigned and observed SHA-256 |
|---|---|
| `execution_windows/wake5/output/mass_cancellation_audit.json` | `c44873be9ffd96796780c81322bbb7405c738a79436832d0bd10c80db16b221a` |
| `execution_windows/wake3/output/multibook_raw_evaluation.json` | `c93f81a12c2c85726d72ba3c61109b475a9ac50fdd8ef5c5f07aaaca3b009e77` |
| `execution_windows/wake3/output/pair_candidate_evaluation.json` | `da6d11dbd9a50111664f58c28ad20c9ea3b67e309b751ca3a895afb883b2ff20` |
| `execution_windows/wake3b/output/full_candidate_evaluation.json` | `75c9b9983a0d53d693f02fded94da2e78acbfaa5ed522eec179e84f6e6ba4512` |
| `execution_windows/wake4/output/efficiency_candidate_evaluation.json` | `d88df96a5d11405477098d10b11a6bea98e8c06a5bdf1c51379d2ff2a572f002` |
| `PA_BPE_Wake5_Report.md` | `004f6d39dec38799c472e66cc375efeec0adb693e2b244831bd19bf4b1388e82` |

The bound files expose aligned integer costs for the existing arms. Before any decomposition, the implementation must nevertheless verify the common sampling hash, work/split names, list lengths, and row order against the frozen sampling records. Equal list lengths alone do not prove row alignment.

## Exact estimands and sign conventions

Let domain \(D\in\{T,B\}\) denote TICO dev100 or pooled Books rows, and let \(a\) be one of the 15 non-Classical arms. For row \(i\), write Classical English/French costs as \((e_{0i},f_{0i})\), arm costs as \((e_{ai},f_{ai})\), and

\[
d_{0i}=e_{0i}-f_{0i},\quad d_{ai}=e_{ai}-f_{ai},\quad
s_{0i}=e_{0i}+f_{0i},\quad s_{ai}=e_{ai}+f_{ai}.
\]

For positive token mass, define row Gini

\[
g_{mi}=\frac{|e_{mi}-f_{mi}|}{2(e_{mi}+f_{mi})},\qquad m\in\{0,a\}.
\]

The three proposed row outcomes should be frozen as

\[
Y^{(g)}_{ai}=g_{0i}-g_{ai},\qquad
Y^{(|d|)}_{ai}=|d_{0i}|-|d_{ai}|,\qquad
Y^{(s)}_{ai}=s_{ai}-s_{0i}.
\]

Thus positive \(Y^{(g)}\) and \(Y^{(|d|)}\) mean less aligned-row imbalance, whereas positive \(Y^{(s)}\) means a token-cost increase. These outcomes must not be collapsed into a single success score without a prospectively frozen utility. In particular, \(Y^{(g)}\) is a macro-row contrast; it does **not** decompose the nonlinear aggregate-language Gini.

The grouping variable must be computed once from Classical and reused for every arm:

- sign partition: \(K_i\in\{d_{0i}<0,d_{0i}=0,d_{0i}>0\}\);
- length partition: use Classical \(s_{0i}\), never arm-specific length.

The bound audit shows that the Classical TICO sign groups contain 85 negative, 4 zero, and 11 positive rows. The four-row zero cell is therefore intrinsically fragile; a displayed conditional mean is not a stable population estimate merely because it exists.

## Exact TICO-reference decomposition

For one fixed arm, one fixed outcome \(Y\), and one fixed partition, let

\[
p_{Dk}=\frac{n_{Dk}}{n_D},\qquad
\mu_{Dk}=\frac{1}{n_{Dk}}\sum_{i:D_i=D,K_i=k}Y_i,qquad
\mu_D=\sum_k p_{Dk}\mu_{Dk}.
\]

When every Books-positive group also has TICO support, the proposed TICO-reference Oaxaca/standardization identity is

\[
\Delta=\mu_B-\mu_T=C_T+R_T,
\]

\[
C_T=\sum_k(p_{Bk}-p_{Tk})\mu_{Tk},\qquad
R_T=\sum_k p_{Bk}(\mu_{Bk}-\mu_{Tk}).
\]

Equivalently, \(\widetilde\mu_{B\leftarrow T}=\sum_kp_{Bk}\mu_{Tk}\), so

\[
C_T=\widetilde\mu_{B\leftarrow T}-\mu_T,qquad
R_T=\mu_B-\widetilde\mu_{B\leftarrow T}.
\]

This is an exact sample identity. `composition contribution` and `within-group residual` are defensible names. `composition mechanism` and `changed method response` are not: the split is reference-dependent and does not identify causes.

The non-uniqueness must be disclosed. A Books-reference decomposition uses Books conditional means and generally assigns different magnitudes to the two terms. Even with common support, the symmetric Kitagawa form,

\[
C_{sym}=\frac12\sum_k(p_{Bk}-p_{Tk})(\mu_{Bk}+\mu_{Tk}),\qquad
R_{sym}=\frac12\sum_k(p_{Bk}+p_{Tk})(\mu_{Bk}-\mu_{Tk}),
\]

is also exact and generally differs from \((C_T,R_T)\). Therefore a claim such as “x% of failure is caused by composition” is not invariant and is not justified. At most, report the frozen TICO-reference values, and optionally the symmetric values as a reference-sensitivity check.

## Empty groups, duplicate cutpoints, and zero mass

### Support violations

Do not impute an absent TICO conditional mean. Let \(A=\{k:p_{Tk}>0\}\) and \(N=\{k:p_{Tk}=0,p_{Bk}>0\}\). The exact support-aware identity is

\[
\Delta=
\underbrace{\sum_{k\in A}(p_{Bk}-p_{Tk})\mu_{Tk}}_{C_T}
+\underbrace{\sum_{k\in A:p_{Bk}>0}p_{Bk}(\mu_{Bk}-\mu_{Tk})}_{R_T}
+\underbrace{\sum_{k\in N}p_{Bk}\mu_{Bk}}_{U},
\]

where \(U\) is an unmatched-support remainder. For \(p_{Bk}=0,p_{Tk}>0\), no Books conditional mean is needed; its residual contribution is zero and its composition contribution is \(-p_{Tk}\mu_{Tk}\). If both masses are zero, omit the cell. When \(U\ne0\), the proposed two-way “composition versus conditional” attribution is unavailable for the full shift; report all three terms instead. A deterministic, outcome-blind adjacent-bin merge is an alternative for length bins, but it must be frozen before looking at arm outcomes. Semantically distinct sign cells should not be merged merely to manufacture common support.

### Length-bin definition

Sort the 100 Classical TICO values \(s_{0i}\) and define nearest-rank cutpoints

\[
q_p=s_{0,(\lceil pn_T\rceil)},\qquad p\in\{0.25,0.50,0.75\}.
\]

Use explicit non-overlapping intervals

\[
(-\infty,q_{.25}],\ (q_{.25},q_{.50}],\ (q_{.50},q_{.75}],\ (q_{.75},\infty).
\]

The same numeric cutpoints must be applied to Books. Report the three cutpoint integers and both domains' cell counts. Integer ties can make adjacent cutpoints equal and nominal bins empty; nearest-rank quantiles do not guarantee four groups of 25. Collapse duplicate interior cutpoints by a predetermined rule or retain an explicit empty/support-remainder cell. Never change cutpoints by arm, Books work, or leave-one-author replicate.

### Zero-token rows

If \(s_{0i}=0\) or \(s_{ai}=0\), \(Y^{(g)}_{ai}\) is undefined; do not silently map \(0/0\) to zero. Report the exact count and mark the arm/domain Gini decomposition unavailable unless a common-row exclusion rule was prospectively fixed. Arm-dependent row dropping changes group masses and destroys clean cross-arm comparability. The absolute-gap and cost outcomes remain arithmetically defined, but must be reported separately. The current artifacts report nonempty evaluated rows; this should still be enforced as an input assertion rather than assumed.

## Leave-one-author-block-out protocol

Recompute Books \(p_{Bk}\), \(\mu_{Bk}\), \(\mu_B\), and all components after omitting each complete author block; keep TICO quantities and frozen length cutpoints unchanged. The ten works map to only six author blocks (Brontë, Defoe, Doyle, Dumas, Verne, Voltaire), with unequal numbers of works. Consequently:

- author-block omission is a sensitivity analysis, not six independent replications;
- do not attach a binomial p-value, confidence interval, or “generalizes to authors” statement;
- report the full-data value, six leave-one-author values/range, sign count, and any support violation;
- “sign-stable under omission” means only that no single observed author block reverses the displayed sample sign.

The sign and length partitions are two overlapping views of the same rows. Their composition terms must **not** be added or treated as unique explained shares. A joint sign-by-length table would create sparse cells with only 100 TICO rows and is not warranted here unless separately frozen and support-audited.

## Post-execution partition-dependence audit

After the initial protocol review, the coordinator requested a focused audit of the completed diagnostic. The newly observed files were read-only and were not part of the original six-file assignment binding:

| Read-only diagnostic output | Observed SHA-256 |
|---|---|
| `execution_windows/wake6/output/conditional_shift_decomposition.json` | `53b28afedd0226a78f95240b6b1339463f52bc26cf88555d78a7a36d230c0265` |
| `execution_windows/wake6/output/conditional_shift_verification.json` | `22ed260b1854d627b720bd803e5a7fdd7d6de69a7476163b86b5df437d6f2da5` |

The verification artifact reports 2,342 checks, all passed; this validates coverage and arithmetic identities, not statistical or causal interpretation.

For `full_minmax`, the same macro-row Gini-gain domain shift is \(-0.0127082931\) under both partitions, as it must be. The TICO-reference components change materially:

| Partition | Composition contribution | Within-group residual | Algebraic pattern |
|---|---:|---:|---|
| Classical baseline gap sign | -0.0177139727 | +0.0050056796 | composition term is larger in absolute value; residual offsets it |
| Classical baseline length | -0.0004749096 | -0.0122333836 | residual term is larger in absolute value; both terms have the total's sign |

This is direct evidence that `component_with_larger_absolute_magnitude` is **not** a mechanism label. The total shift is invariant, but the allocation changes with the chosen conditioning sigma-field. Gap sign absorbs the large change in sign-group proportions together with sign-specific TICO means; length bins allocate almost the same shift to within-bin differences. Neither partition is privileged by the algebra, and neither blocks the other covariate or unmeasured domain features. Therefore the result cannot be described as “primarily composition-driven,” “primarily conditional-response-driven,” or as identifying the main failure mechanism. The only defensible statement is that the observed allocation is partition-dependent.

A 3-by-4 sign-by-length refinement is not a valid rescue in the current sample. Classical TICO has only four zero-gap rows total, so its four joint length cells must collectively contain only four observations and some may be empty. Such a table would make conditional means unstable or unsupported, and a result selected after seeing the separate-partition disagreement would be retrospective. Even with adequate support, joint stratification would only move omitted heterogeneity into a finer descriptive residual; it would not identify causality. The current decision should therefore be **non-identifiability**, not immediate joint stratification. A joint partition may be prospectively frozen for a substantially larger, genuinely unexposed dataset with explicit minimum cell counts and unmatched-support handling.

## Claims that the protocol cannot support

The proposed arithmetic cannot justify any of the following classifications:

1. **Causal composition shift versus causal response shift.** The residual includes unmeasured lexical, orthographic, semantic, genre, author, alignment, and length differences, sampling noise, coarse-bin residual heterogeneity, and tokenizer-by-domain interaction.
2. **Covariate shift in the statistical sense.** Sign and baseline token cost are only two tokenizer-derived summaries; equality of conditional outcome distributions given these summaries is neither tested nor plausible from this table alone.
3. **Percentage of failure explained.** Component magnitude and even apparent dominance depend on the reference domain, partition, scale, and outcome; ratios are unstable when total shift is near zero or terms oppose.
4. **Fairness improvement from raw absolute-gap reduction alone.** \(|d|\) is length-sensitive. Books rows are often longer than TICO rows, so cross-domain raw-gap and raw-cost shifts partly reflect exposure length. Macro-row Gini is the normalized companion; a prospectively defined relative-cost sensitivity may be shown but must not replace the frozen raw outcome.
5. **Independent confirmation or general multilingual evidence.** TICO and Books are exposed English–French diagnostics; arms are deterministic, correlated, and previously inspected.
6. **Method selection.** Mechanical enumeration of all 15 contrasts is appropriate, and highlighting `full_minmax`, `eff_minmax`, and `exact_train` is acceptable only as prior specification. The decomposition supplies no new selection criterion.

The decomposition also cannot establish that the observed conditional residual caused the previously observed Books cost/fairness failure. Baseline sign and length are properties of a trained Classical tokenizer, not randomized treatments.

## Recommended reporting and decision

For each of the 15 arm contrasts and each of the three outcomes, report separately for sign and length partitions:

1. frozen group definition, counts and proportions in both domains;
2. conditional means with raw numerators/counts;
3. \(\mu_T\), \(\mu_B\), total shift \(\Delta\), \(C_T\), \(R_T\), and, if needed, unmatched-support remainder \(U\);
4. an exact reconstruction check \(\Delta=C_T+R_T+U\), with rational/integer arithmetic where possible and decimal tolerance used only for serialization;
5. full-data and six leave-one-author-block-out component values;
6. explicit direction labels (`fairness gain`, `gap reduction`, `cost increase`) rather than a common “better” sign.

No categorical “composition-driven” or “conditional-driven” decision rule is justified on this exposed diagnostic. Magnitude dominance and percentage thresholds would be retrospective and reference-dependent; mere sign agreement is too weak. The strongest permissible language is descriptive:

> Under the frozen TICO-reference partition, reweighting TICO conditional sample means to the observed Books group proportions contributes \(C_T\) to the observed mean-outcome shift, while \(R_T\) remains as a within-group sample residual; the result is/is not sign-stable to omitting one observed author block.

If an unmatched-support term is nonzero, append that the two-way attribution is incomplete. If reference choice reverses an apparent dominance, say the attribution is reference-sensitive and stop there.

## Minimum defensible interpretation

This analysis can determine whether the **observed** TICO-to-Books difference for a fixed existing tokenizer contrast is arithmetically associated with changed proportions of Classical baseline sign/length groups, changed within-group mean contrasts, or unsupported Books cells. It can also show whether those sample signs survive omission of any one observed Books author block. It cannot distinguish causal mechanisms, estimate generalization, certify covariate shift, or motivate a new tokenizer from these exposed bilingual data.

Review outcome: **proceed only as a support-aware, reference-labelled descriptive decomposition; retain no categorical mechanism or method-selection rule.**

Changed file: `review/wake6_conditional_shift_review.md` only.
