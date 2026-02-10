#!/usr/bin/env python3
"""
Multi-Task Learning System for Next-Word Prediction
Handles grammar, world knowledge, sentiment analysis, translation, spatial reasoning, math, and more
Achieves superior performance through shared representations and task-specific adaptation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM, PreTrainedModel
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== TASK DEFINITIONS ==========

class TaskType(Enum):
    """Supported task types"""
    GRAMMAR = "grammar"
    WORLD_KNOWLEDGE = "world_knowledge"
    SENTIMENT = "sentiment"
    TRANSLATION = "translation"
    SPATIAL_REASONING = "spatial_reasoning"
    MATH = "math"
    NEXT_WORD = "next_word"
    NAMED_ENTITY = "named_entity"
    QUESTION_ANSWERING = "question_answering"
    SUMMARIZATION = "summarization"


@dataclass
class TaskConfig:
    """Configuration for a specific task"""
    task_type: TaskType
    task_name: str
    description: str
    input_format: str
    output_format: str
    loss_weight: float = 1.0
    head_hidden_size: int = 768
    num_labels: Optional[int] = None
    is_classification: bool = False
    is_generation: bool = True


# ========== TASK-SPECIFIC HEADS ==========

class TaskHead(nn.Module):
    """Base class for task-specific prediction heads"""
    
    def __init__(self, hidden_size: int, config: TaskConfig):
        super().__init__()
        self.config = config
        self.hidden_size = hidden_size
    
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError


class GenerationHead(TaskHead):
    """Head for generation tasks (next-word prediction)"""
    
    def __init__(self, hidden_size: int, vocab_size: int, config: TaskConfig):
        super().__init__(hidden_size, config)
        self.projection = nn.Linear(hidden_size, vocab_size)
    
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Generate logits for next token"""
        return self.projection(hidden_states)


class ClassificationHead(TaskHead):
    """Head for classification tasks"""
    
    def __init__(self, hidden_size: int, config: TaskConfig):
        super().__init__(hidden_size, config)
        self.dropout = nn.Dropout(0.1)
        self.dense = nn.Linear(hidden_size, config.head_hidden_size)
        self.classifier = nn.Linear(config.head_hidden_size, config.num_labels)
    
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Classify input"""
        x = self.dropout(hidden_states)
        x = torch.relu(self.dense(x))
        x = self.dropout(x)
        return self.classifier(x)


class SequenceLabelingHead(TaskHead):
    """Head for sequence labeling tasks (NER, POS tagging)"""
    
    def __init__(self, hidden_size: int, config: TaskConfig):
        super().__init__(hidden_size, config)
        self.dropout = nn.Dropout(0.1)
        self.dense = nn.Linear(hidden_size, config.head_hidden_size)
        self.classifier = nn.Linear(config.head_hidden_size, config.num_labels)
    
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Label each token in sequence"""
        x = self.dropout(hidden_states)
        x = torch.relu(self.dense(x))
        x = self.dropout(x)
        return self.classifier(x)


