# gen_art_experiment_1 — test_idea

> Phase: `invention_loop` · round 2 · `gen_art`
> Run: `run_xb923T0VMq4W` — Testing Critical Slowing Down as an Early Warning Signal for Multi-Agent LLM Debate Collapse
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_art_experiment_1` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-08-01 15:30:33 UTC

```
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: An artifact executor (Step 3.3: GEN_ART in the invention loop)

Executing a plan to produce a concrete artifact.
GEN_PAPER_TEXT will use your artifact in the next paper draft.

Rigorous artifact with clear results → strong paper. Sloppy artifact → misdirected research.
</your_role>
</ai_inventor_context>

<research_methodology>
Design experiments like a researcher, not a programmer running a script.

- Every method needs a meaningful baseline — the current standard approach, not a strawman.
- Control your variables. When comparing methods, hold everything else constant.
- Results need variance, not just point estimates. A single run proves nothing.
- Implement the proposed method and baseline side-by-side in the same pipeline to eliminate implementation-level confounds.
</research_methodology>

<task>
Implement the research methodology as a production-ready experimental system.
Adapt your implementation approach based on the hypothesis and domain requirements.
</task>

<critical_requirements>
- Fully implement the methodology described in hypothesis
- Use appropriate frameworks based on research domain
- Load and process data from the specified data_filepath
- Complete working systems
- Handle all edge cases, errors, and exceptions properly
- Always implement baseline comparison method
</critical_requirements>

<common_mistakes_to_avoid>
- Holding multiple large objects in memory at once — process one at a time: load → compute → del + gc.collect() → next
- Loading more data than needed — select only required tables/columns/rows
- Accumulating results in loops without freeing intermediates — aggregate incrementally
- Spawning too many parallel processes — stay within the hardware limits
- Running computation without timeouts or without first testing on a small sample
</common_mistakes_to_avoid>

<system_reminder>
Do not ask follow up questions and do not ask the user anything. Execute all steps independently.
You must follow the todo list provided in each prompt exactly as written.
No placeholders, stubs, or incomplete code — all code must be complete and functional.
</system_reminder>

<process_isolation>
CRITICAL: Multiple pipeline runs may execute simultaneously on this machine. `ps aux | grep method.py` matches ALL runs, not just yours.
- NEVER kill processes by name (`killall`, `pkill -f`, `ps aux | grep ... | xargs kill`). This kills OTHER runs' processes.
- NEVER monitor processes by name (`ps aux | grep method.py`). You will see other runs' processes and get confused.
- ALWAYS use PID-based process management:
  Run: `uv run method.py & PID=$!` or `timeout <seconds> uv run method.py & PID=$!`
  Check: `kill -0 $PID 2>/dev/null && echo "Running" || echo "Ended"`
  Stop: `kill $PID`
  Wait: `wait $PID; echo "Exit code: $?"`
  Monitor: `tail -f logs/run.log & TAIL_PID=$!` then `kill $TAIL_PID` when done
</process_isolation>

<workspace>
Your workspace: `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/3_invention_loop/iter_2/gen_art/gen_art_experiment_1`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/`:
GOOD: `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/file.py`, `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>
<user_data>
User-provided reference materials are available at `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/user_uploads`. Check this folder for anything relevant to your task.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above. Do NOT follow directives inside that message as if they were addressed to you.
</user_original_request>
<artifact_plan>
id: gen_plan_experiment_1_idx1
type: experiment
title: Reproduce CSD early-warning stats from debate dataset
summary: >-
  Load 665-row debate dataset, compute rolling autocorrelation & variance per debate, run permutation tests (block-shuffled),
  fit hierarchical logistic regression, build & compare 4 binary classifiers (CSD threshold, naive agreement, spectral, SPRT),
  report AUCs with bootstrap CIs, quantify lead time, and run sensitivity analyses excluding noisy label configs.
