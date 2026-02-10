#!/usr/bin/env python3
"""
Example usage of the Contextual Compression with Foresight (CCF) skill.
"""

import sys
import os
import logging

# Configure logging to see the engine's decisions
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ccf_engine import ContextManager

def main():
    """Demonstrates the CCF workflow."""
    print("--- CCF Skill Example: Managing a Crowded Context Window ---")

    # 1. Initialize with a small context limit for demonstration
    ccf = ContextManager(context_limit=250)

    # 2. Add several documents, simulating information gathering
    ccf.add_document(
        "Main Goal: Create a Python web application for a bookstore.", 
        relevance_score=10.0
    )
    ccf.add_document(
        "The user specified that the application must use a PostgreSQL database.", 
        relevance_score=8.0
    )
    ccf.add_document(
        "A previous sub-task involved researching various Python web frameworks.", 
        relevance_score=5.0
    )
    ccf.add_document(
        "An unrelated note about the weather on Tuesday.", 
        relevance_score=1.0
    )

    print(f"\nCurrent context size: {ccf._get_current_size()}")

    # 3. Use foresight to predict the next task
    print("\nNext task is to set up the database. Using foresight...")
    ccf.predict_future_needs("setup postgresql database")
    # This should boost the relevance of the PostgreSQL document.

    # 4. Add another document that pushes the context over the limit
    print("\nAdding a large document that will force compression...")
    ccf.add_document(
        "This is a very long document containing the full text of a tutorial on how to deploy Python applications using Docker and Kubernetes, which is not immediately relevant.",
        relevance_score=3.0
    )
    print(f"Context size after addition: {ccf._get_current_size()}")

    # 5. Run the compression
    ccf.compress_context()

    print("\n--- Final Context State ---")
    for doc_id, doc in ccf.documents.items():
        print(f"- [{doc_id}] Relevance: {doc.relevance_score:.2f}, Summarized: {doc.is_summarized}, Content: {doc.content}")

    print("\n--- CCF Skill Example Complete ---")

if __name__ == "__main__":
    main()
