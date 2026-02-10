#!/usr/bin/env python3
"""
Complete RLHF (Reinforcement Learning from Human Feedback) System
With Reward Model and PPO (Proximal Policy Optimization)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from collections import defaultdict
from dataclasses import dataclass
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== DATA STRUCTURES ==========

@dataclass
class HumanFeedback:
    """Human feedback on two responses"""
    prompt: str
    response_a: str
    response_b: str
    preference: int  # 0 = A better, 1 = B better, 2 = tie
    confidence: float  # 0-1
    reasoning: str


@dataclass
class PPOBatch:
    """Batch for PPO training"""
    prompts: List[str]
    responses: List[str]
    rewards: torch.Tensor
    values: torch.Tensor
    log_probs: torch.Tensor
    advantages: torch.Tensor
    returns: torch.Tensor


# ========== HUMAN FEEDBACK SYSTEM ==========

class HumanFeedbackCollector:
    """Collect and manage human feedback"""
    
    def __init__(self):
        self.feedback_data = []
        self.preference_counts = defaultdict(int)
        
        logger.info("Initialized Human Feedback Collector")
    
    def collect_feedback(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        preference: int,
        confidence: float = 0.8,
        reasoning: str = ""
    ) -> HumanFeedback:
        """Collect human feedback on two responses"""
        
        feedback = HumanFeedback(
            prompt=prompt,
            response_a=response_a,
            response_b=response_b,
            preference=preference,
            confidence=confidence,
            reasoning=reasoning
        )
        
        self.feedback_data.append(feedback)
        self.preference_counts[preference] += 1
        
        logger.info(f"Collected feedback: A vs B (preference={preference}, confidence={confidence:.1%})")
        
        return feedback
    
    def get_preference_dataset(self) -> List[Tuple[str, str, str, int]]:
        """Get dataset for reward model training"""
        return [(f.prompt, f.response_a, f.response_b, f.preference) for f in self.feedback_data]
    
    def get_statistics(self) -> Dict:
        """Get feedback statistics"""
        total = len(self.feedback_data)
        
        return {
            'total_feedback': total,
            'preference_a': self.preference_counts[0],
            'preference_b': self.preference_counts[1],
            'preference_tie': self.preference_counts[2],
            'avg_confidence': np.mean([f.confidence for f in self.feedback_data]) if self.feedback_data else 0
        }


# ========== PREFERENCE DATASET ==========

class PreferenceDataset(Dataset):
    """Dataset for reward model training"""
    
    def __init__(self, feedback_data: List[Tuple[str, str, str, int]], tokenizer, max_length: int = 512):
        self.feedback_data = feedback_data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self) -> int:
        return len(self.feedback_data)
    
    def __getitem__(self, idx: int) -> Dict:
        prompt, response_a, response_b, preference = self.feedback_data[idx]
        
        # Tokenize
        prompt_tokens = self.tokenizer.encode(prompt)[:self.max_length // 2]
        response_a_tokens = self.tokenizer.encode(response_a)[:self.max_length // 2]
        response_b_tokens = self.tokenizer.encode(response_b)[:self.max_length // 2]
        
        # Combine
        input_a = prompt_tokens + response_a_tokens
        input_b = prompt_tokens + response_b_tokens
        
        # Pad
        if len(input_a) < self.max_length:
            input_a = input_a + [0] * (self.max_length - len(input_a))
        if len(input_b) < self.max_length:
            input_b = input_b + [0] * (self.max_length - len(input_b))
        
        return {
            'input_a': torch.tensor(input_a[:self.max_length], dtype=torch.long),
            'input_b': torch.tensor(input_b[:self.max_length], dtype=torch.long),
            'preference': torch.tensor(preference, dtype=torch.long)
        }


# ========== REWARD MODEL ==========

class RewardModel(nn.Module):
    """Reward model for learning human preferences"""
    
    def __init__(self, vocab_size: int, hidden_size: int = 768, num_layers: int = 2):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=hidden_size,
                nhead=8,
                dim_feedforward=3072,
                batch_first=True
            ),
            num_layers=num_layers
        )
        
        self.reward_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, 1)
        )
        
        logger.info(f"Initialized Reward Model (vocab_size={vocab_size}, hidden_size={hidden_size})")
    
    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        # Embed
        x = self.embedding(input_ids)
        
        # Encode
        x = self.encoder(x)
        
        # Get reward from last token
        x = x[:, -1, :]
        
        # Predict reward
        reward = self.reward_head(x)
        
        return reward


class RewardModelTrainer:
    """Train reward model from human feedback"""
    
    def __init__(self, model: RewardModel, learning_rate: float = 1e-4):
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        self.metrics = defaultdict(list)
        
        logger.info(f"Initialized Reward Model Trainer on {self.device}")
    
    def train_step(self, batch: Dict) -> float:
        """Train on batch"""
        self.model.train()
        
        input_a = batch['input_a'].to(self.device)
        input_b = batch['input_b'].to(self.device)
        preference = batch['preference'].to(self.device)
        
        # Forward pass
        reward_a = self.model(input_a)
        reward_b = self.model(input_b)
        
        # Compute loss (Bradley-Terry model)
        # P(A > B) = sigmoid(r_a - r_b)
        logits = reward_a - reward_b
        
        # Cross-entropy loss
        loss = F.cross_entropy(
            torch.cat([logits, -logits], dim=1),
            preference
        )
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()
        
        self.metrics['loss'].append(loss.item())
        
        return loss.item()
    
    def get_reward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Get reward for input"""
        self.model.eval()
        
        with torch.no_grad():
            input_ids = input_ids.to(self.device)
            reward = self.model(input_ids)
        
        return reward