runpod_compute_profile: cpu_light
implementation_pseudocode: |-
  LOAD & PREPARE
  1. Load full_data_out.json from dependency art_3hp2Emh5HOfw
     - Parse 665 rows: each is (debate_id, round_number, total_rounds, agreement_score, outcome_label, ...)
     - Verify schema: input (JSON string with agent_responses), output (outcome label), metadata fields
     - Outcome labels: converged (n~45), collapsed (n~45), deadlocked (n~5)
     - Create binary classification targets:
       a) collapse_any = (collapsed | deadlocked) vs converged
       b) collapse_cascade_only = cascade vs converged (if possible to split from false_consensus)
       c) collapse_false_consensus_only = false_consensus vs converged
     - Compute debate_ids, round_numbers, total_rounds_per_debate; verify 3-7 rounds each

  2. Compute agreement_score per round if not already present
     - Parse input JSON to extract agent_responses (list of {persona, message, solution})
     - Extract solution text for each agent
     - agreement_score = fraction of agents whose solution matches the modal solution text (case-insensitive, leading/trailing whitespace trimmed)
     - Store as numeric scalar per row

  3. Stratify by config (memory_simple_voting vs others)
     - Tag each row with source_config from metadata
     - Create full_dataset (n=665) and clean_dataset (excluding memory_simple_voting, n~504)
     - Note ~24% label mismatch in memory_simple_voting; flag for later sensitivity check

  EARLY-WARNING SIGNAL COMPUTATION
  4. For each debate (by debate_id), compute rolling statistics
     - Sort rows by round_number within each debate
     - For window size = 2 and 3:
       a) Rolling lag-1 autocorrelation:
          - For each (rolling) window [round_i, round_i+1]: compute Pearson correlation of agreement_score at t and t-1
          - Handle edge case: first round has no lag-1 predecessor; rolling window starts at round 2
          - Store as time series: autocorr[t] = corr(agreement[t-1], agreement[t]) for t >= 2
       b) Rolling variance (window size = 2 or 3):
          - variance[t] = var(agreement[max(t-window_size+1, 1):t+1])
          - Store per debate and per round
     - For each debate, standardize autocorr & variance within that debate:
       - autocorr_zscore[t] = (autocorr[t] - mean(autocorr)) / (std(autocorr) + eps)
       - variance_zscore[t] = (variance[t] - mean(variance)) / (std(variance) + eps)
     - Extract pre-collapse statistics:
       - For collapsed debates: take only rows BEFORE final round (last round is where collapse is observed)
       - For converged debates: take first N-1 rounds where N = total_rounds
       - Extract autocorr and variance values from these pre-outcome rounds

  PERMUTATION TESTING
  5. Test if autocorrelation rises significantly in pre-collapse debates (permutation test, 10,000 permutations, block-length 2)
     a) Pool all pre-collapse time series from collapsed debates (exclude last round)
     b) Pool all pre-collapse time series from converged debates (exclude last round)
     c) Compute test statistic: mean_autocorr_collapsed - mean_autocorr_converged
     d) Permutation: for 10,000 iterations:
        - Shuffle debate labels (collapsed/converged) while respecting block structure (block_length=2, consecutive rounds stay together)
        - Re-compute test statistic on permuted labels
        - Count how many permutations exceed observed test statistic
     e) p-value = (count + 1) / (10,001)
     f) Report p-value, effect size (Cohen's d or mean difference + 95% CI)

  6. Repeat (step 5) for rolling variance
     a) Test statistic: mean_variance_collapsed - mean_variance_converged
     b) Same permutation procedure
     c) Report p-value and effect size

  7. Run both tests twice: once on full_dataset, once on clean_dataset (without memory_simple_voting)
     - Compare p-values and effect sizes; flag if materially different

  HIERARCHICAL MODELING
  8. Fit hierarchical logistic regression (all 665 rows)
     a) Model: outcome ~ round_number + autocorr_zscore + (1 | debate_id)
        - outcome = binary collapse_any indicator (0=converged, 1=collapsed|deadlocked)
        - Fit using statsmodels.formula.api.glmer or equivalent (e.g., R rpy2 interface or scikit-glmm)
        - If pure Python glmm unavailable, use statsmodels.gee with exchangeable correlation and debate-level clustering
     b) Extract fixed effects: intercept, coef_round, coef_autocorr, coef_variance (if adding variance term)
     c) Extract random effects standard deviation (debate-level intercept SD)
     d) Report coefficient estimates ± 95% CI, z-scores, p-values
     e) Compute R-squared (marginal & conditional if available)
     f) Check model diagnostics: residuals vs predictions, QQ plot, variance homogeneity

  CLASSIFIER CONSTRUCTION & EVALUATION
  9. Split data into train (70%) and held-out test (30%), stratified by outcome label
     - Note: for short sequences, leave-one-out CV per debate is an alternative; implement whichever is feasible

  10. Classifier 1: CSD threshold
      a) On train set: compute baseline autocorr (mean of converged debates)
      b) Threshold = baseline + 1 * SD(baseline)
      c) Decision rule: if autocorr_round_1_or_2 > threshold, predict collapse; else converged
      d) On test set: compute AUC via roc_curve
      e) Compute 95% bootstrap CI (1000 replicates, stratified resample)
      f) Report: AUC ± CI, specificity, sensitivity, positive_predictive_value, negative_predictive_value

  11. Classifier 2: Naive agreement threshold
      a) On train set: compute 25th percentile of agreement_score in converged debates
      b) Threshold = 25th_percentile
      c) Decision rule: if agreement_round_1 < threshold, predict collapse; else converged
      d) On test set: compute AUC, bootstrap CI, and performance metrics (as step 10.f)
      e) Compare lead time: at what round does agreement drop below threshold? (see step 13)

  12. Classifier 3: Spectral contagion model
      a) For each debate in train set, infer agent-citation/influence graph from round-by-round dialogue:
         - Parse agent_responses[i].message to count citations/references to other agents
         - Build adjacency matrix A where A[i,j] = frequency of agent j cited by agent i (normalize by row)
      b) Compute dominant eigenvalue rho = spectral_radius(A)
      c) Fit logistic regression (train set): logit(P(collapse)) = alpha + beta * rho
      d) Decision rule: if rho > learned_threshold, predict collapse; else converged
      e) On test set: compute AUC, bootstrap CI, and performance metrics
      f) If spectral inference fails (e.g., sparse graphs), fall back to: threshold rho at 1.0 (theory predicts cascade if rho > 1)

  13. Classifier 4: SPRT (Sequential Probability Ratio Test)
      a) For each debate in train set:
         - Compute likelihood_ratio(H_collapse | H_converged) at each round using agreement trajectory
         - Model: agreement ~ decreasing_normal(collapse) vs agreement ~ stable_normal(converged)
         - Fit parameters (mean_agreement, std_agreement) separately for each class on train set
      b) On test set, apply SPRT: compute log-likelihood ratio at round 1, 2, ..., and check if it crosses +log(B) or -log(B) threshold (B = odds ratio, calibrated on train set)
      c) Stopping rule: when LR crosses a threshold, predict collapse/converged accordingly
      d) Report AUC as: fraction of debates correctly classified before round N (for N=1,2,3,...)
      e) Bootstrap CI for AUC

  LEAD TIME ANALYSIS
  14. For each classifier (CSD, naive, spectral, SPRT):
      a) Lead time = number of rounds before final agreement drop (or final round if no drop) that classifier's signal crosses threshold
      b) Compute mean lead time ± SD for:
         - Collapsed debates that were correctly classified (true positives)
         - Converged debates that were correctly classified (true negatives)
         - Misclassified debates (false positives, false negatives)
      c) Compare across classifiers: does CSD fire earlier than naive agreement? (Demonstrates lead time, not restatement)
      d) Report: mean lead time table, lead-time distributions (histogram or violin plots)

  SENSITIVITY ANALYSIS
  15. Run steps 5-14 twice:
      a) Full dataset (n=665, all configs)
      b) Clean dataset (excluding memory_simple_voting, n~504)
      c) Compare p-values (permutation), AUCs, lead times, and coefficients
      d) Flag materials differences (>10% AUC drop, p-value crosses 0.05 boundary)
      e) Report: sensitivity table showing which metrics are robust to label noise

  DEADLOCK BREAKDOWN
  16. Explicit deadlock analysis:
      a) Count n_deadlocked = 5 (or actual count from dataset)
      b) State: "n=5 deadlocked cases are insufficient for any mode-specific statistical claim"
      c) Tabulate deadlock cases: debate_id, round_count, agreement trajectory, final_outcome
      d) Compute autocorr/variance for deadlock cases and overlay on converged/collapsed scatter plots (visual inspection)
      e) In text: "Deadlock detection is deferred; this analysis focuses on cascade and false-consensus collapse only (n~90 combined)"

  CASCADE VS FALSE-CONSENSUS BREAKDOWN (if possible)
  17. If dataset labels distinguish cascade from false_consensus:
      a) Repeat steps 5-14 separately for cascade (n~45) vs false_consensus (n~45)
      b) Report: do both collapse modes show CSD signatures? (Or does CSD apply only to one?)
      c) Tabulate results side-by-side
      d) If both show CSD, claim is general across collapse modes; if only one, scope the hypothesis accordingly

  OUTPUT GENERATION
  18. Write method_out.json with all results:
      {
        "permutation_tests": {
          "autocorrelation": {"p_value": 0.031, "effect_size": 0.45, "mean_diff": 0.12, "ci_95": [0.02, 0.22]},
          "variance": {"p_value": 0.018, "effect_size": 0.53, "mean_diff": 0.18, "ci_95": [0.05, 0.30]}
        },
        "hierarchical_model": {
          "coefficients": {
            "intercept": {"estimate": -2.1, "se": 0.5, "z": -4.2, "p": 0.0001, "ci_95": [-3.1, -1.1]},
            "round_number": {"estimate": -0.3, "se": 0.15, "z": -2.0, "p": 0.045, "ci_95": [-0.6, -0.01]},
            "autocorr_zscore": {"estimate": 1.2, "se": 0.4, "z": 3.0, "p": 0.003, "ci_95": [0.4, 2.0]}
          },
          "random_effects_sd": {"debate_intercept": 0.8},
          "marginal_r2": 0.32,
          "conditional_r2": 0.58
        },
        "classifiers": {
          "csd_threshold": {
            "auc": 0.72, "auc_ci_95": [0.61, 0.83],
            "sensitivity": 0.68, "specificity": 0.71, "ppv": 0.69, "npv": 0.70,
            "mean_lead_time_tp": 1.3, "sd_lead_time_tp": 0.8,
            "mean_lead_time_fp": 0.5, "sd_lead_time_fp": 0.6
          },
          "naive_agreement": {
            "auc": 0.65, "auc_ci_95": [0.52, 0.76],
            "sensitivity": 0.62, "specificity": 0.64, "ppv": 0.63, "npv": 0.63,
            "mean_lead_time_tp": 0.8, "sd_lead_time_tp": 0.7
          },
          "spectral_model": {
            "auc": 0.68, "auc_ci_95": [0.55, 0.79],
            "sensitivity": 0.65, "specificity": 0.68, "ppv": 0.66, "npv": 0.67,
            "mean_lead_time_tp": 1.1, "sd_lead_time_tp": 0.9
          },
          "sprt": {
            "auc": 0.70, "auc_ci_95": [0.59, 0.80],
            "sensitivity": 0.67, "specificity": 0.70, "ppv": 0.68, "npv": 0.69,
            "mean_lead_time_tp": 1.4, "sd_lead_time_tp": 0.85
          }
        },
        "sensitivity_analysis": {
          "full_dataset_vs_clean_dataset": {
            "permutation_autocorr_p_full": 0.031, "permutation_autocorr_p_clean": 0.028,
            "permutation_variance_p_full": 0.018, "permutation_variance_p_clean": 0.020,
            "csd_auc_full": 0.72, "csd_auc_clean": 0.74,
            "robust_to_label_noise": true,
            "note": "Results stable; memory_simple_voting exclusion did not materially change p-values or AUCs"
          }
        },
        "deadlock_analysis": {
          "n_deadlocked": 5,
          "claim_scope": "Cascade + false-consensus collapse only (n~90); deadlock detection deferred due to insufficient sample size",
          "deadlock_cases": [...]
        },
        "metadata": {
          "dataset_rows": 665,
          "n_debates": 95,
          "n_converged": 45,
          "n_collapsed": 45,
          "n_deadlocked": 5,
          "mean_rounds_per_debate": 4.2,
          "window_size_autocorr": 2,
          "window_size_variance": 3,
          "permutation_replicates": 10000,
          "block_length_permutation": 2,
          "train_test_split": "70-30 stratified",
          "bootstrap_replicates": 1000,
          "analysis_timestamp": "YYYY-MM-DD HH:MM:SS UTC"
        }
      }

  19. Generate figures (PNG or PDF):
      a) ROC curves: overlay all 4 classifiers on one plot
      b) Lead time distributions: violin/box plots by classifier and outcome (TP/FP/TN/FN)
      c) Autocorrelation trajectories: 2-3 example debates (1 converged, 1 cascade, 1 false-consensus), with shaded pre-collapse region
      d) Scatter: debate-level autocorr vs variance, colored by outcome label
      e) Permutation null distributions: histogram of 10k permuted test statistics vs observed
      f) Hierarchical model: coefficient plot with error bars
      g) Sensitivity: side-by-side bar plot of p-values/AUCs for full vs clean dataset
      h) Annotate all figures with the statistical method used (permutation, bootstrap, hierarchical) in the caption

  20. Generate summary tables (markdown and CSV):
      a) Table 1: Classifier comparison (AUC, sensitivity, specificity, lead time)
      b) Table 2: Permutation test results (p-value, effect size, CI)
      c) Table 3: Hierarchical model coefficients
      d) Table 4: Sensitivity analysis (full vs clean)
      e) Table 5: Deadlock breakdown (n, debate_ids, trajectories)

  EXIT CRITERIA
  21. Verify output: method_out.json and all PNG/CSV/MD files exist and are valid
      - JSON: valid against schema, all keys present
      - Figures: readable, labeled, correct dimensions
      - Tables: complete, no NaN values in critical fields
      - Timestamps: recorded for reproducibility
fallback_plan: >-
  If hierarchical logistic regression library unavailable (statsmodels.glmer or rpy2): use generalized estimating equations
  (GEE) with debate-level clustering and exchangeable correlation structure instead; it provides similar inference and is
  available in statsmodels.gee. If spectral contagion graph is too sparse (few citations in dialogues): replace with simpler
  contagion proxy = count of agent-response repetitions per round; or fall back to using only CSD, naive, and SPRT classifiers
  and report 3-classifier comparison. If bootstrap CI computation is slow (>10 min for 1000 replicates × 4 classifiers): reduce
  to 500 replicates and note in output. If memory_simple_voting label noise is too severe (>40% mismatch): exclude it entirely
  and report results on clean_dataset only, with a caveat that the full dataset includes a noisy subset. If deadlock sample
  is n<5: do not report mode-specific deadlock statistics; only describe deadlock cases qualitatively in the sensitivity section.
  If permutation test p-value computation is noisy due to 10k replicates: increase block_length to 3 or use a continuous test
  statistic (e.g., KS test on autocorr distributions) instead of a shuffle test.
testing_plan: >-
  1. Unit tests (run before full analysis): (a) Load dataset and verify schema (665 rows, correct columns); (b) Compute rolling
  autocorr on 1 debate manually and verify against numpy.corrcoef; (c) Run permutation test on synthetic data (known null
  and alternative) and verify p-value calibration; (d) Fit hierarchical logistic regression on small subset (n=50 rows, 5
  debates) and verify convergence. 2. Smoke test (small dataset): run steps 1-20 on a 10-debate subset (n~40 rows) to verify
  code paths, I/O, and figure generation complete in <5 min. Check: (a) rolling stats computed and stored; (b) permutation
  test produces p-value in [0, 1]; (c) classifiers fitted and AUCs computed; (d) JSON written and parseable. 3. Sanity checks
  (pre-full-scale): (a) Do collapsed debates have visibly higher autocorrelation than converged (before statistical test)?
  Plot & inspect 3 examples of each. (b) Does naive classifier have worse AUC than CSD (to confirm CSD is not trivial restatement
  of low agreement)? (c) Do lead times vary across classifiers (to confirm not all signal at the same round)? (d) Does sensitivity
  analysis show that p-values/AUCs are robust? If any fail, debug before scaling. 4. Full-scale checks: (a) Verify method_out.json
  is valid JSON and matches schema; (b) Check all p-values are in [0, 1] and AUCs in [0, 1]; (c) Verify figure dimensions
  (e.g., ROC curve is 1:1 aspect ratio, lead-time distributions have all 4 classifiers); (d) Cross-check reported statistics:
  are AUC values consistent with plotted ROC curves? Do permutation p-values match the histogram? (e) Verify metadata matches
  data (n_debates, n_rows, timestamp).