class TranslationHead(TaskHead):
    """Head for translation tasks"""
    
    def __init__(self, hidden_size: int, vocab_size: int, config: TaskConfig):
        super().__init__(hidden_size, config)
        self.projection = nn.Linear(hidden_size, vocab_size)
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=8)
    
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Generate translation"""
        # Apply attention
        attn_output, _ = self.attention(hidden_states, hidden_states, hidden_states)
        # Project to vocabulary
        return self.projection(attn_output)


# ========== MULTI-TASK MODEL ==========

class MultiTaskLearningModel(nn.Module):
    """
    Multi-Task Learning Model for Next-Word Prediction
    Shares base encoder, has task-specific heads
    """
    
    def __init__(self, model_name: str, tasks: List[TaskConfig]):
        super().__init__()
        
        logger.info(f"Initializing MTL Model with {len(tasks)} tasks")
        
        # Load base model
        self.base_model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.hidden_size = self.base_model.config.hidden_size
        self.vocab_size = self.base_model.config.vocab_size
        
        # Task configurations
        self.tasks = {task.task_type: task for task in tasks}
        self.task_heads = nn.ModuleDict()
        
        # Create task-specific heads
        self._create_task_heads()
        
        # Task-specific layer normalization
        self.task_layer_norms = nn.ModuleDict()
        for task_type in self.tasks:
            self.task_layer_norms[task_type.value] = nn.LayerNorm(self.hidden_size)
        
        # Shared adapter layers for better task interaction
        self.shared_adapter = nn.Sequential(
            nn.Linear(self.hidden_size, self.hidden_size * 4),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(self.hidden_size * 4, self.hidden_size)
        )
        
        logger.info(f"MTL Model initialized with {len(self.task_heads)} task heads")
    
    def _create_task_heads(self):
        """Create task-specific prediction heads"""
        for task_type, config in self.tasks.items():
            task_name = task_type.value
            
            if config.is_classification:
                head = ClassificationHead(self.hidden_size, config)
            elif task_type == TaskType.NAMED_ENTITY:
                head = SequenceLabelingHead(self.hidden_size, config)
            elif task_type == TaskType.TRANSLATION:
                head = TranslationHead(self.hidden_size, self.vocab_size, config)
            else:
                head = GenerationHead(self.hidden_size, self.vocab_size, config)
            
            self.task_heads[task_name] = head
            logger.info(f"Created head for task: {task_name}")
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        task_type: Optional[TaskType] = None,
        labels: Optional[Dict[str, torch.Tensor]] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass for multi-task learning
        
        Args:
            input_ids: Input token IDs
            attention_mask: Attention mask
            task_type: Target task type
            labels: Task-specific labels for loss computation
        
        Returns:
            Dictionary with task outputs and losses
        """
        # Get base model outputs
        outputs = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
            return_dict=True
        )
        
        hidden_states = outputs.hidden_states[-1]  # Last layer
        
        # Apply shared adapter
        adapted_hidden_states = self.shared_adapter(hidden_states)
        
        results = {}
        
        # If specific task is provided, use only that head
        if task_type is not None:
            task_name = task_type.value
            task_config = self.tasks[task_type]
            
            # Apply task-specific layer norm
            normalized_states = self.task_layer_norms[task_name](adapted_hidden_states)
            
            # Get task predictions
            task_head = self.task_heads[task_name]
            logits = task_head(normalized_states)
            
            results[task_name] = {
                'logits': logits,
                'hidden_states': hidden_states
            }
            
            # Compute loss if labels provided
            if labels is not None and task_name in labels:
                loss = self._compute_task_loss(
                    logits,
                    labels[task_name],
                    task_config
                )
                results[task_name]['loss'] = loss
        
        # Otherwise, compute all task outputs
        else:
            total_loss = 0
            
            for task_type, task_config in self.tasks.items():
                task_name = task_type.value
                
                # Apply task-specific layer norm
                normalized_states = self.task_layer_norms[task_name](adapted_hidden_states)
                
                # Get task predictions
                task_head = self.task_heads[task_name]
                logits = task_head(normalized_states)
                
                results[task_name] = {
                    'logits': logits,
                    'hidden_states': hidden_states
                }
                
                # Compute loss if labels provided
                if labels is not None and task_name in labels:
                    loss = self._compute_task_loss(
                        logits,
                        labels[task_name],
                        task_config
                    )
                    weighted_loss = loss * task_config.loss_weight
                    results[task_name]['loss'] = loss
                    total_loss += weighted_loss
            
            if labels is not None:
                results['total_loss'] = total_loss
        
        return results
    
    def _compute_task_loss(
        self,
        logits: torch.Tensor,
        labels: torch.Tensor,
        task_config: TaskConfig
    ) -> torch.Tensor:
        """Compute loss for a specific task"""
        if task_config.is_classification:
            # Classification loss
            loss_fn = nn.CrossEntropyLoss()
            return loss_fn(logits.view(-1, logits.size(-1)), labels.view(-1))
        else:
            # Generation loss
            loss_fn = nn.CrossEntropyLoss()
            return loss_fn(logits.view(-1, logits.size(-1)), labels.view(-1))
    
    def predict(
        self,
        text: str,
        task_type: TaskType,
        num_predictions: int = 5
    ) -> Dict:
        """
        Make prediction for a specific task
        
        Args:
            text: Input text
            task_type: Target task
            num_predictions: Number of predictions
        
        Returns:
            Predictions dictionary
        """
        self.eval()
        
        with torch.no_grad():
            # Tokenize input
            inputs = self.tokenizer(text, return_tensors="pt")
            
            # Get model outputs
            outputs = self.forward(
                input_ids=inputs['input_ids'],
                attention_mask=inputs.get('attention_mask'),
                task_type=task_type
            )
            
            task_name = task_type.value
            logits = outputs[task_name]['logits']
            
            # Get top predictions
            if self.tasks[task_type].is_classification:
                probabilities = F.softmax(logits, dim=-1)
                top_probs, top_indices = torch.topk(probabilities, num_predictions)
                predictions = top_indices[0].tolist()
                scores = top_probs[0].tolist()
            else:
                # For generation, get top tokens
                next_token_logits = logits[0, -1, :]
                probabilities = F.softmax(next_token_logits, dim=-1)
                top_probs, top_indices = torch.topk(probabilities, num_predictions)
                
                predictions = [self.tokenizer.decode([idx]) for idx in top_indices]
                scores = top_probs.tolist()
            
            return {
                'task': task_name,
                'input': text,
                'predictions': predictions,
                'scores': scores
            }


