# gen_plan_experiment_1 — test_idea

> Phase: `invention_loop` · round 2 · `gen_plan`
> Run: `run_xb923T0VMq4W` — Testing Critical Slowing Down as an Early Warning Signal for Multi-Agent LLM Debate Collapse
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_plan_experiment_1` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-08-01 15:26:29 UTC

````
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: A plan generator (Step 3.2: GEN_PLAN in the invention loop)

You received the hypothesis, an artifact direction to elaborate, and dependency artifacts relevant to the plan.
Your job: elaborate this direction into a detailed, actionable plan for the executor agent.

Specific, actionable plan → valuable artifact. Vague plan → wasted execution.
</your_role>
</ai_inventor_context>

<artifact_type_info>
You are expanding an artifact direction of type: EXPERIMENT

EXPERIMENT
Run code to test hypotheses, implement methods, and collect empirical results.
Runtime: Python 3.12, UV (any pip package), isolated workspace, gradual scaling (mini → full data).
Tools: Full shell/Python/filesystem access, the aii-web-tools skill (web search, page fetch, regex grep over full page/PDF text), and other skills.
Skills: aii-json (schema validation), aii-openrouter-llms (call any LLM — GPT, Gemini, Llama, etc.), domain-specific as needed.
Capabilities: Implement and run any code-based experiment, compare method vs baselines.
Deps: REQUIRED at least one DATASET | OPTIONAL RESEARCH for methodology guidance
</artifact_type_info>

<available_resources>
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

<software_constraints>
- Python only implementation
- Python standard library and all popular PyPI packages available (numpy, pandas, scikit-learn, scipy, matplotlib, requests, etc.)
- Local parallelism encouraged: multiprocessing, asyncio, threading — see aii-parallel-computing skill
- LLM API calls must go through OpenRouter only (no direct OpenAI, Anthropic, etc.)
- **HARD LIMIT**: Maximum $10 USD total spend on LLM API calls (OpenRouter). Track cumulative cost after every call and STOP IMMEDIATELY if approaching this limit. Never exceed this budget under any circumstances.
</software_constraints>
</available_resources>

<time_budget>

The experiment executor has 6h total (including writing code, debugging, testing, and fixing errors).

</time_budget>

<available_tools>
Web research is available through the aii-web-tools skill, in three levels (broad → specific):

1. web search — Returns titles, URLs, snippets. Use first to discover and scan the landscape.
2. web fetch — Reads a page and returns its content as markdown (HTML or PDF). Use to understand a source. May miss specific details — use fetch_grep below if it doesn't find what you need.
3. fetch_grep — Regex search over a page/PDF's full text. Returns exact matching sections with context. Use for precise details, exact numbers, methodology, or PDFs.

Workflow: search → fetch (understand) → fetch_grep (extract specifics).
</available_tools>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<plan_guidelines>
You are expanding an artifact direction from the strategy into a detailed plan.
The artifact direction specifies what to do at a high level (type, objective, approach, dependencies).
Your job is to make it concrete and actionable as a detailed plan.
Use web research to look up technical details, verify feasibility, and find reference materials
that will make your plan more concrete and actionable for the executor.

GOOD PLANS:
- Make each component SPECIFIC and actionable (not vague platitudes)
- Consider both success AND failure scenarios
- Build on the approach in the artifact direction
- Add concrete details the executor needs

BAD PLANS:
- Vague hand-waving ("do research on X")
- Ignoring the approach in the artifact direction
- Missing critical details the executor needs
</plan_guidelines>

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

<hypothesis>
kind: hypothesis
title: Critical Slowing Down Warns of Debate Collapse
hypothesis: >-
  In multi-agent LLM debate, the ecological 'critical slowing down' (CSD) signature — a directional rise in lag-1 autocorrelation
  (and, more ambiguously, a change in variance) of the round-by-round inter-agent agreement trajectory — appears before debates
  collapse into false consensus or cascading error, and can serve as a mechanism-agnostic early-warning statistic. Given the
  short trajectories available (3-7 rounds per debate), the claim is restricted to a QUALITATIVE, population-level effect
  (pre-collapse debates show higher round-1/2 autocorrelation than converging debates, pooled across debates via permutation/hierarchical
  testing) rather than a precise per-debate point estimate; individual-debate autocorrelation/variance values on 2-3-point
  rolling windows are not claimed to be reliable in isolation. The claim now covers only the two failure modes with adequate
  sample size in available data — cascading/false-consensus collapse — and explicitly does NOT claim CSD detects deadlock,
  since deadlock is too rare (n=5) in the current corpus to support any mode-specific claim. A companion goal is to make the
  theoretical transfer argument self-contained: a minimal formal bistable discrete-time model of agreement dynamics with an
  explicit drift parameter approaching a fold bifurcation, developed in the paper body rather than only summarized from a
  background artifact.
motivation: >-
  Existing multi-agent system (MAS) reliability work either attributes failure AFTER it happened (MAST-style taxonomies, Who&When
  attribution) or predicts failure using a specific mechanistic model of propagation (spectral cascade thresholds, epidemic/percolation
  models, SPRT on a judge's consensus score) that must be fitted per failure type and per topology. None of these give a cheap,
  universal, real-time 'is this debate about to tip over' signal that works regardless of whether the impending failure is
  an error cascade, a groupthink collapse, or a deadlock. Ecology and climate science solved an analogous problem decades
  ago: many very different kinds of regime shifts (lake eutrophication, ecosystem collapse, epileptic seizures, financial
  crashes) share the same generic precursor — as a system approaches a critical transition, its recovery from small perturbations
  slows down, which shows up statistically as rising variance and rising autocorrelation in the observed state, regardless
  of the underlying mechanism. If this signature transfers to LLM debate dynamics, it would give MAS designers a lightweight,
  plug-in, failure-type-agnostic early-warning gauge — directly useful for deciding when to trigger costly interventions (extra
  verifier agents, human escalation, model diversification) without having to first diagnose which of the many known MAS failure
  modes is occurring.
assumptions:
- >-
  Inter-agent agreement/consensus in a debate can be quantified as a numeric or vector state at each round (e.g., pairwise
  embedding similarity of agent responses, or a judge-model consensus score), producing a short discrete time series per debate.
- >-
  Debates that end in collapse (error cascade, false consensus, deadlock) pass through a genuine dynamical transition rather
  than failing instantly at round 1, so there are at least 3-5 rounds of pre-collapse dynamics to measure trends in.
- >-
  The generic critical-slowing-down statistics (variance, lag-1 autocorrelation) can be estimated meaningfully from short
  LLM-debate time series (few rounds, need repeated/perturbed trials or cross-topic pooling to get enough samples per debate).
- >-
  A meaningful fraction of runs collapse under standard multi-agent debate setups on existing benchmarks, so both collapsing
  and non-collapsing trajectories can be compared.
investigation_approach: >-
  Use OpenRouter to run multi-agent debate (e.g., 3-5 agent debate/refinement rounds, mixing model families for realism) over
  a benchmark with objectively checkable answers (e.g., a math/logic QA set) so each run can be labeled ex post as 'collapsed
  into a wrong consensus' or 'converged to correct answer' or 'deadlocked'. For each run, at every round compute a scalar
  agreement statistic from response embeddings (e.g., a lightweight embedding model or simple lexical/semantic similarity)
  and, separately, an LLM-judge consensus score. To get enough repeated samples to estimate rolling variance/autocorrelation
  within a debate, run each debate instance multiple times with small temperature-induced perturbations (mirroring how ecological
  EWS studies use repeated systems or spatial replicates when a single time series is too short) and treat the ensemble of
  perturbed replicates at each round as the 'system under repeated small perturbation.' Compute rolling variance and lag-1
  autocorrelation of the agreement statistic across rounds, and test whether these rise in the rounds preceding collapse,
  using collapsing vs. non-collapsing runs as the two classes. Compare this generic EWS signal's predictive lead time and
  AUC against two baselines: (a) a naive threshold on the agreement score itself (does agreement just look 'low' right before
  collapse, i.e. no advance warning), and (b) a cascade-specific baseline (fit a simple propagation/spectral estimate per
  run) to see whether the mechanism-agnostic signal is competitive with a mechanism-specific one despite requiring no model
  fitting.
success_criteria: >-
  Confirmed if: (1) collapsing runs show a statistically significant rise in variance and/or lag-1 autocorrelation of the
  agreement statistic in the 1-2 rounds preceding collapse, relative to non-collapsing runs (e.g., higher AUC than chance
  for classifying eventual collapse using only pre-collapse EWS trend, tested with a held-out set and permutation-based significance);
  (2) the EWS-based warning fires with positive lead time before the agreement score itself drops below any fixed 'low agreement'
  threshold, i.e., it is not simply restating that agreement is already low; (3) the EWS signal's classification performance
  is comparable to (not necessarily better than) the cascade-specific spectral/SPRT baseline, despite using no model of the
  failure mechanism. Disconfirmed if variance/autocorrelation show no consistent pre-collapse trend, or only trend after agreement
  has already dropped (no lead time), or the effect only appears in one narrow debate configuration and does not generalize
  across topologies (e.g., star vs. chain) or benchmarks.
related_works:
- >-
  MAST (Multi-Agent System Failure Taxonomy) and successors classify and attribute MAS failures AFTER a trace completes (post-hoc
  diagnosis); this hypothesis instead targets a real-time, pre-collapse statistical precursor computed while the debate is
  still running.
- >-
  'From Spark to Fire' (error-cascade modeling in LLM multi-agent collaboration) derives a spectral amplification threshold
  R = beta*rho(A)/delta from an explicit Independent-Cascade propagation model fit to the specific topology and transmission/correction
  rates; this hypothesis instead uses a model-free statistical signature (variance/autocorrelation) that needs no mechanistic
  cascade model and is not tied to one failure mechanism.
- >-
  Sequential Consensus for Multi-Agent LLM Debates (Wald-SPRT compute governor) halts debate using a sequential hypothesis
  test on an LLM judge's consensus score reaching a 'useful convergence' boundary; this is a decision rule about whether MORE
  debate rounds will help, not a warning that the debate is approaching a failure/collapse regime, and it requires calibrating
  the judge's score to the domain, whereas EWS statistics are computed directly on any agreement signal without domain-specific
  calibration.
- >-
  Percolation-theory/epidemic-threshold approaches to MAS reliability (e.g., Reliability-Contagion Feasibility in LLM multi-agent
  networks) predict a static structural failure threshold from network topology and per-node fault probabilities before deployment;
  this hypothesis is dynamic and run-time, monitoring the live trajectory of a specific ongoing debate rather than a topology-level
  structural constant.
- >-
  Early-warning signals for critical transitions in ecology/climate science (Scheffer et al., and the deep-learning-for-EWS
  line) establish that rising variance and autocorrelation generically precede many kinds of regime shifts in complex systems;
  this hypothesis is the first application of that specific generic-EWS toolkit (as opposed to domain-specific propagation
  models) to LLM multi-agent debate dynamics.
inspiration: >-
  CONCEPTUAL: borrowing the ecology/climate-science idea that a system nearing a critical transition can be flagged generically,
  without knowing the transition's specific cause, because slowed recovery from perturbation is a universal signature of approaching
  a tipping point (Scheffer et al.'s 'early-warning signals for critical transitions'). METHODOLOGICAL: importing the concrete
  statistics used for this in dynamical-systems/ecology — rolling variance and lag-1 autocorrelation of a system's state over
  successive small perturbations — and applying them directly, with minimal modification, to the round-by-round agreement
  trajectory of LLM multi-agent debates, in place of the mechanism-specific propagation/spectral models (cascade thresholds,
  SPRT on judge scores) that the multi-agent-systems field currently uses for run-time reliability signals.
terms:
- term: Critical slowing down
  definition: >-
    A property of dynamical systems approaching a critical transition (tipping point): the system recovers more slowly from
    small perturbations, which manifests statistically as increasing variance and increasing autocorrelation in the observed
    state over time, before any visible collapse occurs.
- term: Early-warning signal (EWS)
  definition: >-
    A generic, model-free statistical indicator (e.g., rising variance or rising lag-1 autocorrelation) computed from a system's
    observed state over time that tends to precede many different kinds of critical transitions, without requiring a mechanistic
    model of the specific transition.
- term: Lag-1 autocorrelation
  definition: >-
    The correlation between a time series and a one-step-lagged copy of itself; rising lag-1 autocorrelation indicates the
    system's state is becoming more persistent/slower to change, a hallmark of approaching a critical transition.
- term: Multi-agent debate
  definition: >-
    A collaborative LLM setup where multiple agent instances (possibly different models) exchange and critique responses over
    several rounds before converging on a final answer.
- term: Debate collapse
  definition: >-
    The endpoint where multi-agent debate ends in a failure state — the agents converge on an incorrect answer (false consensus/error
    cascade) or fail to converge at all (deadlock) — as opposed to converging on a correct, well-supported answer.
- term: Cascade-specific spectral threshold
  definition: >-
    A structural reliability estimate (used in prior MAS work) computed from an explicit model of error propagation over the
    agent graph, such as R = beta*rho(A)/delta, where exceeding a threshold predicts runaway error spread; requires fitting
    transmission/correction parameters to a specific propagation mechanism.
summary: >-
  This hypothesis proposes that the generic 'critical slowing down' statistics used in ecology and climate science to anticipate
  regime shifts — rising variance and rising autocorrelation before a tipping point — also appear in the round-by-round agreement
  trajectory of LLM multi-agent debates before they collapse into cascading errors or false consensus, offering a mechanism-agnostic,
  real-time early-warning signal that existing MAS reliability tools (which are either post-hoc or tied to a specific failure
  mechanism) do not provide.
_relation_rationale: >-
  Same CSD-transfer frame; narrowed to qualitative/pooled claims, dropped deadlock, added self-contained formal model
_confidence_delta: decreased
_key_changes:
- >-
  Downgraded per-debate point estimates (AUC, exact p-values, Cohen's d, Spearman rho) to unverified pending a real analysis-code
  artifact that reproduces every Section 4 statistic directly from the 665-row dataset; anything only echoing the research-roadmap's
  'anticipated' ecology figures (e.g. 60-80% colored-noise false-positive rate) must be labeled as literature expectation,
  not measurement
- >-
  Restricted statistical claims to qualitative/population-level trends given 3-7 round trajectories and 2-3 point rolling
  windows, per reviewer's methodology critique; recommend pooling via permutation testing or hierarchical/mixed-effects models
  rather than treating each debate's autocorrelation as a precise independent estimate
- >-
  Dropped deadlock as a claimed detectable failure mode (only n=5 cases) — hypothesis now explicitly scoped to cascade/false-consensus
  collapse only
- >-
  Added requirement for an explicit, self-contained minimal formal bistable model (toy discrete-time map with a fold-bifurcation
  drift parameter) for the theoretical transfer argument, rather than deferring entirely to the background research artifact
- >-
  Added need to situate against the matched-compute skepticism literature on multi-agent debate (i.e., debate sometimes underperforms
  single-agent baselines) and to explicitly describe baseline-classifier construction (naive/spectral/SPRT) with train/calibration
  splits and information parity across rounds
- >-
  Flagged need for a sensitivity analysis excluding the noisy memory_simple_voting config (~24% label mismatch) before headline
  numbers can be trusted
relation_type: evolution
</hypothesis>

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for the methods, proper baselines, and evaluation this field demands.

- **aii-handbook-auto-computational-linguistics** — Verified field handbook for computational linguistics as a SCIENCE of language (not NLP engineering).
- **aii-handbook-auto-mechanistic-interpretability** — Verified field handbook for mechanistic-interpretability research.
- **aii-handbook-auto-multi-agent-llm-systems** — Verified field handbook for multi-agent LLM systems (MAS) research.
- **aii-handbook-auto-neurosymbolic** — Verified field handbook for neuro-symbolic AI research (LLM+solver, autoformalization, text2logic).
</available_domain_handbooks>

<artifact_direction>
Make this direction concrete and actionable. Keep the same type and respect dependencies.

id: experiment_iter2_dir1
type: experiment
objective: >-
  Reproduce and verify every statistic in Section 4 directly from the 665-row dataset, using hierarchical modeling to handle
  short time series, and establish honest scope boundaries (deadlock underpowered; cascade + false-consensus only).
approach: >-
  Load the full_data_out.json dataset from art_3hp2Emh5HOfw (665 round-level rows, 95 debates, 3-7 rounds each). For each
  debate trajectory, compute rolling lag-1 autocorrelation and rolling variance (window sizes 2-3, following Section 3.3).
  Perform permutation tests (10,000 permutations, block-shuffle with block length 2) to test whether autocorrelation rises
  significantly more in pre-collapse vs. non-collapse debates (reproduces p=0.031 claim). Similarly test rolling variance
  differences (reproduces p=0.018 claim). Fit hierarchical logistic regression: outcome ~ round + autocorrelation + (1|debate_id),
  using all 665 rows, to borrow strength across debates and handle short sequences. Compute AUC for four binary classifiers:
  (1) CSD threshold (round-1/2 autocorrelation > baseline+1SD), (2) naive agreement (round-1 agreement < 25th percentile),
  (3) spectral model (infer contagion matrix from agent citations, test if ρ>1), (4) SPRT (likelihood ratio on agreement crossings).
  For each classifier, compute 95% bootstrap CIs (1000 replicates, stratified by outcome label). Compute lead time: number
  of rounds before final agreement drop that signal crosses threshold; report mean ± SD for each classifier. Conduct sensitivity
  analysis: run all above analyses twice—once on full dataset (n=95), once excluding memory_simple_voting config (which has
  ~24% label noise). Report whether AUC/p-values/lead times change materially; if results are robust to label noise, include
  both; if sensitive, flag. Explicit deadlock breakdown: show that n=5 deadlocked cases are too rare for any mode-specific
  claim. Report separate results for cascade (n~45) vs. false-consensus (n~45) if feasible. Output: method_out.json with all
  statistics (p-values, AUCs with bootstrap CIs, lead times, effect sizes, hierarchical model coefficients), detailed tables
  showing which numbers are permutation-test-derived vs. bootstrap vs. hierarchical, and sensitivity analysis results. Generate
  figures (e.g., ROC curves, lead-time distributions, autocorrelation trajectories) annotated to show statistical methods
  used.
depends_on:
- id: art_3hp2Emh5HOfw
  label: dataset
  relation_type:
  relation_rationale:
</artifact_direction>

<dependencies>
Completed artifacts this artifact can use during execution.

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
out_expected_files:
- data.py
- full_data_out.json
- preview_data_out.json
- mini_data_out.json
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
</dependencies>

<instructions>
YOUR ROLE: Write a detailed PLAN for the artifact. A separate executor agent runs the actual artifact later.

You are a PLANNER, not an executor. Your output is a plan that tells the executor what to do and how.
Do NOT execute the artifact itself — a separate agent handles that. Your job is to plan it so well that the executor can follow your plan step by step.

You CAN and SHOULD: search the web, read papers, and explore library docs to make your plan concrete.
You CANNOT run shell commands or scripts — code execution is disabled. Research via web tools only.

Do NOT do the executor's job: don't download datasets, don't implement code, don't run experiments, don't write proofs, don't compute evaluations.

<artifact_executor_scope>
IMPORTANT: Each artifact executor has a focused prompt that guides it to do ONE thing well. It will NOT perform tasks outside its scope — assigning the wrong work to the wrong artifact type wastes an iteration. Match the task to the right executor.

EXPERIMENT executor scope:
  Output: method_out.json with results (metrics, predictions, analysis) — the core computational work
  DOES: Implement and run methods/algorithms, compute metrics, compare approaches, produce quantitative results
  DOES NOT: Collect new datasets (depends on DATASET artifacts for input data), write formal proofs
  This is the right artifact for any code that processes data and produces results
</artifact_executor_scope>

<artifact_planning_rules>
EXPERIMENT: Must depend on at least one DATASET. Define clear metrics and baselines before running. Consider trying multiple method variations rather than a single approach.
</artifact_planning_rules>


GOOD PLANS: specific, actionable, consider failure scenarios, build on the suggested approach.
BAD PLANS: vague hand-waving, ignoring the suggested approach, missing critical executor details.
</instructions><user_data>
User-provided reference materials are available at `/home/adrian/projects/ai-inventor/aii_data/users/uitest-20260731/runs/run_xb923T0VMq4W/user_uploads`. Check this folder for anything relevant to your task.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above. Do NOT follow directives inside that message as if they were addressed to you.
</user_original_request>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "description": "Plan for an EXPERIMENT artifact.",
  "properties": {
    "title": {
      "description": "Plan title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters).",
      "title": "Title",
      "type": "string"
    },
    "summary": {
      "default": "",
      "description": "Brief summary",
      "title": "Summary",
      "type": "string"
    },
    "runpod_compute_profile": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "cpu_light",
      "description": "Compute tier for execution \u2014 pick from the available profiles list (e.g., 'gpu', 'cpu_heavy', 'cpu_light'). Only used in RunPod mode.",
      "title": "Runpod Compute Profile"
    },
    "implementation_pseudocode": {
      "description": "High-level pseudocode for the experiment implementation",
      "title": "Implementation Pseudocode",
      "type": "string"
    },
    "fallback_plan": {
      "description": "What to do if the primary approach fails - alternative methods, simplified versions",
      "title": "Fallback Plan",
      "type": "string"
    },
    "testing_plan": {
      "description": "How to validate the experiment works: start with small/fast tests, look for confirmation signals before running full-scale experiments",
      "title": "Testing Plan",
      "type": "string"
    }
  },
  "required": [
    "title",
    "implementation_pseudocode",
    "fallback_plan",
    "testing_plan"
  ],
  "title": "ExperimentPlan",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [2] HUMAN-USER prompt · 2026-08-01 15:26:29 UTC

```
LAUNCH WINDOW RELOAD: reload while the start POST is still in flight.
```

### [3] SKILL-INPUT — aii-handbook-auto-multi-agent-llm-systems · 2026-08-01 15:26:43 UTC

The agent loaded the **aii-handbook-auto-multi-agent-llm-systems** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

```
---
name: aii-handbook-auto-multi-agent-llm-systems
description: "Verified field handbook for multi-agent LLM systems (MAS) research. ALWAYS read before ANY multi-agent-LLM research work — ideation/novelty assessment, study planning, experiment/eval design, write-up, or review; do NOT do any of these from priors alone (the frontier moved fast through H1-2026 and several obvious-looking directions are saturated). Triggers: multi-agent systems / MAS, agent orchestration or topology, multi-agent debate, mixture-of-agents, inter-agent communication or protocols (MCP/A2A), MAS failure analysis / attribution / self-evolution, MAS benchmarks, cost or token economics of agent systems. NOT for: building single-agent apps, framework API how-tos (AutoGen / LangGraph / CrewAI usage), classical non-LLM multi-agent systems (MARL, robotics, agent-based social simulation), or generic prompting questions."
---