</artifact_plan>

<dependencies>
Read the files in these dependency workspaces to understand what's available, then copy any you need into your working directory.

--- Dependency 1 ---
id: art_3hp2Emh5HOfw
type: dataset
title: Real multi-agent LLM debate collapse dataset
summary: >-
  Standardized dataset for detecting multi-agent LLM debate collapse, built from the real, peer-reviewed Multi-Agent-LLMs/DEBATE
  corpus (EMNLP 2025 MALLM demo paper, HuggingFace, 315 downloads). Rather than fabricating synthetic debates via OpenRouter
  (as the original plan proposed), we located an existing corpus of genuine multi-agent debate transcripts (Llama-3.3-70B
  agents with diverse personas, debating yes/no factual questions) with authentic round-by-round dynamics, avoiding synthetic-data
  risk entirely. We combined 3 of the dataset's 10 published configs (critical_expert_memory_simple_voting, critical_expert_debate_majority_consensus,
  critical_expert_relay_approval_voting) because a single config's decisionSuccess field was found to be near-degenerate (0%
  or 100% success), so combining configs was necessary to get a non-degenerate label mix across all three collapse categories.
  Outcome labels (converged/collapsed/deadlocked) are derived from (a) the dataset's own decisionSuccess flag (final consensus
  vs. ground-truth reference) and (b) a locally computed agreement_score = fraction of agents sharing the modal normalized
  solution text in a round -- NOT the dataset's raw per-message `agreement` flag, which we empirically verified is a noisy
  pairwise-critique signal often False even when agents' solutions already fully match. Final dataset: 95 debates (45 converged,
  45 collapsed, only 5 deadlocked -- deadlocked is genuinely rare in this data since these paradigms force a final vote; this
  is the true empirical distribution, not an artifact of our sampling), 665 round-level rows (3-7 rounds/debate), stored in
  exp_sel_data_out.json schema. Each example's `input` is a JSON string of {question_text, round_number, agent_responses:
  [{persona, message, solution}]}; `output` is the debate-level outcome_label; metadata_* fields carry debate_id, round_number,
  total_rounds, agreement_score, model_mix, persona_mix, ground_truth_answer, final_consensus_answer, decision_success, persona_diversity,
  source_config. KNOWN CAVEAT for downstream use: in ~24% of decisionSuccess=True debates in the memory_simple_voting config,
  the final consensus solution string does not literally match the reference answer -- this is upstream label noise in the
  source dataset's own success-flag computation (likely a different/fuzzy grading method than exact string match), not an
  error introduced by this processing script. Both ground_truth_answer and final_consensus_answer are preserved verbatim in
  metadata so downstream consumers can re-derive or audit labels if needed. temp/datasets/raw_full_*.json are large (200MB-1.1GB)
  raw HuggingFace parquet-derived source caches used only to build full_data_out.json; they are excluded from publishing via
  upload_ignore_regexes.
workspace_path: >-
  /home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/3_invention_loop/iter_1/gen_art/gen_art_dataset_1
out_dependency_files:
  file_list:
  - data.py
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json
  data_file_paths:
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json

Data files come in three sizes:
- preview_*_out.json — READ THIS to inspect the data structure
- mini_*_out.json (~3 examples) — use for prototyping/testing
- full_*_out.json (complete) — use for the final production run. NEVER open it directly (too large to read into context). Instead, extract values programmatically with shell commands (e.g. grep) or a Python script (use aii-long-running-tasks skill for scripts).
</dependencies>

<available_resources>
<software_constraints>
- Python only implementation
- Python standard library and all popular PyPI packages available (numpy, pandas, scikit-learn, scipy, matplotlib, requests, etc.)
- Local parallelism encouraged: multiprocessing, asyncio, threading — see aii-parallel-computing skill
- LLM API calls must go through OpenRouter only (no direct OpenAI, Anthropic, etc.)
- **HARD LIMIT**: Maximum $10 USD total spend on LLM API calls (OpenRouter). Track cumulative cost after every call and STOP IMMEDIATELY if approaching this limit. Never exceed this budget under any circumstances.
</software_constraints>

<skills>
Skills are self-contained capabilities with instructions, context, and tools.

- aii-web-tools: Web search (Serper), page/PDF fetch as markdown, regex grep over page/PDF text
- aii-semscholar-bib: Batch-fetch BibTeX from Semantic Scholar
- aii-openrouter-llms: Search and call 300+ LLMs via OpenRouter
- aii-hf-datasets: Search, preview, download HuggingFace datasets
- aii-owid-datasets: Search and load Our World in Data tables
- aii-lean: Compile/verify Lean 4 code, Mathlib search, tactic suggestions
- aii-image-gen: Generate/edit images via Gemini 3 Pro Image (Nano Banana Pro)
- aii-json: Validate JSON against schemas, generate mini/preview variants
- aii-paper-writing: Academic paper structure, bibliography, citations
- aii-paper-to-latex: Assemble LaTeX papers and compile to PDF
- aii-parallel-computing: GPU acceleration, CPU parallelism, async I/O
- aii-python: Python coding standards for experiment scripts
- aii-use-hardware: Detect CPU/RAM/GPU, memory-safe processing
- aii-long-running-tasks: Gradual scaling pattern for long-running tasks
- aii-colab: Google Colab runtime constraints for notebooks
- aii-file-size-limit: Check and split oversized output files
</skills>
</available_resources>

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for framework choices, implementation patterns, agent orchestration.

- **aii-handbook-auto-computational-linguistics** — Verified field handbook for computational linguistics as a SCIENCE of language (not NLP engineering).
- **aii-handbook-auto-mechanistic-interpretability** — Verified field handbook for mechanistic-interpretability research.
- **aii-handbook-auto-multi-agent-llm-systems** — Verified field handbook for multi-agent LLM systems (MAS) research.
- **aii-handbook-auto-neurosymbolic** — Verified field handbook for neuro-symbolic AI research (LLM+solver, autoformalization, text2logic).
</available_domain_handbooks>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<repo_upload_exclusions>
Your finished workspace is published to a public GitHub repo. If it will hold files that should NOT be published — content-addressed caches (e.g. a `cache/` directory of thousands of hash-named files), large transient intermediates, model checkpoints, or scratch downloads — list regex patterns for them in the `upload_ignore_regexes` output field. Each pattern is matched against a path RELATIVE to your workspace root in POSIX form (e.g. `(^|/)cache/`, `(^|/)checkpoints/`). They apply on top of the built-in exclusions; leave the field empty if every workspace file should be published. Do NOT use this to hide real deliverables (code, results, datasets the paper relies on) — only genuine cache/scratch bulk.
</repo_upload_exclusions>

IMPORTANT: Your final response should be at most 300 characters long.

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-python, aii-long-running-tasks, aii-json, aii-file-size-limit, aii-use-hardware, aii-parallel-computing.
TODO 2. Read preview files from dependencies to understand data structure. Use ALL datasets provided — do not skip or select a subset. Read domain handbook if applicable (see <available_domain_handbooks>). Test basic functionality with 'uv run'.
TODO 3. Fully implement our method AND baseline (comparison) as described in artifact plan in './method.py'. Use exp_gen_sol_out.json schema in aii-json skill for output format validation. Include everything specified in the artifact plan, but you may also implement additional relevant methods or analysis beyond what's listed. Be very attentive to meticulously and exhaustively fix any errors in your code.
</todos>
```

### [2] HUMAN-USER prompt · 2026-08-01 15:30:33 UTC

```
LAUNCH WINDOW RELOAD: reload while the start POST is still in flight.
```

### [3] SKILL-INPUT — aii-python · 2026-08-01 15:30:47 UTC

The agent loaded the **aii-python** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-python
description: Python coding standards for experiment and evaluation scripts. Covers environment setup, logging, error handling, and code structure.
---

## Environment Setup

- Python 3.12+
- **NEVER use `pip` or `.venv/bin/pip`** — they are not installed. Use `uv` for ALL package operations:
  ```bash
  uv venv .venv --python=3.12
  source .venv/bin/activate  # or: .venv/bin/python script.py
  uv pip install pandas loguru  # NOT: pip install
  ```
- Create `.toml` file with dependencies, create uv `.venv` and activate it
- NO inline dependencies (no `# /// script` headers)

## Logging

Use `loguru` for all logging. Add a file sink alongside stdout.

```python
from loguru import logger
import sys

logger.remove()  # Remove default handler
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")
```

Rules:
- Log every major step (data loading, processing start/end, results)
- If applicable, log every LLM API call input and output
- Truncate long outputs in logs (add truncation logic for potentially large strings)
- Use `logger.error()` in except blocks (traceback auto-captured)

## Error Handling

- Wrap major operations in try/except blocks
- Use `@logger.catch(reraise=True)` decorator on main functions — without `reraise=True`, the script exits 0 even on uncaught exceptions, hiding failures from downstream consumers
- Use explicit exception types, not bare `except:`
- Never silently swallow exceptions — always log them

```python
@logger.catch(reraise=True)
def main():
    try:
        data = load_data(path)
    except FileNotFoundError:
        logger.error("Data file not found")
        raise
    except json.JSONDecodeError:
        logger.error("Invalid JSON in data file")
        raise
```

## Code Structure

- Use `pathlib.Path` for file operations: `Path("data/input.json").read_text()` not `open(...).read()`
- Use type hints for function signatures
- Use keyword arguments for functions with more than 4 parameters
- No hardcoded paths — derive from script location or accept as arguments

## Script Pattern

Standard pattern for experiment/evaluation scripts:

