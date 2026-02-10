#!/usr/bin/env python3
"""
Example usage of the Semantic Code Weaving (SCW) skill.
"""

import sys
import os
import json

# Add the skill src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from scw_engine import SemanticCodeWeaver

def main():
    """Demonstrates building and using an intent graph."""
    print("--- SCW Skill Example: Building an Intent Graph for a Blog ---")

    # 1. Instantiate the weaver
    scw = SemanticCodeWeaver()

    # 2. Build the graph from a user prompt: "Create a blog with users and posts"
    print("\nBuilding intent graph from user prompt...")
    user_model_id = scw.add_node(
        name="User Data Model",
        description="Represents a user with username, email, and hashed password.",
        node_type="data_model"
    )
    post_model_id = scw.add_node(
        name="Post Data Model",
        description="Represents a blog post with title, content, and an author reference.",
        node_type="data_model",
        dependencies=[user_model_id]
    )
    auth_feature_id = scw.add_node(
        name="User Authentication",
        description="Endpoints for user signup and login.",
        node_type="feature",
        dependencies=[user_model_id]
    )
    posts_api_id = scw.add_node(
        name="CRUD API for Posts",
        description="API endpoints to create, read, update, and delete posts.",
        node_type="feature",
        dependencies=[post_model_id, auth_feature_id]
    )

    # 3. Get the recommended implementation order
    implementation_plan = scw.get_implementation_order()
    print(f"\nRecommended Implementation Order: {implementation_plan}")

    # 4. Simulate the implementation process
    print("\nSimulating code generation process...")
    for node_id in implementation_plan:
        node = scw.get_node(node_id)
        print(f"  - Generating code for: {node.name} ({node_id})")
        # In a real scenario, this is where you would call a code generation model
        scw.mark_as_implemented(node_id)
    
    # 5. Verify that all nodes are implemented
    unimplemented = scw.get_unimplemented_nodes()
    if not unimplemented:
        print("\n✅ Success: All intents have been woven into the codebase.")
    else:
        print(f"\n❌ Failure: {len(unimplemented)} intents remain unimplemented.")

    # 6. Serialize the final graph for auditing
    final_graph = scw.to_dict()
    print("\n--- Final Intent Graph ---")
    print(json.dumps(final_graph, indent=2))

    print("\n--- SCW Skill Example Complete ---")

if __name__ == "__main__":
    main()