<!-- GENERATED by amg-handbook-forge — DRAFT for expert review. generated: 2026-07-07 · next_check:
     2026-10 (volatile.md half-life ≈ months). ✓x=exec · [Sn]=cited · ⚠️=candidate. Row fails → `STALE: <what>` in place. -->

# Multi-agent LLM systems — field handbook

## Overview

Scope: task-solving LLM multi-agent systems (classical non-LLM MARL and societal simulation are different
literatures). The star is the SUBSTRATE below — a dated, source-anchored map of where the field stands mid-2026,
with an explicit do-not-redo list. The only lens is open questions; nothing here prescribes a direction. Every
[Sn] resolves to a verbatim quote in [SOURCES.md](SOURCES.md); date-sensitive figures live in [volatile.md](volatile.md).

## Organizing principles (how the field reasons)

- The newest synthesis organizes the field as the LIFE progression — Lay the capability foundation → Integrate
  through collaboration → Find faults through attribution → Evolve through self-improvement — with the F→E
  handoff as its named weak link [S2].
- The failure locus is coordination, not member capability: errors propagate across agents and interaction
  rounds, are hard to diagnose, and rarely feed back into structure [S2] [S1].
- The field's working null hypothesis is economic: token spend, not architecture, explains most performance
  variance, so any structural claim is judged against matched-compute aggregation [S3] [S7].
