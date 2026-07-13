---
difficulty: hard
last_sent:
review_count: 0
tags:
  - nlp
  - rnn
  - lstm
  - sequence
topic: ml-ai
---

# Sequence Models: RNN, LSTM, and GRU

Recurrent Neural Networks (RNNs) process sequential data by maintaining a hidden state that carries information across timesteps. They were the dominant architecture for NLP and time series before transformers. Understanding them explains both historical context and why transformers won.

## RNN Architecture

An RNN processes a sequence one element at a time, updating a hidden state:

$$h_t = \tanh(W_{hh} h_{t-1} + W_{xh} x_t + b)$$
$$y_t = W_{hy} h_t + b_y$$

The same weights are shared across all timesteps — this parameter sharing allows RNNs to handle variable-length sequences.

```python
import torch
import torch.nn as nn

class SimpleRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.hidden_size = hidden_size
        self.W_xh = nn.Linear(input_size, hidden_size)
        self.W_hh = nn.Linear(hidden_size, hidden_size)
        self.W_hy = nn.Linear(hidden_size, output_size)
    
    def forward(self, x, h_prev=None):
        # x: (batch, seq_len, input_size)
        batch_size, seq_len, _ = x.shape
        if h_prev is None:
            h_prev = torch.zeros(batch_size, self.hidden_size)
        
        outputs = []
        h_t = h_prev
        for t in range(seq_len):
            h_t = torch.tanh(self.W_xh(x[:, t]) + self.W_hh(h_t))
            y_t = self.W_hy(h_t)
            outputs.append(y_t)
        
        return torch.stack(outputs, dim=1), h_t
```

## The Vanishing Gradient Problem

During backpropagation through time (BPTT), gradients are multiplied by the same weight matrix $W_{hh}$ at each timestep:

$$\frac{\partial h_T}{\partial h_t} = \prod_{k=t+1}^{T} \frac{\partial h_k}{\partial h_{k-1}}$$

When $||W_{hh}|| < 1$, gradients vanish exponentially; when $||W_{hh}|| > 1$, they explode. In practice, gradients almost always **vanish**, making it impossible for vanilla RNNs to learn long-range dependencies (e.g., remembering a word from 50+ tokens ago).

| Sequence Length | Gradient Magnitude | Learning Ability |
|-----------------|-------------------|------------------|
| 5-10 steps | Moderate | Good |
| 20-50 steps | Very small | Poor |
| 100+ steps | Essentially zero | None |

## LSTM (Long Short-Term Memory)

LSTM (Hochreiter & Schmidhuber, 1997) solves vanishing gradients with a **cell state** (highway) and three **gates** that control information flow:

**Forget gate**: What to discard from cell state
$$f_t = \sigma(W_f [h_{t-1}, x_t] + b_f)$$

**Input gate**: What new information to store
$$i_t = \sigma(W_i [h_{t-1}, x_t] + b_i)$$
$$\tilde{C}_t = \tanh(W_C [h_{t-1}, x_t] + b_C)$$

**Cell state update**: Combines forget and input
$$C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$$

**Output gate**: What to output from cell state
$$o_t = \sigma(W_o [h_{t-1}, x_t] + b_o)$$
$$h_t = o_t \odot \tanh(C_t)$$

The cell state $C_t$ flows through time with only element-wise multiplications (no matrix multiplication), preventing gradient vanishing:

```python
class LSTMCell(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        combined = input_size + hidden_size
        self.W_f = nn.Linear(combined, hidden_size)
        self.W_i = nn.Linear(combined, hidden_size)
        self.W_c = nn.Linear(combined, hidden_size)
        self.W_o = nn.Linear(combined, hidden_size)
    
    def forward(self, x_t, h_prev, c_prev):
        combined = torch.cat([h_prev, x_t], dim=1)
        f = torch.sigmoid(self.W_f(combined))
        i = torch.sigmoid(self.W_i(combined))
        c_tilde = torch.tanh(self.W_c(combined))
        o = torch.sigmoid(self.W_o(combined))
        
        c_t = f * c_prev + i * c_tilde
        h_t = o * torch.tanh(c_t)
        return h_t, c_t
```

## GRU (Gated Recurrent Unit)

GRU (Cho et al., 2014) simplifies LSTM by merging the forget and input gates into a single **update gate** and combining cell state with hidden state:

$$z_t = \sigma(W_z [h_{t-1}, x_t])$$ (update gate)
$$r_t = \sigma(W_r [h_{t-1}, x_t])$$ (reset gate)
$$\tilde{h}_t = \tanh(W [r_t \odot h_{t-1}, x_t])$$
$$h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t$$

| Feature | LSTM | GRU |
|---------|------|-----|
| Gates | 3 (forget, input, output) | 2 (update, reset) |
| Parameters | More | Fewer (~75% of LSTM) |
| Training speed | Slower | Faster |
| Performance | Slightly better on long sequences | Comparable on most tasks |

## Bidirectional RNNs

Process the sequence in both directions and concatenate outputs:

$$h_t = [\overrightarrow{h_t}; \overleftarrow{h_t}]$$

This allows the model to use both past and future context. Essential for tasks like NER and sentiment analysis where the full sequence is available.

**Limitation**: Cannot be used for autoregressive generation (you don't have future context when generating).

## Why Transformers Superseded RNNs

| Limitation | RNN | Transformer |
|------------|-----|-------------|
| Parallelization | Sequential (slow) | Fully parallel |
| Long-range dependencies | Vanishing gradients | Self-attention (direct) |
| Training speed | $O(n)$ sequential steps | $O(1)$ parallel steps |
| Memory | $O(1)$ per timestep | $O(n^2)$ attention matrix |
| Hardware utilization | Poor on GPUs | Excellent on GPUs |

Transformers with self-attention can directly attend to any token, eliminating the sequential bottleneck entirely. The $O(n^2)$ memory cost is addressed by efficient attention variants (FlashAttention, sparse attention).

## Key Takeaways

- RNNs maintain hidden state to process sequences, but suffer from vanishing gradients
- LSTM's cell state and gating mechanism solve vanishing gradients for moderate-length sequences
- GRU is a simpler, faster alternative with comparable performance
- Bidirectional RNNs use both past and future context but aren't suitable for generation
- Transformers replaced RNNs due to parallelization and better long-range dependency handling
- Understanding RNNs explains the motivation behind transformer architectures

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Not packing padded sequences | Model learns from padding tokens | Use `nn.utils.rnn.pack_padded_sequence` |
| Forgetting to detach hidden state | Memory grows, gradients explode | `h.detach()` when not backpropagating through time |
| Mismatched hidden state size | Runtime error | Ensure `hidden_size` matches across layers |
| Using RNN for long sequences (>100) | Poor performance | Switch to transformer or add attention |
| Bidirectional in autoregressive model | Information leakage | Use unidirectional for generation |
| Not shuffling sequence order | Biased training | Always shuffle training sequences |
