# Scholar-Loop — Full Project State Analysis
*Audit timestamp: 2026-07-14 04:00 IST*

---

## 1. Git State Summary

| Metric | Count |
|--------|-------|
| Committed `.md` notes | **247** |
| **Untracked** `.md` notes (new, not staged) | **97** |
| Total `.md` files on disk | **344** |
| Last commit | `63d5b8a` — *"add ml-ai notes (transformer, RL, NLP, CV+YOLO)"* |

**All 97 untracked files are valid additions** waiting to be committed. Nothing is in a broken half-state on disk, but the agent in production only sees the 247 committed files. The 97 new notes — including all 65 papers — are invisible to the GitHub Actions cron until you `git add && git commit`.

---

## 2. Critical Bugs Found

### 🔴 BUG 1: 17 notes have broken/missing YAML frontmatter — they will NEVER be properly picked

The agent picks notes by `post.metadata.get("topic")`. Files that use `## Frontmatter` as a markdown heading (instead of a YAML `---` block) get parsed as `topic=None, difficulty=None` by python-frontmatter.

**The 12 papers with `## Frontmatter` (prose-style, not YAML):**
```
paper-ai-layoff.md          paper-conductor.md        paper-datasets-hf.md
paper-energy-based-models   paper-ijepa.md            paper-leworldmodel.md
paper-neurosymbolic.md      paper-self-improving-code paper-spatial-claw.md
paper-sycophancy.md         paper-understanding-training  paper-vl-jepa.md
```

**Confirmed by parsing test:**
```
paper-ai-layoff.md:  topic=MISSING  difficulty=MISSING  ← BROKEN
paper-conductor.md:  topic=MISSING  difficulty=MISSING  ← BROKEN
paper-adam.md:       topic=papers   difficulty=hard     ✓
```

**5 more files with prose-style metadata (no YAML `---`):**
```
knowledge/system-design/system-design-fundamentals.md   (uses "**Difficulty:** medium" inline)
knowledge/system-design/ddia-distributed-systems.md     (uses "**Difficulty:** hard" inline)
knowledge/system-design/generative-ai-system-design.md
knowledge/system-design/ml-system-design.md
knowledge/fullstack/fastapi-for-ai.md
```

**Fix:** Convert all `## Frontmatter` / prose-style metadata to proper YAML `---` blocks with `topic:`, `difficulty:`, `last_sent:`, `review_count: 0`.

---

### 🔴 BUG 2: `agentic-ai/` and `sql/` folders exist but are NOT in `TOPIC_DIRS` — 9 notes permanently dead

```python
# agent/send_daily.py line 24:
TOPIC_DIRS = ["dsa", "system-design", "ml-ai", "fullstack", "papers"]
```

`knowledge/agentic-ai/` (5 notes) and `knowledge/sql/` (4 notes) are completely ignored by the agent.
Additionally all 5 agentic-ai notes have `topic=MISSING` in their frontmatter.

**Fix:** Add `"agentic-ai"` and `"sql"` to `TOPIC_DIRS`, fix the agentic-ai frontmatter.

---

### 🔴 BUG 3: Duplicate paper — `paper-deepseek-r1.md` and `paper-deepseek-r1-orig.md`

Two separate files covering the exact same paper:
- `paper-deepseek-r1.md` (3.8KB) — shorter summary, proper YAML ✓
- `paper-deepseek-r1-orig.md` (5.7KB) — more detailed, also proper YAML ✓

Both will be independently picked and emailed. Resolve: delete the shorter one or rename the longer to `paper-deepseek-r1-extended.md` with a note in tags.

---

### 🟡 BUG 4: `ingestion/pdf_to_notes.py` is MISSING

```
ingestion/ — EMPTY directory (0 files)
```

The README documents `python ingestion/pdf_to_notes.py --skip-existing` and git history has `aaa7423 feat: add PDF ingestion script` followed by `68f1642 fix: update pdf_to_notes.py to google-genai SDK`. The file was never committed — it only existed locally and was lost. You have **115 PDFs** in `~/Anmol/Research Papers/` with no batch-ingestion path right now.

---

