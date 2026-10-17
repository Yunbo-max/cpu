# CREDO selection / independent recalibration protocol (frozen 2026-10-17)

## Question

On CREDO synthetic Setting I (`sigma=0.1`), does choosing the largest source `get_prob` score from one calibration sample produce an optimistic selected score relative to recomputing that selected decision's score on an independent calibration sample?

## Design

- 200 independent replicates, seeds 91000–91199.
- Each replicate uses 100 training, 100 selection-calibration, and 100 independent evaluation-calibration observations from the same known Gaussian distribution. This is exchangeable and separates the selection data from evaluation calibration data.
- Fit one Gaussian component to training data, matching the source notebook's Setting I.
- With the source implementation and `K=100`, select `argmax(get_prob)` using selection calibration. Score that same selected vertex again using the independent evaluation calibration and the same fitted generative model.
- Compare paired same-calibration selected score minus independent-calibration selected score, plus the fixed-origin score as a nonselected control. Estimate true vertex optimality probabilities from a separate 1,000,000-draw reference sample.
- One CPU thread; no parameter sweep.

## Endpoints

Primary: mean paired score difference, same-calibration selected score minus independent-calibration score for that same selected vertex. Secondary: both scores relative to the selected decision's known-distribution optimality frequency. Use paired normal 95% intervals descriptively.

This exploratory diagnostic cannot establish general post-selection validity or novelty. All prior data and results have been inspected.