# ========== TASK ROUTER ==========

class TaskRouter:
    """
    Detects task type from input text
    Routes to appropriate task head
    """
    
    def __init__(self):
        self.task_patterns = {
            TaskType.GRAMMAR: [
                "grammar", "correct", "sentence", "verb", "noun", "tense"
            ],
            TaskType.WORLD_KNOWLEDGE: [
                "capital", "country", "city", "president", "population", "located"
            ],
            TaskType.SENTIMENT: [
                "sentiment", "review", "opinion", "like", "hate", "good", "bad", "feel"
            ],
            TaskType.TRANSLATION: [
                "translate", "russian", "spanish", "french", "german", "chinese", "word for"
            ],
            TaskType.SPATIAL_REASONING: [
                "where", "location", "left", "right", "next to", "inside", "outside"
            ],
            TaskType.MATH: [
                "calculate", "math", "equation", "answer", "+", "-", "*", "/", "="
            ],
            TaskType.QUESTION_ANSWERING: [
                "what", "who", "when", "where", "why", "how", "?"
            ],
            TaskType.NAMED_ENTITY: [
                "name", "person", "organization", "entity", "tag"
            ]
        }
    
    def detect_task(self, text: str) -> TaskType:
        """
        Detect task type from input text
        
        Args:
            text: Input text
        
        Returns:
            Detected task type
        """
        text_lower = text.lower()
        
        # Count pattern matches for each task
        task_scores = {}
        
        for task_type, patterns in self.task_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            if score > 0:
                task_scores[task_type] = score
        
        # Return task with highest score
        if task_scores:
            return max(task_scores, key=task_scores.get)
        
        # Default to next-word prediction
        return TaskType.NEXT_WORD
    
    def detect_multiple_tasks(self, text: str, top_k: int = 3) -> List[Tuple[TaskType, float]]:
        """
        Detect multiple possible tasks with confidence scores
        
        Args:
            text: Input text
            top_k: Number of top tasks to return
        
        Returns:
            List of (task_type, confidence) tuples
        """
        text_lower = text.lower()
        task_scores = {}
        
        for task_type, patterns in self.task_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            task_scores[task_type] = score
        
        # Normalize scores to probabilities
        total_score = sum(task_scores.values()) or 1
        task_probs = [
            (task, score / total_score)
            for task, score in sorted(
                task_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_k]
        ]
        
        return task_probs


# ========== TRAINING UTILITIES ==========

