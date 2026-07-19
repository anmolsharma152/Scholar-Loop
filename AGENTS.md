# AGENTS.md

Guidance for coding agents working in **Scholar-Loop**.

## Product scope

Scholar-Loop is a **spaced-repetition learning companion**: FSRS-scheduled Learn and Quiz digests over a personal markdown knowledge base, delivered by email.

**Out of scope:**

| Domain | Product |
|--------|---------|
| Gmail/GitHub operator / tasks | Ozyman |
| Job boards / LPA fit | Disha |
| Creative diverge–evaluate idea OS | IdeaForge |

Portfolio: [docs/portfolio-product-boundaries.md](./docs/portfolio-product-boundaries.md).  
Resume: [docs/STATUS.md](./docs/STATUS.md).

## Important paths

| Area | Path |
|------|------|
| Daily agent | `agent/send_daily.py` |
| Knowledge notes | `knowledge/` |
| FSRS DB | `data/user.db` |
| Init / convert | `scripts/init_db.py`, `scripts/convert_notes.py` |
| Actions | `.github/workflows/` |

## Engineering norms

- Prefer **dry-run** before live Resend.  
- DSA uses `sequence` curriculum order — don’t randomize new DSA intros.  
- Scheduling state is in SQLite, not frontmatter.  
- Actions may commit `data/user.db` with `[skip ci]`.  
- Atomic commits; never commit API keys.  
- Do not absorb Ozyman/Disha/IdeaForge features here.