### 🟡 BUG 5: ml-ai subdirectories contain `images/` folders the email agent can't serve

```
knowledge/ml-ai/activation-functions/images/  (1 file)
knowledge/ml-ai/autoencoders/images/          (2 files)
knowledge/ml-ai/cnn/images/                   (5 files)
knowledge/ml-ai/neural-networks/images/       (3 files)
knowledge/ml-ai/optimizers/images/            (1 file)
knowledge/ml-ai/segmentation/images/          (2 files)
```

If those `.md` files use `![](images/xxx.png)` relative links, every email containing them will render broken images. The email is sent as inline HTML with no file server. Either base64-embed images or strip the `<img>` tags in the render step.

---

### 🟡 BUG 6: Title derivation is wrong for paper files

```python
# send_daily.py line 128:
title = path.stem.replace("-", " ").title()
```

`paper-kan.md` → `"Paper Kan"` (should be `"KAN: Kolmogorov–Arnold Networks"`)

Email subjects look like `"Scholar-Loop: Paper Adam, Paper Transformer"` — unprofessional and confusing. Fix: parse the first `# Heading` from `post.content` instead of slugifying the filename.

---

## 3. Knowledge Base Quality Assessment

### Papers (65 files) — Overall: Good quality, inconsistent format

| Quality Tier | Count | Detail |
|---|---|---|
| ✅ Proper YAML + full structured content | 53 | Problem/Architecture/Results/Impact/Limitations sections |
| ⚠️ Inline prose frontmatter (broken) | 12 | `## Frontmatter` heading — topic/difficulty missing |
| 🔁 Duplicate | 1 pair | `deepseek-r1` + `deepseek-r1-orig` |

**Size distribution:** 3.2KB–7.9KB. Smallest files (datasets-hf 3.2KB, energy-based-models 3.4KB, neurosymbolic 3.4KB) are thin for "hard" papers and need expansion.

**Notable papers from `~/Anmol/Research Papers/` (115 PDFs) NOT yet covered:**
- AdaJEPA, LeJEPA, DINO-WM (world model variants beyond leworldmodel)
- DistilBERT, Decision Transformer
- Gemini Robotics 1.5, Gemma4/Phi4/Qwen3 comparison
- HAFLQ (federated LoRA), RT-DETRv3
- International AI Safety Reports (2025 + 2026)
- "The Assistant Axis", "Values in the Wild" (alignment/safety)
- LLaMA 1 (you have llama2 + llama3 but not llama1)

---

### DSA (41 files) — Overall: Good (short = intentional brevity, not stubs)

The small files (binary-tree 1.6KB, bfs 1.8KB) are well-structured and correct. Small size is appropriate for focused algorithmic notes.

