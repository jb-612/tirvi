---
name: re-architect-research
description: Clean-slate architecture research for brownfield modernization. Evaluates open-source alternatives, design patterns, and build-vs-adopt decisions using multi-agent research teams with adversary debate. Part of the Brownfield Refactoring Toolkit.
argument-hint: "<project-root or reverse-prd-path>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, WebSearch, WebFetch
---

# Re-Architect Research — Clean-Slate Evaluation for Brownfield Modernization

Evaluate architecture alternatives for the project at `$ARGUMENTS`.

## Purpose

Before refactoring a brownfield codebase, this skill answers the fundamental
question: **should we refactor the existing code, replace it with open-source
alternatives, or build something new?**

It approaches the problem as a **clean-slate architecture evaluation** — as if
a team of architects needs to design the solution from scratch, using the
existing codebase and its reverse-engineered PRD only as requirements input.

## Prerequisites

- **Reverse PRD** exists (from `reverse-prd` skill) — product intent documented
- **ACM ingested** — code structure mapped in knowledge graph
- **Behavioral spec** exists (from `sweep-analytics`) — runtime behavior documented
- **Test suite** in place — characterization tests pin current behavior

## Methodology: 8-Step Research Process

### Step 1: Understand Product Intent (Clean Slate)

Read the reverse PRD and behavioral spec as if they were a requirements document
for a greenfield project. Forget the current implementation exists.

**Extract:**
- Core product capabilities (what must it do?)
- User personas and workflows (who uses it and how?)
- Quality attributes (performance, scalability, reliability, security)
- Integration requirements (what external systems must it connect to?)
- Constraints (deployment model, team size, budget, timeline)

**Output:** `docs/research/re-architect/00-product-requirements.md`

### Step 1b: Surface Hidden Assumptions

Before defining clusters, explicitly list the assumptions baked into the current
architecture. These often hide migration costs and scope risks.

**Extract from the reverse PRD and codebase:**
- Technology commitments (e.g., "SQLite is the only database", "Python 3.11+")
- Deployment assumptions (e.g., "runs on a single Mac", "no Docker")
- Scale assumptions (e.g., "8 agents max", "single user")
- Integration assumptions (e.g., "MCP is the integration layer", "launchd for scheduling")

**For each assumption, ask:**
- Is this a hard constraint or a legacy choice?
- Does this assumption limit which alternatives are viable?
- What would change if we removed this assumption?

Present the assumption list to the user. Ask them to confirm which are hard
constraints vs negotiable before research agents waste cycles evaluating
incompatible options.

**Output:** Add assumptions section to `docs/research/re-architect/00-product-requirements.md`

### Step 2: Define Research Clusters

Group the product capabilities into architectural domains. Each cluster gets
its own research agent. Typical clusters for a multi-agent orchestration platform:

| Cluster | Domain | Key Questions |
|---------|--------|---------------|
| A | Agent Orchestration & Dispatch | How to schedule, dispatch, and coordinate AI agents? |
| B | Communication & Integration | How to connect Slack, Teams, email, WhatsApp? |
| C | Knowledge Management & RAG | How to manage Brain/, Memory/, semantic search? |
| D | Dashboard & Observability | How to build the operational dashboard and monitoring? |
| E | Task & Workflow Management | How to manage Todoist-like task lifecycle? |
| F | Testing & Quality | How to test agentic systems (evals, behavioral testing)? |

**For each cluster, specify:**
- What the cluster must accomplish (from Step 1 requirements)
- Candidate open-source projects and libraries to evaluate
- Evaluation criteria (see Step 2b below)
- Links to explore (see Reference Resources section)

**Output:** `docs/research/re-architect/01-research-clusters.md`

### Step 2b: Research Agent Instructions Template

Each research agent receives these detailed instructions:

