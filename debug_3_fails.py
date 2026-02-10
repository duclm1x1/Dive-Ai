"""Debug context compaction only."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "desktop-app", "backend"))

from dive_core.engine.context_guard import ContextWindowGuard

bg = ContextWindowGuard(model_max_tokens=500)
print("Budget available:", bg.budget.available)
print("Max tokens:", bg.budget.max_tokens)

# Add messages
for i in range(20):
    r = bg.add_message("user", "Message %d: " % i + "word " * 50)
    r2 = bg.add_message("assistant", "Response %d: " % i + "reply " * 50)

print("Current tokens:", bg.current_token_count())
print("Messages:", len(bg._messages))
print("Compaction count so far:", bg._compaction_count)

# Try manual compact
target = int(bg.budget.available * 0.3)
print("Target tokens:", target)
print("Before > target?", bg.current_token_count() > target)

# Check compactable
compactable = [m for m in bg._messages if m.compactable and not m.preserved]
print("Compactable msgs:", len(compactable))

cp = bg.compact(target_ratio=0.3)
print("Compact result:", cp)
