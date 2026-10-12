# Wake 5 read-only metric diagnostic review

Reviewed at: 2026-10-11T22:30:12Z  
Request: `wake5-metric-diagnostic-review`  
Delegation: `pa-bpe-wake5-metric-review`  
Status: **completed, with all five bound inputs hash-matched before review**  
Scope: mathematical and protocol review only; no experiment, runner action, method selection, or confirmation claim.

## Exact binding

The parent binding in the assignment is checkpoint generation 5, active idea `pa-bpe-domain-robustness` revision 1, goal-contract version 1, manifest SHA-256 `e3d107a2a72834e5ff5ab10539dea3198a97ce89f4605d6fb4fcbc30f3bfa61b`, under Research Autopilot Simple `0.3.0-simple.9`.

All assigned inputs matched exactly:

| Bound input | Assigned and observed SHA-256 |
|---|---|
| `execution_windows/wake3/output/multibook_raw_evaluation.json` | `c93f81a12c2c85726d72ba3c61109b475a9ac50fdd8ef5c5f07aaaca3b009e77` |
| `execution_windows/wake3/output/pair_candidate_evaluation.json` | `da6d11dbd9a50111664f58c28ad20c9ea3b67e309b751ca3a895afb883b2ff20` |
| `execution_windows/wake3b/output/full_candidate_evaluation.json` | `75c9b9983a0d53d693f02fded94da2e78acbfaa5ed522eec179e84f6e6ba4512` |
| `execution_windows/wake4/output/efficiency_candidate_evaluation.json` | `d88df96a5d11405477098d10b11a6bea98e8c06a5bdf1c51379d2ff2a572f002` |
| `PA_BPE_Wake4_Report.md` | `f2c0c5c30924d261345f90744f0948e6064f3a99ef31e17cad55aef416bc6736` |

The JSON files contain aligned integer `paired_costs` and report both aggregate `gini` and `mean_sentence_gini`. The latter should nevertheless be independently reconstructed from `paired_costs` in the diagnostic; its name alone is not a sufficient definition, and Wake 4's arithmetic verification was not specifically a cancellation-decomposition audit.

## Mathematical relationship

For aligned row (i), let English and French token costs be (a_i,b_i\ge 0), and define

\[
s_i=a_i+b_i,\qquad d_i=a_i-b_i,\qquad S=\sum_i s_i.
\]

For (S>0), the ordinary two-value Gini of aggregate language costs is

\[
G_{\mathrm{agg}}
=\frac{\left|\sum_i a_i-\sum_i b_i\right|}
       {2\left(\sum_i a_i+\sum_i b_i\right)}
=\frac{|\sum_i d_i|}{2S}.
\]

This is also the Gini of the two language means when both languages use the same number of aligned rows. It measures only the **net signed gap**. It does not measure the typical aligned-row gap.

Define row Gini for every nonempty-cost row (s_i>0):

\[
g_i=\frac{|d_i|}{2s_i}.
\]

Two distinct sentence-level summaries are needed:

\[
G_{\mathrm{macro}}=\frac{1}{|V|}\sum_{i\in V}g_i,
\qquad
G_{\mathrm{mass}}=\frac{\sum_i s_i g_i}{S}
=\frac{\sum_i|d_i|}{2S},
\]

where (V=\{i:s_i>0\}). `macro` answers how imbalanced a typical aligned row is; `mass` weights long/high-token rows more heavily and gives the exact algebraic decomposition below. Neither can replace the other.

By the triangle inequality,

\[
0\le G_{\mathrm{agg}}\le G_{\mathrm{mass}}.
\]

Let

\[
P=\sum_i\max(d_i,0),\qquad N=\sum_i\max(-d_i,0).
\]

Then the exact cancellation load and cancellation fraction are

\[
C=G_{\mathrm{mass}}-G_{\mathrm{agg}}
=\frac{\min(P,N)}{S},
\]

\[
\kappa=
\begin{cases}
1-G_{\mathrm{agg}}/G_{\mathrm{mass}}
=2\min(P,N)/(P+N), & P+N>0,\\
0, & P+N=0.
\end{cases}
\]

Thus (G_{\mathrm{agg}}=0) proves only that total positive and negative signed gaps balance. It does **not** imply sentence parity. For example, two rows with costs `(10,0)` and `(0,10)` have (G_{\mathrm{agg}}=0), (G_{\mathrm{macro}}=G_{\mathrm{mass}}=0.5), and \(\kappa=1\). Conversely, rows `(10,5),(10,5)` have no cancellation: all three Ginis equal (1/6) and \(\kappa=0\).

The identity also exposes why a lower aggregate Gini can be misleading. For arm (A) relative to fixed reference (B),

\[
\Delta G_{\mathrm{agg}}
=\Delta G_{\mathrm{mass}}-\Delta C.
\]

If \(\Delta G_{\mathrm{agg}}<0\) but \(\Delta G_{\mathrm{mass}}\ge0\), the entire apparent aggregate improvement is caused by increased signed-gap cancellation: necessarily \(\Delta C>\Delta G_{\mathrm{mass}}\). This is an algebraic mechanism signature, not merely a rank correlation.

## Required deterministic diagnostic

The diagnostic should reconstruct all quantities from integer `paired_costs` using exact integer sums and rational comparisons before converting to decimal output. It should not tune a threshold or select a winning arm on these exposed data.

For every already-existing arm and every frozen work/split, report:

1. (n,S,P,N,G_{\mathrm{agg}},G_{\mathrm{mass}},G_{\mathrm{macro}},C,\kappa);
2. median, 90th percentile and maximum of (g_i), with one fixed documented quantile convention;
3. counts and token-gap masses for (d_i>0,d_i=0,d_i<0);
4. total cost (S/n) and worst-language mean cost, because parity can improve by making the previously cheaper language more expensive;
5. exact equality checks against stored aggregate `gini` and stored `mean_sentence_gini` after the latter's intended convention is declared.