```
You are researching Cluster [X]: [Domain Name].

## Product Requirements for This Cluster
[Extracted from Step 1 — what must this cluster accomplish?]

## Candidate Solutions to Evaluate
[List of specific GitHub repos, libraries, frameworks]

## Evaluation Criteria
For each candidate, assess:

1. **Functional fit** (0-10): Does it solve the core problem?
   - Which requirements does it cover? Which gaps remain?
   - Does it handle our scale (8 agents, 25+ integrations, SQLite backend)?

2. **Maturity** (0-10): Is it production-ready?
   - GitHub stars, contributors, release cadence, issue resolution time
   - Documentation quality, examples, community support
   - Breaking change history (stability)

3. **Integration effort** (0-10, inverted — 10 = easiest):
   - How much glue code to integrate with our stack?
   - Does it require replacing infrastructure (DB, message queue)?
   - Can it be adopted incrementally or is it all-or-nothing?

4. **Maintenance burden** (0-10, inverted — 10 = lowest burden):
   - How much ongoing maintenance to keep it working?
   - Vendor lock-in risk? Single-maintainer risk?
   - License compatibility (Apache 2.0, MIT preferred)

5. **Build-vs-adopt score**:
   - ADOPT: Use as-is or with minor configuration
   - ADAPT: Fork or extend to fit our needs
   - BUILD: Write custom code (the existing approach)
   - COMPLEMENT: Use alongside existing code

## Research Depth
- Read the README, architecture docs, and key source files
- Search for production case studies and comparisons
- Check alternatives and competitors
- Note any showstoppers (license, Python version, platform)

## Output Format
For each candidate:
- Name, URL, stars, license, last commit
- Functional fit assessment (which requirements covered)
- Integration analysis (what changes needed)
- Risks and showstoppers
- Verdict: ADOPT / ADAPT / BUILD / COMPLEMENT / REJECT

## Confidence
If your confidence in any assessment is below 95%, formulate a specific
question for the user and include it in your output under "Questions for User".
```

### Step 3: Execute Parallel Research

Launch research agents — one per cluster, running in parallel via `TeamCreate`:

```
TeamCreate("re-architect-research")
Agent(name="cluster-a", mode="acceptEdits", prompt="Research Cluster A: Agent Orchestration...")
Agent(name="cluster-b", mode="acceptEdits", prompt="Research Cluster B: Communication...")
Agent(name="cluster-c", mode="acceptEdits", prompt="Research Cluster C: Knowledge Management...")
Agent(name="cluster-d", mode="acceptEdits", prompt="Research Cluster D: Dashboard...")
Agent(name="cluster-e", mode="acceptEdits", prompt="Research Cluster E: Task Management...")
Agent(name="cluster-f", mode="acceptEdits", prompt="Research Cluster F: Testing & Quality...")
```

Each agent writes its findings to:
`docs/research/re-architect/cluster-{letter}-{domain}.md`

### Step 4: Synthesize and Cross-Reference

After all agents complete, the team lead synthesizes:

1. **Overlap analysis** — Which candidates appear in multiple clusters?
   (e.g., LangGraph for both orchestration and workflow)
