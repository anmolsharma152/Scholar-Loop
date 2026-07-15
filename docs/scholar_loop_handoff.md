# Scholar-Loop Handoff Context

*This document summarizes the work completed on the Scholar-Loop project. You can provide this directly to the next agent (e.g., Big Pickle in OpenCode) to give them complete context on the project's current state and architecture.*

---

## 1. What We Saw (Initial State)

When we started, **Scholar-Loop** was a rough, partially-implemented MVP designed to send daily spaced-repetition emails containing study notes.

*   **Architecture:** A single linear Python script (`agent/send_daily.py`) triggered by a GitHub Actions cron job. It used the `frontmatter` library to read markdown files, `Groq` to generate a quiz, and `Resend` to email them.
*   **Knowledge Base:** The repo had ~30 tracked markdown notes, but over 150 untracked files across various directories. Some files were duplicated (DeepSeek dumps) and 17 notes had broken YAML frontmatter causing crashes.
*   **Bugs:** 
    *   **LLM Bug:** The Groq-enhanced text was computed, but silently discarded due to a variable shadowing bug in the `render()` function. The user paid for API calls but received raw markdown.
    *   **HTML Bug:** The email layout concatenated two complete `<!DOCTYPE html>...<html>` documents together with an `<hr>`, resulting in invalid HTML that rendered poorly.
    *   **Selection Logic:** All topics were selected completely randomly, which was fine for independent papers but terrible for structured subjects like Data Structures & Algorithms (DSA).
*   **Prompting:** The LLM was instructed to prepend a quiz and then copy-paste the entire raw 2,000-word markdown note, making the emails overly long and tedious to read.

---

## 2. What We Did (The Fixes & Features)

We transformed the project into a robust, premium-feeling MVP through a series of rapid iterations:

### Data & Knowledge Base Cleanup
*   Cleaned up all untracked files, removed duplicates, and fixed the 17 broken YAML frontmatter headers.
*   Integrated **193 clean notes** across 7 primary topics (`dsa`, `fullstack`, `ml-ai`, `papers`, `system-design`, `agentic-ai`, `sql`).
*   Updated `extract_title()` to dynamically read the first `# H1` heading inside the markdown file instead of relying on ugly filename slugs.

### Core Engine Fixes (`send_daily.py`)
*   Fixed the LLM rendering bug so the enhanced content actually makes it into the email.
*   Fixed the HTML concatenation bug by splitting the layout into a single valid `EMAIL_WRAPPER` and an internal `NOTE_SECTION`.
*   Added the note `{title}` to the HTML display (it was previously only visible in the subject line).

### The "Premium" Email Redesign
*   Completely rewrote the HTML template to look like a premium tech newsletter.
*   Expanded max-width to 850px for desktop readability, added a vibrant purple gradient header, modern typography, sleek drop-shadows, and crisp `[AI-enhanced]` pill badges.

### LLM Prompt Engineering
*   Changed the prompt from "copy-paste the note" to **"synthesize a 2-minute read"**. 
*   The LLM now completely rewrites the note into three punchy sections: **🧠 The Core Intuition**, **🔑 Key Takeaways**, and a **🎯 Self-Test**.
*   **Spoiler Tags:** Fixed the quiz answer key. Since email clients (like Gmail) strip interactive `<details>` tags, we instructed the LLM to output answers in a white-text-on-white-background `<blockquote>`. The user simply highlights the invisible text to reveal the answers.

### Sequential Curriculums Feature (DSA)
*   Implemented a major architectural change: **Sequential Learning**.
*   Wrote a python script to map the 41 `dsa` files to a strict 18-module syllabus, injecting a `sequence: X` field into their frontmatter.
*   Updated the `pick_one()` algorithm: For topics with `sequence` tags, the agent strictly introduces the lowest unread sequence number first. Old notes are still reviewed randomly. This allows structured learning for DSA while keeping randomized flashcard learning for other topics.

### Infrastructure & Automation
*   Configured the GitHub Actions workflow (`daily-email.yml`) to run **twice a day** (07:00 IST and 16:00 IST).
*   Verified that the bot safely commits metadata (`review_count`, `last_sent`) back to the `main` branch using a `[skip ci]` tag to prevent infinite loops.
*   Rewrote the `README.md` to document the new 193-note state and future roadmap.

---

## 3. What State It Is In Now (Current State)

The Scholar-Loop MVP is now **fully robust, heavily tested, and actively running in production.** 

It successfully wakes up twice a day, probabilistically scores 193 notes based on how long it has been since you last saw them, forces sequential progression for DSA, synthesizes them into a beautiful premium email via Groq, sends them via Resend, and updates its own database (the git repo).

### Future Roadmap (Already Planned)
We drafted an `implementation_plan.md` outlining the next phases when you are ready:
1. **Phase 1.5 (Live Watchers):** Adding `ingestion/arxiv_watch.py` to automatically pull new papers matching your interests into a review queue.
2. **Phase 2.0 (LangGraph Agent):** Refactoring `send_daily.py` into a stateful LangGraph architecture with specialized nodes (`select`, `enhance`, `compose`, `deliver`) and a RAG pipeline (`note_search.py`) to select notes based on semantic relevance.
3. **Phase 2.5 (SM-2):** Upgrading the weighted-random scorer to a true SM-2 spaced-repetition algorithm.
