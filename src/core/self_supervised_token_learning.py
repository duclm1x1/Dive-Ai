#!/usr/bin/env python3
"""
Self-Supervised Learning for Numerical Token Prediction
Learns from unlabeled data using multiple self-supervision techniques:
- Masked Language Modeling (MLM)
- Next Token Prediction (NTP)
- Contrastive Learning
- Denoising Autoencoder
- Numerical Pattern Recognition
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import tiktoken
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from collections import Counter, defaultdict
import re
from dataclasses import dataclass
import json
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== DATA STRUCTURES ==========

@dataclass
class SelfSupervisedBatch:
    """Batch for self-supervised learning"""
    original_tokens: torch.Tensor
    masked_tokens: torch.Tensor
    mask_positions: torch.Tensor
    next_tokens: torch.Tensor
    numerical_labels: torch.Tensor


# ========== DATASETS ==========

class SelfSupervisedTextDataset(Dataset):
    """Dataset for self-supervised learning from unlabeled text"""
    
    def __init__(
        self,
        texts: List[str],
        tokenizer,
        max_length: int = 512,
        mask_prob: float = 0.15,
        mask_token_id: int = 50256
    ):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.mask_prob = mask_prob
        self.mask_token_id = mask_token_id
        
        logger.info(f"Initialized dataset with {len(texts)} texts")
    
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict:
        text = self.texts[idx]
        
        # Tokenize
        tokens = self.tokenizer.encode(text)[:self.max_length]
        
        # Pad or truncate
        if len(tokens) < self.max_length:
            tokens = tokens + [0] * (self.max_length - len(tokens))
        else:
            tokens = tokens[:self.max_length]
        
        tokens = torch.tensor(tokens, dtype=torch.long)
        
        # Create masked version for MLM
        masked_tokens, mask_positions = self._create_masked_version(tokens.clone())
        
        # Create next token targets
        next_tokens = self._create_next_token_targets(tokens)
        
        # Create numerical labels
        numerical_labels = self._create_numerical_labels(tokens)
        
        return {
            'original_tokens': tokens,
            'masked_tokens': masked_tokens,
            'mask_positions': mask_positions,
            'next_tokens': next_tokens,
            'numerical_labels': numerical_labels,
            'text': text
        }
    
    def _create_masked_version(self, tokens: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Create masked version for MLM"""
        mask_positions = torch.zeros_like(tokens)
        
        for i in range(len(tokens)):
            if random.random() < self.mask_prob:
                mask_positions[i] = 1
                
                # 80% mask, 10% random, 10% keep
                rand = random.random()
                if rand < 0.8:
                    tokens[i] = self.mask_token_id
                elif rand < 0.9:
                    tokens[i] = random.randint(0, 50256)
                # else: keep original
        
        return tokens, mask_positions
    
    def _create_next_token_targets(self, tokens: torch.Tensor) -> torch.Tensor:
        """Create next token prediction targets"""
        next_tokens = torch.zeros_like(tokens)
        next_tokens[:-1] = tokens[1:]
        return next_tokens
    
    def _create_numerical_labels(self, tokens: torch.Tensor) -> torch.Tensor:
        """Create numerical understanding labels"""
        labels = torch.zeros_like(tokens)
        
        for i, token_id in enumerate(tokens):
            token_str = self.tokenizer.decode([token_id.item()])
            
            # Check if numerical
            if re.match(r'^-?\d+\.?\d*$', token_str.strip()):
                labels[i] = 1  # Numerical token
            elif token_str.strip() in ['+', '-', '*', '/', '%', '=']:
                labels[i] = 2  # Operator
            elif token_str.strip() in ['.', ',', '!', '?']:
                labels[i] = 3  # Punctuation
        
        return labels


# ========== SELF-SUPERVISED MODELS ==========

class MaskedLanguageModel(nn.Module):
    """Masked Language Modeling for self-supervision"""
    
    def __init__(self, vocab_size: int, hidden_size: int = 768, num_layers: int = 6):
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
        self.mlm_head = nn.Linear(hidden_size, vocab_size)
        
        logger.info(f"Initialized MLM with vocab_size={vocab_size}, hidden_size={hidden_size}")
    
    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        # Embed
        x = self.embedding(tokens)
        
        # Encode
        x = self.encoder(x)
        
        # Predict masked tokens
        logits = self.mlm_head(x)
        
        return logits