2. **Contradiction analysis** — Which candidates conflict?
   (e.g., using Qdrant for RAG means not using ACM's FalkorDB vectors)
3. **Complementary pairs** — Which candidates work well together?
4. **Redundancy check** — Which candidates solve the same problem differently?
5. **Preservation analysis** — What existing code/tools should we keep?
   (e.g., Obsidian Brain/, existing MCP servers, ACM itself)

6. **Evidence tie-back** — For each recommendation, trace which cluster agents
   and sources support or oppose it:

   ```markdown
   ## Evidence Tie-Back

   | Recommendation | Supporting Clusters | Opposing Clusters | Evidence Tier | Confidence |
   |----------------|---------------------|-------------------|---------------|------------|
   | Adopt LangGraph for orchestration | A (functional fit 9/10), E (workflow overlap) | D (dashboard lock-in risk) | T2 (case studies) | High |
   | Keep SQLite backend | C (sufficient at scale), D (dashboard reads) | A (concurrency limits) | T3 (team experience) | Medium |
   ```

   Recommendations backed by only one cluster should be flagged as "single-source".

**Output:** `docs/research/re-architect/02-synthesis.md`

### Step 5: Adversary Debate (3 Rounds)

Spawn an adversary agent that challenges the synthesis:

**Round 1 — Challenge assumptions:**
- "Why not just refactor the existing code instead of adopting X?"
- "What's the migration cost you're not accounting for?"
- "Is this premature optimization or genuine need?"

**Round 2 — Stress-test alternatives:**
- "What happens when library X breaks on upgrade?"
- "Is the community actually active or just stars?"
- "Show me a production deployment at our scale"

**Round 3 — Defend or revise:**
- Team lead responds to all challenges
- Revise recommendations where the adversary raised valid technical concerns
- Note unresolved debates for user decision

**Escalation thresholds:**
- If the adversary challenges a ADOPT verdict and the defense cannot cite a T1/T2
  production case study, downgrade to ADAPT or flag for user decision
- If the adversary identifies a migration cost >2x the original estimate, escalate:
  "Migration cost disputed — adversary estimates [X], synthesis estimates [Y].
  This is a resource decision for the user."
- If a cluster's top candidate has a single-maintainer risk and no fork strategy,
  the adversary's concern stands — note it in the risk register regardless of defense

**Output:** `docs/research/re-architect/03-adversary-debate.md`

### Step 6: Write Final Research Documents

**Per-cluster research docs** (detailed):
```
docs/research/re-architect/
├── 00-product-requirements.md    # Step 1 output
├── 01-research-clusters.md       # Step 2 output
├── cluster-a-orchestration.md    # Per-cluster analysis
├── cluster-b-communication.md
├── cluster-c-knowledge.md
├── cluster-d-dashboard.md
├── cluster-e-tasks.md
├── cluster-f-testing.md
├── 02-synthesis.md               # Cross-cluster analysis
├── 03-adversary-debate.md        # Challenge and defense
└── 04-conclusion.md              # Final recommendation
```

**Master conclusion doc** (`04-conclusion.md`):
- Recommended architecture (component diagram)
- Per-cluster verdict (ADOPT/ADAPT/BUILD/COMPLEMENT for each domain)
- **Confidence contract per verdict** — each verdict includes:
  - Confidence level (High/Medium/Low)
  - Evidence tier backing it (T1=production case study, T2=benchmark/comparison, T3=team experience, T4=vendor docs only)
  - Adversary status (defended/revised/unresolved)
  - Example: "Cluster A: ADOPT LangGraph — High confidence, T2 evidence, defended against adversary"
- Migration strategy (incremental path from current to target)
- Risk register (what could go wrong, mitigations)
- Critic's view (what the adversary still disagrees with)
- **Escalated decisions** — items where agents disagreed and the user must decide
- Research limitations (what we couldn't verify, assumptions made)
- Estimated effort per component

### Step 7: Generate Diagrams

Add Mermaid diagrams **only to the conclusion document**:
```
docs/diagrams/
├── re-architect-target.mmd       # Recommended target architecture
├── re-architect-migration.mmd    # Migration sequence from current to target
└── re-architect-components.mmd   # Component relationship with ADOPT/BUILD labels
```

### Step 8: ACM Indexing Decision (HITL)

Present the user with a list of research artifacts and ask which should be
indexed into ACM:

- Product requirements → ACM Requirements layer
- Architecture decisions → ACM Design layer
- Component evaluations → ACM Features layer

**HITL gate:** User approves which artifacts to ingest before running `acm ingest`.

## Confidence Protocol

At every step, every agent must self-assess confidence:

- **95-100%**: Proceed without asking
- **80-94%**: Note the uncertainty in the output, proceed
- **Below 80%**: STOP and ask the user a specific clarifying question

Questions should be concrete, not open-ended:
- BAD: "What do you think about the dashboard approach?"
- GOOD: "The dashboard cluster has two competing options: (A) keep vanilla JS + decompose the monolith, or (B) adopt Phoenix/Arize for observability. Your reverse PRD emphasizes real-time agent monitoring — does that imply you need the Arize-style observability features, or is the current dashboard's feature set sufficient if cleaned up?"

## Reference Resources

These are example starting points for research. Agents should expand beyond
these with their own web searches.

### Agent Orchestration & Dispatch
- https://github.com/langchain-ai/deepagents — LangChain deep agents
- https://github.com/BrainBlend-AI/atomic-agents — Atomic agents framework
- https://github.com/nousresearch/hermes-agent — Hermes agent
- https://github.com/coleam00/Archon — Archon agent framework
- https://github.com/block/goose — Block's Goose agent
- https://github.com/emcie-co/parlant — Parlant conversational agents
- https://github.com/topoteretes/cognee — Cognee cognitive framework
- https://github.com/pvolok/mprocs — Multi-process orchestration

### Knowledge Management & RAG
- https://github.com/pixeltable/pixeltable — PixelTable multimodal data
- https://github.com/qdrant/qdrant — Qdrant vector database
- https://github.com/onyx-dot-app/onyx — Onyx knowledge platform

### Search & Research
- https://github.com/BunsDev/Perplexica-Search-Engine-AI — Perplexica search
- https://github.com/karpathy/autoresearch — Karpathy's autoresearch loop
- https://github.com/ItzCrazyKns/Vane — Vane AI search

### Observability & Testing
- https://github.com/Arize-ai/phoenix — Arize Phoenix observability
- https://github.com/alexzhang13/rlm — RLM (RL for models)
- https://github.com/disler/claude-code-hooks-multi-agent-observability — Claude Code observability hooks

### Dashboard & UI
- https://github.com/simstudioai/sim — Sim Studio AI
- https://github.com/kitplummer/clikan — CLI Kanban board

### Skills & Workflow
- https://github.com/sickn33/antigravity-awesome-skills — Skills collection
- https://github.com/obra/superpowers — Superpowers agent patterns
- https://github.com/garrytan/gstack — GStack development patterns
- https://github.com/hardikpandya/stop-slop — Anti-slop quality patterns
- https://github.com/instructkr/claw-code — Claw code patterns

### Task & Project Management
- https://github.com/yohayetsion/product-org-os — Product Org OS
- https://github.com/katanemo/plano — Plano routing/workflow

### AI Infrastructure
- https://github.com/BerriAI/litellm — LiteLLM proxy (multi-model)
- https://github.com/browserbase/stagehand-python — Stagehand browser automation
- https://github.com/mcp-use/mcp-use — MCP client utilities
- https://github.com/paperclipai/paperclip — Paperclip AI
- https://github.com/toon-format/toon — Toon format
- https://www.minimax.io/news/minimax-m27-en — MiniMax M27 model
- https://www.augmentcode.com/product/intent — Augment Code intent understanding

### Agent Development Patterns
- https://github.com/disler/single-file-agents/tree/main/ai_docs — Single-file agent patterns
- https://docs.astral.sh/uv/#scripts — UV script patterns

### Additional User Resources
- https://drive.google.com/drive/folders/1VVrBKXFKy0NE8ZSsgdR6jcEyf4gql2L6 — Shared reference materials

## Integration with Brownfield Toolkit

This skill is the bridge between Phase 2 (characterization testing) and Phase 3
(refactoring). Its output directly feeds:

1. **Phase 3 refactoring plan** — which components to refactor vs replace
2. **ADR creation** — architectural decisions for each cluster
3. **ACM Design layer** — architecture decisions indexed for traceability
4. **Migration plan** — incremental path from current to target

## Quality Criteria

The research is complete when:
- Every cluster has a detailed analysis with 3+ candidates evaluated
- Every candidate has a quantified score (functional fit, maturity, integration, maintenance)
- Cross-cluster synthesis identifies overlaps, contradictions, and complementary pairs
- Adversary challenged and team defended (or revised) across 3 rounds
- Master conclusion has a clear recommendation per cluster
- Critic's view and research limitations are documented
- Diagrams show target architecture and migration path
- User has been asked about any decision where confidence was below 95%