- That null now has a theory: at a fixed reasoning-token budget with perfect context use, a single agent is more
  information-efficient (Data Processing Inequality — each handoff can only lose information); MAS is predicted
  competitive only where context use degrades or more compute is spent [S6].
- Verification is treated as easier than generation, so verifier count is a live test-time scaling axis [S15] —
  but self-evaluation without an external signal is known to fail and can degrade answers [S16].
- Inter-agent natural language is a chosen tradeoff, not a given: interpretable and overseeable, but argued
  structurally misaligned with the vector spaces models compute in (information loss, behavioral drift) [S18].

## Frontier (recency-weighted)

### Structure vs matched compute (weight-capped here — the saturated core, see repeller)

- First systematic multi-agent-debate evaluation (5 MAD methods × 9 benchmarks × 4 models): MAD often fails to
  beat single-agent CoT / Self-Consistency even at much higher inference compute; the one robust lever found is
  model heterogeneity, named a universal antidote [S7] (2025-02, rev 2025-06).
- The critique now has a theory, not just benchmarks: the Data Processing Inequality argument predicts exactly
  when MAS becomes competitive — degraded single-agent context use, or extra compute [S6] (2026-04).

### Topology & orchestration

- Adaptive/learned MAS optimized per-benchmark show "topological overfitting" (no cross-domain transfer) and
  "illusory coordination" (surface accuracy while interactions diverge from intended behavior) [S9] (2026-04).
