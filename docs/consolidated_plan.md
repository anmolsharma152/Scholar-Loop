# Scholar-Loop — Consolidated Sprint Plan

*Sprint date: 2026-07-15*

---

## Current State

| Metric | Value |
|--------|-------|
| Total notes | 343 (193 committed, 150 orphaned in `obsidian/`) |
| Notes agent sees | 193 (7 topics in `TOPIC_DIRS`) |
| DSA notes | 41 (all have `sequence:` tags, only 1 ever sent) |
| DSA sent | 1 (`segment-tree.md` seq=19, `review_count: 1`) |
| DSA unsent | 40 |
| Cron | GitHub Actions, 7 AM + 4 PM IST |
| Email | Resend, HTML template, 850px, purple gradient header |
| LLM | Groq (llama-3.3-70b-versatile), recap + quiz generation |

---

## Fix 1: DSA Reset + Mandatory Selection

**Priority**: Highest — user's main ask. DSA notes never appear in emails.

### 1a. Reset `segment-tree.md` metadata

`knowledge/dsa/segment-tree.md` is the only DSA file with `last_sent` set (`2026-07-13`) and `review_count: 1`. Set `last_sent` → null, `review_count` → 0.

This is a one-off manual edit, not code.

### 1b. Add `--reset-dsa` flag to `send_daily.py`

When passed, iterates all `knowledge/dsa/*.md`, sets `last_sent` → null, `review_count` → 0. Used once to clean slate. Remove after use.

```python
# In argument parser:
parser.add_argument("--reset-dsa", action="store_true",
    help="Reset all DSA metadata (last_sent=null, review_count=0)")

# Early in main():
if args.reset_dsa:
    for md in (KNOWLEDGE_DIR / "dsa").glob("*.md"):
        post = frontmatter.load(str(md))
        post.metadata["last_sent"] = None
        post.metadata["review_count"] = 0
        with open(md, "w") as f:
            f.write(frontmatter.dumps(post))
    print("DSA metadata reset.")
    return
```

### 1c. Fix selection algorithm

**Problem**: `main()` (lines 310-324) picks 3 notes randomly across ALL topics. `pick_notes_for_email()` (lines 216-238) then runs the sequence filter, which limits DSA to 1 note max. DSA gets selected ~5% of the time.

**Fix**: Add `dsa_caught_up()` helper. Modify `main()` to enforce DSA-mandatory when not caught up.

```python
def dsa_caught_up():
    """True = every DSA note has review_count >= 2."""
    for md in (KNOWLEDGE_DIR / "dsa").glob("*.md"):
        post = frontmatter.load(str(md))
        if (post.metadata.get("review_count") or 0) < 2:
            return False
    return True

# Replace lines 310-324 in main():
if not dsa_caught_up():
    dsa_note = pick_notes_for_email(1, ["dsa"])
    other   = pick_notes_for_email(1, [t for t in TOPIC_DIRS if t != "dsa"])
    notes   = dsa_note + other
else:
    notes = pick_notes_for_email(3, list(TOPIC_DIRS.keys()))
```

**Why this works**: The sequence filter (`pick_notes_for_email` lines 216-238) still applies. With 41 notes at `review_count: 0`, `max_completed` starts at 0, picks from seq 1 (3 notes). After all seq-1 notes are sent (3 emails), `max_completed` becomes 1, picks from seq 2, etc. `segment-tree.md` (seq=19) will be held until seq 18 completes — correct behavior.

**Timeline**: DSA-mandatory for ~41 days (82 sends = 41 notes × 2 reviews). After that, reverts to original random.

**Edge case**: If user runs `--reset-dsa` mid-cycle, `dsa_caught_up()` immediately returns `False` and the cycle restarts from seq 1.

---

## Fix 2: Mobile Email CSS

**Priority**: High — emails look broken on phones.

### Current problems
- `EMAIL_WRAPPER` (line 32): `padding: 40px` — too wide on mobile
- `NOTE_SECTION` (line 55): `padding: 24px` — no responsive reduction
- `QUIZ_ANSWER` (line 66): `padding: 20px` — same
- No `@media` queries anywhere
- Code blocks (`<pre>`) overflow horizontally
- Tables don't scroll
- AI badges don't wrap

### Fix: Add responsive styles inside `EMAIL_WRAPPER`

Add a `<style>` block inside `EMAIL_WRAPPER` (line 32) with:

```css
@media only screen and (max-width: 600px) {
  body { padding: 16px !important; font-size: 14px !important; }
  .note-section { padding: 16px !important; }
  .note-section h1 { font-size: 20px !important; }
  pre { overflow-x: auto !important; white-space: pre !important; }
  table { display: block !important; overflow-x: auto !important; }
  .ai-badges { flex-wrap: wrap !important; }
  .content-div { word-wrap: break-word !important; overflow-wrap: break-word !important; }
}
```

