---
topic: ml-ai
difficulty: medium
tags: [ml, mlops, systems]
---

# ML Systems Fundamentals

## 1. Data Pipelines

### Data Ingestion & Processing
- **Batch pipelines**: Scheduled ETL (Apache Spark, Airflow). Best for training datasets.
- **Streaming pipelines**: Kafka, Flink, gRPC for real-time feature computation.
- **Key challenge**: Unstructured data normalization — PDFs, scrapes, raw text require MinHash deduplication + semantic clustering.

### Feature Stores
- Centralized repository for computed features, serving both training (offline) and inference (online).
- **Online/offline consistency**: Features computed in batch must match online serving values — point-in-time correct feature stores prevent temporal leakage.
- **Schema evolution**: Handle missing data, type changes, new features without breaking downstream models.
- Tools: Feast, Tecton, Hopsworks.

### Data Quality
- **Temporal leakage prevention**: Strictly enforce chronological boundaries — no future information in training features.
- **Label quality**: Human-in-the-loop annotation, active learning for edge cases, frontier-model auto-labeling with constitution-based filtering.
- **Multimodal drift detection**: Kolmogorov-Smirnov tests on latent space distributions when non-text inputs shift.

---

## 2. Model Serving

### Batch vs. Real-Time Serving

| Dimension | Batch | Real-Time |
|---|---|---|
| Latency | Minutes to hours | < 100 ms |
| Use case | Daily recommendations,报表 | Ad ranking, fraud detection |
| Infrastructure | Spark, scheduled jobs | Model servers (Triton, vLLM) |
| Cost | Lower (amortized) | Higher (always-on GPU) |

### Inference Optimization
- **Quantization**: INT8, FP4, GPTQ, AWQ — shrink model for edge/cloud inference.
- **KV-Cache management**: PagedAttention (vLLM) eliminates fragmentation; manages KV cache at OS level.
- **Continuous batching**: Dynamic iteration-level scheduling — inject new requests as soon as a sequence emits `<EOS>`.
- **Prefix/context caching**: Cache KV states of common system prompts to bypass prefill computation.
- **Hardware kernel fusion**: FlashAttention fuses attention ops, keeps data in SRAM.

### Autoscaling
- Scale based on queue depth, GPU utilization, or latency SLAs.
- **Cold start mitigation**: Pre-warmed model replicas, snapshot-based loading.

---

## 3. Monitoring & Drift Detection

### Concept Drift
- The relationship between inputs and target changes over time (e.g., economic shifts change purchasing behavior).
- **Detection**: Track a shadow model against ground-truth feedback; trigger retraining when KL-divergence crosses threshold.
- **Adaptive models**: Online learning with exponential decay weighting on recent data.

### Data Drift (Covariate Shift)
- Input distribution changes but P(Y|X) remains the same.
- **Population Stability Index (PSI)**: Quantifies distribution shift between training and serving data.
- PSI > 0.2 typically signals significant drift requiring investigation.

### Silent Failures
- Model maintains high overall accuracy but performance collapses for a specific subgroup.
- **Mitigation**: Slicing analytics, fairness dashboards, disparate impact metrics across demographic clusters.

### LLM-Specific Observability
- Standard metrics (F1, accuracy) insufficient for open-ended outputs.
- **LLM-as-a-Judge**: Calibrated smaller model evaluates outputs on Relevance, Hallucination, Toxicity rubrics.
- **Distributed tracing**: LangSmith/OpenTelemetry to trace multi-agent execution graphs.

---

## 4. A/B Testing & Experimentation

### Standard A/B Testing
- Randomly assign users to control (current model) and treatment (new model).
- Measure statistical significance on key metrics (CTR, revenue, engagement).
- **Pitfall**: Requires large sample sizes; high-variance metrics need weeks of data.

### CUPED (Controlled-experiment Using Pre-Experiment Data)
- Uses pre-experiment covariates to reduce variance by 30-50%.
- Halves required sample size for same statistical power.
- Particularly valuable when treatment effect is small relative to natural variance.

### Multi-Armed Bandits
- Balance exploration (trying new variants) vs. exploitation (serving best-known variant).
- Thompson Sampling, UCB1 algorithms — faster convergence than fixed A/B tests.
- Best for cold-start scenarios or rapidly changing environments.

---

## 5. CI/CD for ML

### Training Pipeline
- **Version control**: DVC for data/model versioning, MLflow for experiment tracking.
- **Reproducibility**: Seed固定, Docker containers, Conda environments, exact dependency pinning.
- **Fault tolerance**: Async checkpointing to separate storage; automated node-recovery in distributed training.

### Deployment Pipeline
- **Shadow deployment**: New model serves alongside production but doesn't affect users; compare outputs.
- **Canary release**: Route 1-5% of traffic to new model; monitor for degradation before full rollout.
- **Blue-green deployment**: Maintain two identical environments; swap traffic atomically.
- **Rollback**: Automated rollback if drift metrics or error rates exceed thresholds.

### Infrastructure
- **Distributed training**: 3D parallelism (Tensor + Pipeline + Data) via Megatron-LM, DeepSpeed ZeRO.
- **Optimiser memory**: ZeRO stages partition optimizer states, gradients, and parameters across cluster.
- **Environment isolation**: Conda/miniconda with lazy-loading shell hooks; avoid system-wide package managers.

---

## 6. Production Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|---|---|---|
| Training-serving skew | Good offline metrics, poor production | Point-in-time correct features |
| Feature leakage | Inflated offline AUC, collapse in prod | Strict temporal boundaries |
| Feedback loop bias | Model reinforces its own biases | Inject exploration / diversity |
| Silent subgroup failure | High avg accuracy, minority poor | Slice-based monitoring |
| Model staleness | Performance slowly degrades | Scheduled retraining + drift triggers |