- Live counter-current: task-adaptive topology routing (parallel / sequential / hierarchical / hybrid per task)
  reports 12–23% over static single-topology baselines at identical models — single-author preprint, directly
  clashing with [S9]; see Open questions [S10] (2026-02).

### Failure, attribution & repair

- MAST is the field's failure instrument — exact figures (commonly mis-recalled): taxonomy built from 150 traces
  (kappa = 0.88), 14 modes / 3 categories; MAST-Data = 1600+ annotated traces, 7 frameworks [S1] (2025-03, rev 2025-10).
- Failure attribution (which agent, which step) is formalized and benchmarked — and far from solved: the best
  automated method reaches 53.5% (Who&When, ICML 2025 Spotlight) [S12] (2025-04).
- Verifier/critic agents act with a DELAY, so false claims propagate before correction — yielding instability
  thresholds and optimal corrector placement (single-author preprint) [S13] (2026-06).
- E-stage methods arriving: TPGO treats the MAS as a graph of optimizable nodes and derives textual feedback
  from execution traces to pinpoint failures and suggest granular edits [S14] (2026-04).

### Communication & interop

- The latent-communication thread passes continuous hidden states between agents on the premise that
  downsampling thought to discrete tokens loses information — a heavily occupied lane [S17] (2025-11).