# ========== PPO ALGORITHM ==========

class PPOPolicy(nn.Module):
    """Policy network for PPO"""
    
    def __init__(self, vocab_size: int, hidden_size: int = 768, num_layers: int = 2):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=hidden_size,
                nhead=8,
                dim_feedforward=3072,
                batch_first=True
            ),
            num_layers=num_layers
        )
        
        self.policy_head = nn.Linear(hidden_size, vocab_size)
        self.value_head = nn.Linear(hidden_size, 1)
        
        logger.info(f"Initialized PPO Policy (vocab_size={vocab_size})")
    
    def forward(self, input_ids: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass"""
        # Embed
        x = self.embedding(input_ids)
        
        # Encode
        x = self.encoder(x)
        
        # Get last token representation
        x_last = x[:, -1, :]
        
        # Policy logits
        policy_logits = self.policy_head(x)
        
        # Value
        value = self.value_head(x_last)
        
        return policy_logits, value


class PPOTrainer:
    """PPO training algorithm"""
    
    def __init__(
        self,
        policy: PPOPolicy,
        reward_model: RewardModel,
        learning_rate: float = 1e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_ratio: float = 0.2,
        entropy_coef: float = 0.01
    ):
        self.policy = policy
        self.reward_model = reward_model
        self.optimizer = torch.optim.Adam(policy.parameters(), lr=learning_rate)
        
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_ratio = clip_ratio
        self.entropy_coef = entropy_coef
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.policy.to(self.device)
        self.reward_model.to(self.device)
        
        self.metrics = defaultdict(list)
        
        logger.info(f"Initialized PPO Trainer on {self.device}")
    
    def compute_advantages(
        self,
        rewards: torch.Tensor,
        values: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Compute advantages using GAE"""
        
        advantages = []
        gae = 0
        
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[t + 1]
            
            delta = rewards[t] + self.gamma * next_value - values[t]
            gae = delta + self.gamma * self.gae_lambda * gae
            advantages.insert(0, gae)
        
        advantages = torch.tensor(advantages, dtype=torch.float32)
        returns = advantages + values
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        return advantages, returns
    
    def train_step(self, batch: PPOBatch, num_epochs: int = 3) -> Dict:
        """Train on batch"""
        
        losses = defaultdict(float)
        
        for epoch in range(num_epochs):
            self.policy.train()
            
            # Forward pass
            policy_logits, values = self.policy(batch.prompts)
            
            # Compute log probabilities
            log_probs_new = F.log_softmax(policy_logits, dim=-1)
            
            # Compute policy loss (PPO clipped objective)
            ratio = torch.exp(log_probs_new - batch.log_probs)
            surr1 = ratio * batch.advantages
            surr2 = torch.clamp(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio) * batch.advantages
            policy_loss = -torch.min(surr1, surr2).mean()
            
            # Compute value loss
            value_loss = F.mse_loss(values.squeeze(), batch.returns)
            
            # Compute entropy bonus
            entropy = -(log_probs_new * torch.exp(log_probs_new)).sum(dim=-1).mean()
            
            # Total loss
            total_loss = policy_loss + 0.5 * value_loss - self.entropy_coef * entropy
            
            # Backward pass
            self.optimizer.zero_grad()
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 1.0)
            self.optimizer.step()
            
            losses['policy_loss'] += policy_loss.item()
            losses['value_loss'] += value_loss.item()
            losses['entropy'] += entropy.item()
            losses['total_loss'] += total_loss.item()
        
        # Average over epochs
        for key in losses:
            losses[key] /= num_epochs
            self.metrics[key].append(losses[key])
        
        return losses


