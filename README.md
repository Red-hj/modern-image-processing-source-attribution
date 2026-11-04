# When Restoration Gains Reverse in Camera Attribution

Code and saved data for the paper *When Restoration Gains Reverse in Camera Attribution*.

## What the paper studies

Source-camera attribution uses weak device traces in an image to identify the camera that captured it. Restoration can reduce reconstruction error while reducing correct attribution. The paper studies where these changes arise after a specified restoration: in scoring and candidate ranking, candidate acceptance, or the final reported answer. Paired amplitude and component exchanges further test which actual ranking losses a local scoring response explains.

The saved data in this package correspond to three main findings:

- **Score composition changes the restoration response.** On CSAFE, correct raw rankings change from 215 to 203 with the original D+L score, and from 218 to 221 with the D control that removes the learned logit while keeping the residuals fixed. The indoor subsets of two ForensiCam cohorts show the opposite interaction.
- **Candidate sets and top-ranked outputs can change in opposite directions.** At the reported 20% wrong-set calibration allowance with state-specific calibration, CSAFE singleton-correct sets change from 152 to 160, while correct winners change from 211 to 176. The paired range for the set increase is [-9, 25]; stricter allowances and shared cutoffs change the comparison.
- **Mechanism coverage is measured on actual losses.** Bidirectional amplitude exchanges reproduce and rescue the same two of 13 BM3D losses and five of 13 Restormer losses.

## How to run

Use Python 3.10 or newer. First check file integrity:

```sh
python scripts/check_package.py
```

Use the Python standard library to reproduce core rankings, crossed answers, additional-cohort component states, Gaussian amplitude coverage, and 22 conditional ranges:

```sh
python scripts/reproduce.py --core-only
```

After installing the dependencies, the full entry point also computes raw ROC/DET, AUC and paired ranges:

```sh
python -m pip install -r requirements.txt
python scripts/reproduce.py
```

Check 4,758 recorded raw acceptance-path rows, 8,916 fixed-weight merge configurations and 81,204 exact-rational candidate scores:

```sh
python scripts/reproduce_paths_precision.py
```

The programs compare their results with `expected/`, write generated files to `results/`, and print a `PASS_...` status on success. The raw paths are previously recorded results; the precision check concerns the arithmetic combining the same saved D/L values and represented weight.

Optional plots:

```sh
python scripts/plot_raw_paths.py
python scripts/plot_verification.py
```

Run the full reproduction before plotting verification curves. Raw-path plots read the saved reference results. All plots are written under `results/figures/`.

## Relationship between files and paper analyses

|Paper analysis|Main data (under data/)|Reference results (under expected/)|
|---|---|---|
|Fixed-residual scoring and rankings|core_scores.json, native_components.json|core_ranks.csv, native_rank_summary.csv|
|Acceptance and output|core_scores.json, raw_path_inputs.json|CSAFE_crossed_answers.csv, raw_paths.csv|
|Amplitude coverage on actual losses|amplitude_scores.json|amplitude_counts.csv, amplitude_coverage.csv|
|Paired conditional ranges|paired_contrasts.csv|conditional_ranges.csv|
|Raw verification and same-model centering|raw_verification_scores.json, resampling_weights.npz, classical_centering_scores.json|raw_ROC_DET.csv, raw_verification_AUC.csv, classical_centering_answers.csv|
|Fixed-weight merge precision|merge_components.json|merge_precision_rows.csv|

`src/camera_attribution/` contains scoring, decision, uncertainty and verification implementations. `scripts/` provides reproduction and plotting entry points; `docs/` describes the protocol and third-party sources. `data/PROVENANCE.json` records source identities and hashes. Parent identities, device labels, candidate order and processing-state pairing are retained.

## Data and scope

CSAFE and core ForensiCam contain 394 evaluation parents in total. The additional ten-device native-JPEG cohort has 160 evaluation parents and is reported separately; its 50-reference-parent-per-device setting is retained. Processing states and JPEG qualities reuse the same parents.

See the [protocol](docs/PROTOCOL.md) and [third-party sources](docs/THIRD_PARTY_NOTICES.md). Third-party images and weights are accessed under their original distribution terms.
