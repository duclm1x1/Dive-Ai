#!/usr/bin/env python3
"""
Contextual Compression with Foresight (CCF) - Skill Implementation

This skill provides a framework for managing an LLM's limited context window 
intelligently, by summarizing less relevant information and predicting future 
context needs.
"""

import logging
from typing import Dict, List, Any, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Represents a piece of information in the context window."""
    doc_id: str
    content: str
    relevance_score: float = 1.0
    is_summarized: bool = False

class ContextManager:
    """Manages the context window by summarizing and prioritizing documents."""

    def __init__(self, context_limit: int = 1000):
        self.documents: Dict[str, Document] = {}
        self.context_limit = context_limit  # Max characters in context
        self.doc_counter = 0
        logger.info(f"Context Manager initialized with a limit of {context_limit} characters.")

    def _get_current_size(self) -> int:
        """Calculates the total size of the current context."""
        return sum(len(doc.content) for doc in self.documents.values())

    def add_document(self, content: str, relevance_score: float = 1.0) -> str:
        """Adds a new document to the context."""
        self.doc_counter += 1
        doc_id = f"DOC-{self.doc_counter:04d}"
        doc = Document(doc_id=doc_id, content=content, relevance_score=relevance_score)
        self.documents[doc_id] = doc
        logger.info(f"Added document '{doc_id}' to context.")
        return doc_id

    def predict_future_needs(self, future_goal: str):
        """Simulates an LLM predicting future context needs and adjusting relevance scores."""
        logger.info(f"Predicting future needs for goal: '{future_goal}'")
        for doc in self.documents.values():
            # Simple heuristic: if a keyword from the goal is in the doc, boost its relevance
            if any(keyword in doc.content.lower() for keyword in future_goal.lower().split()):
                doc.relevance_score *= 1.5
                logger.info(f"Boosting relevance for doc '{doc.doc_id}' based on future goal.")

    def _summarize_document(self, doc: Document):
        """Simulates summarizing a document to save space."""
        if not doc.is_summarized:
            original_length = len(doc.content)
            # Simple summary: take the first 50 characters
            doc.content = doc.content[:50] + "..."
            doc.is_summarized = True
            logger.warning(f"Summarized document '{doc.doc_id}' to save {original_length - len(doc.content)} characters.")

    def compress_context(self):
        """Compresses the context to fit within the limit, prioritizing by relevance."""
        logger.info("--- Starting Context Compression ---")
        current_size = self._get_current_size()
        if current_size <= self.context_limit:
            logger.info("Context is within limits. No compression needed.")
            return

        # Sort documents by relevance, least relevant first
        sorted_docs = sorted(self.documents.values(), key=lambda d: d.relevance_score)

        for doc in sorted_docs:
            if self._get_current_size() <= self.context_limit:
                break
            self._summarize_document(doc)
        
        # If still over the limit, start removing the least relevant summaries
        while self._get_current_size() > self.context_limit and sorted_docs:
            doc_to_remove = sorted_docs.pop(0)
            if doc_to_remove.doc_id in self.documents:
                logger.error(f"Context still too large. Discarding least relevant document: '{doc_to_remove.doc_id}'")
                del self.documents[doc_to_remove.doc_id]

        logger.info(f"--- Compression Complete. Final context size: {self._get_current_size()} ---")