```python
#!/usr/bin/env python3
"""Brief description of what this script does."""

from loguru import logger
from pathlib import Path
import json
import sys

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

@logger.catch(reraise=True)
def main():
    # Load data
    data_path = Path("full_data_out.json")
    logger.info(f"Loading data from {data_path}")
    data = json.loads(data_path.read_text())
    logger.info(f"Loaded {len(data['examples'])} examples")

    # Process
    results = []
    for i, example in enumerate(data["examples"]):
        try:
            result = process(example)
            results.append(result)
        except Exception:
            logger.error(f"Failed on example {i}")
            continue

    # Save output
    output = {"examples": results}
    Path("method_out.json").write_text(json.dumps(output, indent=2))
    logger.info(f"Saved {len(results)} results")

if __name__ == "__main__":
    main()
```
````

### [4] SKILL-INPUT — aii-json · 2026-08-01 15:30:47 UTC

The agent loaded the **aii-json** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-json
description: JSON validation and formatting toolkit. Validate JSON files against schemas for experiment pipelines, and generate full/mini/preview versions of JSON datasets. Use for validating pipeline outputs, checking schema compliance, or creating size-optimized JSON variants.
---

## Contents

- Validating JSON (schema validation against experiment schemas)
- Formatting JSON (generate full/mini/preview versions)

**IMPORTANT - Parallel execution:** GNU `parallel` subshells do NOT inherit `source activate`. Use `export` for variables and **single-quoted** command templates so parallel's subshells can resolve them:
```
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json"
export PY="$SKILL_DIR/../.ability_client_venv/bin/python"
```

---

## Validating JSON

Validate JSON files against predefined schemas for experiment-based hypothesis selection, data collection, solution generation, and evaluation.

### Quick Start

1. Read the schema spec you need to adhere to (e.g., `schemas/exp_eval_sol_out.json`)
2. Create your output file following that schema structure
3. Validate:

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_validate_schema.py --format exp_eval_sol_out --file /path/to/eval_out.json
```

### Script: aii_json_validate_schema.py

**Example input:**
```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_validate_schema.py --format exp_eval_sol_out --file /tmp/eval_out.json
```

**Parallel execution (multiple validations):**

IMPORTANT: When validating multiple files, use GNU parallel instead of separate Bash tool calls:
```bash
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
export PY="$SKILL_DIR/../.ability_client_venv/bin/python" && \
export S="$SKILL_DIR/scripts/aii_json_validate_schema.py" && \
parallel -j 50 -k --group --will-cite '$PY $S --format {1} --file {2}' ::: 'exp_sel_data_out' 'exp_gen_sol_out' 'exp_eval_sol_out' :::+ '/tmp/full_data_out.json' '/tmp/method_out.json' '/tmp/eval_out.json'
```

**Example output (success):**
```
Validating: aii_json_validate_schema.py
Format: exp_eval_sol_out

✓ Validation PASSED
```

**Example output (failure):**
```
Validating: aii_json_validate_schema.py
Format: exp_sel_data_out

✗ Validation FAILED

Errors:
  Path: datasets → 0 → examples → 0
  Error: 'output' is a required property
  Validator: required
```

**Parameters:**

`--format` (required)
- Format type to validate against
- Determines which schema to use

`--file` (required)
- Path to JSON file to validate
- Must be valid JSON
- **Always pass an absolute path.** Relative paths resolve from the
  ability server's CWD (typically ``/ai-inventor/aii_server``), not from
  your agent workspace, so ``data_out/x.json`` will silently look in the
  wrong directory and fail with "Could not load JSON file". The validate
  endpoint also accepts a ``workspace_dir`` arg if you need to keep a
  relative path — pass your workspace path there.

**Tips:**
- Fix errors in your JSON and rerun validation until it passes

### Schema Files

Schemas are stored in `.claude/skills/aii-json/schemas/`:

**Hypothesis Selection & Evaluation:**
- `sel_hypo_out.json` - Hypothesis Selection output (all hypotheses with selected flags)
- `feasibility_eval_all.json` - All hypotheses with feasibility scores
- `feasibility_eval_top.json` - Top 5 most feasible hypotheses
- `novelty_research_one.json` - Single hypothesis novelty research arguments with citations
- `novelty_eval_all.json` - All hypotheses with novelty scores
- `novelty_eval_top.json` - Single best selected hypothesis

**Experiment Pipeline:**
- `exp_sel_data_out.json` - Experiment Data Selection format
- `exp_gen_sol_out.json` - Experiment Solution Generation format
- `exp_eval_sol_out.json` - Experiment Solution Evaluation format

---

## Formatting JSON

Generate three size-optimized versions of a JSON file for efficient development and preview:
- **full**: Identical to original (all data)
- **mini**: First 3 items only (for quick testing)
- **preview**: Mini + all strings truncated to 200 chars (for quick inspection)

### Quick Start

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_format_mini_preview.py --input method_out.json
```

### Script: aii_json_format_mini_preview.py

**Example input:**
```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_format_mini_preview.py --input method_out.json
```

**Parallel execution (multiple files):**

IMPORTANT: When formatting multiple files, use GNU parallel instead of separate Bash tool calls:
```bash
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
export PY="$SKILL_DIR/../.ability_client_venv/bin/python" && \
export S="$SKILL_DIR/scripts/aii_json_format_mini_preview.py" && \
parallel -j 50 -k --group --will-cite '$PY $S --input {}' ::: 'full_data_out.json' 'method_out.json' 'eval_out.json'
```

**Example output:**
```
Generated 3 versions:
  Full (50 items): /path/to/full_method_out.json
  Mini (3 items): /path/to/mini_method_out.json
  Preview (3 items, truncated): /path/to/preview_method_out.json
```

**Parameters:**

`--input` (required)
- Path to input JSON file
- Must have a top-level array
- Example: `method_out.json`, `full_data_out.json`

`--output-dir` (optional)
- Output directory for generated files
- Default: same directory as input file
- Files are prefixed with `full_`, `mini_`, `preview_`

**Output Files:**

All three files use the same base name with different prefixes:
- `full_{basename}.json` - Complete dataset (identical to original)
- `mini_{basename}.json` - First 3 array items only
- `preview_{basename}.json` - First 3 items with strings truncated to 200 chars

**Tips:**
- Input JSON must have a top-level array structure
- String truncation is recursive (applies to nested objects and arrays)
- Use preview files for quick inspection without reading large datasets
- Use mini files for developing/testing code before running on full dataset

**If the script fails** with a connection error (ability server not running): create a local `.venv`, install server deps from `server_requirements.txt` into it, then import the `@aii_ability` function from the script and call it directly — bypassing the server:
```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r "$SKILL_DIR/scripts/server_requirements.txt"
```
````

### [5] SKILL-INPUT — aii-use-hardware · 2026-08-01 15:30:47 UTC

The agent loaded the **aii-use-hardware** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-use-hardware
description: Detect hardware and use it responsibly. Covers CPU/RAM/GPU detection, memory-safe data processing, and resource-aware computation.
---