Keep three aggregation levels separate:

- per aligned row;
- per work/domain;
- across works.

For Books, report both the macro mean of the ten work metrics and a pooled-row metric. The report's `mean_book_gini` is a macro average of work Ginis; it is not generally the Gini of pooled work totals. The cancellation identity holds within each work and, by linearity, for the macro means if (\bar C\) is averaged in the same way. Do not mix TICO and Books into one score.

### Predeclared retrospective interpretation rules

Apply the following to every fixed arm/reference contrast in a mechanically enumerated table (at minimum, all arms versus Classical; mechanism controls may be shown separately). Do not choose contrasts after seeing the diagnostics.

1. **Cancellation-consistent mismatch on a unit:** \(\Delta G_{\mathrm{agg}}<0\), \(\Delta G_{\mathrm{mass}}\ge0\), and therefore \(\Delta C>\Delta G_{\mathrm{mass}}\). This says aggregate parity improved while absolute aligned-row imbalance did not.
2. **Macro-row mismatch:** \(\Delta G_{\mathrm{agg}}<0\) and \(\Delta G_{\mathrm{macro}}\ge0\). This is complementary rather than algebraically identical, because short and long rows receive equal weight.
3. **Aligned improvement:** both \(\Delta G_{\mathrm{agg}}<0\) and \(\Delta G_{\mathrm{mass}}<0\). Still disclose \(\Delta C\), total cost and worst-language cost; do not infer that lower parity cost is Pareto-improving.
4. **Descriptive ranking instability:** the aggregate contrast changes sign across works or when an author block is omitted, without a stable cancellation-mismatch signature. Call this domain/sample sensitivity, not stochastic optimizer noise: these tokenizers and evaluations are deterministic.
5. **Stable within-exposed-set structural signature:** the pooled or work-macro cancellation-mismatch condition holds and retains both sign conditions under every leave-one-author-block-out recomputation. Books should be blocked by author, not only by work, because Doyle and Verne contribute multiple works. This remains descriptive evidence on exposed data, not confirmation.

The leave-one-author-block-out rule is preferable to sentence bootstrap or a nominal ten-work sign test here. Sentences are nested within works, several works share authors, and ten work outcomes are not ten independent replications. If a later inferential interval is desired, its sampling unit and population must be declared prospectively on a genuinely unexposed set.

## Edge cases and implementation cautions

- If (S=0), all Ginis are undefined and the unit should be reported `NA`, not zero. Rows with (s_i=0) contribute no token mass and must be excluded from `macro` with their count disclosed. If one language cost is zero and the other positive, (g_i=0.5).
- When (P+N=0), set \(\kappa=0\) by explicit convention and report (G_{\mathrm{mass}}=G_{\mathrm{agg}}=0\); otherwise the fraction is undefined.
- Two-language Gini lies in ([0,0.5]). These identities should not be stated as a general multilingual result. A third-language extension needs a separately frozen multiway or pairwise decomposition.
- `mean_sentence_gini` is likely a macro-row statistic, whereas the exact cancellation identity requires the token-mass-weighted statistic. Reporting only the existing mean is insufficient.
- Exact rational sign comparisons avoid arbitrary epsilons. Decimal rounding is presentation only. If practical-effect thresholds are later wanted, they must be frozen before unexposed confirmation rather than invented retrospectively.
- Translation pairs can differ legitimately in orthographic, morphological and semantic length. Token-count parity is a tokenizer burden diagnostic, not a complete language-fairness construct. Character/byte-normalized costs would answer another question and must not be silently substituted.
- Lower Gini alone can be achieved by raising the efficient language's cost. Total cost, per-language costs and worst-language cost must remain co-primary descriptive quantities.
- The prior 36-table verification supports integer cost/aggregate consistency, but does not by itself establish the new cancellation interpretation or independence of observations.

## Interpretation of the currently bound evidence

The bound artifacts are sufficient to execute the proposed diagnostic because they retain aligned integer costs for the exposed bilingual rows. They are not sufficient to call a mechanism confirmed. Wake 4 already established that near-zero development aggregate Gini did not yield better exposed Books Gini or cost, and that the compression-oriented control was strongest among its three new arms. The cancellation audit can determine whether aggregate parity and aligned-row parity disagree **within these realized samples**; it cannot establish that cancellation caused out-of-domain failure, that the same behavior generalizes to other languages, or that a sentence-level objective will improve confirmation performance.

In particular, no new candidate should be selected from Books based on this retrospective audit. A sentence-level or cost-budgeted rule is justified for prospective testing only if the exact decomposition shows a stable, interpretable mismatch, after which its rule and thresholds must be frozen before use on genuinely unexposed works/authors/domains.

## Review outcome and next action

**Outcome:** The aggregate two-language Gini can conceal arbitrarily large aligned-row imbalance through signed-gap cancellation. The exact distinguishing diagnostic is the pair \((G_{\mathrm{mass}},C)\), supplemented by (G_{\mathrm{macro}}), rather than another aggregate rank table. The identity \(G_{\mathrm{agg}}=G_{\mathrm{mass}}-C\) gives a deterministic test of objective mismatch; author-block stability distinguishes a stable in-sample mechanism signature from fragile work ranking.

**Next action:** Independently reconstruct the declared metrics from every frozen `paired_costs` table, emit exact-consistency checks and the predeclared all-arm contrast table, and retain the result as retrospective exposed-data diagnosis only. Do not train or select a new method until that audit is complete and a genuinely unexposed confirmation protocol is frozen.

Changed file: `review/wake5_metric_diagnostic_review.md` only.
