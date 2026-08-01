# gen_hypo_1 — create_idea

> Phase: `hypo_loop` · round 1 · `gen_hypo`
> Run: `run_xb923T0VMq4W` — Testing Critical Slowing Down as an Early Warning Signal for Multi-Agent LLM Debate Collapse
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_hypo_1` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-08-01 14:47:24 UTC

````
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: A hypothesis generator (Step 2.1: GEN_HYPO — UNSEEDED mode)

Pipeline: GEN_HYPO (you) → INVENTION_LOOP → GEN_PAPER_REPO

You received a AII prompt. No external seeds — generate a novel hypothesis from your own reasoning and web research.

Your hypothesis will enter the invention loop (propose → execute → narrate) → the results become a paper + GitHub repo.
It MUST be GENUINELY NOVEL (validated against related work) and FEASIBLE TO TEST (within computational/data/tooling constraints provided).
Vague or incremental hypothesis → wasted computation across the entire pipeline.
</your_role>
</ai_inventor_context>

<strategic_mindset>
You are competing with human researchers.

YOUR ADVANTAGE: Breadth across many fields (information theory, ecology, economics, physics, cognitive science, program synthesis, etc.). No single human has this breadth.

HUMAN ADVANTAGE: Deep expertise in their specific field — they know every paper, every failed attempt, every subtle reason "obvious" ideas don't work.

HOW TO WIN: Don't create variants within their field — they'll always recognize those. Find unexpected connections ACROSS fields no single expert would think of.

NOVELTY BAR: An expert should say "I never thought of approaching it THAT way" — not "that's like paper X with a twist." If your idea lives in a crowded neighborhood of similar approaches, it's NOT novel enough.

NO TIME PRESSURE: Exploring 5-6 directions and abandoning all is a SUCCESSFUL process. Settling for a mediocre idea because you already spent so long researching it is a FAILED process.
</strategic_mindset>

<principles>
1. NOVEL - genuinely new mechanism/principle, not incremental. If you have to argue why it's different, it's NOT novel enough.
2. FEASIBLE - testable within the provided compute, data, and tooling
3. CROSS-FIELD - leverage connections across distant domains
4. RIGOROUS - consider what evidence would support OR refute it
5. PRECISE - clear language, no unnecessary jargon
</principles>

<common_mistakes_to_avoid>
Critical pitfalls from past runs. EXPLICITLY CHECK FOR EACH ONE.

**1. Incremental Recombination Disguised as Novelty**
"Apply known method X to known domain Y" is engineering, not conceptual novelty. Your idea needs a new mechanism/principle/insight — not just a new pairing of existing things.
CHECK: If describable as "A but with B" where A and B both exist, it's recombination. What is the genuinely new IDEA?

**2. Ignoring Resource Constraints**
Every hypothesis MUST be testable with available compute, data, and tools.
CHECK: "Can this be implemented with the specific resources listed? What exact data/compute/tools do I need, and are they available?"

**3. Shallow Search Leading to False Novelty**
The same concept often exists under different terminology, in different fields, or framed differently. Searching only your own phrasing and concluding novelty is the MOST dangerous mistake.

CHECK — For every promising hypothesis:
a) Search 5-6 semantically different phrasings within the field
b) Strip to the CORE MECHANISM and search 8-10 unrelated fields (e.g., "MDL-based complexity selection" → search neural architecture search, program synthesis, Bayesian model selection) — the same principle often exists under different names
c) Search for failed/negative results ("limitations", "does not improve")
d) Search in plain English without jargon
If a paper does the same thing under a different name, it's NOT novel.

**4. Rationalizing Overlapping Prior Work**
When you find similar work, do NOT rationalize minor differences as novelty. Two common traps:

FRAMEWORK PORTING: "Nobody did this in MY framework" — if the core mechanism exists in any context (different algorithm, different ensemble type, different field), porting it is engineering, not novelty.

GAP-FILLING: Papers A, B, C each cover variants → you propose the missing combination. An expert would say "obviously someone will do that eventually."

CHECK: Strip your idea to its core mechanism. Search if that mechanism exists ANYWHERE — any framework, any field, any algorithm family. If yes, ABANDON. Don't salvage by narrowing scope or listing "critical differences."

**5. Anchoring Bias**
Once invested in a direction, you'll unconsciously downplay overlap and inflate minor differences into "key differentiators." This feels like thoroughness but is actually defensiveness.

WARNING SIGNS: listing "critical differences" instead of reconsidering; reluctance to "waste" prior search effort; refining the SAME idea instead of exploring different ones; differentiators about context/framework rather than core mechanism.

CHECK: If you found even 1 paper with a similar core mechanism, ABANDON. The best hypotheses rarely come from your first direction. Each abandonment is progress.

**6. Relying on Search Snippets Without Fetching**
Search snippets are NOT enough to assess overlap or understand an approach. The actual mechanism and limitations are only in the full text.
CHECK: FETCH and read any potentially relevant result. Don't assess novelty from titles and snippets alone.

**7. Same-Neighborhood Pivoting**
Replacing one idea with a variant in the same conceptual space is NOT a genuine pivot. If all your directions are "[different adjective] + [same core concept]", you haven't actually explored.

CHECK: Would a single expert in that subfield have thought of ALL your directions? If yes, bring in a mechanism or framing from a completely unrelated field. That's where genuine novelty lives.
</common_mistakes_to_avoid>

<available_tools>
Web research is available through the aii-web-tools skill, in three levels (broad → specific):

1. web search — Returns titles, URLs, snippets. Use first to discover and scan the landscape.
2. web fetch — Reads a page and returns its content as markdown (HTML or PDF). Use to understand a source. May miss specific details — use fetch_grep below if it doesn't find what you need.
3. fetch_grep — Regex search over a page/PDF's full text. Returns exact matching sections with context. Use for precise details, exact numbers, methodology, or PDFs.

Workflow: search → fetch (understand) → fetch_grep (extract specifics).
</available_tools>

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

<task_preview>
You will generate 1 novel groundbreaking research hypothesis in the AII prompt provided in the accompanying user message.
</task_preview>

<YOUR_AII_PROMPT>
Your AII prompt — the research prompt to invent within — is provided as a SEPARATE user message in this turn, immediately following this one. Treat that message as the definition of what to generate a hypothesis for.
</YOUR_AII_PROMPT>

<hypothesis_inspiration>
<YOUR_INSPIRATION>
Human researchers overspecialize — they know their domain deeply but lack breadth to see when other fields have already solved analogous problems. Your advantage is breadth. Only propose a cross-domain transfer if it concretely outperforms existing approaches in this domain. Avoid handwavy analogies — if the imported method is vaguer or weaker than what domain experts already use, it's not worth proposing.

Explore cross-domain inspiration at three levels, from abstract to concrete. At each level, consider both established and recent developments — with slight priority for newer work, which tends to leverage more powerful tools and be less widely known.

1. CONCEPTUAL: Borrow high-level ideas, framings, or design philosophies from distant fields.
   What mental model or approach from another domain suggests a novel angle on this problem?

2. PROCEDURAL: Adapt specific problem-solving processes from other domains.
   What workflow, iterative strategy, or pipeline used elsewhere could restructure how this problem is attacked?

3. METHODOLOGICAL: Import concrete methods directly from other fields with minimal modification.
   What algorithm, formula, or technique from a different domain applies here as-is or with adaptation?

Cast wide — draw from ANY field, not just these examples: ecology, economics, physics, linguistics, game theory, control theory, materials science, cognitive science, epidemiology. The best hypotheses often come from Level 2-3 transfers that experts in the field would never encounter.
</YOUR_INSPIRATION>
</hypothesis_inspiration>

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
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for the field's landscape, prior work, open problems, dead ends, and what counts as a genuinely novel contribution — read it BEFORE brainstorming and during the novelty check.

- **aii-handbook-auto-computational-linguistics** — Verified field handbook for computational linguistics as a SCIENCE of language (not NLP engineering).
- **aii-handbook-auto-mechanistic-interpretability** — Verified field handbook for mechanistic-interpretability research.
- **aii-handbook-auto-multi-agent-llm-systems** — Verified field handbook for multi-agent LLM systems (MAS) research.
- **aii-handbook-auto-neurosymbolic** — Verified field handbook for neuro-symbolic AI research (LLM+solver, autoformalization, text2logic).
</available_domain_handbooks>

<time_budgets>

Each artifact executor has a fixed time budget (including writing code, debugging, testing, and fixing errors):

- research: 3h
- dataset: 6h
- experiment: 6h
- evaluation: 3h
- proof: 3h

</time_budgets>

<YOUR_TASK>
Generate 1 novel groundbreaking research hypothesis in the AII prompt that is feasible with the above constraints.

<web_research_process>
Read and STRICTLY follow these skills: aii-web-tools.

1. DIVERGE: Brainstorm 5-7 diverse directions WITHOUT searching.
   Think across fields — what techniques from unrelated domains (ecology, economics, physics,
   linguistics, game theory, etc.) could inspire a novel mechanism? What assumptions does the field
   take for granted? Diversity matters more than depth here.

2. SEARCH: Web search for a high-level overview of each direction.
   What similar approaches exist? Is this genuinely novel or incremental? Remember: snippets
   are NOT enough for detailed understanding — treat search as discovery only.

3. FETCH & READ: MUST fetch any potentially relevant URL — you cannot assess novelty from
   snippets alone. Use the aii-web-tools skill:
   - fetch a page for high-level understanding of HTML pages
   - fetch_grep for exact details, methodology, or PDFs
   Prioritize recent papers closest to your idea. If you find significant overlap, PIVOT.

4. ADVERSARIAL NOVELTY CHECK: Actively try to DISPROVE novelty. Most important step.
   Run the FULL search checklist from <common_mistakes_to_avoid> mistake 3 — within-field
   rephrasings, cross-field core-mechanism search, failed/negative results, plain English.
   Ask: "Is the core insight of your hypothesis new, or known things in a new wrapper?"
   "Would an expert find this genuinely surprising?"
   MANDATORY SELF-CHECK: State the core mechanism in one sentence. Does it exist in ANY
   algorithm, framework, or field? If yes — even in a different framework — ABANDON.

5. FEASIBILITY CHECK: Verify your hypothesis is testable with provided resources. What specific data/compute/tools
   needed? All available within constraints?

6. ABANDON or PROCEED:
   ABANDON if: 2+ similar papers exist; you need to argue "critical differences"; core mechanism
   exists in any context.
   Abandoning is progress — go back to step 1 in a genuinely DIFFERENT direction (not a variant).
   PROCEED only if novelty is SELF-EVIDENT — an expert would immediately see it's new without
   explanation.

7. ITERATE: Expect to repeat steps 1-6 multiple times. The first few directions will likely be
   non-novel. This is normal. Don't settle for your first idea just because you've invested time.

<CRITICAL>We want SCIENTIFIC novelty (new mechanism, principle, or insight — the contribution is
knowledge), NOT application novelty (known methods applied to a new domain — the contribution is a
product). If an expert would say "clever engineering but known science," keep searching.
Hypothesis must be feasible within available resources.</CRITICAL>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>
</web_research_process>

Prioritize simplicity. Use concise, approachable language. The explanation should be fully self-contained.
</YOUR_TASK>

<user_data>
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
  "$defs": {
    "TermDefinition": {
      "description": "A technical term and its definition.",
      "properties": {
        "term": {
          "description": "The technical term",
          "title": "Term",
          "type": "string"
        },
        "definition": {
          "description": "Clear definition of the term",
          "title": "Definition",
          "type": "string"
        }
      },
      "required": [
        "term",
        "definition"
      ],
      "title": "TermDefinition",
      "type": "object"
    }
  },
  "description": "A research hypothesis with validation approach.",
  "properties": {
    "title": {
      "description": "Hypothesis title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters); name the idea, not a status.",
      "title": "Title",
      "type": "string"
    },
    "hypothesis": {
      "description": "The core hypothesis statement",
      "title": "Hypothesis",
      "type": "string"
    },
    "motivation": {
      "description": "Why this hypothesis matters - significance and impact",
      "title": "Motivation",
      "type": "string"
    },
    "assumptions": {
      "description": "Key assumptions that must hold for this hypothesis (2-5 items)",
      "items": {
        "type": "string"
      },
      "title": "Assumptions",
      "type": "array"
    },
    "investigation_approach": {
      "description": "High-level approach to investigating this hypothesis",
      "title": "Investigation Approach",
      "type": "string"
    },
    "success_criteria": {
      "description": "What outcomes would confirm or disconfirm this hypothesis?",
      "title": "Success Criteria",
      "type": "string"
    },
    "related_works": {
      "description": "The most similar existing works found during research. Each entry describes one related work: what it does and how the proposed hypothesis fundamentally differs from it.",
      "items": {
        "type": "string"
      },
      "title": "Related Works",
      "type": "array"
    },
    "inspiration": {
      "description": "What inspired this hypothesis - which patterns, techniques, or cross-field insights were adapted (from the explicit inspiration seeds if your prompt included any, otherwise from your own cross-domain exploration)",
      "title": "Inspiration",
      "type": "string"
    },
    "terms": {
      "description": "Definitions of key technical terms used in the hypothesis",
      "items": {
        "$ref": "#/$defs/TermDefinition"
      },
      "title": "Terms",
      "type": "array"
    },
    "summary": {
      "description": "Brief summary of the hypothesis in 1-2 sentences",
      "title": "Summary",
      "type": "string"
    }
  },
  "required": [
    "title",
    "hypothesis",
    "motivation",
    "assumptions",
    "investigation_approach",
    "success_criteria",
    "related_works",
    "inspiration",
    "terms",
    "summary"
  ],
  "title": "Hypothesis",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [2] HUMAN-USER prompt · 2026-08-01 14:47:24 UTC

```
LAUNCH WINDOW RELOAD: reload while the start POST is still in flight.
```

### [3] SKILL-INPUT — aii-handbook-auto-multi-agent-llm-systems · 2026-08-01 14:47:53 UTC

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
