# Complete RLHF + PPO Training System
## Reinforcement Learning from Human Feedback with Reward Model and Proximal Policy Optimization

**Date:** February 3, 2026  
**Purpose:** Align language models with human preferences using RLHF  
**Techniques:** Reward Model, PPO, Human Feedback Integration

---

## Overview

**RLHF (Reinforcement Learning from Human Feedback)** là kỹ thuật được dùng để huấn luyện:
- ChatGPT
- Claude
- Gemini
- Và hầu hết các LLM hiện đại

**3 Stages:**
1. **Supervised Fine-Tuning (SFT)** - Huấn luyện trên dữ liệu chất lượng cao
2. **Reward Model Training** - Học từ feedback con người
3. **PPO Training** - Tối ưu hóa policy dựa trên reward

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    RLHF Pipeline                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Stage 1: Human Feedback Collection                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Prompt → Generate 2 Responses → Human Preference│   │
│  │ (A vs B) → Collect Feedback                     │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                               │
│  Stage 2: Reward Model Training                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Input: (Prompt, Response A, Response B)         │   │
│  │ Target: Preference (A > B, B > A, or Tie)      │   │
│  │ Learn: Bradley-Terry Model                      │   │
│  │ Output: Reward Model r(x, y)                    │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                               │
│  Stage 3: PPO Policy Training                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Policy: π(y|x)                                  │   │
│  │ Value: V(x)                                     │   │
│  │ Reward: r(x, y) from Reward Model              │   │
│  │ Optimize: PPO Objective                         │   │
│  │ Output: Aligned Policy                          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Stage 1: Human Feedback Collection

### Preference Data Format

```python
{
    "prompt": "What is machine learning?",
    "response_a": "Machine learning is a subset of AI.",
    "response_b": "ML learns from data without explicit programming.",
    "preference": 1,  # 0 = A better, 1 = B better, 2 = tie
    "confidence": 0.9,
    "reasoning": "Response B is more comprehensive"
}
```

### Collection Process

1. **Generate Candidates** - Generate 2 responses for each prompt
2. **Human Annotation** - Humans choose which is better
3. **Collect Feedback** - Store preference and confidence
4. **Build Dataset** - Accumulate feedback data

### Example

```python
from rlhf_ppo_system import RLHFPipeline

pipeline = RLHFPipeline()

# Collect feedback
pipeline.stage1_collect_feedback(
    prompt="What is machine learning?",
    response_a="Machine learning is a subset of artificial intelligence.",
    response_b="ML learns from data without being explicitly programmed.",
    preference=1,  # B is better
    confidence=0.9,
    reasoning="Response B is more comprehensive and accurate"
)
```

---

## Stage 2: Reward Model Training

### Reward Model Architecture

```
Input (Prompt + Response)
    ↓
Embedding Layer
    ↓
Transformer Encoder (2-4 layers)
    ↓
Last Token Representation
    ↓
Reward Head (MLP)
    ↓
Output: Scalar Reward r(x, y)
```

### Bradley-Terry Model

The reward model learns to predict preferences using Bradley-Terry model:

```
P(A > B) = sigmoid(r_a - r_b)

Loss = -log(P(preferred > non-preferred))
```

### Training Process

```python
# Train reward model
pipeline.stage2_train_reward_model(
    num_epochs=3,
    batch_size=32
)
```

### Loss Function

```
L_reward = -log(sigmoid(r_preferred - r_non_preferred))
```

### Key Points

- **Preference Learning** - Learn to rank responses
- **Scalar Reward** - Single reward value per response
- **Contrastive Learning** - Compare pairs of responses
- **Generalization** - Learn general preference patterns

---

## Stage 3: PPO Training

### PPO Algorithm

**Proximal Policy Optimization** is a state-of-the-art policy gradient algorithm:

```
Objective:
L^CLIP(θ) = E_t[min(r_t(θ) Â_t, clip(r_t(θ), 1-ε, 1+ε) Â_t)]

Where:
- r_t(θ) = π_θ(a_t|s_t) / π_old(a_t|s_t)  (probability ratio)
- Â_t = advantage estimate
- ε = clip parameter (typically 0.2)
```