class NextTokenPredictor(nn.Module):
    """Next Token Prediction for self-supervision"""
    
    def __init__(self, vocab_size: int, hidden_size: int = 768, num_layers: int = 6):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.decoder = nn.TransformerDecoder(
            nn.TransformerDecoderLayer(
                d_model=hidden_size,
                nhead=8,
                dim_feedforward=3072,
                batch_first=True
            ),
            num_layers=num_layers
        )
        self.ntp_head = nn.Linear(hidden_size, vocab_size)
        
        logger.info(f"Initialized NTP with vocab_size={vocab_size}, hidden_size={hidden_size}")
    
    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        # Embed
        x = self.embedding(tokens)
        
        # Decode (causal)
        x = self.decoder(x, x)
        
        # Predict next tokens
        logits = self.ntp_head(x)
        
        return logits


class ContrastiveTokenEncoder(nn.Module):
    """Contrastive learning for token representations"""
    
    def __init__(self, vocab_size: int, hidden_size: int = 768, embedding_size: int = 128):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.encoder = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, embedding_size)
        )
        
        logger.info(f"Initialized Contrastive Encoder")
    
    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        # Embed
        x = self.embedding(tokens)
        
        # Encode to embedding space
        embeddings = self.encoder(x)
        
        # Normalize
        embeddings = F.normalize(embeddings, dim=-1)
        
        return embeddings


class DenoisingAutoencoder(nn.Module):
    """Denoising Autoencoder for numerical understanding"""
    
    def __init__(self, vocab_size: int, hidden_size: int = 768):
        super().__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Embedding(vocab_size, hidden_size),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU()
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(hidden_size // 2, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, vocab_size)
        )
        
        logger.info(f"Initialized Denoising Autoencoder")
    
    def forward(self, tokens: torch.Tensor, noise_level: float = 0.1) -> torch.Tensor:
        """Forward pass with noise"""
        # Add noise
        noisy_tokens = tokens.clone()
        mask = torch.rand_like(tokens, dtype=torch.float) < noise_level
        noisy_tokens[mask] = torch.randint(0, 50256, noisy_tokens[mask].shape)
        
        # Encode
        encoded = self.encoder(noisy_tokens)
        
        # Decode
        logits = self.decoder(encoded)
        
        return logits


