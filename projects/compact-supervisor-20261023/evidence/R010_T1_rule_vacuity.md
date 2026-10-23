# R010 T1 zero-support and rare-exception rule admission
Read-only pinned source Yunbo-max/TabKG@e44fdf17f98b50ee1348392982e083a1db8f6ad7:
reasoning/graph_validator.py blob
ee4f3c65054e14dfc6351adc436f1e8e9f10c0e1:
  validate_semantic: len(condition_subset)==0 returns 1.0;
  validate_graph: threshold default .90, accepts score >= threshold.
main.py CLI also defaults validation_threshold to .90.
graph_compressor.py may label targets as dependent in an
accepted edge plan. Full latent generation and downstream
conditional-rule reconstruction were NOT audited in this turn.

Case A: rule is wrong whenever rare antecedent A occurs, with
P(A)=.001 independently per row, n=200. Source validator scores
rule 1.0 if there are no antecedent rows. Probability of this
event = .999^200 = .8186488294786356.
Logical vacuous truth is not statistical positive evidence.

Case B: 2% of data are domain-valid deviations from a proposed
rule; n=50, validation threshold .9. The rule is kept when
K~Binomial(50,.02) <=5; acceptance probability
.9995217827857852. Conditional on actually applying a
deterministic repair that erases those legitimate deviations,
the synthetic indicator distribution loses mass .02 and
total-variation distance is at least .02.

Classical support-aware remedy, NOT an original statistical
theorem: abstain when conditional count=0, keep both numerator
and denominator, use a one-sided Clopper-Pearson lower bound
to approve only if L>=tau. For 100% observed successes and
one-sided 95% coverage, L=.05^(1/n); at n=28 it is .898534,
at n=29 it is .901855. Real valid exception labels must be
distinguished from erroneous/noisy records.
Falsifier: complete production pipeline never applies this
semantic validator to an irreversible reconstruction, or
independent domain audit finds the alleged exceptions invalid.
Closest rule-discovery agents arXiv 2608.15109 and 2026
semantic-firewall overmining make novelty UNVERIFIED.