Also:
- Change `EMAIL_WRAPPER` body padding to `40px 20px` (horizontal 20px, vertical 40px)
- Add `class="note-section"` to `NOTE_SECTION` div
- Add `class="ai-badges"` to badge container
- Add `class="content-div"` to content wrapper

**Files**: `agent/send_daily.py` lines 32-72 (all template strings)

---

## Fix 3: Ingest 8 PDFs

**Priority**: Medium — expands the knowledge base.

### 8 PDFs to process

| # | File | Topic | Destination |
|---|------|-------|-------------|
| 1 | `~/Anmol/Research Papers/SparDA_ A Sparse Dynamic Sparse Attention.pdf` | papers | `knowledge/papers/` |
| 2 | `~/Anmol/Research Papers/AI Safety Reports...Part 4.pdf` | papers | `knowledge/papers/` |
| 3 | `~/Anmol/Research Papers/AI Safety Reports...Part 5.pdf` | papers | `knowledge/papers/` |
| 4 | `~/Anmol/Research Papers/Grokking Explained...pdf` | papers | `knowledge/papers/` |
| 5 | `~/Anmol/Research Papers/Building Machines That Learn...pdf` | papers | `knowledge/papers/` |
| 6 | `~/Anmol/Research Papers/X-Token_ Learning Context Distillation...pdf` | papers | `knowledge/papers/` |
| 7 | `~/Downloads/LLM-Interview-Questions.pdf` | fullstack? | `knowledge/fullstack/` or `knowledge/ml-ai/` |
| 8 | `~/Downloads/One Stop MCP.pdf` | agentic-ai | `knowledge/agentic-ai/` |

### Approach

Recreate `ingestion/pdf_to_notes.py`. Use Gemini API to read each PDF, generate structured markdown with frontmatter (`title`, `topic`, `tags`, `created`, `difficulty`). Route to correct `knowledge/` subdirectory.

This file was deleted in commit `63d5b8a` and needs rebuilding from scratch.

---

## Fix 4: Obsidian Files Decision

**Priority**: Low — pending user decision.

### Current state
150 files in `knowledge/obsidian/`, all with `topic: obsidian`. Not in `TOPIC_DIRS`, so agent never selects them. They contain:
- 109 AI System Design Guide notes (interview Q&A format)
- 39 ML/Fullstack/Agentic-ai interview questions

### Options
1. **Delete** `knowledge/obsidian/` — cleanest. User has proper notes for these topics already.
2. **Redistribute** — move relevant files into real topic dirs with corrected `topic:` tags. Large manual effort.
3. **Add `obsidian` to `TOPIC_DIRS`** — agent can select them, but `topic: obsidian` prints wrong in emails.

**Recommendation**: Delete. The interview Q&A format is less valuable than curated notes.

**User decision required.**

---

## Fix 5: Cleanup

**Priority**: Low — housekeeping.

### Files deleted (already done)
- `scratchpad_v0p4ylzb.md` — antigravity browser failure log
- `email_preview.html` — stale old email template (680px layout)
- `add_sequences.py` — one-shot script, already committed to git

### Files moved to `docs/`
- `implementation_plan.md` — describes sequential curriculum (now done)
- `scholar_loop_analysis.md` — pre-fix audit (many issues now resolved)
- `scholar_loop_handoff.md` — antigravity sprint handoff
- `walkthrough.md` — describes email redesign + sequential curriculum (both done)

### Files to potentially delete
- `docs/implementation_plan.md` — fully implemented, can delete
- `docs/scholar_loop_analysis.md` — stale audit, can delete
- `docs/scholar_loop_handoff.md` — stale handoff, can delete
- `docs/walkthrough.md` — stale, can delete

**Recommendation**: Delete all 4 docs after this plan is committed (they're in git history if ever needed).

---

## Execution Order

1. **Fix 1** (DSA reset + mandatory selection) — highest priority
2. **Fix 2** (mobile email CSS) — quick, no dependencies
3. **Fix 3** (8 PDF ingestion) — needs `ingestion/pdf_to_notes.py` recreated
4. **Fix 5** (cleanup) — trivial deletions
5. Commit + dry-run test
6. **Fix 4** (obsidian) — pending user decision

---

## Open Questions

1. `LLM-Interview-Questions.pdf` → `ml-ai/` or `fullstack/`?
2. `One Stop MCP.pdf` → `agentic-ai/`?
3. Obsidian files → delete, redistribute, or keep as-is?
4. After sprint → what to build next (SM-2 / live watchers / LangGraph)?
5. Should the 4 stale docs in `docs/` be deleted after this plan is committed?
