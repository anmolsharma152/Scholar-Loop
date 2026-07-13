---
topic: system-design
difficulty: hard
tags: [system-design, ml-systems, mlops, training, serving]
last_sent:
review_count: 0
---

# ML System Design

## ML System Design Lifecycle

1. **Problem definition:** Business metric → ML metric
2. **Data engineering:** Collection, labeling, validation, versioning
3. **Feature engineering:** Feature store, transformations, pipelines
4. **Model development:** Baseline → iterate → select
5. **Evaluation:** Offline metrics, online A/B testing
6. **Deployment:** Serving strategy, infrastructure
7. **Monitoring:** Drift detection, performance degradation
8. **Iteration:** Retrain, update, improve

---

## Data Engineering

### Data Collection
- **Structured:** SQL databases, data warehouses
- **Unstructured:** Web scraping, APIs, logs
- **Streaming:** Kafka, Kinesis for real-time data
- **Labeling:** Manual annotation, weak supervision (Snorkel), active learning

### Data Validation
- **Schema validation:** Enforce column types, ranges (Great Expectations)
- **Statistical validation:** Distribution shift detection
- **Data lineage:** Track source → transformations → usage

### Data Versioning
- **DVC (Data Version Control):** Git-like versioning for data and models
- **Delta Lake / Iceberg:** ACID transactions on data lakes

---

## Feature Engineering

### Feature Store
- Central repository for computed features
- **Offline store:** Batch features for training
- **Online store:** Low-latency features for serving
- Tools: Feast, Tecton, Hopsworks

### Training-Serving Skew
- **Definition:** Difference between features available during training vs serving
- **Causes:** Different code paths, data leakage, stale features
- **Prevention:** Shared feature computation code, monitoring

### Common Feature Types
- **Numerical:** Normalized, binned, polynomial
- **Categorical:** One-hot, target encoding, embedding
- **Temporal:** Time since event, rolling statistics
- **Text:** TF-IDF, embeddings, attention features

---

## Model Development

### Baseline Approach
- Start simple: logistic regression, XGBoost
- Establishes minimum performance bar
- Often surprisingly competitive

### Model Selection Criteria
- Inference latency requirements
- Training data availability
- Model interpretability needs
- Infrastructure constraints (GPU availability)
- Team expertise

### Training Considerations
- **Distributed training:** Data parallelism, model parallelism
- **Mixed precision:** FP16/BF16 for faster training
- **Checkpointing:** Save model state for recovery
- **Hyperparameter optimization:** Bayesian, random search, Optuna

---

## Model Deployment Strategies

### Serving Modes
| Mode | Latency | Use Case | Examples |
|---|---|---|---|
| Batch | Hours | Daily recommendations, reports | Spark, Airflow |
| Near-real-time | Minutes | Feature refresh, caching | Scheduled inference |
| Real-time | < 100ms | Fraud detection, search ranking | TensorFlow Serving, Triton |

### Deployment Patterns
- **Canary deployment:** Roll out to 1% → 10% → 100%
- **Shadow mode:** Run new model alongside old; compare outputs
- **Blue-green:** Two identical environments; switch traffic
- **Rollback:** Quick revert to previous model version

### Container Orchestration
- Kubernetes: Auto-scaling, self-healing, rolling updates
- GPU scheduling: NVIDIA device plugin, time-slicing

---

## Monitoring and Observability

### What to Monitor
- **Model performance:** Accuracy, latency P50/P95/P99, throughput
- **Data quality:** Null rates, distribution shifts, schema violations
- **System health:** CPU/GPU utilization, memory, queue depth
- **Business metrics:** Revenue, conversion, user satisfaction

### Drift Detection
- **Data drift (covariate shift):** Input distribution changes
- **Concept drift:** Relationship between input and label changes
- **Detection methods:** KL divergence, PSI, statistical tests
- **Response:** Trigger retraining pipeline

### Alerting
- Set thresholds on key metrics
- Anomaly detection on metric time series
- Escalation policies for critical failures

---

## MLOps

### CI/CD for ML
- **CI:** Code + data + model validation
- **CD:** Automated model deployment after validation passes
- **CT (Continuous Training):** Automated retraining on new data

### ML Platform Components
- **Orchestration:** Airflow, Kubeflow Pipelines, Prefect
- **Experiment tracking:** MLflow, Weights & Biases
- **Model registry:** Versioned model storage with metadata
- **Feature store:** Feast, Tecton
- **Serving:** TFServing, Triton, Seldon, BentoML

### Reproducibility
- Pin all dependencies (pip, conda)
- Version data, code, and model together
- Log experiments with all hyperparameters
- Use deterministic seeds

---

## Common ML System Design Patterns

### Recommendation System
1. Candidate generation (coarse, fast: two-tower model)
2. Ranking (fine, accurate: gradient boosted trees or deep model)
3. Re-ranking (diversity, freshness, business rules)

### Fraud Detection
- High imbalance: SMOTE, focal loss, undersampling
- Real-time features: Transaction velocity, device fingerprint
- Model: XGBoost or LightGBM for latency + interpretability
- Explainability: SHAP values for flagged transactions

### Search Ranking
- Query understanding: Spell correction, intent classification
- Retrieval: BM25 + dense retrieval (bi-encoder)
- Ranking: Cross-encoder or learned ranking model
- Features: Query-document relevance, freshness, popularity
