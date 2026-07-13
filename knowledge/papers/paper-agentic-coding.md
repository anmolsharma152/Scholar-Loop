---
topic: papers
difficulty: medium
last_sent:
review_count: 0
tags:
  - paper
  - agentic-coding
  - labor-market
  - expertise
  - empirical-study
---

# Agentic Coding and Persistent Returns to Expertise

**Authors:** Zoe Hitzig, Maxim Massenkoff, Eva Lyubich, Ryan Heller, Peter McCrory (Anthropic)
**Published:** Anthropic Research Report, June 2026
**arXiv:** N/A

## Problem & Motivation

Agentic coding tools have rapidly grown in adoption—GitHub projects with coding agent activity more than doubled since late 2025, and Claude Code users average 20 hours per week using the tool. But little was known about how these tools are actually used in practice: who uses them, whether non-coders can direct them effectively, and whether domain expertise still matters when AI handles the implementation. The authors wanted to understand the real-world dynamics of human-AI collaboration in coding and whether the labor market implications of agentic coding reward expertise or technical skill. The study provides evidence on approximately 400,000 interactive sessions from roughly 235,000 people between October 2025 and April 2026, using Claude Code through CLI, claude.ai, or the desktop app.

## Key Idea / Architecture

This is an empirical study based on a privacy-preserving analysis of ~400,000 interactive Claude Code sessions from ~235,000 people between October 2025 and April 2026. The authors developed a framework for classifying agentic coding usage along three dimensions: work mode (what kind of task), decision attribution (who decides what vs. how), and expertise level. Sessions were classified into nine work modes: writing (25%), fixing (26%), testing (5%), orchestrating (0.5%), operating (17%), understanding (14%), planning, analyzing data, and communicating.

Decision attribution was measured by classifying all meaningful decisions in each session as either planning (what to do) or execution (how to do it), then attributing each to Claude or the user. Expertise was rated on a five-point scale (novice to expert) based on how precisely users frame directions, what they ask Claude to verify, and whether the user or Claude corrects the other. Success was measured through two complementary classifiers: judged success (did the person accomplish their goal?) and verified success (judged success + hard evidence like passing tests or git commits).

## Key Contributions

1. Found a clear division of labor: people make ~70% of planning decisions while Claude makes ~80% of execution decisions—the user decides what to build, the agent decides how
2. Demonstrated that domain expertise, not coding proficiency, amplifies effective use: experts get ~12 actions per prompt vs. ~5 for novices, and 5x more output
3. Showed every major occupation succeeds at coding nearly the same rate as software engineers (within 7 percentage points)
4. Found verified success rates: 15% for novices vs. 28-33% for intermediate/expert users, with most gains coming from novice-to-intermediate transition
5. Tracked temporal trends: debugging share fell from 33% to 19%, average session value rose 27% over seven months
6. Introduced a privacy-preserving analysis framework using model classifiers validated against telemetry data with >90% agreement

## Results (Specific Numbers)

- Dataset: ~400,000 sessions from ~235,000 people (Oct 2025–Apr 2026)
- Division of labor: users make 70% planning decisions, Claude makes 80% execution decisions
- Actions per prompt: novices ~5, experts ~12 (geometric means, p<0.001)
- Output per prompt: novices ~600 words, experts ~3,200 words
- Verified success: novices 15%, intermediate 28%, expert 33%
- Partial success rate: novices 77%, intermediate 91%, expert 92%
- Session value increase: 27% average over 7 months
- Debugging share decline: 33% → 19% of sessions
- Software engineers verified success: 34% in code-producing sessions (vs. 29% for other occupations)
- Management occupations: highest verified success rate, slightly above software engineering

## Why It Matters / Impact

This study provides the first large-scale empirical evidence on how agentic coding reshapes knowledge work. The finding that domain expertise matters more than coding skill has profound implications for education and labor markets: programming proficiency is becoming less valuable than deep understanding of the problem domain. The modest gap between intermediate and expert users suggests proficiency—not mastery—is sufficient to capture most benefits. The temporal trends showing increasing task value and shifting work composition suggest agentic coding tools are moving up the value chain from debugging to higher-level creation and operations. The evidence that non-software occupations achieve near-software-engineer success rates suggests coding agents are democratizing technical work across professions. These findings may preview how agentic tools will reshape other forms of knowledge work.

## Weaknesses / Limitations

- Cannot measure real-world outcomes (whether code is actually used or discarded after the session)
- Excludes non-interactive usage (SDK integrations, headless mode) which represents a substantial share of agentic coding activity
- Success and expertise classifications depend on model reading of transcripts, not ground-truth human labels
- Only covers Claude Code users, potentially not representative of all agentic coding tools or platforms
- The 70% planning / 80% execution split is measured by a classifier, not ground-truth annotations
- Task value estimation is based on freelance market comparisons, which are coarse and may not reflect actual economic value
- Occupation inference is only possible for ~70% of sessions, with the remainder unclassified
- The expertise classifier is task-specific, not measuring general coding ability or domain knowledge
- The 4-turn average session structure with ~10 actions per prompt may not represent all use patterns

## Follow-up Work

- Tracking whether returns to expertise decrease over time as models improve
- Measuring non-interactive agentic coding usage and its economic impact
- Longitudinal analysis of how the division of labor evolves as models become more capable
- Extension to non-coding knowledge work domains (legal, medical, financial analysis)
- Studying how the value of coding-specific education changes in an agentic coding world
- Analysis of how agentic coding adoption affects open-source contribution patterns and project sustainability
- Investigating whether longer prompts and detailed constraints actually increase task success or just completion rates
- Measuring the impact of the four-turn average session structure on user learning and independence over time
- Evaluating whether partial success rates (novice 77%, expert 92%) represent genuine value or just user effort

---