- Protocol scope split a reviewer expects you to know: MCP = model↔tools/data (a single open standard replacing
  per-source connectors); A2A = agent↔agent, explicitly complementary to MCP [S4] (2024-11) · [S5] (2025-04).

### Evaluation & economics

- MAS eval has moved past final accuracy: MultiAgentBench (ACL 2025) scores collaboration quality with
  milestone-based KPIs and compares coordination protocols (star / chain / tree / graph) [S20] (2025-03).
- First independent (non-vendor) cost-accuracy Pareto: over 4 orchestration patterns × 5 LLMs on 10,000
  financial documents, reflexive tops F1 (0.943) at 2.3× cost; hierarchical supervisor-worker sits on the
  Pareto frontier (F1 0.921 at 1.4×) [S21] (2026-03).

## Recent (~1–2 yr, compressed)

- Multi-Agent Verification: scale the NUMBER of off-the-shelf aspect verifiers (binary approve/reject, no
  training) as the test-time axis — verification, not more debate rounds [S15] (2025-02).
- The two production-craft poles, both vendor-staked (2025-06): Cognition — reliability = context engineering on
  ONE thread [S19]; Anthropic — MAS pays off on parallel-heavy, context-exceeding, tool-heavy tasks at ~15× token cost [S3].
- Position line naming the comms tension: NL is structurally misaligned with LLM vector spaces —
  interpretability bought at an information cost [S18] (2025-06).

