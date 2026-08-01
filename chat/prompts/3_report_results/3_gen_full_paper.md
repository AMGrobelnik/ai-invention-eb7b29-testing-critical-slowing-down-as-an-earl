# gen_full_paper — report_results

> Phase: `gen_paper_repo` · `gen_full_paper`
> Run: `run_xb923T0VMq4W` — Testing Critical Slowing Down as an Early Warning Signal for Multi-Agent LLM Debate Collapse
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_full_paper` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-08-01 15:58:39 UTC

````
<research_methodology>
Write like an experienced academic. Reviewers judge both the science and the writing.

- Claims must be proportional to evidence. Choose verbs carefully — "demonstrate," "observe," and "hypothesize" mean different things.
- Every result needs: what was measured, on what data, the numbers, and what they mean.
- Methodology must be specific enough to reproduce. Related work must be organized by theme, not a literature dump.
- State limitations honestly. Avoid both overclaiming and excessive hedging.
</research_methodology>

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
Your workspace: `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/4_gen_paper_repo/_4_assemble_paper/paper/workspace`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/4_gen_paper_repo/_4_assemble_paper/paper/workspace/`:
GOOD: `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/4_gen_paper_repo/_4_assemble_paper/paper/workspace/file.py`, `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/4_gen_paper_repo/_4_assemble_paper/paper/workspace/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>

<task>
Create a publication-ready top-conference LaTeX paper with BibTeX from <paper_text> and <available_figures>, compile to PDF.
</task>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<paper_text>
title: >-
  Testing Critical Slowing Down as an Early Warning Signal for Multi-Agent LLM Debate Collapse
abstract: >-
  Multi-agent LLM debate—where multiple agents exchange critiques over multiple rounds—can improve reasoning but risks collapse
  into false consensus or cascading errors. We test whether critical slowing down (CSD), a mechanism-agnostic early-warning
  signal from ecology and climate science, can predict debate collapse before it occurs. Using a real dataset of 95 multi-agent
  debates from the peer-reviewed DEBATE corpus, we measure lag-1 autocorrelation and rolling variance of inter-agent agreement
  scores and evaluate their predictive power via cross-validation. Our findings are negative: CSD statistics (mean AUC = 0.49,
  SD = 0.037) perform at chance level and are outperformed by naive agreement-score thresholds (AUC = 0.586, p < 0.05) and
  spectral cascade models (AUC = 0.587). Permutation tests on agreement trajectories find no significant pre-collapse autocorrelation
  rise (p = 0.554) and only marginal variance rise (p = 0.099). This work contributes methodologically by (1) demonstrating
  how to properly evaluate early-warning hypotheses on short time series via cross-validation and permutation testing, (2)
  quantifying the challenge of applying ecology-derived statistical signatures to discrete LLM systems, and (3) identifying
  that simple agreement-level features predict collapse as well as more sophisticated dynamics-based signals. We discuss why
  CSD fails to transfer and identify boundary conditions—notably, the discretized nature of agreement scores and the extremely
  short debate trajectories (3–7 rounds)—that may explain divergence from ecological systems.
paper_text: |
  # Testing Critical Slowing Down as an Early Warning Signal for Multi-Agent LLM Debate Collapse

  ## 1 Introduction

  Multi-agent collaboration among large language models has emerged as a promising approach to improve reasoning quality and reduce errors on complex tasks. Debate-based systems, in which multiple agent instances iteratively exchange critiques and refine positions, have shown empirical improvements: MATH accuracy improves from 49.50% (single-agent baseline) to 84.2% via debate, and GSM8K benefits from similar gains [1]. However, this collaborative approach introduces a critical vulnerability: debates do not always converge toward correct answers. Instead, they frequently collapse into one of two failure modes: *false consensus*, where all agents converge on an incorrect answer through recursive reinforcement, or *cascading error*, where a false premise propagates through agents and amplifies across rounds [2].

  The empirical record documents that while 88–94% of debate instances achieve some form of convergence within maximum rounds [3, 4], a substantial fraction converge incorrectly. Once locked into false consensus (particularly by rounds 3–4), escape becomes extremely difficult through continued iteration [2]. This creates an operational challenge: practitioners cannot distinguish a debate that will collapse until after the collapse has already occurred, limiting opportunities for intervention (e.g., halting the debate, injecting a verifier agent, diversifying model pools).

  **Existing Approaches and Their Limitations:** Multi-agent system (MAS) reliability research currently falls into two categories. Post-hoc attribution methods—exemplified by the Multi-Agent System Failure Taxonomy (MAST), which identifies 14 distinct failure modes across three categories [5]—can diagnose failures *after* a debate trace completes, but provide no advance warning. Mechanism-specific prediction models, such as spectral cascade thresholds (leveraging the spectral radius ρ(Γ_N) of the cascade propagation matrix) or Sequential Probability Ratio Testing (SPRT) on judge consensus scores, require detailed knowledge of the specific propagation mechanism and must be fitted per configuration [6, 7]. Neither approach provides a *real-time, mechanism-agnostic* signal that fires meaningfully before failure is irreversible.

  **The Transferred Hypothesis:** We investigate whether critical slowing down (CSD)—a model-free, mechanism-agnostic early-warning signature from ecology and climate science—transfers to LLM multi-agent debate dynamics. In ecology, many different kinds of catastrophic transitions (lake eutrophication, ecosystem collapse, epileptic seizures, financial crashes) share a generic statistical precursor: as a system approaches a critical threshold, it recovers more slowly from small perturbations [8]. This phenomenon manifests statistically as rising variance and rising lag-1 autocorrelation in observations of the system state over successive time steps, and crucially requires no understanding of *why* the system will fail [8, 9]. The same statistical signatures appear across systems with completely different mechanisms and scales.

  We hypothesize that this generic signal transfers to LLM multi-agent debates: as a debate approaches collapse, the inter-agent agreement trajectory should exhibit rising autocorrelation and variance before convergence locks in. This would provide a lightweight, plug-and-play early-warning gauge working across debate topologies and failure modes, without requiring that we first diagnose which specific failure is imminent.

  **Why Transfer Seemed Plausible:** Agreement-formation dynamics in debates exhibit several features that resemble bistable systems in ecology. Agents can enter a "consensus basin" (where all agents converge on a particular answer) or remain distributed across multiple distinct positions. Once the consensus basin dominates, escape becomes difficult—a hallmark of bistability. Additionally, agreement formation is a discrete dynamical process: at each round, agents observe peer responses and update their positions, making the round-by-round agreement trajectory a natural object for time-series analysis.

  **This Work:** We test the CSD hypothesis empirically on a real dataset of 95 multi-agent debates (665 round-level observations) from the peer-reviewed Multi-Agent-LLMs/DEBATE corpus [10]. For each debate, we compute lag-1 autocorrelation and rolling variance of inter-agent agreement scores and evaluate their predictive power using stratified cross-validation against ground-truth outcome labels (converged vs. collapsed). We compare CSD-based classifiers against two baselines: (1) naive agreement-score thresholds, and (2) spectral cascade models derived from agent influence patterns.

  **Key Finding and Contribution:** Our evaluation reveals that the CSD hypothesis is *not supported by the data*. The CSD classifier achieves AUC = 0.49 (SD = 0.037)—at chance level—while naive agreement thresholds achieve AUC = 0.586 and spectral models achieve AUC = 0.587 \footnote{Code: \url{https://github.com/AMGrobelnik/ai-invention-eb7b29-testing-critical-slowing-down-as-an-earl/tree/main/round-2/evaluation-1}}. Permutation tests find no significant pre-collapse autocorrelation rise (p = 0.554) and only marginal variance rise (p = 0.099). This negative result is scientifically valuable and contributes in three ways: (1) it demonstrates the proper methodology for evaluating early-warning hypotheses on short time series (cross-validation with permutation significance testing); (2) it quantifies the challenge of transferring ecology-derived signatures to discrete, short-trajectory LLM systems; and (3) it shows that simple agreement-level features already capture most predictive information, suggesting that dynamics-based signals may not provide additional leverage.

  ### 1.1 Summary of Contributions

  1. **Hypothesis Test and Negative Result:** A rigorous test of critical slowing down as an early-warning signal for multi-agent debate collapse, with honest reporting of negative findings .

  2. **Real-World Dataset and Methodology:** Standardized dataset of 95 genuine multi-agent debates from the peer-reviewed DEBATE corpus, with clear outcome labels and ground-truth annotations, evaluated via 5-fold stratified cross-validation with bootstrap confidence intervals [ARTIFACT:art_3hp2Emh5HOfw, art__Y7Wo-8aXTiM].

  3. **Methodological Roadmap for Short Time Series:** Concrete technical requirements and pitfalls for evaluating early-warning statistics on short time series (3–7 observations per debate), including permutation test design, rolling window sizing, and robustness checks for label noise [ARTIFACT:art__Y7Wo-8aXTiM, art_A_N6Ruq9QzOr].

  4. **Analysis of Transfer Failure:** Identification of boundary conditions explaining why CSD does not transfer: the discretized nature of agreement scores (leading to frequent constant trajectories and undefined autocorrelation), the extremely short debate duration (3–7 rounds), and the absence of external stochastic forcing or recovery dynamics .

  5. **Baseline Comparison and Lead-Time Analysis:** Quantitative comparison showing that naive agreement thresholds match or exceed CSD performance, with equal lead-time (all methods fire with ~7 rounds of advance notice relative to debate termination, because debates are uniformly short) .

  ## 2 Related Work

  ### 2.1 Early-Warning Signals in Ecology and Complex Systems

  Critical slowing down (CSD) is a generic statistical signature of systems approaching critical transitions. Scheffer et al.'s landmark 2009 Nature review argued that diverse complex systems exhibit CSD regardless of underlying mechanism: as a system approaches a bifurcation, recovery from perturbations slows, manifesting as rising variance and lag-1 autocorrelation in the observed state [8]. Dakos et al. (2012) provided empirical validation in lake ecosystems and ecological networks: rising variance and autocorrelation appeared 1–2 years before regime shifts, robust across detrending methods [9]. Recent work extended EWS to spectral approaches (Smax, ROSA: Ratio of Spectra) that outperform variance-based metrics in distinguishing fold from flip bifurcations and mitigating false positives from colored noise [11, 12].

  A central methodological challenge in applying EWS is distinguishing genuine system slowing from autocorrelation induced by noise. ROSA divides out the noise autocorrelation process itself, reducing false-positive rates from 60–80% to ~15–20% in colored-noise regimes [12].

  ### 2.2 Multi-Agent LLM Failure Modes and Reliability

  Recent work has systematically documented multi-agent LLM failure modes. MAST (Multi-Agent System Failure Taxonomy) identifies 14 failures across three categories: system design issues (misaligned objectives), inter-agent misalignment (conflicting information), and task verification problems [5]. Error cascade models characterize how a single false premise propagates without atomic provenance tracking, causing deterministic amplification [2]. Sycophantic conformity, where RLHF-aligned models abandon independent reasoning to adopt modal peer answers (up to 85.5% sycophancy rate), has been documented as a consensus-acceleration failure mechanism [13]. Convergence dynamics studies find that 88–94% of debates achieve consensus, but many converge incorrectly, with consensus inertia—difficulty escaping false consensus once locked in—pronounced by iteration 3–4 [3, 4].

  ### 2.3 Spectral Cascade Models and SPRT

  Spectral analysis of cascade propagation identifies the spectral radius ρ(Γ_N) as a critical parameter: ρ < 1 suppresses errors (attenuate), ρ ≈ 1 preserves magnitude, ρ > 1 triggers exponential amplification [6]. Homogeneous-model teams produce contagion coefficients 3–5× larger than heterogeneous configurations, placing them closer to cascade thresholds [6]. SPRT (Sequential Probability Ratio Testing) operates as a compute governor, monitoring likelihood-ratio boundaries on agreement patterns and terminating when evidence for one position becomes sufficient [7]. These mechanisms are powerful but require fitting per configuration—no universal parameter set applies across topologies or model mixes.

  ### 2.4 Matched-Compute Context: Does Debate Help?

  An important context for early-warning research is the matched-compute question: at equal token budgets, does multi-agent debate outperform single-agent baselines (e.g., chain-of-thought, self-consistency)? Empirical findings are mixed. Some work reports debate improvements on mathematical and logical reasoning tasks [1, 3], while other work finds that single-agent methods with equivalent compute often match or exceed debate performance [14]. This literature motivates collapse detection: even if debate sometimes underperforms single-agent baselines on average, early-warning signals remain valuable for deployments that *do* use debate, allowing practitioners to stop debate before collapse locks in and revert to safer baselines.

  ### 2.5 Novelty: Evaluating CSD Transfer to LLM Debates

  While early-warning signals are mature in ecology and spectral cascade models are established in multi-agent systems, **the rigorous empirical test of whether ecological CSD signatures transfer to LLM debate dynamics is novel**. Prior work applies CSD to diverse systems (epidemiology, climate, finance) but has not evaluated it on LLM collaboration. The present work fills this gap and, through negative findings, demonstrates that naive transfer fails and articulates the boundary conditions explaining why.

  ## 3 Methods

  ### 3.1 Dataset: Multi-Agent-LLMs/DEBATE Corpus

  We use the publicly available DEBATE corpus, a peer-reviewed dataset released at EMNLP 2025 (MALLM demo paper, 315 HuggingFace downloads) [10]. The corpus contains authentic multi-agent debate transcripts: Llama-3.3-70B agents with diverse personas (Botanist, Wildlife Biologist, Zoologist) debating yes/no factual questions over 3–7 rounds.

  We combined three debate protocol configurations to obtain balanced outcome labels:
  - `critical_expert_memory_simple_voting`
  - `critical_expert_debate_majority_consensus`
  - `critical_expert_relay_approval_voting`

  Single configurations exhibited degenerate outcome distributions (0% or 100% success). Final dataset: **95 debates with 665 round-level rows**. Outcome breakdown:
  - Converged (correct): 45 debates (47.4%)
  - Collapsed (incorrect): 45 debates (47.4%)
  - Deadlocked: 5 debates (5.3%, too sparse for mode-specific claims)

  **Known Label Noise:** ~24% of decisionSuccess=True debates in memory_simple_voting have mismatched final consensus and reference answers, indicating upstream label noise in the source dataset \footnote{Code: \url{https://github.com/AMGrobelnik/ai-invention-eb7b29-testing-critical-slowing-down-as-an-earl/tree/main/round-1/dataset-1}}. Both answers are preserved for downstream audit.

  ### 3.2 Agreement Quantification

  For each round of each debate, we compute **agreement score** = fraction of agents with the modal normalized solution text. Range: 0.33 (all agents differ) to 1.0 (full consensus). This metric is discrete but directly indexes consensus formation.

  **Critical Challenge:** Because agreement is a discretized fraction (k-of-n agents), it is frequently exactly constant across a debate's early rounds, making lag-1 autocorrelation undefined (NaN). This reduces effective sample size for autocorrelation analysis substantially below variance analysis .

  ### 3.3 CSD Statistics: Lag-1 Autocorrelation and Rolling Variance

  For each debate trajectory (3–7 observations), we compute:

  **Lag-1 autocorrelation:** ρ₁ = Σ[(zₜ - μ)(zₜ₊₁ - μ)] / Σ(zₜ - μ)². This measures persistence: ρ₁ → 1 indicates slowing, ρ₁ → 0 indicates independence.

  **Rolling variance:** Computed within sliding windows of size w ∈ {2, 3} on z-scored (within-debate) agreement. Detrending via linear regression before computing windows.

  ### 3.4 Permutation Testing on Short Time Series

  Given short time series (3–7 points), we employ block-shuffled permutation tests (10,000 replicates, block_length=2) comparing pre-collapse vs pre-convergence autocorrelation and variance [ARTIFACT:art__Y7Wo-8aXTiM]. This avoids parametric assumptions and directly estimates significance without relying on biased point estimates from short windows.

  ### 3.5 Cross-Validation and Classifier Evaluation

  We compare four binary classifiers on a 70/30 stratified debate-level train/test split:

  1. **CSD-threshold:** Predict "collapse" if early-round (rounds 1–2) rolling autocorrelation > mean + 1 SD of pre-debate baseline (converged debates).

  2. **Naive-agreement baseline:** Predict "collapse" if round-1 agreement < 25th percentile of converged debates.

  3. **Spectral-cascade model:** Compute dominant eigenvalue of persona-mention citation graph inferred from debate text; fit logistic regression on ρ(Γ_N) to predict collapse.

  4. **SPRT:** Fit per-class Normal distributions on agreement trajectories; compute cumulative log-likelihood ratio; threshold at ±2.0.

  For each classifier, we compute AUC with 1000-replicate bootstrap 95% confidence intervals, sensitivity, specificity, PPV, NPV, and lead-time (rounds before final debate round at which the classifier fires an alarm).

  ### 3.6 Robustness and Sensitivity Analysis

  We run the entire pipeline twice: once on the full dataset and once excluding the noisy memory_simple_voting config. Sensitivity to label noise is flagged if AUC changes >10% or p-values cross the 0.05 boundary .

  We also assess window-size effects and bootstrap stability of short-window rolling estimates.

  ## 4 Results

  ### 4.1 Dataset and Agreement Trajectory Characteristics

  Mean debate length: 7.0 ± 0.0 rounds (all debates in dataset have exactly 7 rounds as designed). Mean agreement score progression:
  - Round 1: 0.63 ± 0.18
  - Round 2: 0.75 ± 0.15
  - Round 3: 0.84 ± 0.12
  - Rounds 4–7: 0.91 ± 0.08

  Critically, agreement *increases* over rounds regardless of outcome (converged or collapsed debates show nearly identical trajectories). This demonstrates that agreement score alone is **not** a sufficient early-warning signal—high agreement does not discriminate correct from incorrect consensus.

  ### 4.2 Permutation Tests: CSD Statistics Do Not Show Pre-Collapse Trends

  [FIGURE:fig1]

  We compared rolling autocorrelation and variance in pre-collapse debates (rounds 1–6 of debates that collapsed at round 7) vs pre-convergence debates (identical rounds in debates that converged at round 7). Results [ARTIFACT:art__Y7Wo-8aXTiM]:

  **Autocorrelation (Full Dataset):**
  - Mean difference: 0.364 (collapse > convergence)
  - 95% CI: [-0.442, 1.169]
  - p-value (two-sided): 0.554
  - Effect size (Cohen's d): 0.512
  - Effective sample size: n=11 (collapse group), n=4 (convergence group)

  The autocorrelation signal is not statistically significant and is extremely sparse due to undefined values when agreement is constant.

  **Variance (Full Dataset):**
  - Mean difference: 0.00119 (collapse > convergence)
  - 95% CI: [-0.00029, 0.00267]
  - p-value (two-sided): 0.0994
  - Effect size (Cohen's d): 0.145
  - Effective sample size: n=250 (collapse), n=225 (convergence)

  Variance shows marginal evidence (p = 0.099) but does not reach statistical significance and exhibits small effect size. Notably, the variance effect is directionally opposite to the ecology prediction: collapsing debates have *slightly higher* variance in pre-collapse rounds, contradicting the "consensus stickiness" hypothesis.

  ### 4.3 Cross-Validation Performance: CSD at Chance Level

  [FIGURE:fig2]

  Five-fold stratified cross-validation results (95 debates total; 67 train, 28 test per fold) :

  | Classifier | Mean AUC | SD AUC | Mean Precision | Mean Recall | Mean F1 |
  |---|---|---|---|---|---|
  | CSD | 0.490 | 0.037 | 0.505 | 0.900 | 0.647 |
  | Naive-agreement | 0.586 | 0.057 | 0.526 | 1.000 | 0.690 |
  | Spectral-cascade | 0.587 | 0.054 | 0.526 | 1.000 | 0.690 |
  | SPRT | 0.586 | 0.057 | 0.526 | 1.000 | 0.690 |

  **Key Finding:** The CSD classifier performs at chance level (AUC = 0.49, SD = 0.037, 95% CI approximately [0.42, 0.56]). All three baselines significantly outperform CSD (naive and spectral are within 0.001 of each other). The CSD classifier achieves 90% recall but 0% specificity—it predicts "collapse" for nearly all debates, making it useless for early warning.

  ### 4.4 Feature Ablation: Autocorrelation Worse Than Variance

  [FIGURE:fig3]

  When evaluated separately, autocorrelation-only achieves AUC = 0.464 (worse than chance), while variance-only achieves AUC = 0.529 (still below the naive baseline of 0.586). Combined, both features together degrade to AUC = 0.490, suggesting they provide negative information or are highly correlated with noise.

  ### 4.5 Sensitivity Analysis: Robustness to Label Noise

  Excluding the memory_simple_voting config (which carries ~24% label mismatch):

  | Classifier | Full AUC | Clean AUC | |Δ AUC| |
  |---|---|---|---|
  | CSD | 0.500 | 0.500 | 0.000 |
  | Naive | 0.557 | 0.600 | 0.043 |
  | Spectral | 0.576 | 0.167 | 0.409 |
  | SPRT | 0.590 | 0.667 | 0.077 |

  Resultsare not robust. The spectral model's AUC drops 40.9 percentage points when excluding the noisy config, indicating severe overfitting to label artifacts. CSD remains at chance (0.50) in both conditions .

  ### 4.6 Lead-Time Analysis: No Advance Warning

  Lead time = rounds of advance warning before the debate's final round where the classifier fires an alarm. All debates in the dataset have exactly 7 rounds; alarm is measured relative to round 7. Results:

  | Classifier | Mean Lead Time (rounds) | SD |
  |---|---|---|
  | CSD | 7.0 | 0.0 |
  | Naive-agreement | 7.0 | 0.0 |
  | Spectral | 7.0 | 0.0 |
  | SPRT | 7.0 | 0.0 |

  All classifiers fire at or after the debate concludes—no method provides actionable advance warning. This is because debates are uniformly short (exactly 7 rounds) and agreement agreement converges quickly (by round 3–4, agreement is already >0.8). By the time any signal would fire, the debate is already effectively concluded.

  ### 4.7 Colored-Noise Analysis and CSD Mechanism Absence

  We examined the power spectral density (PSD) of agreement trajectories to assess whether they exhibit colored noise (autocorrelated forcing) that might masquerade as CSD. Results:

  - **Collapsed debates:** 68% "flat/no variation" regime, 24% white noise, 8% low-frequency-peak (system dynamics)
  - **Converged debates:** 84% "flat/no variation" regime, 13% white noise, 2% low-frequency-peak

  The dominance of the "flat" regime (agreement constant or nearly constant across early rounds) explains the high NaN rate in autocorrelation and the absence of meaningful variance. There is no evidence of system oscillations or recovery dynamics that would manifest as CSD .

  ## 5 Discussion

  ### 5.1 Why Critical Slowing Down Does Not Transfer to LLM Debates

  Our results provide clear evidence that the CSD hypothesis does not hold in multi-agent LLM debates. We identify several boundary conditions explaining this failure:

  **1. No External Recovery Dynamics:** CSD in ecological systems arises from repeated, externally-driven perturbations (seasonal forcing, rainfall variability, human interventions) that push the system away from equilibrium and test its return rate. LLM debates lack this: there is no external perturbation during debate (unless a human or external verifier injects information, which does not occur in this corpus). Agreement dynamics are purely endogenous to agent updates. Without external recovery testing, slowing cannot manifest.

  **2. Discretization and Saturation:** Agreement scores, computed as the fraction of agents sharing a modal solution, are discrete (e.g., 1/3, 2/3, 3/3 for 3 agents). Early rounds frequently exhibit agreement = 1.0 (full consensus) from the start, making the trajectory constant and autocorrelation undefined. In contrast, ecological systems measure continuous variables (e.g., lake nutrient concentration, forest biomass). Discretization leads to frequent saturation (agreement at ceiling) and high NaN rates for autocorrelation.

  **3. Extremely Short Trajectories:** Debates consist of 3–7 rounds. Classical CSD methodology (per ecology literature) operates on time series of dozens to hundreds of observations per system. Rolling windows of size 2–3 on a 7-point series are at the extreme lower limit of statistical reliability. Permutation tests and bootstrap confidence intervals partially mitigate this, but cannot overcome the fundamental information scarcity.

  **4. Bistability Unconfirmed:** CSD theory predicts bistability (competing attractor basins) as necessary. While MAST documents distinct failure outcomes, we have not explicitly measured bistability via state-space reconstruction or perturbation experiments. Debates may not exhibit true bistability—instead, agreement might be a unidirectional process (monolithic convergence once one position dominates) rather than a system poised between two competing basins.

  ### 5.2 Why Simple Agreement Thresholds Succeed Where CSD Fails

  The naive agreement-score baseline (AUC = 0.586) outperforms CSD (AUC = 0.490). This suggests that the signal predictive of collapse is simply *low agreement in early rounds*, not *dynamics of agreement*. Conversations collapsing occur when agents remain distributed across multiple positions even after several rounds—a different phenomenon than low variance or slow recovery.

  Intuitively, if after round 1 or 2 the agents have not converged to a single modal answer, the debate is less likely to converge *correctly* by the final round. This is a simpler and more direct signal than reconstructing dynamical slowing. The spectral cascade model (AUC = 0.587) also outperforms CSD by similarly leveraging agent interaction structure, but is more complex to implement (requires citation graph inference).

  ### 5.3 Methodological Contributions: How to Evaluate EWS on Short Time Series

  While the CSD hypothesis fails, this work makes a methodological contribution by establishing the proper approach for evaluating early-warning hypotheses on short, discrete time series:

  1. **Permutation Testing:** Block-shuffled permutation tests (not parametric significance) are essential when rolling-window estimates are biased and unreliable (as they are for 2–3 point windows).

  2. **Cross-Validation:** Train/test splits at the debate level (not round level) ensure no information leakage and test generalization to unseen debates.

  3. **Robustness to Label Noise:** Sensitivity analysis excluding high-noise data sources is essential—spectral models' AUC collapsed 40 points when excluding noisy configs, indicating no robust signal.

  4. **Feature Ablation:** Showing that autocorrelation-only performs worse than variance-only highlights that individual CSD components are uninformative.

  5. **Lead-Time Measurement:** Computing when classifiers fire relative to debate termination clarifies whether signals are truly advance warnings or post-hoc observations. Our result (all methods fire at debate end) reveals that 7-round debates are too short for advance warning regardless of signal type.

  ### 5.4 Implications for Multi-Agent System Design

  This negative result has positive implications for practitioners:

  1. **Simplicity is Better:** If the goal is early detection of problematic debates, simple agreement-score tracking suffices. No need for complex dynamics-based models.

  2. **Extend Debate Duration:** For early warning to be actionable, debates must extend longer than 3–7 rounds. Current debate systems in the corpus terminate at round 7 by design, leaving no time to intervene after an early-warning signal fires. Extended debates (10–20 rounds) combined with simple agreement thresholds might enable mid-trajectory intervention.

  3. **Focus on Intervention Mechanics, Not Detection:** Rather than perfecting early-warning prediction, focus on how to *act* on such signals (how to diversify models, inject corrective information, halt debate gracefully without wasting prior rounds).

  ### 5.5 Limitations

  1. **Single Model Family:** The DEBATE corpus uses only Llama-3.3-70B agents with persona variation. Multi-model deployments (GPT-4, Claude, Llama, different sizes) may exhibit different agreement dynamics and cascade coefficients 3–5× larger or smaller [6].

  2. **Single Task Domain:** Debates are yes/no factual questions. Mathematical reasoning (MATH), logical puzzles, or open-ended generation may show different convergence patterns.

  3. **No Explicit Bistability Confirmation:** We assume debate dynamics exhibit bistability but have not measured it via perturbation experiments or state-space reconstruction.

  4. **Lead-Time Ceiling:** All debates are exactly 7 rounds by design. True lead-time comparison requires longer sequences where advance warning can precede termination.

  ## 6 Conclusion

  We tested the hypothesis that critical slowing down—a generic early-warning signature from ecology—transfers to LLM multi-agent debate collapse. Using a real dataset of 95 authentic debates and rigorous cross-validation methodology, we find the hypothesis is **not supported**. CSD statistics (autocorrelation and rolling variance) perform at chance level (AUC = 0.490) and are substantially outperformed by naive agreement-score thresholds (AUC = 0.586) and spectral models (AUC = 0.587).

  This negative result is scientifically valuable, contributing (1) a methodological framework for evaluating early-warning hypotheses on short, discrete time series via permutation testing and cross-validation, (2) evidence that simple agreement-level features already capture collapse-predictive information, and (3) identification of boundary conditions explaining CSD transfer failure: discretization of agreement, extremely short trajectories (3–7 rounds), absence of external recovery dynamics, and unconfirmed bistability.

  Future work should investigate whether explicit perturbation experiments (injecting false/correct statements mid-debate and measuring recovery rate) reveal latent CSD signatures invisible in unperturbed trajectories, test generalization across longer debates and multi-model configurations, and develop intervention mechanics (how to act on early-warning signals when they do fire).

  ### Future Work

  - **Perturbation Experiments:** Inject false statements mid-debate; measure recovery rate as a direct test of critical slowing. Slower recovery in pre-collapse debates would validate the underlying mechanism.
  - **Extended Debate Trajectories:** Design debates to run 15–30 rounds, enabling true lead-time measurement and mid-trajectory interventions.
  - **Multi-Model and Multi-Task Evaluation:** Test generalization across GPT-4/Claude/Llama mixes and benchmarks (MATH, GSM8K, reasoning).
  - **Explicit Bistability Tests:** Reconstruct state-space attractor geometry via embedding; measure separatrix distance as an early warning for eventual basin boundary crossing.

  ## References

  [1] M. Ma et al., "M3MAD-Bench: Are Multi-Agent Debates Really Effective Across Domains and Modalities?" *arXiv*, 2026. ArXiv:2601.02854v1.

  [2] Y. Xie et al., "From Spark to Fire: Modeling and Mitigating Error Cascades in LLM-Based Multi-Agent Collaboration," *arXiv*, 2026. ArXiv:2603.04474.

  [3] Z. Zeng et al., "Can LLM Agents Really Debate? A Controlled Study of Multi-Agent Debate in Logical Reasoning," *arXiv*, 2025. ArXiv:2511.07784.

  [4] Z. Wang et al., "The impact of multi-agent debate protocols on debate quality: a controlled case study," *arXiv*, 2025. ArXiv:2603.28813v1.

  [5] M. Cemri et al., "Why Do Multi-Agent LLM Systems Fail?" *NeurIPS*, 2025. ArXiv:2503.13657.

  [6] J. Chen et al., "Contagion Networks: Evaluator Preference Propagation in Multi-Agent LLM Systems," *arXiv*, 2026. ArXiv:2606.20493.

  [7] R. Chen et al., "Sequential Consensus for Multi-Agent LLM Debates: A Wald-SPRT compute governor with calibration-based failure detection," *arXiv*, 2026. ArXiv:2605.19193.

  [8] M. Scheffer, S. R. Carpenter, T. M. Lenton, and J. Bascompte, "Anticipating critical transitions," *Science*, vol. 338, no. 6105, pp. 344–348, 2012.

  [9] V. Dakos, S. R. Carpenter, W. A. Brock, and A. M. Neuhauser, "Robustness of variance and autocorrelation as indicators of critical slowing down," *Ecology*, vol. 93, no. 2, pp. 264–271, 2012.

  [10] S. Min et al., "Multi-Agent LLM Debate Corpus (DEBATE)," HuggingFace, 2025. https://huggingface.co/datasets/Multi-Agent-LLMs/DEBATE.

  [11] T. Lenton et al., "Detecting and distinguishing tipping points using spectral early warning signals," *J. Royal Soc. Interface*, vol. 17, no. 170, p. 20200482, 2020.

  [12] N. Boers, B. Bookhagen, N. Marwan, and J. Kurths, "Seeking more robust early warning signals for climate tipping points: the ratio of spectra method (ROSA)," *Environ. Res. Lett.*, vol. 19, no. 5, p. 054007, 2024.

  [13] A. Sap et al., "Talk Isn't Always Cheap: Understanding Failure Modes in Multi-Agent Debate," *arXiv*, 2025. ArXiv:2509.05396.

  [14] S. Wang et al., "Scaling Laws and Compute Budgets in Multi-Agent Systems," *arXiv*, 2025. (Hypothetical reference representing matched-compute debate comparison literature.)
summary: >-
  We tested whether critical slowing down (CSD)—a generic early-warning signal from ecology—predicts multi-agent LLM debate
  collapse. Using 95 real debates from the DEBATE corpus and rigorous cross-validation, we find the hypothesis is not supported:
  CSD classifiers achieve AUC=0.49 (chance level), significantly underperforming naive agreement thresholds (AUC=0.586) and
  spectral models (AUC=0.587). Permutation tests find no significant pre-collapse autocorrelation rise (p=0.554) and only
  marginal variance rise (p=0.099). This negative result contributes methodologically by (1) establishing proper evaluation
  protocols for early-warning hypotheses on short time series, (2) demonstrating that simple agreement-level features already
  capture collapse-predictive signal, and (3) identifying boundary conditions explaining transfer failure: agreement score
  discretization, extremely short debate trajectories (3–7 rounds), absence of external perturbations, and unconfirmed bistability.
  Future work should pursue perturbation experiments, longer debate sequences, and multi-model generalization.
</paper_text>

<available_figures>
--- Item 1 ---
id: fig1
title: 'Permutation test results: CSD statistics in collapse vs convergence'
caption: >-
  Comparison of rolling lag-1 autocorrelation and rolling variance between pre-collapse debates (final round is collapse)
  and pre-convergence debates (final round is correct convergence). Left: autocorrelation distributions from 10,000 permutations.
  Mean difference autocorr: 0.364 (p=0.554, not significant). Right: variance distributions. Mean difference variance: 0.00119
  (p=0.099, marginal but not significant). Effect sizes are small (Cohen's d ≤ 0.51). NaN rates are high for autocorrelation
  due to constant agreement trajectories.
image_gen_detailed_description: >-
  Two side-by-side histograms on a white background. Left panel titled 'Lag-1 Autocorrelation Permutation Test'. X-axis labeled
  'Autocorrelation Difference (collapse - convergence)', ranging from -1.5 to 2.0. Y-axis labeled 'Frequency (out of 10000
  permutations)', ranging from 0 to 1500. Histogram shows bell-shaped distribution centered around 0, colored in light blue,
  with a red vertical line at x=0.364 (observed mean difference). Insert box: 'p=0.554, d=0.51, n_collapse=11, n_convergence=4'.
  Right panel titled 'Rolling Variance Permutation Test'. X-axis labeled 'Variance Difference (collapse - convergence)', ranging
  from -0.005 to 0.015. Y-axis labeled 'Frequency', ranging from 0 to 1500. Distribution again centered near zero with red
  line at x=0.00119 (observed difference). Insert box: 'p=0.099, d=0.145, n_collapse=250, n_convergence=225'. Sans-serif font,
  no grid.
aspect_ratio: '21:9'
summary: >-
  Permutation tests show no significant pre-collapse rise in autocorrelation (p=0.554) and only marginal variance rise (p=0.099),
  undermining the critical-slowing-down hypothesis.
figure_path: figures/fig1_v0.jpg

--- Item 2 ---
id: fig2
title: Cross-validation AUC comparison across classifiers
caption: >-
  Five-fold stratified cross-validation results comparing CSD, naive-agreement threshold, spectral cascade, and SPRT classifiers.
  CSD achieves AUC=0.49 (SD=0.037, at chance level), while naive-agreement, spectral, and SPRT all exceed AUC=0.58. Error
  bars show ±1 SD from the bootstrap. CSD's high recall (0.90) but zero specificity indicates it predicts collapse for nearly
  all debates, rendering it uninformative for early warning.
image_gen_detailed_description: >-
  Grouped bar chart. X-axis: four classifier names (CSD, Naive-Agreement, Spectral, SPRT). Y-axis: AUC, ranging 0.0-1.0. Bars:
  CSD (red) =0.490 with error bar SD±0.037; Naive-Agreement (blue) =0.586 with SD±0.057; Spectral (green) =0.587 with SD±0.054;
  SPRT (orange) =0.586 with SD±0.057. A horizontal dashed line at y=0.5 labeled 'Chance'. Bars with error bars shown as black
  whiskers. Title inside: 'Mean AUC ± 1 SD (5-fold CV, n=95 debates)'. Sans-serif font, white background, light gray grid
  on Y-axis.
aspect_ratio: '21:9'
summary: >-
  CSD classifier performs at chance level (AUC 0.49) while baseline methods exceed AUC 0.58, indicating CSD provides no predictive
  signal.
figure_path: figures/fig2_v0.jpg

--- Item 3 ---
id: fig3
title: 'Feature ablation: individual vs combined CSD components'
caption: >-
  AUC when using autocorrelation alone, variance alone, or both features combined. Autocorrelation alone (AUC=0.464) performs
  below chance, variance alone (AUC=0.529) below baselines, and combined (AUC=0.490) is worse than variance alone, suggesting
  feature interactions are unhelpful or negatively correlated.
image_gen_detailed_description: >-
  Bar chart with three bars. X-axis: feature combination (Autocorr-Only, Variance-Only, Both). Y-axis: AUC, ranging 0.0-1.0.
  Bars: Autocorr-Only (light red) =0.464 with error bar SD±0.028; Variance-Only (light blue) =0.529 with SD±0.020; Both (light
  orange) =0.490 with SD±0.037. Dashed line at y=0.5 labeled 'Chance'. Dashed line at y=0.586 labeled 'Naive-Baseline'. Title:
  'Feature Ablation: AUC by Feature Set (5-fold CV)'. Sans-serif font, white background.
aspect_ratio: '21:9'
summary: >-
  Autocorrelation alone underperforms chance; variance alone is weak; combined CSD features degrade further, indicating neither
  component carries useful signal.
figure_path: figures/fig3_v0.jpg
</available_figures>

<figure_requirements>
CRITICAL: Include ALL figures from <available_figures>. No exceptions.

- Every figure MUST use \includegraphics{figures/filename.jpg}
- Do NOT skip, convert to tables, or describe without inserting
- Each needs: \begin{figure*|figure}[placement], \includegraphics, \caption, \label, \end{...} — pick env + placement by the figure's `aspect_ratio` field (see PLACEMENT below). Constrain every \includegraphics with `width=\linewidth,height=0.4\textheight,keepaspectratio` (single-column) or `width=\textwidth,height=0.45\textheight,keepaspectratio` (figure*). Use exactly these option keys — `max height=` is NOT valid LaTeX
- Use the `caption` field from each figure for \caption{...} — do NOT invent new captions
- Place figures where their [FIGURE:fig_id] markers appear in paper_text
- VERIFICATION: paper.tex MUST have exact same number of \includegraphics as <available_figures>
- Do NOT generate new figure images (no matplotlib, no PIL, no image generation). Use ONLY the pre-generated figures from <available_figures>. They were already created by a previous pipeline step.

PLACEMENT BY ASPECT RATIO (use the `aspect_ratio` field on each figure):
- `21:9` (architecture diagrams / hero figures): \begin{figure*}[!t] (full two-column width, top of page). The hero architecture diagram should appear EARLY in the paper — typically at the top of page 2. Marker placement in paper_text already determines this; preserve it.
- `16:9` (comparisons, multi-panel results): \begin{figure*}[!t] for full-width or \begin{figure}[!htbp] for single-column.
- `4:3` / `1:1` / `3:2` / `3:4` / `9:16`: \begin{figure}[!htbp] (single-column).
</figure_requirements>

<artifact_links>
The paper_text contains \footnote{Code: \url{...}} references linking to artifact source code
on GitHub. Include \usepackage{hyperref} and \usepackage{url}.
Preserve these exactly as-is — do not remove, rewrite, or convert them to plain text.
The URLs will not resolve yet (the repo is deployed after compilation) — do NOT try to verify or fix them.
</artifact_links>

<headings>
NEVER use inline math (``$...$``) inside ``\section{...}`` / ``\subsection{...}`` / ``\subsubsection{...}`` arguments — hyperref's bookmark builder errors out (``Token not allowed in a PDF string``) and the PDF outline breaks. If a section heading needs a math-looking term, use the text equivalent (``d star`` not ``$d^*$``, ``alpha-equivalent`` not ``$\alpha$-equivalent``) or wrap it in ``\texorpdfstring{$math$}{plain}``. Inline math inside body paragraphs is fine.
</headings>

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-paper-to-latex, aii-semscholar-bib.
TODO 2. Review <paper_text> and <available_figures>. Copy all figure images into ./figures/ in your workspace. Count figures — MUST include every one. Plan placements per section. Build `./references.bib` via aii_semscholar_bib__fetch — collect DOIs/ArXiv IDs from <paper_text> and batch-fetch all BibTeX in one call. Do NOT fabricate entries.
TODO 3. Create `./paper.tex` per aii-paper-to-latex skill's setup, write ALL sections, insert ALL figures from <available_figures>, include `./references.bib` via \bibliography. Compile to PDF per skill's process. Fix errors.
TODO 4. CRITICAL VERIFICATION: Run `grep -c 'includegraphics' paper.tex`, confirm count equals figures in <available_figures>. If not, add missing figures. Verify `./paper.pdf` was created.
TODO 5. VISUAL REVIEW: Write Python script to convert EVERY page of paper.pdf to PNG at 150 DPI (use pdf2image or pymupdf). Then read ALL page screenshots — each page image costs ~1,600 tokens so a 15-page paper is only ~24K tokens. You MUST read every page. The ONLY exception is if all page images would not fit in your remaining context — in that case, read as many as fit and state which pages you are skipping and why. Check every page for layout issues, overlapping figures, cut-off text, bad spacing, formatting problems. Fix issues and recompile.
TODO 6. FINAL READ: Check page count (`pdfinfo paper.pdf` or pymupdf). Read entire paper.pdf — check for missing sections, unclear explanations, inconsistencies, typos. Fix and recompile. The ONLY exception is if all pages would not fit in your remaining context — in that case, read as many pages as fit and state which pages you are skipping and why.
</todos>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "FullPaperExpectedFiles": {
      "description": "All expected output files from full paper generation.",
      "properties": {
        "paper_tex_path": {
          "description": "Path to LaTeX source file. Example: 'paper.tex'",
          "title": "Paper Tex Path",
          "type": "string"
        },
        "paper_pdf_path": {
          "description": "Path to compiled PDF. Example: 'paper.pdf'",
          "title": "Paper Pdf Path",
          "type": "string"
        },
        "references_bib_path": {
          "description": "Path to BibTeX bibliography file. Example: 'references.bib'",
          "title": "References Bib Path",
          "type": "string"
        },
        "figure_paths": {
          "description": "Paths to all figure image files. Example: ['figures/fig1_v0.jpg', 'figures/fig2_v0.jpg']",
          "items": {
            "type": "string"
          },
          "title": "Figure Paths",
          "type": "array"
        }
      },
      "required": [
        "paper_tex_path",
        "paper_pdf_path",
        "references_bib_path",
        "figure_paths"
      ],
      "title": "FullPaperExpectedFiles",
      "type": "object"
    }
  },
  "description": "Full paper \u2014 structured output from paper generation.",
  "properties": {
    "title": {
      "description": "Paper title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance. Aim for about 4-8 words (~40 characters).",
      "maxLength": 90,
      "minLength": 12,
      "title": "Title",
      "type": "string"
    },
    "summary": {
      "description": "Brief summary of the generated paper: sections written, figures included, compilation status",
      "maxLength": 5000,
      "minLength": 500,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/FullPaperExpectedFiles",
      "description": "All output files you created. Must include paper.tex, paper.pdf, references.bib, and paths to all figure files."
    }
  },
  "required": [
    "title",
    "summary",
    "out_expected_files"
  ],
  "title": "FullPaper",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [2] HUMAN-USER prompt · 2026-08-01 15:58:39 UTC

```
LAUNCH WINDOW RELOAD: reload while the start POST is still in flight.
```

### [3] SKILL-INPUT — aii-paper-to-latex · 2026-08-01 15:58:47 UTC

The agent loaded the **aii-paper-to-latex** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-paper-to-latex
description: LaTeX paper assembly and compilation. Covers document setup, figure inclusion from pre-generated JPEGs, compilation process, and output files. Use when assembling a paper from pre-written text and pre-generated figures into a compiled PDF.
---

## LaTeX Paper Assembly

Assembles a research paper from paper text, pre-generated figure JPEGs, and bibliography into a compiled PDF.

### Document Setup

```latex
\documentclass[11pt,letterpaper]{article}
\usepackage{graphicx, geometry, amsmath, hyperref, natbib, booktabs, xcolor, listings}
\geometry{margin=1in}
\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black}
```

### Figure Inclusion

CRITICAL: Include ALL figures. Every figure MUST appear in the paper.

```latex
\begin{figure}[!htbp]
  \centering
  \includegraphics[width=0.92\textwidth,keepaspectratio]{figures/filename.jpg}
  \caption{Descriptive caption.}
  \label{fig:label}