class NumericalPatternLearner(nn.Module):
    """Learn numerical patterns through self-supervision"""
    
    def __init__(self, hidden_size: int = 768):
        super().__init__()
        
        self.pattern_detector = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 4)  # 4 classes: text, number, operator, punctuation
        )
        
        self.number_predictor = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, 1)  # Predict next number
        )
        
        logger.info(f"Initialized Numerical Pattern Learner")
    
    def forward(self, embeddings: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass"""
        # Detect pattern type
        pattern_logits = self.pattern_detector(embeddings)
        
        # Predict next number
        number_pred = self.number_predictor(embeddings)
        
        return pattern_logits, number_pred


# ========== SELF-SUPERVISED TRAINER ==========

class SelfSupervisedTrainer:
    """Trainer for self-supervised learning"""
    
    def __init__(
        self,
        mlm_model: MaskedLanguageModel,
        ntp_model: NextTokenPredictor,
        contrastive_model: ContrastiveTokenEncoder,
        denoising_model: DenoisingAutoencoder,
        numerical_model: NumericalPatternLearner,
        learning_rate: float = 1e-4,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.mlm_model = mlm_model.to(device)
        self.ntp_model = ntp_model.to(device)
        self.contrastive_model = contrastive_model.to(device)
        self.denoising_model = denoising_model.to(device)
        self.numerical_model = numerical_model.to(device)
        
        self.device = device
        
        # Optimizers
        self.mlm_optimizer = torch.optim.AdamW(mlm_model.parameters(), lr=learning_rate)
        self.ntp_optimizer = torch.optim.AdamW(ntp_model.parameters(), lr=learning_rate)
        self.contrastive_optimizer = torch.optim.AdamW(contrastive_model.parameters(), lr=learning_rate)
        self.denoising_optimizer = torch.optim.AdamW(denoising_model.parameters(), lr=learning_rate)
        self.numerical_optimizer = torch.optim.AdamW(numerical_model.parameters(), lr=learning_rate)
        
        # Loss functions
        self.ce_loss = nn.CrossEntropyLoss()
        self.mse_loss = nn.MSELoss()
        
        self.metrics = defaultdict(list)
        
        logger.info(f"Initialized Self-Supervised Trainer on {device}")
    
    def train_mlm(self, batch: Dict) -> float:
        """Train Masked Language Model"""
        self.mlm_model.train()
        
        masked_tokens = batch['masked_tokens'].to(self.device)
        original_tokens = batch['original_tokens'].to(self.device)
        mask_positions = batch['mask_positions'].to(self.device)
        
        # Forward pass
        logits = self.mlm_model(masked_tokens)
        
        # Compute loss only on masked positions
        loss = 0
        for i in range(len(mask_positions)):
            if mask_positions[i].sum() > 0:
                masked_logits = logits[i][mask_positions[i] == 1]
                masked_targets = original_tokens[i][mask_positions[i] == 1]
                loss += self.ce_loss(masked_logits, masked_targets)
        
        loss = loss / len(mask_positions)
        
        # Backward pass
        self.mlm_optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.mlm_model.parameters(), 1.0)
        self.mlm_optimizer.step()
        
        self.metrics['mlm_loss'].append(loss.item())
        return loss.item()
    
    def train_ntp(self, batch: Dict) -> float:
        """Train Next Token Predictor"""
        self.ntp_model.train()
        
        tokens = batch['original_tokens'].to(self.device)
        next_tokens = batch['next_tokens'].to(self.device)
        
        # Forward pass
        logits = self.ntp_model(tokens)
        
        # Compute loss
        loss = self.ce_loss(logits.view(-1, logits.size(-1)), next_tokens.view(-1))
        
        # Backward pass
        self.ntp_optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.ntp_model.parameters(), 1.0)
        self.ntp_optimizer.step()
        
        self.metrics['ntp_loss'].append(loss.item())
        return loss.item()
    
    def train_contrastive(self, batch: Dict, temperature: float = 0.07) -> float:
        """Train Contrastive Learning"""
        self.contrastive_model.train()
        
        tokens = batch['original_tokens'].to(self.device)
        
        # Create two augmented views
        view1 = tokens.clone()
        view2 = tokens.clone()
        
        # Add noise to create augmentations
        mask1 = torch.rand_like(tokens, dtype=torch.float) < 0.1
        mask2 = torch.rand_like(tokens, dtype=torch.float) < 0.1
        
        view1[mask1] = torch.randint(0, 50256, view1[mask1].shape).to(self.device)
        view2[mask2] = torch.randint(0, 50256, view2[mask2].shape).to(self.device)
        
        # Get embeddings
        emb1 = self.contrastive_model(view1)
        emb2 = self.contrastive_model(view2)
        
        # Contrastive loss (simplified NT-Xent)
        logits = torch.matmul(emb1, emb2.t()) / temperature
        labels = torch.arange(len(emb1)).to(self.device)
        
        loss = self.ce_loss(logits, labels)
        
        # Backward pass
        self.contrastive_optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.contrastive_model.parameters(), 1.0)
        self.contrastive_optimizer.step()
        
        self.metrics['contrastive_loss'].append(loss.item())
        return loss.item()
    
    def train_denoising(self, batch: Dict) -> float:
        """Train Denoising Autoencoder"""
        self.denoising_model.train()
        
        tokens = batch['original_tokens'].to(self.device)
        
        # Forward pass with noise
        logits = self.denoising_model(tokens, noise_level=0.15)
        
        # Compute loss
        loss = self.ce_loss(logits.view(-1, logits.size(-1)), tokens.view(-1))
        
        # Backward pass
        self.denoising_optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.denoising_model.parameters(), 1.0)
        self.denoising_optimizer.step()
        
        self.metrics['denoising_loss'].append(loss.item())
        return loss.item()
    
    def train_numerical(self, batch: Dict) -> float:
        """Train Numerical Pattern Learner"""
        self.numerical_model.train()
        
        tokens = batch['original_tokens'].to(self.device)
        numerical_labels = batch['numerical_labels'].to(self.device)
        
        # Get embeddings from contrastive model
        embeddings = self.contrastive_model(tokens)
        
        # Forward pass
        pattern_logits, number_pred = self.numerical_model(embeddings)
        
        # Compute loss
        pattern_loss = self.ce_loss(pattern_logits.view(-1, 4), numerical_labels.view(-1))
        
        # Backward pass
        self.numerical_optimizer.zero_grad()
        pattern_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.numerical_model.parameters(), 1.0)
        self.numerical_optimizer.step()
        
        self.metrics['numerical_loss'].append(pattern_loss.item())
        return pattern_loss.item()
    
    def train_step(self, batch: Dict) -> Dict:
        """Single training step on all self-supervised tasks"""
        losses = {
            'mlm': self.train_mlm(batch),
            'ntp': self.train_ntp(batch),
            'contrastive': self.train_contrastive(batch),
            'denoising': self.train_denoising(batch),
            'numerical': self.train_numerical(batch)
        }
        
        total_loss = sum(losses.values())
        losses['total'] = total_loss
        
        return losses
    
    def get_metrics(self) -> Dict:
        """Get training metrics"""
        metrics = {}
        
        for key, values in self.metrics.items():
            if values:
                metrics[key] = {
                    'current': values[-1],
                    'mean': np.mean(values),
                    'min': np.min(values),
                    'max': np.max(values)
                }
        
        return metrics


# ========== MAIN ==========

def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Supervised Token Learning")
    parser.add_argument("--texts", nargs="+", default=["The sum of 2 + 3 is 5", "Machine learning is powerful"], help="Input texts")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--vocab-size", type=int, default=50257, help="Vocabulary size")
    
    args = parser.parse_args()
    
    # Initialize tokenizer
    tokenizer = tiktoken.get_encoding("cl100k_base")
    
    # Create dataset
    dataset = SelfSupervisedTextDataset(args.texts, tokenizer)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    
    # Initialize models
    mlm_model = MaskedLanguageModel(args.vocab_size)
    ntp_model = NextTokenPredictor(args.vocab_size)
    contrastive_model = ContrastiveTokenEncoder(args.vocab_size)
    denoising_model = DenoisingAutoencoder(args.vocab_size)
    numerical_model = NumericalPatternLearner()
    
    # Initialize trainer
    trainer = SelfSupervisedTrainer(
        mlm_model, ntp_model, contrastive_model, denoising_model, numerical_model
    )
    
    # Training loop
    logger.info(f"Starting training for {args.epochs} epochs")
    
    for epoch in range(args.epochs):
        logger.info(f"\nEpoch {epoch+1}/{args.epochs}")
        
        total_losses = defaultdict(float)
        
        for batch_idx, batch in enumerate(dataloader):
            losses = trainer.train_step(batch)
            
            for key, value in losses.items():
                total_losses[key] += value
            
            if (batch_idx + 1) % max(1, len(dataloader) // 5) == 0:
                logger.info(f"  Batch {batch_idx+1}/{len(dataloader)}")
                for key, value in losses.items():
                    logger.info(f"    {key}: {value:.4f}")
        
        # Print epoch summary
        logger.info(f"\nEpoch {epoch+1} Summary:")
        for key, value in total_losses.items():
            avg_loss = value / len(dataloader)
            logger.info(f"  Avg {key}: {avg_loss:.4f}")
    
    # Print final metrics
    logger.info("\n" + "="*80)
    logger.info("SELF-SUPERVISED TRAINING COMPLETE")
    logger.info("="*80)
    
    metrics = trainer.get_metrics()
    for key, metric in metrics.items():
        logger.info(f"{key}:")
        logger.info(f"  Current: {metric['current']:.4f}")
        logger.info(f"  Mean: {metric['mean']:.4f}")
        logger.info(f"  Min: {metric['min']:.4f}")
        logger.info(f"  Max: {metric['max']:.4f}")


if __name__ == "__main__":
    main()