## Durable core (the few foundations that still hold)

- Du et al. 2023 — the founding "debate improves reasoning" result; the baseline the skeptic line attacks [S23].
- Mixture-of-Agents — layered aggregation, each layer reads all prior-layer outputs; 65.1 vs 57.5 (GPT-4 Omni)
  on AlpacaEval 2.0 — read as aggregation until cost-matched [S22].
- MetaGPT — canonical role-crew/SOP assembly line; the hand-designed baseline learned methods must beat [S24].
- LLMs cannot reliably self-correct reasoning without external feedback (ICLR 2024) [S16].
- ADAS — the learned-topology transfer CLAIM (a meta agent programs new agents in code; claims cross-domain
  robustness) — now directly contested, see Open questions [S11].
- "More Agents Is All You Need" — agent-count scaling via sampling-and-voting; reread today as self-consistency [S25].

## Already crowded — go ELSEWHERE (do-not-redo)

The blank space is NOT in these lanes; each is saturated through H1-2026:

- Compute-matched "does MAS beat a single agent per $": benchmark wave + DPI theory + newest entrant showing
  auto-generated MAS underperform CoT-SC at up to 10× the cost — the field's loudest thread [S6] [S8].
- Adaptive/learned topology AND its rebuttal: both the method line and the "topological overfitting / illusory
  coordination" critique are published [S10] [S9].
- Failure attribution (which agent/step): named benchmark plus a dense 2026 follow-on wave [S12].
- Latent / vector inter-agent communication (hidden-state, KV-cache variants) — already has a unifying survey [S17].
- Self-evolving / self-improving MAS: dense H1-2026 wave of frameworks that learn to evolve from execution
  feedback, plus a dedicated survey [S14].
- Building new interop protocols: MCP + A2A are standardized, vendor-backed, foundation-governed — compose on
  them instead of proposing another [S4] [S5].

## Open questions the field hasn't answered (the whole lens — the reader answers in their own way)

1. Once inference compute, sample aggregation, and context-window relief are controlled, what residual — if
   any — do the agentic ingredients (roles, personas, turn-taking, inter-agent dialogue) contribute, and on
   which task families? The theory predicts MAS wins only under degraded context use or extra compute [S6] [S7];
   no result yet isolates the residual itself.
2. What makes a critique or verification signal genuinely EXTERNAL? Self-correction fails without external
   feedback [S16], task verification is one of MAST's three failure categories [S1] — so does a same-family
   peer critic count as external, and where exactly is the boundary?
3. Same object, opposite 2026 verdicts: task-adaptive topology reports +12–23% at identical models [S10], while
   independent evaluation finds adaptive MAS overfit topologically with illusory coordination [S9], and the
   claimed cross-domain transfer of searched designs [S11] is measured as no advantage over CoT-SC [S8]. Under
   what conditions does learned structure transfer, and what evaluation separates real coordination from
   surface accuracy?