\end{figure}
```

Rules:
- ALWAYS use `[!htbp]` float placement (NOT `[t]` or `[h]` alone)
- ALWAYS constrain with `width` and `keepaspectratio` to prevent page takeover
- Every figure needs `\caption`, `\label`, and a `\ref` in the text
- Do NOT convert figures to tables or describe them without inserting the image
- Do NOT skip any figures

### Compilation Process

Run each command separately (do NOT chain with `&&` — pdflatex often exits non-zero on warnings, which would skip bibtex and leave citations as `??`):

```bash
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
```

All four commands are required. Skipping bibtex causes `??` in all citations.
Fix any errors between runs. Verify `./paper.pdf` was created.

### Output Files

- `./paper.tex` — LaTeX source
- `./references.bib` — bibliography file
- `./paper.pdf` — compiled PDF
- `./figures/*.jpg` — all figure images (pre-generated, copied into workspace)
````

### [4] SKILL-INPUT — aii-semscholar-bib · 2026-08-01 15:58:51 UTC

The agent loaded the **aii-semscholar-bib** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-semscholar-bib
description: Build bibliographies using Semantic Scholar. Batch-fetch BibTeX for papers by DOI, ArXiv ID, or title. Use when writing papers, generating reference lists, or building .bib files.
---

## Tool: `aii_semscholar_bib__fetch`

Batch-fetch BibTeX entries from Semantic Scholar. Pass all references in a single call — the tool handles batching internally.

### How it works

1. **DOI/ArXiv refs** → batched into POST /paper/batch calls (up to 500 per API call, auto-chunked)
2. **Title-only refs** → individual GET /paper/search/match (1s delay between)
3. **Post-process** → fix entry type, fix citation key (AuthorYYYY), inject DOI

The ability server runs a single worker (`max_threads: 1`). Multiple concurrent tool calls are queued — each runs independently (no cross-request aggregation). Batching happens within each request.

### Input format

```json
{
  "references": [
    {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
    {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
    {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
  ]
}
```

Each reference object can have:
- `doi` — DOI string (ArXiv DOIs like `10.48550/arXiv.XXXX.XXXXX` auto-convert to ArXiv IDs)
- `arxiv` — ArXiv ID (e.g. `"2305.14325"`)
- `title` — Paper title (used for search/match when no DOI/ArXiv)
- `author` — First author last name (for cleaner citation key)
- `year` — Publication year (int, for citation key)

At least one of `doi`, `arxiv`, or `title` is required per reference.

### Output format

```json
{
  "success": true,
  "bib_text": "@inproceedings{Vaswani2017, ...}\n\n@article{Wei2022, ...}",
  "total": 3,
  "found": 3,
  "failed_count": 0,
  "entries": [{"citation_key": "Vaswani2017", "bibtex": "...", "title": "...", "doi": "...", "arxiv": ""}],
  "failed": []
}
```

### Workflow

1. Collect DOIs, ArXiv IDs, or titles for all papers you need to cite
2. Call `aii_semscholar_bib__fetch` with the full list in **one call**
3. Save `bib_text` from the response to your `references.bib` file
4. Check `failed` — for any missed papers, follow the **fallback procedure** below

### Fallback for failed references (MANDATORY)

NEVER fabricate BibTeX. For each failed reference:
1. **WebSearch** for `"Title" author year` (try `site:arxiv.org` too)
2. **WebFetch** the paper page → extract title, authors, year, venue, DOI/ArXiv ID
3. If DOI/ArXiv found → retry `aii_semscholar_bib__fetch` with it
4. Last resort: write BibTeX by hand using **only verified info from the actual paper page**

---

### CLI (for manual use / debugging)

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-semscholar-bib" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_semscholar_bib__fetch.py --refs '[
  {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
  {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
  {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
]'
```

`--json, -j` — output raw JSON instead of .bib text

**If the script fails** with a connection error (ability server not running): create a local `.venv`, install server deps from `server_requirements.txt` into it, then import the `@aii_ability` function from the script and call it directly — bypassing the server:
```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r "$SKILL_DIR/scripts/server_requirements.txt"
```
````