class MultiTaskTrainer:
    """Trainer for multi-task learning"""
    
    def __init__(
        self,
        model: MultiTaskLearningModel,
        learning_rate: float = 1e-4,
        device: str = "cuda"
    ):
        self.model = model
        self.device = device
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=10
        )
    
    def train_step(
        self,
        batch: Dict[str, torch.Tensor],
        task_type: TaskType
    ) -> float:
        """
        Single training step
        
        Args:
            batch: Training batch
            task_type: Task type to train on
        
        Returns:
            Loss value
        """
        self.model.train()
        
        # Forward pass
        outputs = self.model(
            input_ids=batch['input_ids'].to(self.device),
            attention_mask=batch.get('attention_mask', None),
            task_type=task_type,
            labels={task_type.value: batch['labels'].to(self.device)}
        )
        
        loss = outputs[task_type.value]['loss']
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()
        
        return loss.item()
    
    def train_multi_task_step(
        self,
        batches: Dict[TaskType, Dict[str, torch.Tensor]]
    ) -> float:
        """
        Training step on multiple tasks
        
        Args:
            batches: Dictionary of task -> batch
        
        Returns:
            Total loss
        """
        self.model.train()
        
        total_loss = 0
        
        for task_type, batch in batches.items():
            outputs = self.model(
                input_ids=batch['input_ids'].to(self.device),
                attention_mask=batch.get('attention_mask', None),
                task_type=task_type,
                labels={task_type.value: batch['labels'].to(self.device)}
            )
            
            loss = outputs[task_type.value]['loss']
            total_loss += loss
        
        # Backward pass
        self.optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()
        
        return total_loss.item()


# ========== MAIN ==========

def create_default_tasks() -> List[TaskConfig]:
    """Create default task configurations"""
    return [
        TaskConfig(
            task_type=TaskType.GRAMMAR,
            task_name="Grammar Correction",
            description="Correct grammatical errors",
            input_format="text",
            output_format="corrected_text",
            loss_weight=1.0
        ),
        TaskConfig(
            task_type=TaskType.WORLD_KNOWLEDGE,
            task_name="World Knowledge",
            description="Answer factual questions",
            input_format="question",
            output_format="answer",
            loss_weight=1.0
        ),
        TaskConfig(
            task_type=TaskType.SENTIMENT,
            task_name="Sentiment Analysis",
            description="Analyze sentiment",
            input_format="text",
            output_format="sentiment",
            loss_weight=1.0,
            is_classification=True,
            num_labels=3
        ),
        TaskConfig(
            task_type=TaskType.TRANSLATION,
            task_name="Translation",
            description="Translate between languages",
            input_format="text",
            output_format="translated_text",
            loss_weight=1.0
        ),
        TaskConfig(
            task_type=TaskType.SPATIAL_REASONING,
            task_name="Spatial Reasoning",
            description="Reason about spatial relationships",
            input_format="text",
            output_format="answer",
            loss_weight=1.0
        ),
        TaskConfig(
            task_type=TaskType.MATH,
            task_name="Math Question",
            description="Solve math problems",
            input_format="question",
            output_format="answer",
            loss_weight=1.0
        ),
        TaskConfig(
            task_type=TaskType.QUESTION_ANSWERING,
            task_name="Question Answering",
            description="Answer questions",
            input_format="question",
            output_format="answer",
            loss_weight=1.0
        ),
        TaskConfig(
            task_type=TaskType.NAMED_ENTITY,
            task_name="Named Entity Recognition",
            description="Recognize named entities",
            input_format="text",
            output_format="entities",
            loss_weight=1.0,
            num_labels=5
        ),
    ]


if __name__ == "__main__":
    # Example usage
    logger.info("Initializing Multi-Task Learning System")
    
    # Create tasks
    tasks = create_default_tasks()
    
    # Initialize model
    model = MultiTaskLearningModel(
        model_name="distilgpt2",
        tasks=tasks
    )
    
    # Initialize task router
    router = TaskRouter()
    
    # Example predictions
    test_texts = [
        "The capital of Azerbaijan is",
        "In my free time, I like to",
        "Movie review: I was engaged and on the edge of my seat the whole time. The movie was",
        "3 + 8 + 4 =",
        "Where did Zuko go?"
    ]
    
    logger.info("Making predictions on test texts...")
    for text in test_texts:
        detected_task = router.detect_task(text)
        logger.info(f"Text: {text}")
        logger.info(f"Detected task: {detected_task.value}")
        
        # Make prediction
        prediction = model.predict(text, detected_task, num_predictions=3)
        logger.info(f"Predictions: {prediction['predictions']}")
        logger.info("")