# ========== COMPLETE RLHF PIPELINE ==========

class RLHFPipeline:
    """Complete RLHF training pipeline"""
    
    def __init__(self, vocab_size: int = 50257):
        self.feedback_collector = HumanFeedbackCollector()
        self.reward_model = RewardModel(vocab_size)
        self.reward_trainer = RewardModelTrainer(self.reward_model)
        
        self.policy = PPOPolicy(vocab_size)
        self.ppo_trainer = PPOTrainer(self.policy, self.reward_model)
        
        logger.info("Initialized Complete RLHF Pipeline")
    
    def stage1_collect_feedback(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        preference: int,
        confidence: float = 0.8,
        reasoning: str = ""
    ):
        """Stage 1: Collect human feedback"""
        
        self.feedback_collector.collect_feedback(
            prompt, response_a, response_b, preference, confidence, reasoning
        )
    
    def stage2_train_reward_model(self, num_epochs: int = 3, batch_size: int = 32):
        """Stage 2: Train reward model on human feedback"""
        
        logger.info("Stage 2: Training Reward Model")
        
        feedback_data = self.feedback_collector.get_preference_dataset()
        
        if not feedback_data:
            logger.warning("No feedback data available")
            return
        
        dataset = PreferenceDataset(feedback_data, tokenizer=None, max_length=512)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        for epoch in range(num_epochs):
            total_loss = 0
            
            for batch in dataloader:
                loss = self.reward_trainer.train_step(batch)
                total_loss += loss
            
            avg_loss = total_loss / len(dataloader)
            logger.info(f"Epoch {epoch+1}/{num_epochs}: Reward Model Loss = {avg_loss:.4f}")
    
    def stage3_train_policy_with_ppo(self, num_epochs: int = 3, batch_size: int = 32):
        """Stage 3: Train policy with PPO using reward model"""
        
        logger.info("Stage 3: Training Policy with PPO")
        
        # This would use the reward model to provide rewards
        # In practice, you would generate responses and get rewards
        
        for epoch in range(num_epochs):
            logger.info(f"PPO Epoch {epoch+1}/{num_epochs}")
            # Training loop would go here
    
    def get_training_status(self) -> Dict:
        """Get training status"""
        
        feedback_stats = self.feedback_collector.get_statistics()
        reward_metrics = dict(self.reward_trainer.metrics)
        ppo_metrics = dict(self.ppo_trainer.metrics)
        
        return {
            'feedback_statistics': feedback_stats,
            'reward_model_metrics': reward_metrics,
            'ppo_metrics': ppo_metrics,
            'timestamp': datetime.now().isoformat()
        }


# ========== MAIN ==========

def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RLHF + PPO System")
    parser.add_argument("--stage", choices=["collect", "reward", "ppo", "all"], default="all", help="Training stage")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = RLHFPipeline()
    
    logger.info("="*80)
    logger.info("RLHF + PPO TRAINING PIPELINE")
    logger.info("="*80)
    
    # Stage 1: Collect feedback
    if args.stage in ["collect", "all"]:
        logger.info("\nStage 1: Collecting Human Feedback")
        
        # Example feedback
        pipeline.stage1_collect_feedback(
            prompt="What is machine learning?",
            response_a="Machine learning is a subset of artificial intelligence.",
            response_b="ML learns from data without being explicitly programmed.",
            preference=1,
            confidence=0.9,
            reasoning="Response B is more comprehensive"
        )
        
        pipeline.stage1_collect_feedback(
            prompt="Explain neural networks",
            response_a="Neural networks are inspired by the brain.",
            response_b="Neural networks are computational models with layers of nodes.",
            preference=0,
            confidence=0.8,
            reasoning="Response A is clearer"
        )
        
        stats = pipeline.feedback_collector.get_statistics()
        logger.info(f"Feedback Statistics: {stats}")
    
    # Stage 2: Train reward model
    if args.stage in ["reward", "all"]:
        logger.info("\nStage 2: Training Reward Model")
        pipeline.stage2_train_reward_model(num_epochs=3, batch_size=2)
    
    # Stage 3: Train policy with PPO
    if args.stage in ["ppo", "all"]:
        logger.info("\nStage 3: Training Policy with PPO")
        pipeline.stage3_train_policy_with_ppo(num_epochs=2, batch_size=2)
    
    # Print status
    status = pipeline.get_training_status()
    logger.info("\n" + "="*80)
    logger.info("TRAINING STATUS")
    logger.info("="*80)
    logger.info(json.dumps(status, indent=2, default=str))


if __name__ == "__main__":
    main()