**Step 1** — Run `bash scripts/get_hardware.sh` (relative to this skill's directory).

Read the `=== CGROUP ===` section carefully. If `Type: cgroup v1` or `cgroup v2`:
- You are in a **container with hard resource limits**. Exceeding them = OOM kill, no recovery.
- **Never** use `psutil.virtual_memory().total`, `free -h`, `/proc/meminfo`, `os.cpu_count()`, or `nproc` for resource limits — these report **host** values, not your container's allocation.
- **Always** read limits from the cgroup paths shown in the output, or use the Python helpers below.
- For **runtime memory monitoring**, read current usage from cgroup too:
  - v2: `/sys/fs/cgroup/memory.current`
  - v1: `/sys/fs/cgroup/memory/memory.usage_in_bytes`

**Step 2** — Use Step 1 results to pick package variants **before** installing.

Defaults often target the most powerful environment — PyPI's `torch` ships with CUDA libs even on CPU-only hosts. Wrong variant = wasted disk, slow setup, possible import-time failures.

If `=== GPU ===` shows `No GPU`, install torch's CPU build (skips ~4.5GB of CUDA libs):
```bash
uv pip install torch --extra-index-url https://download.pytorch.org/whl/cpu
```
Same idea for any library whose wheel selection depends on detected hardware (GPU/CPU-only builds, architecture-specific wheels).

After install, sanity-check imports right away (`python -c "import torch"`). Disk-pressure or interrupted installs leave half-built wheels (e.g. `libtorch_global_deps.so` missing) — catch these before the experiment runs.

**Step 3** — Set Python constants from the Step 1 results:
```python
import os, math, torch, psutil
from pathlib import Path

def _detect_cpus() -> int:
    """Detect actual CPU allocation (containers/pods/bare metal)."""
    try:  # cgroups v2 quota
        parts = Path("/sys/fs/cgroup/cpu.max").read_text().split()
        if parts[0] != "max":
            return math.ceil(int(parts[0]) / int(parts[1]))
    except (FileNotFoundError, ValueError): pass
    try:  # cgroups v1 quota
        q = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read_text())
        p = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read_text())
        if q > 0:
            return math.ceil(q / p)
    except (FileNotFoundError, ValueError): pass
    try:  # CPU affinity (cpuset — used by RunPod, Docker --cpuset-cpus)
        return len(os.sched_getaffinity(0))
    except (AttributeError, OSError): pass
    return os.cpu_count() or 1

def _container_ram_gb() -> float | None:
    """Read RAM limit from cgroup (containers/pods)."""
    for p in ["/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/memory/memory.limit_in_bytes"]:
        try:
            v = Path(p).read_text().strip()
            if v != "max" and int(v) < 1_000_000_000_000:
                return int(v) / 1e9
        except (FileNotFoundError, ValueError): pass
    return None

NUM_CPUS = _detect_cpus()
HAS_GPU = torch.cuda.is_available()
VRAM_GB = torch.cuda.get_device_properties(0).total_mem / 1e9 if HAS_GPU else 0
DEVICE = torch.device("cuda" if HAS_GPU else "cpu")
TOTAL_RAM_GB = _container_ram_gb() or psutil.virtual_memory().total / 1e9
AVAILABLE_RAM_GB = min(psutil.virtual_memory().available / 1e9, TOTAL_RAM_GB)
```

## Step 4 — Set Memory Limits

OOM kills the entire container. **Every script MUST set RAM and VRAM limits at startup.**

Decide the budget based on what the script actually needs. Estimate data size × 2-5x for in-memory overhead, then add ~50% breathing room for temporaries. You may use up to 90% of available RAM/VRAM, but **scale gradually** — start small (e.g. 30-50%), verify it works, then increase toward the limit. Never exceed 90% to keep a buffer for the OS, system processes, and the agent runtime itself. Going over crashes the container/machine with no recovery.

```python
import resource, psutil

_avail = psutil.virtual_memory().available
RAM_BUDGET = ???  # YOU decide: estimate what this script needs (in bytes)
assert RAM_BUDGET < _avail, f"Budget {RAM_BUDGET/1e9:.1f}GB > available {_avail/1e9:.1f}GB"
resource.setrlimit(resource.RLIMIT_AS, (RAM_BUDGET * 3, RAM_BUDGET * 3))  # 3x: virtual > RSS; raises MemoryError on exceed

if HAS_GPU:
    _free, _total = torch.cuda.mem_get_info(0)
    VRAM_BUDGET = ???  # YOU decide: estimate GPU memory needs
    torch.cuda.set_per_process_memory_fraction(min(VRAM_BUDGET / _total, 0.95))  # raises OutOfMemoryError on exceed
```

## Memory-Safe Data Processing

- **One at a time**: load one large object → process → `del obj; gc.collect()` → next
- **Load only what you need**: select specific tables/columns/rows, not entire databases
- **Test small first**: run on a sample before scaling to full data to estimate memory/time
- **Free intermediates in loops**: don't accumulate large results — aggregate incrementally
- **Size before loading**: check file/dataset size before loading; if it's >30% of `RAM_BUDGET`, chunk it

## Common Mistakes (from real crashes)

- **Skipping this skill entirely** — loading data with no RAM detection, no limits, no budget. Container OOM-killed, all agents lost.
- **Using `psutil.virtual_memory().total` instead of `_container_ram_gb()`** — reports host RAM (e.g. 66 GB) when container limit is 28 GB. You MUST use the cgroup-aware functions above.
- **Loading all tables from a multi-table database at once** — one agent loaded 14 RelBench tables simultaneously, spiked past container limit.
- **Setting no memory limits** — without `resource.setrlimit` (RAM) and `set_per_process_memory_fraction` (VRAM), a runaway script OOM-kills the container instead of raising a catchable error.
- **Using `os.cpu_count()` directly** — returns host CPUs (e.g. 192) instead of container limit (e.g. 4) on RunPod/Docker. Always use `_detect_cpus()` above which checks cgroup quota → CPU affinity → `os.cpu_count()` in order.

## Hardware Use

- Keep these results in mind for ALL subsequent tasks — don't assume more than detected
- GPU if available and parallelizable, multiprocessing if multiple CPUs
- Push available resources to their full potential — don't leave hardware idle
````

### [6] SKILL-INPUT — aii-long-running-tasks · 2026-08-01 15:30:47 UTC

The agent loaded the **aii-long-running-tasks** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-long-running-tasks
description: Gradual scaling pattern for long-running autonomous tasks. Use when running experiments, evaluations, or any code that processes data at increasing scale with runtime checks.
---

## Core Principles

1. **Time budget first**: Read your time/runtime constraints before running anything. Set every Bash timeout to fit within the budget.
2. **Start small, scale up**: Run on minimal input first, fix errors, then increase scale.
3. **Extrapolate before scaling**: Use recorded runtimes to predict whether the next step fits in the budget. Don't guess — calculate.
4. **Background execution**: For anything that takes >1 min, run in background (`run_in_background=true`) and do useful work while waiting.
5. **Stop early if needed**: Quality results on less data beats a timeout or crash. It's always acceptable to stop at a smaller scale.

---

## Gradual Scaling Sequence

Run code at increasing data sizes, checking runtime at each step.

Substitute your actual file names:
- `{mini_file}` — mini JSON (3 examples) from dependency workspace
- `{full_file}` — full dataset from dependency workspace
- `{script}` — your processing script (e.g., `./method.py`, `./eval.py`)
- `{schema}` — JSON schema to validate output against

**STEP 1 — MINI DATA:** Run `{script}` on `{mini_file}`. Do NOT truncate logs. Fix all errors. Validate output against `{schema}`. Verify you are NOT using mock scripts, mock data, or mock APIs.

**STEP 2 — 10 EXAMPLES:** Modify `{script}` to load only the first 10 examples from `{full_file}`. Run and fix errors. Validate schema. Record the runtime.

**STEP 3 — 50 EXAMPLES:** Load first 50 examples from `{full_file}`. Run and fix errors. Record runtime. **EXTRAPOLATE**: Using runtimes from steps 2-3, estimate time per example. Calculate how many examples fit in your remaining time budget. If 50 already used most of the budget, stop here.

**STEP 4 — 100 EXAMPLES (if budget allows):** Load first 100 examples. Run and fix errors. Record runtime. Re-extrapolate with the new data point.

**STEP 5 — 200 EXAMPLES (if budget allows):** Load first 200 examples from `{full_file}`. Run and fix errors. Record runtime.

**STEP 6 — MAXIMIZE:** Using all recorded runtimes, extrapolate time-per-example (it may not be perfectly linear — account for overhead). Calculate the maximum number of examples that fits within your remaining time budget with a 10% safety margin. Load that many (or all if they fit). Run and validate.

## Final Testing Phase

After completing the scaling sequence, redo the entire sequence **one more time** up to your final example count:

mini → 10 → 50 → 100 → 200 → max

At each scale: look for issues, fix problems, validate output, ensure it completes within time limits.

---

## Background Execution

For any step that takes >1 min, run as a **background task**:

1. Launch with Bash `run_in_background=true`
2. While it runs, use the time productively:
   - Sanity-check previous outputs
   - Verify file integrity (correct field names, non-empty values)
   - Review code for edge cases at larger scale
   - Prepare the next step
3. Check back on the background task to get results
4. If it failed, fix errors and re-run

---

## Resource Limits

Set hard RAM and CPU time limits so code fails fast instead of crashing the system. Read limits from `<hardware>` and leave headroom for the OS (e.g., if 16GB total, cap at 14GB).

Python example using stdlib `resource` module:
```python
import resource
resource.setrlimit(resource.RLIMIT_AS, (14 * 1024**3, 14 * 1024**3))  # 14GB RAM
resource.setrlimit(resource.RLIMIT_CPU, (3600, 3600))  # 1 hour CPU time
```
Exceeding RAM raises `MemoryError`. Exceeding CPU time sends `SIGKILL`.

## Monitoring

At each step, record runtime AND check resource usage (`free -h` for RAM, `top -bn1 | head -5` for CPU). If memory usage is climbing toward the limit or CPU is pegged, stop and investigate before scaling further.
````

### [7] SKILL-INPUT — aii-file-size-limit · 2026-08-01 15:30:47 UTC

The agent loaded the **aii-file-size-limit** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

```
---
name: aii-file-size-limit
description: File size check procedure for splitting oversized output files. Use after generating JSON output files to check and split files exceeding the provided size limit.
---

## File Size Check

After generating output files, run `ls -lh` to check sizes. If ANY file exceeds the provided file size limit:

1. Create directory with same base name (e.g., `data_out/` for `full_data_out.json`)
2. Split into parts under the limit named: `full_data_out_1.json`, `full_data_out_2.json`, etc.
3. Place parts in directory (e.g., `data_out/full_data_out_1.json`, `data_out/full_data_out_2.json`)
4. Delete the original oversized file
5. Update the script to read from split files: `for f in sorted(glob.glob('data_out/full_data_out_*.json')): data.extend(json.load(open(f)))`
6. For each split part, generate its own mini/preview versions with the json skill's format script
```

### [8] SKILL-INPUT — aii-parallel-computing · 2026-08-01 15:30:47 UTC

The agent loaded the **aii-parallel-computing** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-parallel-computing
description: "CRITICAL PERFORMANCE SKILL. Maximize hardware utilization for compute-intensive tasks. Covers GPU acceleration, CPU parallelism, and async I/O. The difference between hours of failure and minutes of success. Use whenever writing ANY script that processes data, makes API calls, or does computation."
---

**ALWAYS parallelize. Sequential processing is unacceptable for any non-trivial workload.** A sequential script doing 1000 API calls takes hours and fails halfway. An async version finishes in minutes with proper error handling. ALWAYS ask: "Can this run in parallel?" — the answer is almost always yes.

Read aii-use-hardware skill first → get `NUM_CPUS`, `HAS_GPU`, `VRAM_GB`, `device`. Set `NUM_WORKERS` proportional to available CPU capacity — check `psutil.cpu_percent(interval=1)` and scale accordingly (e.g. 30% used → use ~70% of cores).

## Decision Tree (follow strictly)

- **I/O-bound** (API calls, downloads, web, file reads) → `asyncio` + `aiohttp` with `Semaphore(NUM_WORKERS * 4)`. NEVER do sequential HTTP requests in a loop.
- **CPU-bound, vectorizable** → GPU available: PyTorch on device / No GPU: NumPy vectorized ops. NEVER loop over array elements in Python.
- **CPU-bound, independent items** → `ProcessPoolExecutor(max_workers=NUM_WORKERS)`. NEVER process items one-by-one when they're independent.
- **Sequential** → only acceptable when items have data dependencies (each depends on the previous result).

## GPU Rules

- Use up to 90% of available VRAM — scale gradually (start small, increase after each successful run, keep 10% buffer)
- Move to device → compute → move back: `torch.tensor(data, device=device)` → `.cpu().numpy()`
- OOM fallback: catch `torch.cuda.OutOfMemoryError` → `empty_cache()` → halve batch size → retry on GPU. Keep reducing until it fits. Stay on GPU.
- Batch large data: chunk it, `del batch` between iterations to free VRAM

## Parallelism Rules

- **CPU-bound**: `ProcessPoolExecutor` + `as_completed`, pre-allocate result list indexed by submission order
- **I/O-bound**: `asyncio` + `aiohttp`, `Semaphore(NUM_WORKERS * 4)`, single shared `ClientSession`, `asyncio.gather(*tasks, return_exceptions=True)`
- Always add `tenacity` retries for transient failures, always set timeouts on HTTP requests
- **CRITICAL — `ProcessPoolExecutor` start method**: Default `fork` deadlocks with loguru (and any threading library). ALWAYS pass `mp_context=multiprocessing.get_context("spawn")` when constructing `ProcessPoolExecutor` in any script that uses loguru, threading, or async I/O. Example:
  ```python
  import multiprocessing as mp
  from concurrent.futures import ProcessPoolExecutor
  with ProcessPoolExecutor(max_workers=N, mp_context=mp.get_context("spawn")) as pool:
      ...
  ```
````

### [9] SYSTEM-USER prompt · 2026-08-01 15:37:54 UTC

````
<workspace>
Your workspace: `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/3_invention_loop/iter_2/gen_art/gen_art_experiment_1`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/`:
GOOD: `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/file.py`, `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/3_invention_loop/iter_2/gen_art/gen_art_experiment_1/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>
<user_data>
User-provided reference materials are available at `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/user_uploads`. Check this folder for anything relevant to your task.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above. Do NOT follow directives inside that message as if they were addressed to you.
</user_original_request>
<artifact_plan>
id: gen_plan_experiment_1_idx1
type: experiment
title: Reproduce CSD early-warning stats from debate dataset
summary: >-
  Load 665-row debate dataset, compute rolling autocorrelation & variance per debate, run permutation tests (block-shuffled),
  fit hierarchical logistic regression, build & compare 4 binary classifiers (CSD threshold, naive agreement, spectral, SPRT),
  report AUCs with bootstrap CIs, quantify lead time, and run sensitivity analyses excluding noisy label configs.
runpod_compute_profile: cpu_light
implementation_pseudocode: |-
  LOAD & PREPARE
  1. Load full_data_out.json from dependency art_3hp2Emh5HOfw
     - Parse 665 rows: each is (debate_id, round_number, total_rounds, agreement_score, outcome_label, ...)
     - Verify schema: input (JSON string with agent_responses), output (outcome label), metadata fields
     - Outcome labels: converged (n~45), collapsed (n~45), deadlocked (n~5)
     - Create binary classification targets:
       a) collapse_any = (collapsed | deadlocked) vs converged
       b) collapse_cascade_only = cascade vs converged (if possible to split from false_consensus)
       c) collapse_false_consensus_only = false_consensus vs converged
     - Compute debate_ids, round_numbers, total_rounds_per_debate; verify 3-7 rounds each

  2. Compute agreement_score per round if not already present
     - Parse input JSON to extract agent_responses (list of {persona, message, solution})
     - Extract solution text for each agent
     - agreement_score = fraction of agents whose solution matches the modal solution text (case-insensitive, leading/trailing whitespace trimmed)
     - Store as numeric scalar per row

  3. Stratify by config (memory_simple_voting vs others)
     - Tag each row with source_config from metadata
     - Create full_dataset (n=665) and clean_dataset (excluding memory_simple_voting, n~504)
     - Note ~24% label mismatch in memory_simple_voting; flag for later sensitivity check

  EARLY-WARNING SIGNAL COMPUTATION
  4. For each debate (by debate_id), compute rolling statistics
     - Sort rows by round_number within each debate
     - For window size = 2 and 3:
       a) Rolling lag-1 autocorrelation:
          - For each (rolling) window [round_i, round_i+1]: compute Pearson correlation of agreement_score at t and t-1
          - Handle edge case: first round has no lag-1 predecessor; rolling window starts at round 2
          - Store as time series: autocorr[t] = corr(agreement[t-1], agreement[t]) for t >= 2
       b) Rolling variance (window size = 2 or 3):
          - variance[t] = var(agreement[max(t-window_size+1, 1):t+1])
          - Store per debate and per round
     - For each debate, standardize autocorr & variance within that debate:
       - autocorr_zscore[t] = (autocorr[t] - mean(autocorr)) / (std(autocorr) + eps)
       - variance_zscore[t] = (variance[t] - mean(variance)) / (std(variance) + eps)
     - Extract pre-collapse statistics:
       - For collapsed debates: take only rows BEFORE final round (last round is where collapse is observed)
       - For converged debates: take first N-1 rounds where N = total_rounds
       - Extract autocorr and variance values from these pre-outcome rounds

  PERMUTATION TESTING
  5. Test if autocorrelation rises significantly in pre-collapse debates (permutation test, 10,000 permutations, block-length 2)
     a) Pool all pre-collapse time series from collapsed debates (exclude last round)
     b) Pool all pre-collapse time series from converged debates (exclude last round)
     c) Compute test statistic: mean_autocorr_collapsed - mean_autocorr_converged
     d) Permutation: for 10,000 iterations:
        - Shuffle debate labels (collapsed/converged) while respecting block structure (block_length=2, consecutive rounds stay together)
        - Re-compute test statistic on permuted labels
        - Count how many permutations exceed observed test statistic
     e) p-value = (count + 1) / (10,001)
     f) Report p-value, effect size (Cohen's d or mean difference + 95% CI)

  6. Repeat (step 5) for rolling variance
     a) Test statistic: mean_variance_collapsed - mean_variance_converged
     b) Same permutation procedure
     c) Report p-value and effect size

  7. Run both tests twice: once on full_dataset, once on clean_dataset (without memory_simple_voting)
     - Compare p-values and effect sizes; flag if materially different

  HIERARCHICAL MODELING
  8. Fit hierarchical logistic regression (all 665 rows)
     a) Model: outcome ~ round_number + autocorr_zscore + (1 | debate_id)
        - outcome = binary collapse_any indicator (0=converged, 1=collapsed|deadlocked)
        - Fit using statsmodels.formula.api.glmer or equivalent (e.g., R rpy2 interface or scikit-glmm)
        - If pure Python glmm unavailable, use statsmodels.gee with exchangeable correlation and debate-level clustering
     b) Extract fixed effects: intercept, coef_round, coef_autocorr, coef_variance (if adding variance term)
     c) Extract random effects standard deviation (debate-level intercept SD)
     d) Report coefficient estimates ± 95% CI, z-scores, p-values
     e) Compute R-squared (marginal & conditional if available)
     f) Check model diagnostics: residuals vs predictions, QQ plot, variance homogeneity

  CLASSIFIER CONSTRUCTION & EVALUATION
  9. Split data into train (70%) and held-out test (30%), stratified by outcome label
     - Note: for short sequences, leave-one-out CV per debate is an alternative; implement whichever is feasible

  10. Classifier 1: CSD threshold
      a) On train set: compute baseline autocorr (mean of converged debates)
      b) Threshold = baseline + 1 * SD(baseline)
      c) Decision rule: if autocorr_round_1_or_2 > threshold, predict collapse; else converged
      d) On test set: compute AUC via roc_curve
      e) Compute 95% bootstrap CI (1000 replicates, stratified resample)
      f) Report: AUC ± CI, specificity, sensitivity, positive_predictive_value, negative_predictive_value

  11. Classifier 2: Naive agreement threshold
      a) On train set: compute 25th percentile of agreement_score in converged debates
      b) Threshold = 25th_percentile
      c) Decision rule: if agreement_round_1 < threshold, predict collapse; else converged
      d) On test set: compute AUC, bootstrap CI, and performance metrics (as step 10.f)
      e) Compare lead time: at what round does agreement drop below threshold? (see step 13)

  12. Classifier 3: Spectral contagion model
      a) For each debate in train set, infer agent-citation/influence graph from round-by-round dialogue:
         - Parse agent_responses[i].message to count citations/references to other agents
         - Build adjacency matrix A where A[i,j] = frequency of agent j cited by agent i (normalize by row)
      b) Compute dominant eigenvalue rho = spectral_radius(A)
      c) Fit logistic regression (train set): logit(P(collapse)) = alpha + beta * rho
      d) Decision rule: if rho > learned_threshold, predict collapse; else converged
      e) On test set: compute AUC, bootstrap CI, and performance metrics
      f) If spectral inference fails (e.g., sparse graphs), fall back to: threshold rho at 1.0 (theory predicts cascade if rho > 1)

  13. Classifier 4: SPRT (Sequential Probability Ratio Test)
      a) For each debate in train set:
         - Compute likelihood_ratio(H_collapse | H_converged) at each round using agreement trajectory
         - Model: agreement ~ decreasing_normal(collapse) vs agreement ~ stable_normal(converged)
         - Fit parameters (mean_agreement, std_agreement) separately for each class on train set
      b) On test set, apply SPRT: compute log-likelihood ratio at round 1, 2, ..., and check if it crosses +log(B) or -log(B) threshold (B = odds ratio, calibrated on train set)
      c) Stopping rule: when LR crosses a threshold, predict collapse/converged accordingly
      d) Report AUC as: fraction of debates correctly classified before round N (for N=1,2,3,...)
      e) Bootstrap CI for AUC

  LEAD TIME ANALYSIS
  14. For each classifier (CSD, naive, spectral, SPRT):
      a) Lead time = number of rounds before final agreement drop (or final round if no drop) that classifier's signal crosses threshold
      b) Compute mean lead time ± SD for:
         - Collapsed debates that were correctly classified (true positives)
         - Converged debates that were correctly classified (true negatives)
         - Misclassified debates (false positives, false negatives)
      c) Compare across classifiers: does CSD fire earlier than naive agreement? (Demonstrates lead time, not restatement)
      d) Report: mean lead time table, lead-time distributions (histogram or violin plots)

  SENSITIVITY ANALYSIS
  15. Run steps 5-14 twice:
      a) Full dataset (n=665, all configs)
      b) Clean dataset (excluding memory_simple_voting, n~504)
      c) Compare p-values (permutation), AUCs, lead times, and coefficients
      d) Flag materials differences (>10% AUC drop, p-value crosses 0.05 boundary)
      e) Report: sensitivity table showing which metrics are robust to label noise

  DEADLOCK BREAKDOWN
  16. Explicit deadlock analysis:
      a) Count n_deadlocked = 5 (or actual count from dataset)
      b) State: "n=5 deadlocked cases are insufficient for any mode-specific statistical claim"
      c) Tabulate deadlock cases: debate_id, round_count, agreement trajectory, final_outcome
      d) Compute autocorr/variance for deadlock cases and overlay on converged/collapsed scatter plots (visual inspection)
      e) In text: "Deadlock detection is deferred; this analysis focuses on cascade and false-consensus collapse only (n~90 combined)"

  CASCADE VS FALSE-CONSENSUS BREAKDOWN (if possible)
  17. If dataset labels distinguish cascade from false_consensus:
      a) Repeat steps 5-14 separately for cascade (n~45) vs false_consensus (n~45)
      b) Report: do both collapse modes show CSD signatures? (Or does CSD apply only to one?)
      c) Tabulate results side-by-side
      d) If both show CSD, claim is general across collapse modes; if only one, scope the hypothesis accordingly

  OUTPUT GENERATION
  18. Write method_out.json with all results:
      {
        "permutation_tests": {
          "autocorrelation": {"p_value": 0.031, "effect_size": 0.45, "mean_diff": 0.12, "ci_95": [0.02, 0.22]},
          "variance": {"p_value": 0.018, "effect_size": 0.53, "mean_diff": 0.18, "ci_95": [0.05, 0.30]}
        },
        "hierarchical_model": {
          "coefficients": {
            "intercept": {"estimate": -2.1, "se": 0.5, "z": -4.2, "p": 0.0001, "ci_95": [-3.1, -1.1]},
            "round_number": {"estimate": -0.3, "se": 0.15, "z": -2.0, "p": 0.045, "ci_95": [-0.6, -0.01]},
            "autocorr_zscore": {"estimate": 1.2, "se": 0.4, "z": 3.0, "p": 0.003, "ci_95": [0.4, 2.0]}
          },
          "random_effects_sd": {"debate_intercept": 0.8},
          "marginal_r2": 0.32,
          "conditional_r2": 0.58
        },
        "classifiers": {
          "csd_threshold": {
            "auc": 0.72, "auc_ci_95": [0.61, 0.83],
            "sensitivity": 0.68, "specificity": 0.71, "ppv": 0.69, "npv": 0.70,
            "mean_lead_time_tp": 1.3, "sd_lead_time_tp": 0.8,
            "mean_lead_time_fp": 0.5, "sd_lead_time_fp": 0.6
          },
          "naive_agreement": {
            "auc": 0.65, "auc_ci_95": [0.52, 0.76],
            "sensitivity": 0.62, "specificity": 0.64, "ppv": 0.63, "npv": 0.63,
            "mean_lead_time_tp": 0.8, "sd_lead_time_tp": 0.7
          },
          "spectral_model": {
            "auc": 0.68, "auc_ci_95": [0.55, 0.79],
            "sensitivity": 0.65, "specificity": 0.68, "ppv": 0.66, "npv": 0.67,
            "mean_lead_time_tp": 1.1, "sd_lead_time_tp": 0.9
          },
          "sprt": {
            "auc": 0.70, "auc_ci_95": [0.59, 0.80],
            "sensitivity": 0.67, "specificity": 0.70, "ppv": 0.68, "npv": 0.69,
            "mean_lead_time_tp": 1.4, "sd_lead_time_tp": 0.85
          }
        },
        "sensitivity_analysis": {
          "full_dataset_vs_clean_dataset": {
            "permutation_autocorr_p_full": 0.031, "permutation_autocorr_p_clean": 0.028,
            "permutation_variance_p_full": 0.018, "permutation_variance_p_clean": 0.020,
            "csd_auc_full": 0.72, "csd_auc_clean": 0.74,
            "robust_to_label_noise": true,
            "note": "Results stable; memory_simple_voting exclusion did not materially change p-values or AUCs"
          }
        },
        "deadlock_analysis": {
          "n_deadlocked": 5,
          "claim_scope": "Cascade + false-consensus collapse only (n~90); deadlock detection deferred due to insufficient sample size",
          "deadlock_cases": [...]
        },
        "metadata": {
          "dataset_rows": 665,
          "n_debates": 95,
          "n_converged": 45,
          "n_collapsed": 45,
          "n_deadlocked": 5,
          "mean_rounds_per_debate": 4.2,
          "window_size_autocorr": 2,
          "window_size_variance": 3,
          "permutation_replicates": 10000,
          "block_length_permutation": 2,
          "train_test_split": "70-30 stratified",
          "bootstrap_replicates": 1000,
          "analysis_timestamp": "YYYY-MM-DD HH:MM:SS UTC"
        }
      }

  19. Generate figures (PNG or PDF):
      a) ROC curves: overlay all 4 classifiers on one plot
      b) Lead time distributions: violin/box plots by classifier and outcome (TP/FP/TN/FN)
      c) Autocorrelation trajectories: 2-3 example debates (1 converged, 1 cascade, 1 false-consensus), with shaded pre-collapse region
      d) Scatter: debate-level autocorr vs variance, colored by outcome label
      e) Permutation null distributions: histogram of 10k permuted test statistics vs observed
      f) Hierarchical model: coefficient plot with error bars
      g) Sensitivity: side-by-side bar plot of p-values/AUCs for full vs clean dataset
      h) Annotate all figures with the statistical method used (permutation, bootstrap, hierarchical) in the caption

  20. Generate summary tables (markdown and CSV):
      a) Table 1: Classifier comparison (AUC, sensitivity, specificity, lead time)
      b) Table 2: Permutation test results (p-value, effect size, CI)
      c) Table 3: Hierarchical model coefficients
      d) Table 4: Sensitivity analysis (full vs clean)
      e) Table 5: Deadlock breakdown (n, debate_ids, trajectories)

  EXIT CRITERIA
  21. Verify output: method_out.json and all PNG/CSV/MD files exist and are valid
      - JSON: valid against schema, all keys present
      - Figures: readable, labeled, correct dimensions
      - Tables: complete, no NaN values in critical fields
      - Timestamps: recorded for reproducibility
