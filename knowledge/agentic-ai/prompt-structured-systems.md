---
topic: agentic-ai
difficulty: easy
tags: [llm, prompting, structured-output, system-prompts]
last_sent:
review_count: 0
---

# Prompt Engineering: Structured Outputs & Systems

## Structured Outputs

### JSON Mode
```
Respond in the following JSON format:
{
  "sentiment": "positive|negative|neutral",
  "confidence": 0.0-1.0,
  "key_phrases": ["phrase1", "phrase2"]
}
```

### XML Tags
```
<analysis>
<sentiment>positive</sentiment>
<confidence>0.85</confidence>
</analysis>
```

### Function Calling
- Most reliable for structured output
- Model generates structured function call
- Supported natively by OpenAI, Anthropic, Google

## System Prompt Design

### Structure
```
1. Role definition: "You are a senior data analyst..."
2. Task description: "Analyze the provided data and..."
3. Constraints: "Always cite sources. Never make up data."
4. Format instructions: "Respond in markdown with..."
5. Examples (optional): Few-shot examples of desired behavior
6. Edge case handling: "If you don't know, say so..."
```

### Best Practices
- Be specific about what you want (and don't want)
- Put important instructions at the beginning and end (primacy/recency)
- Use examples to demonstrate format and behavior
- Set explicit boundaries for what the model should/shouldn't do
- Version your system prompts; A/B test changes

## Prompt Optimization

### Iterative Process
1. Start with clear task description
2. Test on diverse inputs
3. Identify failure modes
4. Add instructions/examples to fix failures
5. Repeat

### Common Failure Modes

| Failure | Fix |
|---|---|
| Model ignores instructions | Move instruction to start and end |
| Wrong output format | Add explicit format example |
| Hallucination | Add "If unsure, say you don't know" |
| Too verbose | "Respond in 2-3 sentences maximum" |
| Off-topic | Tighten system prompt scope |
| Inconsistent | Add few-shot examples |

## Prompt Injection Defense

### Threats
- **Direct injection:** User overrides system prompt ("Ignore previous instructions...")
- **Indirect injection:** Malicious content in retrieved documents
- **Jailbreaking:** Techniques to bypass safety filters

### Defenses
1. **Input sanitization:** Filter known injection patterns
2. **Instruction hierarchy:** System prompt > user input; use delimiters
3. **Output validation:** Check output against expected format/content
4. **Separation:** Keep system prompt in system role, not user message
5. **Monitoring:** Flag unusual outputs for review

## Advanced Techniques

### Meta-Prompting
Ask the model to improve its own prompt.

### Chain-of-Verification (CoVe)
1. Model generates initial answer
2. Model generates verification questions about its answer
3. Model answers each verification question independently
4. Model revises answer based on verification

### Prompt Chaining for Complex Tasks
1. **Analyze:** "What are the key points in this document?"
2. **Structure:** "Organize these points into categories."
3. **Draft:** "Write a summary using this structure."
4. **Review:** "Check this summary for accuracy and completeness."