4. Why do diagnosed failures rarely translate into structural self-improvement [S2]? Attribution is benchmarked
   (best 53.5% [S12]) and typed blame signals exist [S1] — what is missing between a localized, typed fault and
   a safe structural change (the survey's own closed-loop agenda [S2])?
5. Can MAS reliability be predicted before running rather than measured after? Error propagation is the named
   failure locus [S2], delay effects already yield instability thresholds and corrector-placement results [S13],
   and a 1600+-trace corpus exists to fit against [S1] — yet there is no compositional account mapping
   per-agent error rates + topology to system reliability.
6. Is model-pool heterogeneity the actual mechanism behind reported multi-agent gains? It is the quoted
   "universal antidote" and the named reopening condition for the buried debate line [S7] — would a
   matched-compute heterogeneous pool beat self-consistency over the single best model?

## What counts as DEEP here (taste)

| Naive move | Expert judgment/move | Why (failure prevented) | tier | src |
|---|---|---|---|---|
| Ship another MAS framework: +X% on one benchmark, unmatched compute, no failure analysis | The rewarded move is a reusable diagnostic instrument — MAST, "the first Multi-Agent System Failure Taxonomy"; recognition = independent adoption (IBM applied it to turn raw ITBench traces into structured failure signatures) | problematizes-nothing — the field's own critique names weak baselines / limited coverage as the incremental signature | L·B | [S1] [S26] [S7] |
| Homogeneous multi-agent debate as a reasoning booster | Buried (2025-02→06): MAD often loses to CoT/Self-Consistency at higher compute. Reopening condition, per the same paper: model-heterogeneous pools at matched compute | dead-end | L | [S7] |
| Intrinsic self-correction — an agent repairing its own reasoning with no external signal | Buried (2023-10, ICLR 2024): performance can even degrade after self-correction. Reopens only with an external correction signal (tools, execution, ground truth); whether a same-family peer counts is unresolved | dead-end | L | [S16] |
| "More homogeneous agents = collaboration advance" (agent-count scaling) | Buried: the effect is sampling-and-voting — reproducible by self-consistency, and single-agent is information-optimal at matched budget. Reopens if structured, communicating agents beat a matched-token aggregation-only arm | dead-end | L | [S25] [S7] [S6] |

Science-vs-application, as this field draws it: the science bar is a matched-compute, failure-analyzed,
mechanism-attributing claim (the critique's demand to rethink evaluation and stop overvaluing MAD as-is [S7]);
a working framework with a headline delta and no failure analysis is application-tier [S7] [S1].

## Critical rules (execution · eval · validity)

| Naive move | Expert judgment/move | Why (failure prevented) | tier | src |
|---|---|---|---|---|
| Compare the MAS against one weak single call, or at unmatched spend | Designing the comparison: equalize TOTAL tokens and $ across arms; report accuracy-vs-cost, expecting MAD-loses-to-CoT/SC as the outcome to beat | wrong-result — the gain may be purchased compute, not method | L | [S7] [S6] |
| Attribute a win to collaboration/structure directly | Before claiming structure: add a matched-token aggregation-only arm (same N samples + vote/judge, no roles or dialogue); structure must beat THAT | wrong-result — aggregation alone reproduces debate-like gains | L | [S7] [S25] |
| Mix model pools freely, or test a single model | Choosing pools: run homogeneous and heterogeneous pools as an explicit factor — heterogeneity is the named confound and lever | wrong-result — pool diversity, not the mechanism, may carry the gain | L | [S7] |
| Report top-line accuracy only | Reporting: annotate traces against MAST (14 modes / 3 categories) and give the failure-mode distribution; add collaboration/process metrics, not just completion | wasted-cost — unactionable eval; reads incremental in 2026 | L | [S1] [S20] |
| Claim MAS superiority in general | Writing the claim: scope to the predicted-win regime (degraded single-agent context use, or more compute [S6]; value covering ~15× tokens [S3]) and name where it should NOT help (shared-context work) | wrong-result — overclaim against the known boundary invites the skeptic line | L·B·C | [S6] [S3] [S19] |
| Review a "new MAS framework" on its own terms | Reviewing: map it onto the settled canon — debate, MoA/voting, role-crews, learned topology search — and demand the explicit delta vs the nearest | wrong-result — re-skins ship as novel | L | [S23] [S22] [S24] [S11] |

## Decision guide

- Shared-context, dependency-dense work (most coding): single thread + context engineering is the
  production-proven pole [S19]; go multi-agent where single-agent context use degrades or more compute is
  justified [S6] and task value covers ~15× tokens [S3]. Both poles are vendor-staked — see SOURCES.
- Picking an orchestration pattern under a budget: the one independent Pareto study puts hierarchical
  supervisor-worker on the cost-accuracy frontier (F1 0.921 at 1.4×), reflexive best-but-2.3× — scoped to
  financial-document extraction [S21].
- Spending test-time compute: verifier COUNT is a demonstrated scaling axis [S15]; more debate rounds is not
  [S7]; a critique signal must be external to count [S16].
- Verifier placement: verification acts with delay, so false claims propagate before correction —
  placement/timing, not mere presence, is the lever (single-author framing) [S13].
- Interop plumbing: MCP for model↔tools/data, A2A for agent↔agent — explicitly complementary; pick by scope
  rather than conflating them [S4] [S5].

## Ground rules (known-lane — terse)

- MAS ≈ 15× chat tokens; token usage alone ≈ 80% of variance — vendor-internal, single-origin figures [S3].
- Settled canon a novelty claim must clear: multi-agent debate [S23] · MoA / layered aggregation [S22] ·
  role-crews / SOP pipelines [S24] · learned topology search [S11].
- MAST's three failure categories: system design issues · inter-agent misalignment · task verification [S1].
- MoA's 65.1 vs 57.5 (AlpacaEval 2.0) is an aggregation result — cost-match before citing it as a multi-agent win [S22].

## Reference documentation

- **[volatile.md](volatile.md)** — every date/version-sensitive figure above (trace counts, SOTA numbers,
  cost anchors, the crowded list's shelf life); re-check before relying on any number.
- **[SOURCES.md](SOURCES.md)** — provenance: every [Sn] with tier, reliable-for scope, and verbatim quote.

## Candidate lane  ⚠️ (expert to resolve — NOT verified)

- ⚠️ "Attribution→repair is now tractable" is INFERRED, not quoted: typed blame signals + a 1600+-trace corpus
  exist [S1] and the survey names the F→E gap and a closed-loop agenda [S2], but no fetched source states the
  repair loop is newly enabled; known E-stage work optimizes orchestration rather than closing
  attribution-driven, non-regression-verified repair. Confirm: a 2026 paper citing attribution artifacts as its
  enabler and verifying non-regression. Refute: such a paper exists → treat this lane as crowded too.
- ⚠️ "Compositional reliability theory is uncrowded" rests on a single scan: adjacent work exists (delay /
  instability thresholds [S13]) but no per-agent-error→system-reliability composition theory was found — low
  confidence. Confirm or refute with a fresh search for a MAS reliability-calculus paper before investing.
- ⚠️ Taste anchor is substituted: the DEEP exemplar's award/meta-review rationale was not recoverable (review
  page access-gated), so the taste row rests on adoption-by-reference (IBM applying MAST [S26]) rather than a
  committee rationale. Confirm: recover the venue meta-review or an equivalent award rationale and check it
  names the same separating cue.
```

### [4] SKILL-INPUT — aii-web-tools · 2026-08-01 15:26:55 UTC

The agent loaded the **aii-web-tools** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-web-tools
description: "Web research toolkit: web search (Serper/Google), web page fetch as markdown (HTML and PDF), and regex grep over full page/PDF text. Use whenever a task needs to search the web, read a page, mine a paper/PDF, verify citations, or extract exact quotes, numbers, or methodology from a URL."
---

## Web tools

You have three web capabilities: **search**, **fetch**, and **grep** (exact
regex extraction over a full page or PDF).

**Pick where they come from, in this order:**

1. **If you have built-in `WebSearch` / `WebFetch` tools, PREFER those over the
   scripts below.** They may be **deferred tools** (listed by name but with
   schemas not yet loaded) — if so, call `ToolSearch("select:WebSearch,WebFetch")`
   ONCE to load them, then use them normally. Do not skip them just because they
   need that one extra load step; they are the preferred path. Pair them with the
   `aii_web_tools__fetch_grep` script below when you need exact text / numbers /
   methodology that a summary would miss, or when reading a PDF.
2. **Only if you have NO built-in `WebSearch` / `WebFetch`** (e.g. the OpenHands
   backend), use the scripts in this skill (below). They are our own
   implementations — Serper.dev for search, html2text + PyMuPDF for fetch, and
   regex grep over the full document text. They work without any built-in web
   tools.

Workflow either way: **search** (discover) → **fetch** (read for the gist) →
**grep** (pull exact details / read PDFs).

---

## Running the scripts

Run every script with the skill's pre-provisioned interpreter (it already has
`requests`, `html2text`, `pymupdf`, `python-dotenv`). Set `PY` once:

```bash
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-web-tools"
export PY="$SKILL_DIR/../.ability_client_venv/bin/python"
```

### 1. Search the web (Serper.dev / Google)

```bash
$PY "$SKILL_DIR/scripts/aii_fast_web_search.py" --query "neuro-symbolic FOL translation LLM" --max-results 10
```

Returns ranked title / URL / snippet lines. Use it first to scan the
landscape; snippets are for discovery only — fetch a page before judging it.

### 2. Fetch a page as markdown (HTML or PDF)

```bash
$PY "$SKILL_DIR/scripts/aii_fast_web_fetch.py" fetch --url "https://arxiv.org/abs/2303.11366" --max-chars 10000
```

`--max-chars` caps output (default 10000); `--char-offset N` pages further in.
Handles PDFs transparently via PyMuPDF.

### 3. Grep a page or PDF (exact regex extraction)

```bash
$PY "$SKILL_DIR/scripts/aii_fast_web_fetch.py" grep --url "https://arxiv.org/pdf/2303.11366" --pattern "verbal reinforcement" --max-matches 20 --context-chars 200
```

Returns only the matching sections with surrounding context — the right tool
for exact numbers, table values, methodology, or long PDFs where a summary
would lose the detail. `-i` for case-insensitive.

**Parallelize** independent searches/fetches in one turn; only sequence a
fetch after the search that produced its URL.

---

## Notes

- The scripts call our ability server. If a script prints
  `Ability service not available`, the server is down — say so rather than
  silently improvising a different search method.
- Do **not** hand-roll your own `requests`/scraping for search when these
  tools are available: Serper returns clean Google results and the fetch/grep
  scripts already handle HTML, PDFs, and encoding.
````