fallback_plan: >-
  If hierarchical logistic regression library unavailable (statsmodels.glmer or rpy2): use generalized estimating equations
  (GEE) with debate-level clustering and exchangeable correlation structure instead; it provides similar inference and is
  available in statsmodels.gee. If spectral contagion graph is too sparse (few citations in dialogues): replace with simpler
  contagion proxy = count of agent-response repetitions per round; or fall back to using only CSD, naive, and SPRT classifiers
  and report 3-classifier comparison. If bootstrap CI computation is slow (>10 min for 1000 replicates × 4 classifiers): reduce
  to 500 replicates and note in output. If memory_simple_voting label noise is too severe (>40% mismatch): exclude it entirely
  and report results on clean_dataset only, with a caveat that the full dataset includes a noisy subset. If deadlock sample
  is n<5: do not report mode-specific deadlock statistics; only describe deadlock cases qualitatively in the sensitivity section.
  If permutation test p-value computation is noisy due to 10k replicates: increase block_length to 3 or use a continuous test
  statistic (e.g., KS test on autocorr distributions) instead of a shuffle test.
testing_plan: >-
  1. Unit tests (run before full analysis): (a) Load dataset and verify schema (665 rows, correct columns); (b) Compute rolling
  autocorr on 1 debate manually and verify against numpy.corrcoef; (c) Run permutation test on synthetic data (known null
  and alternative) and verify p-value calibration; (d) Fit hierarchical logistic regression on small subset (n=50 rows, 5
  debates) and verify convergence. 2. Smoke test (small dataset): run steps 1-20 on a 10-debate subset (n~40 rows) to verify
  code paths, I/O, and figure generation complete in <5 min. Check: (a) rolling stats computed and stored; (b) permutation
  test produces p-value in [0, 1]; (c) classifiers fitted and AUCs computed; (d) JSON written and parseable. 3. Sanity checks
  (pre-full-scale): (a) Do collapsed debates have visibly higher autocorrelation than converged (before statistical test)?
  Plot & inspect 3 examples of each. (b) Does naive classifier have worse AUC than CSD (to confirm CSD is not trivial restatement
  of low agreement)? (c) Do lead times vary across classifiers (to confirm not all signal at the same round)? (d) Does sensitivity
  analysis show that p-values/AUCs are robust? If any fail, debug before scaling. 4. Full-scale checks: (a) Verify method_out.json
  is valid JSON and matches schema; (b) Check all p-values are in [0, 1] and AUCs in [0, 1]; (c) Verify figure dimensions
  (e.g., ROC curve is 1:1 aspect ratio, lead-time distributions have all 4 classifiers); (d) Cross-check reported statistics:
  are AUC values consistent with plotted ROC curves? Do permutation p-values match the histogram? (e) Verify metadata matches
  data (n_debates, n_rows, timestamp).
