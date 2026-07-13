---
topic: ml-ai
title: "Machine Learning Basics & Evaluation"
difficulty: easy
tags: [ml, fundamentals, evaluation]
sources:
  - "ML_Lec1_Learning.pdf"
  - "ML_Lec2_Training_Evaluation.pdf"
  - "ML_Lec4_Linear_Regression.pdf"
---

# ML Basics & Evaluation

## What is Machine Learning

- ML programs computers to **learn from input data** rather than being explicitly programmed.
- **Learning** = converting experience into expertise/knowledge.
- Input to a learning algorithm is **training data** (experience); output is a program that performs the task.
- Key insight: A successful learner must **generalize beyond training data** (inductive reasoning), not just memorize.

## Types of Learning

### Supervised Learning
- Training data: `{(x⁽ⁱ⁾, y⁽ⁱ⁾)}` — input-output pairs with labels.
- **Regression**: Predict continuous values (e.g., house price). Output ∈ ℝ.
- **Classification**: Predict discrete class labels (e.g., spam/ham). Output ∈ {0, 1}.

### Unsupervised Learning
- Training data: `{x⁽ⁱ⁾}` — no labels.
- Goal: discover hidden structure (clustering, dimensionality reduction).

### Reinforcement Learning
- Agent learns by interacting with an environment, receiving rewards/penalties.

## The ML Pipeline

1. **Data Collection & Preparation** — gather, clean, handle missing values, scale features.
2. **Train/Validation/Test Split** — separate data to evaluate generalization.
3. **Model Selection** — choose algorithm based on problem type.
4. **Training** — initialize parameters → compute predictions → compute loss → update parameters (e.g., gradient descent).
5. **Validation** — tune hyperparameters, monitor for overfitting.
6. **Testing** — final evaluation on unseen data.

### Loss Functions
- **MSE** for regression: `J(θ) = (1/2m) Σ (hθ(x⁽ⁱ⁾) - y⁽ⁱ⁾)²`
- **Cross-entropy** for classification.

## Classification vs Regression

| Aspect | Regression | Classification |
|--------|-----------|----------------|
| Output | Real numbers | Class labels |
| Error Metrics | MSE, MAE, R² | Accuracy, Precision, Recall, F1, AUC-ROC |
| Decision Boundary | None | Separates classes |

## Evaluation Metrics

### Classification Metrics
- **Accuracy**: fraction correct overall.
- **Precision**: of predicted positives, how many are truly positive.
- **Recall**: of actual positives, how many are correctly identified.
- **F1-Score**: harmonic mean of precision and recall.
- **ROC-AUC**: measures discrimination ability across all thresholds.

### Regression Metrics
- **MSE** (Mean Squared Error)
- **MAE** (Mean Absolute Error)
- **R² Score**: variance explained by the model.

## Key Concepts

- **Overfitting**: model memorizes training data, fails on unseen data.
- **Generalization**: ability to perform well on new, unseen examples.
- **Inductive bias**: assumptions the learner makes to generalize (e.g., linearity, smoothness).
