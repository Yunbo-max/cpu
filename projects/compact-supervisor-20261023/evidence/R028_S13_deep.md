# R028 S13: conditional source class alias does not imply author's experiments duplicate

D1 UAI2026 paper https://proceedings.mlr.press/v337/yamao26a.html and official source isct-nakatalab/UAI2026_Robust_Decision-Focused_Learning_via_Worst-Case_Regret_Minimization@d3122144c97b39c7a5165023803fcee1bfc0fcc3. src/train_core.py blob 651b6fef689360c3e046aaa215834b644049a465 maps reg_ellip to robust_regret/ellip and ropt_budget to robust_opt/sparse. src/optmodel/robust_oracle.py blob 80099351f668c71dd75e5afd27abdc8e13aef967 defines RobustOptDataset(RobustRegretDataset) pass, latter precomputes worst cost from observed optimal actions.

D2 Under identical X,C, uc type/radius, seed, optimizer and losses, the two class paths generate identical static labels and gradients. This is a conditional source equivalence, not a universal statement about published configurations.

D3 Direct negative test: official README experiments do NOT fix the same uncertainty model. reg_ellip uses ellipsoid kappa7.5, ropt_budget sparse rho5. For Ctr=[[-2,-.3],[0,.2],[2,.7]], c=(0,.2), observed e1, empirical sigma=(2.0000000025,.50000001), the source ellipsoid support with kappa1 yields (2.0000000025,.2), sparse top1 rho1 yields (1,.2). At the README illustrative radii these produce (15.000000019,.2) vs (5,.2). Thus reported experiments need not be duplicates even though class implementation is shared.

D4 Rival explanation: static observed-action adversarial data are a deliberate cheap surrogate; paper theoretical predictor-dependent max-Regret uses Danskin differentiation. Robust DFL IJCAI2024 and later optimization gradients are known. No novelty claim or refutation of published task results.

D5 CPU test /mnt/data/r028/robust_dfl_config_audit.py uses pinned formula but does NOT import PyEPO or Gurobi. Script SHA256 907de1c60a8907b2ac7c9e58e48746685db44b4f63cb34b675f2867a85bb8097, receipt SHA256 cfc74ada0f5771de3974f6c196ff4bb1880bf6d5c70986efdb2b9af7130ba61d. Native experiments require solver access and fair matched configs plus original distinct published configs. Negative control under identical config shows same labels.

D6 Status: deep source audit, no new original algorithm or trained model effect, formal independent reviewer pending, no GPU or paid API.