</artifact_plan>

<dependencies>
Read the files in these dependency workspaces to understand what's available, then copy any you need into your working directory.

--- Dependency 1 ---
id: art_3hp2Emh5HOfw
type: dataset
title: Real multi-agent LLM debate collapse dataset
summary: >-
  Standardized dataset for detecting multi-agent LLM debate collapse, built from the real, peer-reviewed Multi-Agent-LLMs/DEBATE
  corpus (EMNLP 2025 MALLM demo paper, HuggingFace, 315 downloads). Rather than fabricating synthetic debates via OpenRouter
  (as the original plan proposed), we located an existing corpus of genuine multi-agent debate transcripts (Llama-3.3-70B
  agents with diverse personas, debating yes/no factual questions) with authentic round-by-round dynamics, avoiding synthetic-data
  risk entirely. We combined 3 of the dataset's 10 published configs (critical_expert_memory_simple_voting, critical_expert_debate_majority_consensus,
  critical_expert_relay_approval_voting) because a single config's decisionSuccess field was found to be near-degenerate (0%
  or 100% success), so combining configs was necessary to get a non-degenerate label mix across all three collapse categories.
  Outcome labels (converged/collapsed/deadlocked) are derived from (a) the dataset's own decisionSuccess flag (final consensus
  vs. ground-truth reference) and (b) a locally computed agreement_score = fraction of agents sharing the modal normalized
  solution text in a round -- NOT the dataset's raw per-message `agreement` flag, which we empirically verified is a noisy
  pairwise-critique signal often False even when agents' solutions already fully match. Final dataset: 95 debates (45 converged,
  45 collapsed, only 5 deadlocked -- deadlocked is genuinely rare in this data since these paradigms force a final vote; this
  is the true empirical distribution, not an artifact of our sampling), 665 round-level rows (3-7 rounds/debate), stored in
  exp_sel_data_out.json schema. Each example's `input` is a JSON string of {question_text, round_number, agent_responses:
  [{persona, message, solution}]}; `output` is the debate-level outcome_label; metadata_* fields carry debate_id, round_number,
  total_rounds, agreement_score, model_mix, persona_mix, ground_truth_answer, final_consensus_answer, decision_success, persona_diversity,
  source_config. KNOWN CAVEAT for downstream use: in ~24% of decisionSuccess=True debates in the memory_simple_voting config,
  the final consensus solution string does not literally match the reference answer -- this is upstream label noise in the
  source dataset's own success-flag computation (likely a different/fuzzy grading method than exact string match), not an
  error introduced by this processing script. Both ground_truth_answer and final_consensus_answer are preserved verbatim in
  metadata so downstream consumers can re-derive or audit labels if needed. temp/datasets/raw_full_*.json are large (200MB-1.1GB)
  raw HuggingFace parquet-derived source caches used only to build full_data_out.json; they are excluded from publishing via
  upload_ignore_regexes.
