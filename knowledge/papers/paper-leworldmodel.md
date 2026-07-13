---
topic: papers
difficulty: hard
tags: [paper, world-model, video-prediction, representation-learning, planning, robotics, dynamics]
last_sent:
review_count: 0
---

# LeWorldModel: Learning a World Model by Watching Videos

## Problem & Motivation
Building world models that can predict future states of the environment is fundamental for robotic planning and embodied AI. Existing video prediction models either lack the abstract representations needed for planning, or require extensive interaction data that is expensive to collect. The question: can we learn a world model purely from video observation that is useful for robotic control?

## Key Idea / Architecture
LeWorldModel combines several key ideas:
1. **JEPA-based representation learning**: Uses joint-embedding predictive architecture to learn video representations
2. **Latent dynamics model**: Learns transition dynamics in the latent space (not pixel space)
3. **Action conditioning**: The dynamics model conditions on actions to predict future states
4. **Video pretraining**: Trained on large-scale video datasets (e.g., Ego4D, YouTube)
5. **Fine-tuning for control**: The pretrained world model is fine-tuned on robot interaction data

The architecture has:
- An encoder that maps video frames to latent representations
- A dynamics model that predicts future latent states given current state and action
- A decoder for visualization (but the core model operates entirely in latent space)

The key insight is that learning dynamics in a well-learned latent space (via JEPA) is more efficient and generalizable than learning in pixel space.

## Key Contributions
- First demonstration of learning a useful world model from video observation for robotic control
- JEPA-based representation learning for temporal sequences (extending I-JEPA to video)
- Latent space dynamics model that generalizes across environments
- Positive transfer from video pretraining to robotic control tasks
- The model can be used for planning: roll out hypothetical action sequences in latent space

## Results
- **Video prediction**: Competitive with state-of-the-art video prediction models on standard benchmarks
- **Robotic control**: Successfully learns control policies from the learned world model
- **Data efficiency**: Pretraining on videos significantly reduces the amount of robot interaction data needed
- **Generalization**: The world model generalizes to novel environments and tasks not seen during pretraining
- **Planning**: The model supports forward simulation for planning action sequences
- **Transfer**: Video pretraining transfers to robotic domains despite the domain gap

## Why It Matters / Impact
LeWorldModel represents a significant step toward the long-standing goal of learning world models from observation. By combining JEPA representation learning with latent dynamics modeling, it shows that robots can learn about their environment by watching videos before interacting. This is crucial for scaling robotics, as real-world interaction data is expensive and dangerous to collect. The approach connects to theories of embodied cognition and could enable more sample-efficient robot learning.

## Weaknesses / Limitations
- The domain gap between YouTube/egocentric videos and robot interaction is significant
- Latent space planning is computationally expensive for long-horizon tasks
- The model doesn't handle contact-rich manipulation well
- Video pretraining data may contain irrelevant or misleading dynamics
- Limited evaluation on real-world robots (primarily simulated environments)
- The architecture requires careful balancing of encoder, dynamics, and decoder components
