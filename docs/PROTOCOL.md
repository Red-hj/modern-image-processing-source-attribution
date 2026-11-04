# Analysis protocol

This protocol describes the scoring and decision analyses used in *When Restoration Gains Reverse in Camera Attribution*. The supplied inputs are recorded score vectors, scalar D/L components, paired query identities and resampling weights. The scripts reconstruct the analyses from those values.

## 1. Images, roles and pairing

Each parent is one original photograph. Its degraded and restored versions retain the same parent identifier and reference, calibration or evaluation role. Candidate galleries and reference templates remain fixed within a controlled comparison.

CSAFE has nine devices with 26 evaluation parents per device, giving 234 queries. Core ForensiCam has ten devices and 80 evaluation queries per domain (indoor and outdoor), giving 160. These form the 394-parent core analysis. The additional ten-device native-JPEG cohort has another 80 evaluation queries per domain and is reported separately. Each device uses 50 reference parents. The two JPEG qualities reuse the CSAFE evaluation parents.

## 2. Scores and rankings

At each internal scale, D is the sum of residual-template products and L is the learned matching logit. The original score adds D and L in float32 at scales 1400 and 1024, then merges them with weights 1 and float32(1024/1400). The fixed-residual D control removes L while retaining the residuals, templates, product sums, weights and arithmetic.

Raw scores refer to matcher outputs before candidate-specific EER division. That division is a separate candidate mapping, distinct from both the original score and the gallery acceptance cutoff.

A strict correct ranking requires the true source to score higher than every other candidate. Before/after comparisons retain both losses of previously correct queries and gains on previously incorrect queries.

## 3. Acceptance and reported answers

At a common cutoff tau, admit every candidate whose score is at least tau. The two output actions evaluate different answers:

|Action|Correct (C)|Wrong (W)|Rejected (R)|
|---|---|---|---|
|Accepted set|The true source is the sole admitted candidate|Any wrong candidate is admitted|No candidate is admitted|
|Winner|The true source is the unique highest-scoring admitted candidate|A wrong source is the unique highest-scoring admitted candidate|The set is empty or the highest score is tied|

A set containing wrong candidates can still return a correct winner if the true source is uniquely highest. With K denoting correct rankings, J their below-cutoff rejected subset, and M correct winners selected from ambiguous accepted sets, the recorded counts satisfy:

```text
correct winners = K - J = correct singleton sets + M
```

The 20% allowance concerns wrong sets in the designated calibration pool. For m calibration parents, sort each parent's maximum wrong-candidate score in descending order, set k = floor(0.20*m), and place the cutoff at the next representable value above the (k+1)-th score. The raw-path analysis retains all budgets k = 0,...,m, including the all-admitted endpoint. This calibration allowance and outside-gallery false acceptance have different events and denominators.

SS fits each processing state's own cutoff. CN applies the degraded-state cutoff to both states; CR applies the restored-state cutoff to both. The score/cutoff crossings retain the state being held fixed and the replacement order used for each contrast.

## 4. Amplitude and component exchanges

The Gaussian amplitude records contain four matched residual states: the degraded endpoint, degraded structure with restored amplitude, restored structure with degraded amplitude, and the restored endpoint. Each amplitude ratio is determined by that parent's observed scale-wise RMS values. These exchanges differ from dividing every query residual by its own RMS to obtain a unit-amplitude input.

For a query that loses correct ranking after restoration, reproduction means that restored amplitude on degraded structure also loses correctness. Rescue means that degraded amplitude on restored structure restores correctness. Bidirectional coverage requires both events on the same lost parent: two of 13 BM3D losses and five of 13 Restormer losses in the recorded Gaussian experiment.

Saved-component crosses compare D0+L0, D1+L0, D0+L1 and D1+L1 with the original scale-wise arithmetic. Actual endpoint crosses on the additional cohort and crosses within amplitude pairs retain their respective pair identities.

The precision analysis recombines saved D/L values with the same float32-represented weight using float64 and exact-rational arithmetic. It checks 8,916 configurations and 81,204 candidate scores, while retaining the original D/L inputs and weight value.

## 5. Conditional ranges and verification

The 22 conditional ranges preserve paired query events. CSAFE resamples parents within its nine fixed devices; ForensiCam uses eight shared S-label content groups per domain and keeps each group's devices, candidates and states together. The fitted rules stay fixed. These pointwise ranges condition on the recorded galleries, parent composition and sampling units.

Raw verification compares genuine and wrong-source scores across queries. Each query contributes one genuine comparison and all wrong-candidate comparisons. ROC/DET, AUC and paired AUC ranges preserve those within-query dependencies; the stored paired weights provide 2,000 resampling draws. Candidate rankings, accepted answers and pooled verification retain their own comparison units.
