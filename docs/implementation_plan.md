# Sequential Curriculums (DSA Roadmap)

Currently, Scholar-Loop uses a purely random selection algorithm for all unread notes. While great for independent topics like `papers`, a structured topic like `dsa` requires a linear progression so you aren't asked to learn Tries before you learn Basic Arrays.

This plan introduces **Sequential Curriculums** to the agent.

## User Review Required

> [!IMPORTANT]  
> The 18-module syllabus you provided is very detailed, but currently, your `knowledge/dsa` folder has exactly 41 markdown files (e.g., `arrays.md`, `binary-search.md`, `stack.md`, `trie.md`). I will need to map these 41 files to the order of your syllabus.

## Open Questions

> [!TIP]
> 1. Do you want me to rename/restructure your 41 existing files to perfectly match the exact syllabus chapters you pasted, or should I just assign them sequence numbers that follow the logical flow of your syllabus?
> 2. Should this sequential logic apply *only* to `dsa`, or should we make it a general feature where any note with a `sequence: X` frontmatter field is forced to be introduced in order? (I recommend making it a general feature).

## Proposed Changes

### `knowledge/dsa/*.md`
- Add a `sequence: <number>` field to the YAML frontmatter of all 41 files in the `knowledge/dsa/` directory.
- Files will be numbered `1` through `41` based on the progression of your syllabus (Basics → Sorting → Arrays → Binary Search → Strings → Linked Lists → Bit Manipulation → Recursion → Stacks/Queues → Sliding Window → Greedy → Trees → BST → Heaps → Graphs → DP → Tries).

### `agent/send_daily.py`
- Modify the `pick_one()` selection logic. 
- **New Algorithm:** When assembling the pool of eligible notes, the agent will look at all notes with `last_sent: null` (unread notes). If they have a `sequence` field, the agent will find the absolute lowest sequence number that hasn't been read yet, and **exclude** all higher sequence numbers from the pool.
- **Result:** The agent will only ever introduce the *next* new topic in the sequence, while still randomly picking old topics for spaced-repetition review.

## Verification Plan

### Automated Tests
- Run `python agent/send_daily.py --dry-run` multiple times to verify that the agent *only* selects `dsa` notes that are next in the sequence, while old notes are still reviewed correctly.

### Manual Verification
- Await user approval on the mapping of the 41 files to the sequence numbers before committing.
