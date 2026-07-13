---
topic: papers
difficulty: hard
last_sent:
review_count: 0
tags:
  - paper
  - gpt-4
  - multimodal
  - safety
  - alignment
  - scaling
  - rlhf
---

# GPT-4 Technical Report

**Authors:** OpenAI
**Published:** arXiv preprint, updated March 2024
**arXiv:** 2303.08774v6

## Problem & Motivation

Scaling language models has yielded broad benchmark increases, but GPT-4 aims for a more general problem solver. Need to evaluate LLMs on human-level academic and professional exams. Safety challenges increase with capabilities, requiring systematic adversarial testing and alignment. Multimodal understanding (text + images) is critical for real-world applications. The project also required developing infrastructure that behaves predictably across scales, enabling performance predictions from models trained with 1/1000th the compute.

## Key Idea / Architecture

GPT-4 is a large-scale multimodal model accepting image and text inputs, producing text outputs. It is a Transformer pre-trained to predict the next token using publicly available data and licensed third-party data, then fine-tuned with RLHF. The architecture details—including model size, hardware, training compute, dataset construction, and training method—are deliberately withheld for competitive and safety reasons. The report focuses on predictable scaling: loss prediction using power law L(C) = aC^b + c from models trained with up to 10,000x less compute, and capability prediction on HumanEval using approximate power law -E_P[log(pass_rate(C))] = alpha * C^(-k). Alignment follows InstructGPT methodology: supervised fine-tuning, reward model training, then PPO with a Rule-Based Reward Model (RBRM) for safety scoring. A model-assisted safety pipeline uses multiple specialized models for content filtering and policy compliance. Red-teaming involved 50+ domain experts across security, biology, international law, and other fields.

## Key Contributions

1. Human-level performance on academic exams: Uniform Bar Exam ~90th percentile (298/400), SAT EBRW 710/800 (93rd), SAT Math 700/800 (89th), GRE Verbal 169/170 (99th)
2. Predictable scaling: accurately predicted GPT-4 final loss and HumanEval pass rates from models trained with 1,000x-10,000x less compute before training completed
3. Multimodal capabilities: TextVQA 78.0%, DocVQA 88.4%, MMMU 56.8% (pass@1), 62.4% (Maj1@32)
4. Comprehensive safety framework: automated adversarial testing using GPT-4 itself, model-assisted safety pipeline

## Results (Specific Numbers)

### Exam Performance

| Exam | GPT-4 | Percentile | GPT-3.5 |
|------|-------|------------|---------|
| Uniform Bar Exam (MBE+MEE+MPT) | 298/400 | ~90th | 213/400 (~10th) |
| LSAT | 163 | ~88th | 149 (~40th) |
| SAT EBRW | 710/800 | ~93rd | 670/800 (~87th) |
| SAT Math | 700/800 | ~89th | 590/800 (~70th) |
| GRE Quantitative | 163/170 | ~80th | 157/170 (~62nd) |
| GRE Verbal | 169/170 | ~99th | 154/170 (~63rd) |
| USABO Semifinal | 87/150 | 99th-100th | 43/150 (31st-33rd) |

### Standard Benchmarks

| Benchmark | GPT-4 | GPT-3.5 |
|-----------|-------|---------|
| MMLU (5-shot CoT) | 86.4% | 70.0% |
| HumanEval (pass@1) | 67% | 48% |
| MATH | 42.5% | 13.5% |
| GSM8K | 92% | 57% |
| HellaSwag | 95.3% | 85.5% |

### Multimodal Benchmarks

- TextVQA 78.0%, DocVQA 88.4%, MathVista 49.9%
- MMMU pass@1 56.8%, Maj1@32 62.4%

### Leetcode Coding

- Easy: 31/41, Medium: 21/80, Hard: 3/45

### Economic Impact Estimate

- GPT-4 estimated to impact ~19% of jobs (36% of US jobs), with higher-education and higher-wage jobs more exposed

## Why It Matters / Impact

GPT-4 demonstrated that large multimodal models can match or exceed human-level performance on professional and academic examinations, establishing a new evaluation paradigm. The predictable scaling results validated that small-scale experiments can forecast large-model capabilities, critical for safety. The model set the standard for multimodal understanding and influenced the entire industry's approach to alignment, evaluation, and safety reporting.

## Weaknesses / Limitations

- Architecture, training data, compute details deliberately withheld—no reproducibility
- Hallucinations and factual errors persist ("not fully reliable")
- Makes simple reasoning errors on challenging problems despite strong overall performance
- Limited multimodal: text output only, no image generation
- Benchmark contamination possible for some exams
- Cannot prevent misuse by determined adversaries
- Over-refusal of harmless requests remains an issue

## Follow-up Work / Key References

- GPT-4 Turbo (2023) — extended context to 128K tokens, reduced pricing
- GPT-4o (2024) — native multimodal output, faster inference
- InstructGPT (Ouyang et al., 2022) — foundational RLHF alignment methodology
- Kaplan et al. (2020) and Henighan et al. (2021) — scaling law foundations for predictable scaling
- Wei et al. (2022) chain-of-thought prompting — referenced for capability prediction