> [!WARNING]
> `calculus-basics.md`, `linear-algebra-eigen.md`, `linear-algebra-vectors-matrices.md` are in `knowledge/dsa/` but these are **math topics, not DSA**. They belong in `knowledge/math/` (doesn't exist yet) or need retagging.

---

### System Design (13 files) — Overall: Two-tier quality problem

| File | Size | Status |
|---|---|---|
| `api-gateway.md` | 997B | Stub (~150 words). Proper YAML ✓ |
| `load-balancer.md` | 1.3KB | Stub. Proper YAML ✓ |
| `cdn.md` | 1.7KB | Stub. Proper YAML ✓ |
| `caching-strategies.md` | 1.7KB | Stub. Proper YAML ✓ |
| `message-queues.md` | 2.1KB | Thin but ok. Proper YAML ✓ |
| `system-design-fundamentals.md` | 5.4KB | Rich content. **No YAML** 🔴 |
| `ddia-distributed-systems.md` | 5.6KB | Rich content. **No YAML** 🔴 |
| `generative-ai-system-design.md` | 5.2KB | Rich content. **No YAML** 🔴 |
| `ml-system-design.md` | 5.5KB | Rich content. **No YAML** 🔴 |

The 4 broken untracked files are the most detailed notes in the folder but can't be picked. The 5 committed stubs have valid metadata but thin content.

---

### ML-AI (33 files + 7 subdirs) — Overall: Good

Well-structured. Agent's `rglob("*.md")` correctly picks up subdirectory notes too. Image issue (Bug 5) is the main risk. The untracked additions all look valid.

---

### Fullstack (13 files) — Overall: Good quality, thin topic coverage

Only `fastapi-for-ai.md` has broken frontmatter. Rest are clean. Missing areas: databases, Docker, testing, Next.js, deployment.

---

### Agentic-AI (5 files) — Overall: Good content, 100% broken metadata

All 5 notes (`agentic-design-patterns`, `llm-serving-inference`, `multi-agent-systems`, `prompt-engineering`, `rag-systems`) have **no YAML frontmatter AND are not in TOPIC_DIRS**. Completely invisible. High-value notes — should be priority-fixed.

---

### SQL (4 files) — Overall: Clean, just needs agent registration

All 4 files have proper YAML with `topic: sql`. Only issue: `sql` not in `TOPIC_DIRS`.

---

### Obsidian (`knowledge/obsidian/`) — Status: 150 files, committed but invisible

Not in `TOPIC_DIRS`. Contains:
- `interview-questions/` — 5 role-based folders (AI_Architect, AI_Engineer, Data_Scientist, ML_Engineer, AI_Researcher)
- `ai-system-design-guide/` — 18 chapters (00-interview-prep → 16-case-studies)

These are committed but the agent never sees them. Decision needed: integrate into rotation, or move to a `reference/` folder outside `knowledge/`.

---

## 4. Source Material Inventory (not yet ingested)

| Source | Location | Notes |
|---|---|---|
| Research PDFs | `~/Anmol/Research Papers/` | 115 PDFs, ~50 not yet in papers/ |
| Obsidian Study Q&A | `~/Documents/Obsidian Vault/Study/` | ML/DL/Python/SQL/Stats interview Q&A |
| Obsidian Notes | `~/Documents/Obsidian Vault/Notes/` | Python, maths, optimization lectures |
| LearningResource | `~/Projects/LearningResource/` | Math for ML, NLP Zero-to-Hero, RL |
| IIT Mandi material | `~/Anmol/Masai_X_IITMandi/Study Material/` | 3 trimesters not explored |

---

## 5. Prioritized Fix List

### 🔴 Immediate (agent correctness broken)

- [ ] **Fix 17 broken frontmatter files** — convert `## Frontmatter` and prose-style to proper YAML `---`
- [ ] **Add `agentic-ai` and `sql` to `TOPIC_DIRS`** in `send_daily.py`
- [ ] **Fix agentic-ai frontmatter** — add `topic: agentic-ai` to all 5 files
- [ ] **Commit all 97 untracked files** — they're invisible to the GitHub Actions cron

### 🟡 High Priority (quality + UX)

- [ ] **Fix title derivation** — parse `# H1` from `post.content` instead of filename slug
- [ ] **Resolve deepseek duplicate** — delete `paper-deepseek-r1-orig.md` or rename clearly
- [ ] **Move calculus/linear-algebra out of `dsa/`** — create `math/` topic or retag
- [ ] **Restore `ingestion/pdf_to_notes.py`** — 115 PDFs waiting, no ingestion path exists

### 🟠 Medium Priority (content gaps)

- [ ] **Expand thin papers** — datasets-hf, energy-based-models, neurosymbolic all need more substance
- [ ] **Expand thin system-design stubs** — api-gateway (1KB), load-balancer (1.3KB), cdn (1.7KB)
- [ ] **Fix image links** — check ml-ai subdir `.md` files for broken `![](images/...)` refs in email
- [ ] **Decide on `obsidian/`** — integrate into rotation or move out of `knowledge/`
- [ ] **Ingest priority missing papers** — LeJEPA, DINO-WM, Gemini Robotics, AI Safety Reports

### 🔵 Low Priority / V1.5+

- [ ] Add `math/` topic folder for calculus, linear algebra, probability notes
- [ ] Ingest Obsidian interview Q&A into `interview/` topic
- [ ] Ingest LearningResource course materials
- [ ] Ingest IIT Mandi study material (unexplored — may have unique content)