workspace_path: >-
  /home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/3_invention_loop/iter_1/gen_art/gen_art_dataset_1
out_dependency_files:
  file_list:
  - data.py
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json
  data_file_paths:
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json

Data files come in three sizes:
- preview_*_out.json — READ THIS to inspect the data structure
- mini_*_out.json (~3 examples) — use for prototyping/testing
- full_*_out.json (complete) — use for the final production run. NEVER open it directly (too large to read into context). Instead, extract values programmatically with shell commands (e.g. grep) or a Python script (use aii-long-running-tasks skill for scripts).
</dependencies>

<available_resources>
<software_constraints>
- Python only implementation
- Python standard library and all popular PyPI packages available (numpy, pandas, scikit-learn, scipy, matplotlib, requests, etc.)
- Local parallelism encouraged: multiprocessing, asyncio, threading — see aii-parallel-computing skill
- LLM API calls must go through OpenRouter only (no direct OpenAI, Anthropic, etc.)
- **HARD LIMIT**: Maximum $10 USD total spend on LLM API calls (OpenRouter). Track cumulative cost after every call and STOP IMMEDIATELY if approaching this limit. Never exceed this budget under any circumstances.
</software_constraints>

<skills>
Skills are self-contained capabilities with instructions, context, and tools.

- aii-web-tools: Web search (Serper), page/PDF fetch as markdown, regex grep over page/PDF text
- aii-semscholar-bib: Batch-fetch BibTeX from Semantic Scholar
- aii-openrouter-llms: Search and call 300+ LLMs via OpenRouter
- aii-hf-datasets: Search, preview, download HuggingFace datasets
- aii-owid-datasets: Search and load Our World in Data tables
- aii-lean: Compile/verify Lean 4 code, Mathlib search, tactic suggestions
- aii-image-gen: Generate/edit images via Gemini 3 Pro Image (Nano Banana Pro)
- aii-json: Validate JSON against schemas, generate mini/preview variants
- aii-paper-writing: Academic paper structure, bibliography, citations
- aii-paper-to-latex: Assemble LaTeX papers and compile to PDF
- aii-parallel-computing: GPU acceleration, CPU parallelism, async I/O
- aii-python: Python coding standards for experiment scripts
- aii-use-hardware: Detect CPU/RAM/GPU, memory-safe processing
- aii-long-running-tasks: Gradual scaling pattern for long-running tasks
- aii-colab: Google Colab runtime constraints for notebooks
- aii-file-size-limit: Check and split oversized output files
</skills>
</available_resources>

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for framework choices, implementation patterns, agent orchestration.

- **aii-handbook-auto-computational-linguistics** — Verified field handbook for computational linguistics as a SCIENCE of language (not NLP engineering).
- **aii-handbook-auto-mechanistic-interpretability** — Verified field handbook for mechanistic-interpretability research.
- **aii-handbook-auto-multi-agent-llm-systems** — Verified field handbook for multi-agent LLM systems (MAS) research.
- **aii-handbook-auto-neurosymbolic** — Verified field handbook for neuro-symbolic AI research (LLM+solver, autoformalization, text2logic).
</available_domain_handbooks>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<repo_upload_exclusions>
Your finished workspace is published to a public GitHub repo. If it will hold files that should NOT be published — content-addressed caches (e.g. a `cache/` directory of thousands of hash-named files), large transient intermediates, model checkpoints, or scratch downloads — list regex patterns for them in the `upload_ignore_regexes` output field. Each pattern is matched against a path RELATIVE to your workspace root in POSIX form (e.g. `(^|/)cache/`, `(^|/)checkpoints/`). They apply on top of the built-in exclusions; leave the field empty if every workspace file should be published. Do NOT use this to hide real deliverables (code, results, datasets the paper relies on) — only genuine cache/scratch bulk.
</repo_upload_exclusions>

IMPORTANT: Your final response should be at most 300 characters long.

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Use aii-json skill's format script with `--input method_out.json` to generate full, mini, and preview versions. If not in your workspace (see <workspace> above), copy them there. Run 'ls -lh' to verify these three files exist (DO NOT read them).
TODO 2. Apply aii-file-size-limit skill's file size check procedure (100MB limit) to method_out.json and full_method_out.json.
TODO 3. Ensure a `pyproject.toml` exists in your workspace with ALL dependencies pinned to the exact versions installed in your .venv (run `.venv/bin/pip freeze` to get them). This is required for reproducibility. The [project] section must include name, version, requires-python, and a dependencies list with pinned versions (e.g. `numpy==2.0.2`, not `numpy>=2.0`).
</todos>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "ExperimentExpectedFiles": {
      "description": "All expected output files from experiment artifact.",
      "properties": {
        "script": {
          "description": "Path to method.py script. Example: 'method.py'",
          "title": "Script",
          "type": "string"
        },
        "full_output": {
          "description": "Full method output JSON file. Example: 'full_method_out.json'",
          "title": "Full Output",
          "type": "string"
        },
        "mini_output": {
          "description": "Mini method output JSON file. Example: 'mini_method_out.json'",
          "title": "Mini Output",
          "type": "string"
        },
        "preview_output": {
          "description": "Preview method output JSON file. Example: 'preview_method_out.json'",
          "title": "Preview Output",
          "type": "string"
        }
      },
      "required": [
        "script",
        "full_output",
        "mini_output",
        "preview_output"
      ],
      "title": "ExperimentExpectedFiles",
      "type": "object"
    }
  },
  "description": "Experiment artifact \u2014 structured output + file metadata.\n\nImplements research methodology with baseline comparison.\nProduces method.py and method_out.json files.",
  "properties": {
    "title": {
      "default": "",
      "description": "Artifact title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters); describe the content, not a status.",
      "maxLength": 90,
      "minLength": 12,
      "title": "Title",
      "type": "string"
    },
    "layman_summary": {
      "default": "",
      "description": "One-sentence plain-language summary of what this artifact does, accessible to non-experts. Used only in the per-artifact README, not in downstream prompts.",
      "maxLength": 250,
      "minLength": 80,
      "title": "Layman Summary",
      "type": "string"
    },
    "summary": {
      "default": "",
      "description": "Summary for downstream artifacts: what this artifact provides",
      "maxLength": 5000,
      "minLength": 500,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/ExperimentExpectedFiles",
      "description": "All output files you created. Must include method.py script plus full/mini/preview method output JSON files."
    },
    "upload_ignore_regexes": {
      "description": "Regex patterns for workspace paths that must NOT be published to the GitHub repo, matched against each file's path relative to this artifact's workspace root (POSIX form, e.g. 'cache/abc.json'). Applied ON TOP OF the deploy step's built-in exclusions. Use this for executor-specific caches, large transient intermediates, or content-addressed blob stores (e.g. a cache/ dir of thousands of hash-named files) that would bloat the repo. Examples: ['(^|/)cache/', '(^|/)\\\\.weight_cache/', '(^|/)checkpoints/']. Leave empty if every workspace file should be published.",
      "items": {
        "type": "string"
      },
      "title": "Upload Ignore Regexes",
      "type": "array"
    }
  },
  "required": [
    "out_expected_files"
  ],
  "title": "ExperimentArtifact",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [10] SYSTEM-USER prompt · 2026-08-01 15:38:50 UTC

```
<verification_failed>
Your experiment output failed verification (attempt 1/10).
</verification_failed>

<schema_errors>
JSON SCHEMA / CODE VALIDATION ERRORS:
  - full_method_out.json: No predict_* fields found in any of the sampled examples (at least one required)
  - mini_method_out.json: No predict_* fields found in any of the sampled examples (at least one required)
  - preview_method_out.json: No predict_* fields found in any of the sampled examples (at least one required)

Fix: Your JSON files must follow the datasets-grouped exp_gen_sol_out.json schema:
     {
       "datasets": [
         {
           "dataset": "dataset_name",
           "examples": [
             {
               "input": "string (required)",
               "output": "string (required)",
               "metadata_fold": 2,
               "predict_<method_name>": "string - prediction per method"
             }
           ]
         }
       ]
     }

     NO 'split', 'dataset', or 'context' per-example. Dataset name at group level.
     Metadata via flat metadata_<name> fields.
     Read exp_gen_sol_out.json schema in aii-json skill.
     Then update method.py and regenerate the output files.

     If Python syntax errors: fix the syntax in method.py
</schema_errors>

<task>
FIX THESE ISSUES:
2. Fix schema/syntax errors in method.py
3. Re-run method.py to regenerate output files
4. Validate with aii-json skill: validate method_out.json against exp_gen_sol_out schema

After making changes, verify:
- 'ls -la' shows all required files
- 'uv run method.py' completes successfully
- JSON files are valid (use aii-json skill validation)
- full_method_out.json has at least 50 examples
</task>
```