### Policy Network

```
Input (Prompt)
    ↓
Embedding Layer
    ↓
Transformer Encoder
    ↓
Policy Head → Action Logits
    ↓
Value Head → Value Estimate
```

### Advantage Estimation (GAE)

```
Generalized Advantage Estimation:
Â_t = δ_t + (γλ)δ_{t+1} + (γλ)²δ_{t+2} + ...

Where:
δ_t = r_t + γV(s_{t+1}) - V(s_t)  (TD residual)
```

### PPO Loss

```
L_total = L_policy + 0.5 * L_value - β * H(π)

Where:
- L_policy = PPO clipped objective
- L_value = MSE(V_predicted, V_target)
- H(π) = entropy bonus (exploration)
```

### Training Process

```python
# Train policy with PPO
pipeline.stage3_train_policy_with_ppo(
    num_epochs=3,
    batch_size=32
)
```

---

## Key Concepts

### 1. Reward Model

**Purpose:** Learn human preferences  
**Input:** (Prompt, Response)  
**Output:** Scalar reward  
**Training:** Preference pairs (A vs B)

```
r_model(prompt, response) → scalar reward
```

### 2. Policy Network

**Purpose:** Generate high-reward responses  
**Input:** Prompt  
**Output:** Response distribution  
**Training:** PPO objective with reward model

```
π(response | prompt) → probability distribution
```

### 3. Value Function

**Purpose:** Estimate expected return  
**Input:** Prompt  
**Output:** Value estimate  
**Training:** Regression on returns

```
V(prompt) → expected return
```

### 4. Advantage Function

**Purpose:** Measure how good an action is relative to average  
**Formula:** A(s,a) = Q(s,a) - V(s)  
**Benefit:** Reduces variance in policy gradient

```
Advantage = Return - Value Estimate
```

---

## Complete Training Loop

### Step 1: Initialize

```python
pipeline = RLHFPipeline(vocab_size=50257)
```

### Step 2: Collect Feedback

```python
for prompt in prompts:
    response_a = generate(prompt, model_a)
    response_b = generate(prompt, model_b)
    
    preference = get_human_preference(response_a, response_b)
    
    pipeline.stage1_collect_feedback(
        prompt, response_a, response_b, preference
    )
```

### Step 3: Train Reward Model

```python
pipeline.stage2_train_reward_model(
    num_epochs=3,
    batch_size=32
)

# Reward model now predicts: r(prompt, response)
```

### Step 4: Generate Rollouts

```python
for prompt in prompts:
    response = policy.generate(prompt)
    reward = reward_model(prompt, response)
    value = value_function(prompt)
    advantage = reward - value
```

### Step 5: Train Policy with PPO

```python
pipeline.stage3_train_policy_with_ppo(
    num_epochs=3,
    batch_size=32
)

# Policy now optimized for high rewards
```

### Step 6: Repeat

Iterate steps 2-5 multiple times for continuous improvement

---

## Hyperparameters

### Reward Model

| Parameter | Value | Description |
|-----------|-------|-------------|
| Learning Rate | 1e-4 | Adam optimizer |
| Batch Size | 32 | Preference pairs |
| Epochs | 3-5 | Training iterations |
| Hidden Size | 768 | Model dimension |
| Num Layers | 2-4 | Transformer layers |

### PPO

| Parameter | Value | Description |
|-----------|-------|-------------|
| Learning Rate | 1e-4 | Adam optimizer |
| Gamma (γ) | 0.99 | Discount factor |
| GAE Lambda (λ) | 0.95 | Advantage smoothing |
| Clip Ratio (ε) | 0.2 | PPO clipping |
| Entropy Coef (β) | 0.01 | Exploration bonus |
| Epochs per Batch | 3 | Policy update iterations |

---

## Loss Functions

### Reward Model Loss

```
L_reward = -log(sigmoid(r_preferred - r_non_preferred))

Bradley-Terry model for preference learning
```

### PPO Policy Loss

```
L_policy = E[min(r_t * Â_t, clip(r_t, 1-ε, 1+ε) * Â_t)]

Clipped objective for stable training
```

### Value Loss

```
L_value = MSE(V_predicted, V_target)

Regression on returns
```

### Entropy Bonus

```
L_entropy = -β * H(π) = β * Σ π(a|s) * log(π(a|s))

Encourages exploration
```

### Total Loss

```
L_total = L_policy + 0.5 * L_value - β * L_entropy

Balanced training
```

---

## Best Practices

### 1. Data Quality

✅ **Do:**
- Collect diverse feedback
- Use confident annotators
- Ensure consistent labeling
- Validate data quality

❌ **Don't:**
- Use low-quality feedback
- Mix different annotation styles
- Include biased preferences
- Ignore annotation disagreement

### 2. Reward Model Training

✅ **Do:**
- Train on diverse preferences
- Monitor loss curves
- Validate on held-out data
- Check reward model calibration

❌ **Don't:**
- Overfit to small dataset
- Ignore preference distribution
- Train without validation
- Use uncalibrated rewards

### 3. PPO Training

✅ **Do:**
- Use appropriate learning rates
- Monitor policy divergence
- Check advantage estimates
- Validate on test prompts

❌ **Don't:**
- Use too high learning rates
- Train for too many epochs
- Ignore KL divergence
- Overfit to reward model

### 4. Monitoring

✅ **Do:**
- Track reward model accuracy
- Monitor policy performance
- Check KL divergence from base model
- Validate on human evaluation

❌ **Don't:**
- Ignore training metrics
- Train blindly
- Skip validation
- Assume convergence

---

## Troubleshooting

### Problem: Reward Model Not Learning

**Causes:**
- Insufficient feedback data
- Low quality annotations
- Imbalanced preferences
- Poor hyperparameters

**Solutions:**
- Collect more feedback
- Improve annotation quality
- Balance preference distribution
- Tune learning rate

### Problem: Policy Diverging from Base Model

**Causes:**
- Too high learning rate
- Insufficient KL penalty
- Reward model overfitting
- Too many PPO epochs

**Solutions:**
- Lower learning rate
- Increase KL penalty
- Validate reward model
- Reduce PPO epochs

### Problem: Reward Hacking

**Causes:**
- Reward model exploiting edge cases
- Unrealistic responses
- Gaming the reward signal

**Solutions:**
- Add KL penalty to objective
- Monitor response quality
- Use human evaluation
- Diversify reward model training

---

## Evaluation

### Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Reward Model Accuracy** | Preference prediction accuracy | >80% |
| **Policy Reward** | Average reward on test set | High |
| **KL Divergence** | Distance from base model | Low |
| **Human Evaluation** | Human preference for aligned model | >70% |
| **Response Quality** | Fluency, coherence, correctness | High |

### Validation

```python
# Get training status
status = pipeline.get_training_status()

print(f"Feedback Statistics: {status['feedback_statistics']}")
print(f"Reward Model Metrics: {status['reward_model_metrics']}")
print(f"PPO Metrics: {status['ppo_metrics']}")
```

---

## References

### Papers

1. **RLHF Origins**
   - Christiano et al. (2017) - "Deep Reinforcement Learning from Human Preferences"

2. **PPO Algorithm**
   - Schulman et al. (2017) - "Proximal Policy Optimization Algorithms"

3. **Reward Model**
   - Ziegler et al. (2019) - "Fine-Tuning Language Models from Human Preferences"

4. **InstructGPT/ChatGPT**
   - Ouyang et al. (2022) - "Training language models to follow instructions with human feedback"

### Key Concepts

- **Bradley-Terry Model** - Preference learning
- **Generalized Advantage Estimation (GAE)** - Advantage estimation
- **Proximal Policy Optimization (PPO)** - Policy optimization
- **KL Divergence** - Divergence penalty
- **Entropy Bonus** - Exploration encouragement

---

## Conclusion

**RLHF + PPO is the state-of-the-art approach for aligning language models with human preferences.**

**Key Steps:**
1. Collect human feedback on response pairs
2. Train reward model to predict preferences
3. Use PPO to optimize policy based on rewards
4. Iterate for continuous improvement

**Result:** Language models that are helpful, harmless, and honest!

---

**System ready for production RLHF training!** 🚀
